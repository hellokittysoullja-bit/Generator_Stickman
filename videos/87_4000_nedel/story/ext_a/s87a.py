"""Рилс 87 «4000 недель» — все клипы. frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (W(i)); числа в коде — длительности движений.
Бег хука — движок рилсов 82/85 (base85.py: план шагов, камера, влёт правил 28–29, заголовок big_title).
Сетка жизни — 80 строк (годы) × 52 клетки (недели), клетки — SVG-паттерны (тысячи клеток без тысяч узлов).
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — рисунок хука белым на чёрном (замер заполнения)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from base85 import *  # noqa: E402,F401,F403
from base85 import SH, PE, dima, lib, INK, W, WE, T0, T1, NOCAM, MASK, WALL, FLOOR, PIV, _CUR  # noqa: E402

GRID_BG = "#d6c6a2"      # линии сетки
EMPTY = "#fffaf0"        # пустая неделя
GONE = "#6b6660"         # прошедшая (погасла)
LIVED = "#3f6fd1"        # закрашено фломастером
LIVED_L = "#9db8ee"
WARM = "#ffbe3d"         # неделя с важным делом
WARM_L = "#ffe39a"
SKIN, SKIN_SH = "#f0c9a6", "#d9a883"
ROWS, COLS = SH["grid"]["rows"], SH["grid"]["cols"]
LIVED_N = SH["grid"]["lived_weeks"]
CC = 30.0                # клетка мира хука


# ═════════════════════════ клетки ═════════════════════════
def pat(c, fill, bg=GRID_BG, gap=.14, x0=0.0, y0=0.0, scrib=None):
    """Паттерн клетки c×c: заливка fill, просвет-линия bg; scrib — цвет штриховки фломастером поверх."""
    pid = lib.uid("pt")
    g = c * gap / 2
    inner = f'<rect width="{c:.3f}" height="{c:.3f}" fill="{bg}"/><rect x="{g:.3f}" y="{g:.3f}" width="{c - 2 * g:.3f}" height="{c - 2 * g:.3f}" fill="{fill}"/>'
    if scrib:
        z = scrib_pts(0, 0, c)
        inner += (f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in z)}" fill="none" stroke="{scrib}" '
                  f'stroke-width="{c * .2:.2f}" stroke-linejoin="round" stroke-linecap="round"/>')
    lib.DEFS.append(f'<pattern id="{pid}" x="{x0:.3f}" y="{y0:.3f}" width="{c:.3f}" height="{c:.3f}" patternUnits="userSpaceOnUse">{inner}</pattern>')
    return pid


def scrib_pts(x, y, c, n=4):
    """Зигзаг штриховки клетки (x, y) — левый верх."""
    m = c * .2
    out = []
    for i in range(n + 1):
        yy = y + m + (c - 2 * m) * i / n
        out += [(x + m, yy), (x + c - m, yy + (c - 2 * m) / n * .5)]
    return out


def scrib_cell(x, y, c, p=1.0, col=LIVED, bg=LIVED_L):
    """Одна клетка, закрашиваемая на глазах: p 0…1 — сколько зигзага уже нарисовано."""
    if p <= 0:
        return ""
    g = c * .07
    pts = scrib_pts(x, y, c)
    n = max(2, int(math.ceil(len(pts) * p)))
    pts = pts[:n]
    return (f'<rect x="{x + g:.1f}" y="{y + g:.1f}" width="{c - 2 * g:.1f}" height="{c - 2 * g:.1f}" fill="{bg}" opacity="{min(1, p * 2):.2f}"/>'
            f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{col}" stroke-width="{c * .2:.1f}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def rect_pat(x, y, w, h, pid, op=1.0):
    if w <= 0 or h <= 0:
        return ""
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="url(#{pid})" opacity="{op:.3f}"/>'


def life_grid(x0, y0, c, cols, rows, n, scrib=True, empty=EMPTY, bg=GRID_BG):
    """Сетка cols×rows с левого верха (x0, y0): первые n клеток (по строкам) закрашены синим."""
    pe = pat(c, empty, bg=bg, x0=x0, y0=y0)
    pl = pat(c, LIVED_L, x0=x0, y0=y0, scrib=LIVED if scrib else None)
    o = [rect_pat(x0, y0, cols * c, rows * c, pe)]
    n = max(0, min(n, cols * rows))
    full, rem = int(n // cols), int(n % cols)
    o.append(rect_pat(x0, y0, cols * c, full * c, pl))
    o.append(rect_pat(x0, y0 + full * c, rem * c, c, pl))
    return "".join(o)


def cell_xy(x0, y0, c, idx, cols):
    return x0 + (idx % cols) * c, y0 + (idx // cols) * c


# ═════════════════════════ значки в клетках (без букв) ═════════════════════════
def icon(kind, cx, cy, s, rot=0.0):
    """Крошечный значок дела в клетке: центр (cx, cy), размер s (≈ сторона клетки)."""
    k = s / 100
    if kind == "book":
        b = (shape(lib.rrect(-34, -40, 34, 40, 6), "#3d74c6", line([(-22, -40), (-22, 40)], 4, "#24497f") , w=4.2, seed=511)
             + f'<rect x="-12" y="-24" width="36" height="8" rx="3" fill="#ffffff" opacity=".8"/>')
    elif kind == "bag":
        b = (shape(lib.rrect(-34, -30, 34, 42, 16), "#4fa86a", shape(lib.rrect(-20, 6, 20, 32, 8), "#3c8a55", "", w=3, seed=513), w=4.2, seed=512)
             + line([(-16, -30), (-12, -46), (12, -46), (16, -30)], 5, INK, seed=514))
    elif kind == "friends":
        b = ""
        for dx, col in ((-20, "#e8765a"), (22, "#f2b84a")):
            b += shape(ellipse_pts(dx, 22, 22, 24, 14), col, "", w=3.6, seed=520 + dx)
            b += shape(ellipse_pts(dx, -18, 15, 15, 12), SKIN, f'<circle cx="{dx - 5}" cy="-20" r="2.6" fill="{INK}"/><circle cx="{dx + 5}" cy="-20" r="2.6" fill="{INK}"/>', w=3.4, seed=530 + dx)
    elif kind == "sea":
        b = (f'<circle cx="18" cy="-22" r="16" fill="#ffc93d" stroke="{INK}" stroke-width="3"/>'
             + shape([(-42, 0), (42, 0), (42, 40), (-42, 40)], "#5fb0e6", "", w=3.4, seed=541)
             + line([(-38, 6), (-24, -2), (-10, 6), (4, -2), (18, 6), (34, -2)], 4, "#2f78b8", seed=542))
    elif kind == "star":
        pts = [(46 * math.cos(-math.pi / 2 + i * math.pi / 5) * (1 if i % 2 == 0 else .45),
                46 * math.sin(-math.pi / 2 + i * math.pi / 5) * (1 if i % 2 == 0 else .45)) for i in range(10)]
        b = shape(pts, "#ffb02e", "", w=4.0, seed=551)
    elif kind == "paw":
        b = (shape(ellipse_pts(0, 14, 26, 21, 14), "#7a4a2a", "", w=0, seed=561, ink=False)
             + "".join(shape(ellipse_pts(dx, dy, 10, 12, 10), "#7a4a2a", "", w=0, seed=562 + i, ink=False)
                       for i, (dx, dy) in enumerate(((-27, -14), (-10, -28), (10, -28), (27, -14)))))
    else:
        b = ""
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.1f}) scale({k:.3f})">{b}</g>'


def pop(t, t0, d=.28):
    """Выскакивание значка: 0 до t0, перелёт и успокоение."""
    if t < t0:
        return 0.0
    return lib.back_out(clamp((t - t0) / d), 2.4)


# ═════════════════════════ предметы ═════════════════════════
def marker(x, y, ang, k=1.0, cap=True):
    """Фломастер: (x, y) — кончик, ang — направление от кончика к хвосту (градусы)."""
    b = (shape(lib.rrect(18, -15, 150, 15, 10), "#2f4f9a", f'<rect x="96" y="-15" width="10" height="30" fill="#ffffff" opacity=".7"/>', w=3.6, seed=601)
         + shape([(0, -4), (20, -12), (20, 12), (0, 4)], LIVED, "", w=3.0, seed=602))
    if cap:
        b += shape(lib.rrect(140, -18, 186, 18, 12), "#2f4f9a", "", w=3.4, seed=603)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({k:.3f})">{b}</g>'


def fist(x, y, k=1.0, rot=0.0, sleeve="#e8765a"):
    """Кулак с фломастером в кадре крупно: рукав уходит за край вниз-вправо."""
    b = (shape(lib.rrect(30, 20, 360, 120, 40), sleeve, line([(60, 30), (60, 112)], 3, lib.mul(sleeve, (.8, .8, .8)), seed=611), w=4.4, seed=612)
         + shape(ellipse_pts(0, 40, 70, 58, 18), SKIN, line([(-40, 14), (-10, 6)], 3, SKIN_SH, seed=613) + line([(-46, 40), (-12, 34)], 3, SKIN_SH, seed=614), w=4.2, seed=615))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">{b}</g>'


def book(x, y, k, rot=0.0, lit=0, tilt=1.0):
    """Книга обложкой к зрителю: на обложке сетка 6×8 клеточек (без букв), lit — сколько клеток уже зажглось тёплым."""
    o = [shape(lib.rrect(-150, -200, 150, 200, 10), "#2f6a58", line([(-126, -200), (-126, 200)], 4, "#1f4a3d", seed=621), w=5.0, seed=622)]
    c = 30
    x0, y0 = -100, -150
    for i in range(48):
        cx, cy = x0 + (i % 6) * (c + 7), y0 + (i // 6) * (c + 7)
        col = WARM if i < lit else "#e9f2ec"
        o.append(f'<rect x="{cx}" y="{cy}" width="{c}" height="{c}" rx="4" fill="{col}" opacity="{1 if i < lit else .85}"/>')
    o.append(f'<rect x="146" y="-196" width="16" height="392" fill="#f4efe2" stroke="{INK}" stroke-width="3"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k * tilt:.3f} {k:.3f})">{"".join(o)}</g>'


def tube(x, y, k, rot=0.0, L=340.0):
    """Плакат, свёрнутый в трубку, перевязан лентой."""
    o = [shape(lib.rrect(-L / 2, -40, L / 2, 40, 40), "#fffaf0", line([(-L / 2 + 30, -10), (L / 2 - 30, -14)], 3, GRID_BG, seed=631)
               + line([(-L / 2 + 30, 14), (L / 2 - 30, 12)], 3, GRID_BG, seed=632), w=4.4, seed=633),
         f'<ellipse cx="{L / 2 - 6}" cy="0" rx="16" ry="38" fill="#f0e6cf" stroke="{INK}" stroke-width="3.5"/>',
         f'<path d="M{L / 2 - 14} -20 Q{L / 2 - 2} 0 {L / 2 - 14} 20" fill="none" stroke="{GRID_BG}" stroke-width="3"/>',
         f'<rect x="-14" y="-42" width="28" height="84" fill="{WARM}" stroke="{INK}" stroke-width="3"/>',
         line([(0, 40), (-24, 78)], 6, WARM, seed=634) + line([(0, 40), (22, 80)], 6, WARM, seed=635)]
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">{"".join(o)}</g>'


def poster(x0, y0, w, h, n, roll=1.0, lit=(), scrib=True, ticks=True):
    """Плакат «жизнь в неделях»: лист w×h, сетка 52×80, n закрашенных; roll 0…1 — какая доля листа развёрнута сверху
    (низ — трубка). lit — индексы клеток, горящих тёплым."""
    c = min((w - 70) / COLS, (h - 110) / ROWS)
    gx = x0 + 48 + (w - 70 - COLS * c) / 2
    gy = y0 + 80
    hv = max(40.0, h * roll)
    cl = lib.clip_rect(x0 - 10, y0 - 10, w + 20, hv + 10)
    o = [f'<rect x="{x0 + 14}" y="{y0 + 18}" width="{w}" height="{hv}" fill="#000" opacity=".12"/>',
         f'<g clip-path="url(#{cl})">',
         shape(lib.rrect(x0, y0, x0 + w, y0 + h, 6), "#fffdf7", "", w=4.0, seed=641),
         f'<rect x="{x0 + w * .22}" y="{y0 + 26}" width="{w * .56}" height="24" rx="12" fill="{INK}" opacity=".78"/>',
         life_grid(gx, gy, c, COLS, ROWS, n, scrib, bg="#a8966e")]
    for i in lit:
        cx, cy = cell_xy(gx, gy, c, i, COLS)
        o.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{c:.1f}" height="{c:.1f}" fill="{WARM}"/>')
    if ticks:
        for r in range(0, ROWS + 1, 5):
            yy = gy + r * c
            o.append(f'<rect x="{gx - 26}" y="{yy - 2:.1f}" width="{16 if r % 10 == 0 else 10}" height="4" fill="{INK}" opacity=".6"/>')
    o.append("</g>")
    if roll < .999:
        yb = y0 + hv
        o.append(shape(lib.rrect(x0 - 8, yb - 30, x0 + w + 8, yb + 30, 30), "#f7f0de", line([(x0 + 20, yb - 6), (x0 + w - 20, yb - 8)], 3, GRID_BG, seed=642), w=4.2, seed=643))
    o.append(f'<circle cx="{x0 + w / 2}" cy="{y0 + 12}" r="13" fill="#e8504a" stroke="{INK}" stroke-width="3"/>')
    return "".join(o), (gx, gy, c)


# ═════════════════════════ мир хука: бескрайняя сетка ═════════════════════════
def ensure_k(kind):
    if _CUR[0] == kind:
        return
    _CUR[0] = kind
    if kind == "hook":
        plan(dict(a=-0.4, b=T1("s03") + .6, x0=0.0, tc=0.2, st=0.55, step=190.0, leap=None, stumble=None))
    elif kind == "walk":
        plan(dict(a=T0("s18") - 1.5, b=T1("s18") + .5, x0=0.0, tc=0.46, st=0.62, step=150.0, walk=True))


def world_grid(hx, t, warm=False, span=(-2600.0, 1800.0, -2600.0, 1700.0)):
    """Сетка под всем экраном в мире бега: всё правее Димы живое, левее — погасло (или загорелось тёплым на петле)."""
    xa, xb, ya, yb = hx + span[0], hx + span[1], span[2], span[3]
    pe = pat(CC, EMPTY)
    o = [rect_pat(xa, ya, xb - xa, yb - ya, pe)]
    col_c = WARM if warm else GONE
    pg = pat(CC, col_c, bg=("#d99a2b" if warm else "#4f4b46"))
    edge = math.floor((hx - 110) / CC) * CC
    fade = 5
    o.append(rect_pat(xa, ya, edge - fade * CC - xa, yb - ya, pg))
    for j in range(fade):                       # колонки гаснут по одной за спиной
        x = edge - (j + 1) * CC
        op = clamp((j + 1 - ((hx - 110) - edge) / CC) / fade) ** .8
        o.append(rect_pat(x, ya, CC, yb - ya, pg, op))
    o.append(f'<rect x="{xa:.1f}" y="-3" width="{xb - xa:.1f}" height="6" fill="#6d5f45"/>')
    return "".join(o)


def step_flash(t, warm=False):
    """Под каждым шагом клетка вспыхивает и гаснет."""
    o = []
    for c in contacts(t - .35, t):
        u = (t - c[0]) / .35
        if 0 <= u <= 1:
            x = math.floor((c[2] + 20) / CC) * CC
            for dy, a in ((-CC, 1.0), (0.0, .8), (-2 * CC, .6), (-CC, .6)):
                o.append(f'<rect x="{x:.1f}" y="{dy:.1f}" width="{CC}" height="{CC}" fill="{WARM}" opacity="{a * (1 - u):.2f}"/>')
            r = 40 + 120 * u
            o.append(f'<circle cx="{x + CC / 2:.1f}" cy="0" r="{r:.1f}" fill="none" stroke="{WARM}" stroke-width="{8 * (1 - u):.1f}" opacity="{1 - u:.2f}"/>')
    return "".join(o)


def cat_hop(x, t, k=.42, per=.42, h=180.0, ph0=0.0, look=(-.6, -.1), walk=False):
    """Кот скачет: дуга прыжка, в полёте задние лапы вытянуты, на земле сжатие."""
    ph = ((t + ph0) / per) % 1.0
    if walk:
        st = dict(walk=(t * 2.2) % 1.0, look=look, tail=10 * math.sin(t * 5), perk=.6, smile=1.0)
        return PE.cat_svg(x, 0.0, k, st, t)
    air = math.sin(math.pi * ph)
    y = -h * air
    land = max(0.0, 1 - ph / .14) + max(0.0, (ph - .9) / .1)
    st = dict(legs=air, rot=-18 * math.cos(math.pi * ph), sy=1 - .14 * land, sx=1 + .1 * land, look=look,
              tail=25 * math.sin(t * 9), perk=1.0, ear=.4 * air, smile=1.0)
    return PE.cat_svg(x, y, k, st, t)


def run_world(t, s, sx, gy, follow, a, warm=False, cat_dx=330.0, cat_k=.42, walk=False):
    ensure_k("walk" if walk else "hook")
    cam = part_cam(t, a, s, sx, gy, follow)
    p = run_pose(t)
    if walk:
        p["expr"].update(look=(.6, .1), brows="calm", mouth="smile", smile=1.0, lid=.8)
    else:
        p["expr"].update(look=(.7, -.2) if (t // .4) % 2 == 0 else (.2, -.7), brows="up", mouth="gape", lid=1.0)
    dg, wr = dima.draw(p)
    hx = hip_at(t, bob=False)[0]
    g = world_grid(hx, t, warm) + step_flash(t, warm)
    ct = cat_hop(hx + cat_dx + 40 * math.sin(t * 3), t, k=cat_k, walk=walk)
    return cam, g, dg, ct


def hook_body(t, s, sx, gy, follow, a, mirror_=False, cat_dx=330.0, cat_k=.42):
    lib.DEFS.clear()
    cam, g, dg, ct = run_world(t, s, sx, gy, follow, a, cat_dx=cat_dx, cat_k=cat_k)
    if MASK:
        lib.DEFS.append(MASK_F)
        return '<rect width="1080" height="1920" fill="#000"/>' + f'<g filter="url(#mk85)"><g transform="{lib.cam(*cam)}">{g + dg + ct}</g></g>'
    inner = f'<g transform="{lib.cam(*cam)}">{g + ct + dg}</g>'
    if mirror_:
        inner = mirror(inner)
    return f'<rect width="1080" height="1920" fill="{EMPTY}"/>' + inner


def frame_s01(t):
    body = hook_body(t, 1.2, 330.0, 1430.0, .82, 0.0)
    if MASK or NOCAM:
        return lib.svg(body)
    return lib.svg(hook_wrap(body, t, W(SHOT["s01"]["hit_word"])) + title(t))


def frame_s02(t):
    a = T0("s02")
    body = hook_body(t, 1.55, 300.0, 1500.0, .9, a, mirror_=True, cat_dx=420.0, cat_k=.5)
    z = 1 + (0 if NOCAM else .08 * kick2(t, W(5)))
    r = 0 if NOCAM else 2.2 * kick2(t, W(5))
    return lib.svg(f'<g transform="translate(540 {PIV}) rotate({r:.2f}) scale({z:.4f}) translate(-540 {-PIV})">{body}</g>' + title(t))


def frame_s03(t):
    a = T0("s03")
    s = .44 * (1 + .12 * ease_out(clamp((t - a) / (T1("s03") - a))))
    body = hook_body(t, s, 540.0, 1180.0, 1.0, a, cat_dx=300.0)
    z = 1 + .1 * kick2(t, W(7))
    return lib.svg(f'<g transform="translate(540 1000) scale({z:.4f}) rotate({1.5 * kick2(t, W(7)):.2f}) translate(-540 -1000)">{body}</g>' + title(t))


# ═════════════════════════ возраст: ряды закрашиваются ═════════════════════════
def wall_grid(c, x0, y0, n, cols=30, rows=50):
    return life_grid(x0, y0, c, cols, rows, n)


def frame_s04(t):
    """«Если тебе двадцать пять»: Дима крупно у сетки, ряды над ним закрашиваются сверху."""
    lib.DEFS.clear()
    a = T0("s04")
    c = 46.0
    cols = 26
    u = clamp((t - W(10)) / (T1("s04") + .1 - W(10)))
    n = cols * 25 * .55 * ease_in(u, 1.6)
    o = [f'<rect x="-200" y="-300" width="1500" height="2600" fill="{EMPTY}"/>', wall_grid(c, -60, 80, n, cols, 46)]
    e = ex("wow82", look=(.1, -.8)) if t > W(11) else ex("puzzled82", look=(.2, -.5))
    f_ = dfig(560, 1640, 1.25, e, "d82_look_up" if t > W(9) else "d82_rest", t=t, head_add=.03 * math.sin((t - a) * 5))
    o.append(f_["svg"])
    dx, dy, r = drift(t, 1.4)
    z = 1.06 + .04 * (t - a) + .05 * kick2(t, W(11))
    return view("".join(o), 540 + dx, 960 + dy, z, r + 1.2 * kick2(t, W(11)), bg=EMPTY, over=title(t))


def frame_s05(t):
    """«Тысяча триста уже прошли»: вся сетка, заливка проносится до 25-го ряда; Дима внизу ахает."""
    lib.DEFS.clear()
    a = T0("s05")
    u = clamp((t - W(12) + .1) / (WE(14) - W(12) + .1))
    n = LIVED_N * ease_io(u)
    ps, (gx, gy, c) = poster(150, 160, 800, 1290, n)
    o = [wall_bg(1720.0), ps]
    k = min(n, LIVED_N - 1)
    fx, fy = cell_xy(gx, gy, c, int(k), COLS)
    if 0 < u < 1:                                   # фронт заливки — светится
        o.append(f'<circle cx="{fx + c / 2:.1f}" cy="{fy + c / 2:.1f}" r="{30 + 8 * math.sin(t * 30):.1f}" fill="{WARM}" opacity=".55"/>')
    if t > WE(14):
        q = clamp((t - WE(14)) / .3)
        o.append(f'<rect x="{gx - 6:.1f}" y="{gy + 25 * c - 3:.1f}" width="{COLS * c + 12:.1f}" height="6" fill="#e8504a" opacity="{q:.2f}"/>')
        o.append(burst(gx + COLS * c + 10, gy + 25 * c, 90, WE(14), t, "#e8504a", 8, .35))
    e = ex("wow82", look=(-.5, -.8)) if t > W(13) else ex("puzzled82", look=(-.4, -.7))
    f_ = dfig(880, 1690, .6, e, "d82_look_up", t=t)
    o.append(f_["svg"])
    dx, dy, r = drift(t, 1.0)
    z = 1.0 + .03 * (t - a) + .06 * kick2(t, W(13)) + .07 * kick2(t, W(15))
    return view("".join(o), 540 + dx, 930 + dy, z, r + 1.4 * kick2(t, W(15)), bg=WALL)


# ═════════════════════════ призыв: телефон и плакат ═════════════════════════
def frame_s06(t):
    lib.DEFS.clear()
    a = T0("s06")
    x0, y0, x1, y1 = PH
    ttap, tsend = W(17), W(19) + .45
    inner = [mini_room(x0 + 18, y0 + 18, x1 - x0 - 36, 360)]
    rows = [("#8fd16a", 300, 200), ("#e8a24a", 240, 330), ("#8a6fc4", 340, 180), ("#4a8fd8", 260, 280)]
    up = 120 * ease_out(clamp((t - tsend) / .3))
    ny = y0 + 470
    if t >= tsend:
        sc = ease_out(clamp((t - tsend) / .25))
        inner.append(f'<g transform="translate({x0 + 40} {ny + 50}) scale({sc:.3f}) translate({-(x0 + 40)} {-(ny + 50)})">'
                     + comment_row(x0 + 40, ny + 50, "#d4a23a", 230, 150, hl=1 - .5 * clamp((t - tsend - .4) / .6)) + "</g>")
    for i, (cc, n1, n2) in enumerate(rows):
        inner.append(comment_row(x0 + 40, ny + 50 + 120 * i + up, cc, n1, n2, seed=i))
    fy = y1 - 150
    act = t >= ttap
    inner.append(f'<rect x="{x0 + 18}" y="{fy - 40}" width="{x1 - x0 - 36}" height="190" fill="#eef1f6"/>')
    inner.append(f'<rect x="{x0 + 40}" y="{fy}" width="{x1 - x0 - 170}" height="76" rx="38" fill="#ffffff" stroke="{LIVED if act else "#b8c0cc"}" stroke-width="{5 if act else 3}"/>')
    if not act or t >= tsend:
        if int(t * 2.5) % 2 == 0:
            inner.append(f'<rect x="{x0 + 76}" y="{fy + 16}" width="6" height="44" rx="3" fill="{LIVED}"/>')
    else:
        for j in range(3):
            bob = 10 * max(0.0, math.sin((t - ttap) * 12 - j * .9))
            inner.append(f'<circle cx="{x0 + 90 + 36 * j}" cy="{fy + 38 - bob:.1f}" r="11" fill="{LIVED}"/>')
    sb = 1 + .25 * kick2(t, tsend)
    inner.append(f'<g transform="translate({x1 - 80} {fy + 38}) scale({sb:.3f})"><circle r="38" fill="{LIVED}" stroke="{INK}" stroke-width="3"/>'
                 '<path d="M-14 -16 L18 0 L-14 16 L-8 0Z" fill="#fff"/></g>')
    rest, fieldp, sendp = (x1 - 20, y1 - 330), (x0 + 260, fy + 40), (x1 - 80, fy + 40)
    if t < ttap:
        tp = np.array(rest) + (np.array(fieldp) - np.array(rest)) * ease_io(clamp((t - (ttap - .35)) / .35))
    elif t < tsend - .25:
        tp = np.array(fieldp) + np.array([0, 10 * kick2(t, ttap)]) + np.array([14 * math.sin((t - ttap) * 30), 0])
    else:
        tp = np.array(fieldp) + (np.array(sendp) - np.array(fieldp)) * ease_io(clamp((t - (tsend - .25)) / .25)) + np.array([0, 10 * kick2(t, tsend)])
    # плакат за телефоном справа: начинает сворачиваться снизу после отправки
    roll = 1 - .55 * ease_io(clamp((t - tsend) / .5))
    ps, _ = poster(0, 0, 330, 520, LIVED_N * .9, roll=roll, ticks=False)
    pst = f'<g transform="translate(760 1020) rotate(8)">{ps}</g>'
    body = pst + phone_body("".join(inner), t, rot=-3 + 1.2 * math.sin(t * 2), tap=tuple(tp))
    dx, dy, r = drift(t)
    z = .96 + .03 * (t - a) + .05 * kick2(t, tsend) + .04 * kick2(t, ttap)
    return view(body + burst(sendp[0], sendp[1], 110, tsend, t, LIVED, 10, .35), 540 + dx, 860 + dy, z, r, bg="#d9e8f2")


def frame_s07(t):
    """«Пришлю в личку»: трубка-плакат влетает в телефон, в личке бабл-картинка сетки."""
    lib.DEFS.clear()
    a = T0("s07")
    x0, y0, x1, y1 = PH
    tl = W(25)
    inner = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="140" fill="#eef1f6"/>',
             f'<circle cx="{x0 + 90}" cy="{y0 + 92}" r="34" fill="#f2a24a" stroke="{INK}" stroke-width="3"/>',
             f'<rect x="{x0 + 140}" y="{y0 + 76}" width="170" height="16" rx="8" fill="#9aa3b0"/>',
             f'<rect x="{x0 + 40}" y="{y0 + 200}" width="300" height="70" rx="30" fill="#e6e9ef"/>',
             f'<rect x="{x0 + 70}" y="{y0 + 226}" width="200" height="14" rx="7" fill="#b8c0cc"/>']
    if t >= tl:
        sc = lib.back_out(clamp((t - tl) / .3), 2.0)
        bx, by = x1 - 60, y0 + 330
        ps, _ = poster(0, 0, 300, 470, LIVED_N, ticks=False)
        bub = (f'<rect x="-330" y="-10" width="350" height="510" rx="34" fill="{LIVED}"/>'
               f'<g transform="translate(-315 10) scale(.98)">{ps}</g>')
        inner.append(f'<g transform="translate({bx} {by}) scale({sc:.3f})">{bub}</g>')
    body = phone_body("".join(inner), t, rot=2 - 1.0 * math.sin(t * 2))
    over = ""
    t0f, t1f = W(22) - .15, tl
    if t < t1f:                                   # трубка летит из-за правого края в чат
        u = clamp((t - t0f) / (t1f - t0f))
        if t < t0f:     # висит у края, качается
            x, y, rot, k = 880 + 20 * math.sin(t * 6), 420, -20 + 6 * math.sin(t * 5), 1.2
        else:
            e = ease_in(u, 1.6)
            x, y = 880 + (650 - 880) * e, 420 + (700 - 420) * e - 160 * math.sin(math.pi * u)
            rot, k = -20 + 340 * e, 1.2 - .7 * e
        over += tube(x, y, k, rot)
    over += burst(650, 700, 140, tl, t, WARM, 12, .4)
    dx, dy, r = drift(t)
    z = 1.0 + .03 * (t - a) + .06 * kick2(t, tl)
    return view(body + over, 540 + dx, 900 + dy, z, r, bg="#e3eef0")


# ═════════════════════════ плакат на стене ═════════════════════════
def frame_s08(t):
    """Трубка разворачивается на стене сверху вниз; на «Смотри» входит Дима с фломастером."""
    lib.DEFS.clear()
    a = T0("s08")
    roll = ease_out(clamp((t - a - .05) / .9), 2.5)
    ps, _ = poster(330, 170, 660, 1150, 0, roll=roll)
    o = [wall_bg(1690.0), ps]
    tw = W(31) - .3
    xs, xe = -260.0, 300.0
    if t > tw:
        tt = W(34) + .15
        if t < tt:
            ph = (t - tw) / .55
            x = xs + (xe - xs) * ease_out(clamp((t - tw) / (tt - tw)), 1.5)
            f_ = PE.dima82_walk(x, 1540, .8, ph % 1.0, t=t, expr="look82", mug=False)
        else:
            f_ = dfig(xe, 1540, .8, ex("sure82", look=(.6, -.3)), "d82_rest", t=t, head_add=.04 * math.sin((t - tt) * 4))
        o.append(f_["svg"])
        wx, wy = f_["wrist"]["n"]
        o.append(marker(wx + 10, wy + 18, 100, .7))
    dx, dy, r = drift(t, 1.0)
    z = 1.0 + .025 * (t - a) + .05 * kick2(t, W(26)) + .04 * kick2(t, W(31))
    return view("".join(o), 560 + dx, 930 + dy, z, r, bg=WALL)


def frame_s09(t):
    """«Каждая клетка — одна неделя»: камера ныряет в одну клетку, в ней семь точек-дней."""
    lib.DEFS.clear()
    a = T0("s09")
    c = 60.0
    o = [f'<rect x="-3000" y="-3000" width="7000" height="7000" fill="{EMPTY}"/>', life_grid(-1200, -1500, c, 60, 60, 60 * 24)]
    tx, ty = -1200 + 32 * c, -1500 + 28 * c          # клетка-неделя (пустая, ниже прожитых)
    hl = clamp((t - W(36)) / .2)
    o.append(f'<rect x="{tx - 4}" y="{ty - 4}" width="{c + 8}" height="{c + 8}" fill="none" stroke="{WARM}" stroke-width="{4 + 3 * kick2(t, W(39))}" opacity="{hl:.2f}"/>')
    for d in range(7):                                # семь дней загораются по одному на «одна неделя»
        td = W(38) + d * .09
        if t > td:
            sc = pop(t, td, .2)
            cx, cy = tx + c * (.2 + .6 * (d % 4) / 3), ty + c * (.33 if d < 4 else .7)
            if d >= 4:
                cx = tx + c * (.3 + .4 * (d - 4) / 2)
            o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{3.6 * sc:.2f}" fill="{LIVED}"/>')
    u = ease_io(clamp((t - a - .05) / 1.1))
    s = 1.0 * (11.0 ** u)
    cx = 540 * (1 - u) + (tx + c / 2) * u
    cy = 960 * (1 - u) + (ty + c / 2) * u
    if u < .01:
        cx, cy = tx + c / 2 - 200, ty + c / 2 - 300
    else:
        cx = (tx + c / 2 - 200) * (1 - u) + (tx + c / 2) * u
        cy = (ty + c / 2 - 300) * (1 - u) + (ty + c / 2) * u
    s *= 1 + .05 * kick2(t, W(39))
    r = 3 * (1 - u) + .6 * math.sin(t * 2)
    return view("".join(o), cx, cy, s, r, bg=EMPTY)


def frame_s10(t):
    """«Прожитые ты закрашиваешь»: рука с фломастером штрихует клетки одну за другой."""
    lib.DEFS.clear()
    a = T0("s10")
    c = 150.0
    x0, y0 = -60.0, 120.0
    cols = 8
    base = cols * 3
    o = [f'<rect x="-400" y="-400" width="1900" height="2800" fill="{EMPTY}"/>', life_grid(x0, y0, c, cols, 12, base)]
    ts = W(41) - .25
    per = .2
    k = 0
    tip = None
    while True:
        tc = ts + k * per
        if t < tc or k > 20:
            break
        p = clamp((t - tc) / per)
        cx, cy = cell_xy(x0, y0, c, base + k, cols)
        o.append(scrib_cell(cx, cy, c, p))
        if p < 1 or t < tc + per:
            pts = scrib_pts(cx, cy, c)
            tip = pts[min(len(pts) - 1, int(len(pts) * p))]
        k += 1
    if tip is None:
        cx, cy = cell_xy(x0, y0, c, base, cols)
        tip = (cx + c * .5 - 80 * (1 - clamp((t - a) / .3)), cy + c * .3 + 200 * (1 - clamp((t - a) / .3)))
    bob = 6 * math.sin(t * 40)
    o.append(fist(tip[0] + 120, tip[1] + 110 + bob, 1.1, 40) + marker(tip[0], tip[1] + bob, 40, 1.1, cap=False))
    dx, dy, r = drift(t, 1.2)
    camx = 540 + 0.5 * (tip[0] - 540)
    return view("".join(o), camx + dx, 1000 + dy, 1.0 + .05 * kick2(t, W(43)), r + 1.2 * kick2(t, W(43)), bg=EMPTY)


def frame_s11(t):
    """Дима закрашивает ряд и на «замер» застывает."""
    lib.DEFS.clear()
    a = T0("s11")
    c = 52.0
    gx, gy = 470.0, 380.0
    cols, rows = 16, 30
    row = 14
    base = cols * row
    fr = W(48)
    per = .19
    nk = min(9.0, max(0.0, (min(t, fr) - a + .2) / per))
    o = [wall_bg(1760.0, x0=-600, x1=1800), f'<rect x="{gx - 20}" y="{gy - 20}" width="{cols * c + 40}" height="{rows * c + 40}" fill="#fffdf7" stroke="{INK}" stroke-width="4"/>',
         life_grid(gx, gy, c, cols, rows, base)]
    kk = int(nk)
    for j in range(kk + 1):
        cx, cy = cell_xy(gx, gy, c, base + j, cols)
        o.append(scrib_cell(cx, cy, c, 1.0 if j < kk else nk - kk))
    cx, cy = cell_xy(gx, gy, c, base + kk, cols)
    pts = scrib_pts(cx, cy, c)
    tip = pts[min(len(pts) - 1, int(len(pts) * (nk - kk)))]
    if t > fr:
        tip = (tip[0] + 14 * ease_out(clamp((t - fr) / .2)), tip[1] + 30 * ease_out(clamp((t - fr) / .2)))
    e = ex("wow82", look=(.5, -.1)) if t > fr else ex("focus", look=(.8, -.1))
    f_ = dfig(330, 1560, 1.05, e, "d82_rest", t=t, arms={"n": ("ik", (tip[0] + 30, tip[1] + 40), -1)}, hands={"n": dict(PE._GRIP)},
              head_add=(-.06 * kick2(t, fr)) + .02 * math.sin(t * 6) * (t < fr))
    o.append(f_["svg"])
    wx, wy = f_["wrist"]["n"]
    ang = math.degrees(math.atan2(wy - tip[1], wx - tip[0]))
    o.append(marker(tip[0], tip[1], ang, .75))
    if t > fr:
        for i in range(3):
            q = clamp((t - fr - .05 * i) / .3)
            if 0 < q < 1:
                o.append(line([(220 + 30 * i, 880 - 60 * i), (180 + 30 * i - 40 * q, 840 - 60 * i - 40 * q)], 7, INK, seed=700 + i, op=1 - q))
    dx, dy, r = drift(t, 1.0 if t < fr else .2)
    z = 1.1 + .03 * (t - a) + .07 * kick2(t, fr)
    return view("".join(o), 640 + dx, 1050 + dy, z, r + 1.6 * kick2(t, fr), bg=WALL)


def frame_s12(t):
    """«Пустых меньше, чем думал»: отъезд, сетка видна вся, Дима мал рядом."""
    lib.DEFS.clear()
    a = T0("s12")
    ps, (gx, gy, c) = poster(230, 150, 790, 1380, LIVED_N + 140)
    o = [wall_bg(1700.0, x0=-1200, x1=2400), ps]
    e = ex("wow82", look=(.5, -.8))
    f_ = dfig(170, 1560, .56, e, "d82_look_up", t=t, head_add=.02 * math.sin(t * 3))
    o.append(f_["svg"])
    wx, wy = f_["wrist"]["n"]
    o.append(marker(wx + 8, wy + 12, 100, .5))
    if t > W(51):                                     # пустые клетки «дышат» — их меньше, чем казалось
        q = .25 * (.5 + .5 * math.sin((t - W(51)) * 9))
        y_ = gy + (LIVED_N + 140) // COLS * c + c
        o.append(f'<rect x="{gx:.1f}" y="{y_:.1f}" width="{COLS * c:.1f}" height="{gy + ROWS * c - y_:.1f}" fill="{WARM}" opacity="{q:.2f}"/>')
    u = ease_io(clamp((t - a) / 1.3))
    fx, fy = cell_xy(gx, gy, c, LIVED_N + 140, COLS)
    s = 4.0 ** (1 - u) * .98
    cx = fx * (1 - u) + 560 * u
    cy = fy * (1 - u) + 900 * u
    s *= 1 + .04 * kick2(t, W(51))
    return view("".join(o), cx, cy, s, 1.5 * (1 - u) + .3 * math.sin(t * 2), bg=WALL)


# ═════════════════════════ книга ═════════════════════════
def table_top(y):
    return (shape(lib.rrect(-300, y, 1400, y + 60, 8), "#c08a55", line([(-280, y + 18), (1380, y + 22)], 3, "#9c6a3c", seed=801), w=4.2, seed=802)
            + f'<rect x="-300" y="{y + 60}" width="1700" height="900" fill="#a8784f"/>')


def frame_s13(t):
    """«Целая книга»: книга падает на стол, обложка — клеточки без букв; кот на столе вздрагивает."""
    lib.DEFS.clear()
    a = T0("s13")
    ty = 1380.0
    o = [wall_bg(1000.0, x0=-400, x1=1500), win(-40, 300, 300, 820, 31), table_top(ty)]
    tl = W(60)
    fall = .38
    if t < tl - fall:
        y, rot, sq = -400.0, -25.0, 1.0
    elif t < tl:
        u = (t - (tl - fall)) / fall
        y, rot, sq = -400 + (ty - 190 + 400) * ease_in(u, 2), -25 + 25 * u, 1.0
    else:
        b = damp(t, tl, 1.0, 3.5, 7)
        y, rot, sq = ty - 190 - 40 * abs(b), 4 * b, 1 - .08 * kick2(t, tl)
    o.append(f'<ellipse cx="560" cy="{ty + 6}" rx="{200 * clamp(1 - (ty - 190 - y) / 1600):.1f}" ry="22" fill="#000" opacity=".18"/>')
    o.append(f'<g transform="translate(560 {ty}) scale(1 {sq:.3f}) translate(-560 {-ty})">{book(560, y, 1.0, rot)}</g>')
    o.append(burst(560, ty, 260, tl, t, "#ffffff", 12, .45))
    jump = 120 * math.sin(math.pi * clamp((t - tl) / .4))
    o.append(PE.cat_svg(900, ty - jump, .42, dict(look=(-.8, .2) if t < tl else (-.6, -.3), perk=1.0, ear=.6 * kick2(t, tl), tail=20 * math.sin(t * 5),
                                                    legs=.6 * clamp(jump / 100)), t))
    dx, dy, r = drift(t, 1.2)
    z = 1.05 + .03 * (t - a) + .07 * kick2(t, tl)
    return view("".join(o), 560 + dx, 1050 + dy, z, r + 1.5 * kick2(t, tl), bg=WALL)


def frame_s14(t):
    """«Четыре тысячи недель»: Дима держит книгу обложкой к зрителю, клетки на обложке загораются по одной."""
    lib.DEFS.clear()
    a = T0("s14")
    o = [wall_bg(1800.0), bookshelf(-60, 260, 300, 7)]
    f_ = dfig(470, 1720, 1.3, ex("wonder81", look=(-.2, .3)), "d82_hold", t=t, head_add=.03 * math.sin(t * 3))
    o.append(f_["svg"])
    hx, hy = f_["hold"]
    lit = int(clamp((t - W(61) + .1) / (WE(63) - W(61))) * 48)
    o.append(book(hx - 60, hy - 30, 1.15 + .04 * kick2(t, W(61)), -4 + 1.5 * math.sin(t * 2.5), lit=lit))
    o.append(sparkle(hx - 60, hy - 30, 220, WE(63) - .1, t))
    dx, dy, r = drift(t, 1.2)
    z = 1.0 + .05 * (t - a) + .04 * kick2(t, W(63))
    return view("".join(o), 540 + dx, 1000 + dy, z, r, bg=WALL)


# ═════════════════════════ значки дел ═════════════════════════
ICONS = [("book", 66), ("bag", 67), ("friends", 68), ("sea", 70), ("star", 72)]


def frame_s15(t):
    """«В каждую новую клетку»: в клетках выскакивают крошечные значки."""
    lib.DEFS.clear()
    a = T0("s15")
    c = 120.0
    x0, y0 = -100.0, 40.0
    cols = 12
    row = 7
    o = [f'<rect x="-600" y="-600" width="2600" height="3200" fill="{EMPTY}"/>', life_grid(x0, y0, c, cols, 16, cols * row)]
    for j, (kind, wi) in enumerate(ICONS[:4]):
        tp = W(wi) - .05
        sc = pop(t, tp)
        if sc > 0:
            cx, cy = cell_xy(x0, y0, c, cols * row + 2 + j * 2, cols)
            if t > tp:
                o.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{c}" height="{c}" fill="{WARM_L}" opacity="{min(1, (t - tp) * 4):.2f}"/>')
            o.append(icon(kind, cx + c / 2, cy + c / 2, c * 1.05 * sc, 8 * math.sin(t * 3 + j)))
            o.append(sparkle(cx + c / 2, cy + c / 2, 90, tp, t))
    u = clamp((t - a) / (T1("s15") - a))
    cx = 300 + 500 * ease_io(u)
    return view("".join(o), cx, 1020, 1.0 + .03 * kick2(t, W(70)), .6 * math.sin(t * 1.5), bg=EMPTY)


def frame_s16(t):
    """«Одно важное дело, и неделя не пропадает»: Дима ставит звезду, клетка загорается тёплым."""
    lib.DEFS.clear()
    a = T0("s16")
    c = 52.0
    gx, gy = 470.0, 380.0
    cols, rows = 16, 30
    row = 15
    base = cols * row
    o = [wall_bg(1760.0, x0=-600, x1=1800), f'<rect x="{gx - 20}" y="{gy - 20}" width="{cols * c + 40}" height="{rows * c + 40}" fill="#fffdf7" stroke="{INK}" stroke-width="4"/>',
         life_grid(gx, gy, c, cols, rows, base)]
    marks = [(1, "book", -1.0), (3, "friends", -1.0), (5, "bag", -1.0), (7, "star", W(72)), (9, "sea", W(73) + .35)]
    tgt = None
    for j, (ci, kind, tp) in enumerate(marks):
        cx, cy = cell_xy(gx, gy, c, base + ci, cols)
        glow = clamp((t - W(73)) / .25) if ci == 7 else (1.0 if tp < 0 else clamp((t - tp) / .2))
        glow = max(glow, clamp((t - W(76) - .06 * j) / .2))
        if glow > 0:
            o.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{c}" height="{c}" fill="{WARM}" opacity="{glow:.2f}"/>')
        sc = 1.0 if tp < 0 else pop(t, tp)
        if sc > 0:
            o.append(icon(kind, cx + c / 2, cy + c / 2, c * .8 * sc))
        if tp > 0 and tgt is None and t < tp + .25:
            tgt = (cx + c / 2, cy + c / 2)
    for j in range(5):
        o.append(sparkle(gx + (1 + 2 * j + .5) * c, gy + (row + .5) * c, 80, W(76) + .06 * j, t))
    if tgt is None:
        tgt = (gx + 9.5 * c + 40, gy + (row + 1.5) * c)
    e = ex("proud82", look=(.6, -.2)) if t > W(76) else ex("focus", look=(.8, -.1))
    f_ = dfig(330, 1560, 1.05, e, "d82_rest", t=t, arms={"n": ("ik", (tgt[0] + 26, tgt[1] + 40), -1)}, hands={"n": dict(PE._GRIP)})
    o.append(f_["svg"])
    wx, wy = f_["wrist"]["n"]
    o.append(marker(tgt[0] - 4, tgt[1] - 4, math.degrees(math.atan2(wy - tgt[1], wx - tgt[0])), .75))
    dx, dy, r = drift(t, 1.0)
    z = 1.1 + .03 * (t - a) + .05 * kick2(t, W(73)) + .05 * kick2(t, W(77))
    return view("".join(o), 680 + dx, 1050 + dy, z, r, bg=WALL)


def frame_s17(t):
    """«А кот ставит туда свою лапу»: кот прыгает к сетке и ставит отпечаток лапы в клетку."""
    lib.DEFS.clear()
    a = T0("s17")
    c = 120.0
    x0, y0 = -60.0, -200.0
    cols = 11
    o = [f'<rect x="-600" y="-600" width="2600" height="3200" fill="{EMPTY}"/>', life_grid(x0, y0, c, cols, 18, cols * 6)]
    for j, kind in enumerate(("book", "bag", "friends", "sea")):
        cx, cy = cell_xy(x0, y0, c, cols * 6 + 1 + 2 * j, cols)
        o.append(f'<rect x="{cx}" y="{cy}" width="{c}" height="{c}" fill="{WARM}"/>' + icon(kind, cx + c / 2, cy + c / 2, c * .8))
    tp = W(80) + .1
    pcx, pcy = cell_xy(x0, y0, c, cols * 7 + 5, cols)
    if t > tp:
        o.append(f'<rect x="{pcx}" y="{pcy}" width="{c}" height="{c}" fill="{WARM}" opacity="{clamp((t - tp) / .2):.2f}"/>')
        o.append(icon("paw", pcx + c / 2, pcy + c / 2, c * .85 * (1 + .25 * kick2(t, tp))))
        o.append(burst(pcx + c / 2, pcy + c / 2, 130, tp, t, WARM, 10, .4))
    # кот: прыжок снизу к клетке, лапа поднимается и шлёпает
    tj = a + .05
    u = clamp((t - tj) / .45)
    catx = 640 + 120 * (1 - ease_out(u))
    lp = clamp((t - (tp - .3)) / .7)
    caty = 1850 - 260 * ease_out(u) - 650 * math.sin(math.pi * lp) ** .7
    paw = clamp((t - (tp - .35)) / .2) * (1 - .5 * clamp((t - tp) / .15))
    st = dict(look=(.5, -.8), perk=1.0, tail=25 * math.sin(t * 4), paw=paw, paw_dx=120, legs=.8 * (1 - u), smile=1.0 if t > tp else 0.0)
    o.append(PE.cat_svg(catx, caty, 1.0, st, t))
    dx, dy, r = drift(t, 1.2)
    z = 1.0 + .06 * kick2(t, tp)
    return view("".join(o), 560 + dx, 1000 + dy, z, r + 1.2 * kick2(t, tp), bg=EMPTY)


def frame_s18(t):
    """ПЕТЛЯ к хуку: та же сетка, Дима идёт спокойно, клетки за ним загораются тёплым, кот рядом."""
    lib.DEFS.clear()
    cam, g, dg, ct = run_world(t, 1.2, 560.0, 1430.0, 1.0, T0("s18"), warm=True, cat_dx=230.0, cat_k=.42, walk=True)
    return lib.svg(f'<rect width="1080" height="1920" fill="{EMPTY}"/><g transform="{lib.cam(*cam)}">{g + ct + dg}</g>')


def frame(sid, t):
    lib.INK_K[0] = 1.0
    return globals()["frame_" + sid](t)
