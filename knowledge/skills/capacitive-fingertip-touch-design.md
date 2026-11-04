---
name: capacitive-fingertip-touch-design
description: Use when designing any soft capacitive fingertip array for human-like localization, grip and slip.
source: seeded from knowledge/insights (5 problems) (2026-11-02)
---

## 1. Set pitch from human acuity
1. Assume fingertip target **dome ~16 mm class (soft ellipsoid), contact ~15x20 mm ~300 mm2, finger width 15-20 mm** [run 20261102-175237_tactile-fingertip-sensor-for-robot-hands E1,E2; run 20261102-184913_tactile-fingertip-sensor-for-robot-hands E12,E8].
2. Design to **two-point discrimination 1-2 mm to 2-8 mm**: use **2-2.5 mm taxel pitch -> 40-60 taxels per fingertip (48 taxels at 2.5 mm example)** for human-like localization [run 20261102-175237_tactile-fingertip-sensor-for-robot-hands E3,E4; run 20261102-184913_tactile-fingertip-sensor-for-robot-hands E1,E8].

## 2. Design capacitive chain for femtofarad deltas
3. Expect **baseline tens of fF for sub-mm 200 um gaps (26.1 fF example) and ~0.1-0.33 pF for 2.5 mm footprint with ~1 mm gap (0.111-0.332 pF examples)** [run 20261102-175237_tactile-fingertip-sensor-for-robot-hands E17; run 20261102-184913_tactile-fingertip-sensor-for-robot-hands E8,E35].
4. Provide **fF resolution: 16 pF / 16-bit -> 0.244 fF LSB with fF noise floor**; millinewton steps sit near quantization [run 20261102-175237_tactile-fingertip-sensor-for-robot-hands E10,E15].
5. Note light-touch pressure **1 mN on 2.5 mm taxel (~6.25 mm2) = ~160 Pa (0.16 mN/mm2); 1 mN on 1 mm-radius patch = ~0.318 mN/mm2** [run 20261102-184913_tactile-fingertip-sensor-for-robot-hands E16; run 20261102-175237_tactile-fingertip-sensor-for-robot-hands E7].
6. Lower effective modulus by area-fraction structuring: **solid silicone ~1 MPa -> strain ~1e-4, sub-0.1 fF buried in parasitics; pillars ~0.02 MPa -> strain ~0.008, delta ~2.7 fF**; therefore use guarded multiplexing plus per-taxel zero/gain calibration [run 20261102-184913_tactile-fingertip-sensor-for-robot-hands E35,E36,E39].

## 3. Size elastomer for grip overload and split telemetry rates
7. Use **platinum-cure silicone Shore A 10-20 in 1-6 mm stack with sub-mm fingerprint texture** for fingertip-like compliance [run 20261102-175237_tactile-fingertip-sensor-for-robot-hands E5,E6].
8. Check overload: **~1 kg hold needs ~15 N/finger (design ~30 N/fingertip)**; over 300 mm2 **nominal ~100 kPa with peaks ~463 kPa**, where **Shore A 30 (~1 MPa) reaches ~0.463 strain near densification** so bottom out on rigid structure; reference stack mass **~4.89-5 g** [run 20261102-184913_tactile-fingertip-sensor-for-robot-hands E32,E34,E38].
9. Split rates: **slow quasi-static force at tens of Hz (48-taxel row-column ~25 Hz) + fast slip acoustics at kHz**; human Pacinian slip **~200-500 Hz requires >1000 Hz sampling (2000 Hz = 2x margin, 500 Hz Nyquist at 1 kHz)** with **sense-to-grip loop ~34 ms** [run 20261102-175237_tactile-fingertip-sensor-for-robot-hands E19,E23,E24,E25,E26; run 20261102-184913_tactile-fingertip-sensor-for-robot-hands E19,E23].
10. Budget bus: **~43.2 kbps total (~19.2 kbps static + 24 kbps vibration)** fits 4-wire serial [run 20261102-184913_tactile-fingertip-sensor-for-robot-hands E23,E18].

## Use notes
- run 20261102-214941_tactile-fingertip-sensor-for-robot-hands (Chen — Slip Dynamics and Grip Control Signal): Helped: guided row-column shear taxel plus 100-500 Hz / 1 kHz vibration dual-channel slip flag and 10 ms budget that keeps fall within 1 mm.
- run 20261103-170523_tactile-fingertip-sensor-for-robot-hands (Sofia Mount — Finger Integration and Rigid Support): Helped: guided parallel-plate taxel grid, dual-range force cover, and stick-ratio slip flag adopted in decisive choices and estimates.
