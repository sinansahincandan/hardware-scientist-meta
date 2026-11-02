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


def section_problems(heading: str, old_text: str, new_text: str) -> list[str]:
    """The only two code guards (spec §3.2, round-3 B11): §1 never changes, and §5 keeps
    both fixed criteria verbatim. Checked per section, so one bad section never blocks the rest."""
    problems: list[str] = []
    if heading == "## 1. Problem" and new_text.strip() != old_text.strip():
        problems.append("## 1. Problem must remain unchanged")
    if heading == "## 5. Criteria":
        for fixed in config.FIXED_CRITERIA:
            if fixed not in new_text:
                problems.append(f"## 5. Criteria must contain this fixed criterion verbatim: {fixed}")
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

            def _clean(body: str) -> str:
                # A stray "## " section inside a body (the splitter folds its
                # text into the previous canonical section) becomes a phantom
                # heading in the saved document and teaches the optimizer
                # wrong heading names (seen in a real run). Drop the phantom
                # section: its heading line plus its text, up to the next
                # heading. "### " member headings survive.
                kept: list[str] = []
                dropping = False
                for line in body.splitlines():
                    if re.match(r"^##\s", line):
                        dropping = True
                        continue
                    if re.match(r"^###\s", line):
                        dropping = False
                    if not dropping:
                        kept.append(line)
                return "\n".join(kept).strip()

            roles = _clean(roles) or roles
            tools_text = _clean(got.get("## 3. Tools", tools_text))
            protocol = _clean(got.get("## 4. Meeting protocol", protocol))
            if config.PROPOSAL_RULE not in protocol:  # A5: the proposal rule is part of every rev 0
                protocol = protocol.rstrip() + "\n\n" + config.PROPOSAL_RULE
            if "## 5. Criteria" in got and all(f in got["## 5. Criteria"] for f in config.FIXED_CRITERIA):
                criteria = _clean(got["## 5. Criteria"])
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

    def resolve_heading(self, heading: str) -> str | None:
        """Map an optimizer heading onto a canonical one. Exact match first; otherwise the section
        number and the title must agree (an optimizer heading such as "## 3. Criteria", whose number
        and title name different sections, is ambiguous and is dropped, never guessed)."""
        known = [h for h, _ in self.sections]
        if heading in known:
            return heading
        number = re.match(r"^#*\s*(\d+)[.\s]", heading.strip())
        title = re.sub(r"^#*\s*(\d+\.?)?\s*", "", heading.strip()).lower()
        by_number = next((h for h in known if number and re.match(rf"^##\s*{number.group(1)}\.", h)), None)
        by_title = next((h for h in known if title and re.sub(r"^##\s*\d+\.\s*", "", h).lower() == title), None)
        if by_number and by_title and by_number != by_title:
            return None
        return by_number or by_title

    def propose(self, rewrite: MasterPromptRewrite) -> tuple[dict[str, str], list[str]]:
        """Canonical heading -> proposed text for every section the rewrite names, and the
        headings that could not be placed (recorded, never silently lost)."""
        proposed: dict[str, str] = {}
        dropped: list[str] = []
        for section in rewrite.sections:
            canonical = self.resolve_heading(section.heading)
            if canonical is None or canonical == "## 1. Problem":
                dropped.append(section.heading)
                continue
            proposed[canonical] = section.new_text
        return proposed, dropped

    def commit(self, new_texts: dict[str, str], change_note: str, notes: list[str] | None = None) -> dict[str, Any]:
        """Apply the given section texts (already guard-checked by the caller) on top of the current
        sections and save a revision when anything differs from the last saved revision."""
        saved = dict(split_master_prompt((self._dir / f"rev_{self.rev:03d}.md").read_text(encoding="utf-8"))) \
            if (self._dir / f"rev_{self.rev:03d}.md").exists() else dict(self.sections)
        by = dict(self.sections)
        by.update(new_texts)
        candidate = [(h, by[h]) for h, _ in self.sections]
        changed = [h for h, body in candidate if saved.get(h, "").strip() != body.strip()]
        result: dict[str, Any] = {"changed": changed, "change_note": change_note, "no_progress": not changed,
                                  "notes": notes or []}
        if not changed:
            self.no_progress_streak += 1
            return result
        self.no_progress_streak = 0
        self.rev += 1
        self.sections = candidate
        self.save()
        lines = [f"# Diff rev {self.rev}", "", f"Change note: {change_note}", ""]
        lines += [f"- {n}" for n in notes or []]
        for heading in changed:
            lines.append(f"## {heading}")
            for line in difflib.unified_diff(saved.get(heading, "").splitlines(), by[heading].splitlines(),
                                             lineterm="", n=1):
                if line.startswith("+") and not line.startswith("+++"):
                    lines.append(f"<green>+ {line[1:]}</green>")
                elif line.startswith("-") and not line.startswith("---"):
                    lines.append(f"<red>- {line[1:]}</red>")
            lines.append("")
        (self._dir / f"diff_{self.rev:03d}.md").write_text("\n".join(lines), encoding="utf-8")
        self.history.append({"rev": self.rev, "changed": changed, "change_note": change_note})
        return result
