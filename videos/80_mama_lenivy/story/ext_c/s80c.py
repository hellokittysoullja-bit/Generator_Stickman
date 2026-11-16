"""Рилс 80 «Мама была права», группа C — хук, поворот, Оттава, вечер, петля: s01, s02, s03, s12, s15, s18.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Всё время — из shots.json (t0/t1) и voice/words.json (слова по индексу wN),
секунды в коде — только длительности движений. Места — common/room.py (раздел 80), люди — common/people.py (dima80, accuser_shadow,
scientist80), кот — через people.cat_* / common/cat.py, предметы — common/props.py, надпись хука — common/hand_text.py.
Букв и цифр нет, кроме «Ты ленивый?» (s01–s02). NOCAM=1 — без камеры и без надписи (замер движения рисунка), MASK=1 — силуэт
рисунка хука (тень мамы, Дима, бирка) для замера заполнения."""
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
HOOK_TEXT = json.load(open(os.path.join(STORY, "reel.json"))).get("hook_screen", "Ты ленивый?")
NOCAM = bool(os.environ.get("NOCAM"))
MASK = bool(os.environ.get("MASK"))


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
        return lib.svg(f'<g transform="{lib.cam(540, 960, 1.0)}">{world}</g>')
    if MASK:
        return lib.svg(f'<g transform="{lib.cam(cx, cy, s, rot)}">{world}</g>')
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, rot)}">{world}</g>{over}')


def hook_cam(t, t_hit, t_hit2, rot0=-3.6, side0=-52.0, fly=.2, far=1.46, over=.065):
    """Влёт правил 28/29 (не слабее эталона 17): масштаб 1/far → 1 за fly с без разгона, перелёт over с отскоком, поворот rot0 с
    возвратом, боковой занос side0; удар +4 % на t_hit и +10 % на t_hit2. -> (множитель масштаба, поворот, занос, доля полёта 0…1)."""
    u = clamp(t / fly)
    e = ease_out(u, 3)
    s = 1 / far + (1 - 1 / far) * e
    if t > fly:
        s += over * math.exp(-7 * (t - fly)) * math.cos(2 * math.pi * 2.2 * (t - fly))
    rot = rot0 * (1 - e) + damp(t, fly, 1.3, 2.0, 6.0)
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


def mask_fill(svg_):
    """MASK=1: всё нарисованное — чистый синий на белом (замер заполнения)."""
    fid = lib.uid("mk")
    lib.DEFS.append(f'<filter id="{fid}"><feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 9 0"/></filter>')
    return '<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>' + f'<g filter="url(#{fid})">{svg_}</g>'


# ═════════════════════════ надпись хука «Ты ленивый?» (экранные координаты, s01–s02) ═════════════════════════
HOOK_SIZE = 1.2
HOOK_Y = 340.0              # линия строки: буквы ≈ 225…340; ниже — тень мамы (верх ≥ 370 после влёта, замер MASK)


def hook_title(t, t_end):
    """Пишется с 0.00 за 0.30 с (маркер-росчерк), целиком к 0.35; стоит до склейки поворота t_end и гаснет на ней."""
    if t >= t_end or NOCAM or MASK:
        return ""
    w = text_width(HOOK_TEXT, HOOK_SIZE)
    x0 = (1080 - w) / 2 - 30          # наклон 13° уводит верх букв вправо — строку чуть левее центра
    return hand_text(HOOK_TEXT, t, 0.0, .30, x0, HOOK_Y, HOOK_SIZE, ink="#1b1530", bold=1.9)


# ═════════════════════════ хук: тень мамы, бирка-гиря на шее Димы ═════════════════════════
FL = R.W80_FL
D_X = 700.0                 # Дима-подросток стоит (таз по x)
D_K = .64                   # масштаб взрослого; подросток = age 0 → ×0.8
M_X = 300.0                 # тень мамы: таз по x
M_K = .71                   # тень огромная (выше потолка кадра не уходит: голова ≈ 470)
TAG_K = .55


def lamp_off(t):
    """Лампа качается по эллипсу (скорость не обнуляется): смещение (dx, dy) света; тени едут в обратную сторону."""
    w = 2 * math.pi * 1.15
    return 46 * math.cos(w * t + .6), 20 * math.sin(w * t + .6)


def _tag_land(sid_t0=0.0):
    return stress(2, .4)                       # ударное «ВА» «права» — бирка с лязгом падает на шею


def hook_state(t):
    """Хореография хука s01–s02: возвращает dict позы Димы, бирки, тени. Удары: w0 «Мама», w2 «пра-ВА», w3 «ты», w4 «просто», w5 «ле-НИ-вый»."""
    tl = _tag_land()
    t3, t4, t5 = W(3), W(4), stress(5, .4)
    # тень мамы: указка в замахе с кадра 0, выпад на «Мама», второй тычок на «ты» (в лоб), нависает на «ленивый»
    jab = .55 + .2 * math.sin(2 * math.pi * 2.4 * t + 1.9)          # кадр 0 — уже в движении замаха
    jab = jab * (1 - sm(t, W(0) - .1, W(0))) + sm(t, W(0) - .1, W(0) + .04)
    jab -= .55 * sm(t, W(0) + .2, W(1) + .1) - .55 * sm(t, t3 - .12, t3 + .02)        # отвод и тычок в лоб на «ты»
    jab -= .35 * sm(t, t3 + .25, t4 + .1)
    jab += .3 * sm(t, t5 - .15, t5)
    stretch = 1 + .04 * kick(t, W(0), .06, 4) + .05 * kick(t, t3, .05, 5) + .05 * sm(t, t4, t5 + .1)
    # Дима: стоит → под весом оседает (s01) → на колени на «просто» → лицом к полу на «ленивый»
    sag = sm(t, tl, tl + .22)
    kneel = sm(t, t4 - .05, t4 + .22)
    crush = sm(t, t5 - .12, t5 + .06)
    return dict(jab=clamp(jab, 0, 1.15), stretch=stretch, sag=sag, kneel=kneel, crush=crush, tl=tl)


def dima_hook(t, st):
    """Дима-подросток под гирей. Возвращает fig (people.dima80) и точку шеи."""
    sag, kneel, crush, tl = st["sag"], st["kneel"], st["crush"], st["tl"]
    jolt = 26 * kick(t, tl, .04, 6)                                           # бирка ударила — рывок вниз
    flinch = kick(t, W(0), .05, 6) + kick(t, W(3), .05, 6)
    if kneel < .5:
        hy0 = PE.hip_on_floor(FL, D_K, 0.0)
        hy = hy0 + 40 * sag + jolt + 30 * kneel
        feet = PE.stand_kw(D_X, hy0, D_K * PE.age_k(0.0), "dima")["feet"]
        pose = ("d80_stand", "d80_sag")
        u = clamp(sag * .95 + .05 * math.sin(t * 9))
        expr = "hit80" if (flinch > .3 or (t > tl and t < tl + .25)) else ("heavy80" if sag > .5 else "teen80")
        fig = PE.dima80(D_X - 10 * sag, hy, D_K, expr, pose, t, u=u, age=0.0, feet=feet, lean_add=-.04 * flinch,
                        head_add=.08 * flinch)
    else:
        sc = D_K * PE.age_k(0.0) * PE.HEIGHT["dima"]
        hy = FL - 330 * sc + 10 * crush + jolt * .3
        kw = PE.kneel_kw(D_X, hy, D_K, "dima", 0.0)
        pose = ("d80_grab", "d80_kneel_down") if crush > .01 else "d80_grab"
        expr = "crush80" if crush > .4 else "heavy80"
        fig = PE.dima80(D_X, hy, D_K, expr, pose, t, u=crush, age=0.0, feet=kw["feet"], lean_add=.18 * crush, head_add=.25 * crush)
    return fig


def tag_now(t, fig, st):
    """Бирка: до удара летит к шее (кадр 0 — уже в полёте, крутится, шнур хлещет), на «ВА» садится и раскачивается под весом."""
    nx, ny = fig["neck"]
    tl = st["tl"]
    if t < tl:
        u = clamp(t / tl)
        e = 1 - (1 - u) ** 1.4                                                # без разгона с нуля: летит с кадра 0
        sx, sy = nx - 480, ny + 40
        x = lerp(sx, nx, e)
        y = lerp(sy, ny, e) - 130 * math.sin(math.pi * e) * (1 - .5 * e)
        swing = lerp(-210, 0, e) + 25 * math.sin(t * 21)
        return dict(x=x, y=y, swing=swing, on=False)
    sw = damp(t, tl, 24, 1.6, 2.6) + 4 * math.sin(t * 2.7)
    if st["kneel"] > .01:      # на коленях бирка тянет вниз к полу: шнур натянут, бирка у пола
        sw = sw * (1 - st["kneel"]) + 8 * math.sin(t * 3.1) * st["kneel"]
    return dict(x=nx, y=ny, swing=sw, on=True)


def hook_world(t, close=False):
    st = hook_state(t)
    d = R.hook_wall(t)
    ox, oy = lamp_off(t)
    tx, ty, tk = R.shadow_tremble(t)
    # тень мамы на стене: едет против лампы, дрожит, вытягивается вверх на ударах
    fig = dima_hook(t, st)
    hd = fig["head"]
    aim = (hd[0] - 20, hd[1] - 30)
    sh = PE.accuser_shadow("mama", M_X, PE.hip_on_floor(FL, M_K), M_K, st["jab"], t, col="#2a2230", op=.86, blur_sd=3.0, aim=aim, reach=1.15)
    sx = 1 + tk + (st["stretch"] - 1) * .4
    sy = st["stretch"] + tk
    shadow = (f'<g transform="translate({-ox * .6 + tx:.2f} {-oy * .3 + ty:.2f}) translate({M_X:.1f} {FL:.1f}) scale({sx:.4f} {sy:.4f}) '
              f'translate({-M_X:.1f} {-FL:.1f})">{sh["svg"]}</g>')
    # тень самого Димы на стене (маленькая, сзади), тоже от лампы
    dshadow = R.wall_shadow(f'<g transform="translate({60 - ox * .4:.1f} {-12 - oy * .2:.1f})">{fig["svg"]}</g>', .35, "#2a2230", 4)
    # свет лампы на стене качается: смещаем всю стену с пятном (пол и плинтус на месте — они в том же слое, но край пятна резкий)
    wall = f'<g transform="translate({ox:.2f} {oy:.2f})">{d["bg"]}</g>'
    tg = tag_now(t, fig, st)
    cord_on = True
    tag = PR.iron_tag(tg["x"], tg["y"], TAG_K, tg["swing"], seed=1, t=t, cord_on=cord_on)
    tag_back = PR.iron_tag(tg["x"], tg["y"], TAG_K, tg["swing"], seed=1, t=t, layer="cord") if tg["on"] else ""
    eff = ""
    tl = st["tl"]
    a = bump(t, tl - .01, .32)                       # лязг: штрихи удара у бирки и пыль у ног
    if a > .01:
        cx_, cy_ = PR.iron_tag_center(tg["x"], tg["y"], TAG_K, tg["swing"])
        for j in range(6):
            ang = math.radians(-180 + 36 * j)
            r0, r1 = 120, 120 + 90 * a
            eff += line([(cx_ + r0 * math.cos(ang), cy_ + r0 * math.sin(ang)), (cx_ + r1 * math.cos(ang), cy_ + r1 * math.sin(ang))], 6, INK,
                        seed=8051 + j, op=min(1, 2 * a))
    for t_d, amp in ((tl + .05, 1.0), (W(4) + .1, 1.2)):
        e = clamp((t - t_d) / .6)
        if 0 < e < 1:
            for j in range(5):
                px = D_X - 160 + 80 * j + 30 * e * (j - 2)
                eff += blob(ellipse_pts(px, FL - 18 - 50 * e * (1 + .3 * (j % 2)), (26 + 50 * e) * amp, (16 + 22 * e) * amp, 12), "#d9cbb3", .75 * (1 - e) ** 1.5)
    # штрихи веса под биркой (тянет к полу)
    if tg["on"] and t > tl + .1:
        cx_, cy_ = PR.iron_tag_center(tg["x"], tg["y"], TAG_K, tg["swing"])
        wv = .6 + .4 * math.sin(t * 17)
        for j in range(3):
            xx = cx_ - 50 + 50 * j
            eff += line([(xx, cy_ + 100), (xx + 3, cy_ + 150 + 30 * wv)], 5, INK, taper=.7, seed=8061 + j, op=.75)
    # трещины пола на «ленивый»
    cr = sm(t, stress(5, .4) - .05, stress(5, .4) + .2)
    if cr > .01:
        for j, (dx, dy) in enumerate(((-260, 40), (-120, 90), (60, 70), (200, 50), (300, 110))):
            p0 = (D_X - 40 + .2 * dx, FL + 8)
            eff += line([p0, (p0[0] + .5 * dx * cr, p0[1] + .4 * dy * cr + 10), (p0[0] + dx * cr, p0[1] + dy * cr)], 4.5, INK, taper=.6, seed=8070 + j)
    if MASK:
        world = mask_fill(shadow + tag_back + fig["svg"] + tag)
    else:
        world = wall + d["front"] + shadow + dshadow + tag_back + fig["svg"] + tag + eff + d["shade"]
    return world, fig, st


def s01(t):
    lib.dyn_begin()
    world, fig, st = hook_world(t)
    kk, rc, side, fl = hook_cam(t, W(0), stress(2, .4))
    sx1, sy1 = shake2(t, W(0), 8)
    sx2, sy2 = shake2(t, stress(2, .4), 14)
    cx = 540 + side - sx1 - sx2 + 4 * math.sin(t * 2.1)
    cy = 935 - sy1 - sy2
    s = 1.03 * kk * (1 + .02 * sm(t, .5, 1.6))
    over = hook_title(t, T1("s02"))
    blur = radial_blur(world, cx, cy, s, rc, fl)
    return wrap(world, cx, cy, s, rc, blur + over)


def s02(t):
    lib.dyn_begin()
    world, fig, st = hook_world(t, close=True)
    t5 = stress(5, .4)
    hd = fig["head"]
    u = sm(t, T0("s02") - .2, T1("s02"))
    cx = lerp(610, 650, u)
    cy = lerp(895, 905, u)
    s = 1.08 * (1 + .04 * u + .10 * kick(t, t5, .04, 4) + .03 * kick(t, W(3), .04, 5))
    sx, sy = shake2(t, t5, 16)
    sx3, sy3 = shake2(t, W(4) + .1, 7)
    return wrap(world, cx - sx - sx3, cy - sy - sy3, s, 0.0, hook_title(t, T1("s02")))


# ═════════════════════════ s03: поворот — всполох, темнота, тени-обвинители ═════════════════════════
ACC = (("mama", 7, 220.0, .74, False), ("teacher", 8, 470.0, .8, False), ("aunt", 9, 890.0, .76, True))


def s03(t):
    tg = T0("s03")
    if t < tg - 1e-6:
        return s02(t)
    lib.dyn_begin()
    reveal = sm(t, W(6) - .05, W(6) + .35)
    d = R.turn_dark(t, reveal)
    pcx, pcy, prx, pry = d["anchors"]["pool"]
    # Дима посередине, на коленях с биркой, съёживается на каждой новой тени
    sc = D_K * PE.age_k(0.0) * PE.HEIGHT["dima"]
    cow = sum(kick(t, W(i), .05, 5) for _, i, *_ in ACC)
    hy = FL - 330 * sc + 8 * cow + 6 * math.sin(t * 2.6)
    kw = PE.kneel_kw(540, hy, D_K, "dima", 0.0)
    fig = PE.dima80(540, hy, D_K, "cower80", "d80_grab", t, age=0.0, feet=kw["feet"], lean_add=.06 * cow - .04, head_add=-.1 * cow)
    nx, ny = fig["neck"]
    tag = PR.iron_tag(nx, ny, TAG_K, 4 * math.sin(t * 2.2) + damp(t, W(7), 6, 2, 4), seed=1, t=t)
    dima = R.cold_tint(R.cold_tint(fig["svg"] + tag, 1.0, 1.0), 0.0, .55)
    # тени проступают одна за другой и тычут в Диму (в голову)
    shadows = ""
    hd = fig["head"]
    for kind, wi, x, k, fl in ACC:
        a = sm(t, W(wi) - .06, W(wi) + .14)
        if a <= .005:
            continue
        jab = .25 + .75 * sm(t, W(wi), W(wi) + .12) + .08 * math.sin(t * 7 + wi)
        hip = PE.hip_on_floor(FL, k)
        sh = PE.accuser_shadow(kind, x, hip, k, jab, t, col=R.T80_SHADOW, op=.92 * a, blur_sd=3.5, flip=fl, aim=(hd[0], hd[1] - 20), reach=1.1)
        grow = 1 + .06 * (1 - a)
        shadows += (f'<g transform="translate({x:.1f} {FL:.1f}) scale({grow:.4f}) translate({-x:.1f} {-FL:.1f})">{sh["svg"]}</g>')
    wc = lib.clip_rect(-900, -900, 2880, FL + 906)        # тени — только на стене, не на полу
    world = d["bg"] + f'<g clip-path="url(#{wc})">{shadows}</g>' + dima + d["shade"]
    # всполох-сбой 2 кадра, затем тьма тает к «Так»
    if t < tg + 2 / 30:
        cover = 1.0
    else:
        cover = (1 - reveal) * .95
    if cover > .003:
        world += f'<rect x="-900" y="-900" width="2880" height="3720" fill="#03050c" opacity="{cover:.3f}"/>'
    s = 1.18 * (1 + .01 * math.sin(t * .9) + sum(.035 * kick(t, W(i), .05, 4) for _, i, *_ in ACC))
    cx = 540 + 6 * math.sin(t * 1.1)
    cy = 900 + 4 * math.sin(t * .8)
    over = R.glitch_flash(t, tg, 0.0) if t < tg + 2 / 30 else ""
    return wrap(world, cx, cy, s, 0.0, over)


# ═════════════════════════ s12: зимняя Оттава — учёные у окна, канал, тетрадь ═════════════════════════
SKATERS = ((420.0, 1300.0, .085, 60.0, "friend", False), (760.0, 1250.0, .075, -45.0, "pal", True), (1060.0, 1420.0, .1, 80.0, "friend", False),
           (1450.0, 1230.0, .07, -55.0, "pal", True), (1250.0, 1350.0, .085, -70.0, "friend", True))
NOTE = (-95.0, 812.0)            # центр открытой тетради на столе за окном (мир)


def _skater(x, y, k, t, who, flip, seed):
    ph = t * 2.6 + seed
    sw = math.sin(ph)
    arms = {"f": ("ang", 0.9 + .4 * sw, 0.3), "n": ("ang", -0.6 - .4 * sw, 0.3)}
    fig = PE.figure(who, x, y, k, None, lean=.22, arms=arms, feet=PE.stand_kw(x, y, k, who, spread=90 + 40 * sw)["feet"], flip=flip)
    return fig["svg"]


def maple_leaf(x, y, k, rot, col="#d2452c"):
    """Кленовый лист: пять лопастей с зубцами, черешок, прожилки."""
    pts = []
    lob = [(0, -100), (22, -58), (60, -72), (50, -30), (92, -20), (56, 6), (70, 40), (20, 22), (8, 60), (0, 40)]
    full = lob + [(-a, b) for a, b in lob[::-1][1:-1]]
    for a, b in full:
        pts.append(lib.T([(a * k, b * k)], x, y, 1, rot)[0] if False else (x + (a * math.cos(math.radians(rot)) - b * math.sin(math.radians(rot))) * k,
                                                                       y + (a * math.sin(math.radians(rot)) + b * math.cos(math.radians(rot))) * k))
    def P(a, b):
        c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        return (x + (a * c - b * s_) * k, y + (a * s_ + b * c) * k)
    inner = line([P(0, 40), P(0, -80)], 2.4, "#8e2414", taper=.5, seed=8811) + line([P(0, 10), P(60, -55)], 2, "#8e2414", taper=.6, seed=8812) \
        + line([P(0, 10), P(-60, -55)], 2, "#8e2414", taper=.6, seed=8813)
    return shape(pts, col, inner, w=3.0, seed=8810) + line([P(0, 40), P(4, 90)], 4, "#7a3a1c", taper=.3, seed=8814)


def notebook(x, y, k, t, u):
    """Открытая тетрадь (без букв): две страницы с бледными линейками; u 0…1 — перо рисует облачко и убегающую от него фигурку."""
    o = [shape(rect_pts(x - 120 * k, y - 60 * k, x + 120 * k, y + 60 * k), "#f6f1e4",
               "".join(line([(x - 110 * k, y - 40 * k + 18 * k * j), (x + 110 * k, y - 40 * k + 18 * k * j)], 1.2, "#a9c2d8", taper=0, wmin=1,
                            seed=8820 + j, op=.7) for j in range(6))
               + line([(x, y - 60 * k), (x, y + 60 * k)], 2.2, "#b8ab92", taper=0, wmin=1, seed=8827), w=3.0, seed=8828)]
    if u > .01:
        # облачко на правой странице: волнистый контур дорисовывается по u
        cx, cy = x + 62 * k, y - 8 * k
        n = 24
        m = max(2, int(n * clamp(u / .55)))
        pts = [(cx + (30 + 6 * math.sin(i * 1.9)) * k * math.cos(2 * math.pi * i / n), cy + (18 + 4 * math.sin(i * 2.3)) * k * math.sin(2 * math.pi * i / n))
               for i in range(m + 1)]
        o.append(line(pts, 2.6, "#2a2a3a", taper=.2, wmin=.5, seed=8830))
        # фигурка палочками бежит влево от облачка
        v = clamp((u - .5) / .45)
        if v > .01:
            fx, fy = x - 40 * k, y + 2 * k
            parts = [[(fx, fy - 26 * k), (fx - 4 * k, fy)], [(fx - 4 * k, fy), (fx - 18 * k, fy + 20 * k)], [(fx - 4 * k, fy), (fx + 12 * k, fy + 18 * k)],
                     [(fx - 2 * k, fy - 18 * k), (fx - 20 * k, fy - 8 * k)], [(fx - 2 * k, fy - 18 * k), (fx + 16 * k, fy - 26 * k)]]
            nn = max(1, int(len(parts) * v + .999))
            for j, pp in enumerate(parts[:nn]):
                o.append(line(pp, 2.6, "#2a2a3a", taper=.2, wmin=.5, seed=8840 + j))
            o.append(f'<circle cx="{fx + 2 * k:.1f}" cy="{fy - 34 * k:.1f}" r="{7 * k:.1f}" fill="none" stroke="#2a2a3a" stroke-width="2.6"/>')
            if v > .7:
                for j in range(3):
                    o.append(line([(fx + 22 * k, fy - 18 * k + 10 * k * j), (fx + 36 * k, fy - 18 * k + 10 * k * j)], 2, "#2a2a3a", taper=.5, seed=8850 + j))
    return "".join(o)


def s12(t):
    lib.dyn_begin()
    d = R.ottawa(t)
    an = d["anchors"]
    wx0, wy0, wx1, wy1 = an["uni_win"]
    t61, t63, t66 = W(61), W(63), W(66)
    # внутри окна: тёплая комната, стол, два учёных над тетрадью
    room = [blob(rect_pts(wx0 - 20, wy0 - 20, wx1 + 20, wy1 + 20), "#e9b878")]
    room.append(blob(rect_pts(wx0, wy0 + 40, wx0 + 110, wy1), "#b07a4a", .8))                      # шкаф с корешками без букв
    for j in range(4):
        yy = wy0 + 110 + 95 * j
        room.append(line([(wx0, yy), (wx0 + 110, yy)], 4, "#6a4428", taper=0, wmin=1, seed=8860 + j))
        for i in range(5):
            room.append(blob(rect_pts(wx0 + 8 + 20 * i, yy - 70 + 6 * (i % 2), wx0 + 24 + 20 * i, yy - 2), ["#7a3b30", "#3f5a6e", "#8a7a3a"][(i + j) % 3], .9))
    lean_b = .12 * sm(t, t66 - .2, t66 + .1)
    sa = PE.scientist80("a", wx0 + 120, 905.0, .3, "point" if t > t61 else "rest", t, "talk" if t < t66 else "ah", lean_add=.04 * math.sin(t * 1.7))
    sb = PE.scientist80("b", wx1 - 60, 905.0, .3, "write" if t > t66 - .3 else "point", t, "ah" if t > t66 + .3 else "focus", flip=True, lean_add=lean_b)
    nu = sm(t, t66 - .05, t66 + .7)
    table = shape(rect_pts(wx0 - 10, 832, wx1 + 10, wy1 + 10), "#8a5a34", blob(rect_pts(wx0 - 10, 832, wx1 + 10, 842), "#a8744a"), w=3.0, seed=8870)
    nb = notebook(NOTE[0], NOTE[1] + 6, .62, t, nu)
    inside = "".join(room) + sa["svg"] + sb["svg"] + table + nb
    # перо в руке учёного b бежит по тетради
    if t > t66 - .3:
        hx, hy = sb["hold"]
        inside += line([(hx, hy), (hx - 10, hy + 26)], 4, "#1f2a4a", taper=0, wmin=1, seed=8871)
    win = f'<g clip-path="url(#{an["win_clip"]})">{inside}</g>'
    sk = "".join(_skater(x + v * (t - 22.0), y, k, t, who, fl, i * 1.3) for i, (x, y, k, v, who, fl) in enumerate(SKATERS))
    # кленовый лист кружит над каналом
    lu = clamp((t - (T0("s12") - .2)) / 2.4)
    lx = 760 + 380 * lu + 90 * math.sin(t * 3.1)
    ly = 640 + 520 * lu + 30 * math.sin(t * 4.3)
    leaf = maple_leaf(lx, ly, 1.3, 60 * t + 25 * math.sin(t * 2.7))
    pb0 = sm(t, W(66) - .3, W(66) - .02)
    world = d["bg"] + sk + win + f'<g opacity="{1 - .85 * pb0:.3f}">{d["front"]}</g>' + leaf + d["snow"]
    # камера: окно (Учёные) → проезд над каналом (Канаде) → тетрадь крупно (пишут)
    A = (-110.0, 720.0, 1.85)
    B = (860.0, 1020.0, 1.02)
    C = (NOTE[0] + 5, NOTE[1] - 70, 2.7)
    pa = sm(t, t63 - .18, t63 + .3)
    pb = sm(t, t66 - .3, t66 - .02)
    cx = lerp(lerp(A[0], B[0], pa), C[0], pb)
    cy = lerp(lerp(A[1], B[1], pa), C[1], pb) - 40 * bump(t, t63 - .1, .5)
    s = lerp(lerp(A[2] * (1 + .04 * sm(t, T0("s12"), t63)), B[2], pa), C[2], pb)
    whip = 1 - sm(t, T0("s12") - .2, T0("s12") + .12)
    cx -= 260 * whip
    return wrap(world, cx, cy, s * (1 + .03 * kick(t, t61, .05, 5)))


# ═════════════════════════ s15: вечер — облачко снова, Дима спокойно кивает ему ═════════════════════════
# Комната стола — группы A (s80a.desk_room, A.seated), как у s09/s11/s16/s17: тот же стол, лампа, окно; s15 кончается позой начала s16
# (ладонь на груди, облачко над головой, мимика yes80).
def _A():
    sys.path.insert(0, os.path.join(STORY, "ext_a"))
    import s80a
    return s80a


def s15(t):
    lib.dyn_begin()
    A = _A()
    t0, t1 = T0("s15"), T1("s15")
    t81, t83, t84 = W(81), W(83), stress(84, .3)
    bg, desk = A.desk_room(t, "evening")
    DX, DY = A.DESK_X, A.DESK_Y
    SX, SY = DX - 120, DY - 72
    hx, hy = A.HIP
    k = A.SC
    # садится: таз опускается на стул к «Поэтому»
    sit_u = ease_out(clamp((t - (t0 - .2)) / (W(80) + .1 - (t0 - .2))), 2)
    dy_ = -90 * (1 - sit_u) + 8 * kick(t, W(80) + .1, .06, 5)
    palm = sm(t, t83 - .2, t83 + .1)
    rest_n = (SX + 150, SY - 60)
    chest = (hx + 215 * k, hy - 225 * k)
    tgt = (lerp(rest_n[0], chest[0], palm), lerp(rest_n[1], chest[1], palm) + dy_)
    arms = {"n": ("ik", tgt, -1), "f": ("ik", (SX + 70 + 4 * math.sin(t * 2), SY - 105 + .3 * dy_), -1)}
    hn = {"dir": (-.75, -.45), "curl": (.05, .05, .1, .15), "spread": .1, "thumb": .1} if palm > .5 else {"curl": (.4, .45, .5, .55), "thumb": .4, "dir": (.85, .5)}
    hands = {"n": hn, "f": {"curl": (.35, .4, .45, .5), "thumb": .35, "dir": (.9, .55)}}
    nod = .16 * bump(t, t84 - .06, .32) + .1 * bump(t, t84 + .26, .3)
    look_up = sm(t, t81, t83)
    if t < t81 + .05:
        expr = dict(PE.EXPR["dima"]["det80"])
    elif t < t83 - .1:
        expr = dict(PE.EXPR["dima"]["gloom80"], look=(.3, -.6))
    elif t < t84 - .1:
        expr = dict(PE.EXPR["dima"]["calm80"])
    else:
        expr = dict(PE.EXPR["dima"]["yes80"])
    head = -.12 * look_up + nod
    kw = dict(y=hy + dy_)
    fig_b = A.seated(t, expr, "write", .06, head, layers=("legs", "pelvis"), **kw)
    fig = A.seated(t, expr, "write", .06, head, arms=arms, hands=hands, layers=("arm_f", "body"), **kw)
    arm = A.seated(t, expr, "write", .06, head, arms=arms, hands=hands, layers=("arm_n",), **kw)
    lamp = PR.lamp_desk(DX + 300, DY - 130, 1.0, on=1.0, seed=17)
    sheets = PR.scribble_sheet(SX, SY, 1.2, 0.0, -4, seed=172, w=240, h=320, sy=.6)
    pen_svg = PR.pen(SX + 250, SY + 30, .62, 80, seed=17)
    # облачко набухает над головой на «теперь» (как в s09), на «себе» отвечает кивку — чуть съёживается
    hd = fig["head"]
    g = sm(t, t81 - .05, t81 + .35)
    cl = PR.gloom_cloud(hd[0] + 30 + 8 * math.sin(t * 1.4), hd[1] - 250 + 6 * math.sin(t * 2.1) + 14 * bump(t, t84, .4), 1.15, t,
                        rain=.25, shrink=.12 * bump(t, t84, .5), seed=17, grow=g)
    # кот на подоконнике смотрит на Диму; на кивке моргает и чуть наклоняет голову
    cat = PE.cat_svg(150.0, 872.0, .46, dict(look=(.8, .3), tail=6 * math.sin(t * 2.1), flame_e=1.0, blink=bump(t, t84 + .1, .2),
                                              tilt=-5 * sm(t, t83, t84)), t)
    marks = ""
    uu = (t - t84) / .35
    if 0 < uu < 1:
        for j in range(2):
            x0 = hd[0] + 150 + 18 * j
            marks += line([(x0, hd[1] - 30 + 30 * uu), (x0 + 6, hd[1] + 10 + 30 * uu)], 5 * (1 - uu) + 1, INK, taper=.6, wmin=.2, seed=8890 + j, op=.7 * (1 - uu))
    world = (bg + cat + A.chair(hx, hy + 20 + dy_) + fig_b["svg"] + desk + lamp + sheets + pen_svg + fig["svg"] + arm["svg"] + cl + marks
             + PR.glow(DX + 160, DY - 90, 420, .55, "#FFD98A"))
    pu = ease_io(clamp((t - (t0 - .2)) / (t1 - t0 + .4)))
    s = lerp(1.0, 1.1, pu) * (1 + .02 * bump(t, t84, .4))
    return A.frame_svg(world, lerp(580, 540, pu), lerp(900, 880, pu), s, -.3 * math.sin(t * 1.1))


# ═════════════════════════ s18: петля — тот же ракурс и свет, на стене огромная тень кота ═════════════════════════
L_DIMA = (560.0, 1265.0)          # таз сидящего за столом Димы (лицом вправо, пишет); ниже — передняя стенка стола
L_CAT = (330.0, 1124.0, .8)       # кот сидит на столе между лампой и Димой, у его спины
L_LAMP = (95.0, 1120.0, 1.3)     # настольная лампа (дно)


def s18(t):
    lib.dyn_begin()
    t0, t1 = T0("s18"), T1("s18")
    t93, t94, t95, t97, t98 = W(93), W(94), W(95), W(97), W(98)
    d = R.hook_wall(t, warm=1.0, desk=True)
    dy = d["anchors"]["desk_y"]
    # Дима пишет: ручка бежит по листу, без бирки
    hx, hy = L_DIMA
    wr = math.sin(t * 8.5)
    ex = dict(PE.EXPR["dima"]["write80"])
    ex["closed"] = bump(t, t95 + .1, .18)
    kw = dict(lean_add=.04 + .01 * wr, head_add=.04 * math.sin(t * 1.6) - .06 * bump(t, t95 - .1, .5))
    fig = PE.dima80(hx, hy, 1.0, ex, "d80_pen", t, age=1.0, **kw)
    ph = fig["hold"]
    pen = PR.pen(ph[0] + 6 + 8 * wr, ph[1] + 24, .55, -25 + 6 * wr, seed=18)
    sheet = PR.scribble_sheet(ph[0] + 40, dy + 4, .8, clamp(.35 + .6 * (t - t0) / (t1 - t0)), rot=0, seed=18, sy=.3)
    # кот усаживается на «кот», прислоняется к Диме на «сидит … рядом», огонёк теплеет на «тоска уходит»
    cx_, cy_, ck = L_CAT
    settle = damp(t, t93 - .05, .07, 2.2, 4.5)
    lean = 9 * sm(t, t94 - .05, t95 + .1)
    warm = 1.0 + .7 * sm(t, t97, t98 + .3)
    st = dict(look=(-.3, -.1) if t < t94 else (.7, -.5), tail=8 * math.sin(t * 2.0), flame_e=warm, blink=bump(t, t95 + .25, .2),
              tilt=6 * sm(t, t94, t95), ear=5 * bump(t, t93 + .1, .3))
    cat = PE.cat_svg(cx_, cy_, ck, st, t)
    cat = (f'<g transform="translate({cx_:.1f} {cy_:.1f}) rotate({lean:.2f}) scale({1 + settle:.4f} {1 - settle:.4f}) '
           f'translate({-cx_:.1f} {-cy_:.1f})">{cat}</g>')
    # огромная мягкая тень кота на стене — от лампы слева, тот же свет, что у тени мамы в хуке
    lx, ly, lk = L_LAMP
    ox, oy = lamp_off(t)
    px, py = lx + 40, dy - 60
    sc = 2.25 + .05 * math.sin(t * 1.3)
    shx, shy = 440.0 + .15 * ox, 700.0 + .1 * oy          # куда на стене ложится середина тени (выше головы Димы)
    shadow = R.wall_shadow(f'<g transform="translate({shx:.1f} {shy:.1f}) scale({sc:.3f}) translate({-cx_:.1f} {-(cy_ - 130 * ck):.1f})">{cat}</g>',
                           .42, "#5a3a24", 9)
    dshadow = ""
    lamp = PR.lamp_desk(lx, dy + 6, lk, on=1.0, seed=18)
    glow = f'<g {lib.blur(26)}>' + blob(ellipse_pts(lx + 30, dy - 120, 180, 120, 18), "#ffd890", .35) + '</g>'
    # последний серый клубок: сидит на углу стола, на «тоска» отрывается и улетает вправо-вверх, тает
    u = clamp((t - (t97 - .05)) / .9)
    if u < 1:
        bx = lerp(990.0, 1260.0, ease_io(u)) + 6 * math.sin(t * 3)
        by = lerp(dy - 50, dy - 650, ease_io(u)) - 10 * math.sin(t * 2.3)
        clump = PR.gloom_cloud(bx, by, 1.1 * (1 - .4 * u), t, shrink=1.0, seed=18, pale=.3 + .7 * u)
        clump = f'<g opacity="{1 - u ** 1.5:.3f}">{clump}</g>'
    else:
        clump = ""
    world = d["bg"] + shadow + dshadow + glow + fig["svg"] + d["front"] + sheet + pen + lamp + cat + clump + d["shade"]
    uu = sm(t, t0 - .2, t1 + .2)
    s = lerp(1.12, 1.02, uu)
    return wrap(world, lerp(580, 540, uu), lerp(850, 870, uu), s)


def frame(sid, t):
    return {"s01": s01, "s02": s02, "s03": s03, "s12": s12, "s15": s15, "s18": s18}[sid](t)
