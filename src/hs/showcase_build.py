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


ROOT = Path(__file__).resolve().parents[2]


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
                ("schematic", "render", "annotated", "local_", "edited_", "sketch_", "sam_overlay")))
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
    return str(problem.get("statement") or problem.get("prompt") or problem.get("description") or
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
            "attempt": int(rd.parent.name.split("_")[-1]), "round": int(rd.name.split("_")[-1]),
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
    svg_text = (ROOT / "docs" / fig).read_text(encoding="utf-8")
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


def _sentences(text: str, n: int) -> str:
    """The first n sentences, never cut mid-word."""
    parts = re.split(r"(?<=[.!?])\s+", " ".join(str(text).split()))
    return " ".join(parts[:n])


def _archive(run_dir: Path) -> list[dict[str, Any]]:
    path = run_dir / "archive.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


DECISION_WORDS = {
    "s1_pass": "the picture matched the mechanism sketch",
    "s1_retry": "the picture did not match the mechanism sketch, so the image prompt was corrected",
    "s1_exhausted": "the picture could not be drawn faithfully within the round limit; nothing was sent to the design",
    "s2_return": "the designer evaluation saw a design flaw, so the concept went back to the council",
}


def _stage_a_steps(run_dir: Path, it: int) -> list[tuple[str, str]]:
    """(fig1 node, sentence) per Stage A iteration — every sentence read from that iteration's files (A2)."""
    it_dir = run_dir / "stage_a" / f"iter_{it:02d}"
    entry = next((e for e in _archive(run_dir) if int(e.get("iteration", -1)) == it), {})
    steps: list[tuple[str, str]] = []
    rev = entry.get("revision")
    if rev is not None:
        rev_file = run_dir / "master_prompt" / f"rev_{int(rev):03d}.md"
        roster = re.findall(r"^###\s+(.+?)\s*$", rev_file.read_text(encoding="utf-8").split("## 3.")[0],
                            flags=re.MULTILINE) if rev_file.exists() else []
        steps.append(("n-master", f"The council worked from master prompt revision {int(rev)}."))
        if roster:
            steps.append(("n-council", f"{len(roster)} members took part: {', '.join(roster)}."))
    closure, board = _read_json(it_dir / "closure.json"), _read_json(it_dir / "whiteboard.json")
    manager_turns = len(list(it_dir.glob("turns/c*_Manager.json")))
    if manager_turns:
        steps.append(("n-manager-seat", f"The Manager spoke {manager_turns} times, once at the end of each cycle."))
    if closure:
        ev = board.get("evidence", [])
        tools: dict[str, int] = {}
        for e in ev:
            tools[str(e.get("tool", "")).split(":")[0]] = tools.get(str(e.get("tool", "")).split(":")[0], 0) + 1
        objs = board.get("objections", [])
        open_blocking = [o for o in objs if o.get("status") == "open" and o.get("blocking")]
        proposal = board.get("proposal")
        closed = "by consensus" if closure.get("closed_by") == "consensus" else "at the cycle cap without consensus"
        steps.append(("n-meeting", (
            f"The meeting ran {closure.get('cycles_used')} cycles and closed {closed}. The board holds "
            f"{len(ev)} evidence items ({', '.join(f'{n} {t}' for t, n in sorted(tools.items())) or 'none'}), "
            f"{len(objs)} objections ({len(open_blocking)} blocking still open) and "
            + (f"proposal version {proposal.get('version')}." if proposal else "no proposal."))))
    verdict = _read_json(it_dir / "verdict.json")
    if verdict:
        word = "accepted" if verdict.get("accept") else "sent back"
        reqs = len(verdict.get("evidence_requests", []) or [])
        steps.append(("n-evaluator", f"The Evaluator {word} the solution: {_sentences(verdict.get('feedback', ''), 2)}"
                      + (f" It asked the room for {reqs} more pieces of evidence." if reqs else "")))
    edit = _read_json(it_dir / "manager_edit.json")
    if edit:
        changed = edit.get("changed") or []
        steps.append(("n-master", ("The Manager's two-step diagnosis led to a rewrite of " + ", ".join(changed) + "."
                                   if changed else "The Manager's diagnosis changed no section of the master prompt.")))
    if entry:
        status = {"accepted": "accepted", "rejected": "rejected by the Evaluator",
                  "rejected_by_designer": "rejected by the designer evaluation (design flaw)",
                  "could_not_draw": "accepted, but could not be drawn faithfully"}.get(entry.get("status"), entry.get("status"))
        steps.append(("n-council-archive", f"The council archive records this solution as {status}."))
    return steps


def _stage_b_steps(rd: dict[str, Any]) -> list[tuple[str, str]]:
    """(fig2 node, sentence) per Stage B round — read from the round folder (A2)."""
    d: Path = rd["dir"]
    steps: list[tuple[str, str]] = []
    geo = _read_json(d / "schematic.json")
    if geo:
        steps.append(("n-schematic", f"Code drew the mechanism sketch with {len(geo.get('boxes', {}))} parts."))
    vlm = _read_json(d / "vlm_prompt.json")
    if vlm:
        change = _sentences(vlm.get("changes_from_previous", ""), 1)
        steps.append(("n-vlm-writer", "The image prompt was written" + (f": {change}" if change else ".")))
    if rd["render"].exists():
        steps.append(("n-render", "The image model rendered the device from the sketch."))
    loc = _read_json(d / "localization.json")
    if loc:
        parts = loc.get("parts", [])
        found = [x.get("id") for x in parts if x.get("found")]
        missing = [x.get("id") for x in parts if not x.get("found")]
        steps.append(("n-labels", f"Code labelled {len(found)} of {len(parts)} parts"
                      + (f"; not found in the picture: {', '.join(missing)}." if missing else ".")))
    words = DECISION_WORDS.get(rd["decision"], rd["decision"])
    steps.append(("n-designer-eval", f"The designer evaluation named {len(rd['regions'])} regions; {words}."))
    if rd["decision"] == "s2_return":
        steps.append(("n-back-to-a", "The designer's feedback went back to the council."))
    steps.append(("n-image-archive", "The prompt, render and evaluation were stored in the image archive."))
    return steps


INDEX_STYLE = """<style>
body{font-family:'Segoe UI',Helvetica,Arial,sans-serif;background:#0f1216;color:#e8eaed;margin:0}
header{max-width:1240px;margin:0 auto;padding:44px 28px 10px}
header h1{font-size:44px;margin:0;letter-spacing:-.5px}
header p{font-size:19px;color:#b8c0cc;max-width:900px;line-height:1.5}
.flow{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 6px}
.flow span{background:#1d232b;border:1px solid #2f3a46;border-radius:20px;padding:6px 14px;font-size:14px;color:#cfd6df}
.flow b{color:#7cc4ff}
.card{max-width:1240px;margin:28px auto;background:#171b21;border:1px solid #262d36;border-radius:18px;overflow:hidden}
.top{display:grid;grid-template-columns:1.35fr 1fr;align-items:start}
.top img{width:100%;height:auto;display:block}
.text{padding:26px 28px}
.text h2{font-size:28px;margin:0 0 8px;line-height:1.2}
.prob{color:#9aa4b1;font-size:15px;line-height:1.5}
.mech{font-size:19px;line-height:1.5;margin:14px 0;color:#fff}
.stats{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.stats span{background:#0f1216;border:1px solid #2f3a46;border-radius:10px;padding:6px 10px;font-size:13px}
.stats b{display:block;font-size:20px;color:#7cc4ff}
ol{padding-left:20px;font-size:15px;line-height:1.55}
.q{border-left:4px solid #f0b429;background:#1f1a0e;padding:10px 14px;font-size:15px;border-radius:6px}
.strip{display:grid;grid-template-columns:repeat(4,1fr);gap:2px;background:#262d36}
.strip a{position:relative;display:block;background:#0f1216}
.strip img{width:100%;height:220px;object-fit:cover;object-position:top;display:block}
.strip span{position:absolute;left:8px;top:8px;background:rgba(0,0,0,.78);color:#fff;padding:4px 9px;border-radius:8px;font-size:13px}
.links{padding:14px 28px;font-size:15px}.links a{color:#7cc4ff;margin-right:18px}
@media (max-width:900px){.top{grid-template-columns:1fr}.strip{grid-template-columns:repeat(2,1fr)}}
</style>"""


def _stats(run_dir: Path) -> list[tuple[str, str]]:
    """Numbers for the index card, read from the run's files."""
    revs = sorted((run_dir / "master_prompt").glob("rev_*.md")) if (run_dir / "master_prompt").exists() else []
    roster = re.findall(r"^###\s+(.+?)\s*$", revs[0].read_text(encoding="utf-8").split("## 3.")[0],
                        flags=re.MULTILINE) if revs else []
    iters = sorted(run_dir.glob("stage_a/iter_*"))
    ev = [e for it in iters for e in _read_json(it / "whiteboard.json").get("evidence", [])]
    count = {t: sum(1 for e in ev if str(e.get("tool", "")).split(":")[0] in t) for t in
             (("web_search",), ("calc", "vetted_calc", "simulate"), ("sketch",))}
    closure = _read_json(iters[-1] / "closure.json") if iters else {}
    verdict = _read_json(iters[-1] / "verdict.json") if iters else {}
    rounds = len(list(run_dir.glob("stage_b/attempt_*/round_*/eval.json")))
    cost = float(_read_json(run_dir / "cost.json").get("total_usd", 0))
    out = [(str(len(roster)), "expert members"), (str(count[("web_search",)]), "sources found"),
           (str(count[("calc", "vetted_calc", "simulate")]), "calculations"), (str(count[("sketch",)]), "sketches")]
    if closure:
        out.append((f"{closure.get('cycles_used')} cycles",
                    "consensus" if closure.get("closed_by") == "consensus" else "cycle cap"))
    if verdict:
        out.append(("accepted" if verdict.get("accept") else "sent back", f"meeting {len(iters)}"))
    out += [(str(rounds), "picture rounds"), (f"${cost:.2f}", "Meta API cost")]
    return out


def build_showcase(run_dirs: list[Path], out: Path = ROOT / "showcase") -> Path:
    fmap = json.loads((ROOT / "docs" / "figures_map.json").read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    cards: list[str] = []
    for run_dir in run_dirs:
        slug = _slug(run_dir)
        dest = out / slug
        copy_run(run_dir, dest)
        _dossier(run_dir, dest, fmap)
        problem, sol = _problem(run_dir), _final_solution(run_dir)
        sketches = sorted(dest.glob("stage_a/iter_*/evidence/sketch_*.png"),
                          key=lambda q: int(q.stem.split("_")[-1]) if q.stem.split("_")[-1].isdigit() else 0)
        overlays = sorted(dest.glob("stage_b/attempt_*/round_*/sam_overlay.png"))
        thumbs = [(sketches[-1] if sketches else None, "The council's own sketch"),
                  (overlays[-1] if overlays else None, "What SAM 3.1 saw"),
                  (dest / "final" / "panel_B.png", "Critical part"),
                  (dest / "final" / "panel_D.png", "How it is made")]
        strip = "".join(f"<a href='{slug}/{t.relative_to(dest).as_posix()}'><img src='{slug}/{t.relative_to(dest).as_posix()}'>"
                        f"<span>{html.escape(cap)}</span></a>" for t, cap in thumbs if t is not None and t.exists())
        stats = "".join(f"<span><b>{html.escape(v)}</b>{html.escape(k)}</span>" for v, k in _stats(run_dir))
        choices = "".join(f"<li>{html.escape(str(c))}</li>" for c in sol.get("decisive_choices", []))
        hero = f"{slug}/final/panel_A.png" if (dest / "final" / "panel_A.png").exists() else ""
        cards.append(f"""<section class="card"><div class="top">
<a href="{slug}/final/figure.png">{f'<img src="{hero}" alt="the concept">' if hero else ''}</a>
<div class="text"><h2>{html.escape(str(problem.get('title', slug)))}</h2>
<p class="prob">{html.escape(_prompt_text(problem))}</p>
<p class="mech">{html.escape(str(sol.get('mechanism_sentence', '')))}</p>
<div class="stats">{stats}</div>
<ol>{choices}</ol>
<div class="q"><b>Open question:</b> {html.escape(str(sol.get('open_question', '')))}</div></div></div>
<div class="strip">{strip}</div>
<div class="links"><a href="{slug}/final/figure.png">Full figure</a><a href="{slug}/board.html">The council's whiteboard</a>
<a href="{slug}/report.html">Report</a><a href="{slug}/dossier.html">Dossier</a><a href="{slug}/REVIEW.md">Review</a></div></section>""")
    (out / "index.html").write_text(
        "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
        f"<title>Hardware Scientist</title>{INDEX_STYLE}</head><body><header><h1>Hardware Scientist</h1>"
        "<p>Give it a hardware problem in plain words. A council of AI engineers searches the literature, computes "
        "and sketches on a shared whiteboard; an evaluator judges the concept; a manager coaches the council when "
        "it fails. Then the accepted concept is drawn, measured by SAM 3.1, critiqued and redrawn until the picture "
        "matches the design. All models: Meta Muse Spark, Muse Image and SAM 3.1.</p>"
        "<div class='flow'><span><b>1</b> problem</span><span><b>2</b> council on a whiteboard</span>"
        "<span><b>3</b> evaluator</span><span><b>4</b> manager rewrites the council's prompt</span>"
        "<span><b>5</b> mechanism sketch → render</span><span><b>6</b> SAM + critic → keep or revert</span>"
        "<span><b>7</b> concept figure</span></div></header>" + "".join(cards) + "</body></html>", encoding="utf-8")
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
    # 2. Whiteboard over time (facts per iteration)
    p.append("<h2>2. Whiteboard over time</h2>")
    iters = sorted(run_dir.glob("stage_a/iter_*"))
    seeded = _read_json(run_dir / "seeded_from.json")
    if seeded:
        p.append(f"<p>No council meeting ran in this run: it redrew the accepted solution of run "
                 f"{html.escape(str(seeded.get('source_run', '')))}.</p>")
    for it_dir in iters:
        wb = _read_json(it_dir / "whiteboard.json")
        if not wb:
            continue
        ev = wb.get("evidence", [])
        sketches = [e for e in ev if e.get("tool") == "sketch"]
        proposal = wb.get("proposal")
        verdict = _read_json(it_dir / "verdict.json")
        verdict_words = ("The Evaluator accepted it." if verdict.get("accept") else "The Evaluator sent it back.") \
            if verdict else ""
        p.append(f"<div class='event'><b>Meeting {int(it_dir.name.split('_')[-1]) + 1}</b>: {len(ev)} evidence items, "
                 f"{len(sketches)} sketches, {len(wb.get('objections', []))} objections. "
                 + (f"Proposal: {html.escape(_sentences(proposal.get('text', ''), 1))} " if proposal else "No proposal. ")
                 + f"{verdict_words} <a href='board.html'>Open the board</a></div>")
    # 3. Path through the architecture: one overlay per stage (D22), sentences from the files (A2)
    p.append("<h2>3. Path through the architecture</h2>")
    a_steps = [_stage_a_steps(run_dir, int(it.name.split("_")[-1])) for it in iters]
    if a_steps:
        path_nodes = list(dict.fromkeys(n for steps in a_steps for n, _ in steps))
        p.append("<h3>Stage A</h3><div class='overlay'>"
                 + _overlay_svg("fig1_architecture.svg", path_nodes, fmap) + "</div>")
        for idx, steps in enumerate(a_steps):
            p.append(f"<h4>Meeting {idx + 1}</h4>" + "".join(
                f"<div class='event'>{html.escape(text)}</div>" for _n, text in steps))
    if rounds:
        b_steps = [_stage_b_steps(rd) for rd in rounds]
        path_nodes = list(dict.fromkeys(n for steps in b_steps for n, _ in steps))
        p.append("<h3>Stage B</h3><div class='overlay'>"
                 + _overlay_svg("fig2_visualization_pipeline.svg", path_nodes, fmap) + "</div>")
        for rd, steps in zip(rounds, b_steps, strict=True):
            p.append(f"<h4>Picture {rd['attempt'] + 1}, round {rd['round'] + 1}</h4>" + "".join(
                f"<div class='event'>{html.escape(text)}</div>" for _n, text in steps))
            for reg in rd["regions"]:
                p.append(f"<div class='event small'>Region on {html.escape(str(reg.get('part_id')))}: observed "
                         f"{html.escape(str(reg.get('observed', '')))} — expected "
                         f"{html.escape(str(reg.get('expected', '')))}</div>")
    # 4. What ran and what did not (prose, from the files; replaces the conformance table)
    p.append("<h2>4. What ran and what did not</h2>")
    archive = _archive(run_dir)
    edits = [it for it in iters if (it / "manager_edit.json").exists()]
    decisions = [rd["decision"] for rd in rounds]
    ran = []
    if archive:
        ran.append(f"The council met {len(archive)} times and the Manager diagnosed {len(edits)} failures")
    if rounds:
        ran.append(f"the picture loop ran {len(rounds)} rounds")
    not_ran = []
    if "s2_return" not in decisions:
        not_ran.append("no picture sent the design back to the council")
    if not any(rd["progress"] for rd in rounds):
        not_ran.append("no local repair of a picture region was attempted")
    if not any(it.glob("rewrite*.json") for it in iters):
        not_ran.append("no master prompt rewrite happened")
    p.append("<p>" + html.escape(("; ".join(ran) + ". ") if ran else "")
             + html.escape(("In this run " + "; ".join(not_ran) + ".") if not_ran else "") + "</p>")
    # 5. Self-improvement (facts)
    p.append("<h2>5. Self-improvement</h2>")
    revs = sorted((run_dir / "master_prompt").glob("rev_*.md")) if (run_dir / "master_prompt").exists() else []
    p.append(f"<p>The master prompt has {len(revs)} saved revisions in this run"
             + (" (revision 0 plus one per applied rewrite)." if revs else ".") + "</p>")
    for it_dir in iters:
        diag = _read_json(it_dir / "gradient_prompt.json") or _read_json(it_dir / "diagnosis.json")
        if diag:
            p.append(f"<div class='event'><b>Meeting {int(it_dir.name.split('_')[-1]) + 1}</b> — the Manager's "
                     f"root cause: {html.escape(_sentences(diag.get('root_cause', ''), 2))}"
                     + (f" Agenda: {html.escape(_sentences(diag.get('agenda', ''), 2))}" if diag.get("agenda") else "")
                     + "</div>")
    lessons_file = ROOT / "lessons.md"
    added = [line for line in lessons_file.read_text(encoding="utf-8").splitlines()
             if f"run {run_dir.name}]" in line] if lessons_file.exists() else []
    p.append("<p>Lessons this run added to lessons.md: " + (
        "</p><ul>" + "".join(f"<li>{html.escape(line.lstrip('- '))}</li>" for line in added) + "</ul>"
        if added else "none.</p>"))
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
