"""Stage B rerun from an accepted solution (v2 C).

Reuses the exact Stage B blocks of the controller (mechanism sketch,
VLM writer, image model, annotator, DesignerEval with regions and
source trace, VLM prompt gradient, local edit + progress check, figure
composer) without re-running Stage A. If the designer routes back with
an S2 design flaw, the feedback is saved as s2_return.json and Stage A
is left to a full `hs run`.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from hs import config
from hs.client import BudgetExceeded
from hs.controller import Trace, build_references, make_run_dir
from hs.schemas import Problem, SolutionPrompt
from hs.stage_b import figure as figure_mod
from hs.stage_b import schematic as schematic_mod
from hs.stage_b.annotate import Annotator
from hs.stage_b.designer_eval import DesignerEvalRunner, decide, feedback_text, label_failed
from hs.stage_b.image_archive import ImageArchive
from hs.stage_b.image_model import ImageModel
from hs.stage_b.vlm_prompt import VLMPromptWriter


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


def rerun_stage_b(client: Any, source: Path, base: Path = Path("runs")) -> dict[str, Any]:
    problem = Problem.model_validate_json((source / "problem.json").read_text(encoding="utf-8"))
    solution, sol_path = find_accepted_solution(source)
    run_dir = make_run_dir(problem, base)
    (run_dir / "problem.json").write_text(problem.model_dump_json(indent=2), encoding="utf-8")
    if hasattr(client, "cost"):
        client.cost.run_dir = run_dir
        client.cost.flush()
    trace = Trace(run_dir)
    trace.log(f"stage B rerun seeded from {source} ({sol_path.relative_to(source)})")
    iter_dir = run_dir / "stage_a" / "iter_00"
    iter_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(sol_path, iter_dir / "solution.json")
    (iter_dir / "verdict.json").write_text(json.dumps(
        {"accept": True, "feedback": f"seeded from accepted solution in {source.name} for v2 Stage B rerun",
         "evidence_requests": []}, indent=2), encoding="utf-8")
    for extra in ("novelty.md", "whiteboard.md"):
        src_file = sol_path.parent / extra
        if src_file.exists():
            shutil.copy(src_file, iter_dir / extra)

    img_archive = ImageArchive(run_dir)
    result: dict[str, Any] = {"run_dir": str(run_dir), "decision": "schematic_failed"}
    spec, errors = schematic_mod.spec_and_check(client, solution)
    if spec is not None and not errors:
        result.update(_rounds(client, solution, spec, run_dir, trace, img_archive, source))
    else:
        (run_dir / "s2_return.json").write_text(json.dumps(
            {"feedback": "the concept cannot be drawn consistently: " + "; ".join(errors)}, indent=2),
            encoding="utf-8")
        result["decision"] = "s2_return"
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


def _rounds(client: Any, solution: SolutionPrompt, spec: Any, run_dir: Path,
            trace: Trace, img_archive: ImageArchive, source: Path) -> dict[str, Any]:
    from hs.stage_b.prompt_gradient import VLMPromptGradientRunner, composite_region

    sources: list[str] = []
    for novelty in sorted(source.glob("stage_a/iter_*/novelty.md")):
        for line in novelty.read_text(encoding="utf-8").splitlines():
            if line.startswith("- http"):
                sources.append(line[2:])
    label_failures = 0
    s1_diffs = ""
    last: tuple[Any, ...] | None = None
    best_pass: tuple[Any, ...] | None = None
    decision = "s2_return"
    ev = None
    for r in range(config.MAX_S1_ROUNDS):
        round_dir = run_dir / "stage_b" / "attempt_00" / f"round_{r:02d}"
        round_dir.mkdir(parents=True, exist_ok=True)
        geometry = schematic_mod.render_schematic(spec, round_dir)
        vlm = VLMPromptWriter(client).write(
            solution, spec, round_dir / "schematic.png", round_dir / "schematic_labeled.png",
            img_archive, s1_differences=s1_diffs, corrections=s1_diffs,
            force_code_labels=label_failures >= 2)
        (round_dir / "vlm_prompt.json").write_text(vlm.model_dump_json(indent=2), encoding="utf-8")
        render_path = round_dir / "render.png"
        render_path.write_bytes(ImageModel(client).edit(vlm, round_dir / "schematic.png"))
        annotated_path, loc, missing = Annotator(client).run(
            render_path, spec, geometry, round_dir / "annotated.png",
            code_labels=(vlm.label_mode == "code"))
        ev = DesignerEvalRunner(client).run(annotated_path, round_dir / "schematic_labeled.png",
                                            solution, missing)
        decision = decide(ev, r, config.MAX_S1_ROUNDS)
        (round_dir / "eval.json").write_text(ev.model_dump_json(indent=2), encoding="utf-8")
        (round_dir / "decision.txt").write_text(decision + "\n", encoding="utf-8")
        img_archive.add(attempt=0, round_idx=r, vlm_prompt=vlm.prompt,
                        render_path=str(render_path), annotated_path=str(annotated_path),
                        s1_faithful=ev.s1_faithful, s1_differences=ev.s1_differences,
                        s2_flaw=ev.s2_flaw, s2_feedback=ev.s2_feedback, decision=decision)
        last = (solution, spec, annotated_path, loc, render_path)
        if ev.s1_faithful:
            best_pass = last
        trace.log(f"stageb round {r}: S1={ev.s1_faithful} S2={ev.s2_flaw} decision={decision}")
        if label_failed(ev):
            label_failures += 1
        s1_diffs = "\n".join(x for x in (ev.s1_differences, ev.label_findings, ev.pixel_description) if x)
        if decision == "s1_retry":
            grad_runner = VLMPromptGradientRunner(client)
            try:
                grad = grad_runner.run(render_path, round_dir / "schematic_labeled.png", vlm, ev)
                (round_dir / "vlm_gradient.json").write_text(grad.model_dump_json(indent=2), encoding="utf-8")
                s1_diffs = (grad.summary + "\n" + "\n".join(
                    f"{g.part_id}: {g.diagnosis} -> {g.prompt_fix}" for g in grad.per_region)
                    + "\n" + s1_diffs)
                render_regions = [x for x in ev.regions if x.source == "render" and len(x.box) == 4]
                if grad.fix_mode == "local" and render_regions:
                    current = render_path
                    for region in render_regions:
                        fix = next((g.prompt_fix for g in grad.per_region
                                    if g.part_id == region.part_id), region.expected)
                        edited_path = round_dir / f"edited_{region.part_id}.png"
                        edited_path.write_bytes(client.image_edit(
                            f"Change only this: {fix}. Keep everything else in the image identical.", current))
                        comp_path = round_dir / f"local_{region.part_id}.png"
                        info = composite_region(current, edited_path, region.box, comp_path)
                        (round_dir / f"composite_{region.part_id}.json").write_text(
                            json.dumps(info), encoding="utf-8")
                        if not info["outside_unchanged"]:
                            continue
                        ann_local, _l, _m = Annotator(client).run(
                            comp_path, spec, geometry, round_dir / f"annotated_local_{region.part_id}.png",
                            code_labels=(vlm.label_mode == "code"))
                        check = grad_runner.progress_check(ann_local, ev, fix)
                        (round_dir / f"progress_{region.part_id}.json").write_text(
                            check.model_dump_json(indent=2), encoding="utf-8")
                        if check.fixed_region_pass and check.previous_pass and not check.seam_visible:
                            current = comp_path
                            trace.log(f"stageb round {r}: local edit {region.part_id} kept")
            except BudgetExceeded:
                raise
            except Exception as exc:
                trace.log(f"stageb round {r}: VLM prompt gradient skipped: {exc}")
        if decision != "s1_retry":
            break
    out: dict[str, Any] = {"decision": decision}
    chosen = best_pass or last
    if decision == "s1_pass" and chosen is not None:
        sol, sp, annot, loc, _render = chosen
        figure = figure_mod.compose(client, sol, sp, annotated_path=annot, localization=loc,
                                    run_dir=run_dir, master_history=[], s_history=img_archive.entries(),
                                    sources=sources)
        out["figure"] = str(figure)
    elif decision == "s2_return" and ev is not None:
        fb = feedback_text(ev, config.MAX_S1_ROUNDS - 1, config.MAX_S1_ROUNDS)
        (run_dir / "s2_return.json").write_text(json.dumps({"feedback": fb}, indent=2), encoding="utf-8")
        out["feedback"] = fb
    return out
