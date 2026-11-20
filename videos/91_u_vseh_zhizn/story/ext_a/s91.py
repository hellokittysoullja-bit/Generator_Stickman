"""Рилс 91 «У всех жизнь, а у тебя?», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — общее время ролика.
Время — только из shots.json (t0/t1) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
Галерея идеальных фото в золотых рамках (море с пальмами, свадьба, блестящая машина, улыбка); у Димы — кривые дешёвые
рамки (лапша, конверт-счёт, тесная комната). Главный приём — кот лапой переворачивает рамку по оси Y (ширина до нуля,
разворот, тень на стене), на обороте настоящее. Хук s01 — влёт правил 28–29 (anim.hook_cam) за бегущим Димой; s18 —
петля тем же ракурсом (Дима идёт спокойно, рамки перевёрнуты оборотом).
NOCAM=1 — без влёта, тряски и заголовка (замер движения рисунка); MASK=1 — только рисунок хука белым на чёрном."""
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
import room  # noqa: E402
import cat as CT  # noqa: E402
import props as PR  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
NOCAM = bool(os.environ.get("NOCAM"))
MASK = bool(os.environ.get("MASK"))


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
    u = t - a
    if u <= 0:
        return 0.0
    return min(1.0, u / up) * (math.exp(-(u - up) / down) if u > up else 1.0)


def shake(t, a, amp=10.0, dur=.35, f=11.0):
    u = t - a
    if u <= 0 or u > dur * 3:
        return 0.0, 0.0
    e = math.exp(-u / dur * 2.5)
    return amp * e * math.sin(2 * math.pi * f * u), amp * .6 * e * math.cos(2 * math.pi * f * .8 * u)


def pop(t, a, d=.24):
    """0 → перелёт → 1."""
    u = clamp((t - a) / d)
    return lib.back_out(u, 2.2) if u < 1 else 1.0


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def tf(inner, x, y, k=1.0, rot=0.0):
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({k:.4f})">{inner}</g>'


def title(t):
    if NOCAM or MASK:
        return ""
    hits = [W(i) for i in SH["title"]["hits"]]
    return big_title.layer(t, text=SH["title"]["text"], t_in=SH["title"]["t_in"], t_out=SH["title"]["t_out"], hits=hits)


def view(body, cx, cy, s, rot=0.0, over="", bg="#e9dcc4"):
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


# ═════════════════════════ люди ═════════════════════════
def with_pal(who, over, fn):
    p0 = people.PAL[who]
    people.PAL[who] = dict(p0, **over)
    try:
        return fn()
    finally:
        people.PAL[who] = p0


def ex_(**kw):
    d = {"brows": "calm", "mouth": "smile", "smile": .5, "lid": .8, "look": (0, 0), "bags": False}
    d.update(kw)
    return d


ARMS0 = {"f": ("ang", 0.18, 0.18), "n": ("ang", -0.1, 0.25)}


def waist(who, x, y, k, ex, arms=None, hands=None, flip=False, lean=0.0, head_ang=0.0, pal=None, layers=None):
    """Человек по пояс; (x, y) — таз. -> figure dict."""
    arms = dict(ARMS0, **(arms or {}))
    def go():
        return people.figure(who, x, y, k, ex, lean=lean, head_ang=head_ang, arms=arms, hands=hands, flip=flip, layers=layers)
    return with_pal(who, pal, go) if pal else go()


def standing(who, x, ground, k, ex, arms=None, hands=None, flip=False, lean=0.0, head_ang=0.0, pal=None, layers=None):
    arms = dict(ARMS0, **(arms or {}))
    sc = k * people.HEIGHT.get(who, 1.0)
    y = ground - (people.LEG_LEN - 12) * sc - 6

    def go():
        return people.figure(who, x, y, k, ex, lean=lean, head_ang=head_ang, arms=arms, hands=hands, flip=flip,
                             feet=people.stand_kw(x, y, k, who)["feet"], layers=layers)
    return with_pal(who, pal, go) if pal else go()


def dima_hip(ground, k):
    return ground - (people.LEG_LEN - 12) * k - 6


def phone(x, y, k=1.0, rot=0.0, glow=1.0):
    o = shape(lib.rrect(-34, -62, 34, 62, 12), "#2b2e38", "", w=4, seed=9101)
    o += blob(lib.rrect(-26, -52, 26, 50, 6), lib.mix("#5b6378", "#bfe3ff", glow))
    return tf(o, x, y, k, rot)


# ═════════════════════════ рамка и переворот ═════════════════════════
PW, PH = 600.0, 440.0
GOLD, GOLD_SH, GOLD_HI = "#d8a636", "#a8761c", "#f8dc82"
WOOD, WOOD_SH, WOOD_HI = "#9a7650", "#6e5134", "#b8956a"
BACK, BACK_SH = "#c49a66", "#9a7244"


_BOR = {}


def border(style, w, h, seed=0):
    """Багет через <use>: одна резьба на кадр для всех одинаковых рамок."""
    key = (style, round(w), round(h), seed)
    if key not in _BOR:
        n0 = len(lib.DEFS)
        sv, b = _border(style, w, h, seed)
        gid = lib.uid("bor")
        _BOR[key] = (f'<use href="#{gid}"/>', b, lib.DEFS[n0:] + [f'<g id="{gid}">{sv}</g>'])
        del lib.DEFS[n0:]
    u, b, defs = _BOR[key]
    if defs[-1] not in lib.DEFS:
        lib.DEFS.extend(defs)
    return u, b


def _border(style, w, h, seed=0):
    """Багет вокруг поля w×h (центр 0, 0): gold — резной золотой, cheap — тонкий кривой деревянный, back — оборот (картон)."""
    if style == "gold":
        b = 44
        o = shape(lib.rrect(-w / 2 - b, -h / 2 - b, w / 2 + b, h / 2 + b, 8), GOLD,
                  blob([(w / 2 + b, -h / 2 - b), (w / 2 + b, h / 2 + b), (-w / 2 - b, h / 2 + b), (-w / 2, h / 2), (w / 2, h / 2), (w / 2, -h / 2)],
                       GOLD_SH, .75)
                  + line([(-w / 2 - b + 12, h / 2), (-w / 2 - b + 12, -h / 2 - b + 12), (w / 2, -h / 2 - b + 12)], 6, GOLD_HI, seed=seed + 1, op=.9),
                  w=5.5, seed=9200 + seed)
        o += shape(lib.rrect(-w / 2 - 14, -h / 2 - 14, w / 2 + 14, h / 2 + 14, 3), GOLD_SH, "", w=3.2, seed=9201 + seed)
        for cx_, cy_ in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            x, y = cx_ * (w / 2 + b / 2), cy_ * (h / 2 + b / 2)
            o += shape(ellipse_pts(x, y, 16, 16, 12), GOLD_HI, blob(ellipse_pts(x + 4, y + 4, 8, 8, 10), GOLD_SH, .8), w=3, seed=9210 + seed)
        for j in range(5):                                  # резьба: завитки по верху и низу
            xx = -w / 2 + (j + .5) * w / 5
            for yy in (-h / 2 - b / 2, h / 2 + b / 2):
                o += line([(xx - 22, yy + 4), (xx - 8, yy - 8), (xx + 8, yy + 6), (xx + 22, yy - 4)], 3, GOLD_SH, seed=9220 + seed + j, op=.85)
        return o, b
    if style == "back":
        b = 26
        o = shape(lib.rrect(-w / 2 - b, -h / 2 - b, w / 2 + b, h / 2 + b, 4), WOOD_SH, "", w=5, seed=9230 + seed)
        return o, b
    b = 22
    o = shape([(-w / 2 - b - 4, -h / 2 - b + 3, 1), (w / 2 + b, -h / 2 - b - 4, 1), (w / 2 + b + 3, h / 2 + b, 1), (-w / 2 - b, h / 2 + b + 4, 1)], WOOD,
              blob([(w / 2, -h / 2), (w / 2 + b + 3, -h / 2 - b), (w / 2 + b + 3, h / 2 + b), (w / 2, h / 2)], WOOD_SH, .8)
              + line([(-w / 2 - b + 6, -h / 2), (-w / 2 - b + 8, h / 2)], 3, WOOD_HI, seed=seed + 7), w=5, seed=9240 + seed)
    o += line([(w / 2 + b - 4, -h / 2 - b + 8), (w / 2 + b - 30, -h / 2 + 30)], 3, INK, seed=9245 + seed, op=.6)       # трещина в углу
    return o, b


_PIC = {}


def picture(fn, t, w, h):
    """Содержимое рамки; картинка «на восьмёрках» (8 раз в секунду) и кэш — одна и та же фотография в десятке рамок
    считается один раз (defs, что она добавила, возвращаются в lib.DEFS при каждом попадании)."""
    if fn.__name__ == "<lambda>":
        return _picture(fn, t, w, h)
    key = (fn.__name__, round(w), round(h), int(t * 8))
    if key not in _PIC:
        n0 = len(lib.DEFS)
        sv = _picture(fn, int(t * 8) / 8, w, h)
        gid = lib.uid("pic")
        _PIC[key] = (f'<use href="#{gid}"/>', lib.DEFS[n0:] + [f'<g id="{gid}">{sv}</g>'])
        del lib.DEFS[n0:]
        if len(_PIC) > 400:
            _PIC.pop(next(iter(_PIC)))
    sv, defs = _PIC[key]
    if defs[-1] not in lib.DEFS:
        lib.DEFS.extend(defs)
    return sv


def _picture(fn, t, w, h):
    c = lib.clip_rect(-w / 2, -h / 2, w, h)
    sx, sy = w / PW, h / PH
    return f'<g clip-path="url(#{c})"><rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#f4efe4"/>' \
           f'<g transform="scale({sx:.4f} {sy:.4f})">{fn(t)}</g></g>'


def framed(x, y, k, t, front, back=None, flip=0.0, style="gold", rot=0.0, w=PW, h=PH, glow=0.0, flash=0.0, wire=True, seed=0,
           shadow=True, lift=0.0):
    """Рамка на стене: центр (x, y), масштаб k. flip 0…1 — поворот по вертикальной оси (лицо → оборот): ширина сжимается до
    ребра и раскрывается обратной стороной; ближний край чуть выше (перспектива), тень на стене отходит и темнеет."""
    a = math.pi * clamp(flip)
    c, s_ = math.cos(a), math.sin(a)
    sx = max(abs(c), .02)
    face = c >= 0 or back is None
    sk = 7.0 * s_ * (1 if face else -1)
    sy = 1 + .07 * s_
    if face:
        bo, b = border(style, w, h, seed)
        body = bo + picture(front, t, w, h)
    else:
        bo, b = border("back", w, h, seed)
        body = bo + picture(back, t, w, h)
        body += line([(-w / 2 - 6, -h / 2 - b + 10), (w / 2 + 6, -h / 2 - b + 10)], 3, "#5a412a", seed=seed + 40, op=.5)
    if glow > .01:
        body = PR.glow(0, 0, max(w, h) * .9, .8 * glow, "#fff3c4") + body
    if face and (glow > .01 or flash > .01):          # блик бежит по стеклу
        ph = (t * .7 + seed * .37) % 1.0
        gx = -w / 2 + (w + 300) * ph - 150
        cc = lib.clip_rect(-w / 2, -h / 2, w, h)
        body += f'<g clip-path="url(#{cc})" opacity="{.35 + .4 * flash:.3f}"><path d="M{gx:.1f} {-h / 2 - 20:.1f} L{gx + 70:.1f} {-h / 2 - 20:.1f} ' \
                f'L{gx - 40:.1f} {h / 2 + 20:.1f} L{gx - 110:.1f} {h / 2 + 20:.1f}Z" fill="#ffffff"/></g>'
    if flash > .01:
        body += rect(-w / 2 - b, -h / 2 - b, w / 2 + b, h / 2 + b, "#fffbe8", .45 * flash)
    o = ""
    if shadow:
        off = 22 + 40 * s_ + 26 * lift
        op = .26 + .12 * s_
        ww = (w / 2 + b) * max(sx, .12)
        for g_ in (0, 10, 20):             # мягкая тень без фильтра: три слоя
            o += f'<rect x="{-ww + off - g_:.1f}" y="{-h / 2 - b + off - g_:.1f}" width="{2 * ww + 2 * g_:.1f}" height="{h + 2 * b + 2 * g_:.1f}" ' \
                 f'rx="{10 + g_}" fill="#3a2a1a" opacity="{op * (.5, .3, .2)[g_ // 10]:.3f}"/>'
    if wire and lift < .5:
        o += line([(-w * .25, -h / 2 - b), (0, -h / 2 - b - 70), (w * .25, -h / 2 - b)], 3, "#6b6258", taper=0, wmin=1, seed=seed + 50, op=.8)
        o += f'<circle cx="0" cy="{-h / 2 - b - 72:.1f}" r="7" fill="#7a6a5a" stroke="{INK}" stroke-width="2.5"/>'
    o += f'<g transform="skewY({sk:.2f}) scale({sx:.4f} {sy:.4f})">{body}</g>'
    if sx < .3:                                        # ребро рамки, когда она боком
        e = (1 - sx / .3) * 24
        col = GOLD_SH if style == "gold" else WOOD_SH
        o += rect(-e / 2, -h / 2 - b, e / 2, h / 2 + b, col)
    return tf(o, x, y, k, rot)


# ═════════════════════════ картинки в рамках (поле 600×440, центр 0, 0) ═════════════════════════
def sky(top, bot, y0=-220, y1=220):
    g = lib.lin_grad([(0, top, 1), (1, bot, 1)], 0, y0, 0, y1, units="userSpaceOnUse")
    return f'<rect x="-320" y="{y0}" width="640" height="{y1 - y0}" fill="url(#{g})"/>'


def pic_sea(t):
    o = sky("#4aa6ea", "#c8ecfb", -220, 40)
    o += PR.sun(170, -120, 46, 1.0, t, seed=4)
    o += blob([(-320, 30), (320, 30), (320, 120), (-320, 120)], "#2f8fd0")
    for j in range(5):
        y = 48 + j * 16
        xo = 30 * math.sin(t * 2 + j)
        o += line([(-300 + xo, y), (-180 + xo, y - 4), (-60 + xo, y)], 3, "#bfe6fb", seed=9300 + j, op=.8)
        o += line([(60 - xo, y + 6), (200 - xo, y + 2), (300 - xo, y + 6)], 3, "#bfe6fb", seed=9310 + j, op=.8)
    o += shape([(-330, 120), (330, 108), (330, 240), (-330, 240)], "#f3d892", blob([(-330, 170), (330, 160), (330, 240), (-330, 240)], "#e5c477", .7),
               w=4, seed=9320)
    o += tf(room._palm82(0, 0, 420, t, 1, lean=.12), -200, 200, .55)
    o += tf(room._palm82(0, 0, 360, t, 3, lean=-.1), 240, 210, .5)
    o += room._gull82(-40, -130, t, .6, 1) + room._gull82(40, -100, t + .3, .45, 2)
    return o


GROOM = {"TOP": "#2e3140", "TOP_SH": "#20222e", "TOP_SH2": "#171922", "FOLD": "#0f1016", "STITCH": "#4b5068"}
BRIDE = {"TOP": "#fbf8f2", "TOP_SH": "#e4ddd0", "TOP_SH2": "#cfc6b6", "FOLD": "#b8ae9c", "STITCH": "#ffffff"}


def couple(t, angry=0.0, k=.46, y=330):
    """Жених (слева) и невеста (справа) по пояс. angry 0 — счастливы, обнялись; 1 — ругаются лицом к лицу."""
    if angry < .5:
        e1 = ex_(brows="up", mouth="laugh", open=.55, smile=1.0, lid=.8, look=(.4, -.1))
        e2 = ex_(brows="up", mouth="laugh", open=.55, smile=1.0, lid=.8, look=(-.4, -.1))
        a1 = {"n": ("ik", (60, 140), -1)}
        g = waist("youth", -105, y, k, e1, arms=a1, pal=GROOM, head_ang=.12)
        b = waist("girl", 105, y, k * .95, e2, flip=True, pal=BRIDE, head_ang=.12)
        veil = blob(ellipse_pts(b["head"][0] + 20, b["head"][1] + 40, 85, 120, 18), "#ffffff", .55)
        flowers = "".join(shape(ellipse_pts(b["head"][0] + 30 * math.cos(q), b["head"][1] - 60 + 10 * math.sin(q), 11, 11, 10),
                                "#f6a6b8" if j % 2 else "#ffffff", "", w=2.4, seed=9400 + j) for j, q in enumerate((2.2, 2.0, 1.7, 1.4, 1.1)))
        return veil + g["svg"] + b["svg"] + flowers
    e = ex_(brows="frown", mouth="talk", open=.9, lid=.95, look=(1, -.1), smile=0)
    pt = math.sin(t * 14)
    g = waist("youth", -170, y, k, e, arms={"n": ("ik", (-40 + 10 * pt, 30), -1)}, hands={"n": {"dir": (1, -.2), "curl": (0, .9, .9, .9), "thumb": .6}},
              pal=GROOM, lean=-.08)
    b = waist("girl", 170, y, k * .95, dict(e, look=(1, -.2)), flip=True, arms={"n": ("ik", (40 - 10 * pt, 40), -1)},
              hands={"n": {"dir": (-1, -.2), "curl": (0, .9, .9, .9), "thumb": .6}}, pal=BRIDE, lean=-.08)
    return g["svg"] + b["svg"]


def pic_wedding(t):
    o = sky("#fbd9e0", "#fff3e6")
    for j in range(11):                                       # арка из цветов
        q = math.pi * j / 10
        x, y = -230 * math.cos(q), 40 - 230 * math.sin(q)
        o += shape(ellipse_pts(x, y, 26, 24, 12), "#f59ab0" if j % 2 else "#ffffff", blob(ellipse_pts(x, y, 9, 9, 8), "#f6c94a"), w=3, seed=9410 + j)
        o += line([(x, y + 20), (x + 14, y + 34)], 3, "#5fae52", seed=9430 + j)
    o += couple(t)
    for j in range(7):                                        # конфетти-сердечки
        x = -260 + 85 * j + 10 * math.sin(t * 3 + j)
        y = -200 + ((t * 60 + j * 53) % 160)
        o += tf(PR.heart(0, 0, .25, 0, seed=j), x, y, 1, 15 * math.sin(t * 2 + j))
    return o


def pic_car(t):
    o = sky("#ffe9b0", "#ffb978", -220, 120)
    o += blob([(-320, 110), (320, 110), (320, 240), (-320, 240)], "#e8d6c0")
    o += blob(ellipse_pts(0, 150, 260, 30, 20), "#c9b49a", .8)
    o += PR.sports_car(0, 140, .82, seed=2, t=t)
    for j, (x, y) in enumerate(((-150, 60), (90, 20), (200, 80))):
        u = .5 + .5 * math.sin(t * 6 + j * 2)
        o += PR.star4(x, y, 12 + 10 * u, 1.0)
    for j in range(3):
        o += line([(-260 + 40 * j, -200), (-200 + 40 * j, -90)], 5, "#ffffff", seed=9450 + j, op=.5)
    return o


def pic_smile(t):
    o = sky("#ffd36a", "#fff3c4")
    for j in range(12):
        q = 2 * math.pi * j / 12 + t * .4
        o += line([(170 * math.cos(q), -10 + 170 * math.sin(q)), (330 * math.cos(q), -10 + 330 * math.sin(q))], 10, "#fff6d6", seed=9460 + j, op=.7)
    e = ex_(brows="up", mouth="laugh", open=.6, smile=1.0, lid=.8, look=(0, .1))
    f = waist("stud82", -20, 400, .62, e, arms={"n": ("ik", (190, 0), -1)}, hands={"n": {"dir": (0, -1), "curl": (.9, 0, 0, .9), "thumb": .3}})
    o += f["svg"]
    o += PR.sparkles(-170, -110, .9, 1.0, t, seed=2, col="#ffffff") + PR.sparkles(180, -60, .7, 1.0, t, seed=5, col="#ffffff")
    return o


def smile_card(x, y, k=1.0, rot=0.0):
    o = line([(0, 40), (0, 230)], 9, "#a87a48", taper=0, wmin=1, seed=9470)
    o += shape(ellipse_pts(0, 0, 70, 56, 20), "#fff2c8", line([(-46, -2), (-20, 26), (20, 26), (46, -2)], 7, INK, seed=9471)
               + line([(-46, -2), (0, 40), (46, -2)], 0.1, INK, seed=9472), w=4, seed=9473)
    return tf(o, x, y, k, rot)


def back_smile(t):
    o = sky("#8f939c", "#b5b8bf")
    o += blob([(-320, 120), (320, 120), (320, 240), (-320, 240)], "#7c7f86")
    o += shape(lib.rrect(-280, 60, -110, 150, 10), "#9fa3ab", line([(-270, 80), (-120, 84)], 3, "#6c7078", seed=9480), w=3.5, seed=9481)   # смятая кровать
    e = ex_(brows="sad", mouth="wobble", open=.2, smile=0, lid=.45, look=(0, .3), bags=True)
    pp = (40, -30)
    f = waist("stud82", 0, 400, .62, e, arms={"n": ("ik", (pp[0] + 10, pp[1] + 150), -1)}, hands={"n": {"dir": (0, -1), "curl": (.9, .9, .9, .9), "thumb": .7}},
              head_ang=-.06)
    hx, hy = f["head"]
    o += f["svg"]
    o += smile_card(hx + 22, hy + 95, 1.25, -4 + 2 * math.sin(t * 5))
    return o


def back_wedding(t):
    o = sky("#9aa3b4", "#c7ccd6")
    o += couple(t, angry=1.0, k=.44, y=330)
    o += shape([(-200, 170, 1), (200, 170, 1), (220, 240, 1), (-220, 240, 1)], "#8a6a4a", "", w=4, seed=9490)        # стол
    o += PR.paper_stack(0, 172, .8, n=9, seed=4, mess=.6)
    for j in range(5):                                         # счета летают
        q = t * 3 + j * 1.3
        o += PR.paper(-130 + 65 * j + 14 * math.sin(q), -170 + 26 * math.cos(q), .4, 20 * math.sin(q + j), seed=j)
    return o


def back_car(t, u=1.0):
    """Бумажная цепь кредита от машины к горизонту (без цифр): звенья в перспективе, дальние мельче и теснее."""
    o = sky("#9fa8b8", "#d9dde4", -220, -40)
    o += blob([(-320, -40), (320, -40), (320, 240), (-320, 240)], "#b9b2a4")
    o += line([(-320, -40), (320, -40)], 3, "#7c7466", seed=9500)
    N, V = (-10.0, 235.0), (170.0, -40.0)
    R, D0, step = 105.0, 300.0, 120.0
    links = []
    n = int(4 + 40 * clamp(u))
    for i in range(n):
        q = D0 / (D0 + step * i)
        x, y = V[0] + (N[0] - V[0]) * q, V[1] + (N[1] - V[1]) * q
        r = R * q
        sw = max(1.2, 13 * q)
        if i % 2:
            rx, ry = r * .2, r * .62
        else:
            rx, ry = r * .85, r * .42
        links.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="{INK}" stroke-width="{sw + max(1.5, 5 * q):.1f}" '
                     f'transform="rotate({-50:.0f} {x:.1f} {y:.1f})"/>'
                     f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="#f6f2e8" stroke-width="{sw:.1f}" '
                     f'transform="rotate({-50:.0f} {x:.1f} {y:.1f})"/>')
    o += "".join(reversed(links))
    o += PR.sports_car(-200, 225, .42, seed=2, t=t)
    return o


def two_beach(t, smile=0.0, flash=0.0):
    """Двое на пляже перед фото: отвернулись друг от друга, надулись; на вспышке разом натягивают улыбки, он поднял телефон."""
    o = sky("#aab5bf", "#dfe3e6", -220, 40)
    o += blob([(-320, 30), (320, 30), (320, 110), (-320, 110)], "#6f93ad")
    o += shape([(-330, 110, 1), (330, 104, 1), (330, 240, 1), (-330, 240, 1)], "#d9c99e", "", w=4, seed=9580)
    sm = clamp(smile)
    if sm < .5:
        e1 = ex_(brows="frown", mouth="pursed", smile=0, lid=.75, look=(-1, .1))
        a = waist("youth", -120, 360, .42, e1, flip=True)
        b = waist("girl", 120, 360, .41, dict(e1, look=(1, .1)))
        o += a["svg"] + b["svg"]
        for j, (x, y) in enumerate(((a["head"][0], a["head"][1] - 110), (b["head"][0], b["head"][1] - 110))):     # пар обиды
            o += line([(x - 24, y), (x - 8, y - 30)], 5, INK, seed=9590 + j) + line([(x + 8, y), (x + 24, y - 30)], 5, INK, seed=9595 + j)
    else:
        e1 = ex_(brows="up", mouth="laugh", open=.6, smile=1.0, lid=.95, look=(.1, .1))
        a = waist("youth", -80, 360, .42, e1, head_ang=.12)
        b = waist("girl", 90, 360, .41, dict(e1, look=(-.2, .1)), flip=True, head_ang=.12)
        o += a["svg"] + b["svg"]
    if flash > .01:
        o += rect(-320, -240, 320, 240, "#ffffff", .85 * flash)
    return o


def pic_noodles(t):
    o = sky("#d8cdb8", "#c2b59c")
    o += blob([(-320, 90), (320, 90), (320, 240), (-320, 240)], "#9c7a56")
    cup = [(-110, -60), (110, -60), (86, 150), (-86, 150)]
    o += shape(cup, "#f6f1e6", blob([(-104, -20), (104, -20), (98, 30), (-98, 30)], "#d9483c") + blob([(40, -60), (110, -60), (86, 150), (30, 150)], "#ddd6c6", .7),
               w=5, seed=9600)
    for j in range(6):
        x = -80 + 32 * j
        pts = [(x, -50), (x + 10, -80), (x - 8, -104), (x + 8, -128)]
        o += line(pts, 13, INK, seed=9610 + j) + line(pts, 8, "#f6d27a", seed=9610 + j)
    o += line([(40, -170), (90, -40)], 9, "#c9c4b8", taper=0, wmin=1, seed=9620)                          # вилка
    for j in range(3):
        x = -60 + 50 * j
        ph = t * 3 + j
        o += line([(x + 8 * math.sin(ph + q), -130 - 30 * q) for q in range(4)], 4, "#ffffff", seed=9625 + j, op=.7)
    return o


def pic_bill(t):
    o = sky("#cfd3da", "#b7bcc6")
    env = [(-200, -110), (200, -110), (200, 140), (-200, 140)]
    o += shape(env, "#f3ead8", line([(-200, -110), (0, 30), (200, -110)], 4, INK, seed=9631) + blob([(-200, 140), (0, 20), (200, 140)], "#e3d6bc", .8),
               w=5, seed=9630)
    p = 1 + .08 * math.sin(t * 8)
    o += tf(shape(ellipse_pts(0, 0, 52, 52, 18), "#d9363a", blob(ellipse_pts(-10, -12, 30, 26, 14), "#ee5a5a", .7)
                  + line([(0, -26), (0, 8)], 10, "#fff2e8", taper=0, wmin=1, seed=9633) + blob(ellipse_pts(0, 22, 6, 6, 8), "#fff2e8"), w=4, seed=9632),
            0, 40, p)
    o += line([(-230, -170), (-190, -140)], 5, INK, seed=9634) + line([(230, -170), (190, -140)], 5, INK, seed=9635)
    return o


def pic_room(t):
    o = sky("#b9ad97", "#a89c86")
    for j in range(5):                                        # обои отходят
        o += line([(-300 + 130 * j, -220), (-296 + 130 * j, 220)], 3, "#9c907a", seed=9640 + j, op=.6)
    o += shape(lib.rect_pts(150, -170, 270, -60), "#8fa6bd", line([(210, -170), (210, -60)], 4, INK, seed=9645), w=4, seed=9646)      # окошко
    sw = 6 * math.sin(t * 2.3)
    o += line([(-150, -220), (-150 + sw * .3, -150)], 3, INK, seed=9647) + PR.glow(-150 + sw * .3, -130, 70, .7) + \
        shape(ellipse_pts(-150 + sw * .3, -136, 16, 20, 12), "#fff2b0", "", w=3, seed=9648)
    e = ex_(brows="worry", mouth="wobble", open=.2, smile=0, lid=.75, look=(.2, -.4), bags=True)
    d = waist("dima", 40, 470, .72, e, head_ang=.3, lean=.05)
    o += d["svg"]
    o += shape([(-320, 140), (-140, 140), (-140, 240), (-320, 240)], "#7a6a8a", "", w=4, seed=9649)    # край кровати
    return o


# ═════════════════════════ галерея ═════════════════════════
FLY = 1500.0
WALL, WALL_SH, PANEL, FLOOR = "#ece0c8", "#d9c9ab", "#c9ad85", "#b78a5c"


def gallery_bg(t, x0=-1200.0, x1=4800.0, dark=0.0, top=-2400.0):
    wc = lib.mix(WALL, "#8e8c96", dark)
    o = [rect(x0, top, x1, FLY - 280, wc)]
    o.append(rect(x0, FLY - 280, x1, FLY, lib.mix(PANEL, "#6f6c76", dark)))
    o.append(line([(x0, FLY - 280), (x1, FLY - 280)], 6, lib.mix("#a88a62", "#55525c", dark), taper=0, wmin=1, seed=9700))
    for k in range(int((x1 - x0) / 300) + 1):
        xx = x0 + 300 * k
        o.append(shape(lib.rect_pts(xx + 30, FLY - 250, xx + 270, FLY - 30), lib.mix("#d3b994", "#7a7782", dark), "", w=3, seed=9710 + k))
    o.append(rect(x0, FLY, x1, FLY + 2400, lib.mix(FLOOR, "#5d5660", dark)))
    for k in range(int((x1 - x0) / 160) + 1):
        xx = x0 + 160 * k
        o.append(line([(xx, FLY + 6), (xx - 140, FLY + 700)], 3, lib.mix("#9a6f45", "#4a4450", dark), seed=9730 + k, op=.7))
    for k in range(int((x1 - x0) / 900) + 1):              # потолочные споты: конусы света
        xx = x0 + 900 * k + 300
        o.append(f'<path d="M{xx - 30} {top} L{xx + 30} {top} L{xx + 260} {FLY - 300} L{xx - 260} {FLY - 300}Z" fill="#fff8e0" opacity="{.18 * (1 - dark):.3f}"/>')
    return "".join(o)


PICS = {"sea": pic_sea, "wedding": pic_wedding, "car": pic_car, "smile": pic_smile}
BACKS = {"sea": lambda t: two_beach(t), "wedding": back_wedding, "car": back_car, "smile": back_smile}
ROW = ["sea", "wedding", "car", "smile"]


def gallery_frames(t, x0, x1, flip=0.0, flash_t=None, k=.62, seed0=0):
    """Рамки на стене двумя рядами; flash_t(i) -> 0…1 — вспышка рамки i."""
    o = []
    step = 520.0
    i0 = int(math.floor(x0 / step)) - 1
    for i in range(i0, int(x1 / step) + 2):
        for r, y in enumerate((620.0, 1040.0)):
            j = (i * 2 + r) % 4
            x = i * step + (200 if r else 0)
            fl = flash_t(i * 2 + r) if flash_t else 0.0
            o.append(framed(x, y, k * (1.0 if r else .9), t, PICS[ROW[j]], BACKS[ROW[j]], flip=flip, rot=3 * math.sin(i * 1.7 + r),
                            glow=fl, flash=fl, seed=seed0 + (i * 2 + r) % 9))
    return "".join(o)


# ═════════════════════════ s01–s02: Дима бежит по галерее ═════════════════════════
RUN_V = 640.0
HIT01 = stress(2, .25)            # «чУвствовать»


def run_x(t):
    return 200.0 + RUN_V * t


def run_k(t):
    return .66 - .1 * ease_io(clamp(t / 3.0)) - .06 * ease_io(ramp(t, W(4), .5))


def flash_fn(t):
    def f(i):
        a = .12 + ((i * 0.37) % 1.0) * 2.6
        return bump(t, a, .05, .22) + .7 * bump(t, HIT01 + .04 * (i % 5), .04, .2)
    return f


def dima_run(t, x=None, trip=0.0, expr="panic82"):
    k = run_k(t)
    x = run_x(t) if x is None else x
    ph = t / .36
    fig = people.dima82_run(x, FLY - people.LEG_LEN * .9 * k, k, ph % 1.0, t, expr=expr, boot=False, socks=None, sandwich=False, lean=.32,
                            trip=trip)
    return fig


def fg_frames(t, cx, dx_par=1.6):
    """Передний план: рамки на тросах сверху и прислонённые снизу — пролетают быстрее (параллакс)."""
    o = []
    for i in range(-2, 9):
        x = i * 760 - (cx - 800) * (dx_par - 1)
        j = i % 4
        o.append(framed(x, 120 + 40 * math.sin(i), 1.35, t, PICS[ROW[j]], flash=bump(t, .3 + (i % 3) * .55, .05, .25), rot=6 * math.sin(i * 2.3),
                        seed=20 + i % 5, wire=False))
        o.append(framed(x + 380, FLY + 430, 1.25, t, PICS[ROW[(j + 2) % 4]], rot=-8 + 4 * math.sin(i), glow=.5 * bump(t, .6 + (i % 4) * .4, .05, .3),
                        seed=30 + i % 5, wire=False))
    return "".join(o)


def hook_scene(t, trip=0.0):
    cx = run_x(t) + 110
    cy = 1080.0
    fr = gallery_frames(t, cx - 1100, cx + 1100, flash_t=flash_fn(t))
    d = dima_run(t, trip=trip)
    fg = fg_frames(t, cx)
    body = gallery_bg(t, cx - 1400, cx + 1400) + fr + d["svg"] + fg
    return body, fr + d["svg"] + fg, cx, cy


def hook_wrap(body, t, hit, bg="#e9dcc4"):
    import anim
    hc = anim.hook_cam(t, hit=hit)
    z, r, dx, dy = hc["zoom"], hc["rot"], hc["dx"], hc["dy"]
    piv = 1000.0
    tr = f"translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) scale({z:.5f}) translate(-540 {-piv})"
    blur = ""
    amt = hc["zoom_blur"] / 0.07
    if amt > 0.03:
        for dk, op in ((.03, .30), (.06, .2), (.1, .12)):
            blur += (f'<use href="#hk91" opacity="{op * min(1.0, amt):.3f}" transform="translate({540 + dx:.2f} {piv + dy:.2f}) rotate({r:.3f}) '
                     f'scale({z * (1 + dk * amt):.5f}) translate(-540 {-piv})"/>')
    return f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{tr}"><g id="hk91">{body}</g></g>{blur}'


MASK_F = '<filter id="mk91"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 9 0"/></filter>'


def frame_s01(t):
    body, maskw, cx, cy = hook_scene(t)
    s = .96 + .03 * t
    if MASK:
        lib.DEFS.append(MASK_F)
        return lib.svg(f'<rect width="1080" height="1920" fill="#000"/><g transform="{lib.cam(cx, cy, s, 0)}"><g filter="url(#mk91)">{maskw}</g></g>')
    dx, dy = shake(t, HIT01, 12) if not NOCAM else (0, 0)
    v = f'<g transform="{lib.cam(cx + dx, cy + dy, s, 0)}">{body}</g>'
    if NOCAM:
        return lib.svg('<rect width="1080" height="1920" fill="#e9dcc4"/>' + v)
    return lib.svg(hook_wrap(v, t, HIT01) + title(t))


def frame_s02(t):
    a, b = T0("s02"), T1("s02")
    trip = ease_io(ramp(t, W(4) + .1, .35)) * (1 - .6 * ramp(t, W(4) + .9, .4))
    body, _, cx, cy = hook_scene(t, trip)
    u = ease_io(ramp(t, a, b - a))
    s = 1.02 + .22 * u + .05 * bump(t, W(4) + .15)
    dx, dy = shake(t, W(4) + .15, 10)
    return view(body, cx - 40 * u + dx, cy + 60 * u + dy, s, -2 * u, over=title(t))


# ═════════════════════════ s03: стена рамок до неба ═════════════════════════
def frame_s03(t):
    a, b = T0("s03"), T1("s03")
    u = ease_io(ramp(t, a, b - a))
    o = [gallery_bg(t, -1200, 2400, top=-3200)]
    for r in range(6):
        y = 1040 - 440 * r
        for i in range(-2, 4):
            x = i * 520 + (200 if r % 2 else 0)
            j = (i + r) % 4
            gl = .4 + .4 * math.sin(t * 5 + i + r * 1.3)
            o.append(framed(x, y, .62 * (1 - .04 * r), t, PICS[ROW[j]], glow=gl, seed=(i + r) % 9))
    ex = dict(people.EXPR["dima"]["look82"], look=(.1, -1))
    d = people.dima82(520, dima_hip(FLY, .3), .3, ex, "d82_rest", t=t, feet="stand", head_add=-.25)
    o.append(d["svg"])
    o.append(PR.sweat(600, FLY - 330, .5) if False else "")
    return view("".join(o), 540, 1150 - 650 * u, .95 - .25 * u, 0, over=title(t))


# ═════════════════════════ s04: три идеальные рамки (храповик) ═════════════════════════
def frame_s04(t):
    a, b = T0("s04"), T1("s04")
    o = [gallery_bg(t, -800, 1900)]
    spots = [("wedding", 11, (330, 520), 1.0, -5), ("car", 12, (760, 860), .95, 5), ("sea", 14, (360, 1190), 1.0, -3)]
    for name, wi, (x, y), k, rot in spots:
        p = pop(t, W(wi) - .04, .26)
        if p <= .01:
            continue
        o.append(framed(x, y + 200 * (1 - min(1.0, p)), k * p * .82, t, PICS[name], glow=.7 * bump(t, W(wi), .06, .5) + .25, flash=bump(t, W(wi), .04, .2),
                        rot=rot * p, seed=hash(name) % 9))
    z = 1.0 + .03 * ease_io(ramp(t, a, b - a))
    for wi in (11, 12, 14):
        z += .025 * bump(t, W(wi), .05, .25)
    return view("".join(o), 560, 860, z, 0)


# ═════════════════════════ s05: три кривые рамки Димы ═════════════════════════
def drop_in(t, at, d=.22):
    u = clamp((t - at) / d)
    if u <= 0:
        return None
    y = -500 * (1 - u * u) if u < 1 else 0.0
    sq = bump(t, at + d, .03, .12)
    return y, sq


def frame_s05(t):
    a, b = T0("s05"), T1("s05")
    o = [gallery_bg(t, -800, 1900, dark=.35)]
    items = [(pic_noodles, 18, (300, 470), .62, 7), (pic_bill, 19, (790, 560), .6, -8), (pic_room, 21, (540, 1050), .95, 2)]
    for fn, wi, (x, y), k, rot in items:
        r = drop_in(t, W(wi) - .2)
        if r is None:
            continue
        dy, sq = r
        o.append(framed(x, y + dy, k, t, fn, style="cheap", rot=rot + 4 * sq, seed=wi % 9, lift=0))
        if sq > .02:
            o.append(PR.dust_puff(x, y + PH * k / 2 + 30, .8, clamp((t - W(wi) - .02) / .4), seed=wi))
    lh = max([W(wi) for _, wi, *_ in items if W(wi) <= t], default=-9)
    dx, dy = shake(t, lh, 8) if lh > 0 else (0, 0)
    z = 1.0 + .06 * ease_io(ramp(t, a, b - a)) + .04 * bump(t, W(22), .05, .4)
    return view("".join(o), 540 + dx, 820 + dy + 60 * ease_io(ramp(t, W(21), .6)), z, 0)


# ═════════════════════════ кот переворачивает рамку ═════════════════════════
def cat_flipper(x, y, k, t, paw=0.0, look=(-.6, -.2), hop=0.0, smile=0.0, blink=0.0):
    st = dict(look=look, tail=6 * math.sin(t * 1.7), flame_e=.9, paw=paw, paw_dx=95.0, smile=smile, blink=blink, tilt=6 * paw)
    return CT.draw(x, y - hop, k, st, t)


def flip_scene(t, front, back, flip_a, flip_d, bg_dark=0.0, fx=600.0, fy=880.0, fk=.95, cat_in=None, hit=None, extra_back=""):
    """Большая рамка + кот справа снизу, лапа толкает правый край; flip_a — начало переворота, flip_d — длительность."""
    u = ease_io(ramp(t, flip_a, flip_d))
    paw = ease_out(ramp(t, flip_a - .25, .25)) * (1 - ease_io(ramp(t, flip_a + flip_d * .6, .3)))
    o = [gallery_bg(t, -800, 1900, dark=bg_dark)]
    o.append(framed(fx, fy, fk, t, front, back, flip=u, glow=.3 * (1 - u), seed=3, lift=math.sin(math.pi * u)))
    if u > .5 and extra_back:
        o.append(extra_back)
    hop = 0.0
    cx_ = 175.0
    if cat_in is not None:
        h = clamp((t - cat_in) / .3)
        if h <= 0:
            return "".join(o), u
        hop = 220 * math.sin(math.pi * h)
        cx_ -= 320 * (1 - ease_out(h, 2))
        if h < 1:
            o.append(PR.dust_puff(cx_, 1240, .5, clamp((t - cat_in - .3) / .4), seed=3) if False else "")
    sm = 1.0 if u > .8 else 0.0
    o.append(cat_flipper(cx_, 1232, .7, t, paw=paw, hop=hop, smile=sm, look=(.9, -.4) if u < .8 else (.3, .2)))
    if hit is not None:
        o.append(PR.sparkles(fx, fy - 250, 1.2, bump(t, hit, .05, .5), t, seed=7))
    return "".join(o), u


def frame_s06(t):
    a, b = T0("s06"), T1("s06")
    fa = stress(26, .45)
    body, u = flip_scene(t, pic_smile, back_smile, fa, .55, cat_in=W(24) - .1, hit=stress(30, .2))
    hk = stress(30, .2)
    dx, dy = shake(t, hk, 11)
    z = .98 + .06 * ease_io(ramp(t, a, b - a)) + .12 * ease_out(ramp(t, hk, .12)) - .04 * ease_io(ramp(t, hk + .2, .4))
    return view(body, 500 + dx, 960 + dy - 30 * ease_io(ramp(t, hk, .2)), z + .1, 1.5 * bump(t, hk, .05, .4))


# ═════════════════════════ s07: призыв ═════════════════════════
def frame_s07(t):
    import story_cta_tg as tg
    press = W(33) + 0.12
    return tg.frame(t, t0=press - 1.10, press=press, common=os.path.join(STORY, "common"))


# ═════════════════════════ s08: хуже всех ═════════════════════════
def frame_s08(t):
    a, b = T0("s08"), T1("s08")
    o = [gallery_bg(t, -800, 1900, dark=.25)]
    for r in range(3):
        for i in range(-1, 4):
            x = i * 420 + (160 if r % 2 else 0)
            j = (i + r) % 4
            o.append(framed(x, 1050 - 400 * r, .55, t, PICS[ROW[j]], glow=.5 + .3 * math.sin(t * 4 + i * 1.7 + r), seed=(i + r) % 9))
    k = .52
    d = people.dima82(440, dima_hip(FLY, k), k, "slump", "d80_slump", t=t, feet="stand")
    o.append(d["svg"])
    hx, hy = d["head"]
    cu = ease_out(ramp(t, W(40) - .1, .35))
    if cu > .01:
        o.append(PR.storm(hx + 40 + 6 * math.sin(t * 2), hy - 180, 300 * cu, 130 * cu, seed=4, flash=bump(t, W(40) + .1, .05, .2)))
        for j in range(6):
            yy = hy - 150 + ((t * 700 + j * 47) % 140)
            o.append(line([(hx - 110 + 40 * j, yy), (hx - 116 + 40 * j, yy + 26)], 3, "#6fa6d6", seed=9800 + j, op=.8 * cu))
    pw = ease_out(ramp(t, W(41) - .1, .3))
    o.append(cat_flipper(760, FLY + 10, .62, t, paw=pw, look=(-.9, -.3)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560 - 30 * u, 1000 + 40 * u, .9 + .1 * u, 0)


# ═════════════════════════ s09–s11: три переворота (храповик) ═════════════════════════
def frame_s09(t):
    a, b = T0("s09"), T1("s09")
    hk = stress(44, .2)
    body, u = flip_scene(t, pic_wedding, back_wedding, a + .12, .4, bg_dark=.15, hit=hk)
    dx, dy = shake(t, hk, 9)
    z = 1.0 + .05 * ease_io(ramp(t, a, b - a)) + .07 * bump(t, hk, .05, .3)
    return view(body, 500 + dx, 960 + dy, z + .12, -1.2 * bump(t, hk, .05, .3))


def frame_s10(t):
    a, b = T0("s10"), T1("s10")
    hk = stress(47, .15)
    grow = ease_out(ramp(t, hk - .05, .5))
    body, u = flip_scene(t, pic_car, lambda tt: back_car(tt, .25 + .75 * grow), a + .06, .34, bg_dark=.2, hit=hk)
    dx, dy = shake(t, hk, 9)
    z = 1.04 - .04 * ease_io(ramp(t, a, b - a)) + .08 * bump(t, hk, .05, .3)
    return view(body, 500 + dx, 960 + dy, z + .12, 1.2 * bump(t, hk, .05, .3))


def frame_s11(t):
    a, b = T0("s11"), T1("s11")
    hk = stress(51, .2)
    fl = W(54) + .03
    sm = ease_out(ramp(t, fl, .08))
    body, u = flip_scene(t, pic_sea, lambda tt: two_beach(tt, sm, bump(tt, fl, .03, .25)), stress(49, 0) - .05, .32, bg_dark=.25, hit=hk)
    dx, dy = shake(t, hk, 8)
    z = 1.0 + .08 * ease_io(ramp(t, a, b - a)) + .06 * bump(t, hk, .05, .3) + .05 * bump(t, fl, .04, .3)
    return view(body, 500 + dx, 960 + dy, z + .12, 0)


# ═════════════════════════ s12–s13: Мичиган — лента и тучи ═════════════════════════
def scroller(who, x, ground, k, t, mood=0.0, flip=False, seed=0):
    e = ex_(brows=("calm" if mood < .5 else "sad"), mouth="flat", smile=0, lid=.7 - .25 * mood, look=(.2 if not flip else -.2, .8), bags=mood > .5)
    sgn = -1 if flip else 1
    pp = (x + sgn * 95 * k / .5, ground - 860 * k)
    f = standing(who, x, ground, k, e, arms={"n": ("ik", pp, -1), "f": ("ik", (pp[0] - sgn * 30 * k / .5, pp[1] + 20), -1)},
                 hands={"n": {"dir": (0, -1), "curl": (.7, .7, .7, .7), "thumb": .5}, "f": {"dir": (0, -1), "curl": (.7, .7, .7, .7), "thumb": .5}},
                 flip=flip, head_ang=.25)
    th = (t * 7 + seed) % 1.0
    o = f["svg"] + phone(pp[0] - sgn * 10 * k / .5, pp[1] - 30 * k / .5, k * 1.1 / .5 * .5, sgn * -12, glow=1)
    o += line([(pp[0] + sgn * 4, pp[1] - 40 * k / .5 + 30 * th), (pp[0] + sgn * 4, pp[1] - 70 * k / .5 + 30 * th)], 3, "#ffffff", seed=seed + 9, op=.6)
    return o, f["head"]


def sky_room(dark=0.0):
    g = lib.lin_grad([(0, lib.mix("#cfe3ef", "#59607a", dark), 1), (1, lib.mix("#f1ece0", "#8a8698", dark), 1)], 0, -600, 0, FLY,
                     units="userSpaceOnUse")
    return f'<rect x="-1200" y="-2600" width="3600" height="{FLY + 2600}" fill="url(#{g})"/>' + rect(-1200, FLY, 2400, 4000, lib.mix("#c9b89a", "#6d6676", dark))


def clipboard(x, y, k, t, tick=0.0):
    o = shape(lib.rrect(-80, -110, 80, 110, 8), "#a8794a", "", w=4, seed=9900)
    o += shape(lib.rect_pts(-66, -90, 66, 100), "#fbf8f0", "".join(line([(-50, -50 + 34 * j), (40, -50 + 34 * j)], 3, "#b9b2a4", seed=9901 + j) for j in range(4)),
               w=3, seed=9905)
    o += shape(lib.rrect(-34, -124, 34, -96, 6), "#9aa0aa", "", w=3, seed=9906)
    if tick > .01:
        o += PR.check_mark(10, 30, .7, tick, col="#2f9a4a")
    return tf(o, x, y, k, -8)


def frame_s12(t):
    a, b = T0("s12"), T1("s12")
    dk = .25 * ease_io(ramp(t, a, b - a + 1.0))
    o = [sky_room(dk)]
    o.append(rect(-1200, FLY - 420, 2400, FLY - 410, "#b9ad97"))
    sci = people.scientist82("a", 170, dima_hip(FLY, .5), .5, "rest", t=t, expr="focus", feet="stand", flip=False,
                             arms={"n": ("ik", (300, FLY - 560), -1)}, hands={"n": {"dir": (1, -.4), "curl": (.8, .8, .8, .8), "thumb": .6}})
    o.append(sci["svg"])
    o.append(clipboard(330, FLY - 590, .9, t, tick=ease_out(ramp(t, W(57) + .1, .3))))
    grow = .35 + .65 * ease_out(ramp(t, W(59), .5))
    for j, (who, x, k) in enumerate((("stud82", 560, .46), ("elder82", 800, .47), ("subj82", 1020, .48))):
        s_, (hx, hy) = scroller(who, x, FLY, k, t, mood=.3 * grow, flip=False, seed=j)
        o.append(s_)
        col = lib.mix("#e6e9ee", "#8d929e", .4 * grow)
        o.append(PR.cloud(hx + 6 * math.sin(t * 2 + j), hy - 150, 200 * grow, 100 * grow, seed=j, col=col))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600 + 40 * u, 1060, .92 + .05 * u, 0)


def frame_s13(t):
    a, b = T0("s13"), T1("s13")
    u = ease_io(ramp(t, a, b - a))
    dk = .25 + .55 * u
    o = [sky_room(dk)]
    o.append(PR.clock(540, 260, 110, angle_h=360 * (t - a) * .8, angle_m=360 * (t - a) * 4))
    hk = stress(67, .2)
    for j, (who, x, k) in enumerate((("stud82", 250, .58), ("elder82", 560, .6), ("subj82", 860, .6))):
        s_, (hx, hy) = scroller(who, x, FLY + 200, k, t, mood=.4 + .6 * u, seed=j)
        o.append(s_)
    st_w = 360 + 700 * ease_io(ramp(t, a + .2, hk - a - .2))
    o.append(PR.storm(560 + 10 * math.sin(t * 1.5), 700, st_w, 230 + 60 * u, seed=5, flash=bump(t, hk, .03, .25)))
    if t >= hk - .02:
        o.append(PR.bolt(600, 700, 560, 1020, u=clamp((t - hk) / .2) * .3 + (.7 if t - hk > .06 else 0), w=30, seed=2))
        for j in range(20):
            yy = 720 + ((t * 900 + j * 61) % 380)
            xx = 230 + 34 * j
            o.append(line([(xx, yy), (xx - 8, yy + 34)], 3.5, "#9cc6ea", seed=9950 + j, op=.85))
    dx, dy = shake(t, hk, 10)
    return view("".join(o), 560 + dx, 940 + dy, .98 + .08 * u, 0)


# ═════════════════════════ s14: своя кухня против их витрины ═════════════════════════
def cake(x, y, k, t):
    o = shape(lib.rect_pts(-150, 0, 150, 14), "#e9e4dc", "", w=4, seed=9960)
    o += line([(0, 14), (0, 70)], 12, "#d8d2c8", taper=0, wmin=1, seed=9961) + shape(ellipse_pts(0, 76, 70, 12, 14), "#e9e4dc", "", w=3.5, seed=9962)
    for j, (w_, h_, col) in enumerate(((130, 90, "#f7c6d0"), (100, 78, "#fbe3e8"), (70, 66, "#f7c6d0"))):
        y0 = -sum(hh for _, hh, _ in [(130, 90, 0), (100, 78, 0), (70, 66, 0)][:j]) - h_
        o += shape(lib.rrect(-w_, y0, w_, y0 + h_, 10), col, blob(lib.rect_pts(-w_, y0, w_, y0 + 18), "#ffffff")
                   + "".join(blob(ellipse_pts(-w_ + 22 + 30 * q, y0 + 20, 9, 14, 8), "#ffffff") for q in range(int(w_ / 15))), w=4, seed=9963 + j)
    for j in range(5):
        o += shape(ellipse_pts(-56 + 28 * j, -246, 12, 12, 10), "#e2364a", blob(ellipse_pts(-60 + 28 * j, -250, 4, 4, 6), "#ffffff"), w=3, seed=9970 + j)
    o += line([(0, -258), (0, -320)], 7, "#7fb4e8", taper=0, wmin=1, seed=9975)
    o += PR.att_flame(0, -322, .5, t)
    return tf(o, x, y, k)


def dishes(x, y, k, t, wob=0.0):
    o = ""
    for j in range(9):
        dx = 18 * math.sin(j * 1.9) + wob * 12 * math.sin(t * 20 + j) * j / 9
        o += shape(ellipse_pts(dx, -26 * j, 120 - 3 * j, 22, 18), "#eef0f2" if j % 2 else "#dfe6ee", line([(-80 + dx, -26 * j + 6), (60 + dx, -26 * j + 10)], 2.4,
                   "#c7b26a", seed=9980 + j, op=.7), w=3.6, seed=9985 + j)
    o += tf(shape(ellipse_pts(0, 0, 90, 40, 18), "#5a5e68", blob(ellipse_pts(0, -6, 70, 26, 14), "#8a6a3a"), w=4, seed=9995)
            + line([(80, 0), (220, -30)], 14, "#3d4048", taper=0, wmin=1, seed=9996), 30 + wob * 6 * math.sin(t * 17), -260, 1, -18)
    o += PR.mug(-120, -10, .6, rot=-12, col="red", coffee=False, seed=3) + PR.mug(140, -40, .55, rot=20, col="white", coffee=False, seed=4)
    for j in range(3):
        o += line([(-60 + 50 * j, -330), (-50 + 50 * j, -360)], 3, "#7c8a6a", seed=9998 + j, op=.6)
    return tf(o, x, y, k)


def frame_s14(t):
    a, b = T0("s14"), T1("s14")
    u = ease_io(ramp(t, a, .35))
    lft, rgt = [], []
    # слева: витрина магазина с идеальным тортом
    lft.append(rect(-200, -200, 560, 2200, "#2f3448"))
    lft.append(shape(lib.rect_pts(30, 380, 520, 1260), "#fff6e6", "", w=6, seed=10001))
    lft.append(PR.glow(275, 760, 420, .9 + .1 * math.sin(t * 3), "#fff1c0"))
    for j in range(6):                                               # полосатый навес
        lft.append(blob([(10 + 86 * j, 300), (96 + 86 * j, 300), (96 + 86 * j, 380), (10 + 86 * j, 380)], "#e05a5a" if j % 2 else "#fbf5ea"))
    lft.append(line([(10, 300), (530, 300)], 5, INK, seed=10002))
    sh = bump(t, W(77), .06, .5)
    lft.append(cake(275, 1120, 1.35 + .08 * sh, t))
    lft.append(PR.sparkles(275, 760, 1.4, .6 + .4 * sh, t, seed=3, col="#ffffff"))
    lft.append(line([(80, 420), (180, 560)], 8, "#ffffff", seed=10003, op=.5) + line([(110, 420), (240, 620)], 5, "#ffffff", seed=10004, op=.35))
    lft.append(rect(-200, 1260, 560, 2200, "#3b3f52"))
    # справа: Димина кухня, гора посуды
    rgt.append(rect(520, -200, 1300, 2200, "#b7b39a"))
    for j in range(8):
        rgt.append(line([(540 + 70 * j, 700), (540 + 70 * j, 1150)], 2, "#9c987f", seed=10010 + j, op=.6))
    rgt.append(shape(lib.rect_pts(520, 1150, 1300, 1260), "#8a7a6a", "", w=5, seed=10020))
    wob = bump(t, W(74), .05, .6)
    rgt.append(dishes(680, 1150, 1.1, t, wob))
    e = ex_(brows="worry", mouth="flat", smile=0, lid=.7, look=(-1, -.2), bags=True)
    d = waist("dima", 905, 1440, .6, e, flip=True, head_ang=.1)
    rgt.append(d["svg"])
    rgt.append(shape(lib.rect_pts(520, 1330, 1320, 2300), "#8a7a6a", line([(540, 1350), (1300, 1350)], 4, "#6a5a4a", seed=10021), w=5, seed=10022))
    cl_l = lib.clip_rect(-400, -400, 940 + 0, 2800)
    cl_r = lib.clip_rect(540, -400, 1200, 2800)
    dxl = -600 * (1 - u)
    dxr = 600 * (1 - ease_io(ramp(t, a + .1, .35)))
    body = f'<g clip-path="url(#{cl_l})"><g transform="translate({dxl:.1f} 0)">{"".join(lft)}</g></g>' \
           f'<g clip-path="url(#{cl_r})"><g transform="translate({dxr:.1f} 0)">{"".join(rgt)}</g></g>'
    body += line([(540, -200), (548, 500), (532, 1000), (546, 1500), (540, 2200)], 12, INK, taper=0, wmin=1, seed=10030)
    v = ease_io(ramp(t, a, b - a))
    return view(body, 540, 900, 1.0 + .04 * v, 0, bg="#2f3448")


# ═════════════════════════ s15–s16: сравнивает себя с собой ═════════════════════════
def ghost(svg, op=.45):
    return f'<g opacity="{op:.3f}">{svg}</g>'


def frame_s15(t):
    a, b = T0("s15"), T1("s15")
    o = [gallery_bg(t, -800, 1900)]
    for i in range(-1, 4):
        o.append(framed(i * 520, 760, .6, t, PICS[ROW[i % 4]], seed=i % 9))
    turn = ease_io(ramp(t, a + .15, .3))
    k = .56
    d = people.dima82(640, dima_hip(FLY, k), k, "calm82", "d82_rest", t=t, feet="stand", flip=turn < .5, head_add=-.05)
    gp = ease_out(ramp(t, W(81) - .2, .5))
    if gp > .01:
        g = people.dima82(220, dima_hip(FLY, k), k, "downcast", "d80_slump", t=t, feet="stand")
        o.append(ghost(g["svg"], .45 * gp))
        o.append(PR.sparkles(220, FLY - 600, 1.0, gp, t, seed=2, col="#ffffff"))
    o.append(d["svg"])
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 470 - 40 * u, 1030, 1.0 + .1 * u, 0)


def step_block(x0, x1, y_top, ground, seed=0):
    return shape(lib.rect_pts(x0, y_top, x1, ground), "#c9a37a", blob(lib.rect_pts(x0, y_top, x1, y_top + 22), "#e2c39a")
                 + blob(lib.rect_pts(x1 - 40, y_top, x1, ground), "#a8835c", .8), w=5.5, seed=10100 + seed)


def frame_s16(t):
    a, b = T0("s16"), T1("s16")
    o = [gallery_bg(t, -800, 1900)]
    s1, s2 = FLY - 120, FLY - 260
    o.append(step_block(120, 470, s1, FLY + 40, 1))
    o.append(step_block(470, 860, s2, FLY + 40, 2))
    k = .5
    g = people.dima82(300, dima_hip(s1, k), k, "downcast", "d80_slump", t=t, feet="stand")
    o.append(ghost(g["svg"], .45))
    hp = ease_io(ramp(t, W(86) - .1, .35))
    hop = 120 * math.sin(math.pi * hp)
    gy = s2 if hp > .5 else s1
    x = 430 + 230 * hp
    d = people.dima82(x, dima_hip(gy, k) - hop, k, "proud82" if hp > .6 else "calm82", "d82_rest", t=t, feet="stand")
    o.append(d["svg"])
    o.append(PR.sparkles(x, s2 - 640, 1.3, bump(t, W(86) + .25, .06, .6), t, seed=4))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 500, 1080 - 40 * u, 1.05 + .05 * u, 0)


# ═════════════════════════ s17: кот на троне из рамок ═════════════════════════
def frame_s17(t):
    a, b = T0("s17"), T1("s17")
    o = [gallery_bg(t, -800, 1900, top=-1200)]
    o.append(PR.glow(540, 900, 700, .8, "#fff1c4"))
    o.append(framed(540, 760, .95, t, PICS["sea"], rot=0, seed=1, wire=False, glow=.5))      # спинка трона
    for j, (x, y, rot, nm) in enumerate(((330, 1180, -14, "car"), (750, 1170, 12, "sea"), (540, 1330, 0, "smile"), (380, 1420, 6, "sea"),
                                          (700, 1430, -5, "wedding"))):
        o.append(framed(x, y, .62, t, PICS[nm], BACKS[nm], flip=1.0 if j % 2 else 0.0, rot=rot, seed=j + 2, wire=False))
    fix = bump(t, stress(94, .2), .1, .5)
    st = dict(look=(.6, -.3), tail=10 * math.sin(t * 1.6), flame_e=1.0, smile=1.0, blink=1.0, tilt=8 + 4 * math.sin(t * 2), paw=.6 * fix)
    o.append(CT.draw(540, 1170, 1.05, st, t))
    hx, hy = CT.head_world(540, 1170, 1.05, st)
    o.append(PR.crown(hx + 6 * math.sin(t * 2), hy - 125 - 20 * fix, .9, rot=12 - 10 * fix, bounce=fix))
    o.append(PR.sparkles(540, hy - 260, 1.4, .7, t, seed=6))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1000 - 40 * u, .95 + .07 * u, 0)


# ═════════════════════════ s18: петля — ракурс хука, рамки перевёрнуты ═════════════════════════
def frame_s18(t):
    a, b = T0("s18"), T1("s18")
    tt = .6 + (t - a) * .45                 # ракурс хука, Дима идёт медленнее
    x = run_x(tt)
    cx = x + 110
    fr = gallery_frames(t, cx - 1100, cx + 1100, flip=1.0)
    k = .6
    d = people.dima82_walk(x, dima_hip(FLY, k), k, (t * 1.3) % 1.0, t, expr="calm82", mug=False)
    cat_ = CT.draw(cx + 330, FLY + 10, .6, dict(look=(-.8, -.1), smile=1.0, blink=1.0 if t > W(98) else 0.0, tail=8 * math.sin(t * 1.7)), t)
    body = gallery_bg(t, cx - 1400, cx + 1400) + fr + d["svg"] + cat_
    return view(body, cx, 1080, .99, 0)


FRAMES = {k[6:]: v for k, v in dict(globals()).items() if k.startswith("frame_s")}


def frame(sid, t):
    if sid != "s07":
        lib.DEFS.clear()
    return FRAMES[sid](t)
