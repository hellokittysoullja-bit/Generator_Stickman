"""Сцена rows рилса 26 (s12, 20.08–24.12): итог британского опыта. Два ряда по 10 человечков в спортивной форме на
беговых дорожках; слева у ряда значок: сверху листок со строчками (дописали «когда и где»), снизу пустой листок.
Все разминаются на месте с первого кадра (серые). Верхний ряд: на «девять из десяти» (20.88–21.48) по очереди
загораются зелёным 9 из 10 (каждый подпрыгивает, вскидывает руки), один остаётся серым. Нижний: на «трети» (23.2)
загораются только 3. Без букв и цифр."""
import math

import lib
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, rad_grad,
                 rect_pts, shape, smooth, svg)

_ST = {}
ROW_Y = [820, 1230]           # линия ступней рядов
X0, DX = 232, 86
TOP_ON = [20.88 + k * (0.60 / 8) for k in range(9)]       # 9 из 10, по очереди
TOP_IDX = [0, 1, 2, 3, 4, 5, 7, 8, 9]                       # шестой (5-й с нуля... 6) остаётся серым
BOT_ON = {1: 23.20, 5: 23.27, 8: 23.34}

GREY, GREY_SH, GREY_LO = "#b9c1cd", "#9aa3b2", "#8a93a3"
GREEN, GREEN_SH, GREEN_LO = "#3cbf63", "#279a4a", "#1f6e3a"
SKIN_SET = ["#f2c9a8", "#c98e6a", "#e8b896", "#8a5a3c", "#f0c4a0", "#d9a07a", "#f4d0b4", "#a8704c", "#e9c0a0", "#c99470"]
HAIR_SET = ["#3a2418", "#2a1a14", "#c8622a", "#5a3a26", "#e0b050", "#1a1210", "#6a4a30", "#2a1a14", "#9a9aa6", "#3a2a22"]


def background():
    s = []
    lin_grad([(0, "#eef3f6", 1), (1, "#d9e4ea", 1)], 0, 0, 0, 1, gid="gBgR")
    s.append(f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" fill="url(#gBgR)"/>')
    g = rad_grad([(0, "#fff6e0", .8), (1, "#fff6e0", 0)], 300, 300, 900, 700)
    s.append(f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" fill="url(#{g})"/>')
    # две беговые дорожки
    for k, y in enumerate(ROW_Y):
        tr = [(-200, y - 26, 1), (W + 200, y - 26, 1), (W + 200, y + 62, 1), (-200, y + 62, 1)]
        inner = blob([(-200, y + 30), (W + 200, y + 30), (W + 200, y + 62), (-200, y + 62)], "#a8483a", .8)
        inner += line([(-200, y - 8), (W + 200, y - 8)], 4, "#f6efe6", taper=.02, wmin=.95, seed=20 + k, op=.95)
        inner += line([(-200, y + 46), (W + 200, y + 46)], 4, "#f6efe6", taper=.02, wmin=.95, seed=22 + k, op=.95)
        s.append(shape(tr, "#c45a46", inner, w=4.4, seed=24 + k))
    return "".join(s)


def icon_sheet(x, y, written, sd):
    """Значок-листок 120×156 (центр x, y). written — три волнистые синие строчки и галочка; иначе пустой."""
    s = []
    s.append(blob(rect_pts(x - 52, y - 70, x + 72, y + 92, 8), "#5a6a7a", .25, blur(6)))
    inner = ""
    if written:
        for k in range(3):
            yy = y - 36 + k * 34
            pts = [(x - 40 + j * 8, yy + 4 * math.sin(j * 1.3 + k)) for j in range(10 if k < 2 else 7)]
            inner += line(pts, 5, "#2d55a8", taper=.3, wmin=.5, seed=sd + k)
        inner += line([(x + 14, y + 52), (x + 26, y + 64), (x + 46, y + 38)], 7, GREEN, taper=.3, seed=sd + 5)
    else:
        inner += blob(rect_pts(x - 60, y - 78, x + 60, y + 78), "#e2e6ec", .5)
    s.append(shape(rect_pts(x - 60, y - 78, x + 60, y + 78, 6), "#fbf9f2", inner, w=4.2, seed=sd + 10))
    # загнутый уголок
    s.append(shape([(x + 34, y - 78, 1), (x + 60, y - 52, 1), (x + 34, y - 52, 1)], "#e2ddd0", "", w=3, seed=sd + 11))
    return "".join(s)


def runner(x, y, i, row, on_t, t):
    """Человечек ~200 px (ступни y). on_t — когда загорается (или None). Разминка на месте всё время."""
    lit = 0.0 if on_t is None else smooth(on_t, on_t + 0.08, t)
    e = (t - on_t) if on_t is not None and t >= on_t else -1.0
    ph = i * 0.9 + row * 2.1
    jog = math.sin(t * 8.5 + ph)
    hop = 0.0
    arms_up = 0.0
    if e >= 0:
        hop = -46 * math.sin(math.pi * clamp(e / 0.32)) - 8 * abs(math.sin((t - on_t - 0.32) * 7.5)) * (e > 0.32)
        arms_up = smooth(0.0, 0.14, e)
    bob = -5 * abs(jog) + hop
    top = GREY if lit < .5 else GREEN
    top_sh = GREY_SH if lit < .5 else GREEN_SH
    low = GREY_LO if lit < .5 else GREEN_LO
    skin = "#d6d2cc" if lit < .5 else SKIN_SET[(i + row * 3) % 10]
    hair = "#8f97a4" if lit < .5 else HAIR_SET[(i + row * 3) % 10]
    s = []
    if lit > 0:
        g = rad_grad([(0, "#9dffb2", .7 * lit), (1, "#9dffb2", 0)], x, y - 100 + bob, 95, 120)
        s.append(f'<ellipse cx="{f(x)}" cy="{f(y - 100 + bob)}" rx="95" ry="120" fill="url(#{g})"/>')
    sq = 1 - (0.12 * math.exp(-max(e - 0.32, 0) * 9) if e > 0.3 else 0)
    s.append(blob(ellipse_pts(x, y + 4, 34 + bob * .2, 7, 12), "#5a6a7a", .3))
    g_ = []
    # ноги (бег на месте: колени по очереди)
    for k, sgn in enumerate((-1, 1)):
        lift = max(0, sgn * jog) * 22 * (1 - arms_up)
        hip = (x + sgn * 13, y - 92)
        knee = (x + sgn * 15 + 4, y - 50 - lift)
        foot = (x + sgn * 15, y - 10 - lift * 1.2)
        g_.append(line([hip, knee, foot], 15, low, taper=.05, wmin=.95, seed=300 + i * 7 + k))
        g_.append(shape(ellipse_pts(foot[0] + 5, foot[1] + 4, 15, 8, 10), "#ffffff", blob([(foot[0] - 8, foot[1] + 6), (foot[0] + 20, foot[1] + 6), (foot[0] + 20, foot[1] + 12), (foot[0] - 8, foot[1] + 12)], "#9aa3b2"),
                        w=2.6, seed=320 + i * 7 + k))
    # руки
    for k, sgn in enumerate((-1, 1)):
        sh = (x + sgn * 22, y - 150)
        if arms_up > 0:
            el = (x + sgn * (34 + 6 * arms_up), y - 150 - 34 * arms_up + (1 - arms_up) * 30)
            hd = (x + sgn * (42 + 8 * arms_up), y - 150 - 70 * arms_up + (1 - arms_up) * 54)
        else:
            sw = -sgn * jog
            el = (x + sgn * 30, y - 126 + 4 * sw)
            hd = (x + sgn * 24 + 10 * sw * sgn, y - 104 - 8 * sw)
        g_.append(line([sh, el, hd], 13, top_sh, taper=.05, wmin=.95, seed=340 + i * 7 + k))
        g_.append(shape(ellipse_pts(hd[0], hd[1], 8, 8, 10), skin, "", w=2.4, seed=350 + i * 7 + k))
    # туловище — кофта с молнией
    body = [(x - 26, y - 160, 1), (x + 26, y - 160, 1), (x + 28, y - 90), (x + 20, y - 84, 1), (x - 20, y - 84, 1), (x - 28, y - 90)]
    inner = blob([(x + 6, y - 160), (x + 26, y - 160), (x + 28, y - 90), (x + 6, y - 84)], top_sh, .8)
    inner += line([(x, y - 154), (x, y - 88)], 2.4, INK, taper=.1, wmin=.8, seed=360 + i, op=.55)
    inner += line([(x - 22, y - 120), (x - 24, y - 92)], 3.4, "#f4f1ea", taper=.1, wmin=.8, seed=361 + i, op=.85)
    g_.append(shape(body, top, inner, w=3.4, seed=362 + i))
    # голова
    hx, hy = x, y - 190
    g_.append(shape(ellipse_pts(hx, hy, 25, 27, 16), skin, blob(ellipse_pts(hx + 8, hy + 6, 18, 20, 12), lib.mul(skin, (.86, .84, .9)), .6),
                    w=3.4, seed=370 + i))
    g_.append(shape([(hx - 26, hy - 4), (hx - 24, hy - 20), (hx - 6, hy - 30), (hx + 16, hy - 28), (hx + 27, hy - 10), (hx + 22, hy - 14),
                     (hx + 4, hy - 18), (hx - 14, hy - 12)], hair, "", w=2.8, seed=380 + i))
    if lit > .5:
        for sgn in (-1, 1):
            g_.append(f'<ellipse cx="{f(hx + sgn * 9)}" cy="{f(hy - 1)}" rx="5" ry="6.5" fill="#ffffff" stroke="{INK}" stroke-width="2.2"/>'
                      f'<circle cx="{f(hx + sgn * 9)}" cy="{f(hy)}" r="2.6" fill="{INK}"/>')
        g_.append(line([(hx - 9, hy + 11), (hx, hy + 16), (hx + 9, hy + 11)], 3, INK, seed=390 + i))
    else:
        for sgn in (-1, 1):
            g_.append(f'<circle cx="{f(hx + sgn * 9)}" cy="{f(hy)}" r="3" fill="{INK}"/>')
        g_.append(line([(hx - 6, hy + 13), (hx + 6, hy + 13)], 2.6, INK, seed=390 + i))
    s.append(f'<g transform="translate({f(x)} {f(y + bob)}) scale({f(1 / sq ** .5)} {f(sq)}) translate({f(-x)} {f(-y)})">{"".join(g_)}</g>')
    # искры на загорании
    if 0 <= e < 0.45:
        for j in range(6):
            a = -math.pi / 2 + (j - 2.5) * 0.42
            r0 = 120 + 70 * ease_out(e / .45)
            L = 26 * (1 - e / .45)
            cx, cy = x, y - 120
            s.append(line([(cx + math.cos(a) * r0 * .7, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + L) * .7, cy + math.sin(a) * (r0 + L))],
                          6, "#3cbf63", taper=.5, seed=400 + i * 9 + j))
    return "".join(s)


def s12(t):
    s = []
    for row, y in enumerate(ROW_Y):
        written = row == 0
        k = 1 + 0.03 * math.sin(t * 2.4 + row)
        pulse = 0.0
        if row == 0 and t > 20.88:
            pulse = 0.08 * math.exp(-(t - 20.88) * 3)
        if row == 1 and t > 23.2:
            pulse = 0.08 * math.exp(-(t - 23.2) * 3)
        sc = k + pulse
        ix, iy = 100, y - 120
        s.append(f'<g transform="translate({ix} {f(iy)}) rotate({f(-4 + 3 * math.sin(t * 1.7 + row))}) scale({f(sc)}) translate({-ix} {-iy})">'
                 f'{_ST["icon"][row]}</g>')
        for i in range(10):
            on = None
            if row == 0 and i in TOP_IDX:
                on = TOP_ON[TOP_IDX.index(i)]
            if row == 1 and i in BOT_ON:
                on = BOT_ON[i]
            s.append(runner(X0 + i * DX, y, i, row, on, t))
    u = clamp((t - 20.08) / 4.04)
    cm = cam(560, 900, 1.0 + 0.03 * ease_io(u), 0.3 - 0.6 * u)
    return "".join(s), cm


def frame(sid, t):
    if not _ST:
        _ST["bg"] = background()
        _ST["icon"] = [icon_sheet(100, ROW_Y[0] - 120, True, 500), icon_sheet(100, ROW_Y[1] - 120, False, 520)]
        lib.static_done()
    lib.dyn_begin()
    art, cm = s12(t)
    return svg(f'<rect width="{W}" height="{H}" fill="#d9e4ea"/><g transform="{cm}">{_ST["bg"]}{art}</g>')
