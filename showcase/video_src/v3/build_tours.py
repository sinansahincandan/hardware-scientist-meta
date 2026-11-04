"""Architecture (Fig. 1) and picture-loop (Fig. 2) tour bases + camera keys + preview keyframes.

The owner's SVGs are only rendered (prep.py -> assets/fig*_6000.png); every overlay is drawn on the PNG here.
Camera boxes are [x0, y0, x1, y1] in the base PNG's pixels, all exactly 16:9.
"""
import json

import numpy as np
from PIL import Image

from common import A, HERE, Shooter, foot, page, write

Image.MAX_IMAGE_PIXELS = None
S = Shooter()
BW = 6000  # base width before padding


def fit169(box, W, H):
    x0, y0, x1, y1 = box
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    if w / h > 16 / 9:
        h = w * 9 / 16
    else:
        w = h * 16 / 9
    w, h = min(w, W), min(h, H)
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return [round(x0), round(y0), round(x0 + w), round(y0 + h)]


def keyframes(name, base_png, W, H, keys, refs):
    """One 1920x1080 preview per key: the base image zoomed to the box, caption pill, footer."""
    css = """
.cam{position:absolute;left:0;top:0;transform-origin:0 0}
.cap{position:absolute;background:rgba(18,32,48,.9);color:#fff;font-size:40px;font-weight:700;
 padding:14px 30px;border-radius:999px;display:flex;align-items:center;gap:16px}
.cap .tg{font-size:24px;font-weight:700;color:#ffb48a;border:2px dashed #ffb48a;border-radius:999px;padding:4px 14px}
.foot{background:rgba(245,246,248,.92);left:0;right:0;bottom:0;padding:10px 64px 12px}
"""
    outs = []
    for i, k in enumerate(keys, 1):
        x0, y0, x1, y1 = k["box"]
        s = 1920 / (x1 - x0)
        tag = f'<span class="tg">{k["tag"]}</span>' if k.get("tag") else ""
        pos = {"bl": "left:64px;bottom:76px", "tl": "left:64px;top:48px", "br": "right:64px;bottom:76px", "tr": "right:64px;top:48px", "r": "right:30px;top:856px;flex-direction:column;align-items:flex-start;font-size:36px;border-radius:28px;padding:20px 30px"}[k.get("pos", "bl")]
        cap = f'<div class="cap" style="{pos}">{k["caption"]}{tag}</div>' if k.get("caption") else ""
        body = (f'<img class="cam" src="../{base_png}" style="width:{W}px;height:{H}px;transform:scale({s}) translate({-x0}px,{-y0}px)">'
                f'{cap}{foot(*refs)}')
        outs += S.shoot(write(f"{name}_{i}.html", page(body, css)), f"{HERE}/{name}_{i}.png")
    return outs


# ================================================================ Fig. 1 architecture
fig1 = Image.open(f"{A}/fig1_6000.png").convert("RGB")
a = np.asarray(fig1.convert("L"))
# cut in the white gap between the blue "How?" area and the Controller-loop panel
rows = [y for y in range(2700, 3400) if (a[y] < 250).mean() == 0]
cut = (rows[0] + rows[-1]) // 2 if rows else 3060
top = fig1.crop((0, 0, BW, cut))
H1 = round(BW * 9 / 16)  # 3375
pad1 = (H1 - cut) // 2
base1 = Image.new("RGB", (BW, H1), "white")
base1.paste(top, (0, pad1))
base1.save(f"{A}/_arch_raw.png")
base1.save(f"{HERE}/arch_base.png")  # the base is the plain render, no overlay


def d1(x0, y0, x1, y1):  # Fig. 1 display coords (2000-wide preview) -> base pixels
    return [x0 * 3, y0 * 3 + pad1, x1 * 3, y1 * 3 + pad1]


# boxes in arch_base.png pixels, read off zoom crops of the figure
arch_keys = [
    dict(box=[0, 0, BW, H1], caption="", hold=0.8),
    dict(box=fit169([100, 0, 2600, 1406], BW, H1), caption="The engineer gives only the what", pos="tr", hold=1.0),
    dict(box=fit169([960, 1317, 2700, 2296], BW, H1), caption="Experts advise, a chief designer decides", pos="br", hold=1.4),
    dict(box=fit169([880, 2150, 2000, 2780], BW, H1), caption="Everything lands on one whiteboard", hold=1.2),
    dict(box=fit169([1780, 2150, 2900, 2780], BW, H1), caption="A reviewer writes the critique", pos="tr", hold=1.0),
    dict(box=fit169([0, 600, 4933, 3375], BW, H1), caption="Critique → gradient → prompt rewrite", tag="inspired by TextGrad", pos="tr", hold=1.8),
    dict(box=fit169([2300, 150, 5950, 2203], BW, H1), caption="Lessons, skills and tools carry to the next problem", pos="tl", hold=1.4),
    dict(box=[0, 0, BW, H1], caption="", hold=0.6),
]
json.dump({"image": "arch_base.png", "size": [BW, H1],
           "note": "boxes are [x0,y0,x1,y1] in arch_base.png pixels, all 16:9; hold = suggested seconds; caption/tag/pos (bl, tl, br, tr, r) are drawn in the arch_N.png previews",
           "keys": arch_keys}, open(f"{HERE}/arch_keys.json", "w"), indent=1)
keyframes("arch", "arch_base.png", BW, H1, arch_keys, ("textgrad", "symbolic", "debate", "ace"))

# ================================================================ Fig. 2 picture loop
fig2 = Image.open(f"{A}/fig2_6000.png").convert("RGB")
ytop, ybot = 160 * 3, 1462 * 3  # below the green title band, through the anatomy panel
crop2 = fig2.crop((0, ytop, BW, ybot)).copy()
# blank the legend panel (right of the anatomy panel)
Image.Image.paste(crop2, (255, 255, 255), (1272 * 3, (895 * 3) - ytop, BW, ybot - ytop))
H2 = ybot - ytop
W2 = round(H2 * 16 / 9)
padx = (W2 - BW) // 2
base2 = Image.new("RGB", (W2, H2), "white")
base2.paste(crop2, (padx, 0))
base2.save(f"{HERE}/picture_loop_base.png")


def d2(x0, y0, x1, y1):
    return [x0 * 3 + padx, (y0 - 160) * 3, x1 * 3 + padx, (y1 - 160) * 3]


# boxes in picture_loop_base.png pixels, read off zoom crops of the figure
pic_keys = [
    dict(box=[0, 0, W2, H2], caption="", hold=0.8),
    dict(box=fit169([600, 0, 3600, 1688], W2, H2), caption="Sketch → image prompt → Muse Image", hold=1.6),
    dict(box=fit169([3600, 238, 5600, 1363], W2, H2), caption="SAM maps every part, the critic checks", pos="tl", hold=1.6),
    dict(box=fit169([1667, 400, 5520, 1198], W2, H2), caption="Wrong picture: a gradient on the image prompt", tag="image-grad", pos="tr", hold=1.6),
    dict(box=fit169([2950, 320, 5650, 1839], W2, H2), caption="Keep or revert, part by part", pos="br", hold=1.0),
    dict(box=fit169([4400, 1146, 6452, 2300], W2, H2), caption="Wrong design: back to the team and the master prompt", hold=1.4),
    dict(box=fit169([573, 2257, 4243, 3889], W2, H2), caption="The final figure, panel by panel", pos="br", hold=1.2),
    dict(box=[0, 0, W2, H2], caption="", hold=0.5),
]
json.dump({"image": "picture_loop_base.png", "size": [W2, H2],
           "note": "boxes are [x0,y0,x1,y1] in picture_loop_base.png pixels, all 16:9; hold = suggested seconds; captions drawn in picture_loop_N.png previews",
           "keys": pic_keys}, open(f"{HERE}/picture_keys.json", "w"), indent=1)
keyframes("picture_loop", "picture_loop_base.png", W2, H2, pic_keys, ("opt2i", "idea2img", "som", "sam3"))
S.close()
print("cut", cut, "pad1", pad1, "W2", W2, "padx", padx)
