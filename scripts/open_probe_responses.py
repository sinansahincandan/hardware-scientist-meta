"""Probe Baseten's /v1/responses endpoint for the exact call shapes MetaClient sends (spec §9):
instructions + input items, reasoning effort, function tools, function_call_output with
previous_response_id, strict json_schema via text.format, input_image, and the hosted web_search tool.
Writes runs/open_probe/responses_probe.json. Cost: a few cents."""
from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from open_probe import BASE_URL, MODEL, ROOT, dump, load_env  # noqa: E402


def main() -> int:
    import os

    from openai import OpenAI

    load_env()
    client = OpenAI(base_url=BASE_URL, api_key=os.environ["BASETEN_API_KEY"])
    out: dict[str, object] = {}

    def probe(name, fn):
        t0 = time.time()
        try:
            r = fn()
            out[name] = {"ok": True, "seconds": round(time.time() - t0, 1), "response": dump(r)}
            print(f"[{name}] ok in {time.time() - t0:.1f}s")
            return r
        except Exception as exc:
            out[name] = {"ok": False, "error": repr(exc)[:2000]}
            print(f"[{name}] FAILED: {repr(exc)[:400]}")
            return None

    tools = [{"type": "function", "name": "calc", "description": "Evaluate an arithmetic expression.",
              "strict": True,
              "parameters": {"type": "object", "additionalProperties": False, "required": ["expression"],
                             "properties": {"expression": {"type": "string"}}}}]
    r1 = probe("fn_call", lambda: client.responses.create(
        model=MODEL, instructions="You are a careful engineer. Use tools for arithmetic.",
        input=[{"type": "message", "role": "user", "content": [
            {"type": "input_text", "text": "Use calc to compute 17.3 * 4.2, then state the result."}]}],
        tools=tools, reasoning={"effort": "low"}, max_output_tokens=2000))
    call = next((i for i in (getattr(r1, "output", None) or []) if getattr(i, "type", "") == "function_call"), None)
    if call is not None:
        probe("chain_previous_id", lambda: client.responses.create(
            model=MODEL, instructions="You are a careful engineer. Use tools for arithmetic.",
            previous_response_id=r1.id, tools=tools, reasoning={"effort": "low"}, max_output_tokens=2000,
            input=[{"type": "function_call_output", "call_id": call.call_id, "output": "72.66"}]))

    schema = {"type": "object", "additionalProperties": False, "required": ["verdict", "reason"],
              "properties": {"verdict": {"type": "string", "enum": ["works", "fails"]},
                             "reason": {"type": "string"}}}
    probe("text_format_schema", lambda: client.responses.create(
        model=MODEL, instructions="Judge physical feasibility.", reasoning={"effort": "medium"},
        input=[{"type": "message", "role": "user", "content": [
            {"type": "input_text", "text": "Does an overbalanced weight wheel run forever?"}]}],
        text={"format": {"type": "json_schema", "name": "Verdict", "schema": schema, "strict": True}},
        max_output_tokens=3000))

    png = ROOT / "showcase/lunar-regolith-excavation-robot/final/_render_without_callouts.png"
    b64 = base64.b64encode(png.read_bytes()).decode()
    probe("input_image", lambda: client.responses.create(
        model=MODEL, instructions="", reasoning={"effort": "low"}, max_output_tokens=2000,
        input=[{"type": "message", "role": "user", "content": [
            {"type": "input_text", "text": "How many wheels are visible? One line."},
            {"type": "input_image", "image_url": "data:image/png;base64," + b64}]}]))

    probe("hosted_web_search", lambda: client.responses.create(
        model=MODEL, instructions="Cite sources.", reasoning={"effort": "low"}, max_output_tokens=2000,
        tools=[{"type": "web_search", "search_context_size": "low"}], include=["web_search_call.results"],
        input=[{"type": "message", "role": "user", "content": [
            {"type": "input_text", "text": "What is the bulk density of lunar regolith? Search and cite."}]}]))

    (ROOT / "runs/open_probe/responses_probe.json").write_text(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
