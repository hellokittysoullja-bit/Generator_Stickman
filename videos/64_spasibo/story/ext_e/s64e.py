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
HALL_FLOOR = 1520.0
SIT9 = 1290.0
PS9 = 0.66
STATIONS = [("youth", 330.0, 0.0), ("beard", 1080.0, .10), ("curly", 1830.0, .20)]   # кто, таз x, сдвиг начала


def hall_back(t):
    o = [blob(rect_pts(-1400, -900, 3600, HALL_FLOOR), "#F3EBDC")]
    o.append(blob(rect_pts(-1400, HALL_FLOOR - 120, 3600, HALL_FLOOR), "#EADFCB"))
    o.append(line([(-1400, HALL_FLOOR - 120), (3600, HALL_FLOOR - 118)], 4, INK, taper=0, wmin=.8, seed=9001))
    o.append(blob(rect_pts(-1400, HALL_FLOOR, 3600, 2800), "#D9C3A0"))
    for j in range(-6, 26):        # доски пола
        x = j * 170
        o.append(line([(x, HALL_FLOOR + 8), (x - 60, 2700)], 2.4, "#BFA47D", taper=0, wmin=.6, seed=9010 + j))
    o.append(line([(-1400, HALL_FLOOR), (3600, HALL_FLOOR + 2)], 5, INK, taper=0, wmin=.8, seed=9002))
    # высокие окна между местами: рамы и полосы дневного света на полу (форма окна, без овалов)
    for j, wx in enumerate((-60, 705, 1455, 2205)):
        x0, x1, y0, y1 = wx - 150, wx + 150, 330, 1060
        sky = blob(rect_pts(x0, y0, x1, y1), "#CFE6F2") + blob(rect_pts(x0, y1 - 160, x1, y1), "#DCEFE0")
        sky += blob(ellipse_pts(x0 + 90, y1 - 150, 110, 70, 14), "#A9CF9A") + blob(ellipse_pts(x1 - 60, y1 - 130, 90, 60, 14), "#9CC48C")
        o.append(shape(rect_pts(x0, y0, x1, y1), "#CFE6F2", sky, w=5, seed=9100 + j))
        o.append(line([(wx, y0), (wx, y1)], 7, "#FFFFFF", taper=0, wmin=1, seed=9110 + j))
        o.append(line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], 7, "#FFFFFF", taper=0, wmin=1, seed=9120 + j))
        o.append(shape(rect_pts(x0 - 18, y1, x1 + 18, y1 + 22), "#FFFFFF", "", w=3.4, seed=9130 + j))
        # полоса света на полу: трапеция формы окна
        o.append(blob([(x0 + 40, HALL_FLOOR + 14), (x1 + 40, HALL_FLOOR + 14), (x1 + 230, HALL_FLOOR + 330), (x0 + 230, HALL_FLOOR + 330)], "#E7D3B0"))
    return "".join(o)


def chair9(x, y, sc, seed):
    """Стул участника: спинка слева от таза (смотрит вправо), сиденье под тазом."""
    o = []
    bx = x - 150 * sc
    o.append(shape([(bx - 18 * sc, y + 40 * sc), (bx - 30 * sc, y - 360 * sc), (bx + 10 * sc, y - 360 * sc), (bx + 16 * sc, y + 40 * sc)],
                   "#7C9AB8", blob(rect_pts(bx, y - 350 * sc, bx + 12 * sc, y + 40 * sc), "#5E7D9C"), w=4, seed=seed))
    o.append(shape(lib.rrect(bx - 26 * sc, y - 380 * sc, bx + 24 * sc, y - 200 * sc, 14 * sc), "#8BA9C6", "", w=4, seed=seed + 1))
    leg_y = HALL_FLOOR + 8
    for j, lx in enumerate((x - 140 * sc, x + 110 * sc)):
        o.append(shape(rect_pts(lx - 9 * sc, y + 40 * sc, lx + 9 * sc, leg_y), "#5E6B78", "", w=3.4, seed=seed + 3 + j))
    return "".join(o)


def seat_front9(x, y, sc, seed):
    return shape(lib.rrect(x - 170 * sc, y + 10 * sc, x + 140 * sc, y + 52 * sc, 12 * sc), "#8BA9C6",
                 blob(rect_pts(x - 170 * sc, y + 34 * sc, x + 140 * sc, y + 52 * sc), "#6E8CAA"), w=4, seed=seed)


def write_u(t, d):
    """Сколько письма написано: с «написать» строки идут быстро, к «благодарности» лист полон."""
    return 1.0 * ease_out(clamp((t - (T9_WRITE - .5 + d * .3)) / (T9_THANKS - .12 - (T9_WRITE - .5 + d * .3))), 1.4)


def station(who, X, d, t, look_cam=0.0):
    """Участник за столом пишет письмо; к «благодарности» рисует внизу сердечко и улыбается."""
    sc = PS9 * PE.HEIGHT[who]
    Y = SIT9 + 3 * math.sin(t * 1.7 + X)
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
    kw["feet"] = {"n": ((X + 330 * sc, HALL_FLOOR + 40), 0.0), "f": ((X + 280 * sc, HALL_FLOOR + 30), 0.0)}
    fig = PE.figure(who, X, Y, PS9, ex, layers=("legs", "pelvis"), **kw)
    upper = PE.figure(who, X, Y, PS9, ex, layers=("arm_f", "body"), **kw)
    arm_f = PE.figure(who, X, Y, PS9, ex, layers=("arm_f",), **kw)
    arm_n = PE.figure(who, X, Y, PS9, ex, layers=("arm_n",), **kw)
    o = [chair9(X, Y, sc, 9300 + int(X)), fig["svg"], seat_front9(X, Y, sc, 9320 + int(X))]
    o.append(clip_y(upper["svg"], -3000, yb + 6))
    # стол: крышка от yb до yf, кромка и ножки
    o.append(P.desk(X + 250 * sc, yf, 640 * sc, 1.0, depth=yf - yb, legs=True, seed=int(X) % 50, leg_h=HALL_FLOOR - yf - 10))
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
    for who, X, d in STATIONS:
        sv, inf = station(who, X, d, t)
        o.append(sv)
        info[who] = inf
        if inf["smile"] > .3:
            hx, hy = inf["head"]
            o.append(P.sparkles(hx + 40, hy - 40, 1.1, inf["smile"] * .9, t, seed=int(X) % 13, n=3, r=150))
    # камера: с ближнего плана юноши — панорама вдоль столов с отъездом (видны все трое к «благодарности»),
    # потом наезд на ближний лист и лицо женщины с кудрями
    a = sm(t, 21.6, 22.95)
    b = sm(t, 23.2, 24.25)
    cx = lerp(lerp(470, 1080, a), info["curly"]["letter"][0] - 60, b)
    cy = lerp(lerp(1060, 1010, a), info["curly"]["letter"][1] - 170, b)
    s = lerp(lerp(1.05, .5, ease_out(a, 1.6)), 1.12, ease_in(b, 1.3))
    rot = lerp(-1.2, .6, a) + lerp(0, -.8, b)
    set_ink(s)
    return cam_wrap("".join(o), cx, cy, s, rot, bg="#F3EBDC")


def frame(sid, t):
    lib.dyn_begin()
    lib.DEFS.clear()
    return {"s09": s09}[sid](t)
