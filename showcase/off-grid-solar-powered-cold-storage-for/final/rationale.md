# Rationale — Sun-only 1-tonne 4-6C cold store with PV, LiFePO4 bank and ice-bank

Keep 1 tonne produce at 4-6C in hot ambient using sun only with night and cloudy ride-through without grid or diesel.

## Key estimates
- pull-down thermal energy: 25.0 kWh (hand calculation; evidence ['E1'])
- wall gain estimate: 215.59999999999997 W (conduction calculation; evidence ['E3'])
- crate net volume: 2.712 m3 (volume calculation; evidence ['E5'])
- total mass check: 1000.0 kg (hand calculation; evidence ['E7'])
- combined thermal load: 30.184 kWh (hand addition; evidence ['E9'])
- door conduction estimate: 13.765500000000001 W (conduction calculation; evidence ['E10'])
- staged fill duration: 4.0 days (staged-intake division; evidence ['E12'])
- autonomy sizing nominal: 11.25 kWh (hand calculation; evidence ['E13'])
- PV array sizing minimum: 1600.0 W (standard off-grid sizing; evidence ['E14'])
- batch infiltration estimate: 0.12 kWh (batch-scaling calculation; evidence ['E15'])
- updated daily load: 6.048 kWh (hand addition; evidence ['E16'])
- autonomy check usable: 1.4880952380952381 days (autonomy division; evidence ['E17'])
- low-sun daily energy: 3.75 kWh (standard off-grid derate; evidence ['E18'])
- infiltration electric conversion: 0.048 kWh (hand conversion; evidence ['E19'])
- total payload: 1000.0 kg (payload review; evidence ['E20'])
- autonomy recheck usable: 1.4763779527559056 days (autonomy division; evidence ['E21'])
- low-sun PV required: 4.064 kW (standard derate sizing; evidence ['E22'])
- ice-bank latent estimate: 9.277777777777779 kWh (latent heat calculation; evidence ['E23'])
- PV area estimate: 20.299999999999997 m2 (panel area division; evidence ['E24'])
- canopy post-load estimate: 75.0 kg (footing load division; evidence ['E25'])

## Risks
- Array undersupply on cloudy days with 2kW giving 3.75kWh per day versus 6.05kWh load — mitigation: Stage 250kg per day intake over 4 days and upsize to 4kW PV with MPPT plus ice-bank
- Night deep-discharge without diesel backup — mitigation: Retain 48V 240Ah bank near 11.25kWh plus ice-bank for night peak shaving
- Door-opening infiltration adding to wall gain — mitigation: Use self-closing door with double gaskets plus PVC strip curtain and two fixed loadings per day

## Novelty
Separate vented steel shade canopy carrying PV above cam-lock PU panels combined with staged intake and daytime-charged ice-bank to shave night battery load.

## Sources
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf
- https://order.phaesun.com/docs/600529_DB_EN.pdf

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=False S2 flaw=False decision=s1_retry
- attempt 0 round 1: S1 faithful=False S2 flaw=False decision=s1_retry
- attempt 0 round 2: S1 faithful=True S2 flaw=False decision=s1_pass

Panels failing light check (hollow marker in caption): steps [1, 2, 3, 4, 5]

## Figure notes
- flow view skipped: 'int' object has no attribute 'append'
