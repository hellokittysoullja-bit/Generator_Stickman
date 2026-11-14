"""Дневная комната Димы для рилса 46 (desk-планы s03, s04, s14): то же окно, стена, часы, доска, полка и стол, что в
ночной комнате рилса 32 (den.py), но окно на дневной город, лампа выключена, на столе ноутбук (3/4, экран с письмом) и
кружка. Мир — в тех же координатах, что den.py (Дима сидит слева лицом вправо, таз (230, 1262))."""
import math

import den
import lib
import room
from lib import INK, blob, ellipse_pts, line, mix, rect_pts, shape

LAP = (700.0, 1122.0, 1.0)        # ноутбук: центр переднего края, масштаб
SCR_W, SCR_H = 270.0, 250.0       # внутренний размер экрана (локальные px)


def window_day(t, tone="noon"):
    x0, y0, x1, y1 = den.WIN
    if tone == "noon":
        stops = [(0, "#5fb0ea", 1), (.55, "#9bd6f5", 1), (1, "#d6f0fb", 1)]
        far, h1, h2, h3, lit, dark = "#a9bdd6", "#b9c9de", "#9db3d0", "#aabfd9", "#f2f8fd", "#6f8fb8"
    else:
        stops = [(0, "#f0a47a", 1), (.5, "#f9cf9b", 1), (1, "#fff0cc", 1)]
        far, h1, h2, h3, lit, dark = "#d9b5a0", "#d8bba8", "#c9a897", "#d3b3a0", "#fff2d4", "#9a7c78"
    sky = lib.lin_grad(stops, 0, 0, 0, 1)
    inner = [f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="url(#{sky})"/>']
    if tone == "noon":
        sx, sy = x0 + 250, y0 + 100
        g = lib.rad_grad([(0, "#fff8c8", .9), (.4, "#fff4b0", .35), (1, "#fff4b0", 0)], sx, sy, 150, 150)
        inner.append(f'<rect x="{sx - 160}" y="{sy - 160}" width="320" height="320" fill="url(#{g})"/>')
        inner.append(blob(ellipse_pts(sx, sy, 44, 44, 20), "#fff6b8"))
    else:
        sx, sy = x0 + 80, y1 - 250
        g = lib.rad_grad([(0, "#fff0b0", .95), (.4, "#ffd890", .4), (1, "#ffd890", 0)], sx, sy, 200, 200)
        inner.append(f'<rect x="{sx - 210}" y="{sy - 210}" width="420" height="420" fill="url(#{g})"/>')
        inner.append(blob(ellipse_pts(sx, sy, 40, 40, 20), "#fff2b0"))
    # облака плывут
    for k, (cx, cy, sc) in enumerate([(60, 120, 1.0), (260, 250, .8), (180, 60, .6)]):
        x = x0 + (cx + 9 * t + 400 * k) % (x1 - x0 + 240) - 120
        y = y0 + cy
        c = [blob(ellipse_pts(x, y, 70 * sc, 26 * sc, 14), "#ffffff", .95),
             blob(ellipse_pts(x - 34 * sc, y - 14 * sc, 36 * sc, 24 * sc, 12), "#ffffff", .95),
             blob(ellipse_pts(x + 30 * sc, y - 18 * sc, 40 * sc, 28 * sc, 12), "#ffffff", .95)]
        inner.extend(c)
    far_pts = [(x0 - 20, y1 - 330), (x0 + 60, y1 - 330), (x0 + 60, y1 - 390), (x0 + 140, y1 - 390), (x0 + 140, y1 - 300), (x0 + 220, y1 - 300),
               (x0 + 220, y1 - 420), (x0 + 290, y1 - 420), (x0 + 290, y1 - 340), (x1 + 20, y1 - 340), (x1 + 20, y1 + 20), (x0 - 20, y1 + 20)]
    inner.append(blob(far_pts, far))
    for i, (x, y, w, col) in enumerate([(x0 - 10, y1 - 250, 120, h1), (x0 + 120, y1 - 200, 110, h2), (x0 + 240, y1 - 280, 120, h3)]):
        inner.append(shape(rect_pts(x, y, x + w, y1 + 30), col, blob(rect_pts(x + w * .72, y, x + w, y1 + 30), mix(col, "#000000", .12), .8), w=3,
                           seed=3210 + i))
        rs = den.rsd(3220, i)
        for r in range(6):
            for c in range(int(w // 34)):
                wx, wy = x + 12 + c * 34, y + 18 + r * 46
                if wy > y1:
                    continue
                inner.append(blob(rect_pts(wx, wy, wx + 18, wy + 26), lit if rs.uniform() < .5 else dark))
    fr = "#e8dcc6"
    mx, my = (x0 + x1) / 2, y0 + (y1 - y0) * .45
    inner.append(blob(rect_pts(mx - 10, y0, mx + 10, y1), fr) + blob(rect_pts(x0, my - 10, x1, my + 10), fr))
    s = [shape(rect_pts(x0 - 22, y0 - 22, x1 + 22, y1 + 22, 6), fr, blob(rect_pts(x1, y0 - 22, x1 + 22, y1 + 22), "#c8baa2", .9), w=4.6, seed=3230)]
    s.append(shape(rect_pts(x0, y0, x1, y1, 4), "#9bd6f5", "".join(inner), w=4, seed=3231))
    for k, (a, b) in enumerate([((x0 + 26, y0 + 130), (x0 + 110, y0 + 40)), ((x0 + 40, y0 + 190), (x0 + 150, y0 + 80))]):
        s.append(f'<path d="M{a[0]} {a[1]}L{b[0]} {b[1]}" stroke="#ffffff" stroke-opacity=".28" stroke-width="{12 - k * 4}" stroke-linecap="round"/>')
    s.append(shape(rect_pts(x0 - 44, y1 + 16, x1 + 44, y1 + 46, 4), "#efe4d0", blob(rect_pts(x0 - 44, y1 + 34, x1 + 44, y1 + 46), "#cbbda4", .9),
                   w=4, seed=3232))
    s.append(room.pot(x1 - 70, y1 + 16, .9, 3240, leaves=6, col="#5f86a8"))
    cx0 = x1 + 30
    cur = [(cx0, y0 - 60), (cx0 + 70, y0 - 60), (cx0 + 82, y0 + 200), (cx0 + 64, y1 + 60), (cx0 + 96, den.FLOOR_Y - 60, 1), (cx0 + 6, den.FLOOR_Y - 60, 1),
           (cx0 + 14, y1)]
    inn = blob([(cx0 + 40, y0 - 60), (cx0 + 70, y0 - 60), (cx0 + 82, y0 + 200), (cx0 + 64, y1 + 60), (cx0 + 96, den.FLOOR_Y - 60), (cx0 + 56, den.FLOOR_Y - 60)],
               "#7d3b3b", .8)
    for k in range(3):
        xx = cx0 + 20 + k * 22
        inn += line([(xx, y0 - 40), (xx + 4, y0 + 300), (xx + 12, den.FLOOR_Y - 80)], 2.4, "#5e2b2b", seed=3250 + k, op=.8)
    s.append(shape(cur, "#a24f48", inn, w=4.2, seed=3249))
    s.append(shape(rect_pts(x0 - 70, y0 - 78, x1 + 150, y0 - 62, 6), "#3a2a22", "", w=3, seed=3248))
    return "".join(s)


def room_back_day(t, clock=(270.0, 0.0, 0.0, 0.0), tone="noon"):
    h, m, jolt, tilt = clock
    return "".join([den.wall(t), window_day(t, tone), den.board(t), den.shelf(t), den.clock(h, m, jolt, tilt), den.floor()])


def daylight(tone="noon", k=1.0):
    """Тёплый свет из окна: луч на стену и стол + лёгкая засветка (screen) — поверх мира, в координатах мира."""
    col = "#fff3d0" if tone == "noon" else "#ffd9a0"
    g = lib.lin_grad([(0, col, .30 * k), (1, col, 0)], 0, 0, 1, 1)
    beam = [(60, 300), (420, 280), (1000, 1250), (380, 1330)]
    gl = lib.rad_grad([(0, col, .28 * k), (1, col, 0)], 250, 560, 700, 700)
    return (f'<path d="{lib.fill_d([p + (1,) for p in beam])}" fill="url(#{g})" style="mix-blend-mode:screen" {lib.blur(18)}/>'
            f'<rect x="-600" y="-600" width="2400" height="3400" fill="url(#{gl})" style="mix-blend-mode:screen"/>')


# ═════════════════════════ ноутбук ═════════════════════════
def laptop(content="", glow=1.0, lap=LAP, bob=0.0):
    """Ноутбук в три четверти: низкая база с клавиатурой и стоящий экран. content — SVG в локальных координатах экрана
    (0..SCR_W, 0..SCR_H). Возвращает (svg, функция локальные→мир)."""
    bx, by, k = lap
    by = by + bob

    def P(x, y):
        return (bx + x * k, by + y * k)

    def Q(pts):
        return [P(*p[:2]) + tuple(p[2:]) for p in pts]

    o = [blob([P(-190, 10), P(200, 10), P(214, 24), P(-170, 28)], "#1a0c04", .35, lib.blur(8))]
    # передняя грань базы и верхняя грань с клавишами
    o.append(shape(Q([(-176, -16, 1), (190, -16, 1), (190, 4, 1), (-176, 4, 1)]), "#b9c2d0",
                   blob(Q([(-176, -4), (190, -4), (190, 4), (-176, 4)]), "#8e98a8", .9), w=3.6, seed=5101))
    top = Q([(-176, -16, 1), (190, -16, 1), (152, -58, 1), (-136, -58, 1)])
    inner = ""
    for r in range(3):
        y = -26 - r * 11
        xa, xb = -150 + r * 10, 168 - r * 10
        for c in range(11):
            x = xa + (xb - xa) * c / 10
            inner += blob([P(x - 11, y - 3), P(x + 11, y - 3), P(x + 10, y + 3), P(x - 10, y + 3)], "#6f7a8c", .95)
    inner += blob([P(-30, -18), P(60, -18), P(54, -26), P(-22, -26)], "#8a95a6", .9)
    o.append(shape(top, "#cdd5e0", inner, w=3.6, seed=5102))
    # экран: рамка и матрица
    outer = Q([(-142, -58, 1), (156, -58, 1), (156, -318, 1), (-142, -332, 1)])
    o.append(shape(outer, "#aeb7c6", blob(Q([(120, -58), (156, -58), (156, -318), (120, -322)]), "#8a94a6", .9), w=4, seed=5103))
    x0, y0, x1, y1 = -126, -314, 140, -72
    gx = lib.rad_grad([(0, "#bfe0ff", .35 * glow), (1, "#bfe0ff", 0)], *P(0, -190), 330 * k, 330 * k)
    scr = Q([(x0, y0 + 5, 1), (x1, y0 - 2, 1), (x1, y1, 1), (x0, y1, 1)])
    ax, ay = P(x0, y0 + 5)
    sx = (x1 - x0) / SCR_W * k
    sy = (y1 - y0) / SCR_H * k
    cid = lib.clip_of(scr)
    body = (f'<g clip-path="url(#{cid})"><rect x="{ax - 4:.1f}" y="{ay - 12:.1f}" width="{(x1 - x0) * k + 8:.1f}" height="{(y1 - y0) * k + 20:.1f}" fill="#f4f7fb"/>'
            f'<g transform="translate({ax:.2f} {ay:.2f}) scale({sx:.4f} {sy:.4f})">{content}</g></g>')
    o.append(shape(scr, "#f4f7fb", body, w=3.2, seed=5104))
    o.append(f'<rect x="{P(-200, -420)[0]:.1f}" y="{P(-200, -420)[1]:.1f}" width="{440 * k:.1f}" height="{440 * k:.1f}" fill="url(#{gx})" style="mix-blend-mode:screen"/>')
    # точка камеры на рамке
    o.append(f'<circle cx="{P(7, -325)[0]:.1f}" cy="{P(7, -325)[1]:.1f}" r="3" fill="#6f7a8c"/>')

    def to_world(lx, ly):
        return (ax + lx * sx, ay + ly * sy)
    return "".join(o), to_world


LINES = [230, 214, 236, 190, 224, 150, 232, 206, 120]
LINE_Y0, LINE_DY = 112, 15


def letter(hl=-1.0, dim=0.0, flash=0.0):
    """Письмо на экране: шапка почты, тема, отправитель, 9 строк-полосок без букв, кнопка. hl — какая строка подсвечена (дробная)."""
    o = ['<rect width="270" height="250" fill="#f4f7fb"/>',
         '<rect width="270" height="30" fill="#3f6fb5"/>']
    for j in range(3):
        o.append(f'<circle cx="{16 + j * 14}" cy="15" r="4.2" fill="#ffffff" opacity=".85"/>')
    o.append('<rect x="18" y="44" width="186" height="13" rx="6" fill="#2d3a52"/>')
    o.append('<circle cx="30" cy="82" r="13" fill="#e0a93a"/><circle cx="30" cy="78" r="4.4" fill="#fbe9c8"/><path d="M21 90 Q30 80 39 90Z" fill="#fbe9c8"/>')
    o.append('<rect x="52" y="73" width="92" height="7" rx="3.5" fill="#5a6a85"/><rect x="52" y="86" width="60" height="6" rx="3" fill="#9aa7bd"/>')
    if hl >= 0:
        i = int(math.floor(hl))
        fr = hl - i
        i = max(0, min(len(LINES) - 1, i))
        y = LINE_Y0 + i * LINE_DY
        w = LINES[i] * min(1.0, .15 + fr * .95 + .1)
        o.append(f'<rect x="14" y="{y - 5}" width="{w + 8:.1f}" height="16" rx="5" fill="#ffe27a" opacity=".95"/>')
    for i, w in enumerate(LINES):
        y = LINE_Y0 + i * LINE_DY
        o.append(f'<rect x="18" y="{y}" width="{w}" height="6.4" rx="3.2" fill="#76849d"/>')
    o.append('<rect x="18" y="226" width="64" height="18" rx="9" fill="#3f6fb5"/><rect x="30" y="233" width="40" height="4" rx="2" fill="#ffffff" opacity=".8"/>')
    if dim > 0:
        o.append(f'<rect width="270" height="250" fill="#2a3346" opacity="{dim:.3f}"/>')
    if flash > 0:
        o.append(f'<rect width="270" height="250" fill="#ffffff" opacity="{flash:.3f}"/>')
    return "".join(o)


def mug_on_desk(t, x=906.0, y=1122.0, k=.5):
    return den.mug(x, y, k, "#e0a93a", fill="coffee", steam_t=t)


def compose_day(world, cam, tone="noon", front="", set_ink=None):
    cx, cy, s, r = cam
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62
    g = lib.rad_grad([(0, "#0a0c1e", 0), (.62, "#0a0c1e", 0), (1, "#0a0c1e", .30)], 540, 900, 1180, 1400)
    return lib.svg('<rect width="1080" height="1920" fill="#4d6170"/>'
                   f'<g transform="{lib.cam(cx, cy, s, r)}">{world}{daylight(tone)}</g>' + front +
                   f'<rect width="1080" height="1920" fill="url(#{g})"/>')
