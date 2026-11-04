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
- run 20261103-201825_small-wind-turbine-for-a-wind-tunnel-com (Maya — Aerodynamics & Rotor Lead): Helped. Maya E9 used it to compute A=0.126 m2 for D=40 cm, fit with 2.5 cm clearance per side in 45 cm cube E9+E10, Re75 50271 at 5 m/s to 110597 at 11 m/s E9, and shaft power 2.9W to 30.8W at Cp0.30. It directly fed rpm checks E22 2890 rpm at 11 m/s TSR5.5 and E23 1310 rpm at 5 m/s used in decisive choice F1->C1 and still cited in solution.
- run 20261103-170525_small-wind-turbine-for-a-wind-tunnel-com (Aero — Rotor Aerodynamics Lead): Helped - sized operating-range shaft power and speed for 40cm rotor decision F1.
