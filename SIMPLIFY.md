# SIMPLIFY.md — candidates for removal (owner decision)

Removed in round 3 (D20, done): `Localization.confidence`, `RequirementCheck` / `stage_at_fault`,
`EvalRegion.fixed`, the two-state schematic, `SKETCH_SINGLE_REQUEST`, `report._old_report_html`,
the base64 showcase page (`hs showcase`; `hs showcase-build` remains) and base64 images on the
compare page, the LLM turn check, the flow view, the label keyword parse, image-drawn labels,
`cli._run_with_dir`, the second Stage B loop, the 250-word truncation, the cap code rule, the
member-count guard. Each is recorded in JOURNAL.md.

Not removed — I am unsure, please decide:

1. **Local edit + composite + progress check** (`stage_b/loop.py`, `prompt_gradient.py`). It ran once in
   v2 and both edits were reverted. Without decodable SAM masks the composite is a feathered box, not a
   mask. Keep (the gradient may choose it) or remove (every fix becomes a full re-render)?
2. **LLM localization fallback** (`annotate.Annotator.localize`) for parts SAM does not find. Costs one
   call per round when used; without it those parts get no label.
3. **Vetted calculators** (`stage_a/calculators.py`, AUTOPILOT §7.6). Members can do the same with `calc`;
   they add provenance fields. Used rarely in v2.
4. **`hs examples`** (LLM-generated problems) and **`hs feedback`** — not used by the demo.
5. **`hs stageb`** (Stage B rerun from an accepted solution). Useful for cheap re-renders; its runs have no
   meeting, which the pages now state.
6. **Chain-restart machinery** in `council.run_member_turn` (same-chain retries, up to 4 fresh restarts,
   plus a whole-turn retry in `Meeting._turn`). Needed in v1 for expired chains; it can multiply a
   turn's requests (worst case ~48). A simpler rule: one fresh restart, then end the turn.
7. **`figure.recompose`** — layout-only rebuild of an existing figure; only useful for manual repairs.
8. **`board --live`** auto-refresh mode — not used in any run.
