---
name: mast-vio-dust-navigation-sizing
description: Use when placing a mast-mounted stereo visual-inertial odometry system for teleoperated navigation in dusty, feature-poor terrain.
source: run 20261103-210007_lunar-regolith-excavation-robot (2026-11-03)
---

1. Set mast height to clear hopper/dust cloud: 500 mm mast for 0.5 m stowed height, stereo depth camera with IMU and wheel encoders for <2% drift, 10 cm at 8 m accuracy.
2. Check camera dust tolerance: select RealSense-class depth camera IP rating and clean with brush/shroud; verify homography-based VIO (LuVo E28 E29) maintains track in BP-1 dust.
3. Budget link and FOV: ensure dual-radio heartbeat does not occlude camera FOV; tilt to cover 0.5-5 m path for 0.05-0.10 m/s E49 traverse.
Typical values: 500 mm mast E28-E33, 10 Hz heartbeat 0.5 s auto-brake E30-E31 with 0.0533 m stop distance E35, <2% drift over sortie.

## Use notes
- run 20261104-123502_lunar-regolith-excavation-robot (Dr. Priya Sharma — Power, Sensing & Remote Autonomy): Did not help this run - skill opened at E32 and web searches E34-E35 for IP65 stereo cameras were done, but no evidence shows mast height, baseline, FOV, stowed vs deployed clearance for VIO, or dusty feature-poor degradation sizing. Transfer line mentions folding mast VIO generically but no calculation, simulation or decisive choice cites mast geometry or VIO performance.
