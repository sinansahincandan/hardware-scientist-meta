"""MetaClient — all model calls go through here (Responses API only, spec §9).

Field names are exactly those of spec §9. `instructions` is resent on every
call (it is NOT carried by previous_response_id).
"""
from __future__ import annotations

import base64
import fcntl
import json
import os
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from hs import config
from hs.schemas import make_strict_schema


class BudgetExceeded(Exception):
    """Raised BEFORE a call that would cross a cost cap, or on a provider billing error (HTTP 402).

    Never retried: every caller lets it propagate so the controller stops cleanly."""


def price_usage(usage: dict[str, Any]) -> float:
    p = config.PRICES
    cached = int(usage.get("cached_input_tokens", 0) or 0)
    inp = int(usage.get("input_tokens", 0) or 0)
    out = int(usage.get("output_tokens", 0) or 0)
    searches = int(usage.get("searches", 0) or 0)
    images = int(usage.get("images", 0) or 0)
    sam_calls = int(usage.get("sam_calls", 0) or 0)
    return (
        max(inp - cached, 0) * p["input_per_1m"] / 1e6
        + cached * p["cached_input_per_1m"] / 1e6
        + out * p["output_per_1m"] / 1e6
        + searches * p["web_search_per_query"]
        + images * p["image_each"]
        + sam_calls * p["sam_image_each"]
        + float(usage.get("modal_seconds", 0) or 0) * p.get("modal_gpu_per_second", 0.0)
    )


def estimate_call_usd(instructions: str, input_items: list[dict[str, Any]], max_output_tokens: int,
                      tools: list[dict[str, Any]] | None = None) -> float:
    """Worst-case price of one Responses call, for the pre-call budget check: input at the
    uncached rate (chars / 4, images ~1.5k tokens each), full max_output_tokens, and three
    searches when web_search is offered. Chained calls also re-bill earlier context; the
    margin between this estimate and the cap absorbs that."""
    p = config.PRICES
    chars = len(instructions)
    images = 0
    for item in input_items:
        for block in item.get("content", []) if isinstance(item.get("content"), list) else []:
            if block.get("type") == "input_image":
                images += 1
            else:
                chars += len(str(block.get("text", "")))
        if item.get("type") == "function_call_output":
            chars += len(str(item.get("output", "")))
    in_tokens = chars / 4 + images * 1500
    searches = 3 if any(t.get("type") == "web_search" for t in tools or []) else 0
    return (in_tokens * p["input_per_1m"] / 1e6 + max_output_tokens * p["output_per_1m"] / 1e6
            + searches * p["web_search_per_query"])


class BudgetLedger:
    """Project-wide ledger of real Meta spend (round-3 item 0), capped at MAX_TOTAL_SPEND_USD.

    One JSONL line per real call (time, run id, role, model, tokens, images, SAM calls,
    searches, estimated USD from config.PRICES). Read under a file lock before every call
    and appended after it, so parallel runs and commands share one total.
    """

    def __init__(self, path: Path | None = None, cap_usd: float | None = None) -> None:
        self.path = Path(path or config.BUDGET_LEDGER_PATH)
        self.cap_usd = config.MAX_TOTAL_SPEND_USD if cap_usd is None else cap_usd

    @contextmanager
    def _locked(self) -> Iterator[None]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path.with_suffix(".lock"), "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def _entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def entries(self) -> list[dict[str, Any]]:
        with self._locked():
            return self._entries()

    def total(self) -> float:
        return sum(float(e.get("usd", 0.0)) for e in self.entries())

    def check(self, estimated_usd: float) -> None:
        spent = self.total()
        if spent + estimated_usd > self.cap_usd:
            raise BudgetExceeded(
                f"budget cap ${self.cap_usd:.2f} would be exceeded "
                f"(spent ${spent:.4f} across all runs, next call est. ${estimated_usd:.4f}; "
                f"ledger {self.path})"
            )

    def add(self, run_id: str, entry: dict[str, Any]) -> float:
        record = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "run_id": run_id, **entry}
        with self._locked():
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
            total = sum(float(e.get("usd", 0.0)) for e in self._entries())
        print(f"[budget] {entry.get('role')} +${float(entry.get('usd', 0.0)):.4f} | total ${total:.4f} "
              f"of ${self.cap_usd:.2f} | left ${self.cap_usd - total:.4f}", file=sys.stderr, flush=True)
        return total

    def per_run(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for e in self.entries():
            totals[e.get("run_id", "")] = totals.get(e.get("run_id", ""), 0.0) + float(e.get("usd", 0.0))
        return totals


class CostLog:
    def __init__(self, run_dir: Path | None, max_cost: float | None = None,
                 ledger: BudgetLedger | None = None) -> None:
        self.run_dir = run_dir
        self.max_cost = config.MAX_COST_USD_PER_RUN if max_cost is None else max_cost
        self.ledger = ledger
        self.entries: list[dict[str, Any]] = []
        self.total_usd = 0.0
        if run_dir is not None:
            existing = run_dir / "cost.json"
            if existing.exists():
                try:
                    data = json.loads(existing.read_text(encoding="utf-8"))
                    self.entries = list(data.get("entries", []))
                    self.total_usd = float(data.get("total_usd", 0.0))
                except Exception:
                    pass

    def check_budget(self, estimated_usd: float = 0.05) -> None:
        if self.total_usd + estimated_usd > self.max_cost:
            raise BudgetExceeded(
                f"cost cap ${self.max_cost:.2f} would be exceeded "
                f"(spent ${self.total_usd:.4f}, next call est. ${estimated_usd:.4f})"
            )
        if self.ledger is not None:
            self.ledger.check(estimated_usd)

    def record(self, role: str, model: str, usage: dict[str, Any]) -> float:
        usd = price_usage(usage)
        self.entries.append(
            {
                "role": role,
                "model": model,
                "input": int(usage.get("input_tokens", 0) or 0),
                "cached_input": int(usage.get("cached_input_tokens", 0) or 0),
                "output": int(usage.get("output_tokens", 0) or 0),
                "reasoning": int(usage.get("reasoning_tokens", 0) or 0),
                "searches": int(usage.get("searches", 0) or 0),
                "images": int(usage.get("images", 0) or 0),
                "sam_calls": int(usage.get("sam_calls", 0) or 0),
                "modal_seconds": round(float(usage.get("modal_seconds", 0) or 0), 3),
                "usd": round(usd, 6),
            }
        )
        self.total_usd += usd
        self.flush()
        if self.ledger is not None:
            self.ledger.add(self.run_dir.name if self.run_dir is not None else "no-run", self.entries[-1])
        return usd

    def note(self, role: str) -> None:
        """Zero-cost marker entry (e.g. counting a retried turn in cost.json)."""
        self.entries.append({"role": role, "model": "", "input": 0, "cached_input": 0,
                             "output": 0, "reasoning": 0, "searches": 0, "images": 0, "usd": 0.0})
        self.flush()

    def flush(self) -> None:
        if self.run_dir is None:
            return
        self.run_dir.mkdir(parents=True, exist_ok=True)
        payload = {"total_usd": round(self.total_usd, 6), "entries": self.entries}
        (self.run_dir / "cost.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _usage_from_response(resp: Any) -> dict[str, Any]:
    usage = getattr(resp, "usage", None)
    if usage is None:
        return {"input_tokens": 0, "output_tokens": 0}
    def g(obj: Any, *names: str) -> int:
        for n in names:
            v = getattr(obj, n, None)
            if v is None and isinstance(obj, dict):
                v = obj.get(n)
            if v is not None:
                try:
                    return int(v)
                except Exception:
                    return 0
        return 0

    details = getattr(usage, "input_tokens_details", None)
    cached = g(details, "cached_tokens") if details is not None else 0
    out_details = getattr(usage, "output_tokens_details", None)
    reasoning = g(out_details, "reasoning_tokens") if out_details is not None else 0
    # Hosted web_search is billed per query on top of tokens (QUESTIONS.md 14.2:
    # each search shows up as a `web_search_call` output item).
    searches = sum(1 for item in getattr(resp, "output", []) or []
                   if getattr(item, "type", None) == "web_search_call")
    return {
        "input_tokens": g(usage, "input_tokens"),
        "cached_input_tokens": cached,
        "output_tokens": g(usage, "output_tokens"),
        "reasoning_tokens": reasoning,
        "searches": searches,
    }


def search_sources(resp: Any) -> list[dict[str, Any]]:
    """Every source a response's web searches touched (B8). Meta's search is a small browser: it searches
    (`web_search_call.results`, needs include=["web_search_call.results"], spec §14.2; snippets come back empty),
    opens and searches inside pages (open_page / find_in_page actions), and ties each sentence of the reply to its
    source (url_citation annotations with character spans). Each source: {url, title, snippet, query, cited, read};
    snippet is the cited sentence of the reply — what the member took from that source. Cited sources first."""
    found: dict[str, dict[str, Any]] = {}
    opened: set[str] = set()
    for item in getattr(resp, "output", []) or []:
        kind = getattr(item, "type", None)
        if kind == "web_search_call":
            action = getattr(item, "action", None)
            atype = str(getattr(action, "type", "") or "") if action is not None else ""
            if atype in ("open_page", "find_in_page"):
                opened.add(str(getattr(action, "url", "") or ""))
                continue
            query = str(getattr(action, "query", "") or "") if action is not None else ""
            for res in getattr(item, "results", None) or []:
                get = (lambda k, r=res: r.get(k) if isinstance(r, dict) else getattr(r, k, None))
                url = str(get("url") or "")
                if url and url not in found:
                    found[url] = {"url": url, "title": str(get("title") or ""), "snippet": str(get("snippet") or ""),
                                  "query": query, "cited": False}
        elif kind == "message":
            for block in getattr(item, "content", []) or []:
                text = str(getattr(block, "text", "") or "")
                for ann in getattr(block, "annotations", []) or []:
                    url = str(getattr(ann, "url", "") or "")
                    if getattr(ann, "type", None) != "url_citation" or not url:
                        continue
                    a, b = getattr(ann, "start_index", None), getattr(ann, "end_index", None)
                    said = " ".join(text[a:b].split()) if isinstance(a, int) and isinstance(b, int) and b > a else ""
                    rec = found.setdefault(url, {"url": url, "title": str(getattr(ann, "title", "") or ""),
                                                 "snippet": "", "query": "", "cited": False})
                    rec["cited"] = True
                    if said and said not in rec["snippet"]:
                        rec["snippet"] = (rec["snippet"] + " " + said).strip()
    for rec in found.values():
        rec["read"] = rec["url"] in opened
    return sorted(found.values(), key=lambda r: (not r["cited"], not r["read"]))


def _output_text(resp: Any) -> str:
    texts: list[str] = []
    for item in getattr(resp, "output", []) or []:
        if getattr(item, "type", None) == "message":
            for block in getattr(item, "content", []) or []:
                if getattr(block, "type", None) == "output_text":
                    texts.append(getattr(block, "text", "") or "")
    return "\n".join(texts)


def _is_truncated(resp: Any, max_tokens: int, text: str) -> bool:
    if getattr(resp, "status", "completed") != "completed":
        return True
    usage = _usage_from_response(resp)
    return int(usage.get("output_tokens", 0)) >= max_tokens - 64


class MetaClient:
    """Real client. Constructed only when MODEL_API_KEY is present."""

    def __init__(self, run_dir: Path | None = None, max_cost: float | None = None) -> None:
        self.cost = CostLog(run_dir, max_cost=max_cost, ledger=BudgetLedger())
        self._sdk: Any = None

    def _client(self) -> Any:
        if self._sdk is None:
            from openai import OpenAI

            self._sdk = OpenAI(base_url="https://api.meta.ai/v1", api_key=os.environ["MODEL_API_KEY"])
        return self._sdk

    # -- low level ---------------------------------------------------------
    def responses(self, *, role: str, instructions: str, input_items: list[dict[str, Any]],
                  tools: list[dict[str, Any]] | None = None, schema_model: type[BaseModel] | None = None,
                  max_output_tokens: int | None = None, previous_response_id: str | None = None,
                  parallel_tool_calls: bool | None = None, include: list[str] | None = None) -> Any:
        rc = config.ROLES[role]
        max_tokens = max_output_tokens or rc.max_output_tokens
        self.cost.check_budget(estimate_call_usd(instructions, input_items, max_tokens, tools))
        kwargs: dict[str, Any] = {
            "model": rc.model,
            "instructions": instructions,
            "input": input_items,
            "reasoning": {"effort": rc.effort},
            "max_output_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
        if previous_response_id:
            kwargs["previous_response_id"] = previous_response_id
        if parallel_tool_calls is not None:
            kwargs["parallel_tool_calls"] = parallel_tool_calls
        if include:
            kwargs["include"] = include  # e.g. ["web_search_call.results"] (spec §14.2, verified)
        if schema_model is not None:
            kwargs["text"] = {"format": {"type": "json_schema", "name": schema_model.__name__,
                                         "schema": make_strict_schema(schema_model), "strict": True}}
        resp = self._create_with_retries(kwargs)
        text = _output_text(resp)
        if schema_model is not None and (_is_truncated(resp, max_tokens, text)):
            # The truncated reply was billed too: record it before re-asking.
            self.cost.record(role, rc.model, _usage_from_response(resp))
            kwargs["max_output_tokens"] = min(max_tokens * 2, 32000)
            self.cost.check_budget(estimate_call_usd(instructions, input_items, kwargs["max_output_tokens"], tools))
            resp = self._create_with_retries(kwargs)
        self.cost.record(role, rc.model, _usage_from_response(resp))
        return resp

    def _create_with_retries(self, kwargs: dict[str, Any], sdk: Any = None) -> Any:
        """5xx/429: retry with backoff (max 3). 402: BudgetExceeded. Other 400s raise. A content-filter 400
        is taken as a reason to re-word, not to resend: one retry with numbers, units and codes removed
        from the text (owner decision 2026-11-02); if that is blocked too, the error is raised."""
        from hs.plain import plain_request

        client = sdk or self._client()
        delay = 2.0
        last_exc: Exception | None = None
        plain = False
        for attempt in range(3):
            try:
                return client.responses.create(**kwargs)
            except Exception as exc:
                status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
                if status == 402:  # billing / credit exhausted: stop via the best-effort path
                    raise BudgetExceeded(f"Meta billing error HTTP 402 (out of credit or billing problem; check the dashboard): {exc}") from exc
                if "content management policy" in str(exc):
                    if plain:
                        raise
                    plain = True
                    kwargs = plain_request(kwargs)
                    self.cost.note("content_filter_retry_plain")
                    continue
                if status in (400, 402):
                    raise
                last_exc = exc
                if attempt == 2:
                    break
                retry_after = None
                resp = getattr(exc, "response", None)
                headers = getattr(resp, "headers", None) if resp is not None else None
                if headers is not None:
                    try:
                        retry_after = float(headers.get("Retry-After"))
                    except Exception:
                        retry_after = None
                time.sleep(retry_after if retry_after else delay)
                delay *= 2
        assert last_exc is not None
        raise last_exc

    # -- high level --------------------------------------------------------
    def structured(self, role: str, model_cls: type[BaseModel], instructions: str,
                   user_text: str, image_paths: list[Path] | None = None) -> Any:
        content: list[dict[str, Any]] = [{"type": "input_text", "text": user_text}]
        for path in image_paths or []:
            content.append({"type": "input_image",
                            "image_url": "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()})
        last_error: Exception | None = None
        for attempt in range(2):
            text = user_text if attempt == 0 else (
                user_text + f"\n\nYour previous reply was not valid for the required format "
                f"({last_error}). Reply again with only the requested structured output.")
            attempt_content = [{"type": "input_text", "text": text}, *content[1:]]
            resp = self.responses(role=role, instructions=instructions,
                                  input_items=[{"type": "message", "role": "user", "content": attempt_content}],
                                  schema_model=model_cls)
            try:
                return model_cls.model_validate_json(_output_text(resp))
            except Exception as exc:  # empty or malformed structured output: re-ask once
                last_error = exc
        assert last_error is not None
        raise last_error

    def free_text(self, role: str, instructions: str, user_text: str,
                  tools: list[dict[str, Any]] | None = None) -> tuple[str, list[dict[str, Any]]]:
        searching = any(t.get("type") == "web_search" for t in tools or [])
        resp = self.responses(role=role, instructions=instructions,
                              input_items=[{"type": "message", "role": "user", "content": [
                                  {"type": "input_text", "text": user_text}]}],
                              tools=tools, include=["web_search_call.results"] if searching else None)
        return _output_text(resp), search_sources(resp)

    def member_turn(self, **kwargs: Any) -> str:  # implemented in stage_a.council via tool loop
        raise NotImplementedError("MetaClient.member_turn is provided by hs.stage_a.council.run_member_turn")

    def image_edit(self, prompt: str, reference_png: Path, size: str = "1536x1024",
                   extra_refs: list[Path] | None = None) -> bytes:
        """`extra_refs` (C14): further reference images, e.g. the council's own sketches of the concept;
        the documented `images` field is an array."""
        import requests

        self.cost.check_budget(estimated_usd=0.05)
        if config.IMAGE_BACKEND == "responses":
            return self._image_via_responses(prompt, reference_png, size)
        body = {
            "model": config.IMAGE_MODEL,
            "prompt": prompt,
            "images": [{"image_url": "data:image/png;base64," + base64.b64encode(Path(p).read_bytes()).decode()}
                       for p in [reference_png, *(extra_refs or [])]],
            "n": 1, "size": size, "output_format": "png", "response_format": "b64_json",
            "reasoning_strength": "high",
            "tool_enablement": {"enable_web_search": False, "enable_image_search": False, "enable_shell": False},
        }
        headers = {"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}", "Content-Type": "application/json"}
        delay = 5.0
        last: Exception | None = None
        started = time.time()
        for _ in range(3):
            try:
                r = requests.post("https://api.meta.ai/v1/images/edits",
                                  json={k: v for k, v in body.items() if k != "_plain"}, headers=headers, timeout=240)
                if r.status_code in (500, 503, 429):
                    wait = r.headers.get("Retry-After")
                    time.sleep(float(wait) if wait else delay)
                    delay *= 2
                    continue
                if r.status_code == 402:
                    raise BudgetExceeded(f"Meta billing error HTTP 402 (out of credit or billing problem; check the dashboard): {r.text[:1000]}")
                if r.status_code == 400 and "content management policy" in r.text and not body.get("_plain"):
                    from hs.plain import plain_words

                    body = {**body, "prompt": plain_words(body["prompt"]), "_plain": True}
                    self.cost.note("content_filter_retry_plain")
                    continue
                if r.status_code >= 400:
                    # Deterministic rejection: never retry blind, and keep the
                    # body — it was once lost and cost a full run (QUESTIONS.md).
                    raise RuntimeError(f"image edit HTTP {r.status_code}: {r.text[:1000]}")
                r.raise_for_status()
                data = r.json()["data"][0]["b64_json"]
                self.cost.record("image_model", config.IMAGE_MODEL, {"images": 1})
                return base64.b64decode(data)
            except (RuntimeError, BudgetExceeded):
                raise
            except Exception as exc:
                last = exc
                if time.time() - started > 240:
                    break
                time.sleep(delay)
                delay *= 2
        assert last is not None
        raise last

    def sam_segment(self, phrase: str, image_png: Path, metadata: dict[str, str] | None = None) -> str:
        """One sam-3.1 image call (docs /docs/sam/segmenting): a short noun phrase or a box/point
        prompt string -> the raw box+mask token text (empty when nothing matches). The image is sent
        as PNG at most 1024 px on its long side. `self.last_sam` keeps the streamed event types and
        any usage the provider reported, for the smoke test and the SAM log."""
        import io

        from PIL import Image

        self.cost.check_budget(estimated_usd=0.01)
        with Image.open(image_png) as im:
            im = im.convert("RGB")
            scale = min(1.0, 1024 / max(im.size))
            if scale < 1.0:
                im = im.resize((round(im.width * scale), round(im.height * scale)))
            buf = io.BytesIO()
            im.save(buf, format="PNG")
            sent_size = im.size
        image_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        for attempt in range(4):  # temporary provider errors (overload, rate limit) are retried with back-off
            try:
                stream = self._client().with_options(max_retries=0).responses.create(
                    model=config.SAM_MODEL,
                    input=[{"type": "message", "role": "user", "content": [
                        {"type": "input_text", "text": phrase},
                        {"type": "input_image", "image_url": image_url}]}],
                    stream=True, **({"metadata": metadata} if metadata else {}))
                break
            except Exception as exc:
                code = getattr(exc, "status_code", None)
                if code == 402:
                    raise BudgetExceeded(f"Meta billing error HTTP 402 (out of credit or billing problem; check the dashboard): {exc}") from exc
                if code in (429, 500, 502, 503) and attempt < 3:
                    time.sleep(5.0 * 2 ** attempt)
                    continue
                raise
        parts: list[str] = []
        events: list[str] = []
        final_text, usage = "", None
        for event in stream:
            etype = getattr(event, "type", "")
            events.append(etype)
            if etype == "response.output_text.delta":
                parts.append(getattr(event, "delta", "") or "")
            elif etype == "response.output_text.done":
                final_text = getattr(event, "text", "") or final_text
            elif etype == "response.completed":
                resp = getattr(event, "response", None)
                usage = getattr(resp, "usage", None)
                final_text = final_text or _output_text(resp)
        self.cost.record("sam", config.SAM_MODEL, {"sam_calls": 1})
        text = "".join(parts) or final_text
        self.last_sam = {"phrase": phrase, "sent_size": sent_size, "event_types": sorted(set(events)),
                         "usage": str(usage) if usage is not None else None, "chars": len(text)}
        return text

    def _image_via_responses(self, prompt: str, reference_png: Path, size: str) -> bytes:
        resp = self.responses(
            role="vlm_writer", instructions="",
            input_items=[{"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": "data:image/png;base64," + base64.b64encode(Path(reference_png).read_bytes()).decode()},
            ]}],
            tools=[{"type": "image_generation", "output_format": "png", "size": size}],
        )
        for item in getattr(resp, "output", []) or []:
            if getattr(item, "type", None) == "image_generation_call":
                self.cost.record("image_model", config.IMAGE_MODEL, {"images": 1})
                return base64.b64decode(item.result)
        raise RuntimeError("image_generation_call missing in responses fallback")
