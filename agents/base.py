"""Shared agent runner: load the role's prompt, call the model, parse JSON, log the action."""
from __future__ import annotations

import json
from pathlib import Path

from llm import parse_json

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

OUTPUT_CONTRACT = """
Reply with ONE JSON object only, with these keys:
  "summary": short plain-text summary,
  "details": object with your role-specific results,
  "evidence": list of {"claim": str, "source": URL or "ASSUMPTION"},
  "confidence": number 0..1 (how strongly the evidence supports going on),
  "pivot_suggestion": string or null.
Only cite URLs that appear in the provided sources. Anything else is "ASSUMPTION".
Never promise income or success. Never invent reviews, testimonials, sign-ups or deadlines.
"""


def load_prompt(role: str) -> str:
    return (PROMPTS_DIR / f"{role}.md").read_text(encoding="utf-8")


def run_agent(role: str, action: str, context: dict, llm, log) -> dict:
    system = load_prompt(role) + "\n" + OUTPUT_CONTRACT
    user = "Context (JSON):\n" + json.dumps(context, indent=2, default=str)[:12000]
    reply = llm(system, user)
    try:
        result = parse_json(reply.text)
    except (ValueError, json.JSONDecodeError) as exc:
        result = {"summary": f"Model reply could not be parsed: {exc}", "details": {},
                  "evidence": [], "confidence": 0.0}
    result.setdefault("evidence", [])
    result.setdefault("details", {})
    allowed = set(context.get("sources") or [])
    for item in result["evidence"]:
        if item.get("source") not in allowed:
            item["source"] = "ASSUMPTION"
    cited = sorted({e["source"] for e in result["evidence"] if e["source"] != "ASSUMPTION"})
    log.append(role, action, sources=cited, model=reply.model, cost=reply.cost, tokens=reply.tokens)
    return result
