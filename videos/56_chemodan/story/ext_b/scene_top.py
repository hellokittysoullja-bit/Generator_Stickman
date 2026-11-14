"""Рилс 56 s03 (3.17–5.28) и s05 (7.9–10.47): чемодан сверху.
s03 — раскрытый чемодан сверху-спереди крупно: Дима слева (голова и рука крупно), свитер из руки летит на «положил» (3.33), пружинит,
рука поправляет рукав на «свитер» (4.64). s05 — вид строго сверху: куча свитеров, зонт 8.56, фен 9.12, сковородка 9.68 падают
(рисунок крупнее к камере в полёте), чемодан каждый раз приседает и отскакивает."""
import math

import numpy as np

import dima
import lib
import props
from lib import INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg
from props import LINING, LINING_D, TEAL, TEAL_D, TEAL_L, place

SEED = 5000


def rounded_poly(pts, r):
    out = []
    n = len(pts)
    for i in range(n):
        v = np.array(pts[i], float)
        a = np.array(pts[i - 1], float)
        b = np.array(pts[(i + 1) % n], float)
        da, db = a - v, b - v
        la, lb = np.linalg.norm(da), np.linalg.norm(db)
        p1 = v + da / la * min(r, la / 2.2)
        p2 = v + db / lb * min(r, lb / 2.2)
        q = v + ((p1 + p2) / 2 - v) * 0.42
        out += [(p1[0], p1[1], 1), (q[0], q[1]), (p2[0], p2[1], 1)]
    return out


def floor_bg(light=(300, 300)):
    s = []
    g = lin_grad([(0, "#d9b27f", 1), (1, "#b58852", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-1500" y="-1500" width="4200" height="5200" fill="url(#{g})"/>')
    for k in range(-26, 40):
        y = k * 132
        s.append(line([(-1500, y), (2600, y + 8)], 3.0, "#8c6238", taper=.05, wmin=.9, seed=SEED + k % 20, op=.55))
        for j in range(-6, 8):
            x = j * 420 + (k % 3) * 140 + (k % 2) * 90
            s.append(line([(x, y), (x + 3, y + 132)], 2.4, "#8c6238", taper=.05, wmin=.9, seed=SEED + 40 + (k + j) % 30, op=.45))
    gl = rad_grad([(0, "#fff0c8", .55), (1, "#fff0c8", 0)], light[0], light[1], 900, 760)
    s.append(f'<rect x="-1500" y="-1500" width="4200" height="5200" fill="url(#{gl})" style="mix-blend-mode:screen"/>')
    return "".join(s)


# ═════════════════════════ раскрытый чемодан сверху-спереди (s03) ═════════════════════════
CX3 = 600


def open_case_front(t):
    s = []
    cx = CX3
    # крышка — стоит позади, внутренней стороной к нам
    lid = rounded_poly([(cx - 335, 320), (cx + 335, 320), (cx + 362, 820), (cx - 362, 820)], 44)
    s.append(shape(lid, TEAL, blob(rect_pts(cx - 400, 780, cx + 400, 830), TEAL_D, .5), w=6.0, seed=SEED + 100))
    li = rounded_poly([(cx - 296, 364), (cx + 296, 364), (cx + 322, 790), (cx - 322, 790)], 26)
    g = lin_grad([(0, LINING, 1), (1, LINING_D, 1)], 0, 0, 0, 1)
    inner = ""
    # сетчатый карман с молнией
    inner += shape(rounded_poly([(cx - 250, 430), (cx + 250, 430), (cx + 262, 640), (cx - 262, 640)], 18), "#e6d6b4",
                   "".join(line([(cx - 250 + k * 36, 436), (cx - 262 + k * 36 + 40, 636)], 1.8, "#c9b68a", seed=SEED + 110 + k, op=.7) for k in range(14)) +
                   line([(cx - 250, 434), (cx + 250, 434)], 4, "#8f805c", seed=SEED + 130), w=3.6, seed=SEED + 131)
    inner += shape(rect_pts(cx - 250, 424, cx + 250, 446, 8), "#bfae84", "", w=3.2, seed=SEED + 132)   # молния кармана
    # эластичные ремни
    for k, y in enumerate((690, 748)):
        inner += blob(rect_pts(cx - 306, y, cx + 306, y + 20, 4), "#8f805c", .95) + line([(cx - 300, y + 2), (cx + 300, y + 2)], 2, "#5f5238", seed=SEED + 140 + k, op=.7)
    inner += blob(rect_pts(cx - 14, 680, cx + 14, 770, 4), "#c9ced8", .95)
    s.append(shape(li, f"url(#{g})", inner, w=4.0, seed=SEED + 150))
    # основание: трапеция
    outer = rounded_poly([(cx - 352, 800), (cx + 352, 800), (cx + 420, 1290), (cx - 420, 1290)], 40)
    s.append(shape(outer, TEAL, "", w=6.0, seed=SEED + 160))
    inl = rounded_poly([(cx - 322, 822), (cx + 322, 822), (cx + 384, 1252), (cx - 384, 1252)], 26)
    g2 = lin_grad([(0, LINING_D, 1), (.3, LINING, 1), (1, "#f6ecd4", 1)], 0, 0, 0, 1)
    inn2 = blob([(cx - 330, 822), (cx + 330, 822), (cx + 350, 900), (cx - 350, 900)], "#b9a678", .45)         # тень от петель крышки
    inn2 += line([(cx - 330, 826), (cx + 330, 826)], 5, "#8f805c", seed=SEED + 161, op=.8)
    inn2 += "".join(line([(cx - 300 + k * 60, 870), (cx - 340 + k * 68, 1240)], 1.8, "#dcccA0".lower(), seed=SEED + 170 + k, op=.55) for k in range(11))
    # ремень поперёк
    inn2 += blob([(cx - 360, 1160), (cx + 360, 1160), (cx + 372, 1190), (cx - 372, 1190)], "#8f805c", .95)
    inn2 += blob(rect_pts(cx - 16, 1150, cx + 16, 1200, 4), "#c9ced8", .95)
    s.append(shape(inl, f"url(#{g2})", inn2, w=4.0, seed=SEED + 180))
    # передний борт и уголки
    s.append(shape(rounded_poly([(cx - 420, 1290), (cx + 420, 1290), (cx + 424, 1360), (cx - 424, 1360)], 26), TEAL_D,
                   line([(cx - 400, 1302), (cx + 400, 1302)], 4, TEAL_L, seed=SEED + 190, op=.8), w=5.6, seed=SEED + 191))
    for sx in (-1, 1):
        s.append(shape(rounded_poly([(cx + sx * 380, 1282), (cx + sx * 438, 1282), (cx + sx * 440, 1372), (cx + sx * 384, 1372)], 14), "#33505c", "", w=4.4, seed=SEED + 195 + sx))
    return "".join(s)


def sweater_world(x, y, rot, sx, sy, col, sd, sl_l, sl_r, sq=(1, 1)):
    return place(props.sweater(col, sd, sl_l, sl_r), x, y, rot, sx * sq[0], sy * sq[1])


def cuff_local(side, ang):
    a = math.radians(ang)
    return (side * 66 + math.sin(a) * 128, -58 + math.cos(a) * 128)


def to_world(p, x, y, rot, sx, sy):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return (x + (p[0] * sx) * c - (p[1] * sy) * s, y + (p[0] * sx) * s + (p[1] * sy) * c)


T_THROW, T_LAND, T_TUG = 3.33, 3.64, 4.64
LAND = (690, 1030)
SCALE_S = 1.32
SWEATER_COL = "#c9503c"


def lerp(a, b, u):
    return a + (b - a) * u


def s03_state(t):
    """Положение свитера: в руке → полёт → приземление → пружина. Возвращает (x, y, rot, sx, sy, sl_l, sl_r)."""
    # в руке: висит за манжету левого рукава
    if t < T_THROW:
        hx, hy = hand_target(t)
        sw = math.sin(t * 7.0) * 6
        return hx + 30, hy + 120, 12 + sw * 1.4, SCALE_S * 1.15, SCALE_S * 1.15, -18 + sw * 2, 24 - sw * 2
    if t < T_LAND:
        u = (t - T_THROW) / (T_LAND - T_THROW)
        h0 = hand_target(T_THROW)
        x0, y0 = h0[0] + 30, h0[1] + 120
        x = lerp(x0, LAND[0], ease_out(u, 1.6))
        y = lerp(y0, LAND[1], u) - 300 * 4 * u * (1 - u)
        rot = lerp(12, 360 + 8, ease_io(u))
        sc = lerp(1.15, 1.0, u) * SCALE_S
        return x, y, rot, sc, sc * lerp(1.0, 0.8, u), -30 + 40 * math.sin(u * 9), 36 - 30 * math.sin(u * 8)
    e = t - T_LAND
    # первый подскок 0.30 с, второй 0.2 с
    if e < 0.30:
        w = e / 0.30
        hop = 130 * 4 * w * (1 - w)
    elif e < 0.52:
        w = (e - 0.30) / 0.22
        hop = 40 * 4 * w * (1 - w)
    else:
        hop = 0
    sqz = 0
    for c0, k in ((0.0, 1.0), (0.30, 0.45), (0.52, 0.2)):
        if e >= c0:
            sqz += k * math.exp(-(e - c0) * 14) * math.cos((e - c0) * 30)
    sx = SCALE_S * (1 + 0.30 * sqz)
    sy = SCALE_S * 0.8 * (1 - 0.34 * sqz)
    # рукава болтаются и успокаиваются; левый остаётся задранным — его поправит рука
    wob = math.exp(-e * 5) * math.sin(e * 26)
    left_final = -140
    tug = smooth(T_TUG, T_TUG + 0.22, t)
    sl_l = lerp(left_final + 14 * wob, -22, tug) + (6 * math.exp(-(t - T_TUG - .22) * 9) * math.sin((t - T_TUG) * 40) if t > T_TUG + .22 else 0)
    sl_r = 30 - 12 * wob
    return LAND[0], LAND[1] - hop, 3 * wob, sx, sy, sl_l, sl_r


REST = (330, 1150)


def hand_target(t):
    """Где ближняя рука (запястье): держит свитер до броска, отдыхает, тянется за манжетой на 4.3–4.6, тянет, отпускает, уходит."""
    if t < T_THROW:
        u = clamp((t - 2.9) / 0.4)
        return (470 + 30 * math.sin(t * 5.5) + 10 * u, 880 - 35 * math.sin(t * 4.0) - 20 * u)
    if t < 4.28:
        u = ease_io((t - T_THROW) / 0.42)
        return (lerp(490, REST[0], u), lerp(860, REST[1], u))
    cuff = cuff_world(t)
    if t < 4.56:
        u = ease_out((t - 4.28) / 0.28, 2)
        return (lerp(REST[0], cuff[0], u), lerp(REST[1], cuff[1], u))
    if t < 4.95:
        return cuff
    u = ease_io((t - 4.95) / 0.38)
    return (lerp(cuff[0], REST[0], u), lerp(cuff[1], REST[1], u))


def cuff_world(t):
    x, y, rot, sx, sy, sl_l, sl_r = s03_state_cuffless(t)
    c = cuff_local(-1, sl_l)
    return to_world(c, x, y, rot, sx, sy)


def s03_state_cuffless(t):
    """Положение свитера после приземления (без обращения к руке)."""
    e = t - T_LAND
    wob = math.exp(-e * 5) * math.sin(e * 26)
    tug = smooth(T_TUG, T_TUG + 0.22, t)
    return LAND[0], LAND[1], 3 * wob, SCALE_S, SCALE_S * 0.8, lerp(-140 + 14 * wob, -22, tug), 30 - 12 * wob


def dima_pose(t):
    lean = 0.30 + 0.025 * math.sin(t * 2.3)
    nod = 0.0
    if t >= T_TUG:
        u = t - T_TUG
        nod = -0.20 * math.sin(clamp(u / 0.34) * math.pi) + 0.09 * math.sin(clamp((u - 0.34) / 0.3) * math.pi) * 1.0 if u < 0.7 else 0
    happy = t >= T_TUG - 0.05
    sw_t = ease_out(clamp((t - T_THROW) / 0.5))
    look = (0.4 + 0.5 * math.sin(t * 2.0) * 0.3, 0.55) if t < T_LAND else (0.5, 0.6)
    exp = {"lid": 0.55 + 0.25 * smooth(T_THROW, T_LAND, t), "look": look, "brows": "glad" if happy else ("up" if T_THROW <= t < T_TUG - 0.05 else "calm"),
           "mouth": "smirk" if happy else ("grin" if T_THROW <= t < T_THROW + 0.35 else "flat"), "hair": 3 * math.sin(t * 3.1) + (6 * math.exp(-(t - T_LAND) * 10) if t > T_LAND else 0)}
    tgt = hand_target(t)
    grip = 0.0
    if 4.5 <= t < 5.0:
        grip = smooth(4.5, 4.62, t) * (1 - smooth(4.84, 4.95, t))
    if t < T_THROW:
        grip = 1.0
    pose = {"hip": (-110, 1210), "lean": lean, "head_ang": 0.05 + nod + 0.03 * math.sin(t * 2.6),
            "feet": {"n": ((60, 1910), 0.0), "f": ((-90, 1910), 0.0)},
            "arms": {"n": ("ik", tgt), "f": ("ik", (330, 1000), -1)},
            "hands": {"n": ("open", 0.15 + 0.85 * grip) if t >= T_THROW else "fist", "f": "fist"},
            "expr": exp, "hood": 3 * math.sin(t * 3.0), "strings": (3 * math.sin(t * 3.1), 0)}
    return pose


def case_state(t):
    e = t - T_LAND
    k = math.exp(-max(e, 0) * 11) * math.cos(max(e, 0) * 32) if e > 0 else 0
    return 1 + 0.012 * k, 1 - 0.018 * k


def s03_frame(t):
    s = [floor_bg((540, 500))]
    sq = case_state(t)
    s.append(props.shadow(CX3 + 10, 1385, 470, 46, .45, 14))
    s.append(f'<g transform="translate({CX3} 1360) scale({sq[0]:.4f} {sq[1]:.4f}) translate({-CX3} -1360)">{open_case_front(t)}')
    x, y, rot, sx, sy, sl_l, sl_r = s03_state(t)
    if T_LAND <= t:
        s.append(props.shadow(x + 18, y + 40, 210, 70, .3, 12))
    s.append(sweater_world(x, y, rot, sx, sy, SWEATER_COL, 5200, sl_l, sl_r))
    if 0 < t - T_LAND < 0.5:
        k = (t - T_LAND) / 0.5
        s.append(props.dust(x, y + 70, k, 6, 240, 80, 5300))
        s.append(props.burst(x, y, k, 8, 150, 270, 9, "#fff4c2", 5310))
    s.append("</g>")
    dima.BS = 1.2
    dima.LWK = 1.3
    g, _ = dima.draw(dima_pose(t))
    s.append(g)
    # свитер в руке рисуем поверх кисти не нужно: рука держит за манжету — манжета под пальцами
    # камера: влёт нет (план 2D), с первого кадра ход и наклон; толчок на приземлении
    u = clamp((t - 2.97) / 2.5)
    sc = 1.0 + 0.10 * ease_io(u)
    ccx, ccy = lerp(560, 600, u), lerp(860, 960, u)
    rot = lerp(-2.6, 1.0, ease_io(u)) + 0.5 * math.sin(t * 2.4)
    e = t - T_LAND
    if e > 0:
        kk = math.exp(-e * 8)
        sc *= 1 + 0.045 * kk
        ccy += 16 * kk * math.sin(e * 38)
        rot += 1.6 * kk * math.sin(e * 24)
    e2 = t - T_TUG
    if e2 > 0:
        kk = math.exp(-e2 * 9)
        sc *= 1 + 0.025 * kk
        rot += -1.0 * kk * math.sin(e2 * 26)
    return svg(f'<rect width="{W}" height="{H}" fill="#b58852"/><g transform="{cam(ccx, ccy, sc, rot)}">{"".join(s)}</g>')


# ═════════════════════════ s05: вид строго сверху ═════════════════════════
CX5, HINGE = 540, 724
LAND_T = {"umb": 8.56, "dry": 9.12, "pan": 9.68}
FALL = 0.40


def flat_case(sq):
    """Чемодан раскрыт плашмя: верхняя половина — крышка (подкладка, сетка), нижняя — основание (в него складывают)."""
    cx = CX5
    s = []
    out = rounded_poly([(cx - 392, 140), (cx + 392, 140), (cx + 392, 1296), (cx - 392, 1296)], 54)
    s.append(shape(out, TEAL, blob(rect_pts(cx - 396, 1250, cx + 396, 1300), TEAL_D, .5), w=6.4, seed=SEED + 300))
    # крышка
    g = lin_grad([(0, LINING_D, 1), (1, LINING, 1)], 0, 0, 0, 1)
    top = rounded_poly([(cx - 352, 182), (cx + 352, 182), (cx + 352, HINGE - 14), (cx - 352, HINGE - 14)], 30)
    inner = shape(rounded_poly([(cx - 290, 250), (cx + 290, 250), (cx + 290, 500), (cx - 290, 500)], 20), "#e6d6b4",
                  "".join(line([(cx - 290 + k * 40, 256), (cx - 300 + k * 40 + 44, 496)], 1.8, "#c9b68a", seed=SEED + 310 + k, op=.7) for k in range(16)) +
                  line([(cx - 290, 256), (cx + 290, 256)], 4, "#8f805c", seed=SEED + 330), w=3.6, seed=SEED + 331)
    for k, y in enumerate((560, 620)):
        inner += blob(rect_pts(cx - 352, y, cx + 352, y + 22, 4), "#8f805c", .95)
    s.append(shape(top, f"url(#{g})", inner, w=4.2, seed=SEED + 335))
    # шарнир
    s.append(shape(rect_pts(cx - 396, HINGE - 14, cx + 396, HINGE + 16, 8), TEAL_D, "", w=4.4, seed=SEED + 336))
    # основание
    g2 = lin_grad([(0, LINING, 1), (1, "#f6ecd4", 1)], 0, 0, 0, 1)
    bot = rounded_poly([(cx - 352, HINGE + 16), (cx + 352, HINGE + 16), (cx + 352, 1254), (cx - 352, 1254)], 30)
    s.append(shape(bot, f"url(#{g2})", blob([(cx - 360, HINGE + 16), (cx + 360, HINGE + 16), (cx + 360, HINGE + 60), (cx - 360, HINGE + 60)], "#b9a678", .45), w=4.2, seed=SEED + 337))
    # замки по краям (зелёно-серые, видны сверху)
    for sx in (-1, 1):
        s.append(shape(rounded_poly([(cx + sx * 392, 1050), (cx + sx * 428, 1050), (cx + sx * 428, 1130), (cx + sx * 392, 1130)], 8), "#c9ced8", "", w=3.8, seed=SEED + 340 + sx))
    return "".join(s)


def pile(t, gr):
    """Куча свитеров в основании: пять слоёв, дышит и приседает вместе с чемоданом; gr — вздутие от приземлённых предметов."""
    s = []
    base = [(470, 1010, -14, 1.9, 0), (610, 990, 20, 1.85, 1), (540, 920, 4, 1.75, 2), (440, 930, 28, 1.6, 3), (640, 1090, -26, 1.7, 4)]
    for x, y, rot, sc, i in base:
        s.append(props.shadow(x + 14, y + 22, 170 * sc / 1.9, 70 * sc / 1.9, .35, 10))
        s.append(place(props.sweater(props.SWEATERS[i], 5400 + i * 100, -40 + 12 * math.sin(t * 2.0 + i), 38 - 10 * math.sin(t * 2.2 + i)), x, y + 0, rot, sc * gr, sc * gr))
    return "".join(s)


def impacts(t):
    """Сжатие чемодана: сумма затухающих пружин от трёх ударов + остаточное дрожание от предыдущих свитеров (s04) в начале клипа."""
    k = 0.0
    amp = {"umb": 0.45, "dry": 0.6, "pan": 1.0}
    for n, c in LAND_T.items():
        e = t - c
        if e > 0:
            k += amp[n] * math.exp(-e * 9) * math.cos(e * 26)
    e0 = t - 7.7
    k += 0.35 * math.exp(-max(e0, 0) * 7) * math.cos(max(e0, 0) * 24) if e0 >= 0 else 0
    return k


ITEMS = {
    "umb": dict(start=(930, -260), land=(560, 980), r0=80, r1=-24, s_land=1.38, fn=props.umbrella, shadow=(300, 40)),
    "dry": dict(start=(150, -280), land=(520, 1050), r0=-70, r1=16, s_land=1.2, fn=props.dryer, shadow=(220, 60)),
    "pan": dict(start=(840, -300), land=(560, 1030), r0=40, r1=-8, s_land=1.25, fn=props.pan, shadow=(180, 140)),
}


def fall_item(name, t, sd):
    it = ITEMS[name]
    tl = LAND_T[name]
    if t < tl - FALL:
        return "", False
    u = (t - (tl - FALL)) / FALL
    s = []
    if u < 1:
        p = ease_in(u, 2.0)
        x = lerp(it["start"][0], it["land"][0], ease_io(u) * 0.35 + 0.65 * u)
        y = lerp(it["start"][1], it["land"][1], p)
        rot = lerp(it["r0"], it["r1"], ease_out(u, 1.5))
        sc = it["s_land"] * lerp(1.9, 1.0, p)
        # тень растёт и темнеет на куче при приближении
        sx_, sy_ = it["shadow"]
        s.append(props.shadow(it["land"][0] + 14, it["land"][1] + 24, sx_ * (0.4 + .6 * p), sy_ * (0.4 + .6 * p), .1 + .3 * p, 14))
        s.append(place(it["fn"](sd), x, y, rot, sc))
        return "".join(s), False
    e = t - tl
    # посадка: короткое «вдавливание» предмета и лёгкий подскок
    bounce = 26 * math.exp(-e * 12) * abs(math.sin(e * 22))
    sc = it["s_land"] * (1 + 0.07 * math.exp(-e * 12) * math.cos(e * 30))
    rot = it["r1"] + 4 * math.exp(-e * 9) * math.sin(e * 30)
    x, y = it["land"]
    sx_, sy_ = it["shadow"]
    s.append(props.shadow(x + 14, y + 24, sx_, sy_, .38, 12))
    s.append(place(it["fn"](sd), x, y - bounce, rot, sc))
    return "".join(s), True


def s05_frame(t):
    k = impacts(t)
    sqz = 1 - 0.048 * k
    # вздутие кучи: каждый предмет раздвигает свитера
    gr = 1.0 + 0.03 * sum(1 for c in LAND_T.values() if t >= c) + 0.02 * k
    s = [floor_bg((540, 700))]
    s.append(props.shadow(CX5 + 18, 800, 470, 700, .5, 28))
    s.append(f'<g transform="translate({CX5} 720) scale({sqz:.4f}) translate({-CX5} -720)">{flat_case(k)}{pile(t, gr)}')
    for i, n in enumerate(("umb", "dry", "pan")):
        g, landed = fall_item(n, t, 5600 + i * 40)
        s.append(g)
    # эффекты удара
    for n, c in LAND_T.items():
        e = t - c
        if 0 < e < 0.5:
            x, y = ITEMS[n]["land"]
            kk = e / 0.5
            s.append(props.dust(x, y + 70, kk, 7, 260, 70, 5800, rmax=40))
            s.append(props.burst(x, y, kk, 11, 190, 340, 11, "#fff4c2", 5810 + int(c * 10)))
    s.append("</g>")
    # камера: сверху, наезд и накренённые удары
    u = clamp((t - 7.7) / 2.9)
    sc = lerp(1.04, 1.28, ease_io(u))
    ccx, ccy = lerp(540, 540, u), lerp(930, 1010, u)
    rot = lerp(3.5, -1.0, ease_io(u)) + 0.5 * math.sin(t * 2.5)
    for n, c in LAND_T.items():
        e = t - c
        if e > 0:
            kk = math.exp(-e * 8) * (1.0 if n == "pan" else 0.7)
            sc *= 1 + 0.05 * kk
            ccy += 20 * kk * math.sin(e * 40)
            rot += (-2.2 if n == "dry" else 2.2) * kk * math.sin(e * 26)
    return svg(f'<rect width="{W}" height="{H}" fill="#b58852"/><g transform="{cam(ccx, ccy, sc, rot)}">{"".join(s)}</g>')


def frame(sid, t):
    lib.dyn_begin()
    return s03_frame(t) if sid == "s03" else s05_frame(t)
