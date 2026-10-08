# Executable rule model

Rule data is declarative JSON validated by schemas/executable-rule.schema.json. Conditions use a closed operator set; no Python expressions, eval, scripts, network code, or downloaded executable content are accepted. Each rule version has a logical rule ID, unique version ID, jurisdiction/topic, effective interval, priority, conditions, a constrained place-of-supply outcome, source references, requirements, exclusions and review triggers.

The loader rejects unknown operators, outcome keys, invalid intervals, duplicate version IDs, missing evidence, unknown source IDs and provisions not listed in the source registry. Rule selection first filters by transaction date, then conditions. Equal-priority overlapping applicable rules with incompatible outcomes cause RULE_CONFLICT. Priority never resolves contradictory equal-priority rules.

Engine rule outputs determine only place-of-supply candidates within the listed scope. They do not calculate rates, decide AAM exemption, invoice wording, or filing duties.