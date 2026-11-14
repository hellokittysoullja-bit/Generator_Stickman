"""Кот крупно рилса 44 (агент room): s05 (на подлокотнике дивана, «почему» — наклон головы, розовое облачко-сахарная
вата проплывает, кот трогает его лапой — лопается на «мешают»), s18 (на полке рядом с копилкой-котом, смотрит в камеру,
медленно моргает, на «кот» огонёк вспыхивает). Кот — world.draw_sit (как look/hero.png: ЛЕВОЕ от зрителя ухо
загнуто, зелёные глаза, по две оранжевые полоски, огонёк на закрученном хвосте). frame(sid, t), t — общее время."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat  # noqa: E402
import den  # noqa: E402
import dream  # noqa: E402
import piggy44  # noqa: E402
import lib  # noqa: E402
import world  # noqa: E402
from ink import ellipse_pts  # noqa: E402
from lib import INK, W, H, back_out, blob, blur, cam, clamp, ease_io, ease_out, line, rect_pts, shape, smooth, svg  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!:").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


T_ZNA = wt("знаешь")          # 6.96
T_POCH = wt("почему")         # 7.36
T_SLAD = wt("сладкие")        # 7.76
T_MECHTY = wt("мечты")        # 8.20
T_MESH = wt("мешают")         # 9.227
T_NAP = wt("напиши")          # 37.56
T_KOT = wt("кот", 37.0)       # 38.00
_ST = {}


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def blinks(t, times, half=.09):
    bl = 0.0
    for tb in times:
        if abs(t - tb) < half:
            bl = max(bl, min(1, 1.7 * (1 - abs(t - tb) / half)))
    return bl


def flicks(t, times):
    fl = 0.0
    for c in times:
        e = t - c
        if 0 <= e < 0.5:
            fl += -15 * math.exp(-e * 9) * math.sin(e * 30)
    return fl


def vignette(a=.4):
    vg = lib.rad_grad([(0, "#1a1028", 0), (.6, "#1a1028", 0), (1, "#1a1028", a)], 540, 900, 1180, 1400)
    return f'<rect width="{W}" height="{H}" fill="url(#{vg})"/>'


# ═════════════════════════════ подлокотник дивана (s05) ═════════════════════════════
def armrest():
    """Подлокотник крупно: широкий валик (верх в перспективе), круглый торец слева, передняя грань вниз."""
    S, SS, SH, SD = world.SOFA, world.SOFA_SH, world.SOFA_HI, world.SOFA_DK
    y = 1290.0
    s = []
    top = [(40, y - 20, 1), (1180, y - 20, 1), (1180, y + 150, 1), (40, y + 150, 1)]
    s.append(shape(top, SH, blob([(0, y + 70), (1180, y + 70), (1180, y + 150), (0, y + 150)], S, .75) +
                   line([(120, y + 12), (1180, y + 16)], 3, S, seed=7581, op=.7), w=5, seed=7580))
    front = [(40, y + 150, 1), (1180, y + 150, 1), (1180, 2400, 1), (40, 2400, 1)]
    s.append(shape(front, S, blob([(0, y + 150), (1180, y + 150), (1180, y + 196), (0, y + 196)], SS, .9) +
                   line([(60, y + 360), (1180, y + 356)], 3, SD, seed=7591, op=.5), w=5, seed=7590))
    # круглый торец валика слева
    end = ellipse_pts(70, y + 100, 120, 150, 24)
    inner = blob(ellipse_pts(96, y + 130, 100, 120, 20), SS, .8)
    inner += line([(20, y + 30), (30, y + 100), (60, y + 190)], 2.6, SD, seed=7601, op=.55)
    inner += blob(ellipse_pts(78, y + 104, 18, 22, 12), SD, .9)
    s.append(shape(end, S, inner, w=5, seed=7600))
    return "".join(s)


def candy(x, y, k, t, wob=0.0, seed=4900):
    """Облачко-сахарная вата: пушистый розовый ком на бумажной палочке, мягкая тень, блики-нити."""
    pts = dream.cloud_pts(100, 80, n=9, wob=.06 + wob, t=t, seed=seed, bulge=.42)
    pts = [(p[0], p[1]) + tuple(p[2:]) for p in pts]
    inner = blob(ellipse_pts(30, 50, 130, 70, 16), "#ef8fb4", .9)
    inner += blob(ellipse_pts(-36, -34, 40, 22, 12, rot=-20), "#ffd6e6", .95)
    for j, (a, b, c) in enumerate((((-60, -10), (-20, -30), (20, -18)), ((-10, 20), (30, 4), (70, 14)), ((-70, 30), (-40, 40), (-6, 34)))):
        inner += line([a, b, c], 2.6, "#fbd0e2", seed=seed + 20 + j, op=.9)
    stick = [(-6, 70, 1), (6, 70, 1), (10, 190, 1), (-2, 190, 1)]
    o = [shape(stick, "#f1e3c2", blob([(2, 70), (6, 70), (10, 190), (4, 190)], "#cdb98e", .9), w=3.4, seed=seed + 1)]
    o.append(shape(pts, "#f7a8c8", inner, w=4.6, seed=seed + 2))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f}) rotate({4 * math.sin(t * 1.3):.2f})">{"".join(o)}</g>'


def candy_pop(x, y, e, seed=4950):
    """Вата лопнула: розовые клочки и блёстки разлетаются, кольцо штрихов «пуф»."""
    if e < 0 or e > .9:
        return ""
    o = []
    rs = np.random.RandomState(seed)
    for j in range(14):
        a = rs.uniform(0, 2 * math.pi)
        d = rs.uniform(140, 300) * (1 - math.exp(-e * 7))
        px, py = x + math.cos(a) * d, y + math.sin(a) * d + 160 * e * e
        r = rs.uniform(12, 26) * (1 - smooth(.4, .9, e))
        if r < 6:
            continue
        if j % 2:
            pts = dream.cloud_pts(r, r * .85, n=6, seed=seed + j, bulge=.35)
            o.append(shape([(px + p[0], py + p[1]) + tuple(p[2:]) for p in pts], "#f7a8c8", "", w=3.2, seed=seed + 40 + j))
        else:
            o.append(world.spark(px, py, r * 1.1, 40 * e * (1 if j % 4 else -1), seed + 60 + j, "#ffe7f1"))
    u = clamp(e / .28)
    if u < 1:
        for j in range(9):
            a = 2 * math.pi * j / 9
            r0, r1 = 80 + 60 * ease_out(u), 110 + 100 * ease_out(u)
            o.append(line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)], 8 * (1 - u) + 1.5,
                          INK, seed=seed + 80 + j, taper=.3, wmin=.4))
    return "".join(o)


def room_blur(t, cx=560, cy=760, z=1.5):
    if "bg" not in _ST:
        _ST["bg"] = world.room_back(0) + world.sofa_back()
    return f'<g {blur(7)}><g transform="{cam(cx, cy, z, 0)}">{_ST["bg"]}{world.evening_light(t)}</g></g>'


def s05(t):
    if "arm" not in _ST:
        _ST["arm"] = armrest()
        room_blur(t)
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    tp = T_MESH
    ep = t - tp
    # облачко ваты: вплывает слева к «сладкие», висит у морды, лапа тянется и тычет — хлоп на «мешают»
    u_in = ease_out(clamp((t - (T_SLAD - .45)) / .9), 2.4)
    cx_ = -130 + 280 * u_in + 8 * osc(t, .7)
    cy_ = 800 - 50 * u_in + 12 * osc(t, .9, 1)
    # кот смотрит в камеру → на «сладкие» глазами провожает облачко → после хлопка снова в камеру, моргает
    k_look = smooth(T_SLAD - .2, T_SLAD + .1, t) * (1 - smooth(tp + .35, tp + .6, t))
    look = (.05 * osc(t, .45) - .95 * k_look, -.05 + .05 * k_look)
    bl = blinks(t, (6.78, 8.62, tp + .12, tp + .2))
    tilt = 1.5 * osc(t, .2) - 9 * smooth(T_POCH - .05, T_POCH + .2, t) * (1 - smooth(T_SLAD + .3, T_SLAD + .6, t)) - 4 * k_look
    tilt += 5 * bump(t, tp, .35)
    flick = flicks(t, (T_POCH + .05, tp + .02))
    raise_ = back_out(clamp((t - (tp - .55)) / .3), 1.5) * (1 - ease_io(clamp((t - (tp + .35)) / .35)))
    push = math.sin(math.pi * clamp((t - (tp - .22)) / .3)) if tp - .22 < t < tp + .08 else 0.0
    tail = 6 * osc(t, .32) - 2 + (14 * math.exp(-ep * 3) * math.sin(ep * 12) if ep > 0 else 0.0)
    flame_k = 1.3 + .08 * osc(t, .5) + .5 * bump(t, tp, .4)
    nod = 7 * bump(t, T_POCH, .3) - 10 * bump(t, tp, .25)
    kitty = world.draw_sit(t, look, (bl, bl), tilt, tail, flick, raise_, push, nod, flame_k, 0.0)
    swell = 1 + .12 * smooth(tp - .2, tp, t)
    cnd = candy(cx_, cy_, .95 * swell, t, wob=.08 * smooth(tp - .25, tp, t)) if ep < 0 else ""
    pop = candy_pop(cx_, cy_ - 10, ep)
    u = clamp((t - 6.65) / 3.4)
    zc = (540, 860)
    z = 1.0 + .07 * ease_io(u) + .03 * bump(t, tp, .35)
    fg = f'translate({zc[0]} {zc[1]}) scale({z:.4f}) translate({-zc[0]} {-zc[1]})'
    par = f'translate({zc[0]} {zc[1]}) scale({1 + (z - 1) * .4:.4f}) translate({-zc[0] - 12 * u} {-zc[1]})'
    shift = f'translate(0 {-60})'
    return svg(f'<rect width="{W}" height="{H}" fill="#3a3550"/><g transform="{par}">{room_blur(t)}</g>'
               f'<g transform="{fg} {shift}"><g transform="translate(0 {1300 - world.SEAT_T - 140:.0f})"></g>{_ST["arm"]}<g transform="translate(80 0)">{kitty}</g>{cnd}{pop}</g>'
               + vignette())


# ═════════════════════════════ s18 — призыв: кот на полке рядом с копилкой ═════════════════════════════
def shelf_plank():
    """Полка крупно: верх в перспективе и передняя кромка доски, под ней стена."""
    WOOD, WOOD_SH, WOOD_HI, WOOD_DK = den.WOOD, den.WOOD_SH, den.WOOD_HI, den.WOOD_DK
    y = 1290.0
    s = [blob(rect_pts(-100, y + 120, 1180, 2400), "#3f5160")]
    top = [(-100, y - 22, 1), (1180, y - 22, 1), (1180, y + 40, 1), (-100, y + 40, 1)]
    inner = blob([(-100, y + 10), (1180, y + 10), (1180, y + 40), (-100, y + 40)], WOOD, .8)
    for k, yy in enumerate((y - 6, y + 14)):
        inner += line([(-80, yy), (300, yy + 2), (700, yy - 1), (1160, yy + 1)], 2.2, WOOD_SH, seed=7700 + k, op=.6)
    s.append(shape(top, WOOD_HI, inner, w=5, seed=7701))
    front = [(-100, y + 40, 1), (1180, y + 40, 1), (1180, y + 120, 1), (-100, y + 120, 1)]
    s.append(shape(front, WOOD, blob([(-100, y + 92), (1180, y + 92), (1180, y + 120), (-100, y + 120)], WOOD_SH, .9) +
                   line([(40, y + 70), (260, y + 72)], 2.2, WOOD_DK, seed=7711, op=.5), w=5, seed=7710))
    s.append(blob(rect_pts(-100, y + 120, 1180, y + 170), "#000000", .25, blur(10)))
    return "".join(s)


def piggy_edge():
    """Краешек копилки-кота слева: рыжевато-кремовая керамика, ухо, прорезь на спине, нарисованный глаз и румянец,
    наклейка с Фудзи, блик глазури."""
    C, CS, CD = "#efc08c", "#d39a5e", "#b47843"
    s = [blob(ellipse_pts(30, 1282, 300, 22, 16), "#140a1e", .35, blur(6))]
    ear = [(150, 830), (196, 700, 1), (250, 820)]
    s.append(shape(ear, C, blob([(196, 700), (250, 820), (214, 830)], CS, .9) + blob([(190, 760), (204, 740), (220, 800), (196, 806)], "#e79a8f", .9),
                   w=5, seed=7800))
    body = ellipse_pts(20, 1050, 300, 250, 30)
    inner = blob(ellipse_pts(60, 1170, 300, 170, 20), CS, .9)
    inner += blob(ellipse_pts(-40, 900, 120, 60, 16, rot=-20), "#fbe2c4", .95)
    inner += blob(ellipse_pts(170, 900, 26, 12, 10, rot=-10), "#ffffff", .95)
    # нарисованная мордочка (глаз-дуга, румянец, нос, усы), смотрит вправо на кота
    inner += line([(196, 990), (222, 978), (248, 990)], 6, INK, seed=7811, taper=.3, wmin=.4)
    inner += blob(ellipse_pts(232, 1036, 26, 14, 12), "#ee9a8f", .8)
    inner += blob([(286, 1014), (304, 1010), (296, 1026)], "#e47f8a")
    for k, (a, b) in enumerate((((262, 1040), (322, 1030)), ((262, 1052), (322, 1058)))):
        inner += line([a, b], 2.6, CD, seed=7812 + k, op=.8)
    # наклейка с Фудзи (круглая, белый край)
    sx, sy = 40, 1110
    stk = blob(ellipse_pts(sx, sy, 62, 58, 18), "#ffffff")
    stk += blob(ellipse_pts(sx, sy, 52, 48, 18), "#9fd0f0")
    stk += blob([(sx - 46, sy + 26), (sx, sy - 26), (sx + 46, sy + 26)], "#5b74b0")
    stk += blob([(sx - 14, sy - 10), (sx, sy - 26), (sx + 14, sy - 10), (sx + 6, sy - 6), (sx, sy - 12), (sx - 6, sy - 6)], "#ffffff")
    stk += blob(ellipse_pts(sx + 24, sy - 20, 9, 9, 10), "#ffd36a")
    inner += stk + line(ellipse_pts(sx, sy, 62, 58, 18) + [ellipse_pts(sx, sy, 62, 58, 18)[0]], 3, INK, seed=7820, taper=.05, wmin=.9)
    s.append(shape(body, C, inner, w=5.6, seed=7801))
    # прорезь для монет сверху
    s.append(shape([(-20, 812, 1), (120, 818, 1), (118, 832, 1), (-22, 826, 1)], "#3a2418", "", w=3.4, seed=7802))
    return "".join(s)


def wall_blur(t):
    """Стена как в s17 (шалфейные обои ext_b), мягко размыта — кот крупно, фон дальше."""
    if "wall18" not in _ST:
        _ST["wall18"] = piggy44.wallpaper()
    return f'<g {blur(5)}><g transform="{cam(560, 820, 1.25, 0)}">{_ST["wall18"]}</g></g>'


def slow_blink(t, t0, close=.32, hold=.22, open_=.38):
    if t < t0 or t > t0 + close + hold + open_:
        return 0.0
    if t < t0 + close:
        return ease_io((t - t0) / close)
    if t < t0 + close + hold:
        return 1.0
    return 1 - ease_io((t - t0 - close - hold) / open_)


def s18(t):
    if "pl" not in _ST:
        _ST["pl"] = f'<g transform="translate(0 {1268 - piggy44.SHELF_Y})">{piggy44.shelf(-400, 1500)}</g>'
        _ST["pig"] = piggy44.piggy_at(-60, 1268, 1.6, sticker=1.0)
        wall_blur(t)
        cat.static_parts()
        lib.static_done()
    lib.dyn_begin()
    ek = t - T_KOT
    bl = max(slow_blink(t, 38.45), slow_blink(t, 40.2), blinks(t, (39.4,)))
    look = (.04 * osc(t, .35) - .5 * bump(t, 39.0, .7), -.06 + .04 * osc(t, .27))
    tilt = 2 * osc(t, .18) - 6 * smooth(T_NAP - .05, T_NAP + .25, t) * (1 - smooth(39.0, 39.6, t)) + 4 * smooth(40.0, 40.8, t)
    flick = flicks(t, (T_KOT + .03, 39.9))
    tail = 6 * osc(t, .3) - 2 + (10 * math.exp(-ek * 3) * math.sin(ek * 12) if ek > 0 else 0.0)
    flame_k = 1.3 + .08 * osc(t, .5)
    if ek > -0.05:
        flame_k += 1.0 * back_out(clamp((ek + .05) / .18), 2.0) * math.exp(-max(ek - .15, 0) * 1.6)
    nod = 6 * bump(t, T_NAP, .3)
    kitty = world.draw_sit(t, look, (bl, bl), tilt, tail, flick, 0.0, 0.0, nod, flame_k, .35 * smooth(38.4, 38.8, t) * (1 - smooth(40.8, 41.3, t)))
    fxw, fyw = cat.flame_world(world.CAT_X, world.CAT_Y, world.CAT_S, tail)
    fxw += 30
    emb = world.embers(t, fxw, fyw - 170, T_KOT + .06)
    gl = ""
    if ek > -0.05:
        kk = clamp((flame_k - 1.3) / 1.0)
        g = lib.rad_grad([(0, "#ffb050", .5 * kk), (1, "#ffb050", 0)], fxw, fyw, 520, 520)
        gl = f'<rect width="{W}" height="{H}" fill="url(#{g})" style="mix-blend-mode:screen"/>'
    u = clamp((t - 37.2) / 4.5)
    zc = (520, 840)
    es = clamp(ek / .3) if ek > 0 else 0.0
    z = 1.0 + .1 * (.3 * u + .7 * ease_io(u)) + .03 * math.sin(math.pi * es)
    fg = f'translate({zc[0]} {zc[1]}) scale({z:.4f}) translate({-zc[0]} {-zc[1]})'
    par = f'translate({zc[0]} {zc[1]}) scale({1 + (z - 1) * .4:.4f}) translate({-zc[0] - 10 * u} {-zc[1]})'
    return svg(f'<rect width="{W}" height="{H}" fill="#9fae8e"/><g transform="{par}">{wall_blur(t)}</g>'
               f'<g transform="{fg} translate(0 -60)">{_ST["pl"]}<g transform="rotate({1.0 * math.sin(t * 1.4):.3f} -60 1268)">{_ST["pig"]}</g>{gl}<g transform="translate(30 0)">{kitty}</g>{emb}</g>' + vignette())


SHOTS = {"s05": s05, "s18": s18}


def frame(sid, t):
    return SHOTS[sid](t)
