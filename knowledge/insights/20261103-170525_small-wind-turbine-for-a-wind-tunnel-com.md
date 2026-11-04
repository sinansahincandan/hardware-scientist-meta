# Insights from Small wind turbine for a wind-tunnel competition
Source run: 20261103-170525_small-wind-turbine-for-a-wind-tunnel-com

## Wind power available to sub-meter rotors scales with V-cubed
Available wind power follows P = 0.5*rho*A*V^3. A 0.4 m diameter disk (A ~0.126 m2) intercepts about 9.6 W at 5 m/s rising to about 102 W at 11 m/s, more than 10x increase for 2.2x wind speed.
Evidence: E28 (wind power 11 m/s 40cm rotor: 102 W); E33 (wind power at 5 m/s 40cm rotor: 9.62)

## Small HAWT power coefficient and tip-speed operating regime
Small three-blade horizontal-axis rotors achieve practical Cp around 0.33 at tip-speed ratio around 5.5, yielding about 3.2 W shaft from 9.6 W wind. Same TSR implies very high speed: a 0.4 m rotor reaches about 302 rad/s (~2880 rpm) at 11 m/s.
Evidence: E1 (search: small wind turbine rotor power coefficient tip speed ratio 3 blades: onlinelibrary.wiley.com — Optimal Design and Aerodynamic Performance Prediction of a Horizontal Axis Small‐Scale Wind Turbine — 2022 — https://onlinelibrary.wiley.com/doi/10.1155/2022/3947164); E34 (shaft power at 5 m/s with Cp 0.33: 3.17); E27 (rotor omega at 11 m/s TSR5.5: 302 rad/s); E29 (rpm at 11 m/s: 2.88×10³ rpm)

## Gust thrust and overturning load scale for stalled micro-rotor
Survival thrust scales with dynamic pressure times disk area. A stalled 0.4 m disk at 22 m/s sees about 33.6-37.3 N thrust, producing about 8.4-8.75 N-m overturning moment on a ~0.25 m mast arm that the support structure must react.
Evidence: E17 (gust dynamic load scale 40cm rotor: 37.3); E19 (thrust estimate with coefficient: 33.6 N); E20 (overturning moment at post top: 8.4 m⋅N); E31 (overturning moment from 35N at 0.25m arm: 8.75)

## Outrunner-as-generator voltage matching class and limits
A direct-drive brushless outrunner used as generator produces open voltage proportional to rpm (Voc ~ rpm/Kv). With Kv ~220, output spans about 5.9 V at low-wind rotor speed to about 13.1 V at top speed, defining the conditioner input range.
Evidence: E25 (skill: outrunner-generator-voltage-matching: Use when matching a direct-drive brushless outrunner as generator to a small rotor for safe voltage over speed range.); E30 (Voc top wind Kv220: 13.1 V); E35 (open voltage at 5 m/s with Kv220: 5.95)

## Wind competition loss-of-load stop standard
Collegiate wind-tunnel competition rules require shutdown to below 10% speed within 10 s on command or on loss of load, requiring a fail-safe brake that works without external power.
Evidence: E23 (search: Collegiate Wind Competition load disconnect shutdown 10 seconds requirement: energy.gov — University of Colorado Boulder Technical Design Report 2021 U.S. Department of Energy Collegiate Wind Competition — 2021 — https://www.energy.gov/sites/default/files/2021-11/ucb-turbinereport-2021.pdf); E24 (search: Collegiate Wind Competition load disconnect shutdown 10 seconds requirement: ceias.nau.edu — Requirements — 2023 — https://ceias.nau.edu/capstone/projects/EE/2023/Cyclone/teamcyclone-req.html)
