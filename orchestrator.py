"""Orchestrator: runs the six phases in order with a gate after each.

Usage:
  python orchestrator.py run --idea "..." [--source URL ...] [--fresh-log]
  python orchestrator.py payment-test

Each phase writes outputs/phase<N>_step1_<name>.md and outputs/phase<N>_gate_decision.md.
Anything outbound (setting a price, publishing a page, creating a checkout link, refunding)
goes through approval.require_approval and does not happen without a founder "approve".
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import gates
from agents import analyst, builder, commercial, researcher, seller, validator
from approval import ApprovalRejected, cli_approver, require_approval
from decision_log import DecisionLog


@dataclass
class Phase:
    number: int
    name: str
    step: str
    agent: Callable
    approval_action: str | None = None


PHASES = [
    Phase(1, "discover", "opportunities", researcher.run),
    Phase(2, "validate", "validation", validator.run),
    Phase(3, "build", "product_spec", builder.run),
    Phase(4, "commercial", "offer", commercial.run, approval_action="approve_offer_and_price"),
    Phase(5, "sell", "landing_page", seller.run, approval_action="publish_landing_page"),
    Phase(6, "operate", "learnings", analyst.run),
]


def render(phase: Phase, result: dict) -> str:
    lines = [f"# Phase {phase.number} ({phase.name}): {phase.step.replace('_', ' ')}", "",
             str(result.get("summary", "")), "", "## Evidence", "",
             "| Claim | Source |", "|---|---|"]
    for e in result.get("evidence", []):
        claim = str(e.get("claim", "")).replace("|", "/")
        lines.append(f"| {claim} | {e.get('source', 'ASSUMPTION')} |")
    lines += ["", f"Confidence: {result.get('confidence')}", "", "## Details", "",
              "```json", json.dumps(result.get("details", {}), indent=2), "```", ""]
    return "\n".join(lines)


def render_gate(d: gates.GateDecision) -> str:
    return "\n".join([f"# Phase {d.phase} gate decision", "", f"**Outcome: {d.outcome.upper()}**", "",
                      *[f"- {r}" for r in d.reasons], ""])


def run_pipeline(idea: str, llm, approver, log: DecisionLog, out_dir: Path,
                 sources: list[str] | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    context: dict = {"idea": idea, "sources": sources or []}
    log.append("orchestrator", "start_run", sources=sources or [])
    for phase in PHASES:
        attempt = 1
        while True:
            result = phase.agent(context, llm, log)
            decision = gates.evaluate(phase.number, result, attempt=attempt)
            log.append("gate", f"phase{phase.number}_gate", outcome=decision.outcome,
                       sourced_ratio=round(decision.sourced_ratio, 2), confidence=decision.confidence)
            if decision.outcome != gates.REPEAT:
                break
            attempt += 1
            context["gate_feedback"] = decision.reasons
        (out_dir / f"phase{phase.number}_step1_{phase.step}.md").write_text(render(phase, result), "utf-8")
        (out_dir / f"phase{phase.number}_gate_decision.md").write_text(render_gate(decision), "utf-8")
        if decision.outcome != gates.GO:
            log.append("orchestrator", "end_run", outcome=decision.outcome, phase=phase.number)
            return {"outcome": decision.outcome, "phase": phase.number}
        if phase.approval_action:
            try:
                require_approval(phase.approval_action, str(result.get("summary", "")), approver, log,
                                 agent=phase.name)
            except ApprovalRejected:
                log.append("orchestrator", "end_run", outcome="founder_rejected", phase=phase.number)
                return {"outcome": "founder_rejected", "phase": phase.number}
            log.append(phase.name, f"{phase.approval_action}_done", approved_by="founder",
                       mocked=phase.approval_action == "publish_landing_page")
        context[phase.name] = {"summary": result.get("summary"), "details": result.get("details")}
        context.pop("gate_feedback", None)
    log.append("orchestrator", "end_run", outcome="go", phase=len(PHASES))
    return {"outcome": "go", "phase": len(PHASES)}


def payment_test(approver, log: DecisionLog, out_dir: Path) -> dict:
    """MOCKED sale-to-cash run: checkout, payment, duplicate webhook, refund, reconciliation."""
    import payments
    import reconcile
    import refunds
    from delivery import has_access
    from store import Store

    store = Store()
    order = payments.create_checkout(store, "demo digital product", 1900, approver, log)
    event = payments.simulate_payment(order)
    first = payments.handle_event(store, event, log)
    second = payments.handle_event(store, event, log)
    access_after_pay = has_access(store, order["id"])
    refund = refunds.request_refund(store, order["id"], approver, log, reason="payment test")
    access_after_refund = has_access(store, order["id"])
    rec = reconcile.reconcile(store)
    report = "\n".join([
        "# Payment test log (MOCKED provider, no real money)", "",
        f"- Order: {order['id']} for ${order['amount_cents'] / 100:.2f}",
        f"- First webhook: {first}; repeated webhook: {second}",
        f"- Access after payment: {access_after_pay}",
        f"- Refund: {refund}; access after refund: {access_after_refund}",
        f"- Reconciliation balanced: {rec['balanced']}", "",
        "```json", json.dumps(rec, indent=2), "```", ""])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "payment_test_log.md").write_text(report, "utf-8")
    return rec


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="launchpad: agent team from idea to sellable digital product")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run the six-phase pipeline for an idea")
    r.add_argument("--idea", required=True)
    r.add_argument("--source", action="append", default=[], help="source URL the agents may cite")
    r.add_argument("--fresh-log", action="store_true", help="clear decision_log.json first")
    sub.add_parser("payment-test", help="MOCKED checkout, delivery, refund and reconciliation run")
    args = p.parse_args(argv)

    log = DecisionLog()
    out_dir = Path(os.environ.get("OUTPUT_DIR", "outputs"))
    if args.cmd == "run":
        from llm import OllamaLLM
        if args.fresh_log:
            log.reset()
        result = run_pipeline(args.idea, OllamaLLM(), cli_approver, log, out_dir, args.source)
    else:
        result = payment_test(cli_approver, log, out_dir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
