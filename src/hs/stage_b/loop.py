"""The Stage B round loop (spec §5, round-3 items A1/A7): one copy, used by the
controller and by `hs stageb`.

Per round: mechanism sketch -> VLM prompt -> render -> localization + code labels ->
designer evaluation of the UNLABELED render -> decide. On an S1 failure the VLM prompt
gradient diagnoses each region; a local fix composites edited pixels into the render
(boxes and composite share the render's coordinate basis), a full fix rewrites the prompt.

Outcomes (A1): s1_pass, s2_return (the critic saw a design flaw: the only outcome that
sends a gradient back to Stage A), s1_exhausted (could not be drawn faithfully within the
round limit: reported as such, nothing is sent to the design).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hs.client import BudgetExceeded
from hs.schemas import DesignerEval, Localization, SchematicSpec, SolutionPrompt, VLMPrompt
from hs.stage_b import part_map as pm
from hs.stage_b import schematic as schematic_mod
from hs.stage_b.annotate import Annotator
from hs.stage_b.designer_eval import DesignerEvalRunner, decide, s1_exhausted_text, s2_feedback_text
from hs.stage_b.image_archive import ImageArchive
from hs.stage_b.image_model import ImageModel
from hs.stage_b.vlm_prompt import VLMPromptWriter


@dataclass
class RoundResult:
    solution: SolutionPrompt
    spec: SchematicSpec
    annotated: Path
    localization: Localization
    render: Path


@dataclass
class StageBResult:
    decision: str  # s1_pass | s2_return | s1_exhausted
    rounds: int
    last: RoundResult | None = None
    best_pass: RoundResult | None = None
    ev: DesignerEval | None = None
    feedback: str = ""  # s2_return: the designer's own words + regions; s1_exhausted: the report text
    notes: list[str] = field(default_factory=list)


def _fault_key(part_id: str, observed: str) -> str:
    return f"{part_id}: {' '.join(observed.split())}"


def run_stage_b(client: Any, solution: SolutionPrompt, spec: SchematicSpec, attempt_dir: Path,
                img_archive: ImageArchive, log: Any, *, attempt: int, max_rounds: int) -> StageBResult:
    """Run up to `max_rounds` rounds; `log(msg)` receives one trace line per event.

    C17: every round after the first is judged against all earlier faults (fixed / still wrong /
    regressed) and by a written comparison with the kept render; it is kept only if it fixed something
    and broke nothing, otherwise the render and the image prompt revert to the kept round.
    """
    from hs.stage_b.prompt_gradient import VLMPromptGradientRunner, composite_region

    attempt_dir.mkdir(parents=True, exist_ok=True)
    part_map = pm.build_part_map(client, solution, spec, attempt_dir)
    result = StageBResult(decision="s1_exhausted", rounds=0)
    corrections = ""
    kept: dict[str, Any] | None = None  # {"render", "vlm", "ev", "sam", "round"}
    earlier_faults: dict[str, str] = {}  # fault key -> part id, every fault flagged in any round
    carry: tuple[Path, VLMPrompt] | None = None  # a kept local edit is the next round's render
    for r in range(max_rounds):
        round_dir = attempt_dir / f"round_{r:02d}"
        round_dir.mkdir(parents=True, exist_ok=True)
        geometry = schematic_mod.render_schematic(spec, round_dir)
        render_path = round_dir / "render.png"
        if carry is not None:
            render_path.write_bytes(carry[0].read_bytes())
            vlm = carry[1]
            carry = None
        else:
            vlm = VLMPromptWriter(client).write(
                solution, spec, round_dir / "schematic.png", round_dir / "schematic_labeled.png", img_archive,
                corrections=corrections, previous_prompt=kept["vlm"].prompt if kept else "")
            render_path.write_bytes(ImageModel(client).edit(vlm, round_dir / "schematic.png"))
        (round_dir / "vlm_prompt.json").write_text(vlm.model_dump_json(indent=2), encoding="utf-8")
        meas = pm.measure(client, render_path, part_map)
        diffs = pm.differences(meas, part_map)
        rechecks = pm.recheck(meas, diffs, kept["sam"] if kept else None)
        pm.save_round(round_dir, meas, diffs, rechecks)
        sam_text = pm.evidence_text(diffs, rechecks, part_map)
        annotated_path, loc, missing = Annotator(client).run(render_path, spec, geometry, round_dir / "annotated.png",
                                                             localization=pm.to_localization(meas, spec))
        ev = DesignerEvalRunner(client).run(
            render_path, round_dir / "schematic_labeled.png", solution, missing, measurements=sam_text,
            earlier_faults=list(earlier_faults), previous_render=kept["render"] if kept else None)
        decision = decide(ev, r, max_rounds)
        (round_dir / "eval.json").write_text(ev.model_dump_json(indent=2), encoding="utf-8")
        (round_dir / "decision.txt").write_text(decision + "\n", encoding="utf-8")
        img_archive.add(attempt=attempt, round_idx=r, vlm_prompt=vlm.prompt,
                        render_path=str(render_path), annotated_path=str(annotated_path),
                        s1_faithful=ev.s1_faithful, s1_differences=ev.s1_differences,
                        s2_flaw=ev.s2_flaw, s2_feedback=ev.s2_feedback, decision=decision)
        this_round = RoundResult(solution, spec, annotated_path, loc, render_path)
        result.ev, result.rounds, result.decision = ev, r + 1, decision
        # C17 keep or revert, from the critic's own statuses and comparison
        statuses = [x.status for x in ev.previous_regions]
        new_faults = [x for x in ev.regions if _fault_key(x.part_id, x.observed) not in earlier_faults
                      and x.part_id not in set(earlier_faults.values())]
        if kept is None:
            keep, why = True, "first round"
        elif "regressed" in statuses:
            keep, why = False, "a fault flagged earlier regressed"
        elif decision == "s1_pass":
            keep, why = True, "faithful, and every earlier fault is fixed"
        elif "fixed" in statuses and not new_faults:
            keep, why = True, "fixed an earlier fault and introduced none"
        else:
            keep, why = False, "fixed no earlier fault" if "fixed" not in statuses else "introduced new faults"
        _log_sam_use(round_dir, attempt_dir, r, diffs, ev, keep, why)
        log(f"attempt {attempt} round {r}: S1={ev.s1_faithful} S2={ev.s2_flaw} decision={decision}; "
            f"{'kept' if keep else 'reverted'} ({why})")
        if keep:
            kept = {"render": render_path, "vlm": vlm, "ev": ev, "sam": {**meas, "differences": diffs}, "round": r}
            result.last = this_round
            if ev.s1_faithful and decision != "s2_return":
                result.best_pass = this_round
        for x in ev.regions:
            earlier_faults.setdefault(_fault_key(x.part_id, x.observed), x.part_id)
        if decision != "s1_retry":
            break
        if not keep:
            corrections = (corrections + "\nTHE LAST ATTEMPT WAS REVERTED (" + why + "): "
                           + ev.comparison_with_previous).strip()
            continue
        # S1 failed with rounds left: the regions are the output gradient; the VLM prompt gradient
        # names the prompt sentence at fault and chooses a local or full fix.
        corrections = "\n".join(x for x in (ev.s1_differences, sam_text) if x)
        grad_runner = VLMPromptGradientRunner(client)
        try:
            grad = grad_runner.run(render_path, round_dir / "schematic_labeled.png", vlm, ev, measurements=sam_text)
        except BudgetExceeded:
            raise
        except Exception as exc:  # the gradient is advisory; the next round still gets the differences
            log(f"attempt {attempt} round {r}: VLM prompt gradient failed: {exc}")
            continue
        (round_dir / "vlm_gradient.json").write_text(grad.model_dump_json(indent=2), encoding="utf-8")
        corrections = (grad.summary + "\n" + "\n".join(
            f"{g.part_id}: {g.diagnosis} -> {g.prompt_fix}" for g in grad.per_region) + "\n" + corrections)
        render_regions = [x for x in ev.regions if x.source == "render" and len(x.box) == 4]
        if grad.fix_mode != "local" or not render_regions:
            continue
        current = render_path
        for region in render_regions:
            fix = next((g.prompt_fix for g in grad.per_region if g.part_id == region.part_id), region.expected)
            edited_path = round_dir / f"edited_{region.part_id}.png"
            edited_path.write_bytes(client.image_edit(
                f"Change only this: {fix}. Keep everything else in the image identical.", current))
            comp_path = round_dir / f"local_{region.part_id}.png"
            info = composite_region(current, edited_path, region.box, comp_path)
            (round_dir / f"composite_{region.part_id}.json").write_text(json.dumps(info), encoding="utf-8")
            if not info["outside_unchanged"]:
                log(f"attempt {attempt} round {r}: local edit {region.part_id} reverted (outside-box pixels changed)")
                continue
            check = grad_runner.progress_check(comp_path, ev, fix)
            (round_dir / f"progress_{region.part_id}.json").write_text(check.model_dump_json(indent=2),
                                                                       encoding="utf-8")
            if check.fixed_region_pass and check.previous_pass and not check.seam_visible:
                current = comp_path
                log(f"attempt {attempt} round {r}: local edit {region.part_id} kept")
            else:
                log(f"attempt {attempt} round {r}: local edit {region.part_id} reverted by progress check")
        if current != render_path:
            carry = (current, vlm)
    if result.ev is not None:
        if result.decision == "s2_return":
            result.feedback = s2_feedback_text(result.ev)
        elif result.decision == "s1_exhausted":
            result.feedback = s1_exhausted_text(result.ev, result.rounds)
    return result


def _log_sam_use(round_dir: Path, attempt_dir: Path, r: int, diffs: dict[str, list[str]], ev: DesignerEval,
                 keep: bool, why: str) -> None:
    """Item 16 log: which segmenter findings the critique used, whether earlier ones were fixed, and
    which measured deviations nobody noticed (C18: an unnoticed deviation is a defect to report)."""
    mentioned = {x.part_id for x in ev.regions}
    text = " ".join(f"{d.what} {d.measured} {d.expected}" for d in ev.deviations).lower()
    unnoticed = [pid for pid in diffs if pid not in mentioned and pid.lower() not in text]
    record = {"round": r, "sam_differences": diffs, "critique_part_ids": sorted(mentioned),
              "sam_parts_used_by_critique": sorted(set(diffs) & mentioned), "unnoticed_sam_deviations": unnoticed,
              "kept": keep, "why": why,
              "earlier_faults": [x.model_dump() for x in ev.previous_regions]}
    (round_dir / "sam_use.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    if r > 0:
        prev = attempt_dir / f"round_{r - 1:02d}" / "sam_use.json"
        if prev.exists():
            data = json.loads(prev.read_text(encoding="utf-8"))
            data["outcome_next_round"] = {x.part_id: x.status for x in ev.previous_regions}
            prev.write_text(json.dumps(data, indent=2), encoding="utf-8")
