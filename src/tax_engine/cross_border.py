"""Non-operative EU Article 196 screening and destination-pack boundary.

The screen reports whether the supplied facts appear to meet the EU-level
Article 196 elements. It does not determine national VAT liability. National
implementation is never executable unless an approved country rule is supplied.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import date

EU_196_SOURCE = "eu-vat-directive-2025-04-operational"
EU_196_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02006L0112-20250414"
EU_MEMBER_STATES = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"}


def _stage(name, status, value, rule_id, evidence, dependencies, reason):
    return {"stage": name, "status": status, "value": value, "rule_id": rule_id,
            "evidence": evidence, "dependencies": dependencies, "reason": reason}


def screen_article196(facts: dict) -> dict:
    """Return a scoped EU-condition screen; never a reverse-charge conclusion."""
    pos = facts["place_of_supply"]
    service = facts["service_classification"]
    customer = facts["customer_taxable_person_status"]
    supplier = facts["supplier_destination_establishment"]
    ev = []
    if supplier["country"] != facts["customer_country"]:
        return {"status": "requires_review", "value": "CANNOT_DETERMINE", "evidence": [],
                "reason": "Supplier establishment facts are not tied to the determined destination country."}
    if pos["status"] == "DETERMINED" and pos["country"] == facts["customer_country"] and pos["rule_version_id"] == "eu-vat-services-b2b-general@1":
        ev.extend(deepcopy(pos["evidence"]))
    else:
        result = {"status": "requires_review", "value": "CANNOT_DETERMINE", "evidence": [],
                  "reason": "A supported Article 44 place-of-supply path to the destination is required."}
        return result
    if facts["customer_country"] != pos["country"]:
        return {"status": "requires_review", "value": "CANNOT_DETERMINE", "evidence": ev,
                "reason": "Customer country conflicts with the upstream Article 44 destination; do not resolve location evidence by guessing."}
    if not any(e["source_id"] == EU_196_SOURCE and e["provision"] == "Article 196" for e in ev):
        ev.append({"source_id": EU_196_SOURCE, "provision": "Article 196", "source_version": "2025-04-14", "retrieved_at": "2026-10-08",
                   "supports": "EU-level conditions for recipient liability; does not establish destination-state implementation.", "authority_level": "primary", "source_url": EU_196_URL, "quote_or_extract": None, "content_hash": None})
    if not any(e["source_id"] == EU_196_SOURCE and e["provision"] == "Article 192a" for e in ev):
        ev.append({"source_id": EU_196_SOURCE, "provision": "Article 192a", "source_version": "2025-04-14", "retrieved_at": "2026-10-08",
                   "supports": "Relevant fixed-establishment non-intervention boundary for whether supplier is regarded as not established in the taxing Member State.", "authority_level": "primary", "source_url": EU_196_URL, "quote_or_extract": None, "content_hash": None})
    if service not in {"GENERAL_SERVICE", "STANDARD_TAXABLE_GENERAL_TECHNICAL_SERVICE"} or facts["special_rule_screened"] != "YES_NO_SPECIAL_RULE":
        return {"status": "unsupported", "value": "REQUIRES_CLASSIFICATION_OR_SPECIAL_RULE_REVIEW", "evidence": ev,
                "reason": "The shared Phase 5.6 screen is limited to a reviewed general-service Article 44 path with explicit special-rule screening."}
    if customer in {"UNKNOWN", "CONFLICTING"}:
        return {"status": "requires_review", "value": "CANNOT_DETERMINE", "evidence": ev,
                "reason": "Claimed business status and VAT-ID evidence cannot replace an established recipient status."}
    if customer == "NOT_TAXABLE_PERSON":
        return {"status": "determined", "value": "NOT_ELIGIBLE", "evidence": ev,
                "reason": "The supplied reviewed customer status does not meet an Article 196 recipient category."}
    if customer == "NON_TAXABLE_LEGAL_PERSON_VAT_IDENTIFIED":
        vat_id = facts["customer_vat_id"]
        if vat_id["country"] != facts["customer_country"] or not vat_id["present"] or vat_id["verification"] != "SYNTHETIC_VALID":
            return {"status": "requires_review", "value": "CANNOT_DETERMINE", "evidence": ev,
                    "reason": "A non-taxable legal person requires supported VAT identification for this Article 196 recipient path."}
    if facts["supplier_country"] not in EU_MEMBER_STATES:
        return {"status": "determined", "value": "NOT_ELIGIBLE", "evidence": ev,
                "reason": "The supplier is not established in an EU Member State for this Article 196 screen."}
    if facts["supplier_taxable_person"] == "NO":
        return {"status": "determined", "value": "NOT_ELIGIBLE", "evidence": ev,
                "reason": "The supplied facts do not establish a taxable-person supplier."}
    if facts["supplier_taxable_person"] == "UNKNOWN":
        return {"status": "requires_review", "value": "CANNOT_DETERMINE", "evidence": ev,
                "reason": "Supplier taxable-person status is unresolved."}
    if supplier["state"] == "UNKNOWN" or (supplier["state"] == "EXISTS" and supplier["intervenes_in_supply"] == "UNKNOWN"):
        return {"status": "requires_review", "value": "CANNOT_DETERMINE", "evidence": ev,
                "reason": "German establishment/intervention is unresolved and may be material under Article 192a."}
    if supplier["state"] == "EXISTS" and supplier["intervenes_in_supply"] == "YES":
        return {"status": "determined", "value": "NOT_ELIGIBLE", "evidence": ev,
                "reason": "The supplied facts indicate a relevant German supplier establishment intervenes; the EU non-established-supplier element is not met on this screen."}
    return {"status": "determined", "value": "ELIGIBLE", "evidence": ev,
            "reason": "EU-level Article 196 elements screen as supported by supplied facts. This is not a destination-state liability determination."}


def evaluate_destination(country: str, eligibility: dict, facts: dict, implementation_packs: dict) -> dict:
    """Fail closed for absent/unapproved country packs and unresolved conditions."""
    if country != "DE":
        return {"status": "unsupported", "value": "UNSUPPORTED_DESTINATION_IMPLEMENTATION", "rule_id": None,
                "evidence": [], "reason": "Phase 5.6 implements no destination-state operational handler outside Germany."}
    pack = implementation_packs.get(country)
    if pack is None:
        return {"status": "unsupported", "value": "UNSUPPORTED_DESTINATION_IMPLEMENTATION", "rule_id": None,
                "evidence": [], "reason": f"No {country} implementation pack is registered."}
    if eligibility.get("value") != "ELIGIBLE":
        return {"status": "not_assessed", "value": "ARTICLE_196_PREREQUISITES_UNRESOLVED", "rule_id": None,
                "evidence": [], "reason": "Destination assessment depends on a supported EU-level Article 196 screen."}
    if (pack.get("status") != "EXECUTABLE" or not pack.get("approved_rule_version_id")
            or pack.get("approval_chain_verified") is not True or not pack.get("effective_from")):
        return {"status": "not_assessed", "value": "DESTINATION_RULE_NOT_APPROVED", "rule_id": None,
                "evidence": [], "reason": "A verified immutable human-approval chain and effective date are required from the trusted country-pack loader."}
    try:
        transaction_date = date.fromisoformat(facts["transaction_date"])
        effective_from = date.fromisoformat(pack["effective_from"])
        effective_to = date.fromisoformat(pack["effective_to"]) if pack.get("effective_to") else None
    except (KeyError, TypeError, ValueError):
        return {"status": "requires_review", "value": "CANNOT_DETERMINE", "rule_id": pack["approved_rule_version_id"],
                "evidence": [], "reason": "Transaction or approved-rule effective dates are missing or malformed."}
    if transaction_date < effective_from or (effective_to and transaction_date >= effective_to):
        return {"status": "not_assessed", "value": "RULE_NOT_EFFECTIVE_FOR_TRANSACTION_DATE", "rule_id": pack["approved_rule_version_id"],
                "evidence": [], "reason": "No effective approved destination rule covers this transaction date."}
    condition = check_destination_conditions(country, facts)
    if condition["status"] != "determined":
        return {**condition, "rule_id": pack["approved_rule_version_id"], "evidence": []}
    return {"status": "determined", "value": "APPLIES", "rule_id": pack["approved_rule_version_id"],
            "evidence": deepcopy(pack.get("evidence", [])),
            "reason": "Approved destination-specific rule and its explicit conditions are satisfied."}


def check_destination_conditions(country: str, facts: dict) -> dict:
    """Check DE-specific factual gates without approving or executing a rule."""
    supplier = facts["supplier_destination_establishment"]
    if supplier["country"] != country:
        return {"status": "requires_review", "value": "CANNOT_DETERMINE",
                "reason": "Supplier establishment facts do not match the destination pack country."}
    if supplier["state"] == "UNKNOWN" or (supplier["state"] == "EXISTS" and supplier["intervenes_in_supply"] == "UNKNOWN"):
        return {"status": "requires_review", "value": "CANNOT_DETERMINE",
                "reason": "Destination fixed-establishment intervention is unresolved."}
    if facts["destination_taxability_status"] != "REVIEWED_TAXABLE_NO_EXEMPTION_IDENTIFIED":
        return {"status": "requires_review", "value": "DESTINATION_TAXABILITY_UNRESOLVED",
                "reason": "A reviewed narrow taxable-service classification is required; a generic service label cannot establish German exemption status."}
    return {"status": "determined", "value": "PRECONDITIONS_MET",
            "reason": "Destination factual gates pass; this is not a reverse-charge conclusion."}


def assess_cross_border(facts: dict, as_of_date: str, packs: dict | None = None) -> dict:
    """Build stage records. Downstream stages stay not_assessed until approved rules exist."""
    eligibility = screen_article196(facts)
    eligibility_status = "determined" if eligibility["status"] == "determined" else eligibility["status"]
    eligibility_ev = eligibility["evidence"]
    dest = evaluate_destination(facts["customer_country"], eligibility, facts, packs or {})
    stages = [
        _stage("article_196_eligibility", eligibility_status, eligibility["value"], None, eligibility_ev,
               ["place_of_supply", "customer_taxable_person_status", "supplier_destination_establishment", "service_classification", "special_rule_screened"], eligibility["reason"]),
        _stage("destination_reverse_charge", dest["status"], dest["value"], dest["rule_id"], dest["evidence"],
               ["article_196_eligibility", "destination_implementation_pack", "supplier_destination_establishment", "destination_taxability_status"], dest["reason"]),
    ]
    downstream = [
        ("supplier_vat_charging", ["place_of_supply", "hungarian_territorial_scope_rule"], "HU territorial VAT candidate is blocked; reverse charge is not a substitute for the territorial-scope test."),
        ("invoice_jurisdiction", ["article_219a", "destination_reverse_charge", "supplier_establishment", "self_billing"], "Article 219a route and national invoice implementation candidate are not approved."),
        ("invoice_metadata", ["invoice_jurisdiction", "article_226", "article_222", "hungarian_invoice_law"], "No invoice fields or final wording are generated before invoice jurisdiction and national requirements are approved."),
        ("eu_recap_reporting", ["destination_reverse_charge", "customer_vat_id", "german_exemption_status", "article_262"], "Article 44 alone does not determine EU recapitulative reporting."),
        ("a60_reporting", ["eu_recap_reporting", "hungarian_registration", "a60_statutory_and_form_scope"], "Hungarian filing implementation remains distinct from the EU recap obligation."),
        ("aam_effect", ["taxpayer_aam_status", "hungarian_cross_border_aam_rule"], "AAM effect is isolated and not inferred."),
        ("tax_point", ["chargeable_event_facts", "tax_point_rules"], "Tax point was not assessed."),
    ]
    for name, deps, reason in downstream:
        stages.append(_stage(name, "not_assessed", "NOT_ASSESSED", None, [], deps, reason))
    asks = [s["reason"] for s in stages if s["status"] in {"requires_review", "unsupported", "not_assessed"}]
    return {"assessment_id": "cross-border-screen", "as_of_date": as_of_date, "transaction_date": facts.get("transaction_date", as_of_date),
            "facts": deepcopy(facts), "stages": stages, "requires_human_review": True,
            "unresolved_questions": asks}
