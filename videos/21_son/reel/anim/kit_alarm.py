"""Слои хука рилса 21 «Ты спал 8 часов, а утром разбит?» для HyperFrames — по базе рилса 13 (стандарт 24), образец —
рилс 20 (kit_scroll.py) и рилс 17 (kit_rush.py).

Рисунок gen/s1_alarm.png ×2 (.cache/anim/s1_alarm_x2.png, Real-ESRGAN + Lanczos); координаты ×2 сняты сеткой anim.grid
11.11. Слои: голова кота (с усами, без правого уха), правое ухо (подёргивается), одеяло (кот тянет его на себя),
хвост (сеткой с физикой tail_rig; дымок огонька едет с огоньком), будильник (дребезжит и подпрыгивает), дуги звона у
будильника (мигают); маски глаз — для век в композиции. Подушка, изголовье, тумбочка — фон.
Фон: дыры большие (голова 0,6 млн px) — LaMa на них рисует призрак (урок рилса 20), поэтому под головой — чистая бумага
этого же рисунка (стена сверху) и тон изголовья с его линией, под будильником — стена этого же рисунка; anim.inpaint_bg —
только узкими швами по краю дыр, под хвостом и у ножек будильника на столешнице (там линии сцены надо продолжить)."""
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
X2 = "s1_alarm_x2.png"
ORIGIN = (0, 600)                 # левый верх сцены (композиции) в ×2
SIZE = (2048, 2080)
HEAD_POLY = [(255, 1265), (372, 1180), (372, 905), (560, 850), (800, 815), (960, 740), (1170, 680), (1262, 690),
             (1272, 1040), (1325, 1170), (1462, 1330), (1482, 1462), (1418, 1475), (1405, 1640), (255, 1640)]
EAR_POLY = [(928, 1040), (932, 1000), (952, 925), (1006, 838), (1066, 766), (1135, 690), (1180, 672), (1262, 700), (1268, 1085), (1205, 1112), (1090, 1080)]
EAR_PIVOT = (1150, 1085)          # основание правого уха
BLANKET_SEED = (800, 1850)
TAIL_POLY = [(285, 2010), (520, 1990), (660, 2040), (675, 2170), (680, 2620), (285, 2620)]
TAIL_PIVOT = (560, 2068)          # корень хвоста — середина его верха под складкой одеяла (у 470 правый край корня махал)
FLAME_BOX = (555, 2350, 625, 2440)
FLAME_SAT, FLAME_BRIGHT = 90, 140
SMOKE_BOX = (580, 2150, 680, 2395)
CLOCK_POLY = [(1650, 1395), (1678, 1372), (1735, 1335), (1858, 1335), (1915, 1375), (1940, 1395), (1945, 1480), (1932, 1620), (1905, 1690),
              (1685, 1690), (1660, 1620), (1652, 1480)]
CLOCK_FEET_Y = 1640               # ниже — столешница: у будильника там только обод циферблата и ножки
FACE = (1796, 1543, 131, 125)     # обод циферблата: центр и полуоси
CLOCK_PIVOT = (1795, 1672)        # между ножками на столешнице
TABLE_EDGE_Y = 1645               # задний край столешницы
BUZZ_BOXES = [(1605, 1310, 1688, 1400), (1918, 1325, 2000, 1415)]
FEET = [(1680, 1652, 1740, 1690), (1850, 1652, 1905, 1690)]   # ножки будильника на столешнице
EYES = {"l": (570, 1260, 840, 1440), "r": (935, 1255, 1210, 1440)}
HEADBOARD_Y = 894                 # верхний край изголовья за головой
PILLOW_Y = (1032, 1016)           # верхний край подушки у x 350 и 1300
INK = (88, 74, 66)                # тушь линий изголовья и подушки (замер по рисунку)
HEAD_TUCK = 70                    # px: голова заходит под одеяло (кот вздрагивает вверх — щели нет)
TAIL_TUCK = 15                    # мало: на хлёсте заход вылезал из-под складки плашкой; под складкой в фоне — тень
SEAT = (820, 1600)                # ось наклона головы — подбородок у одеяла
BLANKET_BASE_Y = 2200             # одеяло тянется вверх от своего нижнего края


def region(shape, poly):
    reg = np.zeros(shape[:2], np.uint8); cv2.fillPoly(reg, [np.int32(poly)], 1)
    return reg


def box(shape, b):
    m = np.zeros(shape[:2], np.uint8); x0, y0, x1, y1 = b; m[y0:y1, x0:x1] = 1
    return m


def fill_holes(m):
    m = (m > 0).astype(np.uint8)
    h, w = m.shape
    ff = m.copy(); pad = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 1)
    return (m | (1 - ff)).astype(np.uint8)


def blanket_mask(A):
    """Одеяло — связная светлая область, замкнутая тушью контура (сверху голова и подушка, снизу хвост и край)."""
    g = A.mean(2)
    ink = cv2.dilate((g < 140).astype(np.uint8), np.ones((5, 5), np.uint8))
    free = (1 - ink).astype(np.uint8)
    n, lab = cv2.connectedComponents(free)
    m = (lab == lab[BLANKET_SEED[1], BLANKET_SEED[0]]).astype(np.uint8)
    m = fill_holes(cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)))
    return cv2.dilate(m, np.ones((9, 9), np.uint8))           # контур одеяла — ему


def head_mask(A, blanket):
    reg = region(A.shape, HEAD_POLY)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    m = (((g < 150) | (sat > 45)) & (reg > 0) & (blanket == 0)).astype(np.uint8)
    # линия изголовья проходит сквозь кончики шерсти на макушке: из маски уходит только сама линия (столбцы, где над
    # и под полосой линии шерсти нет), кончики шерсти остаются голове (drop_scene_lines срезал их вместе с линией)
    y0, y1 = HEADBOARD_Y - 7, HEADBOARD_Y + 8
    near = m[y0 - 14:y0].any(0) | m[y1:y1 + 14].any(0)
    near = cv2.dilate(near.astype(np.uint8)[None], np.ones((1, 7), np.uint8))[0] > 0
    m[y0:y1, ~near] = 0
    core = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(core)
    core = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    core = fill_holes(cv2.morphologyEx(core, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)))
    return anim.keep_attached((m | core) & reg & (1 - blanket))


def tail_mask(A, blanket):
    """Хвост — вся тёмная шерсть в многоугольнике (с тонким клином у складки одеяла справа: раскрытие его срезало, и
    клин оставался в фоне тёмным обрывком), огонёк — по цвету; одеяло поверх корня хвоста закрывает его край."""
    reg = region(A.shape, TAIL_POLY)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    flame = (sat > FLAME_SAT) & (A.max(2) > FLAME_BRIGHT) & (box(A.shape, FLAME_BOX) > 0)
    m = ((g < 125) | flame).astype(np.uint8)
    m = anim.drop_scene_lines(A, cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) & reg)
    m = fill_holes(m) & reg
    # линии рамы кровати и края одеяла у хвоста — не хвост: всё дальше 11 px от тела хвоста (кончики шерсти ближе)
    core = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    m = (m & cv2.dilate(core, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23)))) | flame.astype(np.uint8)
    return anim.keep_attached(m)


def clock_mask(A):
    reg = region(A.shape, CLOCK_POLY)
    g = A.mean(2); sat = A.max(2) - A.min(2)
    m = ((g < 226) | (sat > 34)).astype(np.uint8) & reg
    m = fill_holes(cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))) & reg
    fb = np.zeros_like(reg)
    for b in FEET:
        fb |= box(A.shape, b)
    feet = cv2.morphologyEx(((g < 150) & (reg > 0) & (fb > 0)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    feet = fill_holes(feet)
    rim = np.zeros_like(m); cv2.ellipse(rim, FACE[:2], FACE[2:], 0, 0, 360, 1, -1)
    m[CLOCK_FEET_Y:] = (rim | feet)[CLOCK_FEET_Y:]
    return anim.keep_attached(m)


def light_strokes(A, b, thr=236, min_area=60, local=None):
    """Штрихи в рамке: темнее thr или (local) темнее своего окружения на local — дымок на сером борту кровати."""
    g = A.mean(2)
    dark = (g < thr) if local is None else (cv2.GaussianBlur(g, (0, 0), 10) - g > local)
    m = (dark & (box(A.shape, b) > 0)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    out = np.zeros_like(m)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= min_area:
            out[lab == i] = 1
    return out


def eye_mask(A, b):
    """Глаз изнутри: жёлто-зелёная радужка со зрачком (выпуклая оболочка зелёного), без линии века."""
    x0, y0, x1, y1 = b
    c = A[y0:y1, x0:x1]
    gr = ((c[..., 1] > c[..., 2] + 70) & (c[..., 1] > 150)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(gr)
    gr = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    hull = cv2.convexHull(cv2.findNonZero(gr))
    m = np.zeros_like(gr); cv2.fillConvexPoly(m, hull, 1)
    m = cv2.erode(m, np.ones((3, 3), np.uint8))
    ys, xs = np.where(m)
    bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    return m[by0:by1, bx0:bx1], (int(x0 + bx0), int(y0 + by0))


def tuck(A, part, under, reach, keep_from=None, src_dy=0):
    """Часть заходит под соседний слой на reach px: шерсть её тоном (медиана шерсти у края) с зерном рисунка. Только
    под телом части (столбцы, где над ней тело), а не вдоль усов: усы касаются края одеяла далеко от морды, и заход
    тянулся полосой через всю подушку (лист 11.11)."""
    core = cv2.morphologyEx(part, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    contact = (cv2.dilate(core, np.ones((9, 9), np.uint8)) > 0) & (under > 0)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * reach + 1,) * 2)
    add = (cv2.dilate(contact.astype(np.uint8), k) > 0) & (under > 0) & ~(part > 0)
    add &= cv2.dilate(core, np.ones((2 * reach + 41, 1), np.uint8)) > 0
    if keep_from is not None:
        add &= keep_from
    edge = (cv2.dilate(add.astype(np.uint8), np.ones((61, 61), np.uint8)) > 0) & (core > 0) & (A.mean(2) < 160) & (A.mean(2) > 60)
    # зерно шерсти — шумом (сдвинутый кусок рисунка приносил под ухо контур глаза, лист 11.11)
    nz = cv2.GaussianBlur(np.random.default_rng(5).normal(0, 1, A.shape[:2]).astype(np.float32), (0, 0), 1.2)
    img = A.copy()
    img[add] = np.median(A[edge], axis=0) + (6 * nz / (nz.std() + 1e-6))[add][:, None]
    if src_dy:          # шерсть самой части в src_dy px (сверху/снизу): заход виден на рывке — ровная заливка читалась плашкой
        src, ok = np.roll(A, src_dy, axis=0), np.roll(core, src_dy, axis=0) > 0
        take = add & ok
        img[take] = src[take]
    return img, (part | add).astype(np.uint8)


def background(A, head, ear, blanket, tail, clock, buzz, smoke):
    """Фон без движущихся частей. Дыры большие — LaMa на них рисует призрак (урок рилса 20, и тут первая проба: серый
    хвост на борту кровати), поэтому дыра заливается этим же рисунком: под головой — стена (сверху, где пусто) и
    тон изголовья с его линией, край подушки линией; под будильником — стена выше и тон столешницы с её краем и тенью;
    под хвостом — борт кровати и тень под ней в тех же строках правее (рама — одна горизонталь). anim.inpaint_bg —
    только узкий шов по краю дыр (дорисованное встык с настоящим)."""
    H, W = A.shape[:2]
    yy, xx = np.mgrid[:H, :W]
    above = lambda k: np.roll(A, k, axis=0)          # noqa: E731  строки на k px выше
    cat = (head | ear).astype(np.uint8)
    core = cv2.morphologyEx(cat, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    hole_head = (cv2.dilate(core, np.ones((17, 17), np.uint8)) > 0) | (cv2.dilate(cat, np.ones((7, 7), np.uint8)) > 0)
    hole_head &= ~(cv2.erode(blanket, np.ones((9, 9), np.uint8)) > 0)
    hole_clock = cv2.dilate((clock | buzz), np.ones((13, 13), np.uint8)) > 0
    hole_tail = (cv2.dilate(tail, np.ones((13, 13), np.uint8)) > 0) | (cv2.dilate(smoke, np.ones((25, 25), np.uint8)) > 0)
    hole_tail &= ~(cv2.erode(blanket, np.ones((9, 9), np.uint8)) > 0)
    wall_hi, wall_lo = above(300), above(1000)       # чистая стена: строки 400–600 и 20–640 (ухо — от 690)
    tile = A[100:612]                                 # зерно — с чистой стены, плиткой на весь лист (под хвостом
    paper = np.concatenate([tile] * (-(-H // len(tile))), 0)[:H]   # сдвиг на 1000 px приносил усы головы)
    grain = paper - cv2.GaussianBlur(paper, (0, 0), 4)
    pil_y = PILLOW_Y[0] + (xx - 350) * (PILLOW_Y[1] - PILLOW_Y[0]) / (1300 - 350)
    g = A.mean(2)

    def smooth(zone):
        # гладкое продолжение тона своей зоны (изголовье, подушка с серой тенью у головы) внутрь дыры, крупнее — шире
        valid = zone & ~hole_head & (g > 150)
        out = np.broadcast_to(np.median(A[valid], axis=0), A.shape).astype(np.float32)
        for sg in (150, 60, 25, 10):
            f, d = anim._nfill(A, valid, sg); out = np.where((d > 0.15)[..., None], f, out)
        return out + grain
    band = (yy > HEADBOARD_Y + 6) & (yy < pil_y - 6) & (xx > 175) & (xx < 1445)
    pillow = (yy > pil_y + 7) & (xx > 250) & (xx < 1395) & ~(blanket > 0)
    fill = np.where((yy < HEADBOARD_Y)[..., None], wall_hi, np.where((yy < pil_y)[..., None], smooth(band), smooth(pillow)))
    ink = np.zeros((H, W), np.uint8)
    cv2.line(ink, (160, HEADBOARD_Y), (1460, HEADBOARD_Y), 1, 5, cv2.LINE_AA)
    cv2.line(ink, (350, PILLOW_Y[0]), (1300, PILLOW_Y[1]), 1, 5, cv2.LINE_AA)
    fill = np.where((ink > 0)[..., None], np.array(INK, np.float32), fill)
    bgA = A.copy()
    bgA[hole_head] = fill[hole_head]
    lines = hole_head & (g < 120) & ~(cv2.dilate(cat, np.ones((5, 5), np.uint8)) > 0)   # линии сцены у кончиков усов
    bgA[lines] = A[lines]
    # будильник: стена на 700 px выше; столешница — её тон с зерном, задний край линией, мягкая тень под будильником
    top = A[TABLE_EDGE_Y + 8:TABLE_EDGE_Y + 48, 1602:1652].reshape(-1, 3)
    table = np.median(top, axis=0) + grain
    sh = np.zeros((H, W), np.float32); cv2.ellipse(sh, (1797, 1672), (125, 13), 0, 0, 360, 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 6)[..., None]
    table = table * (1 - 0.13 * sh)
    tl = np.zeros((H, W), np.uint8); cv2.line(tl, (1597, TABLE_EDGE_Y), (1953, TABLE_EDGE_Y + 1), 1, 5, cv2.LINE_AA)
    table = np.where((tl > 0)[..., None], np.array(INK, np.float32), table)
    clk = np.where((yy < TABLE_EDGE_Y - 3)[..., None], above(700), table)
    bgA[hole_clock] = clk[hole_clock]
    # хвост: те же строки на 500 px правее — борт кровати, рама и тень под кроватью
    side = np.roll(A, -500, axis=1)
    # у корня хвоста, под складкой одеяла — тень под одеялом (тон борта кровати сразу под краем одеяла), а не сдвинутое
    # одеяло соседних столбцов: там оно приносило светлые прямоугольники и обрывок края (лист 11.11)
    dark = np.clip((yy - 2030) / 95.0, 0, 1)[..., None]                  # под складкой темнее
    shade = np.median(A[2120:2140, 700:900].reshape(-1, 3), axis=0) * (0.5 + 0.42 * dark)
    side = np.where((yy < 2125)[..., None], shade + grain, side)
    bgA[hole_tail] = side[hole_tail]

    def seam(h, w=9):
        hu = h.astype(np.uint8)
        return (cv2.dilate(hu, np.ones((w, w), np.uint8)) > 0) & ~(cv2.erode(hu, np.ones((w, w), np.uint8)) > 0)
    ring = (seam(hole_head) | seam(hole_tail)) & ~(cv2.erode(blanket, np.ones((5, 5), np.uint8)) > 0)
    ring |= seam(hole_clock)
    ring &= ~(cv2.dilate(ink | tl | lines.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) | (yy > 2000)
    return anim.inpaint_bg(bgA, ring, cache_dir=CACHE, grow=False)


def main():
    os.makedirs(OUT, exist_ok=True)
    x2 = os.path.join(CACHE, X2)
    if not os.path.exists(x2):
        import upscale
        os.makedirs(CACHE, exist_ok=True)
        a = np.asarray(Image.open(os.path.join(REEL, "gen", "s1_alarm.png")).convert("RGB"))
        Image.fromarray(upscale.upscale(a, 2)).save(x2)
    A = np.asarray(Image.open(x2).convert("RGB")).astype(np.float32)

    blanket = blanket_mask(A)
    tail = tail_mask(A, blanket)
    low = np.zeros_like(blanket); low[2110:] = 1
    blanket &= (1 - tail) | (1 - low)                    # контур складки над корнем хвоста — одеялу (оно сверху)
    # ниже складки одеяла у хвоста — уже не одеяло: светлая кромка одеяла рядом с хвостом ложилась на него, когда он машет
    blanket &= (1 - (cv2.dilate(tail, np.ones((21, 21), np.uint8)) & low))
    head = head_mask(A, blanket)
    ear = (region(A.shape, EAR_POLY) & head).astype(np.uint8)
    ear, head = anim.split_part(ear, head & (1 - ear), core_open=5)
    full = (head | ear).astype(np.uint8)
    # claim_strokes здесь не нужен (усов у уха нет), а длинный тонкий контур уха он считал чужим усом и отдавал голове:
    # контур оставался стоять, когда ухо дёргалось (лист 11.11)
    ear_fill = np.zeros_like(ear)
    ear = anim.underlap(ear, head, full, width=30, around=(*EAR_PIVOT, 170))
    smoke = light_strokes(A, SMOKE_BOX, local=10) & ~cv2.dilate(tail, np.ones((5, 5), np.uint8)).astype(bool)
    smoke = anim.keep_attached(smoke.astype(np.uint8), reach=40)
    clock = clock_mask(A)
    buzz = np.zeros_like(clock)
    for b in BUZZ_BOXES:
        buzz |= light_strokes(A, b, thr=150)
    buzz &= (1 - cv2.dilate(clock, np.ones((5, 5), np.uint8)))

    bg = background(A, head, ear, blanket, tail, clock, buzz, smoke)
    # голова заходит под одеяло (вздрагивает вверх — под подбородком нет щели), хвост — под одеяло у основания
    head_img, head_m = tuck(A, head, blanket, HEAD_TUCK, keep_from=(np.mgrid[:A.shape[0], :A.shape[1]][1] > 380)
                            & (np.mgrid[:A.shape[0], :A.shape[1]][1] < 1290), src_dy=80)
    tail_img, tail_m = tuck(A, tail, blanket, TAIL_TUCK, src_dy=-(TAIL_TUCK + 20))
    # под основанием уха у головы — шерсть (ухо лежит поверх головы; дёрнулось — под ним мех, а не дыра в фон)
    base = ear.astype(bool) & (cv2.dilate(head, np.ones((181, 181), np.uint8)) > 0)
    head_img, head_m = tuck(head_img, head_m, base.astype(np.uint8), 90, src_dy=-110)

    Ap, bg = anim.paper_like(A), anim.paper_like(bg)
    head_img, tail_img = anim.paper_like(head_img), anim.paper_like(tail_img)
    if ear_fill.any():
        u8 = np.clip(Ap, 0, 255).astype(np.uint8)
        Ap_ear = cv2.inpaint(u8, cv2.dilate(ear_fill, np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA).astype(Ap.dtype)
    else:
        Ap_ear = Ap
    layers = {}
    parts = [("tail", tail_img, tail_m, True), ("blanket", Ap, blanket, True), ("head", head_img, head_m, True),
             ("ear", Ap_ear, ear, True), ("clock", Ap, clock, True), ("buzz", Ap, buzz, False), ("smoke", Ap, smoke, False)]
    for name, img, m, keep in parts:
        if name == "blanket":
            save_cloth(OUT, name, img, m.astype(np.uint8), layers)
        else:
            anim.save_layer(OUT, name, img, m.astype(np.uint8), layers, keep_attached_=keep)
    ox, oy = ORIGIN; w, h = SIZE
    Image.fromarray(np.clip(bg[oy:oy + h, ox:ox + w], 0, 255).astype(np.uint8)).save(os.path.join(OUT, "bg.png"))
    for v in layers.values():
        v["xy"] = (v["xy"][0] - ox, v["xy"][1] - oy)
    tx, ty = layers["tail"]["xy"]
    tail_part(os.path.join(OUT, "tail.png"), attach=(TAIL_PIVOT[0] - ox - tx, TAIL_PIVOT[1] - oy - ty))
    merge_smoke(layers)
    eyes = {}
    g = A.mean(2)
    for k, b in EYES.items():
        m, (ex, ey) = eye_mask(A, b)
        Image.fromarray(np.dstack([np.full(m.shape + (3,), 255, np.uint8), (m * 255).astype(np.uint8)])).save(
            os.path.join(OUT, f"eye_{k}.png"))
        ring = np.zeros(A.shape[:2], bool); ring[ey - 40:ey + m.shape[0] + 40, ex - 40:ex + m.shape[1] + 40] = True
        ring &= (g < 120) & (g > 45) & head.astype(bool)
        fur = np.median(Ap[ring], axis=0)
        # веко — шерсть над этим глазом (ровная заливка на крупном плане читалась серой плашкой): кусок рисунка над
        # линией века той же ширины, что веко (124 % глаза), опускается вместе с ним
        h, w = m.shape; lw = int(round(w * 1.24)); lx = ex - (lw - w) // 2
        lid = Ap[ey - 14 - h:ey - 14, lx:lx + lw]
        Image.fromarray(np.clip(lid, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f"lid_{k}.png"))
        eyes[k] = dict(xy=(ex - ox, ey - oy), wh=(int(m.shape[1]), int(m.shape[0])),
                       fur="#%02x%02x%02x" % tuple(int(round(c)) for c in fur))
    rel = lambda p: (p[0] - ox, p[1] - oy)      # noqa: E731
    meta = dict(origin=ORIGIN, size=SIZE, layers=layers, eyes=eyes, tail_pivot=rel(TAIL_PIVOT), ear_pivot=rel(EAR_PIVOT),
                clock_pivot=rel(CLOCK_PIVOT), seat=rel(SEAT), blanket_base=BLANKET_BASE_Y - oy, fps=30)
    json.dump(meta, open(os.path.join(OUT, "kit.json"), "w"), indent=1)
    print(json.dumps(meta))


def save_cloth(out_dir, name, img, mask, layers, soft=0.8):
    """anim.save_layer для светлой ткани: тот же край (мягкий, без бумажной каймы, проверка оторванных кусков), но без
    trim_paper_edge — он снимает светлые бесцветные пиксели у края маски, а одеяло само светлое и бесцветное: край
    одеяла выходил рваным, и в щели было видно, как под ним дёргаются голова и хвост (лист 11.11)."""
    m = anim.keep_attached(mask)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), soft)
    ys, xs = np.where(a > 0.02)
    x0, y0, x1, y1 = xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7
    im = np.dstack([np.asarray(img)[y0:y1, x0:x1], 255 * a[y0:y1, x0:x1]]).clip(0, 255).astype(np.uint8)
    al = im[..., 3].astype(np.float32) / 255
    paper = np.median(im[..., :3][al < 0.02], axis=0) if (al < 0.02).any() else (250, 247, 240)
    im[..., :3] = anim.defringe(im[..., :3], al, paper).round().astype(np.uint8)
    if anim.detached_share(al) >= 0.002:
        raise ValueError(f"слой {name}: оторванные куски ({anim.detached_share(al):.4f})")
    Image.fromarray(im).save(os.path.join(out_dir, name + ".png"))
    layers[name] = dict(xy=(int(x0), int(y0)), wh=im.shape[1::-1])


def split_flame(rgba):
    """tail_rig.split_flame, но огонёк — только его строки: общий шаг отдаёт огоньку всё над ним в его столбцах (у хвоста
    рилса 13 там пусто), а здесь прямо над огоньком висит корень хвоста — он уезжал с огоньком на кончик (лист 11.11)."""
    im = np.asarray(rgba, np.float32)
    rgb, a = im[..., :3], im[..., 3]
    fl = (((rgb.max(2) - rgb.min(2)) > FLAME_SAT) & (rgb.mean(2) > FLAME_BRIGHT) & (a > 30)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fl)
    if n <= 1:
        return np.asarray(rgba), None, None
    fl = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    ys, xs = np.where(fl)
    y_base = int(ys.max()); x0, x1 = int(xs.min()) - 12, int(xs.max()) + 12
    top = max(0, int(ys.min()) - 10)
    reg = np.zeros_like(fl); reg[top:max(top, y_base - 4), max(0, x0):x1] = 1
    m = cv2.GaussianBlur(((a > 8) & (reg > 0)).astype(np.float32), (0, 0), 1.0)
    tail = np.dstack([rgb, a * (1 - m)]).clip(0, 255).astype(np.uint8)
    flame = np.dstack([rgb, a * m]).clip(0, 255).astype(np.uint8)[top:y_base + 4, max(0, x0):x1]
    return tail, flame, dict(xy=[max(0, x0), top], base=[int((xs.min() + xs.max()) / 2), y_base])


def tail_part(layer_png, attach, name="tail"):
    rgba = np.asarray(Image.open(layer_png).convert("RGBA"))
    body, flame, fl = split_flame(rgba)
    Image.fromarray(body).save(os.path.join(OUT, f"{name}_body.png"))
    if flame is not None:
        Image.fromarray(flame).save(os.path.join(OUT, f"{name}_flame.png"))
    mesh = tail_rig.build_mesh(body, attach)
    json.dump(dict(mesh, flame=fl), open(os.path.join(OUT, f"{name}_mesh.json"), "w"))


def merge_smoke(layers):
    """Дымок огонька едет с огоньком: дорисовывается в tail_flame.png (как в рилсе 20)."""
    mp = os.path.join(OUT, "tail_mesh.json"); mesh = json.load(open(mp))
    if not mesh.get("flame"):
        raise RuntimeError("tail_rig не нашёл огонёк — дымку не к чему приклеиться")
    fl = np.asarray(Image.open(os.path.join(OUT, "tail_flame.png")).convert("RGBA")).astype(np.float32)
    sm = np.asarray(Image.open(os.path.join(OUT, "smoke.png")).convert("RGBA")).astype(np.float32)
    tx, ty = layers["tail"]["xy"]; sx, sy = layers["smoke"]["xy"]
    fx, fy = mesh["flame"]["xy"]
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
