# SUMMARY.md — hand-off (AUTOPILOT §6)

## Runs that exist (final, accepted, real API)

| Example | Final run folder | Cost | Result |
|---|---|---|---|
| 01 Stair-climbing hand truck | `runs/20261031-184531_stair-climbing-hand-truck-for-parcel-cou/` | $7.2244 (+$0.04 panel-D regen) | accepted, 7 iters |
| 02 Solar cold room | `runs/20261031-212855_off-grid-solar-powered-cold-storage-for-/` | $1.9136 (+$0.06) | accepted, 2 iters |
| 03 Footbridge damping | `runs/20261031-220800_vibration-retrofit-for-a-lively-pedestri/` | $2.5186 (+$0.04) | accepted, 3 iters |

Each final folder contains `report.html`, `board.html`, `final/figure.png`
(panels A–D + `force_flow.png`), and `REVIEW.md`. Two earlier example-01
runs are kept as broken runs, each with its own `REVIEW.md`
(`20261031-170455` best-effort, `20261031-175744` crashed).

- Compare page: `runs/compare_20261031-230924.html`
- Showcase page: `runs/showcase.html` (`hs showcase <run> <run> <run>`)
- Open each run's `report.html` (deliverable header: mechanism sentence,
  panel A, three decisive choices, open question) and `board.html`
  (working step-by-step whiteboard replay).

## What changed and why (all `FIX:`/`SPEC:` commits)

- **§7 implemented** (`SPEC_CHANGES.md`): image-drawn labels with S1
  label checking and code-label fallback after two failures; structured
  visual plan; pixel-first designer review (observed/ambiguous/missing
  + stage at fault); Secretary deliverable fields (mechanism sentence,
  exactly 3 decisive choices, 1 open question, transfer line); vetted
  calculators with input provenance; persona-driven literature search.
- **Whiteboard was empty in real runs** — the tool schema declared only
  `action`, so models packed fields into the action string. Full §12.16
  schema + defensive unwrapping; meetings now close by consensus.
- **Real-turn history** is now recorded (board replay works for real runs).
- **Optimizer headings** are canonicalized ("Meeting protocol" →
  "## 4. Meeting protocol"); rewrites actually land; `rewrite.json` saved.
- **Chain expiry** (`previous_response_id` 400, provider-side): same-request
  retries, up to 4 fresh chain restarts per turn, one whole-turn retry.
- **Evaluator** no longer demands bench traces (spec §4.5/§13 alignment;
  accept bar unchanged). Run costs dropped sharply after this fix.
- **Visuals**: schematic layout rank-normalized; annotator labels in
  readable side margins; figure layout from measured panel heights;
  fabrication steps regenerated as workshop scenes; force-flow view.

## Total runtime cost

**$16.37** across every `cost.json` in `runs/` (real model spend ≈ $16.02
plus $0.35 fake synthetic and ≈ $0.05 smoke probes logged outside `runs/`).
Session budget was $60 — not approached, no BLOCKED.md needed.

## Verification

- `HS_SMOKE=1 .venv/bin/python -m pytest tests/test_smoke_real.py -q` → 2 passed
- `.venv/bin/python -m pytest -q` → 29 passed, 2 skipped (real smoke, opt-in)
- `.venv/bin/ruff check src tests` → clean
- Every panel A, figure, schematic, annotated render, force-flow view,
  sketch and panel D of the final runs was opened and looked at as an image.

## Open problems (honest)

1. **No HTML screenshots**: Chromium crashes under this sandbox and
   WeasyPrint lacks pango, so `docs/screens/` holds the three panel-A
   images (the system's best visuals, below) instead of 1920×1080 page
   captures. Board/report pages were verified structurally and through
   their embedded images, not as browser screenshots.
2. The schematic remains a grid diagram, not a mechanism sketch like
   `docs/design/ref_reference_sketch_two_states.png` (a two-state view
   is generated alongside it).
3. Image-label quality is inconsistent: S1 rejects many first renders
   for mispointed leaders (by design), so Stage B usually needs the
   retry loop or a return to Stage A. Costs stay modest because of it.
4. Example 02's evaluator never rejected, so its Manager rewrite was
   triggered by a designer return, not an evaluator rejection.
5. Panel B is a crop of panel A in the final runs (the one generated
   close-up that passed its light check was a hallucinated diagram;
   it was replaced — see run 03 REVIEW.md).

## The three screenshots that best show the system

- `docs/screens/01_stair_truck_panel_A.png` — tri-star hand truck on
  stairs, parcel aboard, image-drawn labels verified by S1.
- `docs/screens/02_solar_cold_room_panel_A.png` — solar cold room with
  code-drawn margin labels, produce inside, cold airflow visible.
- `docs/screens/03_footbridge_panel_A.png` — twin 400 kg TMDs recessed
  in the inter-girder void (the S2 flaw fix made visible).

---

# v2 addendum (2026-11-01) — Hardware Scientist v2

## Final v2 runs (all in showcase/, each with REVIEW.md in runs/)

| Example | Run folder | How produced | Cost | Result |
|---|---|---|---|---|
| 01 Stair hand truck | `runs/20261101-154944_...` | Stage B rerun from v1 accepted solution | $0.2696 | S1 pass, round 0 |
| 02 Solar cold room | `runs/20261101-165746_...` | fresh full run | $1.3587 | accepted iter 0, S1 pass round 2 |
| 03 Footbridge TMD | `runs/20261101-161405_...` | fresh full run (rerun had routed back) | $1.9268 | accepted iter 1, S1 pass round 1 |

Total v2 session hs spend: **$7.14** (cap $40). Tests: 44 passed,
2 skipped; ruff clean.

## What v2 changed (spec first, then code; all pushed per item)
- **A** Region-anchored DesignerEval with source trace (render vs
  schematic), two-step TextGrad chain for Stage A/S2
  (gradient_output.json + gradient_prompt.json; optimizer consumes
  step 2 only), VLM prompt gradient for S1, local edit + composite
  with outside-box pixel assertion and progress check, Manager
  new_tool proposals capped at MAX_MANAGER_NEW_TOOLS=2 through the
  same sandbox/registry.
- **B** Manager sits in the room (own colour, manager_notes.md,
  end-of-cycle steering turn); speaking rule + cheap turn check with
  one retry; evidence reuse by id; mechanism sketch with joints,
  motion/load arrows, dimensions, and now real part aspect ratios;
  roster trace fixed; sketch failures are one line; every Manager
  rewrite saves rev_N.md + diff_N.md (root cause of the lost rev:
  optimizer heading "## 3. Process" silently dropped — fixed with
  numeric fallback + dropped_headings reporting, verified live in
  run 20261101-160854).
- **C** Renders are photoreal and mechanism-readable (see dossiers).
  Flow view is council-chosen via flow_choice only; automatic
  force-flow removed. Weakest remaining visuals: figure panel B/D
  fabrication (one invented linkage close-up in run 03, truncated
  captions) — recorded in each REVIEW.md.
- **D** Citations resolved at record time; references.md per run
  (CLI path bug fixed: `hs run` now builds it; prior-art URLs included).
- **E** Largest v1 call 75,592 input tokens; member growth 2.6k→49.8k
  triggered compaction (whiteboard + summarized transcript + evidence
  on demand). Compacted run: max member input 19,867 (halved), more
  objections and a rejection before acceptance — kept. Full comparison
  in run 20261101-160854's REVIEW.md.
- **F** report.html short and human-first; board.html per cycle with
  Manager cards; relative images ≤1600 px; pages are KBs, far under
  2 MB. Page screenshots are BLOCKED.md (every headless engine fails
  in this sandbox; pages verified structurally, all images viewed
  directly).
- **I/J** showcase/index.html + one dossier.html per problem with
  figure path overlays (geometry verified by rasterizing an overlay
  at the correct scale), conformance tables, cost per role. Final
  runs copied into tracked showcase/ (49 MB, no file >50 MB).

## Known remaining risks
- Label localization can ground a part on the wrong object; new
  IoU guard drops duplicate claims instead of mispointing (run
  20261101-165139 diagnosed the failure; fix committed after).
- Members sometimes cite literature from memory without searching
  (run 02c: no member web_search calls); prior-art check still searches.
- Stochastic provider content-filter 400s now retry (QUESTIONS.md).
- The VLM prompt gradient ran in all three final runs and chose
  fix_mode "full" every time; the local-edit + composite branch is
  covered by unit tests and the earlier rerun machinery, but no real
  run has kept a local edit yet.
