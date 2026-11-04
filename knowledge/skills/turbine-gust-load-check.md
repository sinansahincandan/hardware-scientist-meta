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
- run 20261103-201825_small-wind-turbine-for-a-wind-tunnel-com (Jonas — Structures & Integration Lead): Helped. Jonas E14/E16 used it to compute survival thrust Tcalc 37.3 N Ct1.0 to 48.4 N Ct1.3 at 22 m/s E16, moment M=14.9-19.4 Nm at L=0.5m (corrected to L=0.4m M=19.4 Nm E31), bending sigma 19.3-25.1 MPa on 25mm OD x 2mm wall 6061-T6 post E16, SF 12.4 to 9.5 vs 240 MPa yield E11/E12/E16. Verified stacked fore-aft length 350 mm within 450 mm cube E16/E17 and adopted for structural sizing in F4.
- run 20261103-170525_small-wind-turbine-for-a-wind-tunnel-com (Aero — Rotor Aerodynamics Lead): Helped - quantified 22m/s survival thrust and post moment driving spine/post and yaw-out.
