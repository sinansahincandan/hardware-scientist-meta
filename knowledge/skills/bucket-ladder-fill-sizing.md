---
name: bucket-ladder-fill-sizing
description: Use when sizing bucket-elevator fill time to reach target hopper payload.
source: run 20261104-121008_lunar-regolith-excavation-robot (2026-11-04)
---

1. Size max payload from M_max = volume * compacted bulk density (e.g., 20 L at 1500 kg/m3 = 30 kg max (E10)(E11)).
2. Select operating fill fraction for stability and spill (e.g., 15 kg = half-full (E11)).
3. Estimate fill time T = M_op / rate for each loader option (e.g., ladder to 15 kg: 112 s vs scraper to 15 kg: 450 s (E11)).
4. Verify trip rate meets throughput and power-energy budget before choosing ladder vs scraper vs kerf-plus-ladder.

## Use notes
