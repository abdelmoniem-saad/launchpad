# Phase 2 (Validate), step 2.2: Demand test: landing page draft and a waitlist target

Status: **LIVE**. Model: `ollama/gpt-oss:20b`. Brief: Notion templates that help freelance video editors track client revisions, feedback rounds and deadlines in one place

## Conclusion

The landing page and waitlist test is likely to meet the 20‑signup threshold, but the conversion assumption is optimistic and the evidence is weak, so the founder should repeat the test before committing further.

## Supporting points

- A single‑email capture landing page can achieve a 5–10% conversion rate (C2.2-8). (SOURCED: C2.2-8)
- Paid Google Ads and Facebook lead campaigns typically deliver 8–8.5% landing page conversions (C2.2-6, C2.2-7). (SOURCED: C2.2-6, C2.2-7)
- The calculator projects 20 signups from 200 visitors at a 10% conversion rate, meeting the 14‑day threshold (calculator). (ASSUMPTION)
- The 10% conversion assumption is not directly sourced and is higher than typical industry averages, making the result uncertain. (ASSUMPTION)

Strategy architect recommendation: **REPEAT**. The projected 10% conversion rate is an assumption rather than a sourced figure, and typical landing page conversions for paid traffic hover around 8–8.5%. Given this uncertainty, repeating the test will provide more reliable data before scaling.

## Work

- **landing_page_markdown:** # Freelance Video Editor Revision Tracker

**Track every client revision, feedback round and deadline in one Notion page**

- **All clients in one view** – see who sent feedback, what changes are pending and when they’re due.
- **Automatic reminders** – set a due date and get a gentle nudge when it’s close.
- **One‑click export** – copy the revision log into your email or project file.

> *No hidden fees, no extra software. Just a clean Notion template that fits into your existing workflow.*

## Get the Template

Enter your email below to receive the template and updates on new features.

[Email input field] [Sign up]

---

**Why this matters** – Freelance video editors juggle multiple clients and deadlines. A single, shared revision tracker keeps everyone on the same page and saves hours of back‑and‑forth communication.

---

*We’ll never sell your data. No spam. Just updates on the template pack.*

## Calculator results (quant modeler)

```json
{
  "proposed_threshold": {
    "metric": "waitlist signups",
    "target": 20,
    "days": 14,
    "basis": "200 visitors x 0.1 conversion (a value below 1 is read as a fraction; ASSUMPTION unless sourced). Assumption based on C2.2-6, C2.2-7, C2.2-8, C2.2-4"
  }
}
```

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit | Acceptable | The landing page uses only copy and a single email field, which the founder can create within the 10 h weekly budget. No advanced design or coding skills required. |  |
| marketing | The product can be positioned as a must‑have for freelance video editors needing efficient revision workflows. Demand can be validated via a waitlist and low‑cost outreach. | The waitlist claim is weak without prior audience; the founder should test demand through a small paid ad or community post before scaling. | Allocate a small portion of the budget to a targeted LinkedIn ad to drive waitlist sign‑ups, keeping spend within the USD 300 limit. |
| finance | Acceptable | The projected spend for 200 visitors at $1.50 per click (Google) and $0.80 per click (Facebook) is roughly $300, matching the budget. No hidden costs are assumed. | If actual CPC is higher, the founder may need to reduce the test window or cut one channel. |

## Claims ledger

| ID | Claim | Label | Source |
|---|---|---|---|
| C2.2-1 | The median landing page conversion rate across all industries is about 6.6% | SOURCED | https://leadpages.com/blog/landing-page-conversion-benchmarks-2026 |
| C2.2-2 | A waitlist conversion rate of 10% or higher is considered strong for a focused waitlist page | SOURCED | https://dev.to/aymaneonlinedev/waitlist-benchmarks-conversion-referral-email-rates-2026-hbm |
| C2.2-3 | A 20%+ waitlist conversion rate is excellent, usually with warm or targeted traffic | SOURCED | https://dev.to/aymaneonlinedev/waitlist-benchmarks-conversion-referral-email-rates-2026-hbm |
| C2.2-4 | Cold paid traffic typically yields lower conversion rates than warm traffic for waitlists | SOURCED | https://lemonpage.ai/blog/waitlist-conversion-benchmarks-by-industry |
| C2.2-5 | The definition of waitlist conversion is unique visits on a validation landing page divided by email submissions | SOURCED | https://lemonpage.ai/blog/waitlist-conversion-benchmarks-by-industry |
| C2.2-6 | The median landing page conversion rate for paid Google Ads search campaigns is 8.18% | SOURCED | https://christopholivierconsulting.com/conversion-rate-benchmarks/ |
| C2.2-7 | The median landing page conversion rate for paid Facebook lead campaigns is 8.54% | SOURCED | https://christopholivierconsulting.com/conversion-rate-benchmarks/ |
| C2.2-8 | A typical landing page with a single email capture can achieve a conversion rate of 5–10% | SOURCED | https://dev.to/aymaneonlinedev/waitlist-benchmarks-conversion-referral-email-rates-2026-hbm |
| C2.2-9 | The median landing page conversion rate for all industries is 6.6% according to Unbounce benchmark analysis | SOURCED | https://www.octoagency.io/blog/landing-page-conversion-rate/ |
| C2.2-10 | The top 25% of landing pages convert at 11.4% or higher | SOURCED | https://christopholivierconsulting.com/conversion-rate-benchmarks/ |

## Proposed actions (MOCKED, pending founder approval in the action gateway)

- act_842fe708

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- founder approved
