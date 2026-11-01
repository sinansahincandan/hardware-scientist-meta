"""v2 B3/A5: rewrite headings never silently lost; Manager tool proposals."""
from __future__ import annotations

from pathlib import Path

from hs.master_prompt import MasterPrompt
from hs.schemas import Gradients, MasterPromptRewrite, RewriteSection, ToolProposal
from hs.stage_a.manager import Manager


def _master(tmp_path: Path) -> MasterPrompt:
    from hs import config

    sections = [
        ("## 1. Problem", "p"),
        ("## 2. Roles", "### A\n### B\n### C\n"),
        ("## 3. Tools", "old tools text"),
        ("## 4. Meeting protocol", "proto"),
        ("## 5. Criteria", "\n".join(config.FIXED_CRITERIA)),
        ("## 6. Lessons applied", "lessons"),
    ]
    master = MasterPrompt(tmp_path, "t", sections, rev=0)
    master.save()
    return master


def test_numbered_heading_maps_and_saves_rev_and_diff(tmp_path: Path) -> None:
    master = _master(tmp_path)
    rewrite = MasterPromptRewrite(
        sections=[RewriteSection(heading="## 3. Process", new_text="new tools text, longer")],
        change_note="retitle test",
    )
    report = master.apply_rewrite(rewrite)
    assert report["changed"] == ["## 3. Tools"]
    assert (tmp_path / "master_prompt" / "rev_001.md").exists()
    assert (tmp_path / "master_prompt" / "diff_001.md").exists()
    assert "new tools text" in dict(master.sections)["## 3. Tools"]


def test_unknown_heading_is_reported_not_silent(tmp_path: Path) -> None:
    master = _master(tmp_path)
    rewrite = MasterPromptRewrite(
        sections=[RewriteSection(heading="## 9. Nowhere", new_text="x")],
        change_note="bad heading",
    )
    report = master.apply_rewrite(rewrite)
    assert report["dropped_headings"] == ["## 9. Nowhere"]
    assert not (tmp_path / "master_prompt" / "rev_001.md").exists()


class _StubTools:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def new_tool(self, author, name, description, parameters, python_source, smoke_test_input):
        self.calls.append(name)
        return True, "ok"


def test_manager_tool_proposals_capped_at_two(tmp_path: Path) -> None:
    manager = Manager(client=None, master=_master(tmp_path))
    tools = _StubTools()
    proposals = [ToolProposal(name=f"tool_{i}", description="d", python_source="def run(a): return 1")
                 for i in range(4)]
    registered = manager.register_proposed_tools(Gradients(new_tool_proposals=proposals), tools)
    assert registered == ["tool_0", "tool_1"]
    assert tools.calls == ["tool_0", "tool_1"]
    # Cap persists across iterations.
    assert manager.register_proposed_tools(Gradients(new_tool_proposals=proposals), tools) == []


class _StubRev0Client:
    is_fake = False

    def free_text(self, role, instructions, user_text):
        return ("## 2. Roles\n### A\nmech\n### B\ntherm\n### C\nfab\n"
                "## 3. Criteria\nstray criteria heading inside\n"
                "## 3. Tools\nuse calc\n## 4. Meeting protocol\nspeak clearly\n"
                "## 5. Pipeline\nstray\n"), []


def test_rev0_saved_document_has_only_canonical_headings(tmp_path: Path) -> None:
    import re as _re

    from hs.schemas import Problem

    problem = Problem(title="t", statement="p")
    master = MasterPrompt.rev0(_StubRev0Client(), problem, "", tmp_path)
    saved = (tmp_path / "master_prompt" / "rev_000.md").read_text(encoding="utf-8")
    headings = _re.findall(r"^## .*", saved, flags=_re.M)
    assert headings == ["## 1. Problem", "## 2. Roles", "## 3. Tools",
                        "## 4. Meeting protocol", "## 5. Criteria", "## 6. Lessons applied"]
    assert "stray" not in saved
    assert master.rev == 0
