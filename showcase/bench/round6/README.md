# Round 6 benchmark (2026-11-04)

Six problems (01 stair hand truck, 02 solar cold room, 03 footbridge damper, b1 lunar excavator, b2 robot fingertip,
b3 wind turbine). Three systems: one prompt to Muse Spark (baseline_v2, the same designs as round 5), Hardware
Engineer on the Meta Model API (round-6 runs, after the SPEC-14 fixes), Hardware Engineer on open weights (round-6
runs; the stair truck and the turbine ran out of the $80 open-weights budget before an accepted design and are not
judged). Blind packets with salt r12 (`bench6_key.json` maps A/B/C to systems). Two passes, each pass split over
two independent Claude judge agents (`bench6_scores_p1a/p1b` = pass 1, `p2a/p2b` = pass 2), rubric
`examples/bench/RUBRIC_v3.md` (fault audit before any score). Summary computed by `showcase/video_src/bench6.py`
into `bench6_summary.json`; slide `bench6_slide.png`.

| | mean of 40 over problems | ± std |
|---|---|---|
| Hardware Engineer (Meta API) | 26.2 | 2.9 |
| One Meta prompt | 26.9 | 3.0 |
| Hardware Engineer (open weights, 4 problems) | 26.1 | 2.5 |

Gain per problem −2% ± 16%: a tie. HE ahead in 4 of 12 verdicts. No fatal faults in any design; major faults per
judge pass: HE 16.5, one prompt 17.5, open weights 15.0 (4 problems). Criterion sums (of 30): HE ahead on numbers
right and supported (20 vs 17.5) and how it is made (22 vs 21); behind on picture shows the design (13.5 vs 16),
physically works (21 vs 22.5), explains how it works (20.5 vs 22.5), no image-generator mistakes (17.5 vs 18.5).
Since round 5: HE making plans 19.5 → 22; HE open weights 19.2 → 26.1. Picture–text contradictions remain HE's main
weakness (turbine drawn with four blades for a three-blade rotor although SAM counted four; footbridge drawn as a
slab on two columns; hand-truck climbing clusters drawn as a caster base).
