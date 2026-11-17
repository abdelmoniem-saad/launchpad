"""Smoke: a brief runs to the first checkpoint and through the pipeline; log entries have the
required fields; outputs use phase/step names; the cost report is written."""
import json
import re
import uuid
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app import decision_log as dl
from app import orchestrator
from tests.conftest import BRIEF


def start(env, brief=None):
    graph = orchestrator.build(InMemorySaver())
    cfg = {"configurable": {"thread_id": uuid.uuid4().hex}, "recursion_limit": 400}
    res = graph.invoke({"brief": brief or BRIEF, "run_dir": env["out"], "fast_mode": True}, cfg)
    return graph, cfg, res


def drive(graph, cfg, res, decide):
    """Resume until done; `decide(payload)` returns the founder's answer."""
    seen = []
    while res.get("__interrupt__"):
        payload = res["__interrupt__"][0].value
        seen.append(payload)
        res = graph.invoke(Command(resume=decide(payload)), cfg)
    return res, seen


def test_brief_runs_to_first_checkpoint(env):
    _, _, res = start(env)
    payload = res["__interrupt__"][0].value
    assert payload["type"] == "checkpoint" and payload["step"] == "1.1"
    assert Path(payload["file"]).name == "phase1_step1_idea_and_industry.md"


def test_full_run_names_log_and_cost(env):
    graph, cfg, res = start(env)

    def decide(p):
        if p["type"] == "enter_results":
            return {"actual": 150}
        return {"decision": "approve"}

    res, seen = drive(graph, cfg, res, decide)
    assert res["status"] == "completed", res.get("stop_reason")
    out = Path(env["out"])
    names = sorted(p.name for p in out.iterdir())
    for n in names:
        assert re.match(r"^(phase\d_(step\d_[a-z0-9_]+|gate_[a-z0-9_]+)\.(md|json)|cost_report\.json)$", n), n
    assert "phase1_gate_evidence.json" in names and "phase2_gate_demand.json" in names
    assert "phase4_step1_pricing.md" in names and "phase4_step2_policies.md" in names
    assert "Status: **LIVE**" in (out / "phase4_step1_pricing.md").read_text()
    assert "Status: **MOCKED**" in (out / "phase4_step2_policies.md").read_text()
    cost = json.loads((out / "cost_report.json").read_text())
    assert cost["cost_usd"] == 0 and cost["calls"] > 0
    entries = dl.entries()
    assert entries
    for e in entries:
        for k in dl.REQUIRED_KEYS:
            assert k in e
        assert e["approved_by"] in (None, "founder")
        assert isinstance(e["sources"], list) and isinstance(e["cost"], (int, float))
    assert any(e["approved_by"] == "founder" for e in entries)


def test_missing_brief_fields_trigger_interview(env):
    graph, cfg, res = start(env, {"idea": "Notion templates for editors"})
    payload = res["__interrupt__"][0].value
    assert payload["type"] == "brief_interview"
    assert "budget_usd" in payload["missing"]
    res = graph.invoke(Command(resume={"target_customer": "editors", "budget_usd": 100, "hours_per_week": 5,
                                       "skills": "editing"}), cfg)
    assert res["__interrupt__"][0].value["type"] == "checkpoint"


def test_founder_stop_ends_engagement(env):
    graph, cfg, res = start(env)
    res, _ = drive(graph, cfg, res, lambda p: {"decision": "stop"})
    assert res["status"] == "stopped"
    assert (Path(env["out"]) / "phase1_gate_final_recommendation.md").exists()


def test_clarifying_questions_asked_once(env):
    brief = {k: v for k, v in BRIEF.items() if k not in ("product_format", "existing_audience", "success_goal")}
    graph, cfg, res = start(env, brief)
    payload = res["__interrupt__"][0].value
    assert payload["type"] == "brief_interview" and payload["missing"] == []
    fields = {q["field"]: q for q in payload["questions"]}
    assert fields["product_format"]["options"] and fields["success_goal"]["options"] is None
    res = graph.invoke(Command(resume={"product_format": "template pack"}), cfg)  # skipping the others is allowed
    assert res["__interrupt__"][0].value["type"] == "checkpoint"
