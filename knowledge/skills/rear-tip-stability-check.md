---
name: rear-tip-stability-check
description: Use when checking any rear-tip dump body for tip-over about rear axle.
source: run 20261102-214939_lunar-regolith-excavation-robot (2026-11-02)
---

1. Sum dry mass and payload CG positions (e.g., 52 kg dry budget [E34] + 30 kg soil in 20 L [E18]).
2. Take moments about rear tip pivot/axle for worst case soil behind axle.
3. Compute overturn ratio = overturning moment / restoring moment (e.g., 0.288 worst case [E42]).
4. Check safety factor = restoring / overturning >2.0 for dump (e.g., 2.02 dry vs soil moment [E43]).
5. If fails, move battery/low mass forward, limit tip angle, or shorten overhang.

## Use notes
