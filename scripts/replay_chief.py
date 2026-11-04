"""Replay one real chief-designer turn on a finished run's whiteboard, with its selections, proposal and opinions
cleared, to check that the chief's board actions land (a cheap check before a full run). No Stage B.

Usage: .venv/bin/python scripts/replay_chief.py <run_dir> <out_dir> [cycle] [--closing] [--close]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.open_client import OpenClient as MetaClient  # open-weights copy
from hs.master_prompt import MasterPrompt, roster_of, split_master_prompt
from hs.stage_a.meeting import Meeting
from hs.stage_a.whiteboard import WBClosure, Whiteboard


def main() -> int:
    run, out = Path(sys.argv[1]), Path(sys.argv[2])
    cycle = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 4
    closing = "--closing" in sys.argv
    src = run / "stage_a" / "iter_00"
    sections = split_master_prompt(min((run / "master_prompt").glob("rev_*.md")).read_text(encoding="utf-8"))
    problem = json.loads((run / "problem.json").read_text(encoding="utf-8"))
    master = MasterPrompt(out, problem["title"], sections)
    roster = roster_of(sections)

    board = Whiteboard.load(src / "whiteboard.json")
    board.selections, board.proposal, board.closure = [], None, WBClosure()
    board.votes.clear()
    board.roster = list(roster)
    for c in board.concepts:
        c.status = "open"

    meeting = Meeting(MetaClient(run_dir=out, max_cost=0.5), master, out, 0)
    meeting.board = board
    meeting.tools.board = board
    turns = sorted((src / "turns").glob("c*.json"), key=lambda p: (int(p.name[1:].split("_")[0]), p.name))
    meeting.transcript = [json.loads(p.read_text(encoding="utf-8")) for p in turns
                          if int(p.name[1:].split("_")[0]) <= cycle and "Manager" not in p.name]
    meeting._run_manager_turn(roster, cycle, closing=closing)
    if "--close" in sys.argv and board.proposal is not None:
        # members give their readiness opinions on the chief's proposal, then the chief's closing turn
        meeting.max_cycles = cycle
        closed_by = meeting._closing_rounds(roster)
        print(f"closed_by {closed_by}; opinions {len(board.votes)} of {len(roster)} on the current version")

    ops = [json.loads(line) for line in (meeting.iter_dir / "whiteboard_history.jsonl").read_text().splitlines()]
    for o in ops:
        if o.get("kind") == "op":
            print(("ok  " if o["ok"] else "FAIL"), o["op"].get("action"), "->", str(o["msg"])[:160])
    print(f"selections {len(board.selections)} of {len(board.functions)} functions; "
          f"proposal {'v' + str(board.proposal.version) if board.proposal else 'none'}")
    board.save(meeting.iter_dir / "whiteboard.json")
    (meeting.iter_dir / "replay_board.md").write_text(board.render_markdown(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
