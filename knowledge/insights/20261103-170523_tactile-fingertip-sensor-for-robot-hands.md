# Insights from Tactile fingertip sensor for robot hands
Source run: 20261103-170523_tactile-fingertip-sensor-for-robot-hands

## Soft millinewton touch is a femtofarad capacitance regime
A 1 mN touch, about 0.102 g equivalent, on a millimeter-scale soft dielectric deflects only about 2.08 micrometre, producing about 0.882 fF change on about 212 fF base capacitance for a 2 mm taxel with 0.5 mm gap. Capacitive sensing in this force and size regime is a sub-femtofarad delta regime requiring femtofarad-resolution converter class such as AD7147.
Evidence: E40 (threshold mass equivalent of 1mN in grams: 0.102); E32 (threshold deflection of soft dielectric pad: 2.08 μm); E33 (capacitance change at 1mN threshold: 0.882 fF); E16 (base capacitance of 2mm taxel with 0.5mm dielectric: 2.12e-13); E11 (search: capacitance to digital converter AD7147 femtofarad resolution datasheet: datasheet.octopart.com — AD7147 (Rev. E) — https://datasheet.octopart.com/AD7147PACPZ-RL-Analog-Devices-datasheet-101563057.pdf)

## Fingertip contact spot and array pitch are millimeter-scale
Hertz contact for 1 mN on soft skin is about 0.475 mm radius at about 1.41 kPa mean pressure, while human fingertip two-point discrimination is millimeter-scale. Tactile arrays with about 2 mm pitch match this contact and acuity scale for human-scale touch localization.
Evidence: E7 (Hertz contact radius for 1mN on soft skin: 0.475); E37 (minimum pressure for 1mN over Hertz contact: 1.41 mN/mm²); E24 (search: human fingertip two-point discrimination spatial resolution mm: en.wikipedia.org — Two-point discrimination — https://en.wikipedia.org/wiki/Two-point_discrimination); E14 (search: capacitive tactile fingertip sensor array pitch resolution 2 mm: swb.skku.edu — Robotics Innovatory | Research | Previous researches — http://swb.skku.edu/roboticsinnovatory/tactile.do)

## Slip-catch time budget is tens of milliseconds and tens of millimeters
Human-like grip slip reflex latency is on the order of 74 ms, during which a free object falls about 26.9 mm. Incipient slip appears as edge slip with center stick before gross sliding, defining a tens-of-milliseconds, tens-of-millimeters catch budget for grip slip detection.
Evidence: E26 (search: human grip slip reflex latency milliseconds tactile: encyclopedia.ambient.tech — Tactile Perception for Manipulation — https://encyclopedia.ambient.tech/articles/tactile_perception_for_manipulation.html); E36 (recompute fall distance in mm during 74ms reflex for latency budget check: 26.9); E25 (search: robot tactile incipient slip detection center stick edge slip: lab.sdm.keio.ac.jp — Design of Elastic Finger — 2001 — https://lab.sdm.keio.ac.jp/maenolab/previoushp/paper/IROS2001_yamada.pdf); E28 (search: robot tactile incipient slip detection center stick edge slip: fujipress.jp — JRM Vol.14 p.140 (2002) | Fuji Technology Press: academic journal publisher — 2002 — https://www.fujipress.jp/jrm/rb/robot001400020140/)

## M2 steel screw pair proof load dwarfs fingertip grip forces
Per steel screw load tables, a pair of M2 steel screws provides about 922 N proof load. That is more than an order of magnitude above 10-30 N human fingertip pinch and grip forces, a rule of thumb for sizing miniature finger-base fasteners.
Evidence: E18 (search: M2 steel screw shear strength tensile load: roymech.co.uk — Screw Ultimate Loads and Torques — https://www.roymech.co.uk/Useful_Tables/Screws/Screw_loads.htm); E43 (correct M2 pair proof load from screw table: 922 N)
