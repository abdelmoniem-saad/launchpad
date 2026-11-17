# Phase 3 (Build), step 3.1: MVP spec, user docs draft and test plan (MOCKED)

Status: **MOCKED**. Model: `ollama/gpt-oss:20b`. Brief: Notion templates that help freelance video editors track client revisions, feedback rounds and deadlines in one place

> **DEMO INPUT:** the step 2.4 waitlist result in this run is hypothetical; no real demand test was run, so everything from step 2.4 on is a demonstration, not validated demand.

## Conclusion

MOCKED draft for founder review: MVP spec, user docs draft and test plan (MOCKED).

Strategy architect recommendation: **GO**. Phase is MOCKED; drafts only, nothing is executed.

## Work

- **core_features:**
  - 1. Client Dashboard – a single Notion page listing all active clients with status tags (draft, revision, approved).
  - 2. Revision Tracker – a linked database that records each revision request, notes, and due dates per client.
  - 3. Deadline Calendar – a shared calendar view that syncs with the Revision Tracker to show upcoming deadlines and reminders.
  - 4. Feedback Notes – a template for editors to paste client feedback directly into the Revision Tracker, auto‑linking to the relevant revision record.
  - 5. Export Summary – a simple button that compiles the current client list, revisions, and deadlines into a PDF for quick sharing.
- **out_of_scope:**
  - Custom Notion integrations or API automation
  - Advanced analytics or reporting dashboards
  - Multi‑language support
  - Paid subscription or marketplace integration
- **user_docs_draft:** # Revision‑Tracking Template Pack

## What it does
This Notion template pack lets you keep all your clients, revisions, and deadlines in one place. No more juggling spreadsheets or sticky notes.

## How to use it
1. **Add a new client** – Click *Add Client* and fill in the name and contact.
2. **Track revisions** – For each new revision request, click *Add Revision* under the client. Paste the client’s feedback, set a due date, and mark the status.
3. **See deadlines** – Open the *Deadline Calendar* to view all upcoming due dates at a glance.
4. **Export** – When you’re ready to share a status update, click *Export Summary* to generate a PDF.

## Tips
- Use the status tags (Draft, Revision, Approved) to quickly see where each project stands.
- Keep the feedback notes concise; the template will auto‑link them to the revision record.
- The calendar view can be filtered by client or status for focused work sessions.

Happy editing!
- **test_plan:**
  - 1. Create a landing page with a clear headline and a waitlist sign‑up form.
2. Run a 14‑day test using free social media posts and a small paid boost (≤$50) to drive traffic.
3. Track unique sign‑ups; success is 16 or more unique emails.
4. After the test, send a follow‑up email to all sign‑ups asking for a 5‑minute interview about their revision workflow.
5. Use interview responses to validate the core features and refine the template pack.

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit | The founder can build the five core features within 10 hours per week using existing Notion skills and writing tutorials for documentation. | Any feature requiring advanced Notion scripting or external integrations is out of scope due to lack of time and skill. | Focus on manual data entry and simple linked databases; postpone automation until a later phase. |
| marketing | The demand test will rely on a clear value proposition and a simple landing page to attract freelance video editors. | The headline must explicitly mention revision tracking; generic terms like "workflow" may not convert. Also, the waitlist sign‑up form should be minimal to avoid friction. | Use a single email field and a short opt‑in text; add a follow‑up email later if needed. |
| finance | The total budget must stay within $300, including $50 for paid traffic and $200 for hosting and domain costs. | Any additional tools or services that exceed the $300 cap are not allowed. | Use free Notion templates and free email marketing tools; avoid paid analytics or CRM. |
| product | The product scope is limited to a single Notion template pack with five core features; no API or automation. | Adding a custom Notion integration would exceed the founder’s weekly hours and budget. | Implement manual linking and simple database views; defer automation to a future iteration.}} |

## Open disagreements for the founder

- Any feature requiring advanced Notion scripting or external integrations is out of scope due to lack of time and skill.
- The headline must explicitly mention revision tracking; generic terms like "workflow" may not convert. Also, the waitlist sign‑up form should be minimal to avoid friction.
- Any additional tools or services that exceed the $300 cap are not allowed.
- Adding a custom Notion integration would exceed the founder’s weekly hours and budget.

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- founder approved
