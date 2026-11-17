"""Phase 2, Validate: test demand, competitors and willingness to pay against the evidence."""
from __future__ import annotations

from agents.base import run_agent


def run(context: dict, llm, log) -> dict:
    return run_agent("validator", "validate_demand", context, llm, log)
