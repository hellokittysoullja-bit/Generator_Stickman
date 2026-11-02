"""Слои хука рилса 14 «Опять начнёшь с понедельника?» для HyperFrames — по базе рилса 13 (стандарт 24).

Рисунок gen/m1_sunday.png, увеличенный вдвое (.cache/anim/m1_sunday_x2.png, waifu2x); координаты ×2, сняты сеткой
anim.grid 02.11. Слои: кот (тело с поднятой лапой и маркером), хвост (сеткой с физикой, tail_rig), список новой жизни
(качается на кнопках). Красный круг на понедельнике рисует композиция (SVG), на рисунке его нет: тёплые цвета
рисунка — только у огонька (палитра). Фон — anim.inpaint_bg под каждым предметом отдельно."""
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
ORIGIN = (0, 160)                 # левый верх сцены (композиции) в ×2
SIZE = (2048, 2800)
CAT_POLY = [(380, 760), (450, 750), (620, 1060), (640, 1250), (770, 1380), (1000, 1330), (1290, 1330), (1340, 1600),
            (1480, 1620), (1610, 1820), (1610, 2245), (1290, 2255), (1200, 2300), (850, 2300), (740, 2200), (720, 1900),
            (580, 1660), (560, 1450), (380, 820)]
TAIL_POLY = [(1345, 1620), (1480, 1620), (1610, 1820), (1610, 2245), (1290, 2255), (1215, 2200), (1230, 2050),
             (1300, 1950), (1335, 1840)]
TAIL_PIVOT = (1240, 2150)         # основание хвоста у тела
FLOOR_Y = 2240                    # ниже — сиденье табурета: коту только тёмная тушь лап
LIST_BOX = (1590, 470, 2020, 2560)
LIST_PIN = (1810, 500)            # список висит на кнопках сверху
CIRCLE = (470, 692, 112, 100)     # круг на первом квадрате (понедельник): центр и полуоси, ×2
CAT_FOOT = (1030, 2290)


def _edge(src, gs, x, lo, hi, paper):
    """Цвет стены над или под листом в столбце x: медиана светлой бумаги, без туши."""
    seg = src[max(0, lo):hi, x]; ok = gs[max(0, lo):hi, x] > 200
    return np.median(seg[ok], axis=0) if ok.sum() >= 4 else paper


def cat_mask(A):
    reg = np.zeros(A.shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(CAT_POLY)], 1)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    m = (((g < 200) | (sat > 45)) & (reg > 0)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    feet = ((g < 130) & (reg > 0)).astype(np.uint8)
    m[FLOOR_Y:] = feet[FLOOR_Y:]
    inv = (1 - m).astype(np.uint8)                                   # блики глаз и волоски — коту
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < 400:
            m[lab == i] = 1
    m = anim.drop_scene_lines(A, m)                                  # линии календаря за лапой — сцене
    return anim.keep_attached(m)


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "m1_sunday_x2.png")).convert("RGB")).astype(np.float32)
    cat = cat_mask(A)
    tail_reg = np.zeros_like(cat); cv2.fillPoly(tail_reg, [np.int32(TAIL_POLY)], 1)
    tail = cat & tail_reg; body = cat & ~tail_reg.astype(bool)
    tail, body = anim.split_part(tail, body)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, cat, around=(*TAIL_PIVOT, 200))
    lst = np.zeros_like(cat)
    for o in anim.ink_objects(A, box=LIST_BOX, min_area=5000):
        lst |= o
    hole = cv2.dilate(cat.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
    bg = anim.inpaint_bg(A, hole, cache_dir=CACHE)
    # под списком — ровная стена: заливка по столбцам от стены над листом к стене под ним, с зерном. LaMa на дыре
    # во весь лист (2 тыс. px) оставляла серое пятно и призраки строк (лист 02.11)
    x0, y0, x1, y1 = LIST_BOX
    ya, yb, xa, xb = y0 - 70, y1 + 40, x0 - 30, min(x1 + 20, A.shape[1])
    gs = bg.mean(2); paper = np.median(bg[ya - 80:ya, xa:xb][gs[ya - 80:ya, xa:xb] > 200], axis=0)
    tops = np.array([_edge(bg, gs, x, ya - 30, ya, paper) for x in range(xa, xb)], np.float32)
    bots = np.array([_edge(bg, gs, x, yb, yb + 30, paper) for x in range(xa, xb)], np.float32)
    tops = cv2.GaussianBlur(tops[None], (0, 0), 25)[0]; bots = cv2.GaussianBlur(bots[None], (0, 0), 25)[0]   # без полос
    k = np.linspace(0, 1, yb - ya)[:, None, None]
    fill = tops[None] * (1 - k) + bots[None] * k
    m = np.zeros(bg.shape[:2], np.float32); m[ya + 12:yb - 12, xa + 12:xb] = 1
    m = cv2.GaussianBlur(m, (0, 0), 8)[ya:yb, xa:xb, None]                 # мягкий край заливки, без ступеньки
    bg[ya:yb, xa:xb] = bg[ya:yb, xa:xb] * (1 - m) + fill * m
    rng = np.random.default_rng(14)
    grain = cv2.GaussianBlur(rng.normal(0, 1, (yb - ya, xb - xa)).astype(np.float32), (0, 0), 0.8)
    bg[ya:yb, xa:xb] += (grain * 1.6)[..., None] * m
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    for name, img, m in (("tail", Ap_tail, tail), ("body", Ap, body), ("list", Ap, lst)):
        anim.save_layer(OUT, name, img, m.astype(np.uint8), layers)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - ox - tx, TAIL_PIVOT[1] - oy - ty),
                          out_dir=OUT, name="tail")
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, tail_pivot=(TAIL_PIVOT[0] - ox, TAIL_PIVOT[1] - oy),
                cat_foot=(CAT_FOOT[0] - ox, CAT_FOOT[1] - oy), list_pin=(LIST_PIN[0] - ox, LIST_PIN[1] - oy),
                circle=(CIRCLE[0] - ox, CIRCLE[1] - oy, CIRCLE[2], CIRCLE[3]), fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
