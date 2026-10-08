# Tax Reasoning Engine v1

## Flow
Structured contexts -> deterministic normalization -> taxpayer/AAM context and generic threshold comparison -> customer location/status -> reviewed service category -> date-scoped rule selection -> conflict/evidence checks -> staged result -> escalation.

Each stage returns status, value, rule ID, evidence, assumptions, confidence and reason. The engine uses no LLM and executes no arbitrary rule code. It hashes canonical input/rule/as-of data to create deterministic decision IDs and trace text. Missing facts stay unknown; contradicted location evidence is not reconciled heuristically.

Only rules with registered evidence can produce legal stage conclusions. Overall results remain partial when VAT charging, reverse charge, invoicing or reporting is outside reviewed scope. No output writes or acts on another system.