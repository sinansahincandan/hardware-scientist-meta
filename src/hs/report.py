"""hs report (one run) + hs compare (several runs), spec §8. Self-contained HTML."""
from __future__ import annotations

import html
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def _compare_img(path: Path) -> str:
    """Relative link from runs/ (where compare pages live) to a run's figure; no base64 (D20)."""
    if not path.exists():
        return "no figure"
    rel = os.path.relpath(path, Path(__file__).resolve().parents[2] / "runs")
    return f"<a href='{html.escape(rel)}'><img src='{html.escape(rel)}' style='max-width:240px'></a>"


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


def picture_rounds_html(run_dir: Path) -> str:
    """D22/item 16: every picture round as a strip — the render, the critic's verdict and notes, kept or
    reverted — then what the segmenter (SAM 3.1) saw on the last kept round. Read from the round folders."""
    import re

    trace = (run_dir / "trace.md").read_text(encoding="utf-8") if (run_dir / "trace.md").exists() else ""
    words = {"s1_pass": "faithful to the sketch — accepted", "s1_retry": "not yet faithful — prompt corrected",
             "s1_exhausted": "could not be drawn faithfully within the round limit",
             "s2_return": "showed a design flaw — back to the council"}
    cards: list[str] = []
    last_overlay = None
    for rd in sorted(run_dir.glob("stage_b/attempt_*/round_*")):
        ev = _read_json(rd / "eval.json")
        if not ev:
            continue
        a, n = int(rd.parent.name.split("_")[-1]), int(rd.name.split("_")[-1])
        dec = (rd / "decision.txt").read_text(encoding="utf-8").strip() if (rd / "decision.txt").exists() else ""
        kept = re.search(rf"attempt {a} round {n}: .*?; (kept|reverted) \(([^)]*)\)", trace)
        notes = "".join(f"<li>{html.escape(x.get('part_id', ''))}: {html.escape(x.get('observed', ''))}</li>"
                        for x in ev.get("regions", []))
        fixed = "".join(f"<li>{html.escape(x.get('part_id', ''))}: {html.escape(x.get('status', '').replace('_', ' '))}</li>"
                        for x in ev.get("previous_regions", []))
        rel = (rd / "render.png").relative_to(run_dir).as_posix()
        cards.append(
            f"<div class='round'><a href='{rel}'><img src='{rel}'></a><div><b>Picture {a + 1}, round {n + 1}:</b> "
            f"{html.escape(words.get(dec, dec))}"
            + (f" <span class='small'>({html.escape(kept.group(1))}: {html.escape(kept.group(2))})</span>" if kept else "")
            + (f"<p class='small'>Earlier faults now:</p><ul class='small'>{fixed}</ul>" if fixed else "")
            + (f"<p class='small'>What the critic flagged:</p><ul class='small'>{notes}</ul>" if notes else "")
            + "</div></div>")
        if (rd / "sam_overlay.png").exists() and (not kept or kept.group(1) == "kept"):
            last_overlay = rd / "sam_overlay.png"
    if not cards:
        return "<p>No picture rounds in this run.</p>"
    out = "".join(cards)
    if last_overlay is not None:
        rel = last_overlay.relative_to(run_dir).as_posix()
        out += ("<h3>What the segmenter saw (SAM 3.1)</h3><p class='small'>Code asked SAM for each part by a plain "
                "phrase and measured the boxes against what the design expects; the critic received the differences "
                f"as evidence.</p><a href='{rel}'><img src='{rel}' style='max-width:100%'></a>")
    return out


def council_changes_html(run_dir: Path) -> str:
    """B11: how each member's role block changed from one master prompt revision to the next."""
    import difflib
    from itertools import pairwise

    from hs.master_prompt import member_block, roster_of, split_master_prompt

    revs = sorted((run_dir / "master_prompt").glob("rev_*.md")) if (run_dir / "master_prompt").exists() else []
    if len(revs) < 2:
        return "<p>The council's instructions were not rewritten in this run.</p>"
    out: list[str] = []
    for old_path, new_path in pairwise(revs):
        old = split_master_prompt(old_path.read_text(encoding="utf-8"))
        new = split_master_prompt(new_path.read_text(encoding="utf-8"))
        old_roster, new_roster = roster_of(old), roster_of(new)
        items: list[str] = []
        for name in new_roster:
            if name not in old_roster:
                items.append(f"<li><b>{html.escape(name)}</b> joined the council.</li>")
                continue
            before, after = member_block(old, name), member_block(new, name)
            if before.strip() != after.strip():
                diff = [line for line in difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm="", n=0)
                        if line[:1] in "+-" and not line.startswith(("+++", "---"))]
                items.append(f"<li><b>{html.escape(name)}</b>'s instructions changed:<pre>"
                             + html.escape("\n".join(diff)) + "</pre></li>")
        items += [f"<li><b>{html.escape(n)}</b> left the council.</li>" for n in old_roster if n not in new_roster]
        n_new = int(new_path.stem.split("_")[-1])
        out.append(f"<h3>Revision {n_new}</h3>" + (f"<ul>{''.join(items)}</ul>" if items else
                                                    "<p>No member's instructions changed in this revision.</p>"))
    return "".join(out)


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
.round{display:flex;gap:16px;background:#fff;border-radius:10px;padding:12px;margin:10px 0;align-items:flex-start}
.round img{width:380px;flex:none}
</style>"""


def report_html(run_dir: Path) -> str:
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
        if (run_dir / "merged_from.json").exists():
            events.append(f"The council meeting below ran in run {html.escape(str(seeded.get('source_run', '')))}; "
                          "this run redrew its accepted solution.")
        else:
            events.append(f"This run redrew the accepted solution of run {html.escape(str(seeded.get('source_run', '')))}; "
                          "no council meeting ran in this run.")
    for entry in archive:
        k = int(entry.get("iteration", 0))
        iter_dir = run_dir / "stage_a" / f"iter_{k:02d}"
        closure = _read_json(iter_dir / "closure.json")
        if closure:
            closed = closure.get("closed_by", "")
            events.append(f"The council meeting {'closed by consensus' if closed == 'consensus' else ('closed by the chief designer’s decision' if closed == 'chief' else 'reached the cycle cap without consensus')} "
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
            what = (f"The picture could not be drawn faithfully after {n_rounds} rounds. This was reported to the "
                    "Manager as a drawing failure, not as a design flaw; the Manager decided whether the design "
                    "needed more detail.")
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
    parts.append("<h2>How the picture was made</h2>" + picture_rounds_html(run_dir))
    parts.append("<h2>How the council changed</h2>" + council_changes_html(run_dir))
    # 5. References
    refs = _read_text(run_dir / "references.md")
    parts.append("<h2>References</h2>")
    if refs:
        items = [l for l in refs.splitlines() if l and not l.startswith("#")]
        parts.append(f"<details><summary>{len(items)} sources found by the council's searches and the prior-art "
                     "check (click to open)</summary><ol class='small'>" + "".join(
                         f"<li>{html.escape(l.split('. ', 1)[-1])}</li>" for l in items) + "</ol></details>")
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


def write_report(run_dir: Path) -> Path:
    out = run_dir / "report.html"
    out.write_text(report_html(run_dir), encoding="utf-8")
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
            f"<td>{_compare_img(run_dir / 'final' / 'figure.png')}</td>"
            f"<td>${float(cost.get('total_usd', 0)):.4f}</td></tr>")
    return ("<!doctype html><html><head><meta charset='utf-8'><title>Compare</title></head><body>"
            "<h1>Compare</h1><table border='1'><tr><th>Problem</th><th>Iterations to accept</th>"
            "<th>Closures</th><th>Accept/reject sequence</th><th>S1 rounds</th><th>Returns B→A</th>"
            "<th>Figure</th><th>Cost</th></tr>" + "".join(rows) + "</table></body></html>")


def write_compare(run_dirs: list[Path], out: Path | None = None) -> Path:
    if out is None:
        out = Path(__file__).resolve().parents[2] / "runs" / f"compare_{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(compare_html(run_dirs), encoding="utf-8")
    return out
