"""Комната Димы в ремонте (рилс 38, сцена reno): коробка комнаты в одной точке схода — задняя стена, две боковые,
потолок, пол. Старые жёлтые обои, новая мятная краска (кусок у лестницы растёт), ободранный угол, окно (вечер — луна,
день — небо), лампа-переноска на крючке, газеты и плёнка на полу, банка краски, стремянка, коробки с плиткой, мешки,
розетка без крышки с проводами. Мир: задняя стена x XL..XR, потолок CY, низ стены FY; пол идёт к зрителю (y > FY).
Режим света и что доделано — ST (set_state)."""
import math

import numpy as np

import lib
from lib import INK, blob, ellipse_pts, line, rect_pts, shape

XL, XR, CY, FY = -80.0, 1180.0, 80.0, 1420.0
VP = (550.0, 860.0)
WIN = (900.0, 330.0, 1130.0, 860.0)            # окно на задней стене
HOOK = (250.0, 190.0)                          # крючок лампы-переноски
OUTLET = (700.0, 1330.0)

PAPER_Y, PAPER_Y2, PAPER_ST, PAPER_FL = "#ecd27e", "#d6b862", "#f2dc94", "#c49d45"
MINT, MINT_SH, MINT_HI, MINT_WET = "#a9dcc4", "#86c2a7", "#c6eadb", "#97d3b8"
PLASTER, PLASTER_SH = "#cfc6b4", "#b9af9b"
CEIL = "#ece6d8"
FLOORC, FLOOR_SH, FLOOR_LN = "#b88a5c", "#9d724a", "#8a6240"

ST = dict(tod="evening", lamp=1.0, paint=0.0, stripe=(1.0, 1.0), back_done=False, left_done=False, outlet_new=False, pendant=False,
          film_off=0.0, sheet=None)


def set_state(**kw):
    ST.update(dict(tod="evening", lamp=1.0, paint=0.0, stripe=(1.0, 1.0), back_done=False, left_done=False, outlet_new=False,
                   pendant=False, film_off=0.0, sheet=None))
    ST.update(kw)


def proj(x, y, m):
    """Точка задней стены (x, y), вынесенная к зрителю на глубину m (0 — на стене)."""
    return (VP[0] + (x - VP[0]) * (1 + m), VP[1] + (y - VP[1]) * (1 + m))


def rs(*k):
    return np.random.RandomState(sum((i + 3) * 7919 * int(v) for i, v in enumerate(k)) % (2 ** 31))


M_FAR = 2.6      # глубина переднего края комнаты


# ═════════════════════════ стены, потолок, пол ═════════════════════════
def wallpaper_pattern():
    pid = "pWp"
    if not any('id="pWp"' in d for d in lib.DEFS):
        lib.DEFS.append(f'<pattern id="{pid}" width="96" height="130" patternUnits="userSpaceOnUse">'
                        f'<rect width="96" height="130" fill="{PAPER_Y}"/><rect x="0" width="22" height="130" fill="{PAPER_ST}" opacity=".7"/>'
                        f'<rect x="22" width="3" height="130" fill="{PAPER_Y2}" opacity=".8"/>'
                        f'<path d="M62 20 c6 -8 12 0 6 6 c8 2 4 12 -4 8 c0 9 -11 8 -9 0 c-9 1 -9 -10 0 -9 c-4 -8 6 -12 7 -5 Z" fill="{PAPER_FL}" opacity=".8"/>'
                        f'<path d="M62 85 c6 -8 12 0 6 6 c8 2 4 12 -4 8 c0 9 -11 8 -9 0 c-9 1 -9 -10 0 -9 c-4 -8 6 -12 7 -5 Z" fill="{PAPER_FL}" opacity=".8"/>'
                        f'<circle cx="62" cy="26" r="3" fill="#b88a3c"/><circle cx="62" cy="91" r="3" fill="#b88a3c"/></pattern>')
    return pid


def wavy_x(x, y0, y1, amp, seed, n=18):
    r = rs(seed)
    ys = np.linspace(y0, y1, n)
    return [(x + amp * (r.uniform(-1, 1) * .6 + .4 * math.sin(i * 1.3 + seed)), y) for i, y in enumerate(ys)]


def back_wall():
    pid = wallpaper_pattern()
    o = [f'<rect x="{XL}" y="{CY}" width="{XR - XL}" height="{FY - CY}" fill="url(#{pid})"/>']
    # пятна и выцветание старых обоев
    for j, (x, y, r) in enumerate([(150, 300, 70), (980, 1050, 90), (1120, 520, 60), (300, 1150, 80)]):
        o.append(blob(ellipse_pts(x, y, r, r * .8, 14), "#c7a95a", .35))
    # ободранные места у правого края (серая штукатурка, рваный край)
    for j, (x0, y0, w, h) in enumerate([(1080, 960, 90, 150), (720, 160, 120, 70)]):
        r = rs(40 + j)
        pts = []
        for k in range(16):
            a = 2 * math.pi * k / 16
            rr = 1 + r.uniform(-.25, .2)
            pts.append((x0 + w / 2 + w / 2 * rr * math.cos(a), y0 + h / 2 + h / 2 * rr * math.sin(a)))
        o.append(shape(pts, PLASTER, blob([(p[0] + 6, p[1] + 6) for p in pts[:8]], PLASTER_SH, .5), w=3, seed=4100 + j))
    if ST["back_done"]:
        o.append(shape(rect_pts(XL, CY, XR, FY), MINT, blob(rect_pts(XL, CY, XL + 120, FY), MINT_SH, .6), w=0.1, ink=False, seed=4150))
    else:
        o.append(painted_piece())
    # карниз под потолком и плинтус
    o.append(shape(rect_pts(XL, CY, XR, CY + 22), "#e9e2d2", blob(rect_pts(XL, CY + 14, XR, CY + 22), "#cfc6b4"), w=3, seed=4180))
    o.append(shape(rect_pts(XL, FY - 30, XR, FY), "#d8cfbd", blob(rect_pts(XL, FY - 12, XR, FY), "#b9ae98", .9), w=3.4, seed=4181))
    return "".join(o)


PAINT_X0, PAINT_X1 = 70.0, 560.0                # уже покрашенный кусок (до лестницы)
STRIPE = (560.0, 660.0)                         # полоса, которую катит валик в s01


def painted_piece():
    """Покрашенный кусок: прямоугольник с неровным правым краем + полоса валика (ST['stripe'] = (верх, низ) в долях)."""
    o = []
    r = rs(77)
    left = [(PAINT_X0 + r.uniform(-8, 8), y) for y in np.linspace(FY - 30, CY + 22, 10)]
    right = []
    for i, y in enumerate(np.linspace(CY + 22, FY - 30, 22)):
        right.append((PAINT_X1 + 18 * math.sin(i * 1.7) + r.uniform(-12, 12), y))
    pts = left + right
    inner = blob([(PAINT_X0 - 20, CY), (PAINT_X0 + 70, CY), (PAINT_X0 + 60, FY), (PAINT_X0 - 20, FY)], MINT_SH, .55)
    for j in range(7):            # следы валика — вертикальные полосы чуть светлее
        x = PAINT_X0 + 40 + j * 66
        inner += blob([(x, CY + 30), (x + 22, CY + 30), (x + 18, FY - 40), (x - 4, FY - 40)], MINT_HI, .35)
    o.append(shape(pts, MINT, inner, w=2.2, seed=4200, var=.5))
    a, b = ST["stripe"]        # доли высоты стены: верх полосы (0 — потолок, 1 — пол), низ
    if b - a > .005:
        x0, x1 = STRIPE
        y0 = CY + 22 + (FY - 52 - CY) * a
        y1 = CY + 22 + (FY - 52 - CY) * b
        rr = rs(81)
        top = [(x0 + (x1 - x0) * u, y0 + 10 * math.sin(u * 7 + 1) + rr.uniform(-4, 4)) for u in np.linspace(0, 1, 7)]
        bot = [(x1 - (x1 - x0) * u, y1 + 6 * math.sin(u * 5)) for u in np.linspace(0, 1, 5)]
        sp = [(x0 - 4, y0 + 8)] + top + [(x1 + 6, y0 + 10), (x1 + 4, y1)] + bot + [(x0 - 6, y1)]
        inner = blob([(x0 + 18, y0), (x0 + 40, y0), (x0 + 36, y1), (x0 + 14, y1)], "#c9f2e2", .8)
        inner += blob([(x1 - 16, y0), (x1, y0), (x1, y1), (x1 - 16, y1)], MINT_SH, .6)
        o.append(shape(sp, MINT_WET, inner, w=2.2, seed=4210, var=.5))
    return "".join(o)


def left_wall():
    p0, p1 = (XL, CY), (XL, FY)
    q0, q1 = proj(XL, CY, M_FAR), proj(XL, FY, M_FAR)
    poly = [p0, p1, q1, q0]
    if ST["left_done"]:
        inner = blob(poly, MINT_SH, .9)
        inner += blob([p0, p1, proj(XL, FY, .25), proj(XL, CY, .25)], MINT, .9)
        return shape([(x, y, 1) for x, y in poly], MINT_SH, inner, w=4, seed=4300)
    inner = blob(poly, PLASTER_SH, .35)
    # клочья старых обоев на штукатурке (ободранный угол), трещины
    for j, (m0, m1, v0, v1) in enumerate([(.05, .45, .05, .4), (.2, .9, .55, .95), (.9, 1.5, .1, .35)]):
        r = rs(310 + j)
        pts = []
        for k in range(10):
            mm = m0 + (m1 - m0) * (k / 9)
            vv = v0 + r.uniform(-.04, .06)
            pts.append(_lw(mm, vv))
        for k in range(10):
            mm = m1 - (m1 - m0) * (k / 9)
            vv = v1 + r.uniform(-.08, .04)
            pts.append(_lw(mm, vv))
        inner += shape(pts, PAPER_Y, blob(pts[:6], PAPER_Y2, .6), w=2.6, seed=4310 + j, var=.6)
    inner += line([_lw(.6, .3), _lw(.7, .38), _lw(.68, .5), _lw(.8, .56)], 2.4, "#8e8574", seed=4330, op=.8)
    inner += line([_lw(.3, .7), _lw(.38, .66), _lw(.44, .74)], 2.2, "#8e8574", seed=4331, op=.8)
    inner += blob([p0, p1, proj(XL, FY, .18), proj(XL, CY, .18)], "#9e9686", .45)
    return shape([(x, y, 1) for x, y in poly], PLASTER, inner, w=4, seed=4300)


def _lw(m, v):
    """Точка левой стены: m — глубина, v — высота (0 — потолок, 1 — пол)."""
    return proj(XL, CY + (FY - CY) * v, m)


def right_wall():
    p0, p1 = (XR, CY), (XR, FY)
    q0, q1 = proj(XR, CY, M_FAR), proj(XR, FY, M_FAR)
    poly = [p0, p1, q1, q0]
    inner = blob(poly, PLASTER_SH, .5)
    inner += blob([p0, p1, proj(XR, FY, .2), proj(XR, CY, .2)], "#9e9686", .45)
    r = rs(350)
    for j in range(5):
        m, v = r.uniform(.1, 1.2), r.uniform(.15, .8)
        inner += line([proj(XR, CY + (FY - CY) * v, m), proj(XR, CY + (FY - CY) * (v + .06), m + .1)], 2.2, "#8e8574", seed=4351 + j, op=.7)
    return shape([(x, y, 1) for x, y in poly], "#d6cfc2", inner, w=4, seed=4350)


def ceiling():
    poly = [(XL, CY), (XR, CY), proj(XR, CY, M_FAR), proj(XL, CY, M_FAR)]
    inner = blob([(XL, CY), (XR, CY), proj(XR, CY, .3), proj(XL, CY, .3)], "#d9d2c2", .6)
    return shape([(x, y, 1) for x, y in poly], CEIL, inner, w=4, seed=4400)


def floor():
    poly = [(XL, FY), (XR, FY), proj(XR, FY, M_FAR), proj(XL, FY, M_FAR)]
    inner = ""
    for k in range(-6, 15):
        xb = XL + k * 105
        inner += line([(xb, FY), proj(xb, FY, M_FAR)], 2.6, FLOOR_LN, seed=4500 + k + 10, op=.8, taper=.1, wmin=.7)
    inner += blob([(XL, FY), (XR, FY), proj(XR, FY, .15), proj(XL, FY, .15)], FLOOR_SH, .55)
    return shape([(x, y, 1) for x, y in poly], FLOORC, inner, w=4, seed=4450)


# ═════════════════════════ окно ═════════════════════════
def window(t):
    x0, y0, x1, y1 = WIN
    day = ST["tod"] == "day"
    stops = [(0, "#6fb6ec", 1), (.7, "#a9d6f4", 1), (1, "#dcefff", 1)] if day else [(0, "#0d1534", 1), (.6, "#1b2a58", 1), (1, "#2f3f74", 1)]
    sky = lib.lin_grad(stops, 0, 0, 0, 1)
    inner = [f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{x1 - x0 + 20}" height="{y1 - y0 + 20}" fill="url(#{sky})"/>']
    if day:
        for k, (cx, cy, cw) in enumerate([(x0 + 70, y0 + 90, 60), (x0 + 200, y0 + 210, 46)]):
            cx += 6 * math.sin(t * .3 + k)
            cl = [ellipse_pts(cx, cy, cw, cw * .45, 12), ellipse_pts(cx + cw * .6, cy - 10, cw * .6, cw * .4, 12), ellipse_pts(cx - cw * .6, cy + 4, cw * .5, cw * .32, 12)]
            inner.append("".join(blob(c, "#ffffff", .92) for c in cl))
        bcol, bsh = "#9fb6c8", "#86a0b4"
    else:
        mx, my = x0 + 120, y0 + 110
        g = lib.rad_grad([(0, "#fff6d8", .55), (1, "#fff6d8", 0)], mx, my, 120)
        inner.append(f'<circle cx="{mx}" cy="{my}" r="120" fill="url(#{g})"/>')
        moon = ellipse_pts(mx, my, 42, 42, 24)
        inner.append(shape(moon, "#fff2c2", blob(ellipse_pts(mx - 12, my + 8, 9, 7, 10), "#e9d9a0") +
                           blob(ellipse_pts(mx + 14, my - 12, 6, 5, 10), "#e9d9a0"), w=3, seed=4601))
        r = rs(4602)
        for j in range(14):
            sx, sy = r.uniform(x0 + 10, x1 - 10), r.uniform(y0 + 10, y1 - 200)
            tw = .55 + .45 * math.sin(t * (2 + j % 3) + j)
            inner.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{1.6 + r.uniform(0, 1.6):.1f}" fill="#fff8e0" opacity="{tw:.2f}"/>')
        bcol, bsh = "#1a2348", "#141b3a"
    # дома за окном
    hs = [(x0 - 10, y1 - 170, 90), (x0 + 75, y1 - 250, 80), (x0 + 150, y1 - 140, 70), (x0 + 215, y1 - 210, 80)]
    rr = rs(4610)
    for k, (hx, hy, hw) in enumerate(hs):
        inner.append(blob(rect_pts(hx, hy, hx + hw, y1 + 10), bcol))
        inner.append(blob(rect_pts(hx + hw - 14, hy, hx + hw, y1 + 10), bsh))
        for a in range(3):
            for b in range(6):
                wx, wy = hx + 12 + a * 22, hy + 16 + b * 30
                if wy > y1 - 10:
                    continue
                lit = (not day) and rr.uniform() < .45
                inner.append(f'<rect x="{wx}" y="{wy}" width="11" height="14" fill="{"#ffd77a" if lit else ("#c9dbe8" if day else "#2a3566")}"/>')
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o = [f'<g clip-path="url(#{c})">{"".join(inner)}</g>']
    # рама
    fr = "#f1ece1"
    o.append(shape(rect_pts(x0 - 22, y0 - 22, x1 + 22, y0), fr, "", w=4, seed=4620))
    o.append(shape(rect_pts(x0 - 22, y0 - 22, x0, y1), fr, "", w=4, seed=4621))
    o.append(shape(rect_pts(x1, y0 - 22, x1 + 22, y1), fr, "", w=4, seed=4622))
    xm = (x0 + x1) / 2
    o.append(shape(rect_pts(xm - 9, y0, xm + 9, y1), fr, "", w=3.6, seed=4623))
    o.append(shape(rect_pts(x0, y0 + 170, x1, y0 + 186), fr, "", w=3.6, seed=4624))
    o.append(line([(x0 + 20, y0 + 220), (x0 + 60, y0 + 190)], 3, "#ffffff", seed=4625, op=.5))
    # подоконник: пока в плёнке (как у кота в s04)
    sill = [(x0 - 50, y1, 1), (x1 + 50, y1, 1), (x1 + 66, y1 + 26, 1), (x0 - 66, y1 + 26, 1)]
    o.append(shape(sill, "#e8e2d6", blob([(x0 - 66, y1 + 16), (x1 + 66, y1 + 16), (x1 + 66, y1 + 26), (x0 - 66, y1 + 26)], "#c9c1b0"), w=4, seed=4630))
    if not ST["back_done"]:
        film = [(x0 - 30, y1 - 8), (x1 + 70, y1 - 6), (x1 + 76, y1 + 60), (x1 + 40, y1 + 90), (x0 + 60, y1 + 70), (x0 - 32, y1 + 92)]
        o.append(blob(film, "#e3f1f6", .45))
        o.append(line([(x0 - 40, y1 + 40), (x0 + 60, y1 + 30), (x0 + 150, y1 + 60)], 2.4, "#ffffff", seed=4631, op=.8))
        o.append(line([(x1 - 40, y1 + 30), (x1 + 50, y1 + 55)], 2.4, "#ffffff", seed=4632, op=.8))
    # батарея под окном
    bx0, bx1, by0, by1 = x0 + 10, x1 - 10, y1 + 140, y1 + 330
    col = "#f4f1ea" if ST["back_done"] else "#d9d2c4"
    inner = "".join(blob(rect_pts(bx0 + 8 + k * 28, by0 + 10, bx0 + 20 + k * 28, by1 - 10, 5), "#cfc7b6" if ST["back_done"] else "#b9b0a0", .9)
                    for k in range(int((bx1 - bx0 - 10) / 28)))
    if not ST["back_done"]:
        for j, (px, py) in enumerate([(bx0 + 60, by0 + 60), (bx0 + 180, by1 - 50)]):
            inner += blob(ellipse_pts(px, py, 22, 12, 10), "#a48d6a", .6)
    o.append(shape(rect_pts(bx0, by0, bx1, by1, 12), col, inner, w=4, seed=4640))
    return "".join(o)


# ═════════════════════════ свет ═════════════════════════
def hook_lamp(t, on):
    """Лампа-переноска на крючке: крючок, шнур, решётка-клетка, лампочка."""
    hx, hy = HOOK
    sw = 3 * math.sin(t * 1.3)
    lx, ly = hx + sw, hy + 150
    o = []
    o.append(line([(hx - 6, hy - 10), (hx - 6, hy + 4), (hx + 6, hy + 10), (hx + 10, hy)], 5, "#5d5a58", seed=4700, taper=.2, wmin=.8))
    # шнур: с крючка вниз к лампе и петлёй к полу (к стене)
    o.append(line([(hx, hy + 6), (hx + sw * .5, hy + 70), (lx, ly - 26)], 6, "#2d2a2e", seed=4701, taper=.1, wmin=.9))
    o.append(line([(hx + 4, hy + 8), (hx + 60, hy + 140), (hx + 110, hy + 480), (hx + 170, FY - 60), (hx + 230, FY)], 5, "#2d2a2e", seed=4702,
                  taper=.1, wmin=.9))
    # ручка-патрон
    o.append(shape(rect_pts(lx - 16, ly - 34, lx + 16, ly - 4, 6), "#e2722e", blob(rect_pts(lx + 4, ly - 34, lx + 16, ly - 4), "#b6551e"), w=3.4,
                   seed=4703))
    bulb = ellipse_pts(lx, ly + 34, 26, 34, 16)
    o.append(shape(bulb, "#fff3c4" if on > .5 else "#e7e2d4", blob(ellipse_pts(lx - 8, ly + 24, 7, 12, 8), "#ffffff", .9), w=3, seed=4704))
    # клетка
    for k, dx in enumerate((-30, -14, 0, 14, 30)):
        bow = 1 - (dx / 34) ** 2
        o.append(line([(lx + dx * .5, ly - 4), (lx + dx * 1.05, ly + 30), (lx + dx * .5 * bow + dx * .2, ly + 74)], 3.2, "#3a3a40", seed=4710 + k,
                      taper=.1, wmin=.9))
    o.append(line([(lx - 32, ly + 28), (lx, ly + 34), (lx + 32, ly + 28)], 3, "#3a3a40", seed=4720, taper=.1, wmin=.9))
    o.append(line([(lx - 18, ly + 70), (lx, ly + 76), (lx + 18, ly + 70)], 3, "#3a3a40", seed=4721, taper=.1, wmin=.9))
    return "".join(o), (lx, ly + 34)


def pendant(t):
    """Повешенная лампа (s15): провод с потолка, абажур-конус мятный."""
    x, y = 360.0, proj(360, CY, .35)[1]
    o = [line([(x, y - 150), (x, y)], 4, "#2d2a2e", seed=4750, taper=.1, wmin=.9)]
    sh = [(x - 20, y, 1), (x + 20, y, 1), (x + 74, y + 70, 1), (x - 74, y + 70, 1)]
    o.append(shape(ellipse_pts(x, y + 70, 74, 14, 16), "#fff3c4", "", w=3, seed=4752))
    o.append(shape(sh, "#5fae9c", blob([(x + 4, y), (x + 20, y), (x + 74, y + 70), (x + 30, y + 70)], "#468c7c", .9), w=3.6, seed=4751))
    return "".join(o)


def outlet():
    x, y = OUTLET
    o = []
    if ST["outlet_new"]:
        o.append(shape(rect_pts(x - 34, y - 34, x + 34, y + 34, 8), "#f7f4ee", blob(rect_pts(x - 34, y + 18, x + 34, y + 34, 6), "#dcd6ca"), w=3.4,
                       seed=4800))
        o.append(shape(ellipse_pts(x, y, 22, 22, 16), "#ece7dd", "", w=2.6, seed=4801))
        o.append(blob(ellipse_pts(x - 8, y, 4, 5, 8), INK) + blob(ellipse_pts(x + 8, y, 4, 5, 8), INK))
        return "".join(o)
    o.append(shape(ellipse_pts(x, y, 30, 30, 16), "#6f675c", blob(ellipse_pts(x + 6, y + 6, 22, 22, 12), "#4f483f"), w=3, seed=4805))
    for k, (col, dx, dy) in enumerate([("#d8483c", 40, -40), ("#3b6fc4", 52, -6), ("#f2c23a", 34, 30)]):
        pts = [(x - 4 + k * 4, y), (x + dx * .5, y + dy * .4 - 12), (x + dx, y + dy)]
        o.append(line(pts, 7, INK, seed=4810 + k, taper=.05, wmin=.95))
        o.append(line(pts, 4, col, seed=4815 + k, taper=.05, wmin=.95))
        o.append(line([(x + dx, y + dy), (x + dx + 8, y + dy + 2)], 3, "#c98b3a", seed=4820 + k, taper=.1))
    return "".join(o)


def calendar(x, y, n_off, t, day0=3):
    """Отрывной календарь: подложка, блок листков; n_off — сколько листков уже сорвано (дробное — летит)."""
    o = []
    o.append(shape(rect_pts(x - 70, y - 100, x + 70, y + 110, 6), "#b5452f", blob(rect_pts(x - 70, y - 100, x + 70, y - 60), "#8f3322"), w=3.6,
                   seed=4900))
    o.append(line([(x, y - 112), (x, y - 100)], 4, "#5d5a58", seed=4901))
    k = int(n_off)
    num = day0 + k
    o.append(shape(rect_pts(x - 58, y - 54, x + 58, y + 98, 3), "#f7f3ea", blob(rect_pts(x - 58, y + 86, x + 58, y + 98), "#ddd5c4") +
                   blob(rect_pts(x - 58, y - 54, x + 58, y - 30), "#d8483c") +
                   f'<text x="{x}" y="{y + 64}" text-anchor="middle" font-family="IDB" font-weight="900" font-size="78" fill="#1c1622">{num}</text>',
                   w=3.4, seed=4902 + k))
    return "".join(o)


def flying_leaf(x, y, u, num, seed):
    """Сорванный листок: u 0..1 — путь (вверх-вбок, кувырок, вниз)."""
    if u <= 0 or u >= 1:
        return ""
    r = rs(seed)
    side = 1 if r.uniform() > .5 else -1
    dx = side * (120 + 160 * u) * u + r.uniform(-20, 20) * u
    dy = -140 * math.sin(math.pi * min(1, u * 1.6)) + 520 * u * u
    rot = side * (40 + 360 * u)
    sx = abs(math.cos(u * 7 + seed)) * .7 + .3
    inner = (blob(rect_pts(-58, -54, 58, -30), "#d8483c") +
             f'<text x="0" y="64" text-anchor="middle" font-family="IDB" font-weight="900" font-size="78" fill="#1c1622">{num}</text>')
    g = shape(rect_pts(-58, -54, 58, 98, 3), "#f7f3ea", inner, w=3.4, seed=4950 + seed)
    return f'<g transform="translate({x + dx:.1f} {y + dy:.1f}) rotate({rot:.1f}) scale({sx:.3f} 1)">{g}</g>'


# ═════════════════════════ пол: газеты, плёнка, предметы ═════════════════════════
def newspapers(off=0.0, x_lo=-500.0, x_hi=1700.0):
    """Газеты на полу (вид сверху в перспективе), сдвинуты на off по x (беговая дорожка). Повторяются с шагом."""
    o = []
    step = 420.0
    k0 = int(math.floor((x_lo - off) / step)) - 1
    k1 = int(math.ceil((x_hi - off) / step)) + 1
    for k in range(k0, k1):
        r = rs(5000 + (k % 7 + 7) % 7)
        cx = k * step + off + r.uniform(-30, 30)
        m0, m1 = .14 + r.uniform(0, .05), .34 + r.uniform(0, .06)
        w = 300 + r.uniform(-30, 40)
        sk = r.uniform(-25, 25)
        pts = [_fl(cx - w / 2 + sk, m0), _fl(cx + w / 2 + sk, m0 + .01), _fl(cx + w / 2 - sk, m1), _fl(cx - w / 2 - sk, m1 - .01)]
        inner = ""
        for j in range(5):
            mm = m0 + (m1 - m0) * (.18 + j * .15)
            a = _fl(cx - w * .4, mm)
            b = _fl(cx + w * (.05 if j == 0 else .38), mm)
            inner += line([a, b], 5 if j == 0 else 2.6, "#8f8a80", seed=5010 + j, op=.7, taper=.1, wmin=.8)
        inner += blob([_fl(cx + w * .1, m0 + .03), _fl(cx + w * .4, m0 + .03), _fl(cx + w * .4, m0 + .09), _fl(cx + w * .1, m0 + .09)], "#b9b2a4", .8)
        inner += blob([_fl(cx - w * .2, m1 - .06), _fl(cx + w * .1, m1 - .07), _fl(cx, m1 - .03)], MINT, .9)   # капли краски
        o.append(shape([(p[0], p[1], 1) for p in pts], "#ece6d6", inner, w=3, seed=5000 + k * 3))
    return "".join(o)


def _fl(x, m):
    """Точка пола: x на линии стены, глубина m."""
    return proj(x, FY, m)


def film(off=0.0, x_lo=-500.0, x_hi=1700.0, m0=.08, m1=.6):
    """Прозрачная плёнка поверх газет: бледная заливка + блики и складки (едут с off)."""
    poly = [_fl(x_lo, m0), _fl(x_hi, m0), _fl(x_hi, m1), _fl(x_lo, m1)]
    o = [blob([p + (1,) for p in poly], "#e6f3f8", .28)]
    step = 260.0
    k0 = int(math.floor((x_lo - off) / step)) - 1
    k1 = int(math.ceil((x_hi - off) / step)) + 1
    for k in range(k0, k1):
        r = rs(5100 + (k % 5 + 5) % 5)
        x = k * step + off
        a = _fl(x + r.uniform(-20, 20), m0 + .03)
        b = _fl(x + 60 + r.uniform(-30, 30), (m0 + m1) / 2)
        c = _fl(x + 20 + r.uniform(-30, 30), m1 - .03)
        o.append(line([a, b, c], 4.4, "#ffffff", seed=5110 + k % 9, op=.75, taper=.5, wmin=.2))
        d = _fl(x + 130, m0 + .1)
        e = _fl(x + 210, m0 + .2)
        o.append(line([d, e], 3, "#ffffff", seed=5120 + k % 9, op=.6, taper=.5, wmin=.2))
        o.append(line([_fl(x + 90, m1 - .12), _fl(x + 150, m1 - .05)], 2.6, "#9fb7c2", seed=5130 + k % 9, op=.5, taper=.5, wmin=.2))
    # передний край плёнки — мятая кромка
    edge = [_fl(x_lo + (x_hi - x_lo) * u, m1 + .01 * math.sin(u * 40 + off * .02)) for u in np.linspace(0, 1, 40)]
    o.append(line(edge, 3, "#9fb7c2", seed=5140, op=.8, taper=.05, wmin=.9))
    return "".join(o)


def paint_can(x, y, k=1.0, roller_in=False):
    """Банка краски белая с мятным потёком (y — низ)."""
    w, h = 74 * k, 96 * k
    o = [blob(ellipse_pts(x + 10 * k, y + 4 * k, w * 1.1, 14 * k, 14), "#2a1c10", .25)]
    body = [(x - w, y - h, 1), (x + w, y - h, 1), (x + w, y - 8 * k), (x, y + 6 * k), (x - w, y - 8 * k)]
    inner = blob([(x + w * .45, y - h), (x + w, y - h), (x + w, y), (x + w * .45, y)], "#d9d4c8", .9)
    inner += blob([(x - w * .5, y - h * .7), (x + w * .2, y - h * .7), (x + w * .2, y - h * .3), (x - w * .5, y - h * .3)], "#7fc4ad")
    inner += blob([(x - w * .2, y - h), (x - w * .05, y - h), (x - w * .06, y - h * .55), (x - w * .12, y - h * .5), (x - w * .2, y - h * .62)], MINT)
    o.append(shape(body, "#f7f5f0", inner, w=4, seed=5200))
    o.append(shape(ellipse_pts(x, y - h, w, 16 * k, 18), "#cfc9bd", blob(ellipse_pts(x, y - h + 2 * k, w * .86, 12 * k, 16), MINT), w=3.6, seed=5201))
    o.append(line([(x - w, y - h), (x - w * .6, y - h - 60 * k), (x + w * .6, y - h - 60 * k), (x + w, y - h)], 3.4, "#7b7770", seed=5202, taper=.1,
                  wmin=.9))
    return "".join(o)


def tile_boxes(x, y, k=1.0):
    o = [blob(ellipse_pts(x + 90 * k, y + 6, 190 * k, 18 * k, 14), "#2a1c10", .25)]
    for j, (dx, dy, w, h) in enumerate([(0, 0, 220, 90), (20, -90, 180, 80), (-10, -170, 200, 70)]):
        x0, y1 = x + dx * k, y + dy * k
        x1, y0 = x0 + w * k, y1 - h * k
        top = [(x0, y0, 1), (x1, y0, 1), (x1 + 26 * k, y0 - 16 * k, 1), (x0 + 26 * k, y0 - 16 * k, 1)]
        side = [(x1, y0, 1), (x1 + 26 * k, y0 - 16 * k, 1), (x1 + 26 * k, y1 - 16 * k, 1), (x1, y1, 1)]
        inner = blob(rect_pts(x0 + 20 * k, y0 + 18 * k, x0 + 90 * k, y0 + 44 * k), "#f2ead6", .9)
        inner += "".join(blob(rect_pts(x0 + 104 * k + q * 22 * k, y0 + 20 * k, x0 + 120 * k + q * 22 * k, y0 + 36 * k), "#5f9ec0") for q in range(3))
        o.append(shape(side, "#a8743c", "", w=3.4, seed=5300 + j * 3))
        o.append(shape(rect_pts(x0, y0, x1, y1), "#c58c4a", inner, w=3.6, seed=5301 + j * 3))
        o.append(shape(top, "#d9a764", line([((x0 + x1) / 2, y0), ((x0 + x1) / 2 + 26 * k, y0 - 16 * k)], 6, "#bfa67a", seed=5302 + j * 3, op=.8),
                       w=3.4, seed=5303 + j * 3))
    return "".join(o)


def bags(x, y, k=1.0):
    o = [blob(ellipse_pts(x + 40 * k, y + 6, 170 * k, 18 * k, 14), "#2a1c10", .25)]
    for j, (dx, dy, rot) in enumerate([(0, 0, -4), (110, -10, 6), (40, -80, -2)]):
        cx, cy = x + dx * k, y + dy * k
        pts = [(cx - 80 * k, cy - 4 * k), (cx - 70 * k, cy - 70 * k), (cx - 30 * k, cy - 84 * k), (cx + 40 * k, cy - 82 * k), (cx + 80 * k, cy - 64 * k),
               (cx + 84 * k, cy - 6 * k), (cx + 30 * k, cy + 4 * k), (cx - 40 * k, cy + 4 * k)]
        inner = blob([(cx + 20 * k, cy - 84 * k), (cx + 84 * k, cy - 64 * k), (cx + 84 * k, cy + 4 * k), (cx + 20 * k, cy + 4 * k)], "#b9ab90", .9)
        inner += blob(rect_pts(cx - 40 * k, cy - 56 * k, cx + 20 * k, cy - 26 * k), "#e1d6bf", .9)
        inner += line([(cx - 34 * k, cy - 42 * k), (cx + 12 * k, cy - 42 * k)], 3, "#8b7d64", seed=5410 + j, op=.8)
        o.append(f'<g transform="rotate({rot} {cx:.1f} {cy:.1f})">' + shape(pts, "#d6c7a8", inner, w=3.6, seed=5400 + j) + "</g>")
    return "".join(o)


def ladder(x, y, k=1.0, front=False):
    """Стремянка серебристая (вид сбоку-спереди): две пары ног, ступени. front=False — дальние ноги, True — ближние со ступенями."""
    h = 640 * k
    top = (x, y - h)
    o = []
    if not front:
        o.append(blob(ellipse_pts(x, y + 4, 200 * k, 16 * k, 14), "#2a1c10", .22))
        for dx in (150,):
            o.append(line([(top[0] + 10, top[1] + 10), (x + dx * k, y)], 22 * k, INK, seed=5500, taper=.02, wmin=.95))
            o.append(line([(top[0] + 10, top[1] + 10), (x + dx * k, y)], 13 * k, "#a9b2bb", seed=5501, taper=.02, wmin=.95))
        o.append(line([(x + 40 * k, y - h * .55), (x + 120 * k, y - h * .2)], 8 * k, "#7d858e", seed=5502, taper=.05, wmin=.9))
        return "".join(o)
    # ближняя пара ног и ступени
    lx0, lx1 = x - 150 * k, x - 40 * k
    for j in range(4):
        u = (j + 1) / 5
        a = (top[0] - 30 * k + (lx0 - top[0] + 30 * k) * u, top[1] + h * u)
        b = (top[0] + 30 * k + (lx1 - top[0] - 30 * k) * u, top[1] + h * u)
        st = [(a[0] - 6, a[1] - 14 * k, 1), (b[0] + 6, b[1] - 14 * k, 1), (b[0] + 6, b[1] + 8 * k, 1), (a[0] - 6, a[1] + 8 * k, 1)]
        o.append(shape(st, "#c3cbd3", blob([(a[0], a[1]), (b[0], b[1]), (b[0], b[1] + 8 * k), (a[0], a[1] + 8 * k)], "#8f98a2"), w=3.4, seed=5510 + j))
    for j, (p0, p1) in enumerate([((top[0] - 30 * k, top[1]), (lx0, y)), ((top[0] + 30 * k, top[1]), (lx1, y))]):
        o.append(shape(lib.band([p0, p1], 26 * k, 26 * k, step=8, cap=False), "#b8c1ca",
                       blob(lib.band([(p0[0] + 6, p0[1]), (p1[0] + 6, p1[1])], 8 * k, 8 * k, step=8, cap=False), "#e6ecf1", .9), w=3.6, seed=5520 + j))
        o.append(shape(rect_pts(p1[0] - 18 * k, y - 18 * k, p1[0] + 18 * k, y, 4), "#2d2a2e", "", w=3, seed=5525 + j))
    # верхняя площадка
    o.append(shape(rect_pts(top[0] - 70 * k, top[1] - 22 * k, top[0] + 70 * k, top[1] + 6 * k, 6), "#c3cbd3",
                   blob(rect_pts(top[0] - 70 * k, top[1] - 4 * k, top[0] + 70 * k, top[1] + 6 * k), "#8f98a2"), w=3.6, seed=5530))
    return "".join(o)


def ladder_step_y(x, y, k, j):
    """y верха ступени j (0..3) ближней пары."""
    h = 640 * k
    return y - h + h * (j + 1) / 5 - 14 * k


def light(t, lamp_pos, on, mode):
    """Свет: вечер — тёплое пятно от лампы (screen) и синее затемнение по краям; без лампы — синие сумерки; день — луч."""
    o = []
    if mode == "day":
        g = lib.lin_grad([(0, "#fff6d8", .55), (1, "#fff6d8", 0)], 0, 0, 1, .5)
        x0, y0, x1, y1 = WIN
        beam = [(x0, y0), (x1, y0), (x1 - 300, FY + 500), (x0 - 700, FY + 400)]
        o.append(f'<path d="{lib.fill_d([p + (1,) for p in beam])}" fill="url(#{g})" style="mix-blend-mode:screen" {lib.blur(30)}/>')
        return "".join(o)
    dark = 1 - .55 * on
    o.append(f'<rect x="-2000" y="-2000" width="5200" height="6000" fill="#26306a" opacity="{.42 * dark:.3f}" style="mix-blend-mode:multiply"/>')
    if on > 0:
        lx, ly = lamp_pos
        fl = 1 + .02 * math.sin(t * 9.1) + .015 * math.sin(t * 17)
        g = lib.rad_grad([(0, "#ffe2a0", .7 * on * fl), (.35, "#ffc070", .3 * on), (1, "#ffb060", 0)], lx, ly, 900, 820)
        o.append(f'<rect x="-2000" y="-2000" width="5200" height="6000" fill="url(#{g})" style="mix-blend-mode:screen"/>')
        g2 = lib.rad_grad([(0, "#fffbe8", .9 * on), (.3, "#ffe7a8", .5 * on), (1, "#ffe7a8", 0)], lx, ly, 90)
        o.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="90" fill="url(#{g2})" style="mix-blend-mode:screen"/>')
    return "".join(o)
