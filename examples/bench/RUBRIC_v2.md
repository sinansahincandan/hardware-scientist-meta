# Benchmark rubric v2 (2026-11-03, owner's additions, written before any v2 result was seen)

Same use as RUBRIC.md: an independent judge (a Claude agent that does not know which system made which design) scores
each design 1–5 per criterion with one or two sentences of reasons, then names the better design. Hardware Scientist
never uses scores itself. v2 keeps the five criteria of v1 and adds three the owner named: how well the working
principle is explained, how the device would be made, and whether the picture is free of the usual image-generator
mistakes. Both systems are asked for the same deliverables (design text with a "how it is made" section, and pictures).

| Criterion | 5 means | 1 means |
|---|---|---|
| C1 Meets the constraints | every stated constraint is met, shown with numbers that add up | constraints ignored or claimed without support |
| C2 Physically works | the working principle is sound; nothing violates physics; every function has a part | a step cannot work, or a function has no part doing it |
| C3 Numbers are right and supported | the judge re-derives the deciding numbers and they hold; values have a stated basis | key numbers are wrong, inconsistent or unexplained |
| C4 Picture shows the design | a viewer can see the parts and how it works, and the picture matches the text | picture contradicts the text or does not show how it works |
| C5 Buildable and honest | buildable with real parts; risks and open questions are stated honestly | hand-waving, unrealistic parts, risks hidden |
| C6 Explains how it works | a non-specialist can follow the working principle step by step, from what goes in to what comes out | the principle is vague, jargon-only, or missing a step |
| C7 Tells how to make it | the making stages and methods are concrete and in a sensible order for real parts and shops | no making information, or stages that could not produce the device |
| C8 Picture free of generator mistakes | no wrong counts (blades, wheels), floating or merged parts, impossible joints, wrong scale, garbled text or logos | one or more such mistakes that mislead about the device |

Rules for the judge: check the arithmetic yourself; a confident claim without support scores lower than a modest
claim with support; do not reward length; judge each design on its own before comparing; never guess which system
made which design; look at every picture you are given.

Measured separately (not judged): wall-clock time and Meta API cost per design.
