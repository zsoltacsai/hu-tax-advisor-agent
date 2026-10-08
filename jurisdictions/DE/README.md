# Germany (DE) destination implementation research

This is a research and candidate area, not an executable country pack. The
engine must fail closed unless a Germany rule has its own independent review,
explicit human approval, immutable approved record, and valid provenance chain.

## Source findings as of 2026-10-08

- UStG §3a(2) is the German domestic correspondence to the Article 44 general
  B2B place-of-supply rule. It places the service where the business recipient
  is established, or at the relevant recipient fixed establishment. It has
  statutory exceptions that are outside this narrow screen.
- UStG §13b(1), read with §13b(5), contains the recipient-liability route for
  German-taxable §3a(2) services supplied by an entrepreneur established in
  the rest of the EU. Sections 13b(6) and (7) require exception and supplier
  establishment screening. A German fixed establishment's participation is
  material; unresolved intervention is a review condition.
- UStG §§14 and 14a contain German invoicing provisions. Section 14a(1)
  specifically addresses a supplier established in another Member State when
  the recipient owes the tax. The application of EU Article 219a and Hungarian
  supplier-state invoice rules still requires an independent, date-specific
  review before an operational invoice conclusion.
- UStG §18a describes German recapitulative statements. It is not the filing
  rule for a HU supplier's outbound transaction; that requires the applicable
  Hungarian filing law and form instructions.
- UStG §4 has a broad exemption schedule. `GENERAL_SERVICE` alone is not enough
  to establish that an actual service is taxable and non-exempt in Germany.

The official federal justice statute pages were accessed on 2026-10-08. The
consolidated UStG page states a last amendment dated 2026-06-29. That act-level
amendment date does not prove the effective date of every cited paragraph.
Registry entries preserve this distinction (`effective_date_verified: false`).
The BMF UStAE is administrative guidance, not legislation; current-version
paragraph wording and exact version pinning remain a review blocker.

## Scope and guardrails

The only contemplated rule is German destination reverse-charge
implementation for the narrowly reviewed path: HU supplier, DE taxable-person
recipient, reviewed taxable general service, Article 44 place of supply in DE,
no special rule, and no participating relevant German supplier establishment.
The current pack is deliberately non-executable. It does not decide invoice
fields, Hungarian VAT charging, AAM, OSS, rates, registrations, reporting, or
tax point.

No WP CareGrid service has been classified. Actual service characteristics
must be reviewed; an automated electronic service, human-performed technical
service, consultancy, mixed/composite supply, and other service types may have
different treatment.

## Open review items

1. Confirm paragraph-specific effective dates/version for the transaction date.
2. Have German VAT counsel/accountant review UStG §13b scope, exceptions,
   establishment interaction, and narrow service taxability assumptions.
3. Independently review the Article 219a route and HU invoice implementation.
4. Independently review Article 262(1)(c), the Hungarian 26A60 statutory basis,
   taxpayer filing status, corrections, and reporting period.
5. Confirm AAM interaction separately; no AAM outcome is modeled here.
