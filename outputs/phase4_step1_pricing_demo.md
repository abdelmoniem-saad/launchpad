# Phase 4 (Commercial setup), step 4.1: Pricing: sourced price points and calculator tiers (no payments)

Status: **LIVE**. Model: `ollama/gpt-oss:20b`. Brief: Notion templates that help freelance video editors track client revisions, feedback rounds and deadlines in one place

> **DEMO INPUT:** the step 2.4 waitlist result in this run is hypothetical; no real demand test was run, so everything from step 2.4 on is a demonstration, not validated demand.

## Conclusion

The founder must launch the product as a free template pack and cannot set paid pricing tiers without sourced price data.

## Supporting points

- All core Notion template pack features must remain free because no comparable product prices are available to derive tiers. (ASSUMPTION)
- No pricing tiers can be derived from the calculator because it requires sourced price points, which are absent. (ASSUMPTION)
- The founder’s time and skill constraints align with delivering a free product within the allocated 10 hours per week. (ASSUMPTION)
- Marketing, finance, product, legal, and sales all agree that a free offer is the only viable option at this stage. (ASSUMPTION)

Strategy architect recommendation: **GO**. With no sourced price data, the only defensible strategy is to offer the template pack for free and focus on building a waitlist to validate demand. All departments concur that this approach aligns with resource constraints and legal simplicity, making it safe to proceed.

## Work

- **price_points:**
- **free_features:**
  - All core Notion template pack features
- **tier_notes:** No pricing tiers can be derived because no comparable product prices are available in the provided claims. The calculator cannot generate tiers without sourced data. Core features must remain free to avoid paywalls.

## Calculator results (quant modeler)

```json
{
  "counted_price_points": [],
  "not_counted": [],
  "rule": "A price counts only if its claim is SOURCED (after verification), its quote is on the fetched page, and the quote contains that price.",
  "pricing_tiers": [],
  "basis": "no sourced prices: tiers left to the founder (ASSUMPTION)"
}
```

## Department positions and pushback

| Department | Position | Pushback | Trade-off |
|---|---|---|---|
| founder_fit | The founder can only commit to free core features and cannot set paid tiers without sourced prices. This aligns with the founder’s time and skill constraints. |  |  |
| marketing | Marketing cannot propose demand tests that rely on paid tiers when no price data exists. | Cannot validate pricing strategy without comparable data; must focus on free offer for waitlist. |  |
| finance | Finance confirms that no additional costs are incurred by setting up paid tiers without data. |  |  |
| product | Product can deliver the free template pack within the founder’s weekly hours. |  |  |
| legal | Legal notes that no terms are needed for a free product. |  |  |
| sales | Sales confirms that no paid offer can be created without sourced price points. |  |  |

## Claims ledger

No claims could be sourced in this step; everything above is ASSUMPTION.

## Founder checkpoint

Decision: **approve**

## Gate

Outcome: **GO**

- founder approved
