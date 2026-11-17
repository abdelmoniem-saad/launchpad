# Phase 1 (Discover), step 1.2: Score the idea against 2-3 alternatives

Status: **LIVE**. Model: `ollama/gpt-oss:20b`. Brief: Notion templates that help freelance video editors track client revisions, feedback rounds and deadlines in one place

## Conclusion

Proceed with the Notion Revision Tracker Pack as the most viable option.

## Supporting points

- The Notion Revision Tracker Pack scores highest overall (4.05) due to strong demand, moderate competition, excellent founder fit, and manageable effort. (SOURCED: C1.2-1, C1.2-2)
- The alternative Video Editing Project Brief Template has a lower weighted score (3.6) and higher effort, making it less attractive. (SOURCED: C1.2-1)
- The Revision Checklist App (standalone) scores lowest (2.55) and would require skills and time beyond the founder’s current capacity. (SOURCED: C1.2-4)

Strategy architect recommendation: **GO**. The Notion Revision Tracker Pack has the highest weighted score, aligns with the founder’s skill set and time constraints, and offers a simple, low‑effort solution that meets market demand. The alternatives score lower and either require more effort or additional development resources. Therefore, moving forward with the Notion pack is the best next step.

## Work

- **options:**
  - name: Notion Revision Tracker Pack; is_founder_idea: True; demand: 4; competition: 3; founder_fit: 5; effort: 4; claim_ids: ['C1.2-1', 'C1.2-2']
  - name: Video Editing Project Brief Template; is_founder_idea: False; demand: 3; competition: 4; founder_fit: 3; effort: 5; claim_ids: ['C1.2-1']
  - name: Revision Checklist App (standalone); is_founder_idea: False; demand: 3; competition: 2; founder_fit: 2; effort: 3; claim_ids: ['C1.2-4']

## Calculator results (quant modeler)

```json
{
  "ranked_options": [
    {
      "name": "Notion Revision Tracker Pack",
      "is_founder_idea": true,
      "demand": 4,
      "competition": 3,
      "founder_fit": 5,
      "effort": 4,
      "claim_ids": [
        "C1.2-1",
        "C1.2-2"
      ],
      "weighted_score": 4.05
    },
    {
      "name": "Video Editing Project Brief Template",
      "is_founder_idea": false,
      "demand": 3,
      "competition": 4,
      "founder_fit": 3,
      "effort": 5,
      "claim_ids": [
        "C1.2-1"
      ],
      "weighted_score": 3.6
    },
    {
      "name": "Revision Checklist App (standalone)",
      "is_founder_idea": false,
      "demand": 3,
      "competition": 2,
      "founder_fit": 2,
      "effort": 3,
      "claim_ids": [
        "C1.2-4"
      ],
      "weighted_score": 2.55
    }
  ],
  "weights": "demand 0.35, competition 0.2, founder fit 0.25, effort 0.2"
}
```

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit | The founder can execute the Notion pack with existing skills and time. The brief‑to‑version workflow and revision checklists are within scope. The standalone app would require additional development skills and time beyond the 10‑hour weekly limit. | The standalone app is too resource‑heavy and misaligned with the founder’s values of simple tools. | Focus on the Notion pack and consider a future app if budget and time allow. |

## Open disagreements for the founder

- The founder_fit department notes that the standalone app is too resource‑heavy and misaligned with the founder’s values of simple tools, but this does not affect the decision to pursue the Notion pack.

## Claims ledger

| ID | Claim | Label | Source |
|---|---|---|---|
| C1.2-1 | Freelance video editors need detailed project briefs that include technical specifications and brand guidelines to align work with client expectations. | SOURCED | https://contra.com/hire/english-speaking-video-editors |
| C1.2-2 | Freelance video editors benefit from regular check‑ins and progress updates to ensure alignment and allow time for adjustments before final delivery. | SOURCED | https://contra.com/hire/english-speaking-video-editors |
| C1.2-3 | Platforms like Contra provide a brief‑to‑version revision workflow that turns creative direction into clear cut iterations. | SOURCED | https://gitnux.org/service/freelance-video-editing/ |
| C1.2-4 | VidChops offers revision checklists that help creators manage iterative feedback cycles. | SOURCED | https://worldmetrics.org/service/freelance-video-editing/ |
| C1.2-5 | Bark provides milestone‑based task handoff that groups edits into reviewable deliverables instead of open‑ended custom projects. | ASSUMPTION | ASSUMPTION |
| C1.2-6 | Upwork’s fee structure shifted to a variable 0‑15% rate per contract, with an average effective fee of 12‑13% for most freelancers. | SOURCED | https://chatcut.io/blog/freelance-video-editing-platforms-2026 |
| C1.2-7 | Fiverr’s AI Video Hub launched in March 2026, with demand for AI‑powered video editing spiking 66% in six months. | SOURCED | https://chatcut.io/blog/freelance-video-editing-platforms-2026 |
| C1.2-8 | 59% of video marketers produce video in‑house, 32% use a mix, and only 10% fully outsource, down from 24% pure outsourcing in 2024. | SOURCED | https://chatcut.io/blog/freelance-video-editing-platforms-2026 |
| C1.2-9 | Freelance video editors in India lose money on international payments due to 2‑3% FX spread and intermediary deductions on SWIFT wires. | SOURCED | https://grey.co/blog/freelance-video-editing-platforms |
| C1.2-10 | Receiving US dollar payments via ACH or Fedwire can cost the sender under $1 or $15‑$30, respectively, with minimal fees for the recipient if using a virtual USD account. | SOURCED | https://grey.co/blog/freelance-video-editing-platforms |

## Governance flags

- C1.2-5: quote not found in its source -> ASSUMPTION

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- founder approved
