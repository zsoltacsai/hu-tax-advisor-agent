"""Deterministic structural, rule-registry, and synthetic engine validation."""
import json
import re
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
SCHEMAS=ROOT/"schemas"
checker=FormatChecker()
errors=[]
schema_map={}
registry_refs=Registry()
counts={"schema_files":0,"instances":0,"negative_probes":0}
for path in sorted(SCHEMAS.glob("*.schema.json")):
    try:
        schema=json.loads(path.read_text(encoding="utf-8"))
        schema["$id"]=path.resolve().as_uri()
        Draft202012Validator.check_schema(schema)
        schema_map[path.name]=schema
        registry_refs=registry_refs.with_resource(schema["$id"],Resource.from_contents(schema))
        counts["schema_files"]+=1
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: schema load/check failed: {exc}")

def load(path):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return None

def validate(obj,schema_name,label):
    schema=schema_map.get(schema_name)
    if schema is None:
        errors.append(f"{label}: missing schema {schema_name}")
        return False
    v=Draft202012Validator(schema,registry=registry_refs,format_checker=checker)
    found=sorted(v.iter_errors(obj),key=lambda e:(list(map(str,e.absolute_path)),e.message))
    counts["instances"]+=1
    for err in found:
        loc=".".join(map(str,err.absolute_path)) or "$"
        errors.append(f"{label} at {loc}: {err.message}")
    return not found

def expect_invalid(obj,schema_name,label):
    schema=schema_map[schema_name]
    v=Draft202012Validator(schema,registry=registry_refs,format_checker=checker)
    if list(v.iter_errors(obj)): counts["negative_probes"]+=1
    else: errors.append(f"negative probe unexpectedly accepted: {label}")

registry_path=ROOT/"sources/registry.json"
src_registry=load(registry_path)
source_ids=set()
if src_registry is not None:
    validate(src_registry,"source-registry.schema.json","sources/registry.json")
    rows=src_registry.get("sources",[])
    ids=[x.get("id") for x in rows]
    if len(ids)!=len(set(ids)): errors.append("duplicate source IDs")
    source_ids=set(ids)
    required=("authority","source_type","title","official_url","effective_from","effective_to",
      "publication_date","retrieved_at","version_date","topics","relevant_provisions","authority_level",
      "freshness_class","url_checked","url_reachable","content_accessed","content_verified","effective_date_verified","applicability_verified","notes")
    missing_meta=[]
    for i,row in enumerate(rows):
        validate(row,"source-entry.schema.json",f"source registry entry[{i}]")
        missing=[k for k in required if k not in row]
        if missing:
            missing_meta.append(row.get("id","?"))
            errors.append(f"source {row.get('id')}: missing mandatory metadata {missing}")
    contract_schemas={
      "customer":"customer-context.schema.json","taxpayer":"taxpayer-context.schema.json",
      "transaction":"transaction-context.schema.json","conclusion":"tax-conclusion.schema.json",
      "review-escalation":"review-escalation.schema.json","evidence":"evidence.schema.json",
      "decision-provenance":"decision-provenance.schema.json","mcp-request":"mcp-request.schema.json",
      "mcp-response":"mcp-response.schema.json","rule-version":"rule-version.schema.json"}
    for path in sorted((ROOT/"fixtures/contracts").glob("*.json")):
        obj=load(path)
        if obj is not None:
            schema_name=contract_schemas.get(path.stem)
            if schema_name: validate(obj,schema_name,str(path.relative_to(ROOT)))
            else: errors.append(f"{path.relative_to(ROOT)}: no schema mapping")
            if path.stem=="evidence" and obj.get("source_id") not in source_ids:
                errors.append(f"{path.relative_to(ROOT)}: broken source reference")
            if path.stem=="decision-provenance":
                for ev in obj.get("evidence",[]):
                    if ev.get("source_id") not in source_ids: errors.append("decision provenance has broken source reference")
    for path in sorted((ROOT/"fixtures/scenarios").glob("*.json")):
        obj=load(path)
        if obj is not None: validate(obj,"scenario-fixture.schema.json",str(path.relative_to(ROOT)))

    # Validate the isolated lifecycle stores, evidence links, snapshots, and executable approved rules.
    from src.tax_engine import TaxEngine
    from src.research_pipeline.workflow import ResearchPipeline
    pipeline=ResearchPipeline(ROOT)
    thresholds=load(ROOT/"rules/thresholds.json")
    if thresholds is not None:
        validate(thresholds,"threshold-registry.schema.json","rules/thresholds.json")
        for i,item in enumerate(thresholds.get("thresholds",[])):
            validate(item,"threshold.schema.json",f"rules/thresholds.json thresholds[{i}]")
            if item.get("source_id") not in source_ids: errors.append(f"broken source reference in threshold {item.get('threshold_id')}")
    for path in sorted((ROOT/"research/snapshots").glob("*.json")):
        obj=load(path)
        if obj is not None:
            validate(obj,"research-snapshot.schema.json",str(path.relative_to(ROOT)))
            try: pipeline.read_snapshot(path.stem)
            except Exception as exc: errors.append(f"{path.relative_to(ROOT)}: snapshot integrity/reference check failed: {exc}")
            for source in obj.get("sources_considered",[]):
                if source.get("source_id") not in source_ids: errors.append(f"broken source reference in {path.name}")
    candidate_ids=set()
    for path in sorted((ROOT/"rules/proposed").glob("*.json")):
        obj=load(path)
        if obj is not None:
            validate(obj,"rule-candidate.schema.json",str(path.relative_to(ROOT)))
            candidate_ids.add(obj.get("candidate_id"))
            if not (ROOT/"research/snapshots"/(obj.get("research_id","")+".json")).exists(): errors.append(f"candidate has broken research reference: {path.name}")
            for ev in obj.get("evidence",[]):
                if ev.get("source_id") not in source_ids: errors.append(f"candidate has unknown source: {path.name}")
    for path in sorted((ROOT/"rules/reviews").glob("*.json")):
        obj=load(path)
        if obj is not None:
            validate(obj,"rule-review.schema.json",str(path.relative_to(ROOT)))
            if obj.get("candidate_id") not in candidate_ids: errors.append(f"review has broken candidate reference: {path.name}")
            if not (ROOT/"research/snapshots"/(obj.get("research_id","")+".json")).exists(): errors.append(f"review has broken research reference: {path.name}")
    for path in sorted((ROOT/"rules/approved").glob("*.json")):
        obj=load(path)
        if obj is not None:
            validate(obj,"approved-rule.schema.json",str(path.relative_to(ROOT)))
            approval=obj.get("approval",{})
            if approval.get("candidate_id") not in candidate_ids: errors.append(f"approved rule has broken candidate reference: {path.name}")
            if not (ROOT/"research/snapshots"/(approval.get("research_id","")+".json")).exists(): errors.append(f"approved rule has broken research reference: {path.name}")
    for path in sorted((ROOT/"state/source_checks").glob("*.json")):
        obj=load(path)
        if obj is not None:
            validate(obj,"source-check.schema.json",str(path.relative_to(ROOT)))
            if obj.get("source_id") not in source_ids:errors.append(f"source check has unknown source reference: {path.name}")
    try:
        engine=TaxEngine(ROOT)
        pipeline._audit_events()
        print(f"Executable approved rules loaded: {len(engine.rules)}; threshold records loaded: {len(engine.thresholds)}")
        print(f"Research snapshots: {len(list((ROOT/'research/snapshots').glob('*.json')))}; proposed candidates: {len(list((ROOT/'rules/proposed').glob('*.json')))}")
    except Exception as exc:
        errors.append(f"rule/source provenance validation failed: {exc}")

# Every non-fragment schema reference must resolve to a local schema file.
broken_refs=[]
for name,schema in schema_map.items():
    def walk(node):
        if isinstance(node,dict):
            ref=node.get("$ref")
            if isinstance(ref,str) and not ref.startswith("#"):
                target=ref.split("#",1)[0]
                if target not in schema_map: broken_refs.append(f"{name}: {ref}")
            for val in node.values(): walk(val)
        elif isinstance(node,list):
            for val in node: walk(val)
    walk(schema)
for item in broken_refs: errors.append("broken schema reference "+item)

# Check relative Markdown links, in addition to schema and source-ID references.
broken_docs=[]
for md in ROOT.rglob("*.md"):
    if ".git" in md.parts: continue
    text=md.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)",text):
        target=target.strip().split("#",1)[0]
        if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:",target): continue
        if not (md.parent/target).resolve().exists():
            broken_docs.append(f"{md.relative_to(ROOT)} -> {target}")
for item in broken_docs: errors.append("broken documentation link "+item)

# Negative and positive probes required by the Phase 2 specification.
if src_registry and src_registry.get("sources"):
    source=dict(src_registry["sources"][0])
    missing=dict(source); missing.pop("title",None)
    expect_invalid(missing,"source-entry.schema.json","missing mandatory field")
    bad_enum=dict(source); bad_enum["authority_level"]="legislation"
    expect_invalid(bad_enum,"source-entry.schema.json","invalid authority enum")
    bad_date=dict(source); bad_date["retrieved_at"]="2026-02-31"
    expect_invalid(bad_date,"source-entry.schema.json","malformed calendar date")
    bad_jurisdiction=dict(source); bad_jurisdiction["jurisdiction"]="ZZ"
    expect_invalid(bad_jurisdiction,"source-entry.schema.json","unsupported jurisdiction")
    decision=load(ROOT/"fixtures/contracts/decision-provenance.json")
    invalid_confidence=dict(decision); invalid_confidence["confidence"]="certain"
    expect_invalid(invalid_confidence,"decision-provenance.schema.json","invalid confidence")
    positive=load(ROOT/"fixtures/contracts/conclusion.json")
    if positive is None or not validate(positive,"tax-conclusion.schema.json","valid fixture acceptance"):
        errors.append("valid conclusion fixture was not accepted")
    else: counts["negative_probes"]+=1

scenario_count=len(list((ROOT/"fixtures/scenarios").glob("*.json")))
print(f"Schema files valid: {counts['schema_files']}")
print(f"Registry entries: {len(src_registry.get('sources',[])) if src_registry else 0}")
if src_registry:
    checked=sum(1 for item in src_registry.get("sources",[]) if item.get("url_checked"))
    content=sum(1 for item in src_registry.get("sources",[]) if item.get("content_verified"))
    print(f"URLs marked checked: {checked}; source content marked verified: {content}")
print(f"Fixtures/instances validated: {counts['instances']}")
print(f"Scenario fixtures: {scenario_count}")
print(f"Validation probes passed: {counts['negative_probes']}/6 (5 rejected invalid cases + 1 valid accepted)")
print(f"Duplicate source IDs: {'none' if src_registry and len(src_registry['sources'])==len(set(x['id'] for x in src_registry['sources'])) else 'found'}")
print(f"Broken internal references: {'none' if not broken_refs and not broken_docs else 'found'}")
print(f"Missing mandatory registry metadata: {'none' if src_registry and all(all(k in x for k in required) for x in src_registry['sources']) else 'found'}")
malformed_dates=any(re.search(r"\bdate\b|retrieved_at",e.lower()) for e in errors)
print(f"Malformed dates: {'found' if malformed_dates else 'none'}")
if errors:
    print("VALIDATION FAILED")
    for e in errors: print(" - "+e)
    sys.exit(1)
print("VALIDATION PASSED")
