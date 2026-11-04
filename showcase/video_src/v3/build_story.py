"""hook, simple, sam, fingertip, gallery, open, close frames (1920x1080)."""
import json
import sys

from PIL import Image

from common import A, HERE, Shooter, foot, icon, page, write

ONLY = set(sys.argv[1:])
S = Shooter()
OUT = HERE


def want(n):
    return not ONLY or n in ONLY


def bgcol(path, xy):
    r, g, b = Image.open(path).convert("RGB").getpixel(xy)[:3]
    return f"rgb({r},{g},{b})"


# ---------------------------------------------------------------- hook
if want("hook"):
    css = """
.colh{font-size:24px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--blue);margin-bottom:18px}
.inh{position:absolute;left:96px;top:176px}
.in{position:absolute;left:96px;top:226px;width:590px;height:640px;padding:60px 40px}
.in .mark{font-family:Georgia,serif;font-size:170px;line-height:.8;color:var(--blue);height:100px}
.in .t{font-size:31px;font-weight:700;line-height:1.3;letter-spacing:-.02em;white-space:nowrap}
.in .chips{position:absolute;left:40px;bottom:44px;display:flex;flex-direction:column;gap:14px}
.in .pill{background:var(--bg);border:2px solid var(--line);font-size:27px;color:var(--ink);padding:10px 22px;width:max-content}
.he{position:absolute;left:770px;top:321px;width:330px;height:440px;background:var(--ink);color:#fff;border-radius:26px;padding:42px 36px}
.he .n{font-size:40px;font-weight:800;line-height:1.05;letter-spacing:-.02em;margin-bottom:34px}
.he .r{display:flex;align-items:center;gap:18px;font-size:26px;line-height:1.2;margin-top:26px;color:#dfe6ee}
.he .r svg{flex:none}
.arr{position:absolute;top:517px}
.out{position:absolute;left:1184px;top:176px;width:640px}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.tile{background:#fff;border:2px solid var(--line);border-radius:18px;overflow:hidden}
.tile .ph{height:252px;background:#fff}
.tile .ph img{width:100%;height:100%;object-fit:cover;display:block}
.tile .c{font-size:25px;font-weight:700;padding:10px 16px 12px}
"""
    arrow = """<svg width="70" height="48" viewBox="0 0 70 48"><path d="M4 24 H54" stroke="#1f6fd1" stroke-width="8" stroke-linecap="round"/>
<path d="M40 8 L62 24 L40 40" fill="none" stroke="#1f6fd1" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
    tiles = [("gal_fingertip.png", "Labelled figure", "50% 50%"), ("ft_B.png", "The critical part", "50% 40%"),
             ("ft_step3.png", "How it is made", "50% 45%"), ("ft_board.png", "Whiteboard record", "0% 0%")]
    tl = "".join(f'<div class="tile"><div class="ph"><img src="../assets/{f}" style="object-position:{pos}"></div>'
                 f'<div class="c">{c}</div></div>' for f, c, pos in tiles)
    body = f"""<div class="kicker">Hardware Engineer</div>
<div class="inh colh">What goes in</div>
<div class="in card"><div class="mark">“</div>
<div class="t">Robot hands crush what they hold.<br>Design a fingertip that feels touch.</div>
<div class="chips"><span class="pill">{icon('hand', 28, '#1f6fd1')} fingertip-sized</span>
<span class="pill">{icon('crosshair', 28, '#1f6fd1')} feels 1 mN</span></div></div>
<div class="arr" style="left:692px">{arrow}</div>
<div class="he"><div class="n">Hardware<br>Engineer</div>
<div class="r">{icon('users', 36, '#7fb2f0')} expert team on one whiteboard</div>
<div class="r">{icon('clipboard-check', 36, '#7fb2f0')} a reviewer</div>
<div class="r">{icon('image', 36, '#7fb2f0')} a picture loop</div></div>
<div class="arr" style="left:1108px">{arrow}</div>
<div class="out"><div class="colh">What comes out</div><div class="tiles">{tl}</div></div>
{foot()}"""
    S.shoot(write("hook_1.html", page(body, css)), f"{OUT}/hook_1.png")

    bg = bgcol(f"{A}/gal_fingertip.png", (60, 640))
    css = f"""
body{{background:{bg}}}
.fig{{position:absolute;left:250px;top:0;height:1080px;
 -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 6%,#000 94%,transparent 100%)}}
.hl{{position:absolute;left:96px;top:96px;font-size:58px;font-weight:800;line-height:1.08;letter-spacing:-.025em}}
.hl span{{color:var(--blue)}}
.sub{{position:absolute;left:96px;top:330px;font-size:28px;color:var(--mute)}}
.foot{{color:#7d8794;left:auto;right:64px;text-align:right}}
"""
    body = f"""<img class="fig" src="../assets/gal_fingertip.png">
<div class="kicker">Hardware Engineer</div>
<div class="hl">One paragraph in.<br><span>An engineered<br>concept out.</span></div>
<div class="sub">a robot fingertip that feels a 1 mN touch</div>
{foot()}"""
    S.shoot(write("hook_2.html", page(body, css)), f"{OUT}/hook_2.png")


# ---------------------------------------------------------------- the problem with one prompt (2 states)
# overlays come from prep_problem.py (real SAM 3.1 masks: 4 blades, 2 hoppers; fingertip run rounds 1 -> 2)
if want("problem"):
    mk = json.load(open(f"{A}/som_marks.json"))
    PAL = ["#1f6fd1", "#e0662a", "#7b4fd6", "#1f9d63"]
    css = """
.g1,.g2{position:absolute;left:0;top:0;width:1920px;height:1080px;transition:none}
body.st1 .g2,body.st2 .g1{display:none}
.im{position:absolute;top:236px;width:840px;height:560px;border-radius:22px;overflow:hidden;border:2px solid var(--line)}
.im img{position:absolute;left:0;top:0;width:100%;height:100%;display:block}
.im svg{position:absolute;left:0;top:0}
.tag{position:absolute;left:18px;top:18px;background:rgba(18,32,48,.82);color:#fff;font-size:20px;font-weight:700;padding:6px 16px;border-radius:999px}
.disc{position:absolute;width:62px;height:62px;margin:-31px 0 0 -31px;border-radius:50%;color:#fff;border:4px solid #fff;
 font-size:32px;font-weight:800;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.28)}
.cap{position:absolute;top:828px;font-size:31px;font-weight:700;line-height:1.2}
.cap b{color:var(--red)}
.punch{position:absolute;left:290px;top:96px;font-size:84px;font-weight:800;line-height:1.04;letter-spacing:-.03em}
.punch span{color:var(--red)}
.loopi{position:absolute;left:96px;top:110px}
.pr{position:absolute;top:340px;width:820px;height:547px;border-radius:22px;overflow:hidden;border:2px solid var(--line);background:#fff}
.pr img{width:100%;height:100%;display:block}
.pr svg{position:absolute;left:0;top:0}
.rd{position:absolute;left:18px;top:18px;background:rgba(18,32,48,.82);color:#fff;font-size:22px;font-weight:700;padding:6px 16px;border-radius:999px}
.pl{position:absolute;top:910px;font-size:34px;font-weight:700;color:#fff;padding:10px 26px;border-radius:999px;white-space:nowrap}
.arr{position:absolute;left:926px;top:576px}
"""
    k = 840 / 1920

    at = {("excavator", 0): (640, 650)}  # small hopper: disc beside it, not on it

    def discs(key):
        return "".join(f'<div class="disc" style="left:{at.get((key, i), (x, y))[0] * k:.0f}px;'
                       f'top:{at.get((key, i), (x, y))[1] * k:.0f}px;background:{PAL[i]}">{i + 1}</div>'
                       for i, (x, y) in enumerate(mk[key]))

    (hx1, hy1), (hx2, hy2) = mk["excavator"]
    tur = (f'<div class="im" style="left:96px"><img src="../assets/one_turbine.png"><img src="../assets/som_turbine.png">'
           f'{discs("turbine")}<span class="tag">one prompt</span></div>'
           f'<div class="cap" style="left:96px">4 blades. <b>The text says 3.</b></div>')
    exc = (f'<div class="im" style="left:984px"><img src="../assets/one_excavator.png"><img src="../assets/som_excavator.png">'
           f'<svg width="840" height="560"><path d="M{945 * k:.0f} {720 * k:.0f} L{1215 * k:.0f} {615 * k:.0f}" stroke="#d64545" '
           f'stroke-width="5" stroke-dasharray="12 9" stroke-linecap="round"/></svg>'
           f'{discs("excavator")}<span class="tag">one prompt</span></div>'
           f'<div class="cap" style="left:984px">2 hoppers. <b>The text says 1</b> — and nothing connects them.</div>')
    loop = """<svg width="170" height="170" viewBox="0 0 150 150" fill="none" stroke-linecap="round">
<defs><marker id="r" markerWidth="14" markerHeight="14" refX="10" refY="7" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L14,7 L0,14 z" fill="#d64545"/></marker></defs>
<path d="M75 15 A60 60 0 0 1 132 92" stroke="#d64545" stroke-width="8" marker-end="url(#r)"/>
<path d="M118 120 A60 60 0 0 1 30 116" stroke="#d64545" stroke-width="8" marker-end="url(#r)"/>
<path d="M18 92 A60 60 0 0 1 58 18" stroke="#d64545" stroke-width="8" marker-end="url(#r)"/>
<text x="75" y="84" text-anchor="middle" font-family="DM Sans" font-weight="800" font-size="26" fill="#d64545" stroke="none">hours</text></svg>"""
    kp = 820 / 1920

    def ring(key, col, ic):
        x, y = mk[key]
        x, y = x * kp, min(y * kp, 547 - 46)
        return (f'<svg width="820" height="547"><circle cx="{x:.0f}" cy="{y:.0f}" r="40" fill="none" stroke="{col}" stroke-width="6"/></svg>'
                f'<div style="position:absolute;left:{x - 98:.0f}px;top:{y - 26:.0f}px;width:52px;height:52px;border-radius:50%;'
                f'background:{col};display:flex;align-items:center;justify-content:center">{icon(ic, 34, "#fff", 3)}</div>')

    arrow = """<svg width="68" height="60" viewBox="0 0 68 60"><path d="M4 30 H52" stroke="#122030" stroke-width="8" stroke-linecap="round"/>
<path d="M38 12 L60 30 L38 48" fill="none" stroke="#122030" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
    g2 = f"""<div class="loopi">{loop}</div>
<div class="punch">Feedback fixes one thing.<br><span>Breaks another.</span></div>
<div class="pr" style="left:96px"><img src="../assets/fx_r1.png">{ring('fx_r1', '#1f9d63', 'check')}<span class="rd">round 1</span></div>
<div class="arr">{arrow}</div>
<div class="pr" style="left:1004px"><img src="../assets/fx_r2.png">{ring('fx_r2', '#d64545', 'x')}<span class="rd">round 2</span></div>
<div class="pl" style="left:96px;background:var(--ink)">Fix asked: join cable to flex</div>
<div class="pl" style="left:1004px;background:var(--red)">Joined — now plugged into nothing</div>"""
    body = f"""<div class="kicker">The problem with one prompt</div>
<div class="g1"><h1 class="title">Looks right. Doesn't work.</h1>
{tur}{exc}
<div class="foot">One-prompt renders from our baseline runs: the turbine was specified with three blades; the excavator with one hopper. Parts found by SAM 3.1.</div></div>
<div class="g2">{g2}
<div class="foot">Rounds 1 and 2 of one picture-revision loop in our fingertip run: the reviewer asked for the signal cable to start at the flex.</div></div>"""
    S.shoot(write("problem.html", page(body, css, "st1")), f"{OUT}/problem_{{}}.png", ["st1", "st2"])

# ---------------------------------------------------------------- simple loop diagram (4 states)
if want("simple"):
    css = """
.box{position:absolute;top:400px;height:190px;background:#fff;border:3px solid var(--line);border-radius:26px;
 display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;text-align:center}
.box b{font-size:32px;letter-spacing:-.01em}.box i{font-style:normal;font-size:21px;color:var(--mute);line-height:1.25}
.box.dark{background:var(--ink);border-color:var(--ink);color:#fff}.box.dark i{color:#c4cfdb}
.loop{position:absolute;border-radius:22px;display:flex;align-items:center;gap:16px;padding:0 26px;height:104px}
.loop b{font-size:27px;line-height:1.15}.loop i{font-style:normal;display:block;font-size:20px;font-weight:500;margin-top:4px}
.o{background:#fff3ec;border:3px solid #f0b08c;color:#a8461a}
.p{background:#f4efff;border:3px solid #c6b2f0;color:#5b34b0}
.lab{position:absolute;font-weight:700;font-size:22px}
.tg{position:absolute;font-size:22px;font-weight:700;color:var(--orange);background:#fff;border:2px dashed #f0b08c;border-radius:999px;padding:6px 18px}
.s2,.s3,.s4{opacity:0}
body.st2 .s2,body.st3 .s2,body.st4 .s2{opacity:1}
body.st3 .s3,body.st4 .s3{opacity:1}
body.st4 .s4{opacity:1}
"""
    # box geometry: x0, width
    P, C, E, Pi, F = (96, 230), (392, 360), (818, 270), (1154, 330), (1550, 274)
    def bx(g, cls, ic, col, title, sub):
        return (f'<div class="box {cls}" style="left:{g[0]}px;width:{g[1]}px">{icon(ic, 46, col)}'
                f'<b>{title}</b><i>{sub}</i></div>')
    arrows = """
<svg class="abs" width="1920" height="1080" style="left:0;top:0" fill="none" stroke-linecap="round" stroke-linejoin="round">
<defs>
<marker id="g" markerWidth="16" markerHeight="16" refX="12" refY="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L16,8 L0,16 z" fill="#5d6b7c"/></marker>
<marker id="o" markerWidth="16" markerHeight="16" refX="12" refY="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L16,8 L0,16 z" fill="#e0662a"/></marker>
<marker id="p" markerWidth="16" markerHeight="16" refX="12" refY="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L16,8 L0,16 z" fill="#7b4fd6"/></marker>
<marker id="n" markerWidth="16" markerHeight="16" refX="12" refY="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L16,8 L0,16 z" fill="#1f9d63"/></marker>
</defs>
<g stroke="#5d6b7c" stroke-width="4" marker-end="url(#g)">
<path d="M330 495 L386 495"/><path d="M756 495 L812 495"/><path d="M1092 495 L1148 495"/><path d="M1488 495 L1544 495"/>
</g>
<g class="s2" stroke="#e0662a" stroke-width="5">
<path d="M1000 596 L1000 690" marker-end="url(#o)"/>
<path d="M470 690 L470 600" marker-end="url(#o)"/>
</g>
<g class="s3" stroke="#7b4fd6" stroke-width="5">
<path d="M1420 596 L1420 690" marker-end="url(#p)"/>
<path d="M1220 690 L1220 600" marker-end="url(#p)"/>
</g>
<g class="s4" stroke="#1f9d63" stroke-width="5" stroke-dasharray="14 12">
<path d="M1687 596 L1687 900 L211 900 L211 600" marker-end="url(#n)"/>
</g>
</svg>"""
    body = f"""<div class="kicker">The idea in one picture</div>
<h1 class="title">A design team that improves itself<br>from written critique</h1>
{arrows}
{bx(P, '', 'file-text', '#1f6fd1', 'Problem', 'a paragraph,<br>a few limits')}
{bx(C, '', 'users', '#1f6fd1', 'Expert team', 'search · calculate · sketch<br>on one whiteboard')}
{bx(E, '', 'clipboard-check', '#1f6fd1', 'Evaluator', 'written critique')}
{bx(Pi, '', 'image', '#1f6fd1', 'Picture', 'render the design,<br>check every part')}
{bx(F, 'dark', 'trophy', '#ffffff', 'Concept', 'figure, numbers,<br>how to make it')}
<div class="lab mute" style="left:1102px;top:452px;font-size:19px">pass</div>
<div class="lab s2" style="left:1016px;top:626px;color:var(--orange)">reject</div>
<div class="loop o s2" style="left:430px;top:696px;width:620px">{icon('pen-line', 40, '#e0662a')}<div><b>Manager writes a gradient</b><i>and rewrites the team's prompt</i></div></div>
<div class="tg s2" style="left:430px;top:820px">inspired by TextGrad</div>
<div class="lab s3" style="left:1436px;top:626px;color:var(--purple)">part wrong</div>
<div class="loop p s3" style="left:1120px;top:696px;width:400px">{icon('scan-eye', 40, '#7b4fd6')}<div><b>Critic + SAM</b><i>fix the image prompt,<br>keep or revert</i></div></div>
<div class="lab s4" style="left:780px;top:914px;color:var(--green);font-size:26px">{icon('book-open', 28, '#1f9d63')} &nbsp;lessons carry to the next problem</div>
{foot('textgrad', 'symbolic', 'opt2i', 'sam3')}"""
    S.shoot(write("simple.html", page(body, css, "st1")), f"{OUT}/simple_{{}}.png", ["st1", "st2", "st3", "st4"])

# ---------------------------------------------------------------- SAM hero helper
M = json.load(open(f"{A}/ft_masks.json"))
NAMES = {"skin": "soft skin", "trans": "firm layer", "pillars": "micro-pillars", "flex": "electrode flex",
         "core": "rigid core", "tail": "signal cable"}


def sam_hero(left, top, height, crop, chip_side="left", chip_x=None, chip_font=28, names=NAMES, ty0=40, ty1=None, radius=24):
    """Render crop (x0,y0,x1,y1 in render px) at the given height; masks overlaid; chips + leader lines."""
    W, H = M["size"]
    x0, y0, x1, y1 = crop
    k = height / (y1 - y0)
    w = round((x1 - x0) * k)
    imgs = [f'<img src="../assets/ft_render.png" style="position:absolute;left:{-x0 * k}px;top:{-y0 * k}px;width:{W * k}px">']
    for pid in M["cent"]:
        imgs.append(f'<img src="../assets/mask_{pid}.png" style="position:absolute;left:{-x0 * k}px;top:{-y0 * k}px;width:{W * k}px">')
    order = sorted(M["cent"], key=lambda p: M["cent"][p][1])
    lines, chips = [], []
    n = len(order)
    for i, pid in enumerate(order):
        cx, cy, _ = M["cent"][pid]
        px, py = (cx - x0) * k, (cy - y0) * k
        r, g, b = M["cols"][pid]
        ty1_ = (height - 40) if ty1 is None else ty1
        ty = ty0 + i * (ty1_ - ty0) / (n - 1) if n > 1 else py
        ty = py if abs(py - ty) < 30 else ty
        tx = chip_x if chip_x is not None else 20
        lines.append(f'<path d="M{tx + 10} {ty} L{px} {py}" stroke="rgb({r},{g},{b})" stroke-width="3"/>'
                     f'<circle cx="{px}" cy="{py}" r="9" fill="rgb({r},{g},{b})" stroke="#fff" stroke-width="3"/>')
        chips.append(f'<div class="pill" style="position:absolute;right:{w - tx}px;top:{ty - 24}px;background:rgb({r},{g},{b});'
                     f'color:#fff;font-size:{chip_font}px;padding:6px 18px;white-space:nowrap">{names[pid]}</div>')
    svg = f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="{w}" height="{height}" fill="none">{"".join(lines)}</svg>'
    return (f'<div style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{height}px;overflow:visible">'
            f'<div style="position:absolute;inset:0;overflow:hidden;border-radius:{radius}px">{"".join(imgs)}</div>{svg}{"".join(chips)}</div>')


# ---------------------------------------------------------------- SAM why (2 frames)
if want("sam"):
    css = """
.why{position:absolute;left:96px;top:420px;width:760px;display:flex;flex-direction:column;gap:34px}
.why div{display:flex;gap:22px;align-items:flex-start;font-size:33px;line-height:1.22;font-weight:500}
.why svg{flex:none;margin-top:2px}
"""
    hero = sam_hero(1110, 60, 960, (520, 170, 1272, 1250), chip_x=270)
    body = f"""<div class="kicker">Why SAM 3</div>
<h1 class="title" style="width:820px">Image models lose the part you ask them to fix.</h1>
<div class="why">
<div>{icon('eye-off', 48, '#d64545')}<span>The image model misses small details.</span></div>
<div>{icon('refresh-cw', 48, '#d64545')}<span>Told “fix that part”, it forgets where the part is and redraws everything.</span></div>
<div>{icon('crosshair', 48, '#7b4fd6')}<span><b>SAM gives the critic and the editor the part's exact region.</b></span></div>
</div>
{hero}
{foot('sam3', 'som', 'opt2i')}"""
    S.shoot(write("sam_1.html", page(body, css)), f"{OUT}/sam_1.png")

    css = """
.nums{position:absolute;left:96px;top:300px;width:1728px;display:grid;grid-template-columns:repeat(4,1fr);gap:28px}
.n{background:#fff;border:2px solid var(--line);border-radius:26px;padding:34px 30px;height:380px;display:flex;flex-direction:column}
.n .big{font-size:150px}.n .c{font-size:28px;line-height:1.25;margin-top:22px;font-weight:500}
.n .c b{font-weight:700}
.band{position:absolute;left:96px;top:730px;width:1728px;background:#f4efff;border:3px solid #c6b2f0;border-radius:24px;
 padding:26px 34px;display:flex;gap:22px;align-items:center;font-size:30px;color:#3f2390;font-weight:500}
.faults{position:absolute;left:96px;top:880px;display:flex;gap:16px}
.faults .pill{background:#fff;border:2px solid var(--line);font-size:23px;font-weight:500;color:var(--mute)}
"""
    body = f"""<div class="kicker">Why SAM 3 · what the runs show</div>
<h1 class="title">Parts get lost on full redraws, not on local edits.</h1>
<div class="nums">
<div class="n"><div class="big" style="color:var(--blue)">65</div><div class="c">picture rounds checked across all runs</div></div>
<div class="n"><div class="big" style="color:var(--red)">8</div><div class="c">parts lost or regions made worse: <b>all right after a full re-render</b></div></div>
<div class="n"><div class="big" style="color:var(--green)">0</div><div class="c">after a kept local edit</div></div>
<div class="n"><div class="big" style="color:var(--purple)">3<span style="font-size:80px"> / 3</span></div><div class="c">benchmark faults SAM had already measured; <b>the critic let them pass</b></div></div>
</div>
<div class="band">{icon('wand-sparkles', 44, '#7b4fd6')}<span><b>Round 6:</b> the critic must answer every SAM finding, and local edits use SAM's box.</span></div>
<div class="faults"><span class="pill">excavator: conveyor drawn apart from the hopper</span><span class="pill">fingertip: pillar count and axis</span><span class="pill">turbine: tail size</span></div>
{foot('sam3', 'som')}"""
    S.shoot(write("sam_2.html", page(body, css)), f"{OUT}/sam_2.png")

# ---------------------------------------------------------------- fingertip (3 frames)
if want("fingertip"):
    # before -> after split: raw Muse Image render | same render with SAM 3.1 masks and the plain prompts it was given
    PROMPT = {"skin": "“translucent ridged skin”", "trans": "box prompt · firm layer", "pillars": "box prompt · micro-pillars",
              "flex": "box prompt · electrode flex", "core": "“grey domed base”", "tail": "“black flat cable”"}
    cx0, cy0, cx1, cy1 = 640, 170, 1280, 1250
    hh = 770
    kk = hh / (cy1 - cy0)
    ww = round((cx1 - cx0) * kk)
    W, H = M["size"]
    def panel(left, masks):
        im = [f'<img src="../assets/ft_render.png" style="position:absolute;left:{-cx0 * kk}px;top:{-cy0 * kk}px;width:{W * kk}px">']
        if masks:
            im += [f'<img src="../assets/mask_{pid}.png" style="position:absolute;left:{-cx0 * kk}px;top:{-cy0 * kk}px;width:{W * kk}px">' for pid in M["cent"]]
        return f'<div class="pn" style="left:{left}px;width:{ww}px;height:{hh}px">{"".join(im)}</div>'
    L1, L2, top = 96, 96 + ww + 120, 196
    order = sorted(M["cent"], key=lambda p: M["cent"][p][1])
    tags, lines = [], []
    tx = L2 + ww + 60
    for i, pid in enumerate(order):
        cx, cy, _ = M["cent"][pid]
        px, py = L2 + (cx - cx0) * kk, top + (cy - cy0) * kk
        r, g, b = M["cols"][pid]
        ty = top + 40 + i * (hh - 80) / (len(order) - 1)
        lines.append(f'<path d="M{px} {py} L{tx - 8} {ty}" stroke="rgb({r},{g},{b})" stroke-width="3"/>'
                     f'<circle cx="{px}" cy="{py}" r="8" fill="rgb({r},{g},{b})" stroke="#fff" stroke-width="3"/>')
        tags.append(f'<div class="tg" style="left:{tx}px;top:{ty - 22}px;border-color:rgb({r},{g},{b})">'
                    f'<i style="background:rgb({r},{g},{b})"></i>{PROMPT[pid]}</div>')
    css = """
.pn{position:absolute;top:196px;overflow:hidden;border-radius:22px;border:2px solid var(--line)}
.lb{position:absolute;top:984px;font-size:20px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}
.ar{position:absolute;font-size:64px;font-weight:800;color:var(--faint)}
.tg{position:absolute;display:flex;align-items:center;gap:10px;background:#fff;border:2px solid;border-radius:999px;padding:6px 16px;font-size:22px;font-weight:600;white-space:nowrap}
.tg i{width:14px;height:14px;border-radius:50%;display:block}
.combo{position:absolute;right:96px;top:112px;font-size:24px;font-weight:700;color:var(--blue)}
"""
    body = (f'<div class="kicker">Our best result · robot fingertip</div><h1 class="title" style="font-size:54px">SAM 3.1 finds every part</h1>'
            f'<div class="combo">Muse Image + SAM 3.1 + Muse Spark on the Meta Model API</div>'
            + panel(L1, False) + panel(L2, True)
            + f'<div class="ar" style="left:{L1 + ww + 30}px;top:{top + hh / 2 - 40}px">→</div>'
            + f'<svg class="abs" style="left:0;top:0" width="1920" height="1080" fill="none">{"".join(lines)}</svg>' + "".join(tags)
            + f'<div class="lb" style="left:{L1}px">Muse Image render</div><div class="lb" style="left:{L2}px">SAM 3.1 masks</div>'
            + f'<div class="lb" style="left:{tx}px">what SAM was asked</div>' + foot('sam3', 'som'))
    S.shoot(write("fingertip_1.html", page(body, css)), f"{OUT}/fingertip_1.png")

    bg = bgcol(f"{A}/gal_fingertip.png", (60, 640))
    css = f"""body{{background:{bg}}}
.fig{{position:absolute;left:250px;top:0;height:1080px;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 6%,#000 94%,transparent 100%)}}
.title{{font-size:54px}}
.foot{{left:auto;right:64px;text-align:right;color:#7d8794}}
"""
    body = f"""<img class="fig" src="../assets/gal_fingertip.png">
<div class="kicker">Our best result · robot fingertip</div>
<h1 class="title">How it works,<br>part by part</h1>
<div class="abs mute" style="left:96px;top:240px;font-size:26px;line-height:1.35">every callout<br>checked against<br>its SAM mask</div>
{foot('sam3', 'som', 'idea2img')}"""
    S.shoot(write("fingertip_2.html", page(body, css)), f"{OUT}/fingertip_2.png")

    css = """
.crit{position:absolute;left:96px;top:290px;width:640px;height:572px;border-radius:24px;overflow:hidden;border:2px solid var(--line)}
.crit img{width:100%;height:100%;object-fit:cover}
.cap{position:absolute;font-size:22px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--mute)}
.chain{position:absolute;left:800px;top:290px;display:flex;align-items:center;gap:8px}
.chain .c{background:#fff;border:2px solid var(--line);border-radius:18px;padding:16px 18px;width:226px;height:124px;display:flex;flex-direction:column;gap:8px;font-size:23px;font-weight:700;line-height:1.15}
.chain .ar{font-size:28px;color:var(--faint);font-weight:700}
.nums{position:absolute;left:800px;top:480px;display:flex;gap:56px}
.nums .big{font-size:96px;color:var(--ink)}.nums .c{font-size:23px;color:var(--mute);margin-top:10px;line-height:1.25}
.steps{position:absolute;left:800px;top:730px;display:flex;gap:18px}
.steps div{width:330px}
.steps img{width:330px;height:220px;object-fit:cover;border-radius:16px;border:2px solid var(--line);display:block}
.steps span{display:block;font-size:24px;font-weight:700;margin-top:10px}
"""
    chain = [("cpu", "pillar electrodes"), ("cable", "guarded tail"), ("calculator", "capacitance converter"), ("radio", "slip-aware controller")]
    ch = '<span class="ar">→</span>'.join(f'<div class="c">{icon(i, 32, "#1f6fd1")}{t}</div>' for i, t in chain)
    body = f"""<div class="kicker">Our best result · robot fingertip</div>
<h1 class="title" style="font-size:54px">The part that decides it, how it's measured, how it's made</h1>
<div class="cap" style="left:96px;top:252px;width:640px">critical part · micro-pillar array</div>
<div class="crit"><img src="../assets/ft_B.png"></div>
<div class="cap" style="left:800px;top:252px">measurement chain</div>
<div class="chain">{ch}</div>
<div class="nums">
<div><div class="big">15<span style="font-size:52px"> mm</span></div><div class="c">wide, like<br>a human fingertip</div></div>
<div><div class="big">22.7<span style="font-size:52px">×</span></div><div class="c">a 1 mN touch over the<br>converter's smallest step</div></div>
<div><div class="big">12<span style="font-size:52px"> ms</span></div><div class="c">to scan the whole<br>array for slip</div></div>
</div>
<div class="cap" style="left:800px;top:694px">how it is made</div>
<div class="steps">
<div><img src="../assets/ft_step1.png"><span>Cast the skin</span></div>
<div><img src="../assets/ft_step3.png"><span>Wrap circuit on core</span></div>
<div><img src="../assets/ft_step4.png"><span>Bolt to the finger</span></div>
</div>
{foot('sam3', 'som', 'idea2img')}"""
    S.shoot(write("fingertip_3.html", page(body, css)), f"{OUT}/fingertip_3.png")

# ---------------------------------------------------------------- gallery
GAL = [("excavator", "Lunar excavator"), ("turbine", "Wind-tunnel turbine"), ("handtruck", "Stair-climbing hand truck"),
       ("coldroom", "Solar cold room"), ("damper", "Footbridge damper"), ("fingertip", "Robot fingertip")]
if want("gallery"):
    css = """
.grid{position:absolute;left:40px;top:196px;width:1840px;display:grid;grid-template-columns:repeat(3,1fr);column-gap:20px;row-gap:14px}
.t{position:relative}
.t .im{border-radius:18px;overflow:hidden;aspect-ratio:1.6;background:#ddd}
.t img{width:100%;height:100%;object-fit:cover;object-position:center top;display:block}
.t span{display:block;font-size:28px;font-weight:700;margin:10px 0 0 4px;line-height:1.1}
.kicker{top:52px}.title{top:86px;font-size:58px}
"""
    tiles = "".join(f'<div class="t"><div class="im"><img src="../assets/gal_{n}.png"></div><span>{t}</span></div>' for n, t in GAL)
    body = f"""<div class="kicker">Same system, six problems</div>
<h1 class="title">Six problems in. Six concepts out.</h1>
<div class="grid">{tiles}</div>"""
    # this frame is a full mosaic; the footer would sit on the tiles, so it is the model line only, above the grid
    body += '<div class="abs" style="right:96px;top:122px;font-size:22px;color:var(--faint)">Meta models only</div>'
    S.shoot(write("gallery.html", page(body, css)), f"{OUT}/gallery.png")

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
<div class="foot">Built with Muse Spark Open · open-weights Muse Spark and SAM 3, same architecture and loops</div>"""
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
.band .mm{font-size:26px;color:var(--mute);margin-top:34px;font-weight:500;letter-spacing:.02em}
"""
    top = ["gal_excavator", "gal_turbine", "gal_fingertip", "gal_coldroom", "gal_handtruck"]
    bot = ["open_b1_A", "gal_damper", "open_b2_A", "open_b3_A"]
    body = (f'<div class="r" style="top:0;height:300px">{"".join(f'<img src="../assets/{n}.png">' for n in top)}</div>'
            f'<div class="r" style="top:780px;height:300px">{"".join(f'<img src="../assets/{n}.png">' for n in bot)}</div>'
            """<div class="band"><div class="l1">The engineer gives the what.</div>
<div class="l2">Hardware Engineer works out the how,<br>and shows its proof.</div>
<div class="mm">Muse Spark 1.3 &nbsp;·&nbsp; Muse Image 1.0 &nbsp;·&nbsp; SAM 3.1</div></div>""")
    S.shoot(write("close.html", page(body, css)), f"{OUT}/close.png")

S.close()
print("ok")
