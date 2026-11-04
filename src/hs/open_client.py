"""OpenClient — the open-weights backend: same interface as MetaClient, text on Muse Spark Open.

Every text and picture-reading role (council, Manager, Evaluator, optimizer, VLM writer, critics) goes to
Meta's open-weights Muse Spark Open on Baseten's Responses API. Two things Baseten lacks are done here so
the rest of HS runs unchanged (probe: runs/open_probe/, 2026-11-03):
- previous_response_id (HTTP 501): each response's full input and output is kept and resent; Baseten's
  prompt cache bills the resent part at the cached rate.
- hosted web_search (accepted but never searches; the reply invents [1][2] sources): replaced by the
  web_search / open_page function tools of hs.open_search, run here, and reported back as Meta-style
  web_search_call items plus url_citation spans, so search_sources() and the board see the same shape.
Pictures (image_edit) stay on Meta's muse-image-1.0; SAM is inherited from MetaClient until the Modal
SAM 3.1 app replaces it.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

from pydantic import BaseModel

from hs import config
from hs.client import MetaClient, _is_truncated, _output_text, estimate_call_usd
from hs.open_search import SEARCH_TOOL_NAMES, SEARCH_TOOLS, open_page, web_search
from hs.schemas import make_strict_schema


def load_env(path: Path | None = None) -> None:
    """Keys from the folder's git-ignored .env (shell variables win)."""
    env = Path(path or config.PROJECT_ROOT / ".env")
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            if v.strip():
                os.environ.setdefault(k.strip(), v.strip())


def _replay_items(output: list[Any]) -> list[dict[str, Any]]:
    """A response's output as input items for the next call (reasoning is not resent)."""
    items: list[dict[str, Any]] = []
    for it in output or []:
        kind = getattr(it, "type", None)
        if kind == "function_call":
            items.append({"type": "function_call", "call_id": it.call_id, "name": it.name,
                          "arguments": it.arguments or "{}"})
        elif kind == "message":
            text = "".join(getattr(b, "text", "") or "" for b in getattr(it, "content", []) or [])
            if text:
                items.append({"type": "message", "role": "assistant",
                              "content": [{"type": "output_text", "text": text}]})
    return items


_URL = re.compile(r"https?://[^\s)\]>\"'`]+")


def _citations(text: str, sources: dict[str, str]) -> list[Any]:
    """url_citation spans (as Meta's search returns them) for every searched URL written in the reply:
    the span is the sentence that ends with or contains the URL."""
    anns: list[Any] = []
    for m in _URL.finditer(text):
        url = m.group(0).rstrip(".,;:")
        if url not in sources:
            continue
        start = max(text.rfind(". ", 0, m.start()), text.rfind("\n", 0, m.start()))
        start = 0 if start < 0 else start + 1
        anns.append(NS(type="url_citation", url=url, title=sources[url], start_index=start, end_index=m.start()))
    return anns


class OpenClient(MetaClient):
    """MetaClient with text on Baseten's Muse Spark Open (see module doc)."""

    def __init__(self, run_dir: Path | None = None, max_cost: float | None = None) -> None:
        load_env()
        super().__init__(run_dir=run_dir, max_cost=max_cost)
        self._open_sdk: Any = None
        self._chains: dict[str, list[dict[str, Any]]] = {}

    def _open(self) -> Any:
        if self._open_sdk is None:
            from openai import OpenAI

            self._open_sdk = OpenAI(base_url=config.OPEN_BASE_URL, api_key=os.environ["BASETEN_API_KEY"])
        return self._open_sdk

    def _call(self, role: str, kwargs: dict[str, Any], tools: list[dict[str, Any]] | None) -> Any:
        """One billed Baseten call: budget check, create (MetaClient's retry rules), record."""
        self.cost.check_budget(estimate_call_usd(kwargs.get("instructions", ""), kwargs["input"],
                                                 kwargs["max_output_tokens"], tools))
        resp = self._create_with_retries(kwargs, sdk=self._open())
        from hs.client import _usage_from_response

        self.cost.record(role, config.OPEN_TEXT_MODEL, _usage_from_response(resp))
        return resp

    def responses(self, *, role: str, instructions: str, input_items: list[dict[str, Any]],
                  tools: list[dict[str, Any]] | None = None, schema_model: type[BaseModel] | None = None,
                  max_output_tokens: int | None = None, previous_response_id: str | None = None,
                  parallel_tool_calls: bool | None = None, include: list[str] | None = None) -> Any:
        rc = config.ROLES[role]
        max_tokens = max_output_tokens or rc.max_output_tokens
        if previous_response_id is not None and previous_response_id not in self._chains:
            raise RuntimeError(f"previous response {previous_response_id} not found or expired")
        history = list(self._chains.get(previous_response_id, [])) + list(input_items)
        searching = any(t.get("type") == "web_search" for t in tools or [])
        sent_tools = [t for t in tools or [] if t.get("type") != "web_search"] + (SEARCH_TOOLS if searching else [])
        kwargs: dict[str, Any] = {"model": config.OPEN_TEXT_MODEL, "instructions": instructions,
                                  "reasoning": {"effort": config.OPEN_EFFORT.get(rc.effort, "medium")},
                                  "max_output_tokens": max_tokens}
        if sent_tools:
            kwargs["tools"] = sent_tools
        if parallel_tool_calls is not None:
            kwargs["parallel_tool_calls"] = parallel_tool_calls
        if schema_model is not None:
            kwargs["text"] = {"format": {"type": "json_schema", "name": schema_model.__name__,
                                         "schema": make_strict_schema(schema_model), "strict": True}}

        shown: list[Any] = []          # Meta-style web_search_call items for this response
        seen: dict[str, str] = {}      # url -> title, for citation spans
        actions = 0
        usage = {"input_tokens": 0, "cached": 0, "output_tokens": 0, "reasoning": 0}
        while True:
            kwargs["input"] = history
            resp = self._call(role, kwargs, tools)
            if schema_model is not None and _is_truncated(resp, max_tokens, _output_text(resp)):
                kwargs["max_output_tokens"] = min(max_tokens * 2, 32000)
                resp = self._call(role, kwargs, tools)
            u = getattr(resp, "usage", None)
            if u is not None:
                usage["input_tokens"] += int(getattr(u, "input_tokens", 0) or 0)
                usage["output_tokens"] += int(getattr(u, "output_tokens", 0) or 0)
                usage["cached"] += int(getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0)
                usage["reasoning"] += int(getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", 0) or 0)
            output = list(getattr(resp, "output", []) or [])
            history = history + _replay_items(output)
            search_calls = [i for i in output if getattr(i, "type", None) == "function_call"
                            and getattr(i, "name", "") in SEARCH_TOOL_NAMES]
            for call in search_calls:
                try:
                    args = json.loads(call.arguments or "{}")
                except Exception:
                    args = {}
                actions += 1
                if actions > config.MAX_SEARCH_ACTIONS_PER_CALL:
                    result = "search budget for this reply is used up — answer now with what you have"
                elif call.name == "web_search":
                    query = str(args.get("query", ""))
                    hits = web_search(query)
                    for h in hits:
                        seen.setdefault(h["url"], h["title"])
                    # Snippets are kept from the board (Meta's search returns them empty): what a member
                    # "took from" a source is only what they wrote about it.
                    shown.append(NS(type="web_search_call", status="completed",
                                    action=NS(type="search", query=query),
                                    results=[{"url": h["url"], "title": h["title"], "snippet": ""} for h in hits]))
                    result = "\n".join(f"- {h['title']}\n  {h['url']}\n  {h['snippet']}" for h in hits) or \
                        "no results (try other words)"
                else:
                    url = str(args.get("url", ""))
                    shown.append(NS(type="web_search_call", status="completed",
                                    action=NS(type="open_page", url=url), results=None))
                    seen.setdefault(url, "")
                    result = open_page(url, str(args.get("find", "")))
                history.append({"type": "function_call_output", "call_id": call.call_id, "output": result})
            others = [i for i in output if getattr(i, "type", None) == "function_call"
                      and getattr(i, "name", "") not in SEARCH_TOOL_NAMES]
            if search_calls and not others and not _output_text(resp).strip():
                if actions >= config.MAX_SEARCH_ACTIONS_PER_CALL:  # budget used: offer no search tools
                    rest = [t for t in sent_tools if t.get("name") not in SEARCH_TOOL_NAMES]
                    if rest:
                        kwargs["tools"] = rest
                    else:
                        kwargs.pop("tools", None)
                continue  # the model is still searching: run the next round itself, like a hosted tool
            break

        out_items: list[Any] = list(shown)
        for it in output:
            kind = getattr(it, "type", None)
            if kind == "function_call" and it.name not in SEARCH_TOOL_NAMES:
                out_items.append(NS(type="function_call", name=it.name, arguments=it.arguments,
                                    call_id=it.call_id, status="completed"))
            elif kind == "message":
                blocks = []
                for b in getattr(it, "content", []) or []:
                    text = getattr(b, "text", "") or ""
                    blocks.append(NS(type="output_text", text=text, annotations=_citations(text, seen)))
                out_items.append(NS(type="message", role="assistant", content=blocks))
        rid = f"open_{uuid.uuid4().hex}"
        self._chains[rid] = history
        return NS(id=rid, status=getattr(resp, "status", "completed"), output=out_items,
                  usage=NS(input_tokens=usage["input_tokens"], output_tokens=usage["output_tokens"],
                           input_tokens_details=NS(cached_tokens=usage["cached"]),
                           output_tokens_details=NS(reasoning_tokens=usage["reasoning"])))
