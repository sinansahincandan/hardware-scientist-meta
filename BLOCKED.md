# BLOCKED.md — items that could not be done in this environment

## Page screenshots (v2 B2 / F5 / I) — blocked by the session sandbox

Every rendered-page screenshot route was tried on 2026-11-01 and failed
inside the managed sandbox (seatbelt), before any page code ran:

- Playwright Chromium (cached headless shell): crashes on launch.
- System Google Chrome `--headless=new --screenshot`: exits silently, no file.
- Chromium with tmp HOME, swiftshader, single-process: same crash.
- WKWebView off-screen snapshot (Swift): compiles with a /tmp module cache,
  then `takeSnapshot` fails with WKErrorDomain 1 under the sandbox.
- WeasyPrint: needs libpango; Homebrew cannot write its lock/cache dirs,
  conda cannot write its pkgs/cache dirs, and extracted bottles cannot be
  fetched for the same reason.
- `qlmanage -t` (QuickLook): "sandbox initialization failed".

Opening pages in the user's visible browser is forbidden by the task
("never open any page on my screen"), so that route was not used.

**What was done instead:** every PNG visual (renders, annotated panels,
schematics, sketches, figures) is opened and inspected directly as an
image. The HTML pages (report, board, showcase, dossiers) share the same
CSS and were checked structurally (sizes < 2 MB, relative image paths,
all referenced files exist). The pages still need one human look in a
normal browser before the hackathon demo.

Everything else in the v2 brief is unaffected by this block.

## SAM 3.1 returned no detections in the PHASE 1 check (2026-11-02) — open

One `sam-3.1` call (phrase "metal disk", the 1600x1600 check render of a single red disk)
was accepted and billed but streamed an empty `output_text`. Not retried in PHASE 1
(one call per model). The item-16 smoke test settles the cause (event types, image size,
phrase) before any SAM feature is built; if SAM stays unusable, item 16 falls back to the
critic's own boxes as the brief says.
