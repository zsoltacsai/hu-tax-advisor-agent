"""Write deterministic, synthetic fact fixtures; never uses external systems."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fixtures" / "scenarios"
OUT.mkdir(parents=True, exist_ok=True)

def make(sid, description, country="HU", customer_type="consumer", vat_state="not_checked",
         billing="HU", currency="HUF", date="2026-10-08", frequency="monthly",
         events=None, signals=None, service="Synthetic WordPress maintenance; delivery details unspecified.",
         amount=10000, turnover=None):
    if signals is None:
        signals = [{"kind":"billing","country":billing,"observed_at":"2026-10-08T10:00:00Z"}] if billing else []
    obj = {
      "scenario_id":sid, "description":description,
      "taxpayer":{"country":"HU","entity_type":"sole_proprietor","vat_status_reported":"AAM","facts_reviewed":False,
        "eu_vat_number_present":True,"establishment_country":"HU","tax_year":2026,
        "facts_as_of":"2026-10-08","facts_reviewed":False,"annual_turnover":turnover,"turnover_currency":"HUF",
        "source_fact_ids":["synthetic-taxpayer-facts"]},
      "customer":{"country":country,"business_establishment_country":None,"customer_type_claimed":customer_type,
        "business_status":"unverified","business_status_evidence":[],"status_evidence_reviewed":False,"vat_id":None,
        "vat_id_verification":vat_state,"verification_at":None,"evidence_country_signals":signals},
      "transaction":{"service_as_described":service,"service_classification":"unclassified",
        "classification_basis":[],"classification_reviewed":False,"special_place_of_supply_reviewed":False,
        "automation_level":"unknown","human_intervention":"unknown","article59c_assessment":"not_assessed",
        "billing_frequency":frequency,"currency":currency,"price_basis":"unknown",
        "transaction_date":date,"tax_point_date":None,"payment_provider":"synthetic-no-connection",
        "amount":amount,"events":events or []},
      "expected_validation":{"expected_escalation":True,
        "uncertainty_categories":["MISSING_FACT","LEGAL_INTERPRETATION","HUMAN_ACCOUNTANT_DECISION"],
        "notes":"Synthetic facts only. No tax treatment or legal conclusion asserted."}
    }
    return obj

def ev(kind,date,amount=None,details="Synthetic event; no legal implication asserted."):
    return {"type":kind,"date":date,"amount":amount,"details":details}

rows=[
 make("01-hu-b2c","Synthetic Hungarian consumer."),
 make("02-hu-b2b","Synthetic Hungarian business; no buyer VAT ID supplied.",customer_type="business"),
 make("03-eu-b2b-synthetic-valid","Synthetic EU business with synthetic-valid VAT status; not a real identifier.",
      country="DE",customer_type="business",vat_state="synthetic_valid",billing="DE",currency="EUR",
      signals=[{"kind":"billing","country":"DE","observed_at":"2026-10-08T10:00:00Z"},{"kind":"registry","country":"DE","observed_at":"2026-10-08T10:05:00Z"}]),
 make("04-eu-b2b-invalid-unverified","Synthetic EU business claim; invalid test state, no live lookup.",
      country="FR",customer_type="business",vat_state="synthetic_invalid",billing="FR",currency="EUR"),
 make("05-eu-b2c","Synthetic EU consumer.",country="AT",billing="AT",currency="EUR"),
 make("06-non-eu-b2b","Synthetic non-EU business; separate jurisdiction analysis required.",
      country="US",customer_type="business",billing="US",currency="USD"),
 make("07-non-eu-b2c","Synthetic non-EU consumer.",country="GB",billing="GB",currency="GBP"),
 make("08-refund","Synthetic full refund; original supply facts absent.",
      events=[ev("refund","2026-10-08",10000,"Original supply treatment unspecified.")]),
 make("09-partial-refund","Synthetic partial refund.",
      events=[ev("partial_refund","2026-10-08",2500,"Original supply treatment unspecified.")]),
 make("10-annual-prepaid-subscription","Synthetic prepaid annual subscription; tax point unresolved.",
      country="DE",billing="DE",currency="EUR",frequency="annual",date="2026-11-15",amount=120000,
      events=[ev("purchase","2026-11-15",120000,"Service period 2026-11-15 through 2027-11-14."),
              ev("payment","2026-11-15",120000,"Synthetic advance payment.")]),
 make("11-recurring-monthly-subscription","Synthetic monthly subscription with renewal.",
      events=[ev("purchase","2026-10-01",10000,"Initial month."),
              ev("renewal","2026-11-01",10000,"Renewal.")]),
 make("12-discount-promotion","Synthetic promotion; price/funding structure unknown.",
      events=[ev("discount","2026-10-08",5000,"Discount basis not classified.")]),
 make("13-vat-status-changes-after-purchase","Synthetic VAT status change after purchase; direction/evidence unknown.",
      country="DE",customer_type="business",vat_state="unknown",billing="DE",currency="EUR",
      events=[ev("purchase","2026-10-01",10000,"Purchase precedes reported later change."),
              ev("status_change","2026-10-20",None,"Direction and official evidence unspecified.")]),
 make("14-transaction-near-year-boundary","Synthetic supply/payment split across calendar-year boundary.",
      date="2026-12-31",events=[ev("payment","2027-01-01",10000,"Payment date differs from transaction date.")]),
 make("15-taxpayer-near-aam-threshold","Synthetic turnover near a threshold; value is test input, not legal conclusion.",
      turnover=19950000,amount=100000),
 make("16-missing-customer-country-evidence","Customer country not established.",country=None,billing=None,signals=[]),
 make("17-conflicting-country-evidence","Synthetic billing/IP/payment signals conflict; do not infer location.",
      country=None,billing=None,signals=[
       {"kind":"billing","country":"DE","observed_at":"2026-10-08T10:00:00Z"},
       {"kind":"ip","country":"HU","observed_at":"2026-10-08T10:01:00Z"},
       {"kind":"payment","country":"AT","observed_at":"2026-10-08T10:02:00Z"}])
]
rows[-1]["expected_validation"]={
 "expected_escalation":True,"uncertainty_categories":["CONFLICTING_SOURCES","MISSING_FACT","HUMAN_ACCOUNTANT_DECISION"],
 "notes":"Country signals conflict. No customer location or tax treatment is asserted."
}
for row in rows:
    (OUT/f'{row["scenario_id"]}.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"Wrote {len(rows)} synthetic scenarios to {OUT}")
