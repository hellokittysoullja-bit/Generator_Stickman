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
    M = _hall_pal(mode)
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
    if edge and lit > .01:      # тёплый отсвет огня по нижним ярусам (по краю силуэта, не штрих поперёк)
        o += blob([(x + w * .55, y - h * .2), (x + w, y, 1), (x + w * .1, y)], edge, .18 * lit)
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
    # большой камень за спиной Димы (на нём растёт тень, s07)
    sx, sy = STONE_SHADOW
    sp = stone_shadow_pts()
    lit = lib.mix(NIGHT["stone"], "#8a6248", clamp01(.75 * u * fl))
    g.append(shape(sp, NIGHT["stone"], blob([(sx - 120, sy - 300), (sx + 160, sy - 320), (sx + 300, sy - 200), (sx + 340, HORIZON + 420), (sx - 200, HORIZON + 420),
                                             (sx - 260, sy - 120)], lit, .95), w=5, seed=9420))
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


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# РИЛС 73 «Ты сам виноват» (группа C): холодная дневная комната с пробковой доской, спальня ночью (луна → ночник), пульс сердца.
# Одна комната Димы, мир 1080×1920 по ширине −2600…2600 (стена анфас, пол FL73):
#   стол с ноутбуком  DESK73_X (−2500…−1700), пробковая доска BOARD73 (−1350…−550), окно со шторами WIN73 (−250…350),
#   кровать сбоку BED73 (изголовье справа, подушка у x≈1880), тумбочка с ночником NSTAND73 справа от изголовья, часы CLOCK73 над кроватью.
# Днём (cold_room) — та же стена в холодном серо-голубом свете; ночью (bedroom) — тёмно-синяя луна или тёплый ночник.
# Букв и цифр нет нигде (часы — props.clock без цифр, карточки и конверты пустые — их рисует сцена из props).
#
#   cold_room(t, mode="close"|"wide", curtain_u=0.0) -> dict:
#       bg      — стена, доска (без предметов на ней), окно со шторами, пол; класть первым
#       light   — полоса света из окна на полу (сужается по curtain_u до прожектора на STAND73); класть после bg, до Димы
#       dim     — затемнение комнаты вне луча (растёт с curtain_u); класть ПОСЛЕ людей и кота (они тоже темнеют вне луча)
#       front   — пусто (резерв); cam — камера режима (CAM73_BOARD_CLOSE / CAM73_COLD_WIDE)
#       Предметы на доске (конверт на кнопке BOARD73_PIN, паутина BOARD73_WEB, паучок) — props группы A, ставит сцена.
#   bedroom(t, light="moon"|"lamp"|число 0…1, mode, lamp_u=None) -> dict(bg, light, front, cam, k):
#       light 0 — луна (тёмно-синий, лунный прямоугольник окна на стене и полу), 1 — ночник (тёплое пятно ФОРМЫ АБАЖУРА с
#       мерцанием края, без огромных овалов); число — переход (s09: щелчок ночника за 4–5 кадров).
#       mode — ракурс и его камера cam:
#         "foot"  — s06/s07: ОТДЕЛЬНАЯ композиция в координатах кадра (камера (540, 960, 1)): вид от изножья кровати — потолок
#                   сверху (CEIL73_Y), стена с часами CLOCK_F (центр, r), изголовье, подушка, голова Димы в FOOT_HEAD, одеяло
#                   к зрителю (слой front — КЛАСТЬ ПОСЛЕ головы и плеч Димы). Тень судьи — на потолке/стене в FOOT_SHADOW.
#                   Камеры: CAM73_CLOCK (часы крупно), CAM73_FOOT (кровать, Дима ≥ 45 %), CAM73_PILLOW (лицо на подушке).
#         "wide"  — s08: кровать и окно с луной общим планом (CAM73_BED_WIDE); "bed" — s09–s11 кровать ближе (CAM73_BED);
#         "cam"   — s12: тумбочка с ночником крупно у камеры (CAM73_NSTAND; чашку ставят на NSTAND73_TOP);
#         "board" — s13/s15/s16/s17: доска на стене (CAM73_BOARD_MID, CAM73_BOARD_CLOSE); "desk" — s14 стол (CAM73_DESK).
#       bg — всё за людьми; front — передний план (одеяло в "foot", иначе пусто); k — сила тепла 0…1 (для подкраски кота: warm_tint).
#   board_close(t, light=…) — ракурс хука и петли: доска крупно (BOARD73_PIN в кадре сверху), стена без окна; dict(bg, light, cam).
#   heart_pulse(t, t_beat, amp=1.0) -> SVG поверх кадра (координаты кадра): «удар сердца» — двойной толчок (тук-тук: t_beat и
#       t_beat + 0.2), виньетка темнеет к краям и весь кадр коротко проседает в свете (до 15 % · amp). heart_k(t, t_beat) — сила 0…1
#       (для «дыхания» камеры и дёрганья предметов).
#   warm_tint(svg, k) / cold_tint(svg, k) — подкрасить героя под свет (матрица цвета; тушь остаётся тушью).
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
FL73 = 1560.0
WALL73_Y = 1440.0
BOARD73 = (-1350.0, 300.0, -550.0, 960.0)        # пробковая доска (x0, y0, x1, y1) на стене
BOARD73_PIN = (-860.0, 470.0)                    # кнопка, на которой висит пыльный конверт (хук, s13, петля — карточка)
BOARD73_WEB = (-1350.0, 300.0)                   # угол доски, где паутина (верх-лево)
BOARD73_CLEAN = (-1300.0, 40.0, -600.0, 260.0)   # чистая стена над доской (s15: рукописное «кот» — за буквами ничего)
WIN73 = (-250.0, 220.0, 350.0, 1020.0)           # окно со шторами (рама)
STAND73 = (-520.0, FL73)                         # где стоит Дима (s03): между доской и окном, свет окна падает на него
BED73 = (1300.0, FL73, 1.9)                      # props.bed(x, y, k): ножки на FL, изголовье слева… — свою кровать рисуем здесь (см. _bed73)
BED73_TOP = 1170.0                               # верх матраса
BED73_X = (640.0, 1980.0)                        # матрас от изножья (слева) до изголовья (справа)
BED73_PILLOW = (1860.0, 1150.0)                  # подушка (голова Димы лёжа) — у изголовья справа
NSTAND73 = (2060.0, 2300.0)                      # тумбочка x0..x1 справа от изголовья
NSTAND73_TOP = 1200.0                            # верх тумбочки (чашка, ночник — дном сюда)
LAMP73 = (2200.0, NSTAND73_TOP)                  # ночник: дно абажурной лампы на тумбочке
CLOCK73 = (1250.0, 430.0, 110.0)                 # часы на стене над кроватью (центр, r)
DESK73_X = (-2500.0, -1700.0)                    # стол у стены слева от доски (s14)
DESK73_TOP = 1000.0
CEIL73_Y = -80.0                                 # линия потолка (выше — потолок)
CAM73_BOARD_CLOSE = (-860.0, 760.0, 1.95)        # хук и петля: кнопка с конвертом сверху, морда кота перед доской снизу
CAM73_BOARD_MID = (-950.0, 860.0, 1.15)          # доска средним планом (s13, s15, s16)
CAM73_COLD_WIDE = (-420.0, 980.0, .9)            # s03: Дима посреди комнаты, доска слева, окно справа
CAM73_BED_WIDE = (900.0, 1000.0, .78)            # s08: кровать и окно с луной
CAM73_BED = (1450.0, 1080.0, 1.12)               # s09–s11: кровать с котом
CAM73_NSTAND = (2150.0, 1060.0, 1.5)             # s12: тумбочка у камеры, кот садится рядом
CAM73_DESK = (-2100.0, 980.0, 1.2)               # s14: стол с ноутбуком
# ракурс «от изножья» (s06, s07) — координаты кадра
CLOCK_F = (540.0, 330.0, 120.0)
FOOT_HEAD = (540.0, 1060.0)                      # центр головы Димы на подушке (лицо вверх)
FOOT_SHADOW = (540.0, 150.0)                     # где на потолке/верху стены встаёт тень кота-судьи
FOOT_LAMP = (985.0, 960.0)                       # ночник на тумбочке справа от изголовья (s06–s07 выключен)
CAM73_CLOCK = (540.0, 360.0, 2.1)
CAM73_FOOT = (540.0, 900.0, 1.0)
CAM73_PILLOW = (540.0, 1010.0, 1.75)

PAL73 = {
    "cold": dict(wall="#b5bfc9", wall_hi="#c6cfd7", wall_sh="#9aa6b2", wall_ln="#a6b0bb", base="#d0d7de", base_sh="#a9b3bd",
                 floor="#958a82", floor_b="#7c736d", floor_ln="#625a55", shadow="#4f5866", ceil="#c2cad2", frame="#e3e7ea",
                 cork="#b49a78", cork_sh="#96805f", cork_dot="#8a7354", wood="#8f7a68", wood_sh="#6e5c4e", sheet="#d9dde2", sheet_sh="#b6bec7",
                 sky=("#a9b8c6", "#c3ced8", "#dde3e8"), cur="#7f93a6"),
    "moon": dict(wall="#2a3354", wall_hi="#333d63", wall_sh="#1f2744", wall_ln="#252e4c", base="#384266", base_sh="#29314f",
                 floor="#262a3e", floor_b="#1c1f31", floor_ln="#141626", shadow="#0d1120", ceil="#222a48", frame="#55608a",
                 cork="#4a4652", cork_sh="#3a3744", cork_dot="#2e2c38", wood="#3d3a4e", wood_sh="#2b2a3a", sheet="#5f6a92", sheet_sh="#47507a",
                 sky=("#0a1030", "#16225a", "#2a3a7a"), cur="#3a4670"),
    "lamp": dict(wall="#7a5c55", wall_hi="#91705f", wall_sh="#5a4347", wall_ln="#6c514e", base="#9a7a68", base_sh="#76594e",
                 floor="#6a4630", floor_b="#4e3424", floor_ln="#36241a", shadow="#2a1c18", ceil="#6a4e4c", frame="#c8a888",
                 cork="#b98a5a", cork_sh="#966a42", cork_dot="#7e5634", wood="#9a6a42", wood_sh="#6e4a2c", sheet="#e8cfa6", sheet_sh="#c4a47e",
                 sky=("#0c1232", "#1a2660", "#2e3e80"), cur="#a8584a"),
}
PAL73["moon"]["_u"], PAL73["lamp"]["_u"] = 0.0, 1.0
LAMP_HOT, LAMP_GLOW = "#ffe2a0", "#ffc870"


def _pal73(light):
    """Палитра: "cold" — день; "moon" (0) … "lamp" (1) — ночь; число — смесь луна → ночник."""
    if isinstance(light, str):
        return PAL73[light], (1.0 if light == "lamp" else 0.0)
    u = clamp01(float(light))
    if u <= 0.0 or u >= 1.0:
        return PAL73["lamp" if u >= 1 else "moon"], u
    a, b = PAL73["moon"], PAL73["lamp"]
    out = {"_u": u}
    for k_, v in a.items():
        if k_ == "_u":
            continue
        w_ = b[k_]
        out[k_] = lib.mix(v, w_, u) if isinstance(v, str) else tuple(lib.mix(x, y, u) for x, y in zip(v, w_))
    return out, u


def _wall73(P, x0=-2700.0, x1=2700.0, ceil=True):
    o = []
    g = lib.lin_grad([(0, P["wall_sh"], 1), (.3, P["wall"], 1), (1, P["wall_hi"], 1)], 0, CEIL73_Y, 0, WALL73_Y, units="userSpaceOnUse")
    o.append(f'<rect x="{f(x0)}" y="{f(CEIL73_Y)}" width="{f(x1 - x0)}" height="{f(WALL73_Y - CEIL73_Y)}" fill="url(#{g})"/>')
    if ceil:
        o.append(f'<rect x="{f(x0)}" y="-1400" width="{f(x1 - x0)}" height="{f(CEIL73_Y + 1400)}" fill="{P["ceil"]}"/>')
        o.append(blob(rect_pts(x0, CEIL73_Y - 4, x1, CEIL73_Y + 22), P["base"]) + line([(x0, CEIL73_Y + 22), (x1, CEIL73_Y + 22)], 3.2, INK, taper=0, wmin=1, seed=7301))
    d = "".join(f"M{f(x0 + 60 + i * 150)} {f(CEIL73_Y + 24)}L{f(x0 + 61.5 + i * 150)} {f(WALL73_Y - 40)}" for i in range(int((x1 - x0) // 150) + 1))
    o.append(f'<path d="{d}" stroke="{P["wall_ln"]}" stroke-width="1.8" opacity=".55" fill="none"/>')
    o.append(shape(rect_pts(x0, WALL73_Y - 46, x1, WALL73_Y + 6), P["base"], blob(rect_pts(x0, WALL73_Y - 8, x1, WALL73_Y + 6), P["base_sh"]), w=3.4, seed=7302))
    gf = lib.lin_grad([(0, P["floor"], 1), (1, P["floor_b"], 1)], 0, WALL73_Y, 0, 2600, units="userSpaceOnUse")
    o.append(f'<rect x="{f(x0)}" y="{f(WALL73_Y + 6)}" width="{f(x1 - x0)}" height="{f(2600 - WALL73_Y)}" fill="url(#{gf})"/>')
    ys = [WALL73_Y + 6, 1510, 1600, 1720, 1880, 2080, 2340, 2600]
    d = "".join(f"M{f(x0)} {f(y)}L{f(x1)} {f(y + 2)}" for y in ys[1:-1])
    r = rs(7303)
    for ya, yb in zip(ys[:-1], ys[1:]):
        for _ in range(10):
            x = r.uniform(x0, x1)
            d += f"M{f(x)} {f(ya)}L{f(x + r.uniform(-4, 4))} {f(yb)}"
    o.append(f'<path d="{d}" stroke="{P["floor_ln"]}" stroke-width="3" opacity=".6" fill="none"/>')
    return "".join(o)


def cork_board73(x0, y0, x1, y1, P, seed=0):
    """Пробковая доска: props.cork_board группы A (центр, w, h), подкрашенная под свет палитры P; иначе — своя рамка с пробкой."""
    try:
        import props
        if hasattr(props, "cork_board"):
            return light_tint(props.cork_board((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, seed), P)
    except Exception:
        pass
    sd = 7310 + seed
    fr = 34
    o = [blob(rect_pts(x0 + 14, y0 + 18, x1 + 14, y1 + 22), P["shadow"], .35)]
    o.append(shape(rect_pts(x0, y0, x1, y1), P["wood"], blob(rect_pts(x0, y1 - 14, x1, y1), P["wood_sh"]) + blob(rect_pts(x1 - 14, y0, x1, y1), P["wood_sh"]),
                   w=4.6, seed=sd))
    r = rs(sd)
    inner = blob(rect_pts(x0 + fr, y0 + fr, x1 - fr, y0 + fr + 22), P["cork_sh"], .7)
    d = ""
    for _ in range(int((x1 - x0) * (y1 - y0) / 1800)):
        x, y = r.uniform(x0 + fr, x1 - fr), r.uniform(y0 + fr, y1 - fr)
        rr = r.uniform(2.0, 4.6)
        d += f"M{f(x - rr)} {f(y)}a{f(rr)} {f(rr * .7)} 0 1 0 {f(2 * rr)} 0a{f(rr)} {f(rr * .7)} 0 1 0 {f(-2 * rr)} 0"
    inner += f'<path d="{d}" fill="{P["cork_dot"]}" opacity=".55"/>'
    o.append(shape(rect_pts(x0 + fr, y0 + fr, x1 - fr, y1 - fr), P["cork"], inner, w=3.4, seed=sd + 1))
    return "".join(o)


def _curtains73(x0, y0, x1, y1, u, col, t, seed=0):
    """Две шторы на карнизе: u 0 — раздвинуты у краёв окна, 1 — сведены, между ними щель ~6 % ширины. Складки едут со шторой."""
    sd = 7330 + seed
    w = x1 - x0
    xm = (x0 + x1) / 2
    gap = w * .5 + (w * .035 - w * .5) * smooth01(u)     # полуширина открытой части
    o = []
    sh = lib.mul(col, (.78, .78, .8))
    for sgn in (-1, 1):
        outer = x0 - 70 if sgn < 0 else x1 + 70
        inner_x = xm + sgn * gap
        sw = 4 * math.sin(t * 1.3 + sgn) * (1 - u)
        pts = [(outer, y0 - 30, 1), (inner_x - sgn * 4, y0 - 30, 1), (inner_x + sw, (y0 + y1) / 2), (inner_x - sgn * 10 + sw * 1.5, y1 + 60, 1),
               (outer, y1 + 60, 1)]
        folds = ""
        n = 4
        for i in range(n):
            q = (i + .5) / n
            fx = outer + (inner_x - outer) * q
            folds += line([(fx, y0 - 20), (fx + sw * q, (y0 + y1) / 2), (fx + sw * 1.4 * q, y1 + 50)], 6, sh, taper=.4, wmin=.3, seed=sd + i + 10 * (sgn + 1))
        folds += blob([(inner_x - sgn * 26, y0 - 30), (inner_x, y0 - 30), (inner_x + sw, (y0 + y1) / 2), (inner_x - sgn * 30 + sw, y1 + 60)], sh, .7)
        o.append(shape(pts, col, folds, w=3.6, seed=sd + 5 + sgn))
    o.append(shape(lib.rrect(x0 - 110, y0 - 50, x1 + 110, y0 - 30, 6), "#5d5048", "", w=3.0, seed=sd + 20))
    return "".join(o), (xm - gap, xm + gap)


def _window73(P, light_u, t, curtain_u=0.0, moon_phase=1.0, day=False):
    """Окно WIN73: днём бледное серое небо (холодно, без солнца), ночью луна (moon_phase 0 — серп … 1 — полная). Шторы сводятся."""
    x0, y0, x1, y1 = WIN73
    fr = 18
    ix0, iy0, ix1, iy1 = x0 + fr, y0 + fr, x1 - fr, y1 - fr
    sky = P["sky"]
    g = lib.lin_grad([(0, sky[0], 1), (.6, sky[1], 1), (1, sky[2], 1)], 0, 0, 0, 1)
    inner = f'<path d="M{f(ix0 - 5)} {f(iy0 - 5)}H{f(ix1 + 5)}V{f(iy1 + 5)}H{f(ix0 - 5)}Z" fill="url(#{g})"/>'
    w, h = ix1 - ix0, iy1 - iy0
    if day:      # холодное пасмурное небо: длинные серые облака, силуэт крыш
        for j in range(3):
            cx = ix0 + ((j * 211 + t * 9) % (w + 200)) - 100
            cy = iy0 + h * (.14 + .13 * j)
            inner += blob([(cx - 140, cy + 10, 1), (cx - 90, cy - 18), (cx, cy - 26), (cx + 110, cy - 14), (cx + 150, cy + 10, 1)], "#e9edf0", .9)
        hb = iy1 - h * .26
        for j in range(4):
            bx0 = ix0 - 10 + j * w / 3.4
            inner += blob(rect_pts(bx0, hb + (j % 2) * 40, bx0 + w / 3.8, iy1 + 8), "#9aa6b1")
    else:
        r = rs(7340)
        for i in range(10):
            sx, sy = ix0 + 20 + r.uniform(0, w - 40), iy0 + 20 + r.uniform(0, h * .45)
            tw = .55 + .45 * math.sin(t * 2.2 + i * 1.7)
            inner += f'<circle cx="{f(sx)}" cy="{f(sy)}" r="{f(r.uniform(2, 3.6))}" fill="#e8ecff" opacity="{tw:.2f}"/>'
        mx, my, mr = ix0 + w * .62, iy0 + h * .22, w * .12
        inner += moon73(mx, my, mr, moon_phase, sky[1])
        hb = iy1 - h * .24
        for j in range(4):
            bx0 = ix0 - 10 + j * w / 3.4
            by = hb + (j % 2) * 40
            inner += blob(rect_pts(bx0, by, bx0 + w / 3.8, iy1 + 8), "#0b1030")
            if j % 2 == 0:
                inner += blob(rect_pts(bx0 + 30, by + 30, bx0 + 50, by + 52), "#d9b45a", .8)
    out = [shape(rect_pts(x0, y0, x1, y1), P["frame"], "", w=4.4, seed=7341)]
    out.append(shape(rect_pts(ix0, iy0, ix1, iy1), sky[1], inner, w=3.4, seed=7342))
    xm, ym = (x0 + x1) / 2, iy0 + h * .42
    out.append(blob(rect_pts(xm - 7, iy0, xm + 7, iy1), P["frame"]) + line([(xm - 7, iy0), (xm - 7, iy1)], 2.6, INK, seed=7343)
               + line([(xm + 7, iy0), (xm + 7, iy1)], 2.6, INK, seed=7344))
    out.append(blob(rect_pts(ix0, ym - 7, ix1, ym + 7), P["frame"]) + line([(ix0, ym - 7), (ix1, ym - 7)], 2.6, INK, seed=7345)
               + line([(ix0, ym + 7), (ix1, ym + 7)], 2.6, INK, seed=7346))
    out.append(shape(lib.rrect(x0 - 30, y1, x1 + 30, y1 + 24, 5), P["frame"], blob(rect_pts(x0 - 34, y1 + 13, x1 + 34, y1 + 28), P["base_sh"]), w=3.4, seed=7347))
    cur, gap = _curtains73(x0, y0, x1, y1, curtain_u, P["cur"], t)
    out.append(cur)
    return "".join(out), gap


def moon73(x, y, r, phase=1.0, sky="#16225a"):
    """Луна: phase 0 — тонкий серп, .5 — половина, 1 — полная (тень — круг цвета неба, наезжает справа)."""
    o = shape(ellipse_pts(x, y, r, r, 26), "#f6efc6", blob(ellipse_pts(x - r * .3, y + r * .25, r * .22, r * .18, 10), "#e2d9a8"), w=2.6, seed=7350)
    if phase < .98:
        off = r * 2.1 * phase if phase > .5 else r * (.35 + 1.3 * phase)
        if phase >= .5:      # «половина → полная»: тень уходит направо за край
            o += blob(ellipse_pts(x + r * .1 + off, y, r * 1.02, r * 1.02, 26), sky)
        else:
            o += blob(ellipse_pts(x + off, y - r * .05, r * .98, r * .98, 26), sky)
    return o


def _light_pool73(cx, cy, rx, ry, t, col, op, seed, flick=1.0):
    """Пятно света с чёткой неровной кромкой (два слоя: край и ядро), край колышется — не огромный мягкий овал."""
    return (blob(_jag(cx, cy, rx, ry, t * flick, seed, amp=.035, speed=.8), col, op * .55)
            + blob(_jag(cx, cy - ry * .05, rx * .62, ry * .62, t * flick, seed + 1, amp=.04, speed=1.1), col, op * .5))


def night_lamp73(x, y, k=1.0, on=1.0, t=0.0, P=None):
    """Ночник: props.night_lamp группы A, если есть; иначе — ножка, абажур-трапеция, свет ФОРМЫ абажура вверх и вниз (чёткие края)."""
    try:
        import props
        if hasattr(props, "night_lamp"):
            return props.night_lamp(x, y, k, on, t)
    except Exception:
        pass
    o = []
    on = clamp01(on)
    fl = light(t, on)
    if on > .01:      # конусы света формы абажура: вверх и вниз, ровные края, слегка мерцают
        a = .42 * on * fl
        o.append(blob([(x - 52 * k, y - 120 * k), (x + 52 * k, y - 120 * k), (x + 130 * k, y - 330 * k), (x - 130 * k, y - 330 * k)], LAMP_HOT, a * .55))
        o.append(blob([(x - 70 * k, y - 46 * k), (x + 70 * k, y - 46 * k), (x + 150 * k, y + 2 * k), (x - 150 * k, y + 2 * k)], LAMP_HOT, a))
    o.append(shape(ellipse_pts(x, y - 4 * k, 46 * k, 12 * k, 16), "#6e4a2c", "", w=3.4 * k, seed=7360))
    o.append(line([(x, y - 8 * k), (x + 2 * k, y - 60 * k)], 9 * k, "#6e4a2c", taper=0, wmin=1, seed=7361))
    shade = [(x - 46 * k, y - 120 * k, 1), (x + 46 * k, y - 120 * k, 1), (x + 72 * k, y - 50 * k, 1), (x - 72 * k, y - 50 * k, 1)]
    sc = lib.mix("#c9b49a", LAMP_HOT, on * .9)
    o.append(shape(shade, sc, blob([(x - 72 * k, y - 66 * k), (x + 72 * k, y - 66 * k), (x + 72 * k, y - 50 * k), (x - 72 * k, y - 50 * k)],
                                   lib.mix("#a8957c", "#ffd27a", on), .9), w=3.8 * k, seed=7362))
    if on > .01:
        o.append(blob(ellipse_pts(x, y - 52 * k, 50 * k, 7 * k, 14), "#fff6d8", on))
    return "".join(o)


def _bed73(P, seed=0):
    """Кровать сбоку у стены: изголовье справа (у тумбочки), низкая спинка слева, матрас, простыня. Постель (подушку, одеяло) — bed_linen73."""
    x0, x1 = BED73_X
    y = BED73_TOP
    o = []
    o.append(blob(rect_pts(x0 - 20, FL73 - 18, x1 + 40, FL73 + 26), P["shadow"], .45))
    for lx in (x0 + 20, x1 - 30):
        o.append(shape(rect_pts(lx - 14, y + 120, lx + 14, FL73), P["wood_sh"], "", w=3.4, seed=7370 + int(lx) % 7))
    o.append(shape(lib.rrect(x0 - 10, y + 70, x1 + 20, y + 140, 8), P["wood"], blob(rect_pts(x0 - 10, y + 120, x1 + 20, y + 142), P["wood_sh"]), w=4.2, seed=7371))
    o.append(shape(lib.rrect(x1 - 6, y - 330, x1 + 50, y + 140, 14), P["wood"], blob(rect_pts(x1 + 30, y - 330, x1 + 52, y + 140), P["wood_sh"]), w=4.4, seed=7372))
    o.append(shape(lib.rrect(x0 - 40, y - 80, x0 + 10, y + 140, 12), P["wood"], blob(rect_pts(x0 - 12, y - 80, x0 + 12, y + 140), P["wood_sh"]), w=4.4, seed=7373))
    o.append(shape(lib.rrect(x0, y, x1, y + 80, 18), P["sheet"], blob(rect_pts(x0, y + 54, x1, y + 82), P["sheet_sh"]), w=3.8, seed=7374))
    return "".join(o)


def bed_linen73(P, blanket=1.0, seed=0):
    """Подушка у изголовья и одеяло (сцена кладёт Диму между подушкой и одеялом, если он лежит): dict(pillow, blanket)."""
    px, py = BED73_PILLOW
    pil = shape([(px - 150, py + 22, 1), (px - 160, py - 30), (px - 110, py - 70), (px + 60, py - 76), (px + 120, py - 50), (px + 118, py + 22, 1)],
                lib.mix(P["sheet"], "#ffffff", .2), blob(rect_pts(px - 170, py + 4, px + 130, py + 26), P["sheet_sh"]), w=3.8, seed=7380)
    x0, x1 = BED73_X
    y = BED73_TOP
    qc = lib.mix(P["cur"], P["sheet"], .25)
    pts = [(x0 - 4, y + 96, 1), (x0 - 10, y - 8), (x0 + 200, y - 40 * blanket), (x0 + 700, y - 70 * blanket), (x1 - 360, y - 60 * blanket),
           (x1 - 250, y - 10), (x1 - 240, y + 96, 1)]
    inner = blob([(x0 - 20, y + 60), (x1, y + 60), (x1, y + 100), (x0 - 20, y + 100)], lib.mul(qc, (.78, .78, .8)))
    for i in range(5):
        xx = x0 + 120 + i * 210
        inner += line([(xx, y - 30 * blanket), (xx + 10, y + 90)], 3, lib.mul(qc, (.82, .82, .85)), taper=.3, wmin=.5, seed=7381 + i)
    bl = shape(pts, qc, inner, w=4.2, seed=7386)
    return dict(pillow=pil, blanket=bl)


def _nightstand73(P):
    x0, x1 = NSTAND73
    y = NSTAND73_TOP
    o = [blob(rect_pts(x0 - 6, FL73 - 12, x1 + 20, FL73 + 18), P["shadow"], .45)]
    o.append(shape(rect_pts(x0, y, x1, FL73 - 10), P["wood"], blob(rect_pts(x1 - 22, y, x1, FL73 - 10), P["wood_sh"]), w=4.2, seed=7390))
    o.append(shape(lib.rrect(x0 - 14, y - 22, x1 + 14, y + 6, 5), lib.mix(P["wood"], "#ffffff", .08), "", w=3.8, seed=7391))
    o.append(shape(lib.rrect(x0 + 24, y + 60, x1 - 24, y + 160, 6), P["wood"], blob(ellipse_pts((x0 + x1) / 2, y + 110, 10, 7, 8), P["wood_sh"]),
                   w=3.4, seed=7392))
    return "".join(o)


def _desk73(P):
    x0, x1 = DESK73_X
    y = DESK73_TOP
    o = [shape(rect_pts(x0, y, x1, y + 34), P["wood"], blob(rect_pts(x0, y + 22, x1, y + 34), P["wood_sh"]), w=4.2, seed=7395)]
    for lx in (x0 + 30, x1 - 50):
        o.append(shape(rect_pts(lx, y + 34, lx + 22, FL73), P["wood_sh"], "", w=3.4, seed=7396 + int(lx) % 5))
    return "".join(o)


def _moon_patch73(P, u, t):
    """Лунный прямоугольник окна на полу и косо на стене справа (форма окна, крестовина тенью, чёткие края)."""
    if u <= .01:
        return ""
    x0, y0, x1, y1 = WIN73
    col = "#7f8fd0"
    o = _sun_quad((x1 + 120, y0 + 260), (420, 60), (160, 620), col, "#9aa8e0", inset=.06)
    o += _sun_quad((x0 + 80, WALL73_Y + 30), (560, 10), (520, 240), col, "#9aa8e0", inset=.08)
    return f'<g opacity="{.42 * u:.3f}">{o}</g>'


def _lamp_pools73(t, u):
    """Свет ночника: пятно формы абажура на стене над тумбочкой и тёплый круг на тумбочке/полу (чёткие края, мерцание)."""
    if u <= .01:
        return ""
    lx, ly = LAMP73
    fl = light(t, u)
    o = _light_pool73(lx - 60, ly - 330, 300 * fl, 230 * fl, t, LAMP_GLOW, .26 * u, 7400, 1.5)
    o += _light_pool73(lx - 260, FL73 + 50, 460, 70, t, LAMP_GLOW, .24 * u, 7402, 1.5)
    return o


def board_items_layer():
    """Резерв для сцен: пусто (предметы на доске ставит сцена из props)."""
    return ""


def cold_room(t, mode="close", curtain_u=0.0):
    """Холодный дневной свет: серо-голубая стена, доска, окно с пасмурным небом и шторами. См. шапку раздела 73."""
    P = PAL73["cold"]
    bg = ['<rect x="-3000" y="-1800" width="7000" height="6000" fill="#9aa6b2"/>', _wall73(P)]
    bg.append(cork_board73(*BOARD73, P))
    win, gap = _window73(P, 0.0, t, curtain_u, day=True)
    bg.append(win)
    bg.append(_desk73(P))
    # свет из окна: полоса формы щели штор на стене под окном и на полу, к Диме; сужается со шторами
    gx0, gx1 = gap
    y1 = WIN73[3]
    sx, sy = STAND73
    nar = smooth01(curtain_u)
    fx0 = gx0 - 420 - 260 * (1 - nar)
    fx1 = gx1 - 420 + 60 * (1 - nar)
    lt = [blob([(gx0, y1 + 24), (gx1, y1 + 24), (gx1 + 10, WALL73_Y - 46), (gx0 - 10, WALL73_Y - 46)], "#eef3f6", .35)]
    lt.append(blob([(gx0 - 10, WALL73_Y + 6), (gx1 + 10, WALL73_Y + 6), (fx1 + 40, FL73 + 300), (fx0 - 40, FL73 + 300)], "#e6edf2", .45 + .25 * nar))
    # луч в воздухе (только когда шторы почти сведены — «прожектор»)
    beam = [(gx0, WIN73[1] + 40), (gx1, WIN73[1] + 40), (fx1 + 80, FL73 + 60), (fx0 - 80, FL73 + 60)]
    if nar > .3:
        lt.append(blob(beam, "#f2f6f8", .16 * (nar - .3) / .7))
    dim = ""
    if curtain_u > .01:
        big = "M-3000 -1800H4000V4200H-3000Z"
        bp = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in [(beam[0][0] - 30, beam[0][1]), (beam[1][0] + 30, beam[1][1]), (beam[2][0] + 90, beam[2][1] + 300),
                                                           (beam[3][0] - 90, beam[3][1] + 300)]) + "Z"
        dim = f'<path d="{big}{bp}" fill="#1b2433" fill-rule="evenodd" opacity="{.42 * nar:.3f}"/>'
    cam = CAM73_BOARD_CLOSE if mode == "close" else CAM73_COLD_WIDE
    return dict(bg="".join(bg), light="".join(lt), dim=dim, front="", cam=cam, gap=gap)


def board_close(t, light="cold"):
    """Ракурс хука (light="cold") и петли (light="lamp": тёплый ночник за кадром справа — пятно формы абажура на стене)."""
    if light == "cold":
        d = cold_room(t, "close", 0.0)
        return dict(bg=d["bg"], light="", cam=CAM73_BOARD_CLOSE)
    P, u = _pal73(light)
    bg = ['<rect x="-3000" y="-1800" width="7000" height="6000" fill="#2a1c18"/>', _wall73(P), cork_board73(*BOARD73, P)]
    lx, ly = BOARD73[2] + 260, BOARD73[1] + 520      # ночник за правым краем кадра: свет косым пятном на доску и стену
    fl = light_(t, u)
    lt = blob([(lx, ly - 60), (lx, ly + 60), (lx - 760, ly + 360 * fl), (lx - 760, ly - 420 * fl)], LAMP_GLOW, .13 * u)
    lt += _light_pool73(lx - 330, ly - 20, 300 * fl, 260 * fl, t, LAMP_GLOW, .22 * u, 7410, 1.4)
    return dict(bg="".join(bg), light=lt, cam=CAM73_BOARD_CLOSE)


def light_(t, u=1.0):
    return light(t, u)


def _foot_view73(t, P, u, lamp_u):
    """Вид от изножья кровати (координаты кадра): потолок, стена с часами, изголовье, подушка, одеяло к зрителю."""
    o = [f'<rect x="-600" y="-600" width="2300" height="3200" fill="{P["wall"]}"/>']
    # потолок трапецией сверху (стык со стеной — линия), стена ниже
    cy = 130.0
    o.append(blob([(-600, -600), (1700, -600), (1700, cy - 20), (1080 + 300, cy), (-300, cy), (-600, cy - 20)], P["ceil"]))
    o.append(line([(-600, cy + 6), (1700, cy + 6)], 3.4, INK, taper=0, wmin=1, seed=7420))
    g = lib.lin_grad([(0, P["wall_sh"], 1), (.5, P["wall"], 1), (1, P["wall_hi"], 1)], 0, cy, 0, 1100, units="userSpaceOnUse")
    o.append(f'<rect x="-600" y="{f(cy + 8)}" width="2300" height="1000" fill="url(#{g})"/>')
    d = "".join(f"M{f(-560 + i * 150)} {f(cy + 10)}L{f(-558.5 + i * 150)} 1000" for i in range(16))
    o.append(f'<path d="{d}" stroke="{P["wall_ln"]}" stroke-width="1.8" opacity=".55" fill="none"/>')
    # лунный прямоугольник окна косо на стене слева (окно за левым краем кадра)
    if u < .99:
        mq = _sun_quad((-40, 260), (330, 70), (90, 520), "#8494d4", "#a0acdf", inset=.06)
        o.append(f'<g opacity="{.4 * (1 - u):.3f}">{mq}</g>')
    # изголовье, тумбочка справа с ночником
    o.append(shape(lib.rrect(120, 760, 960, 1080, 30), P["wood"], blob(rect_pts(120, 1040, 960, 1082), P["wood_sh"]) + line([(150, 800), (930, 800)], 3, P["wood_sh"], taper=0, wmin=1, seed=7421), w=4.6, seed=7422))
    o.append(shape(rect_pts(930, 960, 1120, 1300), P["wood"], blob(rect_pts(1090, 960, 1120, 1300), P["wood_sh"]), w=4.0, seed=7423))
    o.append(shape(lib.rrect(918, 940, 1130, 966, 5), lib.mix(P["wood"], "#ffffff", .08), "", w=3.6, seed=7424))
    if lamp_u > .01:
        lx, ly = FOOT_LAMP
        fl = light(t, lamp_u)
        o.append(_light_pool73(lx - 90, ly - 300, 260 * fl, 200 * fl, t, LAMP_GLOW, .26 * lamp_u, 7425, 1.5))
    o.append(night_lamp73(FOOT_LAMP[0], FOOT_LAMP[1], .9, lamp_u, t, P))
    # матрас и подушка
    o.append(shape(lib.rrect(60, 1010, 1020, 1240, 30), P["sheet"], blob(rect_pts(60, 1190, 1020, 1242), P["sheet_sh"]), w=4.0, seed=7426))
    hx, hy = FOOT_HEAD
    pil = [(hx - 330, hy + 70, 1), (hx - 350, hy - 10), (hx - 290, hy - 92), (hx, hy - 112), (hx + 290, hy - 96), (hx + 350, hy - 10), (hx + 330, hy + 70, 1),
           (hx, hy + 92)]
    o.append(shape(pil, lib.mix(P["sheet"], "#ffffff", .18), blob(ellipse_pts(hx, hy + 10, 170, 60, 20), P["sheet_sh"], .8), w=4.0, seed=7427))
    bg = "".join(o)
    # одеяло к зрителю: от плеч Димы (hy + 120) расширяется к низу кадра (перспектива), складки к зрителю
    qc = lib.mix(P["cur"], P["sheet"], .25)
    top = hy + 125
    bl = [(hx - 300, top + 10, 1), (hx - 150, top - 22), (hx, top - 10), (hx + 150, top - 24), (hx + 300, top + 10, 1), (hx + 560, 2000, 1), (hx - 560, 2000, 1)]
    inner = blob([(hx + 120, top), (hx + 320, top), (hx + 620, 2000), (hx + 260, 2000)], lib.mul(qc, (.8, .8, .84)), .8)
    for i in range(4):
        a = -230 + 150 * i
        inner += line([(hx + a * .5, top + 30), (hx + a * .9, top + 400), (hx + a * 1.5, 1990)], 4, lib.mul(qc, (.8, .8, .84)), taper=.4, wmin=.3, seed=7428 + i)
    inner += line([(hx - 290, top + 60), (hx, top + 46), (hx + 290, top + 60)], 6, lib.mix(qc, "#ffffff", .3), taper=.3, wmin=.5, seed=7433)
    front = shape(bl, qc, inner, w=4.6, seed=7434)
    return bg, front


def bedroom(t, light="moon", mode="wide", lamp_u=None, moon_phase=1.0):
    """Спальня ночью (см. шапку раздела 73). lamp_u — включённость ночника (по умолчанию = доля тепла палитры)."""
    P, u = _pal73(light)
    lu = u if lamp_u is None else clamp01(lamp_u)
    if mode == "foot":
        bg, front = _foot_view73(t, P, u, lu)
        return dict(bg=bg, light="", front=front, cam=CAM73_FOOT, k=u, P=P)
    bg = [f'<rect x="-3000" y="-1800" width="7000" height="6000" fill="{P["shadow"]}"/>', _wall73(P)]
    bg.append(cork_board73(*BOARD73, P))
    win, _ = _window73(P, u, t, 0.0, moon_phase=moon_phase)
    bg.append(win)
    bg.append(_desk73(P))
    bg.append(lib_clock73(*CLOCK73, t, P))
    bg.append(_moon_patch73(P, 1 - u, t))
    bg.append(_lamp_pools73(t, lu))
    bg.append(_bed73(P))
    bg.append(_nightstand73(P))
    bg.append(night_lamp73(LAMP73[0], LAMP73[1], 1.0, lu, t, P))
    lin = bed_linen73(P)
    cams = {"wide": CAM73_BED_WIDE, "bed": CAM73_BED, "cam": CAM73_NSTAND, "board": CAM73_BOARD_MID, "desk": CAM73_DESK}
    return dict(bg="".join(bg), pillow=lin["pillow"], blanket=lin["blanket"], light="", front="", cam=cams.get(mode, CAM73_BED_WIDE), k=u, P=P)


def lib_clock73(x, y, r, t, P, h=3, m=12, tick=True):
    """Часы без цифр и делений на 3:12; секундная стрелка дёргается раз в секунду. Ночью циферблат приглушён (читается)."""
    import props
    ah, am = props.clock_hm(h, m)
    face = lib.mix("#c9cde0", "#f7f1e3", .35) if P is PAL73["moon"] else "#f7f1e3"
    o = props.clock(x, y, r, ah, am, seed=73, face=face, rim="#4F78B5")
    if tick:
        sec = math.floor(t) + min(1.0, (t % 1.0) / .06) * 1.0      # рывок за 2 кадра в начале каждой секунды
        a = math.radians(sec * 6 - 90 + 20)
        o += line([(x - math.cos(a) * r * .14, y - math.sin(a) * r * .14), (x + math.cos(a) * r * .76, y + math.sin(a) * r * .76)], 3.2 * r / 90, "#c4413a",
                  taper=.2, wmin=.6, seed=7440)
    return o


def heart_k(t, t_beat):
    """Сила удара сердца 0…1: двойной толчок «тук-тук» (t_beat и t_beat + 0.2), резкий подъём, затухание."""
    v = 0.0
    for t0, a in ((t_beat, 1.0), (t_beat + .2, .65)):
        q = t - t0
        if q > 0:
            v = max(v, a * min(1.0, q / .035) * math.exp(-q / .12))
    return v


def heart_pulse(t, t_beat, amp=1.0, col="#05070f"):
    """Поверх кадра (координаты кадра 1080×1920): виньетка к краям и проседание света всего кадра на удар сердца."""
    k = heart_k(t, t_beat) * amp
    if k < .005:
        return ""
    g = lib.rad_grad([(0, col, 0), (.55, col, 0), (1, col, 1)], 540, 900, 820, 1250)
    return (f'<rect width="1080" height="1920" fill="url(#{g})" opacity="{.75 * k:.3f}"/>'
            f'<rect width="1080" height="1920" fill="{col}" opacity="{.15 * k:.3f}"/>')


def light_tint(svg, P):
    """Подкрасить предмет props (нарисован в дневных цветах) под свет палитры P: холодный день, луна или ночник (смесь)."""
    if P is PAL73["cold"]:
        return cold_tint(svg, 1.0)
    u = P.get("_u", 0.0)
    if u >= .99:
        return warm_tint(svg, 1.0)
    return warm_tint(cold_tint(svg, 0.0, 1 - u), u) if u > .01 else cold_tint(svg, 0.0, 1.0)


def _tint(svg, m, tag):
    fid = f"{tag}{abs(hash(m)) % 10 ** 8}"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        lib.DEFS.append(f'<filter id="{fid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="{m}"/></filter>')
    return f'<g filter="url(#{fid})">{svg}</g>'


def warm_tint(svg, k=1.0):
    """Тёплый свет ночника на герое: красный чуть выше, синий ниже (k 0…1)."""
    k = clamp01(k)
    if k < .01:
        return svg
    r, g, b = 1 + .06 * k, 1 - .02 * k, 1 - .16 * k
    return _tint(svg, f"{r:.3f} 0 0 0 {.02 * k:.3f} 0 {g:.3f} 0 0 {.01 * k:.3f} 0 0 {b:.3f} 0 0 0 0 0 1 0", "wt")


def cold_tint(svg, k=1.0, night=0.0):
    """Холодный свет (день, k) или луна (night 0…1: темнее и синее, но контур читается)."""
    k, n = clamp01(k), clamp01(night)
    r = (1 - .13 * k) * (1 - .45 * n)
    g = (1 - .04 * k) * (1 - .38 * n)
    b = (1 + .06 * k) * (1 - .12 * n)
    return _tint(svg, f"{r:.3f} 0 0 0 0 0 {g:.3f} 0 0 0 0 0 {b:.3f} 0 {.03 * n:.3f} 0 0 0 1 0", "ct")


# ══════════════════════════════════════════════════════════════════════════════════════
# РИЛС 74 «ПРЕКРАТИ НЫТЬ» (пишет группа C; берут все). Трон из офисного кресла, стол ночью, всполох-сбой.
#
# ТРОН — throne_scene(t, light="regal", view="low", sway=0.0) -> dict, КООРДИНАТЫ КАДРА 1080×1920 (камера по умолчанию
#   CAM74_FRAME = (540, 960, 1.0); влёт/наезд — lib.cam вокруг точки кадра). Офисное кресло Димы: высокая спинка с
#   подголовником, подлокотники, сиденье, газлифт и крестовина с колёсиками; накидку (props.throne_drape группы A) и корону
#   ставит сцена по якорям ниже. light: "regal" (холодный фиолетово-синий луч сверху, тёмный фон, пылинки в луче),
#   "dark" (почти чёрный синий, контур туши светлее фона — rim74()), "warm" (тёплая настольная лампа справа за кадром)
#   или число 0…2 — смесь regal(0) → dark(1) → warm(2). sway — качание кресла (градусы, кресло на газлифте пружинит).
#   view: "low"   — снизу крупно (s01, s17): кот k = 3.0, кот+корона ≈ 66 % высоты; крестовина за нижним краем;
#         "front" — фронтально средний план (s04): кот k = 2.5, видно газлифт и крестовину на полу;
#         "top"   — сверху из-за плеча кота на стол Димы (s02): ВНИЗУ кадра пол и стол с Димой, у верхнего края —
#                   край сиденья с накидкой и подлокотник (передний план, крупно). Дима — people.dima(…) в TOP74_DIMA.
#   Слои (класть по порядку): bg → back (спинка) → [накидка на спинку] → seat (сиденье) → [кот] → arms (подлокотники,
#   ПОСЛЕ кота: лапа лежит на подлокотнике — сцена кладёт лапу после arms) → light (луч/пятно поверх всего) → motes.
#   Якоря в dict: cat=(x, y, k) — точка между задних лап кота на сиденье и масштаб cat.draw; arm_r / arm_l = (x, y) — верх
#   подлокотника справа/слева от зрителя (стук когтем); back_top=(x, y) — середина верха спинки; seat_front=(x, y) —
#   середина переднего края сиденья (накидка свисает отсюда); floor_y — пол (корона катится по нему, только "front");
#   drape_k — (sx, sy) накидки под этот вид; cam — камера. drape74(view, t, u, swing) — накидка props.throne_drape, растянутая
#   на спинку и сиденье этого вида (класть после seat, до кота; u 1 → 0 — сползает на пол). Подлокотник стоит так, что
#   cross_tap кота (cat.py) попадает когтем ровно в его верх.
#   rim74(svg, col, r) — светлый контур вокруг силуэта (для темноты s06: «контур туши светлее фона»).
#
# СТОЛ НОЧЬЮ — night_desk(t, light="lamp", view="mid", sky_u=None) -> dict, МИРОВЫЕ координаты комнаты рилса 64/70
#   (стол DESK_X у стены, Дима на стуле слева от стола в SIT лицом вправо, лампа LAMP справа; см. шапку файла), но над
#   столом ОКНО WIN74 (небо по sky_u). light: "lamp" (тёплая лампа горит), "screen" (лампа выключена, в комнате почти
#   темно, светится только телефон — свет экрана на лице кладёт сцена: screen_light74()), число 0…1 — screen → lamp.
#   sky_u — небо в окне: None — ночь со звёздами; число — день-ночь «перелистываются»: целая часть — номер суток,
#   дробная 0…0.5 — день (солнце дугой слева направо), 0.5…1 — ночь (луна дугой), между ними короткий закат/рассвет.
#   Порядок слоёв как у desk_scene: bg → chair_back → desk_top → pool → [Дима: legs] → desk_legs → chair_seat →
#   [тело Димы] → предметы → [ближняя рука] → lamp → dark (затемнение "screen", ПОСЛЕ всего, кроме света экрана).
#   view (камера в dict "cam"): "mid" — Дима средним планом с котом на столе (s06 после 7.40, s08, s10, s13), Дима ≈ 55 %;
#         "wide" — стол общим планом с окном, без людей (s09); "cat" — кот крупно на столе (s15, s16), морда ≈ 45–50 %;
#         "shoulder" — через плечо на экран (s07, s14): отдельная композиция в КООРДИНАТАХ КАДРА (cam = CAM74_FRAME):
#         тёмная стена, край окна слева сверху, столешница внизу; Дима со спины — people.dima_back(SH74_DIMA…), телефон
#         в его руках около SH74_PHONE (props.phone_draft группы A).
#   Точки на столе (мир): PHONE74 (телефон лежит), PLANT74 (горшок цветка дном), JAR74 (банка дном), CAT74 (кот: точка между
#   задних лап, k = CAT74_K), CRACKER74 (крекер/кусочки).
#   screen_light74(x, y, w, h, u, t) — холодный прямоугольник света экрана на лице (наклонный, с чётким краем, лёгкое мерцание).
#
# ВСПЫШКА — glitch_flash(t, t0) -> SVG поверх кадра (координаты кадра): 2 кадра белого (t0 … t0 + 2/30) со смещёнными
#   полосами-сбоем, затем почти чёрный синий, который за 0.12 с уступает сцене до уровня dark_k (сцена кладёт её последней).
# ══════════════════════════════════════════════════════════════════════════════════════
CAM74_FRAME = (540.0, 960.0, 1.0)
THRONE74 = {
    "low": dict(cat=(540.0, 1478.0, 3.0), seat_y=1478.0, back=(268.0, 812.0, 210.0), arm_y=1390.0, arm_x=(196.0, 884.0), floor=None, drape_k=(1.85, 2.6)),
    "front": dict(cat=(540.0, 1452.0, 2.5), seat_y=1452.0, back=(300.0, 780.0, 470.0), arm_y=1383.0, arm_x=(230.0, 850.0), floor=1840.0, drape_k=(1.55, 2.0)),
}
TOP74_DIMA = (470.0, 1330.0)        # s02: таз сидящего Димы (вид сверху-спереди, стол перед ним ниже); scale ≈ 0.8
TOP74_DESK = (90.0, 1360.0, 990.0, 1600.0)   # s02: передний край столешницы (x0, y0, x1, y1 — верх и низ видимой плоскости)
TOP74_PHONE = (520.0, 1300.0)       # s02: где Дима держит телефон у груди
WIN74 = (720.0, 200.0, 1180.0, 700.0)
PHONE74 = (700.0, DESK_TOP - 30.0)
PLANT74 = (1090.0, DESK_TOP - 84.0)
JAR74 = (1010.0, DESK_TOP - 40.0)
CAT74 = (900.0, DESK_TOP - 40.0)
CAT74_K = 1.0
CRACKER74 = (790.0, DESK_TOP - 34.0)
CAM74_MID = (640.0, 720.0, 1.32)
CAM74_WIDE = (900.0, 640.0, 1.18)
CAM74_CAT = (960.0, 760.0, 2.15)
SH74_DIMA = (260.0, 1560.0)         # «через плечо»: основание шеи Димы для people.dima_back(…, scale≈1.9)
SH74_PHONE = (640.0, 1040.0)        # «через плечо»: центр телефона в руках
SH74_DESK_Y = 1330.0                # «через плечо»: дальний край столешницы

THRONE_PAL = {
    "regal": dict(wall0="#17132e", wall1="#2a2350", wall2="#3a3170", floor="#211b3a", beam="#cfc6ff", beam_op=.2,
                  k=(.62, .6, .9), mote=1.0, rim=0.0),
    "dark": dict(wall0="#05070f", wall1="#0a0e1d", wall2="#0f1528", floor="#070a14", beam="#cfc6ff", beam_op=0.0,
                 k=(.3, .32, .46), mote=.25, rim=1.0),
    "warm": dict(wall0="#4a302c", wall1="#6c4a42", wall2="#8a6450", floor="#53382a", beam="#ffd890", beam_op=0.0,
                 k=(1.0, .93, .82), mote=.6, rim=0.0),
}
CHAIR74 = dict(fab="#4b505d", fab_sh="#30343e", fab_hi="#666d7e", metal="#9aa0ab", metal_sh="#5f6570", plastic="#2a2d34")


def _throne_pal(light):
    if isinstance(light, str):
        light = {"regal": 0.0, "dark": 1.0, "warm": 2.0}[light]
    u = max(0.0, min(2.0, float(light)))
    a, b = (THRONE_PAL["regal"], THRONE_PAL["dark"]) if u <= 1 else (THRONE_PAL["dark"], THRONE_PAL["warm"])
    w = u if u <= 1 else u - 1
    out = {}
    for k_, v in a.items():
        bv = b[k_]
        if isinstance(v, str):
            out[k_] = lib.mix(v, bv, w)
        elif isinstance(v, tuple):
            out[k_] = tuple(x + (y - x) * w for x, y in zip(v, bv))
        else:
            out[k_] = v + (bv - v) * w
    out["_warm"] = max(0.0, u - 1)
    out["_dark"] = max(0.0, 1 - abs(u - 1))
    return out


def rim74(svg, col="#56628f", r=3.0, op=1.0, only=False):
    """Светлый контур вокруг силуэта (расширенная альфа под рисунком): в темноте силуэт читается, тушь остаётся тушью.
    only=True — только кольцо контура без самого рисунка (класть поверх затемнения, чтобы контур не гас вместе со сценой)."""
    fid = f"rim{abs(hash((col, r, op, only))) % 10 ** 7}"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        tail = ('<feComposite in="c" in2="SourceAlpha" operator="out"/>' if only else
                '<feMerge><feMergeNode in="c"/><feMergeNode in="SourceGraphic"/></feMerge>')
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">'
                        f'<feMorphology in="SourceAlpha" operator="dilate" radius="{r}" result="d"/>'
                        f'<feFlood flood-color="{col}" flood-opacity="{op}"/><feComposite in2="d" operator="in" result="c"/>{tail}</filter>')
    return f'<g filter="url(#{fid})">{svg}</g>'


def _chair_cols(P):
    k = P["k"]
    return {n: lib.mul(c, k) for n, c in CHAIR74.items()}


def _caster(x, y, s, C, seed):
    return (shape(ellipse_pts(x, y, 26 * s, 20 * s, 12), C["plastic"], blob(ellipse_pts(x + 6 * s, y + 6 * s, 16 * s, 10 * s, 10), "#000000", .3), w=3.0, seed=seed)
            + blob(ellipse_pts(x - 8 * s, y - 6 * s, 8 * s, 5 * s, 8), C["fab_hi"], .5))


def _office_chair(v, P, t, sway=0.0, view="low"):
    """Офисное кресло в кадре (координаты кадра): dict(back, seat, arms, base). v — THRONE74[view]."""
    C = _chair_cols(P)
    cx = 540.0
    sy = v["seat_y"]
    bx0, bx1, btop = v["back"]
    low = view == "low"
    o_back, o_seat, o_arms, o_base = [], [], [], []
    # спинка: высокая, чуть шире кверху (снизу видно — верх дальше, но спинка откинута к нам), подголовник
    back = lib.rrect(bx0, btop + 120, bx1, sy + 10, 46)
    stitch = "".join(line([(bx0 + 40, y), (bx1 - 40, y + 2)], 2.2, C["fab_sh"], taper=0, wmin=1, seed=7741 + i, op=.8)
                     for i, y in enumerate(range(int(btop + 260), int(sy - 60), 150)))
    inner = blob([(bx1 - 70, btop + 120), (bx1, btop + 120), (bx1, sy), (bx1 - 90, sy)], C["fab_sh"], .9) + stitch
    inner += blob([(bx0 + 30, btop + 150), (bx0 + 90, btop + 150), (bx0 + 70, sy - 80), (bx0 + 30, sy - 80)], C["fab_hi"], .55)
    o_back.append(shape(back, C["fab"], inner, w=5.0, seed=7740))
    hw = (bx1 - bx0) * .34
    head = lib.rrect(cx - hw, btop, cx + hw, btop + 150, 40)
    o_back.append(shape(head, C["fab"], blob(rect_pts(cx + hw - 50, btop, cx + hw, btop + 150), C["fab_sh"], .9), w=4.6, seed=7742))
    o_back.append(blob(rect_pts(cx - 40, btop + 146, cx + 40, btop + 126 + 40), C["plastic"]))
    # сиденье: верх (куда сел кот) и передняя кромка; снизу — видна нижняя плоскость и механизм
    sw = (bx1 - bx0) * .62 + 40
    top_ = [(cx - sw, sy - 30, 1), (cx + sw, sy - 30, 1), (cx + sw + 20, sy + 6), (cx - sw - 20, sy + 6)]
    o_seat.append(shape(top_, C["fab"], blob([(cx + sw - 60, sy - 30), (cx + sw + 20, sy + 6), (cx + sw - 80, sy + 6)], C["fab_sh"], .9), w=4.6, seed=7743))
    lip = lib.rrect(cx - sw - 20, sy - 4, cx + sw + 20, sy + 64, 30)
    o_seat.append(shape(lip, C["fab"], blob(rect_pts(cx - sw - 20, sy + 40, cx + sw + 20, sy + 64), C["fab_sh"], .9)
                        + line([(cx - sw + 10, sy + 22), (cx + sw - 10, sy + 22)], 2.2, C["fab_hi"], taper=0, wmin=1, seed=7744, op=.6), w=4.8, seed=7745))
    if low:
        under = ellipse_pts(cx, sy + 70, sw - 10, 46, 18)
        o_seat.append(shape(under, C["plastic"], blob(ellipse_pts(cx, sy + 80, sw * .6, 26, 14), "#000000", .3), w=4.0, seed=7746))
        o_base.append(shape(rect_pts(cx - 70, sy + 96, cx + 70, sy + 150), C["plastic"], "", w=3.6, seed=7747))
        o_base.append(shape(rect_pts(cx - 28, sy + 150, cx + 28, 1990), C["metal"], blob(rect_pts(cx + 6, sy + 150, cx + 28, 1990), C["metal_sh"], .9)
                            + line([(cx - 14, sy + 170), (cx - 14, 1990)], 3, "#ffffff", taper=0, wmin=1, seed=7748, op=.25), w=3.6, seed=7749))
    else:
        fl = v["floor"]
        o_base.append(shape(rect_pts(cx - 60, sy + 60, cx + 60, sy + 104), C["plastic"], "", w=3.4, seed=7747))
        o_base.append(shape(rect_pts(cx - 20, sy + 104, cx + 20, fl - 90), C["metal"], blob(rect_pts(cx + 4, sy + 104, cx + 20, fl - 90), C["metal_sh"], .9), w=3.4, seed=7749))
        hub = (cx, fl - 80)
        for i, (dx, dy) in enumerate(((-260, 40), (260, 40), (-150, 70), (150, 70), (0, 24))):
            leg = [(hub[0] - 18, hub[1] - 10, 1), (hub[0] + 18, hub[1] - 10, 1), (hub[0] + dx + 14, hub[1] + dy, 1), (hub[0] + dx - 14, hub[1] + dy + 10, 1)]
            o_base.append(shape(leg, C["plastic"], "", w=3.2, seed=7750 + i))
            o_base.append(_caster(hub[0] + dx, hub[1] + dy + 28, 1.0, C, 7756 + i))
        o_base.insert(0, blob(ellipse_pts(cx, fl + 20, 330, 34, 20), "#000000", .25))
    # подлокотники: стойка от сиденья, накладка; снизу видна нижняя плоскость накладки
    ay = v["arm_y"]
    for i, ax in enumerate(v["arm_x"]):
        sgn = -1 if ax < cx else 1
        post = [(ax - 20, ay + 30, 1), (ax + 20, ay + 30, 1), (ax + 16 - sgn * 30, sy + 30, 1), (ax - 16 - sgn * 30, sy + 30, 1)]
        o_arms.append(shape(post, C["plastic"], blob([(ax + 4, ay + 30), (ax + 20, ay + 30), (ax + 16 - sgn * 30, sy + 30), (ax - sgn * 30, sy + 30)], "#000000", .3),
                            w=3.6, seed=7760 + i))
        pad = lib.rrect(ax - 92, ay - 26, ax + 92, ay + 30, 26)
        o_arms.append(shape(pad, C["fab"], blob(rect_pts(ax - 92, ay + 8, ax + 92, ay + 30), C["plastic"], .9)
                            + blob(rect_pts(ax - 80, ay - 22, ax + 60, ay - 12), C["fab_hi"], .5), w=4.4, seed=7762 + i))
    tf = f'rotate({sway:.2f} {cx} {sy + 150})'
    g = lambda L: f'<g transform="{tf}">{"".join(L)}</g>' if L else ""  # noqa: E731
    return dict(back=g(o_back), seat=g(o_seat), arms=g(o_arms), base=g(o_base))


def _throne_bg(P, t, view):
    o = ['<rect x="-600" y="-600" width="2280" height="3120" fill="%s"/>' % P["wall0"]]
    g = lib.rad_grad([(0, P["wall2"], 1), (.55, P["wall1"], 1), (1, P["wall0"], 1)], 540, 520, 900, 1200)
    o.append(f'<rect x="-600" y="-600" width="2280" height="3120" fill="url(#{g})"/>')
    # стена: вертикальные полосы обоев и угол комнаты — чтобы фон не был пустым пятном
    d = "".join(f"M{f(x)} -600L{f(x + 1.5)} 2600" for x in range(-420, 1600, 140))
    o.append(f'<path d="{d}" stroke="{P["wall0"]}" stroke-width="2" opacity=".5" fill="none"/>')
    if view == "low":
        # потолок с карнизом сверху (ракурс снизу): тёмная полоса и линия угла
        o.append(blob([(-600, -600), (1680, -600), (1680, 70), (-600, 120)], lib.mix(P["wall0"], "#000000", .3)))
        o.append(line([(-600, 120), (1680, 70)], 4.0, INK, taper=0, wmin=1, seed=7770))
    else:
        fl = THRONE74[view]["floor"]
        o.append(blob([(-600, fl - 110), (1680, fl - 110), (1680, 2600), (-600, 2600)], P["floor"]))
        o.append(line([(-600, fl - 110), (1680, fl - 110)], 3.6, INK, taper=0, wmin=1, seed=7771))
        o.append(blob([(-600, fl - 150), (1680, fl - 150), (1680, fl - 110), (-600, fl - 110)], lib.mix(P["wall1"], "#ffffff", .08)))
    return "".join(o)


def _throne_light(P, t, view):
    """Свет: (за героем — луч/пятно на стене, поверх — лёгкая дымка луча, не выбеливает кота)."""
    beh, over = [], []
    if P["beam_op"] > .005:
        sway = 14 * math.sin(t * .9)
        top = -40 if view == "low" else 60
        beam = [(380 + sway, top), (700 + sway, top), (980, 1560), (100, 1560)]
        beh.append(blob(beam, P["beam"], P["beam_op"] * .75))
        beh.append(blob([(470 + sway, top), (610 + sway, top), (780, 1500), (300, 1500)], P["beam"], P["beam_op"] * .6))
        over.append(blob([(470 + sway, top), (610 + sway, top), (780, 1500), (300, 1500)], P["beam"], P["beam_op"] * .18))
    if P["_warm"] > .01:
        u = P["_warm"]
        fl = light(t, u)
        beh.append(blob([(1180, 360), (1180, 980), (320, 1640 * fl), (280, 160)], LAMP_GLOW, .12 * u))
        beh.append(_light_pool73(820, 700, 380 * fl, 320 * fl, t, LAMP_GLOW, .26 * u, 7780, 1.3))
        over.append(blob([(1180, 360), (1180, 980), (320, 1640 * fl), (280, 160)], LAMP_GLOW, .05 * u))
    return "".join(beh), "".join(over)


def throne_scene(t, light="regal", view="low", sway=0.0):
    """Трон из офисного кресла Димы (координаты кадра). См. шапку раздела 74."""
    P = _throne_pal(light)
    if view == "top":
        return _throne_top(t, P)
    v = THRONE74[view]
    ch = _office_chair(v, P, t, sway, view)
    cx, cy, ck = v["cat"]
    bx0, bx1, btop = v["back"]
    beh, lt = _throne_light(P, t, view)
    mt = motes(t, (300.0, 120.0 if view == "low" else 300.0, 860.0, 1250.0), n=22, u=P["mote"], seed=74) if P["mote"] > .01 else ""
    back, seat, arms, base = ch["back"], ch["seat"], ch["arms"], ch["base"]
    if P["rim"] > .01:
        col = lib.mix("#0f1528", "#56628f", P["rim"])
        back, seat, arms, base = (rim74(x, col, 3.0) for x in (back, seat, arms, base))
    return dict(bg=_throne_bg(P, t, view) + beh, back=base + back, seat=seat, arms=arms, light=lt, motes=mt, cam=CAM74_FRAME, cat=(cx, cy, ck),
                arm_l=(v["arm_x"][0], v["arm_y"] - 26), arm_r=(v["arm_x"][1], v["arm_y"] - 26), back_top=(540.0, btop + 120),
                seat_front=(540.0, v["seat_y"]), floor_y=v["floor"], drape_k=v["drape_k"], pal=P)


def _throne_top(t, P):
    """s02: сверху с трона из-за плеча кота вниз-вперёд на стол Димы. Пол в перспективе, стол, стул Димы; у верхнего края кадра
    передний план — край сиденья кресла и подлокотник (крупно, мягче резкостью: ближе камеры)."""
    k = P["k"]
    fl0, fl1 = lib.mul("#6a4a34", k), lib.mul("#4e3624", k)
    o = [f'<rect x="-600" y="-600" width="2280" height="3120" fill="{fl1}"/>']
    g = lib.lin_grad([(0, fl0, 1), (1, fl1, 1)], 0, 300, 0, 1920, units="userSpaceOnUse")
    o.append(f'<rect x="-600" y="300" width="2280" height="2300" fill="url(#{g})"/>')
    # стена с плинтусом вдали (верх кадра за передним планом)
    o.append(blob([(-600, -600), (1680, -600), (1680, 380), (-600, 420)], lib.mul("#7e7aa0", k)))
    o.append(shape([(-600, 380), (1680, 340), (1680, 380), (-600, 420)], lib.mul("#a7a2c0", k), "", w=3.0, seed=7790))
    # доски пола сходятся к стене (вид сверху)
    d = ""
    for i in range(-6, 14):
        x = 540 + i * 150
        d += f"M{f(540 + (x - 540) * .45)} 400L{f(540 + (x - 540) * 1.9)} 2000"
    for y in (620, 900, 1260, 1700):
        d += f"M-600 {y}L1680 {y - 10}"
    o.append(f'<path d="{d}" stroke="{lib.mul("#43291a", k)}" stroke-width="3" opacity=".55" fill="none"/>')
    # стол Димы: столешница сверху (трапеция), передний торец; ножки
    x0, y0, x1, y1 = TOP74_DESK
    dk = lib.mul(DESKW, k)
    o.append(blob([(x0 - 20, y1 + 30), (x1 + 20, y1 + 30), (x1 + 50, y1 + 380), (x0 - 50, y1 + 380)], "#000000", .22))
    for i, lx in enumerate((x0 + 30, x1 - 30)):
        o.append(shape(rect_pts(lx - 14, y1, lx + 14, y1 + 300), lib.mul(DESKW_SH, k), "", w=3.0, seed=7791 + i))
    front = ""
    front += shape([(x0 + 40, y0, 1), (x1 - 40, y0, 1), (x1, y1, 1), (x0, y1, 1)], dk, blob([(x0 + 40, y0), (x1 - 40, y0), (x1 - 30, y0 + 20), (x0 + 50, y0 + 20)],
                                                                                          lib.mul(DESKW_SH, k), .4), w=4.0, seed=7793)
    front += shape(rect_pts(x0, y1, x1, y1 + 34), lib.mul(DESKW_SH, k), "", w=3.6, seed=7794)
    # стул Димы за столом (спинка видна над его плечами — ставит сцена до Димы: chair_back)
    sx, sy = TOP74_DIMA
    cb = shape(lib.rrect(sx - 150, sy - 520, sx + 150, sy - 330, 24), lib.mul(WOOD, k), blob(rect_pts(sx + 90, sy - 520, sx + 150, sy - 330), lib.mul(WOOD_SH, k), .8),
               w=3.6, seed=7795)
    cb += shape(rect_pts(sx - 140, sy - 340, sx - 116, sy + 20), lib.mul(WOOD_SH, k), "", w=3.0, seed=7796)
    cb += shape(rect_pts(sx + 116, sy - 340, sx + 140, sy + 20), lib.mul(WOOD_SH, k), "", w=3.0, seed=7797)
    # передний план: край сиденья трона с бархатом (накидку можно положить поверх — PR.throne_drape) и подлокотник слева
    C = _chair_cols(P)
    fg = shape([(-600, -600), (1680, -600), (1680, -40), (900, 30, 1), (300, 60, 1), (-600, 40)], C["fab"],
               blob([(-600, -10), (1680, -60), (1680, -40), (900, 30), (300, 60), (-600, 40)], C["fab_sh"], .9), w=6.0, seed=7798)
    fg += shape(lib.rrect(-200, 150, 140, 260, 40), C["fab"], blob(rect_pts(-200, 210, 140, 260), C["plastic"], .9), w=6.0, seed=7799)
    beh, lt = _throne_light(P, t, "front")
    o.append(beh)
    return dict(bg="".join(o), chair_back=cb, desk=front, fg=fg, light=lt, motes=motes(t, (200.0, 300.0, 900.0, 1300.0), n=16, u=P["mote"], seed=75),
                cam=CAM74_FRAME, dima=TOP74_DIMA, phone=TOP74_PHONE, desk_box=TOP74_DESK, pal=P,
                back="", seat="", arms="", cat=None, arm_l=None, arm_r=None, back_top=None, seat_front=(540.0, 40.0), floor_y=None, drape_k=1.8)


# ───────────────────────────── стол ночью ─────────────────────────────
def _sky74(sky_u):
    """Цвета неба и положение светила по sky_u. Возвращает (верх, середина, низ, ('sun'|'moon', x01, y01), stars 0…1)."""
    if sky_u is None:
        return "#0c1232", "#1a2660", "#2e3e80", ("moon", .7, .3), 1.0
    fr = sky_u - math.floor(sky_u)
    DAY = ("#5fa6e6", "#9fd0f2", "#e2f2fb")
    DUSK = ("#3b4c8c", "#c97a8a", "#f2a86e")
    NIGHT = ("#0c1232", "#1a2660", "#2e3e80")

    def mx(A, B, u):
        return tuple(lib.mix(a, b, clamp01(u)) for a, b in zip(A, B))
    if fr < .5:
        q = fr / .5
        cols = mx(NIGHT, DAY, q / .12) if q < .12 else (mx(DAY, DUSK, (q - .82) / .18) if q > .82 else DAY)
        body = ("sun", .1 + .8 * q, .75 - .55 * math.sin(math.pi * q))
        stars = clamp01(1 - q / .1) if q < .1 else 0.0
    else:
        q = (fr - .5) / .5
        cols = mx(DUSK, NIGHT, q / .15) if q < .15 else (mx(NIGHT, NIGHT, 0) if q < .9 else mx(NIGHT, NIGHT, 0))
        body = ("moon", .1 + .8 * q, .75 - .55 * math.sin(math.pi * q))
        stars = clamp01((q - .08) / .15)
    return cols[0], cols[1], cols[2], body, stars


def window74(x0, y0, x1, y1, sky_u=None, t=0.0, dark=0.0):
    """Окно над столом: рама, крестовина, подоконник; небо «перелистывается» по sky_u (см. night_desk), дома силуэтом."""
    top, mid, bot, (kind, bxu, byu), stars = _sky74(sky_u)
    fr = 18
    ix0, iy0, ix1, iy1 = x0 + fr, y0 + fr, x1 - fr, y1 - fr
    g = lib.lin_grad([(0, top, 1), (.6, mid, 1), (1, bot, 1)], 0, 0, 0, 1)
    inner = f'<path d="M{f(ix0 - 5)} {f(iy0 - 5)}H{f(ix1 + 5)}V{f(iy1 + 5)}H{f(ix0 - 5)}Z" fill="url(#{g})"/>'
    bx, by = ix0 + (ix1 - ix0) * bxu, iy0 + (iy1 - iy0) * byu
    if stars > .01:
        r = rs(7811)
        for i in range(14):
            sx_, sy_ = r.uniform(ix0, ix1), r.uniform(iy0, iy0 + (iy1 - iy0) * .6)
            a = stars * (.55 + .45 * math.sin(t * 3 + i))
            inner += f'<circle cx="{f(sx_)}" cy="{f(sy_)}" r="{f(r.uniform(2.2, 4))}" fill="#fff6d6" opacity="{a:.3f}"/>'
    if kind == "sun":
        inner += f'<circle cx="{f(bx)}" cy="{f(by)}" r="70" fill="#ffe9a0" opacity=".45"/>'
        inner += shape(ellipse_pts(bx, by, 44, 44, 18), "#ffd45a", blob(ellipse_pts(bx - 10, by - 10, 22, 20, 12), "#fff1b0", .8), w=3.4, seed=7812)
        r = rs(7813)
        for i in range(3):
            cx_ = ix0 + ((t * 22 + i * 170 + r.uniform(0, 90)) % (ix1 - ix0 + 200)) - 100
            cy_ = iy0 + 70 + i * 60
            inner += shape(ellipse_pts(cx_, cy_, 70, 22, 14), "#ffffff", "", w=2.6, seed=7814 + i, var=.2)
    else:
        inner += f'<circle cx="{f(bx)}" cy="{f(by)}" r="62" fill="#c9d4ff" opacity=".18"/>'
        inner += shape(ellipse_pts(bx, by, 38, 38, 18), "#f4efd8", blob(ellipse_pts(bx + 12, by + 6, 14, 10, 10), "#d8d2b8", .8), w=3.2, seed=7815)
    # дома силуэтом внизу окна, окошки — тёплые квадраты ночью
    night = clamp01(1.0 if kind == "moon" else 0.0) * (1 if sky_u is None else 1)
    hc = lib.mix("#7d8fa6", "#141a36", night)
    r = rs(7816)
    x = ix0 - 10
    while x < ix1:
        w_ = r.uniform(70, 130)
        h_ = r.uniform(70, 170)
        inner += blob(rect_pts(x, iy1 - h_, x + w_, iy1 + 10), hc)
        for j in range(2):
            wy = iy1 - h_ + 24 + j * 44
            if wy < iy1 - 20:
                inner += blob(rect_pts(x + 18, wy, x + 34, wy + 18), "#ffd87a" if night > .5 else "#b9c7d6", .9 if night > .5 else .7)
        x += w_ + r.uniform(4, 16)
    c = lib.clip_rect(ix0, iy0, ix1 - ix0, iy1 - iy0)
    o = [f'<g clip-path="url(#{c})">{inner}</g>']
    frm = "#e8e2d4" if dark < .5 else "#7c86a8"
    rim_ = rect_pts(x0, y0, x1, y1)
    hole = rect_pts(ix0, iy0, ix1, iy1)
    d = lib.fill_d(rim_) if hasattr(lib, "fill_d") else ""
    o.append(f'<path d="{d}{lib.fill_d(hole[::-1])}" fill="{frm}" fill-rule="evenodd"/>')
    o.append(line(rim_ + [rim_[0]], 4.2, INK, taper=0, wmin=1, seed=7817) + line(hole + [hole[0]], 3.2, INK, taper=0, wmin=1, seed=7818))
    mxx, myy = (ix0 + ix1) / 2, (iy0 + iy1) / 2
    o.append(shape(rect_pts(mxx - 7, iy0, mxx + 7, iy1), frm, "", w=2.8, seed=7819))
    o.append(shape(rect_pts(ix0, myy - 7, ix1, myy + 7), frm, "", w=2.8, seed=7820))
    o.append(shape(rect_pts(x0 - 26, y1, x1 + 26, y1 + 28), frm, blob(rect_pts(x0 - 26, y1 + 18, x1 + 26, y1 + 28), "#000000", .2), w=3.6, seed=7821))
    return "".join(o)


def screen_light74(x, y, w=150.0, h=190.0, u=1.0, t=0.0, rot=-8.0):
    """Свет экрана на лице: холодный наклонный прямоугольник с чётким краем и ядро; мерцание еле заметное."""
    if u <= .01:
        return ""
    fl = 1 + .03 * math.sin(t * 9.1) + .02 * math.sin(t * 15.3)
    pts = lib.T(lib.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 22), 0, 0, 1, rot, x, y)
    core = lib.T(lib.rrect(x - w * .32, y - h * .32, x + w * .32, y + h * .32, 16), 0, 0, 1, rot, x, y)
    return blob(pts, "#bfe0ff", .22 * u * fl) + blob(core, "#e6f4ff", .2 * u * fl)


def night_desk(t, light="lamp", view="mid", sky_u=None):
    """Стол ночью (мир) или «через плечо» (кадр). См. шапку раздела 74."""
    lu = 1.0 if light == "lamp" else (0.0 if light == "screen" else clamp01(float(light)))
    if view == "shoulder":
        return _shoulder74(t, lu, sky_u)
    d = desk_scene(t, "night", lamp_on=lu)
    # своё: стена без окна слева — высокое окно WIN_TALL остаётся (оно далеко за краем кадра в "mid"/"cat"), над столом WIN74
    bg = [d["bg"], window74(*WIN74, sky_u=sky_u, t=t, dark=1 - lu)]
    if lu > .01:   # свет лампы: пятно формы абажура на стене над лампой
        fl = light_(t, lu)
        bg.append(_light_pool73(LAMP[0] - 90, LAMP[1] - 260, 230 * fl, 170 * fl, t, LAMP_GLOW, .2 * lu, 7830, 1.2))
    dark = ""
    if lu < .99:
        dark = f'<rect x="-3000" y="-1800" width="8000" height="6000" fill="#060914" opacity="{.8 * (1 - lu):.3f}"/>'
    cam = {"mid": CAM74_MID, "wide": CAM74_WIDE, "cat": CAM74_CAT}[view]
    return dict(bg="".join(bg), chair_back=d["chair_back"], chair_seat=d["chair_seat"], desk_top=d["desk_top"], desk_legs=d["desk_legs"],
                desk=d["desk"], pool=d["pool"], lamp=d["lamp"], dark=dark, cam=cam, sit=SIT, phone=PHONE74, plant=PLANT74, jar=JAR74,
                cat=(CAT74[0], CAT74[1], CAT74_K), cracker=CRACKER74)


def _shoulder74(t, lu, sky_u):
    """Через плечо Димы на экран телефона (координаты кадра): тёмная стена, край окна слева сверху, столешница внизу, лампа справа."""
    M = _M("night")
    k = (.55 + .45 * lu, .55 + .45 * lu, .65 + .35 * lu)
    o = [f'<rect x="-600" y="-600" width="2280" height="3120" fill="{lib.mul(M["wall_sh"], k)}"/>']
    g = lib.lin_grad([(0, lib.mul(M["wall_sh"], k), 1), (1, lib.mul(M["wall"], k), 1)], 0, 0, 0, 1400, units="userSpaceOnUse")
    o.append(f'<rect x="-600" y="-600" width="2280" height="2000" fill="url(#{g})"/>')
    o.append(window74(-260, 120, 300, 820, sky_u=sky_u, t=t, dark=1 - lu))
    if lu > .01:
        fl = light_(t, lu)
        o.append(_light_pool73(900, 760, 330 * fl, 260 * fl, t, LAMP_GLOW, .24 * lu, 7840, 1.2))
    # столешница сверху: дальний край SH74_DESK_Y, к зрителю — ниже края кадра
    dk, dsh = lib.mul(DESKW, k), lib.mul(DESKW_SH, k)
    y = SH74_DESK_Y
    desk_ = shape([(-600, y, 1), (1680, y, 1), (1680, 2600, 1), (-600, 2600, 1)], dk,
                  blob([(-600, y), (1680, y), (1680, y + 26), (-600, y + 26)], dsh, .6)
                  + "".join(line([(x, y + 60 + i * 37), (x + 140, y + 62 + i * 37)], 2, dsh, seed=7841 + i, op=.5) for i, x in enumerate((60, 520, 820, 300))),
                  w=4.0, seed=7845)
    pool = ""
    if lu > .01:
        pool = blob(ellipse_pts(880, y + 160, 260, 70, 20), "#ffe7a0", .3 * lu)
    lamp = ""
    if lu > .01 or True:
        lx, ly = 1010.0, y + 80
        col = lib.mul("#3f6f7a", k)
        lamp = shape(ellipse_pts(lx, ly, 70, 16, 16), col, "", w=3.2, seed=7846)
        lamp += line([(lx, ly - 10), (lx - 30, ly - 300), (lx - 150, ly - 380)], 15, lib.mul("#5a95a2", k), taper=0, wmin=1, seed=7847)
        head = [(lx - 230, ly - 420, 1), (lx - 120, ly - 430, 1), (lx - 60, ly - 300, 1), (lx - 260, ly - 290, 1)]
        lamp += shape(head, col, blob([(lx - 120, ly - 430), (lx - 60, ly - 300), (lx - 110, ly - 296)], lib.mul("#2c535c", k), .85), w=3.6, seed=7848)
        lamp += shape(ellipse_pts(lx - 160, ly - 294, 100, 16, 16), lib.mix("#5d6070", "#fff3c8", lu), "", w=2.8, seed=7849)
    dark = ""
    if lu < .99:
        dark = f'<rect x="-600" y="-600" width="2280" height="3120" fill="#060914" opacity="{.72 * (1 - lu):.3f}"/>'
    return dict(bg="".join(o), desk=desk_, desk_top=desk_, pool=pool, lamp=lamp, dark=dark, cam=CAM74_FRAME, dima=SH74_DIMA, phone=SH74_PHONE,
                chair_back="", chair_seat="", desk_legs="")


def glitch_flash(t, t0, dark_k=0.0):
    """Всполох-сбой: 2 кадра белого со смещёнными полосами (t0 … t0 + 2/30), затем почти чёрный синий, тающий к dark_k за 0.12 с."""
    u = t - t0
    if u < -1e-6:
        return ""
    if u < 2 / 30 - 1e-6:
        r = rs(7850, int(u * 300))
        o = ['<rect x="0" y="0" width="1080" height="1920" fill="#f6f7ff"/>']
        y = 0.0
        while y < 1920:
            h = r.uniform(30, 160)
            dx = r.uniform(-90, 90)
            col = ["#ffffff", "#d9e4ff", "#ffe8f2", "#c9d6ff"][r.randint(4)]
            o.append(f'<rect x="{f(dx)}" y="{f(y)}" width="1080" height="{f(h)}" fill="{col}" opacity="{r.uniform(.4, .9):.2f}"/>')
            if r.rand() < .35:
                o.append(f'<rect x="0" y="{f(y + h * .4)}" width="1080" height="{f(r.uniform(3, 9))}" fill="#3b4fd8" opacity=".5"/>')
            y += h
        return "".join(o)
    a = 1.0 - (1.0 - dark_k) * smooth01((u - 2 / 30) / .12)
    if a <= .005:
        return ""
    return f'<rect x="0" y="0" width="1080" height="1920" fill="#04060e" opacity="{a:.3f}"/>'


def drape74(view, t, u=1.0, swing=0.0, seed=0):
    """Накидка-трон (props.throne_drape группы A) на кресле вида view: верх — над спинкой, низ сиденья — по краю сиденья."""
    import props as PR
    v = THRONE74[view]
    sx, sy = v["drape_k"]
    y0 = v["seat_y"] - 420 * sy
    return f'<g transform="translate(540 {y0:.2f}) scale({sx:.4f} {sy:.4f})">{PR.throne_drape(0, 0, 1.0, u, swing, t, seed)}</g>'


# ═════════════════════════════════════════ РИЛС 78 «Лента, ты слабак» (группа C) ═════════════════════════════════════════
# Все сцены 78 — в КООРДИНАТАХ КАДРА 1080×1920 (камера по умолчанию CAM78 = (540, 960, 1.0); сцена ставит свою камеру поверх).
# Букв и цифр нет нигде. Свет — пятнами с чёткой формой.
#
# ДЕНЬ ХУКА — hook_day(t, view="close", warm=0.0) -> dict(bg, bed, front, shade, cam, anchors):
#   жёсткий холодно-белый свет, резкие тени (тень оконной рамы косо по стене — НИЖЕ зоны текста), фон почти без деталей.
#   view "close" (s01, петля s18): стена во весь кадр, низ — кровать с одеялом (край матраса HD_BED_Y); Дима сидит на кровати
#        слева по пояс, его рука по диагонали вниз вправо, телефон прилип к одеялу около HD_PHONE_BASE.
#        Зона текста HD_TEXT = (90, 170, 990, 440) — только чистая стена (тень рамы и предметы ниже HD_SHADOW_TOP).
#   view "wide" (s02): общий план той же комнаты: стена, плинтус, пол, кровать справа (HW_BED: x0, x1, верх матраса), подушка
#        HW_PILLOW (туда Дима падает лицом), Дима стоит слева у кровати (ступни на HW_FL).
#   warm 0…1 — тот же кадр в тёплом закатном свете (петля s18): стена тёплая, тень рамы становится полосой заката.
#   bg — стена+кровать (до Димы), bed — одеяло на переднем плане (ПОСЛЕ ног/таза Димы, ДО рук и телефона), front — пусто,
#   shade — поверх всего (холодная виньетка/тёплое свечение, без деталей).
#
# НОЧНАЯ СПАЛЬНЯ — night78(t, view, glow=1.0) -> dict(bg, front, dark, glass, anchors, cam):
#   почти темно, светится только экран телефона (свет экрана на лице кладёт сцена — screen_light74). Над кроватью тёмное окно.
#   view "window" (s03): кровать во всю ширину низа кадра, изголовье слева, подушка N78_PILLOW; над кроватью большое тёмное
#        окно N78_GLASS (x0, y0, x1, y1 — стекло): отражение Димы сцена рисует ВНУТРИ стекла — clip id в dict["glass_clip"].
#   view "mid"  (s05, s08, s09): средний план кровати сбоку с окном слева сверху, тумбочка справа (anchors: pillow, bed_top,
#        cat — где сидит кот на одеяле, nstand — верх тумбочки).
#   view "top"  (s04): кровать сверху во весь кадр: подушка сверху, одеяло, край кровати справа, пол, тумбочка (anchors).
#   dark — затемнение (класть ПОСЛЕ людей и предметов, ДО света экрана); glow — доля света экрана в комнате 0…1 (0 — совсем темно).
#
# ВСПЫШКА — glitch_flash(t, t0, dark_k) (из 74, выше).
#
# МАСТЕРСКАЯ ИЗОБРЕТАТЕЛЯ — workshop(t, mess_u=0.0) -> dict(bg, bench, front, houses, win, cam, anchors):
#   тёплая мастерская: дощатая стена, большое окно (win — стекло) с соседними домами (houses — список рамок домов (x0, y0, x1, y1)
#   в кадре, чтобы лентой их опутывать), верстак WS_BENCH (верх столешницы; рулон и ленту ставит сцена), лампа над верстаком.
#   mess_u 0…1 — на полу и стене прибавляется беспорядок (обрезки-полоски без букв), к концу комната темнеет к вечеру.
#
# ВЕЧЕР — evening_chair(t, sun=1.0) -> dict(bg, chair_back, chair_front, light, cam, anchors): кресло у окна на закате
#   (НЕ диван), тёплый свет. anchors: hip — таз сидящего Димы, arm — верх правого подлокотника (кот запрыгивает), knees —
#   колени (кот на коленях), book — книга на подлокотнике слева. Порядок: bg → chair_back → [Дима] → chair_front → [кот] → light.
#   Коридор вечером — hall_scene(t, "evening") (палитра HALL["evening"]).
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
CAM78 = (540.0, 960.0, 1.0)
HD_TEXT = (90.0, 170.0, 990.0, 440.0)
HD_SHADOW_TOP = 470.0
HD_BED_Y = 1150.0                     # край матраса (верх одеяла у Димы)
HD_PHONE_BASE = (820.0, 1290.0)       # где низ телефона прилип к одеялу
HD_HIP = (300.0, 1230.0)              # таз сидящего Димы (s01) — для people.figure
HW_FL = 1560.0
HW_BED = (560.0, 1240.0, 1250.0)      # x0, x1, верх матраса (s02)
HW_PILLOW = (1090.0, 1225.0)
HW_STAND = (250.0, HW_FL)

HALL["evening"] = dict(wall="#c79a7c", wall_hi="#d9b08e", wall_sh="#a87b62", stripe="#b98d70", floor="#8a5a38", floor_b="#6c4428", ln="#4c2e1a",
                       base="#e6cdb2", base_sh="#c4a689", light="#ffd896")


def _hall_pal(mode):
    return HALL.get(mode, HALL["night"])


def _hd_pal(warm):
    cold = dict(wall="#e7edf2", wall_hi="#f6f9fb", wall_sh="#cdd6de", shadow="#b3bfcb", sheet="#eef2f6", sheet_sh="#c2ccd8", quilt="#9fb4c9",
                quilt_sh="#7f95ad", quilt_hi="#c3d2e0", floor="#b9b2a8", floor_b="#9d958b", base="#f3f5f6", base_sh="#c8d0d6", head="#a7b1bb")
    hot = dict(wall="#e9b98e", wall_hi="#f6cfa2", wall_sh="#c99572", shadow="#f8d49a", sheet="#f6dcc0", sheet_sh="#d6ad8a", quilt="#c98a6a",
               quilt_sh="#a66a4e", quilt_hi="#e3a888", floor="#9a6a48", floor_b="#7a5034", base="#f0d2b4", base_sh="#c9a383", head="#8a5a3c")
    w = clamp01(warm)
    return {k: lib.mix(cold[k], hot[k], w) for k in cold}


def _quilt(x0, x1, y0, y1, P, t, seed, bump=0.0):
    """Одеяло-плед на переднем плане: верхний край волной, складки, лёгкое шевеление (bump — подскок кровати)."""
    n = 9
    top = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        top.append((x, y0 + 14 * math.sin(i * 1.7 + seed) + 6 * math.sin(t * 1.3 + i) - bump * 30 * math.sin(math.pi * i / n)))
    pts = [(x0 - 40, y1 + 400, 1)] + top + [(x1 + 40, y1 + 400, 1)]
    inner = blob([(x0 - 40, y0 + 90), (x1 + 40, y0 + 70), (x1 + 40, y1 + 400), (x0 - 40, y1 + 400)], P["quilt_sh"], .45)
    for i in range(6):
        fx = x0 + 90 + i * (x1 - x0 - 180) / 5
        inner += line([(fx, y0 + 30), (fx + 30 * math.sin(i + t * .7), y0 + 260), (fx - 20, y1 + 300)], 5, P["quilt_sh"], taper=.4, wmin=.3, seed=seed + i)
    inner += line([(x0, y0 + 26), (x1, y0 + 20)], 5, P["quilt_hi"], taper=.3, wmin=.4, seed=seed + 9, op=.8)
    return shape(pts, P["quilt"], inner, w=4.6, seed=seed + 20)


def hook_day(t, view="close", warm=0.0, bump=0.0):
    """Жёсткий день хука (и тёплая петля). См. шапку раздела 78."""
    P = _hd_pal(warm)
    w = clamp01(warm)
    o = [f'<rect x="-900" y="-900" width="2880" height="3720" fill="{P["wall"]}"/>']
    g = lib.lin_grad([(0, P["wall_hi"], 1), (.55, P["wall"], 1), (1, P["wall_sh"], 1)], 0, -400, 0, 1700, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-900" width="2880" height="3720" fill="url(#{g})"/>')
    if view == "close":
        # резкая тень оконной рамы косо по стене (окно за правым краем кадра): две створки-параллелограмма, крестовина — светом
        sh = P["shadow"]
        op = .55 - .15 * w
        for (ax, ay, bw, bh) in ((520, HD_SHADOW_TOP + 10, 300, 420), (850, HD_SHADOW_TOP + 60, 300, 420)):
            q = [(ax, ay, 1), (ax + bw, ay + 70, 1), (ax + bw - 160, ay + bh + 70, 1), (ax - 160, ay + bh, 1)]
            if w < .5:   # холод: тень рамы (тёмные полосы крестовины) — рисуем РАМУ тенью, стекло — светом стены
                o.append(blob([(ax - 30, ay - 26, 1), (ax + bw + 30, ay + 44, 1), (ax + bw - 130, ay + bh + 96, 1), (ax - 190, ay + bh + 26, 1)], sh, op * (1 - 2 * w)))
                o.append(blob(q, P["wall_hi"], 1 - 2 * w))
            else:        # закат: пятно света формы окна
                o.append(blob(q, sh, .55 * (2 * w - 1)))
        o.append(blob([(1000, HD_SHADOW_TOP - 10, 1), (1300, HD_SHADOW_TOP + 40, 1), (1300, 1200, 1), (930, 1200, 1)], P["wall_sh"], .35))
        # изголовье слева за Димой (край), матрас
        o.append(shape(lib.rrect(-900, 820, 140, 1300, 26), P["head"], blob(rect_pts(90, 820, 140, 1300), lib.mul(P["head"], (.85, .85, .87))), w=4.4, seed=7801))
        o.append(shape(lib.rrect(-900, HD_BED_Y - 40, 1980, HD_BED_Y + 120, 24), P["sheet"], blob(rect_pts(-900, HD_BED_Y + 60, 1980, HD_BED_Y + 122), P["sheet_sh"]),
                       w=4.0, seed=7802))
        bed = _quilt(-860, 1940, HD_BED_Y + 40, 2400, P, t, 7810, bump)
        an = dict(hip=HD_HIP, phone=HD_PHONE_BASE, bed_y=HD_BED_Y, text=HD_TEXT)
    else:
        # общий план: стена, плинтус, пол; кровать справа с подушкой; резкая тень рамы на стене над кроватью
        fl = HW_FL
        o.append(shape(rect_pts(-900, fl - 60, 1980, fl + 4), P["base"], blob(rect_pts(-900, fl - 12, 1980, fl + 4), P["base_sh"]), w=3.4, seed=7820))
        gf = lib.lin_grad([(0, P["floor"], 1), (1, P["floor_b"], 1)], 0, fl, 0, 2400, units="userSpaceOnUse")
        o.append(f'<rect x="-900" y="{f(fl + 4)}" width="2880" height="1400" fill="url(#{gf})"/>')
        for k, y in enumerate((1620, 1700, 1810, 1960)):
            o.append(line([(-900, y), (1980, y + 2)], 3, lib.mul(P["floor_b"], (.8, .8, .8)), taper=0, wmin=1, seed=7821 + k, op=.6))
        sh = P["shadow"]
        for (ax, ay) in ((600, 520), (860, 570)):
            q = [(ax, ay, 1), (ax + 220, ay + 50, 1), (ax + 110, ay + 350, 1), (ax - 110, ay + 300, 1)]
            o.append(blob([(ax - 24, ay - 20, 1), (ax + 244, ay + 34, 1), (ax + 128, ay + 376, 1), (ax - 136, ay + 322, 1)], sh, .5 * (1 - w)))
            o.append(blob(q, P["wall_hi"] if w < .5 else sh, 1 - w if w < .5 else .5))
        x0, x1, ty = HW_BED
        o.append(blob(rect_pts(x0 - 20, fl - 16, x1 + 60, fl + 30), "#000000", .18))
        for lx in (x0 + 30, x1 - 40):
            o.append(shape(rect_pts(lx - 16, ty + 120, lx + 16, fl), lib.mul(P["head"], (.8, .8, .82)), "", w=3.4, seed=7830 + int(lx) % 9))
        o.append(shape(lib.rrect(x1 - 30, ty - 300, x1 + 40, ty + 150, 16), P["head"], "", w=4.4, seed=7832))
        o.append(shape(lib.rrect(x0, ty + 60, x1, ty + 150, 10), lib.mul(P["head"], (.9, .9, .92)), "", w=4.0, seed=7833))
        o.append(shape(lib.rrect(x0, ty, x1, ty + 90, 20), P["sheet"], blob(rect_pts(x0, ty + 60, x1, ty + 92), P["sheet_sh"]), w=3.8, seed=7834))
        px, py = HW_PILLOW
        o.append(shape([(px - 150, py + 28, 1), (px - 160, py - 34), (px - 100, py - 70 + 40 * bump), (px + 80, py - 74), (px + 140, py - 40), (px + 136, py + 28, 1)],
                       "#f7f9fb", blob(rect_pts(px - 170, py + 6, px + 150, py + 30), P["sheet_sh"]), w=3.8, seed=7835))
        bl = [(x0 - 8, ty + 100, 1), (x0 - 14, ty - 6), (x0 + 200, ty - 30), (x1 - 330, ty - 34), (x1 - 300, ty + 100, 1)]
        bed = shape(bl, P["quilt"], blob(rect_pts(x0 - 14, ty + 60, x1 - 300, ty + 102), P["quilt_sh"], .7)
                    + "".join(line([(x0 + 110 + 120 * i, ty - 20), (x0 + 120 + 120 * i, ty + 96)], 3, P["quilt_sh"], taper=.3, wmin=.5, seed=7836 + i)
                              for i in range(4)), w=4.2, seed=7840)
        an = dict(stand=HW_STAND, pillow=HW_PILLOW, bed=HW_BED, fl=fl, text=HD_TEXT)
    sv = "#203048" if w < .5 else "#7a3a18"
    gv = lib.rad_grad([(0, sv, 0), (.7, sv, 0), (1, sv, .28)], 540, 960, 900, 1300)
    shade = f'<rect x="-900" y="-900" width="2880" height="3720" fill="url(#{gv})"/>'
    return dict(bg="".join(o), bed=bed, front="", shade=shade, cam=CAM78, anchors=an)


# ─────────────── ночь 78 ───────────────
N78 = dict(wall="#1d2440", wall_hi="#252d4e", wall_sh="#151a31", sheet="#3c4670", sheet_sh="#2b3356", quilt="#34406a", quilt_sh="#242d50",
           quilt_hi="#4a5684", wood="#2e2b40", wood_sh="#211f30", floor="#181b2c", floor_b="#10121e", frame="#46507a", base="#2a3152",
           base_sh="#1d2340", head="#2e2b40")
N78_GLASS = (150.0, 150.0, 930.0, 760.0)      # стекло окна над кроватью (s03)
N78_PILLOW = (250.0, 1110.0)                  # подушка (s03): голова полусидящего Димы — над ней
N78_BED_Y = 1060.0                            # верх матраса в s03


def _night_glass(x0, y0, x1, y1, t, seed=0):
    """Тёмное ночное стекло: глубокий синий, редкие звёзды, силуэт домов внизу с двумя-тремя окошками."""
    g = lib.lin_grad([(0, "#05081a", 1), (.7, "#0c1330", 1), (1, "#141c40", 1)], 0, 0, 0, 1)
    o = f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="url(#{g})"/>'
    r = rs(7860 + seed)
    for i in range(9):
        sx, sy = r.uniform(x0 + 20, x1 - 20), r.uniform(y0 + 20, y0 + (y1 - y0) * .45)
        a = .35 + .3 * math.sin(t * 2.1 + i * 1.9)
        o += f'<circle cx="{f(sx)}" cy="{f(sy)}" r="{f(r.uniform(1.8, 3.2))}" fill="#c8d0ff" opacity="{a:.2f}"/>'
    x = x0 - 10
    while x < x1:
        w_, h_ = r.uniform(90, 160), r.uniform(60, 150)
        o += blob(rect_pts(x, y1 - h_, x + w_, y1 + 10), "#03050f")
        if r.rand() < .45:
            o += blob(rect_pts(x + 24, y1 - h_ + 26, x + 42, y1 - h_ + 44), "#c9a24e", .55)
        x += w_ + r.uniform(4, 14)
    return o


def _glass_frame(x0, y0, x1, y1, col, seed):
    fr = 22
    o = []
    rim = rect_pts(x0 - fr, y0 - fr, x1 + fr, y1 + fr)
    hole = rect_pts(x0, y0, x1, y1)
    o.append(f'<path d="{lib.fill_d(rim)}{lib.fill_d(hole[::-1])}" fill="{col}" fill-rule="evenodd"/>')
    o.append(line(rim + [rim[0]], 4.0, INK, taper=0, wmin=1, seed=seed) + line(hole + [hole[0]], 3.0, INK, taper=0, wmin=1, seed=seed + 1))
    xm = (x0 + x1) / 2
    o.append(shape(rect_pts(xm - 8, y0, xm + 8, y1), col, "", w=2.8, seed=seed + 2))
    o.append(shape(rect_pts(x0 - fr - 30, y1 + fr, x1 + fr + 30, y1 + fr + 26), col, blob(rect_pts(x0 - fr - 30, y1 + fr + 16, x1 + fr + 30, y1 + fr + 26), "#000000", .3),
                   w=3.4, seed=seed + 3))
    return "".join(o)


def night78(t, view="window", glow=1.0):
    """Ночная спальня рилса 78 (см. шапку раздела 78)."""
    P = N78
    o = [f'<rect x="-900" y="-900" width="2880" height="3720" fill="{P["wall"]}"/>']
    g = lib.lin_grad([(0, P["wall_sh"], 1), (.5, P["wall"], 1), (1, P["wall_hi"], 1)], 0, -200, 0, 1500, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-900" width="2880" height="3720" fill="url(#{g})"/>')
    front = ""
    glass = None
    an = {}
    if view == "window":
        gx0, gy0, gx1, gy1 = N78_GLASS
        o.append(_night_glass(gx0, gy0, gx1, gy1, t))
        glass = N78_GLASS
        o.append(_glass_frame(gx0, gy0, gx1, gy1, P["frame"], 7870))
        by = N78_BED_Y
        o.append(shape(lib.rrect(-200, 820, 90, 1500, 30), P["head"], blob(rect_pts(50, 820, 90, 1500), P["wood_sh"]), w=4.4, seed=7875))
        o.append(shape(lib.rrect(-220, by, 1300, by + 160, 26), P["sheet"], blob(rect_pts(-220, by + 110, 1300, by + 162), P["sheet_sh"]), w=4.0, seed=7876))
        px, py = N78_PILLOW
        o.append(shape([(px - 220, py + 40, 1), (px - 230, py - 40), (px - 160, py - 96), (px + 90, py - 100), (px + 170, py - 60), (px + 166, py + 40, 1)],
                       "#4b5684", blob(rect_pts(px - 240, py + 10, px + 180, py + 42), P["sheet_sh"]), w=3.8, seed=7877))
        an = dict(pillow=N78_PILLOW, bed_y=by, glass=N78_GLASS)
    elif view == "mid":
        gx0, gy0, gx1, gy1 = (-60.0, 160.0, 520.0, 700.0)
        o.append(_night_glass(gx0, gy0, gx1, gy1, t, 1))
        glass = (gx0, gy0, gx1, gy1)
        o.append(_glass_frame(gx0, gy0, gx1, gy1, P["frame"], 7880))
        fl = 1520.0
        o.append(shape(rect_pts(-900, fl - 50, 1980, fl + 4), P["base"], "", w=3.4, seed=7881))
        o.append(f'<rect x="-900" y="{f(fl + 4)}" width="2880" height="1400" fill="{P["floor"]}"/>')
        by = 1080.0
        o.append(shape(lib.rrect(-40, 700, 60, 1500, 20), P["head"], "", w=4.4, seed=7882))
        o.append(shape(lib.rrect(-60, by, 900, by + 170, 24), P["sheet"], blob(rect_pts(-60, by + 120, 900, by + 172), P["sheet_sh"]), w=4.0, seed=7883))
        for lx in (40, 860):
            o.append(shape(rect_pts(lx - 14, by + 170, lx + 14, fl), P["wood_sh"], "", w=3.2, seed=7884 + lx % 7))
        o.append(shape([(80, by + 20, 1), (70, by - 50), (130, by - 96), (330, by - 100), (390, by - 60), (386, by + 20, 1)], "#4b5684",
                       blob(rect_pts(70, by - 10, 400, by + 22), P["sheet_sh"]), w=3.8, seed=7885))
        nx0, nx1, ny = 930.0, 1180.0, 1180.0
        o.append(shape(rect_pts(nx0, ny, nx1, fl - 6), P["wood"], blob(rect_pts(nx1 - 26, ny, nx1, fl - 6), P["wood_sh"]), w=4.0, seed=7886))
        o.append(shape(lib.rrect(nx0 - 14, ny - 22, nx1 + 14, ny + 6, 5), lib.mix(P["wood"], "#ffffff", .06), "", w=3.6, seed=7887))
        front = _quilt(-60, 880, by + 30, 1560, P, t, 7890)
        an = dict(pillow=(240.0, by - 50), bed_top=by, cat=(640.0, by + 30), nstand=((nx0 + nx1) / 2, ny - 20), fl=fl, glass=glass)
    else:   # top: кровать сверху
        o.append(f'<rect x="-900" y="-900" width="2880" height="3720" fill="{P["floor"]}"/>')
        for i in range(12):
            o.append(line([(-900 + i * 260, -900), (-900 + i * 260 + 4, 2820)], 3, P["floor_b"], taper=0, wmin=1, seed=7900 + i, op=.7))
        bx0, bx1, by0, by1 = 90.0, 980.0, 120.0, 2000.0
        o.append(blob(rect_pts(bx0 + 30, by0 + 30, bx1 + 40, by1 + 40), "#000000", .35))
        o.append(shape(lib.rrect(bx0 - 30, by0 - 60, bx1 + 30, by0 + 40, 20), P["head"], "", w=4.4, seed=7912))
        o.append(shape(lib.rrect(bx0, by0, bx1, by1, 30), P["sheet"], "", w=4.2, seed=7913))
        o.append(shape(lib.rrect(260, by0 + 50, 820, by0 + 330, 80), "#4b5684", blob(ellipse_pts(540, by0 + 200, 200, 70, 18), P["sheet_sh"], .7),
                       w=4.0, seed=7914))
        nx, ny = 1060.0, 300.0
        o.append(shape(rect_pts(nx - 70, ny - 120, nx + 160, ny + 140), P["wood"], blob(rect_pts(nx - 70, ny + 100, nx + 160, ny + 140), P["wood_sh"]),
                       w=4.0, seed=7915))
        front = ""   # одеяло сверху — сцена (оно двигается вместе с Димой); палитра N78 — quilt
        an = dict(bed=(bx0, by0, bx1, by1), pillow=(540.0, by0 + 190), nstand=(nx + 40, ny))
    dark = f'<rect x="-900" y="-900" width="2880" height="3720" fill="#03050c" opacity="{.38 - .18 * clamp01(glow):.3f}"/>'
    gc = lib.clip_rect(glass[0], glass[1], glass[2] - glass[0], glass[3] - glass[1]) if glass else None
    return dict(bg="".join(o), front=front, dark=dark, glass=glass, glass_clip=gc, anchors=an, cam=CAM78, P=P)


# ─────────────── мастерская изобретателя ───────────────
WS_BENCH = (120.0, 1180.0, 980.0)      # x0, верх столешницы y, x1
WS_WIN = (520.0, 180.0, 1000.0, 760.0)


def workshop(t, mess_u=0.0):
    """Мастерская (см. шапку раздела 78)."""
    m = clamp01(mess_u)
    wall, wall_sh, plank = lib.mix("#c89a6a", "#9a7458", m * .5), lib.mix("#a87a50", "#7a5840", m * .5), lib.mix("#b78a5c", "#8c6a4e", m * .5)
    o = [f'<rect x="-900" y="-900" width="2880" height="3720" fill="{wall}"/>']
    for i in range(-6, 18):
        x = i * 92.0
        o.append(line([(x, -900), (x + 2, 1500)], 3.0, wall_sh, taper=0, wmin=1, seed=7930 + i, op=.75))
        o.append(blob(rect_pts(x + 8, -900, x + 30, 1500), plank, .35))
    x0, y0, x1, y1 = WS_WIN
    sky = lib.lin_grad([(0, lib.mix("#9cc6e8", "#e6a072", m), 1), (1, lib.mix("#d9ecf6", "#f6d29a", m), 1)], 0, 0, 0, 1)
    o.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="url(#{sky})"/>')
    houses = []
    r = rs(7940)
    x = x0 + 6
    while x < x1 - 40:
        w_, h_ = r.uniform(110, 150), r.uniform(150, 280)
        hb = (x, y1 - h_, x + w_, y1)
        houses.append(hb)
        col = ["#d7a86e", "#b9c4cf", "#c98a74", "#a9b98e"][len(houses) % 4]
        roof = [(x - 8, y1 - h_ + 2), (x + w_ / 2, y1 - h_ - 60), (x + w_ + 8, y1 - h_ + 2)]
        o.append(shape(roof, "#8a4e3a", "", w=3.0, seed=7941 + len(houses)))
        o.append(shape(rect_pts(*hb), col, blob(rect_pts(x + w_ * .3, y1 - h_ * .55, x + w_ * .55, y1 - h_ * .3), "#fff2c8", .8), w=3.0, seed=7950 + len(houses)))
        x += w_ + r.uniform(10, 30)
    o.append(_glass_frame(x0, y0, x1, y1, "#e9dcc2", 7960))
    # лампа над верстаком: абажур и пятно света формы абажура на стене
    lx = 360.0
    o.append(line([(lx, -900), (lx, 330)], 4, "#3a2a20", taper=0, wmin=1, seed=7965))
    o.append(blob([(lx - 60, 400), (lx + 60, 400), (lx + 200, 900), (lx - 200, 900)], "#ffe2a0", .16))
    o.append(shape([(lx - 40, 330, 1), (lx + 40, 330, 1), (lx + 80, 410, 1), (lx - 80, 410, 1)], "#4f7a6a", "", w=3.6, seed=7966))
    o.append(blob(ellipse_pts(lx, 410, 74, 9, 12), "#fff6d8", .9))
    # инструменты на стене (без букв): ножницы, моток, линейка без делений
    o.append(line([(120, 520), (300, 520)], 10, "#c9b48a", taper=0, wmin=1, seed=7967))
    o.append(shape(ellipse_pts(200, 660, 56, 56, 18), "#c96f4a", blob(ellipse_pts(200, 660, 20, 20, 10), wall), w=3.4, seed=7968))
    for k in range(int(m * 9)):   # беспорядок: обрезки-полоски на стене
        rx_, ry_ = r.uniform(80, 480), r.uniform(800, 1100)
        o.append(blob(lib.T(rect_pts(rx_, ry_, rx_ + 120, ry_ + 26), 0, 0, 1, r.uniform(-30, 30), rx_, ry_),
                      ["#e8645a", "#f2c14e", "#5fb3a8", "#7a8ee0"][k % 4], .85))
    bx0, by, bx1 = WS_BENCH
    o.append(f'<rect x="-900" y="1500" width="2880" height="1400" fill="{lib.mix("#7a5638", "#5a4030", m * .5)}"/>')
    o.append(line([(-900, 1500), (1980, 1502)], 4, INK, taper=0, wmin=1, seed=7969))
    bench = shape(rect_pts(bx0, by, bx1, by + 50), "#9a6a42", blob(rect_pts(bx0, by + 34, bx1, by + 50), "#6e4a2c"), w=4.4, seed=7970)
    for lx2 in (bx0 + 40, bx1 - 70):
        bench += shape(rect_pts(lx2, by + 50, lx2 + 34, 1560), "#7a5232", "", w=3.6, seed=7971 + int(lx2) % 5)
    dark = f'<rect x="-900" y="-900" width="2880" height="3720" fill="#2a1408" opacity="{.25 * m:.3f}"/>' if m > .01 else ""
    return dict(bg="".join(o), bench=bench, front=dark, houses=houses, win=WS_WIN, cam=CAM78,
                anchors=dict(bench=WS_BENCH, stand=(700.0, 1560.0), floor=1500.0))


# ─────────────── вечер: кресло у окна ───────────────
EC_WIN = (560.0, 160.0, 1060.0, 900.0)
EC_HIP = (430.0, 1150.0)


def evening_chair(t, sun=1.0):
    """Кресло у окна на закате (см. шапку раздела 78)."""
    s = clamp01(sun)
    o = ['<rect x="-900" y="-900" width="2880" height="3720" fill="#c48a66"/>']
    g = lib.lin_grad([(0, "#a8705a", 1), (.6, "#c99272", 1), (1, "#b07a5c", 1)], 0, -200, 0, 1500, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-900" width="2880" height="3720" fill="url(#{g})"/>')
    x0, y0, x1, y1 = EC_WIN
    sky = lib.lin_grad([(0, "#5a5a9a", 1), (.45, "#e88a6a", 1), (1, "#ffd08a", 1)], 0, 0, 0, 1)
    o.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="url(#{sky})"/>')
    sy_ = y1 - 170 + 30 * (1 - s) + 6 * math.sin(t * .4)
    o.append(f'<circle cx="{f(x0 + 260)}" cy="{f(sy_)}" r="120" fill="#ffe6a0" opacity=".35"/>')
    o.append(shape(ellipse_pts(x0 + 260, sy_, 64, 64, 22), "#ffd36a", "", w=3.0, seed=7980))
    r = rs(7981)
    x = x0 - 10
    while x < x1:
        w_, h_ = r.uniform(80, 140), r.uniform(80, 180)
        o.append(blob(rect_pts(x, y1 - h_, x + w_, y1 + 10), "#6a4060"))
        x += w_ + r.uniform(6, 16)
    o.append(_glass_frame(x0, y0, x1, y1, "#f0dcc0", 7982))
    # закатный свет: пятно формы окна косо на стене и полу слева (чёткие края)
    lt = _sun_quad((x0 - 520, y0 + 360), (420, 80), (-120, 560), "#ffc27a", "#ffd89a", inset=.06)
    o.append(f'<g opacity="{.45 * s:.3f}">{lt}</g>')
    fl = 1452.0                      # пол на уровне ступней сидящего Димы (people.dima_chair78)
    o.append(shape(rect_pts(-900, fl - 50, 1980, fl + 4), "#e6c4a2", "", w=3.4, seed=7983))
    o.append(f'<rect x="-900" y="{f(fl + 4)}" width="2880" height="1400" fill="#7a4e32"/>')
    # кресло: спинка, сиденье, подлокотники (сиденье — подушка)
    hx, hy = EC_HIP
    cc, csh = "#7a9a6a", "#5a7a4e"
    back = shape(lib.rrect(hx - 260, hy - 560, hx + 240, hy + 40, 90), cc, blob(rect_pts(hx - 260, hy - 200, hx + 240, hy + 40), csh, .6)
                 + line([(hx - 200, hy - 480), (hx + 180, hy - 480)], 4, csh, taper=.3, wmin=.4, seed=7984), w=4.6, seed=7985)
    back += shape(lib.rrect(hx - 300, hy - 20, hx + 380, hy + 220, 40), cc, blob(rect_pts(hx - 300, hy + 150, hx + 380, hy + 222), csh), w=4.4, seed=7986)
    for lx in (hx - 250, hx + 320):
        back += shape(rect_pts(lx - 18, hy + 220, lx + 18, fl), "#5a3a24", "", w=3.4, seed=7987 + int(lx) % 7)
    armL = shape(lib.rrect(hx - 360, hy - 160, hx - 220, hy + 230, 50), cc, blob(rect_pts(hx - 360, hy + 100, hx - 220, hy + 230), csh, .7), w=4.4, seed=7988)
    armR = shape(lib.rrect(hx + 300, hy - 140, hx + 450, hy + 230, 50), cc, blob(rect_pts(hx + 300, hy + 100, hx + 450, hy + 230), csh, .7), w=4.4, seed=7989)
    glow = lib.rad_grad([(0, "#ffb070", .0), (.6, "#ffb070", 0), (1, "#5a2a10", .25)], 540, 960, 900, 1300)
    light = f'<rect x="-900" y="-900" width="2880" height="3720" fill="url(#{glow})"/>'
    return dict(bg="".join(o), chair_back=back + armL, chair_front=armR, light=light, cam=CAM78,
                anchors=dict(hip=EC_HIP, arm=(hx + 375, hy - 150), arm_l=(hx - 290, hy - 170), knees=(hx + 260, hy - 30), win=EC_WIN, fl=fl))


# ═════════════════════════════════════════ РИЛС 80 «Мама была права» (группа C) ═════════════════════════════════════════
# Букв и цифр нет нигде. Свет — пятнами с чёткой формой.
#
# СТЕНА ХУКА И ПЕТЛИ — hook_wall(t, warm=0.0, desk=False) -> dict(bg, floor, light, shade, anchors, cam). КООРДИНАТЫ КАДРА 1080×1920
#   (камера по умолчанию CAM80 = (540, 960, 1.0)). Голая светлая стена, жёсткий тёплый свет лампы СБОКУ СЛЕВА (лампа за кадром,
#   точка света W80_LAMP): большое светлое пятно с резким краем, справа и у пола стена темнее; пол с плинтусом W80_FL.
#   Зона надписи W80_TEXT = (60, 140, 1020, 430) — только чистая стена (тени и предметы ниже W80_SHADOW_TOP).
#   Тени на стене — wall_shadow(svg, op, col, blur) (плоский силуэт любого рисунка) и shadow_tremble(t) (дрожь лампы: dx, dy, dk).
#   warm 0…1 — тот же ракурс тёплым вечером (петля s18); desk=True — внизу стол поперёк кадра (верх столешницы W80_DESK_Y),
#   лампа на столе слева (anchors["lamp"] — точка лампочки, anchors["cat"] — где сидит кот на столе у лампы).
#   Порядок: bg → [тени на стене] → light (свет лампы поверх стены и теней — тени им НЕ светлеют, он только по стене) → [люди,
#   предметы] → floor (ничего; пол в bg) → shade (виньетка поверх всего).
#
# ТЁМНАЯ КОМНАТА ПОВОРОТА — turn_dark(t, reveal=1.0) -> dict(bg, pool, shade, anchors, cam). КООРДИНАТЫ КАДРА. Почти чёрная синяя
#   стена, тусклое холодное пятно света на ней (anchors["pool"] = (cx, cy, rx, ry)) — в нём проступают тени (класть их ПОСЛЕ
#   pool цветом T80_SHADOW); пол на W80_FL. reveal 0…1 — пятно и пол проявляются из темноты.
#
# КОМНАТА ДИМЫ ВЕЧЕРОМ — room_night(t, lamp=1.0) -> dict(bg, bed, front, light, anchors, cam). КООРДИНАТЫ КАДРА. Тёплый вечер:
#   стена, окно в сумерках вверху слева (N80_WIN), тумбочка с ночником справа, кровать поперёк кадра (верх матраса N80_BED_Y,
#   край у зрителя). anchors: sit — таз Димы, сидящего на краю кровати лицом к нам (N80_SIT), floor — пол, cat — где кот
#   стоит на полу перед Димой (N80_CAT). Порядок: bg → [Дима] → bed (передний край кровати, ПОСЛЕ таза и ног Димы? нет — до
#   ног: bed — ткань матраса у зрителя, класть ПЕРЕД Димой, если Дима сидит на краю — тогда ноги поверх) → [кот] → light.
#
# СТОЛ У ОКНА ДНЁМ / ВЕЧЕРОМ — desk80(t, light="day"|"evening", grey=0.0) -> dict как desk_scene (МИРОВЫЕ координаты комнаты
#   рилса 64/70, Дима на стуле SIT слева лицом вправо), плюс окно WIN74 над столом (днём солнце, вечером закат) и anchors:
#   sill — середина подоконника (кот на подоконнике), paper — где лежит лист, phone — где лежит телефон, cloud — где висит
#   облачко над головой сидящего Димы. Порядок слоёв — как desk_scene (bg → chair_back → desk_top → pool → [legs] → desk_legs →
#   chair_seat → [тело] → предметы → [ближняя рука] → lamp). Камеры: CAM80_DESK_MID (Дима по пояс со столом и окном),
#   CAM80_DESK_WIDE (общий), CAM80_DESK_CLOSE (лицо и руки над столом). grey 0…1 — цвета выцветают в серый (grey_tint).
#   grey_tint(svg, u) — снять насыщенность любого куска (облако тоски).
#
# ОТТАВА ЗИМОЙ — ottawa(t) -> dict(bg, snow, anchors, cam). МИРОВЫЕ координаты x −700…1900 (панорама). Бледное зимнее небо,
#   замёрзший канал по диагонали (лёд, снег по берегам, конькобежцев ставит сцена на линии anchors["ice"]), ели в снегу, старое
#   каменное здание университета слева с большим тёплым окном (anchors["uni_win"] = x0, y0, x1, y1 — учёных ставит сцена
#   внутрь, clip-path id в anchors["win_clip"]), фонари без надписей. snow — падающий снег (поверх всего).
#   Камеры: CAM80_UNI (окно крупно), CAM80_CANAL (над каналом).
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
CAM80 = (540.0, 960.0, 1.0)
W80_FL = 1330.0
W80_TEXT = (60.0, 140.0, 1020.0, 430.0)
W80_SHADOW_TOP = 450.0
W80_LAMP = (-260.0, 1060.0)
W80_DESK_Y = 1150.0
T80_SHADOW = "#05070f"


def _w80_pal(warm):
    cold = dict(wall="#d9d2c4", lit="#fbf3df", lit_core="#fffaf0", dark="#9f978a", base="#ece6d8", base_sh="#bdb3a3", floor="#a88d70",
                floor_b="#7c6550", floor_ln="#5e4a39", shadow="#2a2430", vign="#1a1420")
    hot = dict(wall="#c99a72", lit="#f7cf94", lit_core="#ffe6b4", dark="#8a5e44", base="#e8c49c", base_sh="#b48a66", floor="#8f5d3a",
               floor_b="#6a4128", floor_ln="#4c2e1a", shadow="#3a2216", vign="#3a1a08")
    w = clamp01(warm)
    return {k: lib.mix(cold[k], hot[k], w) for k in cold}


def shadow_tremble(t, amp=1.0):
    """Дрожь лампы: (dx, dy, dk) для теней на стене — нервное мерцание, не ровная синусоида."""
    dx = amp * (5 * math.sin(t * 23.0) + 3 * math.sin(t * 41.0 + 1.3) + 2 * math.sin(t * 67.0))
    dy = amp * (3 * math.sin(t * 19.0 + .7) + 2 * math.sin(t * 53.0))
    dk = amp * (.008 * math.sin(t * 29.0) + .005 * math.sin(t * 47.0 + 2.1))
    return dx, dy, dk


def wall_shadow(svg_, op=0.82, col="#2a2430", blur=2.5):
    """Плоский силуэт любого рисунка цветом col (тень на стене): все пиксели → col, альфа = альфа рисунка × op; лёгкий размыв края."""
    r, g, b = (int(col[i:i + 2], 16) / 255 for i in (1, 3, 5))
    fid = lib.uid("wsh")
    bl = f'<feGaussianBlur stdDeviation="{blur:.2f}"/>' if blur > 0 else ""
    lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">'
                    f'<feColorMatrix type="matrix" values="0 0 0 0 {r:.4f} 0 0 0 0 {g:.4f} 0 0 0 0 {b:.4f} 0 0 0 {op:.4f} 0"/>{bl}</filter>')
    return f'<g filter="url(#{fid})">{svg_}</g>'


def grey_tint(svg_, u):
    """Цвета выцветают в серый (u 0…1): насыщенность → 0, чуть холоднее и темнее."""
    if u <= .005:
        return svg_
    fid = lib.uid("gry")
    s = 1 - .92 * clamp01(u)
    lib.DEFS.append(f'<filter id="{fid}" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="{s:.3f}"/>'
                    f'<feComponentTransfer><feFuncR type="linear" slope="{1 - .1 * u:.3f}"/><feFuncG type="linear" slope="{1 - .08 * u:.3f}"/>'
                    f'<feFuncB type="linear" slope="{1 - .03 * u:.3f}"/></feComponentTransfer></filter>')
    return f'<g filter="url(#{fid})">{svg_}</g>'


def hook_wall(t, warm=0.0, desk=False):
    """Стена хука (warm=0) и петли (warm=1, desk=True). См. шапку раздела 80."""
    P = _w80_pal(warm)
    fl = W80_FL
    o = [f'<rect x="-900" y="-900" width="2880" height="3720" fill="{P["dark"]}"/>']
    g = lib.lin_grad([(0, P["wall"], 1), (1, P["dark"], 1)], 0, 0, 1, 0)
    o.append(f'<rect x="-900" y="-900" width="2880" height="{f(fl + 900)}" fill="url(#{g})"/>')
    # пятно света лампы: резкий эллипс с чёткой кромкой (жёсткий свет) + ядро; лампа слева за кадром, чуть ниже середины
    fk = 1 + .012 * math.sin(t * 31) + .008 * math.sin(t * 57)
    lx, ly = 300.0, 860.0
    pool = lib.rad_grad([(0, P["lit_core"], 1), (.45, P["lit"], 1), (.93, P["lit"], .92), (1, P["lit"], 0)], lx, ly, 900 * fk, 760 * fk)
    o.append(f'<rect x="-900" y="-900" width="2880" height="{f(fl + 900)}" fill="url(#{pool})"/>')
    # редкие следы обоев и плинтус
    for i in range(-3, 10):
        x = i * 170.0 + 60
        o.append(line([(x, -900), (x + 2, fl - 40)], w=1.6, color=P["dark"], taper=0.0, wmin=1, seed=8000 + i, op=.18))
    o.append(shape(rect_pts(-900, fl - 46, 1980, fl + 4), P["base"], blob(rect_pts(-900, fl - 12, 1980, fl + 4), P["base_sh"]), w=3.4, seed=8020))
    gf = lib.lin_grad([(0, P["floor"], 1), (1, P["floor_b"], 1)], 0, fl, 0, 2300, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="{f(fl + 4)}" width="2880" height="1400" fill="url(#{gf})"/>')
    for k, y in enumerate((1395, 1490, 1620, 1800)):
        o.append(line([(-900, y), (1980, y + 3)], 3, P["floor_ln"], taper=0, wmin=1, seed=8030 + k, op=.55))
    # свет лампы на полу — полоса с чёткой кромкой
    o.append(blob([(-900, fl + 6, 1), (760, fl + 6, 1), (980, fl + 220, 1), (-900, fl + 260, 1)], P["lit"], .28))
    an = dict(fl=fl, text=W80_TEXT, lamp=W80_LAMP, shadow_top=W80_SHADOW_TOP)
    front = ""
    if desk:   # стол поперёк кадра, лампа на столе слева
        dy = W80_DESK_Y
        dw, dsh, dhi = "#b07a48", "#7e5230", "#cf9a64"
        front += shape(rect_pts(-900, dy + 30, 1980, 2400), dsh, blob(rect_pts(-900, dy + 30, 1980, dy + 60), "#000000", .25), w=4.0, seed=8040)
        front += shape(lib.rrect(-900, dy - 40, 1980, dy + 34, 8), dw, blob(rect_pts(-900, dy - 40, 1980, dy - 28), dhi, .8)
                       + "".join(line([(-900, dy - 12 + 9 * i), (1980, dy - 10 + 9 * i)], 2, dsh, taper=0, wmin=1, seed=8041 + i, op=.4) for i in range(3)),
                       w=4.2, seed=8045)
        an.update(desk_y=dy - 30, lamp=(140.0, dy - 330), cat=(330.0, dy - 22))
    sv = P["vign"]
    gv = lib.rad_grad([(0, sv, 0), (.62, sv, 0), (1, sv, .42)], 520, 900, 880, 1250)
    shade = f'<rect x="-900" y="-900" width="2880" height="3720" fill="url(#{gv})"/>'
    return dict(bg="".join(o), floor="", front=front, light="", shade=shade, anchors=an, cam=CAM80, P=P)


def turn_dark(t, reveal=1.0):
    """Тёмная синяя комната поворота: стена, тусклое холодное пятно (тени проступают в нём), пол. См. шапку раздела 80."""
    fl = W80_FL
    rv = clamp01(reveal)
    o = ['<rect x="-900" y="-900" width="2880" height="3720" fill="#070a18"/>']
    o.append(f'<rect x="-900" y="-900" width="2880" height="{f(fl + 900)}" fill="#0d1226"/>')
    pcx, pcy, prx, pry = 560.0, 820.0, 560.0, 470.0
    fk = 1 + .015 * math.sin(t * 2.3)
    g = lib.rad_grad([(0, "#2c3a6e", .95 * rv), (.7, "#1d2850", .8 * rv), (1, "#0d1226", 0)], pcx, pcy, prx * fk, pry * fk)
    o.append(f'<rect x="-900" y="-900" width="2880" height="{f(fl + 900)}" fill="url(#{g})"/>')
    o.append(shape(rect_pts(-900, fl - 46, 1980, fl + 4), lib.mix("#0d1226", "#25305a", rv), "", w=3.0, seed=8060))
    gf = lib.lin_grad([(0, lib.mix("#070a18", "#141a34", rv), 1), (1, "#05070f", 1)], 0, fl, 0, 2300, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="{f(fl + 4)}" width="2880" height="1400" fill="url(#{gf})"/>')
    o.append(blob(ellipse_pts(560, fl + 70, 420, 60, 24), "#2c3a6e", .35 * rv))
    gv = lib.rad_grad([(0, "#000000", 0), (.6, "#000000", 0), (1, "#000000", .6)], 540, 900, 820, 1200)
    shade = f'<rect x="-900" y="-900" width="2880" height="3720" fill="url(#{gv})"/>'
    return dict(bg="".join(o), pool="", shade=shade, anchors=dict(pool=(pcx, pcy, prx, pry), fl=fl), cam=CAM80)


# ─────────────── комната Димы вечером (s07, группа B) ───────────────
N80_WIN = (120.0, 230.0, 560.0, 760.0)
N80_BED_Y = 1150.0
N80_SIT = (540.0, 1160.0)
N80_FL = 1480.0
N80_CAT = (800.0, 1478.0)
N80_NSTAND = (900.0, 1100.0, 1060.0)   # x0, верх, x1


def room_night(t, lamp=1.0):
    """Комната Димы вечером: тёплая стена, окно в сумерках, ночник на тумбочке, кровать поперёк кадра. См. шапку раздела 80."""
    fl = N80_FL
    o = ['<rect x="-900" y="-900" width="2880" height="3720" fill="#6a4a52"/>']
    g = lib.lin_grad([(0, "#5b4058", 1), (.6, "#8a6066", 1), (1, "#a8746a", 1)], 0, -200, 0, fl, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="-900" width="2880" height="{f(fl + 900)}" fill="url(#{g})"/>')
    for i in range(-3, 10):
        x = i * 160.0 + 40
        o.append(line([(x, -900), (x + 2, fl - 40)], w=1.6, color="#5a3e4c", taper=0.0, wmin=1, seed=8100 + i, op=.3))
    o.append(window74(*N80_WIN, sky_u=.47, t=t, dark=0.0))
    # ночник: тёплое пятно на стене над тумбочкой с чёткой кромкой
    x0, ny, x1 = N80_NSTAND
    lx = (x0 + x1) / 2
    lu = clamp01(lamp) * (1 + .02 * math.sin(t * 7.3))
    if lu > .01:
        o.append(blob(ellipse_pts(lx, ny - 220, 330, 260, 30), "#ffcf8a", .32 * lu))
        o.append(blob(ellipse_pts(lx, ny - 210, 190, 150, 26), "#ffe2a8", .3 * lu))
    o.append(shape(rect_pts(-900, fl - 40, 1980, fl + 4), "#b98a7a", blob(rect_pts(-900, fl - 10, 1980, fl + 4), "#8a6058"), w=3.2, seed=8110))
    gf = lib.lin_grad([(0, "#7a4c34", 1), (1, "#5a3422", 1)], 0, fl, 0, 2300, units="userSpaceOnUse")
    o.append(f'<rect x="-900" y="{f(fl + 4)}" width="2880" height="1400" fill="url(#{gf})"/>')
    for k, y in enumerate((1560, 1680, 1850)):
        o.append(line([(-900, y), (1980, y + 3)], 3, "#43291a", taper=0, wmin=1, seed=8111 + k, op=.5))
    # тумбочка и ночник
    o.append(shape(rect_pts(x0, ny, x1, fl - 4), "#7a5038", blob(rect_pts(x0, ny, x1, ny + 18), "#9a6a4a") +
                   line([(x0 + 14, ny + 170), (x1 - 14, ny + 170)], 3, INK, taper=0, wmin=1, seed=8115) +
                   blob(ellipse_pts(lx, ny + 120, 10, 7, 10), "#d8b07a"), w=4.0, seed=8116))
    o.append(night_lamp73(lx, ny, 1.0, lamp, t))
    # кровать: изголовье слева, матрас поперёк, одеяло
    by = N80_BED_Y
    o.append(shape(lib.rrect(-120, by - 380, 70, fl - 10, 20), "#6b4a3a", blob(rect_pts(30, by - 380, 70, fl - 10), "#4e3428", .6), w=4.2, seed=8120))
    o.append(shape(rect_pts(-80, by + 120, 860, fl - 6), "#5a3e30", "", w=3.6, seed=8121))
    o.append(shape(lib.rrect(-100, by - 20, 880, by + 130, 22), "#e9dccb", blob(rect_pts(-100, by + 80, 880, by + 132), "#c9b8a4"), w=3.8, seed=8122))
    o.append(shape([(-60, by - 10, 1), (-70, by - 90), (40, by - 120), (200, by - 116), (240, by - 70), (230, by - 6, 1)], "#f4ece0",
                   blob(rect_pts(-70, by - 30, 240, by - 6), "#d6c8b4"), w=3.8, seed=8123))
    bed = shape([(250, by + 4, 1), (260, by - 40), (500, by - 56), (870, by - 44), (890, by + 6, 1), (890, by + 130, 1), (250, by + 130, 1)],
                "#8a5a8a", blob(rect_pts(250, by + 80, 890, by + 132), "#6a4068", .8) +
                "".join(line([(330 + 130 * i, by - 40), (340 + 130 * i, by + 126)], 3, "#6a4068", taper=.3, wmin=.5, seed=8124 + i) for i in range(5)),
                w=4.2, seed=8130)
    gv = lib.rad_grad([(0, "#1a0c18", 0), (.6, "#1a0c18", 0), (1, "#1a0c18", .45)], 540, 900, 860, 1250)
    light = f'<rect x="-900" y="-900" width="2880" height="3720" fill="url(#{gv})"/>'
    an = dict(sit=N80_SIT, floor=fl, cat=N80_CAT, bed_y=by, nstand=N80_NSTAND, win=N80_WIN)
    return dict(bg="".join(o), bed=bed, front="", light=light, anchors=an, cam=CAM80)


# ─────────────── стол у окна днём / вечером (s08–s11, s15–s17) ───────────────
CAM80_DESK_MID = (700.0, 840.0, 1.3)
CAM80_DESK_WIDE = (760.0, 980.0, 0.9)
CAM80_DESK_CLOSE = (640.0, 780.0, 1.9)
SILL80 = (1060.0, 728.0)
PAPER80 = (760.0, DESK_TOP - 50.0)
PHONE80 = (1000.0, DESK_TOP - 34.0)


def desk80(t, light="day", grey=0.0):
    """Стол у окна днём ("day") или вечером ("evening"): desk_scene + окно WIN74 над столом. См. шапку раздела 80."""
    mode = "day" if light == "day" else "evening"
    d = desk_scene(t, mode, lamp_on=0.0 if light == "day" else 1.0)
    sky = .25 if light == "day" else .47
    bg = d["bg"] + window74(*WIN74, sky_u=sky, t=t, dark=0.0)
    if light != "day":
        fl = light_(t, 1.0)
        bg += _light_pool73(LAMP[0] - 90, LAMP[1] - 260, 230 * fl, 170 * fl, t, LAMP_GLOW, .2, 8150, 1.2)
    out = dict(d)
    out["bg"] = grey_tint(bg, grey) if grey > .005 else bg
    hx, hy = SIT
    out.update(anchors=dict(sill=SILL80, paper=PAPER80, phone=PHONE80, cloud=(hx + 40, hy - 760), sit=SIT, lamp=LAMP, desk_top=DESK_TOP),
               cam_mid=CAM80_DESK_MID, cam_wide=CAM80_DESK_WIDE, cam_close=CAM80_DESK_CLOSE, sit=SIT)
    return out


# ─────────────── зимняя Оттава (s12) ───────────────
OT_UNI_WIN = (-330.0, 420.0, 90.0, 900.0)
OT_ICE_Y = 1330.0
CAM80_UNI = (-120.0, 760.0, 1.45)
CAM80_CANAL = (900.0, 1060.0, 1.0)


def _fir(x, y, h, seed, col="#2f5a48", snow="#f6f8fb"):
    """Ель в снегу: ярусы-треугольники, на каждом снежная шапка."""
    r = rs(seed)
    o = [shape(rect_pts(x - h * .04, y - h * .12, x + h * .04, y), "#5a4030", "", w=2.6, seed=seed)]
    n = 4
    for i in range(n):
        yb = y - h * .1 - i * h * .21
        w_ = h * (.36 - .07 * i)
        tip = yb - h * .32
        pts = [(x - w_, yb), (x - w_ * .3, yb - h * .06), (x, tip), (x + w_ * .3, yb - h * .06), (x + w_, yb)]
        sn = blob([(x - w_ * .55, yb - h * .1), (x, tip + h * .05), (x + w_ * .5, yb - h * .12), (x + w_ * .2, yb - h * .07 + r.uniform(-4, 4)),
                   (x - w_ * .2, yb - h * .08)], snow, .95)
        o.append(shape(pts, col, sn + blob([(x - w_, yb), (x + w_, yb), (x + w_ * .7, yb - h * .03), (x - w_ * .7, yb - h * .03)], snow, .9),
                       w=3.0, seed=seed + 1 + i))
    return "".join(o)


def ottawa(t):
    """Зимняя Оттава: небо, здание университета с тёплым окном, замёрзший канал, ели, снег. См. шапку раздела 80."""
    o = ['<rect x="-1500" y="-900" width="4400" height="3720" fill="#dfe7ee"/>']
    g = lib.lin_grad([(0, "#b9cde0", 1), (.6, "#e4ebf1", 1), (1, "#f4f0e8", 1)], 0, -300, 0, 1100, units="userSpaceOnUse")
    o.append(f'<rect x="-1500" y="-900" width="4400" height="2100" fill="url(#{g})"/>')
    # бледное зимнее солнце
    o.append(f'<circle cx="1320" cy="260" r="90" fill="#fff6dc" opacity=".55"/>')
    o.append(shape(ellipse_pts(1320, 260, 52, 52, 18), "#fff0c4", "", w=2.4, seed=8200))
    # дальний берег: холмы и лес силуэтом, город — простые крыши без вывесок
    o.append(blob([(-1500, 1000), (-900, 900), (-300, 950), (300, 880), (900, 930), (1500, 860), (2900, 940), (2900, 1200), (-1500, 1200)], "#9fb2c4"))
    r = rs(8201)
    x = 200.0
    while x < 2600:
        w_ = r.uniform(80, 150)
        h_ = r.uniform(60, 160)
        o.append(shape(rect_pts(x, 1000 - h_, x + w_, 1040), "#aebdcc", blob([(x - 8, 1000 - h_), (x + w_ / 2, 1000 - h_ - 40), (x + w_ + 8, 1000 - h_)],
                                                                               "#f4f6f9", .95), w=2.2, seed=8202 + int(x)))
        x += w_ + r.uniform(10, 40)
    for i in range(14):
        o.append(_fir(-200 + i * 190 + r.uniform(-40, 40), 1080, r.uniform(110, 170), 8300 + i * 7, col="#5f7d74"))
    # снежные берега и лёд канала (диагональ к зрителю)
    o.append(shape([(-1500, 1060, 1), (2900, 1040, 1), (2900, 2400, 1), (-1500, 2400, 1)], "#f4f6f9", "", w=3.0, seed=8400))
    ice = [(-1500, 1240, 1), (300, 1180), (1400, 1150), (2900, 1130, 1), (2900, 1480, 1), (1400, 1520), (300, 1560), (-1500, 1620, 1)]
    gi = lib.lin_grad([(0, "#bfd8ea", 1), (1, "#9cc0dc", 1)], 0, 1150, 0, 1600, units="userSpaceOnUse")
    inner = ""
    for i in range(7):
        yy = 1210 + 50 * i
        inner += line([(-1500, yy + 60), (2900, yy - 40)], 2.4, "#e6f2fa", taper=.2, wmin=.4, seed=8410 + i, op=.75)
    for i in range(10):   # следы коньков дугами
        cx_ = -900 + i * 380
        inner += line([(cx_, 1400 - .03 * cx_), (cx_ + 140, 1360 - .03 * cx_), (cx_ + 300, 1390 - .03 * cx_)], 2, "#ffffff", taper=.5, wmin=.2, seed=8420 + i, op=.8)
    o.append(f'<path d="{lib.fill_d(ice)}" fill="url(#{gi})"/>' if hasattr(lib, "fill_d") else blob(ice, "#b2d0e6"))
    o.append(shape(ice, "none", inner, w=3.2, seed=8430))
    for i in range(6):     # ближние ели по краю
        o.append(_fir(1250 + i * 230 + r.uniform(-30, 30), 1700 + 20 * (i % 2), r.uniform(330, 430), 8500 + i * 7))
    # здание университета слева: серый камень, острая крыша, большое тёплое окно-арка
    ux0, uy0, ux1, uy1 = -800.0, 260.0, 380.0, 1240.0
    stone = "#9a948a"
    inner = ""
    for i in range(12):
        yy = uy0 + 60 + i * 80
        inner += line([(ux0, yy), (ux1, yy)], 2, "#7c766c", taper=0, wmin=1, seed=8600 + i, op=.5)
        for j in range(8):
            xx = ux0 + (j + .5 * (i % 2)) * 150
            inner += line([(xx, yy), (xx, yy + 80)], 2, "#7c766c", taper=0, wmin=1, seed=8620 + i * 8 + j, op=.4)
    o.append(shape(rect_pts(ux0, uy0, ux1, uy1), stone, inner, w=4.4, seed=8650))
    o.append(shape([(ux0 - 40, uy0 + 4), ((ux0 + ux1) / 2, uy0 - 330), (ux1 + 40, uy0 + 4)], "#5c6670",
                   blob([(ux0 - 40, uy0 + 4), ((ux0 + ux1) / 2, uy0 - 330), (ux0 + 120, uy0 - 40)], "#f4f6f9", .95), w=4.4, seed=8651))
    o.append(blob([(ux0 - 30, uy0 + 6), (ux1 + 30, uy0 + 6), (ux1 + 10, uy0 + 36), (ux0 - 10, uy0 + 36)], "#f4f6f9", .95))
    wx0, wy0, wx1, wy1 = OT_UNI_WIN
    arch = [(wx0, wy1), (wx0, wy0 + 110)] + [((wx0 + wx1) / 2 + (wx1 - wx0) / 2 * math.cos(math.pi - a), wy0 + 110 - 110 * math.sin(a))
                                           for a in np.linspace(0, math.pi, 14)][1:-1] + [(wx1, wy0 + 110), (wx1, wy1)]
    gw = lib.lin_grad([(0, "#ffe2a4", 1), (1, "#f2b56a", 1)], 0, 0, 0, 1)
    o.append(f'<path d="M{" L".join(f"{f(a)} {f(b)}" for a, b in arch)}Z" fill="url(#{gw})"/>')
    win_clip = lib.uid()      # прямыми отрезками: сглаженный контур выгибался ниже подоконника и выпускал рисунок наружу
    lib.DEFS.append(f'<clipPath id="{win_clip}"><path d="M{" L".join(f"{f(a)} {f(b)}" for a, b in arch)}Z"/></clipPath>')
    # здание справа от окна — тёмные окна этажей (без надписей), фонарь
    for j in range(3):
        for i in range(2):
            xx, yy = ux0 + 80 + i * 170, uy0 + 140 + j * 300
            o.append(shape(rect_pts(xx, yy, xx + 90, yy + 170), "#6e7e8e", blob(rect_pts(xx, yy + 150, xx + 90, yy + 170), "#f4f6f9", .9), w=3.0, seed=8660 + i + 3 * j))
    front = f'<path d="M{" L".join(f"{f(a)} {f(b)}" for a, b in arch)}Z" fill="none" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>' + shape(rect_pts(wx0, wy0, wx1, wy1), "none", line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], 7, "#5a5048", taper=0, wmin=1, seed=8670)
                  + line([(wx0, (wy0 + wy1) / 2 + 40), (wx1, (wy0 + wy1) / 2 + 40)], 7, "#5a5048", taper=0, wmin=1, seed=8671), ink=False)
    front += shape(rect_pts(wx0 - 30, wy1, wx1 + 30, wy1 + 34), "#b8b0a4", blob(rect_pts(wx0 - 30, wy1, wx1 + 30, wy1 + 14), "#f4f6f9"), w=3.6, seed=8673)
    for lxp in (620.0, 1820.0):    # фонари у канала
        o.append(line([(lxp, 1180), (lxp, 820)], 9, "#2a2e36", taper=0, wmin=1, seed=8680 + int(lxp)))
        o.append(shape(lib.rrect(lxp - 30, 770, lxp + 30, 830, 10), "#ffe6a8", "", w=3.2, seed=8682 + int(lxp)))
        o.append(blob(rect_pts(lxp - 34, 760, lxp + 34, 774), "#f4f6f9"))
    # падающий снег
    r = rs(8700)
    sn = []
    for i in range(70):
        x0_, y0_ = r.uniform(-900, 2700), r.uniform(-300, 2000)
        sp = r.uniform(50, 110)
        y_ = (y0_ + sp * t) % 2300 - 300
        x_ = x0_ + 22 * math.sin(t * 1.3 + i)
        sn.append(f'<circle cx="{f(x_)}" cy="{f(y_)}" r="{f(r.uniform(3, 7))}" fill="#ffffff" opacity="{r.uniform(.6, .95):.2f}"/>')
    an = dict(uni_win=OT_UNI_WIN, win_clip=win_clip, ice=(1180.0, 1520.0), win_front=front)
    return dict(bg="".join(o), front=front, snow="".join(sn), anchors=an, cam=CAM80_CANAL)
