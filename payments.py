"""Payments. MOCKED: no real provider is called and no money moves.

The mock follows a test-mode provider's shape: a checkout link per order, then signed-style
webhook events (`payment.succeeded`, `refund.succeeded`) that drive delivery and revocation.
Event handling is idempotent: a repeated event id is ignored, so access is never granted twice.
"""
from __future__ import annotations

import uuid

import delivery
from approval import require_approval

MOCKED = True
FEE_PERCENT, FEE_FIXED_CENTS = 0.029, 30  # MOCKED fee schedule, typical card-processor shape


def create_checkout(store, product: str, price_cents: int, approver, log) -> dict:
    """Create a checkout link. Needs founder approval: it is what customers will pay through."""
    approved_by = require_approval("create_checkout_link",
                                   f"Product: {product}\nPrice: ${price_cents / 100:.2f}\nMode: MOCKED sandbox",
                                   approver, log, agent="payments")
    order_id = f"ord_{uuid.uuid4().hex[:10]}"
    order = {"id": order_id, "product": product, "amount_cents": price_cents, "status": "open",
             "checkout_url": f"mock://checkout/{order_id}"}
    store.data["orders"][order_id] = order
    store.save()
    log.append("payments", "create_checkout_link", approved_by=approved_by, mocked=True, order_id=order_id)
    return order


def simulate_payment(order: dict) -> dict:
    """MOCKED: what the provider's webhook would send after a test-card payment."""
    fee = round(order["amount_cents"] * FEE_PERCENT) + FEE_FIXED_CENTS
    return {"id": f"evt_{uuid.uuid4().hex[:10]}", "type": "payment.succeeded",
            "order_id": order["id"], "amount_cents": order["amount_cents"], "fee_cents": fee}


def handle_event(store, event: dict, log) -> str:
    """Webhook handler. Returns "processed" or "duplicate"."""
    if event["id"] in store.data["processed_events"]:
        log.append("webhooks", f"ignore_duplicate:{event['type']}", event_id=event["id"])
        return "duplicate"
    order = store.data["orders"][event["order_id"]]
    if event["type"] == "payment.succeeded":
        store.data["payments"][order["id"]] = {"amount_cents": event["amount_cents"],
                                               "fee_cents": event["fee_cents"], "event_id": event["id"]}
        order["status"] = "paid"
        delivery.grant_access(store, order, log)
    elif event["type"] == "refund.succeeded":
        store.data["refunds"][order["id"]] = {"amount_cents": event["amount_cents"], "event_id": event["id"]}
        order["status"] = "refunded"
        delivery.revoke_access(store, order, log)
    store.data["processed_events"].append(event["id"])
    store.save()
    log.append("webhooks", f"process:{event['type']}", event_id=event["id"], order_id=order["id"], mocked=True)
    return "processed"
