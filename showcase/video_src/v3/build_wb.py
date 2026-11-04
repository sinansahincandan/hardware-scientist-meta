"""Whiteboard frames, summary style (stair-climbing hand truck run 20261104-130101).

Each frame: the real board crop blurred in the background, ONE big visual element in front.
Board pictures: R/scripts/board_evolution.py replayed stage_a/iter_00 (meeting 1, rejected) into boards/m1 and
iter_01 (meeting 2, same board, accepted) into boards/m2. Counters come from the evolution.json files:
searches (web pages opened by a member) / calculations (calc, vetted_calc, simulate) / sketches.
Sources of the foreground elements:
  roster + tri-star note  = boards/m1/board_c1.png (board header, F4 first note by Kenji Tanaka)
  chosen ideas (stars)    = whiteboard.json selections, shown starred on boards/m1/board_c2.png
  five sketches           = stage_a/iter_00/evidence/sketch_24, 43, 52, 72, 87 (whitespace trimmed)
  reject reason           = stage_a/iter_00/verdict.json ("the folded length cannot contain its own backbone")
  folded sketch           = stage_a/iter_01/evidence/sketch_108.png (its own caption: backbone 1100 + cap 45 = 1145 mm)
  final render            = assets/gal_handtruck.png
"""
import glob
import json
import os

from PIL import Image, ImageOps

from common import HERE, Shooter, foot, icon, page, write

R = "/Users/sinancandan/Downloads/MetaHackathon_HardwareScientist_MetaCode"
RUN = R + "/runs/20261104-130101_stair-climbing-hand-truck-for-parcel-cou/stage_a"
B = os.path.join(HERE, "boards")
CROPS = os.path.join(B, "crops")
os.makedirs(CROPS, exist_ok=True)
BOX_W, BOX_H = 1728, 790  # picture area on the frame
EVO = {m: {r["cycle"]: r for r in json.load(open(os.path.join(B, m, "evolution.json")))} for m in ("m1", "m2")}

STAGES = ["Meeting 1", "Evaluator", "Meeting 2", "Accepted"]

FRAMES = [
    dict(stage=0, title="Four experts, one board", src=("m1", 1), crop=(20, 20, 1880), fg="experts"),
    dict(stage=0, title="One idea per function", src=("m1", 2), crop=(20, 225, 1880), fg="ideas"),
    dict(stage=0, title="Calculations and sketches", src=("m1", 4), crop=(20, 2170, 1840), fg="sketches"),
    dict(stage=1, title="Evaluator: reject", src=("m1", 4), crop=(20, 20, 1880), fg="reject"),
    dict(stage=2, title="Same board, folding rechecked", src=("m2", 1), crop=(20, 2343, 1880), fg="folded"),
    dict(stage=3, title="Accepted", src=("m2", 4), crop=(20, 20, 1880), fg="accept"),
]

EXPERTS = [("Mara Voss", "#1f6fd1"), ("Kenji Tanaka", "#1f9d63"), ("Elena Ruiz", "#d64545"), ("Tomas Lind", "#e0862a")]
STAIRS = ('<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="#1f6fd1" stroke-width="2" '
          'stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h5v-5h5v-5h5V6h3"/></svg>')
STAR = ('<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="#f2b705" stroke="#d99a00" stroke-width="1" '
        'stroke-linejoin="round"><path d="M12 2.5l2.9 6.2 6.6.8-4.9 4.6 1.3 6.6L12 17.4 6.1 20.7l1.3-6.6L2.5 9.5l6.6-.8z"/></svg>')
IDEAS = [("F1 · Support parcel", icon("package", 84, "#1f6fd1", 1.8), "Twin-tube L-frame backbone"),
         ("F2 · Restrain parcel", icon("cable", 84, "#1f6fd1", 1.8), "Webbing strap, cam buckle"),
         ("F3 · Move on flat", icon("truck", 84, "#1f6fd1", 1.8), "Paired solid-rubber wheels"),
         ("F4 · Traverse stairs", STAIRS.format(s=84), "Tri-star wheel cluster")]
SKETCHES = [24, 43, 52, 72, 87]

CSS = """
.kicker{top:46px}.title{top:80px;font-size:56px}
.tl{position:absolute;left:96px;top:162px;display:flex;align-items:center}
.tl .st{display:flex;align-items:center;gap:10px;font-size:19px;font-weight:700;color:var(--faint)}
.tl .dot{width:16px;height:16px;border-radius:50%;background:#d3d9e1;flex:none}
.tl .bar{width:44px;height:3px;background:#d3d9e1;margin:0 12px}
.tl .st.done{color:var(--mute)}.tl .st.done .dot{background:var(--mute)}
.tl .st.now{color:var(--ink)}.tl .st.now .dot{background:var(--blue);box-shadow:0 0 0 6px rgba(31,111,209,.18)}
.tl .st.now.ev .dot{background:var(--orange);box-shadow:0 0 0 6px rgba(224,102,42,.2)}
.tl .st.now.ok .dot{background:var(--green);box-shadow:0 0 0 6px rgba(31,157,99,.2)}
.cnt{position:absolute;right:96px;top:36px;display:flex;gap:34px}
.cnt>div{text-align:right}
.cnt .big{font-size:76px;color:var(--ink)}
.cnt .l{font-size:19px;color:var(--mute);margin-top:4px;font-weight:600;white-space:nowrap}
.cnt .d{font-size:26px;font-weight:800;color:var(--green);margin-left:8px;letter-spacing:0}
.cnt .d.z{color:var(--faint)}
.pic{position:absolute;left:96px;top:212px;width:1728px;height:790px;border:2px solid var(--line);border-radius:22px;
 overflow:hidden;background:#fff}
.pic .bgimg{position:absolute;inset:-20px;width:calc(100% + 40px);height:calc(100% + 40px);filter:blur(7px)}
.pic .veil{position:absolute;inset:0;background:rgba(255,255,255,.55)}
.fgw{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
.fc{background:#fff;border-radius:26px;box-shadow:0 24px 70px rgba(18,32,48,.22),0 4px 14px rgba(18,32,48,.10)}
/* 1 experts */
.ex{padding:46px 56px;display:flex;flex-direction:column;align-items:center;gap:44px;width:1320px}
.ex .row{display:flex;gap:26px}
.ex .chip{display:flex;align-items:center;gap:16px;border:2px solid var(--line);border-radius:999px;padding:10px 28px 10px 10px}
.ex .av{width:72px;height:72px;border-radius:50%;color:#fff;font-size:28px;font-weight:800;display:flex;align-items:center;justify-content:center}
.ex .nm{font-size:30px;font-weight:700;white-space:nowrap}
.ex img{height:400px;display:block;border-radius:6px}
/* 2 ideas */
.ideas{display:flex;gap:28px}
.tile{width:380px;height:470px;padding:40px 34px;position:relative;display:flex;flex-direction:column;align-items:flex-start}
.tile .ic{width:132px;height:132px;border-radius:30px;background:#eaf2fd;display:flex;align-items:center;justify-content:center}
.tile .fn{font-size:22px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);margin-top:44px}
.tile .tx{font-size:46px;font-weight:800;line-height:1.08;letter-spacing:-.02em;margin-top:14px}
.tile .star{position:absolute;right:26px;top:26px}
/* 3 sketches */
.sks{display:flex;gap:14px;align-items:center}
.sks .fc{padding:4px;border-radius:14px}.sks img{height:300px;display:block;border-radius:10px}
/* 4/6 stamps */
.stamp{transform:rotate(-7deg);border:16px solid;border-radius:40px;padding:26px 70px 34px;background:#fff;
 box-shadow:0 24px 70px rgba(18,32,48,.20)}
.stamp .s{font-size:170px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;line-height:1}
.stamp.bad{border-color:var(--red);color:var(--red)}
.stamp.good{border-color:var(--green);color:var(--green)}
.rj{display:flex;flex-direction:column;align-items:center;gap:70px}
.rj .line{font-size:46px;font-weight:700;color:#a83232;background:#fff;border-radius:18px;padding:14px 34px;
 box-shadow:0 10px 30px rgba(18,32,48,.12)}
/* 5 folded */
.fd{padding:30px;position:relative}
.fd img{height:560px;display:block}
.fd .lab{position:absolute;right:60px;bottom:58px;background:var(--green);color:#fff;font-size:48px;font-weight:800;
 border-radius:18px;padding:14px 32px;letter-spacing:-.01em;box-shadow:0 10px 30px rgba(31,157,99,.35)}
/* 6 accept */
.ac{position:relative;width:1700px;height:760px}
.ac .rd{position:absolute;right:0;top:50px;height:660px;border-radius:24px;box-shadow:0 24px 70px rgba(18,32,48,.25);display:block}
.ac .stamp{position:absolute;left:0;top:285px;padding:20px 40px 26px;border-width:13px}
.ac .stamp .s{font-size:100px}
"""


def crop(src, box, out):
    im = Image.open(os.path.join(B, src[0], f"board_c{src[1]}.png")).convert("RGB")
    x, y, w = box
    h = round(w * BOX_H / BOX_W)
    y = max(0, min(y, im.height - h))
    im.crop((x, y, x + w, y + h)).resize((BOX_W, BOX_H), Image.LANCZOS).save(out)


def prep():
    Image.open(os.path.join(B, "m1", "board_c1.png")).convert("RGB").crop((1440, 296, 1880, 465)).save(f"{CROPS}/note.png")
    for it, n in [("iter_00", k) for k in SKETCHES] + [("iter_01", 108)]:
        im = Image.open(f"{RUN}/{it}/evidence/sketch_{n}.png").convert("RGB")
        bb = ImageOps.invert(im.convert("L")).point(lambda v: 255 if v > 30 else 0).getbbox()
        p = 14
        im.crop((max(0, bb[0] - p), max(0, bb[1] - p), min(im.width, bb[2] + p), min(im.height, bb[3] + p))).save(f"{CROPS}/sk_{n}.png")


def fg(kind):
    if kind == "experts":
        chips = "".join(f'<div class="chip"><div class="av" style="background:{c}">{"".join(w[0] for w in n.split())}</div>'
                        f'<div class="nm" style="color:{c}">{n}</div></div>' for n, c in EXPERTS)
        return f'<div class="fc ex"><div class="row">{chips}</div><img src="file://{CROPS}/note.png"></div>'
    if kind == "ideas":
        return '<div class="ideas">' + "".join(
            f'<div class="fc tile"><div class="star">{STAR.format(s=78)}</div><div class="ic">{ic}</div>'
            f'<div class="fn">{fn}</div><div class="tx">{tx}</div></div>' for fn, ic, tx in IDEAS) + "</div>"
    if kind == "sketches":
        return '<div class="sks">' + "".join(f'<div class="fc"><img src="file://{CROPS}/sk_{n}.png"></div>' for n in SKETCHES) + "</div>"
    if kind == "reject":
        return ('<div class="rj"><div class="stamp bad"><div class="s">Rejected</div></div>'
                '<div class="line">the folded size does not add up</div></div>')
    if kind == "folded":
        return (f'<div class="fc fd"><img src="file://{CROPS}/sk_108.png"><div class="lab">1145 mm, part by part</div></div>')
    if kind == "accept":
        return (f'<div class="ac"><img class="rd" src="file://{HERE}/assets/gal_handtruck.png">'
                '<div class="stamp good"><div class="s">Accepted</div></div></div>')


def frame(i, f, prev):
    tl = []
    for k, s in enumerate(STAGES):
        cls = "now" if k == f["stage"] else ("done" if k < f["stage"] else "")
        if k == f["stage"] == 1:
            cls += " ev"
        if k == f["stage"] == 3:
            cls += " ok"
        tl.append(f'<div class="st {cls}"><span class="dot"></span>{s}</div>')
    tl = '<div class="tl">' + '<span class="bar"></span>'.join(tl) + "</div>"
    ev = EVO[f["src"][0]][f["src"][1]]
    vals = (ev["searches"], ev["calculations"], ev["sketches"])
    labs = ("sources read", "calculations", "sketches")
    cells = []
    for v, p, lab in zip(vals, prev, labs):
        d = "" if p is None else (f'<span class="d">+{v - p}</span>' if v > p else '<span class="d z">+0</span>')
        cells.append(f'<div><div class="big">{v}{d}</div><div class="l">{lab}</div></div>')
    cnt = '<div class="cnt">' + "".join(cells) + "</div>"
    img = os.path.join(CROPS, f"wb_{i}.png")
    crop(f["src"], f["crop"], img)
    body = (f'<div class="kicker">The whiteboard never resets · stair-climbing hand truck</div>'
            f'<h1 class="title">{f["title"]}</h1>{tl}{cnt}'
            f'<div class="pic"><img class="bgimg" src="file://{img}"><div class="veil"></div>'
            f'<div class="fgw">{fg(f["fg"])}</div></div>'
            + foot("debate", "reflexion", "textgrad"))
    return page(body, CSS), vals


prep()
S = Shooter()
outs, prev = [], (None, None, None)
for i, f in enumerate(FRAMES, 1):
    html, vals = frame(i, f, prev)
    outs += S.shoot(write(f"whiteboard_{i}.html", html), f"{HERE}/whiteboard_{i}.png")
    print(i, f["title"], vals, [None if p is None else v - p for v, p in zip(vals, prev)])
    prev = vals
S.close()
for old in glob.glob(f"{HERE}/whiteboard_*.png"):
    n = os.path.basename(old)[11:-4]
    if n.isdigit() and int(n) > len(FRAMES):
        os.remove(old)

ims = [Image.open(o).convert("RGB").resize((1280, 720), Image.LANCZOS) for o in outs]
pal = [im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in ims]
pal[0].save(f"{HERE}/whiteboard.gif", save_all=True, append_images=pal[1:], duration=[2600] * len(pal), loop=0, optimize=True)
print(outs)
