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
    # The chief designer writes the proposal at the end of cycle 2; members' opinions on it come in cycle 3.
    assert result.closed_by in ("consensus", "chief")
    assert result.cycles_used == 3
    assert result.board.proposal is not None and result.board.proposal.author == "Manager"
    assert {x.function_id for x in result.board.selections} == {f.id for f in result.board.functions}
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
    assert result.closed_by in ("consensus", "chief")
    resolved = [o for o in result.board.objections if o.author == "Evaluator"]
    assert resolved and all(o.status == "resolved" for o in resolved)
    assert resolved[0].evidence_ids


def test_members_advise_and_only_the_chief_writes_and_closes() -> None:
    from hs.stage_a.whiteboard import Whiteboard

    b = Whiteboard(roster=["A", "B"])
    assert b.apply_op("Manager", {"action": "add_function", "text": "lift soil", "flows": "in: power; out: soil"})[0]
    assert b.apply_op("Manager", {"action": "add_function", "text": "carry soil"})[0]
    assert b.apply_op("A", {"action": "add_concept", "function_id": "F1", "text": "bucket ladder"})[0]
    assert b.apply_op("B", {"action": "add_concept", "function_id": "F1", "text": "drum"})[0]
    ok, msg = b.apply_op("A", {"action": "update_proposal", "text": "x"})
    assert not ok and "chief designer" in msg
    assert not b.apply_op("A", {"action": "select_concept", "function_id": "F1", "concept_id": "C1",
                                "rationale": "r"})[0]
    assert b.apply_op("Manager", {"action": "select_concept", "function_id": "F1", "concept_id": "C1",
                                  "rationale": "ladder beats drum on continuous lift (E3); same on mass"})[0]
    ok, msg = b.apply_op("Manager", {"action": "update_proposal", "text": "x"})
    assert not ok and "F2" in msg  # every function needs a selection first
    assert b.apply_op("Manager", {"action": "select_concept", "function_id": "F2", "concept_id": "",
                                  "rationale": "the ladder's top bucket drops into the frame bin; no separate means"})[0]
    assert b.apply_op("Manager", {"action": "update_proposal", "text": "ladder rover"})[0]
    assert b.proposal.concept_ids == ["C1"]
    assert not b.apply_op("Manager", {"action": "close_meeting", "synthesis": "s"})[0]  # no opinions yet
    b.apply_op("A", {"action": "vote", "ready": True, "reason": "ok"})
    b.apply_op("B", {"action": "vote", "ready": False, "reason": "drum would dig faster"})
    assert b.apply_op("Manager", {"action": "close_meeting",
                                  "synthesis": "B's speed point is real but E3 shows the ladder lifts continuously"})[0]
    assert b.chief_closed() and not b.consensus_reached(["A", "B"])
    assert "concepts from: A, B" in b.render_markdown()


def test_board_tool_schema_declares_every_action_and_field_the_board_reads() -> None:
    """Round-2 benchmark bug: select_concept/close_meeting and their fields were missing from the schema the model
    sees, so the chief sent id/text and status 'selected' and never got a selection onto the board."""
    from hs.stage_a.meeting import MANAGER_ACTIONS, VOTE_ONLY_ACTIONS
    from hs.stage_a.tools import TOOL_SCHEMAS

    wb = next(t for t in TOOL_SCHEMAS if t.get("name") == "whiteboard")
    props = wb["parameters"]["properties"]
    assert MANAGER_ACTIONS | VOTE_ONLY_ACTIONS | {"add_concept", "update_proposal"} <= set(props["action"]["enum"])
    for field in ("function_id", "concept_id", "rationale", "synthesis", "flows", "ready", "reason", "key_claims"):
        assert field in props, field
        assert field in wb["description"] or field in ("ready", "reason", "key_claims"), field


def test_board_accepts_the_shapes_the_model_actually_sent() -> None:
    """Shapes copied from runs/20261103-10503*/stage_a/iter_00/whiteboard_history.jsonl."""
    from hs.stage_a.whiteboard import Whiteboard

    b = Whiteboard(problem_title="t", roster=["A", "B"])
    assert b.apply_op("Manager", {"action": "add_function", "text": "Convert wind to shaft power"})[0]
    assert b.apply_op("Manager", {"action": "add_function", "text": "Convert shaft power to current"})[0]
    # member names the function only in the text
    ok, msg = b.apply_op("A", {"action": "add_concept", "id": "C26", "text": "Plumbing analogy for F2: buffer cap"})
    assert ok and b.concepts[-1].function_id == "F2", msg
    assert b.apply_op("B", {"action": "add_concept", "function_id": "F1", "text": "3-blade rotor"})[0]
    # 'selected' is not a status; the error points to select_concept
    ok, msg = b.apply_op("Manager", {"action": "set_concept_status", "id": "C2", "status": "selected"})
    assert not ok and "select_concept" in msg
    # chief sends id/text instead of concept_id/rationale
    ok, msg = b.apply_op("Manager", {"action": "select_concept", "function_id": "F1", "id": "C2",
                                     "text": "C2 gives shaft power; better than none"})
    assert ok, msg
    ok, msg = b.apply_op("Manager", {"action": "select_concept", "concept_id": "C1", "rationale": "only buffer"})
    assert ok and {s.function_id for s in b.selections} == {"F1", "F2"}, msg
    assert b.apply_op("Manager", {"action": "update_proposal", "text": "rotor + cap",
                                  "key_claims": [{"text": "33 W at 11 m/s", "evidence_ids": ["E9"]},
                                                 {"claim": "brake stops", "evidence": ["E2"]}]})[0]
    assert [(c.claim, c.evidence_ids) for c in b.proposal.key_claims] == [("33 W at 11 m/s", ["E9"]),
                                                                          ("brake stops", ["E2"])]
    # 'False' as a string is not ready
    assert b.apply_op("A", {"action": "vote", "ready": "False", "reason": "brake unproven"})[0]
    assert b.votes["A"].ready is False


def test_callout_faults_do_not_block_a_faithful_pass() -> None:
    from hs.schemas import DesignerEval, PreviousRegionStatus
    from hs.stage_b.designer_eval import decide

    ev = DesignerEval.model_construct(
        s1_faithful=True, s2_flaw=False, regions=[],
        previous_regions=[PreviousRegionStatus(part_id="callout", fault="leader on the cup", status="still_wrong")])
    assert decide(ev, 0) == "s1_pass"


def test_chief_sees_problem_constraints_protocol_and_criteria() -> None:
    """The chief's turn once carried no problem text: it decided without the 60 kg / box limits."""
    from hs.stage_a.meeting import chief_context

    sections = [("## 1. Problem", '{"constraints": ["at most 60 kg"]}'), ("## 2. Roles", "### A\nx"),
                ("## 4. Meeting protocol", "Cycle 1: functions"), ("## 5. Criteria", "works"),
                ("## 6. Lessons applied", "L1")]
    text = chief_context(sections)
    assert "60 kg" in text and "Cycle 1: functions" in text and "works" in text and "L1" in text
    assert "### A" not in text


def test_rewrite_does_not_double_the_heading(tmp_path) -> None:
    from hs.master_prompt import MasterPrompt
    from hs.schemas import MasterPromptRewrite

    mp = MasterPrompt(tmp_path, "t", [("## 1. Problem", "p"), ("## 4. Meeting protocol", "Cycle 1: x")])
    rw = MasterPromptRewrite.model_construct(sections=[type("S", (), {
        "heading": "## 4. Meeting protocol", "new_text": "## 4. Meeting protocol\nCycle 1: y"})()])
    proposed, dropped = mp.propose(rw)
    assert proposed == {"## 4. Meeting protocol": "Cycle 1: y"} and not dropped
