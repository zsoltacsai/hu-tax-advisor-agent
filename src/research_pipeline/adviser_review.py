"""Fail-closed import of a qualified adviser's structured review.

An adviser decision is recorded separately from candidate and execution
approval. This module never edits a candidate or creates an executable rule.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .workflow import PipelineError, ResearchPipeline, digest, load, write_immutable


DECISION_STATUS = {
    "APPROVE_AS_PROPOSED": "ADVISER_APPROVED",
    "APPROVE_WITH_CHANGES": "ADVISER_CHANGES_REQUIRED",
    "REJECT": "ADVISER_REJECTED",
    "INSUFFICIENT_INFORMATION": "ADVISER_REVIEW_PENDING",
    "OUTSIDE_REVIEW_SCOPE": "ADVISER_REVIEW_PENDING",
}


def _candidate_records(root: Path) -> dict[str, tuple[Path, dict[str, Any]]]:
    found = {}
    directory = root / "rules" / "country-candidates" / "phase5.6" / "candidates"
    for path in sorted(directory.glob("*.json")):
        candidate = load(path)
        candidate_id = candidate.get("candidate_id")
        if candidate_id in found:
            raise PipelineError(f"duplicate Phase 5.6 candidate ID: {candidate_id}")
        found[candidate_id] = (path, candidate)
    return found


def import_adviser_response(response: dict[str, Any], root: Path | str | None = None) -> dict[str, Any]:
    pipeline = ResearchPipeline(root)
    pipeline.validate(response, "adviser-response.schema.json")
    repository = Path(root) if root else pipeline.root
    pair = _candidate_records(repository).get(response["candidate_id"])
    if pair is None:
        raise PipelineError(f"unknown Phase 5.6 candidate: {response['candidate_id']}")
    _, candidate = pair
    candidate_hash = digest({k: v for k, v in candidate.items() if k != "candidate_hash"})
    if candidate.get("candidate_hash") != candidate_hash or response["candidate_hash"] != candidate_hash:
        raise PipelineError("adviser response candidate hash does not match the immutable candidate")
    if response["research_id"] != candidate["research_id"]:
        raise PipelineError("adviser response research ID does not match the candidate")
    snapshot = pipeline.read_snapshot(candidate["research_id"])
    snapshot_hash = snapshot.get("snapshot_hash")
    if candidate.get("research_hash") != snapshot_hash or response["research_hash"] != snapshot_hash:
        raise PipelineError("adviser response research snapshot hash does not match the candidate's frozen snapshot")

    status = DECISION_STATUS[response["decision"]]
    target = repository / "rules" / "adviser_reviews" / f"{response['candidate_id']}--{response['review_id']}.json"
    if target.exists():
        prior = load(target)
        if prior.get("response") != response:
            raise PipelineError("adviser review ID already exists with different response contents")
        pipeline.validate(prior, "adviser-review-record.schema.json")
        if prior.get("response_hash") != digest(response):
            raise PipelineError("stored adviser response hash mismatch")
        return prior
    record = {
        "response": response,
        "response_hash": digest(response),
        "adviser_status": status,
        "imported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "execution_approval_created": False,
    }
    pipeline.validate(record, "adviser-review-record.schema.json")
    write_immutable(target, record)
    details = {
        "candidate_id": response["candidate_id"], "candidate_hash": candidate_hash,
        "research_id": snapshot["research_id"], "research_hash": snapshot_hash,
        "response_hash": record["response_hash"], "adviser_status": status,
        "execution_approval_created": False,
    }
    pipeline.audit("ADVISER_RESPONSE_IMPORTED", "adviser-response-importer", response["review_id"], details)
    event_type = {
        "ADVISER_APPROVED": "ADVISER_APPROVED",
        "ADVISER_CHANGES_REQUIRED": "ADVISER_CHANGES_REQUIRED",
        "ADVISER_REJECTED": "ADVISER_REJECTED",
    }.get(status)
    if event_type:
        pipeline.audit(event_type, "adviser-response-importer", response["candidate_id"], details)
    return record


def adviser_status_for_candidate(candidate_id: str, root: Path | str | None = None) -> str:
    """Derive lifecycle status from the append-only import events; no response means pending."""
    pipeline = ResearchPipeline(root)
    candidate_ids = _candidate_records(Path(root) if root else pipeline.root)
    if candidate_id not in candidate_ids:
        raise PipelineError(f"unknown Phase 5.6 candidate: {candidate_id}")
    status = "ADVISER_REVIEW_PENDING"
    for event in pipeline._audit_events():
        if event["event_type"] == "ADVISER_RESPONSE_IMPORTED" and event.get("details", {}).get("candidate_id") == candidate_id:
            status = event["details"]["adviser_status"]
    return status
