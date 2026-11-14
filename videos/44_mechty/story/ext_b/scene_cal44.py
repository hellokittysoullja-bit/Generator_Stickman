"""Сцена calendar рилса 44, план s03 (3.75–5.2, клип 3.55–5.4): «Мечтает уже три года».
Вечер, стена у дивана Димы: слева окно, справа отрывной календарь. Листки срываются пачками и улетают кувырком, за окном
быстро сменяются времена года (зима → весна в цвету → лето → осень, по кругу). На «три» (4.52) поверх слетающих листков
шлёпается крупная красная рукописная «3» (удар камерой, тряска), на «года» (4.72) дописывается «года». Окно после удара
остаётся зимним, идёт снег. Основа листа и стены — calbase рилса 40, полёт листа — scene_calendar рилса 26."""
import math

import numpy as np

import calbase
import lib
import props
from c44 import hand_text, kick, shake, wt
from lib import (INK, W, H, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad,
                 rect_pts, shape, svg)

_ST = {}
T_TRI = wt("три")          # 4.52
T_GODA = wt("года")        # 4.72
PAPER, PAPER_SH, BACK = "#fbf8f0", "#e6dccb", "#e9e2d4"
RED, RED_SH = "#d8433a", "#a92f29"
PX0, PX1, PTOP, PBOT = 590, 970, 520, 1060      # лист отрывного календаря
PCX = (PX0 + PX1) / 2
WX0, WX1, WY0, WY1 = 70, 470, 400, 1000         # окно
SOFA_Y = 1210

# пачки срывов: (время, сторона); листки летят влево (над окном) и вправо
TEARS = []
_rs = np.random.RandomState(44)
for b, tb in enumerate([3.26, 3.46, 3.66, 3.86, 4.06, 4.26, 4.42]):
    for j in range(4 if b < 6 else 3):
        TEARS.append((tb + j * 0.034 + _rs.uniform(0, .01), -1 if (b + j) % 3 else 1, _rs.uniform(.8, 1.25), _rs.uniform(-1, 1)))
FLY = 0.62
DAY0 = 9


def day_of(i):
    return (DAY0 + i - 1) % 31 + 1


# ───────────────────────────── окно и сезоны
SEASONS = ["winter", "spring", "summer", "autumn"]
SEASON_T0, SEASON_DT = 3.30, 0.105


def season_at(t):
    if t >= T_TRI:
        return "winter"
    k = int(math.floor((t - SEASON_T0) / SEASON_DT))
    return SEASONS[k % 4] if k >= 0 else "autumn"


def outside(season):
    sky = {"winter": ("#b9c6d6", "#e4e8ee"), "spring": ("#8fc4ee", "#dff0f7"), "summer": ("#5fb0ea", "#cfeaf8"),
           "autumn": ("#e6b98a", "#f5dcc0")}[season]
    ground = {"winter": "#f4f6fa", "spring": "#9fd07e", "summer": "#6fb85a", "autumn": "#c9a05a"}[season]
    o = []
    g = lin_grad([(0, sky[0], 1), (1, sky[1], 1)], 0, WY0, 0, WY1, units="userSpaceOnUse")
    o.append(f'<rect x="{WX0 - 20}" y="{WY0 - 20}" width="{WX1 - WX0 + 40}" height="{WY1 - WY0 + 40}" fill="url(#{g})"/>')
    if season == "summer":
        o.append(shape(ellipse_pts(390, 500, 46, 46, 16), "#ffd84a", blob(ellipse_pts(402, 512, 30, 30, 12), "#f7c232", .8), w=3.6, seed=5101))
    # дома вдали
    rs = np.random.RandomState(11)
    for k, (x0, x1, top) in enumerate([(40, 170, 760), (160, 300, 720), (290, 420, 780), (410, 520, 740)]):
        col = ["#c98c6a", "#a7b3c4", "#d9b77a", "#b98a8a"][k]
        inner = blob(rect_pts(x0 + (x1 - x0) * .6, top, x1 + 10, 1000), lib.mul(col, (.82, .8, .86)), .9)
        for wy in range(top + 40, 900, 70):
            for wx in range(x0 + 22, x1 - 30, 46):
                inner += blob(rect_pts(wx, wy, wx + 22, wy + 30), "#f3e3b0" if (wx + wy) % 3 else "#6d7a8c")
        o.append(shape([(x0, top, 1), (x1, top, 1), (x1, 1010, 1), (x0, 1010, 1)], col, inner, w=3.4, seed=5110 + k))
        roof = [(x0 - 10, top + 2, 1), ((x0 + x1) / 2, top - 56, 1), (x1 + 10, top + 2, 1)]
        o.append(shape(roof, "#f6f8fb" if season == "winter" else "#7a4a3a", "", w=3.4, seed=5120 + k))
    _ = rs
    o.append(shape([(WX0 - 30, 900, 1), (WX1 + 30, 880, 1), (WX1 + 30, 1030, 1), (WX0 - 30, 1030, 1)], ground,
                   blob([(WX0 - 30, 960), (WX1 + 30, 950), (WX1 + 30, 1030), (WX0 - 30, 1030)], lib.mul(ground, (.9, .9, .94)), .8), w=3.4, seed=5130))
    # дерево
    tx, ty = 220, 930
    trunk = [(tx - 18, ty, 1), (tx - 12, ty - 170), (tx - 40, ty - 270), (tx - 30, ty - 278), (tx - 2, ty - 200), (tx + 8, ty - 300),
             (tx + 20, ty - 296), (tx + 14, ty - 190), (tx + 50, ty - 250), (tx + 58, ty - 240), (tx + 18, ty - 160), (tx + 20, ty, 1)]
    o.append(shape(trunk, "#6b4a35", blob([(tx + 4, ty), (tx + 14, ty - 190), (tx + 20, ty)], "#4f3526", .8), w=4, seed=5140))
    crown = {"spring": ("#f4b6c8", "#e48aa6"), "summer": ("#5fae4f", "#3f8a3a"), "autumn": ("#ec8a2e", "#c9601e")}.get(season)
    if crown:
        for k, (dx, dy, r) in enumerate([(-70, -280, 78), (40, -320, 86), (-10, -380, 74), (90, -250, 66), (-110, -210, 58)]):
            o.append(shape(ellipse_pts(tx + dx, ty + dy, r, r * .86, 14, jitter=.06, seed=k), crown[0],
                           blob(ellipse_pts(tx + dx + r * .3, ty + dy + r * .3, r * .7, r * .5, 12), crown[1], .85), w=4, seed=5150 + k))
    else:
        for k, (a, b) in enumerate([((tx - 40, ty - 270), (tx - 70, ty - 320)), ((tx + 8, ty - 300), (tx + 4, ty - 360)),
                                    ((tx + 50, ty - 250), (tx + 90, ty - 290))]):
            o.append(line([a, b], 9, "#6b4a35", taper=.6, seed=5160 + k))
            o.append(line([(a[0] - 4, a[1] - 6), (b[0] - 2, b[1] - 6)], 6, "#f8fafc", taper=.6, seed=5170 + k))
        o.append(blob(ellipse_pts(tx + 10, ty - 196, 14, 6, 10), "#f8fafc"))
    return "".join(o)


def particles(season, t):
    o = []
    rs = np.random.RandomState({"winter": 1, "spring": 2, "summer": 3, "autumn": 4}[season])
    if season == "summer":
        return ""
    n = 26 if season == "winter" else 14
    for k in range(n):
        x0, sp, ph = rs.uniform(WX0 - 20, WX1 + 20), rs.uniform(120, 220), rs.uniform(0, 1)
        y = WY0 - 30 + ((ph * (WY1 - WY0 + 60) + sp * t) % (WY1 - WY0 + 60))
        x = x0 + 24 * math.sin(t * 2.2 + k)
        if season == "winter":
            r = rs.uniform(5, 9)
            o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#ffffff"/>')
        else:
            col = "#f7c3d3" if season == "spring" else rs.choice(["#e8792a", "#d9541e", "#f0a93a"])
            a = t * 220 + k * 40
            o.append(shape(ellipse_pts(x, y, 13, 7, 8, rot=a), col, "", w=2.2, seed=5200 + k))
    return "".join(o)


def window_frame():
    o = []
    fr = "#f1ece2"
    outer = [(WX0 - 34, WY0 - 34, 1), (WX1 + 34, WY0 - 34, 1), (WX1 + 34, WY1 + 34, 1), (WX0 - 34, WY1 + 34, 1)]
    hole = [(WX0, WY0, 1), (WX0, WY1, 1), (WX1, WY1, 1), (WX1, WY0, 1)]
    d = lib.fill_d(outer) + lib.fill_d(hole)
    o.append(f'<path d="{d}" fill="{fr}" fill-rule="evenodd"/>')
    o.append(f'<path d="{lib.ink_closed(outer, 4.6, seed=5301)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_closed(hole, 4.0, seed=5302)}" fill="{INK}"/>')
    o.append(blob([(WX1, WY0), (WX1 + 34, WY0 - 34), (WX1 + 34, WY1 + 34), (WX1, WY1)], "#d9d1c2", .9))
    mx, my = (WX0 + WX1) / 2, WY0 + (WY1 - WY0) * .42
    o.append(shape([(mx - 11, WY0, 1), (mx + 11, WY0, 1), (mx + 11, WY1, 1), (mx - 11, WY1, 1)], fr, "", w=3.4, seed=5303))
    o.append(shape([(WX0, my - 11, 1), (WX1, my - 11, 1), (WX1, my + 11, 1), (WX0, my + 11, 1)], fr, "", w=3.4, seed=5304))
    # блик на стекле
    o.append(line([(WX0 + 40, WY0 + 120), (WX0 + 120, WY0 + 40)], 10, "#ffffff", taper=.4, seed=5305, op=.55))
    # подоконник
    o.append(shape([(WX0 - 60, WY1 + 34, 1), (WX1 + 60, WY1 + 34, 1), (WX1 + 70, WY1 + 70, 1), (WX0 - 70, WY1 + 70, 1)], "#f6f1e8",
                   blob([(WX0 - 70, WY1 + 58), (WX1 + 70, WY1 + 58), (WX1 + 70, WY1 + 70), (WX0 - 70, WY1 + 70)], "#d8cfbf"), w=4, seed=5306))
    # горшок с кактусом на подоконнике
    px, py = WX1 - 70, WY1 + 34
    o.append(shape([(px - 20, py - 60), (px - 16, py - 120), (px, py - 136), (px + 16, py - 120), (px + 20, py - 60)], "#5f9e5a",
                   line([(px, py - 128), (px, py - 64)], 3, "#3f7a3c", seed=5307), w=3.4, seed=5308))
    o.append(shape([(px - 34, py - 64, 1), (px + 34, py - 64, 1), (px + 26, py, 1), (px - 26, py, 1)], "#c96b4a",
                   blob([(px + 6, py - 64), (px + 34, py - 64), (px + 26, py), (px + 6, py)], "#a3533a", .8), w=3.6, seed=5309))
    return "".join(o)


# ───────────────────────────── календарь
def sheet_front(d):
    s = []
    inner = blob(rect_pts(PX0 - 10, PTOP - 10, PX1 + 10, PTOP + 86), RED)
    inner += blob(rect_pts(PX0 - 10, PTOP + 70, PX1 + 10, PTOP + 86), RED_SH)
    g = _ST["pgrad"]
    inner += f'<rect x="{PX0}" y="{PTOP + 86}" width="{PX1 - PX0}" height="{PBOT - PTOP}" fill="url(#{g})"/>'
    col = "#c9554c" if d % 7 == 0 else "#2e2a2c"
    inner += (f'<text x="{f(PCX)}" y="{f(PTOP + 370)}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="250" '
              f'fill="{col}">{d}</text>')
    inner += line([(PX0 + 70, PTOP + 430), (PX1 - 70, PTOP + 430)], 3, "#cdbfa6", taper=.05, wmin=.9, seed=5400 + d)
    for k in range(3):
        inner += line([(PX0 + 90, PTOP + 470 + k * 18), (PX1 - 90 - 40 * (k == 2), PTOP + 470 + k * 18)], 2.4, "#ddd2bf", taper=.05,
                      wmin=.9, seed=5410 + k)
    s.append(shape([(PX0, PTOP, 1), (PX1, PTOP, 1), (PX1, PBOT, 1), (PX0, PBOT, 1)], PAPER, inner, w=4.2, seed=5420 + d))
    return "".join(s)


def sheet_back():
    inner = blob(rect_pts(PX0 - 10, PTOP + 300, PX1 + 10, PBOT + 10), "#ded5c4", .7)
    return shape([(PX0, PTOP, 1), (PX1, PTOP, 1), (PX1, PBOT, 1), (PX0, PBOT, 1)], BACK, inner, w=4.2, seed=5450)


def board():
    s = []
    s.append(line([(PCX, 300), (PX0 + 40, 440)], 4, "#6b5a46", taper=.1, wmin=.8, seed=5501))
    s.append(line([(PCX, 300), (PX1 - 40, 440)], 4, "#6b5a46", taper=.1, wmin=.8, seed=5502))
    s.append(shape(ellipse_pts(PCX, 296, 13, 13, 12), "#8b8f97", blob(ellipse_pts(PCX - 4, 292, 5, 4, 8), "#d4d8de"), w=3.2, seed=5503))
    inner = blob(rect_pts(PX0 - 40, 500, PX1 + 40, 540), "#4c2a24")
    inner += line([(PX0 - 10, 452), (PX1 + 10, 452)], 4, "#a5584c", taper=.1, wmin=.8, seed=5504, op=.8)
    s.append(shape([(PX0 - 26, 430, 1), (PX1 + 26, 430, 1), (PX1 + 26, 532, 1), (PX0 - 26, 532, 1)], "#7a332d", inner, w=4.6, seed=5505))
    # два металлических зажима
    for k, x in enumerate((PX0 + 70, PX1 - 70)):
        s.append(shape(rect_pts(x - 22, 506, x + 22, 548, 6), "#9aa0aa", blob(rect_pts(x - 22, 530, x + 22, 548), "#6e7480"), w=3, seed=5506 + k))
    return "".join(s)


def pad_edges():
    """Толщина стопки листков снизу и сбоку."""
    s = [blob([(PX0 + 10, PBOT - 4, 1), (PX1 + 8, PBOT - 4, 1), (PX1 + 12, PBOT + 26, 1), (PX0 + 14, PBOT + 24, 1)], "#2a1608", .3, blur(8))]
    pts = [(PX0 + 4, PBOT - 6, 1), (PX1 + 8, PBOT - 6, 1), (PX1 + 8, PBOT + 14, 1), (PX0 + 6, PBOT + 14, 1)]
    inner = "".join(line([(PX0, PBOT - 1 + k * 5), (PX1 + 10, PBOT - 1 + k * 5)], 1.6, "#bfb3a0", taper=.05, wmin=.9, seed=5520 + k) for k in range(3))
    s.append(shape(pts, "#ede5d6", inner, w=3.4, seed=5530))
    s.append(shape([(PX1, PTOP + 40, 1), (PX1 + 8, PTOP + 46, 1), (PX1 + 8, PBOT + 14, 1), (PX1, PBOT, 1)], "#e2d8c6", "", w=2.6, seed=5531))
    return "".join(s)


def tear_xf(t, t0, side, vk, wob):
    e = t - t0
    if e < 0:
        return None, 1.0
    if e > FLY:
        return "gone", 1.0
    peel = ease_in(clamp(e / 0.07), 1.4)
    q = max(0.0, e - 0.05)
    # отрыв: лист загибается вверх вокруг верхнего края (cos), дальше кувыркается в полёте
    phi = math.radians(70 * peel) + q * (9.0 + 3 * wob) * vk
    sy = math.cos(phi)
    dx = side * (520 * vk * q + 120 * q * q * 8) + wob * 40 * q
    dy = -760 * q + 0.5 * 4200 * q * q - 30 * peel
    rot = side * (-10 * peel - 260 * q * vk) + wob * 30 * q
    xf = (f"translate({f(PCX + dx)} {f(PTOP + dy)}) rotate({f(rot)}) scale(1 {f(sy)}) translate({f(-PCX)} {-PTOP})")
    return xf, sy


def n_torn(t):
    return sum(1 for (t0, *_r) in TEARS if t >= t0 + 0.035)


def calendar(t):
    s = [blob([(PX0 + 34, 440, 1), (PX1 + 40, 450, 1), (PX1 + 46, PBOT + 44, 1), (PX0 + 40, PBOT + 40, 1)], "#1d2412", .34, blur(16))]
    s.append(board())
    s.append(pad_edges())
    n = n_torn(t)
    # верхний неподвижный лист — следующий день; под летящими
    s.append(_ST["front"][day_of(n + 1)] if (n + 1) in range(1, 999) else "")
    return "".join(s)


def flying(t):
    s = []
    for i in reversed(range(len(TEARS))):
        t0, side, vk, wob = TEARS[i]
        xf, sy = tear_xf(t, t0, side, vk, wob)
        if xf is None or xf == "gone":
            continue
        body = _ST["front"][day_of(i + 1)] if sy > 0 else _ST["back"]
        s.append(f'<g transform="{xf}">{body}</g>')
    return "".join(s)


def sofa():
    s = []
    col, sh = "#7a2f35", "#5a2027"
    back = [(-200, SOFA_Y + 40), (-120, SOFA_Y - 10), (300, SOFA_Y - 24), (760, SOFA_Y - 22), (1200, SOFA_Y - 6), (1300, SOFA_Y + 60, 1),
            (1300, 2400, 1), (-200, 2400, 1)]
    inner = blob([(-200, SOFA_Y + 60), (1300, SOFA_Y + 70), (1300, 2400), (-200, 2400)], sh, .7)
    inner += line([(-100, SOFA_Y + 26), (500, SOFA_Y + 10), (1200, SOFA_Y + 24)], 5, "#9a454a", taper=.3, seed=5601, op=.8)
    inner += line([(540, SOFA_Y + 60), (550, SOFA_Y + 300)], 4, "#4a1820", taper=.4, seed=5602, op=.8)
    s.append(shape(back, col, inner, w=5.2, seed=5603))
    # плед, свисающий со спинки
    plaid = [(700, SOFA_Y - 14), (900, SOFA_Y - 20), (1010, SOFA_Y - 6), (1000, SOFA_Y + 150), (960, SOFA_Y + 210), (900, SOFA_Y + 170),
             (820, SOFA_Y + 220), (760, SOFA_Y + 160), (690, SOFA_Y + 120)]
    pin = "".join(line([(700 + k * 60, SOFA_Y - 30), (690 + k * 60, SOFA_Y + 230)], 9, "#2f6a4a", taper=.05, wmin=.9, seed=5610 + k, op=.8) for k in range(6))
    pin += "".join(line([(660, SOFA_Y + 20 + k * 60), (1040, SOFA_Y + 14 + k * 60)], 7, "#c9b46a", taper=.05, wmin=.9, seed=5620 + k, op=.7) for k in range(4))
    s.append(shape(plaid, "#4f8f63", pin, w=4.6, seed=5630))
    return "".join(s)


def wall():
    s = [calbase.wallpaper()]
    # тёплый свет торшера справа-сверху
    g = rad_grad([(0, "#ffe7b0", .5), (1, "#ffe7b0", 0)], 900, 300, 700, 700)
    s.append(f'<rect x="-600" y="-600" width="2400" height="2800" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(blob([(WX0 - 4, WY0 - 4, 1), (WX1 + 60, WY0 + 10, 1), (WX1 + 70, WY1 + 90, 1), (WX0 + 10, WY1 + 80, 1)], "#1d2412", .3, blur(14)))
    return "".join(s)


# ───────────────────────────── «3 года»
def three(t):
    e = t - (T_TRI - 0.07)
    if e < 0:
        return ""
    s = []
    if e < 0.07:
        u = ease_in(e / 0.07, 1.6)
        k = 2.6 - 1.6 * u
        sqx, sqy = 1, 1
    else:
        q = e - 0.07
        k = 1.0
        sq = 0.16 * math.exp(-q * 11) * math.cos(q * 26)
        sqx, sqy = 1 + sq, 1 - sq
    x, y = 440, 930
    rot = -7 + 4 * math.exp(-max(0, e - .07) * 8)
    g = (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(k * sqx)} {f(k * sqy)})">'
         + hand_text(0, 0, "3", 640, "#e0352b", "#fbf3e2", 46, weight=700)
         + hand_text(0, 0, "3", 640, "#e0352b", INK, 12, weight=700) + "</g>")
    s.append(f'<g transform="translate(14 18)" opacity=".28" {blur(10)}>' + hand_text(x, y, "3", 640, "#1d2412", weight=700, rot=rot) + "</g>")
    s.append(g)
    # удар: лучики и пыль вокруг
    if 0.07 <= e < 0.45:
        u = clamp((e - 0.07) / 0.36)
        s.append(props.burst(x - 10, y - 230, 2.2, u, seed=5701, color=INK, n=9, r0=95, r1=150))
    # «года» — дописывается слева направо
    w = clamp((t - T_GODA + 0.02) / 0.38)
    if w > 0:
        gx, gy = 610, 1060
        c = lib.clip_rect(gx - 30, gy - 230, 30 + 400 * ease_io(w), 320)
        txt = (hand_text(gx, gy, "года", 230, "#2a2230", "#fbf3e2", 30, anchor="start", rot=-6)
               + hand_text(gx, gy, "года", 230, "#2a2230", anchor="start", rot=-6))
        s.append(f'<g clip-path="url(#{c})">{txt}</g>')
    return "".join(s)


def frame03(t):
    s = [_ST["wall"], f'<g clip-path="url(#{_ST["wclip"]})">{_ST["out"][season_at(t)]}{particles(season_at(t), t)}</g>', _ST["wframe"]]
    s.append(calendar(t))
    s.append(_ST["sofa"])
    s.append(flying(t))
    s.append(three(t))
    return "".join(s)


def cam03(t):
    u = ease_io(clamp((t - 3.55) / 1.85))
    sc = 1.03 + 0.07 * u
    cx = 600 - 50 * u + 6 * math.sin(t * 1.6)
    cy = 800 + 30 * u
    k, rot = kick(t, [T_TRI], 0.07, 9)
    dx, dy = shake(t, T_TRI, 16, 8, 60)
    k2, r2 = kick(t, [T_GODA + 0.05], 0.015, 12)
    return cam(cx + dx, cy + dy, sc * k * k2, rot + r2 + 1.2 - 2.0 * u)


def frame(sid, t):
    if not _ST:
        lib.DEFS.clear()
        _ST["pgrad"] = lin_grad([(0, "#ffffff", 0), (1, "#d6c7a8", .3)], 0, 0, 0, 1)
        _ST["wall"] = wall()
        _ST["out"] = {s: outside(s) for s in SEASONS}
        _ST["wclip"] = lib.clip_rect(WX0, WY0, WX1 - WX0, WY1 - WY0)
        _ST["wframe"] = window_frame()
        _ST["front"] = {d: sheet_front(d) for d in range(1, 32)}
        _ST["back"] = sheet_back()
        _ST["sofa"] = sofa()
        lib.static_done()
    lib.dyn_begin()
    return svg(f'<rect width="{W}" height="{H}" fill="#9fae8e"/><g transform="{cam03(t)}">{frame03(t)}</g>')


_ = (H, ease_out, mix)
