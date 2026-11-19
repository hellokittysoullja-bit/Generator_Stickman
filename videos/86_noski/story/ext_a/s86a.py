"""Рилс 86 «Сосчитай красные носки» — все клипы. frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Время — только из shots.json (t0/t1, окна красного носка "reds") и voice/words.json (W(i)); числа в коде — длительности движений.
Бег хука, комната, телефон — помощники рилса 85 (base85.py — его код без изменений, кроме чтения "cats").
КРАСНЫЙ НОСОК рисуется ТОЛЬКО внутри 7 окон "reds" (red_u); вне окон красного (#d6182a) нет нигде, и других красных
предметов в кадре нет вовсе: ловушки — оранжевые (#f39a2b) и розовые (#f7a8cf) носки.
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука белым на чёрном (замер заполнения)."""
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from base85 import *  # noqa: E402,F401,F403
from base85 import SH, PE, dima, lib, INK, W, WE, T0, T1, NOCAM, MASK, WALL, FLOOR  # noqa: E402

RED, ORANGE, PINK = "#d6182a", "#f39a2b", "#f7a8cf"
BLUE, GREEN, GRAY, WHITE, NAVY, MINT = "#4a8fd8", "#5fb07a", "#b9c0c8", "#f4f1ea", "#3d5f96", "#8fd6c4"
SAFE = (BLUE, GREEN, GRAY, WHITE, NAVY, MINT, ORANGE, PINK)
REDS = {r["id"]: r for r in SH["reds"]}


def red_u(rid, t):
    """0…1 — ход красного носка rid по его окну; None — вне окна (не рисовать)."""
    r = REDS[rid]
    if not r["t"] <= t <= r["t"] + r["dur"]:
        return None
    return (t - r["t"]) / r["dur"]


# ═════════════════════════ носок, корзина, телефон, лампочка ═════════════════════════
SOCK = [(-16, -56), (16, -56), (18, 8), (46, 20), (52, 36), (44, 48), (-4, 48), (-18, 24)]


def sock(x, y, k, rot, col, seed=0):
    if col == RED:
        cuff, heel = "#f2d9dc", "#a81020"
    else:
        cuff, heel = "#ffffff" if col not in (WHITE,) else "#d8dde3", lib.mul(col, (.8, .8, .85))
    inner = (f'<rect x="-30" y="-56" width="70" height="18" fill="{cuff}" opacity=".9"/>'
             f'<path d="M30 22 Q50 26 50 40 L40 46 Q30 34 24 30Z" fill="{heel}"/>'
             f'<path d="M-18 24 Q-12 40 -4 46 L4 46 Q-6 36 -8 22Z" fill="{heel}"/>')
    b = shape(SOCK, col, inner, w=3.2, seed=seed)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">{b}</g>'


def towel(x, y, w, h, col, seed=0, rot=0.0):
    b = shape(lib.rrect(-w / 2, -h / 2, w / 2, h / 2, 10), col,
              f'<rect x="{-w / 2}" y="{h / 2 - 22}" width="{w}" height="10" fill="#ffffff" opacity=".6"/>'
              + line([(-w / 2 + 14, -h / 2 + 18), (w / 2 - 14, -h / 2 + 22)], 2.2, lib.mul(col, (.8, .8, .85)), seed=seed), w=3.4, seed=seed)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">{b}</g>'


def basket_back(x, y, k):
    """Задняя стенка корзины (рисовать до содержимого). (x, y) — середина верхнего края."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">'
            + shape(lib.rrect(-150, -26, 150, 26, 26), "#b8925a", "", w=3.4, seed=301) + "</g>")


def basket_front(x, y, k, seed=0):
    pts = [(-160, 0), (160, 0), (130, 230), (-130, 230)]
    weave = "".join(line([(-150 + 6 * i, 30 + 50 * i), (150 - 6 * i, 30 + 50 * i)], 3, "#a07a44", seed=seed + i) for i in range(4))
    weave += "".join(line([(-120 + 60 * i, 6), (-100 + 50 * i, 226)], 2.4, "#a07a44", seed=seed + 10 + i) for i in range(5))
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">'
            + shape(pts, "#d9b77a", weave, w=4.0, seed=seed)
            + shape(lib.rrect(-168, -14, 168, 18, 14), "#c9a468", "", w=3.6, seed=seed + 20) + "</g>")


def heap(x, y, k, seed=0, n=9, t=0.0):
    """Гора белья над краем корзины (без красного)."""
    rnd = random.Random(seed)
    o = []
    for i in range(n):
        dx, dy = rnd.uniform(-120, 120), rnd.uniform(-90, 0) - 30 * (1 - abs(i - n / 2) / n)
        col = rnd.choice((BLUE, GREEN, WHITE, GRAY, MINT, NAVY))
        if i % 3 == 0:
            o.append(towel(dx, dy, 150, 70, col, seed + i, rnd.uniform(-25, 25)))
        else:
            o.append(sock(dx, dy, 1.1, rnd.uniform(-90, 90), col, seed + i))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">{"".join(o)}</g>'


def phone_flat(x, y, k, rot=0.0, buzz=0.0, glow=0.0, t=0.0, back=False):
    """Телефон лежит на столе (вид сверху-спереди): buzz 0…1 — дрожь и дуги вибрации, glow — экран вспыхивает (без букв)."""
    jx = buzz * 7 * math.sin(t * 95)
    jr = buzz * 2.5 * math.sin(t * 77)
    o = [f'<ellipse cx="6" cy="14" rx="150" ry="62" fill="#000" opacity=".14"/>']
    if back:
        o.append(shape(lib.rrect(-130, -70, 130, 70, 26), "#3a3f4b", f'<circle cx="-80" cy="-28" r="18" fill="#22252c" stroke="#5a606c" stroke-width="5"/>', w=4.0, seed=401))
    else:
        scr = lib.mix("#2a3446", "#cfe6ff", glow)
        o.append(shape(lib.rrect(-130, -70, 130, 70, 26), "#24262e", f'<rect x="-112" y="-54" width="224" height="108" rx="16" fill="{scr}"/>', w=4.0, seed=401))
        if glow > .05:
            o.append(f'<rect x="-96" y="-38" width="192" height="40" rx="12" fill="#ffffff" opacity="{glow:.2f}"/>'
                     f'<circle cx="-72" cy="-18" r="12" fill="{BLUE}" opacity="{glow:.2f}"/>'
                     f'<rect x="-48" y="-26" width="110" height="10" rx="5" fill="#9aa3b0" opacity="{glow:.2f}"/>'
                     f'<rect x="-48" y="-10" width="70" height="8" rx="4" fill="#cfd5de" opacity="{glow:.2f}"/>')
    if buzz > .05:
        for side in (-1, 1):
            for j in range(3):
                r = 150 + 34 * j + 10 * math.sin(t * 40 + j)
                o.append(f'<path d="M{side * r:.1f} -40 Q{side * (r + 22):.1f} 0 {side * r:.1f} 40" fill="none" stroke="{INK}" '
                         f'stroke-width="6" stroke-linecap="round" opacity="{buzz * (1 - .25 * j):.2f}"/>')
    return f'<g transform="translate({x + jx:.1f} {y:.1f}) rotate({rot + jr:.2f}) scale({k:.3f})">{"".join(o)}</g>'


def buzz_env(t, times, dur=.55):
    b = 0.0
    for tb in times:
        u = t - tb
        if 0 <= u < dur:
            b = max(b, (1 - u / dur) ** .6 * (.6 + .4 * abs(math.sin(u * 30))))
    return b


def bulb(x, y, k, on, t=0.0, seed=0):
    """Лампочка внимания над головой: on 1 — горит жёлтым с ореолом, 0 — серая."""
    o = []
    if on > .02:
        g = lib.rad_grad([(0, "#fff3a0", .9 * on), (1, "#fff3a0", 0)], .5, .5, .5)
        o.append(f'<circle cx="0" cy="0" r="{150 + 10 * math.sin(t * 9)}" fill="url(#{g})"/>')
    glass = lib.mix("#c9ccd2", "#ffe45c", on)
    o.append(shape(ellipse_pts(0, 0, 62, 66, 24), glass, f'<path d="M-24 -20 Q-20 -40 0 -44" stroke="#ffffff" stroke-width="8" fill="none" opacity=".8"/>'
                   + line([(-16, 40), (-8, 6), (8, 6), (16, 40)], 3, lib.mix("#8a8f99", "#c98a10", on), seed=seed), w=4.0, seed=seed))
    o.append(shape(lib.rrect(-30, 54, 30, 96, 6), "#9aa3b0", line([(-28, 68), (28, 68)], 2.4, "#6b7380") + line([(-28, 82), (28, 82)], 2.4, "#6b7380"), w=3.4, seed=seed + 1))
    if on > .5:
        for i in range(6):
            a = -math.pi / 2 + (i - 2.5) * .45
            o.append(line([(92 * math.cos(a), 92 * math.sin(a)), (122 * math.cos(a), 122 * math.sin(a))], 6, "#f2b81c", seed=seed + 5 + i))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">{"".join(o)}</g>'


def toss(t, t0, dur, x0, x1, top, bottom=2160.0, spin=520.0):
    """Носок подброшен из-за нижнего края экрана и падает обратно: (x, y, rot) или None вне [t0, t0+dur]."""
    u = (t - t0) / dur
    if not 0 <= u <= 1:
        return None
    return x0 + (x1 - x0) * u, bottom - (bottom - top) * 4 * u * (1 - u), spin * (u - .5)


# ═════════════════════════ комната хука и петли (мир: пол y = 0) ═════════════════════════
def room_b(xa=-900, xb=3800):
    g = lib.lin_grad([(0, "#f6ead2", 1), (1, WALL, 1)], 0, -1200, 0, 0, units="userSpaceOnUse")
    o = [f'<rect x="{xa}" y="-1500" width="{xb - xa}" height="1500" fill="url(#{g})"/>']
    o += [f'<rect x="{x}" y="-1500" width="40" height="1500" fill="#e2cfa8" opacity=".35"/>' for x in range(int(xa) // 120 * 120, int(xb), 120)]
    o.append(f'<rect x="{xa}" y="0" width="{xb - xa}" height="900" fill="{FLOOR}"/>')
    o += [line([(x, 0), (x - 300, 900)], 3, "#b3875a", seed=x) for x in range(int(xa) // 200 * 200, int(xb) + 400, 200)]
    o.append(f'<rect x="{xa}" y="-34" width="{xb - xa}" height="34" fill="#fbf6ea" stroke="{INK}" stroke-width="3"/>')
    o.append(room_items())
    return "".join(o)


def room_items():
    o = [shape(ellipse_pts(850, 230, 520, 120, 28), "#4aa39a", '<ellipse cx="850" cy="230" rx="430" ry="90" fill="none" stroke="#fbf6ea" stroke-width="10" opacity=".7"/>', w=3.6, seed=850),
         plant(-250, 11), win(100, -780, 420, -420, 3), wardrobe(670, 970, -900, 5),
         line([(1120, -760), (1560, -730)], 4, INK, seed=88)]
    for i, (xx, c) in enumerate(((1170, BLUE), (1260, GREEN), (1350, WHITE), (1450, MINT))):   # носки на верёвке над полкой
        o.append(sock(xx, -700 + 3 * i, 1.0, 4, c, seed=90 + i))
    o += [picture(1720, -640, 220, 160, 9), sofa(1900, 2450, 13), lamp(2600, 15), win(2800, -780, 3150, -420, 17), wardrobe(3350, 3650, -900, 19)]
    return "".join(o)


KINDS86 = (("sock", BLUE), ("sock", ORANGE), ("towel", GREEN), ("sock", PINK), ("sock", GREEN), ("towel", MINT), ("sock", WHITE), ("sock", NAVY))


def laundry_throws(t, t_first, t_last, every, origin, vx, rng_seed, floor=60.0, k=1.5, g=2600.0, vy=-1150.0):
    """Бельё летит из корзины по баллистике и ложится на пол (без красного)."""
    rnd = random.Random(rng_seed)
    o = []
    tl, i = t_first, 0
    while tl <= min(t, t_last):
        p0 = np.array(origin(tl), float)
        v = np.array([vx * rnd.uniform(.7, 1.3), vy * rnd.uniform(.8, 1.15)])
        kind, col = KINDS86[(i + rng_seed) % len(KINDS86)]
        spin = rnd.uniform(-900, 900)
        u = t - tl
        fl = floor + rnd.uniform(0, 260)
        a_, b_, c_ = .5 * g, v[1], p0[1] - fl
        tland = (-b_ + math.sqrt(max(b_ * b_ - 4 * a_ * c_, 0))) / (2 * a_)
        if u >= tland:
            u, y = tland, fl
            rot = round(spin * tland / 180) * 180 + 8 * (1 if i % 2 else -1)
        else:
            y, rot = p0[1] + v[1] * u + .5 * g * u * u, spin * u
        x = p0[0] + v[0] * u
        kk = k * rnd.uniform(.85, 1.15)
        o.append(sock(x, y - 30 * k, kk, rot, col, 50 + i) if kind == "sock" else towel(x, y - 30 * k, 130 * kk, 60 * kk, col, 50 + i, rot))
        tl += every
        i += 1
    return "".join(o)


def fly_socks(t, specs):
    """Носки летят у самой камеры (экранные координаты): specs [(t0, dur, (x0, y0), (x1, y1), k, spin, col)]."""
    o = []
    for t0, dur, p0, p1, k, spin, col in specs:
        u = (t - t0) / dur
        if 0 <= u <= 1:
            x = p0[0] + (p1[0] - p0[0]) * u
            y = p0[1] + (p1[1] - p0[1]) * u - 160 * math.sin(math.pi * u)
            o.append(sock(x, y, k * (1 + .25 * u), spin * u, col, seed=int(t0 * 100) % 97))
    return "".join(o)


def carry_pose(t, lift=0.0):
    p = run_pose(t)
    hip = np.array(p["hip"])
    p["arms"]["n"] = ("ik", tuple(hip + np.array([210.0, -300.0 - 60 * lift])), -1)
    p["arms"]["f"] = ("ik", tuple(hip + np.array([150.0, -320.0 - 60 * lift])), -1)
    p["hands"] = {"n": ("open", .3), "f": ("open", .3)}
    return p


def hook_world(t, s, gy, sx, follow, a, seed, vx):
    ensure("hook")
    cam = part_cam(t, a, s, sx, gy, follow)
    lift = .5 + .5 * math.sin(t * 14)
    p = carry_pose(t, lift)
    p["expr"].update(look=(.7, -.5) if (t // .35) % 2 == 0 else (.3, -.8), brows="up", mouth="gape", lid=1.0)
    dg, wr = dima.draw(p)
    bx, by = np.array(wr["n"]) + np.array([-20.0, 30.0])
    bk = basket_back(bx, by, .62) + heap(bx, by - 6, .5, seed=7, n=6) + basket_front(bx, by, .62, seed=31)
    thr = laundry_throws(t, -1.2, T1("s02"), .17, lambda tl: (hip_at(tl, bob=False)[0] + 150, -560.0), vx, seed, k=1.5)
    return cam, dg, bk, thr


def frame_s01(t):
    lib.DEFS.clear()
    cam, dg, bk, thr = hook_world(t, 1.25, 1350.0, 300.0, .45, 0.0, 86, -620.0)
    fg = fly_socks(t, [(-.2, .7, (980, 1500), (-160, 1050), 2.6, -400, BLUE), (.25, .6, (1140, 1250), (-180, 820), 3.0, 500, GREEN),
                       (.55, .65, (900, 1700), (-200, 1200), 2.8, -380, ORANGE), (.85, .6, (1150, 1100), (-150, 1500), 2.4, 420, WHITE)])
    u = red_u(1, t)
    if u is not None:                     # красный 1: через кадр слева направо, середина, виден с первого кадра
        x = 140 + (1260 - 140) * u
        fg += sock(x, 930 - 170 * math.sin(math.pi * u), 2.7, -30 + 380 * u, RED, seed=1)
    world = room_b() + dg + bk + thr
    if MASK:
        lib.DEFS.append(MASK_F)
        return lib.svg('<rect width="1080" height="1920" fill="#000"/><g filter="url(#mk85)">'
                       f'<g transform="{lib.cam(*cam)}">{room_items() + dg + bk + thr}</g>{fg}</g>')
    body = f'<rect width="1080" height="1920" fill="{WALL}"/><g transform="{lib.cam(*cam)}">{world}</g>'
    if NOCAM:
        return lib.svg(body + fg)
    return lib.svg(hook_wrap(body, t, W(SHOT["s01"]["hit_word"])) + fg + title(t))


def frame_s02(t):
    lib.DEFS.clear()
    a = T0("s02")
    cam, dg, bk, thr = hook_world(t, 1.34, 1400.0, 280.0, .72, a, 87, -660.0)
    cx, cy, s_, rot = cam
    cam = (cx, cy, s_, rot + (0 if NOCAM else 2.0 * kick2(t, W(4))))
    fg = fly_socks(t, [(1.25, .55, (-150, 1300), (1200, 900), 3.2, 420, ORANGE), (1.6, .6, (-120, 900), (1200, 1400), 2.8, -380, MINT),
                       (1.95, .55, (-160, 1500), (1180, 1000), 3.4, 500, PINK), (2.25, .5, (-140, 1100), (1200, 800), 2.6, -420, BLUE)])
    world = room_b() + dg + bk + thr
    z = 1 + (0 if NOCAM else .07 * kick2(t, W(4)))
    body = (f'<rect width="1080" height="1920" fill="{WALL}"/>'
            f'<g transform="translate(540 {PIV}) scale({z:.4f}) translate(-540 {-PIV})">{mirror(f"<g transform=\"{lib.cam(*cam)}\">{world}</g>")}</g>')
    return lib.svg(body + fg + title(t))


def frame_s03(t):
    """«Готов?»: Дима выглядывает из-за горы белья в корзине; розовый носок падает на гору."""
    lib.DEFS.clear()
    a = T0("s03")
    o = [wall_bg(1650.0), win(-60, 420, 260, 820, 31), picture(900, 520, 200, 150, 33)]
    nod = .1 * math.sin(math.pi * clamp((t - W(6)) / .35)) if t > W(6) else 0
    e = ex("wow82", look=(0, .1)) if t < W(6) + .4 else ex("sure82", look=(0, .1))
    f_ = dfig(540, 1500, 1.15, e, "d82_hold", t=t, head_add=nod + .03 * math.sin((t - a) * 5))
    o.append(f_["svg"])
    o.append(basket_back(540, 1330, 1.7) + heap(540, 1320, 1.55, seed=12, n=11, t=t))
    tp = W(6) - .45
    if t > tp:
        u = clamp((t - tp) / .4)
        yy = -200 + (1170 + 200) * ease_in(u, 2)
        o.append(sock(600 + 40 * u, yy, 1.8, 30 + 200 * u, PINK, seed=5))
        o.append(burst(610, 1180, 120, tp + .4, t, "#ffffff", 8, .3))
    o.append(basket_front(540, 1330, 1.7, seed=37))
    dx, dy, r = drift(t, 1.3)
    z = 1.08 - .05 * (t - a) + .06 * kick2(t, W(6))
    return view("".join(o), 540 + dx, 1000 + dy, z, r + 1.5 * kick2(t, W(6)), over=title(t))


def frame_s04(t):
    """«Не отвлекайся»: лицо крупно, носки взлетают перед ним снизу и падают, глаза бегут за ними; красный 2."""
    lib.DEFS.clear()
    a = T0("s04")
    o = [wall_bg(2600.0), line([(-200, 300), (1300, 330)], 5, INK, seed=41)]
    for i, (xx, c) in enumerate(((120, BLUE), (330, GREEN), (760, MINT), (960, GRAY))):
        o.append(sock(xx, 380 + 2 * i, 1.4, 6 * math.sin(t * 3 + i), c, seed=42 + i))
    specs = [(3.55, .55, 140, 420, 700, GREEN), (3.85, .5, 900, 640, 760, ORANGE), (4.05, .5, 300, 120, 640, BLUE),
             (4.55, .55, 820, 980, 680, PINK), (4.8, .5, 200, 420, 720, WHITE)]
    socks_ = []
    look = (0, -.2)
    for t0, dur, x0, x1, top, col in specs:
        q = toss(t, t0, dur, x0, x1, top)
        if q:
            socks_.append(sock(q[0], q[1], 2.4, q[2], col, seed=int(t0 * 10)))
            look = ((q[0] - 540) / 500, (q[1] - 900) / 700)
    u = red_u(2, t)
    if u is not None:
        r = REDS[2]
        q = toss(r["t"] + clamp(u) * r["dur"] * .9999, r["t"], r["dur"], 860, 560, 600)
        socks_.append(sock(q[0], q[1], 2.5, q[2], RED, seed=2))
        look = ((q[0] - 540) / 500, (q[1] - 900) / 700)
    e = ex("saucer", look=(clamp(look[0], -1, 1), clamp(look[1], -1, 1)))
    e["closed"] = 0.0
    f_ = dfig(470, 1980, 2.05, e, "d82_rest", t=t, head_add=.05 * math.sin((t - a) * 6))
    o.append(f_["svg"])
    dx, dy, r_ = drift(t, 1.2)
    z = 1.0 + .05 * (t - a) + .07 * kick2(t, W(8))
    return view("".join(o), 540 + dx, 900 + dy, z, r_ + 1.5 * kick2(t, W(8)), over="".join(socks_))


def frame_s05(t):
    """Стиральная машина: барабан крутится, носки кувыркаются в окне; прыжок на «сложнее»; красный 3 в окне."""
    lib.DEFS.clear()
    a = T0("s05")
    tile = "".join(f'<rect x="{x}" y="{y}" width="118" height="118" fill="#dceef2" stroke="#b9d3da" stroke-width="4"/>'
                   for x in range(-200, 1300, 120) for y in range(-200, 1300, 120))
    o = [f'<rect x="-300" y="-300" width="1680" height="2520" fill="#dceef2"/>', tile,
         f'<rect x="-300" y="1300" width="1680" height="900" fill="#c7d2d8"/>']
    jump = 26 * kick2(t, W(10), .05, .2) + 4 * math.sin(t * 60) * (1 if t > W(10) else .4)
    m = [shape(lib.rrect(170, 260, 910, 1420, 40), "#f6f7f9", f'<rect x="170" y="260" width="740" height="200" rx="40" fill="#e6e9ee"/>', w=5.0, seed=51),
         f'<circle cx="760" cy="360" r="38" fill="#ffffff" stroke="{INK}" stroke-width="4"/>',
         f'<rect x="240" y="330" width="240" height="56" rx="12" fill="#cfd5de" stroke="{INK}" stroke-width="3"/>']
    cx, cy, R = 540.0, 930.0, 300.0
    m.append(f'<circle cx="{cx}" cy="{cy}" r="{R + 46}" fill="#d0d6de" stroke="{INK}" stroke-width="6"/>')
    c = lib.clip_rect(cx - R, cy - R, 2 * R, 2 * R, R)
    ang = (t - a) * 340
    inner = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#2d4f7a"/>']
    for i, col in enumerate((ORANGE, BLUE, PINK, GREEN, WHITE, MINT, ORANGE, NAVY)):
        aa = math.radians(ang + i * 45)
        rr = R * (.35 + .4 * ((i * 37) % 5) / 5)
        inner.append(sock(cx + rr * math.cos(aa), cy + rr * math.sin(aa), 1.7, ang * 1.4 + i * 50, col, seed=60 + i))
    u = red_u(3, t)
    if u is not None:      # красный 3: падает сверху через окно и уходит за нижний край окна
        inner.append(sock(cx - 120 + 260 * u, cy - R - 120 + (2 * R + 240) * u, 1.9, 200 * u - 40, RED, seed=3))
    for j in range(3):
        bx_ = cx - 200 + 140 * j + 30 * math.sin(t * 3 + j)
        by_ = cy + R - ((t * 260 + 170 * j) % (2 * R))
        inner.append(f'<circle cx="{bx_:.1f}" cy="{by_:.1f}" r="{14 + 6 * j}" fill="#ffffff" opacity=".35"/>')
    m.append(f'<g clip-path="url(#{c})">{"".join(inner)}<path d="M{cx - R} {cy - 40} Q{cx} {cy - 120} {cx + R} {cy - 40} L{cx + R} {cy + R} L{cx - R} {cy + R}Z" fill="#5f9bd1" opacity=".25"/></g>')
    m.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#9aa3b0" stroke-width="16"/><circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{INK}" stroke-width="4"/>')
    m.append(f'<path d="M{cx - 200} {cy - 210} Q{cx - 240} {cy - 120} {cx - 230} {cy - 40}" stroke="#ffffff" stroke-width="16" fill="none" opacity=".5"/>')
    o.append(f'<g transform="translate(0 {-jump:.1f})">{"".join(m)}</g>')
    o.append(line([(150, 1430), (100, 1460)], 8, INK, seed=57) + line([(930, 1430), (980, 1460)], 8, INK, seed=58) if t > W(10) and (t - W(10)) < .5 else "")
    dx, dy, r_ = drift(t, 1.0)
    z = 1.12 + .06 * (t - a) + .08 * kick2(t, W(10))
    return view("".join(o), 540 + dx, 900 + dy, z, r_ + 2 * kick2(t, W(10)))


# ═════════════════════════ s06–s07: телефон (призыв без букв) ═════════════════════════
def mini_room86(x0, y0, w, h):
    return (f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{WALL}"/>'
            f'<rect x="{x0}" y="{y0 + h * .72}" width="{w}" height="{h * .28}" fill="{FLOOR}"/>'
            f'<rect x="{x0 + w * .62}" y="{y0 + h * .15}" width="{w * .26}" height="{h * .25}" fill="#9fd0f0" stroke="{INK}" stroke-width="3"/>'
            + basket_back(x0 + w * .35, y0 + h * .6, .45) + heap(x0 + w * .35, y0 + h * .6, .42, seed=3, n=6) + basket_front(x0 + w * .35, y0 + h * .6, .45, seed=9)
            + sock(x0 + w * .7, y0 + h * .82, .7, 70, ORANGE, seed=4) + sock(x0 + w * .85, y0 + h * .86, .7, -20, BLUE, seed=6))


def frame_s06(t):
    lib.DEFS.clear()
    a = T0("s06")
    x0, y0, x1, y1 = PH
    ttap, tsend = W(14), WE(16)
    inner = [mini_room86(x0 + 18, y0 + 18, x1 - x0 - 36, 360)]
    rows = [("#8fd16a", 300, 200), ("#e8a24a", 240, 330), ("#8a6fc4", 340, 180), (BLUE, 260, 280)]
    up = 120 * ease_out(clamp((t - tsend) / .3))
    ny = y0 + 470
    if t >= tsend:
        sc = ease_out(clamp((t - tsend) / .25))
        inner.append(f'<g transform="translate({x0 + 40} {ny + 50}) scale({sc:.3f}) translate({-(x0 + 40)} {-(ny + 50)})">'
                     + comment_row(x0 + 40, ny + 50, "#d4a23a", 230, 150, hl=1 - .5 * clamp((t - tsend - .4) / .6)) + "</g>")
    for i, (c, n1, n2) in enumerate(rows):
        inner.append(comment_row(x0 + 40, ny + 50 + 120 * i + up, c, n1, n2, seed=i))
    fy = y1 - 150
    act = t >= ttap
    inner.append(f'<rect x="{x0 + 18}" y="{fy - 40}" width="{x1 - x0 - 36}" height="190" fill="#eef1f6"/>')
    inner.append(f'<rect x="{x0 + 40}" y="{fy}" width="{x1 - x0 - 170}" height="76" rx="38" fill="#ffffff" stroke="{BLUE if act else "#b8c0cc"}" stroke-width="{5 if act else 3}"/>')
    if not act or t >= tsend:
        if int(t * 2.5) % 2 == 0:
            inner.append(f'<rect x="{x0 + 76}" y="{fy + 16}" width="6" height="44" rx="3" fill="{BLUE}"/>')
    else:
        for j in range(3):
            bob = 10 * max(0.0, math.sin((t - ttap) * 12 - j * .9))
            inner.append(f'<circle cx="{x0 + 90 + 36 * j}" cy="{fy + 38 - bob:.1f}" r="11" fill="{BLUE}"/>')
    sb = 1 + .25 * kick2(t, tsend)
    inner.append(f'<g transform="translate({x1 - 80} {fy + 38}) scale({sb:.3f})"><circle r="38" fill="{BLUE}" stroke="{INK}" stroke-width="3"/>'
                 '<path d="M-14 -16 L18 0 L-14 16 L-8 0Z" fill="#fff"/></g>')
    for j in range(4):                    # синие сердечки после отправки
        u = (t - tsend - .1 * j) / .9
        if 0 <= u < 1:
            hx, hy = x1 - 90 - 40 * j + 20 * math.sin(u * 8 + j), fy - 30 - 380 * u
            inner.append(f'<path transform="translate({hx:.1f} {hy:.1f}) scale({1.4 * (1 - .4 * u):.2f})" d="M0 6 c-10 -16 -32 -6 -22 10 l22 18 l22 -18 c10 -16 -12 -26 -22 -10z" fill="{BLUE}" opacity="{1 - u:.2f}"/>')
    rest, fieldp, sendp = (x1 - 20, y1 - 330), (x0 + 260, fy + 40), (x1 - 80, fy + 40)
    if t < ttap:
        tp = np.array(rest) + (np.array(fieldp) - np.array(rest)) * ease_io(clamp((t - (ttap - .35)) / .35))
    elif t < tsend - .25:
        tp = np.array(fieldp) + np.array([0, 10 * kick2(t, ttap)])
    else:
        tp = np.array(fieldp) + (np.array(sendp) - np.array(fieldp)) * ease_io(clamp((t - (tsend - .25)) / .25)) + np.array([0, 10 * kick2(t, tsend)])
    body = phone_body("".join(inner), t, rot=-3 + 1.2 * math.sin(t * 2), tap=tuple(tp))
    dx, dy, r = drift(t)
    z = 1.04 + .03 * (t - a) + .05 * kick2(t, tsend)
    return view(body + burst(sendp[0], sendp[1], 110, tsend, t, BLUE, 10, .35), 540 + dx, 820 + dy, z, r, bg="#d9e8f2")


def envelope86(x, y, k, rot):
    o = [shape(lib.rrect(-80, -52, 80, 52, 8), "#ffffff", "", w=4.0, seed=101),
         line([(-78, -48), (0, 10), (78, -48)], 4, INK, seed=102), f'<rect x="-30" y="12" width="60" height="22" rx="4" fill="{BLUE}"/>']
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">{"".join(o)}</g>'


def frame_s07(t):
    """Конверт влетает в телефон на «пришлю», на «личку» в чате бабл-картинка: гора носков и лупа (без букв)."""
    lib.DEFS.clear()
    a = T0("s07")
    x0, y0, x1, y1 = PH
    tin, tmsg = W(19), W(24)
    inner = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="140" fill="#e6ecf4"/>',
             f'<circle cx="{x0 + 90}" cy="{y0 + 90}" r="34" fill="#d4a23a" stroke="{INK}" stroke-width="3"/>',
             f'<rect x="{x0 + 140}" y="{y0 + 76}" width="180" height="18" rx="9" fill="#9aa3b0"/>']
    by = y0 + 210
    inner.append(f'<rect x="{x1 - 330}" y="{by}" width="280" height="70" rx="30" fill="{BLUE}"/><rect x="{x1 - 300}" y="{by + 26}" width="190" height="16" rx="8" fill="#d8e8fb"/>')
    if t >= tmsg:
        sc = ease_out(clamp((t - tmsg) / .25))
        bx, byy = x0 + 50, by + 120
        pic = (f'<rect x="{bx}" y="{byy}" width="380" height="330" rx="30" fill="#ffffff" stroke="#cfd5de" stroke-width="4"/>'
               f'<rect x="{bx + 20}" y="{byy + 20}" width="340" height="290" rx="20" fill="{WALL}"/>'
               + heap(bx + 190, byy + 220, .9, seed=21, n=8) + magnifier(bx + 250, byy + 130, 1.0, -20))
        inner.append(f'<g transform="translate({bx} {byy}) scale({sc:.3f}) translate({-bx} {-byy})">{pic}</g>')
        for j in range(3):
            inner.append(f'<circle cx="{bx + 40 + 30 * j}" cy="{byy + 380}" r="9" fill="#9aa3b0" opacity="{clamp((t - tmsg - .3 - .15 * j) / .2):.2f}"/>')
    body = phone_body("".join(inner), t, rot=2 - 1.2 * math.sin(t * 2), tap=(x1 + 40, y1 + 40))
    env = ""
    if tin - .3 <= t < tmsg + .05:
        u = clamp((t - (tin - .3)) / (tmsg + .05 - (tin - .3)))
        ex_, ey_ = -150 + (540 + 150) * ease_in(u, 1.6), 260 + (700 - 260) * u - 220 * math.sin(math.pi * u)
        env = envelope86(ex_, ey_, 1.6 * (1 - .6 * ease_in(u, 3)), -30 + 40 * u)
    dx, dy, r = drift(t)
    z = 1.04 + .02 * (t - a) + .06 * kick2(t, tmsg)
    return view(body + env + burst(540, 700, 160, tmsg, t, "#ffd23f", 10, .35), 540 + dx, 820 + dy, z, r, bg="#e4dcf2")


# ═════════════════════════ s08–s11, s15–s16: Дима разбирает бельё у стола ═════════════════════════
def table86(x0, x1, top, seed=0):
    return (shape(lib.rect_pts(x0, top, x1, top + 520), "#a8784f", f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="34" fill="#c49264"/>', w=4.0, seed=seed))


def piles(x, y, k, seed=0):
    o = []
    for i, col in enumerate((BLUE, WHITE, GREEN, MINT)):
        o.append(f'<g transform="translate({x:.1f} {y - 30 * i * k:.1f}) scale({k:.3f})">' + shape(lib.rrect(-110, -18, 110, 18, 10), col, "", w=3.2, seed=seed + i) + "</g>")
    return "".join(o)


def sort_scene(t, sid, hip=1120.0, k=.95, expr="calm82", pose=("place74", "d82_hold"), phone=None, extra_back="", extra_front="", bulb_on=None,
               look=None, phase=0.0):
    a = T0(sid)
    o = [wall_bg(1300.0), win(60, 260, 360, 640, 81), picture(880, 420, 200, 150, 83), extra_back]
    u = .5 + .5 * math.sin((t - a) * 5 + phase)
    e = ex(expr, look=look) if look else ex(expr)
    f_ = dfig(560, hip, k, e, pose, t=t, u=u, head_add=.04 * math.sin((t - a) * 3))
    o.append(f_["svg"])
    if bulb_on is not None:
        hx, hy = f_["head"]
        o.append(bulb(hx + 10, hy - 260 * k, .9 * k, bulb_on, t, seed=88))
    o.append(table86(-200, 1280, 1230, 85))
    o.append(piles(250, 1236, 1.0, seed=86) + piles(820, 1236, .9, seed=90))
    o.append(sock(420, 1250, 1.2, 80, ORANGE, seed=91) + sock(980, 1262, 1.1, -30, PINK, seed=92) + sock(650, 1300, 1.1, 10, BLUE, seed=93))
    if phone:
        o.append(phone_flat(phone[0], phone[1], phone[2], -8, phone[3], phone[4], t))
    o.append(extra_front)
    return o, f_


def frame_s08(t):
    """Общий план: разбирает бельё, телефон на столе; красный 4 — из корзины за спину, за верхний край кадра."""
    lib.DEFS.clear()
    a = T0("s08")
    back = basket_back(930, 1120, 1.0) + heap(930, 1112, .9, seed=33, n=8)
    red = ""
    u = red_u(4, t)
    if u is not None:
        red = sock(930 - 500 * u, 1100 - 1400 * u + 600 * u * u, 1.6, -500 * u, RED, seed=4)
    o, f_ = sort_scene(t, "s08", extra_back="", phone=(170, 1320, .9, 0.0, 0.0))
    o.append(back + red + basket_front(930, 1120, 1.0, seed=35))
    dx, dy, r = drift(t, 1.0)
    z = .92 + .04 * (t - a)
    return view("".join(o), 540 + dx, 1000 + dy, z, r)


def frame_s09(t):
    """Вставка: телефон на столе среди носков жужжит."""
    lib.DEFS.clear()
    a = T0("s09")
    tb = [W(31), W(33)]
    bz = buzz_env(t, tb)
    o = [f'<rect x="-300" y="-300" width="1680" height="2520" fill="#b78a5c"/>']
    o += [line([(-300, y), (1400, y + 40)], 4, "#9c7448", seed=y) for y in range(-200, 2200, 140)]
    o.append(sock(220, 560, 2.2, 40, ORANGE, seed=1) + sock(860, 640, 2.0, -60, GREEN, seed=2) + sock(250, 1400, 2.3, -120, PINK, seed=3)
             + sock(880, 1450, 2.1, 150, BLUE, seed=4) + towel(560, 1650, 520, 200, MINT, 5, 6))
    o.append(phone_flat(540, 980, 2.6, -6, bz, max(bz, .0 if t < tb[0] else .35), t))
    dx, dy, r = drift(t, .8)
    shake = 10 * bz * math.sin(t * 70)
    z = 1.0 + .05 * (t - a) + .06 * kick2(t, tb[0]) + .06 * kick2(t, tb[1])
    return view("".join(o), 540 + dx + shake, 980 + dy, z, r + 1.5 * bz)


def frame_s10(t):
    """«жужжит»: Дима вздрагивает, носки валятся из рук (оранжевый, розовый), телефон дрожит."""
    lib.DEFS.clear()
    a = T0("s10")
    tb = W(34)
    bz = buzz_env(t, [tb, W(35) + .2])
    e = "calm82" if t < tb else "wow82"
    o, f_ = sort_scene(t, "s10", hip=1150.0, k=1.15, expr=e, pose=("d82_hold", "recoil"), phone=(220, 1340, 1.0, bz, bz))
    wr = np.array(f_["wrist"]["n"])
    drops = []
    for i, (col, dx_) in enumerate(((ORANGE, -60), (PINK, 40), (BLUE, -10), (GREEN, 90))):
        if t < tb:
            drops.append(sock(wr[0] + dx_, wr[1] - 30 - 20 * i, 1.4, 60 * i, col, seed=70 + i))
        else:
            u = t - tb - .04 * i
            yy = wr[1] - 30 - 20 * i - 700 * max(0, u) + 4200 * max(0, u) ** 2 * .5
            if yy < 2100:
                drops.append(sock(wr[0] + dx_ * (1 + 3 * max(0, u)), yy, 1.4, 60 * i + 500 * max(0, u), col, seed=70 + i))
    o.append("".join(drops))
    o.append(phone_flat(220, 1340, 1.0, -8, bz, bz, t))
    dx, dy, r = drift(t, 1.0)
    jerk = 30 * kick2(t, tb, .03, .12)
    z = 1.0 + .03 * (t - a) + .08 * kick2(t, tb)
    return view("".join(o), 520 + dx + jerk, 1000 + dy - jerk * .5, z, r + 2.5 * kick2(t, tb))


def frame_s11(t):
    """«не берёт, просто слышит»: крупно, стопка белья на руке, глаза сползают на телефон; красный 5 выскальзывает из стопки."""
    lib.DEFS.clear()
    a = T0("s11")
    tb = W(39)
    bz = buzz_env(t, [tb, W(41)])
    look = (-.2, .2) if t < W(41) - .2 else (-.9, .8)
    o = [wall_bg(1500.0), win(-80, 260, 220, 640, 111)]
    f_ = dfig(600, 1500, 1.5, ex("squint82", look=look), "d82_hold", t=t, head_add=-.06 * smooth(W(41) - .2, W(41) + .2, t))
    o.append(f_["svg"])
    wr = np.array(f_["wrist"]["n"])
    sx, sy = wr[0] - 40, wr[1] - 20
    red = ""
    u = red_u(5, t)
    if u is not None:          # из середины стопки вниз, за нижний край кадра
        red = sock(sx - 40 - 120 * u, sy - 40 + 1600 * u * u + 200 * u, 1.9, 40 + 260 * u, RED, seed=5)
    stack = "".join(f'<g transform="translate({sx:.1f} {sy - 46 * i:.1f}) rotate({3 * math.sin(i + t * 2):.1f})">'
                    + shape(lib.rrect(-170, -24, 170, 24, 12), c, "", w=3.4, seed=120 + i) + "</g>" for i, c in enumerate((WHITE, BLUE, MINT, GRAY, GREEN)))
    o.append(red + stack)
    o.append(phone_flat(190, 1700, 1.6, -10, bz, bz, t))
    dx, dy, r = drift(t, 1.0)
    z = 1.02 + .04 * (t - a) + .06 * kick2(t, tb) + .05 * kick2(t, W(41))
    return view("".join(o), 520 + dx, 1050 + dy, z, r + 1.5 * kick2(t, tb))


# ═════════════════════════ s12–s14: Флорида ═════════════════════════
def palm(x, y, k, t, seed=0):
    o = [line([(x, y), (x + 20 * k, y - 200 * k), (x + 10 * k, y - 400 * k)], 22 * k, "#8a6a44", seed=seed)]
    for i in range(6):
        a = -2.6 + .52 * i + .06 * math.sin(t * 2 + i)
        tip = (x + 10 * k + 210 * k * math.cos(a), y - 400 * k + 150 * k * math.sin(a) + 60 * k)
        mid = (x + 10 * k + 110 * k * math.cos(a), y - 400 * k + 90 * k * math.sin(a) - 20 * k)
        o.append(shape([(x + 10 * k, y - 400 * k), mid, tip, (mid[0], mid[1] + 26 * k)], "#4f9e5e", "", w=3.0, seed=seed + i))
    return "".join(o)


def lab_window(x0, y0, x1, y1, t, red_id=None):
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    g = lib.lin_grad([(0, "#7cc4f0", 1), (1, "#e6f6ff", 1)])
    sky = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>',
           f'<circle cx="{x1 - 90}" cy="{y0 + 90}" r="54" fill="#ffd84a"/>',
           f'<rect x="{x0}" y="{y1 - 70}" width="{x1 - x0}" height="70" fill="#e9d9a6"/>',
           palm(x0 + 110, y1 - 40, .55, t, 7), palm(x0 + (x1 - x0) * .6, y1 - 30, .7, t, 17)]
    if red_id is not None:
        u = red_u(red_id, t)
        if u is not None:    # красный: ветер несёт за окном слева направо (виден только в стекле)
            sky.append(sock(x0 - 90 + (x1 - x0 + 180) * u, y0 + (y1 - y0) * (.35 + .12 * math.sin(u * 6)), 1.25, 360 * u, RED, seed=6))
    o = [f'<g clip-path="url(#{c})">{"".join(sky)}</g>', win_frame(x0, y0, x1, y1, 5)]
    return "".join(o)


def lab_wall():
    return (f'<rect x="-400" y="-400" width="1880" height="2720" fill="#e8f1ee"/>'
            + "".join(f'<rect x="{x}" y="-400" width="40" height="2720" fill="#d4e3df" opacity=".6"/>' for x in range(-400, 1480, 140)))


def desk(x, y, w, seed=0, paper=True):
    o = [shape(lib.rect_pts(x - w / 2, y, x + w / 2, y + 400), "#c49264", f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="26" fill="#d8aa78"/>', w=4.0, seed=seed)]
    if paper:
        o.append(shape(lib.T(lib.rrect(-70, -10, 70, 10, 3), x - 40, y + 8, 1.0, -4), "#ffffff", "", w=2.6, seed=seed + 1))
    return "".join(o)


SUBJ = ("stud82", "curly", "youth", "beard")


def subject(who, x, y, sc, t, expr=None, i=0):
    e = expr or {"brows": "calm", "mouth": "flat", "lid": .7, "look": (0.0, .6)}
    return PE.person(who, x, y + 3 * math.sin(t * 2 + i), sc, e, head_add=.03 * math.sin(t * 1.7 + i))


def frame_s12(t):
    lib.DEFS.clear()
    a = T0("s12")
    o = [lab_wall(), lab_window(330, 120, 750, 560, t)]
    for i, (who, x) in enumerate(zip(SUBJ, (180, 540, 900))):
        f_ = subject(who, x, 1180, .62, t, i=i)
        o.append(f_["svg"])
        o.append(desk(x, 1150, 330, seed=130 + 3 * i))
        o.append(bulb(f_["head"][0] + 10, f_["head"][1] - 190, .6, 1.0, t + i, seed=140 + i))
    u = ease_io(clamp((t - a) / (T1("s12") - a)))
    z = 1.25 + (1.0 - 1.25) * u
    dx, dy, r = drift(t, .6)
    return view("".join(o), 540 + dx, 760 + 140 * u + dy, z, r, bg="#e8f1ee")


def frame_s13(t):
    """Один испытуемый крупно: жужжит телефон на столе, лампочка мигает и тускнеет; красный 6 за окном."""
    lib.DEFS.clear()
    a = T0("s13")
    tb = W(48)
    bz = buzz_env(t, [tb, tb + .7])
    on = 1.0 if t < tb else (.35 + .65 * (1 - smooth(tb, W(49) + .2, t))) * (.6 + .4 * (math.sin((t - tb) * 40) > 0))
    o = [lab_wall(), lab_window(40, 160, 460, 640, t, red_id=6)]
    f_ = subject("stud82", 560, 1450, 1.0, t, {"brows": "up" if t > tb else "calm", "mouth": "flat", "lid": .9, "look": (-.6, .8) if t > tb else (0, .6)})
    o.append(f_["svg"])
    o.append(bulb(f_["head"][0] + 10, f_["head"][1] - 300, 1.0, on, t, seed=150))
    o.append(desk(560, 1420, 900, seed=151))
    o.append(phone_flat(330, 1500, 1.1, -10, bz, bz, t))
    dx, dy, r = drift(t, 1.0)
    z = 1.0 + .04 * (t - a) + .07 * kick2(t, tb)
    return view("".join(o), 540 + dx, 1000 + dy, z, r + 1.5 * kick2(t, tb))


def frame_s14(t):
    """Двое: у левого уведомление, у правого звонок — обе лампочки гаснут почти одинаково."""
    lib.DEFS.clear()
    a = T0("s14")
    tl, tr = W(51), W(53)
    bl = buzz_env(t, [tl])
    br = buzz_env(t, [tr, tr + .5, tr + 1.0], .5) * 1.0
    o = [lab_wall()]
    for i, (who, x, tb, bz, lvl) in enumerate((("curly", 290, tl, bl, .3), ("youth", 800, tr, br, .25))):
        on = 1.0 - (1 - lvl) * smooth(tb + .15, tb + .5, t)
        f_ = subject(who, x, 1300, .78, t, {"brows": "up" if t > tb else "calm", "mouth": "flat", "lid": .85, "look": (0, .8)}, i=i)
        o.append(f_["svg"])
        o.append(bulb(f_["head"][0] + 10, f_["head"][1] - 240, .8, on, t + i, seed=160 + i))
        o.append(desk(x, 1280, 470, seed=165 + 3 * i))
        o.append(phone_flat(x - 60, 1360, .85 if i == 0 else 1.0, -8, bz * (1.0 if i == 0 else 1.4), bz, t))
    o.append(line([(545, 900), (545, 1700)], 5, "#c9d6d2", seed=169))
    dx, dy, r = drift(t, .8)
    z = 1.0 + .03 * (t - a) + .05 * kick2(t, tr) + .05 * kick2(t, W(54))
    return view("".join(o), 540 + dx, 1000 + dy, z, r)


def frame_s15(t):
    """Дима не трогает телефон, а лампочка над его головой всё равно тускнеет."""
    lib.DEFS.clear()
    a = T0("s15")
    tb = W(57)
    bz = buzz_env(t, [tb, tb + .6])
    on = 1.0 - .65 * smooth(W(61) - .1, W(61) + .3, t)
    o, f_ = sort_scene(t, "s15", hip=1150.0, k=1.05, expr="calm82" if t < W(61) else "puzzled82", phone=(200, 1330, 1.0, bz, bz), bulb_on=on,
                       look=(0, .5))
    dx, dy, r = drift(t, .8)
    z = 1.05 + .05 * (t - a) + .06 * kick2(t, W(61))
    return view("".join(o), 540 + dx, 950 + dy, z, r)


def frame_s16(t):
    """Бросает носок в корзину «готово» (красный 7: из-за кучи белья слева — за край корзины справа) и тянется к телефону."""
    lib.DEFS.clear()
    a = T0("s16")
    reach = smooth(W(66) - .3, W(66) + .2, t)
    pose = ("place74", "d82_hold") if reach <= 0 else ("d82_hold", "offer")
    o, f_ = sort_scene(t, "s16", hip=1130.0, k=1.0, expr="sure82", pose=pose, phone=None)
    o.append(phone_flat(760 - 200 * reach, 1330 - 120 * reach, 1.0, -8 + 20 * reach, 0.0, 0.0, t))
    red = ""
    u = red_u(7, t)
    if u is not None:
        red = sock(150 + 760 * u, 1500 - 520 * math.sin(math.pi * u) + 260 * u, 1.6, 400 * u, RED, seed=7)
    o.append(basket_back(900, 1560, 1.15) + heap(900, 1552, 1.0, seed=44, n=7) + red + basket_front(900, 1560, 1.15, seed=45))
    o.append(towel(130, 1560, 420, 230, BLUE, 47, -6) + towel(170, 1450, 380, 160, WHITE, 48, 4))
    dx, dy, r = drift(t, 1.0)
    z = .98 + .04 * (t - a) + .05 * kick2(t, W(66))
    return view("".join(o), 540 + dx, 1050 + dy, z, r)


def bell(x, y, k, cross, pop):
    o = [f'<circle cx="0" cy="0" r="120" fill="#ffffff" stroke="{INK}" stroke-width="6"/>',
         shape([(-52, 40), (-46, -10), (-30, -48), (0, -62), (30, -48), (46, -10), (52, 40), (66, 54), (-66, 54)], "#ffcf3a", "", w=4.0, seed=171),
         f'<circle cx="0" cy="70" r="16" fill="#ffcf3a" stroke="{INK}" stroke-width="4"/>']
    if cross > 0:
        L = 170 * cross
        o.append(f'<line x1="-80" y1="-80" x2="{-80 + L / 1.414:.1f}" y2="{-80 + L / 1.414:.1f}" stroke="#ffffff" stroke-width="30" stroke-linecap="round"/>'
                 f'<line x1="-80" y1="-80" x2="{-80 + L / 1.414:.1f}" y2="{-80 + L / 1.414:.1f}" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>')
    s = pop
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({k * s:.3f})">{"".join(o)}</g>'


def frame_s17(t):
    """Рука кладёт телефон экраном вниз на «вниз»; на «выключает звук» колокольчик перечёркнут."""
    lib.DEFS.clear()
    a = T0("s17")
    tf, tv, ts = W(69), WE(70), W(72)
    o = [f'<rect x="-300" y="-300" width="1680" height="2520" fill="#b78a5c"/>']
    o += [line([(-300, y), (1400, y + 40)], 4, "#9c7448", seed=y) for y in range(-200, 2200, 140)]
    o.append(sock(200, 500, 2.2, 30, BLUE, seed=1) + sock(880, 560, 2.0, -40, ORANGE, seed=2) + sock(860, 1500, 2.2, 120, GREEN, seed=3)
             + towel(220, 1520, 420, 200, MINT, 4, -8))
    fl = smooth(tf, tv, t)                # 0 — экраном вверх, 1 — вниз
    lift = math.sin(math.pi * fl)
    bz = buzz_env(t, [a + .25]) * (1 - fl)
    sx = math.cos(math.pi * fl)
    ph = phone_flat(0, 0, 1.0, 0, bz, .35 * (1 - fl), t, back=fl > .5)
    o.append(f'<g transform="translate(540 {1000 - 80 * lift:.1f}) scale({2.5 * (1 + .12 * lift) * max(abs(sx), .04):.3f} {2.5 * (1 + .12 * lift):.3f})">{ph}</g>')
    # рука: из правого нижнего угла к телефону и обратно
    hin = smooth(tf - .5, tf - .1, t) * (1 - smooth(tv + .15, tv + .5, t))
    hx, hy = 1250 - 520 * hin, 1600 - 420 * hin
    o.append(shape(lib.T(lib.rrect(-60, -90, 500, 90, 80), hx, hy, 1.0, 35), "#d4a23e", "", w=4.0, seed=181))
    o.append(shape(lib.T(lib.rrect(-120, -80, 60, 80, 60), hx, hy, 1.0, 35), "#ecc4a2",
                   line([(-90, -30), (-20, -40)], 2.6, "#bf8a74") + line([(-90, 20), (-20, 10)], 2.6, "#bf8a74"), w=4.0, seed=182))
    pop = back_out(clamp((t - ts) / .3)) if t >= ts else 0
    if pop > 0:
        o.append(bell(540, 520, 1.2, ease_out(clamp((t - W(73)) / .25)), pop))
        o.append(burst(540, 520, 220, W(73), t, "#ffd23f", 12, .4))
    dx, dy, r = drift(t, .8)
    z = 1.0 + .03 * (t - a) + .07 * kick2(t, tv) + .05 * kick2(t, W(73))
    return view("".join(o), 540 + dx, 980 + dy, z, r + 1.5 * kick2(t, tv))


def frame_s18(t):
    """Петля к хуку: та же комната и ракурс, Дима спокойно раскладывает пары носков; на «сколько» камера на корзину."""
    lib.DEFS.clear()
    a = T0("s18")
    s, gy = 1.25, 1350.0
    cam0 = ((540 - 300) / s, (960 - gy) / s, s, 0.0)
    push = ease_io(clamp((t - W(76) + .1) / .5))
    cx = cam0[0] + (650 - cam0[0]) * push
    cy = cam0[1] + (-200 - cam0[1]) * push
    sc = s + (2.0 - s) * push
    u = .5 + .5 * math.sin((t - a) * 4)
    f_ = dfig(170, -410, .62, ex("sure82"), ("place74", "d82_hold"), t=t, u=u)
    o = [room_b(), f_["svg"], coffee_table(-120, 470, seed=21)]
    for i, col in enumerate((BLUE, GREEN, ORANGE, PINK)):
        x = -40 + 135 * i
        o.append(sock(x - 18, -185, .9, -8, col, seed=200 + i) + sock(x + 18, -185, .9, 8, col, seed=210 + i))
    o.append(basket_back(650, -150, .9) + heap(650, -158, .8, seed=55, n=7) + basket_front(650, -150, .9, seed=57))
    dx, dy, r = drift(t, .5)
    return view("".join(o), cx + dx, cy + dy, sc, r, bg=WALL)


def frame(sid, t):
    lib.INK_K[0] = 1.0
    return globals()["frame_" + sid](t)
