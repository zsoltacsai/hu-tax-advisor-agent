"""Create frozen, source-linked Phase 4 research examples and non-executable candidates."""
import json
from pathlib import Path
from datetime import datetime,timezone
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.research_pipeline.workflow import ResearchPipeline,ResearchAgent,ReviewerAgent
pipe=ResearchPipeline(ROOT); agent=ResearchAgent(pipe); reviewer=ReviewerAgent(pipe)
DATE="2026-10-08"; STAMP="2026-10-08T10:00:00+00:00"
S={x["id"]:x for x in pipe.source_registry["sources"]}

def source_row(sid):
    return {"source_id":sid}

def research_case(slug,question,source_ids,provisions,required,interpretation,uncertainties,primary,guidance):
    request={"research_question":question,"jurisdiction":["EU","HU"],"transaction_date":DATE,"as_of_date":DATE,"topics":["vat",slug],"facts":{"case":"synthetic research scope; not a taxpayer case"}}
    provision_rows=[]
    for sid,prov,summary,art in provisions:
        src=S[sid]
        provision_rows.append({"source_id":sid,"provision":prov,"article":art,"paragraph":None,
          "version_date":src.get("version_date"),"summary":summary,
          "applicability_notes":"Identifies relevant text only; issue-specific application remains subject to review.",
          "verified":bool(src.get("content_verified"))})
    draft={"as_of_date":DATE,"sources_considered":[source_row(x) for x in source_ids],
      "primary_sources":primary,"official_guidance":guidance,"secondary_sources":[],
      "relevant_provisions":provision_rows,"facts_required":required,"interpretation":interpretation,
      "uncertainties":uncertainties,"conflicting_sources":[],"candidate_conclusion":interpretation,
      "confidence":"high","confidence_basis":["Confidence is recomputed from frozen source and provision metadata; submitted rating is ignored."]}
    snap=agent.submit(request,draft)
    return snap

eu="eu-vat-directive-current-consolidation-2025-04-14"; act="eu-vat-services-directive-2008-8"; art58="eu-vat-ecommerce-directive-2017-2455"; ec="eu-commission-place-of-taxation"; aam="hu-nav-aam-2026-guidance"
cases={}
cases["article44-general-b2b"]=research_case("article44-general-b2b","What is the general place-of-supply rule for B2B services?",[act,eu,ec],
 [(act,"Article 2; effective 2010-01-01, introducing Directive 2006/112/EC Article 44","Directive amendment and stated application date", "44"),(eu,"Article 44","General B2B service place-of-supply provision","44"),(ec,"Commission summary of Directive Article 44","Commission summary of the general B2B rule","44")],
 ["customer taxable-person status and acting-as-such evidence","customer establishment/fixed establishment receiving the service","service category","special place rules"],
 "Article 44 is the general B2B service rule subject to exceptions and recipient establishment analysis.",
 ["Customer status and receiving establishment require facts; exceptions are outside this research scope."],[act,eu],[ec])
cases["article45-general-b2c"]=research_case("article45-general-b2c","What is the general place-of-supply rule for B2C services?",[act,eu,ec],
 [(act,"Article 2; effective 2010-01-01, introducing Directive 2006/112/EC Article 45","Directive amendment and stated application date", "45"),(eu,"Article 45","General B2C service place-of-supply provision","45"),(ec,"Commission summary of Directive Article 45","Commission summary of the general B2C rule","45")],
 ["customer non-taxable-person status","supplier establishment","service category","special place rules"],
 "Article 45 is the general B2C service rule subject to exceptions.",
 ["Special place rules may displace the general rule; exact service characteristics are necessary."],[act,eu],[ec])
cases["article58-electronic-b2c"]=research_case("article58-electronic-b2c","When does the destination rule apply to B2C electronically supplied services?",[art58,eu,ec],
 [(art58,"Article 1, effective 2019-01-01; Directive 2006/112/EC Article 58(1)-(2)","Amendment and effective date for Article 58","58"),(eu,"Article 58","Consolidated electronic services place-of-supply text","58"),(eu,"Article 58; Article 59c","Consolidated electronic services rule and exception text","58"),(ec,"Commission summary of Directive Article 58 and 59c","Commission description of the B2C electronic-services rule","58")],
 ["service meets the legal electronically supplied service definition","customer is non-taxable and location is evidenced","Article 59c conditions and any option","special exceptions"],
 "Article 58 is a special B2C electronic-services rule; classification and Article 59c must be separately reviewed.",
 ["No conclusion that any particular maintenance/SaaS service is electronically supplied."],[art58,eu],[ec])
cases["article59c-gating"]=research_case("article59c-gating","What low-value exception/option must be assessed before applying Article 58?",[art58,eu,ec],
 [(art58,"Article 1 and Directive 2006/112/EC Article 59c","Amendment establishing the limited exception framework","59c"),(eu,"Article 59c","Consolidated exception/option text","59c"),(ec,"Article 59c","Official guidance summary of low-value framework","59c")],
 ["supplier establishment","EU turnover and applicable threshold period","customer location","whether option was exercised"],
 "Article 59c can affect the Article 58 destination rule; threshold and option inputs need their own legal assessment.",
 ["No threshold amount or eligibility conclusion is made for a real taxpayer."],[art58,eu],[ec])
cases["hungary-2026-aam-threshold"]=research_case("hungary-2026-aam-threshold","What annual domestic AAM threshold does NAV describe for 2026?",[aam],
 [(aam,"NAV 2026 annual threshold guidance; Áfa tv. 188. § (2) reference","NAV reports HUF 20 million 2026 ceiling; conditions and transition rules apply",None)],
 ["correct qualifying turnover base","prior and current-year actual/expected turnover","election and transitional eligibility","cross-border SME status"],
 "NAV guidance reports a HUF 20 million 2026 domestic threshold; this is not an eligibility conclusion.",
 ["Underlying Act was not verified in this repository","AAM election, calculation base, transitions and SME scheme need separate review"],[],[aam])
cases["wp-caregrid-classification-unresolved"]=research_case("wp-caregrid-classification-unresolved","What facts are needed to classify a WordPress maintenance subscription for VAT place-of-supply analysis?",[eu,ec],
 [(eu,"Article 44","General B2B service rule; classification still required","44"),(eu,"Article 45","General B2C service rule; classification still required","45"),(eu,"Article 58","Special B2C electronic-services rule; classification still required","58"),(ec,"Article 44","Commission says service nature and customer status are needed","44"),(ec,"Article 45","Commission says service nature and customer status are needed","45"),(ec,"Article 58","Commission says service nature and customer status are needed","58")],
 ["automation and human work","maintenance/update/backup/security/support tasks","frequency and customization","contractual supply components","whether service can operate without human action"],
 "Cannot determine classification from the product label; request operational facts and accountant/legal review.",
 ["WP CareGrid has not been inspected or classified","A full service-category legal analysis is pending"],[eu],[ec])

# Existing Phase 3 rule material is converted to candidates, never copied into approved/.
old=json.loads((ROOT/"tests/fixtures/phase3-proposed-rule-fixtures.json").read_text(encoding="utf-8"))
mapping={"eu-vat-services-b2b-general":"article44-general-b2b","eu-vat-services-b2c-general":"article45-general-b2c","eu-vat-electronic-b2c-art58":"article58-electronic-b2c"}
for rule in old["rules"]:
    rid=rule["rule_id"]; research_id=cases[mapping[rid]]["research_id"]
    c={"candidate_id":"candidate-"+rule["rule_version_id"]+"-"+research_id[-6:],"research_id":research_id,"rule_id":rid,
      "rule_version_id":rule["rule_version_id"],"status":"PROPOSED","jurisdiction":rule["jurisdiction"],"topic":rule["topic"],
      "priority":rule["priority"],"conditions":rule["conditions"],"outcome":rule["outcome"],"evidence":rule["evidence"],
      "effective_from":rule["effective_from"],"effective_to":rule["effective_to"],"assumptions":[],
      "known_exceptions":rule["exclusions"],"unresolved_questions":rule["human_review_if"],"author":"research-agent",
      "created_at":STAMP,"review_required":True,"requires":rule["requires"],"exclusions":rule["exclusions"],
      "human_review_if":rule["human_review_if"],"description":rule["description"]}
    try: pipe.create_candidate(c)
    except Exception as exc:
        if "already exists" not in str(exc): raise
    reviewer.review(c["candidate_id"])
print("Research snapshots:",len(cases),"; proposed Phase 3 rule candidates:",len(mapping),"; completed reviews:",len(mapping))
