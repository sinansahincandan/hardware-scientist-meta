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


def report_html(run_dir: Path, embed: bool = True) -> str:
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


def write_report(run_dir: Path, embed: bool = True) -> Path:
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


def write_compare(run_dirs: list[Path], out: Path | None = None) -> Path:
    if out is None:
        out = Path("runs") / f"compare_{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(compare_html(run_dirs), encoding="utf-8")
    return out
