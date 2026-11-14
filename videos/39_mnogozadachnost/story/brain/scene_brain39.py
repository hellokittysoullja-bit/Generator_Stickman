"""Сцена «мозг» рилса 39 (s11 s12 s13): мозг-персонаж рилса 35 (ножки в кедах, ручки-«лапша», большие глаза, розовый)
скачет по парящим платформам-карточкам дел в темноте: «ОТЧЁТ» → «СОЗВОН» → «ЧАТ» → «ПОЧТА».
s11 «Мозг просто быстро прыгает» (19.96–21.56): влёт камеры, мозг на «ОТЧЁТЕ» пружинит от нетерпения, на «прыгает»
    (21.17) прыгает к «СОЗВОНУ» (присед → вытяжка → полёт).
s12 «с дела на дело» (21.56–23.1): приземления на «дела» (21.68) и «дело» (22.08), пунктирные дуги прыжков за ним,
    камера ведёт; на «каждом» (22.8) — разбег к следующему прыжку.
s13 «на каждом прыжке что-то теряет» (23.1–24.68): крупно; в прыжке на «прыжке» (23.17) у мозга отлетает кусочек-пазл
    (в мозге остаётся вырез с фоном), мозг приземляется на «ПОЧТУ», кусочек падает в темноту на «теряет» (24.0),
    мозг растерянно оглядывается, разводит ручками, над ним «?».
Всё — функция общего времени ролика t, удары — по voice/words.json. Прыжки: присед-подготовка, вытяжка на отрыве,
одно короткое сжатие на приземлении с маленьким отскоком (без «желе»)."""
import math

import numpy as np

import body as B
import brain_art as BA
import lib
from body import EYE_R, HIP_L, HIP_R, LEG, SH_L, SH_R, Pose, arm, face, leg, rays, star, text, toon_hand
from brain_art import BCX, BCY
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_io, ease_out, ellipse_pts, f, fill_d, ink_closed, line, mix, rect_pts,
                 shape, smooth, svg)

_ST = {}
WT = {}


def word_t(w, after=19.5):
    """Начало первого вхождения слова после after (раньше в ролике есть «дела», «дело»)."""
    if not WT:
        for x in lib.words():
            WT.setdefault(x["word"].strip(",.?!").lower(), []).append(x["start"])
    return min(v for v in WT[w] if v >= after)


T_MOZG = word_t("мозг")            # 19.96
T_PROSTO = word_t("просто")        # 20.32
T_BYSTRO = word_t("быстро")        # 20.80
T_PRYG = word_t("прыгает")         # 21.17
T_DELA = word_t("дела")            # 21.68
T_DELO = word_t("дело")            # 22.08
T_KAZHD = word_t("каждом")         # 22.80
T_PRYZH = word_t("прыжке")         # 23.17
T_TER = word_t("теряет")           # 24.00

SC = 0.8                            # масштаб мозга
STAND = 0.86 * LEG * SC + 106 * SC  # центр мозга над верхом платформы (ножки чуть согнуты)
# платформы: x центра, верх, цвет, надпись, значок
PL = [(760.0, 1050.0, "#6fa8ff", "ОТЧЁТ", "doc"),
      (300.0, 955.0, "#6fcf9c", "СОЗВОН", "phones"),
      (-170.0, 1045.0, "#b79cff", "ЧАТ", "chat"),
      (-650.0, 965.0, "#ffb36b", "ПОЧТА", "mail")]
PW, PD, PF = 340.0, 44.0, 132.0     # ширина, глубина верха, высота лицевой грани
# прыжки: начало приседа, отрыв, приземление, откуда, куда, высота дуги
JUMPS = [(T_PRYG - 0.22, T_PRYG, T_DELA - 0.02, 0, 1, 230.0),
         (T_DELA + 0.06, T_DELA + 0.17, T_DELO, 1, 2, 150.0),
         (T_KAZHD - 0.32, T_KAZHD - 0.12, T_PRYZH + 0.19, 2, 3, 300.0)]
LID = "#f6a9bc"


# ───────────────────────── платформы
def plat(i, t):
    """(x, верх) платформы i: парит, проседает от приземления, чуть — от отрыва."""
    x, g = PL[i][0], PL[i][1]
    g += 7 * math.sin(t * 1.6 + i * 1.9)
    for (tc, to, tl, a, b, h) in JUMPS:
        if b == i:
            g += B.ease_kick(t - tl, 18, 12, 7)
        if a == i:
            g += B.ease_kick(t - to, 9, 14, 8)
    return x, g


def icon(kind, x, y, sd):
    s = []
    if kind == "doc":
        pg = lib.T([(-34, -44, 1), (18, -44, 1), (34, -28, 1), (34, 44, 1), (-34, 44, 1)], x, y, 1, -6)
        inner = "".join(line(lib.T([(-20, yy), (20 if k else 4, yy)], x, y, 1, -6), 5, "#6f87b8", seed=sd + k, taper=.2, wmin=.7)
                        for k, yy in enumerate((-18, -2, 14, 28)))
        s.append(shape(pg, "#ffffff", inner, w=4, seed=sd + 10))
        s.append(shape(lib.T([(18, -44, 1), (18, -28, 1), (34, -28, 1)], x, y, 1, -6), "#d9e2f2", "", w=3.4, seed=sd + 11))
    elif kind == "phones":
        band = [(x - 40 + 80 * u, y - 4 - 46 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 9)]
        s.append(line(band, 13, INK, taper=.02, wmin=.95, seed=sd))
        s.append(line(band, 6, "#4d5872", taper=.02, wmin=.95, seed=sd + 1))
        for k, sx in enumerate((-1, 1)):
            cup = rect_pts(x + sx * 40 - 15, y - 12, x + sx * 40 + 15, y + 34, 12)
            s.append(shape(cup, "#2e3448", blob(rect_pts(x + sx * 40 - 9, y - 6, x + sx * 40 - 2, y + 26, 3), "#5c6788"), w=4, seed=sd + 3 + k))
    elif kind == "chat":
        pts = ellipse_pts(x, y - 6, 44, 32, 18)
        tail = [(x - 22, y + 18), (x - 34, y + 42, 1), (x - 4, y + 22)]
        s.append(shape(tail, "#ffffff", "", w=4, seed=sd + 1))
        s.append(shape(pts, "#ffffff", "", w=4, seed=sd))
        for k in range(3):
            s.append(f'<circle cx="{f(x - 20 + 20 * k)}" cy="{f(y - 6)}" r="6.5" fill="#7a63c9"/>')
    else:
        env = rect_pts(x - 42, y - 28, x + 42, y + 30, 4)
        inner = line([(x - 40, y - 26), (x, y + 6), (x + 40, y - 26)], 4, INK, seed=sd + 2, taper=.2, wmin=.6)
        s.append(shape(env, "#ffffff", inner, w=4, seed=sd))
    return "".join(s)


def platform(i, t):
    x, g = plat(i, t)
    col, name, ic = PL[i][2], PL[i][3], PL[i][4]
    sd = 5000 + i * 100
    s = []
    # свет платформы снизу в темноту (свет, не фигура)
    gr = lib.rad_grad([(0, col, .32), (1, col, 0)], x, g + PF + 30, 260, 120)
    s.append(f'<ellipse cx="{f(x)}" cy="{f(g + PF + 30)}" rx="260" ry="120" fill="url(#{gr})"/>')
    x0, x1 = x - PW / 2, x + PW / 2
    yf = g + PD / 2            # передний край верха
    yb = g - PD / 2            # задний край
    top = [(x0 + 14, yb, 1), (x1 - 14, yb, 1), (x1, yf, 1), (x0, yf, 1)]
    front = rect_pts(x0, yf, x1, yf + PF, 18)
    front = [(x0, yf, 1), (x1, yf, 1)] + [p for p in front if p[1] > yf + 17]
    inner = blob(rect_pts(x1 - 46, yf - 4, x1 + 4, yf + PF + 4), lib.mul(col, (.72, .72, .8)), .95)
    inner += blob(rect_pts(x0 - 4, yf - 2, x1 + 4, yf + 10), lib.mul(col, (1.12, 1.12, 1.08)))
    s.append(shape(front, col, inner, w=5, seed=sd + 1))
    s.append(shape(top, mix(col, "#ffffff", .45), blob([(x1 - 60, yb), (x1 - 14, yb), (x1, yf), (x1 - 46, yf)], mix(col, "#ffffff", .2)),
                   w=4.6, seed=sd + 2))
    s.append(icon(ic, x0 + 66, yf + PF / 2 + 2, sd + 20))
    tx = x0 + 128 + (PW - 128 - 22) / 2
    size = 50 if len(name) <= 5 else 44
    s.append(text(tx, yf + PF / 2 + size * .36, name, size, "#ffffff", sw=8))
    return "".join(s)


# ───────────────────────── фон: темнота, дальние карточки (параллакс), пылинки
def background():
    g = lib.lin_grad([(0, "#262d58", 1), (.45, "#1b2046", 1), (1, "#07081a", 1)], 0, -900, 0, 2600, units="userSpaceOnUse")
    return f'<rect x="-3000" y="-1500" width="7000" height="5500" fill="url(#{g})"/>'


FAR = [(-900, 560, 0.55, "#33406e"), (-330, 380, 0.45, "#2f3a66"), (260, 470, 0.5, "#3a3a6a"), (820, 360, 0.42, "#2d3864"),
       (1250, 600, 0.5, "#363f70"), (-1350, 420, 0.45, "#323b6a")]


def far_layer(t):
    s = []
    for k, (x, y, k_, col) in enumerate(FAR):
        y += 10 * math.sin(t * 0.9 + k)
        w, h = 200 * k_, 120 * k_
        pts = lib.T(rect_pts(-w / 2, -h / 2, w / 2, h / 2, 14 * k_), x, y, 1, 6 * math.sin(k * 2.1))
        s.append(shape(pts, col, blob(lib.T(rect_pts(w / 2 - 30 * k_, -h / 2, w / 2, h / 2), x, y, 1, 6 * math.sin(k * 2.1)), "#262f58"),
                       w=3, seed=6000 + k, ink_color="#161a36"))
    rs = np.random.RandomState(9)
    for k in range(70):
        x, y = rs.uniform(-1800, 1800), rs.uniform(-200, 1900)
        r = rs.uniform(1.6, 3.6)
        tw = .35 + .3 * math.sin(t * rs.uniform(1.5, 3.5) + k)
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#cfd8ff" opacity="{tw:.3f}"/>')
    return "".join(s)


def motes(t):
    rs = np.random.RandomState(4)
    s = []
    for k in range(40):
        x0, y0 = rs.uniform(-1100, 1300), rs.uniform(200, 1700)
        sp, ph, r = rs.uniform(14, 30), rs.uniform(0, 6.28), rs.uniform(2.2, 4.2)
        x = x0 + 30 * math.sin(t * 0.6 + ph)
        y = y0 - sp * (t - 19)
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#c9d6ff" opacity="{.2 + .12 * math.sin(t * 2 + ph):.3f}"/>')
    return "".join(s)


# ───────────────────────── траектория мозга
def landing_q(e):
    """Сжатие после приземления: одно короткое сжатие и маленький отскок (e — секунды после касания)."""
    if e < 0:
        return 0.0
    q = 0.13 * math.sin(math.pi * clamp(e / 0.2)) ** 0.8 if e < 0.2 else 0.0
    q -= 0.025 * math.sin(math.pi * clamp((e - 0.2) / 0.16))
    return q


def air_xy(J, u):
    tc, to, tl, a, b, h = J
    x0, g0 = plat(a, to)
    x1, g1 = plat(b, tl)
    y0 = g0 - STAND + 44 * SC
    y1 = g1 - STAND
    up = ease_out(u / 0.18, 2) if u < 0.18 else 1.0
    yb = y0 + (y1 - y0) * u - 44 * SC * up
    return x0 + (x1 - x0) * u, yb - h * 4 * u * (1 - u)


def state(t):
    """Где мозг и что с телом: x, y центра, наклон, сжатие, ступни, фаза."""
    st = {"phase": "stand", "pl": 0, "e_land": 99.0, "u": 0.0, "J": None}
    cur = None
    for J in JUMPS:
        if t >= J[0]:
            cur = J
    if cur is None:
        st["pl"] = 0
    else:
        tc, to, tl, a, b, h = cur
        st["J"] = cur
        if t < to:
            st["phase"], st["pl"], st["c"] = "crouch", a, ease_io((t - tc) / (to - tc))
        elif t < tl:
            st["phase"], st["u"] = "air", (t - to) / (tl - to)
        else:
            st["pl"], st["e_land"] = b, t - tl
    if st["phase"] == "air":
        x, y = air_xy(cur, st["u"])
        u = st["u"]
        sq = 1 + 0.09 * (1 - smooth(0, .32, u)) + 0.035 * smooth(.72, .95, u)
        rot = -11 * (1 - smooth(0, .5, u)) + 6 * smooth(.55, 1, u)
        st.update(x=x, y=y, sq=sq, rot=rot)
        return st
    px, g = plat(st["pl"], t)
    br = math.sin(t * 2.6)
    y = g - STAND + 3 * br
    x = px
    sq = 1 + 0.012 * br
    rot = 1.5 * math.sin(t * 1.7)
    # нетерпение до первого прыжка: пружинит на «просто» и «быстро»
    if cur is None:
        for tw in (T_MOZG, T_PROSTO, T_BYSTRO):
            k = B.ease_kick(t - tw + 0.04, 1.0, 13, 7)
            y += 26 * SC * k
            sq -= 0.06 * k
    if st["phase"] == "crouch":
        c = st["c"]
        y += 44 * SC * c
        sq -= 0.1 * c
        rot += -7 * c
    e = st["e_land"]
    if e < 1:
        q = landing_q(e)
        y += 120 * SC * q
        sq -= q
        rot += 6 * math.exp(-e * 9) * math.cos(min(e * 12, math.pi))
    st.update(x=x, y=y, sq=sq, rot=rot, g=g)
    return st


def feet(st, pose, t):
    hl, hr = np.array(pose.pt(*HIP_L)), np.array(pose.pt(*HIP_R))
    if st["phase"] != "air":
        g = st["g"]
        return (hl[0] - 16, g), (hr[0] + 12, g)
    u = st["u"]
    L = LEG * SC
    take = np.array([34 * SC, 0.97 * L])        # ноги вытянуты назад-вниз (отрыв)
    tuck = np.array([-14 * SC, 0.56 * L])       # поджаты
    land = np.array([-24 * SC, 0.95 * L])       # вытянуты вперёд к платформе
    if u < 0.5:
        d = take + (tuck - take) * smooth(0, .3, u)
    else:
        d = tuck + (land - tuck) * smooth(.62, .92, u)
    return tuple(hl + d + np.array([-6, 0])), tuple(hr + d + np.array([8, 0]))


def lerp(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def arms_pose(st, pose, t):
    """Запястья и углы кистей: висят / отведены назад (присед) / вверх (полёт) / в стороны (баланс)."""
    sc = pose.sc
    SL, SR = pose.pt(*SH_L), pose.pt(*SH_R)
    a = 10 * math.sin(t * 2.3)
    hang = ((SL[0] - 74 * sc + a * .4, SL[1] + 58 * sc), (SR[0] + 74 * sc - a * .4, SR[1] + 58 * sc), 118 + a * .3, 62 - a * .3)
    back = ((SL[0] + 10 * sc, SL[1] + 70 * sc), (SR[0] + 96 * sc, SR[1] + 40 * sc), 70, 30)
    up = ((SL[0] - 70 * sc, SL[1] - 120 * sc), (SR[0] + 40 * sc, SR[1] - 130 * sc), -112, -70)
    side = ((SL[0] - 120 * sc, SL[1] - 10 * sc), (SR[0] + 120 * sc, SR[1] - 20 * sc), 190, -10)

    def mixp(p, q, u):
        return (lerp(p[0], q[0], u), lerp(p[1], q[1], u), p[2] + (q[2] - p[2]) * u, p[3] + (q[3] - p[3]) * u)
    ph = st["phase"]
    if ph == "crouch":
        return mixp(hang, back, st["c"])
    if ph == "air":
        u = st["u"]
        p = mixp(back, up, smooth(0, .25, u))
        return mixp(p, side, smooth(.6, .95, u))
    e = st["e_land"]
    if st["J"] is None:
        return hang
    return mixp(side, hang, smooth(.05, .45, e))


# ───────────────────────── кусочек-пазл
def _tab(A, B_, n, k=10):
    """Сторона пазла от A к B (B не входит) с круглым «ушком» в сторону n."""
    A, B_, n = np.array(A, float), np.array(B_, float), np.array(n, float)
    d = B_ - A
    L = np.linalg.norm(d)
    tv = d / L
    neck, R = 0.13 * L, 0.17 * L
    c = A + tv * 0.5 * L + n * (neck * .7 + R * .8)
    pa = A + tv * (0.5 * L - neck * 0.55) + n * neck * .7
    pb = A + tv * (0.5 * L + neck * 0.55) + n * neck * .7
    a0 = math.atan2(*(pa - c)[::-1])
    a1 = math.atan2(*(pb - c)[::-1])
    af = math.atan2(n[1], n[0])
    dp = (a1 - a0) % (2 * math.pi)
    if not ((af - a0) % (2 * math.pi) < dp):
        dp -= 2 * math.pi
    pts = [tuple(A) + (1,), tuple(A + tv * (0.5 * L - neck * 0.55)), tuple(pa)]
    pts += [tuple(c + R * np.array([math.cos(a0 + dp * j / k), math.sin(a0 + dp * j / k)])) for j in range(1, k)]
    pts += [tuple(pb), tuple(A + tv * (0.5 * L + neck * 0.55))]
    return pts


def piece_poly():
    """Кусочек в локальных координатах мозга: верх-затылок; ушко влево (в мозг), выемка снизу."""
    x0, x1, y0, y1 = BCX + 40, BCX + 150, BCY - 190, BCY - 52
    pts = [(x0, y0, 1), (x1, y0, 1)]
    pts += _tab((x1, y1), (x0, y1), (0, -1))          # низ справа налево: ушко вверх — выемка в кусочке
    pts += _tab((x0, y1), (x0, y0), (-1, 0))          # левая снизу вверх: ушко влево — в мозг
    return pts


PIECE_C = (BCX + 95, BCY - 105)


def piece_geo():
    if "pc" in _ST:
        return _ST["pc"]
    pts = piece_poly()
    d = fill_d(pts)
    ink = ink_closed(pts, 5.0, var=.2, weight=.4, seed=77)
    _ST["pc"] = (pts, d, ink)
    return _ST["pc"]


def piece_art(levels):
    """Сам кусочек (локальные координаты мозга): мозг, вырезанный по контуру пазла, + тушь разреза внутри мозга."""
    pts, d, ink = piece_geo()
    c = lib.uid()
    lib.DEFS.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
    s = f'<g clip-path="url(#{c})">{BA.brain(levels, pink=True)}</g>'
    s += f'<g clip-path="url(#{BA._G["oclip"]})"><path d="{ink}" fill="{INK}"/></g>'
    return s


def hole_mask():
    pts, d, ink = piece_geo()
    m = lib.uid("m")
    lib.DEFS.append(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="-3000" y="-3000" width="8000" height="8000">'
                    f'<rect x="-3000" y="-3000" width="8000" height="8000" fill="#ffffff"/><path d="{d}" fill="#000000"/></mask>')
    return m


def piece_motion(t, pose0):
    """Полёт кусочка после отрыва: вверх-назад, кувырок, падение в темноту (x, y мира, поворот, масштаб, яркость)."""
    e = t - T_PRYZH
    px, py = pose0.pt(*PIECE_C)
    x = px + 170 * e
    y = py - 430 * e + 0.5 * 2500 * e * e
    rot = pose0.rot + 430 * e
    far = smooth(T_TER - 0.15, T_TER + 0.55, t)
    k = 1 - 0.75 * far
    bright = 1 - 0.8 * far
    return x, y, rot, k, bright


# ───────────────────────── персонаж
def character(t, st, sid):
    pose = Pose(st["x"], st["y"], SC, st["rot"], st["sq"])
    B.set_skin(1.0)
    wl, wr, al, ar = arms_pose(st, pose, t)
    fl, fr = feet(st, pose, t)
    hl, hr = pose.pt(*HIP_L), pose.pt(*HIP_R)
    legs = leg(hr, fr, SC, -1, 1200) + leg(hl, fl, SC, -1, 1220)
    # лицо
    lost = smooth(T_PRYZH + 0.35, T_PRYZH + 0.5, t)        # заметил потерю
    look = (-0.85, 0.05)
    mouth = "smile"
    brow, tilt = 0.3, 0.0
    if st["phase"] == "air":
        mouth = "grin"
        look = (-0.9, 0.3)
    if t > T_PRYZH + 0.3:
        # оглядывается: назад (за кусочком) → вниз → влево → вправо
        tt = t - (T_PRYZH + 0.3)
        lx = 0.9 * smooth(0, .15, tt) - 1.8 * smooth(.75, .95, tt) + 1.6 * smooth(1.15, 1.32, tt)
        ly = -0.2 + 1.0 * smooth(.25, .45, tt) * (1 - smooth(.7, .9, tt))
        look = (lx, ly)
        mouth = "o"
        brow, tilt = 0.9 * lost, -0.5 * lost
    op = 1.0
    for tb in (20.55, 22.32, 24.45):
        if abs(t - tb) < 0.08:
            op = min(op, abs(t - tb) / 0.08)
    fc = face(op, look, mouth, t, brow=brow, brow_tilt=tilt, lid_col=LID, blush=0.45)
    lv = {}
    inner = BA.brain(lv, pink=True) + fc
    popped = t >= T_PRYZH
    out = [shadow_under(st, t)]
    out.append(legs)
    out.append(arm(pose.pt(*SH_L), wl, -40, 1301, SC))
    out.append(arm(pose.pt(*SH_R), wr, 40, 1302, SC))
    if popped:
        m = hole_mask()
        pts, d, ink = piece_geo()
        cut = f'<g clip-path="url(#{BA._G["oclip"]})"><path d="{ink}" fill="{INK}"/></g>'
        out.append(f'<g transform="{pose.tf()}"><g mask="url(#{m})">{inner}</g>{cut}</g>')
    else:
        crack = ""
        if t > T_PRYZH - 0.1:
            pts, d, ink = piece_geo()
            crack = f'<g clip-path="url(#{BA._G["oclip"]})"><path d="{ink}" fill="{INK}"/></g>'
        out.append(f'<g transform="{pose.tf()}">{inner}{crack}</g>')
    out.append(toon_hand(wl[0], wl[1], al, 0.3, 1330, SC * 1.3))
    out.append(toon_hand(wr[0], wr[1], ar, 0.3, 1360, SC * 1.3))
    return "".join(out), pose


def shadow_under(st, t):
    if st["phase"] == "air":
        J = st["J"]
        u = st["u"]
        x0, g0 = plat(J[3], t)
        x1, g1 = plat(J[4], t)
        # тень на той платформе, над которой мозг
        for (px, g) in ((x0, g0), (x1, g1)):
            if abs(st["x"] - px) < PW / 2 - 30:
                hgt = g - STAND - st["y"]
                r = 90 * max(0.4, 1 - hgt / 500)
                return blob(ellipse_pts(st["x"], g + 6, r, r * .2, 14), "#1b1838", .5, blur(6))
        return ""
    return blob(ellipse_pts(st["x"] + 4, st["g"] + 6, 110, 20, 14), "#1b1838", .5, blur(6))


def trails(t):
    """Пунктир дуг прыжков: рисуется за мозгом и остаётся."""
    s = []
    for j, J in enumerate(JUMPS):
        tc, to, tl, a, b, h = J
        if t <= to:
            continue
        uu = clamp((t - to) / (tl - to))
        n = 26
        P = [air_xy(J, uu * i / n) for i in range(n + 1)]
        P = [(x, y + 110 * SC) for x, y in P]
        for i in range(0, n, 2):
            seg = [P[i], P[i + 1]]
            if math.hypot(seg[1][0] - seg[0][0], seg[1][1] - seg[0][1]) < 4:
                continue
            s.append(line(seg, 7, "#efe6ff", taper=.25, wmin=.6, seed=7000 + j * 50 + i))
    return "".join(s)


def piece_layer(t):
    if t < T_PRYZH:
        return ""
    st0 = state(T_PRYZH)
    pose0 = Pose(st0["x"], st0["y"], SC, st0["rot"], 1.0)
    x, y, rot, k, bright = piece_motion(t, pose0)
    art = piece_art({})
    flt = f' style="filter:brightness({bright:.3f})"' if bright < 0.995 else ""
    return (f'<g{flt} transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(SC * k)}) translate({-PIECE_C[0]} {-PIECE_C[1]})">'
            f'{art}</g>')


def pop_fx(t):
    e = t - T_PRYZH
    if e < -0.01 or e > 0.5:
        return ""
    st0 = state(T_PRYZH)
    pose0 = Pose(st0["x"], st0["y"], SC, st0["rot"], 1.0)
    px, py = pose0.pt(*PIECE_C)
    s = rays(px + 10, py - 10, e, 7400, r=50, n=9, col="#ffe27a", dur=0.35, L0=42, w=8)
    for j in range(4):
        kk = back_out(clamp((e - j * 0.04) / 0.2), 2.2) * (1 - smooth(.3, .5, e))
        if kk > 0.03:
            a = -0.9 + j * 0.6
            s += star(px + math.cos(a) * (70 + 60 * e), py + math.sin(a) * (70 + 60 * e) - 30, 20 * kk, "#fff3b0", 7450 + j, rot=30 * j)
    return s


def puzzled(t, pose):
    """«?» над головой и капля пота после потери."""
    e = t - (T_TER - 0.12)
    if e < 0:
        return ""
    k = back_out(clamp(e / 0.28), 2.4)
    hx, hy = pose.pt(BCX - 60, BCY - 175)
    s = f'<g transform="translate({f(hx)} {f(hy - 70)}) rotate({f(8 * math.sin(t * 5))}) scale({f(k)})">'
    s += text(0, 30, "?", 120, "#ffe27a", sw=10) + "</g>"
    ek = clamp((t - (T_PRYZH + 0.5)) / 0.9)
    if ek > 0:
        sx, sy = pose.pt(BCX - 190, BCY - 100)
        s += B.sweat(sx - 10, sy + 60 * ek * ek, 1.15)
    return s


# ───────────────────────── камера
def follow(t, lag=0.06, n=8):
    xs, ys = [], []
    for k in range(n):
        st = state(t - lag * k)
        xs.append(st["x"])
        ys.append(st["y"])
    return sum(xs) / n, sum(ys) / n


def camera(sid, t):
    fx, fy = follow(t)
    if sid == "s11":
        a = 19.76
        u = clamp((t - a) / 0.24)
        k = ease_out(u, 3)
        e = t - a - 0.24
        over = 0.05 * math.exp(-e * 9) * math.sin(min(e * 14, math.pi)) if e > 0 else 0.0
        s = 1.08 * (1 / 1.42 + (1 - 1 / 1.42) * k) * (1 + over) * (1 + 0.03 * smooth(20.0, 21.7, t))
        rot = -3.5 * (1 - k) + 0.6 * math.sin(t * 0.8)
        return fx - 190 + 60 * (1 - k), fy + 175 - 40 * (1 - k), s, rot
    if sid == "s12":
        s = 1.04 + 0.03 * math.sin((t - 21.36) * 0.9)
        s *= 1 + B.ease_kick(t - T_DELA, 0.025, 14, 7) + B.ease_kick(t - T_DELO, 0.025, 14, 7)
        return fx - 170, fy + 175, s, 0.8 * math.sin(t * 0.7)
    # s13: крупно, удар на отрыве кусочка и на приземлении, камера опускается за падающим кусочком
    fx, fy = follow(t, 0.04, 6)
    u = clamp((t - 22.9) / 1.98)
    s = 1.42 + 0.1 * ease_io(u)
    s *= 1 + B.ease_kick(t - T_PRYZH, 0.06, 16, 7) + B.ease_kick(t - JUMPS[2][2], 0.03, 16, 8)
    sh = math.exp(-max(t - T_PRYZH, 0) * 9) * (t > T_PRYZH)
    jx = 9 * sh * math.sin(t * 61)
    jy = 7 * sh * math.sin(t * 47 + 1)
    down = 150 * smooth(T_PRYZH + 0.4, T_TER + 0.1, t)
    right = 150 * smooth(T_PRYZH + 0.15, T_TER, t)
    rot = -1.2 + 2.0 * u + 1.5 * sh * math.sin(t * 33)
    return fx - 70 + right + jx, fy + 120 + down + jy, s, rot


def build_static():
    if _ST.get("ok"):
        return
    BA.init()
    _ST["bg"] = background()
    piece_geo()
    lib.static_done()
    _ST["ok"] = 1


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    cx, cy, s, rot = camera(sid, t)
    st = state(t)
    ch, pose = character(t, st, sid)
    world = [motes(t), trails(t)]
    # кусочек падает ЗА платформы (в темноту), мозг — перед ними
    world += [platform(i, t) for i in range(len(PL))]
    world.append(piece_layer(t))
    world.append(ch)
    world.append(pop_fx(t))
    world.append(puzzled(t, pose))
    far = f'<g transform="{cam(cx * .45 + 300, cy * .6 + 400, s * .7, rot * .5)}">{far_layer(t)}</g>'
    vg = lib.rad_grad([(0, "#000000", 0), (.55, "#000000", 0), (1, "#05061a", .55)], 540, 860, 1050, 1300)
    return svg(f'<rect width="{W}" height="{H}" fill="#1b2046"/><g transform="{cam(cx, cy, s, rot)}">{_ST["bg"]}</g>{far}'
               f'<g transform="{cam(cx, cy, s, rot)}">{"".join(world)}</g><rect width="{W}" height="{H}" fill="url(#{vg})"/>')
