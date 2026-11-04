---
name: front-feed-scraper-hopper-layout
description: Use when integrating a front-mounted shallow drag scraper that feeds directly rearward into a mid-chassis hopper without chute or conveyor.
source: run 20261103-201819_lunar-regolith-excavation-robot (2026-11-03)
---

1. Place scraper at front station (e.g., X0.85-X0.95) and hopper at mid station (e.g., X0.45-X0.65) to eliminate transfer gap - e.g., closes prior 0.30 m aft-to-mid gap (X0.95/X0.98 vs X0.45/0.65) [decisive choice 2]
2. Size scraper width to match hopper inlet width: e.g., scraper 320 mm wide (rake 35 deg) feeding 380 mm wide hopper [parts front_scraper/carry_hopper]
3. Set shallow cut depth for loose simulant: 10-15 mm operational, check deeper cuts separately; add vibration to reduce draft - e.g., 25 Hz 3 mm [parts front_scraper]
4. Verify draft vs traction using McKyes narrow-blade model for cohesion/friction: e.g., draft 40 N at 10 mm to 120 N at 25 mm [E7][E8][E39]
5. Check drawbar reserve: drawbar ~ mu * normal - e.g., normal 373 N [E38], mu 0.30 => 112 N; reserve >1.5 vs 40 N draft at 10 mm, quantify rolling resistance and Bekker sinkage for bearing ~11.5 kPa [open_question][E2][E4][E5][E6]
6. Confirm no conveyor needed: forward drive peels layer directly backward into hopper inlet during motion, buildable with purchasable blade/actuator vs no-concept alternative [decisive choice 2]

## Use notes
