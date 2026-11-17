"""Phase 4, Commercial setup: price, offer, refund policy and terms (founder approves before use)."""
from __future__ import annotations

from agents.base import run_agent


def run(context: dict, llm, log) -> dict:
    return run_agent("commercial", "draft_offer_and_pricing", context, llm, log)
