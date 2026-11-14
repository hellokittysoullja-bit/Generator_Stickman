"""Общие предметы рилса 63 «кофе» — ОДИН вид для групп A…F (своих копий не рисовать). Автор — группа A.
Основа — props.py рилса 62 целиком (всё как было), сверху — раздел КОФЕ (в конце файла, описание ниже в этой строке документации).

КОФЕ (новое в 63; (x, y) — ЦЕНТР ДНА, если не сказано иначе; букв, цифр, шкал и делений нет нигде):
  coffee_mug(x, y, k, rot, col, fill, steam, t, upside, seed)   кружка кофе 110×130·k, ручка справа; fill 0…1 — уровень кофе
                                (0 — пустая, видно дно), steam 0…1 — пар завитками; upside=True — вверх дном (дно сверху, без кофе)
  mug_cut(x, y, k, glow, wave, t, seed)                     кружка В РАЗРЕЗЕ для весов: стенка срезана, внутри почти вся вода
                                (голубая с коричневым оттенком), тонкий тёмный слой кофе сверху; glow 0…1 — подсветка воды, wave 0…1 — волна
  glass(x, y, k, rot, fill, t, splash, seed)               прозрачный стакан 90×140·k (стекло — светлая сплошная заливка), голубая вода
                                наливается снизу вверх (fill 0…1); splash 0…1 — плеск каплями над краем
  splash(x, y, k, u, seed, col)                              капли разлетаются веером из точки (u 0…1 — полёт)
  tea_cup(x, y, k, rot, steam, t, seed)                      чашка чая на блюдце: янтарный чай, ниточка пакетика с пустым ярлычком
  milk_saucer(x, y, k, t, ripple, lick, seed)                блюдце с молоком (ЦЕНТР дна), Ø 260·k; ripple 0…1 — круги ряби,
                                lick 0…1 — момент касания язычка (вмятина и капли)
  coffee_pot(x, y, k, rot, t, seed)                          кофейник 150×220·k (ручка слева, носик справа), без надписей и шкал
  pot_spout(x, y, k, rot)                                    → (sx, sy) кончик носика кофейника в мире (для струи)
  pour_stream(x0, y0, x1, y1, t, w, col, seed, bend)         струя кофе дугой от носика до точки, бесконечно бежит (блики едут)
  jug(x, y, k, fill, seed)                                   кувшин воды 150×230·k
  scales(x, y, k, tilt, left, right, seed)                   рычажные весы без делений: (x, y) — центр основания; tilt° (+ — правая
                                чаша ниже); left/right — SVG на чаше (локальные координаты: (0, 0) — центр дна груза на чаше)
  scale_pans(x, y, k, tilt)                                  → ((lx, ly), (rx, ry)) — где в мире стоят грузы на чашах
  settle(t, t0, a0, a1, freq, damp)                          затухающий переход a0 → a1 с отскоком (для чаш, кадров, всего)
  red_marker(x, y, k, rot, cap)                              красный маркер (ЦЕНТР), длина 130·k, наконечник вправо (rot — куда)
  cross_stroke(p0, p1, q0, q1, u, w, seed, col)              живой крест маркером: штрих p0→p1 на u 0…0.5, q0→q1 на 0.5…1;
                                ширина с нажимом и неровным краем; C_MARKER — красный
  marker_tip(p0, p1, q0, q1, u)                              → (x, y) где сейчас кончик маркера при этом u
  clock(x, y, r, angle_h, angle_m, seed, face, rim)          настенные часы (ЦЕНТР) БЕЗ цифр и делений — только стрелки;
                                углы в градусах по часовой от «12»; clock_hm(h, m) → (angle_h, angle_m)
  table_lamp(x, y, k, on, seed, table)                       настольная лампа + небольшой ЧЁТКИЙ круг света под абажуром
                                (table=True — пятно на столе с чётким краем формы абажура)
  crack(x, y, k, rot, u, seed, col)                          трещина-штрих (начало (x, y), бежит вправо; u 0…1 — длина)
  evap(x, y, k, u, t, seed)                                  дымок испарения: маленькие сплошные завитки вверх (u — сила)
  zzz(x, y, k, t, u)                                         три Z сна растут и поднимаются по очереди
  gloom(x, y, k, t, u, seed)                                 тучка-закорючка над головой (ЦЕНТР дна), тёмная, со спиралькой
  dash_arrow(pts, u, w, col, seed)                           пунктирная стрелка по точкам с наконечником на конце (u — проявление)
  heart(x, y, k, beat, seed)                                 сердце (ЦЕНТР) со штрихами удара; beat 0…1 — толчок
  C_COFFEE_DARK, C_WATER, C_WATER_SH, C_TEA, C_MILK, C_GLASS2, C_MARKER — цвета

(Ниже — как было в 62.)
Общие предметы рилса 62 «медитация».
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


# ═══════════════════════════════ МЕДИТАЦИЯ (рилс 62) ═══════════════════════════════

def pop(t, t0, dur=None, amp=0.32, freq=2.4, damp=6.5):
    """(sx, sy) пружинного выскока после t0: масштаб 0 → перелёт → 1, сначала сжатие по вертикали, затем вытяжка, отскок."""
    u = t - t0
    if u <= 0:
        return 0.0, 0.0
    if dur is not None:
        u = u * 0.9 / max(dur, 1e-3)
    s = max(0.0, lib.spring(u, freq * 0.72, damp))
    e = -amp * math.exp(-damp * 0.8 * u) * math.cos(2 * math.pi * freq * u)
    return s * (1 - 0.6 * e), s * (1 + e)


def squash(t, t0, amp=0.25, freq=3.0, damp=7.0):
    """(sx, sy) удара: сплющивание и отскок с затуханием; до t0 — (1, 1)."""
    u = t - t0
    if u <= 0:
        return 1.0, 1.0
    e = amp * math.exp(-damp * u) * math.cos(2 * math.pi * freq * u)
    return 1 + 0.6 * e, 1 - e


def hop(t, t0, h=60.0, dur=0.32):
    """dy подскока (вверх — отрицательный) по параболе на [t0, t0 + dur]."""
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return -4 * h * u * (1 - u)


def unpop(t, t0, dur=0.22):
    """Масштаб исчезновения: короткий вдох (до 1.12), затем 0."""
    u = (t - t0) / dur
    if u <= 0:
        return 1.0
    if u >= 1:
        return 0.0
    return (1 + 0.5 * math.sin(math.pi * min(u / .4, 1) * .5) * .24) * (1 - lib.ease_in(u, 3))


def _puff_pts(w, h, seed, n=9, bump=(0.12, 0.2), cy=0.0):
    rs = _rs(seed)
    pts = []
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        b = rs.uniform(*bump)
        for m in range(5):
            a = a0 + (a1 - a0) * m / 4
            r = 1 + b * math.sin(math.pi * m / 4)
            pts.append((w / 2 * r * math.cos(a), cy + h / 2 * r * math.sin(a)) + ((1,) if m == 0 else ()))
    return pts


def cloud(x, y, w=300.0, h=200.0, sx=1.0, sy=1.0, seed=0, col="#FFFFFF", dots=None, inner="", ink_w=4.2, anchor="bottom"):
    """Облако-мысль: (x, y) — центр ДНА (якорь сжатия). dots=(dx, dy) — вектор от низа облака к макушке: три кружка-ступеньки."""
    if sx <= 0.01 or sy <= 0.01:
        return ""
    sd = 12000 + seed
    o = []
    if dots:
        g = clamp(min(sx, sy) * 1.4)
        for j, (q, r) in enumerate(((0.22, 20), (0.52, 14), (0.8, 9))):
            if g <= 0.02:
                break
            px, py = x + dots[0] * q, y + dots[1] * q
            o.append(shape(ellipse_pts(px, py, r * g, r * g, 12), col, "", w=3.2, seed=sd + 40 + j))
    hh = h * 1.16 / 2   # бугры выходят за h/2
    pts = _puff_pts(w, h, sd)
    sh = blob(ellipse_pts(w * .1, h * .22, w * .44, h * .3, 16), lib.mul(col, (.92, .93, .96)))
    body = shape(pts, col, sh + inner, w=ink_w, seed=sd + 1)
    oy = -hh if anchor == "bottom" else 0.0
    o.append(f'<g transform="translate({f(x)} {f(y)}) scale({sx:.4f} {sy:.4f}) translate(0 {f(oy)})">{body}</g>')
    return "".join(o)


C_STORM = "#6C7280"
C_STORM_SH = "#4E5360"
C_STORM_HI = "#8E95A3"


def storm(x, y, w=520.0, h=260.0, sx=1.0, sy=1.0, seed=0, flash=0.0, inner=""):
    """Грозовая туча, (x, y) — центр ДНА. flash 0…1 — подсвечивается изнутри (тон светлеет)."""
    if sx <= 0.01 or sy <= 0.01:
        return ""
    sd = 12100 + seed
    fl = clamp(flash)
    c = mix(C_STORM, "#C9CCD6", fl * .7)
    csh = mix(C_STORM_SH, "#9CA1AE", fl * .7)
    chi = mix(C_STORM_HI, "#F2F0E0", fl * .8)
    pts = _puff_pts(w, h, sd, n=11, bump=(0.16, 0.28))
    wav = [(-w * .62 + w * 1.24 * i / 16, h * (.06 + .05 * math.sin(i * 1.7 + seed))) for i in range(17)]
    inn = blob(wav + [(w * .62, h * .7), (-w * .62, h * .7)], csh)
    rs = _rs(sd + 3)
    for j in range(4):   # светлые макушки клубов
        cx = -w * .32 + j * w * .2 + rs.uniform(-10, 10)
        inn += blob(ellipse_pts(cx, -h * .26 + rs.uniform(-8, 8), w * .09, h * .1, 12), chi)
    body = shape(pts, c, inn + inner, w=4.6, seed=sd + 1)
    hh = h * 1.28 / 2
    return f'<g transform="translate({f(x)} {f(y)}) scale({sx:.4f} {sy:.4f}) translate(0 {f(-hh)})">{body}</g>'


def bolt(x0, y0, x1, y1, u=1.0, w=34.0, seed=0, n=5):
    """Молния зигзагом (x0,y0) → (x1,y1). u 0…0.3 — растёт, до 1 — стоит, > 1 — нет."""
    if u <= 0 or u > 1:
        return ""
    g = clamp(u / .3)
    rs = _rs(12200 + seed)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    cen = []
    for i in range(n + 1):
        q = i / n * g
        off = 0 if i in (0, n) else (1 if i % 2 else -1) * rs.uniform(.08, .13) * L
        cen.append((x0 + dx * q + nx * off, y0 + dy * q + ny * off))
    left, right = [], []
    for i, (cx, cy) in enumerate(cen):
        ww = w * (1 - .8 * i / n) / 2
        left.append((cx + nx * ww, cy + ny * ww, 1))
        right.append((cx - nx * ww, cy - ny * ww, 1))
    pts = left + right[::-1]
    return shape(pts, "#FFE14D", blob([(p[0] - 4, p[1]) for p in pts[:len(left)]] + [(p[0], p[1]) for p in pts[len(left):]], "#F7C531"),
                 w=4.0, seed=12201 + seed)


def flash_screen(u, col="#FFF6D8"):
    """Вспышка света на весь кадр (u 0…1 — сила). Это свет, а не фигура."""
    if u <= 0.003:
        return ""
    return f'<rect x="-200" y="-200" width="1480" height="2320" fill="{col}" opacity="{clamp(u):.3f}"/>'


def drop(x, y, k=1.0, rot=0.0, col="#6FB7E8"):
    pts = [(0, -24, 1), (7, -11), (13, 3), (11, 13), (0, 18), (-11, 13), (-13, 3), (-7, -11)]
    o = shape(pts, col, blob(ellipse_pts(5, 8, 8, 7, 10), lib.mul(col, (.8, .85, .92))), w=3.0, seed=12300)
    o += blob(ellipse_pts(-4, 1, 3, 5, 8), "#FFFFFF")
    return _tf(o, x, y, k, rot)


def sweat(x, y, k=1.0, rot=0.0):
    return drop(x, y, k * 1.1, rot, "#9FD6F2")


def rain(x, y, w, t, t0, n=7, seed=0, k=1.0, floor=1300.0, every=0.12):
    """Крупные капли из полосы [x − w/2, x + w/2] на высоте y, после t0; падают с ускорением до floor (там — брызги)."""
    if t < t0:
        return ""
    rs = _rs(12400 + seed)
    o = []
    for j in range(n * 4):
        ts = t0 + j * every + rs.uniform(0, every * .6)
        px = x + rs.uniform(-w / 2, w / 2)
        u = t - ts
        if u < 0:
            continue
        py = y + 300 * u + 1600 * u * u
        if py < floor:
            o.append(drop(px, py, k * rs.uniform(.9, 1.2)))
        else:
            tu = (py - floor) / 260
            if tu < 1:
                for s in (-1, 1):
                    o.append(line([(px + s * 8 * k, floor), (px + s * (16 + 22 * tu) * k, floor - (22 - 10 * tu) * k)],
                                  4 * k * (1 - tu), "#6FB7E8", taper=.4, wmin=.3, seed=12450 + j))
    return "".join(o)


C_SAND = "#E2B65C"
C_SAND_SH = "#C49440"
C_GLASS = "#E4F0F4"


def hourglass(x, y, k=1.0, rot=0.0, flow=0.0, top=0.0, t=0.0, seed=0):
    """Песочные часы без делений, ЦЕНТР (x, y), 160×252. top — доля песка в ВЕРХНЕЙ (по миру) колбе; flow — струя."""
    sd = 12500 + seed
    g = 1 if math.cos(math.radians(rot)) >= 0 else -1
    rv = rot if g > 0 else rot - 180
    a = clamp(top)
    half = [(-58, -104, 1), (-56, -74), (-44, -40), (-20, -12), (-7, 0, 1)]
    glass = half + [(-20, 12), (-44, 40), (-56, 74), (-58, 104, 1), (58, 104, 1), (56, 74), (44, 40), (20, 12), (7, 0, 1),
                    (20, -12), (44, -40), (56, -74), (58, -104, 1)]
    sand = ""
    if a > 0.01:   # верхняя колба: песок у горлышка, воронка посередине
        lv = -6 - 92 * a ** 0.75
        dip = 10 * clamp(flow) * a
        sand += shape([(-70, lv, 1), (-20, lv + 1), (0, lv + dip), (20, lv + 1), (70, lv, 1), (70, 6, 1), (-70, 6, 1)], C_SAND,
                      blob([(-70, lv + 14), (70, lv + 14), (70, 6), (-70, 6)], C_SAND_SH), w=2.6, seed=sd + 2)
    b = 1 - a
    if b > 0.01:   # нижняя колба: горка
        lv = 102 - 88 * b ** 0.8
        pk = 16 * min(1, b * 3)
        sand += shape([(-70, lv + 6, 1), (-30, lv + 2), (0, lv - pk), (30, lv + 2), (70, lv + 6, 1), (70, 110, 1), (-70, 110, 1)], C_SAND,
                      blob([(-70, lv + 26), (70, lv + 26), (70, 110), (-70, 110)], C_SAND_SH), w=2.6, seed=sd + 3)
    if flow > 0.02 and a > 0.01:
        lv = 102 - 88 * b ** 0.8 - 16 * min(1, b * 3)
        ys = [0 + (lv - 0) * i / 6 for i in range(7)]
        sand += line([(1.2 * math.sin(t * 40 + i), yy) for i, yy in enumerate(ys)], 5 * flow, C_SAND, taper=0, wmin=1, seed=sd + 4)
    o = [shape(glass, C_GLASS, sand + line([(-44, -86), (-38, -50), (-22, -24)], 6, "#FFFFFF", taper=.5, wmin=.3, seed=sd + 5) +
               line([(-44, 88), (-40, 60)], 6, "#FFFFFF", taper=.5, wmin=.3, seed=sd + 6), w=3.6, seed=sd + 1)]
    for s in (-1, 1):
        o.append(shape(rrect(s * 72 - 6, -108, s * 72 + 6, 108, 3), C_WOOD, blob(rect_pts(s * 72 + 1, -110, s * 72 + 8, 110), C_WOOD_SH),
                       w=3.0, seed=sd + 7 + s))
    for s in (-1, 1):
        o.append(shape(rrect(-84, s * 115 - 12, 84, s * 115 + 12, 7), C_WOOD,
                       blob(rect_pts(-90, s * 115 + 3, 90, s * 115 + 14), C_WOOD_SH) + line([(-70, s * 115 - 6), (60, s * 115 - 6)], 3, C_WOOD_HI,
                                                                                               taper=.5, wmin=.3, seed=sd + 11), w=3.6, seed=sd + 9 + s))
    return _tf("".join(o), x, y, k, rv)


def smoke_curls(x, y, k=1.0, u=1.0, t=0.0, seed=0, col="#D3D7DE", n=3):
    """Сплошные завитки дыма над (x, y): каждый — S-лента с тушью, кончик закручен спиралью; растёт вверх и колышется."""
    if u <= 0.01:
        return ""
    o = []
    for j in range(n):
        ph = t * 3.0 + j * 2.0
        xs = (j - (n - 1) / 2) * 26
        L = (64 + 14 * (j % 2)) * u
        pts = []
        for i in range(13):
            q = i / 12
            pts.append((xs + 11 * math.sin(ph + q * 4.2) * (0.3 + q), -q * L))
        ex, ey = pts[-1]
        sgn = 1 if j % 2 else -1
        R = 11 * (0.5 + 0.5 * u)
        cx, cy = ex - sgn * R, ey
        for i in range(1, 15):   # спираль 1.1 оборота внутрь
            a = math.pi * (0 if sgn > 0 else 1) - sgn * i * 0.5
            r = R * (1 - i / 18)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        w0 = 10 * k
        P = [(x + px * k, y + py * k) for px, py in pts]
        o.append(line(P, w0 + 4.5, lib.INK, taper=.55, wmin=.3, seed=12600 + seed + j))
        o.append(line(P, w0, col, taper=.6, wmin=.18, seed=12610 + seed + j))
    return "".join(o)


def plate_soup(x, y, k=1.0, steam=1.0, t=0.0, seed=0):
    """Тарелка супа (дно по центру) Ø 220: морковные кружки, зелень, пар-завитки сверху."""
    sd = 12700 + seed
    o = []
    o.append(shape([(-110, -38, 1), (-92, -14), (-56, 0, 1), (56, 0, 1), (92, -14), (110, -38, 1)], "#F4F1EA",
                   blob([(-110, -30), (110, -30), (110, 4), (-110, 4)], "#D9D3C6"), w=3.8, seed=sd))
    o.append(shape(ellipse_pts(0, -38, 112, 30, 22), "#FBF9F4", "", w=3.8, seed=sd + 1))
    soup = blob(ellipse_pts(0, -36, 84, 20, 20), "#E58A3A")
    soup += blob(ellipse_pts(14, -32, 60, 11, 16), "#D27428")
    rs = _rs(sd + 2)
    for j in range(5):
        cx, cy = rs.uniform(-62, 62), rs.uniform(-44, -30)
        soup += shape(ellipse_pts(cx, cy, 9, 5, 10), "#F2A23C", "", w=2.0, seed=sd + 10 + j)
    for j in range(6):
        cx, cy = rs.uniform(-66, 66), rs.uniform(-46, -28)
        soup += blob(ellipse_pts(cx, cy, 4.5, 2.4, 8, rot=rs.uniform(0, 180)), "#4E9A3E")
    o.append(soup)
    o.append(line([(-86, -38), (-60, -52), (0, -58), (60, -52), (86, -38)], 2.6, "#D9D3C6", taper=.7, wmin=.2, seed=sd + 3))
    if steam > 0.01:
        o.append(smoke_curls(0, -60, 1.0, steam, t, seed=sd, col="#E6E8EC"))
    return _tf("".join(o), x, y, k)


def cutlet_fork(x, y, k=1.0, rot=0.0, seed=0):
    """Котлета на вилке: ЦЕНТР котлеты (x, y); ручка вилки вниз (при rot=0), всего ~230."""
    sd = 12800 + seed
    o = [line([(0, 30), (0, 220)], 13, lib.INK, taper=0, wmin=1, seed=sd), line([(0, 32), (0, 218)], 8, C_METAL, taper=0, wmin=1, seed=sd + 1)]
    for j in (-1, 0, 1):
        o.append(line([(j * 12, 30), (j * 12, 52), (0, 62)], 5, C_METAL_SH, taper=0, wmin=1, seed=sd + 2 + j))
    pts = ellipse_pts(0, 0, 72, 46, 18, jitter=.06, seed=sd)
    rs = _rs(sd + 5)
    crust = blob(ellipse_pts(10, 16, 64, 24, 16), "#7A4220")
    for j in range(7):
        crust += blob(ellipse_pts(rs.uniform(-50, 50), rs.uniform(-28, 26), rs.uniform(4, 8), rs.uniform(3, 5), 8), "#6A3618")
    crust += line([(-44, -22), (-18, -34), (12, -34)], 6, "#C7864E", taper=.6, wmin=.2, seed=sd + 6)
    o.append(shape(pts, "#9C5A2E", crust, w=4.0, seed=sd + 7))
    return _tf("".join(o), x, y, k, rot)


C_IRON = "#4F8FD0"
C_IRON_SH = "#3769A0"


def iron(x, y, k=1.0, rot=0.0, smoke=0.0, t=0.0, seed=0):
    """Утюг (дно по центру), нос влево, 176×104; без значков и шкал. smoke — сплошные завитки над носом."""
    sd = 12900 + seed
    o = []
    if smoke > 0.01:
        o.append(smoke_curls(-40, -70, 0.9, smoke, t, seed=sd))
    o.append(line([(78, -30), (100, -26), (118, -10), (130, 10)], 7, "#3A3D44", taper=0, wmin=1, seed=sd + 1))
    o.append(line([(-30, -60), (-26, -96), (44, -96), (54, -54)], 16, lib.INK, taper=0, wmin=1, seed=sd + 2))
    o.append(line([(-30, -60), (-26, -94), (44, -94), (54, -54)], 10, "#3A3D44", taper=0, wmin=1, seed=sd + 3))
    body = [(-88, -12, 1), (-62, -38), (-20, -60), (40, -62), (72, -46), (84, -22), (86, -12, 1)]
    o.append(shape(body, C_IRON, blob([(-90, -26), (90, -26), (90, -8), (-90, -8)], C_IRON_SH) +
                   line([(-50, -36), (-14, -52), (30, -54)], 5, "#8FBCE8", taper=.6, wmin=.2, seed=sd + 4), w=4.0, seed=sd + 5))
    o.append(shape([(-92, -12, 1), (88, -12, 1), (86, 0, 1), (-84, 0, 1)], C_METAL, blob(rect_pts(-92, -5, 90, 2), C_METAL_SH), w=3.2, seed=sd + 6))
    return _tf("".join(o), x, y, k, rot)


def ironing_board(x, y, k=1.0, w=520.0, seed=0):
    """Гладильная доска: ЦЕНТР крышки (x, y), острый конец влево; ножки-крест вниз на 280."""
    sd = 13000 + seed
    o = []
    for s in (-1, 1):
        o.append(line([(s * -110, 14), (s * 110, 280)], 10, lib.INK, taper=0, wmin=1, seed=sd + s))
        o.append(line([(s * -110, 14), (s * 110, 280)], 6, C_METAL, taper=0, wmin=1, seed=sd + 3 + s))
    top = [(-w / 2, 0, 1), (-w / 2 + 70, -18), (w / 2 - 20, -18, 1), (w / 2, -6), (w / 2, 8), (w / 2 - 20, 18, 1), (-w / 2 + 70, 18)]
    o.append(shape(top, "#A9CDE6", blob([(-w, 6), (w, 6), (w, 24), (-w, 24)], "#7FA9C9") +
                   "".join(blob(ellipse_pts(-w / 2 + 90 + 70 * j, -4, 9, 5, 8), "#D6E9F5") for j in range(int((w - 120) / 70))), w=3.8, seed=sd + 6))
    return _tf("".join(o), x, y, k)


def mobilnik(x, y, k=1.0, rot=0.0):
    """Мобильник-силуэт, ЦЕНТР, 70×130: тёмный корпус, без экрана, без букв."""
    o = shape(rrect(-35, -65, 35, 65, 13), "#2B2E35", line([(-24, -52), (-26, 40)], 4, "#4A505C", taper=.5, wmin=.3, seed=13101), w=3.6, seed=13100)
    return _tf(o, x, y, k, rot)


C_CUSHION = "#7E5BA6"
C_CUSHION_SH = "#5E4282"
C_CUSHION_HI = "#9C7DC4"


def cushion(x, y, k=1.0, sy=1.0, col=None, seed=0):
    """Круглая подушка для медитации (дно по центру), Ø 300, высота 80·sy."""
    sd = 13200 + seed
    c, csh, chi = col or (C_CUSHION, C_CUSHION_SH, C_CUSHION_HI)
    hgt = 80 * sy
    body = [(-150, -hgt + 2), (-152, -hgt * .45), (-136, -10), (-90, 0), (90, 0), (136, -10), (152, -hgt * .45), (150, -hgt + 2)]
    inn = blob([(-160, -hgt * .5), (160, -hgt * .5), (160, 6), (-160, 6)], csh)
    for j in range(-3, 4):
        inn += line([(j * 40, -hgt + 10), (j * 44, -6)], 3, csh, taper=.6, wmin=.2, seed=sd + 10 + j)
    o = [shape(body, c, inn, w=4.0, seed=sd)]
    o.append(shape(ellipse_pts(0, -hgt + 2, 150, 42 * min(1.2, sy ** .5), 24), chi,
                   blob(ellipse_pts(20, -hgt + 12, 120, 26, 16), c) + blob(ellipse_pts(0, -hgt + 2, 14, 6, 10), csh), w=3.8, seed=sd + 1))
    return _tf("".join(o), x, y, k)


def mat(x, y, k=1.0, w=640.0, col="#6FA58A", seed=0):
    """Коврик в перспективе, ЦЕНТР, w × 70."""
    sh = lib.mul(col, (.8, .82, .82))
    pts = [(-w / 2, -32, 1), (w / 2, -32, 1), (w / 2 + 34, 34, 1), (-w / 2 - 34, 34, 1)]
    o = shape(pts, col, blob([(-w, 20), (w, 20), (w, 40), (-w, 40)], sh) + line([(-w / 2 + 10, -22), (w / 2 - 10, -22)], 4,
                                                                                 lib.mul(col, (1.12, 1.1, 1.1)), taper=.3, wmin=.4, seed=13301),
              w=3.6, seed=13300 + seed)
    return _tf(o, x, y, k)


_BALLOON = {"red": ("#E0574A", "#B23E33"), "blue": ("#5B8FD6", "#3F6DAE"), "yellow": ("#F2C53D", "#C99A1E"),
            "green": ("#64B07C", "#468A5C"), "orange": ("#F08A3C", "#C46624"), "pink": ("#EE8FB0", "#C46A8A")}


def balloon(x, y, k=1.0, col="red", t=0.0, seed=0, string=180.0, inner=""):
    """Воздушный шарик, ЦЕНТР шара (x, y), r 60×70; нитка вниз длиной string, колышется от t. inner — рисунок на шаре (центр 0,0)."""
    sd = 13400 + seed
    c, csh = _BALLOON.get(col, _BALLOON["red"])
    o = []
    if string > 0:
        pts = [(5 * math.sin(t * 3 + i * .8 + seed) * (i / 6), 78 + string * i / 6) for i in range(7)]
        o.append(line(pts, 3.2, lib.INK, taper=.2, wmin=.6, seed=sd))
    o.append(shape([(-8, 82, 1), (0, 68), (8, 82, 1)], csh, "", w=2.6, seed=sd + 1))
    o.append(shape(ellipse_pts(0, 0, 60, 70, 22), c, blob(ellipse_pts(16, 20, 46, 50, 16), csh) + inner +
                   blob(ellipse_pts(-24, -30, 10, 17, 10, rot=25), "#FFFFFF"), w=3.8, seed=sd + 2))
    return _tf("".join(o), x, y, k)


def att_flame(x, y, k=1.0, t=0.0, u=1.0, seed=0, halo=0.0):
    """Огонёк-внимание (как на хвосте кота): ЦЕНТР ОСНОВАНИЯ (x, y), высота 70·u; язычок колышется."""
    if u <= 0.01:
        return ""
    sw = 7 * math.sin(t * 7 + seed)
    tip = (sw, -70)
    outer = [(0, 4), (-22, -10), (-24, -30), (-10, -52), tip + (1,), (12, -50), (24, -28), (22, -10)]
    inner = [(0, 0), (-12, -10), (-12, -26), (sw * .6, -46, 1), (12, -26), (12, -10)]
    o = ""
    if halo > 0:
        o += glow(x, y - 30 * k * u, 120 * k * u, halo, "#FFC46B")
    o += _tf(shape(outer, "#F28C28", blob(inner, "#FFD24A"), w=3.4, seed=13500 + seed), x, y, k * u)
    return o


def mote(x, y, r=7.0, u=1.0):
    """Пылинка-точка со свечением."""
    o = glow(x, y, r * 7, 0.55 * u, "#FFE7A3") if u > 0 else ""
    return o + blob(ellipse_pts(x, y, r * (0.8 + 0.2 * u), r * (0.8 + 0.2 * u), 12), mix("#E8D9B0", "#FFF2C6", clamp(u)))


def breath_wave(x0, x1, y, amp=30.0, t=0.0, phase=0.0, w=7.0, col="#5C9AD6", n=2.0, seed=0):
    """Волна-лента дыхания от x0 до x1: n периодов, амплитуда amp, бежит со временем."""
    pts = []
    m = 48
    for i in range(m + 1):
        q = i / m
        pts.append((x0 + (x1 - x0) * q, y + amp * math.sin(2 * math.pi * n * q - phase - t * 1.6)))
    return line(pts, w, col, taper=.25, wmin=.4, seed=13600 + seed)


def dash_path(pts, u=1.0, w=6.0, col=None, gap=26.0, dash=16.0, seed=0):
    """Пунктир по точкам (мир); u 0…1 — доля проявленной длины."""
    if u <= 0:
        return ""
    S = lib.sample(pts, False, 2.0)
    L = [0.0]
    for i in range(1, len(S)):
        L.append(L[-1] + math.hypot(S[i][0] - S[i - 1][0], S[i][1] - S[i - 1][1]))
    tot = L[-1] * clamp(u)
    o = []
    s0 = 0.0
    j = 0
    while s0 < tot:
        s1 = min(s0 + dash, tot)
        seg = [(float(S[i][0]), float(S[i][1])) for i in range(len(S)) if s0 <= L[i] <= s1]
        if len(seg) >= 2:
            o.append(line(seg, w, col or lib.INK, taper=.2, wmin=.6, seed=13700 + seed + j))
        s0 += dash + gap
        j += 1
    return "".join(o)


def torch(x, y, k=1.0, on=1.0, wall="#C9B79A", seed=0):
    """Торшер (дно в (x, y)) с небольшим ЧЁТКИМ кругом света на стене вокруг абажура (сплошные тона, без размытия)."""
    cx, cy = x, y - 360 * k
    o = ""
    if on > 0.01:
        o += blob(ellipse_pts(cx, cy, 165 * k, 150 * k, 40), mix(wall, "#FFE7A3", .32 * on))
        o += blob(ellipse_pts(cx, cy, 112 * k, 102 * k, 36), mix(wall, "#FFE7A3", .55 * on))
    return o + lamp_floor(x, y, k, on, seed)


def legs_run(x, y, k=1.0, t=0.0, seed=0, col="#2B2E35"):
    """Две ножки-палочки с ботиночками (бегут), ЦЕНТР таза (x, y), длина 90·k."""
    o = []
    for j, ph in enumerate((0.0, math.pi)):
        a = math.sin(t * 22 + ph) * 0.7
        kx, ky = x + j * 14 * k - 7 * k + math.sin(a) * 40 * k, y + math.cos(a) * 44 * k
        b = a - 0.3 - 0.7 * (0.5 + 0.5 * math.cos(t * 22 + ph))
        fx, fy = kx + math.sin(b) * 42 * k, ky + math.cos(b) * 42 * k
        o.append(line([(x + j * 14 * k - 7 * k, y), (kx, ky), (fx, fy)], 9 * k, col, taper=0, wmin=1, seed=13800 + seed + j))
        o.append(shape(ellipse_pts(fx + 10 * k, fy + 4 * k, 17 * k, 9 * k, 12), "#C8553D", "", w=3.0, seed=13810 + seed + j))
    return "".join(o)



# ═══════════════════════════════ КОФЕ (рилс 63) ═══════════════════════════════
C_COFFEE_DARK = "#4A2C1A"
C_COFFEE_HI = "#7A5238"
C_WATER = "#6FB7E8"
C_WATER_SH = "#4E95C9"
C_WATER_HI = "#B9E0F7"
C_GLASS2 = "#E8F4F8"
C_GLASS2_SH = "#C6DEE6"
C_TEA = "#D9932E"
C_TEA_SH = "#B0701B"
C_MILK = "#FBF8F0"
C_MILK_SH = "#E4DCCB"
C_MARKER = "#D9362B"
C_POT = "#3E4650"
C_POT_SH = "#2A3038"
C_POT_HI = "#66707C"


def settle(t, t0, a0, a1, freq=1.6, damp=4.2):
    """Затухающий переход a0 → a1 после t0 с перелётом и отскоком (до t0 — a0)."""
    if t <= t0:
        return a0
    return a0 + (a1 - a0) * lib.spring(t - t0, freq, damp)


def _steam(o, t, steam, sd, top=-130, xs=(-26, 0, 26), h=17):
    if steam <= 0.01:
        return
    for j, x0 in enumerate(xs):
        ph = t * 2.2 + j * 2.1
        pts = [(x0 + 9 * math.sin(ph + i * .85) * (0.4 + i / 6), top - 8 - h * i * steam) for i in range(6)]
        ex, ey = pts[-1]
        sg = 1 if j % 2 else -1
        for i in range(1, 8):   # завиток на кончике
            a = math.pi * (0 if sg > 0 else 1) - sg * i * .6
            r = 9 * (1 - i / 10)
            pts.append((ex - sg * 9 + r * math.cos(a), ey + r * math.sin(a)))
        o.append(line(pts, 5.2 * steam, "#A9ADB4", taper=.75, wmin=.12, seed=sd + 10 + j))


def coffee_mug(x, y, k=1.0, rot=0.0, col="white", fill=1.0, steam=0.0, t=0.0, upside=False, seed=0):
    """Кружка кофе 110×130 (дно в (x, y)), ручка справа. fill — уровень кофе 0…1, upside — вверх дном."""
    sd = 14000 + seed * 17
    c, csh, chi = MUG_COLS.get(col, MUG_COLS["white"])
    o = []
    if upside:
        body = [(-52, -128, 1), (-54, -70), (-55, -10, 1), (55, -10, 1), (54, -70), (52, -128, 1)]
        o.append(line([(53, -108), (86, -104), (92, -70), (55, -52)], 17, lib.INK, taper=0, wmin=1, seed=sd + 1))
        o.append(line([(53, -108), (84, -104), (89, -70), (55, -52)], 9, c, taper=0, wmin=1, seed=sd + 2))
        inner = blob([(24, -140), (70, -140), (70, 0), (20, 0)], csh) + line([(-34, -110), (-36, -30)], 7, chi, taper=.4, wmin=.3, seed=sd + 3)
        o.append(shape(body, c, inner, w=4.6, seed=sd))
        o.append(shape(ellipse_pts(0, -10, 55, 11, 18), lib.mul(csh, (.92, .92, .92)), "", w=4.0, seed=sd + 4))   # край-губа на столе
        o[-2] = shape(body, c, inner, w=4.6, seed=sd)
        o.insert(len(o) - 1, "")
        o.append(shape(ellipse_pts(0, -128, 52, 10, 18), chi, blob(ellipse_pts(14, -124, 40, 6, 14), c), w=3.6, seed=sd + 5))   # глухое донышко сверху
        o.append(shape(ellipse_pts(0, -129, 30, 5, 14), c, "", w=2.6, seed=sd + 6))                                             # кольцо-ножка
        return _tf("".join(o), x, y, k, rot)
    o.append(line([(53, -104), (86, -100), (92, -66), (53, -36)], 17, lib.INK, taper=0, wmin=1, seed=sd + 1))
    o.append(line([(53, -104), (84, -100), (89, -66), (53, -36)], 9, c, taper=0, wmin=1, seed=sd + 2))
    body = [(-55, -126, 1), (-54, -50), (-50, -8), (-40, 0, 1), (40, 0, 1), (50, -8), (54, -50), (55, -126, 1)]
    inner = blob([(24, -132), (70, -132), (70, 6), (20, 6)], csh)
    inner += line([(-34, -110), (-35, -34)], 7, chi, taper=.4, wmin=.3, seed=sd + 3)
    o.append(shape(body, c, inner, w=4.6, seed=sd))
    o.append(shape(ellipse_pts(0, -126, 55, 13, 18), lib.mul(csh, (.86, .86, .86)), "", w=4.0, seed=sd + 4))
    fl = clamp(fill)
    if fl > 0.02:
        ry = 13 * (0.55 + 0.45 * fl)
        rx = 46 * (0.8 + 0.2 * fl)
        cy = -126 + 4 + (1 - fl) * 8
        o.append(blob(ellipse_pts(0, cy, rx, ry * .7, 16), C_COFFEE_DARK))
        o.append(blob(ellipse_pts(-12, cy - 2, rx * .35, ry * .18, 10), C_COFFEE_HI))
    else:
        o.append(blob(ellipse_pts(0, -122, 44, 8, 16), lib.mul(csh, (.75, .75, .75))))
    _steam(o, t, steam, sd)
    return _tf("".join(o), x, y, k, rot)


def mug_cut(x, y, k=1.0, glow=0.0, wave=0.0, t=0.0, seed=0, col="white"):
    """Кружка в разрезе 110×130: передняя стенка срезана, внутри почти вся вода (голубая с коричневым оттенком), тонкий кофе сверху."""
    sd = 14100 + seed
    c, csh, chi = MUG_COLS.get(col, MUG_COLS["white"])
    o = []
    o.append(line([(53, -104), (86, -100), (92, -66), (53, -36)], 17, lib.INK, taper=0, wmin=1, seed=sd + 1))
    o.append(line([(53, -104), (84, -100), (89, -66), (53, -36)], 9, c, taper=0, wmin=1, seed=sd + 2))
    outer = [(-55, -126, 1), (-54, -50), (-50, -8), (-40, 0, 1), (40, 0, 1), (50, -8), (54, -50), (55, -126, 1)]
    wall = shape(outer, csh, "", w=4.6, seed=sd)
    o.append(wall)
    # полость (срез стенки — светлая кромка толщиной 9)
    cav = [(-45, -124, 1), (-44, -50), (-41, -14), (-33, -9, 1), (33, -9, 1), (41, -14), (44, -50), (45, -124, 1)]
    lvl = -112
    wv = 7 * clamp(wave)
    surf = [(-46 + 92 * i / 16, lvl + wv * math.sin(i / 16 * 2 * math.pi * 1.5 - t * 9) + 1.5 * math.sin(i * 1.3 + t * 3)) for i in range(17)]
    water = [(-50, 0)] + surf + [(50, 0)]
    wcol = mix("#8FB6C9", C_WATER_HI, clamp(glow) * .7)
    inner = blob(water, wcol)
    inner += blob([(p[0], p[1] + 3) for p in surf] + [(46, lvl + 16), (-46, lvl + 16)], mix(C_COFFEE_HI, "#9C7A5E", .4))   # тонкий кофе сверху
    inner += blob(ellipse_pts(-18, -60, 10, 34, 12), mix(wcol, "#FFFFFF", .35))
    for j in range(5):   # коричневые крапинки — «оттенок кофе»
        inner += blob(ellipse_pts(-28 + 14 * j, -40 - 13 * (j % 3), 3, 3, 8), "#A08672")
    if glow > 0.02:   # волна света бежит снизу вверх
        gy = -14 - 100 * ((t * 1.3) % 1.0)
        inner += blob([(-50, gy), (50, gy - 8), (50, gy + 6), (-50, gy + 14)], mix(wcol, "#FFFFFF", .5 * glow))
    o.append(shape(cav, wcol, inner, w=3.4, seed=sd + 5))
    o.append(line([(-50, -126), (-49, -12)], 4, "#FFFFFF", taper=.3, wmin=.4, seed=sd + 6))
    return _tf("".join(o), x, y, k)


def glass(x, y, k=1.0, rot=0.0, fill=1.0, t=0.0, splash=0.0, seed=0):
    """Стакан 90×140 (дно в (x, y)); вода наливается снизу вверх (fill), splash — плеск каплями над краем."""
    sd = 14200 + seed * 13
    o = []
    body = [(-45, -140, 1), (-40, -70), (-36, -6), (-30, 0, 1), (30, 0, 1), (36, -6), (40, -70), (45, -140, 1)]
    fl = clamp(fill)
    inner = blob(rect_pts(14, -150, 60, 10), C_GLASS2_SH)
    if fl > 0.01:
        top = -10 - 122 * fl
        wob_ = 3 * math.sin(t * 7 + seed)
        inner += blob([(-60, top + wob_), (60, top - wob_), (60, 10), (-60, 10)], C_WATER)
        inner += blob([(14, top), (60, top), (60, 10), (14, 10)], C_WATER_SH)
        inner += blob([(-60, top + wob_ - 2), (60, top - wob_ - 2), (60, top - wob_ + 5), (-60, top + wob_ + 5)], C_WATER_HI)
    inner += line([(-28, -124), (-25, -24)], 6, "#FFFFFF", taper=.4, wmin=.3, seed=sd + 3)
    o.append(shape(body, C_GLASS2, inner, w=4.2, seed=sd))
    o.append(shape(ellipse_pts(0, -140, 45, 9, 16), mix(C_GLASS2, C_WATER_HI, .4 if fl > .95 else 0), "", w=3.4, seed=sd + 4))
    if fl > .95:
        o.append(blob(ellipse_pts(0, -139, 38, 6, 14), C_WATER))
    out = _tf("".join(o), x, y, k, rot)
    if splash > 0.01:
        out += splash_drops(x, y - 145 * k, k, splash, seed)
    return out


def splash_drops(x, y, k=1.0, u=1.0, seed=0, col=None):
    """Капли веером из точки: летят по параболам, уменьшаются; u 0…1."""
    if u <= 0 or u >= 1:
        return ""
    o = []
    for j in range(6):
        a = math.radians(-150 + j * 24)
        v = 90 + 30 * (j % 3)
        px = x + math.cos(a) * v * u * k * 1.4
        py = y + math.sin(a) * v * u * k * 1.4 + 160 * u * u * k
        o.append(drop(px, py, k * .55 * (1 - .5 * u), math.degrees(a) + 90, col or C_WATER))
    return "".join(o)


splash = splash_drops


def tea_cup(x, y, k=1.0, rot=0.0, steam=0.0, t=0.0, seed=0):
    """Чашка чая на блюдце (дно блюдца в (x, y)): чашка 120×90, янтарный чай, ниточка пакетика с ПУСТЫМ ярлычком."""
    sd = 14300 + seed
    o = []
    o.append(shape(ellipse_pts(0, -6, 92, 16, 20), "#F3EFE6", blob(ellipse_pts(0, 2, 84, 8, 16), "#CFC8BA"), w=4.0, seed=sd))
    o.append(line([(56, -78), (84, -74), (86, -50), (52, -36)], 15, lib.INK, taper=0, wmin=1, seed=sd + 1))
    o.append(line([(56, -78), (82, -74), (83, -50), (52, -36)], 8, "#F3EFE6", taper=0, wmin=1, seed=sd + 2))
    body = [(-62, -92, 1), (-58, -50), (-44, -16), (-26, -10, 1), (26, -10, 1), (44, -16), (58, -50), (62, -92, 1)]
    o.append(shape(body, "#F3EFE6", blob([(26, -100), (70, -100), (70, 0), (20, 0)], "#CFC8BA"), w=4.4, seed=sd + 3))
    o.append(shape(ellipse_pts(0, -92, 62, 12, 18), "#CFC8BA", "", w=3.6, seed=sd + 4))
    o.append(blob(ellipse_pts(0, -90, 54, 8.5, 16), C_TEA))
    o.append(blob(ellipse_pts(-14, -92, 16, 2.5, 10), "#F0B85A"))
    sw = 3 * math.sin(t * 2.3 + seed)
    o.append(line([(20, -92), (40, -112), (58 + sw, -118), (66 + sw, -96)], 3.4, "#7A6A58", taper=0, wmin=1, seed=sd + 5))
    o.append(shape(rrect(56 + sw, -96, 82 + sw, -66, 3), "#F2E2B8", blob(rect_pts(56 + sw, -74, 84 + sw, -64), "#D9C493"), w=3.0, seed=sd + 6))
    _steam(o, t, steam, sd, top=-100, xs=(-20, 6), h=15)
    return _tf("".join(o), x, y, k, rot)


def milk_saucer(x, y, k=1.0, t=0.0, ripple=0.0, lick=0.0, seed=0):
    """Блюдце с молоком (центр дна), Ø 260. ripple — круги ряби, lick — вмятина от язычка и капли."""
    sd = 14400 + seed
    o = [shape(ellipse_pts(0, -18, 130, 34, 24), "#9DC3E6", blob(ellipse_pts(0, -4, 120, 18, 20), "#7AA6CF"), w=4.4, seed=sd)]
    o.append(shape(ellipse_pts(0, -24, 100, 24, 22), C_MILK, blob(ellipse_pts(14, -16, 80, 12, 18), C_MILK_SH), w=3.2, seed=sd + 1))
    if ripple > 0.01:
        for j in range(3):
            q = (t * 0.9 + j / 3) % 1.0
            o.append(line(ellipse_pts(-6, -26, 16 + 70 * q, 4 + 16 * q, 20)[3:15], 3.0 * (1 - q) * ripple + .3, "#D9D0BE", taper=.4, wmin=.3,
                          seed=sd + 5 + j))
    if lick > 0.01:
        d = math.sin(math.pi * clamp(lick))
        o.append(blob(ellipse_pts(-6, -26, 24 * d, 7 * d, 14), C_MILK_SH))
    return _tf("".join(o), x, y, k)


def coffee_pot(x, y, k=1.0, rot=0.0, t=0.0, seed=0):
    """Кофейник 150×220 (дно в (x, y)), ручка слева, носик справа; тёмный металл, без надписей и шкал."""
    sd = 14500 + seed
    o = []
    o.append(line([(-56, -180), (-102, -170), (-108, -100), (-60, -60)], 20, lib.INK, taper=0, wmin=1, seed=sd + 1))
    o.append(line([(-56, -180), (-100, -170), (-104, -100), (-60, -60)], 11, C_POT_SH, taper=0, wmin=1, seed=sd + 2))
    o.append(shape([(46, -132, 1), (78, -168), (104, -196, 1), (114, -190, 1), (92, -150), (58, -96, 1)], C_POT, "", w=3.8, seed=sd + 3))
    body = [(-48, -196, 1), (-62, -110), (-74, -20), (-66, 0, 1), (66, 0, 1), (74, -20), (62, -110), (48, -196, 1)]
    inner = blob([(18, -210), (90, -210), (90, 10), (24, 10)], C_POT_SH) + line([(-40, -170), (-56, -30)], 8, C_POT_HI, taper=.4, wmin=.3, seed=sd + 4)
    o.append(shape(body, C_POT, inner, w=4.6, seed=sd))
    o.append(shape(ellipse_pts(0, -196, 50, 10, 16), C_POT_SH, "", w=3.6, seed=sd + 5))
    o.append(shape(ellipse_pts(0, -214, 22, 14, 12), C_POT_HI, "", w=3.4, seed=sd + 6))
    o.append(shape(ellipse_pts(0, -6, 70, 9, 16), C_POT_SH, "", w=3.4, seed=sd + 7))
    return _tf("".join(o), x, y, k, rot)


def pot_spout(x, y, k=1.0, rot=0.0):
    a = math.radians(rot)
    px, py = 110, -194
    return x + k * (px * math.cos(a) - py * math.sin(a)), y + k * (px * math.sin(a) + py * math.cos(a))


def pour_stream(x0, y0, x1, y1, t=0.0, w=16.0, col=None, seed=0, bend=0.35):
    """Струя кофе дугой (x0,y0) → (x1,y1); по струе бегут светлые блики — бесконечная."""
    col = col or C_COFFEE_DARK
    pts = []
    for i in range(21):
        q = i / 20
        x = x0 + (x1 - x0) * q
        y = y0 + (y1 - y0) * (q * q * (1 - bend) + q * bend)
        pts.append((x + 2 * math.sin(q * 9 + t * 14), y))
    o = [line(pts, w + 7, lib.INK, taper=.15, wmin=.7, seed=14600 + seed), line(pts, w, col, taper=.15, wmin=.7, seed=14601 + seed)]
    for j in range(3):
        q0 = (t * 2.2 + j / 3) % 1.0
        seg = [p for i, p in enumerate(pts) if q0 * 20 <= i <= q0 * 20 + 2.5]
        if len(seg) >= 2:
            o.append(line(seg, w * .35, C_COFFEE_HI, taper=.5, wmin=.3, seed=14610 + seed + j))
    return "".join(o)


def jug(x, y, k=1.0, fill=0.8, seed=0):
    """Кувшин воды 150×230 (дно в (x, y)), стекло светлой заливкой, голубая вода, ручка справа, носик слева."""
    sd = 14700 + seed
    o = [line([(52, -200), (98, -186), (100, -96), (60, -70)], 18, lib.INK, taper=0, wmin=1, seed=sd + 1),
         line([(52, -200), (96, -186), (96, -96), (60, -70)], 10, C_GLASS2, taper=0, wmin=1, seed=sd + 2)]
    body = [(-60, -222, 1), (-78, -232, 1), (-62, -200), (-58, -150), (-72, -60), (-62, 0, 1), (62, 0, 1), (72, -60), (58, -150), (60, -222, 1)]
    top = -16 - 190 * clamp(fill)
    inner = blob([(-90, top), (90, top - 4), (90, 10), (-90, 10)], C_WATER) + blob([(20, top), (90, top), (90, 10), (24, 10)], C_WATER_SH)
    inner += blob([(-90, top - 2), (90, top - 6), (90, top + 4), (-90, top + 8)], C_WATER_HI)
    inner += line([(-40, -190), (-46, -30)], 7, "#FFFFFF", taper=.4, wmin=.3, seed=sd + 3)
    o.append(shape(body, C_GLASS2, inner, w=4.4, seed=sd))
    return _tf("".join(o), x, y, k)


def scale_pans(x, y, k=1.0, tilt=0.0):
    a = math.radians(tilt)
    py = -330
    L = 230
    lx, ly = -L * math.cos(a), py - L * math.sin(a)
    rx, ry = L * math.cos(a), py + L * math.sin(a)
    return (x + k * lx, y + k * (ly + 150)), (x + k * rx, y + k * (ry + 150))


def scales(x, y, k=1.0, tilt=0.0, left="", right="", seed=0):
    """Рычажные весы БЕЗ делений: стойка 330, коромысло 460, чаши на подвесах висят отвесно. tilt° — правая чаша ниже при +."""
    sd = 14800 + seed
    o = []
    o.append(shape([(-120, 0, 1), (-100, -34), (100, -34), (120, 0, 1)], C_WOOD, blob(rect_pts(-130, -14, 130, 4), C_WOOD_SH), w=4.4, seed=sd))
    o.append(shape([(-12, -34), (-9, -320), (9, -320), (12, -34)], "#C9A54A", blob(rect_pts(2, -330, 16, -30), "#A08332"), w=4.0, seed=sd + 1))
    a = math.radians(tilt)
    py = -330
    L = 230
    ca, sa = math.cos(a), math.sin(a)
    beam = [(-L - 10, -8), (L + 10, -8), (L + 10, 8), (-L - 10, 8)]
    beam = [(px * ca - qy * sa, py + px * sa + qy * ca) for px, qy in beam]
    o.append(shape([p + (1,) for p in beam], "#C9A54A", "", w=4.0, seed=sd + 2))
    o.append(shape(ellipse_pts(0, py, 16, 16, 12), "#A08332", "", w=3.6, seed=sd + 3))
    o.append(shape([(-10, py - 14, 1), (0, py - 44, 1), (10, py - 14, 1)], "#C9A54A", "", w=3.2, seed=sd + 4))
    for side, sg in ((left, -1), (right, 1)):
        hx, hy = sg * L * ca, py + sg * L * sa
        by = hy + 150
        o.append(line([(hx, hy), (hx - 70, by - 4)], 3.4, "#6E6A60", taper=0, wmin=1, seed=sd + 10 + sg))
        o.append(line([(hx, hy), (hx + 70, by - 4)], 3.4, "#6E6A60", taper=0, wmin=1, seed=sd + 20 + sg))
        o.append(shape(ellipse_pts(hx, hy, 7, 7, 8), "#A08332", "", w=2.6, seed=sd + 30 + sg))
        o.append(f'<g transform="translate({f(hx)} {f(by)})">{side}</g>')
        o.append(shape([(-88, -2, 1), (-70, 16), (70, 16), (88, -2, 1)], "#C9A54A", blob(rect_pts(-90, 6, 90, 20), "#A08332"), w=3.8, seed=sd + 40 + sg))
        o[-1] = f'<g transform="translate({f(hx)} {f(by)})">{o[-1]}</g>'
    return _tf("".join(o), x, y, k)


def red_marker(x, y, k=1.0, rot=0.0, cap=False):
    return marker(x, y, k, rot, C_MARKER, cap)


def _cross_pts(p0, p1, u, seed):
    q = clamp(u)
    n = max(2, int(2 + 30 * q))
    pts = []
    for i in range(n):
        s = q * i / (n - 1)
        x = p0[0] + (p1[0] - p0[0]) * s
        y = p0[1] + (p1[1] - p0[1]) * s
        # лёгкая дуга руки и дрожь
        nx, ny = -(p1[1] - p0[1]), (p1[0] - p0[0])
        L = math.hypot(nx, ny) or 1
        b = 0.04 * math.sin(math.pi * s) * L + 3 * math.sin(s * 23 + seed)
        pts.append((x + nx / L * b, y + ny / L * b))
    return pts


def cross_stroke(p0, p1, q0, q1, u=1.0, w=34.0, seed=0, col=None):
    """Живой крест маркером: первый штрих p0→p1 (u 0…0.5), второй q0→q1 (0.5…1). Жирный, с нажимом, неровный край."""
    if u <= 0:
        return ""
    c = col or C_MARKER
    o = []
    u1 = clamp(u / .5)
    pts = _cross_pts(p0, p1, u1, seed)
    o.append(line(pts, w, c, taper=.35, wmin=.45, seed=14900 + seed, peak=.35))
    if u > .5:
        pts = _cross_pts(q0, q1, clamp((u - .5) / .5), seed + 7)
        if len(pts) >= 2:
            o.append(line(pts, w, c, taper=.35, wmin=.45, seed=14903 + seed, peak=.35))
    return "".join(o)


def marker_tip(p0, p1, q0, q1, u):
    if u <= .5:
        s = clamp(u / .5)
        return p0[0] + (p1[0] - p0[0]) * s, p0[1] + (p1[1] - p0[1]) * s
    s = clamp((u - .5) / .5)
    return q0[0] + (q1[0] - q0[0]) * s, q0[1] + (q1[1] - q0[1]) * s


def clock_hm(h, m=0.0):
    hh = (h % 12) + m / 60.0
    return hh * 30.0, m * 6.0


def clock(x, y, r=90.0, angle_h=0.0, angle_m=0.0, seed=0, face="#F7F1E3", rim="#4F78B5"):
    """Настенные часы (ЦЕНТР) без цифр и делений: обод, циферблат, две стрелки и шпенёк."""
    sd = 15000 + seed
    o = [shape(ellipse_pts(x, y, r, r, 28), rim, "", w=4.4, seed=sd)]
    o.append(shape(ellipse_pts(x, y, r * .84, r * .84, 26), face, blob(ellipse_pts(x + r * .2, y + r * .25, r * .62, r * .55, 20), lib.mul(face, (.94, .93, .9))),
                   w=3.2, seed=sd + 1))
    for ang, L, wd in ((angle_h, .46, 10), (angle_m, .7, 7)):
        a = math.radians(ang - 90)
        o.append(line([(x - math.cos(a) * r * .08, y - math.sin(a) * r * .08), (x + math.cos(a) * r * L, y + math.sin(a) * r * L)], wd * r / 90,
                      lib.INK, taper=.3, wmin=.5, seed=sd + 3 + int(L * 10), peak=.2))
    o.append(blob(ellipse_pts(x, y, r * .07, r * .07, 10), C_MARKER))
    return "".join(o)


def table_lamp(x, y, k=1.0, on=1.0, seed=0, table=True):
    """Настольная лампа (дно в (x, y)) и небольшой ЧЁТКИЙ свет: конус с ровными краями и пятно формы абажура на столе."""
    o = []
    on = clamp(on)
    if on > 0.01 and table:
        g = lin_grad([(0, C_LIGHT_HOT, .55 * on), (1, C_LIGHT, .35 * on)], 0, 0, 0, 1)
        o.append(f'<path d="M{f(x - 6 * k)} {f(y - 110 * k)}L{f(x - 130 * k)} {f(y - 4 * k)}L{f(x + 190 * k)} {f(y - 4 * k)}L{f(x + 76 * k)} {f(y - 110 * k)}Z" '
                 f'fill="url(#{g})" style="mix-blend-mode:screen"/>')
        o.append(blob(ellipse_pts(x + 30 * k, y - 4 * k, 162 * k, 26 * k, 24), mix("#FFE7A3", "#FFF6D8", .3)))
    o.append(lamp_desk(x, y, k, on, -8, seed))
    return "".join(o)


def crack(x, y, k=1.0, rot=0.0, u=1.0, seed=0, col=None):
    """Трещина-штрих: зигзаг из (x, y) вправо длиной 260·k с отростками; u 0…1 — сколько пробежала."""
    if u <= 0:
        return ""
    rs = _rs(15100 + seed)
    pts = [(0, 0)]
    for i in range(1, 9):
        pts.append((i * 32, rs.uniform(-14, 14)))
    n = max(2, int(1 + 8 * clamp(u)))
    P = pts[:n]
    o = [line(P, 6, col or lib.INK, taper=.6, wmin=.2, seed=15110 + seed)]
    for j in (3, 6):
        if n > j + 1:
            bx, by = pts[j]
            o.append(line([(bx, by), (bx + 18, by + 22 * (1 if j == 3 else -1)), (bx + 28, by + 30 * (1 if j == 3 else -1))], 4, col or lib.INK, taper=.7, wmin=.2,
                          seed=15120 + seed + j))
    return _tf("".join(o), x, y, k, rot)


def evap(x, y, k=1.0, u=1.0, t=0.0, seed=0):
    """Дымок испарения: маленькие сплошные завитки поднимаются над точкой."""
    return smoke_curls(x, y, k * .55, u, t, seed + 40, "#E3E6EA", 2)


def zzz(x, y, k=1.0, t=0.0, u=1.0):
    """Три Z: растут и поднимаются по очереди, каждая — свой цикл 1.8 с."""
    if u <= 0.01:
        return ""
    o = []
    for j in range(3):
        q = ((t / 1.8) + j / 3) % 1.0
        s = k * (0.55 + 0.6 * q) * clamp(u)
        if q > .9:
            s *= (1 - q) / .1
        o.append(z_mark(x + 40 * q * k + 20 * j * k, y - 150 * q * k, s, 1.0))
    return "".join(o)


def gloom(x, y, k=1.0, t=0.0, u=1.0, seed=0):
    """Тучка-закорючка (ЦЕНТР дна): тёмная, клубится, внутри спиралька-каракуля."""
    if u <= 0.01:
        return ""
    sx, sy = (u, u) if u < 1 else (1.0, 1.0)
    rs = math.sin(t * 2.4 + seed) * 4
    spiral = []
    for i in range(30):
        a = i * .55
        r = 4 + i * 1.4
        spiral.append((r * math.cos(a) + rs, -46 + r * .6 * math.sin(a)))
    inner = line(spiral, 4.2, "#2E323B", taper=.3, wmin=.4, seed=15200 + seed)
    return cloud(x, y + math.sin(t * 3 + seed) * 4, 210, 110, sx, sy, seed=15210 + seed, col=C_STORM, inner=inner, ink_w=4.0)


def dash_arrow(pts, u=1.0, w=6.0, col=None, seed=0):
    """Пунктирная стрелка по точкам, наконечник появляется, когда пунктир дошёл до конца."""
    if u <= 0:
        return ""
    o = dash_path(pts, u, w, col, gap=18.0, dash=22.0, seed=seed)
    if u >= .98:
        (ax, ay), (bx, by) = pts[-2], pts[-1]
        a = math.atan2(by - ay, bx - ax)
        L = 26
        o += line([(bx - L * math.cos(a - .5), by - L * math.sin(a - .5)), (bx, by), (bx - L * math.cos(a + .5), by - L * math.sin(a + .5))], w * 1.1,
                  col or lib.INK, taper=.2, wmin=.5, seed=15300 + seed)
    return o


def heart(x, y, k=1.0, beat=0.0, seed=0):
    """Сердце (ЦЕНТР), 90·k; beat 0…1 — толчок: раздувается и вокруг штрихи удара."""
    s = k * (1 + .22 * math.sin(math.pi * clamp(beat)))
    pts = []
    for i in range(32):
        a = 2 * math.pi * i / 32
        px = 16 * math.sin(a) ** 3
        py = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((px * 2.8, py * 2.8))
    o = shape(pts, "#D9483B", blob(ellipse_pts(14, 10, 22, 18, 12), "#A5322A") + blob(ellipse_pts(-16, -14, 8, 6, 8), "#F08A7C"), w=4.0, seed=15400 + seed)
    out = _tf(o, x, y, s)
    if 0 < beat < 1:
        out += clink(x, y, k * 1.4, beat, seed + 5, "#D9483B")
    return out
