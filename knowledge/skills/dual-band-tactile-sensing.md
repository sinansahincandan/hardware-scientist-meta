---
name: dual-band-tactile-sensing
description: Use when one tactile fingertip must report steady contact force and high-frequency slip vibration without losing either to bandwidth or saturation.
source: run 20261104-121011_tactile-fingertip-sensor-for-robot-hands (2026-11-04)
---

1. Size static path for quasi-static force: calculate base capacitance from taxel area and gap (e.g., 1.5 mm taxel, 200 um gap -> 0.269 pF base (E26)) and delta-C from pressure/strain (e.g., 5.78 kPa on 435 kPa dielectric -> ~3.57 fF change (E55, E28)).
2. Check static resolvability on standard CDC: compare delta-C to LSB (e.g., 244 aF LSB -> ~14.6 counts at 1 mN (E62)) and check headroom to full grip (e.g., 2 N -> 26.6x margin, sweep 1 mN to 50 N strain 0.0133 to 0.489 without saturation (E63, E64)).
3. Size dynamic path separately for slip band: require direct ADC at >2x max slip frequency (e.g., 200 Hz burst (E38), 0.4 mm ridges at 50 mm/s -> ~125 Hz (E39), sample at 2200 Hz via MCU ADC (E68, E71)).
4. Check compute for dynamic filter: FIR MAC rate = taps x Fs (e.g., 44-tap x 2200 Hz = 96800 MAC/s (E78)) fits MCU MIPS/power budget (~0.0991 W readout (E51)).
5. Verify split reason: confirm CDC frame rate cannot pass vibration (e.g., 9.00 ms update, 51.2 kbit/s at 100 Hz frames (E52)) so keep volt-level PVDF film (28 um PVDF (E34, E35)) direct to MCU plus capacitive frames.

## Use notes
