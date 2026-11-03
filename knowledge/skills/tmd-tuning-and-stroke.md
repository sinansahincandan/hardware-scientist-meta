---
name: tmd-tuning-and-stroke
description: Use when adding a vertical TMD to a low-frequency flexible structure.
source: seeded from knowledge/insights (5 problems) (2026-11-02)
---

## 1. Tune and damp per Den Hartog
1. Select **mass ratio mu=mTMD/Mmodal ~1-3% (example 500 kg on 20 t = 2.5%)** for first vertical mode [run 20261102-121628_vibration-retrofit-for-a-lively-pedestri E12,E13,E22].
2. Tune **fTMD/fstruct=1/(1+mu), i.e. 2-3% below structure (example 1.85 Hz for 1.9 Hz)** and damp **zeta~sqrt(3*mu/(8*(1+mu)^3)) ~0.09-0.10 at mu=0.025 (example 0.0933)** [run 20261102-121628_vibration-retrofit-for-a-lively-pedestri E12,E13,E23,E54].
3. Verify reduction: near-optimum tuning/damping drops resonant deck acceleration **>10x (example a_bare=1.75 -> a_tmd=0.103 ratio 17; dense 9.26 -> 0.545)** [run 20261102-121628_vibration-retrofit-for-a-lively-pedestri E47,E51,E52].

## 2. Size spring for sag plus stroke
4. Compute stiffnesses `k=(2*pi*f)^2*M`: **modal k~2.85 MN/m for 20 t at 1.9 Hz; TMD k~6.78e4 N/m (68 kN/m) with c~1.08-1.09e3 N-s/m for 500 kg at ~1.85 Hz** [run 20261102-121628_vibration-retrofit-for-a-lively-pedestri E11,E24,E47].
5. Allow for large static sag plus dynamics: **sag m*g/kTMD ~0.0723 m (72 mm) + resonant relative stroke ~20.1 mm = total ~0.0924 m**, so provide **~90+ mm working compression plus over-travel stops** [run 20261102-121628_vibration-retrofit-for-a-lively-pedestri E55,E53,E56].

## Use notes
