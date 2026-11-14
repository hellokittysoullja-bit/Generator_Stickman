"""Общие предметы рилса 58 «тревога» — ОДИН вид для групп A, B, C (владелец: «не рисуй свои»).

Подключение (в сцене группы, у которой рядом свой lib.py/ink.py):
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common")); import props
Функции возвращают строку SVG (мир кадра, 1080×1920), без собственной камеры. Единица k=1 — масштаб «Дима в полный рост»
(BS 0.6): ладонь Димы ≈ 47 px. На крупных планах предмет и кисть масштабируются ОДНИМ коэффициентом (k предмета = k кисти).
Все заливки сплошные (без полупрозрачных фигур), тушь — INK из lib, как у худи Димы. Букв и цифр нет нигде.

    paper_sheet(x, y, k, fill, rot, t, writing)  листок со страхами; (x, y) — ЦЕНТР листа; 4–8 строк-штрихов, fill 0–1; последняя пишется
    pen(x, y, k, rot)                  шариковая ручка; (x, y) — КОНЧИК пера, ось корпуса вверх (rot° по часовой); колпачок сзади
    desk(x, y, k, w, legs_to)          парта: (x, y) — середина ПЕРЕДНЕЙ кромки столешницы; ширина w (мир), ножки до legs_to
    ticket(x, y, k, rot)               экзаменационный билет, (x, y) — центр
    gradebook(x, y, k, rot, open_)     зачётка тёмно-синяя, (x, y) — центр; open_ 0…1 — раскрыта
    anx_cloud(x, y, k, kind, t)        тревожное облако: kind 0 мелкое, 1 среднее, 2 туча с молнией; (x, y) — центр
    bolt(x, y, k, rot)                 молния #F2C84B отдельно
    timer_circle(x, y, k, u, shake)    таймер-круг без цифр; u 0…1 — доля закрашенного сектора (с 12 часов по часовой)
    pocket(x, y, k)                    карман-кенгуру худи (накладной, тёмнее); (x, y) — центр кармана
Размеры при k=1: ладонь 47, листок 40×56 (длинная сторона ≈ 1,2 ладони), ручка 7×98, билет 44×62, зачётка 50×66, таймер Ø 120,
облако 70–150, парта: столешница толщиной 16, ножки 8 px.
Константы: C_PAPER, C_PEN, C_PEN_CAP, C_PEN_CLIP, C_DESK, C_DESK_END, C_DESK_LEG, C_TICKET, C_GRADE, C_CLOUD, C_BOLT, C_TIMER, C_SECTOR,
C_HOODIE, C_POCKET, PALM, SHEET_W, SHEET_H, PEN_L."""
import math

from lib import blob, ellipse_pts, f, line, mix, rect_pts, shape

C_PAPER = "#FBF8EE"
C_PAPER_SH = "#E9E3D0"
C_INK = "#2a2d30"
C_PEN = "#2F5FA8"
C_PEN_CAP = "#1F3F73"
C_PEN_CLIP = "#9AA0A6"
C_DESK = "#C99A62"
C_DESK_END = "#A87B47"
C_DESK_LEG = "#7A8288"
C_TICKET = "#E9E2CC"
C_TICKET_SH = "#D3CAAC"
C_GRADE = "#2C3E66"
C_GRADE_HI = "#3D548A"
C_CLOUD = "#6E6A8C"
C_CLOUD_SH = "#58547A"
C_CLOUD_HI = "#8A86A8"
C_BOLT = "#F2C84B"
C_TIMER = "#FFFFFF"
C_SECTOR = "#E8892B"
C_HOODIE = "#D9A93B"
C_POCKET = "#B88A22"
PALM = 47.0
SHEET_W, SHEET_H = 40.0, 56.0
PEN_L = 98.0


def _tf(inner, x, y, k, rot=0.0):
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k:.5f})">{inner}</g>'


# ───────────────────────── листок со страхами ─────────────────────────
def paper_sheet(x, y, k=1.0, fill=1.0, rot=0.0, t=0.0, writing=False, lines=6, seed=0, fold=0.0):
    """Листок 40×56 с N строками-штрихами цвета туши (без букв). fill 0–1 — сколько строк записано; последняя строка
    пишется на глазах (длина растёт). writing=True — рисуется «пером» (конец строки чуть темнее). fold 0–1 — сложен пополам (нижняя половина вверх)."""
    sd = 8200 + seed * 13
    lines = max(4, min(8, lines))
    W, H = SHEET_W, SHEET_H
    n_full = fill * lines
    o = []
    body = [(-W / 2, -H / 2, 1), (W / 2 - 1, -H / 2 + 1, 1), (W / 2, H / 2 - 1, 1), (-W / 2 + 1, H / 2, 1)]
    inner = blob([(W * .28, -H / 2), (W / 2, -H / 2), (W / 2, H / 2), (W * .1, H / 2)], C_PAPER_SH)    # тень справа
    top, bot = -H / 2 + 9, H / 2 - 7
    step = (bot - top) / (lines - 1)
    for i in range(lines):
        part = max(0.0, min(1.0, n_full - i))
        if part <= 0.02:
            continue
        y0 = top + i * step
        L = (W - 11) * (0.78 + 0.22 * math.sin(i * 2.3 + seed)) * part
        # неровный штрих: лёгкая волна, у каждой строки свой наклон
        pts = [(-W / 2 + 5, y0 + .6 * math.sin(i)), (-W / 2 + 5 + L * .35, y0 - .9 + 1.1 * math.sin(i * 1.7)),
               (-W / 2 + 5 + L * .7, y0 + .7 * math.cos(i * 1.3)), (-W / 2 + 5 + L, y0 + 1.0 * math.sin(i * .9))]
        inner += line(pts, 2.1, C_INK, taper=.2, wmin=.6, seed=sd + 20 + i, peak=.45)
    pap = shape(body, C_PAPER, inner, w=2.6, seed=sd)
    if fold > .01:
        # сложен: нижняя половина загнута вверх — виден край и тень сгиба
        pap = shape([(-W / 2, -H / 2, 1), (W / 2, -H / 2, 1), (W / 2, 0, 1), (-W / 2, 0, 1)], C_PAPER, blob(rect_pts(-W / 2, -4, W / 2, 0), C_PAPER_SH), w=2.6, seed=sd + 1)
    o.append(pap)
    return _tf("".join(o), x, y, k, rot)


# ───────────────────────── ручка ─────────────────────────
def pen(x, y, k=1.0, rot=0.0, cap_off=0.0):
    """Шариковая ручка: кончик пера в (x, y), корпус идёт вверх (локальная ось −y), rot° по часовой. Корпус #2F5FA8 ⌀7,
    колпачок #1F3F73 с зажимом #9AA0A6 надет сзади (cap_off 0 — надет, >0 — отведён вверх на cap_off px)."""
    sd = 8300
    Lb, Wd = PEN_L, 7.0
    o = []
    # корпус
    body = [(-Wd / 2, -Lb * .68, 1), (Wd / 2, -Lb * .68, 1), (Wd / 2, -9, 1), (Wd / 2 - 2.2, -4), (0.9, 0, 1), (-0.9, 0, 1), (-Wd / 2 + 2.2, -4), (-Wd / 2, -9, 1)]
    inner = blob([(Wd * .1, -Lb * .68), (Wd / 2, -Lb * .68), (Wd / 2, -9), (Wd / 2 - 2.2, -4), (Wd * .1, -4)], mix(C_PEN, "#000000", .22))
    inner += line([(-Wd / 2 + 1.5, -Lb * .66), (-Wd / 2 + 1.5, -16)], 1.5, "#8DB0E0", taper=.2, wmin=.8, seed=sd + 1, peak=.5)
    o.append(shape(body, C_PEN, inner, w=2.0, seed=sd))
    # колпачок на конце (зажим сбоку)
    c0 = -Lb * .68 - cap_off
    cap = [(-Wd / 2 - .6, c0 - Lb * .32, 1), (Wd / 2 + .6, c0 - Lb * .32, 1), (Wd / 2 + .6, c0, 1), (-Wd / 2 - .6, c0, 1)]
    ci = blob([(Wd * .1, c0 - Lb * .32), (Wd / 2 + .6, c0 - Lb * .32), (Wd / 2 + .6, c0), (Wd * .1, c0)], mix(C_PEN_CAP, "#000000", .25))
    o.append(shape(cap, C_PEN_CAP, ci, w=2.0, seed=sd + 2))
    o.append(shape(rect_pts(Wd / 2 - .4, c0 - Lb * .3, Wd / 2 + 2.6, c0 - 4, 1), C_PEN_CLIP, "", w=1.6, seed=sd + 3))
    # кончик
    o.append(blob([(-.9, -1), (.9, -1), (0, 2.5)], C_INK))
    return _tf("".join(o), x, y, k, rot)


# ───────────────────────── парта ─────────────────────────
def desk(x, y, k=1.0, w=520.0, legs_to=None, depth=44.0, seed=0):
    """Парта (вид спереди-сверху): светлое дерево #C99A62, торец #A87B47, металлические ножки #7A8288. (x, y) — середина ПЕРЕДНЕЙ кромки
    столешницы (там, где лежат локти); столешница уходит назад на depth·k вверх. w — ширина в мире (уже умножена на k).
    legs_to — Y пола (по умолчанию y + 330 k)."""
    sd = 8400 + seed * 9
    lt = legs_to if legs_to is not None else y + 330 * k
    hw = w / 2
    o = []
    # ножки (две, трубчатые, с перекладиной)
    for sx in (-1, 1):
        lx = x + sx * (hw - 26 * k)
        o.append(shape(rect_pts(lx - 4 * k, y + 14 * k, lx + 4 * k, lt, 1), C_DESK_LEG, blob(rect_pts(lx + 1 * k, y + 14 * k, lx + 4 * k, lt), mix(C_DESK_LEG, "#000000", .25)),
                       w=2.6 * k, seed=sd + 2 + sx))
        o.append(shape(rect_pts(lx - 11 * k, lt - 5 * k, lx + 11 * k, lt, 2), "#5F666C", "", w=2.4 * k, seed=sd + 6 + sx))
    o.append(shape(rect_pts(x - hw + 26 * k, y + 120 * k, x + hw - 26 * k, y + 128 * k, 1), C_DESK_LEG, "", w=2.4 * k, seed=sd + 8))
    # передняя панель-торец
    o.append(shape(rect_pts(x - hw, y, x + hw, y + 16 * k, 2), C_DESK_END, blob(rect_pts(x - hw, y + 10 * k, x + hw, y + 16 * k), mix(C_DESK_END, "#000000", .2)),
                   w=3.4 * k, seed=sd))
    # поверхность (трапеция уходит назад)
    top = [(x - hw, y, 1), (x + hw, y, 1), (x + hw - 20 * k, y - depth * k, 1), (x - hw + 20 * k, y - depth * k, 1)]
    ti = line([(x - hw * .7, y - depth * k * .35), (x + hw * .1, y - depth * k * .4)], 2.0 * k, mix(C_DESK, "#8a6538", .5), taper=.4, wmin=.5, seed=sd + 3, peak=.5)
    ti += line([(x - hw * .2, y - depth * k * .72), (x + hw * .8, y - depth * k * .66)], 2.0 * k, mix(C_DESK, "#8a6538", .5), taper=.4, wmin=.5, seed=sd + 4, peak=.5)
    ti += blob([(x + hw * .55, y), (x + hw, y), (x + hw - 20 * k, y - depth * k), (x + hw * .6, y - depth * k)], mix(C_DESK, "#8a6538", .25))
    o.append(shape(top, C_DESK, ti, w=3.4 * k, seed=sd + 1))
    return "".join(o)


# ───────────────────────── билет и зачётка ─────────────────────────
def ticket(x, y, k=1.0, rot=0.0, seed=0, lines=5):
    """Экзаменационный билет #E9E2CC: заголовочная полоса и штрихи-строки вместо текста, без букв."""
    sd = 8500 + seed * 9
    W, H = 44.0, 62.0
    body = [(-W / 2, -H / 2, 1), (W / 2, -H / 2 + 1, 1), (W / 2 - 1, H / 2, 1), (-W / 2 + 1, H / 2 - 1, 1)]
    inner = blob([(W * .3, -H / 2), (W / 2, -H / 2), (W / 2, H / 2), (W * .15, H / 2)], C_TICKET_SH)
    inner += blob(rect_pts(-W / 2 + 6, -H / 2 + 6, W / 2 - 6, -H / 2 + 13), "#7E8CB0")                  # полоса-заголовок
    inner += blob(ellipse_pts(W / 2 - 11, -H / 2 + 9.5, 3.2, 3.2, 8), "#C9503C")                       # печать-кружок (без цифр)
    for i in range(lines):
        yy = -H / 2 + 21 + i * 7.6
        L = (W - 14) * (0.95 - .22 * ((i * 5) % 3) / 2)
        inner += line([(-W / 2 + 6, yy), (-W / 2 + 6 + L, yy + .5 * math.sin(i))], 1.9, C_INK, taper=.15, wmin=.7, seed=sd + 5 + i, peak=.5)
    return _tf(shape(body, C_TICKET, inner, w=2.4, seed=sd), x, y, k, rot)


def gradebook(x, y, k=1.0, rot=0.0, open_=0.0, seed=0):
    """Зачётка: тёмно-синяя обложка #2C3E66 с золотой полосой-эмблемой (без букв). open_ 0…1 — раскрыта (виден разворот страниц)."""
    sd = 8600 + seed * 9
    W, H = 50.0, 66.0
    o = []
    if open_ > .02:
        ow = W * (1 + .95 * open_)
        cover = [(-ow / 2 - 3, -H / 2 - 2, 1), (ow / 2 + 3, -H / 2 - 2, 1), (ow / 2 + 3, H / 2 + 2, 1), (-ow / 2 - 3, H / 2 + 2, 1)]
        o.append(shape(cover, C_GRADE, "", w=2.6, seed=sd))
        for sgn in (-1, 1):
            pg = [(0, -H / 2 + 1, 1), (sgn * (ow / 2 - 1), -H / 2 + 2, 1), (sgn * (ow / 2 - 1), H / 2 - 1, 1), (0, H / 2 - 1, 1)]
            ln = "".join(line([(sgn * 4, -H / 2 + 12 + j * 9), (sgn * (ow / 2 - 6), -H / 2 + 12 + j * 9)], 1.7, C_INK, taper=.15, wmin=.7, seed=sd + 20 + j + (4 if sgn > 0 else 0))
                         for j in range(5))
            o.append(shape(pg, C_PAPER, ln, w=2.0, seed=sd + 3 + sgn))
    else:
        body = [(-W / 2, -H / 2, 1), (W / 2, -H / 2, 1), (W / 2, H / 2, 1), (-W / 2, H / 2, 1)]
        inner = blob(rect_pts(-W / 2, -H / 2, -W / 2 + 7, H / 2), mix(C_GRADE, "#000000", .3))        # корешок
        inner += blob([(W * .3, -H / 2), (W / 2, -H / 2), (W / 2, H / 2), (W * .2, H / 2)], mix(C_GRADE, "#000000", .15))
        inner += blob(rect_pts(-W / 2 + 12, -H / 2 + 12, W / 2 - 8, -H / 2 + 28, 2), "#D8B24A")        # эмблема: золотая плашка без букв
        inner += line([(-W / 2 + 14, -H / 2 + 36), (W / 2 - 10, -H / 2 + 36)], 1.8, C_GRADE_HI, taper=.1, wmin=.8, seed=sd + 2)
        inner += line([(-W / 2 + 14, -H / 2 + 42), (W / 2 - 16, -H / 2 + 42)], 1.8, C_GRADE_HI, taper=.1, wmin=.8, seed=sd + 3)
        o.append(shape(body, C_GRADE, inner, w=2.6, seed=sd))
    return _tf("".join(o), x, y, k, rot)


# ───────────────────────── тревожные облака ─────────────────────────
def _cloud_pts(rx, ry, n, seed, bump):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + bump * math.sin(i * 2.7 + seed) * .55 + (bump if i % 2 == 0 else -bump * .5)
        pts.append((rx * r * math.cos(a), ry * r * math.sin(a) * (.92 if math.sin(a) > 0 else 1.0)))
    return pts


def bolt(x, y, k=1.0, rot=0.0):
    """Молния #F2C84B: ломаный зигзаг, остриё вниз; (x, y) — верх."""
    pts = [(8, 0, 1), (-14, 40, 1), (-2, 40, 1), (-12, 84, 1), (18, 30, 1), (4, 30, 1)]
    return _tf(shape(pts, C_BOLT, blob([(4, 30), (18, 30), (-12, 84), (-4, 50)], mix(C_BOLT, "#B48A12", .3)), w=3.0, seed=8700), x, y, k, rot)


def anx_cloud(x, y, k=1.0, kind=1, t=0.0, seed=0, flash=0.0):
    """Тревожное облако серо-фиолетового цвета #6E6A8C с тушью. kind 0 — мелкое (⌀≈70), 1 — среднее (≈110), 2 — туча (≈150) с молнией;
    t — время, облако чуть дышит; flash 0…1 — молния вспыхивает (kind 2). На лице облака — хмурая складка (две чёрточки бровей)."""
    sd = 8800 + seed * 13 + kind * 3
    rx, ry = (36, 22) if kind == 0 else (56, 34) if kind == 1 else (78, 46)
    br = 1 + .035 * math.sin(t * 3.1 + seed)
    pts = [(p[0] * br, p[1] * (2 - br)) for p in _cloud_pts(rx, ry, 11 if kind else 9, seed, .13)]
    pts = [(p[0], p[1], 0) for p in pts]
    inner = blob([(-rx, ry * .25), (rx, ry * .25), (rx, ry * 1.3), (-rx, ry * 1.3)], C_CLOUD_SH)
    inner += blob(ellipse_pts(-rx * .3, -ry * .45, rx * .35, ry * .2, 10), C_CLOUD_HI)
    o = [shape(pts, C_CLOUD, inner, w=3.8 if kind else 3.2, seed=sd)]
    if kind >= 1:   # хмурые брови-штрихи
        s = rx / 56
        o.append(line([(-26 * s, -2 * s), (-8 * s, 6 * s)], 3.6 * s, C_INK, taper=.3, wmin=.7, seed=sd + 5))
        o.append(line([(26 * s, -2 * s), (8 * s, 6 * s)], 3.6 * s, C_INK, taper=.3, wmin=.7, seed=sd + 6))
    out = "".join(o)
    if kind == 2 and flash > .02:
        out = out + bolt(-6, ry * .55, .8 + .5 * flash, 6)
    return _tf(out, x, y, k)


# ───────────────────────── таймер-круг ─────────────────────────
def timer_circle(x, y, k=1.0, u=0.0, shake=0.0, seed=0):
    """Таймер: белый циферблат #FFFFFF, контур тушью, сектор #E8892B закрашивается с 12 часов по часовой, u 0…1. Без цифр: четыре
    деления и стрелка-обод. shake — дрожь в px (мир)."""
    sd = 8900 + seed
    R = 60.0
    u = max(0.0, min(1.0, u))
    o = []
    dial = ellipse_pts(0, 0, R, R, 28)
    inner = ""
    if u > .004:
        if u >= .996:
            inner += blob(ellipse_pts(0, 0, R - 5, R - 5, 28), C_SECTOR)
        else:
            n = max(3, int(40 * u) + 2)
            pts = [(0, 0)] + [((R - 5) * math.sin(2 * math.pi * u * i / n), -(R - 5) * math.cos(2 * math.pi * u * i / n)) for i in range(n + 1)]
            inner += blob(pts, C_SECTOR)
            # тень на закрашенной доле справа-снизу
            inner += line([(0, 0), (0, -(R - 5))], 3.2, mix(C_SECTOR, "#8a4a10", .5), taper=.1, wmin=.9, seed=sd + 9)
            a = 2 * math.pi * u
            inner += line([(0, 0), ((R - 5) * math.sin(a), -(R - 5) * math.cos(a))], 3.2, mix(C_SECTOR, "#8a4a10", .5), taper=.1, wmin=.9, seed=sd + 10)
    for i in range(4):       # деления
        a = math.pi / 2 * i
        inner += line([((R - 5) * math.sin(a), -(R - 5) * math.cos(a)), ((R - 14) * math.sin(a), -(R - 14) * math.cos(a))], 3.0, C_INK, taper=.1, wmin=.9, seed=sd + 20 + i)
    inner += blob(ellipse_pts(0, 0, 5, 5, 10), C_INK)
    o.append(shape(dial, C_TIMER, inner, w=4.4, seed=sd))
    # верхняя кнопка
    o.append(shape(rect_pts(-7, -R - 12, 7, -R + 1, 2), "#9AA0A6", "", w=2.6, seed=sd + 40))
    return _tf("".join(o), x + shake * math.sin(sd), y, k)


# ───────────────────────── карман ─────────────────────────
def pocket(x, y, k=1.0, depth=0.0, seed=0):
    """Накладной карман-кенгуру худи: #B88A22 на #D9A93B (фон — худи рисует сцена). Верхний край-вырез с тенью внутри, depth 0…1 —
    насколько внутри что-то (виден угол листка), (x, y) — центр кармана. Размер 100×60 (по Диме в полный рост)."""
    sd = 9000 + seed
    W, H = 100.0, 60.0
    body = [(-W / 2, -H / 2 + 8, 1), (-W * .22, -H / 2, 1), (W * .22, -H / 2, 1), (W / 2, -H / 2 + 8, 1), (W / 2 + 4, H / 2, 1), (-W / 2 - 4, H / 2, 1)]
    inner = blob([(W * .1, -H / 2), (W / 2, -H / 2 + 8), (W / 2 + 4, H / 2), (W * .15, H / 2)], mix(C_POCKET, "#000000", .15))
    inner += line([(-W * .4, H / 2 - 6), (W * .4, H / 2 - 6)], 2.0, mix(C_POCKET, "#6b4a12", .6), taper=.1, wmin=.8, seed=sd + 2)
    o = []
    if depth > .02:   # угол листка торчит из кармана (рисуется ДО кармана — карман закрывает низ)
        o.append(shape([(-8, -H / 2 + 3 - 18 * depth, 1), (16, -H / 2 + 3 - 18 * depth, 1), (16, -H / 2 + 12, 1), (-8, -H / 2 + 12, 1)], C_PAPER, "", w=1.8, seed=sd + 4))
    o.append(shape(body, C_POCKET, inner, w=3.2, seed=sd))
    return _tf("".join(o), x, y, k)
