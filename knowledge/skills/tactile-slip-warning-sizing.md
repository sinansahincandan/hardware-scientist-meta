---
name: tactile-slip-warning-sizing
description: Use when flagging incipient translational or rotational slip from distributed stick ratio before gross slide.
source: run 20261103-194701_tactile-fingertip-sensor-for-robot-hands (2026-11-03)
---

1. Estimate Coulomb limit shear_max = mu * normal, e.g., 0.45 N shear at 1 N grip [E38] using distributed Coulomb model [E29].
2. Compute per-taxel shear/normal and stick ratio = sticking taxels / total: stable = 1.0, incipient slip = 0.375 [E39].
3. Set warning threshold at 0.5 stick ratio with stick vs slipping shading [E40] to flag before gross slide.
4. Check detect-to-act fits fall budget: e.g., 2 mm drop allows 20.2 ms [E46].
5. Cover 15000:1 force range so slip metric works from 1 mN to 15 N: needs 13.9 bits [E39].

## Use notes
