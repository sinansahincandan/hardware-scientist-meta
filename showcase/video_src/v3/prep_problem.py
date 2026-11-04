"""Set-of-Mark overlays for the problem frame, from real SAM 3.1 masks (no model calls here).

Writes assets/som_turbine.png, som_excavator.png (RGBA, render size), som_marks.json (disc centres),
and assets/fx_r1.png, fx_r2.png (fingertip run rounds 1, 2 with the signal tail tinted).
"""
import json
import os

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
S = os.path.join(os.path.dirname(HERE), "samslide1")
RUN = ("/Users/sinancandan/Downloads/MetaHackathon_HardwareScientist_MetaCode/runs/"
       "20261103-234446_tactile-fingertip-sensor-for-robot-hands/stage_b/attempt_00")
PAL = [(31, 111, 209), (224, 102, 42), (123, 79, 214), (31, 157, 99)]


def tint(masks, size, outline=7, alpha=0.55):
    out = np.zeros((size[1], size[0], 4), np.uint8)
    for m, c in masks:
        ring = np.array(Image.fromarray(m.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(outline))) > 127
        edge = ring & ~np.array(Image.fromarray(m.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(3))).astype(bool)
        out[m] = (*c, int(255 * alpha))
        out[edge] = (*c, 255)
    return Image.fromarray(out, "RGBA")


def split(mask_path, order):
    m = np.array(Image.open(mask_path).convert("L")) > 127
    lab, n = ndimage.label(m)
    comps = [lab == i for i in range(1, n + 1) if (lab == i).sum() > 500]
    comps.sort(key=order)
    return comps


marks = {}
# turbine: four blades, numbered clockwise from the top
tb = split(f"{S}/turbine/sam_masks/blade.png",
           lambda c: np.arctan2(np.nonzero(c)[1].mean() - 790, -(np.nonzero(c)[0].mean() - 630)) % (2 * np.pi))
tint([(c, PAL[i]) for i, c in enumerate(tb)], (1920, 1280)).save(f"{A}/som_turbine.png")
marks["turbine"] = [[float(np.nonzero(c)[1].mean()), float(np.nonzero(c)[0].mean())] for c in tb]
# excavator: two hoppers, left (on the body) first
ex = split(f"{S}/excavator/sam_masks/hopper.png", lambda c: np.nonzero(c)[1].mean())
tint([(c, PAL[i]) for i, c in enumerate(ex)], (1920, 1280)).save(f"{A}/som_excavator.png")
marks["excavator"] = [[float(np.nonzero(c)[1].mean()), float(np.nonzero(c)[0].mean())] for c in ex]

# fingertip rounds 1 -> 2: tint the signal tail, record its lowest point
for r, col, name in [("01", (31, 157, 99), "fx_r1"), ("02", (214, 69, 69), "fx_r2")]:
    im = Image.open(f"{RUN}/round_{r}/render.png").convert("RGBA")
    m = np.array(Image.open(f"{RUN}/round_{r}/sam_masks/tail.png").convert("L")) > 127
    Image.alpha_composite(im, tint([(m, col)], im.size, alpha=0.35)).convert("RGB").save(f"{A}/{name}.png")
    ys, xs = np.nonzero(m)
    k = ys.argmax()
    marks[name] = [float(xs[ys > ys.max() - 40].mean()), float(ys.max())]

json.dump(marks, open(f"{A}/som_marks.json", "w"), indent=1)
print(json.dumps(marks))
