---
name: stowed-box-station-packaging
description: Use when checking a wheeled field robot with deployable wheels, blades and masts fits inside a prescribed LxWxH stowed box.
source: run 20261103-201819_lunar-regolith-excavation-robot (2026-11-03)
---

1. Define chassis station interval (e.g., X0.00-X0.85 for 850 mm chassis) and allocate intervals for folded deployables (e.g., X0.85-X0.95 folded blade, X-0.02-0.02 bumper) [E12][E34]
2. Sum stowed length nominally: chassis + front overhang + rear folded thickness - e.g., 850+20+50=920 mm vs 1000 mm limit = PASS [E9][E12][E33][E35]
3. Sum worst-case tolerance: add folding play + bumper tolerance - e.g., +10+5=935 mm still <1000 mm margin 65 mm [E13]
4. Check stowed width with wheels side-tucked vertically alongside chassis walls inside footprint, not stacked: total width = chassis width (e.g., chassis 420 mm, wheels 250 dia x 120 wide each, total 420 mm <500 mm) [E10][E14]
5. Check stowed height with deployables folded: chassis + folded mast thickness (e.g., 250 mm <500 mm) [E11]
6. Verify layout by sketch that hopper fits its assigned interval (e.g., 180 mm hopper in 200 mm X0.45-0.65 interval, occupancy 0.9) and wheels do not add to width/length when stowed [E24][E34][E41]

## Use notes
