"""Deterministic fact normalization; claims are not legal conclusions."""
from copy import deepcopy
from .exceptions import RuleEvaluationError

EU_COUNTRIES={"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE"}
KNOWN_NON_EU={"US","GB","CA","AU","NZ","CH","NO","IS","JP","SG","TR","UA","RS","BR","MX","IN","CN","KR","ZA"}
SERVICE_CLASSES={"GENERAL_SERVICE","ELECTRONICALLY_SUPPLIED_SERVICE","CONSULTANCY","HUMAN_PERFORMED_TECHNICAL_SERVICE","MIXED_OR_COMPOSITE_SERVICE","UNKNOWN"}

def country_region(code):
    if not code: return "UNKNOWN"
    if code in EU_COUNTRIES: return "EU"
    if code in KNOWN_NON_EU: return "NON_EU"
    return "UNSUPPORTED"

def normalize_facts(contexts):
    if not isinstance(contexts,dict): raise RuleEvaluationError("input must be an object")
    taxpayer=deepcopy(contexts.get("taxpayer") or {})
    customer=deepcopy(contexts.get("customer") or {})
    transaction=deepcopy(contexts.get("transaction") or {})
    supplier=taxpayer.get("establishment_country") or taxpayer.get("country")
    supplier_ok=bool(supplier and taxpayer.get("country")==supplier and taxpayer.get("facts_reviewed") is True)
    claim=customer.get("customer_type_claimed","unknown")
    business_state=customer.get("business_status","unknown")
    proof=customer.get("business_status_evidence",[])
    reviewed=customer.get("status_evidence_reviewed") is True
    capacity_reviewed=customer.get("taxable_person_capacity_reviewed") is True
    if business_state=="verified_business" and claim=="business" and proof and reviewed and capacity_reviewed and customer.get("taxable_person_acting_as_such") is True:
        status="B2B"
    elif business_state=="verified_non_business" and claim=="consumer" and "consumer_declaration" in proof and reviewed:
        status="B2C"
    elif (business_state=="verified_business" and claim=="consumer") or (business_state=="verified_non_business" and claim=="business"):
        status="CONFLICT"
    else:
        status="UNKNOWN"
    signals=customer.get("evidence_country_signals",[])
    signal_countries={s.get("country") for s in signals if s.get("country")}
    if status=="B2B":
        candidate=customer.get("business_establishment_country")
        supported=any(s.get("kind") in {"business_establishment","registry"} and s.get("country")==candidate for s in signals)
        if not candidate:
            candidate=next((s.get("country") for s in signals if s.get("kind") in {"business_establishment","registry"}),None)
        claimed=customer.get("country")
    else:
        candidate=customer.get("country")
        if not candidate and len(signal_countries)==1: candidate=next(iter(signal_countries))
        supported=bool(signals)
        claimed=customer.get("country")
    all_locations=set(signal_countries)
    if claimed: all_locations.add(claimed)
    if candidate: all_locations.add(candidate)
    if len(all_locations)>1:
        location_status="conflict"
        location_reason="CONFLICTING_CUSTOMER_LOCATION_EVIDENCE"
    elif not candidate or not supported:
        location_status="unknown"
        location_reason="MISSING_OR_UNSUPPORTED_CUSTOMER_LOCATION_EVIDENCE"
    else:
        region=country_region(candidate)
        if region=="UNSUPPORTED":
            location_status="unsupported"; location_reason="UNSUPPORTED_COUNTRY_CODE"
        else:
            location_status="determined"; location_reason=None
    raw_class=transaction.get("service_classification","UNKNOWN")
    classification=raw_class if raw_class in SERVICE_CLASSES else "UNKNOWN"
    class_reviewed=(transaction.get("classification_reviewed") is True and
                    bool(transaction.get("classification_basis")) and classification!="UNKNOWN")
    normalized={
      "supplier_country":supplier,"supplier_country_verified":supplier_ok,
      "taxpayer_context_reviewed":taxpayer.get("facts_reviewed") is True,
      "aam_status_reported":taxpayer.get("vat_status_reported","unknown"),
      "tax_year":taxpayer.get("tax_year"),"annual_turnover":taxpayer.get("annual_turnover"),
      "turnover_currency":taxpayer.get("turnover_currency"),
      "customer_status":status,"customer_status_claimed":claim,
      "customer_capacity_reviewed":capacity_reviewed,
      "customer_location_status":location_status,"customer_location_reason":location_reason,
      "customer_location_country":candidate,"customer_country_region":country_region(candidate),
      "customer_establishment_country":candidate if status=="B2B" and location_status=="determined" else None,
      "country_signals":signals,
      "service_classification":classification if class_reviewed else "UNKNOWN",
      "service_classification_input":raw_class,"classification_reviewed":class_reviewed,
      "classification_basis":transaction.get("classification_basis",[]),
      "special_place_of_supply_reviewed":transaction.get("special_place_of_supply_reviewed") is True,
      "supplier_establishment_review":transaction.get("supplier_establishment_review","unreviewed"),
      "recipient_establishment_review":transaction.get("recipient_establishment_review","unreviewed"),
      "article59c_assessment":transaction.get("article59c_assessment","not_assessed"),
      "transaction_date":transaction.get("transaction_date"),
      "tax_point_date":transaction.get("tax_point_date"),
      "currency":transaction.get("currency"),"amount":transaction.get("amount"),
      "transaction":transaction,"taxpayer":taxpayer,"customer":customer
    }
    if normalized["transaction_date"] is None: raise RuleEvaluationError("transaction_date is required")
    return normalized
