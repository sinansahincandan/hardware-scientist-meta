"""SAM part map (round-3 item 16): SAM finds each part, code measures it against an expectation
table derived from the design, and the differences go to the critic as text evidence, never as a
verdict. Masks are not decodable in this session (BLOCKED.md), so measurements use SAM's boxes.

- build_part_map: one LLM call turns each part into a plain visual phrase ("black rubber wheel") and a
  coarse expectation (count, long axis, size against a neighbour, touching parts).
- measure: one sam-3.1 call per part on the unlabeled render; boxes in render pixels.
- differences / recheck: plain sentences comparing measurement with expectation, and with the previous
  round (fixed, still different, moved), so earlier faults cannot come back quietly.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from PIL import Image

from hs.schemas import Box1000, Localization, LocalizedPart, PartMap, SchematicSpec, SolutionPrompt

_BOX = re.compile(r"<\|box;x1=(-?\d+);y1=(-?\d+);x2=(-?\d+);y2=(-?\d+);w=(\d+);h=(\d+)(?:;[^|]*)?\|>")


def build_part_map(client: Any, solution: SolutionPrompt, spec: SchematicSpec, out_dir: Path) -> PartMap:
    parts = "\n".join(f"- {n.id}: {n.label}" for n in spec.nodes)
    part_map = client.structured(
        "part_map", PartMap,
        "You prepare a part map for an image segmenter and an expectation table for checking a render.",
        "For each part below write: visual_phrase — at most four plain words a person would use to point at "
        "it in a photo, by colour, material and shape (for example 'black rubber wheel', 'steel tube frame'); "
        "never an engineering name or an id. Then, from the design (which has the numbers), the coarse "
        "expectation: count (how many instances are visible in a normal view), long_axis (horizontal, "
        "vertical or any, as the part would appear in a side view of the working device), size_vs (the "
        "neighbouring part it is best compared with) and size_ratio (its longest dimension divided by that "
        "neighbour's), touches (ids of the parts it physically touches), and a one-line note.\n\n"
        f"PARTS:\n{parts}\n\nDESIGN:\n{solution.model_dump_json(indent=2)}")
    (out_dir / "part_map.json").write_text(part_map.model_dump_json(indent=2), encoding="utf-8")
    return part_map


def parse_sam(raw: str, img_w: int, img_h: int) -> list[tuple[float, float, float, float]]:
    """Boxes from SAM's record text, scaled to the render's pixel size (half-open right/bottom)."""
    boxes: list[tuple[float, float, float, float]] = []
    for m in _BOX.finditer(raw or ""):
        x1, y1, x2, y2, w, h = (int(v) for v in m.groups())
        sx, sy = img_w / max(w, 1), img_h / max(h, 1)
        boxes.append((x1 * sx, y1 * sy, (x2 + 1) * sx, (y2 + 1) * sy))
    return boxes


def measure(client: Any, render_png: Path, part_map: PartMap) -> dict[str, Any]:
    """One SAM call per part; returns {"size": [w, h], "parts": {id: {"phrase", "boxes"}}}."""
    with Image.open(render_png) as im:
        w, h = im.size
    out: dict[str, Any] = {"size": [w, h], "parts": {}}
    for part in part_map.parts:
        raw = client.sam_segment(part.visual_phrase, render_png)
        out["parts"][part.part_id] = {"phrase": part.visual_phrase, "boxes": parse_sam(raw, w, h)}
    return out


def _gap(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    dx = max(0.0, max(a[0], b[0]) - min(a[2], b[2]))
    dy = max(0.0, max(a[1], b[1]) - min(a[3], b[3]))
    return math.hypot(dx, dy)


def _axis(box: tuple[float, ...]) -> str:
    bw, bh = box[2] - box[0], box[3] - box[1]
    if bw >= 1.3 * bh:
        return "horizontal"
    if bh >= 1.3 * bw:
        return "vertical"
    return "any"


def _main(boxes: list[Any]) -> tuple[float, ...] | None:
    return max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1])) if boxes else None


def differences(meas: dict[str, Any], part_map: PartMap) -> dict[str, list[str]]:
    """Per part, the measured differences from the expectation (coarse: about x2 in size, axis only)."""
    w, h = meas["size"]
    near = 0.03 * math.hypot(w, h)
    by = meas["parts"]
    diffs: dict[str, list[str]] = {}
    for part in part_map.parts:
        found = by.get(part.part_id, {}).get("boxes", [])
        notes: list[str] = []
        main = _main(found)
        if main is None:
            notes.append(f"not found by the segmenter as '{part.visual_phrase}'")
        else:
            if part.count and len(found) != part.count:
                notes.append(f"expected {part.count} visible, found {len(found)}")
            if part.long_axis in ("horizontal", "vertical") and _axis(main) not in (part.long_axis, "any"):
                notes.append(f"expected a {part.long_axis} long axis, measured {_axis(main)}")
            ref = _main(by.get(part.size_vs, {}).get("boxes", []))
            if ref is not None and part.size_ratio > 0:
                ratio = max(main[2] - main[0], main[3] - main[1]) / max(ref[2] - ref[0], ref[3] - ref[1], 1e-6)
                if not 0.5 <= ratio / part.size_ratio <= 2.0:
                    notes.append(f"size against {part.size_vs}: expected about {part.size_ratio:.2g} times, "
                                 f"measured {ratio:.2g} times")
            for other in part.touches:
                ob = by.get(other, {}).get("boxes", [])
                if ob and min(_gap(b, o) for b in found for o in ob) > near:
                    notes.append(f"expected to touch {other}, but they are apart in the picture")
        if notes:
            diffs[part.part_id] = notes
    return diffs


def recheck(meas: dict[str, Any], diffs: dict[str, list[str]], previous: dict[str, Any] | None) -> list[str]:
    """Cross-round re-measure (16c): earlier differences re-measured, untouched parts against their
    previous boxes, so a fault cannot quietly come back."""
    if not previous:
        return []
    lines: list[str] = []
    w, h = meas["size"]
    for pid, old_notes in (previous.get("differences") or {}).items():
        now = diffs.get(pid)
        lines.append(f"{pid}: last round {'; '.join(old_notes)} -> now "
                     + ("; ".join(now) if now else "matches the expectation"))
    for pid, rec in meas["parts"].items():
        if pid in (previous.get("differences") or {}) or pid in diffs:
            continue
        old_main = _main((previous.get("parts") or {}).get(pid, {}).get("boxes", []))
        new_main = _main(rec["boxes"])
        if old_main and new_main:
            shift = math.hypot((new_main[0] + new_main[2] - old_main[0] - old_main[2]) / 2,
                               (new_main[1] + new_main[3] - old_main[1] - old_main[3]) / 2)
            if shift > 0.15 * math.hypot(w, h):
                lines.append(f"{pid}: matched before and still matches, but moved in the picture")
        elif old_main and not new_main:
            lines.append(f"{pid}: found last round, not found now")
    return lines


def evidence_text(diffs: dict[str, list[str]], rechecks: list[str], part_map: PartMap) -> str:
    names = {p.part_id: p.visual_phrase for p in part_map.parts}
    lines = [("Segmenter measurements of the render (evidence, not a verdict; coarse: about x2 in size, "
              "long axis only):")]
    lines += [f"- {pid} ('{names.get(pid, pid)}'): {'; '.join(n)}" for pid, n in diffs.items()] or \
        ["- every part was found and matched its expected count, axis, size and contacts"]
    if rechecks:
        lines.append("Compared with the previous round:")
        lines += [f"- {r}" for r in rechecks]
    return "\n".join(lines)


def to_localization(meas: dict[str, Any], spec: SchematicSpec) -> Localization:
    w, h = meas["size"]
    parts: list[LocalizedPart] = []
    for node in spec.nodes:
        main = _main(meas["parts"].get(node.id, {}).get("boxes", []))
        if main is None:
            parts.append(LocalizedPart(id=node.id, found=False, box_1000=Box1000(x0=0, y0=0, x1=0, y1=0)))
        else:
            parts.append(LocalizedPart(id=node.id, found=True, box_1000=Box1000(
                x0=main[0] / w * 1000, y0=main[1] / h * 1000, x1=main[2] / w * 1000, y1=main[3] / h * 1000)))
    return Localization(parts=parts)


def save_round(out_dir: Path, meas: dict[str, Any], diffs: dict[str, list[str]], rechecks: list[str]) -> None:
    (out_dir / "sam.json").write_text(json.dumps({**meas, "differences": diffs, "rechecks": rechecks},
                                                 indent=2), encoding="utf-8")
