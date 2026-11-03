"""Слои хука рилса 18 «Ответить другу секунда, а ты не отвечаешь неделю?» для HyperFrames — по базе рилса 13.

Рисунок gen/p1_rush.png ×2 (.cache/anim/a1_wait_x2.png, waifu2x); координаты ×2, сняты сеткой anim.grid 03.11. Слои: кот
(тело с кружкой и телефоном), хвост (сеткой с физикой, tail_rig), четыре стикера в воздухе, линии скорости. Стол с
нетронутым листом — фон. Фон — anim.inpaint_bg под каждым предметом."""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); REEL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REEL, "..", "..", "..", "scripts"))
import anim  # noqa: E402
import tail_rig  # noqa: E402

OUT = os.path.join(HERE, "kit")
CACHE = os.path.join(REEL, ".cache", "anim")
ORIGIN = (0, 100)                 # левый верх сцены (композиции) в ×2
SIZE = (2048, 2900)
CAT_POLY = [(240, 2180), (250, 2300), (330, 2620), (450, 2985), (1300, 2985), (1390, 2900), (1420, 2770), (1470, 2600),
            (1460, 2420), (1530, 2280), (1530, 2160), (1560, 2060), (1580, 1660), (1250, 1540), (900, 1500),
            (560, 1540), (290, 1640), (300, 1900), (290, 2100)]
TAIL_POLY = [(1380, 1920), (1970, 1920), (1970, 2945), (1300, 2945), (1300, 2870), (1425, 2770), (1475, 2600),
             (1465, 2420), (1531, 2280), (1531, 2160), (1561, 2060), (1585, 1920)]
TAIL_PIVOT = (1400, 2850)         # основание хвоста у тела
PAGES_BOX = (600, 260, 2000, 1230)
BUBBLE_BOX = (700, 1120, 1340, 1600)
FEET = (870, 2960)                # ось вздрагивания кота
HEAD = (870, 1900)


def fill_holes(m):
    """Всё, что внутри контура кота (кружка, экран телефона, просветы) — коту: заливка снаружи, остальное — внутри."""
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    ff = m.copy(); pad = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(np.uint8)


def ink_in(A, poly, thr=215):
    reg = np.zeros(A.shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(poly)], 1)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    m = (((g < thr) | (sat > 45)) & (reg > 0)).astype(np.uint8)
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)), reg


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "a1_wait_x2.png")).convert("RGB")).astype(np.float32)
    cat_ink, cat_reg = ink_in(A, CAT_POLY)
    tail_ink, tail_reg = ink_in(A, TAIL_POLY)
    cat = fill_holes(anim.keep_attached(cat_ink)) & cat_reg
    tail = anim.keep_attached(tail_ink) & tail_reg & ~cat.astype(bool)
    full = (cat | tail).astype(np.uint8)
    tail, body = anim.split_part(tail, cat)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, full, around=(*TAIL_PIVOT, 200))
    pages = []
    for o in anim.ink_objects(A, box=PAGES_BOX, min_area=20000):
        o = o.astype(bool) & ~cv2.dilate(full, np.ones((9, 9), np.uint8)).astype(bool)
        ys = np.nonzero(o.any(1))[0]
        if o.sum() > 20000 and A[o].mean() > 170 and ys[-1] - ys[0] > 150:   # листок, а не макушка облачка
            pages.append(o)
    pages.sort(key=lambda o: np.argwhere(o)[:, 1].mean())
    swish = np.zeros_like(full)                               # штрихи «полёта» над листками — с фона вон
    for o in anim.ink_objects(A, box=PAGES_BOX, min_area=150):
        if o.sum() < 20000:
            swish |= o.astype(np.uint8)
    bubble = np.zeros_like(full)
    for o in anim.ink_objects(A, box=BUBBLE_BOX, min_area=20000):
        bubble |= o.astype(np.uint8)
    bubble &= ~cv2.dilate(full, np.ones((9, 9), np.uint8))
    bg = A.copy()
    for m in [full, swish, bubble] + [n.astype(np.uint8) for n in pages]:
        hole = cv2.dilate(m.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    parts = [("tail", Ap_tail, tail, True), ("body", Ap, body, True), ("bubble", Ap, bubble, True)]
    parts += [(f"page{i}", Ap, n.astype(np.uint8), True) for i, n in enumerate(pages)]
    for name, img, m, keep in parts:
        anim.save_layer(OUT, name, img, m.astype(np.uint8), layers, keep_attached_=keep)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - ox - tx, TAIL_PIVOT[1] - oy - ty),
                          out_dir=OUT, name="tail")
    rel = lambda p: (p[0] - ox, p[1] - oy)      # noqa: E731
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, tail_pivot=rel(TAIL_PIVOT), feet=rel(FEET), head=rel(HEAD),
                pages=len(pages), fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
