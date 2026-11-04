"""Short real smoke run (round 3, E24 precondition): one problem with small caps.

Usage: .venv/bin/python scripts/smoke_run.py examples/01_stair_cart.json
Caps: 1 Stage A iteration, 1 meeting cycle, 2 picture rounds. Prints the run folder and its cost.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.open_client import OpenClient as MetaClient  # open-weights copy
from hs.controller import Controller
from hs.schemas import Problem


def main() -> int:
    problem = Problem.model_validate_json(Path(sys.argv[1]).read_text(encoding="utf-8"))
    controller = Controller(MetaClient(max_cost=3.0), max_a_iters=1, min_cycles=1, max_cycles=1, max_s1_rounds=2)
    result = controller.run(problem)
    print(f"run folder: {result.run_dir}")
    print(f"final figure: {result.figure_path}")
    print(f"cost: ${result.cost_usd:.4f}")
    for warning in result.warnings:
        print(f"warning: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
