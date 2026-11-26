"""Рилс 130 «Навигатор по делу», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json (общая дорожка voice_merge.py: навигатор Алиса, Дима male2, кот Даниил).
Навигатор — экран с планом квартиры: кухня с холодильником, диван, стол с флажком «ДЕЛО»; синий маршрут, стрелка «100 м».
Кот в кепке водителя (costume.py, внутри рисунка кота) во всех планах, с 33-го слова — за рулём игрушечной машинки.
Призыв — TG-карточка v5 (scripts/story_cta_tg.py). NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people, COMMON  # noqa: E402
import room as RM  # noqa: E402
import costume as CO  # noqa: E402
import story_cta_tg as TG  # noqa: E402

CO.install(CT)
HIT = stress(3, .4)
NAVY, ROUTE, ROUTE_SH = "#1f2a44", "#2f8fe0", "#1d5fa8"


# ═════════════ экран навигатора ═════════════
FRIDGE_P, SOFA_P, DESK_P, START_P = (-190, -190), (-170, 210), (180, -100), (20, 340)
ROUTE_DESK = [START_P, (20, 40), (180, 40), (180, -60)]


def _path(pts, col, w, op=1.0, dash=""):
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" '
            f'opacity="{op:.3f}" {dash}/>')


def _partial(pts, u):
    """Первые u (0…1) длины ломаной."""
    if u >= 1:
        return list(pts)
    L = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    tot, acc, out = sum(L) * u, 0.0, [pts[0]]
    for (a, b), l_ in zip(zip(pts, pts[1:]), L):
        if acc + l_ >= tot:
            f = (tot - acc) / l_ if l_ else 0
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
            return out
        out.append(b)
        acc += l_
    return out


def route(pts, u=1.0, col=ROUTE, sh=ROUTE_SH):
    p = _partial(pts, clamp(u))
    if len(p) < 2:
        return ""
    return _path(p, sh, 30) + _path(p, col, 20)


def map_icons(t, flag_u=1.0, finish_sofa=0.0, pin_sofa=0.0):
    o = []
    # стены квартиры
    for a, b in (((-300, -60), (-60, -60)), ((-60, -60), (-60, -400)), ((60, 80), (300, 80)), ((-300, 80), (-100, 80)), ((60, 80), (60, -120))):
        o.append(line([a, b], 9, "#8a93a6", taper=0, wmin=1, seed=13100 + int(a[0])))
    # холодильник
    fx, fy = FRIDGE_P
    o.append(shape(lib.rrect(fx - 44, fy - 70, fx + 44, fy + 70, 10), "#ffffff", line([(fx - 44, fy - 20), (fx + 44, fy - 20)], 3, seed=13110),
                   w=3.4, seed=13111))
    # диван
    sx, sy = SOFA_P
    o.append(shape(lib.rrect(sx - 100, sy - 40, sx + 100, sy + 40, 16), "#4a6fa5", blob(lib.rrect(sx - 80, sy - 20, sx + 80, sy + 30, 10), "#6a8fc5"),
                   w=3.4, seed=13112))
    # стол и флажок «ДЕЛО»
    dx_, dy_ = DESK_P
    o.append(shape(lib.rect_pts(dx_ - 80, dy_ - 30, dx_ + 80, dy_ + 40), "#b07a48", shape(lib.rect_pts(dx_ - 40, dy_ - 20, dx_ + 40, dy_ + 20), "#2a2d36", "",
                                                                                          w=2, seed=13113), w=3.4, seed=13114))
    if flag_u > .02:
        s = lib.back_out(clamp(flag_u), 2.0)
        fl = line([(0, 0), (0, -150)], 7, taper=0, wmin=1, seed=13115)
        fl += shape([(0, -150, 1), (170, -150, 1), (150, -112), (170, -76, 1), (0, -76, 1)], "#e2453a", "", w=3.4, seed=13116)
        fl += plain("ДЕЛО", 80, -98, 38, fill="#ffffff", anchor="middle")
        o.append(f'<g transform="translate({dx_ - 40} {dy_ - 10}) scale({s:.3f})">{fl}</g>')     # флажок целиком на экране
    if finish_sofa > .02:
        s = lib.back_out(clamp(finish_sofa), 2.0)
        ch = ""
        for i in range(4):
            for j in range(2):
                if (i + j) % 2 == 0:
                    ch += f'<rect x="{i * 36}" y="{-150 + j * 36}" width="36" height="36" fill="#111"/>'
        fl = line([(0, 0), (0, -150)], 7, taper=0, wmin=1, seed=13117)
        fl += f'<rect x="0" y="-150" width="144" height="72" fill="#fff" stroke="#111" stroke-width="4"/>' + ch
        o.append(f'<g transform="translate({sx + 30} {sy - 20}) scale({s:.3f})">{fl}</g>')
    return "".join(o)


def you_marker(x, y, ang=0.0, s=1.0):
    m = shape([(0, -34, 1), (26, 26, 1), (0, 12, 1), (-26, 26, 1)], "#ffffff", "", w=4, seed=13120)
    m = f'<circle r="44" fill="{ROUTE}" opacity=".25"/>' + m
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">{m}</g>'


def banner(kind, t, u=1.0):
    """Верхняя плашка навигатора: turn — зелёная «↱ 100 м», off — красная «Вы отклонились», re — серая «Перестраиваю маршрут»
    со значком, arrive — «Вы прибыли», straight — «↑ 2 мин»."""
    if u <= .02:
        return ""
    col = {"turn": "#2a9a5a", "off": "#d8352a", "re": "#5a6372", "arrive": "#2a9a5a", "straight": "#2a9a5a"}[kind]
    o = [shape(lib.rrect(-310, -420, 310, -300, 22), col, "", w=4, seed=13130)]
    if kind == "turn":
        o.append(line([(-250, -320), (-250, -380), (-180, -380)], 14, "#ffffff", taper=0, wmin=1, seed=13131))
        o.append(shape([(-180, -400, 1), (-150, -380, 1), (-180, -360, 1)], "#ffffff", "", w=2, seed=13132))
        o.append(plain("100 м", -110, -342, 64, fill="#ffffff"))
    elif kind == "straight":
        o.append(line([(-230, -315), (-230, -395)], 14, "#ffffff", taper=0, wmin=1, seed=13133))
        o.append(shape([(-252, -385, 1), (-230, -412, 1), (-208, -385, 1)], "#ffffff", "", w=2, seed=13134))
        o.append(plain("2 мин", -160, -342, 64, fill="#ffffff"))
    elif kind == "off":
        o.append(plain("Вы отклонились", 0, -342, 52, fill="#ffffff", anchor="middle"))
    elif kind == "arrive":
        o.append(plain("Вы прибыли", 0, -342, 58, fill="#ffffff", anchor="middle"))
    else:
        a = t * 420
        o.append(f'<g transform="translate(-250 -360) rotate({a:.1f})">' + _path([(0, -26), (22, -12), (26, 10), (12, 24)], "#ffffff", 8)
                 + shape([(10, 32, 1), (24, 14, 1), (2, 14, 1)], "#ffffff", "", w=1, seed=13135) + "</g>")
        o.append(plain("Перестраиваю", -200, -342, 50, fill="#ffffff"))
    s = .7 + .3 * lib.back_out(clamp(u), 2.0)
    return f'<g transform="translate(0 -360) scale({s:.3f}) translate(0 360)">{"".join(o)}</g>'


def navigator(x, y, k, t, inner="", shake_=0.0, rot=0.0):
    """Корпус навигатора (центр экрана (x, y)), экран 640×860; inner — карта, маршрут, плашки в координатах экрана."""
    o = [shape(lib.rrect(-350, -470, 350, 470, 50), "#22252c", blob(lib.rrect(-340, -460, -300, 460, 30), "#3a3e48", .7), w=6, seed=13140)]
    c = lib.clip_rect(-320, -430, 640, 860, 22)
    o.append(shape(lib.rrect(-320, -430, 320, 430, 22), "#e9eef4", "", w=3, seed=13141))
    grid = "".join(line([(-320, -430 + 80 * j), (320, -430 + 80 * j)], 2, "#d6dde6", taper=0, wmin=1, seed=13142 + j) for j in range(12))
    grid += "".join(line([(-320 + 80 * j, -430), (-320 + 80 * j, 430)], 2, "#d6dde6", taper=0, wmin=1, seed=13160 + j) for j in range(9))
    o.append(f'<g clip-path="url(#{c})">{grid}{inner}</g>')
    o.append(shape(ellipse_pts(0, 450, 16, 6, 10), "#4a4e58", "", w=2, seed=13180))
    dx = 10 * shake_ * math.sin(t * 50)
    return tf("".join(o), x + dx, y, k, rot + 3 * shake_ * math.sin(t * 37))


# ═════════════ квартира ═════════════
def fridge(x, y, u, t, k=1.0):
    """Холодильник (x, y — центр низа), дверь на петлях слева открывается к нам на u; внутри полки и лампочка."""
    w, h = 260, 900
    o = [blob(ellipse_pts(0, 6, 290, 20, 16), "#000000", .18)]
    inner = ""
    if u > .01:
        g = lib.lin_grad([(0, "#e6f3ff", 1), (1, "#b9d6ec", 1)], 0, 0, 0, 1)
        inner += f'<rect x="{-w + 24}" y="{-h + 24}" width="{2 * w - 48}" height="{h - 48}" fill="url(#{g})"/>'
        for j in range(3):
            yy = -h + 260 + 210 * j
            inner += line([(-w + 30, yy), (w - 30, yy)], 6, "#9fb8cc", taper=0, wmin=1, seed=13200 + j)
        inner += shape(lib.rrect(-120, -h + 330, -20, -h + 460, 14), "#f3d36b", "", w=3, seed=13204)
        inner += shape(ellipse_pts(80, -h + 410, 60, 46, 14), "#e2453a", "", w=3, seed=13205)
        inner += shape(lib.rrect(-160, -h + 560, 60, -h + 670, 18), "#f4f1ea", "", w=3, seed=13206)
        inner += PR.glow(0, -h + 120, 240, .8 * u, "#ffffff")
    o.append(shape(lib.rrect(-w, -h, w, 0, 30), "#f4f6f8", inner, w=5, seed=13210))
    leaf = shape(lib.rrect(-w, -h, w, 0, 30), "#fbfcfd", blob(lib.rect_pts(w - 40, -h, w, 0), "#d9dee4", .8)
                 + line([(-w + 10, -h + 320), (w - 10, -h + 320)], 4, "#c9ced6", taper=0, wmin=1, seed=13211), w=5, seed=13212)
    leaf += shape(lib.rrect(w - 70, -h + 360, w - 44, -h + 600, 10), "#c9ced6", "", w=3, seed=13213)
    sx = 1 - 1.75 * ease_io(clamp(u))
    o.append(f'<g transform="translate({-w} 0) scale({sx:.4f} 1) translate({w} 0)">{leaf}'
             + (f'<rect x="{-w}" y="{-h}" width="{2 * w}" height="{h}" fill="#000" opacity="{.3 * u:.3f}"/>' if u > .01 else "") + "</g>")
    return tf("".join(o), x, y, k)


def home(t, wall="#eadccb"):
    o = [plain_room(t, wall=wall)]
    o.append(rug(540, RFL + 150, 600, "#8fb3c9", "#a9c7d9"))
    return o


def mini_nav(x, y, k, t, kind="turn"):
    inner = map_icons(t) + route(ROUTE_DESK) + you_marker(*START_P) + banner(kind, t)
    return navigator(x, y, k, t, inner)


def dima_walk(x, t, k=.7, phase=None, expr="calm82", hold=None, sandwich=False, flip=False):
    """Дима идёт вправо; hold — (dx, dy) ближней руки от таза (держит навигатор/телефон)."""
    wk = people.walk_kw(x, RFL - (people.LEG_LEN - 12) * k - 6, k, (t * 1.6) % 1 if phase is None else phase)
    hx, hy = wk["hip"]
    arms = {"f": ("ang", .18 + .3 * math.sin(2 * math.pi * (t * 1.6)), .25)}
    if hold:
        arms["n"] = ("ik", (hx + hold[0] * k, hy + hold[1] * k), -1)
    f = people.dima82(hx, hy, k, expr, "d82_rest", t=t, feet=wk["feet"], arms=arms, sandwich=sandwich, flip=flip, lean_add=.04)
    f["handpt"] = (hx + hold[0] * k, hy + hold[1] * k) if hold else None
    return f


def toy_car(x, y, k, t, cat_st=None, drive=0.0, cat_in=1.0, wheel_turn=0.0):
    """Игрушечная машинка: кот в кепке за рулём (видно по грудь), колёса крутятся при drive. (x, y) — земля под машинкой."""
    o = []
    spin = t * 600 * drive
    if cat_in > .02:
        st = dict(dict(look=(.5, -.1), smile=1.0, tail=10 * math.sin(t * 3)), **(cat_st or {}))
        o.append(CT.draw(x - 40 * k, y - 120 * k - 30 * k * (1 - cat_in), .75 * k, st, t))
    body = shape([(-260, -40, 1), (-250, -170), (-150, -200), (210, -200), (270, -150), (280, -40, 1)], "#e2453a",
                 blob([(-240, -190), (260, -190), (270, -150), (-250, -150)], "#ff6a5a", .7), w=5, seed=13300)
    body += shape(ellipse_pts(240, -120, 22, 18, 10), "#fff1b0", "", w=3, seed=13301)
    o.append(tf(body, x, y, k))
    # руль: стойка и обод перед котом
    wx, wy = x + 70 * k, y - 250 * k
    o.append(line([(x + 40 * k, y - 190 * k), (wx, wy)], 10 * k, "#2a2c30", taper=0, wmin=1, seed=13302))
    o.append(f'<g transform="translate({wx:.1f} {wy:.1f}) rotate({wheel_turn:.1f}) scale({k:.3f})">'
             + f'<ellipse rx="70" ry="26" fill="none" stroke="#2a2c30" stroke-width="14"/>' + line([(-60, 0), (60, 0)], 8, "#2a2c30", seed=13303) + "</g>")
    for wxx in (-170, 180):
        o.append(tf(shape(ellipse_pts(0, 0, 62, 62, 20), "#2a2c30", blob(ellipse_pts(0, 0, 26, 26, 12), "#9aa0aa"), w=4, seed=13304 + wxx)
                    + line([(-22, 0), (22, 0)], 5, "#5a5f6e", seed=13306), x + wxx * k, y - 40 * k, k, spin))
    return "".join(o)


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: экран навигатора — план квартиры, маршрут к «ДЕЛО», стрелка «100 м»; кот в кепке водителя смотрит на экран."""
    inner = map_icons(t, flag_u=ease_out(clamp((t + .2) / .3))) + route(ROUTE_DESK, ease_io(clamp((t + .4) / .9))) + you_marker(*START_P) + banner("turn", t)
    o = [home(t)[0]]
    o.append(navigator(500, 1160, .92, t, inner, rot=-3))
    o.append(CT.draw(890, 1820, 1.0, dict(look=(-.8, -.6), perk=1.0, tail=10 * math.sin(t * 3)), t))
    dx, dy = shake(t, HIT, 10)
    return hook_view("".join(o), t, HIT, 540, 1160, 1.0, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«поверните к делу»: Дима идёт с навигатором в руке; справа стол с ноутбуком, слева холодильник; кот в кепке у стола."""
    a, b = T0("s02"), T1("s02")
    o = home(t)
    o.append(fridge(80, RFL, 0.0, t, .9))
    o.append(PR.desk(860, RFL - 330, w=440, depth=90, leg_h=330, seed=7))
    o.append(PR.laptop(860, RFL - 338, .8, screen="lines", lines=.0, t=t, seed=1))
    o.append(CT.draw(1010, RFL - 330, .55, dict(look=(-.8, -.1), smile=.8), t))
    x = 400 + 120 * (t - a)
    f = dima_walk(x, t, hold=(220, -260), expr="calm82")
    o.append(f["svg"])
    hx, hy = f["handpt"]
    o.append(mini_nav(hx + 40, hy - 70, .2, t))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1080, 1.0 + .05 * u, 0, t=t)


def frame_s03(t):
    """«Я повернул к холодильнику»: Дима распахивает холодильник, свет в лицо, навигатор в другой руке."""
    a, b = T0("s03"), T1("s03")
    t_open = W(8)
    u = ease_out(ramp(t, t_open, .35))
    o = home(t, wall="#dfe8e0")
    o.append(fridge(380, RFL, u, t, 1.0))
    k = .72
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(830, hip, k, "wow82" if u > .5 else "calm82", "d82_rest", t=t, feet="stand", flip=True, head_add=-.04 * u,
                      arms={"n": ("ik", (700, hip - 150), -1)})
    o.append(f["svg"])
    o.append(PR.glow(560, 900, 380, .5 * u, "#ffffff"))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_open + .1, 8)
    return view("".join(o), 600 + dx, 1100 + dy, 1.02 + .08 * uu, 0, t=t)


def nav_shot(t, inner, sh=0.0, zoom=1.2, cx=540, cy=1080):
    a = t
    o = [home(t)[0]]
    o.append(navigator(540, 1080, 1.0, t, inner, shake_=sh))
    return o


def frame_s04(t):
    """«Вы отклонились от маршрута»: точка уходит с маршрута к холодильнику, маршрут бледнеет, красная плашка."""
    a, b = T0("s04"), T1("s04")
    off = ease_io(ramp(t, a, .9))
    yx = START_P[0] + (FRIDGE_P[0] + 30 - START_P[0]) * off
    yy = START_P[1] + (FRIDGE_P[1] + 120 - START_P[1]) * off
    inner = map_icons(t) + f'<g opacity="{1 - .6 * off:.3f}">{route(ROUTE_DESK)}</g>' + _path([START_P, (yx, yy)], "#d8352a", 10, dash='stroke-dasharray="20 14"')
    inner += you_marker(yx, yy, -40 * off) + banner("off", t, ramp(t, W(11) - .1, .2))
    o = nav_shot(t, inner, sh=bump(t, W(11), .05, .4))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(11), 8)
    return view("".join(o), 540 + dx, 1010 + dy, 1.3 + .06 * u, 0, t=t)


def rebuild_inner(t, u, tangle=0.0, mx=None):
    """Маршрут перестраивается: от холодильника петлями; tangle — клубок."""
    p0 = (FRIDGE_P[0] + 30, FRIDGE_P[1] + 120)
    pts = [p0, (-60, 0), (100, 120), (-120, 140), (60, -40), (180, 40), (180, -60)]
    if tangle > 0:
        pts = [p0]
        for j in range(26):
            a_ = j * 1.1 + t * 2
            r = 90 + 60 * math.sin(j * 1.7)
            pts.append((-10 + r * math.cos(a_) * (.6 + .4 * tangle), 40 + r * math.sin(a_) * (.6 + .4 * tangle)))
    inner = map_icons(t) + route(pts, u)
    inner += you_marker(*p0, ang=-40)
    return inner


def frame_s05(t):
    """«Перестраиваю маршрут»: значок крутится, маршрут рисуется заново петлями."""
    a, b = T0("s05"), T1("s05")
    inner = rebuild_inner(t, ease_io(ramp(t, a + .1, 1.2))) + banner("re", t)
    o = nav_shot(t, inner)
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1010, 1.3 + .06 * u, 0, t=t)


def frame_s06(t):
    """«А по пути открыл ленту»: Дима идёт с бутербродом во рту и листает ленту в телефоне."""
    a, b = T0("s06"), T1("s06")
    o = home(t)
    o.append(fridge(120, RFL, 1.0, t, .9))
    x = 480 + 120 * (t - a)
    f = dima_walk(x, t, hold=(230, -230), expr=dict(people.EXPR["dima"]["calm82"], look=(.6, .6)), sandwich=True)
    o.append(f["svg"])
    hx, hy = f["handpt"]
    hy += 150
    sc = ((t - a) * 300) % 60
    feed = "".join(shape(lib.rrect(-50, -100 + 50 * j - sc, 50, -64 + 50 * j - sc, 6), ["#9fc2e8", "#ffd27a", "#d6c7f0", "#9fe0a4"][j % 4], "", w=2,
                         seed=13400 + j) for j in range(6))
    c = lib.clip_rect(-60, -112, 120, 224, 12)
    o.append(mini_phone(hx + 30, hy - 60, .9, -12, screen="#2f3a55", inner=f'<g clip-path="url(#{c})">{feed}</g>'))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(20), 6)
    return view("".join(o), 600 + dx, 1000 + dy, 1.25 + .05 * u, 0, t=t)


def frame_s07(t):
    """«всего на минутку»: Дима присел на подлокотник дивана и листает ленту; облачко с бегущей лентой."""
    a, b = T0("s07"), T1("s07")
    o = home(t)
    sf = RM.sofa(600, RFL, 1.0)
    o.append(sf["back"])
    x, k = 360.0, .7
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    f = people.dima82(x, RFL - 330, k, dict(people.EXPR["dima"]["calm82"], look=(.6, .7)), "sit_desk", t=t, feet=feet,
                      arms={"n": ("ik", (x + 190, RFL - 440), -1), "f": ("ik", (x + 160, RFL - 430), -1)})
    o.append(f["svg"])
    sc = ((t - a) * 400) % 60
    feed = "".join(shape(lib.rrect(-50, -100 + 50 * j - sc, 50, -64 + 50 * j - sc, 6), ["#9fc2e8", "#ffd27a", "#d6c7f0", "#9fe0a4"][j % 4], "", w=2,
                         seed=13410 + j) for j in range(6))
    c = lib.clip_rect(-60, -112, 120, 224, 12)
    o.append(mini_phone(x + 200, RFL - 470, .85, 8, screen="#2f3a55", inner=f'<g clip-path="url(#{c})">{feed}</g>'))
    o.append(sf["arm_r"])
    o.append(CT.draw(900, RFL - 300, .6, dict(look=(-.9, -.4), turn=-.3), t))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(23), 6)
    return view("".join(o), 580 + dx, 1100 + dy, 1.2 + .06 * u, 0, t=t)


def frame_s08(t):
    """«Перестраиваю маршрут»: маршрут петляет по всей квартире."""
    a, b = T0("s08"), T1("s08")
    inner = rebuild_inner(t, .6 + .4 * ramp(t, a, .8), tangle=.4 * ramp(t, a, b - a)) + banner("re", t)
    o = nav_shot(t, inner, sh=.3)
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1010, 1.3 + .06 * u, 3 * u, t=t)


def frame_s09(t):
    """«Перестраиваю маршрут»: маршрут спутался в клубок, навигатор трясётся."""
    a, b = T0("s09"), T1("s09")
    inner = rebuild_inner(t, 1.0, tangle=.4 + .6 * ramp(t, a, b - a)) + banner("re", t)
    o = nav_shot(t, inner, sh=.8)
    o.append(PR.sweat(860, 640, 1.3, 20))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(26), 8)
    return view("".join(o), 540 + dx, 1010 + dy, 1.3 + .08 * u, -3 * u, t=t)


def frame_s10(t):
    """«Вы прибыли»: маршрут ведёт на диван, на значке дивана клетчатый флаг финиша."""
    a, b = T0("s10"), T1("s10")
    p = [(-60, 40), (-120, 120), (-170, 200)]
    inner = map_icons(t, finish_sofa=ramp(t, W(29) - .1, .25)) + route(p) + you_marker(-170, 200, -30) + banner("arrive", t)
    o = nav_shot(t, inner)
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1010, 1.3 + .08 * u, 0, t=t)


def pin(x, y, txt, u, size=50):
    if u <= .02:
        return ""
    s = lib.back_out(clamp(u), 2.0)
    w = big_w(txt, size) + 70
    body = shape([(0, 0, 1), (-40, -70), (-w / 2, -70), (-w / 2, -170), (w / 2, -170), (w / 2, -70), (40, -70)], "#d8352a", "", w=4, seed=13500)
    body += plain(txt, 0, -102, size, fill="#ffffff", anchor="middle")
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{body}</g>'


def big_w(txt, size):
    import big_title
    return big_title.text_w(txt, size) * .92


def frame_s11(t):
    """«Пункт назначения: диван»: Дима развалился на диване с телефоном, над диваном метка навигатора «ДИВАН»."""
    a, b = T0("s11"), T1("s11")
    o = home(t)
    sf = RM.sofa(540, RFL, 1.0)
    o.append(sf["back"])
    x, k = 420.0, .7
    feet = {"n": ((x + 250 * k, RFL - 10), .2), "f": ((x + 200 * k, RFL - 16), .2)}
    f = people.dima82(x, RFL - 320, k, dict(people.EXPR["dima"]["calm82"], look=(.5, .7)), "sit_desk", t=t, feet=feet, lean_add=-.25,
                      arms={"n": ("ik", (x + 170, RFL - 540), -1), "f": ("ik", (x + 140, RFL - 530), -1)})
    o.append(f["svg"])
    o.append(mini_phone(x + 200, RFL - 540, .85, 14, screen="#9fc7ff"))
    o.append(sf["arm_r"])
    o.append(pin(800, RFL - 600, "ДИВАН", ramp(t, W(32) - .1, .3), 60))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(32), 8)
    return view("".join(o), 560 + dx, 1100 + dy, 1.15 + .06 * u, 0, t=t)


def frame_s12(t):
    """«Тогда за руль сел котик»: кот в кепке водителя запрыгивает в игрушечную машинку, хватает руль; на руле навигатор."""
    a, b = T0("s12"), T1("s12")
    o = home(t)
    j = ease_out(ramp(t, W(35) - .3, .45))
    cx, cy = 560, RFL + 40
    o.append(toy_car(cx, cy, 1.0, t, dict(look=(.4, -.2), smile=1.0 if j >= 1 else .4, legs=0.0), cat_in=1.0 if j >= 1 else 0.0,
                     wheel_turn=20 * math.sin(t * 5) * j))
    if j < 1:
        x = 900 + (cx - 40 - 900) * j
        y = RFL - 300 * math.sin(math.pi * j) + (cy - 120 - RFL) * j
        o.append(CT.draw(x, y, .75, dict(look=(-.7, .2), legs=1 - j, perk=1.0), t))
    o.append(navigator(cx + 300, cy - 420, .3, t, map_icons(t) + route(ROUTE_DESK) + you_marker(*START_P)))
    o.append(line([(cx + 120, cy - 260), (cx + 300, cy - 300)], 8, "#2a2c30", taper=0, wmin=1, seed=13510))
    f = stand(170, t, "wow82", "d82_rest")
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(35) + .15, 8)
    return view("".join(o), 560 + dx, 1180 + dy, 1.05 + .06 * u, 0, t=t)


def frame_s13(t):
    """Кот: «Маршрут построен» — лапа кота жмёт экран, прямая линия от дивана к «ДЕЛО»."""
    a, b = T0("s13"), T1("s13")
    p = [(-170, 200), (180, -60)]
    inner = map_icons(t) + route(p, ease_io(ramp(t, W(39), .5))) + you_marker(-170, 200, 40)
    o = nav_shot(t, inner)
    tap = bump(t, W(38) + .1, .08, .3)
    o.append(CT.draw(880, 1640, 1.05, dict(look=(-.9, -.6), smile=1.0, paw=.9 + .1 * tap, paw_dx=-120, perk=1.0), t))
    o.append(PR.sparkles(540, 1080, 1.6, bump(t, W(39), .05, .5), t, seed=131, n=6, r=260))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 620, 1180, 1.05 + .06 * u, 0, t=t)


def frame_s14(t):
    """«Две минуты прямо»: на экране стрелка прямо и «2 мин», прямая линия к «ДЕЛО»."""
    a, b = T0("s14"), T1("s14")
    p = [(-170, 200), (180, -60)]
    inner = map_icons(t) + route(p) + you_marker(-170, 200, 40) + banner("straight", t, ramp(t, a - .1, .25))
    o = nav_shot(t, inner)
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(41), 6)
    return view("".join(o), 540 + dx, 1010 + dy, 1.3 + .06 * u, 0, t=t)


def frame_s15(t):
    """«без поворотов»: кот в кепке едет в машинке прямо, Дима идёт следом мимо холодильника, не поворачивая."""
    a, b = T0("s15"), T1("s15")
    o = home(t)
    sh = 260 * (t - a)
    o.append(fridge(260 - sh, RFL, 0.0, t, .9))
    o.append(RM.sofa(1200 - sh, RFL, .9)["back"])
    o.append(toy_car(760, RFL + 40, .85, t, dict(look=(.6, -.1), smile=1.0), drive=1.0, wheel_turn=4 * math.sin(t * 9)))
    f = dima_walk(380, t, expr="proud82")
    o.append(f["svg"])
    o.append(PR.speed_arcs(560, RFL - 200, 1.0, 1.0, t, seed=9, n=3, ang=0))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1100, 1.05 + .05 * u, 0, t=t)


def frame_s16(t):
    """«И через две минуты я уже был на месте»: Дима за столом работает, на столе флажок «ДЕЛО», машинка с котом припаркована рядом."""
    a, b = T0("s16"), T1("s16")
    o = desk_room(t, sun=1.0)
    o.append(PR.laptop(640, DESK_Y - 8, 1.0, screen="lines", lines=clamp((t - a) / (b - a)), t=t, seed=1))
    fl = line([(0, 0), (0, -170)], 7, taper=0, wmin=1, seed=13600)
    fl += shape([(0, -170, 1), (180, -170, 1), (160, -130), (180, -92, 1), (0, -92, 1)], "#e2453a", "", w=3.4, seed=13601)
    fl += plain("ДЕЛО", 86, -116, 40, fill="#ffffff", anchor="middle")
    o.append(tf(fl, 830, DESK_Y - 6, 1.0 + .15 * bump(t, W(52), .05, .3)))
    tap = math.sin(t * 30)
    o.append(dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.9, -.1)), lean=.18,
                       arms={"f": ("ik", (560 + 10 * tap, DESK_Y - 30), 1), "n": ("ik", (640 - 10 * tap, DESK_Y - 25), 1)})["svg"])
    o.append(toy_car(900, FL + 30, .55, t, dict(look=(-.8, -.3), smile=1.0)))
    o.append(PR.sparkles(760, DESK_Y - 220, 1.6, bump(t, W(53), .05, .5), t, seed=161, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 620, 880, 1.3 + .06 * u, 0, t=t)


def cta(t, zoom=1.0):
    c = SH["cta"]
    if "bg" not in TG._ST:
        TG._ST["bg"] = TG.background(lib)
        TG.prepare(COMMON)
        lib.static_done()
    lib.dyn_begin()
    body, (cx, cy, s, rot) = TG.layer(t, c["t0"], c["press"], COMMON)
    return lib.svg(f'<rect width="1080" height="1920" fill="#6e4a32"/><g transform="{lib.cam(cx, cy, s * zoom, rot)}">{TG._ST["bg"]}{body}</g>{over(t)}')


def frame_s17(t):
    return cta(t)


def frame_s18(t):
    return cta(t, 1.04)


def frame_s19(t):
    return cta(t, 1.0)


def frame_s20(t):
    """Петля: кадр хука — экран навигатора с маршрутом к «ДЕЛО»."""
    a, b = T0("s20"), T1("s20")
    inner = map_icons(t) + route(ROUTE_DESK) + you_marker(*START_P) + banner("turn", t)
    o = [home(t)[0]]
    o.append(navigator(500, 1160, .92, t, inner, rot=-3))
    o.append(CT.draw(890, 1820, 1.0, dict(look=(-.8, -.6), perk=1.0, tail=10 * math.sin(t * 3)), t))
    return loop_view("".join(o), t, a, b, HIT, 540, 1160, 1.0)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
