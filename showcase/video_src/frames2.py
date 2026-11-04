import json, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; V = S + "/video"
F = "/System/Library/Fonts/Supplemental/Arial.ttf"; FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
BG = (246, 247, 249)
def frame(kicker, title, sub=None):
    im = Image.new("RGB", (1920, 1080), BG); d = ImageDraw.Draw(im)
    d.text((96, 44), kicker, font=ImageFont.truetype(FB, 24), fill=(31, 111, 209))
    d.text((96, 80), title, font=ImageFont.truetype(FB, 46), fill=(22, 32, 44))
    if sub: d.text((96, 142), sub, font=ImageFont.truetype(F, 26), fill=(74, 85, 99))
    return im, d
def tile(im, d, img, box, cap):
    x0, y0, x1, y1 = box; h = y1 - y0 - 40
    k = min((x1 - x0) / img.size[0], h / img.size[1]); r = img.resize((round(img.size[0] * k), round(img.size[1] * k)), Image.LANCZOS)
    im.paste(r, (x0 + (x1 - x0 - r.size[0]) // 2, y0)); d.text((x0 + (x1 - x0 - r.size[0]) // 2, y0 + r.size[1] + 8), cap, font=ImageFont.truetype(FB, 24), fill=(22, 32, 44))
R = "runs"
A = lambda p: Image.open(p).convert("RGB")
def cropA(img, frac):  # panel A only (top part, without the how-it-works strip)
    return img.crop((0, 0, img.size[0], int(img.size[1] * frac)))
# gallery
im, d = frame("THE SAME SYSTEM, SIX PROBLEMS", "Every design comes with its numbers, its sources and its making plan")
tile(im, d, cropA(A(f"{R}/20261103-234812_lunar-regolith-excavation-robot/final/panel_A.png"), 0.88), (60, 190, 950, 640), "Lunar regolith excavator (NASA Lunabotics rules)")
tile(im, d, cropA(A(f"{R}/20261103-224916_small-wind-turbine-for-a-wind-tunnel-com/final/panel_A.png"), 0.88), (970, 190, 1860, 640), "Wind-tunnel turbine, folds into a 45 cm cube")
for i, (p, cap) in enumerate([("stair-climbing-hand-truck-for-parcel-cou", "Stair-climbing hand truck"), ("off-grid-solar-powered-cold-storage-for", "Off-grid solar cold room"), ("vibration-retrofit-for-a-lively-pedestri", "Footbridge vibration damper")]):
    tile(im, d, A(f"showcase/{p}/final/panel_A.png"), (60 + i * 610, 670, 650 + i * 610, 1070), cap)
im.save(f"{V}/gallery.png")
# open weights
im, d = frame("THE SAME LOOPS ON META'S OPEN WEIGHTS · MUSE SPARK + SAM 3", "Half the time, lower scores for now, and still original designs")
for i, (p, cap) in enumerate([("b1", "Excavator with a vibrating scraper"), ("b2", "Fingertip with a clear curved taxel dome"), ("b3", "Hand-held three-blade turbine")]):
    src = A(f"{V}/open_{p}.png")
    tile(im, d, cropA(src, 0.49), (60 + i * 610, 190, 650 + i * 610, 640), cap)
    tile(im, d, src.crop((0, int(src.size[1] * 0.815), src.size[0], src.size[1])), (60 + i * 610, 660, 650 + i * 610, 940), "how it is made")
d.text((96, 960), "Same architecture, run on open-weights Muse Spark (Baseten) and SAM 3 (Modal): 26 min and $2.08 per design.", font=ImageFont.truetype(F, 28), fill=(51, 64, 79))
im.save(f"{V}/open.png")
# hook
im, d = frame("HARDWARE SCIENTIST · META MODELS ONLY", "A paragraph in. An engineered concept out, with its proof.")
prob = json.load(open(f"{R}/20261104-005633_tactile-fingertip-sensor-for-robot-hands/problem.json"))
d.rounded_rectangle([96, 220, 760, 1000], 18, fill="white", outline=(214, 220, 228), width=2)
d.text((128, 250), "WHAT THE ENGINEER WRITES", font=ImageFont.truetype(FB, 22), fill=(31, 111, 209))
y = 300
for line in textwrap.wrap(prob["statement"], 40):
    d.text((128, y), line, font=ImageFont.truetype(F, 30), fill=(22, 32, 44)); y += 42
y += 20
for c in prob.get("constraints", []):
    for j, line in enumerate(textwrap.wrap(c, 38)):
        d.text((128, y), ("• " if j == 0 else "   ") + line, font=ImageFont.truetype(F, 28), fill=(51, 64, 79)); y += 38
d.text((790, 560), "→", font=ImageFont.truetype(FB, 80), fill=(138, 149, 163))
tile(im, d, cropA(A(f"{R}/20261104-005633_tactile-fingertip-sensor-for-robot-hands/final/panel_A.png"), 0.88), (880, 200, 1860, 1060), "What Hardware Scientist returns (plus constraint table, calculations, making plan)")
im.save(f"{V}/hook.png")
