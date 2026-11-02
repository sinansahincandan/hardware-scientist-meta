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


class _OptimizerClient:
    """Scripted Manager calls: step 1, step 2, then the optimizer answers in order."""

    is_fake = False

    def __init__(self, rewrites: list[MasterPromptRewrite], agenda: str = "") -> None:
        self.rewrites, self.agenda = list(rewrites), agenda

    def structured(self, role, model_cls, instructions, user_text, image_paths=None):
        from hs.schemas import OutputGradient

        if model_cls is OutputGradient:
            return OutputGradient(items=[], summary="s")
        if model_cls is Gradients:
            return Gradients(root_cause="r", agenda=self.agenda)
        return self.rewrites.pop(0)


def _edit(tmp_path: Path, client: _OptimizerClient, protocol: str | None = None) -> tuple[MasterPrompt, dict]:
    from hs.stage_a.manager import Manager
    from hs.stage_a.meeting import MeetingResult
    from hs.stage_a.whiteboard import Whiteboard

    master = _master(tmp_path)
    if protocol is not None:
        master.sections = [(h, protocol if h == "## 4. Meeting protocol" else b) for h, b in master.sections]
        master.save()
    iter_dir = tmp_path / "iter"
    iter_dir.mkdir()
    room = MeetingResult(board=Whiteboard(), transcript=[], cycles_used=2, closed_by="cap")
    solution = type("S", (), {"model_dump_json": lambda self, **k: "{}"})()
    report = Manager(client, master).edit(room, solution, "feedback", iter_dir)
    return master, report


def test_guard_keeps_other_sections_and_reasks_only_the_bad_one(tmp_path):
    """A3: one section breaking a guard never discards the rest; every optimizer output is saved."""
    bad = MasterPromptRewrite(sections=[
        RewriteSection(heading="## 5. Criteria", new_text="Be excellent."),
        RewriteSection(heading="## 3. Tools", new_text=(
            "Use calc for every load estimate and cite its evidence id; use simulate for sweeps over the "
            "operating range; sketch every mechanism you propose; search standards and datasheets first."))],
        change_note="first")
    still_bad = MasterPromptRewrite(sections=[RewriteSection(heading="## 5. Criteria", new_text="Still bad.")],
                                    change_note="second")
    master, report = _edit(tmp_path, _OptimizerClient([bad, still_bad]))
    by = dict(master.sections)
    assert "Use calc for every load estimate" in by["## 3. Tools"]
    for fixed in config.FIXED_CRITERIA:
        assert fixed in by["## 5. Criteria"]
    assert report["changed"] == ["## 3. Tools"] and any("## 5. Criteria kept" in n for n in report["notes"])
    assert (tmp_path / "iter" / "rewrite.json").exists()
    assert (tmp_path / "iter" / "rewrite_guard_reask.json").exists()


def test_shrink_reask_shows_removed_lines_and_applies_the_second_answer(tmp_path):
    long_protocol = "\n".join(f"line {i} of the protocol" for i in range(40))
    first = MasterPromptRewrite(sections=[RewriteSection(heading="## 4. Meeting protocol", new_text="short.")],
                                change_note="cut")
    confirm = MasterPromptRewrite(sections=[RewriteSection(heading="## 4. Meeting protocol",
                                                           new_text="short, confirmed.")], change_note="yes")
    client = _OptimizerClient([first, confirm])
    from hs.stage_a import manager as manager_mod

    seen: list[str] = []
    real = manager_mod.Manager._optimize

    def spy(self, instructions, user_text, out):
        seen.append(user_text)
        return real(self, instructions, user_text, out)

    manager_mod.Manager._optimize = spy
    try:
        master, _report = _edit(tmp_path, client, protocol=long_protocol)
    finally:
        manager_mod.Manager._optimize = real
    assert "line 7 of the protocol" in seen[1]  # removed lines are shown
    assert dict(master.sections)["## 4. Meeting protocol"] == "short, confirmed."
    assert (tmp_path / "iter" / "rewrite_shrink_reask.json").exists()


def test_agenda_is_written_into_meeting_protocol(tmp_path):
    from hs.stage_a.manager import AGENDA_HEADING

    master, _ = _edit(tmp_path, _OptimizerClient([MasterPromptRewrite(sections=[], change_note="none")],
                                                 agenda="Targeted: compute the stair-edge wheel load first."))
    protocol = dict(master.sections)["## 4. Meeting protocol"]
    assert AGENDA_HEADING in protocol and "stair-edge wheel load" in protocol
    assert master.rev == 1


def test_revert_only_named_section_and_revert_is_saved(tmp_path):
    master = _master(tmp_path)
    original_protocol = dict(master.sections)["## 4. Meeting protocol"]
    master.commit({"## 4. Meeting protocol": "Protocol v1 text.", "## 3. Tools": "Tools v1 text."}, "v1")
    assert master.rev == 1
    gradients = Gradients(sections_to_change=["## 4. Meeting protocol"], root_cause="repeat",
                          same_problem_as_before=True,
                          revert_sections=[RevertTarget(heading="## 4. Meeting protocol", to_revision=0)])
    assert master.apply_reverts(gradients) == ["## 4. Meeting protocol"]
    report = master.commit({}, "revert only")  # nothing else changed: the revert alone is a revision
    assert report["changed"] == ["## 4. Meeting protocol"] and master.rev == 2
    by = dict(master.sections)
    assert by["## 4. Meeting protocol"] == original_protocol
    assert by["## 3. Tools"] == "Tools v1 text."


def test_diff_shows_only_rewritten_sections(tmp_path):
    master = _master(tmp_path)
    master.commit({"## 4. Meeting protocol": "Cycle 1 decompose. Cycles 2+ defend with evidence and vote late."},
                  "only protocol")
    diff = (tmp_path / "master_prompt" / "diff_001.md").read_text()
    assert "## 4. Meeting protocol" in diff
    assert "## 3. Tools" not in diff
