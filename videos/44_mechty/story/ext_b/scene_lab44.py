"""Сцена study рилса 44, план s08 (14.65–17.6, клип 14.45–17.8): «Психолог Габриэле Эттинген много лет изучала».
Кабинет: исследовательница средних лет (тёмные волосы до плеч, очки, тёмно-зелёный жакет; просто героиня, не портрет)
сидит у стола боком к зрителю и пишет, перелистывает анкеты. На «много лет» (16.52–17.04) за окном быстро сменяются
день и ночь (ночью горит настольная лампа), стопки анкет на столе растут рывками, на стене — листок с графиком.
Человек — person.py рилса 27 (кисти из пяти пальцев), посадка — seat_person из scene_study рилса 27."""
import math

import numpy as np

import lib
import person
from c44 import kick, wt
from lib import (INK, W, H, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts,
                 shape, smooth, svg)

_ST = {}
T_PSY = wt("психолог")      # 14.827
T_MNOGO = wt("много")       # 16.52
T_LET = wt("лет")           # 16.88
T_IZ = wt("изучала")        # 17.08
FLOOR_Y, FEET_Y = 1250, 1268
TX0, TX1, TOP_B, TOP_F = 420, 1000, 1000, 1046
WALL, WALL_SH = "#e9e0cc", "#ddd1b8"
WOOD, WOOD_SH, WOOD_HI = "#9c6a44", "#7a4f30", "#b98557"
SPEC = dict(skin="#efc3a2", hair="bob", hair_c="#2e2421", top="#2f5a43", low="#2c3140", shoes="#3a2a22", face=.72, h=.95,
            sleeve="#2f5a43", collar="#f2ede2", brow_c="#2a1e1a", glasses=True)
SC_P = 0.95
FEET_X = 470
# дни-ночи на «много лет»: состояние меняется каждые DN секунд
DN0, DN = T_MNOGO - 0.02, 0.095
DN_END = T_IZ + 0.05


def night_at(t):
    if t < DN0 or t >= DN_END:
        return False
    return int((t - DN0) / DN) % 2 == 0


def n_cycles(t):
    return 0 if t < DN0 else int((min(t, DN_END) - DN0) / DN)


def ik(sh, tgt, L1=130, L2=120):
    dx, dy = tgt[0] - sh[0], tgt[1] - sh[1]
    L = max(abs(L1 - L2) + 1, min(L1 + L2 - 0.5, math.hypot(dx, dy)))
    base = math.degrees(math.atan2(dx, dy))
    c = clamp((L1 * L1 + L * L - L2 * L2) / (2 * L1 * L), -1, 1)
    d = math.degrees(math.acos(c))
    a1 = min((base - d, base + d), key=lambda a: abs(((a + 180) % 360) - 180))
    ex, ey = sh[0] + L1 * math.sin(math.radians(a1)), sh[1] + L1 * math.cos(math.radians(a1))
    a_f = math.degrees(math.atan2(tgt[0] - ex, tgt[1] - ey))
    return a1, a_f - a1


def seat_person(spec, k, feet_x, floor_y, sc, hands=None, pose=None, sd=0):
    pose = dict(pose or {})
    dr = 1 if spec["face"] >= 0 else -1
    S = sc * spec.get("h", 1.0)
    a1 = 90 * k
    pose["legs"] = {"L": (a1, a1), "R": (a1, a1)}
    foot_y = min(-20.0, -300 + 140 * math.cos(math.radians(a1)) + 140)
    ox = feet_x - dr * 140 * math.sin(math.radians(a1)) * S
    oy = floor_y - (foot_y + 22) * S
    if hands:
        sh_w = 74 * spec.get("bw", 1.0)
        shs = {"L": (-sh_w + 10, -502), "R": (sh_w - 10, -502)}
        arms = {}
        for side, tw in hands.items():
            tl = ((tw[0] - ox) / S, (tw[1] - oy) / S)
            a, b = ik(shs[side], tl)
            sign = -1 if side == "L" else 1
            arms[side] = (a - sign * 6, b)
        pose["arms"] = arms
        pose["near_front"] = True
    return person.draw(spec, pose, ox, oy, sc, sd=sd)


# ───────────────────────── комната
def outside(night):
    s = []
    if night:
        g = lin_grad([(0, "#141a3a", 1), (1, "#2e3a6a", 1)], 0, 330, 0, 820, units="userSpaceOnUse")
    else:
        g = lin_grad([(0, "#7fbde8", 1), (1, "#d6ecf6", 1)], 0, 330, 0, 820, units="userSpaceOnUse")
    s.append(f'<rect x="580" y="330" width="400" height="500" fill="url(#{g})"/>')
    if night:
        s.append(shape([(866, 400), (894, 418), (904, 450), (890, 482), (862, 494), (880, 466), (884, 440), (874, 414)], "#f4efd2", "", w=3, seed=801))
        rs = np.random.RandomState(4)
        for k in range(14):
            x, y = rs.uniform(600, 960), rs.uniform(350, 640)
            s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rs.uniform(2, 3.6))}" fill="#fff6c8"/>')
    else:
        s.append(shape(ellipse_pts(880, 430, 40, 40, 16), "#ffd84a", blob(ellipse_pts(890, 440, 26, 26, 12), "#f7c232", .8), w=3.4, seed=802))
        for k, (x, y, r) in enumerate([(680, 410, 30), (790, 470, 22)]):
            pts = [(x + 1.9 * r * (1 + .2 * math.sin(3 * a + k)) * math.cos(a), y + .7 * r * (1 + .2 * math.sin(3 * a + k)) * math.sin(a))
                   for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)]
            s.append(shape(pts, "#ffffff", "", w=2.6, seed=803 + k))
    # крыши и деревья кампуса
    for k, (x0, x1, top, col) in enumerate([(580, 700, 640, "#c98c6a"), (690, 830, 600, "#b9a17a"), (820, 990, 660, "#a7766a")]):
        c = mix(col, "#1d2040", .55) if night else col
        inner = ""
        for wy in range(top + 34, 830, 56):
            for wx in range(x0 + 18, x1 - 24, 40):
                lit = night and (wx * 7 + wy) % 3 == 0
                inner += blob(rect_pts(wx, wy, wx + 20, wy + 28), "#ffd56a" if lit else ("#2a3050" if night else "#e9eef2"))
        s.append(shape([(x0, top, 1), (x1, top, 1), (x1, 840, 1), (x0, 840, 1)], c, inner, w=3.4, seed=810 + k))
    tc = "#2f4a3a" if night else "#5f9e5a"
    s.append(shape(ellipse_pts(640, 700, 70, 80, 14, jitter=.08, seed=2), tc, "", w=3.4, seed=820))
    return "".join(s)


def window_frame():
    o = []
    X0, Y0, X1, Y1 = 600, 350, 960, 810
    fr = "#f3eee4"
    outer = [(X0 - 30, Y0 - 30, 1), (X1 + 30, Y0 - 30, 1), (X1 + 30, Y1 + 30, 1), (X0 - 30, Y1 + 30, 1)]
    hole = [(X0, Y0, 1), (X0, Y1, 1), (X1, Y1, 1), (X1, Y0, 1)]
    o.append(f'<path d="{lib.fill_d(outer) + lib.fill_d(hole)}" fill="{fr}" fill-rule="evenodd"/>')
    o.append(f'<path d="{lib.ink_closed(outer, 4.4, seed=831)}" fill="{INK}"/>')
    o.append(f'<path d="{lib.ink_closed(hole, 3.8, seed=832)}" fill="{INK}"/>')
    mx = (X0 + X1) / 2
    o.append(shape([(mx - 10, Y0, 1), (mx + 10, Y0, 1), (mx + 10, Y1, 1), (mx - 10, Y1, 1)], fr, "", w=3.2, seed=833))
    o.append(shape([(X0, 560, 1), (X1, 560, 1), (X1, 578, 1), (X0, 578, 1)], fr, "", w=3.2, seed=834))
    o.append(shape([(X0 - 50, Y1 + 30, 1), (X1 + 50, Y1 + 30, 1), (X1 + 60, Y1 + 60, 1), (X0 - 60, Y1 + 60, 1)], "#f6f1e8",
                   blob([(X0 - 60, Y1 + 50), (X1 + 60, Y1 + 50), (X1 + 60, Y1 + 60), (X0 - 60, Y1 + 60)], "#d8cfbf"), w=3.8, seed=835))
    return "".join(o)


def graph_sheet():
    """Листок с графиком на кнопке: оси, столбики и растущая кривая; без букв."""
    x0, y0, x1, y1 = 150, 420, 420, 700
    inner = line([(x0 + 40, y0 + 40), (x0 + 40, y1 - 40), (x1 - 30, y1 - 40)], 4, "#3a3330", taper=.1, wmin=.8, seed=841)
    for k, h in enumerate([50, 80, 70, 120, 150]):
        bx = x0 + 70 + k * 40
        inner += blob(rect_pts(bx, y1 - 42 - h, bx + 24, y1 - 42), ["#7fb2d9", "#7fb2d9", "#7fb2d9", "#e0a64a", "#e0a64a"][k])
    inner += line([(x0 + 60, y1 - 90), (x0 + 130, y1 - 110), (x0 + 190, y1 - 150), (x1 - 40, y1 - 220)], 5, "#d8433a", taper=.2, wmin=.6, seed=842)
    s = [blob(rect_pts(x0 + 14, y0 + 16, x1 + 16, y1 + 18), "#2a1608", .22, blur(8))]
    s.append(shape([(x0, y0, 1), (x1, y0 + 6, 1), (x1 - 4, y1, 1), (x0 + 4, y1 - 4, 1)], "#fbf9f2", inner, w=3.8, seed=843))
    s.append(shape(ellipse_pts((x0 + x1) / 2, y0 + 12, 12, 12, 12), "#d8433a", blob(ellipse_pts((x0 + x1) / 2 - 4, y0 + 8, 4, 3, 8), "#f7a08f"),
                   w=2.8, seed=844))
    return "".join(s)


def shelf():
    s = []
    y = 330
    s.append(shape(rect_pts(80, y, 460, y + 20), WOOD, blob(rect_pts(80, y + 12, 460, y + 20), WOOD_SH), w=3.4, seed=850))
    x = 100
    cols = ["#3f6f9a", "#c9554c", "#d9b14a", "#5f8f5a", "#7a5a9a", "#3f6f9a", "#d98a4a"]
    for k, c in enumerate(cols):
        w = 30 + (k * 7) % 14
        h = 120 + (k * 23) % 40
        s.append(shape(rect_pts(x, y - h, x + w, y), c, line([(x + 6, y - h + 20), (x + w - 6, y - h + 20)], 3, "#f2ead6", seed=851 + k, op=.8),
                       w=3, seed=860 + k))
        x += w + 4
    s.append(shape([(x + 10, y, 1), (x + 30, y - 130, 1), (x + 60, y - 128, 1), (x + 40, y, 1)], "#9a6a4a", "", w=3, seed=870))
    return "".join(s)


def room_static():
    s = [f'<rect x="-400" y="-400" width="{W + 800}" height="{FLOOR_Y + 400}" fill="{WALL}"/>']
    for k in range(-6, 22):
        s.append(f'<rect x="{k * 70}" y="-400" width="26" height="{FLOOR_Y + 160}" fill="{WALL_SH}" opacity=".45"/>')
    s.append(f'<rect x="-400" y="{FLOOR_Y - 220}" width="{W + 800}" height="220" fill="#c9d3c0"/>')
    s.append(shape(rect_pts(-400, FLOOR_Y - 234, W + 400, FLOOR_Y - 216), "#f7f1e4", "", w=3.2, seed=880))
    g = lin_grad([(0, "#8e6446", 1), (1, "#a8784f", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-400" y="{FLOOR_Y}" width="{W + 800}" height="{H}" fill="url(#{g})"/>')
    for i, y in enumerate([1290, 1350, 1430, 1540, 1690]):
        s.append(line([(-400, y), (W + 400, y)], 2.6, "#6f4a30", taper=.05, wmin=.9, seed=881 + i, op=.8))
    s.append(shape(rect_pts(-400, FLOOR_Y - 20, W + 400, FLOOR_Y + 4), "#f7f1e4", "", w=3.2, seed=890))
    s.append(shelf())
    s.append(graph_sheet())
    return "".join(s)


def chair():
    s = []
    seat_y, xb, xf = 1124, FEET_X - 140 * SC_P * .95 - 70, FEET_X - 140 * SC_P * .95 + 92
    col, sh = "#4a5a6a", "#34404c"
    for k, lx in enumerate((xb, xf)):
        s.append(shape(rect_pts(lx - 8, seat_y + 10, lx + 16, FEET_Y), sh, "", w=3.2, seed=900 + k))
    s.append(shape(rect_pts(xb - 10, seat_y - 320, xb + 10, seat_y + 12), col, "", w=3.4, seed=903))
    s.append(shape(rect_pts(xb - 16, seat_y - 330, xb + 30, seat_y - 180, 10), col, blob(rect_pts(xb + 10, seat_y - 330, xb + 30, seat_y - 180), sh, .8),
                   w=3.4, seed=904))
    s.append(shape(rect_pts(xb - 14, seat_y, xf + 14, seat_y + 22), col, blob(rect_pts(xb - 14, seat_y + 12, xf + 14, seat_y + 22), sh), w=3.6, seed=905))
    return "".join(s)


def table_back():
    return "".join(shape(rect_pts(x - 10, TOP_F, x + 10, FLOOR_Y + 6), WOOD_SH, "", w=3.2, seed=910 + k) for k, x in enumerate((TX0 + 40, TX1 - 40)))


def table_top():
    top = [(TX0 + 20, TOP_B, 1), (TX1 - 20, TOP_B, 1), (TX1, TOP_F, 1), (TX0, TOP_F, 1)]
    inner = blob([(TX0 + 20, TOP_B), (TX1 - 20, TOP_B), (TX1 - 8, TOP_B + 18), (TX0 + 10, TOP_B + 18)], WOOD_HI, .7)
    s = [shape(top, WOOD, inner, w=4.2, seed=915)]
    s.append(shape(rect_pts(TX0, TOP_F, TX1, TOP_F + 26), WOOD_SH, "", w=3.8, seed=916))
    # тумба с ящиками справа
    s.append(shape(rect_pts(TX1 - 200, TOP_F + 26, TX1 - 10, FEET_Y), WOOD, "".join(
        shape(rect_pts(TX1 - 186, TOP_F + 40 + k * 66, TX1 - 24, TOP_F + 96 + k * 66, 4), WOOD_HI,
              blob(ellipse_pts(TX1 - 105, TOP_F + 68 + k * 66, 14, 5, 8), "#5a3a22"), w=2.6, seed=917 + k) for k in range(3)), w=3.8, seed=920))
    s.append(shape(rect_pts(TX0 + 8, TOP_F + 26, TX0 + 30, FEET_Y), WOOD, "", w=3.4, seed=921))
    return "".join(s)


def stack(x, n, sd, lean=0.0):
    """Стопка анкет: n листков, у верхних строчки; x — центр, низ на столешнице."""
    s = []
    y = TOP_B + 16
    rs = np.random.RandomState(sd)
    for i in range(n):
        dx = rs.uniform(-5, 5) + lean * i
        yy = y - i * 9
        s.append(shape([(x - 70 + dx, yy - 9, 1), (x + 70 + dx, yy - 9, 1), (x + 72 + dx, yy, 1), (x - 68 + dx, yy, 1)],
                       "#fbf9f2" if i % 3 else "#f1ece0", "", w=2.2, seed=sd + i))
    if n:
        top = y - (n - 1) * 9 - 9
        for k in range(3):
            s.append(line([(x - 52, top - 2 + 0 * k), (x + 40 - k * 10, top - 2)], 1, "#9aa", seed=sd + 90 + k, op=0) if False else "")
        _ = top
    return "".join(s)


def lamp(on):
    s = []
    bx, by = 990, TOP_B + 14
    if on:
        g = rad_grad([(0, "#fff0b0", .7), (.5, "#ffd98a", .25), (1, "#ffd98a", 0)], 820, 960, 420, 300)
        s.append(f'<rect x="300" y="600" width="1100" height="700" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(shape(ellipse_pts(bx, by - 6, 54, 12, 14), "#2f5a43", "", w=3.2, seed=930))
    s.append(line([(bx, by - 10), (bx - 20, by - 150), (bx - 90, by - 210)], 12, "#2f5a43", taper=.05, wmin=.9, seed=931))
    shade_pts = [(bx - 70, by - 250, 1), (bx - 150, by - 160, 1), (bx - 40, by - 150, 1)]
    s.append(shape(shade_pts, "#2f5a43", blob([(bx - 150, by - 160), (bx - 40, by - 150), (bx - 60, by - 170)], "#1f3c2c", .9), w=3.6, seed=932))
    s.append(shape(ellipse_pts(bx - 96, by - 154, 30, 8, 12, rot=6), "#fff3c0" if on else "#d9d2b8", "", w=2.6, seed=933))
    return "".join(s)


def write_hand(t):
    """Правая кисть пишет: мелкие строки по листку перед ней."""
    ph = (t * 1.6) % 1.0
    x = 530 + 60 * ph + 3 * math.sin(t * 23)
    y = TOP_B + 6 - 4 * abs(math.sin(t * 11))
    return x, y


def frame08(t):
    night = night_at(t)
    s = [_ST["room"], f'<g clip-path="url(#{_ST["wclip"]})">{_ST["out_n" if night else "out_d"]}</g>', _ST["wframe"]]
    if night:
        s.append(f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" fill="#1c2346" opacity=".22"/>')
    s.append(chair())
    s.append(table_back())
    # руки: левая придерживает листок, правая пишет
    hr = write_hand(t)
    hl = (500 + 2 * math.sin(t * 1.3), TOP_B + 12)
    look = (0.75, 0.55) if t < T_MNOGO - 0.3 or t > T_IZ + 0.25 else (0.95, -0.25)
    pose = dict(look=look, mouth="flat", blink=1.0 if (t % 2.9) < 0.09 else 0.0,
                head_tilt=4 + 2 * math.sin(t * 1.7), brow=.15, hmode={"L": "rest", "R": "grip"})
    if t > T_LET - 0.05 and t < T_IZ + 0.4:
        pose["mouth"] = "o"
        pose["brow"] = .5
    body = seat_person(SPEC, 1.0, FEET_X, FEET_Y, SC_P, {"L": hl, "R": hr}, pose, sd=3000)
    s.append(table_top())
    # стопки анкет растут рывком на каждой смене дня и ночи
    n = n_cycles(t)
    for k, (x, base, grow) in enumerate([(740, 4, 3), (830, 3, 4), (680, 2, 2)]):
        cnt = base + grow * n
        if k == 2:
            cnt = base + (grow * n if n > 2 else 0)
        st = stack(x, cnt, 950 + k * 40, lean=.4 * (k - 1))
        bump = 0.0
        if n > 0 and t < DN_END + .2:
            q = (t - DN0) % DN
            bump = 6 * math.exp(-q * 30)
        s.append(f'<g transform="translate(0 {f(-bump)})">{st}</g>')
    # листок под рукой и ручка
    s.append(shape([(490, TOP_B + 4, 1), (620, TOP_B + 2, 1), (630, TOP_B + 16, 1), (482, TOP_B + 18, 1)], "#fbf9f2", "", w=2.4, seed=960))
    s.append(lamp(night))
    s.append(body)
    # ручка в правой кисти
    px, py = hr
    s.append(line([(px + 6, py - 4), (px + 40, py - 52)], 7, "#2f5fb0", taper=.1, wmin=.8, seed=961))
    return "".join(s)


def cam08(t):
    u = clamp((t - 14.45) / 3.35)
    k, rot = kick(t, [T_MNOGO], 0.03, 10)
    sc = 1.30 + 0.12 * ease_io(u)
    return cam(610 + 30 * u, 840 + 10 * u, sc * k, rot - 0.6 + 1.0 * u)


def frame(sid, t):
    if not _ST:
        lib.DEFS.clear()
        _ST["room"] = room_static()
        _ST["out_d"] = outside(False)
        _ST["out_n"] = outside(True)
        _ST["wclip"] = lib.clip_rect(600, 350, 360, 460)
        _ST["wframe"] = window_frame()
        lib.static_done()
    lib.dyn_begin()
    return svg(f'<rect width="{W}" height="{H}" fill="{WALL}"/><g transform="{cam08(t)}">{frame08(t)}</g>')


_ = (ease_out, smooth)
