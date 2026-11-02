"""Regression: expired previous_response_id chain restarts the turn fresh.

Observed on a real run (2026-10-31): HTTP 400 "referenced response not
found or expired" mid-turn killed the meeting. Board state is code-side,
so the turn must restart as a fresh chain from the current board.
"""
from types import SimpleNamespace

from hs.master_prompt import MasterPrompt
from hs.stage_a.council import run_member_turn
from hs.stage_a.tools import ToolRunner
from hs.stage_a.whiteboard import Whiteboard


class _StubClient:
    def __init__(self):
        self.calls = 0

    def responses(self, **kwargs):
        self.calls += 1
        if kwargs.get("previous_response_id") is not None:
            raise RuntimeError("Error code: 400 - referenced response not found or expired")
        if self.calls == 1:
            msg = SimpleNamespace(type="message", content=[
                SimpleNamespace(type="output_text", text="working on it")])
            call = SimpleNamespace(type="function_call", name="calc",
                                   arguments='{"expression": "60*9.81", "purpose": "load"}',
                                   call_id="c1")
            return SimpleNamespace(id="resp_1", output=[msg, call])
        msg = SimpleNamespace(type="message", content=[
            SimpleNamespace(type="output_text", text="Final message after restart.")])
        return SimpleNamespace(id="resp_2", output=[msg])


def test_whiteboard_schema_declares_all_fields():
    from hs.stage_a.tools import TOOL_SCHEMAS

    wb = next(t for t in TOOL_SCHEMAS if t.get("name") == "whiteboard")
    props = wb["parameters"]["properties"]
    for field in ("function_id", "text", "target_id", "blocking", "evidence_ids", "ready", "reason"):
        assert field in props, field


def test_unwrap_packed_action_args():
    from hs.stage_a.council import _unwrap_args

    out = _unwrap_args({"action": '{"text": "Move the load", "type": "add_function"}'})
    assert out["action"] == "add_function" and out["text"] == "Move the load"


def test_optimizer_heading_normalized(tmp_path):
    from hs.master_prompt import MasterPrompt
    from hs.schemas import MasterPromptRewrite, RewriteSection

    master = MasterPrompt(tmp_path, "T", [
        ("## 1. Problem", "{}"), ("## 2. Roles", "### A\nx\n### B\ny\n### C\nz"),
        ("## 3. Tools", "t"), ("## 4. Meeting protocol", "old protocol text here"),
        ("## 5. Criteria", ("- The concept must work physically (no violated conservation law, load path, or signal path).\n"
                             "- The concept must be buildable with purchasable parts and ordinary lab/shop methods.")),
        ("## 6. Lessons applied", "l")], rev=0)
    proposed, dropped = master.propose(MasterPromptRewrite(
        sections=[RewriteSection(heading="Meeting protocol", new_text="new protocol: vote only with evidence")],
        change_note="test"))
    report = master.commit(proposed, "test")
    assert report["changed"] == ["## 4. Meeting protocol"] and dropped == []
    assert "vote only with evidence" in dict(master.sections)["## 4. Meeting protocol"]


def test_expired_chain_restarts_turn(tmp_path):
    master = MasterPrompt(tmp_path, "T", [
        ("## 1. Problem", "{}"), ("## 2. Roles", "### Mechanics\ndomain"),
        ("## 3. Tools", "tools"), ("## 4. Meeting protocol", "protocol"),
        ("## 5. Criteria", "criteria"), ("## 6. Lessons applied", "lessons")], rev=0)
    board = Whiteboard()
    tools = ToolRunner(board, tmp_path, tmp_path / "evidence")
    text = run_member_turn(_StubClient(), master, "Mechanics", board, tools, [], cycle=1)
    assert text == "Final message after restart."
    assert board.evidence and board.evidence[0].output_summary  # calc evidence survived the restart
