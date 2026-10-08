# Hungarian cross-border invoice implementation

## Question

Candidate `candidate-hu-invoice-cross-border-service-phase5.6` / rule version `hu-invoice-cross-border-service@1`. Research `research-4f02d5661e1790d85b50`; candidate hash `b0b35b006f7a7428f1d6efa55c69a63d21c88b38213f2fea2b878aad4df038dd`; research hash `60b8a04622effe249947ac8fb873e9f08817b18dbe847fab55201dd1ec23cc1b`.

**LEGAL RULE QUESTION:** Hungarian invoice implementation for cross-border service

**IMPLEMENTATION QUESTION:** Should the engine expose only this stage's result, with what status/value and dependencies, when the required facts are established?

## Proposed rule

Hungarian invoice implementation only

Proposed conditions (not approved):
- Article 219a routes invoicing to HU
- Hungarian issuer and invoice facts
- service date and tax point
- community VAT IDs and RC wording reviewed

## Required facts

**Facts for legal review scenario:** see `REFERENCE_SCENARIO.json`; they are assumptions, not customer evidence.

**FACTS REQUIRED AT RUNTIME:**
- invoice jurisdiction routes to HU
- supplier registration and invoice issuer
- community VAT IDs, customer identity/address
- service description, consideration, performance/tax point
- self-billing and applicable transaction date

Please identify facts that are legally material but absent from the model.

## Known exclusions

- All special and mixed service categories excluded pending separately reviewed rules.
- Unknown or conflicting facts require human review.
- No implementation outside the stated stage.

## Primary legal sources

- `hu-vat-act-njt-consolidation-2025-12-20` — 159. § (2) c), 169. § n). [2007. évi CXXVII. törvény az általános forgalmi adóról — NJT consolidated text shown 2025-12-20](https://njt.hu/jogszabaly/2007-127-00-00.100) (version `2025-12-20`).
- `eu-vat-directive-2025-04-operational` — Article 219a, Article 222, Article 226. [Council Directive 2006/112/EC consolidated text — 2025-04-14 version, operational provisions](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006L0112-20250414) (version `2025-04-14`).

These are review references from the Phase 5.6 source registry; they are not a conclusion that a provision applies. A provision marked for adviser verification is not treated as verified evidence.

## Supporting guidance

- No supporting official guidance is relied upon as a substitute for primary legislation. The BMF/NAV records in the research snapshot are access references only where relevant.

Official guidance supports interpretation but does not replace primary law. Do not rely on provider articles for legal conclusions.

## Effective-date basis

Research snapshot date: `2026-10-08`; synthetic fixture date: `2026-10-08`; the dossier scenario is limited to year 2026 until an exact transaction date is supplied. Relevant consolidated source dates and effective-date verification are listed in `EFFECTIVE_DATE_REVIEW.md`. The German statute entries cite a 2026-06-29 act-level last-amendment date, not paragraph-level effective dates. Please state the date-specific legal versions and any transitional rules.

## Current interpretation

Existing research has not resolved the HU invoice-law provisions for this branch. No provider behavior is treated as law.

## Known uncertainty

- No independent qualified adviser review is present; coding-agent structural review is not tax-adviser review.
- The candidate's frozen evidence pins are:
- `eu-vat-directive-2025-04-operational` / `Article 192a` / `2025-04-14`
- `hu-vat-act-njt-consolidation-2025-12-20` / `37. § (1)` / `2025-12-20`
- `hu-nav-26a60-2026-filing-guidance` / `26A60 03-as lap` / `2026-09-02`
- Related open issues: VAT-004, VAT-006, VAT-008, VAT-012. `VAT-012` is a `NEW_REVIEW_ISSUE` for source/provision alignment. Candidate records have not been edited.

## Current blocker

- BLOCKED: no independent qualified legal/tax reviewer has verified the complete law, effective dates, scope, exceptions, and taxpayer-specific applicability. Structural checks are not legal approval.
- Provision-level effective dates are not fully verified for the target transaction date.
- Candidate-specific exception analysis is incomplete.

## Questions for adviser

- Which Áfa tv. provisions implement the applicable invoice requirements in this case?
- Which Hungarian invoice fields are mandatory?
- How must Community VAT numbers be presented?
- What reverse-charge notation is legally required, and is exact Hungarian wording required?
- What invoice timing rule applies to the cross-border service?
- Which Hungarian-specific exceptions apply?
- Do accounting-provider flags have legal significance or only implementation significance?

Please answer the legal question independently; the proposed conditions are not suggested answers. Distinguish legal requirements from evidence standards and runtime checks.

## Possible adviser decision

Select one: `APPROVE_AS_PROPOSED`, `APPROVE_WITH_CHANGES`, `REJECT`, `INSUFFICIENT_INFORMATION`, `OUTSIDE_REVIEW_SCOPE`.

Return `required_changes`, `missing_exceptions`, `missing_facts`, `corrected_interpretation`, `effective_date_notes`, `source_notes`, `confidence` (`high|medium|low`) and comments in the structured response. Adviser approval is not repository human approval for execution.
