# Rationale — Integrated hand truck with sized brake linkage

Lift and lower 60 kg load step by step on stairs with one operator, hold without grip, fold flat under 15 kg for van stowage.

## Key estimates
- energy to lift 60 kg one riser: 100.0 J (calc; evidence ['E12'])
- tri-star cluster torque: 184.0 N m (calc; evidence ['E13'])
- handle pull from cluster torque and 1.2 m lever: 153.0 N (calc; evidence ['E30'])
- hand pull with 15 to 1 worm and 0.25 m crank: 98.1 N (calc; evidence ['E49'])
- pawl tooth force from cluster torque: 6130.0 N (calc; evidence ['E54'])
- dead-man lever force from worm shaft torque: 61.3 N (calc; evidence ['E55'])
- crank turns per step: 5.0 turns (calc; evidence ['E56'])
- frame bending moment estimate 60kg at 0.5m: 294.0 N m (calc; evidence ['E31'])
- factored moment for SF2: 588.0 N m (calc; evidence ['E50'])
- required section modulus SF2: 2.45 cm3 (calc; evidence ['E52'])
- section modulus one tube: 1440.0 mm3 (calc; evidence ['E53'])
- twin-tube modulus margin vs SF2 requirement: 1.18 ratio (calc; evidence ['E60'])
- unfactored bending stress twin tubes: 102000000.0 Pa (calc; evidence ['E61'])
- total device mass from parts breakdown: 11.3 kg (calc; evidence ['E57'])
- pin double shear stress for fold lock: 27.1 MPa (calc; evidence ['E59'])
- lift energy 15 kg device into van floor 0.6 m: 88.3 J (calc; evidence ['E46'])
- reduction ratio to bring handle pull below target: 1.7 ratio (calc; evidence ['E47'])

## Risks
- handle effort overrun on tri-star cluster — mitigation: use 15 to 1 worm with 0.25 m crank to give 98.1 N below 150 N limit
- thin 1.18 margin and pin collapse on stairs — mitigation: use two tubes giving 2.88 cm3 against 2.45 cm3 required with steel pins
- descent runaway if brake linkage fails — mitigation: hold with self-locking worm plus pawl and 61.3 N dead-man squeeze with uphill stance

## Novelty
Integrated hand truck with tri-star cluster, self-locking worm plus pawl crank and 2-step flat fold

## Sources
- https://www.bestbuy.ca/en-ca/product/vevor-3-in-1-industrial-convertible-stair-climbing-cart-770-lbs-max-load-folding-hand-truck-dolly-with-handle-wheels-stair-climbing-utility-trolley-for-moving-orange-silver/19783042
- https://www.desertcart.tw:443/products/662036546-stair-climbing-hand-truck-440lb-heavy-duty-dolly-cart-stairs
- https://www.amazon.com/dp/B0C66JTD46/ref=btn_assoc_p-facebook_o-1_srctok-8d7973459d7525dc_ht-t
- https://www.amazon.com/dp/B0DSVY7WYR/ref=cm_sw_r_cso_cp_apan_dp_0GWY1AVDRC004T6DYAEY
- https://www.amazon.com/dp/B0C66JTD46/ref=btn_assoc_p-facebook_o-1_srctok-90ef7b2f582d2525_ht-t
- https://www.amazon.com/dp/B0GCCZF5XL/ref=sspa_mw_detail_1
- https://www.amazon.com/dp/B0DSVY7WYR/ref=cm_sw_r_cso_cp_apin_dp_WKMBXCQW250DXZQAEGMQ
- https://www.vevor.com.au/stair-climbing-cart-c_10486/vevor-stair-climbing-cart-150-kg-stair-climb-capacity-aluminum-alloy-folding-trolley-cart-with-telescoping-handle-6-wheels-and-2-bungee-cords-stair-climber-dolly-for-home-groceries-warehouse-p_010923682480
- https://www.vevor.com/stair-climbing-cart-c_10486/vevor-stair-climbing-cart-220-lbs-stair-climbing-capacity-heavy-duty-folding-trolley-cart-with-telescoping-handle-6-wheels-and-2-bungee-cords-stair-climber-dolly-for-home-groceries-warehouse-p_010353528239
- https://eureka.patsnap.com/patent-CN108995697A
- https://patents.google.com/patent/CN110240046B/en
- https://patents.google.com/patent/EP0099061B1/ja
- https://patents.google.com/patent/DE102010054328A1/en
- https://patents.Google.Com/patent/US3288234A/en
- https://www.patentsencyclopedia.com/app/20100294575
- https://patents.google.com/patent/CN103192915A/en
- https://patents.google.com/patent/US4960179A/en
- https://eureka.patsnap.com/patent-CN109484511B
- https://patents.google.com/patent/CN216232654U/en
- https://patents.google.com/patent/CN86201871U/en
- https://eureka.patsnap.com/patent-US20130192907A1
- https://eureka.patsnap.com/patent-US20130274973A1
- https://eureka.patsnap.com/patent-US20100032911A1
- https://patentcut.com/US8764028
- https://patentimages-storage-googleapis-comproxy.c9w.net/a4/4a/8d/0fb55c7af7ac6a/US4264082.pdf
- https://patents.google.com/patent/CA2644990A1/en
- https://patents.google.com/patent/CN205819271U/en
- https://patents.google.com/patent/EP1996440A1/en
- https://www.patentsencyclopedia.com/app/20180229745

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

Fabrication steps not shown because they failed their light check: [1, 2, 3]

## Figure notes
- no measurement chain recorded; panel C omitted
- fabrication step 1 failed its light check (Pixels show vertical twin blue tubes on a steel hinge with a ring quick-pin on a bench fixture, but no L-frame configuration and no distinct skid pads are visible as separate parts.); not shown
- fabrication step 2 failed its light check (Pixels show twin-tube frame with blue pads and green toe plate and a single open pistol-grip with brake lever, not a telescopic closed-loop handle; exact step-2 parts list not met.); not shown
- fabrication step 3 failed its light check (Pixels do not show step-3 assembly as described: handle is an open single-grip lever with dead-man brake, not a telescopic closed-loop handle; no worm-axle crank is mounted; left cluster shows 4 solid wheels not a 3-wheel tri-star; quick pins and skid pads are loose parts/tools on bench, not mounted as listed.); not shown
- labels removed because they pointed at the wrong part: self-locking worm drive plus pawl
