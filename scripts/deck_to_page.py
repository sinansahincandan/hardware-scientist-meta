"""Build showcase/story.html from the slide deck: each slide rendered at 1920x1080 (headless Chromium), with its
speaker notes as the plain-language text under it. One look for the deck and the document.

Usage: .venv/bin/python scripts/deck_to_page.py <deck_folder_with_project/> <blob_map.json>
blob_map.json maps each /_blob/<id> used by the slides to a local image file.
"""
from __future__ import annotations

import base64
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from PIL import Image
from playwright.sync_api import sync_playwright
from shoot import _cached_chromium

PAGE_STYLE = """<style>
body{margin:0;background:#eef1f5;color:#16202c;font:18px/1.6 'DM Sans',Inter,-apple-system,Helvetica,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:40px 24px 60px}
h1{font-size:40px;margin:0 0 6px}.sub{color:#5b6878;margin:0 0 30px}
.slide{margin:0 0 44px}.slide img{width:100%;border-radius:14px;box-shadow:0 6px 24px rgba(20,30,50,.12);display:block}
.slide p{max-width:1000px;margin:16px 4px 0;color:#33404f}
</style>"""


def main() -> int:
    deck, blob_map = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    index = json.loads((deck / "project" / "deck.json").read_text(encoding="utf-8"))
    out_dir = ROOT / "showcase" / "story_assets" / "deck"
    out_dir.mkdir(parents=True, exist_ok=True)
    parts = []
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception:
            browser = pw.chromium.launch(executable_path=_cached_chromium())
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        for k, sid in enumerate(index["order"], 1):
            src = (deck / "project" / "slides" / f"{sid}.html").read_text(encoding="utf-8")
            notes = re.search(r"<aside>(.*?)</aside>", src, flags=re.DOTALL)
            body = re.sub(r"<aside>.*?</aside>", "", src, flags=re.DOTALL)
            body = re.sub(r"/_blob/([0-9a-f]+)", lambda m: Path(blob_map[m.group(1)]).resolve().as_uri(), body)
            body = body.replace('style="', 'style="position:relative;width:1920px;height:1080px;overflow:hidden;'
                                'box-sizing:border-box;', 1)
            tmp = out_dir / f"_{sid}.html"
            tmp.write_text("<!doctype html><html><head><link rel='stylesheet' href='https://fonts.googleapis.com/css2?"
                           "family=DM+Sans:wght@400;500;700&display=swap'><style>*{margin:0;box-sizing:border-box}"
                           f"ul{{padding-left:30px}}</style></head><body>{body}</body></html>", encoding="utf-8")
            page.goto(tmp.as_uri())
            page.wait_for_timeout(600)
            png = out_dir / f"{k:02d}_{sid}.png"
            page.screenshot(path=str(png))
            tmp.unlink()
            jpg = png.with_suffix(".jpg")  # embedded, so the page shows its pictures wherever it is opened
            Image.open(png).convert("RGB").save(jpg, quality=86)
            data = base64.b64encode(jpg.read_bytes()).decode()
            parts.append(f"<div class='slide'><img src='data:image/jpeg;base64,{data}' alt='slide {k}'>"
                         + (f"<p>{html.escape(' '.join(notes.group(1).split()))}</p>" if notes else "") + "</div>")
        browser.close()
    (ROOT / "showcase" / "story.html").write_text(
        "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
        f"<title>Hardware Scientist — how a design evolves</title>{PAGE_STYLE}</head><body><div class='wrap'>"
        "<h1>Hardware Scientist</h1><p class='sub'>How a design evolves — the slides, each with what it shows in "
        "plain words. Full records per problem are in the folders next to this page.</p>"
        + "".join(parts) + "</div></body></html>", encoding="utf-8")
    print(ROOT / "showcase" / "story.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
