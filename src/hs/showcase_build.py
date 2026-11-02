"""Showcase + dossier builder (v2 I/J).

Copies each final run's deliverable files into showcase/<slug>/ and
builds showcase/index.html plus one dossier.html per problem with
architecture path overlays drawn from docs/figures_map.json.
Pages are self-contained (inline CSS, relative paths only).
"""
from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from typing import Any

STYLE = """<style>
body{font-family:'Segoe UI',Helvetica,Arial,sans-serif;background:#f4f4f2;color:#1c1e22;margin:0}
main{max-width:1080px;margin:0 auto;padding:28px 22px 60px}
h1{font-size:30px;line-height:1.2;margin:6px 0 10px} h2{font-size:20px;margin:34px 0 10px;border-bottom:2px solid #222;padding-bottom:5px}
h3{font-size:16px;margin:20px 0 6px} p,li{font-size:15px;line-height:1.55}
.hero{background:#171a1f;color:#eee;border-radius:12px;padding:22px 26px}.hero .mech{font-size:19px;line-height:1.45}
.chip{display:inline-block;background:#e9f2e7;border:1px solid #9db894;border-radius:10px;padding:3px 9px;margin:2px;font-size:13px}
.event{border-left:3px solid #b9c4bb;padding:7px 12px;margin:8px 0;background:#fff}
.q{border:1px solid #d8a920;background:#fdf6dd;border-radius:8px;padding:10px 14px}
a{color:#1a5fb8} img{border-radius:6px;max-width:100%}
.small{color:#666;font-size:13px} table{border-collapse:collapse;background:#fff}
td,th{border:1px solid #ccc;padding:5px 9px;font-size:14px;text-align:left}
.overlay{background:#fff;border:1px solid #ccc;border-radius:8px;padding:8px;margin:10px 0}
dialog img{max-width:94vw;max-height:92vh}
</style>"""

COPY_DIRS = ("final", "master_prompt")
COPY_FILES = ("problem.json", "cost.json", "trace.md", "references.md",
              "report.html", "board.html", "REVIEW.md")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _slug(run_dir: Path) -> str:
    name = re.sub(r"^\d{8}-\d{6}_", "", run_dir.name)
    return name[:44].strip("-") or run_dir.name


def _ts(path: Path) -> str:
    from datetime import datetime

    return datetime.fromtimestamp(path.stat().st_mtime).strftime("[%Y-%m-%d %H:%M]")


def copy_run(run_dir: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for name in COPY_FILES:
        src = run_dir / name
        if src.exists():
            shutil.copy(src, dest / name)
    for name in COPY_DIRS:
        src = run_dir / name
        if src.exists():
            shutil.copytree(src, dest / name)
    # Figure-composer intermediates are provenance bulk, not reading material.
    for step in (dest / "final").glob("_step*"):
        shutil.rmtree(step) if step.is_dir() else step.unlink()
    for sub in ("stage_a", "stage_b"):
        src_root = run_dir / sub
        if not src_root.exists():
            continue
        for item in sorted(src_root.rglob("*")):
            if not item.is_file():
                continue
            keep = item.suffix in (".json", ".md", ".txt") or (
                item.suffix == ".png" and any(k in item.name for k in
                ("schematic", "render", "annotated", "local_", "edited_")))
            if keep:
                target = dest / item.relative_to(run_dir)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(item, target)
    _downscale(dest)


def _downscale(dest: Path) -> None:
    """Display copies at most 1600 px wide (v2 F2); click still enlarges."""
    try:
        from PIL import Image
    except ImportError:
        return
    for img_path in dest.rglob("*.png"):
        try:
            with Image.open(img_path) as im:
                if im.width > 1600:
                    im.resize((1600, round(im.height * 1600 / im.width))).save(img_path)
        except Exception:  # noqa: S112 — a bad image must not sink the page build
            continue


def _final_solution(run_dir: Path) -> dict[str, Any]:
    files = sorted(run_dir.glob("stage_a/iter_*/solution.json"))
    return _read_json(files[-1]) if files else {}


def _problem(run_dir: Path) -> dict[str, Any]:
    return _read_json(run_dir / "problem.json")


def _prompt_text(problem: dict[str, Any]) -> str:
    return str(problem.get("prompt") or problem.get("description") or
               problem.get("title") or "")


def _rounds(run_dir: Path) -> list[dict[str, Any]]:
    rounds: list[dict[str, Any]] = []
    for ev_path in sorted(run_dir.glob("stage_b/attempt_*/round_*/eval.json")):
        ev = _read_json(ev_path)
        rd = ev_path.parent
        grad = _read_json(rd / "vlm_gradient.json")
        progress = sorted(rd.glob("progress_*.json"))
        rounds.append({
            "name": f"{rd.parent.name}/{rd.name}", "dir": rd,
            "decision": (rd / "decision.txt").read_text(encoding="utf-8").strip()
            if (rd / "decision.txt").exists() else "",
            "s1": ev.get("s1_faithful"), "s2": ev.get("s2_flaw"),
            "regions": ev.get("regions", []),
            "fix_mode": grad.get("fix_mode", ""),
            "render": rd / "render.png", "first": ev_path == min(run_dir.glob("stage_b/attempt_*/round_*/eval.json")),
            "progress": [{"part": p.stem.replace("progress_", ""),
                          **{k: _read_json(p).get(k) for k in
                             ("fixed_region_pass", "previous_pass", "seam_visible")}}
                         for p in progress],
        })
    return rounds


def _overlay_svg(fig: str, steps: list[str], fmap: dict[str, Any]) -> str:
    """One overlay: original figure faded, used nodes outlined + badged."""
    meta = fmap[fig]
    nodes: dict[str, list[float]] = meta["nodes"]
    vw, vh = meta["viewBox"]
    svg_text = Path("docs", fig).read_text(encoding="utf-8")
    inner = re.sub(r"^<svg[^>]*>|</svg>$", "", svg_text, flags=re.DOTALL).strip()
    parts = [f'<svg viewBox="0 0 {vw} {vh}" width="100%" xmlns="http://www.w3.org/2000/svg">',
             ('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
              'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
              'fill="#c0392b"/></marker></defs>'),
             f'<g opacity="0.15">{inner}</g>']
    centers: list[tuple[float, float]] = []
    for i, node in enumerate(steps, 1):
        if node not in nodes:
            continue
        x, y, w, h = nodes[node]
        cx, cy = x + w / 2, y + h / 2
        if centers:
            px, py = centers[-1]
            parts.append(f'<line x1="{px}" y1="{py}" x2="{cx}" y2="{cy}" stroke="#c0392b" '
                         f'stroke-width="3" marker-end="url(#arr)" opacity="0.85"/>')
        centers.append((cx, cy))
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
                     f'stroke="#c0392b" stroke-width="4" rx="8"/>')
        parts.append(f'<circle cx="{x + 16}" cy="{y + 16}" r="15" fill="#c0392b"/>'
                     f'<text x="{x + 16}" y="{y + 21}" font-size="16" fill="#fff" '
                     f'text-anchor="middle" font-family="sans-serif">{i}</text>')
    parts.append("</svg>")
    return "".join(parts)


def _stage_a_steps(run_dir: Path, it: int) -> list[tuple[str, str]]:
    """(fig1 node, plain sentence) per Stage A iteration, from artifacts."""
    it_dir = run_dir / "stage_a" / f"iter_{it:02d}"
    steps: list[tuple[str, str]] = [("n-master", "The master prompt revision for this iteration set the council's roles, tools and meeting protocol.")]
    if (it_dir / "solution.json").exists() or list(it_dir.glob("turns/*")):
        steps.append(("n-council", "The council members took their seats with distinct domains."))
        steps.append(("n-manager-seat", "The Manager sat in the room as process lead and steered at the end of each cycle."))
        steps.append(("n-meeting", "The meeting ran in cycles on the shared whiteboard until the members closed it by consensus or the cycle cap closed it."))
    verdict = _read_json(it_dir / "verdict.json")
    if verdict:
        word = "accepted" if verdict.get("accept") else "rejected"
        steps.append(("n-evaluator", f"The evaluator {word} the solution: {str(verdict.get('feedback', ''))[:180]}"))
    if (it_dir / "rewrite.json").exists():
        steps.append(("n-master", "The Manager diagnosed the failure in two steps (output gradient, then prompt gradient) and the optimizer rewrote prompt sections; the rewrite is saved as a new revision with a diff."))
        steps.append(("n-lessons", "Lessons from earlier runs were applied through the master prompt."))
    steps.append(("n-council-archive", "The solution, its status and the feedback were stored in the council archive for later inspirations."))
    return steps


def _stage_b_steps(rd: dict[str, Any]) -> list[tuple[str, str]]:
    steps = [("n-accepted", "The accepted solution entered the visualization pipeline."),
             ("n-schematic", "The mechanism sketch was drawn from the solution: part proportions, joint circles, motion and load arrows, key dimensions."),
             ("n-vlm-writer", "The VLM prompt writer turned the sketch and solution into an image prompt."),
             ("n-render", "The image model rendered the concept from the sketch."),
             ("n-labels", "Part labels were placed on the render (drawn labels checked; code overlay as fallback)."),
             ("n-designer-eval", f"Designer evaluation judged the render region by region: S1 faithful = {rd['s1']}, S2 design flaw = {rd['s2']}; decision {rd['decision']}.")]
    if rd["decision"] == "s2_return":
        steps.append(("n-back-to-a", "A design flaw (source: the schematic or the solution) sent the concept back to the council."))
    steps.append(("n-image-archive", "The round's prompt, render and evaluation were stored in the image archive."))
    if rd["decision"] == "s1_pass":
        steps.append(("n-figure", "The final four-panel figure was composed from the passing render."))
    return steps


def build_showcase(run_dirs: list[Path], out: Path = Path("showcase")) -> Path:
    fmap = json.loads(Path("docs/figures_map.json").read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    cards: list[str] = []
    for run_dir in run_dirs:
        slug = _slug(run_dir)
        dest = out / slug
        copy_run(run_dir, dest)
        _dossier(run_dir, dest, fmap)
        problem, sol = _problem(run_dir), _final_solution(run_dir)
        rounds = _rounds(run_dir)
        revs = sorted((run_dir / "master_prompt").glob("rev_*.md")) \
            if (run_dir / "master_prompt").exists() else []
        fig_rel = f"{slug}/final/figure.png"
        evo = [f"Master prompt revisions: {len(revs)} (rev_000 to rev_{len(revs) - 1:03d})."]
        for rd in rounds:
            fix = f" VLM prompt gradient fix mode: {rd['fix_mode']}." if rd["fix_mode"] else ""
            kept = "".join(f" Local edit on {p['part']} kept: "
                           f"{bool(p['fixed_region_pass'] and p['previous_pass'] and not p['seam_visible'])}."
                           for p in rd["progress"])
            evo.append(f"Stage B {rd['name']}: decision {rd['decision']} with "
                       f"{len(rd['regions'])} evaluated regions.{fix}{kept}")
        choices = "".join(f"<li>{html.escape(str(c))}</li>" for c in sol.get("decisive_choices", []))
        cards.append(f"""<section class="hero"><h1 style="color:#fff">{html.escape(str(problem.get('title', slug)))}</h1>
<p class="mech">{html.escape(str(sol.get('mechanism_sentence', '')))}</p></section>
<h2>The problem</h2><p>{html.escape(_prompt_text(problem))}</p>
<a href="{fig_rel}"><img src="{fig_rel}" alt="final concept figure" style="max-width:100%"></a>
<p class="small">Final concept figure — click to enlarge.</p>
<h2>Three decisive choices</h2><ol>{choices}</ol>
<div class="q"><b>Open question:</b> {html.escape(str(sol.get('open_question', '')))}</div>
<h2>Evolution</h2>{''.join(f'<div class="event">{html.escape(e)}</div>' for e in evo)}
<p><a href="{slug}/report.html">Full report</a> · <a href="{slug}/board.html">Whiteboard replay</a> ·
<a href="{slug}/references.md">Reference list</a> · <a href="{slug}/dossier.html">Dossier</a></p>""")
    (out / "index.html").write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>Hardware Scientist — showcase</title>"
        f"{STYLE}</head><body><main><h1>Hardware Scientist — three problems, three concepts</h1>"
        + "".join(cards) + "</main></body></html>", encoding="utf-8")
    return out / "index.html"


def _dossier(run_dir: Path, dest: Path, fmap: dict[str, Any]) -> Path:
    problem, sol = _problem(run_dir), _final_solution(run_dir)
    rounds = _rounds(run_dir)
    cost = _read_json(run_dir / "cost.json")
    entries = cost.get("entries", [])
    p: list[str] = [(f"<!doctype html><html><head><meta charset='utf-8'>"
                     f"<title>Dossier — {html.escape(str(problem.get('title', '')))}</title>{STYLE}</head>"
                     f"<body><main>")]
    # J1 input -> output
    p.append(f"<h1>{html.escape(str(problem.get('title', run_dir.name)))}</h1>")
    p.append(f"<p class='small'>Run folder: {html.escape(run_dir.name)} · generated {_ts(run_dir / 'problem.json')}</p>")
    p.append(f"<h2>1. Input → output</h2><p>{html.escape(_prompt_text(problem))}</p>")
    if (dest / "final" / "figure.png").exists():
        p.append("<a href='final/figure.png'><img src='final/figure.png' alt='final figure'></a>")
    p.append(f"<div class='hero'><p class='mech'>{html.escape(str(sol.get('mechanism_sentence', '')))}</p></div>")
    p.append("<h3>Three decisive choices</h3><ol>" + "".join(
        f"<li>{html.escape(str(c))}</li>" for c in sol.get("decisive_choices", [])) + "</ol>")
    p.append(f"<div class='q'><b>Open question:</b> {html.escape(str(sol.get('open_question', '')))}</div>")
    first_render = next((rd for rd in rounds if rd["render"].exists()), None)
    if first_render is not None and rounds:
        p.append("<h3>First render next to the final render</h3>")
        rel_first = "/".join(first_render["render"].parts[len(run_dir.parts):])
        p.append(f"<p><img src='{rel_first}' style='max-width:49%'> "
                 f"<img src='final/panel_A.png' style='max-width:49%'></p>")
    refs = (run_dir / "references.md").read_text(encoding="utf-8") if (run_dir / "references.md").exists() else ""
    p.append("<h3>Reference list</h3><pre style='white-space:pre-wrap'>" + html.escape(refs) + "</pre>")
    # J2 whiteboard over time
    p.append("<h2>2. Whiteboard over time</h2>")
    iters = sorted(run_dir.glob("stage_a/iter_*"))
    for it_dir in iters:
        wb = _read_json(it_dir / "whiteboard.json")
        ev = wb.get("evidence", [])
        sketches = [e for e in ev if e.get("tool") == "sketch"]
        objs = wb.get("objections", [])
        verdict = _read_json(it_dir / "verdict.json")
        p.append(f"<div class='event'><b>{_ts(it_dir)} {it_dir.name}</b> — {len(ev)} evidence items, "
                 f"{len(sketches)} sketches, {len(objs)} objections; evaluator accept = "
                 f"{verdict.get('accept')}. Proposal: {html.escape(str(_read_json(it_dir / 'solution.json').get('title', '')))}. "
                 f"<a href='../board.html'>Board step</a></div>")
    # J3 path overlays
    p.append("<h2>3. Path through the architecture</h2>")
    for idx, _it_dir in enumerate(iters):
        steps = _stage_a_steps(run_dir, idx)
        p.append(f"<h3>Stage A iteration {idx}</h3><div class='overlay'>"
                 + _overlay_svg("fig1_architecture.svg", [s for s, _ in steps], fmap) + "</div>")
        p.append("".join(f"<div class='event'><b>{i}.</b> {html.escape(text)}</div>"
                         for i, (_n, text) in enumerate(steps, 1)))
    for rd in rounds:
        steps = _stage_b_steps(rd)
        p.append(f"<h3>Stage B {rd['name']}</h3><div class='overlay'>"
                 + _overlay_svg("fig1_architecture.svg",
                                [s if s in fmap["fig1_architecture.svg"]["nodes"] else "n-designer-eval"
                                 for s, _ in steps], fmap) + "</div>")
        p.append("<div class='overlay'>" + _overlay_svg(
            "fig2_visualization_pipeline.svg", [s for s, _ in steps], fmap) + "</div>")
        p.append("".join(f"<div class='event'><b>{i}.</b> {html.escape(text)}</div>"
                         for i, (_n, text) in enumerate(steps, 1)))
        for reg in rd["regions"]:
            p.append(f"<div class='event'>Region <b>{html.escape(str(reg.get('part_id')))}</b> "
                     f"(box {reg.get('box')}, source {reg.get('source')}): observed "
                     f"{html.escape(str(reg.get('observed', ''))[:200])} — expected "
                     f"{html.escape(str(reg.get('expected', ''))[:200])}</div>")
    # J4 conformance
    p.append("<h2>4. Conformance table</h2>")
    counts: dict[str, int] = {}
    for idx in range(len(iters)):
        for node, _t in _stage_a_steps(run_dir, idx):
            counts[node] = counts.get(node, 0) + 1
    for rd in rounds:
        for node, _t in _stage_b_steps(rd):
            counts[node] = counts.get(node, 0) + 1
    rows = []
    never: list[str] = []
    for fig in ("fig1_architecture.svg", "fig2_visualization_pipeline.svg"):
        for node in fmap[fig]["nodes"]:
            n = counts.get(node, 0)
            rows.append(f"<tr><td>{fig}</td><td>{node}</td><td>{n}</td></tr>")
            if n == 0:
                never.append(node)
    p.append("<table><tr><th>Figure</th><th>Node</th><th>Times exercised</th></tr>" + "".join(rows) + "</table>")
    p.append("<h3>Figure elements never exercised</h3><p>" + (
        ", ".join(sorted(set(never))) if never else "none") +
        ". Nodes with count 0 were not reached by this run (for example no S2 return, "
        "or the lessons node when no rewrite happened).</p>")
    p.append("<h3>Paths the run took that the figures do not show</h3><p>"
             "The v2 additions run inside the drawn nodes but have no node of their own in the "
             "owner's figures: the VLM prompt gradient and progress check (inside DesignerEval → "
             "VLM writer), the local edit + composite, the speaking/turn check (inside Meeting), "
             "citation resolution into the reference list, and the Manager's new_tool proposals. "
             "This is a figure-versus-implementation difference, reported here as instructed; "
             "the figures were not edited.</p>")
    # J5 self-improvement
    p.append("<h2>5. Self-improvement</h2>")
    revs = sorted((run_dir / "master_prompt").glob("rev_*.md")) if (run_dir / "master_prompt").exists() else []
    p.append(f"<p>Master prompt revisions in this run: {len(revs)}. "
             f"Each applied rewrite is saved as rev_N.md with diff_N.md next to it.</p>")
    for it_dir in iters:
        diag = _read_json(it_dir / "gradient_prompt.json") or _read_json(it_dir / "diagnosis.json")
        if diag:
            p.append(f"<div class='event'><b>{it_dir.name}</b> Manager root cause: "
                     f"{html.escape(str(diag.get('root_cause', ''))[:300])} Agenda: "
                     f"{html.escape(str(diag.get('agenda', ''))[:200])}</div>")
        for rd_name in ("gradient_output.json", "gradient_prompt.json", "rewrite.json"):
            if (it_dir / rd_name).exists():
                p.append(f"<p class='small'>{it_dir.name}/{rd_name} saved.</p>")
    for rd in rounds:
        if rd["fix_mode"]:
            p.append(f"<div class='event'>Stage B {rd['name']}: VLM prompt gradient chose "
                     f"fix_mode={rd['fix_mode']}.</div>")
    lessons = Path("lessons.md")
    if lessons.exists():
        p.append("<p>Lessons file (project level): <a href='../../lessons.md'>lessons.md</a> "
                 "is updated at the end of accepted runs.</p>")
    # J6 cost and wall clock
    p.append("<h2>6. Cost and wall-clock time</h2>")
    by_role: dict[str, dict[str, float]] = {}
    for e in entries:
        r = by_role.setdefault(str(e.get("role")), {"n": 0, "usd": 0.0, "input": 0})
        r["n"] += 1
        r["usd"] += float(e.get("usd", 0))
        r["input"] += int(e.get("input", 0))
    p.append("<table><tr><th>Role</th><th>Calls</th><th>Cost USD</th><th>Input tokens</th></tr>" + "".join(
        f"<tr><td>{html.escape(k)}</td><td>{int(v['n'])}</td><td>{v['usd']:.3f}</td><td>{int(v['input'])}</td></tr>"
        for k, v in sorted(by_role.items(), key=lambda kv: -kv[1]["usd"])) + "</table>")
    total = cost.get("total_usd", 0)
    p.append(f"<p>Total run cost: ${total:.3f} USD across {len(entries)} calls. "
             f"Wall clock: run folder created {_ts(run_dir / 'problem.json')}, "
             f"figure finished {_ts(run_dir / 'final' / 'figure.png') if (run_dir / 'final' / 'figure.png').exists() else 'n/a'}.</p>")
    p.append("<p><a href='report.html'>Full report</a> · <a href='board.html'>Whiteboard replay</a> · "
             "<a href='../index.html'>Showcase index</a></p>")
    p.append("</main></body></html>")
    out_path = dest / "dossier.html"
    out_path.write_text("".join(p), encoding="utf-8")
    return out_path
