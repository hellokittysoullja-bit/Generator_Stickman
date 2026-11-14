"""Сцена walk рилса 43 (s12, 21.3–23.44, клип 21.1–23.64): коридор квартиры утром (коридор рилса 37, s16). Дима (рилсы
23–41: лохматый, щетина, мешки, горчичное худи, синие тапки) бредёт зомби слева направо: глаза почти закрыты, голова
свешена, руки вытянуты вперёд, в ближней — кружка. Над головой батарейка с одним красным делением мигает. На
«невыспавшимся» (22.32) он врезается лбом в косяк дверного проёма кухни: кружка выплёскивает кофе, голова откидывается,
вокруг головы кружат звёздочки, батарейка пустеет; камера трясётся.
Слои: ноги, дальняя рука, тело и голова, КОСЯК, ближняя рука с кружкой (рука проходит перед косяком, голова — за ним).
Мир: пол y = 0, x вправо. Ступня в опоре стоит в мире; после удара ноги стоят."""
import math

import numpy as np

import flatlib as F
import lib
from flatlib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, smooth

T_A = 21.10
T_HIT = F.word("невыспавшимся", 22.0)      # 22.32
BS = 0.62
TC = 0.66                    # шаг (с) — медленнее обычного
ST = 0.42
STEP = 150.0
V = STEP / TC
HIP_H = (F.people.THIGH + F.people.SHIN) * BS * 0.985 + F.people.AH * BS * 0.4
WALL_TOP = -1500.0
XJ = None                    # левая кромка косяка (считается по положению лица в момент удара)
_ST = {}

# ───────────────────────────── коридор
def corridor(x0, x1, skip=None):
    s = []
    wall, wall_sh = "#b9d0c4", "#9ab5a8"
    s.append(f'<rect x="{x0:.0f}" y="{WALL_TOP - 600:.0f}" width="{x1 - x0:.0f}" height="{-WALL_TOP + 640:.0f}" fill="{wall}"/>')
    # обои: тонкие вертикальные полосы и мелкий ромбик
    lib.DEFS.append('<pattern id="pWall37" width="64" height="64" patternUnits="userSpaceOnUse">'
                    f'<rect width="64" height="64" fill="{wall}"/><rect x="0" width="6" height="64" fill="{wall_sh}" opacity=".55"/>'
                    '<path d="M32 26 L36 32 L32 38 L28 32Z" fill="#f2efe2" opacity=".7"/></pattern>')
    s.append(f'<rect x="{x0:.0f}" y="{WALL_TOP:.0f}" width="{x1 - x0:.0f}" height="{-WALL_TOP - 260:.0f}" fill="url(#pWall37)"/>')
    # панель снизу (вагонка) и молдинг
    s.append(shape(rect_pts(x0, -260, x1, -10), "#f1e6cf", "".join(
        line([(x, -250), (x, -14)], 2.4, "#d2c3a4", taper=.05, wmin=.9, seed=4100 + int(x) % 97, op=.9)
        for x in np.arange(math.floor(x0 / 70) * 70, x1, 70)), w=4, seed=4101))
    s.append(shape(rect_pts(x0, -276, x1, -252), "#e2d3b3", "", w=3.8, seed=4102))
    s.append(shape(rect_pts(x0, -34, x1, 0), "#cdb58c", "", w=4, seed=4103))
    # предметы на стене по x (повторяются с шагом 1500)
    for k in range(int(math.floor(x0 / 1500)) - 1, int(math.ceil(x1 / 1500)) + 1):
        bx = k * 1500
        if skip is None or not (skip[0] < bx + 520 and bx + 90 < skip[1]):
            s.append(door(bx + 120, k))
        s.append(frame_pic(bx + 760, -980, k))
        s.append(hooks(bx + 1120, k))
    # пол: доска + дорожка
    s.append(shape(rect_pts(x0, 0, x1, 900), "#c99d6c", "".join(
        line([(x0, 40 + j * 70 + j * j * 6), (x1, 40 + j * 70 + j * j * 6)], 3, "#a97f52", taper=.05, wmin=.9, seed=4110 + j, op=.8)
        for j in range(6)), w=4.4, seed=4111))
    s.append(shape(rect_pts(x0, 46, x1, 150), "#6f8f9e", blob(rect_pts(x0, 46, x1, 62), "#a7c3cc", .9) +
                   blob(rect_pts(x0, 134, x1, 150), "#a7c3cc", .9) + blob(rect_pts(x0, 120, x1, 150), "#4f6c7a", .5), w=4, seed=4112))
    return "".join(s)


def door(x, k):
    s = []
    w, h = 380, 860
    s.append(shape(rect_pts(x - 26, -h - 26, x + w + 26, 0), "#f4efe4", blob(rect_pts(x + w, -h - 26, x + w + 26, 0), "#d9d1c0", .9),
                   w=4.4, seed=4200 + k))
    inner = blob(rect_pts(x + w - 60, -h, x + w, 0), "#a8774c", .8)
    for j, (a, b) in enumerate(((-h + 60, -h + 400), (-h + 460, -60))):
        inner += shape(rect_pts(x + 50, a, x + w - 50, b, 8), "#c38d5c", blob(rect_pts(x + w - 70, a, x + w - 50, b), "#a8774c", .8),
                       w=3.2, seed=4210 + j + k)
    s.append(shape(rect_pts(x, -h, x + w, 0), "#c99566", inner, w=4.6, seed=4220 + k))
    s.append(shape(ellipse_pts(x + w - 50, -430, 15, 15, 12), "#e2b84a", blob(ellipse_pts(x + w - 46, -426, 9, 9, 8), "#b98d2a"), w=3,
                   seed=4230 + k))
    return "".join(s)


def frame_pic(x, y, k):
    rs = np.random.RandomState(4300 + k)
    w, h = 300, 220
    inner = f'<rect x="{x - 20}" y="{y - 20}" width="{w + 40}" height="{h + 40}" fill="#a8d4ea"/>'
    inner += blob([(x - 10, y + h * .75), (x + w * .3, y + h * .42), (x + w * .55, y + h * .7), (x + w * .8, y + h * .35), (x + w + 10, y + h * .62),
                   (x + w + 10, y + h + 10), (x - 10, y + h + 10)], "#7fae6a")
    inner += blob(ellipse_pts(x + w * .78, y + h * .22, 22, 22, 12), "#fff1b8")
    _ = rs
    s = [shape(rect_pts(x - 22, y - 22, x + w + 22, y + h + 22, 4), "#7a5236", blob(rect_pts(x + w, y - 22, x + w + 22, y + h + 22), "#5a3a24", .9),
               w=4.2, seed=4310 + k),
         shape(rect_pts(x, y, x + w, y + h), "#a8d4ea", inner, w=3.2, seed=4320 + k)]
    return "".join(s)


def hooks(x, k):
    s = [shape(rect_pts(x - 120, -1180, x + 120, -1150, 6), "#a8774c", "", w=3.6, seed=4400 + k)]
    for j, dx in enumerate((-80, 0, 80)):
        s.append(line([(x + dx, -1150), (x + dx, -1120), (x + dx + 14, -1110)], 6, INK, seed=4410 + j, taper=.2, wmin=.6))
    # шарф и сумка
    s.append(shape([(x - 90, -1124), (x - 64, -1124), (x - 56, -900, 1), (x - 98, -890, 1)], "#5f9a5a",
                   "".join(line([(x - 96, -1060 + j * 50), (x - 58, -1060 + j * 50)], 3, "#3f7a42", seed=4420 + j, op=.8) for j in range(4)),
                   w=3.6, seed=4421 + k))
    s.append(line([(x + 74, -1112), (x + 40, -980), (x + 110, -980), (x + 86, -1112)], 5, "#6b4a30", seed=4430, taper=.1, wmin=.8))
    s.append(shape(rect_pts(x + 20, -990, x + 130, -880, 16), "#d9a35a", blob(rect_pts(x + 100, -990, x + 130, -880), "#b8823e", .9),
                   w=4, seed=4431 + k))
    return "".join(s)


# ───────────────────────────── проём кухни и косяк
def kitchen_opening(xj):
    """Проём справа от косяка: тёплая кухня в солнце (стена, край стола, окно), перемычка сверху."""
    s = []
    x0, x1, top = xj + 60, xj + 700, -1060
    inner = blob(rect_pts(x0, top, x1, 0), "#f7dfa6")
    inner += blob(rect_pts(x0, -300, x1, 0), "#e9c98a")
    inner += shape(rect_pts(x0 + 200, -880, x0 + 470, -520, 6), "#bfe3f4",
                   blob([(x0 + 200, -600), (x0 + 330, -700), (x0 + 470, -620), (x0 + 470, -520), (x0 + 200, -520)], "#a7d49a") +
                   line([(x0 + 335, -880), (x0 + 335, -520)], 6, "#f4efe4", taper=.02, wmin=1, seed=5010), w=4, seed=5011)
    inner += shape(rect_pts(x0 + 120, -420, x1, -380, 6), "#c99566", "", w=4, seed=5012)
    inner += shape(rect_pts(x0 + 140, -380, x0 + 180, 0), "#b17f52", "", w=3.6, seed=5013)
    g = lib.lin_grad([(0, "#fff4cc", .0), (1, "#fff4cc", .55)], 0, 0, 1, 0)
    inner += f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{-top}" fill="url(#{g})"/>'
    s.append(shape(rect_pts(x0, top, x1, 0), "#f7dfa6", inner, w=4.4, seed=5014))
    s.append(shape(rect_pts(xj - 30, top - 80, x1 + 40, top, 4), "#f4efe4", blob(rect_pts(xj - 30, top - 26, x1 + 40, top), "#d9d1c0", .9),
                   w=4.4, seed=5015))
    return "".join(s)


def jamb(xj, shake):
    """Косяк: торец стены с белым наличником, от пола до перемычки; дрожит после удара."""
    dx = 4 * shake
    s = [shape(rect_pts(xj + dx, -1140, xj + 70 + dx, 0), "#f4efe4",
               blob(rect_pts(xj + 44 + dx, -1140, xj + 70 + dx, 0), "#d9d1c0", .95) +
               line([(xj + 14 + dx, -1120), (xj + 14 + dx, -20)], 3, "#ffffff", seed=5020, op=.9), w=4.8, seed=5021)]
    return "".join(s)


# ───────────────────────────── походка
def contacts():
    C = []
    for k in range(-6, 12):
        t = T_HIT - 0.06 - 2 * TC + k * TC
        C.append((t, "n" if k % 2 == 0 else "f", (k - 2) * STEP + STEP * 0.42 - V * 0.06))
    return C


CON = contacts()


def hip_x(tw):
    return V * (tw - T_HIT) + V * 0.0


def foot(side, t):
    cs = [c for c in CON if c[1] == side]
    prev, nxt = cs[0], cs[1]
    for i, c in enumerate(cs):
        if c[0] <= t:
            prev, nxt = c, cs[min(i + 1, len(cs) - 1)]
    ankle_y = -F.people.AH * BS * 0.45
    if t <= prev[0] + ST:
        roll = -0.06 * smooth(prev[0] + ST * .6, prev[0] + ST, t)
        return (prev[2], ankle_y), roll
    u = clamp((t - prev[0] - ST) / (nxt[0] - prev[0] - ST))
    x = prev[2] + (nxt[2] - prev[2]) * ease_io(u)
    y = ankle_y - 26 * math.sin(math.pi * u)         # шаркает
    phi = -0.06 * (1 - u) + 0.05 * math.sin(math.pi * u)
    return (x, y), phi


def feet_at(t):
    tw = min(t, T_HIT)
    out = {}
    for s in ("n", "f"):
        (x, y), phi = foot(s, tw)
        if t > T_HIT:                                 # после удара поднятая стопа опускается
            k = ease_out(clamp((t - T_HIT) / .18))
            y0 = -F.people.AH * BS * 0.45
            y += (y0 - y) * k
            phi *= 1 - k
        out[s] = ((x, y), phi)
    return out


def battery(x, y, t, empty):
    """Батарейка-индикатор: корпус, носик, одно красное деление мигает; после удара — пусто, мигает рамка."""
    s = []
    w, h = 120, 58
    blink = (math.sin(t * 2 * math.pi * (3.0 if empty < .5 else 5.0)) > 0)
    body = rect_pts(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 12)
    inner = blob(rect_pts(x - w / 2, y - h / 2, x + w / 2, y - h / 2 + 12), "#ffffff", .9)
    if empty < .5:
        col = "#e5392f" if blink else "#7a1e18"
        inner += shape(rect_pts(x - w / 2 + 10, y - h / 2 + 10, x - w / 2 + 38, y + h / 2 - 10, 5), col, "", w=2.6, seed=5031)
    s.append(shape(body, "#f6f2ea", inner, w=5.2, seed=5030, ink_color=("#e5392f" if (empty > .5 and blink) else INK)))
    s.append(shape(rect_pts(x + w / 2 - 2, y - 13, x + w / 2 + 12, y + 13, 4), "#9aa3b8", "", w=4, seed=5032))
    return "".join(s)


def mug(x, y, tilt, sd=5040):
    """Кружка: дно в (x, y), ручка слева (к руке), tilt — наклон (рад)."""
    cup = [(-34, -84, 1), (34, -84, 1), (30, 0, 1), (-30, 0, 1)]
    hdl = [(-34, -66), (-58, -62), (-62, -36), (-50, -18), (-32, -20)]
    c, s_ = math.cos(tilt), math.sin(tilt)

    def R(p):
        return (x + p[0] * c - p[1] * s_, y + p[0] * s_ + p[1] * c) + ((1,) if len(p) > 2 else ())
    o = line([R(p) for p in hdl], 9, INK, taper=.05, wmin=.9, seed=sd)
    o += line([R(p) for p in hdl], 4.5, "#e8705a", taper=.05, wmin=.9, seed=sd + 1)
    o += shape([R(p) for p in cup], "#e8705a", blob([R(p) for p in [(10, -84), (34, -84), (30, 0), (8, 0)]], "#c2523e", .9) +
               blob([R(p) for p in [(-30, -80), (30, -80), (30, -70), (-30, -70)]], "#6b3a1e", .95), w=4.4, seed=sd + 2)
    return o


def splash(x, y, e):
    if e < 0 or e > .7:
        return ""
    s = []
    rs = np.random.RandomState(51)
    for k in range(9):
        vx, vy = rs.uniform(150, 700), rs.uniform(-900, -300)
        px, py = x + vx * e, y + vy * e + 1500 * e * e
        r = rs.uniform(6, 11) * (1 - .4 * e / .7)
        s.append(shape(ellipse_pts(px, py, r * 1.5, r * .8, 10, rot=math.degrees(math.atan2(vy + 3000 * e, vx))), "#6b3a1e",
                       blob(ellipse_pts(px - r * .3, py - r * .3, r * .3, r * .3, 8), "#a8693c"), w=2.6, seed=5060 + k))
    return "".join(s)


def orbit_stars(cx, cy, t, e):
    if e < 0:
        return "", ""
    k = back_k(e)
    back, front = [], []
    for j in range(3):
        a = 2 * math.pi * (e * 1.4 + j / 3)
        x = cx + 135 * math.cos(a)
        y = cy - 70 + 30 * math.sin(a)
        st = F.star(x, y, 36 * k * (0.85 + 0.15 * math.sin(t * 9 + j)), a=a)
        (front if math.sin(a) > 0 else back).append(st)
    return "".join(back), "".join(front)


def back_k(e):
    return lib.back_out(clamp(e / .2), 2.2)


def pose_at(t):
    e = t - T_HIT
    hit = e > 0
    tw = min(t, T_HIT)
    ph = 2 * math.pi * (tw - CON[0][0]) / TC
    rec = 0.0
    lean_b = 0.0
    if hit:
        rec = -46 * math.sin(math.pi * clamp(e / .5)) * (1 if e < .25 else 1) - 18 * smooth(.25, .6, e)
        lean_b = -0.24 * math.exp(-e * 5) * math.sin(min(e * 9, math.pi)) - .04 * smooth(.2, .6, e)
    hx = hip_x(tw) + rec
    sway = 0.04 * math.sin(e * 6) * smooth(.3, .6, e) if hit else 0.0
    hip = np.array([hx, -HIP_H - 5 * math.cos(ph) * (0 if hit else 1)])
    lean = 0.10 - 0.025 * math.sin(ph) * (0 if hit else 1) + lean_b + sway
    up = np.array([math.sin(lean), -math.cos(lean)])
    fw = np.array([math.cos(lean), math.sin(lean)])
    sh = hip + up * F.people.TORSO * BS
    arm_dip = 14 * math.sin(ph * .5) if not hit else -30 * math.exp(-e * 4) * math.sin(min(e * 10, math.pi))
    tf = sh + fw * 270 + up * (-36 + arm_dip)
    tn = sh + fw * 262 + up * (-50 - arm_dip * .6)
    arms = {"f": ("ik", tuple(tf), -1), "n": ("ik", tuple(tn), -1)}
    limp = dict(kind="open", flip=1, dir=(1, .55), curl=(.35, .45, .5, .55), spread=.05, thumb=.3, bend=.2)
    fist = dict(kind="open", flip=1, dir=(1, .1), curl=(.9, .95, .95, .95), spread=.02, thumb=.75)
    hands = {"f": limp, "n": fist}
    if not hit:
        ex = dict(lid=.0, closed=.62 + .2 * math.sin(t * 2.3), look=(.4, .4), brows="tired", mouth="talk", open=.32 + .08 * math.sin(t * 3),
                  smile=-.35)
        head_ang = .26 + .05 * math.sin(ph * .5)
    else:
        sq = 1 - smooth(.35, .6, e)
        ex = dict(lid=.0 + .2 * (1 - sq), closed=1.0 * sq + .55 * (1 - sq), look=(.0, -.2), brows="worry", mouth="talk",
                  open=.75 * sq + .3 * (1 - sq), smile=-.6, hair=12 * F.kick(t, T_HIT, 7, 6))
        head_ang = .26 - .5 * math.exp(-e * 5) * math.sin(min(e * 10, math.pi)) - .06 * smooth(.3, .6, e) + .05 * math.sin(e * 5)
    pose = dict(hip=tuple(hip), scale=BS, lean=lean, feet=feet_at(t), arms=arms, hands=hands, expr=ex, head_ang=head_ang, hood=0,
                strings=(3 * math.sin(ph), 2 * math.cos(ph)))
    return pose, hx


def jamb_x():
    global XJ
    if XJ is None:
        F.people.SLIPPERS[0] = True
        lib.DEFS.clear()
        pose, _ = pose_at(T_HIT)
        dm = F.people.draw(pose, "dima")
        F.people.SLIPPERS[0] = False
        XJ = float(dm["head"][0]) + 60
    return XJ


def frame(sid, t):
    xj = jamb_x()
    lib.DEFS.clear()
    e = t - T_HIT
    F.people.SLIPPERS[0] = True
    pose, hx = pose_at(t)
    dm = F.people.draw(pose, "dima")
    F.people.SLIPPERS[0] = False
    # камера: едет за Димой, к удару подтягивается; после — тряска
    cs = 1.10 + 0.08 * ease_io(clamp((t - T_A) / 1.25)) + 0.06 * F.bump(t, T_HIT + .02, .35)
    cx = min(hx, hip_x(T_HIT)) + 110 + 8 * math.sin(t * 1.3)
    cy = -520 + 6 * math.sin(t * 2.0)
    r = 0.5 * math.sin(t * 1.4) + 2.4 * F.kick(t, T_HIT, 6, 7)
    cx += 18 * F.kick(t, T_HIT, 6, 9)
    cy += 14 * F.kick(t, T_HIT + .03, 6, 8)
    F.set_ink(cs)
    view = 1080 / cs
    bg = corridor(cx - view, cx + view, (xj - 60, xj + 760)) + kitchen_opening(xj)
    sh = blob(ellipse_pts(hx + 10, 4, 170, 16, 16), "#2a1606", .28, lib.blur(5))
    hxx, hyy = dm["head"]
    sb, sf = orbit_stars(hxx - 10, hyy - 40, t, e)
    shake = F.kick(t, T_HIT, 7, 11) if e > 0 else 0.0
    # кружка в ближней руке
    wn = dm["wrist"]["n"]
    tilt = -0.08 + (0.5 * math.exp(-e * 5) * math.sin(min(e * 12, math.pi)) if e > 0 else 0.03 * math.sin(t * 3))
    cup = mug(wn[0] + 56, wn[1] + 64, tilt)
    body = sh + dm["legs"] + dm["arm_f"] + sb + dm["body"] + jamb(xj, shake) + dm["arm_n"] + cup + sf + splash(wn[0] + 60, wn[1] - 40, e)
    bat = battery(hxx + 10, hyy - 250 - 6 * math.sin(t * 3), t, 1.0 if e > .05 else 0.0)
    # «бум» у лба: короткие штрихи удара
    if 0 < e < .3:
        u = e / .3
        for j, a in enumerate((-2.3, -2.8, 2.5, 2.9, 3.3)):
            r0 = 40 + 90 * ease_out(u)
            px, py = xj, hyy - 30
            body += line([(px + math.cos(a) * r0, py + math.sin(a) * r0), (px + math.cos(a) * (r0 + 46 * (1 - u)), py + math.sin(a) * (r0 + 46 * (1 - u)))],
                         11, INK, taper=.5, seed=5080 + j)
    light = sunbeam(cx)
    return F.compose(bg + light, body + bat, (cx, cy, cs, r), glow=False)


def sunbeam(cx):
    g = lib.lin_grad([(0, "#fff1c8", 0), (1, "#fff1c8", .35)], 0, 0, 1, 0)
    return f'<rect x="{cx - 900:.0f}" y="-1600" width="1800" height="1800" fill="url(#{g})" style="mix-blend-mode:screen"/>'


_ = (mix, smooth, _ST)
