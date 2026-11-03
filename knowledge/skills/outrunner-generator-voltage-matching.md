---
name: outrunner-generator-voltage-matching
description: Use when matching a direct-drive brushless outrunner as generator to a small rotor for safe voltage over speed range.
source: run 20261103-105038_small-wind-turbine-for-a-wind-tunnel-com (2026-11-03)
---

1. Get rotor shaft speed range from rotor sim over operating winds (e.g., 2626 rpm at 11 m/s, omega 275 rad/s (E9)).
2. Pick direct-drive outrunner Kv for touch-safe volts (e.g., 220 Kv (E23)).
3. Predict open-circuit volts Voc = rpm / Kv: check top-wind Voc near 12 V (e.g., 11.9 V (E23)) and low-wind Voc for start-up (e.g., 5.43 V at 5 m/s (E24)).
4. Estimate shaft power P = T*omega (e.g., 33 W (E25)) then subtract 3-phase bridge loss 2*Vf*I (e.g., 3.3 W at 3 A (E44)) to get net before DC-DC (e.g., 21.4 W (E47)) and size buck-boost for ~2:1 Voc swing.
5. Check dump-resistor brake power V^2/R (e.g., 70.8 W at 2 ohm 11.9 V (E33), 47.2 W at 3 ohm (E48)) and current V/R against yaw slip-ring limit (e.g., 3.97 A vs 4 A limit (E50)(E18)).

## Use notes
