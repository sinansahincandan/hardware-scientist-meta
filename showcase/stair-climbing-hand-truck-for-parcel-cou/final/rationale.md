# Rationale — Tri-star climber with fail-safe brake, strapped toe plate and mid-spine fold operated at 15 deg lean

Move a 60 kg parcel up and down residential stairs with one courier, control descent without runaway, carry load with safety margin, and fold flat to van niche with liftable tare.

## Key estimates
- lever effort over nosing: 226.0 N (simulate stair heave; evidence ['E58'])
- straight slope pull: 441.0 N (simulate stair slope; evidence ['E58'])
- brake holding torque: 98.9 N m (simulate brake hold; evidence ['E58', 'E50'])
- tip margin at 15 deg lean: 6.8 deg (simulate tip margin; evidence ['E60'])
- spine bending stress per tube: 30.6 MPa (calc bending stress; evidence ['E61', 'E41'])
- spine safety factor: 9.02 ratio (calc safety factor; evidence ['E62'])
- tare weight: 7.38 kg (calc tare budget; evidence ['E40', 'E52'])
- hinge pin double shear stress: 36.6 MPa (calc pin shear; evidence ['E54'])
- energy per 0.2 m riser: 141.0 J (simulate energy; evidence ['E58'])

## Risks
- Tip backward on stairs if leaned past tip angle — mitigation: Operate at 15.0 deg lean against 21.8 deg tip for 6.8 deg margin
- Runaway descent on nosing if grip released — mitigation: Fail-safe friction brake plus pawl springs locked on release, sized to 198 N m
- Mid-spine fold unlocks under stair load — mitigation: Over-centre plates with spring detent pin and green-red indicator, pin stress 36.6 MPa

## Novelty
Tri-star climber combining fail-safe carrier brake with single-hinge flat-fold spine and strapped toe for van operation

## Sources
- https://www.ajproducts.ie/p/compact-aluminium-stair-climbing-sack-truck-440578-440576
- https://www.ajproducts.co.uk/p/compact-aluminium-stair-climbing-sack-truck-440578-440576
- https://www.robertdyas.co.uk/special-categories/blue-sack-truck?category=516
- https://www.huntoffice.ie/hand-trucks
- http://www.qdmaterialhandling.com/Sack-Trucks-Foot-Stairclimber-120Kg-Capacity-136.html
- https://brand-supermarket.com/review/Draper-Heavy-Duty-Stair-Climbing-Sack-Truck-Trolley.html
- https://www.diy.com/departments/heavy-duty-stair-climber-sack-truck-steel-yellow-frame-3-linked-wheels-folding-toe-plate-for-extra-storage-200kg-capacity/5060139810678_BQ.prd
- https://www.screwfix.com/c/storage-ladders/hand-trucks/cat831506
- https://uk.bestproducts.reviews/stair-climbing-carts
- https://www.Toolstation.Com/stair-climbing-sack-truck/p87414
- https://www.amazon.com/dp/B0BVV667V9/ref=cm_sw_r_cso_fb_apan_dp_H8787YC87AXTX0YZ8J7G
- https://device.report/manual/8505570
- https://top5best.com/stair-climbing-dolly
- https://www.amazon.com/dp/B0FS71JTYF/ref=cm_sw_r_cso_fm_apin_dp_M09285ZZASCT07Y0BYHW
- https://hasslefreehouse.com/best-stair-climbing-hand-truck
- https://www.amazon.com/dp/B0FP228P3S/ref=sr_1_9
- https://www.amazon.com/dp/B0FS71JTYF/ref=cm_sw_r_cso_cp_apan_dp_W24SGN6G4QCAJEW57NB0
- https://www.bestsportsgearpicks.com/stair-climbing-carts
- https://patentcut.com/US8764028
- https://www.bestreviews.guide/stair-climbing-carts
- https://www.patentsencyclopedia.com/app/20100108412
- https://patents.google.com/patent/US20250027320A1/en
- https://patents.google.com/patent/CN86201871U/en
- https://patentimages-storage-googleapis-comproxy.boingomedia.com/79/e3/4e/0cda66b16bfc58/US3512658.pdf
- https://eureka.patsnap.com/patent-CN106080725A
- https://patents.google.com/patent/US2772096A/en
- https://patents.google.com/patent/AU2023207606A1/en
- https://patents.google.com/patent/US3191953A/en
- https://patents.google.com/patent/US11794798B2/en
- https://patentcut.com/6837337
- https://patents.google.com/patent/DE19951914A1/en

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

## Figure notes
- callouts Brake Band Pawl, Fold Hinge Lock, Harness Strap pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: toe plate 450x350
