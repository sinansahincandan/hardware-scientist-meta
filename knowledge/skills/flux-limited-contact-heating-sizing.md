---
name: flux-limited-contact-heating-sizing
description: Use when selecting a conduction spacer stack between a hot PCM store and skin-contact surface to keep surface below IEC 43C and design 40C while delivering required watts.
source: run 20261103-223203_infant-warmer-for-clinics-without-reliab (2026-11-03)
---

1. Define limits: IEC 60601-1 prolonged skin contact T_surf_max =43C, justify >41C, design limit 40C even when PCM charged at 60C E12,E13,E15,E16 and WHO band 36.5-37.5C E22.
2. Estimate required forward flux: P =5 W at delta T = T_pcm - T_mattress ~3 K E51. Hence required total R_th = delta T / P ~0.6 K/W E51.
3. Build stack: 3 mm food-grade silicone R~0.25 K/W + 5 mm perforated PE foam R~1.0 K/W E51. Account for parallel/perforated reduction to effective ~0.6 K/W E51.
4. Check operating point: with PCM at 37C plateau, T_mattress = T_pcm - P*R = 36.8C within 36.5-37.5C E51.
5. Check hot-charge safety: with PCM/source at 60C, simulate/lump T_surf_hot =39.7C E51 <40C design limit and <43C IEC E12,E15,E51.
6. If T_surf_hot exceeds limit, increase R (thicker foam, lower perforation fraction) or add thermal mass; if T_mattress below band, decrease R.
7. Confirm cleanability and biocompatibility: 0.5% chlorine wipe tolerance, removable tray with 5 deg draft, 8 mm radii E17.

Checks: T_surf_hot <40C at max charge; T_mattress 36.5-37.5C at plateau; R_amb closed 3.75 K/W vs open 1.2 K/W for regulation E51,E25.
Typical values: silicone 3 mm 0.25 K/W, perforated foam 5 mm 1.0 K/W, stack ~0.6 K/W, P~5 W, delta~3 K -> 36.8C plateau, 39.7C hot E51; enclosure loss ~4 W at 22C with 20 mm PE foam + clear half-canopy E51.

## Use notes
