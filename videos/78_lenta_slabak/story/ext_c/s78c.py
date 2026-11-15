"""Рилс 78 «Лента, ты слабак», группа C — хук, поворот, вечер, петля: s01, s02, s03, s16, s17, s18.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Всё время — из shots.json (t0/t1) и voice/words.json (слова по индексу wN),
секунды в коде — только длительности движений. Места — common/room.py (раздел 78), Дима — common/people.py (dima_reach78 и др.),
кот — common/cat.py (через people.cat_*), предметы — common/props.py, надпись хука — common/hand_text.py.
Букв и цифр нет, кроме «Ты слабак?» (s01–s02). NOCAM=1 — без камеры и без надписи (замер движения рисунка)."""
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
HOOK_TEXT = json.load(open(os.path.join(STORY, "reel.json"))).get("hook_screen", "Ты слабак?")
NOCAM = bool(os.environ.get("NOCAM"))


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


def wrap(world, cx, cy, s, rot=0.0, over=""):
    """Мир в камере + экранный слой over (надпись — вне камеры)."""
    set_ink(s)
    if NOCAM:
        return lib.svg(f'<g transform="{lib.cam(cx, cy, 1.0)}">{world}</g>')
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, rot)}">{world}</g>{over}')


def hook_cam(t, t_hit, t_hit2, rot0=3.8, side0=48.0, fly=.2, far=1.45, over=.06):
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
    if amount <= .02 or NOCAM:
        return ""
    o = []
    for j, (dk, op) in enumerate(((.035, .22), (.07, .14), (.11, .08))):
        o.append(f'<g opacity="{op * amount:.3f}" transform="{lib.cam(cx, cy, s * (1 + dk * amount), rot)}">{world}</g>')
    return "".join(o)


# ═════════════════════════ надпись хука «Ты слабак?» (экранные координаты, s01–s02) ═════════════════════════
HOOK_SIZE = 1.36
HOOK_Y = 330.0              # линия строки: буквы ≈ 185…355, зона текста R.HD_TEXT (170–440) — только стена


def hook_title(t, t_end):
    """Пишется с 0.00 за 0.30 с (маркер-росчерк), целиком к 0.35; стоит до склейки поворота t_end и гаснет на ней."""
    if t >= t_end:
        return ""
    w = text_width(HOOK_TEXT, HOOK_SIZE)
    x0 = (1080 - w) / 2 - 20
    return hand_text(HOOK_TEXT, t, 0.0, .30, x0, HOOK_Y, HOOK_SIZE, ink="#141a33", bold=1.8)


# ═════════════════════════ s01: хук — телефон вцепился в палец ═════════════════════════
H_K = 1.08                           # масштаб Димы хука (голова ≈ 320 px)
H_HIP = R.HD_HIP
H_BASE = R.HD_PHONE_BASE
H_CAM = (500.0, 868.0)
H_S = 1.30                           # базовый масштаб хука: рисунок ≥ 65 % высоты картинки 0–1300


def s01_rig(t):
    """Хореография хука: длина резинки, натяг, прокрутка ленты, дрожь. Удары: w1 «ты», w3 «ЛИ-стаешь»."""
    t1, t2 = W(1), W(3)
    # кадр 0 — уже на середине рывка: палец идёт к Диме с ненулевой скоростью
    yank = .55 + .35 * math.sin(2 * math.pi * 1.6 * t + .2)                 # непрерывные рывки руки
    yank += .45 * kick(t, t1 - .04, .07, 4.0)                                 # удар 1: рывок сильнее, резинка до предела
    yank += .45 * kick(t, W(0) - .05, .09, 5.0) - .3 * kick(t, W(0) + .17, .06, 6.0)   # второй рывок на «Если» (w0) и отдача резинки
    snap = kick(t, t2 - .02, .06, 3.2)                                        # удар 2: телефон утягивает палец назад
    pull = clamp(.35 + .5 * yank - .2 * snap)
    L = 300 + 150 * yank - 230 * snap + damp(t, t1 + .06, 40, 3.4, 4) + damp(t, t2 + .05, -55, 3.0, 4)
    L += 14 * math.sin(t * 31)                                               # дрожь усилия
    ang = math.radians(-128 + 6 * math.sin(2 * math.pi * 1.6 * t) - 7 * snap)  # направление от основания к пальцу (вверх-влево)
    tip = (H_BASE[0] + L * math.cos(ang), H_BASE[1] + L * math.sin(ang))
    scroll = 1500 * t + 5200 * max(0.0, t - t2) ** 1.4 + 300 * max(0.0, t - t1)
    bite = .85 + .15 * kick(t, t1, .05, 6)
    stretch = clamp(.4 + .5 * yank - .3 * snap)
    return dict(tip=tip, pull=pull, scroll=scroll, bite=bite, stretch=stretch, snap=snap, yank=yank)


def s01_world(t, rg=None):
    rg = rg or s01_rig(t)
    d = R.hook_day(t, "close", 0.0, bump=.4 * kick(t, W(3), .05, 6))
    hx, hy = H_HIP
    lean = -.06 - .12 * rg["yank"] + .2 * rg["snap"]
    fig = PE.dima_reach78(hx + 12 * rg["snap"], hy, H_K, rg["tip"], rg["pull"], t, "strain78", clasp=True,
                          hair_jit=8 * math.sin(t * 37) + 10 * kick(t, W(1), .05, 6), strings_jit=math.sin(t * 29) + 1.5 * kick(t, W(3), .05, 5),
                          lean=lean, head_add=-.06 * rg["yank"] + .1 * rg["snap"])
    fx, fy = fig["finger"]
    ph_back = PR.phone_biter(H_BASE[0], H_BASE[1], fx, fy, 1.0, rg["bite"], rg["stretch"], rg["scroll"], .7, t, .5, "back", seed=1)
    ph_front = PR.phone_biter(H_BASE[0], H_BASE[1], fx, fy, 1.0, rg["bite"], rg["stretch"], rg["scroll"], .7, t, .5, "front", seed=1)
    cid = lib.clip_of(ellipse_pts(fx - 40, fy - 30, 150, 120, 24))      # кисть поверх корпуса телефона (палец в щели)
    hand = f'<g clip-path="url(#{cid})">{fig["svg"]}</g>'
    eff = ""
    for th in (W(1), W(3)):                                              # штрихи усилия у кисти на ударах
        a = bump(t, th - .02, .3)
        if a > .01:
            for j in range(3):
                ang = math.radians(-150 + 40 * j)
                r0, r1 = 120, 120 + 70 * a
                eff += line([(fx + r0 * math.cos(ang), fy + r0 * math.sin(ang)), (fx + r1 * math.cos(ang), fy + r1 * math.sin(ang))], 6, INK, seed=7811 + j,
                            op=min(1, 2 * a))
    world = d["bg"] + fig["svg"] + d["bed"] + ph_back + hand + ph_front + eff + d["shade"]
    if os.environ.get("MASK"):           # силуэт рисунка хука (Дима, рука, телефон) для замера заполнения
        lib.DEFS.append('<filter id="mk78"><feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 9 0"/></filter>')
        world = '<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>' + f'<g filter="url(#mk78)">{fig["svg"]}' + \
            PR.phone_biter(H_BASE[0], H_BASE[1], fx, fy, 1.0, rg["bite"], rg["stretch"], rg["scroll"], 0.0, t, .5, "all", seed=1) + '</g>'
    return world, fig


def s01(t):
    lib.dyn_begin()
    rg = s01_rig(t)
    world, fig = s01_world(t, rg)
    kk, rc, side, fl = hook_cam(t, W(1), W(3))
    sx1, sy1 = shake2(t, W(1), 7)
    sx2, sy2 = shake2(t, W(3), 12)
    cx = H_CAM[0] + side - sx1 - sx2 + 4 * math.sin(t * 2.1)
    cy = H_CAM[1] - sy1 - sy2
    s = H_S * kk * (1 + .02 * sm(t, .5, 1.6))
    over = hook_title(t, T1("s02"))
    blur = radial_blur(world, cx, cy, s, rc, fl)
    out = wrap(world, cx, cy, s, rc, blur + over)
    return out


# ═════════════════════════ s02: перетягивание, лицом в подушку ═════════════════════════
W_K = .62
W_CAM = (690.0, 1060.0, .93)


def _stand_hip(k):
    sc = k * PE.HEIGHT["dima"]
    return (R.HW_STAND[0], R.HW_FL - (PE.LEG_LEN - 12) * sc - 6)


def _landing():
    """Где Дима ложится лицом в подушку: доля падения u_cap (голова на подушке) и сдвиг стойки, чтобы голова пришла в HW_PILLOW."""
    hx, hy = _stand_hip(W_K)
    px, py = R.HW_PILLOW
    a, b = .3, 1.0
    for _ in range(30):
        m = (a + b) / 2
        if PE.dima_faceplant78(hx, hy, W_K, m, 0.0)["head"][1] < py - 75:
            a = m
        else:
            b = m
    hd = PE.dima_faceplant78(hx, hy, W_K, a, 0.0)["head"]
    return a, (px - 20) - hd[0]


U_CAP, W_DX = _landing()


def s02(t):
    lib.dyn_begin()
    t_bak = stress(6, .22)                        # ударный «БАК» — Дима лицом в подушку
    d = R.hook_day(t, "wide", 0.0, bump=bump(t, t_bak, .35))
    hx, hy = _stand_hip(W_K)
    hx += W_DX
    px, py = R.HW_PILLOW
    base = (px + 110, py - 25)                    # низ телефона прилип к дальнему краю подушки
    t_fall = t_bak - .3
    heel = sm(t, W(4) - .1, W(4) + .12)
    tug = math.sin(2 * math.pi * 1.9 * t) * (1 - sm(t, t_fall - .1, t_fall))
    if t <= t_fall:                               # тянет руку на себя обеими руками, упирается пяткой; резинка струной
        tip = (hx + (470 + 40 * tug - 30 * heel) * W_K, hy - (150 + 20 * tug) * W_K)
        fig = PE.dima_faceplant78(hx - 18 * heel + 8 * tug, hy, W_K, 0.12 + .1 * heel, t, tip=tip)
        fing = fig["finger"]
    else:                                         # резинка выиграла: летит лицом в подушку, отскок и затихает
        e = clamp((t - t_fall) / (t_bak - t_fall))
        u = .25 + (U_CAP - .25) * e - .04 * bump(t, t_bak, .3)
        fig = PE.dima_faceplant78(hx - 18, hy, W_K, u, t)
        fing = None
    if fing is not None:
        mouth = fing
    else:                                         # телефон пружиной назад и довольно шлёпается рядом, на бок
        f0 = (hx + 452 * W_K, hy - 140 * W_K)
        rest = (base[0] + 30, base[1] - 190)
        e = clamp((t - t_fall) / .3)
        sp = 1 - math.exp(-5 * e) * math.cos(8 * e) if e < 1 else 1.0
        sp = min(1.0, sp) if e >= 1 else sp
        mouth = (lerp(f0[0], rest[0], sp), lerp(f0[1], rest[1], sp) - 60 * bump(t, t_bak - .05, .3))
    scroll = 1100 * t + 2400 * max(0.0, t - t_bak)
    stretch = .9 if fing is not None else .5 * (1 - sm(t, t_fall, t_fall + .4)) + .2
    ph_b = PR.phone_biter(base[0], base[1], mouth[0], mouth[1], .62, 1.0, stretch, scroll, .6, t, .5, "back", seed=2)
    ph_f = PR.phone_biter(base[0], base[1], mouth[0], mouth[1], .62, 1.0, stretch, scroll, .6, t, .5, "front", seed=2)
    eff = ""
    a = bump(t, t_bak - .02, .4)
    if a > .01:   # шлёп: перо-штрихи от подушки
        for j in range(5):
            ang = math.radians(-160 + 35 * j)
            r0, r1 = 110, 110 + 110 * a
            eff += line([(px + r0 * math.cos(ang), py - 60 + r0 * math.sin(ang)), (px + r1 * math.cos(ang), py - 60 + r1 * math.sin(ang))], 5, INK,
                        seed=7821 + j, op=min(1, 2 * a))
    if fing is not None:
        cid = lib.clip_of(ellipse_pts(fing[0] - 20, fing[1] - 10, 90, 70, 20))
        world = d["bg"] + d["bed"] + fig["svg"] + ph_b + f'<g clip-path="url(#{cid})">{fig["svg"]}</g>' + ph_f + eff + d["shade"]
    else:
        world = d["bg"] + d["bed"] + fig["svg"] + ph_b + ph_f + eff + d["shade"]
    cx0, cy0, s0 = W_CAM
    dr = sm(t, T0("s02"), t_bak) * 50
    sx, sy = shake2(t, t_bak, 16)
    s = s0 * (1 + .03 * sm(t, T0("s02"), t_fall) + .10 * kick(t, t_bak, .04, 4))
    return wrap(world, cx0 + dr - sx, cy0 - sy, s, 0.0, hook_title(t, T1("s02")))


# ═════════════════════════ s03: поворот — всполох, ночь, отражение кричит ═════════════════════════
N_HIP = (330.0, 1112.0)
N_K = .95
REF_HIP = (760.0, 930.0)                 # отражение: таз (до зеркала), рисуется внутри стекла
REF_K = 1.02


def _night_dima(t, expr, hip=N_HIP, k=N_K, sink=0.0):
    x, y = hip
    return PE.dima_phone(x, y + sink, k, expr, "phone_chest74", t=t, thumb=.6)


def s03(t):
    tg = T0("s03")                        # склейка поворота = конец «слабак» + 0.06 (из shots.json)
    if t < tg - 1e-6:
        return s02(t)
    lib.dyn_begin()
    t7, t9, t11 = W(7), W(9), W(11)
    d = R.night78(t, "window", glow=1.0)
    # Дима полусидит в кровати, телефон двумя руками экраном к себе
    shout = sm(t, t9 - .06, t9 + .06) * (1 - sm(t, t11 - .05, t11 + .1))
    cower = sm(t, t11 - .02, t11 + .18)
    expr = "cower78" if cower > .5 else "shout78" if shout > .3 else "lit78"
    fig = _night_dima(t, expr, sink=40 * cower + 6 * math.sin(t * 2.4) - 8 * shout)
    head = fig["head"]
    # отражение в стекле: тот же Дима, зеркально, линией цвета стекла; кричит сильнее, на «себя» тычет пальцем
    rshout = sm(t, t9 - .02, t9 + .1)
    rx, ry = REF_HIP
    tip = (lerp(rx + 300, rx + 430, sm(t, t11 - .1, t11 + .08)), lerp(ry - 260, ry - 420, sm(t, t11 - .1, t11 + .08)) + 18 * bump(t, t11 + .05, .25))
    rk = REF_K * (1 + .06 * kick(t, t9, .06, 3) + .03 * kick(t, t11, .05, 4))
    rex = dict(PE.EXPR["dima"]["shout78"]) if rshout > .3 else dict(PE.EXPR["dima"]["lit78"])
    rf = PE.dima_reach78(rx, ry, rk, tip, pull=.4 + .6 * sm(t, t11 - .1, t11 + .08), t=t, expr=rex, clasp=False, lean=.1 * rshout,
                         head_add=.12 * rshout)
    refl = f'<g transform="translate({2 * rx:.1f} 0) scale(-1 1)">{rf["svg"]}</g>'
    reveal = sm(t, t7 - .05, t7 + .3)
    glass = f'<g clip-path="url(#{d["glass_clip"]})" opacity="{.25 + .75 * reveal:.3f}">{PE.reflection78(refl, "#8fa6dc", .85)}</g>'
    eff = ""
    for th, cxy in ((t9, head), ):        # штрихи крика у рта
        a = bump(t, th - .02, .5)
        if a > .01:
            for j in range(3):
                ang = math.radians(-40 + 30 * j)
                r0, r1 = 150, 150 + 80 * a
                eff += line([(cxy[0] + r0 * math.cos(ang), cxy[1] + 40 + r0 * math.sin(ang)),
                             (cxy[0] + r1 * math.cos(ang), cxy[1] + 40 + r1 * math.sin(ang))], 5, "#c8d4ff", seed=7831 + j, op=min(1, 2 * a))
    quilt = R._quilt(-860, 1940, R.N78_BED_Y + 50 + 4 * math.sin(t * 1.7), 2400, R.N78, t * 1.6, 7840)
    world = d["bg"] + glass + R.cold_tint(R.cold_tint(fig["svg"], 1.0, 1.0), 0.0, .6) + quilt + eff + d["dark"]
    # свет экрана на лице (поверх затемнения): холодный прямоугольник, телефон светится
    px, py = fig["phone"]
    fl = 1 + .04 * math.sin(t * 9.1) + .03 * math.sin(t * 15.3)
    q = lib.T(lib.rrect(-95, -120, 95, 120, 30), head[0] + 30, head[1] + 20, 1, -10)
    lit = (f'<g {lib.blur(16)}>' + blob(q, "#cfe6ff", .30 * fl) + blob(ellipse_pts(px, py - 10, 120, 90, 18), "#bfe0ff", .28 * fl) + '</g>')
    # тьма поворота: после всполоха почти чёрный синий, в нём светится только экран; с «Так» — ночь проявляется
    if t < tg + 2 / 30:
        cover = 1.0
    else:
        cover = lerp(1.0, .9, sm(t, tg + 2 / 30, tg + .14)) * (1 - reveal)
    dark = f'<rect x="-900" y="-900" width="2880" height="3720" fill="#03050c" opacity="{cover:.3f}"/>' if cover > .003 else ""
    world += dark + f'<g opacity="{.55 + .45 * reveal:.3f}">{lit}</g>'
    cx, cy, s = 520.0, 800.0, 1.3
    s *= 1 + .06 * kick(t, t9, .06, 3.5) + .01 * math.sin(t * .9)
    pull = sm(t, t11, t11 + .4)
    cx = lerp(cx, cx + 60, pull) + 5 * math.sin(t * 1.3)
    cy = lerp(cy, cy - 50, pull) - 30 * kick(t, t9, .06, 3.5)
    over = R.glitch_flash(t, tg, 0.0) if t < tg + 2 / 30 else ""
    return wrap(world, cx, cy, s, 0.0, over)


# ═════════════════════════ s16: коридор — телефон в корзинку, дверь закрылась ═════════════════════════
HD = R.HALL_DOOR                          # (центр x, пол, ширина, высота)
D_K = .8
BASKET = (HD[0] + 120.0, 905.0, .62)     # корзинка на полке в соседней комнате (центр дна, k)
CAM16 = (690.0, 1040.0, 1.0)


def _other_room(t, glow):
    """Соседняя комната в проёме двери: сумрак, полка, корзинка; телефон в корзинке светит холодным пятном."""
    dx, fy, dw, dh = HD
    x0, x1, y0 = dx - dw / 2, dx + dw / 2, fy - dh
    o = [blob(rect_pts(x0, y0, x1, fy), "#3a3f5e")]
    o.append(blob(rect_pts(x0, fy - 140, x1, fy), "#2c2f46"))
    bx, by, bk = BASKET
    o.append(shape(rect_pts(x0 + 20, by, x1 - 10, by + 30), "#6e5a4a", "", w=3.4, seed=7861))
    o.append(line([(x0 + 60, by + 30), (x0 + 90, by + 120)], 6, "#4e3e32", seed=7862))
    if glow > .01:
        o.append(f'<g {lib.blur(18)}>' + blob(ellipse_pts(bx, by - 150 * bk, 230, 150, 18), "#bfe0ff", .45 * glow) + '</g>')
    return "".join(o)


def s16(t):
    lib.dyn_begin()
    t82, t82e, t84, t85 = W(82), WE(82), W(84), W(85)
    d = R.hall_scene(t, "evening")
    dx, fy, dw, dh = HD
    bx, by, bk = BASKET
    rim = PR.basket_rim(bx, by, bk)
    # Дима: подходит (шаг), кладёт телефон экраном вниз в корзинку (рука к корзинке), берётся за ручку и закрывает дверь
    hip_y = fy - (PE.LEG_LEN - 12) * D_K * PE.HEIGHT["dima"] - 4
    walk_u = clamp((t - (T0("s16") - .2)) / (t82 - T0("s16") + .3))
    x = lerp(150.0, 330.0, ease_out(walk_u, 2)) - 40 * sm(t, t84 - .1, t84 + .2) + 20 * sm(t, t85 - .25, t85)
    place = sm(t, t82 - .05, t82e)                  # рука к корзинке
    let_go = t > t82e - .08
    back = sm(t, t82e, t84)                        # рука назад
    knob_u = sm(t, t84, t85 - .05)
    close = ease_in2 = clamp((t - (t85 - .12)) / .2) ** 2 if t > t85 - .12 else 0.0
    knob = (dx + dw / 2 - 30 - (dw - 60) * max(close, .0) - 0, fy - 470 * 1.45)
    if knob_u > .01:
        fig = PE.dima_door78(x, hip_y, D_K, (lerp(dx + dw / 2 - 80, knob[0], close), knob[1]), knob_u, t, "relief78" if close > .9 else "carry78")
        hold = None
    elif place > .01 or back > 0:
        tgt = (lerp(x + 520 * D_K, rim[0] - 60, place), lerp(hip_y - 300 * D_K, rim[1] - 40, place))
        fig = PE.dima_door78(x, hip_y, D_K, tgt, 1.0 - back, t, "carry78")
        hold = None if let_go else fig["wrist"]["n"]
    else:
        fig = PE.dima_carry78(x, hip_y, D_K, phase=t / .55, t=t, arm_u=1.0, walk=walk_u < 1)
        hold = fig["palm"]
    # телефон: на ладони экраном вниз; отпущен — падает в корзинку и подпрыгивает; свет в комнате гаснет за дверью
    if hold is not None:
        ph = PR.phone_flat(hold[0] + 10, hold[1] - 6, .62, 0, 0, True, .5, seed=3)
        ph_in = ""
    else:
        ph = ""
        e = clamp((t - (t82e - .08)) / .14)
        py = lerp(rim[1] - 60, rim[1] + 20, e * e) - 24 * bump(t, t82e + .08, .22)
        ph_in = PR.phone_flat(rim[0], py, .62, 0, 0, True, .6, seed=3)
    glow = 1.0 if t < t85 else 0.0
    room = _other_room(t, glow) + PR.basket(bx, by, bk, seed=1) + ph_in
    # дверь: петли справа, ручка слева; открыта — полотно ребром у правого косяка, закрывается к t85 с хлопком
    sx = lerp(.1, 1.0, close)
    door = PR.door(0, 0, 1.45, 0.0, seed=4)
    door_svg = (f'<g transform="translate({dx + dw / 2:.1f} {fy:.1f}) scale({-sx * (1 + .02 * kick(t, t85 + .08, .03, 9)):.4f} 1) '
                f'translate({-dw / 2:.1f} 0) scale(1 1)">{door}</g>')
    door_svg = f'<g transform="translate({dx + dw / 2:.1f} {fy:.1f}) scale({sx:.4f} 1) translate({-dx - dw / 2:.1f} {-fy:.1f})">' \
               f'<g transform="translate({2 * dx:.1f} 0) scale(-1 1)">{PR.door(dx, fy, 1.45, 0.0, seed=4)}</g></g>'
    strip = ""
    if t > t85 + .1:     # холодный свет из щели под дверью мерцает и гаснет
        a = (1 - sm(t, t85 + .5, t85 + .9)) * (.7 + .3 * math.sin(t * 37) * math.sin(t * 13))
        if a > .01:
            strip = blob(rect_pts(dx - dw / 2 + 20, fy - 7, dx + dw / 2 - 20, fy + 2), "#cfe8ff", a) + \
                f'<g {lib.blur(10)}>' + blob(rect_pts(dx - dw / 2, fy - 4, dx + dw / 2, fy + 60), "#bfe0ff", .35 * a) + '</g>'
    # кот трусит шагом за Димой
    cx_ = lerp(430.0, 650.0, sm(t, T0("s16") - .2, t84 + .1))          # трусит рядом и садится на коврик у двери
    cat_k = .7
    walking = t < t84 + .05
    cst = dict(look=(.6, -.2), tail=8, flame_e=1.0)
    cat = PE.cat_walk(cx_, fy + 4, cat_k, t, cst, .4) if walking else PE.cat_svg(cx_, fy + 4, cat_k, dict(cst, blink=bump(t, t85 + .3, .2)), t)
    world = d["bg"] + room + door_svg + d["frame"] + strip + fig["svg"] + ph + cat
    cx, cy, s = CAM16
    cx += lerp(-30, 30, sm(t, T0("s16") - .2, T1("s16")))
    sx2, sy2 = shake2(t, t85 + .08, 9)
    s *= 1 + .03 * kick(t, t85 + .08, .04, 5)
    return wrap(world, cx - sx2, cy - sy2, s)


# ═════════════════════════ s17: кресло у окна на закате ═════════════════════════
C_K = .82


def s17(t):
    lib.dyn_begin()
    t87, t88 = W(87), W(88)
    d = R.evening_chair(t, sun=.6 + .4 * sm(t, T0("s17"), T1("s17")))
    hx, hy = d["anchors"]["hip"]
    ax, ay = d["anchors"]["arm"]
    us = clamp((t - (t87 - .25)) / .75)
    ub = clamp((t - (t88 - .05)) / .7)
    book_at = (ax - 40, ay - 10)
    fig = PE.dima_chair78(hx, hy, C_K, us, ub, t, book_at=book_at)
    if ub < .5:
        book = PR.book_closed(book_at[0], book_at[1], 1.25, -8, "#3f6fb0")
    else:
        bh = fig["book_hand"]
        book = PR.book_closed(bh[0] + 10, bh[1] + 30, 1.25, -18 + 10 * sm(t, t88 + .3, t88 + .7), "#3f6fb0")
    # кот запрыгивает на подлокотник, когда книга уже в руке
    tj = t88 + .25
    p0 = (ax + 120, d["anchors"]["fl"] - 2)
    p1 = (ax + 45, ay + 14)
    cat_k = .5
    uj = clamp((t - tj) / .55)
    cst = dict(look=(-.6, -.1), tail=6 * math.sin(t * 2), flame_e=1.0 + .3 * bump(t, tj + .55, .4))
    if t < tj:
        cat = PE.cat_svg(p0[0], p0[1], cat_k, dict(cst, ear=6 * bump(t, t87, .3), tilt=4 * math.sin(t * 2.2)), t)
    else:
        cat = PE.cat_jump(p0, p1, cat_k, uj, t, cst)
    world = d["bg"] + d["chair_back"] + fig["svg"] + d["chair_front"] + book + cat + d["light"]
    u = sm(t, T0("s17") - .2, T1("s17") + .2)
    s = lerp(1.14, 1.04, u)
    return wrap(world, 560 + 20 * u, 1000 - 20 * u, s)


# ═════════════════════════ s18: петля — кот спит на коленях ═════════════════════════
L_CAT = (830.0, 1236.0, 1.15)         # кот клубком на коленях (середина низа клубка, k)


def s18(t):
    lib.dyn_begin()
    t91, t93, t97 = W(91), W(93), W(97)
    d = R.hook_day(t, "close", 1.0)
    cx_, cy_, ck = L_CAT
    settle = damp(t, t91 - .05, .08, 2.2, 4.5)
    eye = 1 - sm(t, t93 - .1, t93 + .25)
    st = dict(eye=.7 * eye, breath=1.0 + .4 * (1 - eye), flame_e=1.0 + .9 * bump(t, t97 - .05, .7), turn=.3 * eye, squint=.4 * (1 - eye))
    cat = PE.cat_curl(cx_, cy_, ck, st, t)
    cat = f'<g transform="translate({cx_:.1f} {cy_:.1f}) scale({1 + settle:.4f} {1 - settle:.4f}) translate({-cx_:.1f} {-cy_:.1f})">{cat}</g>'
    head = (cx_ - 150 * ck, cy_ - 130 * ck)
    stroke = max(0.0, t - (t97 - .15)) * .9
    fig = PE.dima_lap78(H_HIP[0], H_HIP[1], H_K, (head[0] - 20, head[1] - 40), t, stroke)
    zz = PR.zzz(cx_ - 120 * ck, cy_ - 300 * ck, .7, t, sm(t, t93, t93 + .4))
    world = d["bg"] + fig["svg"] + d["bed"] + cat + zz + d["shade"]
    cid = lib.clip_of(ellipse_pts(fig["finger"][0] - 40, fig["finger"][1] - 30, 150, 110, 24))
    world = d["bg"] + fig["svg"] + d["bed"] + cat + f'<g clip-path="url(#{cid})">{fig["svg"]}</g>' + zz + d["shade"]
    u = sm(t, T0("s18") - .2, T1("s18") + .2)
    return wrap(world, H_CAM[0] + 15 * u, H_CAM[1] + 20 * u, H_S * (1 + .05 * u))


def frame(sid, t):
    return {"s01": s01, "s02": s02, "s03": s03, "s16": s16, "s17": s17, "s18": s18}[sid](t)
