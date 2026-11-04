"""Give a Stage B redraw folder its problem's meeting, so the pages show the whole problem (no model call).

Usage: .venv/bin/python scripts/merge_redraw.py <redraw_run_dir>
Reads seeded_from.json; copies stage_a/, knowledge_in.json, archive.jsonl and REVIEW.md (if the redraw has none) from the source
run; writes merged_from.json; cost.json total becomes the sum of both runs (both values kept in the note); report.html and board.html are rebuilt.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    redraw = Path(sys.argv[1])
    seeded = json.loads((redraw / "seeded_from.json").read_text(encoding="utf-8"))
    source = ROOT / "runs" / seeded["source_run"]
    if not (redraw / "stage_a").exists():
        shutil.copytree(source / "stage_a", redraw / "stage_a")
    for name in ("knowledge_in.json", "archive.jsonl"):
        if (source / name).exists():
            shutil.copy(source / name, redraw / name)
    if not (redraw / "REVIEW.md").exists() and (source / "REVIEW.md").exists():
        shutil.copy(source / "REVIEW.md", redraw / "REVIEW.md")
    a = float(json.loads((source / "cost.json").read_text(encoding="utf-8")).get("total_usd", 0.0))
    cost = json.loads((redraw / "cost.json").read_text(encoding="utf-8"))
    b = float(cost.get("total_usd", 0.0))
    if (redraw / "merged_from.json").exists():  # already merged: cost.json holds the sum, keep the first note
        b = round(b - a, 4)
    else:
        cost["total_usd"] = round(a + b, 4)
        (redraw / "cost.json").write_text(json.dumps(cost, indent=2), encoding="utf-8")
    (redraw / "merged_from.json").write_text(json.dumps({
        "note": f"stage_a/ and knowledge_in.json copied from run {source.name} (the Stage A this redraw was seeded "
                f"from) so the pages show the whole problem; cost.json total is the sum of both runs "
                f"(${a:.4f} + ${b:.4f})."}, indent=2), encoding="utf-8")
    # the pages were written before the meeting was copied in; rebuild them so they show it
    sys.path.insert(0, str(ROOT / "src"))
    from hs.board import write_board
    from hs.report import write_report
    write_report(redraw)
    write_board(redraw)
    print(f"{redraw.name}: merged from {source.name}, total ${a + b:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
