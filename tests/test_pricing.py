"""Step 4.1 pricing (LIVE): tiers come only from prices that a verified quote on a fetched page contains."""
from app.agents import quant_modeler
from app.phases import STEPS, STEP_INDEX

URL = "https://example.org/pricing"
PAGE = "Compare plans. EditorTrack costs $12 one-time. ClipBoard Pro costs $20 one-time. CutList is $9 per month."
STEP = STEPS[STEP_INDEX["4.1"]]


def claim(cid, quote, type_="SOURCED", url=URL):
    return {"id": cid, "text": quote, "quote": quote, "source_url": url, "type": type_, "step": "4.1"}


def state(claims, memory=None):
    return {"brief": {"budget_usd": 300}, "claims": claims, "sources_text": {URL: PAGE}, "work_memory": memory or {}}


def point(product, price, cid, billing="one_time"):
    return {"product": product, "price_usd": price, "billing": billing, "claim_id": cid}


def test_step_41_is_live_with_research_and_42_is_mocked():
    assert STEP["live"] and STEP["queries"] and STEP["quant"] == "pricing"
    policies = STEPS[STEP_INDEX["4.2"]]
    assert not policies["live"] and "not legal advice" in policies["title"]


def test_tiers_from_sourced_quoted_prices(env):
    claims = [claim("C4.1-1", "EditorTrack costs $12 one-time."), claim("C4.1-2", "ClipBoard Pro costs $20 one-time.")]
    work = {"price_points": [point("EditorTrack", 12, "C4.1-1"), point("ClipBoard Pro", 20, "C4.1-2")]}
    q = quant_modeler.compute(STEP, work, state(claims))
    assert q["price_stats"] == {"count": 2, "min": 12.0, "median": 16.0, "max": 20.0}
    assert [t["price_usd"] for t in q["pricing_tiers"]] == [9.6, 16.0, 25.6]
    assert q["billing"] == "one_time" and len(q["counted_price_points"]) == 2


def test_invented_or_unverified_prices_are_not_counted(env):
    claims = [claim("C4.1-1", "EditorTrack costs $12 one-time."),                  # price not in the quote below
              claim("C4.1-2", "ClipBoard Pro costs $20 one-time.", type_="ASSUMPTION"),  # downgraded by verification
              claim("C4.1-3", "Pro plan costs $49 one-time.")]                    # quote is not on the fetched page
    work = {"price_points": [point("EditorTrack", 15, "C4.1-1"), point("ClipBoard Pro", 20, "C4.1-2"),
                             point("Pro", 49, "C4.1-3"), point("NoClaim", 30, None)]}
    q = quant_modeler.compute(STEP, work, state(claims))
    assert q["counted_price_points"] == [] and q["pricing_tiers"] == []
    assert "ASSUMPTION" in q["basis"] and len(q["not_counted"]) == 4
    labelled = quant_modeler.label_price_points(work, q)["price_points"]
    assert all(p["status"].startswith("ASSUMPTION") for p in labelled)


def test_counted_prices_are_labelled_sourced(env):
    claims = [claim("C4.1-1", "EditorTrack costs $12 one-time.")]
    work = {"price_points": [point("EditorTrack", 12, "C4.1-1"), point("Made up", 99, "C4.1-1")]}
    labelled = quant_modeler.label_price_points(work, quant_modeler.compute(STEP, work, state(claims)))["price_points"]
    assert labelled[0]["status"] == "SOURCED (counted)" and labelled[1]["status"].startswith("ASSUMPTION")


def test_billing_types_are_never_mixed(env):
    claims = [claim("C4.1-1", "EditorTrack costs $12 one-time."), claim("C4.1-2", "ClipBoard Pro costs $20 one-time."),
              claim("C4.1-3", "CutList is $9 per month.")]
    work = {"price_points": [point("EditorTrack", 12, "C4.1-1"), point("ClipBoard Pro", 20, "C4.1-2"),
                             point("CutList", 9, "C4.1-3", billing="monthly")]}
    q = quant_modeler.compute(STEP, work, state(claims))
    assert q["billing"] == "one_time" and q["price_stats"]["count"] == 2


def test_falls_back_to_step_13_sourced_median(env):
    q = quant_modeler.compute(STEP, {"price_points": []}, state([], memory={"price_stats": {"count": 3, "median": 10}}))
    assert [t["price_usd"] for t in q["pricing_tiers"]] == [6.0, 10.0, 16.0] and "1.3" in q["basis"]
