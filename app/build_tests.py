"""Phase 3 tests-pass gate: deterministic checks on the MVP the firm built in step 3.1.

The model writes the product; this code decides whether it passes. No model call, no network.
Every check is named, so a failing build tells the founder (and the redo) exactly what to fix.
"""
from __future__ import annotations

import re

from app.guardrails import rule_violations

MAX_FEATURES = 5
MIN_FEATURE_WORDS = 60
MIN_DOCS_WORDS = 80
PLACEHOLDERS = re.compile(r"\b(todo|tbd|lorem ipsum|placeholder|insert (here|text|your)|coming soon|xxx+)\b|\[[^\]]*(insert|your|tbd)[^\]]*\]",
                          re.I)


def _words(text) -> int:
    return len(re.findall(r"\w+", str(text or "")))


def _features(work: dict) -> list[dict]:
    raw = work.get("core_features")
    return [f for f in raw if isinstance(f, dict)] if isinstance(raw, list) else []


def product_text(work: dict) -> str:
    """Everything a buyer would receive, as one text (used by the rule guard and the placeholder check)."""
    parts = [str(work.get("product_title") or "")]
    parts += [f"{f.get('name', '')}\n{f.get('content', '')}" for f in _features(work)]
    parts.append(str(work.get("user_docs") or ""))
    return "\n\n".join(parts)


def run(work: dict) -> dict:
    """Returns {"tests": [{"name", "passed", "detail"}], "passed", "total", "all_passed"}."""
    feats = _features(work)
    names = [str(f.get("name") or "").strip() for f in feats]
    docs = str(work.get("user_docs") or "")
    plan = [p for p in work.get("test_plan", []) if isinstance(p, dict)] if isinstance(work.get("test_plan"), list) else []
    tests = []

    def check(name: str, passed: bool, detail: str) -> None:
        tests.append({"name": name, "passed": bool(passed), "detail": detail})

    check("has a product title", bool(str(work.get("product_title") or "").strip()), repr(work.get("product_title")))
    check(f"1 to {MAX_FEATURES} core features", 1 <= len(feats) <= MAX_FEATURES, f"{len(feats)} feature(s)")
    thin = [n or "(unnamed)" for n, f in zip(names, feats) if not n or _words(f.get("content")) < MIN_FEATURE_WORDS]
    check(f"every feature is named and has real content (>= {MIN_FEATURE_WORDS} words)", feats and not thin,
          "too thin: " + ", ".join(thin) if thin else "ok")
    check(f"user docs exist (>= {MIN_DOCS_WORDS} words)", _words(docs) >= MIN_DOCS_WORDS, f"{_words(docs)} words")
    undocumented = [n for n in names if n and n.lower() not in docs.lower()]
    check("user docs explain every feature by name", feats and not undocumented,
          "missing: " + ", ".join(undocumented) if undocumented else "ok")
    planned = {str(p.get("feature") or "").strip().lower() for p in plan if str(p.get("check") or "").strip()}
    untested = [n for n in names if n and n.lower() not in planned]
    check("the test plan has a check for every feature", feats and not untested,
          "no check for: " + ", ".join(untested) if untested else f"{len(plan)} check(s)")
    text = product_text(work)
    ph = sorted({m.group(0) for m in PLACEHOLDERS.finditer(text)})
    check("no placeholder text", not ph, "found: " + ", ".join(ph) if ph else "ok")
    bad = rule_violations(text)
    check("rule guard: no income promises, reviews, urgency, impersonation or card data", not bad,
          "violations: " + ", ".join(bad) if bad else "clean")
    passed = sum(t["passed"] for t in tests)
    return {"tests": tests, "passed": passed, "total": len(tests), "all_passed": passed == len(tests)}


def failures(result: dict) -> list[str]:
    return [f"{t['name']} ({t['detail']})" for t in result.get("tests", []) if not t["passed"]]
