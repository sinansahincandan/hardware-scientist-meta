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
from hs.stage_b.designer_eval import (
    DesignerEvalRunner,
    decide,
    part_faults,
    s1_exhausted_text,
    s2_feedback_text,
)
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


def council_sketches(iter_dir: Path, limit: int = 2) -> list[Path]:
    """C14: the council's own sketches of the accepted concept (latest first, at most `limit`)."""
    found = sorted((iter_dir / "evidence").glob("sketch_*.png"),
                   key=lambda p: int(p.stem.split("_")[-1]) if p.stem.split("_")[-1].isdigit() else 0)
    return found[-limit:][::-1]


def concept_sketch(client: Any, solution: SolutionPrompt, spec: SchematicSpec, attempt_dir: Path,
                   sketches: list[Path], log: Any) -> Path | None:
    """Fig. 2 node 1 'concept sketch: real geometry, joints, motion, workpiece and use context': the image model
    redraws the council's own sketches as one clean pencil concept sketch; one check that it shows the parts and
    how they connect. None (code sketch used) when there is no council sketch or the check fails."""
    from hs.schemas import LightCheck

    if not sketches:
        return None
    schematic_mod.render_schematic(spec, attempt_dir, stem="parts")
    parts = ", ".join(f"{n.label}" for n in spec.nodes)
    out = attempt_dir / "concept_sketch.png"
    try:
        out.write_bytes(client.image_edit(
            "A clean engineer's pencil concept sketch on white paper, side view, of this device in use: "
            f"{solution.mechanism_sentence or solution.concept.working_principle} Draw every part with its real "
            f"shape and proportion ({parts}), how the parts connect and which ones move (small motion arrows), the "
            "load or workpiece and the ground or structure it works on. Follow the engineers' hand sketches given as "
            "references for geometry and arrangement. Line drawing only, light grey shading, no colour, no text.",
            sketches[0], extra_refs=[*sketches[1:], attempt_dir / "parts.png"]))
        check = client.structured(
            "light_check", LightCheck, "Light check of a concept sketch.",
            f"Does this sketch show these parts with plausible shapes and connections: {parts}? Is the arrangement "
            "consistent with the engineers' hand sketch (second image)? Answer from the pixels.",
            image_paths=[out, sketches[0]])
    except BudgetExceeded:
        raise
    except Exception as exc:
        log(f"attempt concept sketch could not be made ({type(exc).__name__}); code sketch used")
        return None
    (attempt_dir / "concept_sketch_check.json").write_text(check.model_dump_json(indent=2), encoding="utf-8")
    if not check.ok:
        log(f"concept sketch rejected by its check ({check.reason}); code sketch used")
        return None
    log("concept sketch drawn from the council's sketches and checked; used as the primary reference")
    return out


def run_stage_b(client: Any, solution: SolutionPrompt, spec: SchematicSpec, attempt_dir: Path,
                img_archive: ImageArchive, log: Any, *, attempt: int, max_rounds: int,
                sketches: list[Path] | None = None) -> StageBResult:
    """Run up to `max_rounds` rounds; `log(msg)` receives one trace line per event.

    C17: every round after the first is judged against all earlier faults (fixed / still wrong /
    regressed) and by a written comparison with the kept render; it is kept only if it fixed something
    and broke nothing, otherwise the render and the image prompt revert to the kept round.
    """
    from hs.stage_b.prompt_gradient import VLMPromptGradientRunner, composite_region

    attempt_dir.mkdir(parents=True, exist_ok=True)
    (attempt_dir / "schematic_spec.json").write_text(spec.model_dump_json(indent=2), encoding="utf-8")
    if sketches:
        log(f"attempt {attempt}: council sketches used as extra references: {[p.name for p in sketches]}")
    part_map = pm.build_part_map(client, solution, spec, attempt_dir)
    concept = concept_sketch(client, solution, spec, attempt_dir, sketches or [], log)
    result = StageBResult(decision="s1_exhausted", rounds=0)
    corrections = ""
    kept: dict[str, Any] | None = None  # {"render", "vlm", "ev", "sam", "round"}
    earlier_faults: dict[str, str] = {}  # part id -> the latest fault flagged on it in any round
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
                solution, spec, concept or round_dir / "schematic.png", round_dir / "schematic_labeled.png", img_archive,
                corrections=corrections, previous_prompt=kept["vlm"].prompt if kept else "",
                council_sketches=sketches)
            render_path.write_bytes(ImageModel(client).edit(vlm, concept or round_dir / "schematic.png",
                                                            council_sketches=sketches))
        (round_dir / "vlm_prompt.json").write_text(vlm.model_dump_json(indent=2), encoding="utf-8")
        meas = pm.measure(client, render_path, part_map, out_dir=round_dir)
        diffs = pm.differences(meas, part_map)
        rechecks = pm.recheck(meas, diffs, kept["sam"] if kept else None)
        pm.save_round(round_dir, meas, diffs, rechecks)
        pm.draw_overlay(render_path, round_dir / "sam.json", round_dir / "sam_overlay.png")
        sam_text = pm.evidence_text(diffs, rechecks, part_map)
        annotated_path, loc, missing = Annotator(client).run(render_path, spec, geometry, round_dir / "annotated.png",
                                                             localization=pm.to_localization(meas, spec),
                                                             draw_labels=False)  # Fig. 2: callouts are in the render
        ev = DesignerEvalRunner(client).run(
            render_path, concept or round_dir / "schematic_labeled.png", solution, missing, measurements=sam_text,
            earlier_faults=[f"{pid}: {fault}" for pid, fault in earlier_faults.items()],
            previous_render=kept["render"] if kept else None,
            critical_part=next((f"{n.label} ({n.id})" for n in spec.nodes if n.id == spec.critical_part_id), ""),
            council_sketches=sketches)
        missed = _unaddressed(diffs, ev)
        if missed:  # C18 completeness: one re-ask naming the findings the critic did not address
            log(f"attempt {attempt} round {r}: critic re-asked for unaddressed segmenter findings {missed}")
            ev = DesignerEvalRunner(client).run(
                render_path, concept or round_dir / "schematic_labeled.png", solution, missing,
                measurements=sam_text + "\nYOUR PREVIOUS ANSWER DID NOT ADDRESS THESE FINDINGS: " + ", ".join(missed)
                + ". Answer again in full, with a deviation for each of them.",
                earlier_faults=[f"{pid}: {fault}" for pid, fault in earlier_faults.items()],
                previous_render=kept["render"] if kept else None,
                critical_part=next((f"{n.label} ({n.id})" for n in spec.nodes if n.id == spec.critical_part_id), ""),
                council_sketches=sketches)
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
        new_faults = [x for x in ev.regions if x.part_id not in earlier_faults]
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
        if ev.s1_faithful and part_faults(ev):
            log(f"attempt {attempt} round {r}: the critic answered faithful but listed faults on "
                f"{', '.join(sorted(set(part_faults(ev))))}; treated as not faithful")
        log(f"attempt {attempt} round {r}: S1={ev.s1_faithful} S2={ev.s2_flaw} decision={decision}; "
            f"{'kept' if keep else 'reverted'} ({why})")
        if keep:
            kept = {"render": render_path, "vlm": vlm, "ev": ev, "sam": {**meas, "differences": diffs}, "round": r}
            result.last = this_round
            if ev.s1_faithful and not part_faults(ev) and decision != "s2_return":
                result.best_pass = this_round
        for x in ev.regions:
            earlier_faults[x.part_id] = f"{x.observed} (expected: {x.expected})"
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


def _unaddressed(diffs: dict[str, list[str]], ev: DesignerEval) -> list[str]:
    mentioned = {x.part_id for x in ev.regions}
    text = " ".join(f"{d.what} {d.measured} {d.expected}" for d in ev.deviations).lower()
    return [pid for pid in diffs if pid not in mentioned and pid.lower() not in text]


def _log_sam_use(round_dir: Path, attempt_dir: Path, r: int, diffs: dict[str, list[str]], ev: DesignerEval,
                 keep: bool, why: str) -> None:
    """Item 16 log: which segmenter findings the critique used, whether earlier ones were fixed, and
    which measured deviations nobody noticed (C18: an unnoticed deviation is a defect to report)."""
    mentioned = {x.part_id for x in ev.regions}
    unnoticed = _unaddressed(diffs, ev)
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
