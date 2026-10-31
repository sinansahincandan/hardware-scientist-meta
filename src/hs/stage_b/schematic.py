"""Schematic: spec call + code checks + deterministic rendering (spec §5.1)."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from hs.schemas import SchematicEdge, SchematicLoad, SchematicNode, SchematicSpec, SizeClass, SolutionPrompt

COLORS = ["#d95f4b", "#3f7cac", "#70a37f", "#e3b505", "#8e6c8a", "#4b8f8a"]


def build_spec_from_solution(solution: SolutionPrompt) -> SchematicSpec:
    nodes: list[SchematicNode] = []
    for i, part in enumerate(solution.concept.parts):
        nodes.append(SchematicNode(id=part.id, label=part.name, shape="rect",
                                   size_class_mm=part.size_class_mm,
                                   layout={"col": i, "row": 0},  # type: ignore[arg-type]
                                   color_hint=COLORS[i % len(COLORS)]))
    edges = [SchematicEdge(from_id=c.from_id, to_id=c.to_id, kind=c.kind, label=c.label, arrow=False)
             for c in solution.concept.connections]
    loads = [SchematicLoad(on_id=l.on_id, label=l.label, direction=l.direction)
             for l in solution.concept.loads]
    return SchematicSpec(view="side", nodes=nodes, edges=edges, loads=loads,
                         critical_part_id=solution.figure_spec.critical_part_id,
                         scale_bar_mm=10.0, notes=[])


def check_spec(spec: SchematicSpec, solution: SolutionPrompt) -> list[str]:
    errors: list[str] = []
    part_ids = {p.id for p in solution.concept.parts}
    node_ids = {n.id for n in spec.nodes}
    for pid in sorted(part_ids - node_ids):
        errors.append(f"part {pid} missing as schematic node")
    for edge in spec.edges:
        if edge.from_id not in node_ids:
            errors.append(f"edge endpoint {edge.from_id} missing")
        if edge.to_id not in node_ids:
            errors.append(f"edge endpoint {edge.to_id} missing")
    for load in spec.loads:
        if load.on_id not in node_ids:
            errors.append(f"load endpoint {load.on_id} missing")
    parts_by_id = {p.id: p for p in solution.concept.parts}
    for node in spec.nodes:
        part = parts_by_id.get(node.id)
        if part is not None and (node.size_class_mm.min < part.size_class_mm.min / 3.0
                                 or node.size_class_mm.max > part.size_class_mm.max * 3.0):
            errors.append(f"node {node.id} size outside its class")
    # connectivity (undirected BFS)
    if spec.nodes:
        adj: dict[str, set[str]] = {n.id: set() for n in spec.nodes}
        for edge in spec.edges:
            if edge.from_id in adj and edge.to_id in adj:
                adj[edge.from_id].add(edge.to_id)
                adj[edge.to_id].add(edge.from_id)
        seen: set[str] = set()
        stack = [spec.nodes[0].id]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(adj.get(cur, set()))
        if seen != node_ids:
            errors.append(f"schematic graph not connected: reached {sorted(seen)} of {sorted(node_ids)}")
    if spec.critical_part_id not in node_ids:
        errors.append(f"critical_part_id {spec.critical_part_id} is not a node")
    return errors


def spec_and_check(client: Any, solution: SolutionPrompt) -> tuple[SchematicSpec | None, list[str]]:
    """One spec call (+ one re-ask on check failure). Returns (spec, errors)."""
    if getattr(client, "is_fake", False):
        client.record_fake("schematic")
        spec = build_spec_from_solution(solution)
        if client.scenario == "schematic_fail" and client.fake_attempt == 0:
            spec = spec.model_copy(update={"nodes": spec.nodes[:-1]}) if len(spec.nodes) > 1 else spec
        errors = check_spec(spec, solution)
        if errors:
            # re-ask once; fake scenario keeps failing on attempt 0
            client.record_fake("schematic")
            spec2 = build_spec_from_solution(solution)
            if client.scenario == "schematic_fail" and client.fake_attempt == 0:
                spec2 = spec2.model_copy(update={"nodes": spec2.nodes[:-1]}) if len(spec2.nodes) > 1 else spec2
            errors2 = check_spec(spec2, solution)
            return (spec2 if not errors2 else None), errors2
        return spec, []
    spec = client.structured("schematic", SchematicSpec,
                             "Convert the concept into a 2D schematic spec.",
                             solution.model_dump_json(indent=2))
    errors = check_spec(spec, solution)
    if not errors:
        return spec, []
    spec = client.structured("schematic", SchematicSpec,
                             "Previous spec failed checks: " + "; ".join(errors) + ". Fix it.",
                             solution.model_dump_json(indent=2))
    errors = check_spec(spec, solution)
    return (spec if not errors else None), errors


def _geomean(size: SizeClass) -> float:
    return math.sqrt(max(size.min, 0.01) * max(size.max, 0.01))


def render_schematic(spec: SchematicSpec, out_dir: Path, subset_ids: list[str] | None = None,
                     stem: str = "schematic") -> dict[str, Any]:
    """Deterministic matplotlib render. Returns geometry dict (also saved as <stem>.json)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyArrow, Rectangle

    out_dir.mkdir(parents=True, exist_ok=True)
    nodes = [n for n in spec.nodes if subset_ids is None or n.id in subset_ids]
    node_ids = {n.id for n in nodes}
    edges = [e for e in spec.edges if e.from_id in node_ids and e.to_id in node_ids]
    loads = [l for l in spec.loads if l.on_id in node_ids]
    boxes: dict[str, dict[str, float]] = {}
    positions: dict[str, tuple[float, float, float, float]] = {}
    # Normalize arbitrary LLM layout values to sequential grid ranks so no
    # node lands off-canvas (real specs used col values up to 11 on a 0-9 axis).
    col_rank = {v: i for i, v in enumerate(sorted({n.layout.col for n in nodes}))}
    row_rank = {v: i for i, v in enumerate(sorted({n.layout.row for n in nodes}))}
    ncols = max(len(col_rank), 1)
    for node in nodes:
        gm = _geomean(node.size_class_mm)
        w = min(max(gm / 12.0, 0.7), 2.2)
        h = min(max(gm / 16.0, 0.5), 1.6)
        cx = 1.2 + col_rank[node.layout.col] * (8.4 / max(ncols - 1, 1) if ncols > 1 else 0)
        cy = 3.4 - row_rank[node.layout.row] * 2.0
        positions[node.id] = (cx, cy, w, h)
        boxes[node.id] = {"x0": (cx - w / 2) * 100, "y0": 625 - (cy + h / 2) * 100,
                          "x1": (cx + w / 2) * 100, "y1": 625 - (cy - h / 2) * 100,
                          "label": node.label}
    geometry: dict[str, Any] = {"px_per_mm": 4.0, "boxes": boxes, "width": 1000, "height": 625,
                                "critical_part_id": spec.critical_part_id, "scale_bar_mm": spec.scale_bar_mm}
    for labeled in (False, True):
        fig, ax = plt.subplots(figsize=(10, 6.25), dpi=100)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6.25)
        ax.axis("off")
        for edge in edges:
            x1, y1, _, _ = positions[edge.from_id]
            x2, y2, _, _ = positions[edge.to_id]
            style = "--" if edge.kind == "wireless" else "-"
            ax.plot([x1, x2], [y1, y2], color="#333333", lw=3 if edge.kind == "fluid" else 1.5, linestyle=style)
            if edge.kind == "fluid":
                ax.plot([x1, x2], [y1 + 0.06, y2 + 0.06], color="#333333", lw=1.2)
        for node in nodes:
            cx, cy, w, h = positions[node.id]
            if node.shape == "circle":
                ax.add_patch(Circle((cx, cy), w / 2, facecolor=node.color_hint, edgecolor="#333333"))
            else:
                ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h,
                                       facecolor=node.color_hint, edgecolor="#333333"))
            if labeled:
                ax.text(cx, cy, node.label, ha="center", va="center", fontsize=9)
        for load in loads:
            cx, cy, w, h = positions[load.on_id]
            dx, dy = {"down": (0, -1), "up": (0, 1), "left": (-1, 0), "right": (1, 0),
                      "in": (0, 0), "out": (0, 0)}[load.direction]
            if load.direction in ("in", "out"):
                ax.text(cx + w / 2 + 0.2, cy, "⊙" if load.direction == "in" else "⊗", fontsize=14)
            else:
                ax.add_patch(FancyArrow(cx - dx * (w / 2 + 0.7), cy - dy * (h / 2 + 0.7),
                                        dx * 0.6, dy * 0.6, width=0.05, color="red"))
            if labeled:
                ax.text(cx + w / 2 + 0.2, cy + h / 2 + 0.2, load.label, color="red", fontsize=10)
        name = f"{stem}_labeled.png" if labeled else f"{stem}.png"
        fig.savefig(out_dir / name, bbox_inches="tight")
        plt.close(fig)
    # Two-state reference view (labeled only): same mechanism with the critical
    # part offset one grid step — initial vs operated state (AUTOPILOT §4).
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6), dpi=100)
    for ax, (state, dx) in zip(axes, [("INITIAL", 0.0), ("OPERATED", 0.7)], strict=True):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6.25)
        ax.axis("off")
        ax.set_title(state, fontsize=10)
        for edge in edges:
            x1, y1, _, _ = positions[edge.from_id]
            x2, y2, _, _ = positions[edge.to_id]
            ox1 = dx if edge.from_id == spec.critical_part_id else 0.0
            ox2 = dx if edge.to_id == spec.critical_part_id else 0.0
            ax.plot([x1 + ox1, x2 + ox2], [y1, y2], color="#333333", lw=1.2)
        for node in nodes:
            cx, cy, w, h = positions[node.id]
            if node.id == spec.critical_part_id:
                cx += dx
            ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h,
                                   facecolor=node.color_hint, edgecolor="#333333"))
            ax.text(cx, cy - h / 2 - 0.45, node.label, ha="center", fontsize=7)
    fig.savefig(out_dir / f"{stem}_two_states.png", bbox_inches="tight")
    plt.close(fig)
    (out_dir / f"{stem}.json").write_text(json.dumps(geometry, indent=2), encoding="utf-8")
    return geometry
