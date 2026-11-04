"""Blind judging packets, three designs per problem: the single Meta prompt (baseline), Hardware Scientist on the
Meta Model API, and Hardware Scientist on open weights. Each design is a design.md with the same headings (written by
bench_packets.hs_markdown for both HS designs) plus panel A as figure.jpg; labels A/B/C come from a fixed hash; the
key is written outside the packet folder.

Usage: .venv/bin/python scripts/bench_packets3.py <packets_dir> <key_file> <baseline_dir> \
           b1=<hs_api_run>,<hs_open_run> b2=… b3=…
"""
from __future__ import annotations

import hashlib
import itertools
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench_packets import ROOT, hs_markdown  # noqa: E402


def main() -> int:
    packets, key_file, baseline = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    packets.mkdir(parents=True, exist_ok=True)
    key: dict[str, dict[str, str]] = {}
    perms = list(itertools.permutations(["baseline", "hs_api", "hs_open"]))
    for arg in sys.argv[4:]:
        pid, runs = arg.split("=", 1)
        api_run, open_run = (Path(r) for r in runs.split(","))
        prob_file = next((ROOT / "examples" / "bench").glob(f"{pid}_*.json"))
        order = dict(zip("ABC", perms[int(hashlib.sha256(f"r3open-{pid}".encode()).hexdigest(), 16) % 6]))
        key[pid] = {**order, "hs_api_run": api_run.name, "hs_open_run": open_run.name}
        d = packets / pid
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        shutil.copy(prob_file, d / "problem.json")
        for label, who in order.items():
            (d / label).mkdir()
            if who == "baseline":
                shutil.copy(baseline / prob_file.stem / "design.md", d / label / "design.md")
                src = baseline / prob_file.stem / "figure.png"
            else:
                run = api_run if who == "hs_api" else open_run
                (d / label / "design.md").write_text(hs_markdown(run), encoding="utf-8")
                src = run / "final" / "panel_A.png"
            im = Image.open(src).convert("RGB")
            im.thumbnail((1600, 1600))
            im.save(d / label / "figure.jpg", quality=88)
    key_file.write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(f"{len(key)} packets in {packets}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
