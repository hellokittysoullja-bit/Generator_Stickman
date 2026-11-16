"""Рилс 80 «Мама была права», группа B: Дима, кот, призыв. Время — только из shots.json и voice/words.json (слово по индексу wN).
s04: тёмная комната, Дима растёт в три рывка «лет» (w10), сам затягивает шнур бирки «сам» (w13), смирился «поверил» (w16).
s05: призыв «Телеграм» модулем scripts/story_cta_tg.py: PRESS = W[20].start + 0.12 («Телеграм»), T0 = PRESS − 1.10.
s07: комната вечером, кот на задних лапах поддевает бирку носом: «смотри» (w30) к зрителю, «что»–«было» (w31–w34) дымок из-под
     бирки, «самом» (w36) захлопнулась, бровь.
s08: стол днём, «Дима»–«садился» (w38–w39) садится и закатывает рукав, «дело» (w41) кладёт лист и папку.
s10: «уходил» (w51) отворачивается к телефону, «телефон» (w53) тёплый купол, облако снаружи.
s16: вечер, «да» (w85) кивает облачку, «неприятно» (w86) облачко-клубок на угол стола, берёт ручку.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
import room as R  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, svg  # noqa: E402,F401

INK = lib.INK
W = json.load(open(os.path.join(STORY, "voice", "words.json")))
W = W if isinstance(W, list) else W["words"]
SH = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return W[i]["start"]


def we(i):
    return W[i]["end"]


def T0(sid):
    return SH[sid]["t0"]


def T1(sid):
    return SH[sid]["t1"]


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))


def bump(t, t0, dur):
    u = (t - t0) / dur
    return math.sin(math.pi * u) if 0 < u < 1 else 0.0


def kick(t, t0, dur=.35, freq=2.2, damp=5.0):
    """Затухающий удар после t0: 0 до t0, потом колебание к нулю (для тряски и наездов)."""
    if t < t0:
        return 0.0
    u = (t - t0) / dur
    return math.exp(-damp * u) * math.cos(2 * math.pi * freq * u) if u < 3 else 0.0


def frame_svg(body, cx, cy, s, rot, bg="#05070f", over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def soft(x, y, rx, ry, col, op):
    g = lib.rad_grad([(0, col, op), (.55, col, op * .45), (1, col, 0)], x, y, rx, ry)
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#{g})"/>'


def dima_layers(x, y, k, expr, pose, t, u=1.0, age=1.0, feet=None, flip=False, front=None, **kw):
    """Дима двумя проходами: тело (ноги, таз, дальняя рука, тело) → front (бирка и т.п. между телом и ближней рукой) → ближняя рука."""
    back = people.dima80(x, y, k, expr, pose, t, u, age, feet, flip, layers=("legs", "pelvis", "arm_f", "body"), **dict(kw))
    near = people.dima80(x, y, k, expr, pose, t, u, age, feet, flip, layers=("arm_n",), **dict(kw))
    mid = front(back) if front else ""
    back["svg"] = back["svg"] + mid + near["svg"]
    return back


def jerk(t, t0, dur=.14):
    """Рывок 0→1 за dur с перелётом (пружина): для роста в три рывка."""
    if t <= t0:
        return 0.0
    u = (t - t0) / dur
    if u < 1:
        return ease_out(u, 3) * 1.06
    return 1 + .06 * math.exp(-6 * (u - 1)) * math.cos(2 * math.pi * .9 * (u - 1))


# ═══════════════════════════════ s04: Дима растёт в три рывка, сам затягивает шнур, смирился ═══════════════════════════════
def s04(t):
    lib.dyn_begin()
    g1, g2, g3 = ws(10), we(10), ws(11)          # три рывка роста: «лет» начало, конец, «и»
    T_SAM, T_POV = ws(13), ws(16)
    rm = R.turn_dark(t, 1.0)
    o = [rm["bg"]]
    fl = rm["anchors"]["fl"]
    # тени-обвинители из поворота: ещё тычут, дрожат, гаснут после первого рывка
    fade = 1 - ease_io(clamp((t - g1) / (T_SAM - g1)))
    if fade > .01:
        for kind, x, kk, fl_, ph in (("mama", 150, .78, False, 0.0), ("teacher", 960, .74, True, 1.3), ("aunt", 300, .6, False, 2.4)):
            jab = .75 + .25 * math.sin(t * 7.0 + ph)
            hy = fl - 40 - (people.LEG_LEN - 12) * kk * .98
            sh = people.accuser_shadow(kind, x + 30 * (1 - fade) * (-1 if not fl_ else 1), hy, kk, jab, t, col=R.T80_SHADOW, op=.75 * fade,
                                       blur_sd=4.0, flip=fl_, aim=(540, 700))
            o.append(sh["svg"])
    # рост: возраст 0 → .45 → .78 → 1 тремя рывками
    a1, a2, a3 = jerk(t, g1), jerk(t, g2), jerk(t, g3)
    age = .45 * min(a1, 1.0) + .33 * min(a2, 1.0) + .22 * min(a3, 1.0)
    over = max(a1 - 1, 0) + max(a2 - 1, 0) + max(a3 - 1, 0) if t > g1 else 0.0     # перелёт рывка — вытягивается чуть выше
    k = .86
    x = 540.0
    hip_y = people.hip_on_floor(fl - 6, k, age) - 260 * k * over
    # поза: под гирей (сутулится) → выпрямляется с ростом → руки к горлу «сам» → смирился «поверил»
    u_up = clamp(age / .8)
    u_tie = ease_io(clamp((t - (T_SAM - .3)) / .3))
    u_sl = ease_io(clamp((t - (T_POV - .05)) / .4))
    if t < T_SAM - .3:
        pose, pu = ("d80_sag", "d80_stand"), u_up
        ex = "heavy80" if age < .1 else ("grow80" if age < .9 else dict(people.EXPR["dima"]["grow80"], stubble=1.0, bags=True))
    elif t < T_POV - .05:
        pose, pu = ("d80_stand", "d80_tie"), u_tie
        ex = "tie80"
    else:
        pose, pu = ("d80_tie", "d80_slump"), u_sl
        ex = "resign80"
    # затягивает шнур: короче рывками на «сам»
    tug = ease_out(clamp((t - T_SAM) / .22), 2) * .6 + ease_out(clamp((t - (T_SAM + .3)) / .2), 2) * .4
    cord = 150 - 70 * tug
    br = 6 * math.sin(t * 2.4)
    tk = 1.0

    def tag(fig):
        nx, ny = fig["neck"]
        sw = -10 * kick(t, g1, .4, 1.6, 3) + 8 * kick(t, g2, .4, 1.6, 3) - 7 * kick(t, g3, .4, 1.6, 3) + 6 * kick(t, T_POV, .5, 1.2, 3) \
            + 3 * math.sin(t * 3.1) - 4 * kick(t, T_SAM, .3, 2, 4)
        return P.iron_tag(nx + 30 * fig["k"], ny + 46 * fig["k"], tk, sw, cord=cord, seed=4)
    fig = people.dima80(x, hip_y, k, ex, pose, t, pu, age, feet="stand", lean_add=.02 * math.sin(t * 2.4))
    o.append(soft(x, fl + 6, 300, 40, "#000000", .5))
    o.append(fig["svg"])
    o.append(tag(fig))
    if u_tie > .3 and t < T_POV + .2:        # руки держат ветви шнура: шнур от кулаков к петле
        nx, ny = fig["neck"]
        for side in ("f", "n"):
            wx, wy = people.hand_pos(fig, side, 30)
            o.append(line([(nx + (wx - nx) * .2, ny + 14), (wx, wy - 10)], 6 * tk, P.C_CORD, taper=.1, wmin=.7, seed=8420 + (side == "n")))
    hx, hy = fig["head"]
    # штрихи рывка роста: короткие линии у головы на каждом рывке
    for j, g in enumerate((g1, g2, g3)):
        uu = (t - g) / .22
        if 0 < uu < 1:
            for s_ in (-1, 1):
                xx = hx + s_ * 190 * fig["k"]
                o.append(line([(xx, hy + 60 - 120 * uu), (xx, hy + 160 - 120 * uu)], 7 * (1 - uu) + 1, "#9fb4ff", taper=.6, wmin=.2,
                              seed=8400 + j * 2 + (s_ > 0), op=.8 * (1 - uu)))
    # затягивание: штрихи у шеи
    uu = (t - T_SAM) / .3
    if 0 < uu < 1:
        nx, ny = fig["neck"]
        for j in range(3):
            a_ = math.radians(-160 + 50 * j)
            o.append(line([(nx + 70 * math.cos(a_), ny + 70 * math.sin(a_)), (nx + (100 + 40 * uu) * math.cos(a_), ny + (100 + 40 * uu) * math.sin(a_))],
                          6 * (1 - uu) + 1, "#dfe6ff", taper=.6, wmin=.2, seed=8410 + j, op=.85 * (1 - uu)))
    o.append(rm["shade"])
    # камера: поднимается вместе с ростом, толчок на «поверил»
    pk = kick(t, T_POV, .4, 1.0, 4) if t >= T_POV else 0.0
    s = lerp(1.08, 1.02, ease_io(clamp(age))) * (1 + .06 * max(0.0, pk)) + .01 * (t - T0("s04"))
    cy = lerp(1040, 985, ease_io(clamp(age))) + 0 * br
    return frame_svg("".join(o), 540, cy, s, .3 * math.sin(t * 1.3), bg="#070a18")


# ═══════════════════════════════ s05: призыв «Телеграм» ═══════════════════════════════
def s05(t):
    import story_cta_tg as tg
    press = ws(20) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=COMMON)


def frame(sid, t):
    return globals()[sid](t)
