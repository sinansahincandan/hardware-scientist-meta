---
name: cube-constrained-turbine-packaging
description: When packaging any rotor, nacelle and tower inside a cubic envelope (e.g. Collegiate Wind Competition) check diameter, stacked length and clearances together.
source: run 20261103-201825_small-wind-turbine-for-a-wind-tunnel-com (2026-11-03)
---

1. Size rotor diameter D for power: D = sqrt(4*A/pi) with A from power target. Check tip clearance = (cube_side - D)/2 >= 20-25 mm per side E9 E10 (40 cm rotor in 45 cm cube -> 2.5 cm per side).
2. Stack fore-aft stations: hub + nacelle housing + tail boom socket + yaw bearing + post offset. Verify stacked length < cube_side E16 E17: example 120 mm dia x 300 mm nacelle, 350 mm stacked < 450 mm = True.
3. Check yaw interface outside cube: only post OD (25 mm OD x 2 mm wall 6061-T6 E16) may protrude; slip-ring + thrust yaw bearing (30 mm E-concept) must fit within nacelle diameter.
4. Cross-check survival thrust at gust (Ct 1.0-1.3 E16) for post moment: M = T*L with L = hub height above yaw (0.4-0.5 m E14 E31) -> sigma = M*c/I < 240 MPa yield E11 E12 E16, SF >=8-12 typical E16.
5. Verify mass budget ~1-1.5 kg for tower top: example 1.22 kg E32.

## Use notes
