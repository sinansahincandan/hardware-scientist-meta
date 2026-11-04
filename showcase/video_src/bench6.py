"""Round-6 benchmark summary and slide (no model call).

Reads the four blind judge files (two passes, each pass split over two judges) and the A/B/C key, writes
showcase/bench/round6/bench6_summary.json and a 1920x1080 slide.
Usage: python showcase/video_src/bench6.py <out_png>
"""
import json
import statistics as st
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

R = Path("runs")
key = json.loads((R / "bench6_key.json").read_text())
passes = {"pass1": ["p1a", "p1b"], "pass2": ["p2a", "p2b"]}
P = ["01", "02", "03", "b1", "b2", "b3"]
WHO = ["baseline", "hs", "hs_open"]
C = [f"C{i}" for i in range(1, 9)]


def by_system(files):
    out = {}
    for f in files:
        for pid, labels in json.loads((R / f"bench6_scores_{f}.json").read_text()).items():
            for lab, s in labels.items():
                who = key[pid][lab]
                sev = [x["severity"] for x in s["faults"]]
                out.setdefault(pid, {})[who] = {
                    "total": sum(s[c]["score"] for c in C), "C": {c: s[c]["score"] for c in C},
                    "fatal": sev.count("fatal"), "major": sev.count("major")}
    return out


res = {k: by_system(v) for k, v in passes.items()}
avg = {p: {w: st.mean([res[k][p][w]["total"] for k in res]) for w in WHO if w in res["pass1"][p]} for p in P}
summary = {"key": key, **res, "avg": avg}
for w in WHO:
    vals = [avg[p][w] for p in P if w in avg[p]]
    summary[f"mean_{w}"] = [st.mean(vals), st.stdev(vals) if len(vals) > 1 else 0, len(vals)]
    summary[f"faults_{w}"] = {s: sum(res[k][p][w][s] for k in res for p in P if w in res[k][p]) / 2
                              for s in ("fatal", "major")}
gain = [100 * (avg[p]["hs"] / avg[p]["baseline"] - 1) for p in P]
summary["gain_pct"] = [st.mean(gain), st.stdev(gain)]
wins = sum(res[k][p]["hs"]["total"] > res[k][p]["baseline"]["total"] for k in res for p in P)
ties = sum(res[k][p]["hs"]["total"] == res[k][p]["baseline"]["total"] for k in res for p in P)
summary["hs_wins_of_12"], summary["ties"] = wins, ties
summary["crit_sums"] = {w: {c: sum(res[k][p][w]["C"][c] for k in res for p in P) / 2 for c in C} for w in ("hs", "baseline")}
out_dir = Path("showcase/bench/round6")
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "bench6_summary.json").write_text(json.dumps(summary, indent=1))
print(json.dumps({k: v for k, v in summary.items() if k not in ("key", "pass1", "pass2")}, indent=1))

names = ["Stair hand\ntruck", "Solar\ncold room", "Footbridge\ndamper", "Lunar\nexcavator", "Robot\nfingertip", "Wind\nturbine"]
COL = {"baseline": ("#9aa5b1", "One Meta prompt"), "hs": ("#1f6fd1", "Hardware Engineer"),
       "hs_open": ("#e0662a", "HE, open weights")}
fig, ax = plt.subplots(figsize=(10.4, 6.2), dpi=150)
for i, p in enumerate(P):
    for j, w in enumerate(WHO):
        x = i + (j - 1) * 0.27
        if w not in avg[p]:
            ax.text(x + 0.06, 1, "no design\nin budget", ha="center", fontsize=7.5, color="#e0662a", zorder=5)
            continue
        v = [res[k][p][w]["total"] for k in res]
        ax.bar(x, avg[p][w], 0.25, color=COL[w][0], label=COL[w][1] if i == 3 else None, zorder=2)
        ax.plot([x, x], [min(v), max(v)], color="#16202c", lw=2, zorder=3)
        ax.text(x, max(v) + 0.4, f"{avg[p][w]:g}", ha="center", fontsize=10, color="#16202c")
ax.set_xticks(range(6))
ax.set_xticklabels(names, fontsize=12)
ax.set_ylim(0, 40)
ax.set_ylabel("score of 40 (bar: mean of two judges · line: their range)", fontsize=11)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.yaxis.grid(True, color="#e3e7ec", zorder=0)
ax.legend(frameon=False, fontsize=12, loc="upper left", ncol=3)
plt.tight_layout()
chart = out_dir / "bench6_chart.png"
plt.savefig(chart)
plt.close()

F = "/System/Library/Fonts/Supplemental/Arial.ttf"
FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
im = Image.new("RGB", (1920, 1080), (246, 247, 249))
dr = ImageDraw.Draw(im)
hs_m, bl_m, op_m = summary["mean_hs"], summary["mean_baseline"], summary["mean_hs_open"]
dr.text((96, 44), "SIX PROBLEMS · TWO BLIND JUDGES · FAULT AUDIT BEFORE ANY SCORE", font=ImageFont.truetype(FB, 24),
        fill=(31, 111, 209))
dr.text((96, 80), sys.argv[2] if len(sys.argv) > 2 else "", font=ImageFont.truetype(FB, 40), fill=(22, 32, 44))
ch = Image.open(chart)
ch = ch.resize((1120, round(ch.size[1] * 1120 / ch.size[0])), Image.LANCZOS)
im.paste(ch, (60, 170))
x, y = 1220, 180
fh, fb = summary["faults_hs"], summary["faults_baseline"]
lines = [("Mean of 40, over six problems", FB, 26, (22, 32, 44)),
         (f"Hardware Engineer   {hs_m[0]:.1f} ± {hs_m[1]:.1f}", FB, 30, (31, 111, 209)),
         (f"One Meta prompt      {bl_m[0]:.1f} ± {bl_m[1]:.1f}", FB, 30, (91, 104, 120)),
         (f"HE, open weights      {op_m[0]:.1f} ± {op_m[1]:.1f}  ({op_m[2]} of 6)", FB, 26, (224, 102, 42)),
         (f"Gain per problem  {summary['gain_pct'][0]:+.0f}% ± {summary['gain_pct'][1]:.0f}%", F, 26, (22, 32, 44)),
         (f"HE ahead in {wins} of 12 verdicts, {ties} tied.", F, 26, (22, 32, 44)),
         (f"Fatal + major faults per judge: HE {fh['fatal'] + fh['major']:g}, one prompt {fb['fatal'] + fb['major']:g}",
          F, 24, (22, 32, 44))]
for t, f, s, c in lines:
    dr.text((x, y), t, font=ImageFont.truetype(f, s), fill=c)
    y += s + 18
y += 10
dr.text((x, y), "Sum over six problems, of 30 (mean of judges)", font=ImageFont.truetype(FB, 24), fill=(22, 32, 44))
y += 40
crit = [("Numbers right and supported", "C3"), ("Picture shows the design", "C4"), ("No image-generator mistakes", "C8"),
        ("Meets the limits, shown", "C1"), ("Physically works", "C2"), ("How it is made", "C7")]
dr.text((x + 420, y), "HE", font=ImageFont.truetype(FB, 22), fill=(31, 111, 209))
dr.text((x + 510, y), "one prompt", font=ImageFont.truetype(FB, 22), fill=(91, 104, 120))
y += 34
for lab, c in crit:
    h, g = summary["crit_sums"]["hs"][c], summary["crit_sums"]["baseline"][c]
    col = (23, 122, 76) if h > g else (192, 59, 59) if h < g else (22, 32, 44)
    dr.text((x, y), lab, font=ImageFont.truetype(F, 24), fill=(51, 64, 79))
    dr.text((x + 420, y), f"{h:g}", font=ImageFont.truetype(FB, 24), fill=col)
    dr.text((x + 510, y), f"{g:g}", font=ImageFont.truetype(F, 24), fill=(51, 64, 79))
    y += 36
dr.text((96, 870), "Since round 5 (same one-prompt designs, new judges): HE making plans 19.5 → 22 of 30; "
        "HE on open weights 19.2 → 26.1 of 40.", font=ImageFont.truetype(F, 24), fill=(22, 32, 44))
dr.text((96, 1010), "Judges are Claude agents with rubric v3; they never see which system made a design. "
        "Open weights: the stair truck and turbine ran out of the $80 budget before an accepted design.",
        font=ImageFont.truetype(F, 21), fill=(91, 104, 120))
im.save(sys.argv[1])
