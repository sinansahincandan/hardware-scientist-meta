# Rationale — Concealed twin under-deck TMD retrofit for 40 m footbridge

40 m footbridge with lively 1.9 Hz first vertical bending mode needs concealed under-deck retrofit with zero deck sightline change to add damping and reduce crowd acceleration.

## Key estimates
- modal mass: 10000.0 kg (calc; evidence ['E2'])
- TMD total mass: 500.0 kg (vetted_calc:tuned_mass_damper_den_hartog; evidence ['E3'])
- TMD tuned frequency: 1.8095238095238093 Hz (vetted_calc:tuned_mass_damper_den_hartog; evidence ['E3'])
- TMD damper damping ratio: 0.1336306209562122 - (vetted_calc:tuned_mass_damper_den_hartog; evidence ['E3'])
- TMD stiffness: 64633.59979670308 N/m (vetted_calc:tuned_mass_damper_den_hartog; evidence ['E3'])
- controlled peak acceleration early estimate: 0.97 m/s2 (simulate; evidence ['E5'])
- crowd resonant force: 1400.0 N (simulate; evidence ['E6'])
- uncontrolled peak acceleration: 17.5 m/s2 (simulate; evidence ['E6'])
- controlled peak acceleration: 0.74 m/s2 (simulate; evidence ['E6'])
- effective damping ratio: 9.44 % (simulate; evidence ['E6'])
- damper relative travel: 20.0 mm (simulate; evidence ['E6'])
- 250kg unit weight: 2452.5 N (calc; evidence ['E10'])
- spring static sag: 0.07588932072482424 m (calc; evidence ['E11'])
- clamp-beam bending moment: 1103.625 N*m (calc; evidence ['E12'])
- clamp-beam bending stress: 16541776.782802219 Pa (calc; evidence ['E14'])
- U-bolt slip factor: 14.678899082568808 - (calc; evidence ['E15'])

## Risks
- Host cross-girder capacity for 2x250kg plus dynamic TMD force not checked; only new clamp beam checked — mitigation: Compute existing cross-girder bending and shear including dynamic TMD force per Eurocode
- U-bolt preload/slip margin not fully linked — mitigation: Link 30 kN preload per U-bolt with serrated plates to 36 kN friction vs 2452.5 N weight for 14.68 slip margin
- Comfort target drift from CL1 <0.5 m/s2 to CL2 0.74 m/s2 — mitigation: Explicitly accept CL2 <1.0 m/s2 at 0.74 m/s2 as comfortable retrofit outcome per Setra/Hivoss

## Novelty
Concealed twin 250-kg under-deck TMD on U-bolted clamp beams with zero hardware above deck and soffit-hatch maintenance

## Sources
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/
- https://www.gerb.com/tuned-mass-dampers-tmd
- https://www.gerb.com/tuned-mass-dampers-tmd
- https://www.gerb.com/tuned-mass-dampers-tmd
- https://www.gerb.com/tuned-mass-dampers-tmd
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://deicon.com/wp-content/uploads/2022/04/Pedestrian-Bridge-vibration-control-using-tuned-mass-dampers.pdf
- https://www.vibratec.org/product/tuned-mass-damper-low-frequency/

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=False S2 flaw=False decision=s1_retry
- attempt 0 round 1: S1 faithful=True S2 flaw=False decision=s1_pass

Panels failing light check (hollow marker in caption): steps [4]
