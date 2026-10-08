# MCP design — proposed only
No server implemented or deployed. Future server must be private, authenticated, tenant-scoped, rate-limited, least-privilege, and have read-only access to approved legal records. The local Phase 4 research/review pipeline is not exposed over MCP. Shared request schema is schemas/mcp-request.schema.json; response/error envelope is schemas/mcp-response.schema.json. Inputs include request ID, as-of date, jurisdiction and payload. Outputs include status, result, source refs, uncertainty, human-review flag and timestamp.

| Tool | Inputs -> output | Error states | Access/source requirements |
|---|---|---|---|
| tax_research | issue/date -> cited notes | SOURCE_UNAVAILABLE, DATE_AMBIGUOUS | Authenticated; primary sources |
| tax_analyze_transaction | facts -> draft decision | MISSING_FACTS, CLASSIFICATION_UNCLEAR | Tenant read; no write |
| tax_compare_regimes | profile/year -> alternatives | INPUT_INCOMPLETE, ELIGIBILITY_UNKNOWN | Read only; current law |
| tax_validate_assumptions | assumptions/evidence -> findings | EVIDENCE_MISSING, SOURCE_CONFLICT | Read only |
| tax_review_invoice | redacted fields -> issues | PII_DETECTED, INVOICE_INCOMPLETE | No invoice write |
| tax_generate_decision_matrix | scenarios -> matrix | SCENARIO_INCOMPLETE | Evidence-linked |
| tax_get_legal_sources | issue/date -> source refs | SOURCE_NOT_FOUND, ACCESS_DENIED | Public sources |
| tax_check_rule_freshness | rule IDs -> status/date | RULE_UNKNOWN, SOURCE_UNAVAILABLE | Must report check time |
| tax.research | narrow issue/date -> frozen research snapshot | SOURCE_NOT_VERIFIED, DATE_AMBIGUOUS | Structured result, untrusted external content, no rule promotion |
| tax.rule.status | rule/candidate ID -> lifecycle/freshness | RULE_UNKNOWN | Read only; distinguish proposed and approved |
| tax.rule.evidence | rule ID -> source/version/provision refs | SOURCE_UNKNOWN | Read only; snapshot exact versions |
| tax.explain | decision ID -> stages/evidence/uncertainties | DECISION_UNKNOWN | Deterministic engine trace; no advice extension |
| tax_export_advice | result/format -> JSON/MD | SCHEMA_INVALID, ACCESS_DENIED | Tenant export permission/audit |

There is deliberately no `tax.rule.approve` tool and no AI-callable approval operation. Human approval remains outside MCP and requires the local controlled workflow. No tool may file returns, issue invoices, change tax status/configuration, or commit tax decisions. Never expose secrets, hidden reasoning, or cross-tenant data.
