"""Слои хука рилса 65 «Тянешь, чтобы было идеально?» для HyperFrames — по образцу рилса 54 (kit_space.py).

Рисунок gen/g1_bowl_museum.png (1664×2496) ×2 = src/f1.png (3328×4992); координаты сняты по сетке вида 832×1248 и
умножены на K=4. Слои: кот целиком (хвост с огоньком, лапа у щеки), «штрихи испуга» у уха (выскакивают на ударе),
экспонат спереди — миска, столбики, красный канат и табличка (стоит перед котом: кот отшатывается за ним).
Фон — бумага, под слоями anim.inpaint_bg. F1=путь — подмена исходника для проб."""
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
K = 4.0
ORIGIN = (0, 1000)                        # вид y 250 -> ×2
SIZE = (3328, 3600)                       # до вида y 1150


def P(pts):
    return [(int(x * K), int(y * K)) for x, y in pts]


CAT_REG = P([(3, 270), (555, 270), (555, 500), (590, 560), (590, 660), (505, 720), (505, 935), (3, 935)])   # x≥3: save_layer берёт поле 6 px
MARKS_BOX = tuple(int(v * K) for v in (555, 395, 622, 497))
POST_L = P([(318, 852), (338, 852), (340, 863), (340, 984), (369, 991), (369, 1017), (289, 1017), (289, 991),
             (317, 984), (317, 863)])   # столбик: шар, стойка, основание — узко, без меха
ROPE_BOX = tuple(int(v * K) for v in (330, 815, 728, 918))
EXHIBIT = P([(390, 905), (520, 905), (528, 798), (782, 798), (782, 1112), (348, 1112), (348, 1022), (390, 1000)])
PAW_R = (467, 873, 38, 38)                # правая лапа кота на краю миски (вид): остаётся коту
PIVOT = P([(300, 900)])[0]                # кот качается от лап
HEAD = P([(370, 520)])[0]
MARKS_C = P([(588, 446)])[0]
BOWL_C = P([(530, 975)])[0]


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    big = np.ones((h + 2, w + 2), np.uint8); big[1:-1, 1:-1] = m; big[0, :] = 0; big[:, 0] = 0; big[-1, :] = 0
    ff = big.copy(); pad = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 2)
    return (big[1:-1, 1:-1] | (ff[1:-1, 1:-1] != 2)).astype(np.uint8)


def poly_mask(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def box_mask(shape, box):
    r = np.zeros(shape[:2], np.uint8); x0, y0, x1, y1 = box; r[y0:y1, x0:x1] = 1; return r


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.environ.get("F1") or os.path.join(REEL, "src", "f1.png")).convert("RGB")).astype(np.float32)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    non = ((g < 225) | (sat > 34)).astype(np.uint8)
    r, gg, bb = A[..., 0], A[..., 1], A[..., 2]
    red = ((r > 110) & (r - gg > 60) & (bb > 0.7 * gg) & (r - bb > 40)).astype(np.uint8)   # канат, не оранжевые подушечки
    # экспонат спереди: столбики, канат, миска, табличка, крошки
    rope = cv2.morphologyEx(red & box_mask(A.shape, ROPE_BOX), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    rope = cv2.dilate(rope, np.ones((9, 9), np.uint8)) & cv2.dilate(non, np.ones((3, 3), np.uint8))
    pl = poly_mask(A.shape, POST_L)
    cv2.circle(pl, (int(328 * K), int(841 * K)), int(15 * K), 1, -1)      # шар столбика
    post = fill_holes(cv2.morphologyEx(non & pl, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))) & pl
    paw = np.zeros(A.shape[:2], np.uint8)
    cx, cy, rx, ry = PAW_R; cv2.ellipse(paw, (int(cx * K), int(cy * K)), (int(rx * K), int(ry * K)), 0, 0, 360, 1, -1)
    exr = poly_mask(A.shape, EXHIBIT) & (1 - paw)
    ex = cv2.morphologyEx(non & exr, cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8)) & exr
    front = ((rope | post | ex) > 0).astype(np.uint8)
    # кот: тушь в области кота без экспоната
    reg = poly_mask(A.shape, CAT_REG) & (1 - exr)
    ink = cv2.morphologyEx(non & reg, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8)) & reg
    core = anim.keep_attached(ink)
    cat = (fill_holes(core) & reg).astype(np.uint8)
    cat |= (ink & ~cv2.dilate(cat, np.ones((3, 3), np.uint8))).astype(np.uint8)   # усы — мазки рядом с котом
    # канат и столбик спереди кота: в слое кота под ними дорисован мех (иначе при отшатывании видна дыра)
    over = (cv2.dilate(front, np.ones((5, 5), np.uint8)) & cat).astype(np.uint8)
    x0, y0, bw, bh = cv2.boundingRect(over); x1, y1 = x0 + bw, y0 + bh
    crop = np.ascontiguousarray(np.clip(A[y0:y1, x0:x1], 0, 255).astype(np.uint8))
    om = np.ascontiguousarray((over[y0:y1, x0:x1] > 0).astype(np.uint8) * 255)
    small = cv2.resize(crop, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)   # мех под канатом — мягко, быстро
    sm = (cv2.resize(om, small.shape[1::-1], interpolation=cv2.INTER_NEAREST) > 0).astype(np.uint8) * 255
    fill = cv2.resize(cv2.inpaint(small, cv2.dilate(sm, np.ones((3, 3), np.uint8)), 5, cv2.INPAINT_TELEA), crop.shape[1::-1],
                      interpolation=cv2.INTER_CUBIC)
    catimg = A.copy()
    catimg[y0:y1, x0:x1] = np.where(om[..., None] > 0, fill, crop).astype(np.float32)
    cat_edge = cv2.erode(fill_holes(cat), np.ones((9, 9), np.uint8))
    cat = (cat * ~((front > 0) & (cat_edge == 0))).astype(np.uint8)   # снаружи силуэта канат — только у экспоната
    mk = cv2.morphologyEx(((g < 140) & (box_mask(A.shape, MARKS_BOX) > 0)).astype(np.uint8), cv2.MORPH_CLOSE,
                          np.ones((7, 7), np.uint8))
    hole = cv2.dilate((cat | mk | front).astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
    bg = anim.inpaint_bg(A.copy(), hole, cache_dir=CACHE)
    Ap, bg, Cp = anim.paper_like(A), anim.paper_like(bg), anim.paper_like(catimg)
    layers = {}
    anim.save_layer(OUT, "cat", Cp, cat, layers, keep_attached_=False)
    anim.save_layer(OUT, "marks", Ap, mk, layers, keep_attached_=False)
    anim.save_layer(OUT, "front", Ap, front, layers, keep_attached_=False)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    rel = lambda p: (p[0] - ox, p[1] - oy)      # noqa: E731
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, pivot=rel(PIVOT), head=rel(HEAD), marks_c=rel(MARKS_C),
                bowl_c=rel(BOWL_C), fps=30)
    for f in ["bg.png"] + [n + ".png" for n in layers]:
        im = Image.open(os.path.join(OUT, f)); im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(OUT, f))
    for v in layers.values():
        v["xy"] = (v["xy"][0] // 2, v["xy"][1] // 2); v["wh"] = (v["wh"][0] // 2, v["wh"][1] // 2)
    h2 = lambda p: (p[0] // 2, p[1] // 2)     # noqa: E731
    meta.update(size=(w // 2, h // 2), pivot=h2(meta["pivot"]), head=h2(meta["head"]), marks_c=h2(meta["marks_c"]),
                bowl_c=h2(meta["bowl_c"]), scale=0.5)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
