"""Re-measure one finished picture with the current SAM step (real calls) into a separate folder.

Usage: .venv/bin/python scripts/sam_remeasure.py <round_dir> <out_dir>
Reads render.png, part_map.json and the attempt's schematic_spec.json; writes sam.json, sam_masks/, mask_check/
and sam_overlay.png into <out_dir>. Prints found / not found / rejected per part.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.client import MetaClient
from hs.schemas import PartMap, SchematicSpec
from hs.stage_b import part_map as pm


def main() -> int:
    rd, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    spec = SchematicSpec.model_validate_json((rd.parent / "schematic_spec.json").read_text(encoding="utf-8"))
    pmap = PartMap.model_validate_json((rd.parent / "part_map.json").read_text(encoding="utf-8"))
    client = MetaClient(run_dir=out, max_cost=0.5)
    meas = pm.measure(client, rd / "render.png", pmap, out_dir=out, spec=spec)
    (out / "sam.json").write_text(json.dumps(meas, indent=2, default=list), encoding="utf-8")
    pm.draw_overlay(rd / "render.png", out / "sam.json", out / "sam_overlay.png")
    for pid, rec in meas["parts"].items():
        print(f"{pid}: {len(rec['boxes'])} found via {rec['source']} ('{rec['phrase']}', tried {rec['tried']})"
              + (f"; judge rejected: {rec['rejected_by_judge']}" if rec.get("rejected_by_judge") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
