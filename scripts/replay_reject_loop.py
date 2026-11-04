"""Run Stage A's rejection loop on a finished meeting, with a real rejection: the Manager's two-step gradient and
section rewrite, then meeting 2 on the new master prompt with the Evaluator's requests pinned, the Secretary and
the Evaluator again — the controller's loop body (controller.py, `if not verdict.accept`), no Stage B.

Usage: .venv/bin/python scripts/replay_reject_loop.py <run_dir> <rejected_verdict.json> <out_dir> [--gradients-only]
--gradients-only stops after the Manager's gradients and rewrite (about $0.1; no second meeting).
Meeting 2 continues on meeting 1's board and the Evaluator re-checks its own requests first, as the controller does.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.client import MetaClient
from hs.master_prompt import MasterPrompt, split_master_prompt
from hs.schemas import Problem, SolutionPrompt, Verdict
from hs.stage_a.archive import CouncilArchive
from hs.stage_a.evaluator import Evaluator
from hs.stage_a.manager import Manager
from hs.stage_a.meeting import Meeting, MeetingResult, Secretary
from hs.stage_a.tools import ToolRunner
from hs.stage_a.whiteboard import Whiteboard


def main() -> int:
    run, verdict_path, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(run / "stage_a" / "iter_00", out / "stage_a" / "iter_00")
    (out / "master_prompt").mkdir(parents=True)
    rev0 = min((run / "master_prompt").glob("rev_*.md"))
    shutil.copy(rev0, out / "master_prompt" / "rev_000.md")
    shutil.copy(run / "problem.json", out / "problem.json")
    for d in ("tools",):
        if (run / d).exists():
            shutil.copytree(run / d, out / d)

    client = MetaClient(run_dir=out, max_cost=3.5)
    problem = Problem.model_validate_json((out / "problem.json").read_text(encoding="utf-8"))
    master = MasterPrompt(out, problem.title, split_master_prompt(rev0.read_text(encoding="utf-8")))
    it0 = out / "stage_a" / "iter_00"
    board = Whiteboard.load(it0 / "whiteboard.json")
    turns = sorted((it0 / "turns").glob("c*.json"), key=lambda p: (int(p.name[1:].split("_")[0]), p.name))
    transcript = [json.loads(p.read_text(encoding="utf-8")) for p in turns]
    room = MeetingResult(board=board, transcript=transcript, cycles_used=board.closure.cycles_used,
                         closed_by=board.closure.closed_by)
    solution = SolutionPrompt.model_validate_json((it0 / "solution.json").read_text(encoding="utf-8"))
    verdict = Verdict.model_validate_json(verdict_path.read_text(encoding="utf-8"))
    assert not verdict.accept, "give a rejected verdict"
    shutil.copy(verdict_path, it0 / "verdict.json")

    archive = CouncilArchive(out)
    archive.add(solution, iteration=0, revision=master.rev, status="rejected", accept=False,
                feedback=verdict.feedback, solution_path="stage_a/iter_00/solution.json")
    manager = Manager(client, master)
    report = manager.edit(room, solution, verdict.feedback, it0, tools=ToolRunner(board, out, it0 / "evidence"))
    print("manager edit:", json.dumps({k: report.get(k) for k in ("changed", "reverted", "no_progress")}))
    if "--gradients-only" in sys.argv:
        return 0

    meeting = Meeting(client, master, out, 1)
    meeting.carry_from(it0)  # controller.py: the next meeting continues on the previous board
    meeting.pin_inspirations(manager.inspirations(archive))
    meeting.pin_evaluator_requests(list(verdict.evidence_requests), verdict.feedback)
    room2 = meeting.run()
    print(f"meeting 2: closed_by={room2.closed_by} cycles={room2.cycles_used} "
          f"selections={len(room2.board.selections)}/{len(room2.board.functions)} "
          f"proposal={'v' + str(room2.board.proposal.version) if room2.board.proposal else 'none'}")
    it1 = out / "stage_a" / "iter_01"
    solution2 = Secretary(client).synthesize(room2, problem, it1)
    verdict2 = Evaluator(client).judge(master, solution2, room2.board, room2.closed_by, it1,
                                       previous_requests=list(verdict.evidence_requests))
    print("evaluator 2: accept", verdict2.accept)
    return 0


if __name__ == "__main__":
    sys.exit(main())
