"""Слои хука рилса 20 «Купил абонемент, а не ходишь?» для HyperFrames — по базе рилса 13.

Рисунок gen/g1_hook.png ×2 (.cache/anim/g1_hook_x2.png, upscale.upscale ×2); координаты ×2, сняты сеткой anim.grid 04.11.
Слои: кот (тело с лапой на подушке), хвост (сеткой с физикой, tail_rig), карточка абонемента на верёвке (без гвоздя),
пакет с пыльными кроссовками. Нарисованные пылинки над пакетом убраны с фона — пыль рисует композиция. Фон под каждым
предметом — anim.inpaint_bg. Стена цветная (бежевая акварель), поэтому маски — по отличию от цвета стены/дивана, а не
«тушь на бумаге»."""
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
CAT_POLY = [(850, 1385), (1000, 1325), (1150, 1310), (1310, 1340), (1490, 1385), (1640, 1550), (1540, 1610), (1480, 1640),
            (1465, 1760), (1465, 1890), (1345, 1925), (1300, 1965), (1255, 2065), (1150, 2095), (800, 2110), (540, 2105),
            (515, 2000), (535, 1880), (575, 1820), (590, 1740), (650, 1735), (705, 1800), (720, 1700), (800, 1640),
            (870, 1600), (900, 1560), (890, 1480)]
TAIL_POLY = [(515, 1735), (700, 1735), (718, 1880), (705, 2000), (765, 2040), (890, 2060), (890, 2112), (515, 2112)]
TAIL_PIVOT = (865, 2085)
CARD_QUAD = [(798, 620), (1250, 550), (1266, 795), (842, 872)]
STRINGS = [((1008, 232), (848, 632)), ((1024, 232), (1180, 578))]
BAG_POLY = [(200, 2445), (250, 2400), (285, 2330), (350, 2305), (420, 2330), (470, 2300), (540, 2295), (600, 2340),
            (645, 2420), (715, 2455), (748, 2880), (305, 2960), (148, 2878)]
PILLOW_POLY = [(1460, 1700), (1760, 1600), (1760, 2080), (1150, 2080), (1300, 1930), (1460, 1880)]
DUST_BOX = (300, 2090, 520, 2300)
FEET = (1000, 2100)               # ось ёрзанья кота
HEAD = (1250, 1560)
NAIL = (1015, 215)


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    ff = m.copy(); pad = np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(np.uint8)


def region(shape, poly):
    r = np.zeros(shape[:2], np.uint8); cv2.fillPoly(r, [np.int32(poly)], 1); return r


def unlike(A, reg, ref_box, thr):
    """Пиксели в многоугольнике, заметно отличные от цвета фона рядом (ref_box — кусок чистого фона)."""
    x0, y0, x1, y1 = ref_box
    ref = np.median(A[y0:y1, x0:x1].reshape(-1, 3), 0)
    d = np.sqrt(((A - ref) ** 2).sum(2))
    m = ((d > thr) & (reg > 0)).astype(np.uint8)
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))


def main():
    os.makedirs(OUT, exist_ok=True)
    A = np.asarray(Image.open(os.path.join(CACHE, "g1_hook_x2.png")).convert("RGB")).astype(np.float32)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    cat_reg = region(A.shape, CAT_POLY); tail_reg = region(A.shape, TAIL_POLY)
    dark = ((g < 120) | ((sat > 70) & (g > 120))).astype(np.uint8)       # чёрная шерсть + огонёк, глаз, щёки, ухо
    whole = fill_holes(anim.keep_attached(cv2.morphologyEx(dark & (cat_reg | tail_reg), cv2.MORPH_CLOSE,
                                                           np.ones((5, 5), np.uint8)))) & (cat_reg | tail_reg)
    pil = region(A.shape, PILLOW_POLY).astype(bool) & (g > 175) & (sat < 70)    # подушка в просвете лапы — не кот
    whole[pil] = 0
    whole = anim.keep_attached(whole)
    cat = whole & (1 - tail_reg)
    tail = whole & tail_reg
    full = (cat | tail).astype(np.uint8)
    tail, body = anim.split_part(tail, cat)
    tail, body, tail_fill = anim.claim_strokes(A, tail, body)
    tail = anim.underlap(tail, body, full, around=(*TAIL_PIVOT, 200))
    card = anim.cut_polygon(A, CARD_QUAD, grow=21, sure=11)
    lines = np.zeros_like(card)
    for p0, p1 in STRINGS:
        cv2.line(lines, p0, p1, 1, 30)
    card = (card | (lines & unlike(A, np.ones_like(card), (600, 300, 760, 500), 14))).astype(np.uint8)
    card = cv2.morphologyEx(card, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    card[:228] = 0                                                         # гвоздь остаётся на стене
    bag = anim.cut_polygon(A, BAG_POLY, grow=21, sure=11)
    dust = np.zeros_like(full)
    x0, y0, x1, y1 = DUST_BOX
    dust[y0:y1, x0:x1] = (unlike(A, np.ones_like(full), (180, 2150, 290, 2260), 22)[y0:y1, x0:x1])
    bg = A.copy()
    for m in [full, card, bag, dust]:
        hole = cv2.dilate(m.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
        bg = anim.inpaint_bg(bg, hole, cache_dir=CACHE)
        if m is full:                     # LaMa дорисовала под котом тёмный призрак щеки — его видно, когда кот ёрзает:
            ring = cv2.dilate(hole.astype(np.uint8), np.ones((41, 41), np.uint8)).astype(bool) & ~hole   # тёмное → тон дивана
            sat_ = A.max(2) - A.min(2); g_ = A.mean(2)
            ring &= (g_ > 140) & (g_ < 215) & (sat_ > 6) & (sat_ < 40)      # только ткань дивана: не кремовая стена, не подушка
            sofa = np.median(A[ring], 0)
            gb = bg.mean(2); fix = hole & (gb < sofa.mean() - 14)          # тёмный призрак кота — в тон дивана, линии остаются
            fix[2040:] = False                                             # тень кота на сиденье — оставить
            soft = cv2.GaussianBlur(fix.astype(np.float32), (0, 0), 6)[..., None]
            bg = bg * (1 - soft) + (sofa * 0.97) * soft
    # стена теперь чистая бумага (владелец 04.11): дыра от таблички и верёвок — ровным тоном бумаги с её зерном, без
    # призрака рамки (LaMa оставляла бледный прямоугольник, а табличка в хуке падает и открывает стену целиком)
    ch = cv2.dilate(card, np.ones((31, 31), np.uint8)) > 0
    pring = cv2.dilate(ch.astype(np.uint8), np.ones((61, 61), np.uint8)).astype(bool) & ~ch
    paper = np.median(A[pring], 0)
    rng = np.random.default_rng(20)
    grain = cv2.GaussianBlur(rng.normal(0, 1, A.shape[:2]).astype(np.float32), (0, 0), 0.8)
    grain *= float((A - cv2.GaussianBlur(A, (0, 0), 3))[100:400, 100:400].std()) / max(float(grain.std()), 1e-6)
    soft = cv2.GaussianBlur(ch.astype(np.float32), (0, 0), 8)[..., None]
    soft = np.maximum(soft, ch[..., None].astype(np.float32))
    bg = bg * (1 - soft) + (paper + grain[..., None]) * soft
    Ap = A
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    for name, img, m in [("tail", Ap_tail, tail), ("body", Ap, body), ("card", Ap, card), ("bag", Ap, bag)]:
        anim.save_layer(OUT, name, img, m.astype(np.uint8), layers, keep_attached_=True)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    tx, ty = layers["tail"]["xy"]
    tail_rig.prepare_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - ox - tx, TAIL_PIVOT[1] - oy - ty),
                          out_dir=OUT, name="tail")
    rel = lambda p: (p[0] - ox, p[1] - oy)      # noqa: E731
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, tail_pivot=rel(TAIL_PIVOT), feet=rel(FEET), head=rel(HEAD),
                nail=rel(NAIL), fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))
    S = np.zeros((h, w, 3), np.float32) + (40, 70, 160)                    # лист слоёв на синем — глазами
    for name in ("bag", "card", "body", "tail"):
        L = np.asarray(Image.open(os.path.join(OUT, name + ".png")).convert("RGBA")).astype(np.float32)
        x, y = layers[name]["xy"]; a = L[..., 3:] / 255
        S[y:y + L.shape[0], x:x + L.shape[1]] = L[..., :3] * a + S[y:y + L.shape[0], x:x + L.shape[1]] * (1 - a)
    both = np.concatenate([np.clip(bg, 0, 255), S], 1)
    Image.fromarray(both.astype(np.uint8)).resize((w // 2, h // 4)).save(os.path.join(CACHE, "sofa_layers.jpg"))


if __name__ == "__main__":
    main()
