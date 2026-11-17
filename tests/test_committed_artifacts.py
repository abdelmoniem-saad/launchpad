"""The committed decision log and README links must stay valid."""
import json
import re
from pathlib import Path

from app import decision_log as dl

ROOT = Path(__file__).resolve().parent.parent


def test_committed_decision_log_is_valid():
    entries = json.loads((ROOT / "decision_log.json").read_text("utf-8"))
    assert isinstance(entries, list) and entries
    for e in entries:
        for k in dl.REQUIRED_KEYS:
            assert k in e, (k, e)
        assert e["approved_by"] in (None, "founder")
        assert isinstance(e["sources"], list) and isinstance(e["cost"], (int, float))
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", e["timestamp"])


def test_readme_links_point_to_existing_files():
    text = (ROOT / "README.md").read_text("utf-8")
    missing = [p for p in re.findall(r"\]\(([^)#\s]+)", text)
               if not p.startswith(("http://", "https://", "mailto:")) and not (ROOT / p).exists()]
    assert not missing, f"README links to missing files: {missing}"
