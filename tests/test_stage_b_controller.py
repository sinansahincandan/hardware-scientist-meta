import json
from pathlib import Path

import pytest

from hs.controller import Controller
from hs.fake_client import FakeClient
from hs.lessons import filter_candidates
from hs.schemas import LessonCandidate, Problem
from hs.stage_b.designer_eval import DesignerEval, decide
from hs.stage_b.schematic import build_spec_from_solution, check_spec


@pytest.fixture(autouse=True)
def _lessons_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("HS_LESSONS_PATH", str(tmp_path / "lessons.md"))
    monkeypatch.chdir(tmp_path)


def _run(tmp_path: Path, scenario: str = "happy") -> Path:
    problem = Problem(title="Test device", statement="Design a test device.",
                      constraints=["concept level"], criteria=[], attachments=[])
    client = FakeClient(scenario=scenario)
    result = Controller(client).run(problem, base=tmp_path / "runs")
    return result.run_dir


def _solution():
    from hs.controller import Controller  # noqa: F401
    from hs.stage_a.meeting import MeetingResult, Secretary

    # build a solution through a tiny fake meeting-free path: use Secretary on empty board
    from hs.stage_a.whiteboard import Whiteboard

    client = FakeClient()
    board = Whiteboard()
    result = MeetingResult(board=board, transcript=[], cycles_used=2, closed_by="consensus")
    problem = Problem(title="T", statement="S", constraints=[], criteria=[], attachments=[])
    import tempfile

    with tempfile.TemporaryDirectory():
        return Secretary(client)._from_board(result, problem)


def test_decide_routing():
    assert decide(DesignerEval(s1_faithful=True, s2_flaw=False), 0) == "s1_pass"
    assert decide(DesignerEval(s1_faithful=False, s2_flaw=False), 0) == "s1_retry"
    assert decide(DesignerEval(s1_faithful=False, s2_flaw=False), 2) == "s2_return"
    assert decide(DesignerEval(s1_faithful=True, s2_flaw=True, s2_feedback="x"), 0) == "s2_return"


def test_schematic_checks():
    solution = _solution()
    spec = build_spec_from_solution(solution)
    assert check_spec(spec, solution) == []
    broken = spec.model_copy(update={"nodes": spec.nodes[:-1]})
    assert check_spec(broken, solution)


def test_fake_happy_run_end_to_end(tmp_path):
    run_dir = _run(tmp_path)
    assert (run_dir / "final" / "figure.png").exists()
    for panel in ("panel_A.png", "panel_B.png", "panel_C.png", "panel_D.png"):
        assert (run_dir / "final" / panel).exists()
    assert (run_dir / "final" / "rationale.md").exists()
    report = (run_dir / "report.html").read_text()
    for marker in ("1. Input", "2. Timeline", "3. Per iteration", "4. Revision timeline",
                   "4b. Board", "5. Stage B rounds", "6. Final figure", "Cost table"):
        assert marker in report
    board = (run_dir / "board.html").read_text()
    assert "sticky" in board and "E1" in board and "type='range'" in board or 'type="range"' in board
    cost = json.loads((run_dir / "cost.json").read_text())
    assert cost["total_usd"] > 0
    assert (run_dir / "trace.md").exists()
    archive = [json.loads(l) for l in (run_dir / "archive.jsonl").read_text().splitlines() if l.strip()]
    assert [e["status"] for e in archive] == ["rejected", "accepted"]


def test_fake_schematic_fail_returns_to_a(tmp_path):
    run_dir = _run(tmp_path, scenario="schematic_fail")
    archive = [json.loads(l) for l in (run_dir / "archive.jsonl").read_text().splitlines() if l.strip()]
    assert any(e["status"] == "rejected_by_designer" for e in archive)
    assert (run_dir / "final" / "figure.png").exists()  # second attempt passes


def test_fake_s1_three_fail_then_pass(tmp_path):
    run_dir = _run(tmp_path, scenario="s1_three_fail")
    entries = [json.loads(l) for l in (run_dir / "image_archive.jsonl").read_text().splitlines() if l.strip()]
    assert [e["decision"] for e in entries[:3]] == ["s1_retry", "s1_retry", "s2_return"]
    assert entries[-1]["decision"] == "s1_pass"
    assert (run_dir / "final" / "figure.png").exists()


def test_fake_cost_cap_best_effort(tmp_path):
    run_dir = _run(tmp_path, scenario="cost_cap")
    report = (run_dir / "report.html").read_text()
    assert "6. Final figure" in report
    cost = json.loads((run_dir / "cost.json").read_text())
    assert cost["total_usd"] > 0


def test_lessons_filter():
    kept = filter_candidates([
        LessonCandidate(text="Require evidence before votes.", category="process", structural=True),
        LessonCandidate(text="Device needs red paint.", category="process", structural=False),
        LessonCandidate(text="x" * 250, category="tools", structural=True),
    ], existing_text="")
    assert [c.text for c in kept] == ["Require evidence before votes."]
