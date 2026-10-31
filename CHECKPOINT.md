# CHECKPOINT.md — M0 → M3 (fake mode). Stopping here for review; M4 not started.

## What was built

- **M0 — Scaffold + client + fake mode.** `pyproject.toml` (console script `hs`, `src/hs` layout),
  `.venv` editable install, `config.py` (all §7 caps + one `RoleConfig{model, effort,
  max_output_tokens}` per role — switch any role's model/effort without code changes),
  `client.py` (Responses API only, §9 field names, retries honoring `Retry-After`,
  `BudgetExceeded` checked before every call, every `usage` logged to `cost.json`,
  truncation defence + one doubled-token retry), `fake_client.py` (scenario scripts for every
  branch, synthetic usage, placeholder PNGs), `schemas.py` (all §12 pydantic models +
  strict-schema post-processor: root object, `additionalProperties: false`, all keys required,
  `$ref` inlined, recursion rejected), `sandbox.py`+`launcher.py` (subprocess, `-I`, allow-list
  import hook on the immediate user frame, rlimits, 10 s timeout).
- **M1 — Stage A.** `master_prompt.py` (rev0, heading split, guards, shrink check, revert-only-
  named-section, rev/diff files), `stage_a/whiteboard.py` (ops validation, evidence written by
  code only, `update_proposal` clears votes, one-line rendering), `stage_a/tools.py`
  (calc/simulate/sketch/web_search/new_tool, every result auto-posted as `E<n>` evidence),
  `stage_a/meeting.py` (rotated cycles, deterministic closing rule, vote-only round, Secretary
  synthesis citing evidence ids), `stage_a/council.py` (real Responses tool loop),
  `stage_a/evaluator.py` (prior-art + verdict, never sees transcript, cap+blocking ⇒ reject),
  `stage_a/manager.py` (inspirations, written diagnosis, revert → rewrite), `stage_a/archive.py`.
- **M2 — Stage B.** `stage_b/schematic.py` (spec + topology/size/connectivity checks, one re-ask,
  deterministic no-text + labeled renders), `vlm_prompt.py` (forced no-text `must_not`),
  `image_model.py` (+ `IMAGE_BACKEND="responses"` fallback), `annotate.py` (0–1000 localization,
  Pillow leader lines/arrows/scale bar — all words drawn by code), `designer_eval.py`
  (S1/S2 + `decide()`), `image_archive.py`.
- **M3 — Figure + lessons + CLI.** `stage_b/figure.py` (panels A–D, per-step schematic references
  with logged repair, light checks, `MAX_FIGURE_IMAGES=8`, `rationale.md`), `lessons.py`
  (structural + near-duplicate + ≤200 char filter, ≤5 lines, `hs feedback` verbatim),
  `controller.py` (§7 loop verbatim incl. best-effort exit; report+board on every exit),
  `report.py` (`hs report` §8 sections 1–6, `hs compare`), `board.py` (sticky notes by author
  colour, evidence cards incl. sketches, objection cards, vote dots, timeline slider, `--live`),
  full `hs` CLI (`run|examples|feedback|show|report|compare|board`), `README.md`, `demo.sh`.

Fake-mode branches covered by tests: consensus in cycle 2; cap closure flagging open blocking
objections; Evaluator evidence request pinned as blocking objection and resolved with evidence;
reject → rewrite → accept (`diff_001.md` shows only the rewritten section); guard refusal;
shrink re-ask; Manager repeat → only the named section reverted; schematic-check failure →
`rejected_by_designer` → Stage A; S1 retry ×3 → `s2_return` → Stage A → S1 pass; cost cap →
best-effort report. No spec changes were needed (no `SPEC:` commits; `SPEC_CHANGES.md` not created).

## Verification commands (all run, fake mode)

```bash
.venv/bin/python -m pytest -q        # 22 passed, 2 skipped (real smoke tests)
.venv/bin/hs run --fake examples/01_stair_cart.json   # figure + report + board, cost $0.1162
.venv/bin/ruff check src tests       # All checks passed!
```

Latest fake runs: `runs/20261031-154319_stair-climbing-hand-truck-for-parcel-cou/`
(+ 02, 03 runs and `runs/compare_20261031-154622.html`). Open the `report.html` / `board.html`
in each to review. Fake cost per run: $0.1162 synthetic (28 calls); real cost unmeasured (≈$5–8
per problem per spec §9).

## Smoke tests needing the real API — written, NOT run (yours to run)

```bash
HS_SMOKE=1 .venv/bin/python -m pytest tests/test_smoke_real.py -q   # §14.1 text.format shape; §14.8 truncation shape
export MODEL_API_KEY=...                                            # (your terminal, not the agent's)
.venv/bin/hs run examples/01_stair_cart.json                        # first real end-to-end (M4 start)
```

Still open (§14, recorded in QUESTIONS.md with fallbacks): §14.2 search-results include,
§14.3 sketch single-request image, §14.4 images/edits fields + reference fidelity,
§14.5 localization quality, §14.6 search+structured combo (not needed by design),
§14.7 current prices/credit. Paste any HTTP 400 body into QUESTIONS.md when you run them.

## Open risks

- Real member-turn tool loop (`stage_a/council.py`) is code-complete but only exercised via
  FakeClient scripts; first real run may surface Responses tool-loop shape issues (§14.1–14.3).
- Fake Secretary/Schematic/Localization derive outputs deterministically from board/schematic
  geometry; real structured calls replace them behind the same interfaces.
- Board replay slider steps through precomputed snapshots; the static final-board rendering is
  the no-JS fallback and is what tests assert.
