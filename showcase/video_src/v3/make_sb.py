"""Assemble storyboard.json (narration + visuals); tour keys are read from arch_keys.json / picture_keys.json."""
import glob, json, os
H = os.path.dirname(os.path.abspath(__file__))
def keys(f):
    k = json.load(open(os.path.join(H, f)))["keys"]
    return [{"box": x["box"], "hold": x.get("hold", 1.0), "caption": x.get("caption", "")} for x in k if "Keep or revert" not in x.get("caption", "")]
def reveal(prefix_or_list, at=None):
    imgs = prefix_or_list if isinstance(prefix_or_list, list) else sorted(glob.glob(os.path.join(H, prefix_or_list + "_[0-9].png")))
    imgs = [os.path.basename(i) for i in imgs]
    n = len(imgs)
    return {"type": "reveal", "imgs": imgs, "at": at or [round(i / n, 2) for i in range(n)]}
SEG = [
 ("problem", "The best feedback on a concept is a picture. Ask a frontier model and the picture looks right but doesn't work: four blades where the text says three, hoppers that never connect. Feedback fixes one thing and breaks another.", reveal("problem", [0, 0.58])),
 ("hook", "Hardware Engineer takes one paragraph and returns an engineered concept: a labelled picture you can trust, every number with its calculation, a plan to make it, and the whiteboard behind it. Here, a robot fingertip that feels a one millinewton touch.", reveal("hook", [0, 0.64])),
 ("simple", "It works like a hardware team: experts on one whiteboard, a reviewer like a senior engineer, and a rejection becomes a written gradient that rewrites the team's own instructions, inspired by TextGrad.", reveal("simple", [0, 0.3, 0.6, 0.82])),
 ("architecture", "The engineer gives only the what. Experts advise, a chief designer decides, and everything they search, calculate and sketch lands on one whiteboard. A reviewer writes the critique. On a rejection the Manager turns it into a gradient and rewrites only the lines that let the fault through. Lessons, skills and tools carry to the next problem.", {"type": "tour", "img": "arch_base.png", "keys": keys("arch_keys.json")}),
 ("textgrad", "The reviewer rejects the hand truck: the backbone cannot fold into the van, the bending uses the wrong beam model. The Manager writes what must change and why the instructions let it through, and rewrites only those lines. Next meeting, the same issues are checked first, and pass.", reveal("textgrad", [0, 0.2, 0.36, 0.5, 0.68, 0.86])),
 ("whiteboard", "The whiteboard never resets. Four experts post ideas, the chief designer stars one per function, sketches and calculations fill the board. The reviewer rejects. Meeting two starts on the same board, rechecks the folding, and the design is accepted.", reveal("whiteboard", [0, 0.17, 0.34, 0.5, 0.66, 0.84])),
 ("picture", "A code sketch fixes the geometry, Muse Image renders it, SAM maps every part, and the multimodal critic checks the picture against sketch and text. A wrong picture becomes a gradient on the image prompt, fixed locally and kept only if nothing else gets worse. A wrong design goes back to the team and the master prompt.", {"type": "tour", "img": "picture_loop_base.png", "keys": keys("picture_keys.json")}),
 ("sam", "Why SAM? Image models miss small parts and, told to fix one, redraw everything. SAM 3.1 gives the critic and the editor each part's exact region, and what it finds shapes the feedback: with its marks the critic counted four blades on a three-blade rotor. The final run still argued one away; our next fix.", reveal(["sam_1.png", "sam_count_1.png", "sam_count_2.png", "sam_count_3.png"], [0, 0.42, 0.62, 0.84])),
 ("fingertip", "The robot fingertip: SAM finds the skin, the pillars, the flex circuit, the core and the cable. The figure shows the part that decides it, how it is measured and how it is made: details that carry straight into embodiment design.", reveal("fingertip", [0, 0.36, 0.66])),
 ("gallery", "The same team designed an excavator, a turbine, a hand truck, a cold room and a footbridge damper.", {"type": "still", "img": "gallery.png"}),
 ("open", "The same system also runs on Meta's open weights: Muse Spark Open served on Baseten, SAM 3 on Modal.", {"type": "still", "img": "open.png"}),
 ("benchmark", "Two blind judges, a fault audit before any score: on open weights the designs reach the same level as on the Meta API.", {"type": "still", "img": "benchmark.png"}),
 ("close", "The engineer gives the what. Hardware Engineer works out the how, and learns your engineering practice, design after design.", {"type": "still", "img": "close.png"}),
]
sb = {"voice": "af_heart", "speed": 1.1,
      "tts_python": "/private/tmp/claude-501/-Users-sinancandan-Downloads-MetaHackathon-HardwareScientist-MetaCode/b98a4c52-0a9e-4880-9b01-f68736a14a96/scratchpad/tts/bin/python",
      "segments": [{"id": i, "text": t, "visual": v} for i, t, v in SEG]}
json.dump(sb, open(os.path.join(H, "storyboard.json"), "w"), indent=1)
print(sum(len(t.split()) for _, t, _ in SEG), "words")
