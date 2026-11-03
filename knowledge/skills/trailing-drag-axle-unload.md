---
name: trailing-drag-axle-unload
description: Use when a rear trailing implement pulls behind any wheeled chassis and unloads the front axle.
source: run 20261103-142845_lunar-regolith-excavation-robot (2026-11-03)
---

1. Size drag force of trailing tool at chosen cut (e.g., 172 N pull for 400 mm blade at 25 mm cut (E26, E31)).
2. Compute moment of drag about ground contact to get front-axle unload (e.g., ~43 units unload from trailing drag (E30)).
3. Check traction margin remains positive: available friction minus pull (e.g., 305 N margin after 172 N pull at 39 deg friction (E31)).
4. Check flotation: per-wheel pressure loaded stays low for soft soil (e.g., 12.1 kPa loaded (E33)).
5. If unload or margin fails, reduce cut depth/width or add ballast/wheel area before sizing power (e.g., 51.6 W draft at 0.3 m/s cap (E26)).

## Use notes
