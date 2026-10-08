# EU Article 262 recapitulative statement

## Question

Candidate `candidate-eu-recap-article262-service-phase5.6` / rule version `eu-recap-article262-service@1`. Research `research-4f02d5661e1790d85b50`; candidate hash `7070f52d0646a31ccd839181c64fdce62fe6737b92495a2b792a9e4385c835cb`; research hash `60b8a04622effe249947ac8fb873e9f08817b18dbe847fab55201dd1ec23cc1b`.

**LEGAL RULE QUESTION:** EU recapitulative statement obligation under Article 262(1)(c)

**IMPLEMENTATION QUESTION:** Should the engine expose only this stage's result, with what status/value and dependencies, when the required facts are established?

## Proposed rule

EU recap obligation only

Proposed conditions (not approved):
- qualifying recipient and VAT identification
- recipient liable under Article 196
- not exempt in destination
- supplier reporting facts and period

## Required facts

**Facts for legal review scenario:** see `REFERENCE_SCENARIO.json`; they are assumptions, not customer evidence.

**FACTS REQUIRED AT RUNTIME:**
- supplier VAT identification/reporting status
- recipient taxable-person or qualifying legal-person status and identification
- Article 196 recipient liability
- destination exemption/service classification
- chargeable event, period, corrections

Please identify facts that are legally material but absent from the model.

## Known exclusions

- All special and mixed service categories excluded pending separately reviewed rules.
- Unknown or conflicting facts require human review.
- No implementation outside the stated stage.

## Primary legal sources

- `eu-vat-directive-2025-04-operational` — Article 196, Article 262(1)(c), Article 263, Article 264. [Council Directive 2006/112/EC consolidated text — 2025-04-14 version, operational provisions](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006L0112-20250414) (version `2025-04-14`). **Adviser verify:** one or more requested provisions are not pinned as verified in the frozen snapshot.

These are review references from the Phase 5.6 source registry; they are not a conclusion that a provision applies. A provision marked for adviser verification is not treated as verified evidence.

## Supporting guidance

- No supporting official guidance is relied upon as a substitute for primary legislation. The BMF/NAV records in the research snapshot are access references only where relevant.

Official guidance supports interpretation but does not replace primary law. Do not rely on provider articles for legal conclusions.

## Effective-date basis

Research snapshot date: `2026-10-08`; synthetic fixture date: `2026-10-08`; the dossier scenario is limited to year 2026 until an exact transaction date is supplied. Relevant consolidated source dates and effective-date verification are listed in `EFFECTIVE_DATE_REVIEW.md`. The German statute entries cite a 2026-06-29 act-level last-amendment date, not paragraph-level effective dates. Please state the date-specific legal versions and any transitional rules.

## Current interpretation

Existing research flags Article 262(1)(c)'s conjunction of conditions; Article 44 alone is insufficient. No recap obligation is determined.

## Known uncertainty

- No independent qualified adviser review is present; coding-agent structural review is not tax-adviser review.
- The candidate's frozen evidence pins are:
- `eu-vat-directive-2025-04-operational` / `Article 192a` / `2025-04-14`
- `de-ustg-2026-14-14a` / `14 Absatz 4` / `2026-06-29`
- `hu-vat-act-njt-consolidation-2025-12-20` / `37. § (1)` / `2025-12-20`
- Related open issues: VAT-004, VAT-009, VAT-011, VAT-012, VAT-013. `VAT-012` is a `NEW_REVIEW_ISSUE` for source/provision alignment. Candidate records have not been edited.

## Current blocker

- BLOCKED: no independent qualified legal/tax reviewer has verified the complete law, effective dates, scope, exceptions, and taxpayer-specific applicability. Structural checks are not legal approval.
- Provision-level effective dates are not fully verified for the target transaction date.
- Candidate-specific exception analysis is incomplete.

## Questions for adviser

- Please confirm the required conjunction of supplier identification, recipient identification, recipient liability under Article 196, destination non-exemption and service scope.
- Does the recipient VAT ID need to be validated or otherwise evidenced in a particular way?
- How is destination non-exemption established for this service subtype?
- Which reporting period and chargeable-event date control, and can obligation be decided while period remains unresolved?
- What exceptions, corrections or additional conditions must be represented?

Please answer the legal question independently; the proposed conditions are not suggested answers. Distinguish legal requirements from evidence standards and runtime checks.

## Possible adviser decision

Select one: `APPROVE_AS_PROPOSED`, `APPROVE_WITH_CHANGES`, `REJECT`, `INSUFFICIENT_INFORMATION`, `OUTSIDE_REVIEW_SCOPE`.

Return `required_changes`, `missing_exceptions`, `missing_facts`, `corrected_interpretation`, `effective_date_notes`, `source_notes`, `confidence` (`high|medium|low`) and comments in the structured response. Adviser approval is not repository human approval for execution.
