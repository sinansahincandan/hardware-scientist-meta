---
name: fingertip-flex-rigid-integration
description: Use when integrating CDC, MCU and LDO on a flex-rigid board inside a human-scale fingertip and routing data over I2C.
source: run 20261103-210010_tactile-fingertip-sensor-for-robot-hands (2026-11-03)
---

1. Envelope check: bone 12x15x22 mm inside fingertip 18-22 mm long x 15-18 mm wide x 15 mm high around 16.8 mm distal phalanx [E1,E2,E7,E8]; keep skin volume ~1382 mm3 mass ~1.52 g total ~4.5 g [E8,E28,E39].
2. Substrate: polyimide flex + FR4 rigid, bend radius >3 mm [E33,E34], central lumen 3x4 mm for bayonet-dovetail + M2 datum routing flex to base JST-SH.
3. Chain: 24-bit CDC AD7746 [E29,E30] or AD7147 12-ch [E36,E37] + STM32G4-class MCU [E31,E32] + 3.3 V LDO from 5 V host; budget ~45 mW.
4. Bandwidth: rate = taxels * fs * bits = 30*500 Hz*16 bit =240 kbps [E38]; select I2C 400 kHz nominal /1 MHz max passing 240 kbps.
5. Check shielding/ESD: shielded CDC front-end, ESD diodes, keep ΔC 0.88 fF >10x noise over temperature/creep or add recalibration.

## Use notes
