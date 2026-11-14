"""Общие предметы рилса 64 «спасибо» — ОДИН вид для групп A…F (своих копий не рисовать). Автор — группа A.
Основа — props.py рилса 63 целиком (всё как было), сверху — раздел СПАСИБО (в конце файла). Букв и цифр нет нигде.
Свет — только небольшой и чёткий (table_lamp, torch, chest_glow); огромных мягких овалов не класть.

СПАСИБО (новое в 64; (x, y) — ЦЕНТР, если не сказано иначе; k — масштаб; seed — своё зерно штрихов):
  card(x, y, k, rot, open, inside, write, seed, col)   открытка 170×230·k: обложка с сердечком; open 0…1 — обложка раскрывается
                        влево вокруг корешка (видна её изнанка, потом обе страницы); inside "blank" | "lines" — внутри пусто или
                        строки-штрихи; write 0…1 — сколько строк уже написано (для "lines"). (x, y) — центр закрытой открытки,
                        раскрытая центрируется сама; droop 0…1 — открытка поникает (угол уходит вниз, лёгкий изгиб).
  letter(x, y, k, rot, w, h, write, fold, seed, sy)    письмо: лист w×h с волнистыми строками; write 0…1 — строки пишутся по одной
                        (дробная — текущая строка частично); fold 0…1 — нижняя половина загибается вверх (складывается пополам);
                        letter_tip(x, y, k, rot, w, h, write) → (x, y) где кончик пера на текущей строке (мир).
  pen(x, y, k, rot, cap, seed)                          ручка 180·k с колпачком, ЦЕНТР; при rot=0 кончик ВНИЗ (в (0, +90·k));
                        cap 0…1 — колпачок снят и отведён назад. pen_tip(x, y, k, rot) → кончик в мире.
  click(x, y, k, u, seed)                               щелчок колпачка: короткие штрихи-искры (u 0…1)
  photo_frame(x, y, k, rot, face, inner, seed)          рамка 200×160·k со старой фотографией; face 1 — лицом к нам, 0 — оборотом
                        (переворот — через ребро, виден торец); inner — SVG фото (локально: (0, 0) — центр фото, 160×120)
  drawer(x, y, w, h, out, seed, inner, col)             ящик стола спереди, (x, y) — ЦЕНТР лицевой панели закрытого ящика; out 0…1 —
                        выдвинут (панель опускается и растёт, видно нутро); inner — SVG внутри (локально: (0, 0) — центр нутра).
                        drawer_slot(x, y, w, h, out) → (cx, cy) центр нутра в мире.
  handset(x, y, k, rot)                                 мобильник-силуэт без экрана (то же, что mobilnik)
  gloom_burst(x, y, k, u, seed)                         тучка лопается: клочья и штрихи разлетаются (u 0…1), к 1 — пусто
  sun(x, y, r, rays, t, seed)                           солнце (ЦЕНТР) с лучами пером; rays 0…1 — лучи дорисовываются по одному
  house(x, y, k, warm, seed)                            домик (ЦЕНТР ДНА) 220×230·k; warm 0…1 — от серого к тёплому, окна светятся
  tree(x, y, k, warm, t, seed)                          деревце (ЦЕНТР ДНА) 150×240·k; крона колышется; warm — от серого к зелёному
  speech_bubble(x, y, w, h, u, seed, tail)              пустой пузырь речи (ЦЕНТР); u 0…1 — масштаб (выскок/сдувание задаёт сцена);
                        tail=(dx, dy) — кончик хвостика относительно низа пузыря
  chest_glow(x, y, k, t, u, beat, seed)                 огонёк в груди: маленький язычок и свет ТОЛЬКО вокруг (r ≈ 80·k); beat 0…1 — толчок
  heart_stroke(x, y, k, u, seed, col, w)                сердечко штрихом пера, дорисовывается по u 0…1 (ЦЕНТР)
  sparkles(x, y, k, u, t, seed, n, col, r)              искорки-штрихи (четыре луча пером) вокруг точки, мерцают; u — сила
  purr(x, y, k, t, u, seed)                             штрихи мурлыканья: дуги-волны бегут от точки вбок и вверх
  calendar(x, y, w, h, stamps, glow, flip, t, seed)     календарь-сетка 7×5 БЕЗ цифр и названия, кольца сверху; stamps 0…35 (дробное —
                        текущее солнышко выскакивает); glow 0…1 — лист светится (тёплая бумага + чёткий ореол по краю);
                        flip 0…1 — лист переворачивается вверх через ребро. calendar_cell(x, y, w, h, i) → центр клетки i.
  sun_stamp(x, y, r, u, seed)                           маленькое солнышко-штамп (ЦЕНТР), u — выскок (через pop)
  bookshelf(x, y, w, h, shelves, seed)                  книжная полка (ЦЕНТР ДНА) с пустыми корешками
  memory_bubble(x, y, w, h, u, seed, inner, head, thread, pale, warm)
                        пузырь-воспоминание: облачко-рамка с картинкой (inner, локально (0, 0) — центр, режется облаком);
                        u — масштаб (pop задаёт сцена); head=(hx, hy) — макушка в мире, thread 0…1 — ниточка к голове;
                        pale 0…1 — блёкнет (обесцвечивание фильтром, НЕ прозрачность); warm 0…1 — тёплая рамка и свет вокруг
  day_arc(cx, cy, R, phase, seed)                       солнце/луна по дуге: phase 0…1 — день (солнце слева→вверх→вправо), 1…2 — ночь
                        (луна); → (svg, night 0…1)
  desat(u)                                              атрибут filter обесцвечивания/осветления (u 0…1), без полупрозрачности
  C_CARD, C_CARD_SH, C_HEART, C_LETTER — цвета

(Ниже — как было в 63.)
Общие предметы рилса 63 «кофе» — ОДИН вид для групп A…F (своих копий не рисовать). Автор — группа A.
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
  scales(x, y, k, tilt, left, right, seed, post=330, hang=220)                 рычажные весы без делений: (x, y) — центр основания; tilt° (+ — правая
                                чаша ниже); left/right — SVG на чаше (локальные координаты: (0, 0) — центр дна груза на чаше)
  scale_pans(x, y, k, tilt, post, hang)                                  → ((lx, ly), (rx, ry)) — где в мире стоят грузы на чашах
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


HANG = 220   # длина подвеса чаши


def scale_pans(x, y, k=1.0, tilt=0.0, post=330.0, hang=HANG):
    a = math.radians(tilt)
    py = -post
    L = 230
    lx, ly = -L * math.cos(a), py - L * math.sin(a)
    rx, ry = L * math.cos(a), py + L * math.sin(a)
    return (x + k * lx, y + k * (ly + hang)), (x + k * rx, y + k * (ry + hang))


def scales(x, y, k=1.0, tilt=0.0, left="", right="", seed=0, post=330.0, hang=HANG):
    """Рычажные весы БЕЗ делений: стойка 330, коромысло 460, чаши на подвесах 220 висят отвесно. tilt° — правая чаша ниже при +."""
    sd = 14800 + seed
    o = []
    o.append(shape([(-120, 0, 1), (-100, -34), (100, -34), (120, 0, 1)], C_WOOD, blob(rect_pts(-130, -14, 130, 4), C_WOOD_SH), w=4.4, seed=sd))
    o.append(shape([(-12, -34), (-9, 10 - post), (9, 10 - post), (12, -34)], "#C9A54A", blob(rect_pts(2, -post, 16, -30), "#A08332"), w=4.0, seed=sd + 1))
    a = math.radians(tilt)
    py = -post
    L = 230
    ca, sa = math.cos(a), math.sin(a)
    beam = [(-L - 10, -8), (L + 10, -8), (L + 10, 8), (-L - 10, 8)]
    beam = [(px * ca - qy * sa, py + px * sa + qy * ca) for px, qy in beam]
    o.append(shape([p + (1,) for p in beam], "#C9A54A", "", w=4.0, seed=sd + 2))
    o.append(shape(ellipse_pts(0, py, 16, 16, 12), "#A08332", "", w=3.6, seed=sd + 3))
    o.append(shape([(-10, py - 14, 1), (0, py - 44, 1), (10, py - 14, 1)], "#C9A54A", "", w=3.2, seed=sd + 4))
    for side, sg in ((left, -1), (right, 1)):
        hx, hy = sg * L * ca, py + sg * L * sa
        by = hy + hang
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


# ═════════════════════════════ СПАСИБО (рилс 64) ═════════════════════════════

C_CARD = "#6E92C9"
C_CARD_SH = "#4A6FA5"
C_HEART = "#D9483B"
C_HEART_SH = "#A5322A"
C_LETTER = "#FBF6E6"
C_LETTER_LINE = "#4A5570"


def _heart_pts(s=1.0, n=32):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        px = 16 * math.sin(a) ** 3
        py = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        out.append((px * s, py * s + 1.5 * s))
    return out


def _wavy(x0, x1, y, seed, amp=3.2, per=26.0):
    rs = _rs(seed)
    ph = rs.uniform(0, 6.28)
    n = max(3, int((x1 - x0) / 6))
    return [(x0 + (x1 - x0) * i / (n - 1), y + amp * math.sin(ph + (x1 - x0) * i / (n - 1) / per * 6.28) + rs.uniform(-.6, .6)) for i in range(n)]


def _lines_block(x0, x1, y0, step, n, write, seed, w=3.4, col=None, first_indent=18.0):
    """n волнистых строк-штрихов; write 0…1 — сколько написано (последняя частично)."""
    o = []
    rs = _rs(seed)
    lens = [rs.uniform(.72, 1.0) for _ in range(n)]
    lens[-1] = rs.uniform(.38, .55)
    done = clamp(write) * n
    for j in range(n):
        u = clamp(done - j)
        if u <= 0.01:
            break
        xa = x0 + (first_indent if j == 0 else 0)
        xb = xa + (x1 - xa) * lens[j]
        xe = xa + (xb - xa) * u
        if xe - xa < 6:
            continue
        o.append(line(_wavy(xa, xe, y0 + step * j, seed + 31 * j), w, col or C_LETTER_LINE, taper=.25, wmin=.5, seed=seed + 7 + j))
    return "".join(o)


def _lines_tip(x0, x1, y0, step, n, write, seed, first_indent=18.0):
    rs = _rs(seed)
    lens = [rs.uniform(.72, 1.0) for _ in range(n)]
    lens[-1] = rs.uniform(.38, .55)
    done = clamp(write) * n
    j = min(n - 1, int(done))
    u = clamp(done - j) if done < n else 1.0
    xa = x0 + (first_indent if j == 0 else 0)
    xb = xa + (x1 - xa) * lens[j]
    pts = _wavy(xa, xa + max(6.0, (xb - xa) * u), y0 + step * j, seed + 31 * j)
    return pts[-1]


def card(x, y, k=1.0, rot=0.0, open=0.0, inside="blank", write=0.0, seed=0, col=None, droop=0.0):
    """Открытка 170×230 с сердечком на обложке; корешок слева; open — обложка раскрывается влево через ребро."""
    sd = 16000 + seed * 11
    cc = col or C_CARD
    csh = lib.mul(cc, (.78, .8, .84))
    w, h = 170.0, 230.0
    op = clamp(open)
    cx = -w / 2 * (1 - op)          # смещение: закрытая центрирована по себе, раскрытая — по развороту
    hh = h / 2
    d = droop * 26
    o = []
    # правая (внутренняя) страница
    page = [(0, -hh, 1), (w, -hh + d * .3, 1), (w + d * .2, hh + d, 1), (0, hh, 1)]
    inner_pg = blob(rect_pts(-6, hh - 18, w + 10, hh + 30), C_PAGE_SH)
    if inside == "lines":
        inner_pg += _lines_block(22, w - 18, -hh + 50, 26, 6, write, sd + 50, w=3.0)
    if op > 0.02:
        o.append(shape(page, C_PAGE, inner_pg, w=3.2, seed=sd))
    else:
        o.append(shape(page, csh, "", w=3.2, seed=sd))
    # обложка: поворот вокруг корешка (x=0) через ребро
    a = math.pi * op
    sx = math.cos(a)
    if abs(sx) > 0.035:
        cov = [(0, -hh, 1), (w, -hh + d * .3, 1), (w + d * .2, hh + d, 1), (0, hh, 1)]
        if sx > 0:
            ins = blob(rect_pts(w - 18, -hh - 4, w + 14, hh + 30), csh)
            ins += shape(_heart_pts(3.3), C_HEART, blob(ellipse_pts(14, 12, 18, 15, 10), C_HEART_SH) + blob(ellipse_pts(-15, -12, 7, 5, 8), "#F08A7C"),
                         w=3.4, seed=sd + 3, attrs=f'transform="translate({w / 2:.1f} {-6 + d * .5:.1f})"')
            ins += line([(14, -hh + 14), (w - 14, -hh + 14 + d * .3)], 3, lib.mul(cc, (1.12, 1.1, 1.06)), taper=.3, wmin=.5, seed=sd + 4)
            ins += line([(14, hh - 14), (w - 14, hh - 14 + d)], 3, lib.mul(cc, (1.12, 1.1, 1.06)), taper=.3, wmin=.5, seed=sd + 5)
            body = shape(cov, cc, ins, w=3.6, seed=sd + 2)
        else:
            body = shape(cov, C_PAGE, blob(rect_pts(-6, hh - 16, w + 10, hh + 30), C_PAGE_SH), w=3.4, seed=sd + 6)
        # ребро-торец, когда почти боком
        o.append(f'<g transform="scale({sx:.4f} 1)">{body}</g>')
    else:
        o.append(blob(rect_pts(-4, -hh, 4, hh), csh) + line([(0, -hh), (0, hh)], 4, lib.INK, taper=.1, wmin=.8, seed=sd + 8))
    g = f'<g transform="translate({f(cx)} 0)">{"".join(o)}</g>'
    return _tf(g, x, y, k, rot + droop * 8)


def letter(x, y, k=1.0, rot=0.0, w=200.0, h=260.0, write=1.0, fold=0.0, seed=0, sy=1.0):
    """Письмо: лист с волнистыми строками; write — пишется строка за строкой; fold — нижняя половина загибается вверх."""
    sd = 16200 + seed * 13
    hw, hh = w / 2, h / 2
    n = max(4, int((h - 60) / 26))
    step = (h - 60) / n
    fo = clamp(fold)
    o = []
    # верхняя половина (с её строками)
    top = [(-hw, -hh, 1), (hw, -hh, 1), (hw, 0, 1), (-hw, 0, 1)]
    full = [(-hw, -hh, 1), (hw, -hh, 1), (hw, hh, 1), (-hw, hh, 1)]
    lines_all = _lines_block(-hw + 20, hw - 18, -hh + 34, step, n, write, sd + 40, w=3.2)
    if fo <= 0.01:
        o.append(shape(full, C_LETTER, blob(rect_pts(-hw - 4, hh - 12, hw + 4, hh + 6), C_PAGE_SH) + lines_all, w=3.2, seed=sd))
    else:
        c = clip_rect(-hw - 10, -hh - 10, w + 20, hh + 10)
        o.append(shape(top, C_LETTER, f'<g clip-path="url(#{c})">{lines_all}</g>', w=3.2, seed=sd))
        # нижняя половина поворачивается вокруг линии сгиба (y=0) вверх: масштаб по y = cos
        cy = math.cos(math.pi * fo)
        bot = [(-hw, 0, 1), (hw, 0, 1), (hw, hh, 1), (-hw, hh, 1)]
        if cy > 0.03:
            c2 = clip_rect(-hw - 10, 0, w + 20, hh + 10)
            body = shape(bot, C_LETTER, f'<g clip-path="url(#{c2})">{lines_all}</g>', w=3.2, seed=sd + 1)
        elif cy < -0.03:
            body = shape(bot, lib.mul(C_LETTER, (.93, .92, .88)), line([(-hw + 14, hh - 18), (hw - 20, hh - 22)], 2.4, C_PAGE_SH, taper=.3, wmin=.5, seed=sd + 3),
                         w=3.2, seed=sd + 2)
        else:
            body = line([(-hw, 0), (hw, 0)], 4.5, lib.INK, taper=.1, wmin=.8, seed=sd + 4)
        o.append(f'<g transform="scale(1 {cy if abs(cy) > .03 else 1:.4f})">{body}</g>')
        if fo > 0.97:
            o.append(line([(-hw + 4, 2), (hw - 4, 1)], 2.6, C_PAGE_SH, taper=.3, wmin=.5, seed=sd + 5))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k:.5f} {k * sy:.5f})">{"".join(o)}</g>'


def letter_tip(x, y, k=1.0, rot=0.0, w=200.0, h=260.0, write=1.0, seed=0):
    sd = 16200 + seed * 13
    hw, hh = w / 2, h / 2
    n = max(4, int((h - 60) / 26))
    step = (h - 60) / n
    px, py = _lines_tip(-hw + 20, hw - 18, -hh + 34, step, n, write, sd + 40)
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return (x + k * (px * c - py * s), y + k * (px * s + py * c))


def pen(x, y, k=1.0, rot=0.0, cap=0.0, seed=0):
    """Ручка с колпачком, ЦЕНТР; rot=0 — кончик вниз (0, +90). cap 0…1 — колпачок снимается назад (вверх)."""
    sd = 16400 + seed
    body = shape(rrect(-9, -80, 9, 62, 7), "#2F4F86", blob(rect_pts(3, -84, 12, 66), "#22396A") + blob(rect_pts(-6, -60, -2, 40), "#5577B0"), w=3.0, seed=sd)
    body += shape([(-9, 60, 1), (9, 60, 1), (3, 84, 1), (0, 90, 1), (-3, 84, 1)], "#C9CDD6", blob([(2, 62), (9, 62), (3, 84)], "#8E939E"), w=2.6, seed=sd + 1)
    body += shape(rrect(-5, -92, 5, -78, 3), "#2F4F86", "", w=2.4, seed=sd + 2)
    cu = clamp(cap)
    if cu < 0.999:   # колпачок надет на кончик (снизу)
        dy = -cu * 0  # при снятии колпачок уходит в сторону — рисуем его ниже отдельно
        cp = shape(rrect(-11, 40, 11, 96, 8), "#2F4F86", blob(rect_pts(4, 36, 14, 100), "#22396A"), w=3.0, seed=sd + 3)
        cp += line([(12, 46), (16, 50), (16, 84)], 4, C_METAL, taper=.1, wmin=.8, seed=sd + 4)
        off = lib.ease_io(cu)
        body += f'<g transform="translate({f(30 * off)} {f(120 * off)}) rotate({f(-25 * off)} 0 68)">{cp}</g>' if cu > 0 else cp
    return _tf(body, x, y, k, rot)


def pen_tip(x, y, k=1.0, rot=0.0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return (x - 90 * k * s, y + 90 * k * c)


def click(x, y, k=1.0, u=1.0, seed=0):
    """Щелчок колпачка: три коротких штриха-искры (u 0…1)."""
    if u <= 0 or u >= 1:
        return ""
    o = []
    for j, a in enumerate((-120, -60, -15)):
        r = math.radians(a)
        r0, r1 = (14 + 18 * u) * k, (30 + 30 * u) * k
        o.append(line([(x + r0 * math.cos(r), y + r0 * math.sin(r)), (x + r1 * math.cos(r), y + r1 * math.sin(r))], 5 * k * (1 - .5 * u), lib.INK, taper=.5,
                      wmin=.3, seed=16450 + seed + j))
    return "".join(o)


def photo_frame(x, y, k=1.0, rot=0.0, face=1.0, inner="", seed=0):
    """Рамка 200×160 со старой фото; face — 1 лицом, 0 оборотом (поворот вокруг горизонтальной оси через ребро)."""
    sd = 16500 + seed
    a = math.pi * (1 - clamp(face))
    sy = math.cos(a)
    o = []
    if abs(sy) > 0.04:
        if sy > 0:
            ph = blob(rect_pts(-84, -64, 84, 64), "#E9DDC2") + inner
            c = clip_rect(-80, -60, 160, 120)
            fr = shape(rect_pts(-100, -80, 100, 80), C_WOOD, blob(rect_pts(-100, 60, 100, 82), C_WOOD_SH) + blob(rect_pts(-100, -80, 100, -72), C_WOOD_HI),
                       w=3.6, seed=sd)
            fr += shape(rect_pts(-80, -60, 80, 60), "#E9DDC2", f'<g clip-path="url(#{c})">{ph}</g>', w=2.8, seed=sd + 1)
            fr += line([(-70, -50), (-30, -56)], 3, "#FFFFFF", taper=.5, wmin=.3, seed=sd + 2)
        else:
            fr = shape(rect_pts(-100, -80, 100, 80), C_WOOD_SH, shape(rect_pts(-84, -64, 84, 64), "#A7835A", "", w=2.4, seed=sd + 4) +
                       shape([(-14, 30), (14, 30), (8, 76), (-8, 76)], "#8A6A44", "", w=2.4, seed=sd + 5), w=3.6, seed=sd + 3)
        o.append(f'<g transform="scale(1 {sy:.4f})">{fr}</g>')
    else:
        o.append(shape(rect_pts(-100, -7, 100, 7), C_WOOD_SH, "", w=3.2, seed=sd + 6))
    return _tf("".join(o), x, y, k, rot)


def drawer_slot(x, y, w=360.0, h=110.0, out=0.0):
    u = clamp(out)
    return (x, y + 30 * u - h * .55 * u)


def drawer(x, y, w=360.0, h=110.0, out=0.0, seed=0, inner="", col=None):
    """Ящик стола спереди; out 0…1 — выдвигается к зрителю: панель чуть растёт и опускается, сверху видно нутро."""
    sd = 16600 + seed
    u = clamp(out)
    c = col or C_WOOD
    csh = lib.mul(c, (.78, .74, .7))
    o = []
    # проём в столе (тёмный)
    o.append(blob(rect_pts(x - w / 2, y - h / 2, x + w / 2, y + h / 2), "#3A2A1C"))
    s = 1 + .1 * u
    dy = 30 * u
    if u > 0.02:
        depth = h * .9 * u
        top_y = y - h / 2 * s + dy
        box = [(x - w / 2 * s + 6, top_y, 1), (x + w / 2 * s - 6, top_y, 1), (x + w / 2 - 4, top_y - depth, 1), (x - w / 2 + 4, top_y - depth, 1)]
        nut = blob(rect_pts(x - w, top_y - depth - 10, x + w, top_y + 10), "#6E4A2C")
        sx, sy = drawer_slot(x, y, w, h, u)
        if inner:
            nut += f'<g transform="translate({f(sx)} {f(sy)})">{inner}</g>'
        o.append(shape(box, "#6E4A2C", nut, w=3.4, seed=sd + 1))
        o.append(blob([(x - w / 2 * s + 6, top_y - 2), (x - w / 2 + 4, top_y - depth), (x - w / 2 + 20, top_y - depth), (x - w / 2 * s + 26, top_y - 2)], csh))
    face = rect_pts(x - w / 2 * s, y - h / 2 * s + dy, x + w / 2 * s, y + h / 2 * s + dy)
    fin = blob(rect_pts(x - w, y + h / 2 * s + dy - 14, x + w, y + h + dy), csh) + blob(rect_pts(x - w, y - h / 2 * s + dy - 2, x + w, y - h / 2 * s + dy + 8),
                                                                                         lib.mul(c, (1.12, 1.1, 1.08)))
    o.append(shape(face, c, fin, w=3.8, seed=sd + 2))
    o.append(shape(rrect(x - 34 * s, y - 9 * s + dy, x + 34 * s, y + 9 * s + dy, 8), C_METAL, blob(rect_pts(x - 40, y + 2 + dy, x + 40, y + 14 + dy), C_METAL_SH),
                   w=3.0, seed=sd + 3))
    return "".join(o)


def handset(x, y, k=1.0, rot=0.0):
    return mobilnik(x, y, k, rot)


def gloom_burst(x, y, k=1.0, u=0.0, seed=0):
    """Тучка лопается: серые клочья разлетаются и мельчают, штрихи-лучи разрыва (u 0…1)."""
    if u <= 0 or u >= 1:
        return ""
    rs = _rs(16700 + seed)
    o = []
    e = lib.ease_out(u, 2)
    for j in range(9):
        a = rs.uniform(0, 2 * math.pi)
        d = rs.uniform(90, 190) * e
        r = rs.uniform(16, 32) * (1 - u) ** 1.2
        if r < 2:
            continue
        px, py = x + k * d * math.cos(a), y - 55 * k + k * d * math.sin(a) + 60 * k * u * u
        o.append(shape(ellipse_pts(px, py, r * k, r * k * .8, 10, jitter=.12, seed=j + seed), C_STORM, "", w=3.0 * (1 - u * .5), seed=16710 + seed + j))
    for j in range(8):
        a = 2 * math.pi * j / 8 + .3
        r0, r1 = (60 + 90 * e) * k, (90 + 150 * e) * k
        if u < .7:
            o.append(line([(x + r0 * math.cos(a), y - 55 * k + r0 * math.sin(a)), (x + r1 * math.cos(a), y - 55 * k + r1 * math.sin(a))], 7 * k * (1 - u), lib.INK,
                          taper=.5, wmin=.3, seed=16730 + seed + j))
    return "".join(o)


def sun(x, y, r=70.0, rays=1.0, t=0.0, seed=0):
    """Солнце: диск с бликом, лучи пером — дорисовываются по одному (rays 0…1), чуть пульсируют."""
    sd = 16800 + seed
    o = []
    n = 10
    pr = clamp(rays) * n
    for j in range(n):
        q = clamp(pr - j)
        if q <= 0:
            break
        a = 2 * math.pi * j / n - math.pi / 2 + .08 * math.sin(t * 1.5)
        L = (1.0 + .08 * math.sin(t * 5 + j)) * r * .62
        r0 = r * 1.22
        r1 = r0 + L * q
        mid = (r0 + r1) / 2
        o.append(line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + mid * math.cos(a + .05), y + mid * math.sin(a + .05)),
                       (x + r1 * math.cos(a), y + r1 * math.sin(a))], r * .13, "#E9A21F", taper=.5, wmin=.25, seed=sd + j))
    o.append(shape(ellipse_pts(x, y, r, r, 22), "#F7C948", blob(ellipse_pts(x + r * .25, y + r * .3, r * .8, r * .7, 16), "#EBAE2E") +
                   blob(ellipse_pts(x - r * .38, y - r * .38, r * .2, r * .14, 10, rot=-.6), "#FFF1B8"), w=4.0, seed=sd + 20))
    return "".join(o)


def house(x, y, k=1.0, warm=1.0, seed=0):
    """Домик (ЦЕНТР ДНА): стены, крыша, дверь, два окна; warm 0 — серый, 1 — тёплый и окна светятся."""
    sd = 16900 + seed
    wu = clamp(warm)
    wall = mix("#A9AAB0", "#F2C98A", wu)
    wall_sh = mix("#8B8C93", "#D9A660", wu)
    roof = mix("#6E7079", "#C8553D", wu)
    roof_sh = mix("#55575F", "#9A3B2B", wu)
    win = mix("#5E6270", "#FFD86B", wu)
    o = [shape([(-100, 0, 1), (-100, -140, 1), (100, -140, 1), (100, 0, 1)], wall, blob(rect_pts(50, -150, 110, 10), wall_sh), w=4.0, seed=sd)]
    o.append(shape([(-122, -132, 1), (0, -232, 1), (122, -132, 1)], roof, blob([(10, -232), (130, -132), (40, -132)], roof_sh), w=4.2, seed=sd + 1))
    o.append(shape(rect_pts(56, -222, 82, -170), mix("#7A7C84", "#A5322A", wu), "", w=3.0, seed=sd + 2))
    o.append(shape(rrect(-26, -82, 26, 0, 10), mix("#6E7079", "#8A5B32", wu), blob(ellipse_pts(14, -40, 5, 5, 8), C_METAL), w=3.4, seed=sd + 3))
    for j, wx in enumerate((-66, 66)):
        o.append(shape(rect_pts(wx - 22, -116, wx + 22, -72), win, line([(wx, -116), (wx, -72)], 3, lib.INK, taper=.1, wmin=.8, seed=sd + 6 + j) +
                       line([(wx - 22, -94), (wx + 22, -94)], 3, lib.INK, taper=.1, wmin=.8, seed=sd + 8 + j), w=3.2, seed=sd + 4 + j))
    return _tf("".join(o), x, y, k)


def tree(x, y, k=1.0, warm=1.0, t=0.0, seed=0):
    """Деревце (ЦЕНТР ДНА): ствол и крона-облачко, колышется; warm 0 — серое, 1 — зелёное."""
    sd = 17000 + seed
    wu = clamp(warm)
    sw = 4 * math.sin(t * 1.8 + seed)
    o = [shape([(-12, 0, 1), (-9, -110), (-3, -150, 1), (5, -150, 1), (9, -110), (12, 0, 1)], mix("#7E7F86", "#8A5B32", wu), "", w=3.4, seed=sd)]
    crown = _puff_pts(150, 130, sd + 3, n=8, bump=(.1, .18), cy=0)
    crown = [(p[0] + sw * (1 - (p[1] + 65) / 130), p[1] - 175) + p[2:] for p in crown]
    o.append(shape(crown, mix("#8D9097", "#5C9A78", wu), blob(ellipse_pts(30 + sw, -150, 60, 42, 14), mix("#74777E", "#41735A", wu)) +
                   blob(ellipse_pts(-34 + sw, -205, 22, 16, 10), mix("#A3A6AC", "#7FBF98", wu)), w=4.0, seed=sd + 1))
    return _tf("".join(o), x, y, k)


def speech_bubble(x, y, w=260.0, h=170.0, u=1.0, seed=0, tail=(-60, 70)):
    """Пустой пузырь речи (ЦЕНТР), u — масштаб (0…1+, перелёт задаёт сцена); хвостик к говорящему."""
    if u <= 0.02:
        return ""
    sd = 17100 + seed
    hw, hh = w / 2, h / 2
    pts = ellipse_pts(0, 0, hw, hh, 28)
    a0 = math.atan2(hh * .9, tail[0] * .3 - 20)
    tx, ty = tail[0], hh + tail[1]
    body = []
    # хвостик — отдельной формой под пузырём, его край закрывает тело
    body.append(shape([(tail[0] * .2 - 26, hh * .7, 1), (tx, ty, 1), (tail[0] * .2 + 24, hh * .78, 1)], "#FFFFFF", "", w=3.6, seed=sd + 1))
    body.append(shape(pts, "#FFFFFF", blob(ellipse_pts(hw * .15, hh * .3, hw * .8, hh * .55, 18), "#EEF0F4"), w=4.0, seed=sd))
    body.append(blob([(tail[0] * .2 - 22, hh * .55), (tail[0] * .2 + 20, hh * .6), (tail[0] * .2 + 18, hh * .85), (tail[0] * .2 - 20, hh * .82)], "#EEF0F4"))
    del a0
    return _tf("".join(body), x, y, u)


def chest_glow(x, y, k=1.0, t=0.0, u=1.0, beat=0.0, seed=0):
    """Огонёк в груди: маленький язычок (как у кота на хвосте) и свет только вокруг него."""
    if u <= 0.01:
        return ""
    b = 1 + .25 * math.sin(math.pi * clamp(beat))
    fl = .55 + .45 * (.5 + .5 * math.sin(t * 9 + seed)) * .3 + .3
    o = glow(x, y - 22 * k * u, 80 * k * u * b, min(1.0, .85 * u * fl), "#FFC46B")
    o += att_flame(x, y, .62 * k * b, t, u, seed)
    return o


def heart_stroke(x, y, k=1.0, u=1.0, seed=0, col=None, w=7.0):
    """Сердечко штрихом пера, дорисовывается по u (от выемки сверху по кругу)."""
    if u <= 0.01:
        return ""
    pts = _heart_pts(2.6 * k, 48)
    pts = pts + pts[:1]
    n = max(2, int(len(pts) * clamp(u)))
    return line([(x + p[0], y + p[1]) for p in pts[:n]], w * k, col or C_HEART, taper=.25, wmin=.45, seed=17200 + seed)


def sparkles(x, y, k=1.0, u=1.0, t=0.0, seed=0, n=4, col=None, r=90.0):
    """Искорки-штрихи вокруг точки: четыре луча пером, мерцают (каждая своей фазой)."""
    if u <= 0.01:
        return ""
    rs = _rs(17300 + seed)
    o = []
    c = col or "#F2B632"
    for j in range(n):
        a = rs.uniform(0, 2 * math.pi)
        d = rs.uniform(.55, 1.0) * r * k
        px, py = x + d * math.cos(a), y + d * math.sin(a)
        tw = .55 + .45 * math.sin(t * 6 + j * 2.1 + seed)
        s = 16 * k * clamp(u) * tw
        if s < 2:
            continue
        o.append(line([(px - s, py), (px + s, py)], 4.2 * k, c, taper=.6, wmin=.2, seed=17310 + seed + j))
        o.append(line([(px, py - s * 1.25), (px, py + s * 1.25)], 4.2 * k, c, taper=.6, wmin=.2, seed=17330 + seed + j))
    return "".join(o)


def purr(x, y, k=1.0, t=0.0, u=1.0, seed=0):
    """Штрихи мурлыканья: три дуги-волны бегут от точки вверх-вбок и тают (цикл 0.9 с)."""
    if u <= 0.01:
        return ""
    o = []
    for j in range(3):
        q = (t / .9 + j / 3) % 1.0
        r = (30 + 70 * q) * k
        wv = 5 * k * clamp(u) * (1 - q) ** .7
        if wv < .6:
            continue
        for side in (-1, 1):
            pts = []
            for i in range(9):
                a = math.radians(-60 + 30 * i / 8) if side > 0 else math.radians(-120 - 30 * i / 8)
                rr = r + 4 * k * math.sin(i * 1.7 + t * 20)
                pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
            o.append(line(pts, wv, lib.INK, taper=.5, wmin=.3, seed=17400 + seed + j * 2 + (side > 0)))
    return "".join(o)


def sun_stamp(x, y, r=26.0, u=1.0, seed=0):
    """Солнышко-штамп: оранжевый кружок и восемь коротких лучей; u — выскок (масштаб)."""
    if u <= 0.02:
        return ""
    o = []
    for j in range(8):
        a = 2 * math.pi * j / 8 + seed * .2
        o.append(line([(r * 1.25 * math.cos(a), r * 1.25 * math.sin(a)), (r * 1.7 * math.cos(a), r * 1.7 * math.sin(a))], r * .2, "#E9A21F", taper=.4,
                      wmin=.35, seed=17500 + seed * 9 + j))
    o.append(shape(ellipse_pts(0, 0, r, r, 16), "#F7C948", blob(ellipse_pts(r * .25, r * .3, r * .8, r * .7, 12), "#EBAE2E"), w=3.0, seed=17520 + seed))
    return _tf("".join(o), x, y, u)


def calendar_cell(x, y, w=620.0, h=700.0, i=0):
    gx0, gy0 = x - w / 2 + 30, y - h / 2 + 150
    cw, ch = (w - 60) / 7, (h - 180) / 5
    return (gx0 + cw * (i % 7 + .5), gy0 + ch * (i // 7 + .5))


def calendar(x, y, w=620.0, h=700.0, stamps=0.0, glow=0.0, flip=0.0, t=0.0, seed=0):
    """Настенный календарь-лист: кольца, пустая шапка-полоса, сетка 7×5 без цифр; солнышки по клеткам; flip — лист вверх через ребро."""
    sd = 17600 + seed
    gu = clamp(glow)
    paper_c = mix("#FBF6E6", "#FFF1C2", gu)
    o = []
    fu = clamp(flip)
    sy = math.cos(math.pi * fu)
    hw, hh = w / 2, h / 2
    inner = blob(rect_pts(-hw - 10, hh - 22, hw + 10, hh + 10), mix(C_PAGE_SH, "#F2D98A", gu))
    inner += blob(rect_pts(-hw - 10, -hh - 10, hw + 10, -hh + 110), mix("#C8553D", "#E0703F", gu))
    if sy > 0:
        cw, ch = (w - 60) / 7, (h - 180) / 5
        gx0, gy0 = -hw + 30, -hh + 150
        for r_ in range(6):
            inner += line([(gx0, gy0 + ch * r_), (gx0 + cw * 7, gy0 + ch * r_ + .5)], 2.6, "#9C927C", taper=.1, wmin=.8, seed=sd + 10 + r_)
        for c_ in range(8):
            inner += line([(gx0 + cw * c_, gy0), (gx0 + cw * c_ + .5, gy0 + ch * 5)], 2.6, "#9C927C", taper=.1, wmin=.8, seed=sd + 20 + c_)
        ns = clamp(stamps, 0, 35)
        for i in range(35):
            q = ns - i
            if q <= 0:
                break
            px, py = gx0 + cw * (i % 7 + .5), gy0 + ch * (i // 7 + .5)
            sx_, sy_ = pop(q * .45, 0.0) if q < 3 else (1.0, 1.0)
            s = min(sx_, sy_) if q < 3 else 1.0
            inner += sun_stamp(px, py, min(cw, ch) * .27 * s, 1.0, seed=i)
    o.append(shape(rect_pts(-hw, -hh, hw, hh), paper_c if sy > 0 else lib.mul(paper_c, (.92, .9, .86)), inner if sy > 0 else
                   blob(rect_pts(-hw - 10, hh - 22, hw + 10, hh + 10), C_PAGE_SH), w=4.2, seed=sd))
    body = "".join(o)
    out = []
    if gu > 0.01:   # чёткий тёплый ореол по краю листа (обводка светом, не огромный овал)
        out.append(f'<rect x="{f(x - hw - 14 * gu)}" y="{f(y - hh - 14 * gu)}" width="{f(w + 28 * gu)}" height="{f(h + 28 * gu)}" rx="{f(18 * gu)}" '
                   f'fill="#FFD86B" opacity="{.55 * gu:.3f}" {blur(6)}/>')
    if abs(sy) > 0.03:
        out.append(f'<g transform="translate({f(x)} {f(y - hh)}) scale(1 {sy:.4f}) translate(0 {f(hh)})">{body}</g>')
    else:
        out.append(shape(rect_pts(x - hw, y - hh - 6, x + hw, y - hh + 6), C_PAGE_SH, "", w=3.2, seed=sd + 40))
    for j in range(6):   # кольца
        rx_ = x - hw + 60 + (w - 120) * j / 5
        out.append(line([(rx_ - 8, y - hh + 14), (rx_ - 10, y - hh - 18), (rx_ + 6, y - hh - 26), (rx_ + 10, y - hh - 8)], 6, "#868B96", taper=.1, wmin=.8,
                        seed=sd + 50 + j))
    return "".join(out)


def bookshelf(x, y, w=520.0, h=640.0, shelves=4, seed=0):
    """Книжная полка (ЦЕНТР ДНА): короб, полки, книги с пустыми корешками разных цветов и высот, иногда наклонённые."""
    sd = 17800 + seed
    rs = _rs(sd)
    hw = w / 2
    o = [shape(rect_pts(x - hw, y - h, x + hw, y), C_WOOD_SH, blob(rect_pts(x - hw + 18, y - h + 18, x + hw - 18, y - 18), "#6E4A2C"), w=4.2, seed=sd)]
    cols = [("#C2493D", "#8F3128"), ("#3F6FB0", "#2D5389"), ("#5C9A78", "#41735A"), ("#E0A43A", "#B07A1E"), ("#7E5BA6", "#5E4282"), ("#D9C9A8", "#B0A07F")]
    sh_h = (h - 36) / shelves
    for s_ in range(shelves):
        by = y - 18 - sh_h * s_
        bx = x - hw + 22
        j = 0
        while bx < x + hw - 40:
            bw = rs.uniform(22, 38)
            bh = rs.uniform(.6, .86) * (sh_h - 16)
            c, cs = cols[rs.randrange(len(cols))]
            tilt = rs.random() < .1 and bx < x + hw - 90
            pts = rect_pts(bx, by - bh, bx + bw, by)
            inn = blob(rect_pts(bx + bw * .66, by - bh - 4, bx + bw + 4, by + 4), cs) + line([(bx + 4, by - bh + 14), (bx + bw - 4, by - bh + 14)], 2.4, cs,
                                                                                            taper=.1, wmin=.8, seed=sd + 400 + j)
            bk = shape(pts, c, inn, w=2.8, seed=sd + 100 + s_ * 40 + j)
            if tilt:
                bk = f'<g transform="rotate(14 {f(bx + bw)} {f(by)})">{bk}</g>'
                bx += bw * .4
            o.append(bk)
            bx += bw + rs.uniform(0, 3)
            j += 1
        o.append(shape(rect_pts(x - hw + 10, by, x + hw - 10, by + 14), C_WOOD, blob(rect_pts(x - hw, by + 8, x + hw, by + 16), C_WOOD_SH), w=3.0,
                       seed=sd + 300 + s_))
    return "".join(o)


def desat(u):
    """Атрибут filter: обесцвечивание и осветление (u 0…1) — «бледнеет» без прозрачности."""
    u = clamp(u)
    if u <= 0.005:
        return ""
    q = round(u, 2)
    i = f"ds{int(q * 100)}"
    if not any(f'id="{i}"' in x for x in lib.DEFS):
        s = 1 - .85 * q
        b = .38 * q
        lib.DEFS.append(f'<filter id="{i}" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="{s:.3f}"/>'
                        f'<feComponentTransfer><feFuncR type="linear" slope="{1 - b:.3f}" intercept="{b:.3f}"/><feFuncG type="linear" slope="{1 - b:.3f}" '
                        f'intercept="{b:.3f}"/><feFuncB type="linear" slope="{1 - b:.3f}" intercept="{b:.3f}"/></feComponentTransfer></filter>')
    return f'filter="url(#{i})"'


def memory_bubble(x, y, w=300.0, h=230.0, u=1.0, seed=0, inner="", head=None, thread=0.0, pale=0.0, warm=0.0):
    """Пузырь-воспоминание: облачко-рамка с картинкой; ниточка к голове; pale — блёкнет фильтром; warm — тёплая рамка и свет вокруг."""
    if u <= 0.02:
        return ""
    sd = 17900 + seed
    o = []
    wu = clamp(warm)
    if head is not None and thread > 0.01:
        bx, by = x, y + h * .5 * u
        hx, hy = head
        mx, my = (bx + hx) / 2 + 40 * math.sin(seed), (by + hy) / 2
        pts = [(bx, by), (mx, my), (hx, hy)]
        S = lib.sample(pts, False, 3.0)
        n = max(2, int(len(S) * clamp(thread)))
        o.append(line([(float(p[0]), float(p[1])) for p in S[:n]], 3.6, "#6B6F7A", taper=.3, wmin=.5, seed=sd + 1))
    if wu > 0.01:
        o.append(glow(x, y, max(w, h) * .62 * u, .75 * wu, "#FFD27A"))
    pts = _puff_pts(w, h, sd, n=10, bump=(.08, .14))
    rim = mix("#FFFFFF", "#FFE2A0", wu)
    pic = blob(ellipse_pts(0, 0, w * .62, h * .62, 18), mix("#F4EEDF", "#FFF0CF", wu)) + inner
    pic_g = f'<g {desat(pale)}>{pic}</g>' if pale > 0.005 else pic
    in_pts = _puff_pts(w * .82, h * .78, sd + 5, n=10, bump=(.06, .1))
    body = shape(pts, rim, "", w=4.0, seed=sd + 2) + shape(in_pts, "#F4EEDF", pic_g, w=2.6, seed=sd + 3)
    if pale > 0.005:
        body = f'<g {desat(pale * .7)}>{body}</g>'
    o.append(_tf(body, x, y, u))
    return "".join(o)


def day_arc(cx, cy, R=330.0, phase=0.0, seed=0):
    """Солнце (phase 0…1) и луна (1…2) по дуге слева направо над (cx, cy). → (svg, night 0…1)."""
    ph = phase % 2.0
    q = ph % 1.0
    a = math.pi * (1 - q)
    px, py = cx + R * math.cos(a), cy - R * .8 * math.sin(a)
    if ph < 1:
        night = clamp(1 - min(q, 1 - q) * 8) * 0.0
        s = sun(px, py, 52, 1.0, q * 6, seed)
    else:
        night = clamp(min(q, 1 - q) * 6)
        s = moon(px, py, 40, .6)
    return s, night


# ═════════════════════════════ РИЛС 70 «ПОМИДОРКА» (автор — группа A) ═════════════════════════════
# Букв и цифр нет нигде: циферблат — только риски и красный клин, клавиши пустые, экран — пустая страница / волнистые штрихи.
#   tomato_timer(x, y, k, rot, wedge, ring, shake, leaf_swing, hands, t, seed, arms)
#                         кухонный таймер-помидорка, (x, y) — ЦЕНТР тела, тело 220×180·k (полуширина TOMATO_RX·k, полувысота TOMATO_RY·k).
#                         wedge 0…1 — заведённая доля круга (красный клин на белом циферблате от «12» по часовой):
#                         WEDGE_25 ≈ почти полкруга, WEDGE_2 — тонкий ломтик; ring 0…1 — звон (подскок задаёт сцена, тут — дрожь и дуги);
#                         shake — дрожь тиканья (px·k); leaf_swing — качание листика (градусы); hands 0…1 — ручки-штрихи с
#                         варежками (s11), arms=((dxl, dyl), (dxr, dyr)) — куда тянутся кисти (локально, в единицах k).
#   tomato_dial(x, y, k, rot, wedge, seed)        только белый циферблат с рисками и клином (для макро)
#   tomato_pts(x, y, k, rot)              → dict: top (основание хвостика), left/right (бока для хвата), dial (центр циферблата), r_dial
#   ring_arcs(x, y, k, u, t, seed, r)     дуги-штрихи звона по бокам точки (u — сила, мерцают по t)
#   laptop(x, y, k, open, screen, lines, t, seed, reflect, turn, glow)
#                         ноутбук анфас-сверху, (x, y) — ЦЕНТР ПЕРЕДНЕГО КРАЯ корпуса; корпус 520×200·k (в перспективе), экран 470×300·k.
#                         open 0…1 — крышка поднимается (0 — закрыт, видна крышка сверху); screen "dark" | "reflect" | "page" | "lines";
#                         lines 0…1 — сколько волнистых строк написано; reflect — SVG отражения (локально: (0, 0) — центр экрана,
#                         ширина 470, приглушается само); turn −1…1 — поворот на три четверти (0 — анфас, − влево); glow 0…1 — свет экрана.
#   laptop_pts(x, y, k, open, turn)       → dict: screen (центр), sw, sh, keys (центр клавиатуры), keys_w, hinge, lid_top
#   pedestal(x, y, k, crack, split, seed) тумба-пьедестал (ЦЕНТР ДНА) 300×330·k; crack 0…1 — трещина зигзагом сверху вниз; split 0…1 —
#                         половинки разъезжаются и кренятся. pedestal_top(x, y, k) → (x, y) центр верхней крышки.
#   laurel(x, y, k, u, side, seed)        лавровая веточка (основание в (x, y)), side +1 — вправо-вверх, −1 — влево; u — дорисовка
#   splat(x, y, k, u, drip, t, seed)      красная клякса-помидор с семечками (ЦЕНТР), u 0…1 — растеклась, drip 0…1 — капли стекают вниз
#   mountain(x, y, k, grow, hatch, seed)  гора (ЦЕНТР ОСНОВАНИЯ) 980×1150·k с вершиной-помидоркой и зелёной шапкой-листиком;
#                         grow 0…1 — вырастает снизу вверх (вершина поднимается), hatch 0…1 — склоны штрихуются пером.
#                         mountain_peak(x, y, k, grow) → (x, y) вершина.
#   step_wall(x, y, k, u, glow, t, seed)  ступенька-камень (ЦЕНТР ДНА) 240×80·k, u 0…1 — вытягивается в отвесную стену 240×(80+940u)·k;
#                         glow 0…1 — тёплое свечение ступеньки (чёткий ореол, не овал на весь кадр). step_top(x, y, k, u) → y верха.
#   swing(x, y, k, ang, t, seed, layer)   качели СБОКУ: А-рама 660×760·k (ЦЕНТР ОСНОВАНИЯ), ось сверху, верёвка 520·k, сиденье ребром;
#                         ang — угол качания (градусы, + сиденье уходит вправо); порядок: layer "back" (рамы, дальняя верёвка) →
#                         "seat" → человек без ближней руки → "rope" (ближняя верёвка) → ближняя рука; "all" — без человека.
#                         swing_seat(x, y, k, ang) → (sx, sy, deg) центр сиденья; swing_rope_pts(...) → [(верх, низ)] ближней верёвки.
#   fence(x0, x1, y, k, seed)             штакетник от x0 до x1, низ на y, высота 200·k
#   door(x, y, k, ajar, seed)             закрытая дверь комнаты (ЦЕНТР ДНА) 420×920·k, ручка справа, без табличек; door_handle(x, y, k) → (x, y)
#   wind_lines(x, y, k, u, t, seed, n)    штрихи ветра (бегут влево от точки)
WEDGE_25 = 0.42
WEDGE_2 = 0.045
TOMATO_RX, TOMATO_RY = 112.0, 92.0
C_TOMATO = "#E2412F"
C_TOMATO_SH = "#B52A1F"
C_TOMATO_HI = "#FF7A5E"
C_LEAF = "#4E9A3E"
C_LEAF_SH = "#357029"
C_DIAL = "#FBF8F0"
C_STONE = "#A7A2A0"
C_STONE_SH = "#7F7A7C"


def _tomato_body_pts(rx=TOMATO_RX, ry=TOMATO_RY):
    pts = []
    for i in range(36):
        a = 2 * math.pi * i / 36
        r = 1 - .05 * (.5 + .5 * math.cos(4 * a)) * (1 if math.sin(a) < 0 else .3)     # лёгкие дольки сверху
        y = math.sin(a) * ry * r
        x = math.cos(a) * rx * r * (1 - .06 * (math.sin(a) > 0) * math.sin(a))
        pts.append((x, y - 6 * (math.sin(a) < 0) * (1 - abs(math.cos(a))) ** 3))
    return pts


def tomato_dial(x, y, k=1.0, rot=0.0, wedge=WEDGE_25, seed=0, r=58.0):
    sd = 70100 + seed
    o = [shape(ellipse_pts(0, 0, r, r * .96, 30), C_DIAL, blob(ellipse_pts(r * .18, r * .22, r * .78, r * .7, 20), "#ECE6D8"), w=3.6, seed=sd)]
    wu = clamp(wedge)
    if wu > 0.002:
        n = max(3, int(40 * wu) + 2)
        rr = r * .8
        P = [(0.0, 0.0)] + [(rr * math.sin(2 * math.pi * wu * i / (n - 1)), -rr * math.cos(2 * math.pi * wu * i / (n - 1))) for i in range(n)]
        d = "M0 0 " + " ".join(f"L{f(p[0])} {f(p[1])}" for p in P[1:]) + "Z"
        o.append(f'<path d="{d}" fill="{C_TOMATO}"/>')
        o.append(line([P[1], (0, 0), P[-1]], 2.6, C_TOMATO_SH, taper=.1, wmin=.7, seed=sd + 1))
    for j in range(24):
        a = 2 * math.pi * j / 24
        L = .2 if j % 2 == 0 else .11
        o.append(line([(r * .9 * math.sin(a), -r * .9 * math.cos(a)), (r * (.9 - L) * math.sin(a), -r * (.9 - L) * math.cos(a))],
                      3.0 if j % 2 == 0 else 2.2, lib.INK, taper=.2, wmin=.6, seed=sd + 3 + j))
    o.append(line([(0, 0), (0, -r * .74)], 3.4, lib.INK, taper=.3, wmin=.6, seed=sd + 40))     # стрелка-указатель «12»
    o.append(blob(ellipse_pts(0, 0, r * .09, r * .09, 10), lib.INK))
    return _tf("".join(o), x, y, k, rot)


def tomato_pts(x, y, k=1.0, rot=0.0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def P(px, py):
        return (x + (px * c - py * s) * k, y + (px * s + py * c) * k)
    return dict(top=P(0, -TOMATO_RY + 4), left=P(-TOMATO_RX, 6), right=P(TOMATO_RX, 6), dial=P(0, 10), r_dial=58 * k, bottom=P(0, TOMATO_RY))


def ring_arcs(x, y, k=1.0, u=1.0, t=0.0, seed=0, r=150.0):
    if u <= 0.01:
        return ""
    o = []
    for side in (-1, 1):
        for j in range(3):
            q = clamp(u * (1.25 - j * .2))
            if q <= .02:
                continue
            ph = .5 + .5 * math.sin(t * 38 + j * 1.9 + side)
            rr = (r + 34 * j) * k * (1 + .05 * ph)
            a0, a1 = -.55 * q, .55 * q
            pts = [(x + side * rr * math.cos(a0 + (a1 - a0) * i / 6), y + rr * math.sin(a0 + (a1 - a0) * i / 6)) for i in range(7)]
            o.append(line(pts, (7.5 - 1.5 * j) * k, "#F2B632" if j == 0 else lib.INK, taper=.5, wmin=.25, seed=70200 + seed + j * 3 + side))
    return "".join(o)


def tomato_timer(x, y, k=1.0, rot=0.0, wedge=WEDGE_25, ring=0.0, shake=0.0, leaf_swing=0.0, hands=0.0, t=0.0, seed=0, arms=None,
                 dial=True):
    sd = 70300 + seed
    jx = jy = jr = 0.0
    if shake > 0 or ring > 0:
        a = shake + 9 * ring
        jx = a * math.sin(t * 61 + seed) * .8
        jy = a * math.cos(t * 47 + seed) * .4
        jr = (1.2 * shake / 4 + 6 * ring) * math.sin(t * 53 + seed * .7)
    o = []
    hu = clamp(hands)
    if hu > 0.01:      # ручки-штрихи за телом
        arms = arms or ((-190, 10), (190, 10))
        for side, (ax, ay) in zip((-1, 1), arms):
            sx0, sy0 = side * TOMATO_RX * .9, 18
            ex, ey = sx0 + (ax - sx0) * hu, sy0 + (ay - sy0) * hu
            mx, my = (sx0 + ex) / 2, (sy0 + ey) / 2 - 22
            o.append(line([(sx0, sy0), (mx, my), (ex, ey)], 8, lib.INK, taper=.15, wmin=.7, seed=sd + 1 + side))
            o.append(shape(ellipse_pts(ex, ey, 17, 15, 12), "#FBF8F0", line([(ex - side * 4, ey - 12), (ex - side * 13, ey - 4)], 2.6, seed=sd + 5 + side),
                           w=3.4, seed=sd + 3 + side))
    body = _tomato_body_pts()
    inner = blob([(30, -100), (130, -60), (130, 100), (-20, 100), (60, 40)], C_TOMATO_SH, .95)
    inner += blob(ellipse_pts(-52, -46, 26, 15, 12, rot=-.6), C_TOMATO_HI, .95)
    inner += blob(ellipse_pts(-74, -20, 8, 6, 8), "#FFD3C4")
    for j, xs in enumerate((-58, 0, 58)):
        inner += line([(xs, -80), (xs * 1.18, -10), (xs * 1.05, 70)], 2.4, C_TOMATO_SH, taper=.6, wmin=.15, seed=sd + 10 + j, op=.9)
    o.append(shape(body, C_TOMATO, inner, w=5.0, seed=sd))
    if dial:
        o.append(tomato_dial(0, 10, 1.0, 0, wedge, seed))
    # хвостик и листики
    sw = leaf_swing
    leaves = []
    for j, (a, L) in enumerate(((-150, 62), (-115, 50), (-65, 50), (-30, 62), (-90, 40))):
        aa = math.radians(a + sw * (1 if j % 2 else .7))
        tip = (L * math.cos(aa), -84 + L * math.sin(aa) * .55)
        nx, ny = -math.sin(aa) * 11, math.cos(aa) * 6
        pts = [(-3, -86, 1), (tip[0] * .5 + nx, tip[1] * .5 - 86 * .5 + ny - 2), (tip[0], tip[1], 1), (tip[0] * .5 - nx, tip[1] * .5 - 86 * .5 - ny + 2)]
        leaves.append(shape(pts, C_LEAF if j % 2 == 0 else C_LEAF_SH, "", w=3.0, seed=sd + 20 + j))
    o.append("".join(leaves))
    st_a = math.radians(-90 + sw * 1.4)
    o.append(shape(lib.band([(0, -84), (4 * math.cos(st_a) * 0 + 2, -104), (10 * math.sin(math.radians(sw)), -122)], 11, 8, step=4, cap=True),
                   C_LEAF_SH, "", w=2.8, seed=sd + 30))
    rg = ring_arcs(0, 0, 1.0, ring, t, seed, r=150)
    return _tf("".join(o) , x + jx * k, y + jy * k, k, rot + jr) + (_tf(rg, x, y, k, 0) if rg else "")


def _lid_dir(open_):
    a = math.radians(108 * clamp(open_))
    return .45 * math.cos(a) - .97 * math.sin(a)       # смещение по y на единицу длины крышки (− вверх)


def laptop_pts(x, y, k=1.0, open_=1.0, turn=0.0):
    D, L = 200.0, 300.0
    hinge_y = -D * .45
    top_y = hinge_y + L * _lid_dir(open_)
    sx = 1 - .42 * abs(turn)
    return dict(screen=(x, y + k * (hinge_y + top_y) / 2), sw=470 * k * sx, sh=abs(top_y - hinge_y) * k, keys=(x, y - D * .22 * k),
                keys_w=420 * k * sx, hinge=(x, y + hinge_y * k), lid_top=(x, y + top_y * k))


def laptop(x, y, k=1.0, open_=1.0, screen="dark", lines=0.0, t=0.0, seed=0, reflect="", turn=0.0, glow=0.0):
    sd = 70500 + seed
    D, L = 200.0, 300.0
    hinge = -D * .45
    o = []
    # корпус: передний край y=0 (шире), задний — hinge (уже)
    deck = [(-260, 0, 1), (-232, hinge, 1), (232, hinge, 1), (260, 0, 1), (262, 14, 1), (-262, 14, 1)]
    keys = []
    for r_ in range(4):
        v0, v1 = .16 + r_ * .17, .16 + r_ * .17 + .13
        y0, y1 = hinge * (1 - v0) * 1 + 0, hinge * (1 - v1)
        yy0, yy1 = hinge + (0 - hinge) * v0 * 0 + hinge * -v0 + hinge, 0
        del yy0, yy1
        ya, yb = hinge * (1 - v0), hinge * (1 - v1)
        ya, yb = min(ya, yb), max(ya, yb)
        wa, wb = 220 - 26 * (1 - v0), 220 - 26 * (1 - v1)
        n = 11 if r_ < 3 else 1
        for c_ in range(n):
            if r_ == 3:
                ka, kb = -.42, .42
            else:
                ka, kb = -1 + 2 * c_ / n + .02, -1 + 2 * (c_ + 1) / n - .02
            keys.append(f'<path d="M{f(ka * wa)} {f(ya)}L{f(kb * wa)} {f(ya)}L{f(kb * wb)} {f(yb)}L{f(ka * wb)} {f(yb)}Z" fill="#3A3F49"/>')
        del y0, y1
    pad = f'<path d="M-62 -14L62 -14L60 -4L-60 -4Z" fill="#C8CCD4"/>'
    o.append(shape(deck, "#C9CDD5", "".join(keys) + pad + blob([(-262, 2), (262, 2), (262, 16), (-262, 16)], "#9FA4AE"), w=4.2, seed=sd))
    dy = _lid_dir(open_)
    top = hinge + L * dy
    if dy > -.05:     # крышка лежит/почти лежит: видна её внешняя сторона
        lid = [(-236, hinge, 1), (236, hinge, 1), (258 + 4 * dy, top, 1), (-258 - 4 * dy, top, 1)]
        o.append(shape(lid, "#AEB3BD", blob(ellipse_pts(0, (hinge + top) / 2, 50, 18 * max(.2, dy), 12), "#C3C7CF"), w=4.2, seed=sd + 1))
    else:
        fr = [(-240, hinge + 4, 1), (240, hinge + 4, 1), (244, top, 1), (-244, top, 1)]
        o.append(shape(fr, "#2E323A", "", w=4.4, seed=sd + 2))
        sx0, sx1 = -222, 222
        sy0, sy1 = top + 16 * (-dy), hinge - 10
        spts = [(sx0, sy1, 1), (sx1, sy1, 1), (sx1 + 2, sy0, 1), (sx0 - 2, sy0, 1)]
        cid = lib.clip_of(spts)
        cx, cy = 0.0, (sy0 + sy1) / 2
        sh = abs(sy1 - sy0)
        if screen in ("page", "lines"):
            inner = f'<path d="{lib.fill_d(spts)}" fill="#FDFCF7"/>'
            inner += blob([(sx0, sy0), (sx1, sy0), (sx1, sy0 + sh * .1), (sx0, sy0 + sh * .1)], "#E6E8EE")
            if screen == "lines" and lines > 0:
                inner += _lines_block(sx0 + 38, sx1 - 40, sy0 + sh * .2, sh * .105, 7, lines, sd + 50, w=4.0, col="#5B6170")
                wl = _lines_tip(sx0 + 38, sx1 - 40, sy0 + sh * .2, sh * .105, 7, lines, sd + 50)
                cur = wl
            else:
                cur = (sx0 + 56, sy0 + sh * .2)
            if (t * 1.6) % 1 < .6:
                inner += line([(cur[0] + 4, cur[1] - 13), (cur[0] + 4, cur[1] + 13)], 3.6, "#2B2F38", taper=.05, wmin=.9, seed=sd + 60)
        else:
            inner = f'<path d="{lib.fill_d(spts)}" fill="#141821"/>'
            if screen == "reflect" and reflect:
                inner += f'<g transform="translate({f(cx)} {f(cy)})" opacity=".42" style="mix-blend-mode:screen">{reflect}</g>'
            inner += f'<path d="M{f(sx0 + 40)} {f(sy0)}L{f(sx0 + 120)} {f(sy0)}L{f(sx0 + 20)} {f(sy1)}L{f(sx0 - 60)} {f(sy1)}Z" fill="#FFFFFF" opacity=".05"/>'
        o.append(f'<g clip-path="url(#{cid})">{inner}</g>')
        if glow > 0.01:
            o.append(globals()["glow"](0, (sy0 + sy1) / 2, 300, .35 * glow, "#DDE8FF", ry=200))
    g = "".join(o)
    if abs(turn) > 0.001:
        sxk = 1 - .42 * abs(turn)
        g = f'<g transform="matrix({sxk:.4f} {-.16 * turn:.4f} 0 1 0 0)">{g}</g>'
    return _tf(g, x, y, k)


def pedestal(x, y, k=1.0, crack_=0.0, split=0.0, seed=0):
    sd = 70700 + seed
    su = clamp(split)
    parts = []
    for side in (-1, 1):
        o = []
        body = [(0, -300, 1), (side * 120, -300, 1), (side * 120, -40, 1), (0, -40, 1)]
        o.append(shape(body, "#F2EADB", blob([(side * 80, -300), (side * 120, -300), (side * 120, -40), (side * 80, -40)], "#D8CDB8")
                       + line([(side * 40, -280), (side * 40, -60)], 3, "#CDBFA6", taper=.3, wmin=.4, seed=sd + 3 + side)
                       + line([(side * 82, -280), (side * 82, -60)], 3, "#CDBFA6", taper=.3, wmin=.4, seed=sd + 5 + side), w=0, seed=sd, ink=False))
        o.append(shape([(0, -330, 1), (side * 150, -330, 1), (side * 150, -296, 1), (0, -296, 1)], "#E8DCC4", "", w=0, ink=False))
        o.append(shape([(0, -44, 1), (side * 150, -44, 1), (side * 150, 0, 1), (0, 0, 1)], "#E8DCC4", "", w=0, ink=False))
        for pts in ([(0, -330), (side * 150, -330), (side * 150, -296), (side * 120, -296), (side * 120, -44), (side * 150, -44), (side * 150, 0), (0, 0)],):
            o.append(line(pts, 4.6, lib.INK, taper=.05, wmin=.9, seed=sd + 9 + side))
        g = "".join(o)
        if su > 0:
            g += line([(0, -330), (0, -44)], 4.2, lib.INK, taper=.1, wmin=.8, seed=sd + 12 + side)
            g = f'<g transform="translate({side * 30 * su:.2f} 0) rotate({side * 84 * su:.2f} {side * 150} 0)">{g}</g>'
        parts.append(g)
    o = parts
    cu = clamp(crack_)
    if cu > 0 and su < .05:
        rs = _rs(sd + 30)
        pts = [(0, -330)]
        for i in range(1, 9):
            pts.append((rs.uniform(-18, 18), -330 + i * 41))
        n = max(2, int(1 + 8 * cu))
        o.append(line(pts[:n], 7, lib.INK, taper=.3, wmin=.4, seed=sd + 31))
    elif su < .05:
        o.append(line([(0, -330), (0, -296)], 2.6, lib.INK, seed=sd + 32, op=0))
    return _tf("".join(o), x, y, k)


def pedestal_top(x, y, k=1.0):
    return (x, y - 330 * k)


def laurel(x, y, k=1.0, u=1.0, side=1, seed=0):
    if u <= 0.01:
        return ""
    sd = 70800 + seed
    o = []
    stem = [(0, 0), (side * 40, -60), (side * 60, -130), (side * 56, -200)]
    S = lib.sample(stem, False, 4)
    n = max(2, int(len(S) * clamp(u)))
    o.append(line([(float(p[0]), float(p[1])) for p in S[:n]], 5, C_LEAF_SH, taper=.5, wmin=.3, seed=sd))
    for j in range(6):
        q = clamp(u * 7 - j - .5)
        if q <= 0:
            continue
        p = S[min(len(S) - 1, int(len(S) * (j + 1) / 7))]
        for s2 in (-1, 1):
            a = math.radians(-90 + side * 20 + s2 * 50)
            L = 34 * q
            tip = (p[0] + L * math.cos(a), p[1] + L * math.sin(a))
            nx, ny = -math.sin(a) * 9 * q, math.cos(a) * 9 * q
            m = ((p[0] + tip[0]) / 2, (p[1] + tip[1]) / 2)
            o.append(shape([(p[0], p[1], 1), (m[0] + nx, m[1] + ny), (tip[0], tip[1], 1), (m[0] - nx, m[1] - ny)], C_LEAF, "", w=2.6, seed=sd + j * 2 + s2))
    return _tf("".join(o), x, y, k)


def splat(x, y, k=1.0, u=1.0, drip=0.0, t=0.0, seed=0):
    if u <= 0.01:
        return ""
    sd = 70900 + seed
    rs = _rs(sd)
    uu = clamp(u)
    pts = []
    n = 26
    for i in range(n):
        a = 2 * math.pi * i / n
        r = (1 + (rs.uniform(-.12, .3) if i % 3 else rs.uniform(.25, .55))) * 140 * uu
        pts.append((r * math.cos(a), r * .55 * math.sin(a)))
    inner = blob(ellipse_pts(30 * uu, 22 * uu, 120 * uu, 50 * uu, 16), C_TOMATO_SH, .9)
    inner += blob(ellipse_pts(-50 * uu, -24 * uu, 34 * uu, 12 * uu, 10, rot=-.3), C_TOMATO_HI, .9)
    o = [shape(pts, C_TOMATO, inner, w=4.6, seed=sd + 1)]
    for j in range(5):       # брызги-капельки вокруг
        a = rs.uniform(0, 2 * math.pi)
        d = rs.uniform(190, 260) * uu
        rr = rs.uniform(8, 16) * uu
        o.append(shape(ellipse_pts(d * math.cos(a), d * .55 * math.sin(a), rr, rr * .8, 10), C_TOMATO, "", w=3, seed=sd + 10 + j))
    for j in range(7):       # семечки
        a = rs.uniform(0, 2 * math.pi)
        d = rs.uniform(10, 90) * uu
        o.append(shape(ellipse_pts(d * math.cos(a), d * .5 * math.sin(a), 9 * uu, 5.5 * uu, 8, rot=a), "#F5E6A8", "", w=2.0, seed=sd + 20 + j))
    du = clamp(drip)
    if du > 0:
        for j, (dx, L) in enumerate(((-60, 170), (34, 260), (96, 120))):
            q = clamp(du * 1.3 - j * .15)
            if q <= 0:
                continue
            y0 = 70 * uu * (1 - (dx / 150) ** 2) ** .5 - 6
            yl = y0 + L * q
            o.append(shape([(dx - 13, y0 - 12, 1), (dx + 13, y0 - 12, 1), (dx + 8, yl - 10), (dx, yl + 12), (dx - 8, yl - 10)], C_TOMATO, "", w=3.2, seed=sd + 40 + j))
            o.append(shape(ellipse_pts(dx, yl + 4, 14, 16, 10), C_TOMATO, blob(ellipse_pts(dx - 4, yl - 2, 4, 5, 8), C_TOMATO_HI), w=3.2, seed=sd + 45 + j))
    return _tf("".join(o), x, y, k)


def mountain_peak(x, y, k=1.0, grow=1.0):
    return (x, y - (120 + 1030 * clamp(grow)) * k)


def mountain(x, y, k=1.0, grow=1.0, hatch=1.0, seed=0):
    sd = 71000 + seed
    g = clamp(grow)
    if g <= 0.01:
        return ""
    Hh = 120 + 1030 * g
    Wd = 260 + 720 * g
    rs = _rs(sd)
    left = [(-Wd / 2, 0, 1)]
    right = []
    for i in range(1, 7):
        v = i / 7
        left.append((-Wd / 2 * (1 - v) + rs.uniform(-18, 18) * g, -Hh * v * (.92 + .08 * v)))
    for i in range(6, 0, -1):
        v = i / 7
        right.append((Wd / 2 * (1 - v) + rs.uniform(-18, 18) * g, -Hh * v * (.9 + .1 * v)))
    right.append((Wd / 2, 0, 1))
    peak = (0, -Hh)
    pts = left + [(-Wd * .07, -Hh * .93), peak, (Wd * .07, -Hh * .93)] + right
    inner = blob([peak, (Wd * .08, -Hh * .9), (Wd / 2 + 10, 10), (Wd * .05, 10), (Wd * .12, -Hh * .5)], "#8E9198", .9)
    hu = clamp(hatch)
    if hu > 0:
        nh = int(26 * hu)
        for j in range(nh):
            v = .12 + .8 * j / 26
            yy = -Hh * v
            half = Wd / 2 * (1 - v)
            xa = half * (.15 + .5 * rs.uniform(0, 1))
            inner += line([(xa, yy), (xa + 70 * (1 - v) + 20, yy + 60 * (1 - v) + 30)], 3.2, "#5E6168", taper=.6, wmin=.15, seed=sd + 50 + j)
            xb = -half * (.3 + .55 * rs.uniform(0, 1))
            inner += line([(xb, yy), (xb + 40 * (1 - v) + 10, yy + 50 * (1 - v) + 20)], 2.6, "#7C8088", taper=.6, wmin=.15, seed=sd + 90 + j)
    o = [shape(pts, "#B4B6BB", inner, w=5.4, seed=sd + 1)]
    # вершина-помидорка с шапкой-листиком (масштаб от роста)
    tk = .55 + .9 * g
    tp = (0, -Hh + 40 * tk)
    o.append(tomato_timer(tp[0], tp[1], tk, 0, wedge=0, dial=False, seed=seed + 5))
    return _tf("".join(o), x, y, k)


def step_top(x, y, k=1.0, u=0.0):
    return y - (80 + 940 * clamp(u)) * k


def step_wall(x, y, k=1.0, u=0.0, glow_=0.0, t=0.0, seed=0):
    sd = 71100 + seed
    uu = clamp(u)
    Hh = 80 + 940 * uu
    rs = _rs(sd)
    o = []
    gu = clamp(glow_)
    if gu > 0.01:
        o.append(shape(rrect(-150, -Hh - 30, 150, 14, 40), "#FFD98A", "", w=0, ink=False, attrs=f'opacity="{.55 * gu:.3f}"'))
        o.append(shape(rrect(-136, -Hh - 16, 136, 8, 30), "#FFE9B8", "", w=0, ink=False, attrs=f'opacity="{.7 * gu:.3f}"'))
    pts = [(-120, 0, 1), (-118, -Hh * .5), (-122, -Hh + 14), (-110, -Hh, 1), (110, -Hh, 1), (122, -Hh + 12), (118, -Hh * .5), (120, 0, 1)]
    col = mix(C_STONE, "#E8C27A", .55 * gu)
    inner = blob([(60, -Hh), (130, -Hh), (130, 10), (70, 10)], mix(C_STONE_SH, "#C99A4A", .5 * gu), .95)
    inner += blob([(-120, -Hh), (120, -Hh), (120, -Hh + 22), (-120, -Hh + 22)], mix("#C3BFBC", "#FFE3A0", .6 * gu))
    nb = int(Hh / 110)
    for j in range(nb):         # швы кладки
        yy = -60 - j * 110 + rs.uniform(-8, 8)
        inner += line([(-120, yy), (-40, yy + rs.uniform(-6, 6)), (40, yy + rs.uniform(-6, 6)), (120, yy)], 3.2, C_STONE_SH, taper=.4, wmin=.3, seed=sd + 5 + j)
        xs = rs.uniform(-60, 60)
        inner += line([(xs, yy), (xs + rs.uniform(-8, 8), yy - 104)], 3.0, C_STONE_SH, taper=.4, wmin=.3, seed=sd + 40 + j)
    o.append(shape(pts, col, inner, w=5.2, seed=sd + 1))
    return _tf("".join(o), x, y, k)


SWING_TOP = 760.0
SWING_ROPE = 520.0


def swing_rope_pts(x, y, k=1.0, ang=0.0):
    """Качели сбоку: верёвка от оси (x, y − SWING_TOP·k) под углом ang (+ — сиденье уходит вправо). → [(верх, низ)] ближней верёвки."""
    a = math.radians(ang)
    top = (x, y - SWING_TOP * k)
    return [(top, (top[0] + SWING_ROPE * k * math.sin(a), top[1] + SWING_ROPE * k * math.cos(a)))]


def swing_seat(x, y, k=1.0, ang=0.0):
    a = math.radians(ang)
    return (x + SWING_ROPE * k * math.sin(a), y - SWING_TOP * k + SWING_ROPE * k * math.cos(a), -ang)


def swing(x, y, k=1.0, ang=0.0, t=0.0, seed=0, layer="all"):
    """Качели СБОКУ: А-рама (обе рамы — ЗА человеком, ближняя чуть левее и ниже), верёвка, сиденье ребром.
    layer: "back" — рамы, перекладина-торец, дальняя верёвка (рисовать ПЕРВЫМ); "seat" — сиденье (до человека);
    "rope" — ближняя верёвка (после тела, до ближней руки); "all" — всё подряд (без человека)."""
    sd = 71200 + seed
    o = []
    wood, wsh = C_WOOD, C_WOOD_SH
    top = (x, y - SWING_TOP * k)
    if layer in ("back", "all"):
        for fr_, (bx, by, col) in enumerate(((44 * k, -30 * k, wsh), (-60 * k, 24 * k, wood))):
            for j, dx in enumerate((-330, 330)):
                o.append(shape(lib.band([(x + dx * k + bx, y + by), (top[0] + bx, top[1] + by)], 34 * k, 24 * k, step=6, cap=True), col,
                               line([(x + dx * k * .9 + bx, y - 20 * k + by), (top[0] + dx * k * .08 + bx, top[1] + 40 * k + by)], 2.6 * k, wsh, taper=.5,
                                    wmin=.2, seed=sd + 30 + j + fr_ * 2) if col == wood else "", w=4.4 * k, seed=sd + 1 + j + fr_ * 2))
        bar = [(top[0] - 60 * k, top[1] + 24 * k - 16 * k), (top[0] + 44 * k, top[1] - 30 * k - 16 * k), (top[0] + 50 * k, top[1] - 30 * k + 16 * k),
               (top[0] - 54 * k, top[1] + 24 * k + 16 * k)]
        o.append(shape(bar, wood, blob(bar[2:] + [((bar[0][0] + bar[3][0]) / 2, bar[3][1] - 8 * k)], wsh), w=4.4 * k, seed=sd + 5))
        tp, bt = swing_rope_pts(x, y, k, ang)[0]
        o.append(line([(tp[0] + 22 * k, tp[1] - 14 * k), (bt[0] + 22 * k, bt[1] - 14 * k)], 6 * k, "#6E5238", taper=.05, wmin=.9, seed=sd + 9))
    if layer in ("seat", "all"):
        sx, sy, sdg = swing_seat(x, y, k, ang)
        seat = lib.T(rrect(-95, -6, 95, 20, 6), sx, sy, k, sdg)
        o.append(shape(seat, wood, blob(lib.T(rect_pts(-95, 8, 95, 20), sx, sy, k, sdg), wsh), w=4.4 * k, seed=sd + 20))
    if layer in ("rope", "all"):
        tp, bt = swing_rope_pts(x, y, k, ang)[0]
        o.append(line([tp, ((tp[0] + bt[0]) / 2, (tp[1] + bt[1]) / 2), bt], 7.5 * k, "#8A6A48", taper=.05, wmin=.9, seed=sd + 10))
        o.append(blob(ellipse_pts(tp[0], tp[1], 10 * k, 10 * k, 8), lib.INK))
    return "".join(o)


def fence(x0, x1, y, k=1.0, seed=0):
    sd = 71300 + seed
    rs = _rs(sd)
    o = []
    for yy in (-150, -60):
        o.append(shape([(x0, y + (yy - 12) * k, 1), (x1, y + (yy - 12) * k, 1), (x1, y + (yy + 12) * k, 1), (x0, y + (yy + 12) * k, 1)], "#D9C29A", "", w=3.2 * k,
                       seed=sd + yy))
    xx = x0 + 20 * k
    j = 0
    while xx < x1:
        h = 200 + rs.uniform(-8, 8)
        o.append(shape([(xx - 22 * k, y, 1), (xx - 22 * k, y - (h - 26) * k, 1), (xx, y - h * k, 1), (xx + 22 * k, y - (h - 26) * k, 1), (xx + 22 * k, y, 1)],
                       "#EADCBE", blob([(xx + 8 * k, y - h * k), (xx + 22 * k, y - h * k), (xx + 22 * k, y), (xx + 8 * k, y)], "#CDB98F"), w=3.4 * k, seed=sd + 10 + j))
        xx += 74 * k
        j += 1
    return "".join(o)


def door_handle(x, y, k=1.0):
    return (x + 150 * k, y - 470 * k)


def door(x, y, k=1.0, ajar=0.0, seed=0, col="#C99A6B"):
    sd = 71400 + seed
    o = [shape([(-236, 0, 1), (-236, -960, 1), (236, -960, 1), (236, 0, 1), (210, 0, 1), (210, -936, 1), (-210, -936, 1), (-210, 0, 1)], "#EEE6D6", "",
               w=4.2, seed=sd)]
    inner = blob([(120, -940), (220, -940), (220, 10), (120, 10)], lib.mul(col, (.85, .83, .8)), .9)
    for (a, b) in ((-150, -860), (-150, -500)):
        h = 300 if b == -860 else 380
        inner += shape(rrect(-150, b, 150, b + h, 10), lib.mul(col, (1.05, 1.04, 1.02)), blob(rect_pts(110, b, 150, b + h), lib.mul(col, (.9, .88, .85))),
                       w=3.0, seed=sd + 3 + (b == -500))
    o.append(shape([(-210, 0, 1), (-210, -936, 1), (210, -936, 1), (210, 0, 1)], col, inner, w=4.6, seed=sd + 1))
    hx, hy = 150, -470
    o.append(shape(ellipse_pts(hx, hy, 20, 30, 12), C_METAL_SH, "", w=3.0, seed=sd + 6))
    o.append(shape(rrect(hx - 64, hy - 11, hx + 4, hy + 11, 10), C_METAL, blob(rect_pts(hx - 64, hy + 2, hx + 4, hy + 11), C_METAL_SH), w=3.4, seed=sd + 7))
    o.append(blob(ellipse_pts(hx, hy + 48, 6, 10, 8), "#3A3530"))
    return _tf("".join(o), x, y, k)


def wind_lines(x, y, k=1.0, u=1.0, t=0.0, seed=0, n=4):
    if u <= 0.01:
        return ""
    o = []
    for j in range(n):
        ph = (t * 1.8 + j * .29 + seed * .13) % 1
        yy = y + (j - n / 2) * 60 * k
        xa = x - ph * 380 * k
        L = (120 + 60 * math.sin(j * 2.3)) * k * clamp(u)
        pts = [(xa, yy), (xa - L * .5, yy - 8 * k), (xa - L, yy + 4 * k)]
        if ph < .9:
            o.append(line(pts, 5 * k * (1 - ph * .7), "#7C8794", taper=.7, wmin=.1, seed=71500 + seed + j))
    return "".join(o)


# ═════════════════════════════ РИЛС 71 «ДВА ЛАГЕРЯ» (автор — группа A) ═════════════════════════════
# Букв и цифр нет нигде: пузыри — штрихи-волны и пиктограммы, флажки — знаки (молния / клубок), ящик без надписей.
#   camp_tent(x, y, k, col, flag, open_, bounce, t, seed, wave)
#                         туристическая палатка в три четверти, (x, y) — ЦЕНТР ДНА, ~600×430·k (+ флагшток до −640·k);
#                         col "yellow" | "blue"; flag "bolt" | "yarn" (знак на флажке); open_ 0…1 — полог раскрывается (виден тёмный вход);
#                         bounce — сжатие от дна (+ приплюснута, − вытянута; подскок/удар задаёт сцена через P.squash);
#                         wave — сила колыхания флажка (1 — ветерок). tent_door(x, y, k, bounce) → (x, y) центр входа (откуда вылетают пузыри).
#   camp_flag(x, y, k, flag, t, wave, seed, col)  флажок на древке отдельно (ЦЕНТР НИЗА древка), древко 200·k, полотнище 130×90·k
#   flag_sign(kind, cx, cy, s, seed, col)         только знак: "bolt" — молния, "yarn" — спутанный клубок (s — радиус)
#   comment_bubble(x, y, k, icon, u, wobble, seed, tail, col)
#                         круглый пузырь-реплика 220×180·k (ЦЕНТР); icon "waves" | "arrow_up" | "yarn" | "" ; u — масштаб (pop задаёт сцена);
#                         wobble −1…1 — желейное покачивание (кивок/удар); tail=(dx, dy) хвостик от низа; col — заливка (по лагерю:
#                         BUB_YELLOW / BUB_BLUE / белый).
#   bubble_swarm(cx, cy, t, n, r, k, u, split, spread, seed, icons, cols)
#                         рой пузырей, кружащих вокруг (cx, cy) по эллипсу радиуса r; split 0…1 — чётные уходят влево, нечётные вправо
#                         на spread px; u — масштаб всех (проявление). swarm_pos(...) → [(x, y, i)] те же места.
#   split_flash(x, y0, y1, u, seed, w)            вспышка-зигзаг раскола (вертикальная молния + штрихи-искры), u 0…1 (1 — погасла)
#   task_crate(x, y, k, shrink, rot, seed)        деревянный ящик-дело 300×250·k (ЦЕНТР ДНА), доски, верёвка крест-накрест, узел;
#                         shrink 0…1 — сжимается до кубика (CRATE_MIN доли); при сжатии стороны «хлюпают» (перелёт по осям).
#                         crate_box(x, y, k, shrink) → (x0, y0, x1, y1) рамка в мире.
#   chalk_wall(x0, y0, x1, y1, u, eyes, crumble, t, seed, masks, blink, eye_at, col, sh, rows)
#                         невидимая стена — ТОЛЬКО пунктирный меловой контур кирпичей в прямоугольнике (не полупрозрачная фигура);
#                         masks=[(cx, cy, r), ...] — штрихи видны только у этих точек (ладони), радиус × u; masks=None — вся стена,
#                         проявление от центра по u; eyes 0…1 — сонные глаза-сторож (eye_at=(x, y) центр между глаз, по умолч. центр
#                         стены), blink 0…1 — моргание; crumble 0…1 — кирпичи по одному срываются и падают кусочками, внизу пыль.
#   chalk_dust(x, y, k, u, seed, col)             облачко меловой пыли (u 0…1 — разлёт и исчезновение уменьшением)
#   striped_sock(x, y, k, rot, seed, flat)        полосатый носок лежит на полу (ЦЕНТР), 230×110·k, пятка и мысок синие; flat 0…1 —
#                         насколько смят (0 — «стоит» уголком, 1 — плашмя)
#   sock_worn(ax, ay, k, dirv, pull, seed)        носок НА ступне: (ax, ay) — щиколотка, dirv — куда пальцы; pull 0…1 — натянут
#                         (0 — висит на пальцах, 1 — до щиколотки с резинкой). Рисовать поверх босой ступни.
#   speed_arcs(x, y, k, u, t, seed, n, ang)       дуги-штрихи скорости за движущимся (ang — куда «хвост», градусы)
C_TENT = {"yellow": ("#F2C53D", "#C99A1E", "#F8DD7A"), "blue": ("#4F78B5", "#36588C", "#79A0D6")}
BUB_YELLOW = "#FFF4C7"
BUB_BLUE = "#DCE9F7"
CRATE_MIN = 0.22
C_CHALK = "#FFFFFF"
C_CHALK_SH = "#6F7F92"
C_SOCK = ("#D9483B", "#F4EFE6", "#4F78B5")


def flag_sign(kind, cx, cy, s=30.0, seed=0, col=None):
    sd = 72000 + seed
    if kind == "bolt":
        c = col or "#F2C53D"
        pts = [(-.15, -1.0, 1), (.55, -1.0, 1), (.12, -.15, 1), (.6, -.15, 1), (-.35, 1.05, 1), (-.02, .12, 1), (-.5, .12, 1)]
        pts = [(cx + p[0] * s, cy + p[1] * s, 1) for p in pts]
        return shape(pts, c, "", w=3.0, seed=sd)
    if kind == "yarn":
        c = col or "#4F78B5"
        o = shape(ellipse_pts(cx, cy, s, s, 16), c, "", w=3.0, seed=sd)
        sh = lib.mul(c, (.72, .72, .72))
        for j, (a0, a1) in enumerate(((-.9, .7), (-.3, 1.0), (.2, -.8), (.9, -.2))):
            o += line([(cx + s * .85 * math.cos(a0 * 2), cy + s * .85 * math.sin(a0 * 2)), (cx + s * .1 * j - s * .1, cy - s * .1 * j + s * .1),
                       (cx + s * .85 * math.cos(a1 * 2.4), cy + s * .85 * math.sin(a1 * 2.4))], 2.6, sh, taper=.3, wmin=.4, seed=sd + 2 + j)
        o += line([(cx + s * .7, cy + s * .7), (cx + s * 1.25, cy + s * .95), (cx + s * 1.5, cy + s * .7), (cx + s * 1.8, cy + s * 1.0)], 3.0, sh,
                  taper=.5, wmin=.3, seed=sd + 9)
        return o
    return ""


def camp_flag(x, y, k=1.0, flag="bolt", t=0.0, wave=1.0, seed=0, col="#FFFFFF", pole=200.0):
    sd = 72100 + seed
    o = [line([(0, 0), (0, -pole)], 7, "#5B4632", taper=.05, wmin=.9, seed=sd)]
    o.append(shape(ellipse_pts(0, -pole - 6, 9, 9, 10), "#E2B65C", "", w=2.6, seed=sd + 1))
    top, L, H = -pole + 4, 130.0, 90.0
    pts = []
    for i in range(7):
        q = i / 6
        pts.append((L * q, top + 10 * wave * q * math.sin(t * 7 + q * 3 + seed)))
    bot = [(L * q, top + H - 4 * q + 10 * wave * q * math.sin(t * 7 + q * 3 + seed + .4)) for q in [i / 6 for i in range(6, -1, -1)]]
    poly = [(p[0], p[1], 1) if i in (0, 6) else p for i, p in enumerate(pts)] + bot
    inner = blob([(L * .55, top), (L, top), (L, top + H), (L * .55, top + H)], lib.mul(col, (.9, .9, .9)), .7)
    o.append(shape(poly, col, inner, w=3.6, seed=sd + 2))
    mid = 10 * wave * .5 * math.sin(t * 7 + 1.5 + seed)
    o.append(flag_sign(flag, L * .5, top + H / 2 + mid, 28, seed))
    return _tf("".join(o), x, y, k)


def tent_door(x, y, k=1.0, bounce=0.0):
    return (x - 70 * k * (1 + .5 * bounce), y - 120 * k * (1 - bounce))


def camp_tent(x, y, k=1.0, col="yellow", flag="bolt", open_=0.0, bounce=0.0, t=0.0, seed=0, wave=1.0):
    sd = 72200 + seed
    c, csh, chi = C_TENT[col]
    o = []
    o.append(blob(ellipse_pts(20, 6, 330, 30, 18), "#3a2a20", .18))
    # растяжки и колышки (за палаткой и у края)
    for (a, b) in (((-250, -150), (-340, 8)), ((180, -330), (330, 10))):
        o.append(line([a, b], 2.4, "#7a6a58", taper=.1, wmin=.6, seed=sd + 1))
        o.append(line([(b[0], b[1] - 16), (b[0] + 4, b[1] + 8)], 5, "#5B4632", taper=.2, wmin=.6, seed=sd + 2))
    apex, back_apex = (-70, -420), (170, -380)
    # бок (теневая сторона)
    side = [(apex[0], apex[1], 1), (back_apex[0], back_apex[1], 1), (300, -10, 1), (140, 0, 1)]
    s_in = "".join(line([(apex[0] + 60 * j + 40, apex[1] + 10 * j + 8), (160 + 40 * j - 10, -4 - 3 * j)], 2.6, lib.mul(csh, (.85, .85, .85)), seed=sd + 5 + j, op=.6)
                   for j in range(3))
    o.append(shape(side, csh, s_in, w=4.6, seed=sd + 3))
    # перёд
    front = [(apex[0], apex[1], 1), (140, 0, 1), (-290, 0, 1)]
    f_in = blob([(apex[0], apex[1]), (apex[0] - 40, apex[1] + 60), (-250, -10), (-290, 0)], chi, .8)
    o.append(shape(front, c, f_in, w=4.8, seed=sd + 4))
    # вход: тёмный треугольник, полог расходится
    da, dl, dr = (apex[0], apex[1] + 110), (-175, 0), (35, 0)
    ou = clamp(open_)
    o.append(shape([(da[0], da[1], 1), (dr[0], dr[1], 1), (dl[0], dl[1], 1)], "#2E2A33",
                   blob([(da[0], da[1] + 40), (dr[0] - 30, -4), (dl[0] + 30, -4)], "#3E3844", .9), w=3.8, seed=sd + 6))
    for side_ in (-1, 1):
        edge = dl if side_ < 0 else dr
        mid_x = da[0] + (edge[0] - da[0]) * (.02 + .98 * ou)
        bulge = 26 * side_ * ou
        flap = [(da[0], da[1], 1), (edge[0], edge[1], 1), (mid_x, 0, 1), (mid_x * .5 + da[0] * .5 + bulge, da[1] * .45, 0)]
        fc = c if side_ < 0 else lib.mul(c, (.94, .93, .9))
        o.append(shape(flap, fc, "", w=3.6, seed=sd + 7 + side_))
        if ou > .6:     # подвязанный рулон
            rx = edge[0] - side_ * 10
            o.append(shape(ellipse_pts(rx, -140, 18, 60, 12, rot=8 * side_), chi, "", w=3.2, seed=sd + 9 + side_))
            o.append(line([(rx - 16, -150), (rx + 16, -142)], 3, "#7a3a2a", seed=sd + 11 + side_))
    # шов-молния и конёк
    o.append(line([apex, back_apex], 4.4, lib.mul(csh, (.8, .8, .8)), taper=.1, wmin=.7, seed=sd + 13))
    # флагшток с вершины
    fl = camp_flag(apex[0], apex[1] + 6, 1.0, flag, t, wave, seed, pole=210)
    body = "".join(o) + fl
    sx, sy = 1 + .5 * bounce, 1 - bounce
    return f'<g transform="translate({f(x)} {f(y)}) scale({k * sx:.5f} {k * sy:.5f})">{body}</g>'


def _bubble_icon(icon, s, seed, col_bg):
    sd = 72300 + seed
    if icon == "waves":
        o = ""
        for j in range(3):
            yy = -s * .34 + j * s * .34
            ww = s * (.62 if j < 2 else .4)
            o += line([(-s * .62 + s * .25 * q * ww / (s * .62), yy + (5 if q % 2 else -5)) for q in range(6)], 5.2, INK, taper=.3, wmin=.4, seed=sd + j)
        return o
    if icon == "arrow_up":
        pts = [(0, -s * .8, 1), (s * .55, -s * .15, 1), (s * .2, -s * .15, 1), (s * .2, s * .75, 1), (-s * .2, s * .75, 1), (-s * .2, -s * .15, 1),
               (-s * .55, -s * .15, 1)]
        return shape(pts, "#E0A21E", blob([(s * .05, -s * .6), (s * .5, -s * .15), (s * .2, -s * .15), (s * .2, s * .75), (s * .05, s * .75)], "#C2861A", .8),
                     w=4.0, seed=sd + 5)
    if icon == "yarn":
        return flag_sign("yarn", -s * .1, 0, s * .55, seed, "#6E92C9")
    return ""


INK = lib.INK


def comment_bubble(x, y, k=1.0, icon="waves", u=1.0, wobble=0.0, seed=0, tail=(-50, 55), col="#FFFFFF"):
    if u <= 0.02:
        return ""
    sd = 72400 + seed
    hw, hh = 110.0, 88.0
    o = []
    o.append(shape([(tail[0] * .2 - 26, hh * .66, 1), (tail[0], hh + tail[1], 1), (tail[0] * .2 + 24, hh * .76, 1)], col, "", w=3.8, seed=sd + 1))
    sh = lib.mul(col, (.92, .93, .95))
    o.append(shape(ellipse_pts(0, 0, hw, hh, 28), col, blob(ellipse_pts(hw * .18, hh * .3, hw * .75, hh * .55, 18), sh), w=4.4, seed=sd))
    o.append(blob(ellipse_pts(-hw * .5, -hh * .52, 18, 9, 10, rot=-.5), "#FFFFFF", .9))
    o.append(_bubble_icon(icon, 70, seed, col))
    wb = clamp(wobble, -1, 1)
    sx, sy = 1 + .14 * wb, 1 - .14 * wb
    return f'<g transform="translate({f(x)} {f(y)}) rotate({6 * wb:.2f}) scale({k * u * sx:.5f} {k * u * sy:.5f})">{"".join(o)}</g>'


def swarm_pos(cx, cy, t, n=9, r=260.0, split=0.0, spread=300.0, seed=0):
    rs = _rs(72500 + seed)
    out = []
    for i in range(n):
        ph = 2 * math.pi * i / n + rs.uniform(-.25, .25)
        sp = rs.uniform(1.0, 1.25)
        rr = r * rs.uniform(.45, 1.0)
        a = ph + sp * t
        s = clamp(split)
        side = -1 if i % 2 == 0 else 1
        x = cx + rr * math.cos(a) * (1 - .55 * s) + side * spread * lib.ease_io(s)
        y = cy + rr * .7 * math.sin(a) * (1 - .4 * s)
        out.append((x, y, i))
    return out


def bubble_swarm(cx, cy, t, n=9, r=260.0, k=.6, u=1.0, split=0.0, spread=300.0, seed=0, icons=("waves",), cols=("#FFFFFF",)):
    o = []
    for (x, y, i) in sorted(swarm_pos(cx, cy, t, n, r, split, spread, seed), key=lambda p: p[1]):
        wb = .5 * math.sin(t * 9 + i * 1.7)
        o.append(comment_bubble(x, y, k * (.8 + .25 * ((i * 7) % 5) / 4), icons[i % len(icons)], u, wb, seed + i, (-40 if i % 2 else 40, 45),
                                cols[i % len(cols)]))
    return "".join(o)


def split_flash(x, y0, y1, u=0.0, seed=0, w=70.0):
    if u <= 0 or u >= 1:
        return ""
    o = [bolt(x, y0, x + 20, y1, clamp(u * 1.4), w, seed, 7)]
    g = 1 - u
    for j in range(8):
        a = math.radians(j * 45 + 22)
        r0, r1 = 40 + 160 * u, 90 + 260 * u
        cy = (y0 + y1) / 2
        o.append(line([(x + r0 * math.cos(a), cy + r0 * math.sin(a)), (x + r1 * math.cos(a), cy + r1 * math.sin(a))], 9 * g + 1, "#F2B632",
                      taper=.6, wmin=.2, seed=72600 + seed + j))
    return "".join(o)


def crate_box(x, y, k=1.0, shrink=0.0):
    s = 1 - (1 - CRATE_MIN) * clamp(shrink)
    w, h = 300 * k * s, 250 * k * s
    return (x - w / 2, y - h - 60 * k * s, x + w / 2 + 70 * k * s, y)


def task_crate(x, y, k=1.0, shrink=0.0, rot=0.0, seed=0):
    sd = 72700 + seed
    sh = clamp(shrink)
    s = 1 - (1 - CRATE_MIN) * lib.ease_io(sh)
    # «хлюп» по осям во время сжатия
    j = math.sin(math.pi * sh) * .12
    sx, sy = s * (1 - j), s * (1 + j)
    W, H, D = 300.0, 250.0, 70.0
    o = [blob(ellipse_pts(30, 4, W * .62, 18, 14), "#3a2a20", .2)]
    top = [(-W / 2, -H, 1), (-W / 2 + D, -H - 60, 1), (W / 2 + D, -H - 60, 1), (W / 2, -H, 1)]
    side = [(W / 2, 0, 1), (W / 2, -H, 1), (W / 2 + D, -H - 60, 1), (W / 2 + D, -60, 1)]
    t_in = "".join(line([(-W / 2 + 20 + 90 * i, -H - 4), (-W / 2 + 20 + 90 * i + D * .9, -H - 56)], 2.6, C_WOOD_SH, seed=sd + 1 + i) for i in range(4))
    o.append(shape(top, C_WOOD_HI, t_in, w=4.4, seed=sd))
    o.append(shape(side, C_WOOD_SH, line([(W / 2 + 4, -H * .5), (W / 2 + D - 4, -H * .5 - 60)], 2.6, "#6b4424", seed=sd + 6), w=4.4, seed=sd + 5))
    f_in = ""
    for i in range(1, 3):      # доски
        f_in += line([(-W / 2 + 6, -H * i / 3), (W / 2 - 6, -H * i / 3 + 3)], 3.0, C_WOOD_SH, taper=.1, wmin=.6, seed=sd + 8 + i)
    f_in += blob([(-W / 2, -H), (-W / 2 + 30, -H), (-W / 2 + 30, 0), (-W / 2, 0)], C_WOOD_SH, .7)
    f_in += blob([(W / 2 - 30, -H), (W / 2, -H), (W / 2, 0), (W / 2 - 30, 0)], C_WOOD_SH, .7)
    for (px, py) in ((-W / 2 + 15, -H + 18), (W / 2 - 15, -H + 18), (-W / 2 + 15, -18), (W / 2 - 15, -18)):
        f_in += f'<circle cx="{px}" cy="{py}" r="4.5" fill="#4a3424"/>'
    o.append(shape([(-W / 2, 0, 1), (-W / 2, -H, 1), (W / 2, -H, 1), (W / 2, 0, 1)], C_WOOD, f_in, w=4.8, seed=sd + 7))
    rope = "#C9A66B"
    o.append(line([(-W / 2 - 4, -H * .2), (0, -H * .5), (W / 2 + 4, -H * .8)], 9, rope, taper=.05, wmin=.9, seed=sd + 12))
    o.append(line([(-W / 2 - 4, -H * .8), (0, -H * .5), (W / 2 + 4, -H * .2)], 9, rope, taper=.05, wmin=.9, seed=sd + 13))
    o.append(line([(W / 2 + 4, -H * .8), (W / 2 + D, -H * .8 - 60)], 8, lib.mul(rope, (.85, .85, .85)), taper=.05, wmin=.9, seed=sd + 14))
    o.append(shape(ellipse_pts(0, -H * .5, 22, 18, 12), rope, line([(-12, -H * .5 - 6), (12, -H * .5 + 6)], 2.4, "#8a6a38", seed=sd + 16), w=3.4, seed=sd + 15))
    o.append(line([(0, -H * .5 + 14), (-14, -H * .5 + 52), (-6, -H * .5 + 70)], 6, rope, taper=.4, wmin=.5, seed=sd + 17))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({k * sx:.5f} {k * sy:.5f})">{"".join(o)}</g>'


def _dashes(p0, p1, dash=18.0, gap=13.0, off=0.0):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    out = []
    s = -off
    while s < L:
        a, b = max(0.0, s), min(L, s + dash)
        if b > a + 2:
            out.append(((p0[0] + (p1[0] - p0[0]) * a / L, p0[1] + (p1[1] - p0[1]) * a / L), (p0[0] + (p1[0] - p0[0]) * b / L, p0[1] + (p1[1] - p0[1]) * b / L)))
        s += dash + gap
    return out


def chalk_dust(x, y, k=1.0, u=0.0, seed=0, col="#E9ECF0"):
    if u <= 0 or u >= 1:
        return ""
    rs = _rs(72800 + seed)
    o = []
    for j in range(7):
        a = rs.uniform(math.pi * 1.05, math.pi * 1.95)
        d = (30 + 90 * lib.ease_out(u)) * rs.uniform(.6, 1.2)
        r = (16 + 10 * rs.uniform(0, 1)) * (1 - u) * k
        if r > 1:
            o.append(shape(ellipse_pts(x + d * math.cos(a) * k, y + d * math.sin(a) * k * .6, r, r * .8, 10), col, "", w=2.2, seed=72810 + seed + j,
                           ink_color="#8C98A6"))
    return "".join(o)


def chalk_wall(x0, y0, x1, y1, u=1.0, eyes=0.0, crumble=0.0, t=0.0, seed=0, masks=None, blink=0.0, eye_at=None, col=C_CHALK, sh=C_CHALK_SH,
               rows=None, bw=150.0, bh=70.0, wline=4.0):
    if u <= 0.005 and eyes <= 0.005:
        return ""
    rs = _rs(72900 + seed)
    o = []
    H = y1 - y0
    nr = rows or max(1, int(round(H / bh)))
    rh = H / nr
    cxw, cyw = (x0 + x1) / 2, (y0 + y1) / 2
    R0 = math.hypot(x1 - x0, H) * .6

    def vis(px, py):
        if masks is None:
            d = math.hypot(px - cxw, py - cyw)
            return clamp((R0 * clamp(u) * 1.15 - d) / 60)
        v = 0.0
        for (mx, my, mr) in masks:
            rr = mr * clamp(u)
            if rr <= 1:
                continue
            v = max(v, clamp((rr - math.hypot(px - mx, py - my)) / (rr * .45)))
        return v
    bricks = []
    for r in range(nr):
        ya, yb = y0 + r * rh, y0 + (r + 1) * rh
        xs = x0 - (bw / 2 if r % 2 else 0)
        while xs < x1:
            xa, xb = max(x0, xs), min(x1, xs + bw)
            if xb - xa > 12:
                bricks.append((xa, ya, xb, yb))
            xs += bw
    for i, (xa, ya, xb, yb) in enumerate(bricks):
        d0 = rs.uniform(0, .6)
        fu = clamp((crumble - d0) / .4) if crumble > 0 else 0.0
        if fu >= 1:
            continue
        cxb, cyb = (xa + xb) / 2, (ya + yb) / 2
        dy = fu * fu * (y1 - cyb + 140)
        dx = rs.uniform(-40, 40) * fu
        rot = rs.uniform(-40, 40) * fu
        sc = 1 - .6 * fu
        segs = []
        for (p, q) in (((xa, ya), (xb, ya)), ((xb, ya), (xb, yb)), ((xb, yb), (xa, yb)), ((xa, yb), (xa, ya))):
            segs += _dashes(p, q, off=rs.uniform(0, 20))
        part = []
        for (p, q) in segs:
            v = vis((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) if fu == 0 else 1.0
            if v < .05:
                continue
            ww = wline * (.35 + .65 * v)
            part.append(line([p, q], ww + 2.6, sh, taper=.3, wmin=.5, seed=73000 + i, op=.45))
            part.append(line([p, q], ww, col, taper=.3, wmin=.5, seed=73100 + i))
        if part:
            if fu > 0:
                o.append(f'<g transform="translate({dx:.1f} {dy:.1f}) rotate({rot:.1f} {cxb:.1f} {cyb:.1f}) translate({cxb:.1f} {cyb:.1f}) scale({sc:.3f}) '
                         f'translate({-cxb:.1f} {-cyb:.1f})">{"".join(part)}</g>')
            else:
                o.append("".join(part))
        if 0 < fu < 1 and fu > .55:
            o.append(chalk_dust(cxb + dx, y1 - 10, .8, (fu - .55) / .45, i))
    if eyes > 0.01:
        ex, ey = eye_at or (cxw, cyw)
        op_ = clamp(eyes) * (1 - clamp(blink))
        for side in (-1, 1):
            cx, cy = ex + side * 95, ey
            rx, ry = 62 * clamp(eyes), 30
            lid = cy - ry * .2 + ry * .9 * (1 - op_)      # сонное веко: низко
            low = [(cx - rx, cy), (cx - rx * .5, cy + ry * .9), (cx + rx * .5, cy + ry * .9), (cx + rx, cy)]
            o.append(line(low, 6.5, sh, taper=.4, wmin=.4, seed=73200 + side, op=.45))
            o.append(line(low, 4.4, col, taper=.4, wmin=.4, seed=73201 + side))
            if op_ > .08:
                pr = min(ry * .55, ry * .9 * op_ + 4)
                o.append(f'<circle cx="{cx + 4 * side:.1f}" cy="{cy + ry * .35:.1f}" r="{pr:.1f}" fill="{col}" stroke="{sh}" stroke-width="2" stroke-opacity=".5"/>')
            upper = [(cx - rx - 6, cy), (cx - rx * .4, lid - 4), (cx + rx * .4, lid - 4), (cx + rx + 6, cy)]
            o.append(line(upper, 8.5, sh, taper=.3, wmin=.5, seed=73210 + side, op=.45))
            o.append(line(upper, 6.0, col, taper=.3, wmin=.5, seed=73211 + side))
            for j in range(3):     # ресницы
                q = .3 + .2 * j
                bx = cx - rx + 2 * rx * q
                o.append(line([(bx, lid + 2), (bx + 6 * side * 0 + (j - 1) * 6, lid + 22)], 3.4, col, taper=.6, wmin=.2, seed=73220 + j + side))
    return "".join(o)


def striped_sock(x, y, k=1.0, rot=0.0, seed=0, flat=1.0):
    sd = 73300 + seed
    red, wht, blu = C_SOCK
    fl = clamp(flat)
    # лежит сбоку: голенище слева, пятка снизу, мысок справа
    pts = [(-110, -40 + 18 * (1 - fl), 1), (-30, -44), (20, -36), (80, -30), (112, -6), (106, 26), (60, 36), (0, 34), (-40, 40), (-66, 24),
           (-110, 26, 1)]
    stripes = ""
    for i in range(5):
        xx = -96 + 26 * i
        stripes += shape([(xx, -46), (xx + 13, -46), (xx + 13, 46), (xx, 46)], wht, "", w=0, seed=sd + i, ink=False)
    stripes += blob([(-70, 46), (-70, 10), (-44, 4), (-30, 46)], blu)          # пятка
    stripes += blob([(70, -40), (130, -40), (130, 40), (70, 40)], blu)          # мысок
    stripes += blob([(-120, -50), (-96, -50), (-96, 50), (-120, 50)], blu)      # резинка
    stripes += blob([(-120, 20), (120, 20), (120, 50), (-120, 50)], "#000000", .1)
    body = shape(pts, red, stripes, w=4.2, seed=sd)
    return _tf(body, x, y, k, rot)


def sock_worn(ax, ay, k=1.0, dirv=(1.0, 0.15), pull=1.0, seed=0):
    sd = 73400 + seed
    red, wht, blu = C_SOCK
    d = (dirv[0], dirv[1])
    n_ = math.hypot(*d) or 1
    ang = math.degrees(math.atan2(d[1] / n_, d[0] / n_))
    p = clamp(pull)
    back = -40 - 30 * p      # насколько далеко назад (к щиколотке и выше) натянут
    hang = 26 * (1 - p)      # не натянутый — висит ниже мыска
    pts = [(back, -46 - 10 * p, 1), (40, -38), (110, -26), (150, -6 + hang * .3), (150 + hang, 18 + hang), (110, 34), (40, 36),
           (back + 20, 40), (back, 30, 1)]
    stripes = ""
    for i in range(6):
        xx = back + 10 + 26 * i
        stripes += blob([(xx, -60), (xx + 13, -60), (xx + 13, 60), (xx, 60)], wht)
    stripes += blob([(118, -60), (200, -60), (200, 70), (118, 70)], blu)
    stripes += blob([(back - 10, -70), (back + 18, -70), (back + 18, 70), (back - 10, 70)], blu)
    body = shape(pts, red, stripes, w=4.0, seed=sd)
    return f'<g transform="translate({f(ax)} {f(ay)}) rotate({ang:.2f}) scale({k:.5f})">{body}</g>'


def speed_arcs(x, y, k=1.0, u=1.0, t=0.0, seed=0, n=3, ang=180.0):
    if u <= 0.01:
        return ""
    o = []
    a = math.radians(ang)
    nx, ny = -math.sin(a), math.cos(a)
    for j in range(n):
        off = (j - (n - 1) / 2) * 46 * k
        L = (130 + 50 * ((j + seed) % 2)) * k * clamp(u)
        p0 = (x + nx * off, y + ny * off)
        p1 = (p0[0] + math.cos(a) * L * .5 + nx * 10 * k, p0[1] + math.sin(a) * L * .5 + ny * 10 * k)
        p2 = (p0[0] + math.cos(a) * L, p0[1] + math.sin(a) * L)
        o.append(line([p0, p1, p2], 6 * k, INK, taper=.8, wmin=.1, seed=73500 + seed + j, op=.85))
    return "".join(o)


# ═════════════════════════════ РИЛС 72 «СДВГ НЕ СУЩЕСТВУЕТ» (автор — группа A) ═════════════════════════════
# (x, y) — ЦЕНТР ДНА, если не сказано иначе; букв, цифр, шильдиков нет нигде.
#   phone_flat(x, y, k, rot, spin, face_down=True, glow_=0)  телефон лежит на столе в перспективе (ЦЕНТР), 150×290·k до сжатия;
#                     spin — поворот В ПЛОСКОСТИ стола (градусы, волчок), rot — наклон картинки; face_down=True — видна спинка
#                     с камерой (экран к столу), False — тёмный экран, glow_ — свет экрана (без букв)
#   brain_balloon(x, y, k, t, pop, string)   шарик-мозг (ЦЕНТР шара): розовый, извилины; pop 0…1 — лопнул: клочья летят,
#                     ниточка падает вниз, облачко-штрихи; pop>=1 — только упавшая ниточка
#   paper_tower(x, y, k, lean, flutter, t, pull, n, seed)   башня чистых листов с красной лентой крест-накрест; ширина 340·k,
#                     высота ≈ 11·n·k (n=60 → 660); lean — наклон (градусы, + вправо), башня гнётся дугой; flutter 0…1 — верхние
#                     листы шуршат краями; pull 0…1 — клочок с горошину выезжает из основания вправо.
#                     taper 0…0.6 — ракурс снизу (верх уже). paper_tower_top(x, y, k, lean, n) → верх башни в мире;
#                     scrap_pos(x, y, k, pull) → клочок в мире
#   scrap(x, y, k, rot, seed)                клочок бумаги с горошину (ЦЕНТР), 34×26·k
#   pull_engine(x, y, k, cough, shake, cord, t, seed)   садовый моторчик на раме 300×230·k: бак, цилиндр с рёбрами, выхлоп;
#                     cough 0…1 — клуб дыма из выхлопа (фаза), shake 0…1 — тряска корпуса; cord 0…1 — тросик вытянут (ручка
#                     уходит влево-вверх); handle=(x, y) мира — ручку держит рука (тросик тянется к ней), hand_ang — угол ручки.
#                     engine_handle(x, y, k, cord) → ручка тросика в мире (кисть Димы)
#   puff_cloud(x, y, k, u, seed, col)        клуб дыма/пыли (ЦЕНТР): u 0…1 растёт и тает (рвётся на клочки), сплошной с тушью
#   brain_kid(x, y, k, expr, hop, t, look, seed)   мозг-малыш (ЦЕНТР ДНА, ножки на земле), 260×300·k: розовый, мягкие извилины,
#                     глаза-блюдца, ножки с ботиночками. expr: "calm" | "peek" | "wide" (глаза шире, зрачки-точки, извилины дыбом) |
#                     "scared" (дрожит, брови домиком); hop — dy подскока; look=(x, y) −1…1 — взгляд
#   campfire(x, y, k, u, t, seed)            костёр (ЦЕНТР ДНА): кольцо камней, два бревна крест-накрест, языки пламени;
#                     u 0 — тлеющий уголёк с искрой и струйкой дыма, 1 — полное пламя (дробное — разгорается); искры вверх.
#                     fire_light(x, y, k, u, t) → мерцание 0…1 для света сцены
#   log_seat(x, y, k, w, seed)               бревно-сиденье (ЦЕНТР ДНА) лежит поперёк кадра, длина w·k, торец со спилом справа
#   hanging_sack(x, y, k, sway, drop, t, seed)   ветка (от x влево за кадр) и мешок-узелок на верёвке: (x, y) — точка подвеса
#                     на ветке; sway — качание (градусы); drop 0…1 — верёвка лопнула, мешок падает на 420·k вниз
#   ice_block(x, y, k, crack, split, t, n, seed)   глыба льда 320×300·k; crack 0…1 — трещины бегут; split 0…1 — глыба
#                     распадается на n кубиков, они разъезжаются в ряд по земле. ice_row_pos(x, y, k, split, n, i) → центр кубика i
#   ice_cube(x, y, k, rot, seed)             один ледяной кубик (ЦЕНТР), 90·k, с бликом
#   bean_bag(x, y, k, sag, seed, col)        кресло-мешок (ЦЕНТР ДНА) 520×360·k; sag 0…1 — оплывает (ниже и шире), вмятина под
#                     сидящим. bean_seat(x, y, k, sag) → точка, куда садить таз
C_ICE = "#BFE3F2"
C_ICE_SH = "#8CC2DB"
C_ICE_HI = "#EAF8FD"
C_BRAIN = "#F3A1B5"
C_BRAIN_SH = "#D97893"
C_BRAIN_LN = "#B85A78"
C_ENGINE = "#D9483B"
C_ENGINE_SH = "#A5322A"
C_BAG = "#5C9A78"
C_BAG_SH = "#41735A"
C_BAG_HI = "#7FBF98"
C_RIBBON = "#D9483B"
C_RIBBON_SH = "#A5322A"


def phone_flat(x, y, k=1.0, rot=0.0, spin=0.0, face_down=True, glow_=0.0, seed=0):
    sd = 72000 + seed
    sy = .46
    a = math.radians(spin)
    ca, sa = math.cos(a), math.sin(a)

    def tr(pts):
        out = []
        for p in pts:
            px, py = p[0] * ca - p[1] * sa, p[0] * sa + p[1] * ca
            out.append((px, py * sy) + ((1,) if len(p) > 2 and p[2] else ()))
        return out
    body = rrect(-75, -145, 75, 145, 22)
    edge = [(p[0], p[1] + 16 / sy * 0) for p in body]
    o = []
    # торец (толщина) — тот же контур, опущен на 14 px
    o.append(shape([(q[0], q[1] + 14) for q in tr(edge)], "#1F2228", "", w=3.6, seed=sd))
    if face_down:
        inner = blob(tr(rrect(-60, -130, 60, 130, 16)), "#3A3F49")
        inner += shape(tr(rrect(-52, -128, -8, -84, 12)), "#2B2E35", blob(tr(ellipse_pts(-30, -106, 12, 12, 10)), "#14161B"), w=2.4, seed=sd + 3)
        inner += line(tr([(40, -120), (48, 110)]), 4, "#5A616E", taper=.5, wmin=.3, seed=sd + 4)
        o.append(shape(tr(body), "#2B2E35", inner, w=4.0, seed=sd + 1))
    else:
        scr = "#141821" if glow_ < .02 else mix("#141821", "#DDE8FF", clamp(glow_))
        inner = blob(tr(rrect(-64, -132, 64, 132, 14)), scr)
        o.append(shape(tr(body), "#2B2E35", inner, w=4.0, seed=sd + 1))
        if glow_ > .02:
            o.append(glow(0, 0, 220, .45 * glow_, "#DDE8FF", ry=140))
    return _tf("".join(o), x, y, k, rot)


def _gyri(rx, ry, seed, col=None, w=3.6, wild=0.0, t=0.0):
    """Извилины мозга: волнистые петли внутри эллипса rx×ry (центр 0,0); wild 0…1 — встают дыбом (концы дрожат наружу)."""
    rs = _rs(seed)
    col = col or C_BRAIN_LN
    o = []
    for j in range(7):
        cy = -ry * .62 + j * ry * .21
        half = rx * math.sqrt(max(.05, 1 - (cy / ry) ** 2)) * .8
        pts = []
        for i in range(9):
            u = i / 8
            xx = -half + 2 * half * u
            yy = cy + ry * .07 * math.sin(u * 9 + j * 1.7 + rs.uniform(0, 1))
            pts.append((xx, yy))
        o.append(line(pts, w, col, taper=.5, wmin=.25, seed=seed + j))
    o.append(line([(0, -ry * .9), (3, -ry * .3), (-2, ry * .2)], w * .9, col, taper=.6, wmin=.2, seed=seed + 20))
    if wild > .02:   # извилины дыбом: петельки торчат над макушкой
        for j in range(5):
            ang = math.radians(-150 + j * 30)
            bx, by = rx * .92 * math.cos(ang), ry * .92 * math.sin(ang)
            L = (26 + 8 * (j % 2)) * wild
            wob = 5 * math.sin(t * 30 + j * 2) * wild
            o.append(line([(bx, by), (bx + math.cos(ang) * L * .6 + wob, by + math.sin(ang) * L * .6), (bx + math.cos(ang) * L - wob, by + math.sin(ang) * L)],
                          w * 1.3, lib.INK, taper=.7, wmin=.2, seed=seed + 40 + j))
    return "".join(o)


def _brain_outline(rx, ry, seed, n=11):
    rs = _rs(seed)
    pts = []
    for i in range(n):
        a0 = 2 * math.pi * i / n - math.pi / 2
        a1 = 2 * math.pi * (i + 1) / n - math.pi / 2
        b = rs.uniform(.06, .1)
        for m in range(4):
            a = a0 + (a1 - a0) * m / 4
            r = 1 + b * math.sin(math.pi * m / 4)
            pts.append((rx * r * math.cos(a), ry * r * math.sin(a)) + ((1,) if m == 0 else ()))
    return pts


def brain_balloon(x, y, k=1.0, t=0.0, pop=0.0, string=200.0, seed=0):
    sd = 72100 + seed
    o = []
    if pop <= 0:
        sw = [(5 * math.sin(t * 3 + i * .8) * (i / 6), 86 + string * i / 6) for i in range(7)]
        o.append(line(sw, 3.4, lib.INK, taper=.2, wmin=.6, seed=sd))
        o.append(shape([(-9, 90, 1), (0, 74), (9, 90, 1)], C_BRAIN_SH, "", w=2.8, seed=sd + 1))
        body = _brain_outline(78, 82, sd + 2)
        inner = blob(ellipse_pts(18, 24, 60, 58, 16), C_BRAIN_SH, .55) + _gyri(70, 74, sd + 3)
        inner += blob(ellipse_pts(-30, -40, 11, 18, 10, rot=25), "#FFFFFF")
        o.append(shape(body, C_BRAIN, inner, w=4.2, seed=sd + 4))
        return _tf("".join(o), x, y, k)
    # лопнул: клочья летят по кругу и вниз, ниточка падает свернувшись
    u = clamp(pop)
    rs = _rs(sd + 9)
    for j in range(9):
        a = 2 * math.pi * j / 9 + rs.uniform(-.3, .3)
        d = 40 + 210 * lib.ease_out(u, 2)
        cx, cy = math.cos(a) * d, math.sin(a) * d + 260 * u * u
        s = (1.35 - .6 * u) * rs.uniform(.7, 1.1)
        if s < .08:
            continue
        sh = [(-22, -8, 1), (-6, -16), (16, -12, 1), (24, 2), (8, 14, 1), (-12, 10)]
        o.append(_tf(shape(sh, C_BRAIN if j % 2 else C_BRAIN_SH, line([(-12, 0), (10, -2)], 2.6, C_BRAIN_LN, seed=sd + 30 + j), w=3.0, seed=sd + 10 + j),
                     cx, cy, s, math.degrees(a) + 400 * u))
    # облачко-штрихи хлопка (первая треть)
    if u < .5:
        v = u / .5
        for j in range(10):
            a = 2 * math.pi * j / 10 + .2
            r0, r1 = 70 + 120 * v, 110 + 170 * v
            o.append(line([(math.cos(a) * r0, math.sin(a) * r0), (math.cos(a) * r1, math.sin(a) * r1)], 7 * (1 - v), lib.INK, taper=.7, wmin=.1,
                          seed=sd + 50 + j))
    fy = 90 + 330 * u * u
    pts = [(10 * math.sin(i * 1.4 + u * 6) * (1 - i / 8), fy + i * (string / 8) * (1 - .5 * u)) for i in range(9)]
    o.append(line(pts, 3.4, lib.INK, taper=.2, wmin=.6, seed=sd))
    o.append(shape([(-8 + pts[0][0], fy + 2, 1), (pts[0][0], fy - 12), (8 + pts[0][0], fy + 2, 1)], C_BRAIN_SH, "", w=2.6, seed=sd + 1))
    return _tf("".join(o), x, y, k)


SHEET_T = 11.0


def _tower_curve(lean, n):
    """Смещение по x и угол каждого листа: башня гнётся дугой (верх уходит сильнее)."""
    out = []
    for j in range(n):
        q = j / max(1, n - 1)
        ang = lean * q
        dx = 0.0
        out.append((ang, dx))
    xs, x = [], 0.0
    for j in range(n):
        xs.append(x)
        x += math.sin(math.radians(out[j][0])) * SHEET_T
    return [(xs[j], out[j][0]) for j in range(n)]


def paper_tower_top(x, y, k=1.0, lean=0.0, n=60):
    c = _tower_curve(lean, n)
    dx, ang = c[-1]
    return (x + dx * k, y - n * SHEET_T * math.cos(math.radians(lean * .5)) * k)


def scrap_pos(x, y, k=1.0, pull=0.0):
    u = lib.ease_out(pull, 2)
    return (x + (150 + 170 * u) * k, y - (16 + 60 * math.sin(math.pi * min(1, u * 1.1)) * .4) * k)


def scrap(x, y, k=1.0, rot=0.0, seed=0):
    sd = 72300 + seed
    pts = [(-17, -12, 1), (-4, -14), (17, -11, 1), (15, 2), (18, 12, 1), (2, 13), (-16, 12, 1), (-14, 0)]
    inn = line([(-9, -2), (9, -3)], 2.2, "#B8B0A0", taper=.4, wmin=.4, seed=sd + 1)
    return _tf(shape(pts, "#FFFFFF", inn, w=2.8, seed=sd), x, y, k, rot)


def paper_tower(x, y, k=1.0, lean=0.0, flutter=0.0, t=0.0, pull=0.0, n=60, seed=0, ribbon=True, taper=0.0):
    sd = 72200 + seed
    rs = _rs(sd)
    W2 = 170.0
    curve = _tower_curve(lean, n)
    o = []
    # тень у основания
    o.append(blob(ellipse_pts(0, 4, 210, 22, 16), "#000000", .12))
    # листы снизу вверх: торец-полоска 340×SHEET_T с лёгким разбросом
    mid = n // 2
    for j in range(n):
        dx, ang = curve[j]
        jitter = rs.uniform(-7, 7)
        yb = -j * SHEET_T
        fl = 0.0
        if flutter > 0 and j > n - 9:
            fl = flutter * (j - (n - 9)) / 9 * 9 * math.sin(t * 22 + j * 1.3)
        col = "#FFFFFF" if j % 2 else "#F4F1EA"
        pts = [(-W2 + jitter, yb, 1), (W2 + jitter, yb + fl * .2, 1), (W2 + jitter + fl * .4, yb - SHEET_T - fl, 1), (-W2 + jitter, yb - SHEET_T, 1)]
        g = blob(pts, col) + line([(-W2 + jitter + 4, yb - 1), (W2 + jitter - 4, yb - 1 + fl * .2)], 1.6, "#C9C2B2", taper=.1, wmin=.6, seed=sd + j)
        o.append(f'<g transform="translate({f(dx)} 0) rotate({f(ang)} 0 {f(yb)})">{g}</g>')
    # верхний лист (крышка) в перспективе и контур башни
    dx, ang = curve[-1]
    ytop = -n * SHEET_T
    top = [(-W2 - 6, ytop, 1), (W2 + 6, ytop, 1), (W2 - 14, ytop - 38, 1), (-W2 + 26, ytop - 38, 1)]
    o.append(f'<g transform="translate({f(dx)} 0) rotate({f(ang)} 0 {f(ytop)})">' + shape(top, "#FFFFFF",
             line([(-W2 + 40, ytop - 14), (W2 - 50, ytop - 18)], 2.0, "#D8D2C4", taper=.3, wmin=.4, seed=sd + 90) +
             line([(-W2 + 60, ytop - 26), (W2 - 90, ytop - 28)], 2.0, "#D8D2C4", taper=.3, wmin=.4, seed=sd + 91), w=3.6, seed=sd + 92) + "</g>")
    # боковые контуры тушью по дуге
    lft = [(curve[j][0] - W2 + (math.sin(math.radians(curve[j][1])) * 0), -j * SHEET_T) for j in range(0, n, 4)] + [(curve[-1][0] - W2, ytop)]
    rgt = [(curve[j][0] + W2, -j * SHEET_T) for j in range(0, n, 4)] + [(curve[-1][0] + W2, ytop)]
    o.append(line(lft, 4.6, lib.INK, taper=.15, wmin=.6, seed=sd + 93))
    o.append(line(rgt, 4.6, lib.INK, taper=.15, wmin=.6, seed=sd + 94))
    o.append(line([(-W2 - 4, 0), (W2 + 4, 0)], 4.6, lib.INK, taper=.15, wmin=.6, seed=sd + 95))
    # лента: вертикальная по середине и горизонтальная посередине высоты
    if ribbon:
        vb = [(curve[j][0] - 18, -j * SHEET_T) for j in range(0, n, 3)] + [(curve[-1][0] - 18, ytop)]
        vr = [(curve[-1][0] + 18, ytop)] + [(curve[j][0] + 18, -j * SHEET_T) for j in range(n - 1, -1, -3)]
        o.append(shape(vb + vr, C_RIBBON, blob([(p[0] + 26, p[1]) for p in vb] + [(p[0] + 8, p[1]) for p in vr], C_RIBBON_SH, .6), w=3.4, seed=sd + 96))
        yh = -mid * SHEET_T
        dxm = curve[mid][0]
        hb = [(dxm - W2 - 3, yh + 18, 1), (dxm + W2 + 3, yh + 18, 1), (dxm + W2 + 3, yh - 18, 1), (dxm - W2 - 3, yh - 18, 1)]
        o.append(shape(hb, C_RIBBON, blob([(dxm - W2, yh + 6), (dxm + W2, yh + 6), (dxm + W2, yh + 18), (dxm - W2, yh + 18)], C_RIBBON_SH, .7), w=3.4, seed=sd + 97))
        # бантик на пересечении
        bx, by = dxm, yh
        for sx in (-1, 1):
            o.append(shape([(bx, by, 1), (bx + sx * 46, by - 30), (bx + sx * 56, by + 4), (bx + sx * 40, by + 26)], C_RIBBON,
                           blob([(bx, by), (bx + sx * 40, by + 10), (bx + sx * 40, by + 26)], C_RIBBON_SH, .7), w=3.2, seed=sd + 98 + sx))
        o.append(shape(ellipse_pts(bx, by, 15, 14, 10), C_RIBBON_SH, "", w=3.0, seed=sd + 101))
    g = "".join(o)
    if taper > 0.001:     # ракурс снизу: верх уже низа (перспектива), сжатие по x растёт с высотой — кусочно по полосам
        H_ = n * SHEET_T + 40
        bands = []
        nb = 12
        for b in range(nb):
            y0_, y1_ = -H_ * (b + 1) / nb - 2, -H_ * b / nb + 2
            q = (b + .5) / nb
            sxk = 1 - taper * q
            cx_ = curve[min(n - 1, int(q * (n - 1)))][0]
            cid = lib.clip_rect(-2000, y0_, 4000, y1_ - y0_)
            bands.append(f'<g clip-path="url(#{cid})"><g transform="translate({f(cx_)} 0) scale({sxk:.4f} 1) translate({f(-cx_)} 0)">{g}</g></g>')
        bot = lib.clip_rect(-2000, -2, 4000, 400)
        g = "".join(bands) + f'<g clip-path="url(#{bot})">{g}</g>'
    if pull > 0:
        sx_, sy_ = scrap_pos(0, 0, 1.0, pull)
        g += scrap(sx_, sy_, 1.4, -20 * pull, seed)
    return _tf(g, x, y, k)


def engine_handle(x, y, k=1.0, cord=0.0):
    hx, hy = -96.0, -150.0
    L = 300 * clamp(cord)
    a = math.radians(-148)
    return (x + (hx + math.cos(a) * L) * k, y + (hy + math.sin(a) * L) * k)


def puff_cloud(x, y, k=1.0, u=1.0, seed=0, col="#D3D7DE"):
    if u <= 0.01 or u >= 1:
        return ""
    sd = 72400 + seed
    rs = _rs(sd)
    o = []
    grow = lib.ease_out(min(1, u / .45), 2)
    fade = 1 - lib.ease_in(max(0, (u - .45) / .55), 2)
    for j in range(5):
        a = 2 * math.pi * j / 5 + rs.uniform(-.4, .4)
        d = 30 * grow + 40 * (1 - fade)
        r = (30 + rs.uniform(-6, 10)) * grow * (.35 + .65 * fade)
        if r < 3:
            continue
        cx, cy = math.cos(a) * d, math.sin(a) * d * .7 - 20 * (1 - fade)
        o.append(shape(_puff_pts(2 * r, 2 * r * .85, sd + j, n=6, bump=(.08, .16)), col, "", w=3.6 * (.5 + .5 * fade), seed=sd + 10 + j) if r > 8 else
                 blob(ellipse_pts(cx, cy, r, r, 8), col))
        o[-1] = f'<g transform="translate({f(cx)} {f(cy)})">{o[-1]}</g>' if r > 8 else o[-1]
    return _tf("".join(o), x, y, k)


def pull_engine(x, y, k=1.0, cough=0.0, shake=0.0, cord=0.0, t=0.0, seed=0, handle=None, hand_ang=None):
    sd = 72500 + seed
    jx = shake * 7 * math.sin(t * 61)
    jy = shake * 5 * math.cos(t * 47)
    o = []
    o.append(blob(ellipse_pts(0, 6, 190, 20, 16), "#000000", .14))
    g = []
    # рама-салазки
    g.append(line([(-150, -6), (-140, 0), (150, 0), (160, -8)], 9, "#3B4048", taper=.05, wmin=.8, seed=sd))
    g.append(line([(-110, 0), (-96, -50)], 8, "#3B4048", taper=.05, wmin=.8, seed=sd + 1))
    g.append(line([(110, 0), (96, -50)], 8, "#3B4048", taper=.05, wmin=.8, seed=sd + 2))
    # корпус-кожух
    body = rrect(-120, -170, 110, -40, 26)
    inn = blob(rrect(-120, -90, 110, -40, 20), C_ENGINE_SH, .8) + line([(-96, -150), (60, -154)], 4, "#F08A7C", taper=.4, wmin=.3, seed=sd + 3)
    g.append(shape(body, C_ENGINE, inn, w=4.4, seed=sd + 4))
    # цилиндр с рёбрами справа
    cyl = rrect(90, -160, 170, -60, 12)
    fins = "".join(line([(92, -150 + 16 * j), (168, -150 + 16 * j)], 3.2, "#868B96", taper=.1, wmin=.7, seed=sd + 10 + j) for j in range(6))
    g.append(shape(cyl, C_METAL, fins, w=4.0, seed=sd + 5))
    # бак сверху
    g.append(shape(rrect(-70, -222, 50, -166, 16), "#E9C23E", blob(rrect(-70, -190, 50, -166, 12), "#C99A1E", .8), w=4.0, seed=sd + 6))
    g.append(shape(ellipse_pts(-20, -226, 16, 8, 10), "#3B4048", "", w=3.0, seed=sd + 7))
    # выхлоп справа вверху
    g.append(shape(rrect(170, -150, 214, -124, 8), "#5A616E", "", w=3.4, seed=sd + 8))
    # шкив стартера слева
    g.append(shape(ellipse_pts(-104, -118, 38, 40, 16), "#3B4048", blob(ellipse_pts(-104, -118, 14, 14, 10), "#14161B"), w=4.0, seed=sd + 9))
    o.append(f'<g transform="translate({f(jx)} {f(jy)})">{"".join(g)}</g>')
    # тросик: от шкива к ручке
    hx, hy = engine_handle(0, 0, 1.0, cord)
    if handle is not None:      # ручку держит рука: мировая точка → локальные координаты моторчика
        hx, hy = (handle[0] - x) / k, (handle[1] - y) / k
    sag = 14 * (1 - clamp(cord))
    o.append(line([(-104 + jx, -118 + jy), ((-104 + hx) / 2, (-118 + hy) / 2 + sag), (hx, hy)], 5.0, "#2B2E35", taper=.1, wmin=.7, seed=sd + 20))
    a = math.radians(hand_ang if hand_ang is not None else (-148 if cord > .02 else -100))
    ca, sa = math.cos(a), math.sin(a)
    hp = [(hx - sa * 30, hy + ca * 30), (hx + sa * 30, hy - ca * 30)]
    o.append(line(hp, 18, lib.INK, taper=.05, wmin=.9, seed=sd + 21))
    o.append(line(hp, 12, "#E9C23E", taper=.05, wmin=.9, seed=sd + 22))
    # кашель: клуб дыма из выхлопа
    if 0 < cough < 1:
        o.append(puff_cloud(225 + 30 * cough, -190 - 150 * cough, 1.2 + .8 * cough, cough, seed=sd % 97, col="#BFC4CC"))
    return _tf("".join(o), x, y, k)


def brain_kid(x, y, k=1.0, expr="calm", hop=0.0, t=0.0, look=(0.0, 0.0), seed=0, blink=0.0):
    sd = 72600 + seed
    wide = expr in ("wide", "scared")
    trem = (3 * math.sin(t * 55)) if expr == "scared" else 0.0
    o = []
    o.append(blob(ellipse_pts(0, 4, 100 * (1 + hop / 400), 14, 14), "#000000", .13))
    by = -120 + hop
    # ножки с ботиночками
    for sx in (-1, 1):
        lx = sx * 42
        o.append(line([(lx, by + 70), (lx + sx * 4, -16 + hop * .3)], 9, lib.INK, taper=.05, wmin=.9, seed=sd + sx))
        o.append(shape(ellipse_pts(lx + sx * 16, -10 + hop * .3, 30, 15, 12), "#4F78B5", blob(ellipse_pts(lx + sx * 18, -4 + hop * .3, 22, 7, 10), "#36588C"), w=3.6,
                       seed=sd + 5 + sx))
    # тело-мозг
    body = _brain_outline(130, 104, sd + 10)
    inner = blob(ellipse_pts(24, 34, 100, 70, 16), C_BRAIN_SH, .5) + _gyri(118, 92, sd + 11, wild=1.0 if wide else 0.0, t=t)
    o.append(f'<g transform="translate({f(trem)} {f(by)})">' + shape(body, C_BRAIN, inner, w=4.6, seed=sd + 12))
    # глаза-блюдца
    er = 40 if wide else 32
    lx, ly = look
    for sx in (-1, 1):
        ex, ey = sx * 46, 6
        if blink > .9 and not wide:
            o.append(line([(ex - er, ey), (ex, ey + 8), (ex + er, ey)], 4.6, lib.INK, taper=.4, wmin=.3, seed=sd + 20 + sx))
            continue
        pr = 7 if wide else 15
        ins = (f'<circle cx="{f(ex + lx * er * .4)}" cy="{f(ey + ly * er * .4)}" r="{pr}" fill="#14161B"/>'
               f'<circle cx="{f(ex + lx * er * .4 - pr * .4)}" cy="{f(ey + ly * er * .4 - pr * .5)}" r="{max(2.5, pr * .35):.1f}" fill="#FFFFFF"/>')
        o.append(shape(ellipse_pts(ex, ey, er, er * 1.08, 16), "#FFFFFF", ins, w=4.2, seed=sd + 22 + sx))
    # брови и рот
    if expr == "scared":
        o.append(line([(-80, -46), (-46, -54), (-22, -66)], 4.6, lib.INK, seed=sd + 30))
        o.append(line([(22, -66), (46, -54), (80, -46)], 4.6, lib.INK, seed=sd + 31))
        o.append(line([(-20, 66), (-8, 60), (6, 66), (20, 60)], 4.0, lib.INK, taper=.3, wmin=.4, seed=sd + 32))
    elif expr == "wide":
        o.append(shape(ellipse_pts(0, 68, 11, 13, 10), "#5a2b33", "", w=3.6, seed=sd + 33))
    elif expr == "peek":
        o.append(line([(-14, 62), (0, 66), (14, 62)], 4.0, lib.INK, taper=.3, wmin=.4, seed=sd + 34))
    else:
        o.append(line([(-18, 60), (0, 70), (18, 60)], 4.0, lib.INK, taper=.3, wmin=.4, seed=sd + 35))
    o.append(blob(ellipse_pts(-86, 44, 16, 9, 10), "#E98A86", .5) + blob(ellipse_pts(86, 44, 16, 9, 10), "#E98A86", .5))
    o.append("</g>")
    return _tf("".join(o), x, y, k)


def fire_light(x, y, k=1.0, u=1.0, t=0.0):
    return clamp(u) * (.86 + .08 * math.sin(t * 13) + .06 * math.sin(t * 29 + 1.3))


def _flame_tongue(h, w, t, ph, col, core):
    sw = .18 * w * math.sin(t * 9 + ph) + .1 * w * math.sin(t * 17 + ph * 2)
    tip = (sw, -h)
    pts = [(-w * .5, 0), (-w * .55, -h * .3), (-w * .3 + sw * .3, -h * .62), tip + (1,), (w * .32 + sw * .4, -h * .58), (w * .55, -h * .28), (w * .5, 0)]
    inn = [(-w * .28, 0), (-w * .26, -h * .3), (sw * .6, -h * .62, 1), (w * .26, -h * .3), (w * .28, 0)]
    return shape(pts, col, blob(inn, core), w=3.6, seed=int(ph * 100) % 997 + 72700, ink_color="#7a2a10", var=.2)


def campfire(x, y, k=1.0, u=1.0, t=0.0, seed=0, stones=True):
    sd = 72700 + seed
    rs = _rs(sd)
    o = []
    # камни кольцом (дальние — сначала)
    if stones:
        ring_ = []
        for j in range(11):
            a = 2 * math.pi * j / 11 + .2
            ring_.append((math.sin(a), 150 * math.cos(a), 52 * math.sin(a), j))
        for sa, cx, cy, j in sorted(ring_, key=lambda r: r[2]):
            if cy > 0:
                continue
            s = 1 + .1 * rs.uniform(-1, 1)
            o.append(shape(ellipse_pts(cx, cy, 34 * s, 22 * s, 12), "#8A8F99", blob(ellipse_pts(cx + 6, cy + 8, 26 * s, 12 * s, 10), "#5F646E", .8), w=3.8, seed=sd + j))
    # угли под брёвнами
    glow_u = clamp(.25 + .75 * u)
    o.append(shape(ellipse_pts(0, -6, 96, 26, 14), mix("#3B2A22", "#C2491E", glow_u), blob(ellipse_pts(-10, -10, 60, 12, 12), mix("#5A3524", "#FFB04A", glow_u), .9),
                   w=3.6, seed=sd + 20))
    # брёвна крест-накрест
    for sx, sd2 in ((-1, 21), (1, 22)):
        lg = [(-120 * sx, 6, 1), (-128 * sx, -18, 1), (40 * sx, -62, 1), (54 * sx, -40, 1)]
        o.append(shape(lg, C_WOOD_SH, line([(-100 * sx, -10), (30 * sx, -48)], 3, "#5E3A1E", taper=.4, wmin=.3, seed=sd + sd2 + 50), w=4.2, seed=sd + sd2))
        o.append(shape(ellipse_pts(-124 * sx, -6, 14, 14, 10), C_WOOD_HI, blob(ellipse_pts(-124 * sx, -6, 6, 6, 8), "#7A4A26"), w=3.4, seed=sd + sd2 + 5))
    # пламя / тлеющий уголёк
    if u < .15:
        e = .5 + .5 * math.sin(t * 7)
        o.append(blob(ellipse_pts(4, -40, 9 + 2 * e, 7 + 2 * e, 10), mix("#C2491E", "#FFD24A", e)))
        o.append(blob(ellipse_pts(4, -40, 4, 3, 8), "#FFF2C0"))
        o.append(smoke_curls(6, -50, .7, .8, t, seed=sd % 50, col="#6F7787", n=1))
    else:
        uu = clamp((u - .15) / .85)
        H = 300 * (.25 + .75 * uu)
        tongues = [(-46, .6, .55, 0.3), (40, .7, .5, 1.7), (-12, 1.0, .7, 2.9), (14, .82, .45, 4.1)]
        for dx, hh, ww, ph in tongues:
            o.append(f'<g transform="translate({f(dx * (.5 + .5 * uu))} -30)">' + _flame_tongue(H * hh, 150 * ww * (.5 + .5 * uu), t, ph, "#F28C28", "#FFD24A") + "</g>")
        o.append(f'<g transform="translate(0 -30)">' + _flame_tongue(H * .55, 80 * (.5 + .5 * uu), t * 1.3, 5.3, "#FFC23A", "#FFF2C0") + "</g>")
    # искры вверх
    if u > .05:
        for j in range(7):
            ph = (t * .9 + j / 7 + rs.uniform(0, .1)) % 1
            sx = 40 * math.sin(j * 2.1 + t * 2) * ph + rs.uniform(-60, 60)
            sy = -60 - 420 * ph * (.4 + .6 * u)
            r = 5 * (1 - ph) * clamp(u * 2)
            if r > .8:
                o.append(blob(ellipse_pts(sx, sy, r, r, 8), "#FFD24A"))
    # ближние камни
    if stones:
        for sa, cx, cy, j in sorted(ring_, key=lambda r: r[2]):
            if cy <= 0:
                continue
            s = 1 + .1 * rs.uniform(-1, 1)
            o.append(shape(ellipse_pts(cx, cy, 38 * s, 24 * s, 12), "#8A8F99", blob(ellipse_pts(cx + 6, cy + 8, 28 * s, 13 * s, 10), "#5F646E", .8) +
                           blob(ellipse_pts(cx - 8, cy - 10, 16 * s, 7 * s, 8), mix("#8A8F99", "#FFB04A", .4 * u)), w=3.8, seed=sd + j + 30))
    return _tf("".join(o), x, y, k)


def log_seat(x, y, k=1.0, w=700.0, seed=0):
    sd = 72800 + seed
    hw = w / 2
    body = [(-hw, -10, 1), (-hw + 10, -96, 1), (hw - 30, -100, 1), (hw - 30, -6, 1)]
    bark = "".join(line([(-hw + 40 + 90 * j, -88 + 6 * (j % 2)), (-hw + 80 + 90 * j, -60), (-hw + 60 + 90 * j, -20)], 3.2, "#5E3A1E", taper=.6, wmin=.2,
                        seed=sd + j) for j in range(int(w / 90)))
    o = [blob(ellipse_pts(0, 4, hw, 16, 16), "#000000", .18)]
    o.append(shape(body, C_WOOD_SH, blob([(-hw, -60), (hw, -60), (hw, -6), (-hw, -6)], "#6E4626", .8) + bark, w=4.4, seed=sd + 50))
    ins = "".join(blob(ellipse_pts(hw - 30, -53, 38 - 9 * j, 44 - 10 * j, 14), mix(C_WOOD_HI, "#E9C99A", j % 2)) for j in range(4))
    o.append(shape(ellipse_pts(hw - 30, -53, 40, 47, 16), C_WOOD_HI, ins, w=4.2, seed=sd + 51))
    return _tf("".join(o), x, y, k)


def hanging_sack(x, y, k=1.0, sway=0.0, drop=0.0, t=0.0, seed=0):
    sd = 72900 + seed
    o = []
    # ветка уходит влево за кадр, сучок вправо
    o.append(line([(-900, -40), (-400, -20), (0, 0), (160, 14)], 30, C_WOOD_SH, taper=.15, wmin=.4, seed=sd))
    o.append(line([(-900, -40), (-400, -20), (0, 0), (160, 14)], 6, lib.INK, taper=.15, wmin=.4, seed=sd + 1, op=.0))
    o.append(line([(-300, -24), (-250, -90), (-210, -110)], 12, C_WOOD_SH, taper=.6, wmin=.2, seed=sd + 2))
    for j, (lx, ly) in enumerate(((-240, -100), (-200, -112), (60, 10))):
        o.append(shape(ellipse_pts(lx, ly - 18, 16, 30, 10, rot=-30 + 50 * j), C_GREEN, line([(lx, ly), (lx, ly - 36)], 2, C_GREEN_SH, seed=sd + 40 + j), w=3.2, seed=sd + 30 + j))
    rope_len = 170.0
    dy = 0.0
    if drop > 0:
        dy = 420 * lib.ease_in(clamp(drop), 2)
    a = math.radians(sway + (0 if drop <= 0 else 14 * drop))
    end = (math.sin(a) * rope_len, math.cos(a) * rope_len + dy)
    if drop <= 0:
        o.append(line([(0, 0), (end[0] * .5, end[1] * .5 + 4), end], 4, "#8A6A3E", taper=.05, wmin=.8, seed=sd + 3))
    else:
        o.append(line([(0, 0), (6 * math.sin(t * 9), 40)], 4, "#8A6A3E", taper=.4, wmin=.5, seed=sd + 3))
    # мешок-узелок: тело ниже узла
    sack = [(-70, 40, 1), (-96, 110), (-86, 170), (-40, 196), (40, 196), (86, 170), (96, 110), (70, 40, 1), (30, 18), (-30, 18)]
    inn = blob([(10, 40), (96, 100), (90, 190), (20, 196)], "#A88A5C", .7) + line([(-40, 70), (-20, 150)], 3, "#8A6A3E", taper=.6, wmin=.2, seed=sd + 6)
    s = shape(sack, "#C9A874", inn, w=4.4, seed=sd + 4)
    s += shape([(-40, 22, 1), (-56, -18), (-10, 4), (10, 4), (56, -18), (40, 22, 1)], "#C9A874", "", w=3.8, seed=sd + 5)   # ушки узла
    s += shape(ellipse_pts(0, 18, 20, 12, 10), "#A88A5C", "", w=3.4, seed=sd + 7)
    o.append(f'<g transform="translate({f(end[0])} {f(end[1])}) rotate({f(-math.degrees(a) * .6)})">{s}</g>')
    return _tf("".join(o), x, y, k)


def ice_cube(x, y, k=1.0, rot=0.0, seed=0):
    sd = 73000 + seed
    s = 45
    front = [(-s, -s + 14, 1), (s - 14, -s + 14, 1), (s - 14, s, 1), (-s, s, 1)]
    top = [(-s, -s + 14, 1), (-s + 14, -s, 1), (s, -s, 1), (s - 14, -s + 14, 1)]
    side = [(s - 14, -s + 14, 1), (s, -s, 1), (s, s - 14, 1), (s - 14, s, 1)]
    o = shape(side, C_ICE_SH, "", w=3.2, seed=sd + 1) + shape(top, C_ICE_HI, "", w=3.2, seed=sd + 2)
    o += shape(front, C_ICE, line([(-s + 10, -s + 26), (-s + 10, s - 18)], 4, "#FFFFFF", taper=.4, wmin=.3, seed=sd + 3) +
               line([(-s + 22, -s + 24), (-s + 34, -s + 24)], 3, "#FFFFFF", taper=.3, wmin=.4, seed=sd + 4), w=3.6, seed=sd)
    return _tf(o, x, y, k, rot)


def ice_row_pos(x, y, k=1.0, split=0.0, n=5, i=0):
    u = lib.ease_out(clamp(split), 3)
    cols, rows = 3, 2
    r_, c_ = divmod(i, cols)
    sx, sy = -100 + 100 * c_, -200 + 110 * r_ if n > 3 else -100
    tx, ty = (i - (n - 1) / 2) * 120, -48
    hop_ = -60 * math.sin(math.pi * u)
    return (x + (sx + (tx - sx) * u) * k, y + (sy + (ty - sy) * u + hop_) * k)


def ice_block(x, y, k=1.0, crack=0.0, split=0.0, t=0.0, n=5, seed=0):
    sd = 73100 + seed
    o = []
    if split <= 0.02:
        o.append(blob(ellipse_pts(0, 6, 190, 20, 16), "#000000", .14))
        front = [(-160, -250, 1), (110, -250, 1), (120, 0, 1), (-170, 0, 1)]
        top = [(-160, -250, 1), (-110, -300, 1), (160, -300, 1), (110, -250, 1)]
        side = [(110, -250, 1), (160, -300, 1), (170, -50, 1), (120, 0, 1)]
        inn = line([(-140, -230), (-136, -40)], 6, "#FFFFFF", taper=.4, wmin=.3, seed=sd + 1) + line([(-120, -232), (-80, -232)], 4, "#FFFFFF", taper=.3, wmin=.4, seed=sd + 2)
        inn += blob([(-40, -160), (40, -170), (60, -90), (-20, -70)], C_ICE_SH, .35)
        if crack > 0:
            rs = _rs(sd + 5)
            for j in range(4):
                p = [(-25 + 20 * j, -250)]
                L = clamp(crack * 1.4 - j * .12)
                for m in range(1, 7):
                    if m / 6 > L:
                        break
                    p.append((p[-1][0] + rs.uniform(-34, 34), -250 + 250 * m / 6))
                if len(p) > 1:
                    inn += line(p, 5, "#3F7FA0", taper=.3, wmin=.3, seed=sd + 10 + j)
        o.append(shape(side, C_ICE_SH, "", w=4.0, seed=sd + 3) + shape(top, C_ICE_HI, "", w=4.0, seed=sd + 4) + shape(front, C_ICE, inn, w=4.6, seed=sd))
        if crack > .5:      # колкие искорки льда
            for j in range(4):
                a = math.radians(-120 + 30 * j)
                r0 = 200 + 40 * math.sin(t * 20 + j)
                o.append(line([(math.cos(a) * r0, -150 + math.sin(a) * r0), (math.cos(a) * (r0 + 40), -150 + math.sin(a) * (r0 + 40))], 5, "#3F7FA0", taper=.6,
                              wmin=.1, seed=sd + 30 + j))
        return _tf("".join(o), x, y, k)
    for i in range(n):
        cx, cy = ice_row_pos(0, 0, 1.0, split, n, i)
        o.append(blob(ellipse_pts(cx, -2, 50, 9, 10), "#000000", .12 * clamp(split * 2)))
        o.append(ice_cube(cx, cy, 1.25, (1 - clamp(split)) * (20 - 9 * i), seed=seed * 10 + i))
    return _tf("".join(o), x, y, k)


def bean_seat(x, y, k=1.0, sag=0.0):
    return (x - 20 * k, y - (190 - 50 * sag) * k)


def bean_bag(x, y, k=1.0, sag=0.0, seed=0, col=None):
    sd = 73200 + seed
    c, csh, chi = col or (C_BAG, C_BAG_SH, C_BAG_HI)
    w = 260 * (1 + .14 * sag)
    h = 360 * (1 - .18 * sag)
    pts = [(-w, -6, 1), (-w - 14, -h * .32), (-w * .78, -h * .72), (-w * .3, -h * .98), (w * .2, -h), (w * .7, -h * .84), (w + 10, -h * .4), (w, -6, 1)]
    inn = blob([(-w * .2, -h * .55), (w * .5, -h * .6), (w + 30, -h * .3), (w + 30, 10), (-w * .1, 10)], csh, .75)
    inn += blob(ellipse_pts(-w * .25, -h * .58, w * .5, h * .2, 16), mix(csh, c, .3), .7)      # вмятина под сидящим
    inn += line([(-w * .55, -h * .78), (-w * .35, -h * .5), (-w * .4, -h * .2)], 3.4, csh, taper=.6, wmin=.2, seed=sd + 1)
    inn += line([(w * .4, -h * .8), (w * .55, -h * .5)], 3.4, csh, taper=.6, wmin=.2, seed=sd + 2)
    inn += blob(ellipse_pts(-w * .5, -h * .82, 40, 16, 10, rot=-20), chi, .8)
    o = blob(ellipse_pts(0, 4, w * 1.05, 22, 16), "#000000", .16) + shape(pts, c, inn, w=4.6, seed=sd)
    return _tf(o, x, y, k)
