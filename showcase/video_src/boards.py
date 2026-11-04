import json, sys
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]
F = "/System/Library/Fonts/Supplemental/Arial.ttf"; FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
ev = {w: {c["cycle"]: c for c in json.load(open(f"{S}/{w}/evolution.json"))} for w in ("wb0", "wb1")}
picks = [("wb0", 1, "Meeting 1 · cycle 1"), ("wb0", 2, "Meeting 1 · cycle 2"), ("wb0", 4, "Meeting 1 · closed, sent to the Evaluator"),
         ("wb1", 1, "Meeting 2 · same board, after the prompt rewrite"), ("wb1", 3, "Meeting 2 · closed · accepted")]
for i, (w, c, title) in enumerate(picks):
    b = Image.open(f"{S}/{w}/board_c{c}.png").convert("RGB")
    out = Image.new("RGB", (1920, 1080), (246, 247, 249))
    k = 1040 / b.size[1]
    out.paste(b.resize((round(b.size[0] * k), 1040), Image.LANCZOS), (40, 20))
    left = 40 + round(b.size[0] * k) + 40
    d = ImageDraw.Draw(out)
    d.text((left, 40), "THE WHITEBOARD NEVER RESETS", font=ImageFont.truetype(FB, 24), fill=(31, 111, 209))
    d.text((left, 80), title, font=ImageFont.truetype(FB, 46), fill=(22, 32, 44))
    e = ev[w][c]
    stats = [("sources read", e["searches"]), ("calculations", e["calculations"]), ("sketches", e["sketches"]), ("concepts", e["concepts"])]
    for j, (lab, v) in enumerate(stats):
        x = left + j * 300
        d.text((x, 160), str(v), font=ImageFont.truetype(FB, 72), fill=(22, 32, 44))
        d.text((x, 245), lab, font=ImageFont.truetype(F, 26), fill=(91, 104, 120))
    crop = b.crop((0, int(b.size[1] * 0.775), b.size[0], b.size[1] - 30))
    cw = 1920 - left - 40
    ch = round(crop.size[1] * cw / crop.size[0])
    if ch > 1080 - 320 - 30:
        ch = 1080 - 320 - 30; cw2 = round(crop.size[0] * ch / crop.size[1]); crop = crop.resize((cw2, ch), Image.LANCZOS)
    else:
        crop = crop.resize((cw, ch), Image.LANCZOS)
    d.text((left, 300), "calculations and sketches pinned on the board (bottom of the board, enlarged)", font=ImageFont.truetype(F, 22), fill=(91, 104, 120))
    out.paste(crop, (left, 338))
    out.save(f"{S}/video/board_{i + 1}.png")
    print(i + 1, title, stats)
