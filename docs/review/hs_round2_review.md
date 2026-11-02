# Hardware Scientist — Round 2 review (2026-11-02)

Reviewed: snapshot of `~/Downloads/MetaHackathon_HardwareScientist_MetaCode` at commit `21f95ea` (2026-11-01 17:38), all v2 runs `runs/20261101-*` and `showcase/`. Five parallel reviewers (visual, Stage A process, gradients/Stage B, code/spec, HTML pages rendered in Chromium) plus direct checks. Read-only; nothing was written to Muse's folder.

Finals: 01 = `20261101-154944` (Stage B rerun of the v1 solution), 02 = `20261101-165746`, 03 = `20261101-161405`. Round 2 spend $7.14.

---

## 1. Verdict in one paragraph

Round 2 produced photoreal-looking panel A images and real per-region critique, but most of the new self-improvement machinery is inert or claims more than happened. S2 never fired in 16 designer evaluations; the "routed back to Stage A" runs were S1 exhaustion that the report calls a design flaw. Members made zero searches (0 of 119 evidence items), so every literature citation is from memory. Five of six meetings never formed a proposal; both Stage A rejections were the code rule (cap + an open blocking objection raised by the Manager), not the Evaluator. The Manager's rewrite for 03 was silently lost; the 02 rewrite wrote the answer's numbers into the role text and told members to stop blocking. Roster, tools and protocol did not evolve, so the "the council emerges" claim is not supported yet. The code is small (6.5k lines) and the happy path works; the fix is mostly deletion plus about ten small fixes, not more features.

## 2. Verified facts (checked directly, not only by reviewers)

| Claim | Evidence |
|---|---|
| S2 never fired | `"s2_flaw": true` in 0 of 16 `eval.json`; 0 of 52 regions have source = schematic |
| No member searches | 0 evidence items with `tool: web_search` in all v2 iterations |
| Flow view is a no-op | `final/flow.png` md5 = `panel_A.png` md5 (02); `figure.py` crash "'int' object has no attribute 'append'" |
| `new_tool` cannot be called | absent from `TOOL_SCHEMAS` (`stage_a/tools.py:12–40`) |
| Report misstates S1 exhaustion | `report.py:129`: "The picture showed a design flaw, so the concept went back to the council." |
| Consensus recorded with an open blocking objection | 03 iter_01 `closure.json`: consensus, `open_blocking: ["O4"]` (Manager raised O4 after the votes; `meeting.py:208–215`) |
| Label fallback is a keyword parse | `designer_eval.py:32` searches free text for "wrong", "misspell"…; 5 of 8 hits were false |
| Panel B prompt uses a raw part id | `figure.py:124` `f"close-up of {spec.critical_part_id} and its neighbours"` → 03 "Neighbouring Mass 1/2… pivots" |
| Showcase drops sketches | `showcase_build.py:80` keeps only schematic/render/annotated/local_/edited_ PNGs → 11 broken sketch images on boards |
| Lessons polluted | 22 lessons, 19 about pipeline mechanics (S1, cap, retry, labels), 3 exact duplicates; all fed to every member as §6 |

## 3. Findings by area

### 3.1 Final figures (visual)
- **01 hand truck:** photoreal, on stairs, labels right, but the mechanism cannot climb as drawn: "twin tri-stars" are two half-stars in one plane forming a rigid bogie; clutch axis perpendicular to its disc; scale bar implies 43 mm wheels (spec 100 mm). The Evaluator passed all of it.
- **02 cold room:** best of the three; the only run where regions led to real fixes across rounds 0→2 (missing PV modules, MPPT, wash slab). Remaining: ice-bank leader on the evaporator, MPPT leader to the ground, ~13 crates for 50, door ~1.2 m by the scale bar, flow view silently identical to panel A.
- **03 footbridge:** an infographic, not a scene: cross-girder drawn lengthwise, deck broken by a floating segment, hatch in mid-air, horizontal motion arrow for a vertical mode. Two strings the prompt's `must_not` forbade ("SHS 200x200x8 mm", "320 mm compression travel") are in the final; round 1 passed what round 0 rejected. Panel B is fabricated.
- **Mechanism sketch** is still a box graph: same open circle at every joint, no ground/stair/deck, no axes or real proportions. S1 can only catch missing parts or wrong labels; orientation and topology errors pass. Sketch colours and pin circles leak into renders (pins became "pivots").
- **Panels B/C/D:** B invented (03) or a crop with cut labels; C two boxes or nonsense ("instrument: mu 0.25-0.6"); D steps all failed their light check and still ship, captions cut, schematic colours leak.

### 3.2 Stage A process
- **Speaking rule is cosmetic.** 0 bare ids, but 23/96 member turns cut mid-sentence at 250 words (truncation runs after the turn check), 9/24 Manager turns over 250 words, members in 02 address non-existent "Sam"/"Maya", and the fill-in template invents attributions ("Council Whiteboard, 2026", "Coulomb, 1785"). Turn check: 96 calls, $0.39, 0 retries.
- **Manager in the room works partly.** It names uncomputed quantities and assigns members (4 of 5 answered in 02). But it repeats unanswered requests, re-asks answered ones (board shows only the last line of evidence; `read_evidence` failed 8 times with an empty id), states positions, and its blocking objections act as a veto.
- **Evidence:** 0 searches; 4 duplicate calculations; one phantom number feeding E15; 36/96 member turns produced no board action; 28 failed vote ops ("no proposal").
- **No proposals:** 5 of 6 meetings never formed one; nobody is told to integrate. 02 was accepted with no proposal, no votes, cap closure and 5 open objections.
- **Evaluator:** specific, re-derives arithmetic, but `evidence_requests` empty in all 7 verdicts; checks consistency, not regime. Missed: 03 uncontrolled baseline 17.5 m/s² (1.8 g, unphysical), peak 0.96–0.97 m/s² vs reported 0.74 (evaluated only at ω1), modal mass halved without evidence; 02 E18 3.75 vs 3.0 kWh, battery 11.25 vs 11.52 kWh, canopy wind (~285 kgf/post) ignored.
- **Emergence not supported:** rosters differ only because rev 0 is regenerated per run; no within-run roster/tool/protocol change; `tools/` empty; 0 `new_tool` calls.
- **Compaction:** the 19,867-token figure is a single Manager call (likely search payload); typical member calls 4–8k; the 39,439 baseline is not reproducible from the snapshot; no uncompacted control in v2. Older speech is dropped, not summarized.

### 3.3 Gradients and Stage B loop
- **Stage B is a targeted re-roll, not a closed loop.** The VLM prompt gradient often names the exact sentence that caused a fault (good), but each round is judged from scratch: earlier regions are never re-checked, `EvalRegion.fixed` is never set, new faults appear every round, and a flagged fault can come back and pass (03 "320 mm").
- **fix_mode "full" 10 of 11.** One global flag + "full when the fix spans several parts" + 2–8 regions per critique makes local unreachable. Local ran once (165139 r0), two edits, both correctly reverted. Box coordinates are on the padded `annotated.png`, the composite on `render.png`; the rerun path never carries a kept edit.
- **Labels image-drawn in 15/16 rounds;** 8 of 13 failed rounds were label faults.
- **Stage A gradient: content partly real, plumbing loses it.** Agenda never written into §4; saved `rewrite.json` ≠ applied rewrite (re-ask outputs not saved, `manager.py:128–140`); 03 rewrite discarded because `_canonical` mapped "## 3. Criteria" to "## 5. Criteria" and the guard reverted all; `diagnosis.json` = `gradient_prompt.json`. Worst unapplied rewrite: "reference companion girder check as done and vote ready" — that check is the accepted concept's open question. The gradient is teaching the council to suppress objections.
- **flow_choice** is written by the Secretary; no meeting ever discussed it.

### 3.4 Code and spec
- Spec body still says "clean technical illustration on white" / "no text" (spec lines 15, 219; AGENTS.md:12); writer system prompt still says "a technical illustration"; all 16 prompts open with "Light-background … product-style illustration", so use context is never requested.
- Code burns margins (+640 px per side), panel letter, scale bar and footer into renders; the designer eval then reads them as labels.
- Two copies of the Stage B loop (`controller.py`, `stage_b_rerun.py`) already drifted; `cli._run_with_dir` duplicates `Controller.run`.
- Dead or rubric-like: `Localization.confidence`, `RequirementCheck`/`stage_at_fault`, `EvalRegion.fixed`, two-state schematic, `SKETCH_SINGLE_REQUEST`, `_old_report_html`, base64 compare/showcase pages.
- Cost attribution: Manager in-room turns billed as `member`; searches not counted (invisible to the cost cap).
- Lessons dedupe broken (compares lines with the `[date, run]` suffix); lessons path is relative to the working directory.

### 3.5 HTML deliverables (first real browser render)
- `report.html` (02, 03): demo-ready after small fixes.
- `index.html`: small fixes + content: "The problem" shows the title only (`_prompt_text` misses the `statement` key); mechanism sentences are code soup ("CSK30… 38.5Nm/405N"); pipeline jargon in evolution lines.
- `dossier.html`: path-overlay text is scripted (same sentences every run), "Times exercised" counts those sentences; badge 1 hidden, Stage B steps 1 and 3 missing on Fig. 1, base figure at 15 % opacity; conformance table reads as a scoreboard of raw ids. The 01 dossier invents a meeting that never ran ("rev_000 to rev_-01").
- `board.html`: transcript wall (03: 19,188 px, 11.8k words), duplicated lead sentence per card, raw tool output (`1.8627450980392155`, Python errors), duplicate concept cards, all sketches broken. Not the `board_mock`.
- References: only "prior-art check — URL", no author/title/year; cited sources missing. Reasons cut mid-word (`[:180]`, `[:300]`).

## 4. Does Round 3 (draft items 0–11) cure these?

| Item | Verdict |
|---|---|
| 0 No-scoring audit | **Yes, do first.** Remove confidence, RequirementCheck, conformance counts, turn check, keyword label parse. |
| 1 Writer style root cause | **Yes, needed but incomplete.** Must also edit spec lines 15/219, AGENTS.md, writer system prompt, and stop burning margins/footers into renders; must_not lists must not quote forbidden strings (they get drawn). |
| 2 SAM 3.1 | **Defer.** SAM 3.1 is on the Meta Model API (text-prompt → masks, via Responses API, model `sam-3.1`), so it is feasible, but it does not hit the root causes: the sketch has no geometry, and there is no cross-round re-check. Mask composite serves a local-edit path that never succeeded. |
| 3 Backward chain | **Useful after plumbing fixes** (save every optimizer output, section-wise guard, agenda into §4, tell step 1 when rejection came from the code rule). Add: no design numbers in Roles; never instruct members to drop an objection. |
| 4 Delta updates | **Defer.** SolutionPrompt schema is read by Stage B, report and rerun; high break risk for the time left. |
| 5 knowledge/ | **Minimal version only:** fix dedupe; process lessons go to Manager/optimizer only, not members. Persistent tools are meaningless until `new_tool` is callable. |
| 6 Progress record | **Only useful as a judge input:** pass previous regions to the next designer evaluation ("fixed? regressed?"). As a display strip it fixes nothing. |
| 7 SIMPLIFY.md | **Yes, and delete, not just list.** |
| 8 References | **Blocked by zero searches.** Fix the search→evidence path first. |
| 9 Budget $15, reruns 01/03 | OK. 01 needs a real Stage A meeting for the demo or must be excluded. |
| 10 Blinded comparison | Drop for this deadline. |
| 11 Manager authority | One line; decide together with "Manager objections advisory". |

## 5. Problems no Round 3 item covers (fixes, not new architecture)

1. **Search produces no evidence.** Evidence path only reads `url_citation` annotations; searches unlogged. Fix the web_search_call → evidence path, count searches, allow a citation only with search evidence; remove the "according to <author, year>" slot from the speaking template otherwise.
2. **No proposal ever forms.** Protocol must name who integrates (e.g. the member with most open concepts, or the Secretary drafts v1 after cycle 2); re-check consensus after the Manager turn; Evaluator should not accept a meeting with no proposal.
3. **Manager veto via blocking objections** (owner decision).
4. **S2 dead and S1 exhaustion mislabeled.** Separate `s1_exhausted` outcome with honest wording; designer prompt: "expected" must quote what the sketch shows; if the sketch is silent, source = schematic (a sketch fix, not a design flaw).
5. **No cross-round verification** (see item 6 above).
6. **Mechanism sketch has no geometry** — the real bottleneck of S1.
7. **Panels B/D:** drop the generated close-up (crop only) or fix the prompt; do not ship steps that failed their check.
8. **Flow view crash** (one-line fix) + a protocol sentence so the council actually decides it.
9. **Showcase bugs:** sketch copy filter, `statement` key, `../board.html` link, sentence-boundary truncation, 01 invented meeting.
10. **board.html** needs to be rebuilt toward `board_mock` (or simplified: one card per turn, summary only, details collapsed).
11. **Evaluator regime check:** compare key numbers with everyday scales (e.g. accelerations in g, people for scale) and use `evidence_requests`.
12. **Speaking rule:** re-ask on word count instead of truncating; check Manager turns too.
13. **Lessons:** purge pipeline rules; fix dedupe.

## 6. Constraints that are hurting the system

- Cap + open blocking objection → automatic reject (`evaluator.py:54`), combined with Manager blocking objections.
- 250-word silent truncation.
- All lessons fed to every member as §6.
- Every meeting runs to the 4-cycle cap (no proposal → no consensus); cost scales with it.
- Member-count guard 3–MAX_MEMBERS (item 11).
- `must_not` lists that quote forbidden strings (negative-prompt leak).
- Muse's sandbox cannot screenshot pages → Claude must check pages.
- Coding model is now muse-spark-1.3 (weaker); ~2.5 days to the 2026-11-04 21:00 ET deadline.

## 7. Candidate removals (owner decision)

Local edit + composite + progress check (0 kept edits); conformance table; turn check; two-state schematic; generated panel B close-up; flow view (or fix); `RequirementCheck`, `Localization.confidence`, `EvalRegion.fixed`; duplicate `diagnosis.json`; second Stage B loop and `cli._run_with_dir`; base64 compare/showcase pages; `_old_report_html`.

## 8. What works and must not break

- Region critique → VLM prompt gradient naming the faulty sentence (02 fixed 5 faults across rounds).
- The Manager's named, quantity-specific requests in the room.
- Id-glossed, evidence-first speech (0 bare ids).
- Prior-art step with real URLs; Evaluator's arithmetic re-derivation.
- Photoreal panel A on 01 and 02; short report.html.

## 9. Corrections to earlier documents

- `HS_context_after_round2.md` §16 describes the original round-2 message ($30, open showcase). The message actually sent was the expanded version (A1–A6, B7–B14, C–J, $40, never open pages); Muse's output (dossiers, flow_choice, turn check, speaking rule) confirms it.
- Muse's round-2 summary overstates: "lost-revision root cause fixed" (03 rewrite still lost), "flow views only from council's flow_choice" (never discussed; view crashed), "speaking rule verified" (cosmetic), "citations resolved" (0 searches), "example 03 routed back" (S1 exhaustion, not S2), "compaction gave stronger scrutiny" (rejection came from the Manager flag + code rule). Two REVIEW.md files misstate their runs (01 round count; 03 label fallback and Manager credit).
- New figures from the other session (`fig_architecture`, SAM loop, debate vs HS) show Round 3 targets as if current (knowledge/, SAM part map, insights, tools) and keep v1 errors (Evaluator + Manager merged, no Manager seat, 2–5 cycles, "topology + size class" schematic, no VLM prompt gradient in the loop). The SAM loop figure omits the full re-render path that ran 10 of 11 times.
