---
name: dod-derated-battery-runtime-sizing
description: Use when converting nameplate Li-ion pack energy to usable energy via depth-of-discharge and average mixed load to verify sortie runtime.
source: run 20261103-210007_lunar-regolith-excavation-robot (2026-11-03)
---

1. Compute nameplate Wh: 6S 22.2 V * 10 Ah = 222 Wh semi-solid Li-ion E36 E38.
2. Apply usable DoD: 85% DoD -> 189 Wh usable E43 E47; retain conduction cooling tray low-CG central pack F7.
3. Divide by average mixed power: 90 W avg drive+excavation+vibration -> 2.1 h runtime E48; check 170 Wh per sortie E15 fits within 189 Wh with reserve.
4. Cross-check against dry mass limit 60 kg: pack + 13.9 kg dry estimate E44 + 48 kg payload excluded E45.
Typical values: 222 Wh nameplate E36, 189 Wh usable at 85% DoD E43 E47, 2.1 h @90W E48.

## Use notes
- run 20261104-123502_lunar-regolith-excavation-robot (Dr. Priya Sharma — Power, Sensing & Remote Autonomy): Helped - provided the quantitative energy basis for the architecture decision. E38 calculates 24V*10Ah=240 Wh nameplate, E55/E87 derates to 144 Wh at 60% DoD, and E53/E56-E58/E88-E89 convert to 0.343h at 420W peak and 0.873h at 165W avg interleaved, which is cited in F4->C14+F6->C17 choice to justify a separate sealed battery bay vs ventilated pack and 20.6 vs 52.4 min runtime.
