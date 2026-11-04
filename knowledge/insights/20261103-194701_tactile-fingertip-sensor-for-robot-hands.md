# Insights from Tactile fingertip sensor for robot hands
Source run: 20261103-194701_tactile-fingertip-sensor-for-robot-hands

## Femtofarad budget for millinewton capacitive touch
Millinewton touch on soft elastomer produces ~0.01 strain and ~2.5 um gap change, yielding ~6-7 fF capacitance change from a sub-pF to pF baseline. Capacitance-to-digital converters resolve ~1 fF, giving SNR ~6 at 1 mN threshold.
Evidence: E9 (capacitive taxel 1mN signal budget: strain 0.0125 dd 2.5 um dC 6.72 fF; literature 6fF gives SNR vs 1fF CDC = 6; taxels across 20mm at 2.5mm pitch = 8.0); E5 (search: capacitance to digital converter resolution femtofarad AD7147: analog.com — AD7147A (Rev. B) — https://www.analog.com/media/en/technical-documentation/data-sheets/ad7147a.pdf); E8 (baseline taxel capacitance pF to fF: 531 m)

## Elastomer spread enables sub-pitch localization
A 1-1.5 mm soft skin under ~250 Pa spreads point load to ~3.9 mm radius, covering multiple taxels at 2.5 mm pitch. Weighted-centroid interpolation then achieves ~0.05-0.075 mm acuity, about 1/30 of pitch, a tactile hyperacuity regime.
Evidence: E18 (skin spread vs taxel pitch check: pressure 250 Pa strain 0.0036 compression 5.43 um spread radius 3.87 mm vs pitch 2.5mm); E39 (stick ratio and centroid localization check: expected acuity ~ 0.075 mm; dynamic range = 15000:1 = 13.9 bits needed; SR stable=1, SR incipient=0.375 -> warn=True); E30 (search: tactile sensor spatial resolution centroid interpolation taxel pitch: 1library.net — Tactile Superresolution and Biomimetic Hyperacuity — https://1library.net/document/dzx8xkvq-tactile-superresolution-and-biomimetic-hyperacuity.html)

## Incipient slip signatures and timing budget
Coulomb limit is shear <= mu x normal, e.g. ~0.45 N allowable shear at 1 N normal. Distributed contact shows stick-ratio 1.0 stable falling to ~0.375 at incipient slip. Ridges emit 200-300 Hz, centered ~250 Hz, slip vibration. A 2 mm object drop takes ~20.2 ms, setting flag latency budget. Keep support structure resonance near 11.5 kHz well above the slip band.
Evidence: E38 (Coulomb slip threshold at 1 N grip: 0.45); E39 (stick ratio and centroid localization check: expected acuity ~ 0.075 mm; dynamic range = 15000:1 = 13.9 bits needed; SR stable=1, SR incipient=0.375 -> warn=True); E12 (search: fingerprint ridges amplify tactile slip vibration artificial fingertip: Www.Discovermagazine.com — Fingerprints Are Tuned to Amplify Vibrations and Send Info to the Brain — https://Www.Discovermagazine.com/technology/fingerprints-are-tuned-to-amplify-vibrations-and-send-info-to-the-brain); E46 (drop time for 2 mm fall in ms: 20.2); E44 (core axial resonance estimate vs 300 Hz slip band: 1.15e+04)

## Fourteen-bit tactile range needs bilinear gap
1 mN to 15 N touch is 15000:1 dynamic range requiring ~13.9 bits. A single soft linear gap saturates; a microstructured soft gap for low force in series with a stiff stop gap for high force yields bilinear compression, e.g. ~177 fF at mid-load versus ~531 fF at 15 N full scale.
Evidence: E47 (dynamic range 15N vs 1mN: 1.5e+04); E48 (dual-range bilinear compression vs force: 0.5 177 fF; 15 531 fF; dynamic range 15000 bits 13.9)
