---
name: capacitive-taxel-signal-budgeting
description: Use when sizing millimeter parallel-plate tactile taxels to resolve millinewton touch with standard capacitance-to-digital converters.
source: run 20261103-170523_tactile-fingertip-sensor-for-robot-hands (2026-11-03)
---

1. Set threshold force and pitch: e.g. 1 mN touch on ~2 mm pitch array.
2. Compute threshold deflection of soft dielectric: e.g. 2.08 micron at 1 mN (E32, E31).
3. Compute base capacitance C0 from area/gap/dielectric: e.g. 2 mm taxel with 0.5 mm dielectric -> ~212 fF C0 (E16).
4. Compute threshold delta-C from dC/dgap * deflection: e.g. 0.882 fF change at 1 mN (E33).
5. Check readability: delta-C must exceed CDC femtofarad resolution and noise with margin; e.g. AD7147-class femtofarad CDC resolves sub-fF (E10, E11).
Checks: PASS if delta-C / resolution > ~2-3 and C0 within CDC input range; FAIL otherwise -> increase area, reduce gap, soften dielectric, or choose finer CDC.
Typical values: C0 ~212 fF (E16), delta-C ~0.882 fF at 2.08 micron / 1 mN (E32, E33), 8x6 pads at 2 mm pitch (E17).

## Use notes
