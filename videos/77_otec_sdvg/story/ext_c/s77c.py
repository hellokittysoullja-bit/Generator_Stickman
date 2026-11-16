"""Рилс 77 «СДВГ не бывает?», группа C — хук, поворот, мост, петля: s01, s02, s03, s04, s10, s20.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Всё время — из shots.json (t0/t1) и voice/words.json (слова по индексу wN),
секунды в коде — только длительности движений. Места — common/room.py (раздел 77), отец, Дима — common/people.py, кот — common/cat.py
(через people.cat_*), предметы — common/props.py, надпись хука — common/hand_text.py (текст — reel.json → hook_screen).
Букв и цифр нет, кроме надписи хука (s01–s03). NOCAM=1 — без камеры и без надписи (замер движения рисунка); MASK=1 — силуэт
рисунка хука (отец, кулак, кружка, кот) для замера заполнения."""
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
from hand_text import hand_lines  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, rect_pts  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
HOOK_TEXT = json.load(open(os.path.join(STORY, "reel.json")))["hook_screen"]
NOCAM = bool(os.environ.get("NOCAM"))
MASK = bool(os.environ.get("MASK"))
NOCAM_C = (568.0, 960.0, 1.0)


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


def hop(t, t0, h, dur):
    """Прыжок по параболе: высота над дном (0 вне [t0, t0+dur])."""
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return 4 * h * u * (1 - u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def wrap(world, cx, cy, s, rot=0.0, over=""):
    """Мир в камере + экранный слой over (надпись — вне камеры)."""
    set_ink(s)
    if NOCAM or MASK:        # неподвижная камера: замер движения самого рисунка и заполнения
        return lib.svg(f'<g transform="{lib.cam(*NOCAM_C)}">{world}</g>')
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, rot)}">{world}</g>{over}')


def hook_cam(t, t_hit, t_hit2, rot0=-3.9, side0=-52.0, fly=.2, far=1.46, over=.065):
    """Влёт правил 28/29 (не слабее эталона 17): масштаб 1/far → 1 за fly с без разгона, перелёт over с отскоком, поворот rot0 с
    возвратом, боковой занос; удар +5 % на t_hit и +10 % на t_hit2. -> (множитель масштаба, поворот, занос, доля полёта 0…1)."""
    u = clamp(t / fly)
    e = ease_out(u, 3)
    s = 1 / far + (1 - 1 / far) * e
    if t > fly:
        s += over * math.exp(-7 * (t - fly)) * math.cos(2 * math.pi * 2.2 * (t - fly))
    rot = rot0 * (1 - e) + damp(t, fly, 1.3, 2.0, 6.0)
    side = side0 * (1 - e)
    hit = .05 * kick(t, t_hit, .03, 5.5) + .10 * kick(t, t_hit2, .03, 4.5)
    return s * (1 + hit), rot, side, 1 - e


def radial_blur(world, cx, cy, s, rot, amount):
    """Радиальное размытие влёта: копии мира с чуть большим масштабом поверх, полупрозрачно."""
    if amount <= .02 or NOCAM or MASK:
        return ""
    o = []
    for dk, op in ((.035, .22), (.07, .14), (.11, .08)):
        o.append(f'<g opacity="{op * amount:.3f}" transform="{lib.cam(cx, cy, s * (1 + dk * amount), rot)}">{world}</g>')
    return "".join(o)


def flat(svg, col, op=1.0):
    """Силуэт рисунка одним цветом (жёсткая тень на стене)."""
    fid = lib.uid("fl")
    r, g, b = (int(col[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lib.DEFS.append(f'<filter id="{fid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 {r:.3f} 0 0 0 0 {g:.3f} '
                    f'0 0 0 0 {b:.3f} 0 0 0 {op:.3f} 0"/></filter>')
    return f'<g filter="url(#{fid})">{svg}</g>'


def mask_of(svg):
    """MASK=1: всё, что не фон, — чёрным на белом."""
    lib.DEFS.append('<filter id="mk77"><feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 9 0"/></filter>')
    return '<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>' + f'<g filter="url(#mk77)">{svg}</g>'


def strokes(cx, cy, a, r0, dr, ang0, ang1, n, seed, col=INK, w=6):
    """Штрихи удара пером вокруг точки (веер ang0…ang1), a 0…1 — сила."""
    if a <= .01:
        return ""
    o = []
    for j in range(n):
        ang = math.radians(ang0 + (ang1 - ang0) * j / max(1, n - 1))
        r1 = r0 + dr * a
        o.append(line([(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)), (cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))], w, col,
                      seed=seed + j, op=min(1, 2 * a)))
    return "".join(o)


# ═════════════════════════ надпись хука «СДВГ / не бывает?» (экранные координаты, s01–s03) ═════════════════════════
HOOK_SIZE = 1.40
HOOK_Y = 282.0               # линия первой строки; вторая — на HOOK_LH ниже; буквы ≈ 150…432 (зона R.K77_TEXT)
HOOK_LH = 140.0
HOOK_LINES = HOOK_TEXT.split(" ", 1)


def hook_title(t, t_end):
    """Пишется с 0.00 за 0.30 с (маркер-росчерк), целиком к 0.35; стоит до склейки поворота t_end и гаснет на ней."""
    if t >= t_end or NOCAM or MASK:
        return ""
    return hand_lines(HOOK_LINES, t, 0.0, .30, 540.0, HOOK_Y, HOOK_SIZE, HOOK_LH, ink="#141a33", bold=1.8, dx=(-14.0, 6.0))


# ═════════════════════════ s01: хук — кулак по столу ═════════════════════════
FA_HIP = (190.0, 1398.0)        # таз отца за столом (ноги скрыты столом)
FA_K = 1.34
FA_CAT = (978.0, 1166.0)        # кот на правом краю стола
CAT_K = .72
MUG0 = (815.0, 1150.0)          # кружка дном на столешнице
H_CAM = (568.0, 960.0)
FIST_DOWN = (560.0, 1000.0)     # запястье (мир) — кулак на столешнице
FIST_UP = (770.0, 830.0)        # замах: кулак у лица (не выше головы — над головой надпись)


def s01_rig(t):
    """Хореография хука. Удары: hit1 — начало «СДВГ» (w0), hit2 — ударный «ВА» «бывает» (w2)."""
    h1, h2 = W(0), stress(2, .36)
    # высота кулака h: 1 — замах, 0 — на столе. Кадр 0 — уже на середине удара вниз (без разгона с нуля)
    if t < h1:
        h = .62 * (1 - t / h1)
    elif t < h1 + .06:
        h = .06 * math.sin(math.pi * (t - h1) / .06)          # отдача от стола
    elif t < h2 - .16:
        u = (t - h1 - .06) / (h2 - .16 - h1 - .06)
        h = ease_out(clamp(u / .55), 2) * (.82 + .18 * clamp((u - .55) / .45)) + .1 * math.sin(2 * math.pi * 4.2 * (t - h1)) * clamp(u / .3)   # замах и трясёт кулаком
    elif t < h2:
        h = 1 - ((t - h2 + .16) / .16) ** 1.6
    else:
        h = .04 * math.sin(math.pi * clamp((t - h2) / .06)) + .1 * sm(t, h2 + .1, h2 + .5) + .03 * math.sin(t * 9)
    h = clamp(h, 0, 1.08)
    bounce = 14 * kick(t, h1, .025, 14) + 16 * kick(t, h2, .025, 14)
    return dict(h=h, h1=h1, h2=h2, bounce=bounce)


def mug_state(t, h1, h2):
    """Кружка: качается до удара, подлетает на hit1 и прыгает на дне дважды, на hit2 — выше и крутится. -> (dx, dy, rot, spin, splash)."""
    rot = 7 * math.sin(2 * math.pi * 2.6 * t + 1.1) * math.exp(-1.5 * t) if t < h1 else 0.0
    dy, spin, dx = 0.0, 0.0, 0.0
    for (ta, hh, dur, sp, ddx) in ((h1, 240, .44, .7, 30), (h1 + .44, 52, .2, .1, -6), (h1 + .64, 16, .12, 0, -2), (h2, 300, .52, 1.4, -30),
                                   (h2 + .52, 60, .2, .15, 10)):
        u = (t - ta) / dur
        if 0 < u < 1:
            dy = -4 * hh * u * (1 - u)
            spin = sp * u
            rot = (24 if hh > 100 else 6) * math.sin(math.pi * u) * (1 if ddx > 0 else -1)
    for (ta, dur, ddx) in ((h1, .44, 30), (h1 + .44, .2, -6), (h1 + .64, .12, -2), (h2, .52, -30), (h2 + .52, .2, 10)):
        dx += ddx * clamp((t - ta) / dur)
    splash = clamp((t - h1) / .42) if h1 < t < h1 + .42 else (clamp((t - h2) / .4) if h2 < t < h2 + .4 else 0.0)
    rot += damp(t, h1 + .44, 9, 3.2, 3) + damp(t, h1 + .76, 8, 3.0, 3) + damp(t, h2 + .72, 10, 3.0, 4)
    return dx, dy, rot, spin, splash


def father_hook(t, h, hip, k, expr_shout=1.0, seed_t=0.0):
    """Отец над столом: кулак по высоте h (0 — на столе, 1 — замах), голова и усы дёргаются."""
    tx = lerp(FIST_DOWN[0], FIST_UP[0], h) + hip[0] - FA_HIP[0]
    ty = lerp(FIST_DOWN[1], FIST_UP[1], h) + hip[1] - FA_HIP[1]
    dirv = (lerp(.45, .25, h), lerp(1.0, -1.0, clamp(h * 1.4)))
    ex = dict(PE.EXPR["father77"]["shout"])
    ex["mous"] = math.sin(t * 31) * .8
    ex["chub"] = .8 * math.sin(t * 23 + 1)
    ex["open"] = .7 + .3 * math.sin(t * 17)
    return PE.father(hip[0], hip[1], k, ex, "slam", t, arms={"n": ("ik", (tx, ty), -1)}, hands={"n": {"kind": "fist", "dir": dirv}},
                     lean_add=.03 * (1 - h) - .05 * h + .02 * math.sin(t * 8), head_add=.08 * math.sin(t * 17) - .05 * h)


def cat_hook_st(t, h1, h2):
    """Кот на краю стола: уши прижаты с кадра 0, на ударах вжимается; на hit2 отскакивает к краю."""
    st = dict(flat_ears=1.0, look=(-.8 + .15 * math.sin(t * 7), -.35), squint=0.0, tail=-14 + 18 * math.sin(t * 11), flame_e=.55 + .15 * math.sin(t * 17),
              blink=bump(t, h1 - .01, .16))
    sq = kick(t, h1, .03, 7) + kick(t, h2, .03, 7)
    st["sy"] = 1 - .16 * min(1.0, sq) + .02 * math.sin(t * 21)
    st["sx"] = 1 + .1 * min(1.0, sq)
    st["drop"] = .5 * min(1.0, sq) + .12
    st["tilt"] = -6 + 5 * math.sin(t * 13)
    st["rot"] = 2.5 * math.sin(t * 19)        # дрожит
    return st


def s01_world(t):
    rg = s01_rig(t)
    h1, h2 = rg["h1"], rg["h2"]
    d = R.kitchen77(t, "hook", bounce=rg["bounce"])
    fig = father_hook(t, rg["h"], FA_HIP, FA_K)
    # жёсткая тень отца на стене (свет из окна слева сверху)
    shadow = f'<g transform="translate(70 -30)">{flat(fig["svg"], "#9ea8ae", .55)}</g>'
    mdx, mdy, mrot, spin, splash = mug_state(t, h1, h2)
    mug = PR.enamel_mug(MUG0[0] + mdx, MUG0[1] - 66 - rg["bounce"] + mdy, 1.0, mrot, spin, splash, t)
    jump = hop(t, h2 + .02, 46, .3)
    cx = FA_CAT[0] + 8 * sm(t, h2, h2 + .3)
    st = cat_hook_st(t, h1, h2)
    if jump > 0:
        st["legs"] = .6
    cat = PE.cat_svg(cx, FA_CAT[1] - rg["bounce"] - jump, CAT_K, st, t)
    fx, fy = fig["fist"]
    eff = ""
    for th in (h1, h2):
        a = bump(t, th - .01, .3)
        eff += strokes(fx, d["top"] + 10, a, 70, 90, 190, 350, 5, 7701, INK, 6)
    world = d["bg"] + shadow + fig["svg"] + d["table"] + mug + cat + eff + d["light"]
    if MASK:
        world = mask_of(fig["svg"] + mug + cat)
    return world


def s01(t):
    lib.dyn_begin()
    world = s01_world(t)
    rg = s01_rig(t)
    kk, rc, side, fl = hook_cam(t, rg["h1"], rg["h2"])
    sx1, sy1 = shake2(t, rg["h1"], 9)
    sx2, sy2 = shake2(t, rg["h2"], 14)
    cx = H_CAM[0] + side - sx1 - sx2 + 4 * math.sin(t * 2.1)
    cy = H_CAM[1] - sy1 - sy2
    s = kk * (1 + .02 * sm(t, .6, 1.6))
    blur = radial_blur(world, cx, cy, s, rc, fl)
    return wrap(world, cx, cy, s, rc, blur + hook_title(t, T0("s04")))


# ═════════════════════════ s02: ракурс ребёнка — палец-копьё ═════════════════════════
KID_HIP = (850.0, 1400.0)
KID_K = 1.25
FA2_HIP = (290.0, 1358.0)
FA2_K = 1.3


def s02(t):
    lib.dyn_begin()
    d = R.kitchen77(t, "hook", "low")
    t3, t4 = W(3), stress(4, .55)          # «бывают», ударный «КИ» «слабаки»
    lean = sm(t, T0("s02") - .1, t3 + .1) * .1 + .06 * kick(t, t4 - .06, .06, 4)
    # палец: летит вниз к мальчику с кадра 0, на «слабаки» тычет почти в нос
    jab = sm(t, T0("s02") - .2, t3 + .15) * .6 + .4 * kick(t, t4 - .05, .05, 3.5)
    tgt = (lerp(420, 500, jab), lerp(800, 866, jab))
    ex = dict(PE.EXPR["father77"]["shout_kid"])
    ex["mous"] = math.sin(t * 29) * .7
    ex["open"] = .55 + .45 * math.sin(t * 15)
    fa = PE.father(FA2_HIP[0], FA2_HIP[1], FA2_K, ex, "point", t, lean_add=lean, head_add=.03 * math.sin(t * 11),
                   arms={"n": ("ik", tgt, -1)})
    shadow = f'<g transform="translate(60 -24)">{flat(fa["svg"], "#a7b0b5", .5)}</g>'
    cower = sm(t, t3 - .05, t3 + .2) * .5 + .5 * sm(t, t4 - .06, t4 + .1)
    kex = "flinch77" if t > t4 - .04 else "scared77"
    kid = PE.kid_dima(KID_HIP[0] + 10 * cower, KID_HIP[1] + 30 * cower, KID_K, kex, None, shrug=.25 + .75 * cower, flip=True,
                      lean_add=-.08 * cower + .02 * math.sin(t * 7), head_add=-.05 * cower)
    # карандаш выпадает на «слабаки» и катится по краю стола
    pr = sm(t, t4, t4 + .5)
    pen = PR.pencil(lerp(680, 520, pr), d["top"] - 10 - hop(t, t4, 40, .25), .9, -14 + 10 * math.sin(pr * 9) * (1 - pr))
    # кот под столом: прижатые уши над краем стола справа
    st = dict(flat_ears=1.0, look=(-.8, -.4), flame_e=.4, drop=.3)
    cid = lib.clip_rect(-900, -900, 3000, d["top"] + 900)
    cat = f'<g clip-path="url(#{cid})">{PE.cat_svg(1010, d["top"] + 205 + 4 * math.sin(t * 9) - 14 * kick(t, t4, .05, 5), .9, st, t)}</g>'
    eff = strokes(fa["finger"][0], fa["finger"][1], bump(t, t4 - .02, .3), 40, 70, 120, 240, 3, 7720, INK, 5)
    world = d["bg"] + shadow + kid["svg"] + fa["svg"] + d["table"] + cat + pen + eff + d["light"]
    if MASK:
        world = mask_of(kid["svg"] + fa["svg"])
    sx, sy = shake2(t, t4, 15)
    s = 1.0 + .03 * sm(t, T0("s02"), T1("s02")) + .10 * kick(t, t4, .04, 4)
    cy = 960 - 50 * sm(t, t4, T1("s02") + .2) - sy
    return wrap(world, 540 - sx - 30 * sm(t, t4, T1("s02") + .2), cy, s, 0.0, hook_title(t, T0("s04")))


# ═════════════════════════ s03: кулак у виска — «вот где сила» ═════════════════════════
FA3_HIP = (470.0, 1990.0)
FA3_K = 2.05


def s03(t):
    lib.dyn_begin()
    t5, t6, t7 = W(5), W(6), W(7)
    flash = sm(t, t7 + .05, T1("s03")) * .85
    d = R.kitchen77(t, "hook", flash=flash)
    # «без» — два стука костяшками в висок; «силы» — кулак перед лицом, сжат до дрожи; «воли» — рык
    knock = abs(math.sin(math.pi * clamp((t - t5 + .04) / .11))) * (t5 - .04 < t < t5 + .18)
    front = sm(t, t6 - .08, t6 + .1)
    shake = 4 * math.sin(t * 61) * front
    ex = dict(PE.EXPR["father77"]["hard" if t < t7 - .02 else "shout"])
    ex["flush"] = .2 + .5 * front
    ex["mous"] = .5 * math.sin(t * 27)
    fa0 = PE.father(FA3_HIP[0], FA3_HIP[1], FA3_K, ex, "temple", t, layers=("body",))
    hx, hy = fa0["head"]
    sc = fa0["scale"]
    tem = (hx - 70 * sc - 18 * sc * knock, hy + 30 * sc)
    fr_ = (hx + 150 * sc, hy + 230 * sc)
    tgt = (lerp(tem[0], fr_[0], front) + shake, lerp(tem[1], fr_[1], front) + shake * .6)
    dirv = (lerp(.25, .1, front), lerp(-1, -1, front))
    fa = PE.father(FA3_HIP[0], FA3_HIP[1], FA3_K, ex, "temple", t, arms={"n": ("ik", tgt, 1)}, hands={"n": {"kind": "fist", "dir": dirv}},
                   head_add=.03 * math.sin(t * 9) + .04 * kick(t, t7, .06, 4))
    fx, fy = fa["fist"]
    eff = strokes(fx, fy, front * (.6 + .4 * math.sin(t * 40) ** 2), 90, 60, 0, 360, 8, 7730, INK, 5)
    eff += strokes(hx - 120 * sc, hy, bump(t, t5 - .02, .2) + bump(t, t5 + .09, .2), 40, 50, 150, 230, 3, 7740, INK, 5)
    world = d["bg"] + fa["svg"] + eff + d["light"]
    sx, sy = shake2(t, t7, 8)
    tr = 6 * front * math.sin(t * 47) + 10 * sm(t, t7, T1("s03")) * math.sin(t * 53)
    s = 1.0 + .12 * sm(t, t6 - .1, t6 + .2) + .04 * sm(t, t7, T1("s03"))
    cx = lerp(540, 620, sm(t, t6 - .1, t6 + .2)) - sx + tr
    cy = lerp(960, 900, sm(t, t6 - .1, t6 + .2)) - sy
    return wrap(world, cx, cy, s, 0.0, hook_title(t, T0("s04")))


# ═════════════════════════ s04: поворот — всполох, лампа, тень съёживается ═════════════════════════
FA4_HIP = (470.0, 1400.0)
FA4_K = 1.12


def s04(t):
    tg = T0("s04")
    if t < tg - 1e-6:
        return s03(t)
    lib.dyn_begin()
    t8, t10, t11 = W(8), W(10), W(11)
    swing = 3.2 * math.sin(2 * math.pi * (t - tg) / 1.9 + .6)
    d = R.kitchen77(t, "lamp", lamp_swing=swing)
    look = sm(t, t10 - .05, t10 + .25)
    ex = dict(PE.EXPR["father77"]["look_up" if look > .5 else "tired"])
    fa = PE.father(FA4_HIP[0], FA4_HIP[1], FA4_K, ex, "slump", t, head_add=-.1 * (1 - look) + .02 * math.sin(t * 1.7))
    mug = PR.enamel_mug(R.K77_MUG[0] + 20, R.K77_MUG[1] - 66, 1.0, 0, .1, 0, t, steam=1.0)
    # тень прежнего жеста: огромный отец с поднятым пальцем на стене; с «Так» ссыхается до размеров отца и уходит за него
    u = sm(t, t8 - .05, t11 + .1)
    sk = lerp(2.6, FA4_K, u)
    sx_ = lerp(640, FA4_HIP[0] + 50, u) + 30 * math.sin(math.radians(swing)) * 10
    sy_ = lerp(1500, FA4_HIP[1] + 40, u)
    sh = PE.father_shadow(sx_, sy_, sk, "point", t=t, col="#0a0d1e", op=.55 * (1 - .5 * u), op_fill=.5 * (1 - .4 * u), w=6)
    shadow = f'<g transform="translate({sx_:.1f} {sy_:.1f}) scale(-1 1) translate({-sx_:.1f} {-sy_:.1f})">{sh["svg"]}</g>'
    lit = R.warm_tint(fa["svg"], 1.0)
    world = d["bg"] + shadow + lit + d["table"] + mug + d["dark"] + d["light"]
    s = 1.0 + .05 * sm(t, tg, T1("s04") + .2)
    rot = .5 * math.sin(2 * math.pi * (t - tg) / 1.9)
    out = wrap(world, 540 + 6 * math.sin(t * 1.3), 980, s, rot, "")
    if not (NOCAM or MASK):
        out = out[:-6] + R.glitch_flash(t, tg, 0.0) + "</svg>"
    return out


# ═════════════════════════ s10: мост — тёмный гараж, кот щёлкает выключателем ═════════════════════════
GA_K = .62


def s10(t):
    lib.dyn_begin()
    t44, t45, t48 = W(44), W(45), W(48)
    t_on = W(45) + .08                    # щелчок на «смотри»
    lit = clamp((t - t_on) / .45)
    d = R.garage77(t, lit, "wide")
    bx, by = R.GA77_BOX
    walk0 = (bx - 520, R.GA77_FL)
    jump0 = (bx - 150, R.GA77_FL)
    tj0, tj1 = t44 - .1, t44 + .35
    if t < tj0:
        u = clamp((t - (T0("s10") - .2)) / (tj0 - T0("s10") + .2))
        x = lerp(walk0[0], jump0[0], u)
        cat = PE.cat_walk(x, R.GA77_FL, GA_K, t, dict(turn=.6, look=(.6, -.3), perk=.6), period=.42)
        cp = (x, R.GA77_FL)
    elif t < tj1:
        cat = PE.cat_jump(jump0, (bx, by), GA_K, (t - tj0) / (tj1 - tj0), t, dict(turn=.6))
        cp = (bx, by)
    else:
        paw = sm(t, t_on - .25, t_on - .02) * (1 - sm(t, t_on + .25, t_on + .5))
        turn = lerp(.6, 0.0, sm(t, t48 - .2, t48 + .1))
        st = dict(paw=paw * 1.05, paw_dx=88, turn=turn, look=(lerp(.7, 0, sm(t, t48 - .2, t48 + .1)), lerp(-.5, 0, sm(t, t48 - .2, t48 + .1))),
                  perk=1.0, tail=8 * math.sin(t * 3), smile=.6 * sm(t, t48, t48 + .2), tilt=4 * bump(t, t48, .5))
        cat = PE.cat_svg(bx, by, GA_K, st, t)
        cp = (bx, by)
    sw = PR.light_switch(R.GA77_SWITCH[0], R.GA77_SWITCH[1], .8, on=lit, press=bump(t, t_on - .03, .2))
    junk = PR.garage_junk(R.GA77_JUNK[0], R.GA77_JUNK[1], .78, seed=1)
    door = PR.roll_door(R.GA77_DOOR[0], R.GA77_DOOR[1], R.GA77_DOOR_K, 0.0, 0.0, 0.0, 0.0, t)
    world = d["bg"] + door + junk + sw + cat + d["light"]
    if lit < .99:
        world += d["dark"]
        # в темноте видно глаза и огонёк кота
        fx, fy = cp[0] + (995 - 836) * GA_K, cp[1] + (1076 - 1306) * GA_K
        gl = (1 - lit) * (1 + .1 * math.sin(t * 13))
        world += blob(ellipse_pts(fx, fy - 14, 22, 34, 14), "#ff9a3c", .9 * gl) + blob(ellipse_pts(fx, fy - 10, 70, 80, 16), "#ff9a3c", .15 * gl)
        hx, hy = cp[0], cp[1] + (1072 - 1306) * GA_K
        for ex_ in (-26, 26):
            world += blob(ellipse_pts(hx + ex_ * GA_K * 1.4, hy + 6, 9, 11, 10), "#b6e86a", .85 * (1 - lit))
    cam0 = d["cam"]
    s0 = lerp(1.15, cam0[2], ease_out(clamp((t - t_on) / .6), 3))
    cx = lerp(bx - 260, cam0[0], ease_out(clamp((t - t_on) / .6), 3)) + 20 * (t - T0("s10"))
    cy = lerp(1080, cam0[1], ease_out(clamp((t - t_on) / .6), 3))
    s = s0 * (1 + .03 * sm(t, t_on + .6, T1("s10") + .2))
    return wrap(world, cx, cy, s, 0.0, "")


# ═════════════════════════ s20: петля — тот же стол, тёплый свет, хохот ═════════════════════════
DI20_HIP = (1120.0, 1400.0)
DI20_K = 1.1
CAT20 = (835.0, 1166.0)


def s20(t):
    lib.dyn_begin()
    t97, t99, t101 = W(97), W(99), W(101)
    slap = stress(97, .35)
    bounce = 8 * kick(t, slap, .025, 14)
    d = R.kitchen77(t, "warm", bounce=bounce)
    pu = clamp(.6 + .4 * math.sin(2 * math.pi * 2.4 * t)) if t < slap - .15 else 1 - bump(t, slap - .02, .2)
    ex = dict(PE.EXPR["father77"]["laugh"])
    ex["open"] = .8 + .2 * math.sin(t * 19)
    fa = PE.father(FA_HIP[0], FA_HIP[1], FA_K, ex, ("slap_up", "slap"), t, u=pu, head_add=-.12 - .04 * math.sin(t * 14),
                   lean_add=-.05 + .03 * math.sin(t * 14))
    mug = PR.enamel_mug(MUG0[0] - 40, MUG0[1] - 66 - bounce - hop(t, slap, 30, .22), 1.0, 6 * math.sin(math.pi * clamp((t - slap) / .22)), 0, 0, t,
                        steam=.6)
    lean_in = ease_out(clamp((t - t99 + .25) / .45), 3)
    di = PE.dima77(DI20_HIP[0] + 260 * (1 - lean_in), DI20_HIP[1], DI20_K, "laugh77", "di_laugh", t, lean_add=.25 * lean_in + .03 * math.sin(t * 13),
                   flip=True)
    perk = sm(t, t101 - .2, t101 + .1)
    st = dict(perk=.6 + .4 * perk, look=(-.5, -.2), squint=.6 * perk, smile=1.0, flame_e=1.4, tail=10 * math.sin(t * 4), tilt=4 * math.sin(t * 3),
              sy=1 - .06 * kick(t, slap, .03, 7))
    cat = PE.cat_svg(CAT20[0], CAT20[1] - bounce, CAT_K, st, t)
    world = d["bg"] + di["svg"] + fa["svg"] + d["table"] + mug + cat + d["light"]
    s = 1.0 + .05 * kick(t, slap, .04, 4) + .015 * math.sin(t * 6)
    return wrap(world, 540 + 5 * math.sin(t * 5), 960 + 4 * math.sin(t * 7), s, .4 * math.sin(t * 5), "")


def frame(sid, t):
    return {"s01": s01, "s02": s02, "s03": s03, "s04": s04, "s10": s10, "s20": s20}[sid](t)
