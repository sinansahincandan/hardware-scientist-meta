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
- https://ismcontainers.com/talus-renewables-and-ism-containers-transform-fertilizer-production-in-kenya/
- https://www.pv-magazine.com/2020/11/03/solar-powered-cooling-system-for-vegetable-storage/
- https://www.techwin.co.ke/coldstorages-equipment/coldrooms-storages/solar-cold-rooms
- https://www.pv-magazine.com/2021/06/08/solar-powered-cold-storage-service/
- https://www.techwin.co.ke/dairy-equipment/cold-storage-solutions/coid/solar-powered-cold-rooms
- https://www.researchgate.net/publication/395704662_Mitigating_Post-Harvest_Losses_in_Sub-Saharan_Africa_A_Hybrid_Solar-Powered_Cold_Storage_System_with_Passive_Evaporative_Cooling_and_Smart_Monitoring_for_Smallholder_Farmers
- https://indiacleanenergy.com/solar-cold-storage/
- https://insulatedsystemsltd.com/solar-cold-rooms/
- https://greenworldinvestor.com/all-you-wanted-to-know-about-solar-powered-cold-storage-mobile-units-in-india/
- https://solarsolutions4everyone.co.za/nb/surs/Solar-Cold-Storage:-Powering-Food-Security_Fri-10-Jun-2022-3406.pdf
- https://africaprize.raeng.org.uk/2018-cohort/nnaemeka-chidiebere-ikegwuonu
- https://techxlab.org/solutions/cold-rooms-by-coldhubs/
- https://understandsolar.com/a-communal-solar-fridge-for-nigerian-farmers-markets/
- https://www.renewableenergymagazine.com/jane-marsh/the-rise-of-the-energy-entrepreneur-how-20261019
- https://energypedia.info/index.php?title=ColdHubs_-_Solar_Cold_Rooms_in_Nigeria&oldid=304340
- https://energypedia.info/index.php?title=ColdHubs_-_Solar_Cold_Rooms_in_Nigeria&direction=prev&oldid=304357
- https://afritechconnect.com/article/africa-loses-one-third-of-its-fish-to-spoilage-these-3-innovations-are-fighting-back
- https://www.ccacoalition.org/content/coldhubs-ltd
- https://www.sidley.com/en/probonolanding/sidley-emerging-enterprises-pro-bono-program/projects/coldhubs-ltd
- https://ng.linkedin.com/company/coldhubslimited?trk=article-ssr-frontend-pulse_little-mention
- https://smartbuy.alibaba.com/buyingguides/ecozen-cold-storage
- https://www.iiec.org/coolingdemo-technologies/720-cold-storage-and-food-processing/677-ecofrost-portable-solar-powered-cold-rooms-ecozen-solutions
- https://www.ecozensolutions.com/agriculture/ecofrost-in-kenya.html
- https://www.pv-magazine-india.com/2021/06/07/solar-powered-cold-storage-as-a-service/
- https://5.imimg.com/data5/SELLER/Doc/2022/12/LV/EM/KI/18386671/solar-powered-cold-storage.pdf
- https://www.engineeringforchange.org/solutions/product/ecofrost-micro-cold-storage/
- https://efficiencyforaccess.org/?p=3286
- https://www.eco-business.com/id/news/how-apps-ai-and-solar-powered-cold-rooms-are-driving-sustainable-agriculture/
- https://www.indiamart.com/proddetail/ecofrost-solar-cold-room-20855381197.html

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

Fabrication steps not shown because they failed their light check: [2]

## Figure notes
- callouts DC Chiller Unit, Airflow Fan Kit, Concrete Plinth Base, Steel Support Frame pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: 100mm PU cold box, Fan airflow kit, Steel frame / PV rack
- the critical part (100mm PU cold box) fills most of the picture; panel B would repeat panel A, omitted
- fabrication step 2 not shown: failed its light check twice (Pixels show only insulated-panel box shell on steel frame with door cut-out under assembly; no solar, refrigeration unit, capacity label, or temperature evidence visible to confirm solar cold store for tonne at C.)
- fabrication step 3: the detailed check was blocked by the provider's content filter; it passed a general check only (caption marked)
- fabrication step 4: the detailed check was blocked by the provider's content filter; it passed a general check only (caption marked)
- fabrication step 4 passed after one redraw (first attempt: Pixels show a small insulated box sitting on a wooden workbench with hand-tools for scale, concrete plinth bolted to wood, produce crates and loose copper/electrics and unconnected PV leaning nearby. Scale and support are incompatible with a 1-tonne cold store build stage - it's a bench model/composite, not tonne-scale construction.)
