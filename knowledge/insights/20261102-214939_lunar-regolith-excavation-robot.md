# Insights from Lunar regolith excavation robot
Source run: 20261102-214939_lunar-regolith-excavation-robot

## Loose simulant density and repose regime
Black Point BP-1 lunar simulant is a loose frictional granular regime with bulk density near 1.5 g/cc and angle of repose near 45 deg. Mass carried therefore scales as ~1.5 kg per litre, e.g. 20 L is ~30 kg. Gravity flow in bins and hoppers requires wall slopes steeper than the 45 deg repose angle, otherwise material bridges and must be tipped or vibrated to discharge.
Evidence: E2 (search: Black Point BP-1 lunar simulant bulk density friction angle bearing strength: ares.jsc.nasa.gov — ARES | Exploration Science Projects | Lunar Regolith Simulants | BP-1 — https://ares.jsc.nasa.gov/projects/simulants/bp-1.html); E3 (search: Black Point BP-1 lunar simulant bulk density friction angle bearing strength: simulantdb.com — Planetary Simulant Database — https://www.simulantdb.com/simulants/bp1.html); E13 (search: lunar simulant angle of repose hopper wall slope: researchgate.net — The Effect of Sample Mass on the Angle of Repose of Lunar Regolith Simulants — https://www.researchgate.net/publication/365470382_The_Effect_of_Sample_Mass_on_the_Angle_of_Repose_of_Lunar_Regolith_Simulants); E14 (search: lunar simulant angle of repose hopper wall slope: frontiersin.org — Verification of a virtual lunar regolith simulant — 2024 — https://www.frontiersin.org/journals/space-technologies/articles/10.3389/frspt.2024.1303964/full); E18 (hopper soil mass 20L at 1.5g/cc: 30 kg)

## Shallow cut force versus traction limit
Drag cutting force in simulant scales approximately linearly with cut depth in the shallow regime, e.g. ~275 N at 40 mm depth scales to ~172 N at 25 mm. Available drawbar is mu times loaded weight, e.g. ~483 N at mu 0.6 for ~82 kg total. Cutting power is force times speed, e.g. ~27.5 W at 275 N and 0.1 m/s, with per-wheel drive torque set by dig pull plus rolling resistance, e.g. order 11 N-m per wheel in this class.
Evidence: E39 (scale 275N at 40mm to 25mm slice: 172); E40 (traction available at mu 0.6 loaded 82kg: 483); E41 (drive torque per wheel dig plus rolling: 11); E17 (cutting power from 275N at 0.1m/s: 27.5 m⋅N/s)

## Soft-soil contact pressure and skid-steer yaw cost
Small wheeled vehicles on loose simulant operate at ground pressures of a few kPa when fitted with wide rigid grouser wheels, e.g. ~2.45 kPa for 60 kg class on four wide contacts. Skid steering in this regime incurs a large yaw resistance moment from lateral scrub, e.g. order 88 N-m total, which sizes steering torque far above straight-drive torque.
Evidence: E8 (nominal ground pressure 60kg on four wide wheels: 2.45×10³ N/m²); E10 (order turning moment skid steer estimate: 88.3 m⋅N)

## Teleoperation video and short-sortie energy budgets
Teleoperation over workshop WiFi with H.264 compressed onboard video uses only a few percent of worst-case link capacity, e.g. ~0.05 fraction, leaving margin for command uplink and heartbeat. Mission energy for short excavation sorties is power times time, e.g. 200 W average for 15 min is ~50 Wh, which sizes battery packs in the tens of Wh plus reserve.
Evidence: E27 (video bandwidth fraction of worst-case WiFi: 0.0495); E37 (mission energy 200W average 15min round: 3×10³ min⋅W)
