"""Presentation video from the slide deck: each slide (rendered by scripts/deck_to_page.py at 1920x1080) is shown
for as long as its speaker notes take to read aloud (macOS `say`, local; no model call), then all are joined.

Usage: .venv/bin/python scripts/make_video.py <deck_folder_with_project/> <out.mp4> [voice] [words_per_minute]
Slide images are read from showcase/story_assets/deck/NN_<id>.png in deck order.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    deck, out = Path(sys.argv[1]), Path(sys.argv[2])
    voice = sys.argv[3] if len(sys.argv) > 3 else "Samantha"
    rate = sys.argv[4] if len(sys.argv) > 4 else "175"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    order = json.loads((deck / "project" / "deck.json").read_text(encoding="utf-8"))["order"]
    work = Path(tempfile.mkdtemp())
    parts: list[Path] = []
    total = 0.0
    for k, sid in enumerate(order, 1):
        src = (deck / "project" / "slides" / f"{sid}.html").read_text(encoding="utf-8")
        m = re.search(r"<aside>(.*?)</aside>", src, flags=re.DOTALL)
        notes = " ".join(m.group(1).split()) if m else ""
        png = ROOT / "showcase" / "story_assets" / "deck" / f"{k:02d}_{sid}.png"
        aiff = work / f"{k:02d}.aiff"
        subprocess.run(["say", "-v", voice, "-r", rate, "-o", str(aiff), notes or " "], check=True)
        clip = work / f"{k:02d}.mp4"
        # the slide stays 0.6 s past its narration so slides do not cut mid-breath
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-loop", "1", "-i", str(png), "-i", str(aiff),
                        "-af", "apad=pad_dur=0.6", "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                        "-vf", "scale=1920:1080", "-r", "25", "-c:a", "aac", "-b:a", "160k", "-shortest", str(clip)],
                       check=True)
        probe = subprocess.run([ffmpeg, "-i", str(clip)], capture_output=True, text=True, check=False).stderr  # ffmpeg -i exits 1 by design
        d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", probe)
        secs = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)) if d else 0.0
        total += secs
        print(f"{k:02d} {sid}: {secs:.1f} s, {len(notes.split())} words")
        parts.append(clip)
    listing = work / "list.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in parts), encoding="utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", str(out)], check=True)
    print(f"{out}: {total:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
