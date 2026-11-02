# SUMMARY.md — Hardware Scientist, round 4 (Claude Code, 2026-11-03)

Goal of round 4 (owner): fit the two architecture figures, run the critical loops with real tools, make it presentable.
Every statement points to a file. Round 3 follows below, then the earlier rounds.

## Where to look

- **Showcase:** `showcase/index.html`; per problem `report.html`, `board.html` (now with the whiteboard picture),
  `dossier.html`, `REVIEW.md`. Screens: `docs/screens/r4_*.png`.
- **Final runs (round-4 code, real API, run fresh in order 01 → 02 → 03 so knowledge carries over):**
  | Problem | Run | Outcome | Cost (ledger) |
  |---|---|---|---|
  | 01 stair-climbing hand truck | `runs/20261102-105608_stair-climbing-hand-truck-for-parcel-cou` | consensus in cycle 4, accepted at meeting 1, picture faithful in round 1 | $1.9362 |
  | 02 off-grid solar cold room | `runs/20261102-112524_off-grid-solar-powered-cold-storage-for-` | consensus in cycle 4, accepted at meeting 1, picture faithful in round 1 | $2.2661 |
  | 03 footbridge vibration retrofit | `runs/20261102-121628_vibration-retrofit-for-a-lively-pedestri` | consensus in cycle 4, accepted at meeting 1, picture faithful in round 1 | $1.6361 |
- **Test run kept:** `runs/20261102-104641_…` (Stage B redraw of a round-3 solution, $0.3269) — found the critic
  passing a picture it had itself faulted, SAM missing two-word phrases, crossing labels.
- **Ledger:** $20.85 of the $55 cap after round 4 (round 4 spent $6.25: the test run, the three runs, a content-filter
  reproduction $0.08). `hs budget` lists every run.

## Fit to the owner's figures — what ran in the round-4 runs

Fig. 1 (`docs/fig1_architecture.svg`)
- **Master prompt rev 0 from knowledge/** — fired in all three runs; `knowledge_in.json` records what each inherited
  (run 03: lessons L1–L14 and the insight files of runs 01 and 02).
- **Council + Manager on the whiteboard with tools** — fired: 56–67 evidence items per run, 36–42 search hits, 17–25
  calculations, sketches; the Manager spoke each cycle. Run 01's meeting caught its own negative tipping margin
  (simulation E58) and fixed it (E60) before voting (transcript.md lines 75, 88).
- **Evaluator: written review, constraint by constraint** — fired: `verdict.json` constraint_review in all three runs, in
  prose with the deciding numbers; no constraint was relaxed (none needed it).
- **Fail → Manager two-step gradient → section rewrite → re-meeting** — **did not fire in round 4**: all three runs were
  accepted at meeting 1. Code and tests are in place; the last real rewrite is round-3 smoke run 022817.
- **Council archive** — fired (archive.jsonl, status accepted).
- **knowledge/ at the end of a problem** — fired: `knowledge/insights/<run>.md` for all three runs (4–5 findings each,
  with evidence ids), lessons L11–L14 added, 16 "used in run …" notes under existing lessons (run 01: 5, run 02: 4, run 03: 7).
  No member called search_knowledge in runs 02 or 03 (the inherited findings were about other domains). No member
  wrote a new tool, so knowledge/tools/ is empty.
- **S1 exhausted → Manager "could not be drawn"** — code and test in place; did not occur (every picture passed in round 1).

Fig. 2 (`docs/fig2_visualization_pipeline.svg`)
- **1 Concept sketch from the council's sketches** — fired in runs 01 and 03 (`stage_b/attempt_00/concept_sketch.png`,
  checked); in run 02 blocked by Meta's content filter after the number-free retry. Reproduced: each prompt part passes
  alone, the combination is blocked; a plainer second wording passed and is now built in (not yet in a full run).
- **2 Render with image-model callouts** — fired in all three; the image model ignored "no numbers" in its callouts
  (run 02) and the critic flagged each one.
- **3 Part map · SAM masks and contacts** — fired: masks decoded with meta-sam-parser, filled in each part's colour
  (`sam_overlay.png`); found 5/7, 7/11, 4/7 parts. The head-noun retry found "strap" in run 01. SAM still misses or
  confuses parts (run 03: the mass was segmented as "metal cover").
- **4 Designer evaluation S1/S2 with keep/revert** — fired, round 1 pass in all three. New guard: a part fault the critic
  lists means not faithful (from the test run). Local/full fix and revert did not run (no second round needed).
- **Checks: SAM + judges on callouts, code labels as fallback** — fired in all three: image callouts judged wrong
  (3, 4, 5 of them) → removed by image edit → code labels → code labels checked again, wrong ones removed (1, 3, 3).
- **Figure: panels A–D** — A in all; B in run 01 only (02: critical part fills the picture; 03: not located); C in 01
  and 02; D 4/3/4 steps.

## What round 4 changed (commits 3656ab4 … on main; JOURNAL.md has each step)
- P1: Evaluator constraint review (prose); S1 exhausted → Manager as a drawing failure; whiteboard errors name valid ids.
- P2: knowledge/ — lessons with ids and use notes, insights per problem with search_knowledge, carried tools, retirement.
- P3: SAM masks, image-model callouts with checks, concept sketch from the council's sketches, panel D redraw.
- P3 fixes from the test run: critic consistency guard; SAM head-noun retry; side-column labels that never cover their
  part or cross; fallback labels checked; panel B from the render without callouts.
- P4: whiteboard picture per meeting (function columns, sticky notes, calculations, objections, pinned sketches,
  proposal with votes) on board.html and in the dossier; knowledge section in the dossier; figure layout with the
  making steps full width; showcase strip council sketch → concept sketch → SAM → critical part → making.
- P5 fixes: visible mask fills; concept sketch plain re-word after a filter block; making steps at the device's real
  size (bench / shop floor / site) — added after runs 02 and 03 started, not yet in a full run.

## Still not working / open
- The reject → rewrite → re-meeting loop has not run on round-4 code; it needs a problem the Evaluator rejects.
- Panel A of run 03 keeps only two labels after the checks; SAM misses or confuses parts in every run.
- Run 03's render hangs the damper far lower than the council's sketches; the concept sketch exaggerated it and the critic,
  comparing with the concept sketch, did not flag it.
- Making steps of runs 02 and 03 show large structures on a workbench (fixed in code afterwards).
- new_tool never used by a member; knowledge/tools/ empty; search_knowledge never called.
- Content filter: unpredictable on combined wording; handled by re-wording, not avoidable.

---

# Round 3 (Claude Code, 2026-11-02)

Every statement below points to a file. Earlier rounds (v1, v2) are kept at the end of this file.

## Where to look

- **Showcase:** `showcase/index.html` (three problems), each with `report.html`, `board.html`, `dossier.html`, `REVIEW.md`.
- **Final runs (round-3 code, real API):**
  | Problem | Run | Outcome | Cost (cost.json) |
  |---|---|---|---|
  | 01 stair-climbing hand truck | `runs/20261102-033230_stair-climbing-hand-truck-for-parcel-cou` | consensus in cycle 4, accepted at meeting 1, picture faithful in round 1 | $1.7557 |
  | 02 off-grid solar cold room | `runs/20261102-053545_off-grid-solar-powered-cold-storage-for-` | consensus in cycle 4, accepted at meeting 1, picture faithful in round 1 | $1.9229 |
  | 03 footbridge vibration retrofit | `runs/20261102-082123_vibration-retrofit-for-a-lively-pedestri` | cycle cap (one blocking objection open), accepted by the Evaluator in writing, picture faithful in round 1 | $1.4227 |
- **Runs kept as evidence of fixes** (each with REVIEW.md): 025924 (01, tri-star not drawn), 032624 (01 Stage B redraw, C14),
  035951 (02 crash), 042726 (02 hidden NOT-ready vote, skipped SAM findings), 050118 (02 s1_exhausted), plus the smoke
  runs 022817 (Stage A) and 024314 (Stage B).
- **Screenshots:** `docs/screens/` (index cards, SAM picture, whiteboard, figure).
- **Reviews:** `docs/review/code_review_cc.md` (full code review), `docs/review/hs_round2_review.md`.

## Budget (item 0)

Ledger total **$14.6026 of the $55 cap** (`hs budget`, `budget/ledger.jsonl`), $40.40 left; the dashboard showed $67 at
the start. Per run: access check $0.0001, PHASE 1 check $0.0217, SAM probe $0.0050, search probe $0.0107, filter probe
$0.0389; runs 022817 $1.0522, 024314 $0.5735, 025924 $1.7684, 032624 $0.2018, 033230 $1.7681, 035951 $1.7908,
042726 $1.8584, 050118 $2.1405, 053545 $1.9498, 082123 $1.4227 (ledger values include the later label checks).
Please compare with the Meta dashboard.

## Item by item — did it fire in a real run, did it change anything, what still does not work

**0 Budget ledger.** Fired in every real call (ledger has every entry with run id, role, tokens, searches, images,
SAM calls). Pre-call worst-case estimate; BudgetExceeded no longer swallowed (behaviour test). HTTP 402 → clean stop:
never triggered (no billing error happened), covered by tests only.

**A1 Outcome labels.** Fired: run 050118 ended `s1_exhausted` ("could not be drawn faithfully after 3 rounds",
archive status `could_not_draw`, no figure, nothing sent to Stage A — trace.md). Report wording per outcome
(report.html). S2 → Stage A: fired once in smoke 024314 (round 2) before the R4 rule; since the rule (a flaw counts
only on a faithful render or a sketch-traced region) no real S2 return happened.

**A2 Pages from facts.** Dossier sentences, index cards and the Stage B redraw pages are built from run files
(`showcase/*/dossier.html`; 032624 report says "no council meeting ran in this run"). Conformance table replaced by
two prose sentences. Verified by tests and by reading the rendered pages.

**A3 Manager rewrites never lost.** Fired in smoke 022817: `rewrite.json`, `manager_edit.json`, rev_001 saved, the
agenda written into §4 (`master_prompt/rev_001.md`). Found there: the optimizer wrote `### <member>` sections, which
were dropped — fixed (they now edit that member's block), unit-tested, **not yet exercised in a real run** (all final
runs were accepted at meeting 1, so no rewrite happened).

**A4 No cap code rule; consensus after the Manager.** Fired: runs 042726 and 082123 closed at the cycle cap and the
Evaluator decided in writing (verdict.json). Found in 042726: the closure facts listed only ready votes, so a reasoned
NOT-ready vote was invisible — fixed (all votes with reasons; 053545's verdict cites them).

**A5 Proposals form.** Fired: every final run formed a proposal (v1 or v2) with votes (whiteboard.json); v2 had none
in 5 of 6 meetings.

**A6 No cutting of speech.** Fired: 7–9 shorten re-asks per final run (whiteboard_history.jsonl, `shorten_reask`);
no turn cut; LLM turn check removed.

**A7 Silent no-ops.** new_tool now callable and registered tools are sent — **no member called it in any final run**
(no `tools/*.json`). read_evidence: 2 ok, 1 failure in 082123. Whiteboard op failures remain common (12 of 36 ops
failed in 033230, mostly missing ids). Flow view removed (it never worked). One Stage B loop; Manager and progress
check billed separately; searches counted; lessons dedupe; showcase sketches/statement/link fixed.

**Item 16 SAM smoke test.** Done: call shape, phrase sensitivity, $2.50/1000 images (QUESTIONS.md, spec §14.10).
Masks cannot be decoded (Meta's `meta-sam-parser` install was refused by the session's permission system —
BLOCKED.md); measurements use boxes.

**B8 Search and read sources.** Fired: 36, 45, 27 search sources in the final runs, cited in speech by evidence id and
title (transcript.md). Snippets are mostly empty, so "the passage read" is often unavailable. References carry
site, title, year when stated, URL.

**B9 Understandable speech.** Fired: plain sentences, roster names; failed calculations shown in plain words on
pages. Some turns are still dense with numbers.

**B10 Physical sanity.** Fired: the Evaluator compares with g and everyday scales (082123: 1.75 m/s² = 0.18 g;
v2 had reported 17.5 m/s² for this problem). No evidence_requests were issued in the final runs.

**B11 Manager as coach.** Prompt and optimizer framing changed; member-block diffs shown in reports. Fired only in
smoke 022817 (where the role edits were lost, then fixed). Not exercised since.

**B12 Knowledge.** Partly: lessons.md cleaned (pipeline lessons and duplicates removed), lessons go to the Manager
and optimizer only. **knowledge/insights and knowledge/tools carry-over were not built.**

**B13 Backward chain.** Fired in smoke 022817: gradient_output.json and gradient_prompt.json with 8 feedback
decisions (apply/defer/reject); chain text built by code (unit-tested).

**C14 Sketch method.** Compared on problem 01 (025924 vs 032624, REVIEW.md of 032624): the council's own sketches as
extra references made the tri-star cluster appear as designed; chosen for all runs.

**C15 Writer style.** Fired: all final renders are photoreal in use context with no text in the render.

**C16 SAM part map.** Fired in all final runs: part_map.json, sam.json, sam_overlay.png per round; SAM boxes place
code labels; a label check removed wrong labels (01: worm drive; 02: "PU box"; 03: friction clamps). SAM misses parts
regularly (cooler, battery, clamps) and sometimes confuses parts (02: crates as "insulated box").

**C17 Closed Stage B loop.** Fired: 024314 kept/kept/reverted; 025924 round 1 marked both earlier faults fixed;
050118 reverted rounds that fixed nothing. In the final runs round 1 passed, so the loop had nothing to correct.

**C18 Deviations.** Fired: every final eval lists one deviation per segmenter finding (unnoticed = [] in sam_use.json).
The completeness re-ask was not needed in the final runs. 050118 showed the critic failing S1 on exact counts; the
critic now notes such counts as deviations.

**C19 Panels.** Panel B is a crop of the render (or omitted when the critical part fills the picture); panel C
omitted when no chain was recorded (01); failed fabrication steps are not shipped (01: 3 of 4 failed; 02: 2 shown
after a plain-word re-check; 03: 1 of 4 shown). Content-filter handling: QUESTIONS.md.

**D20 Remove dead code.** Done; SIMPLIFY.md lists 8 further candidates for your decision.

**D21 Board.** Rebuilt; rendered and viewed for all three runs.

**D22 Pages.** Plain mechanism sentences; references folded; one overlay per stage; dossier has the TextGrad chain per
meeting (in the final runs: "accepted at this meeting, so no gradient step ran") and the picture-round strip with the
SAM picture.

**D23 Related work.** README, nine works, each page fetched with its arXiv id.

**E24 Runs.** 01 → 02 → 03 run fresh; 01 and 02 were re-run after fixes (kept runs listed above).

**E25 Self-audit.** All ten showcase pages rendered headless at 1440 px and every slice viewed (index, 3 reports,
3 boards, 3 dossiers); fixes from the audit are in the last commits. Claims in this file and the REVIEW.md files
were re-checked against the run files; two numbers I had written wrongly were corrected (journal ledger figure,
032624 cost).

## Implemented flow versus the owner's figures (R5)

- **fig1 sends "S1 exhausted (reported as such)" back to Stage A**; the implementation sends nothing to the design on
  S1 exhaustion (brief A1/R4). `docs/fig1_architecture-1.svg` ("back to A only on S2") matches the implementation.
- **knowledge/ (lessons · insights · tools)** in both figures: only lessons exist.
- **Part map · SAM (masks · part connections)**: boxes only; connections are box contacts, not mask contacts.
- **fig2 VLM writer "callouts for 4–7 parts"**: the render carries no callouts; code draws all labels (item 16a).
- **Mechanism sketch "real geometry, joints, motion, workpiece, use context"**: the code sketch is still boxes; the
  council's own sketches are added as references, which is what made geometry reach the render.
- **"S1 fail: local or full fix, keep/revert"**: implemented; the local fix composites a feathered box (no masks) and
  never ran in the final runs.
- **Controller "dossier(run)" at the end of a problem**: dossiers are built by `hs showcase-build`, not per run.
- **Panel B "close-up + scale bar"**: a crop of the passing render, by the brief (C19).
- Evaluator and Manager are separate roles, as drawn.

## Still not working / open

- Coach path (B11/B13) and member-block rewrites have not run in a real run since their fixes.
- new_tool never used; whiteboard ops often fail on missing ids.
- SAM masks blocked (needs your permission to install `meta-sam-parser`).
- knowledge/insights and knowledge/tools not built.
- Provider content filter blocks some fabrication-step checks; handled, not avoidable.
- Code labels are small and can overlap (03: "Coil springs" and "Lock pin").

---

# Earlier rounds — v1 hand-off (AUTOPILOT §6)

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
