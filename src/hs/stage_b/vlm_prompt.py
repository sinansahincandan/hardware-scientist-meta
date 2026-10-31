"""VLM prompt writer (spec §5.2 as amended by AUTOPILOT §7.1-2, SPEC-1/2).

The image model may draw brief callouts for the 4-7 focus parts. After two
label failures the controller forces label_mode="code" (clean render +
code-drawn overlay in Annotator).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hs.schemas import SchematicSpec, SolutionPrompt, VLMPrompt
from hs.stage_b.image_archive import ImageArchive

CLEAN_MUST_NOT = "No text, no labels, no numbers, no arrows, no logos, no watermarks."


class VLMPromptWriter:
    def __init__(self, client: Any) -> None:
        self.client = client

    def write(self, solution: SolutionPrompt, spec: SchematicSpec, schematic_png: Path,
              labeled_png: Path, archive: ImageArchive, s1_differences: str = "",
              corrections: str = "", force_code_labels: bool = False) -> VLMPrompt:
        summary = archive.summary_text()
        corr = corrections or s1_differences
        prompt = (
            f"SOLUTION:\n{solution.model_dump_json(indent=2)}\n\n"
            f"PREFERRED VIEW: {solution.figure_spec.preferred_view}\n\n"
            f"IMAGE ARCHIVE SUMMARY:\n{summary}\n\n"
            "Write the image prompt plus a structured visual plan: view; spatial layout; "
            "operating moment (the device in its operating moment, workpiece/sample present); "
            "force/motion/signal transfer path; 4-7 focus parts each with material, purpose and a "
            "brief callout (part name only, spelled exactly as in the schematic labels); real "
            "interactions between the parts; an avoid list. Show fixed vs moving parts and the "
            "force/signal path. Light background, realistic rendered product-style illustration. "
            "The image model draws the brief callouts itself with leader lines; keep them short. "
            "Keep the parts, their connections and relative sizes of the reference; perspective may differ.\n\n"
            + (f"TARGETED CORRECTIONS FROM ACTUAL-IMAGE REVIEW (apply verbatim):\n{corr}\n" if corr else "")
            + ("LABEL MODE: code — do NOT draw any text; code will add labels afterwards.\n"
               if force_code_labels else "LABEL MODE: image — draw the focus-part callouts in the image.\n")
        )
        vlm = self.client.structured("vlm_writer", VLMPrompt,
                                     "You are the VLM prompt writer for a technical illustration.",
                                     prompt, image_paths=[schematic_png, labeled_png])
        if force_code_labels:
            must_not = list(vlm.must_not) + [CLEAN_MUST_NOT]
            return VLMPrompt(prompt=vlm.prompt, must_not=must_not,
                             changes_from_previous=vlm.changes_from_previous,
                             visual_plan=vlm.visual_plan, focus_parts=vlm.focus_parts,
                             label_mode="code")
        return VLMPrompt(prompt=vlm.prompt, must_not=list(vlm.must_not),
                         changes_from_previous=vlm.changes_from_previous,
                         visual_plan=vlm.visual_plan, focus_parts=vlm.focus_parts,
                         label_mode="image")
