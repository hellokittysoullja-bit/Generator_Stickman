"""Диван Димы рилса 44 «мечтает и ничего» (агент room): s01 (хук: вечер, Дима развалился на диване и мечтает, облако
растёт, влёт камеры), s04 (крупнее: в руке пустой пунктирный билет, на «нет» облако лопается).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика; удары — на словах voice/words.json.
Мир — вечерняя комната (world.py: den.py рилса 32 + фиолетовый диван рилса 42); Дима — people.py (лохматый, щетина,
мешки, горчичное худи) сидит, откинувшись на спинку, в 3/4 вправо; облако мечты — dream.py.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dream  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import world  # noqa: E402
from ink import ellipse_pts  # noqa: E402
from lib import INK, back_out, blob, clamp, ease_io, ease_out, line, shape, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!:").lower() == word.lower() and w["start"] >= after - 1e-6:
            return w["start"]
    raise KeyError(word)


T_DIMA = wt("дима")          # 0.16
T_KAZH = wt("каждый")        # 0.56
T_VECH = wt("вечер")         # 1.16
T_MECH = wt("мечтает")       # 1.44
T_BIL = wt("билета")         # 5.40
T_NET = wt("нет")            # 6.24

BS = 0.62
HIP = np.array([330.0, 1186.0])
_ST = {}


def osc(t, fr, ph=0.0):
    return math.sin(2 * math.pi * fr * t + ph)


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def kick(t, t0, dur=.4, freq=2.2):
    u = t - t0
    if u <= 0 or u > dur:
        return 0.0
    return math.exp(-u * 9) * math.cos(2 * math.pi * freq * u)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


def hook_cam(t, hit):
    """Влёт (правила 28–29): 1/1.42 → 1.055 за 0.22 с, отскок к 1, поворот +3.6° → −1° → 0; второй удар +10 % на hit."""
    T = 0.22
    if t < T:
        u = t / T
        z = 1 / 1.42 + (1.055 - 1 / 1.42) * ease_out(u, 3)
        rot = 3.6 * (1 - ease_out(u, 2)) - 1.0 * ease_out(u, 2)
    else:
        u = t - T
        z = 1 + .055 * math.exp(-u * 9) * math.cos(2 * math.pi * 2.2 * u)
        rot = -1.0 * math.exp(-u * 7) * math.cos(2 * math.pi * 1.8 * u)
    z *= 1 + .10 * max(0.0, kick(t, hit, .5, 1.6))
    return z, rot


def blur_px(t):
    return 6.0 * (1 - smooth(0.0, 0.2, t))


# ═════════════════════════════ Дима на диване ═════════════════════════════
def dima(t, arms, hands=None, expr=None, lean=-0.42, head_ang=-0.22, hip=None, breath=0.0):
    lean = -0.42 if lean is None else lean
    h = HIP if hip is None else hip
    p = dict(hip=tuple(h), scale=BS, lean=lean + .012 * breath, feet={"n": ((520, 1478), 0.0), "f": ((486, 1468), 0.0)}, arms=arms,
             hands=hands or {}, expr=expr or {}, head_ang=head_ang, hood=0.0, strings=(1.5 * osc(t, 1.1), 1.2 * osc(t, .9, 1)))
    return people.draw(p, "dima")


def world_back(t):
    if "back" not in _ST:
        _ST["back"] = world.room_back(0) + world.sofa_back()
        _ST["seat"] = world.sofa_seat()
        lib.static_done()
    return _ST["back"]


def compose(inner, cam, blur=0.0, front=""):
    cx, cy, s, r = cam
    g = f'<g transform="{lib.cam(cx, cy, s, r)}">{inner}</g>'
    if blur > .05:
        fid = lib.uid("bl")
        lib.DEFS.append(f'<filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="{blur:.2f}"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    vg = lib.rad_grad([(0, "#0a0c1e", 0), (.62, "#0a0c1e", 0), (1, "#0a0c1e", .42)], 540, 900, 1180, 1400)
    return lib.svg(f'<rect width="1080" height="1920" fill="#2b2a3a"/>{g}{front}<rect width="1080" height="1920" fill="url(#{vg})"/>')


def dreamy_expr(t, smile=1.0, look=(.35, -.85), closed=0.0, mouth="smile", open_=0.0):
    return dict(lid=.42, look=look, brows="up", mouth=mouth, smile=smile, open=open_, closed=closed, blush=.55 * smile, hair=2 * osc(t, 1.2))


HN_REST = dict(kind="open", flip=1, dir=(.4, .9), curl=(.35, .4, .45, .5), spread=.1, thumb=.4, bend=.2)


def lazy_dima(t, expr, ha, br, hip=None, lean=-0.42, n_arm=None, n_hand=None):
    """Развалился: дальняя рука закинута за голову (кисть спрятана за затылком), ближняя лежит на животе."""
    probe = dima(t, {"n": ("ik", (440, 1120), -1), "f": ("ik", (300, 900), 1)}, {"f": dict(kind="none")}, expr, head_ang=ha, breath=br,
                 hip=hip, lean=lean)
    hx, hy = probe["head"]
    tgt = (hx - 58, hy - 10 + 3 * br)
    na = n_arm or ("ik", (440 + 6 * br, 1120 + 4 * br), -1)
    return dima(t, {"n": na, "f": ("ik", tgt, 1)}, {"n": n_hand or HN_REST, "f": dict(kind="none")}, expr, head_ang=ha, breath=br, hip=hip,
                lean=lean)


# ═════════════════════════════ s01 — хук ═════════════════════════════
CL01 = (690.0, 470.0)      # центр облака мечты (мир)


def s01(t):
    world_back(t)
    lib.dyn_begin()
    hit = T_MECH
    z, rot = hook_cam(t, hit)
    # Дима: дышит, мечтательно покачивает головой, улыбка шире к «мечтает»
    br = osc(t, .55)
    sm = .75 + .25 * smooth(T_VECH, hit, t)
    expr = dreamy_expr(t, sm, look=(.42 + .05 * osc(t, .7), -.9), closed=blink_at(t, .95, .16))
    ha = -.24 + .03 * osc(t, .8) - .04 * bump(t, hit, .4)
    d = lazy_dima(t, expr, ha, br)
    # пузыри мысли: три кружка вылетают из головы, облако растёт; на «мечтает» — раздувается до края кадра
    hx, hy = d["head"]
    puffs = []
    for k, (x, y, r, tk) in enumerate([(hx + 120, hy - 150, 22, -.25), (hx + 210, hy - 260, 34, -.12), (hx + 320, hy - 380, 50, .0)]):
        kk = back_out(clamp((t - tk) / .22), 2.0)
        if kk > .02:
            puffs.append(dream.puff(x + 4 * osc(t, .9, k), y + 5 * osc(t, 1.1, k), r * kk * (1 + .05 * osc(t, 1.6, k)), 4700 + k * 10, t))
    grow = .52 + .3 * ease_out(clamp(t / 1.2), 2)
    swell = back_out(clamp((t - (hit - .08)) / .3), 1.4)
    sc = grow + (1.9 - grow) * swell
    rx, ry = 300 * sc, 240 * sc
    pan = 30 * t
    inside = f'<g transform="scale(.6)">{dream.scene_inside(t, 1000, 760, pan)}</g>'
    cl = dream.cloud(t, 300, 240, inside, wob=.05, seed=4500)
    cx = CL01[0] + 40 * swell
    cy = CL01[1] + 60 * swell
    cloud = f'<g transform="translate({cx:.1f} {cy:.1f}) scale({sc:.4f}) rotate({1.5 * osc(t, .4):.2f})">{cl}</g>'
    pet = dream.petals(t, 14, (-200, 100, 1300, 1500), seed=4600, k=1.0)
    inner = (_ST["back"] + _ST["seat"] + d.get("legs", "") + d["arm_f"] + d["body"] + d["arm_n"] + world.evening_light(t)
             + "".join(puffs) + cloud + pet)
    # камера: влёт к Диме и облаку, потом медленный наезд к облаку
    k = ease_io(clamp((t - .2) / 1.4))
    s = 1.18 * z * (1 + .06 * k)
    cam = (520 + 70 * k + 20 * (1 - z), 860 - 120 * k - 30 * (1 - z), s, rot + .3 * osc(t, .5))
    set_ink(s)
    return compose(inner, cam, blur=blur_px(t))


# ═════════════════════════════ s04 — пунктирный билет, облако лопается на «нет» ═════════════════════════════
def ticket_d(w=250.0, h=128.0, r=16.0, notch=17.0):
    """Контур посадочного талона с центром (0, 0): скруглённые углы, полукруглые вырезы на коротких сторонах."""
    x0, y0, x1, y1 = -w / 2, -h / 2, w / 2, h / 2
    return (f"M{x0 + r} {y0} H{x1 - r} A{r} {r} 0 0 1 {x1} {y0 + r} V{-notch} A{notch} {notch} 0 0 0 {x1} {notch} V{y1 - r} "
            f"A{r} {r} 0 0 1 {x1 - r} {y1} H{x0 + r} A{r} {r} 0 0 1 {x0} {y1 - r} V{notch} A{notch} {notch} 0 0 0 {x0} {-notch} "
            f"V{y0 + r} A{r} {r} 0 0 1 {x0 + r} {y0} Z")


def plane_d(k=1.0):
    p = [(-34, 4), (-6, 2), (8, -26), (18, -26), (10, 2), (30, 2), (38, -10), (46, -10), (40, 6), (46, 22), (38, 22), (30, 10), (10, 10),
         (18, 38), (8, 38), (-6, 12), (-34, 10)]
    return "M" + " L".join(f"{x * k:.1f} {y * k:.1f}" for x, y in p) + " Z"


def ticket(x, y, rot, t, glow=0.0, k=1.0):
    """Пустой пунктирный билет: только штриховой контур (внутри пусто), перфорация, пунктирный самолётик.
    glow 0..1 — мигание на «билета»: штрихи бегут и вспыхивают жёлтым."""
    col = lib.mix("#fbf3df", "#ffd84a", glow)
    off = -t * 60
    sw = 7.0 + 2.5 * glow
    d = ticket_d()
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({k:.4f})">']
    for c, wdt in ((INK, sw + 5), (col, sw)):
        o.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{wdt:.1f}" stroke-dasharray="18 13" stroke-dashoffset="{off:.1f}" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(f'<line x1="62" y1="-50" x2="62" y2="50" stroke="{c}" stroke-width="{wdt * .7:.1f}" stroke-dasharray="7 10" '
                 f'stroke-dashoffset="{off * .5:.1f}" stroke-linecap="round"/>')
    o.append("</g>")
    return "".join(o)


def splash(cx, cy, e, seed=4800):
    """Облако лопнуло: белые клочья и капли разлетаются, штрихи «хлоп», лепестки падают."""
    if e < 0 or e > 0.8:
        return ""
    o = []
    rs = np.random.RandomState(seed)
    for j in range(16):
        a = rs.uniform(0, 2 * math.pi)
        sp = rs.uniform(260, 520)
        d = sp * (1 - math.exp(-e * 6)) / 6 * 4
        x = cx + math.cos(a) * (120 + d) * 1.25
        y = cy + math.sin(a) * (90 + d) + 260 * e * e
        r = rs.uniform(14, 34) * (1 - smooth(.35, .8, e))
        if r < 2:
            continue
        if j % 3 == 0:
            o.append(dream.puff(x, y, r * 1.3, seed + j * 7, e))
        else:
            o.append(shape(ellipse_pts(x, y, r * .55, r * .7, 10, rot=math.degrees(a) + 90), "#ffffff",
                           blob(ellipse_pts(x + r * .15, y + r * .25, r * .4, r * .4, 8), dream.CLOUD_SH, .9), w=3.4, seed=seed + 50 + j))
    u = clamp(e / .3)
    if u < 1:
        for j in range(10):
            a = 2 * math.pi * j / 10 + .2
            r0, r1 = 200 + 150 * ease_out(u), 250 + 230 * ease_out(u)
            o.append(line([(cx + math.cos(a) * r0 * 1.2, cy + math.sin(a) * r0), (cx + math.cos(a) * r1 * 1.2, cy + math.sin(a) * r1)],
                          9 * (1 - u) + 1.5, INK, seed=seed + 90 + j, taper=.3, wmin=.4))
    return "".join(o)


CL04 = (510.0, 520.0)


def s04(t):
    world_back(t)
    lib.dyn_begin()
    tn = T_NET
    e = t - tn
    deflate = ease_io(clamp((t - (tn + .12)) / .45))
    br = osc(t, .55)
    # глаза: в мечте вверх; на «нет» — моргнул (два раза) и смотрит перед собой растерянно
    bl = max(blink_at(t, tn + .1, .16), blink_at(t, tn + .42, .14))
    look = (.42 - .1 * deflate, -.9 + .9 * deflate)
    gape = 1 - deflate
    expr = dict(lid=.42 + .2 * deflate, look=look, brows="up" if deflate < .5 else "worry", mouth="laugh" if deflate < .5 else "flat",
                open=.35 + .1 * osc(t, .7) if deflate < .5 else 0.0, smile=1, closed=bl, blush=.5 * gape, hair=2 * osc(t, 1.2) + 6 * bump(t, tn, .3))
    hip = HIP + np.array([10.0, 14.0]) * deflate
    lean = -.42 - .1 * deflate
    ha = -.24 + .02 * osc(t, .8) + .2 * deflate
    # ближняя рука держит билет перед собой, после «нет» медленно опускается на живот
    up = np.array([470.0 + 4 * br, 960.0 + 3 * br])
    down = np.array([440.0, 1110.0])
    wr = up + (down - up) * deflate
    hn = dict(kind="open", flip=1, dir=(.55, -.83), curl=(.62, .7, .75, .8), spread=.04, thumb=.05, bend=.2)
    d = lazy_dima(t, expr, ha, br, hip=hip, lean=lean, n_arm=("ik", tuple(wr), -1), n_hand=hn)
    w0 = d["wrist"]["n"]
    gl = max(bump(t, T_BIL, .22), bump(t, T_BIL + .25, .22))
    tk = ticket(w0[0] + 118, w0[1] - 66, -10 + 4 * osc(t, .9) + 22 * deflate, t, glow=gl, k=.82 * (1 + .1 * gl))
    # облако: раздувается к «нет», хлоп — исчезает, клочья разлетаются
    swell = 1 + .12 * smooth(tn - .35, tn, t)
    cloud = ""
    if e < 0:
        inside = f'<g transform="scale(.6)">{dream.scene_inside(t, 1000, 760, 30 * t)}</g>'
        cl = dream.cloud(t, 300, 240, inside, wob=.05 + .1 * smooth(tn - .3, tn, t), seed=4500)
        cloud = (f'<g transform="translate({CL04[0]:.1f} {CL04[1]:.1f}) scale({.76 * swell:.4f}) rotate({1.5 * osc(t, .4) + 3 * osc(t, 7) * smooth(tn - .3, tn, t):.2f})">'
                 f'{cl}</g>')
        hx, hy = d["head"]
        for k, (dx, dy, r) in enumerate([(110, -150, 20), (180, -240, 30)]):
            cloud = dream.puff(hx + dx, hy + dy + 4 * osc(t, 1, k), r, 4700 + k * 10, t) + cloud
    sp = splash(CL04[0], CL04[1], e)
    pet = dream.petals(t, 9, (0, 200, 1100, 1400), seed=4620, k=1.0, wind=(-120, 160)) if e < .5 else ""
    inner = (_ST["back"] + _ST["seat"] + d.get("legs", "") + d["arm_f"] + d["body"] + tk + d["arm_n"] + world.evening_light(t)
             + cloud + sp + pet)
    u = clamp((t - 5.0) / 2.05)
    pk = kick(t, tn, .45, 2.0)
    s = (1.5 + .08 * ease_io(u)) * (1 + .06 * max(0.0, pk))
    sh = bump(t, tn, .3)
    cam = (390 - 15 * u + 6 * sh * osc(t, 15), 830 + 30 * u + 5 * sh * osc(t, 19, 1), s, -.6 + .8 * u + .8 * sh * osc(t, 11))
    set_ink(s)
    return compose(inner, cam)


SHOTS = {"s01": s01, "s04": s04}


def frame(sid, t):
    return SHOTS[sid](t)
