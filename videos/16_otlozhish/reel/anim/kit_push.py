"""Слои хука рилса 16 «Отложишь дело, и тебе легче?» для HyperFrames — по базе рилса 13 (стандарт 24).

Рисунок gen/o1_push.png ×2 (.cache/anim/o1_push_x2.png, waifu2x); координаты ×2, сняты сеткой anim.grid 03.11. Слои: кот
(тело с лапами), хвост (сеткой с физикой, tail_rig), тяжёлая коробка-дело (едет от лап рывками), облачко пыли из-под
неё. Кровать справа — фон. Фон — anim.inpaint_bg под каждым предметом отдельно."""
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
ORIGIN = (0, 1000)                # левый верх сцены (композиции) в ×2
SIZE = (2048, 1500)
CAT_POLY = [(300, 1300), (360, 1265), (470, 1325), (560, 1285), (760, 1225), (835, 1255), (885, 1430), (945, 1520),
            (965, 1615), (1048, 1625), (1048, 1712), (1005, 1722), (1008, 1852), (990, 1995), (900, 2005), (760, 2050), (700, 2200),
            (725, 2345), (555, 2350), (480, 2255), (400, 2305), (315, 2350), (215, 2350), (240, 2250), (330, 2152),
            (48, 2152), (48, 1478), (250, 1448)]
TAIL_POLY = [(48, 1478), (335, 1478), (352, 1700), (300, 1800), (330, 1900), (405, 2050), (432, 2122), (330, 2160),
             (48, 2160)]
TAIL_PIVOT = (400, 2100)          # основание хвоста у спины
BOX_EDGE_X = 935                  # правее — только тушь коту (лапы и усы на фоне серой коробки)
FLOOR_Y = 2290                    # ниже — тень пола: коту только тушь лап
BOX_BOX = (935, 1460, 1725, 2265)
PUFF_BOX = (800, 2228, 942, 2312)
FEET = (520, 2335)
PAWS = (985, 1800)                # где лапы упираются в коробку
BOX_FOOT = (1330, 2250)           # середина дна коробки: ось её крена


def cat_mask(A):
    reg = np.zeros(A.shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(CAT_POLY)], 1)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    m = (((g < 200) | (sat > 45)) & (reg > 0)).astype(np.uint8)
    m[:, BOX_EDGE_X:] = ((g < 110) & (reg > 0))[:, BOX_EDGE_X:]      # серая коробка под лапами — не кот
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    m[FLOOR_Y:] = ((g < 130) & (reg > 0))[FLOOR_Y:]
    inv = (1 - m).astype(np.uint8)                                   # блики глаз, рот, полоски — коту
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < 2500:
            m[lab == i] = 1
    return anim.keep_attached(m)


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "o1_push_x2.png")).convert("RGB")).astype(np.float32)
    cat = cat_mask(A)
    tail_reg = np.zeros_like(cat); cv2.fillPoly(tail_reg, [np.int32(TAIL_POLY)], 1)
    tail = cat & tail_reg; body = cat & ~tail_reg.astype(bool)
    tail, body = anim.split_part(tail, body)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, cat, around=(*TAIL_PIVOT, 200))
    box = np.zeros_like(cat)
    for o in anim.ink_objects(A, box=BOX_BOX, min_area=20000):
        box |= o
    box &= ~cv2.dilate(cat.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    # коробка целиком: выпуклый контур её рисунка (коробка выпуклая). Там, где её закрывали лапы, в слое была дыра —
    # коробка отъезжает и открывала её (лист 03.11); дыра закрашивается серым самой коробки, левый край — тушью
    n, lab, st, _ = cv2.connectedComponentsWithStats(box.astype(np.uint8))
    big = lab == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    hull = np.zeros_like(cat); cv2.fillPoly(hull, [cv2.convexHull(np.argwhere(big)[:, ::-1].astype(np.int32))], 1)
    hull = hull.astype(bool)
    bite = hull & (~big | (cv2.dilate(cat.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0))
    left = np.where(hull.any(1), hull.argmax(1), 10 ** 6)[:, None]
    xx = np.arange(A.shape[1])[None, :]
    bite |= hull & (A.mean(2) < 120) & (xx < left + 90)               # шерсть лапы у левого края — тоже закрасить
    gray = np.median(A[big & (A.mean(2) > 150)], axis=0)
    img = A.copy(); img[~hull] = gray
    box_img = cv2.inpaint(np.clip(img, 0, 255).astype(np.uint8), bite.astype(np.uint8), 5, cv2.INPAINT_TELEA).astype(np.float32)
    for y in np.nonzero(bite.any(1))[0]:                              # левый край коробки — тушью, как на рисунке
        xs = np.nonzero(hull[y])[0]
        if len(xs): box_img[y, xs[0]:xs[0] + 6] = (40, 40, 42)
    box = hull.astype(np.uint8)
    puff = np.zeros_like(cat)
    for o in anim.ink_objects(A, box=PUFF_BOX, min_area=80):
        puff |= o
    puff &= ~(box | cat.astype(bool))
    bg = A.copy()
    for m in (cat, box, puff):
        hole = cv2.dilate(m.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    # стена и пол за котом и коробкой ровные: LaMa оставляла серый призрак головы и куски контура коробки (лист
    # 03.11) — полоса заливается образцом той же стены, линии пола и пола из чистых столбцов у левого края рисунка
    x0, x1, y0, y1 = 40, 1735, 1200, 2380
    ref = np.median(A[y0:y1, 4:36], axis=1)                                   # профиль стена → линия пола → пол
    rng = np.random.default_rng(16)
    grain = cv2.GaussianBlur(rng.normal(0, 1, (y1 - y0, x1 - x0)).astype(np.float32), (0, 0), 0.8)[..., None] * 1.6
    fill = np.repeat(ref[:, None, :], x1 - x0, axis=1) + grain
    m = np.zeros(bg.shape[:2], np.float32); m[y0 + 10:y1 - 10, x0 + 10:x1 - 10] = 1
    m = cv2.GaussianBlur(m, (0, 0), 6)[y0:y1, x0:x1, None]
    bg[y0:y1, x0:x1] = bg[y0:y1, x0:x1] * (1 - m) + fill * m
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    for name, img, m, keep in (("tail", Ap_tail, tail, True), ("body", Ap, body, True), ("box", anim.paper_like(box_img), box, False),
                               ("puff", Ap, puff, False)):
        anim.save_layer(OUT, name, img, m.astype(np.uint8), layers, keep_attached_=keep)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - ox - tx, TAIL_PIVOT[1] - oy - ty),
                          out_dir=OUT, name="tail")
    rel = lambda p: (p[0] - ox, p[1] - oy)      # noqa: E731
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, tail_pivot=rel(TAIL_PIVOT), feet=rel(FEET), paws=rel(PAWS),
                box_foot=rel(BOX_FOOT), fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
