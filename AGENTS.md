# AGENTS.md — standing rules for this repository (Hardware Scientist)

Read `HARDWARE_SCIENTIST_SPEC.md` fully before writing code. It is the source of truth. `docs/fig1_architecture.png` and `docs/fig2_visualization_pipeline.png` are overviews; the spec text wins on conflict.

## Priority rules
1. Implement the architecture as specified. Do not simplify away the shared whiteboard, the cycle/consensus closing rule, the Manager (written diagnosis + section rewrite + revert on repeat), the archives, the S1/S2 split, or the schematic→render→annotate order.
2. All model calls go through `src/hs/client.py` and use the Responses API (`POST /v1/responses`) with the exact field names in spec §9. Never use Chat Completions. Never invent parameters; check `https://dev.meta.ai/docs/` first.
3. Judgments travel between LLMs as **free written text** (no numeric scores, no issue categories). Structured output is used only for the yes/no decisions and lists the controller must read (`accept`, `s1_faithful`, `s2_flaw`, `same_problem_as_before`, …) and for drawing data. The Master prompt is a Markdown document with fixed headings; the optimizer rewrites whole sections freely; code only enforces the guards in spec §3.2.
4. `HS_FAKE=1` must run the full pipeline offline with synthetic `usage`. Write tests in fake mode. Run `pytest -q` before ending any milestone.
5. Never read or print `MODEL_API_KEY` except to construct the client. Never commit `runs/` outputs that contain keys.
6. LLM-written code runs only via `src/hs/sandbox.py` (subprocess, timeout, allow-listed imports).
7. Image model output contains no text; all labels/arrows/scale bars are drawn by code.
7b. Every `calc`/`simulate`/`sketch`/`web_search` result is posted to the whiteboard as evidence by code. Members can never edit evidence. The evaluator never sees the transcript; it consults evidence when a claim looks doubtful and sends evidence requests back to the room.
8. Enforce every cap in `config.py`; check the cost cap before every call; log every call's `usage` to `cost.json`.
9. Spec §14 lists unverified API details. Settle each with the smoke test named in spec §11 and record the outcome in `QUESTIONS.md`; never build on an unverified shape without that test.

## Working style
- Milestones M0→M4 in order (spec §11). After each: `pytest -q`, `hs run --fake examples/01_stair_cart.json`, then write `CHECKPOINT.md` (what was built, 3 verification commands, open risks).
- Do not stop to ask questions. Record each assumption with the default you chose in `QUESTIONS.md` and continue.
- Prefer small, typed modules over clever abstractions. Type hints everywhere; `ruff` clean.
- When a real API call fails with HTTP 400, print the full error body into `QUESTIONS.md`, fix the request, and add a unit test that covers the fixed shape.
- Keep `README.md` current: setup, demo commands, cost table, known limitations.

## Vocabulary (use these names in code and docs)
MasterPrompt · Council · Whiteboard · Evidence · Meeting (turn, cycle, closure) · CouncilArchive · Secretary · Evaluator (prior-art check + verdict) · Manager (written diagnosis + section rewrite) · Schematic · VLMPromptWriter · ImageModel · Annotator · DesignerEval (S1, S2) · ImageArchive · FigureComposer · Lessons · Controller · Report · Board.

## Examples
`examples/01_stair_cart.json`, `02_solar_cold_room.json`, `03_footbridge_damping.json` are the fixed demo set (see `EXAMPLE_PROBLEMS.md`). Never edit them and never add hand-written hints, rubrics or expected answers for them anywhere in the code or prompts.
