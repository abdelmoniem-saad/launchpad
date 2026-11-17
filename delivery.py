"""Delivery: payment grants access to the digital product; a refund revokes it.

Access is keyed by order id, so granting twice for the same order is a no-op (idempotent).
The download link is MOCKED (a local token, no file host).
"""
from __future__ import annotations

import uuid


def grant_access(store, order: dict, log) -> dict:
    grants = store.data["grants"]
    if order["id"] in grants and grants[order["id"]]["active"]:
        log.append("delivery", "grant_access_skipped_already_active", order_id=order["id"])
        return grants[order["id"]]
    grant = {"token": f"dl_{uuid.uuid4().hex[:12]}", "active": True, "product": order["product"]}
    grants[order["id"]] = grant
    log.append("delivery", "grant_access", order_id=order["id"], mocked=True)
    return grant


def revoke_access(store, order: dict, log) -> None:
    grant = store.data["grants"].get(order["id"])
    if grant:
        grant["active"] = False
    log.append("delivery", "revoke_access", order_id=order["id"])


def has_access(store, order_id: str) -> bool:
    grant = store.data["grants"].get(order_id)
    return bool(grant and grant["active"])
