"""Annotate: localization call + Pillow overlay + scale bar (spec §5.4). All words drawn by code."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


def _font(size: int):  # readable labels at any image size; default bitmap font is not
    for name in ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:  # noqa: S112 — missing font file: try the next candidate
            continue
    return ImageFont.load_default()

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
            out_png: Path, panel_letter: str = "A", code_labels: bool = True) -> tuple[Path, Localization, list[str]]:
        loc = self.localize(render_png, spec, geometry)
        (out_png.parent / "localization.json").write_text(loc.model_dump_json(indent=2), encoding="utf-8")
        img = Image.open(render_png).convert("RGB")
        w, h = img.size
        draw = ImageDraw.Draw(img)
        font = _font(max(16, w // 64))
        small = _font(max(13, w // 90))
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
        if code_labels and boxes_px:
            # White side margins: labels stacked without overlap, leader lines
            # to box centres (co-located hub parts no longer collide).
            pad = max(300, w // 3)
            canvas = Image.new("RGB", (w + 2 * pad, h), "white")
            canvas.paste(img, (pad, 0))
            img = canvas
            boxes_px = {k: (x0 + pad, y0, x1 + pad, y1) for k, (x0, y0, x1, y1) in boxes_px.items()}
            w, h = img.size
            draw = ImageDraw.Draw(img)
            items = sorted(boxes_px.items(), key=lambda kv: (kv[1][1] + kv[1][3]) / 2)
            next_y = {"left": 16.0, "right": 16.0}
            for pid, (x0, y0, x1, y1) in items:
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                text = label_of.get(pid, pid)
                tw = draw.textlength(text, font=font)
                side = "left" if cx < w / 2 else "right"
                ly = max(next_y[side], min(cy, h - 40))
                next_y[side] = ly + font.size + 10  # type: ignore[attr-defined]
                lx = 10 if side == "left" else w - tw - 10
                edge_x = lx + tw + 6 if side == "left" else lx - 6
                draw.rectangle([lx - 4, ly - 3, lx + tw + 4, ly + font.size + 5], fill=(255, 255, 255))  # type: ignore[attr-defined]
                draw.line([edge_x, ly + font.size / 2, cx, cy], fill=(0, 90, 90), width=3)  # type: ignore[attr-defined]
                draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(0, 90, 90))
                draw.text((lx, ly), text, fill=(0, 70, 70), font=font)
        # load arrows (letters from schematic loads; code mode only)
        node_box = boxes_px
        for load in spec.loads if code_labels else []:
            box = node_box.get(load.on_id)
            if box is None:
                continue
            x0, y0, x1, y1 = box
            cx = (x0 + x1) / 2
            draw.line([cx, y0 - 30, cx, y0], fill=(200, 0, 0), width=3)
            draw.polygon([(cx - 5, y0), (cx + 5, y0), (cx, y0 + 8)], fill=(200, 0, 0))
            draw.text((cx + 6, y0 - 30), load.label, fill=(200, 0, 0), font=font)
        # scale bar from critical part
        missing = [p.id for p in loc.parts if not p.found]
        crit = next((n for n in spec.nodes if n.id == spec.critical_part_id), None)
        if crit is not None and spec.critical_part_id in boxes_px:
            cx0, _, cx1, _ = boxes_px[spec.critical_part_id]
            gm = math.sqrt(max(crit.size_class_mm.min, 0.01) * max(crit.size_class_mm.max, 0.01))
            px_per_mm = max((cx1 - cx0) / gm, 0.01)
            bar_px = spec.scale_bar_mm * px_per_mm
            bx, by = 20, h - 64
            draw.line([bx, by, bx + bar_px, by], fill=(0, 90, 90), width=4)
            draw.text((bx, by + 6), f"~{spec.scale_bar_mm:g} mm", fill=(0, 90, 90), font=small)
        draw.text((12, 10), panel_letter, fill=(0, 0, 0), font=font)
        footer = "Conceptual illustration - physical performance not established"
        draw.rectangle([0, h - (small.size + 10), w, h], fill=(255, 255, 255))  # type: ignore[attr-defined]
        draw.text((12, h - (small.size + 6)), footer, fill=(60, 60, 60), font=small)  # type: ignore[attr-defined]
        out_png.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_png)
        return out_png, loc, missing
