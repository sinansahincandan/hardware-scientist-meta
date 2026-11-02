# Hardware Scientist — full code review (Claude Code, round 3, PHASE 2)

Reviewed: commit `ed910f6` (2026-11-02), i.e. the Muse Code round-2 code (`round2-final` = `21f95ea`) plus
Claude's spend ledger, `sam_segment` and the PHASE 1 check script. Read in full: every file in `src/hs/`,
`tests/`, `scripts/`, `pyproject.toml`, `demo.sh`, `HARDWARE_SCIENTIST_SPEC.md`, `AGENTS.md`, `AUTOPILOT.md`,
`SPEC_CHANGES.md`, `CLAUDE.md`, `docs/review/hs_round2_review.md`, and the text of
`docs/fig1_architecture.svg` and `docs/fig2_visualization_pipeline.svg`. No code was changed in this phase.
Line numbers refer to `ed910f6`.

---

## 1. Module map

**Entry and plumbing**
- `cli.py` — the `hs` command (run, examples, feedback, show, report, board, compare, showcase, showcase-build,
  stageb, spend). Builds a `MetaClient` or `FakeClient`. `_cmd_run` pre-creates the run folder and then calls
  its own copy of the controller's exit path (`_run_with_dir`) instead of `Controller.run`.
- `config.py` — per-role model/effort/token table, caps, price table, the default meeting protocol text,
  the fixed criteria, the spend-cap constants.
- `client.py` — `MetaClient`: every real model call (Responses API via the OpenAI SDK pointed at
  `api.meta.ai/v1`; image edits via `requests`; SAM via a streamed Responses call). Retries, truncation
  re-ask, structured-output helper, `CostLog` (per-run `cost.json`) and `SpendLedger` (cross-run cap).
- `fake_client.py` — scripted stand-in for every call, synthetic usage; used by all tests and `--fake`.
- `schemas.py` — pydantic models for every structured output plus the strict-schema post-processor.
- `sandbox.py` + `launcher.py` — run LLM-written Python in a subprocess with an import allow-list and
  CPU/memory/file-size limits.

**Stage A**
- `master_prompt.py` — the Markdown master prompt: rev 0 call, heading split, member blocks, rewrite with
  guards and shrink check, section revert, `rev_N.md`/`diff_N.md`.
- `stage_a/meeting.py` — `Meeting.run()`: cycles of member turns, the Manager's end-of-cycle turn,
  consensus check, vote-only round, closure; the LLM turn check; `Secretary.synthesize()`.
- `stage_a/council.py` — `run_member_turn()`: one member's Responses tool loop (whiteboard ops, calc,
  simulate, sketch, vetted_calc, new_tool, web search citations → evidence). Also used for the Manager's turn.
- `stage_a/tools.py` — tool schemas sent to the model and `ToolRunner` (runs tools, posts evidence files).
- `stage_a/calculators.py` — the seven vetted calculators.
- `stage_a/whiteboard.py` — board state, op validation, consensus rule, Markdown rendering, history log.
- `stage_a/evaluator.py` — prior-art search (free text + web_search) and the structured `Verdict`.
- `stage_a/manager.py` — inspirations pick, output gradient, prompt gradient, Manager tool proposals,
  optimizer rewrite with guard/shrink re-asks.
- `stage_a/archive.py` — `CouncilArchive` (archive.jsonl).
- `lessons.py` — load/filter/append `lessons.md`, `hs feedback`.

**Stage B and pages**
- `stage_b/schematic.py` — `SchematicSpec` call + checks; deterministic matplotlib "mechanism sketch"
  (`schematic.png`, `schematic_labeled.png`, `schematic_two_states.png`).
- `stage_b/vlm_prompt.py` — VLM prompt writer (structured `VLMPrompt`, label mode image/code).
- `stage_b/image_model.py` — joins prompt + must_not and calls `client.image_edit`.
- `stage_b/annotate.py` — localization call, conflicting-box filter, code labels in white side margins,
  load arrows, scale bar, panel letter, footer.
- `stage_b/designer_eval.py` — designer evaluation call, `decide()`, `feedback_text()`, `label_failed()`.
- `stage_b/prompt_gradient.py` — VLM prompt gradient call, progress check call, `composite_region()`.
- `stage_b/image_archive.py` — image_archive.jsonl.
- `stage_b/figure.py` — panels A–D, flow view, rationale.md, `recompose()`.
- `stage_b_rerun.py` — a second copy of the Stage B loop that starts from an accepted solution (`hs stageb`).
- `report.py` — report.html, compare page, the old base64 showcase page, and `_old_report_html` (dead).
- `board.py` — board.html (meeting replay).
- `showcase_build.py` — `showcase/` folder: copies runs, writes index.html and per-run dossier.html with
  architecture overlays and the conformance table.

**Real call flow of one `hs run examples/01_stair_cart.json`**
`cli._cmd_run` → `make_run_dir` → `MetaClient(run_dir)` → `cli._run_with_dir` → `Controller._loop`:
1. `load_lessons()` (reads `./lessons.md`) → `MasterPrompt.rev0` (1–2 free-text calls) → `rev_000.md`.
2. Per iteration k (≤ 8): `Manager.inspirations` (0–1 call) → `Meeting.run`: per cycle (≤ 4) each member
   `_run_real_turn` → `run_member_turn` (≤ 16 Responses requests) + one `turn_check` call (+ one whole re-turn
   on failure); then the Manager turn (`run_member_turn`, billed as `member`); vote-only round = one more full
   turn per member → `Secretary.synthesize` (1 call) → `Evaluator.judge` (prior-art + verdict, 2 calls).
3. Reject → `Manager.edit`: output gradient, prompt gradient, optional tool registration, optimizer
   (+ ≤ 2 re-asks) → next iteration.
4. Accept → `schematic.spec_and_check` (1–2 calls) → per round (≤ 3): render schematic (code), writer (1),
   image edit (1 image), localization (1), designer eval (1); on `s1_retry` the VLM prompt gradient (1) and,
   in local mode, per region one image edit + one localization + one progress check.
5. `s1_pass` → `figure.compose` (close-up ≤ 2 images + light checks, ≤ 5 step images + light checks) →
   `update_lessons` (1 call). Otherwise designer feedback → `Manager.edit` → back to 2.
6. Always: `build_references`, `write_report`, `write_board`. `showcase/` and dossiers are built only by
   the separate `hs showcase-build` command.

---

## 2. Status of every finding in `hs_round2_review.md`

| Round-2 finding | Status | Where now |
|---|---|---|
| S2 never fired; S1 exhaustion reported as design flaw | **Confirmed** | `designer_eval.py:18-20` returns `s2_return` on exhaustion; `feedback_text` :26-28 adds "the concept is probably under-specified"; `controller.py:315-316`, `:327-334` sends it to the Manager; `report.py:129` prints "The picture showed a design flaw" for every `s2_return` |
| Members made zero searches | **Confirmed, root cause found** | `council.py:141-142` breaks out of the loop *before* the citation scan at :200-211, so citations in the final response (the usual place) are never posted; and the PHASE 1 check showed a response with a `web_search_call` but no `url_citation` annotations at all (`runs/meta_check_20261102-014036/check.json`). Evidence `query` is the literal string "member search" (`council.py:208`) |
| Flow view is a no-op / crashes | **Confirmed** | `figure.py:101` `images_used.append` on an int; stops matched by exact lower-case label strings `figure.py:88-90`, so `pts` is usually empty and `flow.png` = panel A |
| `new_tool` cannot be called | **Confirmed** | absent from `TOOL_SCHEMAS` (`tools.py:12-40`); registered tools never added to the request (`council.py:106-108` always sends `TOOL_SCHEMAS`) |
| report.py:129 misstates S1 exhaustion | **Confirmed** | `report.py:128-130` |
| Consensus recorded with an open blocking objection | **Confirmed** | `meeting.py:208-215`: consensus after a member turn sets `closed_by="consensus"` and breaks only the member loop; the Manager turn then runs (:211) and may raise a blocking objection; the re-check at :212 can only set, never clear, consensus |
| Label fallback is a keyword parse | **Confirmed** | `designer_eval.py:32-35`; counted in `controller.py:255-258`, `stage_b_rerun.py:129-130` |
| Panel B prompt uses a raw part id | **Confirmed** | `figure.py:124` |
| Showcase drops sketches | **Confirmed** | `showcase_build.py:78-80` keeps only schematic/render/annotated/local_/edited_ PNGs |
| Lessons polluted, dedupe broken | **Confirmed** | `lessons.py:29-31` keeps the `[date, run]` suffix in existing lines, so a new candidate never reaches ratio 0.8; `lessons.py:19` relative path; full `lessons.md` goes into every member's §6 (`master_prompt.py:144`) |
| 250-word silent truncation | **Confirmed** | `meeting.py:37-39`, applied at :102, :151, :179 |
| LLM turn check (cost, never retried) | **Confirmed** | `meeting.py:121-150` |
| `read_evidence` fails with empty id | **Confirmed** | `whiteboard.py:182-187` reads only `id`; models pass `evidence_ids`/`target_id`; the board shows only the last stdout line of evidence (`tools.py:123`, `:134`) |
| Region boxes on annotated.png, composite on render.png | **Confirmed** | eval sees `annotated.png` (`controller.py:242-243`), which has 2 × `max(300, w/3)` px white margins in code-label mode (`annotate.py:105-109`); `composite_region` maps the same 0–1000 box onto `render.png` (`controller.py:284`); panel B crops the annotated image with render-basis boxes (`figure.py:105-113`) |
| Two Stage B loops drifted; `cli._run_with_dir` duplicates `Controller.run` | **Confirmed** | `controller.py:213-337` vs `stage_b_rerun.py:87-182` (rerun never carries a kept local edit: `current` is discarded after :162); `cli.py:44-77` |
| Manager in-room turns billed as member; searches not counted | **Partly fixed** | searches are now counted from `web_search_call` items (`client.py`, Claude, 2026-11-02); Manager turns still billed `member` (`council.py:106`); progress check billed `designer_eval` (`prompt_gradient.py:44`) |
| Manager rewrite lost (re-ask outputs not saved) | **Confirmed** | `manager.py:127` saves only the first rewrite; `rewrite2`/`rewrite3` (:130-140) are never written |
| `_canonical` maps "## 3. Criteria" to "## 5. Criteria" | **Confirmed** | `master_prompt.py:204-221`: title-word match runs before the number match |
| Agenda never written into §4 | **Confirmed** | only an instruction to the optimizer (`manager.py:123`); no code writes `Gradients.agenda` anywhere |
| `diagnosis.json` = `gradient_prompt.json` | **Confirmed** | `manager.py:89-90` |
| Cap + open blocking objection → reject | **Confirmed** | `evaluator.py:53-56` |
| No proposals form | **Confirmed (cause in prompt text)** | `config.DEFAULT_PROTOCOL` never names who integrates the proposal; the Evaluator is not told whether a proposal formed (`evaluator.py:32-37` passes only `closed_by`) |
| Spec still says "clean technical illustration on white" | **Confirmed** | spec lines 15, 219; `AGENTS.md:12`; writer system prompt `vlm_prompt.py:47`; writer user text "Light background, realistic rendered product-style illustration" `vlm_prompt.py:39` |
| Code burns margins, panel letter, scale bar, footer into the judged image | **Confirmed** | `annotate.py:102-152`; the designer evaluation judges this image |
| Dead/rubric-like code | **Confirmed** | see §5 |
| Pages: scripted dossier sentences, conformance table, "rev_000 to rev_-01", `statement` key, `../board.html`, mid-word cuts | **Confirmed** | `showcase_build.py:172-203` (fixed sentences), :308-325 (conformance table), :220 (`len(revs)-1` = −1 when no revisions), :112-114 (`_prompt_text` misses `statement`), :284 (`../board.html`), `[:180]`/`[:200]`/`[:300]` cuts in `report.py:125,131`, `showcase_build.py:183,306-307,346-347` |
| Mechanism sketch is a box graph | **Confirmed** | `schematic.py:110-218`: rectangles in a grid, one hinge circle at the midpoint of every mechanical edge, a motion arrow drawn on the critical part whether it moves or not (:179-182) |
| Panels D ship after failing their check; captions cut | **Confirmed** | `figure.py:180-182` keeps failed steps; `figure.py:196` keeps 3 wrapped lines; panel C names cut to 2 lines (:52) |
| Flow choice never discussed | **Confirmed** | only the Secretary prompt mentions it (`meeting.py:269-270`) |
| Compaction: older speech dropped, not summarized | **Confirmed** | `council.py:52-69` keeps only the first sentence of older turns, and `since[-8:]` (:82) drops everything older |

Nothing in the round-2 list was wrong.

---

## 3. New defects (not in the round-2 review)

1. **Budget stop is swallowed in three places.** `controller.py:309-311` and `stage_b_rerun.py:164-166` re-raise
   only when the message contains "budget cap" or "hs run cost"; `meeting.py:148-150` only when it contains
   "budget". `BudgetExceeded` says "cost cap … would be exceeded" / "total spend cap …" / "billing error HTTP 402",
   so all three paths swallow it and carry on. Trigger: the cap is crossed inside a VLM gradient, local edit or
   turn check; the run keeps going until another call raises outside these blocks.
2. **Guard second pass can apply a guard-violating rewrite.** `master_prompt.py:243-251`: on the second violation
   it tries reverting one changed section at a time and keeps the candidate if none clears all violations.
   Trigger: two sections each break a guard (e.g. roster count and a fixed criterion) — the candidate is saved as
   the next revision with both violations.
3. **Shrink re-ask can silently drop the rewrite.** `manager.py:135-140` calls `apply_rewrite(rewrite3,
   _shrink_retry=True)` without `_guard_retry`; if `rewrite3` breaks a guard, `apply_rewrite` returns
   `guard_reasked` and nothing is applied, saved, or counted as no-progress. The shrink re-ask also never shows
   the removed lines that spec §3.2 requires.
4. **Reverted sections are used but not saved.** `master_prompt.py:185-194` changes `self.sections` in memory;
   if the following rewrite changes nothing (or is dropped), no revision is saved, so the next meeting runs on a
   prompt that matches no `rev_N.md` file.
5. **Inspirations are chosen blind.** `manager.py:29-33` sends only archive ids and statuses to the picker, never
   the feedback or the solution; `feedback_summary` is cut at 200 characters (:44).
6. **The vote-only round is a full turn.** `meeting.py:219-228` calls `_run_real_turn` (all tools, turn check,
   proposal updates allowed) instead of a vote/raise-objection-only request (spec §4.3).
7. **Final-response citations are never recorded** (`council.py:141-142` before :200) — listed above as the root
   cause of "zero searches".
8. **Sandbox has no filesystem isolation.** `launcher.py` blocks imports but not the `open` builtin, and the
   subprocess runs as the user. LLM-written `calc`/`simulate`/`sketch`/`new_tool` code can read any file the user
   can (for example `~/.zshrc`, which holds `MODEL_API_KEY`) and print it into evidence (written to `runs/` and
   sent back to the model), or write anywhere (only `RLIMIT_FSIZE` applies). No run did this; it is possible.
9. **Sandbox keeps the head of stderr.** `sandbox.py:48-49` keeps the first 4 kB; the real exception line is at
   the end of a long traceback, and `tools.py:149` reports `stderr.splitlines()[-1]` from the cut text.
10. **Secretary invents decisive choices.** `meeting.py:278-283` pads to three with
    "Choice needs Secretary confirmation: <risk>" — text the council never wrote, shown as a decisive choice on
    report.html and index.html.
11. **Stage B rerun fabricates a verdict.** `stage_b_rerun.py:54-56` writes `verdict.json` with `accept: true` and
    copies `whiteboard.md`/`novelty.md`; page builders then narrate a meeting for a run that had none (the 01
    dossier).
12. **Local-mode gradient is lost when no local edit is kept.** `controller.py:272-304`: the gradient diagnosis is
    appended to `s1_diffs` only in the `full` branch; when `local` edits are all reverted, the next writer call
    never sees the diagnosis.
13. **Manager can vote and design.** `whiteboard.apply_op` accepts any action from author "Manager"
    (`whiteboard.py:104-190`); only the instruction text says it must not.
14. **Rev 0 with no roster runs a meeting with no members.** `master_prompt.py:133-138`: if both rev-0 calls miss
    `## 2. Roles`, `roles` is empty, `roster_of` is empty and `meeting.py:198` builds an empty order; only the
    Manager speaks. No guard on rev 0.
15. **Image size is fixed at 1536x1024** (`image_model.py:14`), not the schematic's aspect (spec §5.3).
16. **Schematic geometry does not match the saved PNG.** `schematic.py:149-155` computes boxes on a 1000×625 canvas
    but `savefig(..., bbox_inches="tight")` crops the image; `schematic.json` boxes are offset (used by fake
    localization and the close-up subset).
17. **Duplicate dead line** `meeting.py:196` (order computed twice; the first value is overwritten).

---

## 4. Code deciding what an LLM must decide (owner rules R3/R4)

- `evaluator.py:53-56` — cap closure + open blocking objection forces `accept=False`.
- `designer_eval.py:14-15` — any region with `source == "schematic"` forces `s2_return` even when the critic
  wrote `s2_flaw = false`.
- `designer_eval.py:18-20` + `feedback_text` — S1 exhaustion is turned into a design-flaw return with a fixed
  sentence ("probably under-specified").
- `designer_eval.py:32-35` — keyword parse of free text decides the label fallback.
- `whiteboard.py:96-101` — every Evaluator evidence request is pinned as a *blocking* objection by code.
- `master_prompt.py:73-74` — roster size guard 3..`MAX_MEMBERS` (owner item 11 removes it).
- `manager.py:36-42` — code swaps an inspiration pick for a rejected entry.
- `meeting.py:37-39` — 250-word truncation instead of a re-ask.
- `meeting.py:278-288` — Secretary output padded/overwritten by code.
- `schematic.py:179-182` — a motion arrow on the critical part, decided by code for every design.
- Numeric fields that act as scores: `LocalizedPart.confidence`, `RequirementCheck` (observed/ambiguous/missing
  + `stage_at_fault`), the dossier conformance "Times exercised" counts.

---

## 5. Dead or duplicated code, features that cannot fire, tests that test nothing real

- Cannot fire: `new_tool` (not in schemas), member-registered tools (never injected), the flow view (crash +
  label-string matching), `EvalRegion.fixed` (never set), `RequirementCheck` (requested, never read),
  `Localization.confidence` (never read), `schematic_two_states.png` (never used), `config.SKETCH_SINGLE_REQUEST`
  (never read), `Gradients.agenda` (never read by code).
- Dead: `report._old_report_html` (`report.py:161-266`), `report.showcase_html` / `write_showcase` (base64 page,
  superseded by `showcase_build`), `schematic.build_spec_from_solution` outside fake mode, `annotate.py`
  `code_labels=False` path that still draws panel letter and footer.
- Duplicated: Stage B loop (`controller.py` / `stage_b_rerun.py`), run exit path (`Controller.run` /
  `cli._run_with_dir`), figure layout (`figure.compose` / `figure.recompose`), novelty-source parsing
  (`controller._sources`, `stage_b_rerun._rounds`, `build_references`).
- Tests that lock in behaviour the owner wants removed: `test_autopilot7.py::test_new_schemas_strict_and_defaults`
  asserts the keyword label parse. `test_smoke_real.py` has one assert across two tests. `test_stageb_rerun.py`
  tests only file discovery, not the loop.

---

## 6. Code that can spend Meta credit without a useful bound

- Per member turn up to 16 Responses requests (`council.py:103`), each re-billing the chain; plus one turn check
  and possibly a whole second turn (`meeting.py:126-147`); plus an "expired chain" whole-turn retry
  (`meeting.py:113-118`) that can run another 16 requests. Worst case per turn ≈ 48 requests.
- `_create_with_retries` (3 tries) × SDK default retries (2) on 5xx/429/content-filter 400 → up to 9 HTTP attempts
  per logical call; content-filter 400s are retried as if transient (`client.py:270-276`).
- `image_edit` retries 3× on 5xx/429/any exception within 240 s (`client.py:351-378`).
- Truncated structured output: one doubled re-ask (`client.py:251-257`, now billed), then `structured()` re-asks
  once more on bad JSON (`client.py:300-314`) — bounded.
- Hosted web search is not bounded by `MAX_TOOL_CALLS_PER_TURN`: it never appears as a `function_call`, so the
  counted-tool cap (`council.py:160-163`) never sees it.
- Calls not counted: none known after the 2026-11-02 fixes (truncated reply and searches now recorded). Image and
  SAM usage objects are not read; both are priced per call instead, which matches the pricing page.
- Caps that bound the whole run: per-run `MAX_COST_USD_PER_RUN = 15` and the cross-run ledger (`SpendLedger`,
  $50) — both checked before every call. The round-3 brief asks for $55 and `budget/ledger.jsonl` (item 0).

---

## 7. Secrets and files written outside the project

- `MODEL_API_KEY` is read only from the environment (`client.py:222`, `:347`); never written by code. The sandbox
  strips the environment (`sandbox.py:31-38`). Risk: finding 3.8 (sandboxed code can read `~/.zshrc`).
- `.env` is now git-ignored; no `.env` loader exists (the key lives in `~/.zshrc`).
- Outside the project: the sandbox writes temp dirs under the system temp folder (`sandbox.py:24`,
  `launcher.py:9`); matplotlib/Playwright caches. Relative paths (`lessons.md`, `runs/`, `docs/`, `showcase/`)
  resolve against the working directory, so running `hs` from another folder writes there
  (`lessons.py:19`, `controller.py:51`, `showcase_build.py:145,207,355`, `report.py:344,352`).

---

## 8. Every external call the runtime makes

| Endpoint | Model | Purpose | Code |
|---|---|---|---|
| `POST https://api.meta.ai/v1/responses` | muse-spark-1.3 | all text/vision calls: rev 0, members, Manager turn and gradients, turn check, Secretary, prior-art, verdict, optimizer, inspirations, schematic spec, writer, localization, designer eval, VLM gradient, progress check, light checks, lessons, examples | `client.responses` via OpenAI SDK |
| same, built-in tool `web_search` | muse-spark-1.3 | member and prior-art literature search (Meta's hosted search) | `tools.py:39`, `evaluator.py:25` |
| `POST https://api.meta.ai/v1/images/edits` | muse-image-1.0 | renders, local edits, close-up, fabrication steps | `client.image_edit` |
| `POST https://api.meta.ai/v1/responses` (image_generation tool) | muse-image-1.0 | fallback backend, off by default | `client._image_via_responses` |
| `POST https://api.meta.ai/v1/responses` (stream) | sam-3.1 | segmentation (added 2026-11-02, not yet used by the pipeline) | `client.sam_segment` |

Every model call goes to the Meta Model API. Nothing calls another model provider or service. Page builders make
no network calls (no CDN, no fonts fetched).

---

## 9. Spec and figures versus code

Against `docs/fig1_architecture.svg` / `docs/fig2_visualization_pipeline.svg`:
1. **knowledge/ (lessons · insights · tools)** — code has only `lessons.md`; no insights, no carried tools.
2. **Part map · SAM (masks, part connections, labels)** — not in the pipeline; localization is an LLM box call.
3. **Designer evaluation "re-checks last regions"** — not implemented; each round is judged from scratch.
4. **Mechanism sketch "real geometry, joints, motion, workpiece, use context"** — code draws a box graph.
5. **S1 fail "local or full fix, keep/revert"** — keep/revert exists only for local edits; a full re-render is
   never compared with the previous round.
6. **Fig. 1 routes "S1 exhausted (reported as such)" back to Stage A** (`manager.edit(master, room, s2 or 'S1 x3')`).
   This contradicts round-3 item A1/R4 (no gradient to the design on S1 exhaustion). The untracked-then-committed
   variant `docs/fig1_architecture-1.svg` says "S2: design flaw, only after a faithful render" and
   "back to A only on S2", which matches the brief. **Owner decision needed on which figure is current;
   round 3 follows the brief.**
7. **Fig. 2 node 2 "callouts for 4–7 parts" (image-drawn labels)** contradicts item 16a (labels move to code).
   Round 3 follows the brief.
8. **Controller "dossier(run)" at the end of every problem** — dossiers are built only by `hs showcase-build`.
9. **Evaluator and Manager are separate roles** — matches.
10. **Council "experts + manager in one room", 2–4 cycles, consensus exit** — matches, except the consensus bug
    (finding in §2).

Against the spec text:
- §0.5 / §5.2 "no text … clean technical illustration on white" vs SPEC-1 (image-drawn labels) vs round-3
  item 15/16a (no labels in the image, photoreal use context) — three different rules; spec and AGENTS.md must be
  updated (item 15).
- §3.2 roster guard 3–`MAX_MEMBERS`, §4.3 "≤ 250 words" + LLM turn check, §4.5 cap code rule — all removed by
  round-3 items 4, 6, 11; spec must be updated first.
- §4.3 vote-only round restricted to vote/raise_objection — code runs a full turn (§3 finding 6).
- §4.4 sketch PNG shown to the calling member — not implemented (14.3 still open).
- §4.4 new tools injected into every member's tools — not implemented.
- §5.3 image size = schematic aspect — fixed 1536x1024.
- §5.5b progress check after a full re-render — not implemented.
- §5.6 panel B close-up prompt "close-up of <critical part>" — spec itself prescribes the raw-id prompt;
  item 19 changes it.
- §6 "only lessons.md persists" — item 12 adds `knowledge/`.

---

## 10. What this means for round 3

No finding changes the architecture or the round-3 plan. The figure conflict in §9.6/§9.7 is the only owner
decision; round 3 follows the brief and records it in SUMMARY.md. Small new defects (§3 items 1–6, 9–17) are
folded into item 7; the sandbox filesystem risk (§3.8) is recorded in BLOCKED.md with the mitigation tried.
