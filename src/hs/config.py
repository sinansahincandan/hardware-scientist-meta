"""Caps, per-role model configuration, prices (spec §7, §9).

Every role has one RoleConfig entry: switch a role to another model or a
higher reasoning effort here only — no code changes elsewhere.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RoleConfig:
    model: str
    effort: str  # minimal | low | medium | high | xhigh | max
    max_output_tokens: int


DEFAULT_MODEL = "muse-spark-1.3"
IMAGE_MODEL = "muse-image-1.0"
SAM_MODEL = "sam-3.1"

ROLES: dict[str, RoleConfig] = {
    "member": RoleConfig(DEFAULT_MODEL, "medium", 8000),
    "manager": RoleConfig(DEFAULT_MODEL, "medium", 8000),
    "secretary": RoleConfig(DEFAULT_MODEL, "high", 16000),
    "prior_art": RoleConfig(DEFAULT_MODEL, "low", 4000),
    "evaluator": RoleConfig(DEFAULT_MODEL, "high", 12000),
    "manager_inspirations": RoleConfig(DEFAULT_MODEL, "low", 2000),
    "manager_gradients": RoleConfig(DEFAULT_MODEL, "high", 12000),
    "manager_output_gradient": RoleConfig(DEFAULT_MODEL, "high", 6000),
    "vlm_prompt_gradient": RoleConfig(DEFAULT_MODEL, "high", 6000),
    "optimizer": RoleConfig(DEFAULT_MODEL, "medium", 8000),
    "schematic": RoleConfig(DEFAULT_MODEL, "low", 8000),
    "vlm_writer": RoleConfig(DEFAULT_MODEL, "high", 12000),  # 4000 left no room after high-effort reasoning (empty reply, run 121014 redraw)
    "localization": RoleConfig(DEFAULT_MODEL, "low", 4000),
    "part_map": RoleConfig(DEFAULT_MODEL, "low", 4000),
    "sam_phrases": RoleConfig(DEFAULT_MODEL, "low", 4000),
    "mask_check": RoleConfig(DEFAULT_MODEL, "low", 3000),
    "designer_eval": RoleConfig(DEFAULT_MODEL, "high", 8000),
    "progress_check": RoleConfig(DEFAULT_MODEL, "high", 4000),
    "light_check": RoleConfig(DEFAULT_MODEL, "low", 2000),
    "lessons": RoleConfig(DEFAULT_MODEL, "low", 4000),
    "insights": RoleConfig(DEFAULT_MODEL, "medium", 6000),
    "skills": RoleConfig(DEFAULT_MODEL, "medium", 8000),
    "example_generator": RoleConfig(DEFAULT_MODEL, "medium", 8000),
    "master_rev0": RoleConfig(DEFAULT_MODEL, "medium", 8000),
}

# Hard caps (spec §7), overridable by CLI flags via Controller overrides.
MAX_A_ITERS = 8
MAX_S1_ROUNDS = 3
MAX_B_RETURNS = 2
MIN_CYCLES = 2
MAX_CYCLES = 4
MAX_TOOL_CALLS_PER_TURN = 10  # owner 2026-11-03: members must be able to compute and simulate
MAX_WHITEBOARD_CALLS_PER_TURN = 8
# the chief designer selects one concept per function (4-8), writes the proposal and closes in one turn
MAX_CHIEF_WHITEBOARD_CALLS_PER_TURN = 16
MAX_NEW_TOOLS = 2
MAX_MANAGER_NEW_TOOLS = 2
MAX_FIGURE_IMAGES = 10  # round 4: up to 5 fabrication steps, each with one redraw
MAX_COST_USD_PER_RUN = 15.00
# Round-3 budget (item 0): one project-wide ledger of real Meta spend, checked before
# every call. $55 hard cap for round 3 (dashboard showed $67 credit on 2026-11-02).
# Fake mode never touches it. HS_BUDGET_LEDGER overrides the path (tests).
MAX_TOTAL_SPEND_USD = 150.0  # owner 2026-11-04 13:55: raised from $136 for round 6 (reruns of six problems, turbine redraw)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUDGET_LEDGER_PATH = Path(os.environ.get("HS_BUDGET_LEDGER", PROJECT_ROOT / "budget" / "ledger.jsonl"))

IMAGE_BACKEND = "edits"  # "edits" | "responses" (fallback, spec §5.3)

# Prices: USD per 1M tokens unless noted. Verified against https://dev.meta.ai/docs/pricing-rate-limits
# on 2026-11-02 (muse-spark-1.3 standard mode; web search grounding; muse-image-1.0 flat per image;
# sam-3.1 image segmentation $2.50 per 1,000 images).
PRICES = {
    "input_per_1m": 1.25,
    "cached_input_per_1m": 0.15,
    "output_per_1m": 4.25,
    "web_search_per_query": 2.50 / 1000.0,
    "image_each": 0.01,
    "sam_image_each": 2.50 / 1000.0,
}

FIXED_CRITERIA = [
    "The concept must work physically (no violated conservation law, load path, or signal path).",
    "The concept must be buildable with purchasable parts and ordinary lab/shop methods.",
]

# A5: who integrates the proposal, and when. Part of rev 0's §4 (the optimizer may revise it later).
PROPOSAL_RULE = (
    "Roles: the members advise; the Manager is the chief designer and decides. The Manager writes the function "
    "structure at the start, selects one concept per function with a written comparison, checks the interfaces "
    "between the selected concepts, writes the proposal and closes the meeting when it is settled. Members do not "
    "write proposals: they post concepts and evidence, raise objections, and give a readiness opinion (vote) with "
    "their reason on each proposal version; the Manager answers every opinion."
)

DEFAULT_PROTOCOL = (
    "Cycle 1: the Manager opens with the function structure (verb + noun functions with what flows in and out). "
    "Every member first searches for the best existing solutions to this problem in their own field (competition "
    "winners, products, papers) and posts each as a concept for the function it serves, with its source. "
    "Every member then posts, for EVERY function, at least one concept from their own field (add_concept), or says "
    "in one line that their field has none for it; a member who sees a missing function adds it. A concept is a "
    "way to perform the function (a working principle and the part that does it), so concepts for one function "
    "are alternatives to choose between; a requirement, check or control rule your field puts on someone else's "
    "concept is advice: say it in your message or raise it as an objection, not as a concept. Search the "
    "literature, standards and datasheets of your field and post first order-of-magnitude estimates as evidence. "
    "Cycles 2+: develop and test your own concepts with evidence before adopting another member's; for the "
    "functions the Manager names weakest, bring one concept by analogy from a distant field and write how it maps "
    "onto this problem (drop it if it does not map); attack and defend with evidence, raise and resolve objections; "
    "give your readiness opinion on each proposal version, ready only when it survives your strongest objection. "
    "A behaviour over time (stopping, tipping, heating, deflecting, filling) is shown with simulate, not asserted; "
    "a sum of parts names every term. "
    "This is concept design: what calculation, simulation and sources can settle is settled in the meeting; a test "
    "that needs built hardware cannot be done here, so name it as a bench test and judge readiness on the evidence. "
    "Missing constraints are established from standards, literature or datasheets via web_search and posted "
    "as concepts tagged assumed_constraint, citing the search evidence. A source may be cited only when it is "
    "on the whiteboard as search evidence. "
    "Speaking rule: plain words first, then only the numbers that decide the point, with units and at most "
    "three significant figures; one point per short paragraph, at most three points; an id never stands alone "
    "(write 'the tri-star wheel cluster (C1)', not 'C1'); define every abbreviation on first use; address "
    "other members only by their names; talk only about the device. "
    "Check every key result against everyday scales and known regimes (accelerations in g, sizes against a "
    "person or a door, loads against body weights, energies against daily household use) before relying on it. "
    "Read existing evidence before computing and reuse it by id unless you state why you recompute. "
    "Post a labeled sketch when proposing or changing a concept whose geometry, mechanism or flow "
    "path matters. The Manager speaks first in the meeting and last in every cycle. "
    + PROPOSAL_RULE
)
