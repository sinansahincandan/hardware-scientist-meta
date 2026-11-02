# SPEC_CHANGES.md

## SPEC-1 (AUTOPILOT §7.1): image model may draw its own labels
Replaces spec §0.5/§5.2 "no text in the image" rule. The VLM prompt asks
muse-image-1.0 for brief callouts for the 4–7 focus parts. Designer
evaluation S1 also checks that every label names the right part and is
spelled correctly. If labels are wrong in two consecutive rounds, the
pipeline falls back to a clean render + code-drawn overlay (Annotator).
Intent preserved: words must be correct and legible; the source of the
words (image model vs code) is now a checked choice, not a ban.

## SPEC-2 (AUTOPILOT §7.2–7.3): structured visual plan + pixel-first review
VLMPrompt now carries a structured visual plan (view, spatial layout,
operating moment, transfer path, focus parts, interactions, avoid list).
After a failed review, targeted corrections from the actual-image review
are appended verbatim to the next writer prompt. DesignerEval first
describes what it actually sees (pixel_description) before reading the
concept, and reports each requirement as observed/ambiguous/missing
with the stage that caused each fault (meeting/schematic/prompt/render).

## SPEC-3 (AUTOPILOT §7.4): deliverable summary fields
SolutionPrompt gains mechanism_sentence, decisive_choices (exactly 3),
open_question (exactly 1) and transfer_line
("Force: A → B → C | Measured: D → E"), written by the Secretary.
These head report.html in the deliverable layout.

## SPEC-4 (AUTOPILOT §7.6): vetted calculators
Members may call vetted_calc with one of the named functions in
hs/stage_a/calculators.py next to free calc. Every input records its
provenance (user / source / assumption) in the evidence entry.

## SPEC-5 (round 3, item 0): project-wide budget ledger
Spec §7 caps gain a cross-run cap: every real Meta call is checked before it is sent against
`budget/ledger.jsonl` (worst-case estimate of that call) and appended after it; round-3 cap $55.
HTTP 402 billing errors raise `BudgetExceeded`, never retried. Web searches (`web_search_call`
items) and SAM calls are priced and counted. `hs budget` prints spent, remaining, per-run totals.

## SPEC-6 (round 3, A4/A5/A6): meeting closure, proposal rule, no cutting of speech
- A4: the cap code rule (`closed_by == "cap"` + open blocking objection → reject) is removed; the
  Evaluator gets the closure facts and open objections as information and decides in writing.
  Consensus is decided after the Manager's turn, so the Manager's objection counts.
- A5: the protocol (rev 0 §4 and DEFAULT_PROTOCOL) names who integrates the proposal and when;
  the Manager calls for it if nobody has by the end of cycle 2.
- A6: no 250-word truncation and no LLM turn check; a turn over the limit is re-asked once to
  shorten (members and Manager). The vote-only round allows only vote / raise_objection
  (enforced in code); the Manager's whiteboard actions are limited to process objections and
  read_evidence (it cannot vote or design). Manager turns are billed as `manager`, progress
  checks as `progress_check`.

## SPEC-7 (round 3, A3 + B11 guards): Manager rewrites are never lost
Guards are per section and only two remain (§1 unchanged, both fixed criteria verbatim; the
3–MAX_MEMBERS roster guard and MAX_MEMBERS are removed). Passing sections are applied; a violating
section alone is re-asked once, then keeps its old text. Ambiguous headings ("## 3. Criteria") are
recorded, not guessed. Every optimizer output is saved. Reverts always yield a saved revision. The
Manager's agenda is written into §4 by code. Only gradient_prompt.json is written (no diagnosis.json).

## SPEC-8 (round 3, B8/B9/B10): searches become evidence; speech; physical sanity
- B8: member requests send include=["web_search_call.results"]; every search result is posted as
  evidence (title, organisation/site, year when stated, URL, query, passage when returned) from every
  response including the final one; one extra chained request lets the member cite the new ids.
  Citations only from board evidence; the "according to <author, year>" template slot is removed.
  The prior-art check records its sources the same way.
- B9: plain words first, deciding numbers only (units, <= 3 significant figures), roster names only
  (listed in every turn input), no pipeline vocabulary; evidence summaries are readable (no raw
  decimals or tracebacks).
- B10: members, Manager and Evaluator check key results against everyday scales; the Evaluator
  names unsupported claims, re-derives deciding arithmetic, uses evidence_requests when a number
  looks off, and lists measurable deviations (C18 for Stage A).

## SPEC-9 (round 3, C15 + 16a): photoreal use-context renders, labels by code
Supersedes SPEC-1 (image-drawn labels) and the "clean technical illustration on white" wording of
§0.5/§5.2 and AGENTS.md rule 7. The writer asks for a correct, photorealistic rendering in the use
context (workpiece, real materials, product-shot lighting, mechanism readable), correctness first.
The render carries no labels or callouts; code labels the figure only. The designer evaluation
judges the unlabeled render (no burned margins, footer, panel letter or scale bar). must_not names
kinds of things, never quoted text; code drops must_not entries containing digits.

## SPEC-10 (round 3, items 16-18): SAM part map, closed Stage B loop, deviations
New §5.4b and the closed-loop paragraph in §5.5. SAM 3.1 measures every part per round (boxes only;
masks blocked) against an LLM-derived expectation table; differences are text evidence for the
critic and the gradient; SAM boxes place code labels. Each evaluation rules on every earlier fault
(fixed / still wrong / regressed) and compares with the kept render; rounds that fix nothing or
regress revert render and prompt; s1_pass needs every earlier fault fixed. Deviations are listed
with whether they matter. EvalRegion.fixed, RequirementCheck and Localization.confidence removed.

## SPEC-11 (round 4, owner decisions 2026-11-02): back to the figures
The owner's figures (docs/fig1_architecture.svg, docs/fig2_visualization_pipeline.svg) are the target.
1. S1 exhausted: as in Fig. 1 ("S2: design flaw, or S1 exhausted (reported as such)"): the outcome goes to the
   Manager labelled "could not be drawn faithfully after N rounds" with the regions; the Manager decides in
   writing whether the design is under-specified and should change. Supersedes A1's "nothing sent to the design".
2. Callouts: as in Fig. 2 ("pixels + callouts: image model; checks: SAM + judges"): the image model draws short
   callouts (part names only) for 4–7 focus parts; S1 checks each callout; SAM masks and a label check verify the
   final panel; code labels are the fallback. Supersedes round-3 item 16a / SPEC-9's "no text in the render".
3. SAM masks: meta-sam-parser 0.1.0 installed (owner approved); parts are measured from masks.
4. Evaluator: sees, constraint by constraint, what is not satisfied and says so in writing; it may judge a
   constraint no longer valid and accept with that reason. No scores, no strict quantification.
