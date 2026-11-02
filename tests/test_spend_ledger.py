"""Cross-run spend ledger: checked before every real call, updated after it."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from hs import config
from hs.client import BudgetExceeded, CostLog, MetaClient, SpendLedger


def test_ledger_accumulates_and_persists(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "ledger.json"
    SpendLedger(path, cap_usd=1.0).add("member", "m", 0.25)
    ledger = SpendLedger(path, cap_usd=1.0)  # fresh object = another run
    ledger.add("evaluator", "m", 0.5)
    assert ledger.total() == pytest.approx(0.75)
    data = json.loads(path.read_text())
    assert data["calls"] == 2 and data["cap_usd"] == 1.0
    assert "total $0.7500 of $1.00" in capsys.readouterr().err


def test_ledger_blocks_call_that_would_cross_cap(tmp_path: Path) -> None:
    ledger = SpendLedger(tmp_path / "ledger.json", cap_usd=1.0)
    ledger.add("member", "m", 0.97)
    ledger.check(0.02)
    with pytest.raises(BudgetExceeded, match="total spend cap"):
        ledger.check(0.05)


def test_costlog_checks_ledger_even_when_run_cap_is_fine(tmp_path: Path) -> None:
    ledger = SpendLedger(tmp_path / "ledger.json", cap_usd=1.0)
    ledger.add("earlier_run", "m", 0.99)
    cost = CostLog(tmp_path / "run", max_cost=15.0, ledger=ledger)
    with pytest.raises(BudgetExceeded):
        cost.check_budget()


class _Usage:
    def __init__(self, inp: int, out: int) -> None:
        self.input_tokens = inp
        self.output_tokens = out
        self.input_tokens_details = None
        self.output_tokens_details = None


class _Item:
    def __init__(self, type_: str) -> None:
        self.type = type_
        self.content: list[Any] = []


class _Resp:
    def __init__(self, out_tokens: int, items: list[str], status: str = "completed") -> None:
        self.usage = _Usage(1000, out_tokens)
        self.output = [_Item(t) for t in items]
        self.status = status


def _client(tmp_path: Path, replies: list[Any]) -> MetaClient:
    client = MetaClient.__new__(MetaClient)
    client.cost = CostLog(tmp_path / "run", ledger=SpendLedger(tmp_path / "ledger.json", cap_usd=50.0))
    it = iter(replies)

    def create(**kwargs: Any) -> Any:
        reply = next(it)
        if isinstance(reply, Exception):
            raise reply
        return reply

    client._sdk = type("SDK", (), {"responses": type("R", (), {"create": staticmethod(create)})()})()
    return client


def test_truncated_reply_is_billed_and_searches_counted(tmp_path: Path) -> None:
    from pydantic import BaseModel

    class Out(BaseModel):
        x: int

    truncated = _Resp(4000, ["message"], status="incomplete")
    full = _Resp(10, ["web_search_call", "web_search_call", "message"])
    client = _client(tmp_path, [truncated, full])
    client.responses(role="prior_art", instructions="i", input_items=[], schema_model=Out)
    entries = json.loads((tmp_path / "ledger.json").read_text())["entries"]
    assert len(entries) == 2
    expected_first = 1000 * 1.25 / 1e6 + 4000 * 4.25 / 1e6
    assert entries[0]["usd"] == pytest.approx(expected_first, abs=1e-6)
    assert client.cost.entries[1]["searches"] == 2


class _StatusError(Exception):
    def __init__(self, status: int) -> None:
        super().__init__(f"HTTP {status}: Billing account issue")
        self.status_code = status


def test_billing_402_stops_as_budget_exceeded(tmp_path: Path) -> None:
    client = _client(tmp_path, [_StatusError(402)])
    with pytest.raises(BudgetExceeded, match="402"):
        client.responses(role="member", instructions="i", input_items=[])


def test_fake_client_never_touches_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from hs.fake_client import FakeClient

    path = tmp_path / "ledger.json"
    monkeypatch.setattr(config, "SPEND_LEDGER_PATH", path)
    FakeClient(run_dir=tmp_path / "run").free_text("member", "i", "u")
    assert not path.exists()
