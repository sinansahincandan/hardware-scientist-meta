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
        novelty_md = novelty + "\n\nSources:\n" + "\n".join(f"- {c.get('url', '')}" for c in citations)
        (iter_dir / "novelty.md").write_text(novelty_md, encoding="utf-8")
        # 2) verdict (structured; free-text judgment + accept + evidence requests)
        evidence_table = "\n".join(
            f"{e.id} [{e.tool}] {e.output_summary}" for e in board.evidence)
        prompt = (
            f"PROBLEM AND CRITERIA:\n{sections.get('## 1. Problem', '')}\n{sections.get('## 5. Criteria', '')}\n\n"
            f"SOLUTION:\n{solution.model_dump_json(indent=2)}\n\n"
            f"EVIDENCE TABLE:\n{evidence_table}\n\n"
            f"MEETING CLOSURE: closed_by={closed_by}\n\n"
            f"PRIOR ART:\n{novelty}\n\n"
            "Write your judgment as free text. Consult cited evidence only when a claim looks doubtful; "
            "add one evidence_request per doubtful critical claim. "
            "This is concept-stage design: the only evidence the room can produce is calculation, "
            "simulation, sketches and literature/datasheet search. Judge whether the analysis is sound "
            "(right model, regime, inputs and units), not whether a physical test has been run — you are "
            "not a physical test and no bench exists in this system. Never make acceptance depend on a "
            "bench test, prototype measurement or physical trace; phrase every evidence_request as a "
            "computation, simulation, sketch or search the room can actually perform. If the concept "
            "works physically and is buildable on sound analysis, accept it and put remaining test "
            "needs in your feedback text, not in evidence_requests."
        )
        verdict = self.client.structured(
            "evaluator", Verdict,
            "You are the Evaluator, a senior engineer. Judge whether it works and can be built.",
            prompt)
        # Code rule (spec §4.5): cap closure with open blocking objection => reject.
        if closed_by == "cap" and any(o.blocking and o.status == "open" for o in board.objections):
            verdict = Verdict(feedback=verdict.feedback + " [code rule: cap closure with open blocking objection]",
                              evidence_requests=verdict.evidence_requests, accept=False)
        (iter_dir / "verdict.json").write_text(
            json.dumps({**verdict.model_dump(), "source": "evaluator"}, indent=2), encoding="utf-8")
        return verdict
