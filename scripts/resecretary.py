"""Re-run the Secretary on a finished meeting (saved whiteboard + transcript) and print the part names and the
operating steps it writes — a one-call check of the Secretary's instructions.

Usage: .venv/bin/python scripts/resecretary.py <run_dir> <iter_dir_name> <out_dir>
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.open_client import OpenClient
from hs.schemas import Problem
from hs.stage_a.meeting import MeetingResult, Secretary
from hs.stage_a.whiteboard import Whiteboard


def main() -> int:
    run, it, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    src = run / "stage_a" / it
    board = Whiteboard.load(src / "whiteboard.json")
    turns = []
    for block in (src / "transcript.md").read_text(encoding="utf-8").split("## Cycle ")[1:]:
        head, _, body = block.partition("\n")
        m = re.match(r"(\d+) — (.*)", head.strip())
        if m:
            turns.append({"cycle": int(m.group(1)), "member": m.group(2), "message": body.strip()})
    closure = json.loads((src / "closure.json").read_text(encoding="utf-8"))
    result = MeetingResult(board=board, transcript=turns, cycles_used=max(t["cycle"] for t in turns),
                           closed_by=str(closure.get("closed_by") or "consensus"))
    problem = Problem.model_validate_json((run / "problem.json").read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    client = OpenClient(run_dir=out, max_cost=0.5)
    solution = Secretary(client).synthesize(result, problem, out)
    old = json.loads((src / "solution.json").read_text(encoding="utf-8"))
    print("BEFORE:", [p["name"] for p in old["concept"]["parts"]])
    print("AFTER: ", [p.name for p in solution.concept.parts])
    print("sizes BEFORE:", [(p["name"], p["size_class_mm"]["min"], p["size_class_mm"]["max"]) for p in old["concept"]["parts"]])
    print("sizes AFTER: ", [(p.name, p.size_class_mm.min, p.size_class_mm.max) for p in solution.concept.parts])
    print("steps: ", [f"{s.part_id}: {s.action}" for s in solution.operating_sequence])
    print(f"cost ${client.cost.total_usd:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
