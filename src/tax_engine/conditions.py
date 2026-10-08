"""Closed condition-operator interpreter. Never evaluates arbitrary code."""
from datetime import date
from typing import Any
from .exceptions import RuleValidationError

ALLOWED={"equals","not_equals","in","not_in","exists","not_exists","greater_than","less_than","date_between","all","any"}

def get_path(data: dict, path: str) -> Any:
    current: Any=data
    for part in path.split("."):
        if not isinstance(current,dict) or part not in current: return None
        current=current[part]
    return current

def evaluate_condition(condition: dict, facts: dict) -> bool:
    op=condition.get("operator")
    if op not in ALLOWED: raise RuleValidationError(f"unsupported condition operator: {op}")
    if op=="all": return all(evaluate_condition(c,facts) for c in condition.get("conditions",[]))
    if op=="any": return any(evaluate_condition(c,facts) for c in condition.get("conditions",[]))
    actual=get_path(facts,condition.get("field",""))
    expected=condition.get("value")
    if op=="equals": return actual==expected
    if op=="not_equals": return actual!=expected
    if op=="in": return actual in expected if isinstance(expected,(list,tuple,set)) else False
    if op=="not_in": return actual not in expected if isinstance(expected,(list,tuple,set)) else False
    if op=="exists": return actual is not None
    if op=="not_exists": return actual is None
    if op=="greater_than": return isinstance(actual,(int,float)) and isinstance(expected,(int,float)) and actual>expected
    if op=="less_than": return isinstance(actual,(int,float)) and isinstance(expected,(int,float)) and actual<expected
    if op=="date_between":
        try: point=date.fromisoformat(actual); low=date.fromisoformat(expected[0]); high=date.fromisoformat(expected[1])
        except (TypeError,ValueError,IndexError): return False
        return low<=point<=high
    raise RuleValidationError(f"operator has no implementation: {op}")

def matches(rule: dict, facts: dict) -> bool:
    return all(evaluate_condition(c,facts) for c in rule.get("conditions",[]))
