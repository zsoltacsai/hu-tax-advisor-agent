# Source freshness policy

Freshness labels tell the researcher when cached material must be rechecked. They never upgrade a secondary source into authority and never prove currency by themselves.

| Class | Use | Required behavior | Examples |
|---|---|---|---|
| STATIC_HISTORICAL | Closed historical versions | Preserve immutable version and effective dates; retrieve applicable historical text for the transaction | Repealed act snapshot, prior guidance archived for history |
| LOW_CHANGE | Stable text but amendments remain possible | Confirm no relevant amendment when establishing a version baseline; verify again if the issue/date is sensitive | Specific EU act version, subject to later amendment |
| ANNUAL_REVIEW | Values or eligibility renewed by tax year | Verify the exact requested tax year and threshold base every time | Hungarian AAM threshold |
| HIGH_CHANGE | Guidance, procedures, APIs or laws with material update risk | Re-fetch official source before relying on cached guidance or technical behavior | NAV procedural guidance, VAT Directive consolidated text, NAV Online Számla docs |
| LIVE_VERIFICATION_REQUIRED | Individual status or live system state | Perform authorized live check at relevant time; record response and timestamp. If unavailable, do not infer negative status | VIES VAT-ID state |

Provider documentation is version-dependent and must be checked before describing current behavior. The authority ranking is independent of freshness. Always report retrieved_at and version_date separately. A cached item outside the allowed freshness window is SOURCE_NOT_VERIFIED; status-specific questions can require LIVE_VERIFICATION_REQUIRED.

No VIES lookup or provider API connection is performed. Phase 3 makes no live verification claims.

Phase 5 notes: the NJT Hungary VAT Act page was fetched directly on 2026-10-08 (HTTP 200; page version header 2025-12-20) and NAV A60 form/page and 2026 instructions were accessed the same date. These records do not certify transaction applicability or future freshness. Recheck NAV form/guidance before current reporting reliance. EU consolidated texts are date-pinned and later amendments must be checked.
