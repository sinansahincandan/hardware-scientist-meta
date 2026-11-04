"""Engineering depth of each design, counted from the run files (no model call): what the council did (sources found
and opened, calculations, simulations, sketches, concepts compared, objections, meetings, prompt revisions, skills
used) and what the design hands an engineer (parts with function and material, numbers tied to evidence, constraint
rows, risks, fabrication stages, operating steps, measurement chain). The single prompt's design.md is counted the
same way where it has the item.

Usage: .venv/bin/python scripts/depth_table.py <out.json> name=<run_dir or baseline dir> ...
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def hs_depth(run: Path) -> dict:
    iters = sorted((run / "stage_a").glob("iter_*"))
    ev_by_tool: dict[str, int] = {}
    read = cited = concepts = objections = resolved = 0
    for it in iters:
        b = json.loads((it / "whiteboard.json").read_text(encoding="utf-8"))
        ids = set()
        for e in b.get("evidence", []):
            if e["id"] in ids:
                continue
            ids.add(e["id"])
            ev_by_tool[e["tool"]] = ev_by_tool.get(e["tool"], 0) + 1
            ref = (e.get("references") or [{}])[0]
            read += bool(ref.get("read"))
            cited += bool(ref.get("cited"))
        concepts = max(concepts, len(b.get("concepts", [])))
        objections = max(objections, len(b.get("objections", [])))
        resolved = max(resolved, sum(1 for o in b.get("objections", []) if o.get("status") != "open"))
    sol = json.loads(max((run / "stage_a").glob("iter_*/solution.json")).read_text(encoding="utf-8"))
    c = sol["concept"]
    return {
        "meetings": len(iters),
        "prompt_revisions": max(0, len(list((run / "master_prompt").glob("rev_*.md"))) - 1),
        "sources_found": ev_by_tool.get("web_search", 0),
        "sources_opened": read,
        "calculations": ev_by_tool.get("calc", 0) + ev_by_tool.get("vetted_calc", 0),
        "simulations": ev_by_tool.get("simulate", 0),
        "sketches": ev_by_tool.get("sketch", 0),
        "skills_used": ev_by_tool.get("use_skill", 0),
        "concepts_compared": concepts,
        "objections_raised": objections,
        "parts": len(c.get("parts", [])),
        "numbers_with_basis": len(sol.get("key_estimates", [])),
        "constraint_rows": len(sol.get("constraint_table", [])),
        "risks": len(sol.get("risks", [])),
        "fabrication_stages": len(sol.get("fabrication_steps", [])),
        "operating_steps": len(sol.get("operating_sequence", [])),
        "measurement_chain": len(sol.get("measurement_chain", [])),
        "connections": len(c.get("connections", [])),
    }


def baseline_depth(d: Path) -> dict:
    md = (d / "design.md").read_text(encoding="utf-8")

    def section(name: str) -> list[str]:
        m = re.search(rf"## {name}\n(.*?)(\n## |\Z)", md, re.S)
        return [ln for ln in (m.group(1).splitlines() if m else []) if ln.strip().startswith("-")]

    rec = json.loads((d / "record.json").read_text(encoding="utf-8")) if (d / "record.json").exists() else {}
    cost = json.loads((d / "cost.json").read_text(encoding="utf-8")) if (d / "cost.json").exists() else {}
    searches = sum(int(e.get("searches", 0)) for e in cost.get("entries", []))
    return {"meetings": 0, "prompt_revisions": 0, "sources_found": searches, "sources_opened": 0, "calculations": 0,
            "simulations": 0, "sketches": 0, "skills_used": 0, "concepts_compared": 1, "objections_raised": 0,
            "parts": len(section("Parts")), "numbers_with_basis": len(section("Key numbers")),
            "constraint_rows": len(section("Constraint check")), "risks": len(section("Risks")),
            "fabrication_stages": 0, "operating_steps": 0, "measurement_chain": 0, "connections": 0,
            "wall_seconds": rec.get("wall_seconds")}


def main() -> int:
    out = Path(sys.argv[1])
    table = {}
    for arg in sys.argv[2:]:
        name, path = arg.split("=", 1)
        p = Path(path)
        table[name] = hs_depth(p) if (p / "stage_a").exists() else baseline_depth(p)
    out.write_text(json.dumps(table, indent=2), encoding="utf-8")
    keys = list(next(iter(table.values())))
    print("item".ljust(20) + "".join(n[:11].rjust(12) for n in table))
    for k in keys:
        print(k[:20].ljust(20) + "".join(str(table[n].get(k, "")).rjust(12) for n in table))
    return 0


if __name__ == "__main__":
    sys.exit(main())
