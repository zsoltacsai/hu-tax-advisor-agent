# Supplier VAT charging boundary

Supplier VAT charging is a separate stage from place of supply and recipient reverse charge. The engine carries a determined place-of-supply country into a partial `vat_jurisdiction` stage, with an explicit note that taxability and exemption are not assessed. `supplier_vat_charging` remains `not_assessed` because Phase 5 has no human-approved rule for charging.

Reported AAM status is a fact only. AAM is not treated as a universal exemption; no rate or VAT amount is produced. Domestic HU consumer scenarios require a separately reviewed taxpayer status/eligibility assessment. EU SME scheme and AAM cross-border consequences are out of scope.
