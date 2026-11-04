"""Item 16 smoke test: settle the sam-3.1 call shape on a known image. One attempt per call.
Writes runs/sam_probe_<stamp>/probe.json. Usage: .venv/bin/python scripts/sam_probe.py <image.png> <phrase>..."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.open_client import OpenClient as MetaClient  # open-weights copy


def main() -> int:
    image, phrases = Path(sys.argv[1]), sys.argv[2:]
    run_dir = ROOT / "runs" / f"sam_probe_{time.strftime('%Y%m%d-%H%M%S')}"
    run_dir.mkdir(parents=True)
    client = MetaClient(run_dir=run_dir)
    out = []
    for phrase in phrases:
        meta = {"mask_encoding": "one_bit"} if phrase.startswith("1bit:") else None
        text = phrase.removeprefix("1bit:")
        try:
            raw = client.sam_segment(text, image, metadata=meta)
            out.append({"phrase": text, "metadata": meta, "raw": raw, **client.last_sam})
        except Exception as exc:
            out.append({"phrase": text, "metadata": meta, "error": f"{type(exc).__name__}: {exc}"[:1500]})
        print(text, "->", out[-1].get("chars", out[-1].get("error")), flush=True)
    (run_dir / "probe.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(run_dir / "probe.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
