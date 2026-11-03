---
name: small-rotor-power-sizing
description: Use when sizing any sub-meter wind rotor for shaft power and speed over an operating wind range.
source: run 20261102-214943_small-wind-turbine-for-a-wind-tunnel-com (2026-11-02)
---

1. Compute available wind power P = 0.5*rho*A*V^3 for rotor disc area A at operating winds.
2. Apply realistic small-rotor Cp ~0.3-0.35 to get shaft power Pshaft = Cp*P and check vs electrical target.
3. Pick tip-speed ratio TSR ~6 for 3 blades, compute omega = TSR*V/R and rpm = omega*60/2pi for generator matching.
4. Check cut-in to rated span for torque = Pshaft/omega.

Typical: 44 cm rotor gives 124 W available at 11 m/s (E7, E30); Cp 0.35 gives 43.4 W shaft (E10); TSR 6 gives 300 rad/s (E29, E38) = 2.86e+03 rpm (E39); shaft torque ~0.145 N-m at 11 m/s (E37).

## Use notes
- run 20261103-105038_small-wind-turbine-for-a-wind-tunnel-com (Aero-Rotor Designer): Helped: framed rotor capture calc and delivered operating speed and survival loads used for selection.
