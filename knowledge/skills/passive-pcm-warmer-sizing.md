---
name: passive-pcm-warmer-sizing
description: Use when sizing a paraffin PCM plateau store at 36-38C to hold a low-wattage load in a 36.5-37.5C band for hours without electricity.
source: run 20261103-223203_infant-warmer-for-clinics-without-reliab (2026-11-03)
---

1. Estimate steady loss/load P_need: infant + enclosure ~4-5 W at 20-25C ambient E21,E51.
2. Compute energy need: E_need = P_need * t_hold. For 5 W * 4 h = 20 Wh E21,E32,E54.
3. Select PCM at target melt T ~37C: PureTemp 37 latent ~180-210 J/g E7-E10,E33,E45,E46. Check quantity: 1 kg at 200 kJ/kg = 55.6 Wh E33.
4. Compute gross stored E_store = m * h_latent. 1.2 kg * 210 J/g = 252 kJ = 70 Wh E52,E53,E45,E46.
5. Apply utilization factor eta to infant (rest to ambient): usable E = eta*E_store. Example eta~0.5 gives 33.4 Wh from 1.2 kg E34, still >20 Wh need -> 6.0 h depletion proves >4 h hold E51.
6. Verify by lumped PCM model trace: plateau time in 36.5-37.5C > t_hold and depletion time > t_hold E51.
7. Check recharge outside device at ~60C water does not exceed contact limit in step 4 of companion skill (39.7C <40C when hot-charged E51). Check 20 Wh is 0.2% of household energy E51 for feasibility.

Checks: E_store/ E_need >= 2-3x for eta and drafts; plateau T 36.8C within WHO band E51; closed/open R_amb to extend hold E51.
Typical values: latent 180-210 J/g E33,E45,E46; m 1.0-1.2 kg -> 55-70 Wh E33,E52,E53; P 4-5 W -> 20 Wh/4h E21; depletion 6 h E51.

## Use notes
