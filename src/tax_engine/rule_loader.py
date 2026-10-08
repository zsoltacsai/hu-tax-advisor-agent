"""Schema and provenance validation for declarative rule/source registries."""
import json
import re
import hashlib
from datetime import datetime,timezone
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
from referencing import Registry,Resource
from .exceptions import RuleValidationError

def _canonical_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()

ROOT=Path(__file__).resolve().parents[2]
def _load_json(path):
    try: return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc: raise RuleValidationError(f"cannot load JSON {path}: {exc}") from exc

def _norm(text): return re.sub(r"[^a-z0-9]+","",str(text).lower())

class RuleLoader:
    def __init__(self, root: Path|str|None=None):
        self.root=Path(root) if root else ROOT
        self.schemas={}
        self.schema_registry=Registry()
        for path in (self.root/"schemas").glob("*.schema.json"):
            obj=_load_json(path); obj["$id"]=path.resolve().as_uri(); self.schemas[path.name]=obj
            self.schema_registry=self.schema_registry.with_resource(obj["$id"],Resource.from_contents(obj))
        self.registry=_load_json(self.root/"sources"/"registry.json")
        self.sources={s["id"]:s for s in self.registry.get("sources",[])}
        self.checker=FormatChecker()
        self.rule_provenance={}

    def _validate(self,obj,schema_name,label):
        schema=self.schemas[schema_name]
        validator=Draft202012Validator(schema,registry=self.schema_registry,format_checker=self.checker)
        errors=sorted(validator.iter_errors(obj),key=lambda e:(list(map(str,e.path)),e.message))
        if errors:
            e=errors[0]; raise RuleValidationError(f"{label}: {e.message}")

    def validate_rule(self,rule):
        self._validate(rule,"executable-rule.schema.json",f"rule {rule.get('rule_version_id')}")
        if rule["effective_to"] and rule["effective_to"]<=rule["effective_from"]:
            raise RuleValidationError(f"invalid effective interval in {rule['rule_version_id']}")
        if (rule["rule_scope"]=="GENERAL" and rule["rule_specificity"]!=0) or (rule["rule_scope"]=="SPECIFIC" and rule["rule_specificity"]<=0):
            raise RuleValidationError("rule scope/specificity mismatch")
        for evidence in rule["evidence"]:
            source=self.sources.get(evidence["source_id"])
            if source is None: raise RuleValidationError(f"unknown source ID {evidence['source_id']}")
            if not source.get("url_checked") or not source.get("content_verified"):
                raise RuleValidationError(f"source is not verified: {evidence['source_id']}")
            provision=_norm(evidence["provision"])
            registered=[_norm(p) for p in source.get("relevant_provisions",[])]
            if not any(p and (p in provision or provision in p) for p in registered):
                raise RuleValidationError(f"unregistered provision {evidence['provision']} for {evidence['source_id']}")
        return rule

    def load_rules(self,path:Path|str|None=None):
        approved_dir=(self.root/"rules"/"approved").resolve()
        if path is not None:
            requested=Path(path).resolve()
            if requested!=approved_dir and approved_dir not in requested.parents:
                raise RuleValidationError("executable rules may be loaded only from rules/approved")
            files=[requested] if requested.is_file() else sorted(requested.glob("*.json"))
        else:
            files=sorted(approved_dir.glob("*.json")) if approved_dir.exists() else []
        rules=[]; seen=set(); audit_events={}; lifecycle=[]
        audit_path=self.root/"state"/"audit.jsonl"
        previous=None
        if audit_path.exists():
            for line_no,line in enumerate(audit_path.read_text(encoding="utf-8").splitlines(),1):
                try: event=json.loads(line)
                except Exception as exc: raise RuleValidationError(f"malformed audit event at line {line_no}") from exc
                raw={k:v for k,v in event.items() if k!="event_hash"}
                if event.get("previous_event_hash")!=previous or event.get("event_hash")!=_canonical_hash(raw):
                    raise RuleValidationError(f"audit hash chain invalid at line {line_no}")
                previous=event["event_hash"]; audit_events[event["event_hash"]]=event
                lifecycle.append(event)
        for file in files:
            approved=_load_json(file)
            self._validate(approved,"approved-rule.schema.json",f"approved rule {file.name}")
            if approved["approval"]["approved"] is not True:
                raise RuleValidationError(f"rule has no human approval: {file.name}")
            rule=dict(approved["rule"])
            approval=approved["approval"]
            if _canonical_hash(rule)!=approval["approved_rule_hash"]:
                raise RuleValidationError(f"approved rule content hash mismatch: {file.name}")
            if file.stem!=rule["rule_version_id"]:
                raise RuleValidationError(f"approved rule filename/version mismatch: {file.name}")
            event=audit_events.get(approval["approval_event_hash"])
            if not event or event.get("event_type")!="HUMAN_APPROVAL" or event.get("actor")!=approval["approved_by"] or event.get("subject_id")!=approval["candidate_id"] or event.get("details",{}).get("rule_version_id")!=rule["rule_version_id"]:
                raise RuleValidationError(f"human approval audit record missing or mismatched: {file.name}")
            details=event.get("details",{})
            if any(details.get(k)!=approval.get(k) for k in ("candidate_hash","review_hash","research_snapshot_hash","approved_rule_hash","review_id","research_id")):
                raise RuleValidationError(f"approval audit hashes do not match wrapper: {file.name}")
            candidate_path=self.root/"rules"/"proposed"/(approval["candidate_id"]+".json")
            review_path=self.root/"rules"/"reviews"/(approval["review_id"]+".json")
            snapshot_path=self.root/"research"/"snapshots"/(approval["research_id"]+".json")
            if not candidate_path.exists() or not review_path.exists() or not snapshot_path.exists():
                raise RuleValidationError(f"approval chain candidate/review/research record missing: {file.name}")
            candidate=_load_json(candidate_path); review=_load_json(review_path); snapshot=_load_json(snapshot_path)
            if _canonical_hash(candidate)!=approval["candidate_hash"] or _canonical_hash(review)!=approval["review_hash"]:
                raise RuleValidationError(f"candidate or review hash mismatch: {file.name}")
            if review.get("status")!="APPROVE_FOR_HUMAN_REVIEW" or review.get("candidate_id")!=approval["candidate_id"] or review.get("research_id")!=approval["research_id"]:
                raise RuleValidationError(f"review is missing or does not support human approval: {file.name}")
            snapshot_material={k:v for k,v in snapshot.items() if k!="snapshot_hash"}
            if snapshot.get("snapshot_hash")!=approval["research_snapshot_hash"] or _canonical_hash(snapshot_material)!=approval["research_snapshot_hash"]:
                raise RuleValidationError(f"frozen research snapshot hash mismatch: {file.name}")
            candidate_rule={k:candidate[k] for k in ("rule_id","rule_version_id","jurisdiction","topic","effective_from","effective_to","conditions","outcome","evidence","requires","exclusions","human_review_if","description","priority","rule_scope","rule_specificity")}
            candidate_rule["enabled"]=True
            if _canonical_hash(candidate_rule)!=_canonical_hash(rule):
                raise RuleValidationError(f"approved rule differs from its reviewed immutable candidate: {file.name}")
            source_rows={s["source_id"]:s for s in snapshot.get("sources_considered",[])}
            pinned={(x["source_id"],x["provision"],x["source_version"],x["research_snapshot_id"]) for x in approval["source_versions"]}
            expected={(e["source_id"],e["provision"],e["source_version"],approval["research_id"]) for e in rule["evidence"]}
            if pinned!=expected or any(e["source_id"] not in source_rows for e in rule["evidence"]):
                raise RuleValidationError(f"approved evidence is not pinned to its frozen research snapshot: {file.name}")
            for evidence_item in rule["evidence"]:
                frozen=source_rows[evidence_item["source_id"]]
                expected_version=frozen.get("version_date") or frozen.get("retrieved_at")
                if expected_version and expected_version not in evidence_item["source_version"]:
                    raise RuleValidationError(f"evidence source version differs from frozen research: {file.name}")
                provision_ok=any(x["source_id"]==evidence_item["source_id"] and x["provision"]==evidence_item["provision"] and x["verified"] for x in snapshot.get("relevant_provisions",[]))
                if not provision_ok:
                    raise RuleValidationError(f"approved provision is not verified in the frozen research snapshot: {file.name}")
            self.validate_rule(rule)
            vid=rule["rule_version_id"]
            if vid in seen: raise RuleValidationError(f"duplicate rule version ID: {vid}")
            seen.add(vid)
            # Missing or adverse source checks fail closed; a rule is unavailable until fresh status is recorded.
            status=[]
            latest_checks=[]
            approved_versions={x["source_id"]:x.get("version_date") for x in approval["source_versions"]}
            for ev in rule["evidence"]:
                checkdir=self.root/"state"/"source_checks"
                checks=sorted(checkdir.glob(ev["source_id"]+"*.json"),reverse=True) if checkdir.exists() else []
                if not checks: status.append("UNKNOWN"); continue
                latest=max((json.loads(p.read_text(encoding="utf-8")) for p in checks),key=lambda x:x.get("last_verified_at") or "")
                status.append(latest.get("current_check_status","UNKNOWN"))
                if latest.get("last_version_date")!=approved_versions.get(ev["source_id"]): status.append("CHANGED")
                latest_checks.append(latest)
            if any(s!="UNCHANGED" for s in status): continue
            freshness_days={"HIGH_CHANGE":90,"ANNUAL_REVIEW":365,"LOW_CHANGE":730,"STATIC_HISTORICAL":None,"LIVE_VERIFICATION_REQUIRED":0}
            expired=False
            for ev,check in zip(rule["evidence"],latest_checks):
                age=freshness_days.get(self.sources[ev["source_id"]].get("freshness_class"),0)
                if age==0: expired=True; break
                stamp=check.get("last_verified_at")
                if age is not None and (not stamp or (datetime.now(timezone.utc)-datetime.fromisoformat(stamp)).days>age): expired=True;break
            if expired: continue
            rules.append(rule)
            self.rule_provenance[vid]={"candidate_id":approval["candidate_id"],"candidate_hash":approval["candidate_hash"],
              "review_id":approval["review_id"],"review_hash":approval["review_hash"],"research_snapshot_id":approval["research_id"],
              "research_snapshot_hash":approval["research_snapshot_hash"],"approval_event_hash":approval["approval_event_hash"],
              "approved_rule_hash":approval["approved_rule_hash"],"approved_by":approval["approved_by"],
              "source_versions":approval["source_versions"]}
        # Lifecycle transitions are append-only. A supersession event bounds the old rule at runtime.
        audit=self.root/"state"/"audit.jsonl"
        if audit.exists():
            for event in lifecycle:
                if event.get("event_type")=="RULE_RETIRED":
                    rules=[r for r in rules if r["rule_version_id"]!=event.get("subject_id")]
                if event.get("event_type")=="RULE_SUPERSEDED":
                    end=event.get("details",{}).get("effective_to");old_id=event.get("subject_id")
                    for rule in rules:
                        if rule["rule_version_id"]==old_id and (not rule["effective_to"] or rule["effective_to"]>=end):rule["effective_to"]=end
        return rules

    def load_thresholds(self,path:Path|str|None=None):
        file=Path(path) if path else self.root/"rules"/"thresholds.json"
        data=_load_json(file)
        self._validate(data,"threshold-registry.schema.json","threshold registry")
        seen=set()
        for item in data["thresholds"]:
            sid=item["source_id"]
            if sid not in self.sources: raise RuleValidationError(f"unknown threshold source ID {sid}")
            if item["provision"] and not any(_norm(p) in _norm(item["provision"]) or _norm(item["provision"]) in _norm(p) for p in self.sources[sid].get("relevant_provisions",[])):
                raise RuleValidationError(f"unregistered threshold provision {item['provision']}")
            if item["threshold_id"] in seen: raise RuleValidationError(f"duplicate threshold ID {item['threshold_id']}")
            seen.add(item["threshold_id"])
        return data["thresholds"]
