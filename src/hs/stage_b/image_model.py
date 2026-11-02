"""Image model wrapper (spec §5.3). Pixels only — no text in the output."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hs.schemas import VLMPrompt


class ImageModel:
    def __init__(self, client: Any) -> None:
        self.client = client

    def edit(self, vlm: VLMPrompt, reference_png: Path, size: str = "1536x1024",
             council_sketches: list[Path] | None = None) -> bytes:
        prompt = vlm.prompt + " " + " ".join(vlm.must_not)
        if council_sketches:
            prompt += (" The first reference image is the mechanism sketch to follow; the further reference "
                       "images are the engineers' own hand sketches of how the mechanism works.")
        return self.client.image_edit(prompt, Path(reference_png), size=size, extra_refs=council_sketches)
