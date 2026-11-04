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
