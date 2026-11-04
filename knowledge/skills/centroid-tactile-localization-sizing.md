---
name: centroid-tactile-localization-sizing
description: Use when locating contact on a discrete tactile array to finer resolution than taxel pitch via centroid interpolation.
source: run 20261103-194701_tactile-fingertip-sensor-for-robot-hands (2026-11-03)
---

1. Set taxel pitch p and span: e.g., 2.5 mm pitch across 20 mm gives 8 taxels [E9].
2. Check skin spread covers pitch so centroid sees multiple taxels: require spread radius > p, e.g., 3.87 mm > 2.5 mm [E18].
3. Estimate hyperacuity ratio: interpolation gain ~0.048 of pitch [E35].
4. Predict acuity = ratio x pitch: e.g., ~0.075 mm from 2.5 mm pitch [E39].
5. Implement weighted-centroid of normal signals and verify dot location vs force vectors on map [E40].

## Use notes
