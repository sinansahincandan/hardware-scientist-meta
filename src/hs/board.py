"""hs board: a readable meeting page (v2 F4).

One section per cycle, in time order. Every turn is a card: who spoke, a
one-line summary, then what they added (concepts, sketches, calculations
with units, citations, objections, votes). Objections link to their
resolution. The proposal closes each cycle. Between iterations: the
evaluator's verdict and the Manager's change, in plain words.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hs.stage_a.whiteboard import Whiteboard

MANAGER_COLOR = "#8e44ad"
MEMBER_COLORS = ["#1e6fb8", "#2e8b3a", "#c0392b", "#d4820a", "#0e7a7b", "#b03a5b"]

STYLE = """<style>
body{background:#23272e;font-family:'Segoe UI',Helvetica,Arial,sans-serif;margin:0;color:#222}
header.page{max-width:1100px;margin:0 auto;padding:26px 22px 4px}
header.page h1{color:#fff;font-size:28px;margin:0 0 6px}
header.page p{color:#c9d1d9;margin:0 0 10px}
nav{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}
nav a{background:#2e8b3a;color:#fff;border-radius:10px;padding:4px 12px;text-decoration:none;font-size:13px}
.board{background:#f7f5ef;border-radius:14px;max-width:1100px;margin:14px auto;padding:20px 26px;box-shadow:0 8px 30px rgba(0,0,0,.5)}
.board h2{font-size:20px;border-bottom:3px solid #222;padding-bottom:5px}
.cycle h3{font-size:17px;margin:22px 0 8px}
.card{background:#fff;border:1px solid #ddd;border-radius:10px;padding:12px 16px;margin:10px 0;box-shadow:1px 2px 5px rgba(0,0,0,.08)}
.card .who{font-weight:700}
.card .sum{font-style:italic;color:#444;margin:4px 0 8px}
.sticky{display:inline-block;padding:7px 10px;margin:4px;border:1px solid rgba(0,0,0,.25);border-radius:4px;max-width:300px;vertical-align:top;font-size:14px}
.dropped{opacity:.45;text-decoration:line-through}.favored{outline:3px solid #f5b301}
.evidence{border:2px solid #2e7d32;border-radius:6px;padding:6px 10px;margin:6px 0;font-size:14px;background:#f4faf4}
.objection{border:2px solid #c0392b;border-radius:14px;padding:7px 12px;margin:6px 0;color:#7b241c;background:#fff;font-size:14px}
.objection.resolved{opacity:.6}
.proposal{border:3px double #222;border-radius:6px;padding:10px 14px;background:#fff;margin:12px 0}
.manager{border-left:6px solid #8e44ad}
.verdict{background:#fff7e0;border:1px solid #d8a920;border-radius:8px;padding:10px 14px;margin:12px 0}
img.sketch{max-width:420px;border:1px solid #ccc;border-radius:6px}
.small{color:#666;font-size:13px}
</style>"""


def _records(iter_dir: Path) -> list[dict[str, Any]]:
    p = iter_dir / "whiteboard_history.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _turns(iter_dir: Path) -> list[dict[str, Any]]:
    out = []
    tdir = iter_dir / "turns"
    if tdir.exists():
        for f in sorted(tdir.glob("*.json")):
            try:
                out.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:  # noqa: S112 — unreadable turn file is skipped
                continue
    out.sort(key=lambda t: (int(t.get("cycle", 0)), str(t.get("member", "")) == "Manager", str(t.get("member", ""))))
    return out


def _added_by_turn(records: list[dict[str, Any]]) -> dict[tuple[int, str], list[dict[str, Any]]]:
    added: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for rec in records:
        if rec.get("kind") in ("op", "evidence"):
            added.setdefault((int(rec.get("cycle", 0)), str(rec.get("member", ""))), []).append(rec)
    return added


def _escape(s: Any) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _first_sentence(text: str) -> str:
    text = " ".join(str(text).split())
    for sep in (". ", ".\n"):
        if sep in text:
            return text.split(sep)[0] + "."
    return text[:160]


def board_html(run_dir: Path, *, fragment: bool = False, live: bool = False) -> str:
    problem = {}
    try:
        problem = json.loads((run_dir / "problem.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    title = str(problem.get("title", run_dir.name))
    iter_dirs = sorted((run_dir / "stage_a").glob("iter_*")) if (run_dir / "stage_a").exists() else []
    members: list[str] = []
    nav: list[str] = []
    sections: list[str] = []
    for iter_dir in iter_dirs:
        records = _records(iter_dir)
        turns = _turns(iter_dir)
        added = _added_by_turn(records)
        board_path = iter_dir / "whiteboard.json"
        final = Whiteboard.load(board_path) if board_path.exists() else None
        if final:
            for c in final.concepts:
                if c.author not in members:
                    members.append(c.author)
            for t in turns:
                if t.get("member") not in members and t.get("member") != "Manager":
                    members.append(str(t.get("member")))
        sketch_files = {p.name: p.relative_to(run_dir).as_posix()
                        for p in (run_dir / "stage_a").glob("iter_*/evidence/sketch_*.png")}
        color = {m: MEMBER_COLORS[i % len(MEMBER_COLORS)] for i, m in enumerate(members)}
        color["Manager"] = MANAGER_COLOR
        nav.append(f"<a href='#{iter_dir.name}'>{iter_dir.name.replace('_', ' ')}</a>")
        body: list[str] = [f"<section class='board' id='{iter_dir.name}'><h2>{iter_dir.name.replace('_', ' ')} — the meeting</h2>"]
        cycles = sorted({int(t.get("cycle", 0)) for t in turns} | {int(r.get("cycle", 0)) for r in records})
        for cycle in cycles:
            body.append(f"<div class='cycle'><h3 id='{iter_dir.name}-c{cycle}'>Cycle {cycle}</h3>")
            for turn in [t for t in turns if int(t.get("cycle", 0)) == cycle]:
                member = str(turn.get("member", ""))
                msg = str(turn.get("message", ""))
                items: list[str] = []
                for rec in added.get((cycle, member), []):
                    if rec.get("kind") == "evidence":
                        ev = None
                        if final:
                            ev = next((e for e in final.evidence if e.id == rec.get("evidence_id")), None)
                        if ev is not None:
                            refs = "".join(f"<br><span class='small'>[{i + 1}] {_escape(r.get('authors_or_org', ''))} — "
                                           f"{_escape(r.get('title', ''))} {_escape(r.get('url', ''))}</span>"
                                           for i, r in enumerate(ev.references))
                            sketch = ""
                            if ev.sketch_path and Path(ev.sketch_path).name in sketch_files:
                                sketch = (f"<br><img class='sketch' src='{sketch_files[Path(ev.sketch_path).name]}'>")
                            items.append(f"<div class='evidence'><b>{ev.id}</b> [{_escape(ev.tool)}] "
                                         f"{_escape(ev.output_summary)}{refs}{sketch}</div>")
                        else:
                            items.append(f"<div class='evidence'><b>{rec.get('evidence_id')}</b> [{_escape(rec.get('tool', ''))}]</div>")
                    else:
                        op = dict(rec.get("op", {}))
                        action = str(op.get("action", ""))
                        if action == "add_concept":
                            items.append(f"<div class='sticky'><b>{_escape(op.get('id', ''))}</b> {_escape(op.get('text', ''))}</div>")
                        elif action == "add_function":
                            items.append(f"<p><b>Function {_escape(op.get('id', ''))}:</b> {_escape(op.get('text', ''))}</p>")
                        elif action == "raise_objection":
                            items.append(f"<div class='objection' id='{_escape(op.get('id', ''))}'><b>{_escape(op.get('id', ''))}</b> "
                                         f"[{_escape(member)} → {_escape(op.get('target_id', ''))}] {_escape(op.get('text', ''))}</div>")
                        elif action == "resolve_objection":
                            items.append(f"<p>Resolved <a href='#{_escape(op.get('id', ''))}'>{_escape(op.get('id', ''))}</a>: "
                                         f"{_escape(op.get('resolution', ''))}</p>")
                        elif action == "vote":
                            items.append(f"<p><b>Vote:</b> {'ready' if op.get('ready') else 'not ready'} — {_escape(op.get('reason', ''))}</p>")
                        elif action == "update_proposal":
                            items.append(f"<div class='proposal'><b>Proposal updated:</b> {_escape(op.get('text', ''))}</div>")
                cls = "card manager" if member == "Manager" else "card"
                body.append(f"<div class='{cls}'><span class='who' style='color:{color.get(member, '#333')}'>"
                            f"{_escape(member)}</span><div class='sum'>{_escape(_first_sentence(msg))}</div>"
                            f"<p>{_escape(msg)}</p>{''.join(items)}</div>")
            if final and final.proposal and cycles and cycle == max(cycles):
                body.append(f"<div class='proposal'><b>Current proposal (v{final.proposal.version})</b> "
                            f"[{_escape(final.proposal.author)}]: {_escape(final.proposal.text)}<br>"
                            f"<span class='small'>Changed during the meeting; votes on the cards above.</span></div>")
            body.append("</div>")
        verdict = {}
        try:
            verdict = json.loads((iter_dir / "verdict.json").read_text(encoding="utf-8"))
        except Exception:
            pass
        if verdict:
            body.append(f"<div class='verdict'><b>Evaluator:</b> "
                        f"{'accepted the concept' if verdict.get('accept') else 'sent the concept back'} — "
                        f"{_escape(_first_sentence(str(verdict.get('feedback', ''))))}</div>")
        diagnosis = {}
        try:
            diagnosis = json.loads((iter_dir / "gradient_prompt.json").read_text(encoding="utf-8"))
        except Exception:
            try:
                diagnosis = json.loads((iter_dir / "diagnosis.json").read_text(encoding="utf-8"))
            except Exception:
                diagnosis = {}
        if diagnosis:
            body.append(f"<div class='verdict'><b>The Manager's change:</b> {_escape(diagnosis.get('agenda', '') or diagnosis.get('root_cause', ''))} "
                        f"<span class='small'>(full record: gradient_output.json / gradient_prompt.json in this iteration)</span></div>")
        sections.append("".join(body) + "</section>")
    header = (f"<header class='page'><h1>{_escape(title)}</h1>"
              f"<p>Council whiteboard — who said what, what they computed, and how the design changed.</p>"
              f"<nav>{''.join(nav)}</nav></header>")
    body_html = header + "".join(sections)
    if fragment:
        return STYLE + body_html
    refresh = '<meta http-equiv="refresh" content="5">' if live else ""
    return (f"<!doctype html><html><head><meta charset='utf-8'>{refresh}<title>Board — {_escape(title)}</title>"
            f"{STYLE}</head><body>{body_html}</body></html>")


def write_board(run_dir: Path, live: bool = False) -> Path:
    out = run_dir / "board.html"
    out.write_text(board_html(run_dir, live=live), encoding="utf-8")
    return out
