# Rationale — 40 cm soft-stall rotor with 170-180 Kv feed and 0.80 N-m spring-disc plus dump shutdown

Build a 40 cm wind turbine that fits in a 45 cm cube, makes regulated power from 5 to 11 m/s, survives 22 m/s, and shuts down below 10% speed within 10 s on command or load loss and stays parked.

## Key estimates
- shaft power at 5 m/s: 3.27 W (calc; evidence ['E11'])
- shaft power at 11 m/s: 34.7 W (calc; evidence ['E12'])
- regulated load power at 11 m/s: 22.1 W (calc; evidence ['E66'])
- low-wind regulated power: 2.08 W (calc; evidence ['E80'])
- rotor speed at 5 m/s: 1430.0 rpm (calc; evidence ['E14'])
- rotor speed at 11 m/s: 3150.0 rpm (calc; evidence ['E13'])
- revised volts low to top: 8.41 V (calc; evidence ['E76'])
- survival thrust at 22 m/s: 37.3 N (calc; evidence ['E22'])
- overturning moment at post clamp: 13.1 N m (calc; evidence ['E23'])
- post tip deflection: 0.516 mm (vetted_calc; evidence ['E26'])
- bending stress in post: 16.6 MPa (calc; evidence ['E27'])
- side clearance per side: 2.5 cm (calc; evidence ['E74'])
- axial stack length: 36.0 cm (calc; evidence ['E52'])
- stop time to 315 rpm: 0.673 s (simulate; evidence ['E70'])
- dump power at 18.5 V top: 85.6 W (calc; evidence ['E78'])
- brake disc temperature rise: 4.35 K (calc; evidence ['E53'])

## Risks
- Dump-only brake gives zero torque at zero speed and runs away at 22 m/s — mitigation: Use combined 0.80 N-m spring disc plus 4 ohm dump with soft-stall blades keeping parked torque near 0.25 N-m below hold
- 220 Kv low-wind volts 6.50 V starve regulator and false-trip load sense — mitigation: Rewind to 170-180 Kv giving 8.41 V low to 18.5 V top inside 8-40 V regulator window

## Novelty
Locomotive rheostatic dump-grid feed plus elevator safety-chain normally-closed latching sense transferred to model scale with spring-applied disc plus soft-stall rotor for fail-safe stop and park.

## Sources
- (none)

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

Fabrication steps not shown because they failed their light check: [3, 4]

## Figure notes
- callouts Three Blade Rotor pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: Direct-drive outrunner generator, Three-phase rectifier bridge, Buck-boost regulator, Dump resistor grid, Normally closed safety chain loop
- how it works: 6 numbered steps drawn on panel A
- fabrication step 2 passed after one redraw (first attempt: Pixels show a later complete assembly, not step-2 bedplate stage: spinning 5-blade rigid hub, long shaft through two-bearing housing on bedplate, plus disc brake on rails with caliper, plus rear generator and post/clamp. Step-2 parts are present but with extra rotor blades and generator installed and operating.)
- fabrication step 3 not shown: failed its light check twice (Pixels show four black blades on the spherical spinner hub, not a three-blade fixed-pitch rotor, so it does not match fabrication step 3 parts/stage.)
- fabrication step 4 not shown: failed its light check twice (Pixels fail parts/stage/scale: 4-blade blurred rotor not 3-blade; long extended jack-shaft with separate pillow-block bearings and mid disc, not rigid hub direct-drive outrunner; external yellow/red/black wiring on top of bedplate not threaded inside nacelle/post bore; hanging metal link-chain on generator, not normally-closed electrical safety loop; scale vs grey hand silhouette shows meter-class machine, not ~400mm across.)
