"""Round 3 A2: pages are built from the run's files; no meeting is narrated where none ran."""
from __future__ import annotations

from pathlib import Path

import pytest

from hs.controller import Controller
from hs.fake_client import FakeClient
from hs.schemas import Problem
from hs.showcase_build import build_showcase
from hs.stage_b_rerun import rerun_stage_b


@pytest.fixture(autouse=True)
def _lessons_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("HS_LESSONS_PATH", str(tmp_path / "lessons.md"))


def _full_run(tmp_path: Path) -> Path:
    problem = Problem(title="Test device", statement="Design a test device that lifts a box.",
                      constraints=["concept level"], criteria=[], attachments=[])
    return Controller(FakeClient()).run(problem, base=tmp_path / "runs").run_dir


def test_dossier_sentences_come_from_the_run(tmp_path: Path) -> None:
    run_dir = _full_run(tmp_path)
    build_showcase([run_dir], tmp_path / "showcase")
    slug = next(p for p in (tmp_path / "showcase").iterdir() if p.is_dir())
    dossier = (slug / "dossier.html").read_text()
    index = (tmp_path / "showcase" / "index.html").read_text()
    assert "Design a test device that lifts a box." in index  # problem statement, not the title
    assert "The meeting ran" in dossier and "Conformance" not in dossier and "Times exercised" not in dossier
    assert "rev_-0" not in dossier and "s1_retry" not in index and "fix mode" not in index
    assert dossier.count("<svg") == 2  # one overlay per stage


def test_stage_b_rerun_pages_narrate_no_meeting(tmp_path: Path) -> None:
    source = _full_run(tmp_path)
    result = rerun_stage_b(FakeClient(), source, base=tmp_path / "runs")
    rerun = Path(result["run_dir"])
    assert not (rerun / "stage_a").exists() and (rerun / "seeded_from.json").exists()
    report = (rerun / "report.html").read_text()
    assert "no council meeting ran in this run" in report and "The council meeting" not in report
    build_showcase([rerun], tmp_path / "show2")
    slug = next(p for p in (tmp_path / "show2").iterdir() if p.is_dir())
    dossier = (slug / "dossier.html").read_text()
    assert "No council meeting ran in this run" in dossier and "The meeting ran" not in dossier


def test_report_shows_member_block_changes(tmp_path: Path) -> None:
    from hs.master_prompt import MasterPrompt
    from hs.report import council_changes_html

    master = MasterPrompt(tmp_path, "t", [("## 1. Problem", "p"), ("## 2. Roles", "### A\nold way\n### B\nb")])
    master.save()
    master.commit({"## 2. Roles": "### A\ncheck the edge load first\n### C\nnew member"}, "coach")
    page = council_changes_html(tmp_path)
    assert "check the edge load first" in page and "C</b> joined" in page and "B</b> left" in page
