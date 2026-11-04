"""benchmark (Meta API vs open weights), open, close frames (1920x1080).

Usage: python build_simple.py [benchmark] [open] [close]
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from common import A, HERE, Shooter, page, write  # noqa: E402

R = "/Users/sinancandan/Downloads/MetaHackathon_HardwareScientist_MetaCode"
ONLY = set(sys.argv[1:])
OUT = HERE
BLUE, ORANGE = "#1f6fd1", "#e0662a"


def want(n):
    return not ONLY or n in ONLY


S = Shooter()

# ---------------------------------------------------------------- benchmark chart
if want("benchmark"):
    d = json.load(open(f"{R}/showcase/bench/round6/bench6_summary.json"))
    m_api, s_api, n_api = d["mean_hs"]
    m_open, s_open, n_open = d["mean_hs_open"]
    pids = ["01", "02", "03", "b1", "b2", "b3"]
    pts_api = [d["avg"][p]["hs"] for p in pids if d["avg"][p].get("hs") is not None]
    pts_open = [d["avg"][p]["hs_open"] for p in pids if d["avg"][p].get("hs_open") is not None]
    print("Meta API     :", round(m_api, 2), "+-", round(s_api, 2), "n =", n_api, "points", pts_api)
    print("Open weights :", round(m_open, 2), "+-", round(s_open, 2), "n =", n_open, "points", pts_open)

    from matplotlib import font_manager
    fams = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = next((f for f in ("DM Sans", "Helvetica Neue", "Helvetica", "Arial") if f in fams), "DejaVu Sans")

    fig, ax = plt.subplots(figsize=(11.0, 7.4), dpi=100)
    fig.patch.set_facecolor("#f5f6f8")
    ax.set_facecolor("#f5f6f8")
    xs = [0, 1]
    means, stds, cols = [m_api, m_open], [s_api, s_open], [BLUE, ORANGE]
    ax.bar(xs, means, width=0.5, color=cols, alpha=0.88, zorder=2)
    ax.errorbar(xs, means, yerr=stds, fmt="none", ecolor="#122030", elinewidth=2.2, capsize=12, capthick=2.2, zorder=3)
    # per-problem points beside each bar, fixed (deterministic) horizontal spread
    for x, pts, c in ((0, pts_api, BLUE), (1, pts_open, ORANGE)):
        k = len(pts)
        offs = [0.42 + 0.04 * (i - (k - 1) / 2) for i in range(k)]
        ax.scatter([x + o for o in offs], pts, s=120, color=c, edgecolor="white", linewidth=1.6, zorder=4)
    for x, m, s in zip(xs, means, stds):
        ax.text(x, m + s + 0.8, f"{m:.1f} ± {s:.1f}", ha="center", va="bottom", fontsize=26, fontweight="bold", color="#122030")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"Meta Model API\n{n_api} problems", f"Open weights: Baseten + Modal\n{n_open} problems"], fontsize=20, color="#122030")
    ax.set_ylabel("score of 40 · two blind judges", fontsize=19, color="#5d6b7c", labelpad=14)
    ax.set_ylim(0, 40)
    ax.set_xlim(-0.5, 1.6)
    ax.set_yticks(range(0, 41, 10))
    ax.tick_params(axis="y", labelsize=17, colors="#5d6b7c")
    ax.tick_params(axis="x", length=0, pad=12)
    ax.grid(axis="y", color="#dbe1e8", linewidth=1.2, zorder=0)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#8d98a6")
    ax.text(0.31, min(pts_api) - 1.6, "each dot:\none problem", ha="left", va="top", fontsize=16, color="#8d98a6")
    fig.tight_layout()
    fig.savefig(os.path.join(A, "bench_chart.png"), facecolor=fig.get_facecolor())
    plt.close(fig)

    css = """
.chart{position:absolute;left:60px;top:230px;width:1100px}
.side{position:absolute;left:1240px;top:400px;width:600px;display:flex;flex-direction:column;gap:44px}
.side div{font-size:34px;line-height:1.25;font-weight:500;padding-left:26px;border-left:6px solid var(--line)}
.side div:first-child{border-color:var(--orange);font-weight:700}
"""
    body = """<div class="kicker">Open weights · Baseten</div>
<h1 class="title">The same loops on open weights reach the same level.</h1>
<img class="chart" src="../assets/bench_chart.png">
<div class="side"><div>Muse Spark Open on Baseten, SAM 3 on Modal</div>
<div>4 of 6 problems finished within the open-weights budget</div>
<div>Judges: rubric v3, fault audit before any score</div></div>
<div class="foot">Built with Muse Spark Open · judges never see which system made a design</div>"""
    S.shoot(write("benchmark.html", page(body, css)), f"{OUT}/benchmark.png")

# ---------------------------------------------------------------- open weights
if want("open"):
    css = """
.cols{position:absolute;left:48px;top:300px;width:1824px;display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.c img.a{width:100%;aspect-ratio:1580/1030;object-fit:cover;border-radius:18px 18px 0 0;display:block}
.c img.d{width:100%;display:block;border-radius:0 0 18px 18px;border-top:4px solid #fff}
.c span{display:block;font-size:30px;font-weight:700;margin-top:18px}
"""
    names = [("b1", "Excavator, vibrating scraper"), ("b2", "Fingertip, clear taxel dome"), ("b3", "Hand-held turbine")]
    cols = "".join(f'<div class="c"><img class="a" src="../assets/open_{k}_A.png"><img class="d" src="../assets/open_{k}_D.png"><span>{t}</span></div>' for k, t in names)
    body = f"""<div class="kicker">Open weights</div>
<h1 class="title">Also runs on Meta's open weights.</h1>
<div class="cols">{cols}</div>
<div class="foot">Built with Muse Spark Open · Muse Spark Open served on Baseten, SAM 3 on Modal · same architecture and loops</div>"""
    S.shoot(write("open.html", page(body, css)), f"{OUT}/open.png")

# ---------------------------------------------------------------- close
if want("close"):
    css = """
body{background:#eef1f4}
.r{position:absolute;left:0;width:1920px;display:flex;gap:6px}
.r img{height:100%;object-fit:cover;display:block;flex:1;min-width:0}
.band{position:absolute;left:0;right:0;top:306px;height:468px;background:var(--bg);
 display:flex;flex-direction:column;justify-content:center;padding:0 120px}
.band .l1{font-size:72px;font-weight:800;letter-spacing:-.03em;line-height:1.08}
.band .l2{font-size:64px;font-weight:800;letter-spacing:-.03em;line-height:1.1;color:var(--blue);margin-top:14px}
.band .l3{font-size:52px;font-weight:800;letter-spacing:-.025em;line-height:1.1;color:var(--blue);margin-top:8px}
.band .mm{font-size:26px;color:var(--mute);margin-top:34px;font-weight:500;letter-spacing:.02em}
"""
    top = ["gal_excavator", "gal_turbine", "gal_fingertip", "gal_coldroom", "gal_handtruck"]
    bot = ["open_b1_A", "gal_damper", "open_b2_A", "open_b3_A"]
    imgs_top = "".join(f'<img src="../assets/{n}.png">' for n in top)
    imgs_bot = "".join(f'<img src="../assets/{n}.png">' for n in bot)
    body = (f'<div class="r" style="top:0;height:300px">{imgs_top}</div>'
            f'<div class="r" style="top:780px;height:300px">{imgs_bot}</div>'
            """<div class="band"><div class="l1">The engineer gives the what.</div>
<div class="l2">Hardware Engineer works out the how,</div>
<div class="l3">and learns your engineering practice, design after design.</div>
<div class="mm">Muse Spark 1.3 &nbsp;·&nbsp; Muse Image 1.0 &nbsp;·&nbsp; SAM 3.1</div></div>""")
    S.shoot(write("close.html", page(body, css)), f"{OUT}/close.png")

S.close()
print("ok")
