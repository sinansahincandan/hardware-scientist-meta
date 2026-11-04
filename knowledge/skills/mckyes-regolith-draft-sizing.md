---
name: mckyes-regolith-draft-sizing
description: Use when estimating shallow-cut draft and power for a bucket, blade or drum in cohesive BP-1 lunar simulant with McKyes/Reece model.
source: run 20261104-123502_lunar-regolith-excavation-robot (2026-11-04)
---

1. Define cut: depth d=15-30mm, width w per drum ~0.4m, speed v=0.05-0.08 m/s, bulk gamma and phi from simulant [E17,E21,E22]
2. Calculate gamma term: F_gamma = gamma*d*w*d*N_gamma factor; check ~16.4 N per 0.4m width at d=30mm [E81,E23]
3. Calculate cohesion term: F_c = c * d * w * N_c; check per blade 0.012 kPa·m² at c=0.5kPa [E86], 0.024 kPa·m² at c=1kPa [E82], 0.12 kPa·m² at c=5kPa [E85]
4. Sum twin drums: F_twin = 2*(F_gamma+F_c); verify 80.8 N at c=1kPa [E83] vs 33.2 N simplified [E51] and 273 N paste case at c=5kPa requiring depth limit [open_question]
5. Check traction margin: T_avail = c*A + W*tan(phi) ~573 N [E69] must exceed F_twin + grade; verify factor 2.9 vs 235 N mu traction [decisive_choices] and T_req 199 N slope+draft [E71]
6. Power: P_impl = F_twin*v / eta ; check ~10.8 W at 80N 0.08m/s 0.6 eff [E84] and 420W peak with traction [E52]; limit d to 15-30mm if F_c pushes >100N/side

## Use notes
