"""MetaClient — all model calls go through here (Responses API only, spec §9).

Field names are exactly those of spec §9. `instructions` is resent on every
call (it is NOT carried by previous_response_id).
"""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from hs import config
from hs.schemas import make_strict_schema


class BudgetExceeded(Exception):
    """Raised BEFORE a call that would exceed MAX_COST_USD_PER_RUN."""


def price_usage(usage: dict[str, Any]) -> float:
    p = config.PRICES
    cached = int(usage.get("cached_input_tokens", 0) or 0)
    inp = int(usage.get("input_tokens", 0) or 0)
    out = int(usage.get("output_tokens", 0) or 0)
    searches = int(usage.get("searches", 0) or 0)
    images = int(usage.get("images", 0) or 0)
    return (
        max(inp - cached, 0) * p["input_per_1m"] / 1e6
        + cached * p["cached_input_per_1m"] / 1e6
        + out * p["output_per_1m"] / 1e6
        + searches * p["web_search_per_query"]
        + images * p["image_each"]
    )


class CostLog:
    def __init__(self, run_dir: Path | None, max_cost: float | None = None) -> None:
        self.run_dir = run_dir
        self.max_cost = config.MAX_COST_USD_PER_RUN if max_cost is None else max_cost
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
                "usd": round(usd, 6),
            }
        )
        self.total_usd += usd
        self.flush()
        return usd

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
    return {
        "input_tokens": g(usage, "input_tokens"),
        "cached_input_tokens": cached,
        "output_tokens": g(usage, "output_tokens"),
        "reasoning_tokens": reasoning,
    }


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
        self.cost = CostLog(run_dir, max_cost=max_cost)
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
                  parallel_tool_calls: bool | None = None) -> Any:
        rc = config.ROLES[role]
        max_tokens = max_output_tokens or rc.max_output_tokens
        self.cost.check_budget()
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
        if schema_model is not None:
            kwargs["text"] = {"format": {"type": "json_schema", "name": schema_model.__name__,
                                         "schema": make_strict_schema(schema_model), "strict": True}}
        resp = self._create_with_retries(kwargs)
        text = _output_text(resp)
        if schema_model is not None and (_is_truncated(resp, max_tokens, text)):
            kwargs["max_output_tokens"] = min(max_tokens * 2, 32000)
            resp = self._create_with_retries(kwargs)
        self.cost.record(role, rc.model, _usage_from_response(resp))
        return resp

    def _create_with_retries(self, kwargs: dict[str, Any]) -> Any:
        client = self._client()
        delay = 2.0
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                return client.responses.create(**kwargs)
            except Exception as exc:  # status-aware retry (503/500/429 retry, 400 raise)
                status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
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
        resp = self.responses(role=role, instructions=instructions,
                              input_items=[{"type": "message", "role": "user", "content": content}],
                              schema_model=model_cls)
        return model_cls.model_validate_json(_output_text(resp))

    def free_text(self, role: str, instructions: str, user_text: str,
                  tools: list[dict[str, Any]] | None = None) -> tuple[str, list[dict[str, Any]]]:
        resp = self.responses(role=role, instructions=instructions,
                              input_items=[{"type": "message", "role": "user", "content": [
                                  {"type": "input_text", "text": user_text}]}],
                              tools=tools)
        citations: list[dict[str, Any]] = []
        for item in getattr(resp, "output", []) or []:
            if getattr(item, "type", None) == "message":
                for block in getattr(item, "content", []) or []:
                    for ann in getattr(block, "annotations", []) or []:
                        if getattr(ann, "type", None) == "url_citation":
                            citations.append({"url": getattr(ann, "url", ""), "title": getattr(ann, "title", "")})
        return _output_text(resp), citations

    def member_turn(self, **kwargs: Any) -> str:  # implemented in stage_a.council via tool loop
        raise NotImplementedError("MetaClient.member_turn is provided by hs.stage_a.council.run_member_turn")

    def image_edit(self, prompt: str, reference_png: Path, size: str = "1536x1024") -> bytes:
        import requests

        self.cost.check_budget(estimated_usd=0.05)
        if config.IMAGE_BACKEND == "responses":
            return self._image_via_responses(prompt, reference_png, size)
        body = {
            "model": config.IMAGE_MODEL,
            "prompt": prompt,
            "images": [{"image_url": "data:image/png;base64," + base64.b64encode(Path(reference_png).read_bytes()).decode()}],
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
                r = requests.post("https://api.meta.ai/v1/images/edits", json=body, headers=headers, timeout=240)
                if r.status_code in (500, 503, 429):
                    wait = r.headers.get("Retry-After")
                    time.sleep(float(wait) if wait else delay)
                    delay *= 2
                    continue
                r.raise_for_status()
                data = r.json()["data"][0]["b64_json"]
                self.cost.record("image_model", config.IMAGE_MODEL, {"images": 1})
                return base64.b64decode(data)
            except Exception as exc:
                last = exc
                if time.time() - started > 240:
                    break
                time.sleep(delay)
                delay *= 2
        assert last is not None
        raise last

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
