---
name: fixed-pitch-dump-disc-stop
description: Use when stopping a fixed-pitch sub-meter wind rotor with combined dump plus spring-applied disc to meet timed stop and parked hold.
source: run 20261104-121014_small-wind-turbine-for-a-wind-tunnel-com (2026-11-04)
---

1. Get operating and survival speeds: e.g. 3150 rpm at 11 m/s TSR6 (E13), 1430 rpm at 5 m/s (E14), 10% target 315 rpm (E75).
2. Simulate dump-only stop at survival wind and check cross time vs 10 s rule (E41): e.g. dump-only ran away to 9123 rpm vs <315 rpm target, electric 0.155 N-m vs aero 0.48 N-m -> FAIL (E48).
3. Size spring-applied disc for combined stop: e.g. 0.80 N-m disc + 4 ohm dump crossed 315 rpm in 0.673 s vs 1.65 s with smaller brake (E70)(E47) and held 0 rpm at 10 s.
4. Check parked hold margins: hold / aero >1.5 and hold / factored >1.0, e.g. 1.67 vs 0.48 N-m and 1.11 vs 0.72 N-m factored (E70)(E54).
5. Check dump rating at corrected top volts: e.g. 85.6 W at 18.5 V on 4 ohm (E78), 51.1 W at higher volts (E39).

## Use notes
