"""Probe Baseten's Muse Spark Open (hackathon model) for the features HS needs.

One small real call per feature: plain text, image input, strict JSON schema, function tool call,
reasoning effort, the /v1/responses endpoint, and the usage fields. Prints what came back (never the
key) and writes runs/open_probe/probe.json. Cost: a few cents.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
MODEL = "meta-models/muse-spark-open-1026"
BASE_URL = "https://inference.baseten.co/v1"


def load_env() -> None:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def dump(obj):
    try:
        return obj.model_dump()
    except Exception:
        return str(obj)


def main() -> int:
    load_env()
    client = OpenAI(base_url=BASE_URL, api_key=os.environ["BASETEN_API_KEY"])
    out: dict[str, object] = {}

    def probe(name, fn):
        t0 = time.time()
        try:
            r = fn()
            out[name] = {"ok": True, "seconds": round(time.time() - t0, 1), "response": dump(r)}
            print(f"[{name}] ok in {time.time() - t0:.1f}s")
        except Exception as exc:
            out[name] = {"ok": False, "seconds": round(time.time() - t0, 1), "error": repr(exc)[:2000]}
            print(f"[{name}] FAILED: {repr(exc)[:400]}")

    msg = [{"role": "user", "content": "In one sentence: why does a hydraulic press multiply force?"}]
    probe("plain", lambda: client.chat.completions.create(model=MODEL, messages=msg, max_tokens=800))
    probe("effort_low", lambda: client.chat.completions.create(
        model=MODEL, messages=msg, max_tokens=800, reasoning_effort="low"))
    probe("system_prompt", lambda: client.chat.completions.create(model=MODEL, max_tokens=800, messages=[
        {"role": "system", "content": "Answer in exactly three words."}, *msg]))

    png = sorted((ROOT / "showcase").rglob("*.png"))[:1] or sorted((ROOT / "docs").rglob("*.png"))[:1]
    if png:
        b64 = base64.b64encode(png[0].read_bytes()).decode()
        out["image_file"] = str(png[0].relative_to(ROOT))
        probe("image", lambda: client.chat.completions.create(model=MODEL, max_tokens=1500, messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "Describe this image in two sentences."},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}}]}]))

    schema = {"type": "object", "additionalProperties": False, "required": ["verdict", "reason"],
              "properties": {"verdict": {"type": "string", "enum": ["works", "fails"]},
                             "reason": {"type": "string"}}}
    probe("json_schema", lambda: client.chat.completions.create(
        model=MODEL, max_tokens=1500,
        messages=[{"role": "user", "content": "Does a perpetual motion wheel with weights work?"}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "Verdict", "schema": schema, "strict": True}}))

    tools = [{"type": "function", "function": {
        "name": "calc", "description": "Evaluate an arithmetic expression.",
        "parameters": {"type": "object", "additionalProperties": False, "required": ["expression"],
                       "properties": {"expression": {"type": "string"}}}}}]
    probe("tool_call", lambda: client.chat.completions.create(
        model=MODEL, max_tokens=1500, tools=tools,
        messages=[{"role": "user", "content": "Use the calc tool to compute 17.3 * 4.2, then tell me."}]))

    probe("responses_api", lambda: client.responses.create(
        model=MODEL, input="Say hello in one word.", max_output_tokens=400))

    run_dir = ROOT / "runs" / "open_probe"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "probe.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"wrote {run_dir / 'probe.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
