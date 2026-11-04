---
name: fail-safe-tactile-link-sizing
description: Use when a wired fingertip-to-hand link must deliver full tactile frames plus a sub-30 ms slip warning that fails safe on wire break.
source: run 20261104-121011_tactile-fingertip-sensor-for-robot-hands (2026-11-04)
---

1. Split message into three parts: normally-held heartbeat line + latched slip interrupt + full tactile frame (E79) following track-circuit fail-safe where broken wire reads as danger (E74) and NC e-stop practice (E76, E77).
2. Size frame load: frames x channels x bits (e.g., 100 Hz frames -> 51.2 kbit/s SPI (E52)) to leave headroom for interrupt latency.
3. Size slip timing against contact mechanics: estimate microslip to gross-slip gap (e.g., microslip 53.6 ms, gross-slip 96.8 ms (E38)) and require detector window + link latency < gap (e.g., 30 ms window (E38) leaves 43.2 ms gap (E84)).
4. Check fail-safe behavior: heartbeat energized in normal hold, any break, power loss, or latched slip drops to danger and stays latched until hand controller acknowledges, independent of frame stream.
5. Route physically for reliability: dorsal flex tail with >=3.18 mm bend radius and 0.5 mm ZIF (E43, E67) plus 6-wire cable to hand, verified by open-question shake-and-grip closure test.

## Use notes
