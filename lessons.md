# Lessons

## Process
- Allow a cap-closed meeting with extended cycles to proceed to evaluator archiving and Stage-B retries when the evaluator accepts, rather than auto-blocking advancement on closed_by=cap alone. [2026-11-01, run 20261101-165746_off-grid-solar-powered-cold-storage-for-]
- Permit up to two consecutive s1_retry rounds within the same evaluator-accepted iteration to reach s1_pass without forcing a Stage-A return or new iteration. [2026-11-01, run 20261101-165746_off-grid-solar-powered-cold-storage-for-]

- Permit S1 fidelity retry within the same evaluator-accepted iteration to advance from s1_retry to s1_pass without reopening the meeting or forcing a Stage-A return. [2026-11-01, run 20261101-161405_vibration-retrofit-for-a-lively-pedestri]

- When a meeting closes by cap and the evaluator rejects, require the manager edit to target Roles and Meeting protocol in addition to Criteria to restore consensus close in the next iteration. [2026-10-31, run 20261031-220800_vibration-retrofit-for-a-lively-pedestri]
- Treat evaluator accept with all rounds S1=False as interim archiving only; allow a designer Stage-A return diagnostic to supersede acceptance and continue the pipeline. [2026-10-31, run 20261031-220800_vibration-retrofit-for-a-lively-pedestri]
- After code-label fallback clears label-driven S1 failures, shift S1 retry focus explicitly to geometry and connection fidelity rather than re-checking labels. [2026-10-31, run 20261031-220800_vibration-retrofit-for-a-lively-pedestri]
- Allow S1=True to drive s1_pass and archiving even when S2=False, keeping fidelity success independent from compliance rework. [2026-10-31, run 20261031-220800_vibration-retrofit-for-a-lively-pedestri]

- Gate evaluator archiving on S1 fidelity: do not accept/archive an iteration where every render round is S1=False, even if meeting closed by consensus. [2026-10-31, run 20261031-212855_off-grid-solar-powered-cold-storage-for-]
- Once code-label / text-free fallback is triggered, start the next iteration round 0 with the text-free variant; do not attempt further in-pixel label retries. [2026-10-31, run 20261031-212855_off-grid-solar-powered-cold-storage-for-]
- Empower designer stage to force return to Stage A with a fidelity diagnostic after consecutive S1 failures, rather than waiting for evaluator rejection or manager edit. [2026-10-31, run 20261031-212855_off-grid-solar-powered-cold-storage-for-]

- Block evaluator submission when meeting closed_by=cap; require consensus close before advancing, since cap-closed cycles correlate with rejection. [2026-10-31, run 20261031-184531_stair-climbing-hand-truck-for-parcel-cou]
- Cap Stage-B render retries at 2 attempts; on second consecutive S1 failure return to Stage A instead of spending a third same-stage retry. [2026-10-31, run 20261031-184531_stair-climbing-hand-truck-for-parcel-cou]
- Keep S1 fidelity and S2 compliance as separate gated decisions so retry logic distinguishes render rework from criteria return. [2026-10-31, run 20261031-184531_stair-climbing-hand-truck-for-parcel-cou]

- Trigger code-label / text-free fallback after 2 consecutive label-driven S1 failures instead of spending a third render round on text retry. [2026-10-31, run 20261031-170455_stair-climbing-hand-truck-for-parcel-cou]
- When meetings repeatedly close by cap and evaluator rejects, require manager to make a converging edit or scope cut rather than no-op carryover to next iter. [2026-10-31, run 20261031-170455_stair-climbing-hand-truck-for-parcel-cou]

- Require cited evidence ids before any ready vote in the meeting protocol. [2026-10-31, run 20261031-154601_vibration-retrofit-for-a-lively-pedestri]

- Require cited evidence ids before any ready vote in the meeting protocol. [2026-10-31, run 20261031-154540_off-grid-solar-powered-cold-storage-for-]

- Require cited evidence ids before any ready vote in the meeting protocol. [2026-10-31, run 20261031-154319_stair-climbing-hand-truck-for-parcel-cou]



## Prompts
- Sequence S1 retry prompt edits by failure class: resolve component-omission/geometry fidelity first, then label/text fidelity on the next retry, rather than mixing both fixes in one retry. [2026-11-01, run 20261101-165746_off-grid-solar-powered-cold-storage-for-]

- Include a pre-approved NO TEXT, NO LABELS, NO NUMBERS prompt variant in the prompt library for use once label fidelity blocks acceptance. [2026-10-31, run 20261031-170455_stair-climbing-hand-truck-for-parcel-cou]



## Tools
- Require manager edits to tie directly to evaluator rejection reason with converging scope; expanding edited sections without convergence does not resolve cap-reject loops. [2026-10-31, run 20261031-184531_stair-climbing-hand-truck-for-parcel-cou]



## Image model
- Do not require the image model to render exact strings, symbols, or numeric values in-pixel; treat all precise text as code overlay work because repeated S1 failures persist across retries. [2026-10-31, run 20261031-170455_stair-climbing-hand-truck-for-parcel-cou]



## User feedback
