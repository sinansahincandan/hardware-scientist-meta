"""VLM prompt gradient + local edit + progress check (spec §5.5b)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageFilter

from hs.schemas import DesignerEval, ProgressCheck, VLMPrompt, VLMPromptGradient


class VLMPromptGradientRunner:
    def __init__(self, client: Any) -> None:
        self.client = client

    def run(self, render_png: Path, labeled_png: Path, vlm: VLMPrompt, ev: DesignerEval) -> VLMPromptGradient:
        regions = "\n".join(
            f"- region part={r.part_id} box={r.box} source={r.source}: observed={r.observed} | expected={r.expected}"
            for r in ev.regions) or "(no regions; use the written differences)"
        prompt = (
            "You are the VLM prompt gradient. The designer evaluation regions below are the output "
            "gradient. For EACH region, write a diagnosis: which sentence of the VLM prompt caused "
            "this depiction fault, or what the prompt is missing, and the exact prompt fix. Then set "
            "fix_mode: 'local' when the fixes touch one part/region at a time, 'full' when the fix "
            "spans several parts and the whole image must be regenerated.\n\n"
            f"VLM PROMPT:\n{vlm.prompt}\nMUST NOT: {vlm.must_not}\n\nREGIONS:\n{regions}\n\n"
            f"WRITTEN DIFFERENCES:\n{ev.s1_differences}\n"
        )
        return self.client.structured("vlm_prompt_gradient", VLMPromptGradient,
                                      "You diagnose which VLM-prompt sentence caused each depiction fault.",
                                      prompt, image_paths=[render_png, labeled_png])

    def progress_check(self, annotated_png: Path, ev_before: DesignerEval, fix_notes: str) -> ProgressCheck:
        regions = "\n".join(
            f"- part={r.part_id} box={r.box}: observed={r.observed} | expected={r.expected}"
            for r in ev_before.regions)
        prompt = (
            "Progress check on the edited render. For the regions below: does the fixed region now "
            "pass (fixed_region_pass)? Do previously passing areas still pass (previous_pass)? Is any "
            "paste seam visible (seam_visible)? Judge from the pixels only, and note that a label "
            "alone never proves a connection.\n\n"
            f"REGIONS BEFORE THE FIX:\n{regions}\n\nFIX APPLIED:\n{fix_notes}\n"
        )
        return self.client.structured("progress_check", ProgressCheck,
                                      "You are the progress-check judge for a locally edited render.",
                                      prompt, image_paths=[annotated_png])


def composite_region(previous_png: Path, edited_png: Path, box_1000: list[float],
                     out_png: Path, margin_px: int = 12, feather_px: int = 6) -> dict[str, Any]:
    """Paste only the region box (feathered) from edited onto previous.

    Returns pixel-assertion results: pixels outside the pasted box must be
    identical to the previous render.
    """
    prev = Image.open(previous_png).convert("RGB")
    edited = Image.open(edited_png).convert("RGB")
    if edited.size != prev.size:
        edited = edited.resize(prev.size)
    w, h = prev.size
    x0 = int(max(box_1000[0], 0) / 1000 * w) - margin_px
    y0 = int(max(box_1000[1], 0) / 1000 * h) - margin_px
    x1 = int(min(box_1000[2], 1000) / 1000 * w) + margin_px
    y1 = int(min(box_1000[3], 1000) / 1000 * h) + margin_px
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, w), min(y1, h)
    patch = edited.crop((x0, y0, x1, y1))
    mask = Image.new("L", patch.size, 255)
    if feather_px > 0:
        # Feather only the border: shrink the solid core, blur the rim.
        core = Image.new("L", patch.size, 0)
        from PIL import ImageDraw

        ImageDraw.Draw(core).rectangle(
            [feather_px, feather_px, patch.size[0] - feather_px, patch.size[1] - feather_px], fill=255)
        mask = core.filter(ImageFilter.GaussianBlur(feather_px / 2))
    result = prev.copy()
    result.paste(patch, (x0, y0), mask)
    # Assertion: outside the pasted box every pixel is unchanged.
    outside_ok = True
    rp, pp = result.load(), prev.load()
    for yy in range(0, h, 7):
        for xx in range(0, w, 7):
            if not (x0 <= xx < x1 and y0 <= yy < y1) and rp[xx, yy] != pp[xx, yy]:
                outside_ok = False
    out_png.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_png)
    return {"outside_unchanged": outside_ok, "box_px": [x0, y0, x1, y1]}
