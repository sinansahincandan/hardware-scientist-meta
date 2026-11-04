"""Benchmark: one full Hardware Scientist run per problem file, with wall time recorded (timing.json in the run).

Usage: .venv/bin/python scripts/bench_hs.py examples/bench/b1_lunar_excavator.json [more problem files…]
Each run is capped at $10 (MetaClient max_cost); the project ledger cap still applies.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.open_client import OpenClient as MetaClient  # open-weights copy
from hs.controller import Controller
from hs.schemas import Problem


def main() -> int:
    for arg in sys.argv[1:]:
        problem = Problem.model_validate_json(Path(arg).read_text(encoding="utf-8"))
        start = time.time()
        result = Controller(MetaClient(max_cost=10.0)).run(problem)
        seconds = round(time.time() - start, 1)
        (result.run_dir / "timing.json").write_text(json.dumps(
            {"problem_file": arg, "wall_seconds": seconds, "cost_usd": result.cost_usd}, indent=2), encoding="utf-8")
        print(f"{arg}: {result.run_dir.name} {seconds:.0f} s ${result.cost_usd:.4f}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
