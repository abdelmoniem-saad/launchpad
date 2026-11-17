"""firm.strategy_architect: phase lead. Breaks each step into tasks and assigns them (MECE).

The plan is deterministic (from phases.py) so it costs no tokens; the architect's drafting and
gate recommendation run inside the department panel and the synthesis call.
"""
from __future__ import annotations

from app import decision_log as dl

AGENT = "firm.strategy_architect"


def plan(step: dict, roster: list[str], fast: bool) -> dict:
    tasks = []
    if step.get("queries"):
        tasks.append({"task": "web research, claims with URLs", "owner": "firm.market_researcher"})
    tasks.append({"task": step.get("task") or step["title"], "owner": "firm.strategy_architect + departments"})
    if step.get("quant"):
        tasks.append({"task": f"calculator: {step['quant']}", "owner": "firm.quant_modeler"})
    tasks += [{"task": "conclusion-first report", "owner": "firm.synthesis_lead"},
              {"task": "rule check", "owner": "firm.compliance_officer"},
              {"task": "claim verification", "owner": "governance.verification_gate"}]
    dl.log(AGENT, f"plan step {step['id']} ({'fast' if fast else 'full'} mode): {len(tasks)} tasks, departments {roster}")
    return {"tasks": tasks, "departments": roster}
