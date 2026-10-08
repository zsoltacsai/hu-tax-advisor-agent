class RuleEvaluationError(ValueError):
    """Malformed or incomplete rule input."""

class RuleValidationError(RuleEvaluationError):
    """A rule, schema, evidence, or source reference is invalid."""

class RuleConflictError(RuleEvaluationError):
    """Equally applicable rules produce incompatible outcomes."""
