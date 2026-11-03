"""Слои хука рилса 15 «Чужое сдашь, а своё?» для HyperFrames — по базе рилса 13 (стандарт 24).

Рисунок gen/s1_boxes.png, увеличенный вдвое (.cache/anim/s1_boxes_x2.png, waifu2x); координаты ×2, сняты сеткой
anim.grid 03.11. Слои: кот (тело с лапами), хвост (сеткой с физикой, tail_rig), башня из коробок (качается в лапах),
верхняя коробка (подпрыгивает отдельно). Пыльная гитара — фон: на ударе от неё поднимается пыль (рисует композиция).
Фон — anim.inpaint_bg под каждым предметом отдельно."""
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
CAT_POLY = [(690, 1990), (715, 1915), (760, 1895), (810, 1905), (835, 1935), (1000, 1915), (1200, 1885), (1240, 1878),
            (1265, 1825), (1325, 1815), (1350, 1850), (1350, 1915), (1490, 1910), (1500, 2045), (1640, 2050),
            (1645, 2745), (1250, 2750), (1200, 2800), (1180, 2935), (925, 2935), (900, 2800), (820, 2780), (780, 2700),
            (680, 2600), (650, 2200), (670, 2050)]
TAIL_POLY = [(1415, 2070), (1600, 2070), (1640, 2300), (1640, 2745), (1300, 2745), (1295, 2630), (1355, 2610),
             (1355, 2330), (1415, 2290)]
TAIL_PIVOT = (1300, 2680)         # основание хвоста у тела
TOWER_BOX = (580, 140, 1620, 1935)
BOX1_POLY = [(1048, 148), (1592, 248), (1508, 612), (1412, 600), (1418, 545), (1400, 520), (1300, 493), (1200, 474),
             (1100, 460), (968, 446)]
PAWS = (1035, 1895)               # середина хвата лап под башней: ось качания
BOX1_PIVOT = (1200, 490)          # низ верхней коробки: ось её прыжков
GUITAR = (260, 2520)              # середина пыльной гитары: отсюда пыль на ударе
FEET = (1050, 2920)
FLOOR_Y = 2880                    # ниже — тень у лап: коту только тушь лап
SWEAT_BOX = (1350, 1905, 1505, 2060)  # капли пота: отдельные пятна, едут с котом


def cat_mask(A):
    reg = np.zeros(A.shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(CAT_POLY)], 1)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    m = (((g < 200) | (sat > 45)) & (reg > 0)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    m[FLOOR_Y:] = ((g < 130) & (reg > 0))[FLOOR_Y:]
    inv = (1 - m).astype(np.uint8)                                   # блики глаз, зубы, капли пота — коту
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < 2500:
            m[lab == i] = 1
    return anim.keep_attached(m)


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "s1_boxes_x2.png")).convert("RGB")).astype(np.float32)
    cat = cat_mask(A)
    tail_reg = np.zeros_like(cat); cv2.fillPoly(tail_reg, [np.int32(TAIL_POLY)], 1)
    tail = cat & tail_reg; body = cat & ~tail_reg.astype(bool)
    tail, body = anim.split_part(tail, body)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, cat, around=(*TAIL_PIVOT, 200))
    sweat = np.zeros_like(cat)
    for o in anim.ink_objects(A, box=SWEAT_BOX, min_area=150):
        sweat |= o
    sweat &= ~cat.astype(bool)
    tower = np.zeros_like(cat)
    for o in anim.ink_objects(A, box=TOWER_BOX, min_area=4000):
        tower |= o
    tower &= ~cv2.dilate(cat.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    tower[1935:] = 0
    b1 = np.zeros_like(cat); cv2.fillPoly(b1, [np.int32(BOX1_POLY)], 1)
    box1 = tower & b1.astype(bool); rest = tower & ~box1
    bg = A.copy()
    for m in (cat | sweat, tower):                                           # каждый предмет — своей заливкой
        hole = cv2.dilate(m.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    # под низом башни — ровная стена: LaMa по обрывку тени коробки дорисовывала серую полосу (лист 03.11); полоса
    # заливается бумагой той же стены с зерном, кроме кота
    x0, y0, x1, y1 = 600, 1640, 1440, 1975
    gs = bg.mean(2); paper = np.median(bg[1300:1700, 150:500][gs[1300:1700, 150:500] > 200], axis=0)
    m = np.zeros(bg.shape[:2], np.float32); m[y0:y1, x0:x1] = 1; m[1880:2075, 1330:1515] = 1   # и под каплями пота
    m = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
    rng = np.random.default_rng(15)
    grain = cv2.GaussianBlur(rng.normal(0, 1, bg.shape[:2]).astype(np.float32), (0, 0), 0.8)[..., None] * 1.6
    bg = bg * (1 - m) + (paper + grain) * m
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    for name, img, m, keep in (("tail", Ap_tail, tail, True), ("body", Ap, body, True), ("tower", Ap, rest, False),
                               ("box1", Ap, box1, False), ("sweat", Ap, sweat, False)):
        anim.save_layer(OUT, name, img, m.astype(np.uint8), layers, keep_attached_=keep)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - ox - tx, TAIL_PIVOT[1] - oy - ty),
                          out_dir=OUT, name="tail")
    rel = lambda p: (p[0] - ox, p[1] - oy)      # noqa: E731
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, tail_pivot=rel(TAIL_PIVOT), paws=rel(PAWS),
                box1_pivot=rel(BOX1_PIVOT), box1_edge=[rel((968, 446)), rel((1418, 545))], guitar=rel(GUITAR), feet=rel(FEET), fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
