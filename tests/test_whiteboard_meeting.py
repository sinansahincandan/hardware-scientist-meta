from pathlib import Path

from hs.fake_client import FakeClient
from hs.master_prompt import MasterPrompt
from hs.schemas import Problem
from hs.stage_a.meeting import Meeting
from hs.stage_a.whiteboard import Whiteboard


def _meeting(tmp_path: Path, scenario: str = "happy") -> Meeting:
    client = FakeClient(run_dir=tmp_path, scenario=scenario)
    problem = Problem(title="T", statement="S", constraints=[], criteria=[], attachments=[])
    master = MasterPrompt.rev0(client, problem, "", tmp_path)
    return Meeting(client, master, tmp_path, 0)


def test_whiteboard_op_validation():
    board = Whiteboard()
    ok, msg = board.apply_op("Mechanics", {"action": "add_concept", "function_id": "F9", "text": "x"})
    assert not ok and "unknown function_id" in msg
    ok, _fid = board.apply_op("Mechanics", {"action": "add_function", "text": "Lift"})
    assert ok
    ok, msg = board.apply_op("Mechanics", {"action": "resolve_objection", "id": "O1"})
    assert not ok  # needs evidence ids or reason
    ok, msg = board.apply_op("Mechanics", {"action": "vote", "ready": True})
    assert not ok  # no proposal yet


def test_update_proposal_clears_votes():
    board = Whiteboard()
    board.apply_op("A", {"action": "add_function", "text": "F"})
    board.apply_op("A", {"action": "add_concept", "function_id": "F1", "text": "c"})
    board.apply_op("A", {"action": "update_proposal", "text": "p1", "concept_ids": ["C1"]})
    board.apply_op("A", {"action": "vote", "ready": True, "reason": "ok"})
    assert board.votes
    board.apply_op("A", {"action": "update_proposal", "text": "p2", "concept_ids": ["C1"]})
    assert board.votes == {}
    assert board.proposal is not None and board.proposal.version == 2


def test_meeting_consensus_cycle2(tmp_path):
    meeting = _meeting(tmp_path)
    result = meeting.run()
    assert result.closed_by == "consensus"
    assert result.cycles_used == 2
    assert result.board.proposal is not None
    assert result.board.evidence  # calc/simulate/sketch posted evidence
    tools_used = {e.tool for e in result.board.evidence}
    assert "calc" in tools_used
    calc_ev = next(e for e in result.board.evidence if e.tool == "calc")
    assert "N" in calc_ev.output_summary or "588" in calc_ev.output_summary or calc_ev.output_summary


def test_meeting_cap_flags_blocking(tmp_path):
    meeting = _meeting(tmp_path, scenario="cap")
    result = meeting.run()
    assert result.closed_by == "cap"
    assert result.board.closure.open_blocking


def test_evaluator_request_keeps_meeting_open_until_resolved(tmp_path):
    meeting = _meeting(tmp_path)
    meeting.pin_evaluator_requests(["Compute the worst-case load with units and cite it."], "feedback")
    result = meeting.run()
    assert result.closed_by == "consensus"
    resolved = [o for o in result.board.objections if o.author == "Evaluator"]
    assert resolved and all(o.status == "resolved" for o in resolved)
    assert resolved[0].evidence_ids
