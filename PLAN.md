# PLAN.md — Hardware Scientist implementation plan

Source of truth: `HARDWARE_SCIENTIST_SPEC.md` (§-refs below). Figures `docs/fig1_architecture.png`,
`docs/fig2_visualization_pipeline.png` are overviews; spec text wins on conflict.
Runtime model for **every role**: `muse-spark-1.3` (configurable per role, see §9 below).
Image model: `muse-image-1.0`. Responses API only (`POST /v1/responses`).

Done-checks (each milestone): `pytest -q` green; `hs run --fake examples/01_stair_cart.json`
creates a run folder; `CHECKPOINT.md` rewritten. M0→M3 in fake mode only; real-API smoke
tests are written but **not run** (commands listed in `CHECKPOINT.md`).

---

## 1. Module list (spec §2)

| Module | Responsibility |
|---|---|
| `src/hs/cli.py` | `hs run|examples|feedback|show|report|compare|board`; `--fake` ⇒ `FakeClient`; caps overridable by flags |
| `src/hs/config.py` | Caps (§7), per-role `RoleConfig{model, effort, max_output_tokens}` (§9), prices, `IMAGE_BACKEND` |
| `src/hs/client.py` | `MetaClient`: `responses()` (Responses API), `structured()`, `free_text()`, `member_turn()` tool loop, `image_edit()`; retries + `Retry-After`; `usage`→`cost.json`; `BudgetExceeded` pre-check; `instructions` resent every call; incomplete-retry (double tokens, cap 32k) |
| `src/hs/fake_client.py` | `FakeClient`: same interface, zero network, scripted outputs per role + scenario, synthetic `usage`, placeholder PNGs |
| `src/hs/schemas.py` | Pydantic models §12.1–12.14 + strict-schema post-processor (§9) |
| `src/hs/master_prompt.py` | Markdown master prompt: heading split, rev0, section rewrite + guards + shrink check, section revert, rev/diff files |
| `src/hs/stage_a/council.py` | Member roster from §2 roster; per-turn prompt assembly (own `###` + §1,§3,§4,§5,§6) |
| `src/hs/stage_a/tools.py` | `whiteboard` dispatch, `calc`, `simulate`, `sketch`, `web_search` evidence posting, `new_tool` registry |
| `src/hs/stage_a/whiteboard.py` | `Whiteboard` state (§12.15), op validation (§12.16), `whiteboard.md` rendering, `whiteboard_history.jsonl` |
| `src/hs/stage_a/meeting.py` | Turns, cycle rotation, closing rule (§4.3), vote-only round, Secretary synthesis |
| `src/hs/stage_a/evaluator.py` | Prior-art check (free text + `web_search`) + `Verdict`; never sees transcript; `cap`+blocking ⇒ `accept=false` |
| `src/hs/stage_a/manager.py` | Inspirations pick, `Gradients` diagnosis, revert-then-rewrite orchestration, `no_progress` streak |
| `src/hs/stage_a/archive.py` | `CouncilArchive` JSONL (`accepted|rejected|rejected_by_designer`), `best()` rule (§10) |
| `src/hs/stage_b/schematic.py` | `SchematicSpec` call + code checks + deterministic `render_schematic` (no-text + labeled PNG, `schematic.json` geometry) |
| `src/hs/stage_b/vlm_prompt.py` | `VLMPromptWriter` (`VLMPrompt` + forced `must_not` suffix) |
| `src/hs/stage_b/image_model.py` | `muse-image-1.0` `/v1/images/edits` JSON; `IMAGE_BACKEND="responses"` fallback; retry/backoff, content-policy handling |
| `src/hs/stage_b/annotate.py` | `Localization` call (0–1000 grid) + Pillow overlay (labels, leader lines, arrows, scale bar) |
| `src/hs/stage_b/designer_eval.py` | `DesignerEval` (S1/S2) + `decide()` → `s1_pass|s1_retry|s2_return` |
| `src/hs/stage_b/image_archive.py` | `ImageArchive` JSONL (prompt+render+annotated+eval per round) |
| `src/hs/stage_b/figure.py` | Panels A–D, per-step references with repair, `LightCheck`s, `MAX_FIGURE_IMAGES`, `rationale.md` |
| `src/hs/lessons.py` | `Lessons` distill + 3-filter + append; `hs feedback` verbatim path |
| `src/hs/controller.py` | Loop of §7 verbatim incl. best-effort exit; `Report.write` on every exit |
| `src/hs/report.py` | `hs report` (one run) + `hs compare` (several runs), self-contained HTML, base64 images (`--no-embed`) |
| `src/hs/board.py` | `hs board` replay HTML + `--live` (rewrite per turn, 5 s meta-refresh) |
| `src/hs/sandbox.py` | Subprocess runner (§4.4): timeout, captured/truncated output |
| `src/hs/launcher.py` | In-subprocess: env, `sys.meta_path` allow-list hook (user-frame only), rlimits |

Tests: `tests/` — everything runs with `HS_FAKE=1` / `FakeClient`; no network.

## 2. Schemas (spec §12) — pydantic, field names binding

Shared enums (drawing data only): `ConnectionKind = mechanical|electrical|optical|fluid|wireless|thermal`;
`LoadDirection = up|down|left|right|in|out`.

- **12.1 `SolutionPrompt`**: `title, problem_restatement, assumed_constraints[{constraint, source, evidence_ids[]}]`,
  `functional_decomposition[]`, `concept{working_principle, parts[{id,name,function,material,size_class_mm{min,max},qty}],
  connections[{from_id,to_id,kind,label}], loads[{on_id,label,direction}]}`,
  `key_estimates[{quantity,value,unit,method,evidence_ids[]}]`,
  `measurement_chain[{stage: sensor|conditioning|instrument|computer, name, interface}]`,
  `fabrication_steps[{step,description,method,parts_present[]}]` (3–5),
  `risks[{risk,mitigation}], novelty_claim, cost_class (<$100|$100-1k|$1k-10k|>$10k)`,
  `figure_spec{system_view, critical_part_id, preferred_view: isometric|top|side|section}, open_questions[]`.
- **12.2 `Verdict`**: `feedback: str` (free text), `evidence_requests: list[str]`, `accept: bool`.
  `source` (evaluator/designer/schematic_check) set by code, never by the model.
- **12.3 `Gradients`**: `per_member[{member,what_went_wrong,what_should_change}]`,
  `per_section[{heading,diagnosis,direction}]`, `sections_to_change[]`, `root_cause`,
  `same_problem_as_before: bool`, `repeat_explanation`, `revert_sections[{heading,to_revision}]`.
- **12.4 `MasterPromptRewrite`**: `sections[{heading,new_text}]`, `change_note`.
- **12.5 `SchematicSpec`**: `view: top|side`, `nodes[{id,label,shape: rect|circle|beam|plate|cylinder,
  size_class_mm{min,max}, layout{col,row}, color_hint}]`, `edges[{from_id,to_id,kind,label,arrow}]`,
  `loads[{on_id,label,direction}]`, `critical_part_id`, `scale_bar_mm: float`, `notes[]`.
- **12.6 `VLMPrompt`**: `prompt, must_not[], changes_from_previous`.
- **12.7 `Localization`**: `parts[{id, found: bool, box_1000{x0,y0,x1,y1}, confidence}]`.
- **12.8 `DesignerEval`**: `s1_faithful: bool, s1_differences: str, s2_flaw: bool, s2_feedback: str, notes: str`.
- **12.9 `Lessons`**: `candidates[{text, category: process|prompts|tools|image_model, structural: bool, evidence}]`.
- **12.10 `Problem`**: `title, statement, constraints[], criteria[], attachments[]`.
- **12.11 `Inspirations`**: `picks[{archive_id, why_useful}]` (1–3; ≥1 non-accepted when available — enforced in code).
- **12.12 Master prompt**: not a schema — Markdown with fixed headings (§3 below); rev0 is free Markdown, heading-checked.
- **12.13 `LightCheck`**: `ok: bool, reason: str`.
- **12.14 `ProblemSet`**: `problems: list[Problem]`.
- **12.15 `Whiteboard`** (internal, §4 below). **12.16 whiteboard tool args** (function tool, non-strict, code-validated).

Judgment rule (§0.4): no numeric scores, no issue categories anywhere. Structured output carries only
controller-read decisions/lists + drawing data; everything else is free text and is never parsed for control flow.

## 3. Strict-schema rules (spec §9) — `schemas.make_strict_schema(model)`

Built from `model.model_json_schema()`, then post-processed recursively:

1. Root is a plain object; no top-level (and nowhere) `allOf`/`oneOf`; `anyOf` allowed only below root.
2. Every object gets `additionalProperties: false`; every property key is added to `required`
   (optional fields become required-but-nullable via `anyOf: [T, {type: null}]`).
3. No recursive `$ref`: `$defs` are inlined (depth ≤ 10, ≤ 5000 properties); a recursion cycle raises `ValueError`.
4. Sent as `text={"format": {"type": "json_schema", "name": <ModelName>, "schema": <processed>, "strict": True}}`
   — OpenAI-SDK nesting, **unverified on Meta** (§14.1; M0 smoke test settles it; 400 body → `QUESTIONS.md` + regression test).
5. Function-tool schemas are separate: flat Responses format, `strict` omitted; code validates arguments.
6. Never send `response_format`, `stop`, penalties, `truncation`, unknown `include`s, or
   `include: ["reasoning.encrypted_content"]` with `previous_response_id`; `temperature`/`top_p` unset.
7. Truncation defence: `status != "completed"` OR `usage.output_tokens >= max_output_tokens - 64` OR JSON
   parse failure ⇒ retry once with doubled `max_output_tokens` (cap 32000).

## 4. Markdown master prompt (spec §3.2)

```
# Master prompt — <problem title> — Rev <N>
## 1. Problem            problem.json verbatim (code-written; never editable)
## 2. Roles              ### <member name> blocks; roster = list of ### names
## 3. Tools              free text (+ one-line mentions appended by code when a tool registers)
## 4. Meeting protocol   free text (default protocol_text: cycle 1 decompose/estimate; ≥2 attack/defend/integrate/vote)
## 5. Criteria           free text; must contain verbatim:
                         "The concept must work physically (no violated conservation law, load path, or signal path)."
                         "The concept must be buildable with purchasable parts and ordinary lab/shop methods."
## 6. Lessons applied    lines copied from lessons.md
```

- **Split**: `split_master_prompt(text)` → ordered `[(heading, body)]` on the six `## ` headings; roster =
  `### ` names under §2. A member's instructions = own `###` block + §1, §3, §4, §5, §6.
- **Rev 0**: one free-Markdown call (problem + full `lessons.md`); model writes §2–§6, chooses 3–5 members.
  Code writes §1, inserts fixed criteria + problem criteria verbatim if missing; missing heading ⇒ one re-ask.
- **Rewrite guards** (the only hard rules, `apply_rewrite()`): §1 byte-identical; both fixed criteria still
  present verbatim; 3–`MAX_MEMBERS` members under §2. Violation ⇒ one re-ask with reason; still violating ⇒
  offending section keeps old text. Bound: 1 optimizer call + ≤1 guard re-ask + ≤1 shrink re-ask per iteration.
- **Shrink check**: a rewritten section losing >50% of its length triggers one re-ask
  ("section X lost N% — intended?" + removed lines); the second answer is applied as-is.
- **Revert on repeat**: if `Gradients.same_problem_as_before` and `revert_sections` non-empty, code copies
  those sections' text from the named revision *before* the optimizer runs; other sections keep current text.
  Each revision saved as `master_prompt/rev_{N:03d}.md` + `diff_{N:03d}.md` (red/green per-section diff +
  `change_note`); nothing overwritten. Tool registrations (`runs/<id>/tools/<name>.json`) are revision-independent;
  reverts never unregister a tool.
- **No-progress**: an iteration with zero applied ops increments the streak; two consecutive ⇒ best-effort exit (§7).

## 5. Whiteboard state and ops (spec §4.2, §12.15–12.16)

State `Whiteboard`: `inspirations[{archive_id,status,feedback_summary}]` (read-only),
`functions[{id F<n>,text,author}]`, `concepts[{id C<n>,function_id,text,author,status: open|favored|dropped}]`,
`evidence[{id E<n>,author,tool,purpose,code_or_query,inputs,output_summary,output_full,sketch_path,status: ok|error,cycle}]`
(**written by code only, when a tool runs; members cannot edit/delete**),
`objections[{id O<n>,author,target_id,text,blocking,status: open|resolved,resolution,evidence_ids[]}]`,
`proposal{version,author,text,concept_ids[],key_claims[{claim,evidence_ids[]}]}|null`,
`votes{member:{version,ready,reason}}`, `closure{closed_by,cycles_used,open_blocking[]}`.

Ops (only write path; `action` ∈ `add_function, add_concept, set_concept_status, raise_objection,
resolve_objection, update_proposal, vote, read_evidence`). Code validates: referenced ids exist, `author`
is the caller, a resolution cites ≥1 evidence id or gives a reason; errors return as tool-output text.
`update_proposal` increments `version` and **clears all votes**. Evidence requests from the Evaluator are
pinned by code as open blocking objections authored `"Evaluator"`.

Rendering (`whiteboard.md`, shown to every member on every turn): dropped concepts / resolved objections
render as one line; evidence as one summary line (`E7 [calc, Mechanics] cantilever tip deflection = 0.42 mm (ok)`);
full output via `read_evidence`. Code warns in `trace.md` when rendering exceeds ~30k tokens (chars/4).

Tools (`tools.py`): every `calc`/`simulate`/`sketch`/`web_search`/`new_tool` result is auto-posted as
evidence by code; tool output starts with the new evidence id (`"E12: 0.42 millimeter"`).
`calc` inputs are parsed from `Q_(...)` literals. `sketch` PNG is shown to the calling member in the same
request (fallback two requests, §14.3); ≤4 newest sketches go to other members next turn.
`new_tool`: sandbox smoke test must pass; cap `MAX_NEW_TOOLS=2` per problem; injected from next turn.

## 6. Meeting closing rule (spec §4.3, deterministic code)

- Turn = one member speaks (fresh Responses chain per turn, `previous_response_id` inside the turn only;
  `instructions` resent; input = whiteboard render + transcript since member's last turn + own previous
  message). Caps: 6 counted tool calls/turn (`whiteboard` calls excluded, own cap 8); from the 5th counted
  call `parallel_tool_calls: false`; at cap, pending calls get `"tool budget exhausted — write your message now"`;
  if the model still only calls tools, take the last `message` text and log it. Message ≤250 words. Effort medium.
- Cycle = every member once; cycle `c` starts with member `c mod n`. `MIN_CYCLES=2`, `MAX_CYCLES=4` (clamped).
- **Close check after every turn once `min_cycles` cycles complete** — `closed_by="consensus"` iff:
  (1) a proposal exists; (2) every member's latest vote is `ready: true` for the current proposal version;
  (3) no open objection has `blocking: true`.
- After `MAX_CYCLES`, if a proposal exists without consensus: one **vote-only round** (only `vote` and
  `raise_objection` allowed, no `update_proposal`); consensus there ⇒ `"consensus"`. Otherwise
  `closed_by="cap"`; open blocking objections are copied into `SolutionPrompt.open_questions` and flagged
  to the Evaluator (which then forces `accept=false`).
- Manager never speaks; it reads transcript + `whiteboard_history.jsonl` + per-member stats.
  Secretary (high effort) synthesizes `SolutionPrompt` from final board + transcript, copies evidence ids
  into `key_estimates[].evidence_ids`, adds nothing not on the board.

## 7. FakeClient scripts — every branch exercised offline

`FakeClient` is deterministic and scenario-driven (`HS_FAKE_SCENARIO` / `Controller(scenario=...)`;
default `happy`). Synthetic `usage` on every call so `cost.json` is non-zero with zero network.

| Scenario | Script (what FakeClient returns, in order) | Branch proved |
|---|---|---|
| `happy` (default demo) | Meeting closes by consensus in cycle 2 (members add F/C, `calc` evidence, proposal v1, all `ready`); Evaluator iter 0 `accept=false` + one evidence request → Manager rewrite (§4 text) → iter 1 meeting resolves the pinned Evaluator objection, Evaluator `accept=true`; Stage B round 0 S1 fail → round 1 S1 pass, S2 no | reject → edit → accept; S1 retry → pass; `diff_001.md` shows only rewritten sections |
| `cap` | Members never all vote ready; an open blocking objection survives `MAX_CYCLES` + vote-only round | `closed_by="cap"`, objection copied to `open_questions`, Evaluator forces reject |
| `revert` | Iter 0 reject; iter 1 reject with `same_problem_as_before=true`, `revert_sections=[{§4, to rev 0}]`; optimizer then rewrites only §4; iter 2 accept | only the named section reverts |
| `guard` / `shrink` (unit tests) | Optimizer returns a rewrite deleting a fixed criterion / shrinking §4 by >50% | guard re-ask then old text kept; shrink re-ask applied second time |
| `schematic_fail` | `SchematicSpec` references a missing part / disconnected graph on both the call and the re-ask | `rejected_by_designer`, `returns_to_A` +1, back through Manager |
| `s1_three_fail` | S1 fail ×3 (`MAX_S1_ROUNDS`) → `s2_return` with "render never matched" feedback → Stage A iter accepts again → S1 pass | `s1_retry ×3 → s2_return → Stage A → s1_pass` |
| `s2_flaw` | S1 pass but `s2_flaw=true` with concrete image feature | `s2_return` via designer feedback |
| `evidence_request` | Evaluator iter 0 `accept=false` with `evidence_requests[1]` | pinned blocking objection keeps next meeting open until a member resolves it with evidence |
| `cost_cap` | Synthetic `usage` priced above `MAX_COST_USD_PER_RUN` on an early call | `BudgetExceeded` raised **before** the next call; best-effort figure + report still written |
| `no_progress` | Optimizer returns empty `sections` twice | two consecutive `no_progress` ⇒ best-effort exit |

Placeholder images: Pillow-generated PNGs (labelled blocks, distinct colour per call) for renders,
close-ups and fabrication panels; schematic/annotation use the real deterministic code path.

## 8. Controller caps & run folder (spec §7, §10)

`MAX_A_ITERS=8, MAX_S1_ROUNDS=3, MAX_B_RETURNS=2, MIN_CYCLES=2, MAX_CYCLES=4, MAX_MEMBERS=5,
MAX_TOOL_CALLS_PER_TURN=6, MAX_TURN_MESSAGE_WORDS=250, MAX_NEW_TOOLS=2, MAX_FIGURE_IMAGES=8,
MAX_COST_USD_PER_RUN=15.00` — all in `config.py`, CLI-overridable; cost checked **before every call**.
Run folder exactly as §10 (`master_prompt/`, `stage_a/iter_NN/`, `stage_b/attempt_NN/round_NN/`,
`final/`, `trace.md`, `cost.json`, `report.html`, `board.html`). `Report.write` runs on **every** exit path.

## 9. Per-role model configuration (user requirement)

One `RoleConfig` entry per role in `config.py` — `model`, `reasoning effort`, `max_output_tokens` —
so any role can be switched to another model or higher effort with no code change:

| Role | Model | Effort | Max tokens |
|---|---|---|---|
| member (per turn) | muse-spark-1.3 | medium | 8000 |
| secretary | muse-spark-1.3 | high | 16000 |
| prior-art check | muse-spark-1.3 | low | 4000 |
| evaluator | muse-spark-1.3 | high | 12000 |
| manager-inspirations | muse-spark-1.3 | low | 2000 |
| manager-gradients | muse-spark-1.3 | high | 12000 |
| optimizer | muse-spark-1.3 | medium | 8000 |
| schematic spec | muse-spark-1.3 | medium | 8000 |
| VLM writer | muse-spark-1.3 | medium | 4000 |
| localization | muse-spark-1.3 | low | 4000 |
| designer eval | muse-spark-1.3 | high | 8000 |
| light check | muse-spark-1.3 | low | 2000 |
| lessons | muse-spark-1.3 | medium | 4000 |
| example generator | muse-spark-1.3 | medium | 8000 |
| master-prompt rev0 | muse-spark-1.3 | medium | 8000 |

## 10. Milestones (spec §11)

- **M0** scaffold + client + fake mode + schemas/sandbox. **M1** Stage A. **M2** Stage B.
  **M3** figure + lessons + CLI/report/board. **M4** (real runs) is **out of scope for this session**:
  smoke tests written, not run; exact commands in `CHECKPOINT.md`.
- Spec changes, if forced by implementation: separate `SPEC:` commits + one `SPEC_CHANGES.md` entry each.
  Architecture intent is never changed silently. `examples/` is never edited.
