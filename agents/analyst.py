"""Phase 6, Operate and learn: read run metrics and recommend the next experiment."""
from __future__ import annotations

from agents.base import run_agent


def run(context: dict, llm, log) -> dict:
    return run_agent("analyst", "review_and_learn", context, llm, log)
