---
name: pir-chamber-heat-leak-sizing
description: Use when checking transmission load for any 100 mm PIR/XPS cold chamber to electric holding energy.
source: run 20261104-123515_off-grid-solar-powered-cold-storage-for- (2026-11-04)
---

1. Get wall U from lambda/thickness: 100 mm PIR -> U 0.22-0.25 W/m2K E25, E22, E30, E32.
2. Compute skin area: e.g. 2.5x1.6x2.0 m interior + panels -> ~25.6 m2 E53-derived.
3. Transmission power = U x A x dT: 0.22 x 25.6 x 39 K =220 W E26, E48.
4. Daily thermal = P x 24 h: 5.27 kWh/day E28, E49.
5. Convert to electric via compressor COP 2.2-2.5 at 4C evap/43C cond: 5.27/2.5 =2.11 kWh/day E50, E23, E24.
6. Add respiration: ~30 W/t average -> 0.72 kWh/day thermal E51 -> 0.288 kWh electric E52; sum + infiltration/door + safety -> ~3.56 kWh/day total holding E53.
7. Cross-check against PV/battery: night 14 h x 150 W =2.10 kWh E15 requires battery usable >2.1 kWh E17.

## Use notes
