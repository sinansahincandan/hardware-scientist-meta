"""Redraw a finished run's figure panels with the current code (no model call): panel A labels from the saved
localization and the numbered working steps, panel B, panel C; then recompose figure.png.

Usage: .venv/bin/python scripts/refigure.py <run_dir> [more run dirs…]
Panel A keeps the image model's callouts when the final callout check passed (no _render_without_callouts.png).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.schemas import Localization, SchematicSpec, SolutionPrompt
from hs.stage_b.annotate import Annotator
from hs.stage_b.figure import _panel_b, _panel_c, draw_sequence, recompose


def main() -> int:
    for arg in sys.argv[1:]:
        run = Path(arg)
        sol_path = max(run.glob("stage_a/iter_*/solution.json"))
        solution = SolutionPrompt.model_validate_json(sol_path.read_text(encoding="utf-8"))
        spec = SchematicSpec.model_validate_json(max(run.glob("stage_b/attempt_*/schematic_spec.json"))
                                                 .read_text(encoding="utf-8"))
        loc = Localization.model_validate_json((run / "final" / "localization.json").read_text(encoding="utf-8"))
        clean = run / "final" / "_render_without_callouts.png"
        render = clean if clean.exists() else max(run.glob("stage_b/attempt_*/round_*/render.png"))
        panel_a = run / "final" / "panel_A.png"
        Annotator(None).run(render, spec, {}, panel_a, localization=loc, fallback=False, draw_labels=clean.exists())
        notes: list[str] = []
        passed = [json.loads(x) for x in (run / "image_archive.jsonl").read_text(encoding="utf-8").splitlines()
                  if x.strip() and json.loads(x).get("decision") == "s1_pass"]
        masks = Path(passed[-1]["render"]).parent / "sam_masks" if passed else None  # the masks of the shipped render
        # final/localization.json keeps only the labelled parts; the markers use every part the round located
        located = masks.parent / "localization.json" if masks else None
        marks = (Localization.model_validate_json(located.read_text(encoding="utf-8"))
                 if located and located.exists() else loc)
        draw_sequence(panel_a, solution, marks, notes, masks_dir=masks)
        _panel_b(render, spec, loc, run / "final" / "panel_B.png", notes)
        _panel_c(solution, run / "final" / "panel_C.png")
        print(run.name, recompose(run).name, "; ".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
