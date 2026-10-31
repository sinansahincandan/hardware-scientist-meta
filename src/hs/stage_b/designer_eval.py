"""Designer evaluation: S1 faithful? S2 flaw? + routing (spec §5.5)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hs import config
from hs.schemas import DesignerEval, SolutionPrompt


def decide(ev: DesignerEval, round_idx: int, max_rounds: int = config.MAX_S1_ROUNDS) -> str:
    """Returns s1_pass | s1_retry | s2_return."""
    if ev.s2_flaw:
        return "s2_return"
    if ev.s1_faithful:
        return "s1_pass"
    if round_idx + 1 < max_rounds:
        return "s1_retry"
    return "s2_return"


def feedback_text(ev: DesignerEval, round_idx: int, max_rounds: int = config.MAX_S1_ROUNDS) -> str:
    if ev.s2_flaw:
        return ev.s2_feedback
    if not ev.s1_faithful and round_idx + 1 >= max_rounds:
        return (f"the render never matched the schematic after {max_rounds} rounds: "
                f"{ev.s1_differences}; the concept is probably under-specified")
    return ev.s1_differences or ev.s2_feedback


class DesignerEvalRunner:
    def __init__(self, client: Any) -> None:
        self.client = client

    def run(self, annotated_png: Path, labeled_png: Path, solution: SolutionPrompt,
            missing_parts: list[str]) -> DesignerEval:
        prompt = (
            f"SOLUTION SUMMARY:\n{solution.model_dump_json(indent=2)}\n\n"
            f"MISSING PARTS (not localized): {missing_parts}\n\n"
            "S1: is the render faithful to the schematic (same parts, connections, relative sizes; "
            "perspective/layout may differ)? S2: does seeing it expose a real design flaw? "
            "Do not blame the design for rendering mistakes; S2 must point at a concrete image feature."
        )
        return self.client.structured("designer_eval", DesignerEval,
                                      "You are the designer-evaluator (VLM). Compare annotated render vs schematic.",
                                      prompt, image_paths=[annotated_png, labeled_png])
