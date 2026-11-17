"""firm.engagement_manager: client liaison. Brief completeness, excluded-product check,
opening and closing founder checkpoints, and the final "so what?" review of each report.
"""
from __future__ import annotations

from app import decision_log as dl
from app.guardrails import excluded_reason, refused_request
from app.state import Brief

AGENT = "firm.engagement_manager"


def _brief(brief: dict) -> Brief:
    clean = {}
    for k, v in brief.items():
        if k not in Brief.model_fields:
            continue
        if k in ("budget_usd", "hours_per_week"):
            try:
                v = float(str(v).replace("$", "").replace(",", "")) if v not in (None, "") else None
            except ValueError:
                v = None  # unreadable number: ask again
        clean[k] = v
    return Brief(**clean)


def missing_fields(brief: dict) -> list[str]:
    return _brief(brief).missing()


def interview_questions(brief: dict, clarified: bool) -> list[dict]:
    """Required fields that are missing, plus (once) the clarifying questions not yet answered."""
    b = _brief(brief)
    qs = [{"field": f, "question": f"Please tell us your {f.replace('_', ' ')}.", "options": None, "required": True}
          for f in b.missing()]
    if not clarified:
        qs += [{"field": f, "required": False, **Brief.CLARIFIERS[f]} for f in b.unclarified()]
    return qs


def excluded(brief: dict) -> str | None:
    text = " ".join(str(v) for v in brief.values())
    reason = excluded_reason(text)
    dl.log("firm.compliance_officer", "excluded_product_check: " + ("EXCLUDED, stop" if reason else "allowed"),
           outcome="stop" if reason else "go")
    if reason:
        return reason
    refused = refused_request(text)
    dl.log("firm.compliance_officer", "request_check: " + ("REFUSED, stop" if refused else "allowed"),
           outcome="stop" if refused else "go")
    return refused


def so_what(report: dict) -> dict:
    """Conclusion must lead; an empty conclusion is flagged to the founder rather than padded."""
    if not report.get("conclusion", "").strip():
        report["conclusion"] = "No defensible conclusion: the firm could not support one with evidence."
        report.setdefault("open_disagreements", []).append("Report had no conclusion; treat this step as weak.")
    return report
