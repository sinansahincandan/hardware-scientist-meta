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
    # R4: a design flaw counts only on a faithful render, or when the critic traces it to the sketch or the
    # design itself (a region with source "schematic"); otherwise it is a drawing fault like any other.
    if ev.s2_flaw and (ev.s1_faithful or any(r.source == "schematic" for r in ev.regions)):
        return "s2_return"
    # C17: faithful only when the critic's own statuses leave no earlier fault unfixed.
    if ev.s1_faithful and all(x.status == "fixed" for x in ev.previous_regions):
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
    regions = _regions_text(ev)
    return (f"DRAWING FAILURE, not a verdict on the design: the render could not be drawn faithfully to the "
            f"mechanism sketch after {rounds} rounds. Differences in the last round: {ev.s1_differences}"
            + (f"\nRegions:\n{regions}" if regions else "")
            + "\nDecide whether the design is under-specified (say what the council must specify) or whether "
              "this says nothing about the design.")


class DesignerEvalRunner:
    def __init__(self, client: Any) -> None:
        self.client = client

    def run(self, render_png: Path, sketch_png: Path, solution: SolutionPrompt,
            missing_parts: list[str], measurements: str = "", earlier_faults: list[str] | None = None,
            previous_render: Path | None = None, critical_part: str = "",
            council_sketches: list[Path] | None = None) -> DesignerEval:
        earlier = "\n".join(f"- {f}" for f in earlier_faults or [])
        prompt = (
            "The first image is the render to judge (it carries no labels; any text, numbers, arrows, "
            "margins or callouts drawn into it are themselves a depiction fault). The second image is the "
            "labeled mechanism sketch it must follow. Any images after the previous render are the engineers' "
            "own hand sketches of the mechanism.\n"
            "STEP 1 — PIXEL-FIRST: look at the render ONLY and write pixel_description: what you actually "
            "see, part by part, and how the parts physically touch or connect. Do this before reading the "
            "solution below.\n"
            "STEP 2 — REGIONS: for every mismatch with the sketch, add a region: box [x0,y0,x1,y1] on the "
            "0-1000 grid of the render (origin top-left), part_id, observed (what the pixels show), expected "
            "(what the sketch shows), and source: 'render' when the render differs from the sketch, "
            "'schematic' when the sketch itself is wrong or silent on this aspect. A render that looks like a "
            "diagram, cartoon or CAD wireframe is a depiction fault.\n"
            "STEP 3 — S1/S2: s1_faithful = same parts, same connections, same relative sizes, orientations and "
            "directions as the sketch (perspective may differ). Image models are poor at exact counts: a count "
            "or size that differs but does not change how the device works (eight panels drawn for six, a "
            "partial load of crates) is a deviation to list with matters=false and does not make the render "
            "unfaithful; S1 fails for missing or wrong parts or connections, or for deviations that matter for "
            "the working principle. s2_flaw = seeing the device exposes a real "
            "design problem (interference, impossible assembly, a load path that cannot work, an unreachable "
            "part), or the flaw is already in the sketch or in the design itself (then mark those regions "
            "source 'schematic'). Report a design flaw only when the render is faithful or the flaw is in the "
            "sketch or design: a flaw seen only in an unfaithful render is a drawing fault. Do not blame the design for "
            "rendering mistakes; s2_feedback must point at a concrete feature of the image.\n"
            + (f"STEP 3b — CRITICAL PART: the part that decides whether this concept works is {critical_part}. "
               "Say in pixel_description exactly how it is drawn (how many elements, how they are arranged and "
               "connected). If its working geometry is not visible as in the sketch and the engineers' sketches, "
               "the render is not faithful. A segmenter that cannot find a part is not proof that the part is "
               "absent or present: look at the pixels yourself.\n" if critical_part else "")
            + "STEP 4 — DEVIATIONS: list every visible deviation you can measure (scale, counts, orientations, "
            "proportions), including each one in the segmenter measurements below, and say whether it matters "
            "for the working principle (in concept design a deviation may be acceptable, but it must be noticed).\n"
            + (("STEP 5 — EARLIER FAULTS: for EVERY fault below (flagged in earlier rounds) set previous_regions: "
                "fixed, still_wrong or regressed, with a note. A fault flagged earlier may not quietly pass now. "
                "Then write comparison_with_previous: compared with the previous render (third image), did this "
                "one fix the listed faults, and did it introduce new ones?\nEARLIER FAULTS:\n" + earlier + "\n")
               if earlier else "")
            + (f"\n{measurements}\n" if measurements else "")
            + f"\nSOLUTION SUMMARY:\n{solution.model_dump_json(indent=2)}\n\n"
            + f"PARTS THE LOCALIZER COULD NOT FIND IN THE RENDER: {missing_parts}\n"
        )
        return self.client.structured("designer_eval", DesignerEval,
                                      "You are the designer-evaluator (VLM). Compare the render with the mechanism sketch.",
                                      prompt, image_paths=[render_png, sketch_png]
                                      + ([previous_render] if previous_render is not None else [])
                                      + list(council_sketches or []))
