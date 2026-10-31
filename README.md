# Hardware Scientist

Conceptual hardware design system (Meta Global AI Developer Hackathon). Input: a problem
statement with constraints. Output: an accepted concept (`SolutionPrompt`) and a concept
figure (panels A–D) — system view, critical part, measurement chain, fabrication steps.

A council of LLM experts argues around a shared whiteboard (Stage A); a Manager rewrites the
Markdown master prompt from written feedback (TextGrad-style); Stage B turns the accepted
concept into a schematic → image-model render → code-drawn annotation, judged by S1
(schematic-faithful?) and S2 (design flaw revealed?). All words in images are drawn by code;
the image model paints pixels only. Full brief: [HARDWARE_SCIENTIST_SPEC.md](HARDWARE_SCIENTIST_SPEC.md),
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

## Cost (measured in fake mode; real figures are pre-M4 estimates)

| | Fake mode (this repo, verified) | Real estimate (spec §9, unverified until M4) |
|---|---|---|
| One shipped example (2 Stage A iters, 2 Stage B rounds) | $0.1162 synthetic, 28 calls | ≈ $5–8 |
| Three shipped examples | $0.35 synthetic | ≈ $15–25 total |

Prices: `muse-spark-1.3` $1.25 / $0.15 cached / $4.25 per 1M tokens; web search $2.50/1000;
`muse-image-1.0` $0.01/image. The cost cap ($15/run default) is checked before every call;
every call's usage is logged to `runs/<id>/cost.json`.

## Known limitations (spec §13)

- The evaluator is an LLM judge using its own engineering knowledge; it consults code-computed
  evidence only when a claim looks doubtful. It is not a physical test.
- Novelty is discussed against one web-searched closest prior art; it is not a patent search.
- Prompt-level learning is weaker than weight-level learning; `lessons.md` is a small, filtered memory.
- `muse-image-1.0` reference fidelity is not controllable (`input_fidelity` unsupported);
  S1 exists because of this; the `responses` backend is a switch, not a fix.
- Dimensions are size classes; no tolerance or detailed geometry.
- One accepted concept per run; alternatives live in `archive.jsonl`, not in the figure.
- Real-API shapes in spec §14 are unverified: smoke tests exist (`tests/test_smoke_real.py`)
  but have not been run yet (see `CHECKPOINT.md`).
