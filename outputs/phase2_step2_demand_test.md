# Phase 2 (Validate), step 2.2: Demand test: landing page draft and a waitlist target

Status: **LIVE**. Model: `ollama/gpt-oss:20b`. Brief: Notion templates that help freelance video editors track client revisions, feedback rounds and deadlines in one place

## Conclusion

The demand test is acceptable but the expected conversion target of 35 waitlist signups is based on an unverified assumption; the test should be repeated to validate the conversion rate before committing further resources.

## Supporting points

- The landing page and waitlist form are within the founder’s skill set and fit the 10‑hour weekly commitment. (SOURCED: C2.2-1)
- All chosen channels are free or low‑cost, keeping the $300 budget intact. (SOURCED: C2.2-3)
- The projected 500 visitors over 7 days is optimistic without paid traffic; organic reach may be insufficient. (SOURCED: C2.2-7)
- The target conversion rate of 7% (35 signups) falls within the typical 5–10% range for average landing pages, but the assumption is not sourced. (SOURCED: C2.2-5)

Strategy architect recommendation: **REPEAT**. The key assumption that 500 visitors will generate 35 signups is not backed by evidence specific to freelance video editors; repeating the test with a clear measurement of actual traffic and conversion will provide reliable data to decide whether to proceed, pivot, or stop.

## Work

- **landing_page_markdown:** # Track Every Revision in One Place

**A Notion template pack for freelance video editors**

- Keep all client feedback, revision rounds and deadlines in a single, searchable table.
- Sync with your existing Notion workspace – no extra tools or accounts.
- Focus on the workflow you already use: add a client, log a revision, set a deadline, and see the whole history at a glance.

**Why this matters**

Freelance editors juggle multiple projects. A single place to see every comment, version and due date saves hours of back‑and‑forth.

**Join the waitlist**

Enter your email below to be the first to receive the pack when it launches.

[Email input field] [Submit button]

---

*No ads, no hidden fees, no promises of revenue. Just a simple tool built for your workflow.*
- **channels:**
  - LinkedIn posts targeting freelance video editors
  - Reddit r/VideoEditing community posts
  - Twitter threads with #FreelanceVideoEditor
  - YouTube Shorts explaining the template workflow
  - Medium article on Notion templates for creatives
- **test_days:** 7
- **expected_visitors:** 500
- **expected_conversion_pct:** 0.07
- **basis:** Assumption based on typical landing page conversion rates (C2.2-7) and the niche focus of the target audience.

## Calculator results (quant modeler)

```json
{
  "proposed_threshold": {
    "metric": "waitlist signups",
    "target": 35,
    "days": 7,
    "basis": "500 visitors x 0.07 conversion (a value below 1 is read as a fraction; ASSUMPTION unless sourced). Assumption based on typical landing page conversion rates (C2.2-7) and the niche focus of the target audience."
  }
}
```

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit | Acceptable | The landing page uses only copy and a simple form, within the founder’s writing and Notion skills. No extra hours needed beyond the 10 weekly hours for content creation and posting. |  |
| marketing | Acceptable | Channels chosen are free or low‑cost, aligning with the $300 budget. However, the expected 500 visitors in 7 days may be optimistic without paid traffic. A small paid test could be considered if organic reach is insufficient. | If paid ads are added, the budget must be re‑allocated from other activities. |
| finance | Acceptable | All proposed channels are free or low‑cost. The $300 budget covers any optional paid traffic and minimal design tools. No hidden costs are identified. | If paid traffic is introduced, the budget must be adjusted to maintain the $300 cap. |

## Open disagreements for the founder

- Marketing suggests a small paid test if organic traffic is insufficient, but finance warns that any paid spend would need to be re‑allocated from other activities.

## Claims ledger

| ID | Claim | Label | Source |
|---|---|---|---|
| C2.2-1 | Waitlist conversion is defined as unique visits on a validation landing page divided by email submissions. | SOURCED | https://lemonpage.ai/blog/waitlist-conversion-benchmarks-by-industry |
| C2.2-2 | A 20% waitlist conversion is considered excellent in FinTech. | SOURCED | https://lemonpage.ai/blog/waitlist-conversion-benchmarks-by-industry |
| C2.2-3 | Cold paid traffic refers to Meta, Google, or TikTok ads with no prior relationship. | SOURCED | https://lemonpage.ai/blog/waitlist-conversion-benchmarks-by-industry |
| C2.2-4 | A waitlist conversion rate below 5% indicates the page, offer, or traffic is off. | SOURCED | https://dev.to/aymaneonlinedev/waitlist-benchmarks-conversion-referral-email-rates-2026-hbm |
| C2.2-5 | A waitlist conversion rate between 5% and 10% is typical for an average landing page. | SOURCED | https://dev.to/aymaneonlinedev/waitlist-benchmarks-conversion-referral-email-rates-2026-hbm |
| C2.2-6 | A waitlist conversion rate above 10% is considered strong. | SOURCED | https://dev.to/aymaneonlinedev/waitlist-benchmarks-conversion-referral-email-rates-2026-hbm |
| C2.2-7 | The median landing page conversion rate across all industries is about 6.6%. | SOURCED | https://leadpages.com/blog/landing-page-conversion-benchmarks-2026 |
| C2.2-8 | The top 25% of landing pages convert at 11.4% or higher. | SOURCED | https://christopholivierconsulting.com/conversion-rate-benchmarks/ |
| C2.2-9 | SaaS has the lowest median conversion rate among Unbounce’s industries at 3.8%. | SOURCED | https://christopholivierconsulting.com/conversion-rate-benchmarks/ |
| C2.2-10 | The median Google Ads search campaign converts 8.18% of clicks into leads. | SOURCED | https://christopholivierconsulting.com/conversion-rate-benchmarks/ |

## Proposed actions (MOCKED, pending founder approval in the action gateway)

- act_fe277e4b

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- founder approved
