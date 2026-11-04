# Design notes for the 3-minute video (visual layer, v2)

## What we looked at
- https://x.com/raedle — X returned HTTP 402 to the fetcher; the main session opened it in a browser: a thread of builder projects on the Meta Model API with SAM 3.1 + Muse Spark / Muse Image. Style patterns seen there: before → after split with every instance in bright mask colours; a one-line hook with the plain prompt ("two-word prompt: ..."); real app screens side by side; the model combo named plainly as the punchline.
- Meta recap of the first Llama 3 hackathon (winners OpenGlass, Deb8): https://ai.meta.com/blog/llama-3-hackathon-recap-cerebral-valley/
- OpenGlass README (1st place there): https://github.com/BasedHardware/OpenGlass — one-line claim with a hard number ("less than $25"), product photo and demo video right under it, text later.
- Llama Impact hackathon pages (lablab.ai): https://lablab.ai/ai-hackathons/llama-impact-hackathon/live
- AI Tinkerers video production guide: https://aitinkerers.org/docs/public/video_production_guide.md
- RevenueCat Shipaton pitching guide: https://www.revenuecat.com/blog/engineering/how-to-win-shipaton-part-4-pitching-your-app
- Music Hackspace 3-minute pitch: https://musichackspace.org/blog/hackathon-presentation-tips
- Reskilll 3-minute demo tips: https://blogs.reskilll.com/hackathon-demo-presentation-tips-pitch-3-minutes-win-2026/

## Patterns we use (our own wording; no visuals or text copied)
1. **Real output first, architecture second.** Open on the finished fingertip figure, not on a diagram. The judge sees the payoff in the first 10 s.
2. **One claim per frame, at most ~8 words, big type.** Everything else is the voice-over.
3. **Hero visual full-bleed (or near), one caption.** The image carries the frame; text only labels it.
4. **The problem as one short human quote**, then cut to the answer (problem → result in under 20 s).
5. **Build a diagram step by step.** Each reveal adds one box or one loop in its own colour; the viewer never sees a finished, crowded diagram cold.
6. **Colour = meaning, kept constant.** Blue = the system / accent, orange = design loop, purple = picture loop, green = knowledge. The same colours on every frame.
7. **Numbers as huge type with one caption each** (3–4 per frame, never a table).
8. **Camera moves over one high-res figure** (pan/zoom keyframes) instead of many separate diagram slides; hide what is explained later behind a labelled translucent block.
9. **Show, then name.** Show the part (SAM mask, sketch) first; name the technique small.
10. **Honest proof beats claims.** State measured facts with their limits; no claim beyond the data.
11. **Feature cut.** Only what supports the core idea (self-improving design team from written critique); everything else goes to the repo.
12. **End on a mosaic of real outputs + one-line logline**, model names small. References live in a one-line grey footer on each frame, not on the close.
13. **Before → after mask split with the plain prompts as tags** (render | SAM masks | what SAM was asked), and the model combo named in one line: "Muse Image + SAM 3.1 + Muse Spark on the Meta Model API".
14. **Show the problem first with real faults circled** (one-prompt renders: wrong blade count, hoppers that do not connect) plus a tiny "feedback fixes one thing, breaks another" cycle.

Name on every frame: Hardware Engineer (HE). The owner's architecture figures keep their original text.
