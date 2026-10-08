import unittest
from src.effective_dates import RuleSelectionError, select_rule_version

class EffectiveDateSelectionTests(unittest.TestCase):
    def setUp(self):
        self.rules = [
            {"rule_id":"r-old","lifecycle_status":"historical","effective_from":"2024-01-01","effective_to":"2025-01-01","tax_year":2024},
            {"rule_id":"r-2025","lifecycle_status":"effective","effective_from":"2025-01-01","effective_to":"2026-01-01","tax_year":2025},
            {"rule_id":"r-2026","lifecycle_status":"effective","effective_from":"2026-01-01","effective_to":"2027-01-01","tax_year":2026},
            {"rule_id":"r-future","lifecycle_status":"enacted_not_effective","effective_from":"2027-01-01","effective_to":None,"tax_year":2027},
        ]
    def test_historical_selects_historical_effective_snapshot(self):
        self.assertEqual(select_rule_version(self.rules,"2024-12-31")["rule_id"],"r-old")
    def test_current_transaction_does_not_select_future(self):
        self.assertEqual(select_rule_version(self.rules,"2026-10-08")["rule_id"],"r-2026")
    def test_exclusive_boundary_selects_next_version(self):
        self.assertEqual(select_rule_version(self.rules,"2026-01-01")["rule_id"],"r-2026")
    def test_missing_historical_version_returns_none_instead_of_using_today(self):
        self.assertIsNone(select_rule_version(self.rules[1:],"2024-12-31"))
    def test_tax_year_filter(self):
        self.assertIsNone(select_rule_version(self.rules,"2026-06-01",tax_year=2025))
    def test_overlap_escalates(self):
        overlap=dict(self.rules[2],rule_id="overlap",effective_from="2026-06-01")
        with self.assertRaises(RuleSelectionError): select_rule_version([self.rules[2],overlap],"2026-07-01")
    def test_invalid_date_rejected(self):
        with self.assertRaises(RuleSelectionError): select_rule_version(self.rules,"2026-02-30")

if __name__=="__main__": unittest.main()
