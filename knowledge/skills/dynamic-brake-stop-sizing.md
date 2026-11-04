---
name: dynamic-brake-stop-sizing
description: Use when sizing any generator dump-resistor brake for fail-safe stop time and park hold.
source: run 20261102-214943_small-wind-turbine-for-a-wind-tunnel-com (2026-11-02)
---

1. Select dump resistor R across generator: lower R = higher peak power and faster decay; compare 1/2/5 ohm options.
2. Estimate electrical time constant tau for R + inertia, then time to 10% speed t10 = tau*ln(10) ~2.3*tau and require <10 s.
3. Compute peak brake torque at top omega and energy into resistor to rate resistor.
4. Size friction pad normal force N = T_hold/(mu*r) to hold parked torque at survival wind.

Typical: R=1 gives 324 W peak, R=2 gives 162 W, R=5 gives 65 W (E32); 2 ohm gives tau 2.22 s (E33) and t10 5.11 s (E42, E46); peak brake torque 0.54 N-m (E47); pad needs 37.5 N for hold (E48) with 180 J into resistor (E49).

## Use notes
- run 20261103-105038_small-wind-turbine-for-a-wind-tunnel-com (Safety-Control Engineer): Helped: sized dump plus friction brake for stop time and zero-speed hold with large margin.
- run 20261103-170525_small-wind-turbine-for-a-wind-tunnel-com (Volt — Electrical Power and Safety Shutdown Lead): Helped - framed fail-safe dump-brake for 10s stop requirement and park-hold question.
- run 20261103-224916_small-wind-turbine-for-a-wind-tunnel-com (Electrical Power Engineer): Helped: quantified dump-resistor stop as too slow, forcing phase-short choice.
- run 20261104-121014_small-wind-turbine-for-a-wind-tunnel-com (Power-Systems Engineer): Helped proved dump-alone insufficient and forced combined brake.
