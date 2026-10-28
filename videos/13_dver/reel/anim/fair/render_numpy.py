"""Тот же хук нашим прежним движком (scripts/anim.py), по тем же числам движения, что снял extract.js с HyperFrames.

Отрисовка — как в anim.Layer.draw: слой премультиплицирован, warpAffine INTER_CUBIC, смаз — anim._smear по скорости
слоя (px за кадр), если она больше 2 px (тот же порог, что в Layer.draw). Штрихи — постоянной толщины с круглыми
концами (как SVG у HyperFrames), край мягкий 0,8 px, как у anim.stroke. Без смаза (blur=0) — для сверки снятия движения."""
import json
import math
import os
import sys
import time

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "scripts"))
import anim  # noqa: E402

TRACKS, ASSETS, OUT, BLUR = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == "1"
INK = np.float32((24, 24, 26))
FILES = dict(bg="bg.png", tail="tail.png", body="body.png", cloud="cloud.png", pencil="pencil.png", b1="bubble1.png", b2="bubble2.png")


def load(name):
    im = np.asarray(Image.open(os.path.join(ASSETS, FILES[name])).convert("RGBA")).astype(np.float32)
    return im[..., :3], im[..., 3] / 255.0


def draw(base, rgb, a, M, opacity, smear):
    h, w = a.shape
    corners = np.float32([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]]) @ M.T
    pad = 4 + (int(abs(smear[0]) + abs(smear[1])) if smear else 0)
    x0 = int(max(0, math.floor(corners[:, 0].min()) - pad)); x1 = int(min(base.shape[1], math.ceil(corners[:, 0].max()) + pad))
    y0 = int(max(0, math.floor(corners[:, 1].min()) - pad)); y1 = int(min(base.shape[0], math.ceil(corners[:, 1].max()) + pad))
    if x1 <= x0 or y1 <= y0 or opacity <= 0.004:
        return
    Ml = M.copy(); Ml[0, 2] -= x0; Ml[1, 2] -= y0
    size = (x1 - x0, y1 - y0)
    prgb = cv2.warpAffine(rgb * a[..., None], Ml, size, flags=cv2.INTER_CUBIC, borderValue=0)
    pa = np.clip(cv2.warpAffine(a, Ml, size, flags=cv2.INTER_CUBIC, borderValue=0), 0, 1)
    if smear and math.hypot(*smear) > 2:
        prgb, pa = anim._smear(prgb, pa, smear)
    pa = pa * opacity
    reg = base[y0:y1, x0:x1]
    np.multiply(reg, 1 - pa[..., None], out=reg)
    reg += prgb * opacity


def stroke(base, pts, width, opacity):
    pts = np.float32(pts)
    x0, y0 = np.floor(pts.min(0) - width - 4).astype(int); x1, y1 = np.ceil(pts.max(0) + width + 4).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, base.shape[1]), min(y1, base.shape[0])
    if x1 <= x0 or y1 <= y0:
        return
    m = np.zeros((y1 - y0, x1 - x0), np.float32)
    cv2.polylines(m, [np.int32((pts - [x0, y0]) * 4)], False, 1.0, max(1, int(round(width))), cv2.LINE_AA, shift=2)
    m = cv2.GaussianBlur(m, (0, 0), 0.8)[..., None] * opacity
    reg = base[y0:y1, x0:x1]
    reg[:] = reg * (1 - m) + INK * m


def center(M, wh):
    return M[:, :2] @ np.float32([wh[0] / 2, wh[1] / 2]) + M[:, 2]


def main():
    T = json.load(open(TRACKS)); os.makedirs(OUT, exist_ok=True)
    L = {k: load(k) for k in FILES}
    t0 = time.time()
    prev = None
    for i, fr in enumerate(T["frames"]):
        base = np.zeros((1920, 1440, 3), np.float32)
        Ms = {}
        for ly in fr["layers"]:
            a, b, c, d, e, f = ly["m"]
            M = np.float32([[a, c, e], [b, d, f]]); Ms[ly["id"]] = M
            rgb, al = L[ly["id"]]
            sm = None
            if BLUR and prev is not None and ly["id"] in prev:
                v = center(M, al.shape[::-1]) - center(prev[ly["id"]], al.shape[::-1])
                sm = (float(v[0]), float(v[1]))
            draw(base, rgb, al, M, ly["o"], sm)
        for s in fr["strokes"]:
            stroke(base, s["pts"], s["w"], s["o"])
        for dt in fr["dots"]:
            m = np.zeros(base.shape[:2], np.float32)
            cv2.circle(m, (int(dt["x"] * 4), int(dt["y"] * 4)), int(dt["r"] * 4), 1.0, -1, cv2.LINE_AA, shift=2)
            m = cv2.GaussianBlur(m, (0, 0), 0.8)[..., None] * dt["o"]
            base[:] = base * (1 - m) + INK * m
        prev = Ms
        Image.fromarray(np.clip(base + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f"{i:03d}.png"))
    print(f"numpy: {len(T['frames'])} кадров за {time.time() - t0:.1f} с, размытие {'да' if BLUR else 'нет'}")


main()
