"""AUTOPILOT §7: vetted calculators, deliverable fields, label fallback logic."""
import math

from hs.schemas import DesignerEval, SolutionPrompt, VLMPrompt, make_strict_schema
from hs.stage_a.calculators import VETTED, run_vetted


def test_vetted_calculators_known_values():
    assert set(VETTED) == {"lever_effort", "lead_screw_effort", "cantilever_deflection",
                           "spring_mass_frequency", "first_order_settling",
                           "natural_convection_plate", "tuned_mass_damper_den_hartog"}
    r = run_vetted("lever_effort", {"load_n": 100, "load_arm_m": 0.1, "effort_arm_m": 0.5, "efficiency": 1.0},
                   {"load_n": "user"})
    assert abs(r["effort_n"] - 20.0) < 1e-9
    assert r["provenance"]["load_n"]["source"] == "user"
    assert r["provenance"]["effort_arm_m"]["source"] == "assumption"
    r = run_vetted("spring_mass_frequency", {"stiffness_n_m": 1000, "mass_kg": 1})
    assert abs(r["frequency_hz"] - math.sqrt(1000) / (2 * math.pi)) < 1e-9
    r = run_vetted("tuned_mass_damper_den_hartog",
                   {"main_mass_kg": 1000, "main_frequency_hz": 2.0, "mass_ratio": 0.05})
    assert abs(r["tmd_mass_kg"] - 50.0) < 1e-9
    assert abs(r["tmd_frequency_hz"] - 2.0 / 1.05) < 1e-9


def test_new_schemas_strict_and_defaults():
    for model in (VLMPrompt, DesignerEval, SolutionPrompt):
        schema = make_strict_schema(model)
        assert schema["type"] == "object" and schema["additionalProperties"] is False


def test_vetted_calc_posts_evidence_with_provenance(tmp_path):
    from hs.stage_a.tools import ToolRunner
    from hs.stage_a.whiteboard import Whiteboard

    board = Whiteboard()
    runner = ToolRunner(board, tmp_path, tmp_path / "evidence")
    eid, out = runner.vetted_calc("Mechanics", "lever_effort",
                                  {"load_n": 588.6, "load_arm_m": 0.2, "effort_arm_m": 0.8},
                                  {"load_n": "user"}, purpose="handle effort")
    assert eid in out and board.evidence[-1].tool == "vetted_calc:lever_effort"
    assert board.evidence[-1].inputs["load_n"]["source"] == "user"
