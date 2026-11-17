# Payment and delivery test log (MOCKED)

Run: 2026-11-17T19:39:44Z with `python -m app.payment_test`.
Provider: MOCKED payment provider (test mode, in-process). Fee schedule 2.9% + $0.30 per payment is an ASSUMPTION used only by the mock.
No real money moved, no card data was used, and the download links are MOCKED placeholders. Opening the store and the refund were decided by the founder at the prompt.

Product: Revision tracker Notion template pack, price set by the founder: $19.00

**Result: 13/13 checks passed.**

| # | Check | Expected | Result | |
|---|---|---|---|---|
| 1 | Checkout before the store is approved | blocked | blocked (store not open) | PASS |
| 2 | Open the store without founder approval | blocked | blocked (no founder token) | PASS |
| 3 | Founder decision on opening the store | approve | approved, store open at $19.00 | PASS |
| 4 | Card number offered at checkout | rejected | rejected (opaque buyer ids only) | PASS |
| 5 | Access before payment | none | none | PASS |
| 6 | Payment webhook grants delivery | access granted | processed, link mock://download/3UirxmatyrrgLAzD (MOCKED) | PASS |
| 7 | Second order paid and delivered | access granted | processed | PASS |
| 8 | Same payment webhook delivered twice | ignored, one grant | duplicate, 1 grant(s) | PASS |
| 9 | Forged payment webhook | rejected, no access | rejected, access none | PASS |
| 10 | Refund without founder approval | blocked | blocked (no founder token) | PASS |
| 11 | Founder-approved refund revokes access | refunded, access revoked | processed, access revoked | PASS |
| 12 | Reconciliation: orders, payments, fees, refunds, payout | match | match | PASS |
| 13 | Reconciliation with a test-injected $1.00 payout gap | mismatch flagged | payout_cents: our ledger 1730 cents, provider report 1630 cents | PASS |

## Reconciliation

| Order | Status | Gross | Fee | Refund | Net | Access |
|---|---|---|---|---|---|---|
| ord_4d0c80f8 | paid | $19.00 | $0.85 | $0.00 | $18.15 | active |
| ord_ad9c6766 | refunded | $19.00 | $0.85 | $19.00 | -$0.85 | revoked |
| ord_f0fe5880 | pending | $0.00 | $0.00 | $0.00 | $0.00 | none |

| Total | Our ledger | Provider payout report |
|---|---|---|
| gross | $38.00 | $38.00 |
| fees | $1.70 | $1.70 |
| refunds | $19.00 | $19.00 |
| payout | $17.30 | $17.30 |

Mismatches: none
