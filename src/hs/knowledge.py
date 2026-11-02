"""knowledge/ (Fig. 1, Fig. 2): what carries over between problems.

- knowledge/lessons.md   process lessons with ids, source run and a note per later use (hs.lessons)
- knowledge/insights/    engineering findings per problem, with source run and evidence ids; members search
                         them with the search_knowledge tool (each hit becomes whiteboard evidence)
- knowledge/tools/       tools that passed their sandbox smoke test, loaded in later problems; the Manager may
                         retire one with a written reason (moved to knowledge/tools/retired/)

Read at the start of a problem, updated at its end. Fake runs write into their run folder.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from hs import config


def knowledge_dir() -> Path:
    override = os.environ.get("HS_KNOWLEDGE_DIR")
    return Path(override) if override else config.PROJECT_ROOT / "knowledge"


# -- insights ----------------------------------------------------------------------------------
def write_insights(client: Any, run_dir: Path, problem_title: str, solution_json: str, evidence: list[Any],
                   base: Path | None = None) -> Path | None:
    """One call at the end of a problem: engineering findings that would help a different future problem,
    each tied to evidence ids from this run's board."""
    from hs.schemas import Insights

    if not evidence:
        return None
    table = "\n".join(f"{e.id} [{e.tool}] {e.purpose}: {e.output_summary}" for e in evidence[:120])
    result: Insights = client.structured(
        "insights", Insights,
        "You distil engineering findings for a library that future, different design problems will search.",
        "From this solved problem, write 2 to 5 findings about the engineering domain (a physical regime, a "
        "rule of thumb with its numbers, a component class and its limits, a standard and what it requires) that "
        "would help a DIFFERENT future problem. Never write process advice or anything about this specific "
        "device's design choices. Each finding cites the evidence ids it rests on.\n\n"
        f"PROBLEM: {problem_title}\n\nSOLUTION:\n{solution_json}\n\nEVIDENCE:\n{table}")
    by_id = {e.id: e for e in evidence}
    out_dir = (base or knowledge_dir()) / "insights"
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# Insights from {problem_title}", f"Source run: {run_dir.name}", ""]
    for item in result.items:
        lines.append(f"## {item.title}")
        lines.append(item.text)
        cited = [f"{eid} ({by_id[eid].purpose}: {by_id[eid].output_summary})" for eid in item.evidence_ids if eid in by_id]
        lines.append("Evidence: " + ("; ".join(cited) if cited else "none cited"))
        lines.append("")
    path = out_dir / f"{run_dir.name}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def search_insights(query: str, limit: int = 4, base: Path | None = None) -> list[dict[str, str]]:
    """Plain word-overlap search over all insight entries (no model call)."""
    words = {w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2}
    hits: list[tuple[int, dict[str, str]]] = []
    for path in sorted(((base or knowledge_dir()) / "insights").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        source = next((line.split(": ", 1)[1] for line in text.splitlines() if line.startswith("Source run: ")), path.stem)
        for block in text.split("\n## ")[1:]:
            title, _, body = block.partition("\n")
            score = len(words & set(re.findall(r"[a-z0-9]+", block.lower())))
            if score:
                hits.append((score, {"title": title.strip(), "text": body.strip(), "source": source}))
    hits.sort(key=lambda h: -h[0])
    return [h for _, h in hits[:limit]]


# -- tools -------------------------------------------------------------------------------------
def carried_tools(base: Path | None = None) -> dict[str, dict[str, Any]]:
    tools: dict[str, dict[str, Any]] = {}
    for path in sorted(((base or knowledge_dir()) / "tools").glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            tools[record["name"]] = record
        except Exception:  # noqa: S112 — a corrupt tool file is skipped
            continue
    return tools


def carry_tools(run_dir: Path, base: Path | None = None) -> list[str]:
    """Copy this run's registered (smoke-tested) tools into knowledge/tools/."""
    out = (base or knowledge_dir()) / "tools"
    out.mkdir(parents=True, exist_ok=True)
    carried: list[str] = []
    for path in sorted((run_dir / "tools").glob("*.json")) if (run_dir / "tools").exists() else []:
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("carried_from"):
            continue  # loaded from knowledge/ already
        record["source_run"] = run_dir.name
        (out / path.name).write_text(json.dumps(record, indent=2), encoding="utf-8")
        carried.append(record["name"])
    return carried


def retire_tool(name: str, reason: str, run_id: str, base: Path | None = None) -> bool:
    src = (base or knowledge_dir()) / "tools" / f"{name}.json"
    if not src.exists():
        return False
    dest = src.parent / "retired"
    dest.mkdir(parents=True, exist_ok=True)
    record = json.loads(src.read_text(encoding="utf-8"))
    record["retired"] = {"reason": reason, "run": run_id}
    (dest / src.name).write_text(json.dumps(record, indent=2), encoding="utf-8")
    src.unlink()
    return True
