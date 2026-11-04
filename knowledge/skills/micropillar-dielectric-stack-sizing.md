---
name: micropillar-dielectric-stack-sizing
description: Use when sizing a compressible air-gap micropillar dielectric bilayer to map 1 mN to 5 N into fF-level capacitance change.
source: run 20261103-210010_tactile-fingertip-sensor-for-robot-hands (2026-11-03)
---

1. Stack: 0.8 mm Dragon Skin 10A outer [E21] + 0.7 mm Ecoflex 00-30 [E20] micropillars 0.5 mm tall 30% fill -> effective modulus ~0.02 MPa.
2. Size Hertz spread for F=1 mN: solid 0.3 MPa gives a=0.299 mm d=0.598 mm p_mean=3.57 kPa; structured gives p_mean=0.586 kPa 0.586 mN/mm2 [E17] and d~1.47 mm patch [E8] - verify 3-6x pressure reduction.
3. Compute baseline: C0=ε0*εr*A/gap per 2.25 mm2 taxel (1.5x1.5 mm) = 39.8 fF [E19] (fix unit mm2 error [E18]).
4. Compute sensitivity: ΔC/C0 ~ compression ~2.2% -> ΔC=0.88 fF for 1 mN [E35]; check 1 mN to 5 N range stays within CDC.
5. Gate on electronics: need CDC resolution <0.05 fF and range ±4 pF to 17 pF e.g. AD7746 [E29,E30] / AD7147 [E36,E37]; require margin >20x: 0.88/0.02=44x passes, else increase fill or reduce gap.

## Use notes
- run 20261104-123505_tactile-fingertip-sensor-for-robot-hands (Dr. Kenji Tanaka — Soft Materials & Compliant Structures): Helped - Sized 1.5x1.5mm taxel, 0.5mm air-gap, C0 39.8fF to map 1mN -> 17.8um (3.6% strain) -> ΔC 0.9-1.5fF, SNR 18-30 vs 0.02-0.05fF AD7746 noise floor. Ensures detection at 1 mN without saturation to 10-30N within 13mm envelope. Evidence E19,E20,E57 decisive choice F2/C15.
