"""FakeClient — deterministic offline client (spec §0.7). Zero network.

Scenario scripts (PLAN.md §7) drive every controller branch. Synthetic usage
is priced through the same CostLog path as real calls.
"""
from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw
from pydantic import BaseModel

from hs import config
from hs.client import CostLog
from hs.schemas import (
    DesignerEval,
    Gradients,
    InspirationPick,
    Inspirations,
    LessonCandidate,
    Lessons,
    LightCheck,
    Localization,
    MasterPromptRewrite,
    Problem,
    ProblemSet,
    RewriteSection,
    SchematicSpec,
    SolutionPrompt,
    Verdict,
    VLMPrompt,
)

SYNTHETIC_USAGE = {"input_tokens": 1200, "cached_input_tokens": 200, "output_tokens": 300, "reasoning_tokens": 80}


class FakeClient:
    is_fake = True

    def __init__(self, run_dir: Path | None = None, scenario: str | None = None,
                 max_cost: float | None = None) -> None:
        self.cost = CostLog(run_dir, max_cost=max_cost)
        self.scenario = scenario or os.environ.get("HS_FAKE_SCENARIO", "happy")
        self.fake_iteration = 0
        self.fake_attempt = 0
        self.counters: dict[str, int] = {}
        self._image_n = 0

    def _next(self, key: str) -> int:
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    def record_fake(self, role: str) -> None:
        usage = dict(SYNTHETIC_USAGE)
        if self.scenario == "cost_cap" and role != "master_rev0":
            usage = {"input_tokens": 9_000_000, "cached_input_tokens": 0,
                     "output_tokens": 2_000_000, "reasoning_tokens": 1000}
        self.cost.check_budget(estimated_usd=0.01)
        self.cost.record(role, config.ROLES.get(role, config.ROLES["member"]).model, usage)

    # -- generic LLM surface -------------------------------------------------
    def structured(self, role: str, model_cls: type[BaseModel], instructions: str,
                   user_text: str, image_paths: list[Path] | None = None) -> Any:
        self.record_fake(role)
        name = model_cls.__name__
        handler = getattr(self, f"_fake_{name}", None)
        if handler is None:
            raise NotImplementedError(f"FakeClient has no script for {name}")
        return handler(user_text)

    def free_text(self, role: str, instructions: str, user_text: str,
                  tools: list[dict[str, Any]] | None = None) -> tuple[str, list[dict[str, Any]]]:
        self.record_fake(role)
        if role == "prior_art":
            return (
                ("Closest prior art: a generic commercial product in the same class. "
                 "Difference: the proposed concept integrates the functions differently."),
                [{"url": "https://example.org/fake-prior-art", "title": "Fake prior art"}],
            )
        return ("Fake free-text response.", [{"url": "https://example.org/fake-source", "title": "Fake source"}])

    def image_edit(self, prompt: str, reference_png: Path, size: str = "1536x1024",
                   extra_refs: list[Path] | None = None) -> bytes:
        self.cost.check_budget(estimated_usd=0.05)
        self.cost.record("image_model", config.IMAGE_MODEL, {"images": 1})
        self._image_n += 1
        img = Image.new("RGB", (800, 500), "white")
        draw = ImageDraw.Draw(img)
        colors = ["#d95f4b", "#3f7cac", "#70a37f", "#e3b505", "#8e6c8a"]
        for i in range(4):
            x = 60 + i * 180
            draw.rectangle([x, 180, x + 130, 330], fill=colors[(i + self._image_n) % len(colors)])
        draw.rectangle([40, 360, 760, 380], fill="#cccccc")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def sam_segment(self, phrase: str, image_png: Path, metadata: dict[str, str] | None = None) -> str:
        """Fake SAM: one box per phrase, placed on the fake render's coloured blocks by part number."""
        import re

        self.cost.check_budget(estimated_usd=0.01)
        self.cost.record("sam", config.SAM_MODEL, {"sam_calls": 1})
        with Image.open(image_png) as im:
            w, h = im.size
        digits = re.findall(r"\d+", phrase)
        i = (int(digits[-1]) - 1) % 4 if digits else 0
        x0 = int((60 + i * 180) / 800 * w)
        return (f"<0f>0<|box;x1={x0};y1={int(180 / 500 * h)};x2={x0 + int(130 / 800 * w)};"
                f"y2={int(330 / 500 * h)};w={w};h={h}|><|mask;x=0;y=0;data=1,1,!!!!!!|>")

    # -- scripted member turns (executed by Meeting against real board code) --
    def scripted_turn(self, member: str, roster: list[str], cycle: int, board: Any) -> dict[str, Any]:
        """Return {tools, ops, message, vote} for one fake member turn."""
        idx = roster.index(member)
        tools: list[dict[str, Any]] = []
        ops: list[dict[str, Any]] = []
        vote: dict[str, Any] | None = None
        open_eval = [o for o in board.objections if o.author == "Evaluator" and o.status == "open"]
        if cycle == 1:
            if idx == 0 and not board.functions:
                ops.append({"action": "add_function", "text": "Support and move the load"})
                ops.append({"action": "add_function", "text": "Sense state and keep the operator safe"})
            if board.functions:
                ops.append({"action": "add_concept", "function_id": board.functions[0].id,
                            "text": f"Concept by {member}: modular approach {idx + 1} for the main function"})
            if idx == 0:
                tools.append({"tool": "calc", "expression": "60*9.81",
                              "purpose": "weight force of the rated load"})
            if idx == 1:
                tools.append({"tool": "simulate",
                              "script": "import numpy as np\nx=np.linspace(0,1,5)\nprint(float(x.max()))",
                              "purpose": "trivial response sweep"})
            if idx == 2:
                tools.append({"tool": "sketch",
                              "script": ("import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n"
                                         "plt.figure(figsize=(3,2))\nplt.plot([0,1],[0,1])\nplt.savefig('sketch.png')\n"),
                              "caption": "first layout sketch"})
            message = f"{member}: cycle 1 proposals posted; estimates are on the board as evidence."
        else:
            if open_eval and idx == 0:
                tools.append({"tool": "calc", "expression": "2*60*9.81",
                              "purpose": "check requested by the Evaluator"})
                # resolution op is appended by Meeting after tools run (needs new evidence id)
                ops.append({"action": "__resolve_first_eval__"})
            if board.proposal is None:
                concept_ids = [c.id for c in board.concepts if c.status != "dropped"][:2]
                ops.append({"action": "update_proposal",
                            "text": "Integrated concept: combine the favoured per-function concepts into one device.",
                            "concept_ids": concept_ids,
                            "key_claims": [{"claim": "Rated load force is supported", "evidence_ids": []}]})
            if self.scenario == "cap" and idx == len(roster) - 1:
                if not any(o.author == member and o.status == "open" for o in board.objections):
                    target = board.proposal.concept_ids[0] if board.proposal and board.proposal.concept_ids else "C1"
                    ops.append({"action": "raise_objection", "target_id": target,
                                "text": "Unresolved safety concern: no evidence for the worst-case load.",
                                "blocking": True})
                vote = {"ready": False, "reason": "Blocking objection still open."}
            else:
                still_blocking = any(o.blocking and o.status == "open" and o.author != "Evaluator"
                                       for o in board.objections)
                vote = {"ready": not still_blocking,
                        "reason": "Proposal survives my objections." if not still_blocking else "Blocking objection open."}
            message = f"{member}: reviewed the proposal against the evidence on the board."
        return {"tools": tools, "ops": ops, "message": message, "vote": vote}

    # -- structured scripts ----------------------------------------------------
    def _fake_Verdict(self, user_text: str) -> Verdict:
        n = self._next("verdict")
        if self.scenario == "cap":
            return Verdict(feedback="The meeting closed by cap with an open blocking objection; not acceptable.",
                           evidence_requests=[], accept=False)
        if self.scenario == "revert":
            if n <= 2:
                return Verdict(feedback="The critical quantity was never computed; the room voted too early.",
                               evidence_requests=["Compute the worst-case load with units."] if n == 1 else [],
                               accept=False)
            return Verdict(feedback="The revised process computed the critical quantity; concept works and is buildable.",
                           evidence_requests=[], accept=True)
        # happy / evidence_request / schematic_fail / s1_* / s2_flaw / cost paths
        if n == 1:
            req = ["Compute the worst-case load with units and cite it."]
            return Verdict(feedback="Promising, but the critical load claim has no cited evidence yet.",
                           evidence_requests=req, accept=False)
        return Verdict(feedback="Concept works physically and is buildable with purchasable parts.",
                       evidence_requests=[], accept=True)

    def _fake_Gradients(self, user_text: str) -> Gradients:
        n = self._next("gradients")
        if self.scenario == "revert" and n >= 2:
            return Gradients(
                per_member=[], per_section=[],
                sections_to_change=["## 4. Meeting protocol"],
                root_cause="Same failure repeated: the protocol still lets the room vote before computing.",
                same_problem_as_before=True,
                repeat_explanation="Second failure repeats the first: no critical-quantity computation.",
                revert_sections=[{"heading": "## 4. Meeting protocol", "to_revision": 0}],
            )
        if self.scenario == "no_progress":
            return Gradients(per_member=[], per_section=[], sections_to_change=[],
                             root_cause="Nothing to change.", same_problem_as_before=False,
                             repeat_explanation="", revert_sections=[])
        return Gradients(
            per_member=[{"member": "Mechanics", "what_went_wrong": "Voted before citing evidence",
                         "what_should_change": "Cite evidence ids in key claims"}],
            per_section=[{"heading": "## 4. Meeting protocol", "diagnosis": "Voting happened too early",
                          "direction": "Require cited evidence before a ready vote"}],
            sections_to_change=["## 4. Meeting protocol"],
            root_cause="The protocol let the room converge before the critical quantity was computed.",
            same_problem_as_before=False, repeat_explanation="", revert_sections=[],
        )

    def _fake_MasterPromptRewrite(self, user_text: str) -> MasterPromptRewrite:
        if self.scenario == "no_progress":
            return MasterPromptRewrite(sections=[], change_note="No change proposed.")
        if self.scenario == "guard":
            return MasterPromptRewrite(
                sections=[RewriteSection(heading="## 5. Criteria", new_text="Be excellent.")],
                change_note="Deliberately guard-violating rewrite (fake guard scenario).")
        return MasterPromptRewrite(
            sections=[RewriteSection(
                heading="## 4. Meeting protocol",
                new_text=("Cycle 1: decompose into functions, propose concepts, post first estimates. "
                          "Cycles 2+: attack and defend with evidence. A member may only vote ready "
                          "when every key claim in the proposal cites at least one evidence id. "
                          "Evaluator evidence requests are blocking until resolved with evidence."))],
            change_note="Tightened the voting rule so ready votes require cited evidence (Manager diagnosis).",
        )

    def _fake_Inspirations(self, user_text: str) -> Inspirations:
        import json

        try:
            ids = json.loads(user_text).get("archive_ids", [])
        except Exception:
            ids = []
        picks = [InspirationPick(archive_id=i, why_useful="Relevant past attempt.") for i in ids[:2]]
        return Inspirations(picks=picks)

    def _fake_SolutionPrompt(self, user_text: str) -> SolutionPrompt:
        raise NotImplementedError("Secretary fake path builds SolutionPrompt from the whiteboard")

    def _fake_SchematicSpec(self, user_text: str) -> SchematicSpec:
        raise NotImplementedError("Schematic fake path builds SchematicSpec from the SolutionPrompt")

    def _fake_VLMPrompt(self, user_text: str) -> VLMPrompt:
        n = self._next("vlm")
        return VLMPrompt(
            prompt=f"Photorealistic rendering of the device in use, round {n}: keep the parts, connections and relative sizes of the reference.",
            must_not=[], changes_from_previous="Initial prompt." if n == 1 else "Clarified part separation after S1 differences.",
        )

    def _fake_Localization(self, user_text: str) -> Localization:
        raise NotImplementedError("Annotate fake path derives boxes from schematic geometry")

    def _fake_DesignerEval(self, user_text: str) -> DesignerEval:
        n = self._next("designer")
        if self.scenario == "s1_three_fail":
            if self.fake_attempt == 0:
                return DesignerEval(s1_faithful=False, s1_differences="A part is missing at the centre of the image.",
                                    s2_flaw=False, s2_feedback="", notes="")
            return DesignerEval(s1_faithful=True, s1_differences="", s2_flaw=False, s2_feedback="", notes="")
        if self.scenario == "s2_flaw" and self.fake_attempt == 0:
            return DesignerEval(s1_faithful=True, s1_differences="", s2_flaw=True,
                                s2_feedback="In the annotated render the drive part overlaps the frame at the centre joint, so it cannot be assembled.",
                                notes="")
        if n == 1:
            from hs.schemas import EvalRegion

            return DesignerEval(s1_faithful=False, s1_differences="One part is merged with its neighbour at the left of the image.",
                                regions=[EvalRegion(box=[100, 300, 400, 700], part_id="P2",
                                                    observed="merged with neighbour", expected="separate part",
                                                    source="render")],
                                s2_flaw=False, s2_feedback="", notes="")
        return DesignerEval(s1_faithful=True, s1_differences="", s2_flaw=False, s2_feedback="",
                            notes="Minor: finish looks polished.")

    def _fake_PartMap(self, user_text: str):
        import re

        from hs.schemas import PartMap, PartVisual

        ids = re.findall(r"^- (P\d+): ", user_text, flags=re.MULTILINE)
        return PartMap(parts=[PartVisual(part_id=pid, visual_phrase=f"fake part {pid[1:]}", count=1)
                              for pid in ids])

    def _fake_LabelCheck(self, user_text: str):
        from hs.schemas import LabelCheck

        return LabelCheck(wrong_labels=[], note="fake: labels ok")

    def _fake_Insights(self, user_text: str):
        from hs.schemas import InsightItem, Insights

        return Insights(items=[InsightItem(title="Fake finding", text="A synthetic finding from fake mode.",
                                           evidence_ids=["E1"])])

    def _fake_LightCheck(self, user_text: str) -> LightCheck:
        return LightCheck(ok=True, reason="Panel shows the requested parts.")

    def _fake_OutputGradient(self, user_text: str):
        from hs.schemas import OutputGradient

        return OutputGradient(items=[{"feedback_item": "critical claim lacks evidence",
                                      "must_change": "compute the critical quantity and cite it"}],
                              summary="The solution must carry cited evidence for its critical claim.")

    def _fake_VLMPromptGradient(self, user_text: str):
        from hs.schemas import VLMPromptGradient

        return VLMPromptGradient(per_region=[{"part_id": "P2", "diagnosis": "parts merged in the render",
                                              "prompt_fix": "separate the parts visually"}],
                                 fix_mode="local", summary="Local separation fix.")

    def _fake_ProgressCheck(self, user_text: str):
        from hs.schemas import ProgressCheck

        return ProgressCheck(fixed_region_pass=True, previous_pass=True, seam_visible=False, notes="kept")

    def _fake_Lessons(self, user_text: str) -> Lessons:
        return Lessons(candidates=[
            LessonCandidate(text="Require cited evidence ids before any ready vote in the meeting protocol.",
                            category="process", structural=True, evidence="trace: early votes"),
            LessonCandidate(text="The stair cart needs bigger wheels.",
                            category="process", structural=False, evidence="problem-specific, must be filtered"),
            LessonCandidate(text="Require cited evidence ids before any ready vote in the meeting protocol!",
                            category="prompts", structural=True, evidence="near-duplicate, must be filtered"),
        ])

    def _fake_ProblemSet(self, user_text: str) -> ProblemSet:
        return ProblemSet(problems=[
            Problem(title=f"Generated mechanism problem {i}",
                    statement=f"Design a concept-level device for generated task {i} with measurable performance.",
                    constraints=["Concept level only", "Buildable with purchasable parts"],
                    criteria=[], attachments=[])
            for i in range(1, 4)
        ])
