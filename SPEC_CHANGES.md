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
