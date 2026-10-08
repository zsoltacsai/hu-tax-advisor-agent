# Evaluation framework

## Executable checks

Run:

```powershell
python scripts/bootstrap_research_examples.py
python -m unittest discover -s tests -v
python scripts/validate.py
```

The validator checks every local schema, Phase 2 contract/scenario fixture, source registry metadata, research snapshots, proposed/reviewed/approved rule records, source references, audit-chain integrity, rule loading, and source dependency linkage. Unit tests check effective-date boundaries, schema and fake-citation rejection, source hierarchy, snapshot reproducibility, prompt-injection-as-data, candidate isolation, reviewer disagreement, human-only promotion, rejected candidates, source changes, freshness gating, dependencies, supersession and deterministic engine behavior.

## Evaluation dimensions

The harness separates structural validity from tax correctness. It measures snapshot schema validity, citation/source IDs, source ranking, effective-date handling, unsupported assertions, reviewer disagreement, approval boundary, candidate isolation, source dependency integrity, rule freshness and append-only audit integrity. Research confidence is deterministic and cannot use the model's self-rating.

Do not score substantive tax correctness until expected outcomes are supported by reviewed primary material and qualified adviser review. Research examples are issue-spotting packets, not legal opinions. The Phase 4.5 approved executable set consists of the human-approved general Article 44 and Article 45 rules. Phase 5 candidates remain proposed and non-executable.


Phase 4.5 adds approval-chain tamper/missing-record checks, full rule-version provenance, specific-over-general selection, reviewed fixed-establishment gates, Article 58 no-fallback behavior, and synthetic end-to-end Article 44/45 place-of-supply tests. Test approvals use isolated temporary repositories and synthetic actors; they never approve rules in the repository.

## Phase 5 evaluation

Phase 5 adds tests for synthetic-only scenarios, source/evidence snapshots, non-executable candidate review state, jurisdiction carry-forward, and the prohibition on inferring supplier charging, reverse charge, invoice treatment, reporting or AAM effects. `python scripts/validate.py` checks all schemas, source and internal references, scenarios, contracts, snapshots, candidates, reviews and approval loading. No substantive correctness score is assigned to unapproved candidates. Current executable set: the human-approved Article 44 and Article 45 rules only.

Phase 5.5 adds deterministic dependency-graph validation (including cycle rejection), readiness/hash-link checks, and an Article 196 fact-schema fixture showing that VAT-ID verification does not determine taxable-person status or liability. Dependency checks fail closed unless prerequisites are explicitly determined. These are structural checks only; no downstream legal decision rules or substantive correctness scores were added.
