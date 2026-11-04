"""Round 3 A4/A5/A6: no cutting of speech, consensus after the Manager, closure facts to the Evaluator."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from hs.client import BudgetExceeded
from hs.master_prompt import MasterPrompt
from hs.schemas import Verdict
from hs.stage_a import council
from hs.stage_a.meeting import Meeting


class _Client:
    is_fake = False

    def __init__(self, reply: str = "", raise_budget: bool = False) -> None:
        self.reply, self.raise_budget, self.calls = reply, raise_budget, 0

    def free_text(self, *a: Any, **k: Any) -> tuple[str, list[Any]]:
        self.calls += 1
        if self.raise_budget:
            raise BudgetExceeded("cost cap $15.00 would be exceeded")
        return self.reply, []


def _meeting(tmp_path: Path, client: Any) -> Meeting:
    master = MasterPrompt(tmp_path, "t", [("## 2. Roles", "### A\nmechanics")])
    return Meeting(client, master, tmp_path, 0)


def test_long_turn_is_kept_whole_with_no_extra_call(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Owner 2026-11-03: no word limit; members are asked to write compactly and speech is never cut or re-asked."""
    monkeypatch.setattr(council, "run_member_turn", lambda *a, **k: "word " * 1500)
    client = _Client()
    meeting = _meeting(tmp_path, client)
    meeting._run_real_turn("A", ["A"], 1)
    assert client.calls == 0 and len(meeting.transcript[-1]["message"].split()) == 1500


def test_consensus_is_rechecked_after_the_managers_turn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from hs.fake_client import FakeClient
    from hs.master_prompt import MasterPrompt as MP

    client = FakeClient(run_dir=tmp_path)
    master = MP.rev0(client, SimpleNamespace(title="t", statement="s", constraints=[], criteria=[],
                                             attachments=[], model_dump=lambda: {"title": "t"}), "", tmp_path)
    meeting = Meeting(client, master, tmp_path, 0, min_cycles=2, max_cycles=3)
    original = Meeting._run_manager_turn

    def manager_objects_in_cycle_2(self: Meeting, roster: list[str], cycle: int, **kw) -> None:
        original(self, roster, cycle, **kw)
        if cycle == 2 and not kw:
            self.board.apply_op("Manager", {"action": "raise_objection", "target_id": "proposal",
                                            "text": "The critical load was never computed.", "blocking": True})

    monkeypatch.setattr(Meeting, "_run_manager_turn", manager_objects_in_cycle_2)
    result = meeting.run()
    # Without the objection this fake meeting closes in cycle 3 (opinions follow the chief's cycle-2 proposal);
    # with it, it must not close while the objection is open.
    assert result.cycles_used >= 3
    assert not (result.closed_by in ("consensus", "chief") and result.board.closure.open_blocking)


def test_manager_turn_cannot_vote(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from hs.stage_a.tools import ToolRunner
    from hs.stage_a.whiteboard import Whiteboard

    board = Whiteboard()
    board.apply_op("A", {"action": "add_function", "text": "carry the load"})
    board.apply_op("A", {"action": "add_concept", "function_id": "F1", "text": "frame"})
    board.apply_op("A", {"action": "update_proposal", "text": "frame", "concept_ids": ["C1"]})
    vote = SimpleNamespace(type="function_call", name="whiteboard", call_id="c1",
                           arguments='{"action": "vote", "ready": true, "reason": "fine"}')
    replies = iter([SimpleNamespace(id="r1", output=[vote]),
                    SimpleNamespace(id="r2", output=[SimpleNamespace(type="message", content=[
                        SimpleNamespace(type="output_text", text="Process note.", annotations=[])])])])
    seen_roles: list[str] = []

    class Client:
        def responses(self, **kwargs: Any) -> Any:
            seen_roles.append(kwargs["role"])
            return next(replies)

    master = MasterPrompt(tmp_path, "t", [("## 2. Roles", "### A\nx")])
    council.run_member_turn(Client(), master, "Manager", board, ToolRunner(board, tmp_path, tmp_path / "ev"),
                            [], 1, instructions_override="manager", role="manager",
                            allowed_actions={"raise_objection", "resolve_objection", "read_evidence"})
    assert "Manager" not in board.votes and seen_roles == ["manager", "manager"]


def test_evaluator_sees_closure_facts_and_no_code_rule_overrides_it(tmp_path: Path) -> None:
    from hs.stage_a.evaluator import Evaluator
    from hs.stage_a.whiteboard import Whiteboard

    board = Whiteboard()
    board.apply_op("A", {"action": "add_function", "text": "carry the load"})
    board.apply_op("A", {"action": "raise_objection", "target_id": "F1", "text": "wheel size unknown",
                         "blocking": True})
    board.closure.cycles_used = 4
    prompts: list[str] = []

    class Client:
        def free_text(self, *a: Any, **k: Any) -> tuple[str, list[Any]]:
            return "closest prior art", []

        def structured(self, role: str, model: Any, instructions: str, prompt: str, **k: Any) -> Any:
            prompts.append(prompt)
            return Verdict(feedback="Works; the wheel question is minor.", evidence_requests=[], accept=True)

    solution = SimpleNamespace(model_dump_json=lambda **k: "{}")
    master = SimpleNamespace(sections=[("## 1. Problem", "p"), ("## 5. Criteria", "c")])
    verdict = Evaluator(Client()).judge(master, solution, board, "cap", tmp_path)
    assert verdict.accept is True  # the Evaluator decided; no cap rule flipped it
    assert "No proposal was formed" in prompts[0] and "wheel size unknown" in prompts[0]
    assert "cycle cap without consensus" in prompts[0]


def test_search_results_in_the_final_response_become_citable_evidence(tmp_path: Path) -> None:
    """B8: a member's search posts one evidence item per result (even in the last response), and one
    extra chained request lets the member cite them by id."""
    from hs.stage_a.tools import ToolRunner
    from hs.stage_a.whiteboard import Whiteboard

    search = SimpleNamespace(type="web_search_call", action=SimpleNamespace(query="tri-star wheel diameter"),
                             results=[{"url": "https://example.org/sc3", "title": "SC3 stair climber 2021",
                                       "snippet": "Wheels of 150 mm diameter."}])
    first = SimpleNamespace(id="r1", output=[search, SimpleNamespace(type="message", content=[
        SimpleNamespace(type="output_text", text="Wheels are about 150 mm.", annotations=[])])])
    cite = SimpleNamespace(id="r2", output=[SimpleNamespace(type="message", content=[
        SimpleNamespace(type="output_text", text="The SC3 listing (E1) gives 150 mm wheels.", annotations=[])])])
    replies = iter([first, cite])
    sent: list[dict[str, Any]] = []

    class Client:
        def responses(self, **kwargs: Any) -> Any:
            sent.append(kwargs)
            return next(replies)

    board = Whiteboard()
    master = MasterPrompt(tmp_path, "t", [("## 2. Roles", "### A\nx")])
    text = council.run_member_turn(Client(), master, "A", board, ToolRunner(board, tmp_path, tmp_path / "ev"), [], 1)
    ev = board.evidence[0]
    assert ev.tool == "web_search" and ev.references[0]["url"] == "https://example.org/sc3"
    assert ev.references[0]["year"] == "2021" and "150 mm" in ev.output_full
    assert sent[0]["include"] == ["web_search_call.results"]
    assert sent[1]["previous_response_id"] == "r1" and "E1" in sent[1]["input_items"][0]["content"][0]["text"]
    assert text == "The SC3 listing (E1) gives 150 mm wheels."


def test_backward_chain_links_claim_evidence_turn_and_section(tmp_path: Path) -> None:
    """B13: claim -> evidence -> member turn -> master prompt section, plus process facts."""
    from hs.schemas import KeyEstimate
    from hs.stage_a.manager import backward_chain
    from hs.stage_a.meeting import MeetingResult
    from hs.stage_a.whiteboard import Whiteboard

    board = Whiteboard()
    board.add_evidence("Mechanics", "calc", "wheel load", "Q_(30,'kg')*9.81", "294 newton", cycle=2)
    board.apply_op("Thermal", {"action": "add_function", "text": "climb"})
    board.apply_op("Thermal", {"action": "raise_objection", "target_id": "F1", "text": "edge impact unchecked",
                               "blocking": True})
    room = MeetingResult(board=board, transcript=[{"cycle": 2, "member": "Mechanics",
                                                   "message": "The wheel load is 294 N. More text."}],
                         cycles_used=4, closed_by="cap")
    solution = SimpleNamespace(key_estimates=[KeyEstimate(quantity="wheel load", value=294, unit="N",
                                                          method="calc", evidence_ids=["E1"])])
    master = MasterPrompt(tmp_path, "t", [("## 2. Roles", "### Mechanics\nx\n### Thermal\ny")])
    chain = backward_chain(room, solution, master)
    assert "Claim: wheel load = 294 N" in chain and "E1 (calc by Mechanics, cycle 2)" in chain
    assert "The wheel load is 294 N." in chain and "## 2. Roles / ### Mechanics" in chain
    assert "Open objection O1 by Thermal (blocking)" in chain
    assert "closed by cap after 4 cycles; no proposal formed" in chain


def test_search_evidence_is_capped_per_query_and_deduplicated(tmp_path: Path) -> None:
    from hs.stage_a.tools import ToolRunner
    from hs.stage_a.whiteboard import Whiteboard

    board = Whiteboard()
    runner = ToolRunner(board, tmp_path, tmp_path / "ev")
    sources = [{"url": f"https://ex.org/{i}", "title": f"t{i}", "query": "q"} for i in range(6)]
    assert len(runner.web_search_evidence("A", sources)) == 2  # uncited results: two per query
    assert runner.web_search_evidence("B", sources[:2] + [{"url": "https://ex.org/new", "title": "n", "query": "r"}]) == ["E3"]


def test_cited_source_keeps_the_members_sentence_and_read_status(tmp_path: Path) -> None:
    from types import SimpleNamespace as NS

    from hs.client import search_sources
    from hs.stage_a.tools import ToolRunner
    from hs.stage_a.whiteboard import Whiteboard

    text = "BP-1 bulk density is about 1.6 g/cm3 loose. Other text."
    resp = NS(output=[
        NS(type="web_search_call", action=NS(type="search", query="bp-1 density"),
           results=[{"url": "https://a.org/p.pdf", "title": "BP-1 study", "snippet": ""},
                    {"url": "https://b.org", "title": "other", "snippet": ""}]),
        NS(type="web_search_call", action=NS(type="open_page", url="https://a.org/p.pdf"), results=[]),
        NS(type="message", content=[NS(type="output_text", text=text, annotations=[
            NS(type="url_citation", url="https://a.org/p.pdf", title="BP-1 study", start_index=0, end_index=43)])])])
    src = search_sources(resp)
    assert src[0]["url"] == "https://a.org/p.pdf" and src[0]["cited"] and src[0]["read"]
    assert src[0]["snippet"] == "BP-1 bulk density is about 1.6 g/cm3 loose."
    board = Whiteboard()
    ids = ToolRunner(board, tmp_path, tmp_path / "ev").web_search_evidence("Mara - Mobility", src)
    first = next(e for e in board.evidence if e.id == ids[0])
    assert "took from it: BP-1 bulk density" in first.output_full and "opened and read" in first.output_full
    assert "not opened or cited" in next(e for e in board.evidence if e.id == ids[1]).output_full


def test_evaluator_sees_not_ready_votes_with_reasons(tmp_path: Path) -> None:
    from hs.stage_a.evaluator import Evaluator
    from hs.stage_a.whiteboard import Whiteboard

    board = Whiteboard()
    board.apply_op("A", {"action": "add_function", "text": "cool"})
    board.apply_op("A", {"action": "add_concept", "function_id": "F1", "text": "box"})
    board.apply_op("A", {"action": "update_proposal", "text": "box", "concept_ids": ["C1"]})
    board.apply_op("A", {"action": "vote", "ready": True, "reason": "fine"})
    board.apply_op("B", {"action": "vote", "ready": False, "reason": "no cloudy-day rule"})
    prompts: list[str] = []

    class Client:
        def free_text(self, *a: Any, **k: Any) -> tuple[str, list[Any]]:
            return "p", []

        def structured(self, role: str, model: Any, instructions: str, prompt: str, **k: Any) -> Any:
            prompts.append(prompt)
            return Verdict(feedback="ok", evidence_requests=[], accept=True)

    Evaluator(Client()).judge(SimpleNamespace(sections=[]), SimpleNamespace(model_dump_json=lambda **k: "{}"),
                              board, "cap", tmp_path)
    assert "B: NOT ready (no cloudy-day rule)" in prompts[0] and "A: ready (fine)" in prompts[0]


def test_what_a_speaker_said_about_a_source_is_kept_on_it(tmp_path: Path) -> None:
    from hs.stage_a.tools import ToolRunner
    from hs.stage_a.whiteboard import Whiteboard

    board = Whiteboard()
    runner = ToolRunner(board, tmp_path, tmp_path / "ev")
    [eid] = runner.web_search_evidence("Mara", [{"url": "https://a.org/x", "title": "Fingertip size", "query": "q"}])
    runner.note_citations("Theo", f"Adult index tips are about 17 mm wide ({eid}). Unrelated sentence.")
    ev = next(e for e in board.evidence if e.id == eid)
    assert ev.references[0]["cited"] and ev.references[0]["passage"].startswith("Adult index tips")
    assert "Theo said about it: Adult index tips are about 17 mm wide" in ev.output_full
    runner.note_citations("Theo", f"Adult index tips are about 17 mm wide ({eid}).")  # same sentence: not twice
    assert ev.output_full.count("Theo said about it") == 1
