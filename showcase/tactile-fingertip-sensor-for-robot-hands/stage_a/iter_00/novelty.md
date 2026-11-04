I’ll track down the closest existing fingertip to your ridged dual‑sensing design.
A strong capacitive‑plus‑PVDF candidate surfaced — I’ll open it to confirm the match.
This looks like the closest match — now I’ll verify the remaining construction details before summarizing the differences.
Closest match is **paper + prototype:**

**SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation - Chang et al., Columbia ROAMLab, 2025, arXiv:2510.27048**

Why it is closest:

* Same functional decomposition: static + dynamic touch in one finger-scale fingertip.
> combining a taxelized and highly sensitive dynamic response (PVDF) with a static transduction method (capacitive) for multimodal touch sensing

* Same split-path mechanism: 16-taxel PVDF film sampled at 4 kHz for contact onset / break / slip / vibration, plus capacitive pads for sustained pressure:

> containing a high frequency (4 kHz), 16-taxel PVDF array embedded at the contact surface, complemented by 7 capacitive pads embedded below the PVDF for pressure sensing

>Combining high-performance, taxelized PVDF for dynamic sensing with capacitive pads for static sensing

* Same finger integration: elastomer skin over PVDF near surface, capacitive deeper:
>16-taxel PVDF array which provides very high sensitivity to high frequency events... embedded near the surface of the finger's elastomer... complement... by embedding... capacitive taxels deeper under the surface in order to provide a static pressure response

* Same on-finger electronics concept:
>on-finger electronics consist of a 2-PCB stack housed within the finger... Flat flexible cable ports interface with the capacitive sensor tails and PVDF's FPC cable. A capacitance-to-digital converter samples the capacitive sensors

vs concept: flex tail + converter + microcontroller on-finger board to hand controller.

* Same cost class: total material cost US$365 vs concept $100-1k.

* Explicitly recognizes same problem: PVDF alone as single large taxel insufficient, must complement with static modality and taxelize across finger:
>PVDF has almost exclusively been implemented... as large, off-the-shelf taxels... Challenges remain in (a) how to build taxelized PVDF sheets... (b) how to complement PVDF with a static modality

>We favor a multimodal approach with designated dynamic sensors like PVDF so that the dynamic modality can be tuned to be sensitive to small transient events, while static sensors can preserve a larger dynamic range

Second closest, for ridged skin only, is **SynTouch BioTac**: fingertip-shaped sensor filled with conductive fluid, fingerprint-like ridges on flexible elastomeric skin, vibrations induced when sliding... propagate through fluid, force via impedance + slip microvibrations via hydro-acoustic pressure sensor.

**Decisive differences of this concept vs SpikeATac:**

1. **Skin / mechanics:** Concept: molded Shore A 10 ridged dome + micro-sipes draped like cornea over flat-faceted rigid core with gel interlayer, quantified to 1 mN / 0.47 mm spot. SpikeATac: Ecoflex 00-50 cast elastomer poured in mold, PVDF adhered to flat 0.5 mm Ecoflex sheet then into surface indentation and painted over with ~3 coats Ecoflex — no ridges/sipes, no faceted draped dome, no gel interlayer specified.

2. **PVDF taxelization:** Concept: single continuous 28 um vibration film passing static pressure to underlying capacitive grid. SpikeATac: photolithographed 16-taxel PVDF array itself spatially resolved, plus only 7 discrete COTS capacitive pads below.

3. **Scale:** Concept: 20 mm dia x 22 mm fingertip. SpikeATac: 45x32x25 mm, just larger than human thumb — ~2x larger.

4. **Fail-safe messaging - novel:** Concept: heartbeat + slip-interrupt line + full frame to meet 30 ms warning, normally-held line drops on wire break per track-circuit analogy. SpikeATac has no fail-safe heartbeat/interrupt/cable; output is raw high-rate PVDF + capacitive streams for imitation / RLHF policy for delicate in-hand manipulation:
>raw SpikeATac signals can be incorporated into an imitation and reinforcement learning fine-tuning pipeline

In short: **SpikeATac proves capacitive + taxelized-PVDF dual sensing on-finger works; this concept adds ridged micro-siped dome + gel on facets + deterministic fail-safe slip interrupt instead of learning policy.**


Sources:
- https://arxiv.org/html/2510.27048 — SpikeATac: A Multimodal Tactile Finger withTaxelized Dynamic Sensing for Dexterous Manipulation
- https://www.syntouchllc.com/Products/BioTac/ — SynTouch - BioTac
- https://www.designnews.com/motion-control/video-robots-develop-sense-of-touch — Video: Robots Develop Sense of Touch
- https://mirror.umd.edu/roswiki/BioTac.html — BioTac
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10947720/ — Slip Detection and Grip Adjustment Using Optical Tracking in Prosthetic Hands
- https://www.syntouchllc.com/Media/Publications/_publications/2014_Wettels_Chapter.pdf — 
- https://www.researchgate.net/figure/A-Schematic-diagram-of-the-BioTac-biomimetic-tactile-sensor-Sensing-modalities_fig12_230599922 — | (A) Schematic diagram of the BioTac biomimetic tactile sensor.... | Download Scientific Diagram
- https://www.researchgate.net/profile/Gerald-Loeb/publication/271827182_Multimodal_Tactile_Sensor/links/56630bf608ae4931cd5ed86f/Multimodal-Tactile-Sensor.pdf — Multimodal Tactile Sensor
- https://sirslab.dii.unisi.it/papers/2014/Pacchierotti.EH.2014.Haptics.Fin.pdf — A Datadriven Approach to Remote Tactile Interaction: From a BioTac Sensor to Any Fingertip Cutaneous Device
- https://pmc.ncbi.nlm.nih.gov:443/articles/PMC3405524/ — Use of tactile feedback to control exploratory movements to characterize object compliance
- https://www.syntouchllc.com/Products/BioTac/_media/BioTac_Product_Manual.pdf — Microsoft Word - BioTac Product Manual.docx
- https://www.catalyzex.com/author/Peter%20Ballentine — Peter Ballentine
- https://arxiv.org/html/2510.27048v1 — SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation
- https://arxiv.org/pdf/2510.27048 — SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation
- https://round-lake.dustinice.workers.dev:443/https/arxiv.org/pdf/2510.27048 — SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation
- https://arxiv.org/html/2510.27048v2 — SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation
- https://git.whohe.eu.org/arxiv.org/pdf/2510.27048 — SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation
- https://www.researchgate.net/publication/224685364_Development_of_Anthropomorphic_Robot_Hand_with_Tactile_Sensor_SKKU_Hand_II — Development of Anthropomorphic Robot Hand with Tactile Sensor : SKKU Hand II
- https://www.azosensors.com/article.aspx?ArticleID=3368 — Revolutionizing Robot Touch with Advanced Tactile Sensors
- https://roamlab.github.io/spikeatac/ — SpikeATac
- http://ira.lib.polyu.edu.hk/bitstream/10397/117148/1/Leong_Tactile-sensitive_Artificial_Skin.pdf — This is the Pre-Published Version. The following publication C. Y. Leong, J. Cui, X. Cheng, L. Htein and H. -Y. Tam, "Tactile-Sensitive Artificial Skin for Multiaxial Force Detection and Texture Recognition,"
- https://dokumen.tips/documents/multimodal-tactile-sensor-syntouch-inc-tactile-sensing-in-robotic-end-effectors.html — (PDF) Multimodal Tactile Sensor - SynTouch Inc. · Tactile sensing in robotic end-effectors must meet two types of haptic requirements: those geared toward object identification and characterization - DOKUMEN.TIPS
- https://mdpi-res.com/d_attachment/sensors/sensors-11-08626/article_deploy/sensors-11-08626-v3.pdf?version=1403316092 — Artificial Skin Ridges Enhance Local Tactile Shape Discrimination
- https://static1.squarespace.com/static/59b8113fa8b2b0ac8308da3b/t/60e7acd38ad60325f0c3c321/1625795799350/79+-+2018+-+Dhong+-+Soft+Matter+-+Fingerprints.pdf — Role of fingerprint-inspired relief structures in elastomeric slabs for detecting frictional differences arising from surface monolayers
- https://www.mdpi.com/1424-8220/11/9/8626/pdf — Artificial Skin Ridges Enhance Local Tactile Shape Discrimination
- https://www.mdpi.com/1424-8220/11/9/8626 — Artificial Skin Ridges Enhance Local Tactile Shape Discrimination
- https://www.allaboutcircuits.com/news/can-this-skin-sensor-give-robotics-and-prosthetics-a-delicate-touch/ — Can This Skin Sensor Give Robotics and Prosthetics a Delicate Touch?
- https://www.newscientist.com/article/1897299-bionic-hands-get-the-sensitive-touch/ — Bionic hands get the sensitive touch