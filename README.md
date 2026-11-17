# launchpad

An open-source team of AI agents that takes a founder's idea toward a validated, sellable **digital** product, in six phases with a gate after each: Discover, Validate, Build, Commercial setup, Sell/deliver/get paid, and Operate and learn. It runs on a local open-weight model, costs nothing per run, and does nothing outbound without the founder's explicit approval.

## Quickstart

```bash
docker compose up
```

This starts Ollama and pulls the model (`qwen3:8b`, first run only). Then, in a second terminal, run the pipeline for an idea (the founder approves or rejects each outbound step at the prompt):

```bash
docker compose run --rm app run --idea "Notion templates for freelance video editors" --source https://www.reddit.com/r/editors/
```

Results land in `outputs/` and every agent action is appended to `decision_log.json`. The sale-to-cash flow (MOCKED payments) runs with:

```bash
docker compose run --rm app payment-test
```

Without Docker: install [Ollama](https://ollama.com), run `ollama pull qwen3:8b`, then `python orchestrator.py run --idea "..."` (Python 3.11+, standard library only).

## What works and what is mocked

| Step | Status |
|---|---|
| Phase 1 Discover: researcher reads founder-given sources, ranks opportunities | Working |
| Phase 2 Validate: demand, competitors, willingness to pay | Working |
| Phase 3 Build: MVP spec and first deliverable outline | Working |
| Phase 4 Commercial setup: price, offer, refund policy (founder approves) | Working |
| Phase 5 Sell: landing-page copy with content guardrails (founder approves) | Working |
| Phase 5 Publishing the landing page | **MOCKED** (approval is recorded; nothing is posted) |
| Phase 5 Checkout, payment webhooks, fees | **MOCKED** (no provider called, no money moves) |
| Phase 5 Delivery: payment grants access, idempotent | Working (download link **MOCKED**) |
| Phase 5 Refund revokes access (founder approves) | Working on **MOCKED** payments |
| Phase 5 Reconciliation of orders, payments, fees, refunds | Working; payouts **MOCKED** |
| Phase 6 Operate and learn: analyst recommendations | Working |
| Gates (go / repeat / pivot / stop) after every phase | Working |
| Founder approve/reject, enforced in code (CLI) | Working |
| Web search beyond founder-given URLs | **STUBBED** (claims without a source are labelled `ASSUMPTION`) |

## Architecture

A Python orchestrator ([orchestrator.py](orchestrator.py)) runs six agents in order, one per phase ([agents/](agents/)), each with its own prompt in [prompts/](prompts/). After every phase, [gates.py](gates.py) scores the evidence (share of claims with a source URL, and agent confidence) and returns go, repeat, pivot or stop; weak evidence leads to STOP. Outbound actions pass through [approval.py](approval.py), which raises unless the founder types `approve`. Payments, delivery, refunds and reconciliation live in [payments.py](payments.py), [delivery.py](delivery.py), [refunds.py](refunds.py) and [reconcile.py](reconcile.py). See [ARCHITECTURE.md](ARCHITECTURE.md).

## Models and free resources

- Model: **`qwen3:8b`** (open weights) served locally by **Ollama**. Change it with `LLM_MODEL` in `.env` (for example `llama3.1:8b` or `qwen3:4b` on smaller machines).
- No paid API, account or key is needed. The runtime uses only the Python standard library.
- Payments are MOCKED, so no payment account is needed either.

## Cost per run

About **$0.00 per run** (local model; token counts per step are recorded in `decision_log.json`).

## Demo video

To be added (3 minutes at most).

## What our system will NOT do

- Promise income or success.
- Create fake reviews, testimonials, sign-ups or countdown timers.
- Pose as the founder, a customer or another brand.
- Hold, move or refund money by itself, create accounts, or store passwords or card numbers.
- Publish, send, spend or sign anything without the founder's explicit approval.
- Work on physical goods; financial, investment or crypto products; or health or legal advice products.
- Hide core features behind a paywall.

## How the project stays alive after the hackathon

- **Maintainers:** the founding team, reviewing issues and pull requests on this repository.
- **Roadmap:** real web search with citations, a small web UI for approvals, a test-mode payment provider adapter, more agent evals (see [ARCHITECTURE.md](ARCHITECTURE.md#roadmap)).
- **Community:** MIT-licensed; contributions welcome through issues and pull requests.
- **Funding:** none required to run (local models, no paid services); hosting costs stay at zero.
