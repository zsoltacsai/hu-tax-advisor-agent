# Phase 5.6 research and model boundary

Research is frozen as `research-<generated id>` in `research/snapshots/` and
linked to non-executable country-rule candidates. The official German
Gesetze-im-Internet statute pages, NJT Hungarian VAT Act page, EUR-Lex
Directive consolidation dated 2025-04-14, NAV 26A60 instructions, and the BMF
UStAE entry point were accessed on 2026-10-08. This records access and reviewed
text; it does not mean every provision's effective date, applicability, or
interpretation was independently verified.

## Verified legal mapping (source text accessed)

| Issue | Official provision | Narrow finding | Limit |
|---|---|---|---|
| Article 44 correspondence | UStG §3a(2) | German B2B general service place follows recipient establishment / relevant fixed establishment | Special rules remain screened out; paragraph effective date requires confirmation |
| EU liability gate | Directive Articles 192a, 196 | EU-level test includes qualifying recipient and supplier not established in taxing state, subject to relevant fixed-establishment participation | Does not decide national implementation |
| German liability | UStG §13b(1), (5), (6), (7) | German-taxable §3a(2) services by another-EU-established supplier can place liability on qualifying recipient; exclusions and establishment tests matter | Scope/exceptions require legal review |
| German exemption boundary | UStG §4 | German exemptions are category-specific | Generic `GENERAL_SERVICE` cannot prove non-exemption |
| Invoice jurisdiction | Directive Article 219a; UStG §§14, 14a | Supplier-state routing can apply in specified non-established/recipient-liable cases; German statutory cross-border invoice provision exists | Full current-version and Hungarian implementation review required |
| Invoice contents/timing | Directive Articles 222, 226, 226a | Article 222 has a deadline; Article 226 lists required data; 226a permits omission of certain particulars in defined cases | No invoice text or metadata result is emitted |
| EU recap | Directive Article 262(1)(c) | Cross-border service entry is conditional on recipient liability and additional conditions | Article 44 alone is insufficient |
| HU form | NAV 26A60 instructions, 26A60-03 | Instructions describe relevant EU service transaction rows | Form instructions are not a complete taxpayer-specific statutory determination |
| HU territorial scope | Áfa tv. §§2, 37(1) | Hungarian territorial charging analysis must be separately evaluated against place-of-supply | No conclusion inferred from German reverse charge |

Sources: [UStG §3a](https://www.gesetze-im-internet.de/ustg_1980/__3a.html),
[UStG §13b](https://www.gesetze-im-internet.de/ustg_1980/__13b.html),
[UStG §14](https://www.gesetze-im-internet.de/ustg_1980/__14.html),
[UStG §14a](https://www.gesetze-im-internet.de/ustg_1980/BJNR119530979.html),
[UStG §18a](https://www.gesetze-im-internet.de/ustg_1980/__18a.html),
[UStG §4](https://www.gesetze-im-internet.de/ustg_1980/__4.html),
[EUR-Lex Directive consolidation 2025-04-14](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02006L0112-20250414),
[NJT Áfa tv.](https://njt.hu/jogszabaly/2007-127-00-00),
[NAV 26A60 instructions](https://nav.gov.hu/pfile/file?path=%2Fnyomtatvanyok%2Fletoltesek%2Fnyomtatvanykitolto_programok%2Fnyomtatvanykitolto_programok_nav%2F26A60%2Fkitoltesi-utmutato),
[BMF UStAE](https://www.bundesfinanzministerium.de/Web/DE/Themen/Steuern/Steuerarten/Umsatzsteuer/Umsatzsteuer_Anwendungserlass/umsatzsteuer_anwendungserlass.html).

## Candidate and approval state

The candidate lifecycle separates the shared EU Article 196 eligibility gate,
DE implementation, HU territorial VAT charging, invoice jurisdiction, invoice
metadata, HU invoice implementation, EU recap, and HU A60 reporting. Each
candidate has a research hash, candidate hash, structured checklist review,
and exact blocker list. No independent tax-law reviewer participated; all
candidates remain `BLOCKED`. No candidate is approval-ready and no approval
record was created. Only the pre-existing approved Article 44 and 45 rules are
executable. Article 58 remains unchanged and non-executable.

The preserved approval priority is: (1) EU Article 196 eligibility, (2) DE
Article 196 implementation, (3) HU supplier territorial VAT charging, (4)
Article 219a invoice jurisdiction, (5) EU invoice metadata, (6) HU invoice
implementation, (7) EU recap obligation, and (8) HU A60 implementation. A
later candidate cannot leapfrog an earlier candidate if multiple candidates
eventually qualify for human review.

## Fact model and stage output

The shared screen keeps customer business claim, taxable-person status, VAT-ID
presence/verification, supplier DE establishment and participation, service
classification, special-rule screen, German exemption evidence, upstream
Article 44 result, AAM status, and tax-point status separate. It only screens
EU Article 196 eligibility. Destination implementation returns unsupported or
not assessed unless an approved country pack is present. Every downstream HU,
invoice, reporting, AAM, and tax-point stage remains not assessed.

`STANDARD_TAXABLE_GENERAL_TECHNICAL_SERVICE` is a possible reviewed synthetic
classification label only. It is never inferred from WP CareGrid or from the
generic label `GENERAL_SERVICE`.

## Current limitations

- The current official consolidated texts do not establish paragraph-specific
  effective dates through 2026-10-08 for every cited German provision.
- No production data, VIES, customer records, provider APIs, or external
  transactional system is accessed.
- No German establishment or exemption status is inferred from customer or
  supplier country labels.
- German liability, HU charging, invoices, recap, A60, AAM, and tax point are
  not executable or decided.
- This is a decision-support research foundation, not professional legal or
  tax advice. A qualified adviser must resolve the listed blockers.
