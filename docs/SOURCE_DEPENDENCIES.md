# Source dependencies and freshness

Each rule's evidence IDs provide the source-to-rule edge; immutable research IDs and candidate IDs complete the source → research → candidate → approved-rule chain. `ResearchPipeline.dependencies(source_id)` lists dependent records. A source check uses `UNCHANGED`, `POSSIBLY_CHANGED`, `CHANGED`, or `UNKNOWN`; changed checks create an audit event but never rewrite a rule.

Rule freshness is `CURRENT`, `REVIEW_DUE`, `SOURCE_CHANGED`, `SOURCE_STALE`, `SUPERSEDED`, or `UNKNOWN`. Current executable policy is conservative: a rule must have an `UNCHANGED` check for every evidence source within its freshness class window; missing checks, live-verification-only sources, changed sources, or stale checks prevent loading. `REVIEW_DUE` is represented operationally by `SOURCE_STALE` today. Static historical sources still require an explicit unchanged check. Freshness checks do not prove that a rule's legal interpretation is correct.
