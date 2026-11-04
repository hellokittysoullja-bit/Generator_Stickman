"""Чистая подложка (04.11): модель картинок перерисовывает ТОТ ЖЕ рисунок без кота и того, что у него в лапах; подложка
совмещается с оригиналом (ECC, аффинное) и подгоняется по цвету на кольце вокруг дыры; в кадр идёт только внутри дыры
(+ мягкий шов). Сравнение — рядом с LaMa и MI-GAN на той же дыре: out/plate_<рисунок>.jpg."""
import base64
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, os.path.join(ROOT, "experiments", "cutout"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim  # noqa: E402
import bench  # noqa: E402
import fill_bench  # noqa: E402

OUT = fill_bench.OUT
PROMPT = ("Image 1 is a finished drawing. Redraw exactly the same drawing, the same room, furniture, objects, framing, "
          "scale, line work, colours and paper, but WITHOUT the black cat and without anything it is holding: the place "
          "where the cat was shows what is behind it — the sofa, pillow, floor or wall continue naturally with their "
          "own lines and colours, as if the cat had never been there. Nothing else changes: every other object stays in "
          "exactly the same place and size. No letters or numbers anywhere.")


def plate(key):
    import env; env.load_env()
    import llm_gateway
    case = bench.CASES[key]
    src = os.path.join(ROOT, case["img"])
    p = os.path.join(OUT, f"plate_raw_{key}.png")
    if not os.path.exists(p):
        G = llm_gateway.Gateway(spend_cap=210000)
        small = Image.open(src).convert("RGB").resize((1024, 1536), Image.LANCZOS)
        tmp = os.path.join(OUT, f"_src_{key}.png"); small.save(tmp)
        url = "data:image/png;base64," + base64.b64encode(open(tmp, "rb").read()).decode()
        ims, price = G.image("cx/gpt-image-2.5", PROMPT, "1024x1536", "medium", images=[url], timeout=600)
        open(p, "wb").write(ims[0]); print("подложка", price, flush=True)
    return p


def fuse(rgb, plate_rgb, hole):
    """Совмещение подложки с оригиналом по пикселям вне дыры (ECC, аффинное) + цвет по кольцу, вставка в дыру."""
    h, w = rgb.shape[:2]
    P = cv2.resize(plate_rgb, (w, h), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    g1 = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32); g2 = cv2.cvtColor(P.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    keep = (~cv2.dilate(hole.astype(np.uint8), np.ones((61, 61), np.uint8)).astype(bool)).astype(np.uint8)
    M = np.eye(2, 3, dtype=np.float32)
    try:
        s = 0.25
        a1, a2 = cv2.resize(g1, None, fx=s, fy=s), cv2.resize(g2, None, fx=s, fy=s)
        km = cv2.resize(keep, (a1.shape[1], a1.shape[0]), interpolation=cv2.INTER_NEAREST)
        _, M = cv2.findTransformECC(a1, a2, M, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), km, 5)
        M[:, 2] /= s
    except cv2.error as e:
        print("ECC не сошёлся:", e)
    P = cv2.warpAffine(P, M, (w, h), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    # тон: плавная поправка «оригинал − подложка», снятая вне дыры и протянутая внутрь (нормированная свёртка):
    # подложка чуть иначе окрашивает стену — без поправки в дыре проступала серая тень головы
    out_ = (~cv2.dilate(hole.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)).astype(np.float32)
    d = (rgb.astype(np.float32) - P) * out_[..., None]
    sig = 45
    num = cv2.GaussianBlur(d, (0, 0), sig); den = cv2.GaussianBlur(out_, (0, 0), sig)[..., None]
    P = P + num / np.maximum(den, 1e-3)
    soft = cv2.GaussianBlur(cv2.dilate(hole.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 4)[..., None]
    return rgb.astype(np.float32) * (1 - soft) + P * soft, M


def main(key):
    case = bench.CASES[key]
    rgb = np.asarray(Image.open(os.path.join(ROOT, case["img"])).convert("RGB"))
    a = anim.cut_sam(rgb, case["box"], case["pos"], case["neg"])
    hole = cv2.dilate((a > 0.02).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
    pr = np.asarray(Image.open(plate(key)).convert("RGB"))
    fused, M = fuse(rgb, pr, hole)
    lama = anim.inpaint_bg(rgb.astype(np.float32), hole, cache_dir=os.path.join(OUT, "cache"))
    x0, y0, x1, y1 = case["box"]
    tiles = []
    for name, im in [("LaMa (сейчас)", lama), ("Чистая подложка", fused)]:
        t = Image.fromarray(np.clip(im[y0:y1, x0:x1], 0, 255).astype(np.uint8)); t = t.resize((int(t.width * 800 / t.height), 800))
        ImageDraw.Draw(t).text((10, 8), name, fill=(220, 30, 30), font=fill_bench.FONT); tiles.append(t)
    raw = Image.open(plate(key)).convert("RGB"); raw = raw.resize((int(raw.width * 800 / raw.height), 800))
    ImageDraw.Draw(raw).text((10, 8), "что нарисовала модель", fill=(220, 30, 30), font=fill_bench.FONT); tiles.append(raw)
    S = Image.new("RGB", (sum(t.width for t in tiles) + 20, 800), "white"); x = 0
    for t in tiles:
        S.paste(t, (x, 0)); x += t.width + 10
    S.save(os.path.join(OUT, f"plate_{key}.jpg"), quality=88)
    np.save(os.path.join(OUT, f"plate_M_{key}.npy"), M); print("ok", key, M.round(3).tolist())


if __name__ == "__main__":
    main(sys.argv[1])
