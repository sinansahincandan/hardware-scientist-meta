import sys
from playwright.sync_api import sync_playwright
html, prefix, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto("file://" + html); pg.wait_for_timeout(1200)
    for k in range(1, n + 1):
        pg.evaluate(f"document.body.className='st{k}'")
        pg.screenshot(path=f"{prefix}{k}.png")
    b.close()
