"""Re-judge a finished meeting with the current Evaluator (one real call): the run's own master prompt, solution,
whiteboard and closure, verdict written to <out_dir>. A cheap check of an Evaluator change before a full run.

Usage: .venv/bin/python scripts/rejudge.py <run_dir> <out_dir> [iteration]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.open_client import OpenClient as MetaClient  # open-weights copy
from hs.master_prompt import MasterPrompt, split_master_prompt
from hs.schemas import SolutionPrompt
from hs.stage_a.evaluator import Evaluator
from hs.stage_a.whiteboard import Whiteboard


def main() -> int:
    run, out = Path(sys.argv[1]), Path(sys.argv[2])
    it = run / "stage_a" / f"iter_{int(sys.argv[3]) if len(sys.argv) > 3 else 0:02d}"
    out.mkdir(parents=True, exist_ok=True)
    problem = json.loads((run / "problem.json").read_text(encoding="utf-8"))
    k = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rev = run / "master_prompt" / f"rev_{k:03d}.md"  # meeting k ran on revision k (one rewrite per rejection)
    master = MasterPrompt(out, problem["title"], split_master_prompt(
        (rev if rev.exists() else min((run / "master_prompt").glob("rev_*.md"))).read_text(encoding="utf-8")))
    solution = SolutionPrompt.model_validate_json((it / "solution.json").read_text(encoding="utf-8"))
    board = Whiteboard.load(it / "whiteboard.json")
    prev = run / "stage_a" / f"iter_{int(sys.argv[3]) - 1:02d}" / "verdict.json" if len(sys.argv) > 3 else None
    previous = json.loads(prev.read_text(encoding="utf-8"))["evidence_requests"] if prev and prev.exists() else None
    verdict = Evaluator(MetaClient(run_dir=out, max_cost=0.3)).judge(master, solution, board,
                                                                      board.closure.closed_by, out,
                                                                      previous_requests=previous)
    print("accept", verdict.accept)
    print("requests", json.dumps(verdict.evidence_requests, indent=1)[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
