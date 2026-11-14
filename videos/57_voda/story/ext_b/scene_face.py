"""Рилс 57 группа B: s12 (21.5–23.8) крупно лицо Димы: проверяет себя, облизывает губы, кивает; на «жажды» (23.36) проявляется капля с галочкой штрихами; облегчение."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import dima  # noqa: E402
import fxprops as fp  # noqa: E402
import lib  # noqa: E402
import props  # noqa: E402
from lib import INK, W, H, band, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, mix, rad_grad, rect_pts, shape, smooth, spring, svg  # noqa: E402

SEED = 11000
T0 = 21.3
T_LICK = (22.18, 22.78)
T_NOD = (22.86, 23.3)
T_ICON = 23.36
HS = 2.9                 # масштаб головы (L-единицы → мир)
HO = (500, 760)          # точка «центр лица» в мире


def lerp(a, b, u):
    return a + (b - a) * u


def background(t):
    s = []
    g = lin_grad([(0, "#fbe9d2", 1), (1, "#f1cfa4", 1)], 0, 0, 0, 1)
    s.append(f'<rect x="-600" y="-600" width="2300" height="3200" fill="url(#{g})"/>')
    for x in range(-600, 1700, 170):
        s.append(f'<rect x="{x}" y="-600" width="70" height="3200" fill="#f6dcba"/>')
    # большое светлое окно света сзади и плавающие пузырьки воды (сплошные)
    gl = rad_grad([(0, "#fffbe8", .85), (1, "#fffbe8", 0)], 760, 380, 640, 560)
    s.append(f'<rect x="-600" y="-600" width="2300" height="3200" fill="url(#{gl})" style="mix-blend-mode:screen"/>')
    for i in range(7):
        ph = (t * .12 + i * .143) % 1.0
        x = 120 + (i * 151) % 860 + 14 * math.sin(t * .8 + i)
        y = 1250 - ph * 1250
        r = 14 + 10 * (i % 3)
        s.append(blob(ellipse_pts(x, y, r, r, 12), "#cde9f6"))
        s.append(blob(ellipse_pts(x - r * .3, y - r * .3, r * .3, r * .3, 8), "#ffffff"))
    return "".join(s)


def hood_body():
    """Шея и худи в L-единицах головы."""
    s = []
    hood = [(-230, 90), (-300, 150), (-340, 260), (-310, 380), (-160, 400), (-60, 250)]
    s.append(shape(hood, dima.HOOD_SH, lib.blob([(-300, 260), (-240, 180), (-170, 220), (-200, 360)], dima.HOOD_SH2, .9), w=5.4, seed=SEED + 1))
    neck = [(-70, 60), (82, 66), (96, 220), (84, 280), (-80, 280), (-86, 200)]
    s.append(shape(neck, dima.SKIN, blob([(-86, 60), (-10, 110), (-20, 190), (-86, 200)], dima.SKIN_SH, .9) + blob([(10, 140), (92, 150), (96, 210), (20, 220)], dima.SKIN_SH2, .45), w=5.4, seed=SEED + 2))
    body = [(-470, 520), (-430, 300), (-330, 208), (-190, 176), (-92, 168), (-40, 176), (20, 184), (80, 178), (130, 176), (210, 176), (360, 212), (460, 300), (500, 520)]
    inner = blob([(250, 176), (460, 300), (500, 520), (200, 520), (300, 300)], dima.HOOD_SH, .8)
    inner += lib.line([(-300, 300), (-200, 330), (-150, 420)], 4, dima.FOLD, seed=SEED + 4, op=.8) + lib.line([(260, 290), (320, 340), (330, 440)], 4, dima.FOLD, seed=SEED + 5, op=.8)
    # воротник-резинка
    s.append(shape(body, dima.HOOD, inner, w=5.6, seed=SEED + 3))
    # шнурки
    for k, x0 in enumerate((-30, 46)):
        pts = [(x0, 262), (x0 - 6 + 4 * k, 330), (x0 - 2, 400)]
        s.append(lib.line(pts, 7, "#efe8da", taper=.2, wmin=.8, seed=SEED + 10 + k) + lib.line(pts, 2.4, INK, taper=.2, wmin=.8, seed=SEED + 12 + k, op=.7))
    return "".join(s)


def tongue(u):
    """Язык проводит по губам: u 0→1 — справа налево по верхней губе. В L-единицах головы (центр рта ≈ (64, 92))."""
    tx = lerp(104, 26, ease_io(u))
    ty = 82 - 6 * math.sin(math.pi * u)
    out = clamp(math.sin(math.pi * u) ** .6)
    pts = band([(64, 100), ((64 + tx) / 2, lerp(100, ty, .6)), (tx, ty)], 24, 20, step=4, cap=True)
    o = shape([(40, 88, 1), (66, 84), (90, 90, 1), (90, 108, 1), (66, 112), (40, 106, 1)], "#5a2b33", "", w=4, seed=SEED + 20)
    o += shape(pts, "#e8838f", lib.line([(64, 98), ((64 + tx) / 2, lerp(98, ty, .6)), (tx - 4, ty + 1)], 2.4, "#c25a6a", taper=.3, wmin=.5, seed=SEED + 21) +
               blob(ellipse_pts(tx - 6, ty - 3, 7, 4, 8), "#f7b4bc"), w=4, seed=SEED + 22)
    return o


def lip_shine(t):
    return ""


def icon_drop_check(cx, cy, k, u):
    """Капля с галочкой штрихами: капля — жирный контур, внутри зелёная галочка пером."""
    if u <= 0:
        return ""
    sc = k * (0.2 + 0.8 * min(1.35, lib.back_out(clamp(u / 0.45), 2.4)))
    o = []
    pts = [(0, -120, 1), (66, -30), (92, 40), (60, 108), (0, 130), (-60, 108), (-92, 40), (-66, -30)]
    o.append(shape(pts, props.C_WATER, blob([(-26, 10), (-60, 50), (-30, 100), (0, 118), (10, 40)], props.C_WATER_SH, .0) +
                   blob([(30, -10), (70, 50), (52, 100), (10, 118), (26, 50)], props.C_WATER_SH) + blob(ellipse_pts(-40, 30, 10, 30, 8, rot=20), "#ffffff"), w=10, seed=SEED + 30, var=.1))
    c0 = [(-44, 30), (-12, 70), (50, -8)]
    p = clamp((u - .25) / 0.5)
    if p > 0:
        ck = [c0[0], c0[1]] if p < .5 else [c0[0], c0[1], (c0[1][0] + (c0[2][0] - c0[1][0]) * (p - .5) * 2, c0[1][1] + (c0[2][1] - c0[1][1]) * (p - .5) * 2)]
        if p < .5:
            ck = [c0[0], (c0[0][0] + (c0[1][0] - c0[0][0]) * p * 2, c0[0][1] + (c0[1][1] - c0[0][1]) * p * 2)]
        o.append(lib.line(ck, 34, INK, taper=.05, wmin=.9, seed=SEED + 31, peak=.5))
        o.append(lib.line(ck, 22, "#3fae4a", taper=.05, wmin=.9, seed=SEED + 32, peak=.5))
    return f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(-6 + 5 * math.sin(u * 6))}) scale({sc:.4f})">{"".join(o)}</g>'


def face_state(t):
    """Выражение лица, наклон и сдвиг головы по времени."""
    # взгляд: вверх-влево (вспоминает) → в сторону → к зрителю
    if t < 21.95:
        u = ease_io(clamp((t - T0) / .5))
        look = (lerp(.5, -.5, u), lerp(.0, -.5, u))
    elif t < 22.5:
        u = ease_io((t - 21.95) / .55)
        look = (lerp(-.5, .1, u), lerp(-.5, .35, u))
    else:
        u = ease_io(clamp((t - 22.5) / .4))
        look = (lerp(.1, .55, u), lerp(.35, .1, u))
    lick = t - T_LICK[0]
    licking = T_LICK[0] <= t < T_LICK[1]
    relaxed = smooth(23.2, 23.5, t)
    brows = "up" if t < 21.9 else ("calm" if t < 23.3 else "calm")
    if 21.55 < t < 21.9:
        brows = "det"
    lid = lerp(.78, .52, relaxed)
    mouth = "flat" if t < 23.2 else ("smirk" if t > 23.34 else "relief")
    return look, brows, lid, mouth, licking, relaxed


def s12_frame(t):
    s = [background(t)]
    look, brows, lid, mouth, licking, relaxed = face_state(t)
    # кивок: голова вниз-вверх и вперёд
    nod = 0.0
    if T_NOD[0] <= t < T_NOD[1]:
        u = (t - T_NOD[0]) / (T_NOD[1] - T_NOD[0])
        nod = math.sin(u * math.pi) * 1.0 + .25 * math.sin(u * math.pi * 2.0)
    sway = 0.03 * math.sin(t * 1.9)
    head_ang = math.radians(-2.5 + 2.0 * math.sin(t * 2.1)) + nod * math.radians(7) + (math.radians(-3) if t < 21.95 else 0)
    breath = 6 * math.sin(t * 3.1)
    expr = {"lid": lid, "look": look, "brows": brows, "mouth": mouth, "hair": 3 * math.sin(t * 5.3) + 8 * nod}
    dima.LWK = 0.82
    hd = dima.head(expr)
    if licking:
        u = clamp((t - T_LICK[0]) / (T_LICK[1] - T_LICK[0]))
        # две волны подряд: в первой язык идёт справа налево, во второй — слева направо и убирается
        uu = u * 2 if u < .5 else (1 - (u - .5) * 2)
        hd += tongue(clamp(uu))
    ox, oy = HO[0], HO[1] + breath + 36 * nod
    body = f'<g transform="translate({ox} {HO[1] + breath * .4}) scale({HS})">{hood_body()}</g>'
    head_g = f'<g transform="translate({ox + 10 * nod} {oy}) rotate({math.degrees(head_ang):.3f}) scale({HS})">{hd}</g>'
    s.append(body)
    s.append(head_g)
    # иконка капли с галочкой на «жажды»
    u = (t - T_ICON) / 0.5
    s.append(icon_drop_check(905, 330, 1.2, clamp(u)) if u > 0 else "")
    e = t - T_ICON
    if 0 < e < .5:
        s.append(fp.burst(905, 340, e / .5, 12, 150, 300, 11, "#fff4c2", SEED + 40))
        s.append(props.shine_star(990, 220, 2.6, e / .5))
    # камера: медленный наезд, лёгкий дрейф, толчок на «жажды»
    u2 = clamp((t - T0) / 2.7)
    sc = lerp(1.0, 1.14, ease_io(u2))
    cx, cy = lerp(520, 560, u2), lerp(800, 770, u2)
    rot = lerp(1.6, -1.0, u2) + .4 * math.sin(t * 2.1)
    if e > 0:
        kk = math.exp(-e * 8)
        sc *= 1 + .04 * kk
        cy += 12 * kk * math.sin(e * 40)
    return svg(f'<rect width="{W}" height="{H}" fill="#f1cfa4"/><g transform="{cam(cx, cy, sc, rot)}">{"".join(s)}</g>')


def frame(sid, t):
    lib.dyn_begin()
    return s12_frame(t)
