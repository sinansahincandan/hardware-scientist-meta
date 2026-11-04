# Benchmark rubric v3 (2026-11-04, owner's addition, written before any v3 result was seen)

The owner's concern after round 4: a design can look good at first sight and still break in the details (numbers
that do not add up, a picture that contradicts the text, a step that cannot work with the drawn geometry). v3 keeps
the eight criteria of v2 unchanged and adds a **fault audit that comes before any score**. Hardware Scientist never
uses scores itself; this rubric is only for the outside judge.

## Phase 1 — fault audit (for each design, on its own, before scoring)

Read the whole design text and look at the picture at full size. List every concrete fault you can find, each with
where it is, what is wrong, and how you checked it. Look at least for:

1. **Numbers** — re-derive every deciding number (masses, forces, stresses, power, energy, times, sizes). A sum that
   leaves out parts, a unit slip, a value that does not follow from its own stated inputs.
2. **Constraints** — every constraint said to be "met": is it shown with a computed value, or only claimed?
3. **Physics with the drawn geometry** — can each working step happen with the parts where they are drawn (soil that
   would have to jump a gap, a load path through nothing, a cable that cannot reach)?
4. **Text against picture** — part counts (blades, wheels, legs), what touches what, orientation and direction of
   flow or motion, size against the scale bar or the person/hand in the picture.
5. **Image-generator mistakes** — floating or merged parts, impossible joints, wrong counts, garbled text or logos.
6. **Contradictions** between sections of the same design.

Give each fault a severity:
- **fatal** — the concept would not work as described, or a stated constraint is actually violated;
- **major** — a wrong or unsupported number, or a picture error, that would change an engineer's decision;
- **minor** — cosmetic or easily fixed without changing the design.

## Phase 2 — scores (1–5 per criterion, one or two sentences each)

Same criteria as v2: C1 meets the constraints · C2 physically works · C3 numbers right and supported · C4 picture
shows the design · C5 buildable and honest · C6 explains how it works · C7 tells how to make it · C8 picture free of
generator mistakes. The audit binds the scores:
- a criterion touched by a **major** fault scores at most 3;
- a **fatal** fault caps C2 at 2 (and C1 at 2 if it is a violated constraint);
- polish, confident tone, length and an attractive render earn nothing by themselves; a picture that looks good but
  contradicts the text is scored by the contradiction.

Rules from v2 stay: judge each design on its own before comparing; never guess which system made which design;
look at every picture; do not reward length.

Measured separately (not judged): wall-clock time and Meta API cost per design.
