---
name: turbine-gust-load-check
description: Use when checking any small wind turbine support for survival thrust and bending in gust wind.
source: run 20261102-214943_small-wind-turbine-for-a-wind-tunnel-com (2026-11-02)
---

1. Compute survival thrust from disc: T ~ 0.5*rho*A*V_gust^2*C_T or momentum estimate.
2. Compute overturning moment M = T*L_hub_to_mount for mount and clamp sizing.
3. Check support tube/frame bending stress sigma = M*c/I against yield with margin.
4. Verify tail and yaw parts stay inside envelope under deflection.

Typical: gust at 22 m/s gives thrust 36.1 N (E11) to 45.1 N verification (E19); moment 13.5 N-m at mount (E20); chassis tube stress 3.64 MPa passes 6061-T6 (E21, E13).

## Use notes
- run 20261103-105038_small-wind-turbine-for-a-wind-tunnel-com (Aero-Rotor Designer): Helped: provided survival thrust method checked against disc-area dynamic pressure for post mount.
- run 20261103-170525_small-wind-turbine-for-a-wind-tunnel-com (Aero — Rotor Aerodynamics Lead): Helped - quantified 22m/s survival thrust and post moment driving spine/post and yaw-out.
