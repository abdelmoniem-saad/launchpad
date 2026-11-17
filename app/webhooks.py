"""Webhooks (MOCKED provider): the only path from a payment to delivery, and from a refund to revocation.

Each event is verified (HMAC signature), then recorded by event id in the same transaction as its
effect, so a replayed or duplicated webhook is ignored and can never deliver twice.
  payment.succeeded -> order paid, payment and fee booked, delivery granted
  refund.succeeded  -> order refunded, refund booked, delivery revoked
"""
from __future__ import annotations

import hmac
import json

from app import decision_log as dl
from app import delivery, payments

AGENT = "governance.webhooks"


def handle(body: str, signature: str) -> dict:
    if not hmac.compare_digest(payments.sign(body), signature or ""):
        dl.log(AGENT, "webhook_rejected: bad signature, nothing granted or revoked")
        return {"status": "rejected", "reason": "bad signature"}
    ev = json.loads(body)
    eid, type_, oid = ev["id"], ev["type"], ev["order_id"]
    with payments.db() as con:
        new = con.execute("INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?)",
                          (eid, type_, oid, payments._now())).rowcount == 1
        if not new:
            dl.log(AGENT, f"webhook_duplicate {eid} ({type_} {oid}): ignored, no second delivery")
            return {"status": "duplicate", "event_id": eid}
        if type_ == "payment.succeeded":
            con.execute("UPDATE orders SET status = 'paid' WHERE order_id = ?", (oid,))
            con.executemany("INSERT INTO ledger VALUES (?, ?, ?)",
                            [(oid, "payment", ev["amount_cents"]), (oid, "fee", ev["fee_cents"])])
            token = delivery.grant(con, oid)
            result = {"status": "processed", "event_id": eid, "granted": True, "token": token}
        elif type_ == "refund.succeeded":
            con.execute("UPDATE orders SET status = 'refunded' WHERE order_id = ?", (oid,))
            con.execute("INSERT INTO ledger VALUES (?, 'refund', ?)", (oid, ev["amount_cents"]))
            result = {"status": "processed", "event_id": eid, "revoked": delivery.revoke(con, oid)}
        else:
            result = {"status": "ignored", "event_id": eid, "reason": f"unhandled type {type_}"}
    dl.log(AGENT, f"webhook_{result['status']} {eid} ({type_} {oid})", mocked=True)
    return result
