"""Слои хука рилса 20 «У тебя нет сил, а на ленту есть?» для HyperFrames — по базе рилса 13 (стандарт 24), образец —
рилс 17 (kit_rush.py).

Рисунок lib/l1_tired_scroll.png ×2 (.cache/anim/l1_tired_scroll_x2.png = src/f1.png, Real-ESRGAN + Lanczos); координаты
×2 сняты сеткой anim.grid 10.11. Слои: кот (тело с головой и уставшими глазами), лапа, которая листает, телефон с
держащей лапой, хвост (сеткой с физикой, tail_rig; дымок огонька едет с огоньком), три карточки ленты (каждая со своим
следом), дуги «свайпа» у пальца; маски глаз — для тяжёлого моргания веком в композиции. Подушка — фон.
Фон — над подушкой чистая бумага этого рисунка, ниже — подушка через anim.inpaint_bg; под лапой у тела — кусок шерсти
живота этого же рисунка."""
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
X2 = "l1_tired_scroll_x2.png"
ORIGIN = (960, 0)                 # левый верх сцены (композиции) в ×2
SIZE = (2112, 2048)
CAT_POLY = [(1388, 1120), (1430, 950), (1440, 760), (1520, 640), (1650, 570), (1800, 630), (1950, 590), (2100, 490),
            (2200, 440), (2265, 560), (2320, 800), (2380, 930), (2428, 960), (2428, 1150), (2330, 1200), (2290, 1226),
            (2241, 1240), (2241, 1350), (2236, 1385), (2184, 1545), (2186, 1564), (2362, 1564), (2402, 1600), (2408, 1700), (2345, 1855), (2100, 1845),
            (1980, 1865), (1700, 1865), (1560, 1800), (1545, 1640), (1480, 1600), (1465, 1370), (1388, 1360)]
TAIL_POLY = [(1005, 1102), (1386, 1102), (1386, 1380), (1255, 1440), (1335, 1565), (1455, 1592), (1525, 1612),
             (1575, 1640), (1575, 1752), (1005, 1752)]
TAIL_PIVOT = (1535, 1690)         # основание хвоста у тела
FLAME_BOX = (1225, 1095, 1305, 1175)
FLAME_SAT, FLAME_BRIGHT = 110, 140    # ядро огонька (рыжая шерсть макушки: насыщенность ~80, яркость ~130)
SMOKE_BOX = (1205, 840, 1320, 1112)
ARM_POLY = [(1880, 1360), (1960, 1315), (2050, 1283), (2120, 1250), (2195, 1255), (2244, 1281), (2249, 1337),
            (2200, 1350), (2170, 1347), (2167, 1400), (2127, 1430), (2070, 1426), (2000, 1445), (1930, 1455), (1880, 1427)]
ARM_PIVOT = (1895, 1405)          # плечо: ось взмаха пальца
ARM_BODY_X = 2212                 # левее — под лапой тело кота (заливается шерстью), правее — бумага у кончика пальца
UNDER_PHONE = 40                  # px: тело под телефоном
TUCK_BOX = (0, 0, 2290, 1550)     # где тело заходит под телефон (левый край телефона, выше его низа)
ARM_SEAM = (1885, 1935)           # у плеча лапа тает в тело (край слоя не ступенькой), под ней — сама лапа рисунка
PHONE_POLY = [(2296, 1232), (2520, 1214), (2532, 1280), (2472, 1420), (2470, 1560), (2425, 1582), (2330, 1578),
              (2186, 1576), (2184, 1545), (2242, 1385)]
PHONE_PIVOT = (2400, 1520)        # держащая лапа
PHONE_LOW = 1572                  # ниже — низ телефона кончился: светлое там — бумага у лапы
MARKS_BOX = (2212, 1222, 2300, 1338)
CARDS_BOX = (2430, 40, 2900, 1075)
STREAK_BOXES = [(2590, 350, 2735, 480), (2545, 695, 2690, 810), (2438, 1040, 2630, 1232)]
EYES = {"l": (1755, 1015, 2015, 1190), "r": (2115, 970, 2305, 1135)}
CUSHION_INK = (52, 48, 46)        # тушь контура подушки
PAPER_W = 950                     # левее — пустая бумага рисунка: ею заливается фон над подушкой
FUR_DY = 170                      # шерсть живота на 170 px ниже лапы — заплатка под лапой (левее — бумага)
SEAT = (1950, 1830)               # ось покачивания кота (сидит на подушке)
HEAD = (1950, 1000)


def cushion_top(x):
    """Задний край подушки за котом (по сетке: верх почти ровный y 1622 от x 1460, справа от 2300 опускается к 1637 у
    x 2385, где край снова виден; слева спускается к 1780 у x 1130 — там его закрывает хвост)."""
    x = np.asarray(x, np.float32)
    return np.where(x < 1460, 1622 + (1460 - x) * 158 / 330, 1622 + np.clip(x - 2300, 0, None) * 0.18)


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    ff = m.copy(); pad = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(np.uint8)


def region(shape, poly):
    reg = np.zeros(shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(poly)], 1)
    return reg


def box(shape, b):
    m = np.zeros(shape[:2], np.uint8); x0, y0, x1, y1 = b; m[y0:y1, x0:x1] = 1
    return m


def cat_mask(A):
    """Кот без хвоста: сверху — всё не бумага (шерсть, уши, глаза, усы); ниже 1600 — только тёмная шерсть и подушечки
    лап (подушка бежевая, её контур — тонкие линии вдали от шерсти: отбрасываются)."""
    reg = region(A.shape, CAT_POLY)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    up = ((g < 215) | (sat > 45)).astype(np.uint8)
    low = ((g < 150) | ((sat > 60) & (A[..., 0] > 150))).astype(np.uint8)
    low = cv2.morphologyEx(low, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    core = cv2.morphologyEx(low, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    low &= cv2.dilate(core, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    m = up.copy(); m[1600:] = low[1600:]
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) & reg
    return fill_holes(anim.keep_attached(m)) & reg


def tail_mask(A):
    reg = region(A.shape, TAIL_POLY)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    m = ((g < 170) | ((sat > 45) & (box(A.shape, FLAME_BOX) > 0))).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) & reg
    return anim.keep_attached(m)


def light_strokes(A, b, thr=236):
    """Светлые штрихи (дымок, след карточки, дуги свайпа) на бумаге в рамке."""
    g = A.mean(2)
    m = ((g < thr) & (box(A.shape, b) > 0)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    out = np.zeros_like(m)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 60:
            out[lab == i] = 1
    return out


def eye_mask(A, b):
    """Глаз изнутри: жёлто-зелёная радужка со зрачком (выпуклая оболочка зелёного), без линии века."""
    x0, y0, x1, y1 = b
    c = A[y0:y1, x0:x1]
    gr = ((c[..., 1] > c[..., 2] + 70) & (c[..., 1] > 150)).astype(np.uint8)        # жёлто-зелёная радужка
    n, lab, st, _ = cv2.connectedComponentsWithStats(gr)
    gr = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    hull = cv2.convexHull(cv2.findNonZero(gr))
    m = np.zeros_like(gr); cv2.fillConvexPoly(m, hull, 1)
    m = cv2.erode(m, np.ones((3, 3), np.uint8))
    ys, xs = np.where(m)
    bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    return m[by0:by1, bx0:bx1], (int(x0 + bx0), int(y0 + by0))


def main():
    os.makedirs(OUT, exist_ok=True)
    x2 = os.path.join(CACHE, X2)
    if not os.path.exists(x2):
        import upscale
        os.makedirs(CACHE, exist_ok=True)
        a = np.asarray(Image.open(os.path.join(REEL, "lib", "l1_tired_scroll.png")).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = np.asarray(Image.open(x2).convert("RGB")).astype(np.float32)

    cat = cat_mask(A)
    tail = tail_mask(A) & ~cat.astype(bool)
    full = (cat | tail).astype(np.uint8)
    tail, cat = anim.split_part(tail, cat)
    tail, cat, tail_fill = anim.claim_strokes(A, tail, cat)
    tail = anim.underlap(tail, cat, full, around=(*TAIL_PIVOT, 200))

    phone = (region(A.shape, PHONE_POLY) & (A.mean(2) < 238)).astype(np.uint8)
    phone = fill_holes(cv2.morphologyEx(phone, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))) & region(A.shape, PHONE_POLY)
    # бумага между низом телефона и лапой (её замкнула заливка дыр) — не телефон; блик рамки внутри — телефон
    paper = ((A.mean(2) > 236) & ((A.max(2) - A.min(2)) < 14) & (phone > 0)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(paper)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_TOP] + st[i, cv2.CC_STAT_HEIGHT] >= PHONE_LOW:
            phone[lab == i] = 0
    phone = anim.keep_attached(phone)
    cat = cat & ~phone.astype(bool)
    arm = (region(A.shape, ARM_POLY) & cat).astype(np.uint8)
    arm, rest = anim.split_part(arm, cat & ~arm.astype(bool))
    body = (cat | arm).astype(np.uint8)                    # тело целиком, под лапой — шерсть (залита ниже)
    arm = anim.underlap(arm, rest, body, around=(*ARM_PIVOT, 90))

    smoke = light_strokes(A, SMOKE_BOX, thr=238) & ~cv2.dilate(tail, np.ones((5, 5), np.uint8)).astype(bool)
    smoke = smoke.astype(np.uint8)
    marks = light_strokes(A, MARKS_BOX, thr=225) & ~cv2.dilate(arm | phone, np.ones((7, 7), np.uint8)).astype(bool)
    marks = marks.astype(np.uint8)
    away = cv2.dilate(full | phone, np.ones((15, 15), np.uint8)).astype(bool)
    cards = []
    for o in anim.ink_objects(A, box=CARDS_BOX, min_area=40000):
        o = (o.astype(bool) & ~away).astype(np.uint8)
        if o.sum() > 40000:
            cards.append(o)
    cards.sort(key=lambda o: np.argwhere(o)[:, 0].mean())                 # сверху вниз
    for i, sb in enumerate(STREAK_BOXES[:len(cards)]):
        st = light_strokes(A, sb, thr=238) & ~away & ~cv2.dilate(cards[i], np.ones((5, 5), np.uint8)).astype(bool)
        for j, o in enumerate(cards):
            if j != i:
                st &= ~cv2.dilate(o, np.ones((9, 9), np.uint8)).astype(bool)
        cards[i] = (cards[i] | st).astype(np.uint8)

    # фон: всё, что движется, снимается. Выше заднего края подушки — чистая бумага этого же рисунка (пустое поле слева,
    # отражённое): LaMa на дыре во всего кота (1,1 млн px) рисовала серый призрак кота. Верх подушки за котом — её же
    # тон с тенью к заднему краю и контур тушью (LaMa там мазала тёмной полосой, видной, когда кот подскакивает на
    # ударе — лист 10.11); шов между дорисованным и настоящим — anim.inpaint_bg узкой полосой.
    allm = (full | phone | smoke | marks).astype(np.uint8)
    for o in cards:
        allm |= o
    hole = cv2.dilate(allm, np.ones((13, 13), np.uint8)) > 0
    yy, xx = np.mgrid[:A.shape[0], :A.shape[1]]
    top = cushion_top(xx)
    above = hole & (yy < top)
    pa = A[:, :PAPER_W]
    paper = np.concatenate([pa if k % 2 == 0 else pa[:, ::-1] for k in range(-(-A.shape[1] // PAPER_W))], 1)[:, :A.shape[1]]
    seat = hole & ~above
    cush = (A.mean(2) > 175) & (A.mean(2) < 235) & ((A.max(2) - A.min(2)) < 40) & ~hole & (yy > 1640) & (yy < 1990)
    tone = np.median(A[cush], axis=0)
    grain = paper - cv2.GaussianBlur(paper, (0, 0), 4)
    depth = np.clip((yy - top) / 70.0, 0, 1)[..., None]                   # к заднему краю — тень складки
    surf = tone * (0.86 + 0.14 * depth) + grain
    ink = np.zeros(A.shape[:2], np.uint8)
    xs = np.arange(A.shape[1]); cv2.polylines(ink, [np.int32(np.stack([xs, cushion_top(xs)], 1))], False, 1, 5, cv2.LINE_AA)
    surf = np.where((ink > 0)[..., None], np.array(CUSHION_INK, np.float32), surf)
    bgA = np.where(above[..., None], paper, np.where(seat[..., None], surf, A))
    seam = (cv2.dilate(seat.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0) & ~cv2.erode(seat.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    seam &= yy > top + 6                                                  # контур края не трогать
    bg = anim.inpaint_bg(bgA, seam, cache_dir=CACHE, grow=False)
    # тело под листающей лапой: там шерсть — кусок шерсти живота ниже (тот же рисунок), а не заливка цветом
    under = cv2.dilate(arm, np.ones((9, 9), np.uint8)).astype(bool)
    under[:, ARM_BODY_X:] = False
    under[:, :ARM_SEAM[1]] = False                         # у плеча под лапой — она сама: шов не виден
    under &= cv2.erode(body, np.ones((9, 9), np.uint8)).astype(bool) | arm.astype(bool)
    fur = np.roll(A, -FUR_DY, axis=0)
    k = cv2.GaussianBlur(under.astype(np.float32), (0, 0), 3.0)[..., None]
    body_img = A * (1 - k) + fur * k
    finger = arm.astype(bool); finger[:, :ARM_BODY_X] = False      # за грудью палец висит над бумагой — его у тела нет
    body_mask = (body & ~finger).astype(np.uint8)
    # тело заходит под телефон на UNDER_PHONE px (шерстью бока): телефон вздрагивает, а между ним и котом не
    # должна светиться бумага (первый лист 10.11 — белая щель у нижнего угла телефона)
    reach = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * UNDER_PHONE + 1,) * 2)
    tuck = (cv2.dilate(body_mask, reach) > 0) & (phone > 0) & ~(body_mask > 0)
    tuck &= ~cv2.dilate(finger.astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)
    tuck[:, TUCK_BOX[2]:] = False; tuck[TUCK_BOX[3]:] = False         # только левый край телефона: под низом — бумага
    # цвет шерсти бока (медиана тёмного у края тела) с её же зерном: телефон открывает лишь щель в несколько px, а
    # сдвинутый кусок рисунка приносил туда рамку и экран телефона
    edge = (cv2.dilate(tuck.astype(np.uint8), reach) > 0) & (body_mask > 0) & (A.mean(2) < 120)
    grain = A.mean(2, keepdims=True) - cv2.GaussianBlur(A.mean(2), (0, 0), 6)[..., None]
    body_img[tuck] = np.median(A[edge], axis=0) + np.clip(np.roll(grain, -UNDER_PHONE * 3, axis=1)[tuck], -12, 12)
    body_mask = (body_mask | tuck).astype(np.uint8)

    Ap, bg, body_img = anim.paper_like(A), anim.paper_like(bg), anim.paper_like(body_img)
    Ap_tail = Ap
    if tail_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_tail = cv2.inpaint(u8, cv2.dilate(tail_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    layers = {}
    parts = [("tail", Ap_tail, tail, True), ("body", body_img, body_mask, True), ("arm", Ap, arm, True),
             ("phone", Ap, phone, True), ("smoke", Ap, smoke, False), ("marks", Ap, marks, False)]
    parts += [(f"card{i}", Ap, c, False) for i, c in enumerate(cards)]
    for name, img, m, keep in parts:
        anim.save_layer(OUT, name, img, m.astype(np.uint8), layers, keep_attached_=keep)
    fade_arm(layers["arm"]["xy"][0])
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    tx, ty = layers["tail"]["xy"]
    tail_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - ox - tx, TAIL_PIVOT[1] - oy - ty))
    merge_smoke(layers)
    # веки: маска глаза (белая, альфа — глаз) и цвет шерсти вокруг — композиция опускает по ней тяжёлое веко
    eyes = {}
    g = A.mean(2)
    for k, b in EYES.items():
        m, (ex, ey) = eye_mask(A, b)
        Image.fromarray(np.dstack([np.full(m.shape + (3,), 255, np.uint8), (m * 255).astype(np.uint8)])).save(
            os.path.join(OUT, f"eye_{k}.png"))
        ring = np.zeros(A.shape[:2], bool); ring[ey - 40:ey + m.shape[0] + 40, ex - 40:ex + m.shape[1] + 40] = True
        ring &= (g < 120) & (g > 45) & body.astype(bool)
        fur = np.median(Ap[ring], axis=0)
        eyes[k] = dict(xy=(ex - ox, ey - oy), wh=(int(m.shape[1]), int(m.shape[0])),
                       fur="#%02x%02x%02x" % tuple(int(round(c)) for c in fur))
    rel = lambda p: (p[0] - ox, p[1] - oy)      # noqa: E731
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, eyes=eyes, tail_pivot=rel(TAIL_PIVOT), arm_pivot=rel(ARM_PIVOT),
                phone_pivot=rel(PHONE_PIVOT), seat=rel(SEAT), head=rel(HEAD), cards=len(cards), fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


def fade_arm(x0):
    """Лапа у плеча тает в тело на ARM_SEAM: разрез поперёк шерсти встык давал ступеньку, когда палец листает."""
    p = os.path.join(OUT, "arm.png")
    im = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32)
    xs = np.arange(im.shape[1]) + x0
    im[..., 3] *= np.clip((xs - ARM_SEAM[0]) / (ARM_SEAM[1] - ARM_SEAM[0]), 0, 1)[None, :]
    Image.fromarray(im.clip(0, 255).astype(np.uint8)).save(p)


def tail_part(layer_png, attach, name="tail"):
    """tail_rig.prepare_part с порогом огонька строже: у этого хвоста верх шерсти тонирован оранжевым, и огоньком по
    умолчанию (насыщенность > 60, яркость > 120) считалась вся рыжая макушка — она срезалась с хвоста полосой."""
    rgba = np.asarray(Image.open(layer_png).convert("RGBA"))
    body, flame, fl = tail_rig.split_flame(rgba, sat_min=FLAME_SAT, bright_min=FLAME_BRIGHT)
    Image.fromarray(body).save(os.path.join(OUT, f"{name}_body.png"))
    if flame is not None:
        Image.fromarray(flame).save(os.path.join(OUT, f"{name}_flame.png"))
    mesh = tail_rig.build_mesh(body, attach)
    json.dump(dict(mesh, flame=fl), open(os.path.join(OUT, f"{name}_mesh.json"), "w"))


def merge_smoke(layers):
    """Дымок огонька едет с огоньком: дорисовывается в tail_flame.png (огонёк рисуется на кончике хвоста сеткой
    mesh_part.js), а не стоит отдельным слоем на месте, когда хвост машет."""
    mp = os.path.join(OUT, "tail_mesh.json"); mesh = json.load(open(mp))
    if not mesh.get("flame"):
        raise RuntimeError("tail_rig не нашёл огонёк — дымку не к чему приклеиться")
    fl = np.asarray(Image.open(os.path.join(OUT, "tail_flame.png")).convert("RGBA")).astype(np.float32)
    sm = np.asarray(Image.open(os.path.join(OUT, "smoke.png")).convert("RGBA")).astype(np.float32)
    tx, ty = layers["tail"]["xy"]; sx, sy = layers["smoke"]["xy"]
    fx, fy = mesh["flame"]["xy"]                                   # в системе слоя хвоста
    sx, sy = sx - tx, sy - ty
    x0, y0 = min(fx, sx), min(fy, sy)
    x1, y1 = max(fx + fl.shape[1], sx + sm.shape[1]), max(fy + fl.shape[0], sy + sm.shape[0])
    out = np.zeros((y1 - y0, x1 - x0, 4), np.float32)

    def over(dst, src, x, y):
        a = src[..., 3:] / 255; d = dst[y:y + src.shape[0], x:x + src.shape[1]]
        da = d[..., 3:] / 255; oa = a + da * (1 - a)
        rgb = (src[..., :3] * a + d[..., :3] * da * (1 - a)) / np.maximum(oa, 1e-6)
        d[..., :3] = rgb; d[..., 3:] = oa * 255

    over(out, sm, sx - x0, sy - y0)
    over(out, fl, fx - x0, fy - y0)
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(os.path.join(OUT, "tail_flame.png"))
    mesh["flame"]["xy"] = [int(x0), int(y0)]
    json.dump(mesh, open(mp, "w"))
    os.remove(os.path.join(OUT, "smoke.png")); layers.pop("smoke")


if __name__ == "__main__":
    main()
