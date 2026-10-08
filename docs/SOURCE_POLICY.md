# Source policy

## Authority ranking
1. Binding Hungarian legislation and EU legal acts (primary; verify incorporation, effect and applicable version).
2. Relevant court judgments and binding rulings (scope/finality must be checked).
3. NAV and European Commission guidance (official interpretation/support, not legislation).
4. Official operational systems and technical specifications (authoritative only about those systems).
5. Provider documentation (product behavior only; never equal to law or NAV guidance).
6. Secondary commentary (leads only; never sole basis of material conclusion).

Ranking is an evidence preference, not a claim that an EU directive has direct effect in every domestic dispute. Resolve applicability with qualified review.

## Verification record
Registry separates URL checked from content verified. It records publication date, effective interval, source snapshot/version date, retrieval date, freshness class and notes. A reachable link is not proof that text is current. A consolidated EU text may be a documentation aid; authentic acts in the Official Journal control.

Phase 4 records `url_reachable`, `content_accessed`, `content_verified`, `effective_date_verified`, and `applicability_verified` separately. Research snapshots derive the first four only from registry observations and always leave issue-specific applicability unverified. A model cannot upgrade these flags. Source version date is not legal effective date; publication date is not effective date.

For each material claim cite registry ID, exact provision, version, retrieval date and supported proposition. Prefer primary legislation. Check applicable version first; use NAV/Commission guidance to explain administration. Never rely solely on blogs, accounting commentary, search snippets or forums. Record credible disagreement; do not silently choose. Never fabricate provisions, rulings, decisions, NAV guidance or citations. If a source is unavailable or stale, say so and escalate.


## Freshness and reliance

Classify each reference as `STATIC_HISTORICAL`, `LOW_CHANGE`, `ANNUAL_REVIEW`, `HIGH_CHANGE`, or `LIVE_VERIFICATION_REQUIRED`. Historical legislation is version-pinned; tax-year thresholds require annual verification; NAV procedural guidance and forms require current versions; live registers such as VIES require a live query before a transaction-specific statement; provider API behavior requires version-specific provider documentation. Stale cached data must never be described as currently verified. A source marked URL reachable is not automatically content verified, and content verification is not transaction applicability.

See [SOURCE_FRESHNESS_POLICY.md](SOURCE_FRESHNESS_POLICY.md).
