"""OpenClient (open-weights backend): chain kept client-side, local search reported in Meta's shape.

A fake Baseten SDK stands in for the real one; the shapes match the probe (runs/open_probe/)."""
from types import SimpleNamespace as NS

import pytest

from hs import open_client
from hs.client import _output_text, search_sources
from hs.open_client import OpenClient


def _usage(i=100, o=50, cached=0):
    return NS(input_tokens=i, output_tokens=o, input_tokens_details=NS(cached_tokens=cached),
              output_tokens_details=NS(reasoning_tokens=10))


def _msg(text):
    return NS(type="message", content=[NS(type="output_text", text=text, annotations=[])])


def _fc(name, args, cid):
    return NS(type="function_call", name=name, arguments=args, call_id=cid)


class _FakeSDK:
    """Replays scripted outputs and keeps every request it was sent."""

    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.sent = []
        self.responses = self

    def create(self, **kwargs):
        self.sent.append(kwargs)
        return NS(id="baseten_x", status="completed", output=self.outputs.pop(0), usage=_usage())


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("BASETEN_API_KEY", "test")
    monkeypatch.setattr(open_client, "web_search", lambda q: [
        {"url": "https://ntrs.nasa.gov/regolith.pdf", "title": "Lunar Geotechnical Guide", "snippet": "1.5 g/cm3"},
        {"url": "https://example.org/other", "title": "Other", "snippet": "x"}])
    monkeypatch.setattr(open_client, "open_page", lambda url, find="": f"page {url} about {find}: 1.50 g/cm3")
    return OpenClient(run_dir=tmp_path)


def _use(client, outputs):
    sdk = _FakeSDK(outputs)
    client._open_sdk = sdk
    return sdk


def test_search_runs_locally_and_comes_back_in_meta_shape(client):
    sdk = _use(client, [
        [NS(type="reasoning"), _fc("web_search", '{"query": "lunar regolith bulk density"}', "s1")],
        [_fc("open_page", '{"url": "https://ntrs.nasa.gov/regolith.pdf", "find": "bulk density"}', "s2")],
        [_msg("Regolith packs to about 1.5 g/cm3 near the surface https://ntrs.nasa.gov/regolith.pdf. Next point.")],
    ])
    resp = client.responses(role="member", instructions="be careful", tools=[
        {"type": "web_search", "search_context_size": "medium"}],
        input_items=[{"type": "message", "role": "user", "content": [{"type": "input_text", "text": "go"}]}])
    # three billed calls, no hosted web_search sent, the two local tools offered instead
    assert len(sdk.sent) == 3
    assert all(t.get("type") == "function" for t in sdk.sent[0]["tools"])
    assert {t["name"] for t in sdk.sent[0]["tools"]} == {"web_search", "open_page"}
    assert sdk.sent[0]["reasoning"] == {"effort": "medium"}
    # the second call carries the search call and its result; reasoning is not resent
    second = sdk.sent[1]["input"]
    assert [i.get("type") for i in second] == ["message", "function_call", "function_call_output"]
    assert "Lunar Geotechnical Guide" in second[-1]["output"]
    # what the board sees: Meta-style search items and a citation span on the sentence
    kinds = [i.type for i in resp.output]
    assert kinds == ["web_search_call", "web_search_call", "message"]
    sources = search_sources(resp)
    cited = next(s for s in sources if s["url"] == "https://ntrs.nasa.gov/regolith.pdf")
    assert cited["cited"] and cited["read"] and cited["query"] == "lunar regolith bulk density"
    assert cited["snippet"].startswith("Regolith packs to about 1.5 g/cm3")
    other = next(s for s in sources if s["url"] == "https://example.org/other")
    assert not other["cited"] and other["snippet"] == ""
    assert _output_text(resp).startswith("Regolith packs")
    assert len(client.cost.entries) == 3


def test_previous_response_id_is_kept_client_side(client):
    sdk = _use(client, [
        [_msg("posting a concept"), _fc("whiteboard", '{"action": "add_concept"}', "w1")],
        [_msg("done")],
    ])
    first = client.responses(role="member", instructions="i", tools=[{"type": "function", "name": "whiteboard",
                             "parameters": {"type": "object", "properties": {}}}],
                             input_items=[{"type": "message", "role": "user",
                                           "content": [{"type": "input_text", "text": "turn"}]}])
    assert [i.type for i in first.output] == ["function_call", "message"] or \
        [i.type for i in first.output] == ["message", "function_call"]
    client.responses(role="member", instructions="i", previous_response_id=first.id,
                     input_items=[{"type": "function_call_output", "call_id": "w1", "output": "ok C3"}])
    sent = sdk.sent[1]
    assert "previous_response_id" not in sent
    assert [i.get("type") for i in sent["input"]] == ["message", "message", "function_call", "function_call_output"]
    assert sent["input"][1]["role"] == "assistant"


def test_unknown_previous_id_reads_as_expired_chain(client):
    with pytest.raises(RuntimeError, match="not found or expired"):
        client.responses(role="member", instructions="i", previous_response_id="open_missing", input_items=[])


def test_search_budget_stops_offering_search(client, monkeypatch):
    from hs import config

    monkeypatch.setattr(config, "MAX_SEARCH_ACTIONS_PER_CALL", 2)
    sdk = _use(client, [
        [_fc("web_search", '{"query": "a"}', "a")],
        [_fc("web_search", '{"query": "b"}', "b")],
        [_msg("answer")],
    ])
    client.responses(role="prior_art", instructions="i", tools=[{"type": "web_search"}],
                     input_items=[{"type": "message", "role": "user", "content": [{"type": "input_text", "text": "q"}]}])
    assert "tools" not in sdk.sent[2]


def test_effort_map_covers_every_role():
    from hs import config

    assert all(rc.effort in config.OPEN_EFFORT for rc in config.ROLES.values())
    assert set(config.OPEN_EFFORT.values()) <= {"low", "medium", "high", "xhigh"}


def test_open_sam_json_reads_as_instances_in_render_pixels():
    import base64
    import io
    import json

    import numpy as np
    from PIL import Image

    from hs.stage_b.part_map import parse_instances, parse_masks

    crop = np.zeros((10, 20), dtype=np.uint8)
    crop[2:8, 5:15] = 255
    buf = io.BytesIO()
    Image.fromarray(crop).convert("1").save(buf, format="PNG")
    raw = json.dumps({"open_sam": True, "w": 100, "h": 50, "instances": [
        {"object_id": "3", "box": [10, 10, 30, 20], "conf": 0.91,
         "mask_png": base64.b64encode(buf.getvalue()).decode(), "mask_box": [10, 10, 30, 20]}]})
    insts = parse_instances(raw, 200, 100)  # render is twice the sent size
    assert len(insts) == 1 and insts[0]["object_id"] == "3" and insts[0]["conf"] == 0.91
    assert insts[0]["box"] == (20, 20, 60, 40)
    mask = parse_masks(raw, 200, 100)
    assert mask is not None and mask.shape == (100, 200)
    ys, xs = np.nonzero(mask)
    assert 28 <= xs.min() <= 32 and 48 <= xs.max() <= 52 and 22 <= ys.min() <= 26


def test_box_prompt_text_becomes_boxes_for_modal(client, tmp_path):
    from PIL import Image

    from hs.stage_b.part_map import _box_prompt

    text, ids = _box_prompt({"p1": (100, 200, 300, 400), "p3": (500, 500, 600, 700)}, 2048, 1024)
    calls = []

    class _Sam:
        class segment_boxes:
            @staticmethod
            def remote(png, boxes):
                calls.append(boxes)
                return {"w": 1024, "h": 512, "instances": [], "gpu_seconds": 0.1}

    client._sam = _Sam()
    img = tmp_path / "r.png"
    Image.new("RGB", (2048, 1024)).save(img)
    client.sam_segment(text, img)
    assert [b["object_id"] for b in calls[0]] == ["1", "2"] and ids == {"1": "p1", "2": "p3"}
    assert calls[0][0]["box"] == [102, 102, 307, 205]
    assert client.cost.entries[-1]["model"] == "sam-3-open@modal"
