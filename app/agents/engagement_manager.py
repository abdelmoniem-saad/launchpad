"""firm.engagement_manager: client liaison. Brief completeness, excluded-product check,
opening and closing founder checkpoints, and the final "so what?" review of each report.
"""
from __future__ import annotations

from app import decision_log as dl
from app.guardrails import excluded_reason
from app.state import Brief

AGENT = "firm.engagement_manager"


def missing_fields(brief: dict) -> list[str]:
    return Brief(**{k: v for k, v in brief.items() if k in Brief.model_fields}).missing()


def excluded(brief: dict) -> str | None:
    reason = excluded_reason(" ".join(str(v) for v in brief.values()))
    dl.log("firm.compliance_officer", "excluded_product_check: " + ("EXCLUDED, stop" if reason else "allowed"),
           outcome="stop" if reason else "go")
    return reason


def so_what(report: dict) -> dict:
    """Conclusion must lead; an empty conclusion is flagged to the founder rather than padded."""
    if not report.get("conclusion", "").strip():
        report["conclusion"] = "No defensible conclusion: the firm could not support one with evidence."
        report.setdefault("open_disagreements", []).append("Report had no conclusion; treat this step as weak.")
    return report
