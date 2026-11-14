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
        CAM_SIDE_MID=(730, 900, 1.45)   средний план сбоку (s04): Дима на стуле по колени, стол, ноутбук, лампа
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
    Дима со спины — из people.py (группа B), плечи и затылок на переднем плане: DIMA_V=(250, 1470) — основание шеи для people.dima_back(…, scale≈1.9): голова ~570 px слева, ноутбук и
    пятнышко на стене видны справа от неё. LAPTOP_V=(650, 1262) дно ноутбука (k≈.7), TIMER_V=(905, 1300) таймер (k≈.66).
    CAM_SHOULDER=(540, 960, 1.0); наезд на стену — к WALL_SPOT_V, без рывков.

КОРИДОР (s12) — hall_scene(t, mode="night") -> dict(bg, front): стена коридора (другого цвета), плинтус, пол, вешалка с курткой
    у левого края, коврик; место двери — HALL_DOOR=(867, FL, 684, 1392) (центр x, пол, ширина, высота): дверь из props ставит сцена, здесь —
    только наличник (рама) и тень на полу; front — пусто. Свет — плафон сверху (небольшой круг с чёткой формой).
    CAM_HALL=(600, 1080, 1.0).
    Дверь — props.door(dx, FL, HALL_DOOR_K) ЗЕРКАЛЬНО (ручка слева, к Диме): ручка в мире (dx − 150·k, FL − 470·k) ≈ (650, 878);
    Дима в позе people "door" стоит слева, таз ≈ (300, 962) при scale 1. Наличник у props.door свой — frame из hall_scene не нужен.
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
CAM_SIDE_MID = (730.0, 900.0, 1.45)
CAM_DAY_WIDE = (760.0, 1020.0, 0.86)
CAM_CLEAN = (900.0, 640.0, 1.2)
CAM_DESK_MID = CAM_SIDE_MID
# через плечо (координаты кадра)
WALL_SPOT_V = (600.0, 610.0)
LAPTOP_V = (650.0, 1262.0)
TIMER_V = (905.0, 1300.0)
DIMA_V = (250.0, 1470.0)
CAM_SHOULDER = (540.0, 960.0, 1.0)
# коридор
HALL_DOOR = (867.0, FL, 684.0, 1392.0)
HALL_DOOR_K = 1.45
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
V_LAMP = (1010.0, 1240.0)


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
    o.append(wall_spot(*WALL_SPOT_V, 1.9, spot, mode))
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

    def chair_back(squash=0.0, bounce=0.0, k=1.0):
        """Спинка стула сзади (мы за ней): две стойки и широкая перекладина; squash — сиденье проседает, bounce — спинка качается."""
        cc, csh, chi = lib.mul(WOOD, kk), lib.mul(WOOD_SH, kk), lib.mul(WOOD_HI, kk)
        x0, x1 = DIMA_V[0] - 230 * k, DIMA_V[0] + 230 * k
        yb = 2400 + 30 * squash
        yt = DIMA_V[1] + 230 * k + 40 * squash
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
    lx = dx - 300
    o.append(f'<ellipse cx="{f(lx)}" cy="250" rx="150" ry="60" fill="{M["light"]}" opacity=".22"/>')
    o.append(shape(ellipse_pts(lx, 170, 70, 30, 18), "#f6efd8", blob(ellipse_pts(lx, 182, 60, 14, 14), "#fff8e0"), w=3.0, seed=7930))
    o.append(line([(lx, -600), (lx, 142)], 4, "#3a3d46", taper=0, wmin=1, seed=7931))
    # вешалка с курткой (тёмно-синяя, без надписей) и шарфом
    hx = dx - 1060
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


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# РИЛС 71 «два лагеря» (группа C). Все места — в координатах кадра 1080×1920 при своей камере CAM_* (cx, cy, s).
#
# КРОВАТЬ КРУПНО — ОДИН ракурс для хука s01 и петли s22:  bed_close(t, mode="morning") -> dict(bg, mattress, pillow(squash, dx), motes, front)
#     камера низко у матраса, смотрит вдоль кровати на изголовье: стена с полосой утреннего солнца формы окна, деревянное
#     изголовье, подушка у изголовья, простыня уходит к зрителю до низа кадра. Кокон Димы лежит головой на подушке и тянется к
#     зрителю (вниз по кадру): лицо ≈ BC_FACE, кокон до низа кадра. Порядок: bg → mattress → pillow(squash) → [кокон] → motes → front.
#     BC_PILLOW=(540, 880) центр подушки (вмятина), BC_FACE=(540, 860) центр лица на подушке (лицо ~700 px высотой при k≈2.4),
#     BC_SHEET_Y=700 дальний край матраса, BC_CAT=(930, 1180) где кот стоит лапами на матрасе справа (s22, тычет лапой в кокон).
#     CAM_BED_CLOSE=(540, 960, 1.0). pillow(squash 0…1 — сплющена ударом, dx — сдвиг вмятины).
#     motes(t, u) — пылинки в полосе солнца (кружат, мерцают); front — тень края одеяла внизу (пусто, если не нужен).
#
# КРОВАТЬ СРЕДНИМ ПЛАНОМ (s03, s06, s08):  bed_mid(t, mode="morning") -> dict(bg, bed, front)
#     кровать анфас вдоль стены, Дима сидит на ней лицом к нам; слева в глубине окно с широким подоконником (кот на нём),
#     полоса солнца формы окна на стене справа. Порядок: bg → bed → [кот на подоконнике] → [Дима] → front (передний край матраса,
#     если ступни свисают — класть ДО ступней; front — пусто, оставлен для общего порядка).
#     BM_SIT=(560, 1150) таз сидящего Димы (верх матраса), ступни на полу BM_FLOOR=1560 (стоят на y≈1530)
#     BM_SILL=(250, 772) подоконник: кот сидит лапами на этой линии (k≈.9), BM_WIN=(70, 230, 440, 760)
#     CAM_BED_MID=(540, 960, 1.0); наезд — к лицу (BM_SIT[0], BM_SIT[1] − 430).
#
# КОМНАТА ДНЁМ (s11–s13, s17, s21):  day_room(t) -> dict(bg, desk, stand, bed, front)
#     широкий мир: слева стол с ЗАКРЫТЫМ ноутбуком (ставит сцена: props.laptop), на полу у центра место носка, справа тумба с
#     графином и стаканом (ставит сцена: props.jug, props.glass); дальше вправо (x 1500…2600) кровать у стены с окном и чистой
#     стеной над ней, на стене два флажка-рисунка (жёлтый с молнией, синий с клубком — без букв).
#     FL=1560 пол, WALL_Y=1440 низ стены.  Дима стоит в полный рост по центру: DR_DIMA=(540, 1560 − 598) таз при scale 1.0
#     (ступни на FL, голова ≈ 330) — ≥ 60 % высоты кадра на CAM_ROOM.
#     DR_LAPTOP=(200, 1052) дно ноутбука на столе (k≈.8), DR_SOCK=(790, 1520) носок на полу, DR_JUG=(930, 1180) графин и
#     DR_GLASS=(1010, 1180) стакан на тумбе (дно), DR_DESK=(20, 380, 1060) стол: x0, x1, верх; DR_STAND=(880, 1060, 1190) тумба.
#     CAM_ROOM=(540, 960, 1.0) три дела и Дима целиком; CAM_ROOM_NEAR=(540, 900, 1.25) ближе (мим, s12; ступни уходят под кадр).
#     Кровать справа: DR_BED=(2050, 1560) центр низа ножек, верх матраса DR_BED_TOP=1210 (Дима и кот сидят на нём, s21;
#     край кровати s17 — камера CAM_BED_EDGE=(1720, 1150, 1.35)); флажки DR_FLAGS=((1820, 470), (2280, 470)) центры;
#     DR_CLEAN=(1900, 640, 2200, 860) — ЧИСТАЯ стена между флажками и над изголовьем (рукописное «кот» s21): ни предметов, ни теней.
#     CAM_DR_BED=(2050, 960, 1.0) кровать, флажки и чистая стена.
#
# СТОЛ СБОКУ-СЗАДИ В ТРИ ЧЕТВЕРТИ (s16, s19, s20):  desk34_scene(t) = desk_scene(t, "day") рилса 70 (Дима слева от стола
#     лицом вправо, ноутбук ставить с turn ≥ .55 — экран к Диме, зритель видит крышку сзади-сбоку); камера CAM_DESK34=(760, 860, 1.25)
#     — за левым плечом Димы. Место меловой стены за спиной Димы (s19) — DESK34_WALL=(−120, 300, 260, 1440) (x0, y0, x1, y1).
#
# КУХНЯ ДНЁМ (s09, s10, s18):  kitchen_scene(t, mode="day") -> dict(bg, chairs_back, table, front)
#     стена с плиткой, окно с деревом (качается), столешница с раковиной и краном, нижние шкафы; посередине стол анфас, по
#     краям два стула боком: Дима слева (лицом вправо), друг справа (лицом влево). Порядок: bg → chairs_back → [Дима, друг] → table
#     → [кружки, графин] → front. KS_TABLE=(250, 830, 1160) стол: x0, x1, передняя кромка (верх виден, глубина 90);
#     KS_SIT_L=(170, 1100) таз Димы, KS_SIT_R=(910, 1100) таз друга (scale 1.0); KS_MUG_L=(380, 1130), KS_MUG_R=(700, 1130) — дно кружек;
#     KS_JUG=(540, 1110) — графин на столе (s18); KS_FLOOR=1560. CAM_KITCHEN=(540, 960, 1.0), CAM_KITCHEN_NEAR=(540, 880, 1.3).
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
BC_PILLOW = (540.0, 880.0)
BC_FACE = (540.0, 860.0)
BC_SHEET_Y = 700.0
BC_CAT = (930.0, 1180.0)
CAM_BED_CLOSE = (540.0, 960.0, 1.0)

BM_SIT = (560.0, 1150.0)
BM_FLOOR = 1560.0
BM_SILL = (250.0, 772.0)
BM_WIN = (70.0, 230.0, 440.0, 760.0)
CAM_BED_MID = (540.0, 960.0, 1.0)

DR_DIMA = (540.0, FL - 598.0)
DR_LAPTOP = (200.0, 1052.0)
DR_SOCK = (790.0, 1520.0)
DR_JUG = (930.0, 1180.0)
DR_GLASS = (1010.0, 1180.0)
DR_DESK = (20.0, 380.0, 1060.0)
DR_STAND = (880.0, 1060.0, 1190.0)
CAM_ROOM = (540.0, 960.0, 1.0)
CAM_ROOM_NEAR = (540.0, 900.0, 1.25)
DR_BED = (2050.0, FL)
DR_BED_TOP = 1210.0
CAM_BED_EDGE = (1720.0, 1150.0, 1.35)
DR_FLAGS = ((1820.0, 470.0), (2280.0, 470.0))
DR_CLEAN = (1900.0, 640.0, 2200.0, 860.0)
CAM_DR_BED = (2050.0, 960.0, 1.0)

CAM_DESK34 = (760.0, 860.0, 1.25)
DESK34_WALL = (-120.0, 300.0, 260.0, 1440.0)

KS_TABLE = (250.0, 830.0, 1160.0)
KS_SIT_L = (170.0, 1100.0)
KS_SIT_R = (910.0, 1100.0)
KS_MUG_L = (380.0, 1130.0)
KS_MUG_R = (700.0, 1130.0)
KS_JUG = (540.0, 1110.0)
KS_FLOOR = 1560.0
CAM_KITCHEN = (540.0, 960.0, 1.0)
CAM_KITCHEN_NEAR = (540.0, 880.0, 1.3)

SHEET, SHEET_SH, SHEET_HI = "#eef0f4", "#cdd3dd", "#ffffff"
SUN_WALL, SUN_WALL_HI = "#f8e3b0", "#fcefcc"
MORNING = dict(wall="#e9d6bc", wall_hi="#f2e3cc", wall_sh="#d6bf9f", wall_ln="#dcc7a8")


def _wall_plain(x0, y0, x1, y1, pal, seed=0):
    g = lib.lin_grad([(0, pal["wall_sh"], 1), (.4, pal["wall"], 1), (1, pal["wall_hi"], 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    o = [f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="url(#{g})"/>']
    for i in range(int((x1 - x0) // 150) + 1):
        x = x0 + 40 + i * 150.0
        o.append(line([(x, y0), (x + 1.5, y1)], w=1.8, color=pal["wall_ln"], taper=0.0, wmin=1, seed=8800 + seed + i, op=.5))
    return "".join(o)


def motes(t, box=(560.0, 120.0, 1000.0, 820.0), n=14, u=1.0, seed=0):
    """Пылинки в полосе солнца: кружат по своим орбитам, мерцают (светлые точки с тонкой тушью)."""
    if u <= .01:
        return ""
    x0, y0, x1, y1 = box
    r = rs(8900 + seed)
    o = []
    for i in range(n):
        bx, by = r.uniform(x0, x1), r.uniform(y0, y1)
        rad, w0, ph = r.uniform(18, 46), r.uniform(1.2, 2.6) * (1 if i % 2 else -1), r.uniform(0, 6.3)
        x = bx + rad * math.cos(t * w0 + ph)
        y = by + rad * .7 * math.sin(t * w0 * 1.3 + ph) - 14 * t
        y = y0 + (y - y0) % (y1 - y0)
        a = u * (.55 + .45 * math.sin(t * 5.1 + i * 1.7))
        rr = r.uniform(3.5, 6.5)
        o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr)}" fill="#fff6d6" opacity="{a:.3f}"/>')
    return "".join(o)


# ═════════════════════════ кровать крупно (s01, s22) ═════════════════════════
def bed_close_pillow(squash=0.0, dx=0.0, x=None, y=None):
    """Большая подушка у изголовья (вид спереди, чуть сверху): squash 0…1 — сплющена (ниже и шире), вмятина под головой."""
    x = BC_PILLOW[0] if x is None else x
    y = BC_PILLOW[1] if y is None else y
    s = clamp01(squash)
    w, h = 400 * (1 + .1 * s), 150 * (1 - .32 * s)
    pts = [(x - w, y + h * .5, 1), (x - w * 1.04, y - h * .1), (x - w * .9, y - h * .75), (x - w * .45, y - h * .95), (x, y - h * .9 + 10 * s),
           (x + w * .45, y - h * .95), (x + w * .9, y - h * .75), (x + w * 1.04, y - h * .1), (x + w, y + h * .5, 1), (x, y + h * .62)]
    inner = blob([(x - w * 1.1, y + h * .2), (x + w * 1.1, y + h * .2), (x + w * 1.1, y + h), (x - w * 1.1, y + h)], "#d9dde6")
    inner += blob(ellipse_pts(x + dx, y + h * .05, w * .5, h * (.42 + .25 * s), 22), "#e1e5ec")       # вмятина
    inner += line([(x - w * .8, y - h * .55), (x - w * .4, y - h * .78), (x - w * .05, y - h * .7)], 5, SHEET_HI, taper=.4, wmin=.4, seed=8951)
    for i, sx in enumerate((-1, 1)):    # складки от углов
        inner += line([(x + sx * w * .95, y - h * .6), (x + sx * w * .7, y - h * .3), (x + sx * w * .74, y + h * .1)], 3.0, "#c3c9d4", taper=.5,
                      wmin=.3, seed=8952 + i)
    return shape(pts, "#f3f4f7", inner, w=5.0, seed=8950)


def bed_close(t, mode="morning"):
    """Кровать крупно у стены (ракурс хука и петли). dict(bg, mattress, pillow(squash, dx), motes(t, u), front)."""
    o = ['<rect x="-2600" y="-1600" width="6000" height="6000" fill="#b9845a"/>', _wall_plain(-1400, -900, 2500, 760, MORNING, seed=1)]
    # полоса утреннего солнца формы окна (четыре стекла, крестовина-тень), чёткие края, на стене и заходит на изголовье
    o.append(_sun_quad((470, 60), (470, 50), (90, 560), SUN_WALL, SUN_WALL_HI, inset=.05))
    # изголовье: широкая доска на двух столбиках с шариками
    hb = lib.rrect(40, 330, 1040, 780, 40)
    inner = blob(rect_pts(40, 700, 1040, 780), WOOD_SH)
    for i in range(5):
        inner += line([(120 + 200 * i, 380), (130 + 200 * i, 700)], 3.0, WOOD_SH, taper=.3, wmin=.4, seed=8960 + i, op=.7)
    inner += line([(90, 372), (990, 368)], 7, WOOD_HI, taper=.3, wmin=.4, seed=8966)
    inner += _sun_quad((470, 60), (470, 50), (90, 560), lib.mix(WOOD, "#ffd890", .45), lib.mix(WOOD, "#ffe6b0", .6), inset=.05)
    o.append(shape(hb, WOOD, inner, w=5.0, seed=8961))
    for i, px in enumerate((40, 1040)):
        o.append(shape(rect_pts(px - 34, 300, px + 34, 900), WOOD, blob(rect_pts(px + 10, 300, px + 34, 900), WOOD_SH), w=4.6, seed=8970 + i))
        o.append(shape(ellipse_pts(px, 290, 44, 40, 18), WOOD_HI, blob(ellipse_pts(px + 12, 298, 30, 30, 14), WOOD), w=4.4, seed=8972 + i))
    # матрас и простыня: дальний край BC_SHEET_Y, уходит к зрителю до низа кадра (вид вдоль кровати)
    mt = [(-700, 2500, 1), (-60, BC_SHEET_Y + 60), (40, BC_SHEET_Y, 1), (1040, BC_SHEET_Y, 1), (1140, BC_SHEET_Y + 60), (1780, 2500, 1)]
    g = lib.lin_grad([(0, "#dfe3ea", 1), (.35, SHEET, 1), (1, "#f7f8fa", 1)], 0, BC_SHEET_Y, 0, 1920, units="userSpaceOnUse")
    minner = f'<rect x="-800" y="{f(BC_SHEET_Y - 20)}" width="2700" height="1900" fill="url(#{g})"/>'
    for i, (a, b) in enumerate(((140, -300), (330, 60), (760, 1040), (930, 1400))):     # складки простыни, сходятся к изголовью
        minner += line([(a, BC_SHEET_Y + 60), ((a + b) / 2 + 14, 1300), (b, 1960)], 3.4, SHEET_SH, taper=.6, wmin=.25, seed=8980 + i, op=.8)
    # полоса солнца на простыне (продолжение окна, косо)
    minner += _sun_quad((620, 980), (460, 40), (160, 760), "#fbf2d8", "#fff8e8", inset=.05)
    o_m = shape(mt, SHEET, minner, w=5.0, seed=8985)

    def pillow(squash=0.0, dx=0.0):
        return bed_close_pillow(squash, dx)

    def mts(tt, u=1.0):
        return motes(tt, (500.0, 80.0, 1040.0, 900.0), 16, u, seed=1)
    return dict(bg="".join(o), mattress=o_m, pillow=pillow, motes=mts, front="")


# ═════════════════════════ кровать средним планом (s03, s06, s08) ═════════════════════════
def bed_mid(t, mode="morning"):
    """Кровать анфас у стены, окно с широким подоконником слева в глубине (кот), полоса солнца справа. dict(bg, bed, front)."""
    o = [_wall_plain(-600, -600, 1700, 1440, MORNING, seed=2)]
    o.append(_sun_quad((640, 180), (300, 30), (70, 520), SUN_WALL, SUN_WALL_HI, inset=.05))
    o.append(window(*BM_WIN, "day", t, seed=4, sway=.8, curtain="#5a8fae", sill=False))
    # широкий подоконник (кот сидит на нём)
    x0, y0, x1, y1 = BM_WIN
    o.append(shape(lib.rrect(x0 - 50, BM_SILL[1], x1 + 50, BM_SILL[1] + 34, 6), "#f1ebdd",
                   blob(rect_pts(x0 - 54, BM_SILL[1] + 20, x1 + 54, BM_SILL[1] + 38), "#cfc6b2"), w=3.6, seed=9001))
    # пол и плинтус
    o.append(shape(rect_pts(-600, 1400, 1700, 1446), "#f4eedf", blob(rect_pts(-600, 1434, 1700, 1446), "#d6ccb4"), w=3.4, seed=9002))
    gf = lib.lin_grad([(0, "#c8915c", 1), (1, "#b07a48", 1)], 0, 1446, 0, 2100, units="userSpaceOnUse")
    o.append(f'<rect x="-600" y="1446" width="2300" height="700" fill="url(#{gf})"/>')
    for k, y in enumerate((1500, 1580, 1690, 1830)):
        o.append(line([(-600, y), (1700, y)], w=3.0, color="#8a5b34", taper=0.0, wmin=1, seed=9010 + k, op=.55))
    o.append(_sun_quad((560, 1470), (420, 10), (140, 120), "#d9a66e", "#e2b37c", inset=.08))
    # кровать: изголовье за Димой, подушка, матрас с одеялом, передняя царга, ножки
    b = []
    b.append(shape(lib.rrect(300, 760, 1100, 1120, 30), WOOD, blob(rect_pts(300, 1060, 1100, 1120), WOOD_SH)
                   + line([(340, 800), (1060, 796)], 6, WOOD_HI, taper=.3, wmin=.4, seed=9021), w=4.6, seed=9020))
    b.append(shape(lib.rrect(260, 1040, 1180, 1160, 26), SHEET, blob(rect_pts(260, 1120, 1180, 1160), SHEET_SH), w=4.4, seed=9022))
    b.append(bed_close_pillow(0.0, 0.0, 860, 1050))
    b.append(shape(rect_pts(250, 1150, 1190, 1290), WOOD, blob(rect_pts(250, 1260, 1190, 1290), WOOD_SH)
                   + line([(280, 1180), (1160, 1178)], 5, WOOD_HI, taper=.3, wmin=.4, seed=9024), w=4.6, seed=9023))
    for i, lx in enumerate((280, 1160)):
        b.append(shape(rect_pts(lx - 22, 1290, lx + 22, 1440), WOOD_SH, "", w=3.6, seed=9025 + i))
    b.append(blob(ellipse_pts(720, 1446, 520, 18, 20), "#6e4a2c", .25))
    return dict(bg="".join(o), bed="".join(b), front="")


# ═════════════════════════ комната днём (s11–s13, s17, s21) ═════════════════════════
def _flag_drawing(x, y, col, icon, rot=0.0, seed=0):
    """Флажок-рисунок на стене: листок на кнопке, на нём флажок на древке со знаком (молния / клубок) — без букв."""
    o = shape(rect_pts(x - 95, y - 120, x + 95, y + 120), "#fbf8ef", blob(rect_pts(x + 70, y - 120, x + 95, y + 120), "#e9e3d2"), w=3.6, seed=9100 + seed)
    o += line([(x - 50, y + 95), (x - 46, y - 90)], 7, WOOD_SH, taper=.1, wmin=.8, seed=9101 + seed)
    fl = [(x - 46, y - 90, 1), (x + 70, y - 60), (x - 46, y - 10, 1)]
    o += shape(fl, col, "", w=3.6, seed=9102 + seed)
    if icon == "bolt":
        o += shape([(x + 2, y - 76, 1), (x - 16, y - 48, 1), (x - 2, y - 48, 1), (x - 12, y - 24, 1), (x + 14, y - 56, 1), (x, y - 56, 1)], "#ffffff", "", w=2.4,
                   seed=9103 + seed)
    else:
        o += shape(ellipse_pts(x - 4, y - 50, 18, 18, 14), "#ffffff", line([(x - 18, y - 56), (x + 8, y - 40)], 2.4, INK, seed=9104 + seed)
                   + line([(x - 14, y - 64), (x + 12, y - 48)], 2.4, INK, seed=9105 + seed), w=2.4, seed=9106 + seed)
        o += line([(x + 12, y - 40), (x + 30, y - 22), (x + 22, y - 6)], 3.0, "#ffffff", taper=.3, wmin=.4, seed=9107 + seed)
    o += shape(ellipse_pts(x, y - 108, 9, 9, 10), "#d9534a", "", w=2.2, seed=9108 + seed)
    return f'<g transform="rotate({rot} {f(x)} {f(y)})">{o}</g>'


def day_room(t):
    """Комната днём: три дела слева-справа от центра, кровать у стены дальше вправо. dict(bg, desk, stand, bed, front).
    Порядок: bg → desk → stand → bed → [предметы, Дима, кот] → front."""
    o = [wall_floor("day")]
    o.append(window(-560, 200, -120, 900, "day", t, seed=6, sway=.7, curtain="#5a8fae"))
    o.append(_sun_quad((-80, 300), (300, 30), (70, 640), "#f6e7bf", "#fbf0d2", inset=.05))
    o.append(shelf(460, 760, 560, "day", seed=4, t=t))
    o.append(rug(600, FL + 60, 420, 80, "day", seed=5))
    # окно над кроватью справа, чистая стена DR_CLEAN между флажками
    o.append(window(2420, 160, 2760, 560, "day", t, seed=7, sway=.6, curtain="#e0b04a"))
    for (fx, fy), col, ic, rot, sd in ((DR_FLAGS[0], "#e8b93a", "bolt", -4, 0), (DR_FLAGS[1], "#4f78b5", "yarn", 3, 20)):
        o.append(_flag_drawing(fx, fy, col, ic, rot, sd))
    # стол слева
    x0, x1, ty = DR_DESK
    d = [shape([(x0, ty, 1), (x0 + 24, ty - 90, 1), (x1 - 24, ty - 90, 1), (x1, ty, 1)], DESKW, blob(rect_pts(x0, ty - 10, x1, ty), DESKW_SH, .5),
               w=3.8, seed=9200)]
    d.append(shape(rect_pts(x0, ty, x1, ty + 34), DESKW_SH, "", w=3.6, seed=9201))
    for i, lx in enumerate((x0 + 30, x1 - 30)):
        d.append(shape([(lx - 13, ty + 34, 1), (lx + 13, ty + 34, 1), (lx + 10, FL, 1), (lx - 10, FL, 1)], DESKW, "", w=3.2, seed=9202 + i))
    d.append(blob(ellipse_pts((x0 + x1) / 2, FL + 4, (x1 - x0) / 2 + 20, 12, 18), "#6e4a2c", .3))
    # тумба справа
    sx0, sx1, sy = DR_STAND
    s = [shape([(sx0, sy, 1), (sx0 + 14, sy - 50, 1), (sx1 - 14, sy - 50, 1), (sx1, sy, 1)], WOOD_HI, "", w=3.6, seed=9210)]
    s.append(shape(rect_pts(sx0, sy, sx1, FL - 20), WOOD, blob(rect_pts(sx1 - 22, sy, sx1, FL - 20), WOOD_SH)
                   + line([(sx0 + 14, sy + 160), (sx1 - 14, sy + 160)], 3.0, WOOD_SH, taper=0, wmin=1, seed=9212)
                   + shape(lib.rrect((sx0 + sx1) / 2 - 24, sy + 70, (sx0 + sx1) / 2 + 24, sy + 84, 6), "#3a3d46", "", w=2.0, seed=9213), w=3.8, seed=9211))
    s.append(blob(ellipse_pts((sx0 + sx1) / 2, FL - 14, (sx1 - sx0) / 2 + 14, 9, 14), "#6e4a2c", .3))
    # кровать у стены справа (анфас, изголовье у стены)
    bx, by = DR_BED
    bt = DR_BED_TOP
    b = [shape(lib.rrect(bx - 520, bt - 330, bx + 520, bt + 40, 30), WOOD, line([(bx - 480, bt - 296), (bx + 480, bt - 300)], 6, WOOD_HI, taper=.3,
                                                                                    wmin=.4, seed=9221), w=4.6, seed=9220)]
    b.append(bed_close_pillow(0.0, 0.0, bx - 230, bt - 40))
    b.append(shape(lib.rrect(bx - 560, bt - 40, bx + 560, bt + 60, 24), "#e8634a", blob(rect_pts(bx - 560, bt + 30, bx + 560, bt + 60), "#b84a36")
                   + "".join(line([(bx - 480 + 160 * i, bt - 30), (bx - 470 + 160 * i, bt + 50)], 6, "#f6c06a", taper=.1, wmin=.8, seed=9230 + i)
                             for i in range(7)), w=4.4, seed=9222))
    b.append(shape(rect_pts(bx - 570, bt + 60, bx + 570, bt + 190), WOOD, blob(rect_pts(bx - 570, bt + 160, bx + 570, bt + 190), WOOD_SH), w=4.6, seed=9223))
    for i, lx in enumerate((bx - 540, bx + 540)):
        b.append(shape(rect_pts(lx - 22, bt + 190, lx + 22, by), WOOD_SH, "", w=3.6, seed=9224 + i))
    b.append(blob(ellipse_pts(bx, by + 4, 600, 16, 20), "#6e4a2c", .25))
    return dict(bg="".join(o), desk="".join(d), stand="".join(s), bed="".join(b), front="")


# ═════════════════════════ стол в три четверти (s16, s19, s20) ═════════════════════════
def desk34_scene(t):
    """Тот же стол, что у рилса 70 днём (Дима слева лицом вправо, ноутбук экраном к нему). Слои — как desk_scene."""
    return desk_scene(t, "day")


# ═════════════════════════ кухня днём (s09, s10, s18) ═════════════════════════
KS_PAL = dict(wall="#efe2c6", wall_sh="#ddcca8", wall_hi="#f6ecd6", wall_ln="#e2d4b6", tile="#f6f1e4", tile_ln="#d8cdb4", cab="#6fa3a0",
              cab_sh="#55827f", cab_hi="#8fc0bc")


def _side_chair(x, sy, k=1.0, face=1, seed=0):
    """Стул боком: спинка за тазом (face=1 — сидящий смотрит вправо, спинка слева). dict(back, seat)."""
    seat = sy + 24 * k
    bx = x - face * 120 * k
    back = shape([(bx - 12 * k, seat, 1), (bx + 12 * k, seat, 1), (bx + 6 * k * face, seat - 380 * k, 1), (bx - 18 * k * face, seat - 376 * k, 1)], WOOD,
                 "", w=3.4, seed=9300 + seed)
    back += shape(lib.rrect(bx - 26 * k, seat - 370 * k, bx + 26 * k, seat - 240 * k, 10 * k), WOOD_HI, "", w=3.2, seed=9301 + seed)
    xa, xb = sorted((bx, x + face * 170 * k))
    fr = [shape(lib.rrect(xa - 20 * k, seat - 6 * k, xb + 20 * k, seat + 26 * k, 8 * k), WOOD, blob(rect_pts(xa - 20 * k, seat + 16 * k, xb + 20 * k, seat + 26 * k),
                                                                                                    WOOD_SH), w=3.4, seed=9302 + seed)]
    for i, lx in enumerate((bx, x + face * 150 * k)):
        fr.append(shape([(lx - 10 * k, seat + 26 * k, 1), (lx + 10 * k, seat + 26 * k, 1), (lx + 8 * k, KS_FLOOR, 1), (lx - 8 * k, KS_FLOOR, 1)], WOOD,
                        "", w=3.0, seed=9303 + seed + i))
    return dict(back=back, seat="".join(fr))


def _sink(x, y, t=0.0):
    """Раковина в столешнице (вид спереди-сверху) и кран — без надписей."""
    o = shape(ellipse_pts(x, y + 8, 120, 20, 22), "#9aa4ae", blob(ellipse_pts(x, y + 12, 104, 13, 20), "#6f7a85"), w=3.2, seed=9320)
    o += line([(x + 70, y), (x + 70, y - 110), (x + 30, y - 132), (x - 4, y - 118)], 12, "#b8c0c8", taper=0, wmin=1, seed=9321)
    o += line([(x + 70, y), (x + 70, y - 110), (x + 30, y - 132), (x - 4, y - 118)], 4, "#e6eaee", taper=0, wmin=1, seed=9322)
    o += shape(lib.rrect(x + 56, y - 40, x + 84, y - 26, 5), "#8a939c", "", w=2.2, seed=9323)
    return o


def kitchen_scene(t, mode="day"):
    """Кухня днём: стена, плитка, окно с деревом, столешница с раковиной; стол анфас и два стула боком. dict(bg, chairs_back, table, front)."""
    m = KS_PAL
    o = [_wall_plain(-600, -600, 1700, 1440, m, seed=3)]
    # фартук из плитки за столешницей справа
    o.append(f'<rect x="560" y="640" width="1200" height="{f(940 - 640)}" fill="{m["tile"]}"/>')
    for k in range(0, 16):
        o.append(line([(560 + k * 76, 640), (560 + k * 76, 940)], 2.2, m["tile_ln"], taper=.02, wmin=.95, seed=9330 + k, op=.9))
    for k in range(1, 4):
        o.append(line([(560, 640 + k * 75), (1760, 640 + k * 75)], 2.2, m["tile_ln"], taper=.02, wmin=.95, seed=9350 + k, op=.9))
    o.append(window(70, 200, 470, 720, "day", t, seed=8, sway=1.0, curtain="#e9b96a"))
    o.append(_sun_quad((520, 230), (260, 30), (60, 380), SUN_WALL, SUN_WALL_HI, inset=.05))
    # верхние шкафы справа
    for i, (x0, x1) in enumerate(((620, 860), (870, 1110), (1120, 1360))):
        o.append(shape(rect_pts(x0, 160, x1, 560), m["cab"], blob(rect_pts(x1 - 24, 160, x1, 560), m["cab_sh"]) + blob(rect_pts(x0 + 16, 176, x0 + 26, 544),
                                                                                                                       m["cab_hi"]), w=4.0, seed=9360 + i))
        o.append(shape(lib.rrect(x0 + 24, 470, x0 + 38, 530, 6), "#c4ccd4", "", w=2.4, seed=9365 + i))
    # столешница с раковиной и нижние шкафы (за столом, справа)
    cy = 940.0
    for i, (x0, x1) in enumerate(((560, 820), (830, 1090), (1100, 1360))):
        o.append(shape(rect_pts(x0, cy + 30, x1, 1400), m["cab"], blob(rect_pts(x1 - 24, cy + 30, x1, 1400), m["cab_sh"]), w=4.0, seed=9370 + i))
        o.append(shape(lib.rrect(x0 + 100, cy + 70, x0 + 160, cy + 84, 6), "#c4ccd4", "", w=2.4, seed=9375 + i))
    o.append(shape(rect_pts(540, cy - 6, 1700, cy + 30), "#d8b07c", blob(rect_pts(540, cy + 16, 1700, cy + 30), "#b48a58"), w=3.8, seed=9380))
    o.append(_sink(900, cy, t))
    # пол
    o.append(shape(rect_pts(-600, 1400, 1700, 1446), "#f4eedf", blob(rect_pts(-600, 1434, 1700, 1446), "#d6ccb4"), w=3.4, seed=9390))
    gf = lib.lin_grad([(0, "#c8915c", 1), (1, "#b07a48", 1)], 0, 1446, 0, 2100, units="userSpaceOnUse")
    o.append(f'<rect x="-600" y="1446" width="2300" height="700" fill="url(#{gf})"/>')
    for k, y in enumerate((1500, 1580, 1690, 1830)):
        o.append(line([(-600, y), (1700, y)], w=3.0, color="#8a5b34", taper=0.0, wmin=1, seed=9391 + k, op=.55))
    cl = _side_chair(KS_SIT_L[0], KS_SIT_L[1], 1.0, 1, seed=0)
    cr = _side_chair(KS_SIT_R[0], KS_SIT_R[1], 1.0, -1, seed=10)
    # стол анфас между ними
    x0, x1, ty = KS_TABLE
    tb = [shape([(x0, ty, 1), (x0 + 20, ty - 90, 1), (x1 - 20, ty - 90, 1), (x1, ty, 1)], "#d8b07c", blob(rect_pts(x0, ty - 12, x1, ty), "#c79e6a", .6)
                + line([(x0 + 60, ty - 50), (x0 + 300, ty - 52)], 2.6, "#ecc995", taper=.4, wmin=.3, seed=9401), w=4.0, seed=9400)]
    tb.append(shape(rect_pts(x0, ty, x1, ty + 32), "#b48a58", "", w=3.8, seed=9402))
    for i, lx in enumerate((x0 + 36, x1 - 36)):
        tb.append(shape([(lx - 14, ty + 32, 1), (lx + 14, ty + 32, 1), (lx + 10, KS_FLOOR, 1), (lx - 10, KS_FLOOR, 1)], "#b48a58", "", w=3.2, seed=9403 + i))
    tb.append(blob(ellipse_pts((x0 + x1) / 2, KS_FLOOR + 4, (x1 - x0) / 2 + 30, 12, 18), "#6e4a2c", .3))
    return dict(bg="".join(o), chairs_back=cl["back"] + cr["back"], chair_seats=cl["seat"] + cr["seat"], table="".join(tb), front="")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# РИЛС 72 «СДВГ не существует» (группа C). Все места — в координатах кадра 1080×1920 при своей камере (cx, cy, s).
#
# КУХОННЫЙ СТОЛ КРУПНО ДНЁМ (хук s01):  kitchen_close(t) -> dict(bg, table, motes, front)
#     резкий белый свет: белая стена с плиткой, жёсткий прямоугольник солнца из окна (чёткие края, тень крестовины), стол
#     светлого дерева, к зрителю до низа кадра. Кот СИДИТ НА СТОЛЕ мордой к зрителю: лапы на линии KC_CAT (k≈KC_CAT_K),
#     телефон лежит перед ним KC_PHONE. Порядок: bg → table → [тень кота, телефон, кот] → motes → front.
#     CAM_KC=(540, 930, 1.05). motes(t, u) — пылинки в луче.
# НОЧЬ, ТОТ ЖЕ РАКУРС (петля s22):  fire_close(t, u=1) -> dict(bg, table, fire, motes, front)
#     то же место кота и предмета, но ночь у костра: тёмно-синее небо, силуэты елей, вместо стола — широкий пень (верх на той же
#     линии, что стол), костёр слева внизу за краем кадра (видны языки и искры у левого края), его свет — пятном на пне и
#     тёплой гранью справа налево. Порядок: bg → table → [кот, кубик] → fire → motes(искры) → front.
#
# ДНЁМ У КРЕСЛА-МЕШКА (s03–s05):  bag_room(t) -> dict(bg, front)
#     белая стена, большое окно слева с резким белым светом (полоса формы окна на стене и на полу, чёткие края), светлый пол,
#     ковёр. Кресло-мешок (props.bean_bag) ставит сцена: BB=(560, 1500) центр низа, k≈1; Дима в нём — таз ≈ BB_HIP.
#     BB_CAT=(900, 1500) кот на полу справа (лапы на линии), BB_TOWER=(220, 1500) низ башни листов (s05) слева у окна,
#     BB_PHONE_FLOOR=(760, 1520) где телефон ложится экраном вниз на пол. CAM_BB=(560, 960, 1.0), CAM_BB_NEAR=(600, 1000, 1.3).
#
# НОЧЬ У КОСТРА:  fire_scene(t, u=1.0, mode="wide") -> dict(sky, bg, ground, stones_back, fire, stones_front, log, front, cam, light)
#     один мир для s06–s21: небо и ели, земля, круг света вокруг огня (пятно по форме, мерцает, не мягкий овал), камни кругом,
#     бревно-сиденье слева, большое дерево справа с веткой над огнём. u — сила огня 0…1 (0 — тлеющая искра, тьма; 1 — пламя);
#     свет пятна, камней и ствола следует за u. Порядок: sky → bg → ground → stones_back → [кот за костром] → fire →
#     stones_front → log → [Дима на бревне, кот рядом, предметы] → front.  cam — камера режима (cx, cy, s) для lib.cam.
#     Огонь — props.campfire (группа A), пока его нет — временный огонь здесь же (_temp_fire).
#     FIRE=(640, 1330) центр основания огня; LOG=(120, 1360) центр бревна (длина ~520, верх ≈ LOG_TOP);
#     DIMA_LOG=(140, LOG_TOP) таз сидящего Димы (scale 1); CAT_FAR=(880, 1250) кот по ту сторону огня (k≈.45, спиной или
#     анфас); CAT_NEAR=(940, 1400) кот ближе к огню справа; STONE_SHADOW=(-60, 1080) большой камень за спиной Димы (тень
#     растёт на нём, s07; камень рисует bg, плоская грань обращена к огню; контур — stone_shadow_pts()); TOWER=(960, 1400) низ башни листов (s16–s17);
#     BRANCH=(780, 470) точка ветки над огнём, где висит мешок (s20–s21); SKY_CLEAN=(380, 180, 900, 560) — чистое небо без
#     звёзд и веток (рукописное «кот» s20). Режимы mode и их камеры FIRE_CAMS:
#        "wide"   (s06, s11) общий: огонь, бревно, камень, кот за огнём
#        "face"   (s07, s10) лицо Димы на бревне крупно, огонь внизу справа, камень с тенью за спиной
#        "smoke"  (s08, s09) вверх над огнём: дым на фоне неба, внизу пламя и макушка Димы
#        "tower"  (s16, s17) Дима стоит перед башней справа от огня
#        "laptop" (s18, s19) Дима сидит на бревне с ноутбуком, огонь справа
#        "branch" (s20, s21) кот близко у огня, над ним ветка с мешком
#     light(t, u) -> множитель мерцания 0.85…1.1 (для тёплой грани на героях). fire_tint(svg, t, u, k=1) — обернуть героя в
#     фильтр ночи у костра: тёплый, приглушённый, с мерцанием (контур туши остаётся тёмным, лица читаются).
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
CAM_KC = (540.0, 930.0, 1.05)
KC_TABLE_Y = 1040.0          # дальний край столешницы (у стены)
KC_CAT = (540.0, 1235.0)     # точка между задних лап кота на столе
KC_CAT_K = 3.05
KC_PHONE = (575.0, 1262.0)   # центр телефона на столе перед котом (phone_flat k≈1.35)
WHITE = dict(wall="#eef0ee", wall_hi="#f8f9f7", wall_sh="#dde1df", wall_ln="#e2e6e4")

BB = (560.0, 1500.0)
BB_HIP = (560.0, 1300.0)
BB_CAT = (900.0, 1500.0)
BB_TOWER = (220.0, 1500.0)
BB_PHONE_FLOOR = (760.0, 1520.0)
CAM_BB = (560.0, 960.0, 1.0)
CAM_BB_NEAR = (600.0, 1000.0, 1.3)

FIRE = (640.0, 1330.0)
LOG = (120.0, 1360.0)
LOG_TOP = 1300.0
DIMA_LOG = (140.0, LOG_TOP)
CAT_FAR = (880.0, 1250.0)
CAT_NEAR = (940.0, 1400.0)
STONE_SHADOW = (-60.0, 1080.0)
TOWER = (960.0, 1400.0)
BRANCH = (780.0, 470.0)
SKY_CLEAN = (380.0, 180.0, 900.0, 560.0)
HORIZON = 930.0
FIRE_CAMS = {"wide": (560.0, 1000.0, 1.0), "face": (200.0, 960.0, 1.75), "smoke": (640.0, 760.0, 1.15),
             "tower": (760.0, 980.0, 1.0), "laptop": (300.0, 1040.0, 1.4), "branch": (800.0, 900.0, 1.05)}
NIGHT = dict(sky0="#070c1d", sky1="#12204a", sky2="#22336a", tree="#070b16", tree_e="#16213c", ground="#141a2a",
             ground2="#1b2234", stone="#3a3f4f", stone_sh="#22263a", stone_lit="#b97a4e", log="#4a3324", log_sh="#2c1d14",
             log_lit="#c47e48", lit=("#2c2630", "#4a3428", "#704a2c", "#9a6634"))


def light(t, u=1.0):
    """Мерцание огня: множитель яркости 0.85…1.1 (несколько синусов разной частоты, не шум-дрожь)."""
    v = 1 + .05 * math.sin(t * 7.3) + .035 * math.sin(t * 12.9 + 1.3) + .02 * math.sin(t * 23.1 + .4)
    return 1 + (v - 1) * clamp01(u)


def fire_tint(svg, t, u=1.0, k=1.0):
    """Герой у ночного костра: приглушить и согреть цвета (матрица), сила мерцает. k — 0 день … 1 ночь у огня."""
    fl = light(t, u)
    a = clamp01(k)
    r = 1 - a * (1 - .78 * fl * (.55 + .45 * u))
    g = 1 - a * (1 - .56 * fl * (.55 + .45 * u))
    b = 1 - a * (1 - .5 * (.7 + .3 * u))
    br = a * .045 * u * fl
    fid = f"ft{int(r * 1000)}_{int(g * 1000)}_{int(b * 1000)}"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        lib.DEFS.append(f'<filter id="{fid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="'
                        f'{r:.3f} 0 0 0 {br:.3f} 0 {g:.3f} 0 0 {br * .5:.3f} 0 0 {b:.3f} 0 0 0 0 0 1 0"/></filter>')
    return f'<g filter="url(#{fid})">{svg}</g>'


def _jag(cx, cy, rx, ry, t, seed, n=40, amp=.06, speed=1.0):
    """Неровное пятно света: радиус с неровностями формы + медленное колыхание (мерцание края)."""
    r = rs(9700 + seed)
    ph = r.uniform(0, 6.3, 5)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + amp * (math.sin(3 * a + ph[0]) + .6 * math.sin(5 * a + ph[1] + t * 2.1 * speed) + .4 * math.sin(9 * a + ph[2] - t * 3.7 * speed)
                       + .3 * math.sin(14 * a + ph[3] + t * 6.0 * speed))
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


# ═════════════════════════ кухонный стол крупно (s01) ═════════════════════════
def _wall_light(x0, y0, x1, y1, pal, step=150.0):
    """Стена: вертикальный градиент и редкие швы обоев (простые штрихи — дёшево для большого холста)."""
    g = lib.lin_grad([(0, pal["wall_sh"], 1), (.4, pal["wall"], 1), (1, pal["wall_hi"], 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    d = "".join(f"M{f(x0 + 40 + i * step)} {f(y0)}L{f(x0 + 41.5 + i * step)} {f(y1)}" for i in range(int((x1 - x0) // step) + 1))
    return (f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="url(#{g})"/>'
            f'<path d="{d}" stroke="{pal["wall_ln"]}" stroke-width="1.8" opacity=".5" fill="none"/>')


def _tiles(x0, y0, x1, y1, s=86.0, col="#dfe4e2", seed=0):
    """Плитка: светлая заливка и сетка швов простыми штрихами (на плитке нет букв и рисунков)."""
    d = "".join(f"M{f(x0)} {f(y0 + i * s)}L{f(x1)} {f(y0 + i * s + 2)}" for i in range(int((y1 - y0) // s) + 1))
    d += "".join(f"M{f(x0 + j * s)} {f(y0)}L{f(x0 + j * s + 1)} {f(y1)}" for j in range(int((x1 - x0) // s) + 2))
    return blob(rect_pts(x0, y0, x1, y1), "#f4f6f4") + f'<path d="{d}" stroke="{col}" stroke-width="2.4" fill="none"/>' 


def kitchen_close(t):
    """Стол крупно днём, резкий белый свет. dict(bg, table, motes(t, u), front)."""
    o = ['<rect x="-2600" y="-1600" width="6000" height="6000" fill="#c9cfcc"/>', _wall_light(-1400, -900, 2500, KC_TABLE_Y, WHITE)]
    o.append(_tiles(-300, 640, 1400, KC_TABLE_Y, col="#d6dcda", seed=1))
    # жёсткий прямоугольник солнца формы окна: белый, с тенью крестовины, косо через стену за котом
    o.append(_sun_quad((560, -120), (560, 70), (180, 900), "#fffef6", "#ffffff", inset=.05))
    # край окна слева: рама и белое небо-засвет (резкий свет)
    o.append(shape(rect_pts(-300, -200, 60, 560), "#ffffff", blob(rect_pts(30, -200, 60, 560), "#d9dedc"), w=5, seed=9611))
    o.append(shape(rect_pts(-300, 548, 90, 596), "#f1f3f1", blob(rect_pts(-300, 580, 90, 596), "#cfd5d3"), w=4, seed=9612))
    # столешница светлого дерева: дальний край KC_TABLE_Y, к зрителю шире до низа кадра (вид чуть сверху)
    tp = [(-1400, 2200, 1), (-1400, KC_TABLE_Y, 1), (2500, KC_TABLE_Y, 1), (2500, 2200, 1)]
    g = lib.lin_grad([(0, "#cfa678", 1), (.3, "#e2bd90", 1), (1, "#ecc99e", 1)], 0, KC_TABLE_Y, 0, 1920, units="userSpaceOnUse")
    inner = f'<rect x="-800" y="{f(KC_TABLE_Y - 20)}" width="2700" height="1300" fill="url(#{g})"/>'
    for i, (a, b) in enumerate(((60, -500), (300, -60), (620, 820), (900, 1500), (1080, 1900))):     # волокна дерева к зрителю
        inner += line([(a, KC_TABLE_Y + 8), ((a + b) / 2 + 20, 1400), (b, 2000)], 2.6, "#c49a6c", taper=.6, wmin=.25, seed=9620 + i, op=.75)
    # солнце на столе: жёсткая полоса продолжает окно (белее дерева)
    inner += _sun_quad((-40, KC_TABLE_Y + 30), (520, -10), (760, 780), "#f6dcb4", "#fbe8c8", inset=.05)
    inner += blob(rect_pts(-800, KC_TABLE_Y, 2000, KC_TABLE_Y + 14), "#b88e62")      # тень под стеной
    table = shape(tp, "#e2bd90", inner, w=5.2, seed=9625)

    def mts(tt, u=1.0):
        return motes(tt, (120.0, 40.0, 900.0, 1000.0), 18, u, seed=7)
    return dict(bg="".join(o), table=table, motes=mts, front="")


# ═════════════════════════ ночь, тот же ракурс (s22) ═════════════════════════
def _spruce(x, y, h, w, col, seed, edge=None, lit=0.0):
    """Ель силуэтом: ярусы-треугольники с зубчатым краем; edge — светлая грань справа (свет огня), lit 0…1."""
    r = rs(9800 + seed)
    pts = [(x, y - h, 1)]
    tiers = 6
    for i in range(1, tiers + 1):
        q = i / tiers
        yy = y - h + h * q * .92
        ww = w * (.18 + .82 * q) * r.uniform(.88, 1.08)
        pts.append((x + ww * .55, yy - h * .05))
        pts.append((x + ww, yy, 1))
    pts.append((x + w * .12, y))
    pts.append((x - w * .12, y))
    left = []
    for i in range(tiers, 0, -1):
        q = i / tiers
        yy = y - h + h * q * .92
        ww = w * (.18 + .82 * q) * r.uniform(.88, 1.08)
        left.append((x - ww, yy, 1))
        left.append((x - ww * .55, yy - h * .05))
    pts += left
    o = blob(pts, col)
    if edge and lit > .01:
        o += line([(x + 4, y - h * .9), (x + w * .5, y - h * .45), (x + w * .9, y - h * .05)], 6, edge, taper=.6, wmin=.2, seed=9810 + seed,
                  op=.55 * lit)
    return o


def _night_sky(x0, y0, x1, y1, seed=0, stars=True, clean=None):
    g = lib.lin_grad([(0, NIGHT["sky0"], 1), (.6, NIGHT["sky1"], 1), (1, NIGHT["sky2"], 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    o = [f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="url(#{g})"/>']
    if stars:
        r = rs(9900 + seed)
        for i in range(70):
            x, y = r.uniform(x0, x1), r.uniform(y0, y0 + (y1 - y0) * .8)
            if clean and clean[0] - 40 < x < clean[2] + 40 and clean[1] - 40 < y < clean[3] + 40:
                continue
            rr = r.uniform(1.6, 3.6)
            o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr)}" fill="#dfe6ff" opacity="{r.uniform(.4, .9):.2f}"/>')
    return "".join(o)


def _sparks(x, y, t, u, n=14, h=520.0, seed=0, k=1.0):
    """Искры вверх от огня: каждая — короткий тёплый штрих, летит по своей кривой, гаснет к верху."""
    if u <= .02:
        return ""
    r = rs(9950 + seed)
    o = []
    for i in range(n):
        per = r.uniform(.9, 1.6)
        ph = r.uniform(0, per)
        q = ((t + ph) % per) / per
        dx = r.uniform(-60, 60) * k + 40 * math.sin(q * 5 + i) * k
        yy = y - q * h * k * (.6 + .4 * u)
        xx = x + dx * (.3 + q)
        a = (1 - q) * u
        if a < .05:
            continue
        L = 10 * k
        o.append(line([(xx, yy), (xx - 3 * k, yy + L)], 4.2 * k, "#ffcf5a", taper=.5, wmin=.3, seed=9960 + i, op=a))
    return "".join(o)


def _temp_fire(x, y, k, u, t, seed=0):
    """Временный огонь (пока нет props.campfire группы A): поленья и языки пламени, u 0 — тлеющая искра."""
    o = []
    for i, (a, L) in enumerate(((-14, 150), (16, 150), (-2, 120))):
        p0 = (x - L * k * math.cos(math.radians(a)), y + 8 * k - L * k * math.sin(math.radians(a)) * .3)
        p1 = (x + L * k * math.cos(math.radians(a)), y + 8 * k + L * k * math.sin(math.radians(a)) * .3)
        from ink import band as _band
        o.append(shape(_band([p0, p1], 34 * k, 30 * k, step=6), NIGHT["log"], blob([(p0[0], p0[1]), (p1[0], p1[1]), (p1[0], p1[1] + 14 * k), (p0[0], p0[1] + 14 * k)],
                                                                                NIGHT["log_sh"]), w=4.2 * k, seed=9970 + i))
    if u < .3:
        e = .5 + .5 * math.sin(t * 6.1) * .5 + .25 * math.sin(t * 11.3)
        o.append(blob(ellipse_pts(x, y - 4 * k, 12 * k * (1 + .2 * e), 7 * k, 10), "#ff5a2a", .6 + .4 * e))
        o.append(blob(ellipse_pts(x, y - 5 * k, 5 * k, 3.5 * k, 8), "#ffd27a"))
    if u > .05:
        for j, (dx, hk) in enumerate(((-40, .7), (0, 1.0), (38, .78))):
            sw = 10 * math.sin(t * 8 + j * 2)
            hh = 230 * k * hk * u
            P = [(x + dx * k - 40 * k * u, y), (x + dx * k - 30 * k * u, y - hh * .4), (x + dx * k + sw * k, y - hh, 1), (x + dx * k + 30 * k * u, y - hh * .45),
                 (x + dx * k + 40 * k * u, y)]
            Q = [(x + dx * k - 20 * k * u, y), (x + dx * k + sw * .6 * k, y - hh * .62, 1), (x + dx * k + 20 * k * u, y)]
            o.append(shape(P, "#ff8a2a", blob(Q, "#ffd04a"), w=3.6 * k, seed=9980 + j, ink_color="#7a2a10"))
    return "".join(o)


def campfire(x, y, k=1.0, u=1.0, t=0.0, seed=0, stones=False):
    """Огонь: props.campfire группы A, если уже есть; иначе временный. Камни кольцом рисует fire_scene (они освещены огнём)."""
    try:
        import props
        if hasattr(props, "campfire"):
            return props.campfire(x, y, k, u, t, seed, stones=stones)
    except Exception:
        pass
    return _temp_fire(x, y, k, u, t, seed)


def fire_close(t, u=1.0):
    """Ракурс s01 ночью: тот же кадр, вместо стола пень, костёр слева внизу за краем, тёплый свет. dict(bg, table, fire, motes, front)."""
    fl = light(t, u)
    o = ['<rect x="-2600" y="-1600" width="6000" height="6000" fill="#0c1222"/>', _night_sky(-1400, -900, 2500, KC_TABLE_Y, seed=3)]
    for i, (x, h, w) in enumerate(((-120, 820, 300), (140, 640, 240), (930, 760, 280), (1150, 900, 320), (720, 520, 200))):
        o.append(_spruce(x, KC_TABLE_Y + 30, h, w, NIGHT["tree"] if i != 4 else NIGHT["tree_e"], 30 + i, "#c88a52", .7 * u * fl if x < 600 else 0))
    # земля за пнём
    o.append(blob(rect_pts(-1400, KC_TABLE_Y - 20, 2500, 2400), NIGHT["ground"]))
    o.append(blob(_jag(-60, KC_TABLE_Y + 120, 760 * (.8 + .2 * u), 120, t, 3, amp=.05), NIGHT["lit"][1] if u > .2 else NIGHT["ground2"]))
    # широкий пень вместо стола: круглый срез (кольца, трещина), кора по краю; кот сидит на срезе; свет огня слева
    cx, cy, rx, ry = 560.0, KC_TABLE_Y + 330, 820.0, 330.0
    bark = [(cx - rx, cy, 1), (cx - rx, cy + 900, 1), (cx + rx, cy + 900, 1), (cx + rx, cy, 1)]
    binner = blob(rect_pts(cx - rx - 20, cy, cx - rx * .3, cy + 900), lib.mix("#4a3324", "#b8743e", .55 * u * fl), .9)
    for i in range(9):
        bx = cx - rx + 40 + i * 190
        binner += line([(bx, cy + 60), (bx + 14, cy + 300), (bx - 6, cy + 700)], 5, "#22160e", taper=.5, wmin=.3, seed=9990 + i, op=.8)
    table = shape(bark, "#3e2a1c", binner, w=5.2, seed=9994)
    top = ellipse_pts(cx, cy, rx, ry, 40)
    g = lib.lin_grad([(0, lib.mix("#7a5636", "#d9995c", .6 * u * fl), 1), (.6, "#6a4a30", 1), (1, "#4e3622", 1)], 0, 0, 1, 0)
    inner = f'<rect x="{f(cx - rx - 10)}" y="{f(cy - ry - 10)}" width="{f(2 * rx + 20)}" height="{f(2 * ry + 20)}" fill="url(#{g})"/>'
    for i in range(1, 6):
        q = i / 6
        inner += f'<path d="{lib.ink_closed(ellipse_pts(cx + 20 * q, cy + 10 * q, rx * q, ry * q, 36), 2.4, seed=9980 + i)}" fill="#4a3020" opacity=".55"/>'
    inner += line([(cx + 60, cy - ry * .9), (cx + 30, cy - ry * .4), (cx + 70, cy + ry * .1)], 4, "#3a2416", taper=.5, wmin=.3, seed=9989)
    table += shape(top, "#6a4a30", inner, w=5.2, seed=9995)
    fire = campfire(-60, 1760, 1.9, u, t, seed=4, stones=True) + _sparks(-40, 1560, t, u, 16, 900, seed=2, k=1.6)

    def mts(tt, uu=1.0):
        return _sparks(-60, 1600, tt, uu * u, 10, 1400, seed=6, k=1.2)
    return dict(bg="".join(o), table=table, fire=fire, motes=mts, front="")


# ═════════════════════════ днём у кресла-мешка (s03–s05) ═════════════════════════
def bag_room(t):
    """Белая стена, окно слева с резким светом, светлый пол, ковёр. Кресло ставит сцена (props.bean_bag). dict(bg, front)."""
    o = ['<rect x="-2600" y="-1600" width="6000" height="6000" fill="#c9cfcc"/>', _wall_light(-1400, -900, 2600, 1440, WHITE)]
    o.append(window(-300, 200, 200, 1000, "day", t, seed=21, sway=.9, curtain="#9fb6c6"))
    o.append(_sun_quad((330, 260), (420, 40), (120, 760), "#fffef6", "#ffffff", inset=.05))
    o.append(shape(rect_pts(-1400, 1400, 2600, 1446), "#f7f8f6", blob(rect_pts(-1400, 1434, 2600, 1446), "#d6dbd9"), w=3.4, seed=9701))
    gf = lib.lin_grad([(0, "#d8c4a4", 1), (1, "#c8b08a", 1)], 0, 1446, 0, 2100, units="userSpaceOnUse")
    o.append(f'<rect x="-1400" y="1446" width="4000" height="1200" fill="url(#{gf})"/>')
    o.append('<path d="' + "".join(f"M-1400 {y}L2600 {y + 3}" for y in (1500, 1580, 1690, 1830)) + '" stroke="#a88e6a" stroke-width="3" opacity=".55" fill="none"/>')
    o.append(_sun_quad((120, 1460), (520, 20), (300, 140), "#f2e6cf", "#fbf3e2", inset=.08))
    o.append(rug(620, 1560, 430, 70, "day", seed=5))
    return dict(bg="".join(o), front="")


# ═════════════════════════ ночь у костра (s06–s21) ═════════════════════════
def _stone(x, y, w, h, t, u, fl, seed, side=0.0):
    """Камень: тёмный, освещённый бок к огню (side — где огонь по x: <0 слева, >0 справа)."""
    r = rs(9500 + seed)
    pts = [(x - w, y), (x - w * .9, y - h * .6), (x - w * .4, y - h * r.uniform(.9, 1.05)), (x + w * .3, y - h), (x + w * .9, y - h * .55), (x + w, y)]
    lit = lib.mix(NIGHT["stone"], NIGHT["stone_lit"], clamp01(.85 * u * fl))
    s = 1 if side > 0 else -1
    inner = blob([(x + s * w * .1, y - h * 1.1), (x + s * w * 1.1, y - h * .7), (x + s * w * 1.1, y + 4), (x + s * w * .2, y + 4)], lit, .9)
    inner += blob([(x - s * w * 1.1, y - h * .2), (x - s * w * .3, y - h * .1), (x - s * w * .2, y + 4), (x - s * w * 1.1, y + 4)], NIGHT["stone_sh"])
    return shape(pts, NIGHT["stone"], inner, w=4.4, seed=9520 + seed)


def stone_shadow_pts():
    """Контур большого камня за спиной Димы (для клипа тени на нём, s07)."""
    sx, sy = STONE_SHADOW
    return [(sx - 330, HORIZON + 420), (sx - 300, sy - 160), (sx - 120, sy - 300), (sx + 160, sy - 320), (sx + 300, sy - 200), (sx + 340, HORIZON + 420)]


def fire_scene(t, u=1.0, mode="wide"):
    """Ночь у костра. Возвращает слои в мировых координатах и камеру режима (см. шапку раздела)."""
    fl = light(t, u)
    sky = '<rect x="-2600" y="-1600" width="6000" height="6000" fill="#05080f"/>' + _night_sky(-1400, -1200, 2600, HORIZON + 40, seed=1, clean=SKY_CLEAN)
    b = []
    # дальние ели по горизонту
    r = rs(9400)
    x = -1400.0
    i = 0
    while x < 2600:
        h = r.uniform(260, 520)
        w = r.uniform(110, 180)
        b.append(_spruce(x, HORIZON + 20, h, w, NIGHT["tree_e"] if i % 3 else NIGHT["tree"], 100 + i))
        x += r.uniform(110, 190)
        i += 1
    # ближние ели слева и справа (тёплая грань от огня)
    for j, (x, h, w) in enumerate(((-560, 1100, 360), (-260, 900, 300), (1350, 1000, 340), (1650, 1200, 380))):
        b.append(_spruce(x, HORIZON + 140, h, w, NIGHT["tree"], 200 + j, "#c88a52", .6 * u * fl))
    # большое дерево справа: ствол и ветка над огнём (мешок висит в BRANCH)
    from ink import band as _band
    trunk = _band([(1080, HORIZON + 260), (1060, 700), (1070, 200), (1090, -300)], 120, 90, step=8)
    tinner = blob([(1000, 1300), (1040, 1300), (1030, -300), (990, -300)], lib.mix(NIGHT["log"], NIGHT["log_lit"], .7 * u * fl), .9)
    b.append(shape(trunk, NIGHT["log_sh"], tinner, w=5, seed=9411))
    br = _band([(1060, 420), (900, 450), (BRANCH[0], BRANCH[1]), (520, 500), (420, 530)], 46, 14, step=6)
    b.append(shape(br, NIGHT["log_sh"], blob([(1060, 440), (420, 545), (420, 560), (1060, 470)], lib.mix(NIGHT["log"], NIGHT["log_lit"], .5 * u * fl), .8),
                   w=4.2, seed=9412))
    for k_, (a, c) in enumerate((((860, 455), (820, 380)), ((620, 490), (590, 430)))):        # сучки
        b.append(line([a, c], 9, NIGHT["log_sh"], taper=.5, wmin=.3, seed=9413 + k_))
    # большой камень за спиной Димы (на нём растёт тень, s07)
    sx, sy = STONE_SHADOW
    sp = stone_shadow_pts()
    lit = lib.mix(NIGHT["stone"], "#8a6248", clamp01(.75 * u * fl))
    b.append(shape(sp, NIGHT["stone"], blob([(sx - 120, sy - 300), (sx + 160, sy - 320), (sx + 300, sy - 200), (sx + 340, HORIZON + 420), (sx - 200, HORIZON + 420),
                                             (sx - 260, sy - 120)], lit, .95), w=5, seed=9420))
    # земля и круг света: пятна по форме, края колышутся
    g = [blob(rect_pts(-1400, HORIZON, 2600, 2600), NIGHT["ground"])]
    g.append(blob(_jag(FIRE[0], FIRE[1] + 40, 1150, 330, t, 1, amp=.04, speed=.6), NIGHT["ground2"]))
    if u > .02:
        for j, (rx, ry, col) in enumerate(((900, 260, NIGHT["lit"][0]), (650, 190, NIGHT["lit"][1]), (420, 125, NIGHT["lit"][2]), (220, 66, NIGHT["lit"][3]))):
            q = clamp01(u * 1.4 - j * .18)
            if q <= .01:
                continue
            g.append(blob(_jag(FIRE[0], FIRE[1] + 10, rx * (.55 + .45 * q) * fl, ry * (.55 + .45 * q) * fl, t, 10 + j, amp=.07, speed=1.4)
                          , col, .5 + .5 * q))
    for j in range(9):      # травинки на краю света
        gx = -300 + j * 170 + 40 * math.sin(j * 7)
        g.append(line([(gx, 1560), (gx + 8, 1520), (gx + 14, 1500)], 4, "#2a3348", taper=.5, wmin=.3, seed=9430 + j))
    # камни кругом огня: задние (до огня) и передние (после)
    back, front = [], []
    for j in range(9):
        a = math.pi * (j / 9) * 2 + .3
        cx, cy = FIRE[0] + 210 * math.cos(a), FIRE[1] + 40 + 62 * math.sin(a)
        st = _stone(cx, cy, 46 - 6 * (j % 2), 38 + 6 * (j % 3), t, u, fl, j, side=FIRE[0] - cx)
        (front if math.sin(a) > 0 else back).append((cy, st))
    stones_back = "".join(s for _, s in sorted(back))
    stones_front = "".join(s for _, s in sorted(front))
    # бревно-сиденье слева: срез к огню светлее
    lx, ly = LOG
    lp = _band([(lx - 280, ly + 10), (lx, ly), (lx + 260, ly - 14)], 92, 84, step=8)
    linner = blob([(lx - 300, ly - 50), (lx + 280, ly - 64), (lx + 280, ly - 30), (lx - 300, ly - 16)], lib.mix(NIGHT["log"], NIGHT["log_lit"], .6 * u * fl), .9)
    linner += blob([(lx - 300, ly + 20), (lx + 280, ly + 6), (lx + 280, ly + 60), (lx - 300, ly + 60)], NIGHT["log_sh"])
    for j in range(4):
        linner += line([(lx - 240 + 130 * j, ly - 30), (lx - 200 + 130 * j, ly - 26)], 2.4, "#2a1a10", seed=9440 + j, op=.7)
    log = shape(lp, NIGHT["log"], linner, w=5, seed=9445)
    log += shape(ellipse_pts(lx + 262, ly - 14, 22, 44, 14), lib.mix("#7a5a3c", "#e0a060", .6 * u * fl),
                 line([(lx + 262, ly - 30), (lx + 256, ly - 14), (lx + 264, ly + 2)], 2.2, "#4a3020", seed=9446), w=4, seed=9447)
    fire = campfire(FIRE[0], FIRE[1], 1.0, u, t, seed=1) + _sparks(FIRE[0], FIRE[1] - 60, t, u, 12, 600, seed=1)
    return dict(sky=sky, bg="".join(b), ground="".join(g), stones_back=stones_back, fire=fire, stones_front=stones_front, log=log, front="",
                cam=FIRE_CAMS.get(mode, FIRE_CAMS["wide"]), light=fl)
