"""Skills (knowledge/skills/): engineering procedures council members open when a design needs them.

A skill is one Markdown file with a short header — name and description (when to use it) — and a body: the steps,
the checks, typical values with where they came from. Members see only the list of names and descriptions in their
turn; they open a skill with the use_skill tool, and the opening is posted on the whiteboard as evidence. At the end
of every problem one call writes new skills from what this problem established, and writes a use note under each
skill that was opened (did it help, and why); a skill that keeps not helping is retired in writing
(knowledge/skills/retired/). Fake runs write into their run folder.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

from hs.knowledge import knowledge_dir

_NAME = re.compile(r"[^a-z0-9]+")


def skills_dir(base: Path | None = None) -> Path:
    return (base or knowledge_dir()) / "skills"


def slug(name: str) -> str:
    return _NAME.sub("-", name.lower()).strip("-")[:60] or "skill"


def _header(text: str) -> dict[str, str]:
    m = re.match(r"---\n(.*?)\n---\n", text, flags=re.DOTALL)
    out: dict[str, str] = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


def list_skills(base: Path | None = None) -> list[dict[str, str]]:
    d = skills_dir(base)
    return [{**_header(p.read_text(encoding="utf-8")), "file": p.name} for p in sorted(d.glob("*.md"))] \
        if d.exists() else []


def index_text(base: Path | None = None) -> str:
    """What a member sees every turn: one line per skill."""
    rows = [f"- {s.get('name', s['file'][:-3])}: {s.get('description', '')}" for s in list_skills(base)]
    return ("SKILLS from earlier problems (open one with use_skill when it applies; it is posted on the board):\n"
            + "\n".join(rows) + "\n") if rows else ""


def read_skill(name: str, base: Path | None = None) -> str | None:
    p = skills_dir(base) / f"{slug(name)}.md"
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8")
    return re.sub(r"\n## Use notes\n.*\Z", "", text, flags=re.DOTALL).strip()  # the procedure, without the history


def write_skill(name: str, description: str, body: str, source: str, base: Path | None = None) -> Path:
    d = skills_dir(base)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{slug(name)}.md"
    p.write_text(f"---\nname: {slug(name)}\ndescription: {' '.join(description.split())}\nsource: {source} "
                 f"({date.today().isoformat()})\n---\n\n{body.strip()}\n\n## Use notes\n", encoding="utf-8")
    return p


def add_note(name: str, run_id: str, member: str, note: str, base: Path | None = None) -> bool:
    p = skills_dir(base) / f"{slug(name)}.md"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8").rstrip() + f"\n- run {run_id} ({member}): {' '.join(note.split())}\n"
    p.write_text(text, encoding="utf-8")
    return True


def retire(name: str, why: str, run_id: str, base: Path | None = None) -> bool:
    p = skills_dir(base) / f"{slug(name)}.md"
    if not p.exists():
        return False
    dest = p.parent / "retired"
    dest.mkdir(exist_ok=True)
    (dest / p.name).write_text(p.read_text(encoding="utf-8") + f"\nRetired in run {run_id}: {why}\n", encoding="utf-8")
    p.unlink()
    return True


def update_skills(client: Any, run_id: str, problem_title: str, solution_json: str, evidence: list[Any],
                  base: Path | None = None) -> list[str]:
    """End of a problem: use notes for the skills that were opened, new skills from what this problem established,
    retirements with a written reason. Returns a list of plain log lines."""
    from hs.schemas import SkillUpdate

    opened = [(e.code_or_query, e.author, e.id) for e in evidence if e.tool == "use_skill"]
    table = "\n".join(f"{e.id} [{e.tool}, {e.author}] {e.purpose}: {e.output_summary}" for e in evidence[:120])
    existing = index_text(base) or "(none yet)"
    result: SkillUpdate = client.structured(
        "skills", SkillUpdate,
        "You maintain a library of engineering skills that AI council members open when a design needs them.",
        "A skill is a reusable engineering procedure for a kind of check or sizing a FUTURE, DIFFERENT design may "
        "need (for example sizing a battery for a duty cycle, checking that parts fit an envelope, tracing a load "
        "path, choosing a damper). Never a skill about this device's own choices, and never pipeline mechanics.\n"
        "1) For each skill this run opened (listed below), write one note: whether it helped and why, from the "
        "evidence. Set retire=true only if the notes show it misleads or never applies, and say why.\n"
        "2) Propose at most 3 NEW skills this problem established on evidence, not already in the library: name "
        "(2-5 words), description (one sentence: when to use it), body (Markdown: numbered steps, the checks, typical "
        "values with the evidence ids they came from). Skip if nothing new and reusable was established.\n\n"
        f"EXISTING SKILLS:\n{existing}\nOPENED IN THIS RUN: "
        + ("; ".join(f"{n} by {m} ({i})" for n, m, i in opened) or "none")
        + f"\n\nPROBLEM: {problem_title}\n\nSOLUTION:\n{solution_json[:6000]}\n\nEVIDENCE:\n{table}")
    log: list[str] = []
    who = {slug(n): m for n, m, _ in opened}
    for note in result.notes:
        if add_note(note.name, run_id, who.get(slug(note.name), "council"), note.note, base):
            log.append(f"skill {slug(note.name)}: use note written")
        if note.retire and retire(note.name, note.why or note.note, run_id, base):
            log.append(f"skill {slug(note.name)} retired: {note.why or note.note}")
    for new in result.new[:3]:
        if (skills_dir(base) / f"{slug(new.name)}.md").exists():
            continue
        write_skill(new.name, new.description, new.body, f"run {run_id}", base)
        log.append(f"new skill {slug(new.name)}")
    return log
