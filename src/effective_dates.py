"""Pure date-based selection of versioned rule metadata; contains no tax logic."""
from datetime import date
from typing import Any

class RuleSelectionError(ValueError):
    pass

def select_rule_version(records: list[dict[str, Any]], transaction_date: str, *, tax_year: int | None = None) -> dict[str, Any] | None:
    """Select the unique effective interval containing transaction_date.

    effective_to is exclusive. Effective, superseded, and historical records
    may apply to an earlier transaction date. Proposed and not-yet-effective
    records are never selected.
    Transition references require human review outside this utility.
    Returns None when no version applies and raises on ambiguous overlapping versions.
    """
    try:
        point = date.fromisoformat(transaction_date)
    except (TypeError, ValueError) as exc:
        raise RuleSelectionError("transaction_date must be an ISO calendar date") from exc
    candidates = []
    for record in records:
        if record.get("lifecycle_status") not in {"effective", "superseded", "historical"} or record.get("future_announced", False):
            continue
        start = record.get("effective_from")
        end = record.get("effective_to")
        if not start or date.fromisoformat(start) > point:
            continue
        if end and point >= date.fromisoformat(end):
            continue
        year = record.get("tax_year")
        if tax_year is not None and year is not None and year != tax_year:
            continue
        candidates.append(record)
    if len(candidates) > 1:
        raise RuleSelectionError("overlapping effective rule versions; human review required")
    return candidates[0] if candidates else None
