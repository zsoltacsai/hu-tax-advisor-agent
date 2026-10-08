# Effective-date and rule-version policy

## Required question
For a transaction tax point/date D, select only a rule version whose legal effective interval contains D, after checking commencement and transitional provisions. Publication date is not effective date. Tax year is not a substitute for transaction date.

## Rule version fields
Each source/rule record should retain publication_date, effective_from, effective_to (exclusive end convention documented per rule), tax_year where applicable, version_date (snapshot date), transition references, status (proposed, enacted_not_effective, effective, superseded), and retrieval timestamp. Preserve prior versions; never overwrite an old rule snapshot.

## Selection
1. Obtain transaction date and tax point; if uncertain, stop and escalate.
2. Resolve legal effective intervals and specific commencement/transition clauses from official acts.
3. Select the interval containing the date; verify no later amendment with retrospective or transitional application.
4. Separately expose current law and announced future law. Do not substitute either for historical law.
5. Annual thresholds require the relevant tax year and correct turnover base.
6. If the applicable version cannot be verified, return cannot_determine with SOURCE_NOT_VERIFIED or LIVE_VERIFICATION_REQUIRED.

The registry records both retrieval and version dates. A reachable URL is not proof that its content is current or effective for a transaction.

Phase 4.5 Article 44/45 candidate versions begin 2010-01-01 based on Directive 2008/8/EC Article 2. The Article 58 proposal is bounded to 2019-01-01 through 2026-12-31 because Directive (EU) 2025/516 changes Article 59c from 2027-01-01. It is not approved; a separate future version and a complete threshold/option fact model are required. See [PHASE4_5_RESEARCH.md](PHASE4_5_RESEARCH.md).
