# Rationale — Under-deck vertical TMD at midspan on clamped cross-frame with perforated screen

Lively 1.9 Hz vertical footbridge mode exceeds 0.7 m/s2 comfort limit and needs under-deck retrofit hung entirely from below with no deck closure or appearance change that dissipates mode energy to comfortable acceleration

## Key estimates
- peak vertical deck acceleration comfort limit: 0.7 m/s2 (web_search; evidence ['E13', 'E2'])
- bare single-walker resonant acceleration: 1.75 m/s2 (calc; evidence ['E22'])
- damped peak deck acceleration with TMD: 0.106 m/s2 (simulate; evidence ['E32'])
- TMD moving mass: 800.0 kg (vetted_calc; evidence ['E11', 'E33'])
- TMD tuning frequency: 1.83 Hz (vetted_calc; evidence ['E11', 'E33'])
- TMD spring stiffness: 105412.0 N/m (vetted_calc; evidence ['E11'])
- TMD damping ratio: 12.0 % (vetted_calc; evidence ['E11', 'E33'])
- total static hung load TMD plus frame: 9.81 kN (calc; evidence ['E29', 'E44'])
- TMD stroke in band: 2.52 mm (simulate; evidence ['E32'])
- slip safety factor 8 clamps: 3.26 ratio (calc; evidence ['E45', 'E39'])
- required response reduction factor: 2.5 ratio (calc; evidence ['E31'])
- static weight from 800 kg mass: 7850.0 N (calc; evidence ['E34'])
- spring force from stroke: 266.0 N (calc; evidence ['E35'])
- damper force estimate: 63.8 N (calc; evidence ['E36'])

## Risks
- Modal mass differs from assumed 20000 kg causing detuning — mitigation: Freeze modal mass at 20000 kg and rerun Den Hartog sizing with measured mass
- Clamp slip under hung TMD load — mitigation: Share 9.81 kN hung load on 8 clamps for 32.0 kN capacity and 3.26 factor
- Local girder flange bending under clamp point loads — mitigation: Treat about 1.23 kN per clamp as person-scale non-critical at concept stage and do detailed check with flange thickness and spacing

## Novelty
Recessed under-deck TMD cassette with shadow-gap perforated color-matched screen hiding tuned unit on clamped no-drill support with lock-off

## Sources
- https://structechnique.com/download/15/free/aO4RBDPc
- https://mediatum.ub.tum.de/doc/1762603/document.pdf
- http://fstructures.com/structures/pedestrian-bridge-vibration-dynamics/
- https://files.kgf.cz/6btngt25so12/Tuned%20Mass%20Dampers%20for%20Vibration%20Control%20of%20Footbridges%20from%20an%20Architectural%20Point%20of%20View_KGF%20hydraulika_Jiri%20Kucera_Bridges%20in%20Danube%20Bas.pdf?download
- https://api.repository.cam.ac.uk/server/api/core/bitstreams/3afdf7af-401b-44f6-8bdb-b40f25db454f/content
- https://www.ioa.org.uk/system/files/publications/C MEINHARDT D NEWLAND J TALBOT D TAYLOR VIBRATION PERFORMANCE OF LONDONS MILLENNIUM FOOTBRIDGE.pdf
- https://www.fullscaledynamics.com/project/vibration-simulations-and-tuned-mass-damper-design-for-castle-bridge-bristol/
- https://www.scribd.com/document/467340093/P-1
- https://dspace.vut.cz/server/api/core/bitstreams/fe91b2bb-e77d-41e7-847d-e32cfb3c7d2a/content
- https://pmarketresearch.com/auto/passive-tuned-mass-damper-market/
- https://core.ac.uk/download/pdf/4431304.pdf
- https://pmarketresearch.com/auto/tuned-mass-damper-system-market/
- https://dataintelo.com/report/active-tuned-mass-dampers-market
- https://dataintelo.com/report/bridge-wind-vibration-tuned-mass-dampers-market
- https://pmarketresearch.com/worldwide-tuned-mass-damper-tmd-market-research/
- https://market.us/report/tuned-mass-damper-market/
- https://growthmarketreports.com/report/bridge-wind-vibration-tuned-mass-dampers-market
- https://www.scribd.com/document/312613078/Mass-Dampers
- https://patents.google.com/patent/US6292967B1/en
- https://eureka.patsnap.com/patent-CN103758029A
- https://patents.google.com/patent/CN112227180A/en
- https://patents.google.com/patent/CN113737633A/en
- https://patents.google.com/patent/CN103774771A/en
- http://eureka.patsnap.com/patent-US10634205B2
- https://eureka.patsnap.com/patent-CN102493572B
- https://eureka.patsnap.com/patent-US20190249740A1
- https://patents.google.com/patent/CN102888904B/en
- https://patents.google.com/patent/CN102561174A/en
- https://patents.google.com/patent/CN108797311B/en

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

Fabrication steps not shown because they failed their light check: [1, 2, 3]

## Figure notes
- labels removed because they pointed at the wrong part: Friction clamps
- fabrication step 1 failed its light check (Core lift-below clamping of gray transverse member to green girder bottom flange is visible, but pixels also show extra structural parts beyond the three listed - blue diagonal tube with two clamps, bolted end-plate/bracket, top C-clamp - plus shop tools, so not exactly those parts.); not shown
- fabrication step 2 failed its light check (Pixels show bench-top mockup on wooden workbench, not bridge under-deck. No existing longitudinal girder visible; base frame held by workshop G/bar clamps not friction beam clamps; no transverse cross-beam on girder; red screw is workshop clamp screw not maintenance lock-off pin. Does not match listed step 2 parts.); not shown
- fabrication step 3 failed its light check (Pixels show a workshop bench mock-up, not an under-deck install: test columns/rig, tools and bench present, no identifiable existing bridge girder, no verifiable 800kg mass, vertical-only freedom, +/-30mm clearance, or distinct maintenance lock-off pin.); not shown
