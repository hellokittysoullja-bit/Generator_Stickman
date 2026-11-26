"""Будильник рилса 37 — один и тот же предмет во всех сценах (clock/, bed/, flat/): круглый механический, красный
корпус, две серебристые чашечки-звонка с молоточком между ними, кнопка сверху, кремовый циферблат с рисками, чёрные
стрелки, две ножки. Модуль самодостаточный: свои clipPath — внутри группы (без общего DEFS), тушь — ink.py этой папки,
загруженный по пути под своим именем (не путается с lib/ink соседних сцен).

Импорт из соседней сцены:
    import importlib.util, os
    sp = importlib.util.spec_from_file_location("alarm37", os.path.join(STORY, "clock", "alarm.py"))
    alarm37 = importlib.util.module_from_spec(sp); sp.loader.exec_module(alarm37)
    svg += alarm37.alarm(cx, cy, size=120, hh=7, mm=0, ring=1.0, t=t, uid="a1")

alarm(cx, cy, size, hh, mm, ring, t, press, squash, rot, uid)
  cx, cy — центр циферблата в координатах сцены; size — радиус корпуса в px (низ ножек: cy + 1.27·size,
  верх звонков: cy − 1.40·size, ширина по звонкам ≈ 2.4·size);
  hh, mm — время стрелок (mm может быть дробным и > 60: стрелки крутятся непрерывно);
  ring 0..1 — сила звона: молоточек бьёт по чашкам ~18 раз в секунду, корпус дрожит (нужно t — время ролика);
  press 0..1 — кнопка сверху вдавлена; squash ≤ 1 — сплющен по вертикали (от низа ножек), шире по бокам;
  rot — наклон в градусах вокруг низа ножек; uid — префикс id (разный у двух будильников в одном кадре).
shadow(cx, floor_y, size, op) — мягкая тень под ножками. ring_marks(cx, cy, size, t, amp) — штрихи звона у чашек.
"""
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("_alarm37_ink", os.path.join(_HERE, "ink.py"))
_ink = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_ink)

INK = "#1c1622"
RED, RED_SH, RED_SH2, RED_HI = "#e0402f", "#b02a22", "#8e1f1a", "#ff8b73"
STEEL, STEEL_SH, STEEL_HI = "#d9dde4", "#a3a9b5", "#ffffff"
FACE, FACE_SH = "#fbf0d6", "#ead7ad"
FOOT_Y = 238.0     # низ ножек в единицах (радиус корпуса 200)
TOP_Y = -280.0     # верх звонков


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class _Ctx:
    def __init__(self, uid):
        self.uid, self.n = uid, 0

    def cid(self):
        self.n += 1
        return f"{self.uid}c{self.n}"

    def shape(self, pts, fill, inner="", w=5.0, seed=0, var=0.28, weight=0.45, ink=True):
        d = _ink.fill_d(pts)
        out = [f'<path d="{d}" fill="{fill}"/>']
        if inner:
            c = self.cid()
            out.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath><g clip-path="url(#{c})">{inner}</g>')
        if ink:
            out.append(f'<path d="{_ink.ink_closed(pts, w, var=var, weight=weight, seed=abs(int(seed)) % 2**31)}" fill="{INK}"/>')
        return "".join(out)


def blob(pts, color, op=1.0):
    o = f' opacity="{op:.3f}"' if op != 1 else ""
    return f'<path d="{_ink.fill_d(pts)}" fill="{color}"{o}/>'


def line(pts, w=4.0, color=INK, taper=0.6, wmin=0.12, seed=3, op=1.0):
    d = _ink.ink_open(pts, w, taper=taper, wmin=wmin, seed=abs(int(seed)) % 2**31)
    if not d:
        return ""
    o = f' opacity="{op:.3f}"' if op != 1 else ""
    return f'<path d="{d}" fill="{color}"{o}/>'


E = _ink.ellipse_pts


def _rot(pts, ang, ox=0.0, oy=0.0):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(ox + p[0] * c - p[1] * s, oy + p[0] * s + p[1] * c) + ((1,) if len(p) > 2 and p[2] else ()) for p in pts]


# ───────────────────────── части (единицы: радиус корпуса 200, центр циферблата в 0, 0)
BELL_ANG, BELL_R = 32.0, 216.0     # чашки: угол от верха и расстояние центра обода от центра


def _bell(cx_, side, sd):
    """Чашка-звонок: купол наружу, обод к корпусу; стойка от корпуса к центру купола."""
    a = side * BELL_ANG
    ox, oy = BELL_R * math.sin(math.radians(a)), -BELL_R * math.cos(math.radians(a))
    s = []
    # стойка
    st = _rot([(-7, 20, 1), (7, 20, 1), (7, -40, 1), (-7, -40, 1)], a, ox, oy)
    s.append(cx_.shape(st, STEEL_SH, "", w=3.2, seed=sd))
    # купол: обод y=0 (x ∈ ±80), макушка y=−74
    dome = [(-82, 4, 1)] + [(-82 * math.cos(math.radians(u)), -76 * math.sin(math.radians(u))) for u in range(12, 170, 18)] + [(82, 4, 1)]
    inner = blob(_rot([(10, 6), (82, 6), (78, -24), (50, -60), (20, -74), (40, -30)], a, ox, oy), STEEL_SH, .9)
    inner += blob(_rot(E(-34, -44, 13, 26, 10, rot=-35), a, ox, oy), STEEL_HI, .85)
    inner += blob(_rot([(-90, 4), (90, 4), (90, -6), (-90, -6)], a, ox, oy), "#8b92a0", .7)
    s.append(cx_.shape(_rot(dome, a, ox, oy - 0), STEEL, inner, w=4.6, seed=sd + 1))
    # шишечка на макушке
    s.append(cx_.shape(_rot(E(0, -80, 11, 8, 10), a, ox, oy), STEEL_SH, "", w=3, seed=sd + 2))
    return "".join(s), (ox, oy)


def _hammer(cx_, ang, sd):
    """Молоточек: ось над кнопкой, стержень вверх, головка-шарик; ang — отклонение в градусах."""
    px, py = 0.0, -196.0
    L = 80.0
    a = math.radians(ang)
    hx, hy = px + L * math.sin(a), py - L * math.cos(a)
    nx, ny = math.cos(a), math.sin(a)
    rod = [(px - nx * 5, py - ny * 5, 1), (hx - nx * 5, hy - ny * 5, 1), (hx + nx * 5, hy + ny * 5, 1), (px + nx * 5, py + ny * 5, 1)]
    s = [cx_.shape(rod, STEEL_SH, "", w=2.6, seed=sd)]
    s.append(cx_.shape(E(hx, hy, 17, 17, 12), STEEL, blob(E(hx + 5, hy + 6, 14, 13, 10), STEEL_SH, .9) +
                       blob(E(hx - 6, hy - 6, 5, 4, 8), STEEL_HI, .9), w=3.4, seed=sd + 2))
    return "".join(s)


def _button(cx_, press, sd):
    y = -200 + 12 * press
    s = cx_.shape([(-34, y + 22, 1), (-30, y - 8, 1), (30, y - 8, 1), (34, y + 22, 1)], RED_SH, "", w=3.4, seed=sd)
    s += cx_.shape(E(0, y - 8, 32, 9, 14), RED, blob(E(-10, y - 11, 12, 3, 8), RED_HI, .9), w=3.2, seed=sd + 1)
    return s


def _foot(cx_, side, sd):
    a = side * 142.0
    ox, oy = 196 * math.sin(math.radians(a)), -196 * math.cos(math.radians(a))
    pts = [(ox - side * 18, oy - 10, 1), (ox + side * 22, oy - 4, 1), (ox + side * 40, FOOT_Y - 6), (ox + side * 34, FOOT_Y, 1),
           (ox + side * 6, FOOT_Y, 1), (ox - side * 12, FOOT_Y - 8)]
    return cx_.shape(pts, RED_SH, blob([(ox + side * 10, oy), (ox + side * 40, FOOT_Y), (ox + side * 20, FOOT_Y)], RED_SH2, .9),
                     w=4.2, seed=sd)


def _body(cx_, sd):
    s = []
    inner = blob(E(26, 30, 196, 196, 36), RED_SH, .95)
    inner += blob(E(46, 50, 186, 186, 36), RED_SH2, .5)
    inner += blob(E(-96, -118, 62, 22, 16, rot=-40), RED_HI, .85)
    inner += blob(E(-148, -40, 12, 40, 12, rot=-12), RED_HI, .6)
    s.append(cx_.shape(E(0, 0, 200, 200, 40), RED, inner, w=6.4, seed=sd))
    # металлический ободок стекла
    s.append(cx_.shape(E(0, 0, 168, 168, 40), STEEL, blob(E(10, 12, 166, 166, 36), STEEL_SH, .9), w=4.0, seed=sd + 1))
    return "".join(s)


def _face(cx_, sd):
    s = []
    inner = blob(E(14, 18, 156, 156, 36), FACE_SH, .55)
    s.append(cx_.shape(E(0, 0, 156, 156, 40), FACE, inner, w=3.6, seed=sd))
    for k in range(60):
        a = math.radians(k * 6)
        big = k % 15 == 0
        mid = k % 5 == 0
        if not (big or mid):
            r0, r1 = 136, 144
            s.append(line([(math.sin(a) * r0, -math.cos(a) * r0), (math.sin(a) * r1, -math.cos(a) * r1)], 3.2, "#6a5f55",
                          taper=.1, wmin=.8, seed=sd + 10 + k))
            continue
        r0, r1 = (108, 146) if big else (122, 146)
        s.append(line([(math.sin(a) * r0, -math.cos(a) * r0), (math.sin(a) * r1, -math.cos(a) * r1)], 12 if big else 7.5, INK,
                      taper=.12, wmin=.75, seed=sd + 10 + k))
    return "".join(s)


def _hand(cx_, ang, L, w, sd, tail=24):
    a = math.radians(ang)
    dx, dy = math.sin(a), -math.cos(a)
    nx, ny = -dy, dx
    pts = [(-dx * tail + nx * w * .45, -dy * tail + ny * w * .45, 1), (dx * L * .7 + nx * w * .62, dy * L * .7 + ny * w * .62),
           (dx * L, dy * L, 1), (dx * L * .7 - nx * w * .62, dy * L * .7 - ny * w * .62), (-dx * tail - nx * w * .45, -dy * tail - ny * w * .45, 1)]
    return cx_.shape(pts, INK, "", w=2.0, seed=sd)


def _glass(cx_):
    g = blob([(-128, -60), (-110, -104), (-70, -134), (-30, -146), (-60, -118), (-96, -82), (-116, -40)], "#ffffff", .55)
    g += blob(E(92, 96, 14, 7, 8, rot=-40), "#ffffff", .5)
    return g


def alarm(cx, cy, size=200.0, hh=7.0, mm=0.0, ring=0.0, t=0.0, press=0.0, squash=1.0, rot=0.0, uid="al"):
    cx_ = _Ctx(uid)
    k = size / 200.0
    # звон: молоточек (треугольная волна ~18 Гц), дрожь корпуса
    ham = 0.0
    jit_r, jit_y = 0.0, 0.0
    if ring > 0:
        ph = (t * 18.0) % 1.0
        tri = 4 * abs(ph - 0.5) - 1          # −1..1
        ham = 46.0 * ring * max(-1.0, min(1.0, tri * 1.5))
        jit_r = ring * 3.2 * math.sin(t * 2 * math.pi * 23)
        jit_y = -ring * 7.0 * abs(math.sin(t * 2 * math.pi * 11.5))
    sq = max(0.3, squash)
    sx = 1.0 + (1.0 - sq) * 0.85
    s = []
    bl, _ = _bell(cx_, -1, 11)
    br, _ = _bell(cx_, 1, 21)
    s.append(_hammer(cx_, ham, 31))
    s.append(bl + br)
    s.append(_foot(cx_, -1, 41) + _foot(cx_, 1, 45))
    s.append(_body(cx_, 51))
    s.append(_button(cx_, press, 61))
    s.append(_face(cx_, 71))
    ha = ((hh % 12) + mm / 60.0) * 30.0
    ma = (mm % 60.0) * 6.0
    s.append(_hand(cx_, ha, 92, 20, 81))
    s.append(_hand(cx_, ma, 132, 14, 82))
    s.append(cx_.shape(E(0, 0, 14, 14, 12), INK, blob(E(-3, -4, 4, 4, 8), "#5a5560", .9), w=2, seed=83))
    s.append(cx_.shape(E(0, 0, 6, 6, 8), RED, "", w=1.5, seed=84))
    s.append(_glass(cx_))
    tf = (f"translate({f(cx)} {f(cy + FOOT_Y * k)}) rotate({f(rot + jit_r)}) translate(0 {f(jit_y * k)}) "
          f"scale({k * sx:.5f} {k * sq:.5f}) translate(0 {-FOOT_Y})")
    return f'<g transform="{tf}">{"".join(s)}</g>'


def shadow(cx, floor_y, size=200.0, op=0.35, color="#2a1c18"):
    k = size / 200.0
    return f'<ellipse cx="{f(cx)}" cy="{f(floor_y)}" rx="{f(250 * k)}" ry="{f(26 * k)}" fill="{color}" opacity="{op:.3f}"/>'


def ring_marks(cx, cy, size=200.0, t=0.0, amp=1.0, color=INK, seed=0):
    """Штрихи звона: по три дуги-штриха снаружи каждой чашки, пульсируют с частотой звона."""
    if amp <= 0.02:
        return ""
    k = size / 200.0
    s = []
    for side in (-1, 1):
        a = math.radians(side * BELL_ANG)
        bx, by = BELL_R * math.sin(a), -BELL_R * math.cos(a)
        for j in range(3):
            ph = (t * 9 + j * 0.33) % 1.0
            r0 = 110 + 26 * j + 30 * ph
            spread = 0.42 + 0.08 * j
            ang0 = math.atan2(by, bx)          # наружу от центра
            pts = []
            for u in range(7):
                aa = ang0 + (u / 6 - 0.5) * spread * 2
                pts.append((cx + (bx + math.cos(aa) * (r0 - 60)) * k * 1.0, cy + (by + math.sin(aa) * (r0 - 60)) * k))
            # перо: штрих короткий, по дуге
            s.append(line(pts, 11 * k * amp * (1 - 0.5 * ph), color, taper=.6, wmin=.15, seed=seed + 17 * j + (3 if side > 0 else 0)))
    return "".join(s)
