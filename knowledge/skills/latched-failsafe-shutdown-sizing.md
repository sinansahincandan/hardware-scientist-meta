---
name: latched-failsafe-shutdown-sizing
description: Use when any unmanned power system must latch shutdown on overvoltage, overspeed or manual command and stay safe without power.
source: run 20261103-224916_small-wind-turbine-for-a-wind-tunnel-com (2026-11-03)
---

1. Put over-voltage OR over-speed OR manual stop in normally-closed series loop that trips on open/power-loss (E45, E46, E50).
2. Set trip threshold with ripple margin >=4x: e.g., 2.0 V margin vs 0.5 V ripple (E51) to avoid false trigger.
3. Wire phase-short ahead of load disconnect so brake stays applied when load opens (E53).
4. Carry load only through yaw joint/slip-ring; keep brake current out of slip-ring (E53, E36, E37).
5. Latch trip without power plus spring-applied park pad to stay parked after stop (E53, E51).

## Use notes
