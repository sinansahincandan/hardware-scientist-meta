"""Blind judging packets: for each benchmark problem, the Hardware Scientist design and the single-prompt design in
the same format (design.md with the same headings + one picture), labelled A and B by a fixed hash; the key is
written outside the packet folder.

Usage: .venv/bin/python scripts/bench_packets.py <packets_dir> <key_file> [salt=<text>] b1=<hs_run_dir> b2=<hs_run_dir> …
salt changes the fixed A/B labelling (round 1 put HS on B for b1–b3; round 2 uses salt=r2).
prev_b1=<run> adds an earlier Hardware Scientist run as a third design (labels A/B/C, mixed by the same hash);
open_b1=<run> [openfig_b1=<run>] adds Hardware Scientist on open weights (its picture from a redraw if given).
"""
from __future__ import annotations

import hashlib
import json
import os
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
    board = json.loads((sol_path.parent / "whiteboard.json").read_text(encoding="utf-8"))
    ev = {e["id"]: e for e in board.get("evidence", [])}

    def basis(k: dict) -> str:  # the calculation behind a number, as it stands on HS's whiteboard
        parts = []
        for eid in k.get("evidence_ids", [])[:2]:
            e = ev.get(eid)
            if e:
                code = " ".join(str(e.get("code_or_query", "")).split())[:220]
                parts.append(f"{e['purpose']}: {code} → {str(e.get('output_summary', ''))[:120]}")
        return "; ".join(parts) or k["method"]

    nums = [f"- {k['quantity']}: {k['value']:g} {k['unit']} ({basis(k)})" for k in sol.get("key_estimates", [])]
    steps = [f"- {s['action']}" for s in sol.get("operating_sequence", [])]
    risks = [f"- {r['risk']} — {r['mitigation']}" for r in sol.get("risks", [])]
    made = [f"- {f['description']} ({f['method']})" if f.get("method") else f"- {f['description']}"
            for f in sol.get("fabrication_steps", [])]
    table = [f"- {r['constraint']}: {r['design_value']} — {r['how_shown']}" for r in sol.get("constraint_table", [])]
    return (f"# {sol['title']}\n\n## How it works\n{sol.get('mechanism_sentence', '')} "
            f"{sol['concept'].get('working_principle', '')}\n" + ("\n".join(steps) + "\n" if steps else "")
            + "\n## Parts\n" + "\n".join(parts) + "\n\n## Key numbers\n" + "\n".join(nums)
            + "\n\n## Constraint check\n" + ("\n".join(table) if table else verdict.get("constraint_review", ""))
            + "\n\n## Risks\n" + "\n".join(risks)
            + ("\n\n## How it is made\n" + "\n".join(made) if made else "") + "\n")


def main() -> int:
    packets, key_file = Path(sys.argv[1]), Path(sys.argv[2])
    packets.mkdir(parents=True, exist_ok=True)
    key: dict[str, dict[str, str]] = {}
    args = sys.argv[3:]
    salt = next((a.split("=", 1)[1] for a in args if a.startswith("salt=")), "")
    prev = {a.split("=", 1)[0][5:]: Path(a.split("=", 1)[1]) for a in args if a.startswith("prev_")}
    # open_b1=<run>: Hardware Scientist on open weights (another folder); openfig_b1=<run>: its picture from a
    # Stage B redraw of the same meeting
    opn = {a.split("=", 1)[0][5:]: Path(a.split("=", 1)[1]) for a in args if a.startswith("open_")}
    ofig = {a.split("=", 1)[0][8:]: Path(a.split("=", 1)[1]) for a in args if a.startswith("openfig_")}
    for arg in [a for a in args if not a.startswith(("salt=", "prev_", "open_", "openfig_"))]:
        pid, run = arg.split("=", 1)
        run = Path(run)
        prob_file = next((ROOT / "examples" / "bench").glob(f"{pid}_*.json"))
        base = ROOT / "runs" / os.environ.get("BASELINE_OUT", "baseline") / prob_file.stem
        designs = {"hs": run, "baseline": base} | ({"hs_prev": prev[pid]} if pid in prev else {}) \
            | ({"hs_open": opn[pid]} if pid in opn else {})
        # labels by a fixed hash of problem + salt + design, so neither system always sits first
        ranked = sorted(designs, key=lambda who: hashlib.sha256((pid + salt + who).encode()).hexdigest()) \
            if len(designs) > 2 else (["hs", "baseline"] if int(hashlib.sha256((pid + salt).encode()).hexdigest(), 16) % 2 == 0
                          else ["baseline", "hs"])
        order = dict(zip("ABC", ranked, strict=False))
        key[pid] = {**order, "hs_run": run.name} | ({"hs_prev_run": prev[pid].name} if pid in prev else {}) \
            | ({"hs_open_run": str(opn[pid]), "hs_open_fig": str(ofig.get(pid, opn[pid]))} if pid in opn else {})
        d = packets / pid
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        shutil.copy(prob_file, d / "problem.json")
        for label, who in order.items():
            (d / label).mkdir()
            if who in ("hs", "hs_prev", "hs_open"):
                (d / label / "design.md").write_text(hs_markdown(designs[who]), encoding="utf-8")
                fig_run = ofig.get(pid, designs[who]) if who == "hs_open" else designs[who]
                full = fig_run / "final" / "figure.png"  # panels A-D: the device, its critical part, how it is made
                src = full if full.exists() else fig_run / "final" / "panel_A.png"
            else:
                shutil.copy(base / "design.md", d / label / "design.md")
                src = base / "figure.png"
            im = Image.open(src).convert("RGB")
            im.thumbnail((1800, 2400))
            im.save(d / label / "figure.jpg", quality=88)
    key_file.write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(f"{len(key)} packets in {packets}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
