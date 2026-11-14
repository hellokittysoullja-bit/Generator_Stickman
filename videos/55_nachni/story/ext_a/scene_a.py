"""Рилс 55 «начни», группа A: Дима, ноутбук, комната.
s01 (0–1.4): ночь, Дима хватается за голову у ноутбука, влёт камеры.
s02 (1.4–4.2): крупно ноутбук с пустым документом, удар ладонью на «отчёт» (1.92), календарь с 7 перечёркнутыми днями; на 2.84 Дима встаёт и садится.
s03 (4.2–7.2): облако-мысль с горой листов, придавливает Диму на «весь» (5.60); на 7.0 заходит кот.
s06 (13.2–15.6): крючок-мысль с оборванной бумагой дёргается на «даёт» (13.90), Дима отмахивается.
s13 (29.3–32.2): день, Дима берёт ноутбук, ставит на стол, садится на «садится» (31.41); кот запрыгивает на соседний стул.
s14 (32.2–34.9): таймер на пять минут (круг с секторами) на «пять» (32.30), на «первую строчку» (33.75) рисуется одна строка.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Герои, комната, кот — из рилса 51 (ext_d), ноутбук и сцены — новые."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import base_d as D  # noqa: E402
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
from lib import (blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rect_pts, shape, smooth,  # noqa: E402
                 svg, back_out, spring)

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))
T = {i: w["start"] for i, w in enumerate(WORDS)}
T_SESTI, T_OTCHET, T_KAZHDY, T_VES, T_DAET = T[4], T[6], T[7], T[14], T[29]
T_SADITSYA, T_PYAT, T_STROCHKU = T[62], T[65], T[69]
_ST = {}
DESK_BACK, DESK_FRONT, BS = D.DESK_BACK, D.DESK_FRONT, D.BS
LAP_X0, LAP_X1 = 470, 790          # основание ноутбука на столе (профиль)
NIGHT_TINT = "#3a4890"


def rnd(k, a=0.0, b=1.0):
    x = math.sin(k * 127.1 + 311.7) * 43758.5453
    return a + (x - math.floor(x)) * (b - a)


def G(inner, tx=0.0, ty=0.0, s=1.0, rot=0.0, extra=""):
    return f'<g transform="translate({f(tx)} {f(ty)}) rotate({f(rot)}) scale({s:.5f})" {extra}>{inner}</g>'


def head_pos(lean, ha=0.0, torso_k=1.0, hip_off=(0, 0), head_off=(0, 0)):
    """Центр головы Димы в мире (та же формула, что people.draw)."""
    H = D.D_HIP + np.array(hip_off, float)
    up = people.rot(np.array([0.0, -1.0]), lean)
    fw = people.rot(np.array([1.0, 0.0]), lean)
    neck = up * (400 * torso_k + 52) + fw * 30
    hp = neck + people.rot(np.array([24.0, -96.0]), lean * .5 + ha) + np.array(head_off, float)
    return H + hp * BS


def hand_spec(curl=.25, d=None, thumb=None):
    h = dict(kind="open", flip=1, dir=(1, .35), curl=(curl, curl, curl, curl * .9), spread=.04 + .12 * (1 - curl),
             thumb=curl if thumb is None else thumb, bend=.1)
    if d:
        h["dir"] = d
    return h


# ═════════════════════════ ноутбук в профиль ═════════════════════════
def laptop_profile(t, glow=1.0, x0=LAP_X0, x1=LAP_X1, y=DESK_BACK + 40, tilt=0.0):
    """Открытый ноутбук на столе, вид сбоку: Дима слева, экран повёрнут к нему. y — линия стола под основанием."""
    o = [blob(ellipse_pts((x0 + x1) / 2 + 14, y + 4, (x1 - x0) / 2 + 40, 10, 16), "#2a1408", .32)]
    base = [(x0, y - 1, 1), (x1 + 4, y - 1, 1), (x1 + 4, y - 20, 1), (x0 + 8, y - 20, 1)]
    o.append(shape(base, "#aeb4c4", blob([(x0, y - 1), (x1 + 4, y - 1), (x1 + 4, y - 9), (x0, y - 9)], "#8a90a4", .9) +
                   blob([(x0 + 8, y - 20), (x1 + 4, y - 20), (x1 + 4, y - 16), (x0 + 8, y - 16)], "#dfe3ee", .9), w=4.2, seed=5001))
    # клавиши — светлая полоса на верхней грани
    for k in range(9):
        kx = x0 + 28 + k * 26
        o.append(blob(rect_pts(kx, y - 19.5, kx + 17, y - 16.8, 1.2), "#59607a", .9))
    a = math.radians(-14 + tilt)                       # экран откинут назад от вертикали
    hx, hy = x1 - 6, y - 20
    L_, th = 330, 17
    dx, dy = math.sin(-a) * L_, -math.cos(a) * L_
    nx, ny = -dy / L_ * th, dx / L_ * th               # нормаль толщины (к Диме)
    lid = [(hx, hy, 1), (hx + dx, hy + dy, 1), (hx + dx + nx, hy + dy + ny, 1), (hx + nx, hy + ny, 1)]
    o.append(shape(lid, "#cfd3df", blob([(hx, hy), (hx + dx, hy + dy), (hx + dx + nx * .3, hy + dy + ny * .3), (hx + nx * .3, hy + ny * .3)], "#a3a9ba", .9),
                   w=4.2, seed=5002))
    # светящаяся грань экрана со стороны Димы (тонкая полоса света)
    ex = [(hx + nx * .95, hy + ny * .95), (hx + dx + nx * .95, hy + dy + ny * .95), (hx + dx + nx * 1.0, hy + dy + ny * 1.0), (hx + nx * 1.0, hy + ny * 1.0)]
    o.append(blob(ex, mix("#bcdcff", "#ffffff", .5), .9 * glow))
    return "".join(o)


def screen_glow(x, y, rx, ry, k, col="#bcdcff"):
    g = rad_grad([(0, col, .55 * k), (.5, col, .2 * k), (1, col, 0)], x, y, rx, ry)
    return f'<rect x="{f(x - rx)}" y="{f(y - ry)}" width="{f(2 * rx)}" height="{f(2 * ry)}" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def laptop_closed(cx, cy, ang, s=1.0):
    """Закрытый ноутбук (тонкая плита, вид сбоку-сверху), центр (cx, cy), угол ang."""
    w, h = 250, 22
    body = shape([(-w / 2, -h / 2, 1), (w / 2, -h / 2, 1), (w / 2, h / 2, 1), (-w / 2, h / 2, 1)], "#bfc4d2",
                 blob([(-w / 2, h / 2 - 8), (w / 2, h / 2 - 8), (w / 2, h / 2), (-w / 2, h / 2)], "#8a90a4", .9) +
                 blob([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, -h / 2 + 5), (-w / 2, -h / 2 + 5)], "#e5e8f1", .9) +
                 blob(ellipse_pts(0, 0, 11, 6, 10), "#8a90a4", .8), w=4.2, seed=5010)
    return G(body, cx, cy, s, ang)


# ═════════════════════════ мир (комната + герои) ═════════════════════════
def world2(t, d, cat_st, cam, *, night=0.0, lamp_rot=0.0, lap="open", lap_glow=1.0, cat=True, between="", extra_front="", cat_pos=None,
           chair2=None, motes=True, chair_dx=0.0, lap_extra="", flame_k=1.0, day_light=False):
    D.set_ink(cam[2])
    D.CAT_POS = cat_pos or (990.0, 1146.0, 0.68)
    w = [_ST["room"], f'<g transform="rotate({lamp_rot:.3f} 700 -400)">{_ST["lamp"]}</g>']
    if chair2:
        w.append(room.chair(chair2[0], chair2[1], -1, 2400))
    w.append(room.chair(D.D_HIP[0] + chair_dx, D.D_HIP[1] + 4, 1, 2300))
    w.append(_ST["legs"])
    w.append(d.get("legs", ""))
    w.append(_ST["top"])
    if lap == "open":
        w.append(laptop_profile(t, lap_glow))
    w.append(lap_extra)
    if cat:
        w.append(D.cat_draw(t, cat_st))
    w.append(d["arm_f"])
    w.append(d["body"])
    w.append(d["arm_n"])
    w.append(between)
    if night > 0:
        g = rad_grad([(0, "#46549e", .35 * night), (.5, "#3a4890", .62 * night), (1, "#1e2260", .88 * night)], 650, 1060, 1000, 1300)
        w.append(f'<rect x="-1600" y="-2200" width="4400" height="3800" fill="url(#{g})" style="mix-blend-mode:multiply"/>')
        w.append(f'<rect x="-1600" y="-2200" width="4400" height="3800" fill="{NIGHT_TINT}" opacity="{.35 * night:.3f}" style="mix-blend-mode:multiply"/>')
    if not day_light:
        w.append(_ST["light"])
    if motes:
        w.append(D.motes(t))
    if lap == "open" and night > 0:
        w.append(screen_glow(640, 1010, 520, 360, lap_glow * night))
    if cat:
        w.append(D.flame_glow(t, cat_st, flame_k))
    w.append(extra_front)
    return f'<g transform="{lib.cam(*cam)}">{"".join(w)}</g>'


# ═════════════════════════ значки ═════════════════════════
def sweat_drop(x, y, t, seed, s=1.0):
    ph = (t * 1.5 + seed * 0.41) % 1.0
    a = math.sin(ph * math.pi) ** .6
    dy = ph * 110 * s
    d = [(0, -34), (10, -12, 1), (14, 4), (0, 14), (-14, 4), (-10, -12, 1)]
    d = [(p[0] * s + x, p[1] * s + y + dy) + ((1,) if len(p) > 2 else ()) for p in d]
    if a < .15:
        return ""
    return shape(d, "#a8dcf5", blob([(x - 2 * s, y + dy - 4 * s), (x + 8 * s, y + dy + 2 * s), (x, y + dy + 10 * s)], "#ffffff", .8), w=3.4 * s, seed=seed + 3)


def stress_marks(x, y, t, k=1.0, col="#e8452c"):
    """Три коротких штриха-лучика вокруг головы (дрожат)."""
    o = []
    for i, ang in enumerate((-150, -110, -70, -30)):
        a = math.radians(ang)
        j = 7 * math.sin(t * 26 + i * 2.1)
        r0, r1 = 150 + j, 210 + j * 1.5
        o.append(line([(x + r0 * math.cos(a) * 1.0, y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))], 11 * k, col, taper=.5,
                      wmin=.2, seed=9100 + i, peak=.5))
    return "".join(o)


def dust(t, t0, x, y, n=7, dur=.5):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return ""
    o = []
    for i in range(n):
        a = -math.pi * (i + .5) / n
        r = 20 + 90 * ease_out(u)
        o.append(f'<circle cx="{x + r * math.cos(a) * 1.3:.1f}" cy="{y + r * math.sin(a) * .6:.1f}" r="{(10 * (1 - u) + 2):.1f}" fill="#f1e7d8"/>')
    return "".join(o)


# ═════════════════════════ облако-мысль ═════════════════════════
def cloud_pts(cx, cy, rx, ry, n=9, seed=0):
    pts = []
    hw = math.pi / n
    for k in range(n):
        ac = 2 * math.pi * k / n
        for da, rr, cor in ((-hw, 0.88, 1), (-hw * .55, 1.08, 0), (0, 1.14 + 0.03 * math.sin(k * 2.3 + seed), 0), (hw * .55, 1.08, 0)):
            a = ac + da
            pts.append((cx + rx * rr * math.cos(a), cy + ry * rr * math.sin(a)) + ((1,) if cor else ()))
    return pts


def sheet_pile(n, t, spread=1.0):
    """Гора листов бумаги (штрихи вместо текста), n штук, в координатах облака (центр 0,0)."""
    o = []
    for i in range(int(n)):
        r = rnd(i + 7)
        x = (r - .5) * 360 * spread + (i % 3 - 1) * 24
        y = 150 - (i * 36) * .8 * (1 if spread < 1.5 else 1) + (rnd(i + 3) - .5) * 24
        ang = (rnd(i + 11) - .5) * 38
        u = clamp(n - i)
        sw = 150 * (0.4 + .6 * u)
        pg = [(-sw / 2, -sw * .66, 1), (sw / 2, -sw * .66, 1), (sw / 2, sw * .66, 1), (-sw / 2, sw * .66, 1)]
        ins = "".join(blob(rect_pts(-sw * .38, -sw * .5 + j * 26, sw * (.38 - (.15 if j % 3 == 2 else 0)), -sw * .5 + 11 + j * 26, 5), "#aeb3c4", .95)
                      for j in range(5))
        o.append(G(shape(pg, "#fffdf6", ins, w=4, seed=9200 + i), x, y + 8 * math.sin(t * 3 + i), 1.0, ang))
    return "".join(o)


def thought_cloud(cx, cy, rx, ry, inner, t, sx=1.0, sy=1.0, rot=0.0, seed=1):
    cl = cloud_pts(0, 0, rx, ry, 9, seed)
    cid = lib.clip_of(cl)
    body = blob(rect_pts(-rx * 1.4, -ry * 1.5, rx * 1.4, ry * 1.5), "#f4f1ff")
    body += blob(rect_pts(-rx * 1.4, ry * .35, rx * 1.4, ry * 1.5), "#dcd8f2", .8)
    art = shape(cl, "#f4f1ff", f'<g clip-path="url(#{cid})">{body}{inner}</g>', w=7, seed=9300 + seed)
    return f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({sx:.4f} {sy:.4f})">{art}</g>'


def bubbles(x0, y0, x1, y1, k, t):
    """Цепочка пузырьков-хвостик от головы к облаку."""
    o = []
    for j, (fr, r_) in enumerate([(.18, 20), (.45, 31), (.76, 44)]):
        u = clamp(k * 3 - j * .6)
        if u <= 0:
            continue
        px, py = x0 + (x1 - x0) * fr, y0 + (y1 - y0) * fr
        o.append(shape(ellipse_pts(px, py, r_ * back_out(u, 2), r_ * back_out(u, 2), 14), "#f4f1ff", "", w=4.6, seed=9400 + j))
    return "".join(o)


# ═════════════════════════ ночной общий кадр ═════════════════════════
def sit_pose(t, lean=.1, ha=0.0, expr=None, n_t=None, f_t=None, hands=None, torso_k=1.0, head_off=(0, 0), hip_off=(0, 0), feet_dx=0.0, sn=-1, sf=-1):
    e = dict(lid=.55, look=(.6, .1), brows="tired", mouth="flat", flush=0.0)
    if expr:
        e.update(expr)
    arms = {"n": ("ik", n_t or (520, DESK_FRONT - 28), sn), "f": ("ik", f_t or (560, DESK_BACK + 4), sf)}
    hands = hands or {"n": hand_spec(.3), "f": hand_spec(.35)}
    return D.dima(lean, arms, hands, e, head_ang=ha, torso_k=torso_k, head_off=head_off, hip_off=hip_off, feet_dx=feet_dx)


def cat_state(t, **kw):
    st = dict(look=(-.9, .1), turn=-.9, blink=0.0, ear=0.0, tail=5 * D.osc(t, .45) + 2 * D.osc(t, 1.3), smile=0, tilt=0.0, perk=0.0, flame_e=1.0)
    st.update(kw)
    return st


# ═════════════════════════ s01 ═════════════════════════
def frame01(t):
    base_z = 1.5
    if t < .22:
        z = base_z / 1.4 + (base_z - base_z / 1.4) * ease_out(t / .22, 3)
    else:
        z = base_z + .13 * ease_io(clamp((t - .22) / 1.4))
    rot = -3.0 * (1 - ease_out(t / .45, 2.5)) + .5 * math.sin(t * 9) * math.exp(-t * 1.5)
    lean = .20 + .03 * math.sin(t * 8)
    ha = .10 + .05 * math.sin(t * 2 * math.pi * 3.2)
    hp = head_pos(lean, ha)
    tug = (6 * math.sin(t * 2 * math.pi * 6.5), 8 * math.sin(t * 2 * math.pi * 5.2 + 1))
    n_t = (hp[0] - 70 + tug[0], hp[1] - 60 + tug[1])
    f_t = (hp[0] - 95 + tug[0] * .7, hp[1] - 100 - tug[1] * .6)
    expr = dict(lid=.92, look=(.55, .25), brows="worry", mouth="tired", flush=.45 * smooth(0, 1, t),
                hair=3.5 * math.sin(t * 31), closed=0.0)
    d = sit_pose(t, lean, ha, expr, n_t, f_t, {"n": hand_spec(.85, (.2, -1)), "f": hand_spec(.85, (.5, -1))}, head_off=(0, 4 * math.sin(t * 20)), sn=1, sf=1)
    hp = d["head"]
    ex = "".join(sweat_drop(hp[0] + dx, hp[1] - 60 + k * 30, t, k + 1, 1.3) for k, dx in enumerate((-120, 130))) if t > .25 else ""
    ex += stress_marks(hp[0] - 20, hp[1] - 30, t) if t > .12 else ""
    cam = (500, 1215, z, rot)
    return world2(t, d, cat_state(t), cam, night=1.0, lamp_rot=3.2 * math.sin(t * 6.5) * math.exp(-t * .3), cat=False,
                  lap_glow=.8 + .2 * math.sin(t * 31), extra_front=ex)


# ═════════════════════════ крупный ноутбук (спереди) ═════════════════════════
DOC = "#f8f6ef"


def kbd_front(press=None):
    """Палуба ноутбука вид спереди (перспектива), press — {(row, col): глубина}."""
    o = []
    deck = [(-430, 40, 1), (430, 40, 1), (506, 340, 1), (-506, 340, 1)]
    o.append(shape(deck, "#c3c8d6", blob([(-430, 40), (430, 40), (440, 70), (-440, 70)], "#aeb3c4", .9), w=5.4, seed=5101))
    for r in range(4):
        y0, y1 = 70 + r * 62, 70 + r * 62 + 50
        for c in range(12):
            def X(yy, u):
                wy = 430 + (yy - 40) * (76 / 300)
                return -wy * .94 + 2 * wy * .94 * u
            u0, u1 = c / 12 + .004, (c + 1) / 12 - .004
            pr = (press or {}).get((r, c), 0.0)
            dy = 5 * pr
            ky0, ky1 = y0 + dy, y1 + dy
            o.append(blob([(X(ky0, u0), ky0, 1), (X(ky0, u1), ky0, 1), (X(ky1, u1), ky1, 1), (X(ky1, u0), ky1, 1)], "#aeb3c4"))
            o.append(blob([(X(ky0, u0), ky0 - 5 + dy * .3, 1), (X(ky0, u1), ky0 - 5 + dy * .3, 1), (X(ky1, u1), ky1 - 8, 1), (X(ky1, u0), ky1 - 8, 1)],
                          "#f1f3f9" if pr < .3 else "#ffe9a8"))
    o.append(shape(rect_pts(-96, 286, 96, 328, 10), "#d6dae6", "", w=3.6, seed=5102))
    o.append(shape([(-506, 340, 1), (506, 340, 1), (498, 362, 1), (-498, 362, 1)], "#8d93a7", "", w=4.4, seed=5103))
    return "".join(o)


def screen_front(t, doc_fn=None):
    o = [shape(rect_pts(-436, -540, 436, 50, 40), "#2c2f3d", "", w=6.4, seed=5110)]
    cid = lib.clip_rect(-404, -508, 808, 526, 22)
    c = [blob(rect_pts(-404, -508, 404, 18), DOC)]
    c.append(blob(rect_pts(-404, -508, 404, -440), "#e1e4ee"))
    for k, x in enumerate((-370, -336, -302)):
        c.append(blob(ellipse_pts(x, -474, 9, 9, 10), ("#e8685a", "#f0c24e", "#6cc07a")[k]))
    for k, (x0, x1) in enumerate([(-160, -60), (-30, 70), (100, 180), (210, 330)]):
        c.append(blob(rect_pts(x0, -482, x1, -466, 8), "#a9aec0"))
    c.append(blob(rect_pts(-404, -440, 404, -428), "#cfd3e0", .6))
    # поля страницы
    c.append(blob(rect_pts(-300, -396, -296, 18), "#e9e6dc", .8))
    if doc_fn:
        c.append(doc_fn())
    o.append(f'<g clip-path="url(#{cid})">{"".join(c)}</g>')
    o.append(f'<g clip-path="url(#{cid})">' + blob([(-404, -508), (-120, -508), (-404, -250)], "#ffffff", .16) + "</g>")
    o.append(shape(ellipse_pts(0, -526, 7, 7, 10), "#171822", "", w=2.4, seed=5111))
    return "".join(o)


def laptop_front(t, doc_fn=None, press=None):
    return screen_front(t, doc_fn) + kbd_front(press)


def sleeve_band(a, b, w0, w1, seed):
    pts = lib.band([tuple(a), tuple(b)], w0, w1, step=6, cap=False)
    ins = blob([(p[0], p[1]) for p in lib.band([tuple(a), tuple(b)], w0 * .35, w1 * .35, step=6, cap=False)], D.HOOD_SH if hasattr(D, "HOOD_SH") else "#a97b25", .0)
    return shape(pts, D.HOOD, ins, w=6, seed=seed)


def hand_front(wr, ang, k=1.9, curl=.45, spread=.18, side=1, seed=0, sleeve_from=None):
    """Кисть сверху-спереди: запястье wr, пальцы направлены по ang (град, 0 = вправо, -90 = вверх); рукав уходит вниз за кадр."""
    people.C = people.PAL["dima"]
    kw = people.hand_kw()
    a = math.radians(ang)
    d = np.array([math.cos(a), math.sin(a)])
    wr = np.array(wr, float)
    o = []
    s0 = wr - d * 60
    far = wr - d * 900
    o.append(shape(lib.band([tuple(far), tuple(s0 + d * 20)], 250, 215, step=8, cap=False), D.HOOD,
                   "".join(line([tuple(s0 - d * (60 + 90 * j) + np.array([-d[1], d[0]]) * 110), tuple(s0 - d * (60 + 90 * j) - np.array([-d[1], d[0]]) * 90)], 4,
                                D.FOLD, seed=seed + j, op=.7) for j in range(4)), w=6, seed=seed + 20))
    cuff = lib.band([tuple(wr - d * 130), tuple(wr - d * 18)], 200, 190, step=6, cap=False)
    o.append(shape(cuff, D.HOOD_SH, "", w=5, seed=seed + 30))
    o.append(Hand.hand(wr + d * 2, d, flip=side, k=k, curl=(curl, curl * .9, curl, curl * 1.05), spread=spread, thumb=.35, bend=.1, seed=seed + 40, **kw))
    return "".join(o)


def calendar_note(t, t0, cx, cy, s=1.0):
    """Листок-календарь (7 клеток в ряд, без цифр), дни по очереди перечёркиваются красным."""
    u = clamp((t - t0) / .28)
    if u <= 0:
        return ""
    o = []
    pg = [(-300, -110, 1), (300, -110, 1), (300, 120, 1), (-300, 120, 1)]
    inner = blob(rect_pts(-300, -110, 300, -50), "#d6564a")
    for k in range(7):
        x0 = -280 + k * 80
        inner += blob(rect_pts(x0, -30, x0 + 66, 100, 8), "#f1ede0")
        inner += line([(x0 + 10, -4), (x0 + 36, -4)], 5, "#a9aec0", taper=.1, wmin=.9, seed=9500 + k)
        # перечёркивание
        a = T_CAL + k * .13
        v = clamp((t - a) / .13)
        if v > 0:
            p1 = [(x0 + 8, -12), (x0 + 8 + 50 * min(1, v * 2), -12 + 100 * min(1, v * 2))]
            inner += line(p1, 12, "#d6322c", taper=.2, wmin=.7, seed=9510 + k)
            if v > .5:
                w2 = (v - .5) * 2
                inner += line([(x0 + 58, -12), (x0 + 58 - 50 * w2, -12 + 100 * w2)], 12, "#d6322c", taper=.2, wmin=.7, seed=9520 + k)
    o.append(shape(pg, "#fffdf6", inner, w=5.6, seed=9530))
    o.append(shape(ellipse_pts(0, -112, 14, 14, 10), "#c9ced9", "", w=3.6, seed=9531))
    k = back_out(u, 2.0)
    return G("".join(o), cx, cy + 30 * (1 - k), s * k, -2.5)


T_CAL = 1.78


def closeup_bg(t, mode="night"):
    if mode == "night":
        g = lib.lin_grad([(0, "#3b365f", 1), (1, "#201e3a", 1)], 0, 0, 0, 1)
        o = [f'<rect x="-200" y="-200" width="1500" height="2400" fill="url(#{g})"/>']
        o.append(f'<rect x="-200" y="1000" width="1500" height="1000" fill="#7a5238"/><rect x="-200" y="990" width="1500" height="16" fill="#5a3a26"/>')
        o.append(screen_glow(540, 700, 800, 700, .7))
        o.append(D.motes(t, 3, 20, (0, 100, 1080, 1000)))
    else:
        o = ['<rect x="-200" y="-200" width="1500" height="2400" fill="#a9c3c0"/>']
        o.append('<rect x="-200" y="1020" width="1500" height="1000" fill="#c88a58"/><rect x="-200" y="1010" width="1500" height="14" fill="#8f5f36"/>')
        g = rad_grad([(0, "#fff0c0", .5), (1, "#fff0c0", 0)], 700, 400, 800, 800)
        o.append(f'<rect x="-200" y="-200" width="1500" height="1200" fill="url(#{g})" style="mix-blend-mode:screen"/>')
        o.append(D.motes(t, 4, 20, (0, 100, 1080, 1000)))
    return "".join(o)


# ═════════════════════════ s02 ═════════════════════════
def frame02_close(t):
    D.set_ink(1.0)
    u = clamp((t - 1.2) / 1.7)
    z = 1.0 + .12 * ease_io(u)
    hit = t - T_OTCHET
    sh = math.exp(-hit * 9) * (1 if hit >= 0 else 0)
    shx, shy = 14 * sh * math.sin(hit * 70), 18 * sh * math.sin(hit * 55 + 1)
    cam = lib.cam(540 + shx, 900 + shy + 20 * (1 - u), z, -1.5 * sh * math.sin(hit * 40) + .6 * math.sin(t * 2.2))
    o = [closeup_bg(t, "night")]
    # ноутбук подпрыгивает от удара
    lift = -22 * sh if hit >= 0 else 0
    cur_on = int(t * 2.2) % 2 == 0
    cursor = lambda: (blob(rect_pts(-296, -392, -290, -350), "#2f6bd6") if cur_on else "")
    lap = laptop_front(t, cursor)
    o.append(G(lap, 540, 760 + lift, .98))
    # руки: зависают, дёргаются назад на «сесть», правая бьёт на «отчёт»
    back = smooth(T_SESTI - .06, T_SESTI + .1, t) * (1 - smooth(T_SESTI + .1, T_SESTI + .5, t))
    hov = 7 * math.sin(t * 2 * math.pi * 2.6)
    # левая
    lx, ly = 330, 1180 + hov + 120 * back
    o.append(hand_front((lx, ly), -80, 1.9, .45, .2, 1, 3000))
    # правая: замах → удар
    wind = smooth(T_OTCHET - .32, T_OTCHET - .04, t) * (1 - smooth(T_OTCHET - .04, T_OTCHET + .0, t))
    slam = smooth(T_OTCHET - .04, T_OTCHET + .05, t) * (1 - smooth(T_OTCHET + .08, T_OTCHET + .5, t))
    rx, ry = 760, 1170 + 7 * math.sin(t * 2 * math.pi * 2.3 + 1) - 150 * wind + 120 * slam + 120 * back
    o.append(hand_front((rx, ry), -100, 1.9 + .1 * slam, .15 + .45 * (1 - slam), .35, -1, 3100))
    o.append(dust(t, T_OTCHET + .02, 760, 1290))
    o.append(calendar_note(t, 1.62, 540, 165, .9))
    if hit >= 0 and hit < .3:
        a = 1 - hit / .3
        for i in range(6):
            an = math.radians(-160 + i * 28)
            r0, r1 = 160 + 120 * hit * 3, 260 + 160 * hit * 3
            o.append(line([(760 + r0 * math.cos(an), 1240 + r0 * math.sin(an) * .5), (760 + r1 * math.cos(an), 1240 + r1 * math.sin(an) * .5)],
                          12, "#fff3c4", taper=.5, wmin=.1, seed=9600 + i, op=a))
    return f'<g transform="{cam}">{"".join(o)}</g>'


def frame02_wide(t):
    """Дима встаёт (2.84) и снова садится."""
    up = smooth(T_KAZHDY, T_KAZHDY + .32, t)
    dn = smooth(3.55, 3.95, t)
    st = up * (1 - dn)                                  # 1 — стоит
    bump_ = math.exp(-(t - 3.95) * 11) * math.sin(max(0, (t - 3.95)) * 30) * (1 if t > 3.95 else 0)
    lean = .16 * (1 - st) + .02 * st + .02 * bump_
    hip_off = (75 * st, -150 * st + 8 * bump_)
    feet_dx = -145 * st
    hd = hand_spec(.4)
    n_t = (520, DESK_FRONT - 28) if st < .5 else (250 + 90, 1262 - 150 + 250)
    n_t = (520 * (1 - st) + 380 * st, (DESK_FRONT - 28) * (1 - st) + 1180 * st)
    f_t = (560 * (1 - st) + 400 * st, (DESK_BACK + 4) * (1 - st) + 1160 * st)
    expr = dict(lid=.7, look=(.5, .1), brows="worry" if st > .1 else "tired", mouth="talk" if st > .2 else "flat", open=.3, flush=.4)
    d = sit_pose(t, lean, 0.03 * math.sin(t * 9) * st, expr, n_t, f_t, {"n": hand_spec(.5), "f": hand_spec(.5)}, hip_off=hip_off, feet_dx=feet_dx)
    zp = 1.0 + .02 * math.exp(-(t - T_KAZHDY) * 5) if t > T_KAZHDY else 1
    u = clamp((t - 2.8) / 1.6)
    cam = (570, 1160, 1.18 + .06 * ease_io(u), -1.0 * (1 - u))
    ex = dust(t, 3.95, 330, 1260, 6)
    return world2(t, d, cat_state(t), cam, night=1.0, lamp_rot=2.5 * math.sin(t * 5), cat=False, lap_glow=.9, extra_front=ex)


def frame02(t):
    if t < T_KAZHDY - .02:
        return frame02_close(t)
    return frame02_wide(t)


# ═════════════════════════ s03 ═════════════════════════
T_CLOUD0 = T[11] - .1          # «начинать»
T_ENTER = 7.0


def frame03(t):
    grow = smooth(T[11], T_VES - .1, t)                           # облако растёт
    press = clamp((t - T_VES) / .9)
    hit = ease_out(clamp((t - T_VES) / .16), 3)
    sag = hit * (.55 + .12 * math.sin(clamp(t - T_VES, 0, 3) * 4) * math.exp(-(t - T_VES) * 2)) if t > T_VES else 0
    lean = .08 + .06 * grow + .46 * sag
    head_off = (0, 70 * sag)
    torso_k = 1 - .10 * sag
    ha = .02 + .16 * sag
    hp = head_pos(lean, ha, torso_k, head_off=head_off)
    tn = (520 + 30 * sag, DESK_FRONT - 28)
    d = sit_pose(t, lean, ha, dict(lid=.7 - .35 * sag, look=(.5, .2), brows="worry", mouth="flat", flush=.25 * sag), tn,
                 (560 + 40 * sag, DESK_BACK + 8), {"n": hand_spec(.4 + .4 * sag), "f": hand_spec(.4)}, torso_k=torso_k, head_off=head_off)
    # облако
    ccx = 400
    base_cy = 520
    top_of_head = hp[1] - 190 * BS * 1.0
    k = ease_out(grow, 2.2)
    rx, ry = 255 * k + 8, 190 * k + 6
    cy = min(base_cy, top_of_head - ry * 1.1) if k > .4 else top_of_head - 150 - 220 * k
    cy = top_of_head - ry * 1.12 - 130 * (1 - sag) * grow + 20 * sag
    sq = 1.0
    sx = 1 + .16 * sag * (1 if True else 0)
    sy = 1 - .26 * sag
    pile = sheet_pile(8 * smooth(T[11] + .1, T_VES, t), t, 1.0)
    inner = G(pile, 0, 20, 1.2, 0)
    cl = ""
    if k > .02:
        shake = 6 * math.sin(t * 40) * math.exp(-(t - T_VES) * 6) if t > T_VES else 2 * math.sin(t * 13) * grow
        cl = thought_cloud(ccx + shake, cy + ry * (1 - sy) * .5, rx, ry, inner, t, sx, sy, 2.0 * math.sin(t * 3) * (1 - sag))
        cl = bubbles(hp[0] - 10, hp[1] - 170 * BS, ccx, cy + ry * 1.1, grow, t) + cl
    # кот заходит
    ent = clamp((t - T_ENTER) / .55)
    cx_ = 1500 - 560 * ease_out(ent, 2.2)
    ex_front = cl
    cat_on = t >= T_ENTER - .6
    walk = (1 - ent) > 0
    st = cat_state(t, tail=8 * D.osc(t, 1.2) + 3, look=(-.8, .2), turn=-.8 + .4 * ent, ear=4 * D.bump(t, 7.3, .4),
                   tilt=-3 * D.bump(t, 7.35, .6))
    u = clamp((t - 4.0) / 3.4)
    thump = math.exp(-(t - T_VES) * 8) * math.sin((t - T_VES) * 55) * (1 if t > T_VES else 0)
    cam = (500 + 40 * u + 8 * thump, 1000 + 70 * u + 22 * thump, 1.0 + .13 * ease_io(u), -.5 + .6 * u + .6 * thump)
    cp = (cx_, 1146 - 14 * math.sin(math.pi * clamp(ent * 4 % 1)) * (1 if ent < 1 else 0), .68)
    return world2(t, d, st, cam, night=1.0, lamp_rot=2.0 * math.sin(t * 3.1), cat=cat_on, cat_pos=cp, lap_glow=.9, extra_front=ex_front)


# ═════════════════════════ s06 ═════════════════════════
def hook_art(t, jerk):
    """Большой крючок с оборванной бумагой (в координатах облака)."""
    o = []
    ring = [(0 + 26 * math.cos(a), -215 + 26 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 18)]
    o.append(line(ring, 30, lib.INK, taper=.02, wmin=.98, seed=9700))
    o.append(line(ring, 18, "#c4c9d6", taper=.02, wmin=.98, seed=9701))
    shaft = [(0, -190), (0, -90), (0, 20), (2, 70)]
    curve = [(2 + 100 * (1 - math.cos(a)) * -.0 + (-95 + 95 * math.cos(a)) * 1.0 + 95 * 0, 70 + 95 * math.sin(a)) for a in np.linspace(0, math.pi * 1.2, 14)]
    pts = shaft + [(p[0], p[1]) for p in curve]
    o.append(line(pts, 40, lib.INK, taper=.02, wmin=.96, seed=9702))
    o.append(line(pts, 27, "#c4c9d6", taper=.02, wmin=.96, seed=9703))
    o.append(line([(-8, -180), (-8, 40)], 8, "#f4f6fb", taper=.3, wmin=.5, seed=9704, op=.9))
    # оборванная бумага, зацепившаяся на конце: мотается
    fl = 9 * math.sin(t * 9) + 20 * jerk
    tipx, tipy = curve[-1]
    pg = [(-52, -8, 1), (52, -8, 1), (56, 100), (38, 128, 1), (24, 96), (6, 138, 1), (-12, 100), (-30, 142, 1), (-46, 104), (-58, 132, 1), (-56, 40)]
    ins = "".join(blob(rect_pts(-38, 14 + j * 24, 36 - (12 if j == 2 else 0), 24 + j * 24, 5), "#aeb3c4", .95) for j in range(3))
    o.append(G(shape(pg, "#fffdf6", ins, w=4.4, seed=9710), tipx - 4, tipy + 10, 1.0, fl))
    return "".join(o)


def frame06(t):
    jt = t - T_DAET
    jerk = math.exp(-jt * 6) * math.sin(jt * 38) if jt >= 0 else 0.0
    wave_a = smooth(14.05, 14.35, t) * (1 - smooth(14.95, 15.3, t))
    wv = math.sin((t - 14.2) * 2 * math.pi * 3.4)
    lean = .12 - .05 * wave_a + .04 * (1 if jt >= 0 else 0) * math.exp(-jt * 3) * (1 if jt >= 0 else 0)
    ha = .03 * math.sin(t * 2.0) - .06 * wave_a
    hp = head_pos(lean, ha)
    n_t = (520 * (1 - wave_a) + (hp[0] + 150 + 55 * wv) * wave_a, (DESK_FRONT - 28) * (1 - wave_a) + (hp[1] - 60 + 25 * abs(wv)) * wave_a)
    expr = dict(lid=.8, look=(.4, .4), brows="worry" if jt < .0 else "det", mouth="flat" if wave_a < .1 else "talk", open=.25, flush=.15 + .3 * wave_a)
    d = sit_pose(t, lean, ha, expr, n_t, (560, DESK_BACK + 6), {"n": hand_spec(.4 - .3 * wave_a), "f": hand_spec(.4)})
    hp = d["head"]
    # крючок-мысль над головой; дёргается на «даёт», при отмахивании улетает и возвращается
    away = smooth(14.25, 14.6, t) * (1 - smooth(14.85, 15.35, t))
    appear = smooth(13.15, 13.55, t)
    bx = hp[0] + 170 + 170 * away * .4 + 10 * jerk
    by = hp[1] - 420 - 60 * (1 - appear) - 40 * away + 14 * abs(jerk)
    rot = 10 * jerk + 7 * wave_a * wv * (1 if t < 15 else 0) + 2 * math.sin(t * 3)
    sc = (.88 + .12 * back_out(appear, 2.0)) * (1 + .1 * jerk * 0)
    cl = ""
    if appear > .02:
        inner = G(hook_art(t, jerk), 0, 12, 1.0, 0)
        cl = bubbles(hp[0] + 10, hp[1] - 150, bx - 20, by + 240 * sc, appear, t)
        cl += thought_cloud(bx, by, 285 * sc, 250 * sc, inner, t, 1 + .05 * abs(jerk), 1 - .05 * abs(jerk), rot, seed=3)
    st = cat_state(t, look=(-.5 + .5 * math.sin(t * 1.3) * 0, -.2), turn=-.55, ear=5 * D.bump(t, T_DAET, .4), tilt=-4 * smooth(13.4, 13.9, t),
                   perk=.4 * smooth(13.2, 13.8, t), blink=D.Cat_blink(t, [(14.9, .06, .0)]))
    cam = (560 + 14 * math.sin(t * 1.7), 960 + 10 * math.sin(t * 1.3) + 14 * jerk * 0, 1.0 + .08 * ease_io(clamp((t - 13.0) / 2.6)) + .02 * math.exp(-jt * 8) * (jt >= 0),
           1.2 * math.sin(t * 1.9) + .8 * jerk)
    return world2(t, d, st, cam, night=.85, lamp_rot=1.6 * math.sin(t * 2.6), cat=True, cat_pos=(1010, 1146, .68), lap_glow=.9, extra_front=cl)


# ═════════════════════════ s13 (день) ═════════════════════════
def frame13(t):
    T0 = 29.1
    seat = smooth(30.95, T_SADITSYA, t)                    # садится ровно к 31.41
    grab = smooth(29.5, 29.95, t)
    put = smooth(30.1, 30.55, t)
    # ноутбук: у груди → на стол
    lx = 330 + 330 * put - 20 * (1 - grab)
    ly = 1020 * (1 - put) + (DESK_BACK + 40 - 12) * put - 28 * math.sin(math.pi * put)
    lang = -8 * (1 - put) + 0 * put
    # Дима стоит у стула слева от стола, потом садится
    st = 1 - seat
    plop = math.exp(-(t - T_SADITSYA) * 10) * math.sin((t - T_SADITSYA) * 34) * (1 if t > T_SADITSYA else 0)
    lean = .02 * st + .12 * (1 - st) + (.22 * math.sin(math.pi * seat) if seat < 1 else 0) * 0.5 + .03 * plop
    hip_off = (75 * st, -150 * st + 8 * plop)
    feet_dx = -145 * st
    lk = (lx - 125 * 0, ly)
    hpos_n = (lx - 105, ly + 4) if put < 1 else (LAP_X0 + 60, DESK_FRONT - 30)
    n_t = (hpos_n[0] * (1 - seat) + (520) * seat, hpos_n[1] * (1 - seat) + (DESK_FRONT - 28) * seat)
    f_t = ((lx + 105) * (1 - seat) + 560 * seat, (ly + 6) * (1 - seat) + (DESK_BACK + 4) * seat)
    if seat > .99:
        n_t, f_t = (520, DESK_FRONT - 28), (560, DESK_BACK + 4)
    expr = dict(lid=.75, look=(.55, .1), brows="det" if seat < .6 else "calm", mouth="flat" if seat < .8 else "smile", smile=.5, flush=0.0, blush=.3 * seat)
    d = sit_pose(t, lean, .03 * math.sin(t * 6) * st, expr, n_t, f_t, {"n": hand_spec(.55), "f": hand_spec(.55)}, hip_off=hip_off, feet_dx=feet_dx)
    lap_extra = ""
    lap = "open" if put >= 1 and t > 30.6 else "none"
    if lap == "none":
        lap_extra = laptop_closed(lx, ly, lang)
    else:
        op = smooth(30.6, 31.1, t)
    # кот запрыгивает на соседний стул
    j = clamp((t - 30.45) / .55)
    cx0, cy0 = 1180, 1470
    cx1, cy1 = 1060, 1262
    cx_ = cx0 + (cx1 - cx0) * j
    cy_ = cy0 + (cy1 - cy0) * ease_out(j, 1.6) - 180 * math.sin(math.pi * j)
    land = math.exp(-(t - 31.0) * 9) * math.sin((t - 31.0) * 30) * (1 if t > 31.0 else 0)
    cat_in = t > 30.35
    ground_cat = t <= 30.45
    ck = .68 * (1 + .04 * land)
    cst = cat_state(t, look=(-.8, .1), turn=-.7, tail=7 * D.osc(t, 1.0), blink=D.Cat_blink(t, [(31.9, .06, 0)]), ear=4 * D.bump(t, 31.0, .4),
                    smile=1 if t > 31.6 else 0, flame_e=1.2)
    cam = (640 + 24 * (1 - clamp((t - T0) / 3.1)), 1130, 1.0 + .16 * ease_io(clamp((t - T0) / 3.1)), -1.0 * (1 - clamp((t - T0) / 3.1)))
    out = world2(t, d, cst, cam, night=0.0, lamp_rot=1.2 * math.sin(t * 2.4), lap=lap, lap_extra=lap_extra, cat=cat_in, cat_pos=(cx_, cy_, ck),
                 chair2=(1060, 1262), motes=True, day_light=True, lap_glow=.4)
    # хлёст: горизонтальное размытие в первые 0.3 с
    wp = ease_out(clamp(1 - (t - T0) / .32), 2)
    if wp > .02:
        fid = "whip1"
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-5%" width="140%" height="110%"><feGaussianBlur stdDeviation="{f(70 * wp)} 0"/></filter>')
        out = f'<g filter="url(#{fid})" transform="translate({f(-260 * wp)} 0)">{out}</g>'
    return out


# ═════════════════════════ s14 ═════════════════════════
def timer_art(t, k):
    """Кухонный таймер: круг с пятью секторами, без цифр. k — появление; сектора зажигаются на «пять»."""
    o = []
    cols = ["#e8685a", "#f0a04a", "#f2cf5a", "#7dbf7a", "#5a9bd8"]
    face = ellipse_pts(0, 0, 150, 150, 36)
    inner = ""
    for i in range(5):
        a0, a1 = -90 + i * 72, -90 + (i + 1) * 72
        on = clamp((t - (T_PYAT - .02 + .1 * i)) / .12)
        pts = [(0, 0)] + [(150 * math.cos(math.radians(a)), 150 * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 10)]
        col = mix("#e7e1d3", cols[i], on)
        inner += blob(pts, col)
        inner += line([(0, 0), (150 * math.cos(math.radians(a0)), 150 * math.sin(math.radians(a0)))], 5, lib.INK, taper=.05, wmin=.95, seed=9800 + i)
    inner += blob(ellipse_pts(0, 0, 52, 52, 20), "#fffaf0")
    o.append(shape(face, "#f6f0e2", inner, w=7, seed=9810))
    sw = ((t - (T_PYAT + .6)) / 2.0) % 1.0 if t > T_PYAT + .6 else 0.0
    ang = -90 + 72 * 5 * 0 + 360 * sw * 0.15
    o.append(line([(0, 0), (112 * math.cos(math.radians(ang)), 112 * math.sin(math.radians(ang)))], 14, lib.INK, taper=.1, wmin=.8, seed=9811))
    o.append(shape(ellipse_pts(0, 0, 22, 22, 14), "#d6322c", "", w=4.6, seed=9812))
    # колпачок сверху и ножки
    o.append(shape(rect_pts(-36, -190, 36, -150, 10), "#d6322c", "", w=5, seed=9813))
    return G("".join(o), 0, 0, k, 0)


def line_on_screen(t):
    """Одна строка, прорисовывается по словам (серые закруглённые штрихи) и каретка."""
    words = [(-290, 110), (-165, 70), (-80, 150), (88, 90), (190, 70)]
    o = []
    a = T_STROCHKU
    tot = clamp((t - a) / 0.9)
    end_x = -290
    for k, (x0, w_) in enumerate(words):
        u = clamp(tot * len(words) - k)
        if u > 0:
            o.append(blob(rect_pts(x0, -352, x0 + w_ * u, -330, 10), "#4a4f68"))
            end_x = x0 + w_ * u
    if int(t * 3) % 2 == 0 or tot < 1:
        o.append(blob(rect_pts(end_x + 6, -362, end_x + 12, -322), "#2f6bd6"))
    return "".join(o)


def frame14(t):
    u = clamp((t - 32.0) / 3.0)
    z = 1.0 + .14 * ease_io(u)
    cam = lib.cam(540 + 20 * (u - .5), 900 + 30 * (1 - u), z, .7 * (1 - u) - .3)
    D.set_ink(z)
    o = [closeup_bg(t, "day")]
    typing = smooth(T_PYAT + .35, T_PYAT + .6, t)
    press = {}
    for i in range(14):
        ph = t * 9 + i * 2.1
        r_, c_ = int(rnd(int(ph) * 3 + i) * 4), int(rnd(int(ph) * 5 + i + 3) * 12)
        press[(r_, c_)] = typing * max(0.0, 1 - (ph % 1) * 1.6) if i < 5 else 0
    lap = laptop_front(t, lambda: line_on_screen(t), press)
    o.append(G(lap, 560, 700, .94))
    # таймер слева, выскакивает на «пять»
    tk = back_out(clamp((t - T_PYAT + .05) / .3), 2.2) if t > T_PYAT - .05 else 0
    if tk > .01:
        wob = 1 + .05 * math.sin((t - T_PYAT) * 20) * math.exp(-(t - T_PYAT) * 4)
        o.append(G(timer_art(t, tk * wob * .85), 178, 1000))
    # руки печатают
    bob = lambda ph: (6 * math.sin(t * 2 * math.pi * 4.5 + ph)) * typing
    hov = 5 * math.sin(t * 3)
    o.append(hand_front((360, 1190 + bob(0) + hov), -78, 1.9, .5 + .1 * math.sin(t * 25) * typing, .22, 1, 3200))
    o.append(hand_front((780, 1195 + bob(2) + hov), -102, 1.9, .5 + .1 * math.sin(t * 27 + 1) * typing, .3, -1, 3300))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ═════════════════════════ вход ═════════════════════════
def frame(sid, t):
    if not _ST:
        D.DAY[0] = sid in ("s13",)
        D.static_all()
        _ST["room"], _ST["legs"], _ST["top"], _ST["light"], _ST["lamp"] = D._ST["room"], D._ST["legs"], D._ST["top"], D._ST["light"], D._ST["lamp"]
    lib.dyn_begin()
    body = {"s01": frame01, "s02": frame02, "s03": frame03, "s06": frame06, "s13": frame13, "s14": frame14}[sid](t)
    return svg(f'<rect width="1920" height="1920" fill="#2a1f2a"/>{body}')
