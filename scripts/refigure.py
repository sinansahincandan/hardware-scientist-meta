"""Redraw a finished run's figure panels with the current code (no model call): panel A labels from the saved
localization and the numbered working steps, panel B, panel C; then recompose figure.png.

Usage: .venv/bin/python scripts/refigure.py <run_dir> [more run dirs…]
Panel A keeps the image model's callouts when the final callout check passed (no _render_without_callouts.png).
"""
from __future__ import annotations

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
        draw_sequence(panel_a, solution, loc, notes)
        _panel_b(render, spec, loc, run / "final" / "panel_B.png", notes)
        _panel_c(solution, run / "final" / "panel_C.png")
        print(run.name, recompose(run).name, "; ".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
