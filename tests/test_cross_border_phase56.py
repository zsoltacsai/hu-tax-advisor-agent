import json
import unittest
from pathlib import Path

from src.tax_engine.cross_border import assess_cross_border, check_destination_conditions, evaluate_destination, screen_article196
from src.research_pipeline.workflow import ResearchPipeline, digest

ROOT = Path(__file__).resolve().parents[1]


def facts(**updates):
    value = {
        "transaction_date": "2026-10-08", "supplier_country": "HU", "supplier_taxable_person": "YES",
        "supplier_destination_establishment": {"country": "DE", "state": "NONE", "intervenes_in_supply": "NOT_APPLICABLE"},
        "customer_country": "DE", "customer_claims_business": True,
        "customer_taxable_person_status": "TAXABLE_PERSON_ACTING_AS_SUCH",
        "customer_vat_id": {"country": "DE", "present": True, "verification": "SYNTHETIC_VALID"},
        "service_classification": "GENERAL_SERVICE", "special_rule_screened": "YES_NO_SPECIAL_RULE",
        "destination_taxability_status": "UNKNOWN",
        "place_of_supply": {"status": "DETERMINED", "country": "DE", "rule_version_id": "eu-vat-services-b2b-general@1", "evidence": []},
        "aam_status": "AAM", "tax_point_status": "NOT_ASSESSED",
    }
    value.update(updates)
    return value


class Phase56CrossBorderTests(unittest.TestCase):
    def test_eu_eligibility_is_separate_from_destination_pack(self):
        result = assess_cross_border(facts(), "2026-10-08", {"DE": {"status": "RESEARCH_ONLY"}})
        self.assertEqual(result["stages"][0]["value"], "ELIGIBLE")
        self.assertEqual(result["stages"][1]["status"], "not_assessed")
        self.assertEqual(result["stages"][1]["value"], "DESTINATION_RULE_NOT_APPROVED")
        ResearchPipeline(ROOT).validate(result, "cross-border-assessment.schema.json")

    def test_unsupported_destination_country(self):
        f = facts(customer_country="IT", supplier_destination_establishment={"country":"IT","state":"NONE","intervenes_in_supply":"NOT_APPLICABLE"}, place_of_supply={"status": "DETERMINED", "country": "IT", "rule_version_id": "eu-vat-services-b2b-general@1", "evidence": []})
        screen = screen_article196(f)
        self.assertEqual(screen["value"], "ELIGIBLE")
        result = evaluate_destination("IT", screen, f, {})
        self.assertEqual(result["value"], "UNSUPPORTED_DESTINATION_IMPLEMENTATION")
        self.assertNotEqual(result["status"], "determined")

    def test_valid_vat_id_does_not_replace_unknown_taxable_status(self):
        result = screen_article196(facts(customer_taxable_person_status="UNKNOWN"))
        self.assertEqual(result["status"], "requires_review")

    def test_taxable_status_does_not_require_vat_id_for_article196_screen(self):
        f = facts(customer_vat_id={"country":"DE", "present": False, "verification": "MISSING"})
        self.assertEqual(screen_article196(f)["value"], "ELIGIBLE")

    def test_non_taxable_legal_entity_requires_identification(self):
        f = facts(customer_taxable_person_status="NON_TAXABLE_LEGAL_PERSON_VAT_IDENTIFIED",
                  customer_vat_id={"country":"DE","present":False,"verification":"MISSING"})
        self.assertEqual(screen_article196(f)["status"], "requires_review")

    def test_supplier_taxable_person_unknown_requires_review(self):
        self.assertEqual(screen_article196(facts(supplier_taxable_person="UNKNOWN"))["status"], "requires_review")

    def test_unresolved_relevant_german_fixed_establishment(self):
        result = screen_article196(facts(supplier_destination_establishment={"country":"DE","state": "EXISTS", "intervenes_in_supply": "UNKNOWN"}))
        self.assertEqual(result["status"], "requires_review")

    def test_participating_german_supplier_establishment_fails_screen(self):
        result = screen_article196(facts(supplier_destination_establishment={"country":"DE","state": "EXISTS", "intervenes_in_supply": "YES"}))
        self.assertEqual(result["value"], "NOT_ELIGIBLE")

    def test_special_service_is_not_general_rule_screened(self):
        result = screen_article196(facts(service_classification="SPECIAL_SERVICE"))
        self.assertEqual(result["status"], "unsupported")

    def test_unknown_service_classification_is_not_supported(self):
        result = screen_article196(facts(service_classification="UNKNOWN"))
        self.assertEqual(result["status"], "unsupported")

    def test_destination_exemption_unknown_never_produces_result(self):
        # Even a research-only DE pack cannot produce a liability determination.
        result = evaluate_destination("DE", {"value": "ELIGIBLE"}, facts(), {"DE": {"status": "RESEARCH_ONLY"}})
        self.assertEqual(result["status"], "not_assessed")
        self.assertEqual(check_destination_conditions("DE", facts())["value"], "DESTINATION_TAXABILITY_UNRESOLVED")

    def test_germany_factual_conditions_can_pass_without_concluding_reverse_charge(self):
        result = check_destination_conditions("DE", facts(destination_taxability_status="REVIEWED_TAXABLE_NO_EXEMPTION_IDENTIFIED"))
        self.assertEqual(result["value"], "PRECONDITIONS_MET")
        self.assertNotEqual(result["value"], "APPLIES")

    def test_invoice_jurisdiction_and_reporting_stay_blocked(self):
        result = assess_cross_border(facts(), "2026-10-08", {"DE": {"status": "RESEARCH_ONLY"}})
        by_name = {s["stage"]: s for s in result["stages"]}
        for stage in ("invoice_jurisdiction", "invoice_metadata", "eu_recap_reporting", "a60_reporting"):
            self.assertEqual(by_name[stage]["status"], "not_assessed")

    def test_aam_and_tax_point_are_isolated(self):
        first = assess_cross_border(facts(aam_status="AAM", tax_point_status="NOT_ASSESSED"), "2026-10-08", {"DE": {"status": "RESEARCH_ONLY"}})
        second = assess_cross_border(facts(aam_status="NOT_AAM", tax_point_status="REVIEWED"), "2026-10-08", {"DE": {"status": "RESEARCH_ONLY"}})
        self.assertEqual(first["stages"][:2], second["stages"][:2])
        self.assertEqual(first["stages"][-2]["status"], "not_assessed")
        self.assertEqual(first["stages"][-1]["status"], "not_assessed")

    def test_conflicting_destination_evidence_requires_review(self):
        f = facts(customer_country="AT")
        result = screen_article196(f)
        self.assertEqual(result["status"], "requires_review")

    def test_no_destination_pack_can_return_applies(self):
        result = evaluate_destination("DE", {"value": "ELIGIBLE"}, facts(), {})
        self.assertEqual(result["value"], "UNSUPPORTED_DESTINATION_IMPLEMENTATION")

    def test_pack_metadata_without_verified_approval_chain_cannot_execute(self):
        pack = {"status":"EXECUTABLE", "approved_rule_version_id":"de-example@1", "effective_from":"2010-01-01", "evidence":[]}
        result = evaluate_destination("DE", {"value":"ELIGIBLE"}, facts(), {"DE":pack})
        self.assertEqual(result["value"], "DESTINATION_RULE_NOT_APPROVED")

    def test_phase56_candidate_and_review_hashes_are_stable_and_blocked(self):
        p = ResearchPipeline(ROOT)
        candidates = sorted((ROOT / "rules/country-candidates/phase5.6/candidates").glob("*.json"))
        reviews = list((ROOT / "rules/country-candidates/phase5.6/reviews").glob("*.json"))
        self.assertEqual(len(candidates), 8)
        self.assertEqual(len(reviews), 8)
        review_by_id = {json.loads(x.read_text(encoding="utf-8"))["candidate_id"]: json.loads(x.read_text(encoding="utf-8")) for x in reviews}
        for path in candidates:
            candidate = json.loads(path.read_text(encoding="utf-8"))
            claimed = candidate["candidate_hash"]
            self.assertEqual(claimed, digest({k: v for k, v in candidate.items() if k != "candidate_hash"}))
            self.assertEqual(candidate["status"], "BLOCKED")
            snap = p.read_snapshot(candidate["research_id"])
            self.assertEqual(candidate["research_hash"], snap["snapshot_hash"])
            review = review_by_id[candidate["candidate_id"]]
            self.assertEqual(review["candidate_hash"], claimed)
            self.assertEqual(review["status"], "BLOCKED")
            self.assertEqual(review["review_hash"], digest({k: v for k, v in review.items() if k != "review_hash"}))

    def test_de_engine_chain_has_no_human_approval(self):
        pack = json.loads((ROOT / "jurisdictions/registry.json").read_text(encoding="utf-8"))["packs"][0]
        self.assertEqual(pack["country"], "DE")
        self.assertEqual(pack["status"], "RESEARCH_ONLY")
        self.assertEqual(pack["approved_rule_version_ids"], [])

    def test_synthetic_germany_chain_end_to_end_is_scoped(self):
        fixture = json.loads((ROOT / "fixtures/cross_border/de-general-b2b-synthetic.json").read_text(encoding="utf-8"))
        result = assess_cross_border(fixture["facts"], fixture["transaction_date"], {"DE": {"status":"RESEARCH_ONLY"}})
        ResearchPipeline(ROOT).validate(result, "cross-border-assessment.schema.json")
        by_name = {x["stage"]: x for x in result["stages"]}
        self.assertEqual(by_name["article_196_eligibility"]["value"], "ELIGIBLE")
        self.assertEqual(by_name["destination_reverse_charge"]["status"], "not_assessed")
        self.assertTrue(all(by_name[x]["status"] == "not_assessed" for x in ("supplier_vat_charging", "invoice_jurisdiction", "invoice_metadata", "eu_recap_reporting", "a60_reporting", "aam_effect", "tax_point")))


if __name__ == "__main__":
    unittest.main()
