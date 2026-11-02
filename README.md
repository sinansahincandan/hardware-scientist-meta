# Hardware Scientist

Conceptual hardware design system (Meta Global AI Developer Hackathon). Input: a problem
statement with constraints. Output: an accepted concept (`SolutionPrompt`) and a concept
figure (panels A–D) — system view, critical part, measurement chain, fabrication steps.

A council of LLM experts argues around a shared whiteboard (Stage A); a Manager rewrites the
Markdown master prompt from written feedback (TextGrad-style); Stage B turns the accepted
concept into a schematic → image-model render → code-drawn annotation, judged by S1
(schematic-faithful?) and S2 (design flaw revealed?). The image model may draw
brief part callouts, checked by S1; after two label failures, labels fall back to
code-drawn overlays (`SPEC_CHANGES.md`). Full brief: [HARDWARE_SCIENTIST_SPEC.md](HARDWARE_SCIENTIST_SPEC.md),
plan: [PLAN.md](PLAN.md), assumptions: [QUESTIONS.md](QUESTIONS.md).

## Setup

```bash
python3 -m venv .venv            # or: uv venv .venv
source .venv/bin/activate
pip install -e ".[dev]"          # or: uv pip install --python .venv/bin/python -e ".[dev]"
export MODEL_API_KEY=...         # only needed for real runs (never commit it)
```

## Demo

```bash
hs run --fake examples/01_stair_cart.json     # offline, scripted FakeClient, synthetic cost
hs run examples/01_stair_cart.json            # real run (muse-spark-1.3 for every role)
open runs/<id>/report.html                    # evolution of one problem
open runs/<id>/board.html                     # whiteboard replay
hs compare runs/<a> runs/<b> runs/<c>         # side-by-side page
hs feedback "the council never questioned the sensor bandwidth"
hs examples --n 5                             # generate new problems (never overwrites)
./demo.sh                                     # the three shipped examples + compare
```

Every role's model and reasoning effort is configurable in `src/hs/config.py` (`ROLES`,
one entry per role: member, secretary, evaluator, manager, optimizer, schematic, VLM writer,
localization, designer eval, light check, lessons, example generator, master rev0).

## Cost (measured)

Real runs, 2026-10-31 (muse-spark-1.3 + muse-image-1.0; `cost.json` of each run):

| Run | Outcome | Cost |
|---|---|---|
| Example 01 stair truck (final run `20261031-184531`) | accepted (7 Stage A iters) | $7.2244 |
| Example 02 solar cold room (`20261031-212855`) | accepted (2 iters) | $1.9136 |
| Example 03 footbridge TMD (`20261031-220800`) | accepted (3 iters) | $2.5186 |
| Two earlier 01 attempts (kept, REVIEW.md) | best-effort / crashed, then fixed | $2.0010 + $2.1291 |
| Real smoke probes (§14) | pass | about $0.05 |

Total for the three final examples: **$11.66**. All real runs including failed
attempts and smoke: about $15.9 (session budget $60, AUTOPILOT.md). Fake mode is
$0.1162 synthetic per example. Prices: `muse-spark-1.3` $1.25 / $0.15 cached /
$4.25 per 1M tokens; web search $2.50/1000; `muse-image-1.0` $0.01/image. The
cost cap ($15/run default) is checked before every call; every call's usage is
logged to `runs/<id>/cost.json`.

**Budget ledger ($55 for round 3, all runs).** Every real Meta call is checked against
`budget/ledger.jsonl` (git-ignored; one line per call: time, run id, role, model, tokens,
images, SAM calls, searches, estimated USD; `MAX_TOTAL_SPEND_USD` in `config.py`) before it is
sent, with a worst-case estimate of that call, and appended after it. Each call prints a running
line to stderr: `[budget] evaluator +$0.0123 | total $3.4567 of $55.00 | left $51.5433`.
`hs budget` prints spent, remaining and per-run totals. A call that could cross the cap, or a
Meta HTTP 402 billing error, raises `BudgetExceeded` (never retried); the run then ends through
the best-effort path with its files saved. Fake mode never writes the ledger. The ledger counts
only calls made by this code; the Meta dashboard is the authority on credit left.

Pages: `hs showcase-build runs/<a> runs/<b> runs/<c> --out showcase` (see below) builds the showcase;
the old single-file `hs showcase` page was removed in round 3 (D20).

## Known limitations (spec §13)

- The evaluator is an LLM judge using its own engineering knowledge; it consults code-computed
  evidence only when a claim looks doubtful. It is not a physical test.
- Novelty is discussed against one web-searched closest prior art; it is not a patent search.
- Prompt-level learning is weaker than weight-level learning; `lessons.md` is a small, filtered memory.
- `muse-image-1.0` reference fidelity is not controllable (`input_fidelity` unsupported);
  S1 exists because of this; the `responses` backend is a switch, not a fix.
- Dimensions are size classes; no tolerance or detailed geometry.
- One accepted concept per run; alternatives live in `archive.jsonl`, not in the figure.
- Real-API shapes in spec §14 are settled (see `QUESTIONS.md`): `text.format`
  nesting works, truncation reports `status=incomplete`, image edits accept
  `tool_enablement`/`reasoning_strength`, localization is usable. Remaining:
  provider chain state (`previous_response_id`) can expire mid-turn — the
  member-turn loop retries and restarts chains from the code-side board.
- Image-model labels invent values, so labels fall back to code-drawn
  overlays after two label failures (AUTOPILOT §7.1, `SPEC_CHANGES.md`).
- Fabrication-step renders (panel D) read as parts posters, and the final
  schematic is a grid diagram, not a mechanism sketch — known visual limits.

## v2 additions (2026-11-01)

- `hs stageb runs/<run>` — rerun Stage B only, seeded from a run's
  accepted (or latest) solution; an S2 route-back is saved to
  `s2_return.json`, never hidden.
- `hs showcase-build runs/<a> runs/<b> runs/<c> --out showcase` —
  copy the final runs and build `showcase/index.html` plus one
  `showcase/<problem>/dossier.html` per problem (architecture path
  overlays from `docs/figures_map.json`, conformance tables, cost
  per role). The shipped showcase is committed at `showcase/`.
- v2 behaviour: region-anchored designer evaluation with source
  trace, two-step Manager gradients, Manager in the room, speaking
  rule with turn checks, transcript compaction, resolved citations
  (`references.md` per run). Page screenshots could not be taken in
  the build sandbox — see `BLOCKED.md`.
