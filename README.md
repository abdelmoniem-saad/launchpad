# launchpad

An open-source AI consulting firm that a founder hires to take a brief to a validated, sellable **digital** product. It builds the company's departments along the way, keeps the founder in charge of every decision, and says "don't launch this" when the evidence is weak. It runs on a local open-weight model with no keys and no paid services.

## Quickstart

```bash
docker compose up
```

Then open **http://localhost:8501**, fill in the brief and start the engagement. The first start downloads the model (`qwen3:8b`, about 5 GB), so it takes a while. Plan for about 8 GB of free RAM and 10 GB of disk. To use the Groq free tier as an optional fast mode, put `GROQ_API_KEY` in `.env`.

Without Docker you need Python 3.11+ and [Ollama](https://ollama.com):

```bash
ollama pull qwen3:8b
pip install -r requirements.txt
streamlit run app/ui.py
```

There is also a command-line founder console, which runs the same graph: `python -m app.cli --brief briefs/<name>.json`.

## What works and what is mocked

| Phase | Step | Status |
|---|---|---|
| Intake | Brief completeness check with a founder interview; excluded-product check (STOP with the reason) | **Working** |
| 1 Discover | 1.1 Sharpen the idea and decide the industry (niches scored by the calculator) | **Working** |
| 1 Discover | 1.2 Score the idea against 2-3 alternatives | **Working** |
| 1 Discover | 1.3 Define the market: competitors and prices, all sourced | **Working** |
| 1 Discover | 1.4 Demand signals and a Mom Test interview script; evidence gate | **Working** |
| 2 Validate | 2.1 Lean Canvas | **Working** |
| 2 Validate | 2.2 Demand test: landing page draft and a waitlist target the founder locks | **Working** (publishing is **MOCKED**) |
| 2 Validate | 2.3 Collaborations: communities, partners, outreach drafts | **Working** (sending is **MOCKED**) |
| 2 Validate | 2.4 Founder enters the real result; demand gate compares it in code | **Working** |
| 2 Validate | 2.5 Company blueprint: roles, founder / automate / hire later, cost against budget | **Working** (job posts are **MOCKED**) |
| 3 Build | MVP spec, user docs draft, test plan | **MOCKED** |
| 4 Commercial setup | Pricing tiers (calculator), draft terms, privacy and refund policies. No payment code of any kind | **MOCKED** |
| 5 Launch | Store page and launch post drafts; automatic delivery to buyers | **MOCKED** |
| 6 Operate and learn | Support replies, metrics plan, persevere-or-pivot memo | **MOCKED** |
| Governance | Founder checkpoint after every step; action gateway with one-time tokens; Tier 1 rule guard; Tier 2 claim check; team health check; decision log; cost report | **Working** |
| Payments | Checkout, delivery after payment, refunds, reconciliation | **STUBBED** (design only, in [ARCHITECTURE.md](ARCHITECTURE.md#sale-to-cash)) |

**MOCKED** means drafts only: whatever the founder approves is written to `outputs/` with a MOCKED label. Nothing is actually published, sent, charged, signed or contacted.

## Architecture

The founder is the client and the system is a consulting firm. Six firm agents run every step: engagement manager, strategy architect, market researcher, quant modeler, synthesis lead and compliance officer. The client's departments (Founder Fit, Marketing, Finance, Product, Legal, Sales, Operations, Support) are added phase by phase and push back on recommendations, using only the founder's real constraints. A LangGraph parent graph runs intake and then each step through one reusable step subgraph: research, department work, the calculator, a conclusion-first report, the rule guard, claim verification and a health check. After every step there is a founder checkpoint (approve / edit / redo / stop), and a gate decides go / repeat / pivot / stop in code. Anything outbound goes through an action gateway that only executes with a one-time token, created when the founder clicks Approve. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Models and free resources

- **Default, keyless:** `qwen3:8b` (Apache-2.0, open weights) via Ollama. Set `LOCAL_MODEL` to use `qwen3:4b` on small laptops or `gpt-oss:20b` (Apache-2.0) on bigger machines.
- **Optional fast mode:** the Groq free tier with `openai/gpt-oss-120b` (open weights), only when `GROQ_API_KEY` is set. Calls are rate-limited, and any error falls back to the local model.
- **Web research, keyless:** self-hosted SearXNG, with the `ddgs` package, the Hacker News Algolia API and the Wikipedia API as fallbacks; page text is extracted with `trafilatura`.
- No paid API, account or card is needed.

## Cost per run

**About $0.00 per run** (local model). Every model call's tokens and wall-clock time are counted and saved to `outputs/cost_report.json` at each step; the CLI also prints the total at the end. The committed demo run's figures are in [outputs/cost_report.json](outputs/cost_report.json).

## Demo video

To be added (3 minutes at most).

## What our system will NOT do

- Promise income or guarantee success.
- Generate fake reviews, testimonials, signups or urgency (countdowns, "only 3 left").
- Impersonate the founder, customers or other brands.
- Hold, move or refund money. There is no payment code of any kind.
- Store passwords or card details; anything that looks like a card number is removed.
- Publish, send, spend, sign, hire or contact anyone without the founder's approval, and even then only as a MOCKED record.
- Hide core features behind a paywall.
- Invent internal company data (sprint velocity, margins, headcount). A new venture has none; unknowns are labelled `ASSUMPTION`.
- Work on physical goods, financial or crypto products, health advice or legal advice. These are refused at intake, with the reason.

## How the project stays alive after the hackathon

- **Open license:** Apache-2.0. Anyone can run, fork and extend it.
- **Extend with a file:** a new department is one prompt file in `prompts/departments/` plus one line in `app/phases.py`.
- **Roadmap:** take phases 3-6 from MOCKED to LIVE one at a time, add a real checkout behind founder approval (designed in ARCHITECTURE.md), more region-aware research sources, and more evals of the guardrails.
- **Maintainers and community:** the founding team reviews issues and pull requests. Costs stay at $0 because everything runs locally.
