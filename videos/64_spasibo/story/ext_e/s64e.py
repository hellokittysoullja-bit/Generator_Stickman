"""Рилс 64 «спасибо», группа E — исследование «визит благодарности».
s09 (21.81–24.04): светлая аудитория, три участника (юноша, бородач, женщина с кудрями) за столами пишут письма; «написать» (22.13)
    перья ведут строки штрихами, «письмо» (22.59) листы заполняются, «благодарности» (22.93) каждый рисует внизу сердечко и
    улыбается. Камера: панорама вдоль столов с отъездом, потом наезд на ближний лист.
s10 (24.04–26.40): гостиная, участница с кудрями стоя читает письмо пожилому отцу в кресле; «человеку» (25.02) отец поднимает
    глаза, «лично» (25.58) кладёт ладонь на сердце, глаза блестят, она смущённо улыбается. Мягкий наезд, дрейф между лицами.
s11 (26.40–29.20): три лица крупно в ряд (участница, бородач, отец): «Счастливее» (26.40) серые лица по очереди заливаются цветом,
    улыбки распускаются, искорки у глаз; «чувствовали» (28.29) бородач смеётся, участница прикрывает рот ладонью. Откат.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Люди — common/people.py, предметы — common/props.py; здесь — только
мебель своих мест (столы аудитории, кресло, гостиная) и хореография."""
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
import people as PE  # noqa: E402
import props as P  # noqa: E402
from lib import blob, clamp, ease_in, ease_io, ease_out, ellipse_pts, line, mix, rect_pts, shape, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(i):
    return WORDS[i]["start"]


def lerp(a, b, u):
    return a + (b - a) * u


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    return 0.0 if (u <= 0 or u >= 1) else math.sin(math.pi * u) ** 2


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def ex_mix(a, b, u):
    """Промежуточная мимика: числа и пары — плавно, имена (брови, рот) — на середине."""
    u = clamp(u)
    out = {}
    for k in set(a) | set(b):
        va, vb = a.get(k), b.get(k)
        if va is None:
            va = vb if not isinstance(vb, (int, float)) else (0.0 if k not in ("lid",) else .8)
        if vb is None:
            vb = va if not isinstance(va, (int, float)) else (0.0 if k not in ("lid",) else .8)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool):
            out[k] = va + (vb - va) * u
        elif isinstance(va, tuple) and isinstance(vb, tuple):
            out[k] = tuple(x + (y - x) * u for x, y in zip(va, vb))
        else:
            out[k] = vb if u >= .5 else va
    return out


def E(who, name):
    return dict(PE.EXPR[who][name])


def cam_wrap(body, cx, cy, s, rot=0.0, bg="#EFE6D6", dx=0.0, dy=0.0):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="translate({dx:.2f} {dy:.2f})">'
               f'<g transform="{lib.cam(cx, cy, s, rot)}">{body}</g></g>')


def clip_y(inner, y0, y1, x0=-3000, x1=6000):
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    return f'<g clip-path="url(#{c})">{inner}</g>'


# ═════════════════════════ s09: аудитория, трое пишут ═════════════════════════
T9_WRITE, T9_LETTER, T9_THANKS = wt(43), wt(44), wt(45)
WALL9 = 640.0             # низ стены аудитории (дальше — пол уходит к зрителю)
# кто, таз (x, y), масштаб, сдвиг начала: дальний — юноша, средний — бородач, ближний — женщина с кудрями
STATIONS = [("youth", 640.0, 830.0, .50, 0.0), ("beard", 250.0, 1190.0, .66, .10), ("curly", 520.0, 1600.0, .86, .20)]


def hall_back(t):
    o = [blob(rect_pts(-1400, -1400, 3000, WALL9), "#F3EBDC")]
    o.append(blob(rect_pts(-1400, WALL9 - 70, 3000, WALL9), "#E6D9C2"))
    o.append(line([(-1400, WALL9 - 70), (3000, WALL9 - 69)], 4, INK, taper=0, wmin=.8, seed=9001))
    o.append(blob(rect_pts(-1400, WALL9, 3000, 3200), "#D9C3A0"))
    for j in range(-12, 22):        # доски пола сходятся к стене
        x = 540 + j * 130
        o.append(line([(540 + j * 70, WALL9 + 4), (x + (x - 540) * 1.4, 3000)], 2.4, "#C2A880", taper=0, wmin=.6, seed=9010 + j))
    o.append(line([(-1400, WALL9), (3000, WALL9 + 2)], 5, INK, taper=0, wmin=.8, seed=9002))
    # высокие окна в стене; от каждого на полу — полоса света формы окна (чёткая, с переплётом)
    for j, wx in enumerate((-260, 220, 700, 1180)):
        x0, x1, y0, y1 = wx - 130, wx + 130, -60, 520
        sky = blob(rect_pts(x0, y0, x1, y1), "#CFE6F2") + blob(rect_pts(x0, y1 - 130, x1, y1), "#DCEFE0")
        sky += blob(ellipse_pts(x0 + 80, y1 - 120, 100, 60, 14), "#A9CF9A") + blob(ellipse_pts(x1 - 50, y1 - 105, 80, 52, 14), "#9CC48C")
        o.append(shape(rect_pts(x0, y0, x1, y1), "#CFE6F2", sky, w=5, seed=9100 + j))
        o.append(line([(wx, y0), (wx, y1)], 7, "#FFFFFF", taper=0, wmin=1, seed=9110 + j))
        o.append(line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], 7, "#FFFFFF", taper=0, wmin=1, seed=9120 + j))
        o.append(shape(rect_pts(x0 - 16, y1, x1 + 16, y1 + 20), "#FFFFFF", "", w=3.4, seed=9130 + j))
        for half in (0, 1):        # две створки — два чётких светлых параллелограмма
            ax0 = x0 + half * 136 + 6
            ax1 = ax0 + 118
            q = [(ax0 + 60, WALL9 + 20, 1), (ax1 + 60, WALL9 + 20, 1), (ax1 + 330, WALL9 + 520, 1), (ax0 + 330, WALL9 + 520, 1)]
            o.append(blob(q, "#E6D2AE"))
    return "".join(o)


def chair9(x, y, sc, floor, seed):
    """Стул участника: спинка слева от таза (смотрит вправо), сиденье под тазом."""
    o = []
    bx = x - 150 * sc
    o.append(shape([(bx - 18 * sc, y + 40 * sc, 1), (bx - 30 * sc, y - 360 * sc, 1), (bx + 10 * sc, y - 360 * sc, 1), (bx + 16 * sc, y + 40 * sc, 1)],
                   "#7C9AB8", blob(rect_pts(bx, y - 350 * sc, bx + 12 * sc, y + 40 * sc), "#5E7D9C"), w=4, seed=seed))
    o.append(shape(lib.rrect(bx - 26 * sc, y - 380 * sc, bx + 24 * sc, y - 200 * sc, 14 * sc), "#8BA9C6", "", w=4, seed=seed + 1))
    for j, lx in enumerate((x - 140 * sc, x + 110 * sc)):
        o.append(shape(rect_pts(lx - 9 * sc, y + 40 * sc, lx + 9 * sc, floor), "#5E6B78", "", w=3.4, seed=seed + 3 + j))
    return "".join(o)


def seat_front9(x, y, sc, seed):
    return shape(lib.rrect(x - 170 * sc, y + 10 * sc, x + 140 * sc, y + 52 * sc, 12 * sc), "#8BA9C6",
                 blob(rect_pts(x - 170 * sc, y + 34 * sc, x + 140 * sc, y + 52 * sc), "#6E8CAA"), w=4, seed=seed)


def write_u(t, d):
    """Сколько письма написано: с «написать» строки идут быстро, к «благодарности» лист полон."""
    return 1.0 * ease_out(clamp((t - (T9_WRITE - .5 + d * .3)) / (T9_THANKS - .12 - (T9_WRITE - .5 + d * .3))), 1.4)


def station(who, X, Y0, PS9, d, t, look_cam=0.0):
    """Участник за столом пишет письмо; к «благодарности» рисует внизу сердечко и улыбается."""
    sc = PS9 * PE.HEIGHT[who]
    Y = Y0 + 3 * sc * math.sin(t * 1.7 + X)
    floor = Y0 + 300 * sc
    yb, yf = Y - 250 * sc, Y - 150 * sc               # задний и передний край крышки
    lw, lh, lk, lsy = 200.0, 260.0, .95 * sc, .52
    LX, LY = X + 270 * sc, (yb + yf) / 2 + 4 * sc
    LROT = -6.0
    wu = write_u(t, d)
    th = T9_THANKS - .08 + d * .55                     # начало сердечка у каждого своё
    hu = ease_io(clamp((t - th) / .55))
    # кончик пера: по строке, потом по сердечку
    px, py = P.letter_tip(0, 0, 1.0, 0, lw, lh, max(.001, min(.999, wu)), seed=d * 10)
    heart_c = (0.0, lh / 2 - 34)
    hpts = P._heart_pts(.95, 48)
    if hu > 0:
        q = hpts[min(len(hpts) - 1, int(hu * (len(hpts) - 1)))]
        tx, ty = heart_c[0] + q[0], heart_c[1] + q[1]
        k_in = clamp(hu * 6)
        px, py = lerp(px, tx, k_in), lerp(py, ty, k_in)
    if t > th + .55:            # отводит перо, любуется
        lift = ease_out(clamp((t - th - .55) / .4))
        px, py = lerp(px, 70, lift * .6), lerp(py, lh / 2 - 10, lift * .6) - 40 * lift
    c, s = math.cos(math.radians(LROT)), math.sin(math.radians(LROT))
    tip = (LX + lk * (px * c - py * lsy * s), LY + lk * (px * s + py * lsy * c))
    if t > th + .55:
        tip = (tip[0], tip[1] - 20 * sc * ease_out(clamp((t - th - .55) / .4)))
    # перо: наклон назад к руке; кисть держит его у кончика пальцами
    prot = -28.0 + 4 * math.sin(t * 9 + X)
    pk = .78 * sc
    a = math.radians(prot)
    axis = (-math.sin(a), math.cos(a))                 # от центра к кончику
    pc = (tip[0] - axis[0] * 90 * pk, tip[1] - axis[1] * 90 * pk)
    grip = (tip[0] - axis[0] * 52 * pk, tip[1] - axis[1] * 52 * pk)
    hd = (axis[0] * .55 + .35, axis[1] * .55 + .2)
    n_ = math.hypot(*hd)
    hd = (hd[0] / n_, hd[1] / n_)
    wrist = (grip[0] - hd[0] * 70 * sc, grip[1] - hd[1] * 70 * sc - 8 * sc)
    # мимика: серьёзно → улыбка к сердечку
    smile = ease_io(clamp((t - th) / .5))
    ex = ex_mix(E(who, "serious"), E(who, "happy"), smile)
    ex["look"] = (lerp(.45, .25, smile), lerp(.65, .35, smile))
    if look_cam > 0:
        ex["look"] = (lerp(ex["look"][0], -.15, look_cam), lerp(ex["look"][1], 0, look_cam))
    ex["closed"] = max(bump(t, 21.9 + d * 1.7, .16), bump(t, 23.75 + d, .16))
    kw = PE.pose_kw("write", X, Y, PS9, who)
    kw["arms"]["n"] = ("ik", wrist, -1)
    kw["hands"]["n"] = {"dir": hd, "curl": (.62, .7, .75, .8), "thumb": .75, "spread": .05, "bend": .05}
    # дальняя рука прижимает лист у верхнего края
    kw["arms"]["f"] = ("ik", (LX - 40 * sc, yb + 22 * sc), -1)
    kw["hands"]["f"] = {"dir": (.85, .35), "curl": (.2, .2, .25, .3), "thumb": .3, "spread": .12}
    kw["lean"] += .04 * math.sin(t * 2.1 + d * 3) + .05 * smile
    kw["head_ang"] += .05 * smile - .03
    kw["feet"] = {"n": ((X + 330 * sc, floor), 0.0), "f": ((X + 280 * sc, floor - 8 * sc), 0.0)}
    fig = PE.figure(who, X, Y, PS9, ex, layers=("legs", "pelvis"), **kw)
    upper = PE.figure(who, X, Y, PS9, ex, layers=("arm_f", "body"), **kw)
    arm_f = PE.figure(who, X, Y, PS9, ex, layers=("arm_f",), **kw)
    arm_n = PE.figure(who, X, Y, PS9, ex, layers=("arm_n",), **kw)
    o = [chair9(X, Y, sc, floor - 6 * sc, 9300 + int(X)), fig["svg"], seat_front9(X, Y, sc, 9320 + int(X))]
    o.append(clip_y(upper["svg"], -3000, yb + 6))
    # стол: крышка от yb до yf, кромка и ножки
    o.append(P.desk(X + 250 * sc, yf, 640 * sc, 1.0, depth=yf - yb, legs=True, seed=int(X) % 50, leg_h=floor - yf - 26))
    o.append(clip_y(arm_f["svg"], yb + 6, 6000))
    o.append(P.letter(LX, LY, lk, LROT, lw, lh, write=wu, seed=d * 10, sy=lsy))
    if hu > 0:
        hx = LX + lk * (heart_c[0] * c - heart_c[1] * lsy * s)
        hy = LY + lk * (heart_c[0] * s + heart_c[1] * lsy * c)
        o.append(f'<g transform="translate({hx:.2f} {hy:.2f}) scale(1 {lsy})">{P.heart_stroke(0, 0, .95 * lk, hu, seed=d * 7, w=8)}</g>')
    o.append(P.pen(pc[0], pc[1], pk, prot, cap=1.0 if False else 0.999, seed=d * 3))
    o.append(arm_n["svg"])
    return "".join(o), dict(head=upper["head"], tip=tip, letter=(LX, LY), sc=sc, smile=smile, th=th)


def s09(t):
    o = [hall_back(t)]
    info = {}
    for who, X, Y0, ps, d in STATIONS:
        sv, inf = station(who, X, Y0, ps, d, t)
        o.append(sv)
        info[who] = inf
        if inf["smile"] > .3:
            hx, hy = inf["head"]
            o.append(P.sparkles(hx + 40, hy - 40, 1.1, inf["smile"] * .9, t, seed=int(X) % 13, n=3, r=150))
    # камера: с ближнего плана юноши — панорама вдоль столов с отъездом (видны все трое к «благодарности»),
    # потом наезд на ближний лист и лицо женщины с кудрями
    a = sm(t, 21.6, 22.9)
    b = sm(t, 23.15, 24.25)
    L = info["curly"]["letter"]
    cx = lerp(lerp(800, 600, a), L[0] - 70, b)
    cy = lerp(lerp(760, 1180, a), L[1] - 60, b)
    s = lerp(lerp(1.45, 1.02, ease_out(a, 1.6)), 1.75, ease_in(b, 1.3))
    rot = lerp(-1.2, .6, a) + lerp(0, -.8, b)
    set_ink(s)
    return cam_wrap("".join(o), cx, cy, s, rot, bg="#F3EBDC")


# ═════════════════════════ s10: гостиная, дочь читает письмо отцу ═════════════════════════
T10_CHEL, T10_LICH = wt(49), wt(50)          # «человеку» 25.02, «лично» 25.58
FL10 = 1700.0
CUR10 = (290.0, .76)                          # x таза, масштаб участницы
FA10 = (790.0, .78)                           # x таза, масштаб отца
CH_BR, CH_BR_SH, CH_BR_HI = "#b0663e", "#8a4b2c", "#c98256"


def living_bg(t):
    o = [blob(rect_pts(-900, -900, 2000, FL10), "#e7d7c0")]
    for i in range(-14, 34):       # обои: тонкая полоска
        x = i * 70
        o.append(blob(rect_pts(x, -900, x + 8, 1300), "#dccab0", .9))
    o.append(shape(rect_pts(-900, 1300, 2000, FL10), "#c9a882", blob(rect_pts(-900, 1300, 2000, 1318), "#dcc09c"), w=3.4, seed=9401))
    for i in range(-10, 26):
        x = i * 120
        o.append(line([(x, 1340), (x, FL10 - 20)], 2.2, "#b08d66", taper=0, wmin=.8, seed=9410 + i, op=.8))
    o.append(blob(rect_pts(-900, FL10, 2000, 2800), "#a2704a"))
    for i in range(10):
        yy = FL10 + 26 + i * 36 + i * i * 3
        o.append(line([(-900, yy), (2000, yy + 4)], 2.2, "#82553a", taper=0, wmin=1, seed=9420 + i, op=.6))
    o.append(line([(-900, FL10), (2000, FL10)], 4, INK, taper=0, wmin=.8, seed=9430))
    # окно между ними: занавески, небо с деревом
    wx0, wy0, wx1, wy1 = 360.0, 330.0, 760.0, 880.0
    sway = 5 * math.sin(t * 1.2)
    sky = blob(rect_pts(wx0, wy0, wx1, wy1), "#cfe5f0") + blob(rect_pts(wx0, wy0 + 330, wx1, wy1), "#e2efe0", .8)
    sky += blob(ellipse_pts(470 + sway, 640, 120, 90, 14), "#8fbc72") + blob(ellipse_pts(640 + sway * 1.2, 700, 110, 80, 14), "#7eae63")
    sky += shape(rect_pts(540, 700, 560, wy1), "#6e4a2c", "", w=2.6, seed=9440)
    o.append(shape(rect_pts(wx0, wy0, wx1, wy1), "#cfe5f0", sky, w=4.6, seed=9441))
    o.append(shape(rect_pts((wx0 + wx1) / 2 - 9, wy0, (wx0 + wx1) / 2 + 9, wy1), "#f6f0e2", "", w=3, seed=9442))
    o.append(shape(rect_pts(wx0, (wy0 + wy1) / 2 - 9, wx1, (wy0 + wy1) / 2 + 9), "#f6f0e2", "", w=3, seed=9443))
    o.append(shape(rect_pts(wx0 - 30, wy1, wx1 + 30, wy1 + 26), "#f6f0e2", "", w=3.4, seed=9444))
    for side, x in ((-1, wx0 - 20), (1, wx1 + 20)):
        cur = [(x - 60, wy0 - 40), (x + 60, wy0 - 40), (x + 50 + side * 10, wy1 + 60), (x - 50 + side * 10, wy1 + 60)]
        inner = "".join(line([(x - 40 + 26 * j, wy0 - 30), (x - 36 + 26 * j + side * 6, wy1 + 50)], 2.2, "#9a4f3a", seed=9450 + j + side * 7, op=.7)
                        for j in range(4))
        o.append(shape(cur, "#c4644a", inner, w=4, seed=9446 + side))
    o.append(line([(wx0 - 110, wy0 - 40), (wx1 + 110, wy0 - 40)], 8, "#6e4a2c", taper=0, wmin=1, seed=9449))
    # полоса солнца формы окна на стене справа (чёткая)
    for (a0, a1) in ((wx0, (wx0 + wx1) / 2 - 9), ((wx0 + wx1) / 2 + 9, wx1)):
        for (b0, b1) in ((wy0, (wy0 + wy1) / 2 - 9), ((wy0 + wy1) / 2 + 9, wy1)):
            q = [(a0 + 560, b0 + 260), (a1 + 560, b0 + 260), (a1 + 560 + (b1 - b0) * .25, b1 + 260), (a0 + 560 + (b1 - b0) * .25, b1 + 260)]
            o.append(f'<polygon points="{" ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in q)}" fill="#fff3d6" opacity=".4"/>')
    # картинка без букв
    o.append(P.wall_sketch(-120, 560, 1.2, 0, seed=3, kind="house"))
    o.append(blob(ellipse_pts(560, FL10 + 120, 620, 90, 24), "#7f9a8a"))
    o.append(blob(ellipse_pts(560, FL10 + 120, 520, 66, 24), "#97b2a0"))
    return "".join(o)


def armchair10(x, y, sc):
    """Кресло отца (лицом влево): спинка справа от таза, сиденье, подлокотник ближний — отдельно."""
    k = sc / .78
    back = [(x - 40 * k, y + 60 * k, 1), (x - 10 * k, y - 470 * k), (x + 80 * k, y - 560 * k, 1), (x + 240 * k, y - 540 * k), (x + 300 * k, y - 420 * k, 1),
            (x + 300 * k, y + 80 * k, 1)]
    o = [shape(back, CH_BR, blob([(x + 160 * k, y - 520 * k), (x + 300 * k, y - 420 * k), (x + 300 * k, y + 80 * k), (x + 170 * k, y + 80 * k)], CH_BR_SH, .85)
               + blob([(x + 40 * k, y - 520 * k), (x + 140 * k, y - 545 * k), (x + 110 * k, y - 500 * k)], CH_BR_HI, .9), w=5, seed=9460)]
    seat = [(x - 330 * k, y - 30 * k, 1), (x + 260 * k, y - 40 * k, 1), (x + 290 * k, y + 200 * k, 1), (x - 320 * k, y + 210 * k, 1)]
    o.append(shape(seat, CH_BR_SH, blob(rect_pts(x - 340 * k, y + 120 * k, x + 300 * k, y + 220 * k), "#6f3c22", .9), w=5, seed=9461))
    for lx in (x - 290 * k, x + 250 * k):
        o.append(shape(rect_pts(lx - 16 * k, y + 205 * k, lx + 16 * k, FL10 - 4), "#5a3a24", "", w=3, seed=9462 + int(lx) % 5))
    return "".join(o)


def armchair10_arm(x, y, sc):
    k = sc / .78
    arm = [(x - 300 * k, y - 140 * k, 1), (x - 100 * k, y - 150 * k, 1), (x - 80 * k, y + 200 * k, 1), (x - 300 * k, y + 205 * k, 1)]
    return shape(arm, CH_BR, blob(rect_pts(x - 310 * k, y + 20 * k, x - 70 * k, y + 210 * k), CH_BR_SH, .85)
                 + blob(ellipse_pts(x - 200 * k, y - 140 * k, 100 * k, 22 * k, 14), CH_BR_HI, .9), w=5, seed=9465)


def speaking(t, amp=.3, base=.08):
    for w in WORDS:
        if w["start"] - .03 <= t <= w["end"]:
            ph = (t - w["start"]) / max(.08, (w["end"] - w["start"])) * max(1, len(w["word"]) // 3)
            return base + amp * abs(math.sin(math.pi * ph))
    return 0.0


def s10(t):
    # отец: сидит лицом влево; «человеку» поднимает глаза, «лично» — ладонь на сердце, глаза блестят
    fx, fs = FA10
    fsc = fs * PE.HEIGHT["father"]
    fy = FL10 - 24 - 300 * fsc
    up = sm(t, T10_CHEL - .05, T10_CHEL + .3)
    hrt = sm(t, T10_LICH - .1, T10_LICH + .35)
    fex = ex_mix(E("father", "serious"), E("father", "look_up"), up)
    fex = ex_mix(fex, dict(E("father", "moved"), look=(.35, -.25), tear=.8), hrt)
    if hrt > .6:
        fex["mouth"], fex["smile"] = "smile", .55 * hrt
    fex["closed"] = max(bump(t, 24.4, .16), bump(t, 26.1, .16))
    knee = (230.0, -40.0)
    heart = (55.0, -250.0)
    ln = (lerp(knee[0], heart[0], hrt), lerp(knee[1], heart[1], hrt))
    farms = {"n": ("ik", (fx + ln[0] * fsc, fy + ln[1] * fsc), -1), "f": ("ik", (fx + 250 * fsc, fy - 30 * fsc), -1)}
    fh_n = {"curl": (.4, .4, .45, .5), "thumb": .4, "dir": (1, .4)} if hrt < .5 else {"dir": (-.3, -1), "curl": (.15, .15, .2, .25), "spread": .12, "thumb": .2}
    fhands = {"n": fh_n, "f": {"curl": (.45, .45, .5, .55), "thumb": .4, "dir": (1, .3)}}
    ffeet = {"n": ((fx + 330 * fsc, FL10 - 20), 0.0), "f": ((fx + 285 * fsc, FL10 - 26), 0.0)}     # ноги в координатах до зеркала (flip)
    fkw = dict(feet=ffeet, flip=True, arms=farms, hands=fhands, lean_add=.05 - .08 * up + .015 * math.sin(t * 1.9), head_add=-.12 * up + .03 * math.sin(t * 1.3))
    f_low = PE.old_father(fx, fy, fs, fex, None, layers=("legs", "pelvis", "arm_f", "body"), **fkw)
    f_arm = PE.old_father(fx, fy, fs, fex, None, layers=("arm_n",), **fkw)
    # дочь: стоит, держит письмо двумя руками, читает вслух; на «лично» поднимает глаза на отца и смущённо улыбается
    cx_, cs = CUR10
    csc = cs * PE.HEIGHT["curly"]
    cy_ = FL10 - (PE.LEG_LEN - 12) * csc
    shy = sm(t, T10_LICH - .05, T10_LICH + .4)
    cex = ex_mix(dict(E("curly", "serious"), look=(.45, .6), brows="calm"), E("curly", "shy"), shy)
    if shy < .5:
        cex["mouth"] = "talk"
        cex["open"] = speaking(t, .28, .05)
        cex["smile"] = .15
    cex["look"] = (lerp(.45, .6, shy), lerp(.6, -.05, shy))
    cex["closed"] = bump(t, 24.7, .15)
    Lc = (cx_ + 250 * csc, cy_ - 330 * csc + 3 * math.sin(t * 2.3) + 18 * shy)
    lk = csc * .82
    lw, lh = 200.0, 250.0
    Gl = (Lc[0] - lw / 2 * lk + 6, Lc[1] + 30 * lk)
    Gr = (Lc[0] + lw / 2 * lk - 6, Lc[1] + 40 * lk)
    carms = {"f": ("ik", (Gl[0] - 50 * csc, Gl[1] + 40 * csc), -1), "n": ("ik", (Gr[0] + 30 * csc, Gr[1] + 55 * csc), -1)}
    chands = {"f": {"kind": "none"}, "n": {"kind": "none"}}
    cfeet = PE.stand_kw(cx_, cy_, cs, "curly", spread=60)["feet"]
    ckw = dict(feet=cfeet, arms=carms, hands=chands, lean_add=.03 * math.sin(t * 1.6) + .04 * shy, head_add=.06 - .1 * shy, shrug=.25 * shy)
    c_body = PE.participant("curly", cx_, cy_, cs, cex, None, layers=("legs", "pelvis", "arm_f", "body", "arm_n"), **ckw)
    gbl, gfl = PE.grip_svg("curly", Gl, 6 * lk, -1, k=csc * .95, h=64, seed=9470)
    gbr, gfr = PE.grip_svg("curly", Gr, 6 * lk, +1, k=csc * .95, h=64, seed=9471)
    letter = P.letter(Lc[0], Lc[1], lk, 4 - 3 * shy, lw, lh, write=1.0, seed=21)
    body = (living_bg(t) + armchair10(fx, fy, fsc) + f_low["svg"] + armchair10_arm(fx, fy, fsc) + f_arm["svg"]
            + c_body["svg"] + gbl + gbr + letter + gfl + gfr)
    if hrt > .5:
        hd = f_low["head"]
        body += P.sparkles(hd[0] - 40, hd[1] - 20, .9, (hrt - .5) * 2, t, seed=4, n=2, r=110)
    # камера: мягкий наезд, дрейф от дочери к отцу и обратно на «лично»
    a = sm(t, 23.84, 26.6)
    cx = lerp(470, 600, sm(t, 24.4, 25.3)) - 60 * shy
    cy = lerp(1090, 1050, a)
    s = lerp(1.0, 1.14, a)
    set_ink(s)
    return cam_wrap(body, cx, cy, s, .5 * math.sin(t * .8), bg="#e7d7c0")


# ═════════════════════════ s11: три лица в ряд — серые заливаются цветом ═════════════════════════
T11_SCH, T11_CHUV = wt(51), wt(55)           # «Счастливее» 26.40, «чувствовали» 28.29
ROW11 = [("curly", 215.0, 1520.0, .9, 0.0), ("beard", 520.0, 1440.0, .9, .32), ("father", 865.0, 1530.0, .9, .64)]


def s11(t):
    o = [blob(rect_pts(-900, -900, 2000, 2900), "#efe3cf")]
    # мягкие тёплые полосы фона (бумага), без пятен света
    for i in range(-6, 14):
        o.append(blob(rect_pts(-900, i * 180, 2000, i * 180 + 90), "#eadcc4", .8))
    for who, x, y, sc, d in ROW11:
        tc = T11_SCH + .12 + d * 1.15
        col = ease_io(clamp((t - tc) / .55))
        happy = ease_out(clamp((t - tc - .1) / .5))
        e0 = E(who, "serious")
        e1 = dict(E(who, "happy" if who != "father" else "happy"))
        ex = ex_mix(e0, e1, happy)
        if who == "father":
            ex = ex_mix(ex, dict(E("father", "happy"), tear=.6), 1.0) if happy > .5 else ex
        ex["look"] = (lerp(.3, -.2, happy), lerp(.4, 0.0, happy))
        lean = .02 * math.sin(t * 1.8 + d * 5)
        head = .03 * math.sin(t * 1.4 + d * 3) - .06 * happy
        arms = None
        hands = None
        pose = None
        # «чувствовали»: бородач смеётся, участница прикрывает рот ладонью
        lu = ease_out(clamp((t - T11_CHUV + .05) / .3))
        if who == "beard" and lu > 0:
            ex = ex_mix(ex, E("beard", "laugh"), lu)
            hh = abs(math.sin((t - T11_CHUV) * 2 * math.pi * 3.0))
            ex["open"] = ex.get("open", .8) * (.65 + .35 * hh)
            head -= .22 * lu
            lean -= .08 * lu + .03 * hh * lu
        if who == "curly":
            pose = "hand_mouth"
            hm = lu
            kw0 = PE.pose_kw("hand_mouth", x, y, sc, "curly")
            tgt_up = kw0["arms"]["n"][1]
            rest = (x + 150 * sc * PE.HEIGHT["curly"], y + 120 * sc)
            arms = {"f": ("ang", .18, .2), "n": ("ik", (lerp(rest[0], tgt_up[0], hm), lerp(rest[1], tgt_up[1], hm)), -1)}
            hands = {"n": {"dir": (.1, -1), "curl": (.15, .15, .2, .25), "spread": .1, "thumb": .2}}
            if hm > .3:
                ex = ex_mix(ex, E("curly", "cover"), hm)
                ex["look"] = (-.2, 0.0)
        ex["closed"] = bump(t, 26.55 + d * 2.1, .15)
        fig = PE.figure(who, x, y, sc, ex, lean=lean + (PE.POSE["hand_mouth"][0] if pose else 0), head_ang=head, arms=arms or {"f": ("ang", .18, .2), "n": ("ang", -.05, .25)},
                        hands=hands, layers=("body", "arm_n") if who == "curly" else ("body",), flip=(who == "father"))
        flt = P.desat(1 - col)
        o.append(f'<g {flt}>{fig["svg"]}</g>' if flt else fig["svg"])
        if happy > .2:
            hx, hy = fig["head"]
            o.append(P.sparkles(hx + 30, hy - 10, .9, happy, t, seed=int(x) % 11, n=3, r=130))
    # стол перед ними закрывает низ (таз), на столе — три листа-письма
    ty = 1395.0
    o.append(shape(rect_pts(-400, ty, 1480, ty + 60), "#c99a62", blob(rect_pts(-400, ty + 44, 1480, ty + 60), "#a07440"), w=4, seed=9480))
    o.append(shape(rect_pts(-400, ty + 60, 1480, 2600), "#b4834f", blob(rect_pts(-400, ty + 60, 1480, ty + 90), "#946235"), w=4, seed=9481))
    for j, (lx, rr) in enumerate(((260, -8), (560, 5), (860, -3))):
        o.append(P.letter(lx, ty + 22, .5, rr, 200, 250, write=1.0, seed=30 + j, sy=.22))
    a = ease_io(clamp((t - 26.2) / 3.2))
    cx, cy, s = 540, lerp(1110, 1130, a), lerp(1.36, 1.26, a)
    sx = 0.0
    if t > T11_CHUV:
        h = t - T11_CHUV
        sx = 6 * math.exp(-4 * h) * math.sin(h * 50)
    set_ink(s)
    return cam_wrap("".join(o), cx + sx, cy, s, .4 * math.sin(t * .9), bg="#efe3cf")


def frame(sid, t):
    lib.dyn_begin()
    lib.DEFS.clear()
    return {"s09": s09, "s10": s10, "s11": s11}[sid](t)
