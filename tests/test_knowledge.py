"""knowledge/ (Fig. 1): lessons with ids and use notes, insights search, carried and retired tools."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from hs import knowledge
from hs.lessons import append_lessons, load_lessons, record_uses
from hs.schemas import LessonUse


@pytest.fixture()
def kdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("HS_KNOWLEDGE_DIR", str(tmp_path / "k"))
    monkeypatch.delenv("HS_LESSONS_PATH", raising=False)
    return tmp_path / "k"


def test_lessons_get_ids_and_use_notes(kdir: Path) -> None:
    load_lessons()
    append_lessons({"process": ["Name who integrates the proposal."]}, "run_a")
    append_lessons({"process": ["Check loads against body weight."]}, "run_b")
    text = (kdir / "lessons_full.md").read_text()
    assert "- L1: Name who integrates" in text and "- L2: Check loads" in text
    record_uses([LessonUse(lesson_id="L1", note="helped: a proposal formed in cycle 2.")], "run_c")
    lines = (kdir / "lessons_full.md").read_text().splitlines()
    i = next(n for n, line in enumerate(lines) if line.startswith("- L1:"))
    assert lines[i + 1] == "  - used in run run_c: helped: a proposal formed in cycle 2."


def test_insights_search_and_search_knowledge_evidence(kdir: Path, tmp_path: Path) -> None:
    (kdir / "insights").mkdir(parents=True)
    (kdir / "insights" / "run1.md").write_text(
        "# Insights from A\nSource run: run1\n\n## Footbridge comfort limit\nPeak vertical acceleration below "
        "0.7 m/s2 for comfort.\nEvidence: E3\n\n## Stair riser heights\nResidential risers 150-197 mm.\nEvidence: E2\n")
    hits = knowledge.search_insights("vertical acceleration comfort")
    assert hits[0]["title"] == "Footbridge comfort limit" and hits[0]["source"] == "run1"
    from hs.stage_a.tools import ToolRunner
    from hs.stage_a.whiteboard import Whiteboard

    board = Whiteboard()
    _eid, out = ToolRunner(board, tmp_path / "run", tmp_path / "ev").search_knowledge("A", "stair riser", cycle=1)
    assert board.evidence[0].tool == "search_knowledge" and "Stair riser heights" in out


def test_tools_carry_over_and_retire(kdir: Path, tmp_path: Path) -> None:
    run = tmp_path / "run1"
    (run / "tools").mkdir(parents=True)
    (run / "tools" / "beam.json").write_text(json.dumps({"name": "beam", "description": "d", "parameters": {},
                                                         "python_source": "def run(a): return 1"}))
    assert knowledge.carry_tools(run) == ["beam"]
    from hs.stage_a.tools import ToolRunner
    from hs.stage_a.whiteboard import Whiteboard

    runner = ToolRunner(Whiteboard(), tmp_path / "run2", tmp_path / "ev2")
    assert runner.new_tools["beam"]["carried_from"] == "run1"
    assert any(s.get("name") == "beam" for s in runner.schemas())
    assert knowledge.retire_tool("beam", "gave wrong units", "run2")
    assert not (kdir / "tools" / "beam.json").exists()
    assert json.loads((kdir / "tools" / "retired" / "beam.json").read_text())["retired"]["reason"] == "gave wrong units"


def test_light_copy_is_short_and_counts_uses(kdir: Path) -> None:
    from hs.lessons import load_light

    load_lessons()
    append_lessons({"process": ["Name who integrates the proposal."]}, "run_a")
    record_uses([LessonUse(lesson_id="L1", note="helped: a proposal formed.")], "run_b")
    record_uses([LessonUse(lesson_id="L1", note="did not help: nobody read it.")], "run_c")
    light = load_light()
    assert "- L1: Name who integrates the proposal. (used 2×, helped 1×)" in light
    assert "run_a" not in light and "used in run" not in light
    assert (kdir / "lessons.md").exists() and "run_b" in (kdir / "lessons_full.md").read_text()


def test_skill_is_listed_opened_on_the_board_and_noted(kdir: Path, tmp_path: Path) -> None:
    from hs import skills
    from hs.fake_client import FakeClient
    from hs.stage_a.tools import ToolRunner
    from hs.stage_a.whiteboard import Whiteboard

    skills.write_skill("Battery duty check", "Use when a design carries a battery.",
                       "1. Energy per run = average power x run time.", "run_a")
    assert "battery-duty-check: Use when a design carries a battery." in skills.index_text()
    board = Whiteboard()
    eid, out = ToolRunner(board, tmp_path, tmp_path / "ev").use_skill("Mara", "battery duty check")
    assert eid == "E1" and "Energy per run" in out and board.evidence[0].tool == "use_skill"
    assert ToolRunner(board, tmp_path, tmp_path / "ev").use_skill("Mara", "nope")[1].startswith("error:")
    log = skills.update_skills(FakeClient(run_dir=tmp_path), "run_b", "T", "{}", board.evidence)
    assert "new skill fake-sizing-check" in log
    assert skills.read_skill("battery-duty-check") and "## Use notes" not in skills.read_skill("battery-duty-check")
