"""Final figure panels A-D (spec §5.6). Words/captions drawn by code only."""
from __future__ import annotations

import json
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
    img = Image.new("RGB", (760, 220), "white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 8), "C Measurement chain", fill=(0, 0, 0))
    x = 20
    for stage in solution.measurement_chain:
        draw.rectangle([x, 70, x + 150, 150], outline=(0, 90, 90), width=2)
        draw.text((x + 8, 90), stage.stage, fill=(0, 90, 90))
        draw.text((x + 8, 112), stage.name[:18], fill=(0, 0, 0))
        draw.line([x + 150, 110, x + 180, 110], fill=(0, 90, 90), width=2)
        draw.polygon([(x + 180, 110), (x + 170, 105), (x + 170, 115)], fill=(0, 90, 90))
        x += 185
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
    step_images: list[Path] = []
    failed_steps: list[int] = []
    for i, present in enumerate(repaired):
        if images_used >= config.MAX_FIGURE_IMAGES:
            trace_notes.append(f"figure image budget reached; step {i + 1} panel skipped")
            break
        tmp = final_dir / f"_step{i + 1}_ref"
        schematic_mod.render_schematic(spec, tmp, subset_ids=present, stem=f"step{i + 1}")
        png = client.image_edit(f"fabrication step {i + 1}: show exactly parts {present}",
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
        strip = Image.new("RGB", (360 * len(thumbs), 260), "white")
        d = ImageDraw.Draw(strip)
        steps_sorted = sorted(solution.fabrication_steps, key=lambda s: s.step)
        for i, thumb in enumerate(thumbs):
            strip.paste(thumb, (360 * i, 0))
            desc = steps_sorted[i].description[:34] if i < len(steps_sorted) else ""
            mark = " (o)" if (i + 1) in failed_steps else ""
            d.text((360 * i + 6, 232), f"{i + 1}. {desc}{mark}", fill=(0, 0, 0))
        panel_d = final_dir / "panel_D.png"
        strip.save(panel_d)
    else:
        panel_d = panel_c
    # compose 2-column figure
    a = Image.open(panel_a).resize((780, 488))
    b = Image.open(panel_b)
    b = b.resize((380, 300)) if b.size[0] > 0 else b
    c = Image.open(panel_c)
    dimg = Image.open(panel_d)
    canvas = Image.new("RGB", (1600, 1250), "white")
    canvas.paste(a, (10, 10))
    canvas.paste(b, (810, 10))
    canvas.paste(c, (810, 330))
    dimg = dimg.resize((min(dimg.size[0], 1580), 260)) if dimg.size[0] > 0 else dimg
    canvas.paste(dimg, (10, 900))
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
