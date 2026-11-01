"""v2: regions, source trace, local-edit composite assertion, gradient schemas."""
from PIL import Image

from hs.schemas import DesignerEval, EvalRegion, OutputGradient, VLMPromptGradient, make_strict_schema
from hs.stage_b.designer_eval import decide
from hs.stage_b.prompt_gradient import composite_region


def test_composite_keeps_outside_pixels(tmp_path):
    prev = Image.new("RGB", (200, 200), (10, 20, 30))
    prev.save(tmp_path / "prev.png")
    edited = Image.new("RGB", (200, 200), (200, 0, 0))
    edited.save(tmp_path / "edited.png")
    info = composite_region(tmp_path / "prev.png", tmp_path / "edited.png",
                            [250, 250, 750, 750], tmp_path / "out.png", margin_px=0, feather_px=0)
    assert info["outside_unchanged"] is True
    out = Image.open(tmp_path / "out.png")
    assert out.getpixel((10, 10)) == (10, 20, 30)  # outside box: previous render
    assert out.getpixel((100, 100)) == (200, 0, 0)  # inside box: edited


def test_source_trace_routes_schematic_region_to_s2():
    ev = DesignerEval(s1_faithful=False, regions=[
        EvalRegion(box=[0, 0, 100, 100], part_id="P1", observed="x", expected="y", source="schematic")])
    assert decide(ev, 0) == "s2_return"
    ev2 = DesignerEval(s1_faithful=False, regions=[
        EvalRegion(box=[0, 0, 100, 100], part_id="P1", observed="x", expected="y", source="render")])
    assert decide(ev2, 0) == "s1_retry"


def test_gradient_schemas_strict():
    for model in (OutputGradient, VLMPromptGradient):
        schema = make_strict_schema(model)
        assert schema["additionalProperties"] is False
