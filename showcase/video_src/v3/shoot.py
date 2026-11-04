"""Render an HTML frame to 1920x1080 PNG(s).
usage: python shoot.py page.html out_prefix [state1 state2 ...]
  no states  -> out_prefix.png
  states     -> out_prefix1.png, out_prefix2.png ... with <body class=state>
Uses the system Chrome via Playwright (channel="chrome"); fonts load from Google Fonts.
"""
import os
import sys

from playwright.sync_api import sync_playwright

html, prefix, states = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3:]
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto("file://" + html)
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(400)
    if not states:
        pg.screenshot(path=f"{prefix}.png")
    for k, st in enumerate(states, 1):
        pg.evaluate(f"document.body.className={st!r}")
        pg.wait_for_timeout(100)
        pg.screenshot(path=f"{prefix}{k}.png")
    b.close()
