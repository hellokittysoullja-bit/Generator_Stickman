"""Рилс 110 «Первый будильник», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Говорит Дима от первого лица (имя не звучит и не пишется). Сквозное место: спальня — кровать, подушка, окно со шторами,
будильник на тумбе у двери (хук, решение, итог, петля); аудитория с закрытой дверью; парта; кухня с кофе и окном на остановку.
NOCAM=1 — без влёта, тряски и надписей (замер движения рисунка)."""
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
import room as RM  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
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


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def tf(inner, x, y, k=1.0, rot=0.0):
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{inner}</g>'


def text(s, x, y, size, fill="#ffffff", stroke="#111", sw=10.0, anchor="middle", op=1.0):
    """Надпись шрифтом IDB (вшит в base.html) с обводкой."""
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-size="{size:.1f}" text-anchor="{anchor}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw:.1f}" stroke-linejoin="round" paint-order="stroke"{o} '
            f'style="font-kerning:none">{s}</text>')


def plain(s, x, y, size, fill="#1d2448", anchor="start", op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-size="{size:.1f}" text-anchor="{anchor}" fill="{fill}"{o} '
            f'style="font-kerning:none">{s}</text>')


# ═════════════════════════ экранные надписи ═════════════════════════
def title(t):
    if NOCAM:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


def plate(t, spec, y=220.0, w=660.0, size=58.0):
    """Маленькая жёлтая плашка вверху кадра (в безопасной зоне, выше лиц): выскакивает и тает."""
    if NOCAM:
        return ""
    a, b = spec["t_in"], spec["t_out"]
    if t < a or t > b + .15:
        return ""
    u = ease_out(ramp(t, a + .02, .2))
    op = 1.0 - ramp(t, b, .15)
    s = .6 + .4 * lib.back_out(u, 2.0) if u < 1 else 1.0
    body = (f'<rect x="{-w / 2}" y="-62" width="{w}" height="104" rx="22" fill="#FFD23F" stroke="#111" stroke-width="6"/>'
            + text(spec["text"], 0, 18, size, fill="#111", stroke="#111", sw=0.01))
    return f'<g opacity="{op:.3f}" transform="translate(540 {y}) rotate(-2) scale({s:.4f})">{body}</g>'


def kot_print(t, t0, x, y, size):
    """Кодовое слово печатными: жирный IDB, жёлтый с чёрной обводкой и тенью (как «КОТ» в рилсах 101–104); буквы выскакивают по
    одной с t0 (по 0.09 с), y — базовая линия, x — центр слова."""
    if t < t0:
        return ""
    o = []
    w = size * .74
    for j, ch in enumerate("КОТ"):
        u = clamp((t - t0 - .09 * j) / .2)
        if u <= 0:
            continue
        s = lib.back_out(u, 2.6) if u < 1 else 1.0
        cx = x + (j - 1) * w
        letter = (f'<text x="0" y="10" font-family="IDB" font-size="{size:.1f}" text-anchor="middle" fill="#000" opacity=".35" '
                  f'stroke="#000" stroke-width="{size * .12:.1f}" stroke-linejoin="round">{ch}</text>'
                  + text(ch, 0, 0, size, fill="#FFD23F", stroke="#111", sw=size * .11))
        o.append(f'<g transform="translate({cx:.1f} {y:.1f}) rotate({-3 + 2 * j}) scale({s:.4f})">{letter}</g>')
    return "".join(o)


def kot_small(t):
    """«КОТ» держится маленьким вверху до конца призыва (план s13)."""
    if NOCAM:
        return ""
    k = SH["kot"]
    if t < T1("s13") - .01 or t > k["t_out"]:
        return ""
    return kot_print(t, -9.0, 300, 330, 140)


def over(t):
    return title(t) + plate(t, SH["label"]) + plate(t, SH["label2"], w=520, size=76) + kot_small(t)


BG = "#efe2c8"


def view(body, cx, cy, s, rot=0.0, bg=BG, t=0.0, extra=""):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{extra}{over(t)}')


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
            blur += (f'<use href="#hk110" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk110">{body}</g></g>{blur}'


def cat(x, y, k, t, st=None):
    st = dict(dict(look=(-.4, -.2), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t)


# ═════════════════════════ телефон крупно в руке (хук, s05, s11, петля) ═════════════════════════
PH_C = (540.0, 980.0)
PX0, PY0, PX1, PY1 = PR.phone_frame_rect(*PH_C, 1.0)        # экран 560×1000
BTN = (540.0, PY1 - 240.0)                                  # зелёная кнопка «Вызов»
BTN_R = 92.0
PH_BG = "#3b3552"

def phone_hand(t, screen, typing=0.0, shake_u=0.0, thumb_to=None, bg=PH_BG, thumb=True):
    """Телефон в руке крупно (экран — SVG screen(x0, y0, x1, y1)); большой палец тянется к thumb_to; рукав худи снизу."""
    cx, cy = PH_C
    o = [rect(-900, -1400, 2200, 2600, bg)]
    for j, (bx, by, br) in enumerate(((-120, 260, 160), (1180, 420, 210), (60, 1700, 190), (1120, 1600, 150))):
        o.append(blob(ellipse_pts(bx, by, br, br, 22), "#ffd9a0", .08 + .03 * math.sin(t * 2 + j)))
    o.append(PR.glow(cx, cy, 900, .35, "#8fb7ff"))
    o.append(PR.phone_frame(cx, cy, 1.0, 1.0, glow_=.4, seed=1))
    x0, y0, x1, y1 = PX0, PY0, PX1, PY1
    c = lib.clip_rect(x0, y0, x1 - x0, y1 - y0)
    o.append(f'<g clip-path="url(#{c})">{screen(x0, y0, x1, y1)}</g>')
    # ладонь снизу и рукав худи (горчичный)
    o.append(shape([(x1 + 40, y1 + 520), (x1 + 420, y1 + 380), (x1 + 640, y1 + 1200), (x0 + 100, y1 + 1200)], "#d9a441",
                   blob([(x1 + 40, y1 + 700), (x1 + 640, y1 + 600), (x1 + 640, y1 + 1200), (x0 + 100, y1 + 1200)], "#b9862c", .7), w=5, seed=5019))
    o.append(shape([(x0 - 70, y1 - 160), (x0 + 40, y1 + 40), (x1 + 20, y1 + 120), (x1 + 200, y1 + 560), (x0 + 60, y1 + 760), (x0 - 140, y1 + 600)],
                   "#ecc4a2", blob([(x0 - 70, y1 + 200), (x1 + 100, y1 + 300), (x1 + 160, y1 + 600), (x0 - 140, y1 + 600)], "#d9a984", .7), w=5,
                   seed=5020))
    if thumb:
        if thumb_to is not None:
            tx, ty = thumb_to
        else:
            tx = x0 + 160 + 200 * (.5 + .5 * math.sin(t * 9)) * typing
            ty = y1 - 70 - 40 * abs(math.sin(t * 22)) * typing
        o.append(shape(lib.band([(x1 + 110, y1 + 420), (tx + 30, ty + 40)], 120, 92), "#ecc4a2", "", w=5, seed=5021))
        o.append(shape(ellipse_pts(tx + 22, ty + 18, 30, 38, 14), "#f7ddd0", "", w=3, seed=5022))
    sx = 14 * shake_u * math.sin(t * 60)
    sy = 6 * shake_u * math.cos(t * 47)
    rot = 1.2 * shake_u * math.sin(t * 38)
    return f'<g transform="translate({sx:.2f} {sy:.2f}) rotate({rot:.2f} {cx} {cy + 600})">{"".join(o)}</g>'

FL = 1300.0
WALL, WALL_SH, FLOOR_C = "#efe2c8", "#e3d2b2", "#cdb48c"
DESK_Y = FL - 300
def chair(x, y, k=1.0):
    o = [shape(lib.rrect(-100, -16, 110, 10, 6), "#a8774a", "", w=4, seed=1011)]
    o.append(shape([(-100, -16, 1), (-80, -16, 1), (-70, -330, 1), (-92, -330, 1)], "#a8774a", "", w=4, seed=1012))
    for s in (-1, 1):
        o.append(shape([(s * 80 - 9, 8, 1), (s * 80 + 9, 8, 1), (s * 86 + 9, 240, 1), (s * 86 - 9, 240, 1)], "#8a6038", "", w=3.4, seed=1013 + s))
    return tf("".join(o), x, y, k)


def mini_phone(x, y, k, rot=0.0, screen="#2f3a55", inner=""):
    """Телефон в руке (центр), экран 120×220 в своих координатах."""
    o = [shape(lib.rrect(-72, -128, 72, 128, 22), "#2a2d36", "", w=4, seed=9700)]
    o.append(shape(lib.rrect(-60, -112, 60, 112, 12), screen, inner, w=2.4, seed=9701))
    return tf("".join(o), x, y, k, rot)


def desk_room(t, strikes=(), mode="day", sun=0.0, list_on=True):
    o = [rect(-1400, -1400, 2600, FL, WALL)]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, FL, WALL_SH, .55))
    o.append(rect(-1400, FL, 2600, FL + 1400, FLOOR_C))
    o.append(line([(-1400, FL), (2600, FL)], 5, seed=11))
    o.append(PR.window(150, 700, 300, 420, mode=mode, t=t, seed=3, curtain=False))
    if sun > 0:
        o.append(PR.glow(150, 500, 420, .35 * sun, "#fff1b0"))
    o.append(chair(320, FL - 240, 1.0))
    o.append(PR.desk(680, DESK_Y, w=660, depth=100, leg_h=260, seed=7))
    return o


DHIP = FL - 290


def dima_desk(t, expr="calm82", pose="sit_desk", arms=None, hands=None, head_add=0.0, lean=.1):
    feet = people.sit_kw(360, DHIP, .5)["feet"]
    kw = {}
    if arms:
        kw["arms"] = arms
    if hands:
        kw["hands"] = hands
    return people.dima82(360, DHIP, .5, expr, pose, t=t, feet=feet, lean_add=lean, head_add=head_add, **kw)


def dima_call(t, expr="proud82", head_add=0.0):
    """Дима за столом, телефон у уха (ближняя рука к виску, телефон закрывает ухо, лицо открыто)."""
    feet = people.sit_kw(360, DHIP, .5)["feet"]
    probe = people.dima82(360, DHIP, .5, expr, "sit_desk", t=t, feet=feet, lean_add=.1, head_add=head_add)
    tx, ty = probe["temple"]
    tgt = (tx - 70 * .5, ty + 150 * .5)
    arms = {"f": ("ang", 0.16, 0.16), "n": ("ik", tgt, 1)}
    hands = {"f": {"curl": (.4, .4, .45, .5), "thumb": .4}, "n": {"dir": (.3, -1), "curl": (.7, .75, .8, .8), "thumb": .6}}
    f = people.dima82(360, DHIP, .5, expr, "sit_desk", t=t, feet=feet, lean_add=.1, head_add=head_add, arms=arms, hands=hands)
    hx, hy = f["head"]
    ph = mini_phone(tx - 34, ty + 18, .42, -14, screen="#1d2448")
    return f, ph

PAPER = "#f6efdf"


def paper_bg():
    return rect(-2000, -2000, 3500, 4000, PAPER) + "".join(
        line([(-1200, 200 + 90 * j), (2600, 200 + 90 * j)], 2, "#e3d6bb", taper=0, wmin=1, seed=6000 + j) for j in range(24))



# ═════════════════════════ мессенджер: иконка, список чатов, чат ═════════════════════════


GREEN, RED, BLUE = "#3fb26a", "#e2453a", "#2f8fe0"


RFL = 1560.0


def plain_room(t, wall=WALL, floor=FLOOR_C, x0=-1400.0, x1=2600.0):
    o = [rect(x0, -1400, x1, RFL, wall)]
    for i in range(int(x0 // 120), int(x1 // 120) + 1):
        o.append(rect(i * 120, -1400, i * 120 + 46, RFL, WALL_SH, .55))
    o.append(rect(x0, RFL - 46, x1, RFL, "#d8c3a0"))
    o.append(line([(x0, RFL - 46), (x1, RFL - 46)], 3, seed=7))
    o.append(rect(x0, RFL, x1, RFL + 1400, floor))
    o.append(line([(x0, RFL), (x1, RFL)], 5, seed=11))
    return "".join(o)


def day_timer(x, y, k, u, t, label="24 ч"):
    """Таймер «24 ч»: круг циферблата, зелёный сектор обходит круг на u."""
    o = [blob(ellipse_pts(x + 10, y + 14, 230 * k, 230 * k, 30), "#000000", .2)]
    o.append(shape(ellipse_pts(x, y, 230 * k, 230 * k, 30), "#ffffff", "", w=7, seed=8500))
    r = 200 * k
    if u > .005:
        a1 = -90 + 360 * clamp(u)
        large = 1 if a1 + 90 > 180 else 0
        ex, ey = x + r * math.cos(math.radians(a1)), y + r * math.sin(math.radians(a1))
        if u < .999:
            o.append(f'<path d="M{x} {y} L{x} {y - r} A{r} {r} 0 {large} 1 {ex:.1f} {ey:.1f} Z" fill="#7cc46a" opacity=".8"/>')
        else:
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#7cc46a" opacity=".8"/>')
    for j in range(12):
        a = math.radians(j * 30)
        o.append(line([(x + 205 * k * math.cos(a), y + 205 * k * math.sin(a)), (x + 225 * k * math.cos(a), y + 225 * k * math.sin(a))], 5, INK,
                      taper=0, wmin=1, seed=8510 + j))
    ha = math.radians(-90 + 360 * clamp(u))
    o.append(line([(x, y), (x + 170 * k * math.cos(ha), y + 170 * k * math.sin(ha))], 10, INK, taper=.3, wmin=.5, seed=8530))
    o.append(text(label, x, y + 50 * k, 140 * k, fill="#1d2448", stroke="#ffffff", sw=10))
    return "".join(o)


FL82 = RM.FL82
HK = .85
HHIP = FL82 - 598 * HK
HDOOR = RM.HALL82["door"]


# ═════════════════════════ рилс 109: стол с книгой ═════════════════════════
BOOK = (560.0, DESK_Y - 30.0)       # дно корешка раскрытой книги на столе
PHN = (760.0, DESK_Y - 40.0)        # телефон на столе
HIT01 = stress(1, .4)


def table(t, mode="evening", lamp=1.0):
    o = desk_room(t, mode=mode)
    o.append(PR.lamp_desk(1060, DESK_Y - 70, 1.1, on=lamp, tilt=-10, seed=1))
    if lamp > 0:
        o.append(PR.glow(620, DESK_Y - 120, 380, .3 * lamp, "#fff1b0"))
    return o


def reader(t, expr="focus", head_add=0.12, lean=.16, arms=None, hands=None):
    e = dict(people.EXPR["dima"]["focus"]) if expr == "focus" else expr
    if expr == "focus":
        e.update(look=(.7, .75), bags=False)
    return dima_desk(t, e, head_add=head_add, lean=lean, arms=arms, hands=hands)


def book(t, k=.85, flip=0.0, blur=0.0):
    return PR.book_open(BOOK[0], BOOK[1], k, flip=flip, seed=1)


def phone_desk(x, y, k=1.0, rot=0.0, buzz=0.0, t=0.0, glow_=0.0):
    bx = 6 * buzz * math.sin(t * 90)
    br = 3 * buzz * math.sin(t * 70)
    o = PR.phone_flat(x + bx, y, k, rot + br, face_down=False, glow_=glow_, seed=3)
    if buzz > .05:
        for s in (-1, 1):
            o += line([(x + s * 110 * k, y - 30 * k), (x + s * 140 * k, y - 50 * k)], 5, "#e2453a", taper=0, wmin=1, seed=40 + s)
            o += line([(x + s * 120 * k, y), (x + s * 155 * k, y - 6 * k)], 5, "#e2453a", taper=0, wmin=1, seed=42 + s)
    return o


CATD = (880.0, DESK_Y - 50.0)      # кот сидит на столе справа


def phone_crawl(t):
    c = ease_out(ramp(t, -.2, 1.6))
    return PHN[0] - 90 * c, PHN[1]


BCAM = (600.0, 960.0, 1.15)        # общий план спальни


def bview(o, t, z=0.0, dx=0.0, dy=0.0, rot=0.0, cx=None, cy=None, s=None):
    return view("".join(o), (cx or BCAM[0]) + dx, (cy or BCAM[1]) + dy, (s or BCAM[2]) + z, rot, t=t)


def stand(x, t, expr="proud82", pose="d82_rest", flip=False, k=.78, **kw):
    hip = BFL - (people.LEG_LEN - 12) * k - 6
    return people.dima82(x, hip, k, expr, pose, t=t, feet="stand", flip=flip, **kw)


def pillow_cat(t, look=(.8, -.2), lie=False, smug=0.0):
    if lie:
        return CT.curl(PIL[0] + 40, MAT + 2, .5, dict(eye=.5, squint=smug, look=(.6, -.4)), t)
    return cat(PIL[0] + 10, MAT - 6, .5, t, dict(look=look, perk=1.0, smile=.6, tail=10 * math.sin(t * 3)))


def empty_bed(t, blanket=True):
    o = PR.pillow(PIL[0] + 20, MAT - 10, 1.3, seed=1)
    if blanket:
        o += PR.blanket(BED[0] + 120, MAT + 4, 1.0, w=520, h=90, seed=2, col="quilt", bump=.6)
    return o


def frame_s01(t):
    """ХУК: будильник звенит на тумбе у двери, Дима в кровати распахивает глаза; кот сидит на подушке."""
    o = bedroom(t, sun=1.0)
    o.append(pillow_cat(t))
    o.append(in_bed(t, expr="saucer" if t > .15 else "awake73")["svg"])
    o.append(clock_on_stand(t, ring=1.0))
    o.append(overlay(t, sun=.6))
    dx, dy = shake(t, HIT01, 10)
    v = f'<g transform="{lib.cam(620 + dx, 1180 + dy, 1.2, 0)}">{"".join(o)}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + over(t))


def frame_s02(t):
    """«встаю с первого будильника»: Дима садится, одеяло взлетает; на «первого» он уже стоит у кровати и тянется; кот на подушке."""
    a, b = T0("s02"), T1("s02")
    tu = W(4) - .05
    o = bedroom(t, sun=1.0)
    if t < tu:
        o.append(pillow_cat(t))
        o.append(in_bed(t, sit=ease_out(ramp(t, a, .25)), expr="rush82" if False else "saucer")["svg"])
        o.append(people.cocoon_blanket(BHIP[0] + 160, MAT - 40, .55, ramp(t, a + .1, .5), t))
    else:
        o.append(empty_bed(t, blanket=False))
        o.append(pillow_cat(t, look=(.9, -.4)))
        o.append(people.cocoon_blanket(BHIP[0] + 160, MAT - 40, .55, .6 + .4 * ramp(t, tu, .4), t))
        f = stand(700, t, "laugh82", "d82_one", k=.66, head_add=.05 * bump(t, tu, .05, .3))
        o.append(f["svg"])
        o.append(PR.sparkles(700, 800, 1.6, bump(t, tu + .05, .05, .5), t, seed=12, n=6, r=220))
    o.append(clock_on_stand(t, ring=1.0 - ramp(t, W(5), .2), press=ramp(t, W(5), .1)))
    o.append(overlay(t, sun=.6))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tu, 12)
    return bview(o, t, .05 + .04 * u, dx, dy, -1 + 2 * u, cy=1110)


def press_hand(bx, by, u):
    """Рука снизу справа жмёт кнопку (u 0 — у края, 1 — палец на кнопке)."""
    sx, sy = 1260, 1800
    tx, ty = sx + (bx - sx) * u, sy + (by - sy) * u
    o = shape(lib.band([(sx + 200, sy + 400), (tx + 30, ty + 50)], 170, 120), "#d9a441", "", w=5, seed=5101)
    o += shape(lib.band([(tx + 120, ty + 200), (tx + 10, ty + 10)], 110, 70), "#ecc4a2", "", w=5, seed=5102)
    o += shape(ellipse_pts(tx, ty, 44, 52, 14), "#f7ddd0", "", w=4, seed=5103)
    return o


def frame_s03(t):
    """«А раньше переставлял его пять раз»: будильник крупно на тумбе у подушки, рука пять раз жмёт кнопку, счётчик ×1…×5, время ползёт."""
    a, b = T0("s03"), T1("s03")
    presses = [a + .15 + (W(11) - a - .2) * q / 4 for q in range(5)]
    n = sum(1 for q in presses if t >= q)
    pr = max((bump(t, q, .05, .12) for q in presses), default=0.0)
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552")]
    o.append(PR.glow(540, 900, 700, .3, "#8fb7ff"))
    o.append(PR.pillow(220, 1500, 3.2, seed=1))
    o.append(shape(lib.rrect(380, 1260, 1000, 1900, 16), "#a8774a", "", w=5, seed=620))
    o.append(AL.alarm(640, 1030, 420, hh=7, mm=5 * n, ring=0.0 if pr > .2 else .6, t=t, press=pr, uid="al3"))
    bx, by = 640, 1030 - 230
    near = .85 + .15 * pr
    o.append(press_hand(bx + 20, by - 10, near if t > a + .05 else ramp(t, a - .1, .15)))
    if n:
        o.append(text(f"×{n}", 860, 520, 220 * (1 + .25 * bump(t, presses[n - 1], .04, .2)), fill="#e2453a", stroke="#111", sw=14))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(10), 10)
    return view("".join(o), 560 + dx, 1000 + dy, 1.0 + .06 * u, 0, bg="#3b3552", t=t)


def corridor(t, door=0.0):
    o = [plain_room(t, wall="#dfe6e9")]
    o.append(PR.door(800, RFL, 1.0, ajar=door, seed=4, col="#8fa7c9"))
    o.append(shape(lib.rrect(720, RFL - 1110, 880, RFL - 1010, 10), "#ffffff", "", w=4, seed=630))
    o.append(text("205", 800, RFL - 1036, 70, fill="#1d2448", stroke="#ffffff", sw=2))
    return o


def frame_s04(t):
    """«опаздывал на пары»: Дима бежит по коридору к аудитории, дверь закрыта, он врезается в неё взглядом; пот."""
    a, b = T0("s04"), T1("s04")
    o = corridor(t)
    k = .78
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    stop = ramp(t, W(14) - .1, .2)
    x = 150 + 380 * ease_out(ramp(t, a - .1, W(14) - a))
    if stop < 1:
        f = people.dima82_run(x, hip, k, (t - a) / .35, t=t, expr="rush82", boot=False, socks=None, sandwich=False)
    else:
        f = people.dima82(x, hip, k, "panic82", "d82_shrug", t=t, feet="stand")
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.sweat(hx - 60, hy - 40, 1.2, -20))
    o.append(PR.speed_arcs(x - 220, hip - 200, 1.2, 1 - stop, t, seed=7, n=3, ang=180))
    if t > W(14):
        o.append(text("!", 900, RFL - 1180, 200 * pop(t, W(14), .25), fill="#e2453a", stroke="#111", sw=12))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(14) + .1, 12)
    return view("".join(o), 560 + dx, 1060 + dy, 1.12 + .06 * u, 0, t=t)


def frame_s05(t):
    """«а потом весь день был разбитым»: Дима за партой клюёт носом над тетрадью, Z над головой."""
    a, b = T0("s05"), T1("s05")
    o = desk_room(t, mode="day")
    o.append(PR.paper(560, DESK_Y - 40, 1.6, -6, w=180, h=130, seed=3, kind="lines", sy=.5))
    nod = .5 + .5 * math.sin((t - a) * 5)
    e = {"brows": "tired", "mouth": "tired", "lid": .2 + .2 * (1 - nod), "look": (.3, .6)}
    f = dima_desk(t, e, head_add=.1 + .25 * nod, lean=.2 + .12 * nod)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.zzz(hx + 120, hy - 150, 1.2, t, 1.0))
    o.append(PR.pen(640, DESK_Y - 60, .8, 70))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(20), 6)
    return view("".join(o), 520 + dx, 860 + dy, 1.7 + .08 * u, 0, t=t)


def frame_s06(t):
    """«Вот что я поменял»: спальня, Дима у кровати поднимает палец, над ним лампочка; кот на подушке; надпись сверху."""
    a, b = T0("s06"), T1("s06")
    t_idea = W(21) + .15
    o = bedroom(t)
    o.append(empty_bed(t))
    o.append(pillow_cat(t))
    f = stand(720, t, "wow82" if t > t_idea else "sure82", "d82_one", head_add=.06 * bump(t, t_idea, .08, .3))
    o.append(f["svg"])
    hx, hy = f["head"]
    if t > t_idea:
        o.append(PR.glow(hx + 190, hy - 170, 220, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx + 190, hy - 170 + 8 * math.sin(t * 5), 1.2 * pop(t, t_idea, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx + 190, hy - 170, 1.8, bump(t, t_idea, .05, .5), t, seed=41, n=5, r=200))
    o.append(clock_on_stand(t))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_idea, 9)
    return bview(o, t, .04 * u, dx, dy, -1 + 2 * u)


def frame_s07(t):
    """«Будильник стоит у двери, а не у кровати»: будильник прыгает с места у кровати на тумбу у двери; у кровати красный крест."""
    a, b = T0("s07"), T1("s07")
    o = bedroom(t)
    o.append(empty_bed(t))
    o.append(pillow_cat(t, look=(.9, -.3)))
    o.append(shape(lib.rrect(140, BFL - 220, 260, BFL, 8), "#a8774a", "", w=4, seed=640))
    j = ease_io(ramp(t, W(25), .5))
    x0, y0 = 200, BFL - 220 - 40
    x1, y1 = NST[0], NST[1] - 300 - 40
    x = x0 + (x1 - x0) * j
    y = y0 + (y1 - y0) * j - 320 * math.sin(math.pi * j)
    o.append(AL.alarm(x, y, 110, hh=7, mm=0, ring=0.0, t=t, rot=360 * j, uid="al7"))
    if j >= 1:
        o.append(PR.sparkles(x1, y1 - 60, 1.4, bump(t, W(25) + .5, .05, .4), t, seed=51, n=5, r=150))
    cu = ramp(t, W(32) - .1, .25)
    if cu > 0:
        o.append(line([(140, BFL - 380), (140 + 120 * cu, BFL - 380 + 120 * cu)], 16, "#e2453a", taper=.2, wmin=.6, seed=651))
        if cu > .5:
            o.append(line([(260, BFL - 380), (260 - 120 * (cu - .5) * 2, BFL - 380 + 120 * (cu - .5) * 2)], 16, "#e2453a", taper=.2, wmin=.6,
                          seed=652))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(32), 9)
    return bview(o, t, .02 * u, dx, dy, cx=580)


def frame_s08(t):
    """«Чтобы выключить, приходится встать»: Дима идёт от кровати к двери и жмёт кнопку звенящего будильника."""
    a, b = T0("s08"), T1("s08")
    tp = W(36)
    o = bedroom(t)
    o.append(empty_bed(t))
    o.append(pillow_cat(t, look=(.9, -.3)))
    k = .78
    hip = BFL - (people.LEG_LEN - 12) * k - 6
    w = ease_io(ramp(t, a, tp - .3 - a))
    x = 380 + (NST[0] - 260 - 380) * w
    if w < 1:
        f = people.dima82_walk(x, hip, k, (t - a) / .5, t=t, expr="squint82", mug=False)
    else:
        f = people.dima82(x, hip, k, "proud82" if t > tp else "squint82", "d82_press", t=t, feet="stand")
    o.append(f["svg"])
    o.append(clock_on_stand(t, ring=1.0 - ramp(t, tp, .15), press=bump(t, tp, .05, .3)))
    if t > tp:
        o.append(PR.tap_rings(NST[0], NST[1] - 400, ramp(t, tp, .35), 1.4, col="#FFD23F"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tp, 9)
    return bview(o, t, .06 * u, dx, dy, cx=620 + 80 * u)


def frame_s09(t):
    """«Шторы открыты с вечера»: вечер, Дима у окна раздвигает шторы."""
    a, b = T0("s09"), T1("s09")
    cu = ease_io(ramp(t, W(38) - .2, .6))
    o = bedroom(t, curt=cu, night=True)
    o.append(empty_bed(t))
    o.append(overlay(t, night=.6))
    f = stand(WIN[0] + 10, t, "calm82", "d82_shrug" if cu > .3 else "d82_hold", head_add=-.15)
    o.append(f["svg"])
    o.append(PR.sparkles(WIN[0], WIN[1] - 300, 1.4, bump(t, W(40), .05, .5), t, seed=61, n=4, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(38), 6)
    return view("".join(o), WIN[0] + dx, 980 + dy, 1.2 + .06 * u, 0, bg="#1d2448", t=t)


def frame_s10(t):
    """«и свет будит вместе со звонком»: утро, солнце заливает комнату через открытое окно, будильник звенит, Дима садится и щурится."""
    a, b = T0("s10"), T1("s10")
    sun = ease_io(ramp(t, W(42) - .2, .6))
    o = bedroom(t, sun=1.0)
    o.append(pillow_cat(t, look=(.6, -.6)))
    o.append(in_bed(t, sit=ease_out(ramp(t, W(46) - .4, .4)), expr="squint82" if sun > .5 else "awake73")["svg"])
    o.append(clock_on_stand(t, ring=1.0 if t > W(44) else 0.0))
    o.append(overlay(t, sun=.3 + .9 * sun))
    o.append(PR.sparkles(WIN[0], WIN[1] - 260, 2.0, bump(t, W(42), .05, .6), t, seed=71, n=6, r=260))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(46), 8)
    return bview(o, t, .05 + .05 * u, dx, dy, cy=1100)


def frame_s11(t):
    """«А кот садится на подушку»: Дима встал (на краю кадра), кот запрыгивает с пола на подушку и садится."""
    a, b = T0("s11"), T1("s11")
    tl = W(51)
    o = bedroom(t, sun=1.0)
    o.append(empty_bed(t))
    j = ease_io(ramp(t, W(48) - .2, tl - W(48) + .2))
    x = 760 + (PIL[0] + 10 - 760) * j
    y = BFL + (MAT - 6 - BFL) * j - 260 * math.sin(math.pi * j)
    o.append(cat(x, y, .5, t, dict(look=(-.8, -.2), legs=1.0 if 0 < j < 1 else 0.0, perk=1.0, smile=.8 * ramp(t, tl, .2),
                                  tail=14 * math.sin(t * 5))))
    if t > tl:
        o.append(PR.dust_puff(PIL[0] + 20, MAT, .7, ramp(t, tl, .4), seed=5))
    f = stand(780, t, "calm82", "d82_rest", flip=True)
    o.append(f["svg"])
    o.append(overlay(t, sun=.5))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tl, 9)
    return bview(o, t, .03 * u, dx, dy, cx=580)


def frame_s12(t):
    """«и обратно лечь уже некуда»: Дима поворачивается к кровати, кот развалился клубком на подушке; Дима смеётся."""
    a, b = T0("s12"), T1("s12")
    o = bedroom(t, sun=1.0)
    o.append(empty_bed(t))
    o.append(pillow_cat(t, lie=True, smug=ramp(t, W(54), .3)))
    f = stand(680, t, "puzzled82" if t < W(55) else "laugh82", "d82_shrug", flip=True, head_add=.04 * math.sin(t * 5))
    o.append(f["svg"])
    o.append(PR.purr(PIL[0] + 120, MAT - 140, .9, t, 1.0, seed=2))
    o.append(overlay(t, sun=.5))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(56), 8)
    return bview(o, t, .03 + .04 * u, dx, dy, cx=560)


def frame_s13(t):
    """«Напиши «КОТ»»: поле комментария, крупно печатается жёлтое «КОТ»; Дима внизу слева, кот прыгает и садится рядом с ним."""
    a, b = T0("s13"), T1("s13")
    t_k = a - .1
    o = [paper_bg()]
    cb = 1.0
    if cb > .01:
        box = (f'<rect x="-420" y="-200" width="840" height="400" rx="40" fill="#ffffff" stroke="#111" stroke-width="7"/>'
               + f'<path d="M-260 196 l-40 90 l120 -90 z" fill="#ffffff" stroke="#111" stroke-width="7" stroke-linejoin="round"/>'
               + f'<rect x="-416" y="150" width="832" height="40" fill="#ffffff"/>'
               + plain("комментарий", -370, -130, 40, fill="#9aa0aa"))
        if t < t_k and int(t * 6) % 2 == 0:
            box += rect(-6, -60, 6, 60, "#2f6fd1")
        o.append(tf(box, 540, 590, cb, -1.5))
    o.append(PR.glow(540, 700, 420, .5 * ramp(t, t_k + .2, .3), "#ffe9a8"))
    o.append(kot_print(t, t_k, 540, 680, 300))
    o.append(PR.sparkles(540, 600, 2.4, bump(t, t_k + .3, .05, .5), t, seed=91, n=6, r=380))
    k = .62
    hip = 1640 - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(330, hip, k, "proud82", "d82_rest", t=t, feet="stand", head_add=.05 * math.sin(t * 3))
    o.append(f["svg"])
    t_j = a + .25
    j = ease_io(ramp(t, t_j, .4))
    x = 1180 + (620 - 1180) * j
    y = 1640 - 260 * math.sin(math.pi * j)
    o.append(cat(x, y, .9, t, dict(look=(-.7, -.4), legs=1.0 - j if j < 1 else 0.0, smile=1.0 if j >= 1 else .4, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_k + .25, 8)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)


def frame_s14(t):
    """«чтобы тоже вставать с первого раза»: утро, будильник звенит, Дима бодро вскакивает у кровати."""
    a, b = T0("s14"), T1("s14")
    tu = W(64)
    o = bedroom(t, sun=1.0)
    o.append(empty_bed(t, blanket=t > tu))
    o.append(pillow_cat(t, look=(.8, -.4)))
    if t < tu:
        o.append(in_bed(t, sit=ease_out(ramp(t, a, .4)), expr="saucer")["svg"])
    else:
        f = stand(780, t, "laugh82", "d82_one", k=.66, head_add=.05 * bump(t, tu, .05, .3))
        o.append(f["svg"])
        o.append(PR.sparkles(780, 820, 1.6, bump(t, tu, .05, .5), t, seed=81, n=6, r=220))
    o.append(clock_on_stand(t, ring=1.0 - ramp(t, tu + .2, .2)))
    o.append(overlay(t, sun=.6))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tu, 10)
    return bview(o, t, .05 + .05 * u, dx, dy, cy=1100)


def frame_s15(t):
    """«и успевать к первой паре»: дверь аудитории открыта, Дима спокойно заходит с улыбкой; часы над дверью."""
    a, b = T0("s15"), T1("s15")
    o = corridor(t, door=1.0)
    ah, am = PR.clock_hm(8, 55)
    o.append(PR.clock(380, RFL - 1150, 90, ah, am, seed=2))
    k = .78
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    x = 440 + 260 * ease_io(ramp(t, a, b - a))
    f = people.dima82_walk(x, hip, k, (t - a) / .5, t=t, expr="proud82", mug=False)
    o.append(f["svg"])
    o.append(PR.sparkles(800, RFL - 600, 1.8, bump(t, W(69), .05, .5), t, seed=91, n=6, r=240))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(69), 7)
    return view("".join(o), 600 + dx, 980 + dy, 1.12 + .06 * u, 0, t=t)


KFL = 1500.0


def kitchen(t, mode="day"):
    o = [rect(-1400, -1400, 2600, KFL, "#f3dcc0")]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, KFL, "#ead0b0", .6))
    o.append(rect(-1400, KFL, 2600, KFL + 1400, "#c9a77e"))
    o.append(line([(-1400, KFL), (2600, KFL)], 5, seed=11))
    return o


def street_window(t, x, y, w, h, bus_u=0.0, run=True):
    """Окно на остановку: небо, дорога, автобус уезжает, люди бегут к нему."""
    c = lib.clip_rect(x - w / 2, y - h, w, h)
    inner = [rect(x - w / 2, y - h, x + w / 2, y, "#bfe3f5"), rect(x - w / 2, y - h * .32, x + w / 2, y, "#9aa3ad")]
    inner.append(PR.bus(x - 60 + 500 * bus_u, y - h * .12, .55, u=bus_u, seed=1, puff=bus_u))
    if run:
        for q, kind in enumerate(("student", "elder")):
            ph = (t / .3 + q * .5)
            inner.append(people.townsman82_walk(kind, x - w / 2 + 40 + 60 * q + 120 * (t % 3), y - h * .12 - 60, .28, ph, t=t,
                                                hold_ribbon=False)["svg"])
    o = f'<g clip-path="url(#{c})">{"".join(inner)}</g>'
    o += f'<rect x="{x - w / 2}" y="{y - h}" width="{w}" height="{h}" fill="none" stroke="#f7f1e3" stroke-width="22"/>'
    o += line([(x, y - h), (x, y)], 14, "#f7f1e3", taper=0, wmin=1, seed=700)
    o += rect(x - w / 2 - 30, y, x + w / 2 + 30, y + 26, "#e8dcc4")
    return o


def frame_s16(t):
    """«Сегодня в восемь я уже пил кофе»: кухня, часы на 8:00, Дима за столом с кружкой кофе, пар; кот на подоконнике."""
    a, b = T0("s16"), T1("s16")
    o = kitchen(t)
    o.append(street_window(t, 760, 900, 460, 460, run=False))
    ah, am = PR.clock_hm(8, 0)
    o.append(PR.clock(230, 900, 90 * (1 + .1 * bump(t, W(73), .05, .3)), ah, am, seed=3))
    ty = KFL - 330
    k = .62
    hip = ty + 20
    f = people.dima82(330, hip, k, "proud82", "d82_mug", t=t, feet=people.sit_kw(330, hip, k)["feet"], head_add=-.04)
    o.append(PR.stool(330, hip + 40, .62, seed=1))
    o.append(f["svg"])
    mx, my = f["hold"]
    o.append(PR.mug(mx + 10, my + 30, 1.3, col="red", coffee=True, steam=1.0, t=t))
    o.append(PR.desk(560, ty, w=520, depth=90, leg_h=320, seed=9))
    o.append(PR.coffee_pot(700, ty - 40, .8) if hasattr(PR, "coffee_pot") else "")
    o.append(cat(900, 900, .5, t, dict(look=(-.8, .2), smile=.8, tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(230, 900, 1.4, bump(t, W(73), .05, .5), t, seed=95, n=5, r=160))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(73), 8)
    return view("".join(o), 500 + dx, 1100 + dy, 1.35 + .06 * u, 0, t=t)


def frame_s17(t):
    """«а не бежал на остановку»: Дима с кружкой у окна; за окном люди бегут к автобусу, автобус уезжает; Дима улыбается."""
    a, b = T0("s17"), T1("s17")
    o = kitchen(t)
    bu = ease_io(ramp(t, W(80) - .3, 1.2))
    o.append(street_window(t, 620, 1060, 700, 640, bus_u=bu))
    k = .82
    hip = KFL - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(260, hip, k, "proud82", "d82_mug", t=t, feet="stand", head_add=-.05)
    o.append(f["svg"])
    mx, my = f["hold"]
    o.append(PR.mug(mx + 10, my + 30, 1.4, col="red", coffee=True, steam=1.0, t=t))
    o.append(cat(900, 1110, .5, t, dict(look=(-.3, -.2), smile=1.0, tail=12 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(80), 7)
    return view("".join(o), 540 + dx, 1000 + dy, 1.15 + .06 * u, 0, t=t)


def frame_s18(t):
    """Петля: кадр хука — Дима в кровати, будильник начинает звенеть."""
    a, b = T0("s18"), T1("s18")
    import anim
    hc = anim.hook_cam(0.0, hit=HIT01)
    u = ease_io(ramp(t, a, b - a))
    o = bedroom(t, sun=1.0)
    o.append(pillow_cat(t))
    o.append(in_bed(t, expr="awake73")["svg"])
    o.append(clock_on_stand(t, ring=ramp(t, a + .1, .3)))
    o.append(overlay(t, sun=.6))
    s = 1.2 * (1 + (hc["zoom"] - 1) * u)
    return view("".join(o), 620, 1180, s, hc["rot"] * u, t=t)


def frame(sid, t):
    lib.DEFS.clear()

# ═════════════════════════ рилс 110: спальня ═════════════════════════
import alarm as AL  # noqa: E402

BFL = 1500.0                       # пол спальни
BED = (640.0, BFL, 1.25)            # кровать: ножки, масштаб (изголовье слева)
MAT = BED[1] - 118 * BED[2]         # верх матраса
BHIP = (BED[0] + 60, MAT + 10)      # таз Димы на матрасе
PIL = (BED[0] - 250, MAT - 30)      # подушка (кот садится сюда)
WIN = (560.0, 950.0)                # окно (центр низа рамы)
NST = (1000.0, BFL)                  # тумба у двери
DOORB = (1270.0, BFL)
HIT01 = stress(0, .5)


def curtains(x, y, w, h, u, col="#c96f4a"):
    """Шторы на окне: u 0 — задёрнуты, 1 — раздвинуты к краям."""
    o = []
    hw = w / 2
    for s_ in (-1, 1):
        inner = x + s_ * (hw * (1 - .85 * u)) * 0
        x_in = x + s_ * hw * .85 * u
        x_out = x + s_ * (hw + 40)
        a, b = sorted((x_in, x_out))
        pts = [(a, y - h - 30), (b, y - h - 30), (b + 10 * s_, y + 20), (a - 10 * s_, y + 20)]
        folds = "".join(line([(a + (b - a) * q, y - h), (a + (b - a) * q + 6, y)], 3, lib.mul(col, (.75, .75, .75)), taper=0, wmin=1,
                             seed=600 + j + (10 if s_ > 0 else 0)) for j, q in enumerate((.25, .5, .75)))
        o.append(shape(pts, col, folds, w=4, seed=610 + s_))
    o.append(rect(x - hw - 80, y - h - 50, x + hw + 80, y - h - 30, "#6e4a2c"))
    return "".join(o)


def bedroom(t, light=1.0, curt=1.0, sun=0.0, night=False):
    """Спальня: стена, окно со шторами, кровать, тумба у двери (дверь справа). light — день (1) / ночь (0)."""
    o = [rect(-1400, -1400, 2600, BFL, "#efe2c8")]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, BFL, WALL_SH, .55))
    o.append(rect(-1400, BFL, 2600, BFL + 1400, FLOOR_C))
    o.append(line([(-1400, BFL), (2600, BFL)], 5, seed=11))
    o.append(PR.window(WIN[0], WIN[1], 420, 520, mode="night" if night else ("day" if sun > .5 else "evening"), t=t, seed=3, curtain=False))
    o.append(curtains(WIN[0], WIN[1], 420, 520, curt))
    o.append(PR.door(DOORB[0], DOORB[1], 1.0, ajar=0.0, seed=2))
    o.append(shape(lib.rrect(NST[0] - 110, NST[1] - 300, NST[0] + 110, NST[1], 10), "#a8774a",
                   blob(lib.rect_pts(NST[0] - 110, NST[1] - 160, NST[0] + 110, NST[1] - 150), "#8a6038"), w=4, seed=620))
    o.append(PR.bed(*BED, seed=1))
    o.append(blob(ellipse_pts(560, BFL + 140, 520, 70, 30), "#b85c4a", .9))
    o.append(blob(ellipse_pts(560, BFL + 140, 440, 50, 30), "#d27a62", .9))
    return o


def overlay(t, night=0.0, sun=0.0):
    o = ""
    if night > 0:
        o += rect(-1400, -1400, 2600, 2900, "#1d2448", .5 * night)
    if sun > 0:
        o += PR.glow(WIN[0], WIN[1] - 260, 900, .55 * sun, "#fff1b0")
        o += f'<path d="M{WIN[0] - 210} {WIN[1] - 520} L{WIN[0] + 210} {WIN[1] - 520} L{WIN[0] + 700} {BFL + 300} L{WIN[0] - 500} {BFL + 300} Z" fill="#fff4c0" opacity="{.35 * sun:.3f}"/>'
    return o


def clock_on_stand(t, ring=0.0, press=0.0, x=None, y=None, size=110.0, hh=7, mm=0):
    x = NST[0] if x is None else x
    y = NST[1] - 300 - 72 * size / 200 if y is None else y
    return AL.alarm(x, y, size, hh=hh, mm=mm, ring=ring, t=t, press=press, uid=f"al{int(x)}") + AL.ring_marks(x, y, size, t, ring)


def in_bed(t, sit=0.0, expr="awake73", roll=0.0, cover="chest"):
    return people.dima_bed(BHIP[0], BHIP[1], .62, expr=expr, sit=sit, roll=roll, t=t, cover=cover, col="blue")


def frame_s01(t):
    o = bedroom(t)
    o.append(cat(PIL[0] - 60, MAT - 20, .45, t, dict(look=(.8, -.2), perk=1.0, tail=10 * math.sin(t * 3))))
    f = in_bed(t)
    o.append(f["svg"])
    o.append(clock_on_stand(t, ring=1.0))
    print(f["head"], f["pillow"])
    o.append(overlay(t))
    return view("".join(o), 600, 1020, 1.3, 0, t=t)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
