"""Sale to cash (MOCKED provider): payment triggers delivery, a refund revokes access, duplicate
webhooks cannot deliver twice, nothing happens without the founder, and reconciliation matches."""
import json

import pytest

from app import approval, delivery, payments, reconcile, refunds, webhooks
from app import decision_log as dl


@pytest.fixture
def shop(env):
    payments.reset()
    aid = payments.propose_store(env["out"], "Template pack", 19)
    payments.open_store(aid, approval.founder_approve(aid))
    return {"out": env["out"], "provider": payments.MockProvider()}


def paid_order(shop, buyer="buyer-1"):
    oid = payments.checkout(buyer)
    body, sig = shop["provider"].pay(oid)
    return oid, body, sig, webhooks.handle(body, sig)


def test_store_needs_founder_token(env):
    payments.reset()
    with pytest.raises(payments.StoreNotOpen):
        payments.checkout("buyer-1")
    aid = payments.propose_store(env["out"], "Template pack", 19)
    with pytest.raises(approval.ApprovalRequired):
        payments.open_store(aid, None)
    with pytest.raises(approval.ApprovalRequired):
        payments.open_store(aid, "guessed-token")
    assert payments.store() is None


def test_payment_webhook_grants_delivery_once(shop):
    oid, body, sig, res = paid_order(shop)
    assert res["granted"] and delivery.has_access(res["token"])
    assert payments.order(oid)["status"] == "paid"
    assert webhooks.handle(body, sig)["status"] == "duplicate"
    assert [g["order_id"] for g in delivery.grants()].count(oid) == 1


def test_no_access_before_payment_or_with_forged_webhook(shop):
    oid = payments.checkout("buyer-2")
    assert delivery.grant_for(oid) is None
    forged = json.dumps({"id": "evt_x", "type": "payment.succeeded", "order_id": oid, "amount_cents": 1, "fee_cents": 0})
    assert webhooks.handle(forged, "bad")["status"] == "rejected"
    assert delivery.grant_for(oid) is None and payments.order(oid)["status"] == "pending"


def test_refund_needs_founder_and_revokes_access(shop):
    oid, _, _, res = paid_order(shop)
    aid = refunds.request(shop["out"], oid, "buyer asked")
    with pytest.raises(approval.ApprovalRequired):
        refunds.execute(aid, None, shop["provider"])
    assert delivery.has_access(res["token"])
    out = refunds.execute(aid, approval.founder_approve(aid), shop["provider"])
    assert out["revoked"] and not delivery.has_access(res["token"])
    assert payments.order(oid)["status"] == "refunded"
    with pytest.raises(approval.ApprovalRequired):  # the one-time token cannot be reused
        refunds.execute(aid, "reuse", shop["provider"])
    assert any(e["approved_by"] == "founder" and "refund" in e["action"] for e in dl.entries())


def test_card_data_and_emails_never_accepted(shop):
    for bad in ("4111 1111 1111 1111", "someone@example.com"):
        with pytest.raises(ValueError):
            payments.checkout(bad)


def test_reconciliation_matches_and_flags_gaps(shop):
    paid_order(shop, "buyer-1")
    oid2, _, _, _ = paid_order(shop, "buyer-2")
    aid = refunds.request(shop["out"], oid2, "buyer asked")
    refunds.execute(aid, approval.founder_approve(aid), shop["provider"])
    report = shop["provider"].payout_report()
    rec = reconcile.reconcile(report)
    assert rec["ok"], rec["mismatches"]
    fee = payments.MockProvider.fee(1900)
    assert rec["expected"]["payout_cents"] == 1900 * 2 - 2 * fee - 1900
    assert not reconcile.reconcile({**report, "payout_cents": report["payout_cents"] - 100})["ok"]


def test_log_entries_have_required_keys(shop):
    paid_order(shop)
    for e in dl.entries():
        assert all(k in e for k in dl.REQUIRED_KEYS)
