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
              labeled_png: Path, archive: ImageArchive, corrections: str = "") -> VLMPrompt:
        prompt = (
            f"SOLUTION:\n{solution.model_dump_json(indent=2)}\n\n"
            f"PREFERRED VIEW: {solution.figure_spec.preferred_view}\n\n"
            f"IMAGE ARCHIVE SUMMARY:\n{archive.summary_text()}\n\n"
            "Write the image prompt plus a structured visual plan: view; spatial layout; "
            "operating moment (the device in its operating moment, workpiece/sample present); "
            "force/motion/signal transfer path; 4-7 focus parts each with material and purpose; real "
            "interactions between the parts; an avoid list. The focus parts MUST include the critical part "
            "and its direct sketch neighbours, and every focus part must be visibly drawn (not hidden inside "
            "another part). Show fixed vs moving parts and the force/signal path. Keep the parts, their "
            "connections and relative sizes of the reference; perspective may differ. The image carries no "
            "text at all: code adds every label afterwards.\n\n"
            + (f"TARGETED CORRECTIONS FROM ACTUAL-IMAGE REVIEW (apply verbatim):\n{corrections}\n" if corrections else "")
        )
        vlm = self.client.structured("vlm_writer", VLMPrompt,
                                     "You are the VLM prompt writer for a technical illustration.",
                                     prompt, image_paths=[schematic_png, labeled_png])
        return VLMPrompt(prompt=vlm.prompt, must_not=list(vlm.must_not),
                         changes_from_previous=vlm.changes_from_previous,
                         visual_plan=vlm.visual_plan, focus_parts=vlm.focus_parts)
