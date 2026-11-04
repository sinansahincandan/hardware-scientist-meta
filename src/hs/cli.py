"""hs CLI (spec §8): run | examples | feedback | show | report | compare | board | budget."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def _make_client(fake: bool, run_dir: Path | None = None, scenario: str | None = None,
                 max_cost: float | None = None) -> Any:
    if fake or os.environ.get("HS_FAKE") == "1":
        from hs.fake_client import FakeClient

        return FakeClient(run_dir=run_dir, scenario=scenario, max_cost=max_cost)
    from hs.client import MetaClient

    return MetaClient(run_dir=run_dir, max_cost=max_cost)


def _cmd_run(args: argparse.Namespace) -> int:
    from hs.controller import Controller
    from hs.schemas import Problem

    problem = Problem.model_validate_json(Path(args.problem).read_text(encoding="utf-8"))
    client = _make_client(bool(args.fake))
    caps: dict[str, int] = {}
    if args.quick:
        caps = _quick_mode()
    result = Controller(client, **caps).run(problem)  # binds the client's cost log to the new run folder
    print(f"run folder: {result.run_dir}")
    print(f"final figure: {result.figure_path}")
    print(f"cost: ${result.cost_usd:.4f}")
    for warning in result.warnings:
        print(f"warning: {warning}")
    return 0


def _quick_mode() -> dict[str, int]:
    """Same loops, smaller: for a reviewer who wants a design in about a quarter of an hour (full runs take 45-75
    min). Two meetings of up to two cycles, members and chief at low effort with fewer tool calls, two picture
    rounds, no return from the picture to the design, two making-step images."""
    from dataclasses import replace

    from hs import config

    for role in ("member", "manager"):
        config.ROLES[role] = replace(config.ROLES[role], effort="low")
    config.MAX_TOOL_CALLS_PER_TURN = 5
    config.MAX_FIGURE_IMAGES = 2
    print("quick mode: up to 2 meetings x 2 cycles, low effort members, 2 picture rounds")
    return {"max_a_iters": 2, "max_s1_rounds": 2, "max_b_returns": 0, "min_cycles": 2, "max_cycles": 2}


def _cmd_examples(args: argparse.Namespace) -> int:
    from hs.schemas import ProblemSet

    client = _make_client(bool(args.fake), run_dir=None)
    result: ProblemSet = client.structured(
        "example_generator", ProblemSet,
        "Generate diverse concept-level mechanical-engineering problems.",
        f"Generate {args.n} problems: research or application goal, 3-6 constraints, 0-3 criteria, "
        "diverse domains, solvable at concept level without CAD.")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    written: list[str] = []
    for i, problem in enumerate(result.problems[: args.n], start=1):
        path = Path(f"examples/gen_{stamp}_{i}.json")
        n = 1
        while path.exists():
            n += 1
            path = Path(f"examples/gen_{stamp}_{i}_{n}.json")
        path.write_text(problem.model_dump_json(indent=2), encoding="utf-8")
        written.append(str(path))
        print(path)
    return 0


def _cmd_feedback(args: argparse.Namespace) -> int:
    from hs.lessons import add_user_feedback

    add_user_feedback(args.text)
    print("feedback appended to knowledge/lessons.md ## User feedback")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    archive_path = run_dir / "archive.jsonl"
    if archive_path.exists():
        print("== verdict history ==")
        for line in archive_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                e = json.loads(line)
                print(f"{e.get('id')} iter={e.get('iteration')} rev={e.get('revision')} "
                      f"status={e.get('status')} accept={e.get('accept')}")
    ia = run_dir / "image_archive.jsonl"
    if ia.exists():
        print("== S1/S2 history ==")
        for line in ia.read_text(encoding="utf-8").splitlines():
            if line.strip():
                e = json.loads(line)
                print(f"attempt {e.get('attempt')} round {e.get('round')}: S1={e.get('s1_faithful')} "
                      f"S2={e.get('s2_flaw')} -> {e.get('decision')}")
    cost_path = run_dir / "cost.json"
    if cost_path.exists():
        cost = json.loads(cost_path.read_text(encoding="utf-8"))
        print(f"== cost: ${float(cost.get('total_usd', 0)):.4f} over {len(cost.get('entries', []))} calls ==")
    revs = sorted((run_dir / "master_prompt").glob("rev_*.md")) if (run_dir / "master_prompt").exists() else []
    print(f"master prompt revisions: {[r.name for r in revs]}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    from hs.report import write_report

    out = write_report(Path(args.run_dir))
    print(out)
    return 0


def _cmd_board(args: argparse.Namespace) -> int:
    from hs.board import write_board

    out = write_board(Path(args.run_dir), live=bool(args.live))
    print(out)
    return 0


def _cmd_showcase_build(args: argparse.Namespace) -> int:
    from hs.showcase_build import build_showcase

    out = build_showcase([Path(p) for p in args.run_dirs], Path(args.out))
    print(out)
    return 0


def _cmd_stageb(args: argparse.Namespace) -> int:
    from hs.stage_b_rerun import rerun_stage_b

    client = _make_client(bool(args.fake), run_dir=None)
    result = rerun_stage_b(client, Path(args.run_dir))
    print(json.dumps(result, indent=2))
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    from hs.report import write_compare

    out = write_compare([Path(p) for p in args.run_dirs])
    print(out)
    return 0


def _cmd_budget(args: argparse.Namespace) -> int:
    from hs.client import BudgetLedger

    ledger = BudgetLedger()
    total = ledger.total()
    print(f"Meta spend (ledger): ${total:.4f} of ${ledger.cap_usd:.2f} cap, ${ledger.cap_usd - total:.4f} left")
    print(f"ledger: {ledger.path}")
    for run_id, usd in ledger.per_run().items():
        print(f"  {run_id}: ${usd:.4f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hs", description="Hardware Scientist")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("problem")
    run.add_argument("--fake", action="store_true")
    run.add_argument("--quick", action="store_true", help="same loops, fewer cycles and rounds (about 15 min)")
    run.set_defaults(func=_cmd_run)
    ex = sub.add_parser("examples")
    ex.add_argument("--n", type=int, default=5)
    ex.add_argument("--fake", action="store_true")
    ex.set_defaults(func=_cmd_examples)
    fb = sub.add_parser("feedback")
    fb.add_argument("text")
    fb.set_defaults(func=_cmd_feedback)
    show = sub.add_parser("show")
    show.add_argument("run_dir")
    show.set_defaults(func=_cmd_show)
    rep = sub.add_parser("report")
    rep.add_argument("run_dir")
    rep.set_defaults(func=_cmd_report)
    board = sub.add_parser("board")
    board.add_argument("run_dir")
    board.add_argument("--live", action="store_true")
    board.set_defaults(func=_cmd_board)
    comp = sub.add_parser("compare")
    comp.add_argument("run_dirs", nargs="+")
    comp.set_defaults(func=_cmd_compare)
    sb = sub.add_parser("stageb")
    sb.add_argument("run_dir")
    sb.add_argument("--fake", action="store_true")
    sb.set_defaults(func=_cmd_stageb)
    scb = sub.add_parser("showcase-build")
    scb.add_argument("run_dirs", nargs="+")
    scb.add_argument("--out", default="showcase")
    scb.set_defaults(func=_cmd_showcase_build)
    bud = sub.add_parser("budget")
    bud.set_defaults(func=_cmd_budget)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
