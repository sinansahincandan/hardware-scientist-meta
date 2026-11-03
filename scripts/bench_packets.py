"""Blind judging packets: for each benchmark problem, the Hardware Scientist design and the single-prompt design in
the same format (design.md with the same headings + one picture), labelled A and B by a fixed hash; the key is
written outside the packet folder.

Usage: .venv/bin/python scripts/bench_packets.py <packets_dir> <key_file> b1=<hs_run_dir> b2=<hs_run_dir> …
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def hs_markdown(run: Path) -> str:
    sol_path = max(run.glob("stage_a/iter_*/solution.json"))
    sol = json.loads(sol_path.read_text(encoding="utf-8"))
    verdict = json.loads((sol_path.parent / "verdict.json").read_text(encoding="utf-8"))
    parts = [f"- {p['name']} — {p['function']}" for p in sol["concept"]["parts"]]
    nums = [f"- {k['quantity']}: {k['value']:g} {k['unit']} ({k['method']})" for k in sol.get("key_estimates", [])]
    steps = [f"- {s['action']}" for s in sol.get("operating_sequence", [])]
    risks = [f"- {r['risk']} — {r['mitigation']}" for r in sol.get("risks", [])]
    return (f"# {sol['title']}\n\n## How it works\n{sol.get('mechanism_sentence', '')} "
            f"{sol['concept'].get('working_principle', '')}\n" + ("\n".join(steps) + "\n" if steps else "")
            + "\n## Parts\n" + "\n".join(parts) + "\n\n## Key numbers\n" + "\n".join(nums)
            + "\n\n## Constraint check\n" + verdict.get("constraint_review", "") + "\n\n## Risks\n" + "\n".join(risks)
            + "\n")


def main() -> int:
    packets, key_file = Path(sys.argv[1]), Path(sys.argv[2])
    packets.mkdir(parents=True, exist_ok=True)
    key: dict[str, dict[str, str]] = {}
    for arg in sys.argv[3:]:
        pid, run = arg.split("=", 1)
        run = Path(run)
        prob_file = next((ROOT / "examples" / "bench").glob(f"{pid}_*.json"))
        base = ROOT / "runs" / "baseline" / prob_file.stem
        hs_first = int(hashlib.sha256(pid.encode()).hexdigest(), 16) % 2 == 0
        order = {"A": "hs", "B": "baseline"} if hs_first else {"A": "baseline", "B": "hs"}
        key[pid] = {**order, "hs_run": run.name}
        d = packets / pid
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        shutil.copy(prob_file, d / "problem.json")
        for label, who in order.items():
            (d / label).mkdir()
            if who == "hs":
                (d / label / "design.md").write_text(hs_markdown(run), encoding="utf-8")
                src = run / "final" / "panel_A.png"
            else:
                shutil.copy(base / "design.md", d / label / "design.md")
                src = base / "figure.png"
            im = Image.open(src).convert("RGB")
            im.thumbnail((1600, 1600))
            im.save(d / label / "figure.jpg", quality=88)
    key_file.write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(f"{len(key)} packets in {packets}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
