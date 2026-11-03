---
name: footbridge-crowd-vibration-check
description: Use when checking any footbridge vertical serviceability under synchronized crowd resonance.
source: seeded from knowledge/insights (5 problems) (2026-11-02)
---

## 1. Screen frequency and comfort target
1. Check first vertical mode against walking band **~1.5-2.2 Hz**; if inside, full Setra/HiVoSS check required with dense crowd governing [run 20261102-121628_vibration-retrofit-for-a-lively-pedestri E38].
2. Apply vertical bands: **<0.5 m/s2 maximum comfort, <1.0 m/s2 minimum/mean, >2.5 m/s2 unacceptable** [run 20261102-121628_vibration-retrofit-for-a-lively-pedestri E38].

## 2. Build resonant crowd force
3. Model vertical walking as **~700 N body weight with ~280 N (~40%) first harmonic at step resonance** [run 20261102-121628_vibration-retrofit-for-a-lively-pedestri E44,E50].
4. For sparse walkers add linearly; for **dense Class III ~0.5 pedestrians/m2 use imperfect sync Neq ~10.8*sqrt(zeta*N)** acting in phase at resonance [run 20261102-121628_vibration-retrofit-for-a-lively-pedestri E41,E42].
5. Reference scale: **Neq~5.29 -> harmonic force ~1.48e3 N**, producing kN-scale excitation and multi-m/s2 bare-deck response at **damping ~0.5-1%** (example bare 1.75 m/s2 single-case scaling to 9.26 m/s2 dense) [run 20261102-121628_vibration-retrofit-for-a-lively-pedestri E49,E50,E47,E51].

## Use notes
