"""Рилс 79 «Месть сну», группа C — хук, фасад, Утрехт, петля: s01, s02, s06, s13, s17, s18.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Всё время — из shots.json (t0/t1) и voice/words.json (слова по индексу wN),
секунды в коде — только длительности движений. Места — common/room.py (раздел 79), Дима и люди — common/people.py (…79), кот —
common/cat.py (через people.cat_svg / cat_curl), предметы — common/props.py, надпись хука — common/hand_text.py.
Букв и цифр нет, кроме «Куда делась ночь?» (s01–s02). NOCAM=1 — без камеры и без надписи (замер движения рисунка);
MASK=1 — только силуэт рисунка хука (часы, люк, Дима с кроватью) белым на чёрном (замер заполнения)."""
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
HOOK_TEXT = json.load(open(os.path.join(STORY, "reel.json"))).get("hook_screen", "Куда делась ночь?")
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
        return lib.svg(f'<g transform="{lib.cam(cx, cy, 1.0)}">{world}</g>')
    if MASK:
        return lib.svg(f'<g transform="{lib.cam(cx, cy, s, rot)}">{world}</g>')
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s, rot)}">{world}</g>{over}')


def hook_cam(t, t_hit, t_hit2, rot0=-3.9, side0=-52.0, fly=.2, far=1.46, over=.062):
    """Влёт правил 28/29 (не слабее эталона 17): масштаб 1/far → 1 за fly с без разгона, перелёт over с отскоком, поворот rot0 с
    возвратом, боковой занос; удар +4 % на t_hit и +10 % на t_hit2. -> (множитель масштаба, поворот, занос, доля полёта 0…1)."""
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


# ═════════════════════════ надпись хука «Куда делась ночь?» (экранные координаты, s01–s02) ═════════════════════════
HOOK_SIZE = 1.15
HOOK_LINES = ("Куда делась", "ночь?")
HOOK_BASE = (262.0, 388.0)       # линии строк: буквы ≈ 155…390, зона R.AT_TEXT — только плоскость ската, поля ≥ 50 px


def hook_title(t, t_end):
    """Пишется с 0.00 за 0.30 с (маркер-росчерк: первая строка 0–.21, вторая .21–.30), целиком к 0.35; стоит до склейки t_end."""
    if t >= t_end:
        return ""
    a, b = HOOK_LINES
    la, lb = len(a.replace(" ", "")), len(b)
    ta = .30 * la / (la + lb)
    o = ""
    for txt, y, t0, dur in ((a, HOOK_BASE[0], 0.0, ta), (b, HOOK_BASE[1], ta, .30 - ta)):
        w = text_width(txt, HOOK_SIZE)
        x0 = (1080 - w) / 2 - 12
        o += hand_text(txt, t, t0, dur, x0, y, HOOK_SIZE, ink="#f6eedc", bold=1.85)
    # мягкая тёмная подложка-тень под буквами (читаемость на светлеющем потолке): та же надпись, смещённая и прозрачная
    sh = ""
    for txt, y, t0, dur in ((a, HOOK_BASE[0], 0.0, ta), (b, HOOK_BASE[1], ta, .30 - ta)):
        w = text_width(txt, HOOK_SIZE)
        x0 = (1080 - w) / 2 - 12
        sh += hand_text(txt, t, t0, dur, x0 + 5, y + 6, HOOK_SIZE, ink="#05081a", bold=1.85, op=.55)
    return sh + o


# ═════════════════════════ мансарда ночью: общее для s01, s02, s18 ═════════════════════════
LIE_K, LIE_TILT = .75, 10.0
LIE_HIP = (658.0, 1130.0)          # таз лежащего Димы: голова — на R.AT_HEAD, на подушке


def beam(phase, op=1.0):
    """Свет луны/солнца из люка — пятно формы стекла на стене и кровати, бежит против светила; цвет — от неба."""
    p = phase % 1.0
    sunk = 1 - abs(2 * ((p - .25) % 1.0) - 1)
    u = .45 + 1.1 * (p / .5) * .5 if p < .5 else -.05 + 1.1 * (p - .5) / .5
    bx, by = R._arc_pt(R.AT_SKY, u, 1.0)
    cx = sum(q[0] for q in R.AT_SKY) / 4
    dx = -1.2 * (bx - cx) - 290
    dy = 260 + .25 * (by - 560)
    q = [(x + dx + .25 * (y - 450), y + dy + .12 * (x - 650)) for x, y in R.AT_SKY]
    col = lib.mix("#8fa8ff", "#ffd890", sunk)
    a = (.22 + .3 * sunk) * op
    mt = ((q[0][0] + q[1][0]) / 2, (q[0][1] + q[1][1]) / 2)
    mb = ((q[3][0] + q[2][0]) / 2, (q[3][1] + q[2][1]) / 2)
    return (f'<g style="mix-blend-mode:screen" {lib.blur(5)}>' + blob([(x, y, 1) for x, y in q], col, a)
            + line([mt, mb], 12, "#000000", taper=0, wmin=1, seed=7955, op=.8 * a) + "</g>")


def clock_spin(t, rate_m, rate_h, blur, ring=0.0, sector_u=0.0):
    """Часы мансарды со стрелками, крутящимися со скоростями rate (оборотов в секунду), ring — сплошной круг-смаз."""
    x, y, r = R.AT_CLOCK
    o = PR.attic_clock(x, y, r, hour_a=rate_h, min_a=rate_m, blur=blur, sector_u=sector_u)
    if ring > .01:
        o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .74:.1f}" fill="#5a5468" opacity="{.28 * ring:.3f}"/>'
        o += line(ellipse_pts(x, y, r * .7, r * .7, 30) + [ellipse_pts(x, y, r * .7, r * .7, 30)[0]], 4, "#3a3448", taper=0, wmin=1, seed=7951,
                  op=.5 * ring)
    return o


# ═════════════════════════ s01: хук — ночь пролетает за секунду ═════════════════════════
def s01_state(t):
    h1, h2 = stress(1, .4), stress(3, .22)       # «лёг», «оДИНнадцать»
    phase = .18 + 1.25 * t + .5 * sm(t, h2 - .03, h2 + .12)          # на «ДИН» — луна и солнце меняются ещё раз
    rm = 360 * (3.0 * t + 2.2 * max(0.0, t - h2) + 1.2 * sm(t, h1 - .05, h1 + .2))
    rh = 360 * (.85 * t + .9 * max(0.0, t - h2)) + 40
    blur = .75 + .25 * sm(t, h2 - .05, h2 + .05)
    ring = sm(t, h2 - .04, h2 + .08)
    bed = 34 * kick(t, h1 - .03, .05, 7.0) + damp(t, h1 + .05, -12, 3.0, 5) + 4 * math.sin(t * 19)
    flash = kick(t, h1 - .02, .03, 9.0)
    return dict(h1=h1, h2=h2, phase=phase, rm=rm, rh=rh, blur=blur, ring=ring, bed=bed, flash=flash)


def attic_night_world(t, st, mode="phone", u=0.0, glow=1.0, expr=None, extra=None, light="night_phone", sky=None, show_phone=True):
    d = R.attic(t, light, sky=st["phase"] if sky is None else sky, bump=clamp(st["bed"] / 40.0, -1, 1), pillow=False)
    clk = clock_spin(t, st["rm"], st["rh"], st["blur"], st.get("ring", 0.0), st.get("sector", 0.0))
    hx, hy = LIE_HIP
    fig = PE.dima_lie79(hx, hy, LIE_K, t, mode, u=u, glow=glow, tilt=LIE_TILT, bump=st["bed"], pillow=True, expr=expr,
                        blink=st.get("blink", 0.0), blanket=st.get("blanket", 0.0))
    if not show_phone and mode == "phone":
        pass
    bm = beam(st["phase"]) if not isinstance(st["phase"], str) else ""
    fx = ""
    if st.get("flash", 0) > .01 and fig.get("phone"):
        px, py = fig["phone"]
        g = lib.rad_grad([(0, "#e6f2ff", .7 * st["flash"]), (1, "#e6f2ff", 0)], px, py, 260)
        fx += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="260" fill="url(#{g})"/>'
    if not isinstance(st["phase"], str):
        sunk = 1 - abs(2 * ((st["phase"] - .25) % 1.0) - 1)
        bm += (f'<rect x="-2200" y="-1400" width="4600" height="4400" fill="#ff9a50" opacity="{.16 * sunk:.3f}" '
               'style="mix-blend-mode:screen"/>')
    world = d["bg"] + d["sky"] + d["frame"] + bm + clk + fig["svg"] + (extra(fig) if extra else "") + fx + d["light"] + d["shade"]
    if MASK:
        lib.DEFS.append('<filter id="mk79"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>')
        sky_pts = [(x, y, 1) for x, y in R.AT_SKY]
        x, y, r = R.AT_CLOCK
        bed = shape(lib.rrect(R.AT_HEADBOARD[0], R.AT_BED_Y - 6, R.AT_BED_X[1], R.AT_BED_Y + 250, 12), "#fff", "", w=1)
        world = ('<rect x="-3000" y="-3000" width="8000" height="8000" fill="#000"/><g filter="url(#mk79)">' + R._skylight_frame(d["P"]) +
                 blob(sky_pts, "#fff") + blob(ellipse_pts(x, y, r, r, 30), "#fff") + bed + fig["svg"] + "</g>")
    return world, fig, d


def s01(t):
    lib.dyn_begin()
    st = s01_state(t)
    world, fig, d = attic_night_world(t, st, "phone", glow=1.0)
    eff = strokes(R.AT_CLOCK[0], R.AT_CLOCK[1], R.AT_CLOCK[2] * 1.08, R.AT_CLOCK[2] * 1.5, bump(t, st["h2"] - .02, .32), n=10, w=7, col="#d8dcf4",
                  seed=7960)
    world += eff
    cx0, cy0, s0 = R.AT_CAM_HOOK
    kk, rc, side, fl = hook_cam(t, st["h1"], st["h2"])
    sx1, sy1 = shake2(t, st["h1"], 8)
    sx2, sy2 = shake2(t, st["h2"], 12)
    cx = cx0 + side - sx1 - sx2 + 4 * math.sin(t * 2.1)
    cy = cy0 - sy1 - sy2
    s = s0 * kk * (1 + .02 * sm(t, .5, 1.6))
    over = hook_title(t, T1("s02"))
    blur = radial_blur(world, cx, cy, s, rc, fl)
    return wrap(world, cx, cy, s, rc, blur + over)


# ═════════════════════════ s02: стрелки встают на «три», телефон падает ═════════════════════════
def s02_state(t):
    h3 = stress(7, .2)                      # «три»
    a, b = W(4), W(5)
    # стрелки тормозят рывками с «а»/«уснул» и с размаху встают на «три» (часовая 90°, минутная 0°), дрожат пружиной
    st1 = s01_state(T0("s02"))
    m0, h0 = st1["rm"], st1["rh"]
    dt = t - T0("s02")
    v = 3.0 * (1 - .5 * sm(t, a - .05, a + .15) - .3 * sm(t, b, b + .2))
    jerk = .08 * math.sin(2 * math.pi * 6 * dt) * sm(t, a, a + .1)
    rm = m0 + 360 * (v * dt + jerk) * (1 if t < h3 else 0)
    rh = h0 + 360 * (.6 * dt) * (1 if t < h3 else 0)
    if t >= h3:
        # пришли на «три»: ближайшие кратные полному обороту + 0° / 90°, пружина
        mt = 360 * math.ceil((m0 + 360 * v * (h3 - T0("s02"))) / 360)
        ht = 360 * math.ceil((h0 + 360 * .6 * (h3 - T0("s02"))) / 360) + 90
        rm = mt + damp(t, h3, 14, 4.0, 7.0)
        rh = ht + damp(t, h3, -9, 3.6, 7.0)
    blur = .75 * (1 - sm(t, a, h3)) * (1 if t < h3 else 0) + .25 * (t < h3)
    phase = st1["phase"] + 1.0 * dt * (1 - sm(t, a, h3)) if t < h3 + .3 else "dawn"
    if t >= h3:
        phase = "dawn"
    sleep_u = sm(t, h3 - .04, h3 + .18)
    blink = clamp(.25 + .5 * sm(t, a, h3 - .05) + .25 * math.sin(t * 9) ** 8)
    bed = damp(t, h3 + .25, 10, 3, 6)
    return dict(h3=h3, phase=phase, rm=rm, rh=rh, blur=blur, ring=0.0, bed=bed, flash=0.0, sleep_u=sleep_u, blink=blink)


def s02(t):
    lib.dyn_begin()
    st = s02_state(t)
    h3 = st["h3"]
    rel = h3 + .07                                     # телефон выскальзывает из рук на «три» (руки разжались наполовину)
    phone_svg = ""

    def extra(fig):
        nonlocal phone_svg
        if t < rel:
            return ""
        f0 = PE.dima_lie79(LIE_HIP[0], LIE_HIP[1], LIE_K, rel, "hug", u=.49, tilt=LIE_TILT, pillow=False)
        p0 = f0["phone"]
        p1 = (LIE_HIP[0] - 50, LIE_HIP[1] + 70)          # соскользнул на одеяло перед руками
        u = clamp((t - rel) / .34)
        x = lerp(p0[0], p1[0], u)
        y = p0[1] + (p1[1] - p0[1]) * u * u - 50 * math.sin(math.pi * u) * (1 - u)
        y -= damp(t, rel + .34, 16, 4, 8) if u >= 1 else 0
        rot = -30 + 210 * ease_out(u, 2)
        return PR.phone_flat(x, y, .42, rot=rot, face_down=True, glow_=0.0, seed=7970)
    mode, u = ("hug", st["sleep_u"]) if t >= h3 - .04 else ("phone", 0.0)
    st["blanket"] = .6 * st["sleep_u"]
    glow = 1.0 - sm(t, h3 - .02, h3 + .06)
    expr = "sleep79" if t >= h3 else None
    world, fig, d = attic_night_world(t, st, mode, u=u, glow=glow, expr=expr, extra=extra, light="night_phone")
    x, y, r = R.AT_CLOCK
    world += strokes(x, y, r * 1.08, r * 1.55, bump(t, h3 - .02, .34), n=9, w=8, col="#e8ecff", seed=7975, a0=-60, span=300)
    cx0, cy0, s0 = R.AT_CAM_CLOCK
    dt = t - T0("s02")
    hit = .10 * kick(t, h3, .04, 4.0)
    sx, sy = shake2(t, h3, 12)
    cx = cx0 + 30 * dt - sx
    cy = cy0 - 18 * dt - sy
    s = s0 * (1 + .04 * dt) * (1 + hit)
    over = hook_title(t, T1("s02"))
    return wrap(world, cx, cy, s, -.6 + damp(t, h3, 1.2, 3, 6), over)


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


# ═════════════════════════ s06: фасад, окна-истории, камера к мансарде ═════════════════════════
SIL = (("cook", 0), ("run", 1), ("sit_cat", 2))


def s06(t):
    lib.dyn_begin()
    t24, t25, t26, t27 = stress(24, .3), stress(25, .25), stress(26, .3), stress(27, .2)
    lit = [sm(t, tt - .02, tt + .1) for tt in (t24, t25, t26)]
    d = R.house_facade(t, lit, attic_glow=.75 + .25 * math.sin(t * 13) ** 2)
    sil = ""
    for (kind, i), u in zip(SIL, lit):
        if u < .05:
            continue
        x0, y0, x1, y1 = R.HF_WIN[i]
        cid = R.windows_clip(i)
        k = .26
        px = (x0 + x1) / 2 - {"cook": 70, "run": 10 + 30 * math.sin(t * 3), "sit_cat": 75}[kind]
        py = y1 - 18 if kind != "sit_cat" else y1 - 60
        f = PE.dima_silhouette79(kind, px, py, k, t, col="#3a2a3a")
        pop = 1 + .15 * bump(t, (t24, t25, t26)[i] - .02, .25)
        sil += (f'<g clip-path="url(#{cid})" opacity="{u:.3f}"><g transform="translate({px:.1f} {py:.1f}) scale({pop:.3f}) '
                f'translate({-px:.1f} {-py:.1f})">{f["svg"]}</g></g>')
    # кот на коньке: сидит, огонёк ярче, на «Диму» смотрит вниз, хвост качается
    rx, ry = R.HF_RIDGE
    cst = dict(PE.CAT_ST["ridge79"], tail=4 + 3 * math.sin(t * 3.1), blink=bump(t, t25 + .1, .2))
    cat = PE.cat_svg(rx + 6, ry + 4, .42, cst, t)
    world = d["sky"] + d["bg"] + d["windows"] + sil + d["frames"] + cat
    # вспышки-штрихи у окна, когда оно загорается
    for i, tt in enumerate((t24, t25, t26)):
        x0, y0, x1, y1 = R.HF_WIN[i]
        world += strokes((x0 + x1) / 2, (y0 + y1) / 2, 170, 230, bump(t, tt - .02, .3), n=8, w=6, col="#ffe2a0", seed=7980 + 10 * i)
    c0, c1 = R.HF_CAM_LOW, R.HF_CAM_TOP
    u = ease_io(clamp((t - (t27 - .05)) / .5))
    u = u + .04 * math.sin(math.pi * clamp((t - (t27 + .45)) / .25)) * (t > t27 + .45)
    cx = lerp(c0[0], c1[0], u)
    cy = lerp(c0[1] + 30 * (t - T0("s06")), c1[1], u)          # до взлёта — медленный дрейф вниз-вверх по фасаду
    s_ = lerp(c0[2], c1[2], u) * (1 + .03 * (t - T0("s06")))
    rot = .8 * math.sin(math.pi * u)
    cx, wh = whip_in(world, cx, cy, s_, rot, t, T0("s06"))
    return wrap(world, cx, cy, s_, rot, "") if not wh else lib.svg(f'<g transform="{lib.cam(cx, cy, s_, rot)}">{world}</g>{wh}')


# ═════════════════════════ s13: вечерний Утрехт, учёные, карточка-пиктограмма ═════════════════════════
def pict_card(cx, cy, k=1.0, rot=0.0, push=0.0):
    """Пустая карточка-пиктограмма без букв: месяц сверху слева, подушка справа, ладонь отодвигает её (push 0…1)."""
    w, h = 210 * k, 150 * k
    o = shape(lib.rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 14 * k), "#fbf6ea", "", w=3.6, seed=7990)
    o += R._moon79(cx - 58 * k, cy - 30 * k, 26 * k, 0.0, calm=True)
    px = cx + 42 * k + 18 * k * push
    pil = [(px - 44 * k, cy + 44 * k, 1), (px - 48 * k, cy + 6 * k), (px - 30 * k, cy - 10 * k), (px + 30 * k, cy - 12 * k), (px + 48 * k, cy + 4 * k),
           (px + 46 * k, cy + 44 * k, 1)]
    o += shape(pil, "#a9c0e6", "", w=3.0, seed=7991)
    hx = px - 64 * k
    hand = [(hx - 46 * k, cy + 36 * k, 1), (hx - 46 * k, cy + 10 * k), (hx - 14 * k, cy + 6 * k), (hx + 4 * k, cy + 14 * k), (hx + 6 * k, cy + 28 * k),
            (hx - 8 * k, cy + 38 * k, 1)]
    o += shape(hand, "#f2c9a8", "", w=3.0, seed=7992)
    for j in range(2):
        o += line([(hx - 70 * k, cy + (14 + 14 * j) * k), (hx - 52 * k, cy + (14 + 14 * j) * k)], 4 * k, INK, seed=7993 + j)
    return f'<g transform="rotate({rot:.2f} {cx:.1f} {cy:.1f})">{o}</g>'


def s13(t):
    lib.dyn_begin()
    t58, t60, t63 = stress(58, .2), stress(60, .3), stress(63, .3)
    lab = sm(t, t58 - .04, t58 + .12)
    d = R.utrecht(t, lab)
    x0, y0, x1, y1 = R.UT_LAB
    cid = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    hold = sm(t, t63 - .1, t63 + .14)
    sk = .5
    cy_card = lerp(y1 + 80, y0 + 150, ease_out(hold, 2)) + damp(t, t63 + .14, 10, 3, 6)
    card_c = ((x0 + x1) / 2, cy_card)
    card = pict_card(card_c[0], card_c[1], 1.05, -4 + 4 * hold, push=sm(t, t63 + .15, t63 + .45))
    if hold > .02:
        sa = PE.scientist79("a", x0 + 115, y1 + 25, sk, pose="hold", center=(card_c[0] - 30, card_c[1]), held_svg="", t=t)
        sb = PE.scientist79("b", x1 - 115, y1 + 35, sk, pose="hold", center=(card_c[0] + 30, card_c[1]), held_svg="", t=t, flip=True)
    else:
        sa = PE.scientist79("a", x0 + 115, y1 + 25, sk, t=t)
        sb = PE.scientist79("b", x1 - 115, y1 + 35, sk, t=t, flip=True)
    inside = d["lab"] + sa["svg"] + sb["svg"] + (card if hold > .02 else "")
    world = (d["sky"] + d["bg"] + f'<g clip-path="url(#{cid})" opacity="{max(.15, lab):.3f}">{inside}</g>' + d["lab_frame"] + d["water"] + d["bridge"]
             + d["front"])
    world += strokes(card_c[0], card_c[1], 140, 200, bump(t, t63 + .1, .3), n=8, w=6, col="#fff0c0", seed=7995)
    # камера: окно → на «Голландии» над каналом к башне → на «назвали» обратно к окну с толчком
    lab_c = R.UT_CAM_LAB
    wide = (1500.0, 560.0, .62)
    near = ((x0 + x1) / 2, (y0 + y1) / 2 + 60, 1.45)
    u1 = ease_io(clamp((t - (t60 - .08)) / .5))
    u2 = ease_io(clamp((t - (t63 - .3)) / .32))
    c = [lerp(lab_c[i], wide[i], u1) for i in range(3)]
    c = [lerp(c[i], near[i], u2) for i in range(3)]
    dt = t - T0("s13")
    cx, cy, s_ = c[0] + 20 * dt, c[1], c[2] * (1 + .02 * dt) * (1 + .06 * kick(t, t63 + .02, .05, 4))
    cx, wh = whip_in(world, cx, cy, s_, 0, t, T0("s13"))
    set_ink(s_)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s_, 0)}">{world}</g>{wh}')


FRAMES = {"s01": s01, "s02": s02, "s06": s06, "s13": s13}


def frame(sid, t):
    return FRAMES[sid](t)
