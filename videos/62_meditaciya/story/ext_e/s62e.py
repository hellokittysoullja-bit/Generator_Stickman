"""Рилс 62 «медитация», группа E — вечерняя комната, начало: s01 (хук: плюх в лотос), s03 (сел, закрыл глаза, блаженство),
s08 (башня из трёх облаков над головой кренится). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Комната — common/room.py, люди — common/people.py, предметы и облака — common/props.py."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


T_RESHIL, T_MEDIT = wt(1), wt(2)               # 0.40, 0.76
T_SEL, T_ZAKRYL, T_GLAZA = wt(6), wt(7), wt(8)  # 2.80, 3.25, 3.67
T_POTOM, T_PODUMAL, T_MEDIT2, T_NE = wt(25), wt(26), wt(28), wt(29)   # 11.01, 11.41, 12.12, 12.69
E = people.EXPR["dima"]


def lerp(a, b, u):
    return a + (b - a) * u


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def ex(name, **kw):
    e = dict(E[name])
    e.update(kw)
    return e


def blinkv(t, times, dur=.16):
    v = 0.0
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def damp(t, t0, amp, freq=3.0, dmp=6.0):
    """Затухающее колебание после t0 (0 до t0)."""
    u = t - t0
    if u <= 0:
        return 0.0
    return amp * math.exp(-dmp * u) * math.sin(2 * math.pi * freq * u)


def scale_about(svg, cx, cy, sx, sy):
    return f'<g transform="translate({cx:.2f} {cy:.2f}) scale({sx:.4f} {sy:.4f}) translate({-cx:.2f} {-cy:.2f})">{svg}</g>'


def rotate_about(svg, cx, cy, deg):
    return f'<g transform="rotate({deg:.3f} {cx:.2f} {cy:.2f})">{svg}</g>'


def hook_cam(t, t_hit, base_s=1.0):
    """Влёт правила 28/29 (не слабее рилса 17): с 40 % дальше за 0.22 с, перелёт 5 % с отскоком, поворот 3.6° с возвратом,
    второй удар +9 % на ударном слоге. Возвращает (масштаб-множитель, поворот, боковой занос)."""
    u = clamp(t / .22)
    e = ease_out(u, 3)
    s = 1 / 1.4 + (1 - 1 / 1.4) * e
    over = .055 * math.exp(-7 * max(0.0, t - .22)) * math.sin(2 * math.pi * 2.2 * max(0.0, t - .22) + math.pi / 2) if t > .22 else 0.0
    s += over if t > .22 else 0.0
    rot = -3.6 * (1 - e) + damp(t, .22, 1.2, 2.0, 6.0)
    side = -55 * (1 - e)
    hit = 0.0
    if t > t_hit:
        h = t - t_hit
        hit = .09 * math.exp(-5.5 * h) * (1 if h > .03 else h / .03)
    return s * (1 + hit), rot, side


def speed_lines(p, vel, k=1.0, seed=0, u=1.0):
    """Штрихи скорости тушью позади летящего (p — центр, vel — направление полёта)."""
    if u <= .02:
        return ""
    vx, vy = vel
    n = math.hypot(vx, vy) + 1e-9
    dx, dy = vx / n, vy / n
    nx, ny = -dy, dx
    o = []
    for i, (off, ln) in enumerate(((-150, 240), (-40, 320), (80, 260), (190, 200))):
        a = (p[0] - dx * (150 + 40 * (i % 2)) + nx * off * k, p[1] - dy * (150 + 40 * (i % 2)) + ny * off * k)
        b = (a[0] - dx * ln * k * u, a[1] - dy * ln * k * u)
        o.append(line([a, b], 7 * k, INK, taper=.8, wmin=.1, seed=seed + i, peak=.15))
    return "".join(o)


def dust(cx, cy, t, t0, k=1.0, seed=0):
    """Пыль-клубы от плюха: сплошные бежевые клубки с тушью разлетаются в стороны и тают размером (не прозрачностью)."""
    u = t - t0
    if u <= 0 or u > .7:
        return ""
    o = []
    for i, (ang, d, r) in enumerate(((180, 290, 34), (200, 230, 26), (165, 340, 22), (0, 290, 34), (-20, 240, 26), (15, 340, 22), (190, 170, 18), (-10, 170, 18))):
        e = ease_out(clamp(u / .45), 2)
        a = math.radians(ang)
        x = cx + math.cos(a) * d * e * k
        y = cy - math.sin(a) * 40 * e * k - 30 * e * k
        rr = r * k * (1 - (u / .7) ** 1.5) * (.6 + .6 * e)
        if rr < 2:
            continue
        o.append(shape(ellipse_pts(x, y, rr * 1.2, rr, 12, jitter=.1, seed=seed + i), "#e8dcc4", "", w=2.6, seed=seed + 20 + i))
    return "".join(o)


def cam_wrap(body, cx, cy, s, rot=0.0):
    return f'<g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>'


# ═══════════════════════════════ s01: хук — плюх в лотос ═══════════════════════════════
def frame01(t):
    X, Y = R.seat()
    S = 1.04
    # полёт: с кадра 0 Дима уже летит по дуге слева-сверху, приземляется на «решил»
    TL = T_RESHIL
    if t < TL:
        u = t / TL
        x = lerp(X - 330, X, u)
        y = lerp(Y - 400, Y, u * u * .55 + u * .45) - 120 * 4 * u * (1 - u) * .35
        spin = lerp(-.42, -.05, u)
        fold = lerp(.05, .45, u)
        vel = (330 / TL, (400 * (1.1 * u + .45)) / TL)
    else:
        x, y = X, Y
        spin = -.05 * math.exp(-8 * (t - TL))
        fold = .45 + .55 * ease_out(clamp((t - TL) / .16), 2)
        vel = (0, 0)
    # приземление: подушка сплющивается, Дима проседает со сжатием и отскакивает
    csx, csy = PR.squash(t, TL, amp=.32, freq=3.2, damp=7.0)
    bsx, bsy = PR.squash(t, TL, amp=.16, freq=3.0, damp=7.5)
    y += (1 - csy) * 80 * R.CUSH_K * R.CUSH_H * .9
    spread = 1.0 + damp(t, TL + .1, .16, 3.4, 6.0)
    # руки: в полёте вверх-в стороны (размахивает), к «медитировать» ложатся на колени колечком
    kn = people.lotus_knees(x, y, S, spread)
    up_n = (x + 300 * S + 30 * math.sin(t * 22), y - 760 * S)
    up_f = (x - 260 * S - 30 * math.sin(t * 19), y - 700 * S)
    knee_n = (kn["n"][0] - 40 * S, kn["n"][1] - 46 * S)
    knee_f = (kn["f"][0] + 30 * S, kn["f"][1] - 40 * S)
    ua = sm(t, TL + .05, T_MEDIT + .08)
    tn = (lerp(up_n[0], knee_n[0], ua), lerp(up_n[1], knee_n[1], ua))
    tf = (lerp(up_f[0], knee_f[0], ua), lerp(up_f[1], knee_f[1], ua))
    if t < T_MEDIT:
        hands = {"n": {"dir": (.3, -1), "spread": .45, "curl": (0, .02, .05, .1), "thumb": .1},
                 "f": {"dir": (-.3, -1), "spread": .45, "curl": (0, .02, .05, .1), "thumb": .1}}
    else:
        hands = {"f": {"kind": "mudra", "k": 1.0, "dir": (-.35, 1)}, "n": {"kind": "mudra", "k": 1.0, "dir": (.45, 1)}}
    arms = {"n": ("ik", tn, -1), "f": ("ik", tf, 1)}
    # лицо: в полёте восторг (рот открыт, волосы торчат), после «медитировать» — торжественность, грудь колесом
    if t < TL + .12:
        e = ex("zeal", look=(.3, .55), hair=10)
    elif t < T_MEDIT:
        e = ex("zeal", look=(.2, .1), open=.35, hair=4)
    else:
        e = ex("solemn", look=(.15, -.25), lid=.5 + .1 * math.sin(t * 3))
        e["closed"] = blinkv(t, (1.22,))
    chest = sm(t, T_MEDIT, T_MEDIT + .3)
    lean = spin - .07 * chest
    head_ang = -.1 * chest + damp(t, TL, .12, 3.0, 7)
    torso_k = 1.0 + .05 * chest + .015 * math.sin(t * 4)
    fg = people.figure("dima", x, y, S, e, lean=lean, head_ang=head_ang, arms=arms, hands=hands, torso_k=torso_k,
                       lotus={"fold": fold, "spread": spread, "sag": 0.0})
    body = fg["svg"]
    if abs(bsx - 1) > 1e-3:
        body = scale_about(body, X, Y + 230, bsx, bsy)
    if t < TL:
        body = speed_lines((x, y - 250), vel, 1.0, seed=50, u=clamp(1 - t / TL * .3)) + body
    bgr = R.room_bg(t, "evening", flick=clamp(1 - abs(t - TL) / .2), sway=damp(t, TL, 7, 2.2, 3.5))
    cush = PR.cushion(R.CUSH[0], R.CUSH[1], R.CUSH_K, sy=R.CUSH_H * csy)
    cush = scale_about(cush, R.CUSH[0], R.CUSH[1], csx, 1.0)
    world = bgr["bg"] + cush + body + dust(R.CUSH[0], R.CUSH[1] - 20, t, TL, 1.3, seed=70) + bgr["front"]
    # камера: влёт с кадра 0, удар на «решил», тряска на приземлении, потом лёгкий дрейф к лицу
    hs, hrot, hside = hook_cam(t, TL)
    sh = PR.shake(t, TL, 18, .4, seed=3)
    drift = sm(t, .6, 1.6)
    cx = 545 + hside + sh[0] + lerp(-120, 0, ease_out(clamp(t / .4), 2)) * 0
    fly_cy = y - 330
    cy = lerp(fly_cy, lerp(1000, 960, drift), sm(t, .2, .55)) + sh[1]
    s = 1.0 * hs * lerp(1.0, 1.04, drift)
    set_ink(s)
    return lib.svg(cam_wrap(world, cx, cy, s, hrot))


# ═══════════════════════════════ s03: сел, закрыл глаза, блаженство ═══════════════════════════════
def frame03(t):
    X, Y = R.seat()
    S = 1.04
    a = 2.5
    # ёрзает на «сел»: два подскока со сжатием, таз бегает вбок
    hop = PR.hop(t, T_SEL - .02, h=34, dur=.22) + PR.hop(t, T_SEL + .24, h=18, dur=.18)
    wig = 16 * math.sin(2 * math.pi * 3.2 * (t - T_SEL)) * math.exp(-3 * max(0.0, t - T_SEL)) if t > T_SEL - .05 else 0.0
    csx, csy = PR.squash(t, T_SEL + .2, amp=.14, freq=3.2, damp=8)
    breath = math.sin(2 * math.pi * (t - T_GLAZA) / 1.6) if t > T_GLAZA else 0.0
    settle = sm(t, T_GLAZA, T_GLAZA + .45)
    x = X + wig
    y = Y + hop + (1 - csy) * 80 * R.CUSH_K * R.CUSH_H * .9 + 10 * settle
    fid = clamp((t - T_SEL + .05) / .6)
    if 0 < fid < 1:
        kw = people.lotus_kw("fidget", x, y, S, u=fid * 2)
    else:
        kw = people.lotus_kw("sit", x, y, S)
    # глаза: смотрит по сторонам, на «закрыл» веки опускаются, к «глаза» — дуги; на «глаза» блаженная улыбка
    cl = sm(t, T_ZAKRYL, T_ZAKRYL + .28)
    if cl < .98:
        e = ex("solemn", look=(lerp(-.4, .45, sm(t, a, T_SEL + .3)), -.1), lid=.62, brows="up" if t < T_SEL + .4 else "calm")
        e["closed"] = max(cl, blinkv(t, (2.62,)))
        e["mouth"] = "flat"
    else:
        sml = sm(t, T_GLAZA, T_GLAZA + .3)
        e = ex("bliss", smile=lerp(.15, .95, sml), shut=1.0)
        if sml < .05:
            e["mouth"] = "flat"
    kw["lean"] = kw.get("lean", 0.0) - .03 * settle + .01 * breath
    kw["head_ang"] = .06 * math.sin(2 * math.pi * 1.6 * (t - a)) * (1 - settle) - .06 * settle
    fg = people.figure("dima", x, y, S, e, torso_k=1.0 + .022 * breath - .02 * settle, head_off=(0, 8 * settle), **kw)
    body = fg["svg"]
    bgr = R.room_bg(t, "evening")
    cush = scale_about(PR.cushion(R.CUSH[0], R.CUSH[1], R.CUSH_K, sy=R.CUSH_H * csy), R.CUSH[0], R.CUSH[1], csx, 1.0)
    world = bgr["bg"] + cush + body + bgr["front"]
    # хлёст обратно в комнату: камера влетает справа и тормозит, потом медленный наезд на лицо
    wi = ease_out(clamp((t - a) / .32), 3)
    push = sm(t, a + .3, 4.6)
    hx, hy = fg["head"]
    cx = lerp(560, hx + 10, push * .7) + 380 * (1 - wi)
    cy = lerp(990, hy + 330, push * .75)
    s = lerp(1.2, 1.42, push) - .1 * (1 - wi)
    rot = 4 * (1 - wi) + .4 * math.sin(t * 1.3)
    set_ink(s)
    return lib.svg(cam_wrap(world, cx, cy, s, rot))


# ═══════════════════════════════ s08: башня из трёх облаков ═══════════════════════════════
def _lunch(k=1.0, t=0.0):
    return PR.plate_soup(-30 * k, 50 * k, .78 * k, steam=1.0, t=t, seed=81) + PR.cutlet_fork(70 * k, -10 * k, .62 * k, rot=-22, seed=82)


def _friend(k=1.0, t=0.0):
    s = .2 * k
    stomp = abs(math.sin(t * 9.0))
    fx, fy = -10 * k, 150 * k - 10 * stomp * k
    f = people.figure("pal", fx, fy, s, people.EXPR["pal"]["hurt"], layers=("arm_f", "body", "arm_n"),
                      arms={"f": ("ang", .25, .3), "n": ("ik", (fx + 160 * s, fy - 360 * s + 12 * math.sin(t * 18) * k), -1)},
                      hands={"n": {"kind": "none"}})
    w = f["wrist"]["n"]
    mob = PR.mobilnik(w[0] + 14 * k, w[1] - 26 * k, .5 * k, rot=10 + 12 * math.sin(t * 18))
    bk, fr = people.grip_svg("pal", (w[0] + 14 * k, w[1] - 18 * k), 18 * k, 1, k=s * 1.03, seed=960)
    return f["svg"] + bk + mob + fr


def _iron(k=1.0, t=0.0):
    jump = abs(math.sin(t * 7)) * 8 * k
    return PR.ironing_board(0, 50 * k, .5 * k, w=520) + PR.iron(10 * k, 34 * k - jump, .72 * k, rot=-4, smoke=1.0, t=t, seed=83)


def frame08(t):
    X, Y = R.seat()
    S = 1.04
    a = 10.75
    tilt_u = sm(t, T_MEDIT2 - .05, T_MEDIT2 + .45)
    # Дима: глаза закрыты, брови сведены (терпит), на «медитация» вжимает голову в плечи и жмурится
    duck = ease_out(clamp((t - T_MEDIT2) / .22), 2)
    if t < T_MEDIT2:
        e = {"brows": "pinch", "mouth": "flat", "shut": 1.0}
    else:
        e = ex("squeeze")
    kw = people.lotus_kw("sit", X, Y, S)
    kw["head_ang"] = .05 * math.sin(t * 2.4) * (1 - duck) + .04 * duck
    kw["lean"] = .05 * duck
    shiver = 3.0 * math.sin(t * 40) * duck
    fg = people.figure("dima", X + shiver, Y, S, e, head_off=(0, 70 * duck), torso_k=1.0 - .05 * duck, **kw)
    hx, hy = fg["head"]
    top = hy - 220 * S
    # башня: снизу обед, над ним друг, наверху утюг; каждый ярус качается сильнее, облака сплющены теснотой
    sway = math.sin(2 * math.pi * .9 * (t - a))
    lean_deg = 5.5 * sway + 20 * tilt_u + damp(t, T_MEDIT2 + .45, 4, 1.6, 2.5)
    clouds = []
    base = (hx + 10, top - 20)
    levels = [("lunch", 360, 220, 121), ("friend", 330, 250, 122), ("iron", 400, 230, 123)]
    yc = 0.0
    for i, (kind, w, h, sd) in enumerate(levels):
        jostle = math.sin(2 * math.pi * 1.7 * t + i * 1.9)
        sqy = .86 - .03 * i + .05 * jostle
        sqx = 1.0 + .07 * (1 - sqy / .9) + .03 * jostle
        if t > T_MEDIT2:
            sqy += .06 * math.sin(2 * math.pi * 3 * (t - T_MEDIT2)) * math.exp(-3 * (t - T_MEDIT2))
        ang = math.radians(lean_deg * (.35 + .4 * i))
        cxw = base[0] + math.sin(ang) * (-yc) * -1 + 10 * jostle * (i + 1) * .5
        cyw = base[1] - yc * math.cos(ang) + (8 * i if t > T_MEDIT2 else 0)
        k = .95
        inner = {"lunch": _lunch, "friend": _friend, "iron": _iron}[kind](k, t)
        dots = (hx + 30 - cxw, top + 60 - cyw) if i == 0 else None
        c = PR.cloud(cxw, cyw, w, h, sqx, sqy, seed=sd, dots=dots, inner=inner)
        clouds.append(rotate_about(c, cxw, cyw - h * sqy * .5, lean_deg * (.3 + .35 * i)))
        yc += h * sqy * .98
    bgr = R.room_bg(t, "evening")
    sweat = ""
    if t > T_MEDIT2 + .1:
        u = clamp((t - T_MEDIT2 - .1) / .5)
        sweat = PR.sweat(hx + 120 * S, hy - 60 * S + 120 * u, 1.2, rot=8)
    world = bgr["bg"] + R.cushion_layer() + fg["svg"] + sweat + "".join(clouds) + bgr["front"]
    # медленный откат, кадр качается в такт башне
    pb = sm(t, a, 12.95)
    s = lerp(1.06, .98, pb)
    cx = 560 + 6 * sway
    cy = lerp(800, 790, pb)
    rot = 1.4 * sway + 2.2 * tilt_u
    sh = PR.shake(t, T_MEDIT2, 10, .35, seed=8)
    set_ink(s)
    return lib.svg(cam_wrap(world, cx + sh[0], cy + sh[1], s, rot))


FRAMES = {"s01": frame01, "s03": frame03, "s08": frame08}


def frame(sid, t):
    lib.DEFS.clear()
    lib.static_done()
    return FRAMES[sid](t)
