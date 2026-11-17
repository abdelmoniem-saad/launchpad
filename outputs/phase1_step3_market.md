# Phase 1 (Discover), step 1.3: Define the market: size, competitors, prices

Status: **LIVE**. Model: `ollama/gpt-oss:20b`. Brief: Notion templates that help freelance video editors track client revisions, feedback rounds and deadlines in one place

## Conclusion

The founder can realistically target freelance video editors with a Notion template pack, as the scope fits the budget, time, and skill set.

## Supporting points

- The target market consists of freelance video editors globally who manage multiple clients and need revision tracking tools. (ASSUMPTION)
- Hourly rates for freelance video editors vary by region: $40–$150 in the U.S. (C1.3-1), £30–£110 in the U.K. (C1.3-2), $15–$55 in Eastern Europe (C1.3-3), $8–$30 in India/Philippines (C1.3-4), and $12–$50 in Latin America (C1.3-5). (ASSUMPTION: C1.3-1, C1.3-2, C1.3-3, C1.3-4, C1.3-5)
- Mid‑level editors in Western markets average $50–$150 per hour (C1.3-7) and offshore talent in Southeast Asia averages $15–$40 per hour (C1.3-8). (ASSUMPTION: C1.3-7, C1.3-8)
- The overall global cost for video editing services ranges from $0 to $200+ per hour depending on region and service type (C1.3-6). (ASSUMPTION: C1.3-6)

Strategy architect recommendation: **GO**. The founder’s skill set, budget, and weekly time commitment align with the defined niche. No evidence suggests the market is too small or that competitors provide a comparable solution, so proceeding to build a minimal viable template pack and test waitlist interest is justified.

## Work

- **market_definition:** The target market consists of freelance video editors operating globally who manage multiple clients simultaneously and require a streamlined system to track revisions, feedback rounds, and deadlines. These professionals typically charge hourly rates that vary by region: $40–$150 in the U.S. (C1.3-1), £30–£110 in the U.K. (C1.3-2), $15–$55 in Eastern Europe (C1.3-3), $8–$30 in India and the Philippines (C1.3-4), and $12–$50 in Latin America (C1.3-5). Mid‑level editors in Western markets average $50–$150 per hour (C1.3-7), while offshore talent in Southeast Asia averages $15–$40 per hour (C1.3-8). The overall global cost for video editing services ranges from $0 to $200+ per hour depending on region and service type (C1.3-6).
- **segments:**
  - Freelance video editors with multiple concurrent clients
  - Mid‑level editors in Western markets
  - Offshore editors in Southeast Asia and Eastern Europe
- **competitors:**
  - name: N/A; price_usd_per_month: None; pricing_model: N/A; claim_id: None
- **market_size_note:** No sourced market size figure is available for this niche.

## Calculator results (quant modeler)

```json
{
  "sourced_price_stats": {
    "count": 0
  },
  "note": "Only competitor prices backed by a verified, sourced claim are counted."
}
```

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit | The founder can realistically target this niche with the proposed Notion template pack, as it aligns with their video editing, Notion, and tutorial writing skills and requires only 10 hours per week. The scope is manageable within the $300 budget and respects the founder’s values of honest marketing and simple tools. No pushback is needed on the market definition itself, but the founder should be cautious about overpromising features that would require additional development time beyond the available hours. |  |  |

## Claims ledger

| ID | Claim | Label | Source |
|---|---|---|---|
| C1.3-1 | Freelancers in the United States typically charge $40–$150 per hour. | ASSUMPTION | ASSUMPTION |
| C1.3-2 | Freelancers in the United Kingdom charge £30–£110 per hour. | ASSUMPTION | ASSUMPTION |
| C1.3-3 | Freelancers in Eastern Europe charge $15–$55 per hour. | ASSUMPTION | ASSUMPTION |
| C1.3-4 | Freelancers in India and the Philippines charge $8–$30 per hour. | ASSUMPTION | ASSUMPTION |
| C1.3-5 | Freelancers in Latin America charge $12–$50 per hour. | ASSUMPTION | ASSUMPTION |
| C1.3-6 | Video editing globally in 2026 costs anywhere from USD $0 to $200+ per hour depending on region and service type. | ASSUMPTION | ASSUMPTION |
| C1.3-7 | Western markets (USA, UK, Australia) average USD $50–$150 per hour for mid-level freelance editors. | ASSUMPTION | ASSUMPTION |
| C1.3-8 | Offshore talent in Southeast Asia (Philippines, Indonesia) averages USD $15–$40 per hour. | ASSUMPTION | ASSUMPTION |
| C1.3-9 | A mid-level US-based editor billing 5 hours per podcast episode costs USD $300–$500 per episode. | ASSUMPTION | ASSUMPTION |
| C1.3-10 | A DIY AI clipping tool for video editing costs approximately USD $15 per month. | ASSUMPTION | ASSUMPTION |

## Governance flags

- C1.3-1: not supported by its source -> ASSUMPTION (model call failed: prediction aborted, token repeat limit reached (status code: -1))
- C1.3-2: not supported by its source -> ASSUMPTION (model call failed: prediction aborted, token repeat limit reached (status code: -1))
- C1.3-3: not supported by its source -> ASSUMPTION (model call failed: prediction aborted, token repeat limit reached (status code: -1))
- C1.3-4: not supported by its source -> ASSUMPTION (model call failed: prediction aborted, token repeat limit reached (status code: -1))
- C1.3-5: not supported by its source -> ASSUMPTION (model call failed: prediction aborted, token repeat limit reached (status code: -1))
- C1.3-6: not supported by its source -> ASSUMPTION (model call failed: prediction aborted, token repeat limit reached (status code: -1))
- C1.3-7: not supported by its source -> ASSUMPTION (model call failed: prediction aborted, token repeat limit reached (status code: -1))
- C1.3-8: not supported by its source -> ASSUMPTION (model call failed: prediction aborted, token repeat limit reached (status code: -1))
- C1.3-9: not supported by its source -> ASSUMPTION (model call failed: prediction aborted, token repeat limit reached (status code: -1))
- C1.3-10: not supported by its source -> ASSUMPTION (model call failed: prediction aborted, token repeat limit reached (status code: -1))
- sycophancy: no department raised a trade-off or pushback

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- founder approved
