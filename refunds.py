"""Refunds. The system never refunds by itself: the founder approves each one. MOCKED provider."""
from __future__ import annotations

import uuid

import payments
from approval import require_approval


def request_refund(store, order_id: str, approver, log, reason: str = "") -> str:
    order = store.data["orders"][order_id]
    paid = store.data["payments"].get(order_id)
    if not paid:
        raise ValueError(f"order {order_id} has no payment to refund")
    require_approval("issue_refund",
                     f"Order: {order_id}\nAmount: ${paid['amount_cents'] / 100:.2f}\nReason: {reason or '-'}\nMode: MOCKED",
                     approver, log, agent="refunds")
    event = {"id": f"evt_{uuid.uuid4().hex[:10]}", "type": "refund.succeeded",
             "order_id": order_id, "amount_cents": paid["amount_cents"]}
    return payments.handle_event(store, event, log)
