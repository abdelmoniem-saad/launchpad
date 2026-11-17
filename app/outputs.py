"""Writes outputs/: phase<N>_step<M>_<name>.md per step, phase<N>_gate_<name>.(md|json) per gate,
and cost_report.json. Conclusion first; every claim shows its source URL or ASSUMPTION.
"""
from __future__ import annotations

import json
from pathlib import Path

from app import config
from app.phases import PHASE_NAMES


def _p(state, name: str) -> Path:
    d = Path(state["run_dir"])
    d.mkdir(parents=True, exist_ok=True)
    return d / name


def sfx(state) -> str:
    """Optional run label, so a second demo run (e.g. the weak brief) sits beside the first in outputs/."""
    label = (state.get("run_label") or "").strip().lower()
    return f"_{label}" if label else ""


def step_file(state, step) -> Path:
    phase, num = step["id"].split(".")
    return _p(state, f"phase{phase}_step{num}_{step['name']}{sfx(state)}.md")


def _render_value(v, depth=0) -> list[str]:
    pad = "  " * depth
    if isinstance(v, dict):
        out = []
        for k, x in v.items():
            if isinstance(x, (dict, list)):
                out.append(f"{pad}- **{k}:**")
                out += _render_value(x, depth + 1)
            else:
                out.append(f"{pad}- **{k}:** {x}")
        return out
    if isinstance(v, list):
        out = []
        for x in v:
            if isinstance(x, dict):
                out.append(f"{pad}- " + "; ".join(f"{k}: {y}" for k, y in x.items() if not isinstance(y, (dict, list)) or y))
            else:
                out.append(f"{pad}- {x}")
        return out
    return [f"{pad}{v}"]


def render_step(state, step, decision: dict | None = None, gate: dict | None = None) -> str:
    report, label = state.get("report") or {}, "LIVE" if step.get("live") else "MOCKED"
    lines = [f"# Phase {step['phase']} ({PHASE_NAMES[step['phase']]}), step {step['id']}: {step['title']}", "",
             f"Status: **{label}**. Model: `{config.model_name()}`. Brief: {state['brief'].get('idea', '')}", "",
             "## Conclusion", "", report.get("conclusion", ""), ""]
    if (state.get("evidence") or {}).get("demo_input") and step["phase"] >= 2 and step["id"] >= "2.4":
        lines[4:4] = ["> **DEMO INPUT:** the step 2.4 waitlist result in this run is hypothetical; no real demand test was run, "
                      "so everything from step 2.4 on is a demonstration, not validated demand.", ""]
    if report.get("key_points"):
        lines += ["## Supporting points", ""]
        for kp in report["key_points"]:
            ids = ", ".join(kp.get("claim_ids") or [])
            lines.append(f"- {kp.get('text', '')} ({kp.get('label', 'ASSUMPTION')}{': ' + ids if ids else ''})")
        lines.append("")
    if report.get("rationale"):
        lines += [f"Strategy architect recommendation: **{report.get('recommendation', '').upper()}**. {report['rationale']}", ""]
    if state.get("work"):
        lines += ["## Work", ""] + _render_value(state["work"]) + [""]
    if state.get("quant"):
        lines += ["## Calculator results (quant modeler)", "", "```json", json.dumps(state["quant"], indent=2), "```", ""]
    drafts = state.get("drafts") or {}
    if drafts:
        lines += ["## Department positions and pushback", "", "| Department | Position | Pushback | Trade-off |", "|---|---|---|---|"]
        for d, p in drafts.items():
            cell = lambda s: str(s or "").replace("|", "/").replace("\n", " ")  # noqa: E731
            lines.append(f"| {d} | {cell(p.get('position'))} | {cell(p.get('pushback'))} | {cell(p.get('tradeoff'))} |")
        lines.append("")
    if report.get("open_disagreements"):
        lines += ["## Open disagreements for the founder", ""] + [f"- {x}" for x in report["open_disagreements"]] + [""]
    mine = [c for c in state.get("claims", []) if c.get("step") == step["id"]]
    if mine:
        lines += ["## Claims ledger", "", "| ID | Claim | Label | Source |", "|---|---|---|---|"]
        for c in mine:
            text = c["text"].replace("|", "/").replace("\n", " ")
            lines.append(f"| {c['id']} | {text} | {c['type']} | {c.get('source_url') if c['type'] == 'SOURCED' else 'ASSUMPTION'} |")
        lines.append("")
    elif step.get("live") and step.get("queries"):
        lines += ["## Claims ledger", "", "No claims could be sourced in this step; everything above is ASSUMPTION.", ""]
    flags = (state.get("verification_flags") or []) + (state.get("health_flags") or [])
    if flags:
        lines += ["## Governance flags", ""] + [f"- {f}" for f in flags] + [""]
    if state.get("pending_actions"):
        lines += ["## Proposed actions (MOCKED, pending founder approval in the action gateway)", ""]
        lines += [f"- {a}" for a in state["pending_actions"]] + [""]
    if decision:
        lines += ["## Founder checkpoint", "", f"Decision: **{decision.get('decision')}**"
                  + (f". Feedback: {decision.get('feedback')}" if decision.get("feedback") else ""), ""]
    if gate:
        lines += ["## Gate", "", f"Outcome: **{gate['outcome'].upper()}**", ""] + [f"- {r}" for r in gate["reasons"]] + [""]
    return "\n".join(lines)


def write_step(state, step, decision=None, gate=None) -> Path:
    path = step_file(state, step)
    path.write_text(render_step(state, step, decision, gate), "utf-8")
    return path


def write_gate(state, step, name: str, gate: dict) -> None:
    data = {"step": step["id"], "gate": name, "outcome": gate["outcome"], "reasons": gate["reasons"],
            "comparison": gate.get("comparison"), "thresholds": state.get("thresholds"),
            "founder_decision": state.get("founder_decision")}
    _p(state, f"phase{step['phase']}_gate_{name}{sfx(state)}.json").write_text(json.dumps(data, indent=2), "utf-8")
    md = [f"# Phase {step['phase']} gate: {name}", "", f"**Outcome: {gate['outcome'].upper()}**", ""] + [f"- {r}" for r in gate["reasons"]]
    _p(state, f"phase{step['phase']}_gate_{name}{sfx(state)}.md").write_text("\n".join(md) + "\n", "utf-8")


def write_final(state, phase: int, outcome: str, reasons: list[str]) -> None:
    lines = [f"# Final recommendation: {outcome.upper()}", "", f"Brief: {state['brief'].get('idea', '')}", "",
             *[f"- {r}" for r in reasons], "", "## Gate history", ""]
    lines += [f"- step {g['step']}: {g['outcome']} ({'; '.join(g['reasons'])})" for g in state.get("gate_history", [])]
    lines += ["", "This system never promises income or success. Every claim above is sourced or labelled ASSUMPTION."]
    _p(state, f"phase{phase}_gate_final_recommendation{sfx(state)}.md").write_text("\n".join(lines) + "\n", "utf-8")


def write_cost(state) -> dict:
    rep = config.COST.report()
    _p(state, f"cost_report{sfx(state)}.json").write_text(json.dumps(rep, indent=2), "utf-8")
    return rep
