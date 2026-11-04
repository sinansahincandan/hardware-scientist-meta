"""Real check of OpenClient on Baseten (a few cents): a prior-art search reply (local web search, Meta-style
sources) and one structured Verdict. Writes runs/open_check/result.json and cost.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.client import search_sources  # noqa: F401
from hs.open_client import OpenClient
from hs.schemas import Verdict


def main() -> int:
    out_dir = ROOT / "runs" / "open_check"
    client = OpenClient(run_dir=out_dir, max_cost=0.5)
    text, sources = client.free_text(
        "prior_art", "Find the closest existing product, patent or paper to this concept and state the difference.",
        "Concept: a four-wheeled lunar regolith excavator with a front bucket-wheel and a tipping hopper, "
        "about 60 kg, for collecting 1 tonne of regolith per day near a lander.",
        tools=[{"type": "web_search", "search_context_size": "low"}])
    verdict = client.structured(
        "evaluator", Verdict, "You judge a concept design. Prose only, no scores.",
        "Concept: overbalanced weight wheel that turns forever to drive a water pump. Judge if it can work.")
    result = {"prior_art_text": text, "sources": sources, "verdict": verdict.model_dump(),
              "cost_usd": client.cost.total_usd}
    (out_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(text[:1500])
    print("\nSOURCES:")
    for s in sources:
        print(f"  cited={s['cited']} read={s['read']} q={s['query'][:50]!r} {s['url'][:90]}")
        if s["snippet"]:
            print(f"      took: {s['snippet'][:200]}")
    print("\nVERDICT:", json.dumps(verdict.model_dump())[:800])
    print(f"\ncost ${client.cost.total_usd:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
