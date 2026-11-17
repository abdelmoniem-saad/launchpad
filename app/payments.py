"""Payments (MOCKED): store, checkout and a mock payment provider. No real money and no card data.

Flow: the founder opens the store through the action gateway (a `publish` action that only runs with
the founder's one-time token). A buyer checks out; payment happens on the provider's side, so this code
never sees card details. The provider then sends a signed webhook (app/webhooks.py), and only that
webhook grants delivery (app/delivery.py). Refunds go through app/refunds.py, again founder-approved.

MOCKED: `MockProvider` is an in-process simulation of a payment provider; no real or sandbox payment system is ever contacted. Its fee schedule
(2.9% + $0.30 per payment, not returned on refund) is an ASSUMPTION used only by the mock. Amounts are
integer cents. Buyers are stored as an opaque reference, never a name, email or card number.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app import approval
from app import decision_log as dl

AGENT = "governance.payments"
PROVIDER_NAME = "MOCKED payment provider (simulated, in-process)"
FEE_PCT, FEE_FIXED_CENTS = 0.029, 30  # ASSUMPTION: typical card fee, used only by the mock
_CARD_LIKE = re.compile(r"(?:\d[ -]?){13,19}")
_SECRET = os.environ.get("MOCK_WEBHOOK_SECRET") or secrets.token_hex(16)

SCHEMA = """
CREATE TABLE IF NOT EXISTS store (id INTEGER PRIMARY KEY CHECK (id = 1), product TEXT, price_cents INTEGER, action_id TEXT);
CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, buyer_ref TEXT, amount_cents INTEGER, status TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, type TEXT, order_id TEXT, processed_at TEXT);
CREATE TABLE IF NOT EXISTS grants (order_id TEXT PRIMARY KEY, token TEXT UNIQUE, status TEXT);
CREATE TABLE IF NOT EXISTS ledger (order_id TEXT, kind TEXT, cents INTEGER);
CREATE TABLE IF NOT EXISTS provider_ledger (order_id TEXT, kind TEXT, cents INTEGER);
"""


class StoreNotOpen(Exception):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def db() -> sqlite3.Connection:
    path = Path(os.environ.get("STATE_DIR", "data")) / "sales.sqlite"
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con


def reset() -> None:
    """Start a clean sales ledger (used by the payment test run)."""
    with db() as con:
        for t in ("store", "orders", "events", "grants", "ledger", "provider_ledger"):
            con.execute(f"DELETE FROM {t}")


def propose_store(run_dir: str, product: str, price_usd: float) -> str:
    """Opening the store is a `publish` action: it waits for the founder's approval."""
    payload = {"kind": "open_store", "product": product, "price_usd": round(float(price_usd), 2),
               "draft": f"Open the store for '{product}' at ${float(price_usd):.2f} (MOCKED provider, simulated)"}
    return approval.propose(run_dir, "5.1", "publish", payload, "Open the store so buyers can check out", "dept.sales")


def open_store(action_id: str, token: str | None) -> dict:
    """Runs only with the founder's one-time token; raises approval.ApprovalRequired otherwise."""
    approval.execute(action_id, token)
    a = next(x for x in approval.list_actions() if x["id"] == action_id)
    product, cents = a["payload"]["product"], round(a["payload"]["price_usd"] * 100)
    with db() as con:
        con.execute("INSERT OR REPLACE INTO store VALUES (1, ?, ?, ?)", (product, cents, action_id))
    dl.log(AGENT, f"store_open (MOCKED) '{product}' at {cents} cents via {action_id}", approved_by="founder", mocked=True)
    return {"product": product, "price_cents": cents}


def store() -> dict | None:
    with db() as con:
        row = con.execute("SELECT product, price_cents, action_id FROM store WHERE id = 1").fetchone()
    return {"product": row[0], "price_cents": row[1], "action_id": row[2]} if row else None


def checkout(buyer_ref: str) -> str:
    """Create a pending order. Card details are never accepted: the provider's hosted page collects payment."""
    if _CARD_LIKE.search(buyer_ref or "") or "@" in (buyer_ref or ""):
        dl.log(AGENT, "checkout_rejected: buyer reference looked like a card number or email; only opaque ids are stored")
        raise ValueError("buyer_ref must be an opaque id: no card numbers or personal data")
    s = store()
    if not s:
        dl.log(AGENT, "checkout_blocked: store not opened by the founder")
        raise StoreNotOpen("the founder has not approved opening the store")
    oid = f"ord_{uuid.uuid4().hex[:8]}"
    with db() as con:
        con.execute("INSERT INTO orders VALUES (?, ?, ?, 'pending', ?)", (oid, buyer_ref, s["price_cents"], _now()))
    dl.log(AGENT, f"checkout_created {oid} {s['price_cents']} cents (MOCKED)", mocked=True)
    return oid


def order(order_id: str) -> dict | None:
    with db() as con:
        row = con.execute("SELECT order_id, buyer_ref, amount_cents, status FROM orders WHERE order_id = ?",
                          (order_id,)).fetchone()
    return dict(zip(("order_id", "buyer_ref", "amount_cents", "status"), row)) if row else None


def sign(body: str) -> str:
    return hmac.new(_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()


class MockProvider:
    """MOCKED payment provider (in-process simulation). It keeps its own ledger, which reconciliation checks against ours."""

    name = PROVIDER_NAME

    @staticmethod
    def fee(amount_cents: int) -> int:
        return round(amount_cents * FEE_PCT) + FEE_FIXED_CENTS

    def _event(self, type_: str, order_id: str, **data) -> tuple[str, str]:
        body = json.dumps({"id": f"evt_{uuid.uuid4().hex[:10]}", "type": type_, "order_id": order_id, **data},
                          sort_keys=True)
        return body, sign(body)

    def pay(self, order_id: str) -> tuple[str, str]:
        """The buyer completes payment on the provider's page. Returns the signed webhook (body, signature)."""
        o = order(order_id)
        if not o:
            raise KeyError(order_id)
        with db() as con:
            if con.execute("SELECT 1 FROM provider_ledger WHERE order_id = ? AND kind = 'payment'", (order_id,)).fetchone():
                raise ValueError(f"{order_id} is already paid at the provider")
            fee = self.fee(o["amount_cents"])
            con.executemany("INSERT INTO provider_ledger VALUES (?, ?, ?)",
                            [(order_id, "payment", o["amount_cents"]), (order_id, "fee", fee)])
        return self._event("payment.succeeded", order_id, amount_cents=o["amount_cents"], fee_cents=fee)

    def refund(self, order_id: str) -> tuple[str, str]:
        """Called only by app/refunds.py after the founder approved that refund."""
        o = order(order_id)
        with db() as con:
            paid = con.execute("SELECT cents FROM provider_ledger WHERE order_id = ? AND kind = 'payment'",
                               (order_id,)).fetchone()
            if not paid:
                raise ValueError(f"{order_id} has no payment to refund")
            if con.execute("SELECT 1 FROM provider_ledger WHERE order_id = ? AND kind = 'refund'", (order_id,)).fetchone():
                raise ValueError(f"{order_id} is already refunded at the provider")
            con.execute("INSERT INTO provider_ledger VALUES (?, 'refund', ?)", (order_id, paid[0]))
        return self._event("refund.succeeded", order_id, amount_cents=o["amount_cents"])

    def payout_report(self) -> dict:
        with db() as con:
            rows = con.execute("SELECT kind, SUM(cents) FROM provider_ledger GROUP BY kind").fetchall()
        t = {k: v for k, v in rows}
        gross, fees, refunds = t.get("payment", 0), t.get("fee", 0), t.get("refund", 0)
        return {"gross_cents": gross, "fees_cents": fees, "refunds_cents": refunds,
                "payout_cents": gross - fees - refunds}
