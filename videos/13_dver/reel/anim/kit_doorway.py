"""Набор слоёв хука рилса 13 для движков (HyperFrames, Remotion, наш numpy): каждый двигающийся предмет — свой PNG
с прозрачностью, фон — без них. Из оплаченных рисунков d1 (дверь, кот, пустое облачко) и d5 (облачко с карандашом),
бесплатно. Координаты ×2 (исходник 1024×1536 увеличен вдвое), сняты сеткой anim.grid 28.10.

Почему так: прежняя сцена двигала куски плоской картинки, поэтому всё, что сдвигалось, открывало «дыру», а её надо
было чем-то заливать. Профессиональная перекладка (After Effects, Rive, Spine) всегда начинается с разобранных слоёв.
Фон под котом заливается построчно цветом этой же строки стены и пола: стена и пол здесь горизонтальные, поэтому
линия пола продолжается сама, а открывается эта заливка лишь узкой полосой у края кота, когда он подпрыгивает."""
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
ORIGIN = (230, 740)               # левый верх сцены (координаты слоёв в kit.json) в ×2
SIZE = (1440, 1920)
BG_TOP = 300                      # фон выше сцены на 300 px: над облачком — место под якорь, обрывкам есть куда лететь
DOOR = (410, 1385)                # внутренний проём: строки фона берутся отсюда
CAT_POLY = [(420, 1700), (640, 1690), (700, 1400), (1120, 1380), (1330, 1360), (1378, 1400), (1378, 1680), (1418, 1700), (1418, 1840),
            (1500, 1840), (1500, 2060), (1378, 2060), (1378, 2300),   # правее 1378 — рамка двери, кроме усов
            (1300, 2660), (700, 2660), (640, 2380), (420, 2380)]
TAIL_POLY = [(420, 1720), (625, 1720), (665, 1860), (705, 1960), (735, 2120), (745, 2380), (420, 2380)]
TAIL_PIVOT = (735, 2230)          # основание хвоста под телом
CAT_FOOT = (1070, 2520)          # точка опоры: между лапами на полу (низ лап — y 2521)
PENCIL_POLY = [(742, 846), (765, 765), (893, 598), (905, 575), (925, 558), (956, 558), (974, 580), (962, 605),
               (940, 630), (804, 803)]   # контур карандаша в d5 (сетка ×2 с шагом 20)
FLAME = (545, 1790)
HEAD = (1030, 1880, 340)          # морда: центр и радиус, в ней дырки — блики глаз
FLOOR_Y = 2250                    # линия стены и пола
ERASE = [(1235, 2395, 1380, 2450), (1350, 2075, 1380, 2400)]               # огонёк хвоста: его свечение на стене тоже убрать
CLOUD_BOX = (590, 740, 1340, 1335); BUB_BOX = (960, 1320, 1070, 1480)


def load(name):
    return np.asarray(Image.open(os.path.join(REEL, ".cache", "anim", name)).convert("RGB")).astype(np.float32)


def rgba(img, m, box=None):
    """Слой: цвет + альфа, обрезанный по рамке маски с запасом; возвращает картинку и её левый верх."""
    ys, xs = np.where(m > 0.02)
    x0, y0, x1, y1 = (xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7) if box is None else box
    out = np.dstack([img[y0:y1, x0:x1], 255 * m[y0:y1, x0:x1]]).clip(0, 255).astype(np.uint8)
    return out, (int(x0), int(y0))


def ink_mask(img, poly, thr=200, close=7):
    """Тушь и шерсть внутри многоугольника: темнее бумаги или цветные (огонёк, глаза); дырки (глаза) залиты."""
    reg = np.zeros(img.shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(poly)], 1)
    g = img.mean(2); sat = img.max(2) - img.min(2)
    m = ((g < thr) | (sat > 45)) & (reg > 0)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
    # дырки заливаются только мелкие (блики, светлые волоски): крупная «дырка» — это стена, замкнутая линией двери
    # или завитком хвоста (первый проход 28.10 вырезал их вместе с котом)
    # заливаются только дырки в морде (блики глаз) и совсем мелкие; бумага между усами и у лап — не кот
    inv = (1 - m).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(inv)
    for i in range(1, n):
        cx, cy = cen[i]; area = st[i, cv2.CC_STAT_AREA]
        if area < 150 or (area < 3000 and ((cx - HEAD[0]) / HEAD[2]) ** 2 + ((cy - HEAD[1]) / HEAD[2]) ** 2 < 1):
            m[lab == i] = 1
    # самый большой кусок и то, что начинается выше линии пола (усы, шерсть); линии пола и рамки — нет
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n <= 1:
        return m
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    keep = (lab == big).astype(np.uint8)
    for i in range(1, n):
        if i != big and st[i, cv2.CC_STAT_AREA] > 40 and st[i, cv2.CC_STAT_TOP] + st[i, cv2.CC_STAT_HEIGHT] < FLOOR_Y:
            keep[lab == i] = 1
    return keep


def main():
    os.makedirs(OUT, exist_ok=True)
    A = load("d1_doorway_x2.png"); B = load("d5_curtain_x2.png")
    cat = ink_mask(A, CAT_POLY)
    floor_shadow = cat.copy(); floor_shadow[:2440] = 0       # тень на полу у лап — не кот: оставить фону
    reg = np.zeros_like(cat); cv2.fillPoly(reg, [np.int32(CAT_POLY)], 1)
    feet = ((A.mean(2) < 150) & (reg > 0)).astype(np.uint8)       # ниже линии лап — только тёмная тушь лап, без тени
    feet = cv2.morphologyEx(feet, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    cat[2440:] = feet[2440:]; cat[2532:] = 0
    for x0, y0, x1, y1 in ERASE:                                 # линия пола у лапы и рамка двери у усов
        cat[y0:y1, x0:x1] = 0
    # рамка двери справа идёт вертикально сквозь усы: вертикальные штрихи в этой полосе — не кот
    # только в столбцах, где рамка тёмная и выше кота (y 1450–1650) — шерсть щеки рядом не трогать
    gA = A.mean(2)
    frame_cols = [x for x in range(1370, 1520) if np.median(gA[1450:1650, x]) < 150]
    for x in frame_cols:
        for xx in range(x - 2, x + 3):
            # тонкая линия: слева и справа через 6 px светло; в шерсти или на усе — не трогать
            run = cat[1650:2100, xx] & (gA[1650:2100, xx] < 150) & (gA[1650:2100, xx - 7] > 150) & (gA[1650:2100, xx + 7] > 150)
            cat[1650:2100, xx] &= ~run
    cat[1650:2100, 1420:1520] &= gA[1650:2100, 1420:1520] < 120     # за рамкой у кота только усы: тёмные штрихи
    cat_bub = np.zeros_like(cat)
    for m in anim.ink_objects(A, box=BUB_BOX, min_area=300): cat_bub |= m
    cat &= ~cv2.dilate(cat_bub, np.ones((9, 9), np.uint8)).astype(bool)          # пузырёк мысли — не кот
    tail_reg = np.zeros_like(cat); cv2.fillPoly(tail_reg, [np.int32(TAIL_POLY)], 1)
    tail = cat & tail_reg; body = cat & ~tail_reg.astype(bool)
    cloud = np.zeros_like(cat); bub = np.zeros_like(cat)
    for m in anim.ink_objects(A, box=CLOUD_BOX, min_area=20000): cloud |= m
    for m in anim.ink_objects(A, box=BUB_BOX, min_area=300): bub |= m
    # фон: всё, что двигается, убрано; каждая строка залита медианой той же строки проёма вне предметов
    hole = cv2.dilate((cat | cloud | bub).astype(np.uint8), np.ones((15, 15), np.uint8))
    cv2.circle(hole, FLAME, 95, 1, -1)
    hole = hole > 0
    bg = A.copy()
    x0, x1 = DOOR
    for y in range(700, 2700):
        row = A[y, x0:x1]; ok = ~hole[y, x0:x1] & (row.mean(1) > 120)
        if ok.sum() > 20 and hole[y].any():
            bg[y, hole[y]] = np.median(row[ok], axis=0)
    # у правой рамки двери линии вертикальные: там дыра заливается по столбцам, иначе рамка рвётся за усами
    x0s, x1s = 1360, 1530
    for x in range(x0s, x1s):
        col = hole[:, x]
        if col.any():
            ys = np.where(~col)[0]
            for c in range(3):
                bg[col, x, c] = np.interp(np.where(col)[0], ys, A[ys, x, c])
    # под лапами — тень на полу: цвет самой тени вокруг лап, а не цвет строки (иначе под котом белое пятно)
    band = np.zeros_like(hole); band[2440:2700] = hole[2440:2700]
    if band.any():
        ring = cv2.dilate(band.astype(np.uint8), np.ones((61, 61), np.uint8)).astype(bool) & ~hole
        ring[:2440] = False
        shade = np.median(A[ring], axis=0)
        bg[band] = shade
        # шов заливки тени мягкий: верхний край ровным прямоугольником читался бы как заплатка
        k = cv2.GaussianBlur(cv2.dilate(band.astype(np.uint8), np.ones((25, 25), np.uint8)).astype(np.float32), (0, 0), 10)[..., None]
        bg = bg * (1 - k) + cv2.GaussianBlur(bg, (0, 0), 14) * k
    soft = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 2)[..., None]
    bg = anim.paper_like(A * (1 - soft) + bg * soft)
    Ap = anim.paper_like(A)
    layers = {}

    def save(name, img, m):
        """Слой с мягким краем в 1 px (без каймы) — в kit/<name>.png, рамка — в kit.json."""
        im, xy = rgba(img, cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8))
        Image.fromarray(im).save(os.path.join(OUT, name + ".png")); layers[name] = dict(xy=xy, wh=im.shape[1::-1])

    for name, m in (("tail", tail), ("body", body), ("cloud", cloud)):
        save(name, Ap, m)
    n, lab = cv2.connectedComponents(bub)
    for i in range(1, n):
        save(f"bubble{i}", Ap, lab == i)
    # карандаш из d5: многоугольник по его контуру, обводка тушью остаётся карандашу
    pm = np.zeros(B.shape[:2], np.uint8); cv2.fillPoly(pm, [np.int32(PENCIL_POLY)], 1)
    # край — по самой обводке тушью: внутри многоугольника, сжатого на 6 px, — корпус; в полосе края — только тушь
    core = cv2.erode(pm, np.ones((13, 13), np.uint8)); band = cv2.dilate(pm, np.ones((9, 9), np.uint8))
    pm = (core | (band & (B.mean(2) < 120))).astype(np.uint8)
    pm = cv2.morphologyEx(pm, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    cs, _ = cv2.findContours(pm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    pm = np.zeros_like(pm); cv2.drawContours(pm, [max(cs, key=cv2.contourArea)], -1, 1, -1)
    save("pencil", anim.paper_like(B), pm)
    ox, oy = ORIGIN; w, h = SIZE
    bg_crop = np.clip(bg[oy - BG_TOP:oy + h, ox:ox + w], 0, 255).astype(np.uint8)
    Image.fromarray(bg_crop).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():                                   # в координаты мира сцены
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    meta = dict(origin=ORIGIN, size=SIZE, bg_top=BG_TOP, layers=layers, tail_pivot=(TAIL_PIVOT[0] - ox, TAIL_PIVOT[1] - oy),
                cat_foot=(CAT_FOOT[0] - ox, CAT_FOOT[1] - oy), fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
