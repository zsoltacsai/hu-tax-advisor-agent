"""Arithmetic threshold comparator; does not decide statutory eligibility."""
from typing import Any

def compare_threshold(amount: float | int | None, threshold: dict | None, currency: str | None=None, year: int | None=None) -> dict[str,Any]:
    if amount is None or threshold is None:
        return {"status":"unknown","amount":amount,"threshold_id":threshold.get("threshold_id") if threshold else None,"reason":"amount or threshold metadata missing"}
    if currency and currency!=threshold.get("currency"):
        return {"status":"unknown","amount":amount,"threshold_id":threshold.get("threshold_id"),"reason":"currency mismatch; no implicit conversion"}
    if year is not None and year!=threshold.get("year"):
        return {"status":"unknown","amount":amount,"threshold_id":threshold.get("threshold_id"),"reason":"tax-year mismatch"}
    limit=threshold["amount"]
    state="below_threshold" if amount<limit else "at_threshold" if amount==limit else "above_threshold"
    return {"status":state,"amount":amount,"threshold_id":threshold["threshold_id"],"threshold_amount":limit,"currency":threshold["currency"],"year":threshold["year"],"reason":"Arithmetic comparison only; legal eligibility is not determined."}
