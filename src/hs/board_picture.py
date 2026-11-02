"""The whiteboard as a picture (round 4 P4, after docs/design/board_mock.png): one board per meeting showing its
final state — functions as columns with sticky-note concepts, boxed calculations, pinned sketches, objections as
red ovals, the proposal frame with each member's vote. Everything is read from whiteboard.json; no model call."""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

PICTURE_STYLE = """<style>
.wb{background:#fdfdfb;border:14px solid #d9dde3;border-radius:16px;box-shadow:inset 0 0 40px rgba(0,0,0,.05),
  0 10px 30px rgba(0,0,0,.45);padding:22px 26px 18px;margin:14px 0 22px;font-family:'Chalkboard SE','Comic Sans MS',
  'Marker Felt',cursive;color:#222;position:relative}
.wb-top{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}
.wb h3{font-size:30px;margin:0;text-transform:uppercase;letter-spacing:1px;text-decoration:underline 3px}
.wb .who span{margin-right:16px;font-size:16px}
.wb .badge{display:inline-block;border:3px solid #c0392b;color:#c0392b;border-radius:22px;padding:2px 14px;
  font-size:16px;transform:rotate(-3deg);margin-top:8px}
.wb .prop{border:4px double #222;padding:10px 14px;max-width:440px;font-size:16px;background:#fff}
.wb .prop b{font-size:20px;text-transform:uppercase}
.wb .votes span{margin-right:12px;font-size:15px}
.wb .cols{display:grid;gap:18px;margin-top:20px}
.wb .col{border-left:3px dashed #b8bec7;padding-left:14px}
.wb .col:first-child{border-left:none;padding-left:0}
.wb .col h4{font-size:19px;margin:0 0 10px;border-bottom:3px solid #222;display:inline-block;text-transform:uppercase}
.wb .notes{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:14px}
.wb .note{display:block;padding:10px 12px;margin:0;box-shadow:2px 4px 8px rgba(0,0,0,.18);font-size:15px;
  line-height:1.3;position:relative}
.wb .note:nth-child(odd){transform:rotate(-1.2deg)} .wb .note:nth-child(even){transform:rotate(1deg)}
.wb .note small{display:block;font-size:12px;opacity:.75;margin-top:4px}
.wb .note.dropped{opacity:.5;text-decoration:line-through}
.wb .note.favored::after{content:'\\2605';position:absolute;top:-14px;right:-6px;font-size:28px;color:#f5b301}
.wb .ev{display:inline-block;border:3px solid #2e7d32;border-radius:6px;padding:4px 10px;margin:6px 8px 6px 0;
  font-size:15px;color:#1b5e20;background:#fff}
.wb .ev i{font-size:12px;color:#555;font-style:normal}
.wb .obj{display:inline-block;border:3px solid #c0392b;border-radius:50%;padding:12px 22px;margin:8px 10px 4px 0;
  color:#a93226;font-size:14px;max-width:360px;transform:rotate(-2deg)}
.wb .obj.resolved{text-decoration:line-through;opacity:.55;border-style:dashed}
.wb .pins img{height:150px;border:1px solid #ccc;margin:6px 10px 0 0;background:#fff;box-shadow:2px 3px 6px rgba(0,0,0,.2)}
.wb .tray{height:14px;background:linear-gradient(#cfd4da,#b9bfc6);border-radius:0 0 8px 8px;margin:16px -26px -18px;
  display:flex;justify-content:center;gap:36px;align-items:center}
.wb .tray i{display:block;width:90px;height:9px;border-radius:5px}
</style>"""

STICKY = ["#fff4a3", "#c9ecff", "#d7f5d0", "#ffd9e8", "#ffe4c2", "#e6dcff"]
INK = ["#1e6fb8", "#2e8b3a", "#c0392b", "#d4820a", "#0e7a7b", "#b03a5b"]


def _e(x: Any) -> str:
    return html.escape(str(x))


def _short(text: str, words: int = 26) -> str:
    """Whole sentences up to about `words` words (never cut mid-word)."""
    parts = re.split(r"(?<=[.!?;])\s+", " ".join(str(text).split()))
    out: list[str] = []
    for p in parts:
        if out and len(" ".join(out + [p]).split()) > words:
            break
        out.append(p)
    return " ".join(out)


STOP = {"a", "an", "and", "at", "for", "in", "of", "on", "or", "the", "to", "with", "per", "plus"}


def _clause(text: str, words: int = 6) -> str:
    """A short heading: the first clause, at most `words` words."""
    first = re.split(r",|;|:| — | - | with | so that | by | from | to keep ", " ".join(str(text).split()), maxsplit=1)[0]
    out = first.split()[:words]
    while len(out) > 2 and out[-1].lower() in STOP:
        out.pop()
    return " ".join(out)


def _note(text: str) -> str:
    text = re.sub(r"^[a-z]+(_[a-z]+)+:\s*", "", str(text).strip())  # drop a tag like "assumed_constraint:"
    return _short(text, 14) if len(text.split()) <= 18 else _clause(text, 14) + " …"


def _value(summary: str) -> str:
    text = re.sub(r"\s*mixed \(see keys\)", "", str(summary)).rstrip(", ")
    first = text.split(", ")[0]
    if "=" in first:
        key, _, val = first.partition("=")
        try:
            val = f"{float(val):.3g}"
        except ValueError:
            pass
        first = f"{key.replace('_', ' ')} = {val}"
    return " ".join(first.split()[:10])


def board_picture_html(board: dict[str, Any], run_dir: Path, iter_dir: Path, members: list[str], title: str,
                       cycles: int, max_cycles: int) -> str:
    color = {m: INK[i % len(INK)] for i, m in enumerate(members)}
    sticky = {m: STICKY[i % len(STICKY)] for i, m in enumerate(members)}
    first = {m: m.split(" —")[0].split(" - ")[0] for m in members}
    who = "".join(f"<span style='color:{color[m]}'>● {_e(first[m])}</span>" for m in members)
    prop = board.get("proposal")
    votes = board.get("votes", {})
    prop_html = ""
    if prop:
        ticks = "".join(
            f"<span style='color:{color.get(m, '#333')}'>{_e(first.get(m, m))} "
            f"{'✓' if v.get('ready') and v.get('version') == prop.get('version') else '…'}</span>"
            for m, v in votes.items())
        prop_html = (f"<div class='prop'><b>Proposal v{_e(prop.get('version'))}</b><br>{_e(_short(prop.get('text', ''), 40))}"
                     f"<div class='votes'>{ticks}</div></div>")
    funcs = board.get("functions", [])
    cols: list[str] = []
    concepts = board.get("concepts", [])
    for f in funcs[:4]:
        notes = "".join(
            f"<span class='note {_e(c.get('status', ''))}' style='background:{sticky.get(c.get('author'), '#fff4a3')}'>"
            f"{_e(_note(c.get('text', '')))}<small>— {_e(first.get(c.get('author'), c.get('author')))}</small></span>"
            for c in concepts if c.get("function_id") == f.get("id"))
        cols.append(f"<div class='col'><h4 title='{_e(f.get('text', ''))}'>{_e(f.get('id'))} · {_e(_clause(f.get('text', '')))}</h4>"
                    f"<div class='notes'>{notes or '<small>no concept pinned here</small>'}</div></div>")
    evidence = [e for e in board.get("evidence", []) if e.get("status") == "ok"
                and str(e.get("tool", "")).split(":")[0] in ("calc", "vetted_calc", "simulate")]
    ev_html = "".join(f"<span class='ev'>{_e(_clause(e.get('purpose', ''), 6))}: {_e(_value(e.get('output_summary', '')))} "
                      f"<i>{_e(e.get('id'))}</i></span>" for e in evidence[-8:])
    objs = "".join(f"<span class='obj {'resolved' if o.get('status') == 'resolved' else ''}'>? {_e(_short(o.get('text', ''), 16))}"
                   f"<br><small>— {_e(first.get(o.get('author'), o.get('author')))}, {_e(o.get('id'))}"
                   f" ({'resolved' if o.get('status') == 'resolved' else 'open'})</small></span>"
                   for o in board.get("objections", [])[-4:])
    pins = "".join(f"<img src='{_e((iter_dir / e['sketch_path']).relative_to(run_dir).as_posix())}' title='{_e(e.get('purpose', ''))}'>"
                   for e in board.get("evidence", []) if e.get("tool") == "sketch" and e.get("sketch_path")
                   and (iter_dir / e["sketch_path"]).exists())
    return (f"<div class='wb'><div class='wb-top'><div><h3>{_e(title)}</h3><div class='who'>{who}</div>"
            f"<span class='badge'>cycle {cycles} / {max_cycles}</span></div>{prop_html}</div>"
            f"<div class='cols' style='grid-template-columns:repeat({max(len(cols), 1)},1fr)'>{''.join(cols)}</div>"
            + (f"<div>{ev_html}</div>" if ev_html else "") + (f"<div>{objs}</div>" if objs else "")
            + (f"<div class='pins'>{pins}</div>" if pins else "") + "<div class='tray'>" + "".join(f"<i style='background:{c}'></i>" for c in INK[:5]) + "</div></div>")
