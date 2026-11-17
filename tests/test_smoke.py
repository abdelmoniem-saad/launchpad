"""Smoke tests: pipeline steps, gates, founder approval, and sale to cash. No model server needed."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gates  # noqa: E402
import orchestrator  # noqa: E402
import payments  # noqa: E402
import reconcile  # noqa: E402
import refunds  # noqa: E402
from agents import researcher  # noqa: E402
from approval import ApprovalRejected, reject_all, require_approval  # noqa: E402
from decision_log import REQUIRED_KEYS, DecisionLog  # noqa: E402
from delivery import has_access  # noqa: E402
from llm import LLMResult  # noqa: E402
from store import Store  # noqa: E402

SRC = "https://example.org/forum-thread"


def fake_llm(strong=True):
    def call(system, prompt):
        evidence = [{"claim": "people ask for this", "source": SRC},
                    {"claim": "made-up stat", "source": "https://not-in-sources.example"}]
        body = {"summary": "test", "details": {"landing_page_markdown": "A simple template."},
                "evidence": evidence if strong else [{"claim": "hunch", "source": "ASSUMPTION"}],
                "confidence": 0.8 if strong else 0.1, "pivot_suggestion": None}
        return LLMResult(text="<think>x</think>" + json.dumps(body), model="fake-model", tokens=10)
    return call


def approve_all(action, summary):
    return True


class Base(unittest.TestCase):
    def setUp(self):
        researcher.fetch_source = lambda url, limit=3000: "offline test text"  # no network in tests
        self.tmp = Path(tempfile.mkdtemp())
        self.log = DecisionLog(self.tmp / "log.json")
        self.out = self.tmp / "outputs"


class TestGates(Base):
    def test_weak_evidence_stops(self):
        self.assertEqual(gates.evaluate(1, {"evidence": [], "confidence": 0.9}).outcome, gates.STOP)

    def test_strong_evidence_goes(self):
        r = {"evidence": [{"claim": "a", "source": SRC}], "confidence": 0.7}
        self.assertEqual(gates.evaluate(1, r).outcome, gates.GO)

    def test_mixed_repeats_then_stops(self):
        r = {"evidence": [{"claim": "a", "source": SRC}, {"claim": "b", "source": "ASSUMPTION"},
                          {"claim": "c", "source": "ASSUMPTION"}], "confidence": 0.5}
        self.assertEqual(gates.evaluate(1, r, attempt=1).outcome, gates.REPEAT)
        self.assertEqual(gates.evaluate(1, r, attempt=2).outcome, gates.STOP)


class TestPipeline(Base):
    def test_full_run_writes_outputs_and_log(self):
        res = orchestrator.run_pipeline("templates for editors", fake_llm(), approve_all,
                                        self.log, self.out, [SRC])
        self.assertEqual(res["outcome"], "go")
        for n in range(1, 7):
            self.assertTrue(list(self.out.glob(f"phase{n}_step1_*.md")))
            self.assertTrue((self.out / f"phase{n}_gate_decision.md").exists())
        for entry in self.log.entries():
            for key in REQUIRED_KEYS:
                self.assertIn(key, entry)
        # citations not in the given sources are relabelled ASSUMPTION
        self.assertIn("ASSUMPTION", (self.out / "phase1_step1_opportunities.md").read_text("utf-8"))

    def test_weak_idea_stops_at_first_gate(self):
        res = orchestrator.run_pipeline("vague idea", fake_llm(strong=False), approve_all,
                                        self.log, self.out, [])
        self.assertEqual(res, {"outcome": "stop", "phase": 1})

    def test_disallowed_product_stops(self):
        res = orchestrator.run_pipeline("crypto trading signal bot", fake_llm(), approve_all,
                                        self.log, self.out, [SRC])
        self.assertEqual(res["outcome"], "stop")


class TestApproval(Base):
    def test_nothing_goes_out_without_approval(self):
        res = orchestrator.run_pipeline("templates for editors", fake_llm(), reject_all,
                                        self.log, self.out, [SRC])
        self.assertEqual(res, {"outcome": "founder_rejected", "phase": 4})
        self.assertFalse((self.out / "phase5_step1_landing_page.md").exists())
        self.assertFalse(any(e["approved_by"] == "founder" for e in self.log.entries()))

    def test_require_approval_raises_on_reject(self):
        with self.assertRaises(ApprovalRejected):
            require_approval("publish", "x", reject_all, self.log)

    def test_checkout_needs_approval(self):
        store = Store(self.tmp / "state.json")
        with self.assertRaises(ApprovalRejected):
            payments.create_checkout(store, "p", 1000, reject_all, self.log)
        self.assertEqual(store.data["orders"], {})


class TestSaleToCash(Base):
    def test_pay_deliver_once_refund_revokes_reconciles(self):
        store = Store(self.tmp / "state.json")
        order = payments.create_checkout(store, "p", 1900, approve_all, self.log)
        event = payments.simulate_payment(order)
        self.assertEqual(payments.handle_event(store, event, self.log), "processed")
        token = store.data["grants"][order["id"]]["token"]
        self.assertEqual(payments.handle_event(store, event, self.log), "duplicate")
        self.assertEqual(store.data["grants"][order["id"]]["token"], token)
        self.assertTrue(has_access(store, order["id"]))
        refunds.request_refund(store, order["id"], approve_all, self.log)
        self.assertFalse(has_access(store, order["id"]))
        rec = reconcile.reconcile(store)
        self.assertTrue(rec["balanced"], rec["issues"])
        self.assertEqual(rec["rows"][0]["net_cents"], -payments.simulate_payment(order)["fee_cents"])


if __name__ == "__main__":
    unittest.main()
