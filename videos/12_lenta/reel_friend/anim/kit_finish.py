"""Слои хука рилса 12 (версия друга) «Все успели, а ты?» для HyperFrames — по базе рилса 13 (стандарт 24).

Рисунок один — gen/k1_finish.png, увеличенный вдвое (.cache/anim/k1_finish_x2.png, waifu2x); координаты ×2, сняты
сеткой anim.grid 02.11. Каждый двигающийся предмет — свой PNG общим шагом anim.save_layer; фон под ними —
anim.inpaint_bg (ореол, LaMa, зерно своей бумаги); хвост — сеткой с физикой (tail_rig.prepare_part).
Слои: кот (тело), хвост, две половинки финишной ленты, трое уходящих, шарик в небе, вздох-облачка у морды."""
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
ORIGIN = (160, 300)               # левый верх сцены (композиции) в ×2
SIZE = (1728, 2772)
CAT_POLY = [(360, 1780), (560, 1790), (700, 1880), (1100, 1860), (1230, 1680), (1340, 1670), (1500, 1900),
            (1530, 2200), (1630, 2270), (1650, 2480), (1450, 2440), (1300, 2470), (1300, 2700), (560, 2700),
            (560, 2300), (360, 2300)]
TAIL_POLY = [(360, 1790), (612, 1790), (612, 2090), (640, 2140), (670, 2200), (680, 2300), (360, 2300)]
TAIL_PIVOT = (650, 2215)          # основание хвоста под телом
FLOOR_Y = 2610                    # ниже — тень у лап: коту только тёмная тушь лап
PUFF_BOX = (1250, 2400, 1560, 2630)      # два облачка вздоха и две капли у морды
PEOPLE_BOX = (770, 1060, 1370, 1320)    # с кубком справа
BALLOON_BOX = (1235, 175, 1400, 600)
TAPE_L = dict(poly=[(282, 1360), (560, 1430), (835, 1590), (815, 1672), (560, 1655), (282, 1495)], pivot=(282, 1428))
TAPE_R = dict(poly=[(1768, 1330), (1500, 1395), (1100, 1560), (885, 1552), (948, 1682), (1250, 1625), (1768, 1505)],
              pivot=(1768, 1418))
POST_L, POST_R = 296, 1754        # внутренние края столбов: столбы остаются фону


def cat_mask(A):
    reg = np.zeros(A.shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(CAT_POLY)], 1)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    m = (((g < 200) | (sat > 45)) & (reg > 0)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    feet = ((g < 140) & (reg > 0)).astype(np.uint8)                  # у лап тень пола: коту только тушь лап
    m[FLOOR_Y:] = feet[FLOOR_Y:]
    inv = (1 - m).astype(np.uint8)                                   # мелкие дырки (блики глаз, волоски) — коту
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < 400:
            m[lab == i] = 1
    puff = np.zeros_like(m)
    for o in anim.ink_objects(A, box=PUFF_BOX, min_area=120):
        puff |= o
    m &= ~cv2.dilate(puff, np.ones((7, 7), np.uint8)).astype(bool)
    return anim.keep_attached(m), puff


def _edge(src, gs, x, lo, hi, paper):
    """Край листа над или под лентой в столбце x: медиана светлой бумаги, без туши."""
    seg = src[max(0, lo):hi, x]; ok = gs[max(0, lo):hi, x] > 200
    return np.median(seg[ok], axis=0) if ok.sum() >= 4 else paper


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "k1_finish_x2.png")).convert("RGB")).astype(np.float32)
    cat, puff = cat_mask(A)
    tail_reg = np.zeros_like(cat); cv2.fillPoly(tail_reg, [np.int32(TAIL_POLY)], 1)
    tail = cat & tail_reg; body = cat & ~tail_reg.astype(bool)
    tail, body = anim.split_part(tail, body)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, cat, around=(*TAIL_PIVOT, 200))
    tl = anim.cut_polygon(A, TAPE_L["poly"]); tl[:, :POST_L] = 0
    tr = anim.cut_polygon(A, TAPE_R["poly"]); tr[:, POST_R:] = 0
    people = np.zeros_like(cat)
    for o in anim.ink_objects(A, box=PEOPLE_BOX, min_area=1500):
        people |= o
    balloon = np.zeros_like(cat)
    for o in anim.ink_objects(A, box=BALLOON_BOX, min_area=200):
        balloon |= o
    # каждый предмет — своей заливкой: одна дыра на весь рисунок (от шарика до лап) уходила в LaMa уменьшенной
    # вчетверо, и под котом оставались тёмные пятна и лапы (лист 02.11)
    bg = A.copy()
    for m in ((cat | puff), people, balloon):
        hole = cv2.dilate(m.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
    src = bg.copy()                                 # лента заливается от фона, где кота уже нет
    # под лентой — чистый лист между столбами: строка заливается медианой той же строки (LaMa на месте ленты
    # дорисовывала новую ленту от её обрывков у столбов — лист 02.11)
    # дыра — сами многоугольники ленты с запасом 30 px: контур рваных концов лежит у их края, по маске он оставался
    poly = np.zeros(A.shape[:2], np.uint8)
    for t in (TAPE_L, TAPE_R):
        cv2.fillPoly(poly, [np.int32(t["poly"])], 1)
    tape = (cv2.dilate(poly | (tl > 0) | (tr > 0), np.ones((61, 61), np.uint8)) > 0)
    tape[:, :POST_L + 4] = False; tape[:, POST_R - 4:] = False
    # по столбцам: цвет листа над лентой плавно переходит в цвет листа под ней (строки в середине ленты целиком
    # закрыты обеими половинками — медианы строки там нет)
    paper = np.median(src[(src.mean(2) > 200) & ~tape], axis=0)
    gs = src.mean(2)
    for x in np.nonzero(tape.any(0))[0]:
        yh = np.nonzero(tape[:, x])[0]; y0, y1 = yh.min(), yh.max()

        top, bot = _edge(src, gs, x, y0 - 24, y0, paper), _edge(src, gs, x, y1 + 1, y1 + 25, paper)
        k = ((yh - y0) / max(1, y1 - y0))[:, None]
        bg[yh, x] = top * (1 - k) + bot * k
    rng = np.random.default_rng(12)                                            # зерно листа в полосу заливки
    grain = cv2.GaussianBlur(rng.normal(0, 1, A.shape[:2]).astype(np.float32), (0, 0), 0.8)
    bg[tape] += (grain[tape] * 1.6)[:, None]
    soft = cv2.GaussianBlur(tape.astype(np.float32), (0, 0), 2)[..., None]
    bg = src * (1 - soft) + bg * soft
    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    for name, img, m, keep in (("tail", Ap_tail, tail, True), ("body", Ap, body, True), ("tape_l", Ap, tl > 0, True),
                               ("tape_r", Ap, tr > 0, True), ("people", Ap, people, False), ("balloon", Ap, balloon, False),
                               ("puff", Ap, puff, False)):
        anim.save_layer(OUT, name, img, m.astype(np.uint8), layers, keep_attached_=keep)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - ox - tx, TAIL_PIVOT[1] - oy - ty),
                          out_dir=OUT, name="tail")
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, tail_pivot=(TAIL_PIVOT[0] - ox, TAIL_PIVOT[1] - oy),
                cat_foot=(980 - ox, 2650 - oy), tape_l_pivot=(TAPE_L["pivot"][0] - ox, TAPE_L["pivot"][1] - oy),
                tape_r_pivot=(TAPE_R["pivot"][0] - ox, TAPE_R["pivot"][1] - oy), fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
