---
name: link-loss-stop-sizing
description: Use when sizing any teleoperated wheeled robot for safe stop under link-loss latency.
source: run 20261103-105032_lunar-regolith-excavation-robot (2026-11-03)
---

1. Cap traverse speed for blind teleoperation - e.g. 0.3 m/s capped traverse (E16).
2. Define link-loss detection timeout and auto-stop trigger - e.g. 500 ms link-loss auto-stop (E16, E17).
3. Compute free-travel + braking stop distance - e.g. 0.195 m stop distance (E16).
4. Check: stop distance < clearance to bin/obstacle and mast camera + AprilTag alignment holds for dump (E10, E12, E17); enforce independent stop guard.

## Use notes
- run 20261103-142845_lunar-regolith-excavation-robot (Systems Autonomy Lead): Helped: set 0.3 m/s cap with 0.5 s auto-stop for 0.15 m coast under waypoint video teleop.
