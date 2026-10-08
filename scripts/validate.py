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
      "mcp-response":"mcp-response.schema.json","rule-version":"rule-version.schema.json",
      "vat-operational-stages":"vat-operational-stages.schema.json",
      "article196-assessment":"article196-assessment.schema.json",
      "cross-border-assessment":"cross-border-assessment.schema.json"}
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
    cross_fixture=ROOT/"fixtures/cross_border/de-general-b2b-synthetic.json"
    if cross_fixture.exists():
        obj=load(cross_fixture)
        if obj is not None: validate(obj,"cross-border-assessment.schema.json",str(cross_fixture.relative_to(ROOT)))

    # Validate the isolated lifecycle stores, evidence links, snapshots, and executable approved rules.
    from src.tax_engine import TaxEngine
    from src.research_pipeline.workflow import ResearchPipeline, digest
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
            if path.name=="phase5.5-readiness.json":
                validate(obj,"phase5-readiness.schema.json",str(path.relative_to(ROOT)))
                if not (ROOT/"research/snapshots"/(obj.get("research_id","")+".json")).exists(): errors.append("Phase 5.5 readiness has broken research reference")
                for assessment in obj.get("candidate_assessments",[]):
                    candidate=load(ROOT/"rules/proposed"/(assessment.get("candidate_id","")+".json"))
                    if candidate is None or digest(candidate)!=assessment.get("candidate_hash"): errors.append("Phase 5.5 readiness candidate hash/reference mismatch")
                    if assessment.get("status")=="READY_FOR_HUMAN_REVIEW" and assessment.get("blockers"): errors.append("readiness marked ready with blockers")
            else:
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
    phase56=ROOT/"rules/country-candidates/phase5.6"
    phase56_candidate_ids=set()
    candidate_hashes={}
    for path in sorted((phase56/"candidates").glob("*.json")) if (phase56/"candidates").exists() else []:
        obj=load(path)
        if obj is None: continue
        validate(obj,"country-rule-candidate.schema.json",str(path.relative_to(ROOT)))
        phase56_candidate_ids.add(obj.get("candidate_id"))
        material={k:v for k,v in obj.items() if k!="candidate_hash"}
        if obj.get("candidate_hash")!=digest(material): errors.append(f"country candidate hash mismatch: {path.name}")
        candidate_hashes[obj.get("candidate_id")]=obj.get("candidate_hash")
        snapshot_path=ROOT/"research/snapshots"/(obj.get("research_id","")+".json")
        if not snapshot_path.exists(): errors.append(f"Phase 5.6 candidate has broken research reference: {path.name}")
        else:
            snap=load(snapshot_path)
            if snap and obj.get("research_hash")!=snap.get("snapshot_hash"): errors.append(f"Phase 5.6 candidate research hash mismatch: {path.name}")
            if snap:
                frozen={x.get("source_id"):x for x in snap.get("sources_considered",[])}
                for ev in obj.get("evidence",[]):
                    pin=frozen.get(ev.get("source_id"))
                    if pin is None: errors.append(f"Phase 5.6 evidence source absent from snapshot: {path.name}/{ev.get('source_id')}")
                    elif not pin.get("verification",{}).get("content_verified"): errors.append(f"Phase 5.6 evidence relies on unverified source text: {path.name}/{ev.get('source_id')}")
                    elif ev.get("source_version")!=(pin.get("version_date") or "accessed-2026-10-08"): errors.append(f"Phase 5.6 source version pin mismatch: {path.name}/{ev.get('source_id')}")
                    if not any(x.get("source_id")==ev.get("source_id") and x.get("provision")==ev.get("provision") and x.get("verified") for x in snap.get("relevant_provisions",[])):
                        errors.append(f"Phase 5.6 evidence provision absent from verified research: {path.name}/{ev.get('source_id')}/{ev.get('provision')}")
        for ev in obj.get("evidence",[]):
            if ev.get("source_id") not in source_ids: errors.append(f"Phase 5.6 candidate has unknown source: {path.name}")
    phase56_review_ids=set()
    phase56_reviews={}
    for path in sorted((phase56/"reviews").glob("*.json")) if (phase56/"reviews").exists() else []:
        obj=load(path)
        if obj is None: continue
        validate(obj,"country-rule-review.schema.json",str(path.relative_to(ROOT)))
        phase56_review_ids.add(obj.get("candidate_id"))
        phase56_reviews[obj.get("candidate_id")]=obj
        material={k:v for k,v in obj.items() if k!="review_hash"}
        if obj.get("review_hash")!=digest(material): errors.append(f"Phase 5.6 review hash mismatch: {path.name}")
        if obj.get("candidate_id") not in phase56_candidate_ids: errors.append(f"Phase 5.6 review has missing candidate: {path.name}")
        if obj.get("candidate_hash")!=candidate_hashes.get(obj.get("candidate_id")): errors.append(f"Phase 5.6 review candidate hash mismatch: {path.name}")
        if obj.get("status") not in {"READY_FOR_HUMAN_REVIEW","NEEDS_CHANGES","BLOCKED","REJECTED"}: errors.append(f"Phase 5.6 review has invalid lifecycle status: {path.name}")
    if phase56_candidate_ids!=phase56_review_ids: errors.append("Phase 5.6 candidates/reviews are not a one-to-one set")
    for candidate_id,review in phase56_reviews.items():
        candidate=next((load(p) for p in (phase56/"candidates").glob("*.json") if (load(p) or {}).get("candidate_id")==candidate_id),None)
        if candidate and candidate.get("status")!=review.get("status"): errors.append(f"Phase 5.6 candidate/review status mismatch: {candidate_id}")
        if review.get("status")=="READY_FOR_HUMAN_REVIEW" and (set(review.get("checklist",{}).values())!={"PASS"} or "independent" not in review.get("reviewer_type","").lower()):
            errors.append(f"Phase 5.6 ready status lacks all-pass independent review: {candidate_id}")
    pack_path=ROOT/"jurisdictions/registry.json"
    if pack_path.exists():
        pack_data=load(pack_path)
        if pack_data:
            validate(pack_data,"country-pack-registry.schema.json",str(pack_path.relative_to(ROOT)))
            packs={x.get("country"):x for x in pack_data.get("packs",[])}
            if len(packs)!=len(pack_data.get("packs",[])): errors.append("duplicate destination country pack")
            for country,pack in packs.items():
                if pack.get("status")=="EXECUTABLE" and not pack.get("approved_rule_version_ids"): errors.append(f"executable country pack has no approved rule: {country}")
                for cid in pack.get("candidate_ids",[]):
                    if cid not in phase56_candidate_ids: errors.append(f"country pack has broken candidate reference: {country}/{cid}")
                rid=pack.get("research_id")
                if rid and not (ROOT/"research/snapshots"/(rid+".json")).exists(): errors.append(f"country pack has broken research reference: {country}/{rid}")
    adviser_store=ROOT/"rules/adviser_reviews"
    for path in sorted(adviser_store.glob("*.json")) if adviser_store.exists() else []:
        obj=load(path)
        if obj is None: continue
        validate(obj,"adviser-review-record.schema.json",str(path.relative_to(ROOT)))
        response=obj.get("response",{})
        cid=response.get("candidate_id")
        candidate_path=phase56/"candidates"/(cid+".json")
        if not candidate_path.exists(): errors.append(f"adviser response has unknown candidate: {path.name}")
        else:
            candidate=load(candidate_path)
            expected_hash=digest({k:v for k,v in candidate.items() if k!="candidate_hash"})
            if response.get("candidate_hash")!=expected_hash or candidate.get("candidate_hash")!=expected_hash: errors.append(f"adviser response candidate hash mismatch: {path.name}")
            if response.get("research_id")!=candidate.get("research_id"): errors.append(f"adviser response research linkage mismatch: {path.name}")
            snapshot_path=ROOT/"research/snapshots"/(response.get("research_id","")+".json")
            snapshot=load(snapshot_path) if snapshot_path.exists() else None
            if not snapshot or response.get("research_hash")!=snapshot.get("snapshot_hash"): errors.append(f"adviser response snapshot hash mismatch: {path.name}")
        if obj.get("response_hash")!=digest(response): errors.append(f"adviser response content hash mismatch: {path.name}")
        if obj.get("execution_approval_created") is not False: errors.append(f"adviser response claims execution approval: {path.name}")
        if obj.get("adviser_status")=="ADVISER_APPROVED" and response.get("decision")!="APPROVE_AS_PROPOSED": errors.append(f"adviser status/decision mismatch: {path.name}")
    dossier=ROOT/"docs/adviser-review"
    required_adviser_docs=["START_HERE.md","VAT_ADVISER_REVIEW_PACKAGE.md","REFERENCE_SCENARIO.json","FACT_MODEL_REVIEW.md","ASSUMPTIONS.md","OPEN_ISSUES.md","EFFECTIVE_DATE_REVIEW.md","SOURCE_INDEX.md","adviser-response.schema.json"]
    candidate_sheet_names=["01_ARTICLE_196_ELIGIBILITY.md","02_DE_REVERSE_CHARGE.md","03_HU_SUPPLIER_VAT_CHARGING.md","04_ARTICLE_219A_INVOICE_JURISDICTION.md","05_EU_INVOICE_METADATA.md","06_HU_INVOICE_IMPLEMENTATION.md","07_ARTICLE_262_RECAP.md","08_HU_A60.md"]
    for name in required_adviser_docs+candidate_sheet_names:
        if not (dossier/name).is_file(): errors.append(f"missing adviser review package document: {name}")
    expected_sections=["Question","Proposed rule","Required facts","Known exclusions","Primary legal sources","Supporting guidance","Effective-date basis","Current interpretation","Known uncertainty","Current blocker","Questions for adviser","Possible adviser decision"]
    for name in candidate_sheet_names:
        path=dossier/name
        if path.is_file():
            headings=re.findall(r"^## (.+)$",path.read_text(encoding="utf-8"),re.MULTILINE)
            if headings!=expected_sections: errors.append(f"adviser review sheet section/order mismatch: {name}")
    portable=ROOT/"dist/hu-tax-adviser-review-package"
    manifest_path=portable/"MANIFEST.json"
    if not manifest_path.is_file(): errors.append("portable adviser package manifest missing")
    else:
        manifest=load(manifest_path)
        if manifest:
            material={k:v for k,v in manifest.items() if k!="package_hash"}
            if manifest.get("package_hash")!=digest(material): errors.append("portable adviser package manifest hash mismatch")
            if set(manifest.get("files",{}))!={"START_HERE.md","VAT_ADVISER_REVIEW_PACKAGE.md","REFERENCE_SCENARIO.json","FACT_MODEL_REVIEW.md","ASSUMPTIONS.md","OPEN_ISSUES.md","EFFECTIVE_DATE_REVIEW.md","SOURCE_INDEX.md","adviser-response.schema.json",*candidate_sheet_names}:
                errors.append("portable adviser package file manifest does not match the curated handoff contents")
            if len(manifest.get("candidate_ids",[]))!=8 or set(manifest.get("candidate_ids",[]))-phase56_candidate_ids:
                errors.append("portable adviser package candidate manifest is incomplete or unknown")
            for name,expected_hash in manifest.get("files",{}).items():
                file_path=portable/name
                if not file_path.is_file(): errors.append(f"portable adviser package file missing: {name}")
                elif digest(file_path.read_text(encoding="utf-8"))!=expected_hash: errors.append(f"portable adviser package file hash mismatch: {name}")
            actual_files={x.name for x in portable.iterdir() if x.is_file() and x.name!="MANIFEST.json"}
            if actual_files!=set(manifest.get("files",{})): errors.append("portable adviser package contains unmanifested or missing files")
            if manifest.get("contains_customer_data") is not False or manifest.get("contains_execution_approval") is not False: errors.append("portable adviser package has prohibited contents")
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
try:
    from src.tax_engine.dependencies import load_dependencies
    dependency_graph=load_dependencies(ROOT/"rules/dependencies.json")
    print(f"Dependency graph valid and acyclic: {len(dependency_graph)} stages")
except Exception as exc:
    errors.append(f"dependency graph invalid: {exc}")
try:
    cross_graph=load(ROOT/"rules/cross-border-dependencies.json")
    from src.tax_engine.dependencies import validate_acyclic
    validate_acyclic(cross_graph["stages"])
    print(f"Cross-border dependency graph valid and acyclic: {len(cross_graph['stages'])} stages")
except Exception as exc:
    errors.append(f"cross-border dependency graph invalid: {exc}")
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
