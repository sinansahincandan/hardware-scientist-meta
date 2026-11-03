# Rationale — Integrated wheeled drum rover with rear high-lift hopper dump

Drive over loose BP-1 simulant, excavate with low force, operate with no line-of-sight by remote link, and carry and high-lift dump regolith within 60 kg and 1.0 by 0.5 by 0.5 m start envelope.

## Key estimates
- sortie energy: 170.0 Wh (calc; evidence ['E32'])
- pack specific energy: 90.6 Wh/kg (calc; evidence ['E34'])
- reconciled total mass: 53.0 kg (calc; evidence ['E37'])
- runtime at full load: 1.41 h (calc; evidence ['E36'])
- actuator force total: 735.0 N (calc; evidence ['E41'])
- actuator input work: 110.0 J (calc; evidence ['E42'])
- useful lift energy: 88.3 J (calc; evidence ['E38'])
- tip stability factor: 4.66 ratio (calc; evidence ['E43'])
- front axle residual mass: 16.9 kg (calc; evidence ['E40'])
- nominal ground pressure: 9820.0 N/m2 (calc; evidence ['E10'])
- robot weight at 60 kg: 589.0 N (calc; evidence ['E9'])
- drawbar pull ratio: 0.0662 ratio (calc; evidence ['E12'])
- stopping distance: 0.25 m (calc; evidence ['E19'])
- autonomy power share: 29.0 W (calc; evidence ['E20'])
- autonomy mass share: 1.73 kg (calc; evidence ['E21'])

## Risks
- Single drum 39 N reaction slips wheels or raises power — mitigation: Keep cut shallow near 30 mm and hopper load centred
- Raised 15 kg load tips over rear axle due to moment-arm sensitivity — mitigation: Fix overhang at 0.30 m and wheelbase at 0.70 m and verify by deployed side sketch to 1.05 m
- Sortie energy and pack mass do not close under limit — mitigation: Use purchasable 480 Wh pack for 1.41 h margin and re-sum mass

## Novelty
Combination of front transverse drum with central hopper on rear high-lift mast plus folding 1.0 m perception mast with heartbeat stop-hold in 60 kg wheeled rover

## Sources
- (none)

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

## Figure notes
- callouts Rear lift mast pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: Front transverse digging drum, 24 V battery pack
