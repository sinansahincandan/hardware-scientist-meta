# Rationale — Solar-only 1-tonne staged cold store with flat-pack chamber

Provide solar-only day-and-night power for 1 tonne produce cold storage, maintain chill with insulation, refrigeration and air circulation, in a weatherproof transportable cooperatively assemblable chamber with 1-tonne crate layout.

## Key estimates
- array power for 8 kWh per day at 5 peak sun hours: 2.13 kW (calc; evidence ['E16'])
- staged daily electrical need: 8.0 kWh/day (calc; evidence ['E16', 'E31', 'E56'])
- wall transmission leak: 185.0 W (simulate; evidence ['E31'])
- steady cooling load: 315.0 W (simulate; evidence ['E31'])
- steady electrical power at COP 2: 157.0 W (simulate; evidence ['E31'])
- steady daily electricity: 3.78 kWh/day (simulate; evidence ['E31'])
- product pull-down thermal energy 1 tonne 25K: 25.0 kWh (calc; evidence ['E56'])
- average pull-down cooling power over 24h: 1040.0 W (calc; evidence ['E57'])
- peak electrical power pulldown plus leak at COP 2 plus fan: 662.0 W (calc; evidence ['E60', 'E57', 'E31'])
- peak battery current at 48V for 662W: 13.8 A (calc; evidence ['E61'])
- battery usable store 48V 100Ah: 5.12 kWh (datasheet; evidence ['E10'])
- chamber inner volume: 10.6 m3 (simulate; evidence ['E44'])
- produce volume fill fraction: 27.1 % (simulate; evidence ['E44'])
- floor uniform pressure from 1 tonne: 2.04 kPa (calc; evidence ['E43', 'E44'])
- wall U from 100mm polyurethane: 0.22 W/m2K (simulate; evidence ['E31'])

## Risks
- One-shot 1-tonne pull-down of 25 kWh exceeds solar day and battery — mitigation: Stage loading over 3 days at ~333 kg per day with outside sort
- Running 662 W peak all night empties battery — mitigation: Run steady 157 W hold with duty cycling; night need ~1.88-4 kWh within 5.12 kWh store
- Warm air infiltration and spoilage spread from damaged produce — mitigation: 800 mm door with double gaskets, 3 mm squeeze, brief openings for 1-2 crates and FIFO rotation

## Novelty
Flat-pack cam-lock insulated chamber on steel skid with roof array rails combining 1.0 kW variable-speed DC cooling, 50x20 kg vented crates on side racks with aisle, and 3-day staged loading with outside sort and FIFO to fit 2.2 kW solar and 5.12 kWh store

## Sources
- https://pmarketresearch.com/auto/solar-powered-cold-room-market/
- https://www.saurenergy.com/solar-energy-news/when-the-rain-falls-short-the-cold-chain-has-to-step-up-12047710
- https://srj0408.substack.com/p/p3-post-harvest-technologies-for
- http://prsync.com/grand-view-reesearch/solar-powered-cold-storage-market-investment-opportunities-in-emerging-regions-4863033/
- https://coldchainsa.com/powering-the-cold-chain-renewable-energy-solutions-for-south-african-cold-storage-operations/
- https://germanclinic.co.za/MSK/solar/Solar-powered-cold-rooms-Tokelau_Thu-18-May-2023-41785.pdf
- https://containerserviceforu1.co.za/sites/default/files/Solar-powered-cold-rooms-in-Pitcairn-Islands_Tue-28-Oct-2025-45608.pdf
- https://makingprosperity.com/solutions-details/coldhubs
- https://www.GrandViewResearch.com/industry-analysis/solar-powered-cold-storage-market-report
- https://understandsolar.com/a-communal-solar-fridge-for-nigerian-farmers-markets/
- https://vc.easychair.org/publications/preprint/hsMw/open
- https://www.slideserve.com/teamijtsrd1123/design-and-fabrication-of-solar-powered-mobile-cold-room-powerpoint-ppt-presentation
- https://www.researchgate.net/publication/352887974_Experimental_study_of_cold_storage_packed_domestic_refrigerator_with_solar_powered_variable_speed_compressor
- https://www.scribd.com/document/682597654/8-Development-and-Performance-Evaluation-of-a-Solar-Energy-based-Portable-Micro-Cold-Storage-1
- https://www.scribd.com/document/435774142/Design-and-Fabrication-of-Solar-Powered-Mobile-Cold-Room
- http://repository.pnb.ac.id/5202/5/8.Simmirarity_Analysis%20Performance%20of%20Full%20Direct.pdf
- https://1library.net/document/yd2g0nlq-power-refrigeration-trinath-kumar-mahesh-ramana-sambasiva-theresa.html
- https://uatweb.usaid.gov/sites/default/files/2022-05/Powering-Health_Cold-Chain-Refrigeration.pdf
- https://www.sciencedirect.com/science/article/abs/pii/S0038092X1930787X
- https://patents.google.com/patent/US20140157794A1/en
- https://patents.google.com/patent/EP3885677A1/en
- https://www.patentsencyclopedia.com/app/20180106509
- https://patents.google.com/patent/CN211380001U/en
- https://patents.glgoo.top/patent/US7543455
- https://patents.justia.com/patent/20150285541
- https://patents.google.com/patent/US20170336134A1/en
- https://patents.google.com/patent/US4367633A/en
- https://patents.justia.com/patent/10823478
- https://theindexproject.org/award/nominees/4322
- https://foodplanetprize.org/initiatives/coldhubs-coldhubs-is-fixing-food-loss-with-off-grid-cool-rooms/
- https://solve.mit.edu/solutions/31462
- https://agrinnovators.org/wp-content/uploads/2023/10/COLEACP-PAFO_FICHE-ENTREPRISE-ColdHubs-EN.pdf
- https://www.Nairaland.Com/5139810/how-nigerias-coldhubs-solar-refrigerating-farms
- https://agrinnovators.org/business-profile/coldhubs/
- https://www.freshplaza.com/north-america/article/9034925/nigerian-start-up-solar-refrigerating-farms-coldhubs/
- https://africaprize.raeng.org.uk/2018-cohort/nnaemeka-chidiebere-ikegwuonu
- https://disruptafrica.com/2018/10/22/how-nigerias-coldhubs-is-solar-refrigerating-farms-to-profitability/
- https://businessday.ng/uncategorized/article/nnaemeka-ikegwuonu-lessons-in-penetrating-a-new-market/?amp

## Master prompt revision history

## S1/S2 history
- attempt 0 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

Fabrication steps not shown because they failed their light check: [2, 3, 4, 5]

## Figure notes
- fabrication step 2 could not be made or checked (BadRequestError: Error code: 400 - The response was filtered due to the prompt triggering our content management policy.); not shown
- fabrication step 3 could not be made or checked (BadRequestError: Error code: 400 - The response was filtered due to the prompt triggering our content management policy.); not shown
- fabrication step 4 could not be made or checked (BadRequestError: Error code: 400 - The response was filtered due to the prompt triggering our content management policy.); not shown
- fabrication step 5 could not be made or checked (BadRequestError: Error code: 400 - The response was filtered due to the prompt triggering our content management policy.); not shown
- labels removed because they pointed at the wrong part: PU box 2.4x2x2.2m

## Fabrication steps re-checked (plain-word check)
- fabrication step 1 re-checked: shown — Pixels show raised galvanized skid on bench with plywood spreader boards, vertical corner posts bolted to skid and to upper roof rails, screw-type ground anchors at corners, and light-gray sandwich insulated box mounted on top.
- fabrication step 2 re-checked: shown — Pixels show sandwich insulated box on stand with hinged insulated door, black perimeter gasket seal, hinges/latch, and metal rain canopy above door - matching fabrication step 2 parts.
- fabrication step 3: both checks blocked by the content filter; not shown
- fabrication step 4 re-checked: not shown — Array is mounted indoors on wall above controller, not ground-mounted beside room; no ground mount or roof rails/anchors visible. Skid, controller, battery and panels present but step 4 configuration not shown.
- fabrication step 5: both checks blocked by the content filter; not shown
