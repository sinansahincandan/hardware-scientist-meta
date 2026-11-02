"""Designer evaluation: pixel-first S1/S2 + routing (spec §5.5, round-3 A1)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hs import config
from hs.schemas import DesignerEval, SolutionPrompt


def decide(ev: DesignerEval, round_idx: int, max_rounds: int = config.MAX_S1_ROUNDS) -> str:
    """s1_pass | s1_retry | s2_return | s1_exhausted, from the critic's own yes/no fields.

    Only the critic's s2_flaw sends the concept back to Stage A. Running out of rounds is
    s1_exhausted: the picture could not be drawn faithfully, which says nothing about the design.
    """
    if ev.s2_flaw:
        return "s2_return"
    if ev.s1_faithful:
        return "s1_pass"
    if round_idx + 1 < max_rounds:
        return "s1_retry"
    return "s1_exhausted"


def _regions_text(ev: DesignerEval) -> str:
    return "\n".join(f"- {r.part_id} (box {r.box}): observed {r.observed}; expected {r.expected}"
                     for r in ev.regions)


def s2_feedback_text(ev: DesignerEval) -> str:
    """The designer's own words and regions: the feedback Stage A receives on an S2 return."""
    regions = _regions_text(ev)
    return ev.s2_feedback + (f"\nRegions the designer pointed at:\n{regions}" if regions else "")


def s1_exhausted_text(ev: DesignerEval, rounds: int) -> str:
    """Report text for an S1 exhaustion; never sent to the design."""
    return (f"The render could not be drawn faithfully to the mechanism sketch after {rounds} rounds. "
            f"Differences in the last round: {ev.s1_differences}")


class DesignerEvalRunner:
    def __init__(self, client: Any) -> None:
        self.client = client

    def run(self, render_png: Path, sketch_png: Path, solution: SolutionPrompt,
            missing_parts: list[str]) -> DesignerEval:
        prompt = (
            "The first image is the render to judge (it carries no labels; any text, numbers, arrows, "
            "margins or callouts drawn into it are themselves a depiction fault). The second image is the "
            "labeled mechanism sketch it must follow.\n"
            "STEP 1 — PIXEL-FIRST: look at the render ONLY and write pixel_description: what you actually "
            "see, part by part, and how the parts physically touch or connect. Do this before reading the "
            "solution below.\n"
            "STEP 2 — REGIONS: for every mismatch with the sketch, add a region: box [x0,y0,x1,y1] on the "
            "0-1000 grid of the render (origin top-left), part_id, observed (what the pixels show), expected "
            "(what the sketch shows), and source: 'render' when the render differs from the sketch, "
            "'schematic' when the sketch itself is wrong or silent on this aspect. A render that looks like a "
            "diagram, cartoon or CAD wireframe is a depiction fault.\n"
            "STEP 3 — S1/S2: s1_faithful = same parts, same connections, same relative sizes, orientations and "
            "directions as the sketch (perspective may differ). s2_flaw = seeing the device exposes a real "
            "design problem (interference, impossible assembly, a load path that cannot work, an unreachable "
            "part), or the flaw is already in the sketch or in the design itself. Do not blame the design for "
            "rendering mistakes; s2_feedback must point at a concrete feature of the image.\n\n"
            f"SOLUTION SUMMARY:\n{solution.model_dump_json(indent=2)}\n\n"
            f"PARTS THE LOCALIZER COULD NOT FIND IN THE RENDER: {missing_parts}\n"
        )
        return self.client.structured("designer_eval", DesignerEval,
                                      "You are the designer-evaluator (VLM). Compare the render with the mechanism sketch.",
                                      prompt, image_paths=[render_png, sketch_png])
