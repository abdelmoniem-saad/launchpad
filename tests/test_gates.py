"""Gates: a missed threshold never returns go; a locked threshold cannot change; weak evidence stops."""
import pytest

from app import gates


def test_target_100_actual_12_is_not_go():
    t = gates.lock_threshold({}, {"metric": "waitlist signups", "target": 100, "days": 14})
    g = gates.demand_gate(t, 12)
    assert g["outcome"] in (gates.PIVOT, gates.STOP)
    assert g["outcome"] != gates.GO


def test_target_met_is_go():
    t = gates.lock_threshold({}, {"metric": "waitlist signups", "target": 100, "days": 14})
    assert gates.demand_gate(t, 130)["outcome"] == gates.GO


def test_locked_threshold_cannot_change():
    t = gates.lock_threshold({}, {"metric": "waitlist signups", "target": 100, "days": 14})
    with pytest.raises(gates.ThresholdLocked):
        gates.change_threshold(t, {"target": 10})
    with pytest.raises(gates.ThresholdLocked):
        gates.lock_threshold(t, {"metric": "waitlist signups", "target": 10, "days": 14})


def test_unlocked_threshold_never_passes():
    assert gates.demand_gate({"target": 100}, 500)["outcome"] == gates.STOP


def test_weak_evidence_recommends_stop():
    claims = [{"id": "a", "step": "1.1", "type": "ASSUMPTION"}, {"id": "b", "step": "1.4", "type": "ASSUMPTION"}]
    assert gates.evidence_gate(claims)["outcome"] == gates.STOP


def test_no_demand_signal_recommends_pivot():
    claims = [{"id": str(i), "step": "1.1", "type": "SOURCED"} for i in range(4)]
    assert gates.evidence_gate(claims)["outcome"] == gates.PIVOT


def _phase1(product_demand):
    claims = [{"id": f"C1.1-{i}", "step": "1.1", "type": "SOURCED"} for i in range(3)]
    return claims + [{"id": "C1.4-1", "step": "1.4", "type": "SOURCED", "product_demand": product_demand}]


def test_demand_for_the_problem_only_means_dont_launch():
    g = gates.evidence_gate(_phase1(False))
    assert g["outcome"] == gates.STOP and any("don't launch this" in r for r in g["reasons"])


def test_demand_for_the_product_passes():
    assert gates.evidence_gate(_phase1(True))["outcome"] == gates.GO


def test_demo_input_is_labelled_everywhere(env):
    """A hypothetical 2.4 result is allowed only as a labelled DEMO INPUT, in the gate, step files and log."""
    from pathlib import Path
    from app import decision_log as dl
    from app.gates import DEMO_NOTE
    from tests.test_smoke import drive, start
    graph, cfg, res = start(env)
    res, _ = drive(graph, cfg, res, lambda p: {"actual": 150, "demo_input": True} if p["type"] == "enter_results"
                   else {"decision": "approve"})
    gate = next(g for g in res["gate_history"] if g["step"] == "2.4")
    assert gate["reasons"][0] == DEMO_NOTE
    later = sorted(Path(env["out"]).glob("phase[3-6]_step*.md"))
    assert later and all("DEMO INPUT" in p.read_text() for p in later)
    assert any(e.get("demo_input") for e in dl.entries())


def test_threshold_target_reads_fractions_and_never_locks_zero():
    import pytest
    from app.gates import lock_threshold
    from app.tools import threshold_target
    assert threshold_target(200, 0.05) == 10 and threshold_target(200, 5) == 10
    assert threshold_target(0, 5) == 0 and threshold_target("lots", 5) == 0
    with pytest.raises(ValueError):
        lock_threshold({}, {"target": 0})
