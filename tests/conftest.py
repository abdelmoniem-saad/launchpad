"""Test fixtures: a fake chat model and offline research tools. No network, no Ollama."""
import json
import re
import sys
import uuid
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config, tools  # noqa: E402

PAGE = ("Freelance video editors on the forum say client revisions are hard to track and invoices get lost. "
        "Many editors ask for a simple tracker template. EditorTrack costs $12 per month. "
        "ClipBoard Pro costs $20 per month. A community of 40,000 editors meets weekly. ") * 3
URL = "https://example.org/editors-forum"
URL2 = "https://example.org/pricing-page"


def work_for(step_id: str, overrides: dict) -> dict:
    base = {
        "1.1": {"sharpened_idea": "Revision tracker templates for freelance video editors",
                "niches": [{"name": "video editors", "why": "pain", "demand": 4, "competition": 3, "founder_fit": 5, "claim_ids": []},
                           {"name": "photographers", "why": "adjacent", "demand": 3, "competition": 2, "founder_fit": 3, "claim_ids": []}]},
        "1.2": {"options": [{"name": "tracker", "is_founder_idea": True, "demand": 4, "competition": 3, "founder_fit": 5, "effort": 4}]},
        "1.3": {"market_definition": "freelance editors", "segments": ["solo"], "competitors": [], "market_size_note": "unknown"},
        "1.4": {"demand_signals": [{"signal": "editors ask for a tracker", "claim_id": "C1.4-1"}],
                "interview_script": ["Tell me about the last time a revision got lost."], "who_to_interview": "editors"},
        "2.2": {"landing_page_markdown": "# Revision tracker\nJoin the waitlist.", "channels": ["forum"], "test_days": 14,
                "expected_visitors": 1000, "expected_conversion_pct": 10, "basis": "ASSUMPTION"},
        "2.3": {"communities": [], "partners": [], "outreach_drafts": [{"to": "forum mods", "channel": "email", "message": "Hello"}]},
        "2.5": {"roles": [{"department": "finance", "role": "bookkeeping", "choice": "automate", "reason": "cheap", "monthly_cost_usd": 30}],
                "backlog": {"finance": ["set up tool"]}, "job_post_drafts": []},
    }
    return overrides.get(step_id, base.get(step_id, {"draft": f"MOCKED draft {step_id}"}))


class FakeChat:
    """Returns role-appropriate JSON. `overrides` maps step id -> work dict."""

    def __init__(self, overrides=None, synthesis_extra=""):
        self.overrides = overrides or {}
        self.synthesis_extra = synthesis_extra
        self.calls = []

    def invoke(self, messages):
        system, user = messages[0].content, messages[1].content
        self.calls.append(system[:40])
        step = (re.search(r"Step (\d\.\d)", user) or [None, "1.1"])[1]
        if system.startswith("# firm.market_researcher"):
            urls = re.findall(r'"url": "([^"]+)"', user)
            body = {"claims": [{"text": "Editors ask for a simple tracker template", "source_url": u,
                                "quote": "Many editors ask for a simple tracker template"} for u in urls[:2]]}
        elif "verify claims" in system:
            ids = re.findall(r'"id": "([^"]+)"', user)
            body = {"verdicts": [{"id": i, "supported": True, "note": ""} for i in ids]}
        elif system.startswith("# firm.strategy_architect"):
            depts = re.findall(r"## dept\.(\w+)", system)
            body = {"work": work_for(step, self.overrides),
                    "departments": {d: {"position": f"{d} view {uuid.uuid4().hex[:6]}", "pushback": f"{d} concern about scope",
                                        "tradeoff": "time vs reach"} for d in depts}}
        elif system.startswith("# firm.synthesis_lead"):
            ids = re.findall(r'"id": "(C[\d.]+-\d+)"', user)
            body = {"conclusion": f"Step {step} conclusion. {self.synthesis_extra}".strip(),
                    "key_points": [{"text": "Editors want a tracker", "claim_ids": ids[:1]}],
                    "open_disagreements": [], "recommendation": "go", "rationale": "evidence ok"}
        elif system.startswith("# firm.compliance_officer"):
            body = {"work": {"draft": "clean rewrite"}}
        else:
            body = {"position": "dept review", "pushback": "a concern", "tradeoff": "cost"}
        return AIMessage(content=json.dumps(body), usage_metadata={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150})


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("DECISION_LOG", str(tmp_path / "decision_log.json"))
    monkeypatch.setenv("STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("SEARCH_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(tools, "search", lambda q: {"query": q, "results": [{"url": URL}, {"url": URL2}], "cached": False})
    monkeypatch.setattr(tools, "fetch", lambda url, limit=3500: {"url": url, "text": PAGE})
    fake = FakeChat()
    config.set_llm(fake)
    yield {"dir": tmp_path, "out": str(tmp_path / "outputs"), "llm": fake}
    config.set_llm(None)


BRIEF = {"idea": "Notion templates that track client revisions for freelance video editors",
         "target_customer": "freelance video editors", "market": "global, English-speaking",
         "budget_usd": 200, "hours_per_week": 10, "skills": "video editing, Notion", "values": "honest, simple"}
