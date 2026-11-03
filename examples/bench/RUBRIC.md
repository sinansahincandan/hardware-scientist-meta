# Benchmark rubric (written before any result was seen, 2026-11-03)

Used by an independent judge (a Claude agent with no access to which design came from which system). Hardware
Scientist itself never uses scores; this rubric exists only to compare it with a single prompt, as the owner asked.

For each problem the judge receives the problem (exactly as given to both systems) and two designs, A and B, each a
design document with the same headings and one picture. The judge scores each design 1–5 on each criterion, with one
or two sentences of reasons that point at the document or the picture, then names the better design overall.

| Criterion | 5 means | 1 means |
|---|---|---|
| C1 Meets the constraints | every stated constraint is met, shown with numbers that add up | constraints ignored or claimed without support |
| C2 Physically works | the working principle is sound; nothing violates physics; every function has a part | a step cannot work, or a function has no part doing it |
| C3 Numbers are right and supported | the judge re-derives the deciding numbers and they hold; values have a stated basis | key numbers are wrong, inconsistent or unexplained |
| C4 Picture shows the design | a viewer can see the parts and how it works, and the picture matches the text | picture contradicts the text or does not show how it works |
| C5 Buildable and honest | buildable with real parts; risks and open questions are stated honestly | hand-waving, unrealistic parts, risks hidden |

Rules for the judge: check the arithmetic yourself; a confident claim without support scores lower than a modest
claim with support; do not reward length; judge each design on its own before comparing; never guess which system
made which design.

Measured separately (not judged): wall-clock time and Meta API cost per design.
