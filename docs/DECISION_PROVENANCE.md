# Decision provenance model

A future decision is reproducible only from the full chain:

INPUT FACTS + RULE VERSIONS + SOURCE EVIDENCE + INTERPRETATION + ASSUMPTIONS = CONCLUSION

The decision schema stores decision/as-of/transaction dates, facts, assumptions, rule IDs and source versions/effective intervals, evidence references, interpretation, conclusion status, uncertainty categories, confidence, human-review flag and unresolved questions. Evidence points to registry IDs and exact provisions; it also stores source URL, retrieval date, version date and what it supports.

Do not store hidden model reasoning. Store a concise rationale sufficient for audit, not private chain-of-thought. A decision with unavailable legal version or necessary live evidence is cannot_determine. Any later correction creates a new decision record linked to the superseded ID; never rewrite history.