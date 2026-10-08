"""Phase 5.5 source and scenario foundation tests; no tax outcome is computed."""
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from src.tax_engine.dependencies import load_dependencies, unmet_dependencies, validate_acyclic

ROOT = Path(__file__).resolve().parents[1]


class Phase55FoundationTests(unittest.TestCase):
    def test_dependency_graph_is_acyclic_and_downstream_fails_closed(self):
        graph = load_dependencies(ROOT / "rules/dependencies.json")
        self.assertGreaterEqual(len(graph), 8)
        self.assertIn("reverse_charge", unmet_dependencies("invoice_treatment", graph, {"supplier_vat_charging": "determined"}))
        self.assertEqual(unmet_dependencies("aam", graph, {"taxpayer_vat_status": "determined", "tax_year_turnover": "determined", "election_and_eligibility_facts": "determined"}), [])

    def test_dependency_cycle_rejected(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            validate_acyclic({"a": {"depends_on": ["b"]}, "b": {"depends_on": ["a"]}})

    def test_article196_fixture_is_valid_and_vat_id_does_not_decide_status(self):
        schema = json.loads((ROOT / "schemas/article196-assessment.schema.json").read_text(encoding="utf-8"))
        fixture = json.loads((ROOT / "fixtures/contracts/article196-assessment.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(fixture)
        self.assertEqual(fixture["facts"]["customer_vat_id"]["verification_state"], "VERIFIED")
        self.assertEqual(fixture["facts"]["customer_taxable_person_status"]["state"], "UNKNOWN")
        self.assertEqual(fixture["outcome"], "NOT_ASSESSED")

    def test_candidate_readiness_is_blocked_and_hash_linked(self):
        record = json.loads((ROOT / "rules/reviews/phase5.5-readiness.json").read_text(encoding="utf-8"))
        self.assertEqual(len(record["candidate_assessments"]), 5)
        self.assertEqual(record["ready_candidates"], [])
        self.assertFalse(record["human_approval_prompt_required"])
        self.assertTrue(all(row["status"] == "BLOCKED" and row["blockers"] for row in record["candidate_assessments"]))


if __name__ == "__main__":
    unittest.main()
