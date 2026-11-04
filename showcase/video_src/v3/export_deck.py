"""Deck slides (deck3/*.jpg), deck_pub slide files, showcase/story.html from the video2 frames + storyboard narration."""
import base64, glob, html, json, os, re, sys
from PIL import Image
S = os.path.dirname(os.path.abspath(__file__)); V = f"{S}/video2"
sb = {g["id"]: g["text"] for g in json.load(open(f"{V}/storyboard.json"))["segments"]}
def last(prefix):
    return sorted(glob.glob(f"{V}/{prefix}_[0-9].png"))[-1]
SL = [  # id, frame, alt, note
 ("problem", last("problem"), "One-prompt renders with SAM-coloured parts: four blades for three, two hoppers for one; feedback fixes one thing and breaks another", sb["problem"]),
 ("hook_in_out", f"{V}/hook_1.png", "What goes in: one paragraph. What comes out: labelled figure, numbers with calculations, making plan, whiteboard", sb["hook"]),
 ("hook", f"{V}/hook_2.png", "A one-paragraph problem beside the labelled robot fingertip concept", "One paragraph in, an engineered concept out: a robot fingertip that feels a 1 mN touch."),
 ("simple", last("simple"), "Simple loop: problem, expert team, evaluator, picture, concept; critique flows back as a gradient", sb["simple"]),
 ("architecture", f"{V}/arch_1.png", "Full architecture: engineer, master prompt, council, whiteboard, evaluator, Manager gradient, knowledge", sb["architecture"]),
 ("textgrad", last("textgrad"), "Five cards from a real hand-truck run with pictures: reviewer says no, what must change, why it got through, new rule, re-checked first", sb["textgrad"]),
 ("whiteboard", f"{V}/whiteboard.gif", "Animated whiteboard of the stair-climbing hand truck growing over two meetings", sb["whiteboard"]),
 ("picture_loop", f"{V}/picture_loop_1.png", "Picture loop: code sketch, prompt writer, Muse Image, SAM part map, critic, image-prompt gradient, back to the team", sb["picture"]),
 ("sam_why", f"{V}/sam_1.png", "SAM masks on the fingertip: soft skin, firm layer, micro-pillars, electrode flex, signal cable, rigid core", "Image models miss small parts and, told to fix one, redraw everything. SAM 3.1 gives the critic and the editor each part's exact region, and what it finds goes straight into the feedback."),
 ("sam_count", f"{V}/sam_count_3.png", "Wind turbine: critic alone sees three blades; with SAM numbered marks it counts four; in the final run it still argued one away", "With SAM's numbered marks the critic counted four blades on a three-blade rotor and sent the picture back. In the final full run it still called the fourth blade motion blur: not solved yet."),
 ("fingertip", f"{V}/fingertip_2.png", "Robot fingertip figure with its labelled parts", sb["fingertip"]),
 ("fingertip_made", f"{V}/fingertip_3.png", "Fingertip critical part, measurement chain and making steps", "The part that decides it, how it is measured and how it is made: details that carry into embodiment design."),
 ("gallery", f"{V}/gallery.png", "Six concepts: excavator, turbine, hand truck, cold room, footbridge damper, fingertip", sb["gallery"]),
 ("open", f"{V}/open.png", "Three designs made on open-weights Muse Spark Open on Baseten and SAM 3 on Modal. Built with Muse Spark Open.", sb["open"]),
 ("benchmark", f"{V}/benchmark.png", "One chart: Hardware Engineer on the Meta API vs on open weights, mean and std of two blind judges", sb["benchmark"] + " Mean of 40: 26.2 ± 2.9 on the Meta API over six problems, 26.1 ± 2.5 on open weights over the four that finished in budget."),
 ("close", f"{V}/close.png", "Mosaic of final figures with the closing line", sb["close"]),
]
os.makedirs(f"{S}/deck3", exist_ok=True); os.makedirs(f"{S}/deck_pub/project/slides", exist_ok=True)
for f in glob.glob(f"{S}/deck3/*") + glob.glob(f"{S}/deck_pub/project/slides/*"): os.remove(f)
out = []
for i, (sid, frame, alt, note) in enumerate(SL, 1):
    dst = f"{S}/deck3/{i:02d}_{sid}." + ("gif" if frame.endswith(".gif") else "jpg")
    if frame.endswith(".gif"): os.system(f"cp '{frame}' '{dst}'")
    else: Image.open(frame).convert("RGB").save(dst, quality=90)
    out.append((sid, dst, alt, note))
json.dump([[s, os.path.basename(d), a, n] for s, d, a, n in out], open(f"{S}/deck3/slides.json", "w"), indent=1)
# story.html (self-contained)
page = ["<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Hardware Engineer — the story</title><style>",
"body{margin:0;background:#eef1f5;color:#16202c;font:18px/1.6 'DM Sans',Inter,-apple-system,Helvetica,Arial,sans-serif}",
".wrap{max-width:1180px;margin:0 auto;padding:40px 16px 60px}h1{font-size:40px;margin:0 0 6px}.sub{color:#5b6878;margin:0 0 30px}",
".slide{margin:0 0 44px}.slide img{width:100%;border-radius:14px;box-shadow:0 6px 24px rgba(20,30,50,.12);display:block}.slide p{max-width:1000px;margin:16px 4px 0;color:#33404f}",
"</style></head><body><div class='wrap'><h1>Hardware Engineer</h1><p class='sub'>A self-improving design team built on Meta models: Muse Spark 1.3, Muse Image 1.0, SAM 3.1; also on Muse Spark Open on Baseten, SAM 3 on Modal. Video: hardware_engineer_3min.mp4 · benchmark: bench/round6/</p>"]
for sid, dst, alt, note in out:
    mime = "image/gif" if dst.endswith("gif") else "image/jpeg"
    b = base64.b64encode(open(dst, "rb").read()).decode()
    page.append(f"<div class='slide'><img alt=\"{html.escape(alt)}\" src='data:{mime};base64,{b}'><p>{html.escape(note)}</p></div>")
page.append("</div></body></html>")
open("/Users/sinancandan/Downloads/MetaHackathon_HardwareScientist_MetaCode/showcase/story.html", "w").write("\n".join(page))
print(len(out), "slides")
