"""Сцена study рилса 44, план s09 (17.6–19.4, клип 17.4–19.6): «как мечты влияют на дела».
Два ряда маленьких разных людей (человечки из scene_rows рилса 26/40, но каждый в своей одежде). На «мечты» (17.96) над
каждым по очереди выскакивает облачко мечты с картинкой (море, гитара, дом, кубок, машина, гора, книга, самолёт…).
На «дела» (18.96) у части людей под ногами появляется зелёная стрелка вперёд и они шагают по ней; у остальных облака
раздуваются, а сами они стоят. Панорама вдоль рядов. Без букв."""
import math

import numpy as np

import lib
import props
from c44 import kick, wt
from lib import (INK, W, H, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, lin_grad, rad_grad, rect_pts, shape,
                 smooth, svg)

_ST = {}
T_MECH = wt("мечты", 17.0)   # 17.96
T_DELA = wt("дела")          # 18.96
ROW_Y = [700, 1260]
X0, DX = 170, 185
N = 5
DOERS = {(0, 1), (0, 3), (1, 0), (1, 2), (1, 4)}
SKIN = ["#f2c9a8", "#c98e6a", "#e8b896", "#8a5a3c", "#f0c4a0", "#d9a07a", "#f4d0b4", "#a8704c", "#e9c0a0", "#c99470"]
HAIR = ["#3a2418", "#2a1a14", "#c8622a", "#5a3a26", "#e0b050", "#1a1210", "#6a4a30", "#9a9590", "#7a4a2a", "#3a2a22"]
TOPS = ["#d8433a", "#3f6f9a", "#e0a64a", "#5f8f5a", "#7a5a9a", "#2f8f8a", "#d98a4a", "#c9554c", "#4a6ab0", "#8a6a4a"]
LOWS = ["#3b3f58", "#4a4136", "#2c3140", "#5a4a3a", "#34404c"]
ICONS = ["sea", "guitar", "house", "cup", "car", "mount", "plane", "book", "sea", "house"]
GREEN, GREEN_SH = "#3cbf63", "#279a4a"


def icon(name, x, y, k, sd):
    """Маленькая картинка внутри облачка (центр x, y; размер ~ 90·k)."""
    s = []
    if name == "sea":
        s.append(shape(ellipse_pts(x + 20 * k, y - 14 * k, 14 * k, 14 * k, 12), "#ffd84a", "", w=2.4, seed=sd))
        for j in range(2):
            yy = y + (8 + 14 * j) * k
            s.append(line([(x - 40 * k + i * 10 * k, yy + 4 * k * math.sin(i * 1.6)) for i in range(9)], 5 * k, "#3f8fd0", taper=.2, seed=sd + 1 + j))
    elif name == "guitar":
        s.append(shape(rect_pts(x - 28 * k, y - 10 * k, x + 28 * k, y + 28 * k), "#5f8fd0",
                       blob(rect_pts(x - 6 * k, y - 10 * k, x + 6 * k, y + 28 * k), "#f2c232"), w=2.6, seed=sd))
        s.append(shape(rect_pts(x - 32 * k, y - 22 * k, x + 32 * k, y - 8 * k), "#7aa6e0", blob(rect_pts(x - 6 * k, y - 22 * k, x + 6 * k, y - 8 * k), "#f2c232"),
                       w=2.6, seed=sd + 1))
        for sg in (-1, 1):
            s.append(shape([(x, y - 22 * k), (x + sg * 22 * k, y - 40 * k), (x + sg * 26 * k, y - 26 * k)], "#f2c232", "", w=2.2, seed=sd + 3 + sg))
    elif name == "house":
        s.append(shape(rect_pts(x - 26 * k, y - 4 * k, x + 26 * k, y + 30 * k), "#f2d7a8", blob(rect_pts(x - 6 * k, y + 8 * k, x + 8 * k, y + 30 * k), "#8a5a34"),
                       w=2.6, seed=sd))
        s.append(shape([(x - 36 * k, y - 2 * k, 1), (x, y - 34 * k, 1), (x + 36 * k, y - 2 * k, 1)], "#d8433a", "", w=2.6, seed=sd + 1))
    elif name == "cup":
        s.append(shape([(x - 24 * k, y - 26 * k, 1), (x + 24 * k, y - 26 * k, 1), (x + 16 * k, y + 4 * k), (x, y + 10 * k), (x - 16 * k, y + 4 * k)],
                       "#f2c232", blob([(x + 4 * k, y - 26 * k), (x + 24 * k, y - 26 * k), (x + 16 * k, y + 4 * k), (x + 4 * k, y + 8 * k)], "#d49a1e", .9),
                       w=2.6, seed=sd))
        s.append(shape(rect_pts(x - 5 * k, y + 8 * k, x + 5 * k, y + 22 * k), "#f2c232", "", w=2.2, seed=sd + 1))
        s.append(shape(rect_pts(x - 16 * k, y + 22 * k, x + 16 * k, y + 30 * k), "#8a5a34", "", w=2.2, seed=sd + 2))
    elif name == "car":
        s.append(shape([(x - 40 * k, y + 16 * k, 1), (x - 36 * k, y - 2 * k), (x - 16 * k, y - 4 * k), (x - 6 * k, y - 20 * k), (x + 18 * k, y - 20 * k),
                        (x + 28 * k, y - 4 * k), (x + 40 * k, y), (x + 40 * k, y + 16 * k, 1)], "#3f8fd0", "", w=2.6, seed=sd))
        for dx in (-22, 22):
            s.append(shape(ellipse_pts(x + dx * k, y + 18 * k, 9 * k, 9 * k, 10), "#2a2a2e", "", w=2.2, seed=sd + 3 + dx))
    elif name == "mount":
        s.append(shape([(x - 44 * k, y + 26 * k, 1), (x - 8 * k, y - 26 * k, 1), (x + 8 * k, y - 26 * k, 1), (x + 44 * k, y + 26 * k, 1)], "#6f8fb8",
                       blob([(x - 18 * k, y - 12 * k), (x - 8 * k, y - 26 * k), (x + 8 * k, y - 26 * k), (x + 18 * k, y - 12 * k), (x + 6 * k, y - 6 * k),
                             (x - 4 * k, y - 12 * k)], "#ffffff"), w=2.6, seed=sd))
    elif name == "plane":
        s.append(line([(x - 10 * k, y + 8 * k), (x - 6 * k, y + 22 * k)], 2.4, INK, seed=sd + 2))
        s.append(line([(x + 10 * k, y + 8 * k), (x + 6 * k, y + 22 * k)], 2.4, INK, seed=sd + 3))
        s.append(shape([(x, y - 34 * k), (x + 26 * k, y - 16 * k), (x + 20 * k, y + 2 * k), (x + 8 * k, y + 10 * k, 1), (x - 8 * k, y + 10 * k, 1),
                        (x - 20 * k, y + 2 * k), (x - 26 * k, y - 16 * k)], "#d8433a",
                       blob([(x - 8 * k, y - 34 * k), (x + 8 * k, y - 34 * k), (x + 6 * k, y + 10 * k), (x - 6 * k, y + 10 * k)], "#f2c232"), w=2.6, seed=sd))
        s.append(shape(rect_pts(x - 9 * k, y + 20 * k, x + 9 * k, y + 32 * k), "#8a5a34", "", w=2.2, seed=sd + 1))
    elif name == "book":
        s.append(shape([(x - 38 * k, y - 18 * k, 1), (x, y - 10 * k, 1), (x + 38 * k, y - 18 * k, 1), (x + 38 * k, y + 22 * k, 1), (x, y + 28 * k, 1),
                        (x - 38 * k, y + 22 * k, 1)], "#fbf9f2", line([(x, y - 10 * k), (x, y + 28 * k)], 2.4, INK, seed=sd + 1), w=2.6, seed=sd))
    return "".join(s)


def cloud(cx, cy, k, name, sd, head, trail=1.0):
    o = []
    for j, (u, r) in enumerate([(.82, 7), (.64, 11)]):
        x, y = cx + (head[0] - cx) * u, cy + (head[1] - cy) * u
        rr = r * clamp(trail * 2 - j)
        if rr > 1.5:
            o.append(shape(ellipse_pts(x, y, rr, rr * .86, 10), props.PAPER, "", w=2.6, seed=sd + j))
    if k <= 0.02:
        return "".join(o)
    pts = props.cloud_pts(cx, cy, 70, 54, 8, k)
    inner = blob(ellipse_pts(cx + 10 * k, cy + 14 * k, 66 * k, 40 * k, 16), "#efe7d4", .9)
    inner += icon(name, cx, cy, 0.9 * k, sd + 10)
    o.append(shape(pts, props.PAPER, inner, w=3.4, seed=sd + 5))
    return "".join(o)


def little(x, y, i, row, t, walk=None):
    """Человечек ~230 px (ступни y). walk — фаза шага (None — стоит, чуть покачивается)."""
    j = i + row * N
    skin, hair, top, low = SKIN[j % 10], HAIR[(j * 3) % 10], TOPS[(j * 7) % 10], LOWS[j % 5]
    top_sh = lib.mul(top, (.8, .78, .86))
    ph = j * 1.3
    sw = math.sin(walk) if walk is not None else 0.0
    bob = -6 * abs(math.sin(walk)) if walk is not None else -2 * math.sin(t * 2.6 + ph)
    g = []
    g.append(blob(ellipse_pts(x, y + 4, 40, 8, 12), "#5a4a3a", .25))
    for k, sgn in enumerate((-1, 1)):
        a = sgn * sw * 24
        hip = (x + sgn * 12, y - 100)
        knee = (x + sgn * 12 + 46 * math.sin(math.radians(a)), y - 54)
        foot = (x + sgn * 12 + 92 * math.sin(math.radians(a)) * .9, y - 10)
        g.append(line([hip, knee, foot], 17, low, taper=.05, wmin=.95, seed=300 + j * 7 + k))
        g.append(shape(ellipse_pts(foot[0] + 8, foot[1] + 3, 16, 8, 10), "#2e2a2c", "", w=2.6, seed=320 + j * 7 + k))
    for k, sgn in enumerate((-1, 1)):
        a = -sgn * sw * 30
        sh = (x + sgn * 24, y - 160)
        el = (x + sgn * 30 + 26 * math.sin(math.radians(a)), y - 122)
        hd = (x + sgn * 30 + 46 * math.sin(math.radians(a)), y - 90)
        g.append(line([sh, el, hd], 14, top_sh, taper=.05, wmin=.95, seed=340 + j * 7 + k))
        g.append(shape(ellipse_pts(hd[0], hd[1], 9, 9, 10), skin, "", w=2.4, seed=350 + j * 7 + k))
    body = [(x - 28, y - 172, 1), (x + 28, y - 172, 1), (x + 30, y - 96), (x + 22, y - 90, 1), (x - 22, y - 90, 1), (x - 30, y - 96)]
    g.append(shape(body, top, blob([(x + 6, y - 172), (x + 28, y - 172), (x + 30, y - 96), (x + 6, y - 90)], top_sh, .8), w=3.4, seed=362 + j))
    hx, hy = x, y - 204
    g.append(shape(ellipse_pts(hx, hy, 27, 29, 16), skin, blob(ellipse_pts(hx + 9, hy + 6, 19, 21, 12), lib.mul(skin, (.86, .84, .9)), .6),
                   w=3.4, seed=370 + j))
    style = j % 3
    if style == 0:
        hp = [(hx - 28, hy - 2), (hx - 26, hy - 22), (hx - 6, hy - 32), (hx + 16, hy - 30), (hx + 29, hy - 10), (hx + 22, hy - 16), (hx + 4, hy - 20),
              (hx - 14, hy - 14)]
    elif style == 1:
        hp = [(hx - 30, hy + 18), (hx - 30, hy - 14), (hx - 12, hy - 33), (hx + 14, hy - 33), (hx + 30, hy - 14), (hx + 30, hy + 18), (hx + 22, hy + 16),
              (hx + 20, hy - 12), (hx - 20, hy - 12), (hx - 22, hy + 16)]
    else:
        hp = [(hx - 27, hy - 6), (hx - 22, hy - 28), (hx, hy - 36), (hx + 22, hy - 28), (hx + 27, hy - 6), (hx + 14, hy - 20), (hx - 10, hy - 22)]
    g.append(shape(hp, hair, "", w=2.8, seed=380 + j))
    up = walk is None and t > T_DELA
    for sgn in (-1, 1):
        ex, ey = hx + sgn * 10 + 3, hy - 1
        g.append(f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="6" ry="7.5" fill="#ffffff" stroke="{INK}" stroke-width="2.2"/>'
                 f'<circle cx="{f(ex + 1.5)}" cy="{f(ey - (3 if up else 0))}" r="3" fill="{INK}"/>')
    if walk is not None:
        g.append(line([(hx - 6, hy + 12), (hx + 3, hy + 17), (hx + 11, hy + 11)], 3, INK, seed=390 + j))
    else:
        g.append(line([(hx - 4, hy + 15), (hx + 8, hy + 15)], 2.6, INK, seed=390 + j))
    return f'<g transform="translate(0 {f(bob)})">{"".join(g)}</g>'


def arrow(x, y, u, sd):
    """Зелёная стрелка вперёд под ногами: вырастает вправо."""
    if u <= 0:
        return ""
    L = 150 * u
    pts = [(x - 40, y + 16, 1), (x - 40 + L, y + 16, 1), (x - 40 + L, y + 4, 1), (x - 6 + L, y + 30, 1), (x - 40 + L, y + 56, 1), (x - 40 + L, y + 44, 1),
           (x - 40, y + 44, 1)]
    return shape(pts, GREEN, blob(rect_pts(x - 40, y + 34, x + L, y + 46), GREEN_SH, .8), w=3.4, seed=sd)


def background():
    s = []
    g = lin_grad([(0, "#f3ead6", 1), (1, "#e8dcc0", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#{g})"/>')
    g2 = rad_grad([(0, "#fff6e0", .8), (1, "#fff6e0", 0)], 540, 700, 700, 600)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#{g2})"/>')
    for k, y in enumerate(ROW_Y):
        pts = [(-500, y - 12, 1), (W + 500, y - 12, 1), (W + 500, y + 70, 1), (-500, y + 70, 1)]
        s.append(shape(pts, "#d9c9a6", blob(rect_pts(-500, y + 40, W + 500, y + 70), "#c7b590", .8), w=3.6, seed=700 + k))
    return "".join(s)


def frame09(t):
    s = [_ST["bg"]]
    back, front = [], []
    for row, y in enumerate(ROW_Y):
        for i in range(N):
            x0 = X0 + i * DX + (40 if row else 0)
            doer = (row, i) in DOERS
            st = T_DELA + 0.04 * i
            walk = None
            x = x0
            if doer and t > st + 0.12:
                q = t - st - 0.12
                x = x0 + 55 * ease_out(clamp(q / 0.45), 2) + 25 * max(0, q - 0.45)
                walk = q * 11
            if doer:
                s.append(arrow(x0 + 20, y, ease_out(clamp((t - st) / 0.16)), 800 + row * 10 + i))
            # облачко
            ct = T_MECH + 0.05 * (i + row * N) * 0.9
            e = t - ct
            k = 0.0
            if e > 0:
                k = 1 + 0.2 * math.exp(-e * 9) * math.cos(e * 20) if e > 0.1 else ease_out(e / 0.1) * 1.2
            if doer and t > st + 0.1:
                k *= 1 - ease_out(clamp((t - st - 0.1) / 0.3), 2)
            if not doer and t > st:
                k *= 1 + 0.45 * ease_out(clamp((t - st) / 0.35))
            hx, hy = x, y - 240
            cx, cy = x + 24 + 6 * math.sin(t * 2 + i), y - 360 - (40 * (k - 1) if k > 1 else 0)
            tr = clamp((t - (17.42 + 0.05 * (i + row * N))) / 0.3)
            if doer:
                tr *= 1 - clamp((t - st - 0.1) / 0.25)
            item = little(x, y, i, row, t, walk) + cloud(cx, cy, k, ICONS[(i + row * N) % 10], 900 + (row * N + i) * 20, (hx, hy), tr)
            (front if doer else back).append(item)
        s += back + front
        back, front = [], []
    return "".join(s)


def cam09(t):
    u = clamp((t - 17.4) / 2.2)
    k, rot = kick(t, [T_MECH, T_DELA], 0.025, 12)
    return cam(470 + 150 * ease_io(u), 880 + 10 * u, 1.3 * k, rot + 0.6 - 1.2 * u)


def frame(sid, t):
    if not _ST:
        lib.DEFS.clear()
        _ST["bg"] = background()
        lib.static_done()
    lib.dyn_begin()
    return svg(f'<rect width="{W}" height="{H}" fill="#efe4cc"/><g transform="{cam09(t)}">{frame09(t)}</g>')


_ = (blur, smooth, np)
