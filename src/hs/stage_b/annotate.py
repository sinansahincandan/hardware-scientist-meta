"""Annotate: localization call + Pillow overlay + scale bar (spec §5.4). All words drawn by code."""
from __future__ import annotations

import json
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


def nice_scale_mm(size_mm: float) -> float:
    """A round scale-bar length (1, 2 or 5 x 10^n mm) no longer than the critical part's own size."""
    import math as _m

    exp = 10 ** _m.floor(_m.log10(max(size_mm, 0.01)))
    return max(m * exp for m in (1, 2, 5) if m * exp <= max(size_mm, exp))


def px_per_mm(spec: SchematicSpec, boxes_px: dict[str, tuple[float, float, float, float]],
              reference: float = 0.0) -> tuple[float, float]:
    """Picture scale: for every located part, its longer box side over its largest stated size; the median of those
    estimates. One part alone misleads (a pillar boxed as a whole array, a solar array only partly boxed).
    Returns (pixels per mm, the largest located part's size in mm), or (0, 0) when no part is located."""
    est: list[float] = []
    largest = 0.0
    for n in spec.nodes:
        if n.id in boxes_px and n.size_class_mm.max > 0:
            x0, y0, x1, y1 = boxes_px[n.id]
            est.append(max(x1 - x0, y1 - y0) / n.size_class_mm.max)
            largest = max(largest, n.size_class_mm.max)
    if reference > 0:  # a hand or person of known size in the picture outranks the parts' own stated sizes
        return reference, largest
    if not est:
        return 0.0, 0.0
    est.sort()
    return est[len(est) // 2], largest


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

    def check_labels(self, image_png: Path, labels: list[str]) -> list[str]:
        """One look at a labelled image: which of these labels point at the wrong part or are misspelled?"""
        from hs.schemas import LabelCheck

        if not labels:
            return []
        check = self.client.structured(
            "light_check", LabelCheck, "You check labels and callouts on a product photo.",
            "Each label below appears in the image with a leader line ending on a part. List, exactly as written "
            "below, every label whose leader ends on a part that is NOT what the label names, or that is "
            "misspelled or unreadable in the image. Judge from the pixels.\nLABELS: " + "; ".join(labels),
            image_paths=[image_png])
        return [x for x in check.wrong_labels if x in labels]

    def run(self, render_png: Path, spec: SchematicSpec, geometry: dict[str, Any], out_png: Path,
            panel_letter: str = "A", localization: Localization | None = None,
            fallback: bool = True, draw_labels: bool = True) -> tuple[Path, Localization, list[str]]:
        """Label the render for the figure (16a): boxes from SAM when given (the localization call only
        for parts SAM did not find), labels drawn by code inside the frame with a leader to each part."""
        if localization is None:
            loc = self.localize(render_png, spec, geometry)
        else:
            loc = localization.model_copy(deep=True)  # never change the caller's record (panel B and markers use it)
            missing_ids = [p.id for p in loc.parts if not p.found]
            if fallback and missing_ids and not getattr(self.client, "is_fake", False):
                subset = spec.model_copy(update={"nodes": [n for n in spec.nodes if n.id in missing_ids]})
                extra = {p.id: p for p in self.localize(render_png, subset, geometry).parts if p.found}
                loc = Localization(parts=[extra.get(p.id, p) for p in loc.parts], px_per_mm=loc.px_per_mm)
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
        # written as located: a refigure reads it back, and parts dropped below only for labelling were lost from
        # it on every redraw (run 170523 lost its critical part and panel B)
        (out_png.parent / "localization.json").write_text(loc.model_dump_json(indent=2), encoding="utf-8")
        for pid in _drop_conflicting(boxes_px):  # overlapping boxes: label one of them only
            boxes_px.pop(pid, None)
            for part in loc.parts:
                if part.id == pid:
                    part.found = False
        label_of = {n.id: n.label for n in spec.nodes}
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        fs = font.size  # type: ignore[attr-defined]
        # Callout layout: labels in a left and a right column (the side nearest each part), ordered top to
        # bottom by the part's height, so leaders run sideways and never cross another label.
        items = [(pid, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2) for pid, b in boxes_px.items()] if draw_labels else []
        pad, gap = 10, 12
        label_rects: list[list[float]] = []
        for side in ("left", "right"):
            col = sorted([it for it in items if (it[1] < w / 2) == (side == "left")], key=lambda it: it[2])
            next_top = 8.0
            for pid, cx, cy in col:
                text = label_of.get(pid, pid)
                tw = draw.textlength(text, font=font)
                lx = 16 if side == "left" else w - tw - 16
                floor = h - fs - (2 * fs + 50 if side == "left" else 16)  # the scale bar sits bottom-left
                ly = min(max(cy - fs / 2, next_top), floor)
                below = (lx - 6 < cx < lx + tw + 6) and (ly - 4 < cy < ly + fs + 6)  # the label would hide its part
                if below:
                    ly = min(max(cy + 2 * fs, next_top), floor)
                next_top = ly + fs + pad + gap
                rect = (lx - 6, ly - 4, lx + tw + 6, ly + fs + 6)
                label_rects.append([*rect])
                ax, ay = (rect[2] if side == "left" else rect[0]), (rect[1] + rect[3]) / 2
                if below:
                    ax, ay = min(max(cx, rect[0] + 12), rect[2] - 12), rect[1]
                draw.line([ax, ay, cx, cy], fill=(0, 80, 80, 255), width=max(2, w // 600))
                draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(0, 80, 80, 255), outline=(255, 255, 255, 255))
                # the leader's end dot is kept clear too: a step marker on it hid which part a label names
                # (run 152604: the hopper's dot under marker 4, its leader seemed to end on the mast)
                label_rects.append([cx - 10, cy - 10, cx + 10, cy + 10])
                draw.rounded_rectangle(rect, radius=6, fill=(255, 255, 255, 232), outline=(0, 80, 80, 255))
                draw.text((lx, ly), text, fill=(0, 60, 60, 255), font=font)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        missing = [p.id for p in loc.parts if not p.found]
        ppm, ref_mm = px_per_mm(spec, boxes_px, loc.px_per_mm)
        if ppm > 0:
            bar_mm = nice_scale_mm(ref_mm / 3)  # a round length about a third of the largest part
            bar_px = bar_mm * ppm
            if 10 < bar_px < w / 2:
                bx, by = 20, h - 40
                draw.rectangle([bx - 8, by - small.size - 14, bx + bar_px + 8, by + 10], fill=(255, 255, 255))  # type: ignore[attr-defined]
                draw.line([bx, by, bx + bar_px, by], fill=(0, 80, 80), width=4)
                draw.text((bx, by - small.size - 8), f"~{bar_mm:g} mm", fill=(0, 80, 80), font=small)  # type: ignore[attr-defined]
        draw.text((12, 8), panel_letter, fill=(0, 0, 0), font=font)
        out_png.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_png)
        out_png.with_suffix(".labels.json").write_text(json.dumps(label_rects), encoding="utf-8")  # for the step markers
        return out_png, loc, missing
