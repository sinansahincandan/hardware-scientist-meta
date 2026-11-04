import json, statistics as st, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; V = S + "/video"
d = json.load(open("runs/bench5_summary.json")); a, b = d["pass1"], d["pass2"]
P = ["01", "02", "03", "b1", "b2", "b3"]
names = ["Stair hand\ntruck", "Solar\ncold room", "Footbridge\ndamper", "Lunar\nexcavator", "Robot\nfingertip", "Wind\nturbine"]
HS, BL = "#1f6fd1", "#9aa5b1"
fig, ax = plt.subplots(figsize=(10.4, 6.2), dpi=150)
for i, p in enumerate(P):
    for j, (w, c, lab) in enumerate([("baseline", BL, "One Meta prompt"), ("hs", HS, "Hardware Scientist")]):
        v1, v2 = a[p][w]["total"], b[p][w]["total"]; m = (v1 + v2) / 2; x = i + (j - 0.5) * 0.36
        ax.bar(x, m, 0.34, color=c, label=lab if i == 0 else None, zorder=2)
        ax.plot([x, x], [min(v1, v2), max(v1, v2)], color="#16202c", lw=2, zorder=3)
        ax.text(x, max(v1, v2) + 0.4, f"{m:g}", ha="center", fontsize=12, color="#16202c")
ax.set_xticks(range(6)); ax.set_xticklabels(names, fontsize=12)
ax.set_ylim(0, 40); ax.set_ylabel("score of 40 (bar: mean of two judges · line: their range)", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.yaxis.grid(True, color="#e3e7ec", zorder=0); ax.legend(frameon=False, fontsize=12, loc="upper left", ncol=2)
plt.tight_layout(); plt.savefig(f"{V}/bench_chart.png"); plt.close()
F = "/System/Library/Fonts/Supplemental/Arial.ttf"; FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
im = Image.new("RGB", (1920, 1080), (246, 247, 249)); dr = ImageDraw.Draw(im)
dr.text((96, 44), "SIX PROBLEMS · TWO BLIND JUDGES · EVERY NUMBER RE-DERIVED BEFORE ANY SCORE", font=ImageFont.truetype(FB, 24), fill=(31, 111, 209))
dr.text((96, 80), "Against one Meta prompt: even on average, ahead where numbers and pictures are checked", font=ImageFont.truetype(FB, 40), fill=(22, 32, 44))
ch = Image.open(f"{V}/bench_chart.png"); ch = ch.resize((1120, round(ch.size[1] * 1120 / ch.size[0])), Image.LANCZOS); im.paste(ch, (60, 170))
x = 1220; y = 180
avg = d["avg"]; hs = [avg[p]["hs"] for p in P]; bl = [avg[p]["baseline"] for p in P]
diff = [h - g for h, g in zip(hs, bl)]; pct = [100 * (h / g - 1) for h, g in zip(hs, bl)]
lines = [("Mean of 40, over six problems", FB, 26, (22, 32, 44)),
         (f"Hardware Scientist  {st.mean(hs):.1f} ± {st.stdev(hs):.1f}", FB, 30, (31, 111, 209)),
         (f"One Meta prompt      {st.mean(bl):.1f} ± {st.stdev(bl):.1f}", FB, 30, (91, 104, 120)),
         (f"Gain per problem  {st.mean(pct):+.0f}% ± {st.stdev(pct):.0f}%  (a tie)", F, 26, (22, 32, 44)),
         ("Judges preferred HS in 7 of 12 verdicts.", F, 26, (22, 32, 44))]
for t, f, s, c in lines:
    dr.text((x, y), t, font=ImageFont.truetype(f, s), fill=c); y += s + 18
y += 10
dr.text((x, y), "Sum over six problems, of 30 (mean of judges)", font=ImageFont.truetype(FB, 24), fill=(22, 32, 44)); y += 40
crit = [("Numbers right and supported", "C3"), ("Picture shows the design", "C4"), ("No image-generator mistakes", "C8"),
        ("Meets the limits, shown", "C1"), ("Explains how it works", "C6"), ("How it is made", "C7")]
dr.text((x + 420, y), "HS", font=ImageFont.truetype(FB, 22), fill=(31, 111, 209)); dr.text((x + 510, y), "one prompt", font=ImageFont.truetype(FB, 22), fill=(91, 104, 120)); y += 34
for lab, c in crit:
    h = sum(a[p]["hs"]["C"][c] + b[p]["hs"]["C"][c] for p in P) / 2; g = sum(a[p]["baseline"]["C"][c] + b[p]["baseline"]["C"][c] for p in P) / 2
    col = (23, 122, 76) if h > g else (192, 59, 59) if h < g else (22, 32, 44)
    dr.text((x, y), lab, font=ImageFont.truetype(F, 24), fill=(51, 64, 79)); dr.text((x + 420, y), f"{h:g}", font=ImageFont.truetype(FB, 24), fill=col); dr.text((x + 510, y), f"{g:g}", font=ImageFont.truetype(F, 24), fill=(51, 64, 79)); y += 36
y += 16
for t in ["Next target: concrete making plans (HS 19.5 vs 24).", "HS on open weights: 19.2 of 40 on three problems.",
          "The same two judges differ by 2.2 points per design on", "average, so one judge alone cannot separate the systems."]:
    dr.text((x, y), t, font=ImageFont.truetype(F, 23), fill=(74, 85, 99)); y += 32
dr.text((96, 1010), "Round 4 (one judge, no fault audit, three problems) had shown +16%; the stricter audit with a second judge does not confirm it.", font=ImageFont.truetype(F, 22), fill=(91, 104, 120))
im.save(f"{V}/benchmark.png")
print([round(x,1) for x in pct])
