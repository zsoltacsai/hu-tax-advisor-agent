"""Local Phase 4 research/rule workflow; no network or model calls."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.research_pipeline.workflow import ResearchPipeline,PipelineError

def read(path):
    try:return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:raise PipelineError(f"cannot read JSON {path}: {e}")
def output(value):print(json.dumps(value,ensure_ascii=False,indent=2))
def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("research-submit");a.add_argument("--request",required=True);a.add_argument("--draft",required=True)
    a=sub.add_parser("research-validate");a.add_argument("--id",required=True)
    a=sub.add_parser("candidate-create");a.add_argument("--file",required=True)
    a=sub.add_parser("review-rule");a.add_argument("--candidate",required=True)
    a=sub.add_parser("approval-preview");a.add_argument("--candidate",required=True)
    a=sub.add_parser("approve-rule");a.add_argument("--candidate",required=True);a.add_argument("--actor",required=True)
    a=sub.add_parser("reject-rule");a.add_argument("--candidate",required=True);a.add_argument("--actor",required=True);a.add_argument("--reason",required=True)
    a=sub.add_parser("rule-status");a.add_argument("--candidate",required=True)
    a=sub.add_parser("list-rule-dependencies");a.add_argument("--source-id")
    a=sub.add_parser("record-source-check");a.add_argument("--file",required=True);a.add_argument("--actor",required=True)
    a=sub.add_parser("check-rule-freshness");a.add_argument("--rule-version",required=True)
    a=sub.add_parser("supersede-rule");a.add_argument("--old-version",required=True);a.add_argument("--new-version",required=True);a.add_argument("--effective-to",required=True);a.add_argument("--actor",required=True)
    a=sub.add_parser("retire-rule");a.add_argument("--rule-version",required=True);a.add_argument("--actor",required=True);a.add_argument("--reason",required=True)
    args=ap.parse_args(argv);p=ResearchPipeline(ROOT)
    try:
        if args.cmd=="research-submit": result=p.create_research(read(args.request),read(args.draft))
        elif args.cmd=="research-validate": result=p.read_snapshot(args.id)
        elif args.cmd=="candidate-create": result=p.create_candidate(read(args.file))
        elif args.cmd=="review-rule": result=p.review_candidate(args.candidate)
        elif args.cmd=="approval-preview": result=p.approval_preview(args.candidate)
        elif args.cmd=="approve-rule":
            if not sys.stdin.isatty():raise PipelineError("human approval requires an interactive terminal; non-interactive approval is disabled")
            preview=p.approval_preview(args.candidate)
            print("HUMAN APPROVAL REVIEW\n"+json.dumps(preview,ensure_ascii=False,indent=2))
            print("Approval is final for this immutable candidate hash. Review all limitations and source versions above.")
            phrase=input('Type exactly: I APPROVE THIS RULE FOR EXECUTION\n> ')
            result=p.approve(args.candidate,args.actor,phrase)
        elif args.cmd=="reject-rule": result=p.reject(args.candidate,args.actor,args.reason)
        elif args.cmd=="rule-status": result={"candidate_id":args.candidate,"status":p.candidate_status(args.candidate)}
        elif args.cmd=="list-rule-dependencies": result=p.dependencies(args.source_id)
        elif args.cmd=="record-source-check": result=p.record_source_check(read(args.file),args.actor)
        elif args.cmd=="check-rule-freshness": result={"rule_version_id":args.rule_version,"freshness":p.freshness(args.rule_version)}
        elif args.cmd=="supersede-rule": result=p.supersede(args.old_version,args.new_version,args.effective_to,args.actor)
        elif args.cmd=="retire-rule": result=p.retire(args.rule_version,args.actor,args.reason)
        else: raise PipelineError("unknown command")
        output(result);return 0
    except (PipelineError,ValueError,KeyError) as exc:
        print(f"REJECTED: {exc}",file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
