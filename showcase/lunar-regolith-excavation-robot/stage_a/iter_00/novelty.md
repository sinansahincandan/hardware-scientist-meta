I'll search for the closest existing rover to your front-drum high-lift design.
Closest match:

**NASA RASSOR - Regolith Advanced Surface Systems Operations Robot - US 9,027,265 `Zero horizontal reaction force excavator` + IEEE Big Sky 2013 paper.**

* What it is:

> Teleoperated mobile platform with unique space regolith excavation capability, net-zero reaction force, to load, haul and dump under low-g

> Conceived 2011 counter-rotating bucket drum method, demonstrated at that year's NASA Lunabotics Mining Competition

> Protected as US patent 9,027,265, `Zero horizontal reaction force excavator`, granted 12 May 2015

> Listed by NASA as KSC-TOPS-7, KSC-13664 KSC-14032, Patent 9,027,265, Paper IEEE Big Sky 2013

Why closest:

1. Same job + same envelope: mine and haul simulant in `1 m long, 0.5 m wide, 0.5 m tall` and `maximum mass of 60 kg` Lunabotics rules vs RASSOR 2.0 `System mass 66 kg`, `Regolith payload 80 kg`.
2. Same digging principle: transverse bucket drum(s):
> Hollow cylinders with scoops staggered around perimeter; regolith enters through scoops, slides down internal baffle, transported inside drum, discharged by reversing rotation
> During loading scoops sequentially take multiple cuts while rotating at approximately 20 rpm. During hauling drums raised by rotating arms for clearance. On reaching dump, drums reverse rotation to expel soil.
3. Same mobility problem in BP-1: `metallic link tracks in Black Point 1 basalt simulant required many iterations`, tested vs `13 inch wheels` and `17 inch wheels in four wheel configuration`. `17 inch four wheel succeeded 3 of 3` on 25-deg tilt table vs tracks and 13-in once in three, selected with slightly lower drawbar pull and fewer failure modes.
4. Same remote operation: `wireless control, telemetry, and onboard transmitting cameras, allowing teleoperation with situational awareness`, `chassis symmetrical so machine continues after overturning`, `arms fold`, `control wireless with onboard transmitting cameras`.

Decisive difference vs this Concept `front bucket drum -> central hopper -> high-lift mast`:

* RASSOR = **dual counter-rotating drums on opposing arms** to `provide near-zero horizontal and minimal vertical net reaction force so excavation is not reliant on traction or weight`, reactions `cancel` and `net force approaches zero`, reacted internally not through traction. Concept = **single front transverse drum** feeding separate central hopper. Loses zero-reaction cancellation; must react `45.7 N cutting` with 60 kg chassis weight/traction.

* RASSOR = **drums ARE the hopper/hauler** - soil remains in raised drums during travel. Concept = drum + **separate 10 kg central hopper + rear high-lift mast with dual 500 N actuators to 1.05 m lip** to clear 1.0 m bin. RASSOR explicitly `eliminates need for onboard dump bin, thus reducing complexity and weight`.

* RASSOR dump = **stand up vertical Z-position to dump into receiving hopper without ramp**, `fold into Z with chassis vertical, one set drums/wheels on ground and other reaching from top`. Concept dump = stay level, lift hopper on mast to 1.05 m and gravity pour - adds tip-over moment, actuator/linkage and spill path not in RASSOR.

* RASSOR power / bus: `48 VDC bus`, 10 actuators, 27 cm/s avg, 56.5 cm/s max. Concept: 24 V pack, 4-wheel drive rigid chevron grouser wheels, sealed box + tilting sensor mast + dual-link heartbeat E-stop - mission-specific Lunabotics implementation, not RASSOR symmetric overturn-tolerant system.


Sources:
- https://github.com/djmorvay/ysu-nasa-lunabotics/blob/HEAD/README.md — djmorvay/ysu-nasa-lunabotics - README.md
- https://github.com/deejay2545/ysu-nasa-lunabotics — deejay2545/ysu-nasa-lunabotics — YSU NASA Lunabotics Rover - VHDL
- https://keplerelectronics.com/Wiki/Lunabotics_Senior — keplerelectronics
- https://www.futureengineers.org/lunaboticsjunior/gallery/56285 — Future Engineers :: Lunabotics Junior Challenge :: Gallery :: Phoebe
- https://www.researchgate.net/figure/The-Laurentian-University-Lunabot-during-the-2011-NASA-Lunabotics-Competition-Credit_fig11_272744550 — The Laurentian University Lunabot during the 2011 NASA Lunabotics...
- https://www.thomasnet.com/insights/university-of-virginia-bruno-excavation-rover-nasa-challenge/ — University of Virginia Students Win NASA Challenge With Excavation Rover
- https://forums.ni.com/t5/Student-Projects/Mile-High-Miners-Nasa-Lunabotics-Project-Colorado-School-of/ta-p/3528955 — Mile-High Miners Nasa Lunabotics Project (Colorado School of Mines)
- https://www.slideserve.com/fritzi/nasa-lunabotics-mining-competition-interim-design-presentation — PPT - NASA Lunabotics Mining Competition Interim Design Presentation PowerPoint Presentation - ID:2504869
- https://news.asu.edu/20201228-asu-lunabotics-team-competes-kennedy-space-center — ASU Lunabotics team competes at Kennedy Space Center
- https://www.futureengineers.org/lunaboticsjunior/gallery/56158 — Future Engineers :: Lunabotics Junior Challenge :: Gallery :: Lunar Robot
- https://www.futureengineers.org/lunaboticsjunior/gallery/54487 — Future Engineers :: Lunabotics Junior Challenge :: Gallery :: NASA CHARLIE LUNAR ROVER
- https://spaceref.com/science-and-exploration/rassor-the-moon-mining-robot-4/ — RASSOR, The Moon Mining Robot
- https://www.designfax.net/cms/dfx/opens/articleview.php?nid=4&bid=273&aid=2159&eid= — Designfax – Technology for OEM Design Engineers
- https://philosophy.hi7.co/mining-other-worlds-5716eec9eda44.html — Mining other worlds
- https://core.ac.uk/download/pdf/227725500.pdf — SRR ISRU COMPASS - V3 - Final-compressed more
- https://www.nanowerk.com/news2/robotics/newsid=28702.php — NASA working on mining robot for space missions
- https://www.academia.edu/108343315/Oxygen_Production_System_for_Refueling_Human_Landing_System_Elements — Oxygen Production System for Refueling Human Landing System Elements
- https://phys.org/news/2013-01-hard-working-robot.amp — Engineers building hard-working mining robot
- https://phys.org/news/2013-01-hard-working-robot.html?loadCommentsForm=1 — Engineers building hard-working mining robot
- https://www.scribd.com/document/351238756/Skonieczny2011 — Innovative Bucket-Wheel Design for Lunar Excavators | PDF | Moon | Mars
- https://space-robotics.org/robots/lunar/rassor/ — RASSOR | Space Robotics
- https://lsc-pagepro.mydigitalpublication.com/publication/?i=608807&p=18&view=issueViewer — Inside Unmanned Systems APR-MAY 2018 Page 18
- https://technology.nasa.gov/patent/KSC-TOPS-7 — Regolith Advanced Surface Systems Operations Robot (RASSOR) Excavator
- https://grabcad.com/challenges/nasa-regolith-advanced-surface-systems-operations-robot-rassor-bucket-drum-design-challenge — NASA Regolith Advanced Surface Systems Operations Robot (RASSOR) Bucket Drum Design Challenge  | Engineering & Design Challenges | GrabCAD
- https://ntrs.nasa.gov/citations/20150022134 — RASSOR - Regolith Advanced Surface Systems Operations Robot - NASA Technical Reports Server (NTRS)
- https://prezi.com/sz_4bygwhgsp/rassor/ — RASSOR by 21171 21171 on Prezi
- https://nasa3d.arc.nasa.gov/detail/RASSOR — Regolith Advanced Surface Systems Operations Robot (RASSOR) | 3D Resources
- https://techport.nasa.gov/view/125628 — NASA TechPort - Project
- https://science.nasa.gov/3d-resources/regolith-advanced-surface-systems-operations-robot-rassor/ — Regolith Advanced Surface Systems Operations Robot (RASSOR) - NASA Science
- https://bigthink.com/hard-science/nasa-moon-robot/432 — Want to help design a moon robot? NASA needs you.
- https://www.highergov.com/contract/80NSSC22PA953/ — STTR
  
  Lunar Surface Site Preparation for Landing/Launch Padand Blast Shield Construction