# Insights from Small wind turbine for a wind-tunnel competition
Source run: 20261104-122320_small-wind-turbine-for-a-wind-tunnel-com

## Sub-meter rotor power regime Cp ~0.35 at TSR ~5
Shaft power follows P_shaft = Cp * 0.5 * rho * A * V^3 with Cp ~0.35 for low-Reynolds 3-blade sub-meter rotors at tip-speed ratio ~5. For ~0.126 m2 disk: available wind power ~56 W at 9 m/s yielding ~19.6 W shaft at ~2149 rpm, and ~102 W at 11 m/s yielding ~35.7-35.9 W shaft at ~2626 rpm.
Evidence: E8 (available wind power 40cm rotor at 11 m/s: 102); E9 (rotor power curve 5-11 m/s and thrust: V=9 Pwind=56.1 Pshaft=19.6 rpm=2149 T=0.087 Th=5.3; V=11 Pwind=102 Pshaft=35.9 rpm=2626 T=0.13 Th=7.92; survival V=22 Th=31.7); E25 (check shaft power at 11 m/s: 35.7 W)

## Wind thrust rule from dynamic pressure with Ct ~0.85
Aerodynamic thrust scales as Thrust = Ct * q * A with q = 0.5*rho*V^2 and Ct ~0.85. Reference numbers: q ~296 Pa at 22 m/s; thrust ~5.3 N at 9 m/s and ~7.9 N at 11 m/s rising to ~31.7 N at 22 m/s survival for ~0.126 m2 disk. Use q*A*Ct to size mounts, towers and nacelle booms for operating plus 2x wind-speed survival cases.
Evidence: E9 (rotor power curve 5-11 m/s and thrust: V=9 Pwind=56.1 Pshaft=19.6 rpm=2149 T=0.087 Th=5.3; V=11 Pwind=102 Pshaft=35.9 rpm=2626 T=0.13 Th=7.92; survival V=22 Th=31.7); E33 (dynamic pressure 22 m/s: 296)

## Electrical dump brake limit requires aero unload to park
Dump-resistor dynamic braking as a component class is torque-limited: a 1.5-2.0 ohm dump on a small brushless-outrunner generator yields braking torque ~0.116 N-m versus aero driving torque ~0.13 N-m at top speed, leaving the rotor spinning at ~77% of top speed (~211 rad/s). Parking below 10% requires adding large aerodynamic unloading to ~5% residual torque plus phase-short; that combination reaches ~9.9% at ~4.9 s and holds ~0.81% at 10 s.
Evidence: E26 (generator voltage match and dump-resistor stop time: R=1.5 P=31.8W Tb=0.116Nm vs aero 0.13Nm; k 0.000316; final w=211.0 rad/s = 76.7% top); E27 (combined dump brake plus feather stop: below 10% at t=4.9s w=27.3; t=4.9 w=27.3 = 9.9%); E40 (verify stop stays below 10 percent with 2 ohm dump plus feather: check 4.9s: 9.9% of top; 10s: 0.81% of top -> holds; KE order ~100J class)

## 100-J stop energy scale for sub-meter rotors at ~2600 rpm
Small rotors at 2600-2890 rpm store ~100 J-class kinetic energy (~113 J) with overspeed trip set ~110% of top speed (~2890 rpm). Dissipation budget for shutdown is therefore ~100 J over a few seconds (~24 W in dump resistor class), yielding stop in ~5 s with ~50% margin against a 10 s requirement when aero plus electrical braking are combined.
Evidence: E32 (Verify shutdown timing and gust survival margins from board evidence: trip 2889 rpm, KE 113 J, stop 4.9s < 10s margin 51%, SF 4.4); E39 (trip threshold 110 percent top speed: 2.89e+03); E40 (verify stop stays below 10 percent with 2 ohm dump plus feather: check 4.9s: 9.9% of top; 10s: 0.81% of top -> holds; KE order ~100J class)
