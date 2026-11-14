"""Слои хука рилса 66 «Весь план, а в среду ноль?» для HyperFrames — по образцу рилса 54 (kit_space.py).

Рисунок gen/g1_monday_list.png (1664×2496) ×2 = src/f1.png (3328×4992); координаты сняты по сетке исходника 1664×2496
и умножены на K=2. Слои: кот целиком (хвост с огоньком, лапа, «искры» гордости над лапой — одним куском), длинный
список (полоса от лапы до пола и петли на полу — одним куском, стол в него не входит). Фон — стол и бумага
(anim.inpaint_bg под обоими). Композиция — весь рисунок в половинном размере, её координаты = координаты исходника.
F1=путь — подмена исходника для проб."""
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
K = 2.0                                   # исходник 1664×2496 -> исходник рилса ×2 (3328×4992)
TABLE_Y = 1388                            # ниже — стол: у кота берутся только тёмные лапы


def P(pts):
    return [(int(x * K), int(y * K)) for x, y in pts]


CAT_REG = P([(40, 640), (380, 640), (400, 290), (1170, 290), (1170, 620), (1215, 630), (1215, 752), (1046, 760),
             (1046, 1000), (1010, 1300), (1005, 1470), (930, 1470), (930, 1462), (740, 1462), (740, 1470), (440, 1470),
             (440, 1462), (40, 1462)])
LIST_REG = P([(1022, 686), (1306, 686), (1346, 750), (1350, 1400), (1370, 1450), (1384, 1550), (1372, 1660),
              (1345, 1775), (1308, 1890), (1348, 1945), (1356, 2015), (1336, 2075), (1242, 2108), (1230, 2200),
              (1165, 2216), (893, 2432), (378, 2342), (380, 2308), (728, 2024), (828, 2020), (812, 1900), (826, 1815),
              (900, 1806), (948, 1856), (990, 1700), (1018, 1450), (1026, 900), (1034, 762)])
FEET = P([(700, 1450)])[0]               # ось прыжка кота: между лапами на столе
GRIP = P([(1140, 705)])[0]               # где лапа держит список
HEAD = P([(690, 560)])[0]


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    big = np.zeros((h + 2, w + 2), np.uint8); big[1:-1, 1:-1] = m
    ff = big.copy(); pad = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 2)
    return (big[1:-1, 1:-1] | (ff[1:-1, 1:-1] != 2)).astype(np.uint8)


def poly_mask(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.environ.get("F1") or os.path.join(REEL, "src", "f1.png")).convert("RGB")).astype(np.float32)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    H, Wd = g.shape
    upper = np.zeros((H, Wd), np.uint8); upper[:int(TABLE_Y * K)] = 1
    reg = poly_mask(A.shape, CAT_REG)
    non = (((g < 205) | (sat > 45)) & (upper > 0)) | ((g < 110) & (upper == 0))   # на столе — только тёмные лапы
    ink = cv2.morphologyEx((non & (reg > 0)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8)) & reg
    core = anim.keep_attached(ink)
    cat = (fill_holes(core) & reg).astype(np.uint8)
    cat |= ((g < 150) & (reg > 0) & (upper > 0) & ~cv2.dilate(cat, np.ones((3, 3), np.uint8)).astype(bool)).astype(np.uint8)  # усы, искры
    lreg = poly_mask(A.shape, LIST_REG)
    below = np.zeros_like(upper); below[int(760 * K):] = 1
    below[int(760 * K):int(1010 * K), :int(1047 * K)] = 0      # мех бока заходит на край полосы — остаётся коту
    cat &= ~((lreg > 0) & (below > 0))                      # клин списка под лапой — не кот
    cat = anim.keep_attached(cat, reach=4)
    lm = ((g > 200) | (g < 125)) & (lreg > 0)
    lm = cv2.morphologyEx(lm.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) & lreg
    lm = fill_holes(lm) & lreg
    lm = (lm & ~cv2.dilate(cat, np.ones((9, 9), np.uint8)).astype(bool)).astype(np.uint8)
    lm = anim.keep_attached(lm)
    bg = A.copy()
    split = np.zeros_like(upper); split[:int(1900 * K)] = 1   # дыра выше кропа LaMa (3328) — заливается частями
    for part in (cat, lm & split, lm & (1 - split)):
        hole = cv2.dilate(part.astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    # над столом за котом и списком — чистая бумага: LaMa оставляла обрывки края свитка у лапы (видны, когда список
    # падает); «искры» гордости над лапой не трогаются — они нарисованы на бумаге
    wipe = np.zeros_like(upper); wipe[int(640 * K):int(TABLE_Y * K) - 20, int(990 * K):int(1400 * K)] = 1
    wipe &= ~cv2.dilate(cat, np.ones((7, 7), np.uint8)).astype(bool)
    paper = np.median(bg[int(200 * K):int(300 * K), int(1300 * K):int(1600 * K)].reshape(-1, 3), axis=0)
    a = cv2.GaussianBlur(wipe.astype(np.float32), (0, 0), 6)[..., None]
    bg = bg * (1 - a) + paper * a
    layers = {}
    anim.save_layer(OUT, "list", Ap, lm, layers, keep_attached_=False)
    anim.save_layer(OUT, "cat", Ap, cat, layers, keep_attached_=False)
    Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    meta = dict(origin=(0, 0), size=(Wd, H), layers=layers, feet=FEET, grip=GRIP, head=HEAD, fps=30)
    for f in ["bg.png"] + [n + ".png" for n in layers]:
        im = Image.open(os.path.join(OUT, f)); im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(OUT, f))
    for v in layers.values():
        v["xy"] = (v["xy"][0] // 2, v["xy"][1] // 2); v["wh"] = (v["wh"][0] // 2, v["wh"][1] // 2)
    h2 = lambda p: (p[0] // 2, p[1] // 2)     # noqa: E731
    meta.update(size=(Wd // 2, H // 2), feet=h2(FEET), grip=h2(GRIP), head=h2(HEAD), scale=0.5)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
