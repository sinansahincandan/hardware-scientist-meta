---
name: sealed-battery-bay-thermal-sizing
description: Use when sizing a sealed under-belly LiFePO4 bay that must reject heat by conduction through fines and dust without ventilation.
source: run 20261104-121345_lunar-regolith-excavation-robot (2026-11-04)
---

1. Define electrical window: nameplate 24V 20Ah 480Wh (P6) with 20-80% SoC usable window = 288 Wh usable (E44), average 150W load (E46).
2. Compute runtime: usable Wh / avg load = 288Wh /150W =1.92 h (E46,E53) and verify against sortie requirement; no facility power during sortie (E34).
3. Size thermal path: sealed aluminium bay with finned heat spreader and labyrinth seals to conduct to chassis/air, keep cells within LiFePO4 limits per thermal guides (E36,E37).
4. Check dust vs cooling trade: sealed vs vented; verify mass 55kg under 60kg limit (E13,E54) includes bay (P6 245-275mm class).
5. Typical values: usable 60% of nameplate (E44); 150W mixed load runtime ~1.9h (E46); conduction-only cooling required for IP5X (E32).

## Use notes
- run 20261104-123502_lunar-regolith-excavation-robot (Dr. Priya Sharma — Power, Sensing & Remote Autonomy): Helped - sized conduction path for sealed under-belly LiFePO4 bay without ventilation. E91/E101 3mm Al plate R=0.000278 K/W on 0.06m2, E102 1mm 3 W/mK filler R=0.00556 K/W, E103 gasket, E104 total stack, combined with E58 thermal check to produce decisive choice thermal result 21.3K rise to 41.3C <45C limit with 0.12m2 Al spreader.
