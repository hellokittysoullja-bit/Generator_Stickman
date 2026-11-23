"""Рилс 109 «Книга», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу); числа в коде — длительности движений.
Говорит Дима от первого лица (имя не звучит и не пишется). Сквозное место: стол с раскрытой книгой, телефоном и котом (хук, боли,
решение, итог, петля); дверь в другую комнату; бумажка с вопросом; ужин с другом.
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
    if t < T1("s14") - .01 or t > k["t_out"]:
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
            blur += (f'<use href="#hk109" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk109">{body}</g></g>{blur}'


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


def frame_s01(t):
    """ХУК: стол, книга открыта, Дима читает; телефон рядом вибрирует и ползёт к его руке."""
    o = table(t)
    o.append(reader(t)["svg"])
    o.append(book(t))
    o.append(phone_desk(*phone_crawl(t), .5, -10 + 14 * ramp(t, -.2, 1.6), buzz=1.0, t=t, glow_=.8))
    o.append(cat(CATD[0], CATD[1], .5, t, dict(look=(-.8, .3), perk=1.0, tail=10 * math.sin(t * 3))))
    dx, dy = shake(t, HIT01, 10)
    v = f'<g transform="{lib.cam(600 + dx, 820 + dy, 1.8, 0)}">{"".join(o)}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{BG}"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + over(t))


def phone_fall(t, ta, x0, y0):
    """Телефон слетает со стола вправо за край и падает (с ta)."""
    u = clamp((t - ta) / .5)
    x = x0 + 420 * u
    y = y0 - 160 * math.sin(math.pi * min(u, .5)) + 900 * max(0.0, u - .35) ** 2 * 3
    return phone_desk(x, y, .5, -10 + 420 * u, t=t)


def frame_s02(t):
    """«часу без телефона»: кот на столе тянет лапу и смахивает телефон за край; Дима читает дальше, кот довольный."""
    a, b = T0("s02"), T1("s02")
    ta = W(6) - .05
    o = table(t)
    o.append(reader(t)["svg"])
    o.append(book(t))
    px, py = phone_crawl(t)
    if t < ta:
        o.append(phone_desk(px, py, .5, 4, buzz=1.0, t=t, glow_=.8))
    else:
        o.append(phone_fall(t, ta, px, py))
    reach = ease_io(ramp(t, a, ta - a)) * (1 - ease_io(ramp(t, ta + .15, .3)))
    o.append(cat(CATD[0], CATD[1], .5, t, dict(look=(-.9, .4), paw_l=reach, paw_l_dx=70 + 190 * reach, smile=ramp(t, ta + .2, .2),
                                              perk=1.0, tail=14 * math.sin(t * 5))))
    o.append(PR.speed_arcs(px + 120, py - 60, .8, bump(t, ta, .05, .3), t, seed=5, n=3, ang=0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(7), 12)
    return view("".join(o), 610 + dx, 820 + dy, 1.6 + .1 * u, -1 + 2 * u, t=t)


def frame_s03(t):
    """«А раньше брал его через минуту»: Дима отрывается от книги, рука хватает телефон со стола; таймер «0:58»."""
    a, b = T0("s03"), T1("s03")
    tg = W(10)
    g = ease_io(ramp(t, tg - .3, .3))
    lift = ease_io(ramp(t, tg + .05, .4))
    hp = (PHN[0] - 60, PHN[1] - 20)
    tgt = (hp[0] - 120 * lift, hp[1] - 160 * lift)
    probe = reader(t)
    arms = {"f": ("ang", 0.16, 0.16), "n": ("ik", tgt, 1)} if g > 0 else None
    e = dict(people.EXPR["dima"]["rush82"]); e["look"] = (.8, .5)
    o = table(t)
    f = dima_desk(t, e if g > .3 else dict(people.EXPR["dima"]["focus"], look=(.7, .75), bags=False), head_add=.12 - .1 * g, lean=.16,
                  arms={"f": ("ang", 0.16, 0.16), "n": ("ik", (probe["wrist"]["n"][0] + (tgt[0] - probe["wrist"]["n"][0]) * g,
                                                                probe["wrist"]["n"][1] + (tgt[1] - probe["wrist"]["n"][1]) * g), 1)} if arms else None)
    o.append(book(t))
    o.append(f["svg"])
    o.append(phone_desk(tgt[0] + 40 if g >= 1 else PHN[0], tgt[1] + 20 if g >= 1 else PHN[1], .5, 10 - 30 * lift, t=t, glow_=.8))
    o.append(day_timer(790, 520, .5 * pop(t, W(12) - .1, .25), 58 / 60, t, label="0:58"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tg, 9)
    return view("".join(o), 580 + dx, 800 + dy, 1.5 + .1 * u, 0, t=t)


def blur_def(sd):
    fid = f"bl{int(sd * 100)}"
    lib.DEFS[fid] = f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="{sd:.2f}"/></filter>'
    return fid


def frame_s04(t):
    """«терял нить на каждой странице»: книга крупно на бумаге, строки плывут и расплываются; на «странице» знак «?»; Дима сбоку щурится."""
    a, b = T0("s04"), T1("s04")
    bl = 7 * ease_io(ramp(t, W(15), .6))
    o = [paper_bg()]
    bk = PR.book_open(690, 1300, 3.2, seed=1)
    wob = 10 * ramp(t, W(15), .4) * math.sin(t * 7)
    if bl > .3:
        bk = f'<g {lib.blur(round(bl, 1))} transform="translate({wob:.1f} 0)">{bk}</g>'
    o.append(bk)
    o.append(PR.question_mark(860, 640, 2.4 * pop(t, W(18), .25), 1.0, col="#e2453a"))
    k = .8
    hip = 1880 - (people.LEG_LEN - 12) * k
    sq = dict(people.EXPR["dima"]["squint82"]); sq["look"] = (.6, .4)
    f = people.dima82(140, hip, k, sq if t < W(18) else "puzzled82", "d82_shrug" if t > W(18) else "d82_rest", t=t, feet="stand",
                      head_add=-.08)
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(18), 8)
    return view("".join(o), 540 + dx, 1060 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)


def frame_s05(t):
    """«а к ночи не помнил, что читал»: ночь, лампа погасла, книга закрыта; Дима за столом смотрит в пустоту, над ним пустое облачко."""
    a, b = T0("s05"), T1("s05")
    o = desk_room(t, mode="night")
    o.append(PR.lamp_desk(1060, DESK_Y - 70, 1.1, on=0.0, tilt=-10, seed=1))
    o.append(rect(-1400, -1400, 2600, 2700, "#1d2448", .45))
    o.append(PR.glow(1060, DESK_Y - 200, 300, .25, "#8fb7ff"))
    e = dict(people.EXPR["dima"]["puzzled82"]); e["look"] = (.3, -.8)
    f = dima_desk(t, e, head_add=-.1, lean=.05)
    o.append(f["svg"])
    o.append(PR.book_closed(600, DESK_Y - 40, 1.0, rot=-4))
    hx, hy = f["head"]
    cu = pop(t, W(22) - .1, .3)
    o.append(PR.thought_cloud(hx + 170, hy - 240, 1.3, u=cu, seed=2, dots=1))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(23), 6)
    return view("".join(o), 580 + dx, 820 + dy, 1.55 + .1 * u, 0, bg="#1d2448", t=t)


def frame_s06(t):
    """«Вот что я поменял»: Дима за столом поднимает палец, над ним лампочка; кот на столе; надпись сверху."""
    a, b = T0("s06"), T1("s06")
    t_idea = W(26) + .15
    o = table(t)
    o.append(book(t))
    f = dima_desk(t, "wow82" if t > t_idea else "sure82", pose="d82_one", head_add=.06 * bump(t, t_idea, .08, .3), lean=0.0)
    o.append(f["svg"])
    hx, hy = f["head"]
    if t > t_idea:
        o.append(PR.glow(hx + 60, hy - 230, 200, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx + 60, hy - 230 + 8 * math.sin(t * 5), 1.0 * pop(t, t_idea, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx + 60, hy - 230, 1.6, bump(t, t_idea, .05, .5), t, seed=41, n=5, r=180))
    o.append(phone_desk(PHN[0], PHN[1], .5, 6, t=t))
    o.append(cat(CATD[0], CATD[1], .5, t, dict(look=(-.8, -.3), smile=.8, perk=1.0, tail=12 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_idea, 9)
    return view("".join(o), 580 + dx, 800 + dy, 1.45 + .08 * u, -1 + 2 * u, t=t)


DOOR = (820.0, RFL)


def frame_s07(t):
    """«Телефон уходит в другую комнату»: Дима у двери в тёмную комнату, телефон из руки улетает внутрь на тумбочку, дверь закрывается."""
    a, b = T0("s07"), T1("s07")
    t_th, t_cl = W(31), W(34) - .15
    o = [plain_room(t)]
    o.append(rect(DOOR[0] - 210, DOOR[1] - 936, DOOR[0] + 210, DOOR[1], "#3b3552"))
    o.append(shape(lib.rrect(DOOR[0] - 120, DOOR[1] - 240, DOOR[0] + 120, DOOR[1], 10), "#6e4a2c", "", w=4, seed=77))
    u = clamp((t - t_th) / .45)
    if u <= 0:
        pass
    ajar = 1.0 - ease_io(ramp(t, t_cl, .3))
    o.append(PR.door(DOOR[0], DOOR[1], 1.0, ajar=ajar, seed=1))
    k = .72
    hip = RFL - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(380, hip, k, "proud82" if t > t_cl else "sure82", "d82_hold" if t < t_th else "d82_one", t=t, feet="stand",
                      head_add=.04 * math.sin(t * 3))
    o.append(f["svg"])
    hx0, hy0 = f["hold"]
    if t < t_th:
        o.append(phone_desk(hx0, hy0, .45, -20, t=t))
    elif ajar > .15 or u < 1:
        x = hx0 + (DOOR[0] - hx0 + 20) * u
        y = hy0 + (DOOR[1] - 270 - hy0) * u - 260 * math.sin(math.pi * u)
        o.append(phone_desk(x, y, .45 - .1 * u, -20 + 380 * u, t=t))
    if t > t_cl + .3:
        o.append(PR.sparkles(DOOR[0], DOOR[1] - 600, 1.6, bump(t, t_cl + .3, .05, .5), t, seed=51, n=5, r=200))
    o.append(cat(140, RFL, .7, t, dict(look=(.8, -.4), perk=1.0, smile=.6, tail=12 * math.sin(t * 3))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, t_cl + .3, 8)
    return view("".join(o), 560 + dx, 1060 + dy, 1.05 + .06 * uu, 0, t=t)


def note(x, y, k=1.0, rot=0.0, q=1.0):
    o = PR.paper(0, 0, 1.0, 0, w=150, h=110, seed=4, kind="blank", col="#fffbe8")
    o += PR.question_mark(0, 0, .55, q, col="#e2453a")
    return tf(o, x, y, k, rot)


def frame_s08(t):
    """«а на стол ложится бумажка с одним вопросом»: стол крупно, книга; сверху слетает бумажка и ложится рядом, на ней «?»."""
    a, b = T0("s08"), T1("s08")
    tl = W(39) + .1
    o = table(t)
    o.append(reader(t, expr=dict(people.EXPR["dima"]["calm82"], look=(.8, .4)))["svg"])
    o.append(book(t))
    u = clamp((t - (tl - .8)) / .8)
    x = PHN[0] + 30 + 60 * math.sin(u * 6) * (1 - u)
    y = PHN[1] - 20 - 600 * (1 - ease_out(u))
    o.append(note(x, y, 1.0, -8 + 25 * math.sin(u * 5) * (1 - u), q=ramp(t, W(41), .4)))
    if t > tl:
        o.append(PR.dust_puff(PHN[0] + 30, PHN[1] - 10, .6, ramp(t, tl, .4), seed=2))
    o.append(cat(CATD[0], CATD[1], .5, t, dict(look=(-.9, .2 if t > tl else -.6), perk=1.0, tail=10 * math.sin(t * 3))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tl, 7)
    return view("".join(o), 610 + dx, 820 + dy, 1.55 + .1 * uu, 0, t=t)


def frame_s09(t):
    """«о чём эта глава?»: бумажка крупно, вопрос дописывается от руки по словам; ручка рядом."""
    a, b = T0("s09"), T1("s09")
    o = [paper_bg()]
    o.append(blob(lib.rrect(170 + 18, 560 + 22, 910 + 18, 1240 + 22, 26), "#000000", .15))
    o.append(shape(lib.rrect(170, 560, 910, 1240, 26), "#fffbe8", "".join(
        line([(220, 700 + 110 * j), (860, 700 + 110 * j)], 2, "#d9cfb4", taper=0, wmin=1, seed=900 + j) for j in range(5)), w=6, seed=901))
    words = [("О ЧЁМ", 43), ("ЭТА", 45), ("ГЛАВА?", 46)]
    ys = [790, 930, 1090]
    last = (540, 760)
    for j, (w_, wi) in enumerate(words):
        u = ramp(t, max(a, W(wi) - .05), .25)
        if u <= 0:
            continue
        cid = lib.clip_rect(160, ys[j] - 130, 760 * u, 170)
        o.append(f'<g clip-path="url(#{cid})">{plain(w_, 540, ys[j], 130 if j < 2 else 150, fill="#2f4f86", anchor="middle")}</g>')
        last = (160 + 760 * u, ys[j] - 20)
    o.append(PR.pen(last[0] + 30, last[1] - 60, 1.4, -30))
    o.append(cat(870, 1700, .8, t, dict(look=(-.6, -.8), perk=1.0, smile=.6, tail=12 * math.sin(t * 3))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(46), 7)
    return view("".join(o), 540 + dx, 1060 + dy, 1.0 + .06 * uu, -1 + 2 * uu, bg=PAPER, t=t)


def mmss(sec):
    sec = max(0, int(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def frame_s10(t):
    """«Первые две минуты тянет проверить»: таймер 0:00 → 2:00; Дима читает, ближняя рука дёргается к пустому месту, где лежал телефон."""
    a, b = T0("s10"), T1("s10")
    sec = 120 * clamp((t - a) / (W(52) - .1 - a))
    o = table(t)
    o.append(book(t))
    o.append(note(PHN[0] + 160, PHN[1] - 10, .7, -6))
    gx, gy = PHN[0] - 20, PHN[1] - 10
    o.append(f'<rect x="{gx - 60}" y="{gy - 26}" width="120" height="52" rx="12" fill="none" stroke="#8a6038" stroke-width="5" '
             f'stroke-dasharray="14 10" opacity=".8"/>')
    probe = reader(t)
    wx, wy = probe["wrist"]["n"]
    tw = max(0.0, math.sin((t - a) * 5.5)) ** 3 * (1 - ramp(t, W(51), .3))
    tgt = (wx + (gx - 40 - wx) * .8 * tw, wy + (gy - 20 - wy) * .8 * tw)
    e = dict(people.EXPR["dima"]["squint82"]); e["look"] = (.8, .5)
    f = dima_desk(t, e if tw > .3 else dict(people.EXPR["dima"]["focus"], look=(.7, .75), bags=False), head_add=.12, lean=.16,
                  arms={"f": ("ang", 0.16, 0.16), "n": ("ik", tgt, 1)})
    o.append(f["svg"])
    o.append(day_timer(800, 500, .5, sec / 120 * 2 / 60, t, label=mmss(sec)))
    o.append(cat(CATD[0] + 40, CATD[1], .45, t, dict(look=(-.9, .3), perk=1.0, tail=10 * math.sin(t * 3))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(50), 6)
    return view("".join(o), 580 + dx, 780 + dy, 1.5 + .08 * uu, 0, t=t)


def frame_s11(t):
    """«На третьей я уже читаю»: 3:00, Дима погружён в книгу, тёплый свет, искры; кот жмурится."""
    a, b = T0("s11"), T1("s11")
    sec = 120 + 60 * clamp((t - a) / (W(54) - a))
    o = table(t, lamp=1.0)
    w = ramp(t, a, .5)
    o.append(PR.glow(560, DESK_Y - 200, 520, .45 * w, "#ffd98a"))
    o.append(book(t, flip=clamp((t - W(55)) / .5)))
    f = reader(t, expr=dict(people.EXPR["dima"]["calm82"], look=(.7, .75)))
    o.append(f["svg"])
    o.append(PR.sparkles(560, DESK_Y - 200, 1.6, bump(t, W(56), .05, .6), t, seed=61, n=6, r=200))
    o.append(day_timer(800, 500, .5, sec / 3600, t, label=mmss(sec)))
    o.append(cat(CATD[0] + 40, CATD[1], .45, t, dict(look=(-.9, .3), squint=1.0, smile=1.0, tail=8 * math.sin(t * 2))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(56), 5)
    return view("".join(o), 580 + 20 * uu + dx, 790 + dy, 1.65 - .1 * uu, 0, t=t)


def frame_s12(t):
    """«А кот ложится на книгу»: Дима привстаёт, кот прыгает со стола и плюхается клубком на раскрытую книгу."""
    a, b = T0("s12"), T1("s12")
    up = ease_out(ramp(t, a - .1, .35))
    tj = W(59) - .1
    tl = W(61)
    o = table(t)
    o.append(book(t))
    f = people.dima82(360, DHIP - 120 * up, .5, "panic82" if t > tl else "sure82", "d82_rest", t=t,
                      feet=people.sit_kw(360, DHIP, .5)["feet"], lean_add=-.05 * up, head_add=.05 * bump(t, tl, .05, .3))
    o.append(f["svg"])
    j = ease_io(ramp(t, tj, tl - tj))
    if t < tl:
        x = CATD[0] + (BOOK[0] - CATD[0]) * j
        y = CATD[1] - 260 * math.sin(math.pi * j) + (BOOK[1] - CATD[1]) * j
        o.append(cat(x, y, .5, t, dict(look=(-.9, .2), legs=1.0 if 0 < j < 1 else 0.0, perk=1.0, tail=16 * math.sin(t * 6))))
    else:
        sq = 1 - .15 * bump(t, tl, .04, .2)
        o.append(f'<g transform="translate({BOOK[0]} {BOOK[1]}) scale({1 / sq:.3f} {sq:.3f}) translate({-BOOK[0]} {-BOOK[1]})">'
                 + CT.curl(BOOK[0] - 10, BOOK[1] + 6, .42, dict(eye=.6, look=(-.6, -.3)), t) + '</g>')
        o.append(PR.dust_puff(BOOK[0], BOOK[1], .7, ramp(t, tl, .45), seed=3))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tl, 11)
    return view("".join(o), 580 + dx, 800 + dy, 1.5 + .1 * uu, 0, t=t)


def frame_s13(t):
    """«если я встаю раньше времени»: Дима садится обратно и смеётся; кот лежит на книге клубком и мурчит; таймер идёт."""
    a, b = T0("s13"), T1("s13")
    down = ease_io(ramp(t, a, .4))
    o = table(t)
    o.append(book(t))
    f = people.dima82(360, DHIP - 120 * (1 - down), .5, "laugh82" if t > W(65) else "sure82", "d82_shrug", t=t,
                      feet=people.sit_kw(360, DHIP, .5)["feet"], head_add=.05 * math.sin(t * 6))
    o.append(f["svg"])
    o.append(CT.curl(BOOK[0] - 10, BOOK[1] + 6, .42, dict(eye=.4 + .4 * math.sin(t * 2) ** 2, look=(-.6, -.3)), t))
    o.append(PR.purr(BOOK[0] + 60, BOOK[1] - 150, .8, t, 1.0, seed=1))
    o.append(day_timer(800, 500, .5, 23 / 60, t, label="23:00"))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(65), 6)
    return view("".join(o), 580 + dx, 800 + dy, 1.5 + .1 * uu, 1 - 2 * uu, t=t)
def frame_s14(t):
    """«Напиши «КОТ»»: поле комментария, крупно печатается жёлтое «КОТ»; Дима внизу слева, кот прыгает и садится рядом с ним."""
    a, b = T0("s14"), T1("s14")
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


def frame_s15(t):
    """«чтобы тоже читать по часу»: Дима читает, кот сидит рядом на столе; круг часа заполняется до «60 мин»."""
    a, b = T0("s15"), T1("s15")
    u = ease_io(ramp(t, a + .1, W(74) + .2 - a))
    o = table(t)
    o.append(PR.glow(560, DESK_Y - 200, 480, .35, "#ffd98a"))
    o.append(book(t, flip=clamp((t - W(72)) / .5)))
    o.append(reader(t, expr=dict(people.EXPR["dima"]["calm82"], look=(.7, .75)))["svg"])
    o.append(cat(CATD[0], CATD[1], .5, t, dict(look=(-.9, .4), smile=.8, tail=10 * math.sin(t * 3))))
    o.append(day_timer(800, 500, .5 * (1 + .08 * bump(t, W(74), .05, .3)), u, t, label=f"{int(60 * u)} мин"))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(74), 6)
    return view("".join(o), 580 + dx, 800 + dy, 1.45 + .08 * uu, 0, t=t)


def frame_s16(t):
    """«и помнить, что прочитал»: Дима откинулся и улыбается, над ним облачко: книга и галочка; кот кивает."""
    a, b = T0("s16"), T1("s16")
    o = table(t)
    o.append(book(t))
    f = dima_desk(t, dict(people.EXPR["dima"]["proud82"], look=(.4, -.6)), head_add=-.08, lean=0.0)
    o.append(f["svg"])
    hx, hy = f["head"]
    cu = pop(t, W(76) - .1, .3)
    inner = PR.book_open(-40, 40, .5, seed=2) + PR.check_mark(80, 0, .9, ramp(t, W(77), .3)) if cu > .3 else ""
    o.append(PR.thought_cloud(hx + 180, hy - 230, 1.3, u=cu, seed=2, dots=1, inner=inner))
    o.append(PR.sparkles(hx + 180, hy - 230, 1.6, bump(t, W(78), .05, .5), t, seed=71, n=5, r=200))
    o.append(cat(CATD[0], CATD[1], .5, t, dict(look=(-.8, -.6), smile=1.0, tail=12 * math.sin(t * 4))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(76), 7)
    return view("".join(o), 580 + dx, 780 + dy, 1.45 + .08 * uu, 1 - 2 * uu, t=t)


def bookmark_book(x, y, k, rot=0.0):
    o = PR.book_closed(x, y, k, rot=rot)
    o += shape([(x + 20 * k, y - 30 * k), (x + 44 * k, y - 30 * k), (x + 44 * k, y + 40 * k), (x + 32 * k, y + 28 * k), (x + 20 * k, y + 40 * k)],
               "#e2453a", "", w=3, seed=990)
    return o


def frame_s17(t):
    """«Вчера дочитал главу»: Дима захлопывает книгу, из неё торчит закладка; искры; надпись «ДОЧИТАЛ»."""
    a, b = T0("s17"), T1("s17")
    tc = W(80) + .15
    o = table(t)
    if t < tc:
        o.append(book(t, flip=clamp((t - a) / (tc - a))))
    else:
        o.append(bookmark_book(BOOK[0], BOOK[1] - 10, 1.5 + .15 * bump(t, tc, .04, .2), rot=-3))
        o.append(PR.dust_puff(BOOK[0], BOOK[1], .6, ramp(t, tc, .4), seed=4))
        o.append(PR.sparkles(BOOK[0], BOOK[1] - 140, 1.8, bump(t, tc + .05, .05, .6), t, seed=81, n=6, r=200))
    f = dima_desk(t, "proud82" if t > tc else dict(people.EXPR["dima"]["focus"], look=(.7, .75), bags=False), head_add=.05, lean=.05)
    o.append(f["svg"])
    o.append(cat(CATD[0], CATD[1], .5, t, dict(look=(-.8, .2), smile=1.0 if t > tc else .3, perk=1.0, tail=14 * math.sin(t * 5))))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tc, 10)
    return view("".join(o), 580 + dx, 820 + dy, 1.55 + .1 * uu, 0, t=t)


def frame_s18(t):
    """«и пересказал её другу за ужином»: кухонный стол, тарелки; Дима увлечённо рассказывает с жестом, у друга удивлённое лицо;
    на столе книга с закладкой."""
    a, b = T0("s18"), T1("s18")
    o = [plain_room(t, wall="#f3dcc0")]
    o.append(PR.window(540, 900, 360, 420, mode="evening", t=t, seed=5, curtain=False))
    o.append(PR.glow(540, 700, 420, .3, "#ffd98a"))
    ty = RFL - 330
    k = .62
    hip_d = ty + 20
    fd = people.dima82(250, hip_d, k, "laugh82" if math.sin(t * 7) > -.2 else "wow82", "d82_shrug" if (t - a) % .9 < .45 else "d82_one", t=t,
                       feet=people.sit_kw(250, hip_d, k)["feet"], head_add=.05 * math.sin(t * 8), lean_add=.06)
    e = {"brows": "up", "mouth": "o", "open": .6, "lid": 1.0, "look": (-.6, -.1)}
    ff = people.figure("beard", 830, hip_d, k, expr=e, feet=people.sit_kw(830, hip_d, k, "beard")["feet"], flip=True,
                       head_ang=-.05 + .03 * math.sin(t * 3))
    o.append(PR.stool(250, hip_d + 40, .62, seed=1) + PR.stool(830, hip_d + 40, .62, seed=2))
    o.append(fd["svg"])
    o.append(ff["svg"])
    o.append(PR.desk(540, ty, w=560, depth=90, leg_h=320, seed=9))
    o.append(PR.plate_soup(420, ty - 40, .55, steam=1.0, t=t, seed=1))
    o.append(PR.plate_soup(660, ty - 40, .55, steam=1.0, t=t, seed=2))
    o.append(bookmark_book(540, ty - 30, .7, rot=-5))
    hx, hy = ff["head"]
    if t > W(85) - .1:
        o.append(PR.sparkles(hx, hy - 180, 1.4, bump(t, W(85), .05, .5), t, seed=91, n=5, r=160))
    dhx, dhy = fd["head"]
    o.append(PR.speech_bubble(dhx + 150, dhy - 230, 230, 150, u=pop(t, a + .1, .3), seed=3, tail=(-70, 70)))
    if t > a + .3:
        o.append(PR.book_open(dhx + 150, dhy - 200, .6, seed=2))
    o.append(cat(560, RFL + 10, .55, t, dict(look=(.6, -.6), smile=1.0, tail=12 * math.sin(t * 3))))
    if t > W(85) - .1:
        o.append(text("!", hx + 40, hy - 170, 150 * pop(t, W(85) - .1, .25), fill="#e2453a", stroke="#111", sw=8))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(85), 8)
    return view("".join(o), 540 + dx, 1100 + dy, 1.1 + .08 * uu, 0, t=t)


def frame_s19(t):
    """Петля: кадр хука — стол, книга, телефон снова начинает вибрировать."""
    a, b = T0("s19"), T1("s19")
    import anim
    hc = anim.hook_cam(0.0, hit=HIT01)
    u = ease_io(ramp(t, a, b - a))
    tt = -.2 + (t - a) * .3
    o = table(t)
    o.append(reader(t)["svg"])
    o.append(book(t))
    o.append(phone_desk(*phone_crawl(tt), .5, -10, buzz=ramp(t, a + .1, .3), t=t, glow_=.8))
    o.append(cat(CATD[0], CATD[1], .5, t, dict(look=(-.8, .3), perk=1.0, tail=10 * math.sin(t * 3))))
    s = 1.8 * (1 + (hc["zoom"] - 1) * u)
    return view("".join(o), 600, 820, s, hc["rot"] * u, t=t)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
