---
name: phase-short-brake-sizing
description: Use when stopping any small direct-drive brushless generator in seconds by shorting phases on power loss.
source: run 20261103-224916_small-wind-turbine-for-a-wind-tunnel-com (2026-11-03)
---

1. Estimate spinning kinetic energy from inertia and top speed: e.g., ~87 J rotor store (E59), ~218 J total with aero drive (E44).
2. Measure phase-plus-switch resistance R; predict short performance by test/simulation: e.g., R=0.25 ohm gives t10=1.34 s vs R=0.75 ohm gives t10=30 s (E51); 2-ohm dump gives tau=8.71 s t10=20.1 s and fails 10 s (E44).
3. Predict peak electrical stress at top speed: e.g., Vpk~10 V (E44), Ipk~39.6 A Ppk~392 W for 0.25-ohm short (E51).
4. Size shorting switch so continuous rating covers pulse: e.g., 47 A MOSFET (E61) > 39.6 A pulse (E51).
5. Check winding heating from dissipated energy: e.g., 79.2 J gives ~4.11 C rise (E51, E52) — accept if < insulation limit.
6. Bench-verify speed <10% within 10 s and latched parked: e.g., 1.34 s passes (E51); add spring pad for park hold after electrical stop.

## Use notes
