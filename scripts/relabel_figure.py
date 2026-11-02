"""Re-check panel A's labels of a finished run (16a) and recompose the figure; no new images.

Usage: .venv/bin/python scripts/relabel_figure.py runs/<id>
Uses the passing round recorded in image_archive.jsonl and the saved schematic_spec.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.client import MetaClient
from hs.schemas import Localization, SchematicSpec
from hs.stage_b.figure import recompose, relabel_panel_a


def main() -> int:
    run_dir = Path(sys.argv[1])
    entry = next(e for e in reversed([json.loads(x) for x in (run_dir / "image_archive.jsonl").read_text().splitlines()
                                      if x.strip()]) if e["decision"] == "s1_pass")
    render = Path(entry["render"])
    attempt = render.parent.parent
    spec = SchematicSpec.model_validate_json((attempt / "schematic_spec.json").read_text())
    loc = Localization.model_validate_json((render.parent / "localization.json").read_text())
    notes: list[str] = []
    relabel_panel_a(MetaClient(run_dir=run_dir), spec, render, loc, run_dir / "final" / "panel_A.png", notes)
    recompose(run_dir)
    with (run_dir / "final" / "rationale.md").open("a", encoding="utf-8") as fh:
        fh.write("".join(f"- {n}\n" for n in notes))
    print("\n".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
