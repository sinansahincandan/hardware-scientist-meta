"""hs report (one run) + hs compare (several runs), spec §8. Self-contained HTML."""
from __future__ import annotations

import base64
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _img(path: Path, embed: bool, run_dir: Path, width: int = 420) -> str:
    if not path.exists():
        return f"<i>missing image: {html.escape(path.name)}</i>"
    if embed:
        data = base64.b64encode(path.read_bytes()).decode()
        return f"<img src='data:image/png;base64,{data}' style='max-width:{width}px'>"
    try:
        rel = path.relative_to(run_dir)
    except ValueError:
        rel = path
    return f"<img src='{rel}' style='max-width:{width}px'>"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _sf(x: float) -> str:
    """At most 3 significant figures, for human-facing numbers."""
    return f"{x:.3g}"


def _sentences(text: str, n: int) -> str:
    """The first n sentences of text, never cut mid-word."""
    import re

    parts = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    return " ".join(parts[:n])


def _rel_img(path: Path, run_dir: Path, width: int = 900) -> str:
    """Relative-path image, display copy downscaled to <=1600 px, click to full."""
    if not path.exists():
        return f"<i>missing image: {html.escape(path.name)}</i>"
    try:
        from PIL import Image

        img = Image.open(path)
        display = path
        if max(img.size) > 1600:
            disp_dir = path.parent / "display"
            disp_dir.mkdir(exist_ok=True)
            display = disp_dir / path.name
            if not display.exists():
                img.thumbnail((1600, 1600))
                img.convert("RGB").save(display)
        rel_full = path.relative_to(run_dir).as_posix()
        rel_disp = display.relative_to(run_dir).as_posix()
        return (f"<a href='{rel_full}' target='_blank'><img src='{rel_disp}' "
                f"style='max-width:{width}px;width:100%;cursor:zoom-in'></a>")
    except Exception:
        return f"<i>image: {html.escape(path.name)}</i>"


REPORT_STYLE = """<style>
body{font-family:'Segoe UI',Helvetica,Arial,sans-serif;background:#f4f4f2;color:#1c1e22;margin:0}
main{max-width:1080px;margin:0 auto;padding:28px 22px 60px}
h1{font-size:30px;line-height:1.2;margin:6px 0 10px} h2{font-size:20px;margin:34px 0 10px;border-bottom:2px solid #222;padding-bottom:5px}
h3{font-size:16px;margin:20px 0 6px} p,li{font-size:15px;line-height:1.55}
.hero{background:#171a1f;color:#eee;border-radius:12px;padding:22px 26px}
.hero .mech{font-size:19px;line-height:1.45}
.chip{display:inline-block;background:#e9f2e7;border:1px solid #9db894;border-radius:10px;padding:3px 9px;margin:2px;font-size:13px}
.event{border-left:3px solid #b9c4bb;padding:7px 12px;margin:8px 0;background:#fff}
.event b{color:#333}
.q{border:1px solid #d8a920;background:#fdf6dd;border-radius:8px;padding:10px 14px}
a{color:#1a5fb8} img{border-radius:6px}
.small{color:#666;font-size:13px}
</style>"""


def report_html(run_dir: Path, embed: bool = False) -> str:
    problem = _read_json(run_dir / "problem.json")
    archive = [json.loads(l) for l in (run_dir / "archive.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()] \
        if (run_dir / "archive.jsonl").exists() else []
    img_entries = [json.loads(l) for l in (run_dir / "image_archive.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()] \
        if (run_dir / "image_archive.jsonl").exists() else []
    cost = _read_json(run_dir / "cost.json")
    sol_files = sorted((run_dir / "stage_a").glob("iter_*/solution.json")) if (run_dir / "stage_a").exists() else []
    sol = _read_json(sol_files[-1]) if sol_files else _read_json(run_dir / "seeded_solution.json")
    parts: list[str] = [("<!doctype html><html><head><meta charset='utf-8'>"
                         f"<title>{html.escape(str(problem.get('title', run_dir.name)))}</title>"
                         f"{REPORT_STYLE}</head><body><main>")]
    # 1. The problem
    parts.append(f"<p class='small'>Hardware Scientist — concept report</p><h1>{html.escape(str(problem.get('title', run_dir.name)))}</h1>")
    parts.append(f"<p>{html.escape(str(problem.get('statement', '')))}</p>")
    if problem.get("constraints"):
        parts.append("<ul>" + "".join(f"<li>{html.escape(str(c))}</li>" for c in problem["constraints"]) + "</ul>")
    # 2. The final figure
    parts.append("<h2>The concept</h2>")
    if (run_dir / "final" / "figure.png").exists():
        parts.append(_rel_img(run_dir / "final" / "figure.png", run_dir, width=1040))
    else:
        parts.append("<p>No final figure: no render in this run was judged faithful to the mechanism sketch.</p>")
    # 3. Mechanism, choices, open question
    if sol:
        parts.append("<div class='hero'>")
        parts.append(f"<p class='mech'>{html.escape(str(sol.get('mechanism_sentence', '')))}</p>")
        parts.append(f"<p>{html.escape(str(sol.get('transfer_line', '')))}</p>")
        parts.append("<h3 style='color:#fff'>Three decisive design choices</h3><ol>"
                     + "".join(f"<li>{html.escape(str(c))}</li>" for c in (sol.get("decisive_choices") or [])[:3]) + "</ol>")
        parts.append(f"<div class='q' style='color:#222'><b>The open question</b><br>{html.escape(str(sol.get('open_question', '')))}</div>")
        parts.append("</div>")
    # 4. What happened (one plain sentence per event)
    parts.append("<h2>What happened</h2>")
    events: list[str] = []
    seeded = _read_json(run_dir / "seeded_from.json")
    if seeded:
        events.append(f"This run redrew the accepted solution of run {html.escape(str(seeded.get('source_run', '')))}; "
                      "no council meeting ran in this run.")
    for entry in archive:
        k = int(entry.get("iteration", 0))
        iter_dir = run_dir / "stage_a" / f"iter_{k:02d}"
        closure = _read_json(iter_dir / "closure.json")
        if closure:
            closed = closure.get("closed_by", "")
            events.append(f"The council meeting {'closed by consensus' if closed == 'consensus' else 'reached the cycle cap without consensus'} "
                          f"after {closure.get('cycles_used', '?')} cycles.")
        verdict = _read_json(iter_dir / "verdict.json")
        if verdict:
            events.append(f"The evaluator {'accepted the concept' if verdict.get('accept') else 'sent the concept back'}: "
                          f"{html.escape(_sentences(str(verdict.get('feedback', '')), 2))}")
    rounds_by_attempt: dict[int, int] = {}
    for e in img_entries:
        rounds_by_attempt[int(e.get("attempt", 0))] = rounds_by_attempt.get(int(e.get("attempt", 0)), 0) + 1
    for e in img_entries:
        dec = str(e.get("decision", ""))
        n_rounds = rounds_by_attempt.get(int(e.get("attempt", 0)), 0)
        if dec == "s1_pass":
            what = "The picture matched the mechanism sketch."
        elif dec == "s1_retry":
            what = ("The picture did not match the mechanism sketch; the image prompt was corrected: "
                    + html.escape(_sentences(str(e.get("s1_differences", "")), 1)))
        elif dec == "s1_exhausted":
            what = (f"The picture could not be drawn faithfully after {n_rounds} rounds. Nothing was sent back to "
                    "the design, because a drawing failure says nothing about whether the design works.")
        elif dec == "s2_return":
            what = ("The designer evaluation saw a design flaw in the picture, so the concept went back to the "
                    "council: " + html.escape(_sentences(str(e.get("s2_feedback", "")), 2)))
        else:
            what = html.escape(dec)
        events.append(f"Picture {int(e.get('attempt', 0)) + 1}, round {int(e.get('round', 0)) + 1}: {what}")
    diffs = sorted((run_dir / "master_prompt").glob("diff_*.md"))
    for d in diffs:
        events.append(f"The Manager changed the council's instructions (<a href='master_prompt/{d.name}'>see the diff</a>).")
    events.append(f"The whole run cost ${_sf(float(cost.get('total_usd', 0)))}.")
    parts.append("".join(f"<div class='event'>{e}</div>" for e in events))
    # 5. References
    refs = _read_text(run_dir / "references.md")
    parts.append("<h2>References</h2>")
    if refs:
        items = [l for l in refs.splitlines() if l and not l.startswith("#")]
        parts.append("<ol>" + "".join(
            f"<li>{html.escape(l.split('. ', 1)[-1])}</li>" for l in items) + "</ol>")
    else:
        parts.append("<p>No literature references were recorded in this run.</p>")
    # Files (linked, never inlined)
    parts.append("<h2>Files</h2><ul>"
                 "<li><a href='board.html'>Whiteboard replay</a></li>"
                 "<li><a href='references.md'>Reference list (Markdown)</a></li>"
                 + "".join(f"<li><a href='stage_a/{d.name}/transcript.md'>{d.name} transcript</a> · "
                           f"<a href='stage_a/{d.name}/whiteboard.md'>whiteboard</a></li>"
                           for d in sorted((run_dir / 'stage_a').glob('iter_*'))) 
                 + "</ul>")
    parts.append(f"<p class='small'>Run {run_dir.name} · total cost ${_sf(float(cost.get('total_usd', 0)))} · "
                 "conceptual illustration — physical performance not established.</p>")
    parts.append("</main></body></html>")
    return "".join(parts)


def _old_report_html(run_dir: Path, embed: bool = True) -> str:
    problem = _read_json(run_dir / "problem.json")
    archive_path = run_dir / "archive.jsonl"
    archive = [json.loads(l) for l in archive_path.read_text(encoding="utf-8").splitlines() if l.strip()] \
        if archive_path.exists() else []
    cost = _read_json(run_dir / "cost.json")
    parts: list[str] = [("<!doctype html><html><head><meta charset='utf-8'>"
                         f"<title>Report {run_dir.name}</title>"
                         "<style>body{font-family:sans-serif}pre{white-space:pre-wrap;background:#f5f5f5;padding:8px}"
                         ".chip{display:inline-block;border:1px solid #333;padding:3px 8px;margin:2px;border-radius:10px}"
                         "del{background:#fdd}ins{background:#dfd;text-decoration:none}</style></head><body>")]
    parts.append(f"<h1>{html.escape(str(problem.get('title', run_dir.name)))}</h1>")
    # Deliverable header (AUTOPILOT §4 ref_deliverable_layout): mechanism sentence,
    # concept image, three decisive choices, one open question, next-iteration box.
    sol_files = sorted((run_dir / "stage_a").glob("iter_*/solution.json")) if (run_dir / "stage_a").exists() else []
    sol = _read_json(sol_files[-1]) if sol_files else {}
    if sol:
        parts.append("<div style='background:#171a1f;color:#eee;padding:22px 26px;border-radius:10px'>")
        parts.append(f"<p style='font-size:19px;margin:4px 0'>{html.escape(str(sol.get('mechanism_sentence', '')))}</p>")
        parts.append(f"<p style='color:#9fd0ff'>{html.escape(str(sol.get('transfer_line', '')))}</p>")
        parts.append(_img(run_dir / "final" / "panel_A.png", embed, run_dir, width=980))
        ff = run_dir / "final" / "flow.png"
        if ff.exists():
            parts.append("<p>Flow view (governing quantity, as decided by the council):</p>" + _img(ff, embed, run_dir, width=980))
        parts.append("<h3 style='color:#fff'>Three decisive design choices</h3><ol>"
                     + "".join(f"<li style='margin:6px 0'>{html.escape(str(c))}</li>"
                               for c in (sol.get("decisive_choices") or [])[:3]) + "</ol>")
        parts.append(f"<div style='border:1px solid #e6c34a;border-radius:8px;padding:10px 14px'>"
                     f"<b>The open question</b><br>{html.escape(str(sol.get('open_question', '')))}</div>")
        parts.append("<div style='background:#20261e;border-radius:8px;padding:10px 14px;margin-top:10px'>"
                     "<b>Next iteration</b><br>Move the design forward: answer the open question with a "
                     "measurement or a focused redesign, then re-run the designer evaluation.</div></div>")
    parts.append("<h2>1. Input</h2>")
    parts.append(f"<p>{html.escape(str(problem.get('statement', '')))}</p><ul>"
                 + "".join(f"<li>{html.escape(str(c))}</li>" for c in problem.get("constraints", [])) + "</ul>")
    # timeline strip
    parts.append("<h2>2. Timeline</h2><div>")
    for entry in archive:
        parts.append(f"<span class='chip'>iter {entry.get('iteration')} rev {entry.get('revision')}: "
                     f"{html.escape(str(entry.get('status')))}</span>")
    img_entries: list[dict[str, Any]] = []
    ia = run_dir / "image_archive.jsonl"
    if ia.exists():
        img_entries = [json.loads(l) for l in ia.read_text(encoding="utf-8").splitlines() if l.strip()]
    for e in img_entries:
        parts.append(f"<span class='chip'>B attempt {e.get('attempt')} round {e.get('round')}: {e.get('decision')}</span>")
    parts.append(f"<span class='chip'>cost ${float(cost.get('total_usd', 0)):.4f}</span></div>")
    # per iteration
    parts.append("<h2>3. Per iteration</h2>")
    iter_dirs = sorted((run_dir / "stage_a").glob("iter_*")) if (run_dir / "stage_a").exists() else []
    for iter_dir in iter_dirs:
        k = iter_dir.name
        parts.append(f"<h3>{k}</h3>")
        closure = _read_json(iter_dir / "closure.json")
        parts.append(f"<p>closed_by={html.escape(str(closure.get('closed_by')))} cycles={closure.get('cycles_used')}</p>")
        diffs = sorted((run_dir / "master_prompt").glob("diff_*.md"))
        parts.append(f"<p>Master prompt revisions: {len(list((run_dir / 'master_prompt').glob('rev_*.md')))}</p>")
        parts.append(f"<h4>Whiteboard</h4><pre>{html.escape(_read_text(iter_dir / 'whiteboard.md'))}</pre>")
        parts.append(f"<h4>Transcript</h4><pre>{html.escape(_read_text(iter_dir / 'transcript.md'))}</pre>")
        solution = _read_json(iter_dir / "solution.json")
        parts.append(f"<h4>Solution</h4><pre>{html.escape(json.dumps(solution, indent=2)[:4000])}</pre>")
        verdict = _read_json(iter_dir / "verdict.json")
        parts.append(f"<h4>Evaluator</h4><p>accept={verdict.get('accept')}</p>"
                     f"<pre>{html.escape(str(verdict.get('feedback', '')))}</pre>"
                     f"<p>Evidence requests: {html.escape(str(verdict.get('evidence_requests', [])))}</p>")
        parts.append(f"<p>Prior art:</p><pre>{html.escape(_read_text(iter_dir / 'novelty.md')[:2000])}</pre>")
        diagnosis = _read_text(iter_dir / "diagnosis.json")
        parts.append(f"<h4>Manager diagnosis</h4><pre>{html.escape(diagnosis[:3000])}</pre>")
        for diff in diffs:
            parts.append(f"<h4>{diff.name}</h4><pre>{html.escape(_read_text(diff))}</pre>")
    # revision timeline
    parts.append("<h2>4. Revision timeline</h2><table border='1'><tr><th>id</th><th>iteration</th>"
                 "<th>status</th><th>feedback</th></tr>")
    for entry in archive:
        parts.append(f"<tr><td>{entry.get('id')}</td><td>{entry.get('iteration')}</td>"
                     f"<td>{html.escape(str(entry.get('status')))}</td>"
                     f"<td>{html.escape(str(entry.get('feedback', ''))[:300])}</td></tr>")
    parts.append("</table>")
    # board tab
    from hs.board import board_html

    parts.append("<h2>4b. Board</h2>" + board_html(run_dir, fragment=True))
    # stage B rounds
    parts.append("<h2>5. Stage B rounds</h2>")
    for e in img_entries:
        render = run_dir / "stage_b" / f"attempt_{int(e.get('attempt', 0)):02d}" / f"round_{int(e.get('round', 0)):02d}"
        parts.append(f"<h3>attempt {e.get('attempt')} round {e.get('round')} — {e.get('decision')}</h3>")
        parts.append("<table><tr><td>schematic</td><td>render</td><td>annotated</td></tr><tr>")
        parts.append(f"<td>{_img(render / 'schematic_labeled.png', embed, run_dir)}</td>")
        parts.append(f"<td>{_img(render / 'render.png', embed, run_dir)}</td>")
        parts.append(f"<td>{_img(render / 'annotated.png', embed, run_dir)}</td></tr></table>")
        parts.append(f"<p>VLM prompt: {html.escape(str(e.get('vlm_prompt', ''))[:400])}</p>"
                     f"<p>S1 differences: {html.escape(str(e.get('s1_differences', '')))}</p>"
                     f"<p>S2: {html.escape(str(e.get('s2_feedback', '')))}</p>")
    # final figure
    parts.append("<h2>6. Final figure</h2>")
    parts.append(_img(run_dir / "final" / "figure.png", embed, run_dir, width=900))
    parts.append(f"<pre>{html.escape(_read_text(run_dir / 'final' / 'rationale.md'))}</pre>")
    parts.append("<h3>Cost table</h3><table border='1'><tr><th>role</th><th>model</th><th>input</th>"
                 "<th>output</th><th>usd</th></tr>")
    for entry in cost.get("entries", []):
        parts.append(f"<tr><td>{entry.get('role')}</td><td>{entry.get('model')}</td><td>{entry.get('input')}</td>"
                     f"<td>{entry.get('output')}</td><td>{entry.get('usd')}</td></tr>")
    parts.append(f"</table><p>Total: ${float(cost.get('total_usd', 0)):.4f}</p>")
    parts.append("</body></html>")
    return "".join(parts)


def write_report(run_dir: Path, embed: bool = False) -> Path:
    out = run_dir / "report.html"
    out.write_text(report_html(run_dir, embed=embed), encoding="utf-8")
    return out


def compare_html(run_dirs: list[Path]) -> str:
    rows: list[str] = []
    for run_dir in run_dirs:
        problem = _read_json(run_dir / "problem.json")
        archive_path = run_dir / "archive.jsonl"
        archive = [json.loads(l) for l in archive_path.read_text(encoding="utf-8").splitlines() if l.strip()] \
            if archive_path.exists() else []
        ia = run_dir / "image_archive.jsonl"
        img_entries = [json.loads(l) for l in ia.read_text(encoding="utf-8").splitlines() if l.strip()] \
            if ia.exists() else []
        cost = _read_json(run_dir / "cost.json")
        closures = []
        for iter_dir in sorted((run_dir / "stage_a").glob("iter_*")) if (run_dir / "stage_a").exists() else []:
            closures.append(str(_read_json(iter_dir / "closure.json").get("closed_by", "")))
        accepted_at = next((e.get("iteration") for e in archive if e.get("accept")), "")
        rows.append(
            f"<tr><td>{html.escape(str(problem.get('title', run_dir.name)))}</td>"
            f"<td>{accepted_at}</td><td>{html.escape(', '.join(closures))}</td>"
            f"<td>{html.escape(' → '.join(str(e.get('status')) for e in archive))}</td>"
            f"<td>{len(img_entries)}</td>"
            f"<td>{sum(1 for e in archive if e.get('status') == 'rejected_by_designer')}</td>"
            f"<td>{_img(run_dir / 'final' / 'figure.png', True, run_dir, width=240)}</td>"
            f"<td>${float(cost.get('total_usd', 0)):.4f}</td></tr>")
    return ("<!doctype html><html><head><meta charset='utf-8'><title>Compare</title></head><body>"
            "<h1>Compare</h1><table border='1'><tr><th>Problem</th><th>Iterations to accept</th>"
            "<th>Closures</th><th>Accept/reject sequence</th><th>S1 rounds</th><th>Returns B→A</th>"
            "<th>Figure</th><th>Cost</th></tr>" + "".join(rows) + "</table></body></html>")


def showcase_html(run_dirs: list[Path]) -> str:
    """Showcase: per run, exact input prompt left, final figure right (click to
    enlarge), mechanism sentence + 3 decisive choices + open question under it.
    Nothing else on the page. Same visual style as report.html."""
    blocks: list[str] = []
    for run_dir in run_dirs:
        problem = _read_json(run_dir / "problem.json")
        prompt_text = problem.get("statement", "")
        if problem.get("constraints"):
            prompt_text += "\n\nConstraints:\n" + "\n".join(f"- {c}" for c in problem["constraints"])
        if problem.get("criteria"):
            prompt_text += "\n\nCriteria:\n" + "\n".join(f"- {c}" for c in problem["criteria"])
        sol_files = sorted((run_dir / "stage_a").glob("iter_*/solution.json")) if (run_dir / "stage_a").exists() else []
        sol = _read_json(sol_files[-1]) if sol_files else {}
        figure = run_dir / "final" / "figure.png"
        fig_html = ""
        if figure.exists():
            data = base64.b64encode(figure.read_bytes()).decode()
            fig_html = (f"<a href='data:image/png;base64,{data}' target='_blank'>"
                        f"<img src='data:image/png;base64,{data}' style='width:100%;cursor:zoom-in'></a>")
        else:
            fig_html = "<i>missing final figure</i>"
        blocks.append(
            "<div style='display:flex;gap:28px;align-items:flex-start;background:#171a1f;color:#eee;"
            "padding:26px 28px;border-radius:10px;margin:0 0 28px'>"
            f"<div style='flex:0 0 34%'><h2 style='color:#fff;margin-top:0'>{html.escape(str(problem.get('title', run_dir.name)))}</h2>"
            f"<pre style='white-space:pre-wrap;background:#23272e;color:#eee;padding:14px;border-radius:8px'>{html.escape(prompt_text)}</pre></div>"
            f"<div style='flex:1'>{fig_html}"
            f"<p style='font-size:18px'>{html.escape(str(sol.get('mechanism_sentence', '')))}</p>"
            "<ol>" + "".join(f"<li style='margin:6px 0'>{html.escape(str(c))}</li>"
                             for c in (sol.get("decisive_choices") or [])[:3]) + "</ol>"
            f"<p><b>The open question</b><br>{html.escape(str(sol.get('open_question', '')))}</p>"
            "</div></div>")
    return ("<!doctype html><html><head><meta charset='utf-8'><title>Showcase</title>"
            "<style>body{font-family:sans-serif;background:#111318;margin:18px}</style></head><body>"
            + "".join(blocks) + "</body></html>")


def write_showcase(run_dirs: list[Path], out: Path | None = None) -> Path:
    if out is None:
        out = Path(__file__).resolve().parents[2] / "runs" / "showcase.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(showcase_html(run_dirs), encoding="utf-8")
    return out


def write_compare(run_dirs: list[Path], out: Path | None = None) -> Path:
    if out is None:
        out = Path(__file__).resolve().parents[2] / "runs" / f"compare_{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(compare_html(run_dirs), encoding="utf-8")
    return out
