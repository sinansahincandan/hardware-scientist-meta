# Insights from Tactile fingertip sensor for robot hands
Source run: 20261102-214941_tactile-fingertip-sensor-for-robot-hands

## Millinewton Hertz contact on soft silicone
A 1 mN normal touch on Shore 10A silicone produces a Hertz contact radius of ~0.25 mm with pressure on the order of 1 mN per mm2. This sets the contact-spreading scale and sensitivity floor for detecting millinewton touch through compliant skin.
Evidence: E9 (Hertz contact radius mm for 1mN on Shore 10A silicone: 0.247)

## Femtofarad scale of millimeter capacitive taxels
A ~2 mm pitch soft capacitive taxel has base capacitance around 200 fF, requiring capacitance-to-digital readout with femtofarad resolution such as AD7147-class. This defines the electrical dynamic range for millimeter-resolution flexible tactile arrays.
Evidence: E18 (base capacitance fF for 2mm taxel: 212); E11 (search: capacitive tactile fingertip sensor array pitch resolution mN: research-collection.ethz.ch — Artificial Fingertip with Embedded Fiber-Shaped Sensing Arrays for — 2024 — https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/671097/weichart-et-al-2024-artificial-fingertip-with-embedded-fiber-shaped-sensing-arrays-for-high-resolution-tactile-sensing.pdf?sequence=6&isAllowed=y); E12 (search: capacitance to digital converter resolution femtofarad AD7147 datasheet: analog.com — AD7147A (Rev. B) — https://www.analog.com/media/en/technical-documentation/data-sheets/ad7147a.pdf)

## Slip vibration band and fall latency budget
Slip-induced micro-vibration occupies roughly 100-500 Hz in the Pacinian FA-II band and requires sampling around 1 kHz. Free-fall kinematics allows only ~14.3 ms to limit drop to 1 mm, with ~0.49 mm fall in 10 ms, so sense-to-flag latency must be on the 10 ms order.
Evidence: E21 (search: human fingertip slip detection vibration frequency Pacinian FA-II bandwidth: pmc.ncbi.nlm.nih.gov — Neurophysiology of slip sensation and grip reaction: insights for hand prosthesis control of slippage - PMC — https://pmc.ncbi.nlm.nih.gov/articles/PMC7613203/); E23 (search: tactile sensor sampling rate slip detection 1 kHz robot grip control latency: ia801601.us.archive.org — Micro-Vibration-Based Slip Detection in Tactile Force Sensors — https://ia801601.us.archive.org/11/items/pubmed-PMC3926583/PMC3926583-s140100709.pdf); E39 (max delay for 1mm fall in ms: 14.3); E41 (fall in mm for 10ms sense-to-flag: 0.491)

## Fingertip envelope and silicone tear limit
Human fingertip envelope is about 18 mm width by 28 mm length with volume around 7810 mm3, bounding any rigid core plus skin stack. Dragon Skin 10-class Shore 10A silicone has tear strength around 17.9 N per mm, which bounds peel and tear margin for thin membranes bonded to rigid substrates.
Evidence: E1 (search: human fingertip dimensions size width length: mdpi-res.com — Free and Forced Vibration Modes of the Human Fingertip — https://mdpi-res.com/d_attachment/applsci/applsci-11-05709/article_deploy/applsci-11-05709-v3.pdf?version=1624348917); E34 (envelope volume estimate fingertip box: 7.81×10³ mm³); E8 (search: Dragon Skin silicone Smooth-On Shore hardness tear strength datasheet: smooth-on.com — Dragon Skin™ 10 SLOW vs. Dragon Skin™ 20 NV — https://www.smooth-on.com/compare/4670/40768/a/); E44 (tear strength N per mm from pli: 17.9)
