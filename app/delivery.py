"""Delivery (MOCKED): access to the digital product, granted per order and revoked on refund.

Only app/webhooks.py calls grant() and revoke(), after a verified provider webhook; a model never does.
Grants are keyed by order id, so a repeated webhook cannot deliver twice. The download link is a
MOCKED placeholder: nothing is actually hosted or sent.
"""
from __future__ import annotations

import secrets
import sqlite3

from app import payments


def grant(con: sqlite3.Connection, order_id: str) -> str:
    """Idempotent: a second grant for the same order returns the existing token."""
    con.execute("INSERT OR IGNORE INTO grants VALUES (?, ?, 'active')", (order_id, secrets.token_urlsafe(12)))
    return con.execute("SELECT token FROM grants WHERE order_id = ?", (order_id,)).fetchone()[0]


def revoke(con: sqlite3.Connection, order_id: str) -> bool:
    return con.execute("UPDATE grants SET status = 'revoked' WHERE order_id = ? AND status = 'active'",
                       (order_id,)).rowcount == 1


def download_link(token: str) -> str:
    return f"mock://download/{token} (MOCKED)"


def has_access(token: str) -> bool:
    with payments.db() as con:
        row = con.execute("SELECT status FROM grants WHERE token = ?", (token,)).fetchone()
    return bool(row and row[0] == "active")


def grants() -> list[dict]:
    with payments.db() as con:
        rows = con.execute("SELECT order_id, token, status FROM grants ORDER BY order_id").fetchall()
    return [dict(zip(("order_id", "token", "status"), r)) for r in rows]


def grant_for(order_id: str) -> dict | None:
    return next((g for g in grants() if g["order_id"] == order_id), None)
