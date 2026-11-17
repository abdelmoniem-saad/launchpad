"""Content limits checked before anything is shown to the founder for approval."""
from __future__ import annotations

import re

BANNED_PRODUCT_TERMS = [
    "crypto", "trading signal", "investment", "stock pick", "forex", "loan",
    "diagnos", "medical advice", "treatment plan", "legal advice", "lawsuit",
    "physical product", "shipping",
]
BANNED_COPY_PATTERNS = [
    r"guarantee[ds]?\s+(income|results|success|profit)",
    r"make \$?\d+.*\b(day|week|month)\b",
    r"testimonial",
    r"only \d+ (left|spots)",
    r"offer ends in",
    r"countdown",
]


def product_block_reason(text: str) -> str | None:
    low = text.lower()
    for term in BANNED_PRODUCT_TERMS:
        if term in low:
            return f"product category not allowed (matched '{term}')"
    return None


def copy_violations(text: str) -> list[str]:
    low = text.lower()
    return [p for p in BANNED_COPY_PATTERNS if re.search(p, low)]
