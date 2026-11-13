"""Предметы сцены cat рилса 34: розовая коробка пончиков (откидная крышка, без надписей, 6 пончиков в 2 ряда), синяя
миска кота, жареная рыбка с хвостиком (и с укусом), крошки. Всё — в мировых координатах, (x, y) — низ-центр предмета,
k — масштаб. Манера та же: живая тушь, плоский цвет + одна тень."""
import math

import lib
from lib import INK, blob, clip_of, ellipse_pts, f, line, mix, shape, T

PINK, PINK_SH, PINK_L, PINK_D = "#f2a0b6", "#d47a96", "#f9c3d1", "#a9506c"
BLUE, BLUE_SH, BLUE_L, BLUE_IN = "#3d74c9", "#2a559e", "#7aa6e6", "#24467f"
FISH, FISH_SH, FISH_L, FISH_D = "#d98f3a", "#a9601e", "#f2bf6c", "#7a3f12"

# коробка: ширина 2*BW, передняя стенка FH, верх (крышка) — трапеция глубиной BD, задний край уже на BN
BW, FH, BD, BN, LIP = 260, 128, 118, 30, 24


# ─────────────────────────────── пончики (для щели под крышкой и открытой коробки)
def donut(x, y, r, glaze, sprinkles=True, seed=0):
    """Пончик сверху: тесто, глазурь волной, дырка, посыпка."""
    s = []
    s.append(shape(ellipse_pts(x, y, r, r * .62, 18), "#d9a25a", blob(ellipse_pts(x + r * .2, y + r * .2, r * .8, r * .4, 14), "#b9803e", .9),
                   w=3.2, seed=seed))
    gl = [(x + r * .84 * math.cos(a) + 3 * math.sin(a * 5 + seed), y + r * .52 * math.sin(a) + 2 * math.sin(a * 7 + seed))
          for a in [i * math.pi / 12 for i in range(24)]]
    inner = blob(ellipse_pts(x - r * .3, y - r * .2, r * .3, r * .12, 10), mix(glaze, "#ffffff", .45), .9)
    if sprinkles:
        cols = ["#ff5d73", "#ffd166", "#5ec4ff", "#7bd389", "#ffffff"]
        for i in range(10):
            a = i * 2.39 + seed
            rr = r * (.5 + .22 * ((i * 7) % 3) / 2)
            px, py = x + rr * math.cos(a), y + rr * .6 * math.sin(a)
            inner += line([(px - 4, py - 2), (px + 4, py + 2)], 3.4, cols[i % 5], taper=.05, wmin=.9, seed=seed + 40 + i)
    s.append(shape(gl, glaze, inner, w=3.0, seed=seed + 1))
    s.append(shape(ellipse_pts(x, y, r * .26, r * .17, 12), "#5a3418", "", w=2.8, seed=seed + 2))
    return "".join(s)


def box(x, y, k=1.0, lift=0.0, puff=0.0, seed=0):
    """Закрытая коробка пончиков. lift — на сколько (в px коробки) передний край крышки приподнят: щель, в ней пончики.
    puff 0..1 — облачко сахарной пудры из щели при хлопке."""
    def P(pts):
        return T(pts, x, y, k)
    s = []
    ytop = -FH
    yb = -FH - BD
    # тень под коробкой
    s.append(blob(P(ellipse_pts(14, 6, BW + 40, 22, 18)), "#2a1206", .3, lib.blur(7)))
    # тело: передняя стенка
    front = [(-BW, ytop, 1), (BW, ytop, 1), (BW, 0, 1), (-BW, 0, 1)]
    inner = blob(P([(BW - 70, ytop), (BW, ytop), (BW, 0), (BW - 70, 0)]), PINK_SH, .9)
    inner += line(P([(-BW + 30, -14), (BW - 30, -14)]), 2.4, PINK_D, seed=seed + 3, op=.55)
    s.append(shape(P(front), PINK, inner, w=4.6, seed=seed + 1))
    # щель: если крышка приподнята — тёмная внутренность и верх пончиков
    if lift > 0.5:
        gap = [(-BW + 4, ytop), (BW - 4, ytop), (BW - BN - 6, yb + 6), (-BW + BN + 6, yb + 6)]
        cg = clip_of(P(gap))
        dn = ""
        for row, (yy, rr) in enumerate(((-FH - 28, 52), (-FH - 70, 46))):
            for i in range(3):
                xx = (i - 1) * (150 - row * 18)
                dn += donut(*P([(xx, yy)])[0], rr * k, ["#f58fb0", "#7a4528", "#fbf3e6"][(i + row) % 3], True, seed=seed + 50 + i * 7 + row * 3)
        glow = lib.rad_grad([(0, "#fff2c0", .55), (1, "#fff2c0", 0)], *P([(0, ytop - 20)])[0], BW * k, 60 * k)
        s.append(f'<g clip-path="url(#{cg})">{blob(P(gap), "#5a2a3a")}{dn}'
                 f'<rect x="{f(x - BW * k)}" y="{f(y + (yb - 20) * k)}" width="{f(2 * BW * k)}" height="{f((BD + 40) * k)}" fill="url(#{glow})"/></g>')
    # крышка: задний край на петле, передний поднят на lift (в проекции — вверх)
    ly = ytop - lift
    lid = [(-BW + BN, yb, 1), (BW - BN, yb, 1), (BW + 4, ly, 1), (-BW - 4, ly, 1)]
    inner = blob(P([(BW - BN - 60, yb), (BW - BN, yb), (BW + 4, ly), (BW - 70, ly)]), mix(PINK_L, PINK_SH, .5), .85)
    inner += blob(P([(-BW + BN + 30, yb + 14), (-BW + BN + 150, yb + 14), (-BW + 130, ly - 16), (-BW + 20, ly - 16)]), "#fde0e8", .6)
    # продавленная линия-сгиб у петли и прорезь для язычка
    inner += line(P([(-BW + BN + 10, yb + 14), (BW - BN - 10, yb + 14)]), 2.6, PINK_D, seed=seed + 5, op=.5)
    s.append(shape(P(lid), PINK_L, inner, w=4.6, seed=seed + 2))
    # передний язычок крышки (заходит на переднюю стенку)
    lip = [(-BW - 4, ly, 1), (BW + 4, ly, 1), (BW + 2, ly + LIP, 1), (-BW - 2, ly + LIP, 1)]
    li = blob(P([(BW - 68, ly), (BW + 4, ly), (BW + 2, ly + LIP), (BW - 70, ly + LIP)]), PINK_SH, .9)
    li += blob(P(lib.rect_pts(-46, ly + 6, 46, ly + 16, 5)), PINK_D, .55)
    s.append(shape(P(lip), PINK, li, w=4.2, seed=seed + 4))
    if puff > 0.01:
        s.append(sugar_puff(*P([(0, ytop - 4)])[0], k, puff, seed))
    return "".join(s)


def lid_top(x, y, k=1.0):
    """Точка середины верха крышки (для кота, сидящего на коробке)."""
    return (x, y + (-FH - BD * 0.45) * k)


def sugar_puff(x, y, k, u, seed=0):
    """Облачко сахарной пудры из щели крышки: мелкие комочки разлетаются в стороны вдоль кромки и тают (уменьшаются)."""
    s = []
    for i in range(10):
        side = -1 if i % 2 else 1
        j = i // 2
        d = (40 + 46 * j) * k * lib.ease_out(u, 2.2)
        r = (7 + 3 * ((i * 5) % 3)) * k * (1 - u) ** 1.3
        if r < 1.0:
            continue
        px = x + side * (30 + j * 52) * k + side * d
        py = y - (8 + 14 * ((i * 3) % 4)) * k * lib.ease_out(u, 2) - 6 * k
        s.append(shape(ellipse_pts(px, py, r, r * .8, 10, jitter=.12, seed=seed + i), "#fffaf2", "", w=1.8 * min(1, r / (6 * k)),
                       seed=seed + 90 + i, ink_color="#cfc2b6"))
    return "".join(s)


# ─────────────────────────────── миска
BR, BRY, BH = 104, 30, 96          # радиус обода, полуось обода по y, высота миски


def bowl_back(x, y, k=1.0, seed=0):
    """Задняя часть: обод сверху и внутренность миски, тень на столе."""
    def P(pts):
        return T(pts, x, y, k)
    s = [blob(P(ellipse_pts(10, 4, BR * .95, 16, 16)), "#2a1206", .3, lib.blur(6))]
    inner = blob(P(ellipse_pts(0, -BH + 5, BR * .88, BRY * .74, 24)), BLUE_IN)
    inner += blob(P(ellipse_pts(-26, -BH + 10, BR * .5, BRY * .3, 16)), mix(BLUE_IN, "#ffffff", .15), .9)
    s.append(shape(P(ellipse_pts(0, -BH, BR, BRY, 28)), BLUE_L, inner, w=4.2, seed=seed + 1))
    return "".join(s)


def bowl_front(x, y, k=1.0, seed=0):
    """Передняя стенка миски (рисуется поверх рыбки и морды кота) и передняя половина обода."""
    def P(pts):
        return T(pts, x, y, k)
    s = []
    n = 14
    front_arc = [(BR * math.cos(a), -BH + BRY * math.sin(a)) for a in [i * math.pi / n for i in range(n + 1)]]
    body = [(BR, -BH, 1), (BR - 8, -BH + 40), (BR * .7, -6), (BR * .55, 0, 1), (-BR * .55, 0, 1), (-BR * .7, -6), (-BR + 8, -BH + 40),
            (-BR, -BH, 1)] + front_arc[::-1][1:-1]
    inner = blob(P([(BR * .35, -BH), (BR + 10, -BH), (BR, 4), (BR * .3, 4)]), BLUE_SH, .95)
    inner += line(P([(-BR * .74, -BH + 30), (-BR * .62, -26)]), 7, BLUE_L, seed=seed + 7, op=.9)
    # белая полоска-узор по стенке
    inner += line(P([(-BR + 12, -BH + 52), (-40, -BH + 62), (40, -BH + 62), (BR - 12, -BH + 52)]), 6, "#e9f0fb", taper=.05, wmin=.9,
                  seed=seed + 8, op=.95)
    s.append(shape(P(body), BLUE, inner, w=4.4, seed=seed + 2))
    return "".join(s)


def bowl(x, y, k=1.0, inside="", seed=0):
    return bowl_back(x, y, k, seed) + inside + bowl_front(x, y, k, seed)


# ─────────────────────────────── жареная рыбка
def fish(x, y, k=1.0, rot=0.0, bites=(), tail=0.0, seed=0):
    """Рыбка-жарёха: нос влево, хвост вправо; (x, y) — середина тела. bites — список (bx, by, r) в координатах рыбки:
    выкусы (край укуса с мякотью и тушью)."""
    s = []
    body = [(-92, 2), (-80, -22), (-44, -38), (8, -40), (52, -28), (78, -8), (78, 10), (52, 26), (8, 36), (-44, 34), (-80, 20)]
    tl = T([(70, -4), (112, -40), (130, -36), (116, -2, 1), (130, 34), (112, 40), (70, 6)], 0, 0, 1, tail, 72, 0)
    s.append(shape(tl, FISH, line(T([(84, 0), (118, -24)], 0, 0, 1, tail, 72, 0), 2.4, FISH_D, seed=seed + 3, op=.8) +
                   line(T([(84, 2), (118, 26)], 0, 0, 1, tail, 72, 0), 2.4, FISH_D, seed=seed + 4, op=.8), w=4, seed=seed + 2))
    s.append(shape([(-20, -38), (0, -58), (36, -52), (44, -30)], FISH_SH, "", w=3.6, seed=seed + 5))
    inner = blob([(-92, 6), (-40, 16), (40, 18), (80, 6), (80, 40), (-92, 40)], FISH_SH, .9)
    inner += blob([(-60, -28), (-10, -34), (40, -26), (-10, -22)], FISH_L, .85)
    for i in range(4):
        x0 = -40 + i * 28
        inner += line([(x0, -30), (x0 + 16, 22)], 4.2, FISH_D, taper=.4, wmin=.4, seed=seed + 10 + i, op=.8)
    inner += line([(-56, -26), (-60, 0), (-54, 24)], 3.0, FISH_D, seed=seed + 20, op=.85)
    mid = ""
    bites = list(bites)
    mk = ""
    if bites:
        mid_id = lib.uid("m")
        holes = "".join(f'<circle cx="{f(bx)}" cy="{f(by)}" r="{f(r)}" fill="black"/>' for bx, by, r in bites)
        lib.DEFS.append(f'<mask id="{mid_id}" maskUnits="userSpaceOnUse" x="-200" y="-200" width="400" height="400">'
                        f'<rect x="-200" y="-200" width="400" height="400" fill="white"/>{holes}</mask>')
        mk = f' mask="url(#{mid_id})"'
        cb = clip_of(body)
        for i, (bx, by, r) in enumerate(bites):
            ring = ellipse_pts(bx, by, r + 7, r + 7, 18)
            mid += f'<g clip-path="url(#{cb})"><circle cx="{f(bx)}" cy="{f(by)}" r="{f(r + 5)}" fill="#f6e3bf"/></g>'
            ink = lib.ink_closed(ellipse_pts(bx, by, r, r, 22), 3.6, seed=seed + 30 + i)
            mid += f'<g clip-path="url(#{cb})"><path d="{ink}" fill="{INK}"/></g>'
            _ = ring
    s.append(f'<g{mk}>' + shape(body, FISH, inner + mid, w=4.4, seed=seed + 1) + "</g>")
    # глаз — точка-крестик «жареный» (маленький, без белка)
    s.append(shape(ellipse_pts(-62, -8, 7, 7, 10), "#fbf3e0", "", w=2.6, seed=seed + 7))
    s.append(f'<circle cx="-62" cy="-8" r="2.6" fill="{INK}"/>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(k)})">{"".join(s)}</g>'


def bones(x, y, k=1.0, rot=0.0, seed=0):
    """Рыбий скелетик (съеденная рыбка): голова, хребет, рёбра, хвост."""
    s = []
    s.append(shape([(-92, 2), (-78, -22), (-56, -26), (-50, 2), (-56, 26), (-78, 22)], "#f2e6cc", blob([(-70, 6), (-50, 6), (-56, 26), (-78, 22)],
                                                                                                      "#d9c7a0", .9), w=3.6, seed=seed))
    s.append(f'<circle cx="-72" cy="-6" r="4" fill="{INK}"/>')
    s.append(line([(-50, 0), (70, 0)], 5, "#f2e6cc", taper=.05, wmin=.9, seed=seed + 1))
    s.append(line([(-50, 0), (70, 0)], 2.2, INK, taper=.05, wmin=.9, seed=seed + 2, op=.8))
    for i in range(6):
        xx = -34 + i * 18
        for sg in (-1, 1):
            s.append(line([(xx, 0), (xx + 8, sg * (22 - i * 2))], 3.2, mix("#f2e6cc", "#8a7a5a", .4), taper=.4, wmin=.4, seed=seed + 10 + i * 2 + (sg > 0)))
    s.append(shape([(70, -2), (104, -30), (114, -24), (100, 0, 1), (114, 24), (104, 30), (70, 2)], "#f2e6cc", "", w=3.4, seed=seed + 4))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(k)})">{"".join(s)}</g>'


def crumbs(x, y, k, u, seed=0, n=9):
    """Хрустящие крошки разлетаются от укуса: u — секунды после укуса (0..~0.7); падают по параболе, кувыркаются."""
    if u <= 0 or u > 0.8:
        return ""
    s = []
    for i in range(n):
        a = math.radians(-160 + i * 140 / (n - 1) + 9 * math.sin(i * 3.1 + seed))
        v = (330 + 90 * ((i * 7) % 4)) * k
        px = x + math.cos(a) * v * u
        py = y + math.sin(a) * v * u * .8 + 1300 * k * u * u
        r = (4.5 + 2 * (i % 3)) * k
        rot = u * 600 * (1 if i % 2 else -1) + i * 40
        col = FISH if i % 3 else FISH_SH
        s.append(shape(T([(-r, -r * .5), (r * .3, -r), (r, r * .2), (-r * .2, r * .8)], px, py, 1, rot), col, "", w=1.8 * k, seed=seed + 60 + i))
    return "".join(s)
