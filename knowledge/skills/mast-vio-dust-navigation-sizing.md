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
