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


def run_stage_b(client: Any, solution: SolutionPrompt, spec: SchematicSpec, attempt_dir: Path,
                img_archive: ImageArchive, log: Any, *, attempt: int, max_rounds: int) -> StageBResult:
    """Run up to `max_rounds` rounds; `log(msg)` receives one trace line per event."""
    from hs.stage_b.prompt_gradient import VLMPromptGradientRunner, composite_region

    result = StageBResult(decision="s1_exhausted", rounds=0)
    corrections = ""
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
            vlm = VLMPromptWriter(client).write(solution, spec, round_dir / "schematic.png",
                                                round_dir / "schematic_labeled.png", img_archive,
                                                corrections=corrections)
            render_path.write_bytes(ImageModel(client).edit(vlm, round_dir / "schematic.png"))
        (round_dir / "vlm_prompt.json").write_text(vlm.model_dump_json(indent=2), encoding="utf-8")
        annotated_path, loc, missing = Annotator(client).run(render_path, spec, geometry,
                                                             round_dir / "annotated.png")
        ev = DesignerEvalRunner(client).run(render_path, round_dir / "schematic_labeled.png", solution, missing)
        decision = decide(ev, r, max_rounds)
        (round_dir / "eval.json").write_text(ev.model_dump_json(indent=2), encoding="utf-8")
        (round_dir / "decision.txt").write_text(decision + "\n", encoding="utf-8")
        img_archive.add(attempt=attempt, round_idx=r, vlm_prompt=vlm.prompt,
                        render_path=str(render_path), annotated_path=str(annotated_path),
                        s1_faithful=ev.s1_faithful, s1_differences=ev.s1_differences,
                        s2_flaw=ev.s2_flaw, s2_feedback=ev.s2_feedback, decision=decision)
        this_round = RoundResult(solution, spec, annotated_path, loc, render_path)
        result.last, result.ev, result.rounds, result.decision = this_round, ev, r + 1, decision
        if ev.s1_faithful:
            result.best_pass = this_round
        log(f"attempt {attempt} round {r}: S1={ev.s1_faithful} S2={ev.s2_flaw} decision={decision}")
        if decision != "s1_retry":
            break
        # S1 failed with rounds left: the regions are the output gradient; the VLM prompt
        # gradient names the prompt sentence at fault and chooses a local or full fix.
        corrections = "\n".join(x for x in (ev.s1_differences, ev.pixel_description) if x)
        grad_runner = VLMPromptGradientRunner(client)
        try:
            grad = grad_runner.run(render_path, round_dir / "schematic_labeled.png", vlm, ev)
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
