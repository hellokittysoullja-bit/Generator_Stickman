"""Сцена wash рилса 38 (s08, s09): автомойка днём (Nunes, Drèze 2006). Без букв и логотипов.
s08 «На автомойке водителям давали» (13.95–15.6): синий хэтчбек въезжает под жёлтую арку, тормозит с клевком; на
     «автомойке» (14.24) синие и красные щётки начинают крутиться, сверху льётся вода, на машине растёт пена, брызги
     летят от щёток; на «водителям» (14.80) у водителя (мужчина в красной кепке) опускается стекло, он поворачивается
     к нам и улыбается.
s09 «карточки на бесплатную мойку» (15.6–17.45): слева окошко кассы, из него рука работника в синей перчатке
     протягивает карточку к окну машины; на «бесплатную» (16.32) над карточкой выскакивает значок: машинка с
     блёстками и подарочным бантом; на «мойку» (16.88) водитель берёт карточку и тянет её к себе.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import hand as HD
import lib
import parts34 as P
import person
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, rad_grad,
                 rect_pts, shape, smooth, svg)

_ST = {}
AVTO = P.wt("автомойке")            # 14.24
VODIT = P.wt("водителям")           # 14.80
KART = P.wt("карточки", 15)         # 15.68
BESPL = P.wt("бесплатную")          # 16.32
MOYKU = P.wt("мойку")               # 16.88

GROUND = 1180
CAR_X = 560
CAR = "#3f7fd0"
CAR_SH = "#2c5fa6"
CAR_HI = "#7fb2ee"
GLASS = "#bfe3f4"
DRIVER = dict(skin="#e9b994", hair="short", hair_c="#4a3426", top="#4f9a62", low="#33384a", face=0.5, cap="#d8402f",
              stubble=True, brow_c="#4a3426")
GLOVE = ("#5aa7ee", "#3b86d0", "#2f6fb2", "#5aa7ee")
D_SKIN = ("#e9b994", "#cf9a78", "#b98266", "#f3cdb4")


def sh(c, k=person.SH_K):
    return lib.mul(c, k)


# ═══════════════════════════════ фон s08
def bg_wash():
    s = []
    g = lib.lin_grad([(0, "#7cc4f2", 1), (1, "#cdeafb", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{1300}" fill="url(#{g})"/>')
    # солнце и облака
    s.append(shape(ellipse_pts(860, 170, 70, 70, 20), "#ffd84a", blob(ellipse_pts(880, 190, 52, 52, 16), "#f6c234", .7), w=4.4, seed=8001))
    for k, (cx, cy, sc) in enumerate(((180, 150, 1.0), (560, 90, .8), (1150, 260, .9), (-120, 300, .8))):
        s.append(shape(P.cloud_pts(cx, cy, 120 * sc, 46 * sc, 7, sd=8010 + k), "#ffffff",
                       blob(P.cloud_pts(cx + 10, cy + 16, 108 * sc, 30 * sc, 6, sd=8020 + k), "#e3f1fb", .9), w=3.6, seed=8030 + k))
    # навес мойки: полосатый край
    s.append(shape(rect_pts(-900, 360, W + 900, 420), "#f4f6f8", "", w=4.6, seed=8040))
    stripe = []
    for k in range(-12, 26):
        x = k * 90
        stripe.append(blob([(x, 420), (x + 45, 420), (x + 45, 470, 1), (x + 22, 486), (x, 470, 1)], "#2f86d6" if k % 2 == 0 else "#ffffff"))
    s.append("".join(stripe))
    s.append(line([(-900, 420), (W + 900, 420)], 4.4, INK, taper=.05, wmin=.9, seed=8041))
    # задняя стена — плитка
    s.append(blob([(-900, 486), (W + 900, 486), (W + 900, GROUND), (-900, GROUND)], "#dfeaf0"))
    for k in range(0, 14):
        y = 520 + k * 52
        s.append(f'<rect x="-900" y="{y}" width="{W + 1800}" height="3" fill="#c3d3dd"/>')
    for r in range(14):
        y = 520 + r * 52
        off = 0 if r % 2 == 0 else 50
        for k in range(-10, 22):
            x = k * 100 + off
            s.append(f'<rect x="{x}" y="{y - 49}" width="3" height="49" fill="#c3d3dd"/>')
    # тень под навесом
    s.append(f'<rect x="-900" y="486" width="{W + 1800}" height="70" fill="#b8cad6" opacity=".55"/>')
    # шланг на катушке у стены слева
    s.append(shape(ellipse_pts(30, 760, 58, 58, 18), "#f2c230", blob(ellipse_pts(42, 772, 44, 44, 14), "#d8a420", .8), w=4.2, seed=8050))
    for r in (40, 28):
        s.append(f'<path d="{lib.ink_closed(ellipse_pts(30, 760, r, r, 16), 3.4, seed=8051 + r)}" fill="#3a3440"/>')
    s.append(line([(60, 800), (80, 900), (60, 1010), (90, 1120)], 9, "#3a3440", taper=.05, wmin=.9, seed=8053))
    # пол: мокрый бетон
    s.append(blob([(-900, GROUND), (W + 900, GROUND), (W + 900, H + 900), (-900, H + 900)], "#9fb0bc"))
    s.append(blob([(-900, GROUND), (W + 900, GROUND), (W + 900, GROUND + 40), (-900, GROUND + 40)], "#8a9caa"))
    s.append(line([(-900, GROUND), (W + 900, GROUND)], 4.6, INK, taper=.05, wmin=.9, seed=8060))
    # лужи-отражения
    for k, (cx, cy, rx) in enumerate(((240, 1330, 210), (820, 1420, 240), (480, 1600, 300))):
        s.append(blob(ellipse_pts(cx, cy, rx, rx * .12, 18), "#b9d6e8", .9))
        s.append(line([(cx - rx * .5, cy - 4), (cx + rx * .1, cy - 6)], 5, "#e8f4fb", seed=8070 + k, op=.9))
    # решётка слива
    s.append(shape(rect_pts(380, 1250, 700, 1290, 6), "#6f7f8c", "".join(
        f'<rect x="{392 + k * 26}" y="1258" width="12" height="24" rx="3" fill="#3f4a55"/>' for k in range(12)), w=3.6, seed=8080))
    return "".join(s)


def gantry_back():
    """Жёлтая арка мойки: стойки и верхняя балка с форсунками (за машиной)."""
    s = []
    for x0 in (110, 910):
        s.append(shape(rect_pts(x0, 560, x0 + 64, GROUND + 6), "#f2c230",
                       blob(rect_pts(x0 + 40, 560, x0 + 64, GROUND + 6), "#d8a420", .9), w=4.6, seed=8100 + x0))
        s.append(shape(rect_pts(x0 - 14, GROUND - 14, x0 + 78, GROUND + 10, 4), "#5a6470", "", w=3.6, seed=8110 + x0))
    beam = rect_pts(80, 500, 1000, 584, 8)
    inner = blob(rect_pts(80, 556, 1000, 584), "#d8a420", .9)
    for k in range(10):           # предупреждающие полосы
        x = 120 + k * 88
        inner += blob([(x, 500), (x + 34, 500), (x + 4, 556), (x - 30, 556)], "#2a2630", .92)
    s.append(shape(beam, "#f2c230", inner, w=5, seed=8120))
    for k in range(7):            # форсунки
        x = 190 + k * 115
        s.append(shape(rect_pts(x - 12, 584, x + 12, 606, 3), "#8f9aa6", "", w=3, seed=8130 + k))
    return "".join(s)


# ═══════════════════════════════ щётки
def spin_phase(t, t0, w=15.0, tau=0.18):
    e = t - t0
    if e <= 0:
        return 0.0
    return w * (e - tau * (1 - math.exp(-e / tau)))


def spin_speed(t, t0, tau=0.18):
    e = t - t0
    return 0.0 if e <= 0 else 1 - math.exp(-e / tau)


def brush_v(cx, y0, y1, R, col, ph, sp, sd):
    """Вертикальная щётка сбоку: столб ворса с рваным краем; полосы ворса бегут поперёк (вращение вокруг оси)."""
    dark, light = sh(col, (.72, .72, .8)), lib.mix(col, "#ffffff", .3)
    n = 16
    ys = np.linspace(y0, y1, n)
    L, Rr = [], []
    for i, y in enumerate(ys):
        a = 8 * math.sin(y * .045 + ph * 2.0) * (0.4 + sp) + 5 * math.sin(i * 2.7 + sd)
        b = 8 * math.sin(y * .045 + ph * 2.0 + 1.7) * (0.4 + sp) + 5 * math.cos(i * 2.3 + sd)
        L.append((cx - R - a, y))
        Rr.append((cx + R + b, y))
    pts = [(cx - R * .8, y0 - 8)] + L + [(cx, y1 + 10)] + Rr[::-1] + [(cx + R * .8, y0 - 8)]
    inner = ""
    N = 12
    for k in range(N):
        th = ph + 2 * math.pi * k / N
        c = math.cos(th)
        if c <= 0.05:
            continue
        x = cx + R * math.sin(th)
        wd = max(4.0, 2 * math.pi * R / N * c * .42)
        cc = dark if k % 2 == 0 else light
        inner += f'<rect x="{f(x - wd / 2)}" y="{f(y0 - 20)}" width="{f(wd)}" height="{f(y1 - y0 + 40)}" fill="{cc}" opacity=".85"/>'
    inner += blob(rect_pts(cx + R * .45, y0 - 20, cx + R + 30, y1 + 30), dark, .55)
    if sp > .4:                   # смаз вращения: тонкие штрихи поперёк
        for k in range(7):
            y = y0 + 40 + k * (y1 - y0 - 80) / 6
            inner += line([(cx - R * .7, y + 6), (cx, y), (cx + R * .7, y + 6)], 3, "#ffffff", seed=sd + 40 + k, op=.55 * sp)
    s = shape(pts, col, inner, w=4.4, seed=sd)
    # ось и мотор сверху
    s += shape(rect_pts(cx - 30, y0 - 54, cx + 30, y0 - 8, 8), "#8f9aa6", blob(rect_pts(cx + 8, y0 - 54, cx + 30, y0 - 8), "#6f7a86", .9), w=3.8,
               seed=sd + 2)
    s += shape(rect_pts(cx - 9, 584, cx + 9, y0 - 54), "#5a6470", "", w=3, seed=sd + 3)
    return s


def brush_h(x0, x1, cy, R, col, ph, sp, sd):
    """Верхняя горизонтальная щётка над крышей: полосы бегут сверху вниз."""
    dark, light = sh(col, (.72, .72, .8)), lib.mix(col, "#ffffff", .3)
    n = 18
    xs = np.linspace(x0, x1, n)
    T, B = [], []
    for i, x in enumerate(xs):
        a = 7 * math.sin(x * .05 + ph * 2) * (0.4 + sp) + 4 * math.sin(i * 2.9 + sd)
        b = 7 * math.sin(x * .05 + ph * 2 + 1.3) * (0.4 + sp) + 4 * math.cos(i * 2.1 + sd)
        T.append((x, cy - R - a))
        B.append((x, cy + R + b))
    pts = [(x0 - 10, cy)] + T + [(x1 + 10, cy)] + B[::-1]
    inner = ""
    N = 12
    for k in range(N):
        th = ph + 2 * math.pi * k / N
        c = math.cos(th)
        if c <= 0.05:
            continue
        y = cy + R * math.sin(th)
        hd = max(4.0, 2 * math.pi * R / N * c * .42)
        cc = dark if k % 2 == 0 else light
        inner += f'<rect x="{f(x0 - 20)}" y="{f(y - hd / 2)}" width="{f(x1 - x0 + 40)}" height="{f(hd)}" fill="{cc}" opacity=".85"/>'
    inner += blob(rect_pts(x0 - 20, cy + R * .45, x1 + 20, cy + R + 30), dark, .55)
    s = shape(pts, col, inner, w=4.4, seed=sd)
    for x in (x0 - 26, x1 + 26):  # подвес к балке
        s += shape(rect_pts(x - 10, 584, x + 10, cy + 8), "#5a6470", "", w=3, seed=sd + 3 + int(x))
        s += shape(ellipse_pts(x, cy, 22, 22, 12), "#8f9aa6", blob(ellipse_pts(x + 6, cy + 6, 14, 14, 10), "#6f7a86", .9), w=3.6, seed=sd + 5 + int(x))
    return s


# ═══════════════════════════════ машина (бок, носом вправо); система: колёса на y=0, центр между осями x=0
WHEEL_X = (-195, 205)
WR = 64


def car_body_pts():
    pts = [(-318, -46, 1), (-326, -110), (-320, -196), (-292, -284), (-246, -330), (-80, -346), (40, -342), (100, -320),
           (186, -214), (290, -192), (326, -160), (336, -96), (330, -44, 1)]
    # низ: от переда к заду с арками колёс
    for wx in (WHEEL_X[1], WHEEL_X[0]):
        r = 82
        a0, a1 = math.radians(-24), math.radians(204)
        pts.append((wx + r * math.cos(a0), -64 - r * math.sin(a0), 1))
        for a in np.linspace(a0, a1, 12)[1:-1]:
            pts.append((wx + r * math.cos(a), -64 - r * math.sin(a)))
        pts.append((wx + r * math.cos(a1), -64 - r * math.sin(a1), 1))
    return pts


FRONT_WIN = [(-24, -204, 1), (-24, -318, 1), (34, -318), (84, -302), (162, -212, 1), (162, -204, 1)]
REAR_WIN = [(-266, -204, 1), (-282, -270), (-238, -318), (-60, -322, 1), (-60, -204, 1)]


def wheel(x, ang, sd):
    s = shape(ellipse_pts(x, -64, WR, WR, 22), "#2a2630", blob(ellipse_pts(x + 10, -54, WR - 8, WR - 8, 18), "#1c1822", .8), w=4.2, seed=sd)
    s += shape(ellipse_pts(x, -64, 36, 36, 18), "#c9ced6", blob(ellipse_pts(x + 6, -58, 28, 28, 14), "#a7aeb8", .8), w=3.4, seed=sd + 1)
    for k in range(5):
        a = ang + k * 2 * math.pi / 5
        s += line([(x + 8 * math.cos(a), -64 + 8 * math.sin(a)), (x + 30 * math.cos(a), -64 + 30 * math.sin(a))], 7, "#7f8894", taper=.1, wmin=.8,
                  seed=sd + 3 + k)
    s += f'<circle cx="{f(x)}" cy="-64" r="9" fill="#5a6470"/>'
    return s


def car(x, gy, wang, tilt, bdy, glass_drop, driver_svg, foam_svg="", arm_svg="", sc=1.0):
    """Машина: x — центр, gy — земля; tilt — клевок кузова (°, + — нос вниз), bdy — подвеска; glass_drop 0..1."""
    b = []
    body = car_body_pts()
    inner = blob([(-330, -110), (340, -110), (340, -30), (-330, -30)], CAR_SH, .9)
    inner += blob([(-300, -260), (-60, -300), (190, -200), (300, -186), (300, -178), (-310, -230)], CAR_HI, .55)
    inner += line([(-300, -150), (310, -140)], 3, CAR_SH, seed=8301, op=.9)
    inner += line([(-40, -200), (-36, -60)], 3.4, INK, seed=8302, op=.85)      # шов двери
    inner += line([(166, -200), (176, -70)], 3.4, INK, seed=8303, op=.85)
    inner += shape(rect_pts(40, -180, 86, -166, 6), "#d8dde4", "", w=2.6, seed=8304)      # ручка
    inner += shape(rect_pts(-210, -180, -166, -166, 6), "#d8dde4", "", w=2.6, seed=8305)
    b.append(shape(body, CAR, inner, w=5.4, seed=8300))
    # окна: салон тёмный, водитель, стекло
    for k, wp in enumerate((REAR_WIN, FRONT_WIN)):
        cid = lib.clip_of(wp)
        cabin = blob(rect_pts(-300, -360, 200, -190), "#3d4a5c") + blob(rect_pts(-300, -230, 200, -190), "#2c3644")
        cabin += blob([(-300, -360), (-150, -360), (-200, -190), (-300, -190)], "#46566a", .8)
        drv = driver_svg if k == 1 else ""
        gl = ""
        if k == 1:
            dy = 120 * glass_drop
            gl = (f'<g transform="translate(0 {f(dy)})">' + blob(wp, GLASS, .5) +
                  line([(0, -300), (40, -250)], 9, "#ffffff", seed=8311, op=.75) + line([(30, -310), (80, -240)], 5, "#ffffff", seed=8312, op=.6) +
                  line([(-22, -300 + 0), (160, -300)], 3, INK, seed=8313, op=.6 if glass_drop > .02 else 0) + "</g>")
        else:
            gl = blob(wp, GLASS, .5) + line([(-240, -300), (-190, -230)], 9, "#ffffff", seed=8314, op=.75)
        b.append(f'<g clip-path="url(#{cid})">{cabin}{drv}{gl}</g>')
        b.append(f'<path d="{lib.ink_closed(wp, 4.2, seed=8320 + k)}" fill="{INK}"/>')
    # стойка B между окнами
    b.append(shape(rect_pts(-60, -322, -24, -204), CAR_SH, "", w=3.4, seed=8330))
    # зеркало, фары, бамперы
    b.append(shape([(150, -224), (196, -236), (206, -206), (162, -198)], CAR, blob([(150, -210), (206, -214), (206, -206), (162, -198)], CAR_SH), w=3.6,
                   seed=8331))
    b.append(shape([(292, -182), (326, -164), (330, -138), (298, -146)], "#fff3b0", "", w=3.4, seed=8332))
    b.append(shape([(-326, -196), (-310, -196), (-306, -150), (-326, -146)], "#e2483d", "", w=3.2, seed=8333))
    b.append(shape(rect_pts(240, -76, 344, -44, 10), "#c9ced6", blob(rect_pts(240, -58, 344, -44), "#a7aeb8"), w=3.6, seed=8334))
    b.append(shape(rect_pts(-336, -80, -250, -48, 10), "#c9ced6", blob(rect_pts(-336, -60, -250, -48), "#a7aeb8"), w=3.6, seed=8335))
    body_g = f'<g transform="translate(0 {f(bdy)}) rotate({f(tilt)} 0 -60)">{"".join(b)}{arm_svg}{foam_svg}</g>'
    wh = "".join(wheel(wx, wang, 8340 + i * 10) for i, wx in enumerate(WHEEL_X))
    shadow = blob(ellipse_pts(0, 4, 360, 22, 18), "#55667a", .45, blur(6))
    return f'<g transform="translate({f(x)} {f(gy)}) scale({f(sc)})">{shadow}{wh}{body_g}</g>'


def driver_in_car(t, fc, smile, look, blink, sc=0.74, hx=62, hy=-250, tilt=0.0):
    """Водитель за стеклом: голова в (hx, hy) системы машины, тело ниже пояса окна (его закрывает дверь)."""
    sp = dict(DRIVER, face=fc)
    pose = {"look": look, "mouth": "smile" if smile > .5 else "flat", "brow": 0.6 * smile, "blink": blink, "head_tilt": tilt,
            "legs": {"L": (0, 0), "R": (0, 0)}}
    y0 = hy + 624 * sc
    return person.draw(sp, dict(pose, no_legs=True, no_arms=True), hx, y0, sc, sd=8400)


# ═══════════════════════════════ пена, вода, брызги (s08)
FOAM = [(-250, -300, 40), (-190, -330, 52), (-120, -350, 46), (-40, -356, 50), (40, -352, 44), (110, -326, 40), (220, -206, 40), (280, -192, 34),
        (-300, -230, 30), (-150, -365, 30), (0, -372, 34), (240, -222, 26)]


def foam(t):
    s = []
    for k, (x, y, r) in enumerate(FOAM):
        t0 = AVTO + 0.08 + k * 0.07
        e = t - t0
        if e < 0:
            continue
        k_ = back_out(clamp(e / 0.25), 2.2) * (1 + 0.04 * math.sin(t * 9 + k))
        rr = r * k_
        pts = P.cloud_pts(x, y, rr * 1.2, rr * .8, 6, sd=8500 + k)
        s.append(shape(pts, "#ffffff", blob(ellipse_pts(x + rr * .25, y + rr * .3, rr * .9, rr * .45, 12), "#d6ebf8", .9), w=3.2, seed=8510 + k))
        for j in range(2):     # пузырьки
            bx, by = x + (j - .5) * rr * .9, y - rr * .5 - 3 * j
            s.append(f'<circle cx="{f(bx)}" cy="{f(by)}" r="{f(5 + 2 * j)}" fill="#ffffff" stroke="{INK}" stroke-width="2"/>')
    return "".join(s)


def water(t):
    """Струи из форсунок сверху: штрихи падают от балки до щёток и крыши; начинаются на «автомойке»."""
    e = t - AVTO
    if e < 0:
        return ""
    s = []
    amp = smooth(0, 0.15, e)
    for k in range(7):
        x = 190 + k * 115
        y_end = 700 if 160 < x < 930 else 700
        for j in range(3):
            ph = ((t * 3.4 + j / 3 + k * .13) % 1.0)
            y0 = 606 + ph * (y_end - 606)
            ln = min(44 * amp, y_end - y0)
            if ln < 6:
                continue
            for dx in (-10, 10):
                s.append(line([(x + dx * (1 + ph), y0), (x + dx * (1 + ph) * 1.25, y0 + ln)], 4, "#7fc3f0", taper=.4, wmin=.3,
                              seed=8600 + k * 10 + j))
    return "".join(s)


def drops(t, cx, cy, R, side, sd):
    """Капли, слетающие с крутящейся щётки по дуге."""
    sp = spin_speed(t, AVTO)
    if sp <= 0.05:
        return ""
    s = []
    rs = np.random.RandomState(sd)
    for k in range(10):
        per = 0.5
        t0 = AVTO + rs.uniform(0, per)
        e = (t - t0) % per if t > t0 else -1
        if e < 0:
            continue
        y = cy + rs.uniform(-260, 220)
        vx = side * rs.uniform(500, 900)
        vy = rs.uniform(-420, -150)
        x = cx + side * R + vx * e
        yy = y + vy * e + 1400 * e * e
        r = rs.uniform(6, 10) * (1 - e / per * .5)
        ang = math.degrees(math.atan2(vy + 2800 * e, vx)) - 90
        s.append(f'<g transform="translate({f(x)} {f(yy)}) rotate({f(ang)})">' + shape([(0, -r * 2.2), (r, 0), (0, r), (-r, 0)], "#8fd0f5", "", w=2.4,
                                                                                       seed=sd + k) + "</g>")
    return "".join(s)


def s08(t):
    art = [_ST["bg"], _ST["gantry"]]
    ph = spin_phase(t, AVTO)
    sp = spin_speed(t, AVTO)
    sway = 0.25 * math.sin(t * 2.2)          # до старта щётки чуть качаются (машина толкает воздух)
    art.append(brush_v(220, 700, GROUND - 30, 78, "#2f86d6", ph + sway, sp, 8200))
    art.append(brush_v(870, 700, GROUND - 30, 78, "#e2483d", -ph - sway, sp, 8220))
    art.append(drops(t, 220, 900, 90, -1, 8240))
    art.append(drops(t, 870, 900, 90, 1, 8260))
    # машина въезжает и тормозит с клевком
    t_in, t_stop = 13.75, 14.42
    u = clamp((t - t_in) / (t_stop - t_in))
    x = 60 + (CAR_X - 60) * ease_out(u, 2)
    e_stop = t - t_stop
    tilt = 2.6 * P.kick(t, t_stop, 5, 12) if e_stop > 0 else -0.6 * smooth(13.75, 13.9, t)
    bdy = 4 * math.sin(t * 7) * (1 - u) * .5 + 6 * P.kick(t, t_stop, 6, 14)
    wang = (x - 60) / WR
    glass = ease_io(clamp((t - (VODIT - 0.05)) / 0.35))
    turn = smooth(VODIT + 0.05, VODIT + 0.35, t)
    fc = 0.55 - 0.5 * turn
    look = (0.7 * (1 - turn) + 0.1 * turn, -0.1 + 0.2 * turn)
    blink = P.bump(t, 14.05, 0.14) + P.bump(t, 15.3, 0.14)
    drv = driver_in_car(t, fc, turn, look, blink, tilt=-3 * turn + 1.5 * math.sin(t * 2))
    art.append(car(x, GROUND, wang, tilt, bdy, glass, drv, foam(t)))
    art.append(brush_h(330, 780, 772 - 0, 62, "#e2483d" if False else "#2f86d6", ph * 1.1, sp, 8280))
    art.append(water(t))
    # «пш-ш» — пар/брызги на старте щёток
    art.append(P.pop_lines(220, 760, t - AVTO, 90, 150, 6, col="#8fd0f5", w=7, sd=8700))
    art.append(P.pop_lines(870, 760, t - AVTO, 90, 150, 6, col="#8fd0f5", w=7, sd=8710))
    uu = clamp((t - 13.75) / 2.05)
    sc = 1.42 + 0.3 * ease_io(uu) + 0.03 * P.kick(t, AVTO, 6, 14) + 0.035 * P.kick(t, VODIT + 0.1, 6, 14)
    return "".join(art), cam(540 + 50 * ease_io(uu), 955 - 50 * ease_io(uu), sc, 0.7 - 1.0 * uu)


# ═══════════════════════════════ s09: окошко кассы и окно машины
BOX = (150, 250, 770, 640)          # окошко кассы (проём)


def bg_booth():
    s = []
    g = lib.lin_grad([(0, "#7cc4f2", 1), (1, "#cdeafb", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{H + 1800}" fill="url(#{g})"/>')
    s.append(shape(P.cloud_pts(150, -40, 150, 52, 7, sd=9001), "#ffffff", "", w=3.6, seed=9002))
    s.append(shape(ellipse_pts(1010, -60, 80, 80, 20), "#ffd84a", blob(ellipse_pts(1030, -40, 60, 60, 16), "#f6c234", .7), w=4.4, seed=9005))
    # будка кассы: стена во всю ширину
    s.append(shape(rect_pts(-900, 120, W + 900, 1100), "#eef2f5", "".join(
        f'<rect x="-900" y="{y}" width="{W + 1800}" height="3" fill="#d3dce3"/>' for y in range(230, 1100, 76)), w=5, seed=9010))
    roof = [(-900, 70), (W + 900, 70), (W + 900, 150, 1), (-900, 150, 1)]
    inner = "".join(blob([(x, 112), (x + 50, 112), (x + 50, 150), (x, 150)], "#ffffff") for x in range(-900, W + 900, 100))
    s.append(shape(roof, "#2f86d6", inner, w=5, seed=9011))
    s.append(blob(rect_pts(-900, 150, W + 900, 190), "#c5d0d8", .8))
    # окошко
    ox0, oy0, ox1, oy1 = BOX
    s.append(shape(rect_pts(ox0 - 30, oy0 - 30, ox1 + 30, oy1 + 30, 18), "#c9d2da", blob(rect_pts(ox1, oy0 - 30, ox1 + 30, oy1 + 30), "#aeb9c3", .8),
                   w=4.6, seed=9020))
    inner = blob(rect_pts(ox0, oy0, ox1, oy1), "#2f4656")
    inner += blob([(ox0, oy0), (ox0 + 200, oy0), (ox0 + 60, oy1), (ox0, oy1)], "#3a5566", .9)
    inner += f'<rect x="{ox0}" y="{oy0}" width="{ox1 - ox0}" height="70" fill="#f4d58a" opacity=".22"/>'     # лампа внутри
    inner += shape(rect_pts(560, 330, 740, 470, 8), "#3a3f4c", blob(rect_pts(574, 344, 726, 456, 4), "#7fb3d6"), w=3.4, seed=9022)   # монитор
    inner += shape(rect_pts(630, 470, 670, 520), "#3a3f4c", "", w=3, seed=9025)
    _ST["booth_inner_clip"] = (ox0, oy0, ox1, oy1)
    s.append(shape(rect_pts(ox0, oy0, ox1, oy1, 10), "#2f4656", inner, w=5, seed=9021))
    return "".join(s)


def booth_front():
    """Полочка окошка и низ рамы — поверх работника (он стоит за ними)."""
    ox0, oy0, ox1, oy1 = BOX
    s = shape(rect_pts(ox0 - 60, oy1 - 6, ox1 + 64, oy1 + 36, 6), "#dfe5ea", blob(rect_pts(ox0 - 60, oy1 + 20, ox1 + 64, oy1 + 36), "#b9c3cc"), w=4.4,
              seed=9024)
    return s


WORKER = dict(skin="#c98c66", hair="short", hair_c="#2a1a14", top="#2c3e66", low="#2c3e66", face=0.45, cap="#2f86d6", brow_c="#2a1a14")


def thumb(Wr, d, k, skin, sd, flip=1, thumb_a=0.6):
    """Большой палец отдельно (как в hand.hand), чтобы лечь поверх карточки."""
    sk, ssh, ssh2, nail = skin
    Wr = np.array(Wr, float)
    d = np.array(d, float)
    d /= np.linalg.norm(d) + 1e-9
    n = np.array([-d[1], d[0]]) * flip

    def tf(x, y):
        p = Wr + d * x * k + n * y * k
        return (float(p[0]), float(p[1]))
    a = -0.95 + 0.75 * thumb_a
    base = np.array([16.0, -30.0])
    p1 = base + np.array([math.cos(a), math.sin(a)]) * 34
    a2 = a + .25 + .3 * thumb_a
    p2 = p1 + np.array([math.cos(a2), math.sin(a2)]) * 30
    a3 = a2 + .2
    p3 = p2 + np.array([math.cos(a3), math.sin(a3)]) * 20
    T = [tf(*q) for q in (base + np.array([-6, 8]), base, p1, p2, p3)]
    th = lib.band(T, 27 * k, 19 * k, step=2.5, cap=True)
    inner = blob(lib.band(T[1:4], 12 * k, 8 * k, step=3, cap=False), ssh, .5)
    if nail != sk:
        dd = (p3 - p2) / np.linalg.norm(p3 - p2)
        nc = tf(*(p3 - dd * 4))
        ang = math.degrees(math.atan2(d[1], d[0]))
        inner += blob(ellipse_pts(nc[0], nc[1], 6.5 * k, 6 * k, 10, rot=ang), nail)
    return shape(th, sk, inner, w=3.0, seed=sd)


def hand_pinch(Wr, d, k, skin, sd, flip=1, item=""):
    """Кисть держит плоский предмет щепотью: пальцы — снизу (за предметом), предмет, большой палец — сверху."""
    sk, ssh, ssh2, nail = skin
    fingers = HD.hand(Wr, d, shape_fn=shape, line_fn=line, skin=sk, skin_sh=ssh, skin_sh2=ssh2, nail=nail, flip=flip, k=k,
                      curl=(.35, .45, .55, .65), spread=.12, thumb=.6, bend=.1, seed=sd, nails=nail != sk, show_thumb=False)
    return fingers + item + thumb(Wr, d, k, skin, sd + 50, flip, .7)


def card_small(sd=0, stamps=0):
    """Маленькая карточка в руке: кремовая, синяя полоса, 2×5 кружков (без букв). Центр (0, 0), 150×94."""
    s = shape(rect_pts(-75, -47, 75, 47, 9), "#fbf3df", blob(rect_pts(-75, -47, 75, -24), "#2f6db5") + blob(rect_pts(-75, 34, 75, 47), "#efe2c2"),
              w=3.2, seed=sd)
    for r in range(2):
        for c in range(5):
            x, y = -52 + c * 26, -4 + r * 26
            s += f'<circle cx="{x}" cy="{y}" r="8.5" fill="#ffffff" stroke="#2f6db5" stroke-width="3.2"/>'
    s += f'<circle cx="-50" cy="-36" r="5" fill="#ffffff"/><circle cx="-38" cy="-36" r="3.5" fill="#ffffff"/>'
    return s


def gift_icon(x, y, k, t, sd):
    """Значок «бесплатная мойка»: белый круг, синяя машинка с блёстками, сверху подарочный бант."""
    if k <= 0:
        return ""
    s = []
    s.append(blob(ellipse_pts(8, 10, 118, 118, 28), "#5a7a95", .35, blur(5)))
    s.append(shape(ellipse_pts(0, 0, 118, 118, 28), "#ffffff", blob(ellipse_pts(14, 18, 104, 104, 24), "#e6f2fb", .9), w=6, seed=sd))
    # машинка
    c = [(-70, 24, 1), (-72, -4), (-50, -12), (-30, -44), (24, -46), (48, -14), (72, -8), (76, 24, 1)]
    s.append(shape(c, CAR, blob([(-72, 10), (76, 10), (76, 24), (-72, 24)], CAR_SH, .9) +
                   blob([(-24, -36), (-4, -36), (-4, -14), (-38, -14)], GLASS) + blob([(4, -36), (20, -36), (38, -14), (4, -14)], GLASS), w=4.4, seed=sd + 1))
    for wx in (-40, 44):
        s.append(shape(ellipse_pts(wx, 26, 17, 17, 12), "#2a2630", blob(ellipse_pts(wx, 26, 7, 7, 8), "#c9ced6"), w=3.4, seed=sd + 2 + wx))
    # пузыри-пена над машинкой
    for j, (bx, by, br) in enumerate(((-50, -62, 13), (-28, -74, 9), (40, -60, 11))):
        s.append(f'<circle cx="{bx}" cy="{by}" r="{br}" fill="#ffffff" stroke="{INK}" stroke-width="3"/>')
    # бант сверху
    by = -118
    for sg in (-1, 1):
        loop = [(0, by), (sg * 50, by - 46), (sg * 70, by - 20), (sg * 54, by + 8), (sg * 10, by + 4)]
        if sg < 0:
            loop = loop[::-1]
        s.append(shape(loop, "#e2483d", blob(ellipse_pts(sg * 46, by - 10, 14, 10, 10), "#b8261f", .9), w=4.2, seed=sd + 10 + sg))
        tail = [(sg * 6, by + 6), (sg * 40, by + 52), (sg * 26, by + 60), (sg * 2, by + 18)]
        if sg < 0:
            tail = tail[::-1]
        s.append(shape(tail, "#e2483d", "", w=3.6, seed=sd + 20 + sg))
    s.append(shape(ellipse_pts(0, by + 2, 16, 14, 10), "#ff6b5e", "", w=3.8, seed=sd + 30))
    # блёстки вокруг — мерцают
    for j, (sx, sy, r) in enumerate(((-150, -40, 30), (150, -70, 36), (130, 90, 24), (-128, 96, 22), (0, 150, 18))):
        tw = 0.75 + 0.35 * math.sin(t * 14 + j * 1.9)
        s.append(P.sparkle(sx, sy, r * tw, "#ffd84a", sd=sd + 40 + j, rot=15 * j + 40 * t))
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(k)})">{"".join(s)}</g>'


def ik(a, b, L1, L2, side=1):
    """Локоть между плечом a и кистью b (длины L1, L2); side — в какую сторону от прямой a→b сгиб."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = max(1e-3, min(math.hypot(dx, dy), L1 + L2 - 1))
    x = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, L1 * L1 - x * x))
    ux, uy = dx / d, dy / d
    return (a[0] + ux * x - uy * h * side, a[1] + uy * x + ux * h * side)


def s09(t):
    art = [_ST["booth"]]
    ox0, oy0, ox1, oy1 = BOX
    take0, take1 = MOYKU - 0.3, MOYKU
    reach = ease_out(clamp((t - 15.35) / (KART - 15.35)), 3)
    reach_d = ease_io(clamp((t - take0) / (take1 - take0)))
    release = ease_in(clamp((t - (MOYKU + 0.08)) / 0.35), 2)
    pull = ease_io(clamp((t - (MOYKU + 0.1)) / 0.45))
    joy = smooth(BESPL - 0.05, BESPL + 0.15, t)
    # работник за окошком (тело обрезано проёмом), рука в синей перчатке тянет карточку вниз к машине
    wsc = 0.82
    whx, why = 330, 420 + 4 * math.sin(t * 2.3)
    lean = 8 * reach - 6 * release
    wpose = {"look": (0.8, 0.7), "mouth": "smile", "brow": 0.4, "blink": P.bump(t, 16.05, 0.14), "head_tilt": lean * .5 + 2 * math.sin(t * 1.8)}
    wbody = person.draw(WORKER, dict(wpose, no_legs=True, no_arms=True), whx, why + 624 * wsc, wsc, sd=9150)
    cid = lib.clip_rect(ox0, oy0, ox1 - ox0, oy1 - oy0, 10)
    art.append(f'<g clip-path="url(#{cid})">{wbody}</g>')
    sh0 = (whx + 52 * wsc + 6, why + (624 - 502) * wsc + 6)
    # запястье работника: в покое у края полки → тянется вниз-вправо
    w_rest, w_out = (500, 600), (400, 760)
    wx = w_rest[0] + (w_out[0] - w_rest[0]) * reach + 12 * math.sin(t * 4.2) * (1 - reach_d)
    wy = w_rest[1] + (w_out[1] - w_rest[1]) * reach + 8 * math.sin(t * 5.1) * (1 - reach_d)
    wx -= 70 * release
    wy -= 110 * release
    elbow = ik(sh0, (wx, wy), 150, 140, -1)
    rr = release * math.pi
    d_w = np.array([0.55 + 0.3 * math.sin(rr), math.cos(rr)])
    arm_w = person.tube(sh0, elbow, (wx - d_w[0] * 10, wy - d_w[1] * 10), 66, 58, 50, WORKER["top"], 9100, inner_sh=True)
    # карточка
    pop = 1 + 0.1 * P.kick(t, KART, 7, 16)
    hold_w = (wx + 120, wy + 92)
    car_S, car_cx, car_gy = 2.3, 541, 1656
    if t < MOYKU:
        cpos = hold_w
        crot = -10 + 5 * math.sin(t * 3.4)
    else:
        dst = (470, 1080)
        cpos = (hold_w[0] + (dst[0] - hold_w[0]) * pull + (0 if pull else 0), (wy + 200 * release + 92) + (dst[1] - (wy + 200 * release + 92)) * pull)
        cpos = (520 + (dst[0] - 520) * pull, 852 + (dst[1] - 852) * pull)
        crot = -10 + 18 * pull
    card_g = (f'<g transform="translate({f(cpos[0])} {f(cpos[1])}) rotate({f(crot)}) scale({f(1.55 * pop)})">' +
              f'<g transform="translate(-45 0)">{card_small(9200)}</g></g>')
    # водитель в машине (машина крупно, видны крыша и переднее окно)
    fc = -0.6
    blink = P.bump(t, 15.9, 0.14) + P.bump(t, 17.3, 0.14)
    sp = dict(DRIVER, face=fc)
    look = (-0.6, -0.7 + 0.5 * pull) if t < MOYKU + 0.2 else (-0.5, 0.3)
    dpose = {"look": look, "mouth": "o" if BESPL - 0.02 < t < BESPL + 0.32 else ("smile" if t > 15.55 else "flat"),
             "brow": 0.2 + 0.7 * joy, "blink": blink, "head_tilt": 6 - 4 * pull + 4 * joy * P.bump(t, BESPL, 0.5) + 1.5 * math.sin(t * 2.4)}
    drv = person.draw(sp, dict(dpose, no_legs=True, no_arms=True), 88, -262 + 624 * .74, .74, sd=8400)
    car_svg = car(car_cx, car_gy, 0.3, 0, 0, 1.0, drv, sc=car_S)
    art.append(car_svg)
    # рука водителя: из окна вверх к карточке (ниже кромки окна её закрывает дверь)
    beltY = car_gy - 204 * car_S
    sh_d = (car_cx - 6 * car_S, beltY + 40)
    if t < take0:
        hx, hy = sh_d[0] - 30, beltY + 120
    else:
        tgt = (cpos[0] - 6, cpos[1] + 90)
        a = reach_d if t < MOYKU else 1.0
        hx = sh_d[0] - 30 + (tgt[0] - sh_d[0] + 30) * a
        hy = beltY + 120 + (tgt[1] - beltY - 120) * a
    d_arm = ""
    if hy < beltY + 60:
        elb = ik(sh_d, (hx, hy + 30), 170, 160, -1)
        d_arm = person.tube(sh_d, elb, (hx, hy + 30), 78, 70, 60, DRIVER["top"], 9400, inner_sh=True)
        cut = lib.clip_rect(-900, -900, W + 1800, beltY + 900)
        d_arm = f'<g clip-path="url(#{cut})">{d_arm}</g>'
    # кисти: работник держит щепотью до «мойку», потом водитель
    if t < MOYKU:
        w_hand = hand_pinch((wx, wy), tuple(d_w), 1.05, GLOVE, 9300, flip=1, item=card_g)
        card_g = ""
    else:
        w_hand = HD.hand((wx, wy), tuple(d_w), shape_fn=shape, line_fn=line, skin=GLOVE[0], skin_sh=GLOVE[1], skin_sh2=GLOVE[2], nail=GLOVE[0],
                         flip=1, k=1.05, curl=(.25, .3, .35, .45), spread=.25, thumb=.2, seed=9300, nails=False)
    d_hand = ""
    if hy < beltY + 60:
        if t >= MOYKU:
            d_hand = hand_pinch((hx, hy + 30), (0, -1), 1.05, D_SKIN, 9450, flip=-1, item=card_g)
            card_g = ""
        else:
            d_hand = HD.hand((hx, hy + 30), (0, -1), shape_fn=shape, line_fn=line, skin=D_SKIN[0], skin_sh=D_SKIN[1], skin_sh2=D_SKIN[2], nail=D_SKIN[3],
                             flip=-1, k=1.05, curl=(.15, .2, .25, .3), spread=.3, thumb=.15, seed=9450)
        cut = lib.clip_rect(-900, -900, W + 1800, beltY + 900)
        d_hand = f'<g clip-path="url(#{cut})">{d_hand}</g>'
    art.append(booth_front() if False else "")
    art.append(arm_w + w_hand)
    art.append(d_arm + d_hand)
    art.append(card_g)
    # значок «бесплатно» над карточкой
    e = t - BESPL
    if e > -0.04:
        k = back_out(clamp((e + 0.04) / 0.26), 2.4) * (1 + 0.025 * math.sin(e * 6))
        gx, gy2 = 790, 560 - 10 * math.sin(e * 3)
        art.append(gift_icon(gx, gy2, k * 1.0, t, 9500))
        art.append(P.pop_lines(gx, gy2, e, 150, 220, 8, col="#ffb52a", w=9, sd=9560))
    uu = clamp((t - 15.4) / 2.25)
    sc = 1.04 + 0.08 * ease_io(uu) + 0.035 * P.kick(t, BESPL, 6, 14) + 0.02 * P.kick(t, MOYKU, 6, 14)
    return "".join(art), cam(560 + 20 * uu, 840 + 20 * uu, sc, -0.5 + 0.8 * uu)


def build_static():
    if _ST:
        return
    _ST["bg"] = bg_wash()
    _ST["gantry"] = gantry_back()
    _ST["booth"] = bg_booth()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s08": s08, "s09": s09}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#cdeafb"/><g transform="{cm}">{art}</g>')
