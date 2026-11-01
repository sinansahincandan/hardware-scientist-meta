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


def test_schematic_aspect_controls_box_proportions(tmp_path) -> None:
    from hs.schemas import Layout, SchematicNode, SchematicSpec, SizeClass
    from hs.stage_b.schematic import render_schematic

    def node(nid: str, aspect: float) -> SchematicNode:
        return SchematicNode(id=nid, label=nid, size_class_mm=SizeClass(min=100, max=400),
                             layout=Layout(col=0, row=0), aspect=aspect)

    spec = SchematicSpec(nodes=[node("spring", 0.35)], critical_part_id="spring")
    geo = render_schematic(spec, tmp_path / "a")
    box = geo["boxes"]["spring"]
    assert box["y1"] - box["y0"] > box["x1"] - box["x0"]  # tall, not wide
    spec2 = SchematicSpec(nodes=[node("girder", 6.0)], critical_part_id="girder")
    geo2 = render_schematic(spec2, tmp_path / "b")
    box2 = geo2["boxes"]["girder"]
    assert box2["x1"] - box2["x0"] > box2["y1"] - box2["y0"]  # wide, not tall


def test_drop_conflicting_labels() -> None:
    from hs.stage_b.annotate import _drop_conflicting

    boxes = {
        "crates": (655.0, 355.0, 795.0, 495.0),   # grounded on the cabinet itself
        "cabinet": (650.0, 350.0, 800.0, 500.0),
        "drums": (100.0, 700.0, 200.0, 800.0),
    }
    assert _drop_conflicting(boxes) == {"crates"}
    # Genuine containment (small part inside a big chamber) is kept.
    nested = {"chamber": (0.0, 0.0, 900.0, 900.0), "evaporator": (300.0, 100.0, 500.0, 200.0)}
    assert _drop_conflicting(nested) == set()
    assert _drop_conflicting({"a": (0.0, 0.0, 10.0, 10.0), "b": (50.0, 50.0, 60.0, 60.0)}) == set()
