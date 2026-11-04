"""Replay cycle-1 member turns on a finished run's opening board (functions only, as after the Manager's
opening) and record what Muse Spark Open asks for in every raw reply: search calls, board calls, text.
A cheap check of whether members search before a full run.

Usage: .venv/bin/python scripts/replay_member.py <run_dir> <out_dir> "<member name>" ["<member name>" ...]
Writes <out_dir>/raw_calls.jsonl (one line per Baseten reply) and <out_dir>/open_search.jsonl.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.master_prompt import MasterPrompt, split_master_prompt
from hs.open_client import OpenClient
from hs.stage_a.meeting import Meeting
from hs.stage_a.whiteboard import Whiteboard


class LoggingClient(OpenClient):
    """OpenClient that writes the shape of every raw Baseten reply."""

    member = ""

    def _call(self, role, kwargs, tools):
        resp = super()._call(role, kwargs, tools)
        items = []
        for it in getattr(resp, "output", []) or []:
            kind = getattr(it, "type", "")
            if kind == "function_call":
                args = (it.arguments or "")[:120]
                items.append(f"{it.name}({args})")
            elif kind == "message":
                text = "".join(getattr(b, "text", "") or "" for b in it.content or [])
                items.append(f"text[{len(text.split())} words]")
        rec = {"member": self.member, "role": role, "offered": [t.get("name", t.get("type")) for t in kwargs.get("tools", [])],
               "items": items, "out_tokens": getattr(resp.usage, "output_tokens", 0)}
        with (self.cost.run_dir / "raw_calls.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        return resp


def main() -> int:
    run, out = Path(sys.argv[1]), Path(sys.argv[2])
    members = sys.argv[3:]
    src = run / "stage_a" / "iter_00"
    sections = split_master_prompt(min((run / "master_prompt").glob("rev_*.md")).read_text(encoding="utf-8"))
    problem = json.loads((run / "problem.json").read_text(encoding="utf-8"))
    master = MasterPrompt(out, problem["title"], sections)
    saved = Whiteboard.load(src / "whiteboard.json")
    opening = json.loads((src / "turns" / "c0_Manager.json").read_text(encoding="utf-8"))
    client = LoggingClient(run_dir=out, max_cost=1.0)
    for member in members:
        meeting = Meeting(client, master, out, 0)
        board = Whiteboard(functions=saved.functions, roster=saved.roster)
        meeting.board = board
        meeting.tools.board = board
        meeting.transcript = [opening]
        client.member = member
        message = meeting._turn(member, 1)
        searches = [e for e in board.evidence if e.tool == "web_search"]
        print(f"== {member}: {len(board.concepts)} concepts, {len(searches)} search evidence, "
              f"{len(board.evidence) - len(searches)} other evidence; message {len(message.split())} words")
    for line in (out / "raw_calls.jsonl").read_text().splitlines():
        rec = json.loads(line)
        print(rec["member"].split("—")[0].strip()[:18], rec["items"])
    print(f"cost ${client.cost.total_usd:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
