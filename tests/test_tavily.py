"""Optional Tavily search: used first when TAVILY_API_KEY is set, falls back to keyless search on error."""
import pytest

from app import tools

PAGE_TEXT = "Freelance editors say client revisions are hard to track. " * 10


class FakeResponse:
    def __init__(self, body, status=200):
        self.body, self.status_code = body, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise tools.requests.HTTPError(f"{self.status_code} Client Error for url: {tools.TAVILY_URL}")

    def json(self):
        return self.body


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setenv("SEARCH_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(tools, "SEARXNG_URL", "")
    return tmp_path


def test_tavily_results_and_page_text_are_used(cache, monkeypatch):
    sent = {}

    def post(url, headers, json, timeout):
        sent.update(url=url, auth=headers["Authorization"], body=json)
        return FakeResponse({"results": [{"url": "https://example.org/a", "title": "A", "content": "snippet",
                                          "raw_content": PAGE_TEXT}]})

    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    monkeypatch.setattr(tools.requests, "post", post)
    monkeypatch.setattr(tools.requests, "get", lambda *a, **k: pytest.fail("page should come from Tavily, not a download"))
    res = tools.search("editor revision tracker")
    assert res["results"][0]["engine"] == "tavily"
    assert sent["auth"] == "Bearer tvly-test" and sent["body"]["include_raw_content"] == "text"
    assert tools.fetch("https://example.org/a")["text"] == PAGE_TEXT.strip()[:tools.PAGE_CHARS]


def test_tavily_error_falls_back_to_keyless_search(cache, monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-bad")
    monkeypatch.setattr(tools.requests, "post", lambda *a, **k: FakeResponse({}, status=401))
    monkeypatch.setattr(tools, "_ddgs", lambda q: [{"url": "https://example.org/b", "engine": "ddgs/google"}])
    res = tools.search("editor revision tracker")
    assert res["results"][0]["engine"] == "ddgs/google"
    assert "tvly-bad" not in str(res)


def test_without_key_tavily_is_never_called(cache, monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.setattr(tools.requests, "post", lambda *a, **k: pytest.fail("Tavily called without a key"))
    monkeypatch.setattr(tools, "_ddgs", lambda q: [{"url": "https://example.org/c", "engine": "ddgs/google"}])
    assert tools.search("editor revision tracker")["results"][0]["engine"] == "ddgs/google"
    assert tools.search_backend().startswith("keyless")
