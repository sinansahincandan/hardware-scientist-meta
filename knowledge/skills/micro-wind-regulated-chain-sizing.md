---
name: micro-wind-regulated-chain-sizing
description: Use when sizing a rectifier plus buck-boost feed from a variable-speed micro-wind generator to a steady regulated load.
source: run 20261104-121014_small-wind-turbine-for-a-wind-tunnel-com (2026-11-04)
---

1. Get rotor speed range from TSR: e.g. 1430 rpm at 5 m/s (E14) to 3150 rpm at 11 m/s (E13).
2. Match Kv so low-wind rectified volts exceed regulator minimum and top stays below maximum: 220 Kv gave 6.5 V low below 8 V minimum (E37)(E60) while 170 Kv gave 8.41 V low and 18.5 V top inside 8-40 V (E76)(E60).
3. Apply rectifier plus buck-boost chain efficiency to shaft power: e.g. shaft 3.27 W at 5 m/s (E11) and 34.7 W at 11 m/s (E12) -> regulated 2.08 W low (E80) and 22.1 W top at 85% efficiency (E66).
4. Size dump for top volts: e.g. 4 ohm gives 51.1 W / 3.58 A (E39)(E40), revised 85.6 W at 18.5 V (E78), energy ~84.3 J in 1.65 s stop (E67).

## Use notes
