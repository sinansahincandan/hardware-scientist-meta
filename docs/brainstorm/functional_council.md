# Brainstorm: should the council be split by function, and should members advise rather than decide?

2026-11-03. Owner's questions after reading Kate Fu's papers and his own METU ME407 teaching (report:
`ME407_FALL2022_FR_C1.pdf`, Vestel oven tray; method from Dieter & Schmidt, *Engineering Design*, 3/e pp. 175–177).
Three Opus reading reports (ME407 report, Fu et al., Dieter / Pahl & Beitz) are summarised in the Sources section;
this assessment is mine (Fable), checked against HS's code and its real runs.

## 1. What HS does today (facts from code and runs)

- **It already decomposes into functions.** Cycle 1 of the protocol says "decompose the problem into functions,
  propose concepts per function" (`config.DEFAULT_PROTOCOL`); the whiteboard has `add_function`, `add_concept
  (function_id)`, `set_concept_status open|favored|dropped`, `update_proposal`, `vote`. The excavator benchmark run
  (`runs/20261102-214939…`) ended with F1–F7 and C1–C10.
- **But the function list is a side-effect of the roster, not a shared artifact.** Kaito (mobility) wrote F1–F3 and
  their only concepts; Mara (excavation) F4–F6 and theirs; Ilya (sensing) F7. Six of seven functions had exactly one
  concept, by its own author. No concept was ever marked `favored` or `dropped`; no per-function selection happened.
  ME407 had 3–10 means per function and eight whole-concept combinations.
- **Members decide.** The proposal is written by a member (the one "whose concepts are favored for the most
  functions", else one the Manager names), and members' `ready` votes close the meeting. The Manager "steers the
  process; it does not design" and never votes.
- **Roles drift between discipline and function.** Rev 0 only says "3–5 members with distinct domains". For
  physics-heavy problems the model picks disciplines (structural dynamics, damping, constructability); for product
  problems it picks function-shaped roles ("Interception & Lift Mechanics", "Floating Platform, Anchoring & Storage").
  The owner noticed this; it is not designed, it is the model's habit.
- **Compatibility is checked only at the end.** Since the round-4 review, the Evaluator traces every material,
  energy and signal flow to a part. That check runs at acceptance, after the proposal is integrated — not when the
  function-winners are combined. The drum-to-hopper gap in the excavator was exactly an interface between the F4
  winner and the F5 winner that nobody checked at combination time.

## 2. What the literature and the ME407 case say

**ME407 (as applied).** Verb–noun functions on two levels; morphological chart; objective-tree weights with no
stated basis; integer scores with no written reasons; winners per function not carried into the combination; eight
combinations listed by hand with no compatibility logic; whole-concept matrix decided by 0.10 on a 10-point scale.
Two things I verified myself: Table 5.3's encoder total is printed 4.05 but is 6×0.34 + 9×0.66 = 7.98, so the lid
sensor winner was wrong; and the concept-stage sensor choice (ultrasonic/infrared) was overturned in detail design
because temperature was not a criterion in any sensor matrix. Detail design also found the scissor–screw lock, the
horizontal-guide moment and the vertical/horizontal clash — all interactions between separately chosen means.

**Fu et al.** Functional vector search on *all* subfunctions raised novelty; on one or two subfunctions it did not
(RED 2015) — a member who owns one function searches one slice. Far analogies have a sweet spot and help *after*
a first round, aimed at unsolved sub-problems (JMD 2013; Tseng 2008). Examples fixate even faculty, and a good
example that omits a subfunction makes everyone omit it (Linsey 2010; Fu 2010). Teams that adopt teammates'
ideas early converge prematurely and finish worse; good teams converge late and deliberately (McComb 2015). An AI
process manager matched human managers (Gyory 2022). Principles/guidelines/heuristics are best written as single
imperative directives with context (Fu, Yang, Wood 2016).

**Dieter / Pahl & Beitz / critics.** Function structures with matching energy–material–signal flows; the
morphological chart is to be *combined systematically* with a compatibility screen (P&B criteria A–G: compatible
with each other, meets the requirements list, realisable, cost, safety, information available). Pugh's datum
comparison beats weighted sums in simulation (Frey 2009); weighted sums assume independence and can rank-reverse
(Hazelrigg, Belton & Gear); choosing the best means per function ignores interactions and function sharing. The
team leader "promotes good decision-making"; "data outranks expert opinion".

## 3. Assessment

### Function or discipline? — Both, with a clear division of labour

Keep the **members by discipline** and make the **function structure a shared artifact** that is not owned by any
member.

- Discipline is what an LLM persona can actually *do* with: its search queries, the sources it can read, the
  insights and skills it opens, and the Evaluator's domain checks are all discipline-shaped. A "function owner"
  persona has no vocabulary of its own; in our runs it degenerates into the discipline that happens to serve that
  function (Kaito = mobility functions), which is the worst of both: one author per function, one concept per
  function, and the Fu 2015 one-slice search.
- Function ownership at concept stage reproduces ME407's weakness: separate optimisation per function, interactions
  found late. ME407 itself split by *subsystem* only in detail design, not at concept.
- What functions must do for us: guarantee coverage and breadth. So: the function structure (with flows) is written
  once, early, by the chief designer from the problem and the first search results; members may challenge it; and
  **every member must post, for every function, either a concept from their field or one line saying their field
  has none.** That fills the morphological chart with cross-discipline alternatives (the tri-star vs grouser choice
  happened only because one member had two ideas) and is where far analogies enter.

### Advisors and a chief designer? — Yes, and the evidence supports it

The owner's instinct matches McComb/Cagan (late, deliberate convergence by one synthesizer beats early adoption) and
Dieter's leader ("promote good decision-making", data over opinion). Proposed roles:

| Role | Today | Proposed |
|---|---|---|
| Members | design, integrate the proposal, vote | **advise**: functions challenged, concepts per function, evidence, objections, a written readiness *opinion* (not a binding vote) |
| Manager (meeting turn) | process lead, never designs | **Chief Designer**: writes the function structure; selects a means per function in prose (datum comparison, reasons for every loser); checks interfaces between selected means (flows match, P&B A–G) *before* composing; composes 2–3 whole candidates; writes the proposal and owns it |
| Evaluator | independent judge | unchanged (independence is the point) |
| Manager (gradient) | rewrites members' prompts after rejection | unchanged in code, but it now also rewrites the Chief Designer's section — so it must stay a separate role from the chief, or it grades its own work |

Risks and the mitigations the literature suggests:
- The chief becomes a single fixation point (Linsey: one example fixates faculty). Mitigation: members develop
  concepts in parallel for a full cycle before the chief selects (McComb: fewer interactions, slower convergence);
  the chief must write why each rejected alternative lost; a far-analogy turn in cycle 2 aimed at the functions the
  chief marked weakest.
- A function silently disappears in synthesis (Fu 2010 omission effect). Mitigation: the chief's proposal must map
  every function to a means; the Evaluator already checks flows — add "every function has a means" as its first
  check.
- Prose selection could become hand-waving. Mitigation: Pugh-style structure without numbers — a datum concept per
  function, each alternative better/same/worse per criterion *with the evidence id that says so* — which is also what
  Frey's simulations favour and what owner rule 1 allows.

### What not to change
Discipline rosters; the no-numbers rule (ME407's arithmetic error that flipped a winner and the rank-reversal
literature both argue for it); the Evaluator's independence; the TextGrad prompt-rewrite loop.

## 4. Ranked changes

| # | Change | Why (evidence) | Cost | How we would know it worked |
|---|---|---|---|---|
| 1 | Function structure with flows as a shared whiteboard object written by the chief in cycle 1; every member posts a concept or "none" for every function | ME407 breadth (3–10 means/function); Fu 2015 all-functions search; our runs: 1 concept/function | small: protocol text + one chief turn at the start of cycle 1 | concepts per function ≥ 2 from ≥ 2 members in a real run |
| 2 | Advisor council + Chief Designer selects per function in prose, checks interfaces at combination, writes the proposal; members give readiness opinions, not votes | McComb late convergence; Dieter leader; ME407 interactions found late; excavator drum→hopper gap | medium: meeting.py (chief turn, closure rule), PROPOSAL_RULE, member instructions, Secretary reads the chief's rationale | Evaluator rejections for missing functions/interfaces drop; the interface check fires before the Evaluator does |
| 3 | Coverage check: chief's proposal maps every function; Evaluator's first check is "every function has a means" | Fu 2010 omission effect | small | no accepted design with an orphan function |
| 4 | Analogy timing: near prior art in cycle 1; a far-analogy turn in cycle 2 on the weakest functions, each with a written mapping, unmapped ones dropped | Fu/Tseng sweet spot and timing | small: protocol text | more cross-domain concepts that survive to the proposal |
| 5 | Skills as imperative directives tagged principle / guideline / heuristic with context; library indexed by function + flow | Fu, Yang, Wood 2016; Roth's catalogues | small: skills.py header + seeding prompt | members open skills more often and notes say they helped |
| 6 | Concept = working principle {function, flows in/out, physical effect, geometry/material, motion} | Pahl & Beitz; feeds the schematic and the picture critic directly | larger: schema + Secretary + Stage B | fewer "mechanism of a different kind" picture faults |

## 5. Testing it

Fake-mode tests cover the mechanics (functions object, chief turn, closure without votes). The honest test is the
benchmark harness we already have: the same problem, current council vs advisor-council-plus-chief, blind rubric
judging. One pair on the excavator (the problem with the known interface gap) costs about $4.6 of the $12.6 left;
finishing b4 and b5 for the hackathon benchmark needs about $5. Both fit, with little margin; the owner decides the
order.

## Sources
- ME407 Fall 2022 group C1 report (Opus reading report, verified at Tables 5.3 and 5.7).
- Fu et al.: RED 2015 26:77–95; JMD 2013 135(2):021007 and 135(3):031006; Design Studies 2013 34(6); JMD 2014
  136(11):111102; JMD 2016 138(10):101103; Linsey et al. JMD 2010 132:041003; Chan et al. JMD 2011; McComb, Cagan,
  Kotovsky 2015; Gyory et al. JMD 2022 144(2).
- Dieter & Schmidt, *Engineering Design* 5/e (chapters 3, 6, 7, 8; team supplements); Pahl & Beitz, *Engineering
  Design: A Systematic Approach*; Frey et al. RED 2009 20:41–58; Hazelrigg JMD 1996; McComb, Goucher-Lambert, Cagan
  Design Science 2017; Belton & Gear 1983; Roth, *Konstruieren mit Konstruktionskatalogen*.
