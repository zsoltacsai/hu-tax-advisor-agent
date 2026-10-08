# Human rule approval

Only a candidate in `HUMAN_REVIEW_REQUIRED`, with a reviewer outcome `APPROVE_FOR_HUMAN_REVIEW`, may be promoted. The local CLI requires an interactive terminal, a human actor label, and the operator to type the exact confirmation phrase `I APPROVE THIS RULE FOR EXECUTION`; a CLI flag or piped input cannot approve. It validates the engine rule and evidence again, requires current source checks, records a hash-chained `HUMAN_APPROVAL` event, stores content-hashed approval metadata, and writes an immutable wrapper into `rules/approved/`.

AI output, reviewer output, a candidate status field, and a caller-supplied `approved: true` are never sufficient. There is no MCP approval tool. The CLI's actor string is an audit label, not authentication, and a local user who can edit the repository can bypass filesystem controls. Production-grade identity and access controls are required before deployment.


Before the confirmation prompt, the CLI displays the immutable candidate hash, rule ID/version/summary, effective interval, source IDs and versions, reviewer status, known limitations, unresolved questions, and research snapshot hash. `approval-preview --candidate ID` shows the same content without approving. The exact confirmation phrase is tied to the candidate hash shown in that invocation.
