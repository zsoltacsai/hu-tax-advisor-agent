# Rule specificity and safe fallback

Executable rules declare `rule_scope` (`GENERAL` or `SPECIFIC`) and an integer `rule_specificity`. The selector first chooses maximum specificity; declared priority breaks ties only at the same specificity. A specific rule therefore outranks a general rule when both are applicable.

The current Article 44/45 candidates match only a reviewed `GENERAL_SERVICE` classification and require a completed special-rule exclusion screen. Article 58 is specific and matches only explicitly reviewed `ELECTRONICALLY_SUPPLIED_SERVICE` facts; it is not approved. If a classified special/out-of-scope category has no approved applicable specific rule, the engine reports `UNSUPPORTED_SCENARIO` or requires review. It does not fall through to Article 44/45.

This is a deterministic selection mechanism, not a tax-law classifier. The facts and scope review are supplied by a human; no service label is inferred from product name or delivery channel.
