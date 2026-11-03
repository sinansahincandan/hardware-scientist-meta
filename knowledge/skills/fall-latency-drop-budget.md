---
name: fall-latency-drop-budget
description: Use when sizing any detect-to-act loop that must catch a slipping or dropped object before it falls beyond tolerance.
source: run 20261102-214941_tactile-fingertip-sensor-for-robot-hands (2026-11-02)
---

1. Set allowable free-fall drop D_allow for slip/catch (e.g., 1 mm grip tolerance).
2. Convert to total time budget with d = 0.5*g*t^2 -> t_allow = sqrt(2*D_allow/g).
3. Allocate sense-to-flag plus actuation inside t_allow; keep sense-to-flag <= ~70% of budget.
4. Check fall for candidate latency with same formula and require D << D_allow.
5. If human reaction (~60 ms) used, verify it fails small tolerances before choosing machine loop.

Typical values: 14.3 ms allows only 1 mm fall (E39); 10 ms sense-to-flag gives 0.491 mm fall (E41); 64 ms window gives 20.1 mm fall and exceeds 1 mm (E27).

## Use notes
