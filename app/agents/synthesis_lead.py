"""firm.synthesis_lead: conclusion-first report (Pyramid Principle) with open disagreements."""
from __future__ import annotations

import json

from app import config
from app import decision_log as dl
from app.state import SynthesisReport

AGENT = "firm.synthesis_lead"


def write(step: dict, state: dict, note: str = "") -> dict:
    claims = [{"id": c["id"], "text": c["text"], "type": c["type"]} for c in state.get("claims", []) if c.get("step") == step["id"]]
    user = (f"Step {step['id']}: {step['title']}\nBrief: {json.dumps(state['brief'], ensure_ascii=False)}\n"
            f"Work: {json.dumps(state.get('work', {}), ensure_ascii=False)[:3500]}\n"
            f"Calculator results: {json.dumps(state.get('quant', {}), ensure_ascii=False)[:1500]}\n"
            f"Department positions: {json.dumps(state.get('drafts', {}), ensure_ascii=False)[:2500]}\n"
            f"Claims: {json.dumps(claims, ensure_ascii=False)}\n" + (f"Fix these problems: {note}\n" if note else ""))
    reply = config.call_model(AGENT, config.load_prompt("synthesis_lead.md"), user)
    try:
        report = SynthesisReport(**{k: v for k, v in reply.items() if k in SynthesisReport.model_fields}).model_dump()
    except Exception:  # noqa: BLE001  (schema failure -> empty report, caught by the verification gate)
        report = SynthesisReport().model_dump()
    if reply.get("_error"):
        report["conclusion"] = report["conclusion"] or f"(model error: {reply['_error']})"
    known = {c["id"] for c in claims}
    for kp in report["key_points"]:
        ids = [i for i in (kp.get("claim_ids") or []) if i in known]
        kp["claim_ids"] = ids
        kp["label"] = "SOURCED" if any(c["type"] == "SOURCED" for c in claims if c["id"] in ids) else "ASSUMPTION"
    dl.log(AGENT, f"write_report step {step['id']}", model=config.model_name(), cost=0)
    dl.log("firm.strategy_architect", f"gate_recommendation step {step['id']}: {report['recommendation']}",
           model=config.model_name(), cost=0, outcome=report["recommendation"])
    return report
