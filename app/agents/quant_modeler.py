"""firm.quant_modeler: every number goes through the calculator. The model never does the maths."""
from __future__ import annotations

from app import decision_log as dl
from app import tools

AGENT = "firm.quant_modeler"


def compute(step: dict, work: dict, state: dict) -> dict:
    kind = step.get("quant")
    brief = state["brief"]
    out: dict = {}
    try:
        if kind == "score_niches":
            ranked = tools.weighted_scores(work.get("niches", []), {"demand": 0.4, "competition": 0.3, "founder_fit": 0.3})
            out = {"ranked_niches": ranked, "weights": "demand 0.4, competition 0.3, founder fit 0.3",
                   "chosen_niche": ranked[0]["name"] if ranked else None}
        elif kind == "score_options":
            ranked = tools.weighted_scores(work.get("options", []),
                                           {"demand": 0.35, "competition": 0.2, "founder_fit": 0.25, "effort": 0.2})
            out = {"ranked_options": ranked, "weights": "demand 0.35, competition 0.2, founder fit 0.25, effort 0.2"}
        elif kind == "price_stats":
            claims = {c["id"]: c for c in state.get("claims", [])}
            sourced = [c.get("price_usd_per_month") for c in work.get("competitors", [])
                       if claims.get(c.get("claim_id") or "", {}).get("type") == "SOURCED"]
            out = {"sourced_price_stats": tools.price_stats(sourced),
                   "note": "Only competitor prices backed by a verified, sourced claim are counted."}
        elif kind == "threshold":
            target = tools.threshold_target(work.get("expected_visitors", 0), work.get("expected_conversion_pct", 0))
            out = {"proposed_threshold": {"metric": "waitlist signups", "target": target,
                                          "days": int(work.get("test_days") or 14),
                                          "basis": f"{work.get('expected_visitors')} visitors x {work.get('expected_conversion_pct')}% "
                                                   f"conversion (ASSUMPTION unless sourced). {work.get('basis', '')}"}}
        elif kind == "blueprint_cost":
            out = tools.total_cost(work.get("roles", []), brief.get("budget_usd"))
        elif kind == "pricing":
            median = ((state.get("work_memory") or {}).get("price_stats") or {}).get("median")
            out = ({"pricing_tiers": tools.pricing_options(median), "basis": f"sourced competitor median ${median}/month"}
                   if median else {"pricing_tiers": [], "basis": "no sourced competitor prices: tiers left to the founder (ASSUMPTION)"})
    except (TypeError, ValueError, KeyError) as exc:
        out = {"error": f"calculator rejected the inputs: {exc}"}
    if kind:
        dl.log(AGENT, f"calculator {kind} step {step['id']}", model=None, cost=0)
    return out
