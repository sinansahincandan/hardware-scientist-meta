"""Render the open-weights slides (showcase/open_weights/slides/*.html) headless at 1920x1080 to PNG and JPG,
and the comparison page to a full-page PNG. Never opens the owner's browser.

Usage: <python with playwright> scripts/render_slides.py [slides_dir]
(default: showcase/open_weights/slides; the comparison page is rendered only for the default)
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "showcase" / "open_weights"


def _cached_chromium() -> str | None:
    cache = Path.home() / "Library" / "Caches" / "ms-playwright"
    for pattern in ("chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell",
                    "chromium-*/chrome-mac*/*.app/Contents/MacOS/*"):
        found = sorted(cache.glob(pattern))
        if found:
            return str(found[-1])
    return None


def main() -> int:
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            browser = p.chromium.launch(executable_path=_cached_chromium())
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        slides = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT / "slides"
        for html in sorted(slides.resolve().glob("*.html")):
            if html.name == "index.html":
                continue
            page.goto(html.as_uri())
            page.wait_for_load_state("networkidle")
            png = html.with_suffix(".png")
            page.screenshot(path=str(png))
            Image.open(png).convert("RGB").save(png.with_suffix(".jpg"), quality=90)
            print(png)
        index = OUT / "index.html"
        if index.exists() and len(sys.argv) == 1:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(index.as_uri())
            page.wait_for_load_state("networkidle")
            page.screenshot(path=str(OUT / "index_full.png"), full_page=True)
            print(OUT / "index_full.png")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
