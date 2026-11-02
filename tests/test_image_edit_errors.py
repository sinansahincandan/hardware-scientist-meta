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


class _StatusError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status


def test_content_filter_400_is_reworded_once_then_raised() -> None:
    """Owner decision 2026-11-02: a blocked request is retried once without numbers, not resent as is."""
    client = MetaClient.__new__(MetaClient)
    client.cost = MagicMock()
    attempts = []

    class _Sdk:
        class responses:
            @staticmethod
            def create(**kw):
                attempts.append(1)
                if len(attempts) < 3:
                    raise _StatusError(400, "The response was filtered due to the prompt "
                                            "triggering our content management policy.")
                return "ok"

    client._sdk = _Sdk()
    client._client = lambda: _Sdk  # type: ignore[method-assign]
    import hs.client as hc

    with patch.object(hc.time, "sleep", lambda s: None), pytest.raises(_StatusError):
        client._create_with_retries({})
    assert len(attempts) == 2


def test_plain_400_still_raises() -> None:
    client = MetaClient.__new__(MetaClient)

    class _Sdk:
        class responses:
            @staticmethod
            def create(**kw):
                raise _StatusError(400, "invalid parameter: demo")

    client._sdk = _Sdk()
    client._client = lambda: _Sdk  # type: ignore[method-assign]
    with pytest.raises(_StatusError, match="invalid parameter"):
        client._create_with_retries({})


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
