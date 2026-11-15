"""Рилс 73 «Ты сам виноват», группа B: Дима один и ночь без сна.
s03 (2.80–4.48, whip): холодная комната общим планом; «никто» (2.93) шторы съезжаются, полоса света сужается до прожектора на Диме;
    «тебе» (3.26) Дима оглядывается; «не поможет» (3.65–4.40) кот поворачивает голову и уходит вправо ШАГОМ, плечи Димы опускаются.
s07 (8.75–10.20): лицо на подушке крупно (вид от изножья), лунный свет; «мозг» (8.95) над головой проступает клубок-мозг,
    «три» (9.33) глазки вспыхивают, клубок опускается, Дима натягивает одеяло до носа; медленное моргание.
s08 (10.20–11.55): кровать и окно с луной; 10.24 / 10.65 / 11.05 — щелчок ночи: фаза луны (серп → половина → полная),
    Дима переворачивается (новая поза через промежуточные кадры), паутина в углу окна гуще; вспышка темноты 2 кадра.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Предметы — common/props.py, люди и кот — common/people.py / cat.py, место — room.py."""
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
import props as P  # noqa: E402
import room as R  # noqa: E402
from lib import clamp, ease_in, ease_io, ease_out, svg  # noqa: E402

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?:«»").lower() == word:
            return w["start"]
    raise KeyError(word)


def lerp(a, b, u):
    return a + (b - a) * u


def frame_svg(body, cx, cy, s, rot, bg, over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def whip_in(t, t0, dur=.2):
    u = clamp((t - t0) / dur)
    e = 1 - ease_out(u, 3)
    return -150 * e, -2.0 * e


# ═══════════════════════════════ s03: Дима один ═══════════════════════════════
T3_IN = 2.80
T3_NIK = wt("никто")              # 2.93
T3_TEB = wt("тебе")               # 3.26
T3_NE = wt("не", 3.5)             # 3.65
T3_POM = wt("поможет")            # 3.98
SC3 = .86
D3 = (R.STAND73[0] + 190, R.FL73 - (people.LEG_LEN - 12) * SC3 * people.HEIGHT["dima"] - 14)
CAT3 = (30.0, R.FL73 - 4)
K3 = .95


def s03(t):
    lib.dyn_begin()
    cu = ease_out(clamp((t - T3_NIK) / .24), 3)
    d = R.cold_room(t, "wide", cu)
    o = [d["bg"], d["light"]]
    # доска: пыльный конверт на кнопке (качается от хлопка штор), паутина в углу доски
    sw = 2.0 * math.sin(t * 5.2) + 7 * math.exp(-max(0, t - T3_NIK - .1) * 4) * math.sin(max(0, t - T3_NIK) * 16) * (t > T3_NIK)
    o.append(P.cobweb(R.BOARD73_WEB[0] + 8, R.BOARD73_WEB[1] + 8, 1.5, tremble=.3, t=t, ang=0, span=90, L=150, seed=31))
    o.append(R.cold_tint(P.pinned_envelope(*R.BOARD73_PIN, 1.15, swing=sw, dust=1.0, web=.8, t=t, seed=3), .6))
    # Дима: растерянно смотрит на доску → оглядывается → плечи опускаются
    x, y = D3
    br = 3 * math.sin(t * 2 * math.pi / 2.6)
    g = clamp((t - T3_TEB) / .14) * (1 - clamp((t - T3_TEB - .42) / .16))         # оглянулся и вернулся
    sag = ease_io(clamp((t - T3_POM) / .38))
    if sag > .01:
        pk = dict(pose="rest", u_pose=("sag73", sag))
        ex = "sag73" if sag > .4 else "lost73"
    elif g > .01:
        pk = dict(pose="rest", u_pose=("glance73", g))
        ex = "glance73" if g > .5 else "lost73"
    else:
        pk = dict(pose="rest")
        ex = "lost73"
    look_flick = .08 * math.sin(t * 7.0)                                          # голова живёт с первого кадра
    fig = people.dima(x, y + br, SC3, ex, head_add=look_flick - .5 * g + .12 * sag, **pk, **people.stand_kw(x, y, SC3))
    o.append(R.cold_tint(fig["svg"], 1.0))
    # кот: стоит рядом, холодно смотрит на Диму → поворачивает голову вправо → уходит шагом вправо из кадра
    turn_u = ease_out(clamp((t - T3_NE) / .16), 2)
    walk_u = clamp((t - T3_NE - .16) / .9)
    cx = CAT3[0] + 520 * ease_in(walk_u, 1.4)
    st = dict(people.CAT_ST["judge"])
    st.update(turn=-.6 + 1.6 * turn_u, look=(-.7 + 1.6 * turn_u, -.2), tail=4 * math.sin(t * 6))
    if walk_u > 0:
        cs = people.cat_walk(cx, CAT3[1], K3, t, st, period=.42)
    else:
        st["tilt"] = 2 * math.sin(t * 3)
        cs = people.cat_svg(cx, CAT3[1], K3, st, t)
    o.append(R.cold_tint(cs, 1.0))
    o.append(d["dim"])
    # камера: хлёст влево, затем медленный отъезд вслед за сужающимся светом
    wx, wr = whip_in(t, T3_IN)
    zu = ease_io(clamp((t - T3_IN) / (4.68 - T3_IN)))
    s = lerp(1.06, .96, zu)
    cx_, cy_ = -390 + lerp(40, 0, zu), 1000
    return frame_svg("".join(o), cx_ - wx / s, cy_, s, wr, "#9aa6b2")


# ═══════════════════════════════ s07: лицо на подушке и клубок-мозг ═══════════════════════════════
T7_MOZG = wt("мозг")              # 8.95
T7_TRI = wt("три")                # 9.33
T7_NOCH = wt("ночи")              # 9.53
SC7 = 1.0
_F7 = people.dima(0, 0, SC7, "awake73", layers=("body",))
D7 = (R.FOOT_HEAD[0] - _F7["head"][0], R.FOOT_HEAD[1] - _F7["head"][1])


def s07(t):
    lib.dyn_begin()
    d = R.bedroom(t, "moon", "foot")
    o = [d["bg"]]
    # Дима: глаза открыты в потолок, медленное моргание 9.62–10.02, после «три» взгляд на клубок
    bl = math.sin(math.pi * clamp((t - 9.70) / .5)) ** 1.2
    base = dict(people.EXPR["dima"]["awake73"])
    lk = .25 * math.sin(t * 1.9)
    base["look"] = (lk, -.45 + .15 * clamp((t - T7_TRI) / .2))
    if t > T7_TRI:
        base["brows"] = "worry"
    ex = people.awake_blink(base, bl)
    br = 2.5 * math.sin(t * 2 * math.pi / 3.4)
    fig = people.dima(D7[0], D7[1] + br, SC7, ex, layers=("body",), head_add=.03 * math.sin(t * 1.3))
    o.append(R.cold_tint(fig["svg"], 0.0, 1.0))
    # одеяло: на «три» натягивается до носа; пальцы держат край
    pull = ease_out(clamp((t - T7_TRI - .04) / .22), 3)
    dy = -88 * pull
    o.append(f'<g transform="translate(0 {dy:.2f})">{d["front"]}</g>')
    if pull > .02:
        hx, hy = R.FOOT_HEAD
        ey = hy + 125 + dy - 20
        for sx in (-1, 1):
            kx = hx + sx * 120
            o.append(R.cold_tint(_knuckles(kx, ey + 26 * (1 - pull), sx), 0.0, 1.0))
    # клубок-мозг над головой: проступает на «мозг», вспыхивает и опускается на «три»
    u = ease_out(clamp((t - T7_MOZG + .05) / .35), 2)
    low = ease_out(clamp((t - T7_TRI) / .3), 2)
    eyes = clamp((t - T7_MOZG - .12) / .15)
    glow = math.exp(-max(0.0, t - T7_TRI) * 5) * (t >= T7_TRI)
    bx = R.FOOT_HEAD[0] + 12 * math.sin(t * 2.3)
    by = R.FOOT_HEAD[1] - 300 + 60 * low + 6 * math.sin(t * 3.1)
    o.append(P.brain_scribble(bx, by, .68 + .06 * low, u, eyes, 0.0, t, seed=7, glow=glow))
    # камера: медленный наезд к лицу 5 %, на «три» короткий удар +4 %
    s0 = 2.75 * (1 + .05 * ease_io(clamp((t - 8.55) / 1.85)))
    q = t - T7_TRI
    bump = .04 * math.sin(math.pi * clamp(q / .22)) if 0 < q < .22 else 0.0
    s = s0 * (1 + bump)
    return frame_svg("".join(o), R.FOOT_HEAD[0], R.FOOT_HEAD[1] - 40, s, .4 * math.sin(t * .9), "#1a2040")


def _knuckles(x, y, sx):
    """Кончики пальцев над краем одеяла (четыре костяшки), без кисти и предплечья."""
    o = []
    for i in (3, 2, 1, 0):
        cx = x + sx * (i - 1.5) * 21
        pts = lib.ellipse_pts(cx, y - 2 * abs(i - 1.5), 15, 22, 12)
        o.append(lib.shape(pts, "#ecc4a2", lib.blob(lib.ellipse_pts(cx + 5, y + 8, 9, 12, 10), "#d39f83") +
                           lib.blob(lib.ellipse_pts(cx, y - 13, 6, 5, 8), "#f1cdbd"), w=3.2, seed=7700 + i + (sx + 1) * 5))
    return "".join(o)


# ═══════════════════════════════ s08: ночь за ночью ═══════════════════════════════
T8 = (wt("каждую"), 10.65, 11.05)       # 10.24, 10.65, 11.05
CAM8 = (1070.0, 1000.0, .6)
PHASES8 = (.08, .22, .5, 1.0)
POSES8 = (dict(roll=0.0, expr="awake73"), dict(roll=1.0, expr="stare73"), dict(roll=.35, expr="sag73"), dict(roll=.85, expr="awake73"))
SC8 = .78
HEAD8 = (1835.0, 1112.0)


def _night8(t):
    i = sum(1 for x in T8 if t >= x)
    return i, (t - T8[i - 1]) if i else 99.0


def s08(t):
    lib.dyn_begin()
    i, since = _night8(t)
    d = R.bedroom(t, "moon", "wide", moon_phase=0.0)
    o = [d["bg"]]
    # своя луна в видимой полосе окна (луна комнаты — за левым краем кадра)
    wx0, wy0, wx1, wy1 = R.WIN73
    c = lib.clip_rect(wx0 + 30, wy0 + 30, wx1 - wx0 - 60, wy1 - wy0 - 60)
    o.append(f'<g clip-path="url(#{c})">{R.moon73(262, 400, 58, PHASES8[i])}</g>')
    # паутина в углу окна гуще с каждой ночью
    for j in range(i + 1):
        o.append(P.cobweb(wx1 + 18, wy0 - 20 + 8 * j, 1.1 + .35 * j, tremble=.2, t=t, ang=0 + 12 * j, span=90, L=120 + 30 * j, seed=80 + j,
                          col="#8f9bc0"))
    # Дима: поза ночи i; переход из прежней — 3 промежуточных кадра (0.1 с)
    a = POSES8[max(0, i - 1)] if i else POSES8[0]
    b = POSES8[i]
    m = ease_io(clamp(since / .1))
    roll = lerp(a["roll"], b["roll"], m)
    ex = b["expr"] if m > .5 else a["expr"]
    sc = SC8 * people.HEIGHT["dima"]
    hip = (HEAD8[0] - 548 * sc, HEAD8[1] + 50 * sc)
    db = people.dima_bed(hip[0], hip[1], SC8, people.awake_blink(ex, .0), roll=roll, t=t, cover=.25, col="blue", flip=True, seed=8)
    o.append(R.cold_tint(db["svg"], 0.0, 1.0))
    # камера: фиксированная крупность, на каждом щелчке микросдвиг 1.5 % и вспышка темноты 2 кадра
    cx, cy, s = CAM8
    s *= 1 + .015 * i + .004 * math.sin(t * 1.4)
    cx += 10 * ((i % 2) * 2 - 1) * (i > 0)
    over = ""
    if 0 <= since < 2.5 / 30:
        over = '<rect width="1080" height="1920" fill="#05070f" opacity=".82"/>'
    return frame_svg("".join(o), cx, cy, s, 0.0, "#1a2040", over)


SHOTS = {"s03": s03, "s07": s07, "s08": s08}


def frame(sid, t):
    return SHOTS[sid](t)
