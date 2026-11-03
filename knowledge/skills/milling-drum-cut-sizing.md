---
name: milling-drum-cut-sizing
description: Use when sizing any transverse milling drum shallow soil cut for power and traction margin.
source: run 20261103-152604_lunar-regolith-excavation-robot (2026-11-03)
---

1. Compute volumetric cut rate Q = width x depth x advance speed. Check units to cm3/s. Typical: 0.3 m wide x 25 mm deep x 0.02 m/s advance = 150 cm3/s (E15).
2. Estimate mechanical cutting power P = specific energy u x Q. Use u ~0.45 J/cm3 for loose simulant/soil trenching. Typical: 0.45 x 150 = 67.5 W (E31).
3. Derive tangential drum force Ft = P / tip speed v_tip. Use v_tip ~1 m/s for small drum. Typical: 67.5 W / 1 m/s = 67.5 N (E34).
4. Check thrust margin: Ft plus rolling drag must stay well below available traction W*tan(phi). Typical: 67.5 N cut << 749 N traction from 893 N loaded weight (E24, E27, E34).
5. Check power chain: drum + tracks + lift must fit mission energy and battery. Typical mission ~1.56e5 J / 43.3 Wh (E28, E29).

## Use notes
