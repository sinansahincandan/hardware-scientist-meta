"""Presentation video from a storyboard (local only; no Meta model call): each segment is narrated with a local
open text-to-speech model (Kokoro, voice af_heart) and shows one visual for exactly as long as its narration:

- still:  one 1920x1080 image
- reveal: several images in order, cross-faded at the given fractions of the segment (a diagram building up)
- tour:   one large image and a list of camera boxes; the camera eases from box to box (far, then closer)

Usage: .venv/bin/python scripts/make_video.py <storyboard.json> <out.mp4>
The storyboard is {"voice": "af_heart", "speed": 1.08, "tts_python": "<python with kokoro>", "segments": [
  {"id": "...", "text": "...", "visual": {"type": "still", "img": "..."}} ...]}.
Image paths are relative to the storyboard file. Tour boxes are [x0, y0, x1, y1] in source pixels with a relative hold weight: {"box": [...], "hold": 1.0}; each box is
widened to 16:9 around its centre and the source is padded with its own corner colour where the box leaves it.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

W, H, FPS = 1920, 1080, 25
MOVE_S = 1.4  # camera move between tour boxes
FADE_S = 0.5  # reveal cross-fade

TTS = """
import sys, json, numpy as np, soundfile as sf
import misaki.espeak as _e
class _NoFallback:
    def __init__(self, *a, **k): raise RuntimeError("no espeak")
_e.EspeakFallback = _NoFallback
from kokoro import KPipeline
job = json.loads(sys.argv[1])
p = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
for item in job["items"]:
    audio = np.concatenate([a for _, _, a in p(item["text"], voice=job["voice"], speed=job["speed"])])
    sf.write(item["out"], np.concatenate([audio, np.zeros(int(24000 * 0.35), dtype=audio.dtype)]), 24000)
"""


def _ease(t: float) -> float:
    return t * t * (3 - 2 * t)


def _fit(img: Image.Image) -> Image.Image:
    if img.size == (W, H):
        return img
    canvas = Image.new("RGB", (W, H), img.getpixel((0, 0)))
    k = min(W / img.size[0], H / img.size[1])
    im = img.resize((round(img.size[0] * k), round(img.size[1] * k)), Image.LANCZOS)
    canvas.paste(im, ((W - im.size[0]) // 2, (H - im.size[1]) // 2))
    return canvas


def _box169(b: list[float]) -> tuple[float, float, float, float]:
    x0, y0, x1, y1 = b
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    if w / h < W / H:
        w = h * W / H
    else:
        h = w * H / W
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2


def _tour_frames(spec: dict, n: int):
    src = Image.open(spec["img"]).convert("RGB")
    pad = max(src.size) // 4  # room for boxes that leave the image
    big = Image.new("RGB", (src.size[0] + 2 * pad, src.size[1] + 2 * pad), src.getpixel((2, 2)))
    big.paste(src, (pad, pad))
    keys = [(_box169([v + pad for v in k["box"]]), float(k.get("hold", 1.0))) for k in spec["keys"]]
    total = n / FPS
    hold_total = max(total - MOVE_S * (len(keys) - 1), 0.5)
    weight = sum(h for _, h in keys)
    timeline = []  # (start, end, box_a, box_b)
    t = 0.0
    for i, (box, h) in enumerate(keys):
        d = hold_total * h / weight
        timeline.append((t, t + d, box, box))
        t += d
        if i + 1 < len(keys):
            timeline.append((t, t + MOVE_S, box, keys[i + 1][0]))
            t += MOVE_S
    for f in range(n):
        tt = f / FPS
        seg = next((s for s in timeline if s[0] <= tt < s[1]), timeline[-1])
        a = _ease(min(max((tt - seg[0]) / max(seg[1] - seg[0], 1e-6), 0.0), 1.0)) if seg[2] != seg[3] else 0.0
        box = tuple(seg[2][j] + (seg[3][j] - seg[2][j]) * a for j in range(4))
        yield big.resize((W, H), Image.BICUBIC, box=box)


def _reveal_frames(spec: dict, n: int):
    imgs = [_fit(Image.open(p).convert("RGB")) for p in spec["imgs"]]
    at = spec.get("at") or [i / len(imgs) for i in range(len(imgs))]
    for f in range(n):
        tt = f / n
        k = max(i for i, a in enumerate(at) if a <= tt)
        fade = (tt - at[k]) * n / FPS / FADE_S if k > 0 else 1.0
        yield imgs[k] if fade >= 1 else Image.blend(imgs[k - 1], imgs[k], fade)


def main() -> int:
    board, out = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")), Path(sys.argv[2])
    here = Path(sys.argv[1]).resolve().parent  # image paths in the storyboard are relative to it
    for s in board["segments"]:
        v = s["visual"]
        for k in ("img",):
            if k in v:
                v[k] = str(here / v[k])
        if "imgs" in v:
            v["imgs"] = [str(here / p) for p in v["imgs"]]
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    work = Path(tempfile.mkdtemp())
    segs = board["segments"]
    items = [{"text": s["text"], "out": str(work / f"{i:02d}.wav")} for i, s in enumerate(segs)]
    subprocess.run([board["tts_python"], "-c", TTS, json.dumps({"voice": board.get("voice", "af_heart"),
                    "speed": board.get("speed", 1.0), "items": items})], check=True,
                   stderr=subprocess.DEVNULL)
    parts, total = [], 0.0
    for i, s in enumerate(segs):
        wav = work / f"{i:02d}.wav"
        with wave.open(str(wav)) as w:
            secs = w.getnframes() / w.getframerate()
        n = int(secs * FPS) + 1
        vis = s["visual"]
        frames = (_tour_frames(vis, n) if vis["type"] == "tour" else _reveal_frames(vis, n) if vis["type"] == "reveal"
                  else (_fit(Image.open(vis["img"]).convert("RGB")) for _ in range(n)))
        clip = work / f"{i:02d}.mp4"
        proc = subprocess.Popen([ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                 "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav), "-c:v", "libx264",
                                 "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac",
                                 "-b:a", "192k", "-shortest", str(clip)], stdin=subprocess.PIPE)
        assert proc.stdin is not None
        for fr in frames:
            proc.stdin.write(fr.tobytes())
        proc.stdin.close()
        proc.wait()
        total += secs
        print(f"{i + 1:02d} {s['id']}: {secs:.1f} s, {len(s['text'].split())} words")
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
