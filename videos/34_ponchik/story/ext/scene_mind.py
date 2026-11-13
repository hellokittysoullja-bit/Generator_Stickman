"""Сцена mind рилса 34 (s07, s08): внутренний мир Димы на тёмно-синем фоне (как фон мозга рилсов 24–32).
s07 «Когда ругаешь себя, становится так плохо» (11.2–13.3): маленький грустный Дима сидит на полу, обхватив колени;
     над ним вырастает огромный строгий «внутренний Дима» (тот же Дима — горчичное худи, щетина, мешки — только хмурый,
     руки в боки), на «ругаешь» (11.72) наклоняется и грозит пальцем, ругается; маленький вжимается; на «становится»
     (12.4) над маленьким собирается тучка, на «так» (13.04) льёт дождь, на «плохо» (13.36) — сильнее и темнее.
s08 «что хочется заесть это ещё сильнее» (13.3–16.2): круг-ловушка из 4 значков без букв со стрелками: пончик →
     грозящий палец → тучка с дождём → надкушенный пончик → снова пончик; значки выскакивают по одному, на «заесть»
     (14.52) круг замыкается и начинает крутиться, на «сильнее» (15.52) крутится быстрее и вырастает, тучка темнеет.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import parts34 as P
import people
from lib import (INK, W, H, back_out, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rad_grad, shape,
                 smooth, svg)

_ST = {}
RUGAESH = P.wt("ругаешь")          # 11.72
STANOV = P.wt("становится")        # 12.40
TAK = P.wt("так", 12)              # 13.04
PLOHO = P.wt("плохо")              # 13.36
CHTO = P.wt("что", 13.5)           # 13.84
ZAEST = P.wt("заесть")             # 14.52
SILNEE = P.wt("сильнее")           # 15.52
FLIP = -1
NSIDE = -1
EFF = 0.8                          # экранная толщина туши героя


def background():
    s = []
    lib.lin_grad([(0, "#1b2244", 1), (.55, "#26315e", 1), (1, "#2f3d72", 1)], 0, 0, 0, 1, gid="gMind")
    s.append(f'<rect x="-700" y="-700" width="{W + 1400}" height="{H + 1400}" fill="url(#gMind)"/>')
    rad_grad([(0, "#4a5d9e", .85), (.6, "#36467e", .35), (1, "#36467e", 0)], 540, 820, 700, 760, gid="gMindSpot")
    s.append(f'<rect x="-700" y="-700" width="{W + 1400}" height="{H + 1400}" fill="url(#gMindSpot)"/>')
    return "".join(s)


def dust(t, n=30, sd=4):
    rs = np.random.RandomState(sd)
    s = []
    for k in range(n):
        x0, y0 = rs.uniform(-120, W + 120), rs.uniform(-100, H)
        sp, ph, r = rs.uniform(14, 34), rs.uniform(0, 6.28), rs.uniform(2.2, 4.6)
        x = x0 + 30 * math.sin(t * 0.7 + ph)
        y = (y0 - sp * (t - 10)) % (H + 200) - 100
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#c9d6ff" opacity="{.16 + .12 * math.sin(t * 2 + ph):.3f}"/>')
    return "".join(s)


def layers(d):
    return d.get("legs", "") + d["arm_f"] + d.get("pelvis", "") + d["body"] + d["arm_n"]


# ═══════════════════════════════ s07
GX, GY, GS = 330, 1150, 1.22         # бёдра великана, масштаб
SX, SY, SS = 830, 1240, 0.56          # маленький Дима: таз на полу (в отражённой системе смотрит влево)


def talk(t, t0, t1, rate=6.5):
    if t < t0 or t > t1:
        return 0.0
    v = .5 + .5 * math.sin(2 * math.pi * rate * (t - t0)) * (.7 + .3 * math.sin(t * 3.1))
    return clamp(v * smooth(t0, t0 + .08, t) * (1 - smooth(t1 - .1, t1, t)))


def giant(t):
    """Великан-«внутренний Дима»: вырастает снизу (11.0–11.45), на «ругаешь» наклоняется вперёд и грозит пальцем."""
    rise = ease_out(clamp((t - 11.0) / 0.42), 3)
    over = 1 + 0.03 * P.kick(t, 11.35, 6, 12)
    lean_k = smooth(RUGAESH - 0.12, RUGAESH + 0.12, t)
    breath = math.sin(t * 2.4)
    s = GS * over
    hx = GX + 20 * lean_k
    hy = GY + 260 * (1 - rise) + 4 * breath
    lean = 0.04 + 0.12 * lean_k + 0.05 * P.kick(t, RUGAESH, 5, 12)
    lib.INK_K[0] = EFF / s
    wag = smooth(RUGAESH - 0.05, RUGAESH + 0.05, t) * math.sin(2 * math.pi * 3.2 * (t - RUGAESH))
    up = ease_out(clamp((t - (RUGAESH - 0.22)) / 0.2), 3)                # рука с бедра — вверх к «ругаешь»
    hip_n = (hx + 60 * s, hy - 30 * s)
    nt0 = (hx + 400 * s + 8 * wag, hy - 470 * s + 40 * lean_k)         # кисть с пальцем — перед грудью, ниже лица
    nt = (hip_n[0] + (nt0[0] - hip_n[0]) * up, hip_n[1] + (nt0[1] - hip_n[1]) * up - 60 * s * math.sin(math.pi * up))
    ft = (hx - 110 * s, hy - 70 * s)                                    # кулак на бедре (за телом)
    o = talk(t, RUGAESH - 0.06, 13.3, 6.0)
    hang = -0.06 + 0.1 * lean_k + 0.03 * math.sin(t * 5) * lean_k
    look = (0.55, 0.55 + 0.1 * lean_k)
    blink = P.bump(t, 12.6, 0.16)
    d = people.draw(dict(hip=(hx, hy), scale=s, lean=lean,
                         feet={"n": ((hx + 70 * s, hy + 620 * s), 0.0), "f": ((hx - 50 * s, hy + 615 * s), 0.0)},
                         arms={"f": ("ik", ft, 1), "n": ("ik", nt, NSIDE)},
                         hands={"n": dict(kind="none"), "f": dict(kind="none")},
                         expr=dict(brows="det", mouth="talk", open=0.25 + 0.6 * o, smile=-1.2, lid=0.4, look=look, closed=blink),
                         head_ang=hang), "dima")
    W_ = d["wrist"]["n"]
    ang = math.radians(-82 + 16 * wag) * up + math.radians(150) * (1 - up)      # на бедре — кулак пальцами назад-вниз
    hand = P.point_hand(W_, (math.cos(ang), math.sin(ang)), k=s * 0.98, sd=7100, flip=FLIP, index=up > 0.35)
    brows = angry_brows(d, s, lean * .5 + hang)
    # «злые» штрихи у головы на ругани
    fx = ""
    e = t - RUGAESH
    hp = d["head"]
    for j, tt in enumerate((RUGAESH, 12.12, 12.72)):
        fx += P.pop_lines(hp[0] + 40, hp[1] - 170, t - tt, 170, 290, 3, a0=-math.pi / 2 + 0.25, spread=1.6, col="#ff6a4a", w=16, sd=7200 + j * 7)
    lib.INK_K[0] = 1.0
    return layers(d) + brows + hand + fx


def angry_brows(d, s, a, sd=7400):
    """Сердитые брови поверх чёлки (у people.py брови прячутся под волосами): толстые, к переносице вниз.
    a — полный поворот головы (рад), координаты — система головы Димы (people.dima_head)."""
    hp = d["head"]
    c, sn = math.cos(a), math.sin(a)

    def tf(p):
        return (hp[0] + (p[0] * c - p[1] * sn) * s, hp[1] + (p[0] * sn + p[1] * c) * s)

    o = ""
    for (cx, cy, rx, ry), lid, sd2 in (((16, -12, 50, 51), [(-40, -56), (20, -42), (70, -20)], 0), ((92, -10, 39, 47), [(48, -22), (96, -38), (136, -52)], 5)):
        ep = [tf(p) for p in ellipse_pts(cx, cy, rx + 1, ry + 1, 16)]
        cid = lib.clip_of(ep)
        wedge = [tf(p) for p in [(lid[0][0], -130), (lid[-1][0], -130)] + lid[::-1]]
        o += f'<g clip-path="url(#{cid})"><path d="{lib.fill_d(wedge)}" fill="#ecc4a2"/>'
        o += line([tf(p) for p in lid], 7, INK, taper=.3, wmin=.5, seed=sd + 10 + sd2) + "</g>"
    o += line([tf(p) for p in [(-30, -92), (10, -84), (52, -58)]], 13, "#3d2418", taper=.35, wmin=.45, seed=sd, peak=.6)
    o += line([tf(p) for p in [(70, -58), (100, -76), (128, -86)]], 11, "#3d2418", taper=.35, wmin=.45, seed=sd + 1, peak=.4)
    return o


def small(t):
    """Маленький Дима сидит на полу, обхватив колени (отражён — смотрит влево, к великану); на «ругаешь» вжимается."""
    flinch = smooth(RUGAESH, RUGAESH + 0.15, t)
    shake = 0.02 * P.kick(t, RUGAESH, 6, 30)
    sob = 0.5 + 0.5 * math.sin(t * 7) if t > PLOHO - 0.1 else 0.0
    s = SS
    lib.INK_K[0] = EFF / s
    lean = 0.22 + 0.12 * flinch + shake + 0.015 * math.sin(t * 2.2)
    d = people.draw(dict(hip=(0, 0), scale=s, lean=lean,
                         feet={"n": ((330 * s, 38 * s), 0.18), "f": ((300 * s, 30 * s), 0.18)},
                         arms={"f": ("ik", (262 * s, -250 * s + 12 * s * flinch), -1), "n": ("ik", (285 * s, -238 * s + 12 * s * flinch), -1)},
                         hands={"n": dict(kind="open", curl=(.6, .65, .7, .7), spread=.05, thumb=.8, dir=(0.55, 0.85)), "f": dict(kind="none")},
                         expr=dict(brows="worry", mouth="tired", lid=0.25 - 0.1 * flinch, look=(-0.1 - 0.4 * (1 - flinch), 0.5 + 0.3 * flinch),
                                   closed=P.bump(t, 11.5, 0.16)),
                         head_ang=0.12 + 0.18 * flinch + 0.02 * sob), "dima")
    lib.INK_K[0] = 1.0
    shadow = blob(ellipse_pts(SX - 70, SY + 26, 190, 24, 16), "#121a36", .55)
    lay = d["arm_f"] + d.get("legs", "") + d.get("pelvis", "") + d["body"] + d["arm_n"]       # дальняя рука — за коленями
    return shadow + f'<g transform="translate({f(SX)} {f(SY)}) scale(-1 1)">{lay}</g>'


def s07(t):
    art = [_ST["bg"], dust(t)]
    # холодное пятно света под маленьким
    art.append(_ST["pool"])
    art.append(giant(t))
    art.append(small(t))           # маленький — ближе к нам, рука великана проходит за ним
    # тучка над маленьким
    form = ease_out(clamp((t - STANOV) / 0.35), 3)
    if form > 0:
        sc = 1.0 * back_out(form, 2.0) * (1 + 0.12 * smooth(PLOHO - 0.05, PLOHO + 0.15, t)) * (1 + 0.04 * P.kick(t, PLOHO, 6, 14))
        rain = smooth(TAK - 0.05, TAK + 0.15, t) * (0.6 + 0.4 * smooth(PLOHO - 0.05, PLOHO + 0.1, t))
        dark = 0.25 + 0.75 * smooth(TAK, PLOHO + 0.1, t)
        cx = SX - 90 + 8 * math.sin(t * 1.7)
        cy = 850 + 6 * math.sin(t * 2.3)
        art.append(P.storm(cx, cy, sc, dark, t, rain, sd=7300, rain_len=170))
    # камера: лёгкий наезд, толчок на «ругаешь»
    u = clamp((t - 11.0) / 2.5)
    sc = 1.0 + 0.06 * ease_io(u) + 0.03 * P.kick(t, RUGAESH, 6, 14) + 0.015 * P.kick(t, PLOHO, 6, 14)
    return "".join(art), cam(560 + 20 * u, 900 + 10 * u, sc, 0.6 - 0.9 * u)


# ═══════════════════════════════ s08: круг-ловушка
RC = (540, 760)
RR = 330
POP = [13.0, 13.42, CHTO, ZAEST - 0.06]        # пончик, палец, тучка, надкушенный пончик


def spin_angle(t):
    """Угол поворота круга (град): с «заесть» разгон до 80°/с, с «сильнее» — до 260°/с (интеграл скорости)."""
    def w(tt):
        return 80 * smooth(ZAEST, ZAEST + 0.4, tt) + 180 * smooth(SILNEE - 0.05, SILNEE + 0.35, tt)
    if t <= ZAEST:
        return 0.0
    n = max(2, int((t - ZAEST) * 120))
    ts = np.linspace(ZAEST, t, n)
    return float(np.trapezoid([w(x) for x in ts], ts))


def badge(x, y, sc, inner, sd, glow=0.0):
    s = ""
    if glow > 0.01:
        g = rad_grad([(0, "#ffe27a", .7 * glow), (1, "#ffe27a", 0)], x, y, 175 * sc, 175 * sc)
        s += f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(175 * sc)}" fill="url(#{g})"/>'
    s += blob(ellipse_pts(x + 8 * sc, y + 12 * sc, 126 * sc, 126 * sc, 24), "#10142a", .45)
    s += shape(ellipse_pts(x, y, 126 * sc, 126 * sc, 24), "#f6efe0", blob(ellipse_pts(x + 26 * sc, y + 30 * sc, 112 * sc, 105 * sc, 20), "#e6dcc6", .9),
               w=5, seed=sd)
    return s + f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{inner}</g>'


def arrow_arc(a0, a1, r, prog, sd, col="#ffd23a"):
    """Толстая дуговая стрелка по кругу от угла a0 к a1 (рад, по часовой), дорисовка prog 0..1."""
    if prog <= 0.01:
        return ""
    a1p = a0 + (a1 - a0) * prog
    pts = [(RC[0] + r * math.cos(a), RC[1] + r * math.sin(a)) for a in np.linspace(a0, a1p, 18)]
    o = line(pts, 30, INK, taper=.02, wmin=.9, seed=sd)
    o += line(pts, 19, col, taper=.02, wmin=.9, seed=sd + 1)
    # наконечник
    a = a1p
    tip = (RC[0] + r * math.cos(a + 0.06), RC[1] + r * math.sin(a + 0.06))
    tx, ty = -math.sin(a), math.cos(a)            # касательная по часовой
    nx, ny = math.cos(a), math.sin(a)
    bx, by = tip[0] - tx * 44, tip[1] - ty * 44
    head = [(tip[0] + tx * 4, tip[1] + ty * 4, 1), (bx + nx * 34, by + ny * 34, 1), (bx - nx * 34, by - ny * 34, 1)]
    o += shape(head, col, "", w=4.6, seed=sd + 2)
    return o


def icon_finger(t, sd):
    wag = math.sin(2 * math.pi * 3.0 * t)
    a = math.radians(-90 + 14 * wag)
    lib.INK_K[0] = 1.0
    return P.point_hand((-10 - 50 * math.cos(a), 70 - 50 * math.sin(a)), (math.cos(a), math.sin(a)), k=0.95, sd=sd, flip=-1)


def icon_storm(t, dark, sd):
    return P.storm(0, -30, 0.78, dark, t, 1.0, sd=sd, rain_len=120)


def s08(t):
    art = [_ST["bg"], dust(t, 34, 9)]
    spin = spin_angle(t)
    grow = 1 + 0.14 * smooth(SILNEE - 0.05, SILNEE + 0.4, t) + 0.05 * P.kick(t, SILNEE, 5, 12)
    dark = 0.2 + 0.8 * smooth(SILNEE - 0.1, SILNEE + 0.5, t)
    # вихрь-штрихи по кругу, когда крутится быстро
    fast = smooth(SILNEE, SILNEE + 0.4, t)
    base = [-90, 0, 90, 180]                       # верх, право, низ, лево
    angs = [math.radians(b + spin) for b in base]
    r = RR * grow
    arrows = []
    for i in range(4):
        j = (i + 1) % 4
        pa = POP[j] if j else ZAEST
        prog = ease_out(clamp((t - pa + 0.05) / 0.3), 2)
        if j == 0:
            prog = ease_out(clamp((t - ZAEST) / 0.3), 2)
        gap = math.radians(33) / grow ** .3
        arrows.append(arrow_arc(angs[i] + gap, angs[i] + math.pi / 2 - gap, r, prog, 8100 + i * 10))
    if fast > 0.01:
        for k in range(10):
            a0 = math.radians(spin * 1.0 + k * 36)
            rr = r + 150 + 20 * math.sin(k * 2.1)
            pts = [(RC[0] + rr * math.cos(a), RC[1] + rr * math.sin(a)) for a in np.linspace(a0, a0 + 0.45, 8)]
            arrows.append(line(pts, 7, "#9fb4ff", taper=.6, wmin=.1, seed=8200 + k, op=.7 * fast))
    art += arrows
    icons = []
    for i in range(4):
        e = t - POP[i]
        if e < -0.02:
            continue
        k = back_out(clamp(e / 0.3), 2.6)
        bob = 6 * math.sin(t * 3 + i * 1.7)
        x = RC[0] + r * math.cos(angs[i])
        y = RC[1] + r * math.sin(angs[i]) + bob
        sc = 0.98 * k * grow ** .5
        glow = math.exp(-max(0, e) * 4) if e > 0 else 0.0
        if i == 0:
            inner = f'<g transform="translate(0 4) scale(1.5)">{P.donut("pink", 8000)}</g>'
        elif i == 1:
            inner = icon_finger(t, 8010)
        elif i == 2:
            inner = icon_storm(t, dark, 8020)
        else:
            bite = smooth(ZAEST - 0.02, ZAEST + 0.06, t)
            bites = [(48, -18, 24)] + ([(18, -40, 20)] if bite > 0.5 else [])
            inner = f'<g transform="translate(0 4) scale(1.5)">{P.donut("pink", 8030, bites=bites)}</g>'
            if e > 0:   # крошки от укуса
                for c in range(6):
                    ce = t - ZAEST
                    if 0 < ce < 0.6:
                        a = -1.2 + c * 0.45
                        inner += blob(ellipse_pts(70 + 90 * ce * math.cos(a), -20 + 90 * ce * math.sin(a) + 160 * ce * ce, 5, 4, 6),
                                      P.CRUMB if c % 2 else "#f58fbb")
        icons.append(badge(x, y, sc, inner, 8040 + i, glow))
    art += icons
    # камера: лёгкий наезд с первого кадра, толчок на «сильнее»
    u = clamp((t - 13.1) / 3.3)
    sc = 1.0 + 0.05 * ease_io(u) + 0.035 * P.kick(t, SILNEE, 6, 14) + 0.02 * P.kick(t, ZAEST, 6, 14)
    return "".join(art), cam(540, 830 - 10 * u, sc, -0.5 + 0.8 * u)


def build_static():
    if _ST:
        return
    _ST["bg"] = background()
    g = rad_grad([(0, "#6f86d6", .5), (.7, "#4a5d9e", .18), (1, "#4a5d9e", 0)], SX - 70, SY + 10, 330, 110)
    _ST["pool"] = f'<ellipse cx="{SX - 70}" cy="{SY + 10}" rx="330" ry="110" fill="url(#{g})"/>'
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s07": s07, "s08": s08}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{art}</g>')
