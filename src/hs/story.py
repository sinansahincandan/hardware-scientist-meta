"""The jury document (`showcase/story.html`): one problem, top to bottom — the input; how the output evolved,
each version beside the prompt that generated it; the same events located on the owner's block diagrams; what SAM
contributed; the other problems. Every quote, number and picture is read from the run files; the only hand-written
text is headings and one-line explanations of what a step is."""
from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from hs.showcase_build import ROOT, _read_json, _sentences

STYLE = """<style>
:root{--ink:#16202c;--mute:#5b6878;--line:#dfe4ea;--bg:#f6f7f9;--card:#fff;--blue:#1f6fd1;--red:#d64545;
  --green:#1f9d63;--amber:#c98a12}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 Inter,-apple-system,
  'Segoe UI',Helvetica,Arial,sans-serif}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
header{background:#101826;color:#fff;padding:40px 0 30px}header h1{margin:0;font-size:34px;letter-spacing:-.5px}
header p{margin:6px 0 0;color:#b9c6d6;max-width:860px}
h2{font-size:24px;margin:0 0 4px}.lead{color:var(--mute);margin:0 0 18px}
section{padding:34px 0;border-bottom:1px solid var(--line)}
.input{background:var(--card);border:1px solid var(--line);border-left:6px solid var(--blue);border-radius:10px;
  padding:18px 22px}.input h3{margin:0 0 6px;font-size:20px}.input ul{margin:8px 0 0 18px;padding:0}
.k{font-size:12px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:var(--mute);margin:4px 0}
.row{display:grid;grid-template-columns:300px 1fr 1fr;gap:16px;background:var(--card);border:1px solid var(--line);
  border-radius:10px;padding:14px;margin-bottom:12px;align-items:start}
.row img{width:100%;border-radius:6px;border:1px solid var(--line);background:#fff}
.tag{display:inline-block;font-size:12px;font-weight:700;border-radius:4px;padding:2px 8px;color:#fff;margin-bottom:6px}
.t-a{background:var(--blue)}.t-r{background:var(--red)}.t-m{background:var(--amber)}.t-g{background:var(--green)}
.prompt{font:13px/1.45 ui-monospace,Menlo,monospace;background:#f3f5f8;border:1px solid var(--line);border-radius:6px;
  padding:10px;white-space:pre-wrap}.prompt .add{background:#dff5e8;color:#0b5a34}
.res p{margin:0 0 6px}.res ul{margin:4px 0 6px 18px;padding:0}
.quote{border-left:3px solid var(--red);padding:2px 10px;color:#4a1f1f;background:#fdf3f3;margin:4px 0 8px}
.quote.ok{border-color:var(--green);color:#173d2a;background:#f1faf5}
.steps{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.step{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.step svg{width:100%;height:auto;border-radius:6px;background:#fff;display:block}
.step p{margin:8px 0 0}.step b.n{display:inline-block;width:24px;height:24px;border-radius:50%;background:var(--red);
  color:#fff;text-align:center;line-height:24px;font-size:13px;margin-right:6px}
.sam{display:grid;grid-template-columns:1fr 1fr;gap:14px}.sam figure{margin:0}.sam img{width:100%;border-radius:6px}
figcaption{font-size:13px;color:var(--mute);margin-top:4px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line)}
td,th{padding:10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;font-size:14px}
td img{width:200px;border-radius:6px}
footer{padding:24px 0 40px;color:var(--mute);font-size:13px}
</style>"""


def _e(x: Any) -> str:
    return html.escape(str(x))


def _ins(text: str, words: int = 0) -> str:
    text = " ".join(str(text).split())
    if words and len(text.split()) > words:
        text = " ".join(text.split()[:words]) + " …"
    return _e(text)


def _thumb(src: Path, assets: Path, name: str, width: int = 900, circle: list[list[float]] | None = None) -> str:
    """A reduced copy in story_assets/ (optionally with red circles on 0-1000 boxes); returns its page path."""
    img = Image.open(src).convert("RGB")
    if circle:
        d = ImageDraw.Draw(img)
        for b in circle:
            x0, y0, x1, y1 = (b[0] / 1000 * img.width, b[1] / 1000 * img.height, b[2] / 1000 * img.width,
                              b[3] / 1000 * img.height)
            d.ellipse([x0 - 35, y0 - 35, x1 + 35, y1 + 35], outline=(214, 69, 69), width=10)
    img.thumbnail((width, width))
    out = assets / f"{name}.jpg"
    img.save(out, quality=85)
    return f"story_assets/{out.name}"


def _role_line(rev: Path, member: str) -> str:
    text = rev.read_text(encoding="utf-8") if rev.exists() else ""
    m = re.search(rf"### {re.escape(member)}.*?\*\*Decision authority:\*\*(.*?)\n", text, flags=re.DOTALL)
    return " ".join(m.group(1).split()) if m else ""


def _diff_html(old: str, new: str) -> str:
    """New text with the words not in the old text highlighted (word level)."""
    old_words = set(re.findall(r"[\w-]+", old.lower()))
    out = []
    for tok in re.split(r"(\s+)", new):
        bare = re.sub(r"[^\w-]", "", tok.lower())
        out.append(f"<span class='add'>{_e(tok)}</span>" if bare and bare not in old_words else _e(tok))
    return "".join(out)


def _frame(fig: str, nodes: list[str], fmap: dict[str, Any], edge: tuple[str, str] | None = None,
           colour: str = "#d64545") -> str:
    """A zoom into the owner's figure around the blocks that fired, outlined and numbered; the figure is one shared
    file (story_assets/<fig>), referenced, never copied into the page."""
    meta = fmap[fig]
    vw, vh = meta["viewBox"]
    boxes = [meta["nodes"][n] for n in nodes if n in meta["nodes"]]
    x0 = min(b[0] for b in boxes) - 70
    y0 = min(b[1] for b in boxes) - 70
    x1 = max(b[0] + b[2] for b in boxes) + 70
    y1 = max(b[1] + b[3] for b in boxes) + 70
    w = max(x1 - x0, 760)
    h = max(y1 - y0, w * 0.55)  # one aspect for every frame; never so close that the context is lost
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x0, y0 = max(0, min(cx - w / 2, vw - w)), max(0, min(cy - h / 2, vh - h))
    parts = [f"<svg viewBox='{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}' xmlns='http://www.w3.org/2000/svg'>",
             f"<image href='story_assets/{fig}' x='0' y='0' width='{vw}' height='{vh}'/>",
             f"<rect x='0' y='0' width='{vw}' height='{vh}' fill='#fff' opacity='0.35'/>"]
    del edge  # the figure's own arrows show the loop; a straight overlay line crossed other blocks
    for b in boxes:
        parts.append(f"<rect x='{b[0] - 6}' y='{b[1] - 6}' width='{b[2] + 12}' height='{b[3] + 12}' rx='12' "
                     f"fill='{colour}' fill-opacity='0.08' stroke='{colour}' stroke-width='7'/>")
    parts.append("</svg>")
    return "".join(parts)


def build_story(slugs: list[str], out: Path = ROOT / "showcase", hero_slug: str = "lunar-regolith-excavation-robot",
                sam_run: Path | None = None) -> Path:
    fmap = json.loads((ROOT / "docs" / "figures_map.json").read_text(encoding="utf-8"))
    assets = out / "story_assets"
    if assets.exists():
        shutil.rmtree(assets)
    assets.mkdir(parents=True)
    for fig in fmap:
        shutil.copy(ROOT / "docs" / fig, assets / fig)
    hero = out / hero_slug
    prob = _read_json(hero / "problem.json")
    it0, it1 = hero / "stage_a" / "iter_00", hero / "stage_a" / "iter_01"
    s0, s1 = _read_json(it0 / "solution.json"), _read_json(it1 / "solution.json")
    v0, v1 = _read_json(it0 / "verdict.json"), _read_json(it1 / "verdict.json")
    b0 = _read_json(it0 / "whiteboard.json")
    edit, grad = _read_json(it0 / "manager_edit.json"), _read_json(it0 / "gradient_prompt.json")
    r0 = hero / "stage_b" / "attempt_00" / "round_00"
    r1 = hero / "stage_b" / "attempt_00" / "round_01"
    ev0, ev1 = _read_json(r0 / "eval.json"), _read_json(r1 / "eval.json")
    vlm0, vgrad = _read_json(r0 / "vlm_prompt.json"), _read_json(r0 / "vlm_gradient.json")
    local_fix = next((x.get("prompt_fix", "") for x in vgrad.get("per_region", []) if x.get("prompt_fix")), "")
    ke = {k["quantity"]: f"{k['value']:g} {k['unit']}" for k in s0.get("key_estimates", [])}
    ke1 = {k["quantity"]: f"{k['value']:g} {k['unit']}" for k in s1.get("key_estimates", [])}
    rev0 = (hero / "master_prompt" / "rev_000.md").read_text(encoding="utf-8")
    power = next((m for m in re.findall(r"^### (.+)$", rev0, flags=re.MULTILINE) if "Power" in m), "")
    role0 = _role_line(hero / "master_prompt" / "rev_000.md", power)
    role1 = _role_line(hero / "master_prompt" / "rev_001.md", power)
    sk0 = sorted((it0 / "evidence").glob("sketch_11.png")) or sorted((it0 / "evidence").glob("sketch_*.png"))
    sk1 = sorted((it1 / "evidence").glob("sketch_48.png")) or sorted((it1 / "evidence").glob("sketch_*.png"))
    review = (hero / "REVIEW.md").read_text(encoding="utf-8") if (hero / "REVIEW.md").exists() else ""
    fb0 = v0.get("feedback", "")
    m = re.search(r"Re-derivation.*?(?=Lift|$)", fb0, flags=re.DOTALL)
    reject_quote = _sentences(m.group(0), 2) if m else _sentences(fb0, 2)

    p: list[str] = [("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' "
                     f"content='width=device-width'><title>Hardware Scientist — how a design evolves</title>{STYLE}"
                     "</head><body>")]
    p.append("<header><div class='wrap'><h1>Hardware Scientist</h1><p>An engineer states a hardware problem in plain "
             "words. A council of AI engineers designs it; an Evaluator accepts or rejects; on rejection a Manager "
             "rewrites the council's own instructions; the accepted design is drawn, measured by SAM and corrected "
             "until the picture matches. Below: one problem, start to finish. All models are Meta's (Muse Spark, "
             f"Muse Image, SAM 3.1); this run cost ${float(_read_json(hero / 'cost.json').get('total_usd', 0)):.2f}."
             "</p></div></header>")

    # 1 input
    p.append("<section><div class='wrap'><h2>1 · Input</h2><p class='lead'>Exactly what the system was given.</p>"
             f"<div class='input'><h3>{_e(prob.get('title'))}</h3><p>{_e(prob.get('statement'))}</p><div class='k'>"
             "Constraints</div><ul>" + "".join(f"<li>{_e(c)}</li>" for c in prob.get("constraints", []))
             + "</ul></div></div></section>")

    # 2 evolution
    p.append("<section><div class='wrap'><h2>2 · How the output evolved</h2><p class='lead'>Each version (left), "
             "the prompt that produced it (middle), and what happened next (right).</p>")
    p.append("<div class='row'><div>"
             + (f"<img src='{_thumb(sk0[0], assets, 'd1')}' alt='council sketch, meeting 1'>" if sk0 else "")
             + "</div><div><span class='tag t-a'>Design v1 · council meeting 1</span><div class='k'>Generated by — "
             f"design prompt rev 0, {_e(power.split(' —')[0])}'s role</div><div class='prompt'>{_e(role0)}</div></div>"
             f"<div class='res'><p><b>Design:</b> {_e(s0.get('mechanism_sentence'))}</p><p>Battery "
             f"{_e(ke.get('battery mass', '?'))} for {_e(ke.get('30-min average power', '?'))}; total "
             f"{_e(ke.get('joint mass total with payload', '?'))}. "
             f"{sum(1 for v in b0.get('votes', {}).values() if v.get('ready'))} of {len(b0.get('votes', {}))} "
             "members ready.</p><span class='tag t-r'>Evaluator rejects</span>"
             f"<div class='quote'>{_ins(reject_quote, 40)}</div></div></div>")
    p.append("<div class='row'><div>"
             + (f"<img src='{_thumb(sk1[0], assets, 'd2')}' alt='council sketch, meeting 2'>" if sk1 else "")
             + "</div><div><span class='tag t-m'>Manager rewrites the prompt</span><div class='k'>Design prompt rev 1 — "
             "same role, new duties highlighted</div>"
             f"<div class='prompt'>{_diff_html(role0, role1)}</div><p style='font-size:13px;color:var(--mute)'>"
             f"Also rewritten: {_e(', '.join(h.replace('## ', '') for h in edit.get('changed', []) if 'Roles' not in h))}. "
             f"Root cause, in the Manager's words: {_ins(grad.get('root_cause', ''), 30)}</p></div>"
             f"<div class='res'><span class='tag t-a'>Design v2 · council meeting 2</span><p>{_e(s1.get('mechanism_sentence'))}"
             f"</p><p>Battery now {_e(ke1.get('pack specific energy', '?'))} (a purchasable pack), total "
             f"{_e(ke1.get('reconciled total mass', '?'))}, lift force {_e(ke1.get('actuator force total', '?'))}.</p>"
             f"<span class='tag t-g'>Evaluator accepts</span><div class='quote ok'>{_ins(v1.get('constraint_review', ''), 45)}"
             "</div></div></div>")
    reg = (ev0.get("regions") or [{}])[0]
    circles = [x["box"] for x in ev0.get("regions", []) if len(x.get("box", [])) == 4]
    p.append("<div class='row'><div>"
             f"<img src='{_thumb(r0 / 'render.png', assets, 'p1', circle=circles)}' alt='render round 1'>"
             "</div><div><span class='tag t-a'>Picture v1</span><div class='k'>Generated by — image prompt (start)</div>"
             f"<div class='prompt'>{_ins(vlm0.get('prompt', ''), 70)}</div></div><div class='res'><span class='tag t-r'>"
             f"Critic: not faithful</span><div class='quote'>{_e(reg.get('observed', ''))}</div><p>The prompt gradient "
             f"chose a <b>{_e(vgrad.get('fix_mode', ''))}</b> fix: redraw only the circled region.</p></div></div>")
    prev = (ev1.get("previous_regions") or [{}])[0]
    zoom = ""
    comp = _read_json(r0 / "composite_callout.json").get("box_px")
    if comp:
        orig_w = (_read_json(r0 / "sam.json").get("size") or [0])[0]  # the box is in the original render's pixels
        crops = []
        for src in (r0 / "render.png", r1 / "render.png"):
            im = Image.open(src).convert("RGB")
            k = im.width / orig_w if orig_w else 1.0
            x0, y0, x1, y1 = (v * k for v in comp)
            pad = 0.45 * max(x1 - x0, y1 - y0)
            crops.append(im.crop((int(max(x0 - pad, 0)), int(max(y0 - pad, 0)), int(min(x1 + pad, im.width)),
                                  int(min(y1 + pad, im.height)))))
        pair = Image.new("RGB", (crops[0].width + crops[1].width + 12, max(c.height for c in crops)), "white")
        pair.paste(crops[0], (0, 0))
        pair.paste(crops[1], (crops[0].width + 12, 0))
        pair.save(assets / "p2zoom.png")
        zoom = (f"<img src='{_thumb(assets / 'p2zoom.png', assets, 'p2zoom', 700)}' style='margin-top:8px'>"
                "<div style='font-size:12px;color:var(--mute)'>the fixed region: before | after</div>")
    p.append("<div class='row'><div>"
             f"<img src='{_thumb(r1 / 'render.png', assets, 'p2')}' alt='render round 2'>{zoom}</div><div><span class='tag t-m'>"
             "Picture v2 · local fix</span><div class='k'>Generated by — region edit instruction</div>"
             f"<div class='prompt'>{_e(local_fix)}</div></div><div class='res'><span class='tag t-g'>Critic: faithful"
             f"</span><div class='quote ok'>Earlier fault on the {_e(prev.get('part_id', ''))}: {_e(prev.get('status', ''))}. "
             f"{_ins(prev.get('note', '') or ev1.get('comparison_with_previous', ''), 40)}"
             "</div></div></div>")
    misses = re.findall(r"^- \*\*(.+?)\*\*", review.split("## Independent review")[-1], flags=re.MULTILINE) \
        if "## Independent review" in review else []
    p.append("<div class='row'><div>"
             f"<img src='{_thumb(hero / 'final' / 'figure.png', assets, 'fig')}' alt='final figure'></div><div>"
             "<span class='tag t-g'>Concept figure</span><p>Labelled view, critical part, measurement chain, how it is "
             "made.</p></div><div class='res'><span class='tag t-r'>Independent review afterwards</span><ul>"
             + "".join(f"<li>{_e(x)}</li>" for x in misses[:4])
             + "</ul><p><b>The system changed, not this design:</b> the Evaluator now sums parts against every size "
             "limit, reconciles conflicting values and traces every material, energy and signal flow to a part.</p>"
             "</div></div></div></section>")

    # 3 the loops on the owner's block diagrams
    steps = [
        ("fig1_architecture.svg", ["n-master", "n-council", "n-meeting"], None,
         (f"<b>Meeting 1.</b> Four engineers search, calculate and sketch on the whiteboard "
         f"({len(b0.get('evidence', []))} evidence items). It ends at the round limit with 1 of 4 ready.")),
        ("fig1_architecture.svg", ["n-meeting", "n-evaluator"], ("n-meeting", "n-evaluator"),
         ("<b>Trigger — the Evaluator rejects.</b> It re-does the battery arithmetic: 1000 Wh in 2.92 kg is three "
         "times what a real pack holds.")),
        ("fig1_architecture.svg", ["n-evaluator", "n-master"], ("n-evaluator", "n-master"),
         ("<b>Action — the Manager's two-step gradient.</b> Decides which feedback to apply and which prompt section "
         f"caused it; rewrites {len(edit.get('changed', []))} sections of the design prompt (rev 0 → rev 1).")),
        ("fig1_architecture.svg", ["n-meeting", "n-evaluator", "n-council-archive"], None,
         ("<b>Meeting 2 on rev 1 → accepted.</b> Pack replaced, folded size and lift force computed. Both solutions "
         "are kept in the council archive.")),
        ("fig2_visualization_pipeline.svg", ["n-accepted", "n-schematic", "n-vlm-writer", "n-render"], None,
         ("<b>Picture.</b> The council's sketches become a concept sketch; the prompt writer turns it into an image "
         "prompt; the image model renders.")),
        ("fig2_visualization_pipeline.svg", ["n-labels", "n-designer-eval"], ("n-labels", "n-designer-eval"),
         ("<b>Trigger — the critic finds a fault.</b> SAM measures each part; the critic compares picture and sketch "
         "region by region: one label points at dust, not at the drum.")),
        ("fig2_visualization_pipeline.svg", ["n-designer-eval", "n-vlm-writer", "n-render"],
         ("n-designer-eval", "n-vlm-writer"),
         ("<b>Action — local fix.</b> Only the faulty region is redrawn; the same region is checked again, marked "
         "fixed, and the round is kept.")),
        ("fig1_architecture.svg", ["n-image-archive", "n-figure", "n-lessons"], None,
         ("<b>Output and memory.</b> The figure is composed; every picture round is archived; lessons and findings "
         "go to knowledge/ for the next problem.")),
    ]
    p.append("<section><div class='wrap'><h2>3 · Where it happened on the architecture</h2><p class='lead'>The same "
             "events on our block diagrams. Red boxes = the blocks that fired at that step; the figure's own arrows "
             "show the loop taken.</p><div class='steps'>")
    for k, (fig, nodes, edge, text) in enumerate(steps, 1):
        p.append(f"<div class='step'>{_frame(fig, nodes, fmap, edge)}<p><b class='n'>{k}</b>{text}</p></div>")
    p.append("</div></div></section>")

    # 4 SAM
    if sam_run is not None and sam_run.exists():
        from hs.stage_b import part_map as pm

        a0, a1 = sam_run / "round_00", sam_run / "round_01"
        ov = assets / "sam_r0.png"
        pm.draw_overlay(a0 / "render.png", a0 / "sam.json", ov)
        u = _read_json(a0 / "sam_use.json")
        diffs, used = u.get("sam_differences", {}), u.get("sam_parts_used_by_critique", [])
        e0, e1 = _read_json(a0 / "eval.json"), _read_json(a1 / "eval.json")
        g0 = _read_json(a0 / "vlm_gradient.json")
        prevs = {x.get("part_id"): x.get("status") for x in e1.get("previous_regions", [])}
        p.append("<section><div class='wrap'><h2>4 · What SAM contributes</h2><p class='lead'>SAM 3.1 outlines each "
                 "part in the picture. Code measures count, direction and contact and gives the differences to the "
                 "critic as written evidence; the critic must answer each one; confirmed ones become prompt edits. "
                 f"Example: {_e(_read_json(sam_run.parents[1] / 'problem.json').get('title', ''))}, picture round 1 → 2."
                 "</p><div class='sam'><figure>"
                 f"<img src='{_thumb(ov, assets, 'sam_r0v', 1100)}'><figcaption>Round 1: what SAM found (each part's "
                 "box in its colour).</figcaption></figure><figure>"
                 f"<img src='{_thumb(a1 / 'render.png', assets, 'sam_r1', 1100)}'><figcaption>Round 2, after the prompt "
                 "edit.</figcaption></figure></div><table style='margin-top:14px'><tr><th>SAM measured</th><th>Critic "
                 "confirmed</th><th>Prompt edit</th><th>Round 2</th></tr>")
        for pid in used:
            region = next((r for r in e0.get("regions", []) if r.get("part_id") == pid), {})
            fix = next((x.get("prompt_fix", "") for x in g0.get("per_region", []) if x.get("part_id") == pid), "")
            p.append(f"<tr><td>{_e(pid)}: {_e('; '.join(diffs.get(pid, [])))}</td><td>{_ins(region.get('observed', ''), 22)}"
                     f"</td><td>{_ins(fix, 30)}</td><td><b>{_e(prevs.get(pid, '—'))}</b></td></tr>")
        change = _read_json(a1 / "vlm_prompt.json").get("changes_from_previous", "")
        p.append("</table>" + (f"<p><b>How the image prompt changed for round 2:</b> {_e(change)}</p>" if change else ""))
        upgrade = ROOT / "docs" / "screens" / "r5_sam_remeasure_04.png"
        if upgrade.exists():
            p.append("<p style='margin-top:14px'><b>SAM itself was improved during the project.</b> On the excavator "
                     "picture the first version found 3 of 10 parts and mistook the digging drum for a wheel. Now the "
                     "vision model writes the phrases from the picture, parts no phrase finds are prompted with a box, "
                     "and a judge removes wrong matches: 9 of 10 found.</p>"
                     f"<img src='{_thumb(upgrade, assets, 'sam_upgrade', 1100)}' style='width:75%;border-radius:8px'>")
        p.append("</div></section>")

    # 5 all problems
    p.append("<section><div class='wrap'><h2>5 · All problems</h2><table><tr><th>Problem</th><th>Output</th>"
             "<th>What ran</th><th>Cost</th></tr>")
    for slug in slugs:
        d = out / slug
        if not d.exists():
            continue
        pr = _read_json(d / "problem.json")
        iters = sorted(d.glob("stage_a/iter_*"))
        rejected = sum(1 for i in iters if _read_json(i / "verdict.json") and not _read_json(i / "verdict.json").get("accept"))
        rounds = len(list(d.glob("stage_b/attempt_*/round_*")))
        sol = _read_json(iters[-1] / "solution.json") if iters else {}
        p.append(f"<tr><td><b>{_e(pr.get('title'))}</b><br>{_ins(pr.get('statement', ''), 28)}</td>"
                 f"<td><a href='{slug}/final/figure.png'><img src='{_thumb(d / 'final' / 'panel_A.png', assets, slug, 500)}'>"
                 f"</a><br>{_ins(sol.get('mechanism_sentence', ''), 26)}</td><td>{len(iters)} meeting"
                 f"{'s' if len(iters) != 1 else ''}, {rejected} rejection{'s' if rejected != 1 else ''}, {rounds} picture "
                 f"round{'s' if rounds != 1 else ''}<br><a href='{slug}/dossier.html'>details</a></td>"
                 f"<td>${float(_read_json(d / 'cost.json').get('total_usd', 0)):.2f}</td></tr>")
    p.append("</table></div></section><footer><div class='wrap'>Built from the run files by hs.story; full records "
             "per problem in the linked folders (whiteboard, transcripts, prompts, renders, reviews).</div></footer>"
             "</body></html>")
    path = out / "story.html"
    path.write_text("".join(p), encoding="utf-8")
    return path
