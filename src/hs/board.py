"""hs board: whiteboard replay HTML (spec §8, AUTOPILOT §4 board bar).

Dark page, white board, sticky notes in member colours, boxed evidence
with ids, red objection cards, proposal frame, subtitle bar and a
working step-by-step replay (the slider re-renders the board per step).
Static final-board cards remain as the no-JS fallback.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hs.stage_a.whiteboard import Whiteboard

COLORS = ["#ffe082", "#a5d6a7", "#90caf9", "#f48fb1", "#ce93d8", "#ffcc80"]
MEMBER_COLORS = ["#1e6fb8", "#2e8b3a", "#7d3c98", "#d35400", "#0e7a7b", "#b03a5b"]

STYLE = """<style>
body{background:#23272e;font-family:'Segoe UI',Helvetica,Arial,sans-serif;margin:0;color:#222}
.board{background:#f7f5ef;border-radius:14px;margin:18px;padding:22px 26px;box-shadow:0 8px 30px rgba(0,0,0,.5)}
.board h1{font-family:'Segoe Print','Comic Sans MS',cursive;font-size:30px;margin:2px 0 4px;letter-spacing:.5px}
.sub{color:#555;font-style:italic;margin-bottom:8px}
.legend span{display:inline-block;padding:3px 10px;border-radius:10px;margin:2px;color:#fff;font-size:13px}
.proposal{border:3px double #222;border-radius:6px;padding:10px 14px;background:#fff;max-width:520px;float:right;margin:0 0 10px 14px}
.proposal b{font-family:'Segoe Print','Comic Sans MS',cursive}
.cols{display:flex;gap:18px;clear:both;flex-wrap:wrap}
.col{flex:1;min-width:260px;border-left:2px dashed #bbb;padding-left:14px}
.col h3{font-family:'Segoe Print','Comic Sans MS',cursive;font-size:17px;border-bottom:3px solid #222;padding-bottom:3px}
.sticky{display:inline-block;padding:9px 11px;margin:5px;border:1px solid rgba(0,0,0,.25);max-width:230px;vertical-align:top;
 box-shadow:2px 3px 6px rgba(0,0,0,.25);font-size:14px;transform:rotate(-.6deg)}
.sticky b{display:block;font-size:12px;color:#333}
.dropped{opacity:.4;text-decoration:line-through}.favored{outline:3px solid #f5b301}
.evidence{border:2px solid #2e7d32;border-radius:4px;padding:6px 9px;margin:6px 0;background:#fff;font-size:14px}
.evidence b{color:#1b5e20}
.objection{border:3px solid #c0392b;border-radius:40px;padding:8px 14px;margin:8px 0;color:#922b21;background:#fff;font-size:14px}
.objection.resolved{opacity:.55}.objection.resolved span{text-decoration:line-through}
.dot{display:inline-block;border-radius:50%;border:1px solid #333;padding:2px 7px;margin:2px;background:#eee}
.ready{background:#a5d6a7}.msg{border-left:3px solid #90caf9;padding:4px 8px;margin:4px;background:#fff;font-size:14px}
.subtitle{position:sticky;bottom:0;background:#2b3038;color:#eee;padding:12px 18px;display:flex;gap:14px;align-items:center}
.subtitle .who{color:#ce93d8;font-weight:600}
.timeline{background:#2b3038;color:#eee;padding:8px 18px}
.timeline input[type=range]{width:46%}
section.static{background:#f7f5ef;border-radius:14px;margin:18px;padding:16px 22px}
</style>"""


def _snapshots(iter_dir: Path) -> tuple[list[dict[str, Any]], Whiteboard | None, list[dict[str, Any]]]:
    board_path = iter_dir / "whiteboard.json"
    final = Whiteboard.load(board_path) if board_path.exists() else None
    history_path = iter_dir / "whiteboard_history.jsonl"
    records: list[dict[str, Any]] = []
    if history_path.exists():
        records = [json.loads(l) for l in history_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    transcript: list[dict[str, Any]] = []
    for turn_file in sorted((iter_dir / "turns").glob("*.json")) if (iter_dir / "turns").exists() else []:
        transcript.append(json.loads(turn_file.read_text(encoding="utf-8")))
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
        msg = next((t.get("message", "") for t in transcript
                    if t.get("member") == rec.get("member") and t.get("cycle") == rec.get("cycle")), "")
        snapshots.append({
            "label": f"cycle {rec.get('cycle', '?')} · {rec.get('member', '')} · {rec.get('kind', '')}",
            "member": str(rec.get("member", "")), "message": msg,
            "functions": [f.model_dump() for f in board.functions],
            "concepts": [c.model_dump() for c in board.concepts],
            "objections": [o.model_dump() for o in board.objections],
            "proposal": board.proposal.model_dump() if board.proposal else None,
            "votes": {k: v.model_dump() for k, v in board.votes.items()},
            "evidence": [e.model_dump() for e in (final.evidence[:ev_count] if final else [])],
        })
    if not snapshots and final is not None:
        snapshots.append({
            "label": "final", "member": "", "message": "",
            "functions": [f.model_dump() for f in final.functions],
            "concepts": [c.model_dump() for c in final.concepts],
            "objections": [o.model_dump() for o in final.objections],
            "proposal": final.proposal.model_dump() if final.proposal else None,
            "votes": {k: v.model_dump() for k, v in final.votes.items()},
            "evidence": [e.model_dump() for e in final.evidence],
        })
    return snapshots, final, transcript


def board_html(run_dir: Path, *, fragment: bool = False, live: bool = False) -> str:
    iter_dirs = sorted((run_dir / "stage_a").glob("iter_*")) if (run_dir / "stage_a").exists() else []
    sections: list[str] = []
    all_snapshots: list[dict[str, Any]] = []
    legend_members: list[str] = []
    title = run_dir.name
    try:
        title = json.loads((run_dir / "problem.json").read_text(encoding="utf-8")).get("title", title)
    except Exception:
        pass
    for iter_dir in iter_dirs:
        snapshots, final, transcript = _snapshots(iter_dir)
        all_snapshots.extend(snapshots)
        if final is not None:
            for c in final.concepts:
                if c.author not in legend_members:
                    legend_members.append(c.author)
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
                cards.append(f"<div class='{cls}'><b>{o.id}</b> [{o.author} → {o.target_id}] "
                             f"<span>{o.text}</span> resolution: {o.resolution} evidence={o.evidence_ids}</div>")
            for t in transcript:
                cards.append(f"<div class='msg'><b>Cycle {t.get('cycle')} — {t.get('member')}</b>: {t.get('message', '')}</div>")
        sections.append(f"<section class='static'><h2>{iter_dir.name} (final board)</h2>{''.join(cards)}</section>")
    legend = " ".join(
        f"<span style='background:{MEMBER_COLORS[i % len(MEMBER_COLORS)]}'>{m}</span>"
        for i, m in enumerate(legend_members))
    member_color_js = json.dumps({m: MEMBER_COLORS[i % len(MEMBER_COLORS)] for i, m in enumerate(legend_members)})
    sticky_color_js = json.dumps({m: COLORS[i % len(COLORS)] for i, m in enumerate(legend_members)})
    slider = (
        f"<div class='timeline'><label>Replay: <input type='range' id='step' min='0' "
        f"max='{max(len(all_snapshots) - 1, 0)}' value='{max(len(all_snapshots) - 1, 0)}'></label>"
        f"<button onclick='play()'>Play/Pause</button> <span id='stepLabel'></span></div>"
        f"<div class='subtitle'><span class='who' id='subWho'></span><span id='subMsg'></span></div>"
        f"<script>const snaps={json.dumps(all_snapshots)};const MC={member_color_js};const SC={sticky_color_js};"
        "function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');}"
        "function show(i){const s=snaps[i];if(!s)return;document.getElementById('stepLabel').textContent="
        "'step '+(i+1)+' / '+snaps.length+' · '+s.label;"
        "document.getElementById('subWho').textContent=s.member||'';"
        "document.getElementById('subMsg').textContent=s.message||s.label;"
        "let h='';if(s.proposal){h+=\"<div class='proposal'><b>PROPOSAL v\"+s.proposal.version+'</b> ['+esc(s.proposal.author)+'] '+esc(s.proposal.text)+'</div>';}"
        "h+=\"<div class='cols'>\";for(const f of s.functions){h+=\"<div class='col'><h3>\"+f.id+' · '+esc(f.text)+'</h3>';"
        "for(const c of s.concepts.filter(x=>x.function_id===f.id)){const cls='sticky'+(c.status==='dropped'?' dropped':c.status==='favored'?' favored':'');"
        "h+=\"<div class='\"+cls+\"' style='background:\"+(SC[c.author]||'#eee')+\"'><b>\"+c.id+' — '+esc(c.author)+'</b>'+esc(c.text)+'</div>';}"
        "for(const e of s.evidence){h+=\"<div class='evidence'><b>\"+e.id+' · '+esc(e.output_summary)+'</b> ['+esc(e.tool)+', '+esc(e.author)+']</div>';}"
        "for(const o of s.objections){h+=\"<div class='objection\"+(o.status==='resolved'?' resolved':'')+\"'><b>\"+o.id+'</b> ['+esc(o.author)+' → '+esc(o.target_id)+'] <span>'+esc(o.text)+'</span></div>';}"
        "h+='</div>';}h+='</div>';"
        "h+=\"<div>Votes: \"+Object.entries(s.votes).map(([m,v])=>\"<span class='dot \"+(v.ready?'ready':'')+\"' title='\"+esc(v.reason)+\"'>\"+esc(m[0])+'</span>').join(' ')+'</div>';"
        "document.getElementById('liveBoard').innerHTML=h;}"
        "document.getElementById('step').addEventListener('input',e=>show(+e.target.value));"
        "let timer=null;function play(){if(timer){clearInterval(timer);timer=null;return;}"
        "let st=document.getElementById('step');timer=setInterval(()=>{st.value=(+st.value+1)%(snaps.length||1);show(+st.value);},1100);}"
        "show(snaps.length-1);</script>"
    )
    body = (f"<div class='board'><h1>{title}</h1><div class='sub'>Council whiteboard — concepts, evidence and objections as they happened</div>"
            f"<div class='legend'>{legend}</div><div id='liveBoard'></div></div>"
            f"{slider}{''.join(sections)}")
    if fragment:
        return STYLE + body
    refresh = '<meta http-equiv="refresh" content="5">' if live else ""
    return (f"<!doctype html><html><head><meta charset='utf-8'>{refresh}<title>Board {run_dir.name}</title>"
            f"{STYLE}</head><body>{body}</body></html>")


def write_board(run_dir: Path, live: bool = False) -> Path:
    out = run_dir / "board.html"
    out.write_text(board_html(run_dir, live=live), encoding="utf-8")
    return out
