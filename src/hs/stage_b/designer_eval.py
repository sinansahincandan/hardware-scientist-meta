"""Designer evaluation: pixel-first S1/S2 + routing (spec §5.5, AUTOPILOT §7.3)."""
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


def label_failed(ev: DesignerEval) -> bool:
    """True when S1 failed because image-drawn labels are wrong/misspelled."""
    text = (ev.label_findings or "").lower()
    return bool(text) and any(w in text for w in ("wrong", "misspell", "mislabel", "incorrect", "does not match"))


class DesignerEvalRunner:
    def __init__(self, client: Any) -> None:
        self.client = client

    def run(self, annotated_png: Path, labeled_png: Path, solution: SolutionPrompt,
            missing_parts: list[str]) -> DesignerEval:
        prompt = (
            "STEP 1 — PIXEL-FIRST: look at the annotated render ONLY and write pixel_description: "
            "what you actually see, part by part, including every visible label exactly as spelled. "
            "A label alone never proves a connection; describe the physical connection you can see. "
            "Do this before reading the solution below.\n"
            "STEP 2 — LABELS: in label_findings, check every drawn label: does it name the right "
            "part and is it spelled correctly? Say 'labels ok' only if all pass; otherwise name each wrong label.\n"
            "STEP 3 — REQUIREMENTS: for each requirement (same parts, same connections, same relative "
            "sizes, operating moment visible, transfer path visible) report observed/ambiguous/missing "
            "and name the stage that caused each fault: meeting, schematic, prompt, or render.\n"
            "STEP 4 — S1/S2: S1 faithful = same parts/connections/relative sizes (perspective may differ) "
            "AND all labels correct. If any label is wrong, s1_faithful=false and start s1_differences with 'LABEL: '. "
            "S2: does seeing it expose a real design flaw? Do not blame the design for rendering mistakes; "
            "S2 must point at a concrete image feature.\n\n"
            f"SOLUTION SUMMARY:\n{solution.model_dump_json(indent=2)}\n\n"
            f"MISSING PARTS (not localized): {missing_parts}\n"
        )
        return self.client.structured("designer_eval", DesignerEval,
                                      "You are the designer-evaluator (VLM). Compare annotated render vs schematic.",
                                      prompt, image_paths=[annotated_png, labeled_png])
