"""Рилс 72 «СДВГ не существует», группа D — голоса прошлого у костра (ночь):
s07 (7.96–9.55): Дима на бревне обнял колени, лицо в тёплом свете снизу; «пятнадцать лет» — его тень на камне за спиной растёт из
    детской во взрослую; кот далеко за огнём, спиной к нам, огонёк в такт пламени.
s08 (9.55–10.45): дым над огнём собирается в учительницу (линия дыма), «учителей» грозит пальцем и указкой; камера плывёт вверх.
s09 (10.45–11.18): дым перетекает в маму (руки в боки, качает головой), «мамы» вздыхает; внизу край лица Димы, он опускает глаза.
s10 (11.18–12.40): дым складывается в хмурое лицо самого Димы, на «себя» нависает ближе; Дима втягивает голову и утыкается в колени.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Ночь у костра — common/room.py, Дима, тень, дымные силуэты — common/people.py,
кот — common/cat.py. Надписей, букв и цифр нет."""
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
import people  # noqa: E402
import room as R  # noqa: E402
from lib import blob, clamp, ease_io, ease_out, ellipse_pts, line  # noqa: E402,F401

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


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.update(kw)
    return e


def blinks(t, times, dur=.16):
    v = 0.0
    for a in times:
        u = (t - a) / dur
        if 0 < u < 1:
            v = max(v, math.sin(math.pi * u))
    return v


def warm(svg, t, u=1.0):
    return R.fire_tint(svg, t, u, 1.0)


def warm_cat(svg, t, u=1.0):
    """Кот у огня: тинт слабее — шерсть остаётся почти чёрной."""
    return R.fire_tint(svg, t, u, .3)


HIP = R.DIMA_LOG


def dima_seated(t, pose_a="hug_knees", pose_b=None, u=0.0, e=None, lean=0.0, head=0.0, shrug=0.0, tight=1.0):
    """Дима на бревне, колени к груди (people: hug_knees / chin_knees), живое покачивание поверх позы. -> (svg, fig)."""
    hx, hy = HIP
    if pose_b:
        kw = people.mix_pose(pose_a, pose_b, u, hx, hy, 1.0)
    else:
        kw = people.pose_kw(pose_a, hx, hy, 1.0)
    feet = people.knees_kw(hx, hy, 1.0, tight=tight)["feet"]
    fig = people.dima(hx, hy, 1.0, e or ex("glassy"), None, feet=feet, arms=kw["arms"], hands=kw["hands"],
                      lean_add=kw["lean"] + lean + .01 * math.sin(t * 1.9), head_add=kw["head_ang"] + head + .015 * math.sin(t * 1.3),
                      shrug=shrug)
    return fig["svg"], fig


def eye_glint(fig, u=1.0):
    """Отблеск огня в глазах (тёплая точка) — лицо живое в темноте."""
    if u <= .01 or "head" not in fig:
        return ""
    gx, gy = fig["head"]
    return "".join(blob(ellipse_pts(gx + dx + 6, gy - 20, 5, 5, 8), "#FFC24A", .85 * u) for dx in (18, 92))


def scene(t, mode="wide"):
    sc = R.fire_scene(t, 1.0, mode)
    back = "".join(sc[k] for k in ("sky", "bg", "ground", "stones_back"))
    return sc, back


def shot(world, cx, cy, s, rot=0.0):
    set_ink(s)
    return lib.svg(f'<rect width="1080" height="1920" fill="#05080f"/><g transform="{lib.cam(cx, cy, s, rot)}">{"".join(world)}</g>')


# ═════════════════════════ s07: «пятнадцать лет» — тень на камне растёт ═════════════════════════
T_SL = wt("слышал", 7.5)          # 8.13
T_15 = wt("пятнадцать", 7.5)      # 8.52
T_LET = wt("лет", 8.5)            # 9.04
CAT07 = (470.0, 1165.0, .4)       # кот за огнём, спиной к нам


def stone_shadow(t, age_u):
    """Тень Димы на камне за спиной: растёт из детской во взрослую, клип по контуру камня, чуть дрожит со светом огня."""
    sx, sy = R.STONE_SHADOW
    c = lib.clip_of(R.stone_shadow_pts())
    fl = R.light(t)
    k = 1.0 * (1 + .03 * (fl - 1) * 10)
    feet = (sx - 100 + 6 * math.sin(t * 6.1), R.HORIZON + 440)
    return f'<g clip-path="url(#{c})" opacity=".82">{people.dima_shadow(feet[0], feet[1], k, age_u, t, col="#140d14", blur_sd=4.0)}</g>'


def s07(t):
    lib.dyn_begin()
    sc, back = scene(t, "face")
    age = sm(t, T_15 - .02, T_LET + .2)
    nod = .05 * bump(t, T_SL, .4)
    e = ex("glassy", look=(.55, .2), closed=blinks(t, (8.35, 9.35)), lid=.55)
    dsvg, fig = dima_seated(t, e=e, head=nod)
    cx, cy, ck = CAT07
    st = dict(turn=0.0, look=(0, 0), tail=10 * math.sin(t * 2.6), flame_e=1.0 + .35 * math.sin(t * 7.3) + .2 * math.sin(t * 12.9))
    cat = warm_cat(cat_back(cx, cy, ck, st, t), t)
    world = [back, stone_shadow(t, age), cat, sc["fire"], sc["stones_front"], sc["log"], warm(dsvg, t), eye_glint(fig)]
    # медленный наезд на лицо
    fx, fy = fig.get("head", (HIP[0] + 60, HIP[1] - 470))
    u = sm(t, 7.76, 9.75)
    cx_, cy_ = lerp(110.0, fx - 170, u), lerp(1060.0, fy + 280, u)
    s = lerp(1.22, 1.36, u)
    return shot(world, cx_, cy_, s)


def cat_back(x, y, k, st, t):
    """Кот спиной к нам: рисунок cat.draw без морды (затылок — шерсть, уши, хвост с огоньком). Пока в cat.py нет вида со спины —
    голова повёрнута к огню и закрыта затылком: морда сдвинута turn=±1 и перекрыта пятном шерсти."""
    st = dict(st)
    st["turn"] = 0.0
    st["blink"] = 1.0
    body = CAT.draw(x, y, k, st, t)
    hx, hy = CAT.head_world(x, y, k, st)
    nape = blob(ellipse_pts(hx, hy + 10 * k, 100 * k, 86 * k, 18), CAT.CAT, 1.0) + line(
        [(hx - 40 * k, hy - 30 * k), (hx, hy - 44 * k), (hx + 40 * k, hy - 30 * k)], 3, CAT.CAT_EDGE, seed=7401, op=.7)
    return body + nape


def frame(sid, t):
    return {"s07": s07}[sid](t)
