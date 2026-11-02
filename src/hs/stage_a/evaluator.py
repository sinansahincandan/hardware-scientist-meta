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
              closed_by: str, iter_dir: Path) -> Verdict:
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
        evidence_table = "\n".join(
            f"{e.id} [{e.tool}, {e.author}] {e.purpose}: {e.output_summary}" for e in board.evidence)
        if board.proposal is None:
            proposal_fact = "No proposal was formed on the whiteboard in this meeting."
        else:
            votes = [f"{m}: {'ready' if v.ready else 'NOT ready'} ({v.reason})" for m, v in board.votes.items()
                     if v.version == board.proposal.version]
            proposal_fact = (f"Proposal v{board.proposal.version} by {board.proposal.author}. Votes on it: "
                             + ("; ".join(votes) if votes else "none") + ".")
        open_objections = "\n".join(
            f"- {o.id} by {o.author} ({'blocking' if o.blocking else 'not blocking'}): {o.text}"
            for o in board.objections if o.status == "open") or "(none)"
        prompt = (
            f"PROBLEM AND CRITERIA:\n{sections.get('## 1. Problem', '')}\n{sections.get('## 5. Criteria', '')}\n\n"
            f"SOLUTION:\n{solution.model_dump_json(indent=2)}\n\n"
            f"EVIDENCE TABLE:\n{evidence_table}\n\n"
            f"HOW THE MEETING CLOSED (facts, for your judgement): closed by "
            f"{'consensus' if closed_by == 'consensus' else 'the cycle cap without consensus'} after "
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
            "the concept unsettled); no rule decides this for you."
        )
        verdict = self.client.structured(
            "evaluator", Verdict,
            "You are the Evaluator, a senior engineer. Judge whether it works and can be built.",
            prompt)
        (iter_dir / "verdict.json").write_text(
            json.dumps({**verdict.model_dump(), "source": "evaluator"}, indent=2), encoding="utf-8")
        return verdict
