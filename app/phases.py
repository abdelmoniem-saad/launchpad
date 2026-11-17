"""Phase and step definitions, the department roster per phase, and which gate each step uses.

Phases 1-2 and the phase 4 pricing step are LIVE (real web research + verification). The rest of
phases 3-6 is MOCKED: the firm writes drafts with the same governance, but nothing is built, sold,
delivered or published.
"""
from __future__ import annotations

DEPARTMENTS_BY_PHASE = {
    1: ["founder_fit"],
    2: ["marketing", "finance"],
    3: ["product"],
    4: ["legal", "sales"],
    5: ["operations"],
    6: ["support"],
}

PHASE_NAMES = {1: "Discover", 2: "Validate", 3: "Build", 4: "Commercial setup", 5: "Launch (sell, deliver, get paid)",
               6: "Operate and learn"}


def roster(phase: int) -> list[str]:
    out = []
    for p in range(1, phase + 1):
        out += DEPARTMENTS_BY_PHASE[p]
    return out


STEPS = [
    {"id": "1.1", "phase": 1, "name": "idea_and_industry", "live": True,
     "title": "Sharpen the idea and decide the industry",
     "queries": ["{idea} {customer} problems", "{idea} market niche {market}", "{customer} biggest challenges tools"],
     "task": "Sharpen the founder's idea into one sentence and propose 3 candidate niches/industries for it. "
             "Score each niche 1-5 on demand (evidence of need), competition (5 = least crowded) and founder_fit "
             "(founder's skills, time and values).",
     "work_keys": '{"sharpened_idea": str, "niches": [{"name": str, "why": str, "demand": 1-5, "competition": 1-5, "founder_fit": 1-5, "claim_ids": [str]}]}',
     "quant": "score_niches"},
    {"id": "1.2", "phase": 1, "name": "scoring", "live": True,
     "title": "Score the idea against 2-3 alternatives",
     "queries": ["{niche} alternatives", "{idea} vs", "best tools for {customer}"],
     "task": "Compare the founder's idea (in the chosen niche) with 2-3 alternative digital product ideas for the same customer. "
             "Score each 1-5 on demand, competition (5 = least crowded), founder_fit, effort (5 = easiest to build).",
     "work_keys": '{"options": [{"name": str, "is_founder_idea": bool, "demand": 1-5, "competition": 1-5, "founder_fit": 1-5, "effort": 1-5, "claim_ids": [str]}]}',
     "quant": "score_options"},
    {"id": "1.3", "phase": 1, "name": "market", "live": True,
     "title": "Define the market: size, competitors, prices",
     "queries": ["{niche} pricing", "{niche} competitors {market}", "{niche} market size"],
     "task": "Define the market: who buys, segments, the main competitors and their published prices (only prices found in the sources), "
             "and any sourced market size figure.",
     "work_keys": '{"market_definition": str, "segments": [str], "competitors": [{"name": str, "price_usd_per_month": number or null, "pricing_model": str, "claim_id": str or null}], "market_size_note": str}',
     "quant": "price_stats"},
    {"id": "1.4", "phase": 1, "name": "demand_and_interviews", "live": True, "gate": "evidence",
     "title": "Demand signals and a Mom Test interview script",
     "queries": ["{niche} reddit", "\"looking for\" {niche} {customer}", "{customer} frustrated with {niche}"],
     "task": "List demand signals found in the sources (people describing the problem, asking for solutions, paying for workarounds). "
             "Label them as signals, never as signups. Write a Mom Test interview script: questions about past behaviour, "
             "no pitching, no hypotheticals; and who to interview.",
     "work_keys": '{"demand_signals": [{"signal": str, "claim_id": str}], "interview_script": [str], "who_to_interview": str}',
     "quant": None},
    {"id": "2.1", "phase": 2, "name": "lean_canvas", "live": True,
     "title": "Lean Canvas",
     "queries": ["{niche} customer acquisition channels", "{niche} unfair advantage"],
     "task": "Fill the Lean Canvas for the chosen idea using the earlier steps' findings.",
     "work_keys": '{"problem": [str], "customer_segments": [str], "unique_value_proposition": str, "solution": [str], "channels": [str], "revenue_streams": [str], "cost_structure": [str], "key_metrics": [str], "unfair_advantage": str}',
     "quant": None},
    {"id": "2.2", "phase": 2, "name": "demand_test", "live": True,
     "title": "Demand test: landing page draft and a waitlist target",
     "queries": ["landing page waitlist conversion rate", "{niche} community size"],
     "task": "Draft an honest landing page (MOCKED, never published) with a waitlist sign-up, list channels to drive visitors, "
             "and propose a demand test: expected visitors in the test window and an expected conversion % (both ASSUMPTION unless sourced). "
             "No reviews, testimonials, urgency or income promises.",
     "work_keys": '{"landing_page_markdown": str, "channels": [str], "test_days": int, "expected_visitors": number, "expected_conversion_pct": number, "basis": str}',
     "quant": "threshold", "actions": [("publish", "landing_page_markdown", "Publish the landing page draft")]},
    {"id": "2.3", "phase": 2, "name": "collaborations", "live": True,
     "title": "Collaborations: communities and partners",
     "queries": ["{customer} community forum", "{niche} newsletter", "{customer} association {market}"],
     "task": "Find communities and potential partners where the target customer gathers (from the sources) and draft short, honest "
             "outreach messages in the founder's own name (MOCKED, never sent).",
     "work_keys": '{"communities": [{"name": str, "why": str, "claim_id": str or null}], "partners": [{"name": str, "why": str, "claim_id": str or null}], "outreach_drafts": [{"to": str, "channel": str, "message": str}]}',
     "quant": None, "actions": [("send", "outreach_drafts", "Send outreach drafts")]},
    {"id": "2.4", "phase": 2, "name": "demand_results", "live": True, "gate": "demand", "needs_results": True,
     "title": "Founder enters results; demand gate",
     "queries": [], "task": "", "work_keys": "", "quant": None},
    {"id": "2.5", "phase": 2, "name": "company_blueprint", "live": True,
     "title": "Company blueprint",
     "queries": ["freelance {niche} hourly rate", "no-code automation tools pricing"],
     "task": "Design the company: one role per department on the roster. For each, decide founder does it / automate it / hire later, "
             "with the reason and a monthly cost (sourced, or ASSUMPTION). Give each department a 3-5 item backlog. "
             "Any job post is a draft only (MOCKED).",
     "work_keys": '{"roles": [{"department": str, "role": str, "choice": "founder|automate|hire_later", "reason": str, "monthly_cost_usd": number, "cost_claim_id": str or null}], "backlog": {"<department>": [str]}, "job_post_drafts": [{"role": str, "text": str}]}',
     "quant": "blueprint_cost", "actions": [("hire", "job_post_drafts", "Post job drafts")]},
    {"id": "3.1", "phase": 3, "name": "mvp_spec", "live": False,
     "title": "MVP spec, user docs draft and test plan (MOCKED)", "queries": [],
     "task": "Write the MVP spec (at most 5 core features, out of scope list), a short user docs draft and a test plan.",
     "work_keys": '{"core_features": [str], "out_of_scope": [str], "user_docs_draft": str, "test_plan": [str]}', "quant": None},
    {"id": "4.1", "phase": 4, "name": "pricing", "live": True,
     "title": "Pricing: sourced price points and calculator tiers (no payments)",
     "queries": ["{niche} price", "{niche} template pricing", "{customer} pay for {niche}"],
     "task": "Find the prices that comparable products publish in the sources (one entry per product, with the claim_id of the claim "
             "that quotes the price; never a price that is not in the sources) and say whether each is one-time or monthly. "
             "Pricing tiers are computed by the calculator from the sourced prices, never by you; comment on them. "
             "Say which features stay free: core features must never be paywalled. No payment setup of any kind.",
     "work_keys": '{"price_points": [{"product": str, "price_usd": number, "billing": "one_time|monthly|yearly", "claim_id": str}], "free_features": [str], "tier_notes": str}',
     "quant": "pricing"},
    {"id": "4.2", "phase": 4, "name": "policies", "live": False,
     "title": "Draft terms, privacy and refund policies (MOCKED, not legal advice)", "queries": [],
     "task": "Draft terms of service, privacy policy and refund policy summaries in plain language, labelled as drafts that are not "
             "legal advice and must be reviewed by the founder (and a lawyer where needed) before use.",
     "work_keys": '{"terms_summary": str, "privacy_summary": str, "refund_policy": str}', "quant": None},
    {"id": "5.1", "phase": 5, "name": "launch_drafts", "live": False,
     "title": "Store page and launch post drafts; delivery (MOCKED)", "queries": [],
     "task": "Draft the store page and one launch post in the founder's own name, and describe how buyers would receive the product "
             "automatically (MOCKED). No urgency, reviews, testimonials or income promises.",
     "work_keys": '{"store_page_markdown": str, "launch_post": str, "delivery_plan": str}', "quant": None,
     "actions": [("publish", "store_page_markdown", "Publish the store page"), ("publish", "launch_post", "Publish the launch post")]},
    {"id": "6.1", "phase": 6, "name": "operate_plan", "live": False,
     "title": "Support replies, metrics plan, persevere-or-pivot memo (MOCKED)", "queries": [],
     "task": "Draft 3 support reply templates, a metrics plan (what to track and the decision threshold for each) and a persevere-or-pivot memo template.",
     "work_keys": '{"support_replies": [str], "metrics_plan": [{"metric": str, "threshold": str}], "persevere_or_pivot_memo": str}', "quant": None},
]

STEP_INDEX = {s["id"]: i for i, s in enumerate(STEPS)}
