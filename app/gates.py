"""Gate evaluator: go / repeat / pivot / stop, decided in code.

Gate types: founder approval (the checkpoint), evidence thresholds (Phase 1 evidence gate),
a pre-registered demand threshold locked by the founder before results exist (Phase 2 demand
gate, compared in code), and tests pass (Phase 3 build gate, app/build_tests.py).
"""
from __future__ import annotations

from app.tools import compare_threshold

GO, REPEAT, PIVOT, STOP = "go", "repeat", "pivot", "stop"
MAX_REPEATS_PER_STEP = 1
MAX_PIVOTS = 1
DEMO_NOTE = ("DEMO INPUT: this result is hypothetical, entered to demonstrate the gate and later phases; "
             "no real demand test was run, so demand is NOT validated")


class ThresholdLocked(Exception):
    pass


def lock_threshold(thresholds: dict, proposal: dict) -> dict:
    """Founder locks the demand threshold. Once locked it cannot change."""
    if thresholds.get("locked"):
        raise ThresholdLocked("threshold already locked; it cannot be changed after locking")
    target = int(proposal["target"])
    if target < 1:
        raise ValueError("a demand threshold must be at least 1; a target of 0 can never fail")
    return {**proposal, "target": target, "days": int(proposal.get("days", 14)), "locked": True}


def change_threshold(thresholds: dict, new: dict) -> dict:
    if thresholds.get("locked"):
        raise ThresholdLocked("threshold already locked; it cannot be changed after locking")
    return {**thresholds, **new}


def evidence_gate(claims: list[dict], phase: int = 1) -> dict:
    """Phase 1 evidence gate: enough verified, sourced claims and at least one sourced demand signal
    for THIS product. A source that only shows the customer's general problems is not demand for the
    product (`product_demand` is set by guardrails.product_demand_check; unchecked claims count)."""
    mine = [c for c in claims if str(c.get("step", "")).startswith(f"{phase}.")]
    sourced = [c for c in mine if c.get("type") == "SOURCED"]
    signals = [c for c in sourced if str(c.get("step")) == f"{phase}.4"]
    demand = [c for c in signals if c.get("product_demand", True) is True]
    unchecked = [c for c in signals if "product_demand" in c and c["product_demand"] is None]
    sites = {_site(c.get("source_url")) for c in demand} - {""}
    ratio = len(sourced) / len(mine) if mine else 0.0
    reasons = [f"{len(sourced)}/{len(mine)} Phase {phase} claims are sourced and verified (ratio {ratio:.2f})",
               f"{len(demand)} of {len(signals)} sourced demand signal(s) from step {phase}.4 show demand for this product"
               + (f", from {len(sites)} independent site(s)" if demand else "")]
    if len(sourced) < 3 or ratio < 0.3:
        return {"outcome": STOP, "reasons": reasons + ["evidence too weak: recommend STOP rather than build on assumptions"]}
    if not signals:
        return {"outcome": PIVOT, "reasons": reasons + ["no sourced demand signal: recommend PIVOT to a different niche"]}
    if unchecked and not demand:  # fail closed: a signal nobody could check never counts as demand
        return {"outcome": REPEAT, "reasons": reasons + [
            f"{len(unchecked)} signal(s) could not be checked for product demand (model error): repeat the check, never count them"]}
    if not demand:
        return {"outcome": STOP, "reasons": reasons + [
            "don't launch this: the sources show the customer's problems, but none shows anyone wanting this "
            "product or paying for something like it. Recommend STOP rather than build on hope."]}
    if len(sites) < MIN_DEMAND_SITES:
        return {"outcome": PIVOT, "reasons": reasons + [
            f"thin evidence: demand for this product shows up on fewer than {MIN_DEMAND_SITES} independent sites, so one "
            "community or one vendor page could be the whole story. Recommend PIVOT (sharper niche or different customer)."]}
    return {"outcome": GO, "reasons": reasons + ["evidence threshold met"]}


MIN_DEMAND_SITES = 2


def _site(url) -> str:
    """Registered site of a URL (www. and subdomains of the same site count once)."""
    from urllib.parse import urlparse
    host = urlparse(str(url or "")).netloc.lower().split(":")[0]
    parts = [p for p in host.split(".") if p]
    if len(parts) >= 3 and len(parts[-1]) == 2 and parts[-2] in ("co", "com", "org", "net", "ac", "gov", "edu"):
        return ".".join(parts[-3:])  # e.g. example.co.uk
    return ".".join(parts[-2:])


def demand_gate(thresholds: dict, actual: int | None, demo_input: bool = False) -> dict:
    g = _demand_gate(thresholds, actual)
    if demo_input and actual is not None:
        g = {**g, "reasons": [DEMO_NOTE] + g["reasons"], "demo_input": True}
    return g


def _demand_gate(thresholds: dict, actual: int | None) -> dict:
    if not thresholds.get("locked"):
        return {"outcome": STOP, "reasons": ["no locked threshold: a target must be locked before results exist"]}
    if actual is None:
        return {"outcome": REPEAT, "reasons": ["no results entered yet: run the demand test, then enter the real number"]}
    cmp = compare_threshold(thresholds["target"], actual)
    reasons = [f"locked target {cmp['target']} {thresholds.get('metric', '')} in {thresholds.get('days')} days; actual {cmp['actual']} ({cmp['ratio']:.0%})"]
    if cmp["met"]:
        return {"outcome": GO, "reasons": reasons + ["threshold met"], "comparison": cmp}
    if cmp["ratio"] >= 0.5:
        return {"outcome": PIVOT, "reasons": reasons + ["below target but real interest: recommend PIVOT (positioning or channel)"], "comparison": cmp}
    return {"outcome": STOP, "reasons": reasons + ["far below target: recommend STOP"], "comparison": cmp}


def tests_gate(result: dict) -> dict:
    """Phase 3 gate: the MVP passes every build test (app/build_tests.py), checked in code."""
    from app.build_tests import failures
    if not result or not result.get("tests"):
        return {"outcome": REPEAT, "reasons": ["no build test results: the MVP was not built"]}
    reasons = [f"{result['passed']}/{result['total']} build tests passed"]
    if result.get("all_passed"):
        return {"outcome": GO, "reasons": reasons + ["all build tests pass"]}
    return {"outcome": REPEAT, "reasons": reasons + [f"failing: {f}" for f in failures(result)]}


def step_gate(step: dict, state: dict, founder_decision: str) -> dict:
    """Combine the founder's checkpoint decision with the step's evidence rules."""
    sid = step["id"]
    repeats = (state.get("repeats") or {}).get(sid, 0)
    if founder_decision == "stop":
        return {"outcome": STOP, "reasons": ["founder chose stop"]}
    if founder_decision == "redo":
        if repeats >= MAX_REPEATS_PER_STEP + 1:
            return {"outcome": STOP, "reasons": ["step already redone; stopping rather than looping"]}
        return {"outcome": REPEAT, "reasons": ["founder asked to redo with feedback"]}
    if state.get("step_blocked"):
        if repeats >= MAX_REPEATS_PER_STEP:
            return {"outcome": STOP, "reasons": ["output blocked by the rule guard twice"]}
        return {"outcome": REPEAT, "reasons": ["output blocked by the rule guard; repeating once"]}
    if step.get("gate") == "evidence":
        g = evidence_gate(state.get("claims", []), step["phase"])
        if g["outcome"] == REPEAT and repeats >= MAX_REPEATS_PER_STEP:
            g = {"outcome": STOP, "reasons": g["reasons"] + ["the product demand check failed twice: STOP rather than guess"]}
        if g["outcome"] == PIVOT and (state.get("pivots") or 0) >= MAX_PIVOTS:
            g = {"outcome": STOP, "reasons": g["reasons"] + ["already pivoted once: STOP"]}
        return g
    if step.get("gate") == "demand":
        ev = state.get("evidence") or {}
        g = demand_gate(state.get("thresholds") or {}, ev.get("actual"), bool(ev.get("demo_input")))
        if g["outcome"] == REPEAT and repeats >= MAX_REPEATS_PER_STEP:
            g = {**g, "outcome": STOP, "reasons": g["reasons"] + ["paused: run the demand test, then start again with the real result"]}
        if g["outcome"] == PIVOT and (state.get("pivots") or 0) >= MAX_PIVOTS:
            g = {**g, "outcome": STOP, "reasons": g["reasons"] + ["already pivoted once: STOP"]}
        return g
    if step.get("gate") == "tests":
        g = tests_gate((state.get("quant") or {}).get("build_tests") or {})
        if g["outcome"] == REPEAT and repeats >= MAX_REPEATS_PER_STEP:
            g = {**g, "outcome": STOP, "reasons": g["reasons"] + ["build tests still fail after one redo: STOP rather than ship a broken MVP"]}
        return g
    return {"outcome": GO, "reasons": ["founder approved"]}
