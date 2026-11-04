---
name: high-lift-dump-clearance-sizing
description: Use when sizing any rear-pivot tilting hopper to pour over a fixed bin lip.
source: run 20261103-152604_lunar-regolith-excavation-robot (2026-11-03)
---

1. Define target: bin lip height H_bin and opening width. Typical assumed: 0.50 m high lip (E50).
2. Define dump geometry: rear pivot height Hp plus hopper length Lh at tilt angle theta. Compute poured lip height H_pour = Hp + Lh*sin(theta). Typical: 0.45 m pivot + 0.7 m hopper at 45 deg = 0.945 m (E50).
3. Check clearance margin: H_pour - H_bin > 0.2-0.4 m for misalignment and heap. Typical: 0.945 - 0.50 = 0.44 m margin (E50).
4. Check load for actuator: soil weight Ws = mass*g. Typical: 31 kg soil = 304 N (E8, E43).
5. Check stability at tilt: restoring moment from chassis and tracks must exceed overturning from raised load. Typical margin 205 Nm holds upright (E44).

## Use notes
- run 20261104-121345_lunar-regolith-excavation-robot (Prof. James Okoro — Mobility & Excavation Systems Specialist): Helped. Sized 55deg single 24V actuator (C6) to clear fixed 300mm bin lip (E40) while keeping CG forward of rear axle for stability. Enabled F4 trade that tilt geometry provides clearance with self-lock.
