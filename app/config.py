"""Model factory and the single entry point for every model call.

Default: a local open-weight model through Ollama (keyless). Optional fast mode: Groq free tier
(`openai/gpt-oss-120b`) when GROQ_API_KEY is set, rate-limited, with any error falling back to
local Ollama. Every call is timed and its tokens counted for the cost report.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"

LOCAL_MODEL = os.environ.get("LOCAL_MODEL", "qwen3:8b")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
FAST_MODE = os.environ.get("FAST_MODE", "1") != "0"


@dataclass
class CostTracker:
    calls: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    seconds: float = 0.0
    by_agent: dict = field(default_factory=dict)

    def add(self, agent: str, tin: int, tout: int, secs: float) -> None:
        self.calls += 1
        self.tokens_in += tin
        self.tokens_out += tout
        self.seconds += secs
        a = self.by_agent.setdefault(agent, {"calls": 0, "tokens": 0, "seconds": 0.0})
        a["calls"] += 1
        a["tokens"] += tin + tout
        a["seconds"] = round(a["seconds"] + secs, 1)

    def report(self) -> dict:
        return {"cost_usd": 0.0, "model": model_name(), "calls": self.calls,
                "tokens_in": self.tokens_in, "tokens_out": self.tokens_out,
                "tokens_total": self.tokens_in + self.tokens_out,
                "wall_clock_seconds": round(self.seconds, 1), "by_agent": self.by_agent,
                "pricing_note": "Local Ollama, the Groq free tier and the Tavily free tier are priced at $0."}


COST = CostTracker()
_llm = None


def model_name() -> str:
    if os.environ.get("GROQ_API_KEY"):
        return f"groq/{GROQ_MODEL} (fallback ollama/{LOCAL_MODEL})"
    return f"ollama/{LOCAL_MODEL}"


def build_llm():
    from langchain_ollama import ChatOllama

    # gpt-oss cannot switch reasoning off: with reasoning=False it still reasons, hidden, until it hits
    # num_predict and returns an empty reply. Low effort plus room for the reasoning tokens fixes that.
    gpt_oss = LOCAL_MODEL.startswith("gpt-oss")
    local = ChatOllama(model=LOCAL_MODEL, base_url=OLLAMA_HOST, format="json",
                       reasoning="low" if gpt_oss else False,
                       temperature=0.2, num_ctx=8192, num_predict=4096 if gpt_oss else 1500)
    if not os.environ.get("GROQ_API_KEY"):
        return local
    from langchain_core.rate_limiters import InMemoryRateLimiter
    from langchain_groq import ChatGroq

    limiter = InMemoryRateLimiter(requests_per_second=0.4, check_every_n_seconds=0.2, max_bucket_size=1)
    groq = ChatGroq(model=GROQ_MODEL, temperature=0.2, rate_limiter=limiter,
                    model_kwargs={"response_format": {"type": "json_object"}})
    return groq.with_fallbacks([local])


def set_llm(llm) -> None:
    """Swap the model (tests use a fake chat model)."""
    global _llm
    _llm = llm


def get_llm():
    global _llm
    if _llm is None:
        _llm = build_llm()
    return _llm


def load_prompt(path: str) -> str:
    return (PROMPTS_DIR / path).read_text(encoding="utf-8")


def parse_json(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model reply")
    return json.loads(text[start:end + 1])


def call_model(agent: str, system: str, user: str) -> dict:
    """Call the model, return parsed JSON. Failure returns {"_error": ...} instead of raising."""
    from langchain_core.messages import HumanMessage, SystemMessage

    t0 = time.time()
    try:
        msg = get_llm().invoke([SystemMessage(content=system), HumanMessage(content=user)])
    except Exception as exc:  # noqa: BLE001
        COST.add(agent, 0, 0, time.time() - t0)
        return {"_error": f"model call failed: {exc}"}
    usage = getattr(msg, "usage_metadata", None) or {}
    COST.add(agent, usage.get("input_tokens", 0), usage.get("output_tokens", 0), time.time() - t0)
    try:
        return parse_json(msg.content if isinstance(msg.content, str) else str(msg.content))
    except (ValueError, json.JSONDecodeError) as exc:
        return {"_error": f"unparseable reply: {exc}"}
