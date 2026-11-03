"""Meeting: turns, cycles, closing rule, Secretary (spec §4.3). Council turn logic lives here."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hs import config
from hs.master_prompt import MasterPrompt, roster_of
from hs.schemas import (
    ConceptBody,
    Connection,
    FabricationStep,
    FigureSpec,
    KeyEstimate,
    Load,
    MeasurementStage,
    Part,
    Problem,
    SizeClass,
    SolutionPrompt,
)
from hs.stage_a.tools import ToolRunner
from hs.stage_a.whiteboard import HistoryLog, Whiteboard


@dataclass
class MeetingResult:
    board: Whiteboard
    transcript: list[dict[str, Any]]
    cycles_used: int
    closed_by: str
    stats: dict[str, dict[str, int]] = field(default_factory=dict)


VOTE_ONLY_ACTIONS = {"vote", "raise_objection", "read_evidence"}
MANAGER_ACTIONS = {"raise_objection", "resolve_objection", "read_evidence", "add_function", "set_concept_status",
                   "select_concept", "update_proposal", "close_meeting"}


def chief_context(sections: list[tuple[str, str]]) -> str:
    """The master-prompt sections the chief designer decides by: the problem with its constraints, the meeting
    protocol, the criteria and the process lessons (B12). These are the optimized sections, so a Manager rewrite
    after a rejection reaches the chief's next meeting (Fig. 1: master prompt -> council, Manager included)."""
    by = dict(sections)
    return "\n\n".join(f"{h}\n{by[h]}" for h in ("## 1. Problem", "## 4. Meeting protocol", "## 5. Criteria",
                                                   "## 6. Lessons applied") if by.get(h))

class Meeting:
    def __init__(self, client: Any, master: MasterPrompt, run_dir: Path, iteration: int,
                 min_cycles: int = config.MIN_CYCLES, max_cycles: int = config.MAX_CYCLES) -> None:
        self.client = client
        self.master = master
        self.run_dir = run_dir
        self.iteration = iteration
        self.min_cycles = max(1, min(min_cycles, max_cycles))
        self.max_cycles = max_cycles
        self.iter_dir = run_dir / "stage_a" / f"iter_{iteration:02d}"
        self.iter_dir.mkdir(parents=True, exist_ok=True)
        (self.iter_dir / "turns").mkdir(exist_ok=True)
        self.board = Whiteboard()
        self.history = HistoryLog(self.iter_dir / "whiteboard_history.jsonl")
        self.tools = ToolRunner(self.board, run_dir, self.iter_dir / "evidence")
        self.transcript: list[dict[str, Any]] = []

    # -- setup ---------------------------------------------------------------------
    def pin_inspirations(self, inspirations: list[dict[str, Any]]) -> None:
        self.board.inspirations = inspirations

    def pin_evaluator_requests(self, requests: list[str], feedback: str) -> None:
        self.board.pin_evaluator_requests(requests, feedback)

    # -- turns -----------------------------------------------------------------------
    def _apply_scripted_turn(self, member: str, roster: list[str], cycle: int) -> None:
        turn = self.client.scripted_turn(member, roster, cycle, self.board)
        new_evidence_ids: list[str] = []
        for tool_call in turn.get("tools", []):
            kind = tool_call["tool"]
            if kind == "vetted_calc":
                eid, _ = self.tools.vetted_calc(member, tool_call["name"], tool_call.get("args", {}),
                                                tool_call.get("input_sources"), tool_call["purpose"], cycle=cycle)
            elif kind == "calc":
                eid, _ = self.tools.calc(member, tool_call["expression"], tool_call["purpose"], cycle=cycle)
            elif kind == "simulate":
                eid, _ = self.tools.simulate(member, tool_call["script"], tool_call["purpose"], cycle=cycle)
            elif kind == "sketch":
                eid, _ = self.tools.sketch(member, tool_call["script"], tool_call["caption"], cycle=cycle)
            else:
                continue
            new_evidence_ids.append(eid)
            self.history.append({"cycle": cycle, "member": member, "kind": "evidence", "evidence_id": eid, "tool": kind})
        for op in turn.get("ops", []):
            if op.get("action") == "__resolve_first_eval__":
                target = next((o for o in self.board.objections if o.author == "Evaluator" and o.status == "open"), None)
                if target is not None:
                    real_op = {"action": "resolve_objection", "id": target.id,
                               "evidence_ids": new_evidence_ids[-1:] or [e.id for e in self.board.evidence[-1:]],
                               "resolution": "Computed the requested quantity; see cited evidence."}
                    ok, msg = self.board.apply_op(member, real_op)
                    self.history.append({"cycle": cycle, "member": member, "kind": "op", "op": real_op, "ok": ok, "msg": msg})
                continue
            ok, msg = self.board.apply_op(member, op)
            self.history.append({"cycle": cycle, "member": member, "kind": "op", "op": op, "ok": ok, "msg": msg})
        if turn.get("vote") is not None and self.board.proposal is not None:
            vote_op = {"action": "vote", "ready": turn["vote"]["ready"], "reason": turn["vote"]["reason"]}
            # In fake cap scenario an open Evaluator objection still allows voting; board rule decides.
            ok, msg = self.board.apply_op(member, vote_op)
            self.history.append({"cycle": cycle, "member": member, "kind": "op", "op": vote_op, "ok": ok, "msg": msg})
        self.transcript.append({"cycle": cycle, "member": member, "message": str(turn.get("message", ""))})

    def _turn(self, speaker: str, cycle: int, **kwargs: Any) -> str:
        """One real turn with the expired-chain whole-turn retry; history records are kept."""
        from hs.stage_a.council import run_member_turn

        records: list[dict[str, Any]] = []
        try:
            message = run_member_turn(self.client, self.master, speaker, self.board, self.tools,
                                      self.transcript, cycle, history=records, **kwargs)
        except Exception as exc:
            if "not found or expired" not in str(exc):
                raise
            # Last resort: one whole-turn retry from the current board state.
            message = run_member_turn(self.client, self.master, speaker, self.board, self.tools,
                                      self.transcript, cycle, history=records, **kwargs)
        for rec in records:
            self.history.append(rec)
        return message

    def _shorten_if_long(self, speaker: str, message: str, instructions: str, role: str, cycle: int) -> str:
        """A6: a turn over the word limit is re-asked once to shorten; speech is never cut by code."""
        limit = config.MAX_TURN_MESSAGE_WORDS
        words = len(message.split())
        if words <= limit:
            return message
        text, _ = self.client.free_text(
            role, instructions,
            f"Your message below has {words} words; the room's limit is {limit}. Rewrite it in at most "
            f"{limit} words. Keep every point, every deciding number with its unit and every evidence id; "
            f"drop repetition, not content. Reply with the message only.\n\nYOUR MESSAGE:\n{message}")
        shorter = text.strip()
        kept = shorter if shorter and len(shorter.split()) < words else message
        self.history.append({"cycle": cycle, "member": speaker, "kind": "shorten_reask", "words_before": words,
                             "words_after": len(kept.split())})
        return kept

    def _run_real_turn(self, member: str, roster: list[str], cycle: int, vote_only: bool = False) -> None:
        """Responses tool loop for one member turn (real client only; fake uses scripted turns)."""
        from hs.master_prompt import member_instructions
        from hs.stage_a.tools import TOOL_SCHEMAS

        if vote_only:
            message = self._turn(
                member, cycle, allowed_actions=VOTE_ONLY_ACTIONS,
                tool_schemas=[t for t in TOOL_SCHEMAS if t.get("name") == "whiteboard"],
                extra_instruction=("\nThis is the final vote-only round: the cycles are over. Read the current "
                                   "proposal, the open objections and the evidence, then vote on the proposal "
                                   "with your reason, or raise an objection. No other board actions."))
            vote = self.board.votes.get(member)
            if self.board.proposal is not None and (vote is None or vote.version != self.board.proposal.version):
                # an opinion written only in the message is not on the board, and the chief cannot close without it
                # (replay on run 105032: one member spoke without calling vote); ask once more
                self.history.append({"cycle": cycle, "member": member, "kind": "vote_reask"})
                self._turn(member, cycle, allowed_actions=VOTE_ONLY_ACTIONS,
                           tool_schemas=[t for t in TOOL_SCHEMAS if t.get("name") == "whiteboard"],
                           extra_instruction=("\nYour last message gave no readiness opinion on the board. Call the "
                                              "whiteboard tool now with action vote, ready true or false, and your "
                                              "reason in one or two sentences."))
        else:
            message = self._turn(member, cycle)
        message = self._shorten_if_long(member, message, member_instructions(self.master.sections, member),
                                        "member", cycle)
        self.transcript.append({"cycle": cycle, "member": member, "message": message})
        self.history.append({"cycle": cycle, "member": member, "kind": "turn_end"})

    def _fake_chief(self, cycle: int, opening: bool) -> str:
        """Fake mode: the chief designer's board actions, scripted (offline runs exercise the same board code)."""
        if opening:
            if not self.board.functions:
                self.board.apply_op("Manager", {"action": "add_function", "text": "Support and move the load",
                                                "flows": "in: load weight, operator force; out: load moved"})
                self.board.apply_op("Manager", {"action": "add_function", "text": "Sense state and keep the operator safe",
                                                "flows": "in: position signal; out: stop signal"})
            return "Chief designer: the function structure is on the board; every member posts a concept per function."
        if cycle >= 2:
            for f in self.board.functions:
                cid = next((c.id for c in self.board.concepts if c.function_id == f.id and c.status != "dropped"), "")
                self.board.apply_op("Manager", {"action": "select_concept", "function_id": f.id, "concept_id": cid,
                                                "rationale": "Best supported by the evidence on the board; the "
                                                             "alternatives are worse on load path and cost."
                                                if cid else "No separate means needed: covered by the frame."})
            if self.board.proposal is None:
                self.board.apply_op("Manager", {"action": "update_proposal",
                                                "text": "Integrated concept from the selected concept per function.",
                                                "key_claims": [{"claim": "Rated load force is supported",
                                                                "evidence_ids": []}]})
            self.board.apply_op("Manager", {"action": "close_meeting",
                                            "synthesis": "Every member's opinion is answered on the board; settled."})
        return "Chief designer: selections and the proposal are on the board."

    def _run_manager_turn(self, roster: list[str], cycle: int, opening: bool = False, closing: bool = False) -> None:
        """The Manager is the chief designer (owner decision 2026-11-03, docs/brainstorm/functional_council.md):
        opens the meeting with the function structure, selects a concept per function in prose, checks the
        interfaces, writes the proposal and decides when it is settled. Members advise. Never votes."""
        tag = "c0_Manager" if opening else (f"c{cycle}_Manager_final" if closing else f"c{cycle}_Manager")
        base, n = tag, 1
        while (self.iter_dir / "turns" / f"{tag}.json").exists():
            n += 1
            tag = f"{base}_{n}"
        if getattr(self.client, "is_fake", False):
            message = self._fake_chief(cycle, opening)
            self.transcript.append({"cycle": 0 if opening else cycle, "member": "Manager", "message": message})
            self.history.append({"cycle": 0 if opening else cycle, "member": "Manager", "kind": "turn_end"})
            (self.iter_dir / "turns" / f"{tag}.json").write_text(
                json.dumps({"cycle": cycle, "member": "Manager", "message": message}, indent=2), encoding="utf-8")
            return
        from hs.stage_a.council import SPEAKING_RULE

        role = (
            "You are the Manager of this council and its chief designer. The members are domain experts who "
            "advise you: they post concepts, evidence and objections, and give a readiness opinion with a reason. "
            "You decide the design. You do not invent concepts of your own: you select, combine and integrate the "
            "members' concepts, and when a function has no adequate concept you ask named members for more. "
            "Data outranks opinion: weigh each member's advice by the evidence behind it, and say so. ")
        selected = {x.function_id for x in self.board.selections}
        unselected = [f.id for f in self.board.functions if f.id not in selected]
        every_cycle = (
            "Check key results against everyday scales; sum the parts against each size and mass limit; reconcile "
            "two values for one quantity; go through open blocking objections and resolve those the evidence "
            "settles (cite it) or name who must settle them. Answer each readiness opinion. ")
        if opening:
            task = (
                "OPENING TURN, before the members speak. Read the problem and write its function structure on the "
                "whiteboard with add_function: 4 to 8 functions, each a verb and a noun that does not presuppose a "
                "solution ('lift the soil', not 'run the bucket ladder'), each with flows: what goes in and out "
                "(energy, material, signal). Cover the whole job the device must do, including every hand-over "
                "between functions. Then tell the members: every member posts, for every function, at least one "
                "concept from their field, or says in one line that their field has none. Do not post concepts.")
        elif closing:
            task = (
                "CLOSING TURN: the cycles are over. "
                + (f"Functions without a selection: {', '.join(unselected)} — select them now with select_concept. "
                   if unselected else "")
                + ("There is no proposal on the board: write it now with update_proposal(text, key_claims) — the "
                   "Evaluator judges the proposal you write. " if self.board.proposal is None else "")
                + "Read the members' readiness opinions. If the proposal is settled, "
                "close the meeting (close_meeting) with a synthesis that answers every member's opinion by name and "
                "says how you weighed it; if a blocking objection is still open or an opinion raises a problem the "
                "evidence has not settled, do not close: say what remains open. This is concept design: the meeting "
                "settles what calculation, simulation and sources can settle. A test that needs built hardware "
                "cannot be done here and is no reason to keep the meeting open; name it as a bench test in your "
                "synthesis.")
        elif cycle == 1:
            task = (
                f"END OF CYCLE 1 of {self.max_cycles}. Check that every function has concepts from at least two "
                "members; name the members who still owe one; name the two weakest functions, for which members "
                "should bring a distant analogy with a written mapping in cycle 2. Point out a critical quantity "
                "nobody computed. " + every_cycle)
        else:
            task = (
                f"END OF CYCLE {cycle} of {self.max_cycles}: select and integrate now. "
                + (f"Functions without a selection: {', '.join(unselected)}. " if unselected else "")
                + "For each function, call select_concept(function_id, concept_id, rationale) with a rationale "
                "that compares the chosen concept with each alternative for that function (better / same / worse on "
                "the criteria, with evidence ids); a function that needs no separate means gets an empty concept_id "
                "and the reason. Before you compose, check every interface between the selected concepts: what one "
                "hands to the next (material, energy, signal) must match, and a hand-over no part does is a missing "
                "function — add it. Then call update_proposal(text, key_claims) from your selections, each claim "
                "with its evidence ids. " + every_cycle
                + "When the proposal is settled — no blocking objection open, every member's opinion on the current "
                "version given and answered — close the meeting with close_meeting(synthesis); a test that needs built "
                "hardware is a bench test to name in the synthesis, not an open point. ")
        instructions = role + task + (
            " Keep short notes: end your message with one line 'Note on <member>: ...' for each member you "
            "observed. " + SPEAKING_RULE) + "\n\n" + chief_context(self.master.sections)
        message = self._turn("Manager", cycle, instructions_override=instructions, role="manager",
                             allowed_actions=MANAGER_ACTIONS)
        message = self._shorten_if_long("Manager", message, instructions, "manager", cycle)
        self.transcript.append({"cycle": 0 if opening else cycle, "member": "Manager", "message": message})
        self.history.append({"cycle": 0 if opening else cycle, "member": "Manager", "kind": "turn_end"})
        (self.iter_dir / "turns" / f"{tag}.json").write_text(
            json.dumps({"cycle": cycle, "member": "Manager", "message": message}, indent=2), encoding="utf-8")
        with (self.iter_dir / "manager_notes.md").open("a", encoding="utf-8") as fh:
            fh.write(f"\n## {'Opening' if opening else ('Closing' if closing else f'Cycle {cycle}')}\n{message}\n")

    def _closing_rounds(self, roster: list[str]) -> str:
        """After the cycles: members give readiness opinions on the proposal (vote-only round, spec §4.3), then the
        chief's closing turn. A closing turn that revises the proposal clears the opinions, so the revision gets one
        more round of opinions and one more closing turn; the loop then ends either way."""
        for _ in range(2):
            version = self.board.proposal.version if self.board.proposal else 0
            for member in roster:
                if getattr(self.client, "is_fake", False):
                    turn = self.client.scripted_turn(member, roster, self.max_cycles, self.board)
                    if turn.get("vote") is not None:
                        self.board.apply_op(member, {"action": "vote", "ready": turn["vote"]["ready"],
                                                     "reason": turn["vote"]["reason"]})
                else:
                    self._run_real_turn(member, roster, self.max_cycles, vote_only=True)
            if self.board.consensus_reached(roster):
                return "consensus"
            self._run_manager_turn(roster, self.max_cycles, closing=True)
            if self.board.chief_closed():
                return "chief"
            if self.board.proposal is None or self.board.proposal.version == version:
                break
        return "cap"

    # -- main loop ---------------------------------------------------------------------
    def run(self) -> MeetingResult:
        roster = roster_of(self.master.sections)
        stats: dict[str, dict[str, int]] = {m: {"evidence": 0, "objections_raised": 0,
                                                "votes": 0, "tool_errors": 0}
                                            for m in roster}
        closed_by = "cap"
        cycles_used = 0
        self.board.roster = list(roster)
        self._run_manager_turn(roster, 1, opening=True)  # the chief designer writes the function structure
        for cycle in range(1, self.max_cycles + 1):
            cycles_used = cycle
            # spec §4.3: cycle c starts with member (c-1) mod n
            order = roster[(cycle - 1) % len(roster):] + roster[: (cycle - 1) % len(roster)] if roster else []
            for member in order:
                if getattr(self.client, "is_fake", False):
                    self._apply_scripted_turn(member, roster, cycle)
                else:
                    self._run_real_turn(member, roster, cycle)
                (self.iter_dir / "turns" / f"c{cycle}_{member}.json").write_text(
                    json.dumps({"cycle": cycle, "member": member,
                                "message": self.transcript[-1]["message"] if self.transcript else ""}, indent=2),
                    encoding="utf-8")
                if cycle >= self.min_cycles and self.board.consensus_reached(roster):
                    break
            self._run_manager_turn(roster, cycle)
            # A4: closure is decided after the Manager's turn, so an objection it raised counts.
            if cycle >= self.min_cycles and self.board.chief_closed():
                closed_by = "chief"
                break
            if cycle >= self.min_cycles and self.board.consensus_reached(roster):
                closed_by = "consensus"
                break
        if closed_by == "cap" and self.board.roster and self.board.proposal is None:
            # the chief never wrote a proposal in the cycles: it selects and writes one now, so members can
            # give their opinions on it and the Evaluator judges a proposal, not loose concepts
            self._run_manager_turn(roster, self.max_cycles, closing=True)
        if closed_by == "cap" and self.board.proposal is not None:
            closed_by = self._closing_rounds(roster)
        open_blocking = [o.id for o in self.board.objections if o.blocking and o.status == "open"]
        self.board.closure.closed_by = closed_by
        self.board.closure.cycles_used = cycles_used
        self.board.closure.open_blocking = open_blocking
        for m in roster:
            stats[m]["evidence"] = sum(1 for e in self.board.evidence if e.author == m)
            stats[m]["objections_raised"] = sum(1 for o in self.board.objections if o.author == m)
            stats[m]["votes"] = 1 if m in self.board.votes else 0
            stats[m]["tool_errors"] = sum(1 for e in self.board.evidence if e.author == m and e.status == "error")
        self.board.save(self.iter_dir / "whiteboard.json")
        (self.iter_dir / "whiteboard.md").write_text(self.board.render_markdown(), encoding="utf-8")
        (self.iter_dir / "transcript.md").write_text(
            "\n\n".join(f"## Cycle {t['cycle']} — {t['member']}\n{t['message']}" for t in self.transcript),
            encoding="utf-8")
        (self.iter_dir / "closure.json").write_text(
            json.dumps(self.board.closure.model_dump(), indent=2), encoding="utf-8")
        return MeetingResult(board=self.board, transcript=list(self.transcript),
                             cycles_used=cycles_used, closed_by=closed_by, stats=stats)


class Secretary:
    def __init__(self, client: Any) -> None:
        self.client = client

    def synthesize(self, result: MeetingResult, problem: Problem, iter_dir: Path) -> SolutionPrompt:
        if getattr(self.client, "is_fake", False):
            self.client.record_fake("secretary")
            solution = self._from_board(result, problem)
        else:
            prompt = (
                "Synthesize the SolutionPrompt from the final whiteboard and transcript. "
                "Copy evidence ids into key_estimates where they exist. Add nothing not on the board. "
                "Also write: mechanism_sentence (one sentence stating the working principle in plain words a "
                "non-specialist can follow: no part ids, no product codes, units with a space, at most three "
                "significant figures); "
                "decisive_choices (EXACTLY 3, the choices that most determine whether this concept works, taken from the "
                "chief designer's selections on the whiteboard with the reason each beat its alternatives); "
                "open_question (EXACTLY 1, the most important unresolved question); "
                "fabrication_steps: 3 to 5 coarse stages of how the device is made, each in plain words a "
                "non-specialist can follow (for example 'Assemble the frame and mount the wheels'); mention a size or "
                "rating only where it helps to recognise the stage, and give no wiring details or process recipes — "
                "this is a concept figure, not build instructions; "
                "operating_sequence: 3 to 6 steps of how the device works, in the order they happen when it is "
                "used, each on the part that does it (part_id from the parts list) with a plain action of at most 8 "
                "words a non-specialist understands (for example 'digs loose soil', 'lifts the full bucket', 'tips "
                "soil into the bin'); include every hand-over between parts — if no part does a step, say so in "
                "open_questions; "
                "measurement_chain: the stages in the order the signal travels (the sensing element, then its "
                "conditioning, then the instrument or link, then the computer or operator that acts on it), each a real "
                "part of this concept named in plain words (never an id or a snake_case name); "
                "transfer_line formatted exactly as: <governing quantity>: A -> B -> C | Measured: D -> E "
                "where the governing quantity is the one that actually decides this design (Load, Heat, "
                "Energy, Fluid, Signal...), naming the real parts/sensor stages of this concept.\n\n"
                f"WHITEBOARD:\n{result.board.render_markdown()}\n\n"
                "TRANSCRIPT:\n" + "\n".join(f"{t['member']}: {t['message']}" for t in result.transcript)
            )
            solution = self.client.structured("secretary", SolutionPrompt,
                                              "You are the Secretary. Output only the structured solution.",
                                              prompt)
        # Deliverable summary (AUTOPILOT §7.4): at most 3 choices, and only what the Secretary wrote.
        solution.decisive_choices = (solution.decisive_choices or [])[:3]
        if not solution.open_question:
            solution.open_question = (solution.open_questions[0] if solution.open_questions
                                      else "No open question was recorded by the council.")
        if not solution.mechanism_sentence:
            solution.mechanism_sentence = solution.concept.working_principle
        if result.closed_by == "cap":
            for oid in result.board.closure.open_blocking:
                obj = next((o for o in result.board.objections if o.id == oid), None)
                if obj is not None:
                    solution.open_questions.append(f"{oid}: {obj.text}")
        (iter_dir / "solution.json").write_text(solution.model_dump_json(indent=2), encoding="utf-8")
        return solution

    def _from_board(self, result: MeetingResult, problem: Problem) -> SolutionPrompt:
        board = result.board
        evidence_ids = [e.id for e in board.evidence if e.status == "ok"]
        parts = [
            Part(id="P1", name="Main frame", function="Carries the rated load", material="steel tube",
                 size_class_mm=SizeClass(min=300, max=600), qty=1),
            Part(id="P2", name="Drive / lift unit", function="Moves the load between levels", material="aluminium",
                 size_class_mm=SizeClass(min=100, max=300), qty=1),
            Part(id="P3", name="Sensor unit", function="Senses load and position", material="electronics",
                 size_class_mm=SizeClass(min=20, max=80), qty=1),
        ]
        return SolutionPrompt(
            title=problem.title,
            problem_restatement=problem.statement,
            mechanism_sentence="A framed unit carries the load while a drive unit moves it and a sensor unit guards safety.",
            decisive_choices=["Framed load path sized for the rated load", "Drive unit moves the load between levels", "Sensor unit guards the worst-case state"],
            open_question="Does the drive hold the rated load at the worst-case position?",
            transfer_line="Force: load -> frame -> drive unit | Measured: load cell -> amplifier -> laptop",
            assumed_constraints=[],
            functional_decomposition=[f.text for f in board.functions] or ["Support and move the load"],
            concept=ConceptBody(
                working_principle="A framed unit carries the load while a drive unit moves it and a sensor unit guards safety.",
                parts=parts,
                connections=[Connection(from_id="P1", to_id="P2", kind="mechanical", label="bolted"),
                             Connection(from_id="P2", to_id="P3", kind="electrical", label="signal")],
                loads=[Load(on_id="P1", label="F", direction="down")],
            ),
            key_estimates=[KeyEstimate(quantity="rated load force", value=588.6, unit="N",
                                       method="calc: mass times gravity",
                                       evidence_ids=evidence_ids[:1])],
            measurement_chain=[
                MeasurementStage(stage="sensor", name="load cell", interface="bridge"),
                MeasurementStage(stage="conditioning", name="amplifier", interface="analog"),
                MeasurementStage(stage="instrument", name="DAQ", interface="USB"),
                MeasurementStage(stage="computer", name="laptop", interface="software"),
            ],
            fabrication_steps=[
                FabricationStep(step=1, description="Cut and weld the main frame", method="welding", parts_present=["P1"]),
                FabricationStep(step=2, description="Fit the drive unit to the frame", method="bolting", parts_present=["P1", "P2"]),
                FabricationStep(step=3, description="Wire the sensor unit and test", method="wiring", parts_present=["P1", "P2", "P3"]),
            ],
            risks=[{"risk": "Overload at worst case", "mitigation": "Rated with margin; sensor cutoff"}],
            novelty_claim="Integrated folding frame with sensed drive (fake-mode claim).",
            cost_class="$100-1k",
            figure_spec=FigureSpec(system_view="side view of the integrated unit", critical_part_id="P2",
                                   preferred_view="side"),
            open_questions=[],
        )
