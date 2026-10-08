"""Validate/import a qualified VAT adviser's JSON response; never approves execution."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.research_pipeline.adviser_review import import_adviser_response


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/import_adviser_response.py RESPONSE.json", file=sys.stderr)
        return 2
    try:
        response = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        result = import_adviser_response(response, ROOT)
    except Exception as exc:
        print(f"Adviser response rejected: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"candidate_id": result["response"]["candidate_id"],
        "adviser_status": result["adviser_status"], "execution_approval_created": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
