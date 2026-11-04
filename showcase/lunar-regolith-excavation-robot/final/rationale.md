# Rationale — Skid-Steer Kerf-and-Ladder Lunar Digger with Screw-Tilt Pour

Build a blind-operated lunar digger that traverses, loosens, collects, contains and discharges BP-1 soil within 60 kg mass and 1.0 by 0.5 by 0.5 m stowed box.

## Key estimates
- standing mass: 46.0 kg (calc; evidence ['E62', 'E66', 'E67'])
- stowed length: 0.9 m (simulate; evidence ['E51'])
- kerf cut force: 11.0 N (calc; evidence ['E64'])
- traction: 294.0 N (simulate; evidence ['E23'])
- ladder dig power: 16.4 W (calc; evidence ['E59'])
- dig energy per trip: 0.512 Wh (calc; evidence ['E60'])
- frame sag: 3.96 mm (calc; evidence ['E63'])
- watchdog stop distance: 0.308 m (simulate; evidence ['E32'])
- drift with fiducial reset: 0.15 m (simulate; evidence ['E33'])
- dump clearance: 0.15 m (simulate; evidence ['E51'])
- ground pressure: 15.6 kPa (calc; evidence ['E25'])

## Risks
- BP-1 arches over outlet and pour stalls — mitigation: Run half-full 15 kg trips and bench-test arching plus screw torque after build
- Rear tilt tips machine or misses bin blind — mitigation: Keep level-ground pour, fiducial creep align and heartbeat stop with 0.308 m stop

## Novelty
Narrow kerf loosening feeding wide ladder pickup with screw-metered tilt pour under camera-only blind operation

## Sources
- https://mine.geo.mtu.edu/Lunabotics.html
- http://dspace.bracu.ac.bd:8080/xmlui/handle/10361/7429
- https://forums.ni.com/t5/Student-Projects/Mile-High-Miners-Nasa-Lunabotics-Project-Colorado-School-of/ta-p/3528955
- https://www.alabamaastrobotics.com/nasa-lunabotics-2025.html
- https://attachments.are.na/44605482/3ed9028d0848397f5e6b39eca3d06c50.pdf?1774077464
- https://library.bracu.ac.bd/vufind/Record/10361-7429/Details
- http://dspace.bracu.ac.bd:8080/xmlui/feed/rss_2.0/10361/6991
- https://docslib.org/doc/13426284/a-review-of-extra-terrestrial-mining-robot-concepts
- http://dspace.bracu.ac.bd:8080/xmlui/feed/rss_1.0/10361/6991
- https://archive.org/stream/NASA_NTRS_Archive_20110016233/NASA_NTRS_Archive_20110016233_djvu.txt
- https://mechanical.sdsu.edu/design-day/_files/2024/ares.pdf
- https://www.researchgate.net/publication/262332670_A_Simple_Tele-Robotic_Lunar_Excavator
- https://pdfslide.net/documents/a-review-of-extra-terrestrial-regolith-excavation-concepts-.html
- https://www.slideserve.com/reuben-monroe/nasa-lunabotics-mining-competition-interim-design-presentation
- https://docslib.org/doc/9899597/a-review-of-extra-terrestrial-regolith-excavation-concepts-and-prototypes-lunar-isru-2019-july-17-2019-columbia-maryland
- http://missions.info-quest.org/Documents/PDF/5066_Mueller.pdf
- https://www.researchgate.net/publication/278117394_Productive_Lightweight_Robotic_Excavation_for_the_Moon_and_Mars
- https://lunarnetworks.blogspot.com/2013/01/chonodrobot-2-simple-efficient-semit.html
- https://ascelibrary.org/doi/abs/10.1061/9780784484470.023
- https://patents.google.com/patent/DE10157345C1/en
- https://www.osti.gov/biblio/6429955
- https://patents.google.com/patent/DE528341C/en
- https://patents.google.com/patent/DE497298C/en
- https://patents.google.com/patent/DE501439C/en
- https://patents.justia.com/patent/6533944
- https://c.91souke.com/extdomains/patents.google.com/patent/DE590778C/en
- https://patents.google.com/patent/DE9111981U1/en
- https://ntrs.nasa.gov/api/citations/20150009348/downloads/20150009348.pdf
- https://patents.google.com/patent/US6533944B1/en
- https://patents.google.com/patent/DE694594C/en
- http://dspace.bracu.ac.bd:8080/xmlui/feed/atom_1.0/10361/6991
- http://dspace.bracu.ac.bd:8080/xmlui/feed/atom_1.0/10361/6992
- https://www.infona.pl/contributor/1@bwmeta1.element.wiley-jai-v-28-i-2-jai1900/tab/publications
- https://www.infona.pl/contributor/1@bwmeta1.element.springer-doi-10_1186-S12884-018-2046-0/tab/publications?searchConf=authorResource&resultPage=2&q=sc*op*l_0*p_0iPP.20*p_0cP.1&resultItemPerPage=20&searchPhrase=
- https://lunarnetworks.blogspot.com/2013/01/chonodrobot-2-simple-efficient-semit.html
- https://engprojects.tcnj.edu/lunabotics26/tcnj-lunabotics-team/competition/
- https://github.com/mianqun/pantherlunabotics2025-2026/blob/HEAD/CLAUDE.md
- https://pdfslide.tips/download/link/lunabotics-rles.html
- https://www.science.gov/topicpages/n/nasa+lunar+mining
- https://digital.wpi.edu/downloads/4j03d2179?locale=en
- https://peer.asee.org/senior-design-experience-using-nasa-s-lunabotics-mining-competition-best-practices-and-evaluation-of-student-learning.pdf
- https://www.alabamaastrobotics.com/faq.html
- https://archive.org/stream/NASA_NTRS_Archive_20110016233/NASA_NTRS_Archive_20110016233_djvu.txt
- https://www.yumpu.com/xx/document/view/67075271/mechatronics-2013-recent-technological-and-scientific-advances-pdfdrive-/545
- https://www.science.gov/topicpages/r/remote+excavation+system
- https://patents.justia.com/patent/20240200447
- https://patents.justia.com/patent/20180345536
- https://patents.justia.com/patent/8061441
- https://patents.Google.Com/patent/CN209438556U/en
- https://patents.google.com/patent/DE497298C/en
- https://patents.google.com/patent/US1466568A/en
- https://patents.google.com/patent/CN214526319U/en
- https://eureka.patsnap.com/patent-CN106988356A
- https://patents.google.com/patent/CN114293987A/en
- https://patents.google.com/patent/JP2911881B1/en
- https://amanrajdce.github.io/data2/lunabot_sys_eng_paper.pdf
- https://www.researchgate.net/publication/262332670_A_Simple_Tele-Robotic_Lunar_Excavator
- https://library.bracu.ac.bd/vufind/Record/10361-7415/Details
- https://library.bracu.ac.bd/vufind/Record/10361-7310/Details
- http://dspace.bracu.ac.bd:8080/xmlui/feed/rss_2.0/10361/6992
- http://dspace.bracu.ac.bd:8080/xmlui/feed/rss_2.0/10361/6991
- https://web1.eng.famu.fsu.edu/me/senior_design/2011/team19/presentations/final_design.pdf
- http://dspace.bracu.ac.bd:8080/xmlui/feed/rss_1.0/10361/6991
- https://web1.eng.famu.fsu.edu/me/senior_design/2011/team19/presentations/springMidtermPresentation.pdf
- http://dspace.bracu.ac.bd:8080/xmlui/feed/rss_1.0/10361/6992
- https://core.ac.uk/download/pdf/10573073.pdf
- https://core.ac.uk/download/pdf/10569729.pdf
- https://vdocuments.net/regolith-advanced-surface-systems-operations-robot-advanced-surface-systems.html
- https://sciences.ucf.edu/class/wp-content/uploads/sites/23/2017/03/CLASS-SSERVI-Robotic-Construction-Mueller-v1-March-2017.compressed.pdf
- https://www.researchgate.net/profile/Rachel-Cox-7/publication/261248231_Regolith_Advanced_Surface_Systems_Operations_Robot_RASSOR/links/5c0fdb224585157ac1bb3893/Regolith-Advanced-Surface-Systems-Operations-Robot-RASSOR.pdf?origin=scientificContributions
- https://zenodo.org/records/1263919/files/article.pdf?download=1
- https://ntrs.nasa.gov/api/citations/20170002067/downloads/20170002067.pdf?attachment=true
- https://www.designfax.net/cms/dfx/opens/articleview.php?nid=4&bid=273&aid=2159&eid=
- https://www.nanowerk.com/news2/robotics/newsid=28702.php
- https://lsic.jhuapl.edu/uploadedDocs/presentations/932-Focus%20Area%20Presentations.pdf
- http://cs.roboticbuilding.eu/images/6/69/3.paper.pdf
- https://www.homelandsecuritynewswire.com/dr20130204-nasa-engineers-building-sturdy-bluecollar-mining-robot?page=0,0
- http://dspace.bracu.ac.bd:8080/xmlui/feed/atom_1.0/10361/6992
- http://dspace.bracu.ac.bd:8080/xmlui/feed/atom_1.0/10361/6991
- http://dspace.bracu.ac.bd:8080/xmlui/handle/10361/7429
- https://www.booksci.cn/literature_d127060_6.htm
- https://library.bracu.ac.bd/vufind/Record/10361-7429/Details
- http://dspace.bracu.ac.bd:8080/xmlui/feed/atom_1.0/10361/7016

## Master prompt revision history
- rev 1: ['## 4. Meeting protocol'] — No prompt change: six items are image-model leader/bracket fidelity limits against already-specified design (E51, E24, E64, E10, E11, E23, E25, E59, E60, E44, E32, E33, E62, E68, E63); no Roles or protocol gap, so no rewrite warranted.

## S1/S2 history
- attempt 0 round 0: S1 faithful=False S2 flaw=False decision=s1_retry
- attempt 0 round 1: S1 faithful=False S2 flaw=False decision=s1_retry
- attempt 0 round 2: S1 faithful=False S2 flaw=False decision=s1_exhausted
- attempt 1 round 0: S1 faithful=True S2 flaw=False decision=s1_pass

## Figure notes
- callouts Kerf Chain, Wedge Hopper, Folding Arms, Grouser Wheels pointed at the wrong part or were misspelled; the callouts were removed and code labelled the parts instead
- labels removed because they pointed at the wrong part: auger discharge screw, lithium phosphate battery packs
- how it works: 5 numbered steps drawn on panel A
- fabrication step 1 passed after one redraw (first attempt: Image shows wheels, winch, electronics and upper tube assembly already fitted to the frame, not the bare twin-tube aluminium chassis alone, so it is not fabrication step 1.)
- fabrication step 4 passed after one redraw (first attempt: Pixels show bucket ladder and wedge hopper with rear auger screw, but chassis has three tubes not twin-tube, wheels are small rubber caster-type not rigid grouser wheels, and left-end shows short drive loop not a narrow kerf trenching chain; stage/scale mix does not meet all listed parts for step 4.)
