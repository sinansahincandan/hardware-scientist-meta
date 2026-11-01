# Whiteboard
## Functions
- F1 [Structural Dynamics Lead] Limit first vertical bending response near 1.9 Hz to comfortable acceleration
## Concepts
- C1 [Structural Dynamics Lead, open, for F1] Under-deck vertical Tuned Mass Damper (TMD) at midspan, hidden below deck, tuned to 1.9 Hz with ~2% modal mass ratio and added viscous damping
- C2 [Retrofit Integration Architect, open, for F1] Concealed under-deck support frame: bolted cross-frames between existing girders carrying two 200 kg TMD units below soffit, 30 mm stroke clearance, lockable access hatches from below, soffit-matched finish, no fixings through deck wearing surface
## Evidence
- E1 [calc, Structural Dynamics Lead] 1.75 (ok)
- E2 [vetted_calc:tuned_mass_damper_den_hartog, Structural Dynamics Lead] vetted_calc error: tuned_mass_damper_den_hartog() missing 2 required positional arguments: 'main_mass_kg' and 'main_frequency_hz' (error)
- E3 [sketch, Structural Dynamics Lead] 40m footbridge side view, first vertical bending mode shape max at midspan, under-deck TMD mass-spring-damper hidden below deck at midspan (ok)
- E4 [vetted_calc:tuned_mass_damper_den_hartog, Vibration Control Specialist] tmd_mass_kg=400.0 mixed (see keys), tmd_frequency_hz=1.8627450980392155 mixed (see keys), tmd_damping_ratio=0.08574929257125442 mixed (see keys), tmd_stiffness_n_m=54793.190139073544 mixed (see keys), (ok)
- E5 [calc, Vibration Control Specialist] 400.0 (ok)
- E6 [simulate, Vibration Control Specialist] deck_amp~1.4 mm TMD stroke~8.2 mm (ok)
- E7 [sketch, Retrofit Integration Architect] Under-deck concealed TMD mounting cross-section - no change to deck view, access from below (ok)
- E8 [simulate, Vibration Control Specialist] det +5% zeta_eff=0.064 (ok)
- E9 [calc, Vibration Control Specialist] 3924.0 (ok)
- E10 [calc, Retrofit Integration Architect] 3924.0 (ok)
- E11 [calc, Structural Dynamics Lead] 3924.0 (ok)
- E12 [calc, Structural Dynamics Lead] 2452500.0 (ok)
- E13 [simulate, Vibration Control Specialist] det +5%: deck 0.95 mm acc 0.136 m/s2 stroke 5.33 mm (ok)
- E14 [calc, Vibration Control Specialist] calc failed: NameError: name 'pi' is not defined (error)
## Objections
- O1 [Pedestrian Comfort and Construction Planner -> C2, blocking=False] Under-deck TMD support needs fatigue check for added mass and re-tuning access plan before comfort sign-off
- O2 [Manager -> C2, blocking=True] Process block: C2 support needs quantified connection static+dynamic forces and fatigue check for 400 kg added mass, and C1 needs off-tune (+/-5%) comfort/ stroke check before proposal/vote
- O3 [Manager -> C1, blocking=True] Process block: need -5% detune acceleration and stroke to complement +5% check before joint proposal
## Proposal
- (none)
## Votes
