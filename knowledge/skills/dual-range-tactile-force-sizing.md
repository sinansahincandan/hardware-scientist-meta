---
name: dual-range-tactile-force-sizing
description: Use when one tactile array must measure millinewton touch to tens-of-newtons grip without saturation.
source: run 20261103-170523_tactile-fingertip-sensor-for-robot-hands (2026-11-03)
---

1. Define full range ratio: e.g. 1 mN light touch to 30 N grip = 30000:1, cannot fit one linear cell without saturation.
2. Allocate soft cell for low end: size pulp/dielectric so 1 mN gives readable deflection/delta-C, e.g. 2.08 micron -> 0.882 fF on 212 fF base (E32, E33, E16).
3. Allocate firm cell / second range for high end: stiffer dielectric or smaller gain so 30 N stays within gap and CDC range.
4. Define cross-over calibration map: centroid/location from soft array, force from blended soft-plus-firm map.
Checks: PASS if low-end delta-C > CDC resolution (E10, E11) AND high-end compression < solid / shorting; FAIL if single cell saturates -> add stiffness step.
Typical values: 1 mN threshold (E6), 30 N grip with 90 N proof mount margin (E43, E18), 30000:1 range.

## Use notes
- run 20261104-123505_tactile-fingertip-sensor-for-robot-hands (Dr. Kenji Tanaka — Soft Materials & Compliant Structures): Helped - Verified single array spans mN touch to tens-of-N grip without saturation: worst-case ΔC 0.9fF >30x noise 0.05fF at 1mN while 10-30N compression stays <0.5mm gap with posts preventing short. Evidence E19,E57 and F2 dual-range to 10-30N.
