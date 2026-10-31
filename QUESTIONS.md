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

## Unverified API items (spec §14) — status: NOT RUN (fake mode only this session)

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
