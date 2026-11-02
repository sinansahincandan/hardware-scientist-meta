"""Round 4 P4: the whiteboard picture and the knowledge record."""
from __future__ import annotations

import json
from pathlib import Path

from hs.board_picture import _clause, _value, board_picture_html


def _board() -> dict:
    return {
        "functions": [{"id": "F1", "text": "Climb the step with the load, at walking pace"},
                      {"id": "F2", "text": "Hold the load safely"}],
        "concepts": [{"id": "C1", "function_id": "F1", "author": "Mechanics", "status": "favored",
                      "text": "assumed_constraint: Tri-star wheel cluster"}],
        "evidence": [{"id": "E1", "tool": "calc", "status": "ok", "purpose": "weight of the load",
                      "output_summary": "weight_n=588.6 mixed (see keys), other=1"}],
        "objections": [{"id": "O1", "author": "Ergonomics", "text": "does the brake hold?", "status": "open"}],
        "proposal": {"version": 2, "text": "Rubber track climber."},
        "votes": {"Mechanics": {"version": 2, "ready": True}, "Ergonomics": {"version": 1, "ready": False}},
    }


def test_board_picture_reads_only_the_board(tmp_path: Path) -> None:
    out = board_picture_html(_board(), tmp_path, tmp_path / "stage_a" / "iter_00", ["Mechanics", "Ergonomics"],
                             "Stair cart", 2, 4)
    assert "cycle 2 / 4" in out and "Proposal v2" in out
    assert "Tri-star wheel cluster" in out and "assumed_constraint" not in out  # tag stripped
    assert "no concept pinned here" in out  # F2 has no note, said plainly
    assert "weight n = 589" in out and "E1" in out
    assert "does the brake hold?" in out and "(open)" in out
    assert "Mechanics ✓" in out and "Ergonomics …" in out  # vote on an older version is not a tick


def test_heading_never_ends_on_a_small_word() -> None:
    assert _clause("Dissipate first vertical mode energy at 1.9 Hz") == "Dissipate first vertical mode energy"
    assert _value("tmd_mass_kg=800.0 mixed (see keys), f=1") == "tmd mass kg = 800; f = 1"


def test_knowledge_in_recorded(tmp_path: Path, monkeypatch) -> None:
    from hs.controller import _record_knowledge_in

    base = tmp_path / "knowledge"
    (base / "insights").mkdir(parents=True)
    (base / "insights" / "run_a.md").write_text("# x\n", encoding="utf-8")
    (base / "tools").mkdir()
    (base / "tools" / "t.json").write_text(json.dumps({"name": "t", "source_run": "run_a"}), encoding="utf-8")
    monkeypatch.setenv("HS_KNOWLEDGE_DIR", str(base))
    _record_knowledge_in(tmp_path, "# Lessons\n- L1: a [d]\n- L2: b [d]\n")
    rec = json.loads((tmp_path / "knowledge_in.json").read_text(encoding="utf-8"))
    assert rec == {"lessons": ["L1", "L2"], "insight_runs": ["run_a"], "tools": {"t": "run_a"}}


def test_critic_listing_a_part_fault_is_not_a_pass() -> None:
    from hs.schemas import DesignerEval
    from hs.stage_b.designer_eval import decide

    base = {"pixel_description": "x", "s1_faithful": True, "s2_flaw": False}
    floating = {"box": [0, 0, 1, 1], "part_id": "cluster", "observed": "third cluster floating",
                "expected": "two clusters", "source": "render"}
    callout = {**floating, "part_id": "callout"}
    assert decide(DesignerEval.model_validate({**base, "regions": [floating]}), 0, 3) == "s1_retry"
    assert decide(DesignerEval.model_validate({**base, "regions": [callout]}), 0, 3) == "s1_pass"


def test_sam_tries_the_head_noun_when_the_phrase_misses(tmp_path: Path) -> None:
    from PIL import Image

    from hs.schemas import PartMap
    from hs.stage_b import part_map as pm

    img = tmp_path / "r.png"
    Image.new("RGB", (100, 100), "white").save(img)

    class C:
        def __init__(self) -> None:
            self.asked: list[str] = []

        def structured(self, role, cls, *args, **kwargs):  # the judge: nothing rejected
            return cls()

        def sam_segment(self, phrase: str, _png: Path, metadata=None) -> str:
            self.asked.append(phrase)
            return "" if phrase == "metal frame" else "<|box;x1=10;y1=10;x2=50;y2=50;w=100;h=100|>"

    pmap = PartMap.model_validate({"parts": [{"part_id": "spine", "visual_phrase": "metal frame",
                                             "visible_count": 1}]})
    c = C()
    with_boxes = pm.measure(c, img, pmap)
    assert c.asked == ["metal frame", "frame"]
    assert with_boxes["parts"]["spine"]["phrase"] == "frame"


def test_concept_sketch_rewords_once_after_a_content_filter_block(tmp_path: Path) -> None:
    from PIL import Image
    from test_stage_b_controller import _solution

    from hs.fake_client import FakeClient
    from hs.stage_b import loop
    from hs.stage_b.schematic import build_spec_from_solution

    fake = FakeClient(run_dir=tmp_path)
    sol = _solution()
    spec = build_spec_from_solution(sol)
    sketch = tmp_path / "sketch_1.png"
    Image.new("RGB", (64, 64), "white").save(sketch)
    prompts: list[str] = []
    real_edit = fake.image_edit

    def edit(prompt: str, ref: Path, size: str = "1024x1024", extra_refs=None) -> bytes:
        prompts.append(prompt)
        if len(prompts) == 1:
            raise RuntimeError("Error code: 400 - triggering our content management policy.")
        return real_edit(prompt, ref, size, extra_refs=extra_refs)

    fake.image_edit = edit  # type: ignore[method-assign]
    logs: list[str] = []
    loop.concept_sketch(fake, sol, spec, tmp_path, [sketch], logs.append)
    assert len(prompts) == 2 and prompts[1].startswith("Redraw the engineers' hand sketches")
    assert any("re-worded" in line for line in logs)
