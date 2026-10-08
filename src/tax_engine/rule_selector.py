"""Select effective rule versions and detect incompatible applicable outcomes."""
from datetime import date
from .exceptions import RuleConflictError, RuleEvaluationError

def select_effective_rules(rules: list[dict], transaction_date: str, jurisdiction: str="EU") -> list[dict]:
    try: point=date.fromisoformat(transaction_date)
    except (TypeError,ValueError) as exc: raise RuleEvaluationError("invalid transaction/effective date") from exc
    selected=[]
    for rule in rules:
        if not rule.get("enabled",False): continue
        if rule.get("jurisdiction") not in {jurisdiction,"MULTI"}: continue
        try:
            start=date.fromisoformat(rule["effective_from"])
            end=date.fromisoformat(rule["effective_to"]) if rule.get("effective_to") else None
        except (KeyError,TypeError,ValueError) as exc: raise RuleEvaluationError(f"invalid effective interval in {rule.get('rule_id')}") from exc
        if start<=point and (end is None or point<end): selected.append(rule)
    return selected

def resolve_applicable(applicable: list[dict]) -> list[dict]:
    if not applicable: return []
    # Specific rules always outrank general rules; priority only breaks ties
    # within the same declared scope/specificity and never bridges scopes.
    highest_specificity=max(r["rule_specificity"] for r in applicable)
    scoped=[r for r in applicable if r["rule_specificity"]==highest_specificity]
    highest=max(r["priority"] for r in scoped)
    winners=[r for r in scoped if r["priority"]==highest]
    signatures={repr(sorted(r["outcome"].items())) for r in winners}
    if len(signatures)>1:
        ids=sorted(r["rule_version_id"] for r in winners)
        raise RuleConflictError("RULE_CONFLICT: equal-priority rules have incompatible outcomes: "+", ".join(ids))
    return sorted(winners,key=lambda r:(r["rule_id"],r["rule_version_id"]))
