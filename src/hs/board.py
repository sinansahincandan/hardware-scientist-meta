"""hs board: whiteboard replay HTML (spec §8). Rendered from history + transcript + evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hs.stage_a.whiteboard import Whiteboard

COLORS = ["#ffe082", "#a5d6a7", "#90caf9", "#f48fb1", "#ce93d8", "#ffcc80"]


def _snapshots(iter_dir: Path) -> tuple[list[dict[str, Any]], Whiteboard | None, list[dict[str, Any]]]:
    board_path = iter_dir / "whiteboard.json"
    final = Whiteboard.load(board_path) if board_path.exists() else None
    history_path = iter_dir / "whiteboard_history.jsonl"
    records: list[dict[str, Any]] = []
    if history_path.exists():
        records = [json.loads(l) for l in history_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    board = Whiteboard()
    if final is not None:
        board.inspirations = final.inspirations
    snapshots: list[dict[str, Any]] = []
    ev_count = 0
    for rec in records:
        if rec.get("kind") == "evidence":
            ev_count += 1
        elif rec.get("kind") == "op":
            board.apply_op(str(rec.get("member", "")), dict(rec.get("op", {})))
        snapshots.append({
            "label": f"cycle {rec.get('cycle', '?')} · {rec.get('member', '')} · {rec.get('kind', '')}",
            "functions": [f.model_dump() for f in board.functions],
            "concepts": [c.model_dump() for c in board.concepts],
            "objections": [o.model_dump() for o in board.objections],
            "proposal": board.proposal.model_dump() if board.proposal else None,
            "votes": {k: v.model_dump() for k, v in board.votes.items()},
            "evidence": [e.model_dump() for e in (final.evidence[:ev_count] if final else [])],
        })
    if not snapshots and final is not None:
        snapshots.append({
            "label": "final", "functions": [f.model_dump() for f in final.functions],
            "concepts": [c.model_dump() for c in final.concepts],
            "objections": [o.model_dump() for o in final.objections],
            "proposal": final.proposal.model_dump() if final.proposal else None,
            "votes": {k: v.model_dump() for k, v in final.votes.items()},
            "evidence": [e.model_dump() for e in final.evidence],
        })
    transcript: list[dict[str, Any]] = []
    for turn_file in sorted((iter_dir / "turns").glob("*.json")) if (iter_dir / "turns").exists() else []:
        transcript.append(json.loads(turn_file.read_text(encoding="utf-8")))
    return snapshots, final, transcript


def board_html(run_dir: Path, *, fragment: bool = False, live: bool = False) -> str:
    iter_dirs = sorted((run_dir / "stage_a").glob("iter_*")) if (run_dir / "stage_a").exists() else []
    sections: list[str] = []
    all_snapshots: list[dict[str, Any]] = []
    legend_members: list[str] = []
    for iter_dir in iter_dirs:
        snapshots, final, transcript = _snapshots(iter_dir)
        all_snapshots.extend(snapshots)
        if final is not None:
            for c in final.concepts:
                if c.author not in legend_members:
                    legend_members.append(c.author)
        # static (no-JS) rendering of the final board for this iteration
        cards: list[str] = []
        if final is not None:
            if final.proposal:
                cards.append(f"<div class='proposal'><b>Proposal v{final.proposal.version}</b> "
                             f"[{final.proposal.author}] {final.proposal.text}</div>")
            vote_dots = " ".join(
                f"<span class='dot {'ready' if v.ready else 'notready'}' title='{m}: {v.reason}'>{m[0]}</span>"
                for m, v in final.votes.items())
            cards.append(f"<div class='votes'>Votes: {vote_dots}</div>")
            for f in final.functions:
                cards.append(f"<h3>{f.id} — {f.text}</h3>")
                for c in [x for x in final.concepts if x.function_id == f.id]:
                    color = COLORS[legend_members.index(c.author) % len(COLORS)] if c.author in legend_members else "#eee"
                    cls = "sticky dropped" if c.status == "dropped" else ("sticky favored" if c.status == "favored" else "sticky")
                    cards.append(f"<div class='{cls}' style='background:{color}'><b>{c.id}</b> [{c.author}] {c.text}</div>")
            for e in final.evidence:
                sketch = ""
                if e.sketch_path:
                    rel = f"stage_a/{iter_dir.name}/{e.sketch_path}"
                    sketch = f"<br><img src='{rel}' style='max-width:220px'>"
                cards.append(f"<div class='evidence'><b>{e.id} · {e.output_summary}</b> "
                             f"[{e.tool}, {e.author}] purpose: {e.purpose}{sketch}"
                             f"<details><summary>code/query</summary><pre>{e.code_or_query}</pre>"
                             f"<pre>{e.output_full}</pre></details></div>")
            for o in final.objections:
                cls = "objection resolved" if o.status == "resolved" else "objection"
                strike = "style='text-decoration:line-through'" if o.status == "resolved" else ""
                cards.append(f"<div class='{cls}'><b>{o.id}</b> [{o.author} → {o.target_id}] "
                             f"<span {strike}>{o.text}</span> resolution: {o.resolution} evidence={o.evidence_ids}</div>")
            for t in transcript:
                cards.append(f"<div class='msg'><b>Cycle {t.get('cycle')} — {t.get('member')}</b>: {t.get('message', '')}</div>")
        sections.append(f"<section><h2>{iter_dir.name}</h2>{''.join(cards)}</section>")
    legend = " ".join(
        f"<span class='sticky' style='background:{COLORS[i % len(COLORS)]}'>{m}</span>"
        for i, m in enumerate(legend_members))
    slider = (
        f"<div class='timeline'><label>Timeline: <input type='range' id='step' min='0' "
        f"max='{max(len(all_snapshots) - 1, 0)}' value='{max(len(all_snapshots) - 1, 0)}'></label>"
        f"<button onclick='play()'>Play/Pause</button> <span id='stepLabel'></span></div>"
        f"<script>const snaps={json.dumps(all_snapshots)};"
        "function show(i){document.getElementById('stepLabel').textContent=snaps.length?snaps[i].label:'';}"
        "document.getElementById('step').addEventListener('input',e=>show(+e.target.value));"
        "let timer=null;function play(){if(timer){clearInterval(timer);timer=null;return;}"
        "let s=document.getElementById('step');timer=setInterval(()=>{s.value=(+s.value+1)%(snaps.length||1);show(+s.value);},900);}"
        "show(snaps.length-1);</script>"
    )
    body = (f"<h1>Whiteboard replay — {run_dir.name}</h1><div class='legend'>{legend}</div>"
            f"{slider}{''.join(sections)}")
    style = ("<style>.sticky{display:inline-block;padding:8px;margin:4px;border:1px solid #999;max-width:240px;vertical-align:top}"
             ".dropped{opacity:.45}.favored{outline:3px solid gold}.evidence{border:1px solid teal;padding:6px;margin:4px}"
             ".objection{border:2px solid red;padding:6px;margin:4px}.proposal{border:2px solid #333;padding:8px}"
             ".dot{display:inline-block;border-radius:50%;border:1px solid #333;padding:2px 6px;margin:2px}"
             ".ready{background:#a5d6a7}.msg{border-left:3px solid #90caf9;padding:4px;margin:4px}</style>")
    if fragment:
        return style + body
    refresh = '<meta http-equiv="refresh" content="5">' if live else ""
    return (f"<!doctype html><html><head><meta charset='utf-8'>{refresh}<title>Board {run_dir.name}</title>"
            f"{style}</head><body>{body}</body></html>")


def write_board(run_dir: Path, live: bool = False) -> Path:
    out = run_dir / "board.html"
    out.write_text(board_html(run_dir, live=live), encoding="utf-8")
    return out
