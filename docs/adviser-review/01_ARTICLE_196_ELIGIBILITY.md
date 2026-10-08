# EU Article 196 eligibility

## Question

Candidate `candidate-eu-article196-eligibility-phase5.6` / rule version `eu-article196-eligibility@1`. Research `research-4f02d5661e1790d85b50`; candidate hash `aa025ecaa1aff2a989f94bbc02710d96c13b40cdca68f55cdbdeee03ce17b4b9`; research hash `60b8a04622effe249947ac8fb873e9f08817b18dbe847fab55201dd1ec23cc1b`.

**LEGAL RULE QUESTION:** EU Article 196 eligibility screen

**IMPLEMENTATION QUESTION:** Should the engine expose only this stage's result, with what status/value and dependencies, when the required facts are established?

## Proposed rule

EU Article 196 eligibility only; no destination-state implementation

Proposed conditions (not approved):
- Article 44 place of supply in destination
- qualifying recipient status supported
- supplier not established in destination under Article 192a
- service within reviewed scope

## Required facts

**Facts for legal review scenario:** see `REFERENCE_SCENARIO.json`; they are assumptions, not customer evidence.

**FACTS REQUIRED AT RUNTIME:**
- Article 44 path/rule version and place-of-supply evidence
- recipient category and taxable-person capacity
- customer establishment and VAT-ID evidence
- supplier taxable-person status, Member State and relevant FE/intervention
- actual service classification, exceptions and transaction date

Please identify facts that are legally material but absent from the model.

## Known exclusions

- All special and mixed service categories excluded pending separately reviewed rules.
- Unknown or conflicting facts require human review.
- No implementation outside the stated stage.

## Primary legal sources

- `eu-vat-directive-2025-04-operational` — Article 43, Article 44, Article 192a, Article 196. [Council Directive 2006/112/EC consolidated text — 2025-04-14 version, operational provisions](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006L0112-20250414) (version `2025-04-14`). **Adviser verify:** one or more requested provisions are not pinned as verified in the frozen snapshot.

These are review references from the Phase 5.6 source registry; they are not a conclusion that a provision applies. A provision marked for adviser verification is not treated as verified evidence.

## Supporting guidance

- No supporting official guidance is relied upon as a substitute for primary legislation. The BMF/NAV records in the research snapshot are access references only where relevant.

Official guidance supports interpretation but does not replace primary law. Do not rely on provider articles for legal conclusions.

## Effective-date basis

Research snapshot date: `2026-10-08`; synthetic fixture date: `2026-10-08`; the dossier scenario is limited to year 2026 until an exact transaction date is supplied. Relevant consolidated source dates and effective-date verification are listed in `EFFECTIVE_DATE_REVIEW.md`. The German statute entries cite a 2026-06-29 act-level last-amendment date, not paragraph-level effective dates. Please state the date-specific legal versions and any transitional rules.

## Current interpretation

The existing research frames Article 196 as a separate EU eligibility stage dependent on Article 44 path, recipient qualification and supplier establishment conditions. It does not decide destination-state liability. The reviewer must confirm the exact legal test.

## Known uncertainty

- No independent qualified adviser review is present; coding-agent structural review is not tax-adviser review.
- The candidate's frozen evidence pins are:
- `eu-vat-directive-2025-04-operational` / `Article 192a` / `2025-04-14`
- `de-ustg-2026-14-14a` / `14 Absatz 4` / `2026-06-29`
- `hu-vat-act-njt-consolidation-2025-12-20` / `37. § (1)` / `2025-12-20`
- Related open issues: VAT-001, VAT-004, VAT-011, VAT-012. `VAT-012` is a `NEW_REVIEW_ISSUE` for source/provision alignment. Candidate records have not been edited.

## Current blocker

- BLOCKED: no independent qualified legal/tax reviewer has verified the complete law, effective dates, scope, exceptions, and taxpayer-specific applicability. Structural checks are not legal approval.
- Provision-level effective dates are not fully verified for the target transaction date.
- Candidate-specific exception analysis is incomplete.

## Questions for adviser

- What is the exact legal relationship between Article 44 and Article 196 for the modeled service?
- Which recipient categories and capacity/identification conditions satisfy Article 196?
- What supplier establishment and fixed-establishment conditions apply?
- When and how does Article 192a affect whether the supplier is regarded as established in the taxing state?
- Is VAT identification a legal condition for each recipient category, or evidence of status?
- Which material exceptions must be screened before this stage can return an eligibility result?
- Which EU legal text/effective version applies to transactions on each relevant date in 2026?
- Are additional legally material facts needed?

Please answer the legal question independently; the proposed conditions are not suggested answers. Distinguish legal requirements from evidence standards and runtime checks.

## Possible adviser decision

Select one: `APPROVE_AS_PROPOSED`, `APPROVE_WITH_CHANGES`, `REJECT`, `INSUFFICIENT_INFORMATION`, `OUTSIDE_REVIEW_SCOPE`.

Return `required_changes`, `missing_exceptions`, `missing_facts`, `corrected_interpretation`, `effective_date_notes`, `source_notes`, `confidence` (`high|medium|low`) and comments in the structured response. Adviser approval is not repository human approval for execution.
