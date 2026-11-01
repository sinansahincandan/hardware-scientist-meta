# Whiteboard
## Functions
- F1 [Solar Power Specialist] Keep 1 tonne produce at 4-6 C in hot ambient
- F2 [Solar Power Specialist] Generate all electricity from sun only
- F3 [Solar Power Specialist] Ride through night and cloudy periods without grid or diesel
## Concepts
- C1 [Solar Power Specialist, open, for F1] 100mm PU insulated 10m3 cold room with DC vapour-compression cooler holding 4-6C
- C2 [Solar Power Specialist, open, for F2] Tilted roof monocrystalline PV array with MPPT charge controller, sized by daily kWh divided by peak sun hours plus 25% losses
- C3 [Solar Power Specialist, open, for F3] 48V LiFePO4 battery bank with 1.5 days autonomy plus thermal ice-bank for night cooling
- C4 [Structural Enclosure Designer, open, for F1] Twin side racks with central aisle holding fifty 600x400x226mm vented crates for 1 tonne, internal room about 2.6x2.0x2.1m high giving 10m3 gross and 2.7m3 net crate volume (assumed_constraint per NCCD 3.4m3 per tonne guideline)
- C5 [Post-Harvest Cooperative Operations Lead, open, for F1] Ground-level cooperative loading workflow with fifty 20kg vented crates on twin racks, external wash slab with chlorinated water, and pay-per-crate cooperative ownership with trained local caretaker
## Evidence
- E1 [calc, Solar Power Specialist] 25.0 (ok)
- E2 [sketch, Solar Power Specialist] Insulated cold room with roof PV array, MPPT controller, battery bank and DC vapour-compression unit; airflow loop shown. (ok)
- E3 [calc, Refrigeration and Thermal Engineer] 215.59999999999997 (ok)
- E4 [sketch, Refrigeration and Thermal Engineer] Insulated cold room section with evaporator fan airflow over produce crates, 100mm PU walls, condenser heat rejection outside, condensate drain. (ok)
- E5 [calc, Structural Enclosure Designer] 2.712 (ok)
- E6 [sketch, Structural Enclosure Designer] Cold room enclosure: twin side racks with 50 vented crates, central aisle, hinged door with seals, 100mm PU panels and vented PV shade roof. (ok)
- E7 [calc, Post-Harvest Cooperative Operations Lead] 1000 (ok)
- E8 [sketch, Post-Harvest Cooperative Operations Lead] Cooperative loading workflow: ground-level door, central aisle, twin crate racks, external wash slab (ok)
- E9 [calc, Refrigeration and Thermal Engineer] 30.184 (ok)
- E10 [calc, Structural Enclosure Designer] 13.765500000000001 (ok)
- E11 [sketch, Structural Enclosure Designer] Insulated door with gaskets, cam-lock PU panels, rack aisle and PV shade canopy gap (ok)
- E12 [calc, Post-Harvest Cooperative Operations Lead] 4.0 (ok)
- E13 [calc, Solar Power Specialist] 11.25 (ok)
- E14 [calc, Solar Power Specialist] 1600.0 (ok)
- E15 [calc, Post-Harvest Cooperative Operations Lead] 0.12 (ok)
- E16 [calc, Solar Power Specialist] 6.048 (ok)
- E17 [calc, Solar Power Specialist] 1.4880952380952381 (ok)
- E18 [calc, Solar Power Specialist] 3.75 (ok)
- E19 [calc, Refrigeration and Thermal Engineer] 0.048 (ok)
- E20 [calc, Post-Harvest Cooperative Operations Lead] 1000 (ok)
- E21 [calc, Solar Power Specialist] 1.4763779527559056 (ok)
- E22 [calc, Solar Power Specialist] 4.064 (ok)
- E23 [calc, Refrigeration and Thermal Engineer] 9.277777777777779 (ok)
- E24 [calc, Structural Enclosure Designer] 20.299999999999997 (ok)
- E25 [calc, Structural Enclosure Designer] 75.0 (ok)
- E26 [sketch, Structural Enclosure Designer] Separate steel shade canopy over PU cold room carrying 4kW PV, vent gap, four anchored posts, twin racks inside. (ok)
## Objections
- O1 [Manager -> C3, blocking=False] Battery autonomy in kWh not closed: no combined daily electrical load from E1 pull-down and E3 wall gain to justify 1.5 days. Request Solar Power Specialist to compute.
- O2 [Manager -> C2, blocking=False] Cloudy-sequence refill not closed: E14 sizes for 5 Peak Sun Hours fair-sun only, no 2-3 day low-sun energy balance for F3.
- O3 [Manager -> C1, blocking=False] Door-opening infiltration kWh not added to steady load: E10 covers conduction only, not air exchange vs E9 combined load.
- O4 [Manager -> C3, blocking=False] Ice-bank kWh contribution to 1.5 days autonomy not quantified separately from battery E17; request Refrigeration Engineer to compute latent kWh.
- O5 [Manager -> C3, blocking=False] Ice-bank thermal kWh (E23) not converted to electrical kWh via COP, so combined battery+ice autonomy in days remains unclosed. Request Refrigeration Engineer to provide divisor.
## Proposal
- (none)
## Votes
