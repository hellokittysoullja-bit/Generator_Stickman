"""Рилс 58 группа B: s04 (4.3–6.9) крупно голова Димы; на «мысль» (4.69) над ней сгущается серая туча, на «провалится» (5.97)
молния и туча давит на голову, лицо в панике. Камера: наезд с разгоном, удар на «провалится»."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bits  # noqa: E402
import dima  # noqa: E402
import lib  # noqa: E402
from lib import H, W, blob, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, lin_grad, rad_grad, smooth, svg  # noqa: E402

SEED = 4000
T_THOUGHT, T_FALL = 4.69, 5.97
HS = 2.45
HO = (500, 1040)


def lerp(a, b, u):
    return a + (b - a) * u


def background(t, gloom):
    g = lin_grad([(0, "#f6e3cc", 1), (1, "#eccfa9", 1)], 0, 0, 0, 1)
    s = [f'<rect x="-600" y="-600" width="2300" height="3200" fill="url(#{g})"/>']
    for x in range(-600, 1700, 190):
        s.append(f'<rect x="{x}" y="-600" width="80" height="3200" fill="#f1d6b3"/>')
    s.append(f'<rect x="-600" y="-600" width="2300" height="3200" fill="#3b3860" opacity="{0.34 * gloom:.3f}"/>')
    return "".join(s)


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    g = smooth(T_THOUGHT - 0.1, T_THOUGHT + 0.7, t)               # туча сгущается
    hit = t - T_FALL
    press = smooth(T_FALL, T_FALL + 0.18, t) * (1 - 0.25 * smooth(T_FALL + 0.5, T_FALL + 1.2, t))   # туча давит
    shake = math.exp(-max(0, hit) * 7) * (hit >= 0)
    s = [background(t, g)]
    # ── голова: паника растёт; на ударе зажмурился и втянул голову
    panic = smooth(T_THOUGHT, T_FALL, t)
    squeeze = clamp(press)
    lid = lerp(0.62, 1.0, panic) * (1 - 0.0) - 0.55 * squeeze * (1 if hit < 0.35 else 0)
    if hit > 0.35:
        lid = lerp(0.2, 0.92, smooth(0.35, 0.6, hit))
    lx = lerp(0.3, 0.1, panic) + 0.06 * math.sin(t * 17)
    ly = lerp(0.0, -0.45, panic)                       # смотрит вверх на тучу
    brows = "worry" if t < T_FALL else "strain"
    mouth = "flat" if t < T_THOUGHT + 0.2 else ("gape" if t < T_FALL else "strain")
    expr = {"lid": clamp(lid), "look": (lx, ly), "brows": brows, "mouth": mouth, "hair": 4 * math.sin(t * 6.1) + 20 * shake * math.sin(hit * 55) - 10 * press}
    dima.LWK = 0.82
    hd = dima.head(expr)
    dy = 80 * press + 6 * math.sin(t * 2.4) + 14 * shake * math.sin(hit * 60)
    tilt = lerp(-2, 4, panic) + 5 * press + 2.5 * shake * math.sin(hit * 48)
    tx = 3.5 * panic * math.sin(t * 43) + 7 * shake * math.sin(hit * 71)     # дрожь
    s.append(f'<g transform="translate({HO[0]} {HO[1] + dy * .55}) scale({HS})">{bits.hood_body(SEED)}</g>')
    s.append(f'<g transform="translate({HO[0] + tx} {HO[1] + dy}) rotate({tilt:.3f}) scale({HS})">{hd}</g>')
    # потные капли
    for i, (px, py) in enumerate([(300, 760), (730, 800), (345, 880)]):
        u = clamp((t - (T_THOUGHT + 0.25 + 0.25 * i)) / 0.9)
        if u > 0:
            yy = py + 110 * u * u + 40 * i
            s.append(bits.sweat(px, yy, 1.1 * (1 - .25 * u), rot=8 * math.sin(i)))
    # ── туча: растёт над головой, на «провалится» опускается, молния
    cy = lerp(300, 330, g) + 285 * press + 5 * math.sin(t * 2.2)
    cx = 520 + 12 * math.sin(t * 1.6)
    k = (0.18 + 0.82 * ease_out(g, 2.2)) * (1 + 0.06 * math.sin(t * 5))
    if g > 0.02:
        for j, (ox, oy, sk) in enumerate([(-250, 60, .55), (270, 70, .5), (-90, -90, .7), (150, -70, .62)]):
            s.append(bits.cloud(cx + ox * k, cy + oy * k, 215 * sk * 1.15, 130 * sk * 1.15, k=1, seed=SEED + 50 + j, ph=t * .6 + j, n=6, dark=g * .8, w=5, flat=.3))
        s.append(bits.cloud(cx, cy, 390, 200, k=k, seed=SEED + 60, ph=t * .5, n=9, face=False, dark=g * .8, w=6.5, flat=.35))
    # молния: три вспышки по кадрам (мигание), потом тлеет
    if hit >= 0:
        grow = clamp(hit / 0.1)
        flick = 1.0 if (hit < .28 or 0.4 < hit < .55) else 0.0
        if grow > 0 and (flick or hit < 0.7):
            s.append(bits.bolt(cx - 40, cy + 70 * k, HO[0] + 20, HO[1] - 200 + dy, 130, seed=SEED + 70, u=grow))
        if hit < 0.6:
            s.append(f'<rect x="-600" y="-600" width="2300" height="3200" fill="#fffbe0" opacity="{0.55 * math.exp(-hit * 9) * (1 if flick else .35):.3f}"/>')
        import fxprops as fp
        s.append(fp.burst(HO[0] + 20, HO[1] - 170 + dy, hit / 0.5, 12, 80, 270, 12, "#fff2a8", SEED + 80))
    # ── камера: наезд с разгоном (ease_in), удар на «провалится»
    u = clamp((t - 4.1) / 2.8)
    sc = lerp(0.98, 1.26, ease_in(u, 1.9))
    cyc = lerp(920, 840, u)
    cxc = lerp(540, 520, u)
    rot = lerp(-1.8, 1.0, u)
    if hit >= 0:
        kk = math.exp(-hit * 9)
        sc *= 1 + 0.07 * kk
        cyc += 22 * kk * math.sin(hit * 80)
        cxc += 14 * kk * math.sin(hit * 63)
        rot += 1.6 * kk * math.sin(hit * 55)
    return svg(f'<rect width="{W}" height="{H}" fill="#3b3860"/><g transform="{cam(cxc, cyc, sc, rot)}">{"".join(s)}</g>')
