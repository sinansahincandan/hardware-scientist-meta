"""Stage B rerun: solution discovery and schematic-failure routing."""
from __future__ import annotations

import json
from pathlib import Path

from hs.stage_b_rerun import find_accepted_solution


def _seed_run(tmp_path: Path, accept: bool) -> Path:
    run = tmp_path / "run"
    it = run / "stage_a" / "iter_00"
    it.mkdir(parents=True)
    sol = {
        "title": "t", "problem_restatement": "p", "mechanism_sentence": "m",
        "decisive_choices": ["a", "b", "c"], "open_question": "q",
        "concept": {"working_principle": "w", "parts": []},
        "figure_spec": {"system_view": "s", "critical_part_id": "P1"},
    }
    (it / "solution.json").write_text(json.dumps(sol), encoding="utf-8")
    (it / "verdict.json").write_text(json.dumps({"accept": accept, "feedback": "f"}), encoding="utf-8")
    return run


def test_find_accepted_solution(tmp_path: Path) -> None:
    run = _seed_run(tmp_path, accept=True)
    sol, path = find_accepted_solution(run)
    assert sol.title == "t"
    assert path.name == "solution.json"


def test_find_falls_back_to_latest(tmp_path: Path) -> None:
    run = _seed_run(tmp_path, accept=False)
    sol, _ = find_accepted_solution(run)
    assert sol.title == "t"
