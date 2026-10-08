"""Fail-closed local pipeline. It consumes structured drafts; it does not call an LLM or web service."""
from __future__ import annotations
import hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any,Protocol
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from src.tax_engine.rule_loader import RuleLoader
from src.tax_engine.exceptions import RuleValidationError

ROOT=Path(__file__).resolve().parents[2]
def canonical(value): return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def digest(value): return hashlib.sha256((value if isinstance(value,str) else canonical(value)).encode("utf-8")).hexdigest()
def load(path):
    try: return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc: raise PipelineError(f"invalid JSON at {path}: {exc}") from exc
def write_immutable(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if path.exists():
        if path.read_text(encoding="utf-8")==data:return path
        raise PipelineError(f"immutable record already exists with different contents: {path}")
    try:
        with path.open("x",encoding="utf-8",newline="\n") as f: f.write(data)
    except FileExistsError as exc: raise PipelineError(f"immutable record already exists: {path}") from exc

class PipelineError(ValueError): pass

class ResearchDraftProvider(Protocol):
    """Optional future model/research adapter. Its output is always untrusted data."""
    def research(self,request:dict[str,Any],source_catalog:list[dict[str,Any]])->dict[str,Any]: ...

class ResearchPipeline:
    def __init__(self,root:Path|str|None=None):
        self.root=Path(root) if root else ROOT
        self.loader=RuleLoader(self.root)
        self.source_registry=self.loader.registry
        self.sources=self.loader.sources
        self.schemas={}
        refs=Registry()
        for p in sorted((self.root/"schemas").glob("*.schema.json")):
            schema=load(p); schema["$id"]=p.resolve().as_uri(); self.schemas[p.name]=schema
            refs=refs.with_resource(schema["$id"],Resource.from_contents(schema))
        self.refs=refs
        self.checker=FormatChecker()
        self.audit_path=self.root/"state"/"audit.jsonl"

    def validate(self,obj,schema_name):
        schema=self.schemas.get(schema_name)
        if not schema: raise PipelineError(f"schema not found: {schema_name}")
        errs=sorted(Draft202012Validator(schema,registry=self.refs,format_checker=self.checker).iter_errors(obj),key=lambda e:(list(map(str,e.path)),e.message))
        if errs: raise PipelineError(f"{schema_name}: {errs[0].message}")
        return obj

    def _audit_events(self):
        if not self.audit_path.exists(): return []
        events=[]; previous=None
        for line_no,line in enumerate(self.audit_path.read_text(encoding="utf-8").splitlines(),1):
            try: event=json.loads(line)
            except Exception as exc: raise PipelineError(f"malformed audit event line {line_no}") from exc
            self.validate(event,"audit-event.schema.json")
            raw={k:v for k,v in event.items() if k!="event_hash"}
            if event["previous_event_hash"]!=previous or event["event_hash"]!=digest(raw):
                raise PipelineError(f"audit hash chain invalid at line {line_no}")
            previous=event["event_hash"]; events.append(event)
        return events

    def audit(self,event_type,actor,subject_id,payload):
        events=self._audit_events(); prev=events[-1]["event_hash"] if events else None
        base={"event_id":"evt-"+digest([event_type,subject_id,payload,prev])[:20],"event_type":event_type,
          "occurred_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),"actor":actor,
          "subject_id":subject_id,"payload_hash":digest(payload),"details":payload,"previous_event_hash":prev}
        event={**base,"event_hash":digest(base)}; self.validate(event,"audit-event.schema.json")
        self.audit_path.parent.mkdir(parents=True,exist_ok=True)
        with self.audit_path.open("a",encoding="utf-8",newline="\n") as f:f.write(json.dumps(event,separators=(",",":"))+"\n")
        return event

    def validate_snapshot_sources(self,snapshot):
        ids=set(self.sources)
        for row in snapshot["sources_considered"]:
            sid=row["source_id"]
            if sid not in ids: raise PipelineError(f"unknown source ID: {sid}")
            state=row["verification"]; reg=self.sources[sid]
            expected_flags=(bool(reg.get("url_reachable")),bool(reg.get("content_accessed")),bool(reg.get("content_verified")),bool(reg.get("effective_date_verified")))
            actual_flags=(state["url_reachable"],state["content_accessed"],state["content_verified"],state["effective_date_verified"])
            if actual_flags!=expected_flags or state["applicability_verified"]!=bool(reg.get("applicability_verified")):
                raise PipelineError(f"snapshot verification flags differ from source registry: {sid}")
            if state["applicability_verified"]: raise PipelineError("source applicability is question-specific and cannot be inherited from a registry-level flag")
            tier=state["state"]
            expected=("EFFECTIVE_DATE_VERIFIED" if state["effective_date_verified"] else "CONTENT_VERIFIED" if state["content_verified"] else "CONTENT_ACCESSED" if state["content_accessed"] else "URL_REACHABLE" if state["url_reachable"] else "DISCOVERED")
            if state["state"]=="SOURCE_NOT_VERIFIED" and not any(state[k] for k in ("url_reachable","content_accessed","content_verified","effective_date_verified","applicability_verified")): continue
            if state["state"]!=expected: raise PipelineError(f"source verification state does not match evidence flags: {sid}")
        refs=set()
        for group,level in (("primary_sources","primary"),("court_sources","court_authority"),("official_guidance","official_guidance"),("secondary_sources","secondary")):
            refs.update(snapshot[group])
            for sid in snapshot[group]:
                if sid not in ids: raise PipelineError(f"unknown source ID: {sid}")
                if self.sources[sid].get("authority_level")!=level: raise PipelineError(f"source hierarchy mismatch for {sid}; expected {level}")
        if not refs.issubset(ids): raise PipelineError("source classification contains unknown ID")
        for p in snapshot["relevant_provisions"]:
            if p["source_id"] not in ids: raise PipelineError(f"unknown provision source ID: {p['source_id']}")
            if p["verified"]:
                source=self.sources[p["source_id"]]
                normalized=lambda s:re.sub(r"[^a-z0-9]","",s.lower())
                if not source.get("content_verified") or not any(normalized(p["provision"]) in normalized(x) or normalized(x) in normalized(p["provision"]) for x in source.get("relevant_provisions",[])):
                    raise PipelineError(f"unverified/fabricated provision reference: {p['source_id']} {p['provision']}")

    def create_research(self,request,draft):
        self.validate(request,"research-request.schema.json")
        if not isinstance(draft,dict): raise PipelineError("research result must be a structured object")
        for key in ("sources_considered","primary_sources","court_sources","official_guidance","secondary_sources","relevant_provisions","facts_required","uncertainties","conflicting_sources","confidence_basis"):
            if key in draft and not isinstance(draft[key],list):raise PipelineError(f"research output field must be an array: {key}")
        for row in draft.get("sources_considered",[]):
            if not isinstance(row,dict) or not isinstance(row.get("source_id"),str):raise PipelineError("each considered source must provide a source_id")
        as_of=request.get("as_of_date") or datetime.now(timezone.utc).date().isoformat()
        item={**draft,"question":request["research_question"],"as_of_date":as_of,
          "transaction_date":request["transaction_date"],"jurisdiction":request["jurisdiction"],
          "topics":request["topics"],"facts":request.get("facts",{})}
        item.setdefault("court_sources",[])
        frozen=[]
        for row in item.get("sources_considered",[]):
            source=self.sources.get(row.get("source_id"))
            if not source: raise PipelineError(f"unknown source ID: {row.get('source_id')}")
            url=bool(source.get("url_reachable"));accessed=bool(source.get("content_accessed"));content=bool(source.get("content_verified"));effective=bool(source.get("effective_date_verified"))
            state="EFFECTIVE_DATE_VERIFIED" if effective else "CONTENT_VERIFIED" if content else "CONTENT_ACCESSED" if accessed else "URL_REACHABLE" if url else "DISCOVERED"
            verification={"state":state,"url_reachable":url,"content_accessed":accessed,"content_verified":content,
              "effective_date_verified":effective,"applicability_verified":bool(source.get("applicability_verified")),"checked_at":None,
              "notes":"Verification status is derived from the source registry; the research draft cannot self-attest."}
            frozen.append({"source_id":source["id"],"title":source["title"],"official_url":source["official_url"],
              "source_type":source["source_type"],"authority_level":source["authority_level"],
              "effective_from":source.get("effective_from"),"effective_to":source.get("effective_to"),
              "version_date":source.get("version_date"),"publication_date":source.get("publication_date"),"retrieved_at":source.get("retrieved_at"),
              "verification":verification})
        item["sources_considered"]=frozen
        for source in frozen:
            for label,source_date in (("retrieval",source["retrieved_at"]),("version",source["version_date"])):
                if source_date and source_date>as_of:raise PipelineError(f"source {label} date is after the frozen research as_of_date: {source['source_id']}")
        item["human_review_required"]=True
        item["snapshot_schema_version"]="1.3.0"
        item["confidence"]=self._confidence(item)
        item["research_id"]="research-"+digest(item)[:20]
        item["snapshot_hash"]=digest(item)
        self.validate(item,"research-snapshot.schema.json"); self.validate_snapshot_sources(item)
        target=self.root/"research"/"snapshots"/(item["research_id"]+".json"); existed=target.exists()
        write_immutable(target,item)
        if not existed:self.audit("RESEARCH_CREATED","research-agent",item["research_id"],{"snapshot_hash":item["snapshot_hash"]})
        return item

    def _confidence(self,item):
        # AI self-rating is ignored. High is impossible until reviewer and applicability verification exist.
        source_by_id={x["source_id"]:x["verification"] for x in item.get("sources_considered",[])}
        primary=set(item.get("primary_sources",[]))
        verified=any(source_by_id.get(s,{}).get("content_verified") and source_by_id.get(s,{}).get("effective_date_verified") for s in primary)
        provision=any(x.get("verified") for x in item.get("relevant_provisions",[]))
        if verified and provision and not item.get("conflicting_sources") and not item.get("uncertainties"): return "medium"
        return "low"

    def read_snapshot(self,research_id):
        item=load(self.root/"research"/"snapshots"/(research_id+".json"))
        self.validate(item,"research-snapshot.schema.json")
        claimed=item.get("snapshot_hash"); material={k:v for k,v in item.items() if k!="snapshot_hash"}
        if claimed!=digest(material): raise PipelineError("research snapshot hash mismatch")
        return item

    def create_candidate(self,candidate):
        self.validate(candidate,"rule-candidate.schema.json")
        snap=self.read_snapshot(candidate["research_id"])
        if candidate["status"]!="PROPOSED" or candidate["author"]!="research-agent" or not candidate["review_required"]:
            raise PipelineError("candidate must start PROPOSED, authored by research-agent, and require review")
        if self._candidate_path(candidate["candidate_id"],required=False):raise PipelineError("candidate ID already exists in a lifecycle state")
        evidence_ids={x["source_id"] for x in candidate["evidence"]}
        snapshot_sources={x["source_id"]:x for x in snap["sources_considered"]};snapshot_ids=set(snapshot_sources)
        if not evidence_ids.issubset(snapshot_ids): raise PipelineError("candidate cites source absent from frozen research snapshot")
        for ev in candidate["evidence"]:
            src=snapshot_sources.get(ev["source_id"])
            if not src: raise PipelineError(f"unknown source ID in frozen snapshot: {ev['source_id']}")
            if not src["verification"].get("content_verified"): raise PipelineError(f"candidate relies on unverified source: {ev['source_id']}")
            if not any(ev["provision"]==p["provision"] and p["verified"] for p in snap["relevant_provisions"] if p["source_id"]==ev["source_id"]):
                raise PipelineError("candidate provision not verified in the frozen snapshot")
            ver=src.get("version_date") or (src["verification"].get("checked_at") or "")[:10]
            if ver and ver not in ev["source_version"]: raise PipelineError(f"candidate source version does not match frozen research source: {ev['source_id']}")
        target=self.root/"rules"/"proposed"/(candidate["candidate_id"]+".json");existed=target.exists()
        write_immutable(target,candidate)
        if not existed:self.audit("CANDIDATE_CREATED","research-agent",candidate["candidate_id"],{"research_id":candidate["research_id"]})
        return candidate

    def read_candidate(self,candidate_id):
        c=load(self.root/"rules"/"proposed"/(candidate_id+".json")); self.validate(c,"rule-candidate.schema.json"); return c

    def _candidate_path(self,candidate_id,required=True):
        for folder in ("proposed","rejected","superseded"):
            path=self.root/"rules"/folder/(candidate_id+".json")
            if path.exists():return path
        if required:raise PipelineError(f"candidate not found in lifecycle stores: {candidate_id}")
        return None

    def _move_candidate(self,candidate_id,target_folder):
        source=self._candidate_path(candidate_id);target=self.root/"rules"/target_folder/source.name
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():raise PipelineError(f"lifecycle record already exists: {target}")
        source.replace(target);return target

    def review_candidate(self,candidate_id):
        c=self.read_candidate(candidate_id); snap=self.read_snapshot(c["research_id"])
        source_rows={x["source_id"]:x["verification"] for x in snap["sources_considered"]}
        frozen_sources={x["source_id"]:x for x in snap["sources_considered"]}
        missing=[]; unsupported=[]
        verified_effective_basis=False
        for ev in c["evidence"]:
            state=source_rows.get(ev["source_id"],{})
            if not state.get("content_verified"): missing.append(f"Source content is not verified: {ev['source_id']}")
            if frozen_sources.get(ev["source_id"],{}).get("authority_level")=="primary" and state.get("effective_date_verified"):
                verified_effective_basis=True
        if not verified_effective_basis:missing.append("A primary legal source supporting the candidate effective start date is not verified.")
        primary_effective_dates={frozen_sources[e["source_id"]].get("effective_from") for e in c["evidence"] if e["source_id"] in frozen_sources and frozen_sources[e["source_id"]].get("authority_level")=="primary" and source_rows.get(e["source_id"],{}).get("effective_date_verified")}
        if c["effective_from"] not in primary_effective_dates:missing.append("Candidate effective_from does not match a verified primary source commencement date.")
        if c["effective_to"] and c["effective_to"]<=c["effective_from"]:missing.append("Candidate effective interval is invalid.")
        if snap["conflicting_sources"]: missing.extend(snap["conflicting_sources"])
        if snap["uncertainties"]: missing.extend(snap["uncertainties"])
        if snap["confidence"]=="low": missing.append("Research confidence is low.")
        frozen_sources={x["source_id"]:x for x in snap["sources_considered"]}
        for e in c["evidence"]:
            if e["source_id"] not in frozen_sources: unsupported.append(f"Unknown source in frozen research: {e['source_id']}")
        any_primary=any(frozen_sources[e["source_id"]]["authority_level"]=="primary" for e in c["evidence"] if e["source_id"] in frozen_sources)
        if not any_primary: missing.append("No primary legal source supports the candidate.")
        compatibility_error=None
        try:
            provisional={k:c[k] for k in ("rule_id","rule_version_id","jurisdiction","topic","effective_from","effective_to","conditions","outcome","evidence","requires","exclusions","human_review_if","description","priority","rule_scope","rule_specificity")}
            provisional["enabled"]=True;self.validate(provisional,"executable-rule.schema.json")
        except Exception as exc:
            compatibility_error=str(exc);missing.append("Candidate is not engine-compatible: "+compatibility_error)
        status="REJECT" if unsupported else "NEEDS_CHANGES" if missing else "APPROVE_FOR_HUMAN_REVIEW"
        checks={"source_quality":{"passed":not missing,"findings":missing},
          "source_version":{"passed":not any(not source_rows.get(e["source_id"],{}).get("content_verified") for e in c["evidence"]),"findings":[] if not any(not source_rows.get(e["source_id"],{}).get("content_verified") for e in c["evidence"]) else ["A cited source version is not content verified"]},
          "legal_basis":{"passed":any_primary,"findings":[] if any_primary else ["Primary source missing"]},
          "rule_conditions":{"passed":bool(c["conditions"]),"findings":[] if c["conditions"] else ["No explicit conditions"]},
          "rule_outcome":{"passed":bool(c["outcome"]),"findings":[] if c["outcome"] else ["No explicit outcome"]},
          "effective_date":{"passed":c["effective_from"] in primary_effective_dates and (not c["effective_to"] or c["effective_to"]>c["effective_from"]),"findings":[] if c["effective_from"] in primary_effective_dates else ["No supporting primary commencement date"]},
          "fact_requirements":{"passed":bool(c["conditions"]),"findings":[]},
          "uncertainty":{"passed":status=="APPROVE_FOR_HUMAN_REVIEW","findings":missing},
          "engine_compatibility":{"passed":compatibility_error is None,"findings":["Engine schema and source checks passed; human still must authorize promotion."] if compatibility_error is None else [compatibility_error]}}
        review={"review_id":"review-"+digest([candidate_id,checks,status])[:20],"candidate_id":candidate_id,
          "research_id":c["research_id"],"status":status,"source_review":checks["source_quality"],
          "legal_basis_review":checks["legal_basis"],"effective_date_review":checks["effective_date"],
          "logic_review":{"conditions":checks["rule_conditions"],"outcome":checks["rule_outcome"],"facts":checks["fact_requirements"],"engine_compatibility":checks["engine_compatibility"]},
          "missing_exceptions":c["known_exceptions"],"unsupported_assertions":unsupported,
          "required_changes":missing,"confidence":"medium" if status=="APPROVE_FOR_HUMAN_REVIEW" else "low",
          "human_review_required":True,"reviewed_at":datetime.now(timezone.utc).isoformat(timespec="seconds")}
        self.validate(review,"rule-review.schema.json")
        review_path=self.root/"rules"/"reviews"/(review["review_id"]+".json")
        if review_path.exists(): return load(review_path)
        write_immutable(review_path,review)
        c["status"]="HUMAN_REVIEW_REQUIRED" if status=="APPROVE_FOR_HUMAN_REVIEW" else "NEEDS_CHANGES" if status=="NEEDS_CHANGES" else "REJECTED"
        # Candidate transition is preserved as an immutable status event; original candidate never rewritten.
        state="HUMAN_REVIEW_REQUIRED" if status=="APPROVE_FOR_HUMAN_REVIEW" else "NEEDS_CHANGES" if status=="NEEDS_CHANGES" else "REJECTED"
        candidate_state="AI_REVIEWED" if status=="APPROVE_FOR_HUMAN_REVIEW" else state
        self.audit("REVIEW_COMPLETED","reviewer-agent",candidate_id,{"review_id":review["review_id"],"status":status,"candidate_state":candidate_state})
        if status=="APPROVE_FOR_HUMAN_REVIEW":self.audit("REVIEW_REQUESTED","reviewer-agent",candidate_id,{"review_id":review["review_id"],"candidate_state":"HUMAN_REVIEW_REQUIRED"})
        if status=="NEEDS_CHANGES": self.audit("CHANGES_REQUESTED","reviewer-agent",candidate_id,{"review_id":review["review_id"]})
        if status=="REJECT":
            self.audit("CANDIDATE_REJECTED","reviewer-agent",candidate_id,{"review_id":review["review_id"]})
            self._move_candidate(candidate_id,"rejected")
        return review

    def latest_review(self,candidate_id):
        reviews=[]
        for p in (self.root/"rules"/"reviews").glob("*.json"):
            obj=load(p)
            if obj.get("candidate_id")==candidate_id: reviews.append(obj)
        if not reviews: raise PipelineError("candidate has no review")
        by_id={x["review_id"]:x for x in reviews}
        ordered=[event["details"].get("review_id") for event in self._audit_events()
                 if event["event_type"]=="REVIEW_COMPLETED" and event["subject_id"]==candidate_id]
        for review_id in reversed(ordered):
            if review_id in by_id:return by_id[review_id]
        return max(reviews,key=lambda x:(x["reviewed_at"],x["review_id"]))

    def approve(self,candidate_id,actor,confirmation):
        if not actor or actor.lower() in {"research-agent","reviewer-agent","ai","llm"}: raise PipelineError("approval actor must be an identified human reviewer")
        if confirmation!="I APPROVE THIS RULE FOR EXECUTION": raise PipelineError("explicit human confirmation phrase did not match")
        c=self.read_candidate(candidate_id); review=self.latest_review(candidate_id)
        if review["status"]!="APPROVE_FOR_HUMAN_REVIEW": raise PipelineError("review must be ready for human approval; AI review cannot approve")
        if self._candidate_state(candidate_id)!="HUMAN_REVIEW_REQUIRED": raise PipelineError("candidate is not in human-review state")
        for ev in c["evidence"]: self._require_current_source(ev["source_id"])
        rule={k:c[k] for k in ("rule_id","rule_version_id","jurisdiction","topic","effective_from","effective_to","conditions","outcome","evidence","requires","exclusions","human_review_if","description","priority","rule_scope","rule_specificity")}
        rule["enabled"]=True
        self.loader.validate_rule(rule)
        snap=self.read_snapshot(c["research_id"])
        candidate_hash=digest(c);review_hash=digest(review);snapshot_hash=snap["snapshot_hash"]
        pinned=[]
        for ev in c["evidence"]:
            source=self.sources[ev["source_id"]]
            pinned.append({"source_id":ev["source_id"],"version_date":source.get("version_date"),
              "research_snapshot_id":snap["research_id"],"provision":ev["provision"],"source_version":ev["source_version"]})
        event=self.audit("HUMAN_APPROVAL",actor,candidate_id,{"review_id":review["review_id"],"review_hash":review_hash,
          "candidate_hash":candidate_hash,"research_id":c["research_id"],"research_snapshot_hash":snapshot_hash,
          "rule_version_id":rule["rule_version_id"],"approved_rule_hash":digest(rule)})
        approval={"approved":True,"approved_at":event["occurred_at"],"approved_by":actor,"review_id":review["review_id"],
          "research_id":c["research_id"],"candidate_id":candidate_id,
          "source_versions":pinned,"approval_event_hash":event["event_hash"],"approved_rule_hash":digest(rule),
          "candidate_hash":candidate_hash,"review_hash":review_hash,"research_snapshot_hash":snapshot_hash}
        approved={"rule":rule,"approval":approval}
        self.validate(approved,"approved-rule.schema.json")
        write_immutable(self.root/"rules"/"approved"/(rule["rule_version_id"]+".json"),approved)
        return approved

    def approval_preview(self,candidate_id):
        c=self.read_candidate(candidate_id); snap=self.read_snapshot(c["research_id"]); review=self.latest_review(candidate_id)
        return {"candidate_id":candidate_id,"candidate_hash":digest(c),"rule_id":c["rule_id"],
          "rule_version_id":c["rule_version_id"],"summary":c["description"],
          "effective_from":c["effective_from"],"effective_to":c["effective_to"],
          "sources":[{"source_id":e["source_id"],"source_version":e["source_version"],"provision":e["provision"]} for e in c["evidence"]],
          "review_id":review["review_id"],"review_status":review["status"],
          "known_limitations":c["known_exceptions"],"unresolved_questions":c["unresolved_questions"],
          "research_snapshot_id":snap["research_id"],"research_snapshot_hash":snap["snapshot_hash"]}

    def _require_current_source(self,source_id):
        source=self.sources[source_id];directory=self.root/"state"/"source_checks"
        checks=sorted((load(p) for p in directory.glob(source_id+"*.json")),key=lambda x:x.get("last_verified_at") or "",reverse=True) if directory.exists() else []
        if not checks or checks[0]["current_check_status"]!="UNCHANGED": raise PipelineError(f"source {source_id} lacks a current UNCHANGED check")
        if checks[0]["last_version_date"]!=source.get("version_date"): raise PipelineError(f"source version changed since research/approval: {source_id}")
        age_limit={"HIGH_CHANGE":90,"ANNUAL_REVIEW":365,"LOW_CHANGE":730,"STATIC_HISTORICAL":None,"LIVE_VERIFICATION_REQUIRED":0}.get(source.get("freshness_class"),0)
        if age_limit==0: raise PipelineError(f"source {source_id} requires live verification and cannot be persisted as current")
        checked=datetime.fromisoformat(checks[0]["last_verified_at"])
        if age_limit is not None and (datetime.now(timezone.utc)-checked).days>age_limit: raise PipelineError(f"source check is stale: {source_id}")

    def _candidate_state(self,candidate_id):
        state="PROPOSED"
        for event in self._audit_events():
            if event["subject_id"]!=candidate_id: continue
            if event["event_type"]=="REVIEW_COMPLETED":
                state=event["details"]["candidate_state"]
            if event["event_type"]=="REVIEW_REQUESTED": state="HUMAN_REVIEW_REQUIRED"
            if event["event_type"]=="HUMAN_APPROVAL": state="APPROVED"
            if event["event_type"]=="CANDIDATE_REJECTED": state="REJECTED"
        return state

    def candidate_status(self,candidate_id):
        obj=load(self._candidate_path(candidate_id));self.validate(obj,"rule-candidate.schema.json")
        return self._candidate_state(candidate_id)

    def reject(self,candidate_id,actor,reason):
        if not actor or not reason: raise PipelineError("actor and rejection reason required")
        self.read_candidate(candidate_id)
        self.audit("CANDIDATE_REJECTED",actor,candidate_id,{"reason":reason})
        self._move_candidate(candidate_id,"rejected")

    def supersede(self,old_version_id,new_version_id,effective_to,actor):
        old=self._find_approved(old_version_id); new=self._find_approved(new_version_id)
        if not actor or old_version_id==new_version_id: raise PipelineError("valid human actor and distinct rule versions required")
        from datetime import date
        try: end=date.fromisoformat(effective_to); start=date.fromisoformat(old["rule"]["effective_from"])
        except (TypeError,ValueError) as exc: raise PipelineError("invalid supersession effective date") from exc
        if end<=start: raise PipelineError("supersession date must follow the old rule start")
        if old["rule"]["rule_id"]!=new["rule"]["rule_id"]: raise PipelineError("superseding version must share rule_id")
        if new["rule"]["effective_from"]!=effective_to: raise PipelineError("new rule effective_from must equal supersession date")
        return self.audit("RULE_SUPERSEDED",actor,old_version_id,{"superseded_by":new_version_id,"effective_to":effective_to})

    def retire(self,rule_version_id,actor,reason):
        self._find_approved(rule_version_id)
        if not actor or not reason: raise PipelineError("human actor and retirement reason required")
        return self.audit("RULE_RETIRED",actor,rule_version_id,{"reason":reason})

    def _find_approved(self,version_id):
        for p in (self.root/"rules"/"approved").glob("*.json"):
            obj=load(p)
            if obj.get("rule",{}).get("rule_version_id")==version_id:return obj
        raise PipelineError(f"approved rule not found: {version_id}")

    def dependencies(self,source_id=None):
        rows=[]
        snapshots=self.root/"research"/"snapshots"
        if snapshots.exists():
            for p in snapshots.glob("*.json"):
                obj=load(p)
                for src in obj.get("sources_considered",[]):
                    if source_id is None or src["source_id"]==source_id:
                        rows.append({"source_id":src["source_id"],"path":str(p.relative_to(self.root)),"research_id":obj.get("research_id"),"stage":"research"})
        for folder in ("proposed","approved","rejected","superseded"):
            d=self.root/"rules"/folder
            if not d.exists(): continue
            for p in d.glob("*.json"):
                obj=load(p); rule=obj.get("rule",obj)
                evidence=rule.get("evidence",[])
                for ev in evidence:
                    if source_id is None or ev["source_id"]==source_id:
                        rows.append({"source_id":ev["source_id"],"path":str(p.relative_to(self.root)),
                          "rule_id":rule.get("rule_id"),"candidate_id":obj.get("candidate_id",obj.get("approval",{}).get("candidate_id")),
                          "research_id":obj.get("research_id",obj.get("approval",{}).get("research_id")),"stage":folder})
        return sorted(rows,key=lambda x:(x["source_id"],x.get("rule_id",x.get("research_id","")),x["stage"]))

    def record_source_check(self,check,actor):
        if not actor or actor.lower() in {"research-agent","reviewer-agent","ai","llm"}: raise PipelineError("source verification requires human/tool operator identity")
        self.validate(check,"source-check.schema.json")
        if check["source_id"] not in self.sources: raise PipelineError("unknown source ID")
        directory=self.root/"state"/"source_checks";directory.mkdir(parents=True,exist_ok=True)
        previous=[load(p) for p in directory.glob(check["source_id"]+"*.json")]
        if any(old==check for old in previous):return check
        if previous and check["last_verified_at"]<=max(x["last_verified_at"] for x in previous):
            raise PipelineError("source checks must have strictly increasing verification timestamps")
        path=directory/(check["source_id"]+("-"+digest(check)[:10] if previous else "")+".json")
        write_immutable(path,check)
        if check["current_check_status"] in {"CHANGED","POSSIBLY_CHANGED"}:
            self.audit("SOURCE_CHANGED",actor,check["source_id"],check)
        return check

    def freshness(self,rule_version_id):
        rule=None; folder=None;approved_meta=None
        for f in ("approved","proposed","rejected","superseded"):
            for p in (self.root/"rules"/f).glob("*.json") if (self.root/"rules"/f).exists() else []:
                obj=load(p); candidate=obj.get("rule",obj)
                if candidate.get("rule_version_id")==rule_version_id: rule=candidate;folder=f;approved_meta=obj.get("approval");break
            if rule:break
        if not rule: raise PipelineError(f"unknown rule: {rule_version_id}")
        if folder=="superseded": return "SUPERSEDED"
        if folder!="approved": return "UNKNOWN"
        events=self._audit_events()
        if any(e["event_type"]=="RULE_RETIRED" and e["subject_id"]==rule_version_id for e in events):return "RETIRED"
        if any(e["event_type"]=="RULE_SUPERSEDED" and e["subject_id"]==rule_version_id for e in events):return "SUPERSEDED"
        statuses=[]
        for ev in rule["evidence"]:
            checks=sorted((load(x) for x in (self.root/"state"/"source_checks").glob(ev["source_id"]+"*.json")),key=lambda x:x.get("last_verified_at") or "",reverse=True)
            statuses.append(checks[0]["current_check_status"] if checks else "UNKNOWN")
            pinned={x["source_id"]:x.get("version_date") for x in (approved_meta or {}).get("source_versions",[])}
            if checks and checks[0].get("last_version_date")!=pinned.get(ev["source_id"]):return "SOURCE_CHANGED"
        if "CHANGED" in statuses or "POSSIBLY_CHANGED" in statuses:return "SOURCE_CHANGED"
        if "UNKNOWN" in statuses:return "UNKNOWN"
        stale_cutoff={"HIGH_CHANGE":90,"ANNUAL_REVIEW":365,"LOW_CHANGE":730,"STATIC_HISTORICAL":None,"LIVE_VERIFICATION_REQUIRED":0}
        for ev in rule["evidence"]:
            source=self.sources[ev["source_id"]]; max_age=stale_cutoff.get(source.get("freshness_class"),0)
            checks=sorted((load(x) for x in (self.root/"state"/"source_checks").glob(ev["source_id"]+"*.json")),key=lambda x:x.get("last_verified_at") or "",reverse=True)
            if max_age==0 or (max_age and checks and (datetime.now(timezone.utc)-datetime.fromisoformat(checks[0]["last_verified_at"])).days>max_age):return "SOURCE_STALE"
        return "CURRENT"

class ResearchAgent:
    """Interface for externally generated draft data; intentionally has no model/network client."""
    def __init__(self,pipeline:ResearchPipeline): self.pipeline=pipeline
    def submit(self,request,draft): return self.pipeline.create_research(request,draft)
    def investigate(self,request,provider:ResearchDraftProvider):
        self.pipeline.validate(request,"research-request.schema.json")
        catalog=[{k:s.get(k) for k in ("id","title","jurisdiction","source_type","official_url","effective_from","effective_to","version_date","retrieved_at","authority_level","freshness_class","url_reachable","content_accessed","content_verified","effective_date_verified","applicability_verified","relevant_provisions")} for s in self.pipeline.source_registry["sources"]]
        draft=provider.research(request,catalog)
        return self.pipeline.create_research(request,draft)

class ReviewerAgent:
    """Independent deterministic checklist reviewer; can never perform final human approval."""
    def __init__(self,pipeline:ResearchPipeline): self.pipeline=pipeline
    def review(self,candidate_id): return self.pipeline.review_candidate(candidate_id)
