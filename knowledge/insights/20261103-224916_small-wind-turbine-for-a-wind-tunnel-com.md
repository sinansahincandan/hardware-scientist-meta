# Insights from Small wind turbine for a wind-tunnel competition
Source run: 20261103-224916_small-wind-turbine-for-a-wind-tunnel-com

## Sub-meter rotor power scales with V-cubed and Cp ~0.35
Available wind power follows 0.5*rho*A*V^3. A 0.40 m disc gives ~9.6 W at 5 m/s and ~102 W at 11 m/s, a ~10x rise for 2.2x wind speed. Practical small-rotor shaft power is Cp ~0.30-0.35 of that, e.g. ~35.9 W at 11 m/s, well below the Betz limit of 0.593.
Evidence: E8 (wind power at 11 m/s 40cm rotor: 102); E9 (wind power at 5 m/s 40cm rotor: 9.62); E40 (verify 11 m/s wind power 40cm disc: 102); E41 (shaft power at 11 m/s Cp 0.35: 35.9)

## Tip-speed ratio sets rpm and torque scale
Rotor speed follows omega = TSR*V/R. At TSR ~6 and R 0.20 m, omega is ~150 rad/s at 5 m/s rising to ~330 rad/s (~3150 rpm) at 11 m/s. Shaft torque P/omega is therefore tens of mN-m at cut-in, e.g. ~0.022 N-m at 5 m/s, rising to ~0.109 N-m at 11 m/s.
Evidence: E42 (rotor rpm at 11 m/s TSR6: 3.15e+03); E74 (omega at 5 m/s TSR6: 150); E66 (aero shaft torque at 11 m/s from power and rpm: 0.109); E76 (cut-in shaft torque at 5 m/s: 0.0224)

## Gust thrust scales with V-squared
Parked or operating thrust scales with dynamic pressure q=0.5*rho*V^2 times disc area. At 22 m/s q ~296 Pa, a 0.40 m disc sees ~37 N thrust. On a 25 mm-class post this is order 15 MPa bending stress versus 6061-T6 yield 276 MPa.
Evidence: E20 (gust thrust at 22 m/s 40cm disc: 37.3); E23 (dynamic pressure at 22 m/s survival: 296); E27 (corrected bending stress in yaw post: 1.52e+07); E22 (search: 6061-T6 yield strength 276 MPa: amardeepsteel.com — Aluminium 6061 Pipes & Tubes | 6061-T6 Size Chart & Supplier — https://www.amardeepsteel.com/aluminium-6061-pipes-tubes.html)

## 6061-T6 yield versus fatigue limit
6061-T6 aluminium has yield ~276 MPa but fatigue strength ~96 MPa with no flat S-N endurance limit, so cyclic hub, shaft and post joints must be sized to fatigue not just yield.
Evidence: E54 (search: 6061-T6 aluminium fatigue endurance limit S-N curve: engineeringhulk.com — Mechanical Properties of Materials: List and Tests — https://engineeringhulk.com/mechanical-properties-of-materials/); E55 (search: 6061-T6 aluminium fatigue endurance limit S-N curve: pifyc.com — Fatigue Design Guide | Endurance Limits, S-N Curves, Stress Concentration | PifyC — https://www.pifyc.com/fatigue-design-guide.html); E22 (search: 6061-T6 yield strength 276 MPa: amardeepsteel.com — Aluminium 6061 Pipes & Tubes | 6061-T6 Size Chart & Supplier — https://www.amardeepsteel.com/aluminium-6061-pipes-tubes.html)

## Fail-safe short braking energetics and switch rating
IEC 61400-2 for small turbines and wind-tunnel competition rules require a fail-safe shutdown/brake that stops the rotor and holds it parked on loss of load. Dissipating stored spin energy ~80-90 J through near phase-short resistance ~0.25 ohm stops to 10% speed in ~1.3 s with peak ~40 A and winding rise of only ~4 K, versus ~20 s with a ~2 ohm dump. A power-MOSFET class such as IRLZ44N rated 47 A continuous at 25C covers that short pulse.
Evidence: E51 (brake stop time phase-short vs 2ohm plus false-trigger margin: R=0.75 ohm t10=30s E=336.0J Ppk=130.7W Ipk=13.2A; R=0.25 ohm t10=1.34s E=79.2J Ppk=392.0W Ipk=39.6A; trip margin 2.0V vs 0.5V ripple = 4x, false-trigger low); E44 (brake spin-down to 10pct and resistor heating: tau=8.71 s t10=20.1 s E=217.8 J omega10=33.0; Vpk=10 V Ppk=50.0 W I=5 A; rpm0=3151); E59 (rotor stored energy from inertia estimate: 87.1); E52 (winding temperature rise from 79J stop energy: 4.11); E61 (search: IRLZ44N MOSFET 47A 55V datasheet continuous drain current: manuals.plus — IRLZ44N / IRLZ44NPBF Power MOSFET User Manual — https://manuals.plus/asin/B09SV14RX7.pdf); E48 (search: IEC 61400-2 small wind turbine safety shutdown brake standard: prcrepository.org — Development of a Tool to Aid in the Preliminary Structural Design of Small Wind Turbines — http://prcrepository.org:8080/xmlui/bitstream/handle/20.500.12475/866/Art%c3%adculo%20Final_Jos%c3%a9%20Miranda.pdf?sequence=1&isAllowed=y); E45 (search: Collegiate Wind Competition rules emergency stop shutdown requirement: nrel.gov — U.S. Department of Energy Collegiate Wind Competition 2025 Rules - Phase 2 and 3 — 2025 — https://www.nrel.gov/docs/fy24osti/90855.pdf)
