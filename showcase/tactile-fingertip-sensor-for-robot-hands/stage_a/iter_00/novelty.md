Pinpointing your closest existing touch sensor match — I'll compare proven designs to your dual-mode concept.
I found two strong candidates — a research finger and a commercial product — so I'll dig into their details to nail down the differences.
Closest match is **paper:**

> **SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation** — Chang et al., Columbia ROAM + CLUE labs, arXiv 2510.27048 (2025).

Why it is closest:

* Same working principle: `multimodal tactile finger combining a taxelized and highly sensitive dynamic response (PVDF) with a static transduction method (capacitive) for multimodal touch sensing`.
* Same dual transduction physics claimed: `Combining high-performance, taxelized PVDF for dynamic sensing with capacitive pads for static sensing`.
* Same use of charge amplifiers for PVDF: `use charge amplifiers to measure the charge generated at each electrode, therefore measuring applied strain`, with `high-pass filter behavior` to be `very sensitive to transients without permanently saturating`.
* Same target function: fast / delicate grasp and slip / contact-onset detection: `provides fast, sensitive dynamic signals to the very onset and breaking of contact`, `detect the precise moment of initial contact`.

**Difference vs. this concept:**

1. **Taxelization is inverted:**
   * SpikeATac: `core feature is a 16-taxel PVDF array` `complemented by 7 commercial off-the-shelf (COTS) capacitive taxels deeper under the surface`.
   * This concept: dense **48 static capacitive taxels** at 2.5 mm pitch (6x8) + **single** untaxelized PVDF vibration film, scanned at 25 Hz static / 2 kHz dynamic.

2. **Spring / dielectric:**
   * Concept claims decisive choice of `soft air-gap molded pillars at 20 kPa effective stiffness as both spring and sensing gap` to get 1 mN to 2.66 fF.
   * SpikeATac uses elastomer finger with embedded PVDF near surface and COTS capacitive pads underneath, not a molded air-gap pillar array as combined spring-gap.

3. **Form-factor / mount / interface:**
   * SpikeATac: `At 45 × 32 × 25 mm (length × width × thickness), SpikeATac is just larger than a human thumb`, `finger-shaped` with `180° sensing coverage`, plus optional `accelerometer inside the finger` connected to a `nail feature for surface exploration`.
   * This concept: ~15x20 mm flat fingertip cartridge, `stiff bolted rigid core and holder with replaceable ridged skin cap and rear-exit` 4-wire tail, `6x8 row-column multiplexing to a single 4-wire bus` — quick-change cap + bus architecture not in SpikeATac.

Closest **product** runner-up is Robotiq TSF-85: `Pressure is read across a 28-taxel capacitive array for contact shape and intensity. Vibration is sampled at 1000 Hz to detect slip. An IMU tracks fingertip orientation`, rated `over 1.5 million cycles` — same static+ vibration fingertip idea, but 28 vs 48 taxels, 1000 Hz vs 2000 Hz, no disclosed air-gap pillar + PVDF film split.


Sources:
- https://roamlab.github.io/spikeatac/ — SpikeATac
- https://robotiq.com/contact-core-robotiq — Contact Core | Robotiq
- https://arxiv.org/pdf/2510.27048v2 — SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation
- https://arxiv.org/html/2510.27048 — SpikeATac: A Multimodal Tactile Finger withTaxelized Dynamic Sensing for Dexterous Manipulation
- https://arxiv.org/pdf/2510.27048v3 — SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation
- https://export.arxiv.org/pdf/2510.27048 — SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation
- https://round-lake.dustinice.workers.dev:443/https/arxiv.org/pdf/2510.27048 — SpikeATac: A Multimodal Tactile Finger with Taxelized Dynamic Sensing for Dexterous Manipulation
- https://www.catalyzex.com/author/Eric%20T.%20Chang — Eric T. Chang
- https://robotiq.com/physical-ai — Physical AI | Robotiq
- https://robotiq.com/iq-platform — IQ AI-enabled platform that automates integration | Robotiq
- https://vectorlinux.osuosl.org/pub/ros/ros_wiki_mirror/BioTac.html — BioTac
- https://www.syntouchllc.com/Technology/_publications/2009_Fishel_FingerprintsDOD.pdf — Microsoft Word - FingerprintsDoD.doc
- https://www.liebertpub.com/doi/abs/10.1089/soro.2022.0238 — Artificial Fingertip with Embedded Fiber-Shaped Sensing Arrays for High Resolution Tactile Sensing - Johannes Weichart, Pragash Sivananthaguru, Fergal B. Coulter, Thomas Burger, Christofer Hierold, 2024
- https://blog.robotiq.com/bid/71778/interview-with-matthew-borzage-of-syntouch-on-robotic-tactile-sensors — Interview with Matthew Borzage of SynTouch on Robotic Tactile Sensors
- https://www.yumpu.com/en/document/view/12177900/pdf-235mb-fred-s-grodins-research-symposium-university-of-/153 — The extracellular stimula
- https://hal.science/hal-05398856v1 — Cutaneous Feedback of Fingertip Deformation and Vibration for Palpation in Robotic Surgery  - Archive ouverte HAL
- https://bpb-us-w1.wpmucdn.com/sites.usc.edu/dist/a/37/files/2021/10/Sensing-Tactile-Microvibration.pdf — Sensing tactile microvibrations with the BioTac &#x2014; Comparison with human sensitivity
- https://www.doovi.com/video/cutaneous-feedback-of-fingertip-deformation-and-vibration-for/qV42dGlHJ0s — Cutaneous Feedback of Fingertip Deformation and Vibrati...
- http://arxiv.org/pdf/2402.11879 — Incipient Slip Detection by Vibration Injection into Soft Sensor
- https://patents.google.com/patent/CN111917405A/en — CN111917405A - Force sensitive capacitance sensor
- https://thinkstruct.com/patent/US20070038152A1 — US20070038152A1 - TACTILE BREAST IMAGER AND... | Thinkstruct
- https://patents.google.com/patent/CN212235947U/en — CN212235947U - 
        A capacitive haptic handle
- https://patents.google.com/patent/CN222050871U/en — CN222050871U - 
        Touch sensor
- https://www.notateslaapp.com/news/4790/tesla-patent-reveals-flexible-sensors-that-let-optimus-feel-objects — Tesla Patent Reveals Flexible Sensors That Let Optimus Feel Objects
- https://patents.justia.com/patent/10234996 — U.S. Patent for Capacitive based digitizer sensor Patent (Patent #  10,234,996 issued March 19, 2019) - Justia Patents Search
- https://www.patentsencyclopedia.com/app/20150370373 — CAPACITIVE BASED DIGITIZER SENSOR - Patent application
- https://trea.com/information/tactile-sensor-and-method-for-manufacturing-the-same/patentapplication/b303929d-1d6b-46a5-9382-6c0823ecea62 — TACTILE SENSOR AND METHOD FOR MANUFACTURING THE SAME | TREA
- https://patentcut.com/10234996 — Capacitive based digitizer sensor
- https://patents.google.com/patent/US20090260897A1/en — US20090260897A1 - Capacitive touch sensor