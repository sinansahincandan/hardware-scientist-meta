"""VLM prompt writer (spec §5.2). The render carries no text: labels are drawn by code (round-3 16a)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hs.schemas import SchematicSpec, SolutionPrompt, VLMPrompt
from hs.stage_b.image_archive import ImageArchive


class VLMPromptWriter:
    def __init__(self, client: Any) -> None:
        self.client = client

    def write(self, solution: SolutionPrompt, spec: SchematicSpec, schematic_png: Path,
              labeled_png: Path, archive: ImageArchive, corrections: str = "",
              previous_prompt: str = "", council_sketches: list[Path] | None = None,
              callouts: bool = True) -> VLMPrompt:
        prompt = (
            f"SOLUTION:\n{solution.model_dump_json(indent=2)}\n\n"
            f"PREFERRED VIEW: {solution.figure_spec.preferred_view}\n\n"
            f"WHERE IT WORKS (from the problem): {solution.problem_restatement}\n\n"
            f"IMAGE ARCHIVE SUMMARY:\n{archive.summary_text()}\n\n"
            "GOAL: a correct, photorealistic rendering of this device in its use context, with the workpiece or "
            "load present, real materials, product-shot lighting and the mechanism readable. Correctness against "
            "the mechanism sketch comes first, style second. The images after the first two are the engineers' "
            "own hand sketches of the mechanism: use them to understand how the working parts look and move "
            "(for example how many wheels a cluster has and how they are arranged). The sketch's colours, circles and line style are "
            "drawing conventions, not materials or parts: never ask for them. Describe sizes mainly relative to "
            "neighbouring parts and to familiar things in the scene (a person, a door, a stair step); the design's "
            "numbers are references for proportion, not values to print or to obsess over. Place the device in the "
            "setting the problem describes (the ground, bed, structure or room it works in, as the problem names "
            "it), never a generic field or studio; the objects it works with (what it carries, fills, grips or "
            "sits on) appear at the sizes the solution states relative to the device. Draw each mechanism as the "
            "kind the solution and sketches name (a chain-driven slide stays a slide, not a linkage of cylinders), "
            "and make every flow visible between its stations (how material gets from where it is taken to where "
            "it is stored or delivered).\n"
            "Write the image prompt plus a structured visual plan: view; spatial layout; "
            "operating moment (the device in its operating moment, workpiece/sample present); "
            "force/motion/signal transfer path; 4-7 focus parts each with material and purpose; real "
            "interactions between the parts; an avoid list. The focus parts MUST include the critical part "
            "and its direct sketch neighbours, and every focus part must be visibly drawn (not hidden inside "
            "another part). Show fixed vs moving parts and the force/signal path. Keep the parts, their "
            "connections and relative sizes of the reference; perspective may differ. "
            + ("CALLOUTS (Fig. 2): the image model draws a short callout with a thin leader line for each focus "
               "part; set each focus part's callout to its plain name exactly as it should read (2 to 4 words, no "
               "numbers, no units, no ids). Ask for clean, legible callouts on light tags placed in empty space, and "
               "no other text, margins or scale bars. "
               if callouts else
               "The image carries no text, labels, callouts, margins or scale bars: code adds every label afterwards. ")
            + "In must_not, name kinds of things to avoid; never quote the text, numbers or names you want kept out "
            "of the image (a quoted string gets drawn).\n\n"
            + (f"KEPT PROMPT (the last render that was kept came from this prompt; edit it where the "
               f"corrections point, keep the rest):\n{previous_prompt}\n\n" if previous_prompt else "")
            + (f"TARGETED CORRECTIONS FROM ACTUAL-IMAGE REVIEW (apply verbatim):\n{corrections}\n" if corrections else "")
        )
        vlm = self.client.structured("vlm_writer", VLMPrompt,
                                     "You are the image-prompt writer for a photorealistic product rendering.",
                                     prompt, image_paths=[schematic_png, labeled_png, *(council_sketches or [])])
        # C15: an avoid-entry that quotes numbers gets drawn into the image; drop such entries.
        must_not = [m for m in vlm.must_not if not any(ch.isdigit() for ch in m)]
        return VLMPrompt(prompt=vlm.prompt, must_not=must_not,
                         changes_from_previous=vlm.changes_from_previous,
                         visual_plan=vlm.visual_plan, focus_parts=vlm.focus_parts)
