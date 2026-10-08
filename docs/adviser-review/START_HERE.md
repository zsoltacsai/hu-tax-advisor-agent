# Start here — qualified VAT adviser review

This package asks you to review eight narrow Hungarian/EU/German VAT rule candidates. It uses invented facts only. It is not a customer file, legal opinion, or instruction to charge VAT or file a return. The repository cannot authenticate the reviewer's professional credentials; reviewer_role is a declared role and must be confirmed by the maintainer outside this importer.

## What the system does

It stores source references and versions, synthetic facts, candidate scopes, uncertainties and hashes. Today it can load only the previously approved general-service place-of-supply stages: EU Article 44 `@1` and Article 45 `@1`.

## What it does not do

It does not decide German reverse charge, Hungarian VAT charging, AAM, invoice jurisdiction or contents, EU recap reporting, A60, tax point, or a real customer's VAT-ID status. It has no production/customer/provider/NAV/VIES connection. Article 58 remains `NEEDS_CHANGES`.

## What we need from you

Review the master package, reference scenario, issue register, and one sheet per candidate. For each candidate, return a JSON response conforming to `adviser-response.schema.json`. State your decision, corrections, missing facts/exceptions, legal-version notes, source notes and confidence. The candidate ID/hash and research ID/hash are printed on each sheet and must match your response.

Professional adviser review does not approve execution. A response is imported and audited separately. Any rule would still need candidate revision (if needed), deterministic validation, internal review, and explicit repository human approval.

## How to record a response

1. Copy the four linkage values from the chosen review sheet.
2. Fill the response fields using `adviser-response.schema.json`. Avoid including personal adviser details; the role field is sufficient.
3. Return the JSON response to the repository maintainer. The maintainer will import it with `python scripts/import_adviser_response.py RESPONSE.json`. Import validates the hashes and records an audit event; it cannot approve execution.

**Exact next action: Qualified VAT adviser reviews the Phase 5.7 package.**
