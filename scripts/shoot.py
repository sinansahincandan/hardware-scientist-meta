"""Render an HTML page headless (Playwright Chromium), 1440 px wide, full page, sliced.

Usage: .venv/bin/python scripts/shoot.py <page.html> <out_dir> [slice_height]
Writes <out_dir>/<stem>_full.png and <stem>_NN.png slices; prints the slice paths.
Never opens the owner's browser.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


def _cached_chromium() -> str | None:
    """Use a Chromium already in the Playwright cache when the installed Playwright expects a newer
    build (nothing is downloaded)."""
    cache = Path.home() / "Library" / "Caches" / "ms-playwright"
    for pattern in ("chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell",
                    "chromium-*/chrome-mac*/*.app/Contents/MacOS/*"):
        found = sorted(cache.glob(pattern))
        if found:
            return str(found[-1])
    return None


def shoot(page_path: Path, out_dir: Path, slice_h: int = 1600) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    full = out_dir / f"{page_path.stem}_full.png"
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception:
            browser = pw.chromium.launch(executable_path=_cached_chromium())
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(page_path.resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(full), full_page=True)
        browser.close()
    img = Image.open(full)
    slices: list[Path] = []
    for i, top in enumerate(range(0, img.height, slice_h)):
        part = out_dir / f"{page_path.stem}_{i:02d}.png"
        img.crop((0, top, img.width, min(top + slice_h, img.height))).save(part)
        slices.append(part)
    return slices


if __name__ == "__main__":
    for path in shoot(Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 1600):
        print(path)
