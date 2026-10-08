"""Deterministic synthetic tests for the deliberately narrow rule engine."""
import copy
import json
import unittest
import tempfile,shutil
from datetime import datetime,timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from src.tax_engine import RuleConflictError, TaxEngine
from src.tax_engine.thresholds import compare_threshold
from src.tax_engine.rule_selector import resolve_applicable
from src.research_pipeline.workflow import ResearchPipeline,digest

ROOT=Path(__file__).resolve().parents[1]

def reviewed_context(status="B2C", country="HU", service="GENERAL_SERVICE", txdate="2025-03-01"):
    fixture=json.loads((ROOT/"fixtures/scenarios/01-hu-b2c.json").read_text(encoding="utf-8"))
    t,c,x=(fixture[k] for k in ("taxpayer","customer","transaction"))
    t["facts_reviewed"]=True
    c.update({"country":country,"business_establishment_country":country if status=="B2B" else None,
       "customer_type_claimed":"business" if status=="B2B" else "consumer",
       "business_status":"verified_business" if status=="B2B" else "verified_non_business",
       "business_status_evidence":["company_register"] if status=="B2B" else ["consumer_declaration"],
       "status_evidence_reviewed":True,"taxable_person_acting_as_such":status=="B2B","taxable_person_capacity_reviewed":status=="B2B",
       "evidence_country_signals":[{"kind":"business_establishment" if status=="B2B" else "billing","country":country,"observed_at":"2025-03-01T10:00:00Z"}]})
    x.update({"service_classification":service,"classification_reviewed":True,
       "classification_basis":["synthetic reviewed service facts"],"special_place_of_supply_reviewed":True,
       "supplier_establishment_review":"no_relevant_fixed_establishment","recipient_establishment_review":"no_relevant_fixed_establishment",
       "transaction_date":txdate,"tax_point_date":txdate})
    return {"taxpayer":t,"customer":c,"transaction":x}

class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.repo=Path(cls.tmp.name)
        shutil.copytree(ROOT/"schemas",cls.repo/"schemas");shutil.copytree(ROOT/"sources",cls.repo/"sources")
        shutil.copytree(ROOT/"research",cls.repo/"research")
        (cls.repo/"rules").mkdir(parents=True);shutil.copy(ROOT/"rules/thresholds.json",cls.repo/"rules"/"thresholds.json")
        for folder in ("approved","proposed","reviews","rejected","superseded"):(cls.repo/"rules"/folder).mkdir(parents=True,exist_ok=True)
        (cls.repo/"state"/"source_checks").mkdir(parents=True);(cls.repo/"state"/"audit.jsonl").write_text("",encoding="utf-8")
        source_pipe=ResearchPipeline(ROOT);pipeline=ResearchPipeline(cls.repo)
        for candidate_id in ("candidate-eu-vat-services-b2b-general-v1-2026","candidate-eu-vat-services-b2c-general-v1-2026"):
            candidate=source_pipe.read_candidate(candidate_id);review=source_pipe.latest_review(candidate_id)
            snapshot=source_pipe.read_snapshot(candidate["research_id"])
            (cls.repo/"rules/proposed"/(candidate_id+".json")).write_text(json.dumps(candidate),encoding="utf-8")
            (cls.repo/"rules/reviews"/(review["review_id"]+".json")).write_text(json.dumps(review),encoding="utf-8")
            (cls.repo/"research/snapshots"/(snapshot["research_id"]+".json")).write_text(json.dumps(snapshot),encoding="utf-8")
            pipeline.audit("RESEARCH_CREATED","research-agent",snapshot["research_id"],{"snapshot_hash":snapshot["snapshot_hash"]})
            pipeline.audit("CANDIDATE_CREATED","research-agent",candidate_id,{"research_id":snapshot["research_id"]})
            pipeline.audit("REVIEW_COMPLETED","reviewer-agent",candidate_id,{"review_id":review["review_id"],"status":review["status"],"candidate_state":"AI_REVIEWED"})
            pipeline.audit("REVIEW_REQUESTED","reviewer-agent",candidate_id,{"review_id":review["review_id"],"candidate_state":"HUMAN_REVIEW_REQUIRED"})
            for sid in {e["source_id"] for e in candidate["evidence"]}:
                source=pipeline.sources[sid];checked=datetime.now(timezone.utc).isoformat(timespec="microseconds")
                pipeline.record_source_check({"source_id":sid,"last_verified_at":checked,"last_version_date":source.get("version_date"),"current_check_status":"UNCHANGED","notes":"Synthetic unit-test source check; not a repository approval.","checked_by":"Synthetic unit-test operator"},"Synthetic unit-test operator")
            pipeline.approve(candidate_id,"Synthetic unit-test human reviewer","I APPROVE THIS RULE FOR EXECUTION")
        cls.engine=TaxEngine(cls.repo)
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def test_reviewed_b2c_result_is_partial_and_evidenced(self):
        result=self.engine.evaluate(reviewed_context(),"2026-10-08")
        self.assertEqual(result["status"],"PARTIALLY_DETERMINED")
        place=next(s for s in result["stages"] if s["stage"]=="place_of_supply")
        self.assertEqual(place["value"]["country"],"HU")
        self.assertTrue(place["evidence"])
        self.assertEqual(next(s for s in result["stages"] if s["stage"]=="vat_treatment")["status"],"not_assessed")

    def test_reviewed_eu_b2b_general_service_uses_article_44_rule(self):
        result=self.engine.evaluate(reviewed_context("B2B","DE"),"2026-10-08")
        self.assertEqual(result["selected_rule_ids"],["eu-vat-services-b2b-general"])
        self.assertTrue(any("Article 44" in ev["provision"] for ev in result["evidence"]))
        chain=result["provenance"]["rules"][0]
        self.assertEqual(chain["rule_version_id"],"eu-vat-services-b2b-general@1")
        self.assertTrue(chain["candidate_hash"] and chain["review_hash"] and chain["research_snapshot_hash"] and chain["approval_event_hash"])
        self.assertTrue(self.engine.verify_provenance(result))

    def test_reviewed_eu_b2c_general_service_uses_article45(self):
        result=self.engine.evaluate(reviewed_context("B2C","DE"),"2026-10-08")
        self.assertEqual(result["selected_rule_ids"],["eu-vat-services-b2c-general"])
        self.assertEqual(result["provenance"]["rules"][0]["rule_version_id"],"eu-vat-services-b2c-general@1")

    def test_unapproved_article58_never_falls_back_to_general_rules(self):
        data=reviewed_context("B2C","AT","ELECTRONICALLY_SUPPLIED_SERVICE")
        data["transaction"]["article59c_assessment"]="above_threshold"
        applied=self.engine.evaluate(data,"2026-10-08")
        self.assertEqual(applied["status"],"UNSUPPORTED_SCENARIO")
        self.assertEqual(applied["selected_rule_ids"],[])
        data["transaction"]["article59c_assessment"]="not_assessed"
        pending=self.engine.evaluate(data,"2026-10-08")
        self.assertEqual(pending["status"],"CANNOT_DETERMINE")

    def test_establishment_and_special_rule_reviews_are_required(self):
        data=reviewed_context("B2C","DE");data["transaction"]["supplier_establishment_review"]="unresolved"
        self.assertEqual(self.engine.evaluate(data,"2026-10-08")["status"],"REQUIRES_HUMAN_REVIEW")
        data=reviewed_context("B2B","DE");data["customer"]["taxable_person_acting_as_such"]=False
        self.assertEqual(self.engine.evaluate(data,"2026-10-08")["selected_rule_ids"],[])
        data=reviewed_context("B2B","DE");data["transaction"]["special_place_of_supply_reviewed"]=False
        self.assertEqual(self.engine.evaluate(data,"2026-10-08")["status"],"REQUIRES_HUMAN_REVIEW")

    def test_specific_rule_precedes_general_rule(self):
        general=copy.deepcopy(next(r for r in self.engine.rules if r["rule_id"]=="eu-vat-services-b2c-general"))
        specific=copy.deepcopy(general);specific["rule_id"]="synthetic-specific";specific["rule_version_id"]="synthetic-specific@1"
        specific["rule_scope"]="SPECIFIC";specific["rule_specificity"]=100
        self.assertEqual(resolve_applicable([general,specific]),[specific])

    def test_equal_priority_conflicting_outcome_is_detected(self):
        base=copy.deepcopy(next(r for r in self.engine.rules if r["rule_id"]=="eu-vat-services-b2c-general"))
        base["rule_id"]="synthetic-conflicting-rule"
        base["rule_version_id"]="synthetic-conflicting-rule-v1"
        base["outcome"]["value_from"]="customer_location_country"
        data=reviewed_context()
        result=self.engine.evaluate(data,"2026-10-08",extra_rules=[base])
        self.assertEqual(result["status"],"REQUIRES_HUMAN_REVIEW")
        self.assertTrue(any("RULE_CONFLICT" in warning for warning in result["warnings"]))

    def test_historical_date_uses_effective_rule(self):
        old=reviewed_context(txdate="2009-12-31")
        before=self.engine.evaluate(old,"2026-10-08")
        self.assertEqual(before["status"],"UNSUPPORTED_SCENARIO")
        historic=reviewed_context(txdate="2025-03-01")
        after=self.engine.evaluate(historic,"2026-10-08")
        self.assertEqual(after["selected_rule_ids"],["eu-vat-services-b2c-general"])

    def test_unreviewed_classification_never_inferred_from_description(self):
        data=reviewed_context(); data["transaction"]["classification_reviewed"]=False
        data["transaction"]["service_as_described"]="automated electronic SaaS subscription"
        result=self.engine.evaluate(data,"2026-10-08")
        self.assertEqual(result["status"],"CANNOT_DETERMINE")
        self.assertEqual(result["selected_rule_ids"],[])

    def test_customer_business_claim_without_reviewed_proof_does_not_select_b2b(self):
        data=reviewed_context("B2B","DE")
        data["customer"]["status_evidence_reviewed"]=False
        result=self.engine.evaluate(data,"2026-10-08")
        self.assertEqual(result["status"],"CANNOT_DETERMINE")

    def test_conflicting_country_evidence_escalates(self):
        data=reviewed_context("B2B","DE")
        data["customer"]["evidence_country_signals"].append({"kind":"ip","country":"HU","observed_at":"2025-03-01T10:00:00Z"})
        result=self.engine.evaluate(data,"2026-10-08")
        self.assertEqual(result["status"],"REQUIRES_HUMAN_REVIEW")
        self.assertTrue(result["requires_human_review"])

    def test_unsupported_country_is_not_treated_as_non_eu(self):
        data=reviewed_context("B2C","ZZ")
        result=self.engine.evaluate(data,"2026-10-08")
        self.assertEqual(result["status"],"UNSUPPORTED_SCENARIO")

    def test_missing_customer_location_does_not_fall_back(self):
        data=reviewed_context("B2C","HU")
        data["customer"]["evidence_country_signals"]=[]
        result=self.engine.evaluate(data,"2026-10-08")
        self.assertEqual(result["status"],"CANNOT_DETERMINE")

    def test_identical_inputs_are_deterministic_and_schema_valid(self):
        data=reviewed_context()
        a=self.engine.evaluate(data,"2026-10-08"); b=self.engine.evaluate(data,"2026-10-08")
        self.assertEqual(a,b)
        schema=json.loads((ROOT/"schemas/tax-engine-result.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema,format_checker=FormatChecker()).validate(a)

    def test_bad_confidence_and_bad_dates_are_rejected(self):
        result=self.engine.evaluate(reviewed_context(),"2026-10-08")
        schema=json.loads((ROOT/"schemas/tax-engine-result.schema.json").read_text(encoding="utf-8"))
        bad=copy.deepcopy(result); bad["stages"][0]["confidence"]="certain"
        with self.assertRaises(Exception): Draft202012Validator(schema,format_checker=FormatChecker()).validate(bad)
        with self.assertRaises(ValueError): self.engine.evaluate(reviewed_context(),"2026-02-31")

    def test_threshold_is_arithmetic_only_and_currency_safe(self):
        threshold=next(x for x in self.engine.thresholds if x["year"]==2026)
        self.assertEqual(compare_threshold(threshold["amount"],threshold,"HUF",2026)["status"],"at_threshold")
        self.assertEqual(compare_threshold(1,threshold,"EUR",2026)["status"],"unknown")
        self.assertEqual(compare_threshold(None,threshold,"HUF",2026)["status"],"unknown")

    def test_rule_loader_rejects_evidence_free_rule(self):
        rule=copy.deepcopy(self.engine.rules[0]); rule["evidence"]=[]
        with self.assertRaises(Exception): self.engine.loader.validate_rule(rule)

    def test_default_repository_has_no_implicitly_approved_rules(self):
        self.assertEqual(len(TaxEngine(ROOT).rules),len(list((ROOT/"rules"/"approved").glob("*.json"))))
        with self.assertRaises(Exception): TaxEngine(ROOT,rules_path=ROOT/"rules"/"rules.json")

if __name__=="__main__": unittest.main()
