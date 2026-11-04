# Rationale — Manual tri-star hand truck v4 for one courier with 60 kg parcel

Provide a one-courier manual truck that carries a 60 kg parcel up domestic stairs, rolls on flat, locks hands-off on slopes, and stows flat in a small van.

## Key estimates
- total lifted mass and weight: 67.1 kg and N (sum tare plus parcel and weight conversion; evidence ['E121', 'E122'])
- unified parcel moment: 118.0 N m (parcel weight times 200 mm offset; evidence ['E90'])
- backbone stress with impact: 40.9 MPa (bending stress with 1.5 impact for 40 mm tubes; evidence ['E118'])
- deployed tip whip: 43.9 mm (cantilever deflection with twin 40 mm tube inertia; evidence ['E116'])
- stair work slope and total lock: 129.0 J and N m (total mass energy and slope times cluster radius; evidence ['E96', 'E123', 'E124', 'E132'])
- hand release force: 57.4 N (clamp with lever ratio and cable efficiency; evidence ['E101'])
- folded length: 1145.0 mm (stacked folded dimensions and diagonal entry; evidence ['E104', 'E105', 'E106', 'E109'])

## Risks
- Tired hand cannot hold 188 N descent load by grip alone — mitigation: Hold slope in spring-applied disc plus tooth pin with 57.4 N release and hands-off auto-lock, verify by bench test
- 110 mm whip mistimes cluster nose contact and 1100 mm backbone cannot enter straight through door — mitigation: Upsize to one-piece 40 by 36 mm tubes for 43.9 mm whip under quarter riser and accept 1150 mm diagonal stow

## Novelty
Proven tri-star walking with twin-tube backbone plus spring-applied disc with positive tooth lock for hands-off holding and folding toe plus sliding handle for diagonal van stow, beyond fixed-frame 60 kg stair truck with skids.

## Sources
- (none)

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

Fabrication steps not shown because they failed their light check: [3, 4]

## Figure notes
- callouts Folding Toe Plate, Tri Star Cluster, Main Cluster Axle, Disc Tooth Brake, Dead Man Lever, Telescoping Push Handle pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: folding toe plate, dead-man brake lever with cable
- how it works: 6 numbered steps drawn on panel A
- critical part was not located in the render; panel B omitted
- fabrication step 1 passed after one redraw (first attempt: Pixels show far beyond step 1: twin tubes present but also assembled toe platform, diagonal brace, main gear/cluster, spring, swivel wheeled base and upper handles. Step 1 is only backbone tubes + axle mounts. Scale is plausible vs silhouette, but stage/parts fail.)
- fabrication step 2 passed after one redraw (first attempt: Pixels show twin-tube backbone, folding toe-plate, and root/cluster axle BUT also fully-built hardware: handle with brake lever, telescopic sections with locks, linkage struts, gear, spring, foot/base. That is a complete device, not the step-2 subassembly of backbone+toe-plate+axle. Stage mismatch.)
- fabrication step 3 not shown: failed its light check twice (From the pixels the twin-tube backbone, main axle, two tri-star clusters and large toothed disc with pinion are visible at plausible scale vs the grey silhouette, but no folding toe plate is visible. The listed part set for step 3 is therefore not shown.)
- fabrication step 4 not shown: failed its light check twice (Missing tri-star wheel cluster and main cluster axle - base shows only small swivel casters, not a 3-wheel star cluster, so parts list for step 4 fails despite cable slack loop, strap and brace being visible.)
