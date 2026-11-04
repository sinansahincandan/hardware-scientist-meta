---
name: pitch-plus-dump-gust-shedding
description: When coordinating collective pitch-to-feather and electrical dump to survive gusts above rated wind while limiting thrust.
source: run 20261103-201825_small-wind-turbine-for-a-wind-tunnel-com (2026-11-03)
---

1. Define rated and survival winds: example rated 11 m/s power 30.8W at Cp0.30 E9, survival/gust 22 m/s E14 E16.
2. Compute baseline survival thrust: T = 0.5*rho*A*V^2*Ct. Example A=0.126 m2 E9, Ct1.0 T=37.3N Ct1.3 T=48.4N at 22 m/s E16; size post for worst Ct then plan reduction.
3. Size pitch-to-feather 0-90 deg micro-servo in hub plus passive stall tip E-concept to spill power above 11 m/s and reduce Ct from 1.3 toward 1.0 after pitch.
4. Size dump resistor 2-3 ohm 100W E18 E19 to absorb excess electrical power, coordinated with pitch at same Hall 3180 rpm threshold E-concept; verify resistor thermal peak 32.2W E28 can be sunk without softening PETG nacelle E-assumed-constraint.
5. Verify fail-safe if pitch power lost: dump alone must still meet brake time per dynamic-brake sizing (R2-3 ohm t10 ~5s E28) and structural post SF remains >9 at Ct1.3 E16.

## Use notes
