"""PHASE 1d Meta API check: one call each to text, web search, image, SAM.

All calls go through hs.client.MetaClient (counted in cost.json and the spend
ledger). One attempt per call; a failure is recorded, not retried. Writes
runs/meta_check_<stamp>/check.json. Never prints the key.
Usage: .venv/bin/python scripts/meta_check.py
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs import config
from hs.client import MetaClient, _usage_from_response
from hs.stage_a.tools import TOOL_SCHEMAS


def _clean(text: str) -> str:
    import os

    key = os.environ.get("MODEL_API_KEY", "")
    return text.replace(key, "<key>") if key else text


def main() -> int:
    run_dir = ROOT / "runs" / f"meta_check_{time.strftime('%Y%m%d-%H%M%S')}"
    run_dir.mkdir(parents=True)
    client = MetaClient(run_dir=run_dir)
    client._sdk = client._client().with_options(max_retries=0)  # one attempt per call
    client._create_with_retries = lambda kwargs: client._sdk.responses.create(**kwargs)  # type: ignore[method-assign]
    results: dict[str, Any] = {}

    def attempt(name: str, fn: Any) -> None:
        before = len(client.cost.entries)
        try:
            detail = fn()
            results[name] = {"worked": True, **detail}
        except Exception as exc:
            results[name] = {"worked": False, "error": _clean(f"{type(exc).__name__}: {exc}")[:1500],
                             "trace": _clean(traceback.format_exc())[-1500:]}
        results[name]["cost_entries"] = client.cost.entries[before:]
        print(f"{name}: {'worked' if results[name]['worked'] else 'FAILED'}", flush=True)

    def text() -> dict[str, Any]:
        reply, _ = client.free_text("light_check", "Answer in one sentence.",
                                    "In one sentence, what does a hand truck do?")
        return {"reply": reply}

    def search() -> dict[str, Any]:
        web = [t for t in TOOL_SCHEMAS if t.get("type") == "web_search"]
        assert web, "council TOOL_SCHEMAS has no web_search entry"
        resp = client.responses(role="prior_art", instructions="Use web search once, then answer in one sentence.",
                                input_items=[{"type": "message", "role": "user", "content": [
                                    {"type": "input_text",
                                     "text": "Find one source on stair-climbing hand trucks and name it."}]}],
                                tools=web)
        from hs.client import _output_text

        cites = [{"url": getattr(a, "url", ""), "title": getattr(a, "title", "")}
                 for item in resp.output or [] if getattr(item, "type", "") == "message"
                 for block in getattr(item, "content", []) or []
                 for a in getattr(block, "annotations", []) or [] if getattr(a, "type", "") == "url_citation"]
        return {"tool_sent": web, "reply": _output_text(resp), "citations": cites,
                "usage": _usage_from_response(resp),
                "output_item_types": [getattr(i, "type", "") for i in resp.output or []]}

    ref = run_dir / "reference.png"
    img = Image.new("RGB", (512, 512), "white")
    ImageDraw.Draw(img).ellipse((156, 156, 356, 356), outline="black", width=6)
    img.save(ref)
    render = run_dir / "render.png"

    def image() -> dict[str, Any]:
        data = client.image_edit("A photograph of a single red metal disk lying flat on a plain white table, "
                                 "seen from above, matching the circle in the reference.", ref, size="1024x1024")
        render.write_bytes(data)
        with Image.open(render) as im:
            return {"size": im.size, "format": im.format, "bytes": len(data)}

    def sam() -> dict[str, Any]:
        target = render if render.exists() else ref
        raw = client.sam_segment("metal disk" if target == render else "circle", target)
        return {"image": target.name, "raw_chars": len(raw), "raw_head": raw[:300],
                "records": raw.count("<|box;")}

    attempt("text", text)
    attempt("web_search", search)
    attempt("image", image)
    attempt("sam", sam)
    results["total_usd"] = round(client.cost.total_usd, 6)
    results["prices"] = config.PRICES
    (run_dir / "check.json").write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"total ${client.cost.total_usd:.4f} -> {run_dir.relative_to(ROOT)}/check.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
