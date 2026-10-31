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
