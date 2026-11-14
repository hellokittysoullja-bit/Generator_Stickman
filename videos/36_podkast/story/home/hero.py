"""Общее для планов home рилса 36: поза «стоит», сумка через плечо, абонемент, наушники на шее, телефон, капля пота,
звёздочка-блик. Мир: пол y = 0; Дима — dima.draw (L-единицы × dima.BS)."""
import math

import numpy as np

import dima
import lib
from lib import INK, blob, ellipse_pts, line, shape

BS = dima.BS
KS = 1.22
SOLE = ((66 - dima.AH) * KS + dima.AH) * BS          # лодыжка над полом при плоской стопе
LEG = (dima.THIGH + dima.SHIN) * BS
BAG, BAG_SH, BAG_STRIPE = "#25335c", "#18223f", "#f08a2c"
CARD, CARD_SH = "#2fb3a8", "#22877f"


def stand(hx, fx_far, fx_near, bend=0.985, lean=0.04, dy=0.0, **kw):
    """Стоит: таз над полом, стопы плоско (лодыжки в fx_far, fx_near)."""
    p = dict(hip=np.array([hx, -(SOLE + LEG * bend) + dy]), lean=lean,
             feet={"f": (np.array([fx_far, -SOLE]), 0.0), "n": (np.array([fx_near, -SOLE]), 0.0)},
             arms={"f": ("ang", 0.05, 0.3), "n": ("ang", 0.0, 0.25)}, hands={"n": "fist", "f": "fist"},
             head_ang=0.0, hood=0.0, strings=(0, 0), expr=dict(lid=0.5, look=(0.4, 0.0), brows="calm", mouth="smile"))
    p.update(kw)
    return p


def to_world_g(svg):
    return svg


# ═════════════ сумка (в L-координатах туловища, через крюк over_torso) ═════════════
def duffel(cx, cy, w=360.0, h=190.0, rot=0.0, seed=0, squash=0.0):
    """Спортивная сумка-бочонок (тёмно-синяя, оранжевая полоса, торцы, ручки). Координаты — любые (L или мир через k)."""
    hw, hh = w / 2 * (1 + squash * .25), h / 2 * (1 - squash * .3)
    body = [(-hw + 30, -hh), (hw - 30, -hh), (hw, -hh + 30), (hw + 4, hh - 34), (hw - 26, hh, 1), (-hw + 26, hh, 1), (-hw - 4, hh - 34),
            (-hw, -hh + 30)]
    inner = blob([(-hw - 10, hh * .2), (hw + 10, hh * .2), (hw + 10, hh + 10), (-hw - 10, hh + 10)], BAG_SH, .85)
    inner += blob([(-hw - 10, -hh * .12), (hw + 10, -hh * .12), (hw + 10, hh * .1), (-hw - 10, hh * .1)], BAG_STRIPE)
    inner += line([(-hw + 40, -hh + 14), (hw - 40, -hh + 14)], 2.6, "#8b97c2", seed=seed + 3, op=.8)      # молния
    inner += blob([(-hw + 20, -hh + 10), (-hw * .2, -hh + 10), (-hw * .3, -hh * .4), (-hw + 16, -hh * .4)], "#3b4c80", .6)
    o = [shape(body, BAG, inner, w=5.0, seed=seed)]
    for sx in (-1, 1):                                                          # торцы
        ex = sx * (hw - 8)
        o.append(shape(ellipse_pts(ex, 0, 22, hh * .78, 12), BAG_SH, blob(ellipse_pts(ex, 0, 10, hh * .5, 10), "#2e3f70", .9), w=3.6,
                       seed=seed + 10 + sx))
    o.append(line([(-hw * .35, -hh + 4), (-hw * .3, -hh - 60), (hw * .3, -hh - 60), (hw * .35, -hh + 4)], 9, "#1b2445", seed=seed + 20,
                  taper=.15, wmin=.8))
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f})">{"".join(o)}</g>'


def bag_on_shoulder(sw=0.0, rot_extra=0.0):
    """Крюк over_torso: сумка висит на ближнем плече, у бедра сзади; sw — качание (L)."""
    def f(info):
        S, up, fw = info["S"], info["up"], info["fw"]
        top = S + up * 34 - fw * 10
        bc = np.array([-150.0 + sw * .4, 70.0]) + np.array([sw, 0])
        a = bc + np.array([-110, -80])
        b = bc + np.array([110, -80])
        o = []
        o.append(line([tuple(a), tuple(top - fw * 40 + up * 4), tuple(top + fw * 50)], 16, "#1b2445", seed=971, taper=.08, wmin=.9))
        o.append(duffel(bc[0], bc[1], rot=-8 + sw * .05 + rot_extra, seed=980))
        return "".join(o)
    return f


def headphones_neck():
    """Крюк over_torso: белые накладные наушники на шее (профиль: ближняя чашка сбоку шеи, дуга по груди)."""
    def f(info):
        nk, fw, up = info["neck"], info["fw"], info["up"]
        cup = nk - fw * 34 - up * 6
        band_pts = [tuple(cup + fw * 10 - up * 30), tuple(nk + fw * 40 - up * 40), tuple(nk + fw * 92 - up * 4)]
        o = [line(band_pts, 18, INK, seed=990, taper=.1, wmin=.9), line(band_pts, 11, "#f4f2ec", seed=991, taper=.1, wmin=.9)]
        o.append(shape(ellipse_pts(cup[0], cup[1], 40, 48, 14, rot=-20), "#f4f2ec",
                       blob(ellipse_pts(cup[0] - 8, cup[1] + 8, 26, 34, 12, rot=-20), "#d9d5cb", .9) +
                       blob(ellipse_pts(cup[0] + 6, cup[1] - 4, 14, 20, 10, rot=-20), "#c9c3b6", .9), w=4.4, seed=992))
        return "".join(o)
    return f


def both(*fs):
    return lambda info: "".join(f(info) for f in fs if f)


# ═════════════ абонемент ═════════════
def card(cx, cy, w=150.0, rot=0.0, shine=0.0, seed=0, ink_w=4.4):
    """Бирюзовая пластиковая карта, белая иконка гантели, без букв. shine 0..1 — блик пробегает."""
    h = w * 0.63
    pts = lib.rect_pts(-w / 2, -h / 2, w / 2, h / 2, w * .09)
    inner = blob([(-w, h * .1), (w, h * .25), (w, h), (-w, h)], CARD_SH, .7)
    # гантель
    g = w * .2
    inner += f'<rect x="{-g * 1.2:.1f}" y="{-g * .12:.1f}" width="{g * 2.4:.1f}" height="{g * .24:.1f}" rx="{g * .1:.1f}" fill="#ffffff"/>'
    for sx in (-1, 1):
        inner += f'<rect x="{sx * g * 1.05 - g * .17:.1f}" y="{-g * .5:.1f}" width="{g * .34:.1f}" height="{g:.1f}" rx="{g * .1:.1f}" fill="#ffffff"/>'
        inner += f'<rect x="{sx * g * 1.42 - g * .12:.1f}" y="{-g * .32:.1f}" width="{g * .24:.1f}" height="{g * .64:.1f}" rx="{g * .08:.1f}" fill="#ffffff"/>'
    inner += f'<rect x="{w * .22:.1f}" y="{h * .18:.1f}" width="{w * .2:.1f}" height="{h * .12:.1f}" rx="3" fill="#ffffff" opacity=".55"/>'
    if shine > 0:
        x = -w + shine * 2.2 * w
        inner += blob([(x - 18, -h), (x + 10, -h), (x - 30, h), (x - 58, h)], "#ffffff", .55)
    body = lib.shape(pts, CARD, inner, w=ink_w, seed=seed + 1)
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f})">{body}</g>'


def star(x, y, r, op=1.0, rot=0.0, col="#fffbe6"):
    """Четырёхлучевая звёздочка-блик."""
    if r <= 0.5 or op <= 0.01:
        return ""
    pts = []
    for k in range(8):
        a = math.radians(rot + k * 45)
        rr = r if k % 2 == 0 else r * .22
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return (f'<path d="{lib.fill_d(pts)}" fill="{col}" opacity="{op:.3f}"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .18:.1f}" fill="#ffffff" opacity="{op:.3f}"/>')


def sparkles(x, y, t, t0, R=120, n=5, seed=0, col="#ffe27a"):
    """Искры разлетаются от точки с момента t0."""
    if t < t0:
        return ""
    u = t - t0
    rs = np.random.RandomState(seed)
    o = []
    for k in range(n):
        a = rs.uniform(0, 2 * math.pi)
        d = R * (0.5 + 0.6 * rs.rand()) * lib.ease_out(u / 0.4)
        r = (14 + 10 * rs.rand()) * math.sin(math.pi * lib.clamp(u / (0.55 + 0.25 * rs.rand())))
        o.append(star(x + d * math.cos(a), y + d * math.sin(a), r, 1.0, rot=u * 120, col=col))
    return "".join(o)


def sweat(x, y, k=1.0, op=1.0):
    """Капля пота (голубая, с бликом)."""
    if op <= 0.01:
        return ""
    pts = [(x, y - 26 * k, 1), (x + 12 * k, y - 2 * k), (x + 11 * k, y + 10 * k), (x, y + 16 * k), (x - 11 * k, y + 10 * k), (x - 12 * k, y - 2 * k)]
    return (f'<g opacity="{op:.3f}">' + lib.shape(pts, "#9fd3f0", blob(ellipse_pts(x - 3 * k, y + 4 * k, 4 * k, 6 * k, 8), "#ffffff", .9),
                                                w=2.6, seed=1990) + "</g>")


def motion_lines(pts_list, op=1.0, w=3.2, seed=0):
    return "".join(line(p, w, INK, seed=seed + i, op=op, taper=.5, wmin=.1) for i, p in enumerate(pts_list))


def cam_hook(t, base, hit):
    """Влёт правила 28–29: с 40 % дальше за 0.22 с, перелёт 5 %, поворот −3° с возвратом, удар +8 % на hit."""
    cx, cy, s, r0 = base
    u = t / 0.22
    if t < 0.22:
        z = 1 / 1.4 + (1.05 - 1 / 1.4) * lib.ease_out(u, 3)
    else:
        v = t - 0.22
        z = 1 + 0.05 * math.exp(-7 * v) * math.cos(2 * math.pi * 2.2 * v)
    rot = -3.0 * (1 - lib.ease_out(t / 0.34, 3)) + 0.8 * math.exp(-6 * max(0, t - .34)) * math.sin(2 * math.pi * 2 * max(0, t - .34))
    h = 0.0
    if t >= hit - 0.04:
        w = t - hit
        h = 0.08 * lib.smooth(-0.04, 0.03, w) * math.exp(-3.2 * max(0, w))
    return cx, cy, s * z * (1 + h), r0 + rot
