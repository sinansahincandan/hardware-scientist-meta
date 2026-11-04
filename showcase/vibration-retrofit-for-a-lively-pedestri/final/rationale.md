# Rationale — Twin under-deck tuned mass damper on HSFG-clamped cross-beam

Retrofit a lively 40 m footbridge at 1.9 Hz with under-deck damping to bring Class III crowd shake into Medium comfort with no deck change and weight inside 2 %.

## Key estimates
- TMD total mass: 800.0 kg (calc mass ratio; evidence ['E13'])
- TMD static weight: 7.85 kN (calc static weight; evidence ['E26'])
- pedestrian live load: 600.0 kN (calc live load; evidence ['E30'])
- added weight fraction TMD-only: 1.31 % (calc weight fraction; evidence ['E72'])
- added weight fraction total with beam steel: 1.69 % (calc total weight; evidence ['E76'])
- TMD tuned frequency: 1.83 Hz (calc Den Hartog tuning; evidence ['E14'])
- TMD optimum damping ratio: 12.0 % (calc Den Hartog damping; evidence ['E15'])
- effective damping: 6.2 % (simulate free decay; evidence ['E17'])
- TMD relative stroke: 49.4 mm (simulate free decay; evidence ['E17'])
- static sag: 74.7 mm (calc static sag; evidence ['E63'])
- sag plus stroke envelope: 124.0 mm (calc envelope; evidence ['E68'])
- bare deck acceleration: 8.28 m/s2 (calc bare resonance; evidence ['E43'])
- retrofitted acceleration: 0.67 m/s2 (simulate crowd build-up; evidence ['E45'])
- slip resistance per bolt: 32.9 kN (calc slip resistance; evidence ['E64'])
- combined bracket demand: 13.1 kN (calc combined load; evidence ['E65'])
- stop contact force: 8.4 kN (calc stop force; evidence ['E66'])

## Risks
- tuning drift loses damping — mitigation: twin units detuned about optimum hold 0.476 to 0.526 m/s2 plus annual tuning check from below
- clamp slip or preload loss under dynamics plus stop hit — mitigation: 32.9 kN slip per bolt exceeds 13.1 kN demand including 8.40 kN stop hit with annual re-torque and stop-into-beam check

## Novelty
Twin detuned masses on a single HSFG-clamped transverse beam within girder depth with caged stops and from-below service proven by crowd acceptance run

## Sources
- (none)

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=False S2 flaw=False decision=s1_retry
- attempt 0 round 1: S1 faithful=True S2 flaw=False decision=s1_pass

## Figure notes
- callouts Transverse Cross Beam, Tuned Mass, Clamp Bolt Set pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: HSFG clamp bolt set, deck accelerometer array
- how it works: 6 numbered steps drawn on panel A
- figure repair: last step must contain all parts
- fabrication step 1 passed after one redraw (first attempt: Pixels show a full portal frame: two vertical columns plus a long horizontal beam between them with end bolt groups, not an isolated short transverse cross-beam. Step 1 requires the cross-beam alone first; this is a later assembled stage with extra parts.)
