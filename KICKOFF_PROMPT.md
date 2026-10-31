# Kickoff prompt for Muse Code

## One-time setup (terminal)
```
mkdir hardware_scientist && cd hardware_scientist && git init && mkdir docs
# unzip the hand-off: AGENTS.md, HARDWARE_SCIENTIST_SPEC.md, EXAMPLE_PROBLEMS.md in ./, the two PNGs in ./docs/, the three JSONs in ./examples/
export MODEL_API_KEY=...          # from dev.meta.ai — used by the hs program, not by Muse Code itself
muse --model muse-spark-1.3 --reasoning-effort high
```
- Muse Code loads project rules (`AGENTS.md`) only after you **trust the workspace** — accept the trust prompt (or start with the trust flag your version offers; see `muse --help`).
- If real smoke tests fail with a network error from inside the agent's sandbox, start Muse Code with its network-enabled sandbox flag (see `muse --help`, `--sandbox-network`) or run those smoke tests yourself in a normal terminal.
- `muse --model muse-wonder-1.0` is a valid choice for PLAN.md and tricky debugging if your account has access; default to `muse-spark-1.3` for the bulk of the coding (5× cheaper).

## Paste into Muse Code
```
Read AGENTS.md, HARDWARE_SCIENTIST_SPEC.md and EXAMPLE_PROBLEMS.md completely, then look at docs/fig1_architecture.png and docs/fig2_visualization_pipeline.png.

Goal: implement the Hardware Scientist system exactly as specified, milestone by milestone (spec §11, M0 → M4). Working end-to-end in fake mode comes before any real API call; real calls only in the smoke tests named in §11 and in M4.

Before writing code, write PLAN.md: the module list from spec §2, the pydantic schemas from §12 (with the shared enums), the strict-schema post-processing rules from §9, the Markdown Master prompt with its heading split, rewrite guards and shrink check (§3.2), and the whiteboard state and ops (§4.2, §12.15–12.16), the meeting closing rule (§4.3), and the FakeClient scripts needed to exercise every branch (meeting closes by consensus / by cap; reject → edit → accept; Manager marks a repeated problem → one section reverted; schematic-check failure; S1 retry ×3 → S2 return → Stage A → S1 pass; cost cap hit via synthetic usage). Then start M0.

Rules: Responses API only; field names from spec §9; feedback is free text, structured output only for the yes/no decisions the controller reads; no text drawn by the image model; caps enforced in config.py; cost cap checked before every call. Do not ask me questions — put each assumption with your chosen default in QUESTIONS.md and continue. After each milestone: pytest -q, hs run --fake examples/01_stair_cart.json, then CHECKPOINT.md.

Unverified API details are listed in spec §14. Settle each one with the smoke test named in §11 and record the result (request shape that worked, or the 400 body) in QUESTIONS.md.

M4 runs the three shipped examples for real in order 01 → 02 → 03 and then `hs compare`. When M4 is done, stop and give me: the three commands to verify, the paths to the three report.html and board.html files and the compare page, the measured cost, and the §14 findings.
```

## After hand-off (you)
```
open runs/<id>/report.html                     # evolution of one problem
open runs/compare_<timestamp>.html                              # the three problems side by side
open runs/<id>/board.html                      # replay the council's whiteboard
hs run examples/02_solar_cold_room.json      # re-run one after you change something
hs feedback "<what the architecture missed>"     # goes to lessons.md ## User feedback
```
