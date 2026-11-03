---
name: scraper-cut-traction-sizing
description: Use when sizing any drag scraper or plane blade cut depth so cutting force stays below wheeled traction.
source: run 20261102-214939_lunar-regolith-excavation-robot (2026-11-02)
---

1. Get soil bulk density and reference cut force at reference depth and width (e.g., 1.5 g/cc [E2,E3], 275 N at 40 mm depth [E17,E39]).
2. Scale cut force linearly with depth and width for shallow slices: F2 = F1*(d2/d1)*(w2/w1) (e.g., 172 N at 25 mm x 400 mm [E39]).
3. Compute available drawbar traction as mu * loaded weight (e.g., mu 0.6 on 82 kg loaded = 483 N [E40]).
4. Check Fcut < traction with margin >1.5 and dig-force/weight <0.5 (e.g., 172/483, ratio 0.458 [E19]).
5. If fails, shallow depth (e.g., 25 mm to 10 mm) or widen wheels to raise traction.
6. Size drive from Fcut + rolling: torque per wheel (e.g., 11 N-m [E41]) and cutting power P = Fcut*v (e.g., 27.5 W at 0.1 m/s [E17]).

## Use notes
- run 20261103-105032_lunar-regolith-excavation-robot (Excavation and Regolith Handling Lead): Helped - set shallow cut at 129 N and justified vibrating share to 90.3 N against 222 N traction with margin.
