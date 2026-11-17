"""Phase 3 build: the MVP is built in step 3.1 and a tests-pass gate, checked in code, decides go / repeat / stop."""
from pathlib import Path

from app import build_tests, gates
from tests.conftest import BRIEF, GOOD_MVP, FakeChat
from tests.test_smoke import drive, start


def test_good_mvp_passes_every_build_test():
    res = build_tests.run(GOOD_MVP)
    assert res["all_passed"], build_tests.failures(res)
    assert gates.tests_gate(res)["outcome"] == gates.GO


def test_broken_mvps_fail_named_tests():
    cases = {
        "placeholder": {**GOOD_MVP, "user_docs": GOOD_MVP["user_docs"] + " TODO: finish this."},
        "untested feature": {**GOOD_MVP, "test_plan": GOOD_MVP["test_plan"][:1]},
        "undocumented feature": {**GOOD_MVP, "core_features": GOOD_MVP["core_features"] + [{"name": "Invoice sheet", "content": "x " * 80}]},
        "thin content": {**GOOD_MVP, "core_features": [{"name": "Project board", "content": "A board."}]},
        "fake reviews": {**GOOD_MVP, "user_docs": GOOD_MVP["user_docs"] + " Testimonials: five-star reviews from editors."},
        "empty": {},
    }
    for name, work in cases.items():
        res = build_tests.run(work)
        assert not res["all_passed"], name
        assert gates.tests_gate(res)["outcome"] == gates.REPEAT, name


def test_failing_build_repeats_once_with_the_failures_then_stops(env):
    """The redo is told which tests failed; a build that still fails is never shipped."""
    from app import config
    fake = FakeChat(overrides={"3.1": {**GOOD_MVP, "user_docs": "Too short. TODO"}})
    config.set_llm(fake)
    graph, cfg, res = start(env)
    res, _ = drive(graph, cfg, res, lambda p: {"actual": 150} if p["type"] == "enter_results" else {"decision": "approve"})
    hist = [g for g in res["gate_history"] if g["step"] == "3.1"]
    assert [g["outcome"] for g in hist] == [gates.REPEAT, gates.STOP]
    assert res["status"] == "stopped" and "build tests" in res["stop_reason"]
    assert any("Fix the failing build tests" in c for c in fake.calls_full)


def test_passing_build_writes_the_product_and_the_gate(env):
    graph, cfg, res = start(env)
    res, _ = drive(graph, cfg, res, lambda p: {"actual": 150} if p["type"] == "enter_results" else {"decision": "approve"})
    out = Path(env["out"])
    product = (out / "phase3_step1_mvp_product.md").read_text()
    assert "Revision Tracker" in product and "## Project board" in product and "| PASS |" in product
    assert "Not published, listed or sold" in product
    assert "**Outcome: GO**" in (out / "phase3_gate_tests.md").read_text()
    assert "Status: **LIVE**" in (out / "phase3_step1_mvp_build.md").read_text()
    assert BRIEF["idea"]
