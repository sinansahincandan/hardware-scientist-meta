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
    spec_file = attempt / "schematic_spec.json"
    if spec_file.exists():
        spec = SchematicSpec.model_validate_json(spec_file.read_text())
    else:  # runs made before specs were saved: part ids, names and sizes from the solution
        from hs.schemas import SolutionPrompt
        from hs.stage_b.schematic import build_spec_from_solution

        sol = next(run_dir.glob("stage_a/iter_*/solution.json"), None) or run_dir / "seeded_solution.json"
        spec = build_spec_from_solution(SolutionPrompt.model_validate_json(sol.read_text()))
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
