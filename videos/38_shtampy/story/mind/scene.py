"""Сцена mind рилса 38 (s05, s06, s07): внутренний мир Димы на тёмно-синем фоне (фон и пылинки — как mind рилса 34).
Бесконечная дорожка из плиток в перспективе: от горизонта слева подходит к нам, проходит под Димой (он ровно посередине)
и снова уходит к горизонту справа; оба конца тонут в дымке.
s05 «так легко бросить на середине?» (8.0–10.2): Дима с валиком стоит посередине, на «легко» (8.48) оглядывается назад и
     вперёд (разворот), на «бросить» (8.84) роняет валик (падает, подпрыгивает), на «середине» (9.20) под ним
     выскакивает флажок-метка середины;
s06 «Когда не видно, сколько уже сделано» (9.8–12.1): дорожка ближе; на плитках позади Димы — значки сделанного
     (покрашенная стена, розетка, плитка, лампочка), на «видно» (10.56) наползает серый туман, на «сделано» (11.36)
     значки пропадают в тумане;
s07 «мозг решает, что ничего» (11.7–14.15): на «мозг» (11.92) выскакивает розовый мозг с глазами, ручками и печатью,
     смотрит в туман, щурится на «решает» (12.28), на «ничего» (13.12) с размаху ставит печать на табличку — большая «0»;
     Дима сникает. Всё — функция общего времени ролика t."""
import math

import numpy as np

import brain as BR
import brain_art
import lib
import parts34 as P
import people
from lib import INK, W, H, back_out, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, rect_pts, shape, smooth, svg

_ST = {}
LEGKO = P.wt("легко")              # 8.48
BROS = P.wt("бросить")             # 8.84
SERED = P.wt("середине")           # 9.20
VIDNO = P.wt("видно", 10)          # 10.56
SDEL = P.wt("сделано")             # 11.36
MOZG = P.wt("мозг")                # 11.92
RESH = P.wt("решает")              # 12.28
NICH = P.wt("ничего")              # 13.12
EFF = 0.8

# ─────────────────────────────── дорожка в перспективе
HOR, FOC, HC = 600.0, 900.0, 720.0
Z0, CB, CA, CC = 1200.0, 1100.0, 1800.0, 420.0
ROAD_W = 300.0
TILE = 150.0
DX, DS = 540.0, 0.31               # Дима: x на экране, масштаб
FEET_Y = HOR + FOC * HC / Z0       # 1140


def cX(u):
    return math.copysign(CB * abs(u) + CC * u * u, u)


def cZ(u):
    return Z0 + CA * u * u


def proj(X, Z):
    return (540 + FOC * X / Z, HOR + FOC * HC / Z)


def frame_at(u):
    """Центр, нормаль (в плоскости земли) в точке u."""
    e = 1e-4
    X, Z = cX(u), cZ(u)
    dx, dz = (cX(u + e) - cX(u - e)) / (2 * e), (cZ(u + e) - cZ(u - e)) / (2 * e)
    L = math.hypot(dx, dz)
    return X, Z, -dz / L, dx / L


def arc_params():
    """Значения u через каждые TILE по длине дорожки (в обе стороны от u=0)."""
    us = np.linspace(0, 14, 140001)
    xs = np.array([cX(u) for u in us])
    zs = np.array([cZ(u) for u in us])
    s = np.concatenate([[0], np.cumsum(np.hypot(np.diff(xs), np.diff(zs)))])
    out = []
    k = 0
    while True:
        target = (k + 0.5) * TILE
        if target > s[-1]:
            break
        out.append(float(np.interp(target, s, us)))
        k += 1
    return out


def road_pt(u):
    X, Z, _, _ = frame_at(u)
    return proj(X, Z)


def ground(X, Z, y_off=0.0):
    p = proj(X, Z)
    return (p[0], p[1] + y_off * FOC / Z)


def tile_quad(ua, ub):
    Xa, Za, nxa, nza = frame_at(ua)
    Xb, Zb, nxb, nzb = frame_at(ub)
    h = ROAD_W / 2
    return [(Xa + nxa * h, Za + nza * h), (Xb + nxb * h, Zb + nzb * h), (Xb - nxb * h, Zb - nzb * h), (Xa - nxa * h, Za - nza * h)]


TILE_C = ["#d8c7a6", "#cbb894", "#e0d1b2"]


def road():
    """Статичная дорожка: плитки обеих ветвей от дальних к ближним; у ближних видна толщина (торец)."""
    ups = arc_params()
    bounds = [0.0]
    for u in ups:
        bounds.append(2 * u - bounds[-1])
    tiles = []
    for side in (1, -1):
        for k in range(len(bounds) - 1):
            ua, ub = side * bounds[k], side * bounds[k + 1]
            q = tile_quad(ua, ub)
            zmax = max(p[1] for p in q)
            sp = [proj(*p) for p in q]
            size = max(math.dist(sp[0], sp[1]), math.dist(sp[1], sp[2]))
            if size < 2.2:
                continue
            tiles.append((zmax, side, k, q, sp))
    # центральная плитка (u от −b1 до b1) — одна, без шва под ногами
    tiles.sort(key=lambda r: -r[0])
    o = []
    for zmax, side, k, q, sp in tiles:
        sc = FOC / zmax
        thick = 34.0
        for a, b in ((0, 1), (2, 3)):
            pa, pb = q[a], q[b]
            side_poly = [ground(*pa), ground(*pb), ground(*pb, thick), ground(*pa, thick)]
            o.append(blob(side_poly, "#7d6c57"))
        col = TILE_C[(k + (0 if side > 0 else 1)) % 3]
        inner = blob([sp[1], sp[2], ((sp[2][0] + sp[3][0]) / 2, (sp[2][1] + sp[3][1]) / 2), ((sp[0][0] + sp[1][0]) / 2, (sp[0][1] + sp[1][1]) / 2)],
                     mix(col, "#000000", .08), .9)
        lib.INK_K[0] = max(0.12, min(1.0, sc * 0.9))
        o.append(shape([p + (1,) for p in sp], col, inner, w=3.6, seed=3000 + k * 2 + (side > 0)))
    lib.INK_K[0] = 1.0
    return "".join(o)


def background():
    s = []
    lib.lin_grad([(0, "#1b2244", 1), (.55, "#26315e", 1), (1, "#2f3d72", 1)], 0, 0, 0, 1, gid="gMind")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="url(#gMind)"/>')
    rad_grad([(0, "#4a5d9e", .85), (.6, "#36467e", .35), (1, "#36467e", 0)], 540, 900, 760, 800, gid="gMindSpot")
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="url(#gMindSpot)"/>')
    return "".join(s)


def haze():
    """Дымка у горизонта: концы дорожки тонут."""
    g = lib.lin_grad([(0, "#2a3566", 0), (.45, "#3a4884", .95), (.6, "#3a4884", .95), (1, "#2c3868", 0)], 0, 0, 0, 1, gid="gHaze")
    o = f'<rect x="-900" y="{HOR - 110}" width="{W + 1800}" height="230" fill="url(#gHaze)"/>'
    for k, (x, y, rx, ry) in enumerate(((330, HOR + 10, 260, 60), (760, HOR + 12, 260, 60), (180, HOR + 30, 200, 44), (920, HOR + 30, 200, 44))):
        g = rad_grad([(0, "#5566a0", .85), (1, "#5566a0", 0)], x, y, rx, ry)
        o += f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="url(#{g})"/>'
    return o


def dust(t, n=30, sd=4):
    rs = np.random.RandomState(sd)
    s = []
    for k in range(n):
        x0, y0 = rs.uniform(-200, W + 200), rs.uniform(-200, H)
        sp, ph, r = rs.uniform(14, 34), rs.uniform(0, 6.28), rs.uniform(2.2, 4.6)
        x = x0 + 30 * math.sin(t * 0.7 + ph)
        y = (y0 - sp * (t - 8)) % (H + 300) - 150
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#c9d6ff" opacity="{.16 + .12 * math.sin(t * 2 + ph):.3f}"/>')
    return "".join(s)


# ─────────────────────────────── валик
def roller(base, ang, k=1.0, sd=0):
    """Малярный валик: base — середина рукоятки (в кулаке), ang — направление рукоятки к валику (рад)."""
    d = (math.cos(ang), math.sin(ang))
    n = (-d[1], d[0])

    def tf(x, y):
        return (base[0] + d[0] * x * k + n[0] * y * k, base[1] + d[1] * x * k + n[1] * y * k)
    o = []
    o.append(shape([tf(-60, -13), tf(18, -13), tf(18, 13), tf(-60, 13)], "#3f7ec4", blob([tf(-60, 4), tf(18, 4), tf(18, 13), tf(-60, 13)], "#2c5f9a", .9),
                   w=3.4, seed=sd))
    o.append(line([tf(18, 0), tf(150, 0), tf(170, 22), tf(170, 40)], 9 * k, "#8a9099", taper=.05, wmin=.9, seed=sd + 1))
    o.append(line([tf(18, 0), tf(150, 0), tf(170, 22), tf(170, 40)], 9 * k + 6, INK, taper=.05, wmin=.9, seed=sd + 2))
    o.insert(1, o.pop())
    cyl = [tf(140, 40, ), tf(200, 40), tf(206, 52), tf(206, 150), tf(200, 162), tf(140, 162), tf(134, 150), tf(134, 52)]
    inner = blob([tf(180, 40), tf(206, 40), tf(206, 162), tf(180, 162)], "#86c2a7", .95)
    for j in range(4):
        inner += line([tf(144 + j * 16, 50), tf(146 + j * 16, 152)], 2.4, "#c6eadb", taper=.4, seed=sd + 10 + j, op=.8)
    o.append(shape(cyl, "#a9dcc4", inner, w=4, seed=sd + 3))
    return "".join(o)


# ─────────────────────────────── Дима
def dima(t, x, y, s, face=1.0, hold=True, droop=0.0, look=None, roller_ang=None, mouth="tired", brows="worry", blink=0.0, lean_add=0.0):
    """Маленький Дима стоит: (x, y) — середина между стопами на земле; face 1 — смотрит вправо, −1 — влево (разворот
    сжатием по ширине). hold — валик в руке. droop 0..1 — сник (плечи, голова вниз)."""
    lib.INK_K[0] = EFF / s
    br = math.sin(t * 2.3)
    hip = (0.0, -600 * s + 6 * s * br + 22 * s * droop)
    lean = 0.04 + 0.16 * droop + lean_add + 0.01 * br
    hx, hy = hip
    nt = (hx + 175 * s, hy - 10 * s) if hold else (hx + 60 * s + 30 * s * droop, hy + 40 * s)
    ft = (hx - 30 * s, hy + 50 * s + 10 * s * droop)
    lk = look if look is not None else (0.45, 0.1 + 0.5 * droop)
    hn = dict(kind="open", curl=(.95, .95, .95, .9), spread=.02, thumb=.85, dir=(1.0, 0.15)) if hold else \
        dict(kind="open", curl=(.25, .2, .25, .3), spread=.12, thumb=.2, dir=(0.25, 1.0))
    d = people.draw(dict(hip=hip, scale=s, lean=lean,
                         feet={"n": ((hx + 50 * s, 0.0), 0.0), "f": ((hx - 50 * s, -4 * s), 0.0)},
                         arms={"f": ("ik", ft, 1), "n": ("ik", nt, -1)},
                         hands={"n": hn, "f": dict(kind="open", curl=(.3, .25, .3, .35), spread=.1, thumb=.25, dir=(0.1, 1.0))},
                         expr=dict(brows=brows, mouth=mouth, lid=0.35 - 0.15 * droop, look=lk, closed=blink),
                         head_ang=0.05 + 0.32 * droop), "dima")
    rl = ""
    lib.INK_K[0] = 1.0
    if hold:
        wr = d["wrist"]["n"]
        a = roller_ang if roller_ang is not None else -1.0
        rl = roller((wr[0] + 34 * s, wr[1] + 4 * s), a, 2.6 * s, sd=5200)
    lib.INK_K[0] = 1.0
    body = d.get("legs", "") + d["arm_f"] + d.get("pelvis", "") + d["body"] + rl + d["arm_n"]
    shadow = blob(ellipse_pts(x, y + 4, 120 * s / 0.36, 18 * s / 0.36, 16), "#3d3326", .45, lib.blur(3))
    fx = face if abs(face) > 0.08 else math.copysign(0.08, face)
    return shadow + f'<g transform="translate({f(x)} {f(y)}) scale({fx:.4f} 1)">{body}</g>'


def face_at(t):
    """Разворот на «легко»: назад (8.40–8.50), держит, вперёд (8.62–8.72)."""
    a = smooth(LEGKO - 0.06, LEGKO, t)
    b = smooth(LEGKO + 0.2, LEGKO + 0.26, t)
    v = 1 - 2 * a + 2 * b
    return v


def fallen_roller(t, t0, x0, y0, s):
    """Валик падает из руки (t0), подпрыгивает и ложится на плитку."""
    e = t - t0
    gy = LIE[1]
    if e <= 0:
        return None
    # фазы: падение 0.22 с, отскок 0.18 с, покой
    tx = x0 + (LIE[0] - x0) * clamp(e / 0.55)
    if e < 0.22:
        u = e / 0.22
        y = y0 + (gy - y0) * u * u
        ang = -math.pi / 2 - 0.25 + 1.3 * u
    elif e < 0.42:
        u = (e - 0.22) / 0.2
        y = gy - 46 * math.sin(math.pi * u)
        ang = -math.pi / 2 + 1.05 + 0.5 * u
    else:
        u = e - 0.42
        y = gy - 8 * math.exp(-u * 10) * abs(math.sin(u * 30))
        ang = -math.pi / 2 + 1.55
    return roller((tx, y - 50), ang, 2.6 * s, sd=5200)


def flag(x, y, e, k=1.0):
    """Метка середины: колышек с флажком (половина жёлтая, половина пустая), кольцо света на плитке."""
    if e <= 0:
        return ""
    pop = back_out(clamp(e / 0.3), 2.4)
    o = []
    rr = 60 + 140 * ease_out(clamp(e / 0.5))
    op = 1 - clamp((e - 0.2) / 0.5)
    if op > 0.02:
        o.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rr)}" ry="{f(rr * .28)}" fill="none" stroke="#ffe27a" stroke-width="{f(8 * op + 1)}" opacity="{op:.3f}"/>')
    g = rad_grad([(0, "#ffe27a", .55), (1, "#ffe27a", 0)], x, y, 160, 50)
    o.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="160" ry="50" fill="url(#{g})"/>')
    h = 230 * k * pop
    wave = 6 * math.sin(e * 9)
    top = (x, y - h)
    o.append(line([(x, y), top], 9 * k, INK, taper=.05, wmin=.9, seed=5300))
    o.append(line([(x, y), top], 5 * k, "#d9dde6", taper=.05, wmin=.9, seed=5301))
    fl = [top + (1,), (x + 120 * k * pop, y - h + 20 * k + wave), (x + 118 * k * pop, y - h + 62 * k + wave), (x, y - h + 80 * k, 1)]
    half = blob([top, (x + 60 * k * pop, y - h + 10 * k + wave * .5), (x + 60 * k * pop, y - h + 72 * k + wave * .5), (x, y - h + 80 * k)], "#ffcf3a")
    o.append(shape(fl, "#f3efe4", half + line([(x + 60 * k * pop, y - h + 10 * k), (x + 60 * k * pop, y - h + 72 * k)], 3, INK, seed=5303, op=.6),
                   w=4, seed=5302))
    o.append(shape(ellipse_pts(x, y - h - 6, 12 * k, 12 * k, 10), "#ffcf3a", "", w=3, seed=5304))
    return "".join(o)


LIE = road_pt(0.1)               # где ложится валик


# ═══════════════════════════════ s05
def s05(t):
    art = [_ST["bg"], dust(t), _ST["road"], _ST["haze"]]
    fc = face_at(t)
    hold = t < BROS
    look_back = (1 - smooth(LEGKO + 0.12, LEGKO + 0.2, t)) * smooth(LEGKO - 0.1, LEGKO, t)
    mouth = "gape" if t > SERED else "tired"
    art.append(flag(DX - 105, FEET_Y + 14, t - SERED))
    droop = 0.35 * smooth(BROS, BROS + 0.3, t)
    lookv = (0.55, 0.1) if look_back < 0.5 else (0.6, -0.05)
    if t > SERED:
        lookv = (-0.4, 0.75)
    art.append(dima(t, DX, FEET_Y, DS, face=fc, hold=hold, droop=droop, look=lookv, mouth=mouth, brows="worry",
                    blink=P.bump(t, 8.12, 0.16)))
    rf = fallen_roller(t, BROS, DX + 70, FEET_Y - 300, DS)
    if rf:
        art.append(rf)
        art.append(P.pop_lines(LIE[0] + 30, LIE[1] - 10, t - BROS - 0.22, 40, 90, 5, a0=-math.pi / 2, spread=2.2, col="#e9eeff", w=6, sd=5400))
    # камера: медленный наезд, толчок на «бросить»
    u = clamp((t - 8.0) / 2.2)
    sc = 1.3 + 0.09 * ease_io(u) + 0.045 * P.kick(t, BROS + 0.22, 6, 14) + 0.025 * P.kick(t, SERED, 6, 14)
    return "".join(art), cam(545, 905 + 25 * u, sc, -0.6 + 1.0 * u)


# ═══════════════════════════════ s06
ICON_U = [-0.11, -0.19, -0.28, -0.39]


def icon_wall(sd):
    o = shape(rect_pts(-46, -40, 46, 40, 4), "#ecd27e", blob(rect_pts(-46, -40, 6, 40), "#a9dcc4"), w=3.4, seed=sd)
    o += line([(6, -40), (2, -10), (8, 14), (4, 40)], 3, "#86c2a7", seed=sd + 1)
    return o


def icon_socket(sd):
    o = shape(rect_pts(-40, -40, 40, 40, 12), "#f6f4ee", blob(rect_pts(8, -40, 40, 40), "#dad6cc", .9), w=3.6, seed=sd)
    o += shape(ellipse_pts(0, 0, 26, 26, 18), "#ffffff", "", w=3, seed=sd + 1)
    o += blob(ellipse_pts(-10, 0, 5, 5, 8), INK) + blob(ellipse_pts(10, 0, 5, 5, 8), INK)
    return o


def icon_tile(sd):
    o = shape(rect_pts(-44, -44, 44, 44, 4), "#6fa6d8", "", w=3.4, seed=sd)
    for j in (-14.7, 14.7):
        o += line([(j, -44), (j, 44)], 3, "#f2f2f2", taper=.05, wmin=.9, seed=sd + 2 + int(j))
        o += line([(-44, j), (44, j)], 3, "#f2f2f2", taper=.05, wmin=.9, seed=sd + 5 + int(j))
    return o


def icon_bulb(sd):
    o = shape([(-14, 22, 1), (14, 22, 1), (14, 40, 1), (-14, 40, 1)], "#9aa0a8", line([(-14, 30), (14, 30)], 2.4, INK, seed=sd + 3), w=3, seed=sd + 1)
    o += shape([(-14, 22), (-30, -4), (-30, -26), (-16, -44), (0, -48), (16, -44), (30, -26), (30, -4), (14, 22)], "#ffe27a",
               blob(ellipse_pts(-10, -24, 8, 12, 10), "#fff6c4"), w=3.6, seed=sd)
    return o


ICONS = [icon_wall, icon_socket, icon_tile, icon_bulb]


def badge_on(u, i, t, vis=1.0):
    X, Z, nx, nz = frame_at(u)
    gx, gy = proj(X, Z)
    k = FOC / Z * 0.9
    bob = 4 * math.sin(t * 2.6 + i * 1.3) * k
    cx, cy = gx, gy - 92 * k + bob
    o = blob(ellipse_pts(gx, gy, 70 * k, 14 * k, 12), "#3d3326", .35 * vis)
    inner = ICONS[i](6100 + i * 10)
    o += line([(gx, gy), (gx, cy + 50 * k)], 8 * k, INK, taper=.05, wmin=.9, seed=6050 + i)
    o += f'<g transform="translate({f(cx)} {f(cy)}) scale({f(k)})">'
    o += shape(ellipse_pts(0, 0, 72, 72, 24), "#f6efe0", blob(ellipse_pts(14, 16, 64, 60, 20), "#e6dcc6", .9), w=5, seed=6000 + i)
    o += f'<g transform="scale(.86)">{inner}</g></g>'
    if vis < 0.999:
        o = f'<g opacity="{vis:.3f}">{o}</g>'
    return o


def fog(t, t0, x_from, x_to, y, n=9, sd=6200, k=1.0):
    """Серый туман: клубы наползают слева направо (от x_from к x_to) с t0, клубятся."""
    p = ease_out(clamp((t - t0) / 0.9), 2)
    if p <= 0:
        return ""
    rs = np.random.RandomState(sd)
    o = []
    front = x_from + (x_to - x_from) * p
    for j in range(n):
        fx = x_from - 120 + (front - x_from + 120) * (j + 0.5) / n + rs.uniform(-30, 30)
        fy = y + rs.uniform(-60, 40) + 10 * math.sin(t * 1.3 + j)
        r = rs.uniform(90, 150) * k * (0.6 + 0.4 * p)
        o.append(blob(P.cloud_pts(fx, fy, r, r * .55, 7, sd=sd + j), "#8d94b4", .92, lib.blur(10)))
        o.append(blob(P.cloud_pts(fx - 10, fy - 16, r * .7, r * .35, 6, sd=sd + 40 + j), "#aab0cc", .85, lib.blur(8)))
    return "".join(o)


def s06(t):
    art = [_ST["bg"], dust(t, 30, 6), _ST["road"], _ST["haze"]]
    # значки на плитках позади Димы; гаснут в тумане к «сделано»
    gone = smooth(SDEL - 0.25, SDEL + 0.2, t)
    for i, u in enumerate(ICON_U):
        e = t - (9.86 + i * 0.08)
        pop = back_out(clamp(e / 0.25), 2.2) if e > 0 else 0.0
        vis = 1 - gone
        if pop > 0.01 and vis > 0.01:
            X, Z, _, _ = frame_at(u)
            gx, gy = proj(X, Z)
            art.append(f'<g transform="translate({f(gx)} {f(gy)}) scale({f(pop)}) translate({f(-gx)} {f(-gy)})">{badge_on(u, i, t, vis)}</g>')
    roller_lying = roller((LIE[0], LIE[1] - 50), -math.pi / 2 + 1.55, 2.6 * DS, sd=5200)
    art.append(roller_lying)
    look = (-0.6, 0.35) if t > VIDNO + 0.1 else (0.5, 0.1)
    art.append(dima(t, DX, FEET_Y, DS, face=1.0, hold=False, droop=0.35 + 0.15 * smooth(SDEL, SDEL + 0.3, t), look=look, mouth="tired",
                    brows="worry", blink=P.bump(t, 10.2, 0.16), lean_add=-0.04 * smooth(VIDNO, VIDNO + 0.3, t)))
    # туман: наползает на значки (слева, позади Димы)
    art.append(fog(t, VIDNO - 0.15, -60, DX - 140, 820, 8, 6200))
    art.append(fog(t, VIDNO + 0.1, -100, DX - 200, 950, 7, 6300, 1.15))
    # камера: ближе, дрейф вбок
    u = clamp((t - 9.8) / 2.3)
    sc = 1.75 + 0.06 * ease_io(u)
    return "".join(art), cam(420 + 60 * ease_io(u), 950 + 10 * u, sc, 0.5 - 0.8 * u)


# ═══════════════════════════════ s07
PLATE_BASE = road_pt(0.3)
PLATE = (PLATE_BASE[0], PLATE_BASE[1] - 170)       # центр таблички


def plate(t, zero):
    """Табличка-счётчик на столбике, наклонена к зрителю; zero 0..1 — «0» печати."""
    cx, cy = PLATE
    o = []
    by = PLATE_BASE[1]
    o.append(blob(ellipse_pts(cx, by, 50, 10, 12), "#3d3326", .4))
    o.append(line([(cx, cy + 40), (cx, by)], 16, INK, taper=.05, wmin=.9, seed=6500))
    o.append(line([(cx, cy + 40), (cx, by)], 10, "#8a6a48", taper=.05, wmin=.9, seed=6501))
    top = [(cx - 120, cy - 50, 1), (cx + 120, cy - 50, 1), (cx + 140, cy + 40, 1), (cx - 140, cy + 40, 1)]
    o.append(shape([(cx - 140, cy + 40, 1), (cx + 140, cy + 40, 1), (cx + 140, cy + 62, 1), (cx - 140, cy + 62, 1)], "#9a7a54", "", w=4, seed=6502))
    inner = blob([(cx + 60, cy - 50), (cx + 120, cy - 50), (cx + 140, cy + 40), (cx + 70, cy + 40)], "#e8e0cc", .9)
    if zero > 0:
        sk = 0.82 * (1 + 0.25 * (1 - ease_out(clamp(zero / 0.25))))
        inner += (f'<g transform="translate({f(cx)} {f(cy - 2)}) scale({f(sk)} {f(0.62 * sk)})">'
                  f'<rect x="-92" y="-82" width="184" height="150" rx="16" fill="none" stroke="#d8342c" stroke-width="9" stroke-dasharray="40 6 22 5"/>'
                  f'<text x="0" y="52" text-anchor="middle" font-family="IDB" font-weight="900" font-size="150" fill="#d8342c">0</text></g>')
        for j, (dx, dy, r) in enumerate(((-118, -30, 6), (112, 18, 5), (-60, 34, 4), (96, -38, 4))):
            inner += blob(ellipse_pts(cx + dx, cy + dy, r, r * .6, 8), "#d8342c", .9)
    o.append(shape(top, "#f7f2e6", inner, w=4.4, seed=6503))
    return "".join(o)


def stamp(x, y, ang=0.0, k=1.0, sd=6600):
    """Печать: (x, y) — середина резиновой подошвы (лицо вниз), ang — наклон."""
    o = [shape([(-70, -10, 1), (70, -10, 1), (70, 6, 1), (-70, 6, 1)], "#d8342c", "", w=3.6, seed=sd),
         shape(rect_pts(-64, -50, 64, -10, 6), "#7a4a2a", blob(rect_pts(20, -50, 64, -10), "#5a341c", .9), w=4, seed=sd + 1),
         shape([(-16, -50, 1), (16, -50, 1), (12, -96, 1), (-12, -96, 1)], "#7a4a2a", blob([(4, -50), (16, -50), (12, -96), (4, -96)], "#5a341c", .9),
               w=3.6, seed=sd + 2),
         shape(ellipse_pts(0, -122, 34, 32, 18), "#9a6238", blob(ellipse_pts(12, -112, 22, 20, 12), "#7a4a2a", .8) +
               blob(ellipse_pts(-10, -132, 8, 6, 8), "#c48a5a", .9), w=4, seed=sd + 3)]
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)}) scale({f(k)})">{"".join(o)}</g>'


def brain_pose(t):
    """Положение мозга и печати: выскакивает (MOZG), смотрит в туман, щурится, замах и удар печатью (NICH)."""
    e = t - MOZG
    pop = back_out(clamp(e / 0.32), 2.2) if e > 0 else 0.0
    bx, by = PLATE[0] + 60, PLATE[1] - 310
    by += 8 * math.sin(t * 2.4)
    up = smooth(NICH - 0.42, NICH - 0.12, t)
    slam = smooth(NICH - 0.12, NICH, t)
    back = smooth(NICH + 0.22, NICH + 0.5, t)
    lift = -90 * up + (90 + 135) * slam - 135 * back * 0.85
    lean_x = -40 * slam * (1 - back * .7)
    y = by + lift
    x = bx + lean_x
    sq = 1.0
    if t > NICH:
        sq = 1 - 0.12 * math.exp(-(t - NICH) * 10) * math.cos((t - NICH) * 26)
    rot = -6 * up + 10 * slam * (1 - back)
    sc = 0.6 * pop
    return x, y, sc, rot, sq, pop


def brain_svg(t):
    x, y, sc, rot, sq, pop = brain_pose(t)
    if pop < 0.01:
        return "", None
    pose = BR.Pose(x, y, sc, rot, sq)
    # печать под мозгом, в двух руках
    sx, sy = pose.pt(brain_art.BCX - 40, brain_art.BCY + 300)
    st = stamp(sx, sy, rot * 0.5, 1.0 * pop)
    hy = sy - 112 * 1.0 * pop
    wl, wr = (sx - 30 * pop, hy), (sx + 30 * pop, hy)
    SL, SR = pose.pt(*BR.SH_L), pose.pt(*BR.SH_R)
    arms = BR.arm(SL, wl, -30, 6701, sc) + BR.arm(SR, wr, 30, 6702, sc)
    squint = smooth(RESH - 0.05, RESH + 0.1, t) * (1 - smooth(12.85, 13.0, t))
    look = (-1.0, 0.3) if t < 12.9 else (-0.3, 0.9)
    mouth = "o" if t < RESH else ("smile" if t > NICH + 0.25 else "o")
    face = BR.face(1.0, look, mouth, t, brow=1.0 if squint > 0.3 else 0.4, blink=0.5 * squint)
    body = f'<g transform="{pose.tf()}">{_ST["brain"]}{face}</g>'
    hands = BR.toon_hand(wl[0], wl[1], 10, 0.7, 6710, sc * 1.3) + BR.toon_hand(wr[0], wr[1], 170, 0.7, 6740, sc * 1.3)
    sh = blob(ellipse_pts(x, FEET_Y - 10, 120 * sc / 0.5, 16, 14), "#141b38", .35 * pop, lib.blur(6))
    return sh + arms + st + body + hands, (sx, sy)


def s07(t):
    art = [_ST["bg"], dust(t, 30, 7), _ST["road"], _ST["haze"]]
    art.append(fog(t, 0, -60, DX - 140, 820, 8, 6200) + fog(t, 0, -100, DX - 200, 950, 7, 6300, 1.15))
    art.append(roller((LIE[0], LIE[1] - 50), -math.pi / 2 + 1.55, 2.6 * DS, sd=5200))
    zero = max(0.0, t - NICH)
    art.append(plate(t, zero))
    droop = 0.5 + 0.5 * smooth(NICH + 0.05, NICH + 0.45, t)
    look = (-0.6, 0.35) if t < MOZG + 0.1 else ((0.7, -0.4) if t < NICH else (0.6, 0.9))
    mouth = "gape" if MOZG < t < NICH + 0.3 else "tired"
    art.append(dima(t, DX, FEET_Y, DS, face=1.0, hold=False, droop=droop, look=look, mouth=mouth, brows="worry",
                    blink=P.bump(t, 12.5, 0.16), lean_add=-0.06 * smooth(MOZG, MOZG + 0.2, t) * (1 - smooth(NICH, NICH + 0.3, t))))
    b, sp = brain_svg(t)
    art.append(b)
    if t > MOZG:
        art.append(P.pop_lines(PLATE[0] + 60, PLATE[1] - 310, t - MOZG, 150, 230, 7, col="#ffe27a", w=10, sd=6800))
    if t > NICH:
        art.append(P.pop_lines(PLATE[0], PLATE[1] - 10, t - NICH, 160, 260, 8, col="#ffe27a", w=12, sd=6820))
    # камера: наезд, удар +8 % на «ничего», тряска
    u = clamp((t - 11.7) / 2.45)
    k = P.kick(t, NICH, 6, 14)
    sc = (1.42 + 0.07 * ease_io(u)) * (1 + 0.08 * k)
    sh = 14 * math.exp(-max(0, t - NICH) * 9) * math.sin((t - NICH) * 60) if t > NICH else 0.0
    return "".join(art), cam(640 + 15 * u + sh, 890 + 10 * u + sh * .5, sc, 0.4 - 0.8 * u)


def build_static():
    if _ST:
        return
    _ST["bg"] = background()
    _ST["road"] = road()
    _ST["haze"] = haze()
    _ST["brain"] = brain_art.brain(0, 0.0, stem=False)
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s05": s05, "s06": s06, "s07": s07}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{art}</g>')
