import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.research_pipeline.adviser_review import adviser_status_for_candidate, import_adviser_response
from src.research_pipeline.workflow import PipelineError, ResearchPipeline, digest
from src.tax_engine.rule_loader import RuleLoader

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_ID = "candidate-eu-article196-eligibility-phase5.6"


class AdviserReviewWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for rel in ("schemas", "sources", "research/snapshots", "rules/approved", "rules/proposed", "rules/reviews", "rules/country-candidates/phase5.6/candidates", "state/source_checks"):
            shutil.copytree(ROOT / rel, self.root / rel)
        (self.root / "state").mkdir(exist_ok=True)
        shutil.copy2(ROOT / "state/audit.jsonl", self.root / "state/audit.jsonl")
        self.candidate = json.loads(next((self.root / "rules/country-candidates/phase5.6/candidates").glob(f"{CANDIDATE_ID}.json")).read_text(encoding="utf-8"))
        self.snapshot = json.loads((self.root / "research/snapshots" / f"{self.candidate['research_id']}.json").read_text(encoding="utf-8"))
        self.response = {
            "review_id": "synthetic-test-review-001", "reviewer_role": "qualified_vat_adviser", "review_date": "2026-10-08",
            "candidate_id": CANDIDATE_ID, "candidate_hash": self.candidate["candidate_hash"],
            "research_id": self.candidate["research_id"], "research_hash": self.snapshot["snapshot_hash"],
            "decision": "APPROVE_AS_PROPOSED", "required_changes": [], "missing_exceptions": [], "missing_facts": [],
            "corrected_interpretation": "Synthetic test only.", "effective_date_notes": [], "source_notes": [], "confidence": "medium", "comments": "Synthetic test response; not real adviser feedback.",
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_response_schema_accepts_valid_and_rejects_invalid_decision(self):
        pipe = ResearchPipeline(self.root)
        pipe.validate(self.response, "adviser-response.schema.json")
        bad = dict(self.response, decision="HUMAN_APPROVED")
        with self.assertRaises(PipelineError):
            pipe.validate(bad, "adviser-response.schema.json")

    def test_unknown_candidate_rejected(self):
        bad = dict(self.response, candidate_id="candidate-not-in-repository")
        with self.assertRaises(PipelineError):
            import_adviser_response(bad, self.root)

    def test_candidate_hash_linkage_required(self):
        bad = dict(self.response, candidate_hash="0" * 64)
        with self.assertRaises(PipelineError):
            import_adviser_response(bad, self.root)

    def test_research_snapshot_linkage_required(self):
        bad = dict(self.response, research_hash="f" * 64)
        with self.assertRaises(PipelineError):
            import_adviser_response(bad, self.root)

    def test_import_records_adviser_approval_but_never_execution_approval(self):
        before_files = sorted(p.name for p in (self.root / "rules/approved").glob("*.json"))
        before_rules = RuleLoader(self.root).load_rules()
        self.assertEqual(adviser_status_for_candidate(CANDIDATE_ID, self.root), "ADVISER_REVIEW_PENDING")
        result = import_adviser_response(self.response, self.root)
        self.assertEqual(result["adviser_status"], "ADVISER_APPROVED")
        self.assertFalse(result["execution_approval_created"])
        self.assertEqual(adviser_status_for_candidate(CANDIDATE_ID, self.root), "ADVISER_APPROVED")
        after_files = sorted(p.name for p in (self.root / "rules/approved").glob("*.json"))
        after_rules = RuleLoader(self.root).load_rules()
        self.assertEqual(before_files, after_files)
        self.assertEqual([x["rule_version_id"] for x in before_rules], [x["rule_version_id"] for x in after_rules])
        stored_candidate = json.loads(next((self.root / "rules/country-candidates/phase5.6/candidates").glob(f"{CANDIDATE_ID}.json")).read_text(encoding="utf-8"))
        self.assertEqual(stored_candidate, self.candidate)
        events = ResearchPipeline(self.root)._audit_events()
        types = [e["event_type"] for e in events[-2:]]
        self.assertEqual(types, ["ADVISER_RESPONSE_IMPORTED", "ADVISER_APPROVED"])
        self.assertNotIn("HUMAN_APPROVAL", types)

    def test_import_replay_is_idempotent_and_conflicting_review_id_rejected(self):
        first = import_adviser_response(self.response, self.root)
        second = import_adviser_response(self.response, self.root)
        self.assertEqual(first, second)
        count = len(ResearchPipeline(self.root)._audit_events())
        self.assertEqual(count, len(ResearchPipeline(self.root)._audit_events()))
        conflict = dict(self.response, comments="different content")
        with self.assertRaises(PipelineError):
            import_adviser_response(conflict, self.root)

    def test_audit_event_integrity_detects_tampering(self):
        import_adviser_response(self.response, self.root)
        path = self.root / "state/audit.jsonl"
        rows = path.read_text(encoding="utf-8").splitlines()
        last = json.loads(rows[-1])
        last["event_hash"] = "0" * 64
        rows[-1] = json.dumps(last)
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        with self.assertRaises(PipelineError):
            ResearchPipeline(self.root)._audit_events()


if __name__ == "__main__":
    unittest.main()
