"""Reconciliation: orders, payments, fees, refunds and payouts, matched per order.

Our ledger (built only from verified webhooks) is compared with the provider's payout report, and
access is checked against order status. Any difference is listed for the founder; nothing is
corrected automatically.
"""
from __future__ import annotations

from app import decision_log as dl
from app import payments


def reconcile(provider_report: dict) -> dict:
    with payments.db() as con:
        orders = con.execute("SELECT order_id, amount_cents, status FROM orders ORDER BY created, order_id").fetchall()
        led = con.execute("SELECT order_id, kind, SUM(cents) FROM ledger GROUP BY order_id, kind").fetchall()
        grants = dict(con.execute("SELECT order_id, status FROM grants").fetchall())
    book: dict = {}
    for oid, kind, cents in led:
        book.setdefault(oid, {})[kind] = cents
    rows, mismatches = [], []
    for oid, amount, status in orders:
        b = book.get(oid, {})
        pay, fee, ref = b.get("payment", 0), b.get("fee", 0), b.get("refund", 0)
        access = grants.get(oid, "none")
        rows.append({"order_id": oid, "status": status, "gross_cents": pay, "fee_cents": fee,
                     "refund_cents": ref, "net_cents": pay - fee - ref, "access": access})
        if status in ("paid", "refunded") and pay != amount:
            mismatches.append(f"{oid}: paid {pay} cents but the order is {amount} cents")
        expected_access = {"paid": "active", "refunded": "revoked"}.get(status, "none")
        if access != expected_access:
            mismatches.append(f"{oid}: order is {status} but access is {access} (expected {expected_access})")
    expected = {"gross_cents": sum(r["gross_cents"] for r in rows), "fees_cents": sum(r["fee_cents"] for r in rows),
                "refunds_cents": sum(r["refund_cents"] for r in rows)}
    expected["payout_cents"] = expected["gross_cents"] - expected["fees_cents"] - expected["refunds_cents"]
    for k, v in expected.items():
        if provider_report.get(k) != v:
            mismatches.append(f"{k}: our ledger {v} cents, provider report {provider_report.get(k)} cents")
    dl.log("governance.reconcile", f"reconcile {len(rows)} orders: {'match' if not mismatches else f'{len(mismatches)} mismatch(es)'}",
           mocked=True)
    return {"orders": rows, "expected": expected, "reported": provider_report, "mismatches": mismatches,
            "ok": not mismatches}
