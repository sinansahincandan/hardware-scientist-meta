# Rationale — Solar cold store for 1 tonne at 4-10 C

Provide solar-only power with day-night autonomy to keep 1 tonne of produce at 4-10 C in a washable racked cold box on a low-cost plinth that a cooperative can use daily.

## Key estimates
- Steady cooling load: 376.0 W (simulate; evidence ['E24'])
- Conduction heat gain: 186.0 W (simulate; evidence ['E24'])
- Full-tonne pull-down thermal energy: 25.0 kWh (simulate; evidence ['E24'])
- Steady electric input: 150.0 W (calc; evidence ['E51'])
- Daily holding electric energy: 3.6 kWh (calc; evidence ['E52', 'E24'])
- Daily PV yield from 2.4 kWp: 8.1 kWh (calc; evidence ['E54'])
- Batch electric for 200 kg: 2.0 kWh (calc; evidence ['E55'])
- Night energy 14 h at 150 W: 2.1 kWh (calc; evidence ['E57'])
- Night fraction of battery: 0.41 ratio (calc; evidence ['E58'])
- Fraction of PV yield used: 0.691 ratio (calc; evidence ['E56'])
- Peak electric for 200 kg batch over 8 h plus steady: 0.4 kW (calc; evidence ['E60'])
- Peak DC current at 48 V: 8.33 A (calc; evidence ['E62'])
- Soil pressure under plinth: 2.51 kPa (calc; evidence ['E47'])
- Floor loading from produce: 2.45 kPa (calc; evidence ['E48'])
- Wind pressure at 30 m/s gust: 540.0 Pa (calc; evidence ['E64'])
- Wind force on side wall: 2860.0 N (calc; evidence ['E65'])
- Holding-only autonomy: 1.42 days (calc; evidence ['E66'])
- Thermal buffer 1 tonne for 2 K rise: 1.94 kWh (calc; evidence ['E67'])

## Risks
- Full-tonne pull-down energy exceeds daily PV yield and battery store — mitigation: Cap warm intake at 200 kg per day and pause intake when cloudy
- Cloudy stretch beyond 1.42-day autonomy lets box drift out of 4-10 C — mitigation: Hold only with sealed door and fan mixing using produce thermal buffer and battery reserve
- Wind gust loads panels and light box while soil must carry full weight — mitigation: Keep PV rack separate from cold box and anchor box to plinth

## Novelty
One buildable unit combining PU box plus DC chiller plus airflow plus PV-battery plus crates-racks plus plinth-frame-door for 1 tonne at 4-10 C with capped batch and no-batch cloudy rule.

## Sources
- (none)

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

## Figure notes
- callouts DC Chiller Unit, Insulated Cold Box, Vented Produce Crates, Concrete Support Plinth pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: 100mm PU cold box 2m
- the critical part (100mm PU cold box 2m) fills most of the picture; panel B would repeat panel A, omitted
