---
name: carrier-gap-stability-check
description: Use when sizing a rigid carrier/backing that defines a sub-millimetre capacitive gap under fingertip grip loads.
source: run 20261104-123505_tactile-fingertip-sensor-for-robot-hands (2026-11-04)
---

1. Define proof/grip load case: 10N nominal grip, 30N max grip, 90N proof peel [E35,E37] reacting through dovetail mount.
2. Model carrier as plate/cantilever with material E and second moment: compute stiffness kN/mm [E37 stiffness 26.1 kN/mm] and deflection delta under load.
3. Check delta < allowable fraction of gap: e.g. <5um for 0.5mm gap [E38,E39] to keep C0 calibration; if delta 384um cantilever [E38] or 61.7um Al 1mm fails, go to supported plate.
4. Reduce overhang to ~2mm and/or increase thickness/material to achieve delta << gap: supported plate sag 15.5um at 30N [E39] vs 93.8kPa mount pressure [E36] passes if fully supported [E39].
5. Verify screw stress << proof: 9.9 MPa vs 640 MPa for 2x M1.6 [E37] with capacity 2.56kN [E35].
Typical values: gap 0.5mm C0 39.8fF [E19], allowable <5um [E38], stack 2.8mm vs 13mm envelope [E56], plate sag 15.5um supported vs 384um cantilever [E38,E39].

## Use notes
