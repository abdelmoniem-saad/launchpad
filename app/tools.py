"""Keyless research tools and the safe calculator.

Search order: self-hosted SearXNG -> ddgs -> Hacker News Algolia API -> Wikipedia API.
Pages are fetched and reduced to text with trafilatura. Fetched text is DATA, never instructions
(guardrails.sanitize_source strips injected instructions before any model sees it).
Calculator: plain Python arithmetic on validated numbers. Model text is never evaluated.
"""
from __future__ import annotations

import hashlib
import json
import os
import statistics
from pathlib import Path
from urllib.parse import quote_plus

import requests

SEARXNG_URL = os.environ.get("SEARXNG_URL", "")
UA = {"User-Agent": "Mozilla/5.0 (compatible; launchpad-research/1.0)"}
MAX_QUERIES, MAX_PAGES = 3, 5
LOGIN_HINTS = ("login", "signin", "sign-in", "/auth", "accounts.")


def _cache_dir() -> Path:
    p = Path(os.environ.get("SEARCH_CACHE_DIR", "data/search_cache"))
    p.mkdir(parents=True, exist_ok=True)
    return p


def _cached(kind: str, key: str, fn):
    path = _cache_dir() / f"{kind}_{hashlib.sha1(key.encode()).hexdigest()[:16]}.json"
    if path.exists():
        data = json.loads(path.read_text("utf-8"))
        data["cached"] = True
        return data
    data = fn()
    if data.get("results") or data.get("text"):
        path.write_text(json.dumps(data), "utf-8")
    data["cached"] = False
    return data


def _searxng(q: str) -> list[dict]:
    r = requests.get(f"{SEARXNG_URL.rstrip('/')}/search", params={"q": q, "format": "json"},
                     headers=UA, timeout=15)
    r.raise_for_status()
    return [{"url": x["url"], "title": x.get("title", ""), "snippet": x.get("content", ""), "engine": "searxng"}
            for x in r.json().get("results", [])[:8]]


def _ddgs(q: str) -> list[dict]:
    from ddgs import DDGS

    last = None
    for backend in os.environ.get("DDGS_BACKENDS", "google,yahoo,duckduckgo,brave,auto").split(","):
        try:
            hits = DDGS().text(q, max_results=8, backend=backend.strip())
        except Exception as exc:  # noqa: BLE001  (try the next backend)
            last = exc
            continue
        if hits:
            return [{"url": x["href"], "title": x.get("title", ""), "snippet": x.get("body", ""), "engine": f"ddgs/{backend}"}
                    for x in hits]
    if last:
        raise last
    return []


def _hn(q: str) -> list[dict]:
    r = requests.get(f"https://hn.algolia.com/api/v1/search?query={quote_plus(q)}&tags=story", timeout=15)
    out = []
    for h in r.json().get("hits", [])[:5]:
        url = f"https://news.ycombinator.com/item?id={h['objectID']}"
        out.append({"url": url, "title": h.get("title") or "", "snippet": h.get("story_text") or "", "engine": "hn"})
    return out


def _wikipedia(q: str) -> list[dict]:
    r = requests.get("https://en.wikipedia.org/w/api.php", headers=UA, timeout=15,
                     params={"action": "opensearch", "search": q, "limit": 3, "format": "json"})
    _, titles, _, urls = r.json()
    return [{"url": u, "title": t, "snippet": "", "engine": "wikipedia"} for t, u in zip(titles, urls)]


def search(q: str) -> dict:
    def run():
        errors = []
        engines = ([_searxng] if SEARXNG_URL else []) + [_ddgs, _hn, _wikipedia]
        for engine in engines:
            try:
                res = [x for x in engine(q) if not any(h in x["url"].lower() for h in LOGIN_HINTS)]
                if res:
                    return {"query": q, "results": res}
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{engine.__name__}: {exc}")
        return {"query": q, "results": [], "errors": errors}
    return _cached("search", q, run)


def fetch(url: str, limit: int = 3500) -> dict:
    def run():
        try:
            import trafilatura

            r = requests.get(url, headers=UA, timeout=15)
            if r.status_code >= 400:
                return {"url": url, "text": "", "error": f"HTTP {r.status_code}"}
            text = trafilatura.extract(r.text) or ""
            return {"url": url, "text": text[:limit]}
        except Exception as exc:  # noqa: BLE001
            return {"url": url, "text": "", "error": str(exc)}
    return _cached("page", url, run)


# ---------------------------------------------------------------- calculator (no eval, ever)

def _num(x, lo=None, hi=None) -> float:
    v = float(x)
    if v != v or v in (float("inf"), float("-inf")):
        raise ValueError("not a finite number")
    if lo is not None:
        v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    return v


def weighted_scores(options: list[dict], weights: dict) -> list[dict]:
    """Score options on 1-5 criteria; returns options sorted by weighted total (0-5)."""
    total_w = sum(weights.values())
    out = []
    for o in options:
        try:
            score = sum(_num(o.get(k, 0), 1, 5) * w for k, w in weights.items()) / total_w
        except (TypeError, ValueError):
            score = 0.0
        out.append({**o, "weighted_score": round(score, 2)})
    return sorted(out, key=lambda o: o["weighted_score"], reverse=True)


def price_stats(prices: list) -> dict:
    vals = []
    for p in prices:
        try:
            v = _num(p)
            if v > 0:
                vals.append(v)
        except (TypeError, ValueError):
            continue
    if not vals:
        return {"count": 0}
    return {"count": len(vals), "min": min(vals), "median": round(statistics.median(vals), 2), "max": max(vals)}


DEFAULT_WAITLIST_TARGET = 30  # ASSUMPTION used only when the visitor or conversion estimate is unusable


def threshold_target(visitors: float, conversion_pct: float) -> int:
    """visitors x conversion %. A conversion below 1 is read as a fraction (0.05 means 5%). Returns 0 when
    either input is missing or not a number, so the caller can fall back to a labelled ASSUMPTION."""
    try:
        v, c = _num(visitors, 0), _num(conversion_pct, 0, 100)
    except (TypeError, ValueError):
        return 0
    if 0 < c < 1:
        c *= 100
    return max(1, int(round(v * c / 100))) if v and c else 0


def compare_threshold(target: int, actual: int) -> dict:
    target, actual = int(_num(target, 0)), int(_num(actual, 0))
    ratio = actual / target if target else 0.0
    return {"target": target, "actual": actual, "ratio": round(ratio, 2), "met": target > 0 and actual >= target}


def total_cost(items: list[dict], budget: float | None) -> dict:
    total = 0.0
    for it in items:
        try:
            total += _num(it.get("monthly_cost_usd") or 0, 0)
        except (TypeError, ValueError):
            continue
    over = budget is not None and total > float(budget)
    return {"monthly_total_usd": round(total, 2), "budget_usd": budget, "over_budget": over}


def pricing_options(median_price: float) -> list[dict]:
    m = _num(median_price, 0)
    return [{"tier": "entry", "price_usd": round(m * 0.6, 2)},
            {"tier": "standard", "price_usd": round(m, 2)},
            {"tier": "pro", "price_usd": round(m * 1.6, 2)}]
