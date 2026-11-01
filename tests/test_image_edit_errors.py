"""HTTP 400 from the image endpoint must surface its body, unretried."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hs.client import MetaClient


def _client(tmp_path: Path) -> MetaClient:
    client = MetaClient.__new__(MetaClient)
    client.cost = MagicMock()
    client.cost.check_budget = lambda **kw: None
    return client


class _Block:
    type = "output_text"

    def __init__(self, text: str) -> None:
        self.text = text


class _Item:
    type = "message"

    def __init__(self, text: str) -> None:
        self.content = [_Block(text)]


class _Resp:
    def __init__(self, text: str) -> None:
        self.output = [_Item(text)]


def test_structured_reasks_once_on_empty_output() -> None:
    from pydantic import BaseModel

    class Out(BaseModel):
        x: int

    client = MetaClient.__new__(MetaClient)
    replies = iter([_Resp(""), _Resp('{"x": 3}')])
    client.responses = lambda **kw: next(replies)  # type: ignore[method-assign]
    assert client.structured("r", Out, "i", "u").x == 3


def test_image_edit_400_raises_with_body(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_API_KEY", "test-key-not-real")
    ref = tmp_path / "ref.png"
    ref.write_bytes(b"\x89PNG")
    resp = MagicMock(status_code=400, text='{"error": {"message": "prompt rejected: demo"}}',
                     headers={})
    calls = []

    def fake_post(*a, **kw):
        calls.append(1)
        return resp

    with patch("requests.post", fake_post), pytest.raises(RuntimeError, match="prompt rejected: demo"):
        _client(tmp_path).image_edit("draw it", ref)
    assert len(calls) == 1  # deterministic 400 is not retried
