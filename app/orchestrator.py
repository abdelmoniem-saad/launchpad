"""Parent graph: brief intake -> completeness check (founder interview) -> excluded-product check
-> every step (step subgraph) -> founder checkpoint (interrupt) -> gate -> go / repeat / pivot / stop
-> engagement close-out. Phases 1-2 are LIVE; phases 3-6 are MOCKED drafts.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app import config, gates, outputs, step_subgraph
from app import decision_log as dl
from app.agents import engagement_manager as em
from app.phases import STEPS
from app.state import EngagementState

DECISIONS = ("approve", "edit", "redo", "stop")


def _step(state):
    return STEPS[state["step_index"]]


def intake(state: EngagementState) -> dict:
    config.COST.__init__()
    dl.log("firm.engagement_manager", "brief_intake", model=None)
    return {"status": "running", "step_index": 0, "claims": [], "sources_text": {}, "repeats": {}, "pivots": 0,
            "thresholds": {}, "evidence": {}, "work_memory": {}, "gate_history": [], "founder_feedback": "",
            "fast_mode": state.get("fast_mode", config.FAST_MODE)}


def completeness(state: EngagementState) -> dict:
    questions = em.interview_questions(state["brief"], state.get("clarified", False))
    if not questions:
        dl.log("firm.engagement_manager", "completeness_check: brief complete")
        return {"clarified": True}
    answers = interrupt({"type": "brief_interview", "questions": questions,
                         "missing": [q["field"] for q in questions if q["required"]],
                         "question": "Before we start, a few questions so we understand your case."})
    answers = {k: v for k, v in (answers or {}).items() if v not in (None, "")}
    dl.log("firm.engagement_manager", f"founder_interview: answered {sorted(answers)}")
    return {"brief": {**state["brief"], **answers}, "clarified": True}


def route_completeness(state) -> str:
    return "completeness" if em.missing_fields(state["brief"]) else "excluded_check"


def excluded_check(state: EngagementState) -> dict:
    reason = em.excluded(state["brief"])
    if reason:
        return {"status": "stopped", "stop_reason": reason, "gate_outcome": gates.STOP,
                "gate_history": [{"step": "intake", "outcome": gates.STOP, "reasons": [reason]}]}
    return {}


def collect(state: EngagementState) -> dict:
    """Founder inputs a step needs before it runs (the real demand-test result for 2.4)."""
    step = _step(state)
    if not step.get("needs_results"):
        return {}
    t = state.get("thresholds") or {}
    data = interrupt({"type": "enter_results", "step": step["id"], "threshold": t,
                      "question": f"Enter the real number of {t.get('metric', 'signups')} after {t.get('days')} days (leave blank if the test has not run)."})
    raw = (data or {}).get("actual")
    actual = int(raw) if raw not in (None, "") else None
    dl.log("firm.engagement_manager", f"founder_entered_results step {step['id']}: {actual}", approved_by="founder")
    return {"evidence": {**(state.get("evidence") or {}), "actual": actual}}


def write(state: EngagementState) -> dict:
    outputs.write_step(state, _step(state))
    outputs.write_cost(state)
    return {}


def checkpoint(state: EngagementState) -> dict:
    step = _step(state)
    resp = interrupt({"type": "checkpoint", "step": step["id"], "title": step["title"], "live": step.get("live"),
                      "report": state.get("report"), "work": state.get("work"), "quant": state.get("quant"),
                      "departments": state.get("drafts"), "flags": (state.get("verification_flags") or []) + (state.get("health_flags") or []),
                      "pending_actions": state.get("pending_actions"), "file": str(outputs.step_file(state, step)),
                      "proposed_threshold": (state.get("quant") or {}).get("proposed_threshold")})
    resp = resp or {}
    decision = str(resp.get("decision", "")).lower()
    if decision not in DECISIONS:
        decision = "stop"
    update = {"founder_decision": decision, "founder_feedback": str(resp.get("feedback") or "")[:1000]}
    if decision == "edit" and resp.get("edited_conclusion"):
        update["report"] = {**(state.get("report") or {}), "conclusion": f"{resp['edited_conclusion']} (edited by the founder)"}
    proposal = (state.get("quant") or {}).get("proposed_threshold")
    if decision in ("approve", "edit") and proposal and not (state.get("thresholds") or {}).get("locked"):
        if resp.get("threshold_target") not in (None, ""):
            proposal = {**proposal, "target": int(resp["threshold_target"])}
        update["thresholds"] = gates.lock_threshold(state.get("thresholds") or {}, proposal)
        dl.log("firm.engagement_manager", f"founder_locked_threshold {update['thresholds']['target']} {proposal['metric']} in {proposal['days']} days",
               approved_by="founder")
    dl.log("firm.engagement_manager", f"founder_checkpoint step {step['id']}: {decision}", approved_by="founder",
           outcome=decision)
    return update


def gate(state: EngagementState) -> dict:
    step = _step(state)
    g = gates.step_gate(step, state, state.get("founder_decision", "stop"))
    dl.log("governance.gate_evaluator", f"gate step {step['id']}", outcome=g["outcome"], reasons=g["reasons"])
    if step.get("gate"):
        outputs.write_gate(state, step, step["gate"], g)
    outputs.write_step(state, step, {"decision": state.get("founder_decision"), "feedback": state.get("founder_feedback")}, g)
    history = (state.get("gate_history") or []) + [{"step": step["id"], "outcome": g["outcome"], "reasons": g["reasons"]}]
    upd = {"gate_outcome": g["outcome"], "gate_history": history}
    o = g["outcome"]
    if o == gates.GO:
        mem = dict(state.get("work_memory") or {})
        q, w = state.get("quant") or {}, state.get("work") or {}
        if q.get("chosen_niche"):
            mem["niche"] = q["chosen_niche"]
        if q.get("sourced_price_stats", {}).get("count"):
            mem["price_stats"] = q["sourced_price_stats"]
        mem.setdefault("approved", {})[step["id"]] = (state.get("report") or {}).get("conclusion", "")[:400]
        if step["id"] == "2.5":
            upd["blueprint"] = w
        upd.update({"work_memory": mem, "step_index": state["step_index"] + 1, "founder_feedback": ""})
    elif o == gates.REPEAT:
        upd["repeats"] = {**(state.get("repeats") or {}), step["id"]: (state.get("repeats") or {}).get(step["id"], 0) + 1}
    elif o == gates.PIVOT:
        old = (state.get("work_memory") or {}).get("niche", state["brief"].get("idea"))
        upd.update({"pivots": (state.get("pivots") or 0) + 1, "step_index": 0, "claims": [],
                    "work_memory": {"pivot_from": old},
                    "founder_feedback": f"PIVOT: the evidence did not support '{old}'. Choose a different niche. Reasons: {'; '.join(g['reasons'])}"})
    else:
        upd.update({"status": "stopped", "stop_reason": "; ".join(g["reasons"])})
    return upd


def route_gate(state) -> str:
    o = state.get("gate_outcome")
    if o == gates.STOP:
        return "close_out"
    if o == gates.GO and state["step_index"] >= len(STEPS):
        return "close_out"
    return "collect"


def close_out(state: EngagementState) -> dict:
    stopped = state.get("status") == "stopped"
    idx = min(state.get("step_index", 0), len(STEPS) - 1)
    phase = STEPS[idx]["phase"] if stopped else STEPS[-1]["phase"]
    outcome = gates.STOP if stopped else "completed"
    reasons = [state.get("stop_reason", "")] if stopped else ["All steps approved by the founder. Phases 3-6 are MOCKED drafts."]
    outputs.write_final(state, phase, outcome, reasons)
    rep = outputs.write_cost(state)
    dl.log("firm.engagement_manager", f"engagement_close_out: {outcome}", outcome=outcome,
           tokens=rep["tokens_total"], seconds=rep["wall_clock_seconds"])
    return {"status": "stopped" if stopped else "completed", "cost": rep}


def build(checkpointer):
    g = StateGraph(EngagementState)
    g.add_node("intake", intake)
    g.add_node("completeness", completeness)
    g.add_node("screen", excluded_check)  # refuse excluded products before interviewing the founder
    g.add_node("excluded_check", excluded_check)  # re-check once the interview answers are in
    g.add_node("collect", collect)
    g.add_node("run_step", step_subgraph.build())
    g.add_node("write", write)
    g.add_node("checkpoint", checkpoint)
    g.add_node("gate", gate)
    g.add_node("close_out", close_out)
    g.add_edge(START, "intake")
    g.add_edge("intake", "screen")
    g.add_conditional_edges("screen", lambda s: "close_out" if s.get("status") == "stopped" else "completeness",
                            ["close_out", "completeness"])
    g.add_conditional_edges("completeness", route_completeness, ["completeness", "excluded_check"])
    g.add_conditional_edges("excluded_check", lambda s: "close_out" if s.get("status") == "stopped" else "collect",
                            ["close_out", "collect"])
    g.add_edge("collect", "run_step")
    g.add_edge("run_step", "write")
    g.add_edge("write", "checkpoint")
    g.add_edge("checkpoint", "gate")
    g.add_conditional_edges("gate", route_gate, ["collect", "close_out"])
    g.add_edge("close_out", END)
    return g.compile(checkpointer=checkpointer)
