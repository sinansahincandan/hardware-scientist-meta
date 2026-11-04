# Hardware Engineer — submission form texts

Track: **Push the Frontier**. Each block below is under 3,000 characters (counted by `scripts`-free check: `python3 -c "..."`; see JOURNAL).

## 1. Project description (≤ 3000 chars)

Hardware Engineer (HE) is a self-improving engineering team, built only on Meta models, that turns one paragraph into a hardware concept that works — and rewrites its own instructions from written critique.

Hardware design starts with a concept, and the best feedback on a concept is a picture. Ask a frontier model directly and the picture looks right but does not work: four blades on a three-blade rotor, two hoppers that never connect, numbers that were guessed. Give feedback and it fixes one thing and breaks another. Hours go by.

HE runs those feedback rounds itself. Give it a paragraph, not a specification, and it returns an engineered concept: a labelled photoreal figure you can trust, every number with the calculation behind it, how the device is measured, a plan for how to make it, and the whole whiteboard that led there.

How it works: four domain experts and a chief designer argue on one shared whiteboard; they search the literature, calculate, simulate and sketch. An Evaluator reviews the result like a senior engineer: it re-derives formulas, checks the worst case of every limit and confirms the design agrees with itself. On a rejection the Manager turns the written critique into a textual gradient, inspired by TextGrad: first what in the design must change, then which instruction let the fault through. It rewrites only those lines of the team's prompt; the meeting continues on the same board and the same issues are checked first. Every loop closes: keep or revert.

The picture loop: a code sketch fixes the geometry and Muse Image renders it. SAM 3.1 finds every part and measures counts, contacts and size against a hand or a person. A multimodal critic compares the picture with the sketch and the design text. A wrong picture becomes a gradient on the image prompt and is fixed locally, kept only if nothing else gets worse; a wrong design goes back to the team and into the master prompt.

It learns your practice: lessons, skills and tools from every design are read by the next team, and you can add your own sources to its knowledge base.

Measured honestly: six problems (lunar excavator, robot fingertip, wind-tunnel turbine, stair-climbing hand truck, solar cold room, footbridge damper), two blind judges, a fault audit before any score. HE on the Meta API scores 26.2 ± 2.9 of 40; HE on open weights (Muse Spark Open on Baseten, SAM 3 on Modal) 26.1 ± 2.5 on the four problems that finished within budget. Against one prompt to the same frontier model (26.9 ± 3.0) it is a tie on score: ahead on numbers that are right and supported and on how to make it, behind on the picture showing the design. Picture–text consistency is the next target.

Try it: clone the public repo, paste your Meta API key, run one problem from the terminal (about 30 minutes, about $1.7). Six finished designs with reports, whiteboards and figures are in showcase/.

## 2. Describe your use of Meta products to build the submitted project (≤ 3000 chars)

Every model call inside Hardware Engineer goes to a Meta model through the Meta Model API; there is no other model or service in the runtime.

Muse Spark 1.3 is the whole team. It plays four domain experts and a chief designer who argue on one shared whiteboard with function tools for literature search (Meta's hosted web search), calculation (sandboxed Python), simulation and sketching; a Secretary that writes the accepted solution, its constraint table and the making plan; the Evaluator, which reviews the design as a senior engineer would (formula and regime checks, worst case of every limit, self-consistency) and returns a written verdict as a strict JSON schema; the Manager, which turns a rejection into a two-step textual gradient (what in the design must change; which instruction let it through) and rewrites only the guilty sections of the master prompt; the prompt writer for the image model; and the multimodal critic that looks at the rendered picture itself, with reasoning effort set per role. The knowledge loop (lessons, skills, insights written after each problem) is also Muse Spark.

Muse Image 1.0 renders the concept from a code-drawn mechanism sketch used as the reference image, renders the critical-part close-up and the making steps, and performs the local edits: a wrong part is re-rendered only inside its own region (the critic's box united with SAM's box) and the edit is kept only if nothing outside it changed.

SAM 3.1 is the measuring instrument of the picture loop. For every part in the design it segments the render from text phrases (and box prompts for parts a phrase misses), returns masks and instances, and HE measures counts, which parts touch, long-axis orientation and size against a hand or a person in the picture. Repeated elements (blades, wheels, pillars) are counted and drawn as numbered Set-of-Mark boxes that the critic sees; SAM's masks also place the labels on the final figure. With these marks the critic counted four blades on a three-blade rotor that it had passed from the picture alone.

Open weights: the same system, unchanged in architecture, runs on Muse Spark Open (served on Baseten through its Responses-compatible API) and on SAM 3 open weights (served on Modal, A10G); pictures stay on Muse Image through the Meta API. The open branch carries the SAM licence and the "Built with Muse Spark Open" notice as the Muse Model License requires.

Spend: about $144 of Meta API credit for all development runs and the six-problem benchmark; one full problem costs $3–6, the quick mode about $1.7.

## 3. Why are Meta's models important to your solution (≤ 3000 chars)

Three properties of Meta's models make this design possible, and we used each one.

Muse Spark is multimodal in both directions of our loop. The critic does not read a description of the picture; it looks at the render, the mechanism sketch and the SAM overlay with numbered marks, and compares them with the design text. The experts look at each other's sketches during the meeting. A text-only model would have to trust the image model's own description of what it drew, which is exactly the failure we are fixing.

Muse Spark reasons long enough to review a design. The Evaluator re-derives beam deflection with the right support model, stacks folded lengths part by part instead of accepting a volume, and checks whether a fixed-pitch rotor can stay parked at 22 m/s — and writes why, in prose a colleague can read. That written review is our loss function; the Manager's gradient and the prompt rewrite are only as good as the critique. Function tools with strict JSON schemas let Python branch on accept/reject while every judgment stays in words, with no numeric scores anywhere in the system.

SAM 3 turns the picture from a thing to admire into a thing to measure. Text-prompted segmentation with instances gives counts, contacts and sizes for free, with no training; mask-level regions let the image model fix one part without redrawing the device, which is where parts used to get lost (in 65 picture rounds, every lost part followed a full re-render, none a kept local edit). Nothing comparable exists as a single open model.

Muse Image accepts a reference image, so a code-drawn sketch fixes the geometry and the render stays faithful to the mechanism rather than to a prompt's adjectives; its region edits make the keep-or-revert loop cheap.

And the open weights matter for the product. A company will not send its concept designs to a hosted API; with Muse Spark Open and SAM 3 the same team runs on its own infrastructure, learns that company's engineering practice through the knowledge base, and reached the same benchmark level as the hosted models in our blind judging (26.1 vs 26.2 of 40). One model family covering reasoning, vision, image generation and segmentation, hosted and open, is what let two people build a closed-loop engineering team in a hackathon.

## 4. Feedback on partner technologies (Baseten, Modal)

Baseten (Muse Spark Open, meta-models/muse-spark-open-1026). What worked: the Responses-compatible API ran our whole Stage A unchanged — function tools, strict json_schema output, input images and reasoning effort all behaved as on the Meta API, and replayed history was billed mostly at the cached rate (640 of 747 input tokens cached in our probe). Throughput (2M tokens/min) never limited three parallel runs. What cost us time: previous_response_id returns HTTP 501, so we keep the conversation chain client-side; the hosted web_search tool is accepted but never searches (no web_search_call items, and the reply invented numbered sources), so we had to run our own search tool inside the call; with no reasoning effort sent the model reasons at the highest level and can spend its whole token cap before answering; a request with 16 images fails with HTTP 400 "Too many images (max 8)", which is not in the docs; the model name in the docs (muse-spark-open) differed from the only name the key accepted. Suggestions: document the 8-image limit and the search tool status, return 501s in the error body with the alternative, and ship a cost line per response.

Modal (SAM 3 on A10G). What worked: once deployed, SAM calls took 0.25–3.8 s and three parallel runs cost about $0.19 per run; secrets and GPU selection were simple; the whole SAM service is one file. What cost us time: no L4 started within 200 s even for a plain image, so we moved to A10G; a conditionally defined secret crashed the container at startup with no clear message; cold starts (about 25 s) and the 5-minute idle window dominate the bill for a bursty workload like ours, and the per-call estimate we could make from the API missed them. Model-side, not Modal's fault: the facebook/sam3.1 checkpoint is video-only (multiplex), so the open branch runs SAM 3; the sam3 package imports psutil, scipy and pkg_resources without declaring them. Suggestions: a cold-start/idle cost estimate in the dashboard per app, and a warm-pool option for short bursts.
