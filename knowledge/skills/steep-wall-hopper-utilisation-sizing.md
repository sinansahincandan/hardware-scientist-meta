---
name: steep-wall-hopper-utilisation-sizing
description: Use when sizing a steep-wall sealed carry hopper where wall angle reduces usable volume below bounding-box volume for a target bulk payload.
source: run 20261103-201819_lunar-regolith-excavation-robot (2026-11-03)
---

1. Compute bounding-box volume: L*W*H - e.g., L180 x W380 x H250 mm =0.0171 m3 =1.71e7 mm3 [E17][E32][E37][E40]
2. Apply utilisation factor for wall angle: effective volume = bbox * utilisation - e.g., 32% at 50 deg walls => 0.00547 m3 =5.47e6 mm3 [E23][E42]
3. Compare to required payload volume: e.g., 16 L =0.016 m3; note prior oversize bbox 0.0504 m3 exceeded station by 220 mm (110%) vs new 0.0171 m3 fits [E18][E19]
4. Check station-interval fit: hopper length vs allocated interval - e.g., 180 mm in 200 mm interval occupancy 0.9 with 20 mm margin [E24][E41]
5. Check gravity discharge: wall angle > peak friction angle of bulk solid - e.g., 50 deg walls > BP-1 friction 39-51 deg [E1][E15]
6. Check payload mass if needed: mass = effective volume * bulk density - e.g., use 1.4 t/m3 => 0.0224 t scale factor [E20]

## Use notes
