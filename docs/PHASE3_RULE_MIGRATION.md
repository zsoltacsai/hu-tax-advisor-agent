# Phase 3 rule migration: Phase 4.5

| Phase 3 rule | Phase 3 version | Phase 4.5 candidate | Current disposition |
|---|---|---|---|
| Article 44 general B2B | `eu-vat-services-b2b-general` / `eu-vat-services-b2b-general-2010-v1` | `candidate-eu-vat-services-b2b-general-v1-2026` / `eu-vat-services-b2b-general@1` | Human-approved after the exact typed approval ceremony; one bounded executable rule is loaded. |
| Article 45 general B2C | `eu-vat-services-b2c-general` / `eu-vat-services-b2c-general-2010-v1` | `candidate-eu-vat-services-b2c-general-v1-2026` / `eu-vat-services-b2c-general@1` | Human-approved after the exact typed approval ceremony; one bounded executable rule is loaded. |
| Article 58 electronic B2C with 59c gate | `eu-vat-electronic-b2c-art58` / `eu-vat-electronic-b2c-art58-2019-v1` | `candidate-eu-vat-electronic-b2c-art58-2019-2026-v1` / `eu-vat-electronic-b2c-art58@1` | Freshly researched, bounded to 2019-01-01 through 2026-12-31. Reviewer returns `NEEDS_CHANGES`; not executable. |

The Phase 3 copies remain in `tests/fixtures/phase3-proposed-rule-fixtures.json` as historical synthetic material. They were moved out of the production rule loader before Phase 4; none was silently restored. Phase 4 does not load proposed files. The approved directory contains Articles 44 and 45, each with an approval chain pinning its candidate, review, research snapshot, source versions, and hashes. Neither approval applies to Article 58.

## Semantic and evidence changes

The Article 44 and 45 rule identities retain their general-rule meaning and 2010-01-01 commencement, but their executable conditions are narrower. A specific `GENERAL_SERVICE` classification and reviewed special-rule exclusion screen are required. Article 44 additionally requires a reviewed taxable person acting as such, evidenced customer establishment, and an explicit review that no relevant recipient fixed establishment changes the location. Article 45 requires an explicit reviewed consumer and an explicit review that no relevant supplier fixed establishment changes the location. Unresolved cases do not fall back to a general rule.

Evidence was independently rechecked in Phase 4.5 against EUR-Lex, current European Commission guidance, and available NAV guidance. New frozen snapshots are `research-81efbc33abe0d0b310eb` (44), `research-8018a6583f3726c7a8d2` (45), and `research-14e807caa4ba8e0f50cf` (58/59c). Exact version and snapshot hash are pinned when approval occurs. The NJT primary page was not directly retrievable during this run and is marked unverified; current NAV instructions support but do not replace the primary Hungarian text.

The Article 58 candidate’s gate now explicitly excludes below-threshold/no-option cases, and its interval ends on 2027-01-01 because Directive (EU) 2025/516 changes Article 59c from that date. Its threshold state model does not capture all current-law aggregation, prior-year, establishment, option-period, and crossing-date facts; therefore the rule remains unapproved. No WP CareGrid classification is asserted.
