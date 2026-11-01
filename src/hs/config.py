"""Caps, per-role model configuration, prices (spec §7, §9).

Every role has one RoleConfig entry: switch a role to another model or a
higher reasoning effort here only — no code changes elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoleConfig:
    model: str
    effort: str  # minimal | low | medium | high | xhigh | max
    max_output_tokens: int


DEFAULT_MODEL = "muse-spark-1.3"
IMAGE_MODEL = "muse-image-1.0"

ROLES: dict[str, RoleConfig] = {
    "member": RoleConfig(DEFAULT_MODEL, "medium", 8000),
    "secretary": RoleConfig(DEFAULT_MODEL, "high", 16000),
    "prior_art": RoleConfig(DEFAULT_MODEL, "low", 4000),
    "evaluator": RoleConfig(DEFAULT_MODEL, "high", 12000),
    "manager_inspirations": RoleConfig(DEFAULT_MODEL, "low", 2000),
    "manager_gradients": RoleConfig(DEFAULT_MODEL, "high", 12000),
    "manager_output_gradient": RoleConfig(DEFAULT_MODEL, "high", 6000),
    "vlm_prompt_gradient": RoleConfig(DEFAULT_MODEL, "high", 6000),
    "turn_check": RoleConfig(DEFAULT_MODEL, "low", 1000),
    "optimizer": RoleConfig(DEFAULT_MODEL, "medium", 8000),
    "schematic": RoleConfig(DEFAULT_MODEL, "low", 8000),
    "vlm_writer": RoleConfig(DEFAULT_MODEL, "high", 4000),
    "localization": RoleConfig(DEFAULT_MODEL, "low", 4000),
    "designer_eval": RoleConfig(DEFAULT_MODEL, "high", 8000),
    "light_check": RoleConfig(DEFAULT_MODEL, "low", 2000),
    "lessons": RoleConfig(DEFAULT_MODEL, "low", 4000),
    "example_generator": RoleConfig(DEFAULT_MODEL, "medium", 8000),
    "master_rev0": RoleConfig(DEFAULT_MODEL, "medium", 8000),
}

# Hard caps (spec §7), overridable by CLI flags via Controller overrides.
MAX_A_ITERS = 8
MAX_S1_ROUNDS = 3
MAX_B_RETURNS = 2
MIN_CYCLES = 2
MAX_CYCLES = 4
MAX_MEMBERS = 5
MAX_TOOL_CALLS_PER_TURN = 6
MAX_WHITEBOARD_CALLS_PER_TURN = 8
MAX_TURN_MESSAGE_WORDS = 250
MAX_NEW_TOOLS = 2
MAX_MANAGER_NEW_TOOLS = 2
MAX_FIGURE_IMAGES = 8
MAX_COST_USD_PER_RUN = 15.00

IMAGE_BACKEND = "edits"  # "edits" | "responses" (fallback, spec §5.3)
SKETCH_SINGLE_REQUEST = True  # §14.3 fallback switch

# Prices (spec §9). USD per 1M tokens unless noted.
PRICES = {
    "input_per_1m": 1.25,
    "cached_input_per_1m": 0.15,
    "output_per_1m": 4.25,
    "web_search_per_query": 2.50 / 1000.0,
    "image_each": 0.01,
}

FIXED_CRITERIA = [
    "The concept must work physically (no violated conservation law, load path, or signal path).",
    "The concept must be buildable with purchasable parts and ordinary lab/shop methods.",
]

DEFAULT_PROTOCOL = (
    "Cycle 1: decompose the problem into functions, propose concepts per function "
    "(distant cross-domain analogies welcome), post first order-of-magnitude estimates as evidence. "
    "Cycles 2+: attack and defend with evidence, raise and resolve objections, integrate a proposal, "
    "vote ready only when the proposal survives your strongest objection. "
    "Missing constraints are established from standards, literature or datasheets via web_search "
    "and posted as concepts tagged assumed_constraint with the source as evidence."
)
