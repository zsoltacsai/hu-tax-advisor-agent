# HU Tax Advisor Agent

Independent, synthetic-only Hungarian VAT decision-support foundation. Phase 4 adds local tax research and rule review workflows. It does not provide professional legal or tax advice and is not connected to WP CareGrid, customer data, billing providers, NAV APIs, VIES, or production systems.

## Architecture

`sources/registry.json` records source identity, authority, version/freshness metadata, and URL/content verification flags. `ResearchAgent` ingests untrusted structured drafts and freezes validated snapshots in `research/snapshots/`. Candidates live under `rules/proposed/`; reviewer assessments live under `rules/reviews/`; only explicit human promotion creates an approval-wrapped record under `rules/approved/`. `src/tax_engine/` loads only approved records with valid approval/audit hashes and current source checks. `state/audit.jsonl` is an append-only hash chain. No model API, crawler, or external data connection is implemented.

The original Phase 3 rules remain archived as synthetic fixtures. Phase 4.5 produced new, freshly researched candidates. Articles 44 and 45 have completed their explicit human approval workflows and are the currently loaded executable rules. Article 58 needs changes and is not executable.

## Source hierarchy

Primary Hungarian/EU law; applicable court/binding decisions; official NAV/European Commission guidance; official operational documentation; provider documentation; secondary professional commentary. Guidance does not equal legislation; provider/help and secondary sources cannot alone support material executable rules. See [docs/SOURCE_POLICY.md](docs/SOURCE_POLICY.md) and [docs/SOURCE_FRESHNESS_POLICY.md](docs/SOURCE_FRESHNESS_POLICY.md).

Research snapshots distinguish discovery, URL reachability, content access/verification, effective-date verification, and applicability. A reachable URL does not prove legal content or applicability. Snapshot hashes freeze the sources, versions, provisions, facts, findings, and uncertainties so later registry changes do not silently rewrite historical research.

## Effective dates and evidence

Rule selection uses the transaction date against half-open effective intervals. Publication date, source version date, legal effective date, and issue applicability are separate. The tax point is not calculated. Approved rules require source freshness checks; unknown, stale, changed, and live-verification-only sources block execution. Provenance links source → research → candidate → review → human approval → executable version. See [docs/EFFECTIVE_DATE_POLICY.md](docs/EFFECTIVE_DATE_POLICY.md), [docs/DECISION_PROVENANCE.md](docs/DECISION_PROVENANCE.md), and [docs/SOURCE_DEPENDENCIES.md](docs/SOURCE_DEPENDENCIES.md).

## Research, review, and approval

`ResearchAgent` accepts structured input but does not fetch sources or make legal determinations. Confidence is recomputed and cannot be raised by model self-rating. `ReviewerAgent` independently checks source quality/version, legal basis, candidate logic, dates, facts, exceptions, uncertainty, and schema compatibility. Its strongest state is `APPROVE_FOR_HUMAN_REVIEW`.

Only a human may promote a rule, through the explicit local CLI command below. No MCP approval tool exists. The CLI actor label is an audit string, not authenticated identity, so this workflow is not suitable for an unattended agent or production deployment. See [docs/RULE_APPROVAL.md](docs/RULE_APPROVAL.md), [docs/RULE_LIFECYCLE.md](docs/RULE_LIFECYCLE.md), and [docs/RESEARCH_SECURITY.md](docs/RESEARCH_SECURITY.md).

## Current proposed rule scope

The Phase 4.5 candidates cover narrow general B2B Article 44 and general B2C Article 45 versions (`@1`), plus an Article 58 candidate that remains `NEEDS_CHANGES`. Articles 44/45 require reviewed general-service classification, special-rule screening, customer/supplier status, location evidence, and an explicit fixed-establishment review. Specific or unimplemented service categories never fall through to a general rule. WP CareGrid classification remains unresolved. See [docs/RULE_SCOPE.md](docs/RULE_SCOPE.md).

## Phase 5 operational boundary

Phase 5 adds versioned legal research snapshots, evidence and candidate records for reverse charge, invoice metadata, and EU/HU recapitulative reporting. These candidates were deterministically reviewed as `NEEDS_CHANGES`; none was human-approved or made executable. The engine may carry an evidence-backed place-of-supply country into a partial jurisdiction stage, while supplier charging, reverse charge, invoice treatment, reporting and AAM effect remain `not_assessed`. Read [docs/REVERSE_CHARGE.md](docs/REVERSE_CHARGE.md), [docs/VAT_CHARGING.md](docs/VAT_CHARGING.md), [docs/INVOICE_TREATMENT.md](docs/INVOICE_TREATMENT.md), [docs/EU_RECAP_REPORTING.md](docs/EU_RECAP_REPORTING.md), [docs/AAM_BOUNDARY.md](docs/AAM_BOUNDARY.md), and [docs/PHASE5_RESEARCH.md](docs/PHASE5_RESEARCH.md).

## Local workflow and evaluation

With the repository Python environment and `jsonschema` installed:

```powershell
python scripts/bootstrap_research_examples.py
python -m unittest discover -s tests -v
python scripts/validate.py
```

Submit/review/propose/approve commands are available through `python scripts/research_cli.py --help`. Human promotion requires a passing review, current source checks, an interactive terminal, a human actor label, and typed confirmation; non-interactive approval is disabled. Evaluation covers schemas, source and provision references, source hierarchy, effective dates, candidate isolation, reviewer disagreement, approval, freshness, dependencies, audit integrity, and deterministic engine behavior. It does not certify substantive tax correctness. See [docs/EVALUATION.md](docs/EVALUATION.md).

## Limitations

There is no LLM integration, autonomous source retrieval, identity provider, accountant approval, or production integration. Research is a curated snapshot, not a comprehensive legal search or legal opinion. No source is automatically marked current; a human must record checks. The approval actor label is not authentication. Source freshness windows are policy defaults requiring governance review. Article 44/45 exceptions and all downstream tax issues remain incompletely analyzed. Never use partial output as an operational tax instruction.
