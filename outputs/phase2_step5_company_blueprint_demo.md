# Phase 2 (Validate), step 2.5: Company blueprint

Status: **LIVE**. Model: `ollama/gpt-oss:20b`. Brief: Notion templates that help freelance video editors track client revisions, feedback rounds and deadlines in one place

> **DEMO INPUT:** the step 2.4 waitlist result in this run is hypothetical; no real demand test was run, so everything from step 2.4 on is a demonstration, not validated demand.

## Conclusion

The founder can feasibly build a Notion template pack for freelance video editors within the $300 budget and 10 hrs/week constraint, but demand validation must be prioritized before any paid marketing.

## Supporting points

- Founder has the necessary video‑editing, Notion, and tutorial‑writing skills to create the template pack within the allocated 10 hrs/week. (ASSUMPTION)
- The marketing budget of $50/month (C2.5-1) is sufficient for low‑cost survey tools and organic LinkedIn outreach, keeping spend under the $300 cap. (SOURCED: C2.5-1)
- Demand validation should rely on at least 5 Mom Test interviews (C2.5-8) before launching paid ads, aligning with the marketing department’s pushback. (SOURCED: C2.5-8)
- The target market (global, English‑speaking freelance video editors) is sizable, with the online video platform market projected at $15 billion by 2026 (C2.5-3). (SOURCED: C2.5-3)
- Freelance video editors typically charge $20–$150/hr (C2.5-1, C2.5-2), indicating a willingness to invest in tools that streamline revision workflows. (SOURCED: C2.5-1, C2.5-2)

Strategy architect recommendation: **REPEAT**. The plan is sound but the evidence for demand is weak—only a few interviews are planned. To reduce risk, conduct the interviews first, then decide whether to proceed with paid ads. If interest remains low, pivot to a different niche or product format. If interest is high, proceed with the template pack launch. The current budget and hours are adequate, but validation must precede spending on paid channels.

## Work

- **roles:**
  - department: founder_fit; role: Product Development; choice: founder; reason: Founder has video editing, Notion, and tutorial writing skills; can build template pack within 10 hrs/week.; monthly_cost_usd: 0; cost_claim_id: None
  - department: marketing; role: Demand Validation; choice: automate; reason: Use low‑cost survey tools and social posts to gather Mom Test data; founder can manage within budget.; monthly_cost_usd: 50; cost_claim_id: C2.5-1
  - department: finance; role: Budget Oversight; choice: founder; reason: Founder will track spend against $300 budget; no external hire needed.; monthly_cost_usd: 0; cost_claim_id: None
- **backlog:**
  - **founder_fit:**
    - 1. Draft Notion template structure
    - 2. Write tutorial video
    - 3. Test template with a friend editor
    - 4. Prepare waitlist landing page
    - 5. Iterate based on feedback
  - **marketing:**
    - 1. Create a LinkedIn post announcing waitlist
    - 2. Draft a short survey for Mom Test interviews
    - 3. Identify 10 freelance editor communities
    - 4. Schedule 5 interview slots
    - 5. Compile interview insights
  - **finance:**
    - 1. Set up a simple expense tracker
    - 2. Allocate $250 for marketing tools
    - 3. Reserve $50 for unforeseen costs
    - 4. Review spend weekly
    - 5. Adjust budget if needed
- **job_post_drafts:**
  - role: Freelance Video Editor; text: Seeking a freelance video editor with 2+ years experience in editing YouTube content. Must be comfortable with revision workflows and client communication. Pay $30–$50/hr based on location. Apply with portfolio and brief description of your revision process.

## Calculator results (quant modeler)

```json
{
  "monthly_total_usd": 50.0,
  "budget_usd": 300,
  "over_budget": false
}
```

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit | Approve all founder‑led tasks; ensure no extra hours beyond 10/week. | Any task requiring more than 10 hrs/week or outside editing/Notion skills must be deferred. | Prioritize core template creation over ancillary content. |
| marketing | Validate demand before spending on paid ads. | Do not launch paid campaigns until at least 5 Mom Test interviews confirm interest. | Use organic reach first; reserve budget for retargeting if waitlist >20 signups. |
| finance | Protect $300 budget. | Reject any tool or service costing >$50/month without clear ROI. | Allocate $250 to marketing, $50 to contingency; no external hires. |

## Open disagreements for the founder

- Marketing department insists on no paid campaigns until 5 interviews confirm interest; founder may want to test paid outreach earlier to accelerate sign‑ups.

## Claims ledger

| ID | Claim | Label | Source |
|---|---|---|---|
| C2.5-1 | Freelance video editors typically charge between $20 and $150 per hour depending on location and seniority. | SOURCED | https://videoeditingcompany.com/video-editor-rates-by-country-2026/ |
| C2.5-2 | In Eastern Europe, skilled mid‑to‑senior freelance video editors charge $15–$55 per hour. | SOURCED | https://videoeditingcompany.com/video-editor-rates-by-country-2026/ |
| C2.5-3 | The global online video platform market is projected to reach $15 billion by 2026. | SOURCED | https://www.interviewgrid.com/freelance/video_editor |
| C2.5-4 | Video editing is among the top 10 in‑demand freelance skills on Upwork. | SOURCED | https://www.interviewgrid.com/freelance/video_editor |
| C2.5-5 | Full‑time freelance video editors can earn between $3,000 and $8,000 per month. | SOURCED | https://www.interviewgrid.com/freelance/video_editor |
| C2.5-6 | AI editing tools are automating basic rough cuts, putting pressure on entry‑level editors. | SOURCED | https://freelancecalc.co/freelance-video-editor-rates/ |
| C2.5-7 | Editors with motion graphics, color grading, or narrative skills command 40–60% higher rates than pre‑AI equivalents. | SOURCED | https://freelancecalc.co/freelance-video-editor-rates/ |
| C2.5-8 | A typical revision policy for freelance video editors includes two revision rounds. | SOURCED | https://freelancecalc.co/freelance-video-editor-rates/ |
| C2.5-9 | The average hourly rate for a mid‑level YouTube editor is $65 per hour. | SOURCED | https://freelancecalc.co/freelance-video-editor-rates/ |
| C2.5-10 | A 3‑hour rough cut can balloon to 8+ hours if clients send new footage after the first review. | SOURCED | https://freelancecalc.co/freelance-video-editor-rates/ |

## Proposed actions (MOCKED, pending founder approval in the action gateway)

- act_7e588b82

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- founder approved
