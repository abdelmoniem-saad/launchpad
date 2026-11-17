"""Step subgraph, reused for every step:

strategy_architect (plan) -> market_researcher (live steps) -> work: department panel (fast) or
architect draft + parallel department reviews via Send + one negotiation round (full)
-> quant_modeler (calculator) -> synthesis_lead -> compliance_officer (Tier 1, one rewrite)
-> verification_gate (Tier 2) -> team_health_check -> action proposals (pending, MOCKED).
Step 2.4 takes the founder-entered result and compares it with the locked threshold in code.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from app import approval, gates
from app import decision_log as dl
from app.agents import (compliance_officer, departments, engagement_manager, market_researcher,
                        quant_modeler, strategy_architect, synthesis_lead)
from app.guardrails import health_check, label_numeric_claims, tier2_verify
from app.phases import STEPS, roster
from app.state import EngagementState

MAX_NEGOTIATION_ROUNDS = 2  # review + one negotiation round


def _step(state) -> dict:
    return STEPS[state["step_index"]]


def plan(state: EngagementState) -> dict:
    step = _step(state)
    r = roster(step["phase"])
    strategy_architect.plan(step, r, state.get("fast_mode", True))
    return {"current_step": step["id"], "current_phase": step["phase"], "departments": r,
            "drafts": {"__reset__": True}, "work": {}, "quant": {}, "report": {}, "verification_flags": [],
            "health_flags": [], "step_blocked": False, "compliance_note": "", "pending_actions": [], "health_rerun": False}


def route_after_plan(state) -> str:
    step = _step(state)
    if step.get("needs_results"):
        return "results"
    return "research" if step.get("live") and step.get("queries") else "work"


def research(state: EngagementState) -> dict:
    step = _step(state)
    res = market_researcher.research(step, state)
    claims = [c for c in state.get("claims", []) if c.get("step") != step["id"]] + res["claims"]
    return {"claims": claims, "sources_text": {**(state.get("sources_text") or {}), **res["pages"]}}


def work(state: EngagementState) -> dict:
    step = _step(state)
    if state.get("fast_mode", True):
        out = departments.panel(step, state, state["departments"])
        return {"work": out["work"], "drafts": out["positions"]}
    return {"work": departments.draft_work(step, state)}


def route_after_work(state):
    if state.get("fast_mode", True):
        return "quant"
    return [Send("dept_review", {**state, "_dept": d}) for d in state["departments"]]


def dept_review(state: dict) -> dict:
    d = state["_dept"]
    return {"drafts": {d: departments.review(d, _step(state), state)}}


def negotiate(state: EngagementState) -> dict:
    step, drafts = _step(state), dict(state.get("drafts") or {})
    for _ in range(MAX_NEGOTIATION_ROUNDS - 1):
        for d in state["departments"]:
            others = {k: v for k, v in drafts.items() if k != d}
            drafts[d] = departments.review(d, step, {**state, "drafts": drafts}, others=others)
    return {"drafts": drafts}


def quant(state: EngagementState) -> dict:
    step = _step(state)
    q = quant_modeler.compute(step, state.get("work", {}), state)
    drafts = dict(state.get("drafts") or {})
    if q.get("over_budget") and "finance" in drafts:  # Finance pushback triggered in code
        note = f"Over budget: plan costs ${q['monthly_total_usd']}/month against a ${q['budget_usd']} budget."
        drafts["finance"] = {**drafts["finance"], "pushback": (drafts["finance"].get("pushback", "") + " " + note).strip()}
        dl.log("dept.finance", f"pushback step {step['id']}: {note}")
        return {"quant": q, "drafts": drafts, "pushback_notes": [note]}
    return {"quant": q}


def synthesize(state: EngagementState) -> dict:
    step = _step(state)
    if not step.get("live"):
        report = {"conclusion": f"MOCKED draft for founder review: {step['title']}.", "key_points": [],
                  "open_disagreements": [p["pushback"] for p in (state.get("drafts") or {}).values() if p.get("pushback")],
                  "recommendation": "go", "rationale": "Phase is MOCKED; drafts only, nothing is executed."}
        return {"report": report}
    return {"report": engagement_manager.so_what(synthesis_lead.write(step, state))}


def compliance(state: EngagementState) -> dict:
    step = _step(state)
    w, report, drafts = compliance_officer.clean(state.get("work", {})), state.get("report", {}), state.get("drafts", {})
    violations = compliance_officer.scan(w, report, drafts)
    if not violations:
        dl.log("firm.compliance_officer", f"rule_check step {step['id']}: clean")
        return {"work": w}
    dl.log("firm.compliance_officer", f"rule_check step {step['id']}: violations {violations}; one rewrite", outcome="rewrite")
    w = compliance_officer.clean(compliance_officer.rewrite(step, w, violations))
    if step.get("live"):
        report = synthesis_lead.write(step, {**state, "work": w}, note=f"Remove anything breaking: {violations}")
    clean_drafts = {k: v for k, v in drafts.items() if not compliance_officer.scan({}, {}, {k: v})}
    still = compliance_officer.scan(w, report, clean_drafts)
    if still or not w:
        dl.log("firm.compliance_officer", f"blocked step {step['id']}: {still or 'empty rewrite'}; output dropped", outcome="blocked")
        return {"work": {}, "drafts": {"__reset__": True},
                "report": {"conclusion": f"Output blocked by the rule guard ({', '.join(still or violations)}). Nothing from this draft is used.",
                           "key_points": [], "open_disagreements": [], "recommendation": "repeat", "rationale": "rule guard"},
                "step_blocked": True, "verification_flags": [f"blocked: {still or violations}"]}
    return {"work": w, "report": report, "drafts": {"__reset__": True, **clean_drafts}}


def verify(state: EngagementState) -> dict:
    step = _step(state)
    mine = label_numeric_claims([c for c in state.get("claims", []) if c.get("step") == step["id"]])
    flags = list(state.get("verification_flags") or [])
    if mine and step.get("live") and not state.get("step_blocked"):
        mine, f2 = tier2_verify(mine, state.get("sources_text") or {}, step["id"])
        flags += f2
    claims = [c for c in state.get("claims", []) if c.get("step") != step["id"]] + mine
    report = dict(state.get("report") or {})
    types = {c["id"]: c["type"] for c in mine}
    for kp in report.get("key_points", []):
        kp["label"] = "SOURCED" if any(types.get(i) == "SOURCED" for i in kp.get("claim_ids", [])) else "ASSUMPTION"
    dl.log("governance.verification_gate", f"tier1_verify step {step['id']}: {sum(c['type'] == 'SOURCED' for c in mine)}/{len(mine)} sourced",
           sources=[c["source_url"] for c in mine if c["type"] == "SOURCED"])
    return {"claims": claims, "verification_flags": flags, "report": report}


def health(state: EngagementState) -> dict:
    step = _step(state)
    drafts = state.get("drafts") or {}
    flags = health_check(drafts) if len(drafts) > 0 and not state.get("step_blocked") else []
    dl.log("governance.team_health_check", f"step {step['id']}: {flags or 'healthy'}")
    if flags and not state.get("fast_mode", True) and not state.get("health_rerun"):
        new = {d: departments.review(d, step, {**state, "compliance_note": "Challenge the draft: name one concrete trade-off or risk "
                                                                            "specific to this founder's budget, time or skills."})
               for d in state["departments"]}
        flags2 = health_check(new)
        return {"drafts": new, "health_flags": [f"re-run once: {flags}"] + flags2, "health_rerun": True}
    return {"health_flags": flags}


def actions(state: EngagementState) -> dict:
    step = _step(state)
    if state.get("step_blocked"):
        return {}
    ids = []
    for type_, key, reason in step.get("actions", []):
        payload = (state.get("work") or {}).get(key)
        items = payload[:5] if isinstance(payload, list) else ([payload] if payload else [])
        for item in items:
            ids.append(approval.propose(state["run_dir"], step["id"], type_, {"draft": item, "status": "MOCKED"},
                                        reason, "firm.engagement_manager"))
    return {"pending_actions": ids}


def results(state: EngagementState) -> dict:
    step = _step(state)
    actual = (state.get("evidence") or {}).get("actual")
    g = gates.demand_gate(state.get("thresholds") or {}, actual)
    t = state.get("thresholds") or {}
    report = {"conclusion": f"Demand test: {actual if actual is not None else 'no result yet'} {t.get('metric', '')} against a locked target of "
                            f"{t.get('target')} in {t.get('days')} days. Gate recommendation: {g['outcome'].upper()}.",
              "key_points": [{"text": r, "claim_ids": [], "label": "FOUNDER-ENTERED"} for r in g["reasons"]],
              "open_disagreements": [], "recommendation": g["outcome"], "rationale": "compared in code against the locked threshold"}
    dl.log("governance.demand_gate", f"compare step {step['id']}: {g['reasons'][0]}", outcome=g["outcome"])
    return {"report": report, "quant": g.get("comparison", {}),
            "work": {"founder_entered_result": actual, "note": "Entered by the founder; the system never invents signups."}}


def build():
    g = StateGraph(EngagementState)
    for name, fn in [("plan", plan), ("research", research), ("work", work), ("dept_review", dept_review),
                     ("negotiate", negotiate), ("quant", quant), ("synthesize", synthesize), ("compliance", compliance),
                     ("verify", verify), ("health", health), ("actions", actions), ("results", results)]:
        g.add_node(name, fn)
    g.add_edge(START, "plan")
    g.add_conditional_edges("plan", route_after_plan, ["results", "research", "work"])
    g.add_edge("research", "work")
    g.add_conditional_edges("work", route_after_work, ["quant", "dept_review"])
    g.add_edge("dept_review", "negotiate")
    g.add_edge("negotiate", "quant")
    g.add_edge("quant", "synthesize")
    g.add_edge("synthesize", "compliance")
    g.add_edge("compliance", "verify")
    g.add_edge("verify", "health")
    g.add_edge("health", "actions")
    g.add_edge("actions", END)
    g.add_edge("results", END)
    return g.compile()
