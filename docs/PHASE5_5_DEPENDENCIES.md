# Phase 5.5 operational-stage dependencies

`rules/dependencies.json` declares prerequisites for place of supply, VAT jurisdiction, supplier charging, reverse charge, invoices, EU recapitulative reporting, A60 and AAM. Edges describe required upstream findings; they do not assert the legal test or make an outcome executable. Leaf nodes are named facts that must be supplied and reviewed. `src/tax_engine/dependencies.py` rejects cycles and reports every prerequisite not explicitly `determined`.

The graph is deliberately acyclic. Reverse-charge assessment requires place of supply, customer status, classification, supplier/recipient establishment facts and destination-state law. Invoice treatment additionally depends on charging/liability and tax point/jurisdiction. EU recap reporting depends on distinct reverse-charge, VAT-ID and reporting-period facts; A60 additionally depends on Hungarian form scope and taxpayer filing status. AAM remains a separate status/eligibility assessment.

No Phase 5.5 rule is wired into these stages. The graph must not be read as a checklist whose completion automatically produces tax advice; applicable legal rules and human review remain necessary.
