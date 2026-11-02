"""Pydantic schemas (spec §12) + strict-schema post-processor (spec §9)."""
from __future__ import annotations

import copy
from typing import Any, Literal

from pydantic import BaseModel, Field

ConnectionKind = Literal["mechanical", "electrical", "optical", "fluid", "wireless", "thermal"]
LoadDirection = Literal["up", "down", "left", "right", "in", "out"]


class SizeClass(BaseModel):
    min: float
    max: float


class AssumedConstraint(BaseModel):
    constraint: str
    source: str
    evidence_ids: list[str] = Field(default_factory=list)


class Part(BaseModel):
    id: str
    name: str
    function: str
    material: str
    size_class_mm: SizeClass
    qty: int = 1


class Connection(BaseModel):
    from_id: str
    to_id: str
    kind: ConnectionKind
    label: str = ""


class Load(BaseModel):
    on_id: str
    label: str
    direction: LoadDirection


class ConceptBody(BaseModel):
    working_principle: str
    parts: list[Part]
    connections: list[Connection] = Field(default_factory=list)
    loads: list[Load] = Field(default_factory=list)


class KeyEstimate(BaseModel):
    quantity: str
    value: float
    unit: str
    method: str
    evidence_ids: list[str] = Field(default_factory=list)


class MeasurementStage(BaseModel):
    stage: Literal["sensor", "conditioning", "instrument", "computer"]
    name: str
    interface: str


class FabricationStep(BaseModel):
    step: int
    description: str
    method: str
    parts_present: list[str] = Field(default_factory=list)


class Risk(BaseModel):
    risk: str
    mitigation: str


class FigureSpec(BaseModel):
    system_view: str
    critical_part_id: str
    preferred_view: Literal["isometric", "top", "side", "section"] = "isometric"


class SolutionPrompt(BaseModel):
    title: str
    problem_restatement: str
    mechanism_sentence: str = ""
    decisive_choices: list[str] = Field(default_factory=list)
    open_question: str = ""
    transfer_line: str = ""
    assumed_constraints: list[AssumedConstraint] = Field(default_factory=list)
    functional_decomposition: list[str] = Field(default_factory=list)
    concept: ConceptBody
    key_estimates: list[KeyEstimate] = Field(default_factory=list)
    measurement_chain: list[MeasurementStage] = Field(default_factory=list)
    fabrication_steps: list[FabricationStep] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    novelty_claim: str = ""
    cost_class: Literal["<$100", "$100-1k", "$1k-10k", ">$10k"] = "$100-1k"
    figure_spec: FigureSpec
    open_questions: list[str] = Field(default_factory=list)


class Verdict(BaseModel):
    constraint_review: str = ""  # round 4: per given constraint/criterion, in prose; no scores
    feedback: str
    evidence_requests: list[str] = Field(default_factory=list)
    accept: bool


class MemberNote(BaseModel):
    member: str
    what_went_wrong: str
    what_should_change: str
    explains: str = ""


class SectionNote(BaseModel):
    heading: str
    diagnosis: str
    direction: str
    explains: str = ""


class RevertTarget(BaseModel):
    heading: str
    to_revision: int


class ToolProposal(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    python_source: str
    smoke_test_input: dict[str, Any] = Field(default_factory=dict)


class FeedbackDecision(BaseModel):
    feedback_item: str
    decision: str  # apply | defer | reject — read by people, not by code
    why: str


class Gradients(BaseModel):
    feedback_decisions: list[FeedbackDecision] = Field(default_factory=list)
    per_member: list[MemberNote] = Field(default_factory=list)
    per_section: list[SectionNote] = Field(default_factory=list)
    sections_to_change: list[str] = Field(default_factory=list)
    root_cause: str = ""
    agenda: str = ""
    same_problem_as_before: bool = False
    repeat_explanation: str = ""
    revert_sections: list[RevertTarget] = Field(default_factory=list)
    new_tool_proposals: list[ToolProposal] = Field(default_factory=list)


class OutputGradientItem(BaseModel):
    feedback_item: str
    must_change: str


class OutputGradient(BaseModel):
    items: list[OutputGradientItem] = Field(default_factory=list)
    process_cause: str = ""  # B13: when the rejection came from the process (no proposal, open objection)
    summary: str = ""


class VLMPromptGradientItem(BaseModel):
    part_id: str
    diagnosis: str
    prompt_fix: str = ""


class VLMPromptGradient(BaseModel):
    per_region: list[VLMPromptGradientItem] = Field(default_factory=list)
    fix_mode: Literal["local", "full"] = "local"
    summary: str = ""


class ProgressCheck(BaseModel):
    fixed_region_pass: bool = False
    previous_pass: bool = True
    seam_visible: bool = False
    notes: str = ""


class RewriteSection(BaseModel):
    heading: str
    new_text: str
    reason: str = ""  # B11: why this section changes
    answers: str = ""  # B11: the feedback item it answers


class MasterPromptRewrite(BaseModel):
    sections: list[RewriteSection] = Field(default_factory=list)
    change_note: str = ""


class Layout(BaseModel):
    col: int
    row: int


class SchematicNode(BaseModel):
    id: str
    label: str
    shape: Literal["rect", "circle", "beam", "plate", "cylinder"] = "rect"
    size_class_mm: SizeClass
    layout: Layout
    color_hint: str = "#7fb3d5"
    aspect: float = 1.33  # real width/height ratio of the part (coil spring ~0.35, girder ~6)


class SchematicEdge(BaseModel):
    from_id: str
    to_id: str
    kind: ConnectionKind
    label: str = ""
    arrow: bool = False


class SchematicLoad(BaseModel):
    on_id: str
    label: str
    direction: LoadDirection


class SchematicSpec(BaseModel):
    view: Literal["top", "side"] = "side"
    nodes: list[SchematicNode]
    edges: list[SchematicEdge] = Field(default_factory=list)
    loads: list[SchematicLoad] = Field(default_factory=list)
    critical_part_id: str
    scale_bar_mm: float = 10.0
    notes: list[str] = Field(default_factory=list)


class VisualPlan(BaseModel):
    view: str = ""
    spatial_layout: str = ""
    operating_moment: str = ""
    transfer_path: str = ""
    interactions: str = ""
    avoid: list[str] = Field(default_factory=list)


class FocusPart(BaseModel):
    part_id: str
    material: str = ""
    purpose: str = ""
    callout: str = ""


class VLMPrompt(BaseModel):
    prompt: str
    must_not: list[str] = Field(default_factory=list)
    changes_from_previous: str = ""
    visual_plan: VisualPlan = Field(default_factory=VisualPlan)
    focus_parts: list[FocusPart] = Field(default_factory=list)


class Box1000(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class LocalizedPart(BaseModel):
    id: str
    found: bool
    box_1000: Box1000


class Localization(BaseModel):
    parts: list[LocalizedPart] = Field(default_factory=list)


class EvalRegion(BaseModel):
    box: list[float] = Field(default_factory=list)
    part_id: str = ""
    observed: str = ""
    expected: str = ""
    source: Literal["render", "schematic"] = "render"


class PreviousRegionStatus(BaseModel):
    """C17: the critic's own word on every fault flagged in earlier rounds (read by the loop)."""
    part_id: str
    fault: str
    status: Literal["fixed", "still_wrong", "regressed"]
    note: str = ""


class Deviation(BaseModel):
    """C18: a visible, measurable deviation and whether it matters for the working principle."""
    what: str
    measured: str
    expected: str
    matters: bool
    why: str


class PartVisual(BaseModel):
    part_id: str
    visual_phrase: str
    count: int = 1
    long_axis: Literal["horizontal", "vertical", "any"] = "any"
    size_vs: str = ""
    size_ratio: float = 0.0
    touches: list[str] = Field(default_factory=list)
    note: str = ""


class PartMap(BaseModel):
    parts: list[PartVisual] = Field(default_factory=list)


class DesignerEval(BaseModel):
    pixel_description: str = ""
    regions: list[EvalRegion] = Field(default_factory=list)
    previous_regions: list[PreviousRegionStatus] = Field(default_factory=list)
    comparison_with_previous: str = ""
    deviations: list[Deviation] = Field(default_factory=list)
    s1_faithful: bool
    s1_differences: str = ""
    s2_flaw: bool = False
    s2_feedback: str = ""
    notes: str = ""


class LessonCandidate(BaseModel):
    text: str
    category: Literal["process", "prompts", "tools", "image_model"]
    structural: bool
    evidence: str = ""


class Lessons(BaseModel):
    candidates: list[LessonCandidate] = Field(default_factory=list)


class Problem(BaseModel):
    title: str
    statement: str
    constraints: list[str] = Field(default_factory=list)
    criteria: list[str] = Field(default_factory=list)
    attachments: list[str] = Field(default_factory=list)


class InspirationPick(BaseModel):
    archive_id: str
    why_useful: str


class Inspirations(BaseModel):
    picks: list[InspirationPick] = Field(default_factory=list)


class LabelCheck(BaseModel):
    """16a: labels the checker judged to point at the wrong part (code removes them)."""
    wrong_labels: list[str] = Field(default_factory=list)
    note: str = ""


class LightCheck(BaseModel):
    ok: bool
    reason: str = ""


class ProblemSet(BaseModel):
    problems: list[Problem] = Field(default_factory=list)


# ---------------------------------------------------------------- strict schema
def _inline_refs(node: Any, defs: dict[str, Any], depth: int, seen: frozenset[str]) -> Any:
    # depth counts schema-object nesting (properties/items/combinators), not dict keys
    if depth > 10:
        raise ValueError("schema depth exceeds 10")
    if isinstance(node, dict):
        if "$ref" in node:
            ref = str(node["$ref"])
            name = ref.rsplit("/", 1)[-1]
            if name in seen:
                raise ValueError(f"recursive $ref not allowed: {name}")
            target = defs.get(name)
            if target is None:
                raise ValueError(f"unresolvable $ref: {ref}")
            return _inline_refs(copy.deepcopy(target), defs, depth + 1, seen | {name})
        out: dict[str, Any] = {}
        for key, value in node.items():
            if key == "properties" and isinstance(value, dict):
                out[key] = {pk: _inline_refs(pv, defs, depth + 1, seen) for pk, pv in value.items()}
            elif key in ("items", "additionalProperties") and isinstance(value, (dict, list)):
                out[key] = _inline_refs(value, defs, depth + 1, seen)
            elif key in ("anyOf", "allOf", "oneOf") and isinstance(value, list):
                out[key] = [_inline_refs(v, defs, depth + 1, seen) for v in value]
            else:
                out[key] = _inline_refs(value, defs, depth, seen)
        return out
    if isinstance(node, list):
        return [_inline_refs(v, defs, depth, seen) for v in node]
    return node


def _strictify(node: Any) -> Any:
    if isinstance(node, dict):
        out: dict[str, Any] = {}
        for key, value in node.items():
            if key in ("allOf", "oneOf"):
                raise ValueError(f"strict schema forbids {key}")
            if key in ("$defs", "definitions"):
                continue
            out[key] = _strictify(value)
        if out.get("type") == "object" or "properties" in out:
            props = out.get("properties", {})
            out["additionalProperties"] = False
            out["required"] = sorted(props.keys())
            if "properties" not in out:
                out["properties"] = {}
        return out
    if isinstance(node, list):
        return [_strictify(v) for v in node]
    return node


def make_strict_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Pydantic JSON schema -> Meta strict JSON schema (spec §9 rules)."""
    raw = model.model_json_schema()
    defs: dict[str, Any] = dict(raw.get("$defs", {}))
    inlined = _inline_refs(raw, defs, 0, frozenset())
    strict = _strictify(inlined)
    if not isinstance(strict, dict) or strict.get("type") != "object":
        raise ValueError("strict schema root must be a plain object")
    for banned in ("anyOf", "oneOf", "allOf", "enum", "not"):
        if banned in strict:
            raise ValueError(f"strict schema root must not contain {banned}")
    return strict
