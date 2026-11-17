"""Reconciliation: match orders, payments, fees, refunds and (MOCKED) payouts; flag mismatches."""
from __future__ import annotations


def reconcile(store) -> dict:
    d = store.data
    rows, issues = [], []
    for oid, order in d["orders"].items():
        pay = d["payments"].get(oid)
        ref = d["refunds"].get(oid)
        gross = pay["amount_cents"] if pay else 0
        fee = pay["fee_cents"] if pay else 0
        refunded = ref["amount_cents"] if ref else 0
        net = gross - fee - refunded
        if order["status"] == "paid" and not pay:
            issues.append(f"{oid}: marked paid but no payment recorded")
        if pay and gross != order["amount_cents"]:
            issues.append(f"{oid}: paid {gross} != order amount {order['amount_cents']}")
        if order["status"] == "refunded" and d["grants"].get(oid, {}).get("active"):
            issues.append(f"{oid}: refunded but access still active")
        rows.append({"order_id": oid, "status": order["status"], "gross_cents": gross,
                     "fee_cents": fee, "refund_cents": refunded, "net_cents": net})
    payout = sum(r["net_cents"] for r in rows)  # MOCKED payout: provider would report this
    return {"rows": rows, "expected_payout_cents": payout, "mocked_payout_cents": payout,
            "issues": issues, "balanced": not issues}
