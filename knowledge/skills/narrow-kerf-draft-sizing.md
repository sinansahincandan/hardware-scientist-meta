---
name: narrow-kerf-draft-sizing
description: Use when sizing a narrow-slot trenching chain to fit wheeled traction and cutting power.
source: run 20261104-121008_lunar-regolith-excavation-robot (2026-11-04)
---

1. Estimate full-width shallow cut force for depth and width (e.g., 32.9 N for 0.3 m wide x 50 mm deep scraper in BP-1 (E9)).
2. Scale linearly by width to narrow kerf: F_kerf = F_full * (w_kerf / w_full) (e.g., 11 N for 100 mm kerf (E64)).
3. Check traction margin: require traction >> max(F_full, F_kerf) (e.g., 294 N traction vs 32.9 N cut = 8.9x margin (E23), ground pressure 1.56e4 Pa (E25)).
4. Compute chain cutting power P = F_kerf * chain speed (e.g., 16.4 W (E59)).
5. Compute dig energy per trip E = P * fill time for battery sizing (e.g., 0.512 unit energy for 15 kg trip (E60)).

## Use notes
