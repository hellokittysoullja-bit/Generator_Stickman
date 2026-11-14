"""Сцена study рилса 28 (s08–s12): опыт в Техасе (Ward и др., 2017). Без букв и цифр.
s08 (15.17–17.76): кирпичный корпус университета днём (колонны, кактусы, солнце); камера влетает в большое окно —
     внутри аудитория, взрослые студенты разного вида решают задачи на память (сетка значков на листе).
s09 (17.76–19.5): три парты рядом; на «столе» (18.96) подсвечивается парта с телефоном на столе, на «в сумке» (19.44) —
     парта с телефоном в сумке; третья — без телефона.
s10 (19.5–21.44): третий вариант: студентка ставит телефон на столик в соседней комнате, дверь захлопывается на
     «комнате» (20.64), она идёт обратно.
s11 (21.44–24.77): три столбика результатов со значками (телефон на столе / сумка / дверь); «дверь» растёт выше всех и
     получает звезду на «комнате» (24.08).
s12 (24.77–27.01): рядом с телефоном выключатель щёлкает вкл/выкл (25.55 …), столбик «дверь» не меняется."""
import math

import numpy as np

import lib
import person
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, clip_rect, ease_in, ease_io, ease_out, ellipse_pts, f,
                 line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg, T)

_ST = {}
BRICK, BRICK_SH, BRICK_DK, TRIM = "#b4523a", "#8f3c2b", "#6e2c20", "#f3ede1"
T_TABLE, T_BAG = 18.96, 19.44
SLAM = 20.64
STAR = 24.08
CLICKS = [25.55, 26.05, 26.52]          # выкл, вкл, выкл

STUDENTS = [
    dict(skin="#f0c4a0", hair="short", hair_c="#5a3a26", top="#2d55a8", low="#1f2b52", face=.15, stubble=True),
    dict(skin="#8a5a3c", hair="curly", hair_c="#2a1a14", top="#e07a2e", low="#3a3040", face=-.1),
    dict(skin="#f4d0b4", hair="ponytail", hair_c="#c8622a", top="#3a9a6a", low="#24484a", face=.2),
    dict(skin="#d9a07a", hair="bun", hair_c="#2a1a14", top="#7a4fb0", low="#2a2a3a", face=-.2, glasses=True),
    dict(skin="#e8b896", hair="bald", hair_c="#9a7a66", top="#c94a3f", low="#3a3f4c", face=.1, glasses=True, mustache=True),
    dict(skin="#c98e6a", hair="short", hair_c="#1a1210", top="#2f8a8a", low="#1f3a2c", face=-.15, cap=None),
    dict(skin="#f2c9a8", hair="bob", hair_c="#e0b050", top="#d9467a", low="#2a2a3a", face=.1),
    dict(skin="#a8704c", hair="short", hair_c="#2a1a14", top="#d9a338", low="#2a3040", face=-.05, stubble=True),
    dict(skin="#f0c4a0", hair="curly", hair_c="#7a4a2a", top="#4a5a8c", low="#2a2a3a", face=.25),
]


# ═══════════════════════════════ общее: парта, лист, телефон, студент
def phone_flat(x, y, sc=1.0, rot=0.0, sd=0, glow=0.0):
    """Телефон экраном вниз на столе (вид сверху-спереди), центр (x, y), ширина ~92·sc."""
    s = []
    if glow > 0.01:
        g = rad_grad([(0, "#ffe27a", .9 * glow), (1, "#ffe27a", 0)], 0, 0, 120, 70)
        s.append(f'<ellipse cx="0" cy="0" rx="120" ry="70" fill="url(#{g})"/>')
    s.append(blob(ellipse_pts(2, 10, 50, 9, 12), "#3a2a20", .35, blur(3)))
    s.append(shape([(-44, 2, 1), (44, 2, 1), (42, 10, 1), (-42, 10, 1)], "#1a1d26", "", w=2.6, seed=sd + 1))
    s.append(shape([(-40, -14, 1), (40, -14, 1), (46, 4, 1), (-46, 4, 1)], "#353a4a",
                   blob([(4, -14), (40, -14), (46, 4), (14, 4)], "#262a36", .9) + line([(-34, -10), (14, -11)], 2.4, "#6a7290", seed=sd + 2, op=.8),
                   w=3.0, seed=sd + 3))
    s.append(f'<ellipse cx="-30" cy="-8" rx="5" ry="3" fill="#11131a" stroke="{INK}" stroke-width="1.6"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{"".join(s)}</g>'


def phone_up(x, y, sc=1.0, rot=0.0, on=0.0, sd=0):
    """Телефон стоя (лицом к нам), центр (x, y), 60×116 · sc; on — экран светится."""
    s = []
    scr = mix("#20242f", "#7fd0ff", on)
    inner = blob(rect_pts(-24, -48, 24, 46, 6), scr)
    if on > 0.02:
        inner += blob([(-24, -48), (4, -48), (-24, 0)], "#c8f0ff", .55 * on)
        for k in range(3):
            inner += blob(rect_pts(-16, -34 + k * 22, 16, -24 + k * 22, 3), "#ffffff", .7 * on)
    s.append(shape(rect_pts(-30, -58, 30, 58, 12), "#2b2f3a", inner, w=3.6, seed=sd + 1))
    s.append(f'<rect x="-7" y="-54" width="14" height="3" rx="1.5" fill="#5b6070"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{"".join(s)}</g>'


SHAPES = ["circle", "tri", "square", "star", "circle", "square", "tri", "circle", "star"]


def mini_shape(kind, x, y, r, col, sd):
    if kind == "circle":
        return shape(ellipse_pts(x, y, r, r, 10), col, "", w=2.0, seed=sd)
    if kind == "tri":
        return shape([(x, y - r, 1), (x + r, y + r * .8, 1), (x - r, y + r * .8, 1)], col, "", w=2.0, seed=sd)
    if kind == "square":
        return shape(rect_pts(x - r * .85, y - r * .85, x + r * .85, y + r * .85), col, "", w=2.0, seed=sd)
    pts = []
    for i in range(10):
        rr = r * (1.1 if i % 2 == 0 else .45)
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, col, "", w=2.0, seed=sd)


def paper(x, y, w, h, prog, sd=0):
    """Лист задачи на парте (вид сверху-спереди): сетка 3×3 клеток, prog 0..9 — сколько клеток заполнено значками."""
    s = []
    k = 0.18 * w                         # скос перспективы
    pts = [(x - w / 2 + k * .5, y - h / 2, 1), (x + w / 2 - k * .5, y - h / 2, 1), (x + w / 2, y + h / 2, 1), (x - w / 2, y + h / 2, 1)]
    inner = ""
    cols = ["#e2543f", "#2d55a8", "#3cbf63", "#d9a338"]
    for j in range(3):
        for i in range(3):
            v = (j + .5) / 3
            yy = y - h / 2 + h * (0.12 + 0.78 * v)
            ww = w - k * (1 - v)
            xx = x - ww / 2 + ww * (0.2 + 0.3 * i)
            r = 0.07 * w
            inner += f'<rect x="{f(xx - r)}" y="{f(yy - r * .7)}" width="{f(2 * r)}" height="{f(1.4 * r)}" fill="none" stroke="#9aa6c4" stroke-width="{f(max(1.2, w * .012))}"/>'
            n = j * 3 + i
            if prog > n:
                a = clamp(prog - n)
                inner += f'<g transform="translate({f(xx)} {f(yy)}) scale({f(back_out(a, 2))}) translate({f(-xx)} {f(-yy)})">' + \
                    mini_shape(SHAPES[(n + sd) % 9], xx, yy, r * .55, cols[(n + sd) % 4], sd + n) + "</g>"
    s.append(shape(pts, "#fbfaf4", inner, w=max(2.0, w * .018), seed=sd))
    return "".join(s)


def pencil_item(hnd, ang, sc):
    """Карандаш в кисти: конец у кончиков пальцев, торчит вверх-вправо."""
    x, y = hnd
    a = math.radians(ang)
    tip = (x + math.cos(a) * 46 * sc + 6 * sc, y + math.sin(a) * 46 * sc + 10 * sc)
    back = (tip[0] + 60 * sc, tip[1] - 70 * sc)
    return line([tip, back], 9 * sc, "#e8b23a", taper=.05, wmin=.95, seed=7) + line([tip, (tip[0] + 10 * sc, tip[1] - 12 * sc)], 6 * sc, "#3a2a20", taper=.8, seed=8)


def desk_surface(x, yb, w, depth, sd, col="#c99a62"):
    """Крышка парты: задний край yb, передний yb+depth (шире)."""
    s = []
    k = 0.08 * w
    pts = [(x - w / 2 + k, yb, 1), (x + w / 2 - k, yb, 1), (x + w / 2, yb + depth, 1), (x - w / 2, yb + depth, 1)]
    inner = blob([(x + w * .1, yb), (x + w / 2 - k, yb), (x + w / 2, yb + depth), (x + w * .25, yb + depth)], lib.mul(col, (.9, .88, .9)), .6)
    inner += line([(x - w * .35, yb + depth * .35), (x + w * .1, yb + depth * .3)], 2.4, lib.mul(col, (.8, .75, .75)), seed=sd + 3, op=.6)
    s.append(shape(pts, col, inner, w=3.6, seed=sd))
    return "".join(s)


def desk_front(x, yb, w, depth, floor, sd, col="#c99a62"):
    """Передняя кромка и ножки (под крышкой, до пола)."""
    s = []
    y0 = yb + depth
    th = max(10, depth * .22)
    s.append(blob(ellipse_pts(x, floor + 4, w * .55, 10 + w * .02, 14), "#4a3a30", .3, blur(5)))
    for xx in (x - w / 2 + w * .08, x + w / 2 - w * .08):
        s.append(shape(rect_pts(xx - w * .025, y0 + th - 2, xx + w * .025, floor), "#5a5f6e", blob(rect_pts(xx, y0 + th, xx + w * .025, floor), "#41454f"),
                       w=3, seed=sd + 5 + int(xx)))
    s.append(shape(rect_pts(x - w / 2 + w * .06, y0 + th, x + w / 2 - w * .06, y0 + th + (floor - y0) * .38), "#a87c4c",
                   blob(rect_pts(x + w * .2, y0 + th, x + w / 2 - w * .06, y0 + th + (floor - y0) * .38), "#8a6238", .7), w=3.2, seed=sd + 7))
    s.append(shape(rect_pts(x - w / 2, y0, x + w / 2, y0 + th), lib.mul(col, (.82, .78, .78)), "", w=3.2, seed=sd + 8))
    return "".join(s)


def student(spec, x, yb, sc, t, ph, sd, write=True, mood="focus", extra=None):
    """Студент за партой: без ног, низ туловища спрятан под крышкой (задний край yb). Возвращает (тело, руки):
    тело рисуется ДО крышки, руки — после листа (лежат на парте). Пишет правой, левая придерживает лист."""
    feet = yb + 330 * sc
    wph = t * 7.5 + ph
    look_up = smooth(.0, .25, math.sin(t * .9 + ph * 2) - .55)      # иногда поднимает глаза — вспоминает
    jx, jy = (9 * math.sin(wph) + 5 * math.sin(wph * 2.3), 4 * math.cos(wph * 1.3)) if write else (0, 0)
    bl = ((t + ph * .37) % 3.1)
    pose = {"no_legs": True,
            "hand_target": {"L": (-58, -300), "R": (52 + jx * (1 - look_up), -296 + jy)},
            "curl": {"L": 0.15, "R": 0.75},
            "look": (0.15 * math.sin(ph), 0.75 - 1.1 * look_up),
            "brow": 0.6 + 0.4 * look_up if mood == "focus" else 0.0,
            "mouth": "flat" if mood == "focus" else mood,
            "head_tilt": 5 * math.sin(t * .8 + ph) - 4 * look_up,
            "blink": max(0.0, 1 - abs(bl - 1.5) / 0.07)}
    if write:
        pose["over_hand"] = {"R": lambda h, a: pencil_item(h, a, 1.0)}
    if extra:
        pose.update(extra)
    breath = 2 * math.sin(t * 2.2 + ph)
    body = person.draw(spec, dict(pose, no_arms=True), x, feet + breath * sc, sc, sd=sd)
    arms = person.draw(spec, dict(pose, only_arms=True), x, feet + breath * sc, sc, sd=sd)
    return body, arms


# ═══════════════════════════════ s08: корпус и аудитория
GX0, GX1, GTOP, GBASE = 70, 1010, 470, 1160
WIN = (486, 640, 594, 832)           # большое окно — 108×192 (9:16), в него влетает камера
WC = ((WIN[0] + WIN[2]) / 2, (WIN[1] + WIN[3]) / 2)
WK = (WIN[2] - WIN[0]) / W           # масштаб аудитории внутри окна


def brick_defs():
    DEFS.append(f'<pattern id="pBrick" width="64" height="32" patternUnits="userSpaceOnUse">'
                f'<rect width="64" height="32" fill="{BRICK}"/>'
                f'<path d="M0 15.5H64M0 31.5H64M20 0V15.5M52 16V32" stroke="{BRICK_SH}" stroke-width="2.4"/>'
                f'<rect x="4" y="3" width="12" height="4" fill="#c66a4f" opacity=".7"/><rect x="36" y="19" width="10" height="4" fill="#c66a4f" opacity=".6"/>'
                f'</pattern>')


def sky():
    s = []
    lin_grad([(0, "#5aa6ea", 1), (.6, "#a6d4f5", 1), (1, "#f4ead2", 1)], 0, 0, 0, 1, gid="gSky8")
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{GBASE + 700}" fill="url(#gSky8)"/>')
    g = rad_grad([(0, "#fff8d8", 1), (.25, "#fff1b0", .8), (1, "#fff1b0", 0)], 900, 150, 420, 420)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{GBASE + 700}" fill="url(#{g})"/>')
    # далёкие плоские холмы-месы
    s.append(shape([(-600, GBASE - 40), (-200, GBASE - 150, 1), (40, GBASE - 150, 1), (140, GBASE - 70), (700, GBASE - 80), (860, GBASE - 190, 1),
                    (1180, GBASE - 190, 1), (1300, GBASE - 60), (1700, GBASE - 40, 1), (1700, GBASE + 10, 1), (-600, GBASE + 10, 1)], "#d9a77a",
                   blob([(860, GBASE - 190), (1180, GBASE - 190), (1300, GBASE - 60), (900, GBASE - 60)], "#c48f64", .8), w=4, seed=801))
    return "".join(s)


def sun(t):
    x, y = 900, 150
    s = []
    for k in range(12):
        a = k * math.pi / 6 + t * 0.35
        r0, r1 = 92, 132 + 10 * math.sin(t * 3 + k)
        s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)], 9, "#ffcf3a", taper=.4, seed=810 + k))
    s.append(shape(ellipse_pts(x, y, 72, 72, 24), "#ffd84a", blob(ellipse_pts(x + 14, y + 16, 62, 58, 18), "#f4b92e", .7) +
                   blob(ellipse_pts(x - 24, y - 26, 20, 12, 10, rot=-30), "#fff6c8", .9), w=4.6, seed=809))
    return "".join(s)


def clouds(t):
    s = []
    for k, (x0, y, sc, sp) in enumerate([(160, 230, 1.0, 16), (620, 120, .8, 10), (-180, 380, .9, 13)]):
        x = x0 + sp * (t - 15)
        pts = []
        for i in range(14):
            a = 2 * math.pi * i / 14
            r = 1 + .18 * math.sin(5 * a + k)
            pts.append((x + 110 * sc * math.cos(a) * r, y + 40 * sc * math.sin(a) * r * (0.75 if math.sin(a) > 0 else 1)))
        s.append(shape(pts, "#ffffff", blob(ellipse_pts(x + 20 * sc, y + 22 * sc, 90 * sc, 16 * sc, 10), "#d8e8f5"), w=3.6, seed=820 + k))
    return "".join(s)


def saguaro(x, y, h, sd, arms=((0.45, -1, 0.35), (0.6, 1, 0.3)), sway=0.0):
    """Кактус-сагуаро: ствол высотой h от земли y, руки-отростки (доля высоты, сторона, длина)."""
    s = []
    wdt = h * 0.16
    for k, (u, side, L) in enumerate(arms):
        by = y - h * u
        ax = x + side * wdt * .45
        ex = x + side * (wdt * .5 + h * .18)
        pts = [(ax, by + wdt * .35), (ex, by + wdt * .35), (ex + side * wdt * .02, by - h * L)]
        s.append(shape(person.band(pts, wdt * .62, wdt * .58, step=6, cap=True) if False else
                       lib.band(pts, wdt * .62, wdt * .58, step=6, cap=True), "#4f9a4a",
                       blob(lib.band([(p[0] + side * wdt * .1, p[1]) for p in pts], wdt * .25, wdt * .22, step=6, cap=False), "#3c7c3a", .9),
                       w=3.6, seed=sd + 10 + k))
    trunk = lib.band([(x, y + 4), (x + sway * .3, y - h * .5), (x + sway, y - h)], wdt, wdt * .92, step=6, cap=True)
    inner = blob(lib.band([(x + wdt * .25, y), (x + wdt * .25 + sway * .3, y - h * .5), (x + wdt * .22 + sway, y - h)], wdt * .4, wdt * .36, step=6, cap=False), "#3c7c3a", .9)
    for j in (-1, 1):
        inner += line([(x + j * wdt * .18, y - 6), (x + j * wdt * .18 + sway, y - h + wdt * .2)], 2.4, "#2f6630", seed=sd + 20 + j, op=.7)
    s.append(shape(trunk, "#57a652", inner, w=4, seed=sd + 1))
    return "".join(s)


def prickly(x, y, sc, sd):
    s = []
    for k, (dx, dy, r, rot) in enumerate([(0, -60, 44, -8), (-50, -26, 36, -40), (48, -30, 38, 34), (16, -118, 32, 12)]):
        s.append(shape(ellipse_pts(x + dx * sc, y + dy * sc, r * .78 * sc, r * sc, 14, rot=rot), "#6aae5a",
                       blob(ellipse_pts(x + dx * sc + 8 * sc, y + dy * sc + 8 * sc, r * .5 * sc, r * .7 * sc, 10, rot=rot), "#4d8f45", .8) +
                       "".join(f'<circle cx="{f(x + dx * sc + (i - 1) * 12 * sc)}" cy="{f(y + dy * sc + (i % 2) * 14 * sc - 6 * sc)}" r="{f(2.2 * sc)}" fill="#f6efd0"/>' for i in range(3)),
                       w=3.4, seed=sd + k))
    s.append(shape(ellipse_pts(x + 16 * sc, y - 154 * sc, 10 * sc, 12 * sc, 8), "#e2543f", "", w=2.4, seed=sd + 9))
    return "".join(s)


def win(x, y0, y1, seed=0, w=62):
    s = []
    s.append(shape(rect_pts(x - w / 2 - 8, y0 - 8, x + w / 2 + 8, y1 + 8), TRIM, "", w=3.6, seed=seed))
    inner = blob(rect_pts(x - w / 2, y0, x + w / 2, y1), "#7fa9d8") + \
        blob([(x - w / 2, y0 + 40), (x + w / 2, y0 + 8), (x + w / 2, y0 + 30), (x - w / 2, y0 + 62)], "#c9e2f7", .8)
    s.append(shape(rect_pts(x - w / 2, y0, x + w / 2, y1), "#7fa9d8", inner, w=3.2, seed=seed + 1))
    s.append(line([(x, y0), (x, y1)], 3.2, TRIM, taper=.1, wmin=.9, seed=seed + 4))
    s.append(line([(x - w / 2, (y0 + y1) / 2), (x + w / 2, (y0 + y1) / 2)], 3.2, TRIM, taper=.1, wmin=.9, seed=seed + 5))
    s.append(shape(rect_pts(x - w / 2 - 14, y1 + 8, x + w / 2 + 14, y1 + 20), TRIM, "", w=3, seed=seed + 6))
    return "".join(s)


def building():
    s = []
    s.append(blob([(GX0 + 20, GBASE), (GX1 + 40, GBASE), (GX1 + 120, GBASE + 50), (GX0 + 80, GBASE + 50)], "#b88d58", .55, blur(6)))
    # крыша красной черепицей (Техас)
    roof = [(GX0 - 24, GTOP), (GX0 + 70, GTOP - 96), (GX1 - 70, GTOP - 96), (GX1 + 24, GTOP)]
    rin = blob([(GX0 + 70, GTOP - 96), (GX1 - 70, GTOP - 96), (GX1 - 60, GTOP - 80), (GX0 + 60, GTOP - 80)], "#e07a52")
    for k in range(5):
        y = GTOP - 18 - k * 18
        rin += line([(GX0 - 10 + k * 18, y), (GX1 + 10 - k * 18, y)], 3, "#8f3a24", seed=830 + k, op=.7)
    s.append(shape(roof, "#c4593a", rin, w=4.6, seed=831))
    # фасад
    fac = rect_pts(GX0, GTOP, GX1, GBASE)
    inner = f'<rect x="{GX0}" y="{GTOP}" width="{GX1 - GX0}" height="{GBASE - GTOP}" fill="url(#pBrick)"/>'
    inner += blob([(GX1 - 80, GTOP), (GX1, GTOP), (GX1, GBASE), (GX1 - 40, GBASE)], BRICK_DK, .35)
    inner += blob(rect_pts(GX0, GTOP, GX1, GTOP + 26), BRICK_DK, .45)
    s.append(shape(fac, BRICK, inner, w=5, seed=835))
    s.append(shape(rect_pts(GX0 - 18, GTOP - 10, GX1 + 18, GTOP + 14), TRIM, blob(rect_pts(GX0 - 18, GTOP + 6, GX1 + 18, GTOP + 14), "#cfc6b4"), w=4, seed=836))
    s.append(shape(rect_pts(GX0 - 10, GBASE - 40, GX1 + 10, GBASE), "#d9cfbd", blob(rect_pts(GX0 - 10, GBASE - 14, GX1 + 10, GBASE), "#b9ae99"), w=4, seed=838))
    for k, x in enumerate([140, 250, 830, 940]):
        s.append(win(x, 560, 680, seed=840 + k * 10))
        s.append(win(x, 790, 910, seed=880 + k * 10))
    # портик с колоннами вокруг большого окна
    PX0, PX1 = 360, 720
    s.append(shape([(PX0 - 30, 560), (540, 490), (PX1 + 30, 560)], TRIM, blob([(PX0 + 10, 552), (540, 510), (PX1 - 10, 552)], "#e3dccd"), w=4.4, seed=850))
    s.append(shape(rect_pts(PX0 - 30, 560, PX1 + 30, 584), TRIM, "", w=4, seed=851))
    s.append(shape(ellipse_pts(540, 538, 14, 14, 12), "#e8c35a", "", w=2.6, seed=852))
    # рама большого окна (стекло рисует сцена)
    x0, y0, x1, y1 = WIN
    s.append(shape(rect_pts(x0 - 16, y0 - 16, x1 + 16, y1 + 16, 4), TRIM, blob(rect_pts(x0 - 16, y1, x1 + 16, y1 + 16), "#d6cdb9"), w=4, seed=853))
    s.append(shape(rect_pts(x0 - 26, y1 + 16, x1 + 26, y1 + 30), TRIM, "", w=3.4, seed=854))
    for x in (PX0, PX0 + 56, PX1 - 56, PX1):
        col = rect_pts(x - 15, 584, x + 15, GBASE - 40)
        s.append(shape(col, TRIM, blob(rect_pts(x + 4, 584, x + 15, GBASE - 40), "#d4cbb8") +
                       line([(x - 5, 594), (x - 5, GBASE - 50)], 2, "#cfc6b4", seed=855 + x), w=3.4, seed=856 + x))
        s.append(shape(rect_pts(x - 21, 580, x + 21, 594), TRIM, "", w=3, seed=857 + x))
        s.append(shape(rect_pts(x - 21, GBASE - 54, x + 21, GBASE - 40), TRIM, "", w=3, seed=858 + x))
    # дверь под окном
    door = [(500, GBASE - 40, 1), (500, 950), (540, 918), (580, 950), (580, GBASE - 40, 1)]
    s.append(shape(door, "#5a3524", blob([(540, 918), (580, 950), (580, GBASE - 40), (548, GBASE - 40)], "#3f2418") +
                   line([(540, 926), (540, GBASE - 44)], 2.6, "#2a160e", seed=860), w=3.6, seed=861))
    for j in range(3):
        s.append(shape(rect_pts(PX0 - 40 - j * 14, GBASE - 40 + j * 14, PX1 + 40 + j * 14, GBASE - 26 + j * 14), "#ece4d4", "", w=3.2, seed=862 + j))
    return "".join(s)


def ground():
    s = []
    lin_grad([(0, "#e8c690", 1), (1, "#d6a76a", 1)], 0, 0, 0, 1, gid="gSand")
    s.append(f'<rect x="-600" y="{GBASE - 6}" width="{W + 1200}" height="{H + 600}" fill="url(#gSand)"/>')
    s.append(line([(-500, GBASE - 6), (W + 500, GBASE - 6)], 4, INK, taper=.1, wmin=.8, seed=870))
    path = [(470, GBASE + 2), (610, GBASE + 2), (820, H + 400, 1), (260, H + 400, 1)]
    s.append(shape(path, "#efe2c4", blob([(600, GBASE), (820, H + 400), (700, H + 400), (580, GBASE)], "#d9c6a0", .9), w=4, seed=871))
    rs = np.random.RandomState(8)
    for k in range(40):
        x, y = rs.uniform(-200, W + 200), rs.uniform(GBASE + 40, 1800)
        if 330 < x < 760:
            continue
        s.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rs.uniform(4, 9))}" ry="{f(rs.uniform(2, 4))}" fill="#b98a52" opacity=".7"/>')
    return "".join(s)


def cacti(t):
    s = []
    sw = 3 * math.sin(t * 1.3)
    s.append(saguaro(150, GBASE + 120, 430, 900, sway=sw))
    s.append(saguaro(950, GBASE + 90, 360, 930, arms=((0.5, 1, 0.32), (0.38, -1, 0.22)), sway=-sw))
    s.append(prickly(300, GBASE + 70, 0.9, 960))
    s.append(prickly(810, GBASE + 180, 1.1, 970))
    s.append(prickly(-30, GBASE + 230, 1.2, 980))
    return "".join(s)


# ─── аудитория (координаты 1080×1920)
FLOOR_I = 1000


def classroom_back():
    s = []
    lin_grad([(0, "#f3e6c8", 1), (1, "#e8d6b0", 1)], 0, 0, 0, 1, gid="gWallI")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{FLOOR_I + 900}" fill="url(#gWallI)"/>')
    lin_grad([(0, "#b9824e", 1), (1, "#a0693c", 1)], 0, 0, 0, 1, gid="gFloorI")
    s.append(f'<rect x="-900" y="{FLOOR_I}" width="{W + 1800}" height="{H + 900}" fill="url(#gFloorI)"/>')
    for k in range(-6, 16):
        x = 540 + k * 110
        s.append(line([(540 + (x - 540) * .35, FLOOR_I), (540 + (x - 540) * 2.6, H + 400)], 2.4, "#8a5a32", taper=.1, wmin=.8, seed=1300 + k, op=.7))
    s.append(line([(-900, FLOOR_I), (W + 900, FLOOR_I)], 4, INK, taper=.05, wmin=.9, seed=1320))
    s.append(blob(rect_pts(-900, FLOOR_I - 34, W + 900, FLOOR_I), "#c9a77a"))
    # доска без букв: только меловые фигуры (круг, квадрат, треугольник — задача на память)
    s.append(shape(rect_pts(250, 300, 830, 640, 6), "#2f5a46", blob(rect_pts(250, 560, 830, 640), "#284e3d", .6) +
                   blob([(270, 320), (420, 320), (300, 520)], "#3a6c55", .5), w=5, seed=1330))
    s.append(shape(rect_pts(236, 290, 844, 304), "#a87c4c", "", w=3.2, seed=1331))
    s.append(shape(rect_pts(236, 636, 844, 656), "#a87c4c", "", w=3.2, seed=1332))
    for k, (kind, x) in enumerate([("circle", 380), ("square", 540), ("tri", 700)]):
        if kind == "circle":
            s.append(line([(x + 48 * math.cos(a), 450 + 48 * math.sin(a)) for a in np.linspace(0, 6.4, 24)], 6, "#eef4ea", taper=.1, wmin=.7, seed=1340))
        elif kind == "square":
            s.append(line([(x - 44, 406), (x + 44, 404), (x + 46, 494), (x - 42, 496), (x - 44, 404)], 6, "#eef4ea", taper=.1, wmin=.7, seed=1341))
        else:
            s.append(line([(x, 400), (x + 50, 496), (x - 50, 494), (x, 400)], 6, "#eef4ea", taper=.1, wmin=.7, seed=1342))
    # окна с видом на кактусы
    for k, x in enumerate([60, 1020]):
        s.append(shape(rect_pts(x - 110, 260, x + 110, 760, 4), "#9fd0f2",
                       blob(rect_pts(x - 110, 620, x + 110, 760), "#e8c690") + saguaro(x - 20, 760, 220, 1350 + k * 20) +
                       blob([(x - 110, 420), (x + 110, 300), (x + 110, 360), (x - 110, 480)], "#ffffff", .45), w=5, seed=1360 + k))
        s.append(line([(x, 260), (x, 760)], 5, TRIM, taper=.05, wmin=.9, seed=1370 + k))
        s.append(shape(rect_pts(x - 124, 760, x + 124, 780), TRIM, "", w=3.2, seed=1372 + k))
    # часы без цифр
    s.append(shape(ellipse_pts(540, 190, 52, 52, 24), "#fbf8ee", blob(ellipse_pts(548, 198, 48, 48, 18), "#e6dfcc", .7), w=5, seed=1380))
    return "".join(s)


def clock_hands(t):
    a1 = (t * 30) % 360
    s = line([(540, 190), (540 + 36 * math.sin(math.radians(a1)), 190 - 36 * math.cos(math.radians(a1)))], 5, INK, taper=.3, seed=1381)
    s += line([(540, 190), (540 + 24 * math.sin(math.radians(130)), 190 - 24 * math.cos(math.radians(130)))], 7, INK, taper=.3, seed=1382)
    return s


SUN_BEAMS = None


def beams(t):
    s = []
    for k, x in enumerate([60, 1020]):
        side = 1 if x < 540 else -1
        g = lin_grad([(0, "#fff4c8", .45 + .08 * math.sin(t * 1.4 + k)), (1, "#fff4c8", 0)], 0, 0, 1, 1, gid=f"gBeam{k}")
        s.append(f'<path d="M{x - 100} 280 L{x + 100} 270 L{x + side * 420 + 140} 1400 L{x + side * 420 - 200} 1420 Z" fill="url(#{g})"/>')
    return s and "".join(s)


ROWS = [  # (y заднего края крышки, масштаб студента, x-центры, ширина парты)
    (830, .50, [175, 415, 655, 895], 200),
    (1010, .64, [140, 410, 680, 950], 245),
    (1230, .80, [190, 545, 900], 300),
]


def classroom(t, extra=None):
    """Вся аудитория — фон + три ряда парт со студентами (задние рисуются первыми)."""
    s = [_ST["cls_back"], clock_hands(t), beams(t)]
    n = 0
    for r, (yb, sc, xs, dw) in enumerate(ROWS):
        depth = dw * .30
        floor = yb + depth + 320 * sc
        for j, x in enumerate(xs):
            spec = STUDENTS[(n * 4 + 1) % len(STUDENTS)]
            ph = n * 1.7
            body, arms = student(spec, x, yb, sc, t, ph, 1500 + n * 100)
            s.append(body)
            s.append(desk_surface(x, yb, dw, depth, 1400 + n * 10))
            prog = clamp((t - 15.0 - n * 0.13) / 2.6) * 7 + 1
            s.append(paper(x + dw * .02, yb + depth * .58, dw * .40, depth * .62, prog, sd=n))
            s.append(arms)
            s.append(desk_front(x, yb, dw, depth, floor, 1450 + n * 10))
            n += 1
    return "".join(s)


def s08(t):
    # камера: 14.97–15.55 мягкий наезд на фасад, 15.55–16.2 влёт в окно (экспоненциально), дальше — внутри
    zin = ease_io(clamp((t - 15.5) / 0.75))
    s_end = 1.05 / WK
    if zin < 1:
        s0 = 0.95 + 0.12 * ease_out(clamp((t - 14.97) / 0.6), 2)
        S = s0 * (s_end / s0) ** zin
        # центр едет к окну так, чтобы окно росло на месте
        c0 = (540, 870)
        k = (1 - s0 / S) / (1 - s0 / s_end) if S > s0 + 1e-6 else 0.0
        cx = c0[0] + (WC[0] - c0[0]) * k
        cy = c0[1] + (WC[1] - c0[1]) * k
        inside = f'<g transform="translate({WIN[0]} {f(WC[1] - H * WK / 2)}) scale({WK:.6f})">{classroom(t)}</g>'
        cl = lib.clip_rect(WIN[0], WIN[1], WIN[2] - WIN[0], WIN[3] - WIN[1])
        art = _ST["sky"] + sun(t) + clouds(t) + _ST["ground"] + _ST["bld"] + f'<g clip-path="url(#{cl})">{inside}</g>' + \
            shape(rect_pts(*WIN), "none", "", w=3.6, seed=1999) + cacti(t)
        return art, cam(cx, cy, S, 0.6 * (1 - zin)), "#9cc8ee"
    u = clamp((t - 16.25) / 1.75)
    return classroom(t), cam(540, 960 - 30 * u, 1.05 + 0.08 * (0.5 * u + 0.5 * ease_io(u)), -0.4 * u), "#e8d6b0"


# ═══════════════════════════════ s09 / s10: три варианта
D3 = [200, 540, 880]
YB3 = 1000
SC3 = .78
DW3 = 300


def bag(x, y, phone_vis, sd, glow=0.0):
    """Рюкзак на полу у парты (низ y), из переднего кармана торчит телефон."""
    s = []
    s.append(blob(ellipse_pts(x, y + 4, 74, 12, 12), "#3a2a20", .35, blur(4)))
    body = [(x - 62, y, 1), (x - 66, y - 110), (x - 50, y - 150), (x, y - 166), (x + 50, y - 150), (x + 66, y - 110), (x + 62, y, 1)]
    inner = blob([(x + 20, y - 160), (x + 66, y - 110), (x + 62, y), (x + 24, y)], "#1f5a52", .8)
    s.append(shape(body, "#2f8a7a", inner, w=4, seed=sd))
    s.append(line([(x - 40, y - 150), (x - 30, y - 190), (x + 30, y - 190), (x + 40, y - 150)], 7, "#1f5a52", taper=.1, wmin=.9, seed=sd + 1))
    if glow > 0.01:
        g = rad_grad([(0, "#ffe27a", .9 * glow), (1, "#ffe27a", 0)], x, y - 80, 110, 90)
        s.append(f'<ellipse cx="{f(x)}" cy="{f(y - 80)}" rx="110" ry="90" fill="url(#{g})"/>')
    if phone_vis:
        s.append(phone_up(x + 6, y - 96, .62, -8, 0.0, sd + 5))
    s.append(shape([(x - 50, y - 70, 1), (x + 50, y - 70, 1), (x + 48, y - 8, 1), (x - 48, y - 8, 1)], "#37a08e",
                   blob([(x + 14, y - 70), (x + 50, y - 70), (x + 48, y - 8), (x + 14, y - 8)], "#2a7c6e", .8) +
                   line([(x - 44, y - 64), (x + 44, y - 64)], 3, "#e8c35a", seed=sd + 7), w=3.6, seed=sd + 6))
    return "".join(s)


def pop_ring(x, y, rx, ry, e, sd):
    """Обвод-«обводка маркером» вокруг предмета: рисуется за 0.25 с и пульсирует."""
    if e < 0:
        return ""
    u = clamp(e / 0.25)
    n = 40
    m = max(3, int(n * u * 1.08))
    pts = []
    for i in range(m):
        a = -math.pi * .6 + 2.06 * math.pi * i / n
        r = 1 + 0.025 * math.sin(i * 1.3) + 0.03 * math.sin(e * 6) + 0.05 * (i / n)
        pts.append((x + rx * r * math.cos(a), y + ry * r * math.sin(a)))
    return line(pts, 9, "#ffcf3a", taper=.25, wmin=.5, seed=sd)


def spot(x, y0, y1, k):
    """Пятно тёплого света на варианте."""
    if k <= 0.01:
        return ""
    g = rad_grad([(0, "#fff6c8", 1.0 * k), (.55, "#ffe27a", .55 * k), (1, "#ffe27a", 0)], x, (y0 + y1) / 2, 230, (y1 - y0) * .62)
    return f'<ellipse cx="{f(x)}" cy="{f((y0 + y1) / 2)}" rx="230" ry="{f((y1 - y0) * .62)}" fill="url(#{g})"/>'


def wall9():
    s = []
    lin_grad([(0, "#f3e6c8", 1), (1, "#e8d6b0", 1)], 0, 0, 0, 1, gid="gWall9")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{1400 + 900}" fill="url(#gWall9)"/>')
    lin_grad([(0, "#b9824e", 1), (1, "#a0693c", 1)], 0, 0, 0, 1, gid="gFloor9")
    fl = 1250
    s.append(f'<rect x="-900" y="{fl}" width="{W + 1800}" height="{H + 900}" fill="url(#gFloor9)"/>')
    for k in range(-8, 18):
        x = 540 + k * 120
        s.append(line([(540 + (x - 540) * .7, fl), (540 + (x - 540) * 2.2, H + 400)], 2.4, "#8a5a32", taper=.1, wmin=.8, seed=1600 + k, op=.7))
    s.append(line([(-900, fl), (W + 900, fl)], 4, INK, taper=.05, wmin=.9, seed=1620))
    s.append(blob(rect_pts(-900, fl - 34, W + 900, fl), "#c9a77a"))
    s.append(shape(rect_pts(-200, 330, 1280, 700, 6), "#2f5a46", blob(rect_pts(-200, 620, 1280, 700), "#284e3d", .6), w=5, seed=1630))
    s.append(shape(rect_pts(-214, 690, 1294, 710), "#a87c4c", "", w=3.2, seed=1631))
    for k, (kind, x) in enumerate([("circle", 200), ("star", 540), ("tri", 880)]):
        s.append(mini_shape(kind, x, 500, 50, "#2f5a46", 1640 + k).replace('fill="#2f5a46"', 'fill="none"'))
        s.append(f'<g opacity=".95">{line([(x - 70, 600), (x + 70, 598)], 5, "#eef4ea", taper=.3, seed=1650 + k)}</g>')
    # потолок и лампы
    s.append(blob(rect_pts(-900, -900, W + 900, 150), "#e6d3ac"))
    s.append(line([(-900, 150), (W + 900, 150)], 4, INK, taper=.05, wmin=.9, seed=1670))
    for k, x in enumerate([200, 540, 880]):
        s.append(line([(x, 150), (x, 220)], 4, "#5a5f6e", taper=.05, wmin=.9, seed=1671 + k))
        s.append(shape([(x - 70, 262, 1), (x - 34, 218, 1), (x + 34, 218, 1), (x + 70, 262, 1)], "#3f8a7a",
                       blob([(x + 10, 218), (x + 34, 218), (x + 70, 262), (x + 30, 262)], "#2f6a5e"), w=3.6, seed=1675 + k))
        s.append(shape(ellipse_pts(x, 264, 40, 9, 12), "#fff3c4", "", w=2.6, seed=1679 + k))
    # тонкие разделители-перегородки между вариантами
    for x in (370, 710):
        s.append(shape(rect_pts(x - 6, 760, x + 6, fl), "#d6c4a0", "", w=3, seed=1660 + x))
    return "".join(s)


def three_desks(t):
    s = [_ST["wall9"]]
    fl = 1250
    depth = DW3 * .3
    k1 = smooth(T_TABLE - .05, T_TABLE + .15, t)
    k2 = smooth(T_BAG - .05, T_BAG + .15, t)
    k1 *= 1 - 0.55 * k2
    s.append(spot(D3[0], 700, 1260, k1) + spot(D3[1], 700, 1260, k2))
    specs = [STUDENTS[0], STUDENTS[3], STUDENTS[2]]
    moods = ["focus", "focus", "smile"]
    for i, x in enumerate(D3):
        body, arms = student(specs[i], x - 10, YB3, SC3, t, i * 2.1, 1800 + i * 100, mood=moods[i])
        s.append(body)
        s.append(desk_surface(x, YB3, DW3, depth, 1700 + i * 10))
        s.append(paper(x - 30, YB3 + depth * .55, DW3 * .4, depth * .62, 1 + clamp((t - 17.5) / 2) * (3 + 2 * i), sd=3 + i))
        if i == 0:
            pe = t - T_TABLE
            sc = 1 + 0.35 * math.exp(-max(pe, 0) * 6) * math.sin(max(pe, 0) * 14) * (pe > 0) + 0.15 * smooth(T_TABLE - .05, T_TABLE + .1, t)
            s.append(phone_flat(x + 95, YB3 + depth * .5, .9 * sc, -6, 1710, glow=k1))
        s.append(arms)
        s.append(desk_front(x, YB3, DW3, depth, fl, 1750 + i * 10))
    pe2 = t - T_BAG
    bsc = 1 + 0.12 * math.exp(-max(pe2, 0) * 6) * math.sin(max(pe2, 0) * 14) * (pe2 > 0)
    bx, by = D3[1] + 118, fl + 6
    s.append(f'<g transform="translate({bx} {by}) scale({f(bsc)}) translate({-bx} {-by})">{bag(bx, by, True, 1770, k2)}</g>')
    s.append(pop_ring(D3[0] + 95, YB3 + depth * .5, 80, 44, t - T_TABLE - 0.04, 1780))
    s.append(pop_ring(bx + 4, by - 90, 92, 120, t - T_BAG - 0.04, 1781))
    return "".join(s)


def s09(t):
    # общий план всех трёх → к столу на «столе» → панорама к сумке на «в сумке»
    a = ease_io(clamp((t - 18.45) / 0.55))
    b = ease_io(clamp((t - 19.18) / 0.32))
    drift = clamp((t - 17.56) / 2.14)
    cx = 540 + (300 - 540) * a + (600 - 300) * b + 10 * drift
    cy = 860 + (900 - 860) * a + (930 - 900) * b
    sc = 1.0 + 0.03 * drift + 0.36 * a + 0.06 * b
    push = 0.03 * math.exp(-max(t - T_TABLE, 0) * 5) * (t > T_TABLE) + 0.03 * math.exp(-max(t - T_BAG, 0) * 5) * (t > T_BAG)
    return three_desks(t), cam(cx, cy, sc + push, 0.5 - 0.9 * drift), "#e8d6b0"


# ─── s10: дверь в соседнюю комнату
DOOR = (600, 640, 860, 1250)        # проём: x0, y0, x1, y1 (пол)
TABLE10 = (735, 1040)                # столик в соседней комнате: центр верха


def next_room(t):
    x0, y0, x1, y1 = DOOR
    s = []
    lin_grad([(0, "#f7d9a8", 1), (1, "#e9bf83", 1)], 0, 0, 0, 1, gid="gNext")
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#gNext)"/>')
    s.append(blob(rect_pts(x0, 1140, x1, y1), "#c48f5a"))
    s.append(line([(x0, 1140), (x1, 1140)], 3, "#8a5a32", seed=1900, op=.8))
    # окошко в соседней комнате (тоже кактус) и столик
    s.append(shape(rect_pts(x0 + 130, 690, x0 + 230, 820, 4), "#9fd0f2", blob(rect_pts(x0 + 130, 780, x0 + 230, 820), "#e8c690") +
                   saguaro(x0 + 190, 820, 90, 1910), w=3.6, seed=1901))
    tx, ty = TABLE10
    for xx in (tx - 70, tx + 70):
        s.append(shape(rect_pts(xx - 7, ty + 12, xx + 7, 1170), "#7a4c2c", "", w=3, seed=1902 + xx))
    s.append(shape(rect_pts(tx - 92, ty - 4, tx + 92, ty + 16, 4), "#b07a48", blob(rect_pts(tx - 92, ty + 6, tx + 92, ty + 16), "#8a5a36"), w=3.6, seed=1905))
    return "".join(s)


def door_leaf(theta):
    """Створка на петлях у правого косяка, открывается вглубь соседней комнаты. theta 0 — закрыта, 1 — открыта (≈80°)."""
    x0, y0, x1, y1 = DOOR
    a = math.radians(84 * theta)
    wv = (x1 - x0) * math.cos(a)
    shrink = 0.10 * math.sin(a) * (y1 - y0)
    xl = x1 - wv
    pts = [(xl, y0 + shrink * .4, 1), (x1, y0, 1), (x1, y1, 1), (xl, y1 - shrink * .6, 1)]
    col = mix("#9a5f34", "#6e4123", 0.6 * math.sin(a))
    inner = ""
    if wv > 30:
        for k, (a0, b0) in enumerate([(0.12, 0.45), (0.55, 0.9)]):
            ya, yb = y0 + (y1 - y0) * a0, y0 + (y1 - y0) * b0
            inner += shape([(xl + wv * .18, ya, 1), (x1 - wv * .18, ya, 1), (x1 - wv * .18, yb, 1), (xl + wv * .18, yb, 1)], lib.mul(col, (.88, .86, .86)),
                           "", w=2.6, seed=1920 + k)
        inner += shape(ellipse_pts(xl + wv * .14, (y0 + y1) / 2 + 20, 9, 9, 10), "#e8c35a", "", w=2.4, seed=1925)
    return shape(pts, col, inner, w=4.2, seed=1926)


def wall10():
    x0, y0, x1, y1 = DOOR
    s = []
    lin_grad([(0, "#f3e6c8", 1), (1, "#e8d6b0", 1)], 0, 0, 0, 1, gid="gWall10")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{y1 + 900}" fill="url(#gWall10)"/>')
    lin_grad([(0, "#b9824e", 1), (1, "#a0693c", 1)], 0, 0, 0, 1, gid="gFloor10")
    s.append(f'<rect x="-900" y="{y1}" width="{W + 1800}" height="{H + 900}" fill="url(#gFloor10)"/>')
    for k in range(-8, 18):
        x = 540 + k * 120
        s.append(line([(540 + (x - 540) * .7, y1), (540 + (x - 540) * 2.2, H + 400)], 2.4, "#8a5a32", taper=.1, wmin=.8, seed=1940 + k, op=.7))
    s.append(line([(-900, y1), (W + 900, y1)], 4, INK, taper=.05, wmin=.9, seed=1960))
    s.append(blob(rect_pts(-900, y1 - 34, x0 - 18, y1), "#c9a77a"))
    s.append(blob(rect_pts(x1 + 18, y1 - 34, W + 900, y1), "#c9a77a"))
    # пробковая доска и полка (без надписей) слева
    s.append(shape(rect_pts(70, 520, 340, 760, 6), "#c99a62", "".join(
        shape(rect_pts(px - 34, py - 26, px + 34, py + 26), c, "", w=2.6, seed=1970 + i) for i, (px, py, c) in
        enumerate([(130, 580, "#fff1a0"), (230, 600, "#ffc6d6"), (290, 690, "#c8ecff"), (150, 690, "#d6f6c4")])), w=4.2, seed=1969))
    return "".join(s)


def door_frame():
    x0, y0, x1, y1 = DOOR
    s = shape([(x0 - 22, y1, 1), (x0 - 22, y0 - 22, 1), (x1 + 22, y0 - 22, 1), (x1 + 22, y1, 1), (x1, y1, 1), (x1, y0, 1), (x0, y0, 1), (x0, y1, 1)],
              "#f3ede1", blob(rect_pts(x1, y0 - 22, x1 + 22, y1), "#d6cdb9"), w=4.2, seed=1980)
    return s


def s10_student(t):
    """Студентка (STUDENTS[2]) кладёт телефон на столик за дверью, отходит и идёт обратно."""
    spec = dict(STUDENTS[2])
    sc = .74
    x = 470.0
    walk = None
    turn = smooth(20.0, 20.25, t)
    spec["face"] = 0.75 * (1 - turn) + (-0.45) * turn
    if t > 20.66:
        e = t - 20.66
        x = 470 - 150 * ease_in(clamp(e / 0.4), 1.6) - 260 * max(0, e - 0.4)
        walk = e * 9.0
    pose = {"look": (0.6 * (1 - turn) - 0.5 * turn, 0.2 * (1 - turn)), "mouth": "flat" if t < 20.7 else "smile", "brow": 0.0}
    if walk is not None:
        pose["walk"] = walk
        pose["curl"] = {"L": 0.6, "R": 0.6}
        sw_ = math.sin(walk)
        pose["hand_target"] = {"L": (-104 - 14 * sw_, -282 + 16 * sw_), "R": (104 - 14 * sw_, -282 - 16 * sw_)}
    # правая рука: телефон → на столик → назад
    reach = smooth(19.25, 19.62, t) * (1 - smooth(19.8, 20.05, t))
    hold = t < 19.72
    tx = (TABLE10[0] - 20 - x) / sc
    ty = (TABLE10[1] - 18 - 1250) / sc
    rest = (90, -310)
    if walk is None:
        tgt = (rest[0] + (tx - rest[0]) * reach, rest[1] + (ty - rest[1]) * reach - 40 * math.sin(math.pi * reach))
        pose["hand_target"] = {"R": tgt, "L": (-80, -300 + 4 * math.sin(t * 3))}
        pose["curl"] = {"R": 0.55 if hold else 0.2}
        if hold:
            pose["in_hand"] = {"R": lambda h, a: phone_up(h[0] + 34 * math.cos(math.radians(a)), h[1] + 34 * math.sin(math.radians(a)) - 18, .95, 0, 0.0, 2140)}
        if t > 20.66 - 0.01 and t < 21.0:
            pose["mouth"] = "smile"
    bob = 0.0
    return person.draw(spec, pose, x, 1250 + bob, sc, sd=2100), x


def slam_fx(t):
    e = t - SLAM
    if e < 0 or e > 0.5:
        return ""
    x0, y0, x1, y1 = DOOR
    s = []
    u = e / 0.5
    for k in range(5):
        a = math.radians(-160 + k * 35)
        r0 = 40 + 50 * ease_out(u)
        L = 50 * (1 - u)
        if L < 8:
            break
        cx, cy = (x0 + x1) / 2, y0 - 30
        s.append(line([(cx + math.cos(a) * r0 * 2.2, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + L) * 2.2, cy + math.sin(a) * (r0 + L))], 8, INK,
                      taper=.6, seed=2000 + k))
    for k, (cx, sd) in enumerate([(x0 + 10, 2010), (x1 - 10, 2020)]):
        r = (26 + 40 * ease_out(u)) * (1 - ease_in(u, 3))
        if r < 4:
            continue
        side = -1 if k == 0 else 1
        pts = []
        for i in range(9):
            a = math.pi + math.pi * i / 8
            rr = r * (1 + 0.10 * math.sin(i * 1.9 + k))
            pts.append((cx + side * r * .5 + rr * 1.3 * math.cos(a), y1 + 2 + rr * .8 * math.sin(a)))
        pts += [(cx + side * r * .5 + r * 1.3, y1 + 4, 1), (cx + side * r * .5 - r * 1.3, y1 + 4, 1)]
        s.append('<g>' + shape(pts, "#f1e4c8", blob(ellipse_pts(cx + side * r * .5 + 10, y1 - r * .2, r * .8, r * .3, 10), "#dccaa6", .8),
                                                                 w=3.2, seed=sd) + "</g>")
    return "".join(s)


def s10(t):
    x0, y0, x1, y1 = DOOR
    close = ease_in(clamp((t - 20.28) / (SLAM - 20.28)), 2.2)
    theta = 1 - close
    if t > SLAM:
        e = t - SLAM
        theta = 0.03 * math.exp(-e * 9) * abs(math.sin(e * 30))
    phone_on_table = t >= 19.72
    nr = next_room(t)
    if phone_on_table:
        land = t - 19.72
        nr += phone_up(TABLE10[0] - 20, TABLE10[1] - 56 + (-10 * math.exp(-land * 14) * abs(math.cos(land * 18))), .55 * 0.95 / .55 * .74, 0, 0.0, 2150)
    stud, sx = s10_student(t)
    art = _ST["wall10"] + nr + door_leaf(theta) + door_frame() + slam_fx(t) + stud
    shake = 8 * math.exp(-max(t - SLAM, 0) * 10) * math.sin((t - SLAM) * 60) * (t > SLAM)
    u = clamp((t - 19.3) / 2.34)
    return art, cam(625 - 50 * ease_io(clamp((t - 20.7) / 0.9)) + shake, 990, 1.66 + 0.06 * ease_io(u), -0.3 + 0.5 * u), "#e8d6b0"


# ═══════════════════════════════ s11 / s12: столбики
BASE = 1050
BX = [250, 540, 830]
BW = 170
BH = [300, 390, 660]
BCOL = [("#e2735a", "#c2563f"), ("#e8b23a", "#c9922b"), ("#3cbf63", "#279a4a")]


def bar_heights(t):
    h = []
    for i in range(3):
        if i < 2:
            u = clamp((t - 21.28 - i * 0.12) / 0.75)
            h.append(BH[i] * (ease_out(u, 3) + 0.05 * math.sin(math.pi * u) * (u < 1)))
        else:
            u = clamp((t - 21.36) / 2.49)
            v = 0.55 * ease_out(clamp(u / 0.35), 2) + 0.45 * ease_in(clamp((u - 0.35) / 0.65), 1.3) if u < 1 else 1.0
            hh = BH[2] * v
            if t > 23.85:
                hh = BH[2] * (1 + 0.05 * math.exp(-(t - 23.85) * 5) * math.sin((t - 23.85) * 14))
            h.append(hh)
    return h


def icon_table(sd):
    s = shape(rect_pts(-46, -6, 46, 8, 3), "#b07a48", "", w=3, seed=sd)
    for xx in (-36, 36):
        s += shape(rect_pts(xx - 4, 8, xx + 4, 40), "#7a4c2c", "", w=2.4, seed=sd + 2 + xx)
    s += f'<g transform="translate(0 -10) scale(.62)">{phone_flat(0, 0, 1, 0, sd + 5)}</g>'
    return s


def icon_bag(sd):
    return f'<g transform="translate(0 30) scale(.48)">{bag(0, 0, True, sd)}</g>'


def icon_door(sd):
    s = shape(rect_pts(-34, -46, 34, 46, 3), "#9a5f34", shape(rect_pts(-22, -36, 22, -4), "#874f2a", "", w=2, seed=sd + 1) +
              shape(rect_pts(-22, 4, 22, 36), "#874f2a", "", w=2, seed=sd + 2), w=3.4, seed=sd)
    s += shape(ellipse_pts(24, 4, 5, 5, 8), "#e8c35a", "", w=2, seed=sd + 3)
    s = shape(rect_pts(-44, -54, 44, 46), "#f3ede1", "", w=3, seed=sd + 4) + s
    return s


def badge(x, y, kind, t, i, sd):
    bob = 4 * math.sin(t * 2.2 + i)
    ic = {"table": icon_table, "bag": icon_bag, "door": icon_door}[kind](sd)
    s = shape(ellipse_pts(x, y + bob, 74, 74, 28), "#fbf8ee", blob(ellipse_pts(x + 10, y + bob + 12, 66, 64, 20), "#ece4d0", .8), w=4.4, seed=sd + 50)
    return s + f'<g transform="translate({f(x)} {f(y + bob)})">{ic}</g>'


def star(x, y, sc, rot, sd):
    pts = []
    for i in range(10):
        r = (64 if i % 2 == 0 else 28) * sc
        a = -math.pi / 2 + i * math.pi / 5 + math.radians(rot)
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r, 1))
    inner = blob([(x, y - 70 * sc), (x + 70 * sc, y - 10 * sc), (x + 40 * sc, y + 60 * sc), (x, y + 10 * sc)], "#f4b92e", .8)
    inner += blob(ellipse_pts(x - 16 * sc, y - 18 * sc, 10 * sc, 6 * sc, 8, rot=-30), "#fff6c8", .9)
    return shape(pts, "#ffd84a", inner, w=4.4 * max(sc, .5), seed=sd)


def chart_bg():
    s = []
    lin_grad([(0, "#f6eedb", 1), (1, "#ead9b8", 1)], 0, 0, 0, 1, gid="gChart")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="url(#gChart)"/>')
    for k in range(-6, 30):
        y = -400 + k * 80
        s.append(f'<rect x="-900" y="{y}" width="{W + 1800}" height="2" fill="#d9c7a2" opacity=".6"/>')
    s.append(line([(80, BASE), (1000, BASE)], 7, INK, taper=.05, wmin=.9, seed=2200))
    return "".join(s)


def bars(t, h, star_t=STAR):
    s = []
    for i in range(3):
        x = BX[i]
        hh = max(h[i], 2)
        c, csh = BCOL[i]
        s.append(blob(rect_pts(x - BW / 2 + 12, BASE - hh + 12, x + BW / 2 + 12, BASE), "#b9a27a", .45))
        inner = blob(rect_pts(x + BW * .18, BASE - hh, x + BW / 2, BASE), csh, .85)
        inner += blob(rect_pts(x - BW / 2 + 16, BASE - hh + 14, x - BW / 2 + 34, BASE - 14), "#ffffff", .35)
        s.append(shape(rect_pts(x - BW / 2, BASE - hh, x + BW / 2, BASE, 10), c, inner, w=5, seed=2210 + i))
    # звезда на «дверь»
    e = t - star_t
    if e > -0.02:
        x, y = BX[2], BASE - h[2] - 100
        sc = back_out(clamp((e + 0.02) / 0.3), 2.6) * (1 + 0.05 * math.sin(e * 5))
        s.append(star(x, y + 4 * math.sin(e * 3), sc * 1.25, 12 * math.sin(e * 2.5) + (1 - clamp(e / .3)) * -80, 2230))
        for k in range(8):
            if e > 0.5:
                break
            a = k * math.pi / 4 + .2
            r0 = 90 + 120 * ease_out(e / .5)
            L = 40 * (1 - e / .5)
            s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))], 9, "#ffcf3a", taper=.5, seed=2240 + k))
        if e > 0.3:
            for k in range(3):
                ph = (e * 0.8 + k / 3) % 1
                a = k * 2.1 + 0.6
                sx, sy = x + math.cos(a) * 120, y + math.sin(a) * 90 - 20 * ph
                r = 14 * math.sin(math.pi * ph)
                s.append(blob([(sx, sy - r), (sx + r * .3, sy - r * .3), (sx + r, sy), (sx + r * .3, sy + r * .3), (sx, sy + r), (sx - r * .3, sy + r * .3),
                               (sx - r, sy), (sx - r * .3, sy - r * .3)], "#ffcf3a"))
    for i, kind in enumerate(["table", "bag", "door"]):
        s.append(f'<g transform="translate({BX[i]} {BASE - 92}) scale(.92) translate({-BX[i]} {-(BASE - 92)})">' + badge(BX[i], BASE - 92, kind, t, i, 2260 + i * 60) + "</g>")
    return "".join(s)


def s11(t):
    h = bar_heights(t)
    u = clamp((t - 21.24) / 3.73)
    push = 0.03 * math.exp(-max(t - STAR, 0) * 5) * (t > STAR)
    return _ST["chart"] + bars(t, h), cam(540 + 20 * ease_io(u), 835 - 20 * u, 1.30 + 0.05 * ease_io(u) + push, 0.4 - 0.7 * u), "#f0e4c8"


# ─── s12: выключатель у телефона, столбик не меняется
SW = (1150, 930)       # выключатель
PH12 = (1150, 600)     # телефон


def switch_state(t):
    st = True
    for c in CLICKS:
        if t >= c:
            st = not st
    return st


def toggle(t):
    """Выключатель-тумблер на пластине: рычажок перекидывается с перелётом на каждом щелчке."""
    x, y = SW
    st = 1.0
    ang = -28.0
    for c in CLICKS:
        e = t - c
        if e >= 0:
            st = 1 - st
            u = clamp(e / 0.09)
            tgt = -28 if st > .5 else 28
            prev = -tgt
            jig = 6 * math.exp(-max(e - .09, 0) * 18) * math.cos(max(e - .09, 0) * 50) * (e > .09)
            ang = prev + (tgt - prev) * ease_in(u, 2) + (jig if tgt > 0 else -jig)
    on = st > .5
    s = []
    s.append(shape(rect_pts(x - 70, y - 100, x + 70, y + 100, 18), "#fbf8ee", blob(rect_pts(x + 20, y - 100, x + 70, y + 100, 18), "#e2dccb", .8), w=4.6, seed=2300))
    s.append(shape(rect_pts(x - 30, y - 56, x + 30, y + 56, 10), "#3a3f4c", "", w=3.6, seed=2301))
    lamp = "#3cbf63" if on else "#8a909e"
    if on:
        g = rad_grad([(0, "#9dffb2", .8), (1, "#9dffb2", 0)], x, y - 78, 40, 26)
        s.append(f'<ellipse cx="{x}" cy="{y - 78}" rx="40" ry="26" fill="url(#{g})"/>')
    s.append(shape(ellipse_pts(x, y - 78, 9, 9, 10), lamp, "", w=2.6, seed=2302))
    a = math.radians(ang)
    tip = (x + math.sin(a) * 74, y - math.cos(a) * 74 * (1 if True else 1))
    lever = lib.band([(x, y), ((x + tip[0]) / 2, (y + tip[1]) / 2), tip], 26, 20, step=5, cap=True)
    s.append(shape(lever, "#d9dde8", blob(lib.band([(x + 6, y), (tip[0] + 6, tip[1])], 10, 8, step=5, cap=False), "#b9bfcc", .9), w=3.8, seed=2303))
    s.append(shape(ellipse_pts(x, y, 16, 16, 12), "#9aa3b2", "", w=3, seed=2304))
    return s and "".join(s), on


def click_fx(t):
    s = []
    x, y = SW
    for c in CLICKS:
        e = t - c
        if 0 <= e < 0.3:
            u = e / 0.3
            for k in range(6):
                a = k * math.pi / 3 + .4
                r0 = 110 + 50 * ease_out(u)
                L = 26 * (1 - u)
                s.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + L), y + math.sin(a) * (r0 + L))], 7, "#e2543f", taper=.5, seed=2310 + k))
    return "".join(s)


def level_line(h, t, k):
    """Пунктир на уровне верха «двери» — до телефона: столбик стоит, сколько ни щёлкай."""
    if k <= 0.01:
        return ""
    y = BASE - h
    x0 = BX[2] + BW / 2 + 10
    x1 = x0 + (PH12[0] + 120 - x0) * k
    s = []
    n = int((x1 - x0) / 34)
    for i in range(n):
        a = x0 + i * 34
        s.append(line([(a, y), (a + 20, y)], 5, "#2f6db5", taper=.1, wmin=.8, seed=2330 + i))
    return "".join(s)


def s12(t):
    h = bar_heights(t)
    k = back_out(clamp((t - 24.6) / 0.32), 1.8)
    sw, on = toggle(t)
    glow = 0.0
    for c in CLICKS:
        pass
    on_amt = 1.0 if on else 0.0
    # экран гаснет/загорается за 2 кадра
    last = max([c for c in CLICKS if c <= t], default=None)
    if last is not None and t - last < 0.07:
        on_amt = 0.5
    ph = phone_up(PH12[0], PH12[1], 2.5 * k, 4 * math.sin(t * 1.6), on_amt, 2350)
    if on_amt > 0.6:
        g = rad_grad([(0, "#9fdcff", .6), (1, "#9fdcff", 0)], PH12[0], PH12[1], 240, 300)
        ph = f'<ellipse cx="{PH12[0]}" cy="{PH12[1]}" rx="{f(240 * k)}" ry="{f(300 * k)}" fill="url(#{g})"/>' + ph
    # провод от телефона к выключателю
    wire = line([(PH12[0], PH12[1] + 140 * k), (PH12[0] - 30, PH12[1] + 200), (SW[0] - 10, SW[1] - 118)], 6, "#3a3f4c", taper=.05, wmin=.9, seed=2360) if k > .6 else ""
    swg = f'<g transform="translate({SW[0]} {SW[1]}) scale({f(1.15 * k)}) translate({-SW[0]} {-SW[1]})">{sw}</g>'
    art = _ST["chart"] + bars(t, h) + level_line(h[2], t, smooth(24.9, 25.3, t)) + wire + ph + swg + click_fx(t)
    u = clamp((t - 24.57) / 2.64)
    pop = 0.025 * sum(math.exp(-max(t - c, 0) * 8) * (t > c) for c in CLICKS)
    return art, cam(960 + 15 * ease_io(u), 815, 1.32 + 0.05 * ease_io(u) + pop, 0.3 - 0.6 * u), "#f0e4c8"


# ═══════════════════════════════ кадр
def build_static():
    if _ST:
        return
    brick_defs()
    _ST["sky"] = sky()
    _ST["ground"] = ground()
    _ST["bld"] = building()
    _ST["cls_back"] = classroom_back()
    _ST["wall9"] = wall9()
    _ST["wall10"] = wall10()
    _ST["chart"] = chart_bg()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm, bg = {"s08": s08, "s09": s09, "s10": s10, "s11": s11, "s12": s12}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="{bg}"/><g transform="{cm}">{art}</g>')
