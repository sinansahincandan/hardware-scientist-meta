"""The committee page (`showcase/story.html`): one problem followed from input to figure through both loops of the
owner's figures, then every problem, what carried over between them, and the output files. Every sentence and
picture is read from the showcase copies of the runs (showcase/<slug>/); nothing is written by hand here except
headings and the one-line explanations of what a step is."""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from hs.board_picture import PICTURE_STYLE, board_picture_html
from hs.showcase_build import ROOT, _read_json, _sentences, _stats

STYLE = """<style>
:root{--bg:#0b0e13;--panel:#141922;--line:#263040;--ink:#e8edf4;--mute:#9aa7b8;--acc:#5eb3ff;--red:#ff6b6b;
  --grn:#4cd68a;--amb:#ffc857}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 -apple-system,
  'Segoe UI',Inter,Helvetica,Arial,sans-serif}
a{color:var(--acc)}.wrap{max-width:1240px;margin:0 auto;padding:0 28px}
header.hero{padding:70px 0 40px;background:radial-gradient(1200px 500px at 20% -10%,#1d3557 0,transparent 60%),
  radial-gradient(900px 400px at 90% 0,#3a1d57 0,transparent 55%)}
.hero h1{font-size:58px;line-height:1.05;margin:0 0 16px;letter-spacing:-1px}
.hero p.lead{font-size:22px;color:#c9d4e3;max-width:900px;margin:0 0 26px}
.chips span{display:inline-block;border:1px solid var(--line);background:#111722;border-radius:99px;padding:6px 14px;
  margin:0 8px 8px 0;font-size:14px;color:#cbd6e6}
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-top:26px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.kpi b{display:block;font-size:30px;color:var(--acc);line-height:1.1}.kpi span{font-size:13px;color:var(--mute)}
section{padding:46px 0;border-top:1px solid #182030}
h2{font-size:34px;margin:0 0 8px;letter-spacing:-.5px}h2+p.sub{color:var(--mute);margin:0 0 26px;font-size:18px}
h3{font-size:22px;margin:0 0 10px}
.io{display:grid;grid-template-columns:1fr 1.4fr;gap:22px;align-items:start}
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px 22px}
.card.input{border-left:5px solid var(--acc)}.card .k{font-size:12px;text-transform:uppercase;letter-spacing:1.5px;
  color:var(--mute);margin-bottom:6px}
.card ul{margin:8px 0 0 18px;padding:0}
img.big{width:100%;border-radius:14px;border:1px solid var(--line);display:block}
.timeline{position:relative;margin-left:22px;border-left:3px solid var(--line);padding-left:34px}
.step{position:relative;margin:0 0 34px}
.step .dot{position:absolute;left:-55px;top:2px;width:38px;height:38px;border-radius:50%;display:flex;
  align-items:center;justify-content:center;font-weight:700;font-size:16px;color:#0b0e13}
.step.a .dot{background:var(--acc)}.step.r .dot{background:var(--red)}.step.g .dot{background:var(--grn)}
.step.m .dot{background:var(--amb)}
.step h3 small{font-weight:400;color:var(--mute);font-size:15px;margin-left:8px}
.quote{border-left:4px solid var(--red);background:#1a1416;padding:12px 16px;border-radius:0 10px 10px 0;margin:10px 0}
.quote.ok{border-color:var(--grn);background:#121a15}
.diff{font:13.5px/1.5 ui-monospace,Menlo,monospace;background:#0f131a;border:1px solid var(--line);border-radius:10px;
  padding:12px 14px;white-space:pre-wrap}
.diff .del{color:#ff9b9b;text-decoration:line-through}.diff .add{color:#8ff0b5}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}.trio{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
figure{margin:0}figcaption{font-size:14px;color:var(--mute);margin-top:6px}
.wbwrap{background:#e9edf2;border-radius:16px;padding:6px 10px;color:#222}
.decisions li{margin-bottom:6px}.tag{display:inline-block;font-size:12px;border-radius:6px;padding:1px 7px;margin-right:6px;
  background:#20324a;color:#bfe0ff}
.problems{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.prob img{width:100%;height:260px;object-fit:cover;object-position:top;border-radius:12px;display:block}
.prob h3{margin:14px 0 6px}.prob p{margin:0 0 10px;color:#c9d4e3}
.loops span{display:inline-block;font-size:13px;border-radius:99px;padding:3px 10px;margin:0 6px 6px 0;
  border:1px solid var(--line)}.loops .on{background:#13301f;border-color:#2f7a4f;color:#9ff0c0}
.loops .off{color:#7b8797}
.know{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.know .card{padding:14px}.know b{color:var(--amb)}
.figs{display:grid;grid-template-columns:1fr 1fr;gap:16px}.figs .card{padding:10px;background:#fff}
.files code{font-size:13.5px;color:#cfe3ff}
footer{padding:40px 0 70px;color:var(--mute);font-size:14px}
</style>"""


def _e(x: Any) -> str:
    return html.escape(str(x))


def _rel(path: Path, out: Path) -> str:
    return path.relative_to(out).as_posix()


def _verdict(it_dir: Path) -> dict[str, Any]:
    return _read_json(it_dir / "verdict.json")


def _first_rejection(dest: Path) -> int | None:
    for it_dir in sorted(dest.glob("stage_a/iter_*")):
        v = _verdict(it_dir)
        if v and not v.get("accept"):
            return int(it_dir.name.split("_")[-1])
    return None


def _diff_excerpt(dest: Path, rev: int, max_lines: int = 8) -> str:
    """A few red/green lines from the master prompt diff (the role whose wording changed most)."""
    path = dest / "master_prompt" / f"diff_{rev:03d}.md"
    if not path.exists():
        return ""
    reds = re.findall(r"<red>- (.*?)</red>", path.read_text(encoding="utf-8"))
    greens = re.findall(r"<green>\+ (.*?)</green>", path.read_text(encoding="utf-8"))
    pairs = [(r, g) for r, g in zip(reds, greens, strict=False) if g and len(g) > len(r) + 40][:max_lines // 2]
    rows = []
    for r, g in pairs:
        rows.append(f"<span class='del'>{_e(r)}</span>\n<span class='add'>{_e(g)}</span>")
    return "<div class='diff'>" + "\n\n".join(rows) + "</div>" if rows else ""


def _members(board: dict[str, Any]) -> list[str]:
    names = list(dict.fromkeys([*board.get("votes", {}), *(c.get("author") for c in board.get("concepts", []))]))
    return [m for m in names if m and m != "Manager"]


def _boxed_render(rd: Path, assets: Path, name: str) -> Path | None:
    """The round's render with the critic's regions drawn in red (code only)."""
    ev = _read_json(rd / "eval.json")
    src = rd / "render.png"
    if not src.exists():
        return None
    img = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(img)
    for r in ev.get("regions", []):
        b = r.get("box") or []
        if len(b) == 4:
            x0, y0, x1, y1 = (b[0] / 1000 * img.width, b[1] / 1000 * img.height, b[2] / 1000 * img.width,
                              b[3] / 1000 * img.height)
            pad = 30
            d.ellipse([x0 - pad, y0 - pad, x1 + pad, y1 + pad], outline=(255, 70, 70), width=8)
    img.thumbnail((1400, 1400))
    out = assets / f"{name}.jpg"
    img.save(out, quality=86)
    return out


def _loops(dest: Path) -> list[tuple[str, bool]]:
    iters = sorted(dest.glob("stage_a/iter_*"))
    rejected = any(_verdict(i) and not _verdict(i).get("accept") for i in iters)
    rewrote = any(_read_json(i / "manager_edit.json").get("changed") for i in iters)
    rounds = sorted(dest.glob("stage_b/attempt_*/round_*"))
    local = any((r / "vlm_gradient.json").exists() for r in rounds)
    notes = (dest / "final" / "rationale.md").read_text(encoding="utf-8") if (dest / "final" / "rationale.md").exists() else ""
    searched = any(e.get("tool") == "search_knowledge" for i in iters
                   for e in _read_json(i / "whiteboard.json").get("evidence", []))
    return [("Evaluator rejected", rejected), ("Manager rewrote the prompt", rewrote),
            ("picture redrawn after critique", len(rounds) > 1 or local),
            ("wrong labels replaced", "pointed at the wrong part" in notes),
            ("knowledge library searched", searched), ("concept sketch", bool(list(dest.glob("stage_b/attempt_*/concept_sketch.png"))))]


def loop_map(dest: Path) -> str:
    """Both loops as one diagram (code-drawn SVG): Stage A on top, Stage B below; a box is lit with its count when
    the run's files show it ran, and the two feedback arrows are lit when they fired."""
    iters = sorted(dest.glob("stage_a/iter_*"))
    rounds = sorted(dest.glob("stage_b/attempt_*/round_*"))
    rejects = sum(1 for i in iters if _verdict(i) and not _verdict(i).get("accept"))
    rewrites = sum(1 for i in iters if _read_json(i / "manager_edit.json").get("changed"))
    searches = sum(1 for i in iters for e in _read_json(i / "whiteboard.json").get("evidence", []) if e.get("tool") == "web_search")
    fixes = sum(1 for r in rounds if (r / "vlm_gradient.json").exists())
    concept = bool(list(dest.glob("stage_b/attempt_*/concept_sketch.png")))
    k_in = _read_json(dest / "knowledge_in.json")
    boxes = [  # (x, y, title, detail, count or flag)
        (20, 40, "Problem", "plain words + constraints", 1),
        (200, 40, "knowledge/", f"{len(k_in.get('lessons', []))} lessons in", len(k_in.get("lessons", []))),
        (380, 40, "Master prompt", f"{len(iters)} revision{'s' if len(iters) != 1 else ''}", len(iters)),
        (560, 40, "Council meeting", f"{searches} search results", len(iters)),
        (740, 40, "Evaluator", f"{rejects} rejected", len(iters)),
        (920, 40, "Accepted", "solution prompt", 1 if iters and _verdict(iters[-1]).get("accept") else 0),
        (560, 170, "Manager gradient", "diagnosis + rewrite", rewrites),
        (20, 330, "Concept sketch", "from council sketches", int(concept)),
        (200, 330, "Render", "image model", len(rounds)),
        (380, 330, "SAM 3.1", "masks + judge", len(rounds)),
        (560, 330, "Critic S1/S2", "regions, keep/revert", len(rounds)),
        (740, 330, "Figure", "panels A–D", int((dest / "final" / "figure.png").exists())),
        (920, 330, "knowledge/", "lessons + findings out", 1),
        (380, 460, "Local fix", "region redrawn", fixes),
    ]
    svg = [("<svg viewBox='0 0 1100 540' width='100%' xmlns='http://www.w3.org/2000/svg' "
            "style='background:#0f141c;border:1px solid #263040;border-radius:16px'>"),
           ("<defs><marker id='ah' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' "
           "orient='auto-start-reverse'><path d='M0,0 L10,5 L0,10 z' fill='#5eb3ff'/></marker>"
           "<marker id='ar' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' "
           "orient='auto-start-reverse'><path d='M0,0 L10,5 L0,10 z' fill='#ff6b6b'/></marker></defs>"),
           "<text x='20' y='26' fill='#9aa7b8' font-size='14' font-family='sans-serif'>STAGE A · DESIGN</text>",
           "<text x='120' y='310' fill='#9aa7b8' font-size='14' font-family='sans-serif'>STAGE B · PICTURE</text>"]
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12)]:
        x0, y0 = boxes[a][0] + 160, boxes[a][1] + 40
        svg.append(f"<line x1='{x0}' y1='{y0}' x2='{boxes[b][0]}' y2='{boxes[b][1] + 40}' stroke='#5eb3ff' "
                   "stroke-width='2.5' marker-end='url(#ah)'/>")
    svg.append("<path d='M1000,120 L1000,288 L100,288 L100,328' stroke='#5eb3ff' stroke-width='2.5' fill='none' "
               "marker-end='url(#ah)'/>")
    col = "#ff6b6b" if rejects else "#3a4556"
    svg.append(f"<path d='M820,120 L820,210 L720,210' stroke='{col}' stroke-width='3' fill='none' marker-end='url(#ar)'/>"
               f"<path d='M560,210 L460,210 L460,122' stroke='{col}' stroke-width='3' fill='none' marker-end='url(#ar)'/>"
               f"<text x='828' y='170' fill='{col}' font-size='13' font-family='sans-serif'>reject</text>")
    col = "#ff6b6b" if fixes else "#3a4556"
    svg.append(f"<path d='M640,410 L640,500 L542,500' stroke='{col}' stroke-width='3' fill='none' marker-end='url(#ar)'/>"
               f"<path d='M380,500 L280,500 L280,412' stroke='{col}' stroke-width='3' fill='none' marker-end='url(#ar)'/>"
               f"<text x='648' y='460' fill='{col}' font-size='13' font-family='sans-serif'>not faithful</text>")
    for x, y, title, detail, count in boxes:
        on = bool(count)
        svg.append(f"<rect x='{x}' y='{y}' width='160' height='80' rx='12' fill='{'#13304d' if on else '#151b25'}' "
                   f"stroke='{'#5eb3ff' if on else '#2a3444'}' stroke-width='{2.5 if on else 1.5}'/>"
                   f"<text x='{x + 12}' y='{y + 30}' fill='{'#e8edf4' if on else '#5d6878'}' font-size='16' "
                   f"font-weight='700' font-family='sans-serif'>{_e(title)}</text>"
                   f"<text x='{x + 12}' y='{y + 54}' fill='{'#9fc6ea' if on else '#4d5767'}' font-size='13' "
                   f"font-family='sans-serif'>{_e(detail)}</text>")
        if on and count > 1:
            svg.append(f"<circle cx='{x + 148}' cy='{y + 4}' r='15' fill='#ffc857'/><text x='{x + 148}' y='{y + 9}' "
                       f"text-anchor='middle' font-size='14' font-weight='700' font-family='sans-serif' "
                       f"fill='#111'>×{count if count < 100 else '99+'}</text>")
    svg.append("</svg>")
    return "".join(svg)


def build_story(slugs: list[str], out: Path = ROOT / "showcase") -> Path:
    dests = [out / s for s in slugs if (out / s).exists()]
    assets = out / "story_assets"
    assets.mkdir(parents=True, exist_ok=True)
    hero = next((d for d in dests if _first_rejection(d) is not None), dests[0])
    totals = {"sources": 0, "calcs": 0, "meetings": 0, "rounds": 0, "cost": 0.0}
    for d in dests:
        for it in d.glob("stage_a/iter_*"):
            ev = _read_json(it / "whiteboard.json").get("evidence", [])
            totals["meetings"] += 1
            totals["sources"] += sum(1 for e in ev if e.get("tool") == "web_search")
            totals["calcs"] += sum(1 for e in ev if str(e.get("tool", "")).split(":")[0] in ("calc", "vetted_calc", "simulate"))
        totals["rounds"] += len(list(d.glob("stage_b/attempt_*/round_*")))
        totals["cost"] += float(_read_json(d / "cost.json").get("total_usd", 0.0))
    p: list[str] = [("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
                     f"<title>Hardware Scientist — how it works</title>{STYLE}{PICTURE_STYLE}</head><body>")]
    p.append("<header class='hero'><div class='wrap'><h1>Hardware Scientist</h1>"
             "<p class='lead'>A council of AI engineers designs hardware from a plain-language problem. They search "
             "the literature, calculate and sketch on a shared whiteboard; an Evaluator judges the concept; when it "
             "fails, a Manager diagnoses why and rewrites the council's own instructions. The accepted concept is "
             "drawn, measured by SAM and critiqued until the picture matches the design — and what each problem "
             "teaches is kept for the next.</p>"
             "<div class='chips'><span>Muse Spark 1.3 — council, Manager, Evaluator, critic</span>"
             "<span>Muse Image 1.0 — sketches, renders, making steps</span><span>SAM 3.1 — part masks</span>"
             "<span>Meta Model API only</span></div>"
             f"<div class='kpis'><div class='kpi'><b>{len(dests)}</b><span>design problems</span></div>"
             f"<div class='kpi'><b>{totals['meetings']}</b><span>council meetings</span></div>"
             f"<div class='kpi'><b>{totals['sources']}</b><span>search results on the whiteboards</span></div>"
             f"<div class='kpi'><b>{totals['calcs']}</b><span>calculations & simulations</span></div>"
             f"<div class='kpi'><b>{totals['rounds']}</b><span>picture rounds</span></div>"
             f"<div class='kpi'><b>${totals['cost']:.2f}</b><span>Meta API cost, all problems</span></div></div>"
             "</div></header>")

    # -- one problem, start to finish --
    prob = _read_json(hero / "problem.json")
    iters = sorted(hero.glob("stage_a/iter_*"))
    p.append("<section><div class='wrap'><h2>One problem, start to finish</h2>"
             "<p class='sub'>Both self-correction loops of the architecture, as they ran — every quote below is "
             "from the run's own files.</p>")
    p.append(f"<div class='io'><div class='card input'><div class='k'>Input — written by an engineer</div>"
             f"<h3>{_e(prob.get('title'))}</h3><p>{_e(prob.get('statement'))}</p><ul>"
             + "".join(f"<li>{_e(c)}</li>" for c in prob.get("constraints", [])) + "</ul></div>"
             f"<figure><img class='big' src='{_rel(hero / 'final' / 'figure.png', out)}'>"
             f"<figcaption>Output — the concept figure the system produced.</figcaption></figure></div>")
    p.append("<div class='timeline' style='margin-top:40px'>")
    n = 0
    for it_dir in iters:
        it = int(it_dir.name.split("_")[-1])
        board = _read_json(it_dir / "whiteboard.json")
        closure = _read_json(it_dir / "closure.json")
        n += 1
        ready = sum(1 for v in board.get("votes", {}).values() if v.get("ready"))
        p.append(f"<div class='step a'><div class='dot'>{n}</div><h3>Council meeting {it + 1}"
                 f"<small>{closure.get('cycles_used')} rounds · {len(board.get('evidence', []))} evidence items · "
                 f"{ready} of {len(board.get('votes', {}))} members ready"
                 + (f" · {n_open} blocking objection{'s' if n_open != 1 else ''} still open" if (n_open := sum(
                     1 for o in board.get('objections', []) if o.get('blocking') and o.get('status') != 'resolved')) else "")
                 + "</small></h3>"
                 f"<div class='wbwrap'>{board_picture_html(board, out, it_dir, _members(board), str(prob.get('title', '')), int(closure.get('cycles_used') or 0), 4)}</div></div>")
        v = _verdict(it_dir)
        if v:
            n += 1
            ok = bool(v.get("accept"))
            p.append(f"<div class='step {'g' if ok else 'r'}'><div class='dot'>{n}</div><h3>Evaluator "
                     f"{'accepts' if ok else 'rejects'}<small>re-derives the numbers itself, constraint by "
                     f"constraint</small></h3><div class='quote {'ok' if ok else ''}'>"
                     f"{_e(_sentences(v.get('constraint_review', '') or v.get('feedback', ''), 3))}</div>"
                     + ("" if ok else f"<p>{_e(_sentences(v.get('feedback', ''), 3))}</p>") + "</div>")
        g = _read_json(it_dir / "gradient_prompt.json")
        edit = _read_json(it_dir / "manager_edit.json")
        if g or edit:
            n += 1
            decisions = g.get("feedback_decisions", [])[:4]
            p.append(f"<div class='step m'><div class='dot'>{n}</div><h3>Manager diagnoses and rewrites the "
                     f"council's prompt<small>two-step textual gradient</small></h3>"
                     f"<p><b>Root cause:</b> {_e(_sentences(g.get('root_cause', ''), 2))}</p><ul class='decisions'>"
                     + "".join(f"<li><span class='tag'>{_e(d.get('decision'))}</span>{_e(_sentences(d.get('feedback_item', ''), 1))}</li>"
                               for d in decisions) + "</ul>"
                     f"<p><b>Rewritten sections:</b> {_e(', '.join(edit.get('changed') or []) or 'none')}</p>"
                     + _diff_excerpt(hero, it + 1) + "</div>")
    # Stage B
    concept = sorted(hero.glob("stage_b/attempt_*/concept_sketch.png"))
    sketches = sorted(hero.glob("stage_a/iter_*/evidence/sketch_*.png"),
                      key=lambda q: int(q.stem.split("_")[-1]) if q.stem.split("_")[-1].isdigit() else 0)
    if concept:
        n += 1
        p.append(f"<div class='step a'><div class='dot'>{n}</div><h3>From the council's sketch to a concept sketch"
                 f"<small>the image model redraws the engineers' own sketch</small></h3><div class='pair'>"
                 + (f"<figure><img class='big' src='{_rel(sketches[-1], out)}' style='background:#fff'><figcaption>A council "
                    f"member's sketch on the whiteboard.</figcaption></figure>" if sketches else "")
                 + f"<figure><img class='big' src='{_rel(concept[-1], out)}'><figcaption>Concept sketch, checked "
                 f"against the parts list.</figcaption></figure></div></div>")
    rounds = sorted(hero.glob("stage_b/attempt_*/round_*"))
    for k, rd in enumerate(rounds):
        ev = _read_json(rd / "eval.json")
        n += 1
        boxed = _boxed_render(rd, assets, f"{hero.name}_{rd.parent.name}_{rd.name}")
        faithful = bool(ev.get("s1_faithful"))
        regions = ev.get("regions", [])
        prev = ev.get("previous_regions", [])
        grad = _read_json(rd / "vlm_gradient.json")
        p.append(f"<div class='step {'g' if faithful else 'r'}'><div class='dot'>{n}</div><h3>Picture round {k + 1}: "
                 f"critic says {'faithful' if faithful else 'not faithful'}<small>"
                 + ("fault regions circled in red" if regions else "nothing to fix") + "</small></h3>"
                 + (f"<img class='big' src='{_rel(boxed, out)}'>" if boxed else "")
                 + "".join(f"<div class='quote'>{_e(r.get('part_id'))}: {_e(r.get('observed'))} — expected "
                           f"{_e(r.get('expected'))}</div>" for r in regions[:3])
                 + "".join(f"<div class='quote ok'>earlier fault on {_e(x.get('part_id'))}: {_e(x.get('status'))}"
                           f"{(' — ' + _e(_sentences(ev.get('comparison_with_previous', ''), 1))) if ev.get('comparison_with_previous') else ''}</div>"
                           for x in prev[:2])
                 + (f"<p>The image-prompt gradient chose a <b>{_e(grad.get('fix_mode'))}</b> fix: only the faulty "
                    f"region is redrawn, then the same fault is checked again.</p>" if grad.get("fix_mode") else "")
                 + "</div>")
    sam = sorted(hero.glob("stage_b/attempt_*/round_*/sam_overlay.png"))
    if sam:
        n += 1
        p.append(f"<div class='step a'><div class='dot'>{n}</div><h3>SAM 3.1 measures the parts<small>each part's "
                 f"mask in its colour; the measurements go to the critic as evidence</small></h3>"
                 f"<img class='big' src='{_rel(sam[-1], out)}'></div>")
    n += 1
    p.append(f"<div class='step g'><div class='dot'>{n}</div><h3>Concept figure<small>labelled view, critical part, "
             f"measurement chain, how it is made</small></h3><img class='big' src='{_rel(hero / 'final' / 'figure.png', out)}'></div>")
    p.append("</div>")
    review = (hero / "REVIEW.md").read_text(encoding="utf-8") if (hero / "REVIEW.md").exists() else ""
    m = re.search(r"## Comparison with real designs.*?\n(.+?)(?:\n## |\Z)", review, flags=re.DOTALL)
    if m:
        p.append(f"<div class='card' style='margin-top:10px'><div class='k'>Compared with what real teams built "
                 f"(never shown to the system)</div><p>{_e(' '.join(m.group(1).split()))}</p></div>")
    p.append("<h3 style='margin-top:36px'>The path it took through the architecture</h3>"
             "<p class='sub' style='color:var(--mute)'>Lit boxes ran in this problem; numbers say how often. Drawn from "
             "the run's files, after the owner's architecture figures (<a href='../docs/fig1_architecture.svg'>Fig. 1"
             "</a>, <a href='../docs/fig2_visualization_pipeline.svg'>Fig. 2</a>).</p>" + loop_map(hero) + "</div></section>")
    # -- every problem --
    p.append("<section><div class='wrap'><h2>Every problem</h2><p class='sub'>Input in plain words, output as a "
             "concept figure, and which loops fired.</p><div class='problems'>")
    for d in dests:
        pr = _read_json(d / "problem.json")
        sols = list(d.glob("stage_a/iter_*/solution.json"))
        sol = _read_json(max(sols)) if sols else {}
        stats = {k: v for v, k in _stats(d)}
        p.append(f"<div class='card prob'><a href='{d.name}/dossier.html'><img src='{d.name}/final/panel_A.png'></a>"
                 f"<h3>{_e(pr.get('title'))}</h3><p><b>In:</b> {_e(_sentences(pr.get('statement', ''), 2))}</p>"
                 f"<p><b>Out:</b> {_e(sol.get('mechanism_sentence', ''))}</p><div class='loops'>"
                 + "".join(f"<span class='{'on' if on else 'off'}'>{'✓' if on else '·'} {_e(name)}</span>" for name, on in _loops(d))
                 + f"</div><p style='font-size:14px;color:var(--mute)'>{_e(' · '.join(f'{v} {k}' for k, v in list(stats.items())[:6]))}</p>"
                 f"<p style='font-size:14px'><a href='{d.name}/dossier.html'>Dossier</a> · <a href='{d.name}/board.html'>"
                 f"Whiteboard</a> · <a href='{d.name}/report.html'>Report</a> · <a href='{d.name}/REVIEW.md'>Review</a></p></div>")
    p.append("</div></div></section>")

    # -- learning across problems --
    lessons_file = ROOT / "knowledge" / "lessons.md"
    lessons = lessons_file.read_text(encoding="utf-8") if lessons_file.exists() else ""
    p.append("<section><div class='wrap'><h2>It learns across problems</h2><p class='sub'>At the end of each problem "
             "it writes process lessons and engineering findings; the next problem starts from them.</p><div class='know'>")
    for d in dests:
        k_in = _read_json(d / "knowledge_in.json")
        p.append(f"<div class='card'><div class='k'>{_e(_read_json(d / 'problem.json').get('title', ''))}</div>"
                 f"<p>starts with <b>{len(k_in.get('lessons', []))}</b> lessons and <b>{len(k_in.get('insight_runs', []))}</b> "
                 f"findings files from earlier problems</p></div>")
    p.append("</div>")
    notes = re.findall(r"^\s+- used in run \S+: (.+)$", lessons, flags=re.MULTILINE)
    if notes:
        p.append("<div class='card' style='margin-top:14px'><div class='k'>How later problems used the lessons "
                 "(their own notes)</div><ul>" + "".join(f"<li>{_e(x)}</li>" for x in notes[-5:]) + "</ul></div>")
    p.append("</div></section>")

    # -- outputs --
    p.append("<section><div class='wrap'><h2>What a run leaves behind</h2><div class='card files'><ul>"
             "<li><code>final/figure.png</code> — the concept figure (panels A–D) and <code>final/rationale.md</code></li>"
             "<li><code>board.html</code> — the whiteboard, turn by turn, with the board picture per meeting</li>"
             "<li><code>stage_a/iter_*/</code> — transcript, whiteboard, verdict, the Manager's gradients and rewrite</li>"
             "<li><code>master_prompt/rev_*.md</code> and <code>diff_*.md</code> — every version of the council's prompt</li>"
             "<li><code>stage_b/attempt_*/round_*/</code> — renders, the critic's regions, SAM masks, keep or revert</li>"
             "<li><code>dossier.html</code>, <code>report.html</code>, <code>REVIEW.md</code> — the reading copies</li>"
             "<li><code>knowledge/</code> — lessons, findings and tools carried to the next problem</li></ul></div>"
             "</div></section><footer><div class='wrap'>Generated from the run files by hs.story. "
             "Meta Global AI Developer Hackathon, 2026.</div></footer></body></html>")
    path = out / "story.html"
    path.write_text("".join(p), encoding="utf-8")
    return path
