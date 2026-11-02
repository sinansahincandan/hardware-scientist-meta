"""hs board: the meeting as a whiteboard you can follow (round-3 D21, after docs/design/board_mock.png).

One section per cycle, turns in speaking order. Each turn is a card: who spoke, one plain sentence,
and what they put on the board — concepts as sticky notes, calculations as boxed results, sketches
large enough to read, searches grouped by query, objections linked to their resolution, votes. The full
message is folded away. Each cycle ends with the proposal as it stood then. Between meetings: the
Evaluator's verdict and the Manager's change, in plain words. Everything is read from the run's files;
no raw tool output is shown.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from hs import config
from hs.board_picture import PICTURE_STYLE, board_picture_html
from hs.stage_a.whiteboard import Whiteboard

MANAGER_COLOR = "#7d3c98"
MEMBER_COLORS = ["#1e6fb8", "#2e8b3a", "#c0392b", "#d4820a", "#0e7a7b", "#b03a5b"]
STICKY = ["#fff4a3", "#c9ecff", "#d7f5d0", "#ffd9e8", "#ffe4c2", "#e6dcff"]

STYLE = """<style>
body{background:#23272e;font-family:'Segoe UI',Helvetica,Arial,sans-serif;margin:0;color:#222}
header.page{max-width:1120px;margin:0 auto;padding:26px 22px 4px}
header.page h1{color:#fff;font-size:28px;margin:0 0 6px}
header.page p{color:#c9d1d9;margin:0 0 10px}
nav{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}
nav a{background:#2e8b3a;color:#fff;border-radius:10px;padding:4px 12px;text-decoration:none;font-size:13px}
.board{background:#fbfaf6;border-radius:14px;max-width:1120px;margin:14px auto;padding:20px 28px;
  box-shadow:0 8px 30px rgba(0,0,0,.5)}
.board h2{font-family:'Chalkboard SE','Comic Sans MS',cursive;font-size:24px;border-bottom:3px solid #222;padding-bottom:5px}
.legend span{display:inline-block;margin:0 14px 6px 0;font-weight:600}
.cycle h3{font-family:'Chalkboard SE','Comic Sans MS',cursive;font-size:20px;margin:26px 0 8px}
.card{background:#fff;border:1px solid #e3e0d8;border-radius:10px;padding:12px 16px;margin:10px 0;
  box-shadow:1px 2px 5px rgba(0,0,0,.07)}
.card .who{font-weight:700}
.card .sum{margin:4px 0 8px;font-size:16px}
.card details{margin-top:8px}.card summary{cursor:pointer;color:#666;font-size:13px}
.card details p{white-space:pre-wrap;font-size:14px;color:#333}
.sticky{display:inline-block;padding:9px 12px;margin:5px 6px 5px 0;border-radius:3px;max-width:320px;
  vertical-align:top;font-family:'Chalkboard SE','Comic Sans MS',cursive;font-size:15px;box-shadow:2px 3px 6px rgba(0,0,0,.15)}
.sticky small{display:block;color:#555;font-family:'Segoe UI',sans-serif;font-size:12px;margin-top:4px}
.calc{display:inline-block;border:2px solid #2e7d32;border-radius:6px;padding:6px 10px;margin:5px 6px 5px 0;
  font-size:14px;background:#f4faf4;max-width:520px}
.calc b{color:#2e7d32}
.search{font-size:14px;margin:6px 0}.search li{margin:2px 0}
figure.sketch{display:inline-block;margin:8px 10px 8px 0;vertical-align:top}
figure.sketch img{width:440px;max-width:100%;border:1px solid #ccc;border-radius:6px;background:#fff}
figure.sketch figcaption{font-size:13px;color:#444;max-width:440px}
.objection{border:2px solid #c0392b;border-radius:16px;padding:7px 12px;margin:6px 0;color:#7b241c;background:#fff;font-size:14px}
.resolution{border-left:4px solid #2e8b3a;padding:4px 10px;margin:6px 0;font-size:14px;color:#1d5e26}
.vote{font-size:14px;margin:4px 0}
.proposal{border:3px double #222;border-radius:6px;padding:10px 14px;background:#fff;margin:14px 0}
.manager{border-left:6px solid #7d3c98}
.verdict{background:#fff7e0;border:1px solid #d8a920;border-radius:8px;padding:10px 14px;margin:12px 0}
.small{color:#666;font-size:13px}
</style>"""


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _records(iter_dir: Path) -> list[dict[str, Any]]:
    p = iter_dir / "whiteboard_history.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def _turns(iter_dir: Path, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Turns in speaking order (the order of turn_end records), with their messages."""
    files = {}
    for f in sorted((iter_dir / "turns").glob("*.json")) if (iter_dir / "turns").exists() else []:
        t = _read(f)
        if t:
            files[(int(t.get("cycle", 0)), str(t.get("member", "")))] = t
    order = [(int(r.get("cycle", 0)), str(r.get("member", ""))) for r in records if r.get("kind") == "turn_end"]
    seen: list[tuple[int, str]] = []
    for key in order + sorted(files):
        if key not in seen and key in files:
            seen.append(key)
    return [files[k] for k in seen]


def _e(s: Any) -> str:
    return html.escape(str(s))


def _sentence(text: str) -> str:
    """The first sentence, whole (never cut mid-word)."""
    flat = " ".join(str(text).split())
    parts = re.split(r"(?<=[.!?])\s+", flat)
    return parts[0] if parts else flat


def _round3(text: str) -> str:
    """Numbers with more than three significant figures shown with three (older evidence)."""
    from hs.stage_a.tools import _NUMBER, _three_sig

    return _NUMBER.sub(_three_sig, text)


def _failure_words(summary: str) -> str:
    """B9: a failed tool run in plain words on the page (members still get the full error in their turn)."""
    low = summary.lower()
    if "dimensionality" in low or "cannot convert" in low:
        return "failed: the units did not match"
    if "timeout" in low:
        return "failed: the calculation took too long"
    if "not allowed" in low or "permission" in low:
        return "failed: the code used something the sandbox does not allow"
    if "syntax" in low:
        return "failed: the code had a typing error"
    return "failed: the calculation did not run"


def board_html(run_dir: Path, *, fragment: bool = False, live: bool = False) -> str:
    problem = _read(run_dir / "problem.json")
    title = str(problem.get("title", run_dir.name))
    iter_dirs = sorted((run_dir / "stage_a").glob("iter_*")) if (run_dir / "stage_a").exists() else []
    nav: list[str] = []
    sections: list[str] = []
    if not iter_dirs and (run_dir / "seeded_from.json").exists():
        seeded = _read(run_dir / "seeded_from.json")
        sections.append(f"<section class='board'><p>No council meeting ran in this run: it redrew the accepted "
                        f"solution of run {_e(seeded.get('source_run', ''))}.</p></section>")
    for iter_dir in iter_dirs:
        n = int(iter_dir.name.split("_")[-1]) + 1
        records = _records(iter_dir)
        turns = _turns(iter_dir, records)
        final = Whiteboard.load(iter_dir / "whiteboard.json") if (iter_dir / "whiteboard.json").exists() else None
        evidence = {e.id: e for e in final.evidence} if final else {}
        members = list(dict.fromkeys(str(t.get("member")) for t in turns if t.get("member") != "Manager"))
        color = {m: MEMBER_COLORS[i % len(MEMBER_COLORS)] for i, m in enumerate(members)}
        color["Manager"] = MANAGER_COLOR
        sticky = {m: STICKY[i % len(STICKY)] for i, m in enumerate(members)}
        status = {c.id: c.status for c in final.concepts} if final else {}
        resolved_by: dict[str, str] = {}
        for r in records:
            op = r.get("op") or {}
            if r.get("kind") == "op" and r.get("ok") and op.get("action") == "resolve_objection":
                oid = str(op.get("id", ""))
                resolved_by[oid] = (f"resolved in cycle {r.get('cycle')} by {_e(r.get('member'))}: "
                                    f"{_e(op.get('resolution', ''))}")
        nav.append(f"<a href='#{iter_dir.name}'>Meeting {n}</a>")
        body = [f"<section class='board' id='{iter_dir.name}'><h2>Meeting {n}</h2>"
                "<p class='legend'>" + "".join(f"<span style='color:{color[m]}'>● {_e(m)}</span>" for m in members)
                + f"<span style='color:{MANAGER_COLOR}'>● Manager (process lead)</span></p>"]
        raw_board = _read(iter_dir / "whiteboard.json")
        if raw_board:
            closure_info = _read(iter_dir / "closure.json")
            used = int(closure_info.get("cycles_used") or max((int(t.get("cycle", 0)) for t in turns), default=0))
            body.append("<p class='small'>The board as it stood when the meeting closed; the turns that built it follow.</p>"
                        + board_picture_html(raw_board, run_dir, iter_dir, members, title, used, config.MAX_CYCLES))
        proposal_text, proposal_v = "", 0
        for cycle in sorted({int(t.get("cycle", 0)) for t in turns}):
            body.append(f"<div class='cycle'><h3>Cycle {cycle}</h3>")
            votes_in_cycle: dict[str, str] = {}
            for turn in [t for t in turns if int(t.get("cycle", 0)) == cycle]:
                member = str(turn.get("member", ""))
                msg = str(turn.get("message", ""))
                added: list[str] = []
                searches: dict[str, list[str]] = {}
                for r in records:
                    if int(r.get("cycle", 0)) != cycle or str(r.get("member", "")) != member:
                        continue
                    if r.get("kind") == "evidence":
                        ev = evidence.get(str(r.get("evidence_id")))
                        if ev is None:
                            continue
                        if ev.tool == "web_search":
                            ref = (ev.references or [{}])[0]
                            searches.setdefault(ev.purpose.removeprefix("search: "), []).append(
                                f"<li>{_e(ev.id)} · {_e(ref.get('title', ''))} ({_e(ref.get('authors_or_org', ''))}"
                                f"{', ' + _e(ref.get('year')) if ref.get('year') else ''}) "
                                f"<a href='{_e(ref.get('url', ''))}'>link</a></li>")
                        elif ev.tool == "sketch" and ev.sketch_path:
                            src = (iter_dir / ev.sketch_path).relative_to(run_dir).as_posix()
                            added.append(f"<figure class='sketch'><a href='{_e(src)}'><img src='{_e(src)}'></a>"
                                         f"<figcaption>{_e(ev.id)} · {_e(ev.purpose)}</figcaption></figure>")
                        else:
                            result = (_failure_words(ev.output_summary) if ev.status == "error"
                                      else _round3(ev.output_summary))
                            added.append(f"<span class='calc'><b>{_e(ev.id)}</b> {_e(ev.purpose)}: {_e(result)}</span>")
                        continue
                    op = r.get("op") or {}
                    if r.get("kind") != "op" or not r.get("ok"):
                        continue
                    action, oid = op.get("action"), str(r.get("msg", ""))
                    if action == "add_concept":
                        cls = {"favored": " ★ favored", "dropped": " (dropped)"}.get(status.get(oid, ""), "")
                        added.append(f"<span class='sticky' style='background:{sticky.get(member, '#fff4a3')}'>"
                                     f"{_e(op.get('text', ''))}<small>{_e(oid)} for {_e(op.get('function_id', ''))}"
                                     f"{cls}</small></span>")
                    elif action == "add_function":
                        added.append(f"<p><b>Function {_e(oid)}:</b> {_e(op.get('text', ''))}</p>")
                    elif action == "raise_objection":
                        after = resolved_by.get(oid, "still open at the end of the meeting")
                        added.append(f"<div class='objection' id='{_e(iter_dir.name)}-{_e(oid)}'><b>{_e(oid)}"
                                     f"{' (blocking)' if op.get('blocking') else ''}</b> on {_e(op.get('target_id', ''))}: "
                                     f"{_e(op.get('text', ''))}<br><span class='small'>{after}</span></div>")
                    elif action == "resolve_objection":
                        rid = str(op.get("id", ""))
                        added.append(f"<div class='resolution'>Resolved <a href='#{_e(iter_dir.name)}-{_e(rid)}'>"
                                     f"{_e(rid)}</a>: {_e(op.get('resolution', ''))}</div>")
                    elif action == "vote":
                        word = "ready" if op.get("ready") else "not ready"
                        votes_in_cycle[member] = word
                        added.append(f"<div class='vote'><b>Vote: {word}</b> — {_e(op.get('reason', ''))}</div>")
                    elif action == "update_proposal":
                        proposal_text, proposal_v = str(op.get("text", "")), proposal_v + 1
                        added.append(f"<div class='proposal'><b>Wrote proposal v{proposal_v}:</b> "
                                     f"{_e(proposal_text)}</div>")
                for query, items in searches.items():
                    added.append(f"<details class='search'><summary>Searched “{_e(query)}” → {len(items)} "
                                 f"source{'s' if len(items) != 1 else ''} on the board</summary><ul>{''.join(items)}</ul></details>")
                cls = "card manager" if member == "Manager" else "card"
                body.append(f"<div class='{cls}'><span class='who' style='color:{color.get(member, '#333')}'>"
                            f"{_e(member)}</span><div class='sum'>{_e(_sentence(msg))}</div>{''.join(added)}"
                            f"<details><summary>Full message</summary><p>{_e(msg)}</p></details></div>")
            if proposal_text:
                votes = ", ".join(f"{_e(m)}: {v}" for m, v in votes_in_cycle.items()) or "no votes in this cycle"
                body.append(f"<div class='proposal'><b>Proposal at the end of cycle {cycle} (v{proposal_v}):</b> "
                            f"{_e(proposal_text)}<br><span class='small'>Votes this cycle: {votes}</span></div>")
            else:
                body.append(f"<p class='small'>No proposal on the board at the end of cycle {cycle}.</p>")
            body.append("</div>")
        closure = _read(iter_dir / "closure.json")
        if closure:
            body.append(f"<p class='small'>The meeting closed "
                        f"{'by consensus' if closure.get('closed_by') == 'consensus' else 'at the cycle cap without consensus'} "
                        f"after {closure.get('cycles_used')} cycles.</p>")
        verdict = _read(iter_dir / "verdict.json")
        if verdict:
            parts = re.split(r"(?<=[.!?])\s+", " ".join(str(verdict.get("feedback", "")).split()))
            body.append(f"<div class='verdict'><b>The Evaluator {'accepted the concept' if verdict.get('accept') else 'sent the concept back'}.</b> "
                        f"{_e(' '.join(parts[:2]))}</div>")
        edit = _read(iter_dir / "manager_edit.json")
        if edit:
            changed = edit.get("changed") or []
            plain = [re.sub(r"^#+\s*\d+\.\s*", "", h).lower() for h in changed]
            what = ("rewrote the council's " + ", ".join(plain)) if changed else "changed no section of the council's instructions"
            body.append(f"<div class='verdict'><b>The Manager {_e(what)}.</b> {_e(_sentence(edit.get('change_note', '')))}</div>")
        sections.append("".join(body) + "</section>")
    header = (f"<header class='page'><h1>{_e(title)}</h1>"
              f"<p>The council's whiteboard — who said what, what they computed, searched and sketched, "
              f"and how the design changed.</p><nav>{''.join(nav)}</nav></header>")
    body_html = header + "".join(sections)
    if fragment:
        return STYLE + PICTURE_STYLE + body_html
    refresh = '<meta http-equiv="refresh" content="5">' if live else ""
    return (f"<!doctype html><html><head><meta charset='utf-8'>{refresh}<title>Board — {_e(title)}</title>"
            f"{STYLE}{PICTURE_STYLE}</head><body>{body_html}</body></html>")


def write_board(run_dir: Path, live: bool = False) -> Path:
    out = run_dir / "board.html"
    out.write_text(board_html(run_dir, live=live), encoding="utf-8")
    return out
