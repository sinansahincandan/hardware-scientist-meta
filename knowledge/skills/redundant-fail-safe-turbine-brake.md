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
- run 20261103-210013_small-wind-turbine-for-a-wind-tunnel-com (Safety & Braking Engineer): Helped: DIRECT MATCH. Skill triggered for <10% speed in 10s on command/load-loss without external power. Solution C24 implements skill's dual-channel NC MOSFET + relay via 5F 5V 62.5J supercap (E15/E16/E18) to provide net 0.095 N m decel (alpha 27.2 rad/s2) for J 0.0035 kg m2 from 302 rad/s (E17) to <30 rad/s in 10s over residual aero <0.04 N m vs aero 0.408 N m at 22 m/s (E18) vs feathered thrust 7.5 N limit (E5/E6), meeting fail-safe de-energize-to-safe intent. E21 160 J rotational energy and E19/E20 checks support budget.
