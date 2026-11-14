"""Сцена «сетка» рилса 42 (s12 21.0–23.4, s13 23.0–25.3): тёмно-синий фон (как fact). Вверху стоит студент в розовой
футболке с глупым принтом, перед ним 20 сидящих за партами человечков (5×4).
s12 «Они думали, что заметит половина»: на «думали» (21.6) над студентом всплывает пузырь «½»; на «половина» (22.48)
    волной от него половина человечков (шахматкой) поворачивает головы к нему и загорается золотом; медленный отъезд.
s13 «а заметила примерно четверть»: на «заметила» (23.36) «½» в пузыре зачёркивается красным, лишние гаснут и
    отворачиваются; остаётся каждый четвёртый; на «четверть» (24.6) оставшиеся вспыхивают, крупная «¼» бьёт в кадр.
«½» и «¼» — кодом (цифры и косая черта). Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import person
import scene_class as sc_
import scene_fact as sf
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad,
                 rect_pts, shape, svg)

_ST = {}
THINK = 21.6            # «думали»
HALF = 22.48            # «половина»
SAW = 23.36             # «заметила»
QUART = 24.6            # «четверть»
HX, HY = 540, 540       # ноги студента в футболке
GX0, GDX, GY0, GDY = 180, 180, 760, 168
SKIN = ["#f0c4a0", "#8a5a3c", "#f4d0b4", "#d9a07a", "#c98e6a", "#f2c9a8", "#a8704c"]
HAIR = ["#5a3a26", "#2a1a14", "#c8622a", "#e0b050", "#1a1210", "#7a4a2a"]
TOPS = ["#2d55a8", "#3a9a6a", "#7a4fb0", "#c94a3f", "#2f8a8a", "#d9467a", "#d9a338", "#4a5a8c"]


def idx(r, c):
    return r * 5 + c


def in_half(r, c):
    return (r + c) % 2 == 0


def in_quarter(r, c):
    return idx(r, c) % 4 == 0


def gpos(r, c):
    return GX0 + c * GDX, GY0 + r * GDY


def state(r, c, t):
    """(поворот 0..1, свечение 0..1) человечка."""
    x, y = gpos(r, c)
    d = math.hypot(x - HX, y - HY) / 900
    turn, glow = 0.0, 0.0
    if in_half(r, c):
        k = ease_out(clamp((t - HALF - d * .35) / 0.22), 2)
        turn, glow = k, k
        if not in_quarter(r, c):
            off = ease_io(clamp((t - SAW - d * .3) / 0.3))
            turn *= 1 - off
            glow *= 1 - off
    return turn, glow


def seated(r, c, t):
    x, y = gpos(r, c)
    i = idx(r, c)
    turn, glow = state(r, c, t)
    skin, hair, top = SKIN[(i * 3) % 7], HAIR[(i * 5 + 1) % 6], TOPS[(i * 3 + r) % 8]
    sd = 8000 + i * 30
    ph = i * 1.37
    bob = 2.5 * math.sin(t * 3.1 + ph)
    # всплеск на «четверть»
    eq = t - QUART
    pop = 0.0
    if in_quarter(r, c) and eq > 0:
        pop = 12 * math.exp(-eq * 6) * math.sin(min(eq * 14, math.pi))
    yy = y + bob - pop - 10 * turn
    s = []
    if glow > 0.01:
        g = rad_grad([(0, "#ffe46a", .95 * glow), (.5, "#ffb52a", .45 * glow), (1, "#ffb52a", 0)], x, yy - 70, 115, 115)
        s.append(f'<rect x="{f(x - 120)}" y="{f(yy - 190)}" width="240" height="240" fill="url(#{g})"/>')
    topc = mix(top, "#ffd23f", .7 * glow)
    dim = ease_io(clamp((t - QUART - .05) / 0.25)) * (0 if in_quarter(r, c) else .45)
    if dim > 0:
        topc = mix(topc, "#2a3460", dim)
        skin = mix(skin, "#4a5280", dim * .8)
        hair = mix(hair, "#1c2244", dim * .8)
    body = [(-46, 0, 1), (-46, -22), (-36, -44), (0, -54), (36, -44), (46, -22), (46, 0, 1)]
    s.append(shape([(x + px, yy + py) + tuple(e) for px, py, *e in body], topc,
                   blob([(x + 10, yy - 52), (x + 48, yy - 36), (x + 48, yy + 2), (x + 16, yy + 2)], lib.mul(topc, (.8, .78, .86)), .9), w=3.4, seed=sd))
    # голова: поворачивается к студенту (наклон и сдвиг), глаза на него
    hx, hy = x, yy - 86
    dx, dy = HX - x, (HY - 250) - hy
    dn = math.hypot(dx, dy) + 1e-6
    lx, ly = dx / dn * turn, dy / dn * turn
    tilt = -lx * 16 + 4 * math.sin(t * 1.7 + ph) * (1 - turn)
    head = []
    head.append(shape(ellipse_pts(0, 0, 34, 36, 16), skin, blob(ellipse_pts(12, 8, 26, 30, 12), lib.mul(skin, (.86, .82, .88)), .8), w=3.4, seed=sd + 1))
    hs = [(-37, 2), (-36, -22), (-22, -38), (2, -42), (24, -36), (37, -18), (36, 2), (24, -16), (lx * 10 + 6, -24), (lx * 10 - 14, -20), (-26, -12)]
    if i % 3 == 1:          # кудри
        hs = [(-38, 4), (-42, -16), (-32, -36), (-12, -46), (8, -46), (28, -40), (40, -22), (40, 4), (26, -18), (0, -24), (-26, -16)]
    head.append(shape(hs, hair, blob([(6, -42), (37, -18), (36, 2), (24, -16)], lib.mul(hair, (.7, .7, .75)), .9), w=3.4, seed=sd + 2))
    ex0 = lx * 8
    blink = 1.0 if ((t + ph * .41) % 3.3) < 0.07 else 0.0
    for k, ex in enumerate((-12 + ex0, 12 + ex0)):
        if blink:
            head.append(line([(ex - 8, 2), (ex + 8, 2)], 2.6, seed=sd + 5 + k))
        else:
            head.append(shape(ellipse_pts(ex, 0, 8.5, 10.5, 10), "#ffffff",
                              f'<circle cx="{f(ex + lx * 4)}" cy="{f(1 + ly * 4)}" r="3.8" fill="{INK}"/>', w=2.4, seed=sd + 5 + k))
    if turn > .5:
        head.append(shape(ellipse_pts(ex0, 20, 5, 6, 10), "#5a2a2a", "", w=2, seed=sd + 8))       # «о!»
    else:
        head.append(line([(ex0 - 8, 19), (ex0, 22), (ex0 + 8, 19)], 2.6, seed=sd + 8))
    s.append(f'<g transform="translate({f(hx)} {f(hy)}) rotate({f(tilt)})">{"".join(head)}</g>')
    # парта перед человечком, лист и руки
    s.append(shape(rect_pts(x - 66, y - 18, x + 66, y + 4, 4), "#c99a62", blob(rect_pts(x + 20, y - 18, x + 66, y + 4), "#a87c4c", .7), w=3.2, seed=sd + 10))
    s.append(shape(rect_pts(x - 60, y + 4, x + 60, y + 34), "#a87c4c", blob(rect_pts(x + 20, y + 4, x + 60, y + 34), "#8a6238", .7), w=3, seed=sd + 11))
    s.append(shape([(x - 22, y - 16, 1), (x + 22, y - 16, 1), (x + 18, y - 4, 1), (x - 26, y - 4, 1)], "#fbfaf4", "", w=2, seed=sd + 12))
    for k, hx_ in enumerate((x - 34, x + 30)):
        s.append(shape(ellipse_pts(hx_ + (2 * math.sin(t * 7 + ph) if k else 0), y - 16, 10, 7, 10), skin, "", w=2.4, seed=sd + 13 + k))
    return "".join(s)


def hero(t):
    spec = dict(sc_.HERO)
    spec["face"] = 0.0
    pose = {"look": (0.0, 0.25), "mouth": "smile", "brow": -0.3, "on_torso": sc_.print_face(t),
            "blink": 1.0 if (t % 2.9) < .07 else 0.0, "head_tilt": 3 * math.sin(t * 2),
            "arms": {"L": (14, -40 - 6 * math.sin(t * 3)), "R": (-14, 40 + 6 * math.sin(t * 3))}, "curl": {"L": .2, "R": .2}}
    s = []
    g = rad_grad([(0, "#7f95d6", .55), (.6, "#5a70b4", .2), (1, "#5a70b4", 0)], HX, HY - 160, 260, 260)
    s.append(f'<rect x="{HX - 280}" y="{HY - 440}" width="560" height="560" fill="url(#{g})"/>')
    s.append(blob(ellipse_pts(HX, HY + 4, 80, 12, 12), "#141b38", .55, blur(6)))
    sc = .44
    s.append(person.draw(spec, dict(pose, no_arms=True), HX, HY, sc, sd=8800))
    s.append(person.draw(spec, dict(pose, only_arms=True), HX, HY, sc, sd=8800))
    return "".join(s)


def fraction(x, y, num, den, size, col, sd):
    """Дробь кодом: числитель, косая черта, знаменатель (без знака «½», которого может не быть в шрифте)."""
    s = sf.text(x - size * .26, y - size * .1, num, size * .62, col, sw=size * .05)
    s += line([(x + size * .26, y - size * .62), (x - size * .26, y + size * .3)], size * .075, INK, taper=.05, wmin=.9, seed=sd)
    s += line([(x + size * .26, y - size * .62), (x - size * .26, y + size * .3)], size * .045, col, taper=.05, wmin=.9, seed=sd + 1)
    s += sf.text(x + size * .28, y + size * .42, den, size * .62, col, sw=size * .05)
    return s


def half_bubble(t):
    e = t - THINK
    if e < 0:
        return ""
    k = back_out(clamp(e / 0.3), 2.2)
    eh = t - HALF
    if eh > 0:
        k *= 1 + 0.12 * math.exp(-eh * 7) * math.sin(min(eh * 16, math.pi))
    cx, cy = 790, 250 + 8 * math.sin(t * 2.2)
    content = fraction(0, 10, "1", "2", 170, "#3a6ad0", 8900)
    es = t - SAW                                     # зачёркнуто
    if es > 0:
        u = ease_out(clamp(es / 0.25), 2)
        p0, p1 = (-90, -70), (90, 80)
        content += line([p0, (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)], 16, "#e5383b", taper=.2, wmin=.5, seed=8910)
    return sf.bubble(cx, cy, 300, 240, (HX + 60, HY - 380), content, k, 8920, 0.0)


def quarter(t):
    e = t - (QUART - 0.04)
    if e < 0:
        return ""
    u = clamp(e / 0.16)
    sc = 2.2 - 1.2 * ease_in(u, 2)
    if e > 0.16:
        el = e - 0.16
        sc = 1 + 0.12 * math.exp(-el * 8) * math.cos(el * 26)
    x, y = 300, 340
    g = rad_grad([(0, "#ffe27a", .55), (1, "#ffe27a", 0)], 0, 0, 260, 220)
    body = f'<ellipse cx="0" cy="0" rx="260" ry="220" fill="url(#{g})"/>' if e > 0.12 else ""
    body += fraction(0, 30, "1", "4", 240, "#ffd84a", 8950)
    out = f'<g transform="translate({x} {y}) rotate({f(-6 + 2 * math.sin(t * 2))}) scale({f(sc)})">{body}</g>'
    out += sf.rays(x, y, e - 0.16, 8960, r=200, n=14, L0=90, w=13)
    return out


def scene(t):
    s = [_ST["bg"], sf.dust(t), hero(t), half_bubble(t)]
    for r in range(4):
        for c in range(5):
            s.append(seated(r, c, t))
    s.append(quarter(t))
    return "".join(s)


def s12(t):
    u = clamp((t - 21.0) / 2.4)
    sc = 1.22 - 0.16 * (0.35 * u + 0.65 * ease_io(u))
    cx, cy = 540, 760 + 30 * (1 - u)
    rot = -0.6 + 0.8 * u
    sc *= 1 + sf.kick(t, HALF, 0.03, 7, 14)
    return cam(cx, cy, sc, rot), scene(t)


def s13(t):
    u = clamp((t - 23.0) / 2.3)
    sc = 1.06 + 0.1 * ease_io(u)
    cx, cy = 540, 760 - 20 * u
    rot = 0.2 - 0.6 * u
    sc *= 1 + sf.kick(t, SAW, 0.02, 7, 14)
    e = t - QUART
    if e > 0:
        kk = math.exp(-e * 7)
        sc *= 1 + 0.07 * kk
        cx += 14 * kk * math.sin(e * 47)
        cy += 12 * kk * math.sin(e * 39)
        rot += 1.2 * kk * math.sin(e * 31)
    return cam(cx, cy, sc, rot), scene(t)


def build_static():
    _ST["bg"] = sf.background()
    lib.static_done()


def frame(sid, t):
    if not _ST:
        build_static()
    lib.dyn_begin()
    tr, body = {"s12": s12, "s13": s13}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1a2244"/><g transform="{tr}">{body}</g>')
