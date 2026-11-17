"""Phase 5, Sell/deliver/get paid: draft honest landing-page copy (publishing needs founder approval)."""
from __future__ import annotations

from agents.base import run_agent
from guardrails import copy_violations


def run(context: dict, llm, log) -> dict:
    result = run_agent("seller", "draft_landing_page", context, llm, log)
    copy = str(result.get("details", {}).get("landing_page_markdown", ""))
    violations = copy_violations(copy)
    if violations:
        log.append("guardrails", "check_sales_copy", outcome="blocked", violations=violations)
        result["blocked_reason"] = f"sales copy broke content limits: {violations}"
    return result
