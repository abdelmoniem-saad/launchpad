"""firm.quant_modeler: every number goes through the calculator. The model never does the maths."""
from __future__ import annotations

import re

from app import decision_log as dl
from app import build_tests, tools
from app.guardrails import find_quote

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
            basis = (f"{work.get('expected_visitors')} visitors x {work.get('expected_conversion_pct')} conversion "
                     f"(a value below 1 is read as a fraction; ASSUMPTION unless sourced). {work.get('basis', '')}")
            if target < 1:
                target = tools.DEFAULT_WAITLIST_TARGET
                basis = (f"ASSUMPTION: the visitor or conversion estimate was missing or not a number "
                         f"({work.get('expected_visitors')!r} x {work.get('expected_conversion_pct')!r}), so a default target of "
                         f"{target} signups is proposed; the founder should adjust it before locking.")
            out = {"proposed_threshold": {"metric": "waitlist signups", "target": target,
                                          "days": int(work.get("test_days") or 14), "basis": basis}}
        elif kind == "blueprint_cost":
            out = tools.total_cost(work.get("roles", []), brief.get("budget_usd"))
        elif kind == "pricing":
            out = _pricing(work, state)
        elif kind == "build_tests":
            out = {"build_tests": build_tests.run(work)}
    except (TypeError, ValueError, KeyError) as exc:
        out = {"error": f"calculator rejected the inputs: {exc}"}
    if kind:
        dl.log(AGENT, f"calculator {kind} step {step['id']}", model=None, cost=0)
    return out


def _quoted(price, quote: str) -> bool:
    """True when the price figure itself appears in the quoted source text (e.g. 12, 12.0 or 12.00)."""
    v = float(price)
    forms = {f"{v:g}", f"{v:.2f}"} | ({f"{int(v)}"} if v.is_integer() else set())
    return any(re.search(rf"(?<![\d.]){re.escape(f)}(?![\d])", quote) for f in forms)


def label_price_points(work: dict, quant: dict) -> dict:
    """Mark each proposed price point so the report never shows an unsourced price as a finding."""
    counted = {(p["product"], p["price_usd"]) for p in quant.get("counted_price_points", [])}
    points = []
    for p in work.get("price_points", []) if isinstance(work.get("price_points"), list) else []:
        try:
            key = (p.get("product"), float(p.get("price_usd")))
        except (TypeError, ValueError):
            key = None
        points.append({**p, "status": "SOURCED (counted)" if key in counted
                       else "ASSUMPTION: not found in a verified source quote, ignored by the calculator"})
    return {**work, "price_points": points} if points else work


def _pricing(work: dict, state: dict) -> dict:
    """Tiers from price points backed by a SOURCED claim whose quote contains the price; billing types never mixed."""
    claims = {c["id"]: c for c in state.get("claims", [])}
    pages = state.get("sources_text") or {}
    groups: dict[str, list] = {}
    counted, rejected = [], []
    for p in work.get("price_points", []) if isinstance(work.get("price_points"), list) else []:
        c = claims.get(str(p.get("claim_id") or ""), {})
        quote = str(c.get("quote") or "")
        on_page = find_quote(quote, str(pages.get(c.get("source_url"), "")), min_words=1) >= 0
        try:
            ok = c.get("type") == "SOURCED" and on_page and float(p.get("price_usd")) > 0 and _quoted(p["price_usd"], quote)
        except (TypeError, ValueError):
            ok = False
        if ok:
            billing = str(p.get("billing") or "one_time")
            groups.setdefault(billing, []).append(float(p["price_usd"]))
            counted.append({"product": p.get("product"), "price_usd": float(p["price_usd"]), "billing": billing,
                            "claim_id": c["id"], "source_url": c.get("source_url")})
        else:
            rejected.append(p.get("product"))
    out: dict = {"counted_price_points": counted, "not_counted": rejected,
                 "rule": "A price counts only if its claim is SOURCED (after verification), its quote is on the fetched page, "
                         "and the quote contains that price."}
    if groups:
        billing, prices = max(groups.items(), key=lambda kv: len(kv[1]))
        stats = tools.price_stats(prices)
        out.update({"price_stats": stats, "billing": billing, "pricing_tiers": tools.pricing_options(stats["median"]),
                    "basis": f"0.6x / 1x / 1.6x the median of {stats['count']} sourced {billing} price(s): ${stats['median']}"})
        return out
    median = ((state.get("work_memory") or {}).get("price_stats") or {}).get("median")
    if median:
        out.update({"pricing_tiers": tools.pricing_options(median), "billing": "monthly",
                    "basis": f"no price sourced in this step; step 1.3's sourced competitor median ${median}/month"})
    else:
        out.update({"pricing_tiers": [], "basis": "no sourced prices: tiers left to the founder (ASSUMPTION)"})
    return out
