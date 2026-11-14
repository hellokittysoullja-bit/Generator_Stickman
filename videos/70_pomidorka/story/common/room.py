"""Комната Димы рилса 70 «помидорка» (пишет группа C; берут все). Основа — common/room.py рилса 64 (63, 61, 62).

Подключение:  sys.path.insert(0, COMMON); import room as R   (COMMON = videos/70_pomidorka/story/common; lib рядом).
Мир кадра 1080×1920, камера снаружи (lib.cam(cx, cy, s)); мир шире кадра: x −1600…3400, y −600…2400.
Букв и цифр нигде нет: корешки книг пустые, картинка на стене — горы штрихом. Свет — плоскими пятнами с чёткой формой
(небольшой круг лампы под абажуром, днём — полоса солнца формы окна), без огромных мягких овалов.
Все функции возвращают строку SVG в мировых координатах (градиенты — динамические defs, вызывать после lib.dyn_begin()).

РЕЖИМЫ mode: "night"   (s01–s08, s12: лампа горит, окно тёмно-синее, луна, звёзды, дома с огнями; стена приглушённая)
             "evening" (вечер, s06 в начале: небо в закате — оранжево-розовое, дома силуэтом, лампа горит)
             "day"     (s13–s18: лампа выключена, окно голубое, полоса солнца формы окна на стене и полу)
             число 0…1 — переход вечер → ночь (s06: «за окном вечер → сумерки → ночь»): 0 — "evening", 1 — "night";
             цвета неба, стены и пола смешиваются, звёзды и луна проступают ко второй половине, огни в домах зажигаются.

СТОЛ — у ГОЛОЙ светлой стены (над столом ни окна, ни картин: окно в комнате высокое слева, полка справа за лампой).
Дима сидит СЛЕВА от стола в профиль-3/4 вправо (как 64), стол справа от него, на столе ноутбук экраном к Диме, лампа справа.
    desk_scene(t, mode, lamp_swing=0.0, chair_tilt=0.0, lamp_on=None, sit=None, bs=1.0, spot=False) -> dict:
        bg     — стена, высокое окно, картинка, полка, пол, ковёр (класть первым)
        chair_back / chair_seat — спинка стула (ДО Димы) и сиденье с ножками (после ног Димы, до тела)
        desk_top / desk_legs — столешница с царгой / ножки и тень. Порядок слоёв:
                 bg → chair_back → desk_top → pool → [Дима: legs] → desk_legs → chair_seat → [pelvis, arm_f, body] → предметы → [arm_n] → lamp
        desk   — desk_legs + desk_top одной строкой (если Димы нет)
        pool   — небольшой круг света лампы на столешнице (после desk_top, до предметов); днём пусто
        lamp   — лампа (после предметов)
        spot=True — пятнышко-трещинка на стене над столом (WALL_SPOT), то же, что в wall_view
    FL=1560 пол, WALL_Y=1440 низ стены, DESK_TOP=960 передняя кромка столешницы, DESK_D=120 глубина верха
    DESK_X=(560, 1340) столешница: предметы — дном на y ∈ [DESK_TOP − DESK_D + 10, DESK_TOP − 6] (ниже — ближе)
    LAPTOP=(830, DESK_TOP − 40)  дно ноутбука (центр), экран смотрит ВЛЕВО на Диму
    TIMER_DESK=(640, DESK_TOP − 26)  где таймер стоит на столе у ноутбука, ближе к Диме
    MUG_DESK=(1180, DESK_TOP − 70)  кружка у лампы (s06: «прибавилась пустая кружка»)
    LAMP=(1200, DESK_TOP − 60)  дно лампы; круг света LAMP_POOL — небольшой, чёткий край, левее лампы
    SIT=(330, seat_y(1.0))  таз сидящего Димы (bs=1.0); ступни на FL на x≈SIT+300
    CAT_DESK=(1040, DESK_TOP − 40) — кот на столе (лапы на линии), CAT_FLOOR=(1420, FL − 6) — кот на полу
    WALL_SPOT=(960, 520) пятнышко на стене над столом
    CLEAN_WALL=(700, 160, 1320, 600) — ЧИСТАЯ стена над столом (s17, рукописное «кот»): ни предметов, ни теней, ни солнца
    камеры (cx, cy, s) для lib.cam:
        CAM_DESK_CLOSE=(628, 800, 2.35)  «стол крупно» — ОДИН ракурс s01 и s18 (петля): лицо Димы, его руки с таймером над
                                         краем стола, край ноутбука; таймер держать около HOLD=(722, 745)
        CAM_SIDE_MID=(700, 1000, 1.18)   средний план сбоку (s04): Дима на стуле до колен, стол, ноутбук, лампа
        CAM_DAY_WIDE=(760, 1020, 0.86)   общий план днём (s16): Дима за столом целиком, кот на столе, окно, полка
        CAM_CLEAN=(900, 640, 1.2)        Дима, кот на столе и чистая стена над ними (s17)

ЧЕРЕЗ ПЛЕЧО НА СТЕНУ (s05) — отдельная композиция в координатах кадра 1080×1920 (камера по умолчанию CAM_SHOULDER):
    wall_view(t, mode="night", tl=0.0, spot=1.0) -> dict(bg, desk, lamp, chair, pool)
        bg   — голая стена во весь кадр, край высокого окна слева, полоса лунного света формы окна (tl 0…1 — ускоренное время:
               полоса ползёт слева направо и вытягивается, стена темнеет), пятнышко-трещинка WALL_SPOT_V (spot — сила 0…1)
        desk — столешница сверху-сзади (край к зрителю внизу) — класть после bg; ноутбук (экраном к нам, мы за Димой) и таймер
               ставит сцена: LAPTOP_V, TIMER_V
        pool — круг света лампы на столешнице (после desk); lamp — лампа справа (после предметов)
        chair(squash=0, bounce=0) — спинка стула СЗАДИ: класть ПОСЛЕ тела Димы (мы смотрим из-за спинки), голова и плечи выше неё;
               squash — стул пружинит (сиденье проседает, спинка качается)
    Дима со спины — из people.py (группа B), плечи и затылок на переднем плане: DIMA_V=(430, 1640) — середина плеч, рост головы ~ 300 px.
    CAM_SHOULDER=(540, 960, 1.0); наезд на стену — к WALL_SPOT_V, без рывков.

КОРИДОР (s12) — hall_scene(t, mode="night") -> dict(bg, front): стена коридора (другого цвета), плинтус, пол, вешалка с курткой
    слева, коврик; место двери — HALL_DOOR=(600, FL, 330, 820) (центр x, пол, ширина, высота): дверь из props ставит сцена, здесь —
    только наличник (рама) и тень на полу; front — пусто. Свет — плафон сверху (небольшой круг с чёткой формой).
    CAM_HALL=(600, 1080, 1.0).
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
from lib import INK, blob, ellipse_pts, f, line, rect_pts, shape  # noqa: E402

# ─────────────── общие размеры ───────────────
FL = 1560.0
WALL_Y = 1440.0
DESK_TOP = 960.0
DESK_D = 120.0
DESK_TH = 36.0
DESK_X = (560.0, 1340.0)
DRAWER = (760.0, 1090.0, DESK_TOP + DESK_TH, DESK_TOP + DESK_TH + 90.0)
LAMP = (1200.0, DESK_TOP - 60.0)
LAMP_POOL = (1100.0, DESK_TOP - 52.0, 120.0, 28.0)
LAPTOP = (830.0, DESK_TOP - 40.0)
TIMER_DESK = (640.0, DESK_TOP - 26.0)
MUG_DESK = (1180.0, DESK_TOP - 70.0)
CAT_DESK = (1040.0, DESK_TOP - 40.0)
CAT_FLOOR = (1420.0, FL - 6.0)
WALL_SPOT = (960.0, 520.0)
CLEAN_WALL = (700.0, 160.0, 1320.0, 600.0)
HOLD = (722.0, 745.0)
CAM_DESK_CLOSE = (628.0, 800.0, 2.35)
CAM_SIDE_MID = (700.0, 1000.0, 1.18)
CAM_DAY_WIDE = (760.0, 1020.0, 0.86)
CAM_CLEAN = (900.0, 640.0, 1.2)
CAM_DESK_MID = CAM_SIDE_MID
# через плечо (координаты кадра)
WALL_SPOT_V = (600.0, 610.0)
LAPTOP_V = (540.0, 1180.0)
TIMER_V = (790.0, 1205.0)
DIMA_V = (430.0, 1640.0)
CAM_SHOULDER = (540.0, 960.0, 1.0)
# коридор
HALL_DOOR = (600.0, FL, 330.0, 820.0)
CAM_HALL = (600.0, 1080.0, 1.0)
# окно в полный рост
WIN_TALL = (-700.0, 150.0, -120.0, 1150.0)
STAND = (-240.0, FL)
CAM_WIN = (-330.0, 900.0, 0.95)
# диван
SOFA = (2250.0, FL, 1.2)
SOFA_SEAT = 1190.0
ARM_TOP = (2676.0, 1008.0)
SOFA_CLEAN_WALL = (2420.0, 260.0, 3000.0, 680.0)
CAM_SOFA = (2330.0, 1000.0, 1.0)


def seat_y(bs=1.0):
    """Таз сидящего на стуле Димы масштаба bs: ступни на FL (голень 300, бедро горизонтально) — как в 61."""
    return FL - 392.0 * bs


def sofa_hip(bs=1.0):
    """Таз Димы, сидящего на подушке дивана (сиденье ниже стула: колени выше таза)."""
    return SOFA_SEAT - 10.0 * bs


SIT = (330.0, seat_y(1.0))
SOFA_DIMA = (2120.0, sofa_hip(1.0))

WOOD, WOOD_SH, WOOD_HI = "#b27c4c", "#8a5b32", "#ce9a68"
DESKW, DESKW_SH, DESKW_HI = "#c48a52", "#94633a", "#dcaa72"

MODES = {
    "night": dict(wall="#7e7aa0", wall_hi="#958fb2", wall_sh="#625e84", wall_ln="#6d6990", base="#a7a2c0", base_sh="#837ea3",
                    floor="#7a5236", floor_b="#5e3e28", floor_ln="#43291a", rug=("#a8503f", "#d8a45a", "#3f6f7a"), shelf=WOOD_SH,
                    sky=("#141a3c", "#26306a", "#4a4f8c"), shadow="#2a2440", shade_k=(.86, .86, .9)),
    "evening": dict(wall="#a8949a", wall_hi="#bba7a8", wall_sh="#8a7682", wall_ln="#9a868e", base="#c8b8b6", base_sh="#a2908f",
                    floor="#8c5c3a", floor_b="#6c462c", floor_ln="#4c301c", rug=("#b8583f", "#e0aa5c", "#46767c"), shelf=WOOD_SH,
                    sky=("#3b4c8c", "#c97a8a", "#f2a86e"), shadow="#3a2a3a", shade_k=(.94, .9, .92)),
    "day": dict(wall="#e6dcc0", wall_hi="#f1e9d2", wall_sh="#d2c6a6", wall_ln="#d8cdb0", base="#f4eedf", base_sh="#d6ccb4",
                floor="#c8915c", floor_b="#b07a48", floor_ln="#8a5b34", rug=("#c8634a", "#efc77a", "#4f8a8b"), shelf=WOOD,
                sky=("#6fb2ec", "#acd8f5", "#e6f4fb"), shadow="#6e4a2c", shade_k=(1, 1, 1)),
}


def rs(*k):
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return np.random.RandomState(h % (2 ** 31))


def _phase(mode):
    """Доля ночи 0…1 для режимов с лампой; None — день."""
    if isinstance(mode, (int, float)):
        return clamp01(float(mode))
    return {"night": 1.0, "evening": 0.0}.get(mode)


def clamp01(x):
    return max(0.0, min(1.0, x))


def smooth01(u):
    u = clamp01(u)
    return u * u * (3 - 2 * u)


def is_dark(mode):
    return _phase(mode) is not None


def _M(mode):
    """Палитра режима; число — смесь вечер → ночь (цвета, кортежи цветов и множители)."""
    p = _phase(mode)
    if p is None:
        return MODES["day"]
    if p in (0.0, 1.0):
        return MODES["night" if p == 1.0 else "evening"]
    a, b = MODES["evening"], MODES["night"]
    out = {}
    for k, v in a.items():
        w = b[k]
        if isinstance(v, str):
            out[k] = lib.mix(v, w, p)
        elif isinstance(v[0], str):
            out[k] = tuple(lib.mix(x, y, p) for x, y in zip(v, w))
        else:
            out[k] = tuple(x + (y - x) * p for x, y in zip(v, w))
    return out


# ═════════════════════════ стена и пол ═════════════════════════
def wall_floor(mode="night"):
    """Стена (крашеная, лёгкие вертикальные полосы обоев), плинтус, пол-доски. Тянется на весь мир."""
    M = _M(mode)
    o = []
    g = lib.lin_grad([(0, M["wall_sh"], 1), (.35, M["wall"], 1), (1, M["wall_hi"], 1)], 0, -600, 0, WALL_Y, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="-600" width="5000" height="{f(WALL_Y + 600)}" fill="url(#{g})"/>')
    for i in range(-16, 34):
        x = i * 140.0
        o.append(line([(x, -600), (x + 1.5, WALL_Y - 40)], w=1.8, color=M["wall_ln"], taper=0.0, wmin=1, seed=40 + i, op=.55))
    o.append(shape(rect_pts(-1600, WALL_Y - 46, 3400, WALL_Y + 6), M["base"], blob(rect_pts(-1600, WALL_Y - 8, 3400, WALL_Y + 6), M["base_sh"]),
                   w=3.4, seed=70))
    gf = lib.lin_grad([(0, M["floor"], 1), (1, M["floor_b"], 1)], 0, WALL_Y, 0, 2400, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="{f(WALL_Y + 6)}" width="5000" height="{f(2400 - WALL_Y)}" fill="url(#{gf})"/>')
    ys = [WALL_Y + 6, 1500, 1580, 1680, 1810, 1970, 2170, 2400]
    for k, y in enumerate(ys[1:-1]):
        o.append(line([(-1600, y), (3400, y)], w=3.0, color=M["floor_ln"], taper=0.0, wmin=1, seed=80 + k, op=.6))
    r = rs(5)
    for k, (ya, yb) in enumerate(zip(ys[:-1], ys[1:])):
        for j in range(9):
            x = r.uniform(-1500, 3300)
            o.append(line([(x, ya), (x + r.uniform(-4, 4), yb)], w=2.4, color=M["floor_ln"], taper=0.0, wmin=1, seed=90 + k * 11 + j, op=.5))
    return "".join(o)


def rug(cx, cy, rx, ry, mode="night", seed=0):
    """Круглый полосатый коврик на полу (вид чуть сверху)."""
    M = _M(mode)
    c0, c1, c2 = M["rug"]
    inner = ""
    for sc, col in ((.8, c1), (.6, c0), (.4, c1), (.22, c2)):
        inner += shape(ellipse_pts(cx, cy, rx * sc, ry * sc, 26), col, ink=False)
    return blob(ellipse_pts(cx + 6, cy + 12, rx + 4, ry + 4, 30), M["shadow"], .25) + shape(ellipse_pts(cx, cy, rx, ry, 34), c0, inner, w=3.8, seed=120 + seed)


# ═════════════════════════ окно ═════════════════════════
def _tree(x, y, h, sway, t, seed, col="#5f9a52", sh="#477a3c", trunk="#6e4a2c"):
    """Дерево за окном: ствол и пушистая крона, крона качается (sway)."""
    a = .04 * sway * math.sin(t * 1.9 + seed) + .015 * sway * math.sin(t * 4.3 + seed * 2)
    tx, ty = x + math.sin(a) * h * .9, y - math.cos(a) * h * .9
    o = line([(x, y), ((x + tx) / 2, (y + ty) / 2 + 6), (tx, ty)], 16 * h / 300, trunk, taper=.5, wmin=.4, seed=seed)
    pts = []
    for i in range(14):
        th = 2 * math.pi * i / 14
        rr = h * (.36 + .05 * math.sin(i * 2.7 + seed))
        pts.append((tx + math.cos(th) * rr * 1.05, ty - h * .12 + math.sin(th) * rr * .9))
    inner = blob([(tx + p[0] * .0 + (p[0] - tx) * .55 + h * .1, p[1] + h * .1) for p in pts], sh, .9)
    return o + shape(pts, col, inner, w=3.0, seed=seed + 1)


def window(x0, y0, x1, y1, mode, t=0.0, seed=0, sway=0.6, curtain="#c96f4a", sill=True):
    """Окно с рамой, крестовиной, подоконником и шторами. Вечер — тёмно-синее небо, луна, звёзды-штрихи, силуэты домов с огнями
    окон (тёплые квадраты без всяких знаков); день — голубое небо, облака плывут от t, деревья качаются (sway)."""
    M = _M(mode)
    sd = 7300 + seed
    fr = 18
    ix0, iy0, ix1, iy1 = x0 + fr, y0 + fr, x1 - fr, y1 - fr
    w, h = ix1 - ix0, iy1 - iy0
    sky = M["sky"]
    g = lib.lin_grad([(0, sky[0], 1), (.6, sky[1], 1), (1, sky[2], 1)], 0, 0, 0, 1)
    inner = f'<path d="M{f(ix0 - 5)} {f(iy0 - 5)}H{f(ix1 + 5)}V{f(iy1 + 5)}H{f(ix0 - 5)}Z" fill="url(#{g})"/>'
    r = rs(sd)
    p = _phase(mode)
    if p is not None:
        if p < 1.0:     # закатное солнце садится за дома
            su = 1 - p
            sx_, sy_ = ix0 + w * .34, iy1 - h * .3 + h * .22 * p
            inner += f'<g opacity="{su:.3f}">' + shape(ellipse_pts(sx_, sy_, w * .11, w * .11, 22), "#ffd27a", "", w=2.4, seed=sd + 60) + "</g>"
        st = smooth01((p - .35) / .6)
        for i in range(9):
            if st <= .01:
                break
            sx = ix0 + 24 + r.uniform(0, w - 48)
            sy = iy0 + 20 + r.uniform(0, h * .42)
            tw = (.55 + .45 * math.sin(t * 2.4 + i * 1.7)) * st
            L = 7 + (i % 3) * 2
            inner += line([(sx - L, sy), (sx + L, sy)], 2.6, "#f6efc8", taper=.5, wmin=.3, seed=sd + 10 + i, op=tw)
            inner += line([(sx, sy - L), (sx, sy + L)], 2.6, "#f6efc8", taper=.5, wmin=.3, seed=sd + 30 + i, op=tw)
        mo = smooth01((p - .4) / .5)
        if mo > .01:
            mx, my, mr = ix1 - w * .28, iy0 + h * .2, max(24.0, w * .1)
            inner += (f'<g opacity="{mo:.3f}">' + shape(ellipse_pts(mx, my, mr, mr, 22), "#fbf1c8",
                                                        blob(ellipse_pts(mx + mr * .5, my - mr * .1, mr * .85, mr * .95, 18), sky[1]), w=2.6, seed=sd + 70)
                      + "</g>")
        # дома: силуэты, огни окон зажигаются по одному к ночи
        hb = iy1 - h * .3
        hc = lib.mix("#5a3a5e", "#1b2146", p)
        rl = rs(sd + 5)
        for j in range(5):
            bx0 = ix0 - 10 + j * w / 4.2
            bx1 = bx0 + w / 4.6
            by = hb + (j % 3) * h * .06
            inner += blob(rect_pts(bx0, by, bx1, iy1 + 8), hc)
            for a_ in range(2):
                for b_ in range(3):
                    thr = rl.uniform(-.2, .85)
                    if (a_ + b_ + j) % 3 == 0 or p < thr:
                        continue
                    wx = bx0 + 14 + a_ * (bx1 - bx0 - 28) * .55
                    wy = by + 16 + b_ * 34
                    if wy + 18 < iy1:
                        inner += blob(rect_pts(wx, wy, wx + 16, wy + 18), "#f2c66a")
    else:
        inner += shape(ellipse_pts(ix0 + w * .26, iy0 + h * .2, w * .09, w * .09, 20), "#fff0a8", "", w=2.4, seed=sd + 41)
        for j in range(3):
            cx = ix0 + ((j * 173 + t * 14 + sd) % (w + 160)) - 80
            cy = iy0 + h * (.15 + .14 * j)
            cw = w * (.3 + .06 * (j % 2))
            pts = [(cx - cw / 2, cy + 12)] + [(cx - cw / 2 + cw * i / 5, cy - 14 - 14 * math.sin(i * 1.9 + j)) for i in range(6)] + [(cx + cw / 2, cy + 12)]
            inner += blob(pts, "#ffffff")
        hh = h * .55
        inner += _tree(ix0 + w * .2, iy1 + 30, hh, sway, t, sd + 80)
        inner += _tree(ix0 + w * .78, iy1 + 30, hh * .82, sway, t, sd + 90, col="#6faa5c", sh="#548a44")
        inner += blob([(ix0 - 5, iy1 + 5, 1), (ix0 - 5, iy1 - h * .06), (ix1 + 5, iy1 - h * .09), (ix1 + 5, iy1 + 5, 1)], "#7fae5e")
    frame = "#efe7d6" if not is_dark(mode) else lib.mix("#d8c6c6", "#c9c2d8", _phase(mode))
    out = [shape(rect_pts(x0, y0, x1, y1), frame, "", w=4.4, seed=sd)]
    out.append(shape(rect_pts(ix0, iy0, ix1, iy1), sky[1], inner, w=3.4, seed=sd + 1))
    xm, ym = (x0 + x1) / 2, iy0 + h * .42
    out.append(blob(rect_pts(xm - 7, iy0, xm + 7, iy1), frame) + line([(xm - 7, iy0), (xm - 7, iy1)], 2.6, INK, seed=sd + 2)
               + line([(xm + 7, iy0), (xm + 7, iy1)], 2.6, INK, seed=sd + 3))
    out.append(blob(rect_pts(ix0, ym - 7, ix1, ym + 7), frame) + line([(ix0, ym - 7), (ix1, ym - 7)], 2.6, INK, seed=sd + 4)
               + line([(ix0, ym + 7), (ix1, ym + 7)], 2.6, INK, seed=sd + 5))
    if sill:
        out.append(shape(lib.rrect(x0 - 30, y1, x1 + 30, y1 + 24, 5), lib.mul(frame, (.95, .95, .95)),
                         blob(rect_pts(x0 - 34, y1 + 13, x1 + 34, y1 + 28), lib.mul(frame, (.8, .8, .82))), w=3.4, seed=sd + 6))
    if curtain:
        cur = curtain if not is_dark(mode) else lib.mul(curtain, M["shade_k"]) if _phase(mode) < 1 else lib.mul(curtain, (.72, .66, .8))
        sw = 3.0 * math.sin(t * .8 + seed)
        for sgn, cx in ((-1, x0 - 4), (1, x1 + 4)):
            pts = [(cx - sgn * 6, y0 - 26, 1), (cx + sgn * 78, y0 - 18), (cx + sgn * (66 + sw), y0 * .4 + y1 * .6), (cx + sgn * 86, y1 + 40, 1),
                   (cx - sgn * 8, y1 + 40, 1)]
            fold = line([(cx + sgn * 30, y0), (cx + sgn * (40 + sw * .5), y1 + 30)], 5, lib.mul(cur, (.78, .78, .78)), taper=.4, wmin=.3,
                        seed=sd + 8 + int(sgn + 1))
            out.append(shape(pts, cur, fold, w=3.4, seed=sd + 9 + int(sgn + 1)))
        out.append(shape(lib.rrect(x0 - 50, y0 - 40, x1 + 50, y0 - 24, 6), WOOD_SH, "", w=3.0, seed=sd + 14))
    return "".join(out)


def _sun_quad(A, U, V, col, col2, inset=.06):
    """Полоса солнца формы окна: четыре стекла (A — угол, U вдоль ширины, V вдоль высоты), крестовина — тень, чёткие края."""
    A, U, V = np.array(A, float), np.array(U, float), np.array(V, float)
    o = []
    for (u0, u1) in ((0.0, .47), (.53, 1.0)):
        for (v0, v1) in ((0.0, .4), (.47, 1.0)):
            pts = [tuple(A + U * u0 + V * v0) + (1,), tuple(A + U * u1 + V * v0) + (1,), tuple(A + U * u1 + V * v1) + (1,), tuple(A + U * u0 + V * v1) + (1,)]
            o.append(blob(pts, col))
            q = [tuple(A + U * (u0 + .03) + V * (v0 + inset)) + (1,), tuple(A + U * (u1 - .03) + V * (v0 + inset)) + (1,),
                 tuple(A + U * (u1 - .03) + V * (v0 + inset + .1)) + (1,), tuple(A + U * (u0 + .03) + V * (v0 + inset + .1)) + (1,)]
            o.append(blob(q, col2))
    return "".join(o)


def sun_patches(mode):
    """Днём: полоса солнца формы высокого окна на стене справа от него (за Димой у стола) и пятно на полу. Вечером пусто."""
    if is_dark(mode):
        return ""
    o = _sun_quad((-40, 260), (330, 40), (60, 760), "#f6e7bf", "#fbf0d2", inset=.05)
    o += _sun_quad((-560, 1475), (520, -10), (300, 80), "#d9a66e", "#e2b37c", inset=.08)
    return o


# ═════════════════════════ мебель у стола ═════════════════════════
def shelf(x0, x1, y, mode="night", seed=0, books=True, plant=True, t=0.0):
    """Полка на стене: доска на кронштейнах, книги с ПУСТЫМИ корешками (цветные полосы), горшок с растением."""
    M = _M(mode)
    k = M["shade_k"]
    o = []
    if books:
        r = rs(300 + seed)
        x = x0 + 30
        cols = ["#c8553d", "#4f8a8b", "#e0b04a", "#5a6fb0", "#8a5b9a", "#6aa36a", "#d98a4a"]
        for i in range(7):
            bw = r.uniform(26, 42)
            bh = r.uniform(110, 150)
            lean = -10.0 if i == 6 else 0.0
            c = lib.mul(cols[i % len(cols)], k)
            pts = [(x, y, 1), (x + bw, y, 1), (x + bw + lean * .0, y - bh, 1), (x + lean, y - bh, 1)]
            if lean:
                pts = lib.T([(x, y, 1), (x + bw, y, 1), (x + bw, y - bh, 1), (x, y - bh, 1)], 0, 0, 1, 14, x + bw, y)
            o.append(shape(pts, c, blob(rect_pts(x + bw - 8, y - bh - 4, x + bw + 4, y + 4), lib.mul(c, (.78, .78, .78))) +
                           line([(x + 5, y - bh * .78), (x + bw - 5, y - bh * .78)], 2.6, lib.mul(c, (.7, .7, .7)), taper=0, wmin=1, seed=330 + i),
                           w=3.0, seed=310 + i + seed))
            x += bw + 3
    if plant:
        px = x1 - 80
        ph = 0.04 * math.sin(t * 1.3)
        leaves = ""
        for i, a in enumerate((-60, -30, -5, 20, 45, 70)):
            aa = math.radians(a - 90 + 6 * math.sin(t * 1.3 + i))
            L = 95 + 18 * (i % 2)
            tip = (px + math.cos(aa) * L, y - 72 + math.sin(aa) * L)
            mid = (px + math.cos(aa) * L * .5 + math.cos(aa + 1.5) * 16, y - 72 + math.sin(aa) * L * .5 + math.sin(aa + 1.5) * 16)
            mid2 = (px + math.cos(aa) * L * .5 - math.cos(aa + 1.5) * 16, y - 72 + math.sin(aa) * L * .5 - math.sin(aa + 1.5) * 16)
            leaves += shape([(px, y - 72, 1), mid, tip + (1,), mid2], lib.mul("#6aa35a", k), line([(px, y - 72), tip], 2.0, lib.mul("#4a7f3c", k),
                                                                                               seed=360 + i), w=2.8, seed=350 + i)
        del ph
        o.append(leaves)
        o.append(shape([(px - 52, y - 84, 1), (px + 52, y - 84, 1), (px + 40, y, 1), (px - 40, y, 1)], lib.mul("#d0704a", k),
                       blob(rect_pts(px - 60, y - 84, px + 60, y - 66), lib.mul("#a8553a", k)), w=3.2, seed=340 + seed))
    o.append(shape(rect_pts(x0, y, x1, y + 20), M["shelf"], blob(rect_pts(x0, y + 12, x1, y + 20), WOOD_SH), w=3.4, seed=320 + seed))
    for bx in (x0 + 50, x1 - 50):
        o.append(shape([(bx - 8, y + 20, 1), (bx + 8, y + 20, 1), (bx + 8, y + 64, 1), (bx - 8, y + 30, 1)], "#555a66", "", w=2.4, seed=325 + int(bx) % 7))
    return "".join(o)


def wall_picture(cx, cy, w, h, mode="night", seed=0):
    """Картинка в рамке без букв: горы и солнце штрихом."""
    k = _M(mode)["shade_k"]
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    inner = blob(rect_pts(x0, y0, x1, y1), lib.mul("#f4ead2", k))
    inner += blob([(x0, y1, 1), (x0 + w * .3, y0 + h * .35, 1), (x0 + w * .5, y0 + h * .6, 1), (x0 + w * .72, y0 + h * .3, 1), (x1, y1, 1)],
                  lib.mul("#7fa4b8", k))
    inner += blob(ellipse_pts(x0 + w * .78, y0 + h * .22, w * .08, w * .08, 14), lib.mul("#f2b65a", k))
    return shape(rect_pts(x0 - 14, y0 - 14, x1 + 14, y1 + 14), lib.mul(WOOD_SH, k), "", w=3.2, seed=400 + seed) + shape(rect_pts(x0, y0, x1, y1), "#f4ead2", inner,
                                                                                                                     w=2.6, seed=401 + seed)


def chair(x, sy, k=1.0, tilt=0.0, mode="night"):
    """Деревянный стул сбоку (Дима сидит лицом вправо): спинка слева за тазом. (x, sy) — таз сидящего; сиденье чуть ниже таза.
    tilt — откинулся (градусы, + назад): стул встаёт на задние ножки, поворот вокруг задней ножки на полу.
    dict(back — спинка (ДО Димы), seat — сиденье и ножки (после ног Димы, до тела))."""
    kk = _M(mode)["shade_k"]
    c, sh, hi = lib.mul(WOOD, kk), lib.mul(WOOD_SH, kk), lib.mul(WOOD_HI, kk)
    seat = sy + 24 * k
    bx0 = x - 120 * k
    pivot = (bx0 + 10 * k, FL)

    def P(pts):
        return lib.T(pts, 0, 0, 1, -tilt, pivot[0], pivot[1])
    back = []
    back.append(shape(P([(bx0 - 6 * k, seat, 1), (bx0 + 18 * k, seat, 1), (bx0 + 6 * k, seat - 400 * k, 1), (bx0 - 22 * k, seat - 396 * k, 1)]), c,
                      blob(P(rect_pts(bx0 - 30 * k, seat - 400 * k, bx0 - 10 * k, seat)), sh, .8), w=3.4, seed=500))
    back.append(shape(P(lib.rrect(bx0 - 30 * k, seat - 390 * k, bx0 + 30 * k, seat - 250 * k, 10 * k)), hi, blob(P(rect_pts(bx0 + 10 * k, seat - 390 * k, bx0 + 30 * k,
                                                                                                                             seat - 250 * k)), c, .8),
                      w=3.2, seed=501))
    front = []
    front.append(shape(P(lib.rrect(bx0 - 20 * k, seat - 6 * k, x + 170 * k, seat + 26 * k, 8 * k)), c, blob(P(rect_pts(bx0 - 20 * k, seat + 16 * k, x + 170 * k,
                                                                                                                       seat + 26 * k)), sh), w=3.4, seed=502))
    for i, lx in enumerate((bx0, x + 150 * k)):
        front.append(shape(P([(lx - 10 * k, seat + 26 * k, 1), (lx + 10 * k, seat + 26 * k, 1), (lx + 8 * k, FL, 1), (lx - 8 * k, FL, 1)]), c,
                           blob(P(rect_pts(lx + 2 * k, seat + 26 * k, lx + 10 * k, FL)), sh), w=3.0, seed=503 + i))
    front.append(line(P([(bx0 + 4 * k, seat + 170 * k), (x + 146 * k, seat + 170 * k)]), 7 * k, sh, taper=0, wmin=1, seed=506))
    return dict(back="".join(back), seat="".join(front))


def desk_lamp(on=1.0, swing=0.0, mode="night"):
    """Настольная лампа на столе: основание, изогнутая стойка, абажур-колокол смотрит вниз-влево (к открытке).
    swing — угол качания абажура (градусы; толчок от хлопка ящика — сцена задаёт затухающее колебание).
    Свет — небольшой круг на столешнице с ЧЁТКИМ краем, сдвигается вместе с абажуром; узкий конус слабой заливкой."""
    lx, ly = LAMP
    kk = _M(mode)["shade_k"]
    col, col_sh, col_hi = lib.mul("#3f6f7a", kk), lib.mul("#2c535c", kk), lib.mul("#5a95a2", kk)
    o = [shape(ellipse_pts(lx, ly - 6, 56, 13, 16), col, blob(ellipse_pts(lx + 14, ly - 2, 40, 7, 12), col_sh), w=3.2, seed=3300)]
    j1 = (lx + 6, ly - 150)
    a = math.radians(swing)
    arm = (-90.0, -60.0)
    j2 = (j1[0] + arm[0] * math.cos(a * .5) - arm[1] * math.sin(a * .5), j1[1] + arm[0] * math.sin(a * .5) + arm[1] * math.cos(a * .5))
    o.append(line([(lx, ly - 10), (lx + 10, ly - 80), j1], w=13, color=col_hi, taper=0.0, wmin=1, seed=3301))
    o.append(line([j1, j2], w=12, color=col_hi, taper=0.0, wmin=1, seed=3302))
    o.append(f'<circle cx="{f(j1[0])}" cy="{f(j1[1])}" r="10" fill="{col_sh}" stroke="{INK}" stroke-width="2.6"/>')
    hx, hy = j2
    ang = math.radians(24 + swing)
    ca, sa = math.cos(ang), math.sin(ang)

    def H(x, y):
        return (hx + x * ca - y * sa, hy + x * sa + y * ca)
    head = [H(-20, -16) + (1,), H(20, -16) + (1,), H(70, 70) + (1,), H(-70, 70) + (1,)]
    o.append(shape(head, col, blob([H(20, -16), H(70, 70), H(30, 70), H(0, -16)], col_sh, .85), w=3.6, seed=3303))
    u = lib.clamp(on)
    mouth = ellipse_pts(*H(0, 70), 70, 14, 20)
    mouth = [((p[0] - H(0, 70)[0]) * ca - (p[1] - H(0, 70)[1]) * sa * 1 + H(0, 70)[0], (p[0] - H(0, 70)[0]) * sa + (p[1] - H(0, 70)[1]) * ca + H(0, 70)[1])
             for p in mouth]
    o.append(shape(mouth, lib.mix("#c9bd9c", "#fff3c8", u), "", w=2.8, seed=3304))
    pool = ""
    if u > .02:
        px, py, rx, ry = LAMP_POOL
        m = H(0, 70)
        px = px + (m[0] - (LAMP[0] - 64)) * .9
        # чёткий круг света: ровная заливка, светлее к центру ступенькой, тонкое тёплое кольцо
        pool += f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="{f(rx)}" ry="{f(ry)}" fill="#ffe7a0" opacity="{.5 * u:.3f}"/>'
        pool += f'<ellipse cx="{f(px + 6)}" cy="{f(py - 2)}" rx="{f(rx * .6)}" ry="{f(ry * .6)}" fill="#fff4cc" opacity="{.45 * u:.3f}"/>'
        pool += f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="{f(rx)}" ry="{f(ry)}" fill="none" stroke="#f6c860" stroke-width="2.5" opacity="{.6 * u:.3f}"/>'
        m0, m1 = H(-66, 72), H(66, 72)
        pool += (f'<path d="M{f(m0[0])} {f(m0[1])}L{f(m1[0])} {f(m1[1])}L{f(px + rx * .95)} {f(py)}L{f(px - rx * .95)} {f(py)}Z" '
                 f'fill="#fff0b8" opacity="{.14 * u:.3f}"/>')
    return dict(lamp="".join(o), pool=pool)


def desk(mode="night", drawer=0.0, seed=0):
    """Стол вид спереди: верх-полоса глубины DESK_D, торец, царга с ящиком (drawer 0…1 — выдвинут к зрителю), ножки до FL.
    Возвращает dict(top, front, legs, inside, drawer_front): inside — прямоугольник видимой внутренности ящика."""
    kk = _M(mode)["shade_k"]
    c, sh, hi = lib.mul(DESKW, kk), lib.mul(DESKW_SH, kk), lib.mul(DESKW_HI, kk)
    x0, x1 = DESK_X
    y = DESK_TOP
    sd = 3000 + seed
    ins = 36.0
    top = [(x0 + 24, y - DESK_D, 1), (x1 - 24, y - DESK_D, 1), (x1, y, 1), (x0, y, 1)]
    inner = blob([(x0 + 24, y - DESK_D), (x1 - 24, y - DESK_D), (x1 - 18, y - DESK_D + 18), (x0 + 28, y - DESK_D + 18)], sh, .35)
    r = rs(7 + seed)
    for i in range(4):
        xa = r.uniform(x0 + 80, x1 - 200)
        ya = r.uniform(y - DESK_D + 30, y - 16)
        inner += line([(xa, ya), (xa + r.uniform(40, 90), ya + r.uniform(-3, 3))], w=1.8, color=sh, taper=.6, seed=sd + 10 + i, op=.6)
    top_svg = shape(top, c, inner, w=3.8, seed=sd + 1)
    # задние ножки (видны между передними)
    back_legs = ""
    for i, lx in enumerate((x0 + ins + 60, x1 - ins - 60)):
        back_legs += shape(rect_pts(lx - 11, y + DESK_TH, lx + 11, FL - 60), sh, w=3.0, seed=sd + 20 + i)
    front = [shape(rect_pts(x0, y, x1, y + DESK_TH), c, blob(rect_pts(x0, y + DESK_TH - 10, x1, y + DESK_TH), sh, .9), w=3.8, seed=sd + 2)]
    # царга (узкая доска под столешницей) по всей ширине, кроме ящика
    dx0, dx1, dy0, dy1 = DRAWER
    front.append(shape(rect_pts(x0 + 20, y + DESK_TH, x1 - 20, dy1 + 6), lib.mul(c, (.94, .94, .94)), blob(rect_pts(x0 + 20, dy1 - 6, x1 - 20, dy1 + 6), sh, .8),
                       w=3.2, seed=sd + 3))
    # ящик: проём (тёмный), выдвинутый ящик — боковины и дно внутри видны, передняя панель ниже и чуть крупнее
    u = lib.clamp(drawer)
    front.append(blob(rect_pts(dx0, dy0, dx1, dy1), lib.mul(sh, (.55, .55, .55))))
    pull = 70.0 * u
    s = 1 + .06 * u
    cxm = (dx0 + dx1) / 2
    fx0, fx1 = cxm - (dx1 - dx0) / 2 * s, cxm + (dx1 - dx0) / 2 * s
    fy0, fy1 = dy0 + pull * .55, dy1 + pull * .55 + (dy1 - dy0) * (s - 1)
    inside = None
    if u > .01:
        # внутренность: дно светлого дерева, боковины в перспективе, задняя стенка
        bx = [(dx0 + 8, dy0 + 6, 1), (dx1 - 8, dy0 + 6, 1), (fx1 - 10, fy0 + 4, 1), (fx0 + 10, fy0 + 4, 1)]
        front.append(shape(bx, lib.mul(DESKW_HI, (kk[0] * .9, kk[1] * .88, kk[2] * .85)),
                           blob([(dx0 + 8, dy0 + 6), (dx1 - 8, dy0 + 6), (dx1 - 8, dy0 + 6 + 10 * u), (dx0 + 8, dy0 + 6 + 10 * u)], sh, .7), w=2.8, seed=sd + 4))
        for sgn, (a, b) in ((-1, ((dx0 + 8, dy0 + 6), (fx0 + 10, fy0 + 4))), (1, ((dx1 - 8, dy0 + 6), (fx1 - 10, fy0 + 4)))):
            side = [(a[0], a[1], 1), (b[0], b[1], 1), (b[0], b[1] + 18, 1), (a[0], a[1] + 12, 1)]
            front.append(shape(side, hi, "", w=2.4, seed=sd + 6 + sgn))
        inside = (dx0 + 14, dy0 + 6, dx1 - 14, fy0 + 4)
    df = [shape(rect_pts(fx0, fy0, fx1, fy1), hi, blob(rect_pts(fx0, fy1 - 10, fx1, fy1), sh, .7), w=3.2, seed=sd + 8)]
    hw = 34 * s
    df.append(shape(lib.rrect(cxm - hw, (fy0 + fy1) / 2 - 8, cxm + hw, (fy0 + fy1) / 2 + 8, 7), "#3a3d46", blob(rect_pts(cxm - hw, (fy0 + fy1) / 2 + 2, cxm + hw,
                                                                                                                    (fy0 + fy1) / 2 + 8), "#22252c"),
                    w=2.4, seed=sd + 9))
    drawer_front = "".join(df)
    legs = ""
    for i, lx in enumerate((x0 + ins, x1 - ins)):
        legs += shape([(lx - 15, y + DESK_TH, 1), (lx + 15, y + DESK_TH, 1), (lx + 11, FL, 1), (lx - 11, FL, 1)], c, blob(rect_pts(lx + 3, y + DESK_TH, lx + 15, FL), sh, .8),
                      w=3.2, seed=sd + 12 + i)
    shadow = blob(ellipse_pts((x0 + x1) / 2, FL + 4, (x1 - x0) / 2 + 30, 16, 20), _M(mode)["shadow"], .3)
    return dict(top=top_svg, front="".join(front) + drawer_front, legs=shadow + back_legs + legs, inside=inside, drawer_front=drawer_front)


def wall_spot(x, y, k=1.0, u=1.0, mode="night"):
    """Одинокое пятнышко-трещинка на голой стене: тёмная точка и два коротких волоска трещины (u — сила 0…1)."""
    if u <= .01:
        return ""
    M = _M(mode)
    c = lib.mul(M["wall_sh"], (.62, .62, .66))
    o = blob(ellipse_pts(x, y, 7 * k, 5.5 * k, 10), c)
    o += line([(x + 5 * k, y + 2 * k), (x + 16 * k, y + 9 * k), (x + 24 * k, y + 8 * k)], 2.2 * k, c, taper=.7, wmin=.2, seed=7710)
    o += line([(x - 4 * k, y - 3 * k), (x - 12 * k, y - 13 * k)], 1.8 * k, c, taper=.7, wmin=.2, seed=7711)
    return f'<g opacity="{clamp01(u):.3f}">{o}</g>'


def desk_scene(t, mode="night", drawer=0.0, lamp_swing=0.0, chair_tilt=0.0, lamp_on=None, sit=None, bs=1.0, spot=False):
    """Угол комнаты со столом у голой стены. Порядок слоёв в клипе:
    bg → chair_back → desk_top → pool → [Дима: legs] → desk_legs → chair_seat → [pelvis, arm_f, body] → предметы → [arm_n] → lamp.
    sit — таз Димы (по умолчанию SIT), стул ставится под него."""
    o = [wall_floor(mode)]
    o.append(sun_patches(mode))
    o.append(window(*WIN_TALL, mode, t, seed=1, sway=.7))
    o.append(wall_picture(470, 430, 150, 120, mode, seed=1))
    o.append(shelf(1420, 1760, 560, mode, seed=1, t=t))
    if spot:
        o.append(wall_spot(*WALL_SPOT, 1.0, 1.0, mode))
    o.append(rug(520, FL + 70, 430, 90, mode))
    sx, sy = sit or SIT
    ch = chair(sx, sy, bs, chair_tilt, mode)
    on = (1.0 if is_dark(mode) else 0.0) if lamp_on is None else lamp_on
    lp = desk_lamp(on, lamp_swing, mode)
    d = desk(mode, drawer)
    return dict(bg="".join(o), chair_back=ch["back"], chair_seat=ch["seat"], desk=d["legs"] + d["top"] + d["front"], pool=lp["pool"], lamp=lp["lamp"],
                inside=d["inside"], drawer_front=d["drawer_front"], desk_top=d["top"] + d["front"], desk_legs=d["legs"])


# ═════════════════════════ через плечо на стену (s05) ═════════════════════════
V_DESK_Y = 1120.0       # дальний край столешницы (у стены) в кадре
V_DESK_F = 1420.0       # ближний край столешницы
V_LAMP = (870.0, 1250.0)


def wall_view(t, mode="night", tl=0.0, spot=1.0):
    """Вид из-за спины Димы: голая стена во весь кадр, стол поперёк кадра. tl 0…1 — ускоренное время (полоса света ползёт).
    dict(bg, desk, pool, lamp, chair) — chair — функция chair(squash, bounce) → SVG спинки стула (класть после Димы)."""
    M = _M(mode)
    dark = is_dark(mode)
    o = []
    wall = lib.mix(M["wall"], M["wall_sh"], .35 * clamp01(tl)) if dark else M["wall"]
    g = lib.lin_grad([(0, lib.mix(wall, M["wall_sh"], .5), 1), (.55, wall, 1), (1, lib.mix(wall, M["wall_hi"], .4), 1)], 0, -400, 0, V_DESK_Y,
                     units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-900" width="2880" height="{f(V_DESK_Y + 900)}" fill="url(#{g})"/>')
    for i in range(-6, 14):      # обои: редкие вертикальные полосы
        x = i * 150.0 + 40
        o.append(line([(x, -900), (x + 1.5, V_DESK_Y - 10)], w=1.8, color=M["wall_ln"], taper=0.0, wmin=1, seed=7720 + i, op=.5))
    # край высокого окна слева (рама, кусок неба, штора) — источник полосы света
    o.append(window(-430, 80, 90, 1000, mode, t, seed=11, sway=.5))
    # полоса света формы окна на стене: ночью лунная (бледная), днём солнечная; ползёт слева направо и вытягивается
    u = clamp01(tl)
    ax = 230 + 500 * u
    col, col2 = (("#c9cbe6", "#d8d9ef") if dark else ("#f6e7bf", "#fbf0d2"))
    op = (.38 if dark else .9) * (1 - .55 * u * u)
    o.append(f'<g opacity="{op:.3f}">' + _sun_quad((ax, 170 + 120 * u), (210 + 120 * u, 40 + 70 * u), (40 + 60 * u, 560 - 90 * u), col, col2, inset=.05)
             + "</g>")
    # тень от абажура лампы на стене — клин, ползёт вслед за светом (время идёт)
    if dark:
        sx0 = 760 - 140 * u
        o.append(blob([(sx0, V_DESK_Y - 10, 1), (sx0 + 130, V_DESK_Y - 10, 1), (sx0 + 60 - 60 * u, 640 + 80 * u, 1), (sx0 - 30 - 60 * u, 660 + 80 * u, 1)],
                      M["wall_sh"], .45))
    o.append(wall_spot(*WALL_SPOT_V, 1.15, spot, mode))
    bg = "".join(o)
    # стол: столешница сверху-сзади (трапеция, ближний край шире), торец ближнего края, под столом темно
    kk = M["shade_k"]
    c, sh, hi = lib.mul(DESKW, kk), lib.mul(DESKW_SH, kk), lib.mul(DESKW_HI, kk)
    d = []
    d.append(blob(rect_pts(-900, V_DESK_F, 1980, 2900), lib.mul(M["floor_b"], (.7, .7, .74))))
    top = [(-300, V_DESK_Y, 1), (1380, V_DESK_Y, 1), (1700, V_DESK_F, 1), (-620, V_DESK_F, 1)]
    inner = blob([(-300, V_DESK_Y), (1380, V_DESK_Y), (1400, V_DESK_Y + 26), (-320, V_DESK_Y + 26)], sh, .45)
    r = rs(77)
    for i in range(6):
        xa = r.uniform(-100, 1000)
        ya = r.uniform(V_DESK_Y + 40, V_DESK_F - 30)
        d_ = r.uniform(60, 130)
        inner += line([(xa, ya), (xa + d_, ya + r.uniform(-3, 3))], w=2.2, color=sh, taper=.6, seed=7740 + i, op=.55)
    d.append(shape(top, c, inner, w=4.2, seed=7750))
    d.append(shape(rect_pts(-640, V_DESK_F, 1720, V_DESK_F + 46), c, blob(rect_pts(-640, V_DESK_F + 30, 1720, V_DESK_F + 46), sh, .9), w=4.2, seed=7751))
    d.append(blob(rect_pts(-640, V_DESK_F + 46, 1720, V_DESK_F + 60), "#000000", .25))
    desk_svg = "".join(d)
    # лампа справа: та же модель, что у стола, но вид сзади-сбоку, абажур к ноутбуку
    lx, ly = V_LAMP
    col_, col_sh, col_hi = lib.mul("#3f6f7a", kk), lib.mul("#2c535c", kk), lib.mul("#5a95a2", kk)
    on = 1.0 if dark else 0.0
    lm = [shape(ellipse_pts(lx, ly - 8, 74, 18, 18), col_, blob(ellipse_pts(lx + 16, ly - 2, 52, 9, 12), col_sh), w=3.6, seed=7760)]
    j1 = (lx + 10, ly - 210)
    j2 = (lx - 110, ly - 290)
    lm.append(line([(lx, ly - 14), (lx + 14, ly - 110), j1], w=17, color=col_hi, taper=0.0, wmin=1, seed=7761))
    lm.append(line([j1, j2], w=16, color=col_hi, taper=0.0, wmin=1, seed=7762))
    lm.append(f'<circle cx="{f(j1[0])}" cy="{f(j1[1])}" r="13" fill="{col_sh}" stroke="{INK}" stroke-width="3"/>')
    hx, hy = j2
    ang = math.radians(-28)
    ca, sa = math.cos(ang), math.sin(ang)

    def H(x, y):
        return (hx + x * ca - y * sa, hy + x * sa + y * ca)
    lm.append(shape([H(-26, -20) + (1,), H(26, -20) + (1,), H(92, 92) + (1,), H(-92, 92) + (1,)], col_,
                    blob([H(26, -20), H(92, 92), H(40, 92), H(0, -20)], col_sh, .85), w=4.0, seed=7763))
    m = H(0, 92)
    mouth = [((p[0] - m[0]) * ca - (p[1] - m[1]) * sa + m[0], (p[0] - m[0]) * sa + (p[1] - m[1]) * ca + m[1]) for p in ellipse_pts(m[0], m[1], 92, 18, 20)]
    lm.append(shape(mouth, lib.mix("#c9bd9c", "#fff3c8", on), "", w=3.0, seed=7764))
    pool = ""
    if on:
        px, py = m[0] - 70, V_DESK_Y + 150
        pool += f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="170" ry="42" fill="#ffe7a0" opacity=".5"/>'
        pool += f'<ellipse cx="{f(px + 8)}" cy="{f(py - 3)}" rx="100" ry="25" fill="#fff4cc" opacity=".45"/>'
        pool += f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="170" ry="42" fill="none" stroke="#f6c860" stroke-width="3" opacity=".6"/>'

    def chair_back(squash=0.0, bounce=0.0):
        """Спинка стула сзади (мы за ней): две стойки и широкая перекладина; squash — сиденье проседает, bounce — спинка качается."""
        cc, csh, chi = lib.mul(WOOD, kk), lib.mul(WOOD_SH, kk), lib.mul(WOOD_HI, kk)
        x0, x1 = DIMA_V[0] - 250, DIMA_V[0] + 250
        yb = 2100 + 30 * squash
        yt = DIMA_V[1] + 120 + 40 * squash
        rr = bounce

        def P(pts):
            return lib.T(pts, 0, 0, 1, rr, DIMA_V[0], yb)
        out = []
        for i, sx_ in enumerate((x0, x1 - 34)):
            out.append(shape(P(rect_pts(sx_, yt - 30, sx_ + 34, yb)), cc, blob(P(rect_pts(sx_ + 22, yt - 30, sx_ + 34, yb)), csh, .8), w=4.0, seed=7770 + i))
        out.append(shape(P(lib.rrect(x0 - 16, yt - 40, x1 + 16, yt + 110, 16)), chi, blob(P(rect_pts(x0 - 16, yt + 80, x1 + 16, yt + 110)), cc, .9),
                         w=4.2, seed=7772))
        out.append(shape(P(rect_pts(x0 + 10, yt + 230, x1 - 10, yt + 270)), cc, "", w=3.6, seed=7773))
        return "".join(out)
    return dict(bg=bg, desk=desk_svg, pool=pool, lamp="".join(lm), chair=chair_back)


# ═════════════════════════ коридор (s12) ═════════════════════════
HALL = dict(night=dict(wall="#6f7f86", wall_hi="#83939a", wall_sh="#56656c", stripe="#64747b", floor="#6a4a32", floor_b="#4e3524", ln="#3a2618",
                       base="#9aa6aa", base_sh="#76838a", light="#ffe7a0"),
            day=dict(wall="#c9d6cf", wall_hi="#dbe6e0", wall_sh="#aebdb5", stripe="#bccac2", floor="#b88654", floor_b="#9c6e42", ln="#7a5232",
                     base="#eef0ea", base_sh="#cdd2ca", light="#fff4cc"))


def hall_scene(t, mode="night"):
    """Коридор у двери комнаты: стена другого цвета, чем комната (серо-зелёная), плинтус, пол, вешалка с курткой слева, коврик,
    плафон под потолком. Место двери HALL_DOOR остаётся пустой стеной — дверь из props кладёт сцена (поверх bg); наличник — здесь
    (рама вокруг проёма). dict(bg, frame, front): frame — наличник (класть ПОСЛЕ двери, если полотно шире проёма)."""
    M = HALL["day" if mode == "day" else "night"]
    o = []
    g = lib.lin_grad([(0, M["wall_sh"], 1), (.4, M["wall"], 1), (1, M["wall_hi"], 1)], 0, -600, 0, WALL_Y, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="-600" width="5000" height="{f(WALL_Y + 600)}" fill="url(#{g})"/>')
    for i in range(-14, 30):     # обои коридора: двойные тонкие полосы
        x = i * 110.0
        o.append(line([(x, -600), (x + 1.2, WALL_Y - 40)], w=2.0, color=M["stripe"], taper=0.0, wmin=1, seed=7800 + i, op=.7))
        o.append(line([(x + 12, -600), (x + 13.2, WALL_Y - 40)], w=1.2, color=M["stripe"], taper=0.0, wmin=1, seed=7850 + i, op=.5))
    o.append(shape(rect_pts(-1600, WALL_Y - 56, 3400, WALL_Y + 6), M["base"], blob(rect_pts(-1600, WALL_Y - 10, 3400, WALL_Y + 6), M["base_sh"]),
                   w=3.4, seed=7900))
    gf = lib.lin_grad([(0, M["floor"], 1), (1, M["floor_b"], 1)], 0, WALL_Y, 0, 2400, units="userSpaceOnUse")
    o.append(f'<rect x="-1600" y="{f(WALL_Y + 6)}" width="5000" height="{f(2400 - WALL_Y)}" fill="url(#{gf})"/>')
    for k, y in enumerate((1490, 1560, 1650, 1770, 1930, 2120)):
        o.append(line([(-1600, y), (3400, y)], w=3.0, color=M["ln"], taper=0.0, wmin=1, seed=7910 + k, op=.6))
    r = rs(78)
    for k in range(30):
        x = r.uniform(-1500, 3300)
        y0 = r.choice([1446, 1490, 1560, 1650, 1770, 1930])
        o.append(line([(x, y0), (x + r.uniform(-4, 4), y0 + 70)], w=2.4, color=M["ln"], taper=0.0, wmin=1, seed=7920 + k, op=.45))
    # плафон: небольшой круг с чёткой формой, свет — чёткое пятно на стене под ним
    dx, fy, dw, dh = HALL_DOOR
    lx = dx - 420
    o.append(f'<ellipse cx="{f(lx)}" cy="250" rx="150" ry="60" fill="{M["light"]}" opacity=".22"/>')
    o.append(shape(ellipse_pts(lx, 170, 70, 30, 18), "#f6efd8", blob(ellipse_pts(lx, 182, 60, 14, 14), "#fff8e0"), w=3.0, seed=7930))
    o.append(line([(lx, -600), (lx, 142)], 4, "#3a3d46", taper=0, wmin=1, seed=7931))
    # вешалка с курткой (тёмно-синяя, без надписей) и шарфом
    hx = dx - 520
    o.append(shape(lib.rrect(hx - 150, 520, hx + 150, 556, 8), lib.mul(WOOD_SH, (.95, .95, .95)), "", w=3.2, seed=7940))
    for i, kx in enumerate((hx - 100, hx, hx + 100)):
        o.append(line([(kx, 548), (kx + 4, 600), (kx + 22, 606)], 6, "#3a3d46", taper=.2, wmin=.6, seed=7941 + i))
    jk = [(hx - 30, 590, 1), (hx + 40, 590, 1), (hx + 120, 660), (hx + 140, 980, 1), (hx + 70, 1000), (hx - 60, 1000), (hx - 120, 980, 1), (hx - 100, 660)]
    o.append(shape(jk, "#3d5277", line([(hx + 8, 600), (hx + 2, 990)], 3.2, "#2b3b58", taper=.3, wmin=.4, seed=7946)
                   + blob([(hx + 60, 620), (hx + 130, 700), (hx + 140, 980), (hx + 80, 990)], "#2b3b58", .7), w=4.0, seed=7945))
    sc_ = [(hx - 6, 596, 1), (hx + 30, 596, 1), (hx + 40, 860, 1), (hx + 6, 866, 1)]
    o.append(shape(sc_, "#c8634a", line([(hx + 4, 700), (hx + 36, 700)], 2.4, "#9a4632", taper=0, wmin=1, seed=7948), w=3.2, seed=7947))
    # коврик у двери
    o.append(blob(ellipse_pts(dx + 6, fy + 70, 280, 34, 22), "#000000", .18))
    o.append(shape(lib.rrect(dx - 260, fy + 30, dx + 260, fy + 100, 14), "#8a6f9a",
                   blob(lib.rrect(dx - 230, fy + 44, dx + 230, fy + 86, 10), "#a688b4"), w=3.4, seed=7950))
    # проём двери: тень от полотна на пол
    o.append(blob([(dx - dw / 2, fy, 1), (dx + dw / 2, fy, 1), (dx + dw / 2 + 40, fy + 26, 1), (dx - dw / 2 + 20, fy + 26, 1)], "#000000", .22))
    # наличник
    cas = lib.mul(M["base"], (.98, .98, .98))
    fr = []
    x0, x1, y0 = dx - dw / 2, dx + dw / 2, fy - dh
    for i, pts in enumerate(([(x0 - 34, y0 - 34, 1), (x0, y0 - 34, 1), (x0, fy, 1), (x0 - 34, fy, 1)],
                             [(x1, y0 - 34, 1), (x1 + 34, y0 - 34, 1), (x1 + 34, fy, 1), (x1, fy, 1)],
                             [(x0 - 34, y0 - 34, 1), (x1 + 34, y0 - 34, 1), (x1 + 34, y0, 1), (x0 - 34, y0, 1)])):
        fr.append(shape(pts, cas, blob(rect_pts(pts[0][0], pts[0][1], pts[0][0] + 8, fy), M["base_sh"], .7), w=3.4, seed=7960 + i))
    return dict(bg="".join(o), frame="".join(fr), front="")


# ═════════════════════════ окно в полный рост ═════════════════════════
def window_scene(t, mode="day", sway=1.0):
    """Стена с высоким окном: Дима стоит у окна в полный рост (STAND). bg — стена, окно с деревьями, полоса солнца, пол; front — пусто
    (штора у окна уже в bg; Диму ставить после bg)."""
    o = [wall_floor(mode), sun_patches(mode), window(*WIN_TALL, mode, t, seed=1, sway=sway)]
    o.append(rug(-300, FL + 80, 380, 80, mode, seed=3))
    return dict(bg="".join(o), front="")


# ═════════════════════════ диван ═════════════════════════
def sofa(x, y, k=1.0, mode="day", seed=0, col="#4a6fa5"):
    """Диван анфас: спинка, две подушки сиденья, подлокотники, ножки. (x, y) — низ ножек, центр.
    dict(back — спинка, подушки, левый подлокотник; arm_r — правый подлокотник (класть после Димы, если надо перекрыть))."""
    kk = _M(mode)["shade_k"]
    c = lib.mul(col, kk)
    sh = lib.mul(c, (.8, .8, .82))
    hi = lib.mix(c, "#ffffff", .18)
    W = 820 * k
    x0, x1 = x - W / 2, x + W / 2
    seat = y - 310 * k
    o = [blob(ellipse_pts(x, y + 4, W / 2 + 40, 18, 20), _M(mode)["shadow"], .3)]
    for lx in (x0 + 50 * k, x1 - 50 * k):
        o.append(shape(rect_pts(lx - 14 * k, y - 50 * k, lx + 14 * k, y), lib.mul(WOOD_SH, kk), "", w=2.8, seed=600 + seed + int(lx) % 9))
    o.append(shape(lib.rrect(x0 + 60 * k, seat - 330 * k, x1 - 60 * k, seat + 30 * k, 40 * k), c,
                   blob(lib.rrect(x0 + 60 * k, seat - 120 * k, x1 - 60 * k, seat + 30 * k, 30 * k), sh, .7)
                   + line([(x, seat - 310 * k), (x + 4, seat - 40 * k)], 3.0, sh, taper=.3, wmin=.4, seed=610 + seed), w=4.2, seed=611 + seed))
    o.append(shape(lib.rrect(x0 + 40 * k, y - 120 * k, x1 - 40 * k, y - 40 * k, 16 * k), sh, "", w=3.6, seed=612 + seed))
    for i, (a, b) in enumerate(((x0 + 70 * k, x - 4), (x + 4, x1 - 70 * k))):
        o.append(shape(lib.rrect(a, seat - 40 * k, b, y - 110 * k, 26 * k), hi, blob(lib.rrect(a, seat + 40 * k, b, y - 110 * k, 20 * k), c, .8),
                       w=3.6, seed=620 + seed + i))
    arm = []
    for i, (a, b) in enumerate(((x0, x0 + 110 * k), (x1 - 110 * k, x1))):
        a_svg = shape(lib.rrect(a, seat - 150 * k, b, y - 44 * k, 36 * k), c, blob(lib.rrect(a, seat - 20 * k, b, y - 44 * k, 30 * k), sh, .8)
                      + blob(lib.rrect(a + 10 * k, seat - 146 * k, b - 10 * k, seat - 110 * k, 18 * k), hi, .8), w=4.0, seed=630 + seed + i)
        arm.append(a_svg)
    return dict(back="".join(o) + arm[0], arm_r=arm[1])


def floor_lamp(x, y, k=1.0, mode="day", on=0.0):
    """Торшер у дивана: тонкая стойка, абажур-цилиндр; свет (если on) — только короткий чёткий веер вниз-вверх у абажура."""
    kk = _M(mode)["shade_k"]
    o = [shape(ellipse_pts(x, y - 6, 60, 12, 16), lib.mul("#4a4f5c", kk), "", w=3.0, seed=700)]
    o.append(line([(x, y - 10), (x + 2, y - 760 * k)], 10, lib.mul("#5a606e", kk), taper=0, wmin=1, seed=701))
    top = y - 760 * k
    o.append(shape([(x - 70 * k, top - 120 * k, 1), (x + 70 * k, top - 120 * k, 1), (x + 95 * k, top + 20 * k, 1), (x - 95 * k, top + 20 * k, 1)],
                   lib.mix(lib.mul("#e8c98a", kk), "#fff3c8", on), blob(rect_pts(x + 40 * k, top - 130 * k, x + 100 * k, top + 30 * k), lib.mul("#c9a866", kk), .5),
                   w=3.4, seed=702))
    return "".join(o)


def side_table(x, y, mode="day"):
    """Круглый столик у дивана (кружку/мобильник ставит сцена дном на y − 300)."""
    kk = _M(mode)["shade_k"]
    c = lib.mul(WOOD, kk)
    o = [shape(rect_pts(x - 10, y - 290, x + 10, y), lib.mul(WOOD_SH, kk), "", w=2.8, seed=720)]
    o.append(shape(ellipse_pts(x, y - 4, 60, 12, 14), lib.mul(WOOD_SH, kk), "", w=2.6, seed=721))
    o.append(shape(ellipse_pts(x, y - 300, 120, 26, 22), c, blob(ellipse_pts(x + 10, y - 294, 110, 20, 20), lib.mul(WOOD_HI, kk), .6), w=3.2, seed=722))
    return "".join(o)


def sofa_scene(t, mode="day"):
    """Угол с диваном. Порядок: bg → sofa → [Дима сидит, кот на коленях] → front (правый подлокотник) → [кот на подлокотнике, «кот»].
    Над правым подлокотником CLEAN_WALL — чистая стена (ни картинок, ни солнца, ни теней): там пишется «кот»."""
    o = [wall_floor(mode)]
    # картина над ЛЕВОЙ половиной дивана и торшер слева — чистая стена справа остаётся пустой
    o.append(wall_picture(1960, 520, 260, 190, mode, seed=5))
    o.append(floor_lamp(1600, FL, 1.0, mode, on=0.0))
    o.append(side_table(1700, FL, mode))
    o.append(rug(2250, FL + 90, 560, 95, mode, seed=7))
    sf = sofa(SOFA[0], SOFA[1], SOFA[2], mode)
    return dict(bg="".join(o), sofa=sf["back"], front=sf["arm_r"])
