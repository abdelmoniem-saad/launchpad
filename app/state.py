"""Engagement state and the pydantic schemas every agent output is validated against."""
from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, Optional, TypedDict

from pydantic import BaseModel, Field, field_validator


class Brief(BaseModel):
    idea: str = ""
    target_customer: str = ""
    market: str = ""  # region, e.g. "Egypt / MENA"
    budget_usd: Optional[float] = None
    hours_per_week: Optional[float] = None
    skills: str = ""
    values: str = ""
    product_format: str = ""
    existing_audience: str = ""
    success_goal: str = ""

    REQUIRED: ClassVar[tuple] = ("idea", "target_customer", "budget_usd", "hours_per_week", "skills")
    # Follow-up questions asked once at intake, so the firm understands the case before researching it.
    CLARIFIERS: ClassVar[dict] = {
        "product_format": {"question": "What form should the product take?",
                           "options": ["template pack", "online course", "software tool / web app", "ebook or guide",
                                       "not sure yet"]},
        "existing_audience": {"question": "How many people can you reach today (followers, list, community)?",
                              "options": ["none yet", "under 500", "500 to 5,000", "over 5,000"]},
        "success_goal": {"question": "What would make the next 90 days worth it to you? (a learning goal, not an income target)",
                         "options": None},
    }

    def missing(self) -> list[str]:
        return [f for f in self.REQUIRED if getattr(self, f) in (None, "", 0)]

    def unclarified(self) -> list[str]:
        return [f for f in self.CLARIFIERS if not getattr(self, f)]


class Claim(BaseModel):
    id: str
    text: str
    source_url: Optional[str] = None
    quote: str = ""
    type: Literal["SOURCED", "ASSUMPTION"] = "ASSUMPTION"
    step: str = ""

    @field_validator("type", mode="before")
    @classmethod
    def _norm(cls, v):
        return "SOURCED" if str(v).upper() == "SOURCED" else "ASSUMPTION"


class Threshold(BaseModel):
    metric: str = "waitlist signups"
    target: int = 0
    days: int = 14
    locked: bool = False
    basis: str = ""


class DeptPosition(BaseModel):
    department: str
    position: str = ""
    pushback: str = ""
    tradeoff: str = ""


class SynthesisReport(BaseModel):
    conclusion: str = ""
    key_points: list[dict] = Field(default_factory=list)  # {"text", "claim_ids": [...]}
    open_disagreements: list[str] = Field(default_factory=list)
    recommendation: Literal["go", "repeat", "pivot", "stop"] = "repeat"
    rationale: str = ""

    @field_validator("recommendation", mode="before")
    @classmethod
    def _rec(cls, v):
        v = str(v).lower().strip()
        return v if v in ("go", "repeat", "pivot", "stop") else "repeat"


def merge_dict(old: dict | None, new: dict | None) -> dict:
    """Reducer for parallel department drafts. Returning {"__reset__": True} clears it."""
    if new and new.get("__reset__"):
        return {k: v for k, v in new.items() if k != "__reset__"}
    return {**(old or {}), **(new or {})}


class EngagementState(TypedDict, total=False):
    brief: dict
    run_dir: str
    run_label: str
    clarified: bool
    status: str  # running | stopped | completed
    stop_reason: str
    current_phase: int
    step_index: int
    current_step: str
    departments: list[str]
    messages: list[dict]
    drafts: Annotated[dict, merge_dict]
    work: dict
    pushback_notes: list[str]
    claims: list[dict]
    sources_text: dict
    thresholds: dict
    evidence: dict
    verification_flags: list[str]
    health_flags: list[str]
    pending_actions: list[str]
    report: dict
    quant: dict
    gate_outcome: str
    gate_history: list[dict]
    founder_feedback: str
    founder_decision: str
    repeats: dict
    pivots: int
    blueprint: dict
    cost: dict
    step_blocked: bool
    work_memory: dict
    compliance_note: str
    fast_mode: bool
    health_rerun: bool
    extra: Any
