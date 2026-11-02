"""Round 3 C16-C18: SAM part map measurements, closed Stage B loop (keep or revert), deviations."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from hs.controller import Controller
from hs.fake_client import FakeClient
from hs.schemas import DesignerEval, PartMap, PartVisual, PreviousRegionStatus, Problem
from hs.stage_b import part_map as pm
from hs.stage_b.designer_eval import decide


@pytest.fixture(autouse=True)
def _lessons_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("HS_LESSONS_PATH", str(tmp_path / "lessons.md"))


def test_parse_sam_scales_boxes_to_the_render() -> None:
    raw = "<0f>0<|box;x1=10;y1=20;x2=29;y2=39;w=100;h=100|><|mask;x=0;y=0;data=1,1,!x|>,<0f>1<|box;x1=50;y1=50;x2=59;y2=59;w=100;h=100|>"
    assert pm.parse_sam(raw, 200, 400) == [(20.0, 80.0, 60.0, 160.0), (100.0, 200.0, 120.0, 240.0)]
    assert pm.parse_sam("", 10, 10) == []


def test_differences_are_measured_against_the_expectation() -> None:
    part_map = PartMap(parts=[
        PartVisual(part_id="W", visual_phrase="black wheel", count=6, long_axis="any", touches=["F"]),
        PartVisual(part_id="F", visual_phrase="steel frame", count=1, long_axis="vertical", size_vs="W", size_ratio=10),
        PartVisual(part_id="M", visual_phrase="grey motor", count=1),
    ])
    meas = {"size": [1000, 1000], "parts": {
        "W": {"boxes": [(0, 0, 100, 100), (110, 0, 210, 100)]},
        "F": {"boxes": [(600, 0, 1000, 200)]},  # horizontal, 4x the wheel, far from the wheels
        "M": {"boxes": []}}}
    diffs = pm.differences(meas, part_map)
    assert "expected 6 visible, found 2" in diffs["W"][0]
    assert any("touch F" in d for d in diffs["W"])
    assert any("vertical long axis, measured horizontal" in d for d in diffs["F"])
    assert any("size against W" in d for d in diffs["F"])
    assert diffs["M"] == ["not found by the segmenter as 'grey motor'"]
    again = pm.recheck({"size": [1000, 1000], "parts": {"M": {"boxes": [(0, 0, 9, 9)]}}}, {},
                       {"differences": diffs, "parts": meas["parts"]})
    assert any(line.startswith("M: last round not found") and "matches the expectation" in line for line in again)


def test_faithful_needs_every_earlier_fault_fixed() -> None:
    still = DesignerEval(s1_faithful=True, previous_regions=[
        PreviousRegionStatus(part_id="P2", fault="merged", status="still_wrong")])
    assert decide(still, 1, 3) == "s1_retry"
    fixed = DesignerEval(s1_faithful=True, previous_regions=[
        PreviousRegionStatus(part_id="P2", fault="merged", status="fixed")])
    assert decide(fixed, 1, 3) == "s1_pass"


def _run(tmp_path: Path, scenario: str) -> Path:
    problem = Problem(title="Test device", statement="Design a test device.", constraints=[], criteria=[],
                      attachments=[])
    return Controller(FakeClient(scenario=scenario)).run(problem, base=tmp_path / "runs").run_dir


def test_round_that_fixes_nothing_is_reverted_and_logged(tmp_path: Path) -> None:
    run_dir = _run(tmp_path, "s1_three_fail")
    trace = (run_dir / "trace.md").read_text()
    assert "round 0" in trace and "kept (first round)" in trace
    assert "round 1" in trace and "reverted (fixed no earlier fault)" in trace
    use0 = json.loads(next(run_dir.glob("stage_b/attempt_00/round_00/sam_use.json")).read_text())
    assert "outcome_next_round" in use0 and (run_dir / "stage_b/attempt_00/part_map.json").exists()
    assert json.loads(next(run_dir.glob("stage_b/attempt_00/round_00/sam.json")).read_text())["parts"]


def test_happy_run_labels_come_from_sam_boxes(tmp_path: Path) -> None:
    run_dir = _run(tmp_path, "happy")
    loc = json.loads(next(run_dir.glob("stage_b/attempt_00/round_00/localization.json")).read_text())
    assert any(p["found"] for p in loc["parts"])
    assert (run_dir / "final" / "figure.png").exists()


def test_design_flaw_counts_only_on_a_faithful_render_or_a_sketch_traced_region() -> None:
    from hs.schemas import EvalRegion

    render_only = EvalRegion(part_id="P6", observed="bare ice block", expected="tank", source="render")
    assert decide(DesignerEval(s1_faithful=False, s2_flaw=True, regions=[render_only]), 0, 3) == "s1_retry"
    assert decide(DesignerEval(s1_faithful=False, s2_flaw=True, regions=[render_only]), 2, 3) == "s1_exhausted"
    in_sketch = EvalRegion(part_id="P6", observed="no drain", expected="drain", source="schematic")
    assert decide(DesignerEval(s1_faithful=False, s2_flaw=True, regions=[in_sketch]), 0, 3) == "s2_return"
    assert decide(DesignerEval(s1_faithful=True, s2_flaw=True), 0, 3) == "s2_return"


def test_unaddressed_segmenter_findings_are_detected() -> None:
    from hs.schemas import Deviation
    from hs.stage_b.loop import _unaddressed

    ev = DesignerEval(s1_faithful=True, deviations=[
        Deviation(what="pv_array panel count", measured="14", expected="12", matters=False, why="")])
    diffs = {"pv_array": ["expected 12, found 14"], "dc_cooler": ["not found"]}
    assert _unaddressed(diffs, ev) == ["dc_cooler"]
