# Hardware Engineer (HE) — open-weights copy

**Built with Muse Spark Open.** The same loops as the main branch, run on Meta's open-weights Muse Spark Open (Baseten) and SAM 3 (Modal); pictures from Muse Image 1.0 on the Meta Model API. See `NOTICE.md` and `licenses/`.

Conceptual hardware design system (Meta Global AI Developer Hackathon). Input: a problem
statement with constraints. Output: an accepted concept (`SolutionPrompt`) and a concept
figure (panels A–D) — system view, critical part, measurement chain, fabrication steps.

A council of LLM experts argues around a shared whiteboard (Stage A); a Manager rewrites the
Markdown master prompt from written feedback (TextGrad-style); Stage B turns the accepted
concept into a mechanism sketch → photoreal image-model render → SAM 3.1 part measurements →
designer evaluation (S1: faithful to the sketch? S2: design flaw revealed?), in a closed loop that
keeps a round only when it fixed an earlier fault and broke nothing. The render carries no text;
code draws every label from SAM boxes (round 3, `SPEC_CHANGES.md`). Full brief: [HARDWARE_SCIENTIST_SPEC.md](HARDWARE_SCIENTIST_SPEC.md),
plan: [PLAN.md](PLAN.md), assumptions: [QUESTIONS.md](QUESTIONS.md).

## Setup

```bash
python3 -m venv .venv            # or: uv venv .venv
source .venv/bin/activate
pip install -e ".[dev]"          # or: uv pip install --python .venv/bin/python -e ".[dev]"
export MODEL_API_KEY=...         # only needed for real runs (never commit it; ~/.zshrc works)
```

Before committing: `.venv/bin/python scripts/secret_scan.py` (no key, no file over 50 MB).

## Demo

```bash
hs run --fake examples/01_stair_cart.json     # offline, scripted FakeClient, synthetic cost
hs run examples/01_stair_cart.json            # real run (muse-spark-1.3 for every role)
open runs/<id>/report.html                    # evolution of one problem
open runs/<id>/board.html                     # whiteboard replay
hs compare runs/<a> runs/<b> runs/<c>         # side-by-side page
hs feedback "the council never questioned the sensor bandwidth"
hs examples --n 5                             # generate new problems (never overwrites)
hs budget                                     # Meta spend from the ledger: spent, left, per run
hs stageb runs/<id>                           # redraw an accepted solution (Stage B only, no meeting)
hs showcase-build runs/<a> runs/<b> runs/<c> --out showcase
./demo.sh                                     # the three shipped examples + compare
.venv/bin/python scripts/shoot.py page.html out/   # headless 1440 px page screenshots, sliced
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

## Related work

Each line says what Hardware Scientist takes from the work; every page was fetched on 2026-11-02.

- **TextGrad** (Yuksekgonul et al., 2024, arXiv:2406.07496) — written feedback treated as a gradient and passed backward through the system: critique → output gradient → prompt gradient → targeted prompt edit, in Stage A (master prompt) and Stage B (image prompt).
- **Agent Symbolic Learning** (Zhou et al., 2024, arXiv:2406.18532) — the agent pipeline itself (prompts, roles, tools) is the thing optimized; the Manager rewrites member roles, adds or merges members and registers tools.
- **Trace** (Cheng et al., 2024, arXiv:2406.16218) — the execution trace carries the feedback; the Manager's backward chain links each claim to its evidence, the member turn and the prompt section that produced it.
- **ACE — Agentic Context Engineering** (Zhang et al., 2025, arXiv:2510.04618) — improve the context, not the weights, with incremental edits that do not lose detail; section-wise rewrites with guards, the shrink check and saved revisions.
- **Reflexion** (Shinn et al., 2023, arXiv:2303.11366) — written reflections on past failures kept as memory; the council archive, inspirations and the process lessons.
- **OPT2I** (Mañas et al., 2024, arXiv:2403.17804) — an LLM rewrites the text-to-image prompt until the image matches; Stage B's VLM prompt writer and VLM prompt gradient.
- **SAM 3** (Carion et al., 2025, arXiv:2511.16719) — concept segmentation from short text phrases; Stage B measures each part of a render and places code labels from SAM 3.1 boxes.
- **Set-of-Mark prompting** (Yang et al., 2023, arXiv:2310.11441) — segment first, then let the VLM refer to marked regions; segmenter measurements are given to the critic as region evidence.
- **Multi-agent debate** (Du et al., 2023, arXiv:2305.14325) — several agents critique each other over rounds before converging; the council meeting on a shared whiteboard with objections and votes.
