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
CAT_UP = P([(4, 730), (560, 730), (900, 590), (1190, 590), (1250, 900), (1345, 1150), (1345, 1340), (1160, 1440),
            (1150, 1560), (1195, 1580), (1195, 1668), (1035, 1668), (1035, DESK_Y), (440, DESK_Y), (430, 1612),
            (250, 1605), (4, 1570)])
ARM = P([(572, DESK_Y - 4), (862, DESK_Y - 4), (872, 1688), (988, 1742), (955, 1797), (862, 1828), (772, 1893),
         (668, 1878), (556, 1828), (470, 1772), (486, 1732), (560, 1700), (580, 1690)])
LAPTOP = P([(1392, 1300), (1664, 1306), (1664, 1890), (1120, 1782), (1110, 1750), (1312, 1662), (1310, 1650)])
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
    low = np.zeros((H, Wd), bool); low[int(1600 * K):] = True       # у стола у кота — только тёмный мех лап
    non = ((g < 205) | (sat > 45)) & (up > 0) & ~(low & (g >= 120))
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
    # над столом за котом и ноутбуком — чистая бумага: LaMa оставляла призраки шерсти и рамки экрана (видны, когда
    # кот раскачивается и ноутбук улетает)
    wipe = np.zeros((H, Wd), np.uint8); wipe[:int((DESK_Y - 8) * K)] = 1
    hole_up = cv2.dilate((cat | lap).astype(np.uint8), np.ones((31, 31), np.uint8))
    for n in ("s1", "s4"):
        hole_up |= cv2.dilate(sparks[n].astype(np.uint8), np.ones((17, 17), np.uint8))
    wipe &= hole_up
    lap_up = poly_mask(A.shape, P([(1300, 1280), (1664, 1280), (1664, 1700), (1300, 1660)]))
    wipe |= lap_up & ((np.arange(H)[:, None] < int(1655 * K)) * 1).astype(np.uint8)
    paper = np.median(bg[int(300 * K):int(500 * K), int(300 * K):int(1300 * K)].reshape(-1, 3), axis=0)
    a = cv2.GaussianBlur(wipe.astype(np.float32), (0, 0), 6)[..., None]
    bg = bg * (1 - a) + paper * a
    # стол под тряпкой и под ноутбуком — ровный цвет стола (LaMa рисовала там призрак лапы и края ноутбука), задний край
    # стола за ноутбуком — дорисованная линия туши
    dz = np.zeros((H, Wd), np.uint8)
    dz |= cv2.dilate((am | lap).astype(np.uint8), np.ones((25, 25), np.uint8))
    top = poly_mask(A.shape, P([(240, DESK_Y + 6), (1664, DESK_Y + 10), (1664, 1905), (60, 1905)]))
    dz |= poly_mask(A.shape, P([(1100, 1735), (1664, 1835), (1664, 1915), (1100, 1815)]))   # тень под ноутбуком
    dz |= poly_mask(A.shape, P([(430, 1645), (620, 1645), (620, 1790), (430, 1790)]))       # штрихи и призрак у тряпки
    dz &= top
    dz &= ~(((sat > 40) & (g > 120)) & (sum(sparks.values()) > 0))     # искры s2, s3 не трогать (свои слои)
    # цвет стола — построчная медиана чистого стола (стол светлее сзади, темнее спереди), не одно пятно
    bgg = bg.mean(2)
    ok = (top > 0) & (dz == 0) & (bgg > 150) & (sum(sparks.values()) == 0)
    desk = np.zeros((H, 3), np.float32)
    for y in range(int((DESK_Y + 6) * K), int(1905 * K)):
        r = ok[y]
        desk[y] = np.median(bg[y, r], axis=0) if r.sum() > 50 else desk[y - 1]
    desk = cv2.GaussianBlur(desk[:, None, :], (1, 0), sigmaX=0.1, sigmaY=12)[:, 0, :] if False else desk
    desk = np.repeat(desk[:, None, :], Wd, axis=1)
    a = cv2.GaussianBlur(dz.astype(np.float32), (0, 0), 8)[..., None]
    bg = bg * (1 - a) + desk * a
    ink = np.median(A[(g < 60)].reshape(-1, 3), axis=0) if (g < 60).any() else np.array([40, 40, 40])
    cv2.line(bg, (int(1290 * K), int((DESK_Y - 1) * K)), (Wd, int((DESK_Y + 3) * K)), tuple(float(c) for c in ink), int(5 * K), cv2.LINE_AA)
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
