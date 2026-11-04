"""Web search and page reading for the open-weights backend (owner decision 2026-11-03).

Muse Spark Open on Baseten has no hosted web_search, so members get two function tools instead:
web_search (DuckDuckGo via the free `ddgs` library, no key) and open_page (plain HTTP fetch, HTML or
PDF to text). Plain Python, no model. OpenClient runs them and reports them in the same shape as
Meta's hosted search (web_search_call items), so the board, citations and Evaluator are unchanged.
"""
from __future__ import annotations

import io
import re
from html.parser import HTMLParser
from typing import Any

SEARCH_TOOLS: list[dict[str, Any]] = [
    {"type": "function", "name": "web_search",
     "description": "Search the web (papers, standards, datasheets, manufacturer pages). Returns up to 8 results "
                    "with title, URL and a short snippet. The meeting's rule: constraints and numbers come from the "
                    "literature, and a source counts only when it was found by this search, so search before you "
                    "post concepts or numbers that rest on a source. Open the pages that matter with open_page. "
                    "When you use a source, put its full URL right after the sentence that takes something from it.",
     "parameters": {"type": "object", "additionalProperties": False, "required": ["query"],
                    "properties": {"query": {"type": "string"}}}},
    {"type": "function", "name": "open_page",
     "description": "Open a web page or PDF from a search result and read its text. Give `find` (a few words) to "
                    "get only the passages that contain them, e.g. the value you need.",
     "parameters": {"type": "object", "additionalProperties": False, "required": ["url", "find"],
                    "properties": {"url": {"type": "string"},
                                   "find": {"type": "string", "description": "words to look for; empty for the start of the page"}}}},
]
SEARCH_TOOL_NAMES = {t["name"] for t in SEARCH_TOOLS}

PAGE_CHARS = 6000
_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"}


def web_search(query: str, max_results: int = 8) -> list[dict[str, str]]:
    """[{url, title, snippet}] for a query; empty when every try fails (the member is told so). With three runs
    searching at once the free engines often answer "No results found" for a sound query (10-11 of ~35 searches
    per run on 2026-11-04) and answer it seconds later, so an empty answer is retried twice after a pause."""
    import time

    from ddgs import DDGS

    hits: list[dict[str, Any]] = []
    for pause in (0.0, 3.0, 8.0):
        time.sleep(pause)
        try:
            hits = DDGS().text(query, max_results=max_results, backend="auto") or []
        except Exception:
            hits = []
        if hits:
            break
    return [{"url": str(h.get("href", "")), "title": str(h.get("title", "")), "snippet": str(h.get("body", ""))}
            for h in hits if h.get("href")]


class _Text(HTMLParser):
    _SKIP = frozenset({"script", "style", "noscript", "svg", "nav", "footer", "header", "form"})

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.title = ""
        self._skip = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag in self._SKIP:
            self._skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag in ("p", "br", "li", "tr", "h1", "h2", "h3", "h4", "div", "td", "th"):
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        elif not self._skip:
            self.parts.append(data)


def page_text(url: str, timeout: float = 20.0) -> tuple[str, str]:
    """(title, text) of a page or PDF; raises on HTTP or parse failure."""
    import requests

    r = requests.get(url, headers=_HEADERS, timeout=timeout)
    r.raise_for_status()
    if "pdf" in r.headers.get("Content-Type", "").lower() or url.lower().split("?")[0].endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(r.content))
        text = "\n".join((p.extract_text() or "") for p in reader.pages[:40])
        title = str((reader.metadata or {}).get("/Title", "") or "")
    else:
        parser = _Text()
        parser.feed(r.text)
        text, title = "".join(parser.parts), parser.title
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return " ".join(title.split()), text


def open_page(url: str, find: str = "") -> str:
    """What the member reads: the passages around `find` (or the start of the page), at most PAGE_CHARS."""
    try:
        title, text = page_text(url)
    except Exception as exc:
        return f"could not open {url}: {str(exc)[:200]}"
    if not text:
        return f"{url}: no readable text"
    head = f"{title}\n{url}\n" if title else f"{url}\n"
    words = [w for w in re.findall(r"\w+", find.lower()) if len(w) > 2]
    if not words:
        return head + text[:PAGE_CHARS]
    low = text.lower()
    hits = sorted({m.start() for w in words for m in re.finditer(re.escape(w), low)})
    if not hits:
        return head + f"(none of '{find}' found on the page; start of page)\n" + text[:PAGE_CHARS // 2]
    windows: list[tuple[int, int]] = []
    for h in hits:
        a, b = max(0, h - 400), min(len(text), h + 600)
        if windows and a <= windows[-1][1]:
            windows[-1] = (windows[-1][0], b)
        else:
            windows.append((a, b))
    out, used = [], 0
    for a, b in windows:
        if used >= PAGE_CHARS:
            break
        chunk = text[a:b][: PAGE_CHARS - used]
        out.append("…" + chunk + "…")
        used += len(chunk)
    return head + "\n".join(out)
