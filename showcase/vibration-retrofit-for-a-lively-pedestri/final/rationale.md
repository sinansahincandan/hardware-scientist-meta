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
- https://oa.upm.es/84638/1/10218266.pdf
- https://www.externalworksindex.co.uk/entry/139497/CTS-Bridges/Warren-truss-footbridge-over-Tamworth-railway/
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://structechnique.com/download/15/free/aO4RBDPc
- https://bwk.kuleuven.be/apps/bwm/eurodyn2011/papers/MS09-531.pdf
- https://iopscience.iop.org/article/10.1088/1755-1315/1205/1/012051/pdf
- https://mdpi-res.com/d_attachment/actuators/actuators-15-00389/article_deploy/actuators-15-00389.pdf?version=1783689180
- https://core.ac.uk/download/pdf/51398928.pdf
- https://idus.us.es/bitstream/handle/11441/36164/CMMoST%202015_Jimenez-Alonso_Estimating.pdf?sequence=1&isAllowed=y
- http://fstructures.com/structures/pedestrian-bridge-vibration-dynamics/
- https://www.scribd.com/document/381300829/Banff-Suspension
- http://www.electronicsandbooks.com/edt/manual/Magazine/J/Journal of Sound and Vibration/2010_v329/19/4068-4092.pdf
- https://www.research.unipd.it/retrieve/e14fb26a-9712-3de1-e053-1705fe0ac030/morb.pdf
- https://608698.6bgr9ubv.asia/bitstream/handle/20.500.12065/3213/Characteristic%20Vertical%20Response%20of%20a%20Footbridge%20Due%20to%20Crowd%20Loading.pdf?sequence=1&isAllowed=y
- https://structurae.net/en/literature/conference-paper/dynamic-analysis-of-the-bercy-tolbiac-footbridge
- https://www.researchgate.net/publication/238523383_Characteristic_Vertical_Response_of_a_Footbridge_Due_to_Crowd_Loading
- https://core.ac.uk/download/pdf/43096651.pdf
- https://www.youtube.com/watch?v=_XIA65v_Pd8
- https://patents.google.com/patent/CN215714562U/en
- https://patents.google.com/patent/CN112227180A/en
- https://patents.google.com/patent/CN109518826A/en
- https://eureka.patsnap.com/patent-CN103410091A
- https://patents.google.com/patent/CN211472127U/en
- https://www.patentsencyclopedia.com/app/20130061466
- https://eureka.patsnap.com/patent-CN109869438A
- https://eureka.patsnap.com/patent-CN103276664A
- https://eureka.patsnap.com/patent-CN107354867B
- https://patents.google.com/patent/CN103774771A/en
- https://patents.google.com/patent/US6292967B1/en

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

## Figure notes
- callouts Bridge Deck, Transverse Bearers, Helical Springs, Viscous Dashpots, Clamp Bolts pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: HS bolts, dashpots 1090 Ns/m, removable cover
- critical part was not located in the render; panel B omitted
- no measurement chain recorded; panel C omitted
- fabrication step 3 passed after one redraw (first attempt: Pixels show a bench-top workshop mockup with a small beam, 2 helical springs, 2 dashpot cylinders, a steel block mass on a plate with loose bolts/shims/tools, but no existing footbridge deck and girders, no transverse bearer beams in-situ, no removable under-deck cover fitted below, and not the unlock-mass-for-operation stage under a bridge.)
