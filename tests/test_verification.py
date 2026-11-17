"""Tier 2 quote check and the department-panel key handling."""
import json

from langchain_core.messages import AIMessage

from app import config
from app.agents import departments
from app.guardrails import find_quote, tier2_verify
from tests.conftest import BRIEF

URL = "https://example.org/long-page"
FILLER = "Unrelated text about weather and gardens. " * 40  # ~1,700 chars before the evidence
PAGE = FILLER + "Flower prices fluctuate sharply between seasons, which makes revenue hard to forecast."


class JudgeSpy:
    """Fake model that records what the judge was shown and supports every claim."""

    def __init__(self):
        self.payloads = []

    def invoke(self, messages):
        payload = json.loads(messages[1].content)
        self.payloads.append(payload)
        body = {"verdicts": [{"id": p["id"], "supported": True, "note": ""} for p in payload]}
        return AIMessage(content=json.dumps(body), usage_metadata={"input_tokens": 1, "output_tokens": 1, "total_tokens": 2})


def _claim(cid, quote):
    return {"id": cid, "text": "Flower prices are volatile", "source_url": URL, "quote": quote,
            "type": "SOURCED", "step": "1.1"}


def test_find_quote_ignores_case_punctuation_and_spacing():
    assert find_quote("flower PRICES fluctuate  sharply", PAGE) == PAGE.index("Flower prices")
    assert find_quote("“Flower prices — fluctuate sharply”", PAGE) >= 0
    assert find_quote("prices are stable all year", PAGE) == -1
    assert find_quote("prices", PAGE) == -1  # too short to prove anything


def test_judge_sees_passage_around_quote_deep_in_page(env):
    spy = JudgeSpy()
    config.set_llm(spy)
    claims, flags = tier2_verify([_claim("C1.1-1", "Flower prices fluctuate sharply between seasons")],
                                 {URL: PAGE}, "1.1")
    assert claims[0]["type"] == "SOURCED"
    assert flags == []
    assert "Flower prices fluctuate sharply" in spy.payloads[0][0]["source_text"]


def test_invented_quote_becomes_assumption_without_judge_call(env):
    spy = JudgeSpy()
    config.set_llm(spy)
    claims, flags = tier2_verify([_claim("C1.1-1", "Flower prices doubled in 2025 across Europe")],
                                 {URL: PAGE}, "1.1")
    assert claims[0]["type"] == "ASSUMPTION"
    assert "quote not found" in flags[0]
    assert spy.payloads == []


class PanelReply:
    def __init__(self, departments_field):
        self.field = departments_field

    def invoke(self, messages):
        body = {"work": {}, "departments": self.field}
        return AIMessage(content=json.dumps(body), usage_metadata={"input_tokens": 1, "output_tokens": 1, "total_tokens": 2})


def _panel(env, field):
    config.set_llm(PanelReply(field))
    step = {"id": "1.1", "title": "t", "task": "t", "work_keys": {}}
    return departments.panel(step, {"brief": BRIEF, "claims": []}, ["founder_fit", "finance"])["positions"]


def test_panel_accepts_dept_prefixed_keys(env):
    positions = _panel(env, {"dept.founder_fit": {"position": "p", "pushback": "too many hours", "tradeoff": "t"},
                             "Finance": {"position": "f", "pushback": "", "tradeoff": ""}})
    assert positions["founder_fit"]["pushback"] == "too many hours"
    assert positions["finance"]["position"] == "f"


def test_panel_accepts_list_of_departments(env):
    positions = _panel(env, [{"department": "founder_fit", "position": "p", "pushback": "x", "tradeoff": "y"}])
    assert positions["founder_fit"]["pushback"] == "x"
    assert positions["finance"]["position"] == ""
