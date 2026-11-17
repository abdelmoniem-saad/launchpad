# Revision‑Tracking Notion Template Pack for Freelance Video Editors

> MVP built by the pipeline in step 3.1 for the founder's review. Build tests: 8/8 passed. Not published, listed or sold: launching it needs the founder's approval (phase 5, MOCKED).

> **DEMO INPUT:** this run reached the build step with a hypothetical step 2.4 result; demand is NOT validated.

## Client Dashboard

The Client Dashboard is a single Notion page that lists all active clients in a table. Each row contains the client name, project title, current revision round, and a link to the project’s dedicated workspace. The table is filtered by status (In‑Progress, Completed, On‑Hold) and sorted by due date. Users can add, edit, or delete clients directly from the dashboard, and each action updates the project’s metadata automatically.

## Revision Tracker

The Revision Tracker is a linked database that records every revision round for each project. It includes fields for Revision Number, Date Submitted, Feedback Summary, and Status (Pending, Approved, Re‑work). A formula column calculates the total number of revisions and highlights projects exceeding a user‑defined limit. Users can add new revisions by clicking a button that duplicates the last row and prompts for feedback notes.

## Feedback Form Template

The Feedback Form Template is a pre‑filled Notion page that editors can duplicate for each client. It contains sections for Visual Feedback, Audio Feedback, and Narrative Notes, each with a checkbox list of common issues (e.g., color grading, pacing, audio sync). The template auto‑generates a Revision Number and timestamp, and includes a link back to the Revision Tracker for easy cross‑reference.

## Deadline & Milestone Tracker

The Deadline & Milestone Tracker is a calendar view that displays all project milestones and final deadlines. Each milestone has a due date, a description, and a completion checkbox. The calendar automatically flags overdue items in red and sends a reminder note when a milestone is within 48 hours of its due date. Users can drag milestones to adjust dates, and the tracker updates the Revision Tracker’s status accordingly.

## Revision Summary Report

The Revision Summary Report is a dynamic dashboard that aggregates data from the Revision Tracker. It shows total revisions per client, average revision time, and a heat map of revision frequency. The report includes a downloadable CSV export button and a visual bar chart that updates in real time as new revisions are added. Users can filter the report by date range or client to analyze workflow efficiency.

## How to use it

**How to Use the Revision‑Tracking Notion Template Pack**
1. **Import the Pack** – Download the ZIP, unzip, and open the main Notion page. 
2. **Set Up Your Clients** – In the Client Dashboard, click "Add Client" and fill in the project details. 
3. **Track Revisions** – For each new round, duplicate the Feedback Form Template, fill in the feedback, and click "Submit Revision". The Revision Tracker updates automatically. 
4. **Manage Deadlines** – Use the Deadline & Milestone Tracker to set and adjust dates. Overdue items will be highlighted. 
5. **Review Progress** – Open the Revision Summary Report to see overall revision metrics and export data if needed. 
6. **Iterate** – Use the feedback notes to refine your editing workflow and reduce revision cycles.

## Not included in this version

- Paid subscription model
- Integration with external project management tools
- Automated email notifications
- Mobile app version
- Custom branding beyond Notion’s native options

## Build tests

| Test | Result | Detail |
|---|---|---|
| has a product title | PASS | 'Revision‑Tracking Notion Template Pack for Freelance Video Editors' |
| 1 to 5 core features | PASS | 5 feature(s) |
| every feature is named and has real content (>= 60 words) | PASS | ok |
| user docs exist (>= 80 words) | PASS | 117 words |
| user docs explain every feature by name | PASS | ok |
| the test plan has a check for every feature | PASS | 5 check(s) |
| no placeholder text | PASS | ok |
| rule guard: no income promises, reviews, urgency, impersonation or card data | PASS | clean |
