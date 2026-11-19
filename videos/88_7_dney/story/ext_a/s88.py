"""Рилс 88 «7 дней без телефона», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
Хук s01 — бег из рилсов 82–83 (план шагов, трекинг, влёт правил 28–29; rdima/rcat — копии): кот с телефоном в зубах
мчится галопом, Дима гонится, тянет руки. s02 — шкафчик, s18 — петля тем же ракурсом. Остальные планы — common/people.py,
cat.py, props.py, свой фон. Призыв s08 — scripts/story_cta_tg.py. Дни — отрывной календарь с точками (cal_corner).
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука (Дима и кот) белым на чёрном."""
import json
import math
import os
import sys

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(1, os.path.join(REPO, "scripts"))
import big_title  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import rcat as Cat  # noqa: E402
import rdima as dima  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape, smooth  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
NOCAM = bool(os.environ.get("NOCAM"))
MASK = bool(os.environ.get("MASK"))


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def stress(i, u):
    return W(i) + (WE(i) - W(i)) * u


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def kick(t, t0, rise=.04, tau=.12):
    u = t - t0
    if u <= 0:
        return 0.0
    return (u / rise) if u < rise else math.exp(-(u - rise) / tau)


def damp(t, t0, amp, freq=3.0, dmp=6.0):
    u = t - t0
    if u <= 0:
        return 0.0
    return amp * math.exp(-dmp * u) * math.sin(2 * math.pi * freq * u)


def title(t):
    """Заголовок хука: экранный слой s01–s03; уходит сжатием к склейке s03→s04."""
    if NOCAM or MASK:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=T0("s04") - 0.15, hits=hits)


# ═════════════════════════ бег: план шагов (из run/scene.py рилса 40, быстрее и с прыжком) ═════════════════════════
BS = dima.BS
LEG = (dima.THIGH + dima.SHIN) * BS
AHW = dima.AH * BS
TOEW = dima.TOE * BS * 1.22
C = {}
PL = {}


def plan(conf):
    """conf: a, b (время), x0 (таз в мире на a), tc (шаг, с), st (доля опоры), step (длина), leap=(t, dur, len) или None,
    stumble=t или None, walk (спокойный шаг)."""
    C.clear()
    C.update(conf)
    tc, step = conf["tc"], conf["step"]
    st = conf["st"] * tc
    Cn = []
    for k in range(1, 16):
        if conf.get("still"):        # до a стоит: обе ступни на месте
            Cn.append([conf["a"] - k * tc, "n" if k % 2 == 0 else "f", conf["x0"] - (0 if k % 2 == 0 else 60), 0.0, conf["a"] - k * tc + tc * .99, tc, None])
            continue
        Cn.append([conf["a"] - k * tc, "n" if k % 2 == 0 else "f", conf["x0"] - k * step, 0.0, conf["a"] - k * tc + st, tc, None])
    Cn = Cn[::-1]
    t, x, k = conf["a"], conf["x0"], 0
    lps = [conf[k_] for k_ in ("leap", "leap2") if conf.get(k_)]
    used = [False] * len(lps)
    while t < conf["b"] + 2.0:
        ttc, sstep, tag = tc, step, None
        for j, lp in enumerate(lps):
            if not used[j] and t + tc > lp[0]:
                ttc, sstep, used[j], tag = lp[1], lp[2], True, j
                break
        if conf.get("stumble") and abs(t - conf["stumble"]) < tc / 2:
            ttc, sstep = tc * 1.25, step * .55
        if conf.get("stop_x") is not None and x > conf["stop_x"] and conf.get("stop") is None:
            conf["stop"] = t - 1e-3
        if conf.get("stop") is not None and t > conf["stop"]:      # остановка: приставил ногу и стоит
            Cn.append([t, "n" if k % 2 == 0 else "f", x - sstep * .7, 0.0, t + 30.0, ttc, None])
            last = Cn[-2]
            last[4] = t + 30.0
            break
        Cn.append([t, "n" if k % 2 == 0 else "f", x, 0.0, t + st, ttc, tag])
        t += ttc
        x += sstep
        k += 1
    C.update(conf)
    keys = [((c[0] + min(c[4], c[0] + c[5] * .6)) / 2, c[2] + 6) for c in Cn]
    if conf.get("stop") is not None:
        xe = (Cn[-1][2] + Cn[-2][2]) / 2 + 6
        keys = [kk for kk in keys if kk[0] < Cn[-1][0] - .05] + [(Cn[-1][0] + .25, xe), (Cn[-1][0] + 30, xe)]
    if conf.get("still"):
        keys = [(conf["a"] - 3.0, conf["x0"] - 24)] + [kk for kk in keys if kk[0] >= conf["a"]]
        keys.insert(1, (conf["a"], conf["x0"] - 24))
    ts, xs = zip(*keys)
    PL.clear()
    PL.update(C=Cn, hip_x=PchipInterpolator(np.array(ts), np.array(xs)))


def hip_at(t, bob=True):
    x = float(PL["hip_x"](t))
    if C.get("walk") and (C.get("stop") is not None and t > PL["C"][-1][0] + .2 or C.get("still") and t < C["a"]):
        y = -(LEG * 0.97 + AHW)
        if C.get("sit") is not None:
            y += C["sit_drop"] * ease_io(clamp((t - C["sit"]) / .45))
            x += C.get("sit_dx", 0.0) * ease_io(clamp((t - C["sit"]) / .45))
        return np.array([x, y])
    y = -(LEG * (0.86 if not C.get("walk") else 0.93) + AHW)
    if bob:
        best, tc = 9.0, C["tc"]
        for c in PL["C"]:
            dt = t - (c[0] + c[4]) / 2
            if abs(dt) < abs(best):
                best, tc = dt, c[5]
        y += (12 if not C.get("walk") else 7) * math.cos(2 * math.pi * best / max(tc, 1e-3) * (C["tc"] / tc if tc > C["tc"] * 1.4 else 1))
        for c in PL["C"]:
            if len(c) > 6 and c[6] is not None:
                u = (t - c[4]) / (c[0] + c[5] - c[4])
                if 0 < u < 1:
                    y -= 115 * math.sin(math.pi * u)
    return np.array([x, y])


def planted(c, hip):
    A = np.array([c[2], c[3] - AHW])
    reach = LEG * 0.985
    if np.linalg.norm(A - hip) <= reach:
        return A, 0.0
    toe = np.array([c[2] + TOEW, c[3]])
    lo, hi = 0.0, 1.35
    for _ in range(30):
        m = (lo + hi) / 2
        A2 = toe + dima.rot(np.array([-TOEW, -AHW]), m)
        if np.linalg.norm(A2 - hip) > reach:
            lo = m
        else:
            hi = m
    return toe + dima.rot(np.array([-TOEW, -AHW]), hi), hi


def foot_at(side, t, hip):
    cs = [c for c in PL["C"] if c[1] == side]
    prev, nxt = cs[0], None
    for c in cs:
        if c[0] <= t:
            prev = c
        elif nxt is None:
            nxt = c
    if t <= prev[4] or nxt is None:
        return planted(prev, hip)
    t0, t1 = prev[4], nxt[0]
    u = clamp((t - t0) / (t1 - t0))
    A0, ph0 = planted(prev, hip_at(t0))
    A1 = np.array([nxt[2], nxt[3] - AHW])
    lift = (128 if not C.get("walk") else 60) * (1.0 + 0.5 * (t1 - t0 > 0.3))
    ux = (1 - math.cos(math.pi * u ** 1.3)) / 2
    x = A0[0] + (A1[0] - A0[0]) * ux - (30 if not C.get("walk") else 10) * math.sin(math.pi * clamp(u * 1.5))
    y = A0[1] + (A1[1] - A0[1]) * u - lift * math.sin(math.pi * clamp(u * 1.08)) ** 1.3
    if C.get("walk"):
        phi = 0.35 * math.sin(math.pi * u) - 0.1 * smooth(.8, 1, u)
        return np.array([x, y]), phi
    if u < .3:
        phi = ph0 + (0.75 - ph0) * smooth(0, .3, u)
    elif u < .85:
        phi = 0.75 + (-0.26 - 0.75) * smooth(.3, .85, u)
    else:
        phi = -0.26 * (1 - smooth(.85, 1.0, u))
    return np.array([x, y]), phi


def contacts(t0, t1, side=None):
    return [c for c in PL["C"] if t0 <= c[0] <= t1 and (side is None or c[1] == side)]


def run_pose(t, expr=None, held=None, foot=None, mug=None):
    hip = hip_at(t)
    feet = {s: foot_at(s, t, hip) for s in ("n", "f")}
    cn = [c for c in PL["C"] if c[1] == "n"]
    prev = max([c for c in cn if c[0] <= t], key=lambda c: c[0], default=cn[0])
    psi = 2 * math.pi * (t - prev[0]) / (2 * prev[5])
    walk = C.get("walk")
    arms = {}
    for s_, sg in (("n", 1), ("f", -1)):
        sw = -sg * math.cos(psi)
        if walk:
            arms[s_] = ("ang", 0.05 + 0.32 * sw, 0.5 + 0.2 * max(0, sw))
        else:
            amp = 1.05
            arms[s_] = ("ang", 0.1 + amp * sw, 1.5 + 0.4 * max(0, sw) - 0.4 * max(0, -sw))
    vy = (hip_at(t)[1] - hip_at(t - .05)[1]) / .05
    lean = (0.36 if not walk else 0.06) + C.get("lean_add", lambda t: 0.0)(t)
    p = dict(hip=hip, lean=lean, feet=feet, arms=arms, hands={"n": "fist", "f": "fist"}, head_ang=-0.12 if not walk else 0.02,
             hood=clamp(-vy * 0.05, -16, 22), strings=(clamp(-vy * .04, -30, 30) - 22, clamp(vy * .05, -20, 30)),
             expr=dict(lid=0.95, look=(0.5, -0.05), brows="worry", mouth="flat", hair=clamp(vy * 0.04, -18, 18)))
    if expr:
        p["expr"].update(expr)
    if held is not None:
        p["held_shoe"] = ("n", held)
    if foot:
        p["foot"] = foot
    if mug:
        p["held"] = ("front", mug)
        p["held_side"] = "n"
    return p


# ═════════════════════════ камера бега ═════════════════════════
def track_cam(t, s, sx, gy, shake=1.0, drift=1.0):
    """Трекинг за тазом: таз на экране x = sx, земля на экране y = gy; тряска на каждой опоре 6–10 px, боковой занос."""
    h = (hip_at(t, bob=False) + hip_at(t + .08, bob=False)) / 2
    cx = h[0] + (540 - sx) / s
    cy = (960 - gy) / s
    dy = 0.0
    dx = 0.0
    if shake:
        for i, c in enumerate(contacts(t - 0.4, t)):
            amp = 7.0 + 3.0 * ((int(c[2]) // 7) % 2)
            dy += amp * kick(t, c[0], .03, .07) * math.cos(2 * math.pi * 9 * max(0, t - c[0] - .03))
            dx += (2.5 if i % 2 else -2.5) * kick(t, c[0], .03, .07)
        dy *= shake
        dx *= shake
    dx += drift * (16 * math.sin(t * 2.6 + .4) + 7 * math.sin(t * 5.3))
    rot = drift * (0.7 * math.sin(t * 1.9 + .3)) + shake * 0.25 * dy / 8
    return cx - dx / s, cy - dy / s, s, rot


def hook_wrap(body, t, hit):
    """Влёт правил 28–29 поверх кадра (anim.hook_cam): масштаб, поворот, занос, радиальное размытие копиями."""
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    tr = f"translate({540 + dx:.2f} {PIV + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-PIV})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<g opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {PIV + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-PIV})">{body}</g>')
    return f'<rect width="1080" height="1920" fill="#a9cfe9"/><g transform="{tr}">{body}</g>{blur}'


PIV = 560.0     # центр влёта и удара — у головы Димы: удар на «вовремя» не уводит голову под заголовок


MASK_F = '<filter id="mk82"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def mask_svg(world_mask, cam):
    lib.DEFS.append(MASK_F)
    return lib.svg('<rect width="1080" height="1920" fill="#000"/>'
                   f'<g transform="{lib.cam(*cam)}"><g filter="url(#mk82)">{world_mask}</g></g>')




# ═════════════════════════ телефон в руке бегущего (в L-единицах rdima) ═════════════════════════
PH_BODY, PH_SCREEN = "#2b2e36", "#9fd6ff"


def phone_L(rot_deg=-62.0, glow=1.0, scroll=0.0):
    """Функция для pose["held"]: телефон в кулаке ближней руки, экран к лицу (повёрнут rot_deg), свет экрана."""
    def fn(Wr, d):
        c = Wr + d * 26
        o = []
        if glow > 0.01:
            g = lib.rad_grad([(0, "#d8f2ff", .32 * glow), (1, "#d8f2ff", 0)], c[0] - 20, c[1] - 40, 150)
            o.append(f'<circle cx="{c[0] - 20:.1f}" cy="{c[1] - 40:.1f}" r="150" fill="url(#{g})"/>')
        body = lib.T(lib.rrect(-30, -66, 30, 66, 12), c[0], c[1], 1.0, rot_deg)
        scr = lib.T(lib.rrect(-24, -58, 24, 58, 8), c[0], c[1], 1.0, rot_deg)
        inner = blob(scr, PH_SCREEN)
        for k in range(4):                                # «лента» листается: цветные карточки без букв
            y = -50 + ((k * 30 + scroll * 120) % 120)
            card = lib.T(lib.rrect(-19, y, 19, y + 20, 4), c[0], c[1], 1.0, rot_deg)
            inner += blob(card, ("#ff8a7a", "#ffd166", "#7bd389", "#c9a7ff")[k], .9)
        o.append(dima.shape(body, PH_BODY, inner, w=3.6, seed=2501))
        return "".join(o)
    return fn


# ═════════════════════════ общие помощники планов в комнатах ═════════════════════════
import cat as CT  # noqa: E402

FL = 1240.0                       # пол комнат (мир = кадр при камере (540, 960, 1))
GOLD, GOLD_SH = "#f2b84b", "#c98a22"


def ws(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up=.08, down=.3):
    """0 → 1 за up, затухание за down."""
    u = t - a
    if u <= 0:
        return 0.0
    return min(1.0, u / up) * (math.exp(-(u - up) / down) if u > up else 1.0)


def shake(t, a, amp=10.0, dur=.35, f=11.0):
    u = t - a
    if u <= 0 or u > dur * 3:
        return 0.0, 0.0
    e = math.exp(-u / dur * 2.5)
    return amp * e * math.sin(2 * math.pi * f * u), amp * .6 * e * math.cos(2 * math.pi * f * .8 * u)


def view(body, cx, cy, s, rot=0.0, bg="#e9dcc6", over=""):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def shadow(x, y, rx, op=.2):
    return blob(ellipse_pts(x, y, rx, rx * .13, 20), "#3a2a1c", op)


ROOM = dict(wall="#eadcc4", wall_sh="#d9c6a8", floor="#b98d64", floor_sh="#a07650", base="#f4ead8", ln="#8a6a4c")


def room(x0=-1200.0, x1=2400.0, wall=None, floor=None, seed=0):
    P = dict(ROOM)
    if wall:
        P["wall"], P["wall_sh"] = wall, lib.mul(wall, (.93, .92, .9))
    if floor:
        P["floor"], P["floor_sh"] = floor, lib.mul(floor, (.88, .86, .84))
    o = [rect(x0, -1400, x1, FL, P["wall"])]
    g = lib.lin_grad([(0, P["wall_sh"], .0), (1, P["wall_sh"], .9)], 0, -800, 0, FL, units="userSpaceOnUse")
    o.append(f'<rect x="{x0}" y="-1400" width="{x1 - x0}" height="{FL + 1400}" fill="url(#{g})"/>')
    o.append(rect(x0, FL, x1, FL + 1400, P["floor"]))
    for k in range(int((x1 - x0) / 170) + 1):
        x = x0 + k * 170
        o.append(line([(x, FL + 4), (x - 120, FL + 700)], 2.0, P["floor_sh"], seed=3300 + seed + k, op=.6))
    o.append(shape(lib.rect_pts(x0, FL - 26, x1, FL + 4), P["base"], "", w=3.6, seed=3290 + seed))
    return "".join(o)


def window(x0, y0, x1, y1, sky="#9fd2f2", t=0.0, sun=None, moon=None):
    o = [shape(lib.rect_pts(x0 - 18, y0 - 18, x1 + 18, y1 + 18), "#f6eee0", "", w=4.4, seed=3400)]
    o.append(rect(x0, y0, x1, y1, sky))
    if sun is not None:
        g = lib.rad_grad([(0, "#fff7d0", .9), (1, "#fff7d0", 0)], sun[0], sun[1], 110)
        o.append(f'<circle cx="{sun[0]:.1f}" cy="{sun[1]:.1f}" r="110" fill="url(#{g})"/>'
                 f'<circle cx="{sun[0]:.1f}" cy="{sun[1]:.1f}" r="38" fill="#ffe27a"/>')
    if moon is not None:
        o.append(f'<circle cx="{moon[0]:.1f}" cy="{moon[1]:.1f}" r="32" fill="#f4f0dc"/>'
                 f'<circle cx="{moon[0] + 14:.1f}" cy="{moon[1] - 8:.1f}" r="28" fill="{sky}"/>')
    inner = "".join(o[1:])
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    out = o[0] + f'<g clip-path="url(#{c})">{inner}</g>'
    out += line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], 6, "#f6eee0", taper=0, wmin=1, seed=3401)
    out += line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], 6, "#f6eee0", taper=0, wmin=1, seed=3402)
    out += f'<path d="{lib.ink_closed(lib.rect_pts(x0, y0, x1, y1), 4.0, seed=3403)}" fill="{INK}"/>'
    return out


def sofa(x0, x1, y, col="#5a7fb5"):
    """Диван: сиденье верхом на y; спинка выше, подлокотники по краям."""
    sh = lib.mul(col, (.82, .82, .86))
    o = [shape(lib.rrect(x0 + 40, y - 330, x1 - 40, y + 20, 40), sh, "", w=5, seed=3500)]
    o.append(shape(lib.rrect(x0 + 60, y - 20, x1 - 60, y + 150, 30), col, blob(lib.rect_pts(x0 + 60, y + 90, x1 - 60, y + 150), sh, .6), w=5, seed=3501))
    for k, (a, b) in enumerate(((x0 - 10, x0 + 110), (x1 - 110, x1 + 10))):
        o.append(shape(lib.rrect(a, y - 130, b, y + 160, 45), col, blob(lib.rect_pts(a, y + 40, b, y + 160), sh, .5), w=5, seed=3502 + k))
    for x in (x0 + 40, x1 - 60):
        o.append(rect(x, y + 160, x + 22, y + 200, "#5b3d26"))
    return "".join(o)


def phone_up(x, y, k=1.0, rot=0.0, glow=1.0, scroll=0.0, feed=True, dim=0.0):
    """Телефон экраном к зрителю (ЦЕНТР x, y; 120×240·k), без букв: цветные карточки ленты листаются."""
    o = []
    if glow > .01:
        g = lib.rad_grad([(0, "#d8f2ff", .35 * glow), (1, "#d8f2ff", 0)], x, y, 260 * k)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{260 * k:.1f}" fill="url(#{g})"/>')
    body = lib.T(lib.rrect(-60, -120, 60, 120, 18), x, y, k, rot)
    scr = lib.T(lib.rrect(-50, -106, 50, 106, 10), x, y, k, rot)
    inner = blob(scr, lib.mix(PH_SCREEN, "#3b4250", dim))
    if feed:
        for j in range(6):
            yy = -100 + ((j * 42 + scroll * 160) % 252) - 20
            card = lib.T(lib.rrect(-42, yy, 42, yy + 30, 6), x, y, k, rot)
            inner += blob(card, ("#ff8a7a", "#ffd166", "#7bd389", "#c9a7ff", "#ff9ec7", "#6cc4ff")[j], .9 * (1 - dim))
    c = lib.clip_of(scr)
    o.append(shape(body, PH_BODY, f'<g clip-path="url(#{c})">{inner}</g>', w=4.0 * max(.6, k), seed=3600))
    return "".join(o)


def fig(x, y, sc, expr, pose=None, feet="stand", lean=None, head_ang=None, arms=None, hands=None, layers=None, flip=False):
    kw = {}
    if pose:
        kw.update(people.pose_kw(pose, x, y, sc))
    if feet == "stand":
        kw.update(people.stand_kw(x, y, sc))
    elif feet == "sit":
        kw.update(people.sit_kw(x, y, sc))
    elif isinstance(feet, dict):
        kw["feet"] = feet
    if lean is not None:
        kw["lean"] = lean
    if head_ang is not None:
        kw["head_ang"] = head_ang
    if arms is not None:
        kw["arms"] = arms
    if hands is not None:
        kw["hands"] = hands
    return people.figure("dima", x, y, sc, expr=expr, layers=layers, flip=flip, **kw)


def dima_phone(x, y, sc, expr, t, feet="stand", lean=0.12, glow=1.0, ph_k=None, scroll_v=1.6, extra_arms=None, head_ang=0.32):
    """Дима держит телефон двумя руками перед грудью и смотрит в экран. -> (svg, res, точка телефона)."""
    arms = {"f": ("ik", (x + 215 * sc, y - 285 * sc), -1), "n": ("ik", (x + 305 * sc, y - 290 * sc), -1)}
    if extra_arms:
        arms.update(extra_arms)
    hands = {"f": {"dir": (.9, -.3), "curl": (.55, .55, .6, .62), "thumb": .5}, "n": {"dir": (-.6, -.7), "curl": (.6, .6, .65, .68), "thumb": .6}}
    base = fig(x, y, sc, expr, feet=feet, lean=lean, head_ang=head_ang, arms=arms, hands=hands, layers=("legs", "pelvis", "arm_f", "body"))
    near = fig(x, y, sc, expr, feet=feet, lean=lean, head_ang=head_ang, arms=arms, hands=hands, layers=("arm_n",))
    wf, wn = np.array(base["wrist"]["f"]), np.array(base["wrist"]["n"])
    pp = (wf + wn) / 2 + np.array([10 * sc, -40 * sc])
    ph = phone_up(pp[0], pp[1], (ph_k or 0.9) * sc / .5 * .5, -14, glow, t * scroll_v)
    return base["svg"] + ph + near["svg"], base, pp


def cat(x, y, k, t, **st):
    return CT.draw(x, y, k, st, t)


def gold_drop(x, y, k=1.0, rot=0.0):
    return PR.drop(x, y, k, rot, col=GOLD)


def grains(pts, t, n=30, seed=0, k=1.0, speed=1.0, up=False, col=GOLD):
    """Песчинки летят по ломаной pts (от начала к концу) непрерывной струёй."""
    P_ = np.array(pts, float)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P_, axis=0), axis=1))]
    o = []
    rs = np.random.RandomState(5100 + seed)
    for i in range(n):
        ph = (rs.uniform() + t * speed) % 1.0
        d = ph * seg[-1]
        j = min(len(seg) - 2, int(np.searchsorted(seg, d) - 1))
        j = max(j, 0)
        u = (d - seg[j]) / max(1e-6, seg[j + 1] - seg[j])
        p = P_[j] + (P_[j + 1] - P_[j]) * u + rs.uniform(-12, 12, 2) * k
        r = rs.uniform(4, 8) * k
        o.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r:.1f}" fill="{col}" stroke="{INK}" stroke-width="{1.6 * k:.2f}"/>')
    return "".join(o)


def bez(a, c, b, n=16):
    a, c, b = map(np.array, (a, c, b))
    return [tuple((1 - u) ** 2 * a + 2 * u * (1 - u) * c + u * u * b) for u in np.linspace(0, 1, n)]


def dark(op, col="#14183a"):
    return f'<rect x="-3000" y="-3000" width="7000" height="7000" fill="{col}" opacity="{op:.3f}"/>' if op > .005 else ""




# ═════════════════════════ поправки рилса 88 к общей части ═════════════════════════
def title(t):
    """Заголовок хука «7 ДНЕЙ / БЕЗ ТЕЛЕФОНА»: экранный слой s01–s03, уходит сжатием к ~3.5 с."""
    if NOCAM or MASK:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


import cat as CT  # noqa: E402,F811

FL = 1240.0


def back_out(u, s=1.7):
    return lib.back_out(u, s)


# ═════════════════════════ отрывной календарь (точки вместо цифр) ═════════════════════════
DAYS = [(42, 1), (50, 3), (57, 5), (62, 7)]          # слово «День» → число точек на новом листке


def _leaf(x, y, k, n, seed=0, rot=0.0, op=1.0):
    """Листок календаря (центр x, y; 200×230·k): пустая красная шапка без букв, n точек вместо числа."""
    pts = lib.T(lib.rrect(-100, -100, 100, 130, 10), x, y, k, rot)
    inner = blob(lib.T(lib.rect_pts(-100, -100, 100, -48), x, y, k, rot), "#e2574c")
    inner += blob(lib.T(lib.rect_pts(-100, 110, 100, 130), x, y, k, rot), "#efe6d6")
    pos = [(-60, -5), (-20, -5), (20, -5), (60, -5), (-40, 55), (0, 55), (40, 55)]
    order = [0, 1, 2, 3, 4, 5, 6] if n != 1 else [5]
    if n == 3:
        order = [4, 5, 6]
    if n == 5:
        order = [0, 1, 2, 3, 5]
    for j in order[:n]:
        px, py = lib.T([pos[j]], x, y, k, rot)[0][:2]
        inner += blob(ellipse_pts(px, py, 15 * k, 15 * k, 12), "#f28a2e") + blob(ellipse_pts(px - 4 * k, py - 5 * k, 5 * k, 4 * k, 8), "#ffd9a8")
    g = shape(pts, "#fbf7ee", inner, w=3.4 * max(k, .5), seed=9100 + seed)
    return g if op >= .999 else f'<g opacity="{op:.3f}">{g}</g>'


def calendar(x, y, k, t, n_before=0, tears=(), board=True):
    """Отрывной календарь (центр листка x, y). tears — [(t_tear, n_new)]: на t_tear верхний листок срывается и улетает
    (переворот, падение влево вниз), под ним новый с n_new точками."""
    o = []
    if board:
        o.append(shape(lib.T(lib.rrect(-122, -150, 122, 150, 16), x, y, k), "#8a5a38", "", w=3.6 * k, seed=9150))
    n_cur, flying = n_before, None
    for tt, nn in tears:
        if t >= tt:
            flying = (tt, n_cur)
            n_cur = nn
    o.append(_leaf(x, y + 4 * k, k, n_cur, seed=1))
    if flying is not None:
        u = (t - flying[0]) / 0.5
        if u < 1:
            ue = ease_in_(u)
            fx = x - 260 * k * ue - 30 * k * math.sin(u * 9)
            fy = y - 40 * k * math.sin(math.pi * min(1, u * 1.6)) + 520 * k * ue * ue
            o.append(_leaf(fx, fy, k * (1 - .25 * u), flying[1], seed=2, rot=-80 * ue + 12 * math.sin(u * 14), op=1 - u ** 3))
    for dx in (-60, 60):                                            # кольца
        o.append(line(lib.T([(dx - 10, -132), (dx - 12, -112), (dx, -96), (dx + 12, -112), (dx + 10, -132)], x, y, k), 7 * k, "#7d838e",
                      taper=.1, wmin=.7, seed=9160 + dx))
    return "".join(o)


def ease_in_(u):
    return clamp(u) ** 2


def cal_corner(t):
    """Календарь-счётчик дней в правом верхнем углу кадра (экранный слой), с 15.56 до 28.02 с."""
    return calendar(905, 330, 0.82, t, 0, [(W(i), n) for i, n in DAYS])


# ═════════════════════════ шкафчик ═════════════════════════
def locker(x, yb, k, door=0.0, lock=0.0, inner=""):
    """Тумба-шкафчик на полу (центр низа x, yb), 300×380·k; дверца на петлях справа: door 0 — закрыта, 1 — распахнута к
    зрителю вправо. inner — что лежит внутри (видно, пока дверца открыта). lock 0…1 — навесной замочек проявляется."""
    x0, x1, y0 = x - 150 * k, x + 150 * k, yb - 380 * k
    o = [blob(ellipse_pts(x + 10 * k, yb + 6 * k, 190 * k, 18 * k, 16), "#2a1e14", .2)]
    body = lib.rect_pts(x0, y0, x1, yb)
    o.append(shape(body, "#b98252", blob(lib.rect_pts(x1 - 30 * k, y0, x1, yb), "#9a6a42", .9), w=4.4 * k, seed=9200))
    o.append(shape(lib.rect_pts(x0 - 14 * k, y0 - 26 * k, x1 + 14 * k, y0 + 4 * k), "#c99463", blob(lib.rect_pts(x0 - 14 * k, y0 - 6 * k, x1 + 14 * k, y0 + 4 * k), "#a87648", .8),
                   w=4.0 * k, seed=9201))
    o.append(rect(x0 + 20 * k, yb, x0 + 40 * k, yb + 16 * k, "#5b3d26") + rect(x1 - 40 * k, yb, x1 - 20 * k, yb + 16 * k, "#5b3d26"))
    d = clamp(door)
    ix0, iy0, ix1, iy1 = x0 + 18 * k, y0 + 18 * k, x1 - 18 * k, yb - 18 * k
    if d > 0.01:
        o.append(rect(ix0, iy0, ix1, iy1, "#3a2618"))
        o.append(rect(ix0, (iy0 + iy1) / 2 - 6 * k, ix1, (iy0 + iy1) / 2 + 6 * k, "#6b4a30"))
        c = lib.clip_rect(ix0, iy0, ix1 - ix0, iy1 - iy0)
        o.append(f'<g clip-path="url(#{c})">{inner}</g>')
    # дверца: петли справа (ix1); открытая — узкая и шире наружу (вид в перспективе)
    wdoor = (ix1 - ix0) * (1 - .82 * d)
    ext = 70 * k * math.sin(math.pi * .5 * d)
    dp = [(ix1 - wdoor, iy0 - ext * .25, 1), (ix1, iy0, 1), (ix1, iy1, 1), (ix1 - wdoor, iy1 + ext * .25, 1)]
    if d > 0.01:
        dp = [(ix1, iy0, 1), (ix1 + wdoor * .9 + ext * .1, iy0 - ext * .5, 1), (ix1 + wdoor * .9 + ext * .1, iy1 + ext * .5, 1), (ix1, iy1, 1)]
    o.append(shape(dp, "#c8915e", blob([(p[0], p[1]) for p in dp[:2]] + [(dp[1][0], dp[1][1] + 30 * k), (dp[0][0], dp[0][1] + 30 * k)], "#dcae7c", .7),
                   w=4.2 * k, seed=9202))
    if d < 0.5:
        kx = ix1 - wdoor + 34 * k
        o.append(shape(ellipse_pts(kx, (iy0 + iy1) / 2, 13 * k, 13 * k, 12), "#e8c26a", "", w=3 * k, seed=9203))
        if lock > 0.01:
            lk = back_out(clamp(lock))
            lx, ly = kx + 4 * k, (iy0 + iy1) / 2 + 52 * k
            o.append(line([(lx - 18 * k * lk, ly), (lx - 18 * k * lk, ly - 26 * k * lk), (lx, ly - 40 * k * lk), (lx + 18 * k * lk, ly - 26 * k * lk),
                           (lx + 18 * k * lk, ly)], 6 * k, "#7d838e", taper=.1, wmin=.8, seed=9204))
            o.append(shape(lib.rrect(lx - 26 * k * lk, ly - 4 * k, lx + 26 * k * lk, ly + 40 * k * lk, 8 * k), "#e0b24a",
                           blob(ellipse_pts(lx, ly + 16 * k * lk, 5 * k, 7 * k, 8), "#5b4320"), w=3.4 * k, seed=9205))
    return "".join(o)


# ═════════════════════════ хук s01: кот с телефоном в зубах, Дима гонится ═════════════════════════
def mouth_phone(t, b, swing=0.0):
    """Телефон в зубах кота (координаты головы, рот ≈ (12, 70)): держит поперёк, экран светится, мотается от галопа."""
    p = b["p"]
    a = 8 + 10 * math.sin(2 * math.pi * p - .9)
    o = (f'<g transform="translate(34 96) rotate({a:.2f}) scale(1.3)">'
         f'{shape(lib.rrect(-78, -26, 78, 26, 12), PH_BODY, blob(lib.rrect(-68, -18, 68, 18, 8), PH_SCREEN), w=4.2, seed=9300)}'
         f'{blob(lib.rrect(-60, -12, -10, 4, 4), "#ff8a7a", .9)}{blob(lib.rrect(0, -12, 50, 4, 4), "#ffd166", .9)}</g>')
    o += line([(-10, 80), (6, 92), (22, 86)], 4, INK, seed=9301)          # зубы-клычок прикусывают
    return o


Cat.mouth_shoe = mouth_phone

HOOK = dict(a=-0.6, b=T1("s01") + 0.4, x0=0.0, tc=0.18, st=0.55, step=228.0, leap=None, stumble=None, lean_add=lambda t: -0.02)


def REL01(t):
    return 205.0 + 95.0 * smooth(-0.2, T1("s01") + .2, t)


def dima_chase(t):
    ex = dict(lid=1.0, look=(0.9, 0.15), brows="worry", mouth="pant", hair=0.0)
    p = run_pose(t, expr=ex)
    hip = np.array(p["hip"])
    wob = math.sin(t * 13)
    p["arms"]["n"] = ("ik", tuple(hip + np.array([300.0 + 20 * wob, -290.0 + 18 * math.sin(t * 11)])), -1)
    p["arms"]["f"] = ("ik", tuple(hip + np.array([270.0 - 16 * wob, -250.0 + 14 * math.sin(t * 9 + 1)])), -1)
    p["hands"] = {"n": ("open", 0.35 + .25 * (.5 + .5 * math.sin(t * 17))), "f": ("open", 0.3 + .25 * (.5 + .5 * math.sin(t * 15 + 1)))}
    p["head_ang"] = -0.18
    p["lean"] = 0.42
    return p


def hall_world(cam):
    """Длинная прихожая в мире бега (земля y = 0): обои полосами, плинтус, доски пола, рамки-картинки и двери."""
    cx, cy, s, rot = cam
    a, b = cx - 1000 / s - 300, cx + 1000 / s + 300
    o = [rect(a, -2400, b, 0, "#e9d6b4")]
    g = lib.lin_grad([(0, "#cfb894", .0), (1, "#cfb894", .8)], 0, -1400, 0, 0, units="userSpaceOnUse")
    o.append(f'<rect x="{a:.0f}" y="-2400" width="{b - a:.0f}" height="2400" fill="url(#{g})"/>')
    for i in range(int(a // 110), int(b // 110) + 1):
        x = i * 110.0
        o.append(rect(x, -2400, x + 4, -60, "#dcc49e", .8))
    for i in range(int(a // 900) - 1, int(b // 900) + 2):          # рамки и двери вдоль стены
        x = i * 900.0
        if i % 3 == 0:
            o.append(shape(lib.rect_pts(x - 230, -1080, x + 230, -60), "#f4ead8", rect(x - 200, -1050, x + 200, -60, "#c99a6b"), w=4, seed=9400 + i % 7))
            o.append(shape(ellipse_pts(x + 150, -540, 16, 16, 10), "#e8c26a", "", w=3, seed=9410))
        else:
            col = ("#9fc4d8", "#e6b8a6", "#b9d3a0")[i % 3]
            o.append(shape(lib.rect_pts(x - 140, -820, x + 140, -580), "#8a5a38", rect(x - 118, -798, x + 118, -602, col)
                           + blob([(x - 118, -640), (x - 40, -720), (x + 30, -660), (x + 118, -740), (x + 118, -602), (x - 118, -602)], lib.mul(col, (.8, .82, .8)), .9),
                           w=4, seed=9420 + i % 5))
    o.append(shape(lib.rect_pts(a, -60, b, 4), "#f4ead8", "", w=3.6, seed=9430))
    o.append(rect(a, 0, b, 1400, "#b58457"))
    gf = lib.lin_grad([(0, "#c4935f", 1), (1, "#8a5a38", 1)], 0, 0, 0, 900, units="userSpaceOnUse")
    o.append(f'<rect x="{a:.0f}" y="0" width="{b - a:.0f}" height="1400" fill="url(#{gf})"/>')
    for j, y in enumerate((70, 170, 300, 470, 700)):
        o.append(line([(a, y), (b, y)], 3, "#6e4628", seed=9440 + j, op=.55))
    for i in range(int(a // 330), int(b // 330) + 1):
        x = i * 330.0 + (i % 2) * 140
        y0 = (70, 170, 300, 470)[i % 4]
        o.append(line([(x, y0), (x - 20, y0 + 90)], 2.4, "#6e4628", seed=9450 + i % 9, op=.45))
    return "".join(o)


def _setup(conf):
    plan(conf)
    Cat._grid.clear()
    Cat.SPAN[0], Cat.SPAN[1] = conf["a"] - 0.6, conf["b"] + 1.0


def chase_frame(t, s, sx, gy, hook=False, rot_add=0.0):
    _setup(HOOK)
    Cat.REL_FN[0] = REL01
    cam = track_cam(t, s, sx, gy, shake=0.0 if NOCAM else 1.0, drift=0.0 if NOCAM else 1.0)
    cam = (cam[0], cam[1], cam[2], cam[3] + rot_add * (0 if NOCAM else 1))
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    dg, _ = dima.draw(dima_chase(t))
    cs = Cat.state(t, lambda tt: hip_at(tt, bob=False)[0], C["step"] / C["tc"])
    cs["shoe"] = 0.0
    cs["look"] = (0.9, -0.1)
    cs["blinks"] = (0.95,)
    cg = Cat.draw(cs, t) + Cat.sparks(cs, t)
    if MASK:
        return mask_svg(dg + cg, cam)
    sh = f'<g opacity=".18" transform="matrix(1 0 -0.9 -0.22 0 0)">{dg}</g>'
    body = f'<g transform="{lib.cam(*cam)}">{hall_world(cam)}{sh}{dg}{cg}</g>'
    if NOCAM:
        return lib.svg(body)
    if hook:
        return lib.svg(hook_wrap(body, t, stress(1, .5)) + title(t))
    return lib.svg(f'<rect width="1080" height="1920" fill="#e9d6b4"/>{body}' + title(t))


def frame_s01(t):
    return chase_frame(t, 2.15, 250.0, 1680.0, hook=True)


# ═════════════════════════ s02: телефон в шкафчик, кот захлопывает дверцу ═════════════════════════
LK = (640.0, FL, 1.35)            # шкафчик: центр низа, масштаб
SLAM = stress(6, .55)             # «наконЕц» — дверца хлопает


def locker_room():
    o = [room(-900, 2200, wall="#e9d6b4")]
    o.append(shape(lib.rect_pts(80, 420, 380, 700), "#8a5a38", rect(102, 442, 358, 678, "#9fc4d8")
                   + blob([(102, 640), (190, 560), (260, 610), (358, 540), (358, 678), (102, 678)], "#7fa6bc", .9), w=4, seed=9500))
    return "".join(o)


def frame_s02(t):
    a = T0("s02")
    x, yb, k = LK
    thr = W(4) - .05                                   # «телефона»: телефон влетает в шкафчик
    door = 1.0 - smooth(SLAM - .16, SLAM, t)
    inner = ""
    u = (t - thr) / .34
    land = (x - 30, yb - 120)
    if u >= 1:
        inner = PR.phone_flat(land[0], land[1], .62, 0, 10, face_down=False, glow_=.5)
    o = [locker_room()]
    o.append(locker(x, yb, k, door, lock=smooth(SLAM + .12, SLAM + .4, t), inner=inner))
    if 0 <= u < 1:                                      # летит по дуге, кувыркаясь
        px = -40 + (land[0] + 40) * u
        py = 760 + (land[1] - 760) * u - 300 * math.sin(math.pi * u)
        o.append(phone_up(px, py, .5, 360 * u * 1.3, .8, t * 2))
    elif u < 0:
        o.append(phone_up(-40 + 60 * (t - a) / .2, 760, .5, -20, .8, t * 2))
    # Дима слева тянет руки к шкафчику, хватает воздух
    reach = smooth(a - .2, a + .3, t) * (1 - .6 * smooth(SLAM + .1, SLAM + .5, t))
    dx_ = 150 + 70 * reach
    hipy = 880.0
    sc = .62
    hand_t = lambda dd, oy: (dx_ + (300 + 120 * reach) * sc * 1.0 + dd, hipy - 330 * sc + oy + 10 * math.sin(t * 12 + dd))
    arms = {"n": ("ik", hand_t(40, 30), -1), "f": ("ik", hand_t(0, -10), -1)}
    gr = .5 + .5 * math.sin(t * 16)
    hands = {"n": {"dir": (1, -.1), "curl": (.2 + .5 * gr,) * 4, "spread": .3, "thumb": .3}, "f": {"dir": (1, -.2), "curl": (.2 + .5 * (1 - gr),) * 4, "thumb": .3}}
    ex = dict(people.EXPR["dima"]["gape"]) if t < SLAM else dict(people.EXPR["dima"]["surprise_day"])
    ex["look"] = (.8, .3)
    o.append(shadow(dx_, FL + 14, 160))
    o.append(fig(dx_, hipy, sc, ex, feet="stand", lean=.28 * reach, head_ang=.05, arms=arms, hands=hands)["svg"])
    # кот: прыжок слева на шкафчик (через кадр), сидит на крышке, лапой захлопывает дверцу вправо-вниз
    j0, j1 = a, a + .55
    top = yb - 380 * k - 26 * k
    if t < j1:
        o.append(people.cat_jump((x - 520, FL + 10), (x + 30, top), .62, clamp((t - j0) / (j1 - j0)), t, {"look": (.6, .2)}, height=260))
    else:
        pw = smooth(SLAM - .3, SLAM - .05, t) * (1 - smooth(SLAM + .3, SLAM + .6, t))
        o.append(cat(x + 30, top, .62, t, look=(.5, .7 * pw + .1), paw=pw, paw_dx=90, tilt=-6 * pw, sy=1 - .06 * bump(t, SLAM), sx=1 + .05 * bump(t, SLAM)))
    o.append(PR.dust_puff(x + 140 * k, yb - 40, 1.4, clamp((t - SLAM) / .5), seed=3))
    dx, dy = shake(t, SLAM, 16)
    z = 1.3 + .05 * ramp(t, a, 1.5) + .06 * bump(t, SLAM)
    return view("".join(o), 520 + dx, 920 + dy, z, -1.0 + 2 * ramp(t, a, 1.5), bg="#e9d6b4", over=title(t))


# ═════════════════════════ s03: результат — высыпается, потягивается утром ═════════════════════════
def bedroom_morning(t, warm=1.0):
    o = [room(-900, 2200, wall="#f3dcb4")]
    o.append(window(560, 300, 960, 760, "#bfe6f7", t, sun=(840, 420)))
    g = lib.rad_grad([(0, "#fff3c4", .55 * warm), (1, "#fff3c4", 0)], 760, 560, 700)
    o.append(f'<rect x="-900" y="-400" width="3100" height="2400" fill="url(#{g})"/>')
    o.append(blob([(560, 760), (960, 760), (1100, FL + 300), (360, FL + 300)], "#fff1c0", .35 * warm))
    return "".join(o)


def frame_s03(t):
    a = T0("s03")
    o = [bedroom_morning(t)]
    o.append(PR.bed(360, FL, 1.25, seed=1))
    o.append(PR.blanket(470, FL - 148, 1.2, w=520, h=90, seed=2))
    us = clamp((t - (a - .05)) / 1.15)
    x, y = 300.0, FL - 150
    f_ = people.dima_chair78(x, y, .6, u_stretch=us, t=t)
    o.append(f_["svg"])
    o.append(cat(720, FL - 150, .55, t, look=(-.5, -.5), blink=.9 if abs(t - stress(7, .5)) < .25 else 0.0, tail=10 * math.sin(t * 4)))
    o.append(PR.sparkles(f_["head"][0], f_["head"][1] - 150, 1.2, smooth(W(7), W(7) + .2, t), t, seed=3))
    z = 1.42 + .08 * ease_io(ramp(t, a, 1.2))
    return view("".join(o), 450, 800, z, .6 * math.sin(t * 2), over=title(t))


# ═════════════════════════ три боли: ночь, будильник, книга ═════════════════════════
BED = (520.0, FL, 1.3)


def night_room(t, sky="#141a3e", wall="#2b3360", moon=True):
    o = [room(-900, 2200, wall=wall, floor="#4a3a4e")]
    o.append(window(620, 260, 980, 640, sky, t, moon=(860, 360) if moon else None))
    for i, (sx, sy) in enumerate(((700, 330), (760, 520), (930, 560), (680, 600))):
        if moon:
            o.append(PR.star4(sx, sy, 8 + 3 * math.sin(t * 3 + i), 1.0))
    return "".join(o)


def bed_with(t, expr, cover="chest", seed=0):
    bx, by, bk = BED
    o = [PR.bed(bx, by, bk, seed=seed)]
    d = people.dima_bed(bx - 60, by - 118 * bk - 30, .6, expr=expr, t=t, cover=cover, seed=seed)
    o.append(d["svg"])
    return "".join(o), d


def frame_s04(t):
    a = T0("s04")
    o = [night_room(t)]
    fall = W(12) - .1
    hit = W(12) + .12
    ex = "dull" if t < hit else "wince"
    g, d = bed_with(t, ex)
    o.append(g)
    hx, hy = d["head"]
    u = clamp((t - fall) / (hit - fall))
    wr = np.array(d["wrist"]["n"], float)
    p0 = wr + np.array([-40.0, -110.0])
    p1 = np.array([hx - 10, hy - 40])
    if u < 1:
        pp = p0 + (p1 - p0) * np.array([u, u * u]) + np.array([0, 0])
        o.append(phone_up(pp[0], pp[1] + 6 * math.sin(t * 3) * (1 - u), .55, -20 + 104 * u * u, 1.3 - .5 * u, t * 2.2))
    else:
        o.append(f'<g transform="translate({hx - 10:.1f} {hy - 40:.1f}) rotate(84)">{phone_up(0, 0, .55, 0, .3, 0, feed=True, dim=.6)}</g>')
        o.append(PR.sparkles(hx, hy - 120, 1.0, clamp((t - hit) / .3), t, seed=5, col="#ffd166"))
    o.append(cat(980, FL + 10, .5, t, look=(-.8, -.6), blink=1.0 if abs(t - hit - .05) < .05 else 0.0))
    dx, dy = shake(t, hit, 18)
    z = 1.75 + .1 * ramp(t, a, 1.6) + .08 * bump(t, hit)
    return view("".join(o), hx + 200 + dx, hy - 100 + dy, z, 0, bg="#141a3e")


def alarm(x, y, k, t, ring=0.0):
    """Будильник с двумя чашками-звонками (центр циферблата x, y), без цифр; ring 0…1 — подпрыгивает и звенит дугами."""
    j = ring * abs(math.sin(t * 48)) * 18
    sh = ring * 8 * math.sin(t * 60)
    x, y = x + sh, y - j
    o = []
    for s_ in (-1, 1):
        o.append(line([(x + s_ * 50 * k, y + 70 * k), (x + s_ * 70 * k, y + 110 * k + j)], 8 * k, INK, seed=9700 + s_))
        o.append(shape(lib.T(ellipse_pts(0, 0, 40, 28, 14), x + s_ * 62 * k, y - 86 * k, k, s_ * 30 + 20 * ring * math.sin(t * 70)), "#e2574c", "", w=3.6 * k,
                       seed=9702 + s_))
    o.append(line([(x - 40 * k, y - 110 * k), (x, y - 128 * k), (x + 40 * k, y - 110 * k)], 7 * k, INK, seed=9705))
    o.append(PR.clock(x, y, 92 * k, angle_h=200, angle_m=0, seed=3, rim="#e2574c"))
    if ring > .05:
        for i in range(3):
            ph = (t * 3 + i / 3) % 1
            r = (130 + 120 * ph) * k
            for s_ in (-1, 1):
                pts = [(x + s_ * r * math.cos(math.radians(a_)), y - 60 * k + r * math.sin(math.radians(a_))) for a_ in range(-50, 51, 10)]
                if s_ < 0:
                    pts = [(2 * x - p[0], p[1]) for p in pts]
                o.append(line(pts, 7 * k * (1 - ph), "#e2574c", seed=9710 + i, op=ring * (1 - ph)))
    return "".join(o)


def frame_s05(t):
    a = T0("s05")
    o = [night_room(t, sky="#f2c9a0", wall="#8a7ea8", moon=False)]
    g, d = bed_with(t, {"brows": "tired", "mouth": "o", "open": .25, "shut": 1.0, "lid": 0.0}, cover="chest")
    o.append(g)
    hx, hy = d["head"]
    o.append(PR.zzz(hx + 60, hy - 200, 1.3, t, 1.0))
    tx = BED[0] - 620
    o.append(shape(lib.rect_pts(tx - 110, FL - 330, tx + 110, FL - 300), "#8a5a38", "", w=4, seed=9720))
    o.append(shape(lib.rect_pts(tx - 95, FL - 300, tx + 95, FL), "#a5703f", line([(tx - 80, FL - 160), (tx + 80, FL - 160)], 3, seed=9721), w=4, seed=9722))
    ring = smooth(a, a + .1, t) * (1 + .6 * bump(t, W(16), .05, .4))
    o.append(alarm(tx, FL - 440, .9, t, min(1.0, ring)))
    o.append(cat(BED[0] + 360, FL + 10, .55, t, look=(-.9, -.3), tilt=-10, ear=14 * math.sin(t * 30), blink=.8))
    dx, dy = shake(t, W(16), 14)
    z = 1.5 + .12 * ease_io(ramp(t, a, 1.1))
    cx = tx + 230 + 60 * ramp(t, a, 1.1)
    return view("".join(o), cx + dx, FL - 330 + dy, z, 1.5 * math.sin(t * 9) * bump(t, W(16), .05, .4))


def frame_s06(t):
    a = T0("s06")
    o = [night_room(t, sky="#1b2150", wall="#3a3560")]
    g = lib.rad_grad([(0, "#ffe0a0", .55), (1, "#ffe0a0", 0)], 520, 700, 520)
    o.append(f'<rect x="-900" y="-400" width="3100" height="2400" fill="url(#{g})"/>')
    o.append(PR.bed(BED[0], FL, BED[2], seed=2))
    slide = smooth(W(23) + .1, W(23) + .6, t)
    ub = 1.0 - .55 * slide
    x, y = 380.0, FL - 150
    sleepy = smooth(W(21), W(23) + .2, t)
    ex = dict(people.EXPR["dima"]["read78"])
    ex["lid"] = .55 - .5 * sleepy
    if sleepy > .7:
        ex.update(people.EXPR["dima"]["sleepy"], lid=.08)
    f_ = people.dima_chair78(x, y, .6, u_book=ub, t=t, expr=ex)
    o.append(f_["svg"])
    bx, by = f_["book_hand"]
    bl = 9 * smooth(W(20) - .05, W(20) + .4, t) + 4 * math.sin(t * 7) ** 2 * smooth(W(20), W(21), t)
    bk = PR.book_open(bx + 20, by + 40 + 80 * slide, 1.15, rot=-8 + 30 * slide, seed=4)
    if bl > .3:
        fid = lib.uid("bb")
        lib.DEFS.append(f'<filter id="{fid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{bl:.2f}"/></filter>')
        o.append(f'<g filter="url(#{fid})">{bk}</g><g opacity=".45" transform="translate({1.6 * bl:.1f} {-.8 * bl:.1f})" filter="url(#{fid})">{bk}</g>')
    else:
        o.append(bk)
    if t > W(23) + .3:
        o.append(PR.zzz(f_["head"][0] + 60, f_["head"][1] - 160, 1.0, t, smooth(W(23) + .3, W(23) + .6, t)))
    o.append(cat(BED[0] + 300, FL - 150, .5, t, look=(-.7, -.3), sleep=smooth(W(22), W(23) + .4, t)))
    z = 1.65 + .25 * ease_io(ramp(t, a, 1.6)) - .2 * slide
    return view("".join(o), bx + 20 - 40 * slide, by - 40 + 60 * slide, z, 0)


# ═════════════════════════ s07: календарь на стене ═════════════════════════
def frame_s07(t):
    a = T0("s07")
    o = [room(-900, 2200, wall="#e6d3b6")]
    cx_, cy_ = 560.0, 560.0
    o.append(calendar(cx_, cy_, 1.6, t, 0, [(W(28) - .05, 0)]))
    o.append(locker(900, FL, 1.0, 0.0, lock=1.0))
    o.append(cat(910, FL - 406, .5, t, look=(-.6, -.6), tilt=8 * math.sin(t * 6) * smooth(W(26), W(27), t)))
    reach = smooth(W(27) - .3, W(28) - .05, t) * (1 - smooth(W(28) + .1, W(28) + .5, t))
    hip = (220.0, 900.0)
    sc = .6
    rest = (hip[0] + 140 * sc, hip[1] - 60 * sc)
    tgt = (cx_ - 60, cy_ + 120)
    hn = (rest[0] + (tgt[0] - rest[0]) * reach, rest[1] + (tgt[1] - rest[1]) * reach)
    ex = dict(people.EXPR["dima"]["calm_smile"], look=(.6, -.6))
    o.append(shadow(hip[0], FL + 14, 150))
    o.append(fig(hip[0], hip[1], sc, ex, feet="stand", lean=.04, head_ang=-.1, arms={"n": ("ik", hn, -1), "f": ("ang", .1, .2)},
                 hands={"n": {"dir": (.7, -.7), "curl": (.6 * reach, .6 * reach, .65 * reach, .7 * reach), "thumb": .5}})["svg"])
    z = 1.2 + .5 * ease_io(ramp(t, a, T1("s07") - a))
    return view("".join(o), 520 + 40 * ramp(t, a, 1.3), 800 - 160 * ease_io(ramp(t, a, 1.3)), z, 0)


# ═════════════════════════ s08: призыв ═════════════════════════
def frame_s08(t):
    import story_cta_tg as tg
    press = W(31) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=os.path.join(STORY, "common"))


# ═════════════════════════ s09: «вместе с нами» — дай пять ═════════════════════════
def frame_s09(t):
    a = T0("s09")
    o = [room(-900, 2200, wall="#e6d3b6")]
    o.append(calendar(560, 420, 1.0, t, 0))
    lx = 720.0
    o.append(locker(lx, FL, 1.0, 0.0, lock=1.0))
    top = FL - 406
    hf = W(39) + .05
    u = smooth(hf - .35, hf, t) * (1 - smooth(hf + .5, hf + .8, t))
    hip = (330.0, 900.0)
    sc = .6
    rest = (hip[0] + 140 * sc, hip[1] - 60 * sc)
    meet = (lx - 70, top - 150)
    hn = (rest[0] + (meet[0] - rest[0]) * u, rest[1] + (meet[1] - rest[1]) * u)
    ex = dict(people.EXPR["dima"]["cheerful"], look=(.6, .2))
    o.append(shadow(hip[0], FL + 14, 150))
    o.append(fig(hip[0], hip[1], sc, ex, feet="stand", lean=.06 * u, head_ang=.05, arms={"n": ("ik", hn, -1), "f": ("ang", .1, .2)},
                 hands={"n": {"dir": (.4, -1), "curl": (.1, .1, .12, .15), "spread": .3, "thumb": .2}})["svg"])
    o.append(cat(lx + 20, top, .55, t, look=(-.7, -.3), paw=u, paw_dx=-120, tilt=-8 * u, smile=1.0))
    o.append(PR.sparkles(meet[0], meet[1], 1.4, smooth(hf, hf + .15, t) * (1 - smooth(hf + .5, hf + .9, t)), t, seed=8))
    dx, dy = shake(t, hf, 10)
    z = 1.35 + .1 * ease_io(ramp(t, a, 2.2)) + .06 * bump(t, hf)
    return view("".join(o), 560 + dx, 860 + dy, z, 0)


# ═════════════════════════ дни ═════════════════════════
def day_view(body, cx, cy, s, t, rot=0.0, bg="#e9dcc6"):
    return view(body, cx, cy, s, rot, bg=bg, over=cal_corner(t))


def desk_dima(t, x, y, sc, pocket=0.0, expr="focus"):
    """Дима сидит за столом с ноутбуком; pocket 0…1 — ближняя рука срывается к карману джинсов."""
    rest_n = (x + 330 * sc, y - 250 * sc)
    pk = (x + 150 * sc, y + 30 * sc)
    hn = (rest_n[0] + (pk[0] - rest_n[0]) * pocket, rest_n[1] + (pk[1] - rest_n[1]) * pocket)
    arms = {"f": ("ik", (x + 300 * sc, y - 240 * sc), -1), "n": ("ik", hn, -1)}
    hands = {"f": {"dir": (1, .1), "curl": (.3, .35, .4, .45), "thumb": .4}, "n": {"dir": (.6 - .9 * pocket, .4 + .5 * pocket), "curl": (.3, .35, .4, .45), "thumb": .4}}
    ex = dict(people.EXPR["dima"][expr])
    if pocket > .3:
        ex.update(look=(.1, .9))
    return fig(x, y, sc, ex, feet="sit", lean=.1, head_ang=.12 + .15 * pocket, arms=arms, hands=hands)


def frame_s10(t):
    a = T0("s10")
    o = [room(-900, 2200, wall="#e3dccb")]
    o.append(window(-120, 300, 200, 700, "#bfe6f7", t, sun=(80, 400)))
    x, y = 330.0, FL - 330
    o.append(shape(lib.rrect(x - 110, y, x + 110, y + 40, 10), "#8b5a33", "", w=4, seed=9800) + rect(x - 90, y + 40, x - 70, FL, "#6c4428")
             + rect(x + 70, y + 40, x + 90, FL, "#6c4428"))
    p = 0.0
    for wi in (44, 45):
        p = max(p, bump(t, W(wi) - .05, .1, .25))
    f_ = desk_dima(t, x, y, .62, pocket=min(1.0, p * 1.1))
    o.append(f_["svg"])
    o.append(PR.desk(780, FL - 420, 560, 1.0, leg_h=420))
    o.append(PR.laptop(800, FL - 430, .7, 1.0, screen="light", lines=.6, t=t))
    o.append(cat(1000, FL - 420, .45, t, look=(-.8, .2 + .6 * p)))
    dx, dy = shake(t, W(44), 10)
    dx2, dy2 = shake(t, W(45), 10)
    z = 1.3 + .08 * ramp(t, a, 1.8) + .05 * (bump(t, W(44)) + bump(t, W(45)))
    return day_view("".join(o), 560 + dx + dx2, 900 + dy + dy2, z, t)


def frame_s11(t):
    """Крупно: бедро в джинсах, рука трижды рывком к пустому карману (храповик), подкладка вывернута."""
    a = T0("s11")
    hits = [W(46), W(47), W(49)]
    o = [rect(-600, -600, 1700, 2600, "#e3dccb")]
    o.append(shape([(-300, 820), (1400, 700), (1400, 1500), (-300, 1640)], "#3d5a8a",
                   line([(-300, 1180), (1400, 1100)], 4, "#2b4268", seed=9810) + blob([(-300, 1400), (1400, 1300), (1400, 1500), (-300, 1640)], "#2f4a74", .7),
                   w=6, seed=9811))
    pk = [(380, 790), (720, 770), (700, 900), (560, 960), (420, 930)]
    o.append(line(pk[1:] + [pk[0]], 5, "#c9a24a", seed=9812))
    o.append(line([(380, 790), (720, 770)], 8, INK, seed=9813))
    lin = smooth(hits[2] + .15, hits[2] + .45, t)
    if lin > .01:
        o.append(shape([(470, 790), (630, 782), (640, 790 + 210 * lin), (550, 830 + 260 * lin), (460, 790 + 200 * lin)], "#f2efe6",
                       line([(510, 800), (560, 800 + 200 * lin)], 3, "#c9c3b4", seed=9815), w=4, seed=9814))
    u = 0.0
    for h in hits:
        d = t - (h - .1)
        if -.0 <= d < .45:
            u = max(u, math.sin(math.pi * min(1, d / .45)) ** .6)
    wr = (700 - 160 * u, 140 + 620 * u)
    o.append(line([(1250, -400), (1000, -60), wr], 120, "#d4a23e", taper=.02, wmin=.95, seed=9816))
    o.append(people.hand_svg("dima", wr, (-.45, .9), k=1.7, curl=(.35 + .3 * u,) * 4, thumb=.4, spread=.2))
    if t > hits[2] + .3:
        o.append(PR.sweat(760, 640, 2.0, 20))
    z = 1.0
    dx = dy = 0.0
    for h in hits:
        z += .08 * bump(t, h, .04, .2)
        ddx, ddy = shake(t, h, 12)
        dx += ddx
        dy += ddy
    return day_view("".join(o), 560 + dx, 840 + dy, z, t)


def fridge(x, yb, k, t, look=(0.0, 0.0), blink=0.0, talk=0.0):
    """Холодильник (центр низа) с двумя круглыми магнитами-глазами и магнитом-улыбкой."""
    w, h = 340 * k, 860 * k
    o = [blob(ellipse_pts(x + 10 * k, yb + 6, w * .6, 16 * k, 16), "#2a1e14", .2)]
    o.append(shape(lib.rrect(x - w / 2, yb - h, x + w / 2, yb, 26 * k), "#f2f4f6",
                   blob(lib.rect_pts(x + w / 2 - 40 * k, yb - h, x + w / 2, yb), "#d5dbe0", .9) + line([(x - w / 2, yb - h * .66), (x + w / 2, yb - h * .66)], 4 * k, seed=9900),
                   w=4.6 * k, seed=9901))
    for s_ in (-1, 1):
        o.append(line([(x - w / 2 + 34 * k, yb - h * (.72 if s_ < 0 else .58)), (x - w / 2 + 34 * k, yb - h * (.86 if s_ < 0 else .3))], 9 * k, "#9aa3ab", seed=9902 + s_))
    ey = yb - h * .82
    for i, ex_ in enumerate((-58, 58)):
        ecx = x + ex_ * k
        o.append(shape(ellipse_pts(ecx, ey, 44 * k, 44 * k * (1 - .9 * blink), 16), "#ffffff", "", w=4 * k, seed=9905 + i))
        if blink < .6:
            o.append(blob(ellipse_pts(ecx + look[0] * 18 * k, ey + look[1] * 14 * k, 17 * k, 17 * k * (1 - blink), 12), INK))
    my = yb - h * .74
    o.append(shape(lib.T([(-50, -6), (50, -6), (36, 16 + 22 * talk), (0, 26 + 30 * talk), (-36, 16 + 22 * talk)], x, my, k), "#e2574c", "", w=3.4 * k, seed=9908))
    o.append(shape(lib.T(lib.rrect(-40, -30, 40, 30, 8), x - 60, yb - h * .45, k, -8), "#ffd166", "", w=3 * k, seed=9909))
    o.append(shape(lib.T(ellipse_pts(0, 0, 30, 30, 12), x + 60, yb - h * .5, k), "#7bd389", "", w=3 * k, seed=9910))
    return "".join(o)


def kitchen_bg():
    o = [room(-900, 2200, wall="#d6e6e2", floor="#c9b79a")]
    for j in range(8):
        y = 600 + j * 70
        o.append(line([(-900, y), (2200, y)], 2, "#b7cfd4", seed=9920 + j, op=.8))
    o.append(shape(lib.rect_pts(-500, FL - 420, 230, FL), "#9fb7a8", line([(-500, FL - 380), (230, FL - 380)], 3, seed=9930), w=4, seed=9931))
    o.append(shape(lib.rect_pts(-520, FL - 450, 250, FL - 410), "#e8e2d4", "", w=4, seed=9932))
    return "".join(o)


def frame_s12(t):
    a = T0("s12")
    o = [kitchen_bg()]
    o.append(fridge(760, FL, 1.0, t, look=(-.6, .3), blink=1.0 if abs(t - (a + .9)) < .07 else 0.0))
    yawn = bump(t, W(53) - .05, .15, .5)
    x, y = 380.0, FL - 300
    o.append(shape(lib.rrect(x - 120, y + 10, x + 120, y + 50, 10), "#8b5a33", "", w=4, seed=9940) + rect(x - 90, y + 50, x - 70, FL, "#6c4428")
             + rect(x + 70, y + 50, x + 90, FL, "#6c4428"))
    ex = dict(people.EXPR["dima"]["slump"])
    if yawn > .2:
        ex.update(mouth="o", open=min(1.0, yawn * 1.4), lid=.05)
    arms = {"n": ("ik", (x + 250 * .62, y - 330 * .62 + 60 * yawn), -1), "f": ("ang", .15, .25)}
    f_ = fig(x, y, .62, ex, feet="sit", lean=.25 - .25 * yawn, head_ang=.35 - .5 * yawn, arms=arms,
             hands={"n": {"dir": (.2, -1), "curl": (.5, .5, .55, .6), "thumb": .5}})
    o.append(f_["svg"])
    o.append(cat(1010, FL + 10, .5, t, sleep=.6, look=(-.4, .3)))
    z = 1.3 + .06 * ramp(t, a, 1.6) + .05 * yawn
    return day_view("".join(o), 540, 880, z, t)


def frame_s13(t):
    a = T0("s13")
    o = [kitchen_bg()]
    tk = .5 + .5 * math.sin(t * 22)
    bl = 1.0 if abs(t - (W(55) + .1)) < .07 else 0.0
    side = math.sin((t - a) * 3.0)
    o.append(fridge(760, FL, 1.0, t, look=(-.8, .1 + .2 * side), blink=bl, talk=tk * smooth(W(56) - .1, W(56), t)))
    x, y = 340.0, 860.0
    sc = .62
    g = math.sin(t * 9)
    arms = {"n": ("ik", (x + 280 * sc + 40 * g, y - 300 * sc - 50 * abs(g)), -1), "f": ("ang", .5 + .3 * math.sin(t * 7), 1.0)}
    ex = dict(people.EXPR["dima"]["laugh"] if t > W(56) else people.EXPR["dima"]["friendly"], look=(.9, -.1))
    o.append(shadow(x, FL + 14, 150))
    o.append(fig(x, y, sc, ex, feet="stand", lean=.04, head_ang=-.05, arms=arms, hands={"n": {"dir": (.6, -.8), "curl": (.1, .1, .12, .15), "spread": .3, "thumb": .2}})["svg"])
    for i, tb in enumerate((W(54), W(56) - .2)):
        uu = back_out(clamp((t - tb) / .25))
        if t > tb:
            o.append(PR.speech_bubble(560 + 20 * i, 380 - 60 * i, 200, 130, uu * (1 - smooth(tb + .8, tb + 1.1, t)), seed=i, tail=(-70, 70)))
    o.append(cat(560, FL + 10, .5, t, look=(.8 if side > 0 else -.8, -.6), tilt=6 * side))
    z = 1.3 + .08 * ramp(t, a, 1.6)
    return day_view("".join(o), 560, 830, z, t)


def guitar(x, y, k, rot=0.0, dust=0.0):
    """Акустическая гитара (центр корпуса x, y), гриф вверх-вправо по rot."""
    body = [(0, -150), (70, -140), (96, -80), (78, -20), (120, 50), (118, 140), (60, 190), (0, 200), (-60, 190), (-118, 140), (-120, 50), (-78, -20),
            (-96, -80), (-70, -140)]
    inner = blob(ellipse_pts(0, 30, 36, 36, 14), "#3a2414") + blob([(-118, 120), (118, 120), (60, 190), (-60, 190)], "#a8642c", .6)
    if dust > .01:
        inner += blob(body, "#cfc9be", .55 * dust)
    o = shape(body, "#d98b45", inner, w=4.4, seed=9950)
    o += shape(lib.rect_pts(-16, -520, 16, -140), "#6b4024", "".join(line([(-12 + 8 * j, -520), (-12 + 8 * j, 100)], 1.4, "#f2efe6", seed=9951 + j) for j in range(4)), w=3.6,
               seed=9955)
    o += shape(lib.rrect(-26, -600, 26, -515, 10), "#5a3420", "", w=3.4, seed=9956)
    o += shape(lib.rect_pts(-40, 110, 40, 124), "#3a2414", "", w=2.4, seed=9957)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">{o}</g>'


def note(x, y, k, rot=0.0, op=1.0):
    d = (shape(ellipse_pts(0, 0, 16, 12, 12), INK, "", w=2, seed=9960) + line([(14, -2), (14, -60), (36, -48)], 5, INK, seed=9961))
    return f'<g opacity="{op:.3f}" transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">{d}</g>'


def frame_s14(t):
    a = T0("s14")
    o = [room(-900, 2200, wall="#ead9c0")]
    o.append(shape(lib.rect_pts(700, 300, 1060, FL), "#a5703f", line([(880, 300), (880, FL)], 4, seed=9970) + blob(lib.rect_pts(1010, 300, 1060, FL), "#8a5a38", .9),
                   w=5, seed=9971))
    x, y = 360.0, 860.0
    sc = .62
    take = ease_io(ramp(t, a, W(59) + .3 - a))              # «достал»: гитара с верха шкафа в руки
    strum = smooth(W(61) - .1, W(61) + .1, t)
    gp0 = np.array([860.0, 220.0])
    gp1 = np.array([x + 200 * sc, y - 120 * sc])
    gp = gp0 + (gp1 - gp0) * take
    grot = -10 + (-55 + 10) * take
    sw = math.sin(t * 26) * strum
    neck = gp + np.array([math.sin(math.radians(grot)) * 330, -math.cos(math.radians(grot)) * 330]) * .62
    arms = {"f": ("ik", tuple(neck if take > .6 else gp + np.array([40, -60])), -1),
            "n": ("ik", (gp[0] - 10 + 30 * sw, gp[1] + 20 + 20 * sw) if take > .6 else tuple(gp + np.array([-40, 60])), -1)}
    blow = bump(t, W(60) - .05, .1, .35)
    ex = dict(people.EXPR["dima"]["smile81"] if t > W(61) - .1 else people.EXPR["dima"]["surprise_day"], look=(.7, .3))
    if blow > .2:
        ex.update(mouth="o", open=.5)
    hands = {"f": {"dir": (.6, -.8), "curl": (.6, .6, .65, .7), "thumb": .5}, "n": {"dir": (.3, .9), "curl": (.4, .4, .45, .5), "thumb": .4}}
    base = fig(x, y, sc, ex, feet="stand", lean=.05, head_ang=.12, arms=arms, hands=hands, layers=("legs", "pelvis", "arm_f", "body"))
    near = fig(x, y, sc, ex, feet="stand", lean=.05, head_ang=.12, arms=arms, hands=hands, layers=("arm_n",))
    o.append(shadow(x, FL + 14, 150))
    o.append(base["svg"] + guitar(gp[0], gp[1], .62, grot, dust=1 - smooth(W(60), W(60) + .3, t)) + near["svg"])
    o.append(PR.dust_puff(gp[0] + 60, gp[1] - 80, 1.6, clamp((t - W(60)) / .6), seed=5))
    for i in range(5):
        tn = W(61) + i * .14
        if t > tn:
            v = (t - tn) / 1.0
            if v < 1:
                o.append(note(gp[0] + 80 + 160 * v + 30 * math.sin(v * 8 + i), gp[1] - 120 - 300 * v - i * 20, 1.2, 10 * math.sin(v * 6), 1 - v ** 2))
    o.append(cat(980, FL + 10, .5, t, look=(-.8, -.4), smile=smooth(W(61), W(61) + .2, t), tilt=8 * math.sin(t * 10) * strum))
    dx, dy = shake(t, W(61), 8)
    z = 1.25 + .1 * ease_io(ramp(t, a, 2.7)) + .05 * bump(t, W(61))
    return day_view("".join(o), 560 + dx, 820 + dy, z, t)


def frame_s15(t):
    a = T0("s15")
    pink = smooth(W(67) - .3, W(67) + .3, t)
    o = [room(-900, 2200, wall=lib.mix("#e3d7c8", "#f3d4d0", pink))]
    sky = lib.mix("#bcd6e6", "#f7a6b8", pink)
    o.append(window(420, 240, 1000, 900, sky, t))
    if pink > .01:
        g = lib.lin_grad([(0, "#ff8fa8", pink), (.6, "#ffc3a0", pink), (1, "#ffe3b0", pink)], 0, 240, 0, 900, units="userSpaceOnUse")
        c = lib.clip_rect(420, 240, 580, 660)
        o.append(f'<g clip-path="url(#{c})"><rect x="420" y="240" width="580" height="660" fill="url(#{g})"/>'
                 f'{PR.cloud(600, 520, 180, 70, seed=2, col="#ffd6dc")}{PR.cloud(860, 420, 140, 60, seed=3, col="#ffe6e0")}</g>')
        o.append(line([(710, 240), (710, 900)], 6, "#f6eee0", taper=0, wmin=1, seed=3401) + line([(420, 570), (1000, 570)], 6, "#f6eee0", taper=0, wmin=1, seed=3402))
    o.append(shape(lib.rect_pts(400, 900, 1020, 940), "#f6eee0", "", w=4, seed=9980))
    up = smooth(W(64) - .1, W(64) + .3, t)
    x, y = 300.0, 860.0
    ex = dict(people.EXPR["dima"]["wonder81"] if up > .5 else people.EXPR["dima"]["calm_smile"], look=(.8, -.6 * up))
    o.append(shadow(x, FL + 14, 150))
    o.append(fig(x, y, .62, ex, feet="stand", lean=-.04 * up, head_ang=-.25 * up, arms={"n": ("ang", .15, .3), "f": ("ang", .1, .2)})["svg"])
    o.append(cat(880, 916, .4, t, look=(-.4 + .9 * up, -.8 * up), tail=8 * math.sin(t * 3)))
    if pink > .05:
        o.append(PR.sparkles(700, 420, 1.6, pink, t, seed=11, col="#fff3c0"))
    z = 1.25 + .45 * ease_io(smooth(W(66), T1("s15"), t))
    cx = 560 + 120 * ease_io(smooth(W(66), T1("s15"), t))
    return day_view("".join(o), cx, 800 - 120 * ease_io(smooth(W(66), T1("s15"), t)), z, t)


# ═════════════════════════ s16–s17: Пенсильвания ═════════════════════════
PEOPLE = [("girl", 170.0, 0.0), ("dima", 500.0, .33), ("cap", 830.0, .66)]


def campus_bg(t, warm=0.0):
    o = [rect(-900, -900, 2200, 700, lib.mix("#cfe3ee", "#ffe6c2", warm))]
    for i, (bx, w, h) in enumerate(((-300, 520, 640), (260, 560, 760), (860, 520, 600))):
        col = ("#c8775a", "#b5654c", "#cc8467")[i]
        inner = "".join(rect(bx + 50 + c * 110, 700 - h + 80 + r * 140, bx + 110 + c * 110, 700 - h + 170 + r * 140, "#f3ead8") for c in range((w - 60) // 110)
                        for r in range((h - 140) // 140))
        o.append(shape(lib.rect_pts(bx, 700 - h, bx + w, 700), col, inner, w=4, seed=9990 + i))
        o.append(shape([(bx - 20, 700 - h), (bx + w / 2, 700 - h - 120), (bx + w + 20, 700 - h)], "#8a5a48", "", w=4, seed=9995 + i))
    for x in (-150, 470, 1100):
        o.append(PR.tree(x, 760, 1.4, 1.0, t, seed=int(x) % 7))
    o.append(rect(-900, 700, 2200, 2600, "#a8c473"))
    o.append(shape([(-900, 1080), (2200, 1020), (2200, 1500), (-900, 1560)], "#d9d4cb", "", w=4, seed=9998))
    return "".join(o)


def walker(who, x, y, sc, t, phase, phone_up_=1.0, turn=0.0, expr=None):
    kw = people.walk_kw(x, y, sc, phase, who)
    hip = kw["hip"]
    ph = (hip[0] + 300 * sc, hip[1] - 330 * sc + 90 * sc * (1 - phone_up_))
    arms = {"f": ("ik", (ph[0] - 70 * sc, ph[1] + 10 * sc), -1), "n": ("ik", (ph[0] + 10 * sc, ph[1] + 14 * sc), -1)}
    hands = {"f": {"dir": (.9, -.3), "curl": (.55, .55, .6, .62), "thumb": .5}, "n": {"dir": (-.6, -.7), "curl": (.6, .6, .65, .68), "thumb": .6}}
    ex = expr or {"brows": "calm", "mouth": "flat", "lid": .45, "look": (.4, .8)}
    ha = .35 * phone_up_ - .15 * turn
    base = people.figure(who, hip[0], hip[1], sc, expr=ex, lean=.08, head_ang=ha, arms=arms, hands=hands, feet=kw["feet"], layers=("legs", "pelvis", "arm_f", "body"))
    near = people.figure(who, hip[0], hip[1], sc, expr=ex, lean=.08, head_ang=ha, arms=arms, hands=hands, feet=kw["feet"], layers=("arm_n",))
    pp = ((base["wrist"]["f"][0] + base["wrist"]["n"][0]) / 2, (base["wrist"]["f"][1] + base["wrist"]["n"][1]) / 2 - 30 * sc)
    return base["svg"] + phone_up(pp[0], pp[1], sc * .75, -14, .7 * phone_up_, t * 1.5) + near["svg"], base["head"]


def half_clock(x, y, k, fill):
    """Часики «полчаса»: циферблат без цифр, сектор заполняется до половины (fill 0…1 → 0…180°)."""
    a = 180 * clamp(fill)
    o = shape(ellipse_pts(x, y, 46 * k, 46 * k, 18), "#fffaf0", "", w=4 * k, seed=9991)
    if a > 1:
        n = max(3, int(a / 6))
        pts = [(x, y)] + [(x + 40 * k * math.sin(math.radians(a * i / n)), y - 40 * k * math.cos(math.radians(a * i / n))) for i in range(n + 1)]
        o += blob(pts, "#f28a2e", .9)
    o += line([(x, y), (x + 34 * k * math.sin(math.radians(a)), y - 34 * k * math.cos(math.radians(a)))], 5 * k, INK, seed=9992)
    o += line([(x, y), (x, y - 36 * k)], 5 * k, INK, seed=9993)
    return o


def penn(t, show_clock, cloud_u, look_up):
    o = [campus_bg(t, warm=look_up)]
    for i, (who, x0, ph0) in enumerate(PEOPLE):
        x = x0 + 30 * (t - 28.0) * (1 - look_up)
        g, head = walker(who, x, 1080 - 300 * .5, .5, t, ph0 + (t - 28.0) * 1.6 * (1 - look_up), phone_up_=1 - look_up, turn=look_up,
                         expr={"brows": "calm", "mouth": "smile", "smile": .9, "lid": .7, "look": ((-1) ** i * .6, 0)} if look_up > .5 else None)
        o.append(shadow(x, 1130, 90))
        o.append(g)
        if show_clock > .01:
            o.append(f'<g opacity="{min(1, show_clock * 3):.3f}">{half_clock(head[0], head[1] - 250, 1.9, show_clock)}</g>')
        if cloud_u > .01:
            sk = clamp(cloud_u)
            o.append(PR.gloom(head[0] + 20, head[1] - 120, .8 * sk, t, sk, seed=i))
    return "".join(o)


def frame_s16(t):
    a = T0("s16")
    clk = smooth(W(71) - .05, W(71) + .35, t)
    z = 1.05 + .15 * ease_io(ramp(t, a, T1("s16") - a)) + .05 * bump(t, W(71))
    return view(penn(t, clk, 0.0, 0.0), 620, 760, z, 0)


def frame_s17(t):
    a = T0("s17")
    melt = smooth(W(79) - .1, W(79) + .5, t)
    cl = smooth(a - .1, a + .3, t) * (1 - melt)
    o = penn(t, 1.0 - smooth(a, a + .4, t), cl, smooth(W(79) + .1, W(80), t))
    for i, (who, x0, _) in enumerate(PEOPLE):
        if 0 < melt < 1:
            x = x0 + 60 * (t - 28.0) * 0
            pass
    z = 1.2 + .1 * ease_io(ramp(t, a, T1("s17") - a))
    return view(o, 640, 760, z, 0)


# ═════════════════════════ s18: финал — кот спит на телефоне на запертом шкафчике (ракурс s02) ═════════════════════════
def frame_s18(t):
    a = T0("s18")
    x, yb, k = LK
    o = [locker_room()]
    o.append(locker(x, yb, k, 0.0, lock=1.0))
    top = yb - 380 * k - 26 * k
    o.append(PR.phone_flat(x + 10, top - 10, .9, 0, 10, face_down=False, glow_=.25))
    o.append(CT.curl(x - 30, top - 4, .8, {"breath": 1.2, "flame_e": .6}, t))
    o.append(PR.zzz(x + 90, top - 220, 1.2, t, smooth(W(84) - .2, W(84) + .2, t)))
    z = 1.3 + .12 * ease_io(ramp(t, a, T1("s18") - a))
    return view("".join(o), 560, 920 - 80 * ease_io(ramp(t, a, 2.0)), z, -1.0 + 1.0 * ramp(t, a, 2.0), bg="#e9d6b4")


FRAMES = {k[6:]: v for k, v in dict(globals()).items() if k.startswith("frame_s")}


def frame(sid, t):
    if sid != "s08":
        lib.DEFS.clear()
    return FRAMES[sid](t)
