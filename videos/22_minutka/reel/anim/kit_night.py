"""Слои хука рилса 22 «Ляжешь на минутку, а уже ночь?» для HyperFrames — по базе рилса 13.

Рисунок gen/p1_hook.png ×2 (.cache/anim/p1_hook_x2.png, upscale ×2); координаты ×2, сняты сеткой anim.grid 04.11.
Слои: кот с телефоном на диване (тело), хвост, свисающий с дивана (сеткой с физикой, tail_rig). Окно с пустым стеклом
и диван — фон: небо в окне (таймлапс день → закат → ночь, солнце, луна, звёзды, облака) рисует композиция внутри рамы
PANE. Фон под котом — anim.inpaint_bg."""
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
ORIGIN = (0, 0)
SIZE = (2048, 3072)
PANE = (618, 364, 1424, 1162)      # внутренний край рамы окна — небо рисует композиция
CAT_POLY = [(330, 1640), (400, 1560), (560, 1530), (740, 1390), (830, 1400), (900, 1560), (1000, 1570), (1010, 1570),
            (1030, 1560), (1180, 1550), (1210, 1760), (1440, 1900), (1590, 1920), (1610, 2070), (1530, 2190),
            (1420, 2220), (1200, 2300), (780, 2300), (560, 2250), (420, 2150), (380, 1980), (340, 1820)]
TAIL_POLY = [(1380, 2190), (1640, 2200), (1640, 2620), (1480, 2640), (1420, 2780), (1180, 2780), (1180, 2540),
             (1360, 2470)]
FUR_BOX = (200, 1690, 560, 1915)   # спинка дивана слева от уха кота, ×2
PHONE_POLY = [(1010, 1590), (1036, 1566), (1170, 1556), (1192, 1590), (1186, 1830), (1100, 1880), (1010, 1860)]
TAIL_PIVOT = (1440, 2220)         # основание хвоста у края дивана
FEET = (900, 2280)                # ось вздрагивания кота (спина на сиденье)
HEAD = (650, 1800)


def region(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    ff = m.copy(); pad = np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(np.uint8)


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "p1_hook_x2.png")).convert("RGB")).astype(np.float32)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    ink = ((g < 125) | (sat > 70)).astype(np.uint8)                       # шерсть и тушь, глаза, щёки, подушечки, огонёк
    ink = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    cat_reg, tail_reg = region(A.shape, CAT_POLY), region(A.shape, TAIL_POLY)
    phone = region(A.shape, PHONE_POLY)                                    # телефон светлый — берётся целиком по контуру
    cat = (fill_holes(anim.keep_attached(ink & cat_reg)) | phone) & (cat_reg | phone)
    cat = anim.keep_attached(cat.astype(np.uint8))
    tail = fill_holes(anim.keep_attached(ink & tail_reg)) & tail_reg & (1 - cat)
    full = (cat | tail).astype(np.uint8)
    tail, body = anim.split_part(tail, cat)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, full, around=(*TAIL_PIVOT, 200))
    hole = cv2.dilate(full, np.ones((15, 15), np.uint8)) > 0
    bg = anim.inpaint_bg(A, hole, cache_dir=CACHE)
    # остатки шерсти и огонька, которые LaMa дорисовала из кота (серо-синие пятна у уха, у основания хвоста): второй
    # проход по пятнам, а не по линиям дивана — линии длинные и тонкие, пятна плотные
    gb = bg.mean(2); sb = bg.max(2) - bg.min(2)
    res = (hole & ((gb < 175) | (sb > 55))).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.morphologyEx(res, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)))
    blobs = np.isin(lab, [i for i in range(1, n) if st[i, 4] > 300 and min(st[i, 2], st[i, 3]) > 25])
    if blobs.any():
        bg = anim.inpaint_bg(bg, cv2.dilate(blobs.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0, cache_dir=CACHE)
    # спинка дивана слева от уха: LaMa дорисовала туда шерсть (лист 04.11) — тон спинки дивана, контур спинки остаётся
    x0, y0, x1, y1 = FUR_BOX
    sub = bg[y0:y1, x0:x1]; gs = sub.mean(2); ss = sub.max(2) - sub.min(2)
    fur = (((gs < 205) & (ss < 40) & (gs > 70)) | ((sub[..., 2] > sub[..., 0] + 4) & (gs < 215))).astype(np.uint8)
    fur = cv2.morphologyEx(fur, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cush = np.median(A[y0 + 300:y0 + 380, x0 + 60:x0 + 160].reshape(-1, 3), 0)          # подушка/спинка ниже пятна
    soft = cv2.GaussianBlur(fur.astype(np.float32), (0, 0), 3)[..., None]
    bg[y0:y1, x0:x1] = sub * (1 - soft) + cush * soft
    # кайма дыры, где на рисунке был не кот, а светлый диван или подушка: исходные пиксели честнее любой заливки
    keep = hole & (cv2.dilate(full, np.ones((9, 9), np.uint8)) == 0) & (A.mean(2) > 185)
    soft = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 2)[..., None]
    bg = bg * (1 - soft) + A * soft
    Ap = A
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    for name, img, m in [("tail", Ap_tail, tail), ("body", Ap, body)]:
        anim.save_layer(OUT, name, img, m.astype(np.uint8), layers, keep_attached_=True)
    Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - tx, TAIL_PIVOT[1] - ty), out_dir=OUT,
                          name="tail")
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, tail_pivot=TAIL_PIVOT, feet=FEET, head=HEAD, pane=PANE, fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    S = np.zeros_like(A) + (40, 70, 160)                                    # лист слоёв на синем — глазами
    for name in ("tail", "body"):
        L = np.asarray(Image.open(os.path.join(OUT, name + ".png")).convert("RGBA")).astype(np.float32)
        x, y = layers[name]["xy"]; a = L[..., 3:] / 255
        S[y:y + L.shape[0], x:x + L.shape[1]] = L[..., :3] * a + S[y:y + L.shape[0], x:x + L.shape[1]] * (1 - a)
    both = np.concatenate([np.clip(bg, 0, 255), S], 1)
    Image.fromarray(both.astype(np.uint8)).resize((1024, 768)).save(os.path.join(CACHE, "night_layers.jpg"))
    print(json.dumps({k: v for k, v in meta.items() if k != "layers"}), {k: (v["xy"], v["wh"]) for k, v in layers.items()})


if __name__ == "__main__":
    main()
