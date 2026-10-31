from pathlib import Path

from hs import config
from hs.fake_client import FakeClient
from hs.master_prompt import MasterPrompt, roster_of, split_master_prompt
from hs.schemas import Gradients, MasterPromptRewrite, RevertTarget, RewriteSection


def _master(tmp_path: Path) -> MasterPrompt:
    client = FakeClient(run_dir=tmp_path)
    from hs.schemas import Problem

    problem = Problem(title="T", statement="S", constraints=["c1"], criteria=[], attachments=[])
    return MasterPrompt.rev0(client, problem, "", tmp_path)


def test_rev0_headings_and_roster(tmp_path):
    master = _master(tmp_path)
    headings = [h for h, _ in master.sections]
    assert headings == ["## 1. Problem", "## 2. Roles", "## 3. Tools",
                        "## 4. Meeting protocol", "## 5. Criteria", "## 6. Lessons applied"]
    assert len(roster_of(master.sections)) == 3
    for fixed in config.FIXED_CRITERIA:
        assert fixed in dict(master.sections)["## 5. Criteria"]
    assert (tmp_path / "master_prompt" / "rev_000.md").exists()
    assert len(split_master_prompt(master.text())) == 6


def test_guard_removing_fixed_criterion_refused(tmp_path):
    master = _master(tmp_path)
    before = dict(master.sections)["## 5. Criteria"]
    rewrite = MasterPromptRewrite(
        sections=[RewriteSection(heading="## 5. Criteria", new_text="Be excellent.")],
        change_note="bad")
    report = master.apply_rewrite(rewrite)
    assert report.get("guard_reasked")
    assert dict(master.sections)["## 5. Criteria"] == before
    report2 = master.apply_rewrite(rewrite, _guard_retry=True)
    assert dict(master.sections)["## 5. Criteria"] == before
    assert report2["changed"] == []


def test_shrink_check(tmp_path):
    master = _master(tmp_path)
    long_protocol = "word " * 200
    master.sections = [(h, long_protocol if h == "## 4. Meeting protocol" else b)
                       for h, b in master.sections]
    rewrite = MasterPromptRewrite(
        sections=[RewriteSection(heading="## 4. Meeting protocol", new_text="short.")],
        change_note="shrink")
    report = master.apply_rewrite(rewrite)
    assert report["shrink_asked"] == ["## 4. Meeting protocol"]
    report2 = master.apply_rewrite(rewrite, _shrink_retry=True)
    assert report2["changed"] == ["## 4. Meeting protocol"]


def test_revert_only_named_section(tmp_path):
    master = _master(tmp_path)
    original_protocol = dict(master.sections)["## 4. Meeting protocol"]
    # rev1: change protocol + tools (confirmed shrink re-ask applies the second time)
    rewrite_v1 = MasterPromptRewrite(sections=[
        RewriteSection(heading="## 4. Meeting protocol", new_text="Protocol v1 text."),
        RewriteSection(heading="## 3. Tools", new_text="Tools v1 text."),
    ], change_note="v1")
    first = master.apply_rewrite(rewrite_v1)
    if first.get("shrink_asked"):
        master.apply_rewrite(rewrite_v1, _shrink_retry=True)
    assert master.rev == 1
    gradients = Gradients(sections_to_change=["## 4. Meeting protocol"], root_cause="repeat",
                          same_problem_as_before=True,
                          revert_sections=[RevertTarget(heading="## 4. Meeting protocol", to_revision=0)])
    reverted = master.apply_reverts(gradients)
    assert reverted == ["## 4. Meeting protocol"]
    by = dict(master.sections)
    assert by["## 4. Meeting protocol"] == original_protocol
    assert by["## 3. Tools"] == "Tools v1 text."


def test_diff_shows_only_rewritten_sections(tmp_path):
    master = _master(tmp_path)
    rewrite = MasterPromptRewrite(sections=[
        RewriteSection(heading="## 4. Meeting protocol",
                       new_text="Cycle 1 decompose. Cycles 2+ defend with evidence and vote late."),
    ], change_note="only protocol")
    first = master.apply_rewrite(rewrite)
    if first.get("shrink_asked"):
        master.apply_rewrite(rewrite, _shrink_retry=True)
    diff = (tmp_path / "master_prompt" / "diff_001.md").read_text()
    assert "## ## 4. Meeting protocol" in diff or "## 4. Meeting protocol" in diff
    assert "## 3. Tools" not in diff
