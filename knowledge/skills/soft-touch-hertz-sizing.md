---
name: soft-touch-hertz-sizing
description: Use when sizing any soft elastomer skin to spread millinewton touch onto a discrete sensing element.
source: run 20261102-214941_tactile-fingertip-sensor-for-robot-hands (2026-11-02)
---

1. Get elastomer modulus from Shore A (e.g., Shore 10A silicone) and fingertip/object radii.
2. Compute Hertz contact radius a for light load F: a ~ (F*R/E*)^1/3.
3. Compute mean pressure p = F/(pi*a^2) and spread area vs sensor pitch.
4. Require contact diameter to couple to at least one taxel but localize within 2 mm pitch for human-like resolution.
5. Check membrane can transmit pressure without bottoming or tearing.

Typical values: 1 mN on Shore 10A gives 0.247 mm radius (E9); 1 mN over 1 mm2 taxel gives 1 mN/mm2 pressure (E10); 2 mm pitch taxel gives 212 fF base capacitance (E18).

## Use notes
- run 20261103-194701_tactile-fingertip-sensor-for-robot-hands (Derma — Soft Skin and Contact Mechanics Owner): Helped: sized soft skin to spread 1 mN touch over multiple taxels for centroid and signal.
- run 20261104-121011_tactile-fingertip-sensor-for-robot-hands (Dr. Amara Okafor — Soft Skin Mechanics): Helped - Hertz spreading quantified 1 mN touch as 0.235 mm radius / 0.470 mm spot at 5.78 kPa on Shore A10 (E13, E14) under 2.5 mm stack (E2), directly driving F1 ridged-dome choice over optics/fluid.
