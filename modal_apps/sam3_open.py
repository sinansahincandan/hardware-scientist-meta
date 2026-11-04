"""SAM 3 (Meta, open weights) on a Modal GPU — the open-weights replacement for the Meta API's sam-3.1.

Why SAM 3 and not the SAM 3.1 checkpoint (checked 2026-11-03): facebook/sam3.1 ships one checkpoint
(sam3.1_multiplex.pt) built for the Object Multiplex video pipeline. Its detector was retrained on a
three-neck backbone (convs / interactive_convs / propagation_convs) that the image model does not have, and its
tracker is the multiplex video tracker, so loading it into the image model left 26 detector tensors and every
box-predictor tensor missing; 1,093 of 1,130 shared detector tensors differ from SAM 3, so the two cannot be mixed.
The SAM 3 image checkpoint loads completely. Same gated access, same Meta SAM license.

Two calls, matching what HS sends to SAM (src/hs/stage_b/part_map.py):
- segment_text(png, phrase): every object of a short noun phrase (concept prompt), with its confidence.
- segment_boxes(png, boxes): one object per rough box (the SAM 1 task: interactive instance prediction).
Both return instances in the sent image's pixels: object id, box, confidence, and the mask as a PNG
cropped to its box. Weights come from huggingface.co/facebook/sam3 (gated; the owner's HF read token is kept as
the Modal secret hs-hf) and are cached in a Modal volume after the first download.

Deploy: .venv/bin/modal deploy modal_apps/sam3_open.py
"""
from __future__ import annotations

import base64
import io
import time

import modal

SAM3_COMMIT = "f1647e8"  # facebookresearch/sam3 main on 2026-11-03
# A10G first: on 2026-11-03 no L4 started within 200 s even for a plain image, A10G started at once.
GPU = ["A10G", "L4"]


image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "libgl1", "libglib2.0-0")
    .pip_install("torch==2.10.0", "torchvision", index_url="https://download.pytorch.org/whl/cu128")
    .pip_install(f"git+https://github.com/facebookresearch/sam3.git@{SAM3_COMMIT}", "huggingface_hub",
                 "pillow", "numpy", "einops", "pycocotools",
                 "psutil", "scipy", "setuptools<81")  # imported by sam3 but not declared by it
    .env({"HF_HOME": "/weights/hf"})
)
weights = modal.Volume.from_name("hs-sam31-weights", create_if_missing=True)  # holds both checkpoints
app = modal.App("hs-sam3")
# The owner's Hugging Face read token, added by the owner in the Modal dashboard as the secret "hs-hf".
secrets = [modal.Secret.from_name("hs-hf")]


def _mask_png(mask, box) -> tuple[str, list[int]]:
    """The mask cropped to its box as a 1-bit PNG (base64) and the crop's [x0, y0, x1, y1]."""
    import numpy as np
    from PIL import Image

    h, w = mask.shape
    x0, y0 = max(int(np.floor(box[0])), 0), max(int(np.floor(box[1])), 0)
    x1, y1 = min(int(np.ceil(box[2])), w), min(int(np.ceil(box[3])), h)
    if x1 <= x0 or y1 <= y0:
        return "", [x0, y0, x0, y0]
    buf = io.BytesIO()
    Image.fromarray(mask[y0:y1, x0:x1].astype("uint8") * 255).convert("1").save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode(), [x0, y0, x1, y1]


@app.cls(image=image, gpu=GPU, volumes={"/weights": weights}, secrets=secrets, scaledown_window=300, timeout=600)
class Sam3:
    @modal.enter()
    def load(self) -> None:
        import torch
        from huggingface_hub import hf_hub_download
        from sam3.model.sam3_image_processor import Sam3Processor
        from sam3.model_builder import build_sam3_image_model

        t0 = time.time()
        hf_hub_download("facebook/sam3", "config.json")
        ckpt = hf_hub_download("facebook/sam3", "sam3.pt")
        weights.commit()
        self.model = build_sam3_image_model(checkpoint_path=None, load_from_HF=False, enable_inst_interactivity=True)
        ck = torch.load(ckpt, map_location="cpu", weights_only=True)
        ck = ck["model"] if isinstance(ck.get("model"), dict) else ck
        state = {k.replace("detector.", "", 1): v for k, v in ck.items() if k.startswith("detector.")}
        state.update({k.replace("tracker.", "inst_interactive_predictor.model.", 1): v
                      for k, v in ck.items() if k.startswith("tracker.")})
        missing, unexpected = self.model.load_state_dict(state, strict=False)
        self.model = self.model.cuda().eval()
        self.load_report = {"checkpoint": "facebook/sam3 sam3.pt", "sam3_commit": SAM3_COMMIT,
                            "load_seconds": round(time.time() - t0, 1), "missing": len(missing),
                            "unexpected": len(unexpected), "missing_sample": list(missing)[:12],
                            "gpu": torch.cuda.get_device_name(0)}
        self.processor = Sam3Processor(self.model, confidence_threshold=0.5)
        self.torch = torch

    def _state(self, png: bytes):
        from PIL import Image

        im = Image.open(io.BytesIO(png)).convert("RGB")
        return im, self.processor.set_image(im)

    @modal.method()
    def report(self) -> dict:
        return self.load_report

    @modal.method()
    def segment_text(self, png: bytes, phrase: str) -> dict:
        t0 = time.time()
        with self.torch.autocast("cuda", dtype=self.torch.bfloat16):
            im, state = self._state(png)
            out = self.processor.set_text_prompt(prompt=phrase, state=state)
        masks = out["masks"].squeeze(1).float().cpu().numpy() > 0.5
        boxes = out["boxes"].float().cpu().numpy()
        scores = out["scores"].float().cpu().numpy()
        insts = []
        for k, (m, b, s) in enumerate(zip(masks, boxes, scores), start=1):
            png_b64, crop = _mask_png(m, b)
            insts.append({"object_id": str(k), "box": [float(v) for v in b], "conf": float(s),
                          "mask_png": png_b64, "mask_box": crop})
        return {"w": im.width, "h": im.height, "instances": insts, "gpu_seconds": round(time.time() - t0, 3)}

    @modal.method()
    def segment_boxes(self, png: bytes, boxes: list[dict]) -> dict:
        """boxes: [{object_id, box: [x0, y0, x1, y1]}] in the sent image's pixels."""
        import numpy as np

        t0 = time.time()
        with self.torch.autocast("cuda", dtype=self.torch.bfloat16):
            im, state = self._state(png)
            arr = np.array([b["box"] for b in boxes], dtype=np.float32)
            masks, scores, _ = self.model.predict_inst(state, point_coords=None, point_labels=None,
                                                       box=arr, multimask_output=False)
        masks = np.asarray(masks).reshape(len(boxes), -1, im.height, im.width)[:, 0] > 0.5
        scores = np.asarray(scores).reshape(len(boxes), -1)[:, 0]
        insts = []
        for b, m, s in zip(boxes, masks, scores):
            ys, xs = np.nonzero(m)
            if len(xs) == 0:
                continue
            tight = [float(xs.min()), float(ys.min()), float(xs.max() + 1), float(ys.max() + 1)]
            png_b64, crop = _mask_png(m, tight)
            insts.append({"object_id": str(b["object_id"]), "box": tight, "conf": float(s),
                          "mask_png": png_b64, "mask_box": crop})
        return {"w": im.width, "h": im.height, "instances": insts, "gpu_seconds": round(time.time() - t0, 3)}


@app.local_entrypoint()
def check() -> None:
    """`modal run modal_apps/sam3_open.py`: load the model once and print the load report (logs stream here)."""
    print(Sam3().report.remote())
