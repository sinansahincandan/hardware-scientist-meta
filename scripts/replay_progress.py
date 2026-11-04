"""Re-judge a round's saved local edits with the current progress check (one model call per edit).

Usage: .venv/bin/python scripts/replay_progress.py <round_dir> <out_dir>
Writes <out_dir>/progress_<part>.json beside the original verdict, for comparison.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.open_client import OpenClient
from hs.schemas import DesignerEval, VLMPromptGradient
from hs.stage_b.prompt_gradient import VLMPromptGradientRunner


def main() -> int:
    rd, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    ev = DesignerEval.model_validate_json((rd / "eval.json").read_text(encoding="utf-8"))
    grad = VLMPromptGradient.model_validate_json((rd / "vlm_gradient.json").read_text(encoding="utf-8"))
    runner = VLMPromptGradientRunner(OpenClient(run_dir=out, max_cost=0.5))
    for local in sorted(rd.glob("local_*.png")):
        part = local.stem[len("local_"):]
        fix = next((g.prompt_fix for g in grad.per_region if g.part_id == part), "")
        check = runner.progress_check(local, ev, fix, part_id=part, before_png=rd / "render.png")
        (out / f"progress_{part}.json").write_text(check.model_dump_json(indent=2), encoding="utf-8")
        old = json.loads((rd / f"progress_{part}.json").read_text(encoding="utf-8"))
        print(f"{part}: before fixed={old['fixed_region_pass']} -> now fixed={check.fixed_region_pass} "
              f"previous={check.previous_pass} seam={check.seam_visible} | {check.notes[:240]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
