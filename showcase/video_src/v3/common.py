"""Shared visual system for the v2 frames: one CSS, inline Lucide icons, Playwright shooter."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
HTML = os.path.join(HERE, "html")
os.makedirs(HTML, exist_ok=True)

COL = {"ink": "#122030", "mute": "#5d6b7c", "faint": "#8d98a6", "line": "#dbe1e8", "bg": "#f5f6f8",
       "blue": "#1f6fd1", "orange": "#e0662a", "purple": "#7b4fd6", "green": "#1f9d63", "red": "#d64545"}

# Footer reference sets (works each frame draws on)
REF = {
    "textgrad": "TextGrad — Yuksekgonul et al., Nature 2025",
    "symbolic": "Symbolic Learning — Zhou et al. 2024",
    "trace": "Trace — Cheng et al., NeurIPS 2024",
    "ace": "ACE — Zhang et al. 2025",
    "reflexion": "Reflexion — Shinn et al., NeurIPS 2023",
    "debate": "Multiagent Debate — Du et al., ICML 2024",
    "opt2i": "OPT2I — Mañas et al. (FAIR at Meta), TMLR 2024",
    "idea2img": "Idea2Img — Yang et al., ECCV 2024",
    "som": "Set-of-Mark — Yang et al. 2023",
    "sam3": "SAM 3 — Carion et al. (Meta) 2025",
}
MODELS = "Meta models only: Muse Spark 1.3 · Muse Image 1.0 · SAM 3.1"


def foot(*keys, prefix="Draws on: "):
    if not keys:
        return f'<div class="foot">{MODELS}</div>'
    return '<div class="foot">' + prefix + " · ".join(REF[k] for k in keys) + "</div>"


def icon(name, size=40, color="currentColor", stroke=2.0):
    svg = open(os.path.join(A, "icons", f"{name}.svg")).read()
    svg = svg[svg.index("<svg"):]
    svg = svg.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
    svg = svg.replace('stroke="currentColor"', f'stroke="{color}"').replace('stroke-width="2"', f'stroke-width="{stroke}"')
    return svg


CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;0,9..40,800;1,9..40,400&display=swap');
:root{--ink:#122030;--mute:#5d6b7c;--faint:#8d98a6;--line:#dbe1e8;--bg:#f5f6f8;--card:#fff;
--blue:#1f6fd1;--orange:#e0662a;--purple:#7b4fd6;--green:#1f9d63;--red:#d64545}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{width:1920px;height:1080px;overflow:hidden;position:relative;background:var(--bg);
 font-family:'DM Sans',system-ui,sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased}
.kicker{position:absolute;left:96px;top:58px;font-weight:700;font-size:22px;letter-spacing:.16em;text-transform:uppercase;color:var(--blue)}
.title{position:absolute;left:96px;top:94px;margin:0;font-weight:800;font-size:62px;line-height:1.06;letter-spacing:-.025em}
.foot{position:absolute;left:96px;right:96px;bottom:24px;font-size:18px;color:var(--faint);white-space:nowrap;overflow:hidden}
.abs{position:absolute}
.card{background:#fff;border:2px solid var(--line);border-radius:22px}
.pill{display:inline-flex;align-items:center;gap:10px;border-radius:999px;padding:8px 18px;font-weight:700}
.big{font-weight:800;letter-spacing:-.03em;line-height:1}
.mute{color:var(--mute)}
"""


def page(body, css="", body_class=""):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{css}</style></head>'
            f'<body class="{body_class}">{body}</body></html>')


def write(name, html):
    p = os.path.join(HTML, name)
    open(p, "w").write(html)
    return p


class Shooter:
    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._p = sync_playwright().start()
        self.b = self._p.chromium.launch(channel="chrome")

    def shoot(self, html_path, out, states=None, w=1920, h=1080, scale=1):
        pg = self.b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        pg.goto("file://" + html_path)
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        outs = []
        if states:
            for k, st in enumerate(states, 1):
                pg.evaluate(f"document.body.className={st!r}")
                pg.wait_for_timeout(100)
                o = out.format(k)
                pg.screenshot(path=o)
                outs.append(o)
        else:
            pg.screenshot(path=out)
            outs.append(out)
        pg.close()
        return outs

    def close(self):
        self.b.close()
        self._p.stop()
