"""decision_log.json: one entry per agent action.

Required keys: timestamp, agent, action, sources (URL list), model (str or null),
cost (USD number), approved_by ("founder" for gated actions, otherwise null).
Agent names use the prefixes firm.*, dept.* and governance.*.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_KEYS = ("timestamp", "agent", "action", "sources", "model", "cost", "approved_by")
_lock = threading.Lock()


def log_path() -> Path:
    return Path(os.environ.get("DECISION_LOG", "decision_log.json"))


def entries() -> list[dict]:
    p = log_path()
    if not p.exists() or not p.read_text(encoding="utf-8").strip():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def reset() -> None:
    log_path().write_text("[]\n", encoding="utf-8")


def log(agent: str, action: str, *, sources=None, model=None, cost=0, approved_by=None, **extra) -> dict:
    if approved_by not in (None, "founder"):
        raise ValueError("approved_by must be 'founder' or None")
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent": agent,
        "action": action,
        "sources": sorted({s for s in (sources or []) if isinstance(s, str) and s.startswith("http")}),
        "model": model,
        "cost": cost,
        "approved_by": approved_by,
        **extra,
    }
    with _lock:
        data = entries()
        data.append(entry)
        log_path().write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return entry
