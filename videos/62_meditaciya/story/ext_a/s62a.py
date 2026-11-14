"""Рилс 62 «медитация», группа A: предметы крупно и «кроты».
s02 (1.4–2.7, хлёст): песочные часы крупно на полу у подушки, за ними размыто колено в лотосе. Рука Димы держит часы за талию
    (пальцы огибают раму, большой палец сверху), на «десять» (1.49) переворачивает их рывком (переворот через ребро — часы
    сплющиваются в линию и раскрываются), часы стукают об пол со сжатием и отскоком, рука уходит; на «минут» (1.83) застрявший
    песок срывается струёй. Наезд на колбу, мини-тряска на ударе.
s09 (12.75–14.75, хлёст): Дима крупнее пояса, сосредоточенно зажмурен; две белые мысли засасывает в серую тучу, которая
    вкатывается слева с пружинным отскоком; на «получается» (12.84) молния бьёт в пол рядом, вспышка, дымок; Дима распахивает один
    глаз; на «расстроился» (13.74) сползает, плечи вниз, губа дрожит, из тучи на макушку капают крупные капли. Наезд с разгоном.
s16 (26.55–28.3): мини-мысли выскакивают из-за краёв кадра как кроты: суп справа, утюг слева, мобильник сверху; Дима с закрытыми
    глазами спокойно отталкивает их ладонью («сколько» 26.62 — суп, «раз» 27.18 — утюг и мобильник обеими руками), они улетают с
    пружиной; грозовое облачко снизу справа на «убежал» (27.57) отращивает ножки и удирает за край, Дима машет вслед; из-за спины
    Димы выглядывает кот. Камера подёргивается за каждой мыслью, затем откат.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Люди и предметы — common/ (people, props)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props  # noqa: E402
from lib import band, blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, fill_d, line, mix, rect_pts, shape, svg  # noqa: E402

INK = lib.INK


def lerp(a, b, u):
    return a + (b - a) * u


def bump(t, t0, dur):
    if t < t0:
        return 0.0
    return math.exp(-(t - t0) / dur * 3.0)


def wob(t, t0, amp, freq=3.2, damp=4.0):
    if t < t0:
        return 0.0
    u = t - t0
    return amp * math.exp(-u * damp) * math.sin(2 * math.pi * freq * u)


def whip_in(t, t0, dur=.16):
    """Хлёст на входе плана: (dx, размытие) — кадр влетает сбоку и тормозит."""
    u = clamp((t - t0) / dur)
    e = 1 - (1 - u) ** 3
    return 260 * (1 - e), 18 * (1 - e)


def frame_svg(body, cx, cy, s, rot, blur_x=0.0, bg="#2a2220"):
    cam = lib.cam(cx, cy, s, rot)
    g = f'<g transform="{cam}">{body}</g>'
    if blur_x > .5:
        fid = lib.uid("wb")
        lib.DEFS.append(f'<filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="{blur_x:.1f} 0"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/>' + g)


SLEEVE = ("#d4a23e", "#a97b25", "#8c6219")


def sleeve_arm(elbow, wrist, k, seed=0):
    """Рукав горчичного худи от локтя к запястью: не толще предплечья, у запястья манжета."""
    E, Wr = np.array(elbow, float), np.array(wrist, float)
    d = Wr - E
    L = np.linalg.norm(d)
    d /= L
    n = np.array([-d[1], d[0]])
    cuff0 = Wr - d * 34 * k
    mid = (E + cuff0) / 2 + n * 6 * k
    pts = [tuple(E), tuple(mid), tuple(cuff0)]
    o = []
    sl = band(pts, 104 * k, 92 * k, step=5, cap=False)
    inner = f'<path d="{fill_d(band([tuple(p + n * 22 * k) for p in map(np.array, pts)], 40 * k, 32 * k, step=6, cap=False))}" fill="{SLEEVE[1]}"/>'
    for j in range(3):
        q = E + (cuff0 - E) * (.3 + .2 * j)
        inner += line([tuple(q - n * 32 * k + d * 6 * k), tuple(q + d * 18 * k), tuple(q + n * 18 * k + d * 10 * k)], 4 * k, SLEEVE[2], taper=.5, wmin=.3,
                      seed=seed + j)
    o.append(shape(sl, SLEEVE[0], inner, w=4.4, seed=seed + 5))
    cf = band([tuple(cuff0 - d * 2 * k), tuple(Wr + d * 6 * k)], 96 * k, 88 * k, step=4, cap=False)
    cin = "".join(line([tuple(cuff0 + d * (6 + 9 * j) * k - n * 44 * k), tuple(cuff0 + d * (6 + 9 * j) * k + n * 44 * k)], 2.4 * k, SLEEVE[1], taper=.2,
                       wmin=.6, seed=seed + 10 + j) for j in range(4))
    o.append(shape(cf, mix(SLEEVE[0], "#ffffff", .06), cin, w=4.0, seed=seed + 9))
    return "".join(o)


def floor_planks(y0, y1, x0=-600, x1=1700, col="#9A6B45", seam="#7E5535", hi="#A97A52", vx=540.0, vy=-900.0, seed=0):
    """Деревянный пол в лёгкой перспективе: доски сходятся к точке (vx, vy)."""
    o = [blob(rect_pts(x0, y0, x1, y1), col)]
    for i in range(-14, 16):
        xb = 540 + i * 150
        xt = vx + (xb - vx) * (y0 - vy) / (y1 - vy)
        o.append(line([(xt, y0), (xb, y1)], 3.2, seam, taper=.1, wmin=.8, seed=300 + seed + i))
    rs = np.random.RandomState(seed)
    for j in range(10):
        yy = y0 + (y1 - y0) * (j + 1) / 11 + rs.uniform(-12, 12)
        xx = rs.uniform(-200, 1300)
        o.append(line([(xx, yy), (xx + rs.uniform(60, 140), yy + rs.uniform(-2, 2))], 3, hi, taper=.5, wmin=.3, seed=340 + seed + j))
    return "".join(o)


# ═══════════════════════════════ s02: песочные часы ═══════════════════════════════
HG = np.array([600.0, 880.0])     # центр часов в покое
HGK = 2.8                         # масштаб часов (высота 252·k ≈ 580)
HG_BOT = HG[1] + 126 * HGK        # дно рамы на полу
T_FLIP0, T_LAND = 1.33, 1.51      # переворот: рывок вверх и через ребро, удар об пол на «десять»
T_FLOW = 1.83                     # «минут»: песок сорвался


def s02_bg(t):
    o = [blob(rect_pts(-600, -600, 1700, 640), "#B9917A")]
    o.append(line([(-600, 640), (1700, 640)], 6, "#8C6A55", taper=0, wmin=1, seed=21))
    o.append(floor_planks(640, 1900, seed=2))
    # размытый задний план: подушка и колено Димы в лотосе (джинсы, носок)
    bg = props.cushion(150, 900, 1.25, 1.0)
    knee = shape(ellipse_pts(250, 560, 260, 120, 18, rot=-12), "#3d4c6e", blob(ellipse_pts(290, 610, 220, 70, 14, rot=-12), "#2c3854"), w=5, seed=22)
    shin = shape([(-120, 700), (40, 610), (300, 640), (330, 720), (120, 790), (-120, 800)], "#34425f", "", w=5, seed=23)
    sock = shape(ellipse_pts(330, 690, 110, 56, 16, rot=10), "#e7e1d6", blob(ellipse_pts(350, 715, 90, 30, 12, rot=10), "#c9c1b2"), w=5, seed=24)
    o.append(f'<g {lib.blur(9)}>{bg}{shin}{knee}{sock}</g>')
    return "".join(o)


def s02_state(t):
    """Положение и вид часов: (центр, верт. масштаб переворота, sx, sy удара, доля песка сверху, струя)."""
    c = np.array(HG)
    flip = 1.0
    top = 0.0
    lift = 0.0
    if t < T_FLIP0:   # рука приподнимает часы, замах (с первого кадра — уже в движении)
        a = clamp((t - 1.15) / (T_FLIP0 - 1.15))
        lift = -40 * ease_out(a) - 8 * math.sin(t * 30)
    elif t < T_LAND:
        u = (t - T_FLIP0) / (T_LAND - T_FLIP0)
        flip = math.cos(math.pi * ease_io(u))
        lift = -40 - 120 * math.sin(math.pi * u) + 40 * ease_in(u, 3)
        top = 0.0 if flip > 0 else 1.0
    else:
        top = 1.0
        lift = props.hop(t, T_LAND + .02, 34, .2)
    flow = 0.0
    if t >= T_FLOW:
        flow = ease_out(clamp((t - T_FLOW) / .1))
        top = 1.0 - .2 * (t - T_FLOW)
    sx, sy = props.squash(t, T_LAND, .24, 3.2, 7.5)
    if t > T_LAND + .02:
        s2x, s2y = props.squash(t, T_LAND + .22, .12, 3.4, 8)
        if t > T_LAND + .22:
            sx, sy = sx * s2x, sy * s2y
    c[1] += lift
    return c, flip, sx, sy, top, flow


def s02_hand(t, c, flip):
    """Рука Димы: хват за талию часов справа (ладонь и большой палец за рамой, пальцы поверх), после удара — уходит вправо."""
    k = 1.9
    R = 84 * HGK
    away = ease_in(clamp((t - (T_LAND + .05)) / .22), 2) * 760
    up = ease_in(clamp((t - (T_LAND + .05)) / .22), 2) * 120
    C = np.array([c[0] + away, c[1] + 4 - up])
    if away > 600:
        return "", ""
    back, front = people.grip_svg("dima", tuple(C), R, 1, k=k, h=118, seed=930)
    wr = (C[0] + R + 92 * k * .9, C[1] + 6)
    arm = sleeve_arm((wr[0] + 480, wr[1] + 330), wr, 1.3, seed=60)
    # во время переворота кисть поворачивается вместе с часами: пальцы сжимаются по вертикали
    if t < T_LAND and T_FLIP0 <= t:
        fs = max(.55, abs(flip))
        back = f'<g transform="translate({C[0]:.1f} {C[1]:.1f}) scale(1 {fs:.3f}) translate({-C[0]:.1f} {-C[1]:.1f})">{back}</g>'
        front = f'<g transform="translate({C[0]:.1f} {C[1]:.1f}) scale(1 {fs:.3f}) translate({-C[0]:.1f} {-C[1]:.1f})">{front}</g>'
    return arm + back, front


def frame02(t):
    lib.dyn_begin()
    c, flip, sx, sy, top, flow = s02_state(t)
    o = [s02_bg(t)]
    # тень часов на полу: шире при ударе, меньше, когда часы в воздухе
    lift = HG[1] - c[1]
    sh_w = 230 * (1 - min(lift, 160) / 400) * sx
    o.append(blob(ellipse_pts(HG[0] + 10, HG_BOT + 6, sh_w, 26, 20), "#7A5234"))
    back, front = s02_hand(t, c, flip)
    o.append(back)
    hg = props.hourglass(0, 0, HGK, 0, flow, top, t, seed=1)
    bot = 126 * HGK
    g = (f'<g transform="translate({c[0]:.1f} {c[1] + bot:.1f}) scale({sx:.4f} {sy:.4f}) translate(0 {-bot:.1f}) '
         f'scale(1 {max(abs(flip), .04):.4f})">{hg}</g>')
    o.append(g)
    o.append(front)
    # удар: штрихи у дна и пылинки
    o.append(props.clink(HG[0] - 220, HG_BOT - 30, 1.6, clamp((t - T_LAND) / .32), 2, "#F4E3C0"))
    o.append(props.clink(HG[0] + 230, HG_BOT - 30, 1.6, clamp((t - T_LAND - .03) / .32), 3, "#F4E3C0"))
    body = "".join(o)
    # камера: хлёст, затем наезд на верхнюю колбу (песок сорвался), мини-тряска на ударе
    u = ease_io(clamp((t - 1.4) / 1.5))
    s = 1.22 + .42 * u + .06 * bump(t, T_LAND, .3)
    cx, cy = lerp(690, 610, u), lerp(900, 770, u)
    dx, dy = props.shake(t, T_LAND, 16, .38, 3)
    wx, bl = whip_in(t, 1.4)
    return frame_svg(body, cx + dx - wx / s, cy + dy, s, .6 * math.sin(t * 2.3), bl)


# ═══════════════════════════════ s09: туча и молния ═══════════════════════════════
DX9, DY9, DS9 = 360.0, 1560.0, 1.12        # таз Димы, масштаб
T_BOLT, T_SAD = 12.84, 13.74
STORM_X, STORM_Y = 470.0, 745.0            # дно тучи в покое


def s09_storm(t):
    a = t - 12.55
    xs = lerp(-700, STORM_X, clamp(lib.spring(a / .36 * .7, 1.6, 5.5), -0.2, 1.3)) if a < 1.5 else STORM_X
    sx, sy = props.squash(t, 12.74, .16, 2.8, 6.0)
    rot = 6 * math.exp(-max(a, 0) * 3) * math.sin(a * 9) + 1.2 * math.sin(t * 1.7)
    bob = 8 * math.sin(t * 2.1) + 95 * ease_io(clamp((t - T_SAD) / .6))   # туча опускается вслед за сползающим Димой
    return xs + 90 * ease_io(clamp((t - T_SAD) / .6)), STORM_Y + bob, sx, sy, rot


def s09_dima(t):
    sad = ease_io(clamp((t - T_SAD) / .45))
    kw_a = people.lotus_kw("sit", DX9, DY9, DS9)
    y = DY9 + 70 * sad + 8 * props.hop(t, T_BOLT, 3, .25)
    kw_b = people.lotus_kw("slump", DX9, y, DS9, sag=.6)
    kw_a = people.lotus_kw("sit", DX9, y, DS9, sag=.6 * sad)
    arms = {}
    for k in ("f", "n"):
        pa, pb = kw_a["arms"][k], kw_b["arms"][k]
        arms[k] = ("ik", tuple(lerp(np.array(pa[1]), np.array(pb[1]), sad)), pb[2])
    hands = kw_b["hands"] if sad > .5 else kw_a["hands"]
    lean = lerp(kw_a["lean"], kw_b["lean"], sad) + wob(t, T_BOLT, .05, 4, 5)
    ha = lerp(kw_a["head_ang"], kw_b["head_ang"], sad) - .5 * wob(t, T_BOLT, .12, 3.6, 4.5)
    if t < T_BOLT:
        expr = dict(people.EXPR["dima"]["squeeze"])
    elif t < T_SAD:
        expr = dict(people.EXPR["dima"]["one_eye"])
        expr["hair"] = 14 * math.exp(-(t - T_BOLT) * 4) * math.sin((t - T_BOLT) * 40)
    else:
        expr = dict(people.EXPR["dima"]["upset"])
        expr["trem"] = t
        expr["lid"] = lerp(.7, .4, sad)
    lot = dict(kw_a["lotus"])
    lot["sag"] = .6 * sad
    r = people.figure("dima", DX9, y, DS9, expr, lean=lean, head_ang=ha, arms=arms, hands=hands, lotus=lot)
    return r


def frame09(t):
    lib.dyn_begin()
    o = [blob(rect_pts(-800, -800, 1900, 1290), "#8F8494")]
    for i in range(7):   # обои: тусклые полосы
        o.append(line([(-300 + 220 * i, -800), (-300 + 220 * i, 1280)], 5, "#857A8B", taper=.1, wmin=.8, seed=90 + i))
    o.append(floor_planks(1290, 2400, col="#7E5A44", seam="#634433", hi="#8C6650", seed=9))
    o.append(props.cushion(DX9 + 20, DY9 + 210, 1.6, .8))
    xs, ys, sx, sy, rot = s09_storm(t)
    fl = 0.0
    if t >= T_BOLT:
        fl = math.exp(-(t - T_BOLT) * 7) * (1 if (t - T_BOLT) < .06 or (t - T_BOLT) > .12 else .3)
    # две белые мысли (обед, утюг) затягивает в тучу
    for j, (x0, y0, w, h, inner_fn) in enumerate(((230, 560, 200, 140, "soup"), (720, 520, 190, 130, "iron"))):
        uu = clamp((t - 12.62 - .05 * j) / .3)
        s_ = props.unpop(t, 12.80 + .06 * j, .16)
        if s_ <= 0:
            continue
        px, py = lerp(x0, xs, ease_in(uu, 2)), lerp(y0, ys - 120, ease_in(uu, 2))
        inner = props.plate_soup(0, 50, .55, 0, t) if inner_fn == "soup" else props.iron(0, 40, .55, 0, 0, t)
        o.append(props.cloud(px, py, w, h, s_ * (1 - .3 * uu), s_ * (1 - .45 * uu), 30 + j, inner=inner))
    o.append(f'<g transform="rotate({rot:.2f} {xs:.1f} {ys:.1f})">{props.storm(xs, ys, 660, 270, sx, sy, 2, flash=fl)}</g>')
    # молния в пол справа от Димы, на полу — подпалина и дымок
    o.append(props.bolt(xs + 170, ys - 30, 790, 1310, (t - T_BOLT + .02) / .5, 52, seed=3, n=6))
    if t >= T_BOLT + .05:
        sc = clamp((t - T_BOLT) / .1)
        o.append(blob(ellipse_pts(790, 1312, 60 * sc, 16 * sc, 16), "#3a2a22"))
        o.append(props.smoke_curls(790, 1304, 1.0, clamp((t - T_BOLT - .08) / .4), t, seed=4, col="#B9BCC4"))
    r = s09_dima(t)
    o.append(r["svg"])
    # капли на макушку
    hx, hy = r["head"]
    o.append(props.rain(hx - 10, ys + 10, 150, t, T_SAD + .04, 4, 7, 1.5, floor=hy - 150 * DS9 * .95, every=.13))
    if t >= T_BOLT:
        o.append(props.flash_screen(.55 * math.exp(-(t - T_BOLT) * 10)))
    body = "".join(o)
    a = clamp((t - 12.75) / 2.0)
    sad = ease_io(clamp((t - T_SAD) / .6))
    s = 1.4 + .2 * ease_in(a, 2.2) + .05 * bump(t, T_BOLT, .25)
    cx, cy = lerp(470, 540, sad), lerp(1070, 1085, sad)
    dx, dy = props.shake(t, T_BOLT, 26, .5, 5)
    dx2, dy2 = props.shake(t, T_SAD, 8, .3, 6)
    wx, bl = whip_in(t, 12.75)
    return frame_svg(body, cx + dx + dx2 - wx / s, cy + dy + dy2, s, -.8 * a + .4 * math.sin(t * 2), bl)


# ═══════════════════════════════ s16: мысли-кроты ═══════════════════════════════
DX16, DY16, DS16 = 400.0, 1230.0, 1.0


def mole(t, t_pop, home, start, push_t=None, push_dir=(1, 0), seed=0, w=240, h=170, inner=""):
    """Мини-мысль: выскакивает из-за края (start → home) пружиной; от толчка в push_t улетает с отскоком и вращением."""
    if t < t_pop - .02:
        return ""
    u = t - t_pop
    p = np.array(start, float) + (np.array(home, float) - np.array(start, float)) * clamp(lib.spring(u, 1.9, 6.5), -.2, 1.25)
    sx, sy = props.pop(t, t_pop, amp=.3)
    sx, sy = max(sx, .25), max(sy, .25)     # из норки выезжает уже видимой
    rot = 4 * math.sin(t * 5 + seed)
    if push_t is not None and t >= push_t:
        v = t - push_t
        dv = np.array(push_dir, float)
        p = p + dv * (1400 * v + 900 * v * v)
        qx, qy = props.squash(t, push_t, .35, 3.5, 6)
        sx, sy = sx * qy, sy * qx      # сплющило вдоль толчка
        rot += 260 * v * (1 if dv[0] >= 0 else -1)
    # «дрожит от нетерпения» до толчка
    if push_t is None or t < push_t:
        p = p + np.array([3 * math.sin(t * 37 + seed), 2 * math.sin(t * 29 + seed)])
    c = props.cloud(0, 0, w, h, sx, sy, 60 + seed, inner=inner)
    return f'<g transform="translate({p[0]:.1f} {p[1]:.1f}) rotate({rot:.2f})">{c}</g>'


def s16_dima(t):
    """Дима в лотосе: сначала колечки на коленях; ближней ладонью толкает суп (26.62), обеими — утюг и мобильник (27.18), потом машет."""
    sc = DS16 * people.HEIGHT["dima"]
    x, y = DX16, DY16
    kw = people.lotus_kw("sit", x, y, DS16)
    arms = dict(kw["arms"])
    hands = {k: dict(v) for k, v in kw["hands"].items()}
    open_n = {"dir": (.15, -1), "spread": .35, "curl": (0, .02, .05, .1), "thumb": .1}
    open_f = {"dir": (-.2, -1), "spread": .35, "curl": (0, .02, .05, .1), "thumb": .1}

    def blend(rest, tgt, e):
        return ("ik", tuple(lerp(np.array(rest[1]), np.array(tgt), e)), rest[2])
    # ближняя рука: толчок супа вправо (26.50–26.62–26.85), толчок мобильника вверх (27.06–27.18–27.4), маханье с 27.62
    e1 = ease_out(clamp((t - 26.48) / .14)) * (1 - ease_io(clamp((t - 26.72) / .2)))
    e2 = ease_out(clamp((t - 27.04) / .14)) * (1 - ease_io(clamp((t - 27.32) / .22)))
    ew = ease_out(clamp((t - 27.58) / .16))
    if e1 > 0.01:
        arms["n"] = blend(kw["arms"]["n"], (x + 420 * sc, y - 430 * sc), e1)
        hands["n"] = open_n if e1 > .25 else hands["n"]
    elif e2 > 0.01:
        arms["n"] = blend(kw["arms"]["n"], (x + 240 * sc, y - 690 * sc), e2)
        hands["n"] = dict(open_n, dir=(.05, -1)) if e2 > .25 else hands["n"]
    elif ew > 0.01:
        a = math.sin(2 * math.pi * 2.6 * (t - 27.58))
        arms["n"] = blend(kw["arms"]["n"], (x + (330 + 50 * a) * sc, y - 640 * sc), ew)
        hands["n"] = {"dir": (.35 * a, -1), "spread": .35, "curl": (0, 0, .05, .1), "thumb": .05} if ew > .25 else hands["n"]
    # дальняя рука: толчок утюга влево (27.04–27.18–27.4)
    ef = ease_out(clamp((t - 27.04) / .14)) * (1 - ease_io(clamp((t - 27.32) / .22)))
    if ef > 0.01:
        arms["f"] = blend(kw["arms"]["f"], (x - 250 * sc, y - 500 * sc), ef)
        hands["f"] = open_f if ef > .25 else hands["f"]
    if t < 27.58:
        expr = dict(people.EXPR["dima"]["soft"])
    else:
        expr = dict(people.EXPR["dima"]["side_smile"])
    lean = .03 * math.sin(t * 2.2) - .04 * e1 + .02 * ef
    ha = .04 * math.sin(t * 1.7) + .06 * e2 - .05 * ew
    lot = dict(kw["lotus"])
    return people.figure("dima", x, y + 3 * math.sin(t * 2.4), DS16, expr, lean=lean, head_ang=ha, arms=arms, hands=hands, lotus=lot)


def runaway(t, t_pop=27.30, t_run=27.57):
    """Грозовое облачко: выскакивает снизу справа, на «убежал» отращивает ножки и удирает вправо, подпрыгивая."""
    if t < t_pop - .02:
        return ""
    u = t - t_pop
    home, start = np.array([905.0, 1100.0]), np.array([1300.0, 1150.0])
    p = start + (home - start) * clamp(lib.spring(u, 1.9, 6.5), -.2, 1.25)
    sx, sy = props.pop(t, t_pop, amp=.3)
    sx, sy = max(sx, .25), max(sy, .25)
    legs = ""
    leg_k = 0.0
    if t >= t_run:
        v = t - t_run
        leg_k = clamp(lib.spring(v, 2.4, 6.0) * 1.0, 0, 1.3)
        run = ease_in(clamp((v - .22) / .5), 2)
        p = p + np.array([620 * run, -130 * leg_k + 30 * abs(math.sin(v * 22)) * run])
        legs = props.legs_run(0, 0, 1.5 * leg_k, t * (1 + 2 * run), seed=5)
    c = props.storm(0, 0, 290, 175, sx, sy, 11)
    eyes = ""
    if sx > .6:   # у тучки — два хитрых глазика-точки (не буквы)
        for ex in (-30, 24):
            eyes += blob(ellipse_pts(ex * 1.15, -82, 8, 10, 10), "#1c1622")
    rot = 3 * math.sin(t * 9)
    return f'<g transform="translate({p[0]:.1f} {p[1]:.1f}) rotate({rot:.2f})">{legs}{c}{eyes}</g>'


def frame16(t):
    lib.dyn_begin()
    o = [blob(rect_pts(-600, -600, 1700, 1200), "#EAD6B4")]
    # утренний свет: чёткая полоса формы окна на стене и на полу
    win = [(600, 170), (960, 140), (960, 600), (600, 640)]
    o.append(blob(win, "#F6EAD2"))
    o.append(line([(780, 155), (780, 620)], 16, "#EAD6B4", taper=0, wmin=1, seed=161))
    o.append(line([(600, 405), (960, 370)], 16, "#EAD6B4", taper=0, wmin=1, seed=162))
    o.append(floor_planks(1200, 2200, col="#C08E62", seam="#A3754C", hi="#CC9C70", seed=16))
    o.append(blob([(-200, 1240), (300, 1230), (520, 1420), (-120, 1440)], "#D3A273"))
    # кот выглядывает из-за спины Димы (снизу, слева)
    if t >= 27.62:
        a = t - 27.62
        rise = clamp(lib.spring(a, 1.6, 6), 0, 1.2)
        cy = 1392 - 20 * math.sin(math.pi * clamp(a / .3))
        st = {"turn": .9, "look": (.8, -.1), "blink": .35 + .1 * math.sin(t * 2), "perk": .3, "tilt": -10 * rise + 4, "tail": 3 * math.sin(t * 2)}
        o.append(people.cat_svg(lerp(520, 740, rise), cy, .74, st, t))
    o.append(props.cushion(DX16 + 10, DY16 + 205, 1.12, .85))
    # мысли-кроты за Димой и перед ним
    o.append(mole(t, 26.38, (935, 800), (1330, 770), 26.62, (1, -.15), seed=1, w=260, h=185, inner=props.plate_soup(0, 56, .62, 1, t)))
    o.append(mole(t, 26.80, (135, 650), (-260, 680), 27.18, (-1, -.1), seed=2, w=250, h=175, inner=props.iron(0, 48, .66, 0, .7, t)))
    o.append(mole(t, 26.96, (660, 430), (660, -180), 27.18, (.25, -1), seed=3, w=230, h=170, inner=props.mobilnik(0, 0, .8, 12)))
    r = s16_dima(t)
    o.append(r["svg"])
    o.append(runaway(t))
    # штрихи «шлёп» на толчках
    for tp, (px, py) in ((26.62, (820, 760)), (27.18, (150, 600)), (27.18, (650, 420))):
        o.append(props.clink(px, py, 1.3, clamp((t - tp) / .3), int(px), "#FFFFFF"))
    body = "".join(o)
    # камера подёргивается к каждой мысли, затем откат
    cx, cy, s = 540.0, 930.0, 1.16
    for tp, (px, py), amp in ((26.40, (935, 700), 1), (26.82, (135, 560), 1), (26.98, (660, 330), .8), (27.32, (900, 1030), .9)):
        b = bump(t, tp, .45) * amp
        cx += (px - 540) * .07 * b
        cy += (py - 930) * .07 * b
        s += .035 * b
    back = ease_io(clamp((t - 27.62) / .7))
    s -= .08 * back
    cy += 30 * back
    dx, dy = props.shake(t, 26.62, 7, .25, 1)
    dx2, dy2 = props.shake(t, 27.18, 9, .28, 2)
    return frame_svg(body, cx + dx + dx2, cy + dy + dy2, s, .5 * math.sin(t * 1.6))


def frame(sid, t):
    if sid == "s02":
        return frame02(t)
    if sid == "s09":
        return frame09(t)
    if sid == "s16":
        return frame16(t)
    raise KeyError(sid)
