I'll search for the closest existing small-turbine designs to compare against your concept.
Early results point to Collegiate Wind Competition turbines as the closest match. I'll open the most relevant reports to pin down the differences.
I've identified a strong candidate match. Now I'll verify its braking details to finalize the comparison.
Closest existing system:

**UMass Amherst MinuteWind 2017 DOE Collegiate Wind Competition turbine — Technical Design Report.**

Why it is closest:

* Same competition task / scale: a `3-bladed, upwind, horizontal axis wind turbine` `with a 45-cm rotor diameter, passive yaw system, and actively controlled electrical system with a permanent magnet generator`.
* Same construction practice: `3D printed blades attached to a 3D printed hub to form the rotor`, using `low Reynolds numbers airfoils` and optimized chord/twist from `Blade-Element Momentum (BEM)` code.
* Same electrical idea: permanent-magnet machine + rectifier / inductor / MOSFET circuit + Schottky diode, capacitor, shunt and divider for load power:
  * `335 μH, 6A inductor` paired with main MOSFET to vary effective resistance
  * `A Schottky diode was incorporated` to block reverse current
  * `3.3 milliFarad capacitor` to smooth ripple
* Same shutdown requirement addressed: `load disconnect, or low brake signal, caused the system to run a braking algorithm`, detected as `recording wind speed and had exposed the load but detected no output current`.
* Same <10% speed target demonstrated in <10 s: `RPMs are brought to under 10% of rated in under ten seconds`, initiated at `t=2` then `flattens out at 10% after six seconds` by short-circuit action.

Critical difference — fail-safe combined mechanical + dump stop vs software-only regenerative short:

UMass brakes **only electrically, powered, and stays spinning**:

> `Both the primary and load MOSFET were utilized to brake the turbine. While braking, the primary MOSFET was made to behave like a closed circuit, effectively shorting the leads of the generator through the inductor and primary MOSFET.`

> `When used to brake the turbine, the MOSFET was sent into saturation and the generator was shorted across the inductor and MOSFET. This caused a dramatic increase in current, resulting in a reverse torque`

> `When braking, the controller brought the load MOSFET into cut-off (disconnecting the load) and then brought the inductor MOSFET toward saturation.`

> `This action increased the motor torque and quickly slowed the rotor.`

> `Once the rotor had reached 10% of rated speed, the feedback loop adjusted the inductor gate value to maintain braking speed.`

That is:

1. **No spring-applied disc, no separate dump-resistor grid, no normally-closed safety-chain latching relay.** UMass needs live Arduino + `5V` boost / regulator to hold braking, including `maintain power at input voltages as low as 3V` and `maintaining braking speed and minimum voltage until the brake signal was restored`.
2. **Does not park at 0 rpm.** It controls to and holds ~10% rated, vs concept `0.80 N-m spring-applied solenoid-released disc plus 4 ohm dump` that crosses 315 rpm in 0.673 s and holds `0 rpm at 10 s`.
3. **Different rotor / generator sizing.** UMass tests `design lambda values of 6 and 7` with `design lambda of 7 is superior` using `S834` airfoils, and a `12-V, permanent magnet DC motor was chosen for a generator` with `microprocessor can also force regenerative braking`.

Concept instead fixes:

* `40 cm SD7080 fixed-pitch` soft-stall rotor, `Cp 0.34 at TSR 6` borrowed from large-turbine literature: `rotor radius of 1.8 m and a Tip Speed Ratio (λ) of 6` with `SD7080 airfoil blade has an optimum power coefficient of Cp = 0.34, at λ = 6 for Reynolds number (Re) = 81712`, scaled to 40 cm / 45 cm cube.
* `170-180 Kv direct-drive outrunner through Schottky bridge to 8-40V to 12V buck-boost + switched 4 ohm dump`, to cure low-wind dropout.
* Latching `normally-closed e-stop + load-volt tap + centrifugal overspeed switch` driving **simultaneous** spring disc friction torque usable at zero speed **plus** dump electrodynamic torque — directly addressing the known split in prior art:

> `small wind turbines can be reduced with electrical brakes that dump energy from the generator into a resistor bank, converting the kinetic energy of the blade rotation into heat. However, electrical brakes are generally not suitable for large wind turbines.`

> `they are typically only used after blade furling and electromagnetic controls have already slowed rotation to a safer speed.`

Patent `US 2018/0291873 Disc Brakes for Wind Turbines` separately discloses:

> `A brake for a wind turbine includes a disc coupled to and rotatable with the blade support hub` and `piston and caliper assembly cooperating with the disc to stop or slow rotation`.

But it uses `motorized linear actuator configured to pivot the lever` energized on `excessive wind speed` / `excessive motor speed`, not a spring-applied / solenoid-released fail-safe on loss-of-load combined with soft-stall + dump on the **low-speed shaft** at model scale with latched manual reset and parked hold.

In short: **MinuteWind 2017 = closest integrated prior art; concept = replace Arduino PWM short-circuit hold-at-10% with SD7080 soft-stall + corrected-Kv buck-boost feed + NC-chain latched 0.80 N-m spring disc + 4-ohm dump for unpowered <1 s trip to 0-rpm park.**


Sources:
- https://www.energy.gov/sites/default/files/2017/04/f34/UMA_REPORT_2017-04-05.pdf — Univerity of Massachusetts Amherst Collegiate Wind Competition 2017 Techincal Report
- https://www.patentsencyclopedia.com/app/20180291873 — Disc Brakes for Wind Turbines - Patent application
- https://www.energy.gov/eere/collegiatewindcompetition/articles/seattle-university-business-plan-and-technical-report-2018 — Business Plan and Technical Report
- https://stage.energy.gov/documents/psutechnicaldesignreportpdf — Pennsylvania State University: Technical Design Report
- https://en.wind-turbine.com/wind-turbines/69388/kleinwindkraftanlage-zefir-d14-p10-t23.html?langswitch=en — Small wind turbine ZEFIR D14-P10-T23
- https://pdfdrive.to/dl/technical-design-report — Download Technical Design Report PDF
- https://en.wind-turbine.com/wind-turbines/69392/kleinwindkraftanlage-zefir-d21-p60-t36-60kw.html — Small wind turbine ZEFIR-D21-P60-T36 (60kW)
- https://www.uvu.edu/cet/mce/student-work/docs/mechanical/2025/windturbine_518968_127134368_wind_turbine_poster_spring_2025.pdf — PowerPoint Presentation
- https://docslib.org/doc/7411478/arctic-winds-university-of-alaska-fairbanks — Arctic Winds University of Alaska Fairbanks
- https://en.wind-turbine.com/wind-turbines/75248/kleinwindkraftanlage-zefir-d21-p100-t36-mit-100kw-leistung.html?langswitch=en — Small wind turbine Zefir D21-P100-T36 with 100kW power
- https://www.energy.gov/sites/default/files/2016/02/f29/CWC%20Rules%20and%20Regulations%20Manual_Rev3_160203.pdf — U.S. Department of Energy Collegiate Wind Competition 2016 Rules and Regulations. 
- https://www.energy.gov/sites/default/files/2022-07/PSU_TurbineDesignReport_2022-04-24Optimized.pdf — 2022 Collegiate Wind Competition - Penn State University - Technical Design Report
- http://repo.lib.jfn.ac.lk/xmlui/handle/123456789/2319 — Design of Small Horizontal Axis Wind Turbine for Low Wind Speed Rural Applications
- http://repo.lib.jfn.ac.lk:8080/ujrr/bitstream/123456789/2319/2/Design%20of%20Small%20Horizontal%20Axis%20Wind%20Turbine%20for%20Low%20Wind%20Speed.pdf — Design of Small Horizontal Axis Wind Turbine for Low Wind Speed Rural Applications
- https://scite.ai/reports/design-of-small-horizontal-axis-D1zR8md — Design of small horizontal axis wind turbine for low wind speed rural applications
- https://1library.net/document/4zplvmvq-design-fabrication-small-horizontal-turbine-rotors-reynolds-number.html — Design and Fabrication of Small Horizontal axis wind Turbine Rotors at Low Reynolds Number
- https://doaj.org/article/005f3a9f52814153a9ccc66173ccc886 — Design Optimization and Performance Investigation of a Micro Wind Turbine for Domestic Dwelling Used for Renewable Generation System – DOAJ
- https://ai.updf.cn/paper-detail/design-optimization-and-performance-investigation-of-a-micro-wind-turbine-abbas-abbasalizadeh-17bea61a73fabe322f07fb6677e1194f8ecb2a04 — Design Optimization and Performance Investigation of a Micro Wind Turbine for Domestic Dwelling Used for Renewable Generation System
- https://www.researchgate.net/publication/334308927_Design_of_small_horizontal_axis_wind_turbine_for_low_wind_speed_rural_applications — Design of small horizontal axis wind turbine for low wind speed rural applications
- https://pdfs.semanticscholar.org/f449/f115c0aca6eee3f65eaaac75ea7f1bedfed2.pdf — Journal of Engg. Research Online First Article Experimental investigations of winglet effects on blade geometry of small horizontal axis wind turbine rotors
- https://www.ablesci.com:443/scholar/paper?id=8BA17y6aE — Design Optimization and Performance Investigation of a Micro Wind Turbine for Domestic Dwelling Used for Renewable Generation System - 科研通
- https://patents.justia.com/patent/20190003457 — WIND TURBINE SYSTEM WITH TIME DISTRIBUTED TRANSITIONS
- https://trea.com/information/wind-turbine-system-with-time-distributed-transitions/patentapplication/2fc672d9-7dee-4c11-9b43-d52932655f1a — WIND TURBINE SYSTEM WITH TIME DISTRIBUTED TRANSITIONS
- https://patents.Google.Com/patent/EP3394428A1/en — EP3394428A1 - Wind turbine system with time distributed transitions 
        - Google Patents
- https://www.patentsencyclopedia.com/app/20190003457 — WIND TURBINE SYSTEM WITH TIME DISTRIBUTED TRANSITIONS - Patent application
- https://patents.justia.com/patent/8502403 — U.S. Patent for Multiple generator wind turbine and method of operation thereof Patent (Patent #  8,502,403 issued August 6, 2013) - Justia Patents Search
- https://eureka-patsnap-com.libproxy1.nus.edu.sg/patent-US20070279815A1 — Redundant electrical brake and protection system for electric generators
- https://data.epo.org/publication-server/rest/v1.2/publication-dates/20160518/patents/EP1863162NWB1/document.pdf — REDUNDANT ELECTRICAL BRAKE AND PROTECTION SYSTEM FOR ELECTRIC GENERATORS - European Patent Office - EP 1863162 B1
- https://data.epo.org/publication-server/rest/v1.2/publication-dates/20200909/patents/EP2536944NWB1/document.pdf — TEST SYSTEM FOR WIND TURBINE DUMP LOAD - European Patent Office - EP 2536944 B1
- https://scienceon.kisti.re.kr/srch/selectPORSrchPatent.do?cn=USP2009097586216&dbt=USPA — [특허]Redundant electrical brake and protection system for electric generators