"""Payment and delivery test run (MOCKED provider) -> outputs/payment_test_log.md

  python -m app.payment_test [--product NAME] [--price 19] [--out outputs]

Runs the whole sale-to-cash path against the MOCKED payment provider. The founder approves opening
the store and the refund at the prompts (one-time tokens, the same action gateway as the main
pipeline). No real money moves and no card data is used. The log records what actually happened.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from app import approval, delivery, payments, reconcile, refunds, webhooks
from app.cli import ask


def usd(cents: int | None) -> str:
    return "n/a" if cents is None else f"{'-' if cents < 0 else ''}${abs(cents) / 100:,.2f}"


def founder_ok(prompt: str) -> bool:
    return ask(f"{prompt} Type 'approve' to approve, anything else rejects: ").lower() == "approve"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--product", default="Revision tracker Notion template pack")
    ap.add_argument("--price", type=float, default=19.0, help="price in USD the founder sets")
    ap.add_argument("--out", default="outputs")
    args = ap.parse_args(argv)

    payments.reset()
    provider = payments.MockProvider()
    checks: list[tuple[str, str, str, bool]] = []

    def check(name: str, expected: str, got: str, ok: bool) -> None:
        checks.append((name, expected, got, ok))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {got}")

    # 1. Checkout before the founder opened the store
    try:
        payments.checkout("buyer-001")
        check("Checkout before the store is approved", "blocked", "allowed", False)
    except payments.StoreNotOpen:
        check("Checkout before the store is approved", "blocked", "blocked (store not open)", True)

    # 2. Opening the store without the founder's token
    store_action = payments.propose_store(args.out, args.product, args.price)
    try:
        payments.open_store(store_action, None)
        check("Open the store without founder approval", "blocked", "opened", False)
    except approval.ApprovalRequired:
        check("Open the store without founder approval", "blocked", "blocked (no founder token)", True)

    # 3. Founder decision on the same pending action
    print(f"\nACTION {store_action}: open the store for '{args.product}' at ${args.price:.2f} (MOCKED provider)")
    if not founder_ok("  Founder:"):
        approval.founder_reject(store_action)
        check("Founder decision on opening the store", "approve", "rejected: run stops here", False)
        return write_log(args, provider, checks, None, stopped="The founder rejected opening the store.")
    s = payments.open_store(store_action, approval.founder_approve(store_action))
    check("Founder decision on opening the store", "approve", f"approved, store open at {usd(s['price_cents'])}", True)

    # 4. Card data is never accepted
    try:
        payments.checkout("4111 1111 1111 1111")
        check("Card number offered at checkout", "rejected", "accepted", False)
    except ValueError:
        check("Card number offered at checkout", "rejected", "rejected (opaque buyer ids only)", True)

    # 5. Two buyers pay; the verified webhook grants delivery
    o1, o2 = payments.checkout("buyer-001"), payments.checkout("buyer-002")
    pending = delivery.grant_for(o1)
    check("Access before payment", "none", "none" if pending is None else pending["status"], pending is None)
    body1, sig1 = provider.pay(o1)
    r1 = webhooks.handle(body1, sig1)
    check("Payment webhook grants delivery", "access granted", f"{r1['status']}, link {delivery.download_link(r1.get('token', ''))}",
          r1.get("granted") is True and delivery.has_access(r1["token"]))
    body2, sig2 = provider.pay(o2)
    r2 = webhooks.handle(body2, sig2)
    check("Second order paid and delivered", "access granted", r2["status"], r2.get("granted") is True)

    # 6. Idempotency: the same webhook delivered again
    again = webhooks.handle(body1, sig1)
    n = sum(1 for g in delivery.grants() if g["order_id"] == o1)
    check("Same payment webhook delivered twice", "ignored, one grant", f"{again['status']}, {n} grant(s)",
          again["status"] == "duplicate" and n == 1)

    # 7. A forged webhook (bad signature) for an unpaid order
    o3 = payments.checkout("buyer-003")
    forged = json.dumps({"id": "evt_forged", "type": "payment.succeeded", "order_id": o3, "amount_cents": 1, "fee_cents": 0})
    rf = webhooks.handle(forged, "not-a-valid-signature")
    check("Forged payment webhook", "rejected, no access", f"{rf['status']}, access {delivery.grant_for(o3) or 'none'}",
          rf["status"] == "rejected" and delivery.grant_for(o3) is None)

    # 8. Refund: blocked without the founder, then the founder decides
    ref_action = refunds.request(args.out, o2, "Buyer buyer-002 asked for a refund within the refund window")
    try:
        refunds.execute(ref_action, None, provider)
        check("Refund without founder approval", "blocked", "refunded", False)
    except approval.ApprovalRequired:
        check("Refund without founder approval", "blocked", "blocked (no founder token)", True)
    token2 = delivery.grant_for(o2)["token"]
    print(f"\nACTION {ref_action}: refund order {o2} ({usd(payments.order(o2)['amount_cents'])}) and revoke its access")
    if founder_ok("  Founder:"):
        rr = refunds.execute(ref_action, approval.founder_approve(ref_action), provider)
        check("Founder-approved refund revokes access", "refunded, access revoked",
              f"{rr['status']}, access {'active' if delivery.has_access(token2) else 'revoked'}",
              rr.get("revoked") is True and not delivery.has_access(token2))
    else:
        approval.founder_reject(ref_action)
        check("Founder decision on the refund", "founder's choice", "rejected: no refund, access kept",
              delivery.has_access(token2))

    # 9. Reconciliation against the provider's payout report
    rec = reconcile.reconcile(provider.payout_report())
    check("Reconciliation: orders, payments, fees, refunds, payout", "match",
          "match" if rec["ok"] else "; ".join(rec["mismatches"]), rec["ok"])

    # 10. Reconciliation catches a difference (a test-injected 100-cent gap in the payout report)
    tampered = {**provider.payout_report()}
    tampered["payout_cents"] -= 100
    bad = reconcile.reconcile(tampered)
    check("Reconciliation with a test-injected $1.00 payout gap", "mismatch flagged",
          "; ".join(bad["mismatches"]) or "not flagged", not bad["ok"])

    return write_log(args, provider, checks, rec)


def write_log(args, provider, checks, rec, stopped: str = "") -> int:
    lines = ["# Payment and delivery test log (MOCKED)", "",
             f"Run: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} with `python -m app.payment_test`.",
             f"Provider: {provider.name}. Fee schedule 2.9% + $0.30 per payment is an ASSUMPTION used only by the mock.",
             "No real money moved, no card data was used, and the download links are MOCKED placeholders. "
             "Opening the store and the refund were decided by the founder at the prompt.", "",
             f"Product: {args.product}, price set by the founder: ${args.price:.2f}", "",
             f"**Result: {sum(c[3] for c in checks)}/{len(checks)} checks passed.**", "",
             "| # | Check | Expected | Result | |", "|---|---|---|---|---|"]
    lines += [f"| {i} | {n} | {e} | {g} | {'PASS' if ok else 'FAIL'} |" for i, (n, e, g, ok) in enumerate(checks, 1)]
    if stopped:
        lines += ["", stopped]
    if rec:
        lines += ["", "## Reconciliation", "", "| Order | Status | Gross | Fee | Refund | Net | Access |", "|---|---|---|---|---|---|---|"]
        lines += [f"| {r['order_id']} | {r['status']} | {usd(r['gross_cents'])} | {usd(r['fee_cents'])} | {usd(r['refund_cents'])} "
                  f"| {usd(r['net_cents'])} | {r['access']} |" for r in rec["orders"]]
        e, p = rec["expected"], rec["reported"]
        lines += ["", "| Total | Our ledger | Provider payout report |", "|---|---|---|"]
        lines += [f"| {k.replace('_cents', '')} | {usd(e[k])} | {usd(p.get(k))} |" for k in e]
        lines += ["", "Mismatches: " + ("none" if rec["ok"] else "; ".join(rec["mismatches"]))]
    out = Path(args.out) / "payment_test_log.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", "utf-8")
    print(f"\nWrote {out}")
    return 0 if all(c[3] for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
