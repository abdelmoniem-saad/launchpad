# Phase 1 (Discover), step 1.4: Demand signals and a Mom Test interview script

Status: **LIVE**. Model: `ollama/gpt-oss:20b`. Brief: Notion templates that help freelance video editors track client revisions, feedback rounds and deadlines in one place

## Conclusion

The demand signals and interview script are well‑aligned with the target market and product concept, but no evidence yet confirms that freelance video editors will actually join a waitlist.

## Supporting points

- Freelance video editors juggle multiple projects and need a system to track revisions and deadlines (C1.4-1). (SOURCED: C1.4-1)
- Scope‑verdicted feedback rounds surface out‑of‑scope revisions as billable (C1.4-2). (SOURCED: C1.4-2)
- Existing Notion templates already include databases for Clients, Projects, Invoices, and Feedback Rounds (C1.4-4). (SOURCED: C1.4-4)
- The template offers ready‑made views such as This Week, Money Map, Scope‑Creep Ledger, Feedback Watch (C1.4-5). (SOURCED: C1.4-5)
- Freelancer.com’s job posting volume indicates ongoing demand for video editing services (C1.4-8). (SOURCED: C1.4-8)

Strategy architect recommendation: **GO**. The step successfully produced a set of demand signals backed by sourced claims and a comprehensive interview script that covers key pain points and potential value. The next logical action is to conduct the interviews and gather real user feedback to validate the waitlist hypothesis.

## Work

- **demand_signals:**
  - signal: Freelance video editors juggle multiple projects and need a system to track revisions and deadlines; claim_id: C1.4-1
  - signal: Clients often add out‑of‑scope revisions that become billable, requiring clear scope tracking; claim_id: C1.4-2
  - signal: Existing Notion templates already include databases for Clients, Projects, Invoices, and Feedback Rounds, indicating a template‑based workflow; claim_id: C1.4-4
  - signal: The template offers ready‑made views (This Week, Money Map, Scope‑Creep Ledger, Feedback Watch) that align with common pain points for editors; claim_id: C1.4-5
  - signal: Freelancer.com shows a large pool of video‑editing freelancers and a steady stream of job postings, implying ongoing demand for efficient workflow tools; claim_id: C1.4-8
- **interview_script:**
  - 1. Can you walk me through a recent project where you had to manage multiple clients at once?
  - 2. How do you currently keep track of revisions and feedback from each client?
  - 3. What tools or methods do you use to ensure you’re not missing any scope changes or late feedback?
  - 4. Have you ever had a revision that you didn’t realize was out of scope until after it was completed? What happened?
  - 5. How do you handle invoicing and tracking billable hours for each project?
  - 6. What would make it easier for you to see all your projects, deadlines, and revisions in one place?
  - 7. Have you used Notion or similar database tools for project management before? If so, what did you like or dislike about them?
  - 8. If a template could automatically organize clients, projects, invoices, and feedback rounds, would you find that useful? Why or why not?
  - 9. What would be a reasonable price for a ready‑made template that saves you time on these tasks?
  - 10. Would you be willing to join a waitlist to try such a template if it were available?
  - 11. Is there anything else you wish you had to make your freelance workflow smoother?

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit |  |  |  |

## Claims ledger

| ID | Claim | Label | Source |
|---|---|---|---|
| C1.4-1 | Freelance video editors balancing several edits and feedback deadlines. | SOURCED | https://www.notioninja.com/video-editors-notion-templates |
| C1.4-2 | Scope‑verdicted feedback rounds surface out‑of‑scope revisions as billable. | SOURCED | https://fehu82.github.io/video-editor-client-os/ |
| C1.4-3 | The product was created with AI‑assisted tools and disclosed as such. | SOURCED | https://fehu82.github.io/video-editor-client-os/ |
| C1.4-4 | The Notion template includes databases for Clients, Projects, Invoices, Feedback Rounds. | SOURCED | https://fehu82.github.io/video-editor-client-os/ |
| C1.4-5 | The template offers ready‑made views such as This Week, Money Map, Scope‑Creep Ledger, Feedback Watch. | SOURCED | https://fehu82.github.io/video-editor-client-os/ |
| C1.4-6 | Freelancer has 90.7M registered users and 25.9M total jobs posted. | ASSUMPTION | ASSUMPTION |
| C1.4-7 | Freelancer’s platform allows clients to post jobs and receive bids quickly. | ASSUMPTION | ASSUMPTION |
| C1.4-8 | Freelancer’s job posting volume indicates ongoing demand for video editing services. | SOURCED | https://www.freelancer.com/freelancers/skills/video-editing |

## Governance flags

- C1.4-2: not a demand signal for this product (Focuses on billing out‑of‑scope revisions, which is a related but distinct need; does not show demand for a tracking template.) -> not counted at the evidence gate
- C1.4-3: not a demand signal for this product (Describes product creation method, not a customer demand signal.) -> not counted at the evidence gate
- C1.4-4: not a demand signal for this product (Lists product features, not evidence of customer need.) -> not counted at the evidence gate
- C1.4-5: not a demand signal for this product (Product feature description, not a demand signal.) -> not counted at the evidence gate
- C1.4-8: not a demand signal for this product (General industry demand for video editing services, not specific to the problem the template solves.) -> not counted at the evidence gate
- sycophancy: no department raised a trade-off or pushback

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- 33/36 Phase 1 claims are sourced and verified (ratio 0.92)
- 1 sourced demand signal(s) for this product from step 1.4
- 5 sourced step 1.4 claim(s) were about a different need and do not count
- evidence threshold met
