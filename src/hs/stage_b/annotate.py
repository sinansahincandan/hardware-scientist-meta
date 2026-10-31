"""Annotate: localization call + Pillow overlay + scale bar (spec §5.4). All words drawn by code."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from hs.schemas import Box1000, Localization, LocalizedPart, SchematicSpec


class Annotator:
    def __init__(self, client: Any) -> None:
        self.client = client

    def localize(self, render_png: Path, spec: SchematicSpec, geometry: dict[str, Any]) -> Localization:
        if getattr(self.client, "is_fake", False):
            self.client.record_fake("localization")
            # geometry boxes are in 1000x625 px; convert to the 0-1000 grid:
            parts: list[LocalizedPart] = []
            for node in spec.nodes:
                box = geometry.get("boxes", {}).get(node.id)
                if box is None:
                    parts.append(LocalizedPart(id=node.id, found=False,
                                               box_1000=Box1000(x0=0, y0=0, x1=10, y1=10), confidence=0.0))
                    continue
                parts.append(LocalizedPart(
                    id=node.id, found=True,
                    box_1000=Box1000(x0=box["x0"], y0=box["y0"] / 625 * 1000,
                                     x1=box["x1"], y1=box["y1"] / 625 * 1000),
                    confidence=0.9))
            return Localization(parts=parts)
        part_list = "\n".join(f"{n.id}: {n.label}" for n in spec.nodes)
        loc = self.client.structured(
            "localization", Localization,
            "Locate each part on the normalized 0-1000 grid of the exact image sent.",
            f"Parts:\n{part_list}\n\nGround each part in the image next to this message.",
            image_paths=[render_png])
        return loc

    def run(self, render_png: Path, spec: SchematicSpec, geometry: dict[str, Any],
            out_png: Path, panel_letter: str = "A") -> tuple[Path, Localization, list[str]]:
        loc = self.localize(render_png, spec, geometry)
        (out_png.parent / "localization.json").write_text(loc.model_dump_json(indent=2), encoding="utf-8")
        img = Image.open(render_png).convert("RGB")
        w, h = img.size
        draw = ImageDraw.Draw(img)
        boxes_px: dict[str, tuple[float, float, float, float]] = {}
        for part in loc.parts:
            if not part.found:
                continue
            b = part.box_1000
            x0 = min(max(b.x0 / 1000 * w, 0), w)
            y0 = min(max(b.y0 / 1000 * h, 0), h)
            x1 = min(max(b.x1 / 1000 * w, 0), w)
            y1 = min(max(b.y1 / 1000 * h, 0), h)
            boxes_px[part.id] = (x0, y0, x1, y1)
        label_of = {n.id: n.label for n in spec.nodes}
        # labels with leader lines, placed above each box (collision-avoided by index offset)
        for i, (pid, (x0, y0, x1, y1)) in enumerate(sorted(boxes_px.items())):
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            lx = min(max(cx, 60), w - 60)
            ly = max(14 + (i % 3) * 16, y0 - 24)
            draw.line([cx, cy, lx, ly], fill=(0, 90, 90), width=2)
            draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(0, 90, 90))
            draw.text((lx, ly), label_of.get(pid, pid), fill=(0, 90, 90))
        # load arrows (letters from schematic loads)
        node_box = boxes_px
        for load in spec.loads:
            box = node_box.get(load.on_id)
            if box is None:
                continue
            x0, y0, x1, y1 = box
            cx = (x0 + x1) / 2
            draw.line([cx, y0 - 30, cx, y0], fill=(200, 0, 0), width=3)
            draw.polygon([(cx - 5, y0), (cx + 5, y0), (cx, y0 + 8)], fill=(200, 0, 0))
            draw.text((cx + 6, y0 - 30), load.label, fill=(200, 0, 0))
        # scale bar from critical part
        missing = [p.id for p in loc.parts if not p.found]
        crit = next((n for n in spec.nodes if n.id == spec.critical_part_id), None)
        if crit is not None and spec.critical_part_id in boxes_px:
            cx0, _, cx1, _ = boxes_px[spec.critical_part_id]
            gm = math.sqrt(max(crit.size_class_mm.min, 0.01) * max(crit.size_class_mm.max, 0.01))
            px_per_mm = max((cx1 - cx0) / gm, 0.01)
            bar_px = spec.scale_bar_mm * px_per_mm
            bx, by = 20, h - 30
            draw.line([bx, by, bx + bar_px, by], fill=(0, 90, 90), width=4)
            draw.text((bx, by + 6), f"~{spec.scale_bar_mm:g} mm", fill=(0, 90, 90))
        draw.text((12, 10), panel_letter, fill=(0, 0, 0))
        out_png.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_png)
        return out_png, loc, missing
