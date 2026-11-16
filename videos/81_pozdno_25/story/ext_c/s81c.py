"""Рилс 81 «Всё, поздно», группа C — хук, поворот, Америка, петля: s01, s02, s03, s04, s09, s18.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Всё время — из shots.json (t0/t1) и voice/words.json (слова по индексу wN),
секунды в коде — только длительности движений. Места — common/room.py (раздел 81), Дима и люди — common/people.py (…81), кот —
common/cat.py через people, предметы — common/props.py, надпись хука — common/hand_text.py.
Букв и цифр нет, кроме «Поздно?» (s01–s03). NOCAM=1 — без камеры и без надписи (замер движения рисунка);
MASK=1 — только силуэт рисунка хука (часы с цепями, Дима, песок) белым на чёрном, с камерой (замер заполнения)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people as PE  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from hand_text import hand_text, text_width  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, rect_pts, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
HOOK_TEXT = json.load(open(os.path.join(STORY, "reel.json"))).get("hook_screen", "Поздно?")
NOCAM = bool(os.environ.get("NOCAM"))
MASK = bool(os.environ.get("MASK"))
SAND, SAND_SH, SAND_HI = PR.C_SAND, PR.C_SAND_SH, "#F4D78E"


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def stress(i, u):
    """Момент ударного слога: доля u длины слова i."""
    return W(i) + (WE(i) - W(i)) * u


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def lerp(a, b, u):
    return a + (b - a) * u


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def damp(t, t0, amp, freq=3.0, dmp=6.0):
    u = t - t0
    if u <= 0:
        return 0.0
    return amp * math.exp(-dmp * u) * math.sin(2 * math.pi * freq * u)


def kick(t, t0, rise=.08, dmp=5.0):
    """Импульс 0→1 за rise и затухание."""
    u = t - t0
    if u <= 0:
        return 0.0
    return (u / rise) if u < rise else math.exp(-dmp * (u - rise))


def shake2(t, t0, amp, k=9.0, fr=19.0):
    def dec(tt):
        if tt < 0:
            return 0.0
        return math.exp(-k * tt) * math.sin(2 * math.pi * fr * tt)
    return amp * dec(t - t0), amp * .7 * dec(t - t0 - .013)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


MASK_F = '<filter id="mk81"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def wrap(world, cx, cy, s, rot=0.0, over="", mask_world=None):
    """Мир в камере + экранный слой over (надпись — вне камеры). MASK: только mask_world белым на чёрном."""
    set_ink(s)
    if NOCAM:
        return lib.svg(f'<g transform="{lib.cam(540, 960, 1.0)}">{world}</g>')
    if MASK:
        lib.DEFS.append(MASK_F)
        return lib.svg('<rect width="1080" height="1920" fill="#000"/>'
                       f'<g transform="{lib.cam(cx, cy, s, rot)}"><g filter="url(#mk81)">{mask_world or ""}</g></g>')
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, rot)}">{world}</g>{over}')


def hook_cam(t, t_hit, t_hit2, rot0=3.7, side0=46.0, fly=.19, far=1.48, over=.066):
    """Влёт правил 28/29 (не слабее эталона 17): масштаб 1/far → 1 за fly с без разгона, перелёт over с отскоком, поворот rot0 с
    возвратом, боковой занос; удар +4 % на t_hit и +10 % на t_hit2. -> (множитель масштаба, поворот, занос, доля полёта 0…1)."""
    u = clamp(t / fly)
    e = ease_out(u, 3)
    s = 1 / far + (1 - 1 / far) * e
    if t > fly:
        s += over * math.exp(-7 * (t - fly)) * math.cos(2 * math.pi * 2.2 * (t - fly))
    rot = rot0 * (1 - e) + damp(t, fly, -1.3, 2.0, 6.0)
    side = side0 * (1 - e)
    hit = .04 * kick(t, t_hit, .03, 5.5) + .10 * kick(t, t_hit2, .03, 4.5)
    return s * (1 + hit), rot, side, 1 - e


def radial_blur(world, cx, cy, s, rot, amount):
    """Радиальное размытие влёта: несколько копий мира с чуть большим масштабом поверх, полупрозрачно."""
    if amount <= .02 or NOCAM or MASK:
        return ""
    o = []
    for dk, op in ((.035, .22), (.07, .14), (.11, .08)):
        o.append(f'<g opacity="{op * amount:.3f}" transform="{lib.cam(cx, cy, s * (1 + dk * amount), rot)}">{world}</g>')
    return "".join(o)


def strokes(cx, cy, r0, r1, a, n=8, w=7, col=INK, seed=0, a0=0.0, span=360.0):
    """Штрихи удара веером вокруг точки (a 0…1 — фаза удара)."""
    if a <= .01:
        return ""
    o = []
    for j in range(n):
        ang = math.radians(a0 + span * (j + .5) / n)
        ra, rb = r0 + (r1 - r0) * .2 * a, r0 + (r1 - r0) * a
        o.append(line([(cx + ra * math.cos(ang), cy + ra * math.sin(ang)), (cx + rb * math.cos(ang), cy + rb * math.sin(ang))], w, col, seed=seed + j,
                      op=min(1.0, 2 * a)))
    return "".join(o)


def rnd(i, j=0):
    """Детерминированное «случайное» 0…1 (без состояния)."""
    v = math.sin(i * 12.9898 + j * 78.233 + 4.1) * 43758.5453
    return v - math.floor(v)


# ═════════════════════════ надпись хука «Поздно?» (экранные координаты, s01–s03) ═════════════════════════
HOOK_SIZE = 1.9
HOOK_BASE = 378.0     # линия строки: буквы ≈ 190…385 (зона R.HV_TEXT), ширина 760 — поля по 160 px


def hook_title(t, t_end):
    """Пишется с 0.00 за 0.30 с маркером, целиком к 0.35; стоит до склейки поворота t_end (экранные координаты, камера не двигает)."""
    if t >= t_end or NOCAM or MASK:
        return ""
    w = text_width(HOOK_TEXT, HOOK_SIZE)
    x0 = (1080 - w) / 2 - 10
    sh = hand_text(HOOK_TEXT, t, 0.0, .30, x0 + 6, HOOK_BASE + 7, HOOK_SIZE, ink="#05081a", bold=1.9, op=.6)
    return sh + hand_text(HOOK_TEXT, t, 0.0, .30, x0, HOOK_BASE, HOOK_SIZE, ink="#f6eedc", bold=1.9)


# ═════════════════════════ часы над Димой: общее для s01–s03 и петли ═════════════════════════
GX, GY, GK = R.HV_GLASS                 # горлышко часов в покое и масштаб (крышки ≈ 442…958)
TOP_Y = GY - 280 * GK                   # верх верхней крышки (точка подвеса качания)
BOT_Y = GY + 280 * GK                   # низ нижней крышки (дырочка, откуда сыплется)
ANCH = ((-430.0, 410.0), (1460.0, 404.0))   # цепи уходят вбок за края кадра (ниже надписи)
DIMA_HIP = (455.0, 1740.0)
DIMA_K = 1.15


def rotp(p, c, a):
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)


def chain(p0, p1, t, seed=0, sag=0.0):
    """Цепь звеньями от p0 до p1 (звенья по направлению, чередуются плашмя и ребром)."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = int(L / 40)
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    o = []
    for i in range(n + 1):
        u = i / max(1, n)
        x = p0[0] + (p1[0] - p0[0]) * u
        y = p0[1] + (p1[1] - p0[1]) * u + sag * math.sin(math.pi * u)
        if i % 2 == 0:
            o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="27" ry="14" transform="rotate({ang:.1f} {x:.1f} {y:.1f})" fill="none" '
                     f'stroke="{INK}" stroke-width="11"/><ellipse cx="{x:.1f}" cy="{y:.1f}" rx="27" ry="14" transform="rotate({ang:.1f} {x:.1f} {y:.1f})" '
                     f'fill="none" stroke="{PR.C_CHAIN}" stroke-width="5"/>')
        else:
            o.append(f'<line x1="{x - 24 * math.cos(math.radians(ang)):.1f}" y1="{y - 24 * math.sin(math.radians(ang)):.1f}" '
                     f'x2="{x + 24 * math.cos(math.radians(ang)):.1f}" y2="{y + 24 * math.sin(math.radians(ang)):.1f}" stroke="{INK}" stroke-width="13" '
                     f'stroke-linecap="round"/><line x1="{x - 22 * math.cos(math.radians(ang)):.1f}" y1="{y - 22 * math.sin(math.radians(ang)):.1f}" '
                     f'x2="{x + 22 * math.cos(math.radians(ang)):.1f}" y2="{y + 22 * math.sin(math.radians(ang)):.1f}" stroke="{PR.C_CHAIN_SH}" '
                     f'stroke-width="6" stroke-linecap="round"/>')
    return "".join(o)


def hourglass(t, a, dy=0.0, sand_top=.1, sand_bot=.85, stream=1.0, burst=0.0, crack=0.0, flip=0.0, leak=True):
    """Часы, качнувшиеся на a° вокруг верхней крышки, сдвинутые на dy; цепи от углов крышки вбок. -> (svg, точка дырочки внизу)."""
    piv = (GX, TOP_Y + dy)
    body = PR.giant_hourglass(GX, GY + dy, GK, sand_top=sand_top, sand_bot=sand_bot, stream=stream, crack_u=crack, burst_u=burst, flip_u=flip, t=t,
                              seed=1, chain=0.0)
    hole = rotp((GX, BOT_Y + dy), piv, a)
    if leak and burst < .02:
        body += shape(ellipse_pts(GX, BOT_Y + dy - 4, 15, 7, 12), "#3a2a14", "", w=2.6, seed=8130)
    o = f'<g transform="rotate({a:.3f} {piv[0]:.1f} {piv[1]:.1f})">{body}</g>'
    ch = ""
    for side, an in zip((-1, 1), ANCH):
        p0 = rotp((GX + side * 200 * GK, TOP_Y + dy - 4), piv, a)
        ch += chain(p0, an, t, seed=8131 + side)
        ch += shape(ellipse_pts(p0[0], p0[1], 16, 16, 12), PR.C_CHAIN, "", w=3.2, seed=8133 + side)
    return ch + o, hole


def leak_stream(p0, p1, t, w=9.0, op=1.0):
    """Струйка песка из дырочки вниз до p1: живая, чуть вьётся, крупинки по краю."""
    if p1[1] <= p0[1] + 4 or w <= .3:
        return ""
    n = 10
    pts = [(p0[0] + (p1[0] - p0[0]) * i / n + 3.0 * math.sin(t * 41 + i * 1.7) * i / n, p0[1] + (p1[1] - p0[1]) * i / n) for i in range(n + 1)]
    o = line(pts, w, SAND, taper=0, wmin=1, seed=8140, op=op)
    o += line([(x - w * .25, y) for x, y in pts[:-1]], w * .35, SAND_HI, taper=0, wmin=1, seed=8141, op=.8 * op)
    for j in range(8):
        u = (t * 3.1 + j / 8) % 1
        x = lerp(p0[0], p1[0], u) + (rnd(j, 1) - .5) * w * 2.2
        y = lerp(p0[1], p1[1], u)
        o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2.6 + 1.6 * rnd(j, 2):.1f}" fill="{SAND}" stroke="{INK}" stroke-width="1.2" opacity="{op:.2f}"/>'
    return o


def splash(t, src, t0, t1, rate=40.0, v=(260, 620), up=(.55, 1.3), side=0.0, seed=0, life=1.4, g=2600.0, floor=2400.0, r=(4.5, 8.5)):
    """Песчинки отскакивают от точки src (или src(t_emit)) веером: вылет с rate штук в секунду на [t0, t1], параболы с гравитацией."""
    if rate <= .5:
        return ""
    o = []
    n0, n1 = int(math.floor(max(t0, t - life) * rate)), int(math.floor(min(t1, t) * rate))
    for i in range(n0, n1 + 1):
        te = i / rate + rnd(i, seed) / rate
        if te < t0 or te > min(t, t1):
            continue
        dt = t - te
        if dt < 0 or dt > life:
            continue
        sx, sy = src(te) if callable(src) else src
        ang = math.radians(-90 + (rnd(i, seed + 1) - .5) * 170 + side * 40)
        sp = lerp(v[0], v[1], rnd(i, seed + 2)) * lerp(up[0], up[1], rnd(i, seed + 3))
        x = sx + math.cos(ang) * sp * dt
        y = sy + math.sin(ang) * sp * dt + .5 * g * dt * dt
        if y > floor:
            continue
        rr = lerp(r[0], r[1], rnd(i, seed + 4))
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="{SAND if i % 3 else SAND_HI}" stroke="{INK}" stroke-width="1.4"/>')
    return "".join(o)


def drip(t, src, t0, t1, rate=30.0, spread=24.0, seed=0, g=2600.0, floor=2400.0, v0=60.0):
    """Песок сыплется вниз из src (сквозь пальцы): отвесно, с малым разбросом."""
    if rate <= .5:
        return ""
    o = []
    life = math.sqrt(2 * 1200 / g)
    n0, n1 = int(math.floor(max(t0, t - life) * rate)), int(math.floor(min(t1, t) * rate))
    for i in range(n0, n1 + 1):
        te = i / rate + rnd(i, seed) / rate
        if te < t0 or te > min(t, t1):
            continue
        dt = t - te
        sx, sy = src(te, i) if callable(src) else src
        x = sx + (rnd(i, seed + 1) - .5) * spread + (rnd(i, seed + 5) - .5) * 40 * dt
        y = sy + v0 * dt + .5 * g * dt * dt
        if y > floor:
            continue
        rr = 4 + 4 * rnd(i, seed + 2)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="{SAND if i % 3 else SAND_HI}" stroke="{INK}" stroke-width="1.3"/>')
    return "".join(o)


def dima_hook(t, expr, pose="d81_cup_up", pose2=None, u=1.0, jit=1.0, dx=0.0, dy=0.0, wr=None, lean=0.0, head=0.0):
    """Дима под часами: поза с дрожью (паника: руки ходят, корпус дёргается). wr — сдвиг запястий {'f': (dx, dy), 'n': ...}."""
    x, y = DIMA_HIP[0] + dx, DIMA_HIP[1] + dy
    sc = DIMA_K * PE.HEIGHT["dima"]
    pk = PE.mix_pose(pose, pose2, u, x, y, sc, "dima") if pose2 else PE.pose_kw(pose, x, y, sc, "dima")
    arms = {}
    for k_, a in pk["arms"].items():
        if a[0] == "ik":
            ph = 1.7 if k_ == "n" else 0.0
            ox = jit * (16 * math.sin(2 * math.pi * 3.3 * t + ph) + 7 * math.sin(2 * math.pi * 7.1 * t + 2 * ph))
            oy = jit * (13 * math.cos(2 * math.pi * 2.9 * t + ph) + 6 * math.sin(2 * math.pi * 6.3 * t + ph))
            if wr and k_ in wr:
                ox += wr[k_][0]
                oy += wr[k_][1]
            arms[k_] = ("ik", (a[1][0] + ox, a[1][1] + oy), a[2])
        else:
            arms[k_] = a
    ex = dict(PE.EXPR["dima"][expr]) if isinstance(expr, str) else dict(expr)
    ex["hair"] = ex.get("hair", 0) + 5 * jit * math.sin(t * 23)
    la = lean + jit * .025 * math.sin(2 * math.pi * 4.3 * t)
    ha = head + jit * .05 * math.sin(2 * math.pi * 3.7 * t + .6)
    return PE.dima81(x, y, DIMA_K, ex, pose, t=t, arms=arms, lean_add=la, head_add=ha) if not pose2 else \
        PE.dima81(x, y, DIMA_K, ex, (pose, pose2), t=t, u=u, arms=arms, lean_add=la, head_add=ha)


def crown(fig):
    """Макушка Димы (куда падает песок)."""
    hx, hy = fig["head"]
    s_ = fig["scale"]
    return (hx - 6 * s_, hy - 128 * s_)


def void_world(t, d, items, shadow_items, sh_dx=70.0, sh_dy=34.0):
    """Пустота: задник → тень предметов на заднике → пол → предметы → свет → виньетка."""
    sh = R.cast_shadow(shadow_items, sh_dx, sh_dy, 1.1, d["P"]["shadow"], .42, 5.0, cx=540, cy=700)
    return d["bg"] + sh + d["floor"] + items + d["light"] + d["shade"]


# ═════════════════════════ s01: хук — песок на макушку, паника ═════════════════════════
def s01_state(t):
    h1, h2 = stress(1, .22), stress(2, .35)          # «ДВАдцать», «ПЯТЬ»
    sway = 2.6 * math.sin(2 * math.pi * 1.45 * t + .9) + damp(t, h1, 3.4, 2.3, 4.0) + damp(t, h2, -2.0, 2.6, 5.0)
    dy = -14 * kick(t, h1 - .01, .03, 9) + 8 * kick(t, h1 + .05, .06, 6)
    # кадр 0 — уже в движении: часы только что дёрнулись на цепи (отскок вниз-вверх), Дима вскидывает руки
    dy += 46 * math.exp(-5 * t) * math.cos(2 * math.pi * 2.4 * t)
    sway += 6.0 * math.exp(-3.5 * t) * math.sin(2 * math.pi * 1.9 * t + .3)
    throw = 1 - ease_out(clamp(t / .32), 2)
    return dict(h1=h1, h2=h2, sway=sway, dy=dy, throw=throw)


def s01_world(t):
    st = s01_state(t)
    h1, h2 = st["h1"], st["h2"]
    d = R.hook_void(t)
    top = lerp(.14, .07, clamp(t / 1.4))
    hg, hole = hourglass(t, st["sway"], st["dy"], sand_top=top, sand_bot=.84, stream=1.0)
    flinch = kick(t, h1, .05, 6) + 1.3 * kick(t, h2, .05, 6)
    th = st["throw"]
    fig = dima_hook(t, "panic81", jit=1.0 + .6 * flinch, dy=14 * flinch + 26 * th, lean=-.03 * flinch + .08 * th, head=.12 * th,
                    wr={"f": (-10 * flinch - 60 * th, 30 * flinch + 230 * th), "n": (10 * flinch - 30 * th, 24 * flinch + 260 * th)})
    cr = crown(fig)
    sw = 9 + 9 * kick(t, h1, .04, 4)
    stream = leak_stream(hole, cr, t, sw)
    sand = splash(t, cr, -1.0, 9.0, rate=38 + 50 * kick(t, h1, .05, 3), seed=1, side=.2)
    sand += splash(t, cr, h2, h2 + .09, rate=320, v=(380, 900), up=(.7, 1.3), seed=7, r=(5, 10))
    ph = fig.get("palm", fig["wrist"]["n"])
    sand += drip(t, ph, -1.0, 9.0, rate=22, spread=60, seed=3)
    eff = strokes(cr[0], cr[1] - 10, 70, 150, bump(t, h2 - .01, .3), n=9, w=7, col="#f6eedc", seed=8150, a0=-170, span=160)
    eff += strokes(GX, GY - 120, 260, 340, bump(t, h1 - .01, .28), n=6, w=6, col="#d8e6ff", seed=8160, a0=-180, span=180)
    items = hg + fig["svg"] + stream + sand + eff
    world = void_world(t, d, items, hg + fig["svg"], sh_dx=70 + 6 * st["sway"])
    mask = hg + fig["svg"] + stream + sand
    return world, mask, st


def s01(t):
    lib.dyn_begin()
    world, mask, st = s01_world(t)
    kk, rc, side, fl = hook_cam(t, st["h1"], st["h2"])
    sx1, sy1 = shake2(t, st["h1"], 7)
    sx2, sy2 = shake2(t, st["h2"], 13)
    cx0, cy0, s0 = R.CAM81_HOOK
    cx = cx0 + side - sx1 - sx2 + 3 * math.sin(t * 2.3)
    cy = cy0 - sy1 - sy2
    s = s0 * kk * (1 + .015 * sm(t, .4, 1.5))
    blur = radial_blur(world, cx, cy, s, rc, fl)
    return wrap(world, cx, cy, s, rc, blur + hook_title(t, T1("s03")), mask)


# ═════════════════════════ s02: ладони под струёй, сквозь пальцы, колба пустеет ═════════════════════════
def s02(t):
    lib.dyn_begin()
    a4, a5, a7 = stress(4, .3), stress(5, .35), stress(7, .45)     # «ты», «НИчего», «доБИЛся»
    d = R.hook_void(t)
    sway = 1.8 * math.sin(2 * math.pi * 1.2 * t + .4) + damp(t, a7, 1.6, 2.4, 5)
    top = lerp(.07, 0.0, sm(t, a5, a7))
    hg, hole = hourglass(t, sway, 0.0, sand_top=top, sand_bot=.88, stream=1.0 - sm(t, a7 - .05, a7 + .05))
    # ладони: на «ты» лодочкой прямо под струю (над макушкой), на «ничего» пальцы разжимаются — песок сквозь пальцы
    reach = sm(t, a4 - .12, a4 + .14)
    fig = dima_hook(t, "panic81", jit=.55, dy=-20 * reach, wr={"f": (-170 * reach, -40 * reach), "n": (-200 * reach, -20 * reach)})
    ph = fig.get("palm", fig["wrist"]["n"])
    cr = crown(fig)
    # струя падает отвесно: на макушку, а когда ладони подставлены под дырочку — в ладони
    under = clamp(1 - abs(ph[0] - hole[0]) / 90.0) * reach
    tgt = (hole[0], lerp(cr[1], min(cr[1], ph[1] - 18), under))
    sw = 9.0 * (1 - sm(t, a7 - .06, a7 + .02))
    stream = leak_stream(hole, tgt, t, sw)
    leak = sm(t, a5 - .08, a5 + .1)
    sand = splash(t, tgt, -1.0, a7, rate=26 * (1 - .6 * reach), seed=11, side=.3, v=(200, 420))

    def through(te, i):
        f_ = fig["wrist"]["n"] if i % 2 else fig["wrist"]["f"]
        return (lerp(f_[0], ph[0], .6) + 10, f_[1] + 30)
    sand += drip(t, through, a5 - .05, a7 + .4, rate=60 * leak, spread=90, seed=12, v0=40)
    # последняя песчинка зависает в горлышке
    last = ""
    if t >= a7 - .05:
        gx_, gy_ = rotp((GX, GY + 4), (GX, TOP_Y), sway)
        last = (f'<circle cx="{gx_:.1f}" cy="{gy_ + 2 * math.sin(t * 9):.1f}" r="9" fill="{SAND_HI}" stroke="{INK}" stroke-width="2.4"/>' +
                strokes(gx_, gy_, 22, 46, bump(t, a7, .3), n=6, w=4, col="#f6eedc", seed=8170))
    items = hg + fig["svg"] + stream + sand + last
    world = void_world(t, d, items, hg + fig["svg"], sh_dx=60 + 5 * sway)
    dt = t - T0("s02")
    cx, cy, s0 = 580.0, 835.0 + 22 * dt, 1.2
    push = .06 * kick(t, a7, .05, 4.0)
    sx, sy = shake2(t, a7, 6)
    return wrap(world, cx - sx, cy - sy, s0 * (1 + .02 * dt) * (1 + push), .3 * math.sin(t * 1.7), hook_title(t, T1("s03")))


# ═════════════════════════ s03: последняя песчинка — «тук»; колба лопается, засыпает по пояс ═════════════════════════
def s03(t):
    lib.dyn_begin()
    a8, a9 = stress(8, .3), stress(9, .3)      # «ВСЁ», «ПОЗдно»
    d = R.hook_void(t)
    burst = clamp((t - a9) / .55) if t >= a9 else 0.0
    crack = sm(t, a9 - .12, a9)
    sway = 1.2 * math.sin(2 * math.pi * .9 * t) + damp(t, a9, 3.0, 2.0, 4.0)
    hg, hole = hourglass(t, sway, 0.0, sand_top=0.0, sand_bot=.9, stream=0.0, burst=burst, crack=crack, leak=True)
    drop = .75 * sm(t, a9 + .02, a9 + .4)
    tuk = kick(t, a8, .04, 6.0)
    fig = dima_hook(t, ("panic81" if t < a9 + .1 else "sink81"), pose="d81_cup_up", pose2="d81_drop", u=drop, jit=.35 * (1 - drop),
                    dy=18 * tuk + 40 * drop, lean=-.2 * drop)
    cr = crown(fig)
    # последняя песчинка: выпадает из дырочки и падает на макушку ровно на «Всё»
    grain = ""
    fall = .26
    if a8 - fall <= t < a8:
        u = (t - (a8 - fall)) / fall
        x = lerp(hole[0], cr[0], u)
        y = hole[1] + (cr[1] - hole[1]) * u * u
        grain = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{SAND_HI}" stroke="{INK}" stroke-width="2.6"/>'
    elif t >= a8:
        grain = splash(t, cr, a8, a8 + .02, rate=200, v=(120, 260), seed=21, r=(5, 8))
    eff = strokes(cr[0], cr[1] - 6, 46, 110, bump(t, a8, .3), n=7, w=6, col="#f6eedc", seed=8180, a0=-165, span=150)
    # лопнула: песок обрушивается и горка растёт до пояса
    pile_u = ease_out(clamp((t - a9 - .03) / .5), 3)
    rush = ""
    if burst > 0:
        bx, by = rotp((GX, GY + 140 * GK), (GX, TOP_Y), sway)
        rush = drip(t, (bx, by), a9, a9 + .5, rate=170, spread=280, seed=22, v0=300)
        rush += splash(t, (bx, by), a9, a9 + .12, rate=200, v=(300, 700), seed=23, r=(5, 10))
    pile = PR.sand_pile(DIMA_HIP[0] + 30, 1960, 1.3, pile_u, seed=3)
    eff += strokes(GX, GY + 180, 230, 380, bump(t, a9, .34), n=10, w=8, col="#d8e6ff", seed=8190)
    items = hg + fig["svg"] + grain + rush + pile + eff
    world = void_world(t, d, items, hg + fig["svg"] + pile, sh_dx=60 + 5 * sway)
    dt = t - T0("s03")
    cx, cy, s0 = 540.0, 1080.0 - 10 * dt, .8
    hit = .10 * kick(t, a9, .04, 3.5) + .03 * kick(t, a8, .03, 6)
    sx, sy = shake2(t, a9, 16)
    return wrap(world, cx - sx, cy - sy, s0 * (1 + .025 * dt) * (1 + hit), damp(t, a9, 1.4, 3.0, 6.0), hook_title(t, T1("s03")))


def whip_in(world, cx, cy, s, rot, t, t0, dx0=260.0, dur=.16):
    """Хлёст на входе плана: камера влетает сбоку, мир смазан копиями по горизонтали (гаснет за dur)."""
    u = clamp((t - t0) / dur)
    a = (1 - u) ** 2
    if a <= .02 or NOCAM or MASK:
        return cx, ""
    cx2 = cx - dx0 * a
    o = []
    for j, op in enumerate((.3, .2, .12)):
        o.append(f'<g opacity="{op * a:.3f}" transform="{lib.cam(cx2 + 40 * (j + 1) * a, cy, s, rot)}">{world}</g>')
    return cx2, "".join(o)


# ═════════════════════════ s04: ПОВОРОТ — всполох, ночь, часы на потолке тают ═════════════════════════
LIE_K = .78


def ghost_glass(t, u, seed=0):
    """Часы-мираж над Димой: контур тает (u 0 — видны, 1 — нет), рассыпаясь вверх светлой пылью."""
    gx, gy, gk = R.CEIL81_GHOST
    o = ""
    if u < .98:
        body = PR.giant_hourglass(gx, gy, gk, sand_top=0.0, sand_bot=.0, stream=0.0, t=t, seed=5, chain=0.0)
        o += f'<g opacity="{.46 * (1 - u) ** 1.3:.3f}" style="mix-blend-mode:screen" {lib.blur(2.2 + 8 * u)}>{body}</g>'
    if u > .02:
        for i in range(70):
            a = rnd(i, 31)
            px = gx + (rnd(i, 32) - .5) * 400 * gk
            py = gy + (rnd(i, 33) - .5) * 560 * gk
            ts = a * .6
            v = clamp((u - ts) / .5)
            if v <= 0 or v >= 1:
                continue
            x = px + 30 * math.sin(i + t * 2) * v
            y = py - 160 * v
            o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2 + 3 * rnd(i, 34):.1f}" fill="#e8dcb0" opacity="{.6 * (1 - v):.2f}"/>'
    return o


def s04(t):
    lib.dyn_begin()
    t0 = T0("s04")
    a10, a11, a12 = stress(10, .3), stress(11, .3), stress(12, .3)     # «Так», «думал», «Дима»
    d = R.night81(t, "floor", glow=1.0)
    hx, hy = R.LIE81_HIP
    turn = sm(t, a12 - .05, a12 + .45)
    fig = PE.dima_floor81(hx, hy, LIE_K, t, expr=None, glow=1.0 - .3 * turn, turn=turn, blink=bump(t, a11 + .2, .18))
    ph = fig.get("phone", (hx, hy - 300))
    thumb = bump(t, a11, .25)
    scr = PR.glow(ph[0], ph[1] + 30, 330, (.9 - .35 * turn) * (1 + .25 * thumb), "#9fc8ff")
    melt = sm(t, a10 - .05, a12 + .3)
    ghost = ghost_glass(t, melt)
    world = d["bg"] + ghost + d["light"] + d["rug"] + fig["svg"] + d["dark"] + scr
    cx, cy, s0 = d["cam"]
    dt = t - t0
    cam = lib.cam(cx + 10 * dt, cy - 6 * dt, s0 * (1 + .012 * dt))
    set_ink(s0)
    over = R.glitch_flash(t, t0, 0.0)
    return lib.svg(f'<g transform="{cam}">{world}</g>{over}')


# ═════════════════════════ s09: Америка — улица гаражей, счётчик щёлкает, гараж открывается ═════════════════════════
WALKERS = (("cap", 0.0), ("girl", .3), ("bald", .55), ("youth", .8), ("beard", .15), ("bob", .45))


def s09(t):
    lib.dyn_begin()
    t0 = T0("s09")
    a38, a39 = stress(38, .35), stress(39, .3)     # «посчИтали», «основАтелей» (улица — с «Америке», склейка)
    d = R.us_street(t, garages=False)
    gy = d["anchors"]["ground"]
    gars = ""
    for i, (gx, gy_) in enumerate(R.ST81_GARAGES):
        ou = sm(t, a39 - .05, a39 + .5) if i == 1 else (.3 if i == 3 else 0.0)
        gars += PR.garage(gx, gy_, R.ST81_GARAGE_K, seed=i, open_u=ou)
    # в открывающемся гараже — тёплый свет и человек начинает своё дело (стол с коробками)
    g2x, g2y = R.ST81_GARAGES[1]
    ou = sm(t, a39 - .05, a39 + .5)
    inside = ""
    if ou > .02:
        x0, x1 = g2x - 176, g2x + 176
        clip = lib.clip_rect(x0, g2y - 220, x1 - x0, 220)
        man = PE.passerby81("beard", g2x + 60, g2y - 74, .22, 0.0, 0.0, flip=True)
        tbl = shape(rect_pts(g2x - 150, g2y - 92, g2x - 10, g2y - 80), PR.C_WOOD, "", w=3, seed=8301) + \
            shape(rect_pts(g2x - 140, g2y - 80, g2x - 128, g2y), PR.C_WOOD_SH, "", w=2.6, seed=8302) + \
            shape(rect_pts(g2x - 32, g2y - 80, g2x - 20, g2y), PR.C_WOOD_SH, "", w=2.6, seed=8303) + \
            shape(rect_pts(g2x - 130, g2y - 140, g2x - 70, g2y - 92), "#C9A06A", "", w=3, seed=8304)
        inside = (f'<g clip-path="url(#{clip})"><rect x="{x0:.1f}" y="{g2y - 220:.1f}" width="{x1 - x0:.1f}" height="220" fill="#FFE2A0"/>'
                  + tbl + man["svg"] + "</g>")
        inside += PR.glow(g2x, g2y - 60, 320, .7 * ou, "#FFD98A")
    # вереница людей идёт по тротуару слева направо под счётчиком, счётчик щёлкает на каждого
    cl_x, cl_y = 480.0, 470.0
    people = ""
    clicks = []
    for i, (kind, ph) in enumerate(WALKERS):
        x0 = 300 - i * 160 + (rnd(i, 41) - .5) * 30
        v = 260.0
        x = x0 + (t - (a38 - .6)) * v
        if -200 < x < 1700:
            fig = PE.passerby81(kind, x, gy - 62 + 6 * (i % 2), .34, t, ph)
            people += fig["svg"]
        clicks.append((a38 - .6) + (cl_x - x0) / v)
    click = bump(t, a38 - .02, .18)
    for ct in clicks:
        if ct >= a38 - .02:
            click = max(click, bump(t, ct, .16))
    clicker = PR.tally_clicker(cl_x, cl_y + 10 * math.sin(t * 2.2), 1.3, click, t, seed=1)
    eff = strokes(cl_x, cl_y - 150, 40, 90, bump(t, a38 - .02, .3), n=5, w=6, col="#2a3550", seed=8310, a0=-150, span=120)
    world = d["bg"] + gars + inside + people + d["front"] + clicker + eff
    pan = sm(t, t0, a39 + .1)
    cx = lerp(560, 900, pan)
    cy = lerp(880, 930, sm(t, a39 - .1, a39 + .4))
    s = 1.0 + .22 * sm(t, a39 - .1, a39 + .45)
    cx, blur = whip_in(world, cx, cy, s, 0.0, t, t0, dx0=-300)
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s)}">{world}</g>{blur}')


# ═════════════════════════ s18: ПЕТЛЯ — тот же ракурс, тепло; кот переворачивает часы ═════════════════════════
def s18(t):
    lib.dyn_begin()
    t0 = T0("s18")
    a81, a82 = stress(81, .25), stress(82, .3)          # «ТОЛЬко», «начинАется»
    d = R.hook_void(t, warm=1.0)
    fl = clamp((t - a81) / .5)
    flip = ease_io(fl)
    sway = .9 * math.sin(2 * math.pi * .8 * t) + damp(t, a81 + .5, 2.2, 2.0, 4.0)
    if fl < 1:
        st_top, st_bot, stream = 0.0, .9, 0.0
        fu = flip
    else:
        drain = clamp((t - a82) / 4.0)
        st_top, st_bot, stream, fu = .9 - .3 * drain, .03 + .2 * drain, sm(t, a82 - .05, a82 + .1), 0.0
    hg, hole = hourglass(t, sway, 0.0, sand_top=st_top, sand_bot=st_bot, stream=stream, flip=fu, leak=False)
    fig = dima_hook(t, "laugh81" if t > a81 + .3 else "smile81", pose="d81_laugh", jit=.18, dy=45.0)
    # кот на верхней крышке: лапы вверх («упирается»), на «только» прыгает — часы переворачиваются под ним, он приземляется снова наверх
    k_cat = .78
    cap = rotp((GX, TOP_Y - 2), (GX, TOP_Y), sway)
    if t < a81 - .12:
        cat = PE.cat_svg(cap[0], cap[1], k_cat, dict(PE.CAT_ST["paws_up81"], tail=8 * math.sin(t * 3)), t)
    elif t < a81 + .58:
        u = clamp((t - (a81 - .12)) / .7)
        cat = PE.cat_jump(cap, (cap[0] + 6, cap[1]), k_cat, u, t, dict(PE.CAT_ST["paws_up81"]), height=170)
    else:
        cat = PE.cat_svg(cap[0] + 6, cap[1], k_cat, dict(PE.CAT_ST["proud81"], tail=10 * math.sin(t * 2.4)), t)
    sparkle = ""
    if t >= a82:
        for i in range(10):
            ph_ = (t * 1.3 + i * .1) % 1
            x = GX + (rnd(i, 51) - .5) * 300
            y = GY - 60 + (rnd(i, 52) - .5) * 360
            sparkle += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3 + 3 * math.sin(math.pi * ph_):.1f}" fill="#fff4c8" opacity="{.8 * math.sin(math.pi * ph_):.2f}"/>'
    eff = strokes(GX, GY, 300, 380, bump(t, a81 + .45, .3), n=8, w=6, col="#fff1cf", seed=8320)
    items = hg + fig["svg"] + cat + sparkle + eff
    world = void_world(t, d, items, hg + fig["svg"] + cat, sh_dx=60 + 5 * sway)
    u = ease_out(clamp((t - t0) / 1.4), 2)
    cx0, cy0, s0 = R.CAM81_HOOK
    return wrap(world, cx0, cy0 + 8 * (1 - u), s0 * (1.06 - .06 * u), 0.0)


FRAMES = {"s01": s01, "s02": s02, "s03": s03, "s04": s04, "s09": s09, "s18": s18}


def frame(sid, t):
    return FRAMES[sid](t)
