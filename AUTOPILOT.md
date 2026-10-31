# AUTOPILOT.md — standing instructions for autonomous work

Read this file, AGENTS.md and HARDWARE_SCIENTIST_SPEC.md before acting. Work without asking the owner anything until a stop condition is met. Keep `JOURNAL.md` as a chronological log: `[YYYY-MM-DD HH:MM] what I did · what I found · what I changed · runtime cost so far`.

---

## 1. Definition of done (all must hold)

1. The three examples in `examples/` have each been run **for real** (muse-spark-1.3 / muse-image-1.0) end to end, in order 01 → 02 → 03, with: a whiteboard meeting that contains real calculations, simulations and sketches; written evaluator feedback; at least one Master-prompt rewrite where the evaluator rejected; Stage B renders; a final concept figure; `report.html`; `board.html`; and `hs compare` over the three runs.
2. Every visual a human will see is **presentation-grade** (§4) and has been checked by you as an image, not only as code.
3. `REVIEW.md` exists in each final run folder and `SUMMARY.md` at the root (§6).

## 2. Work loop

1. Run the real smoke tests (`HS_SMOKE=1 .venv/bin/python -m pytest tests/test_smoke_real.py -q`); fix until they pass; record every settled spec §14 item in QUESTIONS.md.
2. Run one example for real. Inspect the whole run folder yourself: trace, transcripts, whiteboard history, evidence, verdicts, diagnoses, prompt diffs, cost.json and **every image (open and look at it)**.
3. Write `runs/<id>/REVIEW.md`: what worked; what is broken or weak; root cause; fix. Check at least: crashes or malformed outputs; shallow whiteboard (few or trivial calculations); members repeating each other; meetings that always hit the cap; vague evaluator feedback; prompt rewrites that change nothing meaningful; renders that ignore the schematic or hide the working interface; unreadable labels; cost hotspots.
4. Fix, commit each fix as `FIX: …`, re-run only when needed. Then the next example.
5. Do the visual work in §4 (it costs almost nothing) and re-render the reports of finished runs (`hs report`, `hs board`) without re-running the models.

## 3. Forbidden shortcuts (never do these, even under time or budget pressure)

- Never make a run "pass" by weakening judgment: do not loosen the evaluator, the designer evaluation, the closing rule or the guards; do not lower caps to finish faster; do not skip review loops.
- Never collapse the council into a single call, remove the whiteboard, or replace member turns with templated text in real mode.
- Never ship placeholder, fake-mode or matplotlib-box images as final visuals; never show fake data in a real run.
- Never add hand-written domain hints, rubrics, expected answers or example-specific code. Never edit `examples/`.
- Spec changes only as `SPEC: …` commits with a SPEC_CHANGES.md entry; keep the architecture's intent (council on a shared whiteboard, written feedback, Manager rewriting the master prompt, Stage B schematic → render → review S1/S2).
- Work only inside this folder.

## 4. Visual quality bar

References in `docs/design/` define the bar. Match or beat them.

- **Final concept figure (panel A)** — `ref_render_bathscope_v1.png`, `ref_render_bathscope_v2_labeled.png`: realistic, rendered, descriptive product-style illustration on a light background; materials and depth appropriate to the use; the device shown **in its operating moment** with the workpiece/sample present; fixed vs moving parts and the force/signal path visible; concise callouts with leader lines; a small inset for motion or the critical interface; a footer line "Conceptual illustration — physical performance not established".
- **Force-flow view** — `ref_force_flow_overlay.png`: a second view of the same render with translucent arrows tracing the load path (drawn by code over the render, or requested from the image model; verify).
- **Deliverable layout** — `ref_deliverable_layout.png`: title, one-sentence working principle, the image, **three decisive design choices**, **one important open question**, and a "next iteration" box. Use this as the top of `report.html`.
- **Whiteboard** — `board_mock.png` / `board_mock.html`: board.html must look like this (fonts, rough.js marker style, sticky notes, member colours, boxed hand-written calculations with evidence ids, red objection circles, proposal frame, subtitle bar, working step-by-step replay). Member sketches must look hand-drawn on the board (matplotlib xkcd + handwriting font, or restyled once with muse-image as "whiteboard marker drawing", labels added by code).
- **Reference sketch for Stage B** — `ref_reference_sketch_two_states.png`: the code schematic shows the actual mechanism (side/top/section), the workpiece, contact anchors, fixed vs moving, and optionally two operating states (initial / operated). Never a flowchart of boxes.
- Check every visual yourself: render HTML pages to 1920×1080 PNGs with headless Chromium (Playwright) and look at them; iterate until they meet the bar. Save final screenshots to `docs/screens/`.

## 5. Model and cost tiering (configure in config.py)

- **High quality where a human looks or a decision is made:** Secretary, Evaluator, Manager, Designer evaluation, VLM prompt writer → muse-spark-1.3, effort high. Final renders and key-moment visuals → muse-image-1.0, reasoning_strength high. Images cost $0.01 each: generate as many as quality needs (e.g. one render per Stage B round, panel B/D renders, sketch restyling).
- **Cheap inner loops:** schematic spec, localization, light checks, inspirations, lessons → effort low; member turns → medium.
- Budget for real system runs in this session: **60 USD total** (sum of cost.json). Each run keeps its own cap.

## 6. Stop conditions and hand-off

Stop when (a) the definition of done holds, (b) the 60 USD runtime budget would be exceeded, or (c) the same failure survives three fix attempts. In (b) or (c) write `BLOCKED.md` with the exact problem. Always finish with `SUMMARY.md`: runs that exist (paths to report.html, board.html, compare page), what changed and why, total runtime cost, open problems, and the three screenshots that best show the system.

---

## 7. Improvements adopted from the owner's earlier prototype (ChatGPT/Codex "Concept Studio")

Implement these as part of the work above. Delete any line the owner does not want before starting.

1. **Image model may draw its own labels and callouts.** muse-image-1.0 produced clean, legible callouts in the reference renders. Replace the spec's "no text in the image" rule with: the VLM prompt asks for brief callouts for the 4–7 focus parts; Designer evaluation S1 also checks that every label names the right part and is spelled correctly; if labels are wrong twice, fall back to a clean render + code overlay. (SPEC change: record it.)
2. **Structured visual plan in the VLM prompt:** view; spatial layout; operating moment; force/motion/signal transfer path; 2–7 focus parts with material and purpose; real interactions between them; an `avoid` list; and, after a failed review, a "targeted corrections from actual-image review" block appended verbatim.
3. **Pixel-first review:** the Designer evaluation first describes what it actually sees in the image, before reading the concept; a label alone never proves a connection. It reports, for each requirement, observed / ambiguous / missing, and names the stage that caused each fault (meeting, schematic, prompt, render).
4. **Deliverable summary:** the Secretary also writes `mechanism_sentence`, `decisive_choices` (exactly 3) and `open_question` (exactly 1), plus one line "Force: A → B → C | Measured: D → E". These head `report.html` (§4 deliverable layout).
5. **Research by expertise and character:** each member searches the literature the way its persona (Master prompt §2) implies — its own domain's directly relevant papers, standards and datasheets, and neighbouring or distant fields where a transferable principle may exist. This is driven by the persona text, not by a fixed quota. When a member borrows from another field, it states on the whiteboard why the principle should transfer.
6. **Vetted calculators next to free calc:** add small named functions the members can call (`lever_effort`, `lead_screw_effort`, `cantilever_deflection`, `spring_mass_frequency`, `first_order_settling`, `natural_convection_plate`, `tuned_mass_damper_den_hartog`), each recording which inputs came from the user, a source or an assumption.
