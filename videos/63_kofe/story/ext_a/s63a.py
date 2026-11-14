"""Рилс 63 «кофе», группа A: миф и правда графикой на бумаге.
s02 (1.4–4.4): «таблица правила» на листе, приколотом к столу: в центре кружка кофе с паром; «каждой» (2.30), «чашки» (2.72)
    слева и справа выскакивают ещё кружки с отскоком; «надо пить» (3.17–3.40) к каждой по пунктирной стрелке снизу подъезжает
    стакан, «стакан» (3.66) встаёт в клетку под кружкой со сжатием, «воды» (4.08) стаканы наполняются голубым снизу вверх.
    Карандашные линии таблицы дорисовываются с первого кадра. Камера: с крупного на центральную кружку отъезд на всю таблицу,
    потом дрейф вправо и лёгкий наезд на правую пару.
s05 (8.25–9.65): тот же лист (пары кружка+стакан); «На самом» (8.35–8.77) влетает красный маркер, «деле» (9.14, пик riser) —
    живой крест через всю таблицу, стаканы подпрыгивают и разъезжаются, лист мнётся складками. Наезд с разгоном к центру креста,
    тряска на ударе.
s07 (12.65–15.4): рычажные весы на бумаге: слева кружка в разрезе (почти вся — вода, тонкий слой кофе сверху), справа —
    пустой пунктирный контур капли («потеря»). «Вода» (12.68) вода светится и качается волной, «почти всё» (14.05–14.38) правая
    чаша тянет вниз, контур дрожит, «возмещает» (14.60) капля воды прыгает из кружки дугой и заполняет контур, весы
    выравниваются с затухающим отскоком. Камера: наезд, качание кадра в такт коромыслу.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Предметы — common/props.py."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import props as P  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rect_pts, shape, svg  # noqa: E402

INK = lib.INK
PENCIL = "#6B6458"


def lerp(a, b, u):
    return a + (b - a) * u


def frame_svg(body, cx, cy, s, rot, bg):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>')


def partial(pts, u):
    """Первая доля u ломаной (для дорисовки линий)."""
    if u <= 0:
        return []
    S = lib.sample(pts, False, 3.0)
    n = max(2, int(len(S) * clamp(u)))
    return [(float(a), float(b)) for a, b in S[:n]]


# ═══════════════════════════════ лист правила (s02, s05) ═══════════════════════════════
SHEET = (110, 330, 970, 1300)          # x0, y0, x1, y1 листа
COLS = [255.0, 540.0, 825.0]           # центры столбцов
ROW_MUG, ROW_GLASS = 760.0, 1175.0     # дно кружек / стаканов
MK, GK = 1.55, 1.45                    # масштабы кружки и стакана
TBL = (150, 470, 930, 1250)            # рамка таблицы
ROW_SPLIT = 830.0
MUG_COLS = ["red", "white", "blue"]
T_POP = [None, 2.30, 2.72]             # центральная с самого начала; левая на «каждой», правая на «чашки»
ORDER = [1, 0, 2]                      # столбец → индекс в T_POP (центр первым)
T_ARROW, T_LAND, T_FILL = 3.10, 3.66, 4.06


def desk_bg(t):
    o = [blob(rect_pts(-800, -800, 1900, 2700), "#7A5236")]
    for i in range(-10, 18):   # волокна стола
        y = -800 + i * 170
        o.append(line([(-800, y), (300, y + 20), (1900, y - 10)], 4, "#6A462D", taper=.2, wmin=.4, seed=40 + i))
    return "".join(o)


def sheet_pts(crumple=0.0, seed=0):
    x0, y0, x1, y1 = SHEET
    pts = []
    n = 14
    for side in range(4):
        for i in range(n):
            q = i / n
            if side == 0:
                x, y = x0 + (x1 - x0) * q, y0
            elif side == 1:
                x, y = x1, y0 + (y1 - y0) * q
            elif side == 2:
                x, y = x1 - (x1 - x0) * q, y1
            else:
                x, y = x0, y1 - (y1 - y0) * q
            j = crumple * (9 * math.sin(i * 2.7 + side * 1.9 + seed) + 6 * math.sin(i * 5.3 + side * .7))
            if side in (0, 2):
                y += j
            else:
                x += j
            pts.append((x, y) + ((1,) if i == 0 else ()))
    return pts


CREASES = [[(150, 520), (420, 700), (610, 640), (930, 900)], [(200, 1240), (480, 980), (720, 1080), (940, 760)],
           [(560, 360), (500, 700), (600, 1000), (520, 1280)], [(120, 900), (380, 860), (700, 940), (960, 860)]]


def sheet(t, draw_u=1.0, crumple=0.0):
    """Лист в клетку с таблицей 3×2 карандашом; draw_u — сколько линий таблицы дорисовано; crumple — помятость."""
    x0, y0, x1, y1 = SHEET
    inner = blob(rect_pts(x0 - 40, y0 - 40, x1 + 40, y1 + 40), P.C_PAGE)
    for i in range(1, 17):   # клетка тетради
        yy = y0 + i * 58
        inner += line([(x0 - 30, yy), (x1 + 30, yy)], 2.2, "#C9D6E4", taper=0, wmin=1, seed=60 + i)
    for i in range(1, 16):
        xx = x0 + i * 58
        inner += line([(xx, y0 - 30), (xx, y1 + 30)], 2.2, "#C9D6E4", taper=0, wmin=1, seed=90 + i)
    inner += line([(x0 + 60, y0 - 30), (x0 + 60, y1 + 30)], 3.0, "#E59A9A", taper=0, wmin=1, seed=120)   # поля
    if crumple > 0.01:   # складки: тень и светлая кромка — сплошные полосы
        for j, cr in enumerate(CREASES):
            pts = partial(cr, clamp(crumple * 1.6 - j * .15))
            if len(pts) >= 2:
                inner += line([(a + 4, b + 5) for a, b in pts], 9 * crumple, "#E3D5B2", taper=.5, wmin=.2, seed=130 + j)
                inner += line(pts, 3.2 * crumple, "#B8A984", taper=.5, wmin=.2, seed=140 + j)
    o = [blob([(p[0] + 14, p[1] + 18) for p in sheet_pts(crumple)], "#5C3D27")]   # тень листа на столе
    o.append(shape(sheet_pts(crumple), P.C_PAGE, inner, w=4.4, seed=150))
    # таблица карандашом: рамка, разделители столбцов, строка
    tx0, ty0, tx1, ty1 = TBL
    segs = [[(tx0, ty0), (tx1, ty0 + 4)], [(tx1, ty0 + 4), (tx1 - 3, ty1)], [(tx1 - 3, ty1), (tx0 + 2, ty1 - 3)], [(tx0 + 2, ty1 - 3), (tx0, ty0)],
            [(tx0 + 2, ROW_SPLIT), (tx1 - 2, ROW_SPLIT + 5)], [(397, ty0 + 2), (400, ty1 - 2)], [(683, ty0 + 3), (680, ty1 - 2)]]
    for j, sg in enumerate(segs):
        u = clamp(draw_u * len(segs) - j)
        pts = partial(sg, u)
        if len(pts) >= 2:
            o.append(line(pts, 6.0, PENCIL, taper=.15, wmin=.5, seed=160 + j))
    # уголки скотча (сплошные)
    for (cx, cy, r) in ((x0 + 10, y0 + 6, -38), (x1 - 10, y0 + 6, 38)):
        o.append(f'<g transform="translate({f(cx)} {f(cy)}) rotate({r})">' +
                 shape(rect_pts(-70, -22, 70, 22), "#E8D9A6", blob(rect_pts(-70, 8, 70, 22), "#D4C38C"), w=3.0, seed=170 + int(cx)) + "</g>")
    return "".join(o)


def mug_in_cell(col, t, extra_dy=0.0, extra_rot=0.0):
    i = ORDER[col]
    tp = T_POP[i]
    x = COLS[col]
    if tp is None:
        sx, sy = 1.0, 1.0
        bob = 4 * math.sin(t * 5.3)
        sx, sy = 1 + .02 * math.sin(t * 6), 1 - .02 * math.sin(t * 6)
    else:
        sx, sy = P.pop(t, tp, amp=.34)
        bob = 0.0
        if sx <= 0.01:
            return ""
    k = MK
    m = P.coffee_mug(0, 0, 1.0, col=MUG_COLS[col], steam=1.0 * clamp(sy), t=t + col, seed=col)
    return (f'<g transform="translate({f(x)} {f(ROW_MUG + extra_dy + bob * 0)}) rotate({f(extra_rot)}) scale({k * sx:.4f} {k * sy:.4f})">'
            f'{m}</g>')


def glass_path(col):
    x = COLS[col]
    sx = {0: -60.0, 1: 540.0, 2: 1140.0}[col]
    return [(sx, 1560.0), (lerp(sx, x, .5) + (-40 if col == 1 else 0), 1420.0), (x, ROW_GLASS)]


def bez(pts, s):
    (ax, ay), (bx, by), (cx, cy) = pts
    return ((1 - s) ** 2 * ax + 2 * (1 - s) * s * bx + s * s * cx, (1 - s) ** 2 * ay + 2 * (1 - s) * s * by + s * s * cy)


def bez_pts(pts, s0=0.0, n=30):
    return [bez(pts, s0 + (1 - s0) * i / n) for i in range(n + 1)]


def glass_in_cell(col, t, fill_on=True, dx=0.0, dy=0.0, rot=0.0):
    d = 0.08 * col
    pth = glass_path(col)
    ta, tl = T_ARROW + d, T_LAND + d * .5
    o = ""
    if t < tl:
        s = ease_io(clamp((t - (ta + .07)) / (tl - ta - .07)))
        au = clamp((t - ta) / .22)
        if au > 0:
            rest = bez_pts(pth, s)
            o += P.dash_arrow(partial(rest, au) if au < 1 else rest, 1.0 if au >= 1 else au, w=7, col=INK, seed=200 + col)
        if s <= 0:
            return o
        gx, gy = bez(pth, s)
        return o + P.glass(gx, gy, GK, rot=-12 * (1 - s) * (1 if col != 0 else -1), fill=0, t=t)
    sx, sy = P.squash(t, tl, amp=.22)
    fl = ease_out(clamp((t - (T_FILL + .07 * col)) / .42)) if fill_on else 0.0
    if not fill_on:
        fl = 0.0
    g = P.glass(0, 0, 1.0, fill=fl, t=t, seed=col, splash=0)
    return f'<g transform="translate({f(COLS[col] + dx)} {f(ROW_GLASS + dy)}) rotate({f(rot)}) scale({GK * sx:.4f} {GK * sy:.4f})">{g}</g>'


def s02(t):
    body = [desk_bg(t), sheet(t, ease_out(clamp((t - 1.2) / 1.0), 2))]
    for c in (0, 1, 2):
        body.append(mug_in_cell(c, t))
    for c in (0, 1, 2):
        body.append(glass_in_cell(c, t))
    # камера: крупно центральная кружка → вся таблица → дрейф вправо и наезд на правую пару
    u1 = ease_io(clamp((t - 1.2) / 1.05))
    s = lerp(1.7, 1.12, u1)
    cx = 540.0
    cy = lerp(ROW_MUG - 80, 835, u1)
    u2 = ease_io(clamp((t - 3.55) / 1.05))
    s *= lerp(1.0, 1.12, u2)
    cx += 70 * u2
    cy += lerp(0, 60, u2)
    for tp in (2.30, 2.72, 3.66):   # толчок камеры на выскок/посадку
        dx, dy = P.shake(t, tp, 7, .25, seed=int(tp * 10))
        cx += dx
        cy += dy
    if t >= T_FILL - .02:
        cy += 0
    return frame_svg("".join(body), cx, cy, s, -1.2 + 1.2 * u1 + .6 * u2, "#7A5236")


# s05
T_MK0, T_X0, T_X1 = 8.20, 8.84, 9.22
CROSS = ((170, 450), (910, 1270), (910, 450), (170, 1270))


def s05(t):
    cr = clamp((t - 9.14) / .35)
    crumple = ease_out(cr, 2) * .9
    sx_, sy_ = P.squash(t, 9.14, amp=.05, freq=2.5)
    body = [desk_bg(t)]
    sheet_g = sheet(t, 1.0, crumple)
    # на ударе лист сплющивается и отскакивает
    items = [sheet_g]
    for c in (0, 1, 2):
        dy = P.hop(t, 9.16 + .04 * c, 28, .3)
        items.append(mug_in_cell(c, t + 0, extra_dy=dy, extra_rot=[-6, 3, 7][c] * ease_out(cr)))
    for c in (0, 1, 2):
        dy = P.hop(t, 9.15 + .03 * c, 120, .42)
        dx = (c - 1) * 150 * ease_out(clamp((t - 9.15) / .4)) + (-130 if c == 1 else 0) * ease_out(clamp((t - 9.15) / .4)) * 0
        dx += [-60, 0, 60][c] * ease_out(clamp((t - 9.15) / .45))
        rot = [-24, 14, 26][c] * math.sin(math.pi * clamp((t - 9.15) / .42))
        items.append(glass_in_cell(c, 20.0, True, dx=dx * .5, dy=dy, rot=rot))
    items.append(P.clink(540, 860, 2.4, clamp((t - 9.14) / .3), seed=3, col=P.C_MARKER))
    xu = ease_io(clamp((t - T_X0) / (T_X1 - T_X0)))
    items.append(P.cross_stroke(*CROSS, u=xu, w=46, seed=5))
    # маркер: влетает из правого верхнего угла, ведёт штрих, после креста отскакивает вверх
    if t < T_X0:
        u = ease_out(clamp((t - T_MK0) / (T_X0 - T_MK0)), 3)
        mx, my = lerp(1250, CROSS[0][0], u), lerp(80, CROSS[0][1], u)
        rot = lerp(-160, -125, u) + 25 * math.sin(u * math.pi)
    elif t < T_X1:
        mx, my = P.marker_tip(*CROSS, xu)
        rot = -125 if xu < .5 else -55
    else:
        u = ease_out(clamp((t - T_X1) / .4))
        mx, my = lerp(CROSS[3][0], CROSS[3][0] + 60, u), lerp(CROSS[3][1], CROSS[3][1] - 260, u)
        rot = -55 + 20 * u
    a = math.radians(rot)
    mk = P.red_marker(mx - 66 * 1.6 * math.cos(a), my - 66 * 1.6 * math.sin(a), 1.6, rot)
    items.append(mk)
    body.append(f'<g transform="translate(540 860) scale({sx_:.4f} {sy_:.4f}) translate(-540 -860)">{"".join(items)}</g>')
    # камера: наезд с разгоном к центру креста, тряска на ударе
    u = ease_in(clamp((t - 8.05) / (9.14 - 8.05)), 2.4)
    s = lerp(1.06, 1.22, u)
    cx, cy = lerp(560, 540, u), lerp(850, 860, u)
    rot = lerp(1.5, -1.0, u)
    if t > 9.14:
        s = 1.22 - .08 * ease_out(clamp((t - 9.14) / .5))
        dx, dy = P.shake(t, 9.14, 26, .45, seed=9)
        cx += dx
        cy += dy
        rot += 2.2 * math.exp(-(t - 9.14) * 7) * math.sin((t - 9.14) * 40)
    return frame_svg("".join(body), cx, cy, s, rot, "#7A5236")


# ═══════════════════════════════ s07: весы ═══════════════════════════════
SC = (540.0, 1240.0)
SK = 1.5
POST, HANGL = 540.0, 270.0
T_WATER, T_DIP, T_JUMP, T_FILLD = 12.68, 14.05, 14.60, 14.92


def tilt07(t):
    a = 4.0 + 1.6 * math.sin((t - 12.4) * 3.1) * math.exp(-(t - 12.4) * .8)       # лёгкое покачивание с начала
    if t > T_DIP:
        a = P.settle(t, T_DIP, a, 15.0, 1.4, 3.0)
    if t > T_FILLD:
        a = P.settle(t, T_FILLD, P.settle(T_FILLD, T_DIP, 4.0, 15.0, 1.4, 3.0), 0.0, 1.25, 2.6)
    return a


def paper_bg(t):
    o = [blob(rect_pts(-800, -800, 1900, 2700), P.C_PAGE)]
    for i in range(-14, 40):
        o.append(line([(-800, i * 64), (1900, i * 64)], 2.2, "#CFDBE6", taper=0, wmin=1, seed=300 + i))
    for i in range(-14, 30):
        o.append(line([(i * 64, -800), (i * 64, 2700)], 2.2, "#CFDBE6", taper=0, wmin=1, seed=360 + i))
    o.append(blob(ellipse_pts(SC[0], SC[1] + 10, 330, 36, 24), "#E3D3AE"))   # тень весов
    return "".join(o)


def drop_outline(u_fill, t, wob=0.0, k=1.0):
    """Контур капли-«потери»: пунктир; u_fill — заполнение голубым снизу вверх."""
    pts = [(0, -96), (28, -52), (44, -14), (38, 14), (0, 30), (-38, 14), (-44, -14), (-28, -52), (0, -96)]
    pts = [(x * k * (1 + .06 * wob * math.sin(t * 40)), (y - 32) * k) for x, y in pts]
    o = ""
    if u_fill > 0.01:
        top = 0 - (130 * k) * clamp(u_fill)
        fill = [(x, y) for x, y in pts]
        cl = lib.clip_of(fill)
        o += f'<g clip-path="url(#{cl})">' + blob(rect_pts(-80 * k, top, 80 * k, 10 * k), P.C_WATER) + \
            blob(rect_pts(10 * k, top, 80 * k, 10 * k), P.C_WATER_SH) + "</g>"
        if u_fill >= .999:
            o += line(lib.sample(pts, False, 2.0).tolist() if hasattr(lib.sample(pts, False, 2.0), "tolist") else pts, 5, INK, taper=0, wmin=1, seed=420)
            o += blob(ellipse_pts(-12 * k, -40 * k, 7 * k, 14 * k, 10), "#FFFFFF")
            return o
    o += P.dash_path(pts, 1.0, 6.5, INK, gap=14, dash=18, seed=421)
    return o


def s07(t):
    a = tilt07(t)
    wave = clamp((t - T_WATER) / .2) * (1.0 if t < 13.9 else .6) + 0.25
    glow = clamp((t - T_WATER) / .15) * (1 - clamp((t - 13.8) / .5)) + .15
    left = P.mug_cut(0, 0, 1.0, glow=glow, wave=wave, t=t)
    left = f'<g transform="scale(1.3)">{left}</g>'
    fill_u = ease_out(clamp((t - T_FILLD) / .16))
    jig = clamp((t - T_DIP) / .1) * (1 - clamp((t - T_JUMP) / .2))
    right = drop_outline(fill_u, t, jig, 1.25)
    body = [paper_bg(t), P.scales(SC[0], SC[1], SK, a, left=left, right=right, post=POST, hang=HANGL)]
    (lx, ly), (rx, ry) = P.scale_pans(SC[0], SC[1], SK, a, POST, HANGL)
    au = clamp((t - 14.1) / .45) * (1 - clamp((t - T_FILLD) / .25))
    if au > 0:
        x0, y0 = lx, ly - 160 * SK
        x1, y1 = rx, ry - 70 * SK
        arc = [(lerp(x0, x1, q / 24), lerp(y0, y1, q / 24) - 330 * 4 * (q / 24) * (1 - q / 24)) for q in range(25)]
        if t > T_JUMP:   # стирается позади капли
            q0 = int(24 * clamp((t - T_JUMP) / (T_FILLD - T_JUMP)))
            arc = arc[q0:]
        if len(arc) >= 2:
            body.append(P.dash_arrow(arc, min(au, .999) if t < T_JUMP and au < 1 else 1.0, w=7, col=P.C_WATER_SH, seed=33))
    # прыжок капли: из кружки (левая чаша) дугой в контур (правая чаша)
    if T_JUMP <= t < T_FILLD + .02:
        u = clamp((t - T_JUMP) / (T_FILLD - T_JUMP))
        x0, y0 = lx, ly - 160 * SK
        x1, y1 = rx, ry - 70 * SK
        px = lerp(x0, x1, u)
        py = lerp(y0, y1, u) - 330 * 4 * u * (1 - u)
        ang = math.degrees(math.atan2((y1 - y0) - 330 * 4 * (1 - 2 * u), (x1 - x0))) - 90
        sx, sy = 1 - .15 * math.sin(math.pi * u), 1 + .25 * math.sin(math.pi * u)
        body.append(f'<g transform="translate({f(px)} {f(py)}) rotate({f(ang)}) scale({sx * SK * 2.6:.3f} {sy * SK * 2.6:.3f})">{P.drop(0, 0)}</g>')
        if u < .25:
            body.append(P.splash_drops(x0, y0, SK * .8, u / .25 * .7, seed=4))
    if t >= T_FILLD:
        body.append(P.splash_drops(rx, ry - 70 * SK, SK * .7, clamp((t - T_FILLD) / .45), seed=8))
    # камера: наезд на весы, качание кадра в такт коромыслу
    u = ease_out(clamp((t - 12.45) / 2.9), 2)
    s = lerp(1.0, 1.1, u)
    cx = lerp(540, 545, u)
    cy = lerp(1010, 990, u)
    rot = -a * .12
    if t > T_FILLD:
        s += .05 * math.exp(-(t - T_FILLD) * 5) * math.sin((t - T_FILLD) * 18)
    return frame_svg("".join(body), cx, cy, s, rot, P.C_PAGE)


def frame(sid, t):
    lib.dyn_begin()
    lib.DEFS.clear()
    return {"s02": s02, "s05": s05, "s07": s07}[sid](t)
