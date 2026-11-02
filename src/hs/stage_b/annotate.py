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


def _iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def _drop_conflicting(boxes: dict[str, tuple[float, float, float, float]]) -> set[str]:
    """Two parts localized onto nearly the same box means one of them was
    grounded on the wrong object; its label would point at the other part —
    worse than no label. Drop the smaller claim so it is reported missing
    instead (a real S1 finding the loop can act on). Genuine containment
    (a small part inside a chamber) has low IoU and is kept."""
    dropped: set[str] = set()
    ids = list(boxes)
    for i, pid in enumerate(ids):
        for other in ids[i + 1:]:
            if _iou(boxes[pid], boxes[other]) > 0.5:
                area_pid = (boxes[pid][2] - boxes[pid][0]) * (boxes[pid][3] - boxes[pid][1])
                area_other = (boxes[other][2] - boxes[other][0]) * (boxes[other][3] - boxes[other][1])
                dropped.add(pid if area_pid <= area_other else other)
    return dropped


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
                                               box_1000=Box1000(x0=0, y0=0, x1=10, y1=10)))
                    continue
                parts.append(LocalizedPart(
                    id=node.id, found=True,
                    box_1000=Box1000(x0=box["x0"], y0=box["y0"] / 625 * 1000,
                                     x1=box["x1"], y1=box["y1"] / 625 * 1000)))
            return Localization(parts=parts)
        part_list = "\n".join(f"{n.id}: {n.label}" for n in spec.nodes)
        loc = self.client.structured(
            "localization", Localization,
            "Locate each part on the normalized 0-1000 grid of the exact image sent.",
            f"Parts:\n{part_list}\n\nGround each part in the image next to this message.",
            image_paths=[render_png])
        return loc

    def run(self, render_png: Path, spec: SchematicSpec, geometry: dict[str, Any], out_png: Path,
            panel_letter: str = "A", localization: Localization | None = None) -> tuple[Path, Localization, list[str]]:
        """Label the render for the figure (16a): boxes from SAM when given (the localization call only
        for parts SAM did not find), labels drawn by code inside the frame with a leader to each part."""
        if localization is None:
            loc = self.localize(render_png, spec, geometry)
        else:
            loc = localization
            missing_ids = [p.id for p in loc.parts if not p.found]
            if missing_ids and not getattr(self.client, "is_fake", False):
                subset = spec.model_copy(update={"nodes": [n for n in spec.nodes if n.id in missing_ids]})
                extra = {p.id: p for p in self.localize(render_png, subset, geometry).parts if p.found}
                loc = Localization(parts=[extra.get(p.id, p) for p in loc.parts])
        img = Image.open(render_png).convert("RGB")
        w, h = img.size
        font = _font(max(18, w // 60))
        small = _font(max(14, w // 90))
        boxes_px: dict[str, tuple[float, float, float, float]] = {}
        for part in loc.parts:
            if not part.found:
                continue
            b = part.box_1000
            boxes_px[part.id] = (min(max(b.x0 / 1000 * w, 0), w), min(max(b.y0 / 1000 * h, 0), h),
                                 min(max(b.x1 / 1000 * w, 0), w), min(max(b.y1 / 1000 * h, 0), h))
        for pid in _drop_conflicting(boxes_px):
            boxes_px.pop(pid, None)
            for part in loc.parts:
                if part.id == pid:
                    part.found = False
        (out_png.parent / "localization.json").write_text(loc.model_dump_json(indent=2), encoding="utf-8")
        label_of = {n.id: n.label for n in spec.nodes}
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        placed: list[tuple[float, float, float, float]] = []
        fs = font.size  # type: ignore[attr-defined]
        for pid, (x0, y0, x1, y1) in sorted(boxes_px.items(), key=lambda kv: kv[1][1]):
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            text = label_of.get(pid, pid)
            tw = draw.textlength(text, font=font)
            lx = min(max(cx - tw / 2, 8), w - tw - 8)
            ly = y0 - fs - 18 if y0 - fs - 18 > 8 else min(y1 + 12, h - fs - 12)
            for _ in range(40):  # step away from labels already placed
                rect = (lx - 6, ly - 4, lx + tw + 6, ly + fs + 6)
                if not any(not (rect[2] < r[0] or rect[0] > r[2] or rect[3] < r[1] or rect[1] > r[3]) for r in placed):
                    break
                ly = ly + fs + 10 if ly + 2 * fs + 20 < h else max(ly - 3 * fs, 8)
            rect = (lx - 6, ly - 4, lx + tw + 6, ly + fs + 6)
            placed.append(rect)
            anchor_y = rect[3] if rect[3] <= cy else rect[1]
            draw.line([lx + tw / 2, anchor_y, cx, cy], fill=(0, 80, 80, 255), width=max(2, w // 600))
            draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(0, 80, 80, 255))
            draw.rounded_rectangle(rect, radius=6, fill=(255, 255, 255, 225))
            draw.text((lx, ly), text, fill=(0, 60, 60, 255), font=font)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        missing = [p.id for p in loc.parts if not p.found]
        crit = next((n for n in spec.nodes if n.id == spec.critical_part_id), None)
        if crit is not None and spec.critical_part_id in boxes_px:
            cx0, _, cx1, _ = boxes_px[spec.critical_part_id]
            gm = math.sqrt(max(crit.size_class_mm.min, 0.01) * max(crit.size_class_mm.max, 0.01))
            bar_px = spec.scale_bar_mm * max((cx1 - cx0) / gm, 0.01)
            if 10 < bar_px < w / 2:
                bx, by = 20, h - 40
                draw.rectangle([bx - 8, by - small.size - 14, bx + bar_px + 8, by + 10], fill=(255, 255, 255))  # type: ignore[attr-defined]
                draw.line([bx, by, bx + bar_px, by], fill=(0, 80, 80), width=4)
                draw.text((bx, by - small.size - 8), f"~{spec.scale_bar_mm:g} mm", fill=(0, 80, 80), font=small)  # type: ignore[attr-defined]
        draw.text((12, 8), panel_letter, fill=(0, 0, 0), font=font)
        out_png.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_png)
        return out_png, loc, missing
