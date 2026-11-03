---
name: bulk-payload-mass-sizing
description: Use when sizing any carried bulk-solid payload mass from hopper volume and bulk density.
source: run 20261103-142845_lunar-regolith-excavation-robot (2026-11-03)
---

1. Get bulk density range for material from simulant/test data (e.g., 1.50-1.60 g/cm3 for BP-1 (E1)).
2. Set carry volume from envelope/bay (e.g., 25 L low mid-bay hopper (E16)).
3. Compute payload mass = volume x mid density (e.g., 25 L x ~1.55 g/cm3 = 38.8 kg soil (E16)).
4. Check mass budget: keep dry robot below limit and carry load low, separate counted mass (e.g., dry <60 kg limit, 38.8 kg carried low not counted (E16, E20)).
5. Check stability/CG: carry low in chassis bay and verify envelope/clearance (e.g., 1.0x0.5x0.5 m stow, 150 mm clearance (E8, E25)) and friction for transport (e.g., 39-51 deg peak friction (E10)).

## Use notes
