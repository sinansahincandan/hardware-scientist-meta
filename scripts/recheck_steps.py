"""Re-check the fabrication-step images a finished run already made (plain-word check, general check
only when the content filter blocks it) and rebuild panel D and the figure; no new images.

Usage: .venv/bin/python scripts/recheck_steps.py runs/<id>
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.client import MetaClient
from hs.schemas import SolutionPrompt
from hs.stage_b.annotate import _font
from hs.stage_b.figure import _step_check, recompose


def main() -> int:
    run_dir = Path(sys.argv[1])
    final = run_dir / "final"
    solution = SolutionPrompt.model_validate_json(next(run_dir.glob("stage_a/iter_*/solution.json")).read_text())
    client = MetaClient(run_dir=run_dir)
    names = {p.id: p.name for p in solution.concept.parts}
    shipped: list[tuple[Path, str]] = []
    notes: list[str] = []
    for step in sorted(solution.fabrication_steps, key=lambda s: s.step):
        image = final / f"_step{step.step}.png"
        if not image.exists():
            continue
        try:
            check, general = _step_check(client, solution, step.step, step.description,
                                         ", ".join(names.get(p, p) for p in step.parts_present), image)
        except Exception as exc:
            if "content management policy" not in str(exc):
                raise
            notes.append(f"fabrication step {step.step}: both checks blocked by the content filter; not shown")
            continue
        caption = f"{step.step}. {step.description}" + (" (general check only)" if general else "")
        notes.append(f"fabrication step {step.step} re-checked: {'shown' if check.ok else 'not shown'}"
                     f"{' (general check only; detailed check blocked by the content filter)' if general else ''}"
                     f" — {check.reason}")
        if check.ok:
            shipped.append((image, caption))
    if shipped:
        captions = [textwrap.wrap(c, width=30) for _, c in shipped]
        tw, th = 520, 325
        strip = Image.new("RGB", (tw * len(shipped), th + 10 + 21 * max(len(c) for c in captions)), "white")
        draw = ImageDraw.Draw(strip)
        for i, ((img, _), lines) in enumerate(zip(shipped, captions, strict=True)):
            strip.paste(Image.open(img).convert("RGB").resize((tw, th)), (tw * i, 0))
            for j, line in enumerate(lines):
                draw.text((tw * i + 6, th + 5 + j * 21), line, fill=(0, 0, 0), font=_font(17))
        strip.save(final / "panel_D.png")
    recompose(run_dir)
    with (final / "rationale.md").open("a", encoding="utf-8") as fh:
        fh.write("\n## Fabrication steps re-checked (plain-word check)\n" + "".join(f"- {n}\n" for n in notes))
    print("\n".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
