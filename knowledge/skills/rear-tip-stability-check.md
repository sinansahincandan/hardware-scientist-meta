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
- run 20261104-121345_lunar-regolith-excavation-robot (Prof. James Okoro — Mobility & Excavation Systems Specialist): Helped. Used to verify 55deg rear-pivot dump does not tip. Restoring moment 243 Nm (E51) vs overturning moment 49.1 Nm for 20kg at 0.25m behind axle (E52) = 4.95x margin (E55). Directly supported decisive choice F4 vs C13/C26.
