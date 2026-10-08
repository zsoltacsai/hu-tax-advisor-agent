# German reverse charge

## Question

Candidate `candidate-de-vat-b2b-cross-border-services-reverse-charge-phase5.6` / rule version `de-vat-b2b-cross-border-services-reverse-charge@1`. Research `research-4f02d5661e1790d85b50`; candidate hash `43d05f3556b0ebd6ae85a89c722d1167c5a81a6af3b1425bcbfa0818bd0cf66a`; research hash `60b8a04622effe249947ac8fb873e9f08817b18dbe847fab55201dd1ec23cc1b`.

**LEGAL RULE QUESTION:** German §13b implementation for qualifying cross-border general services

**IMPLEMENTATION QUESTION:** Should the engine expose only this stage's result, with what status/value and dependencies, when the required facts are established?

## Proposed rule

German destination reverse-charge liability only

Proposed conditions (not approved):
- Article 44 path in DE
- taxable person established
- supplier elsewhere in EU
- no participating relevant DE establishment
- DE taxable supply and exception screen complete

## Required facts

**Facts for legal review scenario:** see `REFERENCE_SCENARIO.json`; they are assumptions, not customer evidence.

**FACTS REQUIRED AT RUNTIME:**
- DE place-of-supply and Article 44 path
- supplier EU establishment and any German FE resources/participation
- recipient taxable-person status and establishment
- service detail and §13b exclusion facts
- German exemption category and evidence
- exact transaction date

Please identify facts that are legally material but absent from the model.

## Known exclusions

- All special and mixed service categories excluded pending separately reviewed rules.
- Unknown or conflicting facts require human review.
- No implementation outside the stated stage.

## Primary legal sources

- `de-ustg-2026-3a` — 3a Absatz 2. [German Umsatzsteuergesetz (UStG), § 3a place of supply](https://www.gesetze-im-internet.de/ustg_1980/__3a.html) (version `2026-06-29`).
- `de-ustg-2026-13b` — 13b Absatz 1, 13b Absatz 5, 13b Absatz 6, 13b Absatz 7. [German Umsatzsteuergesetz (UStG), § 13b recipient liability](https://www.gesetze-im-internet.de/ustg_1980/__13b.html) (version `2026-06-29`).
- `de-ustg-2026-4` — 4 Nummer 8 bis 29. [German Umsatzsteuergesetz (UStG), § 4 exemptions](https://www.gesetze-im-internet.de/ustg_1980/__4.html) (version `2026-06-29`).
- `eu-vat-directive-2025-04-operational` — Article 192a, Article 196. [Council Directive 2006/112/EC consolidated text — 2025-04-14 version, operational provisions](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006L0112-20250414) (version `2025-04-14`).

These are review references from the Phase 5.6 source registry; they are not a conclusion that a provision applies. A provision marked for adviser verification is not treated as verified evidence.

## Supporting guidance

- `de-bmf-ustae-current` — Abschnitt 3a.1, Abschnitt 13b.11. [Umsatzsteuer-Anwendungserlass (current consolidated administrative guidance)](https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Umsatzsteuer/Umsatzsteuer-Anwendungserlass/Umsatzsteuer-Anwendungserlass-aktuell.pdf?__blob=publicationFile&v=44) (version `not pinned`).

Official guidance supports interpretation but does not replace primary law. Do not rely on provider articles for legal conclusions.

## Effective-date basis

Research snapshot date: `2026-10-08`; synthetic fixture date: `2026-10-08`; the dossier scenario is limited to year 2026 until an exact transaction date is supplied. Relevant consolidated source dates and effective-date verification are listed in `EFFECTIVE_DATE_REVIEW.md`. The German statute entries cite a 2026-06-29 act-level last-amendment date, not paragraph-level effective dates. Please state the date-specific legal versions and any transitional rules.

## Current interpretation

Existing research identifies UStG §3a(2) and §13b(1), (5)-(7) as the German statutory path to examine. No German recipient-liability conclusion has been adopted.

## Known uncertainty

- No independent qualified adviser review is present; coding-agent structural review is not tax-adviser review.
- The candidate's frozen evidence pins are:
- `eu-vat-directive-2025-04-operational` / `Article 192a` / `2025-04-14`
- `de-ustg-2026-13b` / `13b Absatz 1` / `2026-06-29`
- `de-ustg-2026-3a` / `3a Absatz 2` / `2026-06-29`
- `de-ustg-2026-4` / `4 Nummer 8 bis 29` / `2026-06-29`
- Related open issues: VAT-002, VAT-003, VAT-004, VAT-011, VAT-012, VAT-013. `VAT-012` is a `NEW_REVIEW_ISSUE` for source/provision alignment. Candidate records have not been edited.

## Current blocker

- BLOCKED: no independent qualified legal/tax reviewer has verified the complete law, effective dates, scope, exceptions, and taxpayer-specific applicability. Structural checks are not legal approval.
- Provision-level effective dates are not fully verified for the target transaction date.
- Candidate-specific exception analysis is incomplete.

## Questions for adviser

- Does UStG §13b(1), together with which applicable subsections, implement recipient liability for the narrow modeled service?
- What exact supplier-establishment conditions apply?
- What fixed-establishment participation test is relevant?
- Which §13b exclusions must be modeled?
- Does the actual service description require additional German classification?
- Which German exemptions could prevent the proposed treatment, and what facts identify them?
- Which transaction-date UStG and guidance versions apply during 2026?

Please answer the legal question independently; the proposed conditions are not suggested answers. Distinguish legal requirements from evidence standards and runtime checks.

## Possible adviser decision

Select one: `APPROVE_AS_PROPOSED`, `APPROVE_WITH_CHANGES`, `REJECT`, `INSUFFICIENT_INFORMATION`, `OUTSIDE_REVIEW_SCOPE`.

Return `required_changes`, `missing_exceptions`, `missing_facts`, `corrected_interpretation`, `effective_date_notes`, `source_notes`, `confidence` (`high|medium|low`) and comments in the structured response. Adviser approval is not repository human approval for execution.
