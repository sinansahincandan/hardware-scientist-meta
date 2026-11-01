"""Final figure panels A-D (spec §5.6). Words/captions drawn by code only."""
from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from hs import config
from hs.schemas import LightCheck, Localization, SchematicSpec, SolutionPrompt
from hs.stage_b import schematic as schematic_mod


def _repair_steps(solution: SolutionPrompt, trace: list[str]) -> list[list[str]]:
    part_ids = [p.id for p in solution.concept.parts]
    repaired: list[list[str]] = []
    seen: set[str] = set()
    steps = sorted(solution.fabrication_steps, key=lambda s: s.step)
    for i, step in enumerate(steps):
        present = [p for p in step.parts_present if p in part_ids]
        if len(present) != len(step.parts_present):
            trace.append(f"figure repair: step {step.step} dropped unknown part ids")
        seen |= set(present)
        present = [p for p in part_ids if p in seen]  # cumulative
        if i == 0 and not present:
            largest = max(solution.concept.parts,
                          key=lambda p: p.size_class_mm.max - p.size_class_mm.min)
            present = [largest.id]
            seen = {largest.id}
            trace.append("figure repair: empty step 1 defaults to the largest part")
        repaired.append(present)
    if repaired and set(repaired[-1]) != set(part_ids):
        repaired[-1] = list(part_ids)
        trace.append("figure repair: last step must contain all parts")
    return repaired


def _panel_c(solution: SolutionPrompt, path: Path) -> None:
    from hs.stage_b.annotate import _font

    img = Image.new("RGB", (1000, 260), "white")
    draw = ImageDraw.Draw(img)
    title, body = _font(26), _font(20)
    draw.text((10, 8), "C Measurement chain", fill=(0, 0, 0), font=title)
    x = 20
    for stage in solution.measurement_chain:
        draw.rectangle([x, 80, x + 200, 190], outline=(0, 90, 90), width=3)
        draw.text((x + 10, 100), stage.stage, fill=(0, 90, 90), font=body)
        for j, line in enumerate(textwrap.wrap(stage.name, width=17)[:2]):
            draw.text((x + 10, 132 + j * 26), line, fill=(0, 0, 0), font=body)
        draw.line([x + 200, 135, x + 235, 135], fill=(0, 90, 90), width=3)
        draw.polygon([(x + 235, 135), (x + 222, 128), (x + 222, 142)], fill=(0, 90, 90))
        x += 240
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def compose(client: Any, solution: SolutionPrompt, spec: SchematicSpec, *,
            annotated_path: Path, localization: Localization, run_dir: Path,
            master_history: list[dict[str, Any]], s_history: list[dict[str, Any]],
            sources: list[str], best_effort: bool = False) -> Path:
    final_dir = run_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    trace_notes: list[str] = []
    images_used = 0
    annotated = Image.open(annotated_path).convert("RGB")
    panel_a = final_dir / "panel_A.png"
    annotated.save(panel_a)
    # Flow view (v2, optional): only when the council recorded a flow_choice.
    # Arrows follow the transfer_line order (the governing quantity's path),
    # never an automatic all-edges overlay.
    if solution.flow_choice:
        try:
            overlay = annotated.convert("RGBA")
            arrows = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
            ad = ImageDraw.Draw(arrows)
            w, h = overlay.size
            centers: dict[str, tuple[float, float]] = {}
            label_of = {n.id: n.label.lower() for n in spec.nodes}
            for p in localization.parts:
                if p.found:
                    centers[label_of.get(p.id, p.id).lower()] = (
                        (p.box_1000.x0 + p.box_1000.x1) / 2000 * w,
                        (p.box_1000.y0 + p.box_1000.y1) / 2000 * h)
            path_text = solution.transfer_line.split("|")[0].split(":", 1)[-1]
            stops = [s.strip().lower() for s in path_text.replace("->", "→").split("→")]
            pts = [centers[s] for s in stops if s in centers]
            from itertools import pairwise

            for (x1, y1), (x2, y2) in pairwise(pts):
                ad.line([x1, y1, x2, y2], fill=(230, 120, 30, 160), width=max(5, w // 220))
                ang = math.atan2(y2 - y1, x2 - x1)
                for da in (2.6, -2.6):
                    ad.line([x2, y2, x2 - 26 * math.cos(ang + da), y2 - 26 * math.sin(ang + da)],
                            fill=(230, 120, 30, 180), width=max(5, w // 220))
            flow_path = final_dir / "flow.png"
            Image.alpha_composite(overlay, arrows).convert("RGB").save(flow_path)
            images_used.append(str(flow_path))
        except Exception as exc:  # flow view is optional; never fail the figure
            trace_notes.append(f"flow view skipped: {exc}")
    # Panel B: crop around critical part
    crit_box = next((p for p in localization.parts if p.id == spec.critical_part_id and p.found), None)
    panel_b_img: Image.Image
    if crit_box is not None:
        w, h = annotated.size
        b = crit_box.box_1000
        x0, y0 = int(b.x0 / 1000 * w), int(b.y0 / 1000 * h)
        x1, y1 = int(b.x1 / 1000 * w), int(b.y1 / 1000 * h)
        pad = 40
        crop = annotated.crop((max(x0 - pad, 0), max(y0 - pad, 0), min(x1 + pad, w), min(y1 + pad, h)))
        if min(crop.size) < 300 and images_used < config.MAX_FIGURE_IMAGES:
            neighbours = [e.from_id if e.to_id == spec.critical_part_id else e.to_id
                          for e in spec.edges if spec.critical_part_id in (e.from_id, e.to_id)]
            subset = list(dict.fromkeys([spec.critical_part_id] + neighbours))
            tmp = final_dir / "_closeup_ref"
            schematic_mod.render_schematic(spec, tmp, subset_ids=subset, stem="closeup")
            ok = False
            for _attempt in range(2):
                if images_used >= config.MAX_FIGURE_IMAGES:
                    break
                png = client.image_edit(f"close-up of {spec.critical_part_id} and its neighbours",
                                        tmp / "closeup.png")
                images_used += 1
                cand = final_dir / "_closeup.png"
                cand.write_bytes(png)
                check = client.structured("light_check", LightCheck, "Light check.",
                                          "Does it show the critical part and its neighbours?",
                                          image_paths=[cand])
                if check.ok:
                    panel_b_img = Image.open(cand).convert("RGB")
                    ok = True
                    break
            if not ok:
                panel_b_img = crop
                trace_notes.append("close-up light check failed; used crop of A for panel B")
        else:
            scale = min(2.0, 600 / max(min(crop.size), 1)) if min(crop.size) > 0 else 1.0
            if scale > 1.0:
                crop = crop.resize((int(crop.size[0] * scale), int(crop.size[1] * scale)))
            panel_b_img = crop
    else:
        panel_b_img = annotated
        trace_notes.append("critical part not localized; panel B reuses panel A")
    draw_b = ImageDraw.Draw(panel_b_img)
    draw_b.text((10, 8), "B Critical part", fill=(0, 0, 0))
    draw_b.line([10, panel_b_img.size[1] - 24, 110, panel_b_img.size[1] - 24], fill=(0, 90, 90), width=4)
    draw_b.text((10, panel_b_img.size[1] - 18), f"~{spec.scale_bar_mm:g} mm", fill=(0, 90, 90))
    panel_b = final_dir / "panel_B.png"
    panel_b_img.save(panel_b)
    # Panel C
    panel_c = final_dir / "panel_C.png"
    _panel_c(solution, panel_c)
    # Panel D: one render per fabrication step
    repaired = _repair_steps(solution, trace_notes)
    steps_sorted = sorted(solution.fabrication_steps, key=lambda s: s.step)
    step_images: list[Path] = []
    failed_steps: list[int] = []
    for i, present in enumerate(repaired):
        if images_used >= config.MAX_FIGURE_IMAGES:
            trace_notes.append(f"figure image budget reached; step {i + 1} panel skipped")
            break
        tmp = final_dir / f"_step{i + 1}_ref"
        schematic_mod.render_schematic(spec, tmp, subset_ids=present, stem=f"step{i + 1}")
        step_desc = steps_sorted[i].description if i < len(steps_sorted) else ""
        names = ", ".join(next((p.name for p in solution.concept.parts if p.id == pid), pid) for pid in present)
        png = client.image_edit(
            f"Photorealistic workshop scene, fabrication step {i + 1}: {step_desc}. "
            f"Show exactly these parts assembled so far ({names}) on a workbench with ordinary "
            f"shop tools, following the reference layout. No text, no labels, no numbers.",
            tmp / f"step{i + 1}.png")
        images_used += 1
        step_path = final_dir / f"_step{i + 1}.png"
        step_path.write_bytes(png)
        check = client.structured("light_check", LightCheck, "Light check.",
                                  f"Does it show step {i + 1} with exactly these parts {present}?",
                                  image_paths=[step_path])
        if not check.ok:
            failed_steps.append(i + 1)
        step_images.append(step_path)
    # compose D strip with code captions
    if step_images:
        thumbs = [Image.open(p).convert("RGB").resize((360, 225)) for p in step_images]
        strip = Image.new("RGB", (360 * len(thumbs), 300), "white")
        d = ImageDraw.Draw(strip)
        from hs.stage_b.annotate import _font

        cap_font = _font(17)
        steps_sorted = sorted(solution.fabrication_steps, key=lambda s: s.step)
        for i, thumb in enumerate(thumbs):
            strip.paste(thumb, (360 * i, 0))
            desc = steps_sorted[i].description if i < len(steps_sorted) else ""
            mark = " (o)" if (i + 1) in failed_steps else ""
            lines = textwrap.wrap(f"{i + 1}. {desc}{mark}", width=30)[:3]
            for j, line in enumerate(lines):
                d.text((360 * i + 6, 230 + j * 21), line, fill=(0, 0, 0), font=cap_font)
        panel_d = final_dir / "panel_D.png"
        strip.save(panel_d)
    else:
        panel_d = panel_c
    # Compose 2-column figure from measured panel heights (no fixed gaps).
    a = Image.open(panel_a)
    a = a.resize((780, int(780 * a.size[1] / max(a.size[0], 1))))
    b = Image.open(panel_b)
    b = b.resize((760, int(760 * b.size[1] / max(b.size[0], 1)))) if b.size[0] > 0 else b
    c = Image.open(panel_c)
    c = c.resize((760, int(760 * c.size[1] / max(c.size[0], 1))))
    dimg = Image.open(panel_d)
    dimg = dimg.resize((1580, int(1580 * dimg.size[1] / max(dimg.size[0], 1)))) if dimg.size[0] > 0 else dimg
    right_h = b.size[1] + 16 + c.size[1]
    row1_h = max(a.size[1], right_h)
    canvas = Image.new("RGB", (1600, 20 + row1_h + 16 + dimg.size[1]), "white")
    canvas.paste(a, (10, 10))
    canvas.paste(b, (810, 10))
    canvas.paste(c, (810, 10 + b.size[1] + 16))
    canvas.paste(dimg, (10, 20 + row1_h))
    figure_path = final_dir / "figure.png"
    canvas.save(figure_path)
    # rationale.md
    lines = [f"# Rationale — {solution.title}", "", solution.problem_restatement, "",
             "## Key estimates"]
    for est in solution.key_estimates:
        lines.append(f"- {est.quantity}: {est.value} {est.unit} ({est.method}; evidence {est.evidence_ids})")
    lines += ["", "## Risks"]
    for risk in solution.risks:
        lines.append(f"- {risk.risk} — mitigation: {risk.mitigation}")
    lines += ["", f"## Novelty\n{solution.novelty_claim}", "", "## Sources"]
    lines += [f"- {s}" for s in sources] or ["- (none)"]
    lines += ["", "## Master prompt revision history"]
    for entry in master_history:
        lines.append(f"- rev {entry.get('rev')}: {entry.get('changed')} — {entry.get('change_note', '')}")
    lines += ["", "## S1/S2 history"]
    for entry in s_history:
        lines.append(f"- attempt {entry.get('attempt')} round {entry.get('round')}: "
                     f"S1 faithful={entry.get('s1_faithful')} S2 flaw={entry.get('s2_flaw')} "
                     f"decision={entry.get('decision')}")
    if failed_steps:
        lines += ["", f"Panels failing light check (hollow marker in caption): steps {failed_steps}"]
    if trace_notes:
        lines += ["", "## Figure notes"] + [f"- {n}" for n in trace_notes]
    if best_effort:
        lines.append("\n_Best-effort figure (run exited through the best-effort path)._")
    (final_dir / "rationale.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (final_dir / "figure_images_used.json").write_text(json.dumps({"images": images_used}), encoding="utf-8")
    return figure_path


def recompose(run_dir: Path) -> Path:
    """Layout-only recomposition from existing panel PNGs (no model calls)."""
    final_dir = run_dir / "final"
    a = Image.open(final_dir / "panel_A.png")
    a = a.resize((780, int(780 * a.size[1] / max(a.size[0], 1))))
    b = Image.open(final_dir / "panel_B.png")
    b = b.resize((760, int(760 * b.size[1] / max(b.size[0], 1))))
    c = Image.open(final_dir / "panel_C.png")
    c = c.resize((760, int(760 * c.size[1] / max(c.size[0], 1))))
    dimg = Image.open(final_dir / "panel_D.png")
    dimg = dimg.resize((1580, int(1580 * dimg.size[1] / max(dimg.size[0], 1))))
    row1_h = max(a.size[1], b.size[1] + 16 + c.size[1])
    canvas = Image.new("RGB", (1600, 20 + row1_h + 16 + dimg.size[1]), "white")
    canvas.paste(a, (10, 10))
    canvas.paste(b, (810, 10))
    canvas.paste(c, (810, 10 + b.size[1] + 16))
    canvas.paste(dimg, (10, 20 + row1_h))
    out = final_dir / "figure.png"
    canvas.save(out)
    return out
