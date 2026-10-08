# Fact-model review

This is the current Phase 5.6 expected fact envelope, summarized for adviser review. It is not a claim that each field is sufficient. Values from the reference case are synthetic assumptions; actual case facts must be separately verified at runtime.

## Supplier

- supplier_country (HU)
- supplier_taxable_person (YES/NO/UNKNOWN)
- Hungarian VAT identification/registration (not fully represented in the cross-border facts schema)
- AAM status (AAM/NOT_AAM/UNKNOWN; isolated from other stages)

## Customer

- customer_country
- customer_claims_business
- customer_taxable_person_status
- customer establishment relevant to the service

## Service

- service_classification
- special_rule_screened
- actual service characteristics, service subtype and mixed-supply facts

## Transaction

- transaction_date
- place_of_supply status/country/rule version
- consideration, contract/performance facts, currency, payment/advance/refund facts are not in this Phase 5.6 cross-border envelope

## Establishment

- supplier_destination_establishment.country/state/intervenes_in_supply
- recipient establishment and whether any fixed establishment receives the service (only summarized by upstream Article 44 evidence today)

## VAT identification

- customer_vat_id country/present/verification
- supplier EU and HU VAT identifiers and reporting status (not fully modeled)

## Exemption

- destination_taxability_status; service-specific statutory exemption category and evidence are not modeled

## Reporting

- tax_point_status
- taxpayer filing/registration status, recap period, A60 period, correction/return facts are not modeled

## Adviser question

**Are any legally material facts missing from this model?** Please separate facts that can be collected/verified at runtime from legal classification questions that need adviser review. Identify evidence standards, conflicts and escalation triggers.
