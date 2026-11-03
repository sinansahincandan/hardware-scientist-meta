---
name: loose-soil-mobility-budget
description: Use when budgeting any small wheeled field robot for soft soil, power, dust and delayed links.
source: seeded from knowledge/insights (5 problems) (2026-11-02)
---

## 1. Treat soil as frictional and check pressure
1. Treat **Black Point-1 simulant as cohesionless high-friction granular with negligible cohesion**; strength scales with normal pressure, cut geometry and friction angle, with angular abrasive fines and dust-ingress risk [run 20261102-153907_lunar-regolith-excavation-robot E1,E2,E3].
2. Compute **nominal ground pressure = weight / total contact area (example ~589 N on four 150x100 mm patches = 9.82e3 Pa / 9.8 kPa)** [run 20261102-153907_lunar-regolith-excavation-robot E9,E10].
3. Compute **drawbar ratio = tool force / weight (example 39 N / 589 N = 0.0662)**; plan that tens of N consumes **~half friction-limited margin (margin 0.566 example)** and use **Bekker sinkage + grouser shear, not paved-tire friction**, for sinkage/slip [run 20261102-153907_lunar-regolith-excavation-robot E11,E12,E7].

## 2. Budget energy, sealing and latency
4. Budget sortie energy `E=P*t`: **~341 W for 0.5 h = 170 Wh, so 480 Wh pack -> ~1.41 h full-load runtime** [run 20261102-153907_lunar-regolith-excavation-robot E32,E36].
5. Seal field electronics to **IP65: dust-tight (no harmful ingress) + water jets any direction via gasketed box, sealed connectors and glands** [run 20261102-153907_lunar-regolith-excavation-robot E29,E30,E31].
6. For **non-line-of-sight 5 GHz WiFi FPV allow ~100 ms-class video+control latency -> ~0.25 m stopping even at crawl** and require **loss-of-heartbeat stop-and-hold** [run 20261102-153907_lunar-regolith-excavation-robot E13,E19].
7. Allow **teleoperation overhead ~29 W and ~1.73 kg for Jetson Orin Nano-class compute, cameras, depth and radio** [run 20261102-153907_lunar-regolith-excavation-robot E16,E20,E21].

## Use notes
