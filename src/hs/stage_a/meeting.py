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
MANAGER_ACTIONS = {"raise_objection", "resolve_objection", "read_evidence"}


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
        else:
            message = self._turn(member, cycle)
        message = self._shorten_if_long(member, message, member_instructions(self.master.sections, member),
                                        "member", cycle)
        self.transcript.append({"cycle": cycle, "member": member, "message": message})
        self.history.append({"cycle": cycle, "member": member, "kind": "turn_end"})

    def _run_manager_turn(self, roster: list[str], cycle: int) -> None:
        """Manager's end-of-cycle steering turn (spec §4.3 v2). Never designs, never votes."""
        if getattr(self.client, "is_fake", False):
            message = ("The Manager has reviewed this cycle. The room has evidence on the board; "
                       "the next cycle should test the weakest claim before voting.")
            self.transcript.append({"cycle": cycle, "member": "Manager", "message": message})
            self.history.append({"cycle": cycle, "member": "Manager", "kind": "turn_end"})
            (self.iter_dir / "turns" / f"c{cycle}_Manager.json").write_text(
                json.dumps({"cycle": cycle, "member": "Manager", "message": message}, indent=2), encoding="utf-8")
            return
        from hs.stage_a.council import SPEAKING_RULE

        instructions = (
            "You are the Manager, process lead of this council. You steer the process only: point out a "
            "critical quantity nobody computed, an objection closed without evidence, a vote that came too "
            "early, or a missing expertise; ask a named member to compute, sketch or look something up; you "
            "may raise or resolve process objections on the whiteboard (whether one of your objections blocks "
            "the vote is your judgement from its content) and register a new tool. From cycle 2, if no "
            "proposal is on the board, name the member whose favored concepts should be integrated and ask "
            "them to write the proposal (update_proposal) in their next turn. Check the key results on the board "
            "against everyday scales (accelerations in g, sizes against a person or a door, loads against body "
            "weights, energies against daily household use) and name any that look off. You never propose design "
            "concepts and you never vote. Keep short notes: end your message with one line "
            "'Note on <member>: ...' for each member you observed. " + SPEAKING_RULE)
        message = self._turn("Manager", cycle, instructions_override=instructions, role="manager",
                             allowed_actions=MANAGER_ACTIONS)
        message = self._shorten_if_long("Manager", message, instructions, "manager", cycle)
        self.transcript.append({"cycle": cycle, "member": "Manager", "message": message})
        self.history.append({"cycle": cycle, "member": "Manager", "kind": "turn_end"})
        (self.iter_dir / "turns" / f"c{cycle}_Manager.json").write_text(
            json.dumps({"cycle": cycle, "member": "Manager", "message": message}, indent=2), encoding="utf-8")
        with (self.iter_dir / "manager_notes.md").open("a", encoding="utf-8") as fh:
            fh.write(f"\n## Cycle {cycle}\n{message}\n")

    # -- main loop ---------------------------------------------------------------------
    def run(self) -> MeetingResult:
        roster = roster_of(self.master.sections)
        stats: dict[str, dict[str, int]] = {m: {"evidence": 0, "objections_raised": 0,
                                                "votes": 0, "tool_errors": 0}
                                            for m in roster}
        closed_by = "cap"
        cycles_used = 0
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
            # A4: consensus is decided after the Manager's turn, so an objection it raised counts.
            if cycle >= self.min_cycles and self.board.consensus_reached(roster):
                closed_by = "consensus"
                break
        if closed_by != "consensus" and self.board.proposal is not None:
            # vote-only round (spec §4.3): only vote / raise_objection
            for member in roster:
                if getattr(self.client, "is_fake", False):
                    turn = self.client.scripted_turn(member, roster, self.max_cycles, self.board)
                    if turn.get("vote") is not None:
                        self.board.apply_op(member, {"action": "vote", "ready": turn["vote"]["ready"],
                                                     "reason": turn["vote"]["reason"]})
                else:
                    self._run_real_turn(member, roster, self.max_cycles, vote_only=True)
            if self.board.consensus_reached(roster):
                closed_by = "consensus"
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
                "Also write: mechanism_sentence (one sentence stating the working principle); "
                "decisive_choices (EXACTLY 3, the choices that most determine whether this concept works); "
                "open_question (EXACTLY 1, the most important unresolved question); "
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
