# Insights from Small wind turbine for a wind-tunnel competition
Source run: 20261103-210013_small-wind-turbine-for-a-wind-tunnel-com

## Small-rotor thrust magnitude and feathering as load limiter
In the 0.4 m-diameter, 5-22 m/s small-turbine regime, axial thrust scales with V^2 and thrust coefficient: ~29.8 N at Ct=0.8 vs ~7.5 N at Ct=0.2 at 22 m/s, a ~4x reduction by pitching to feather. The feathered gust load at 22 m/s equals the unfeathered rated load at 11 m/s (~7.5 N), so base overturning moment can be bounded as Thrust x hub height (e.g., 7.5 N x 0.30 m = 2.25 N·m).
Evidence: E5 (power and thrust estimates: torque 0.102 Nm; Ct0.8 V22 Th=29.8 N; Ct0.2 V22 Th=7.5 N); E6 (complete numbers: Ct0.8 V22 Th=29.8 N; Ct0.2 V22 Th=7.5 N; Ct0.8 V11 Th=7.5 N); E7 (tower base moment feathered 22m/s: 2.25); E20 (tower moment feathered: 2.25 m⋅N)

## Braking torque and energy budget for <10% speed in 10s
Aero driving torque in this size class is O(0.1 N·m) at rated and ~0.4 N·m at 22 m/s. Decelerating inertia J~0.0035 kg·m2 from ~300 rad/s (TSR~5.5 at 11 m/s) to <30 rad/s in 10 s requires alpha ~27 rad/s2 and net retarding torque ~0.095 N·m sustained over residual aero torque. Stored rotational energy is O(100-160 J), which exceeds a 5F 5V supercapacitor hold-up budget of 62.5 J, so a passive dump/heatsink path must absorb the remainder.
Evidence: E5 (power and thrust estimates: torque 0.102 Nm; Ct0.8 V22 Th=29.8 N; Ct0.2 V22 Th=7.5 N); E18 (generator voltage vs Kv and braking torque vs aero torque: aero torque est V 22 0.408 Nm; required net braking torque to stop in 10s from 11 m/s 0.095 Nm alpha 27.2 rad/s2; supercap energy 5F5V 62.5 J); E21 (rotational energy: 160 J)

## Direct-drive outrunner as generator: voltage vs speed and converter range
Repurposed BLDC outrunners in the Kv~380 rpm/V class (Ke~0.025 V per rad/s) produce Voc ~ Ke*omega: ~3.5 V at ~138 rad/s (5 m/s) to ~7.5 V at ~302 rad/s (11 m/s) for a 0.4 m rotor at TSR 5.5. Operation across 5-15 V therefore requires a buck-boost MPPT stage to capture the 2:1+ voltage swing with wind speed.
Evidence: E13 (search: brushless outrunner generator Kv voltage constant wind turbine 400mm rotor: neumotors.com — 3800 SERIES BLDC MOTORS - NeuMotors Brushless Motors — https://neumotors.com/brushless-motor-manufacturing/neumotors-3800-series-bldc-motors-400-to-1600-watt-class/); E17 (check omega 11m/s: 302 rad/s); E18 (generator voltage vs Kv and braking torque vs aero torque: aero torque est V 22 0.408 Nm; required net braking torque to stop in 10s from 11 m/s 0.095 Nm alpha 27.2 rad/s2; supercap energy 5F5V 62.5 J); E19 (verify Voc 11m/s: 7.55 V)

## Yaw power transfer via capsule slip ring
Off-the-shelf M220-series capsule slip rings with ~22 mm bore, 2-circuit 10 A rating provide DC continuity through continuous yaw with contact noise <0.01 ohm, meeting a <0.1 ohm bus requirement without cable wind-up.
Evidence: E9 (search: slip ring capsule 22mm bore low resistance <0.1 ohm wind turbine datasheet: senring.com — M220 Series Medium Capsule Slip Ring - Senring — https://www.senring.com/capsule-slip-ring/m220.html); E10 (search: slip ring capsule 22mm bore low resistance <0.1 ohm wind turbine datasheet: evelta.com — M220A-0210 - Capsule Slip Ring 22mm 2 Circuits 10A 200mm Wire | SenRing ... — https://evelta.com/capsule-slip-ring-od22mm-2-circuits-10a-wire-length-200mm/)
