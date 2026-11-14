"""Рилс 61 «стол», группа B — люди крупно: s03 (мама в дверном проёме: обводит рукой бардак, качает головой, скрещивает руки),
s10 (участница и бородач в профиль друг к другу, облачка мыслей, облако бородача раздувается), s13 (поднос: рука участницы берёт
яблоко, укус, из двух чашек выбирает простую, зелёная галочка). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Люди — только ../common/people.py, предметы — ../common/props.py. Печатных букв и цифр нет."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
from ink import band  # noqa: E402
from lib import (INK, back_out, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix, rect_pts, rrect, shape,  # noqa: E402,F401
                 smooth, spring)

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def decay(t, t0, k=9.0, fr=22.0):
    if t < t0:
        return 0.0
    u = t - t0
    return math.exp(-k * u) * math.sin(2 * math.pi * fr * u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_of(t, times, dur=.14):
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            return math.sin(math.pi * u)
    return 0.0


def talk_open(t, idx):
    """Раскрытие рта по словам голоса: внутри слова — слоги (≈ 7 Гц), между словами — почти закрыт."""
    for i in idx:
        a, b = WORDS[i]["start"], WORDS[i]["end"]
        if a - .03 <= t <= b + .03:
            u = (t - a) / max(.08, b - a)
            return .18 + .55 * abs(math.sin(math.pi * u * max(1, round((b - a) * 7))))
    return .08


def open_hand(c=.2, d=(1, 0), spread=.2, thumb=.2, flip=1, k=1.0):
    return dict(kind="open", flip=flip, dir=d, curl=(c, c, c, c * .9), spread=spread, thumb=thumb, bend=.1, k=k)


def person(who, hip, s, expr, arms, hands, lean=0.0, head_ang=0.0, head_off=(0, 0), feet=None, torso_k=1.0):
    p = dict(hip=tuple(hip), scale=s * people.HEIGHT.get(who, 1.0), lean=lean, torso_k=torso_k, feet=feet, arms=arms, hands=hands, expr=expr,
             head_ang=head_ang, head_off=head_off, hood=0.0, strings=(0, 0))
    return people.draw(p, who)


def lin(stops, x1=0, y1=0, x2=0, y2=1):
    return lib.lin_grad(stops, x1, y1, x2, y2)


def rect_d(x0, y0, x1, y1):
    return f"M{f(x0)} {f(y0)}H{f(x1)}V{f(y1)}H{f(x0)}Z"


# ═════════════════════════════ s03: мама в дверном проёме ═════════════════════════════
T_CHTO, T_BARD, T_NICH, T_HOR, T_PRID = wt(10), wt(13), wt(14), wt(15), wt(17)      # 4.48, 5.16, 5.76, 6.31, 6.93
DOOR = (250, 70, 840, 1700)
WALL3 = "#d8c9a8"
WALL3_SH = "#c4b38f"


def room_wall03(t):
    x0, y0, x1, y1 = DOOR
    o = []
    g = lin([(0, "#e2d4b4", 1), (1, "#cdbd99", 1)])
    o.append(f'<rect x="-600" y="-700" width="2400" height="3400" fill="url(#{g})"/>')
    # обои: тонкие вертикальные полосы с ромбиками (тихий фон, ничего не читается)
    for i in range(-6, 22):
        x = -560 + i * 110
        if x0 - 60 < x < x1 + 60:
            continue
        o.append(line([(x, -700), (x + 2, 2600)], 3, WALL3_SH, taper=0, wmin=1, seed=300 + i, op=.55))
        for j in range(16):
            y = -640 + j * 170 + (85 if i % 2 else 0)
            o.append(blob([(x + 55, y - 10), (x + 61, y), (x + 55, y + 10), (x + 49, y)], "#bfae88", .7))
    # набросок на стене справа от двери (Димин бардак расползся и на стену)
    o.append(PR.wall_sketch(1010, 420, 1.15, 6, seed=3, kind="spiral"))
    o.append(PR.sticky(-80, 700, 1.3, -8, col="yellow", seed=4, mark="star"))
    o.append(PR.sticky(960, 760, 1.2, 10, col="blue", seed=5, mark="arrow"))
    # коридор за проёмом: тёплый свет, пол, дальняя дверь
    cg = lin([(0, "#ffe7b4", 1), (1, "#f2c27a", 1)])
    hall = (shape(rrect(x0 + 330, y0 + 260, x0 + 520, y0 + 900, 6), "#e8c58c", blob(rect_pts(x0 + 470, y0 + 260, x0 + 520, y0 + 900), "#d9ae6e"), w=3.4, seed=310)
            + f'<circle cx="{f(x0 + 350)}" cy="{f(y0 + 600)}" r="9" fill="#b8843e"/>'
            + blob(rect_pts(x0, y1 - 300, x1, y1), "#d9a75c", .95)
            + line([(x0, y1 - 300), (x1, y1 - 306)], 3, "#b8843e", taper=0, wmin=1, seed=311)
            + PR.glow(x0 + 120, y0 + 160, 260, .55))
    o.append(shape(rect_pts(x0, y0, x1, y1), f"url(#{cg})", hall, w=4, seed=312))
    # наличник
    for (xa, xb) in ((x0 - 34, x0), (x1, x1 + 34)):
        o.append(shape(rect_pts(xa, y0 - 34, xb, y1), "#f1e9d8", line([(xa + 10, y0), (xa + 10, y1)], 2, "#d5cab3", taper=0, wmin=1, seed=313), w=3.8,
                       seed=314 + int(xa) % 7))
    o.append(shape(rect_pts(x0 - 34, y0 - 34, x1 + 34, y0), "#f1e9d8", "", w=3.8, seed=318))
    return "".join(o)


def foreground_desk03(t, sh):
    """Край стола-бардака на переднем плане (низ кадра): гора бумажек, кружки, провод — едет чуть быстрее фона (параллакс)."""
    dx = sh * 1.6
    o = [PR.desk(640 + dx, 1640, 1700, 1.0, 380, legs=True, leg_h=500, col="wood", seed=3)]
    o.append(PR.paper_pile(520 + dx, 1500, 1.6, seed=7, n=12))
    o.append(PR.coffee_ring(900 + dx, 1560, 1.2, 0, seed=2))
    o.append(PR.mug(1010 + dx, 1580, 1.6, -4, col="blue", coffee=True, steam=.6, t=t, handle=1, seed=4))
    o.append(PR.mug(170 + dx, 1600, 1.45, 6, col="red", coffee=False, handle=-1, seed=5))
    o.append(PR.cable_tangle(820 + dx, 1490, 1.35, seed=2, t=t))
    return "".join(o)


def frame03(t):
    a = 4.0
    push = ease_io(clamp((t - a) / 3.2))
    x0, y0, x1, y1 = DOOR
    # мама входит в проём: с кадра 0 наклон «заглядывает» → выпрямляется
    enter = ease_out(clamp((t - a) / .45))
    s = 1.12
    sc = s * people.HEIGHT["mama"]
    hip = (520 - 60 * (1 - enter), 1300 + 10 * (1 - enter))
    lean = .16 * (1 - enter)
    # 1) «бардаке» — обводит рукой комнату (ближняя рука вперёд и дугой вправо-вниз)
    sw_in = ease_out(clamp((t - (T_BARD - .14)) / .22))
    sw_out = ease_io(clamp((t - (T_NICH + .05)) / .35))
    sw = sw_in * (1 - sw_out)
    arc = math.sin(clamp((t - T_BARD) / .6) * math.pi * 1.0)
    th_n = .1 + (1.25 + .35 * arc) * sw
    bend_n = .25 - .1 * sw
    # 2) «придумаешь» — скрестила руки
    cr = ease_io(clamp((t - (T_PRID - .2)) / .32))
    rest = people.pose_kw("rest", hip[0], hip[1], s, "mama")
    cross = people.pose_kw("cross", hip[0], hip[1], s, "mama")
    arms = {"f": ("ang", .18, .2), "n": ("ang", th_n, bend_n)}
    hands = {"f": open_hand(.35, (-.1, 1), flip=1, k=sc), "n": open_hand(.08 if sw > .3 else .3, (math.sin(th_n - .3), math.cos(th_n - .3)), spread=.3 * sw + .1,
                                                                      thumb=.1, flip=1, k=sc)}
    if cr > 0:
        # от опущенных рук к скрещенным — по целям ik (запястье опущенной руки в мире → цель скрещивания)
        def wrist_rest(th, bend):
            sp = np.array(hip) + np.array([6.0, -400.0]) * sc
            d1 = np.array([math.sin(th), math.cos(th)])
            e = sp + d1 * people.UPPER * sc
            c_, s_ = math.cos(-bend), math.sin(-bend)
            d2 = np.array([d1[0] * c_ - d1[1] * s_, d1[0] * s_ + d1[1] * c_])
            return e + d2 * people.FORE * sc
        wf0, wn0 = wrist_rest(.18, .2), wrist_rest(th_n, bend_n)
        tf, tn = np.array(cross["arms"]["f"][1]), np.array(cross["arms"]["n"][1])
        e = cr
        arms = {"f": ("ik", tuple(wf0 + (tf - wf0) * e), -1), "n": ("ik", tuple(wn0 + (tn - wn0) * e), 1)}
        hands = {"f": {"kind": "none"}, "n": {"kind": "none"}} if cr > .55 else hands
    # голова: «ничего» — качает головой; вздох после «придумаешь»
    shake_h = .12 * math.sin(2 * math.pi * 2.6 * (t - T_NICH)) * math.exp(-1.4 * (t - T_NICH)) if t > T_NICH else 0.0
    sigh = bump(t, T_PRID + .25, .9)
    ha = shake_h - .04 * sigh + .015 * math.sin(t * 3.1)
    talk = (T_CHTO - .04) < t < WORDS[17]["end"] + .05
    if t < T_HOR - .1:
        brows = "skeptic"
    elif t < T_PRID + .2:
        brows = "frown"
    else:
        brows = "sad"
    expr = dict(lid=.82 - .25 * sigh, brows=brows, mouth="talk" if talk else "pursed", open=talk_open(t, range(10, 18)), smile=0,
                look=(.35 - .5 * sw * (arc * .5 + .5), .15), closed=max(blink_of(t, (4.33, 6.1)), .65 * sigh), hair=3 * decay(t, T_NICH, 4, 2.6))
    m = person("mama", hip, s, expr, arms, hands, lean=lean, head_ang=ha, torso_k=1 + .025 * sigh)
    o = [room_wall03(t)]
    # тень мамы на косяке и полу коридора
    o.append(blob(ellipse_pts(hip[0] + 30, y1 - 120, 230, 30, 14), "#7a5530", .3))
    o.append(m.get("pelvis", "") + m["arm_f"] + m["body"] + m["arm_n"])
    hx, hy = m["head"]
    # тряска на «бардаке», дрейф и наезд на лицо
    sx_, sy_ = PR.shake(t, T_BARD, 14, .4, seed=3)
    z = 1.06 + .42 * push
    set_ink(z)
    cx = 560 + (hx + 40 - 560) * push + sx_
    cy = 960 + (hy + 140 - 960) * push + sy_
    o.append(foreground_desk03(t, (cx - 560) * .5))
    cam = lib.cam(cx, cy, z, -1.0 + 1.6 * push + .6 * decay(t, T_BARD, 6, 9))
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ═════════════════════════════ s10: два лица в профиль, облачка мыслей ═════════════════════════════
T_IDEI, T_BESP = wt(42), wt(44)       # 23.36, 24.62
MID = 540


def neat_bg():
    """Слева: белый аккуратный фон — пустая стена, ровная полка, три одинаковые коробки, линейка-плинтус."""
    o = [f'<rect x="-600" y="-700" width="{MID + 600}" height="3400" fill="#f7f6f2"/>']
    o.append(shape(rect_pts(-300, 1180, MID, 1206), "#e4e1d8", "", w=3.2, seed=330))
    for i in range(3):
        bx = -120 + i * 150
        o.append(shape(rrect(bx, 1080, bx + 120, 1180, 4), "#dde3ea", line([(bx + 30, 1120), (bx + 90, 1120)], 3, "#b9c3cf", taper=0, wmin=1, seed=331 + i),
                       w=3.2, seed=334 + i))
    o.append(shape(rect_pts(-300, 1700, MID, 1730), "#e4e1d8", "", w=3.0, seed=338))
    return "".join(o)


def busy_bg(t):
    """Справа: пёстрый захламлённый фон — цветные обои-пятна, стикеры, наброски вкривь, гирлянда, стопки."""
    o = [f'<rect x="{MID}" y="-700" width="1400" height="3400" fill="#f3d9a8"/>']
    rs = np.random.RandomState(61)
    cols = ["#e8735a", "#5aa7c8", "#8cc06a", "#f2b632", "#b77ac8", "#ef9ab0"]
    for k in range(70):
        x, y = rs.uniform(MID, 1700), rs.uniform(-600, 2300)
        r = rs.uniform(10, 26)
        o.append(blob(ellipse_pts(x, y, r, r * rs.uniform(.6, 1), 10, rot=rs.uniform(0, 180)), cols[k % 6], .55))
    for k in range(8):
        x, y = rs.uniform(MID + 90, 1500), rs.uniform(-250, 1500)
        o.append(PR.sticky(x, y, 1.25, rs.uniform(-25, 25), col=["yellow", "pink", "blue", "green"][k % 4], seed=40 + k,
                           mark=["star", "circle", "arrow", "lines"][k % 4]))
    for k, kind in enumerate(("rocket", "wave", "house", "graph")):
        o.append(PR.wall_sketch(MID + 160 + 260 * (k % 2) + 90 * (k // 2), 260 + 520 * (k // 2) + 140 * (k % 2), 1.05, rs.uniform(-18, 18), seed=50 + k,
                                kind=kind))
    # гирлянда-флажки без букв
    pts = [(MID, 120 + 20 * math.sin(t * 2)), (MID + 260, 210), (MID + 520, 150 + 10 * math.sin(t * 2 + 1)), (1300, 230)]
    o.append(line(pts, 3, INK, taper=0, wmin=1, seed=360))
    for k in range(9):
        u = (k + .5) / 9
        x = MID + 760 * u
        y = 120 + 110 * math.sin(math.pi * u * 1.4) + 6 * math.sin(t * 2 + k)
        o.append(shape([(x - 18, y), (x + 18, y), (x, y + 38)], cols[k % 6], "", w=2.6, seed=361 + k))
    return "".join(o)


def frame10(t):
    a = 23.0
    drift = ease_io(clamp((t - a) / 3.1))
    move = ease_io(clamp((t - (T_BESP - .1)) / .7))
    o = [neat_bg(), busy_bg(t)]
    # разделитель
    o.append(line([(MID, -700), (MID + 4, 2600)], 12, INK, taper=0, wmin=1, seed=370))
    s = 1.6
    # участница слева, смотрит вправо
    bl = blink_of(t, (23.9, 25.5))
    ex_b = dict(people.EXPR["bob"]["think"], look=(.55, -.55 - .1 * math.sin(t * 2)), closed=bl)
    if t > T_BESP + .3:
        ex_b = dict(ex_b, brows="calm", mouth="flat", look=(.7, -.2))
    hipL = (190, 1660 + 6 * math.sin(t * 2.4))
    pL = person("bob", hipL, s, ex_b, {"f": ("ang", .15, .2), "n": ("ang", -.05, .2)}, {}, lean=.05, head_ang=-.06 + .03 * math.sin(t * 1.7))
    # бородач справа, смотрит влево (отражение)
    up_b = ease_out(clamp((t - T_BESP) / .3))
    ex_r = dict(people.EXPR["beard"]["think"], look=(.5, -.6 + .1 * math.sin(t * 2.3)), closed=blink_of(t, (23.6, 24.4)))
    if t > T_BESP:
        ex_r = dict(people.EXPR["beard"]["idea"], look=(.45, -.7), open=.5 + .3 * up_b, hair=0)
    hipR = 950
    pR = person("beard", (hipR, 1640 + 6 * math.sin(t * 2.1 + 1)), s, ex_r, {"f": ("ang", .15, .2), "n": ("ang", -.05, .2)}, {}, lean=.04 - .05 * up_b,
                head_ang=-.05 - .08 * up_b + .03 * math.sin(t * 1.5))
    cL = lib.clip_of(rect_pts(-700, -700, MID - 6, 2600))
    cR = lib.clip_of(rect_pts(MID + 6, -700, 1800, 2600))
    o.append(f'<g clip-path="url(#{cL})">{pL["arm_f"]}{pL["body"]}{pL["arm_n"]}</g>')
    o.append(f'<g clip-path="url(#{cR})"><g transform="translate({2 * hipR} 0) scale(-1 1)">{pR["arm_f"]}{pR["body"]}{pR["arm_n"]}</g></g>')
    hLx, hLy = pL["head"]
    hRx, hRy = 2 * hipR - pR["head"][0], pR["head"][1]
    # облачка: «идеи» — выскакивают пустые над обоими
    uc = back_out(clamp((t - (T_IDEI - .05)) / .32), 2.2)
    uc2 = back_out(clamp((t - (T_IDEI + .07)) / .32), 2.2)
    grow = spring(t - T_BESP, 2.2, 4.0) if t > T_BESP else 0.0
    if uc > 0:
        o.append(PR.thought_cloud(hLx + 90, hLy - 470 + 6 * math.sin(t * 2.2), 1.15, 300, 190, uc, seed=1, dots=1))
    if uc2 > 0:
        kR = 1.15 + .6 * grow
        cxR, cyR = hRx - 60 - 40 * grow, hRy - 440 - 60 * grow + 6 * math.sin(t * 2.5)
        if grow > .02:
            o.append(PR.glow(cxR, cyR - 20, 210 * kR, .8 * min(1.0, grow) * (1 + .08 * math.sin(t * 9)), ry=150 * kR))
        o.append(PR.thought_cloud(cxR, cyR, kR, 300, 190, uc2, seed=2, dots=-1, col=lib.mix("#FFFFFF", "#FFF2B8", min(1.0, grow))))
        if grow > .05:      # искры-штрихи вокруг раздувшегося облака
            for k in range(7):
                ang = -math.pi / 2 + (k - 3) * .42 + .05 * math.sin(t * 6 + k)
                r0 = 200 * kR + 20 * math.sin(t * 8 + k)
                L = 46 * min(1.0, grow)
                p0 = (cxR + r0 * math.cos(ang), cyR + r0 * .7 * math.sin(ang))
                p1 = (cxR + (r0 + L) * math.cos(ang), cyR + (r0 + L) * .7 * math.sin(ang))
                o.append(line([p0, p1], 8, "#f2b632", taper=.4, wmin=.4, seed=380 + k))
    z = 1.04 + .06 * drift + .05 * move
    set_ink(z)
    sx_, sy_ = PR.shake(t, T_BESP, 8, .3, seed=5)
    cam = lib.cam(540 + 120 * move + 20 * drift + sx_, 880 - 30 * drift + sy_, z, .5 - .8 * drift)
    return f'<g transform="{cam}">{"".join(o)}</g>'


# ═════════════════════════════ s13: поднос, яблоко, укус, простая чашка ═════════════════════════════
T_EDU, T_PRIV = wt(55), wt(57)        # 30.48, 31.27
TABLE_Y = 1240


def sleeve_arm(wrist, elbow, k, seed=0):
    """Предплечье в вишнёвом свитере участницы (рукав не толще предплечья), манжета-резинка у запястья."""
    C = people.PAL["bob"]
    W_, E_ = np.array(wrist, float), np.array(elbow, float)
    d = (W_ - E_) / (np.linalg.norm(W_ - E_) + 1e-9)
    n = np.array([-d[1], d[0]])
    c0 = W_ - d * 26 * k
    body = band([tuple(E_), tuple((E_ + c0) / 2), tuple(c0)], 92 * k, 80 * k, step=6, cap=False)
    inner = blob([tuple(E_ - n * 46 * k), tuple(c0 - n * 40 * k), tuple(c0 - n * 12 * k), tuple(E_ - n * 14 * k)], C["TOP_SH"], .85)
    for i, u in enumerate((.3, .55)):
        p = E_ + (c0 - E_) * u
        inner += line([tuple(p + n * 30 * k), tuple(p + d * 8 * k), tuple(p - n * 24 * k)], 2.4, C["FOLD"], seed=seed + i, op=.8)
    o = shape(body, C["TOP"], inner, w=4.4, seed=seed + 5)
    cf = band([tuple(c0), tuple(W_ + d * 4 * k)], 84 * k, 80 * k, step=3, cap=False)
    rib = "".join(line([tuple(c0 + d * j * 6 * k + n * 42 * k), tuple(c0 + d * j * 6 * k - n * 42 * k)], 1.6, C["TOP_SH2"], seed=seed + 10 + j, op=.8)
                  for j in range(1, 5))
    o += shape(cf, C["TOP_SH"], rib, w=3.6, seed=seed + 9)
    return o


def frame13(t):
    a = 29.8
    drift = ease_io(clamp((t - a) / 3.2))
    o = []
    # стол аккуратной комнаты (белый), стена
    o.append('<rect x="-600" y="-700" width="2400" height="3400" fill="#eef0f2"/>')
    o.append(shape(rect_pts(-600, TABLE_Y - 520, 1800, 2700), "#f6f3ec", blob(rect_pts(-600, TABLE_Y - 520, 1800, TABLE_Y - 470), "#e6e1d6"), w=4, seed=400))
    for k in range(5):
        o.append(line([(-600, TABLE_Y - 380 + k * 170), (1800, TABLE_Y - 376 + k * 170)], 2, "#e0dbcf", taper=0, wmin=1, seed=401 + k, op=.8))
    K = 2.3
    tx, ty = 540, TABLE_Y
    o.append(blob(ellipse_pts(tx, ty + 6, 420, 26, 16), "#c9c2b2", .6))
    o.append(PR.tray(tx, ty, K, 360, col="#5C9A78"))
    # шоколадка остаётся
    o.append(PR.chocolate(tx - 260, ty - 34 * K - 60, K * .95, -8))
    # яблоко: рука приходит справа с кадра 0, берёт (30.15), поднимает к «рту» вверх, укус на «еду», кладёт назад к 31.0
    AP0 = np.array([tx + 150.0, ty - 34 * K])        # дно яблока на подносе
    reach = ease_out(clamp((t - a) / .35))
    lift = ease_io(clamp((t - 30.18) / .28))
    down = ease_io(clamp((t - 30.86) / .3))
    up_y = -430
    ap = AP0 + np.array([-60.0, up_y]) * lift + np.array([560.0, 120.0]) * down
    bite = smooth(T_EDU - .02, T_EDU + .05, t)
    sx_, sy_ = PR.shake(t, T_EDU, 12, .3, seed=7)
    ak = K * 1.05
    rot_a = -10 * lift * (1 - down)
    # чашки «привычное»: выезжают слева по подносу перед словом
    cups = ease_out(clamp((t - (T_PRIV - .4)) / .35))
    cpx = tx - 70 + (-700) * (1 - cups)
    cpy = ty - 34 * K
    csx = tx + 140 + 700 * (1 - cups) if cups < 1 else tx + 140
    # рука: до 31.0 — с яблоком; 31.0–31.35 уходит; 31.35–31.75 зависает над колючей, переходит к простой и берёт (31.8), чуть поднимает
    R = 33 * ak
    gk = .95 * ak / 2.3 * 2.3 * .55
    o_back, o_front, o_arm = "", "", ""
    hand_k = 1.25
    if t < 31.16:
        C_ = ap + np.array([0.0, -32 * ak])        # центр яблока
        if t < 30.15:      # подлетает раскрытой ладонью
            W_ = np.array([1300.0, 900.0]) + (C_ + np.array([R + 70, 20]) - np.array([1300.0, 900.0])) * reach
            E_ = W_ + np.array([300.0, 260.0])
            o_arm = sleeve_arm(W_, E_, hand_k, seed=420)
            o_front = people.hand_svg("bob", tuple(W_), (-1, -.25), k=hand_k, curl=(.25, .3, .35, .4), spread=.25, thumb=.25, flip=-1, seed=440)
        else:
            gb, gf = people.grip_svg("bob", tuple(C_), R, +1, k=hand_k, h=78, seed=460)
            W_ = C_ + np.array([R + 70 * hand_k, 6])
            E_ = W_ + np.array([320.0, 230.0 + 60 * lift * (1 - down)])
            o_arm = sleeve_arm(W_ + np.array([-18, 0]), E_, hand_k, seed=420)
            o_back, o_front = gb, gf
        if t > 31.0:      # отпускает
            pass
    else:
        e_away = ease_io(clamp((t - 31.05) / .3))
        hover = ease_io(clamp((t - 31.35) / .25))
        to_plain = ease_io(clamp((t - 31.62) / .2))
        spk = np.array([csx, cpy - 140.0])
        pln = np.array([cpx + 40, cpy - 120.0])
        # сначала тянется к колючей (зависает), потом к простой
        tgt = spk + (pln - spk) * to_plain
        lift2 = ease_out(clamp((t - 31.9) / .3))
        C_cup = np.array([cpx, cpy - 36 * ak * .9]) + np.array([0, -60]) * lift2
        if t < 31.85:
            W_ = np.array([900.0, 760.0]) + (tgt + np.array([90, -40]) - np.array([900.0, 760.0])) * (e_away * (1 - hover) * .3 + hover)
            E_ = W_ + np.array([320.0, 250.0])
            o_arm = sleeve_arm(W_, E_, hand_k, seed=420)
            hesit = .15 * math.sin((t - 31.35) * 18) * (1 - to_plain) * hover
            o_front = people.hand_svg("bob", tuple(W_), (-1, .35 + hesit), k=hand_k, curl=(.35, .4, .45, .5), spread=.15, thumb=.2, flip=-1, seed=440)
        else:
            gb, gf = people.grip_svg("bob", tuple(C_cup + np.array([0, -10])), 38 * ak * .9, +1, k=hand_k, h=70, seed=470)
            W_ = C_cup + np.array([38 * ak * .9 + 70 * hand_k, -4])
            E_ = W_ + np.array([320.0, 230.0])
            o_arm = sleeve_arm(W_ + np.array([-18, 0]), E_, hand_k, seed=420)
            o_back, o_front = gb, gf
    # слои: предметы, рука за предметом, предмет, пальцы
    # отражено: надкус слева, его не закрывают пальцы (рука держит справа)
    apple_svg = f'<g transform="translate({f(2 * ap[0])} 0) scale(-1 1)">{PR.apple(float(ap[0]), float(ap[1]), ak, -rot_a, bite=bite, seed=1)}</g>'
    if t >= 31.16:
        if cups > 0:
            o.append(PR.cup_spiky(csx, cpy, ak * .9, 0, t))
        o.append(o_back)
        if cups > 0:
            lift2 = ease_out(clamp((t - 31.9) / .3)) if t > 31.85 else 0.0
            o.append(PR.cup_plain(cpx, cpy - 60 * lift2, ak * .9))
        o.append(o_arm + o_front)
    else:
        o.append(o_back + apple_svg + o_arm + o_front)
    # хруст: крошки и штрихи «хрум» на укусе
    if t > T_EDU:
        u = clamp((t - T_EDU) / .5)
        ac = ap + np.array([-30.0 * ak, -34 * ak])
        o.append(PR.clink(float(ac[0]) - 40, float(ac[1]) - 30, 1.6, 1 - u, seed=3))
        rs = np.random.RandomState(5)
        for k in range(6):
            ang = math.pi - rs.uniform(-1.2, .9)
            sp = rs.uniform(260, 420)
            px = ac[0] + math.cos(ang) * sp * u
            py = ac[1] + math.sin(ang) * sp * u + 600 * u * u
            if u < 1:
                o.append(shape(ellipse_pts(px, py, 9, 7, 8, rot=rs.uniform(0, 90)), "#FFF4D6", "", w=2.4, seed=480 + k))
    # зелёная галочка у простой чашки
    if t > 32.0:
        uc = clamp((t - 32.0) / .35)
        o.append(PR.check_mark(cpx - 30, cpy - 380, 1.8, ease_out(uc), w=12, seed=4))
    z = 1.5 + .12 * drift
    set_ink(z)
    cam = lib.cam(540 - 30 * drift + sx_ + 14 * math.sin(t * .9), TABLE_Y - 200 - 40 * drift + sy_, z, -.6 + 1.0 * drift)
    return f'<g transform="{cam}">{"".join(o)}</g>'


def frame(sid, t):
    lib.dyn_begin()
    fn = {"s03": frame03, "s10": frame10, "s13": frame13}[sid]
    return lib.svg(fn(t))
