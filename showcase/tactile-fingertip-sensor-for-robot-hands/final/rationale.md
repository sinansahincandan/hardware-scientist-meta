# Rationale — Soft-pillar capacitive plus vibration fingertip cartridge for grip and slip sensing

Robot fingertip must localize touch, measure 1 mN to grip force with shear, detect slip vibration, and mount with wiring surviving grip loads.

## Key estimates
- taxel count: 48.0 taxels (simulate; evidence ['E8'])
- contact area: 300.0 mm2 (simulate; evidence ['E8', 'E32'])
- light-touch pressure from 1 mN on one taxel: 160.0 Pa (calc; evidence ['E16'])
- base capacitance for 2.5 mm taxel: 0.332 pF (calc; evidence ['E35'])
- light-touch strain with soft pillars: 0.008 strain (calc; evidence ['E36'])
- capacitance change at 1 mN: 2.66 fF (calc; evidence ['E35', 'E36', 'E16'])
- static sampling rate: 25.0 Hz (simulate; evidence ['E18', 'E24'])
- vibration sampling rate: 2000.0 Hz (simulate; evidence ['E23'])
- total data rate: 43.2 kbps (simulate; evidence ['E23'])
- nominal grip pressure at 30 N: 100.0 kPa (simulate; evidence ['E32'])
- worst-case pressure: 463.3 kPa (simulate; evidence ['E32'])
- normal grip force for 1 kg object: 14.8 N (simulate; evidence ['E32'])
- effective pillar modulus: 0.02 MPa (calc; evidence ['E39', 'E36'])
- worst-case skin strain: 0.463 strain (calc; evidence ['E34'])
- cartridge mass: 4.89 g (calc; evidence ['E38', 'E37'])

## Risks
- 1 mN signal buried by parasitics, hysteresis 5-10 percent and drift — mitigation: use soft air-gap pillars with guarded row-column scanning and per-taxel zero plus gain updated when unloaded
- thin ridged skin tears under repeated 30 N to 139 N crush — mitigation: mold pillars and skin as one piece and let pillars bottom to solid at high load, replace cap when worn
- mount flexes or tail pinches causing drop or crush — mitigation: use stiff bolted core with rear tail and slip-triggered squeeze proven in drop and crush tests

## Novelty
Soft molded air-gap pillars as combined spring and sensing gap with dual-rate static capacitance plus fast vibration film in a stiff bolted quick-change cap with rear 4-wire bus

## Sources
- (none)

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=False S2 flaw=False decision=s1_retry
- attempt 0 round 1: S1 faithful=False S2 flaw=False decision=s1_retry
- attempt 0 round 2: S1 faithful=True S2 flaw=False decision=s1_pass

Fabrication steps not shown because they failed their light check: [4]

## Figure notes
- callouts Vibration Sensing Film pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: rear flexible tail
- fabrication step 3 passed after one redraw (first attempt: Pixels show an exploded stack, not a step-3 mounted cartridge, and scale fails: the device body is wider in pixels than the grey hand/palm silhouette beside it, whereas a ~20 mm device should be ~1/4-1/5 of hand width. The layers are floating separated instead of assembled and screwed down as a fingertip cartridge with tail out the back.)
- fabrication step 4 not shown: failed its light check twice (Pixels show only assembled exterior - outer skin, flex tail, board edge, screws/base - with a flat grey hand graphic hovering. Internal stack parts silicone pillar dielectric, vibration sensing film, taxel electrode detail, rigid core are not shown, and no unloaded vs grip-load calibrate action is depicted, so fabrication step 4 is not shown.)
