# Phase 1 (Discover), step 1.1: Sharpen the idea and decide the industry

Status: **LIVE**. Model: `ollama/gpt-oss:20b`. Brief: Digital crossword puzzle packs about medieval tax law for professional dog groomers

## Conclusion

The founder should pivot away from the Veterinary Continuing Education niche and instead focus on a low‑budget, generic pet‑care trivia crossword that aligns with their skills and time constraints.

## Supporting points

- The weighted score for Veterinary Continuing Education (2.3) is higher than other niches, but the founder_fit score is only 1, indicating a mismatch with the founder’s available skills and time. (ASSUMPTION)
- The founder’s brief limits the project to 3 hours per week and a $50 budget, which is insufficient for creating specialized veterinary content without external expertise. (ASSUMPTION)
- Generic or AI‑generated pet‑care trivia crosswords can be produced within the budget and time limits using tools such as the free AI crossword generator (C1.1-2). (ASSUMPTION: C1.1-2)

Strategy architect recommendation: **PIVOT**. Although the Veterinary Continuing Education niche scores highest on the weighted metric, the founder’s capacity and expertise are insufficient to deliver it within the stated constraints. Pivoting to a generic pet‑care trivia crossword allows the founder to stay within the 3‑hour weekly limit and $50 budget while still testing the core hypothesis that professional dog groomers value themed puzzles. This approach mitigates risk and aligns with the founder’s values of fun and low‑budget execution.

## Work

- **sharpened_idea:** Create themed crossword puzzle packs that teach niche professional knowledge in a fun, engaging way.
- **niches:**
  - name: Pet Grooming Education; why: Target professional dog groomers with industry‑specific content; demand: 1; competition: 3; founder_fit: 2
  - name: Veterinary Continuing Education; why: Leverage medical terminology for licensed vets; demand: 2; competition: 4; founder_fit: 1
  - name: Pet Care Certification Prep; why: Provide study aids for pet‑care certification exams; demand: 3; competition: 2; founder_fit: 1

## Calculator results (quant modeler)

```json
{
  "ranked_niches": [
    {
      "name": "Veterinary Continuing Education",
      "why": "Leverage medical terminology for licensed vets",
      "demand": 2,
      "competition": 4,
      "founder_fit": 1,
      "claim_ids": [],
      "weighted_score": 2.3
    },
    {
      "name": "Pet Care Certification Prep",
      "why": "Provide study aids for pet\u2011care certification exams",
      "demand": 3,
      "competition": 2,
      "founder_fit": 1,
      "claim_ids": [],
      "weighted_score": 2.1
    },
    {
      "name": "Pet Grooming Education",
      "why": "Target professional dog groomers with industry\u2011specific content",
      "demand": 1,
      "competition": 3,
      "founder_fit": 2,
      "claim_ids": [],
      "weighted_score": 1.9
    }
  ],
  "weights": "demand 0.4, competition 0.3, founder fit 0.3",
  "chosen_niche": "Veterinary Continuing Education"
}
```

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit | The founder can only realistically execute a small, low‑budget project that fits within 3 hours per week and leverages their crossword design skill. The proposed niches above require subject‑matter expertise beyond the founder’s current skill set and would demand more time than available. Therefore, the founder should pivot to a niche that can be addressed with generic or AI‑generated content, such as general pet‑care trivia or basic dog‑grooming facts, which aligns with the founder’s values of fun and the limited budget. The current niches score low on founder_fit and would likely overextend the founder’s capacity. | The founder cannot commit to veterinary or certification content without additional expertise or time. The pet grooming education niche also requires industry knowledge that the founder lacks. The founder should focus on a niche that can be populated with generic or AI‑generated puzzles, such as general pet‑care trivia, to stay within the 3‑hour weekly limit and $50 budget. | If the founder wants to pursue a more specialized niche, they would need to either outsource content creation or significantly increase the budget and time commitment, which conflicts with the brief constraints. |

## Open disagreements for the founder

- Founder_fit department argues that the chosen niche requires subject‑matter expertise beyond the founder’s current skill set, while the calculator prioritizes demand and competition metrics.
- The founder_fit department suggests outsourcing or increasing budget/time, which conflicts with the brief constraints.

## Claims ledger

| ID | Claim | Label | Source |
|---|---|---|---|
| C1.1-1 | A 15‑clue crossword covering medieval legal systems and concepts for middle school history students is available for download. | SOURCED | https://brightsprout.com/crossword/medieval-law-crossword-puzzle |
| C1.1-2 | Template.net offers a free AI crossword puzzle generator that can create puzzles from a prompt describing a subject, theme, or vocabulary. | ASSUMPTION | ASSUMPTION |
| C1.1-3 | Puzzlesales.com sells a variety of crossword‑style puzzle products such as Cross Code, Box Clever, and Equaliser. | ASSUMPTION | ASSUMPTION |
| C1.1-4 | Bestcrosswords.com hosts an archive of over 8,000 themed crosswords from leading constructors, all free to play. | ASSUMPTION | ASSUMPTION |

## Governance flags

- C1.1-2: quote not found in its source -> ASSUMPTION
- C1.1-3: quote not found in its source -> ASSUMPTION
- C1.1-4: quote not found in its source -> ASSUMPTION

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- founder approved
