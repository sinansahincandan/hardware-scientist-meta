---
name: feather-dump-stop-sizing
description: Use when a small pitchable wind rotor must feather plus electrically brake to park below 10% speed within 10 s after overspeed or load loss.
source: run 20261104-122320_small-wind-turbine-for-a-wind-tunnel-com (2026-11-04)
---

1. Compute top-wind aero state: for 0.40 m rotor at 11 m/s with TSR~5 Cp~0.35 get Pshaft~35.9 W, 2626 rpm, torque~0.13 N-m and thrust~7.9 N (E9).
2. Set feather target and residual torque: drive collective pitch to ~80 deg feather via sliding collar servo+spring and assume residual aero torque ~5% of operating for stop simulation (E43, E27, E40).
3. Size electrical brake: select dump ~2.0 ohm 50 W plus phase-short; verify dump-only insufficient (76.7% speed remains) so feather is required (E26, E27, E38).
4. Simulate combined decay from trip speed: start from ~110% top speed ~2889 rpm / KE ~113 J and integrate feathered-residual drive vs dump+short braking (E39, E32, E40).
5. Check park criteria: demonstrate <10% top speed within 10 s - e.g., 9.9% at 4.9 s and 0.81% at 10 s - and latched hold without power (E27, E40, E32).

## Use notes
