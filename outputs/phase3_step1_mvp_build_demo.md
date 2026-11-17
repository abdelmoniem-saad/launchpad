# Phase 3 (Build), step 3.1: Build the MVP and its user docs; tests must pass

Status: **LIVE**. Model: `ollama/gpt-oss:20b`. Brief: Notion templates that help freelance video editors track client revisions, feedback rounds and deadlines in one place

> **DEMO INPUT:** the step 2.4 waitlist result in this run is hypothetical; no real demand test was run, so everything from step 2.4 on is a demonstration, not validated demand.

## Conclusion

No defensible conclusion: the firm could not support one with evidence.

## Work

- **product_title:** Revision‑Tracking Notion Template Pack for Freelance Video Editors
- **core_features:**
  - name: Client Dashboard; content: The Client Dashboard is a single Notion page that lists all active clients in a table. Each row contains the client name, project title, current revision round, and a link to the project’s dedicated workspace. The table is filtered by status (In‑Progress, Completed, On‑Hold) and sorted by due date. Users can add, edit, or delete clients directly from the dashboard, and each action updates the project’s metadata automatically.
  - name: Revision Tracker; content: The Revision Tracker is a linked database that records every revision round for each project. It includes fields for Revision Number, Date Submitted, Feedback Summary, and Status (Pending, Approved, Re‑work). A formula column calculates the total number of revisions and highlights projects exceeding a user‑defined limit. Users can add new revisions by clicking a button that duplicates the last row and prompts for feedback notes.
  - name: Feedback Form Template; content: The Feedback Form Template is a pre‑filled Notion page that editors can duplicate for each client. It contains sections for Visual Feedback, Audio Feedback, and Narrative Notes, each with a checkbox list of common issues (e.g., color grading, pacing, audio sync). The template auto‑generates a Revision Number and timestamp, and includes a link back to the Revision Tracker for easy cross‑reference.
  - name: Deadline & Milestone Tracker; content: The Deadline & Milestone Tracker is a calendar view that displays all project milestones and final deadlines. Each milestone has a due date, a description, and a completion checkbox. The calendar automatically flags overdue items in red and sends a reminder note when a milestone is within 48 hours of its due date. Users can drag milestones to adjust dates, and the tracker updates the Revision Tracker’s status accordingly.
  - name: Revision Summary Report; content: The Revision Summary Report is a dynamic dashboard that aggregates data from the Revision Tracker. It shows total revisions per client, average revision time, and a heat map of revision frequency. The report includes a downloadable CSV export button and a visual bar chart that updates in real time as new revisions are added. Users can filter the report by date range or client to analyze workflow efficiency.
- **user_docs:** **How to Use the Revision‑Tracking Notion Template Pack**
1. **Import the Pack** – Download the ZIP, unzip, and open the main Notion page. 
2. **Set Up Your Clients** – In the Client Dashboard, click "Add Client" and fill in the project details. 
3. **Track Revisions** – For each new round, duplicate the Feedback Form Template, fill in the feedback, and click "Submit Revision". The Revision Tracker updates automatically. 
4. **Manage Deadlines** – Use the Deadline & Milestone Tracker to set and adjust dates. Overdue items will be highlighted. 
5. **Review Progress** – Open the Revision Summary Report to see overall revision metrics and export data if needed. 
6. **Iterate** – Use the feedback notes to refine your editing workflow and reduce revision cycles.
- **out_of_scope:**
  - Paid subscription model
  - Integration with external project management tools
  - Automated email notifications
  - Mobile app version
  - Custom branding beyond Notion’s native options
- **test_plan:**
  - feature: Client Dashboard; check: Verify that adding a new client creates a row with correct fields and links to a new project workspace.
  - feature: Revision Tracker; check: Confirm that submitting a new revision increments the Revision Number and updates the status to Pending.
  - feature: Feedback Form Template; check: Ensure that duplicating the template creates a new page with a unique Revision Number and timestamp.
  - feature: Deadline & Milestone Tracker; check: Check that setting a milestone date displays it on the calendar and flags overdue items in red.
  - feature: Revision Summary Report; check: Validate that the report aggregates revisions correctly and the CSV export contains all revision rows.

## Calculator results (quant modeler)

```json
{
  "build_tests": {
    "tests": [
      {
        "name": "has a product title",
        "passed": true,
        "detail": "'Revision\u2011Tracking Notion Template Pack for Freelance Video Editors'"
      },
      {
        "name": "1 to 5 core features",
        "passed": true,
        "detail": "5 feature(s)"
      },
      {
        "name": "every feature is named and has real content (>= 60 words)",
        "passed": true,
        "detail": "ok"
      },
      {
        "name": "user docs exist (>= 80 words)",
        "passed": true,
        "detail": "117 words"
      },
      {
        "name": "user docs explain every feature by name",
        "passed": true,
        "detail": "ok"
      },
      {
        "name": "the test plan has a check for every feature",
        "passed": true,
        "detail": "5 check(s)"
      },
      {
        "name": "no placeholder text",
        "passed": true,
        "detail": "ok"
      },
      {
        "name": "rule guard: no income promises, reviews, urgency, impersonation or card data",
        "passed": true,
        "detail": "clean"
      }
    ],
    "passed": 8,
    "total": 8,
    "all_passed": true
  }
}
```

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit | All features are within the founder’s Notion and writing skills and fit the 10‑hour weekly limit. |  | Prioritize features that require minimal custom scripting to stay within time constraints. |
| marketing | The MVP provides clear value propositions for freelance video editors and can be showcased in a simple landing page. | The test plan must include a usability check for the Feedback Form Template, as editors may struggle with the duplicate process. | Add a brief video walkthrough to the user docs to improve adoption without extra cost. |
| finance | The MVP development cost is estimated at $200 for Notion template creation and $100 for documentation, within the $300 budget. | No additional costs are justified at this stage. | Allocate remaining $100 to a minimal paid outreach campaign after validation. |
| product | The MVP scope aligns with the founder’s weekly hours and skill set. | Ensure the Revision Summary Report uses only built‑in Notion formulas to avoid scripting overhead. | Exclude advanced analytics features that would require external tools. |

## Open disagreements for the founder

- Report had no conclusion; treat this step as weak.

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- 8/8 build tests passed
- all build tests pass
