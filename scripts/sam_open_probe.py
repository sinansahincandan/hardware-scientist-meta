"""Probe the Modal SAM 3 app on a saved render and compare with the Meta API's SAM on the same image.

Uses run 20261103-152604 (excavator) from the main folder (read only): the phrases Meta SAM found parts
with, and the rough boxes it was box-prompted with. Writes runs/sam_open_probe/: overlay.png (open masks),
result.json (open vs Meta boxes per part, confidences, GPU seconds, load report)."""
from __future__ import annotations

import base64
import io
import json
import sys
import time
from pathlib import Path

import modal
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT.parent / "MetaHackathon_HardwareScientist_MetaCode/runs/20261103-152604_lunar-regolith-excavation-robot"
ROUND = RUN / "stage_b/attempt_00/round_01"


def main() -> int:
    out_dir = ROOT / "runs" / "sam_open_probe"
    out_dir.mkdir(parents=True, exist_ok=True)
    render = Image.open(ROUND / "render.png").convert("RGB")
    meta = json.loads((ROUND / "sam.json").read_text())
    s = min(1.0, 1024 / max(render.size))
    sent = render.resize((round(render.width * s), round(render.height * s)))
    buf = io.BytesIO()
    sent.save(buf, format="PNG")
    png = buf.getvalue()

    sam = modal.Cls.from_name("hs-sam3", "Sam3")()
    t0 = time.time()
    report = sam.report.remote()
    cold = round(time.time() - t0, 1)
    result: dict = {"load_report": report, "first_call_seconds_incl_cold_start": cold, "parts": {}}

    overlay = sent.copy()
    draw = ImageDraw.Draw(overlay, "RGBA")
    colours = [(255, 0, 0), (0, 160, 255), (0, 200, 0), (255, 150, 0), (200, 0, 255), (0, 220, 200),
               (255, 0, 140), (120, 120, 0)]
    boxed = []
    for k, (pid, rec) in enumerate(meta["parts"].items()):
        meta_boxes = [[round(v * s) for v in b] for b in rec.get("boxes", [])]
        entry = {"meta_source": rec.get("source"), "meta_phrase": rec.get("phrase"), "meta_boxes": meta_boxes}
        if rec.get("source") == "phrase" or rec.get("source") == "none":
            phrase = rec.get("phrase")
            got = sam.segment_text.remote(png, phrase)
            entry.update(open_mode="phrase", open_phrase=phrase, gpu_seconds=got["gpu_seconds"],
                         open=[{"box": [round(v) for v in i["box"]], "conf": round(i["conf"], 3)}
                               for i in got["instances"]])
            insts = got["instances"]
        else:
            boxed.append((pid, meta_boxes[0]))
            result["parts"][pid] = entry
            continue
        result["parts"][pid] = entry
        _paint(draw, insts, colours[k % len(colours)], pid)
    if boxed:
        got = sam.segment_boxes.remote(png, [{"object_id": pid, "box": b} for pid, b in boxed])
        for i in got["instances"]:
            k = list(meta["parts"]).index(i["object_id"])
            result["parts"][i["object_id"]].update(
                open_mode="box prompt", gpu_seconds=got["gpu_seconds"],
                open=[{"box": [round(v) for v in i["box"]], "conf": round(i["conf"], 3)}])
            _paint(draw, [i], colours[k % len(colours)], i["object_id"])
    overlay.save(out_dir / "overlay.png")
    result["wall_seconds"] = round(time.time() - t0, 1)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=1)[:4000])
    return 0


def _paint(draw: ImageDraw.ImageDraw, insts: list[dict], colour: tuple[int, int, int], label: str) -> None:
    for i in insts:
        if i.get("mask_png"):
            m = Image.open(io.BytesIO(base64.b64decode(i["mask_png"]))).convert("L")
            x0, y0, _, _ = i["mask_box"]
            ys, xs = np.nonzero(np.asarray(m) > 127)
            for y, x in zip(ys[::3], xs[::3]):
                draw.point((x0 + x, y0 + y), fill=(*colour, 110))
        b = i["box"]
        draw.rectangle(b, outline=(*colour, 255), width=2)
        draw.text((b[0] + 3, b[1] + 3), label, fill=(*colour, 255))


if __name__ == "__main__":
    sys.exit(main())
