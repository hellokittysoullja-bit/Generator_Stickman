"""Сцена form рилса 26 — листок-анкета британского опыта (без букв: шапка и пункты — серые полоски-«текст»).
s10 (16.2–18.04): взгляд участника. Рука исследователя (белый рукав халата) подаёт листок, держа за верхний угол; на «дали»
     (16.56) снизу поднимаются руки участника в синей спортивной куртке, на «листок» (17.12) большие пальцы ложатся на
     лист, рука исследователя отпускает и уходит, листок в руках подтягивается ближе.
s11 (17.64–20.48): тот же листок на столе крупно; рука участника с ручкой (хват из рилса 24/25) пишет рукописью
     «когда: среда, 7:00» (18.0–18.9) и «где: парк у дома» (19.4–20.1). Буквы — контуры Caveat 600 (form_glyphs.json),
     каждая проявляется маской по ходу пера (как scene_list рилса 25)."""
import json
import math
import os

import numpy as np

import hand
import lib
from lib import (DEFS, INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line,
                 lin_grad, mix, rad_grad, rect_pts, shape, smooth, svg)
from parts import sausage

SW, SH_ = 880, 1280          # лист в своих координатах
GIVE, TAKE = 16.56, 17.12
SKIN, SKIN_SH, NAIL = "#ecc4a2", "#d39f83", "#f6dccb"
SKIN_R, SKIN_R_SH = "#c99470", "#a87556"
JACKET, JACKET_SH, JACKET_ST = "#2d55a8", "#20407f", "#f4f1ea"
_ST = {}

# рука с ручкой — в синем рукаве участника (hand.py читает цвета из своих глобальных имён в момент вызова)
hand.HOOD, hand.HOOD_SH, hand.HOOD_SH2, hand.FOLD = JACKET, JACKET_SH, "#18336a", "#132a58"


# ───────────────────────── листок-анкета (локальные координаты 0..SW × 0..SH_)
ROWS = [520, 760]            # линии под ответы (s11 пишет над ними)


def form(sd=0):
    s = []
    inner = ""
    g = lin_grad([(0, "#ffffff", 0), (1, "#ddd4bf", .3)], 0, 0, 0, 1)
    inner += f'<rect x="-20" y="-20" width="{SW + 40}" height="{SH_ + 40}" fill="url(#{g})"/>'
    # шапка: значок-кружок и «заголовок» полосами
    inner += shape(ellipse_pts(110, 120, 46, 46, 16), "#e9eef6", line([(86, 120), (104, 138), (138, 100)], 7, "#2d55a8", seed=sd + 1), w=3.4, seed=sd + 2)
    inner += f'<rect x="190" y="88" width="420" height="30" rx="8" fill="#4a5164"/>'
    inner += f'<rect x="190" y="136" width="300" height="16" rx="6" fill="#aab0bc"/>'
    for k, wd in enumerate([660, 610, 640]):
        inner += f'<rect x="70" y="{232 + k * 40}" width="{wd}" height="14" rx="6" fill="#c3c8d1"/>'
    # поля ответа: короткая серая «метка» слева не нужна — строки пустые, только линейка
    for k, y in enumerate(ROWS):
        inner += line([(70, y), (SW - 70, y)], 3.4, "#7d8597", taper=.05, wmin=.9, seed=sd + 10 + k)
    # пункты с квадратиками
    for k in range(3):
        y = 900 + k * 70
        inner += shape(rect_pts(70, y, 108, y + 38, 4), "#ffffff", "", w=3, seed=sd + 20 + k)
        inner += f'<rect x="132" y="{y + 12}" width="{[380, 300, 420][k]}" height="14" rx="6" fill="#c3c8d1"/>'
    inner += line([(SW - 330, 1180), (SW - 70, 1180)], 3, "#7d8597", taper=.05, wmin=.9, seed=sd + 30)
    s.append(shape([(0, 0, 1), (SW, 0, 1), (SW, SH_, 1), (0, SH_, 1)], "#fbf9f2", inner, w=4.4, seed=sd + 40))
    return "".join(s)


# ───────────────────────── s10: руки берут листок (POV)
def room10():
    s = []
    lin_grad([(0, "#cfe0dc", 1), (1, "#a9c3c2", 1)], 0, 0, 0, 1, gid="gWall10")
    s.append(f'<rect x="-400" y="-400" width="{W + 800}" height="{H + 800}" fill="url(#gWall10)"/>')
    # окно с утренним светом (мягко, «не в фокусе»)
    s.append(blob(rect_pts(640, 120, 1240, 760, 30), "#fff4d8", .85, blur(18)))
    s.append(blob(rect_pts(-300, 200, 260, 900, 30), "#8fb0ae", .7, blur(22)))
    # исследователь за столом: белый халат пятном
    s.append(blob(ellipse_pts(780, 1120, 330, 380, 20), "#f2f2f0", .95, blur(14)))
    s.append(blob(ellipse_pts(860, 1160, 220, 300, 18), "#d8dcdf", .8, blur(16)))
    # стол
    s.append(shape([(-400, 1330, 1), (W + 400, 1290, 1), (W + 400, H + 400, 1), (-400, H + 400, 1)], "#c9a27a",
                   blob([(-400, 1380), (W + 400, 1340), (W + 400, H + 400), (-400, H + 400)], "#b48a63", .8), w=5, seed=60))
    return "".join(s)


def thumb_pts(base, ang, L, wd):
    """Средняя линия большого пальца: от основания под углом ang (градусы), чуть выгнута."""
    a = math.radians(ang)
    pts = []
    for k in range(5):
        u = k / 4
        bend = 0.22 * math.sin(math.pi * u)
        aa = a - bend
        pts.append((base[0] + math.cos(a) * L * u - math.sin(a) * L * bend * .5, base[1] + math.sin(a) * L * u + math.cos(a) * L * bend * .5))
    return pts


def grip_hand(x, y, rot, press, skin, skin_sh, sleeve, sleeve_sh, stripe, sd, layer):
    """Кисть, держащая край листа: в своих координатах край листа — y = 0, лист выше (y < 0), рука снизу.
    layer='back' — рукав, кисть, пальцы (уходят за лист); layer='front' — большой палец поверх листа.
    press 0..1: большой палец от приподнятого (0) до лежащего на листе (1)."""
    s = []
    if layer == "back":
        # рукав и манжета
        sl = [(-78, 420, 1), (-70, 150), (-60, 104, 1), (64, 104, 1), (78, 150), (90, 420, 1)]
        inner = blob([(20, 104), (64, 104), (78, 150), (90, 420), (30, 420)], sleeve_sh, .9)
        if stripe:
            inner += line([(-50, 420), (-48, 150), (-44, 112)], 9, stripe, taper=.05, wmin=.9, seed=sd + 1)
        s.append(shape(sl, sleeve, inner, w=4.6, seed=sd + 2))
        s.append(shape(rect_pts(-66, 92, 70, 130, 12), sleeve_sh, "", w=4, seed=sd + 3))
        # пальцы (за листом, когда рука держит; видны, пока рука тянется): основания под ладонью
        for k, (bx, fa, Lf) in enumerate([(-34, -100, 104), (-10, -93, 118), (14, -86, 112), (36, -79, 92)]):
            a = math.radians(fa)
            fp = [(bx, -40)]
            for j in range(1, 4):
                aa = a + math.radians(6 * j)
                fp.append((fp[-1][0] + math.cos(aa) * Lf / 3, fp[-1][1] + math.sin(aa) * Lf / 3))
            pl = sausage(fp, 27, 24)
            s.append(shape(pl, skin, blob([(q[0] + 7, q[1]) for q in pl], skin_sh, .45), w=3.6, seed=sd + 30 + k))
        # тыл кисти
        palm = [(-52, 100), (-62, 40), (-58, -30), (-46, -62), (-10, -74), (24, -72), (52, -56), (60, -20), (56, 40), (48, 100)]
        pin = blob([(24, -72), (52, -56), (60, -20), (56, 40), (48, 100), (20, 100), (28, 0)], skin_sh, .85)
        for k, xx in enumerate((-30, -8, 16, 38)):
            pin += line([(xx, -10), (xx + 2, -54)], 2.4, skin_sh, seed=sd + 10 + k, op=.7)
        s.append(shape(palm, skin, pin, w=4.4, seed=sd + 4))
    else:
        base = (-30, 92)
        ang = -78 + 26 * (1 - press)
        L = 168 - 10 * (1 - press)
        pts = thumb_pts(base, ang, L, 40)
        pl = sausage(pts, 44, 36)
        tip = pts[-1]
        dx, dy = tip[0] - pts[-2][0], tip[1] - pts[-2][1]
        na = math.degrees(math.atan2(dy, dx))
        inner = blob([(p[0] + 9, p[1] + 2) for p in pl[: len(pl) // 2]] + [(base[0] + 12, base[1])], skin_sh, .55)
        inner += f'<g transform="translate({f(tip[0] - dx * .55)} {f(tip[1] - dy * .55)}) rotate({f(na)})">' \
                 f'{shape(ellipse_pts(0, 0, 15, 11, 12), NAIL if skin == SKIN else "#e3c0a8", "", w=2.2, seed=sd + 21)}</g>'
        inner += line([(pts[2][0] - 14, pts[2][1] + 4), (pts[2][0] + 12, pts[2][1] - 2)], 2.4, skin_sh, seed=sd + 22, op=.8)
        if press > 0.5:
            s.append(blob([(p[0] + 8, p[1] + 10) for p in pl], "#3a3020", .16 * press, blur(5)))
        # контур открыт у основания: палец вырастает из кисти без шва (линии сходят на нет внутри ладони)
        c = lib.clip_of(pl)
        s.append(blob(pl, skin) + f'<g clip-path="url(#{c})">{inner}</g>')
        s.append(line(pl, 4.6, INK, taper=.9, wmin=.0, seed=sd + 23, peak=0.5))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)})">{"".join(s)}</g>'


def s10(t):
    # лист: от исследователя (сверху справа) к центру, потом в руках участника — ближе
    u_in = ease_out(clamp((t - 16.2) / 0.55), 2.4)
    hold = smooth(TAKE, TAKE + 0.5, t)
    swing = 2.2 * math.sin(t * 3.1) * (1 - hold) + 0.8 * math.sin(t * 2.2)
    sc = 0.70 * (1 + 0.1 * hold)
    cx = 600 - 60 * u_in - 20 * hold
    cy = 640 + 120 * u_in + 40 * hold + 6 * math.sin(t * 2.6)
    rot = 8 * (1 - u_in) + swing - 2 * hold
    x0, y0 = -SW / 2, -SH_ / 2

    def P(lx, ly):
        a = math.radians(rot)
        X, Y = (lx + x0) * sc, (ly + y0) * sc
        return cx + X * math.cos(a) - Y * math.sin(a), cy + X * math.sin(a) + Y * math.cos(a)

    sheet = f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({f(sc)}) translate({x0} {y0})">{_ST["form"]}</g>'
    shadow = f'<g transform="translate({f(cx + 26)} {f(cy + 34)}) rotate({f(rot)}) scale({f(sc)}) translate({x0} {y0})" opacity=".22" filter="url(#fSh10)">' \
             f'<rect width="{SW}" height="{SH_}" fill="#203030"/></g>'
    # рука исследователя: держит верхний правый угол (рука сверху, повёрнута на 180°), уходит после TAKE
    rel = smooth(TAKE + 0.05, TAKE + 0.4, t)
    gx, gy = P(SW - 150, 0)
    gx += 80 * rel
    gy -= 520 * ease_in(rel, 1.6)
    press_r = 1 - smooth(TAKE + 0.02, TAKE + 0.16, t)
    rr = rot + 180 + 6 * rel
    back = grip_hand(gx, gy, rr, press_r, SKIN_R, SKIN_R_SH, "#f4f4f2", "#d5d8dc", "", 300, "back")
    front_r = grip_hand(gx, gy, rr, press_r, SKIN_R, SKIN_R_SH, "#f4f4f2", "#d5d8dc", "", 300, "front")
    # руки участника: из-за низа кадра к нижним углам
    up = ease_out(clamp((t - GIVE) / (TAKE - GIVE)), 2.2)
    press = smooth(TAKE - 0.12, TAKE + 0.04, t)
    hands_b, hands_f = "", ""
    for side, lx, sd in ((-1, 150, 400), (1, SW - 150, 500)):
        hx, hy = P(lx, SH_)
        hy += 1100 * (1 - up)
        hx += side * 90 * (1 - up)
        r = rot + side * (14 + 6 * (1 - up))
        fl = f'<g transform="translate({f(hx)} {f(hy)}) scale({side * -1} 1) translate({f(-hx)} {f(-hy)})">' if side > 0 else "<g>"
        hands_b += fl + grip_hand(hx, hy, -r if side > 0 else r, press, SKIN, SKIN_SH, JACKET, JACKET_SH, JACKET_ST, sd, "back") + "</g>"
        hands_f += fl + grip_hand(hx, hy, -r if side > 0 else r, press, SKIN, SKIN_SH, JACKET, JACKET_SH, JACKET_ST, sd, "front") + "</g>"
    art = _ST["room10"] + shadow + back + hands_b + sheet + front_r + hands_f
    u = clamp((t - 16.2) / 1.84)
    cm = cam(560, 860, 1.0 + 0.1 * (0.4 * u + 0.6 * ease_io(u)), -0.6 + 1.0 * u)
    return art, cm


# ───────────────────────── s11: рукопись по ходу пера
G = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "form_glyphs.json")))
FS = 108
SC = FS / G["upm"]
PX0, PY0 = 150, 320           # лист в мире s11
TX0 = PX0 + 84
BASES = [PY0 + ROWS[0] - 16, PY0 + ROWS[1] - 16]
SLOTS = [(18.0, 18.9), (19.4, 20.1)]
INKC = "#26356f"
ANG, HSC = -36, 1.0


def build_lines():
    out = []
    for li, gl in enumerate(G["lines"]):
        x = TX0
        base = BASES[li]
        path, gls = [], []
        for gi, g in enumerate(gl):
            gls.append(dict(g=g, x=x))
            for st in g.get("strokes", []):
                pts = [(x + px * SC, base - py * SC) for px, py in st]
                for k, p in enumerate(pts):
                    path.append((p[0], p[1], gi, k > 0))
            x += g["adv"] * SC
        P = np.array([(p[0], p[1]) for p in path])
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        down = np.array([p[3] for p in path[1:]])
        cost = np.where(down, seg, seg * 0.4)
        cum = np.concatenate([[0], np.cumsum(cost)])
        out.append(dict(path=path, P=P, cum=cum / cum[-1], gls=gls, base=base, x1=x))
    return out


L = build_lines()


def progress(li, t):
    a, b = SLOTS[li]
    u = clamp((t - a) / (b - a))
    return u * 0.85 + 0.15 * (u * u * (3 - 2 * u))


def tip_at(li, p):
    ln = L[li]
    i = int(np.searchsorted(ln["cum"], p, side="right")) - 1
    i = max(0, min(i, len(ln["P"]) - 2))
    c0, c1 = ln["cum"][i], ln["cum"][i + 1]
    q = 0 if c1 <= c0 else (p - c0) / (c1 - c0)
    x, y = ln["P"][i] + (ln["P"][i + 1] - ln["P"][i]) * q
    lift = 0.0 if ln["path"][i + 1][3] else math.sin(math.pi * q)
    return x, y, i, lift


def text_line(li, t):
    ln = L[li]
    a, b = SLOTS[li]
    if t <= a:
        return ""
    p = progress(li, t)
    s = []
    if p >= 1:
        cur = len(ln["gls"])
        i_now = len(ln["P"]) - 1
    else:
        _, _, i_now, _ = tip_at(li, p)
        cur = ln["path"][i_now][2]
    for gi, o in enumerate(ln["gls"]):
        g = o["g"]
        if not g["bounds"] or gi > cur:
            continue
        body = f'<path d="{g["d"]}" transform="translate({f(o["x"])} {ln["base"]}) scale({SC:.5f} {-SC:.5f})" fill="{INKC}"/>'
        if gi == cur and p < 1:
            pts = [(x, y, d) for (x, y, gg, d) in ln["path"][:i_now + 1] if gg == gi]
            tx, ty, _, _ = tip_at(li, p)
            pts.append((tx, ty, True))
            d = ""
            for k, (x, y, dn) in enumerate(pts):
                d += ("L" if (dn and k > 0) else "M") + f"{f(x)} {f(y)}"
            wpx = g["width"] * SC * 1.25
            mid = lib.uid("m")
            DEFS.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-600" y="-600" width="2400" height="3200">'
                        f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{f(wpx)}" stroke-linecap="round" stroke-linejoin="round"/></mask>')
            body = f'<g mask="url(#{mid})">{body}</g>'
        s.append(body)
    return "".join(s)


def pen_tip(t):
    a0 = SLOTS[0][0]
    if t < a0:
        u = ease_out(clamp((t - 17.64) / (a0 - 17.64)), 2.2)
        sx, sy = 980, 1500
        ex, ey = tip_at(0, 0)[:2]
        return sx + (ex - sx) * u, sy + (ey - sy) * u - 40 * math.sin(math.pi * u), 1.0 + 0.06 * (1 - u)
    for li, (a, b) in enumerate(SLOTS):
        if a <= t <= b:
            x, y, _, lift = tip_at(li, progress(li, t))
            return x, y, 1.0 + 0.03 * lift
        if li + 1 < len(SLOTS) and b < t < SLOTS[li + 1][0]:
            u = ease_io((t - b) / (SLOTS[li + 1][0] - b))
            sx, sy = tip_at(li, 1.0)[:2]
            ex, ey = tip_at(li + 1, 0.0)[:2]
            return sx + (ex - sx) * u, sy + (ey - sy) * u - 60 * math.sin(math.pi * u), 1.0 + 0.07 * math.sin(math.pi * u)
    e = t - SLOTS[-1][1]
    u = ease_out(clamp(e / 0.6), 2)
    sx, sy = tip_at(1, 1.0)[:2]
    return sx + 160 * u, sy + 300 * u, 1.0 + 0.06 * u


def table11():
    s = []
    DEFS.append('<pattern id="pWood11" width="420" height="140" patternUnits="userSpaceOnUse">'
                '<rect width="420" height="140" fill="#b88a5c"/>'
                '<path d="M0 30 C120 22 260 40 420 28 M0 78 C140 86 280 66 420 82 M0 118 C110 110 300 126 420 114" fill="none" stroke="#a2764a" stroke-width="3"/>'
                '<rect y="138" width="420" height="2" fill="#8a6038"/></pattern>')
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#pWood11)"/>')
    g = rad_grad([(0, "#fff0c8", .5), (.6, "#ffe0a0", .15), (1, "#ffe0a0", 0)], 380, 600, 1000, 1000)
    s.append(f'<rect x="-600" y="-600" width="{W + 1200}" height="{H + 1200}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    s.append(blob([(PX0 + 22, PY0 + 28), (PX0 + SW + 22, PY0 + 28), (PX0 + SW + 22, PY0 + SH_ + 28), (PX0 + 22, PY0 + SH_ + 28)], "#3a2410", .4, blur(14)))
    s.append(f'<g transform="translate({PX0} {PY0})">{form(700)}</g>')
    # обжитость: стакан воды и секундомер-кнопка без цифр у края
    s.append(blob(ellipse_pts(1000, 210, 100, 100, 18), "#3a2410", .35, blur(9)))
    s.append(shape(ellipse_pts(985, 192, 92, 92, 20), "#d8ecf4", blob(ellipse_pts(985, 192, 72, 72, 18), "#b7dbe9", .9) +
                   blob(ellipse_pts(958, 166, 22, 10, 10, rot=-30), "#ffffff", .9), w=4.4, seed=720))
    return "".join(s)


def s11(t):
    x, y, lift = pen_tip(t)
    ang = ANG + 3 * math.sin(t * 2.3) - 4 * (lift - 1)
    shadow = (f'<g transform="translate({f(x + 26 * lift)} {f(y + 34 * lift)}) scale({f(HSC)})" opacity=".26" filter="url(#fShH11)">'
              f'{hand.hand(ang, 7)}</g>')
    hnd = f'<g transform="translate({f(x)} {f(y)}) scale({f(HSC * lift)})">{hand.hand(ang, 7, 0.0)}</g>'
    txt = text_line(0, t) + text_line(1, t)
    art = _ST["table11"] + txt + shadow + hnd
    lin = clamp((t - 17.64) / 2.84)
    u = 0.4 * lin + 0.6 * ease_io(lin)
    # камера следует за строкой: сначала первая, потом вторая
    k2 = smooth(19.0, 19.6, t)
    cm = cam(600 + 30 * u, PY0 + ROWS[0] - 40 + (ROWS[1] - ROWS[0]) * 0.6 * k2 + 120, 1.22 + 0.08 * u, -1.6 + 1.0 * u)
    return art, cm


def build_static():
    if _ST:
        return
    DEFS.append('<filter id="fSh10" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>')
    DEFS.append('<filter id="fShH11" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .1  0 0 0 0 .05  0 0 0 1 0"/><feGaussianBlur stdDeviation="9"/></filter>')
    _ST["form"] = form(600)
    _ST["room10"] = room10()
    _ST["table11"] = table11()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s10": s10, "s11": s11}[sid](t)
    bgc = "#a9c3c2" if sid == "s10" else "#b88a5c"
    return svg(f'<rect width="{W}" height="{H}" fill="{bgc}"/><g transform="{cm}">{art}</g>')
