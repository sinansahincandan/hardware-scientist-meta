"""VLM prompt writer (spec §5.2). The render carries no text: labels are drawn by code (round-3 16a)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hs.schemas import SchematicSpec, SolutionPrompt, VLMPrompt
from hs.stage_b.image_archive import ImageArchive
from hs.stage_b.schematic import overall_size_mm, scale_reference


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
            f"OVERALL SIZE: the whole device is about {overall_size_mm(spec):.0f} mm across; show it with "
            f"{scale_reference(overall_size_mm(spec)).split(',')[0]} or another everyday object of known size in "
            "the scene, so a viewer reads its true size; a small device is shown close up in the hand or on the "
            "thing it mounts to, never as a large block; the scale object is the only extra thing in the picture.\n\n"
            f"IMAGE ARCHIVE SUMMARY:\n{archive.summary_text()}\n\n"
            "GOAL: a correct, photorealistic product rendering of this device at work: the device, the workpiece or "
            "load it acts on (the one the problem names; when the problem names only a kind of object, an everyday one "
            "from the use the problem describes, never a prop chosen for looks), and only the surface or part it "
            "stands on or mounts to, on a plain seamless light-grey "
            "studio backdrop — no room, landscape, sky, furniture, tools, people or clutter; real materials, "
            "product-shot lighting and the mechanism readable. Correctness against "
            "the mechanism sketch comes first, style second. The images after the first two are the engineers' "
            "own hand sketches of the mechanism: use them to understand how the working parts look and move "
            "(for example how many wheels a cluster has and how they are arranged). The sketch's colours, circles and line style are "
            "drawing conventions, not materials or parts: never ask for them. Describe sizes mainly relative to "
            "neighbouring parts and to familiar things in the scene (a person, a door, a stair step); the design's "
            "numbers are references for proportion, not values to print or to obsess over. Place the device in the "
            "setting the problem describes only through what it touches (a small patch of the ground or bed it works "
            "on, the structure it mounts to, cut off cleanly at the backdrop), never a landscape or a generic field; "
            "the objects it works with (what it carries, fills, grips or "
            "sits on) appear at the sizes the solution states relative to the device. Draw each mechanism as the "
            "kind the solution and sketches name (a chain-driven slide stays a slide, not a linkage of cylinders), "
            "and draw only what is mounted on or touches the device: a part the solution places elsewhere (an operator "
            "station, control room, charger, base station, grid) is not drawn on the device; leave it out or show it "
            "clearly apart. Make every flow visible between its stations (how material gets from where it is taken to where "
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
               "no other text, margins, scale bars, envelope or limit boxes, dimension lines or other drawn guides. "
               if callouts else
               "The image carries no text, labels, callouts, margins, scale bars, envelope or limit boxes, dimension "
               "lines or other drawn guides (a size limit is shown by the device's true size beside the scale "
               "object): code adds every label afterwards. ")
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
