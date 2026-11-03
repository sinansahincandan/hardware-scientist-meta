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

import numpy as np
from PIL import Image

from hs.schemas import (
    Box1000,
    Localization,
    LocalizedPart,
    MaskCheck,
    PartMap,
    RenderParts,
    SchematicSpec,
    SolutionPrompt,
)

_BOX = re.compile(r"<\|box;x1=(-?\d+);y1=(-?\d+);x2=(-?\d+);y2=(-?\d+);w=(\d+);h=(\d+)(?:;[^|]*)?\|>")


def build_part_map(client: Any, solution: SolutionPrompt, spec: SchematicSpec, out_dir: Path) -> PartMap:
    parts = "\n".join(f"- {n.id}: {n.label}" for n in spec.nodes)
    part_map = client.structured(
        "part_map", PartMap,
        "You prepare a part map for an image segmenter and an expectation table for checking a render.",
        "For each part below write: visual_phrase — one to three plain words a person would use to point at "
        "it in a photo: the commonest everyday noun first, with at most one colour or material word (for "
        "example 'solar panel', 'black wheel', 'door', 'metal shelf', 'battery box'); never an engineering "
        "name, a product type or an id. Then, from the design (which has the numbers), the coarse "
        "expectation: count (how many instances a viewer can see and count in one normal view; for parts "
        "present in large numbers, the number likely to be visible, not the total), long_axis (horizontal, "
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


def parse_instances(raw: str, img_w: int, img_h: int) -> list[dict[str, Any]]:
    """Every object SAM returned, in render pixels: box, confidence (when asked for), object id and its own
    boolean mask when decodable (meta-sam-parser, owner-approved 2026-11-02). Fake mode: boxes only."""
    frame = _BOX.search(raw or "")
    if frame is None:
        return []
    fw, fh = int(frame.group(5)), int(frame.group(6))
    sx, sy = img_w / max(fw, 1), img_h / max(fh, 1)
    try:
        import meta_sam_parser as msp

        parser = msp.image_segmentation_format().create_parser()
        parser.push(raw)
        records = parser.finish(msp.CompletedOutcome()).result.records
    except Exception:
        return [{"box": b, "conf": None, "object_id": str(i + 1), "mask": None}
                for i, b in enumerate(parse_sam(raw, img_w, img_h))]
    inst: dict[str, dict[str, Any]] = {}
    for rec in records:
        oid = str(getattr(rec, "object_id", "") or len(inst) + 1)
        if rec.kind == "box":
            inst.setdefault(oid, {"mask": None})
            inst[oid].update(box=(rec.left * sx, rec.top * sy, rec.right * sx, rec.bottom * sy),
                             conf=getattr(rec, "confidence", None), object_id=oid)
        elif rec.kind == "mask":
            try:
                raster = np.frombuffer(msp.decode_mask_to_raster(rec.mask), dtype=np.uint8)
            except Exception:  # noqa: S112 — an undecodable mask leaves that object to its box
                continue
            b = rec.bounds
            small = Image.fromarray((raster.reshape(rec.mask.height, rec.mask.width) * 255).astype(np.uint8))
            x0, y0 = round(b.left * sx), round(b.top * sy)
            x1, y1 = max(round(b.right * sx), x0 + 1), max(round(b.bottom * sy), y0 + 1)
            big = np.asarray(small.resize((x1 - x0, y1 - y0))) > 127
            full = np.zeros((img_h, img_w), dtype=bool)
            full[y0:y0 + big.shape[0], x0:x0 + big.shape[1]] = big[: img_h - y0, : img_w - x0]
            inst.setdefault(oid, {"object_id": oid, "conf": getattr(rec, "confidence", None),
                                  "box": (x0, y0, x1, y1)})["mask"] = full
    kept = [v for v in inst.values() if "box" in v]
    if not kept:  # text the parser does not take (no frame marker): boxes from the token pattern
        return [{"box": b, "conf": None, "object_id": str(i + 1), "mask": None}
                for i, b in enumerate(parse_sam(raw, img_w, img_h))]
    return kept


def parse_masks(raw: str, img_w: int, img_h: int) -> np.ndarray | None:
    """Union of SAM's masks for one phrase as a boolean image in render pixels; None without masks."""
    masks = [i["mask"] for i in parse_instances(raw, img_w, img_h) if i.get("mask") is not None]
    if not masks:
        return None
    union = np.zeros((img_h, img_w), dtype=bool)
    for m in masks:
        union |= m
    return union


def _mask_stats(mask: np.ndarray) -> dict[str, float]:
    """Area, centroid and principal-axis angle (degrees from horizontal, 0–180) of a boolean mask."""
    ys, xs = np.nonzero(mask[::2, ::2])
    if len(xs) < 5:
        return {}
    xs, ys = xs * 2.0, ys * 2.0
    cx, cy = float(xs.mean()), float(ys.mean())
    cov = np.cov(np.vstack([xs - cx, ys - cy]))
    vals, vecs = np.linalg.eigh(cov)
    vx, vy = vecs[:, int(np.argmax(vals))]
    angle = math.degrees(math.atan2(-vy, vx)) % 180.0
    elong = float(math.sqrt(max(vals.max(), 1e-9) / max(vals.min(), 1e-9)))
    return {"area": float(mask.sum()), "cx": cx, "cy": cy, "angle": round(angle, 1), "elongation": round(elong, 2)}


def locate_in_render(client: Any, render_png: Path, part_map: PartMap, spec: SchematicSpec) -> RenderParts:
    """One look at the render (pixels first): for each part, whether it is visible, one to three short phrases
    for how it looks here (colour or material + everyday noun, the segmenter's wording rules) and a rough box.
    The phrases come from this picture, not from the design's vocabulary."""
    labels = {n.id: n.label for n in spec.nodes}
    parts = "\n".join(f"- {p.part_id}: {labels.get(p.part_id, p.part_id)} (first guess: '{p.visual_phrase}')"
                      for p in part_map.parts)
    return client.structured(
        "sam_phrases", RenderParts,
        "You prepare prompts for an image segmenter that finds one concept per short noun phrase.",
        "Look at the picture first. For each part below: visible (can a viewer see it at all); phrases — one to "
        "three alternatives, each a short noun phrase naming ONE object the way it looks in THIS picture: an "
        "everyday noun with at most two attributes such as colour, material or shape ('grey spiked wheel', "
        "'metal hopper', 'black cable', 'tall metal pole'); no plurals, no 'and'/'or', no positions, no "
        "engineering names, no numbers; the first phrase must separate it from similar-looking parts in the picture "
        "(a digging drum and a wheel must not get the same phrase). box_1000: a rough box around the part on a "
        "0-1000 grid, origin top-left.\n\n"
        f"PARTS:\n{parts}", image_paths=[render_png])


def _box_prompt(boxes: dict[str, tuple[float, float, float, float]], w: int, h: int) -> tuple[str, dict[str, str]]:
    """SAM box prompt for up to 16 objects in one call (docs /docs/sam/segmenting), coordinates on the image
    as sent (long side at most 1024 px); returns the text and object id -> part id."""
    s = min(1.0, 1024 / max(w, h))
    sw, sh = round(w * s), round(h * s)
    ids: dict[str, str] = {}
    items = []
    for k, (pid, b) in enumerate(list(boxes.items())[:16], start=1):
        ids[str(k)] = pid
        items.append(f"{k}<|box;x1={round(b[0] / 1000 * sw)};y1={round(b[1] / 1000 * sh)};"
                     f"x2={round(b[2] / 1000 * sw)};y2={round(b[3] / 1000 * sh)};w={sw};h={sh}|>")
    return "<0f>" + ",".join(items), ids


def _crop(render: Image.Image, inst: dict[str, Any]) -> Image.Image:
    """The instance with its mask outlined (or its box when there is no mask), padded, at most 512 px."""
    from PIL import ImageDraw, ImageFilter

    x0, y0, x1, y1 = inst["box"]
    pad = 0.6 * max(x1 - x0, y1 - y0)  # enough surroundings to tell a part from look-alikes nearby
    box = (max(int(x0 - pad), 0), max(int(y0 - pad), 0), min(int(x1 + pad), render.width), min(int(y1 + pad), render.height))
    img = render.copy()
    if inst.get("mask") is not None:
        m = Image.fromarray((inst["mask"] * 255).astype(np.uint8))
        edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
        img.paste((255, 0, 200), (0, 0), edge)
    else:
        ImageDraw.Draw(img).rectangle([x0, y0, x1, y1], outline=(255, 0, 200), width=5)
    out = img.crop(box)
    out.thumbnail((512, 512))
    return out


def _judge(client: Any, render_png: Path, found: dict[str, list[dict[str, Any]]], labels: dict[str, str],
           out_dir: Path | None) -> dict[str, list[str]]:
    """'Checks: SAM + judges' (Fig. 2): one call shows each found object outlined in its own crop and asks whether
    it is the part it was found for. Objects judged to be something else are dropped; returns what they were."""
    import tempfile

    render = Image.open(render_png).convert("RGB")
    crops: list[tuple[str, int, Path]] = []
    tmp = out_dir / "mask_check" if out_dir else Path(tempfile.mkdtemp())
    tmp.mkdir(parents=True, exist_ok=True)
    for pid, insts in found.items():
        for j, inst in enumerate(insts[:4]):
            if len(crops) >= 16:
                break
            path = tmp / f"crop_{len(crops) + 1}.png"
            _crop(render, inst).save(path)
            crops.append((pid, j, path))
    if not crops:
        return {}
    lines = "\n".join(f"crop {k}: should show the {labels.get(pid, pid)}" for k, (pid, _, _) in enumerate(crops, 1))
    check: MaskCheck = client.structured(
        "mask_check", MaskCheck, "You check an image segmenter's output.",
        "Each image below is a crop of one picture of a device; a magenta outline marks what the segmenter found. "
        "For each crop, say whether the outlined thing is the named part of the device (is_part), and if not, what "
        "it is (seen_as). The device's parts are: " + "; ".join(labels.values()) + ". The scene may also hold "
        "things that are not part of the device (ground, load, a bin or container it fills, an object pressing on "
        "or held by it, people, buildings, out-of-focus things in the background); an outline on such a thing is "
        "not the part, even if it looks similar. Judge the outlined object only.\n\n"
        + lines, image_paths=[c[2] for c in crops])
    (tmp / "check.json").write_text(json.dumps({"crops": [f"crop {k}: {pid}" for k, (pid, _, _) in enumerate(crops, 1)],
                                                **check.model_dump()}, indent=2), encoding="utf-8")
    verdict = {it.index: it for it in check.items}
    rejected: dict[str, list[str]] = {}
    for k, (pid, j, _) in sorted(enumerate(crops, 1), key=lambda t: -t[1][1]):
        it = verdict.get(k)
        if it is not None and not it.is_part:
            rejected.setdefault(pid, []).append(it.seen_as or "another part")
            found[pid][j] = {}
    found.update({pid: [i for i in insts if i] for pid, insts in found.items()})
    return rejected


def measure(client: Any, render_png: Path, part_map: PartMap, out_dir: Path | None = None,
            spec: SchematicSpec | None = None) -> dict[str, Any]:
    """SAM per part (Fig. 2 'part map · SAM'): phrases written from this render, tried in turn; parts no phrase
    finds are prompted with their rough box (one call, up to 16 objects); every found object is then checked by a
    judge and misidentified ones are dropped. Boxes always, masks when decodable (sam_masks/<part>.png)."""
    with Image.open(render_png) as im:
        w, h = im.size
    out: dict[str, Any] = {"size": [w, h], "parts": {}}
    seen: dict[str, Any] = {}
    if spec is not None:
        try:
            seen = {p.part_id: p for p in locate_in_render(client, render_png, part_map, spec).parts}
        except NotImplementedError:
            seen = {}
    meta = None if getattr(client, "is_fake", False) else {"include_confidence": "true"}
    found: dict[str, list[dict[str, Any]]] = {}
    for part in part_map.parts:
        rp = seen.get(part.part_id)
        tries = [*(rp.phrases if rp else []), part.visual_phrase]
        head = part.visual_phrase.split()[-1] if len(part.visual_phrase.split()) > 1 else ""
        tries = list(dict.fromkeys(t.strip().lower() for t in [*tries, head] if t and t.strip()))[:4]
        rec: dict[str, Any] = {"phrase": tries[0] if tries else part.visual_phrase, "tried": [], "source": "none"}
        for phrase in tries:
            insts = parse_instances(client.sam_segment(phrase, render_png, metadata=meta), w, h)
            rec["tried"].append(phrase)
            if insts:
                rec.update(phrase=phrase, source="phrase")
                found[part.part_id] = insts
                break
        if rp is not None and not rp.visible:
            rec["visible_to_vlm"] = False
        out["parts"][part.part_id] = rec
    labels = {n.id: n.label for n in spec.nodes} if spec is not None else {}
    try:  # judge the phrase finds; misidentified objects are dropped
        rejected = _judge(client, render_png, found, labels, out_dir)
    except NotImplementedError:
        rejected = {}
    found = {pid: insts for pid, insts in found.items() if insts}
    missing = {pid: (b.x0, b.y0, b.x1, b.y1) for pid, rp in seen.items()
               if pid in out["parts"] and pid not in found and rp.visible and (b := rp.box_1000) is not None
               and b.x1 > b.x0 and b.y1 > b.y0}
    if missing:  # parts no phrase found (or only wrongly): one box-prompt call, then judged the same way
        text, ids = _box_prompt(missing, w, h)
        boxed: dict[str, list[dict[str, Any]]] = {}
        for inst in parse_instances(client.sam_segment(text, render_png, metadata=meta), w, h):
            pid = ids.get(str(inst.get("object_id")))
            if pid:
                boxed.setdefault(pid, []).append(inst)
        try:
            for pid, why in _judge(client, render_png, boxed, labels, out_dir / "box_prompt" if out_dir else None).items():
                rejected.setdefault(pid, []).extend(why)
        except NotImplementedError:
            pass
        for pid, insts in boxed.items():
            if insts:
                found[pid] = insts
                out["parts"][pid].update(source="box prompt", phrase=f"{labels.get(pid, pid)} (box prompt)")
    for pid, rec in out["parts"].items():
        insts = found.get(pid, [])
        rec["boxes"] = [tuple(i["box"]) for i in insts]
        rec["confidence"] = [round(i["conf"], 2) for i in insts if i.get("conf") is not None]
        if pid in rejected:
            rec["rejected_by_judge"] = rejected[pid]
        masks = [i["mask"] for i in insts if i.get("mask") is not None]
        if masks and out_dir is not None:
            union = np.zeros((h, w), dtype=bool)
            for m in masks:
                union |= m
            (out_dir / "sam_masks").mkdir(parents=True, exist_ok=True)
            Image.fromarray((union * 255).astype(np.uint8)).save(out_dir / "sam_masks" / f"{pid}.png")
            rec["mask"] = {"file": f"sam_masks/{pid}.png", **_mask_stats(union)}
    if out_dir is not None:
        out["contacts"] = _mask_contacts(out_dir, list(out["parts"]), w, h)
    return out


def _mask_contacts(out_dir: Path, ids: list[str], w: int, h: int) -> list[list[str]]:
    """Pairs of parts whose masks touch (dilated by ~1 % of the image diagonal), measured at quarter size."""
    from PIL import ImageFilter

    small: dict[str, np.ndarray] = {}
    k = max(3, int(0.01 * math.hypot(w, h) / 4) | 1)
    for pid in ids:
        f = out_dir / "sam_masks" / f"{pid}.png"
        if f.exists():
            im = Image.open(f).resize((max(w // 4, 1), max(h // 4, 1)))
            small[pid] = np.asarray(im.filter(ImageFilter.MaxFilter(k))) > 127
    pairs: list[list[str]] = []
    keys = list(small)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if (small[a] & small[b]).any():
                pairs.append([a, b])
    return pairs


def _gap(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    dx = max(0.0, max(a[0], b[0]) - min(a[2], b[2]))
    dy = max(0.0, max(a[1], b[1]) - min(a[3], b[3]))
    return math.hypot(dx, dy)


def _mask_axis(stats: dict[str, Any]) -> str | None:
    if not stats or stats.get("elongation", 1) < 1.3:
        return None if not stats else "any"
    a = stats["angle"]
    if a < 30 or a > 150:
        return "horizontal"
    if 60 < a < 120:
        return "vertical"
    return f"tilted about {a:.0f} degrees"


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
            measured_axis = _mask_axis(by.get(part.part_id, {}).get("mask", {})) or _axis(main)
            if part.long_axis in ("horizontal", "vertical") and measured_axis not in (part.long_axis, "any"):
                notes.append(f"expected a {part.long_axis} long axis, measured {measured_axis}")
            ref = _main(by.get(part.size_vs, {}).get("boxes", []))
            if ref is not None and part.size_ratio > 0:
                ratio = max(main[2] - main[0], main[3] - main[1]) / max(ref[2] - ref[0], ref[3] - ref[1], 1e-6)
                if not 0.5 <= ratio / part.size_ratio <= 2.0:
                    notes.append(f"size against {part.size_vs}: expected about {part.size_ratio:.2g} times, "
                                 f"measured {ratio:.2g} times")
            contacts = meas.get("contacts")
            for other in part.touches:
                ob = by.get(other, {}).get("boxes", [])
                if not ob:
                    continue
                if contacts is not None and "mask" in by.get(part.part_id, {}) and "mask" in by.get(other, {}):
                    apart = not any({part.part_id, other} == set(pair) for pair in contacts)
                else:
                    apart = min(_gap(b, o) for b in found for o in ob) > near
                if apart:
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
    lines += [f"{i}. {pid} ('{names.get(pid, pid)}'): {'; '.join(n)}" for i, (pid, n) in enumerate(diffs.items(), 1)] \
        or ["- every part was found and matched its expected count, axis, size and contacts"]
    if diffs:
        lines.append("Add one deviation per numbered finding (what = the part id), say what the pixels show "
                     "and whether it matters for the working principle.")
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


SAM_COLORS = [(230, 57, 70), (29, 120, 220), (42, 157, 85), (244, 162, 37), (142, 68, 173), (0, 150, 160),
              (200, 80, 150), (120, 120, 40), (90, 90, 90), (210, 105, 30)]


def draw_overlay(render_png: Path, sam_json: Path, out_png: Path) -> Path:
    """What the segmenter saw: every SAM box on the render in one colour per part with the phrase it was
    given, and a strip listing the parts it could not find (code only; no model call)."""
    from PIL import ImageDraw

    from hs.stage_b.annotate import _font

    data = json.loads(sam_json.read_text(encoding="utf-8"))
    img = Image.open(render_png).convert("RGB")
    w, h = img.size
    font = _font(max(16, w // 70))
    missing = [f"{pid} ('{rec['phrase']}')" for pid, rec in data["parts"].items() if not rec["boxes"]]
    lines: list[str] = []  # the not-found list, wrapped to the picture width
    for item in missing:
        trial = (lines[-1] + "; " + item) if lines else "Not found: " + item
        if lines and ImageDraw.Draw(img).textlength(trial, font=font) <= w - 20:
            lines[-1] = trial
        else:
            lines.append(trial if not lines else item)
    strip_h = (font.size + 14) * (1 + len(lines))  # type: ignore[attr-defined]
    canvas = Image.new("RGB", (w, h + strip_h), "white")
    canvas.paste(img, (0, 0))
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i, (pid, rec) in enumerate(data["parts"].items()):  # all fills first, so no fill covers a name tag
        mask_file = sam_json.parent / rec.get("mask", {}).get("file", "-")
        if mask_file.exists():  # fill the part's mask in its colour
            m = Image.open(mask_file).convert("L").resize((w, h))
            tint = Image.new("RGBA", (w, h), SAM_COLORS[i % len(SAM_COLORS)] + (130,))
            overlay.paste(tint, (0, 0), m.point(lambda v: 255 if v > 127 else 0))  # tint alpha applies once
    for i, (pid, rec) in enumerate(data["parts"].items()):
        color = SAM_COLORS[i % len(SAM_COLORS)]
        for j, (x0, y0, x1, y1) in enumerate(rec["boxes"]):
            draw.rectangle([x0, y0, x1, y1], outline=color + (255,), width=max(2, w // 600))
            if j == 0:
                text = f"{rec['phrase']} ×{len(rec['boxes'])}" if len(rec["boxes"]) > 1 else rec["phrase"]
                tw = draw.textlength(text, font=font)
                ty = max(y0 - font.size - 8, 0)  # type: ignore[attr-defined]
                draw.rectangle([x0, ty, x0 + tw + 10, ty + font.size + 6], fill=color + (230,))  # type: ignore[attr-defined]
                draw.text((x0 + 5, ty + 2), text, fill=(255, 255, 255, 255), font=font)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    found = sum(1 for rec in data["parts"].values() if rec["boxes"])
    d.text((10, h + 6), f"SAM 3.1 found {found} of {len(data['parts'])} parts (each part's mask and box in its colour).",
           fill=(30, 30, 30), font=font)
    if missing:
        for k, line in enumerate(lines):
            d.text((10, h + 6 + (k + 1) * (font.size + 10)), line, fill=(150, 30, 30), font=font)  # type: ignore[attr-defined]
    canvas.save(out_png)
    return out_png
