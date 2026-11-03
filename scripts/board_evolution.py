"""The whiteboard of one meeting, replayed cycle by cycle from whiteboard_history.jsonl (no model call).

Usage: .venv/bin/python scripts/board_evolution.py <iter_dir> <out_dir>
Writes board_c<cycle>.png (the board picture as it stood at the end of each cycle) and evolution.json (counts per
cycle: concepts, evidence by kind, objections open/resolved, proposal version, ready votes).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from playwright.sync_api import sync_playwright
from shoot import _cached_chromium

from hs.board_picture import PICTURE_STYLE, board_picture_html
from hs.stage_a.whiteboard import Whiteboard


def main() -> int:
    it, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    final = json.loads((it / "whiteboard.json").read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in final["evidence"]}
    records = [json.loads(line) for line in (it / "whiteboard_history.jsonl").read_text(encoding="utf-8").splitlines()
               if line.strip()]
    run_dir = it.parents[1]
    title = json.loads((run_dir / "problem.json").read_text(encoding="utf-8"))["title"]
    members = list(dict.fromkeys(r["member"] for r in records if r.get("member") and r["member"] != "Manager"))
    board = Whiteboard()
    snapshots: dict[int, dict] = {}
    for r in records:
        if r.get("kind") == "op" and r.get("ok"):
            board.apply_op(r["member"], r.get("op") or {})
        elif r.get("kind") == "evidence" and r.get("evidence_id") in by_id:
            e = dict(by_id[r["evidence_id"]])
            board.evidence.append(type(board.evidence[0])(**e) if board.evidence else
                                  Whiteboard.model_validate({"evidence": [e]}).evidence[0])
        snapshots[int(r.get("cycle", 0))] = json.loads(json.dumps(board.model_dump()))
    rows = []
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception:
            browser = pw.chromium.launch(executable_path=_cached_chromium())
        page = browser.new_page(viewport={"width": 1300, "height": 900}, device_scale_factor=1.5)
        for cyc in sorted(c for c in snapshots if c > 0):
            snap = snapshots[cyc]
            html = (f"<html><head><meta charset='utf-8'><base href='{run_dir.resolve().as_uri()}/'>{PICTURE_STYLE}</head><body style='margin:0;background:#e9edf2;"
                    f"padding:10px'>{board_picture_html(snap, run_dir, it, members, title, cyc, 4)}</body></html>")
            tmp = out / "_b.html"
            tmp.write_text(html, encoding="utf-8")
            page.goto(tmp.as_uri())
            page.wait_for_timeout(400)
            page.locator(".wb").screenshot(path=str(out / f"board_c{cyc}.png"))
            ev = snap["evidence"]
            rows.append({"cycle": cyc, "concepts": len(snap["concepts"]),
                         "searches": sum(e["tool"] == "web_search" for e in ev),
                         "calculations": sum(e["tool"].split(":")[0] in ("calc", "vetted_calc", "simulate") for e in ev),
                         "sketches": sum(e["tool"] == "sketch" for e in ev),
                         "objections_open": sum(o["status"] != "resolved" for o in snap["objections"]),
                         "objections_resolved": sum(o["status"] == "resolved" for o in snap["objections"]),
                         "proposal_version": (snap.get("proposal") or {}).get("version"),
                         "ready": sum(1 for v in snap.get("votes", {}).values() if v.get("ready"))})
        browser.close()
    (out / "_b.html").unlink(missing_ok=True)
    (out / "evolution.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
