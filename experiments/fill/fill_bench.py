"""Стенд заливки фона под вырезанным котом (04.11): нынешний anim.inpaint_bg (LaMa + ореол + зерно) против MI-GAN
(ONNX, MIT) — на тех же трёх рисунках и тех же дырах (маска anim.cut_sam, расширенная на 15 px). Лист out/fill_<рисунок>.jpg."""
import os
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, os.path.join(ROOT, "experiments", "cutout"))
import anim  # noqa: E402
import bench  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
MIGAN = os.path.join(anim.MODEL_DIR, "migan", "migan_pipeline_v2.onnx")
_S = {}


def migan(img, hole):
    import onnxruntime as ort
    if "s" not in _S:
        if not os.path.exists(MIGAN):
            from huggingface_hub import hf_hub_download
            hf_hub_download("CardAnvilModels/MI-GAN-ONNX", "migan_pipeline_v2.onnx", local_dir=os.path.dirname(MIGAN))
        _S["s"] = ort.InferenceSession(MIGAN, providers=["CPUExecutionProvider"])
    x = np.clip(img, 0, 255).astype(np.uint8).transpose(2, 0, 1)[None]
    m = (np.where(hole, 0, 255).astype(np.uint8))[None, None]          # 255 — известно, 0 — дыра
    y = _S["s"].run(None, {"image": x, "mask": m})[0][0].transpose(1, 2, 0)
    return y.astype(np.float32)


def main():
    os.makedirs(OUT, exist_ok=True)
    for key, case in bench.CASES.items():
        rgb = np.asarray(Image.open(os.path.join(ROOT, case["img"])).convert("RGB"))
        a = anim.cut_sam(rgb, case["box"], case["pos"], case["neg"])
        hole = cv2.dilate((a > 0.02).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
        res = {}
        t = time.time(); res["LaMa (сейчас)"] = anim.inpaint_bg(rgb.astype(np.float32), hole, cache_dir=os.path.join(OUT, "cache")); tl = time.time() - t
        t = time.time(); res["MI-GAN"] = migan(rgb, hole); tm = time.time() - t
        x0, y0, x1, y1 = case["box"]
        tiles = []
        for (name, im), dt in zip(res.items(), (tl, tm)):
            tile = Image.fromarray(np.clip(im[y0:y1, x0:x1], 0, 255).astype(np.uint8))
            tile = tile.resize((int(tile.width * 800 / tile.height), 800))
            ImageDraw.Draw(tile).text((10, 8), f"{name} · {dt:.1f} с", fill=(220, 30, 30), font=FONT)
            tiles.append(tile)
        S = Image.new("RGB", (sum(t.width for t in tiles) + 10, 800), "white"); x = 0
        for t_ in tiles:
            S.paste(t_, (x, 0)); x += t_.width + 10
        S.save(os.path.join(OUT, f"fill_{key}.jpg"), quality=88)
        print(key, round(tl, 1), round(tm, 1), flush=True)


if __name__ == "__main__":
    main()
