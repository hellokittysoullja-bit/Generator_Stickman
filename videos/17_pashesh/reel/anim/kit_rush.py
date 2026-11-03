"""Слои хука рилса 17 «Пашешь, а итог ноль?» для HyperFrames — по базе рилса 13 (стандарт 24).

Рисунок gen/p1_rush.png ×2 (.cache/anim/p1_rush_x2.png, waifu2x); координаты ×2, сняты сеткой anim.grid 03.11. Слои: кот
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
ORIGIN = (0, 600)                 # левый верх сцены (композиции) в ×2
SIZE = (2048, 2200)
CAT_POLY = [(430, 1520), (400, 1420), (395, 1150), (560, 1060), (700, 1050), (800, 960), (1010, 950), (1250, 1060),
            (1380, 1240), (1590, 1380), (1600, 1500), (1680, 1600), (1680, 2020), (1560, 2060), (1440, 2050),
            (1160, 2070), (1160, 2380), (1170, 2560), (1010, 2710), (860, 2660), (790, 2530), (560, 2480), (420, 2480),
            (260, 2430), (270, 2240), (470, 2150), (530, 2060), (420, 1720)]
TAIL_POLY = [(30, 1050), (425, 1050), (428, 1700), (360, 1790), (440, 1950), (540, 2010), (560, 2090),
             (470, 2140), (300, 2110), (30, 2110)]
TAIL_PIVOT = (500, 2040)          # основание хвоста у спины
NOTES_BOX = (300, 680, 1760, 1330)
SPEED_BOX = (20, 2000, 360, 2250)
FEET = (900, 2660)                # опорная лапа: ось наклона кота
HEAD = (1050, 1500)


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
    A = np.asarray(Image.open(os.path.join(CACHE, "p1_rush_x2.png")).convert("RGB")).astype(np.float32)
    cat_ink, cat_reg = ink_in(A, CAT_POLY)
    tail_ink, tail_reg = ink_in(A, TAIL_POLY)
    cat = fill_holes(anim.keep_attached(cat_ink)) & cat_reg
    tail = anim.keep_attached(tail_ink) & tail_reg & ~cat.astype(bool)
    full = (cat | tail).astype(np.uint8)
    tail, body = anim.split_part(tail, cat)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, full, around=(*TAIL_PIVOT, 200))
    notes = []
    for o in anim.ink_objects(A, box=NOTES_BOX, min_area=6000):
        o = o.astype(bool) & ~cv2.dilate(full, np.ones((9, 9), np.uint8)).astype(bool)
        if o.sum() > 6000 and A[o].mean() > 180:              # стикер — белый лист; тёмный кусок (ухо) — коту
            notes.append(o)
    notes.sort(key=lambda o: np.argwhere(o)[:, 1].mean())
    speed = np.zeros_like(full)
    for o in anim.ink_objects(A, box=SPEED_BOX, min_area=200):
        speed |= o.astype(np.uint8)
    speed &= ~cv2.dilate(full, np.ones((9, 9), np.uint8))
    bg = A.copy()
    for m in [full, speed] + [n.astype(np.uint8) for n in notes]:
        hole = cv2.dilate(m.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    parts = [("tail", Ap_tail, tail, True), ("body", Ap, body, True), ("speed", Ap, speed, False)]
    parts += [(f"note{i}", Ap, n.astype(np.uint8), True) for i, n in enumerate(notes)]
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
                notes=len(notes), fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
