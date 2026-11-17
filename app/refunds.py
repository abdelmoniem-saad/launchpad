"""Refunds (MOCKED): requested by Support, executed only after the founder approves.

The system never refunds money by itself. A refund is a `refund` action in the action gateway; it
runs only with the founder's one-time token. The provider (MOCKED) then sends `refund.succeeded`,
and the webhook revokes that order's access.
"""
from __future__ import annotations

from app import approval, payments, webhooks
from app import decision_log as dl


def request(run_dir: str, order_id: str, reason: str) -> str:
    o = payments.order(order_id)
    if not o or o["status"] != "paid":
        raise ValueError(f"{order_id} is not a paid order")
    payload = {"order_id": order_id, "amount_usd": o["amount_cents"] / 100,
               "draft": f"Refund order {order_id} (${o['amount_cents'] / 100:.2f}) and revoke its access (MOCKED provider)"}
    return approval.propose(run_dir, "5.2", "refund", payload, reason, "dept.support")


def execute(action_id: str, token: str | None, provider: payments.MockProvider) -> dict:
    """Raises approval.ApprovalRequired without the founder's token; nothing reaches the provider then."""
    approval.execute(action_id, token)
    a = next(x for x in approval.list_actions() if x["id"] == action_id)
    body, sig = provider.refund(a["payload"]["order_id"])
    dl.log("governance.refunds", f"refund_sent_to_provider {a['payload']['order_id']} via {action_id} (MOCKED)",
           approved_by="founder", mocked=True)
    return webhooks.handle(body, sig)
