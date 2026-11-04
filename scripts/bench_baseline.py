"""Benchmark baseline: the same Meta models used directly — ONE prompt to Muse Spark (web search allowed) that writes
the whole concept design and an image prompt, then ONE Muse Image call that draws it. No council, no Evaluator, no
Manager, no critic, no SAM, no redraw. Wall time and cost recorded.

Usage: .venv/bin/python scripts/bench_baseline.py examples/bench/*.json
Writes <out>/<problem stem>/design.md, figure.png, record.json (out: runs/baseline, or BASELINE_OUT).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from PIL import Image
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.client import MetaClient, _output_text


class BaselineDesign(BaseModel):
    title: str
    how_it_works: str
    parts: list[str]
    key_numbers: list[str]
    constraint_check: list[str]
    risks: list[str]
    how_it_is_made: list[str] = []
    image_prompt: str


PROMPT = (
    "You are an expert hardware design engineer. Design a concept for the problem below. Search the literature if "
    "useful. Return: title; how_it_works (a short paragraph); parts (each 'name — what it does'); key_numbers (the "
    "deciding estimates, each with how it was obtained); constraint_check (one line per given constraint: met or not "
    "and why); risks; how_it_is_made (3 to 5 making stages in order, each with its method, for example "
    "'laser-cut aluminium sheet, bolted'); image_prompt (a prompt for a photorealistic product rendering of the concept on a plain light "
    "grey backdrop that shows how it works).\n\nPROBLEM: {title}\n{statement}\nCONSTRAINTS:\n{constraints}"
)


def _parse(raw: str) -> BaselineDesign:
    """The JSON object in the reply (web search adds progress sentences before it)."""
    dec = json.JSONDecoder()
    for i, ch in enumerate(raw):
        if ch == "{":
            try:
                obj, _ = dec.raw_decode(raw[i:])
            except ValueError:
                continue
            if isinstance(obj, dict) and "title" in obj:
                return BaselineDesign.model_validate(obj)
    raise ValueError(f"no design JSON in reply: {raw[:300]}")


def main() -> int:
    blank = ROOT / "runs" / "baseline" / "_blank.png"
    blank.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (1536, 1024), (236, 238, 240)).save(blank)
    for arg in sys.argv[1:]:
        prob = json.loads(Path(arg).read_text(encoding="utf-8"))
        out = ROOT / "runs" / os.environ.get("BASELINE_OUT", "baseline") / Path(arg).stem
        out.mkdir(parents=True, exist_ok=True)
        client = MetaClient(run_dir=out, max_cost=0.5)
        start = time.time()
        text = PROMPT.format(title=prob["title"], statement=prob["statement"],
                             constraints="\n".join(f"- {c}" for c in prob["constraints"]))
        resp = client.responses(role="secretary", instructions="", input_items=[
            {"type": "message", "role": "user", "content": [{"type": "input_text", "text": text}]}],
            tools=[{"type": "web_search", "search_context_size": "medium"}], schema_model=BaselineDesign)
        design = _parse(_output_text(resp))
        png = client.image_edit(design.image_prompt + " The image carries no text.", blank)
        (out / "figure.png").write_bytes(png)
        seconds = round(time.time() - start, 1)
        md = (f"# {design.title}\n\n## How it works\n{design.how_it_works}\n\n## Parts\n"
              + "".join(f"- {x}\n" for x in design.parts) + "\n## Key numbers\n"
              + "".join(f"- {x}\n" for x in design.key_numbers) + "\n## Constraint check\n"
              + "".join(f"- {x}\n" for x in design.constraint_check) + "\n## Risks\n"
              + "".join(f"- {x}\n" for x in design.risks)
              + ("\n## How it is made\n" + "".join(f"- {x}\n" for x in design.how_it_is_made)
                 if design.how_it_is_made else ""))
        (out / "design.md").write_text(md, encoding="utf-8")
        cost = json.loads((out / "cost.json").read_text(encoding="utf-8")).get("total_usd", 0.0)
        (out / "record.json").write_text(json.dumps({"problem_file": arg, "wall_seconds": seconds,
                                                     "cost_usd": cost, "image_prompt": design.image_prompt},
                                                    indent=2), encoding="utf-8")
        print(f"{arg}: {seconds:.0f} s ${cost:.4f}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
