---
name: fiducial-drift-reset-sizing
description: Use when bounding dead-reckoning drift with periodic fiducial resets for blind operation.
source: run 20261104-121008_lunar-regolith-excavation-robot (2026-11-04)
---

1. Propagate unaided odometry+IMU drift vs distance without fix (e.g., 40 m: 0.8 m along, ~1.4 m lateral; 60 m: 1.2 m along, ~3.14 m lateral (E33)).
2. Select fiducial reset spacing to bound error (e.g., 5 m reset bounds error to ~0.1-0.15 m (E33)).
3. Budget final dock align vs range to fiducial (e.g., 0.03 m at 1.0 m, 0.035 m at 1.5 m, 0.04 m at 2.0 m (E58)).
4. Add creep correction time: T = distance / creep speed (e.g., 0.15 m at 0.1 m/s = 1.5 s (E58)) plus stall backout detect 0.1 s + reverse 0.5 s = 0.6 s (E58).

## Use notes
