"""Общие помощники сцен рилсов-историй 111–116 (формат 4, по образцу s110.py): время из shots.json и voice/words.json,
надписи (хук, плашки, печатное жёлтое кодовое слово), камера, влёт хука (anim.hook_cam), комнаты, Дима стоя и за столом.
Подключение: from h4 import *  (common/ в sys.path; STORY — папка над common/)."""
import json
import math
import os
import sys

COMMON = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(COMMON)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(STORY)))
sys.path.insert(1, os.path.join(REPO, "scripts"))
import big_title  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import cat as CT  # noqa: E402
import props as PR  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
NOCAM = bool(os.environ.get("NOCAM"))
BG = "#efe2c8"
WALL, WALL_SH, FLOOR_C = "#efe2c8", "#e3d2b2", "#cdb48c"
RFL = 1560.0
PAPER = "#f6efdf"
RED, GREEN, BLUE = "#e2453a", "#3fb26a", "#2f8fe0"


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
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-size="{size:.1f}" text-anchor="{anchor}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw:.1f}" stroke-linejoin="round" paint-order="stroke"{o} '
            f'style="font-kerning:none">{s}</text>')


def plain(s, x, y, size, fill="#1d2448", anchor="start", op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="IDB" font-size="{size:.1f}" text-anchor="{anchor}" fill="{fill}"{o} '
            f'style="font-kerning:none">{s}</text>')


# ═════════════ экранные надписи ═════════════
def title(t):
    if NOCAM or "title" not in SH:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


def plate(t, spec, y=220.0, w=660.0, size=58.0):
    """Маленькая жёлтая плашка вверху кадра: выскакивает и тает."""
    if NOCAM or not spec:
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


def word_print(t, t0, x, y, size, word=None):
    """Кодовое слово печатными: жёлтый IDB с чёрной обводкой и тенью; буквы выскакивают по одной с t0 (по 0.07 с)."""
    word = word or SH["kot"]["text"]
    if t < t0:
        return ""
    o = []
    widths = [big_title.text_w(ch, size) for ch in word]
    tot = sum(widths)
    cx = x - tot / 2
    for j, ch in enumerate(word):
        u = clamp((t - t0 - .07 * j) / .2)
        if u > 0:
            s = lib.back_out(u, 2.6) if u < 1 else 1.0
            letter = (f'<text x="0" y="10" font-family="IDB" font-size="{size:.1f}" text-anchor="middle" fill="#000" opacity=".35" '
                      f'stroke="#000" stroke-width="{size * .12:.1f}" stroke-linejoin="round">{ch}</text>'
                      + text(ch, 0, 0, size, fill="#FFD23F", stroke="#111", sw=size * .11))
            o.append(f'<g transform="translate({cx + widths[j] / 2:.1f} {y:.1f}) rotate({-3 + 6 * (j % 2)}) scale({s:.4f})">{letter}</g>')
        cx += widths[j]
    return "".join(o)


def code_small(t):
    """Кодовое слово держится маленьким вверху слева до конца призыва (после плана-призыва)."""
    k = SH.get("kot")
    if NOCAM or not k:
        return ""
    if t < k["t_small"] or t > k["t_out"]:
        return ""
    size = k.get("small", 120)
    return word_print(t, -9.0, 60 + sum(big_title.text_w(c, size) for c in k["text"]) / 2, 330, size)


def over(t):
    return title(t) + plate(t, SH.get("label")) + plate(t, SH.get("label2"), w=SH.get("label2", {}).get("w", 560), size=70) + code_small(t)


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
            blur += (f'<use href="#hk4" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk4">{body}</g></g>{blur}'


def hook_view(body, t, hit, cx, cy, s, rot=0.0, bg=BG, dx=0.0, dy=0.0):
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, rot)}">{body}</g>'
    if NOCAM:
        return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>' + v)
    return lib.svg(hook_wrap(v, t, hit, bg) + over(t))


def loop_view(body, t, a, b, hit, cx, cy, s, bg=BG):
    """Петля: кадр хука, камера разгоняется к его первому кадру (zoom/rot hook_cam на 0 с)."""
    import anim
    hc = anim.hook_cam(0.0, hit=hit)
    u = ease_io(ramp(t, a, b - a))
    return view(body, cx, cy, s * (1 + (hc["zoom"] - 1) * u), hc["rot"] * u, bg=bg, t=t)


def cat(x, y, k, t, st=None):
    st = dict(dict(look=(-.4, -.2), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, st, t)


# ═════════════ комнаты и Дима ═════════════
def plain_room(t, wall=WALL, floor=FLOOR_C, x0=-1400.0, x1=2600.0, fl=RFL, stripes=True):
    o = [rect(x0, -1400, x1, fl, wall)]
    if stripes:
        for i in range(int(x0 // 120), int(x1 // 120) + 1):
            o.append(rect(i * 120, -1400, i * 120 + 46, fl, lib.mul(wall, (.96, .95, .93)), .55))
    o.append(rect(x0, fl - 46, x1, fl, "#d8c3a0"))
    o.append(line([(x0, fl - 46), (x1, fl - 46)], 3, seed=7))
    o.append(rect(x0, fl, x1, fl + 1400, floor))
    o.append(line([(x0, fl), (x1, fl)], 5, seed=11))
    return "".join(o)


def rug(x, y, w=520, col="#b85c4a", col2="#d27a62"):
    return blob(ellipse_pts(x, y, w, 70, 30), col, .9) + blob(ellipse_pts(x, y, w - 80, 50, 30), col2, .9)


def chair(x, y, k=1.0):
    o = [shape(lib.rrect(-100, -16, 110, 10, 6), "#a8774a", "", w=4, seed=1011)]
    o.append(shape([(-100, -16, 1), (-80, -16, 1), (-70, -330, 1), (-92, -330, 1)], "#a8774a", "", w=4, seed=1012))
    for s in (-1, 1):
        o.append(shape([(s * 80 - 9, 8, 1), (s * 80 + 9, 8, 1), (s * 86 + 9, 240, 1), (s * 86 - 9, 240, 1)], "#8a6038", "", w=3.4, seed=1013 + s))
    return tf("".join(o), x, y, k)


def mini_phone(x, y, k, rot=0.0, screen="#2f3a55", inner=""):
    o = [shape(lib.rrect(-72, -128, 72, 128, 22), "#2a2d36", "", w=4, seed=9700)]
    o.append(shape(lib.rrect(-60, -112, 60, 112, 12), screen, inner, w=2.4, seed=9701))
    return tf("".join(o), x, y, k, rot)


def stand(x, t, expr="proud82", pose="d82_rest", flip=False, k=.78, fl=RFL, **kw):
    hip = fl - (people.LEG_LEN - 12) * k - 6
    return people.dima82(x, hip, k, expr, pose, t=t, feet="stand", flip=flip, **kw)


FL = 1300.0
DESK_Y = FL - 300
DHIP = FL - 290


def desk_room(t, mode="day", sun=0.0, wall=WALL, window=True):
    o = [rect(-1400, -1400, 2600, FL, wall)]
    for i in range(-12, 22):
        o.append(rect(i * 120, -1400, i * 120 + 46, FL, lib.mul(wall, (.96, .95, .93)), .55))
    o.append(rect(-1400, FL, 2600, FL + 1400, FLOOR_C))
    o.append(line([(-1400, FL), (2600, FL)], 5, seed=11))
    if window:
        o.append(PR.window(150, 700, 300, 420, mode=mode, t=t, seed=3, curtain=False))
    if sun > 0:
        o.append(PR.glow(150, 500, 420, .35 * sun, "#fff1b0"))
    o.append(chair(320, FL - 240, 1.0))
    o.append(PR.desk(680, DESK_Y, w=660, depth=100, leg_h=260, seed=7))
    return o


def dima_desk(t, expr="calm82", pose="sit_desk", arms=None, hands=None, head_add=0.0, lean=.1, x=360):
    feet = people.sit_kw(x, DHIP, .5)["feet"]
    kw = {}
    if arms:
        kw["arms"] = arms
    if hands:
        kw["hands"] = hands
    return people.dima82(x, DHIP, .5, expr, pose, t=t, feet=feet, lean_add=lean, head_add=head_add, **kw)


def paper_bg():
    return rect(-2000, -2000, 3500, 4000, PAPER) + "".join(
        line([(-1200, 200 + 90 * j), (2600, 200 + 90 * j)], 2, "#e3d6bb", taper=0, wmin=1, seed=6000 + j) for j in range(24))


def cta_code(t, a, b, word=None, size=None):
    """План призыва: поле комментария, жёлтое кодовое слово крупно уже на первом кадре плана, Дима слева, кот прыгает к нему."""
    word = word or SH["kot"]["text"]
    size = size or min(300.0, 700.0 / max(1, len(word)) * 1.25)
    t_k = a - .45
    o = [paper_bg()]
    box = (f'<rect x="-460" y="-200" width="920" height="400" rx="40" fill="#ffffff" stroke="#111" stroke-width="7"/>'
           + f'<path d="M-260 196 l-40 90 l120 -90 z" fill="#ffffff" stroke="#111" stroke-width="7" stroke-linejoin="round"/>'
           + f'<rect x="-456" y="150" width="912" height="40" fill="#ffffff"/>'
           + plain("комментарий", -400, -130, 40, fill="#9aa0aa"))
    o.append(tf(box, 540, 590, 1.0, -1.5))
    o.append(PR.glow(540, 700, 460, .5, "#ffe9a8"))
    o.append(word_print(t, t_k, 540, 600 + size * .36, size, word))
    o.append(PR.sparkles(540, 600, 2.4, bump(t, a + .02, .05, .5), t, seed=91, n=6, r=400))
    k = .62
    hip = 1640 - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(330, hip, k, "proud82", "d82_one", t=t, feet="stand", head_add=.05 * math.sin(t * 3))
    o.append(f["svg"])
    j = ease_io(ramp(t, a + .15, .4))
    x = 1180 + (640 - 1180) * j
    y = 1640 - 260 * math.sin(math.pi * j)
    o.append(cat(x, y, .9, t, dict(look=(-.7, -.4), legs=1.0 - j if j < 1 else 0.0, smile=1.0 if j >= 1 else .4, tail=10 * math.sin(t * 3))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, a + .05, 8)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)
