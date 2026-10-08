# VAT adviser review package — Phase 5.7

**Purpose:** professional review of eight blocked, non-executable candidates. **No adviser response is required to finish this handoff.** This is a decision-support research package, not professional advice.

## Reference scenario

See [`REFERENCE_SCENARIO.json`](REFERENCE_SCENARIO.json). In plain terms: a synthetic HU taxable-person supplier provides a hypothesized general B2B service to a synthetic DE business customer in 2026. Supplier and customer status, IDs, establishments, service classification, date and other transactional inputs are explicitly divided between assumptions for legal review and facts that must be verified at runtime. The scenario does not presume a VAT treatment. German non-exemption is not a fact; it is a conditional question.

## Rule architecture

The model separates: existing Article 44 place-of-supply stage → EU Article 196 eligibility → German implementation → Hungarian supplier territorial charging → invoice jurisdiction → invoice metadata/HU invoice implementation → EU recap → Hungarian A60. These stages are not interchangeable. Article 44 does not itself establish reverse charge; EU eligibility is not German implementation; reverse charge does not itself decide supplier charging, invoicing, or reporting. AAM and tax point remain separate.

The repository currently loads exactly `eu-vat-services-b2b-general@1` and `eu-vat-services-b2c-general@1`. Article 58 is still `NEEDS_CHANGES`. All eight Phase 5.6 candidates remain `BLOCKED`; none is executable or approval-ready.

## What has been accessed and what remains open

The frozen Phase 5.6 snapshot `research-4f02d5661e1790d85b50` records 11 official-source entries and provisions, retrieved 2026-10-08. Official source text was accessed for the cited German UStG provisions, EU VAT Directive consolidation dated 2025-04-14, the NJT Áfa tv. consolidation displayed as 2025-12-20, NAV's 2026 26A60 instructions, and the BMF UStAE entry point. A source being reachable or its text being accessed does not establish that a specific provision is effective on a transaction date or applies to these facts. Germany paragraph-specific effective dates, the exact dated BMF guidance version, HU filing statutory basis, and several candidate source pins remain unresolved. See [Effective-date review](EFFECTIVE_DATE_REVIEW.md), [Source index](SOURCE_INDEX.md), and [Open issues](OPEN_ISSUES.md).

A consistency review found candidate-to-provision evidence mapping concerns. These records are immutable and have not been altered. They are flagged as `VAT-012 NEW_REVIEW_ISSUE`; see each affected sheet and the issue register.

## Decisions requested

For each candidate, use its review sheet and select exactly one: `APPROVE_AS_PROPOSED`, `APPROVE_WITH_CHANGES`, `REJECT`, `INSUFFICIENT_INFORMATION`, or `OUTSIDE_REVIEW_SCOPE`. Please also supply required changes, missing exceptions/facts, corrected interpretation, effective-date notes, source notes and confidence. “Approve” in this package means **adviser review only**, never execution approval.

| Order | Candidate | Review sheet | Current status |
|---:|---|---|---|
| 1 | `candidate-eu-article196-eligibility-phase5.6` / `eu-article196-eligibility@1` — EU Article 196 eligibility | [01_ARTICLE_196_ELIGIBILITY.md](01_ARTICLE_196_ELIGIBILITY.md) | `BLOCKED` |
| 2 | `candidate-de-vat-b2b-cross-border-services-reverse-charge-phase5.6` / `de-vat-b2b-cross-border-services-reverse-charge@1` — German reverse charge | [02_DE_REVERSE_CHARGE.md](02_DE_REVERSE_CHARGE.md) | `BLOCKED` |
| 3 | `candidate-hu-supplier-vat-territorial-charging-phase5.6` / `hu-supplier-vat-territorial-charging@1` — Hungarian supplier territorial VAT charging | [03_HU_SUPPLIER_VAT_CHARGING.md](03_HU_SUPPLIER_VAT_CHARGING.md) | `BLOCKED` |
| 4 | `candidate-eu-invoice-jurisdiction-219a-phase5.6` / `eu-invoice-jurisdiction-219a@1` — EU Article 219a invoice jurisdiction | [04_ARTICLE_219A_INVOICE_JURISDICTION.md](04_ARTICLE_219A_INVOICE_JURISDICTION.md) | `BLOCKED` |
| 5 | `candidate-eu-invoice-metadata-general-b2b-rc-phase5.6` / `eu-invoice-metadata-general-b2b-rc@1` — EU invoice metadata | [05_EU_INVOICE_METADATA.md](05_EU_INVOICE_METADATA.md) | `BLOCKED` |
| 6 | `candidate-hu-invoice-cross-border-service-phase5.6` / `hu-invoice-cross-border-service@1` — Hungarian cross-border invoice implementation | [06_HU_INVOICE_IMPLEMENTATION.md](06_HU_INVOICE_IMPLEMENTATION.md) | `BLOCKED` |
| 7 | `candidate-eu-recap-article262-service-phase5.6` / `eu-recap-article262-service@1` — EU Article 262 recapitulative statement | [07_ARTICLE_262_RECAP.md](07_ARTICLE_262_RECAP.md) | `BLOCKED` |
| 8 | `candidate-hu-a60-article262-implementation-phase5.6` / `hu-a60-article262-implementation@1` — Hungarian A60 implementation | [08_HU_A60.md](08_HU_A60.md) | `BLOCKED` |

## Separate the legal answer from case data

Each sheet distinguishes the **legal rule question**, **facts to verify at runtime**, and **implementation question**. Please do not certify customer/supplier facts as part of your legal response; identify the evidence standard and fields the runtime system must collect. The synthetic case only frames the legal questions.

## No automatic promotion

An imported adviser response is stored in a separate adviser-review record and appended to the audit chain. It cannot change a candidate, create an executable rule, or create repository human approval. The later lifecycle remains: adviser response → structured import → candidate revision if needed → deterministic validation → internal review → explicit human approval → executable rule.
