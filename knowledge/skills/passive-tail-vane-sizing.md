---
name: passive-tail-vane-sizing
description: Use when sizing a passive tail vane and boom to yaw-align any small upwind rotor.
source: run 20261103-105038_small-wind-turbine-for-a-wind-tunnel-com (2026-11-03)
---

1. Fit boom length plus rotor diameter inside transport envelope (e.g., 300 mm boom inside 45 cm cube (E16)).
2. Carry survival thrust moment into spine and check stress/deflection (e.g., M 13.5 Nm sigma 34.2 MPa (E43) from thrust 33.5-44.7 N (E9)).
3. Estimate vane side force at yaw angle and restoring moment M_restore = Fvane * boom (e.g., 2.3 N * 0.3 m = 0.69 Nm (E43)).
4. Check M_restore >= yaw disturbance torque with margin: pass if ratio >1.2, redesign fin if marginal (e.g., 0.69 Nm vs 0.67 Nm ratio 1.0 marginal (E43)).
5. Enlarge fin area or boom until restoring exceeds disturbance (e.g., larger fin 0.834 Nm (E49)) then re-check weathercock stability and yaw bearing friction.

## Use notes
