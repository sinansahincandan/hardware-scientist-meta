I'll search for the closest solar cold-storage products and papers to compare against your design.
That Kenyan prototype looks like a near match — I'll open the source pages to confirm the technical details.
Closest match: field-tested paper unit + deployed product family

### 1. Closest paper: 1.5-tonne Nakuru County, Kenya unit - Odhiambo et al. 2025

> Tested a `1.5 ton capacity solar-powered cold storage unit` in `three remote villages of Nakuru County between March 2022 and February 2023`.

Architecture is essentially same as v3 concept:

> `combined a 2 kW photovoltaic array, a 10 kWh lithium-iron-phosphate battery bank and a variable-speed vapour-compression chiller to hold chamber air at 4-6 °C with 85% relative humidity.`

Performance reported:

> `Shelf life extended by 2.9 to 3.9 times across commodities, with grapes reaching 13.8 days against 4.1 at ambient.`
> `The unit ran autonomously for 21 hours per day on average and coped with rainy-season cloud spells without cold-chain breakdown`

### 2. Closest commercial product: ColdHubs Nigeria 2-3 tonne solar walk-in

> `ColdHubs are 100% solar-powered walk-in cold rooms, installed in outdoor markets and farm clusters.`

> `Cold room: a 10 feet length, 10 feet width and 7 feet height, 120mm insulated cold room panel with floor made of stainless steel. This contains 3 tons of perishable food arranged in 150 units, 20kg stackable plastic crates.`

> `Refrigeration unit: a high fluorocarbon (HFC) free and energy efficient monoblock refrigeration unit for 24/7 refrigeration, using 658 watts of energy per hour.`
> `The temperature is adjustable from -5 to +15° Celsius.`

> `Solar power: rooftop solar panels generating 5.5kw/h, connected to a set of deep-cycle, long lasting batteries, off grid and on grid inverters, runs the Hub in all weather.`

### Difference of your `Off-grid 1-tonne solar cold store v3` vs closest

Narrower 1-tonne staged instantiation, not new principle - as you state in novelty claim.

1. **Capacity / use-case:** 1000 kg / 50x20 kg crates vs 1.5-tonne test unit and 3-tonne / 150x20 kg ColdHubs. Your constraint is staged intake `250 kg per day` with max 8 openings, not full warm-tonne pull-down.
2. **Energy sizing for hotter design point:** `3.6 kWp split 2 on roof + 7 on ground`, 13.5 kWh/d yield for 10.4 kWh/d load at `5 C inside / 43 C ambient, 38 K lift, COP 1.40` vs 2 kW array in Nakuru paper and 5.5 kW rooftop-only ColdHubs. Split array is explicit because `17.6 sqm cannot fit` on cold-box roof.
3. **Storage chemistry explicit:** `48 V lithium iron phosphate` + MPPT + thermostat/probe control vs ColdHubs `deep-cycle` + inverter generic description, and vs Ecofrost alternative route:
> `patented Ice Core Technology that delivers 30+ hours of batteryless backup` with `4-5 kWp solar arrays with 5-6 metric ton` capacity in thermal-storage form.

Your v3 deliberately rejects ice-only / eutectic-only because thermal does not provide dispatchable electricity for fans, controls and compressor start - keeps thermal only as buffer.

4. **Refrigerant / serviceability choice:** DC variable-speed `R134a monoblock` chosen for village service at 43 C vs HFC-free monoblock in ColdHubs and variable-speed chiller in paper - same vapour-compression principle, different service / lift optimization.
5. **Structural scope included:** soft-soil `150 kPa`, six pads at 23.2 kPa, wind uplift 673 kg vs 1390 kg screw-anchor hold, separate chamber and ground-frame paths - not described in ColdHubs / paper abstracts which focus on cooling performance.

In short: same `Sunlight -> electricity -> batteries -> vapour-compression cold air over crates near 5 C` working principle already demonstrated at 1.5-3 tonne; v3 difference is 1-tonne, 43 C, staged-load, split-array, LFP + R134a, anchored PIR-box package.


Sources:
- https://theindexproject.org/award/nominees/4322 — ColdHubs - solar cold rooms - The Index Project
- https://www.agriculturaljournals.com/archives/2025.v7.i9.A.1480/effectiveness-of-solar-powered-cold-storage-for-fresh-produce-preservation-in-remote-areas — Effectiveness of solar-powered cold storage for fresh produce preservation in remote areas
- https://smartbuy.alibaba.com/buyingguides/ecozen-cold-storage — How to Choose Ecozen Cold Storage: A Complete Buyer's Guide
- https://www.pv-magazine.com/2021/06/08/solar-powered-cold-storage-service/ — Solar-powered cold storage service
- https://ireap.thecleannetwork.org/products/35 — IREAP- Product Details
- https://coldchainsa.com/powering-the-cold-chain-renewable-energy-solutions-for-south-african-cold-storage-operations/ — Powering the Cold Chain: Renewable Energy Solutions for South African Cold Storage Operations
- https://ireap.thecleannetwork.org/products/33 — IREAP- Product Details
- https://www.pv-magazine-india.com/2021/06/07/solar-powered-cold-storage-as-a-service/ — Solar-powered cold storage as a service
- https://www.electronicsforu.com/electronics-startups/ecofrost-made-in-india-solar-powered-cold-storage-to-reduce-crop-spoilage — Ecofrost: Made In India Solar-Powered Cold Storage To Reduce Crop Spoilage
- https://agtecher.com/en/hardware/ecofrost-solar-cold-storage/ — Ecofrost Solar Cold Storage: Sustainable... | AgTecher
- https://pmarketresearch.com/auto/solar-powered-cold-room-market/ — Solar Powered Cold Room Market
- https://www.youtube.com/shorts/1L2ijQ9wl0E — They Built a Farm Cold Room That Runs Without Electricity or Batteries? 🤯
- https://our-power.co.uk/solar-powered-ice-makers/ — Solar powered ice maker: off-grid cold chain explained
- https://theindexproject.org/award/nominees/1952 — ColdHubs - The Index Project
- https://techxlab.org/solutions/cold-rooms-by-coldhubs/ — Cold Rooms by ColdHubs
- https://www.sidley.com/en/probonolanding/sidley-emerging-enterprises-pro-bono-program/projects/coldhubs-ltd — ColdHubs Ltd | Sidley Emerging Enterprises Pro Bono Program | Pro Bono | Sidley Austin LLP
- https://energypedia.info/index.php?title=ColdHubs_-_Solar_Cold_Rooms_in_Nigeria&oldid=304340 — ColdHubs - Solar Cold Rooms in Nigeria
- https://theindexproject.org/diseno-responde/winnersandfinalists/4322 — ColdHubs - solar cold rooms - The Index Project
- https://solve.mit.edu/challenges/coastal-communities/solutions/5035/application — MIT Solve | ColdHubs
- https://www.sitra.fi/en/cases/communal-refrigerated-buildings-powered-by-the-sun/ — Communal refrigerated buildings powered by the sun
- https://www.deutschland.de/en/solar-powered-coldhubs-nigeria — Solar-powered ColdHubs, Nigeria
- https://www.iiec.org/coolingdemo-technologies/711-commercial-refrigeration/687-walk-in-solar-powered-cold-stations-controls-cycle-optimisation-cold-hubs — Walk-in, solar-powered cold stations - Controls & Cycle Optimisation (Cold Hubs)
- https://uspatents.landoffree.com/patent/solar-powered-refrigeration-system-2 — LandOfFree - Inventor - Solar-powered refrigeration system
- https://uspatents.landoffree.com/patent/solar-powered-refrigeration-system — LandOfFree - Inventor - Solar-powered refrigeration system
- https://patents.glgoo.top/patent/CN108431512B/en — CN108431512B - Solar air cooler 
        - Google Patents
- https://www.scinovex.com/articles/W7160699909.pdf — Effectiveness of solar-powered cold storage for fresh produce preservation in remote areas
- https://data.epo.org/publication-server/rest/v1.2/publication-dates/20170405/patents/EP3150932NWA1/document.pdf — SOLAR AIRCOOLER - European Patent Office - EP 3150932 A1
- https://www.ijprems.com/ijprems-paper/Design-and-Sizing-Analysis-of-a-SolarPowered-VapourCompression-Mini-Cold-Storage-System-for-Vegetables-with-IoT-Control — | INTERNATIONAL JOURNAL OF PROGRESSIVE | e-ISSN : |
- https://www.researchgate.net/figure/nsulated-milk-can-with-ice-compartment-a-Type-A-handmade-prototype-with-incorporated_fig2_324238779 — Insulated milk-can with ice compartment a) Type A-handmade prototype... | Download Scientific Diagram
- https://patents.justia.com/patent/20180274806 — US Patent Application for SOLAR AIRCOOLER Patent Application (Application #20180274806 issued September 27, 2018) - Justia Patents Search
- https://prism.sustainability-directory.com/scenario/decentralized-solar-cooling-for-perishable-supply-chains/ — Decentralized Solar Cooling for Perishable Supply Chains → Scenario