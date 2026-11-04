---
name: redundant-fail-safe-turbine-brake
description: When sizing any small wind turbine brake that must reach <10% speed on command or load loss without external power.
source: run 20261103-201825_small-wind-turbine-for-a-wind-tunnel-com (2026-11-03)
---

1. Define trigger threshold: 110% rated speed. Example rated 2890 rpm at 11 m/s TSR5.5 E22 -> Hall tach threshold 3180 rpm E-concept, plus electrical detection: bus voltage rate-of-rise comparator + Hall current-zero + RF OR E-concept.
2. Size primary electrical dump: compute rectified Vdc = rpm/KV (e.g. KV500 -> 5.8 Vdc at 2890 rpm E25). Choose R_dump = V^2/P for peak spill power: 6.3 ohm for 31W at 14V E25 fails 10s rule.
3. Run dynamic-brake sweep: with inertia estimate, compute tau and t_10 = ln(10)*tau E28. Require t10 <10 s. Example R=6.3 ohm t10=24.8s tau10.8s fail, R=2-3 ohm tau2.22s t10=5.11s pass to <10% (289 rpm) E28; peak power 32.2W at 2 ohm vs 10.2W at 6.3 ohm E28 -> select 100W wirewound with heatsink to 6061-T6 longerons E-assumed-constraint.
4. Add secondary park-hold: normally-closed solenoid pin on 20 mm disk on 8 mm main shaft E29, spring-engaged, with 5V 5F supercap hold-up. Verify disk clearance to bulkhead E29 and that pin holds max aero torque ~0.1 Nm E27.
5. Verify redundancy: either 3-phase MOSFET short via 2-3 ohm dump OR NC pin achieves stop; log both paths independent of mains.

## Use notes
