---
name: fingertip-mass-stack-budget
description: Use when budgeting mass and thickness of a human-scale fingertip tactile stack against anthropomorphic envelope.
source: run 20261104-123505_tactile-fingertip-sensor-for-robot-hands (2026-11-04)
---

1. Sum component masses: outer skin + pillar layer + flexible carrier + PCB/electronics [E46].
2. Check total vs anthropomorphic limit 10-20g [E55]: typical 1.5g total (skin 0.514g, pillars 0.135g, PCB 0.355g, elec 0.5g) [E48] gives >6x margin.
3. Sum stack thickness: skin 0.8mm + pillars 0.7mm + PET 0.2mm + FR4 0.8mm + lip 0.5mm (~2.8mm) [E56] vs fingertip envelope 13mm [E56] and human fingertip ~20-25mm [E24,E30].
4. Check thermal conduction through stack for mW heat: dT ~2.5K conduction [E48] with silicone k, vs convection overestimate 13.3K [E48] to ensure skin contact <40C.
5. Iterate materials/density (Dragon Skin ~1.07g/cm3 [E43,E45]) if mass or thickness exceeds budget.
Typical values: total 1.5g [E48,E55] vs 10-20g limit [E55], stack 2.8mm [E56] vs 13mm [E56,E24], density 1.07 g/cm3 [E43].

## Use notes
