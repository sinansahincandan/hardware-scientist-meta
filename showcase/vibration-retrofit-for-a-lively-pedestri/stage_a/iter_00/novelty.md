I’ll hunt for the closest existing TMD footbridge retrofits to compare against your twin under-deck concept.
That search surfaced a near-identical span and twin-mass layout — I’ll open the sources to verify the details.
Closest existing work:

**Paper + Product: Lee et al. - `Effective Vibration Control of Existing Footbridge Using Tuned Mass Damper` + KR-manufactured TMD pair, also sold as DEICON-type under-deck pedestrian TMD.**

Paper:

> simple steel box-girder bridge with main span 44.6m, light weight 25.3 kN/m, pedestrian resonance at fundamental mode resulting in unacceptable accelerations

> A set of two 500 kgf vertical TMDs was manufactured by KR and installed into the railings next to the central section

> installation reduced peak acceleration in the meeting box to less than 90% [of bare value]

Presents itself as measure for retrofitting footbridges to make them more friendly to users.

Closest commercial product:

DEICON pedestrian bridge TMD:

> TMDs are specialized tuned damping devices commonly used for abating vibration at a particular natural frequency, comprising inertia element suspended by restoring element and energy dissipating device

> DEICON designed and fabricated two tuned mass dampers with combined moving mass of 500 kg installed at bridge midspan adjacent to two main girders

> TMDs installed underneath, near edge of balcony

> Integrating units within bridge structure allowed system to remain concealed while maintaining direct influence over dominant modal responses

> field measurements acceleration data with TMDs locked then unlocked and operational, effective damping increased by nearly factor 3 for 1.1 Hz mode

### Why this is closest

* Same problem: existing lively lightweight footbridge in resonance, unacceptable comfort.
* Same scale: 44.6 m span vs concept 40 m span.
* Same solution architecture: **twin vertical TMDs, ~400-500 kg each, 800-1000 kg total, at midspan / central section, hidden / integrated.**
* Same verification: before/after accelerometer at midspan, locked vs unlocked.

Other examples are farther:

* London Millennium: 37 fluid-viscous + 52 TMD under deck - same under-deck concealment, Rather than altering silhouette, Arup retrofitted underside with 37 viscous + 52 TMDs, but distributed multi-mode lateral + vertical system for very large bridge, not twin 800 kg retrofit.
* Bagers Plats Malmö: 2 TMDs x 340 kg, lowest vertical 1.85 Hz - very close frequency to 1.9 Hz concept, but new design, not 40 m retrofit with clamped cross-beam.
* Eagles Meadow: TMD bolted most effective location, fitted as close as possible to point of maximum displacement under deck between two main beams - same placement logic, but single TMD, not twin detuned MTMD.

### Difference from concept

Concept is a **specific robust MTMD + weld-free install + acceptance package** not in prior work:

1.  **Twin detuned vs twin identical:** Concept deliberately detunes pair about 1.83 Hz for MTMD robustness to hold 0.476-0.526 m/s2 under drift. Prior twin uses two identical units - e.g. Two identical TMD units 480 kg, fTMD 1.6 Hz, or two 500 kgf units, no detuned band claim.
2.  **Hidden under-deck HSFG-clamped cross-beam:** Concept carries 7.85 kN static + 5.22 kN dynamic into girders as shear via 4x M20 HSFG, 32.9 kN slip/bolt, no weld, no deck change, 124 mm sag+stroke envelope within girder depth. Korean units installed into railings next to central section, not under-deck clamped beam. DEICON units installed adjacent to girders in housing cavity, no HSFG cross-beam, travel stop, fatigue clamp detail disclosed.
3.  **Quantified Medium-comfort retrofit:** 8.28 m/s2 -> 0.67 m/s2, 6.2% effective damping, 12.0% optimum, 49.4 mm travel, 80 mm gap stop for 8.4 kN hit. Prior work reports only relative reduction <90% and damping x3, no 0.5-1.0 m/s2 Medium band filing, no stop / lock-pin / BBAV annual re-tune maintenance chain.


Sources:
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf — | Pedestrian Bridge Vibration |  |  |
- https://koreascience.kr/article/CFKO200311922784278.pub — Effective Vibration Control of Existing Footbridge Using Tuned Mass Damper
				-Proceedings of the Korean Society for Noise and Vibration Engineering Conference
			
		
	 | 학회
- https://www.academia.edu/110792396/Implementation_of_a_Passive_Control_System_in_a_Lively_Footbridge — Implementation of a Passive Control System in a Lively Footbridge
- https://structechnique.com/download/15/free/aO4RBDPc — Retrofitting Eagles Meadow Bridge with a Tuned Mass Damper
- https://structurae.net/fr/litterature/papier-de-conference/economic-approach-to-damping-trail-style-footbridges/apercu-download?download=false — [PREVIEW] Economic Approach to Damping Trail-Style Footbridges 
- https://structurae.net/fr/litterature/papier-de-conference/design-and-construction-of-the-stadium-footbridge-st-helens-uk — The
Design and Construction of the Stadium Footbridge, St Helens, Uk | Structurae
- https://www.academia.edu/53208173/Design_of_a_Semi_active_Tuned_Mass_Damper_for_the_Science_Museum_Footbridge_of_Valladolid — Design of a Semi-active Tuned Mass Damper for the Science Museum Footbridge of Valladolid
- https://link.springer.com/chapter/10.1007/978-3-031-96114-4_73 — Multi-Passive Tuned Mass Damper for Single-Mode Control of Slender Lab-Scale Timber Footbridge
- https://www.oasys-software.com/?p=15356 — Structural design and dynamic assessment of an asymmetric cable-stayed footbridge using Oasys GSA
- https://idus.us.es/bitstream/handle/11441/36164/CMMoST%202015_Jimenez-Alonso_Estimating.pdf?sequence=1&isAllowed=y — Estimating robust optimum parameters of tuned mass dampers using multiobjective genetic algorithms
- https://koreascience.or.kr/article/CFKO200311922784278.page?&lang=en — Effective Vibration Control of Existing Footbridge Using Tuned Mass Damper
				-Proceedings of the Korean Society for Noise and Vibration Engineering Conference
			
		
	 | Korea Science
- https://1library.net/article/additional-damping-devices-modification-of-structural-damping.zpgj1mrz — Additional damping devices - Modification of structural damping
- https://timenote.info/en/Millennium-Bridge-London — Millennium Bridge, London
- https://www.thefreelibrary.com/Lateral+Vibration+Control+of+Long-Span+Small-Radius+Curved+Steel+Box...-a0729497874 — Lateral Vibration Control of Long-Span Small-Radius Curved Steel Box Girder Pedestrian Bridge with Distributed Multiple Tuned Mass Dampers. - Free Online Library
- https://www.vibratec.org/article/case-study-tuned-mass-dampers-for-pedestrian-bridge-in-malmo/ — Case Study: Tuned Mass Dampers for Pedestrian Bridge in Malmö
- https://thuvien.huce.edu.vn/kiposdata1/Baotapchi/Tapchinuocngoai/Journal%20of%20Bridge%20Engineering/2016/Journal%20of%20Bridge%20Engineering.Vol%2021.Iss%208/PDF/Journal%20of%20Bridge%20Engineering.Vol%2021.Iss%208.A7.pdf — Numerical and Experimental Evaluation of the Dynamic Performance of a Footbridge with Tuned Mass Dampers
- https://www.scilit.net/publications/55e8222a5fb04eca89ebaefa665d9e58 — Vibration control of a slender footbridge using passive and semiactive tuned mass dampers
- https://www.mub.eps.manchester.ac.uk/structural-concepts/vibration-reduction/ — Vibration Reduction
- https://www.alexandria.press/read/latent-fragility/the-synchronized-footbridge.html — The Synchronized Footbridge
- https://eureka.patsnap.com/patent-CN104929268B — A frequency continuously adjustable mass damper - Eureka | Patsnap
- https://bwk.kuleuven.be/apps/bwm/eurodyn2011/papers/MS09-531.pdf — Vibration mitigation by means of hysteretic tuned mass dampers
- https://mediatum.ub.tum.de/doc/1762603/document.pdf — Tuned Mass Dampers for Vibration Control of
- https://dspace.vut.cz/server/api/core/bitstreams/fe91b2bb-e77d-41e7-847d-e32cfb3c7d2a/content — Tuned mass dampers ‐ evaluation of the effect on two real footbridges
- https://www.fullscaledynamics.com/project/vibration-simulations-and-tuned-mass-damper-design-for-castle-bridge-bristol/ — Vibration Simulations and Tuned Mass Damper Design for Castle Bridge, Bristol
- https://patents.google.com/patent/CN104929268A/en — CN104929268A - Frequency continuously adjustable mass damper 
        - Google Patents
- https://files.kgf.cz/yrlh8n556n12/Tuned%20Mass%20Damper%20-%20Evaluation%20of%20the%20Effect%20on%20two%20real%20Footbridges%20%28TMD%29_Conference%20Steel%20Bridges%202024_KGF%20hydraulika.pdf?download — Untitled
- https://pure.tue.nl/ws/files/46926621/638689-1.pdf — Eindhoven University of Technology MASTER Effect of tuned mass dampers in footbridge design