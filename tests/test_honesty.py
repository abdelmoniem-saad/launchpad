"""Consulting honesty: invented internal metrics are blocked; Finance pushes back over budget;
unsourced numeric claims become ASSUMPTION; a weak brief ends in stop or pivot."""
import uuid

from langgraph.checkpoint.memory import InMemorySaver

from app import config, guardrails, orchestrator, tools
from app.agents import quant_modeler
from app.step_subgraph import compliance, quant
from tests.conftest import BRIEF, FakeChat
from tests.test_smoke import drive, start


def _state(env, step_index, work, drafts=None):
    return {"brief": BRIEF, "run_dir": env["out"], "step_index": step_index, "work": work, "report": {},
            "drafts": drafts or {}, "claims": [], "departments": ["founder_fit", "marketing", "finance"]}


def test_invented_internal_metric_is_blocked(env):
    config.set_llm(FakeChat())  # rewrite returns a clean draft
    work = {"note": "Our sprint velocity is 40 points and our gross margin is 80%."}
    assert "invented_internal_metrics" in guardrails.rule_violations(str(work))
    out = compliance(_state(env, 0, work))
    assert "sprint velocity" not in str(out.get("work"))


def test_unsourced_numeric_claim_becomes_assumption():
    claims = guardrails.label_numeric_claims([{"id": "x", "text": "The market is worth $4B", "type": "SOURCED", "source_url": None}])
    assert claims[0]["type"] == "ASSUMPTION"


def test_finance_pushback_over_budget(env):
    work = {"roles": [{"department": "marketing", "role": "ads", "choice": "hire_later", "reason": "", "monthly_cost_usd": 900}]}
    drafts = {"finance": {"department": "finance", "position": "ok", "pushback": "", "tradeoff": ""}}
    out = quant({**_state(env, 8, work, drafts), "brief": {**BRIEF, "budget_usd": 200}})
    assert out["quant"]["over_budget"] is True
    assert "Over budget" in out["drafts"]["finance"]["pushback"]


def test_weak_brief_ends_in_stop(env, monkeypatch):
    monkeypatch.setattr(tools, "search", lambda q: {"query": q, "results": [], "cached": False})
    graph, cfg, res = start(env, {**BRIEF, "idea": "an app for everything for everyone"})
    res, _ = drive(graph, cfg, res, lambda p: {"decision": "approve"} if p["type"] == "checkpoint" else {"actual": ""})
    assert res["status"] == "stopped"
    assert any(g["outcome"] in ("stop", "pivot") for g in res["gate_history"])


def test_problem_without_product_demand_says_dont_launch(env):
    """The sources show the customer's problems, but nobody wants this product: the evidence gate stops."""
    config.set_llm(FakeChat(product_demand=False))
    graph, cfg, res = start(env)
    res, _ = drive(graph, cfg, res, lambda p: {"decision": "approve"} if p["type"] == "checkpoint" else {"actual": ""})
    gate_14 = next(g for g in res["gate_history"] if g["step"] == "1.4")
    assert gate_14["outcome"] == "stop"
    assert any("don't launch this" in r for r in gate_14["reasons"])
    assert res["status"] == "stopped"
