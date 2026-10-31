"""VLM prompt writer (spec §5.2). Code always appends the no-text rule."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hs.schemas import SchematicSpec, SolutionPrompt, VLMPrompt
from hs.stage_b.image_archive import ImageArchive

FORCED_MUST_NOT = "No text, no labels, no numbers, no arrows, no logos, no watermarks."


class VLMPromptWriter:
    def __init__(self, client: Any) -> None:
        self.client = client

    def write(self, solution: SolutionPrompt, spec: SchematicSpec, schematic_png: Path,
              labeled_png: Path, archive: ImageArchive, s1_differences: str = "") -> VLMPrompt:
        summary = archive.summary_text()
        prompt = (
            f"SOLUTION:\n{solution.model_dump_json(indent=2)}\n\n"
            f"PREFERRED VIEW: {solution.figure_spec.preferred_view}\n\n"
            f"IMAGE ARCHIVE SUMMARY:\n{summary}\n\n"
            f"S1 DIFFERENCES TO FIX:\n{s1_differences}\n\n"
            "Write the image prompt: materials, finish, view, lighting. Clean technical illustration "
            "on white; keep the parts, their connections and relative sizes of the reference; "
            "perspective may differ from the reference."
        )
        vlm = self.client.structured("vlm_writer", VLMPrompt,
                                     "You are the VLM prompt writer for a technical illustration.",
                                     prompt, image_paths=[schematic_png, labeled_png])
        must_not = list(vlm.must_not) + [FORCED_MUST_NOT]
        return VLMPrompt(prompt=vlm.prompt, must_not=must_not,
                         changes_from_previous=vlm.changes_from_previous)
