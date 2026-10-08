# Approval integrity and immutable rule versions

An approval wrapper pins a canonical SHA-256 hash of the candidate, reviewer record, research snapshot, and final executable rule, plus each evidence source ID, provision, version, and snapshot ID. The human approval audit event repeats these hashes. The loader verifies the hash chain, matching candidate/review/snapshot records, reviewer outcome, candidate-to-rule transformation, approval event, source pins, current freshness checks, and filename/version identity before loading.

Approved JSON is write-once through the lifecycle API. A changed file or altered/missing candidate, review, snapshot, or audit event fails closed. A proposed/review-only copy cannot load because it has no valid wrapper and matching human approval event. Any material update must use a new candidate/version and approval.

SHA-256 and a local hash chain detect accidental or partial tampering; they do not prevent a repository administrator from rewriting all local files and recomputing all hashes. The CLI actor field remains an unauthenticated label. This is a local development integrity control, not a cryptographic identity or production security boundary.
