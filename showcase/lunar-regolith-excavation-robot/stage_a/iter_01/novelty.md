Your drum-and-high-lift rover looks like Lunabotics territory — I'll line up the closest real rover, patent, and paper to define the difference.
I've pinpointed NASA's counter-rotating drum excavator as the closest match — now I'll pull the details to spell out exactly how your single-drum plus lift-mast design differs.
Closest match: **NASA RASSOR - Regolith Advanced Surface Systems Operations Robot**

**Product / Patent / Paper are the same system:**

* Product: `RASSOR Excavator` - `teleoperated mobile robotic platform with a unique space regolith excavation capability` with `net-zero reaction force, thus allowing it to load, haul, and dump space regolith`
* Patent: `9,027,265` - Zero horizontal reaction force excavator
* Paper: `IEEE Big Sky 2013, Regolith Advanced Surface Systems Operations Robot (RASSOR), 03/02/2013`

Detailed in UW-Madison TR-2024-02: `RASSOR operates with two counter-rotating bucket drums on its arms to minimize reaction forces horizontally and vertically, enabling a lighter design.` Vehicle is `chassis, four wheels, two arms and two buckets`

### Why it is closest

1. WheeledISRU excavator: `compact, lightweight` rover for `In Situ Resource Utilization (ISRU)` to `make local commodities, such as propellants and breathing air`
2. Drum excavator: `bucket drums excavate soil/regolith by scoops mounted on the drums exteriors that sequentially take multiple cuts` `rotating at approximately 20 revolutions per minute`, same as proposed front transverse spinning drum scooping soil.
3. Teleoperated with loss-of-signal relevance: `wireless control, telemetry, and onboard transmitting cameras, allowing for teleoperation with situational awareness`, `can be programmed to operate autonomously for selected tasks`
4. High-dump to bin: `capable of standing up in a vertical position to dump into a receiving hopper without using a ramp`

### Decisive difference

Your concept replaces RASSOR's core principles with a **single-drum + separate high-lift hopper architecture:**

* **Excavation:** RASSOR `uses counterrotating bucket drums on opposing arms to provide near-zero horizontal and minimal vertical net reaction force so that excavation is not reliant on the traction or weight of the mobility system`. Proposed concept uses **one** front transverse 200mm drum with 30mm shallow cut for 39 N reaction, accepting traction reaction and relying on 300mm grouser wheels + centred hopper load.

* **Haul + Dump:** RASSOR: `During hauling, the bucket drums are raised by rotating the arms` `while the soil/regolith remains in the raised bucket drums`, `the bucket drums are commanded to reverse their direction of rotation, which causes soil/regolith to be expelled`. It `eliminates the need for an onboard dump bin`.

  Proposed concept **adds** onboard bin: central hopper rides `Rear high-lift mast with dual actuators and chain` to 1.05m pour lip with 0.30m overhang - 0.15m stroke through 4-to-1 chain at 0.80 efficiency. That mast, tip-moment about rear axle, actuator force, and `0.45m stowed pivot on 0.60m guide` geometry have no counterpart in RASSOR.

In short: **RASSOR = dual opposed drums that ARE the hopper and dump by reverse-spin; Proposed = single front drum that FEEDS a separate rear-lifted hopper that dumps by high-lift pour.**


Sources:
- https://www.science.gov/topicpages/e/engineering+autonomous+space — engineering autonomous space: Topics by Science.gov
- http://www.amfcse.org/s/Lunabotics-Guidebook-2027-10-12-27.pdf — NASA LUNABOTICS CHALLENGE guideBOOK 2026 - 2027
- https://github.com/asher-plihal/pantherlunabotics2025-2026/blob/HEAD/CLAUDE.md — asher-plihal/pantherlunabotics2025-2026 - CLAUDE.md
- https://www.science.gov/topicpages/r/remote+excavation+system — remote excavation system: Topics by Science.gov
- https://github.com/roialrogue/pantherlunabotics2025-2026/blob/HEAD/.claude/CLAUDE.md — roialrogue/pantherlunabotics2025-2026 - .claude/CLAUDE.md
- https://github.com/mianqun/pantherlunabotics2025-2026/blob/HEAD/CLAUDE.md — PantherLunabotics2025-2026/CLAUDE.md at 560db41c814db934193b98d364d5717375efb8ce · mianqun/PantherLunabotics2025-2026
- https://ni.lithium.com/ni/attachments/ni/3035/2049/1/Systems%20Engineering%20Report%20_Mile-High%20Miners.pdf — Fall 2011 NASA Lunabotics Mining Competition Systems Engineering Paper
- https://www.science.gov/topicpages/n/nasa+lunabotics+mining — nasa lunabotics mining: Topics by Science.gov
- https://core.ac.uk/download/pdf/10572014.pdf — https://ntrs.nasa.gov/search.jsp?R=20120017902 2019-08-30T23:19:56+00:00Z
- https://jenikirbyhistory.getarchive.net/amp/media/ksc-2011-4154-158899 — CAPE CANAVERAL, Fla. -- A remote controlled or autonomous excavator, called a lunabot, is on display outside of the "Lunarena" at the Kennedy Space Center Visitor Complex in Florida where university students maneuver their remote controlled lunabots, in a "sand box" of ultra-fine simulated lunar soil during NASA's second annual Lunabotics Mining Competition. Thirty-six teams of undergraduate and graduate students from the United States, Bangladesh, Canada, Colombia and India will participate in NASA's Luna…
- https://space-robotics.org/robots/lunar/rassor/ — RASSOR | Space Robotics
- https://ntts-prod.s3.amazonaws.com/t2p/prod/t2media/tops/pdf/KSC-TOPS-7.pdf — Robotics, Automation and Control
- https://lsc-pagepro.mydigitalpublication.com/publication/?i=608807&p=18&view=issueViewer — Inside Unmanned Systems APR-MAY 2018 Page 18
- https://technology.nasa.gov/patent/KSC-TOPS-7 — Regolith Advanced Surface Systems Operations Robot (RASSOR) Excavator
- https://space-robotics.org/robots/lunar/ipex/ — Infrastructure Pilot Excavator
- https://grabcad.com/challenges/nasa-regolith-advanced-surface-systems-operations-robot-rassor-bucket-drum-design-challenge — NASA Regolith Advanced Surface Systems Operations Robot (RASSOR) Bucket Drum Design Challenge  | Engineering & Design Challenges | GrabCAD
- https://ntrs.nasa.gov/citations/20150022134 — RASSOR - Regolith Advanced Surface Systems Operations Robot - NASA Technical Reports Server (NTRS)
- https://nasa3d.arc.nasa.gov/detail/RASSOR — Regolith Advanced Surface Systems Operations Robot (RASSOR)
- https://prezi.com/sz_4bygwhgsp/rassor/ — RASSOR by 21171 21171 on Prezi
- https://ntrs.nasa.gov/citations/20210011366 — Design of an Excavation Robot: Regolith Advanced Surface Systems Operations Robot (RASSOR) 2.0
- https://science.nasa.gov/3d-resources/regolith-advanced-surface-systems-operations-robot-rassor/ — Regolith Advanced Surface Systems Operations Robot (RASSOR) - NASA Science
- https://sbel.wisc.edu/wp-content/uploads/sites/569/2024/05/TR-2024-02.pdf — Simulation-Based Engineering Lab University of Wisconsin-Madison Technical Report TR–2024–02 A Framework for Designing NASA’s RASSOR Rover using Project
- https://vc.easychair.org/publications/preprint/9KVr/download — EasyChair Preprint
- https://s.iafastro.directory/iac/paper/id/80002/abstract-pdf/IAC-23,A3,IP,11,x80002.brief.pdf?2023-04-06.16:46:15 — Paper ID: 80002
- https://m.easychair.org/publications/preprint/9KVr/open — EasyChair Preprint
- http://iafastro.directory/iac/paper/id/63057/abstract-pdf/GLEX-2021,10,1,7,x63057.brief.pdf?2021-02-26.10%3A43%3A42 — Paper ID: 63057
- https://p.iafastro.directory/iac/paper/id/80002/abstract-pdf/IAC-23,A3,IP,11,x80002.brief.pdf?2023-04-06.16:46:15 — IAF SPACE EXPLORATION SYMPOSIUM (A3)
- http://iafastro.directory/iac/paper/id/63057/abstract-pdf/GLEX-2021,10,1,7,x63057.brief.pdf?2021-02-26.10:43:42 — Paper ID: 63057