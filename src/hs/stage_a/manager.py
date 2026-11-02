"""Manager: inspirations, written diagnosis, revert-then-rewrite (spec §4.6, §3.2)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hs.master_prompt import MasterPrompt, section_problems, shrink_fraction
from hs.schemas import Gradients, Inspirations, MasterPromptRewrite, OutputGradient, SolutionPrompt
from hs.stage_a.archive import CouncilArchive
from hs.stage_a.meeting import MeetingResult


class Manager:
    def __init__(self, client: Any, master: MasterPrompt) -> None:
        self.client = client
        self.master = master
        self.last_gradients: Gradients | None = None
        self.manager_tools_registered = 0

    @property
    def no_progress_streak(self) -> int:
        return self.master.no_progress_streak

    def inspirations(self, archive: CouncilArchive) -> list[dict[str, Any]]:
        entries = archive.entries()
        if not entries:
            return []
        # Review finding 5: the picker sees what each past solution was and why it was judged so.
        payload = json.dumps([{"archive_id": e["id"], "status": e["status"], "title": e.get("title", ""),
                               "feedback": e.get("feedback", "")} for e in entries], indent=2)
        picks = self.client.structured("manager_inspirations", Inspirations,
                                       "Pick 1-3 inspirations; at least one rejected if any exist.",
                                       payload)
        by_id = {e["id"]: e for e in entries}
        chosen = [p for p in picks.picks if p.archive_id in by_id][:3]
        # code enforcement: at least one non-accepted when available
        if chosen and all(by_id[p.archive_id]["status"] == "accepted" for p in chosen):
            rejected = [e for e in entries if e["status"] != "accepted"]
            if rejected:
                from hs.schemas import InspirationPick

                chosen[-1] = InspirationPick(archive_id=rejected[-1]["id"], why_useful="Rejected attempt to learn from.")
        return [{"archive_id": p.archive_id, "status": by_id[p.archive_id]["status"],
                 "feedback_summary": by_id[p.archive_id].get("feedback", ""), "why_useful": p.why_useful}
                for p in chosen]

    def output_gradient(self, solution: SolutionPrompt, feedback_text: str,
                        iter_dir: Path, chain: str = "") -> OutputGradient:
        """Step 1 of the TextGrad chain: per feedback item, what must change."""
        prompt = (
            f"SOLUTION:\n{solution.model_dump_json(indent=2)}\n\nWRITTEN FEEDBACK:\n{feedback_text}\n\n"
            f"BACKWARD CHAIN (built by code from the board, the transcript and the master prompt):\n{chain}\n\n"
            "Step 1 (output gradient): for each feedback item or designer region, state in writing "
            "what in the solution or on the whiteboard must change. If the reason for the rejection lies in "
            "the meeting process (no proposal formed, an objection left unresolved, a vote before the "
            "deciding quantity was computed), say so in process_cause. Do not diagnose the prompt yet."
        )
        gradient = self.client.structured("manager_output_gradient", OutputGradient,
                                          "You are the Manager, step 1: judge the output against the feedback.",
                                          prompt)
        (iter_dir / "gradient_output.json").write_text(gradient.model_dump_json(indent=2), encoding="utf-8")
        return gradient

    def diagnose(self, room: MeetingResult, solution: SolutionPrompt, feedback_text: str,
                 iter_dir: Path, output_gradient: OutputGradient | None = None) -> Gradients:
        """Step 2 of the TextGrad chain: which prompt part or behaviour caused it."""
        stats = json.dumps(room.stats)
        notes_path = iter_dir / "manager_notes.md"
        meeting_notes = notes_path.read_text(encoding="utf-8") if notes_path.exists() else ""
        chain = backward_chain(room, solution, self.master)
        if output_gradient is None:
            output_gradient = self.output_gradient(solution, feedback_text, iter_dir, chain)
        prompt = (
            f"BACKWARD CHAIN (claim -> evidence or objection -> member turn -> master prompt section):\n{chain}\n\n"
            "TRANSCRIPT:\n" + "\n".join(f"{t['member']}: {t['message']}" for t in room.transcript)
            + f"\n\nMEMBER STATS: {stats}\n\nYOUR MEETING NOTES:\n{meeting_notes}"
            f"\n\nSTEP-1 OUTPUT GRADIENT:\n{output_gradient.model_dump_json(indent=2)}"
            f"\n\nSOLUTION:\n{solution.model_dump_json(indent=2)}"
            f"\n\nFEEDBACK:\n{feedback_text}\n\nCURRENT MASTER PROMPT:\n{self.master.text()}"
            "\n\nStep 2 (prompt gradient). You are the coach of this council. First, for each feedback item, "
            "write whether you apply, defer or reject it and why (feedback_decisions). Then, per section and per "
            "member, state which part of the prompt or which behaviour produced each step-1 item (cite it in "
            "'explains'), and how it should change. Most often the fix is a member's own role block: how this "
            "member should reason, what to check before proposing, what to search for; sometimes adding, removing "
            "or merging a member, or a new tool. Judge in the agenda whether the problem is targeted or broad. "
            "Never write design answers or numbers into a role, never tell members to drop an objection, and "
            "never tell them to treat an unchecked item as done. Never propose a design. Never write pipeline rules: "
            "retry limits, caps and gating live in code, not in the prompt. State whether this is the "
            "same problem as the previous failure and which sections to revert if so. If a missing "
            "calculator caused the failure, you may add up to 2 entries to new_tool_proposals "
            "(name, description, JSON-schema parameters, python_source defining run(args), "
            "smoke_test_input); each is smoke-tested in the sandbox and registered for all members."
        )
        gradients = self.client.structured("manager_gradients", Gradients,
                                           "You are the Manager, step 2: diagnose which prompt part or behaviour caused the output.",
                                           prompt)
        self.last_gradients = gradients
        (iter_dir / "gradient_prompt.json").write_text(gradients.model_dump_json(indent=2), encoding="utf-8")
        return gradients

    def register_proposed_tools(self, gradients: Gradients, tools: Any) -> list[str]:
        """A5: Manager-proposed tools go through the same sandbox smoke test
        and registry as member tools, capped by MAX_MANAGER_NEW_TOOLS."""
        from hs import config

        registered: list[str] = []
        if tools is None:
            return registered
        for proposal in gradients.new_tool_proposals:
            if self.manager_tools_registered >= config.MAX_MANAGER_NEW_TOOLS:
                break
            ok, _msg = tools.new_tool("Manager", proposal.name, proposal.description,
                                      proposal.parameters, proposal.python_source,
                                      proposal.smoke_test_input)
            if ok:
                self.manager_tools_registered += 1
                registered.append(proposal.name)
        return registered

    def _optimize(self, instructions: str, user_text: str, out: Path) -> MasterPromptRewrite:
        rewrite = self.client.structured("optimizer", MasterPromptRewrite, instructions, user_text)
        out.write_text(rewrite.model_dump_json(indent=2), encoding="utf-8")  # A3: every output is saved
        return rewrite

    def edit(self, room: MeetingResult, solution: SolutionPrompt, feedback_text: str,
             iter_dir: Path, tools: Any = None) -> dict[str, Any]:
        """Diagnosis -> revert (code) -> optimizer rewrite, guarded per section, with at most one guard
        re-ask and one shrink re-ask (spec §3.2). Every optimizer output is saved; nothing is lost silently."""
        output_gradient = self.output_gradient(solution, feedback_text, iter_dir,
                                               backward_chain(room, solution, self.master))
        gradients = self.diagnose(room, solution, feedback_text, iter_dir, output_gradient)
        tools_registered = self.register_proposed_tools(gradients, tools)
        reverted = self.master.apply_reverts(gradients)
        notes = [f"{h} reverted to the revision the Manager named" for h in reverted]
        base = dict(self.master.sections)
        notes_json = gradients.model_dump_json(indent=2)
        rewrite = self._optimize(
            "Rewrite only the sections that need it, as free Markdown section text, using the exact section "
            "headings of the master prompt (e.g. '## 4. Meeting protocol'); for each section give the reason and "
            "the feedback item it answers. Improving how a member reasons is done in that member's ### block "
            "under ## 2. Roles; adding, removing or merging a member is adding, removing or merging ### blocks. "
            "Write engineering content only "
            "(design knowledge, checks, member behaviour, protocol); never write pipeline rules such as retry "
            "limits, caps or gating — those live in code. Never put design answers or numbers into a role, "
            "and never tell members to drop an objection or to treat an unchecked item as done.",
            f"MASTER PROMPT:\n{self.master.text()}\n\nMANAGER NOTES (step-2 prompt gradient; consume this only):\n"
            f"{notes_json}", iter_dir / "rewrite.json")
        change_notes = [rewrite.change_note]
        proposed, dropped = self.master.propose(rewrite)
        notes += [f"heading '{h}' could not be placed on one section; that text was not applied" for h in dropped]
        bad = {h: probs for h, t in proposed.items() if (probs := section_problems(h, base[h], t))}
        if bad:
            listing = "\n\n".join(f"{h}\nPROBLEM: {'; '.join(probs)}\nYOUR TEXT:\n{proposed[h]}"
                                   for h, probs in bad.items())
            again = self._optimize(
                "Your rewrite of the sections below broke a guard. Rewrite only these sections so the guard "
                "holds; keep your intent.", f"MASTER PROMPT:\n{self.master.text()}\n\nSECTIONS:\n{listing}",
                iter_dir / "rewrite_guard_reask.json")
            change_notes.append(again.change_note)
            fixed, _ = self.master.propose(again)
            for h, probs in bad.items():
                if h in fixed and not section_problems(h, base[h], fixed[h]):
                    proposed[h] = fixed[h]
                else:
                    proposed.pop(h)
                    notes.append(f"{h} kept its previous text: {'; '.join(probs)}")
        shrunk = [h for h, t in proposed.items() if shrink_fraction(base[h], t) > 0.5]
        if shrunk:
            listing = "\n\n".join(
                f"{h} lost {round(100 * shrink_fraction(base[h], proposed[h]))} % of its text. Removed lines:\n"
                + "\n".join(f"- {line}" for line in base[h].splitlines() if line.strip() and line not in proposed[h])
                + f"\nYOUR NEW TEXT:\n{proposed[h]}" for h in shrunk)
            again = self._optimize(
                "These sections lost more than half of their text in your rewrite. Is that intended? Reply with "
                "the final text of each listed section (unchanged if the cut was intended).",
                f"MASTER PROMPT:\n{self.master.text()}\n\nSECTIONS:\n{listing}",
                iter_dir / "rewrite_shrink_reask.json")
            change_notes.append(again.change_note)
            confirmed, _ = self.master.propose(again)
            for h in shrunk:
                if h in confirmed and not section_problems(h, base[h], confirmed[h]):
                    proposed[h] = confirmed[h]  # whatever it answers the second time is applied
        if gradients.agenda.strip():
            protocol = proposed.get("## 4. Meeting protocol", base.get("## 4. Meeting protocol", ""))
            proposed["## 4. Meeting protocol"] = with_agenda(protocol, gradients.agenda)
        reasons = [f"{s.heading}: {s.reason} (answers: {s.answers})" for s in rewrite.sections if s.reason]
        report = self.master.commit(proposed, " ".join(n for n in change_notes if n), notes + reasons)
        report["reverted"] = reverted
        report["tools_registered"] = tools_registered
        (iter_dir / "manager_edit.json").write_text(json.dumps(
            {k: v for k, v in report.items() if k != "gradients"}, indent=2), encoding="utf-8")
        return report


def backward_chain(room: MeetingResult, solution: SolutionPrompt, master: MasterPrompt) -> str:
    """B13: for each claim of the solution, the evidence behind it, the member turn that produced the
    evidence and that member's role section; open objections; and the process facts of the meeting."""
    from hs.master_prompt import roster_of

    board = room.board
    by_id = {e.id: e for e in board.evidence}
    roster = roster_of(master.sections)
    lines: list[str] = []
    for est in getattr(solution, "key_estimates", []) or []:
        head = f"Claim: {est.quantity} = {est.value:g} {est.unit} ({est.method})"
        if not est.evidence_ids:
            lines.append(f"- {head} -> no evidence cited")
        for eid in est.evidence_ids:
            ev = by_id.get(eid)
            if ev is None:
                lines.append(f"- {head} -> {eid} is not on the board")
                continue
            turn = next((t["message"] for t in room.transcript
                         if t["member"] == ev.author and t["cycle"] == ev.cycle), "")
            first = turn.split(". ")[0] + "." if turn else "(no message recorded)"
            section = f"## 2. Roles / ### {ev.author}" if ev.author in roster else ev.author
            lines.append(f"- {head} -> {eid} ({ev.tool} by {ev.author}, cycle {ev.cycle}): {ev.purpose}: "
                         f"{ev.output_summary} -> {ev.author}'s turn: \"{first}\" -> {section}")
    for o in board.objections:
        if o.status == "open":
            section = f"## 2. Roles / ### {o.author}" if o.author in roster else o.author
            lines.append(f"- Open objection {o.id} by {o.author} ({'blocking' if o.blocking else 'not blocking'}) "
                         f"on {o.target_id}: {o.text} -> {section}")
    proposal = (f"proposal v{board.proposal.version} by {board.proposal.author}" if board.proposal
                else "no proposal formed")
    ready = [m for m, v in board.votes.items() if board.proposal and v.version == board.proposal.version and v.ready]
    lines.append(f"- Process: the meeting closed by {room.closed_by} after {room.cycles_used} cycles; {proposal}; "
                 f"ready votes: {', '.join(ready) or 'none'} -> ## 4. Meeting protocol")
    return "\n".join(lines)


AGENDA_HEADING = "### Agenda for the next meeting (Manager)"


def with_agenda(protocol: str, agenda: str) -> str:
    """Write the Manager's agenda into §4 (spec §4.6), replacing the previous iteration's agenda."""
    kept: list[str] = []
    skipping = False
    for line in protocol.splitlines():
        if line.strip() == AGENDA_HEADING:
            skipping = True
            continue
        if skipping and line.startswith("### "):
            skipping = False
        if not skipping:
            kept.append(line)
    return "\n".join(kept).rstrip() + f"\n\n{AGENDA_HEADING}\n{agenda.strip()}"
