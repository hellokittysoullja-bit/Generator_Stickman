"""Сцена chain рилса 40 «66 дней».
s08 (11.2–13.7; клип 11.0–13.9): тёмный фон, свет сверху; длинная стальная цепь натянута горизонтально между болтом на
     стене слева и правым краем: 10 звеньев «лицом» с латунными бирками — дни 1–9 (кодом), у десятого бирка пустая;
     между ними звенья «ребром». Камера едет вдоль цепи; на «цепочке» (12.96) по звеньям бежит блик, звено за звеном.
s09 (13.7–16.0; клип 13.5–16.2): та же цепь крупнее у десятого звена; оно дрожит, по нему идёт трещина; на «порвалась»
     (14.32) лопается со вспышкой и искрами, половинки разлетаются, цепь падает на пол волной от места разрыва (тряска);
     на «пропало» (15.28) звенья рассыпаются по полу.
Мир: цепь на y = CY, пол y = FLOOR. Звено рисуется в своих координатах (центр 0, 0) и ставится преобразованием."""
import math

import numpy as np

import lib
from ink import ink_closed
from lib import DEFS, INK, W, H, blob, cam, clamp, ease_io, ease_out, ellipse_pts, f, line, rad_grad, shape, smooth, svg
from ink import fill_d

_ST = {}
P = 230.0                 # шаг звеньев «лицом»
CY = 600.0
FLOOR = 1000.0
N_FACE = 14               # 1..9 — дни, 10 — пустое, 11..14 — дальше цепь
T_GLINT = 12.96
T_BREAK = 14.32
T_SCATTER = 15.28
STEEL, STEEL_SH, STEEL_HI, STEEL_DK = "#a7afbb", "#727b89", "#e8edf3", "#4c5361"
BRASS, BRASS_SH = "#d9b25a", "#a9822f"


def stadium(L, r, n=10):
    pts = []
    for k in range(n + 1):
        a = -math.pi / 2 + math.pi * k / n
        pts.append((L / 2 + r * math.cos(a), r * math.sin(a)))
    for k in range(n + 1):
        a = math.pi / 2 + math.pi * k / n
        pts.append((-L / 2 + r * math.cos(a), r * math.sin(a)))
    return pts


OUT = stadium(80, 54)
INN = stadium(80, 25)


def ring_d():
    return fill_d(OUT) + " " + fill_d(INN[::-1])


def face_link(sd):
    """Звено «лицом»: стальное кольцо-стадион, тень снизу-справа, блик сверху-слева, контур снаружи и внутри."""
    d = ring_d()
    c = lib.uid("rk")
    DEFS.append(f'<clipPath id="{c}"><path d="{d}" clip-rule="evenodd"/></clipPath>')
    o = [f'<path d="{d}" fill="{STEEL}" fill-rule="evenodd"/>']
    inner = blob([(-110, 10), (110, 6), (110, 70), (-110, 70)], STEEL_SH, .95)
    inner += blob([(-60, -14), (60, -14), (60, 14), (-60, 14)], STEEL_SH, .6)
    inner += line([(-70, -40), (-20, -46), (40, -44)], 7, STEEL_HI, taper=.8, wmin=.1, seed=sd + 1)
    inner += line([(-96, -6), (-90, -26)], 5, STEEL_HI, taper=.8, wmin=.1, seed=sd + 2, op=.8)
    o.append(f'<g clip-path="url(#{c})">{inner}</g>')
    o.append(f'<path d="{ink_closed(OUT, 5.0, seed=sd + 3)}" fill="{INK}"/>')
    o.append(f'<path d="{ink_closed(INN, 4.2, seed=sd + 4)}" fill="{INK}"/>')
    return "".join(o), c


def edge_link(sd):
    """Звено «ребром»: длинный узкий стержень; его ближняя прядь лежит поверх концов соседей, концы — в их дырах."""
    pts = lib.rect_pts(-94, -17, 94, 17, 16)
    inner = blob([(-100, 4), (100, 4), (100, 22), (-100, 22)], STEEL_SH, .95)
    inner += line([(-70, -8), (60, -9)], 5, STEEL_HI, taper=.8, wmin=.1, seed=sd + 1)
    return shape(pts, STEEL, inner, w=4.4, seed=sd + 2)


def tag(n, sd):
    """Латунная бирка на колечке: номер дня кодом; n=None — пустая."""
    o = [f'<circle cx="0" cy="-34" r="11" fill="none" stroke="{INK}" stroke-width="9"/>',
         f'<circle cx="0" cy="-34" r="11" fill="none" stroke="{STEEL}" stroke-width="4.5"/>']
    inner = blob(ellipse_pts(10, 10, 38, 38, 16), BRASS_SH, .9) + blob(ellipse_pts(-14, -14, 12, 7, 8, rot=-40), "#f6dc9a", .9)
    o.append(shape(ellipse_pts(0, 6, 40, 40, 22), BRASS, inner, w=4.4, seed=sd))
    if n is not None:
        o.append(f'<text x="0" y="26" text-anchor="middle" font-family="IDB" font-weight="900" font-size="58" fill="#3a2a14">{n}</text>')
    else:
        o.append(f'<circle cx="0" cy="6" r="24" fill="none" stroke="#6e4f16" stroke-width="4" stroke-dasharray="8 7"/>')
    return "".join(o)


# ───────────────────────── фон
def backdrop():
    s = []
    g = lib.lin_grad([(0, "#14151d", 1), (.55, "#262836", 1), (1, "#1a1b24", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="-1500" width="7000" height="{FLOOR + 1500}" fill="url(#{g})"/>')
    # пол: тёмные доски, перспектива не нужна — плоская полоса с тенью
    s.append(f'<rect x="-1500" y="{FLOOR - 30}" width="7000" height="1600" fill="#2e2a2c"/>')
    s.append(f'<rect x="-1500" y="{FLOOR - 30}" width="7000" height="10" fill="#433d3f"/>')
    for k in range(6):
        y = FLOOR + 30 + k * k * 22
        s.append(f'<rect x="-1500" y="{y}" width="7000" height="3" fill="#242022"/>')
    # свет сверху: широкий конус на цепь
    gl = rad_grad([(0, "#fff1d2", .30), (.45, "#ffe2b0", .10), (1, "#ffe2b0", 0)], 1300, CY - 80, 1700, 650)
    s.append(f'<rect x="-1500" y="-1500" width="7000" height="4000" fill="url(#{gl})" style="mix-blend-mode:screen"/>')
    # болт на стене слева: пластина с кольцом
    s.append(shape(lib.rect_pts(30, CY - 120, 110, CY + 120, 12), "#5a606c", blob(lib.rect_pts(80, CY - 120, 110, CY + 120), "#454a55", .9) +
                   "".join(f'<circle cx="70" cy="{CY + dy}" r="9" fill="#2c3038"/>' for dy in (-84, 84)), w=4.6, seed=40))
    return "".join(s)


def light_cone_floor():
    gl = rad_grad([(0, "#ffe6b8", .22), (1, "#ffe6b8", 0)], 1300, FLOOR + 40, 1500, 160)
    return f'<rect x="-1500" y="{FLOOR - 40}" width="7000" height="400" fill="url(#{gl})" style="mix-blend-mode:screen"/>'


# ───────────────────────── состояние звеньев
def face_x(i):
    return i * P


def sag(x):
    return 14 * math.sin(math.pi * clamp((x - 70) / 3700))


RS = np.random.RandomState(40)
JIT = [dict(vx=RS.uniform(-1, 1), rot=RS.uniform(-1, 1), lie=RS.uniform(-1, 1), hop=RS.uniform(.6, 1.2), vs=RS.uniform(.6, 1.4))
       for _ in range(40)]


def fall(tt, drop, hop=1.0):
    """Падение на пол: свободное падение, удар, два затухающих отскока. -> (смещение вниз, доля «лёг» 0..1)."""
    g = 3200.0
    if tt <= 0:
        return 0.0, 0.0
    tl = math.sqrt(2 * drop / g)
    if tt < tl:
        return 0.5 * g * tt * tt, 0.0
    d = tt - tl
    b = 70 * hop * math.exp(-5.5 * d) * abs(math.sin(math.pi * d / 0.17))
    return drop - b, smooth(0, 0.25, d)


def piece_pose(kind, i, t):
    """Положение звена или бирки: (x, y, поворот, сжатие по y). kind: 'face' i=1..14, 'edge' i=1..13 (между i и i+1)."""
    x = face_x(i) + (P / 2 if kind == "edge" else 0)
    y = CY + sag(x)
    rot, sy = 0.0, 1.0
    if t < T_BREAK or (kind == "edge" and i == 0):
        return x, y, rot, sy
    xb = face_x(10)
    d = abs(x - xb) / P
    j = JIT[i + (20 if kind == "edge" else 0)]
    delay = 0.05 + 0.055 * d
    tt = t - T_BREAK - delay
    drop = FLOOR - 28 - y
    dy, lie = fall(tt, drop, j["hop"])
    # звено ложится плашмя: сжатие по y и наклон; части тянутся к якорю
    side = -1 if x < xb else 1
    x += -side * 18 * smooth(0, 0.6, tt) * min(d, 4)
    y += dy
    rot = (12 * j["rot"]) * lie + 6 * side * math.sin(clamp(tt * 3)) * (1 - lie)
    sy = 1 - 0.55 * lie if kind == "face" else 1.0
    if t >= T_SCATTER:
        s = t - T_SCATTER
        vx = j["vx"] * 520 + side * 160
        x += vx * (1 - math.exp(-3.2 * s)) / 3.2
        h = max(0.0, 380 * j["hop"] * s - 0.5 * 3200 * s * s)
        y -= h
        rot += j["rot"] * 28 * (1 - math.exp(-3 * s))
    return x, y, rot, sy


def halves(t):
    """Половинки десятого звена после разрыва: летят в стороны, крутятся, падают и подпрыгивают на полу."""
    if t < T_BREAK:
        return ""
    o = []
    s = t - T_BREAK
    x0, y0 = face_x(10), CY + sag(face_x(10))
    for side, vx, vy, w in ((-1, -330, -760, -420), (1, 360, -880, 520)):
        x = x0 + side * 30 + vx * s
        yy = y0 - 0 + vy * s + 0.5 * 3200 * s * s
        ang = w * s
        fl = FLOOR - 30
        if yy > fl:
            tl = (-vy + math.sqrt(vy * vy + 2 * 3200 * (fl - y0))) / 3200
            d = s - tl
            yy = fl - 60 * math.exp(-6 * d) * abs(math.sin(math.pi * d / 0.16))
            x = x0 + side * 30 + vx * tl + vx * 0.25 * (1 - math.exp(-4 * d)) / 4 * 4
            ang = w * tl + w * 0.15 * (1 - math.exp(-4 * d))
        if t >= T_SCATTER:
            x += side * 120 * (1 - math.exp(-3 * (t - T_SCATTER)))
        clip = _ST["half_l" if side < 0 else "half_r"]
        o.append(f'<g transform="translate({f(x)} {f(yy)}) rotate({f(ang)})"><g clip-path="url(#{clip})">{_ST["face"][10][0]}</g>'
                 f'{line(_ST["zig"], 4.4, INK, taper=.1, wmin=.8, seed=77 + side)}</g>')
    return "".join(o)


def sparks(t):
    if t < T_BREAK:
        return ""
    o = []
    s = t - T_BREAK
    x0, y0 = face_x(10), CY + sag(face_x(10))
    rs = np.random.RandomState(9)
    for k in range(44):
        a = rs.uniform(0, 2 * math.pi)
        v = rs.uniform(500, 1500)
        life = rs.uniform(0.35, 0.8)
        if s > life:
            continue
        vx, vy = v * math.cos(a), v * math.sin(a) - 300
        x = x0 + vx * s
        y = y0 + vy * s + 0.5 * 2200 * s * s
        px = x0 + vx * max(0, s - 0.035)
        py = y0 + vy * max(0, s - 0.035) + 0.5 * 2200 * max(0, s - 0.035) ** 2
        if y > FLOOR - 12:
            continue
        u = s / life
        w = 7 * (1 - u) + 1
        col = "#fff4c0" if u < .3 else ("#ffc24a" if u < .65 else "#ff7a2a")
        o.append(f'<line x1="{f(px)}" y1="{f(py)}" x2="{f(x)}" y2="{f(y)}" stroke="{col}" stroke-width="{f(w)}" stroke-linecap="round"/>')
    # вспышка: кольцо и звезда
    if s < 0.35:
        u = s / 0.35
        g = rad_grad([(0, "#ffffff", 1 - u), (.3, "#fff0b0", .8 * (1 - u)), (1, "#ffb040", 0)], x0, y0, 120 + 380 * u)
        o.append(f'<rect x="{f(x0 - 600)}" y="{f(y0 - 600)}" width="1200" height="1200" fill="url(#{g})" style="mix-blend-mode:screen"/>')
        st = []
        for k in range(16):
            r = (260 if k % 2 == 0 else 50) * (0.4 + 0.8 * ease_out(u))
            aa = k * math.pi / 8 + 0.3
            st.append((x0 + r * math.cos(aa), y0 + r * math.sin(aa)))
        o.append(blob(st, "#fff6d0", .9 * (1 - u), 'style="mix-blend-mode:screen"'))
    return "".join(o)


def crack(t):
    """Трещина на десятом звене перед разрывом (с 13.85), растёт к 14.3."""
    if t < 13.85 or t >= T_BREAK:
        return ""
    u = smooth(13.85, 14.28, t)
    pts = _ST["zig"]
    n = max(2, int(len(pts) * u))
    return line(pts[:n], 3.6, "#1a1c22", taper=.3, wmin=.4, seed=88)


def glint(i, t):
    """Блик по звену: светлая полоса проходит слева направо, звено чуть «звенит» (вспыхивает)."""
    tg = T_GLINT + 0.08 * (i - 6)
    s = t - tg
    if s < -0.02 or s > 0.4:
        return ""
    u = clamp(s / 0.32)
    x = -150 + 300 * u
    clip = _ST["face"][i][1]
    band = [(x - 14, -70), (x + 2, -70), (x + 24, 70), (x + 8, 70)]
    o = f'<g clip-path="url(#{clip})"><g filter="url(#fGl)">{blob(band, "#ffffff", .75 * math.sin(math.pi * u))}</g></g>'
    if 0.2 < u < 0.8:
        k = math.sin(math.pi * (u - 0.2) / 0.6)
        st = []
        for j in range(8):
            r = (34 if j % 2 == 0 else 7) * k
            a = j * math.pi / 4
            st.append((60 + r * math.cos(a), -40 + r * math.sin(a)))
        o += blob(st, "#ffffff", .95)
    return o


def chain(t, sid):
    o = []
    shake = 0.0
    # дрожь десятого звена перед разрывом
    if sid == "s09" and t < T_BREAK:
        shake = 2.4 * smooth(13.7, 14.25, t) * math.sin(t * 95)
    tags = []
    edges = []
    # звенья «ребром» — поверх концов соседей
    for i in range(0, N_FACE):
        x, y, r, sy = piece_pose("edge", i, t)
        edges.append(f'<g transform="translate({f(x)} {f(y)}) rotate({f(r)}) scale(1 {f(sy)})">{_ST["edge"][i]}</g>')
    for i in range(1, N_FACE + 1):
        if i == 10 and t >= T_BREAK:
            continue
        x, y, r, sy = piece_pose("face", i, t)
        if i == 10:
            x += shake
        body = _ST["face"][i][0]
        if sid == "s08":
            body += glint(i, t)
        if i == 10:
            body += crack(t)
        o.append(f'<g transform="translate({f(x)} {f(y)}) rotate({f(r)}) scale(1 {f(sy)})">{body}</g>')
        if i <= 10:
            # бирка висит под звеном и качается; на полу — лежит рядом
            sw = 5 * math.sin(t * 3.1 + i * 0.9)
            lie = 1 - sy if sy < 1 else 0
            ty = 54 * sy + 34
            tx = 0
            tr = sw + r + 50 * lie * (1 if i % 2 else -1)
            if lie > 0:
                tx = 70 * lie * (1 if i % 2 else -1)
                ty = 40 * sy + 20 * (1 - lie)
            ca, sa = math.cos(math.radians(r)), math.sin(math.radians(r))
            gx, gy = x + tx * ca - ty * sa, y + tx * sa + ty * ca
            tags.append(f'<g transform="translate({f(gx)} {f(gy)}) rotate({f(tr)}) scale(1 {f(1 - 0.4 * lie)})">'
                        f'{_ST["tag"][i]}</g>')
    return "".join(o) + "".join(edges) + "".join(tags)


def shadows(t):
    """Мягкие тени цепи на полу: полоса под цепью, ближе к полу — темнее и уже."""
    o = []
    for i in range(1, N_FACE + 1):
        x, y, r, sy = piece_pose("face", i, t)
        h = clamp((FLOOR - y) / (FLOOR - CY))
        o.append(blob(ellipse_pts(x, FLOOR - 6, 110 + 60 * h, 14 + 6 * h, 14), "#08080c", .55 - .3 * h))
    return f'<g filter="url(#fChSh)">{"".join(o)}</g>'


def s08(t):
    u = clamp((t - 11.0) / 2.9)
    e = 0.35 * u + 0.65 * ease_io(u)
    cx = 330 + (2130 - 330) * e
    art = _ST["bg"] + shadows(t) + chain(t, "s08") + light_cone_floor()
    cm = cam(cx, 640, 1.58 + 0.08 * u, -2.0 + 3.0 * u)
    return art, cm


def s09(t):
    u = clamp((t - 13.5) / 2.7)
    s = t - T_BREAK
    sh_x = sh_y = 0.0
    if s > 0:
        a = 26 * math.exp(-6 * s)
        sh_x += a * math.sin(s * 71)
        sh_y += a * math.cos(s * 57)
    s2 = t - T_SCATTER
    if s2 > 0:
        a = 9 * math.exp(-7 * s2)
        sh_x += a * math.sin(s2 * 63)
        sh_y += a * math.cos(s2 * 49)
    zoom = 1.45 - 0.25 * ease_io(u)
    cx = face_x(10) - 60 + 10 * u + sh_x
    cy = 700 + 60 * smooth(T_BREAK, T_BREAK + 0.8, t) + sh_y
    art = _ST["bg"] + shadows(t) + chain(t, "s09") + halves(t) + light_cone_floor() + sparks(t)
    cm = cam(cx, cy, zoom, 0.6 - 0.9 * u + 0.8 * math.exp(-5 * max(0, s)) * (1 if s > 0 else 0) * math.sin(s * 30))
    return art, cm


def build_static():
    if _ST:
        return
    DEFS.append('<filter id="fGl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>')
    DEFS.append('<filter id="fChSh" x="-30%" y="-100%" width="160%" height="300%"><feGaussianBlur stdDeviation="10"/></filter>')
    _ST["bg"] = backdrop()
    _ST["face"] = {i: face_link(500 + i * 10) for i in range(1, N_FACE + 1)}
    _ST["edge"] = {i: edge_link(700 + i * 10) for i in range(0, N_FACE)}
    _ST["tag"] = {i: tag(i if i <= 9 else None, 900 + i * 10) for i in range(1, 11)}
    zig = [(6, -60), (-4, -38), (8, -18), (-6, 2), (6, 22), (-4, 42), (6, 60)]
    _ST["zig"] = zig
    for nm, sgn in (("half_l", -1), ("half_r", 1)):
        c = lib.uid("hz")
        far = sgn * 140
        pts = [(far, -80, 1)] + [(p[0], p[1], 1) for p in zig] + [(far, 80, 1)]
        DEFS.append(f'<clipPath id="{c}"><path d="{fill_d(pts)}"/></clipPath>')
        _ST[nm] = c
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s08": s08, "s09": s09}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1a1b24"/><g transform="{cm}">{art}</g>')
