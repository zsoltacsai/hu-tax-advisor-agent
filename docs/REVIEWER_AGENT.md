# Reviewer Agent

`ReviewerAgent` independently checks a frozen research snapshot and proposed candidate. It produces explicit findings for source quality, source version, primary legal basis, candidate conditions/outcome, effective dates, fact requirements, uncertainty, exceptions, and engine compatibility. A mismatch, unsupported assertion, missing primary source, unresolved uncertainty, or unverified version prevents readiness.

The reviewer is deterministic and local in this phase. It does not repeat or trust a Research Agent confidence score. Its strongest outcome is `APPROVE_FOR_HUMAN_REVIEW`; it cannot perform final approval or change an executable registry. Review records and audit events are immutable.
