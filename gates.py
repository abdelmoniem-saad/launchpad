"""Gates between phases: go / repeat / pivot / stop, decided from the evidence an agent returns.

Each agent returns `evidence`: a list of {"claim", "source"} where source is a URL or
"ASSUMPTION", plus a self-reported `confidence` in [0, 1]. Weak evidence leads to STOP.
"""
from __future__ import annotations

from dataclasses import dataclass, field

GO, REPEAT, PIVOT, STOP = "go", "repeat", "pivot", "stop"


@dataclass
class GateDecision:
    phase: int
    outcome: str
    sourced_ratio: float
    confidence: float
    reasons: list[str] = field(default_factory=list)


def _is_url(s) -> bool:
    return isinstance(s, str) and s.startswith(("http://", "https://"))


def evaluate(phase: int, result: dict, *, attempt: int = 1, max_attempts: int = 2) -> GateDecision:
    evidence = result.get("evidence") or []
    sourced = sum(1 for e in evidence if _is_url(e.get("source")))
    ratio = sourced / len(evidence) if evidence else 0.0
    conf = float(result.get("confidence") or 0.0)
    reasons = [f"{sourced}/{len(evidence)} claims cite a source URL", f"agent confidence {conf:.2f}"]

    if result.get("blocked_reason"):
        reasons.append(f"blocked: {result['blocked_reason']}")
        return GateDecision(phase, STOP, ratio, conf, reasons)
    if not evidence or ratio < 0.2 or conf < 0.3:
        reasons.append("evidence too weak to continue: recommend STOP")
        return GateDecision(phase, STOP, ratio, conf, reasons)
    if ratio >= 0.5 and conf >= 0.6:
        return GateDecision(phase, GO, ratio, conf, reasons)
    if result.get("pivot_suggestion"):
        reasons.append(f"pivot suggested: {result['pivot_suggestion']}")
        return GateDecision(phase, PIVOT, ratio, conf, reasons)
    if attempt < max_attempts:
        reasons.append("evidence mixed: repeat this step")
        return GateDecision(phase, REPEAT, ratio, conf, reasons)
    reasons.append("still mixed after retry: recommend STOP")
    return GateDecision(phase, STOP, ratio, conf, reasons)
