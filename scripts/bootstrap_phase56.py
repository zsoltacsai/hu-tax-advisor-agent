"""Create immutable Phase 5.6 research and blocked candidate/review records.

This is a one-time deterministic bootstrap. It contains no approval path.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.research_pipeline.workflow import ResearchPipeline, digest, write_immutable


def main():
    p = ResearchPipeline(ROOT)
    source_ids = [
        "de-ustg-2026-3a", "de-ustg-2026-13b", "de-ustg-2026-14-14a",
        "de-ustg-2026-18a", "de-ustg-2026-4", "de-bmf-ustae-current",
        "eu-vat-directive-2025-04-operational",
        "eu-vat-directive-current-consolidation-2025-04-14",
        "eu-vat-services-directive-2008-8",
        "hu-vat-act-njt-consolidation-2025-12-20",
        "hu-nav-26a60-2026-filing-guidance",
    ]
    provisions = {
        "de-ustg-2026-3a": ["3a Absatz 2", "3a Absatz 3", "3a Absatz 5"],
        "de-ustg-2026-13b": ["13b Absatz 1", "13b Absatz 5", "13b Absatz 6", "13b Absatz 7"],
        "de-ustg-2026-14-14a": ["14 Absatz 4", "14 Absatz 7", "14a Absatz 1"],
        "de-ustg-2026-18a": ["18a Absatz 2", "18a Absatz 7 Nummer 3", "18a Absatz 8", "18a Absatz 10"],
        "de-ustg-2026-4": ["4 Nummer 8 bis 29"],
        "de-bmf-ustae-current": ["Abschnitt 3a.1", "Abschnitt 13b.11"],
        "eu-vat-directive-2025-04-operational": ["Article 192a", "Article 196", "Article 219a", "Article 222", "Article 226", "Article 226a", "Article 262(1)(c)"],
        "eu-vat-directive-current-consolidation-2025-04-14": ["Article 44", "Article 43"],
        "eu-vat-services-directive-2008-8": ["Article 2", "Article 44", "Article 45"],
        "hu-vat-act-njt-consolidation-2025-12-20": ["37. § (1)", "140. §", "159. § (2) c)", "169. § n)"],
        "hu-nav-26a60-2026-filing-guidance": ["26A60 03-as lap", "26A60 04-es lap", "26A60 version 3.0"],
    }
    primary = [x for x in source_ids if x not in {"de-bmf-ustae-current", "hu-nav-26a60-2026-filing-guidance"}]
    draft = {
        "sources_considered": [{"source_id": x} for x in source_ids],
        "primary_sources": primary, "court_sources": [],
        "official_guidance": ["de-bmf-ustae-current", "hu-nav-26a60-2026-filing-guidance"],
        "secondary_sources": [], "relevant_provisions": [],
        "facts_required": ["supplier establishment and fixed-establishment participation", "recipient taxable-person status and VAT identification", "actual service characteristics and special-rule screen", "German exemption classification and evidence", "supplier VAT status and Hungarian registration", "self-billing, invoice, tax-point and reporting-period facts"],
        "interpretation": "Research mapping only: UStG §3a(2) corresponds to the general B2B Article 44 destination rule; UStG §13b(1), read with (5)-(7), is the national German liability path for scoped cases. This does not establish transaction-specific liability, HU territorial charging, invoicing, or reporting.",
        "uncertainties": ["Paragraph-specific effective dates and amendments must be verified for the transaction date.", "No independent German/Hungarian tax-law review has occurred.", "GENERAL_SERVICE does not establish German non-exemption.", "Article 219a routing and Hungarian invoice implementation need complete review.", "EU recap and A60 taxpayer/period conditions remain unresolved.", "BMF UStAE exact current version and applicability require independent confirmation."],
        "conflicting_sources": [], "candidate_conclusion": "No operational tax conclusion; all new candidates blocked pending complete independent review.",
        "confidence_basis": ["Official statutory and administrative source pages accessed on 2026-10-08.", "Source access does not establish provision-specific effective date or applicability."],
        "exceptions_modeled": ["UStG §13b(6) express exclusions", "special-service and mixed-supply exclusions", "fixed-establishment participation uncertainty", "German exemption status unresolved"],
    }
    for sid, listed in provisions.items():
        for provision in listed:
            draft["relevant_provisions"].append({"source_id": sid, "provision": provision,
                "version_date": p.sources[sid].get("version_date"),
                "summary": "Official source text accessed; legal applicability and transaction-specific effect remain for review.",
                "applicability_notes": "Reference only; no automatic applicability conclusion.", "verified": True})
    request = {"research_question": "2026 Germany destination-state reverse-charge and linked Hungarian supplier VAT, invoicing, recap, and A60 foundation for a narrowly scoped synthetic B2B service.",
        "jurisdiction": ["HU", "EU", "DE"], "transaction_date": "2026-10-08", "as_of_date": "2026-10-08",
        "topics": ["place_of_supply", "reverse_charge", "invoicing", "eu_recap_reporting", "a60_reporting"],
        "facts": {"synthetic_only": True, "production_connections": False}}
    snapshot = p.create_research(request, draft)

    defs = [
        ("eu-article196-eligibility", "EU", "EU Article 196 eligibility screen", ["Article 44 place of supply in destination", "qualifying recipient status supported", "supplier not established in destination under Article 192a", "service within reviewed scope"], "EU Article 196 eligibility only; no destination-state implementation"),
        ("de-vat-b2b-cross-border-services-reverse-charge", "DE", "German §13b implementation for qualifying cross-border general services", ["Article 44 path in DE", "taxable person established", "supplier elsewhere in EU", "no participating relevant DE establishment", "DE taxable supply and exception screen complete"], "German destination reverse-charge liability only"),
        ("hu-supplier-vat-territorial-charging", "HU", "Hungarian territorial charging consequence for a DE place of supply", ["place of supply determined outside HU", "supply within Áfa tv. charging scope reviewed", "supplier/taxpayer facts complete"], "HU VAT territorial charging only; no rate"),
        ("eu-invoice-jurisdiction-219a", "EU", "Invoice-jurisdiction allocation under Article 219a", ["supplier establishment and intervention", "recipient liability", "self-billing status", "Article 219a exception route reviewed"], "Invoice jurisdiction only"),
        ("eu-invoice-metadata-general-b2b-rc", "EU", "Invoice metadata requirements under Directive Articles 222, 226 and 226a", ["invoice jurisdiction determined", "both VAT IDs and parties evidenced", "service and taxable amount facts", "invoice deadline inputs resolved"], "Metadata requirement model only; no rendered invoice"),
        ("hu-invoice-cross-border-service", "HU", "Hungarian invoice implementation for cross-border service", ["Article 219a routes invoicing to HU", "Hungarian issuer and invoice facts", "service date and tax point", "community VAT IDs and RC wording reviewed"], "Hungarian invoice implementation only"),
        ("eu-recap-article262-service", "EU", "EU recapitulative statement obligation under Article 262(1)(c)", ["qualifying recipient and VAT identification", "recipient liable under Article 196", "not exempt in destination", "supplier reporting facts and period"], "EU recap obligation only"),
        ("hu-a60-article262-implementation", "HU", "Hungarian A60 statutory and form implementation", ["EU recap obligation established", "Hungarian filing/registration status", "applicable annual 26A60 version", "period assessed separately"], "A60 obligation only; reporting period not assessed"),
    ]
    blocker = "BLOCKED: no independent qualified legal/tax reviewer has verified the complete law, effective dates, scope, exceptions, and taxpayer-specific applicability. Structural checks are not legal approval."
    root = ROOT / "rules" / "country-candidates" / "phase5.6"
    for slug, jurisdiction, scope, conditions, outcome in defs:
        evidence_ids = ["eu-vat-directive-2025-04-operational"]
        if jurisdiction == "DE": evidence_ids += ["de-ustg-2026-13b", "de-ustg-2026-3a", "de-ustg-2026-4"]
        elif jurisdiction == "HU": evidence_ids += ["hu-vat-act-njt-consolidation-2025-12-20", "hu-nav-26a60-2026-filing-guidance"]
        else: evidence_ids += ["de-ustg-2026-14-14a", "hu-vat-act-njt-consolidation-2025-12-20"]
        evidence=[]
        for sid in dict.fromkeys(evidence_ids):
            source=p.sources[sid]
            provision=next((x["provision"] for x in draft["relevant_provisions"] if x["source_id"]==sid), source["relevant_provisions"][0] if source["relevant_provisions"] else None)
            evidence.append({"source_id":sid,"provision":provision,"source_version":source.get("version_date") or "accessed-2026-10-08",
                "retrieved_at":"2026-10-08","supports":scope,"authority_level":source["authority_level"],"source_url":source["official_url"],"quote_or_extract":None,"content_hash":None})
        base={"candidate_id":"candidate-"+slug+"-phase5.6","rule_version_id":slug+"@1","jurisdiction":jurisdiction,
            "research_id":snapshot["research_id"],"research_hash":snapshot["snapshot_hash"],"scope":scope,"conditions":conditions,
            "outcome_scope":outcome,"evidence":evidence,"effective_from":None,"effective_to":None,
            "exceptions":["All special and mixed service categories excluded pending separately reviewed rules.","Unknown or conflicting facts require human review.","No implementation outside the stated stage."],
            "status":"BLOCKED","blockers":[blocker,"Provision-level effective dates are not fully verified for the target transaction date.","Candidate-specific exception analysis is incomplete." ]}
        base["candidate_hash"]=digest(base)
        p.validate(base,"country-rule-candidate.schema.json")
        candidate_path=root/"candidates"/(base["candidate_id"]+".json")
        candidate_existed=candidate_path.exists()
        write_immutable(candidate_path,base)
        if not candidate_existed:
            p.audit("CANDIDATE_CREATED","research-agent",base["candidate_id"],{"research_id":snapshot["research_id"],"candidate_hash":base["candidate_hash"]})
        checklist={k:"UNRESOLVED" for k in ["eu_national_mapping","scope","exceptions","effective_dates","establishment","customer_status","vat_id","destination_exemption","invoice_jurisdiction","reporting_dependencies","fact_completeness"]}
        review={"review_id":"country-review-"+digest([base["candidate_id"],base["candidate_hash"]])[:20],
            "candidate_id":base["candidate_id"],"candidate_hash":base["candidate_hash"],"research_id":snapshot["research_id"],
            "research_hash":snapshot["snapshot_hash"],"status":"BLOCKED","checklist":checklist,
            "findings":[blocker,*base["blockers"]],"reviewer_type":"structural-coding-agent-not-independent-legal-review","reviewed_at":"2026-10-08"}
        review["review_hash"]=digest(review)
        # Keep review_hash outside schema so write the review record with a declared hash property below.
        p.validate(review,"country-rule-review.schema.json")
        review_path=root/"reviews"/(review["review_id"]+".json")
        review_existed=review_path.exists()
        write_immutable(review_path,review)
        if not review_existed:
            p.audit("REVIEW_COMPLETED","structural-reviewer",base["candidate_id"],{"review_id":review["review_id"],"review_hash":review["review_hash"],"status":"BLOCKED"})
    print(f"Research snapshot: {snapshot['research_id']} ({snapshot['confidence']})")
    print(f"Phase 5.6 blocked candidate/review pairs: {len(defs)}")

if __name__ == "__main__": main()
