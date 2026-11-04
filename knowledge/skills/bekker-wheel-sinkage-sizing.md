---
name: bekker-wheel-sinkage-sizing
description: Use when sizing wheel diameter, width and contact length to keep sinkage and ground pressure below bearing limits on compressible regolith simulant.
source: run 20261104-123502_lunar-regolith-excavation-robot (2026-11-04)
---

1. Get Bekker parameters for BP-1: k_c, k_phi, n from Mueller 2025 pressure-sinkage tests [E64,E65,E66,E67,E2]
2. Calculate ground pressure: p = W / (n_wheels * b * l); check 7.36e3 Pa for 200mm wide 100mm contact [E13,E59], 2.45e3 Pa for 300mm dia option [E68], 1.13e4 Pa at 65mm contact [E72] vs 11.3 kPa deployed [decisive_choices]
3. Solve Bekker p = (k_c/b + k_phi)*z^n for sinkage z; verify 4-6mm sinkage at 65-70mm contact gives 11.3 kPa < 15-20 kPa foot limit [decisive_choices,E72]
4. Check traction: T_avail = c*A + W*tan(phi) =81.0+492.4=573.4 N [E69]; require T_avail > F_draft + W*sin(slope) [E71,E83]
5. Iterate b, dia, l to fit stowed 0.94x0.48x0.48m in 1.0x0.5x0.5m box deployed 0.70m track 0.80m wheelbase [E16,E70,E105] while keeping z <10mm and p < bearing

## Use notes
