# QUESTIONS.md — assumptions, defaults, unverified API items

Every assumption is recorded here with the default chosen; work continues without waiting (spec §0.2).

## Assumptions (default chosen)

1. **Member-turn implementation.** Spec §4.3 describes a Responses tool loop per turn. *Default:* the
   pipeline calls `client.member_turn(...)`, which in `MetaClient` runs the real tool loop
   (`previous_response_id` chaining, caps, `parallel_tool_calls: false` from the 5th counted call) and in
   `FakeClient` runs a deterministic scripted sequence against the real `Whiteboard`/`tools` code.
   Rationale: keeps fake mode offline-deterministic while exercising the same board/tool/evidence code.
2. **`web_search` in fake mode.** No network. *Default:* `FakeClient` returns one synthetic citation
   (`https://example.org/fake-source`) and `tools.web_search_evidence()` posts it as evidence like the real path.
3. **Sketch visibility plumbing (§14.3).** *Default:* implement the primary shape (tool output + user
   `message` with `input_image` in one request); the two-request fallback is a config switch
   (`SKETCH_SINGLE_REQUEST=False` path) exercised only in code, not in fake tests.
4. **Image size string.** §5.3 says `size` is "aspect only". *Default:* pass the schematic's pixel aspect
   as `"<W>x<H>"` (e.g. `1536x1024`); smoke test §14.4 settles the accepted form.
5. **`lessons.md` location.** Spec §2 puts it at repo root; runs may execute from another cwd.
   *Default:* resolved relative to the current working directory, overridable with `HS_LESSONS_PATH`.
6. **Run id.** `runs/<YYYYMMDD-HHMMSS>_<slug>/` local time; slug = problem title, lowercased,
   non-alphanumerics → `-`, max 40 chars. Collisions get `-2`, `-3`, … suffixes.
7. **`hs examples` output.** Spec §8 shows `examples/gen_<timestamp>_<n>.json`; *default:* one file per
   generated problem: `examples/gen_<timestamp>_<i>.json` (never overwrites; shipped 01–03 untouched).
8. **Cost conversion.** Prices from §9 (`muse-spark-1.3` $1.25/$0.15/$4.25 per 1M; search $2.50/1000;
   image $0.01). Cached-input tokens are billed at the cached rate; reasoning tokens are part of output
   tokens for billing and also logged separately. *Default* in `config.py:PRICES`, editable.
9. **Fake synthetic usage.** Every fake call logs fixed synthetic usage (e.g. 1200 in / 300 out) priced
   through the same code path as real calls, so `cost.json` is non-zero offline. Scenario `cost_cap`
   inflates usage to prove the pre-call `BudgetExceeded` check.
10. **Scenario selection.** `HS_FAKE_SCENARIO` env var, else `Controller(scenario=...)`, else `happy`.
    Tests pass the scenario explicitly; the CLI default run uses `happy`.
11. **Board/report images.** Self-contained HTML embeds base64 by default; `--no-embed` writes relative
    paths (spec §8). Board `--live` rewrites `board.html` after every turn with a 5 s meta-refresh.
12. **Master-prompt rev0 in fake mode.** `FakeClient` returns a deterministic Markdown document with the
    six headings and 3 members (Mechanics / Thermal-Fluids / Fabrication for the stair-cart fixture
    shape; generic domains otherwise) so heading-split and roster code run unchanged.

## Unverified API items (spec §14) — settled 2026-10-31 (real API)

- **14.1 SETTLED (pass).** `HS_SMOKE=1 pytest tests/test_smoke_real.py` → 2 passed. The §9 `text.format` nesting works as implemented.
- **14.2 SETTLED (accepted).** Probe (`/tmp/smoke_probe.py`): first `web_search` call returned `web_search_call` items; a chained call with `previous_response_id` + `include: ["web_search_call.results"]` succeeded. Code still relies on `url_citation` annotations only (include stays opt-in, off).
- **14.3 OPEN.** The real member-turn loop returns sketch tool output as text only; the `function_call_output` + user `input_image` single-request shape is not exercised by `council.py`. Sketch PNGs are saved as evidence and shown on the board. Default chosen: keep text-only return, record here; revisit if run reviews show members cannot use sketches.
- **14.4 SETTLED (accepted, fidelity weak).** Toy 3-box schematic → `/v1/images/edits` with `tool_enablement`/`reasoning_strength` accepted (no 400). The render preserved the 3 parts + connections but copied the flat schematic style instead of a rendered illustration. S1 exists for exactly this; real concept prompts are richer. Fallback `IMAGE_BACKEND="responses"` remains available.
- **14.5 SETTLED (usable).** Localization on the toy render found all 3 parts (confidence 0.8). Code-label readability was poor with the default bitmap font — fixed in `annotate.py` (TrueType scaled font, white label backing).
- **14.6 NOT NEEDED** by design (searches in turns, structured output separate). Untested.
- **14.7 PARTLY OPEN.** Prices/limits taken from spec §9 in `config.py`; dashboard credit not checked (no dashboard access in this session). The $15/run cap and $60 session budget bound the exposure.
  *Update 2026-11-02:* the user reported $67 credit left on the dashboard and asked for a $50 limit. The Meta docs list no balance endpoint (dashboard only); `/docs/error-handling` documents HTTP 402 `billing_error` for billing problems. *Default chosen:* a cross-run ledger (`spend_ledger.json`, `MAX_TOTAL_SPEND_USD = 50.00`) starts at $0 on 2026-11-02; earlier runs ($23.51 logged) are not counted in it. 402 now raises `BudgetExceeded`. Two undercounts were fixed at the same time: a truncated structured reply that was re-asked was not recorded, and hosted `web_search_call` items were never priced.
- **14.8 SETTLED.** Truncation probe printed `status=incomplete incomplete=IncompleteDetails(reason='max_output_tokens')`. The defensive detection in `client.py` (status != completed) covers this shape.

## Unverified API items (spec §14) — previous status: NOT RUN (fake mode only, superseded above)

Smoke tests are written under `tests/test_smoke_real.py` (skipped unless `HS_SMOKE=1` + `MODEL_API_KEY`).
Exact commands are listed in `CHECKPOINT.md`. Nothing in the implementation relies on an unverified
shape without a fallback:

| # | Item | Fallback in code |
|---|---|---|
| 14.1 | `text.format` JSON-schema nesting on `/v1/responses` | `MetaClient.structured()` isolates the shape in one place; a 400 body must be pasted here and the shape fixed + regression-tested |
| 14.2 | `include: ["web_search_call.results"]` with `previous_response_id` | Code relies on `message.annotations[].url_citation` only; results-include is opt-in config, off by default |
| 14.3 | `function_call_output` + user `input_image` in one request | Two-request fallback behind `SKETCH_SINGLE_REQUEST` |
| 14.4 | `tool_enablement`/`reasoning_strength` on `/v1/images/edits`; reference fidelity | `IMAGE_BACKEND="responses"` fallback backend implemented |
| 14.5 | Localization quality (0–1000 grid) | Fallback: labels at schematic grid positions scaled to the render |
| 14.6 | `web_search` + `text.format` in one request | Not needed by design (searches in turns, structured output separate) |
| 14.7 | Current prices / limits / remaining credit | Prices centralised in `config.py`; check dashboard before M4 |
| 14.8 | Truncated-response shape (`status`, `incomplete_details`) | Defensive detection (status / token ceiling / JSON parse) + one doubled-token retry |

## 2026-11-01 — image edit HTTP 400 with swallowed body (stageb rerun 03)
Stage B rerun of example 03 died in round 02 at POST /v1/images/edits with
HTTP 400 after two successful rounds. The client retry loop raised only
`HTTPError: 400 Client Error` and discarded the response body, and
round_02's vlm_prompt.json was written only after the image call, so the
exact failing prompt was lost. Fixes: client now raises immediately on
HTTP >= 400 with the body in the message (no blind retries of a
deterministic rejection); vlm_prompt.json is saved before the image call
in both the controller and the Stage B rerun. If the 400 recurs, the body
will be in the traceback; record it here verbatim and adjust the request.
Assumption until then: transient/content-filter rejection of that round's
prompt, since rounds 00-01 with the same shape succeeded and a probe with
the round-00 schematic + test prompt returns 200.

## 2026-11-01 — content-filter 400 killed a run at the evaluator
Full error body: `Error code: 400 - The response was filtered due to the
prompt triggering our content management policy.` (openai.BadRequestError,
Responses API, evaluator free_text call in run 20261101-160854, iteration 2.)
The same council content passed dozens of earlier calls, so this is a
stochastic provider filter, not a request-shape error. Fix per the rule:
`_create_with_retries` now retries a 400 whose body mentions the content
management policy (like a 429, 3 attempts with backoff); all other 400s
still raise immediately. Covered by tests/test_image_edit_errors.py
(test_content_filter_400_is_retried, test_plain_400_still_raises).

## 2026-11-02 — SAM 3.1 smoke test (round 3, item 16) — SETTLED (boxes), masks undecoded

Calls (runs/meta_check_20261102-014036, runs/sam_probe_20261102-020841; $0.0025 each, 3 calls):
- Shape that works: `POST /v1/responses`, `model: "sam-3.1"`, `stream: true`, one user message with
  `input_text` = a short noun phrase and `input_image` = PNG data URL (sent at ≤ 1024 px long side);
  optional `metadata: {"mask_encoding": "one_bit"}` accepted. Implemented in `MetaClient.sam_segment`.
- Output: `response.output_text.delta` text, one comma-separated record per match:
  `<0f>{id}<|box;x1=..;y1=..;x2=..;y2=..;w=..;h=..|><|mask;x=0;y=0;data=H,W,!<base85 body>|>`
  (inclusive pixel box on the image as sent; mask raster H×W covers the box). Zero matches → empty
  text and no delta event (seen on the first call; not an error).
- Usage: `input_tokens=0, output_tokens=0, images_processed=1` → priced per image ($2.50/1000).
- Phrase sensitivity (decisive): on a photo of one red brushed-metal disk, "metal disk" → 0 matches,
  "red disk" → 1 correct box (285,311)-(729,718) of 1024². Part names must be mapped to plain visual
  phrases (colour, material, shape) before SAM sees them.
- Box prompts: documented (`<0f>1<|box;...|>`); not tested (not needed for measuring).
- Masks: the body is arithmetic-coded base85 (protocol/sam3.md in github.com/meta-models/meta-sam);
  decoding needs Meta's `meta-sam-parser` package. Installing it was refused by the session's
  permission system (BLOCKED.md). *Default chosen:* measure from SAM boxes only (count, centre,
  size, box aspect, size ratios, box contacts); no mask angles, no mask composite.

## 2026-11-02 — content filter on fabrication-step checks (problem 02)

Meta's content filter (HTTP 400 "…triggering our content management policy") blocked the light check on
fabrication-step images of problem 02 in two runs. Probe (runs/filter_probe, ~$0.04): the same saved images
passed with neutral wording, so the trigger is in the text, not the image; stripping numbers, units and
product codes ("150V 60A", "48V 100Ah LiFePO4") let step 2 pass the detailed check, but steps 3 and 5 stayed
blocked even with a general question. The filter cannot be inspected or switched off by us.
*Decision (owner, 2026-11-02):* numbers stay as references in prompts, but are not enforced strictly; a
blocked request is taken as a reason to re-word: the client retries it once with numbers, units and codes
removed (every Responses call and image edit; `content_filter_retry_plain` marker in cost.json); a step check
blocked after that falls back to one general check (caption "(general check only)"); blocked again → not shown.

## 2026-11-02 — owner decisions for round 4 (see SPEC-11)
S1 exhausted → Manager "reported as such" (Fig. 1); image-model callouts checked by SAM + judges with code
fallback (Fig. 2); meta-sam-parser installed; Evaluator reviews each constraint in prose and may relax one with
a reason (no scores).

## 2026-11-03 — Why the content filter blocked the concept sketch of run 02 (owner asked) — SETTLED

What is sent: every image request carries the text prompt plus the reference images in the same call
(`POST /v1/images/edits`, `images` array: concept or council sketch first, then further sketches and the parts drawing),
with `reasoning_strength: "high"`.
Probes (scratchpad, $0.08 then $0.03): in run 02 the concept prompt was blocked, and blocked again after the number-free
re-word; in a first reproduction each part of the prompt passed alone and the combination was blocked; the three council
images passed alone. Later the same combined prompt — and two variants without the battery words or the mechanism
sentence — all passed. The same request is therefore blocked at one time and passed at another: the filter is not keyed
to fixed words in our text (most likely it screens the model's own generated reasoning or output, which differs per
call). *Default chosen:* keep the client's number-free re-word and the plain second wording (redraw the hand sketches,
plain part names); a block ends one try, never the step.

## 2026-11-03 — SAM box prompts — SETTLED (verified)

`<0f>1<|box;x1=..;y1=..;x2=..;y2=..;w=W;h=H|>,2<|box;...|>` (docs /docs/sam/segmenting): up to 16 objects in one call;
coordinates on the image as sent (long side ≤1024 px). `metadata: {"include_confidence": "true"}` adds `c` per box and
mask. Probe on run 04's render: 4 of 5 box-prompted parts returned masks with confidence 0.67–0.89. Used for parts no
phrase finds (part_map.measure), followed by the mask judge.

## 2026-11-03 — What web search returns — SETTLED (verified)

Meta's hosted web search is agentic: `search` actions return results with title and URL and an EMPTY snippet;
`open_page` and `find_in_page` actions read pages (no results field); the reply carries `url_citation` annotations with
`start_index`/`end_index` into the reply text. *Default chosen:* evidence = each cited source with the sentence the
member wrote from it (the annotation span) and whether the member opened the page; uncited results at most two per
query, marked "not opened or cited". `search_context_size` raised from low to medium for members.
