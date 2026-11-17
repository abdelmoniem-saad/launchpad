"""Tiny JSON-file store for orders, payments, access grants, refunds and processed events."""
from __future__ import annotations

import json
import os
from pathlib import Path

EMPTY = {"orders": {}, "payments": {}, "grants": {}, "refunds": {}, "processed_events": []}


class Store:
    def __init__(self, path: str | os.PathLike | None = None):
        self.path = Path(path or Path(os.environ.get("STATE_DIR", "data")) / "state.json")
        self.data = json.loads(self.path.read_text("utf-8")) if self.path.exists() else json.loads(json.dumps(EMPTY))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
