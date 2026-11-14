"""Слои хука рилса 68 «Убираешься вместо дела?» для HyperFrames — по образцу рилса 66 (kit_list.py).

Рисунок gen/g1_wipe_desk.png (1664×2496) ×2 = src/f1.png (3328×4992); координаты сняты по сетке исходника 1664×2496
и умножены на K=2. Слои: кот (голова, тело над столом, хвост с огоньком, лапа с тряпкой на столе — одним куском;
тело за столом срезано по заднему краю стола, лапы под столом остаются фоном), ноутбук (экран и клавиатура), четыре
искры блеска. Фон — стол и бумага (anim.inpaint_bg под всеми слоями). Композиция — весь рисунок в половинном размере,
её координаты = координаты исходника. F1=путь — подмена исходника для проб."""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); REEL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REEL, "..", "..", "..", "scripts"))
import anim  # noqa: E402

OUT = os.path.join(HERE, "kit")
CACHE = os.path.join(REEL, ".cache", "anim")
K = 2.0
DESK_Y = 1636                              # задний край стола: выше — кот на бумаге, ниже — только лапа с тряпкой


def P(pts):
    return [(int(x * K), int(y * K)) for x, y in pts]


SPARKS = {"s1": ((335, 1650), 82), "s2": ((410, 1790), 66), "s3": ((1043, 1812), 70), "s4": ((1222, 1543), 72)}
CAT_UP = P([(0, 730), (560, 730), (900, 590), (1190, 590), (1250, 900), (1345, 1150), (1345, 1340), (1160, 1440),
            (1150, 1600), (1195, 1605), (1195, 1690), (1035, 1690), (1035, DESK_Y), (420, DESK_Y), (250, 1620),
            (0, 1570)])
ARM = P([(640, DESK_Y - 4), (862, DESK_Y - 4), (872, 1688), (988, 1742), (955, 1797), (862, 1828), (772, 1893),
         (668, 1878), (556, 1828), (470, 1772), (486, 1732), (568, 1698), (642, 1698)])
LAPTOP = P([(1398, 1300), (1664, 1286), (1664, 1895), (1600, 1880), (1116, 1795), (1110, 1745), (1328, 1688),
            (1338, 1676)])
PIVOT = P([(760, DESK_Y)])[0]             # ось раскачки кота: задний край стола под телом
LAP = P([(1400, 1790)])[0]                 # ось ноутбука: середина основания


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    big = np.zeros((h + 2, w + 2), np.uint8); big[1:-1, 1:-1] = m
    ff = big.copy(); pad = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 2)
    return (big[1:-1, 1:-1] | (ff[1:-1, 1:-1] != 2)).astype(np.uint8)


def poly_mask(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def disc(shape, c, r):
    m = np.zeros(shape[:2], np.uint8); cv2.circle(m, (int(c[0] * K), int(c[1] * K)), int(r * K), 1, -1); return m


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.environ.get("F1") or os.path.join(REEL, "src", "f1.png")).convert("RGB")).astype(np.float32)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    H, Wd = g.shape
    sp_all = np.zeros((H, Wd), np.uint8)
    for c, r in SPARKS.values():
        sp_all |= disc(A.shape, c, r)
    up = poly_mask(A.shape, CAT_UP) & (1 - sp_all)
    non = ((g < 205) | (sat > 45)) & (up > 0)
    ink = cv2.morphologyEx(non.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8)) & up
    cat = fill_holes(anim.keep_attached(ink)) & up
    # лапа с тряпкой на столе: тёмный мех, голубая тряпка и контуры — без серого стола вокруг
    arm = poly_mask(A.shape, ARM) & (1 - sp_all)
    blue = (A[..., 2] - A[..., 0] > 10) & (g > 150)
    am = ((g < 120) | blue) & (arm > 0)
    am = cv2.morphologyEx(am.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)) & arm
    am = fill_holes(am) & arm
    cat = anim.keep_attached((cat | am).astype(np.uint8), reach=6)
    cat = fill_holes(cat) & (up | arm)
    cat |= ((g < 150) & (up > 0) & ~cv2.dilate(cat, np.ones((3, 3), np.uint8)).astype(bool)).astype(np.uint8)  # усы
    cat = anim.keep_attached(cat, reach=4)
    lap = poly_mask(A.shape, LAPTOP)
    sparks = {}
    for n, (c, r) in SPARKS.items():
        d = disc(A.shape, c, r)
        sparks[n] = (((sat > 40) | (g < 170)) & (d > 0) & ~cv2.dilate(cat, np.ones((5, 5), np.uint8)).astype(bool)).astype(np.uint8)
        sparks[n] = cv2.morphologyEx(sparks[n], cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) & d
    bg = A.copy()
    for part in [cat, lap] + list(sparks.values()):
        hole = cv2.dilate(part.astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    layers = {}
    anim.save_layer(OUT, "lap", Ap, lap, layers, keep_attached_=False)
    anim.save_layer(OUT, "cat", Ap, cat, layers, keep_attached_=False)
    for n, m in sparks.items():
        anim.save_layer(OUT, n, Ap, m, layers, keep_attached_=False)
    Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for f in ["bg.png"] + [n + ".png" for n in layers]:
        im = Image.open(os.path.join(OUT, f)); im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(OUT, f))
    for v in layers.values():
        v["xy"] = (v["xy"][0] // 2, v["xy"][1] // 2); v["wh"] = (v["wh"][0] // 2, v["wh"][1] // 2)
    h2 = lambda p: (p[0] // 2, p[1] // 2)     # noqa: E731
    meta = dict(origin=(0, 0), size=(Wd // 2, H // 2), layers=layers, pivot=h2(PIVOT), lap=h2(LAP),
                sparks={n: [int(c[0]), int(c[1])] for n, (c, r) in SPARKS.items()}, fps=30, scale=0.5)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
