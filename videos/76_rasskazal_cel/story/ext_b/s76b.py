"""Рилс 76 «Рассказал о цели», группа B: люди, кухня, «тсс». Время — только из shots.json и voice/words.json (слово по индексу wN).
s02: общий план комнаты хука сбоку, затылки толпы хлопают, Дима на матрасе: «сделал» (w6) хруст, «ничего» (w8) разводит руками, конфетти
     замирает; надпись хука «Кубок за что?» на том же месте экрана, гаснет после «ничего».
s07: Дима сел на матрасе, вот-вот похвастается; кот вскакивает, «пока» (w31) лапа поднята, «сделал» (w33) лапа у губ — «тсс».
s08: вид чуть сверху: «напишешь» (w35) дудка, «будешь» (w38) разворачивается, «обещать» (w40) — снова и снова, ноутбук в пыли.
s10: (хлёст) вечер, кухня: «Дима» (w48) слушатели оборачиваются, «рассказал» (w50) руками прямоугольник, «станет» (w52) палец вверх.
s11: кухня: «программистом» (w53) овация, «ему» (w55) мама протягивает кубок, «хлопали» (w56) кубок над головой, конфетти.
s17: (хлёст) вечер, стол у окна: кубок-стакан, «Дима» (w88) взгляд, «молча» (w90) палец у губ, ноутбук открывается к Диме.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
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
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, shape, svg  # noqa: E402,F401

INK = lib.INK
W = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = {s["id"]: s for s in json.load(open(os.path.join(STORY, "shots.json")))["shots"]}


def ws(i):
    return W[i]["start"]


def we(i):
    return W[i]["end"]


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(a, b, u):
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))


def bump(t, t0, dur=.3):
    u = (t - t0) / dur
    return math.sin(math.pi * u) if 0 < u < 1 else 0.0


def talking(t, i0, i1, rate=6.0):
    """Раскрытие рта 0…1 по словам i0…i1 (рот открыт только внутри слов, слоги — синусом)."""
    for i in range(i0, i1 + 1):
        a, b = ws(i), we(i)
        if a - .03 <= t <= b + .03:
            return .25 + .75 * abs(math.sin(math.pi * rate * (t - a)))
    return 0.0


def frame_svg(body, cx, cy, s, rot, bg="#f4efe4", over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def whip_wrap(g, t, t0, dx=-620.0, dur=.22):
    """Хлёст на входе плана: кадр въезжает сбоку с горизонтальным размытием (только пока летит)."""
    u = clamp((t - (t0 - .08)) / dur)
    if u >= 1:
        return g
    e = ease_out(u, 3)
    off = dx * (1 - e)
    bl = 60 * (1 - e)
    fid = lib.uid("wh")
    lib.DEFS.append(f'<filter id="{fid}" x="-30%" y="-5%" width="160%" height="110%"><feGaussianBlur stdDeviation="{bl:.1f} 0"/></filter>')
    return f'<g transform="translate({off:.1f} 0)" filter="url(#{fid})">{g}</g>'


def arms_mix(A, B, u):
    """Плавный переход между двумя наборами ik-рук (цели линейно, сторона локтя — от B)."""
    u = clamp(u)
    out = {}
    for k in ("f", "n"):
        a, b = A[k], B[k]
        if a[0] == b[0] == "ik":
            out[k] = ("ik", lerp2(a[1], b[1], u), b[2] if len(b) > 2 else -1)
        else:
            out[k] = b if u > .5 else a
    return out


def pose_arms(name, x, y, s, who="dima"):
    return people.pose_kw(name, x, y, s, who)["arms"]


def pose_hands(name, x, y, s, who="dima"):
    return people.pose_kw(name, x, y, s, who)["hands"]


# ═══════════════════════════════ кухня вечером (s10–s11) ═══════════════════════════════
LAMP = (540.0, 330.0)        # абажур над столом


def kitchen_eve(t, swing=0.0):
    """Кухня 74 (kitchen_scene) вечером: за окном закат, стены в тёплом свете лампы-абажура над столом, свет пятном по форме абажура.
    dict(bg, chair_back, chair_seat, table, glow)."""
    k = R.kitchen_scene(t)
    o = [k["bg"]]
    # закат в окне (стекло 88…452 × 218…700), рама поверх
    gid = lib.lin_grad([(0, "#3b3f78", 1), (.55, "#c8607a", 1), (1, "#f2a65a", 1)], 0, 218, 0, 700, units="userSpaceOnUse")
    o.append(f'<rect x="88" y="218" width="364" height="482" fill="url(#{gid})" opacity=".82"/>')
    o.append(blob(ellipse_pts(330, 610, 70, 70, 20), "#ffd27a", .8))
    for i, (x0, x1) in enumerate(((60, 210), (240, 452))):
        o.append(blob([(x0, 700), (x0 + 30, 640), (x0 + 70, 660), (x0 + 110, 610), (x1, 650), (x1, 700)], "#2a2440", .9))
    o.append(line([(270, 218), (270, 700)], 12, "#5b4a5a", taper=0, wmin=1, seed=7701))
    o.append(line([(88, 420), (452, 420)], 12, "#5b4a5a", taper=0, wmin=1, seed=7702))
    # вечер: тёплый приглушённый тон всей кухни
    o.append('<rect x="-700" y="-700" width="2600" height="3000" fill="#c98a5a" opacity=".26" style="mix-blend-mode:multiply"/>')
    o.append('<rect x="-700" y="-700" width="2600" height="900" fill="#3a2a3a" opacity=".18"/>')
    # абажур на шнуре
    sw = 6 * math.sin(t * 1.3) + swing
    lx, ly = LAMP[0] + sw, LAMP[1]
    o.append(line([(LAMP[0], -700), (lx, ly - 70)], 3.4, "#3a2a22", taper=0, wmin=1, seed=7703))
    shade = [(lx - 30, ly - 70, 1), (lx + 30, ly - 70, 1), (lx + 110, ly + 30, 1), (lx - 110, ly + 30, 1)]
    o.append(shape(shade, "#e8823a", blob([(lx + 10, ly - 70), (lx + 30, ly - 70), (lx + 110, ly + 30), (lx + 40, ly + 30)], "#b85a22", .7), w=4.4, seed=7704))
    o.append(blob(ellipse_pts(lx, ly + 34, 70, 14, 16), "#fff2c4"))
    ch = R._side_chair(R.KS_SIT_L[0], R.KS_SIT_L[1], 1.0, 1, seed=0)
    # конус света от абажура до стола (пятно по форме абажура, край чёткий)
    cone = [(lx - 96, ly + 34), (lx + 96, ly + 34), (lx + 330, 1160), (lx - 330, 1160)]
    glow = blob(cone, "#ffe2a0", .16) + blob(ellipse_pts(lx, 1112, 300, 46, 24), "#ffeab8", .35)
    return dict(bg="".join(o), chair_back=ch["back"], chair_seat=ch["seat"], table=k["table"], glow=glow)


def listener(who, x, y, s, t, turn_t, expr_a, expr_b, flip=False, legs=False, seed=0, arms=None, hands=None, lean_add=0.0, extra_head=0.0, shrug=0.0):
    """Слушатель за столом: до turn_t смотрит вниз (на стол), потом поворачивает голову к Диме (справа). Живые моргания."""
    u = ease_io(clamp((t - turn_t) / .28))
    ea = people.EXPR.get(who, {}).get(expr_a, {}) if isinstance(expr_a, str) else expr_a
    eb = people.EXPR.get(who, {}).get(expr_b, {}) if isinstance(expr_b, str) else expr_b
    ex = dict(eb if u > .5 else ea)
    la, lb = ea.get("look", (.3, .6)), eb.get("look", (.6, 0))
    ex["look"] = lerp2(la, lb, u)
    bl = (t * 1.0 + seed * .37) % 3.1
    if bl < .12:
        ex["closed"] = math.sin(math.pi * bl / .12)
    kw = dict(people.sit_kw(x, y, s, who)) if legs else {}
    return people.person(who, x, y + 3 * math.sin(t * 2.1 + seed), s, ex, None, flip=flip, head_add=lerp(.22, -.06, u) + extra_head,
                         lean_add=lean_add + .03 * math.sin(t * 1.4 + seed), arms=arms, hands=hands, shrug=shrug, **kw)


# ═══════════════════════════════ s10: кухня, Дима рассказывает ═══════════════════════════════
# Дима — на переднем плане справа, крупно (свой масштаб и своя камера с параллаксом), слушатели — за столом в глубине.
FG_HIP = (850.0, 1640.0)      # таз Димы на экране (ноги за нижним краем), Дима смотрит влево
FG_S = .96


def fg_wrap(g, cx_off, cy_off, s=1.0):
    """Передний план: экранные координаты, параллакс камеры сильнее фона."""
    return f'<g transform="translate({540 + cx_off:.2f} {960 + cy_off:.2f}) scale({s:.4f}) translate(-540 -960)">{g}</g>'


def kitchen_back(t, people_svg, k_eve):
    o = [k_eve["bg"], k_eve["chair_back"], people_svg, k_eve["chair_seat"], k_eve["table"]]
    o.append(PR.mug(370, 1120, .5, col="red", coffee=True, steam=.6, t=t, seed=1))
    o.append(PR.mug(640, 1118, .5, col="blue", coffee=True, steam=.6, t=t, seed=2, handle=-1))
    o.append(k_eve["glow"])
    return "".join(o)


def s10(t):
    lib.dyn_begin()
    sh = SH["s10"]
    t0, t1 = sh["t0"], sh["t1"]
    T_DIMA, T_VSEM, T_RASS, T_CHTO, T_STAN = ws(48), ws(49), ws(50), ws(51), ws(52)
    ke = kitchen_eve(t)
    _hd = {"f": {"dir": (1, .3), "curl": (.5, .5, .55, .6), "thumb": .4}, "n": {"dir": (1, .3), "curl": (.4, .45, .5, .55), "thumb": .4}}
    gr = listener("granny", 400, 1110, .56, t, T_DIMA + .05, {"look": (.2, .7), "brows": "calm", "mouth": "smile", "smile": .3, "lid": .6},
                  "listen76", seed=1, arms={"f": ("ik", (450, 1095), -1), "n": ("ik", (520, 1090), -1)}, hands=_hd)
    fr = listener("friend", 600, 1105, .56, t, T_DIMA + .16, {"look": (-.4, .5), "brows": "calm", "mouth": "flat", "lid": .6}, "listen76", seed=2,
                  arms={"f": ("ik", (650, 1090), -1), "n": ("ik", (720, 1085), -1)}, hands=_hd)
    mm = listener("mama", R.KS_SIT_L[0], R.KS_SIT_L[1], .6, t, T_DIMA - .05, {"look": (.5, .5), "brows": "calm", "mouth": "smile", "smile": .4, "lid": .7},
                  "listen76", legs=True, seed=3, arms={"f": ("ik", (290, 1110), -1), "n": ("ik", (350, 1105), -1)}, hands=_hd)
    back = kitchen_back(t, gr["svg"] + fr["svg"] + mm["svg"], ke)
    # Дима: передний план справа, лицом влево (flip), горчичное худи; рассказывает
    dx, dy = FG_HIP
    s = FG_S
    talk = talking(t, 48, 52)
    ex = dict(people.EXPR["dima"]["tell76"])
    ex["open"] = .15 + .55 * talk
    ex["mouth"] = "talk" if talk > 0 else "grin"
    u_rect = clamp((t - (T_RASS - .05)) / (we(50) - T_RASS + .25))
    u_up = ease_io(clamp((t - (T_CHTO - .12)) / .3))
    sway = math.sin(2 * math.pi * 1.6 * (t - t0))
    g_arms = people.pose_kw("gesture76", dx, dy, s)["arms"]
    g_arms = {"f": g_arms["f"], "n": ("ik", (g_arms["n"][1][0] + 40 * sway * s, g_arms["n"][1][1] - 60 * s * (1 + .5 * sway)), -1)}
    sweep = ease_io(clamp((t - T_VSEM) / (T_RASS - T_VSEM)))
    if t < T_RASS - .15:      # жестикулирует: ладонь к слушателям, на «всем» обводит их рукой
        arms = g_arms
        hands = {"f": {"dir": (1, .3), "curl": (.4, .42, .46, .5), "thumb": .4},
                 "n": {"dir": (1, lerp(-.6, .1, sweep)), "spread": .35, "curl": (.05, .1, .15, .2), "thumb": .2}}
        if sweep > 0:
            arms = {"f": arms["f"], "n": ("ik", (dx + lerp(330, 400, sweep) * s, dy + lerp(-440, -320, sweep) * s), -1)}
    elif u_up <= 0:           # рисует руками прямоугольник-ноутбук
        rect = people.rect_hands(ease_io(u_rect), dx, dy, s, w=330, h=230)
        arms = arms_mix(g_arms, rect, clamp((t - (T_RASS - .15)) / .15))
        hands = {"f": {"dir": (.3, -1), "spread": .05, "curl": (0, .7, .8, .85), "thumb": .5},
                 "n": {"dir": (.3, -1), "spread": .05, "curl": (0, .7, .8, .85), "thumb": .5}}
    else:                     # палец вверх, мечтательно
        rect = people.rect_hands(1.0, dx, dy, s, w=330, h=230)
        up = pose_arms("point_up76", dx, dy, s)
        tgt_f = (dx + 170 * s, dy - 230 * s)
        arms = {"f": ("ik", lerp2(rect["f"][1], tgt_f, u_up), -1), "n": ("ik", lerp2(rect["n"][1], up["n"][1], u_up), -1)}
        hands = {"f": {"dir": (1, .4), "curl": (.4, .45, .5, .55), "thumb": .4},
                 "n": {"dir": (.15, -1), "curl": (0, .85, .9, .9), "spread": .05, "thumb": .7}}
        if t > T_STAN - .05:
            ex = dict(people.EXPR["dima"]["dream76"])
            ex["open"] = .1 + .4 * talk
            ex["mouth"] = "talk" if talk > 0 else "smile"
    ex["hair"] = 3 * abs(math.sin(t * 7)) if talk > 0 else 0.0
    lean = .04 * math.sin(2 * math.pi * .9 * (t - t0)) + .05 * bump(t, T_RASS, .4)
    d = people.dima(dx, dy, s, ex, None, flip=True, arms=arms, hands=hands, lean_add=lean,
                    head_add=-.04 + .08 * u_up - (.12 * u_up if t > T_STAN else 0.0), **people.stand_kw(dx, dy, s))
    fg = d["svg"]
    if u_up > .6:
        tip = d["wrist"]["n"]
        fg += PR.sparkles(tip[0], tip[1] - 130 * s, 1.0, (u_up - .6) / .4, t, seed=3, n=4, r=80)
    # камера: хлёст из перемотки, медленный дрейф к Диме, толчок на «рассказал»
    u = ease_io(clamp((t - t0) / (t1 - t0)))
    cs = lerp(1.06, 1.14, u) + .02 * bump(t, T_RASS, .35) + .015 * bump(t, T_STAN, .3)
    cx = lerp(470, 520, u) + 2 * math.sin(t * 1.7)
    cy = lerp(880, 870, u) + 2 * math.sin(t * 1.3)
    fgs = 1.0 + .05 * u + .035 * bump(t, T_RASS, .35)
    over = fg_wrap(fg, -lerp(0, 40, u), -lerp(0, 20, u), fgs)
    lib_bg = f'<g transform="{lib.cam(cx, cy, cs, lerp(-.6, .4, u))}">{back}</g>'
    return svg(whip_wrap('<rect width="1080" height="1920" fill="#3a2a2a"/>' + lib_bg + over, t, t0, dx=640))


# ═══════════════════════════════ s11: овация, мама вручает кубок ═══════════════════════════════
def s11(t):
    """Средний план на двоих: мама (слева, лицом вправо) и Дима (справа, лицом влево) у торца стола, слушатели за столом в глубине."""
    lib.dyn_begin()
    sh = SH["s11"]
    t0, t1 = sh["t0"], sh["t1"]
    T_PROG, T_I, T_EMU, T_HLOP = ws(53), ws(54), ws(55), ws(56)
    ke = kitchen_eve(t, swing=10 * bump(t, T_PROG, .6))
    up = ease_out(clamp((t - T_PROG) / .22), 2)       # вскакивают
    o = [ke["bg"]]
    for who, x, y, sc, ph, sd in (("granny", 250, 1110, .56, .1, 1), ("friend", 430, 1105, .56, .55, 2)):
        cu = people.clap_u(t, T_PROG, period=.36 + .03 * sd, phase=ph) if t > T_PROG + .08 else 0.0
        yy = y - 110 * up * sc
        a, h = people.clap_arms(cu, x, yy, sc, who, hy=-430)
        if t < T_PROG + .08:
            a = {"f": ("ik", (x + 50, y - 15), -1), "n": ("ik", (x + 120, y - 20), -1)}
            h = {"f": {"dir": (1, .3), "curl": (.5, .5, .55, .6), "thumb": .4}, "n": {"dir": (1, .3), "curl": (.4, .45, .5, .55), "thumb": .4}}
        ex = dict(people.EXPR[who]["cheer76"] if t > T_PROG + .05 else people.EXPR[who]["listen76"])
        ex["look"] = (.6, -.1)
        o.append(people.person(who, x, yy + 4 * math.sin(t * 9 + sd) * up, sc, ex, None, arms=a, hands=h, head_add=-.08 * up, lean_add=-.05 * up)["svg"])
    o.append(ke["table"])
    o.append(PR.mug(370, 1120, .5, col="red", coffee=True, steam=.6, t=t, seed=1))
    o.append(PR.mug(560, 1118, .5, col="blue", coffee=True, steam=.6, t=t, seed=2, handle=-1))
    o.append(ke["glow"])
    o.append(PR.confetti((60, 300, 1100, 1500), t, T_PROG + .02, n=30, seed=11, burst=(560, 520), life=1.8))
    # мама (слева) и Дима (справа) стоят перед столом
    ms, s = .62, .64
    msc = ms * people.HEIGHT["mama"]
    sc_d = s * people.HEIGHT["dima"]
    floor = R.KS_FLOOR + 160
    mx, my = 560.0, floor - (people.LEG_LEN - 12) * msc - 8
    dx, dy = 900.0, floor - (people.LEG_LEN - 12) * sc_d - 8
    o.append(blob(ellipse_pts(mx + 20, floor + 6, 150, 14, 16), "#4a2e22", .25) + blob(ellipse_pts(dx - 10, floor + 6, 160, 14, 16), "#4a2e22", .25))
    tk = .62
    m_hold = (mx + 240 * msc, my - 250 * msc + 150 * tk)
    m_give = (mx + 380 * msc, my - 330 * msc + 150 * tk)
    give = ease_io(clamp((t - (T_I - .15)) / (T_EMU - T_I + .2)))
    taken = t >= T_EMU + .1
    lift = ease_out(clamp((t - (T_HLOP - .1)) / .3), 2) if taken else 0.0
    d_head0 = people.dima(dx, dy, s, {}, None, flip=True, layers=())["head"]
    tkd = tk * 1.15
    over = (d_head0[0] + 40 * sc_d, d_head0[1] - 250 * sc_d)
    if not taken:
        tro = lerp2(m_hold, m_give, give)
        tro_k = tk
    else:
        tro = lerp2(m_give, over, lift)
        tro_k = lerp(tk, tkd, lift)
    hl, hr = (tro[0] - 124 * tro_k, tro[1] - 250 * tro_k), (tro[0] + 124 * tro_k, tro[1] - 250 * tro_k)
    # мама: держит кубок двумя руками, протягивает; отдала — хлопает
    if not taken:
        ma = {"f": ("ik", (hl[0] + 30, hl[1] + 40), -1), "n": ("ik", (tro[0] + 10, tro[1] - 120 * tro_k), -1)}
        mh = {"f": {"dir": (.4, -1), "curl": (.6, .64, .68, .72), "thumb": .55}, "n": {"dir": (.6, -1), "curl": (.62, .66, .7, .74), "thumb": .6}}
    else:
        cu = people.clap_u(t, T_EMU + .1, period=.36, phase=.3)
        ma, mh = people.clap_arms(cu, mx, my, ms, "mama", hy=-430)
    mex = dict(people.EXPR["mama"]["cheer76"] if t > T_PROG else people.EXPR["mama"]["proud76"])
    mex["look"] = (.7, -.1 - .4 * lift)
    mkw = dict(arms=ma, hands=mh, head_add=-.06 - .1 * lift, **people.stand_kw(mx, my, ms, "mama"))
    o.append(people.person("mama", mx, my, ms, mex, None, layers=("legs", "pelvis", "arm_f", "body"), **mkw)["svg"])
    # Дима: до «ему» удивлён, тянет руки; потом сжимает ручки кубка и поднимает над головой
    if not taken:
        u_reach = ease_io(clamp((t - (T_I - .05)) / (T_EMU - T_I + .1)))
        ex = dict(people.EXPR["dima"]["tell76"])
        ex.update(mouth="o", open=.35 + .25 * bump(t, T_PROG, .4), lid=1.0, look=(.6, .25), brows="up")
        ex["hair"] = 5 * bump(t, T_PROG, .3)
        base = {"f": ("ik", (dx + 200 * sc_d, dy - 260 * sc_d), -1), "n": ("ik", (dx + 250 * sc_d, dy - 300 * sc_d), -1)}
        reach = {"f": ("ik", (2 * dx - hr[0] + 10, hr[1] + 40), -1), "n": ("ik", (2 * dx - hr[0] - 30, hr[1] + 70), -1)}
        arms = arms_mix(base, reach, u_reach)
        hands = {"f": {"dir": (1, -.1), "spread": .3, "curl": (.1, .15, .2, .25), "thumb": .2},
                 "n": {"dir": (1, -.2), "spread": .3, "curl": (.1, .15, .2, .25), "thumb": .2}}
        if u_reach > .85:
            hands = {"f": {"dir": (.3, -1), "curl": (.62, .66, .7, .74), "thumb": .55}, "n": {"dir": (.5, -1), "curl": (.62, .66, .7, .74), "thumb": .55}}
        hd_add = 0.0
    else:
        ex = dict(people.EXPR["dima"]["beam76"])
        ex["hair"] = 6 * abs(math.sin(t * 9)) * lift
        # flip: ближняя рука (n) — слева на экране → левая ручка, дальняя (f) — правая
        arms = {"f": ("ik", (2 * dx - hr[0], hr[1] + 24), -1), "n": ("ik", (2 * dx - hl[0], hl[1] + 24), -1)}
        hands = {"f": {"dir": (.1, -1), "curl": (.62, .66, .7, .74), "thumb": .55}, "n": {"dir": (-.1, -1), "curl": (.62, .66, .7, .74), "thumb": .55}}
        hd_add = -.16 * lift
    hop = PR.hop(t, T_HLOP, 30, .34) if taken else 0.0
    kw = dict(flip=True, arms=arms, hands=hands, head_add=hd_add, lean_add=-.04 * lift, **people.stand_kw(dx, dy - hop, s))
    tro_svg = PR.trophy(tro[0], tro[1] - hop * lift, tro_k, glint=clamp((t - T_HLOP) / .5) if taken else 0.0, t=t)
    if lift > .35:      # руки за головой (лицо не закрыто), кубок поверх кистей — ручки читаются как хват
        o.append(people.dima(dx, dy - hop, s, ex, None, layers=people.LAYERS_BEHIND, **kw)["svg"])
        o.append(tro_svg)
    else:
        o.append(people.dima(dx, dy - hop, s, ex, None, layers=("legs", "pelvis", "arm_f", "body"), **kw)["svg"])
        o.append(tro_svg)
        o.append(people.dima(dx, dy - hop, s, ex, None, layers=("arm_n",), **kw)["svg"])
    o.append(people.person("mama", mx, my, ms, mex, None, layers=("arm_n",), **mkw)["svg"])
    if taken:
        o.append(PR.sparkles(tro[0], tro[1] - hop - 200 * tro_k, 1.1, clamp((t - T_HLOP) / .2), t, seed=5, n=5, r=160))
    o.append(PR.confetti((260, 100, 1200, 1700), t, T_HLOP, n=60, seed=12, burst=(tro[0], tro[1] - 260 * tro_k), life=1.6))
    # камера: средний план на двоих, удар-наезд на «хлопали», тряска на конфетти
    u = ease_io(clamp((t - t0) / (t1 - t0)))
    punch = .1 * ease_out(clamp((t - T_HLOP) / .14), 3) * (1 - .4 * clamp((t - T_HLOP - .14) / .5))
    shk = 9 * math.exp(-6 * max(0.0, t - T_HLOP)) * math.sin(55 * (t - T_HLOP)) if t > T_HLOP else 0.0
    shk += 5 * math.exp(-7 * max(0.0, t - T_PROG)) * math.sin(48 * (t - T_PROG)) if t > T_PROG else 0.0
    cs = lerp(1.32, 1.28, u) + punch
    cx, cy = lerp(720, 740, u) + shk, lerp(960, 930, u) - 60 * lift + .6 * shk
    return frame_svg("".join(o), cx, cy, cs, lerp(.3, -.4, u), bg="#3a2a2a")


# ═══════════════════════════════ комната хука (s02, s07, s08) ═══════════════════════════════
A = R.A76


def chew_mouth(t, rate=3.2):
    """Фаза жевания 0…1 (рот трубочкой то сжат, то приоткрыт)."""
    return .5 + .5 * math.sin(2 * math.pi * rate * t)


def conf_time(t, F, hold=.5):
    """Время конфетти с замиранием: до F идёт, F…F+hold стоит, потом идёт дальше (без скачка)."""
    if t < F:
        return t
    if t < F + hold:
        return F
    return t - hold


def blink(t, seed=0.0, period=3.3):
    p = (t + seed) % period
    return math.sin(math.pi * p / .14) if p < .14 else 0.0


def s02(t):
    lib.dyn_begin()
    sh = SH["s02"]
    t0, t1 = sh["t0"], sh["t1"]
    T_A, T_SDEL, T_NICH = ws(3), ws(6), ws(8)
    tr = R.trophy_room(t, "hook", light="spot")
    mx, my, mk = A["MAT"]
    hx, hy = A["HIP"]
    k = A["DK"]
    sc = k * people.HEIGHT["dima_pj"]
    o = [tr["bg"], PR.floor_mattress(mx, my, mk, sag=.18, sag_x=A["TROPHY"][0], layer="back"), tr["pool"]]
    # хореография Димы: жуёт → «а он не сделал» пожимает плечом → «сделал» хрустит чипсом → «ничего» разводит руками
    u_sh = ease_io(clamp((t - (T_A - .05)) / .22)) * (1 - ease_io(clamp((t - (T_SDEL - .25)) / .2)))
    u_chip = ease_io(clamp((t - (T_SDEL - .25)) / .2)) * (1 - ease_io(clamp((t - (T_SDEL + .25)) / .2)))
    u_spr = ease_out(clamp((t - (T_NICH - .1)) / .2), 2) * (1 - ease_io(clamp((t - (we(8) + .35)) / .3)))
    P_chew = people.pose_kw("chew76", hx, hy, k, "dima_pj")
    P_sh = people.pose_kw("shrug76", hx, hy, k, "dima_pj")
    P_chip = people.pose_kw("chips76", hx, hy, k, "dima_pj")
    P_spr = people.pose_kw("spread76", hx, hy, k, "dima_pj")
    arms = arms_mix(P_chew["arms"], P_sh["arms"], u_sh)
    arms = arms_mix(arms, P_chip["arms"], u_chip)
    arms = arms_mix(arms, P_spr["arms"], u_spr)
    hands = P_spr["hands"] if u_spr > .4 else (P_chip["hands"] if u_chip > .5 else (P_sh["hands"] if u_sh > .5 else P_chew["hands"]))
    lean = lerp(P_chew["lean"], P_spr["lean"], u_spr)
    ex = dict(people.EXPR["dima"]["chew76"])
    ex["chew"] = chew_mouth(t)
    if u_sh > .3:
        ex = dict(people.EXPR["dima"]["shrug76"])
    if t > T_SDEL + .02 and u_spr < .3:
        ex = dict(people.EXPR["dima"]["chew76"])
        ex["chew"] = chew_mouth(t, 5.0)
        ex["brows"] = "calm"
    if u_spr > .3:
        ex = dict(people.EXPR["dima"]["brow76"])
        ex.update(mouth="side", look=(-.2, -.05))
    ex["closed"] = blink(t, .7)
    ex["hair"] = 3 * bump(t, T_SDEL + .05, .25) + 3 * bump(t, T_NICH, .3)
    shrug = .55 * u_sh + .25 * u_spr
    kw = dict(arms=arms, hands=hands, lean_add=lean - P_chew["lean"], shrug=shrug, head_add=.04 * math.sin(t * 2.3) - .05 * u_sh,
              **people.mattress_kw(hx, hy, k))
    fig = people.dima_pj(hx, hy, k, ex, "chew76", layers=("legs", "pelvis", "arm_f", "body"), **kw)
    o.append(fig["svg"])
    # пакет чипсов в дальней руке (поверх тела, под ближней рукой)
    wf = fig["wrist"]["f"]
    o.append(PR.chips_bag(wf[0] + 30 * sc, wf[1] - 40 * sc, .8 * sc / .86, rot=-18 + 25 * u_spr, crunch=.3 + .2 * math.sin(t * 3)))
    # кубок лежит на коленях (поверх ног), не замечен
    tx, ty, tk = A["TROPHY"]
    tx, tk = tx - 70, tk * .9            # новый ракурс: кубок на коленях чуть ближе к Диме, целиком в кадре
    o.append(PR.trophy(tx, ty, tk, glint=clamp((t - t0 - .3) / .9), t=t, rot=-8))
    arm_n = people.dima_pj(hx, hy, k, ex, "chew76", layers=("arm_n",), **kw)
    o.append(arm_n["svg"])
    mp = people.mouth_pt(fig, lean, kw["head_add"])
    if u_chip > .05:      # чипс в пальцах у рта, хруст на «сделал»
        hp = people.hand_pos(arm_n, "n", 55)
        if t < T_SDEL + .02:
            o.append(PR.chip(hp[0], hp[1], .7, rot=20 + 40 * u_chip))
    o.append(PR.chip_crumbs(mp[0] + 10, mp[1] + 10, .9, (t - (T_SDEL + .02)) / .5, seed=3, n=8))
    o.append(PR.floor_mattress(mx, my, mk, sag=.18, sag_x=tx, layer="front"))
    o.append(tr["light"])
    # конфетти: сыплется с кадра 0, на «ничего» замирает на полсекунды
    tc = conf_time(t, T_NICH + .05)
    o.append(PR.confetti((-200, -300, 1300, 1500), tc, 0.0, n=46, seed=21))
    # камера: лёгкий хлёст-дрейф вбок от s01, медленный наезд; на замирании — пауза 2 кадра и толчок
    tcam = conf_time(t, T_NICH + .05, 2 / 30)
    u = ease_io(clamp((tcam - t0) / (t1 - t0)))
    push = .035 * ease_out(clamp((t - (T_NICH + .05 + 2 / 30)) / .2), 2)
    cs = lerp(1.1, 1.14, u) + push
    cx = lerp(500, 485, u) + 2 * math.sin(tcam * 1.5)
    cy = lerp(800, 812, u) + 2 * math.sin(tcam * 1.2)
    body = f'<g transform="{lib.cam(cx, cy, cs, lerp(-1.6, -1.0, u))}">{"".join(o)}</g>'
    # толпа на переднем плане (экранные координаты): затылки и ладони, хлопают с кадра 0
    crowd = people.crowd_backs(-60, 2010, 1200, t, clap_phase=.15, n=4, k=.92, seed=1)
    over = f'<g transform="translate({-30 * u:.1f} 0)">{crowd}</g>'
    title = R.hook_title(t, we(8))
    return svg(whip_wrap('<rect width="1080" height="1920" fill="#efe0bc"/>' + body + over, t, t0, dx=-260, dur=.18) + title)


# ═══════════════════════════════ s07: лапа кота у губ — «тсс» ═══════════════════════════════
def s07(t):
    """Дима сидит, ноги вытянуты, наклонился к коту — вот-вот похвастается; кот на дальнем краю матраса (у стены) тянет лапу к его губам."""
    lib.dyn_begin()
    sh = SH["s07"]
    t0, t1 = sh["t0"], sh["t1"]
    T_POKA, T_SDEL = ws(31), ws(33)
    tr = R.trophy_room(t, "hook", light="day")
    mx, my, mk = A["MAT"]
    hx, hy = 270.0, 1170.0
    k = .9
    sc = k * people.HEIGHT["dima_pj"]
    o = [tr["bg"], PR.floor_mattress(mx, my, mk, sag=.1, sag_x=hx + 100, layer="back")]
    o.append(PR.laptop_closed(940, 925, 1.0, rot=-4))
    cat_p = (735.0, 965.0)
    ck = .84
    land = t0 + .14
    ju = clamp((t - (t0 - .26)) / (land - (t0 - .26)))
    shh = ease_out(clamp((t - (T_SDEL - .06)) / .16), 2)
    lean = .5 + .04 * math.sin(2 * math.pi * 1.1 * (t - t0)) * (1 - shh) - .06 * shh
    head_add = .18 + .03 * math.sin(t * 2.0) * (1 - shh)
    # ближняя ладонь хлопает себя по груди («вот я какой!»), дальняя опирается о матрас позади
    pat = 14 * abs(math.sin(2 * math.pi * 2.2 * (t - t0))) * (1 - shh)
    chest = people.rot(people.np.array([150.0 - pat, -250.0]), lean) * sc
    arms = {"f": ("ik", (hx - 60 * sc, hy + 30 * sc), 1), "n": ("ik", (hx + chest[0], hy + chest[1]), -1)}
    hands = {"f": {"dir": (-.3, 1), "spread": .3, "curl": (.1, .1, .15, .2), "thumb": .2},
             "n": {"dir": (-.5, -.6), "spread": .15, "curl": (.1, .12, .15, .2), "thumb": .25}}
    if shh > .3:
        ex = dict(people.EXPR["dima"]["puffed76"])
        ex["look"] = (.75, .1)
    else:
        ex = dict(people.EXPR["dima"]["boast76"])
        ex["open"] = .45 + .2 * math.sin(t * 9)
        ex["look"] = (.7, .1)
    ex["closed"] = blink(t, 1.3) * (1 - shh)
    ex["hair"] = 4 * bump(t, T_SDEL, .25)
    kwd = dict(arms=arms, hands=hands, lean_add=lean, head_add=head_add, **people.plop_kw(hx, hy, k))
    fig = people.dima_pj(hx, hy, k, ex, None, **kwd)
    mouth = people.mouth_pt(fig, lean, head_add)
    o.append(fig["svg"])
    if ju < 1:
        o.append(people.cat_jump((1000.0, 1300.0), cat_p, ck, ju, t, {"look": (-.4, 0)}))
        tip = None
    else:
        u_raise = ease_io(clamp((t - (T_POKA - .05)) / .2)) * .45 + .55 * ease_io(clamp((t - (T_SDEL - .2)) / .2))
        st = {"look": (-.8, .1), "perk": 1.0 - shh * .5, "blink": .55 * shh, "smile": .5 * shh, "tilt": -6 * shh}
        st["sx"], st["sy"] = PR.squash(t, land, .18, 3.0, 8)
        cat_sv, tip = people.cat_shh76(cat_p[0], cat_p[1], ck, t, u_raise, tip=(mouth[0] + 6, mouth[1] + 4), st=st, side="l")
        o.append(cat_sv)
    o.append(PR.floor_mattress(mx, my, mk, sag=.1, sag_x=hx + 100, layer="front"))
    if tip is not None and shh > .5:        # «тсс»: тихие штрихи у лапы
        for j, a in enumerate((-2.5, -2.0, -1.5)):
            r0, r1 = 46 + 10 * shh, 76 + 16 * shh
            o.append(line([(tip[0] + r0 * math.cos(a), tip[1] + r0 * math.sin(a)), (tip[0] + r1 * math.cos(a), tip[1] + r1 * math.sin(a))], 4.5, INK,
                          seed=7740 + j, op=clamp((shh - .5) * 2)))
    o.append(tr["light"])
    # камера: средний план, лёгкий наезд на лапу у губ
    u = ease_io(clamp((t - t0) / (t1 - t0)))
    cs = lerp(1.3, 1.4, u) + .03 * bump(t, T_SDEL, .3)
    cx = lerp(500, 540, u) + 2 * math.sin(t * 1.4)
    cy = lerp(990, 960, u) + 2 * math.sin(t * 1.1)
    return frame_svg("".join(o), cx, cy, cs, lerp(.8, .2, u), bg="#efe0bc")


# ═══════════════════════════════ s08: дудка снова и снова, ноутбук в пыли ═══════════════════════════════
def horn_unroll(t, blows, up=.13, down=.4):
    """Развёрнутость дудки 0…1: на каждом выдуве быстро разворачивается и медленнее сворачивается обратно."""
    v = 0.0
    for tb in blows:
        if t >= tb:
            e = t - tb
            v = max(v, ease_out(clamp(e / up), 2) if e < up else 1 - ease_io(clamp((e - up - .08) / down)))
    return v


def dusty_laptop(x, y, k, t, seed=0):
    """Закрытый ноутбук на полу (крышка в перспективе) под слоем пыли: серая пелена и пылинки на крышке, пылинки в воздухе."""
    o = [PR.laptop(x, y, k, open_=0.0)]
    rs = __import__("random").Random(7750 + seed)
    lid = [(x - 232 * k, y - 132 * k), (x + 232 * k, y - 132 * k), (x + 255 * k, y - 4 * k), (x - 255 * k, y - 4 * k)]
    o.append(blob(lid, "#e2dccf", .45))
    for j in range(70):
        v, w_ = rs.uniform(0, 1), rs.uniform(-1, 1)
        px = x + w_ * (232 + 23 * v) * k
        py = y - 132 * k + v * 126 * k
        o.append(blob(ellipse_pts(px, py, rs.uniform(2.2, 4.4) * k, rs.uniform(1.4, 2.6) * k, 6), "#a8a194", .75))
    for j in range(10):        # пылинки в воздухе над ноутбуком
        ph = rs.uniform(0, 6.28)
        px = x + rs.uniform(-220, 220) * k + 14 * k * math.sin(t * .7 + ph)
        py = y - rs.uniform(170, 380) * k + 10 * k * math.sin(t * .5 + ph)
        o.append(blob(ellipse_pts(px, py, 4 * k, 4 * k, 6), "#d9d1c0", .95))
    return "".join(o)


def s08(t):
    lib.dyn_begin()
    sh = SH["s08"]
    t0, t1 = sh["t0"], sh["t1"]
    T_NE, T_NAP, T_BUD, T_TOL, T_OBE = ws(34), ws(35), ws(38), ws(39), ws(40)
    tr = R.trophy_room(t, "hook", light="day")
    mx, my, mk = A["MAT"]
    hx, hy = 290.0, 1175.0
    k = .95
    sc = k * people.HEIGHT["dima_pj"]
    o = [tr["bg"], PR.floor_mattress(mx, my, mk, sag=.1, sag_x=hx + 100, layer="back")]
    lap = (780.0, 1470.0)
    lap_svg = dusty_laptop(lap[0], lap[1], .85, t) + PR.dust_puff(lap[0], lap[1] - 80, 1.1, (t - (T_OBE - .05)) / .9, seed=4)
    # кот на дальнем краю матраса: уши опущены, медленно моргает (лапу у губ Дима отвёл на «Не»)
    cat_p = (745.0, 965.0)
    ck = .84
    away = ease_io(clamp((t - (T_NE - .05)) / .25))
    st = dict(people.CAT_ST76["sad"])
    st["blink"] = .45 + .55 * max(0.0, math.sin(2 * math.pi * (t - T_NAP) / 1.6)) ** 6
    st["paw_l"] = .9 * (1 - away)
    st["paw_l_dx"] = 80
    st["look"] = (-.6, .2)
    st["drop"] = .08 * away
    o.append(people.cat_svg(cat_p[0], cat_p[1], ck, st, t))
    # Дима: сидит, ближняя рука держит дудку у рта; на «Не» отводит лапу кота дальней рукой
    blows = [T_NAP - .05, T_BUD - .05, T_TOL - .02, T_OBE - .02]
    un = horn_unroll(t, blows)
    blowing = un > .05
    lean = .12 + .03 * math.sin(t * 2.2) + .05 * un
    P_h = people.pose_kw("horn76", hx, hy, k, "dima_pj")
    f_push = ("ik", (hx + 470 * sc, hy - 500 * sc), -1)
    f_rest = P_h["arms"]["f"]
    pu = bump(t, T_NE - .1, .55)
    arms = {"f": ("ik", lerp2(f_rest[1], f_push[1], pu), -1), "n": P_h["arms"]["n"]}
    hold = ease_io(clamp((t - (T_NE + .05)) / .3))
    arms["n"] = ("ik", lerp2((hx + 300 * sc, hy - 80 * sc), P_h["arms"]["n"][1], hold), -1)
    hands = {"f": P_h["hands"]["f"] if pu < .3 else {"dir": (1, -.2), "spread": .3, "curl": (.1, .15, .2, .25), "thumb": .2},
             "n": P_h["hands"]["n"] if hold > .5 else {"dir": (1, .4), "curl": (.62, .66, .7, .74), "thumb": .55}}
    if blowing:
        ex = dict(people.EXPR["dima"]["blow76"])
        ex["puff"] = .6 + .4 * un
    else:
        ex = dict(people.EXPR["dima"]["shh76"])
        ex.update(mouth="o", open=.25, look=(.6, .05), brows="up")
    ex["closed"] = blink(t, .4) * (1 - un)
    head_add = .04 - .06 * un
    kwd = dict(arms=arms, hands=hands, lean_add=lean - P_h["lean"], head_add=head_add, **people.sit_mat_kw(hx, hy, k))
    fig = people.dima_pj(hx, hy, k, ex, "horn76", layers=("legs", "pelvis", "arm_f", "body"), **kwd)
    o.append(fig["svg"])
    mp = people.mouth_pt(fig, lean, head_add)
    if hold > .02:
        hk = .95 * hold
        o.append(PR.party_horn(mp[0] - 4, mp[1] + 2, hk, rot=-36 + 8 * un, unroll=un, t=t))
    o.append(people.dima_pj(hx, hy, k, ex, "horn76", layers=("arm_n",), **kwd)["svg"])
    o.append(PR.floor_mattress(mx, my, mk, sag=.1, sag_x=hx + 100, layer="front"))
    o.append(lap_svg)
    o.append(tr["light"])
    # камера: чуть сверху (наклон), дрейф вниз-вправо к ноутбуку на «только обещать» и обратно, толчок на каждом выдуве
    u = ease_io(clamp((t - t0) / (t1 - t0)))
    to_lap = ease_io(clamp((t - (T_TOL - .2)) / .45)) * (1 - ease_io(clamp((t - (T_OBE + .35)) / .4)) * .6)
    kick = sum(.025 * bump(t, tb, .22) for tb in blows)
    cs = lerp(1.24, 1.3, u) - .18 * to_lap + kick
    cx = lerp(560, 590, u) + 60 * to_lap + 2 * math.sin(t * 1.3)
    cy = lerp(930, 920, u) + 300 * to_lap + 2 * math.sin(t * 1.0)
    return frame_svg("".join(o), cx, cy, cs, lerp(2.0, 1.4, u), bg="#efe0bc")


def laptop_side76(x, y, k=1.0, open_=1.0, glow=0.0, face=-1, t=0.0, seed=0):
    """Ноутбук сбоку в три четверти: экран смотрит ВЛЕВО (face=-1, к сидящему слева Диме) или вправо (face=1); зритель видит торец
    корпуса и тыльную сторону крышки, экрана не видно. (x, y) — центр низа корпуса на столе; open_ 0 — закрыт, 1 — открыт
    (крышка от петли на дальнем от хозяина краю, чуть откинута назад); glow — свет экрана, падает в сторону хозяина."""
    sd = 7760 + seed
    Ld, th = 300 * k, 16 * k
    dv = (80 * k, -34 * k)                   # глубина корпуса (вглубь сцены)
    xl, xr = x - Ld / 2, x + Ld / 2
    o = []
    o.append(blob(ellipse_pts(x + dv[0] / 2, y + 4 * k, Ld * .6, 12 * k, 16), "#000000", .18))
    top = [(xl, y - th), (xr, y - th), (xr + dv[0], y - th + dv[1]), (xl + dv[0], y - th + dv[1])]
    keys = ""
    for r_ in range(3):
        v = .25 + r_ * .25
        p0 = (xl + 26 * k + dv[0] * v, y - th + dv[1] * v)
        p1 = (xr - 70 * k + dv[0] * v, y - th + dv[1] * v)
        keys += line([p0, p1], 5 * k, "#4a505c", taper=0.0, wmin=1.0, seed=sd + r_, op=.75)
    o.append(shape([pt + (1,) for pt in top], "#c9cdd5", keys, w=3.6 * k, seed=sd + 10))
    o.append(shape(lib.rrect(xl, y - th, xr, y, 4 * k), "#9fa4ae", line([(xl + 8 * k, y - th * .5), (xr - 8 * k, y - th * .5)], 2 * k, "#7f8590",
                                                                     taper=.1, wmin=.8, seed=sd + 11), w=3.6 * k, seed=sd + 12))
    # крышка: петля на дальнем от хозяина крае; угол от «лежит на корпусе» до «открыта, откинута назад»
    hx = xr if face < 0 else xl
    a0 = math.pi if face < 0 else 0.0
    a1 = math.radians(285) if face < 0 else math.radians(255)
    a = a0 + (a1 - a0) * clamp(open_)
    L = 280 * k
    u = (math.cos(a) * L, math.sin(a) * L)
    h0 = (hx, y - th)
    lid = [h0, (h0[0] + u[0], h0[1] + u[1]), (h0[0] + u[0] + dv[0], h0[1] + u[1] + dv[1]), (h0[0] + dv[0], h0[1] + dv[1])]
    inner = blob(ellipse_pts(h0[0] + u[0] * .55 + dv[0] * .5, h0[1] + u[1] * .55 + dv[1] * .5, 16 * k, 12 * k, 10), "#c6cad2", .9)
    o.append(shape([pt + (1,) for pt in lid], "#aeb3bd", inner, w=4 * k, seed=sd + 13))
    edge = [(h0[0] + u[0], h0[1] + u[1]), (h0[0] + u[0] + dv[0], h0[1] + u[1] + dv[1])]
    o.append(line(edge, 6 * k, "#2e323a", taper=0.0, wmin=1.0, seed=sd + 14))
    if glow > .01 and open_ > .5:             # свет экрана стекает в сторону хозяина (влево), с чётким краем у крышки
        sgn = -1 if face < 0 else 1
        cx_ = h0[0] + u[0] * .5 + sgn * 40 * k
        cy_ = h0[1] + u[1] * .5
        fl = 1 + .05 * math.sin(t * 11)
        o.append(f'<g {lib.blur(10)}>{blob([(cx_, cy_ - 140 * k), (cx_ + sgn * 260 * k, cy_ - 210 * k), (cx_ + sgn * 260 * k, cy_ + 170 * k), (cx_, cy_ + 120 * k)], "#cfe6ff", .22 * glow * fl)}</g>')
    return "".join(o)


# ═══════════════════════════════ s17: сейчас — кубок-стакан, палец у губ, ноутбук к себе ═══════════════════════════════
LAP17_TURN = .72           # экран к Диме (Дима слева, лицом вправо; зритель видит крышку сзади-сбоку)


def s17(t):
    lib.dyn_begin()
    sh = SH["s17"]
    t0, t1 = sh["t0"], sh["t1"]
    T_POET, T_DIMA, T_SNACH, T_MOLCH = ws(86), ws(88), ws(89), ws(90)
    bs = .9                   # Дима чуть меньше и ниже: голова не заходит на картину на стене
    sx, sy = R.SIT[0], R.seat_y(bs)
    de = R.desk_evening(t)
    Ad = de["A"]
    sc_ = R.desk_scene(t, "evening", sit=(sx, sy), bs=bs)
    sc_["bg"] += de["shelf"]
    settle = 1 - ease_out(clamp((t - (t0 - .2)) / .45), 3)
    hipy = sy - 60 * settle
    feet = {"n": ((sx + 300 * bs, R.FL - 50 * bs), 0.0), "f": ((sx + 250 * bs, R.FL - 48 * bs), 0.0)}
    glance = ease_io(clamp((t - (T_DIMA - .25)) / .25)) * (1 - ease_io(clamp((t - (T_SNACH - .05)) / .2)))
    shh = ease_io(clamp((t - (T_SNACH - .1)) / .25))
    open_u = ease_io(clamp((t - (T_MOLCH - .15)) / .35))
    # руки: ближняя — к губам («тсс»), дальняя — на крышке ноутбука, открывает её к себе
    lx, ly = 680.0, R.DESK_TOP + 6          # ноутбук ближе к Диме (у края стола под его руками)
    lk = .8
    desk_arms = people.pose_kw("type76", sx, hipy, bs)
    tgt_lips = people.lips76(sx, hipy, bs, desk_arms["lean"], .08 - .1 * glance)
    arms = dict(desk_arms["arms"])
    arms["n"] = ("ik", lerp2(arms["n"][1], tgt_lips, shh), -1)
    a_l = math.pi + math.radians(105) * open_u
    lid_pt = (lx + 150 * lk + math.cos(a_l) * 280 * lk * .55, ly + 36 - 16 * lk + math.sin(a_l) * 280 * lk * .55 + 20)
    reach_lid = ease_io(clamp((t - (T_MOLCH - .3)) / .2))
    arms["f"] = ("ik", lerp2(arms["f"][1], lid_pt, reach_lid), -1)
    hands = dict(desk_arms["hands"])
    if shh > .4:
        hands["n"] = {"dir": (.1, -1), "curl": (0, .88, .92, .92), "spread": .03, "thumb": .75}
    if reach_lid > .4:
        hands["f"] = {"dir": (.6, -.5), "curl": (.3, .35, .4, .45), "thumb": .3}
    if shh > .3:
        ex = dict(people.EXPR["dima"]["shh76"])
        ex["look"] = (.55, .45) if open_u > .3 else (.1, 0)
    elif glance > .3:
        ex = dict(people.EXPR["dima"]["glance76"])
        ex["look"] = (.6, -.85)
    else:
        ex = dict(people.EXPR["dima"]["screen76"])
        ex.update(look=(.5, .4), mouth="flat")
    ex["closed"] = blink(t, 2.1) * (1 - shh)
    head_add = .08 - .14 * glance + .04 * shh
    kw = dict(arms=arms, hands=hands, head_add=head_add, feet=feet)
    parts = {kk: people.dima(sx, hipy, bs, ex, "type76", layers=(kk,), **kw) for kk in ("legs", "pelvis", "arm_f", "body", "arm_n")}
    glow = .85 * open_u
    lap = laptop_side76(lx, ly + 36, lk, open_u, glow=glow, face=-1, t=t)
    # свет экрана на лице (пятно по форме, мерцает)
    hd = parts["body"]["head"]
    face_light = (f'<g {lib.blur(22)}>{blob(ellipse_pts(hd[0] + 70, hd[1] + 30, 70, 110, 20), "#cfe6ff", .16 * glow * (1 + .05 * math.sin(t * 11)))}</g>'
                  if glow > .02 else "")
    # кубок-стакан с карандашами на полке
    cx_, cy_ = Ad["CUP"]
    cup = PR.trophy_pencils(cx_, cy_, .55, t=t)
    cup += PR.sparkles(cx_, cy_ - 120, .7, glance, t, seed=8, n=3, r=70)
    # кот на подоконнике слева, кивает на «молча»
    cat_st = dict(people.CAT_ST76["sill"])
    cat_st["drop"] = people.cat_nod(t, T_SNACH + .1, .34, .3) + people.cat_nod(t, T_MOLCH + .05, .34, .25)
    cat_st["look"] = (.8, .3)
    cat_sv = people.cat_svg(-175, 1146, .68, cat_st, t)
    body = (sc_["bg"] + cat_sv + cup + sc_["chair_back"] + sc_["desk_top"] + sc_["pool"] + parts["legs"]["svg"] + sc_["desk_legs"] + sc_["chair_seat"]
            + parts["pelvis"]["svg"] + parts["arm_f"]["svg"] + parts["body"]["svg"] + face_light + lap + parts["arm_n"]["svg"] + sc_["lamp"])
    u = ease_io(clamp((t - t0) / (t1 - t0)))
    cs = lerp(.88, .95, u) + .02 * bump(t, T_MOLCH, .3)
    cx = lerp(380, 400, u) + 2 * math.sin(t * 1.4)
    cy = lerp(960, 930, u) + 2 * math.sin(t * 1.1)
    return svg(whip_wrap(f'<rect width="1080" height="1920" fill="#2a2440"/><g transform="{lib.cam(cx, cy, cs, lerp(-.5, .3, u))}">{body}</g>',
                         t, t0, dx=640))


SCENES = {"s02": s02, "s07": s07, "s08": s08, "s17": s17, "s10": s10, "s11": s11}


def frame(sid, t):
    return SCENES[sid](t)
