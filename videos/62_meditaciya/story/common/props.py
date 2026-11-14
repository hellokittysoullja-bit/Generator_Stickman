"""Общие предметы рилса 62 «медитация» — ОДИН вид для групп A…F (своих копий не рисовать). Автор — группа A.
Основа — props.py рилса 61 (всё оттуда осталось как было: glow, lamp_floor, window, shake, mug, idea_bulb, thought_cloud…),
сверху — предметы медитации и комедийные помощники (раздел МЕДИТАЦИЯ ниже, в конце файла).

Подключение:  sys.path.insert(0, ".../story/common"); import props
Все функции возвращают строку SVG (мир кадра 1080×1920), без своей камеры. (x, y) — ЦЕНТР ДНА предмета (если не сказано иначе).
Букв и цифр НИГДЕ нет. Заливки сплошные, без полупрозрачных фигур (кроме света glow/beam).

МЕДИТАЦИЯ (новое в 62):
  Комедийные кривые (возвращают числа):
    pop(t, t0, dur=None, amp=0.32, freq=2.4, damp=6.5)  → (sx, sy) пружинного выскока: до t0 (0, 0); потом масштаб с перелётом и
                                                  затуханием, сначала СЖАТИЕ по вертикали (sy < sx), потом вытяжка (sy > sx), отскок.
    squash(t, t0, amp=0.25, freq=3.0, damp=7.0)   → (sx, sy) удара/приземления: сплющивание (sy < 1, sx > 1) и отскок с затуханием;
                                                  до t0 (1, 1). Множить на масштаб предмета.
    hop(t, t0, h=60.0, dur=0.32)                  → dy подскока (отрицательный вверх) по параболе, 0 вне [t0, t0+dur]
    unpop(t, t0, dur=0.22)                        → масштаб исчезновения 1 → 0 (лёгкий вдох вверх перед исчезновением)
  Облака-мысли:
    cloud(x, y, w, h, sx, sy, seed, col, dots, inner, ink_w, anchor)
                                                  облако-мысль, (x, y) — ЦЕНТР ДНА облака (якорь сжатия — низ), три кружка-ступеньки
                                                  вниз к голове: dots = (dx, dy) — куда (относительно низа облака) идёт хвост к макушке
                                                  (None — без хвоста). inner — SVG внутри (координаты: центр облака = (0, 0)), режется по
                                                  облаку. sx, sy — из pop()/squash(). col по умолчанию белый.
    storm(x, y, w, h, sx, sy, seed, flash, inner) грозовая туча (ЦЕНТР ДНА), тёмно-серая, клубы; flash 0…1 — подсветка изнутри
    bolt(x0, y0, x1, y1, u, w, seed)              молния-штрих зигзагом от (x0,y0) к (x1,y1): u 0…1 — бьёт (рост), потом гаснет
                                                  (u > 1 — уже нет); жёлтая с тушью
    flash_screen(u, col)                          вспышка на весь кадр (сплошной цвет, прозрачность по u — это СВЕТ, не фигура)
    rain(x, y, w, t, t0, n, seed, k, floor)       крупные капли из полосы шириной w (низ тучи — y) после t0, падают до floor
    drop(x, y, k, rot, col)                       одна капля (ЦЕНТР), высота 40·k; голубая с бликом
    sweat(x, y, k, rot)                           капля пота (ЦЕНТР), высота 44·k
  Предметы:
    hourglass(x, y, k, rot, flow, top, t, seed)   песочные часы БЕЗ делений (ЦЕНТР), 150×250·k: rot — поворот (переворот 0→180);
                                                  top 0…1 — сколько песка сверху (остальное снизу); flow 0…1 — струя
    plate_soup(x, y, k, steam, t, seed)           тарелка супа с паром (дно по центру), Ø 220·k: морковь-кружки, зелень, пар-завитки
    cutlet_fork(x, y, k, rot, seed)               котлета на вилке (ЦЕНТР котлеты), вилка вниз при rot=0, длина 230·k
    iron(x, y, k, rot, smoke, t, seed)            утюг (дно по центру) 170×90·k, без значков и шкал; smoke 0…1 — дымок СПЛОШНЫМИ завитками
    ironing_board(x, y, k, w, seed)               гладильная доска (ЦЕНТР крышки), ширина w·k, ножки-крест
    smoke_curls(x, y, k, u, t, seed, col)         сплошные завитки дыма над точкой (u — высота/сила)
    mobilnik(x, y, k, rot)                        мобильник-силуэт (ЦЕНТР) 70×130·k: тёмный корпус, без экрана и букв
    cushion(x, y, k, sy, col, seed)               круглая подушка для медитации (дно по центру), Ø 300·k; sy — приплюснутость (squash)
    mat(x, y, k, w, col, seed)                    коврик (ЦЕНТР), w·k × 70·k в перспективе
    balloon(x, y, k, col, t, seed, string)        воздушный шарик (ЦЕНТР шара), r 60·k; string — длина нитки вниз; нитка колышется от t
    att_flame(x, y, k, t, u, seed)                огонёк-внимание (ЦЕНТР ОСНОВАНИЯ), высота 70·k, как огонёк на хвосте кота; u — размер
    mote(x, y, r, u)                              пылинка-точка со свечением (u — накал)
    breath_wave(x0, x1, y, amp, t, phase, w, col, n)
                                                  волна-лента дыхания от x0 до x1 по y: amp — размах, phase — сдвиг (живёт от t)
    dash_path(pts, u, w, col, gap)                пунктирная дорожка по точкам; u 0…1 — сколько проявлено
    torch(x, y, k, on, wall, seed)                торшер с небольшим ЧЁТКИМ кругом света у абажура (wall — цвет стены под кругом)
    legs_run(x, y, k, t, seed)                    две ножки-палочки с ботиночками (ЦЕНТР таза), бегут (для убегающей мысли)
"""
import math

import lib
from lib import blob, clamp, ellipse_pts, f, line, mix, rad_grad, lin_grad, rect_pts, rrect, shape, clip_rect, blur

C_PAGE = "#FBF3DC"
C_PAGE_SH = "#E6D9B8"
C_PAGE_LINE = "#9C927C"
C_BLUE_COVER = "#3F6FB0"
C_BLUE_COVER_SH = "#2D5389"
C_RED_COVER = "#C2493D"
C_RED_COVER_SH = "#8F3128"
C_QUILT = "#C8553D"
C_QUILT_SH = "#9A3B2B"
C_QUILT_HI = "#E27A5C"
C_QUILT_ST = "#F0C987"
C_BLUE = "#4A6FA5"
C_BLUE_SH = "#34507D"
C_BLUE_HI = "#6E92C9"
C_GREEN = "#5C9A78"
C_GREEN_SH = "#41735A"
C_GREEN_HI = "#7FBF98"
C_PILLOW = "#F2E6CF"
C_PILLOW_SH = "#D6C4A3"
C_WOOD = "#B27C4C"
C_WOOD_SH = "#8A5B32"
C_WOOD_HI = "#CE9A68"
C_LAMP = "#F4C24A"
C_LAMP_SH = "#C99726"
C_LIGHT = "#FFE7A3"
C_LIGHT_HOT = "#FFF6D8"
C_METAL = "#B5B9C2"
C_METAL_SH = "#868B96"
C_TORCH = "#D9483B"
C_TORCH_SH = "#A5322A"
C_NIGHT_WALL = "#20254A"
C_NIGHT_FLOOR = "#171A36"
C_NIGHT_DEEP = "#0F1229"
SKY_NIGHT = ("#0E1330", "#1E2756", "#33407A")
SKY_EVENING = ("#3B4C8C", "#7B7DB5", "#F2A86E")
SKY_DAY = ("#7FB8E8", "#B7DBF2", "#EAF4F8")


def _tf(inner, x, y, k=1.0, rot=0.0):
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k:.5f})">{inner}</g>'


def _grad_rect(x0, y0, x1, y1, stops):
    g = lin_grad([(o, c, 1) for o, c in stops], 0, 0, 0, 1)
    return f'<path d="M{f(x0)} {f(y0)}H{f(x1)}V{f(y1)}H{f(x0)}Z" fill="url(#{g})"/>'


# ───────────────────────────── книга ─────────────────────────────

def book_open(x, y, k=1.0, rot=0.0, flip=0.0, seed=0, cover=None):
    """Раскрытая книга, страницы к зрителю. Центр дна корешка — (x, y), ширина 200, высота 130. Строки — штрихи, букв нет."""
    sd = 6000 + seed * 13
    cov, covsh = (cover or C_BLUE_COVER), (C_BLUE_COVER_SH if (cover or C_BLUE_COVER) == C_BLUE_COVER else lib.mul(cover, (.72, .72, .72)))
    o = []
    # обложка выступает на 7 px
    o.append(shape([(-108, -6), (-2, 6, 1), (108, -6), (110, -128), (0, -118, 1), (-110, -128)], cov, "", w=4.0, seed=sd))
    # левая страница (рисунок: солнце, холм)
    lp = [(-2, 0, 1), (-98, -8), (-100, -122), (-2, -112, 1)]
    inner = blob(rect_pts(-110, -130, 0, 0), C_PAGE_SH)
    inner += blob(ellipse_pts(-52, -78, 28, 10, 14), "#88B87A")
    inner += blob(ellipse_pts(-70, -86, 7, 7, 10), "#F2B632")
    for j in range(3):
        inner += line([(-88, -28 + 7 * j), (-14 - 6 * (j % 2), -26 + 7 * j)], 3.0, C_PAGE_LINE, taper=.25, wmin=.6, seed=sd + 20 + j)
    o.append(shape(lp, C_PAGE, inner, w=3.4, seed=sd + 1))
    # правая страница; перелистывается: сжимается к корешку и уходит влево
    if flip < 0.999:
        o.append(shape([(2, 0, 1), (98, -8), (100, -122), (2, -112, 1)], C_PAGE_SH, "", w=3.4, seed=sd + 6))   # следующая страница под перелистываемой
        u = clamp(flip)
        if u < 0.5:
            wR = 96 * (1 - 2 * u) + 4
            lift = 14 * math.sin(math.pi * u * 2)
            rp = [(2, 0, 1), (2 + wR, -8 - lift * .3), (2 + wR + 2 * lift * .4, -122 - lift), (2, -112, 1)]
            inner = ""
            for j in range(9):
                yy = -102 + 10.5 * j
                a, b = 12, 12 + (70 - 9 * (j % 3) - 7 * (j % 2)) * (wR / 96)
                inner += line([(a, yy), (b, yy + 1.5)], 3.0, C_PAGE_LINE, taper=.2, wmin=.6, seed=sd + 30 + j)
            o.append(shape(rp, C_PAGE, inner, w=3.4, seed=sd + 2))
        else:
            wL = 96 * (2 * u - 1) + 4
            rp = [(-2, 0, 1), (-2 - wL, -8), (-2 - wL, -122), (-2, -112, 1)]
            o.append(shape(rp, C_PAGE_SH, "", w=3.4, seed=sd + 3))
            o.append(shape([(2, 0, 1), (98, -8), (100, -122), (2, -112, 1)], C_PAGE, "", w=3.4, seed=sd + 4))
    else:
        o.append(shape([(2, 0, 1), (98, -8), (100, -122), (2, -112, 1)], C_PAGE, "", w=3.4, seed=sd + 4))
    # блок страниц-срез по низу и корешковая щель
    o.append(line([(0, 3), (0, -112)], 3.2, C_PAGE_LINE, taper=.1, wmin=.7, seed=sd + 5, peak=.5))
    return _tf("".join(o), x, y, k, rot)


def book_back(x, y, k=1.0, rot=0.0, cover=None):
    """Раскрытая книга, обращённая к зрителю обложкой (её держит читающий): две створки V, корешок посередине, обрез страниц по верху."""
    cov = cover or C_BLUE_COVER
    covsh = lib.mul(cov, (.72, .72, .72))
    sd = 6200
    o = []
    # страницы-обрез сзади (видны над створками)
    o.append(shape([(-96, -128), (0, -122, 1), (96, -128), (98, -118), (0, -112, 1), (-98, -118)], C_PAGE, "", w=3.0, seed=sd))
    # левая и правая створки обложки
    o.append(shape([(0, 4, 1), (-92, -4), (-100, -112), (0, -108, 1)], cov, blob(rect_pts(-110, -60, 0, 10), covsh), w=4.0, seed=sd + 1))
    o.append(shape([(0, 4, 1), (92, -4), (100, -112), (0, -108, 1)], cov, blob(rect_pts(0, -112, 110, -80), lib.mul(cov, (1.12, 1.12, 1.12))), w=4.0, seed=sd + 2))
    # корешок
    o.append(line([(0, 6), (-1, -60), (0, -110)], 7.0, covsh, taper=.1, wmin=.8, seed=sd + 3))
    # рисунок на обложке: кружок и штрих — без букв
    o.append(blob(ellipse_pts(50, -56, 14, 14, 12), C_LAMP))
    o.append(line([(-80, -46), (-20, -50)], 4, C_QUILT_ST, taper=.2, wmin=.7, seed=sd + 5))
    return _tf("".join(o), x, y, k, rot)


def book_closed(x, y, k=1.0, rot=0.0, cover=None):
    cov = cover or C_RED_COVER
    covsh = lib.mul(cov, (.72, .72, .72))
    sd = 6300
    o = [shape(rrect(-75, -34, 75, 0, 5), cov, blob(rect_pts(-80, -8, 80, 2), covsh), w=3.6, seed=sd)]
    o.append(shape(rrect(-70, -26, 70, -8, 3), C_PAGE, "", w=2.6, seed=sd + 1))
    o.append(line([(-60, -17), (60, -17)], 1.8, C_PAGE_LINE, taper=.2, wmin=.7, seed=sd + 2))
    o.append(line([(-62, -30), (-62, -4)], 3.0, C_QUILT_ST, taper=.2, wmin=.6, seed=sd + 3))
    return _tf("".join(o), x, y, k, rot)


# ───────────────────────────── фонарик и свет ─────────────────────────────

def flashlight(x, y, k=1.0, rot=0.0, on=1.0):
    """Фонарик: центр корпуса (x, y); линза смотрит вправо при rot=0. Корпус 112×32, головка шире. on 0…1 — линза горит."""
    sd = 6400
    o = []
    o.append(shape(rrect(-62, -16, 36, 16, 8), C_TORCH, blob(rect_pts(-66, 4, 40, 20), C_TORCH_SH), w=3.6, seed=sd))
    for j in range(3):   # ребристая накладка
        o.append(line([(-36 + 11 * j, -13), (-36 + 11 * j, 13)], 2.4, C_TORCH_SH, taper=.2, wmin=.7, seed=sd + 5 + j))
    o.append(shape([(34, -16, 1), (52, -24), (60, -26, 1), (60, 26, 1), (52, 24), (34, 16, 1)], C_METAL, blob(rect_pts(30, 8, 64, 30), C_METAL_SH), w=3.6, seed=sd + 1))
    lens = lib.mix("#DDE6EC", C_LIGHT_HOT, clamp(on))
    o.append(shape(ellipse_pts(62, 0, 7, 23, 12), lens, "", w=3.0, seed=sd + 2))
    o.append(shape(rrect(-20, -22, 4, -15, 3), "#F2EDE4" if on < .5 else "#FFD36B", "", w=2.6, seed=sd + 3))   # клавиша
    o.append(shape(ellipse_pts(-62, 0, 5, 12, 10), C_TORCH_SH, "", w=2.6, seed=sd + 4))
    return _tf("".join(o), x, y, k, rot)


def beam(x, y, ang=0.0, length=700.0, spread=18.0, u=1.0, k=1.0, color=None, core=True):
    """Конус света из точки (x, y): ось под углом ang°, длина length, полный угол spread°; u — яркость 0…1. Класть поверх тёмного."""
    if u <= 0.003:
        return ""
    col = color or C_LIGHT
    r0 = 20 * k
    R = r0 + math.tan(math.radians(spread / 2)) * length
    g = lin_grad([(0, col, .95 * u), (.45, col, .5 * u), (1, col, 0)], 0, 0, 1, 0)
    gc = lin_grad([(0, C_LIGHT_HOT, .9 * u), (.6, C_LIGHT_HOT, .3 * u), (1, C_LIGHT_HOT, 0)], 0, 0, 1, 0)
    cone = f'<path d="M0 {f(-r0)}L{f(length)} {f(-R)}L{f(length)} {f(R)}L0 {f(r0)}Z" fill="url(#{g})" {blur(5)}/>'
    if core:
        cone += f'<path d="M0 {f(-r0 * .55)}L{f(length * .8)} {f(-R * .5)}L{f(length * .8)} {f(R * .5)}L0 {f(r0 * .55)}Z" fill="url(#{gc})" {blur(7)}/>'
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)})" style="mix-blend-mode:screen">{cone}</g>'


def glow(x, y, r=300.0, u=1.0, color=None, ry=None):
    """Тёплый круг света (центр (x, y)); класть поверх. Радиус r, яркость u."""
    if u <= 0.003:
        return ""
    col = color or C_LIGHT
    g = rad_grad([(0, col, .9 * u), (.35, col, .5 * u), (1, col, 0)], x, y, r, ry)
    return f'<path d="M{f(x - r)} {f(y - (ry or r))}h{f(2 * r)}v{f(2 * (ry or r))}h{f(-2 * r)}Z" fill="url(#{g})" style="mix-blend-mode:screen"/>'


def lamp_desk(x, y, k=1.0, on=1.0, tilt=0.0, seed=0):
    """Настольная лампа (дно в (x, y)): круглая база, шарнирная штанга, абажур-колокол. on — абажур светится."""
    sd = 6500 + seed
    o = [shape(ellipse_pts(0, -8, 54, 12, 16), C_METAL_SH, blob(ellipse_pts(0, -4, 40, 6, 12), "#6E727C"), w=3.2, seed=sd)]
    o.append(line([(0, -10), (-6, -70), (14, -128)], 10, C_METAL, taper=0.0, wmin=1.0, seed=sd + 1))
    o.append(shape(ellipse_pts(-6, -70, 8, 8, 8), C_METAL_SH, "", w=2.4, seed=sd + 2))
    head = [(-46, 22, 1), (-34, -28), (-12, -52, 1), (30, -52, 1), (50, -28), (62, 22, 1)]
    hc = mix(C_LAMP_SH, C_LAMP, clamp(on))
    inner = blob(rect_pts(-60, 8, 70, 30), mix("#8E6A18", C_LAMP_SH, clamp(on)))
    o.append(_tf(shape(head, hc, inner, w=3.6, seed=sd + 3) +
                 shape(ellipse_pts(8, 22, 54, 7, 14), mix("#E8D9A8", C_LIGHT_HOT, clamp(on)), "", w=2.6, seed=sd + 4), 14, -130, 1.0, tilt))
    return _tf("".join(o), x, y, k)


def lamp_floor(x, y, k=1.0, on=1.0, seed=0):
    """Торшер: тяжёлая база, тонкая ножка 330, абажур-цилиндр. Высота ≈ 390."""
    sd = 6600 + seed
    o = [shape(ellipse_pts(0, -9, 62, 13, 16), C_METAL_SH, blob(ellipse_pts(0, -5, 46, 6, 12), "#6E727C"), w=3.2, seed=sd)]
    o.append(shape([(-5, -10), (-5, -330), (5, -330), (5, -10)], C_METAL, blob(rect_pts(2, -340, 8, 0), C_METAL_SH), w=3.0, seed=sd + 1))
    hc = mix(C_LAMP_SH, C_LAMP, clamp(on))
    shade = [(-52, -330, 1), (-70, -388, 1), (70, -388, 1), (52, -330, 1)]
    inner = blob(rect_pts(-80, -345, 80, -325), mix("#8E6A18", C_LAMP_SH, clamp(on)))
    o.append(shape(shade, hc, inner, w=3.8, seed=sd + 2))
    o.append(shape(ellipse_pts(0, -330, 52, 7, 14), mix("#E8D9A8", C_LIGHT_HOT, clamp(on)), "", w=2.6, seed=sd + 3))
    return _tf("".join(o), x, y, k)


def wall_switch(x, y, k=1.0, on=0.0):
    sd = 6700
    o = [shape(rrect(-23, -35, 23, 35, 7), "#F1EDE4", blob(rect_pts(-25, 22, 25, 38), "#D6D0C2"), w=3.2, seed=sd)]
    o.append(shape(rrect(-10, -22, 10, 22, 4), "#DAD5C8", "", w=2.4, seed=sd + 1))
    ty = -14 if on > .5 else 14
    o.append(shape(rrect(-8, ty - 7, 8, ty + 7, 3), "#FFFFFF" if on > .5 else "#BDB7AA", "", w=2.2, seed=sd + 2))
    return _tf("".join(o), x, y, k)


# ───────────────────────────── постель ─────────────────────────────

_QUILT = {"quilt": (C_QUILT, C_QUILT_SH, C_QUILT_HI), "blue": (C_BLUE, C_BLUE_SH, C_BLUE_HI), "green": (C_GREEN, C_GREEN_SH, C_GREEN_HI)}


def blanket(x, y, k=1.0, w=360.0, h=170.0, seed=0, col="quilt", bump=1.0):
    """Бугор одеяла: дно по центру (x, y), ширина w, высота h·bump. Складки-дуги, стёжка, светлая кромка. Лёгкая асимметрия."""
    sd = 6800 + seed * 17
    c, csh, chi = _QUILT[col]
    hh = h * bump
    pts = [(-w / 2, 0, 1), (-w * .47, -hh * .35), (-w * .36, -hh * .7), (-w * .16, -hh * .95), (w * .06, -hh), (w * .26, -hh * .86),
           (w * .4, -hh * .55), (w * .49, -hh * .2), (w / 2, 0, 1)]
    inner = blob(rect_pts(-w, -hh * .5, w, 20), csh, op=1.0) if False else ""
    inner += blob([(-w / 2, 0), (w / 2, 0), (w * .5, -hh * .22), (0, -hh * .1), (-w * .5, -hh * .22)], csh)
    inner += blob([(-w * .45, -hh * .3), (-w * .3, -hh * .78), (-w * .12, -hh * .95), (-w * .2, -hh * .6), (-w * .38, -hh * .22)], chi)
    for i in range(3):   # стёжка: дуги
        yy = -hh * (.28 + .22 * i)
        inner += line([(-w * .34 + 8 * i, yy + 8), (0, yy - 10 - 5 * i), (w * .34 - 8 * i, yy + 6)], 2.6, csh, taper=.3, wmin=.5, seed=sd + 10 + i)
    for i in range(4):   # полосы узора
        xx = -w * .3 + w * .2 * i
        inner += line([(xx, -hh * .12), (xx + 6, -hh * (.7 + .05 * (i % 2)))], 7, C_QUILT_ST if col == "quilt" else mix(chi, "#FFFFFF", .4), taper=.2, wmin=.8, seed=sd + 20 + i)
    return _tf(shape(pts, c, inner, w=4.4, seed=sd), x, y, k)


def tent_inside(x, y, w=900.0, h=900.0, seed=0):
    """Тёмный купол одеяла изнутри (крупный план): центр нижней кромки (x, y). Складки-дуги, тёплые стёжки по куполу."""
    sd = 6900 + seed
    pts = [(x - w / 2, y, 1), (x - w * .5, y - h * .45), (x - w * .4, y - h * .8), (x - w * .15, y - h * .98), (x + w * .1, y - h), (x + w * .38, y - h * .85),
           (x + w * .5, y - h * .45), (x + w / 2, y, 1)]
    g = rad_grad([(0, "#8A3E34", 1), (.55, "#5D2B2E", 1), (1, "#2B1722", 1)], x - w * .05, y - h * .4, w * .62, h * .7)
    inner = f'<path d="M{f(x - w)} {f(y - h * 1.1)}h{f(2 * w)}v{f(h * 1.3)}h{f(-2 * w)}Z" fill="url(#{g})"/>'
    for i in range(5):
        a = -w * .4 + w * .2 * i
        inner += line([(x + a * .9, y), (x + a * .55, y - h * .5), (x + a * .3, y - h * .92)], 4.0, "#27131E", taper=.5, wmin=.3, seed=sd + 5 + i, op=.55)
    return shape(pts, "#5D2B2E", inner, w=5.0, seed=sd)


def pillow(x, y, k=1.0, rot=0.0, col=None, seed=0):
    sd = 7000 + seed
    c = col or C_PILLOW
    csh = lib.mul(c, (.86, .84, .8))
    pts = [(-92, -10, 1), (-96, -38), (-70, -62), (-20, -70), (40, -66), (86, -56), (98, -30), (92, -8, 1), (30, 2), (-40, 2)]
    inner = blob([(-100, -16), (100, -16), (100, 8), (-100, 8)], csh)
    inner += line([(-80, -44), (-30, -58), (30, -56)], 4, mix(c, "#FFFFFF", .6), taper=.4, wmin=.4, seed=sd + 1)
    return _tf(shape(pts, c, inner, w=3.8, seed=sd), x, y, k, rot)


def bed(x, y, k=1.0, seed=0):
    """Кровать сбоку: ножки стоят на (x, y), изголовье слева (x − 280), спинка справа низкая. Матрас сверху на y − 118·k.
    Постель (подушку, одеяло) ставит сцена на y − 118·k."""
    sd = 7100 + seed
    o = []
    o.append(shape([(-278, -2), (-262, -2), (-262, -150), (-278, -150)], C_WOOD_SH, "", w=3.0, seed=sd))     # ножки
    o.append(shape([(262, -2), (278, -2), (278, -110), (262, -110)], C_WOOD_SH, "", w=3.0, seed=sd + 1))
    o.append(shape(rrect(-288, -330, -246, -92, 8), C_WOOD, blob(rect_pts(-250, -330, -240, -92), C_WOOD_SH), w=4.0, seed=sd + 2))   # изголовье
    o.append(shape(rrect(-286, -104, 284, -70, 6), C_WOOD, blob(rect_pts(-290, -78, 290, -66), C_WOOD_SH), w=4.0, seed=sd + 3))     # рама
    o.append(shape(rrect(-262, -126, 282, -96, 10), "#EFE9DA", blob(rect_pts(-270, -104, 290, -90), "#CFC7B3"), w=3.6, seed=sd + 4))  # матрас
    o.append(shape(rrect(258, -190, 290, -70, 7), C_WOOD, "", w=3.6, seed=sd + 5))      # низкая спинка
    return _tf("".join(o), x, y, k)


# ───────────────────────────── небо, луна, окно ─────────────────────────────

def moon(x, y, r=42.0, halo=1.0):
    g = rad_grad([(0, "#FFF5CF", .55 * halo), (1, "#FFF5CF", 0)], x, y, r * 3.0)
    o = f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 3)}" fill="url(#{g})"/>'
    o += shape(ellipse_pts(x, y, r, r, 18), "#FBF1C8", blob(ellipse_pts(x + r * .45, y - r * .1, r * .88, r * .95, 18), "#E5D9A5"), w=2.4, seed=7201)
    return o


def star4(x, y, r=10.0, u=1.0):
    if u <= 0.01:
        return ""
    r = r * (.5 + .5 * clamp(u))
    return blob([(x, y - r, 1), (x + r * .22, y - r * .22), (x + r, y, 1), (x + r * .22, y + r * .22), (x, y + r, 1), (x - r * .22, y + r * .22), (x - r, y, 1),
                 (x - r * .22, y - r * .22)], "#FFF3C4")


def window(x, y, w=520.0, h=640.0, mode="night", t=0.0, seed=0, far=False, curtain=True):
    """Окно (центр дна рамы (x, y)). Вид: night — тёмное небо, луна, звёзды (мерцают с t); evening — синий вечер с тёплой полосой на горизонте;
    day. far=True — даль: три ряда холмов, горизонт и дорога (для «смотреть вдаль»). Рама 16 px, крестовина."""
    sd = 7300 + seed
    fr = 18
    x0, y0, x1, y1 = x - w / 2, y - h, x + w / 2, y
    snow = mode == "snow"
    if snow:
        mode = "day"
    sky = ("#C9D9E8", "#DCE7F0", "#EEF3F6") if snow else {"night": SKY_NIGHT, "evening": SKY_EVENING, "day": SKY_DAY}[mode]
    ix0, iy0, ix1, iy1 = x0 + fr, y0 + fr, x1 - fr, y1 - fr
    g = lin_grad([(0, sky[0], 1), (.55, sky[1], 1), (1, sky[2], 1)], 0, 0, 0, 1)
    inner = f'<path d="M{f(ix0)} {f(iy0)}H{f(ix1)}V{f(iy1)}H{f(ix0)}Z" fill="url(#{g})"/>'
    if mode == "night":
        for i in range(9):
            sx = ix0 + 40 + (i * 97 + sd) % int(w - 90)
            sy = iy0 + 30 + (i * 61 + sd // 3) % int(h * .5)
            inner += star4(sx, sy, 7 + (i % 3) * 2, .6 + .4 * math.sin(t * 2.2 + i * 1.7))
        inner += moon(x1 - w * .28, iy0 + h * .2, w * .075)
    if snow:   # Миннесота: сугробы, ёлки, падающий снег (живёт от t)
        hz = iy0 + (iy1 - iy0) * .62
        for j in range(5):
            ex = ix0 + (ix1 - ix0) * (.1 + .2 * j) + 10 * math.sin(j * 2.3 + sd)
            eh = (iy1 - iy0) * (.2 + .06 * (j % 3))
            pts = [(ex, hz - eh, 1), (ex + eh * .32, hz + 4, 1), (ex - eh * .32, hz + 4, 1)]
            inner += shape(pts, "#3E7A5A", line([(ex - eh * .18, hz - eh * .45), (ex + eh * .16, hz - eh * .42)], 4, "#FFFFFF", taper=.3, wmin=.4, seed=sd + 40 + j), w=3.0, seed=sd + 30 + j)
        sp = [(ix0 - 10, iy1 + 10, 1)] + [(ix0 + (ix1 - ix0) * i / 8, hz + 6 + 10 * math.sin(i * 1.4)) for i in range(9)] + [(ix1 + 10, iy1 + 10, 1)]
        inner += blob(sp, "#FFFFFF")
        for i in range(26):
            fx = ix0 + ((i * 53 + sd) % int(w - 40)) + 14 * math.sin(t * 1.3 + i)
            fy = iy0 + ((i * 71 + t * 60 + sd) % (iy1 - iy0))
            inner += blob(ellipse_pts(fx, fy, 3.2, 3.2, 6), "#FFFFFF")
    if far:
        hz = iy0 + (iy1 - iy0) * .52
        cols = {"night": ("#2A3568", "#222B58", "#1A2248"), "evening": ("#6A78AE", "#4D5B93", "#35457A"), "day": ("#A9D3A0", "#7FBB7F", "#5DA064")}[mode]
        for j, (cc, amp, off) in enumerate(zip(cols, (22, 30, 38), (0, 60, 130))):
            pts = [(ix0 - 10, iy1 + 10, 1)]
            for i in range(13):
                xx = ix0 - 10 + (w + 20) * i / 12
                pts.append((xx, hz + off * .55 + 14 * j - amp * math.sin(i * 0.9 + j * 1.8 + sd * .1)))
            pts.append((ix1 + 10, iy1 + 10, 1))
            inner += blob(pts, cc)
        if mode in ("evening", "day"):
            inner += line([(ix0 + w * .4, iy1), (ix0 + w * .47, hz + 40), (ix0 + w * .5, hz + 8)], 12, mix(cols[1], "#F6E3C0", .55), taper=.9, wmin=.1, seed=sd + 7, peak=.2)
    out = [shape(rect_pts(x0, y0, x1, y1), "#EDE6D8", "", w=4.4, seed=sd, ink=True)]
    out.append(shape(rect_pts(ix0, iy0, ix1, iy1), sky[1], inner, w=3.4, seed=sd + 1))
    out.append(blob(rect_pts(x - 6, iy0, x + 6, iy1), "#EDE6D8") + line([(x - 6, iy0), (x - 6, iy1)], 2.6, lib.INK, seed=sd + 2) + line([(x + 6, iy0), (x + 6, iy1)], 2.6, lib.INK, seed=sd + 3))
    out.append(blob(rect_pts(ix0, iy0 + (iy1 - iy0) * .46 - 6, ix1, iy0 + (iy1 - iy0) * .46 + 6), "#EDE6D8") +
               line([(ix0, iy0 + (iy1 - iy0) * .46 - 6), (ix1, iy0 + (iy1 - iy0) * .46 - 6)], 2.6, lib.INK, seed=sd + 4) +
               line([(ix0, iy0 + (iy1 - iy0) * .46 + 6), (ix1, iy0 + (iy1 - iy0) * .46 + 6)], 2.6, lib.INK, seed=sd + 5))
    out.append(shape(rrect(x0 - 26, y1, x1 + 26, y1 + 22, 5), "#DCD3C0", blob(rect_pts(x0 - 30, y1 + 12, x1 + 30, y1 + 26), "#B9AF98"), w=3.4, seed=sd + 6))
    if curtain:
        cc = {"night": "#4B3B6E", "evening": "#6E4F7A", "day": "#E9B96A"}[mode]
        for sgn, cx in ((-1, x0 - 4), (1, x1 + 4)):
            pts = [(cx - sgn * 4, y0 - 20, 1), (cx + sgn * 78, y0 - 12), (cx + sgn * 66, y1 * .6 + y0 * .4), (cx + sgn * 84, y1 + 14, 1), (cx - sgn * 6, y1 + 14, 1)]
            out.append(shape(pts, cc, line([(cx + sgn * 30, y0), (cx + sgn * 40, y1)], 5, lib.mul(cc, (.78, .78, .78)), taper=.4, wmin=.3, seed=sd + 8 + int(sgn + 1))
                             + line([(cx + sgn * 56, y0), (cx + sgn * 60, y1)], 4, lib.mul(cc, (1.2, 1.2, 1.2)), taper=.4, wmin=.3, seed=sd + 11 + int(sgn + 1)), w=3.4, seed=sd + 9 + int(sgn + 1)))
    return "".join(out)


# ───────────────────────────── ночь: затемнение с «дырами» света ─────────────────────────────

def cone_d(x, y, ang=0.0, length=700.0, spread=18.0, r0=20.0):
    """Контур конуса света (строка d пути): из точки (x, y), ось ang°, полный угол spread°, у линзы полуширина r0."""
    R = r0 + math.tan(math.radians(spread / 2)) * length
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    pts = [(0, -r0), (length, -R), (length, R), (0, r0)]
    q = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]
    return "M" + "L".join(f"{f(px)} {f(py)}" for px, py in q) + "Z"


def circle_d(x, y, r, ry=None):
    ry = r if ry is None else ry
    return f"M{f(x - r)} {f(y)}a{f(r)} {f(ry)} 0 1 0 {f(2 * r)} 0a{f(r)} {f(ry)} 0 1 0 {f(-2 * r)} 0Z"


def darkness(op=0.62, color="#0A0E26", holes=(), blur_sd=14.0, box=(0, 0, 1080, 1920)):
    """Ночное затемнение поверх ВСЕЙ нарисованной сцены: тёмная вуаль op с мягкими вырезами света (holes — список (d, сила 0…1) или d).
    Освещённое видно в своих цветах с тушью (вуаль, а не screen: тушь не выцветает). Поверх кладут beam()/glow() тёплым цветом."""
    x0, y0, x1, y1 = box
    mid = lib.uid("mk")
    cut = ""
    for h in holes:
        d, a = (h if isinstance(h, tuple) else (h, 1.0))
        cut += f'<path d="{d}" fill="#000" opacity="{a:.3f}" {blur(blur_sd)}/>'
    lib.DEFS.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}">'
                    f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#fff"/>{cut}</mask>')
    return f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{color}" opacity="{op:.3f}" mask="url(#{mid})"/>'


# ═════════════════════════════ стол-бардак (рилс 61) ═════════════════════════════

C_CABLE = "#3A3D44"
C_CABLE_HI = "#5E636D"
C_DESK_WHITE = "#EDE8DE"
C_DESK_WHITE_SH = "#CFC7B8"
MUG_COLS = {"red": ("#D0553F", "#9E3A2A", "#E9836C"), "blue": ("#4F78B5", "#36588C", "#79A0D6"), "green": ("#5E9E78", "#43785A", "#86C29E"),
            "white": ("#F3EFE6", "#CFC8BA", "#FFFFFF"), "yellow": ("#EDB742", "#BE8B22", "#F7D27A")}
C_COFFEE = "#5A3A26"
C_GREEN_OK = "#2FA45A"


def _rs(seed):
    import random
    return random.Random(seed)


def shake(t, t0, amp=10.0, dur=0.35, seed=0):
    """(dx, dy) затухающей тряски после t0 (до t0 — ноль)."""
    u = t - t0
    if u < 0 or u > dur:
        return 0.0, 0.0
    e = (1 - u / dur) ** 2
    return (amp * e * math.sin(u * 71 + seed), amp * e * math.cos(u * 57 + seed * 1.7))


def desk(x, y, w=900.0, k=1.0, depth=170.0, legs=True, col="wood", seed=0, leg_h=300.0):
    """Стол: (x, y) — центр переднего края крышки; видна поверхность глубиной depth (вверх, в перспективе уже на 6 %), торец 26 px,
    ножки leg_h вниз. Возвращает SVG; верх поверхности — y − depth."""
    sd = 8000 + seed
    c, csh, chi = (C_WOOD, C_WOOD_SH, C_WOOD_HI) if col == "wood" else (C_DESK_WHITE, C_DESK_WHITE_SH, "#FAF7F0")
    hw = w / 2
    o = []
    if legs:
        for sx in (-1, 1):
            lx = sx * (hw - 46)
            o.append(shape(rect_pts(lx - 17, 20, lx + 17, 20 + leg_h), csh, blob(rect_pts(lx + 4, 20, lx + 20, 20 + leg_h), lib.mul(csh, (.82, .82, .82))),
                           w=3.6, seed=sd + 1 + sx))
        o.append(shape(rect_pts(-hw + 60, 26, hw - 60, 50), lib.mul(csh, (.86, .86, .86)), "", w=3.0, seed=sd + 4))
    top = [(-hw, 0, 1), (-hw * .94, -depth, 1), (hw * .94, -depth, 1), (hw, 0, 1)]
    inner = ""
    rs = _rs(sd)
    if col == "wood":
        for j in range(5):   # волокна дерева
            yy = -depth * (.15 + .17 * j) + rs.uniform(-6, 6)
            x0 = -hw * .9 + rs.uniform(0, 120)
            inner += line([(x0, yy), (x0 + rs.uniform(180, 380), yy + rs.uniform(-4, 4))], 2.6, chi, taper=.4, wmin=.3, seed=sd + 10 + j)
    inner += blob(rect_pts(-hw, -14, hw, 2), lib.mul(c, (.94, .94, .94)))
    o.append(shape(top, c, inner, w=4.2, seed=sd + 5))
    o.append(shape(rect_pts(-hw, 0, hw, 26), csh, blob(rect_pts(-hw, 16, hw, 28), lib.mul(csh, (.85, .85, .85))), w=4.0, seed=sd + 6))
    return _tf("".join(o), x, y, k)


def _icon(kind, cx, cy, s, col, sd):
    """Значок наброска без букв: кружок, звезда, стрелка, домик, волна, спираль, ракета, график, рожица."""
    o = ""
    if kind == "circle":
        o += line(ellipse_pts(cx, cy, 16 * s, 15 * s, 14) + [(cx + 16 * s, cy + 3 * s)], 3 * s, col, taper=.3, wmin=.4, seed=sd)
    elif kind == "star":
        pts = []
        for i in range(11):
            a = -math.pi / 2 + i * math.pi / 5
            r = (17 if i % 2 == 0 else 7) * s
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        o += line(pts, 3 * s, col, taper=.2, wmin=.5, seed=sd)
    elif kind == "arrow":
        o += line([(cx - 20 * s, cy + 8 * s), (cx, cy - 2 * s), (cx + 20 * s, cy - 10 * s)], 3 * s, col, taper=.3, wmin=.5, seed=sd)
        o += line([(cx + 10 * s, cy - 16 * s), (cx + 21 * s, cy - 10 * s), (cx + 13 * s, cy)], 3 * s, col, taper=.3, wmin=.5, seed=sd + 1)
    elif kind == "house":
        o += line([(cx - 16 * s, cy + 14 * s), (cx - 16 * s, cy - 2 * s), (cx, cy - 16 * s), (cx + 16 * s, cy - 2 * s), (cx + 16 * s, cy + 14 * s), (cx - 16 * s, cy + 14 * s)],
                  3 * s, col, taper=.15, wmin=.6, seed=sd)
        o += line([(cx - 4 * s, cy + 14 * s), (cx - 4 * s, cy + 4 * s), (cx + 4 * s, cy + 4 * s), (cx + 4 * s, cy + 14 * s)], 2.4 * s, col, taper=.2, wmin=.6, seed=sd + 1)
    elif kind == "wave":
        o += line([(cx - 22 * s + 4.4 * s * i, cy + 7 * s * math.sin(i * 1.2)) for i in range(11)], 3 * s, col, taper=.3, wmin=.4, seed=sd)
    elif kind == "spiral":
        o += line([(cx + (1.6 * s * a) * math.cos(a), cy + (1.6 * s * a) * math.sin(a)) for a in [i * .35 for i in range(36)]], 3 * s, col, taper=.4, wmin=.3, seed=sd)
    elif kind == "rocket":
        o += line([(cx, cy - 20 * s), (cx + 8 * s, cy - 6 * s), (cx + 8 * s, cy + 12 * s), (cx - 8 * s, cy + 12 * s), (cx - 8 * s, cy - 6 * s), (cx, cy - 20 * s)], 3 * s, col,
                  taper=.15, wmin=.6, seed=sd)
        o += line([(cx - 8 * s, cy + 6 * s), (cx - 15 * s, cy + 16 * s), (cx - 8 * s, cy + 14 * s)], 2.6 * s, col, taper=.2, wmin=.5, seed=sd + 1)
        o += line([(cx + 8 * s, cy + 6 * s), (cx + 15 * s, cy + 16 * s), (cx + 8 * s, cy + 14 * s)], 2.6 * s, col, taper=.2, wmin=.5, seed=sd + 2)
    elif kind == "graph":
        o += line([(cx - 18 * s, cy - 16 * s), (cx - 18 * s, cy + 14 * s), (cx + 20 * s, cy + 14 * s)], 2.6 * s, col, taper=.15, wmin=.6, seed=sd)
        o += line([(cx - 14 * s, cy + 8 * s), (cx - 4 * s, cy - 2 * s), (cx + 4 * s, cy + 4 * s), (cx + 16 * s, cy - 12 * s)], 3 * s, "#C8553D", taper=.2, wmin=.5, seed=sd + 1)
    elif kind == "face":
        o += line(ellipse_pts(cx, cy, 16 * s, 16 * s, 14) + [(cx + 16 * s, cy + 2 * s)], 3 * s, col, taper=.3, wmin=.4, seed=sd)
        o += blob(ellipse_pts(cx - 6 * s, cy - 4 * s, 2.2 * s, 2.6 * s, 8), col) + blob(ellipse_pts(cx + 6 * s, cy - 4 * s, 2.2 * s, 2.6 * s, 8), col)
        o += line([(cx - 8 * s, cy + 5 * s), (cx, cy + 10 * s), (cx + 8 * s, cy + 5 * s)], 2.4 * s, col, taper=.3, wmin=.5, seed=sd + 1)
    return o


def paper(x, y, k=1.0, rot=0.0, w=120.0, h=160.0, seed=0, kind="lines", sy=1.0, col=None, bend=0.0, corner=True):
    """Лист, ЦЕНТР (x, y). kind: lines | sketch | blank | grid. sy — сплющивание (лежит на столе). bend — изгиб в полёте."""
    sd = 8100 + seed * 7
    rs = _rs(sd)
    pc = col or C_PAGE
    hw, hh = w / 2, h / 2
    b = bend * 0.18 * w
    cs = 16 if corner and kind != "blank" else 0
    pts = [(-hw, -hh, 1), (0, -hh + b * .5), (hw - cs, -hh + b * .1, 1)]
    if cs:
        pts += [(hw, -hh + cs, 1)]
    pts += [(hw + b * .25, 0), (hw, hh, 1), (0, hh + b * .5), (-hw, hh, 1), (-hw - b * .25, 0)]
    inner = blob(rect_pts(-hw - 10, hh - 14, hw + 10, hh + 10), lib.mul(pc, (.94, .93, .9)))
    lc = C_PAGE_LINE
    if kind == "lines":
        n = max(3, int((h - 40) / 18))
        for j in range(n):
            yy = -hh + 24 + 18 * j
            ln = rs.uniform(.45, .85) * (w - 34)
            inner += line([(-hw + 16, yy), (-hw + 16 + ln, yy + rs.uniform(-1.5, 1.5))], 3.2, lc, taper=.25, wmin=.55, seed=sd + 20 + j)
    elif kind == "grid":
        for j in range(1, 6):
            inner += line([(-hw + 8, -hh + h * j / 6), (hw - 8, -hh + h * j / 6)], 1.6, "#B8C4D6", taper=.1, wmin=.8, seed=sd + 30 + j)
        for j in range(1, 5):
            inner += line([(-hw + w * j / 5, -hh + 8), (-hw + w * j / 5, hh - 8)], 1.6, "#B8C4D6", taper=.1, wmin=.8, seed=sd + 40 + j)
        inner += _icon("graph", 0, 0, w / 90, "#3D4A66", sd + 50)
    elif kind == "sketch":
        kinds = ["circle", "star", "arrow", "house", "wave", "spiral", "rocket", "face"]
        a, bb = rs.sample(kinds, 2)
        inner += _icon(a, -hw * .35, -hh * .35, w / 110, "#3D4A66", sd + 60)
        inner += _icon(bb, hw * .3, hh * .25, w / 120, "#C8553D", sd + 61)
        inner += line([(-hw + 16, hh - 30), (-hw + 16 + w * .45, hh - 31)], 3.0, lc, taper=.25, wmin=.55, seed=sd + 62)
    o = shape(pts, pc, inner, w=3.4, seed=sd)
    if cs:   # загнутый уголок
        o += shape([(hw - cs, -hh + b * .1, 1), (hw - cs + 2, -hh + cs - 2, 1), (hw, -hh + cs, 1)], C_PAGE_SH, "", w=2.6, seed=sd + 3)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k:.5f} {k * sy:.5f})">{o}</g>'


def paper_ball(x, y, k=1.0, rot=0.0, seed=0):
    sd = 8200 + seed
    rs = _rs(sd)
    pts = [(22 * (1 + rs.uniform(-.18, .12)) * math.cos(a), 21 * (1 + rs.uniform(-.18, .12)) * math.sin(a), i % 3 == 0)
           for i, a in enumerate([j * 2 * math.pi / 11 for j in range(11)])]
    pts = [(p[0], p[1], 1) if p[2] else (p[0], p[1]) for p in pts]
    inner = blob(ellipse_pts(6, 8, 18, 14, 10), C_PAGE_SH)
    for j in range(4):
        a = rs.uniform(0, 6.28)
        inner += line([(rs.uniform(-8, 4), rs.uniform(-8, 4)), (14 * math.cos(a), 14 * math.sin(a))], 2.2, C_PAGE_LINE, taper=.3, wmin=.4, seed=sd + j)
    return _tf(shape(pts, C_PAGE, inner, w=3.0, seed=sd + 9), x, y, k, rot)


def paper_stack(x, y, k=1.0, n=6, seed=0, mess=0.3, sy=0.5, w=130.0, h=170.0):
    """Стопка листов, дно по центру; каждый следующий выше на 5 px и повернут на ±mess·12°."""
    rs = _rs(8300 + seed)
    o = []
    for j in range(n):
        o.append(paper(rs.uniform(-12, 12) * mess, -h * sy / 2 - 5 * j, 1.0, rs.uniform(-12, 12) * mess, w, h, seed + j * 3,
                       "lines" if j == n - 1 else "blank", sy, corner=(j == n - 1)))
    return _tf("".join(o), x, y, k)


def paper_pile(x, y, k=1.0, seed=0, sy=0.55, n=11):
    """Гора бумажек бардака: дно по центру, ширина ≈ 300, высота ≈ 120. Листы под разными углами, стикер, скомканные шарики."""
    rs = _rs(8400 + seed)
    o = []
    kinds = ["lines", "sketch", "lines", "grid", "blank", "lines", "sketch"]
    for j in range(n):
        u = j / max(1, n - 1)
        px = rs.uniform(-120, 120) * (1 - .55 * u)
        py = -30 - 70 * u + rs.uniform(-10, 10)
        o.append(paper(px, py, 1.0, rs.uniform(-40, 40), rs.uniform(110, 140), rs.uniform(140, 175), seed * 31 + j, kinds[j % len(kinds)], sy))
    o.append(paper_ball(rs.uniform(-130, -90), -18, 1.0, rs.uniform(0, 90), seed + 1))
    o.append(paper_ball(rs.uniform(80, 120), -26, .85, rs.uniform(0, 90), seed + 2))
    return _tf("".join(o), x, y, k)


def flying_sheet(x, y, k=1.0, rot=0.0, seed=0, kind="lines", flap=0.0, sy=1.0):
    """Летящий лист (центр): гнётся волной flap (радианы фазы), чуть сплющивается при повороте «ребром»."""
    return paper(x, y, k, rot + 8 * math.sin(flap * 1.3), 120, 160, seed, kind, sy * (.78 + .22 * abs(math.cos(flap))), bend=math.sin(flap))


def fan_sheets(x, y, t, k=1.0, n=8, seed=0, spread=1.0, kind=None, sy0=0.55):
    """Веер листов из (x, y): t 0…1 — разлёт; листы летят в разные стороны и в камеру (растут до ×1.9), крутятся и гнутся."""
    rs = _rs(8500 + seed)
    o = []
    kinds = ["lines", "sketch", "grid", "lines", "sketch", "blank"]
    items = []
    for j in range(n):
        ang = math.radians(-90 + (j - (n - 1) / 2) * 150 / max(1, n - 1) * spread + rs.uniform(-8, 8))
        dist = rs.uniform(380, 640) * spread
        grow = rs.uniform(1.3, 2.1)
        spin = rs.uniform(-160, 160)
        items.append((grow, ang, dist, spin, j))
    items.sort()   # те, что растут сильнее (ближе к камере), — сверху
    for grow, ang, dist, spin, j in items:
        u = clamp(t)
        e = 1 - (1 - u) ** 2.2
        px = x + math.cos(ang) * dist * e
        py = y + math.sin(ang) * dist * e + 260 * u * u   # падают вниз под конец
        s = k * (1 + (grow - 1) * e)
        sy = sy0 + (1 - sy0) * clamp(e * 1.6)
        o.append(paper(px, py, s, spin * e + rs.uniform(-20, 20), 120, 160, seed * 13 + j, (kind or kinds[j % len(kinds)]), sy,
                       bend=math.sin(u * 9 + j) * clamp(e * 2)))
    return "".join(o)


def mug(x, y, k=1.0, rot=0.0, col="red", coffee=True, steam=0.0, t=0.0, handle=1, seed=0):
    """Кружка, дно по центру: 66×78, ручка справа (handle=1) или слева (−1); сверху эллипс горла с тёмной гладью кофе."""
    sd = 8600 + seed
    c, csh, chi = MUG_COLS.get(col, MUG_COLS["red"])
    o = []
    hs = handle
    o.append(line([(hs * 30, -62), (hs * 52, -60), (hs * 56, -38), (hs * 30, -22)], 11, lib.INK, taper=.0, wmin=1, seed=sd + 1))
    o.append(line([(hs * 30, -62), (hs * 50, -60), (hs * 53, -38), (hs * 30, -22)], 6, c, taper=.0, wmin=1, seed=sd + 2))
    body = [(-33, -76, 1), (-32, -30), (-30, -4), (-24, 0, 1), (24, 0, 1), (30, -4), (32, -30), (33, -76, 1)]
    inner = blob([(18, -80), (40, -80), (40, 4), (14, 4)] if hs > 0 else [(-40, -80), (-18, -80), (-14, 4), (-40, 4)], csh)
    inner += line([(-20 * hs, -66), (-21 * hs, -20)], 5, chi, taper=.4, wmin=.3, seed=sd + 3)
    o.append(shape(body, c, inner, w=3.8, seed=sd))
    o.append(shape(ellipse_pts(0, -76, 33, 9, 16), lib.mul(csh, (.9, .9, .9)), "", w=3.2, seed=sd + 4))
    if coffee:
        o.append(blob(ellipse_pts(0, -74.5, 27, 6.5, 14), C_COFFEE))
        o.append(blob(ellipse_pts(-8, -76, 8, 2, 8), "#7A563C"))
    if steam > 0.01:
        for j in range(3):
            ph = t * 2.4 + j * 2.1
            xs = -14 + 14 * j
            pts = [(xs + 7 * math.sin(ph + i * .9), -90 - 15 * i) for i in range(5)]
            o.append(line(pts, 3.4 * steam, "#9FA3AA", taper=.8, wmin=.1, seed=sd + 10 + j))
    return _tf("".join(o), x, y, k, rot)


def coffee_ring(x, y, k=1.0, rot=0.0, seed=0, sy=0.5):
    sd = 8700 + seed
    pts = [(34 * math.cos(a), 34 * math.sin(a)) for a in [math.radians(20 + i * 300 / 16) for i in range(17)]]
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k:.4f} {k * sy:.4f})">' + \
        line(pts, 5, "#A8774F", taper=.5, wmin=.25, seed=sd) + line([(30, 10), (36, 2)], 4, "#A8774F", taper=.5, wmin=.3, seed=sd + 1) + "</g>"


def clink(x, y, k=1.0, u=1.0, seed=0, col=None):
    """Штрихи удара/звяка вокруг точки: лучики вылетают и гаснут (u 0…1)."""
    if u <= 0 or u >= 1:
        return ""
    c = col or "#F2B632"
    o = []
    for j in range(5):
        a = math.radians(-160 + j * 35)
        r0, r1 = 22 + 30 * u, 44 + 46 * u
        o.append(line([(x + r0 * k * math.cos(a), y + r0 * k * math.sin(a)), (x + r1 * k * math.cos(a), y + r1 * k * math.sin(a))],
                      6 * k * (1 - u * .6), c, taper=.4, wmin=.3, seed=8750 + seed + j))
    return "".join(o)


def cable(pts, col=None, w=9.0, seed=0, hi=True):
    c = col or C_CABLE
    o = line(pts, w + 3.5, lib.INK, taper=0, wmin=1, seed=8800 + seed) + line(pts, w, c, taper=0, wmin=1, seed=8801 + seed)
    if hi:
        o += line([(p[0] - 1.5, p[1] - 2) for p in pts], w * .28, C_CABLE_HI, taper=.6, wmin=.2, seed=8802 + seed)
    return o


def cable_tangle(x, y, k=1.0, seed=0, t=0.0, wind=0.0, col2="#E7E2D6", n=4):
    """Клубок проводов (центр, ≈ 200×110): петли разных проводов (тёмный, белый, красный), живут от t; wind — стягиваются к центру."""
    rs = _rs(8900 + seed)
    cols = [C_CABLE, col2, "#C8553D", "#3F6FB0"]
    o = []
    for j in range(n):
        R = rs.uniform(55, 95) * (1 - .45 * wind)
        ry = R * rs.uniform(.38, .55)
        cx, cy = rs.uniform(-30, 30), rs.uniform(-12, 12)
        ph = rs.uniform(0, 6.28) + t * .8 * (1 if j % 2 else -1)
        turns = 1.6 + .5 * j
        pts = []
        for i in range(int(turns * 14) + 1):
            a = ph + i * 2 * math.pi / 14
            rr = R * (.65 + .35 * math.sin(i * .37 + j))
            pts.append((cx + rr * math.cos(a), cy + ry * (rr / R) * math.sin(a) + 3 * math.sin(i * .9)))
        o.append(cable(pts, cols[j % len(cols)], 8, seed * 7 + j))
    return _tf("".join(o), x, y, k)


def charger(x, y, k=1.0, rot=0.0):
    o = shape(rrect(-20, -28, 20, 28, 6), "#F3F0E8", blob(rect_pts(8, -30, 22, 30), "#D4CFC2"), w=3.4, seed=8950)
    o += shape(rrect(-12, -46, -6, -28, 1.5), C_METAL, "", w=2.2, seed=8951) + shape(rrect(6, -46, 12, -28, 1.5), C_METAL, "", w=2.2, seed=8952)
    return _tf(o, x, y, k, rot)


def flicker(t, t0, t1, seed=0):
    """Накал лампочки: 1 до t0, мигание t0…t1 (3–4 провала), 0 после t1."""
    if t <= t0:
        return 1.0
    if t >= t1:
        return 0.0
    u = (t - t0) / (t1 - t0)
    blink = 1.0 if math.sin(u * 23 + seed) > -0.2 else 0.15
    return clamp((1 - u ** 1.5) * blink)


def idea_bulb(x, y, k=1.0, on=1.0, t=0.0, seed=0, col=None, rays=True):
    """Лампочка-идея, ЦЕНТР колбы (x, y), r 46. on — накал. col — цвет накала (по умолчанию тёплый жёлтый)."""
    sd = 9000 + seed
    hot = col or C_LAMP
    on = clamp(on)
    gc = mix("#D9DCE0", hot, on)
    o = []
    if on > .05 and rays:
        for j in range(8):
            a = math.radians(-90 + (j - 3.5) * 30)
            r0, r1 = 60 + 4 * math.sin(t * 9 + j), 84 + 8 * on + 5 * math.sin(t * 9 + j)
            o.append(line([(r0 * math.cos(a), r0 * math.sin(a)), (r1 * math.cos(a), r1 * math.sin(a))], 7 * on, hot, taper=.4, wmin=.3, seed=sd + j))
    bulb = [(-18, 40, 1), (-22, 30), (-40, 10), (-46, -14), (-36, -38), (0, -50), (36, -38), (46, -14), (40, 10), (22, 30), (18, 40, 1)]
    inner = blob(ellipse_pts(14, -6, 30, 38, 14), mix("#BFC3C9", lib.mul(hot, (.85, .85, .85)), on))
    inner += line([(-24, -26), (-28, -8)], 6, "#FFFFFF" if on > .3 else "#EEF0F2", taper=.5, wmin=.3, seed=sd + 20)
    inner += line([(-8, 22), (-6, 0), (0, -8), (6, 0), (8, 22)], 3.2, mix("#8A8E96", "#C0631E", on), taper=.1, wmin=.7, seed=sd + 21)
    o.append(shape(bulb, gc, inner, w=3.8, seed=sd + 30))
    o.append(shape(rrect(-19, 38, 19, 66, 4), C_METAL, line([(-19, 48), (19, 46)], 2.6, C_METAL_SH, seed=sd + 31) +
                   line([(-19, 57), (19, 55)], 2.6, C_METAL_SH, seed=sd + 32), w=3.2, seed=sd + 33))
    o.append(shape(ellipse_pts(0, 70, 8, 5, 8), "#4A4D55", "", w=2.4, seed=sd + 34))
    return _tf("".join(o), x, y, k)


def laptop_closed(x, y, k=1.0, rot=0.0, col="#9AA0AA"):
    o = shape(rrect(-112, -22, 112, 0, 6), col, blob(rect_pts(-116, -8, 116, 2), lib.mul(col, (.78, .78, .8))), w=3.8, seed=9100)
    o += line([(-104, -15), (104, -15)], 2.2, lib.mul(col, (.7, .7, .72)), taper=.1, wmin=.8, seed=9101)
    return _tf(o, x, y, k, rot)


_STICKY = {"yellow": "#F7DC6F", "pink": "#F4A6B7", "blue": "#9FD0EA", "green": "#B6DE8E", "orange": "#F5B461"}


def sticky(x, y, k=1.0, rot=0.0, col="yellow", seed=0, mark="lines"):
    sd = 9200 + seed
    c = _STICKY.get(col, col)
    pts = [(-35, -35, 1), (35, -35, 1), (35, 30), (30, 35, 1), (-35, 35, 1)]
    inner = blob(rect_pts(-40, -40, 40, -26), lib.mul(c, (.9, .9, .88)))
    if mark == "lines":
        for j in range(3):
            inner += line([(-24, -10 + 13 * j), (16 - 9 * (j % 2), -10 + 13 * j)], 3, lib.mul(c, (.55, .55, .55)), taper=.3, wmin=.5, seed=sd + j)
    elif mark in ("star", "circle", "arrow"):
        inner += _icon(mark, 0, 4, .95, lib.mul(c, (.45, .45, .5)), sd + 5)
    o = shape(pts, c, inner, w=3.0, seed=sd + 9)
    return _tf(o, x, y, k, rot)


def wall_sketch(x, y, k=1.0, rot=0.0, seed=0, kind="house", w=150.0, h=120.0):
    """Набросок на стене на скотче (центр): лист со значком kind, две полоски скотча сверху."""
    sd = 9300 + seed
    o = shape(rect_pts(-w / 2, -h / 2, w / 2, h / 2), C_PAGE, blob(rect_pts(-w / 2 - 5, h / 2 - 12, w / 2 + 5, h / 2 + 5), C_PAGE_SH) +
              _icon(kind, 0, 4, min(w, h) / 50, "#3D4A66", sd + 1), w=3.2, seed=sd)
    for sx in (-1, 1):
        o += shape(rect_pts(sx * w * .36 - 18, -h / 2 - 10, sx * w * .36 + 18, -h / 2 + 8), "#E9DFAE", "", w=2.2, seed=sd + 3 + sx)
    return _tf(o, x, y, k, rot)


def check_mark(x, y, k=1.0, u=1.0, col=None, w=9.0, seed=0):
    if u <= 0:
        return ""
    pts = [(-22, 0), (-12, 10), (-6, 17), (6, 2), (18, -12), (28, -24)]
    S = lib.sample(pts, False, 1.5)
    n = max(2, int(len(S) * clamp(u)))
    p = [(x + float(a) * k, y + float(b) * k) for a, b in S[:n]]
    return line(p, w * k, col or C_GREEN_OK, taper=.35, wmin=.4, seed=9400 + seed, peak=.35)


def checklist(x, y, k=1.0, rot=0.0, checks=0, u=0.0, seed=0, sy=1.0):
    """Лист с 4 чекбоксами (центр, 140×190): checks — отмечено, u — рисуется следующая галочка."""
    sd = 9450 + seed
    inner = blob(rect_pts(-80, 80, 80, 100), lib.mul(C_PAGE, (.94, .93, .9)))
    for j in range(4):
        yy = -62 + 40 * j
        inner += shape(rect_pts(-52, yy - 12, -28, yy + 12), "#FFFFFF", "", w=2.6, seed=sd + j)
        inner += line([(-16, yy), (44 - 10 * (j % 2), yy + 1)], 3.2, C_PAGE_LINE, taper=.25, wmin=.55, seed=sd + 10 + j)
        if j < checks:
            inner += check_mark(-38, yy - 4, .62, 1.0, seed=sd + 20 + j)
        elif j == checks and u > 0:
            inner += check_mark(-38, yy - 4, .62, u, seed=sd + 20 + j)
    o = shape(rect_pts(-70, -95, 70, 95), C_PAGE, inner, w=3.4, seed=sd + 30)
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k:.4f} {k * sy:.4f})">{o}</g>'


def apple(x, y, k=1.0, rot=0.0, bite=0.0, seed=0):
    """Яблоко (дно по центру) Ø 64. bite 0…1 — правый бок надкушен: вогнутый край из трёх полукружий зубов и светлая мякоть."""
    sd = 9500 + seed
    bt = clamp(bite)
    right = [(30, -56), (34, -34), (28, -10)]
    if bt > 0.01:
        d = 14 * bt
        right = [(30 - d * .6, -56), (34 - d, -48), (34 - d * 1.25, -40), (34 - d * .8, -34), (34 - d * 1.25, -27), (34 - d, -18), (28 - d * .3, -10)]
    body = [(0, -54, 1), (14, -62)] + right + [(14, 0), (0, -3, 1), (-14, 0), (-28, -10), (-34, -34), (-30, -56), (-14, -62)]
    inner = blob(ellipse_pts(14, -22, 20, 28, 12), "#A8332A") + line([(-20, -44), (-22, -30)], 6, "#F28B7A", taper=.5, wmin=.3, seed=sd + 1)
    if bt > 0.01:
        fl = [(p[0], p[1]) for p in right] + [(p[0] - 9 * bt, p[1]) for p in right[::-1]]
        inner += blob(fl, "#FFF4D6") + line([(p[0] - 9 * bt, p[1]) for p in right[1:-1]], 2.2, "#E8D6A0", taper=.3, wmin=.4, seed=sd + 6)
    o = [line([(0, -54), (2, -66), (6, -74)], 5, "#6B4A2E", taper=.2, wmin=.6, seed=sd + 2)]
    o.append(shape([(6, -68, 1), (18, -78), (32, -76, 1), (20, -66)], "#5E9E50", line([(8, -68), (28, -75)], 2, "#41733A", seed=sd + 3), w=2.8, seed=sd + 4))
    o.append(shape(body, "#D9473A", inner, w=3.8, seed=sd))
    return _tf("".join(o), x, y, k, rot)


def chocolate(x, y, k=1.0, rot=0.0, seed=0):
    sd = 9600 + seed
    o = shape(rrect(-60, -26, 60, 26, 4), "#6B3A2A", blob(rect_pts(-64, 12, 64, 30), "#4E2A1E"), w=3.6, seed=sd)
    o += shape(rect_pts(-10, -26, 30, 26), "#E8C04A", blob(rect_pts(-12, 14, 32, 28), "#C49A2C") + blob(
        [(10, -12, 1), (13, -3), (22, -2, 1), (15, 4), (18, 13, 1), (10, 8), (2, 13, 1), (5, 4), (-2, -2, 1), (7, -3)], "#FFF3C4"), w=3.0, seed=sd + 1)
    o += shape(rrect(-60, -26, -44, 26, 3), "#8C4E38", "", w=2.6, seed=sd + 2)
    return _tf(o, x, y, k, rot)


def tray(x, y, k=1.0, w=360.0, col="#5C9A78"):
    sd = 9700
    hw = w / 2
    o = shape([(-hw, -20, 1), (-hw + 18, 0, 1), (hw - 18, 0, 1), (hw, -20, 1), (hw - 10, -34, 1), (-hw + 10, -34, 1)], col,
              blob(rect_pts(-hw, -12, hw, 2), lib.mul(col, (.78, .78, .78))) + blob(rect_pts(-hw + 18, -32, hw - 18, -26), lib.mul(col, (1.15, 1.15, 1.12))),
              w=3.8, seed=sd)
    return _tf(o, x, y, k)


def cup_plain(x, y, k=1.0, rot=0.0):
    o = shape(ellipse_pts(0, -6, 58, 11, 18), "#F3EFE6", blob(ellipse_pts(0, -2, 50, 6, 14), "#D8D1C2"), w=3.2, seed=9750)
    o += line([(34, -52), (54, -48), (52, -26), (32, -20)], 10, lib.INK, taper=0, wmin=1, seed=9751) + line([(34, -52), (52, -48), (50, -26), (32, -20)], 5, "#F3EFE6", taper=0, wmin=1, seed=9752)
    o += shape([(-36, -62, 1), (-34, -30), (-24, -10, 1), (24, -10, 1), (34, -30), (36, -62, 1)], "#FFFFFF", blob([(14, -66), (40, -66), (30, -6), (12, -6)], "#E2DCD0"), w=3.6, seed=9753)
    o += shape(ellipse_pts(0, -62, 36, 8, 16), "#E2DCD0", blob(ellipse_pts(0, -61, 30, 5.5, 14), C_COFFEE), w=3.0, seed=9754)
    return _tf(o, x, y, k, rot)


def cup_spiky(x, y, k=1.0, rot=0.0, t=0.0):
    c, csh = "#8E5BC2", "#6A3F99"
    o = []
    for j in range(7):   # шипы по бокам и сверху
        a = math.radians(-180 + j * 30)
        bx, by = 40 * math.cos(a), -40 + 34 * math.sin(a)
        tx, ty = 62 * math.cos(a), -40 + 56 * math.sin(a)
        nx, ny = -math.sin(a) * 9, math.cos(a) * 9
        o.append(shape([(bx - nx, by - ny, 1), (tx, ty, 1), (bx + nx, by + ny, 1)], "#F2B632", "", w=2.8, seed=9800 + j))
    o.append(line([(36, -66), (64, -76), (70, -54), (56, -46), (62, -36), (40, -26)], 10, lib.INK, taper=0, wmin=1, seed=9810))
    o.append(line([(36, -66), (62, -74), (67, -54), (54, -46), (60, -36), (40, -26)], 5, c, taper=0, wmin=1, seed=9811))
    o.append(shape([(-40, -76, 1), (-44, -40), (-30, 0, 1), (30, 0, 1), (44, -40), (40, -76, 1)], c, blob([(14, -80), (48, -80), (36, 4), (10, 4)], csh) +
                   "".join(blob(ellipse_pts(-22 + 16 * j, -40 + 10 * (j % 2), 4, 4, 8), "#F2B632") for j in range(4)), w=3.8, seed=9812))
    o.append(shape(ellipse_pts(0, -76, 40, 9, 16), csh, blob(ellipse_pts(0, -75, 33, 6, 14), "#3FB59B"), w=3.0, seed=9813))
    return _tf("".join(o), x, y, k, rot)


def pencil(x, y, k=1.0, rot=0.0):
    o = shape([(-75, -8, 1), (48, -8, 1), (75, 0, 1), (48, 8, 1), (-75, 8, 1)], "#F2B632", blob(rect_pts(-80, 2, 50, 10), "#C99726"), w=3.2, seed=9850)
    o += shape([(48, -8, 1), (75, 0, 1), (48, 8, 1)], "#F1D9B5", "", w=2.6, seed=9851) + blob([(66, -3), (76, 0), (66, 3)], "#3A3A3A")
    o += shape(rrect(-86, -8, -72, 8, 3), "#E88A8A", "", w=2.6, seed=9852) + blob(rect_pts(-74, -8, -68, 8), C_METAL)
    return _tf(o, x, y, k, rot)


def marker(x, y, k=1.0, rot=0.0, col="#2C6FD1", cap=False):
    o = shape(rrect(-62, -12, 40, 12, 6), "#F4F1EA", blob(rect_pts(-66, 4, 44, 14), "#D6D0C2") + blob(rect_pts(-30, -12, -12, 12), col), w=3.4, seed=9900)
    if cap:
        o += shape(rrect(30, -14, 66, 14, 6), col, "", w=3.2, seed=9901)
    else:
        o += shape([(40, -9, 1), (52, -6), (62, -2, 1), (62, 2, 1), (52, 6), (40, 9, 1)], "#3A3A3A", blob([(54, -3), (66, -1), (66, 1), (54, 3)], col), w=2.8, seed=9902)
    return _tf(o, x, y, k, rot)


def thought_cloud(x, y, k=1.0, w=260.0, h=170.0, u=1.0, seed=0, col="#FFFFFF", dots=1, inner=""):
    """Облачко мыслей (центр). u — выскакивает (масштаб с перелётом). inner — SVG внутри облака (в мировых координатах облака, центр 0,0)."""
    if u <= 0.01:
        return ""
    s = lib.back_out(clamp(u), 2.2) if u < 1 else 1.0
    sd = 9950 + seed
    rs = _rs(sd)
    n = 9
    pts = []
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        bump = rs.uniform(.12, .2)
        for m in range(5):
            a = a0 + (a1 - a0) * m / 4
            r = 1 + bump * math.sin(math.pi * m / 4)
            pts.append((w / 2 * r * math.cos(a), h / 2 * r * math.sin(a)) + ((1,) if m == 0 else ()))
    o = []
    if dots:
        for j, (dx, dy, r) in enumerate(((-.32, .62, 16), (-.46, .82, 10), (-.56, .98, 6))):
            o.append(shape(ellipse_pts(dots * dx * w, dy * h, r, r, 10), col, "", w=3, seed=sd + 40 + j))
    o.append(shape(pts, col, blob(ellipse_pts(w * .12, h * .2, w * .42, h * .32, 14), lib.mul(col, (.93, .93, .95))) + inner, w=3.8, seed=sd + 1))
    return _tf("".join(o), x, y, k * s)


def question_mark(x, y, k=1.0, u=1.0, col=None, w=11.0, seed=0):
    """Знак вопроса штрихами, высота 120, центр. u — дорисовывается (сначала крючок, потом точка)."""
    if u <= 0:
        return ""
    c = col or lib.INK
    hook = [(-30, -30), (-24, -48), (-6, -58), (16, -54), (28, -38), (24, -18), (6, -6), (0, 8), (0, 24)]
    S = lib.sample(hook, False, 1.5)
    n = max(2, int(len(S) * clamp(u / .8)))
    o = line([(x + float(a) * k, y + float(b) * k) for a, b in S[:n]], w * k, c, taper=.4, wmin=.35, seed=9990 + seed, peak=.3)
    if u > .85:
        r = 8 * k * clamp((u - .85) / .15)
        o += blob(ellipse_pts(x, y + 48 * k, r, r, 10), c)
    return o


def z_mark(x, y, k=1.0, u=1.0, col=None):
    if u <= 0.01:
        return ""
    c = col or "#3F6FB0"
    s = k * (.5 + .5 * clamp(u))
    return line([(x - 20 * s, y - 22 * s), (x + 20 * s, y - 22 * s), (x - 20 * s, y + 22 * s), (x + 22 * s, y + 22 * s)], 8 * s, c, taper=.15, wmin=.5, seed=9995)
