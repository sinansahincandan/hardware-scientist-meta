"""Run only the picture critic (designer evaluation, S1/S2) on a stored render, with the same inputs the Stage B loop
gives it: the render, the concept sketch, the accepted solution, the parts the localizer missed and the segmenter's
measurements. One or two Meta calls (about $0.05 each); for checking a critic prompt change before a full run.

Usage: .venv/bin/python scripts/recritique.py <run_dir> <out_dir> [attempt] [round]
Writes <out_dir>/eval.json, decision.txt and unaddressed.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.client import MetaClient
from hs.schemas import PartMap, SchematicSpec, SolutionPrompt
from hs.stage_b import part_map as pm
from hs.stage_b.designer_eval import DesignerEvalRunner, decide
from hs.stage_b.loop import _unaddressed, council_sketches


def main() -> int:
    run, out = Path(sys.argv[1]), Path(sys.argv[2])
    attempt = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rnd = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    out.mkdir(parents=True, exist_ok=True)
    adir = run / "stage_b" / f"attempt_{attempt:02d}"
    rdir = adir / f"round_{rnd:02d}"
    sol_files = sorted(run.glob("stage_a/iter_*/solution.json"))
    sol_path = run / "seeded_solution.json" if (run / "seeded_solution.json").exists() else sol_files[-1]
    solution = SolutionPrompt.model_validate_json(sol_path.read_text(encoding="utf-8"))
    spec = SchematicSpec.model_validate_json((adir / "schematic_spec.json").read_text(encoding="utf-8"))
    pmap = PartMap.model_validate_json((adir / "part_map.json").read_text(encoding="utf-8"))
    sam = json.loads((rdir / "sam.json").read_text(encoding="utf-8"))
    diffs = sam.get("differences", {})
    sam_text = "\n".join(t for t in (pm.evidence_text(diffs, sam.get("rechecks", []), pmap),
                                     pm.extent_text(sam, spec)) if t)
    loc = json.loads((rdir / "localization.json").read_text(encoding="utf-8"))
    missing = [p["id"] for p in loc.get("parts", []) if not p.get("found")]
    sketch = adir / "concept_sketch.png" if (adir / "concept_sketch.png").exists() else rdir / "schematic_labeled.png"
    seeded = json.loads((run / "seeded_from.json").read_text(encoding="utf-8")) if (run / "seeded_from.json").exists() else {}
    src_run = ROOT / "runs" / seeded["source_run"] if seeded.get("source_run") else run
    iters = sorted(src_run.glob("stage_a/iter_*"))
    sketches = council_sketches(iters[-1]) if iters else []
    critical = next((f"{n.label} ({n.id})" for n in spec.nodes if n.id == spec.critical_part_id), "")
    client = MetaClient(run_dir=out, max_cost=0.4)
    runner = DesignerEvalRunner(client)
    ev = runner.run(rdir / "render.png", sketch, solution, missing, measurements=sam_text,
                    critical_part=critical, council_sketches=sketches)
    missed = _unaddressed(diffs, ev)
    if missed:  # the loop's own re-ask (loop.py)
        ev = runner.run(rdir / "render.png", sketch, solution, missing,
                        measurements=sam_text + "\nYOUR PREVIOUS ANSWER DID NOT ADDRESS THESE FINDINGS: "
                        + ", ".join(missed) + ". Answer again in full: for each of them either a region to fix, or a "
                        "deviation whose why says what the pixels show and why the measurement or the expectation is "
                        "wrong or does not change how the device works.",
                        critical_part=critical, council_sketches=sketches)
    (out / "eval.json").write_text(ev.model_dump_json(indent=2), encoding="utf-8")
    (out / "decision.txt").write_text(decide(ev, 0) + "\n", encoding="utf-8")
    (out / "unaddressed.json").write_text(json.dumps({"first_ask": missed, "after": _unaddressed(diffs, ev)}),
                                          encoding="utf-8")
    print(run.name, "decision:", decide(ev, 0), "| S1", ev.s1_faithful, "S2", ev.s2_flaw,
          "| regions:", [(r.part_id, r.source) for r in ev.regions])
    return 0


if __name__ == "__main__":
    sys.exit(main())
