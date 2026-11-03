"""Seed knowledge/skills/ from the engineering findings of earlier problems (knowledge/insights/), one Meta call.

Usage: .venv/bin/python scripts/seed_skills.py
Each skill keeps the evidence ids and the run it came from; nothing is written by hand.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hs.client import MetaClient
from hs.knowledge import knowledge_dir
from hs.schemas import SkillUpdate
from hs.skills import index_text, skills_dir, slug, write_skill


def main() -> int:
    files = sorted((knowledge_dir() / "insights").glob("*.md"))
    corpus = "\n\n".join(f.read_text(encoding="utf-8") for f in files)
    client = MetaClient(run_dir=ROOT / "runs" / "seed_skills", max_cost=0.3)
    result: SkillUpdate = client.structured(
        "skills", SkillUpdate,
        "You maintain a library of engineering skills that AI council members open when a design needs them.",
        "From the findings below, write up to 8 skills. A skill is a reusable engineering procedure a FUTURE, "
        "DIFFERENT design may need (sizing, a check, a standard's limits, a regime test) — never one device's own "
        "choices. For each: name (2-5 words), description (one sentence: when to use it), body (Markdown: numbered "
        "steps, the checks, typical values, and for each value the source run and evidence ids it came from). Merge "
        "findings that are the same procedure. Leave notes empty.\n\nEXISTING SKILLS:\n"
        + (index_text() or "(none)") + f"\n\nFINDINGS (one file per earlier problem):\n{corpus}")
    for new in result.new[:8]:
        if (skills_dir() / f"{slug(new.name)}.md").exists():
            continue
        path = write_skill(new.name, new.description, new.body, "seeded from knowledge/insights (5 problems)")
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
