---
name: off-grid-cold-store-sizing
description: Use when sizing any off-grid vapor-compression cold store for holding, pull-down, PV and autonomy.
source: seeded from knowledge/insights (5 problems) (2026-11-02)
---

## 1. Separate holding from pull-down
1. Compute conduction `Qcond=U*A*dT`. Reference tonne box: **U=0.22 W/m2K, A=25.6 m2, Qcond=186 W, Qsteady=376 W** including respiration, infiltration and fans for 4-10 C box in ~30 K ambient [run 20261102-112524_off-grid-solar-powered-cold-storage-for- E24].
2. Budget pull-down separately: **~25.0 kWh thermal per tonne from ~30 C to ~5 C (c~3.5 kJ/kg-K)**, an order above hourly holding; for 24-h pull-down **P_pull~1042 W thermal** [run 20261102-112524_off-grid-solar-powered-cold-storage-for- E24].

## 2. Convert to electric and PV
3. Apply **DC vapor-compression COP~2.5**: **~370-400 W cold -> ~150 W electric, ~3.6 kWh/day continuous** (daily electric 3.61 kWh in example) [run 20261102-112524_off-grid-solar-powered-cold-storage-for- E51,E52,E24,E20].
4. Apply tropical fixed-tilt yield **~3-4 kWh/day per kWp (example 8.1 kWh/day from 2.4 kWp)** and oversize **PV ~2-3x over holding** to cover batch cooling, charge losses and cloud before battery sizing [run 20261102-112524_off-grid-solar-powered-cold-storage-for- E54,E24].

## 3. Size night store and buffers
5. Size LiFePO4 usable store: **48 V 100 Ah = ~5.12 kWh nominal** [run 20261102-112524_off-grid-solar-powered-cold-storage-for- E7,E9].
6. Check night fraction: **150 W x 14 h = 2.1 kWh, ~0.41 of store, ~1.42 days holding-only autonomy** with no solar [run 20261102-112524_off-grid-solar-powered-cold-storage-for- E57,E58,E66].
7. Credit produce thermal buffer **~1.94 kWh per 2 K rise per tonne** for sealed-box ride-through and alarm thresholds [run 20261102-112524_off-grid-solar-powered-cold-storage-for- E67].
8. Sanity-check pack mass with **COTS 24 V LiFePO4 pack ~90-120 Wh/kg at pack level (480 Wh / 5.3 kg = 90.6 Wh/kg; 819 Wh / 6.8 kg ~120 Wh/kg)**; reject claims **>150-200 Wh/kg (e.g. 1000 Wh in 2.92 kg = 342 Wh/kg)** as cell-only or erroneous [run 20261102-153907_lunar-regolith-excavation-robot E34,E35,E33].

## Use notes
- run 20261104-123515_off-grid-solar-powered-cold-storage-for- (Solar Power Systems Engineer): Helped. Provided holding/pull-down/PV/autonomy budgeting framework used in solution: 1.03 kWp minimum PV for 3.6 kWh/day at 5 PSH 0.70 efficiency E18 vs 2.4 kWp chosen giving 8.4 kWh/day usable E63 (2.36x margin E64); 3.84 kWh usable at 80% DoD E17 vs 2.10 kWh night need E15 (1.82 day autonomy E65); transmission 220W at dT39K E26/E48 =5.27 kWh/day thermal E28/E49 =2.11 kWh electric at COP2.5 E50 plus respiration 0.72 kWh E51 to total 3.56 kWh/day holding E53; pull-down 33.6 kWh thermal E27 =13.4 kWh electric E29 staged over 2-3 days.
