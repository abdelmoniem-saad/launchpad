"""Phase 3, Build: specify the minimum sellable digital product and its first deliverable."""
from __future__ import annotations

from agents.base import run_agent


def run(context: dict, llm, log) -> dict:
    return run_agent("builder", "build_mvp_spec", context, llm, log)
