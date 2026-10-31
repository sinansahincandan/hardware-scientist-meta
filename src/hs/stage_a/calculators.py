"""Vetted calculators (AUTOPILOT §7.6): small named functions next to free calc.

Each returns a dict with the result and a `provenance` map recording, for
every input, whether it came from the user, a source, or an assumption.
Units are SI unless the function name says otherwise.
"""
from __future__ import annotations

import math
from typing import Any

PROVENANCE_KINDS = ("user", "source", "assumption")


def _prov(args: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any]:
    return {k: {"value": v, "source": str(sources.get(k, "assumption"))} for k, v in args.items()}


def lever_effort(load_n: float, load_arm_m: float, effort_arm_m: float, efficiency: float = 0.9, **kw: Any) -> dict[str, Any]:
    """Effort force at the handle of a lever. F = load * la / (ea * eff)."""
    args = {"load_n": load_n, "load_arm_m": load_arm_m, "effort_arm_m": effort_arm_m, "efficiency": efficiency}
    return {"effort_n": load_n * load_arm_m / (effort_arm_m * efficiency), "unit": "N", "inputs": args}


def lead_screw_effort(axial_load_n: float, lead_mm: float, efficiency: float = 0.35, **kw: Any) -> dict[str, Any]:
    """Torque to drive a lead screw. T = F * lead / (2*pi*eff), returned in N*m."""
    args = {"axial_load_n": axial_load_n, "lead_mm": lead_mm, "efficiency": efficiency}
    torque_nmm = axial_load_n * lead_mm / (2 * math.pi * efficiency)
    return {"torque_nm": torque_nmm / 1000.0, "unit": "N*m", "inputs": args}


def cantilever_deflection(load_n: float, length_m: float, youngs_pa: float, second_moment_m4: float, **kw: Any) -> dict[str, Any]:
    """Tip deflection of an end-loaded cantilever. d = F L^3 / (3 E I), in m."""
    args = {"load_n": load_n, "length_m": length_m, "youngs_pa": youngs_pa, "second_moment_m4": second_moment_m4}
    return {"deflection_m": load_n * length_m**3 / (3 * youngs_pa * second_moment_m4), "unit": "m", "inputs": args}


def spring_mass_frequency(stiffness_n_m: float, mass_kg: float, **kw: Any) -> dict[str, Any]:
    """Natural frequency of a spring-mass system, Hz."""
    args = {"stiffness_n_m": stiffness_n_m, "mass_kg": mass_kg}
    return {"frequency_hz": math.sqrt(stiffness_n_m / mass_kg) / (2 * math.pi), "unit": "Hz", "inputs": args}


def first_order_settling(tau_s: float, settling_fraction: float = 0.02, **kw: Any) -> dict[str, Any]:
    """Time for a first-order response to settle within settling_fraction of final."""
    args = {"tau_s": tau_s, "settling_fraction": settling_fraction}
    return {"settling_s": -tau_s * math.log(settling_fraction), "unit": "s", "inputs": args}


def natural_convection_plate(delta_t_k: float, area_m2: float, characteristic_length_m: float = 0.3, **kw: Any) -> dict[str, Any]:
    """Vertical-plate natural convection in air, simplified h = 1.31*(dT/L)^0.25 W/m2K."""
    args = {"delta_t_k": delta_t_k, "area_m2": area_m2, "characteristic_length_m": characteristic_length_m}
    h = 1.31 * (delta_t_k / max(characteristic_length_m, 1e-6)) ** 0.25
    return {"h_w_m2k": h, "heat_w": h * area_m2 * delta_t_k, "unit": "W (heat_w)", "inputs": args}


def tuned_mass_damper_den_hartog(main_mass_kg: float, main_frequency_hz: float, mass_ratio: float = 0.05, **kw: Any) -> dict[str, Any]:
    """Den Hartog optimum TMD: f_opt = f/(1+mu), zeta_opt = sqrt(3mu/(8(1+mu)))."""
    args = {"main_mass_kg": main_mass_kg, "main_frequency_hz": main_frequency_hz, "mass_ratio": mass_ratio}
    mu = mass_ratio
    m_tmd = mu * main_mass_kg
    f_tmd = main_frequency_hz / (1 + mu)
    zeta = math.sqrt(3 * mu / (8 * (1 + mu)))
    k_tmd = m_tmd * (2 * math.pi * f_tmd) ** 2
    c_tmd = 2 * zeta * math.sqrt(k_tmd * m_tmd)
    return {"tmd_mass_kg": m_tmd, "tmd_frequency_hz": f_tmd, "tmd_damping_ratio": zeta,
            "tmd_stiffness_n_m": k_tmd, "tmd_damping_ns_m": c_tmd, "unit": "mixed (see keys)", "inputs": args}


VETTED: dict[str, Any] = {
    "lever_effort": lever_effort,
    "lead_screw_effort": lead_screw_effort,
    "cantilever_deflection": cantilever_deflection,
    "spring_mass_frequency": spring_mass_frequency,
    "first_order_settling": first_order_settling,
    "natural_convection_plate": natural_convection_plate,
    "tuned_mass_damper_den_hartog": tuned_mass_damper_den_hartog,
}


def run_vetted(name: str, args: dict[str, Any], input_sources: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run one vetted calculator; provenance recorded for every input."""
    fn = VETTED[name]
    clean = {k: float(v) for k, v in args.items()}
    result = fn(**clean)
    sources = input_sources or {}
    result["provenance"] = _prov(clean, {str(k): v for k, v in sources.items()})
    result["calculator"] = name
    return result
