# EU invoice metadata

## Question

Candidate `candidate-eu-invoice-metadata-general-b2b-rc-phase5.6` / rule version `eu-invoice-metadata-general-b2b-rc@1`. Research `research-4f02d5661e1790d85b50`; candidate hash `23d673b128588adef6f9241ecd1cb5dc486ccabc02fee949d0c8571a69324214`; research hash `60b8a04622effe249947ac8fb873e9f08817b18dbe847fab55201dd1ec23cc1b`.

**LEGAL RULE QUESTION:** Invoice metadata requirements under Directive Articles 222, 226 and 226a

**IMPLEMENTATION QUESTION:** Should the engine expose only this stage's result, with what status/value and dependencies, when the required facts are established?

## Proposed rule

Metadata requirement model only; no rendered invoice

Proposed conditions (not approved):
- invoice jurisdiction determined
- both VAT IDs and parties evidenced
- service and taxable amount facts
- invoice deadline inputs resolved

## Required facts

**Facts for legal review scenario:** see `REFERENCE_SCENARIO.json`; they are assumptions, not customer evidence.

**FACTS REQUIRED AT RUNTIME:**
- invoice jurisdiction first
- supplier/customer names, addresses, and VAT IDs
- service description, extent, amount and relevant dates
- liability result, tax basis/amount fields and self-billing
- invoice event/date

Please identify facts that are legally material but absent from the model.

## Known exclusions

- All special and mixed service categories excluded pending separately reviewed rules.
- Unknown or conflicting facts require human review.
- No implementation outside the stated stage.

## Primary legal sources

- `eu-vat-directive-2025-04-operational` — Article 222, Article 226, Article 226a. [Council Directive 2006/112/EC consolidated text — 2025-04-14 version, operational provisions](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006L0112-20250414) (version `2025-04-14`).
- `de-ustg-2026-14-14a` — 14 Absatz 4, 14a Absatz 1. [German Umsatzsteuergesetz (UStG), §§ 14 and 14a invoices](https://www.gesetze-im-internet.de/ustg_1980/__14a.html) (version `2026-06-29`).

These are review references from the Phase 5.6 source registry; they are not a conclusion that a provision applies. A provision marked for adviser verification is not treated as verified evidence.

## Supporting guidance

- No supporting official guidance is relied upon as a substitute for primary legislation. The BMF/NAV records in the research snapshot are access references only where relevant.

Official guidance supports interpretation but does not replace primary law. Do not rely on provider articles for legal conclusions.

## Effective-date basis

Research snapshot date: `2026-10-08`; synthetic fixture date: `2026-10-08`; the dossier scenario is limited to year 2026 until an exact transaction date is supplied. Relevant consolidated source dates and effective-date verification are listed in `EFFECTIVE_DATE_REVIEW.md`. The German statute entries cite a 2026-06-29 act-level last-amendment date, not paragraph-level effective dates. Please state the date-specific legal versions and any transitional rules.

## Current interpretation

Existing research identifies Articles 222, 226 and 226a for review. No invoice fields or final wording have been approved.

## Known uncertainty

- No independent qualified adviser review is present; coding-agent structural review is not tax-adviser review.
- The candidate's frozen evidence pins are:
- `eu-vat-directive-2025-04-operational` / `Article 192a` / `2025-04-14`
- `de-ustg-2026-14-14a` / `14 Absatz 4` / `2026-06-29`
- `hu-vat-act-njt-consolidation-2025-12-20` / `37. § (1)` / `2025-12-20`
- Related open issues: VAT-004, VAT-006, VAT-007, VAT-012. `VAT-012` is a `NEW_REVIEW_ISSUE` for source/provision alignment. Candidate records have not been edited.

## Current blocker

- BLOCKED: no independent qualified legal/tax reviewer has verified the complete law, effective dates, scope, exceptions, and taxpayer-specific applicability. Structural checks are not legal approval.
- Provision-level effective dates are not fully verified for the target transaction date.
- Candidate-specific exception analysis is incomplete.

## Questions for adviser

- Confirm when supplier and customer VAT IDs are required and which identifiers belong on this invoice.
- What service description and taxable-amount particulars are required?
- What tax amount/rate particulars apply, including Article 226a omissions if available?
- What invoice deadline applies and which event/date controls it?
- Is the exact text "Reverse charge" mandatory, or is a semantic indication required? Please separate legal indication from language/translation and provider display questions.
- Which version of Articles 222, 226 and 226a governs the transaction?

Please answer the legal question independently; the proposed conditions are not suggested answers. Distinguish legal requirements from evidence standards and runtime checks.

## Possible adviser decision

Select one: `APPROVE_AS_PROPOSED`, `APPROVE_WITH_CHANGES`, `REJECT`, `INSUFFICIENT_INFORMATION`, `OUTSIDE_REVIEW_SCOPE`.

Return `required_changes`, `missing_exceptions`, `missing_facts`, `corrected_interpretation`, `effective_date_notes`, `source_notes`, `confidence` (`high|medium|low`) and comments in the structured response. Adviser approval is not repository human approval for execution.
