"""Phase 5 synthetic-only tests for downstream-stage boundaries."""
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from src.tax_engine import TaxEngine

ROOT = Path(__file__).resolve().parents[1]


class Phase5BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = TaxEngine(ROOT)

    def test_no_unapproved_phase5_rule_is_loaded(self):
        self.assertEqual({r["rule_version_id"] for r in self.engine.rules}, {
            "eu-vat-services-b2b-general@1", "eu-vat-services-b2c-general@1"})

    def test_all_phase5_candidate_reviews_remain_non_executable(self):
        from src.research_pipeline.workflow import ResearchPipeline
        pipe = ResearchPipeline(ROOT)
        candidates = list((ROOT / "rules/proposed").glob("candidate-phase5-*.json"))
        self.assertEqual(len(candidates), 5)
        for path in candidates:
            candidate = json.loads(path.read_text(encoding="utf-8"))
            review = pipe.latest_review(candidate["candidate_id"])
            self.assertEqual(candidate["status"], "PROPOSED")
            self.assertEqual(review["status"], "NEEDS_CHANGES")
            self.assertNotIn(candidate["rule_version_id"], {r["rule_version_id"] for r in self.engine.rules})

    def test_synthetic_scenarios_never_leap_to_operational_conclusions(self):
        downstream = {"supplier_vat_charging", "reverse_charge", "invoice_treatment", "eu_recap_reporting", "aam"}
        fixtures = sorted((ROOT / "fixtures/scenarios").glob("phase5-*.json"))
        self.assertEqual(len(fixtures), 6)
        for path in fixtures:
            fixture = json.loads(path.read_text(encoding="utf-8"))
            facts = {k: fixture[k] for k in ("taxpayer", "customer", "transaction")}
            result = self.engine.evaluate(facts, "2026-10-08")
            self.assertEqual(result, self.engine.evaluate(facts, "2026-10-08"))
            for name in downstream:
                stage = next(s for s in result["stages"] if s["stage"] == name)
                self.assertEqual(stage["status"], "not_assessed", (fixture["scenario_id"], name))
            aam = next(s for s in result["stages"] if s["stage"] == "aam")
            self.assertEqual(aam["value"]["aam_effect_on_transaction"], "NOT_ASSESSED")
            if fixture["transaction"]["service_classification"] == "ELECTRONICALLY_SUPPLIED_SERVICE":
                self.assertEqual(result["selected_rule_ids"], [])
            place = next(s for s in result["stages"] if s["stage"] == "place_of_supply")
            jurisdiction = next(s for s in result["stages"] if s["stage"] == "vat_jurisdiction")
            if place["status"] == "determined":
                self.assertEqual(jurisdiction["status"], "partial")
                self.assertEqual(jurisdiction["value"]["place_of_supply_country"], place["value"]["country"])
                self.assertEqual(jurisdiction["evidence"], place["evidence"])
            else:
                self.assertEqual(jurisdiction["status"], "not_assessed")
            if fixture["customer"]["vat_id_evidence_status"] in {"INVALID", "VERIFICATION_UNAVAILABLE", "PROVIDED_UNVERIFIED"}:
                self.assertEqual(next(s for s in result["stages"] if s["stage"] == "reverse_charge")["status"], "not_assessed")
                status = next(s for s in result["stages"] if s["stage"] == "customer_status")
                self.assertEqual(status["value"]["vat_id_evidence_status"], fixture["customer"]["vat_id_evidence_status"])

    def test_operational_contract_fixture_is_schema_valid_and_conservative(self):
        schema = json.loads((ROOT / "schemas/vat-operational-stages.schema.json").read_text(encoding="utf-8"))
        fixture = json.loads((ROOT / "fixtures/contracts/vat-operational-stages.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(fixture)
        for key in ("supplier_vat_charging", "reverse_charge", "invoice_treatment", "eu_recap_reporting", "aam"):
            self.assertEqual(fixture[key]["status"], "not_assessed")


if __name__ == "__main__":
    unittest.main()
