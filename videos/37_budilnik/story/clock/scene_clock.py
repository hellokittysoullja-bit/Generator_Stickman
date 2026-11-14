"""Сцена clock рилса 37: будильник (alarm.py) на тумбочке у дивана утром.
s01 хук — влёт камеры, будильник звенит и скачет, на «будильник» (0.48) — самый высокий прыжок.
s03 — стрелки бешено крутятся 7:00 → 9:00, за окном светлеет, на «девять» (2.88) встают со стуком.
s04 — из-под пледа рука хлопает по будильнику на «пять» (4.24), звон обрывается, «+5 мин».
s05 — снова звонит, хлопок на «пять» (5.52), счётчик 1 → 2.
s06 — серия хлопков, счётчик 3 → 9 к «девять» (6.64), красный круг; на «раз» (7.04) будильник сплющен, звёздочки.
s09 — угол комнаты у пола: будильник звенит, сверху падает плед на «одеялом» (11.28), бугор трясётся.
Всё — функция общего времени ролика t."""
import math

import numpy as np

import alarm as AL
import lib
from lib import (INK, W, H, back_out, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad,
                 mix, rad_grad, rect_pts, shape, smooth, spring, svg)

E = ellipse_pts
WORDS = lib.words()


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?").lower() == word:
            return w["start"]
    raise KeyError(word)


T_BUD = wt("будильник")          # 0.48
T_NINE = wt("девять")            # 2.88
T_FIVE1 = wt("пять")             # 4.24
T_FIVE2 = wt("пять", 5.0)        # 5.52
T_NINE2 = wt("девять", 6.0)      # 6.64
T_RAZ = wt("раз", 6.9)           # 7.04
T_BLANKET = wt("одеялом", 11.0)  # 11.28

SKIN, SKIN_SH, SKIN_SH2, NAIL = "#ecc4a2", "#d39f83", "#bf8a74", "#f6dccb"
HOOD, HOOD_SH, HOOD_SH2, FOLD = "#d4a23e", "#a97b25", "#8c6219", "#6b4a12"
PLAID, PLAID_D, PLAID_L, PLAID_R = "#4f7d55", "#35583c", "#8fb08a", "#c9473a"   # плед: зелёная клетка с красной нитью
WOOD, WOOD_SH, WOOD_D, WOOD_HI = "#b5794a", "#8e5a34", "#6d4226", "#d39a68"

CLK = (450.0, 860.0)    # центр циферблата на тумбочке
CSZ = 230.0             # радиус корпуса
TOP = 1196.0            # передний край столешницы (низ ножек будильника — чуть выше)
FOOT = CLK[1] + AL.FOOT_Y / 200 * CSZ


# ───────────────────────── фон: стена, окно, тумбочка, край дивана
def plaid_pattern(pid, tf="", scale=1.0):
    """Клетка пледа: тёмные полосы крест-накрест + тонкая красная нить; pattern в userSpace с transform."""
    s = 120 * scale
    p = (f'<pattern id="{pid}" width="{f(s)}" height="{f(s)}" patternUnits="userSpaceOnUse" patternTransform="{tf}">'
         f'<rect width="{f(s)}" height="{f(s)}" fill="{PLAID}"/>'
         f'<rect x="0" y="{f(s * .35)}" width="{f(s)}" height="{f(s * .3)}" fill="{PLAID_D}" opacity=".55"/>'
         f'<rect x="{f(s * .35)}" y="0" width="{f(s * .3)}" height="{f(s)}" fill="{PLAID_D}" opacity=".55"/>'
         f'<rect x="0" y="{f(s * .86)}" width="{f(s)}" height="{f(s * .04)}" fill="{PLAID_R}"/>'
         f'<rect x="{f(s * .86)}" y="0" width="{f(s * .04)}" height="{f(s)}" fill="{PLAID_R}"/>'
         f'<rect x="0" y="{f(s * .12)}" width="{f(s)}" height="{f(s * .03)}" fill="{PLAID_L}" opacity=".8"/>'
         f'<rect x="{f(s * .12)}" y="0" width="{f(s * .03)}" height="{f(s)}" fill="{PLAID_L}" opacity=".8"/>'
         f'</pattern>')
    lib.DEFS.append(p)
    return pid


def room_bg(light):
    """Стена с обоями, окно слева (небо светлеет с light 0..1), косой луч света на стене."""
    s = []
    wall = mix("#5f6a8a", "#a9b6c9", light)
    wall2 = mix("#525c7a", "#93a1b8", light)
    s.append(f'<rect x="-900" y="-900" width="{W + 1800}" height="{TOP + 900}" fill="{wall}"/>')
    # обои: вертикальные полосы с ромбиками
    for k in range(-8, 16):
        x = k * 96
        s.append(f'<rect x="{x}" y="-900" width="22" height="{TOP + 900}" fill="{wall2}" opacity=".45"/>')
    # окно
    wx0, wx1, wy0, wy1 = -420, 60, 130, 760
    sky0 = mix("#2f3c6e", "#9fd2f2", light)
    sky1 = mix("#c98c86", "#fff1c8", light)
    g = lin_grad([(0, sky0, 1), (1, sky1, 1)], 0, 0, 0, 1)
    s.append(shape(rect_pts(wx0 - 26, wy0 - 26, wx1 + 26, wy1 + 26), "#e9e2d4",
                   blob(rect_pts(wx0 - 26, wy1 - 6, wx1 + 26, wy1 + 26), "#cfc5b2"), w=5, seed=301))
    inner = f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="url(#{g})"/>'
    # дома за окном силуэтом
    bcol = mix("#25305a", "#8fb0cc", light)
    for k, (bx, bw, bh) in enumerate([(-410, 120, 300), (-280, 90, 380), (-180, 140, 260), (-30, 110, 340)]):
        inner += blob(rect_pts(bx, wy1 - bh, bx + bw, wy1 + 10), bcol)
        for r in range(3):
            for c in range(2):
                wcol = mix("#ffd27a", "#cfe3f0", light)
                inner += blob(rect_pts(bx + 18 + c * 40, wy1 - bh + 30 + r * 70, bx + 40 + c * 40, wy1 - bh + 62 + r * 70), wcol, .9)
    # солнце поднимается
    sy = wy1 - 60 - 380 * light
    inner += f'<circle cx="-100" cy="{f(sy)}" r="54" fill="{mix("#ff9f6a", "#fff4c2", light)}"/>'
    s.append(shape(rect_pts(wx0, wy0, wx1, wy1), "#000", inner, w=4.4, seed=302))
    s.append(line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], 16, "#e9e2d4", taper=0, wmin=1, seed=303))
    s.append(line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], 16, "#e9e2d4", taper=0, wmin=1, seed=304))
    # штора справа от окна
    cur = [(64, 90, 1), (170, 90, 1), (150, 400), (180, 760), (140, 1000, 1), (76, 1000, 1), (88, 700), (64, 400)]
    s.append(shape(cur, mix("#8a4f52", "#d9837a", light), blob([(120, 90), (170, 90), (150, 400), (180, 760), (140, 1000), (130, 600)],
                                                                   mix("#6b3a3e", "#b9665f", light), .9) +
                   line([(100, 140), (112, 500), (106, 900)], 3, mix("#5b2e33", "#a0544e", light), seed=306, op=.8), w=5, seed=305))
    # луч света из окна — плоская светлая трапеция (без размытия)
    if light > 0.05:
        beam = [(60, 160), (400, 280), (1300, TOP), (480, TOP)]
        s.append(blob(beam, mix("#c7b38e", "#fff6dc", light), .18 + 0.22 * light))
    return "".join(s)


def nightstand(light):
    s = []
    sh = mix("#c8b8a2", "#ffffff", 0)
    # столешница: верх (полоса глубины) + передняя кромка
    top = [(-60, TOP - 96, 1), (900, TOP - 96, 1), (930, TOP, 1), (-90, TOP, 1)]
    inner = blob([(-60, TOP - 96), (900, TOP - 96), (910, TOP - 70), (-70, TOP - 70)], mix("#7a4d2c", WOOD_SH, light), .6)
    inner += "".join(line([(-60 + k * 210, TOP - 80 + (k % 2) * 30), (100 + k * 210, TOP - 70 + (k % 2) * 30)], 2.6, WOOD_SH, seed=320 + k, op=.7)
                     for k in range(5))
    inner += blob([(380, TOP - 96), (700, TOP - 96), (880, TOP), (520, TOP)], WOOD_HI, .35 * light)
    s.append(shape(top, mix("#8e5d39", WOOD, light), inner, w=5.2, seed=321))
    front = [(-90, TOP, 1), (930, TOP, 1), (930, TOP + 44, 1), (-90, TOP + 44, 1)]
    s.append(shape(front, mix("#6e4428", WOOD_SH, light), "", w=5.2, seed=322))
    body = [(-70, TOP + 44, 1), (910, TOP + 44, 1), (910, 2300, 1), (-70, 2300, 1)]
    binner = blob([(600, TOP + 44), (910, TOP + 44), (910, 2300), (600, 2300)], WOOD_D, .5)
    s.append(shape(body, mix("#6a4125", WOOD_SH, light), binner, w=5.2, seed=323))
    # ящик с ручкой
    s.append(shape(rect_pts(-20, TOP + 90, 860, TOP + 400, 14), mix("#76492a", WOOD, light * .85),
                   blob(rect_pts(-20, TOP + 330, 860, TOP + 400), WOOD_SH, .8), w=4.6, seed=324))
    s.append(shape(E(420, TOP + 220, 34, 16, 14), mix("#a88b5a", "#e6c98a", light), blob(E(426, TOP + 226, 30, 12, 10), "#b38f4e", .8),
                   w=3.6, seed=325))
    # стакан воды сзади слева
    gx, gy = 120, TOP - 60
    s.append(shape([(gx - 46, gy - 170, 1), (gx + 46, gy - 170, 1), (gx + 38, gy, 1), (gx - 38, gy, 1)], mix("#7f91b0", "#d8ecf6", light),
                   blob([(gx - 44, gy - 110), (gx + 44, gy - 110), (gx + 38, gy), (gx - 38, gy)], mix("#5e7fb0", "#9fd0ee", light), .9) +
                   blob([(gx - 30, gy - 160), (gx - 20, gy - 160), (gx - 16, gy - 20), (gx - 26, gy - 20)], "#ffffff", .55), w=4.2, seed=326))
    s.append(shape(E(gx, gy - 170, 46, 9, 16), mix("#9aabc8", "#eef8fc", light), "", w=3.2, seed=327))
    return "".join(s)


def bed_edge(light, pid="pPlaid"):
    """Край дивана-кровати справа: ножка, матрас, простыня и плед в клетку, свисающий складками."""
    s = []
    # каркас дивана
    s.append(shape([(760, 1010, 1), (1500, 1010, 1), (1500, 2600, 1), (760, 2600, 1)], mix("#5d4a6c", "#8f7aa6", light),
                   blob(rect_pts(760, 1330, 1500, 2600), mix("#463653", "#6f5b86", light)), w=5.4, seed=340))
    # простыня
    s.append(shape([(770, 940), (900, 920), (1400, 930, 1), (1400, 1060, 1), (780, 1060)], mix("#c4c6cf", "#f6f2ea", light),
                   blob([(780, 1030), (1400, 1020), (1400, 1060), (780, 1060)], mix("#a5a8b6", "#ddd8cc", light)), w=4.8, seed=341))
    return "".join(s)


def plaid_layer(light, pid="pPlaid"):
    s = []
    plaid_pattern(pid, "rotate(8) translate(30 10)")
    pl = [(800, 860), (860, 790), (980, 760), (1200, 740), (1400, 760, 1), (1400, 1380, 1), (1240, 1400), (1120, 1360), (1000, 1390),
          (880, 1350), (820, 1260), (812, 1100)]
    inner = f'<rect x="700" y="600" width="800" height="900" fill="url(#{pid})"/>'
    inner += blob([(800, 1000), (900, 1060), (1000, 1100), (1000, 1400), (800, 1400)], "#1d2f22", .35)
    inner += blob([(980, 780), (1200, 760), (1180, 820), (980, 850)], "#ffffff", .10 + .1 * light)
    inner += line([(880, 900), (900, 1100), (880, 1300)], 4, "#1f3324", seed=343, op=.7)
    inner += line([(1060, 900), (1080, 1120), (1040, 1340)], 4, "#1f3324", seed=344, op=.6)
    s.append(shape(pl, PLAID, inner, w=5.6, seed=342))
    return "".join(s)


def table_shadow(cx, size, op=0.32):
    return AL.shadow(cx, FOOT + 4, size, op)


# ───────────────────────── рука
def sausage(pts, w0, w1):
    S = lib.sample(pts, False, 2.0)
    T = np.gradient(S, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    Wd = np.linspace(w0, w1, len(S))[:, None] / 2
    L, R = S + N * Wd, S - N * Wd
    end, tn, nn = S[-1], T[-1], N[-1]
    r = w1 / 2
    cap = [tuple(end + nn * r * math.cos(a) + tn * r * math.sin(a)) for a in np.linspace(0, math.pi, 9)[1:-1]]
    step = max(1, len(S) // 10)
    return [tuple(p) for p in L[::step]] + [tuple(L[-1])] + cap + [tuple(R[-1])] + [tuple(p) for p in R[::-step]]


def hand_flat(sd=0, spread=0.0):
    """Кисть ладонью вниз, пальцы влево, вид спереди-сверху: тыл кисти, четыре пальца (мизинец дальше всех, выше),
    большой палец ближе к зрителю (ниже). Запястье в (0, 0); низ ладони — y ≈ +44."""
    s = []
    fingers = [(-30, 70, 26, -6), (-12, 86, 28, -2), (6, 94, 29, 2), (24, 86, 29, 6)]     # (dy основания, длина, толщина, наклон)
    for k, (dy, L, w, tilt) in enumerate(fingers):
        dy2 = dy + spread * (k - 1.5) * 8
        x0, y0 = -104, dy2
        pts = [(x0 + 20, y0), (x0 - L * .5, y0 + 2 + tilt * .5), (x0 - L, y0 + 10 + tilt)]
        poly = sausage(pts, w, w * .86)
        inner = blob([(p[0], p[1] + w * .32) for p in poly], SKIN_SH, .55)
        s.append(shape(poly, SKIN, inner, w=3.6, seed=sd + 10 + k))
        tx, ty = x0 - L + 9, y0 + 8 + tilt
        s.append(blob(E(tx, ty - 3, 9, 7, 10), NAIL, .9))
        s.append(line([(x0 - L * .45, y0 - w * .4), (x0 - L * .45 + 3, y0 + w * .2)], 2.2, SKIN_SH2, seed=sd + 20 + k, op=.8))
    # большой палец под краем ладони: виден ниже тыла кисти, ближе к зрителю
    th = sausage([(-20, 22), (-62, 44), (-98, 52)], 34, 27)
    s.append(shape(th, SKIN, blob([(p[0], p[1] + 9) for p in th], SKIN_SH, .55), w=4.0, seed=sd + 50))
    s.append(blob(E(-91, 50, 8, 6, 10, rot=-12), NAIL, .9))
    back = [(14, -40), (-50, -50), (-100, -44), (-122, -22), (-124, 12), (-112, 42), (-60, 48), (-10, 44), (16, 30)]
    inner = blob([(-124, 14), (-112, 42), (-60, 48), (-10, 44), (16, 30), (10, 18), (-60, 30)], SKIN_SH, .9)
    inner += line([(-30, -30), (-84, -30)], 2.4, SKIN_SH2, seed=sd + 41, op=.6)
    inner += line([(-24, -12), (-86, -10)], 2.4, SKIN_SH2, seed=sd + 42, op=.5)
    s.append(shape(back, SKIN, inner, w=4.4, seed=sd + 40))
    for k, y in enumerate((-30, -12, 6, 24)):
        s.append(line([(-110, y - 6), (-118, y + 2), (-110, y + 9)], 2.4, SKIN_SH2, seed=sd + 45 + k, op=.8))
    return "".join(s)


def arm(p0, wrist, ctrl, hand_rot=0.0, sc=1.25, sd=0, spread=0.0):
    """Рукав от p0 (из-под пледа) к запястью по кривой через ctrl, кисть ладонью вниз."""
    pts = [p0, ctrl, wrist]
    S = sausage(pts, 128, 104)
    sleeve = shape(S, HOOD, blob([(p[0] + 8, p[1] + 26) for p in S], HOOD_SH, .8) +
                   line(lib.sample([(p0[0] * .7 + wrist[0] * .3, p0[1] * .7 + wrist[1] * .3 - 10), (ctrl[0], ctrl[1] + 20),
                                    (wrist[0] * .8 + ctrl[0] * .2, wrist[1] * .8 + ctrl[1] * .2 + 10)], False, 8)[::3].tolist(),
                        3.4, FOLD, seed=sd + 1, op=.7), w=5.4, seed=sd)
    ang = math.degrees(math.atan2(wrist[1] - ctrl[1], wrist[0] - ctrl[0]))
    # манжета поверх запястья
    ca = math.radians(ang)
    dx, dy = math.cos(ca), math.sin(ca)
    nx, ny = -dy, dx
    cx_, cy_ = wrist[0] - dx * 2 * sc, wrist[1] - dy * 2 * sc
    hw = 54
    cuff = [(cx_ - dx * 20 + nx * hw, cy_ - dy * 20 + ny * hw, 1), (cx_ + dx * 16 + nx * hw * .92, cy_ + dy * 16 + ny * hw * .92, 1),
            (cx_ + dx * 16 - nx * hw * .92, cy_ + dy * 16 - ny * hw * .92, 1), (cx_ - dx * 20 - nx * hw, cy_ - dy * 20 - ny * hw, 1)]
    cuff_s = shape(cuff, HOOD_SH, "".join(line([(cx_ + dx * u + nx * hw * .8, cy_ + dy * u + ny * hw * .8),
                                                 (cx_ + dx * u - nx * hw * .8, cy_ + dy * u - ny * hw * .8)], 2.2, FOLD, seed=sd + 5 + i, op=.7)
                                            for i, u in enumerate((-12, -2, 8))), w=4.4, seed=sd + 3)
    hand = f'<g transform="translate({f(wrist[0])} {f(wrist[1])}) rotate({f(hand_rot)}) scale({f(sc)})">{hand_flat(sd + 100, spread)}</g>'
    return sleeve + hand + cuff_s


def speed_lines(x, y, n, L, sd, color=INK):
    return "".join(line([(x + (k - (n - 1) / 2) * 46, y - L), (x + (k - (n - 1) / 2) * 46, y)], 6, color, taper=.7, seed=sd + k)
                   for k in range(n))


def impact(x, y, e, sd, r0=60, n=9, color=INK, L=70, w=9, span=1.0):
    """Штрихи удара во все стороны, кроме вниз; e — секунды после удара (живут 0.25 с)."""
    if e < 0 or e > 0.25:
        return ""
    u = e / 0.25
    s = []
    for k in range(n):
        a = math.pi + k * math.pi * span / (n - 1)
        r = r0 + 90 * ease_out(u)
        Lk = L * (1 - u)
        s.append(line([(x + math.cos(a) * r, y + math.sin(a) * r * .8), (x + math.cos(a) * (r + Lk), y + math.sin(a) * (r + Lk) * .8)],
                      w, color, taper=.5, seed=sd + k))
    return "".join(s)


def star(x, y, r, rot=0.0, color="#ffd23f", sd=0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(rot + i * 36 - 90)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, 1))
    return shape(pts, color, blob(E(x - r * .15, y - r * .2, r * .25, r * .18, 8), "#fff6c2", .9), w=max(2.0, r * .09), seed=sd)


def label(x, y, txt, sc, sd, fill="#ffd23f", tcol=INK, rot=-6):
    """Плашка-стикер с надписью (шрифт IDB): жёлтая, тушь по контуру, наклон."""
    if sc <= 0.02:
        return ""
    w = 34 * len(txt) + 60
    h = 108
    body = shape(rect_pts(-w / 2, -h / 2, w / 2, h / 2, 26), fill, blob(rect_pts(-w / 2, h / 2 - 22, w / 2, h / 2), "#e0a92a", .9),
                 w=5, seed=sd)
    tx = (f'<text x="0" y="22" text-anchor="middle" font-family="IDB" font-size="64" fill="{tcol}" '
          f'stroke="{tcol}" stroke-width="1.5">{txt}</text>')
    return f'<g transform="translate({f(x)} {f(y)}) rotate({rot}) scale({f(sc)})">{body}{tx}</g>'


def counter(x, y, n, sc, sd, circle=0.0, pop=0.0):
    """Счётчик-табличка в углу: картонка на скотче, «×» и цифра; circle 0..1 — красный круг дорисовывается."""
    s = []
    s.append(shape(rect_pts(-120, -100, 120, 100, 14), "#fbf3df", blob(rect_pts(-120, 70, 120, 100), "#e8dcc0", .9) +
                   line([(-96, -60), (96, -60)], 2.6, "#c9b99a", seed=sd + 1, op=.8), w=5, seed=sd))
    s.append(shape([(-46, -118, 1), (46, -112, 1), (44, -84, 1), (-48, -90, 1)], "#e8e2c4", "", w=2.4, seed=sd + 2))
    s.append(f'<text x="-46" y="46" text-anchor="middle" font-family="IDB" font-size="74" fill="#8a7d6a">×</text>')
    ds = 1 + 0.35 * pop
    s.append(f'<g transform="translate(36 6) scale({f(ds)})"><text x="0" y="46" text-anchor="middle" font-family="IDB" '
             f'font-size="140" fill="{INK}">{n}</text></g>')
    if circle > 0:
        pts = []
        N = 40
        m = max(2, int(N * 1.12 * circle))
        for i in range(m):
            a = -1.9 + 2 * math.pi * i / N
            rr = 1 + 0.06 * math.sin(i * .7)
            pts.append((28 + math.cos(a) * 92 * rr, -2 + math.sin(a) * 102 * rr))
        s.append(line(pts, 11, "#d62f2f", taper=.35, wmin=.4, seed=sd + 9))
    return f'<g transform="translate({f(x)} {f(y)}) rotate(-4) scale({f(sc)})">{"".join(s)}</g>'


# ───────────────────────── общие кадры у тумбочки
def table_scene(t, light, clock_svg, extra_back="", extra_front="", bed=True):
    s = [room_bg(light)]
    if bed:
        s.append(bed_edge(light))
    s.append(nightstand(light))
    s.append(extra_back)
    s.append(clock_svg)
    s.append(extra_front)
    if bed:
        s.append(plaid_layer(light))
    return "".join(s)


def ring_fx(t, cx, cy, size, amp, sd=0, color=INK):
    return AL.ring_marks(cx, cy, size, t, amp, color, seed=sd)


def hop_series(t, t0, period=0.17, amp=22):
    e = t - t0
    if e < 0:
        return 0.0
    ph = (e % period) / period
    return -amp * 4 * ph * (1 - ph)


# ───────────────────────── s01
def s01(t):
    light = 0.18 + 0.05 * t
    # прыжки на звоне + большой на «будильник»
    hop = hop_series(t, -0.05, 0.16, 18)
    big = 0.0
    tilt = 4.0 * math.sin(t * 2 * math.pi * 3.1)
    e = t - (T_BUD - 0.04)
    if 0 <= e <= 0.36:
        u = e / 0.36
        big = -150 * 4 * u * (1 - u)
        tilt += -9 * math.sin(math.pi * u)
        hop = 0.0
    land = t - (T_BUD + 0.32)
    sq = 1.0
    if 0 <= land < 0.3:
        sq = 1 - 0.14 * math.exp(-land * 14) * math.cos(land * 40)
    elif -0.36 <= e < 0:
        sq = 1 - 0.1 * smooth(-0.36, -0.02, e)          # присел перед прыжком
    cx, cy = CLK[0], CLK[1] + hop + big
    clk = AL.alarm(cx, cy, CSZ, 7, 0, ring=1.0, t=t, squash=sq, rot=tilt, uid="m")
    sh_k = clamp(1 + (hop + big) / 300, .4, 1)
    shadow = AL.shadow(cx, FOOT + 4, CSZ * sh_k, .32 * sh_k)
    fx = ring_fx(t, cx, cy, CSZ, 1.0, 400)
    fx += impact(cx, FOOT, land, 410, r0=150, n=7, L=60, w=8) if land >= 0 else ""
    art = table_scene(t, light, clk, shadow, fx)
    # влёт: масштаб 1/1.4 → 1 за 0.22 с с перелётом 5 %, поворот 3° → 0
    u = clamp(t / 0.22)
    if t < 0.22:
        z = 1 / 1.4 + (1 - 1 / 1.4) * ease_out(u, 3) * 1.05
        r = 3.0 * (1 - ease_out(u, 2)) - 0.6 * ease_out(u, 2)
    else:
        e2 = t - 0.22
        z = 1 + 0.05 * math.exp(-e2 * 12) * math.cos(e2 * 22)
        r = -0.6 * math.exp(-e2 * 10)
    hit = 0.07 * math.exp(-max(t - T_BUD, 0) * 7) * (t >= T_BUD)
    shx = 7 * math.sin(t * 61) + 4 * math.sin(t * 97)
    shy = 6 * math.sin(t * 73 + 1)
    base = 1.32 + 0.06 * t
    cm = cam(CLK[0] + 10 + shx, 800 + shy, base * (z + hit), r)
    return art, cm


# ───────────────────────── s03
def s03(t):
    a = 1.92
    stop = T_NINE
    # минуты: 0 → 120 с разгоном до упора, щелчок на «девять» с откатом
    if t < stop:
        u = clamp((t - a) / (stop - a))
        m = 120 * (0.15 * u + 0.85 * u ** 2.2)
    else:
        e = t - stop
        m = 120 + 4 * math.exp(-e * 9) * math.sin(e * 46)
    light = clamp(0.2 + 0.75 * smooth(a, stop, t))
    e = t - stop
    jolt_y = -40 * math.exp(-max(e, 0) * 11) * abs(math.sin(max(e, 0) * 24)) if e >= 0 else 0.0
    sq = 1 - 0.12 * math.exp(-max(e, 0) * 12) * (e >= 0)
    rot = 1.6 * math.sin(t * 50) * (1 - smooth(stop - 0.1, stop, t)) + (-3 * math.exp(-e * 8) if e >= 0 else 0)
    cx, cy = CLK[0], CLK[1] + jolt_y
    clk = AL.alarm(cx, cy, CSZ, 7, m, ring=0.0, t=t, squash=sq, rot=rot, uid="m")
    # дуги скорости вокруг циферблата, пока крутится
    fx = ""
    spin = 1 - smooth(stop - 0.12, stop, t)
    if spin > 0.02:
        k = CSZ / 200
        ma = math.radians((m % 60) * 6)
        for j in range(3):
            r = (70 + 30 * j) * k
            pts = [(cx + math.sin(ma - d) * r, cy - math.cos(ma - d) * r) for d in np.linspace(0, 0.9 + 0.3 * j, 9)]
            fx += line(pts, 7 * spin * k, "#9a8a70", taper=.8, wmin=.1, seed=500 + j)
    if e >= 0:
        fx += impact(cx, cy - 1.42 * CSZ + 30, e, 510, r0=60, n=9, L=80, w=10)
    shadow = AL.shadow(cx, FOOT + 4, CSZ, .3)
    art = table_scene(t, light, clk, shadow, fx)
    u = clamp((t - a) / 2.04)
    push = 0.10 * ease_out(clamp(e / 0.08), 2) * math.exp(-max(e - 0.08, 0) * 3) if e >= 0 else 0.0
    shx = (5 * math.sin(t * 71)) * (1 - smooth(stop, stop + 0.4, t)) + 9 * math.exp(-max(e, 0) * 10) * math.sin(max(e, 0) * 60) * (e >= 0)
    cm = cam(CLK[0] - 20 + shx, 820 - 20 * u, 1.42 + 0.10 * ease_io(u) + push, -1.0 + 1.6 * u)
    return art, cm


# ───────────────────────── хлопок рукой (s04, s05, s06)
PLAID_EXIT = (1010, 1010)
TOPY = CLK[1] - 1.36 * CSZ        # верх чашек


def hand_pose(t, slaps, t_in, t_out, rest=(980, 760), dsq=0.0):
    """Возвращает (запястье, контроль, угол кисти, spread, ударная фаза e после последнего хлопка, номер хлопка).
    slaps — моменты касания; до первого рука выходит из-под пледа и замахивается; после последнего лежит и уходит."""
    over = (CLK[0] + 160, TOPY - 50 + dsq)   # запястье при касании (ладонь на верхушке, с учётом сплющивания)
    high = (CLK[0] + 210, TOPY - 330)        # замах
    hide = PLAID_EXIT[0] + 60, PLAID_EXIT[1] + 60
    # уходит под плед
    k_in = ease_out(clamp((t - t_in) / 0.22), 2)
    prev = [s for s in slaps if s <= t]
    nxt = [s for s in slaps if s > t]
    idx = len(prev)
    if not prev:
        # выход и замах: hide → rest → high к моменту slaps[0] − 0.07, потом падение
        t1 = slaps[0] - 0.07
        if t < t1:
            u = clamp((t - t_in) / max(t1 - t_in, 1e-3))
            if u < 0.55:
                v = ease_out(u / 0.55, 2)
                w = (hide[0] + (rest[0] - hide[0]) * v, hide[1] + (rest[1] - hide[1]) * v)
            else:
                v = ease_io((u - 0.55) / 0.45)
                w = (rest[0] + (high[0] - rest[0]) * v, rest[1] + (high[1] - rest[1]) * v)
            w = (w[0], w[1] + 6 * math.sin(t * 13))
            return w, -14 * k_in - 10 * (u > .55), 0.4, None, 0
        u = ease_in(clamp((t - t1) / 0.07), 2)
        w = (high[0] + (over[0] - high[0]) * u, high[1] + (over[1] - high[1]) * u)
        return w, -10 + 10 * u, 0.4 * (1 - u), None, 0
    last = prev[-1]
    e = t - last
    if nxt:
        # серия: вверх и снова вниз до следующего касания
        T = nxt[0] - last
        u = clamp(e / T)
        lift = 4 * u * (1 - u) if u < 0.75 else 0
        rise = math.sin(math.pi * clamp(u / 0.8)) if u < 0.8 else 0
        down = ease_in(clamp((u - 0.62) / 0.38), 2)
        hh = 220 * (rise if u < 0.62 else (1 - down) * math.sin(math.pi * 0.62 / 0.8))
        w = (over[0] + 26 * rise, over[1] - hh)
        return w, -6 * rise, 0.2 * rise, e, idx
    # последний: лежит, потом уползает под плед
    if t < t_out:
        sink = 10 * math.exp(-e * 16)
        return (over[0], over[1] + sink - 6 * (1 - math.exp(-e * 3))), 0.0, 0.0, e, idx
    u = clamp((t - t_out) / 0.45)
    ux, uy = ease_out(clamp(u / 0.7), 2), ease_in(u, 2)
    w = (over[0] + (hide[0] - over[0]) * ux, over[1] + (hide[1] - over[1]) * uy - 70 * math.sin(math.pi * ux))
    return w, 8 * u, 0.0, e, idx


def arm_svg(w, rot, spread, sd=600):
    ctrl = (w[0] + 230, w[1] + 120 + 0.35 * (PLAID_EXIT[1] - w[1]))
    return arm(PLAID_EXIT, w, ctrl, rot, 1.25, sd, spread)


def slap_scene(t, slaps, t_in, t_out, ring_on, ring_off_at, n0=0, light=0.9, big=None):
    w, hrot, spread, e, idx = hand_pose(t, slaps, t_in, t_out)
    # будильник: звенит до первого касания после ring_on; удар — сплющивает
    ring = 0.0
    if ring_on <= t < ring_off_at:
        ring = smooth(ring_on, ring_on + 0.05, t)
    sq, press = 1.0, 0.0
    hop = 0.0
    if ring > 0:
        hop = hop_series(t, ring_on, 0.16, 14)
    flat_k = 0.0
    if e is not None:
        press = math.exp(-max(e - 0.1, 0) * 8)
        sq = 1 - 0.2 * math.exp(-e * 10) * math.cos(e * 30)
    if big is not None and t >= big:
        eb = t - big
        flat_k = 1 - 0.4 * math.exp(-eb * 18)
        sq = 0.55 + 0.06 * math.exp(-eb * 7) * math.cos(eb * 26)
    if e is not None:
        w, hrot, spread, e, idx = hand_pose(t, slaps, t_in, t_out, dsq=(FOOT - TOPY) * (1 - sq))
    cx, cy = CLK[0], CLK[1] + hop
    tilt = 2.5 * math.sin(t * 2 * math.pi * 3.3) * ring
    clk = AL.alarm(cx, cy, CSZ, 7, 5.0 * min(n0 + idx, 9), ring=ring, t=t, press=press, squash=sq, rot=tilt, uid="m")
    shadow = AL.shadow(cx, FOOT + 4, CSZ * (1 + 0.3 * (1 - sq)), .32)
    fx = ring_fx(t, cx, cy, CSZ, ring, 700) if ring > 0.05 else ""
    front = ""
    if e is not None:
        front += impact(CLK[0] - 60, TOPY + 10, e, 720 + idx, r0=170, n=6, L=70, w=10, span=0.55)
    # линии скорости при падении руки
    for s_ in slaps:
        d = s_ - t
        if 0 < d < 0.08:
            front += speed_lines(w[0] - 110, w[1] - 70, 3, 110, 740)
    a_s = arm_svg(w, hrot, spread)
    art = table_scene(t, light, clk, shadow, fx + a_s + front)
    return art, e, idx, w


def plus5(t, t_hit, x=255, y=420, sd=760):
    e = t - t_hit - 0.03
    if e < 0:
        return ""
    sc = back_out(clamp(e / 0.2), 2.4) * (1 - ease_in(clamp((e - 0.75) / 0.18), 2))
    return label(x, y - 40 * ease_out(clamp(e / 0.9)), "+5 мин", sc * 1.15, sd)


def s04(t):
    art, e, idx, w = slap_scene(t, [T_FIVE1], 3.56, 4.72, -1, T_FIVE1)
    art += plus5(t, T_FIVE1)
    hit = 0.07 * math.exp(-max(t - T_FIVE1, 0) * 9) * (t >= T_FIVE1)
    shk = 8 * math.exp(-max(t - T_FIVE1, 0) * 12) * math.sin(max(t - T_FIVE1, 0) * 70) * (t >= T_FIVE1)
    u = clamp((t - 3.56) / 1.68)
    cm = cam(600 + shk, 760 - 10 * u, 0.98 + 0.03 * u + hit, 0.5 - 0.6 * u)
    return art, cm, ""


def s05(t):
    ring_on = 4.88
    art, e, idx, w = slap_scene(t, [T_FIVE2], 4.92, 6.22, ring_on, T_FIVE2, n0=1)
    art += plus5(t, T_FIVE2, 270, 430, 770)
    hit = 0.08 * math.exp(-max(t - T_FIVE2, 0) * 9) * (t >= T_FIVE2)
    shk = 9 * math.exp(-max(t - T_FIVE2, 0) * 12) * math.sin(max(t - T_FIVE2, 0) * 70) * (t >= T_FIVE2)
    shk += 3 * math.sin(t * 57) * (ring_on <= t < T_FIVE2)
    u = clamp((t - 4.84) / 1.96)
    cm = cam(590 + shk, 770, 1.02 - 0.03 * u + hit, -0.4 + 0.8 * u)
    n = 2 if t >= T_FIVE2 else 1
    pop = math.exp(-max(t - T_FIVE2, 0) * 8) * (t >= T_FIVE2)
    ui = counter(880, 420, n, 0.9 + 0.08 * pop, 780, pop=pop)
    return art, cm, ui


S06_SLAPS = [6.42, 6.52, 6.60, 6.68, 6.78, 6.88, 6.96, T_RAZ]


def s06(t):
    art, e, idx, w = slap_scene(t, S06_SLAPS, 6.30, 7.62, 6.36, S06_SLAPS[-1] + 0.01, n0=2, big=T_RAZ)
    # счётчик 3 → 9 к «девять»
    if t < 6.42:
        n = 3
    elif t < T_NINE2:
        n = 3 + int(6 * (t - 6.42) / (T_NINE2 - 6.42))
        n = min(n, 8)
    else:
        n = 9
    tick = (t * 25) % 1
    e9 = t - T_NINE2
    pop = math.exp(-max(e9, 0) * 6) * (e9 >= 0)
    circ = ease_out(clamp(e9 / 0.3), 2) if e9 >= 0 else 0
    big9 = 1.0 + 0.35 * ease_out(clamp(e9 / 0.15), 2) if e9 >= 0 else 0.9 + 0.05 * tick
    ui = counter(860, 440, n, big9, 790, circle=circ, pop=pop)
    # звёздочки над сплющенным будильником после «раз»
    er = t - T_RAZ
    stars = ""
    if er >= 0:
        k = back_out(clamp(er / 0.2), 2)
        for j in range(5):
            a = er * 5.5 + j * 2 * math.pi / 5
            sx = CLK[0] + math.cos(a) * 190 * k
            sy = CLK[1] - 150 + math.sin(a) * 42 * k
            stars += star(sx, sy, 34 * k * (0.85 + 0.15 * math.sin(a)), er * 220 + j * 40, sd=800 + j)
    art += stars
    dz = 0.06 * ease_out(clamp((t - 6.4) / 1.4), 2)
    hit = 0.08 * math.exp(-max(er, 0) * 8) * (er >= 0)
    shk = 7 * math.sin(t * 83) * (t < T_RAZ + 0.05) + 12 * math.exp(-max(er, 0) * 10) * math.sin(max(er, 0) * 66) * (er >= 0)
    shy = 5 * math.sin(t * 67 + 2) * (t < T_RAZ)
    cm = cam(590 + shk, 790 + shy, 1.0 + dz + hit, 0.6 * math.sin(t * 9))
    return art, cm, ui


# ───────────────────────── s09: угол комнаты у пола, плед накрывает
CX9, CY9, SZ9 = 560.0, 1010.0, 190.0
FL9 = CY9 + AL.FOOT_Y / 200 * SZ9       # пол под ножками


def corner_bg():
    s = []
    lw = "#8f9cb4"
    rw = "#a7b3c6"
    cxw = 560
    floor_y = 1180
    # стены угла: левая темнее, правая светлее; угол — вертикаль
    s.append(f'<rect x="-900" y="-900" width="{cxw + 900}" height="2800" fill="{lw}"/>')
    s.append(f'<rect x="{cxw}" y="-900" width="1500" height="2800" fill="{rw}"/>')
    for k in range(-10, 8):
        x = cxw - 40 - k * -90 if False else cxw - 70 - k * 110
        if x < cxw:
            s.append(f'<rect x="{x}" y="-900" width="20" height="2800" fill="#7d8aa4" opacity=".5"/>')
    for k in range(0, 10):
        x = cxw + 60 + k * 120
        s.append(f'<rect x="{x}" y="-900" width="22" height="2800" fill="#96a3b8" opacity=".5"/>')
    s.append(line([(cxw, -900), (cxw, floor_y - 60)], 6, "#5f6a84", taper=0, wmin=1, seed=901))
    # плинтус: две полосы к углу (перспектива — пол уходит вглубь к углу)
    s.append(shape([(-900, floor_y + 120, 1), (cxw, floor_y - 60, 1), (cxw, floor_y - 20, 1), (-900, floor_y + 170, 1)], "#efe8da",
                   "", w=4.6, seed=902))
    s.append(shape([(cxw, floor_y - 60, 1), (2000, floor_y + 160, 1), (2000, floor_y + 210, 1), (cxw, floor_y - 20, 1)], "#f7f1e5",
                   "", w=4.6, seed=903))
    # пол: доски, сходящиеся к углу
    fl = [(-900, floor_y + 170, 1), (cxw, floor_y - 20, 1), (2000, floor_y + 210, 1), (2000, 2900, 1), (-900, 2900, 1)]
    inner = ""
    for k in range(-12, 13):
        x1 = cxw + k * 260
        inner += line([(cxw + k * 22, floor_y - 10), (x1, 2900)], 3.4, "#7c5233", taper=0, wmin=1, seed=910 + k, op=.8)
    inner += blob([(cxw - 400, 2900), (cxw + 120, floor_y + 40), (cxw + 520, floor_y + 80), (cxw + 900, 2900)], "#f3c98e", .35)
    s.append(shape(fl, WOOD, inner, w=5, seed=904))
    return "".join(s)


def blanket_pts(u, t):
    """Плед: u=0 — полотно сверху (широкое, волнистое), u=1 — накрыл будильник бугром. Одинаковое число точек."""
    N = 26
    flat = []
    top_y = -380 + (FL9 - 300 + 380) * 0
    for i in range(N):
        a = i / (N - 1)
        x = CX9 - 520 + 1040 * a
        flat.append((x, 0))
    mound = []
    for i in range(N):
        a = i / (N - 1)
        x = CX9 - 495 + 950 * a
        # колокол: верх над будильником
        h = 1.0 / (1 + ((a - 0.5) / 0.25) ** 4)
        y = FL9 + 6 - (2.62 * SZ9 + 36) * h - 18 * math.sin(a * 9.4) * h
        mound.append((x, y))
    return flat, mound


def blanket(t, ring):
    """Плед падает сверху полотном (верхний край волной, низ свисает), цепляется серединой за будильник, края
    доходят до пола — и уже бугор (те же точки, без скачка формы). После «одеялом» бугор трясётся."""
    e = t - T_BLANKET
    fall0 = T_BLANKET - 0.36
    if t < fall0:
        return ""
    _, mound = blanket_pts(0, t)
    N = len(mound)
    floor = [(CX9 + 540 - 1080 * i / (N - 1), FL9 + 34 + 26 * math.sin(math.pi * i / (N - 1)) + 6 * math.sin(i * 1.7)) for i in range(N)]
    if e < 0:
        u = clamp((t - fall0) / 0.36)
        y0 = -560 + (FL9 + 60 + 560) * ease_in(u, 1.7)
        top, bot = [], []
        for i, (mx, my) in enumerate(mound):
            a = i / (N - 1)
            x = CX9 + (mx - CX9) * (1.12 - 0.12 * u) + 10 * math.sin(t * 20 + i) * (1 - u)
            flut = 24 * math.sin(a * 11 + t * 30) * (1 - u)
            sag = -50 * (1 - 4 * (a - .5) ** 2) * (1 - u)
            ty = min(y0 + sag + flut, my)
            top.append((x, ty))
            fy = floor[N - 1 - i][1]
            by = min(ty + 300 + 420 * u ** 2 + 26 * math.sin(i * .8 + t * 21), fy)
            bot.append((x + 12 * math.sin(i + t * 25) * (1 - u), by))
        pts = top + bot[::-1]
        pid = plaid_pattern("pBl", f"translate({f(CX9)} {f(y0)}) rotate(-12)")
    else:
        k = ease_out(clamp(e / 0.12), 2)
        sh = ring * (5 * math.sin(t * 2 * math.pi * 19) + 3 * math.sin(t * 2 * math.pi * 31))
        top = []
        for i, (x, y) in enumerate(mound):
            a = i / (N - 1)
            hmask = 1.0 / (1 + ((a - 0.5) / 0.26) ** 4)
            settle = -18 * (1 - k) * hmask * math.cos(e * 40)
            top.append((x + sh * hmask, y + settle + 4 * math.sin(t * 40 + i) * ring * hmask))
        pts = top + floor
        pid = plaid_pattern("pBl", f"translate({f(CX9 + sh * .5)} {f(FL9 + 60)}) rotate(-12)")
    s = []
    inner = f'<rect x="-600" y="-900" width="2400" height="3400" fill="url(#{pid})"/>'
    inner += blob([(CX9 + 120, -900), (CX9 + 700, -900), (CX9 + 700, 2400), (CX9 + 60, 2400)], "#1d2f22", .3)
    if e >= 0:
        inner += line([(CX9 - 130, FL9 - 2.0 * SZ9), (CX9 - 220, FL9 - 40), (CX9 - 270, FL9 + 30)], 4.5, "#1f3324", seed=951, op=.8)
        inner += line([(CX9 + 130, FL9 - 1.9 * SZ9), (CX9 + 240, FL9 - 30), (CX9 + 310, FL9 + 30)], 4.5, "#1f3324", seed=952, op=.8)
        inner += line([(CX9 - 20, FL9 - 2.4 * SZ9), (CX9 + 14, FL9 - 1.2 * SZ9)], 4, "#1f3324", seed=953, op=.6)
    s.append(shape(pts, PLAID, inner, w=6, seed=950))
    # бахрома по краю
    return "".join(s)


def s09(t):
    e = t - T_BLANKET
    ring = 1.0 if e < 0 else 0.85
    cx, cy = CX9, CY9 + hop_series(t, 10.6, 0.16, 16) * (e < 0)
    tilt = -3 + 3 * math.sin(t * 2 * math.pi * 3.2)
    s = [corner_bg()]
    s.append(AL.shadow(cx, FL9 + 4, SZ9, .3))
    if e < -0.075:
        s.append(AL.alarm(cx, cy, SZ9, 7, 25, ring=ring, t=t, rot=tilt, uid="m"))
        s.append(ring_fx(t, cx, cy, SZ9, 1.0, 960))
    s.append(blanket(t, ring))
    if e >= 0:
        # приглушённые штрихи звона — серые, короче, над бугром
        s.append(AL.ring_marks(cx, FL9 - 2.62 * SZ9 + 150, SZ9 * 0.9, t, 0.7, "#5b6070", seed=970))
        s.append(impact(cx, FL9 - 10, e, 980, r0=420, n=7, L=60, w=8))
    # пыль на приземлении
    if 0 <= e < 0.5:
        for j in range(8):
            side = -1 if j % 2 else 1
            r = 520 + 140 * ease_out(e / .5) + j * 6
            px = cx + side * r
            py = FL9 + 20 - 50 * math.sin(math.pi * clamp(e / .5)) * (0.5 + 0.1 * j)
            rr = 22 * (1 - e / .5) + 4
            s.append(shape(E(px, py, rr, rr * .8, 10, rot=j * 30), "#e9dcc5", "", w=2.4, seed=990 + j))
    u = clamp((t - 10.68) / 1.64)
    hit = 0.07 * math.exp(-max(e, 0) * 8) * (e >= 0)
    shk = 11 * math.exp(-max(e, 0) * 9) * math.sin(max(e, 0) * 64) * (e >= 0) + 3 * math.sin(t * 61) * (e < 0)
    cm = cam(cx + shk, 960 - 30 * u, 1.05 + 0.12 * ease_io(u) + hit, 1.2 - 1.6 * u)
    return "".join(s), cm, ""


_ST = {}


def frame(sid, t):
    lib.dyn_begin()
    r = {"s01": s01, "s03": s03, "s04": s04, "s05": s05, "s06": s06, "s09": s09}[sid](t)
    art, cm = r[0], r[1]
    ui = r[2] if len(r) > 2 else ""
    return svg(f'<rect width="{W}" height="{H}" fill="#3b4258"/><g transform="{cm}">{art}</g>{ui}')
