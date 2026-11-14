"""Рилс 49 «зарядка», группа A: планы s01 s04 s05 s06 s12 (Дима в гостиной).
frame(sid, t) -> SVG 1080×1920 (t — общее время ролика). Дима — people.py, кот — cat.py, кисти — hand.py, комната — своя (гостиная:
диван, окно, торшер, полка, часы, ковёр) в манере world.py. Удары — на словах по voice/words.json. Камера у каждого плана своя,
каждый план двигается с первого кадра."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import world as Wd  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, smooth, T  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def tw(word, nth=0):
    """Время начала слова (по тексту, без знаков) — nth-е вхождение."""
    k = 0
    for w in WORDS:
        if w["word"].strip(".,!?").lower() == word.lower():
            if k == nth:
                return w["start"]
            k += 1
    raise KeyError(word)


T_SEL = tw("сел")            # 0.60
T_NEZNAL = tw("знал")        # 5.92 (в плане s05 «не знал» — «не» 5.76)
T_NE = tw("не")
T_KOMNATU = tw("комнату")    # 8.52
T_LUCHSHIJ = tw("лучший")    # 19.20
T_PONYAL = tw("понял")

BS = 0.62
FLOOR = 1590


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def hook_zoom(t, t0, mx=0.4, dur=0.22, rot=-3.0):
    """Влёт камеры (правило 28/29): масштаб 1/(1+mx) → 1 за dur с перелётом 5 %, поворот rot → 0."""
    u = (t - t0) / dur
    if u <= 0:
        return 1 / (1 + mx), rot
    if u < 1:
        e = ease_out(u, 3)
        return 1 / (1 + mx) + (1.05 - 1 / (1 + mx)) * e, rot * (1 - e) - 1.2 * e
    v = (t - t0 - dur) / 0.3
    if v < 1:
        return 1.05 - .05 * ease_io(v), -1.2 * (1 - ease_io(v))
    return 1.0, 0.0


def whip_in(t, t0, dur=0.2):
    u = clamp((t - t0) / dur)
    return (1 - ease_out(u, 3))


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def txt(x, y, s, size, fill="#f6f1e3", stroke=INK, sw=6, anchor="middle", rot=0.0, op=1.0):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-weight="900" font-size="{size:.1f}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linejoin="round" paint-order="stroke" text-anchor="{anchor}" opacity="{op:.3f}" '
            f'transform="rotate({rot:.2f} {x:.1f} {y:.1f})">{s}</text>')


# ═════════════════════════ Дима ═════════════════════════
def dima(t, hip, lean=0.08, arms=None, hands=None, expr=None, head_ang=0.0, feet=None, hood=0.0):
    hip = np.array(hip, float)
    if feet is None:
        feet = {"n": ((hip[0] + 16, hip[1] + 376), 0.0), "f": ((hip[0] - 4, hip[1] + 372), 0.0)}
    p = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet, arms=arms, hands=hands or {}, expr=expr or {}, head_ang=head_ang,
             hood=hood, strings=(3 * osc(t, 1.3), 2 * osc(t, 1.1, 1)))
    return people.draw(p, "dima")


def kw_hand():
    people.C = people.PAL["dima"]
    return dict(shape_fn=people.shape, line_fn=people.line, skin=people.C["SKIN"], skin_sh=people.C["SKIN_SH"], skin_sh2=people.C["SKIN_SH2"])


def layers(d, mid="", front=""):
    return d.get("legs", "") + d["arm_f"] + d["body"] + mid + d["arm_n"] + front


def flip_x(svg, x0, on):
    """Отразить группу по вертикали через x0 (Дима идёт влево). on — масштаб по x (−1..1)."""
    if abs(on - 1.0) < 1e-6:
        return svg
    return f'<g transform="translate({x0:.2f} 0) scale({on:.4f} 1) translate({-x0:.2f} 0)">{svg}</g>'


# ═════════════════════════ гостиная ═════════════════════════
WALL_C = {"day": "#ead8b0", "sunset": "#e8c79a", "tidy": "#ead8b0"}
SOFA_C, SOFA_SH, SOFA_D = "#6f9a8a", "#557d6f", "#44665a"
WOOD, WOOD_SH = "#c98f5a", "#a8723f"


def wall(mode):
    w = WALL_C.get(mode, "#ead8b0")
    s = [f'<rect x="-1400" y="-1400" width="4200" height="{FLOOR + 1400}" fill="{w}"/>']
    # обои: широкие полосы тоном чуть темнее
    for k in range(-6, 14):
        s.append(f'<rect x="{k * 220}" y="-1400" width="110" height="{FLOOR + 1400}" fill="{mix(w, "#b08850", .10)}"/>')
    # плинтус
    s.append(shape(rect_pts(-1400, FLOOR - 70, 2800, FLOOR), "#f3ead8", blob(rect_pts(-1400, FLOOR - 16, 2800, FLOOR), "#cfc3aa", .9), w=4.4, seed=1801))
    return "".join(s)


WIN = (-110, 330, 380, 1080)


def window(mode, t=0.0):
    x0, x1, y0, y1 = WIN
    if mode == "sunset":
        sky = lib.lin_grad([(0, "#5a6aa8", 1), (.45, "#ec8f6e", 1), (1, "#ffd08a", 1)], 0, 0, 0, 1)
    else:
        sky = lib.lin_grad([(0, "#8fc4ea", 1), (1, "#dff0f6", 1)], 0, 0, 0, 1)
    inner = f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>'
    if mode == "sunset":
        inner += blob(ellipse_pts(x0 + 230, y1 - 250, 120, 120, 20), "#ffe9a8")
        inner += blob(ellipse_pts(x0 + 230, y1 - 250, 86, 86, 20), "#fff6d2")
        for cx, cy, rx in ((x0 + 90, y0 + 250, 110), (x0 + 360, y0 + 160, 90)):
            inner += blob(ellipse_pts(cx, cy, rx, 26, 12), "#f7b6a0", .9)
        roof, win_c = "#4a3a58", "#ffd27a"
    else:
        inner += blob(ellipse_pts(x0 + 110, y0 + 170, 60, 60, 18), "#fff3c4")
        for cx, cy in ((x0 + 300, y0 + 120), (x0 + 380, y0 + 280)):
            inner += blob(ellipse_pts(cx, cy, 70, 24, 12), "#ffffff", .9)
        roof, win_c = "#7f8fa8", "#b9d3e6"
    inner += blob([(x0 - 20, y1 - 200), (x0 + 90, y1 - 230), (x0 + 90, y1 - 290), (x0 + 220, y1 - 290), (x0 + 220, y1 - 220),
                   (x1 + 20, y1 - 250), (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)], roof)
    for x, y in ((x0 + 120, y1 - 250), (x0 + 160, y1 - 250), (x0 + 270, y1 - 180), (x0 + 340, y1 - 190)):
        inner += blob(rect_pts(x, y, x + 24, y + 32), win_c)
    fr = "#f2e9d8"
    mx = (x0 + x1) / 2
    inner += blob(rect_pts(mx - 14, y0, mx + 14, y1), fr) + blob(rect_pts(x0, (y0 + y1) / 2 - 14, x1, (y0 + y1) / 2 + 14), fr)
    s = [shape(rect_pts(x0, y0, x1, y1, 10), fr, inner, w=5, seed=1810)]
    s.append(shape(rect_pts(x0 - 30, y1 - 4, x1 + 30, y1 + 34, 6), fr, blob(rect_pts(x0 - 30, y1 + 20, x1 + 30, y1 + 34), "#d6ccbb"), w=4.4, seed=1811))
    # штора справа
    cur = [(x1 - 10, y0 - 40), (x1 + 120, y0 - 40), (x1 + 140, y1 + 10), (x1 + 110, y1 + 60), (x1 - 10, y1 + 60)]
    s.append(shape(cur, "#c4673f", "".join(line([(x1 + 20 + 28 * k, y0 - 30), (x1 + 24 + 28 * k, y1 + 40)], 3.4, "#9c4c2c", seed=1820 + k, op=.85)
                                            for k in range(4)), w=4.6, seed=1812))
    s.append(line([(x0 - 60, y0 - 50), (x1 + 160, y0 - 50)], 7, WOOD_SH, taper=.05, wmin=.9, seed=1813))
    return "".join(s)


def floor_rug():
    col = "#b98d5f"
    inner = "".join(line([(-1400, FLOOR + 60 + k * 90 + k * k * 8), (2800, FLOOR + 60 + k * 90 + k * k * 8)], 3, mix(col, "#000000", .25),
                         taper=.05, wmin=.9, seed=1900 + k, op=.8) for k in range(8))
    inner += blob(rect_pts(-1400, FLOOR, 2800, FLOOR + 40), "#000000", .12)
    s = [shape(rect_pts(-1400, FLOOR, 2800, 3600), col, inner, w=4.6, seed=1901)]
    rug = [(120, 1650), (1000, 1650), (1060, 1840), (60, 1840)]
    ri = blob([(160, 1690), (960, 1690), (1000, 1800), (110, 1800)], "#e9c46a", .9)
    ri += "".join(line([(150 + k * 90, 1655), (130 + k * 95, 1835)], 3, "#b84c3a", taper=.05, wmin=.9, seed=1910 + k, op=.8) for k in range(9))
    s.append(shape(rug, "#c75a45", ri, w=4.6, seed=1902))
    return "".join(s)


SEAT_Y = 1400


def sofa():
    """Диван анфас: x 330–1010, сиденье 1400. Возвращает (задняя часть, передняя часть — подлокотники и подушки сиденья)."""
    back = []
    bk = rect_pts(350, 1150, 990, 1420, 40)
    inner = blob(rect_pts(350, 1150, 420, 1420), SOFA_SH, .6) + blob(rect_pts(350, 1380, 990, 1420), SOFA_D, .8)
    back.append(shape(bk, SOFA_C, inner, w=5, seed=1950))
    for k, x in enumerate((385, 685)):
        cu = rect_pts(x, 1200, x + 270, 1400, 30)
        back.append(shape(cu, mix(SOFA_C, "#ffffff", .1), blob(rect_pts(x + 190, 1200, x + 270, 1400), SOFA_SH, .6), w=4.4, seed=1951 + k))
    front = []
    seat = rect_pts(330, 1390, 1010, 1500, 28)
    back.append(shape(seat, SOFA_C, blob(rect_pts(330, 1450, 1010, 1500), SOFA_SH, .8) + line([(670, 1394), (670, 1496)], 3.4, SOFA_D, seed=1960, taper=.05, wmin=.9),
                       w=5, seed=1961))
    for k, x in enumerate((296, 944)):
        arm = rect_pts(x, 1250, x + 90, 1520, 34)
        front.append(shape(arm, SOFA_C, blob(rect_pts(x + (50 if k == 0 else 0), 1250, x + 90 - (0 if k == 0 else 50), 1520), SOFA_SH, .65), w=5,
                           seed=1962 + k))
    for x in (340, 950):
        front.append(shape(rect_pts(x, 1520, x + 40, 1590, 6), WOOD_SH, "", w=4, seed=1965 + x % 7))
    return "".join(back), "".join(front)


def floor_lamp(on=1.0):
    x = 1140
    s = [line([(x, 1560), (x, 880)], 12, "#5d5560", taper=.05, wmin=.9, seed=1970)]
    s.append(shape(ellipse_pts(x, 1580, 70, 18, 12), "#5d5560", "", w=4, seed=1971))
    sh = [(x - 80, 900, 1), (x - 54, 780, 1), (x + 54, 780, 1), (x + 80, 900, 1)]
    s.append(shape(sh, mix("#f2cf86", "#fff0b4", on), blob([(x + 20, 780), (x + 54, 780), (x + 80, 900), (x + 30, 900)], "#d9ab5a", .8), w=4.6, seed=1972))
    return "".join(s)


def shelf_wall(items=0.0, books_on=True):
    """Книжная полка на стене: доска x 780–1180, y 820; на ней книги, горшок, рамка. items — 0..1 нарастающий порядок (не используется)."""
    x0, x1, y = 780, 1180, 840
    s = [shape(rect_pts(x0, y, x1, y + 24, 3), WOOD, blob(rect_pts(x0, y + 14, x1, y + 24), WOOD_SH, .9), w=4.4, seed=1980)]
    return "".join(s)


def shelf_things():
    """Содержимое полки в порядке: книги, горшок."""
    s = []
    cols = ["#d4a23e", "#c44f3a", "#3f7a72", "#8ab6d6", "#e07a5f"]
    x = 800
    for k, c in enumerate(cols):
        h = 120 + 18 * (k % 3)
        w = 34 + 4 * (k % 2)
        s.append(shape(rect_pts(x, 840 - h, x + w, 840, 2), c, blob(rect_pts(x + w - 10, 840 - h, x + w, 840), mix(c, "#000000", .25), .8) +
                       line([(x + 6, 840 - h + 24), (x + w - 6, 840 - h + 24)], 2.6, mix(c, "#ffffff", .5), seed=1985 + k, taper=.05, wmin=.9), w=3.6,
                       seed=1986 + k))
        x += w + 2
    px = 1060
    s.append(shape([(px - 40, 838, 1), (px + 40, 838, 1), (px + 30, 770, 1), (px - 30, 770, 1)], "#c4673f",
                   blob([(px + 6, 770), (px + 30, 770), (px + 40, 838), (px + 10, 838)], "#9c4c2c", .9), w=4, seed=1990))
    for k in range(6):
        a = -2.5 + k * .4
        s.append(line([(px, 772), (px + 80 * math.cos(a), 772 + 100 * math.sin(a))], 15, "#5f9a5a", taper=.6, seed=1991 + k))
    return "".join(s)


def plant_floor():
    px, py = 120, FLOOR + 20
    s = [shape([(px - 60, py, 1), (px + 60, py, 1), (px + 46, py - 120, 1), (px - 46, py - 120, 1)], "#c4673f",
               blob([(px + 10, py - 120), (px + 46, py - 120), (px + 60, py), (px + 20, py)], "#9c4c2c", .9), w=4.6, seed=1995)]
    for k in range(7):
        a = -2.9 + k * .45
        s.append(line([(px, py - 120), (px + 150 * math.cos(a), py - 120 + 190 * math.sin(a))], 22, "#5f9a5a", taper=.6, seed=1996 + k))
    return "".join(s)


def clock(h, m, mode="day", k=1.0, x=640, y=560):
    return Wd.clock_wall(h, m, mode, k, x, y)


def frame_pic():
    x, y = 1000, 600
    ins = blob([(x - 70, y - 50), (x - 20, y - 20), (x + 30, y - 70), (x + 70, y - 30), (x + 70, y + 50), (x - 70, y + 50)], "#8fc4a8")
    ins += blob(ellipse_pts(x + 30, y - 24, 14, 14, 10), "#f6e08a")
    return shape(rect_pts(x - 90, y - 76, x + 90, y + 76, 4), "#f6efe0", "", w=4.6, seed=2000) + shape(rect_pts(x - 70, y - 56, x + 70, y + 56), "#cfe7ea", ins, w=3, seed=2001)


def room_base(t, mode="day", clock_t=(10, 0), with_lamp=True, wall_extra=""):
    o = [wall(mode), window(mode, t), floor_rug()]
    if mode == "sunset":
        x0, x1, y0, y1 = WIN
        for dx, w in ((0, 200), (300, 120)):
            pts = [(x0 + 80 + dx, y0 + 80), (x0 + 80 + dx + w, y0 + 80), (x0 + 1400 + dx + w, FLOOR + 260), (x0 + 1400 + dx - 100, FLOOR + 260)]
            o.append(blob(pts, "#ffcf8e", .3, 'style="mix-blend-mode:screen"'))
    o.append(frame_pic())
    o.append(clock(clock_t[0], clock_t[1], mode, 1.0, 700, 560))
    o.append(shelf_wall() + shelf_things())
    o.append(plant_floor())
    return "".join(o)


def room_glow(mode):
    if mode == "sunset":
        x0, x1, y0, y1 = WIN
        o = []
        g = lib.rad_grad([(0, "#ffb36e", .42), (1, "#ffb36e", 0)], 100, 800, 1500, 1300)
        o.append(f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})" style="mix-blend-mode:screen"/>')
        g2 = lib.rad_grad([(0, "#2a1208", 0), (.6, "#2a1208", 0), (1, "#2a1208", .35)], 540, 1000, 1500, 1500)
        o.append(f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g2})"/>')
        return "".join(o)
    g = lib.rad_grad([(0, "#fff3d0", .28), (1, "#fff3d0", 0)], 100, 700, 1400, 1100)
    return f'<rect x="-1400" y="-1400" width="4200" height="4400" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def vignette(col="#2a1408", k=.32):
    g = lib.rad_grad([(0, col, 0), (.62, col, 0), (1, col, k)], 540, 900, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def compose(world_svg, cam, mode="day", front=""):
    cx, cy, s, r = cam
    set_ink(s)
    o = ['<rect width="1080" height="1920" fill="#e7cfa3"/>',
         f'<g transform="{lib.cam(cx, cy, s, r)}">{world_svg}{room_glow(mode)}{front}</g>', vignette()]
    return lib.svg("".join(o))


def sofa_with_cat(t, cat_x, cat_k=.7, cat_st=None, front_extra=""):
    b, f = sofa()
    st = cat_st or {}
    return b, Cat.draw(cat_x, SEAT_Y + 6, cat_k, st, t), f


# ═════════════════════════ телефон ═════════════════════════
PH_W, PH_H = 104.0, 206.0


def phone(x, y, k=1.0, rot=0.0, screen="red", t=0.0, flash=1.0, size=1.0):
    """Смартфон (x, y — центр). screen: 'red' — красный экран с батарейкой 1 % (flash — яркость мигания), 'dead' — чёрный."""
    def P(pts):
        return T(pts, x, y, k, rot)
    hw, hh = PH_W / 2, PH_H / 2
    body = P(rect_pts(-hw, -hh, hw, hh, 16))
    s = [blob(P(rect_pts(-hw + 8, -hh + 10, hw + 8, hh + 10, 16)), "#000000", .13)]
    if screen == "red":
        scr_col = mix("#7a1c1c", "#ff3b30", flash)
    else:
        scr_col = "#14131a"
    inner = blob(P(rect_pts(-hw + 7, -hh + 9, hw - 7, hh - 9, 10)), scr_col)
    if screen == "red":
        bx, by = 0, 6
        inner += shape(P(rect_pts(-34, by - 18, 28, by + 22, 5)), "#26181a", blob(P(rect_pts(-30, by - 14, -20, by + 18)), "#ff6a5a", flash), w=3, seed=2210)
        inner += shape(P(rect_pts(28, by - 8, 36, by + 12, 2)), "#26181a", "", w=2.4, seed=2211)
    else:
        inner += blob(P(ellipse_pts(-hw * .4, -hh * .8, 10, 6, 8)), "#2a2833", .9)
        inner += blob(P([(-hw + 14, -hh + 16), (-hw + 40, -hh + 16), (-hw + 14, hh - 40)]), "#2c2a35", .8)
    s.append(shape(body, "#262630", inner, w=4.4, seed=2212))
    s.append(blob(P(ellipse_pts(0, -hh + 18, 14, 3.2, 8)), "#0a0a10"))
    return "".join(s)


def phone_texts(x, y, k, rot, t, flash):
    """Подпись '1%' на экране (шрифт IDB): отдельным слоем, чтобы вращаться вместе с телефоном."""
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    px, py = x + (0 * c - (-46) * s_) * k, y + (0 * s_ + (-46) * c) * k
    return txt(px, py + 10 * k, "1%", 34 * k, "#fff1ee", "#4a0d0d", 4, rot=rot, op=.55 + .45 * flash)


# ═════════════════════════ s01: хук — телефон сел ═════════════════════════
def s01(t):
    hip = (400.0, 1262.0)
    # красный экран мигает; на «сел» (0.60) гаснет
    dead = t >= T_SEL
    flash = 0.0 if dead else (.5 + .5 * math.sin(2 * math.pi * 5.5 * t + .6))
    shake = 0.0 if not dead else smooth(T_SEL, T_SEL + .1, t) * (1 - smooth(1.1, 1.7, t) * .4)
    jit = 14 * shake
    # телефон перед лицом, чуть вздрагивает
    px = hip[0] + 330 + 8 * osc(t, 3.0) + jit * osc(t, 12) * .7
    py = hip[1] - 300 + 6 * osc(t, 2.2) + jit * osc(t, 15, 1) * .9
    rot_p = 5 * osc(t, 1.7) + 12 * shake * osc(t, 11)
    R = PH_W / 2
    wr = (px - R - 62 * BS + 6, py + 38)
    arms = {"n": ("ik", wr, -1), "f": ("ang", .22, .35)}
    hands = {"n": dict(kind="none"), "f": dict(kind="open", flip=-1, dir=(.15, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)}
    surprise = smooth(T_SEL - .05, T_SEL + .12, t)
    ex = dict(lid=.7 + .3 * surprise, look=(.8, -.4 + .15 * surprise), brows="worry" if surprise < .5 else "up",
              mouth="talk" if surprise > .3 else "flat", open=.9 * surprise + .1, smile=-.5 * surprise,
              hair=7 * shake * osc(t, 7), closed=blink_at(t, 0.38, .12) * (1 - surprise))
    d = dima(t, hip, arms=arms, hands=hands, expr=ex, head_ang=.06 - .1 * surprise + .015 * osc(t, 2.4), lean=.1 - .05 * surprise + .02 * osc(t, 1.9),
             hood=5 * bump(t, T_SEL, .3))
    kw = kw_hand()
    old = people.LWK
    people.LWK = BS
    try:
        gb, gf = Hand.grip((px, py + 38), R, -1, k=BS * 1.05, h=74, seed=2300, **kw)
    finally:
        people.LWK = old
    ph = phone(px, py, 1.0, rot_p, "dead" if dead else "red", t, flash)
    ph_txt = "" if dead else phone_texts(px, py, 1.0, rot_p, t, flash)
    # знак «пусто»: после гашения — крестик-батарейка и штрихи тряски
    fx = ""
    if dead:
        u = clamp((t - T_SEL) / .25)
        for j in range(5):
            a = -1.25 + j * .5
            r0, r1 = 120 + 20 * (1 - u), 150 + 60 * u
            fx += line([(px + r0 * math.cos(a), py - 20 + r0 * math.sin(a) * 1.3), (px + r1 * math.cos(a), py - 20 + r1 * math.sin(a) * 1.3)], 6, INK,
                       seed=2310 + j, op=clamp(u * 1.5) * (1 - smooth(.9, 1.4, t)), taper=.4, wmin=.3)
    w = room_base(t, "day", (10, 0))
    b, cat, f = sofa_with_cat(t, 800, .7, dict(look=(-.4, .2), blink=blink_at(t, .9, .2), tail=4 * osc(t, .6)))
    z, r = hook_zoom(t, 0.0, .4, .22, -3.5)
    k = ease_io(clamp(t / 1.7))
    hit = bump(t, T_SEL, .3)
    cam = (hip[0] + 195 + 20 * k, 1010 - 15 * k, 1.75 * z * (1 + .05 * k + .06 * hit), r + .4 * osc(t, .4) + 1.4 * hit * osc(t, 12))
    body = w + b + cat + f + layers(d, gb + ph + ph_txt + gf, fx)
    return compose(body, cam, "day")


# ═════════════════════════ ходьба ═════════════════════════
def walk_feet(hip, p):
    """Ходьба на месте по фазе p (шаги): стопы ближней и дальней по кругу, подъём при выносе."""
    out = {}
    for side, ph, dx in (("n", 0.0, 16), ("f", .5, -4)):
        a = 2 * math.pi * (p + ph)
        x = hip[0] + dx + 70 * math.sin(a)
        lift = max(0.0, math.cos(a)) * 80
        out[side] = ((x, hip[1] + 376 - lift), .22 * math.cos(a))
    return out


# ═════════════════════════ s04: ходит по гостиной туда-сюда ═════════════════════════
def dima_x_s04(t):
    # 3.6 → вправо до 4.45, разворот, влево до 5.2
    if t < 4.45:
        u = (t - 3.6) / .85
        return 250 + 460 * ease_io(clamp(u)) * .9 + 80 * u, 1
    if t < 4.6:
        return 250 + 460 * .9 + 80 + 0, -1 + 2 * (1 - smooth(4.45, 4.6, t)) * 0 - 2 * smooth(4.45, 4.6, t) + 1
    u = (t - 4.6) / .62
    return 790 - 360 * ease_io(clamp(u)), -1


def s04(t):
    # положение по x: плавный ход туда и обратно, разворот сжатием по x
    if t < 4.42:
        x = 230 + 520 * ease_io(clamp((t - 3.6) / .82)) ** .9
    else:
        x = 750 - 330 * ease_io(clamp((t - 4.52) / .7))
    face = 1.0 if t < 4.42 else (-1.0 if t > 4.58 else 1 - 2 * smooth(4.42, 4.58, t))
    dist = 230 + 0
    # пройденный путь для шагов
    path = (min(t, 4.45) - 3.6) * 620 + max(0.0, t - 4.5) * 460 if t > 3.6 else 0
    p = (t - 3.6) * 2.6
    hip = (x, 1262.0 + 5 * abs(math.sin(2 * math.pi * p)))
    feet = walk_feet(hip, p)
    sw = osc(p, 1.0)
    arms = {"n": ("ang", -.5 + .08 * sw, .15), "f": ("ang", -.45 - .08 * sw, .15)}
    hands = {"n": dict(kind="open", flip=-1, dir=(-.6, .8), curl=(.8, .85, .85, .85), spread=.05, thumb=.8),
             "f": dict(kind="open", flip=-1, dir=(-.6, .8), curl=(.8, .85, .85, .85), spread=.05, thumb=.8)}
    look = .8 * math.sin(2 * math.pi * (t - 3.6) / 1.4)
    ex = dict(lid=.5, look=(.5 + .4 * look, -.1), brows="tired", mouth="flat", closed=blink_at(t, 4.9, .16))
    d = dima(t, hip, lean=.1 + .02 * sw, arms=arms, hands=hands, expr=ex, head_ang=.07 * look, feet=feet)
    dm = flip_x(layers(d), hip[0], face)
    w = room_base(t, "day", (10, 0))
    # кот на диване провожает взглядом: поворот головы за Димой
    tn = clamp((x - 800) / 420, -1, 1)
    b, cat, f = sofa_with_cat(t, 800, .7, dict(turn=-.25 + .8 * tn if False else clamp(tn, -1, 1), look=(clamp(tn, -1, 1), .1), tilt=-5 * tn,
                                                blink=blink_at(t, 4.1, .2), tail=6 * osc(t, .9)))
    ww = whip_in(t, 3.6, .2)
    cxx = .8 * x + .2 * 540 + 60 + 220 * ww
    cam = (cxx, 1060, 1.08 + .03 * ease_io(clamp((t - 3.6) / 1.6)), -.8 * (1 - ease_io(clamp((t - 3.6) / 1.4))) + .5 * osc(t, .5))
    return compose(w + b + cat + f + dm, cam, "day")


# ═════════════════════════ s05: «не знал» — вопросы и часы ═════════════════════════
def qmark(x, y, size, u, rot, t):
    if u <= 0:
        return ""
    sc = lib.back_out(clamp(u * 1.6), 2.2)
    return txt(x, y - 12 * math.sin(t * 5 + x), "?", size * sc, "#f6f1e3", INK, 9, rot=rot)


def s05(t):
    hip = (440.0 + 14 * osc(t, 1.1), 1262.0)
    # разводит руки: к «не» (5.76) подъём до пика; до этого шагает на месте/покачивается
    sp = smooth(5.55, 5.9, t)
    sh = 1 + .0 * sp
    arms = {"n": ("ang", .5 + .7 * sp + .05 * osc(t, 1.3), .5 + .25 * sp), "f": ("ang", -.2 + .1 * osc(t, 1.7) - 1.0 * sp, .5 + .1 * sp)}
    hands = {"n": dict(kind="open", flip=-1, dir=(.9, -.3 * sp - .1 + .0), curl=(.05, .1, .1, .15), spread=.35, thumb=.1),
             "f": dict(kind="open", flip=-1, dir=(-.9, -.2), curl=(.05, .1, .1, .15), spread=.35, thumb=.1)}
    ex = dict(lid=.6 + .4 * sp, look=(.2 + .6 * osc(t, .9), -.2), brows="worry" if sp > .3 else "tired", mouth="talk" if sp > .3 else "flat",
              open=.5 * sp, smile=-.3 * sp, closed=blink_at(t, 5.35, .16))
    d = dima(t, hip, lean=.08 - .06 * sp, arms=arms, hands=hands, expr=ex, head_ang=.05 - .05 * sp + .03 * osc(t, 1.5))
    hx, hy = d["head"]
    # вопросительные знаки над головой на «не знал»
    qs = ""
    for j, (dx, dy, sz, rt) in enumerate(((-90, -250, 150, -14), (10, -330, 190, 6), (110, -260, 140, 16))):
        qs += qmark(hx + dx, hy + dy, sz, (t - (5.72 + .1 * j)) / .3, rt, t)
    # часы: минутная стрелка прыгает на полчаса, потом ещё
    jumps = [5.30, 6.15]
    m = 0.0
    for j, tj in enumerate(jumps):
        m += 30 * (lib.spring(clamp((t - tj) / 0.5, 0, 1) * .5, 3.0, 9.0) if t > tj else 0)
    hh_, mm_ = 10 + (m // 60), m % 60
    hh_ = 10 + m / 60
    mm_ = m % 60
    clk = clock(hh_, mm_, "day", 1.25, 700, 560)
    clk += txt(800, 790, "", 10)
    w = wall("day") + window("day", t) + floor_rug() + frame_pic() + clk + shelf_wall() + shelf_things() + plant_floor()
    b, cat, f = sofa_with_cat(t, 800, .7, dict(look=(-.6, .2), tilt=4, blink=blink_at(t, 6.4, .2), tail=5 * osc(t, .8)))
    u = ease_io(clamp((t - 4.8) / 2.5))
    shk = 5 * bump(t, T_NE, .3) * osc(t, 11)
    cam = (560 + 70 * u + shk, 1030 - 70 * u, 1.0 + .5 * u + .06 * bump(t, T_NE, .25), .8 * (1 - u) - .6 * u * 0 + .5 * osc(t, .6))
    return compose(w + b + cat + f + layers(d, "", qs), cam, "day")


# ═════════════════════════ s06: наводит порядок ═════════════════════════
CLUTTER = [
    # kind, старт (x, y), финиш (x, y), t0, цвет
    ("shirt", (210, 1700), (700, 1335), 7.50, "#8ab6d6"),
    ("sock", (860, 1760), (1110, 840 - 6), 7.62, "#c44f3a"),
    ("mug", (110, 1740), (990, 826), 7.74, "#3f7a72"),
    ("book", (620, 1790), (900, 840), 7.86, "#d4a23e"),
    ("pillow", (980, 1700), (955, 1315), 8.00, "#e9c46a"),
    ("cup", (330, 1820), (1030, 836), 8.14, "#e07a5f"),
]


def clutter_item(kind, x, y, rot, col):
    def P(pts):
        return T(pts, x, y, 1.0, rot)
    if kind == "shirt":
        return shape(P([(-70, -20), (-30, -34), (0, -22), (30, -34), (70, -20), (60, 22), (36, 20), (34, 52), (-34, 52), (-36, 20), (-60, 22)]), col,
                     blob(P([(0, -22), (30, -34), (70, -20), (60, 22), (36, 20), (34, 52), (0, 52)]), mix(col, "#000000", .2), .8), w=4, seed=2400)
    if kind == "sock":
        return shape(P([(-18, -50), (18, -50), (20, 10), (46, 22), (44, 48), (-10, 48), (-20, 6)]), col,
                     blob(P([(-18, -50), (18, -50), (18, -34), (-18, -34)]), "#f6f1e3"), w=3.8, seed=2401)
    if kind == "mug":
        return Wd.mug(x, y + 40, .55, rot, col)
    if kind == "cup":
        return Wd.mug(x, y + 40, .45, rot, col)
    if kind == "book":
        return shape(P(rect_pts(-52, -12, 52, 14, 3)), col, blob(P(rect_pts(-52, 4, 52, 14)), mix(col, "#000000", .3), .9), w=4, seed=2402)
    if kind == "pillow":
        return shape(P(rect_pts(-62, -50, 62, 50, 26)), col, blob(P(rect_pts(20, -50, 62, 50, 20)), mix(col, "#000000", .15), .8) +
                     line(P([(-40, -12), (0, 0), (40, -12)]), 3, mix(col, "#000000", .35), seed=2403, op=.8), w=4.4, seed=2404)
    return ""


def clutter(t):
    s = []
    for i, (kind, a, b, t0, col) in enumerate(CLUTTER):
        dur = .5
        u = clamp((t - t0) / dur)
        e = ease_io(u)
        x = a[0] + (b[0] - a[0]) * e
        arc = 260 + 40 * i
        y = a[1] + (b[1] - a[1]) * e - arc * math.sin(math.pi * u) * (1 if u < 1 else 0)
        rot = 12 * (-1) ** i * (1 - e) + 28 * math.sin(math.pi * u) * (-1) ** i
        sq = 1.0
        if u >= 1:
            # посадка с пружиной
            x, y, rot = b[0], b[1], 0
            y += 8 * math.exp(-(t - t0 - dur) * 12) * math.cos((t - t0 - dur) * 40)
        s.append(clutter_item(kind, x, y, rot, col))
    return "".join(s)


def dust_bunnies(t, clean):
    s = []
    for j, (x, y) in enumerate(((420, 1640), (700, 1720), (240, 1690), (900, 1660))):
        a = 1 - clamp((t - 7.4 - .08 * j) / .3)
        if a > 0:
            s.append(blob(ellipse_pts(x, y, 34 * a, 18 * a, 10), "#a49c8e", .9))
            s.append(blob(ellipse_pts(x - 10, y - 6, 18 * a, 12 * a, 8), "#bdb5a6", .9))
    return "".join(s)


def vacuum(x, y, k, slide, t):
    """Пылесос-щётка: головка на полу в (x, y), труба идёт вверх-влево к руке; возвращает (svg, точка рукоятки)."""
    s = []
    head = shape(rect_pts(x - 74, y - 24, x + 74, y + 18, 12), "#c44f3a",
                 blob(rect_pts(x + 20, y - 24, x + 74, y + 18, 10), "#9c3a2a", .8) + blob(rect_pts(x - 74, y + 6, x + 74, y + 18), "#2b2630", .9), w=4.4, seed=2420)
    top = (x - 30, y - 24)
    handle = (x - 180, y - 470)
    pole = lib.line([top, handle], 15, INK, seed=2421, taper=.05, wmin=.95) + lib.line([top, handle], 8, "#c9ced8", seed=2422, taper=.05, wmin=.95)
    body = shape(rect_pts(x - 70, y - 120, x - 10, y - 20, 14), "#d4a23e", blob(rect_pts(x - 30, y - 120, x - 10, y - 20), "#a97b25", .8), w=4.4, seed=2423)
    grip = shape(rect_pts(handle[0] - 10, handle[1] - 24, handle[0] + 46, handle[1] + 8, 10), "#2b2630", "", w=4, seed=2424)
    s.append(pole + body + head)
    return "".join(s), grip, handle


def s06(t):
    cl = smooth(T_KOMNATU - .1, T_KOMNATU + .1, t)
    sw = osc(t, 2.2)
    hip = (430.0 + 70 * (.5 + .5 * math.sin(2 * math.pi * (t - 7) / 1.9)), 1262.0)
    # щётка ездит перед ним, рука на рукоятке трубы
    vx = hip[0] + 400 + 70 * sw
    vy = 1655
    vsvg, grip_svg, handle = vacuum(vx, vy, 1.0, sw, t)
    # рукоятка в руке: запястье у рукоятки
    wr = (handle[0] - 6, handle[1] + 14)
    # дальняя рука с тряпкой: протирает вверх-вниз перед собой
    rag_c = (hip[0] + 210, 1060 + 60 * osc(t, 3.0))
    arms = {"n": ("ik", wr, -1), "f": ("ik", (rag_c[0] - 30, rag_c[1] + 30), -1)}
    hands = {"n": dict(kind="open", flip=-1, dir=(.3, 1), curl=(.85, .9, .9, .9), spread=.05, thumb=.9),
             "f": dict(kind="none")}
    ex = dict(lid=.55 + .3 * cl, look=(.7, .6), brows="calm", mouth="smile" if cl < .5 else "grin", smile=.5, closed=blink_at(t, 7.9, .16),
              hair=4 * osc(t, 2.4))
    p = (t - 7.0) * 2.4
    feet = walk_feet(hip, p)
    d = dima(t, hip, lean=.1, arms=arms, hands=hands, expr=ex, head_ang=.1 + .03 * sw, feet=feet, hood=3 * osc(t, 2.2))
    rag = Wd.rag(rag_c[0], rag_c[1], .7, 18 * osc(t, 3.0), t)
    mode = "day"
    w = room_base(t, mode, (10, 40))
    b, f = sofa()
    cat = Cat.draw(800, SEAT_Y + 6, .7, dict(look=(-.7, .2), blink=blink_at(t, 8.3, .2), tail=7 * osc(t, 1.0), tilt=3 * osc(t, 1.2)), t)
    items = clutter(t)
    dust = dust_bunnies(t, cl)
    # блёстки чистоты на «комнату»
    spk = ""
    if t > T_KOMNATU:
        u = clamp((t - T_KOMNATU) / .7)
        for j, (sx, sy, sz) in enumerate(((300, 1650, 54), (640, 1700, 44), (860, 1400, 60), (480, 1250, 40), (160, 1500, 36), (1000, 1100, 46), (720, 980, 36))):
            q = clamp((u - .06 * j) * 1.8)
            if q > 0:
                spk += Wd.sparkle(sx, sy, sz * math.sin(math.pi * clamp(q)) , t * 2 + j)
    ww = whip_in(t, 7.0, .2)
    hit = bump(t, T_KOMNATU, .3)
    cam = (560 + 20 * (t - 7.2) + 140 * ww, 1100, 1.0 + .08 * ease_io(clamp((t - 7.2) / 1.8)) + .06 * hit, .6 - .4 * ease_io(clamp((t - 7.2) / 1.8)) + 1.0 * hit * osc(t, 9))
    return compose(w + b + cat + f + dust + layers(d, vsvg + grip_svg, rag) + items + spk, cam, mode)


# ═════════════════════════ s12: вечер, понимает ═════════════════════════
def bulb(x, y, u, t):
    """Лампочка-мысль: растёт с перелётом, горит, лучи."""
    if u <= 0:
        return ""
    sc = lib.back_out(clamp(u * 1.4), 2.4)
    s = []
    glow = lib.rad_grad([(0, "#fff0a0", .75), (1, "#fff0a0", 0)], x, y - 20, 150 * sc, 150 * sc)
    s.append(f'<circle cx="{x:.1f}" cy="{y - 20:.1f}" r="{150 * sc:.1f}" fill="url(#{glow})"/>')
    for j in range(8):
        a = -math.pi / 2 + (j - 3.5) * .42
        r0, r1 = 84 * sc, (112 + 14 * math.sin(t * 8 + j)) * sc
        s.append(line([(x + r0 * math.cos(a), y - 24 + r0 * math.sin(a)), (x + r1 * math.cos(a), y - 24 + r1 * math.sin(a))], 7, INK, seed=2500 + j, taper=.4, wmin=.4))
    gl = [(x - 44 * sc, y - 24), (x - 36 * sc, y - 70 * sc), (x, y - 96 * sc), (x + 36 * sc, y - 70 * sc), (x + 44 * sc, y - 24), (x + 24 * sc, y + 8 * sc),
          (x - 24 * sc, y + 8 * sc)]
    s.append(shape(gl, "#ffe36b", blob([(x + 6 * sc, y - 94 * sc), (x + 36 * sc, y - 70 * sc), (x + 44 * sc, y - 24), (x + 24 * sc, y + 8 * sc), (x + 6 * sc, y)],
                                       "#f2b93a", .8) + blob(ellipse_pts(x - 14 * sc, y - 56 * sc, 9 * sc, 14 * sc, 8), "#fffbd8"), w=4.4, seed=2510))
    s.append(shape(rect_pts(x - 24 * sc, y + 6 * sc, x + 24 * sc, y + 34 * sc, 6), "#9aa0ac", line([(x - 20 * sc, y + 20 * sc), (x + 20 * sc, y + 20 * sc)], 2.4, INK,
                                                                                                   seed=2511, op=.7), w=4, seed=2512))
    return "".join(s)


def s12(t):
    understand = smooth(18.5, 19.1, t)
    smile = smooth(T_LUCHSHIJ - .05, T_LUCHSHIJ + .2, t)
    hip = (560.0, 1402.0)
    ank_n = (hip[0] + 192, 1580.0)
    ank_f = (hip[0] + 168, 1578.0)
    feet = {"n": (ank_n, .05), "f": (ank_f, .05)}
    # правая рука гладит кота: к его спине; дальняя на колене
    cat_x = 885
    cst = dict(look=(-.6, -.1), tilt=3 + 2 * osc(t, .4), blink=.8 + .2 * osc(t, .5) if smile < .5 else 1.0, tail=6 * osc(t, .7), flame_e=.9,
               smile=1.0 if smile > .5 else 0.0)
    pet = 16 * osc(t, 1.2)
    tgt = (cat_x - 52 + pet, SEAT_Y - 205 + 6)
    arms = {"n": ("ik", tgt, -1), "f": ("ang", .55, .55)}
    hands = {"n": dict(kind="open", flip=-1, dir=(.4, .9), curl=(.25, .3, .3, .35), spread=.15, thumb=.3), "f": dict(kind="open", flip=-1, dir=(.4, 1), curl=(.3, .35, .4, .45), spread=.1, thumb=.4)}
    ex = dict(lid=.35 + .55 * understand, look=(.5 + .1 * understand, .1 - .3 * understand), brows="tired" if understand < .35 else "up",
              mouth="flat" if smile < .2 else "grin", open=.3, smile=.5 + .5 * smile, closed=blink_at(t, 18.35, .18),
              blush=.4 * smile)
    d = dima(t, hip, lean=-.05 - .02 * understand, arms=arms, hands=hands, expr=ex, head_ang=.0 + .05 * understand - .03 * smile + .02 * osc(t, .3),
             feet=feet)
    hx, hy = d["head"]
    mode = "sunset"
    w = room_base(t, mode, (19, 5))
    b, f = sofa()
    cat = Cat.draw(cat_x, SEAT_Y + 6, .78, cst, t)
    lamp = floor_lamp(1.0)
    bu = bulb(hx - 30, hy - 250 - 6 * osc(t, 1.4), (t - 18.7) / .35, t)
    # тёплый свет лампы на диван
    u = ease_io(clamp((t - 17.9) / 2.8))
    ww = whip_in(t, 17.9, .2)
    hit = bump(t, T_LUCHSHIJ, .3)
    cam = (680 + 160 * ww - 30 * u, 1240 - 60 * u, 1.0 + .5 * u + .06 * hit, -.8 * (1 - u) + .6 * hit * osc(t, 7))
    body = w + lamp + b + layers(d, "", "") + cat + f
    # ноги Димы перед диваном: ближняя нога поверх сиденья — слои сидят до подлокотника; руку кладём поверх кота
    body = w + lamp + b + d.get("legs", "") + d["arm_f"] + d["body"] + cat + d["arm_n"] + f + bu
    return compose(body, cam, mode)


SHOTS = {"s01": s01, "s04": s04, "s05": s05, "s06": s06, "s12": s12}


def frame(sid, t):
    lib.DEFS.clear()
    return SHOTS[sid](t)
