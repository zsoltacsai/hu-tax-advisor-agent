# Rule lifecycle

Lifecycle states are `PROPOSED`, `AI_REVIEWED`, `HUMAN_REVIEW_REQUIRED`, `NEEDS_CHANGES`, `APPROVED`, `REJECTED`, `SUPERSEDED`, and `RETIRED`. Candidate/review snapshots are immutable; append-only hash-linked audit events define state transitions. Approved rule JSON is immutable. Superseding appends a lifecycle event and narrows the prior version's runtime interval without rewriting its approval record. Retired rules are excluded from execution; superseded rules remain eligible for dates before their supersession boundary. The Phase 3 interval selector remains authoritative for transaction-date choice.

Only `rules/approved/*.json` wrappers can be loaded by the tax engine. Source freshness must be `CURRENT`; absent, stale, possibly changed, or changed source checks keep a rule out of the executable set. See [SOURCE_DEPENDENCIES.md](SOURCE_DEPENDENCIES.md).


The approval wrapper pins SHA-256 hashes for the candidate, reviewer record, research snapshot, and executable rule. It also pins each evidence provision/version. The loader rechecks all links and source checks before loading. An unsafe/stale/changed source leaves the approved record preserved but omits it from execution; no fallback to a general rule is performed. See [APPROVAL_INTEGRITY.md](APPROVAL_INTEGRITY.md).
