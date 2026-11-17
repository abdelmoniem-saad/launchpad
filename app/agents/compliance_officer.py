"""firm.compliance_officer: Tier 1 rule guard over every draft before the verification gate.

Failure -> one rewrite with the violation note; second failure -> output dropped, block logged.
"""
from __future__ import annotations

import json

from app import config
from app import decision_log as dl
from app.guardrails import rule_violations, scrub_card_numbers

AGENT = "firm.compliance_officer"


def scan(work: dict, report: dict, positions: dict) -> list[str]:
    text = json.dumps({"work": work, "report": report, "departments": positions}, ensure_ascii=False)
    return rule_violations(text)


def rewrite(step: dict, work: dict, violations: list[str]) -> dict:
    system = (config.load_prompt("compliance_officer.md") +
              f"\n\nRewrite the work so it breaks none of these rules: {violations}. Keep the same JSON keys. "
              'Reply JSON: {"work": {...}}')
    reply = config.call_model(AGENT, system, json.dumps(work, ensure_ascii=False)[:4000])
    dl.log(AGENT, f"rewrite step {step['id']} to fix {violations}", model=config.model_name(), cost=0)
    return reply.get("work") if isinstance(reply.get("work"), dict) else {}


def clean(work: dict) -> dict:
    return json.loads(scrub_card_numbers(json.dumps(work, ensure_ascii=False)))
