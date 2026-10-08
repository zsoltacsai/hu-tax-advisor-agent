# Hungarian supplier territorial VAT charging

## Question

Candidate `candidate-hu-supplier-vat-territorial-charging-phase5.6` / rule version `hu-supplier-vat-territorial-charging@1`. Research `research-4f02d5661e1790d85b50`; candidate hash `bb80f2e4e9a51e85aee826783d871aefc467659d80aa86bfe6153bd26c7b151f`; research hash `60b8a04622effe249947ac8fb873e9f08817b18dbe847fab55201dd1ec23cc1b`.

**LEGAL RULE QUESTION:** Hungarian territorial charging consequence for a DE place of supply

**IMPLEMENTATION QUESTION:** Should the engine expose only this stage's result, with what status/value and dependencies, when the required facts are established?

## Proposed rule

HU VAT territorial charging only; no rate

Proposed conditions (not approved):
- place of supply determined outside HU
- supply within Áfa tv. charging scope reviewed
- supplier/taxpayer facts complete

## Required facts

**Facts for legal review scenario:** see `REFERENCE_SCENARIO.json`; they are assumptions, not customer evidence.

**FACTS REQUIRED AT RUNTIME:**
- HU supplier status and territorial establishment facts
- place-of-supply result and date
- AAM/registration/VAT-ID status separately
- service consideration, performance and any statutory exception facts

Please identify facts that are legally material but absent from the model.

## Known exclusions

- All special and mixed service categories excluded pending separately reviewed rules.
- Unknown or conflicting facts require human review.
- No implementation outside the stated stage.

## Primary legal sources

- `hu-vat-act-njt-consolidation-2025-12-20` — 2. §, 37. § (1). [2007. évi CXXVII. törvény az általános forgalmi adóról — NJT consolidated text shown 2025-12-20](https://njt.hu/jogszabaly/2007-127-00-00.100) (version `2025-12-20`). **Adviser verify:** one or more requested provisions are not pinned as verified in the frozen snapshot.

These are review references from the Phase 5.6 source registry; they are not a conclusion that a provision applies. A provision marked for adviser verification is not treated as verified evidence.

## Supporting guidance

- No supporting official guidance is relied upon as a substitute for primary legislation. The BMF/NAV records in the research snapshot are access references only where relevant.

Official guidance supports interpretation but does not replace primary law. Do not rely on provider articles for legal conclusions.

## Effective-date basis

Research snapshot date: `2026-10-08`; synthetic fixture date: `2026-10-08`; the dossier scenario is limited to year 2026 until an exact transaction date is supplied. Relevant consolidated source dates and effective-date verification are listed in `EFFECTIVE_DATE_REVIEW.md`. The German statute entries cite a 2026-06-29 act-level last-amendment date, not paragraph-level effective dates. Please state the date-specific legal versions and any transitional rules.

## Current interpretation

Existing research treats Hungarian territorial charging as a separate question under Áfa tv. It does not infer zero rate, exemption, or charging from a DE place of supply or reverse charge.

## Known uncertainty

- No independent qualified adviser review is present; coding-agent structural review is not tax-adviser review.
- The candidate's frozen evidence pins are:
- `eu-vat-directive-2025-04-operational` / `Article 192a` / `2025-04-14`
- `hu-vat-act-njt-consolidation-2025-12-20` / `37. § (1)` / `2025-12-20`
- `hu-nav-26a60-2026-filing-guidance` / `26A60 03-as lap` / `2026-09-02`
- Related open issues: VAT-004, VAT-005, VAT-011, VAT-012. `VAT-012` is a `NEW_REVIEW_ISSUE` for source/provision alignment. Candidate records have not been edited.

## Current blocker

- BLOCKED: no independent qualified legal/tax reviewer has verified the complete law, effective dates, scope, exceptions, and taxpayer-specific applicability. Structural checks are not legal approval.
- Provision-level effective dates are not fully verified for the target transaction date.
- Candidate-specific exception analysis is incomplete.

## Questions for adviser

- How do Áfa tv. §2 and §37(1) apply when the modeled place of supply is Germany?
- If place of supply is Germany, is the transaction outside Hungarian VAT territorial charging scope? Please distinguish this from zero-rated, exempt, and reverse-charged treatment.
- Does AAM status change the territorial-scope result or create separate obligations?
- Does Hungarian/EU VAT-number status change the territorial-scope result?
- Which Hungarian exceptions or taxpayer facts must be modeled?

Please answer the legal question independently; the proposed conditions are not suggested answers. Distinguish legal requirements from evidence standards and runtime checks.

## Possible adviser decision

Select one: `APPROVE_AS_PROPOSED`, `APPROVE_WITH_CHANGES`, `REJECT`, `INSUFFICIENT_INFORMATION`, `OUTSIDE_REVIEW_SCOPE`.

Return `required_changes`, `missing_exceptions`, `missing_facts`, `corrected_interpretation`, `effective_date_notes`, `source_notes`, `confidence` (`high|medium|low`) and comments in the structured response. Adviser approval is not repository human approval for execution.
