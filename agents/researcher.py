"""Phase 1, Discover: find and rank opportunities around the founder's idea."""
from __future__ import annotations

import re
import urllib.request

from agents.base import run_agent
from guardrails import product_block_reason


def fetch_source(url: str, limit: int = 3000) -> str:
    """Read a founder-supplied source page (plain text, truncated). Failures are noted, not fatal."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "launchpad-research/0.1"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read(200_000).decode("utf-8", errors="ignore")
    except Exception as exc:  # noqa: BLE001
        return f"(could not fetch: {exc})"
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)[:limit]


def run(context: dict, llm, log) -> dict:
    blocked = product_block_reason(context["idea"])
    if blocked:
        log.append("researcher", "screen_idea", outcome="blocked", reason=blocked)
        return {"summary": f"Idea not pursued: {blocked}.", "details": {}, "evidence": [],
                "confidence": 0.0, "blocked_reason": blocked}
    if context.get("sources") and "source_text" not in context:
        context["source_text"] = {u: fetch_source(u) for u in context["sources"]}
        log.append("researcher", "read_sources", sources=context["sources"])
    return run_agent("researcher", "find_opportunities", context, llm, log)
