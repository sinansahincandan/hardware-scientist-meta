"""Markdown master prompt: heading split, rewrite guards, shrink check, revert (spec §3.2)."""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path
from typing import Any

from hs import config
from hs.schemas import Gradients, MasterPromptRewrite, Problem

HEADINGS = ["## 1. Problem", "## 2. Roles", "## 3. Tools", "## 4. Meeting protocol",
            "## 5. Criteria", "## 6. Lessons applied"]


def split_master_prompt(text: str) -> list[tuple[str, str]]:
    """Ordered [(heading, body)] split on the six fixed ## headings."""
    positions: list[tuple[str, int]] = []
    for heading in HEADINGS:
        idx = text.find(heading)
        if idx >= 0:
            positions.append((heading, idx))
    positions.sort(key=lambda p: p[1])
    out: list[tuple[str, str]] = []
    for i, (heading, start) in enumerate(positions):
        body_start = start + len(heading)
        end = positions[i + 1][1] if i + 1 < len(positions) else len(text)
        out.append((heading, text[body_start:end].strip("\n")))
    return out


def join_sections(title: str, rev: int, sections: list[tuple[str, str]]) -> str:
    parts = [f"# Master prompt — {title} — Rev {rev}"]
    for heading, body in sections:
        parts.append(f"{heading}\n{body.strip()}")
    return "\n\n".join(parts) + "\n"


def roster_of(sections: list[tuple[str, str]]) -> list[str]:
    body = dict(sections).get("## 2. Roles", "")
    return re.findall(r"^###\s+(.+?)\s*$", body, flags=re.MULTILINE)


def member_block(sections: list[tuple[str, str]], member: str) -> str:
    body = dict(sections).get("## 2. Roles", "")
    match = re.search(rf"^###\s+{re.escape(member)}\s*$", body, flags=re.MULTILINE)
    if not match:
        return ""
    rest = body[match.end():]
    nxt = re.search(r"^###\s+", rest, flags=re.MULTILINE)
    return (rest[: nxt.start()] if nxt else rest).strip()


def member_instructions(sections: list[tuple[str, str]], member: str) -> str:
    by = dict(sections)
    chunks = [f"### {member}\n{member_block(sections, member)}"]
    for heading in ["## 1. Problem", "## 3. Tools", "## 4. Meeting protocol", "## 5. Criteria", "## 6. Lessons applied"]:
        chunks.append(f"{heading}\n{by.get(heading, '')}")
    return "\n\n".join(chunks)


def guard_violations(old: list[tuple[str, str]], new: list[tuple[str, str]]) -> list[str]:
    problems: list[str] = []
    old_by, new_by = dict(old), dict(new)
    if old_by.get("## 1. Problem", "") != new_by.get("## 1. Problem", ""):
        problems.append("## 1. Problem must remain unchanged")
    criteria = new_by.get("## 5. Criteria", "")
    for fixed in config.FIXED_CRITERIA:
        if fixed not in criteria:
            problems.append(f"fixed criterion missing verbatim: {fixed[:40]}...")
    n_members = len(roster_of(new))
    if not (3 <= n_members <= config.MAX_MEMBERS):
        problems.append(f"roster size {n_members} outside 3..{config.MAX_MEMBERS}")
    return problems


def shrink_fraction(old_text: str, new_text: str) -> float:
    if len(old_text) == 0:
        return 0.0
    return max(0.0, (len(old_text) - len(new_text)) / len(old_text))


class MasterPrompt:
    def __init__(self, run_dir: Path, title: str, sections: list[tuple[str, str]], rev: int = 0) -> None:
        self.run_dir = run_dir
        self.title = title
        self.sections = sections
        self.rev = rev
        self.no_progress_streak = 0
        self.history: list[dict[str, Any]] = []

    # -- persistence ---------------------------------------------------------
    @property
    def _dir(self) -> Path:
        d = self.run_dir / "master_prompt"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def text(self) -> str:
        return join_sections(self.title, self.rev, self.sections)

    def save(self) -> Path:
        path = self._dir / f"rev_{self.rev:03d}.md"
        path.write_text(self.text(), encoding="utf-8")
        return path

    def section_at_revision(self, heading: str, rev: int) -> str | None:
        path = self._dir / f"rev_{rev:03d}.md"
        if not path.exists():
            return None
        return dict(split_master_prompt(path.read_text(encoding="utf-8"))).get(heading)

    # -- rev0 ------------------------------------------------------------------
    @classmethod
    def rev0(cls, client: Any, problem: Problem, lessons_text: str, run_dir: Path) -> MasterPrompt:
        problem_block = json.dumps(problem.model_dump(), indent=2)
        if getattr(client, "is_fake", False):
            client.record_fake("master_rev0")
            roles = (
                "### Mechanics\nStructural and mechanism design; challenges load paths and forces.\n\n"
                "### Thermal\nThermal and energy analysis; challenges heat flows and duty cycles.\n\n"
                "### Fabrication\nManufacturing and assembly; challenges buildability and part choice.\n"
            )
        else:
            text, _ = client.free_text(
                "master_rev0",
                "Write sections 2-6 of a master prompt as Markdown with the exact ## headings. "
                "Choose 3-5 members with distinct domains (### <name> under ## 2. Roles).",
                f"Problem:\n{problem_block}\n\nLessons:\n{lessons_text}",
            )
            sections = dict(split_master_prompt(text))
            roles = sections.get("## 2. Roles", "")
            if not roles:
                text, _ = client.free_text("master_rev0", "Previous output missed headings. Rewrite with exact ## headings.",
                                           f"Problem:\n{problem_block}\n\nLessons:\n{lessons_text}")
                sections = dict(split_master_prompt(text))
                roles = sections.get("## 2. Roles", "")
        criteria_lines = list(config.FIXED_CRITERIA) + list(problem.criteria)
        criteria = "\n".join(f"- {c}" for c in criteria_lines)
        tools_text = ("Use calc for quick estimates, simulate for sweeps, sketch for layouts, "
                      "web_search for standards and datasheets. All tools are always available.")
        protocol = config.DEFAULT_PROTOCOL
        lessons_applied = lessons_text.strip() or "(no lessons yet)"
        if not getattr(client, "is_fake", False):
            got = dict(split_master_prompt(text))  # type: ignore[has-type]
            tools_text = got.get("## 3. Tools", tools_text)
            protocol = got.get("## 4. Meeting protocol", protocol)
            if "## 5. Criteria" in got and all(f in got["## 5. Criteria"] for f in config.FIXED_CRITERIA):
                criteria = got["## 5. Criteria"]
        sections: list[tuple[str, str]] = [
            ("## 1. Problem", problem_block),
            ("## 2. Roles", roles),
            ("## 3. Tools", tools_text),
            ("## 4. Meeting protocol", protocol),
            ("## 5. Criteria", criteria),
            ("## 6. Lessons applied", lessons_applied),
        ]
        master = cls(run_dir, problem.title, sections, rev=0)
        master.save()
        return master

    # -- revert + rewrite --------------------------------------------------------
    def apply_reverts(self, gradients: Gradients) -> list[str]:
        reverted: list[str] = []
        by = dict(self.sections)
        for target in gradients.revert_sections:
            old_text = self.section_at_revision(target.heading, target.to_revision)
            if old_text is not None and target.heading in by and target.heading != "## 1. Problem":
                by[target.heading] = old_text
                reverted.append(target.heading)
        self.sections = [(h, by[h]) for h, _ in self.sections]
        return reverted

    def apply_rewrite(self, rewrite: MasterPromptRewrite, *, _guard_retry: bool = False,
                      _shrink_retry: bool = False) -> dict[str, Any]:
        """Apply section rewrites under guards + shrink check. Returns ops report."""
        old_sections = list(self.sections)
        old_by = dict(old_sections)
        new_by = dict(old_sections)
        changed: list[str] = []

        def _canonical(heading: str) -> str | None:
            # Optimizers often return "Meeting protocol" or "4. Meeting protocol"
            # instead of the exact "## 4. Meeting protocol": match by title words.
            wanted = re.sub(r"^#+\s*", "", heading).strip().lower()
            wanted = re.sub(r"^\d+\.?\s*", "", wanted)
            for known in old_by:
                title = re.sub(r"^#+\s*", "", known).strip().lower()
                title = re.sub(r"^\d+\.?\s*", "", title)
                if wanted == title:
                    return known
            # Fall back to the section number ("## 3. Process" -> "## 3. Tools"):
            # dropping a rewrite silently once lost a whole revision (run 02).
            number = re.match(r"^#+\s*(\d+)[.\s]", heading)
            if number:
                for known in old_by:
                    if re.match(rf"^#+\s*{number.group(1)}[.\s]", known):
                        return known
            return heading if heading in old_by else None

        dropped: list[str] = []
        for section in rewrite.sections:
            canonical = _canonical(section.heading)
            if canonical is None:
                dropped.append(section.heading)
                continue
            if canonical is not None:
                section = section.model_copy(update={"heading": canonical})
            if section.heading in new_by and section.heading != "## 1. Problem":
                if new_by[section.heading].strip() != section.new_text.strip():
                    changed.append(section.heading)
                new_by[section.heading] = section.new_text
        candidate = [(h, new_by[h]) for h, _ in old_sections]
        violations = guard_violations(old_sections, candidate)
        result: dict[str, Any] = {"changed": [], "violations": violations, "shrink_asked": [],
                                  "change_note": rewrite.change_note, "no_progress": False,
                                  "dropped_headings": dropped}
        if violations and not _guard_retry:
            result["guard_reasked"] = True
            return result  # caller re-asks once; state untouched
        if violations:
            # Second violation: keep old text for offending sections only.
            for heading in list(changed):
                trial = dict(candidate)
                trial[heading] = old_by[heading]
                if not guard_violations(old_sections, [(h, trial[h]) for h, _ in old_sections]):
                    candidate = [(h, trial[h]) for h, _ in old_sections]
                    changed.remove(heading)
            result["violations_kept_old"] = violations
        # shrink check
        shrinked = [h for h in changed if shrink_fraction(old_by[h], dict(candidate)[h]) > 0.5]
        if shrinked and not _shrink_retry:
            result["shrink_asked"] = shrinked
            result["changed"] = []
            return result  # caller re-asks once with removed lines
        if not changed:
            self.no_progress_streak += 1
            result["no_progress"] = True
            return result
        self.no_progress_streak = 0
        self.rev += 1
        self.sections = candidate
        self.save()
        # diff file
        lines = [f"# Diff rev {self.rev}", "", f"Change note: {rewrite.change_note}", ""]
        for heading in changed:
            lines.append(f"## {heading}")
            for line in difflib.unified_diff(old_by[heading].splitlines(), dict(candidate)[heading].splitlines(),
                                             lineterm="", n=1):
                if line.startswith("+") and not line.startswith("+++"):
                    lines.append(f"<green>+ {line[1:]}</green>")
                elif line.startswith("-") and not line.startswith("---"):
                    lines.append(f"<red>- {line[1:]}</red>")
            lines.append("")
        (self._dir / f"diff_{self.rev:03d}.md").write_text("\n".join(lines), encoding="utf-8")
        result["changed"] = changed
        self.history.append({"rev": self.rev, "changed": changed, "change_note": rewrite.change_note})
        return result
