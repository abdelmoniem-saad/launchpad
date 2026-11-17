"""Gate evaluator: go / repeat / pivot / stop, decided in code.

Gate types: founder approval (the checkpoint), evidence thresholds (Phase 1 evidence gate),
a pre-registered demand threshold locked by the founder before results exist (Phase 2 demand
gate, compared in code), and tests pass (Build, MOCKED here).
"""
from __future__ import annotations

from app.tools import compare_threshold

GO, REPEAT, PIVOT, STOP = "go", "repeat", "pivot", "stop"
MAX_REPEATS_PER_STEP = 1
MAX_PIVOTS = 1


class ThresholdLocked(Exception):
    pass


def lock_threshold(thresholds: dict, proposal: dict) -> dict:
    """Founder locks the demand threshold. Once locked it cannot change."""
    if thresholds.get("locked"):
        raise ThresholdLocked("threshold already locked; it cannot be changed after locking")
    return {**proposal, "target": int(proposal["target"]), "days": int(proposal.get("days", 14)), "locked": True}


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
    demand = [c for c in signals if c.get("product_demand", True)]
    ratio = len(sourced) / len(mine) if mine else 0.0
    reasons = [f"{len(sourced)}/{len(mine)} Phase {phase} claims are sourced and verified (ratio {ratio:.2f})",
               f"{len(demand)} of {len(signals)} sourced demand signal(s) from step {phase}.4 show demand for this product"]
    if len(sourced) < 3 or ratio < 0.3:
        return {"outcome": STOP, "reasons": reasons + ["evidence too weak: recommend STOP rather than build on assumptions"]}
    if not signals:
        return {"outcome": PIVOT, "reasons": reasons + ["no sourced demand signal: recommend PIVOT to a different niche"]}
    if not demand:
        return {"outcome": STOP, "reasons": reasons + [
            "don't launch this: the sources show the customer's problems, but none shows anyone wanting this "
            "product or paying for something like it. Recommend STOP rather than build on hope."]}
    return {"outcome": GO, "reasons": reasons + ["evidence threshold met"]}


def demand_gate(thresholds: dict, actual: int | None) -> dict:
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
        if g["outcome"] == PIVOT and (state.get("pivots") or 0) >= MAX_PIVOTS:
            g = {"outcome": STOP, "reasons": g["reasons"] + ["already pivoted once: STOP"]}
        return g
    if step.get("gate") == "demand":
        g = demand_gate(state.get("thresholds") or {}, (state.get("evidence") or {}).get("actual"))
        if g["outcome"] == REPEAT and repeats >= MAX_REPEATS_PER_STEP:
            g = {**g, "outcome": STOP, "reasons": g["reasons"] + ["paused: run the demand test, then start again with the real result"]}
        if g["outcome"] == PIVOT and (state.get("pivots") or 0) >= MAX_PIVOTS:
            g = {**g, "outcome": STOP, "reasons": g["reasons"] + ["already pivoted once: STOP"]}
        return g
    return {"outcome": GO, "reasons": ["founder approved"]}
