# Lessons (knowledge/lessons.md)

Process lessons for the Manager and the optimizer (round 3 B12: pipeline-mechanics lessons and duplicates removed 2026-11-02; members do not receive them). Each lesson has an id; indented notes say whether it helped in a later run.

## Process
- L16: Council consensus should explicitly record the host-system mounting interface alongside internal assembly order so verification judges integration completeness, not isolated device shape. [2026-11-02, run 20261102-184913_tactile-fingertip-sensor-for-robot-hands]
- L17: Council deliberation should require adjacent-domain owners to jointly confirm soft-to-rigid transition compatibility before agreement so layer sequence is buildable as well as depictable. [2026-11-02, run 20261102-184913_tactile-fingertip-sensor-for-robot-hands]

- L15: Council consensus should explicitly confirm viewpoint-specific layout order of major assemblies, not only parts presence, so downstream checks judge agreed structure over isolated components. [2026-11-02, run 20261102-153907_lunar-regolith-excavation-robot]
  - used in run 20261102-184913_tactile-fingertip-sensor-for-robot-hands: Applied: explicit stacking-order agreement helped judge the rendering faithful on agreed structure.

- L14: Council consensus should record which capacity or quantity depictions may be representative rather than literal so visual verification judges structural intent over exact counts. [2026-11-02, run 20261102-112524_off-grid-solar-powered-cold-storage-for-]
  - used in run 20261102-121628_vibration-retrofit-for-a-lively-pedestri: Applied: judging structural intent over exact counts helped accept S1 pass with S2=False as faithful.
  - used in run 20261102-153907_lunar-regolith-excavation-robot: Applied: judging structural intent over exact counts helped accept S1 pass with S2=False as faithful.
  - used in run 20261102-184913_tactile-fingertip-sensor-for-robot-hands: Applied: judging structural intent over exact counts helped accept S1 pass with S2=False as faithful.

- L11: Manager should require meeting consensus to record joint structural commitments with explicit owner per commitment so downstream accountability stays clear. [2026-11-02, run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou]


- L1: When the Manager revises Meeting protocol and Criteria, it must also align Roles so decision ownership stays consistent with the new process and standards. [2026-11-02, run 20261102-022817_stair-climbing-hand-truck-for-parcel-cou]
  - used in run 20261102-153907_lunar-regolith-excavation-robot: Applied: revising Roles alongside Meeting protocol and Criteria helped keep decision ownership consistent and reach evaluator acceptance in iter 1.
  - used in run 20261102-175237_tactile-fingertip-sensor-for-robot-hands: Applied: manager revised Roles together with Meeting protocol and Criteria after rejection, following L1 with effect pending next iteration.
- L2: Meeting protocol should require each member to articulate domain-specific constraints and cross-domain tradeoffs explicitly before agreement, so consensus integrates distinct expertise. [2026-11-02, run 20261102-022817_stair-climbing-hand-truck-for-parcel-cou]
  - used in run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou: Applied: consensus in 4 cycles suggests explicit domain constraints helped integrate distinct expertise.
  - used in run 20261102-112524_off-grid-solar-powered-cold-storage-for-: Applied: consensus close in 4 cycles suggests explicit domain constraints helped integrate distinct expertise.
  - used in run 20261102-121628_vibration-retrofit-for-a-lively-pedestri: Applied: consensus close in 4 cycles suggests explicit domain constraints helped integrate distinct expertise.
  - used in run 20261102-153907_lunar-regolith-excavation-robot: Applied: distinct domain roster sustaining 4-cycle deliberation suggests explicit constraints helped integrate excavation, autonomy, power, and structures expertise.

- L3: When a meeting closes by cap and the evaluator rejects, require the manager edit to target Roles and Meeting protocol in addition to Criteria to restore consensus close in the next iteration. [2026-10-31, run 20261031-220800_vibration-retrofit-for-a-lively-pedestri]
  - used in run 20261102-153907_lunar-regolith-excavation-robot: Applied: targeting Roles and Meeting protocol plus Criteria after cap-close rejection helped convert iter 0 reject into iter 1 accept.
  - used in run 20261102-175237_tactile-fingertip-sensor-for-robot-hands: Applied: after cap-close plus evaluator reject the manager targeted Roles and Meeting protocol in addition to Criteria, following L3 with effect pending next iteration.
- L4: When meetings repeatedly close by cap and evaluator rejects, require manager to make a converging edit or scope cut rather than no-op carryover to next iter. [2026-10-31, run 20261031-170455_stair-climbing-hand-truck-for-parcel-cou]
  - used in run 20261102-175237_tactile-fingertip-sensor-for-robot-hands: Applied: manager made substantive converging edit to three sections rather than no-op carryover, following L4 with effect pending next iteration.
- L5: Require cited evidence ids before any ready vote in the meeting protocol. [2026-10-31, run 20261031-154319_stair-climbing-hand-truck-for-parcel-cou]

## Prompts
- L12: Master prompts should state intended viewpoint and operational setting alongside parts so council agreement and visual verification share the same framing. [2026-11-02, run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou]
  - used in run 20261102-112524_off-grid-solar-powered-cold-storage-for-: Applied: viewpoint plus operational setting in image prompt helped share framing between agreement and verification.
  - used in run 20261102-121628_vibration-retrofit-for-a-lively-pedestri: Applied: viewpoint plus operational setting in image prompt helped share framing between agreement and verification.
  - used in run 20261102-153907_lunar-regolith-excavation-robot: Applied: stating side-view viewpoint plus granular-soil operational setting helped share framing between agreement and verification.

- L6: Master prompts should specify connection topology between parts, not just a parts list, so council deliberation and visual verification share the same structural ground truth. [2026-11-02, run 20261102-025924_stair-climbing-hand-truck-for-parcel-cou]
  - used in run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou: Applied: topology-rich prompt helped achieve S1 faithful=True with no material difference.
  - used in run 20261102-121628_vibration-retrofit-for-a-lively-pedestri: Applied: connection topology in prompt helped achieve S1 faithful=True with matching parts and orientations.
  - used in run 20261102-153907_lunar-regolith-excavation-robot: Applied: connection-rich prompt with drum, wheels, chassis, and mast topology helped achieve S1 faithful=True with matching arrangement.
  - used in run 20261102-184913_tactile-fingertip-sensor-for-robot-hands: Applied: topology-rich agreement on stacking order and load path helped achieve S1 faithful=True.

- L7: Council rosters should define complementary specialties with explicit ownership areas so deliberation covers all domains without overlap or gaps. [2026-11-02, run 20261102-022817_stair-climbing-hand-truck-for-parcel-cou]
  - used in run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou: Applied: complementary roster with distinct ownership helped reach fast consensus without gaps.
  - used in run 20261102-112524_off-grid-solar-powered-cold-storage-for-: Applied: complementary roster with distinct ownership areas helped reach consensus without gaps.
  - used in run 20261102-121628_vibration-retrofit-for-a-lively-pedestri: Applied: complementary roster with distinct ownership helped reach fast consensus without gaps.
  - used in run 20261102-153907_lunar-regolith-excavation-robot: Applied: complementary Mara/Theo/Priya/Sam ownership areas helped cover all domains without gaps for the rover design.
  - used in run 20261102-175237_tactile-fingertip-sensor-for-robot-hands: Applied: complementary roster with distinct ownership areas was used yet iter 0 still closed without acceptance, so ownership alone did not ensure consensus.
  - used in run 20261102-184913_tactile-fingertip-sensor-for-robot-hands: Applied: complementary roster with distinct ownership helped cover sensing, materials, electronics, and integration without gaps.

## Tools

- L8: Require manager edits to tie directly to evaluator rejection reason with converging scope; expanding edited sections without convergence does not resolve cap-reject loops. [2026-10-31, run 20261031-184531_stair-climbing-hand-truck-for-parcel-cou]

## Image model
- L13: Manager image briefs should specify intended support and mounting treatment for ground-standing assemblies so rendering does not invent extra foundations or merge distinct structures. [2026-11-02, run 20261102-112524_off-grid-solar-powered-cold-storage-for-]

- L9: Visual faithfulness judgments should prioritize presence, placement, and connectivity of major structures over exact counts of repeated elements, which generative rendering approximates imprecisely. [2026-11-02, run 20261102-042726_off-grid-solar-powered-cold-storage-for-]
  - used in run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou: Applied: judging by major structures presence and connectivity helped confirm faithful rendering.
  - used in run 20261102-112524_off-grid-solar-powered-cold-storage-for-: Applied: accepting partial load as faithful shows prioritizing presence and placement over exact counts helped.
  - used in run 20261102-121628_vibration-retrofit-for-a-lively-pedestri: Applied: prioritizing presence, placement and connectivity helped confirm faithful rendering despite S2=False.
  - used in run 20261102-153907_lunar-regolith-excavation-robot: Applied: prioritizing presence, placement, and connectivity helped accept S1 pass with S2=False as faithful despite rendering approximation.
  - used in run 20261102-184913_tactile-fingertip-sensor-for-robot-hands: Applied: prioritizing presence, placement, and connectivity over exact counts helped confirm faithful rendering.

- L10: Image prompts for multi-part products should enumerate all major structures and their visible connections from the chosen viewpoint to achieve faithful rendering. [2026-11-02, run 20261102-025924_stair-climbing-hand-truck-for-parcel-cou]
  - used in run 20261102-105608_stair-climbing-hand-truck-for-parcel-cou: Applied: enumerating major structures and connections helped produce faithful first-round rendering.
  - used in run 20261102-121628_vibration-retrofit-for-a-lively-pedestri: Applied: enumerating major structures and visible connections helped produce faithful first-round rendering.
  - used in run 20261102-153907_lunar-regolith-excavation-robot: Applied: enumerating major structures and visible side-view connections helped produce faithful rendering by round 1.

## User feedback
