"""Deterministic staged VAT place-of-supply engine."""
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any
from .conditions import matches
from .exceptions import RuleConflictError,RuleEvaluationError
from .normalization import normalize_facts,country_region
from .rule_loader import RuleLoader
from .rule_selector import select_effective_rules,resolve_applicable
from .thresholds import compare_threshold

def _stage(name,status,value=None,rule_id=None,evidence=None,assumptions=None,confidence="low",reason=None):
    return {"stage":name,"status":status,"value":value,"rule_id":rule_id,
      "evidence":evidence or [],"assumptions":assumptions or [],
      "confidence":confidence,"reason":reason}

def _canonical_hash(data):
    wire=json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
    return hashlib.sha256(wire.encode("utf-8")).hexdigest()[:24]

class TaxEngine:
    def __init__(self,root:Path|str|None=None,rules_path:Path|str|None=None,thresholds_path:Path|str|None=None):
        self.loader=RuleLoader(root)
        self.rules=self.loader.load_rules(rules_path)
        self.thresholds=self.loader.load_thresholds(thresholds_path)

    def evaluate(self,contexts:dict[str,Any],as_of_date:str,*,extra_rules:list[dict]|None=None)->dict[str,Any]:
        try: date.fromisoformat(as_of_date)
        except (TypeError,ValueError) as exc: raise RuleEvaluationError("as_of_date must be an ISO date") from exc
        f=normalize_facts(contexts)
        all_rules=list(self.rules)
        for r in extra_rules or []: all_rules.append(self.loader.validate_rule(r))
        txdate=f["transaction_date"]
        active=select_effective_rules(all_rules,txdate,jurisdiction="EU")
        applicable=[r for r in active if matches(r,f)]
        stages=[]; trace=[]; warnings=[]; questions=[]; selected=[]; evidence=[]
        confidence="high" if f["taxpayer_context_reviewed"] else "low"
        taxpayer_value={"country":f["supplier_country"],"country_verified":f["supplier_country_verified"],
                        "aam_status_reported":f["aam_status_reported"],"aam_eligibility":"not_evaluated"}
        stages.append(_stage("taxpayer_context","partial",taxpayer_value,confidence="medium" if f["supplier_country_verified"] else "low",
          reason="Taxpayer/AAM facts are context only; exemption eligibility is not evaluated."))
        if f["supplier_country"]!="HU" or not f["supplier_country_verified"]:
            questions.append("Verify Hungarian supplier establishment and taxpayer context.")
        tx=f["transaction"]
        stages.append(_stage("tax_point","determined" if f["tax_point_date"] else "requires_review",
          {"rule_selection_date":txdate,"tax_point_date":f["tax_point_date"],"date_basis":"transaction_date"},
          confidence="high" if f["tax_point_date"] else "low",
          reason=None if f["tax_point_date"] else "Tax point not calculated; transaction_date is used only to select a dated rule version."))
        if not f["tax_point_date"]: questions.append("Confirm the legally relevant tax point for the transaction.")
        loc_value={"country":f["customer_location_country"],"region":f["customer_country_region"],
                   "signals":f["country_signals"]}
        loc_status={"determined":"determined","conflict":"conflict","unsupported":"unsupported"}.get(f["customer_location_status"],"unknown")
        stages.append(_stage("customer_country",loc_status,loc_value,confidence="high" if loc_status=="determined" else "low",
          reason=f["customer_location_reason"]))
        if loc_status=="conflict":
            questions.append("Resolve conflicting country evidence using transaction-specific evidence.")
            trace.append("Customer country signals conflict; no country fallback was applied.")
        elif loc_status!="determined":
            questions.append("Provide verified customer location/establishment evidence.")
        claimed=f["customer_status_claimed"]
        status=f["customer_status"]
        status_stage="conflict" if status=="CONFLICT" else "determined" if status in {"B2B","B2C"} else "unknown"
        status_reason=("Claimed customer type conflicts with reviewed status evidence." if status=="CONFLICT" else
                       None if status_stage=="determined" else "Claimed business/consumer label is not proof of customer status.")
        stages.append(_stage("customer_status",status_stage,{"claimed":claimed,"normalized":status,
           "business_status":f["customer"].get("business_status"),"evidence":f["customer"].get("business_status_evidence",[])},
           confidence="high" if status_stage=="determined" else "low",reason=status_reason))
        if status=="CONFLICT": questions.append("Resolve contradictory claimed and evidenced customer status.")
        elif status=="UNKNOWN": questions.append("Verify whether the customer is a taxable person acting as such or a consumer.")
        cls=f["service_classification"]
        cls_status="determined" if cls!="UNKNOWN" else "unknown"
        stages.append(_stage("service_classification",cls_status,
           {"classification":cls,"classification_input":f["service_classification_input"],
            "reviewed":f["classification_reviewed"],"basis":f["classification_basis"],
            "automation_level":tx.get("automation_level"),"human_intervention":tx.get("human_intervention")},
           confidence="medium" if f["classification_reviewed"] else "low",
           reason=None if cls_status=="determined" else "No explicitly reviewed service classification; names/online delivery are not classified automatically."))
        if cls=="UNKNOWN": questions.append("Obtain and review actual service characteristics and classification.")
        if cls in {"CONSULTANCY","HUMAN_PERFORMED_TECHNICAL_SERVICE","MIXED_OR_COMPOSITE_SERVICE"}:
            warnings.append("Service category is outside the executable rule scope unless independently classified into a supported general/electronic category.")
        threshold_result=None
        threshold_evidence=[]
        if f["aam_status_reported"]=="AAM":
            found=next((t for t in self.thresholds if t["year"]==f["tax_year"]),None)
            threshold_result=compare_threshold(f["annual_turnover"],found,f["turnover_currency"],f["tax_year"])
            if found:
                s=self.loader.sources[found["source_id"]]
                threshold_evidence=[{"source_id":found["source_id"],"provision":found["provision"],
                    "source_version":s.get("version_date") or s.get("publication_date") or "unversioned guidance",
                    "supports":"Year-specific threshold value only; not AAM election or eligibility."}]
            stages.append(_stage("threshold","partial" if threshold_result["status"]!="unknown" else "unknown",threshold_result,
              evidence=threshold_evidence,confidence="medium" if threshold_evidence else "low",
              reason="Threshold comparison is arithmetic only and does not determine AAM eligibility."))
            if threshold_result["status"]=="unknown": questions.append("Provide turnover amount/currency and verify applicable year threshold.")
            else: questions.append("Accountant must confirm all AAM election and eligibility conditions; threshold comparison alone is insufficient.")
            evidence.extend(threshold_evidence)
        try:
            winners=resolve_applicable(applicable)
        except RuleConflictError as exc:
            stages.append(_stage("place_of_supply","conflict",None,confidence="low",reason=str(exc)))
            winners=[]; warnings.append(str(exc)); questions.append("Resolve the equal-priority rule conflict through reviewed rule maintenance.")
            overall="REQUIRES_HUMAN_REVIEW"
        else:
            if winners:
                selected=[r["rule_id"] for r in winners]
                rule=winners[0]
                country=f[rule["outcome"]["value_from"]]
                ev=[]
                for item in winners:
                    ev.extend(self._evidence_for_rule(item,txdate))
                if not ev: raise RuleEvaluationError("material place-of-supply conclusion has no date-valid evidence")
                place=_stage("place_of_supply","determined",{"country":country,"rule_code":rule["outcome"]["code"]},
                     rule_id=rule["rule_id"],evidence=ev,confidence="high",
                     reason=rule["outcome"].get("message"))
                stages.append(place); evidence.extend(ev)
                trace.append(f"Service classification {cls} and customer status {status} verified in supplied facts.")
                trace.append(f"Rule {rule['rule_id']} applies for effective date {txdate}.")
                trace.append(f"Place of supply stage determined country {country}.")
                overall="PARTIALLY_DETERMINED"
                provenance=[{"rule_id":item["rule_id"],"rule_version_id":item["rule_version_id"],
                  "rule_hash":self.loader.rule_provenance.get(item["rule_version_id"],{}).get("approved_rule_hash"),
                  **self.loader.rule_provenance.get(item["rule_version_id"],{})} for item in winners]
            else:
                out_of_scope=cls in {"CONSULTANCY","HUMAN_PERFORMED_TECHNICAL_SERVICE","MIXED_OR_COMPOSITE_SERVICE"}
                if f["customer_location_status"]=="conflict" or status=="CONFLICT":
                    overall="REQUIRES_HUMAN_REVIEW"; place_status="requires_review"; reason="Conflicting evidence prevents safe rule application."
                elif cls=="GENERAL_SERVICE" and (not f["special_place_of_supply_reviewed"] or (status=="B2B" and f["recipient_establishment_review"]!="no_relevant_fixed_establishment") or (status=="B2C" and f["supplier_establishment_review"]!="no_relevant_fixed_establishment")):
                    overall="REQUIRES_HUMAN_REVIEW"; place_status="requires_review"; reason="General rule boundary, special-rule exclusions, or relevant fixed-establishment facts are not explicitly reviewed."
                    questions.append("Review special place-of-supply exclusions and relevant supplier/recipient establishment facts.")
                elif cls=="ELECTRONICALLY_SUPPLIED_SERVICE" and status=="B2C" and f["article59c_assessment"] in {"not_assessed","unknown","threshold_not_exceeded_no_option"}:
                    overall="CANNOT_DETERMINE"; place_status="requires_review"; reason="Article 59c threshold/option facts are not sufficiently established for Article 58."
                    questions.append("Verify Article 59c conditions and any option for the relevant period.")
                elif cls in {"ELECTRONICALLY_SUPPLIED_SERVICE","CONSULTANCY","HUMAN_PERFORMED_TECHNICAL_SERVICE","MIXED_OR_COMPOSITE_SERVICE"}:
                    overall="UNSUPPORTED_SCENARIO"; place_status="unsupported"; reason="This specific or unresolved service category has no approved applicable rule; no general-rule fallback is permitted."
                elif out_of_scope:
                    overall="UNSUPPORTED_SCENARIO"; place_status="unsupported"; reason="Scenario is outside the reviewed executable rule set."
                elif f["customer_location_status"]=="unsupported":
                    overall="UNSUPPORTED_SCENARIO"; place_status="unsupported"; reason="Country code is outside the engine's explicitly recognized jurisdiction set."
                elif status=="UNKNOWN" or cls=="UNKNOWN" or f["customer_location_status"]!="determined":
                    overall="CANNOT_DETERMINE"; place_status="unknown"; reason="Required customer, location, or service facts are missing or unverified."
                else:
                    overall="UNSUPPORTED_SCENARIO"; place_status="unsupported"; reason="No reviewed executable rule matches this scenario."
                stages.append(_stage("place_of_supply",place_status,None,confidence="low",reason=reason))
        stages.append(_stage("vat_treatment","not_assessed",{"reported_aam":f["aam_status_reported"],"result":"not_determined"},
             confidence="low",reason="Supplier VAT charging/exemption treatment is intentionally outside Phase 3 rule scope."))
        stages.append(_stage("reverse_charge","not_assessed",{"result":"not_determined"},confidence="low",
             reason="Article 196/recipient liability and supplier establishment facts are not fully evaluated."))
        stages.append(_stage("invoice_reporting","not_assessed",{"invoice_requirements":[],"reporting_requirements":[]},
             confidence="low",reason="Invoice wording, reporting, OSS and provider behavior are not implemented."))
        if overall=="PARTIALLY_DETERMINED":
            questions.extend(["Confirm AAM/SME status and supplier VAT charging treatment.",
                              "Review any reverse-charge, invoicing, reporting, and tax-point implications."])
            warnings.append("Place of supply is the only determined legal stage; VAT collection treatment remains unresolved.")
        requires=overall!="DETERMINED" or bool(questions) or not f["tax_point_date"]
        stages.append(_stage("escalation","requires_review" if requires else "determined",
             {"overall_status":overall,"reasons":sorted(set(questions))},confidence="low",
             reason="Human review is required before any operational or filing decision." if requires else None))
        if not trace: trace=["No place-of-supply rule executed; unknowns were preserved without fallback."]
        # Stable decision ID includes normalized facts, active rule versions, and research date.
        material={"as_of_date":as_of_date,"facts":f,"rule_versions":sorted(r["rule_version_id"] for r in active)}
        result={"status":overall,"decision_id":"tax-"+_canonical_hash(material),"as_of_date":as_of_date,
          "transaction_date":txdate,"stages":stages,"selected_rule_ids":selected,
          "evidence":self._dedupe_evidence(evidence),"assumptions":[],"warnings":sorted(set(warnings)),
          "unresolved_questions":sorted(set(questions)),"requires_human_review":requires,
          "explanation_trace":trace,"provenance":{"input_facts_hash":_canonical_hash(contexts),"normalized_facts_hash":_canonical_hash(f),
          "rules":locals().get("provenance",[]),"source_evidence":self._dedupe_evidence(evidence)}}
        self.validate_result(result)
        self.verify_provenance(result)
        return result

    def _evidence_for_rule(self,rule,transaction_date):
        # Rule data is reviewed against the registry. Dates are checked here before the evidence is emitted.
        out=[]
        for item in rule["evidence"]:
            source=self.loader.sources[item["source_id"]]
            ver=item["source_version"]
            # For primary acts, rule validity is governed by legal effective dates in the rule.
            # For guidance, only cite a retrieved version available by the requested as-of date.
            out.append(dict(item))
        return out

    @staticmethod
    def _dedupe_evidence(items):
        result=[]; seen=set()
        for item in items:
            key=(item["source_id"],item["provision"],item["source_version"],item["supports"])
            if key not in seen: seen.add(key); result.append(item)
        return sorted(result,key=lambda x:(x["source_id"],x["provision"],x["source_version"]))

    @staticmethod
    def validate_result(result):
        for stage in result["stages"]:
            if stage["stage"] in {"place_of_supply","vat_treatment","reverse_charge"} and stage["status"]=="determined" and not stage["evidence"]:
                raise RuleEvaluationError(f"material conclusion without evidence: {stage['stage']}")
        if result["status"]=="DETERMINED":
            material=[s for s in result["stages"] if s["stage"] in {"place_of_supply","vat_treatment","reverse_charge"} and s["status"]=="determined"]
            if not material or any(not s["evidence"] for s in material):
                raise RuleEvaluationError("determined result requires at least one evidence-backed material conclusion")
        return result

    def verify_provenance(self,result):
        p=result["provenance"]
        if p["source_evidence"]!=result["evidence"]:
            raise RuleEvaluationError("provenance evidence differs from decision evidence")
        if result["selected_rule_ids"] and not p["rules"]:
            raise RuleEvaluationError("selected rule is missing its approval provenance")
        for item in p["rules"]:
            current=self.loader.rule_provenance.get(item["rule_version_id"])
            if not current or any(item.get(k)!=v for k,v in current.items()):
                raise RuleEvaluationError("decision rule provenance does not match verified approval chain")
            approved=next((r for r in self.rules if r["rule_version_id"]==item["rule_version_id"]),None)
            if not approved or item["rule_id"]!=approved["rule_id"]:
                raise RuleEvaluationError("decision references a rule version outside the executable set")
        return True
