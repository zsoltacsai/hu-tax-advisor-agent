"""Deterministic, evidence-backed VAT rule evaluation (no LLM execution)."""
from .engine import TaxEngine
from .exceptions import RuleConflictError, RuleEvaluationError, RuleValidationError

__all__=["TaxEngine","RuleConflictError","RuleEvaluationError","RuleValidationError"]
