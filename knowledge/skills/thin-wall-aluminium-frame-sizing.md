---
name: thin-wall-aluminium-frame-sizing
description: Use when sizing lightweight 6061-T6 tube frames for bending with minimum tare.
source: seeded from knowledge/insights (5 problems) (2026-11-02)
---

## 1. Select alloy and section
1. Use **6061-T6 aluminium with tensile yield ~240-276 MPa** from datasheets for lightweight bending members [run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou E23,E30].
2. For round tube **30x2 mm use mass ~0.475 kg/m and section modulus ~2.31e3 mm3** [run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou E52,E41,E30].

## 2. Check bending and tare
3. Compute bending stress per tube and compare to yield. Reference: **~30.6 MPa per tube for 60-kg-class load -> safety factor ~9.02** [run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou E61,E62].
4. Budget tare explicitly. Reference build **frame+wheels+locks = 7.38 kg**, demonstrating **~7-8 kg tare class** with solid tyres achievable [run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou E40].

## Use notes
