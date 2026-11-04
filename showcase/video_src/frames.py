import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
R, OUT = sys.argv[1], sys.argv[2]
F = "/System/Library/Fonts/Supplemental/Arial.ttf"; FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
BG = (246, 247, 249)
def frame(kicker, title, sub=None):
    im = Image.new("RGB", (1920, 1080), BG); d = ImageDraw.Draw(im)
    d.text((96, 44), kicker, font=ImageFont.truetype(FB, 24), fill=(31, 111, 209))
    d.text((96, 80), title, font=ImageFont.truetype(FB, 46), fill=(22, 32, 44))
    if sub: d.text((96, 142), sub, font=ImageFont.truetype(F, 26), fill=(74, 85, 99))
    return im, d
def put(im, img, box):
    x0, y0, x1, y1 = box; k = min((x1 - x0) / img.size[0], (y1 - y0) / img.size[1])
    r = img.resize((round(img.size[0] * k), round(img.size[1] * k)), Image.LANCZOS)
    im.paste(r, (x0 + (x1 - x0 - r.size[0]) // 2, y0 + (y1 - y0 - r.size[1]) // 2)); return r.size
rd = f"{R}/stage_b/attempt_00/round_00"
render = Image.open(f"{rd}/render.png").convert("RGB")
K = "OUR BEST RESULT · TACTILE FINGERTIP (IN THE SPIRIT OF META'S DIGIT 360)"
im, d = frame(K, "1 · Muse Image renders the accepted design", "the image model's own callouts are not trusted: the next step checks every part")
put(im, render, (96, 200, 1824, 1050)); im.save(f"{OUT}/ft_1.png")
im, d = frame(K, "2 · SAM 3 finds each part in the render", "one mask per part from a plain phrase: the critic gets where each part is and what touches what")
a = np.array(render).astype(float)
cols = {"skin": (230, 80, 80), "trans": (60, 120, 230), "pillars": (40, 170, 90), "flex": (240, 160, 30), "core": (150, 80, 200), "tail": (0, 170, 190)}
names = {"skin": "ridged skin", "trans": "firm layer", "pillars": "micro-pillars", "flex": "electrode flex", "core": "rigid core", "tail": "signal cable"}
cent = {}
for pid, c in cols.items():
    m = np.array(Image.open(f"{rd}/sam_masks/{pid}.png").convert("L").resize(render.size)) > 127
    a[m] = a[m] * 0.45 + np.array(c) * 0.55
    ys, xs = np.nonzero(m); i = np.argmin((xs - xs.mean()) ** 2 + (ys - ys.mean()) ** 2); cent[pid] = (xs[i], ys[i])
ov = Image.fromarray(a.astype("uint8")); od = ImageDraw.Draw(ov); f = ImageFont.truetype(FB, 34)
for pid, (x, y) in cent.items():
    tw = od.textlength(names[pid], font=f); tx = 380 - tw
    ty = y - 20
    od.rectangle([tx - 10, ty - 6, tx + tw + 10, ty + 42], fill=cols[pid]); od.text((tx, ty), names[pid], font=f, fill="white")
    od.line([(x, y), (tx + tw + 10, ty + 18)], fill=cols[pid], width=4); od.ellipse([x - 8, y - 8, x + 8, y + 8], fill=cols[pid], outline="white", width=3)
put(im, ov, (96, 200, 1824, 1050)); im.save(f"{OUT}/ft_2.png")
im, d = frame(K, "3 · The figure: labels, numbered working steps, scale from a hand", None)
put(im, Image.open(f"{R}/final/panel_A.png").convert("RGB"), (96, 150, 1824, 1070)); im.save(f"{OUT}/ft_3.png")
im, d = frame(K, "4 · The critical part, how it is measured, and how it is made", None)
put(im, Image.open(f"{R}/final/panel_B.png").convert("RGB"), (96, 160, 696, 720))
put(im, Image.open(f"{R}/final/panel_C.png").convert("RGB"), (736, 200, 1824, 560))
put(im, Image.open(f"{R}/final/panel_D.png").convert("RGB"), (96, 730, 1824, 1070))
d.text((736, 600), "Making plan: cast skin and firm layer in a two-part mould · mould the pillar array and laminate it", font=ImageFont.truetype(F, 24), fill=(51, 64, 79))
d.text((736, 634), "to the flex circuit · wrap it over the 3D-printed core · bolt to the finger, route the shielded tail", font=ImageFont.truetype(F, 24), fill=(51, 64, 79))
d.text((736, 676), "15.0 mm wide · 1 mN touch gives 22.7 times the converter's smallest step · slip caught in 12 ms", font=ImageFont.truetype(FB, 24), fill=(22, 32, 44))
im.save(f"{OUT}/ft_4.png")
