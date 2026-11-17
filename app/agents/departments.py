"""Client departments (dept.*): built phase by phase; each reviews and pushes back.

Fast mode: one panel call where the strategy architect drafts the step's work and every
department on the roster states its position and pushback.
Full mode: the architect drafts the work, then each department reviews it in parallel
(LangGraph Send fan-out), then one negotiation round where each reads the others' drafts.
Departments may only use the brief's budget, time, skills and values, or sourced figures.
"""
from __future__ import annotations

import json

from app import config
from app import decision_log as dl


def _context(step: dict, state: dict) -> str:
    claims = [{"id": c["id"], "text": c["text"], "type": c["type"], "source_url": c.get("source_url")}
              for c in state.get("claims", []) if c.get("step") == step["id"]]
    earlier = state.get("work_memory") or {}
    return (f"Step {step['id']}: {step['title']}\nTask: {step['task']}\n"
            f"Brief (the founder's real constraints): {json.dumps(state['brief'], ensure_ascii=False)}\n"
            f"Earlier decisions: {json.dumps(earlier, ensure_ascii=False)[:2500]}\n"
            f"Claims for this step (cite by id): {json.dumps(claims, ensure_ascii=False)}\n"
            + (f"Founder feedback to apply: {state['founder_feedback']}\n" if state.get("founder_feedback") else "")
            + (f"Compliance notes to fix: {state['compliance_note']}\n" if state.get("compliance_note") else ""))


def _dept_key(name) -> str:
    key = str(name or "").strip().lower().replace(" ", "_").replace("-", "_")
    return key.removeprefix("dept.").removeprefix("dept_")


def _by_department(raw) -> dict:
    """Panel answers keyed by bare department name, accepting "dept.x" keys or a list of entries."""
    if isinstance(raw, list):
        raw = {(e.get("department") or e.get("name")): e for e in raw if isinstance(e, dict)}
    if not isinstance(raw, dict):
        return {}
    return {_dept_key(k): v for k, v in raw.items() if isinstance(v, dict)}


def panel(step: dict, state: dict, roster: list[str]) -> dict:
    """Fast mode: one call returns {"work": {...}, "departments": {name: {position, pushback, tradeoff}}}."""
    dept_prompts = "\n\n".join(f"## dept.{d}\n{config.load_prompt(f'dept_{d}.md')}" for d in roster)
    system = (config.load_prompt("strategy_architect.md") + "\n\nDepartments at the table:\n" + dept_prompts +
              f"\n\nReply JSON: {{\"work\": {step['work_keys']}, \"departments\": {{\"<name>\": "
              "{\"position\": str, \"pushback\": str, \"tradeoff\": str}}}}\n"
              f"Use exactly these department names as keys: {', '.join(roster)}")
    reply = config.call_model("firm.strategy_architect", system, _context(step, state))
    work = reply.get("work") if isinstance(reply.get("work"), dict) else {}
    answers = _by_department(reply.get("departments"))
    positions = {}
    for d in roster:
        p = answers.get(d) or {}
        positions[d] = {"department": d, "position": str(p.get("position", "")), "pushback": str(p.get("pushback", "")),
                        "tradeoff": str(p.get("tradeoff", ""))}
    dl.log("firm.strategy_architect", f"draft_work_with_department_panel step {step['id']} ({', '.join(roster)})"
           + (f"; error {reply['_error']}" if reply.get("_error") else ""), model=config.model_name(), cost=0)
    for d, p in positions.items():
        dl.log(f"dept.{d}", f"position step {step['id']}" + (": pushback raised" if p["pushback"] else ""),
               model=config.model_name(), cost=0)
    return {"work": work, "positions": positions, "error": reply.get("_error")}


def draft_work(step: dict, state: dict) -> dict:
    """Full mode: the architect drafts the work alone."""
    system = config.load_prompt("strategy_architect.md") + f"\n\nReply JSON: {{\"work\": {step['work_keys']}}}"
    reply = config.call_model("firm.strategy_architect", system, _context(step, state))
    dl.log("firm.strategy_architect", f"draft_work step {step['id']}", model=config.model_name(), cost=0)
    return reply.get("work") if isinstance(reply.get("work"), dict) else {}


def review(dept: str, step: dict, state: dict, others: dict | None = None) -> dict:
    """Full mode: one department reviews the draft (and, in negotiation, the others' positions)."""
    system = (config.load_prompt(f"dept_{dept}.md") +
              '\n\nReply JSON: {"position": str, "pushback": str, "tradeoff": str}')
    user = _context(step, state) + f"\nDraft work: {json.dumps(state.get('work', {}), ensure_ascii=False)[:3000]}"
    if others:
        user += f"\nOther departments said: {json.dumps(others, ensure_ascii=False)[:2000]}"
    reply = config.call_model(f"dept.{dept}", system, user)
    dl.log(f"dept.{dept}", f"{'negotiate' if others else 'review'} step {step['id']}", model=config.model_name(), cost=0)
    return {"department": dept, "position": str(reply.get("position", "")), "pushback": str(reply.get("pushback", "")),
            "tradeoff": str(reply.get("tradeoff", ""))}
