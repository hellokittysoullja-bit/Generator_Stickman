"""Рилс 104 «Не жди мотивацию», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Говорит Дима от первого лица (имя не звучит и не пишется). Сквозной образ: папка «ОТЧЁТ» на столе в паутине и пыли,
настенный календарь с 30 зачёркнутыми днями, красный штамп «СДАН». NOCAM=1 — без влёта, тряски и надписей."""
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(1, os.path.join(REPO, "scripts"))
import big_title  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import cat as CT  # noqa: E402
import props as PR  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402,F401

_sp = importlib.util.spec_from_file_location("alarm104", os.path.join(STORY, "common", "alarm.py"))
AL = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(AL)

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
END = SH["end"]
NOCAM = bool(os.environ.get("NOCAM"))


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def stress(i, u):
    return W(i) + (WE(i) - W(i)) * u


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up=.08, down=.3):
    if a is None:
        return 0.0
    u = t - a
    if u <= 0:
        return 0.0
    return min(1.0, u / up) * (math.exp(-(u - up) / down) if u > up else 1.0)


def shake(t, a, amp=10.0, dur=.35, f=11.0):
    if a is None or NOCAM:
        return 0.0, 0.0
    u = t - a
    if u <= 0 or u > dur * 3:
        return 0.0, 0.0
    e = math.exp(-u / dur * 2.5)
    return amp * e * math.sin(2 * math.pi * f * u), amp * .6 * e * math.cos(2 * math.pi * f * .8 * u)


def pop(t, a, d=.24):
    u = clamp((t - a) / d)
    return lib.back_out(u, 2.2) if u < 1 else 1.0


def ease_in(u):
    return lib.ease_in(u, 2)


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def tf(inner, x, y, k=1.0, rot=0.0):
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{inner}</g>'


def txt(s, x, y, size, fill="#FFFFFF", stroke="#111", sw=None, anchor="middle", op=1.0):
    sw = size * .09 if sw is None else sw
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-size="{size:.1f}" text-anchor="{anchor}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw:.1f}" stroke-linejoin="round" paint-order="stroke"{o} '
            f'style="font-kerning:none">{s}</text>')


# ═════════════════════════ экранные надписи ═════════════════════════
def title(t):
    if NOCAM:
        return ""
    ti = SH["title"]
    return big_title.layer(t, text=ti["text"], t_in=ti["t_in"], t_out=ti["t_out"], hits=[W(i) for i in ti["hits"]])


def label(t):
    """«ВОТ ЧТО Я ПОМЕНЯЛ» — маленькая надпись сверху, только на фразе 6."""
    lb = SH["label"]
    a, b = lb["t_in"], lb["t_out"]
    if NOCAM or t < a or t > b + .2:
        return ""
    k = pop(t, a, .25)
    op = 1 - ramp(t, b, .2)
    k *= 1 - .15 * ramp(t, b, .2)
    body = (f'<rect x="-330" y="-62" width="660" height="92" rx="22" fill="#FFD23F" stroke="#111" stroke-width="6"/>'
            + txt(lb["text"], 0, 8, 58, "#111", "#111", 0))
    return f'<g transform="translate(540 236) rotate(-2) scale({max(.01, k):.3f})" opacity="{op:.3f}">{body}</g>'


def weekend(t):
    """«ВЫХОДНЫЕ МОИ» — крупно сверху на последней фразе."""
    wk = SH["weekend"]
    if NOCAM:
        return ""
    return big_title.layer(t, text=wk["text"], t_in=wk["t_in"], t_out=wk["t_out"], hits=[W(i) for i in wk["hits"]], style="yellow")


def over(t):
    return title(t) + label(t) + weekend(t)


BG = "#efe2c8"


def view(body, cx, cy, s, rot=0.0, bg=BG, t=0.0, extra=""):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{extra}{over(t)}')


# ═════════════════════════ комната ═════════════════════════
FL = 1300.0
WALL, WALL_SH, FLOOR_C = "#efe2c8", "#e3d2b2", "#cdb48c"
NIGHT = "#2a3150"


def room(t, x0=-1400.0, x1=2600.0, dusk=0.0, night=0.0, wall=None):
    wc = lib.mix(lib.mix(wall or WALL, "#e0b18a", dusk), "#4a4f72", night)
    sh = lib.mix(lib.mix(WALL_SH, "#d29c78", dusk), "#41466a", night)
    o = [rect(x0, -1400, x1, FL, wc)]
    for i in range(int(x0 // 120), int(x1 // 120) + 1):
        xa = i * 120
        o.append(rect(xa, -1400, xa + 46, FL, sh, .55))
    o.append(rect(x0, FL - 46, x1, FL, lib.mix("#d8c3a0", "#3d4263", night)))
    o.append(line([(x0, FL - 46), (x1, FL - 46)], 3, seed=7))
    o.append(rect(x0, FL, x1, FL + 1400, lib.mix(lib.mix(FLOOR_C, "#c49470", dusk), "#353a58", night)))
    o.append(line([(x0, FL), (x1, FL)], 5, seed=11))
    for i in range(int(x0 // 300), int(x1 // 300) + 1):
        xa = i * 300
        o.append(line([(xa, FL + 20), (xa + (xa - 540) * .9, FL + 900)], 2.4, lib.mix("#b0966c", "#2c3150", night), seed=20 + i % 9, op=.8))
    return "".join(o)


def chair(x, y, k=1.0, night=0.0):
    c = lib.mix("#a8774a", "#5a4a5a", night)
    c2 = lib.mix("#8a6038", "#4a3c4c", night)
    o = [shape(lib.rrect(-100, -16, 110, 10, 6), c, "", w=4, seed=1011)]
    o.append(shape([(-100, -16, 1), (-80, -16, 1), (-70, -330, 1), (-92, -330, 1)], c, "", w=4, seed=1012))
    for s in (-1, 1):
        o.append(shape([(s * 80 - 9, 8, 1), (s * 80 + 9, 8, 1), (s * 86 + 9, 240, 1), (s * 86 - 9, 240, 1)], c2, "", w=3.4, seed=1013 + s))
    return tf("".join(o), x, y, k)


def sofa(x, y, k=1.0):
    o = shape(lib.rrect(-300, -320, 300, -120, 44), "#8aa0c8", "", w=4.4, seed=9750)
    o += shape(lib.rrect(-340, -170, 340, -40, 30), "#9db2d8", "", w=4.4, seed=9751)
    for s in (-1, 1):
        o += shape(lib.rrect(s * 340 - 54, -240, s * 340 + 54, -30, 30), "#7d93bb", "", w=4.4, seed=9752 + s)
        o += line([(s * 280, -30), (s * 290, 0)], 10, INK, taper=0, wmin=1, seed=9754 + s)
    return tf(o, x, y, k)


def wall_clock(x, y, r, hh, mm, seed=0, wob=0.0):
    ah, am = PR.clock_hm(hh, mm)
    c = PR.clock(x, y, r, angle_h=ah, angle_m=am, seed=seed)
    if abs(wob) > .01:
        c = f'<g transform="rotate({wob:.2f} {x:.1f} {y - r:.1f})">{c}</g>'
    return c


def stand_hip(k, fl=FL):
    return fl - (people.LEG_LEN - 12) * k - 6


def cat(x, y, k, t, st=None):
    st = dict(dict(look=(-.6, -.3), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t)


def sky_window(x, y, w, h, t, phase=0.0, night=0.0, seed=3):
    """Окно (центр дна рамы (x, y)): небо по фазе дня 0 утро → 1 закат (солнце уходит вниз, небо рыжеет); night — ночь."""
    if night > .5:
        return PR.window(x, y, w, h, mode="night", t=t, seed=seed, curtain=False)
    o = [PR.window(x, y, w, h, mode="day", t=t, seed=seed, curtain=False)]
    x0, y0, x1, y1 = x - w / 2 + 18, y - h + 18, x + w / 2 - 18, y - 18
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    top = lib.mix("#8fd0f4", "#f08a5d", phase)
    bot = lib.mix("#d9f1fb", "#ffd58a", phase)
    g = lib.lin_grad([(0, top, 1), (1, bot, 1)], 0, 0, 0, 1)
    sx = x0 + (x1 - x0) * (.2 + .6 * phase)
    sy = y0 + (y1 - y0) * (.18 + .85 * phase * phase)
    sc = lib.mix("#FFD23F", "#ff7a3c", phase)
    inner = (f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="url(#{g})"/>'
             + PR.glow(sx, sy, 120, .7, sc)
             + shape(ellipse_pts(sx, sy, 44, 44, 20), sc, "", w=3.4, seed=seed + 40)
             + blob([(x0, y1 - 60), (x0 + 120, y1 - 100), (x1 - 80, y1 - 70), (x1, y1 - 90), (x1, y1), (x0, y1)], lib.mix("#9cc58a", "#a0715a", phase)))
    o.append(f'<g clip-path="url(#{c})">{inner}</g>')
    # крестовина рамы поверх неба
    o.append(line([(x, y0), (x, y1)], 14, "#f4efe4", taper=0, wmin=1, seed=seed + 50))
    o.append(line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], 14, "#f4efe4", taper=0, wmin=1, seed=seed + 51))
    o.append(line([(x, y0), (x, y1)], 3, INK, taper=0, wmin=1, seed=seed + 52, op=.6))
    return "".join(o)


# ═════════════════════════ папка «ОТЧЁТ», календарь, штамп ═════════════════════════
FOLD_C, FOLD_SH = "#E8B04B", "#C98E2E"
WEB_C = "#7d7872"
STAMP_DX = 138.0


def folder(x, y, k=1.0, t=0.0, dust=1.0, web=1.0, tremble=0.0, stamp=0.0, seed=0, rot=0.0, label=True, torn=0.0):
    """Толстая папка на столе (центр дна (x, y)), видна передом и верхом: корешок с наклейкой «ОТЧЁТ», стопка листов
    торчит сбоку. dust — серый налёт и крапинки, web — паутина от угла папки вверх; stamp 0…1 — оттиск «СДАН» проявлен."""
    sd = 30400 + seed
    o = [blob(ellipse_pts(10, 4, 250, 20, 18), "#3a2a20", .18)]
    # листы, торчащие из папки
    for j in range(3):
        o.append(shape(lib.rect_pts(-196 + 6 * j, -150 + 9 * j, 200 - 10 * j, -22 + 4 * j), "#fbf6e6", "", w=2.6, seed=sd + j))
    # верхняя створка (в перспективе)
    top = [(-226, -150, 1), (-196, -196, 1), (230, -196, 1), (238, -150, 1)]
    o.append(shape(top, lib.mix(FOLD_C, "#ffffff", .12), blob([(-60, -196), (-20, -214), (60, -214), (90, -196)], FOLD_C), w=4.0, seed=sd + 5))
    o.append(blob([(-60, -196), (-48, -216), (70, -216), (84, -196)], FOLD_C))
    o.append(line([(-60, -196), (-48, -216), (70, -216), (84, -196)], 3.6, INK, taper=0, wmin=1, seed=sd + 6))
    # перёд папки
    front = lib.rect_pts(-238, -150, 240, 0)
    inner = blob(lib.rect_pts(-238, -40, 240, 0), FOLD_SH, .55)
    o.append(shape(front, FOLD_C, inner, w=4.6, seed=sd + 7))
    o.append(line([(-238, -148), (240, -148)], 3, INK, taper=0, wmin=1, seed=sd + 8, op=.5))
    if label:
        o.append(shape(lib.rrect(-215, -124, 35, -40, 10), "#fffdf6", "", w=3.4, seed=sd + 9))
        o.append(txt("ОТЧЁТ", -90, -62, 64, "#1d2448", "#fffdf6", 0))
    if stamp > .01:
        o.append(stamp_print(STAMP_DX, -80, .8, stamp))
    if dust > .01:
        rs = PR._rs(sd + 20)
        o.append(blob([(-226, -150), (-196, -196), (230, -196), (238, -150)], "#9c958a", .32 * dust))
        o.append(blob(lib.rect_pts(-238, -150, 240, -132), "#9c958a", .25 * dust))
        sp = []
        for _ in range(int(70 * dust)):
            px = rs.uniform(-230, 236)
            py = rs.uniform(-196, -6) if rs.uniform(0, 1) < .6 else rs.uniform(-196, -150)
            r = rs.uniform(1.4, 3.6)
            sp.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}"/>')
        o.append(f'<g fill="#7d766c" opacity="{.6 * dust:.3f}">{"".join(sp)}</g>')
    if web > .01:
        o.append(f'<g opacity="{web:.3f}">' + PR.cobweb(-226, -150, 1.5, tremble, torn, t, ang=-160, span=100, L=210, seed=seed + 1, col=WEB_C)
                 + PR.cobweb(238, -150, 1.2, tremble, torn, t, ang=-80, span=100, L=170, seed=seed + 2, col=WEB_C) + "</g>")
    return tf("".join(o), x, y, k, rot)


def stamp_print(x, y, k=1.0, u=1.0):
    """Красный оттиск «СДАН» в рамке, слегка повёрнут."""
    u = clamp(u)
    body = (f'<rect x="-120" y="-50" width="240" height="100" rx="12" fill="none" stroke="#d5302a" stroke-width="10"/>'
            f'<rect x="-106" y="-38" width="212" height="76" rx="8" fill="none" stroke="#d5302a" stroke-width="3"/>'
            + txt("СДАН", 0, 24, 70, "#d5302a", "#d5302a", 0))
    return f'<g opacity="{.9 * u:.3f}" transform="translate({x:.1f} {y:.1f}) rotate(-9) scale({k * (1 + .25 * (1 - u)):.4f})">{body}</g>'


def stamp(x, y, k=1.0, rot=0.0, squash=0.0):
    """Штамп: деревянная ручка-груша, шейка, красная подушка. (x, y) — низ подушки (место удара)."""
    sq = clamp(squash)
    sy = 1 - .16 * sq
    sx = 1 + .12 * sq
    o = [shape(lib.rrect(-130, -60, 130, 0, 10), "#d5302a", blob(lib.rect_pts(-130, -20, 130, 0), "#a51f1a", .8), w=4.6, seed=30500)]
    o.append(shape(lib.rrect(-110, -100, 110, -56, 8), "#6b4a32", blob(lib.rect_pts(-110, -70, 110, -56), "#4e3524"), w=4.2, seed=30501))
    o.append(shape(lib.rect_pts(-30, -190, 30, -98), "#8a6038", blob(lib.rect_pts(6, -190, 30, -98), "#6b4a32"), w=4.0, seed=30502))
    o.append(shape(ellipse_pts(0, -250, 78, 72, 24), "#a8774a", blob(ellipse_pts(-22, -272, 26, 20, 12), "#c79a6a"), w=4.4, seed=30503))
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k * sx:.4f} {k * sy:.4f})">{"".join(o)}</g>'


def calendar30(x, y, t, crossed=30, t0=None, t1=None, w=520.0, h=560.0, pulse=0.0, seed=0, night=0.0):
    """Настенный календарь 6×5 = 30 клеток; дни зачёркиваются красными крестами. crossed — сколько крестов стоит
    (если даны t0, t1 — кресты появляются по одному от t0 до t1)."""
    o = []
    paper_c = lib.mix("#fffdf6", "#c9cbe0", night)
    o.append(shape(lib.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, 16), paper_c,
                   blob(lib.rect_pts(x - w / 2, y - h / 2, x + w / 2, y - h / 2 + 92), lib.mix("#E9576A", "#8a4a62", night)), w=5, seed=2001 + seed))
    for j in range(5):
        rx = x - w / 2 + 80 + j * (w - 160) / 4
        o.append(line([(rx, y - h / 2 - 30), (rx, y - h / 2 + 20)], 11, "#8a8f99", taper=0, wmin=1, seed=2002 + j))
    cw, ch = (w - 50) / 6, (h - 130) / 5
    n = 0
    for r in range(5):
        for c in range(6):
            cx = x - w / 2 + 25 + cw * (c + .5)
            cy = y - h / 2 + 110 + ch * (r + .5)
            o.append(shape(lib.rrect(cx - cw / 2 + 5, cy - ch / 2 + 5, cx + cw / 2 - 5, cy + ch / 2 - 5, 7), lib.mix("#f3eee2", "#b9bbd2", night), "",
                           w=2.4, seed=2010 + n))
            if t0 is not None:
                ta = t0 + (t1 - t0) * n / 29
                u = clamp((t - ta) / .1)
            else:
                u = 1.0 if n < crossed else 0.0
            if u > 0:
                s = 1 + .5 * bump(t, ta, .03, .12) if t0 is not None else 1.0
                s *= 1 + .18 * pulse
                q = cw * .32 * s
                o.append(PR.cross_stroke((cx - q, cy - q), (cx + q, cy + q), (cx - q, cy + q), (cx + q, cy - q), u, w=9, seed=n + 7 * seed, col="#d5302a"))
            n += 1
    return "".join(o)


def dust_motes(x0, y0, x1, y1, t, n=16, seed=0, col="#fff6dc", op=.75, gust=0.0):
    """Пылинки в луче: плывут вверх-вбок, мерцают; gust — порыв (разлетаются быстрее)."""
    rs = PR._rs(31000 + seed)
    o = []
    for j in range(n):
        ph = rs.uniform(0, 1)
        sp = rs.uniform(.12, .3) * (1 + 3 * gust)
        u = (ph + t * sp) % 1.0
        px = x0 + (x1 - x0) * ((rs.uniform(0, 1) + .25 * math.sin(t * .9 + j)) % 1.0)
        py = y1 - (y1 - y0) * u
        r = rs.uniform(3, 7)
        a = op * math.sin(math.pi * u) * (.6 + .4 * math.sin(t * 7 + j))
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="{col}" opacity="{max(0, a):.3f}"/>')
    return "".join(o)


def dust_burst(x, y, k, u, seed=0):
    """Пыль разлетается от удара во все стороны (u 0…1)."""
    if u <= 0 or u >= 1:
        return ""
    rs = PR._rs(31500 + seed)
    o = [PR.dust_puff(x, y, k * .7, u, seed)]
    for j in range(22):
        a = rs.uniform(math.pi * 1.0, math.pi * 2.0) if j % 3 else rs.uniform(0, math.pi * 2)
        d = (60 + 360 * ease_out(u, 2)) * k * rs.uniform(.5, 1.1)
        r = rs.uniform(6, 16) * k * (1 - u)
        o.append(blob(ellipse_pts(x + math.cos(a) * d, y + math.sin(a) * d * .6 - 40 * k * u, r, r, 10), "#c7c0b3", .8 * (1 - u)))
    return "".join(o)


# ═════════════════════════ стол Димы ═════════════════════════
DX, DHIP, DK = 330.0, FL - 290, .5
DESK = (690.0, FL - 300)
LAP = (600.0, FL - 330)
FOLD = (880.0, FL - 318)
CAT_AT = (1030.0, DESK[1] - 92)
WIN = (150.0, 840.0)
CAL = (560.0, 520.0)
CLOCK = (900.0, 330.0)


def dima_sit(x, hip, k, expr, t, pose="sit_desk", lean=0.0, head_add=0.0, flip=False, **kw):
    feet = people.sit_kw(x, hip, k)["feet"]
    return people.dima82(x, hip, k, expr, pose, t=t, feet=feet, lean_add=lean, head_add=head_add, flip=flip, **kw)


def desk_world(t, dima="type", clock=(10, 0), cat_st=None, cat_dy=0.0, cat_x=None, phase=0.0, night=0.0, lap_screen="dark", lap_lines=0.0,
               lap_open=1.0, fold=None, cal=None, laptop=True, extra_desk="", desk_w=820):
    """Комната со столом. dima — готовая фигура (dict), "type" — печатает, None — нет; fold — kwargs папки или None (нет)."""
    o = [room(t, dusk=.6 * phase, night=night)]
    o.append(sky_window(WIN[0], WIN[1], 300, 420, t, phase, night))
    if cal is None:
        o.append(calendar30(CAL[0], CAL[1], t, 30, w=420, h=450, night=night))
    elif cal:
        o.append(cal)
    if clock is not None:
        o.append(wall_clock(*CLOCK, 74, clock[0], clock[1], seed=1, wob=clock[2] if len(clock) > 2 else 0.0))
    o.append(chair(DX - 40, FL - 240, 1.0, night))
    o.append(PR.desk(DESK[0], DESK[1], w=desk_w, depth=100, leg_h=260, seed=7))
    f = None
    if dima == "type":
        f = dima_sit(DX, DHIP, DK, "type73", t, pose="sit_desk", lean=.12 + .03 * math.sin(t * 9))
    elif dima:
        f = dima
    if f:
        o.append(f["svg"])
    if fold is not None:
        o.append(folder(FOLD[0], FOLD[1] + 40, .55, t, **fold))
    if laptop:
        o.append(PR.laptop(LAP[0], LAP[1], .5, open_=lap_open, screen=lap_screen, lines=lap_lines, t=t))
    o.append(extra_desk)
    if cat_st is not False:
        o.append(cat(cat_x or CAT_AT[0], CAT_AT[1] - cat_dy, .36, t, cat_st))
    if night > .01:
        o.append(f'<rect x="-1400" y="-1400" width="4000" height="4000" fill="#0a0e26" opacity="{.28 * night:.3f}"/>')
        o.append(PR.glow(LAP[0], LAP[1] - 120, 420, .55 * night, "#a9c6ff"))
    return "".join(o), f


# ═════════════════════════ хук: папка в паутине, календарь, s01 / петля s26 ═════════════════════════
HIT = stress(2, .35)          # «мотиВАцию»: последний, тридцатый крест бьёт по календарю


HCAL = (600.0, 585.0)
HFOLD = (770.0, DESK[1] - 20)


def hook_world(t, tt):
    """Стол крупно: папка «ОТЧЁТ» в пыли и паутине, паук качается, пылинки в луче; на стене календарь — дни
    зачёркиваются один за другим с кадра 0, тридцатый крест бьёт на «мотивацию»; кот на столе дёргает хвостом."""
    o = [room(t)]
    o.append(sky_window(WIN[0] - 60, WIN[1] + 40, 300, 420, t, 0.0))
    t_a = -1.3
    o.append(calendar30(HCAL[0], HCAL[1], tt, t0=t_a, t1=HIT, w=400, h=380, pulse=bump(tt, HIT, .04, .3)))
    o.append(PR.desk(DESK[0], DESK[1], w=860, depth=100, leg_h=260, seed=7))
    o.append(folder(HFOLD[0], HFOLD[1], 1.0, tt, dust=1.0, web=1.0, tremble=.6 + 1.4 * bump(tt, HIT, .04, .3)))
    sx = HFOLD[0] + 170
    sp_drop = 120 + 60 * math.sin(tt * 3.1) + 50 * bump(tt, HIT, .05, .3)
    o.append(line([(sx, HFOLD[1] - 210), (sx, -400)], 1.8, WEB_C, taper=0, wmin=1, seed=31100))
    o.append(PR.spider(sx, HFOLD[1] - 210, 1.1, drop=sp_drop, t=tt, seed=1, look=.3 * math.sin(tt * 4)))
    o.append(cat(CAT_AT[0] - 10, CAT_AT[1] - 18 * bump(tt, HIT, .05, .2), .44, tt,
                 dict(look=(-.9, -.6), perk=bump(tt, HIT, .04, .5), tail=24 * math.sin(tt * 7), ear=.6 * math.sin(tt * 9))))
    o.append(dust_motes(250, 560, 1100, 1000, tt, n=26, seed=1, gust=bump(tt, HIT, .05, .4)))
    o.append(PR.sparkles(HCAL[0], HCAL[1] + 100, 1.3, bump(tt, HIT, .04, .4), tt, seed=3, n=5, r=170, col="#d5302a"))
    return "".join(o)


def hook_cam_scene(t):
    u = ease_io(clamp((t + .2) / 1.7))
    return 730 - 25 * u, 740 + 10 * u + 6 * math.sin(t * 6), 1.3 + .07 * u


def hook_wrap(body, t, hit, bg=BG):
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    piv = 960.0
    tr = f"translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-piv})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<use href="#hk104" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk104">{body}</g></g>{blur}'


def frame_s01(t):
    cx, cy, s = hook_cam_scene(t)
    body = hook_world(t, t)
    dx, dy = shake(t, HIT, 14)
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{body}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT) + over(t))


def frame_s26(t):
    """Петля: тот же мир, что на кадре 0 (дни снова зачёркиваются к тридцатому), камера едет к виду хука."""
    a, b = T0("s26"), T1("s26")
    tt = t - END
    body = hook_world(t, tt)
    import anim
    cx, cy, s = hook_cam_scene(tt)
    u = ease_io(ramp(t, a, b - a))
    h0 = anim.hook_cam(0.0, hit=HIT)
    z = 1.12 + (h0["zoom"] - 1.12) * u
    r = 2 * (1 - u) + h0["rot"] * u
    v = f'<g transform="{lib.cam(cx, cy, s, 0)}">{body}</g>'
    piv = 960.0
    tr = f"translate({540 + h0['dx'] * u:.2f} {piv + h0['dy'] * u:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-piv})"
    return lib.svg(f'<rect width="1080" height="1920" fill="{BG}"/><g transform="{tr}">{v}</g>' + over(t))


# ═════════════════════════ s02: папка крупно, паук спускается ═════════════════════════
def falling_specks(x0, x1, y0, y1, t, n=18, seed=0, op=.8):
    rs = PR._rs(32000 + seed)
    o = []
    for j in range(n):
        ph = (rs.uniform(0, 1) + t * rs.uniform(.35, .7)) % 1.0
        px = rs.uniform(x0, x1) + 14 * math.sin(t * 3 + j)
        py = y0 + (y1 - y0) * ph
        r = rs.uniform(2.5, 6)
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="#8c857a" opacity="{op * math.sin(math.pi * ph):.3f}"/>')
    return "".join(o)


def frame_s02(t):
    """«Отчёт, который я»: папка крупно, наклейка ОТЧЁТ; на «Отчёт» паук резко спускается на нитке перед наклейкой,
    паутина дрожит, сверху сыплется пыль."""
    a, b = T0("s02"), T1("s02")
    t_sp = W(3)
    o = [room(t)]
    o.append(calendar30(HCAL[0], HCAL[1], t, 30, w=400, h=380))
    o.append(PR.desk(DESK[0], DESK[1], w=860, depth=100, leg_h=260, seed=7))
    o.append(folder(HFOLD[0], HFOLD[1], 1.0, t, dust=1.0, web=1.0, tremble=.5 + 1.5 * bump(t, t_sp, .05, .4)))
    sx = HFOLD[0] - 60
    drop = 20 + 105 * ease_out(ramp(t, t_sp, .3)) + 25 * math.sin(t * 5) * ramp(t, t_sp + .3, .2)
    o.append(line([(sx, HFOLD[1] - 420), (sx, -400)], 1.8, WEB_C, taper=0, wmin=1, seed=31101))
    o.append(PR.spider(sx, HFOLD[1] - 420, 1.5, drop=drop, t=t, seed=2, look=.5))
    o.append(falling_specks(HFOLD[0] - 260, HFOLD[0] + 260, HFOLD[1] - 420, HFOLD[1] - 40, t, n=22, seed=2))
    o.append(dust_motes(HFOLD[0] - 300, HFOLD[1] - 500, HFOLD[0] + 300, HFOLD[1], t, n=14, seed=4))
    o.append(cat(CAT_AT[0] - 10, CAT_AT[1], .44, t, dict(look=(-.9, .2), squint=.5, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_sp + .2, 7)
    return view("".join(o), HFOLD[0] + 20 + dx, HFOLD[1] - 120 + dy, 1.85 + .2 * u, -1.5 + 2 * u, t=t)


# ═════════════════════════ s03: 30 дней зачёркнуты ═════════════════════════
def frame_s03(t):
    """«откладывал тридцать дней»: календарь крупно, все 30 дней в красных крестах; на «тридцать» кресты вздрагивают волной,
    красный маркер обводит весь месяц."""
    a, b = T0("s03"), T1("s03")
    t30 = W(7)
    o = [room(t)]
    pulse = bump(t, t30, .05, .35)
    o.append(calendar30(HCAL[0], HCAL[1], t, 30, w=400, h=380, pulse=pulse))
    circ = ease_out(ramp(t, t30 - .05, .45))
    if circ > .01:
        n = 48
        pts = [(HCAL[0] + 250 * math.cos(-2.2 + 2 * math.pi * 1.06 * j / n * circ), HCAL[1] + 20 + 235 * math.sin(-2.2 + 2 * math.pi * 1.06 * j / n * circ))
               for j in range(n + 1)]
        o.append(line(pts, 14, "#d5302a", taper=.3, wmin=.5, seed=3301))
    o.append(PR.sparkles(HCAL[0], HCAL[1], 2.2, bump(t, t30 + .3, .05, .4), t, seed=33, n=6, r=300, col="#d5302a"))
    o.append(PR.desk(DESK[0], DESK[1], w=860, depth=100, leg_h=260, seed=7))
    o.append(folder(HFOLD[0], HFOLD[1], 1.0, t, dust=1.0, web=1.0, tremble=.5))
    o.append(dust_motes(HCAL[0] - 260, HCAL[1] - 200, HCAL[0] + 260, HCAL[1] + 240, t, n=16, seed=5))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t30, 10)
    return view("".join(o), HCAL[0] + dx, HCAL[1] + 40 + dy, 1.75 + .25 * u + .08 * pulse, 1.5 - 3 * u, t=t)


# ═════════════════════════ s04: штамп «СДАН» ═════════════════════════
HS = stress(9, .25)       # «сДАн»: штамп бьёт по папке


def frame_s04(t):
    """«сдан без неё»: красный штамп падает сверху на папку, на «сдан» удар — пыль разлетается, паутина рвётся, кот
    подпрыгивает; штамп отскакивает вверх — на папке красный оттиск СДАН."""
    a, b = T0("s04"), T1("s04")
    fx, fy = HFOLD[0] + STAMP_DX, HFOLD[1] - 80          # место оттиска (мир)
    fall = ease_in(ramp(t, a - .1, HS - a + .1))
    lift = ease_in(ramp(t, HS + .28, .25))
    sq = bump(t, HS, .03, .12)
    if t < HS:
        sy = fy - 1100 * (1 - fall)
    else:
        sy = fy - 18 * sq - 1100 * lift
    hit_u = ramp(t, HS, .7)
    dust = 1 - .75 * ease_out(ramp(t, HS, .35))
    o = [room(t)]
    o.append(calendar30(HCAL[0], HCAL[1], t, 30, w=400, h=380))
    o.append(PR.desk(DESK[0], DESK[1], w=860, depth=100, leg_h=260, seed=7))
    o.append(folder(HFOLD[0], HFOLD[1], 1.0, t, dust=dust, web=1.0 - .4 * ramp(t, HS, .3), tremble=2 * bump(t, HS, .03, .3),
                    stamp=ramp(t, HS + .02, .05) if t > HS else 0.0, torn=ease_out(ramp(t, HS, .2))))
    if t < HS:      # тень штампа растёт на папке
        o.append(blob(ellipse_pts(fx, fy + 30, 140 * (.4 + .6 * fall), 22 * (.4 + .6 * fall), 18), "#3a2a20", .28 * fall))
    o.append(stamp(fx, sy + 50, .85, -9 + 6 * (1 - fall), sq))
    if t < HS:
        o.append(PR.speed_arcs(fx, sy - 260, 1.2, fall, t, seed=41, n=3, ang=270))
    o.append(dust_burst(fx, fy + 40, 1.3, hit_u, seed=4))
    o.append(PR.sparkles(fx, fy, 2.4, bump(t, HS + .05, .05, .45), t, seed=44, n=7, r=320, col="#d5302a"))
    jump = bump(t, HS, .1, .3)
    o.append(cat(CAT_AT[0] - 10, CAT_AT[1] - 140 * jump, .44, t, dict(look=(-.9, -.4), perk=1.0, legs=jump, flat_ears=0.0,
                                                                       smile=ramp(t, HS + .4, .2), tail=30 * math.sin(t * 9))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, HS, 18)
    return view("".join(o), HFOLD[0] + 70 + dx, HFOLD[1] - 260 + dy, 1.45 + .12 * u + .1 * bump(t, HS, .03, .3), 0, t=t)


# ═════════════════════════ s05–s06: ждал настроения с утра до вечера ═════════════════════════
WEB_FOLD = dict(dust=1.0, web=1.0)


def frame_s05(t):
    """«Раньше ждал настроения»: Дима за столом подпёр щёку кулаком и смотрит на папку в паутине; утро, солнце в окне;
    на «настроения» вздыхает (плечи вниз), кот зевает."""
    a, b = T0("s05"), T1("s05")
    sigh = bump(t, W(14), .2, .5)
    f = dima_sit(DX, DHIP, DK, "glum", t, pose="sit_desk", lean=.1 + .05 * sigh, head_add=.06 * sigh + .03 * math.sin(t * 2))
    body, _ = desk_world(t, dima=f, clock=(9, 0 + 20 * (t - a)), phase=.05 * ramp(t, a, b - a), fold=dict(WEB_FOLD, tremble=.4),
                         lap_open=0.0, cat_st=dict(look=(-.6, .2), blink=.6 * bump(t, W(14) + .2, .2, .4), tail=8 * math.sin(t * 2)))
    o = [body, dust_motes(500, 700, 1100, 980, t, n=12, seed=6)]
    hx, hy = f["head"]
    o.append(PR.thought_cloud(hx + 150, hy - 230, .8 * pop(t, W(13), .3), 230, 150, 1.0, seed=5, inner="") if t > W(13) else "")
    if t > W(13):
        o.append(txt("?", hx + 150, hy - 205, 90, "#9aa0aa", "#9aa0aa", 0, op=ramp(t, W(13) + .1, .2)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(14), 5)
    return view("".join(o), 600 + dx, 760 + dy, 1.6 + .12 * u, 1 - 2 * u, t=t)


def frame_s06(t):
    """«с утра до вечера»: окно и Дима ближе; солнце летит по небу и садится, небо и стена рыжеют, часы крутятся;
    на «вечера» солнце уходит за холм, Дима сползает ниже."""
    a, b = T0("s06"), T1("s06")
    ph = ease_io(ramp(t, a - .1, W(18) + .2 - a))
    hh = 9 + 10 * ph
    f = dima_sit(DX, DHIP, DK, "sag73", t, pose="sit_desk", lean=.12 + .1 * ph, head_add=.08 + .1 * ph)
    body, _ = desk_world(t, dima=f, clock=(hh, (hh % 1) * 60, 3 * math.sin(t * 20) * (1 - ph)), phase=ph, fold=dict(WEB_FOLD), lap_open=0.0,
                         cat_st=dict(look=(-.8, -.4), sleep=.6 * ph, tail=6 * math.sin(t * 2)))
    o = [body]
    o.append(PR.speed_arcs(WIN[0] + 60, WIN[1] - 330, .9, 1 - ph, t, seed=61, n=3, ang=-20))
    o.append(PR.speed_arcs(CLOCK[0] + 100, CLOCK[1], .8, 1 - ph, t, seed=62, n=3, ang=0))
    if ph > .02:
        o.append(f'<rect x="-1400" y="-1400" width="4000" height="4000" fill="#ff8a3c" opacity="{.12 * ph:.3f}"/>')
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(18) + .15, 6)
    return view("".join(o), 420 + 60 * u + dx, 720 + dy, 1.5 + .15 * u, 0, t=t)


# ═════════════════════════ s07–s09: кружка, стол, видео «для фона» ═════════════════════════
KITCH = "#d9eef2"


def frame_s07(t):
    """«Мыл кружку»: раковина крупно, кружка под струёй в пене, рука трёт её губкой кругами, пузыри летят."""
    a, b = T0("s07"), T1("s07")
    o = [rect(-900, -1400, 2200, 2600, KITCH)]
    for r in range(18):
        for c in range(14):
            o.append(f'<rect x="{-400 + c * 150:.0f}" y="{-200 + r * 150:.0f}" width="146" height="146" fill="#cbe6ec"/>')
    o.append(shape(lib.rect_pts(-400, 1180, 1600, 1500), "#b9c2cc", "", w=5, seed=7001))         # столешница
    o.append(shape([(140, 1180, 1), (940, 1180, 1), (900, 1460, 1), (180, 1460, 1)], "#8e99a6", blob(lib.rect_pts(180, 1400, 900, 1460), "#7a8592"),
                   w=5, seed=7002))                                                               # мойка
    o.append(line([(780, 1180), (780, 760), (600, 700), (560, 760)], 34, "#9aa3ad", taper=0, wmin=1, seed=7003))
    o.append(line([(780, 1180), (780, 760), (600, 700), (560, 760)], 3, INK, taper=0, wmin=1, seed=7004, op=.6))
    o.append(PR.pour_stream(560, 770, 552, 1100, t, w=26, col="#8fd0f4", seed=1))
    spin = 18 * math.sin(t * 9)
    o.append(PR.coffee_mug(550, 1240, 1.9, spin, col="red", fill=0.0))
    for j in range(16):                                   # пена
        ph = (t * .8 + j * .13) % 1.0
        r = 16 + 10 * ((j * 7) % 3)
        bx = 420 + 260 * ((j * .37) % 1.0) + 30 * math.sin(t * 3 + j)
        by = 1160 - 300 * ph
        o.append(shape(ellipse_pts(bx, by, r * (1 - .4 * ph), r * (1 - .4 * ph), 12), "#ffffff", blob(ellipse_pts(bx - r * .3, by - r * .3, r * .25, r * .25, 8), "#dff6ff"),
                       w=2.2, seed=7100 + j))
    ang = t * 13
    wx, wy = 640 + 90 * math.cos(ang), 1080 + 50 * math.sin(ang)
    o.append(shape(lib.rrect(wx - 80, wy - 50, wx + 80, wy + 50, 22), "#ffd23f", blob(lib.rect_pts(wx - 80, wy + 10, wx + 80, wy + 50), "#5bb36a"), w=4, seed=7200))
    o.append(line([(wx + 60, wy + 30), (wx + 560, wy + 560)], 150, INK, taper=0, wmin=1, seed=7201))
    o.append(line([(wx + 60, wy + 30), (wx + 560, wy + 560)], 136, "#4F78B5", taper=0, wmin=1, seed=7202))
    o.append(people.hand_svg("dima", (wx + 80, wy + 40), (-.7, -.7), 1.6, curl=(.7, .7, .7, .7), thumb=.6, seed=7203))
    o.append(PR.sparkles(550, 1050, 1.3, bump(t, W(20), .05, .4), t, seed=71, n=5, r=200, col="#4FB0E6"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(19), 6)
    return view("".join(o), 600 + dx, 1020 + dy, 1.5 + .1 * u, -2 + 3 * u, bg=KITCH, t=t)


def frame_s08(t):
    """«протирал стол»: Дима стоит у стола и трёт его тряпкой большими кругами вокруг папки, папку не трогает; блеск."""
    a, b = T0("s08"), T1("s08")
    k = .5
    hip = stand_hip(k)
    ang = (t - a) * 12
    tx, ty = 520 + 120 * math.cos(ang), DESK[1] - 50 + 26 * math.sin(ang)
    f = people.dima82(330, hip, k, "dull", "d82_rest", t=t, feet="stand", lean_add=.25,
                      arms={"n": ("ik", (tx, ty - 10), -1)}, hands={"n": {"dir": (1, .3), "curl": (.3, .3, .3, .3), "thumb": .3}})
    body, _ = desk_world(t, dima=f, clock=(13, 20 * (t - a)), fold=dict(WEB_FOLD), laptop=False, cat_st=dict(look=(-.8, .1), tail=10 * math.sin(t * 3)))
    o = [body]
    o.append(shape(ellipse_pts(tx, ty, 70, 22, 14), "#6fb7e8", blob(ellipse_pts(tx - 10, ty - 6, 40, 10, 10), "#9fd3f2"), w=3.4, seed=8001))
    for j in range(4):
        q = ang - .5 * (j + 1)
        o.append(PR.star4(520 + 120 * math.cos(q), DESK[1] - 50 + 26 * math.sin(q) - 10, 12, 1 - .22 * j))
    o.append(PR.sparkles(560, DESK[1] - 60, 1.2, bump(t, W(22), .05, .4), t, seed=81, n=5, r=180))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(21), 5)
    return view("".join(o), 560 + dx, 780 + dy, 1.75 + .12 * u, 1 - 2 * u, t=t)


def screen_rect(x, y, k, open_=1.0):
    p = PR.laptop_pts(x, y, k, open_)
    cx, cy = p["screen"]
    w, h = p["sw"] * .92, p["sh"] * .84
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2


def video_screen(x0, y0, x1, y1, t, play=0.0):
    """Видео на экране: яркий мультик (небо, холмы, прыгающий мячик), кнопка ▶ пропадает на play, полоса прогресса."""
    w, h = x1 - x0, y1 - y0
    c = lib.clip_rect(x0, y0, w, h)
    o = [rect(x0, y0, x1, y1, "#6ec3f0")]
    o.append(blob([(x0, y1 - h * .3), (x0 + w * .4, y1 - h * .5), (x1, y1 - h * .32), (x1, y1), (x0, y1)], "#7cc46a"))
    bx = x0 + w * (.2 + .6 * ((t * .7) % 1.0))
    by = y1 - h * .32 - h * .3 * abs(math.sin(t * 6))
    o.append(shape(ellipse_pts(bx, by, h * .09, h * .09, 14), "#ff8a3c", "", w=2.6, seed=9001))
    o.append(shape(ellipse_pts(x0 + w * .8, y0 + h * .2, h * .1, h * .1, 14), "#FFD23F", "", w=2.4, seed=9002))
    if play < 1:
        s_ = 1 - play
        o.append(f'<g opacity="{s_:.3f}" transform="translate({x0 + w / 2:.1f} {y0 + h / 2:.1f}) scale({1 + .4 * play:.3f})">'
                 f'<circle r="{h * .2:.1f}" fill="#111" opacity=".55"/><path d="M{-h * .07:.1f} {-h * .1:.1f} L{h * .1:.1f} 0 L{-h * .07:.1f} {h * .1:.1f}Z" fill="#fff"/></g>')
    o.append(rect(x0, y1 - 10, x1, y1, "#555"))
    o.append(rect(x0, y1 - 10, x0 + w * (.1 + .3 * play + .05 * t % .3), y1, "#e9576a"))
    return f'<g clip-path="url(#{c})">{"".join(o)}</g>'


def frame_s09(t):
    """«включал видео „для фона“»: Дима откинулся на стуле с кружкой, на ноутбуке на «видео» жмётся ▶ и идёт мультик;
    на «фона» он отодвигает папку локтем за ноутбук."""
    a, b = T0("s09"), T1("s09")
    play = ease_out(ramp(t, W(24), .25))
    push = ease_io(ramp(t, W(26) - .1, .35))
    f = dima_sit(DX, DHIP, DK, "lean_rest" if play > .5 else "dull", t, pose="lean_back", lean=-.05)
    fold = dict(WEB_FOLD, tremble=push)
    body, _ = desk_world(t, dima=f, clock=(15, 20 * (t - a)), fold=None, lap_screen="dark", cat_st=dict(look=(-.9, .0), tail=10 * math.sin(t * 3)))
    o = [body]
    o.append(folder(FOLD[0] + 70 * push, FOLD[1] + 40 - 20 * push, .55 - .08 * push, t, **fold))
    x0, y0, x1, y1 = screen_rect(LAP[0], LAP[1], .5)
    o.append(video_screen(x0, y0, x1, y1, t, play))
    o.append(PR.glow(LAP[0], LAP[1] - 120, 300, .4 * play, "#bfe6ff"))
    o.append(PR.tap_rings((x0 + x1) / 2, (y0 + y1) / 2, ramp(t, W(24), .3), .6, col="#FFD23F"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(24), 6)
    return view("".join(o), 470 + 40 * u + dx, 820 + dy, 1.6 + .15 * u, 0, t=t)


# ═════════════════════════ s10–s11: последняя ночь, паника ═════════════════════════
def frame_s10(t):
    """«А в последнюю ночь»: ночь, луна в окне, комната тёмно-синяя, свет ноутбука; часы крутятся и на «ночь» встают
    на 3:00 с отскоком; на столе гора кружек."""
    a, b = T0("s10"), T1("s10")
    tn = W(30)
    if t < tn:
        m = (t * 2.6 * 60) % 720
        clk = (m / 60, m % 60, 4 * math.sin(t * 20))
    else:
        u = t - tn
        clk = (3, 9 * math.exp(-u * 7) * math.cos(u * 30), 5 * math.exp(-u * 5) * math.sin(u * 25))
    f = dima_sit(DX, DHIP, DK, "zombie", t, pose="sit_desk", lean=.18 + .03 * math.sin(t * 11))
    mugs = "".join(PR.coffee_mug(LAP[0] + 230 + 60 * j, LAP[1] + 20 - 4 * j, .42, -6 + 5 * j, col=("white", "red", "blue")[j % 3], fill=.3,
                                 steam=1.0 if j == 2 else 0.0, t=t, seed=j) for j in range(3))
    body, _ = desk_world(t, dima=f, clock=clk, night=1.0, lap_screen="lines", lap_lines=.2, fold=None, extra_desk=mugs,
                         cat_st=dict(look=(-.8, -.4), blink=.4, tail=6 * math.sin(t * 2)), cat_x=CAT_AT[0] + 20)
    o = [body]
    o.append(PR.sparkles(CLOCK[0], CLOCK[1], 1.2, bump(t, tn, .05, .4), t, seed=101, n=5, r=140))
    if t < tn:
        o.append(PR.speed_arcs(CLOCK[0] + 100, CLOCK[1], .8, 1.0, t, seed=102, n=3, ang=0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tn, 12)
    return view("".join(o), 640 + dx, 640 + dy + 80 * u, 1.35 + .15 * u, 0, bg=NIGHT, t=t)


def frame_s11(t):
    """«делал всё в панике»: Дима крупно в панике строчит, пот летит, кружки дрожат; на «панике» клавиатура дымится."""
    a, b = T0("s11"), T1("s11")
    tp = W(34)
    f = dima_sit(DX, DHIP, DK, "panic82", t, pose="sit_desk", lean=.2 + .05 * math.sin(t * 30))
    mugs = "".join(PR.coffee_mug(LAP[0] + 230 + 60 * j, LAP[1] + 20 - 4 * j + 3 * math.sin(t * 40 + j), .42, -6 + 5 * j,
                                 col=("white", "red", "blue")[j % 3], fill=.3, t=t, seed=j) for j in range(3))
    body, _ = desk_world(t, dima=f, clock=(3, 10 + 30 * (t - a)), night=1.0, lap_screen="lines", lap_lines=.2 + .6 * ramp(t, a, b - a),
                         fold=None, extra_desk=mugs, cat_st=dict(look=(-.9, -.5), perk=1.0, tail=20 * math.sin(t * 8)), cat_x=CAT_AT[0] + 20)
    o = [body]
    hx, hy = f["head"]
    for j in range(3):
        ph = (t * 2.2 + j * .33) % 1.0
        o.append(PR.sweat(hx - 70 - 90 * ph, hy - 40 + 60 * ph, .9, -30))
    o.append(people.strain_marks((hx, hy), .5, t, 1.0))
    smoke = ramp(t, tp - .1, .3)
    o.append(PR.smoke_curls(LAP[0] - 40, LAP[1] - 30, 1.2, smoke, t, seed=1, n=3, col="#9aa0aa"))
    o.append(PR.smoke_curls(LAP[0] + 60, LAP[1] - 30, 1.0, smoke, t, seed=2, n=2, col="#9aa0aa"))
    o.append(PR.glow(LAP[0], LAP[1] - 30, 160, .5 * smoke * (.7 + .3 * math.sin(t * 30)), "#ff6a3c"))
    o.append(PR.speed_arcs(LAP[0] - 200, LAP[1] - 60, .7, 1.0, t, seed=111, n=3, ang=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tp, 12)
    return view("".join(o), 480 + 40 * u + dx, 800 + dy, 1.75 + .15 * u, 2 * math.sin(t * 25) * .3, bg=NIGHT, t=t)


# ═════════════════════════ s12–s15: призыв «КОТ», гора разбивается на шаги ═════════════════════════
PAPER = "#f6efdf"


def paper_bg():
    return rect(-2000, -2000, 3500, 4000, PAPER) + "".join(
        line([(-1200, 200 + 90 * j), (2600, 200 + 90 * j)], 2, "#e3d6bb", taper=0, wmin=1, seed=6000 + j) for j in range(24))


def kot_print(t, t0, x, y, size):
    """Кодовое слово печатными: жирный IDB, жёлтый с чёрной обводкой и тенью (как «КОТ» в рилсе 102); буквы выскакивают
    по одной с t0 (по 0.09 с), y — базовая линия, x — центр слова."""
    if t < t0:
        return ""
    o = []
    w = size * .74
    for j, ch in enumerate("КОТ"):
        u = clamp((t - t0 - .09 * j) / .2)
        if u <= 0:
            continue
        s_ = lib.back_out(u, 2.6) if u < 1 else 1.0
        cx = x + (j - 1) * w
        letter = (f'<text x="0" y="10" font-family="IDB" font-size="{size:.1f}" text-anchor="middle" fill="#000" opacity=".35" '
                  f'stroke="#000" stroke-width="{size * .12:.1f}" stroke-linejoin="round">{ch}</text>'
                  + txt(ch, 0, 0, size, fill="#FFD23F", stroke="#111", sw=size * .11))
        o.append(f'<g transform="translate({cx:.1f} {y:.1f}) rotate({-3 + 2 * j}) scale({s_:.4f})">{letter}</g>')
    return "".join(o)


def kot_top(t, a):
    """КОТ в экранных координатах (вне камеры): в начале s13 уезжает вверх и уменьшается, дальше стоит в безопасной зоне."""
    if NOCAM:
        return ""
    mv = ease_io(ramp(t, T0("s13"), .35))
    return kot_print(t, -9.0, 540, 860 - 430 * mv, 300 - 90 * mv)


def frame_s12(t):
    """«Напиши «КОТ»»: на бумаге крупно выскакивает печатное жёлтое КОТ, кот рядом показывает на слово лапой."""
    a, b = T0("s12"), T1("s12")
    o = [paper_bg()]
    o.append(PR.glow(540, 820, 420, .5 * ramp(t, W(36), .3), "#ffe9a8"))
    o.append(kot_print(t, W(36) - .05, 540, 860, 300))
    o.append(PR.sparkles(540, 800, 2.4, bump(t, W(36) + .3, .05, .5), t, seed=121, n=6, r=380))
    o.append(cat(800, 1420, .95, t, dict(look=(-.6, -.6), paw=ease_out(ramp(t, W(36) - .2, .3)), smile=1.0, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(36), 8)
    return view("".join(o), 540 + dx, 960 + dy, 1.0 + .08 * u, 0, bg=PAPER, t=t)


MT = (540.0, 1300.0)
N_STEPS = 5


def mountain_case(t, grow=1.0, thud=0.0, crack=0.0):
    """Гора-дело: тёмная тяжёлая гора, на вершине папка ОТЧЁТ; crack — трещины по ней."""
    o = [f'<g transform="translate({MT[0]:.1f} {MT[1]:.1f}) scale({1 + .06 * thud:.4f} {1 - .06 * thud:.4f}) translate({-MT[0]:.1f} {-MT[1]:.1f})">']
    o.append(PR.mountain(MT[0], MT[1], .6, grow, 1.0, seed=3))
    top = MT[1] - (120 + 1030 * grow) * .6
    o.append(folder(MT[0], top + 55, .55, t, dust=.6, web=0.0))
    if crack > .01:
        for j in range(4):
            x = MT[0] - 200 + 130 * j
            pts = [(x, MT[1] - 30), (x + 25, MT[1] - 150), (x - 8, MT[1] - 260), (x + 30, MT[1] - 360)]
            n = max(2, int(len(pts) * crack + .99))
            o.append(line(pts[:n], 9, "#fff1b0", taper=.3, wmin=.4, seed=13000 + j))
    o.append("</g>")
    return "".join(o)


def step_pos(i):
    """Ступенька i (0…N_STEPS−1): левый нижний угол, ширина, высота."""
    w, h = 170.0, 140.0
    return 120 + i * w, MT[1] - (i + 1) * h, w, h


def steps(t, t0, dt=.22, lit=0.0, seed=0):
    o = []
    for i in range(N_STEPS):
        ta = t0 + dt * i
        u = clamp((t - ta) / .25)
        if u <= 0:
            continue
        x, y, w, h = step_pos(i)
        s_ = lib.back_out(u, 2.4) if u < 1 else 1.0
        col = lib.mix("#c9a77c", "#9be07a", lit if i == 0 else 0.0)
        body = shape(lib.rect_pts(0, 0, w, MT[1] - y), col, blob(lib.rect_pts(0, 0, w, 18), lib.mul(col, (1.08, 1.08, 1.08))), w=4.4, seed=13100 + i)
        body += shape(lib.rrect(w * .14, 34, w * .86, 92, 14), "#fffdf6", "", w=3, seed=13120 + i)
        body += txt("2 МИН", w / 2, 76, 36, "#1d2448", "#fffdf6", 0)
        o.append(f'<g transform="translate({x + w / 2:.1f} {MT[1]:.1f}) scale({s_:.4f}) translate({-w / 2:.1f} {y - MT[1]:.1f})">{body}</g>')
    return "".join(o)


def frame_s13(t):
    """«чтобы твоё самое тяжёлое дело»: КОТ уезжает вверх; из земли растёт тёмная гора-дело с папкой на вершине,
    на «тяжёлое» она бухает о землю (сплющивается, пыль)."""
    a, b = T0("s13"), T1("s13")
    mv = ease_io(ramp(t, a, .35))
    th = stress(40, .3)
    o = [paper_bg()]
    o.append(rect(-1000, MT[1], 2200, 3000, "#e3d6bb"))
    o.append(line([(-1000, MT[1]), (2200, MT[1])], 6, seed=13200))
    grow = ease_out(ramp(t, a, th - a))
    o.append(mountain_case(t, grow, bump(t, th, .04, .2)))
    o.append(dust_burst(MT[0] - 300, MT[1] - 10, 1.2, ramp(t, th, .6), seed=5) + dust_burst(MT[0] + 300, MT[1] - 10, 1.2, ramp(t, th, .6), seed=6))
    o.append(cat(950, MT[1], .9, t, dict(look=(-.8, -.7), flat_ears=bump(t, th, .05, .5), tail=10 * math.sin(t * 3))))
    del mv
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, th, 16)
    return view("".join(o), 540 + dx, 960 + dy, 1.0 + .05 * u, 0, bg=PAPER, t=t, extra=kot_top(t, a))


def frame_s14(t):
    """«разбилось на шаги по две минуты»: на «разбилось» гора трескается светом и рассыпается, на её месте ступеньки
    выскакивают одна за другой, на каждой бирка «2 МИН»; папка ложится на верхнюю."""
    a, b = T0("s14"), T1("s14")
    tb = W(42)
    o = [paper_bg()]
    o.append(rect(-1000, MT[1], 2200, 3000, "#e3d6bb"))
    o.append(line([(-1000, MT[1]), (2200, MT[1])], 6, seed=13200))
    crack = ease_out(ramp(t, a, tb + .1 - a))
    gone = ramp(t, tb + .15, .2)
    if gone < 1:
        o.append(f'<g opacity="{1 - gone:.3f}">' + mountain_case(t, 1.0, 0.0, crack) + "</g>")
    o.append(dust_burst(MT[0], MT[1] - 400, 2.2, ramp(t, tb + .1, .7), seed=7))
    o.append(steps(t, tb + .15, dt=(W(47) - tb - .15) / (N_STEPS - 1)))
    x, y, w, h = step_pos(N_STEPS - 1)
    if t > W(47):
        o.append(folder(x + w / 2, y - 4, .3 * pop(t, W(47), .3), t, dust=0.0, web=0.0))
    o.append(PR.sparkles(MT[0], MT[1] - 400, 2.6, bump(t, tb + .1, .05, .5), t, seed=141, n=7, r=420))
    o.append(cat(980, MT[1], .9, t, dict(look=(-.8, -.5), perk=1.0, tail=14 * math.sin(t * 4))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb + .1, 12)
    return view("".join(o), 560 + dx, 960 + dy, 1.0 + .05 * u, 0, bg=PAPER, t=t, extra=kot_top(t, a))


def frame_s15(t):
    """«и первый ты сделал, пока кот сидит рядом»: Дима встаёт на первую ступеньку, она загорается зелёным с галочкой;
    на «кот» кот запрыгивает на ступеньку рядом и садится на «рядом»."""
    a, b = T0("s15"), T1("s15")
    t1 = W(51)
    o = [paper_bg()]
    o.append(rect(-1000, MT[1], 2200, 3000, "#e3d6bb"))
    o.append(line([(-1000, MT[1]), (2200, MT[1])], 6, seed=13200))
    lit = ease_out(ramp(t, t1, .25))
    o.append(steps(t, -9.0, lit=lit))
    x, y, w, h = step_pos(N_STEPS - 1)
    o.append(folder(x + w / 2, y - 4, .3, t, dust=0.0, web=0.0))
    x0, y0, w0, h0 = step_pos(0)
    k = .42
    up = ease_io(ramp(t, W(49), t1 - W(49)))
    dxp = -90 + 150 * up
    hip = stand_hip(k, fl=MT[1] - h0 * up) if True else 0
    f = people.dima82(x0 + w0 / 2 + dxp - 40, hip, k, "focus_smile" if up > .5 else "steady", "d82_rest", t=t, feet="stand")
    o.append(f["svg"])
    o.append(PR.check_mark(x0 + w0 / 2 + 20, y0 - 260, 1.6 * pop(t, t1, .3) if t > t1 else 0.0, lit, col="#2f9a4a"))
    o.append(PR.sparkles(x0 + w0 / 2, y0 - 200, 1.4, bump(t, t1 + .05, .05, .5), t, seed=151, n=5, r=160))
    jt = W(53)
    j = ease_io(ramp(t, jt - .1, .4))
    x1_, y1_ = x0 + w0 + 40, MT[1]
    cxp = 1000 + (x1_ + 60 - 1000) * j
    cyp = y1_ - 320 * math.sin(math.pi * j)
    sit = ease_out(ramp(t, W(55), .3))
    o.append(cat(cxp, cyp, .62, t, dict(look=(-.8, -.4), legs=j * (1 - j) * 4 if j < 1 else 0.0, smile=sit, blink=.5 * sit, tail=10 * math.sin(t * 3))))
    if sit > .01:
        o.append(PR.heart(cxp - 20, cyp - 330 - 30 * sit, .7 * pop(t, W(55), .3), bump(t, W(55) + .1, .05, .3)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t1, 8)
    return view("".join(o), 500 + 20 * u + dx, 1040 + dy, 1.2 + .08 * u, 0, bg=PAPER, t=t, extra=kot_top(t, a))


# ═════════════════════════ s16–s22: вот что я поменял ═════════════════════════
DAY_FOLD = dict(dust=1.0, web=1.0)


def timer_box(x, y, k, t, secs=120.0, press=0.0, ring=0.0, done=0.0):
    """Кухонный таймер-куб с табло мм:сс; ring — звенит (трясётся, дуги), done — табло зеленеет."""
    m, s_ = int(max(0, secs) // 60), int(max(0, secs) % 60)
    o = [shape(lib.rrect(-150, -120, 150, 110, 30), lib.mix("#E9576A", "#5bb36a", done), blob(lib.rect_pts(-150, 60, 150, 110), "#00000022"), w=5, seed=16001)]
    o.append(shape(lib.rrect(-115, -85, 115, 30, 14), "#1d2030", "", w=3.4, seed=16002))
    o.append(txt(f"{m}:{s_:02d}", 0, 6, 92, lib.mix("#7CFF9A", "#ffffff", 0), "#1d2030", 0))
    o.append(shape(lib.rrect(-40, -150 + 16 * press, 40, -116, 8), "#f4efe4", "", w=3.4, seed=16003))
    wob = 7 * ring * math.sin(t * 50)
    g = tf("".join(o), x, y, k, wob)
    if ring > .05:
        g += PR.speed_arcs(x + 200 * k, y - 40 * k, .9 * k, ring, t, seed=161, n=3, ang=0)
        g += PR.speed_arcs(x - 200 * k, y - 40 * k, .9 * k, ring, t, seed=162, n=3, ang=180)
    return g


TIMER_AT = (LAP[0] + 260, LAP[1] + 4)
T_START = W(67) + .05                     # «тАймер»: старт отсчёта
T_RATE = 120.0 / (W(73) + .2 - T_START)   # ускоренный отсчёт: 2:00 кончается на «Желание»


def timer_secs(t):
    if t < T_START:
        return 120.0
    return max(0.0, 120.0 - T_RATE * (t - T_START))


def frame_s16(t):
    """«Вот что я поменял»: день, Дима встаёт у стола, на «Вот» щёлкает пальцами — над головой загорается лампочка;
    кот поворачивает голову. Надпись ВОТ ЧТО Я ПОМЕНЯЛ."""
    a, b = T0("s16"), T1("s16")
    ti = W(56) + .05
    k = .5
    f = people.dima82(330, stand_hip(k), k, "wow82" if t > ti else "puzzled82", "d82_one", t=t, feet="stand", flip=False,
                      head_add=.08 * bump(t, ti, .08, .3))
    body, _ = desk_world(t, dima=f, clock=(11, 20 * (t - a)), fold=dict(DAY_FOLD), lap_open=0.0, cat_st=dict(look=(-.9, -.5), perk=ramp(t, ti, .2)))
    o = [body]
    hx, hy = f["head"]
    if t > ti:
        o.append(PR.glow(hx, hy - 260, 220, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx, hy - 260 + 8 * math.sin(t * 5), 1.0 * pop(t, ti, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx, hy - 260, 1.6, bump(t, ti, .05, .5), t, seed=161, n=5, r=180))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ti, 9)
    return view("".join(o), 560 + dx, 840 + dy, 1.35 + .12 * u, 1 - 2 * u, t=t)


def frame_s17(t):
    """«Сажусь на две минуты»: Дима плюхается на стул на «Сажусь» (отскок), на «две» на столе выскакивает таймер 2:00."""
    a, b = T0("s17"), T1("s17")
    ts = W(60) + .05
    drop = ease_in(ramp(t, ts - .25, .25))
    bounce = bump(t, ts, .04, .18)
    hip = DHIP - 200 * (1 - drop) + 14 * bounce
    if drop < 1:
        f = people.dima82(DX + 30 * (1 - drop), hip, DK, "steady", "sit_desk" if drop > .5 else "d82_rest", t=t,
                          feet=people.sit_kw(DX, DHIP, DK)["feet"])
    else:
        f = dima_sit(DX, hip, DK, "steady", t, pose="sit_desk", lean=.05)
    tim = timer_box(*TIMER_AT, .4 * pop(t, W(62), .3), t) if t > W(62) else ""
    body, _ = desk_world(t, dima=f, clock=(11, 5 + 20 * (t - a)), fold=None, lap_open=ease_out(ramp(t, ts + .3, .4)), extra_desk=tim,
                         cat_st=dict(look=(-.8, -.3), tail=10 * math.sin(t * 3)))
    o = [body, PR.sparkles(TIMER_AT[0], TIMER_AT[1] - 40, 1.2, bump(t, W(62), .05, .4), t, seed=171, n=5, r=130)]
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts, 12)
    return view("".join(o), 600 + dx, 830 + dy, 1.5 + .12 * u, 0, t=t)


def frame_s18(t):
    """«без всякого желания»: лицо Димы крупно, кислое; над ним серая тучка с дождиком, на «желания» капает по макушке,
    он пожимает плечами."""
    a, b = T0("s18"), T1("s18")
    shr = ease_io(ramp(t, W(66) - .1, .25))
    f = dima_sit(DX, DHIP, DK, "dull" if shr < .5 else "shrug", t, pose=("sit_desk", "d82_shrug"), u=shr, lean=.02)
    tim = timer_box(*TIMER_AT, .4, t)
    body, _ = desk_world(t, dima=f, clock=(11, 10), fold=None, lap_screen="dark", extra_desk=tim,
                         cat_st=dict(look=(-.8, -.3), tail=8 * math.sin(t * 2)))
    o = [body]
    hx, hy = f["head"]
    cu = pop(t, W(64), .3) if t > W(64) else 0.0
    if cu > .01:
        o.append(PR.rain(hx - 70, hy - 230, 140, t, W(65), n=6, seed=1, k=.7, floor=hy - 90, every=.1))
        o.append(PR.cloud(hx, hy - 210 + 6 * math.sin(t * 4), 260, 130, cu, cu, seed=4, col="#a9afb8"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(66), 6)
    return view("".join(o), hx + 60 + dx, hy - 120 + dy, 2.0 + .15 * u, 0, t=t)


def frame_s19(t):
    """«таймер, кот рядом»: таймер крупно, палец жмёт кнопку на «таймер», отсчёт пошёл; на «кот» кот запрыгивает на стол
    и садится рядом на «рядом»."""
    a, b = T0("s19"), T1("s19")
    press = bump(t, T_START - .05, .05, .15)
    jt = W(68) - .1
    j = ease_io(ramp(t, jt, .35))
    tim = timer_box(*TIMER_AT, .4, t, timer_secs(t), press=press)
    body, _ = desk_world(t, dima="type", clock=(11, 12), fold=None, lap_screen="page", extra_desk=tim, cat_st=False)
    o = [body]
    cx0, cy0 = 1250, FL
    cxp = cx0 + (CAT_AT[0] - 40 - cx0) * j
    cyp = cy0 + (CAT_AT[1] - cy0) * j - 220 * math.sin(math.pi * j)
    o.append(cat(cxp, cyp, .36, t, dict(look=(-.9, -.3), legs=4 * j * (1 - j), smile=ramp(t, W(69), .2), tail=10 * math.sin(t * 3))))
    o.append(PR.tap_rings(TIMER_AT[0], TIMER_AT[1] - 60, ramp(t, T_START - .05, .35), .8, col="#FFD23F"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, T_START, 8)
    return view("".join(o), TIMER_AT[0] + 40 + 30 * u + dx, TIMER_AT[1] - 10 + dy, 2.0 + .12 * u, 0, t=t)


def doc_window(x0, y0, x1, y1, t, open_u=0.0, lines=0.0):
    """Экран: рабочий стол со значком файла «ОТЧЁТ»; на open_u значок раскрывается в документ, строки печатаются."""
    w, h = x1 - x0, y1 - y0
    c = lib.clip_rect(x0, y0, w, h)
    o = [rect(x0, y0, x1, y1, "#3c6fb0")]
    if open_u < 1:
        s_ = 1 + .3 * open_u
        o.append(f'<g opacity="{1 - open_u:.3f}" transform="translate({x0 + w / 2:.1f} {y0 + h * .45:.1f}) scale({s_:.3f})">'
                 + shape(lib.rrect(-60, -50, 60, 50, 6), FOLD_C, "", w=3, seed=20001) + "</g>")
    if open_u > .01:
        k = ease_out(open_u)
        dw, dh = w * .86 * k, h * .86 * k
        dx0, dy0 = x0 + w / 2 - dw / 2, y0 + h * .5 - dh / 2
        o.append(rect(dx0, dy0, dx0 + dw, dy0 + dh, "#fdfcf7"))
        o.append(rect(dx0, dy0, dx0 + dw, dy0 + dh * .12, "#e6e8ee"))
        n = int(7 * clamp(lines) + .999) if lines > 0 else 0
        for i in range(n):
            frac = 1.0 if i < n - 1 else (7 * lines - i)
            ly = dy0 + dh * (.22 + .1 * i)
            o.append(rect(dx0 + dw * .08, ly, dx0 + dw * (.08 + .8 * clamp(frac) * (.7 + .3 * ((i * 37) % 3) / 2)), ly + dh * .035, "#5B6170"))
    return f'<g clip-path="url(#{c})">{"".join(o)}</g>'


def frame_s20(t):
    """«только открыть файл»: экран ноутбука крупно, на «открыть» значок файла раскрывается в документ; кот у экрана."""
    a, b = T0("s20"), T1("s20")
    op_u = ease_out(ramp(t, W(71), .3))
    body, _ = desk_world(t, dima=None, clock=(11, 13), fold=None, lap_screen="dark", extra_desk="", cat_st=dict(look=(-.9, -.2), tail=8 * math.sin(t * 3)),
                         cat_x=CAT_AT[0] - 80)
    x0, y0, x1, y1 = screen_rect(LAP[0], LAP[1], .5)
    o = [body, doc_window(x0, y0, x1, y1, t, op_u, .15 * ramp(t, W(72), .4))]
    o.append(PR.glow((x0 + x1) / 2, (y0 + y1) / 2, 260, .4 * op_u, "#ffffff"))
    o.append(PR.tap_rings((x0 + x1) / 2, y0 + (y1 - y0) * .45, ramp(t, W(71) - .05, .35), .6, col="#FFD23F"))
    o.append(timer_box(*TIMER_AT, .4, t, timer_secs(t)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(71), 7)
    return view("".join(o), (x0 + x1) / 2 + 20 + dx, (y0 + y1) / 2 + 30 + dy, 2.9 + .2 * u, 0, t=t)


def frame_s21(t):
    """«Желание приходит»: Дима печатает спокойно; таймер дошёл до 0:00 и звенит — Дима не встаёт; на «приходит» над
    ним загорается огонёк, искры, строки бегут."""
    a, b = T0("s21"), T1("s21")
    tf_ = W(74)
    fl = ease_out(ramp(t, tf_ - .1, .35))
    f = dima_sit(DX, DHIP, DK, "focus" if fl < .5 else "zeal", t, pose="sit_desk", lean=.12 + .03 * math.sin(t * 12))
    done = timer_secs(t) <= 0
    tim = timer_box(*TIMER_AT, .4, t, timer_secs(t), ring=bump(t, W(73) + .2, .05, .5) if done else 0.0, done=1.0 if done else 0.0)
    body, _ = desk_world(t, dima=f, clock=(11, 15), fold=None, lap_screen="lines", lap_lines=.3 + .5 * ramp(t, a, b - a),
                         extra_desk=tim, cat_st=dict(look=(-.8, -.4), smile=fl, tail=12 * math.sin(t * 3)))
    o = [body]
    hx, hy = f["head"]
    if fl > .01:
        o.append(PR.glow(hx, hy - 210, 200, .6 * fl, "#ffd27a"))
        o.append(PR.att_flame(hx, hy - 170, 1.8, t, fl, seed=1, halo=fl))
        o.append(PR.sparkles(hx, hy - 220, 1.5, bump(t, tf_, .05, .5), t, seed=211, n=6, r=180))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tf_, 9)
    return view("".join(o), 520 + dx, 800 + dy, 1.5 + .15 * u, 1 - 2 * u, t=t)


def frame_s22(t):
    """«уже на третьей минуте»: таймер крупно — 0:00, звенит зелёным, над ним три точки-минуты, на «третьей» вспыхивает
    третья с огоньком; на экране строки растут."""
    a, b = T0("s22"), T1("s22")
    t3 = W(77)
    o = []
    body, _ = desk_world(t, dima="type", clock=(11, 16), fold=None, lap_screen="lines", lap_lines=.6 + .4 * ramp(t, a, b - a),
                         extra_desk=timer_box(*TIMER_AT, .4, t, 0.0, ring=.6, done=1.0), cat_st=dict(look=(-.8, -.4), smile=1.0))
    o.append(body)
    for i in range(3):
        on = 1.0 if i < 2 else ease_out(ramp(t, t3, .2))
        px = TIMER_AT[0] - 70 + 70 * i
        py = TIMER_AT[1] - 140
        col = lib.mix("#d8d2c4", "#ffb22e", on)
        o.append(shape(ellipse_pts(px, py, 22 * (1 + .4 * bump(t, t3, .05, .3) * (i == 2)), 22 * (1 + .4 * bump(t, t3, .05, .3) * (i == 2)), 14), col, "",
                       w=3.4, seed=22000 + i))
    if t > t3:
        o.append(PR.att_flame(TIMER_AT[0] + 70, TIMER_AT[1] - 162, .8, t, ease_out(ramp(t, t3, .25)), seed=2, halo=1.0))
        o.append(PR.sparkles(TIMER_AT[0] + 70, TIMER_AT[1] - 150, 1.0, bump(t, t3, .05, .5), t, seed=221, n=5, r=90))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t3, 9)
    return view("".join(o), TIMER_AT[0] - 120 + dx, TIMER_AT[1] - 120 + dy, 2.0 + .12 * u, 0, t=t)


# ═════════════════════════ s23–s25: отчёт ушёл, пятница 16:00, выходные ═════════════════════════
def mail_screen(x0, y0, x1, y1, t, sent=0.0):
    w, h = x1 - x0, y1 - y0
    c = lib.clip_rect(x0, y0, w, h)
    o = [rect(x0, y0, x1, y1, "#fdfcf7"), rect(x0, y0, x1, y0 + h * .14, "#e6e8ee")]
    o.append(rect(x0 + w * .06, y0 + h * .22, x0 + w * .6, y0 + h * .27, "#9aa0aa"))
    o.append(shape(lib.rrect(x0 + w * .06, y0 + h * .34, x0 + w * .5, y0 + h * .56, 8), FOLD_C, "", w=2.4, seed=23001))
    o.append(txt("ОТЧЁТ", x0 + w * .28, y0 + h * .49, h * .1, "#1d2448", FOLD_C, 0))
    bs = 1 - .12 * bump(t, 0, 1, 1) * 0
    col = lib.mix("#2f8cff", "#2f9a4a", sent)
    o.append(f'<rect x="{x0 + w * .52:.1f}" y="{y0 + h * .66:.1f}" width="{w * .42:.1f}" height="{h * .2:.1f}" rx="{h * .05:.1f}" fill="{col}"/>')
    o.append(txt("Отправить" if sent < .5 else "Отправлено", x0 + w * .73, y0 + h * .8, h * .085, "#ffffff", col, 0))
    del bs
    return f'<g clip-path="url(#{c})">{"".join(o)}</g>'


def plane(x, y, k, rot=0.0):
    pts = [(-60, 0, 1), (70, -40, 1), (0, 30, 1)]
    o = shape(pts, "#ffffff", blob([(0, 30), (70, -40), (-6, 6)], "#dfe6f0"), w=3.4, seed=23100)
    return tf(o, x, y, k, rot)


def frame_s23(t):
    """«Отчёт ушёл»: ноутбук крупно, письмо с вложением ОТЧЁТ; палец-курсор жмёт «Отправить» на «ушёл», кнопка зеленеет,
    бумажный самолётик вылетает с экрана."""
    a, b = T0("s23"), T1("s23")
    ts = W(80)
    sent = ramp(t, ts, .1)
    body, _ = desk_world(t, dima="type", clock=(15, 58), fold=None, lap_screen="dark", cat_st=dict(look=(-.9, -.2)), cat_x=CAT_AT[0] - 60)
    x0, y0, x1, y1 = screen_rect(LAP[0], LAP[1], .5)
    o = [body, mail_screen(x0, y0, x1, y1, t, sent)]
    bx, by = x0 + (x1 - x0) * .73, y0 + (y1 - y0) * .76
    cur_u = ease_io(ramp(t, a, ts - a))
    cx_, cy_ = x0 + 30 + (bx - x0 - 30) * cur_u, y0 + 30 + (by - y0 - 30) * cur_u + 4 * bump(t, ts - .05, .04, .1)
    o.append(f'<path d="M{cx_:.1f} {cy_:.1f} l0 34 l9 -8 l7 14 l6 -3 l-7 -14 l12 -1Z" fill="#ffffff" stroke="#111" stroke-width="2.4"/>')
    o.append(PR.tap_rings(bx, by, ramp(t, ts - .05, .35), .5, col="#FFD23F"))
    if t > ts:
        u = ease_in(ramp(t, ts, .7))
        o.append(plane(bx + 500 * u, by - 420 * u - 80 * math.sin(math.pi * u), .5 + .3 * u, -20 - 10 * u))
        o.append(PR.speed_arcs(bx + 500 * u - 70, by - 420 * u, .5, 1 - u, t, seed=231, n=3, ang=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts, 9)
    return view("".join(o), (x0 + x1) / 2 + 30 * u + dx, (y0 + y1) / 2 + 40 + dy, 3.4 + .2 * u, 0, t=t)


def digi_clock(x, y, k, t, day="ПТ", hhmm="15:59", pulse=0.0):
    o = shape(lib.rrect(-230, -110, 230, 110, 26), "#2a2d38", "", w=5, seed=24001)
    o += shape(lib.rrect(-205, -88, 205, 88, 16), "#141821", "", w=3, seed=24002)
    o += txt(day, -128, 34, 92, "#FFD23F", "#141821", 0)
    o += txt(hhmm, 70, 34, 92, "#7CFF9A", "#141821", 0)
    return tf(o, x, y, k * (1 + .08 * pulse))


def frame_s24(t):
    """«в пятницу в четыре»: на стене цифровые часы: на «пятницу» загорается ПТ, на «четыре» 15:59 → 16:00 с толчком;
    на столе папка с оттиском СДАН, Дима потягивается, кот рядом."""
    a, b = T0("s24"), T1("s24")
    t4 = W(84)
    hhmm = "15:59" if t < t4 else "16:00"
    pul = bump(t, t4, .05, .3) + .6 * bump(t, W(82), .05, .3)
    f = dima_sit(DX, DHIP, DK, "relief", t, pose="arms_wide" if t > t4 else "sit_desk", lean=-.05)
    body, _ = desk_world(t, dima=f, clock=None, fold=dict(dust=0.0, web=0.0, stamp=1.0), lap_screen="page", phase=.25,
                         cat_st=dict(look=(-.8, -.5), smile=1.0, tail=14 * math.sin(t * 4)))
    o = [body]
    o.append(digi_clock(CLOCK[0] - 40, CLOCK[1] + 20, .9, t, "ПТ", hhmm, pul))
    o.append(PR.sparkles(CLOCK[0] - 40, CLOCK[1] + 20, 1.8, bump(t, t4, .05, .5), t, seed=241, n=6, r=260))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t4, 9)
    return view("".join(o), 660 + dx, 640 + 120 * u + dy, 1.3 + .1 * u, 0, t=t)


def frame_s25(t):
    """«и выходные были мои»: диван, Дима развалился с котом на коленях, за окном солнце; на «выходные» надпись
    ВЫХОДНЫЕ МОИ, кот мурлычет, сердечко."""
    a, b = T0("s25"), T1("s25")
    o = [room(t)]
    o.append(sky_window(300, 1000, 380, 520, t, 0.0, seed=5))
    o.append(PR.glow(300, 700, 320, .5, "#fff1b0"))
    o.append(sofa(560, FL, 1.0))
    hip = FL - 170
    f = people.dima82(500, hip, .55, "bliss", "lean_back", t=t, feet=people.sit_kw(500, hip, .55)["feet"], head_add=.04 * math.sin(t * 2))
    o.append(f["svg"])
    o.append(cat(700, FL - 160, .55, t, dict(look=(-.7, -.4), blink=.85, smile=1.0, tail=14 * math.sin(t * 3))))
    o.append(PR.purr(740, FL - 420, 1.2, t, 1.0, seed=251))
    o.append(PR.heart(650, FL - 520 - 60 * ramp(t, W(87), .8), .8 * pop(t, W(87), .3) if t > W(87) else 0.0, bump(t, W(88), .05, .3)))
    o.append(dust_motes(150, 650, 900, 1250, t, n=14, seed=9, col="#fff1b0"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(86), 6)
    return view("".join(o), 560 + dx, 1000 + dy - 40 * u, 1.3 + .12 * u, 1 - 2 * u, t=t)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
