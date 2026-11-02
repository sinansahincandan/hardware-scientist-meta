# CLAUDE.md — Hardware Scientist (HS)

## What this is
Hardware Scientist is a self-evolving compound AI system for conceptual hardware design, built for the Meta Global AI Developer Hackathon (submission due 2026-11-04, 21:00 ET). A council of domain-expert LLM agents and a Manager work a problem on a shared whiteboard; an Evaluator and a rendered prototype return written critique; that critique is backpropagated as textual gradients (TextGrad) into the system's own prompts. The runtime uses only Meta models through the Meta Model API (muse-spark-1.3, muse-image-1.0, sam-3.1). Versions 1–2 were written by Muse Code; from round 3 on, Claude Code writes the code.

Owner: Sinan (mechanical engineer, PhD; no software background). He judges inputs and output figures. Explain what you did in plain words; trace every problem he reports to its source files (whiteboard, transcript, gradients, S1/S2 records, REVIEW.md).

## Source of truth
- `HARDWARE_SCIENTIST_SPEC.md` (spec text wins over figures), `SPEC_CHANGES.md`.
- Architecture figures: `docs/fig1_architecture.svg`, `docs/fig2_visualization_pipeline.svg`. The owner maintains them; do not edit. The implementation must match them.
- Round-2 review with verified findings: `docs/review/hs_round2_review.md`.
- Current task: the round-3 message the owner pastes in: PHASE 1 environment and Meta API check, PHASE 2 full code review (docs/review/code_review_cc.md), PHASE 3 items 0–25.
- The owner does not set up environments or type commands. Do all setup yourself; when he must act (paste the key into .env, read the Meta dashboard, approve a login), tell him in one or two plain sentences.

## Owner's standing rules
1. No numeric scores, ratings or rubrics anywhere. Judgments are prose. Structured fields only where Python must branch.
2. Decisions inside loops (accept, block, local vs full fix, what the Manager changes) are made by the LLMs from written feedback, not by hard-coded rules.
3. TextGrad loop: critique → output gradient → prompt gradient → targeted prompt edit where the problem is → the same issue re-checked → keep or revert. Every loop must close.
4. What is written must actually run. Never report something that did not happen. A feature is done only when a real run shows it working, with the file path recorded in JOURNAL.md.
5. Do not change the architecture or add features he did not approve. Prefer editing and removing. Ask before architecture changes.
6. Minimal problem constraints; the council finds constraints in the literature. Members must search and read sources; no citation without search evidence on the board.
7. Speech: plain words first, only the deciding numbers (units, ≤3 significant figures), ids never alone, roster names only, no pipeline jargon in Stage A, no truncation.
8. Concept design: deviations are acceptable if the concept still works, but the system must notice and state them.
9. Final figure: photoreal device in its use context, mechanism readable, directions/orientation/scale/connections correct. Flow views only when the physics calls for them and the council chose them.
10. No random sampling or best-of-N seeds.

## Budget (Meta credit)
- Meta credit left: $67 (2026-11-02). Only hs runs and smoke tests use it; Claude Code's own work does not.
- Every real Meta call goes through the project-wide ledger (round-3 item 0). Check the ledger before every real run. Round-3 cap: $55.
- Stop cleanly on an out-of-credit or billing error; never retry it.

## Working rules
- Never print, log or commit `MODEL_API_KEY` or any secret. Keep `.env` git-ignored. Run the secret scan before every commit.
- After every numbered item: `pytest -q`, `ruff check src tests`, update JOURNAL.md (`[YYYY-MM-DD HH:MM] what · found · changed · ledger total`), commit, push. No committed file over 50 MB; `runs/` stays out of git; finals go to `showcase/`.
- Verify pages by rendering them headless with Playwright and looking at the screenshots. Never open pages in the owner's browser.
- Look at every image a run produces before calling the run reviewed. REVIEW.md states only what the files show.
- Use subagents sparingly (usage limits); the deadline matters more than parallelism.
