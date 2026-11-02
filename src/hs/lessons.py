"""Lessons: process memory across problems, in knowledge/lessons.md (Fig. 1 knowledge/; spec §6).
Each lesson has an id (L<n>); later runs add an indented note saying whether it helped."""
from __future__ import annotations

import difflib
import os
from datetime import date
from pathlib import Path
from typing import Any

from hs.schemas import Lessons

SECTIONS = {"process": "## Process", "prompts": "## Prompts", "tools": "## Tools",
            "image_model": "## Image model"}
ALL_HEADINGS = ["## Process", "## Prompts", "## Tools", "## Image model", "## User feedback"]


def lessons_path() -> Path:
    override = os.environ.get("HS_LESSONS_PATH")

    from hs.knowledge import knowledge_dir

    return Path(override) if override else knowledge_dir() / "lessons.md"


def load_lessons(path: Path | None = None) -> str:
    p = path or lessons_path()
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# Lessons\n\n" + "\n\n".join(f"{h}\n" for h in ALL_HEADINGS), encoding="utf-8")
    return p.read_text(encoding="utf-8")


def _existing_lines(text: str) -> list[str]:
    """Lesson texts without the "[date, run id]" suffix, so near-duplicates are recognized (A7)."""
    import re

    return [re.sub(r"\s*\[\d{4}-\d{2}-\d{2}, run [^\]]*\]\s*$", "",
                   re.sub(r"^L\d+:\s*", "", line[1:].strip()))
            for line in text.splitlines() if line.startswith("- ")]


def _next_id(text: str) -> int:
    import re

    ids = [int(m) for m in re.findall(r"^- L(\d+):", text, flags=re.MULTILINE)]
    return max(ids, default=0) + 1


def filter_candidates(candidates: list[Any], existing_text: str) -> list[Any]:
    existing = _existing_lines(existing_text)
    kept: list[Any] = []
    for cand in candidates:
        if not cand.structural:
            continue
        if len(cand.text) > 200:
            continue
        if any(difflib.SequenceMatcher(None, cand.text, line).ratio() >= 0.8 for line in existing):
            continue
        kept.append(cand)
        existing.append(cand.text)
    return kept[:5]


def append_lessons(new_by_category: dict[str, list[str]], run_id: str, path: Path | None = None) -> list[str]:
    p = path or lessons_path()
    text = load_lessons(p)
    added: list[str] = []
    for category, lines in new_by_category.items():
        heading = SECTIONS[category]
        block = ""
        for line in lines:
            block += f"- L{_next_id(text + block)}: {line} [{date.today().isoformat()}, run {run_id}]\n"
        added.extend(lines)
        if heading in text:
            idx = text.index(heading) + len(heading)
            text = text[:idx] + "\n" + block + text[idx:]
        else:
            text += f"\n{heading}\n{block}"
    p.write_text(text, encoding="utf-8")
    return added


def update_lessons(client: Any, trace_text: str, image_summary: str, run_id: str,
                   path: Path | None = None) -> list[str]:
    p = path or lessons_path()
    existing = load_lessons(p)
    result: Lessons = client.structured(
        "lessons", Lessons,
        "Propose at most 5 structural lessons about how the council and the Manager should work (never problem "
        "content, and never pipeline mechanics such as retries, caps, rounds, labels, sketches passed between "
        "steps, or gating — those live in code). Then, for each EXISTING lesson (by id, e.g. L3) that this run "
        "shows was applied or ignored, write in uses one sentence on whether it helped.",
        f"TRACE:\n{trace_text[-8000:]}\n\nIMAGE ARCHIVE:\n{image_summary}\n\nEXISTING LESSONS:\n{existing}")
    kept = filter_candidates(result.candidates, existing)
    by_cat: dict[str, list[str]] = {}
    for cand in kept:
        by_cat.setdefault(cand.category, []).append(cand.text)
    if by_cat:
        append_lessons(by_cat, run_id, p)
    if result.uses:
        record_uses(result.uses, run_id, p)
    return [c.text for c in kept]


def record_uses(uses: list[Any], run_id: str, path: Path | None = None) -> None:
    """Indented note under each lesson a run used: whether it helped (Fig. 1 knowledge/, B12)."""
    p = path or lessons_path()
    lines = p.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    notes = {u.lesson_id.strip(): u.note.strip() for u in uses}
    i = 0
    while i < len(lines):
        out.append(lines[i])
        lid = lines[i][2:].split(":", 1)[0] if lines[i].startswith("- L") else ""
        i += 1
        while i < len(lines) and lines[i].startswith("  - "):
            out.append(lines[i])
            i += 1
        if lid in notes:
            out.append(f"  - used in run {run_id}: {notes[lid]}")
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def add_user_feedback(text: str, path: Path | None = None) -> None:
    p = path or lessons_path()
    content = load_lessons(p)
    if "## User feedback" in content:
        idx = content.index("## User feedback") + len("## User feedback")
        content = content[:idx] + f"\n- {text}\n" + content[idx:]
    else:
        content += f"\n## User feedback\n- {text}\n"
    p.write_text(content, encoding="utf-8")
