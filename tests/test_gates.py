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
