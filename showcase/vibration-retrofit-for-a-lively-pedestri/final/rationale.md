# Rationale — Under-deck vertical tuned mass damper at midspan on bolted clamp frame with staged install

40 m footbridge first vertical mode at 1.9 Hz lies in walking range with low damping and exceeds comfort under crowd loading, requiring concealed supplemental damping with staged retrofit without full closure

## Key estimates
- modal mass: 20000.0 kg (assumption for stiffness scaling; evidence ['E11'])
- modal stiffness at 1.9 Hz: 2850000.0 N/m (calc; evidence ['E11'])
- TMD mass: 500.0 kg (calc from 2.5 percent ratio; evidence ['E22', 'E54'])
- TMD tuning frequency: 1.85 Hz (Den Hartog tuning calc; evidence ['E23', 'E54'])
- TMD damping ratio: 0.0956 ratio (Den Hartog optimum re-check; evidence ['E54'])
- TMD stiffness: 67824.9 N/m (Den Hartog calc; evidence ['E24', 'E54'])
- TMD viscous coefficient: 1090.0 N s/m (Den Hartog calc; evidence ['E24'])
- TMD weight: 4900.0 N (calc; evidence ['E35'])
- factored frame design load: 12300.0 N (calc; evidence ['E36'])
- single-walker bare acceleration: 1.75 m/s2 (simulate resonant response; evidence ['E47'])
- single-walker TMD-controlled acceleration: 0.103 m/s2 (simulate resonant response; evidence ['E47'])
- dense-crowd resonant force: 1480.0 N (calc dense crowd scaling; evidence ['E50'])
- dense-crowd bare acceleration: 9.26 m/s2 (calc dense crowd scaling; evidence ['E51'])
- dense-crowd TMD-controlled acceleration: 0.545 m/s2 (calc dense crowd scaling; evidence ['E52'])
- dense-crowd stroke: 20.1 mm (calc dense crowd scaling; evidence ['E53'])
- static spring sag: 72.3 mm (calc; evidence ['E55'])
- total spring compression static plus dynamic: 92.4 mm (calc; evidence ['E56'])

## Risks

## Novelty


## Sources
- (none)

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

## Figure notes
- callouts Helical Support Springs pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: transverse bearer frame
- no measurement chain recorded; panel C omitted
