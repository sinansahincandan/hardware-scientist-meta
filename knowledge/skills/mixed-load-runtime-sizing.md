---
name: mixed-load-runtime-sizing
description: Use when sizing any battery pack for mixed digging and driving duty runtime.
source: run 20261103-105032_lunar-regolith-excavation-robot (2026-11-03)
---

1. Roll up dry mass vs limit including doors/shaker - e.g. 46.8 kg (E22) revised 48.3 kg vs 60 kg limit + 18 kg soil payload (E9, E44).
2. Sum mixed base + digging + vibration loads - e.g. 350 W base (E23) + 30 W vibrator = 380 W mixed load (E39, E45, E46).
3. Compute runtime = pack energy / mixed load - e.g. 256 Wh / 350 W = 43.9 min (E23) (0.731 Wh/W) (E38), revised 40.4 min at 380 W (E46).
4. Check: runtime meets work target (~40.4 min work statement) with low ballast placement retained.

## Use notes
