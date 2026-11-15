"""Рилс 74 «Прекрати ныть», группа D — кот крупно:
s04 (трон фронтально: кот-«король» в съехавшей короне подаётся к зрителю, расцепляет лапы; «Пиши» — тычет лапой прямо в камеру,
вторая передняя на подлокотнике; «комменты» — дважды стукает подушечкой по «стеклу», расходятся кольца),
s15 (кот на столе в тёплом свете лампы довольный: жмурится, маленький язычок, звёздочки; «ушло» — потягивается передними лапами;
«две минуты» — звёздочки вспыхивают, кивок; за ним цветок распрямляется),
s16 (призыв: кот близко подаётся к камере, мягкие глаза; «Что висит» — наклон головы, тянет лапу к зрителю; «у тебя» — лапа замирает
у «стекла»; «Напиши» — мягкий стук подушечкой, кольца).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Места — common/room.py, кот — common/cat.py, предметы — common/props.py.
Букв и цифр нет. Лап у кота всегда четыре: к «стеклу» идёт та же правая передняя лапа (cat.body рисует её вытянутой, подушечка
поверх — её же кончик), вторая передняя на опоре."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people as PE  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»:").lower() == word:
            return w["start"]
    raise KeyError(word)


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


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def cat_u(x, y, k, ux, uy):
    """Точка рисунка кота (ед.) → мир (без поворота тела — в этих планах rot = 0)."""
    return x + (ux - CAT.CX) * k, y + (uy - CAT.CBOT) * k


def paw_tip_u(st):
    pw = st.get("paw", 0.0)
    return CAT.CX + 25 + st.get("paw_dx", 70.0) * pw * 1.6, 1306 - 150 * pw


def paw_pad(x, y, r, press=0.0, rot=0.0, seed=0):
    """Подушечка лапы, повёрнутая к зрителю (ракурс «лапа в камеру»): мех, большая подушка и четыре пальчика; press — прижата к стеклу."""
    sx, sy = 1 + .1 * press, 1 - .08 * press
    o = shape(ellipse_pts(0, 0, r, r * .92, 16), CAT.CAT, blob(ellipse_pts(r * .3, r * .3, r * .7, r * .6, 12), CAT.CAT_SH, .5), w=4.6, seed=seed)
    o += shape(ellipse_pts(0, r * .22, r * .42, r * .34, 14), "#e8823a", blob(ellipse_pts(-r * .1, r * .14, r * .16, r * .1, 8), "#f6b07a", .9),
               w=3.0, seed=seed + 1)
    for j, (a, d) in enumerate(((-140, .56), (-105, .66), (-75, .66), (-40, .56))):
        ar = math.radians(a)
        o += shape(ellipse_pts(math.cos(ar) * r * d, math.sin(ar) * r * d * .95 + r * .1, r * .15, r * .13, 10), "#e8823a", "", w=2.4, seed=seed + 2 + j)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale({sx:.3f} {sy:.3f})">{o}</g>'


def glass_rings(x, y, t, t_tap, k=1.0):
    return PR.tap_rings(x, y, clamp((t - t_tap) / .55), k) if t > t_tap else ""


def poke(t, t_on, taps, t_off=None):
    """Сила вытягивания лапы к стеклу 0…1 и прижатие press на каждом стуке."""
    out = sm(t, t_on - .12, t_on + .12)
    if t_off is not None:
        out *= 1 - sm(t, t_off, t_off + .25)
    press = sum(bump(t, ts - .04, .14) for ts in taps)
    back = sum(.12 * bump(t, ts - .14, .12) for ts in taps)      # замах перед стуком
    return out, min(1.0, press), back


# ═════════════════════════ s04: «Пиши в комменты» ═════════════════════════
T_PI = wt("пиши")            # 3.96 — лапа в камеру
T_KO = wt("комменты")        # 4.28 — первый стук
TAPS4 = (T_KO + .02, T_KO + .26)
CAM4 = (548.0, 960.0, 1.62)


def s04(t):
    lib.dyn_begin()
    d = R.throne_scene(t, "regal", "front", .6 * math.sin(t * 2.6))
    x, y, k = d["cat"]
    st = dict(PE.CAT_ST.get("king74", dict(cross=1.0, smug=1.0, cold=.55)))
    out, press, back = poke(t, T_PI, TAPS4)
    st["cross"] = 1 - sm(t, 3.75, T_PI)
    st["smug"] = .8
    st["cold"] = .35
    st["look"] = (0, .1)
    st["tilt"] = -5 + 3 * math.sin(t * 3.1) + damp(t, T_PI, 3, 3, 6)
    st["drop"] = .1 * sm(t, 3.75, 4.0) + .05 * press
    st["ear"] = -4 + damp(t, T_PI, 6, 4, 6) + 3 * math.sin(t * 10)
    st["tail"] = -8 + 20 * math.sin(2 * math.pi * 1.6 * t + .7)
    st["flame_e"] = 1.2 + .4 * math.sin(t * 9)
    # правая передняя тянется вперёд (к зрителю), левая передняя — на левый подлокотник
    st["paw"] = .3 + .6 * out
    st["paw_dx"] = 40.0
    st["paw_l"] = .25 * sm(t, 3.8, T_PI + .05)
    st["paw_l_dx"] = 247.0 * sm(t, 3.8, T_PI + .05) + 1
    if st["paw_l"] < .03:
        st["paw_l"] = 0.0
    cat = CAT.draw(x, y, k, st, t)
    tx, ty = cat_u(x, y, k, *paw_tip_u(st))
    r = k * (24 + 34 * out) * (1 - back)
    pad = paw_pad(tx, ty, r, press, -12 + 10 * out, seed=4040) if out > .05 else ""
    cr = crown_tilted(x, y, k, st, t)
    lean = 1 + .06 * sm(t, 3.75, 4.05)
    world = (d["bg"] + d["back"] + R.drape74("front", t, 1.0, 14) + d["seat"] +
             f'<g transform="translate({x} {y}) scale({lean:.4f}) translate({-x} {-y})">{cat}{cr}{pad}</g>' + d["arms"] + d["light"] + d["motes"])
    cx, cy, s = CAM4
    z = 1 + .06 * sm(t, T_PI, 4.9) + .02 * press
    sx_, sy_ = (tx - x) * .06 * sm(t, T_PI, 4.9), (ty - cy) * .03
    ss = s * z
    set_ink(ss)
    rings = "".join(glass_rings(*_to_frame(tx, ty, cx + sx_, cy + sy_, ss), t, ts, 1.6) for ts in TAPS4)
    return lib.svg(f'<g transform="{lib.cam(cx + sx_, cy + sy_, ss)}">{world}</g>{rings}')


def _to_frame(x, y, cx, cy, s):
    return 540 + (x - cx) * s, 960 + (y - cy) * s


def crown_tilted(x, y, k, st, t):
    """Корона набок (как после «СДВГ» в s01) на голове кота — та же, что в хуке."""
    sys.path.insert(1, os.path.join(STORY, "ext_c"))
    import s74c      # та же корона и та же посадка на голову, что в хуке (группа C)
    return s74c.crown_on(x, y, k, st, t, slide=26, rot=16 + 3 * math.sin(t * 7), hop=0, shine=.2)


# ═════════════════════════ s15: довольный кот ═════════════════════════
T_USH = wt("ушло")           # 21.84 — потягивается
T_MIN = wt("минуты")         # 22.31 — звёздочки вспыхивают, кивок
CAT15 = (957.0, R.DESK_TOP - 40.0, 1.0)
CAM15 = (998.0, 720.0, 3.9)


def desk_room(t, cat_svg="", front="", plant=None, plant_at=None):
    d = R.night_desk(t, "lamp", "cat")
    px, py = plant_at or R.PLANT74
    pl = PR.houseplant(px, py, .75, **(plant or {}), t=t, seed=1) if plant is not None else ""
    return d["bg"] + d["lamp"] + d["desk_top"] + d["pool"] + pl + cat_svg + front      # лампа у стены — за котом


def s15(t):
    lib.dyn_begin()
    x, y, k = CAT15
    st = dict(PE.CAT_ST.get("happy74", dict(blink=.75, smile=1.0, perk=1.0, flame_e=1.8)))
    st["blink"] = 1.0 - .35 * bump(t, 21.62, .3)      # жмурится от удовольствия (глаза-дуги), на миг приоткрывает
    st["tongue"] = .22 + .06 * math.sin(t * 6)
    st["tilt"] = 6 * math.sin(2 * math.pi * .55 * t + .5) + damp(t, T_MIN, 4, 2.5, 5)
    st["drop"] = PE.cat_nod(t, T_MIN + .05, .4, .3)
    st["tail"] = 6 + 10 * math.sin(2 * math.pi * .8 * t)
    st["flame_e"] = 1.6 + .6 * sm(t, 21.6, 22.6) + .5 * bump(t, T_MIN, .4) + .2 * math.sin(t * 9)
    # потягивается: обе передние лапы вперёд-вверх и обратно (те же две лапы)
    stretch = bump(t, T_USH - .08, .5)
    st["paw"] = .55 * stretch
    st["paw_dx"] = 60.0
    st["paw_l"] = .55 * stretch
    st["paw_l_dx"] = 60.0
    st["sy"] = 1 + .05 * stretch
    if st["paw"] < .03:
        st["paw"] = st["paw_l"] = 0.0
    cat = CAT.draw(x, y, k, st, t)
    hx, hy = cat_u(x, y, k, 836, 1050)
    sp = PR.sparkles(hx, hy, 1.0, .75 + .6 * bump(t, T_MIN, .4), t, seed=15, n=6, r=150 + 30 * bump(t, T_MIN, .4))
    sp += PR.star4(hx - 120, hy - 110, 9 + 9 * bump(t, T_MIN, .4), 1.0) + PR.star4(hx + 130, hy - 90, 7 + 8 * bump(t, T_MIN + .08, .4), 1.0)
    perk = sm(t, 21.75, 22.7)
    world = desk_room(t, cat + sp, plant=dict(droop=1.0, fallen=3.0, perk=perk), plant_at=(1065.0, R.DESK_TOP - 92.0))   # цветок за правым плечом кота
    cx, cy, s = CAM15
    z = 1 + .04 * sm(t, 21.5, 23.15) + .02 * bump(t, T_MIN, .5)
    set_ink(s * z)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, s * z)}">{world}</g>')


# ═════════════════════════ s16: «Что висит у тебя? Напиши» ═════════════════════════
T_CHTO = wt("что", 22.5)     # 22.98
T_NA = wt("напиши", 23.5)    # 24.12 — стук по стеклу
TAPS16 = (T_NA + .06,)
CAT16 = (960.0, R.DESK_TOP - 30.0, 1.0)
CAM16 = (955.0, 735.0, 4.25)


def s16(t):
    lib.dyn_begin()
    x, y, k = CAT16
    st = dict(PE.CAT_ST.get("warm74", dict(blink=.3, smile=1.0, flame_e=1.4)))
    st["blink"] = .1 + .9 * bump(t, 22.85, .14) + .9 * bump(t, 24.62, .14)
    st["perk"] = .9
    st["smile"] = 1.0
    st["look"] = (0, .05)
    q = sm(t, T_CHTO, T_CHTO + .35) * (1 - sm(t, 24.4, 24.8))
    st["tilt"] = 11 * q + 2 * math.sin(t * 2.2)
    st["turn"] = .08 * q
    st["ear"] = 4 * q + 3 * math.sin(t * 2.6) + damp(t, TAPS16[0], 5, 4, 6)
    st["tail"] = -6 + 10 * math.sin(2 * math.pi * .6 * t)
    st["flame_e"] = 1.4 + .2 * math.sin(t * 7)
    out, press, back = poke(t, T_CHTO + .25, TAPS16, t_off=24.75)
    st["paw"] = .9 * out
    st["paw_dx"] = 34.0
    if st["paw"] < .03:
        st["paw"] = 0.0
    cat = CAT.draw(x, y, k, st, t)
    tx, ty = cat_u(x, y, k, *paw_tip_u(st))
    r = k * (24 + 46 * out) * (1 - back)
    pad = paw_pad(tx, ty, r, press, -10 + 8 * out, seed=1616) if out > .05 else ""
    lean = 1 + .07 * sm(t, 22.75, 23.4)
    world = desk_room(t, f'<g transform="translate({x} {y}) scale({lean:.4f}) translate({-x} {-y})">{cat}{pad}</g>', plant=dict(droop=0.0, fallen=3.0, perk=1.0))
    cx, cy, s = CAM16
    z = 1 + .05 * sm(t, 22.75, 25.05) + .02 * press
    ss = s * z
    set_ink(ss)
    ftx, fty = _to_frame(x + (tx - x) * lean, y + (ty - y) * lean, cx, cy, ss)
    rings = "".join(glass_rings(ftx, fty, t, ts, 1.4) for ts in TAPS16)
    return lib.svg(f'<g transform="{lib.cam(cx, cy, ss)}">{world}</g>{rings}')


def frame(sid, t):
    return {"s04": s04, "s15": s15, "s16": s16}[sid](t)
