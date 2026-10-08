"""Build the qualified VAT adviser dossier and a curated portable copy."""
from __future__ import annotations
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.research_pipeline.workflow import ResearchPipeline, digest

OUT = ROOT / "docs" / "adviser-review"
DIST = ROOT / "dist" / "hu-tax-adviser-review-package"
SNAPSHOT_ID = "research-4f02d5661e1790d85b50"

CANDIDATES = [
    ("candidate-eu-article196-eligibility-phase5.6", "01_ARTICLE_196_ELIGIBILITY.md", "EU Article 196 eligibility"),
    ("candidate-de-vat-b2b-cross-border-services-reverse-charge-phase5.6", "02_DE_REVERSE_CHARGE.md", "German reverse charge"),
    ("candidate-hu-supplier-vat-territorial-charging-phase5.6", "03_HU_SUPPLIER_VAT_CHARGING.md", "Hungarian supplier territorial VAT charging"),
    ("candidate-eu-invoice-jurisdiction-219a-phase5.6", "04_ARTICLE_219A_INVOICE_JURISDICTION.md", "EU Article 219a invoice jurisdiction"),
    ("candidate-eu-invoice-metadata-general-b2b-rc-phase5.6", "05_EU_INVOICE_METADATA.md", "EU invoice metadata"),
    ("candidate-hu-invoice-cross-border-service-phase5.6", "06_HU_INVOICE_IMPLEMENTATION.md", "Hungarian cross-border invoice implementation"),
    ("candidate-eu-recap-article262-service-phase5.6", "07_ARTICLE_262_RECAP.md", "EU Article 262 recapitulative statement"),
    ("candidate-hu-a60-article262-implementation-phase5.6", "08_HU_A60.md", "Hungarian A60 implementation"),
]

SOURCES = {
    "candidate-eu-article196-eligibility-phase5.6": [("eu-vat-directive-2025-04-operational", ["Article 43", "Article 44", "Article 192a", "Article 196"])],
    "candidate-de-vat-b2b-cross-border-services-reverse-charge-phase5.6": [("de-ustg-2026-3a", ["3a Absatz 2"]), ("de-ustg-2026-13b", ["13b Absatz 1", "13b Absatz 5", "13b Absatz 6", "13b Absatz 7"]), ("de-ustg-2026-4", ["4 Nummer 8 bis 29"]), ("eu-vat-directive-2025-04-operational", ["Article 192a", "Article 196"]), ("de-bmf-ustae-current", ["Abschnitt 3a.1", "Abschnitt 13b.11"])],
    "candidate-hu-supplier-vat-territorial-charging-phase5.6": [("hu-vat-act-njt-consolidation-2025-12-20", ["2. §", "37. § (1)"])],
    "candidate-eu-invoice-jurisdiction-219a-phase5.6": [("eu-vat-directive-2025-04-operational", ["Article 192a", "Article 219a"]), ("de-ustg-2026-14-14a", ["14 Absatz 7", "14a Absatz 1"])],
    "candidate-eu-invoice-metadata-general-b2b-rc-phase5.6": [("eu-vat-directive-2025-04-operational", ["Article 222", "Article 226", "Article 226a"]), ("de-ustg-2026-14-14a", ["14 Absatz 4", "14a Absatz 1"])],
    "candidate-hu-invoice-cross-border-service-phase5.6": [("hu-vat-act-njt-consolidation-2025-12-20", ["159. § (2) c)", "169. § n)"]), ("eu-vat-directive-2025-04-operational", ["Article 219a", "Article 222", "Article 226"])],
    "candidate-eu-recap-article262-service-phase5.6": [("eu-vat-directive-2025-04-operational", ["Article 196", "Article 262(1)(c)", "Article 263", "Article 264"])],
    "candidate-hu-a60-article262-implementation-phase5.6": [("eu-vat-directive-2025-04-operational", ["Article 262(1)(c)"]), ("hu-nav-26a60-2026-filing-guidance", ["26A60 03-as lap"])],
}

QUESTIONS = {
"candidate-eu-article196-eligibility-phase5.6": [
"What is the exact legal relationship between Article 44 and Article 196 for the modeled service?",
"Which recipient categories and capacity/identification conditions satisfy Article 196?",
"What supplier establishment and fixed-establishment conditions apply?",
"When and how does Article 192a affect whether the supplier is regarded as established in the taxing state?",
"Is VAT identification a legal condition for each recipient category, or evidence of status?",
"Which material exceptions must be screened before this stage can return an eligibility result?",
"Which EU legal text/effective version applies to transactions on each relevant date in 2026?",
"Are additional legally material facts needed?"],
"candidate-de-vat-b2b-cross-border-services-reverse-charge-phase5.6": [
"Does UStG §13b(1), together with which applicable subsections, implement recipient liability for the narrow modeled service?",
"What exact supplier-establishment conditions apply?",
"What fixed-establishment participation test is relevant?",
"Which §13b exclusions must be modeled?",
"Does the actual service description require additional German classification?",
"Which German exemptions could prevent the proposed treatment, and what facts identify them?",
"Which transaction-date UStG and guidance versions apply during 2026?"],
"candidate-hu-supplier-vat-territorial-charging-phase5.6": [
"How do Áfa tv. §2 and §37(1) apply when the modeled place of supply is Germany?",
"If place of supply is Germany, is the transaction outside Hungarian VAT territorial charging scope? Please distinguish this from zero-rated, exempt, and reverse-charged treatment.",
"Does AAM status change the territorial-scope result or create separate obligations?",
"Does Hungarian/EU VAT-number status change the territorial-scope result?",
"Which Hungarian exceptions or taxpayer facts must be modeled?"],
"candidate-eu-invoice-jurisdiction-219a-phase5.6": [
"Which Member State's invoicing rules govern the reference scenario?",
"What conditions activate the supplier-state rule in Article 219a?",
"How does recipient liability under Article 196 affect that route?",
"How does self-billing alter the result?",
"How do supplier or destination fixed establishments affect it?",
"Which effective-date rules apply to the 2026 transaction date?"],
"candidate-eu-invoice-metadata-general-b2b-rc-phase5.6": [
"Confirm when supplier and customer VAT IDs are required and which identifiers belong on this invoice.",
"What service description and taxable-amount particulars are required?",
"What tax amount/rate particulars apply, including Article 226a omissions if available?",
"What invoice deadline applies and which event/date controls it?",
"Is the exact text \"Reverse charge\" mandatory, or is a semantic indication required? Please separate legal indication from language/translation and provider display questions.",
"Which version of Articles 222, 226 and 226a governs the transaction?"],
"candidate-hu-invoice-cross-border-service-phase5.6": [
"Which Áfa tv. provisions implement the applicable invoice requirements in this case?",
"Which Hungarian invoice fields are mandatory?",
"How must Community VAT numbers be presented?",
"What reverse-charge notation is legally required, and is exact Hungarian wording required?",
"What invoice timing rule applies to the cross-border service?",
"Which Hungarian-specific exceptions apply?",
"Do accounting-provider flags have legal significance or only implementation significance?"],
"candidate-eu-recap-article262-service-phase5.6": [
"Please confirm the required conjunction of supplier identification, recipient identification, recipient liability under Article 196, destination non-exemption and service scope.",
"Does the recipient VAT ID need to be validated or otherwise evidenced in a particular way?",
"How is destination non-exemption established for this service subtype?",
"Which reporting period and chargeable-event date control, and can obligation be decided while period remains unresolved?",
"What exceptions, corrections or additional conditions must be represented?"],
"candidate-hu-a60-article262-implementation-phase5.6": [
"What is the primary Hungarian statutory basis for this filing obligation?",
"Would the modeled supplier have to report this service in the 2026 26A60 return?",
"Which form page/section/row type applies?",
"What customer VAT-ID conditions apply?",
"Does AAM status change filing obligation or data requirements?",
"Which facts determine the reporting period?",
"How does period assignment depend on tax point/performance date?",
"Which taxpayer categories, corrections or exceptions must be screened?"],
}

FACTS = {
"Supplier": ["supplier_country (HU)", "supplier_taxable_person (YES/NO/UNKNOWN)", "Hungarian VAT identification/registration (not fully represented in the cross-border facts schema)", "AAM status (AAM/NOT_AAM/UNKNOWN; isolated from other stages)"],
"Customer": ["customer_country", "customer_claims_business", "customer_taxable_person_status", "customer establishment relevant to the service"],
"Service": ["service_classification", "special_rule_screened", "actual service characteristics, service subtype and mixed-supply facts"],
"Transaction": ["transaction_date", "place_of_supply status/country/rule version", "consideration, contract/performance facts, currency, payment/advance/refund facts are not in this Phase 5.6 cross-border envelope"],
"Establishment": ["supplier_destination_establishment.country/state/intervenes_in_supply", "recipient establishment and whether any fixed establishment receives the service (only summarized by upstream Article 44 evidence today)"],
"VAT identification": ["customer_vat_id country/present/verification", "supplier EU and HU VAT identifiers and reporting status (not fully modeled)"],
"Exemption": ["destination_taxability_status; service-specific statutory exemption category and evidence are not modeled"],
"Reporting": ["tax_point_status", "taxpayer filing/registration status, recap period, A60 period, correction/return facts are not modeled"],
}

ASSUMPTIONS = [
 ("Reference supplier is hypothetically established in Hungary and is a taxable person.", "Defines the narrow legal question; not asserted about a real taxpayer.", "All eight", "No; runtime evidence required", "Yes, confirm scope/definition where material"),
 ("Supplier has no relevant German fixed establishment participating in the supply.", "Allows the narrow non-established-supplier question to be posed.", "01, 02, 04, 05, 07, 08", "Yes, but legal materiality and evidence standard need review", "Yes, confirm test"),
 ("Customer is hypothetically established in Germany and claims to be a business.", "Defines destination and B2B reference branch.", "All eight", "Yes", "No, but confirm legal establishment/status test"),
 ("Customer taxable-person status is assumed verified for legal review; business claim alone is not proof.", "Separates legal condition from runtime claim.", "01, 02, 03, 04, 05, 06, 07, 08", "Yes", "Yes, confirm qualifying category"),
 ("A synthetic German VAT ID is present and synthetically valid in the review scenario.", "Permits discussion of identification-dependent paths without any live customer lookup.", "01, 04, 05, 06, 07, 08", "A real ID requires runtime/live verification", "Yes, confirm legal role; no live validation is implied"),
 ("The assumed recipient establishment relevant to the service is in Germany.", "Supports the hypothetical Article 44 branch only.", "01-08", "Yes, with evidence", "Yes, confirm establishment criteria"),
 ("Service is presented as a generic general B2B service and is not asserted to be an electronic service, consultancy, or composite supply.", "Service classification is unresolved; WP CareGrid is not classified.", "01-08", "Actual service characteristics can be collected at runtime", "Yes, adviser must define classification requirements"),
 ("No special place-of-supply rule is assumed only to frame the general-rule review question.", "The general rule cannot be applied until the runtime service screen is complete.", "01, 02, 03, 07", "Yes, based on contract and performance facts", "Yes, confirm exception taxonomy"),
 ("German non-exemption is not a reference-case fact; one candidate asks about a conditional reviewed taxable-service branch.", "A generic service label cannot establish exemption status.", "02, 07", "Service facts can be obtained; legal classification requires review", "Yes"),
 ("Transaction date is a synthetic 2026 date (the Phase 5.6 fixture uses 2026-10-08).", "The dossier asks for 2026 law but exact transaction-day version selection remains date-specific.", "All eight", "Yes", "Yes, confirm applicable legal versions"),
 ("VAT/AAM status is kept separate; reference AAM status is unknown until independently supplied.", "Avoids treating AAM as a universal exemption or cross-border conclusion.", "03, 06, 08", "Yes", "Yes, confirm consequences"),
 ("No self-billing arrangement is assumed.", "Article 219a and invoice responsibilities may depend on self-billing.", "04, 05, 06", "Yes", "Yes, confirm legal effect"),
 ("No conclusion is assumed on invoice wording, invoice provider configuration, reporting period, or tax point.", "These are independent downstream questions.", "04-08", "Yes", "Yes where legal effect is at issue"),
]

ISSUES = [
 ("VAT-001", "EU Article 196 conditions and Article 44 relationship", "Confirm recipient category, supplier scope, and the precise Article 44/196 relationship.", "01, 02, 07, 08"),
 ("VAT-002", "DE UStG §13b and supplier establishment", "Confirm §13b subsections, supplier establishment, fixed-establishment participation and exclusions.", "02, 04, 05"),
 ("VAT-003", "German service taxability and exemption classification", "A generic service label does not establish taxable/non-exempt treatment under UStG §4.", "02, 07"),
 ("VAT-004", "Transaction-date law versions and effective dates", "Consolidation dates are recorded separately from provision effective dates; several 2026 dates are unverified.", "01-08"),
 ("VAT-005", "HU territorial charging and AAM interaction", "Confirm Áfa tv. §§2/37(1), territorial scope, AAM, VAT-ID effects and exceptions.", "03, 08"),
 ("VAT-006", "Invoice jurisdiction under Article 219a", "Confirm supplier-state conditions, recipient liability, self-billing and establishment effects.", "04-06"),
 ("VAT-007", "EU invoice particulars, RC indicator and timing", "Confirm Articles 222/226/226a, exact versus semantic reverse-charge indication and language distinction.", "05, 06"),
 ("VAT-008", "Hungarian invoice implementation", "Exact Áfa tv. provisions, fields, VAT-ID presentation, notation, timing and provider semantics remain for review.", "06"),
 ("VAT-009", "Article 262 conjunction and exemption test", "Confirm recipient identification, Article 196 liability, service scope, destination non-exemption, period and exceptions.", "07, 08"),
 ("VAT-010", "Hungarian A60 statutory basis and filing conditions", "The current snapshot has NAV form guidance but does not pin a sufficient primary statutory basis or taxpayer-specific filing result.", "08"),
 ("VAT-011", "Runtime fact completeness and evidence standards", "Define what documentary/runtime evidence supports taxpayer status, establishments, service facts, IDs, date and filing status.", "01-08"),
 ("VAT-012", "NEW_REVIEW_ISSUE — candidate evidence-to-provision mapping", "Several frozen candidate evidence lists appear to cite provisions unrelated to their outcome scope or omit the key provision. Do not edit frozen candidates in this phase; correct only through a reviewed candidate revision.", "01, 03-08"),
 ("VAT-013", "Service classification boundary", "Actual service may be technical human work, automated electronic service, consultancy, mixed/composite, or another category; WP CareGrid remains unclassified.", "01, 02, 03, 07"),
]
ISSUE_LINKS = {
 "candidate-eu-article196-eligibility-phase5.6": ["VAT-001", "VAT-004", "VAT-011", "VAT-012"],
 "candidate-de-vat-b2b-cross-border-services-reverse-charge-phase5.6": ["VAT-002", "VAT-003", "VAT-004", "VAT-011", "VAT-012", "VAT-013"],
 "candidate-hu-supplier-vat-territorial-charging-phase5.6": ["VAT-004", "VAT-005", "VAT-011", "VAT-012"],
 "candidate-eu-invoice-jurisdiction-219a-phase5.6": ["VAT-004", "VAT-006", "VAT-011", "VAT-012"],
 "candidate-eu-invoice-metadata-general-b2b-rc-phase5.6": ["VAT-004", "VAT-006", "VAT-007", "VAT-012"],
 "candidate-hu-invoice-cross-border-service-phase5.6": ["VAT-004", "VAT-006", "VAT-008", "VAT-012"],
 "candidate-eu-recap-article262-service-phase5.6": ["VAT-004", "VAT-009", "VAT-011", "VAT-012", "VAT-013"],
 "candidate-hu-a60-article262-implementation-phase5.6": ["VAT-004", "VAT-009", "VAT-010", "VAT-011", "VAT-012"],
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def bullet(items):
    return "\n".join(f"- {x}" for x in items)


def main():
    pipeline = ResearchPipeline(ROOT)
    snapshot = pipeline.read_snapshot(SNAPSHOT_ID)
    registry = pipeline.sources
    candidates = {read_json(p)["candidate_id"]: read_json(p) for p in (ROOT/"rules/country-candidates/phase5.6/candidates").glob("*.json")}
    OUT.mkdir(parents=True, exist_ok=True)
    scenario = {
      "scenario_id": "synthetic-hu-de-general-b2b-2026",
      "synthetic_only": True,
      "transaction_year": 2026,
      "supplier": {"country": "HU", "taxable_person": "ASSUMED_FOR_LEGAL_REVIEW", "hungarian_vat_id": "ASSUMED_PRESENT_FOR_REVIEW; VERIFY_AT_RUNTIME", "aam_status": "NOT_ASSUMED; RECORD_SEPARATELY_AT_RUNTIME", "relevant_de_fixed_establishment": "ASSUMED_NONE_FOR_REVIEW; VERIFY_AND_ASSESS_PARTICIPATION_AT_RUNTIME"},
      "customer": {"country": "DE", "business_claim": "ASSUMED_FOR_REVIEW; VERIFY_AT_RUNTIME", "taxable_person_status": "ASSUMED_VERIFIED_FOR_REVIEW; VERIFY_AT_RUNTIME", "german_vat_id": "SYNTHETIC_PRESENT_AND_VERIFIED_FOR_REVIEW_ONLY; LIVE_CHECK_REQUIRED_IF_USED_OPERATIONALLY", "relevant_establishment": "ASSUMED_GERMANY_FOR_REVIEW; VERIFY_AT_RUNTIME"},
      "service": {"classification_hypothesis": "GENERAL_B2B_SERVICE", "special_place_rule": "ASSUMED_NONE_ONLY_TO_FRAME_REVIEW; SCREEN_ACTUAL_SERVICE_AT_RUNTIME", "actual_service_description": "NOT_SUPPLIED", "wp_caregrid_classification": "NOT_CLASSIFIED", "destination_exemption": "NOT_ASSUMED; adviser to review conditional taxable-service branch"},
      "transaction": {"date": "2026-10-08 (synthetic Phase 5.6 fixture date; actual date must be supplied at runtime)", "tax_point": "NOT_ASSESSED", "self_billing": "NOT_ASSUMED; VERIFY_AT_RUNTIME"},
      "review_only_assumptions": ["All facts are fictitious and exist only to ask narrow legal questions.", "No VAT treatment, tax amount, invoice text, filing duty or period is assumed.", "Where a candidate requires a taxable/non-exempt service, that is a conditional branch for adviser validation, not an established fact."],
      "runtime_verification_facts": ["Supplier/cust country and entity status", "Taxable-person capacity and evidence", "VAT IDs and current validation where legally/operationally required", "Supplier/recipient fixed establishments and participation/receipt", "Actual service terms and performance", "Special-rule and exemption classification", "Transaction date, tax point, self-billing, consideration, corrections", "AAM/registration/filing status, reporting period and required form version"]
    }
    write(OUT/"REFERENCE_SCENARIO.json", json.dumps(scenario, ensure_ascii=False, indent=2))

    start = """# Start here — qualified VAT adviser review\n\nThis package asks you to review eight narrow Hungarian/EU/German VAT rule candidates. It uses invented facts only. It is not a customer file, legal opinion, or instruction to charge VAT or file a return. The repository cannot authenticate the reviewer's professional credentials; reviewer_role is a declared role and must be confirmed by the maintainer outside this importer.\n\n## What the system does\n\nIt stores source references and versions, synthetic facts, candidate scopes, uncertainties and hashes. Today it can load only the previously approved general-service place-of-supply stages: EU Article 44 `@1` and Article 45 `@1`.\n\n## What it does not do\n\nIt does not decide German reverse charge, Hungarian VAT charging, AAM, invoice jurisdiction or contents, EU recap reporting, A60, tax point, or a real customer's VAT-ID status. It has no production/customer/provider/NAV/VIES connection. Article 58 remains `NEEDS_CHANGES`.\n\n## What we need from you\n\nReview the master package, reference scenario, issue register, and one sheet per candidate. For each candidate, return a JSON response conforming to `adviser-response.schema.json`. State your decision, corrections, missing facts/exceptions, legal-version notes, source notes and confidence. The candidate ID/hash and research ID/hash are printed on each sheet and must match your response.\n\nProfessional adviser review does not approve execution. A response is imported and audited separately. Any rule would still need candidate revision (if needed), deterministic validation, internal review, and explicit repository human approval.\n\n## How to record a response\n\n1. Copy the four linkage values from the chosen review sheet.\n2. Fill the response fields using `adviser-response.schema.json`. Avoid including personal adviser details; the role field is sufficient.\n3. Return the JSON response to the repository maintainer. The maintainer will import it with `python scripts/import_adviser_response.py RESPONSE.json`. Import validates the hashes and records an audit event; it cannot approve execution.\n\n**Exact next action: Qualified VAT adviser reviews the Phase 5.7 package.**\n"""
    write(OUT/"START_HERE.md", start)

    master = f"""# VAT adviser review package — Phase 5.7\n\n**Purpose:** professional review of eight blocked, non-executable candidates. **No adviser response is required to finish this handoff.** This is a decision-support research package, not professional advice.\n\n## Reference scenario\n\nSee [`REFERENCE_SCENARIO.json`](REFERENCE_SCENARIO.json). In plain terms: a synthetic HU taxable-person supplier provides a hypothesized general B2B service to a synthetic DE business customer in 2026. Supplier and customer status, IDs, establishments, service classification, date and other transactional inputs are explicitly divided between assumptions for legal review and facts that must be verified at runtime. The scenario does not presume a VAT treatment. German non-exemption is not a fact; it is a conditional question.\n\n## Rule architecture\n\nThe model separates: existing Article 44 place-of-supply stage → EU Article 196 eligibility → German implementation → Hungarian supplier territorial charging → invoice jurisdiction → invoice metadata/HU invoice implementation → EU recap → Hungarian A60. These stages are not interchangeable. Article 44 does not itself establish reverse charge; EU eligibility is not German implementation; reverse charge does not itself decide supplier charging, invoicing, or reporting. AAM and tax point remain separate.\n\nThe repository currently loads exactly `eu-vat-services-b2b-general@1` and `eu-vat-services-b2c-general@1`. Article 58 is still `NEEDS_CHANGES`. All eight Phase 5.6 candidates remain `BLOCKED`; none is executable or approval-ready.\n\n## What has been accessed and what remains open\n\nThe frozen Phase 5.6 snapshot `{SNAPSHOT_ID}` records 11 official-source entries and provisions, retrieved 2026-10-08. Official source text was accessed for the cited German UStG provisions, EU VAT Directive consolidation dated 2025-04-14, the NJT Áfa tv. consolidation displayed as 2025-12-20, NAV's 2026 26A60 instructions, and the BMF UStAE entry point. A source being reachable or its text being accessed does not establish that a specific provision is effective on a transaction date or applies to these facts. Germany paragraph-specific effective dates, the exact dated BMF guidance version, HU filing statutory basis, and several candidate source pins remain unresolved. See [Effective-date review](EFFECTIVE_DATE_REVIEW.md), [Source index](SOURCE_INDEX.md), and [Open issues](OPEN_ISSUES.md).\n\nA consistency review found candidate-to-provision evidence mapping concerns. These records are immutable and have not been altered. They are flagged as `VAT-012 NEW_REVIEW_ISSUE`; see each affected sheet and the issue register.\n\n## Decisions requested\n\nFor each candidate, use its review sheet and select exactly one: `APPROVE_AS_PROPOSED`, `APPROVE_WITH_CHANGES`, `REJECT`, `INSUFFICIENT_INFORMATION`, or `OUTSIDE_REVIEW_SCOPE`. Please also supply required changes, missing exceptions/facts, corrected interpretation, effective-date notes, source notes and confidence. “Approve” in this package means **adviser review only**, never execution approval.\n\n| Order | Candidate | Review sheet | Current status |\n|---:|---|---|---|\n"""
    for i, (cid, filename, label) in enumerate(CANDIDATES, 1):
        c = candidates[cid]
        master += f"| {i} | `{cid}` / `{c['rule_version_id']}` — {label} | [{filename}]({filename}) | `{c['status']}` |\n"
    master += "\n## Separate the legal answer from case data\n\nEach sheet distinguishes the **legal rule question**, **facts to verify at runtime**, and **implementation question**. Please do not certify customer/supplier facts as part of your legal response; identify the evidence standard and fields the runtime system must collect. The synthetic case only frames the legal questions.\n\n## No automatic promotion\n\nAn imported adviser response is stored in a separate adviser-review record and appended to the audit chain. It cannot change a candidate, create an executable rule, or create repository human approval. The later lifecycle remains: adviser response → structured import → candidate revision if needed → deterministic validation → internal review → explicit human approval → executable rule.\n"
    write(OUT/"VAT_ADVISER_REVIEW_PACKAGE.md", master)

    for cid, filename, label in CANDIDATES:
        candidate = candidates[cid]
        primary = []
        supporting = []
        for sid, provisions in SOURCES[cid]:
            src = registry.get(sid)
            if not src:
                primary.append(f"- `{sid}` — no registry entry found; adviser should identify a suitable authoritative source.")
                continue
            snapshot_provisions = [x["provision"] for x in snapshot["relevant_provisions"] if x["source_id"] == sid and x["verified"]]
            pin_note = "" if all(prov in snapshot_provisions for prov in provisions) else " **Adviser verify:** one or more requested provisions are not pinned as verified in the frozen snapshot."
            line = f"- `{sid}` — {', '.join(provisions)}. [{src['title']}]({src['official_url']}) (version `{src.get('version_date') or 'not pinned'}`).{pin_note}"
            if src['authority_level'] == 'primary': primary.append(line)
            else: supporting.append(line)
        if not primary: primary = ["- No sufficient primary source for this question is pinned in the current research snapshot; please identify the statutory basis (see VAT-010/VAT-012 as relevant)."]
        if not supporting: supporting = ["- No supporting official guidance is relied upon as a substitute for primary legislation. The BMF/NAV records in the research snapshot are access references only where relevant."]
        facts = {
          "candidate-eu-article196-eligibility-phase5.6": ["Article 44 path/rule version and place-of-supply evidence", "recipient category and taxable-person capacity", "customer establishment and VAT-ID evidence", "supplier taxable-person status, Member State and relevant FE/intervention", "actual service classification, exceptions and transaction date"],
          "candidate-de-vat-b2b-cross-border-services-reverse-charge-phase5.6": ["DE place-of-supply and Article 44 path", "supplier EU establishment and any German FE resources/participation", "recipient taxable-person status and establishment", "service detail and §13b exclusion facts", "German exemption category and evidence", "exact transaction date"],
          "candidate-hu-supplier-vat-territorial-charging-phase5.6": ["HU supplier status and territorial establishment facts", "place-of-supply result and date", "AAM/registration/VAT-ID status separately", "service consideration, performance and any statutory exception facts"],
          "candidate-eu-invoice-jurisdiction-219a-phase5.6": ["place of supply", "who is legally liable", "supplier establishments and intervention", "self-billing agreement and issuer", "transaction and chargeable-event dates"],
          "candidate-eu-invoice-metadata-general-b2b-rc-phase5.6": ["invoice jurisdiction first", "supplier/customer names, addresses, and VAT IDs", "service description, extent, amount and relevant dates", "liability result, tax basis/amount fields and self-billing", "invoice event/date"],
          "candidate-hu-invoice-cross-border-service-phase5.6": ["invoice jurisdiction routes to HU", "supplier registration and invoice issuer", "community VAT IDs, customer identity/address", "service description, consideration, performance/tax point", "self-billing and applicable transaction date"],
          "candidate-eu-recap-article262-service-phase5.6": ["supplier VAT identification/reporting status", "recipient taxable-person or qualifying legal-person status and identification", "Article 196 recipient liability", "destination exemption/service classification", "chargeable event, period, corrections"],
          "candidate-hu-a60-article262-implementation-phase5.6": ["taxpayer VAT registration/filing category and AAM status", "recipient VAT ID and customer status", "Article 196 liability and destination non-exemption facts", "transaction/tax point and reporting period", "applicable annual A60 form version and correction status"],
        }[cid]
        interpretation = {
          "candidate-eu-article196-eligibility-phase5.6": "The existing research frames Article 196 as a separate EU eligibility stage dependent on Article 44 path, recipient qualification and supplier establishment conditions. It does not decide destination-state liability. The reviewer must confirm the exact legal test.",
          "candidate-de-vat-b2b-cross-border-services-reverse-charge-phase5.6": "Existing research identifies UStG §3a(2) and §13b(1), (5)-(7) as the German statutory path to examine. No German recipient-liability conclusion has been adopted.",
          "candidate-hu-supplier-vat-territorial-charging-phase5.6": "Existing research treats Hungarian territorial charging as a separate question under Áfa tv. It does not infer zero rate, exemption, or charging from a DE place of supply or reverse charge.",
          "candidate-eu-invoice-jurisdiction-219a-phase5.6": "Existing research flags Article 219a's supplier-state route and dependencies. It does not determine which state's rules govern this transaction.",
          "candidate-eu-invoice-metadata-general-b2b-rc-phase5.6": "Existing research identifies Articles 222, 226 and 226a for review. No invoice fields or final wording have been approved.",
          "candidate-hu-invoice-cross-border-service-phase5.6": "Existing research has not resolved the HU invoice-law provisions for this branch. No provider behavior is treated as law.",
          "candidate-eu-recap-article262-service-phase5.6": "Existing research flags Article 262(1)(c)'s conjunction of conditions; Article 44 alone is insufficient. No recap obligation is determined.",
          "candidate-hu-a60-article262-implementation-phase5.6": "NAV form instructions are referenced, but the primary Hungarian statutory filing basis and taxpayer-specific duty remain unresolved. No period or filing obligation is determined.",
        }[cid]
        current_pin = "\n".join(f"- `{e['source_id']}` / `{e['provision']}` / `{e['source_version']}`" for e in candidate['evidence'])
        blockers = bullet(candidate["blockers"])
        body = f"""# {label}\n\n## Question\n\nCandidate `{cid}` / rule version `{candidate['rule_version_id']}`. Research `{candidate['research_id']}`; candidate hash `{candidate['candidate_hash']}`; research hash `{candidate['research_hash']}`.\n\n**LEGAL RULE QUESTION:** {candidate['scope']}\n\n**IMPLEMENTATION QUESTION:** Should the engine expose only this stage's result, with what status/value and dependencies, when the required facts are established?\n\n## Proposed rule\n\n{candidate['outcome_scope']}\n\nProposed conditions (not approved):\n{bullet(candidate['conditions'])}\n\n## Required facts\n\n**Facts for legal review scenario:** see `REFERENCE_SCENARIO.json`; they are assumptions, not customer evidence.\n\n**FACTS REQUIRED AT RUNTIME:**\n{bullet(facts)}\n\nPlease identify facts that are legally material but absent from the model.\n\n## Known exclusions\n\n{bullet(candidate['exceptions'])}\n\n## Primary legal sources\n\n{chr(10).join(primary)}\n\nThese are review references from the Phase 5.6 source registry; they are not a conclusion that a provision applies. A provision marked for adviser verification is not treated as verified evidence.\n\n## Supporting guidance\n\n{chr(10).join(supporting)}\n\nOfficial guidance supports interpretation but does not replace primary law. Do not rely on provider articles for legal conclusions.\n\n## Effective-date basis\n\nResearch snapshot date: `2026-10-08`; synthetic fixture date: `2026-10-08`; the dossier scenario is limited to year 2026 until an exact transaction date is supplied. Relevant consolidated source dates and effective-date verification are listed in `EFFECTIVE_DATE_REVIEW.md`. The German statute entries cite a 2026-06-29 act-level last-amendment date, not paragraph-level effective dates. Please state the date-specific legal versions and any transitional rules.\n\n## Current interpretation\n\n{interpretation}\n\n## Known uncertainty\n\n- No independent qualified adviser review is present; coding-agent structural review is not tax-adviser review.\n- The candidate's frozen evidence pins are:\n{current_pin}\n- Related open issues: {', '.join(ISSUE_LINKS[cid])}. `VAT-012` is a `NEW_REVIEW_ISSUE` for source/provision alignment. Candidate records have not been edited.\n\n## Current blocker\n\n{blockers}\n\n## Questions for adviser\n\n{bullet(QUESTIONS[cid])}\n\nPlease answer the legal question independently; the proposed conditions are not suggested answers. Distinguish legal requirements from evidence standards and runtime checks.\n\n## Possible adviser decision\n\nSelect one: `APPROVE_AS_PROPOSED`, `APPROVE_WITH_CHANGES`, `REJECT`, `INSUFFICIENT_INFORMATION`, `OUTSIDE_REVIEW_SCOPE`.\n\nReturn `required_changes`, `missing_exceptions`, `missing_facts`, `corrected_interpretation`, `effective_date_notes`, `source_notes`, `confidence` (`high|medium|low`) and comments in the structured response. Adviser approval is not repository human approval for execution.\n"""
        write(OUT/filename, body)

    write(OUT/"FACT_MODEL_REVIEW.md", "# Fact-model review\n\nThis is the current Phase 5.6 expected fact envelope, summarized for adviser review. It is not a claim that each field is sufficient. Values from the reference case are synthetic assumptions; actual case facts must be separately verified at runtime.\n\n" + "\n".join(f"## {group}\n\n{bullet(fields)}\n" for group, fields in FACTS.items()) + "\n## Adviser question\n\n**Are any legally material facts missing from this model?** Please separate facts that can be collected/verified at runtime from legal classification questions that need adviser review. Identify evidence standards, conflicts and escalation triggers.\n")
    assumptions = "# Assumption register\n\nNo real taxpayer/customer data is used. These are explicit framing assumptions or scenario values; none is silently promoted to a legal conclusion.\n\n| Assumption | Reason | Candidates | Runtime-verifiable? | Adviser confirmation required? |\n|---|---|---|---|---|\n"
    for a, reason, cids, runtime, adviser in ASSUMPTIONS:
        assumptions += f"| {a} | {reason} | {cids} | {runtime} | {adviser} |\n"
    write(OUT/"ASSUMPTIONS.md", assumptions)
    issues = "# Open issue register\n\nEach issue is distinct; candidate sheets reference these IDs. `NEW_REVIEW_ISSUE` means the issue was discovered while compiling this handoff and the underlying candidate was left untouched.\n\n| ID | Issue | What the adviser must resolve | Candidates |\n|---|---|---|---|\n"
    for issue_id, title, detail, cids in ISSUES:
        issues += f"| `{issue_id}` | {title} | {detail} | {cids} |\n"
    write(OUT/"OPEN_ISSUES.md", issues)

    # Effective-date table is generated only from immutable Phase 5.6 snapshot metadata.
    rows = []
    provisions_by_source = {}
    for row in snapshot["relevant_provisions"]:
        provisions_by_source.setdefault(row["source_id"], []).append(row["provision"])
    source_candidates = {}
    for cid, _, _ in CANDIDATES:
        for sid, _ in SOURCES[cid]: source_candidates.setdefault(sid, set()).add(cid)
    effective = "# Effective-date review\n\nThe 2026-10-08 date is the research retrieval/as-of date. A consolidation or version date is not automatically a provision's effective date. No new effective dates are inferred in this package.\n\n| Source / provision | Source version | Known consolidation/version date | Known effective date | Effective date verified? | Transaction dates currently supported | Open question |\n|---|---|---|---|---|---|---|\n"
    for sid in snapshot["primary_sources"] + snapshot["official_guidance"]:
        src = registry[sid]
        source_row = next(x for x in snapshot["sources_considered"] if x["source_id"] == sid)
        version = source_row.get("version_date") or "not pinned"
        consolidation = source_row.get("version_date") or "unknown"
        # Registry dates describe the source record unless provision-level legal
        # effect has been verified. Never present them as a provision date by default.
        known_eff = "not verified for this provision"
        verified = "yes" if source_row["verification"]["effective_date_verified"] else "no"
        if sid == "eu-vat-services-directive-2008-8":
            known_eff = "2010-01-01 source-level commencement; provision-level effect not independently verified"
            verified = "no"
        if sid == "hu-nav-26a60-2026-filing-guidance":
            known_eff = "not applicable: 2026 form-year metadata, not a transaction-rule effective date"
            verified = "no"
        provs = provisions_by_source.get(sid, src.get("relevant_provisions", []))
        for prov in provs:
            eff = f"`{src['id']}` / {prov}"
            questions = "Confirm exact provision commencement, amendments, transition and historical text for date." if verified == "no" else "Confirm source-level date applies to this provision and legal issue."
            if sid == "de-bmf-ustae-current": questions = "Identify exact dated UStAE version and applicable amendment paragraph."
            effective += f"| {eff} | {version} | {consolidation} | {known_eff} | {verified} | None for execution; research framing only for 2026-10-08 | {questions} |\n"
    effective += "\n**Adviser task:** state supported transaction date intervals per candidate. Do not infer paragraph commencement from the UStG act-level last-amendment date or from an EUR-Lex consolidation date.\n"
    write(OUT/"EFFECTIVE_DATE_REVIEW.md", effective)

    # Evidence index: one row per frozen provision reference.
    index = "# Source evidence index\n\nThe following are source records used in the immutable Phase 5.6 research snapshot. `Content verified` means the repository source metadata records official text access/verification; it does not certify legal applicability. Primary law is listed first.\n\n| Authority level | Source ID / provision | Jurisdiction | Authority | Official URL | Content accessed | Content verified | Effective date verified | Candidate dependencies |\n|---|---|---|---|---|---|---|---|---|\n"
    level_order = {"primary": 0, "court_authority": 1, "official_guidance": 2, "official_operational": 3, "provider": 4, "secondary": 5}
    source_rows = {x["source_id"]: x for x in snapshot["sources_considered"]}
    entries = []
    for sid, srcrow in source_rows.items():
        for prov in provisions_by_source.get(sid, []): entries.append((level_order.get(srcrow["authority_level"], 9), sid, prov, srcrow))
    for _, sid, prov, srcrow in sorted(entries):
        src = registry[sid]
        deps = ", ".join(sorted(x for x in source_candidates.get(sid, []))) or "shared research"
        verification = srcrow["verification"]
        index += f"| {srcrow['authority_level']} | `{sid}` / {prov} | {src['jurisdiction']} | {src['authority']} | [official source]({src['official_url']}) | {'yes' if verification['content_accessed'] else 'no'} | {'yes' if verification['content_verified'] else 'no'} | {'yes' if verification['effective_date_verified'] else 'no'} | {deps} |\n"
    write(OUT/"SOURCE_INDEX.md", index)

    response_schema = ROOT/"schemas/adviser-response.schema.json"
    schema_text = response_schema.read_text(encoding="utf-8")
    write(OUT/"adviser-response.schema.json", schema_text)

    # Curated package only: no source code, git data, test fixtures, audit log or archives.
    if DIST.exists():
        if DIST.is_symlink() or DIST.resolve().parent != (ROOT/"dist").resolve():
            raise RuntimeError(f"portable package target escaped its expected directory: {DIST}")
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    selected = ["START_HERE.md", "VAT_ADVISER_REVIEW_PACKAGE.md", "REFERENCE_SCENARIO.json", "FACT_MODEL_REVIEW.md", "ASSUMPTIONS.md", "OPEN_ISSUES.md", "EFFECTIVE_DATE_REVIEW.md", "SOURCE_INDEX.md", "adviser-response.schema.json"] + [name for _, name, _ in CANDIDATES]
    file_hashes = {}
    for filename in selected:
        data = (OUT/filename).read_bytes()
        (DIST/filename).write_bytes(data)
        file_hashes[filename] = digest(data.decode("utf-8"))
    manifest = {"package_id": "hu-tax-adviser-review-phase5.7", "research_id": SNAPSHOT_ID,
        "candidate_ids": [cid for cid, _, _ in CANDIDATES], "files": file_hashes,
        "contains_customer_data": False, "contains_execution_approval": False}
    manifest["package_hash"] = digest(manifest)
    (DIST/"MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    event_payload = {"package_id": manifest["package_id"], "package_hash": manifest["package_hash"], "research_id": SNAPSHOT_ID, "candidate_ids": manifest["candidate_ids"]}
    events = pipeline._audit_events()
    if not any(e["event_type"] == "ADVISER_REVIEW_PACKAGE_CREATED" and e["payload_hash"] == digest(event_payload) for e in events):
        pipeline.audit("ADVISER_REVIEW_PACKAGE_CREATED", "adviser-package-builder", manifest["package_id"], event_payload)
    print(f"Adviser dossier: {OUT}")
    print(f"Portable package: {DIST}")
    print(f"Candidates included: {len(CANDIDATES)}")
    print(f"Package hash: {manifest['package_hash']}")


if __name__ == "__main__": main()
