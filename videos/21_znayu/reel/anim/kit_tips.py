"""Слои хука рилса 21 «Знаешь как, а не делаешь?» для HyperFrames — по базе рилса 13.

Рисунок gen/k1_tips.png ×2 (.cache/anim/k1_tips_x2.png, waifu2x); координаты ×2, сняты сеткой anim.grid 04.11. Слои: кот
(тело с двумя листками на голове), хвост (сеткой с физикой, tail_rig), одиннадцать листков-советов в воздухе, столик с
тремя кружками — фон (немытые кружки стоят, пока кот тонет в советах). Фон — anim.inpaint_bg под каждым предметом."""
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
ORIGIN = (0, 0)                 # левый верх сцены (композиции) в ×2
SIZE = (2048, 3072)
CAT_POLY = [(660, 1360), (940, 1360), (1000, 1250), (1240, 1230), (1310, 1240), (1330, 1500), (1370, 1700),
            (1470, 1760), (1470, 1840), (1370, 1900), (1350, 2100), (1340, 2500), (1310, 2850), (560, 2870), (470, 2600),
            (470, 2080), (360, 2060), (360, 1880), (420, 1700), (420, 1560), (520, 1450), (660, 1440)]
TAIL_POLY = [(40, 2040), (470, 2040), (470, 2600), (560, 2870), (40, 2890)]
FLAME_POLY = [(313, 2063), (332, 2080), (332, 2115), (345, 2140), (354, 2133), (367, 2175), (362, 2217), (320, 2224),
              (268, 2226), (256, 2190), (260, 2160), (276, 2128), (284, 2140), (300, 2103)]
EAR_POLY = [(960, 1420), (1000, 1300), (1160, 1250), (1260, 1250), (1290, 1400), (1300, 1560), (1100, 1540)]   # правое ухо на кремовой перерисовке 04.11
TAIL_PIVOT = (470, 2700)          # основание хвоста у тела
PAGES_BOX = (100, 30, 1800, 1420)
FEET = (900, 2840)                # ось вздрагивания кота
HEAD = (880, 1750)


def fill_holes(m):
    """Всё, что внутри контура кота (кружка, экран телефона, просветы) — коту: заливка снаружи, остальное — внутри."""
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    ff = m.copy(); pad = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(np.uint8)


def ink_in(A, poly, thr=130):
    """Цветной рисунок (стена и пол в акварели): кот — тёмная тушь и шерсть, светлое внутри контура (глаза, листки на
    голове, подушечки) доливает fill_holes; пол и стена светлее порога и в маску не идут."""
    reg = np.zeros(A.shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(poly)], 1)
    sat = A.max(2) - A.min(2)
    low = np.zeros(A.shape[:2], bool); low[2700:] = True            # тень кота на полу — коричневая, не шерсть
    m = ((A.mean(2) < thr) & ~(low & (sat > 50)) & (reg > 0)).astype(np.uint8)
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)), reg


def outlined(A, box, cut, min_area=20000):
    """Листки в воздухе — замкнутые контуры тушью на цветной стене: внешняя граница контура, залитая (ink_objects
    ищет бумагу светлее фона, а листки светлее стены — не годится)."""
    x0, y0, x1, y1 = box
    ink = np.zeros(A.shape[:2], np.uint8); ink[y0:y1, x0:x1] = (A[y0:y1, x0:x1].mean(2) < 110)
    ink &= ~cut
    ink = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    cs, _ = cv2.findContours(ink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cs:
        if cv2.contourArea(c) >= min_area:
            k = np.zeros_like(ink); cv2.drawContours(k, [c], -1, 1, -1); out.append(k)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "k1_tips_x2.png")).convert("RGB")).astype(np.float32)
    cat_ink, cat_reg = ink_in(A, CAT_POLY)
    tail_ink, tail_reg = ink_in(A, TAIL_POLY)
    flame = np.zeros(A.shape[:2], np.uint8); cv2.fillPoly(flame, [np.int32(FLAME_POLY)], 1)
    ear = np.zeros(A.shape[:2], np.uint8); cv2.fillPoly(ear, [np.int32(EAR_POLY)], 1)
    ear &= ((A.mean(2) < 200) | ((A.max(2) - A.min(2)) > 40)).astype(np.uint8)   # розовое ухо светлее порога туши
    cat = fill_holes(anim.keep_attached(cat_ink | ear)) & cat_reg
    tail = (anim.keep_attached(tail_ink | flame) | flame) & (tail_reg | flame) & ~cat.astype(bool)
    full = (cat | tail).astype(np.uint8)
    tail, body = anim.split_part(tail, cat)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, full, around=(*TAIL_PIVOT, 200))
    pages = [o for o in outlined(A, PAGES_BOX, cv2.dilate(full, np.ones((15, 15), np.uint8)))]
    pages.sort(key=lambda o: np.argwhere(o)[:, 0].mean())
    bg = A.copy()
    for m in [full] + [n.astype(np.uint8) for n in pages]:
        hole = cv2.dilate(m.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    parts = [("tail", Ap_tail, tail, True), ("body", Ap, body, True)]
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
