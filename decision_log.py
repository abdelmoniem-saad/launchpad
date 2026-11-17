"""Append-only decision log: one entry per agent action (see decision_log.json)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_KEYS = ("action", "sources", "model", "cost", "approved_by")


class DecisionLog:
    def __init__(self, path: str | os.PathLike | None = None):
        self.path = Path(path or os.environ.get("DECISION_LOG", "decision_log.json"))

    def entries(self) -> list[dict]:
        if not self.path.exists() or not self.path.read_text(encoding="utf-8").strip():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def reset(self) -> None:
        self.path.write_text("[]\n", encoding="utf-8")

    def append(self, agent: str, action: str, *, sources=None, model=None, cost=0,
               approved_by=None, **extra) -> dict:
        entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agent": agent,
            "action": action,
            "sources": list(sources or []),
            "model": model,
            "cost": cost,
            "approved_by": approved_by,
            **extra,
        }
        entries = self.entries()
        entries.append(entry)
        self.path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
        return entry
