# Tax Engine v1 scope

## SUPPORTED
- Evidence-backed place-of-supply determination for explicitly reviewed GENERAL_SERVICE scenarios under the general B2B/B2C rules in EU VAT Directive Articles 44 and 45, when required customer/supplier locations and customer status are verified, and a special place rule has been explicitly reviewed as not applicable.
- Explicitly classified ELECTRONICALLY_SUPPLIED_SERVICE to EU B2C as an Article 58 candidate only when Article 59c threshold/option assessment is explicitly reviewed and permits Article 58; otherwise the place remains unresolved.
- Rule-effective-date selection, evidence attachment, generic threshold comparison, conflict detection, staged output and escalation.

## PARTIALLY SUPPORTED
- HU domestic general services and cross-border EU general services: place-of-supply stage only. AAM/VAT charging treatment remains unresolved because election, exclusions, SME status and other facts are not modeled completely.
- Non-EU general services: EU Directive place-of-supply rule candidate only. Foreign-country VAT, registration, use/enjoyment rules and local compliance are not decided.
- AAM: reported context and a year-specific threshold comparator only; no exemption eligibility or cross-border extension decision.
- Electronic B2C: conditional place rule candidate only, not OSS or VAT collection treatment.

## NOT SUPPORTED
- SaaS/maintenance classification from names or delivery channels; consultancy/mixed supplies unless independently classified into supported general-service category; special place rules; Article 59 non-EU B2C categories; reverse-charge final determination; VAT rate/amount; invoice language; credit notes/refunds; subscription tax point; OSS/IOSS; EU SME election; foreign exchange; reporting/filing.

## REQUIRES LIVE DATA
- Real VAT-ID status/VIES, taxpayer election/registration status, turnover ledger, current foreign customer status and country evidence. Phase 3 makes no live calls.

## REQUIRES HUMAN REVIEW
- All final VAT charging/invoice/reporting outcomes; uncertain classification/status/location/tax point; AAM eligibility or threshold boundary; special-rule exceptions; conflicting sources/rules; any non-EU local consequence. Every Phase 3 overall result is conservative and may remain partial or unresolved.