"""Stage B rerun from an accepted solution (`hs stageb`).

Uses the one Stage B loop (`hs.stage_b.loop`) without re-running Stage A. The new run
folder records where its solution came from (`seeded_from.json`); it holds no meeting,
no verdict and no transcript, so the pages never narrate a meeting for it (round-3 A2).
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from hs import config
from hs.controller import Trace, build_references, make_run_dir
from hs.schemas import Problem, SolutionPrompt
from hs.stage_b import figure as figure_mod
from hs.stage_b import schematic as schematic_mod
from hs.stage_b.image_archive import ImageArchive
from hs.stage_b.loop import run_stage_b


def find_accepted_solution(source: Path) -> tuple[SolutionPrompt, Path]:
    candidates = sorted(source.glob("stage_a/iter_*/solution.json"))
    for sol_path in reversed(candidates):
        verdict_path = sol_path.parent / "verdict.json"
        if verdict_path.exists() and json.loads(verdict_path.read_text(encoding="utf-8")).get("accept"):
            return SolutionPrompt.model_validate_json(sol_path.read_text(encoding="utf-8")), sol_path
    if candidates:
        sol_path = candidates[-1]
        return SolutionPrompt.model_validate_json(sol_path.read_text(encoding="utf-8")), sol_path
    raise FileNotFoundError(f"no solution.json under {source}/stage_a")


def rerun_stage_b(client: Any, source: Path, base: Path = config.PROJECT_ROOT / "runs") -> dict[str, Any]:
    problem = Problem.model_validate_json((source / "problem.json").read_text(encoding="utf-8"))
    solution, sol_path = find_accepted_solution(source)
    run_dir = make_run_dir(problem, base)
    (run_dir / "problem.json").write_text(problem.model_dump_json(indent=2), encoding="utf-8")
    if hasattr(client, "cost"):
        client.cost.run_dir = run_dir
        client.cost.flush()
    trace = Trace(run_dir)
    trace.log(f"stage B rerun seeded from {source} ({sol_path.relative_to(source)}); no Stage A in this run")
    shutil.copy(sol_path, run_dir / "seeded_solution.json")
    (run_dir / "seeded_from.json").write_text(json.dumps(
        {"source_run": source.name, "solution": str(sol_path.relative_to(source))}, indent=2), encoding="utf-8")

    img_archive = ImageArchive(run_dir)
    result: dict[str, Any] = {"run_dir": str(run_dir)}
    spec, errors = schematic_mod.spec_and_check(client, solution)
    if spec is None or errors:
        result.update(decision="schematic_check_failed",
                      feedback="the concept cannot be drawn consistently: " + "; ".join(errors))
    else:
        sb = run_stage_b(client, solution, spec, run_dir / "stage_b" / "attempt_00", img_archive, trace.log,
                         attempt=0, max_rounds=config.MAX_S1_ROUNDS)
        result.update(decision=sb.decision, feedback=sb.feedback)
        if sb.best_pass is not None:
            rnd = sb.best_pass
            figure = figure_mod.compose(client, rnd.solution, rnd.spec, annotated_path=rnd.annotated,
                                        render_path=rnd.render, localization=rnd.localization,
                                        run_dir=run_dir, master_history=[], s_history=img_archive.entries(),
                                        sources=[], best_effort=sb.decision != "s1_pass")
            result["figure"] = str(figure)
    (run_dir / "stage_b_outcome.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    try:
        build_references(run_dir)
        from hs.board import write_board
        from hs.report import write_report

        write_report(run_dir)
        write_board(run_dir)
    except Exception as exc:  # report must never mask the result
        trace.log(f"report/board generation failed: {exc}")
    cost_file = run_dir / "cost.json"
    result["cost_usd"] = float(json.loads(cost_file.read_text(encoding="utf-8")).get("total_usd", 0.0)) \
        if cost_file.exists() else 0.0
    return result
