"""Evaluator: prior-art check + verdict. Never sees the transcript (spec §4.5)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hs.master_prompt import MasterPrompt
from hs.schemas import SolutionPrompt, Verdict
from hs.stage_a.whiteboard import Whiteboard


class Evaluator:
    def __init__(self, client: Any) -> None:
        self.client = client

    def judge(self, master: MasterPrompt, solution: SolutionPrompt, board: Whiteboard,
              closed_by: str, iter_dir: Path, previous_requests: list[str] | None = None) -> Verdict:
        sections = dict(master.sections)
        # 1) prior-art check (free text + web_search)
        novelty, citations = self.client.free_text(
            "prior_art",
            "Find the closest existing product, patent or paper to this concept and state the difference.",
            f"Concept:\n{solution.model_dump_json(indent=2)}",
            tools=[{"type": "web_search", "search_context_size": "low"}],
        )
        novelty_md = novelty + "\n\nSources:\n" + "\n".join(
            f"- {c.get('url', '')} — {c.get('title', '')}" for c in citations)
        (iter_dir / "novelty.md").write_text(novelty_md, encoding="utf-8")
        # 2) verdict (structured; free-text judgment + accept + evidence requests)
        def _read_note(e: Any) -> str:
            ref = e.references[0] if e.references else {}
            if e.tool != "web_search":
                return ""
            return " (page opened by the member)" if ref.get("read") else " (search result only; page not opened)"

        def _how(e: Any) -> str:
            # the calculation itself, so a sum's terms can be checked (without it the Evaluator asked three meetings
            # running for an itemized mass table the board already held: run 194659)
            if str(e.tool).split(":")[0] not in ("calc", "vetted_calc", "simulate"):
                return ""
            code = " ".join(str(e.code_or_query).split())
            return f" [computed as: {code[:400]}{' …' if len(code) > 400 else ''}]"

        evidence_table = "\n".join(
            f"{e.id} [{e.tool}, {e.author}] {e.purpose}: {e.output_summary}{_how(e)}{_read_note(e)}"
            for e in board.evidence)
        if board.proposal is None:
            proposal_fact = "No proposal was formed on the whiteboard in this meeting."
        else:
            votes = [f"{m}: {'ready' if v.ready else 'NOT ready'} ({v.reason})" for m, v in board.votes.items()
                     if v.version == board.proposal.version]
            proposal_fact = (f"Proposal v{board.proposal.version} by {board.proposal.author}. Members' readiness "
                             "opinions on it: " + ("; ".join(votes) if votes else "none") + "."
                             + ("\nCHIEF DESIGNER'S SELECTIONS:\n" + "\n".join(
                                 f"- {x.function_id} -> {x.concept_id or 'no separate means'}: {x.rationale}"
                                 for x in board.selections) if board.selections else "")
                             + (f"\nCHIEF DESIGNER'S CLOSING SYNTHESIS: {board.closure.chief_decision}"
                                if board.closure.chief_decision else ""))
        open_objections = "\n".join(
            f"- {o.id} by {o.author} ({'blocking' if o.blocking else 'not blocking'}): {o.text}"
            for o in board.objections if o.status == "open") or "(none)"
        try:
            problem = json.loads(sections.get("## 1. Problem", "") or "{}")
        except Exception:
            problem = {}
        given = [f"- constraint: {c}" for c in problem.get("constraints", []) or []] + \
                [f"- criterion: {c}" for c in problem.get("criteria", []) or []]
        prompt = (
            f"PROBLEM AND CRITERIA:\n{sections.get('## 1. Problem', '')}\n{sections.get('## 5. Criteria', '')}\n\n"
            + ("GIVEN CONSTRAINTS AND CRITERIA (review each one in constraint_review):\n" + "\n".join(given) + "\n\n"
               if given else "")
            + f"SOLUTION:\n{solution.model_dump_json(indent=2)}\n\n"
            f"EVIDENCE TABLE:\n{evidence_table}\n\n"
            f"HOW THE MEETING CLOSED (facts, for your judgement): closed by "
            f"{'consensus' if closed_by == 'consensus' else ('the chief designer’s decision (members advise; read their opinions)' if closed_by == 'chief' else 'the cycle cap without consensus')} after "
            f"{board.closure.cycles_used} cycles. {proposal_fact}\nOPEN OBJECTIONS:\n{open_objections}\n\n"
            f"PRIOR ART:\n{novelty}\n\n"
            "Write your judgment as free text. Consult cited evidence only when a claim looks doubtful; "
            "add one evidence_request per doubtful critical claim. The evidence table lists every calculation, "
            "simulation, sketch and literature source on the board: point out in your feedback each key claim "
            "that rests on no evidence or source. Check the key numbers against everyday scales and known "
            "regimes (accelerations in g, sizes against a person or a door, loads against body weights, energies "
            "against daily household use) and re-derive the arithmetic that decides acceptance; when a number "
            "looks off, add an evidence_request. List the deviations you can measure between the solution's "
            "numbers and the problem or its own evidence, and say for each whether it matters for the working "
            "principle (a deviation can be acceptable in concept design, but it must be noticed). "
            "This is concept-stage design: the only evidence the room can produce is calculation, "
            "simulation, sketches and literature/datasheet search. Judge whether the analysis is sound "
            "(right model, regime, inputs and units), not whether a physical test has been run — you are "
            "not a physical test and no bench exists in this system. Never make acceptance depend on a "
            "bench test, prototype measurement or physical trace; phrase every evidence_request as a "
            "computation, simulation, sketch or search the room can actually perform. If the concept "
            "works physically and is buildable on sound analysis, accept it and put remaining test "
            "needs in your feedback text, not in evidence_requests. Judge in writing what the meeting facts "
            "above mean for acceptance (for example, whether an open objection or a missing proposal leaves "
            "the concept unsettled); no rule decides this for you. In constraint_review, go through every given "
            "constraint and criterion in a sentence each: met, not met, or no longer valid for this concept (say "
            "why, e.g. the council found from evidence that it does not apply). Accept when the concept works and "
            "every constraint that still holds is met, or its shortfall is acceptable in your engineering judgement "
            "and you say so. Four checks a concept review must not skip, each written out in your feedback: "
            "(0) every function on the board has a means in the solution (a part that does it), or the chief designer "
            "wrote why it needs none; a function with neither is a missing function. "
            "(1) for every size or mass limit, add up the parts the board names along that direction (widths across "
            "the axle including what sits outside the frame, lengths front to back, heights stacked; masses of all "
            "parts) and state the sum against the limit; a limit argued only by a sketch annotation is not shown. "
            "A limit the board gives no part masses or sizes to sum is unknown, not a shortfall: an unknown is "
            "missing analysis the room can do, so ask for the sum with an evidence_request instead of accepting on "
            "the hope that it fits. A sum must carry every part of the solution: name any part it leaves out; a sum "
            "with parts missing does not show the limit. "
            "(1b) every constraint that states a number (a time, a speed, a force, a size, a mass, a power) is met "
            "only when the board computes the design's own value of that quantity and sets it against the number; "
            "a constraint met in words only, or marked not yet calculated, is unknown: ask for the calculation "
            "with an evidence_request rather than accept on it. "
            "(2) when the board gives two different values for the same quantity (a density, a load, a size), say "
            "which one the design used and whether the calculations that depend on it used the sourced one. "
            "(3) trace every flow the device must carry from start to end — material or workpiece, energy, "
            "signal — and name the part that does each step, and check that consecutive parts meet where the layout "
            "places them (positions, side order, which state of a moving part); a step no part does, or a gap "
            "between two parts that nothing bridges, is a missing function, and the concept does not work until it "
            "has one; a part placed in two different places in the text is a contradiction. (4) a blocking objection still open means the room did not "
            "settle that point: say in writing whether the evidence settles it or not. A literature value that rests "
            "on a search result whose page was never opened is weaker than one read from the page; say so where it "
            "decides acceptance. No scores."
            + (("\n\nTHE SAME ISSUES ARE RE-CHECKED FIRST (the loop's rule). Your previous verdict asked the room "
                "for:\n" + "\n".join(f"- {r}" for r in previous_requests) + "\nStart your feedback by saying for "
                "each whether the board now meets it, with the evidence id. When every one is met and the concept "
                "works with every stated limit shown, accept. A new gap you find now is an evidence_request only if "
                "it could make the concept fail or break a stated limit; any other improvement goes in your "
                "feedback text as advice, not as a reason to reject. ") if previous_requests else "")
        )
        verdict = self.client.structured(
            "evaluator", Verdict,
            "You are the Evaluator, a senior engineer. Judge whether it works and can be built.",
            prompt)
        (iter_dir / "verdict.json").write_text(
            json.dumps({**verdict.model_dump(), "source": "evaluator"}, indent=2), encoding="utf-8")
        return verdict
