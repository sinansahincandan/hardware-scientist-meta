"""Final figure panels A-D (spec §5.6). Words/captions drawn by code only."""
from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from hs import config
from hs.client import BudgetExceeded
from hs.plain import plain_words
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


def _panel_c(solution: SolutionPrompt, path: Path) -> bool:
    """Code-only measurement chain; nothing is cut. Returns False (no panel) when the chain is empty."""
    from hs.stage_b.annotate import _font

    stages = solution.measurement_chain
    if not stages:
        return False
    title, body = _font(26), _font(20)
    wrapped = [textwrap.wrap(stage.name, width=17) or [""] for stage in stages]
    box_h = 60 + 26 * max(len(w) for w in wrapped)
    img = Image.new("RGB", (max(1000, 240 * len(stages) + 20), 100 + box_h), "white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 8), "C  Measurement chain", fill=(0, 0, 0), font=title)
    x = 20
    for i, (stage, lines) in enumerate(zip(stages, wrapped, strict=True)):
        draw.rectangle([x, 70, x + 200, 70 + box_h], outline=(0, 90, 90), width=3)
        draw.text((x + 10, 82), stage.stage, fill=(0, 90, 90), font=body)
        for j, line in enumerate(lines):
            draw.text((x + 10, 112 + j * 26), line, fill=(0, 0, 0), font=body)
        if i < len(stages) - 1:
            draw.line([x + 200, 70 + box_h // 2, x + 235, 70 + box_h // 2], fill=(0, 90, 90), width=3)
            draw.polygon([(x + 235, 70 + box_h // 2), (x + 222, 63 + box_h // 2), (x + 222, 77 + box_h // 2)],
                         fill=(0, 90, 90))
        x += 240
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return True


def _panel_b(render_path: Path, spec: SchematicSpec, localization: Localization, path: Path,
             notes: list[str]) -> bool:
    """Crop of the passing render around the critical part (C19), with its name and a scale bar.
    Boxes and crop share the render's coordinate basis. No crop -> no panel B."""
    from hs.stage_b.annotate import _font

    crit = next((p for p in localization.parts if p.id == spec.critical_part_id and p.found), None)
    node = next((n for n in spec.nodes if n.id == spec.critical_part_id), None)
    if crit is None or node is None:
        notes.append("critical part was not located in the render; panel B omitted")
        return False
    render = Image.open(render_path).convert("RGB")
    w, h = render.size
    b = crit.box_1000
    if (b.x1 - b.x0) * (b.y1 - b.y0) > 0.4 * 1000 * 1000:  # the critical part is most of the picture
        notes.append(f"the critical part ({node.label}) fills most of the picture; panel B would repeat panel A, omitted")
        return False
    x0, y0, x1, y1 = b.x0 / 1000 * w, b.y0 / 1000 * h, b.x1 / 1000 * w, b.y1 / 1000 * h
    pad = 0.25 * max(x1 - x0, y1 - y0, 40)
    box = (int(max(x0 - pad, 0)), int(max(y0 - pad, 0)), int(min(x1 + pad, w)), int(min(y1 + pad, h)))
    crop = render.crop(box)
    scale = min(2.0, 700 / max(max(crop.size), 1))
    if scale > 1.0:
        crop = crop.resize((int(crop.size[0] * scale), int(crop.size[1] * scale)))
    font = _font(max(18, crop.size[0] // 32))
    head = font.size + 16  # type: ignore[attr-defined]
    panel = Image.new("RGB", (crop.size[0], crop.size[1] + head), "white")
    panel.paste(crop, (0, head))
    draw = ImageDraw.Draw(panel)
    draw.text((8, 6), f"B  Critical part: {node.label}", fill=(0, 0, 0), font=font)
    gm = math.sqrt(max(node.size_class_mm.min, 0.01) * max(node.size_class_mm.max, 0.01))
    px_per_mm = (x1 - x0) * max(scale, 1.0) / gm if x1 > x0 else 0.0
    from hs.stage_b.annotate import nice_scale_mm

    bar_mm = nice_scale_mm(gm)
    bar_px = bar_mm * px_per_mm
    if 10 < bar_px < crop.size[0] - 20:
        y = panel.size[1] - 18
        draw.rectangle([6, y - 26, 16 + bar_px, panel.size[1] - 2], fill=(255, 255, 255))
        draw.line([10, y, 10 + bar_px, y], fill=(0, 90, 90), width=4)
        draw.text((10, y - 24), f"~{bar_mm:g} mm", fill=(0, 90, 90), font=_font(16))
    path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(path)
    return True


def _step_check(client: Any, solution: SolutionPrompt, step: int, desc: str, names: str,
                image: Path) -> tuple[LightCheck, bool]:
    """Detailed check (the client re-words it once without numbers if the content filter blocks it); only
    if that is blocked too, one general check. Returns (check, general_only)."""
    try:
        return client.structured(
            "light_check", LightCheck, "Light check.",
            f"Does it show fabrication step {step} ({desc}) with these parts: {names}? The numbers are "
            "references only; judge the parts and the stage, not exact sizes. Answer from the pixels.",
            image_paths=[image]), False
    except BudgetExceeded:
        raise
    except Exception as exc:
        if "content management policy" not in str(exc):
            raise
    return client.structured(
        "light_check", LightCheck, "Light check.",
        f"Does this workshop photo show a stage of building this device: {plain_words(solution.title)}? "
        "Answer from the pixels.", image_paths=[image]), True


def relabel_panel_a(client: Any, spec: SchematicSpec, render_path: Path, localization: Localization,
                    panel_a: Path, notes: list[str]) -> None:
    """16a: labels that point at the wrong part are removed, never shown (run 02: 'PU box' on the control box)."""
    from hs.stage_b.annotate import Annotator

    annotator = Annotator(client)
    try:
        wrong = annotator.check_labels(panel_a, spec, localization)
    except BudgetExceeded:
        raise
    except Exception as exc:
        notes.append(f"label check could not run ({type(exc).__name__}); labels not verified")
        return
    if not wrong:
        notes.append("label check: every label points at the part it names")
        return
    kept = Localization(parts=[p.model_copy(update={"found": p.found and p.id not in wrong})
                               for p in localization.parts])
    annotator.run(render_path, spec, {}, panel_a, localization=kept, fallback=False)
    names = [n.label for n in spec.nodes if n.id in wrong]
    notes.append(f"labels removed because they pointed at the wrong part: {', '.join(names)}")


def compose(client: Any, solution: SolutionPrompt, spec: SchematicSpec, *,
            annotated_path: Path, render_path: Path, localization: Localization, run_dir: Path,
            master_history: list[dict[str, Any]], s_history: list[dict[str, Any]],
            sources: list[str], best_effort: bool = False) -> Path:
    final_dir = run_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    trace_notes: list[str] = []
    images_used = 0
    panel_a = final_dir / "panel_A.png"
    Image.open(annotated_path).convert("RGB").save(panel_a)
    relabel_panel_a(client, spec, render_path, localization, panel_a, trace_notes)
    panel_b = final_dir / "panel_B.png"
    has_b = _panel_b(render_path, spec, localization, panel_b, trace_notes)
    panel_c = final_dir / "panel_C.png"
    has_c = _panel_c(solution, panel_c)
    if not has_c:
        trace_notes.append("no measurement chain recorded; panel C omitted")
    # Panel D: one render per fabrication step; a step that fails its light check is not shipped.
    repaired = _repair_steps(solution, trace_notes)
    steps_sorted = sorted(solution.fabrication_steps, key=lambda s: s.step)
    shipped: list[tuple[Path, str]] = []
    failed_steps: list[int] = []
    for i, present in enumerate(repaired):
        if images_used >= config.MAX_FIGURE_IMAGES:
            trace_notes.append(f"figure image budget reached; step {i + 1} panel skipped")
            break
        tmp = final_dir / f"_step{i + 1}_ref"
        schematic_mod.render_schematic(spec, tmp, subset_ids=present, stem=f"step{i + 1}")
        step_desc = steps_sorted[i].description if i < len(steps_sorted) else ""
        names = ", ".join(next((p.name for p in solution.concept.parts if p.id == pid), pid) for pid in present)
        try:
            png = client.image_edit(
                f"Photorealistic workshop scene, fabrication step {i + 1}: {step_desc}. "
                f"Show these parts assembled so far ({names}) on a workbench with ordinary "
                f"shop tools, following the reference layout. The image carries no text.",
                tmp / f"step{i + 1}.png")
            images_used += 1
            step_path = final_dir / f"_step{i + 1}.png"
            step_path.write_bytes(png)
            check, general = _step_check(client, solution, i + 1, step_desc, names, step_path)
        except BudgetExceeded:
            raise
        except Exception as exc:  # a panel-D step must never sink the figure (run 02: content filter 400)
            failed_steps.append(i + 1)
            trace_notes.append(f"fabrication step {i + 1} could not be made or checked ({type(exc).__name__}: "
                               f"{str(exc)[:160]}); not shown")
            continue
        if check.ok:
            shipped.append((step_path, f"{i + 1}. {step_desc}" + (" (general check only)" if general else "")))
            if general:
                trace_notes.append(f"fabrication step {i + 1}: the detailed check was blocked by the provider's "
                                   "content filter; it passed a general check only (caption marked)")
        else:
            failed_steps.append(i + 1)
            trace_notes.append(f"fabrication step {i + 1} failed its light check ({check.reason}); not shown")
    panel_d: Path | None = None
    if shipped:
        from hs.stage_b.annotate import _font

        cap_font = _font(17)
        captions = [textwrap.wrap(cap, width=30) for _, cap in shipped]
        cap_h = 10 + 21 * max(len(c) for c in captions)
        tw, th = 520, 325
        strip = Image.new("RGB", (tw * len(shipped), th + cap_h), "white")
        d = ImageDraw.Draw(strip)
        for i, ((step_path, _cap), lines) in enumerate(zip(shipped, captions, strict=True)):
            strip.paste(Image.open(step_path).convert("RGB").resize((tw, th)), (tw * i, 0))
            for j, line in enumerate(lines):
                d.text((tw * i + 6, th + 5 + j * 21), line, fill=(0, 0, 0), font=cap_font)
        panel_d = final_dir / "panel_D.png"
        strip.save(panel_d)
    for stale, keep in ((panel_b, has_b), (panel_c, has_c)):
        if not keep and stale.exists():
            stale.unlink()
    if panel_d is None and (final_dir / "panel_D.png").exists():
        (final_dir / "panel_D.png").unlink()
    # Compose 2-column figure from measured panel heights (no fixed gaps); absent panels leave no gap.
    canvas = _layout(panel_a, panel_b if has_b else None, panel_c if has_c else None, panel_d)
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
        lines += ["", f"Fabrication steps not shown because they failed their light check: {failed_steps}"]
    if trace_notes:
        lines += ["", "## Figure notes"] + [f"- {n}" for n in trace_notes]
    if best_effort:
        lines.append("\n_Best-effort figure (run exited through the best-effort path)._")
    (final_dir / "rationale.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (final_dir / "figure_images_used.json").write_text(json.dumps({"images": images_used}), encoding="utf-8")
    return figure_path


def _layout(panel_a: Path, panel_b: Path | None, panel_c: Path | None, panel_d: Path | None) -> Image.Image:
    """Panel A full width on top; B, C and D side by side below at one height (no white gaps)."""
    width = 1600
    a = Image.open(panel_a).convert("RGB")
    a = a.resize((width - 20, int((width - 20) * a.size[1] / max(a.size[0], 1))))
    row = [Image.open(p).convert("RGB") for p in (panel_b, panel_c, panel_d) if p is not None]
    row_h = 0
    if row:
        row_h = 420
        row = [im.resize((int(im.size[0] * row_h / max(im.size[1], 1)), row_h)) for im in row]
        total = sum(im.size[0] for im in row) + 12 * (len(row) - 1)
        if total > width - 20:  # shrink the whole row to fit
            k = (width - 20) / total
            row_h = int(row_h * k)
            row = [im.resize((max(int(im.size[0] * k), 1), row_h)) for im in row]
    canvas = Image.new("RGB", (width, 20 + a.size[1] + (12 + row_h if row else 0)), "white")
    canvas.paste(a, (10, 10))
    x = 10
    for im in row:
        canvas.paste(im, (x, 22 + a.size[1]))
        x += im.size[0] + 12
    return canvas


def recompose(run_dir: Path) -> Path:
    """Layout-only recomposition from existing panel PNGs (no model calls)."""
    final_dir = run_dir / "final"

    def _opt(name: str) -> Path | None:
        return final_dir / name if (final_dir / name).exists() else None

    out = final_dir / "figure.png"
    _layout(final_dir / "panel_A.png", _opt("panel_B.png"), _opt("panel_C.png"), _opt("panel_D.png")).save(out)
    return out
