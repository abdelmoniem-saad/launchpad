# Phase 1 (Discover), step 1.4: Demand signals and a Mom Test interview script

Status: **LIVE**. Model: `ollama/gpt-oss:20b`. Brief: Digital crossword puzzle packs about medieval tax law for professional dog groomers

## Conclusion

The evidence shows a clear demand for structured learning and CEU resources among professional dog groomers, but it does not confirm that they would value or purchase a medieval‑tax‑law themed crossword pack.

## Supporting points

- Professional dog groomers and salon owners experience frustration and hidden costs due to lack of formal credentialing, indicating a need for structured learning materials. (SOURCED: C1.4-1, C1.4-2)
- The industry actively seeks CEU opportunities tied to certification, and the AKC PGC requires 25 CEUs, confirming a market for educational content. (SOURCED: C1.4-3, C1.4-4)
- Pet owners spend billions on pet services, creating pressure on groomers to provide top‑tier expertise, which supports the existence of a paying customer base for professional development tools. (SOURCED: C1.4-5)
- No evidence yet that groomers would find a medieval tax law crossword engaging or useful; the interview script is designed to uncover this but has not been tested. (ASSUMPTION)

Strategy architect recommendation: **REPEAT**. The demand signals confirm a need for CEU‑aligned learning resources, but the specific product idea (medieval tax law crossword packs) lacks validation. The next step is to conduct the Mom Test interviews to determine whether groomers would actually use and pay for such a themed crossword. Until that feedback is obtained, the project should be repeated rather than moved forward or abandoned.

## Work

- **demand_signals:**
  - signal: Dog groomers and salon owners feel frustrated by lack of formal credentialing, leading to costly mistakes and reputational damage; claim_id: C1.4-1
  - signal: The absence of a standardized credentialing system creates hidden costs for salon owners, such as client complaints, safety risks, high turnover, and damage to reputation; claim_id: C1.4-2
  - signal: Dog groomers and salon owners actively seek continuing education (CEU) opportunities tied to certification levels; claim_id: C1.4-3
  - signal: The AKC Professional Grooming Credential (PGC) is a recognized exam that requires 25 CEUs to maintain, indicating a demand for structured learning materials; claim_id: C1.4-4
  - signal: Pet owners spend billions on pet services, creating pressure on groomers to provide top‑tier expertise; claim_id: C1.4-5
- **interview_script:**
  - 1. Can you walk me through a recent time you had to learn a new grooming technique or safety protocol? What did you do to learn it?
  - 2. How do you currently keep up with industry standards or certification requirements? What resources do you use?
  - 3. Have you ever felt uncertain about your knowledge or skills when dealing with a client? What happened?
  - 4. What would make it easier for you to stay compliant with CEU or credentialing requirements?
  - 5. If you had a quick, engaging way to test your knowledge (e.g., a crossword or quiz), how would you feel about using it?
  - 6. How much time are you willing to spend on a learning activity that could help you earn CEUs or improve your credentials?
  - 7. What would convince you to pay for a learning tool or resource?
  - 8. Have you ever used a crossword or puzzle as a learning aid? If so, how did it work for you?
  - 9. What are the biggest barriers that prevent you from completing required CEUs or maintaining your credential?
  - 10. If you could design an ideal learning resource for your profession, what features would it have?

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit |  |  |  |

## Claims ledger

| ID | Claim | Label | Source |
|---|---|---|---|
| C1.4-1 | Professional dog groomers and salon owners feel frustrated when hiring new groomers because there is no formal credentialing to verify skills, leading to costly mistakes such as client complaints, safety risks, high turnover, and reputational damage. | SOURCED | https://nationaldoggroomers.com/pgc |
| C1.4-2 | The lack of a standardized credentialing system in dog grooming creates hidden costs for salon owners, including client complaints, safety risks, high turnover, and damage to reputation. | SOURCED | https://nationaldoggroomers.com/pgc |
| C1.4-3 | Dog groomers and salon owners are actively seeking continuing education (CEU) opportunities to maintain professional status, with specific CEU requirements tied to certification levels. | SOURCED | https://www.paccert.org/maintain-your-certification/ |
| C1.4-4 | The AKC Professional Grooming Credential (PGC) is a recognized standardized exam that measures foundational knowledge, safety, and technical skills, and is valid for five years with a requirement of 25 CEUs to maintain the credential. | SOURCED | https://www.akc.org/groomer-hub/akc-professional-grooming-credential/ |
| C1.4-5 | Pet owners spend billions on pet services and products, creating a market where groomers are expected to provide top-tier services and expertise. | SOURCED | https://www.akc.org/groomer-hub/akc-professional-grooming-credential/ |

## Governance flags

- sycophancy: no department raised a trade-off or pushback

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- 15/15 Phase 1 claims are sourced and verified (ratio 1.00)
- 5 sourced demand signal(s) from step 1.4
- evidence threshold met
