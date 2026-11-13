"""Сцена cafe рилса 27: планы s01–s05, s12–s15. frame(sid, t) -> SVG 1080×1920 (t — общее время ролика).

Мир столика — room.py (столик (540, 1150), лавка у стены, окно слева, полка справа); герои — people.py (Дима слева
лицом вправо, друг справа — отражён), кот — cat.py на лавке за столом. Хук s01 — вход: дверь, стойка с кофемашиной,
объятие (hug.py). Камера у каждого плана своя (CAM), движется с первого кадра; удары — на словах по voice/words.json.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cat as Cat  # noqa: E402
import hand as Hand  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import room  # noqa: E402
from lib import clamp, ease_io, ease_out, smooth  # noqa: E402

WORDS = json.load(open(os.path.join(os.path.dirname(HERE), "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["word"].strip(".,?!").lower() == word.lower() and w["start"] >= after:
            return w["start"]
    raise KeyError(word)


T_POLGODA = wt("полгода")          # 2.56
T_LEZHAL = wt("лежал")             # 4.32
T_SKLEILSYA = wt("склеился")       # 6.16
T_POCHEMU = wt("почему")           # 7.76
T_RYUKZAK = wt("рюкзак")           # 27.32
T_TELEFON2 = wt("телефон", 26)     # 26.84
T_HOHOCHUT = wt("хохочут")         # 30.08
T_KOT = wt("кот", 31)              # 31.12

BS = 0.6
D_HIP = np.array([250.0, 1262.0])
F_HIP = np.array([830.0, 1262.0])
F_K = 1.08
CAT_POS = (566.0, 1080.0, 0.55)
BP_POS = (452.0, 1080.0, 0.74)
CUP_D = (430.0, 1150.0, 0.8)
CUP_F = (668.0, 1146.0, 0.8)
PHONE = (548.0, 1176.0, 0.62)


def bump(t, t0, dur=.35):
    """0 → 1 → 0 (импульс)."""
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def osc(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def talk(t, t0, t1, rate=7.0):
    """Раскрытие рта для речи между t0 и t1 (слоги)."""
    if t < t0 or t > t1:
        return 0.0
    v = .5 + .5 * math.sin(2 * math.pi * rate * (t - t0)) * (.7 + .3 * math.sin(t * 3.1))
    return clamp(v * smooth(t0, t0 + .08, t) * (1 - smooth(t1 - .08, t1, t)))


# ═════════════════════════ камера и параллакс ═════════════════════════
def cam_tf(cam, p=1.0, anchor=(540.0, 1000.0)):
    cx, cy, s, r = cam
    ax, ay = anchor
    if p == 1.0:
        return lib.cam(cx, cy, s, r)
    sp = s ** p
    return lib.cam(ax + (cx - ax) * p, ay + (cy - ay) * p, sp, r)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


# ═════════════════════════ герои за столом ═════════════════════════
def mirror_pose(pose, hx):
    def mx(p):
        return (2 * hx - p[0], p[1])
    q = dict(pose)
    if pose.get("feet"):
        q["feet"] = {k: (mx(v[0]), v[1]) for k, v in pose["feet"].items()}
    arms = {}
    for k, a in pose["arms"].items():
        if a[0] == "ik":
            arms[k] = ("ik", mx(a[1])) + tuple(a[2:])
        else:
            arms[k] = a
    q["arms"] = arms
    hs = {}
    for k, h in pose.get("hands", {}).items():
        h = dict(h)
        if "dir" in h:
            h["dir"] = (-h["dir"][0], h["dir"][1])
        hs[k] = h
    q["hands"] = hs
    return q


def mirror_g(s, hx):
    return f'<g transform="translate({2 * hx:.2f} 0) scale(-1 1)">{s}</g>'


def draw_friend(pose):
    hx = pose["hip"][0]
    out = people.draw(mirror_pose(pose, hx), "friend")
    for k in ("legs", "arm_f", "body", "arm_n", "pelvis"):
        if k in out:
            out[k] = mirror_g(out[k], hx)
    out["wrist"] = {k: np.array([2 * hx - v[0], v[1]]) for k, v in out["wrist"].items()}
    out["elbow"] = {k: np.array([2 * hx - v[0], v[1]]) for k, v in out["elbow"].items()}
    out["head"] = np.array([2 * hx - out["head"][0], out["head"][1]])
    return out


def dima_seated(t, **kw):
    hip = D_HIP + np.array(kw.get("hip_off", (0, 0)))
    p = dict(hip=tuple(hip), scale=BS, lean=kw.get("lean", 0.1), feet={"n": ((470, 1468), 0.0), "f": ((445, 1462), 0.0)},
             arms=kw["arms"], hands=kw.get("hands", {}), expr=kw.get("expr", {}), head_ang=kw.get("head_ang", 0.0),
             hood=0.0, strings=kw.get("strings", (0, 0)))
    return people.draw(p, "dima")


def friend_seated(t, **kw):
    hip = F_HIP + np.array(kw.get("hip_off", (0, 0)))
    p = dict(hip=tuple(hip), scale=BS * F_K, lean=kw.get("lean", 0.08), torso_k=1.06, feet={"n": ((640, 1470), 0.0), "f": ((662, 1464), 0.0)},
             arms=kw["arms"], hands=kw.get("hands", {}), expr=kw.get("expr", {}), head_ang=kw.get("head_ang", 0.0))
    return draw_friend(p)


def grip_cup(cupc, side, who, k=1.0, far=False):
    """Пальцы на чашке: (задняя часть, передняя часть). cupc — (x, y, k) чашки."""
    x, y, ck = cupc
    people.C = people.PAL[who]
    kw = dict(shape_fn=people.shape, line_fn=people.line, skin=people.C["SKIN"], skin_sh=people.C["SKIN_SH"], skin_sh2=people.C["SKIN_SH2"])
    if far:
        kw.update(skin=people.far_c(people.C["SKIN"], True), skin_sh=people.far_c(people.C["SKIN_SH"], True))
    sc = BS * (F_K if who == "friend" else 1.0) * k
    old = people.LWK
    people.LWK = sc
    try:
        b, f = Hand.grip((x, y - 44 * ck), 40 * ck, side, k=sc, h=62, seed=2600 + (40 if far else 0), **kw)
    finally:
        people.LWK = old
    return b, f


def cup_wrist(cupc, side, who):
    x, y, ck = cupc
    sc = BS * (F_K if who == "friend" else 1.0)
    return (x + side * (40 * ck + 50 * sc), y - 44 * ck + 4)


# ═════════════════════════ сцена столика ═════════════════════════
def table_scene(t, cam, A):
    """A — словарь актёров на кадр: dima, friend (выход people.draw), cat (st), bp (рюкзак kwargs), cups
    (список (cupc, kwargs)), phone (kwargs), extra_front (svg поверх рук), grips."""
    set_ink(cam[2])
    o = []
    win = room.WIN
    w = []
    w.append(room.wall(t))
    clip = lib.clip_rect(win[0], win[1], win[2] - win[0], win[3] - win[1])
    dx, dy = (cam[0] - 540) * .28, (cam[1] - 1000) * .28
    w.append(f'<g clip-path="url(#{clip})"><g transform="translate({dx:.2f} {dy:.2f})">{room.street(t)}</g></g>')
    w.append(room.window_frame(t))
    w.append(room.pendant(t))
    w.append(room.floor())
    w.append(room.bench(t))
    bp = A.get("bp", {})
    w.append(room.backpack(BP_POS[0], BP_POS[1] - 30, BP_POS[2], **bp))
    if A.get("cat") is not None:
        cx, cy, ck = CAT_POS
        w.append(Cat.draw(cx, cy - 30, ck, A["cat"], t))
    w.append(A.get("behind_table", ""))
    d, f = A["dima"], A["friend"]
    w.append(room.chair(D_HIP[0], D_HIP[1] + 4, 1, 2300))
    w.append(room.chair(F_HIP[0], F_HIP[1] + 4, -1, 2320))
    w.append(d.get("legs", ""))
    w.append(f.get("legs", ""))
    w.append(room.table_leg())
    w.append(room.table_top())
    for cupc, kw in A.get("cups", []):
        w.append(room.cup(cupc[0], cupc[1], cupc[2], steam_t=t, **kw))
    if A.get("phone") is not None:
        w.append(room.phone(PHONE[0], PHONE[1], PHONE[2], **A["phone"]))
    w.append(A.get("on_table", ""))
    w.append(d["arm_f"] + f["arm_f"])
    w.append(A.get("grip_back", ""))
    w.append(d["body"] + f["body"])
    w.append(A.get("mid", ""))
    w.append(d["arm_n"] + f["arm_n"])
    w.append(A.get("grip_front", ""))
    w.append(A.get("extra_front", ""))
    o.append(f'<g transform="{cam_tf(cam)}">{"".join(w)}</g>')
    # гирлянда — чуть ближе стены (параллакс 1.08), передний план — 1.3
    o.append(f'<g transform="{cam_tf(cam, 1.0)}">{room.garland(t)}</g>')
    o.append(A.get("screen_front", ""))
    o.append(vignette())
    return lib.svg("".join(o))


def vignette():
    g = lib.rad_grad([(0, "#2a1408", 0), (.62, "#2a1408", 0), (1, "#2a1408", .42)], 540, 960, 1180, 1400)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


# ═════════════════════════ общие позы ═════════════════════════
def dima_cup(t, expr, head_ang=0.0, hip_off=(0, 0), lean=.12):
    """Дима держит свою чашку двумя руками."""
    wr = cup_wrist(CUP_D, -1, "dima")
    pd = dict(arms={"n": ("ik", wr), "f": ("ik", (wr[0] + 40, wr[1] - 30))}, hands={"n": dict(kind="none"), "f": dict(kind="none")},
              expr=expr, head_ang=head_ang, hip_off=hip_off, lean=lean)
    d = dima_seated(t, **pd)
    gb, gf = grip_cup(CUP_D, -1, "dima")
    return d, gb, room.cup(*CUP_D, steam_t=t) + gf


def friend_rest(t, expr, near=None, far=None, head_ang=0.0, hip_off=(0, 0), lean=.08, hn=None, hf=None):
    """Друг: ближняя рука по умолчанию лежит на столе у чашки, дальняя — на колене за столом."""
    near = near or (702, 1192)
    far = far or (730, 1150)
    pf = dict(arms={"n": ("ik", near), "f": ("ik", far)},
              hands={"n": hn or dict(kind="open", flip=-1, dir=(-1, .25), curl=(.25, .3, .35, .4), spread=.06, thumb=.5, bend=.12),
                     "f": hf or dict(kind="open", flip=-1, dir=(-1, .4), curl=(.3, .35, .4, .45), spread=.05, thumb=.6)},
              expr=expr, head_ang=head_ang, hip_off=hip_off, lean=lean)
    return friend_seated(t, **pf)


def cups_default():
    return [(CUP_F, dict(band_col="#c8642e", handle=-1))]


def blink_at(t, tb, dur=.16):
    return clamp(1 - abs(t - tb) / (dur / 2)) if abs(t - tb) < dur / 2 else 0.0


# ═════════════════════════ s02: садятся, друг жестикулирует, «полгода» — на пальцах ═════════════════════════
def s02(t):
    t0 = 1.24
    k = ease_io(clamp((t - t0) / 2.44))
    cam = (548, 1040 - 14 * k, 1.36 + .1 * k, .3 * osc(t, .3))
    set_ink(cam[2])
    u = clamp((t - t0) / 0.5)
    settle = 1 - math.exp(-6 * u) * math.cos(9 * u)
    hip_d = (0, -46 * (1 - settle))
    u2 = clamp((t - t0 - .08) / 0.5)
    hip_f = (0, -52 * (math.exp(-6 * u2) * math.cos(9 * u2)) * (u2 < 1))
    tp = T_POLGODA
    g = smooth(tp - .34, tp - .04, t)
    wave = osc(t, 1.7)
    n_free = (690 - 30 * wave, 1030 - 40 * abs(osc(t, 1.7, .6)))
    f_free = (880 + 20 * osc(t, 1.3), 1000 - 40 * osc(t, 2.1))
    n_t = (n_free[0] * (1 - g) + 686 * g, n_free[1] * (1 - g) + 1010 * g)
    f_t = (f_free[0] * (1 - g) + 892 * g, f_free[1] * (1 - g) + 880 * g)
    pop = bump(t, tp - .04, .3)
    n_t = (n_t[0], n_t[1] - 18 * pop)
    f_t = (f_t[0], f_t[1] - 24 * pop)
    open_ = talk(t, 1.5, 3.12, 6.5)
    pf = dict(arms={"n": ("ik", n_t), "f": ("ik", f_t)},
              hands={"n": dict(kind="open", flip=-1, dir=(-.35 * (1 - g) - .1, -1), curl=(.1 * (1 - g),) * 4, spread=.12 + .3 * g, thumb=.15),
                     "f": dict(kind="open", flip=-1, dir=(.15, -1), curl=(.05, .2 + .75 * g, .2 + .75 * g, .2 + .75 * g), spread=.08, thumb=.25 + .7 * g)},
              expr=dict(lid=.9, look=(.45, -.05), brows="up", mouth="talk" if t < 3.15 else "grin", open=open_ if t < 3.15 else .7, smile=.9),
              head_ang=-.05 * osc(t, 2.3), hip_off=hip_f, lean=.05)
    f = friend_seated(t, **pf)
    d, gb, gf = dima_cup(t, dict(lid=.65, look=(.5, -.08), brows="up", mouth="grin", hair=5 * math.exp(-4 * u) * osc(t, 3)),
                         head_ang=.04 * osc(t, 1.4), hip_off=hip_d)
    A = dict(dima=d, friend=f, cat=dict(look=(.5, -.1), tail=4 * osc(t, .5), turn=.25), cups=cups_default(), phone=dict(),
             grip_back=gb, grip_front=gf)
    return table_scene(t, cam, A)


# ═════════════════════════ s03: крупно стол, телефон; «лежал» — наезд-удар, телефон дрожит и светится краем ═════════════════════════
def s03(t):
    tl = T_LEZHAL
    pre = ease_io(clamp((t - 3.28) / (tl - 3.28)))
    hit = ease_out(clamp((t - tl + .02) / .16), 3)
    ov = bump(t, tl + .12, .32) * .06
    z = 2.35 + .18 * pre + .75 * hit - ov
    sh = bump(t, tl, .3)
    cam = (PHONE[0] - 6 + 4 * sh * osc(t, 13), PHONE[1] - 30 + 10 * (1 - hit) + 3 * sh * osc(t, 17, 1), z, -1.2 * (1 - pre) + 1.4 * sh * osc(t, 9))
    set_ink(cam[2])
    buzz_k = smooth(tl - .05, tl + .02, t) * (1 - smooth(tl + .75, tl + 1.0, t))
    buzz = (3.2 * buzz_k * osc(t, 23), 1.4 * buzz_k * osc(t, 31, .7))
    glow = buzz_k * (.65 + .35 * abs(osc(t, 3.5)))
    d, gb, gf = dima_cup(t, dict(lid=.6, look=(.5, .3), brows="calm", mouth="smile", smile=.6))
    f = friend_rest(t, dict(lid=.8, look=(.45, .0), brows="up", mouth="talk", open=talk(t, 3.3, 5.4, 6), smile=.7),
                    near=(712 + 6 * osc(t, .9), 1196), hn=dict(kind="open", flip=-1, dir=(-1, .22), curl=(.15 + .1 * osc(t, 1.1), .25, .3, .38),
                                                             spread=.08, thumb=.4, bend=.1))
    A = dict(dima=d, friend=f, cat=dict(look=(.1, .6), tail=3 * osc(t, .5)), cups=cups_default(), phone=dict(glow=glow, buzz=buzz),
             grip_back=gb, grip_front=gf)
    if buzz_k > .05:
        A["on_table"] = buzz_lines(PHONE[0] + buzz[0], PHONE[1] + buzz[1], buzz_k, t)
    return table_scene(t, cam, A)


def buzz_lines(x, y, k, t):
    o = []
    for sx in (-1, 1):
        for j in range(2):
            ph = (t * 6 + j * .5) % 1
            r = 110 + 26 * j + 14 * ph
            a = (1 - ph) * k
            pts = [(x + sx * r * .78, y - 34), (x + sx * (r + 6), y - 4), (x + sx * r * .82, y + 26)]
            o.append(lib.line(pts, 4.0, "#2a2228", seed=3000 + j + (sx > 0) * 5, op=.85 * a, taper=.4, wmin=.3))
    return "".join(o)


# ═════════════════════════ s04: разговор вянет; «склеился» — улыбка друга гаснет; кот смотрит ═════════════════════════
def s04(t):
    k = (t - 4.92) / 2.64
    cam = (552 + 26 * k, 1020 - 8 * k, 1.42 + .05 * k, .25 * osc(t, .25))
    set_ink(cam[2])
    ts = T_SKLEILSYA
    fade = smooth(ts - .1, ts + .45, t)
    op = talk(t, 5.0, ts - .05, 5.5) * (1 - fade)
    # друг рассказывает, жесты стихают; к «склеился» рука падает на стол
    g = 1 - smooth(5.6, ts, t)
    near = (660 - 26 * g * osc(t, 1.4), 1186 - 150 * g * (.6 + .4 * abs(osc(t, 1.4, .4))))
    f = friend_rest(t, dict(lid=.8 - .2 * fade, look=(.45, .05 + .1 * fade), brows="up" if fade < .5 else "calm",
                            mouth="talk" if fade < .5 else "flat", open=op, smile=.7 * (1 - fade)),
                    near=near, hn=dict(kind="open", flip=-1, dir=(-1, .25 - .9 * g), curl=(.2 * (1 - g) + .05,) * 4, spread=.08 + .14 * g, thumb=.4),
                    head_ang=.03 * osc(t, 1.1) * (1 - fade), lean=.08 - .03 * fade)
    # Дима кивает, но косит на телефон
    glance = smooth(5.3, 5.5, t) * (1 - smooth(5.9, 6.05, t)) + smooth(6.35, 6.55, t)
    nod = .05 * osc(t, 1.6) * (1 - smooth(6.3, 6.6, t))
    d, gb, gf = dima_cup(t, dict(lid=.55, look=(.45 - .1 * glance, -.02 + .75 * glance), brows="calm", mouth="smile" if fade < .6 else "flat",
                                 smile=.6 * (1 - fade)), head_ang=nod + .06 * glance)
    cl = (.5 - 1.0 * smooth(5.7, 5.95, t) + .6 * smooth(6.5, 6.8, t), .1 + .2 * smooth(6.5, 6.8, t))
    A = dict(dima=d, friend=f, cat=dict(look=cl, tail=4 * osc(t, .45), turn=.25 - .5 * smooth(5.7, 5.95, t) + .4 * smooth(6.5, 6.8, t),
                                        blink=blink_at(t, 6.98)),
             cups=cups_default(), phone=dict(), grip_back=gb, grip_front=gf)
    return table_scene(t, cam, A)


# ═════════════════════════ s05: крупно кот, смотрит в камеру; «почему» — наклон головы ═════════════════════════
def cat_face():
    x, y, k = CAT_POS
    return x, y - 30 + (1072 - 1306) * k


def s05(t):
    fx, fy = cat_face()
    k = clamp((t - 7.16) / 3.72)
    z = 4.1 + .4 * ease_io(k)
    cam = (fx + 14 - 10 * k, fy + 70, z, -.4 + .8 * k)
    set_ink(cam[2])
    tp = T_POCHEMU
    tilt = 11 * (1 - math.exp(-7 * max(0, t - tp + .06)) * math.cos(10 * max(0, t - tp + .06))) * (t > tp - .06)
    tilt *= 1 - .35 * smooth(9.4, 10.2, t)
    st = dict(look=(.06 * osc(t, .3), .05), tilt=tilt, ear=10 * bump(t, 8.9, .25) - 8 * bump(t, 9.05, .25), tail=5 * osc(t, .45),
              blink=blink_at(t, 9.62, .2), perk=.4 * bump(t, tp, .8), flame_e=1.2)
    d, gb, gf = dima_cup(t, dict(lid=.5, look=(.3, .6), brows="calm", mouth="flat"))
    f = friend_rest(t, dict(lid=.6, look=(.4, .2), brows="calm", mouth="flat"))
    A = dict(dima=d, friend=f, cat=st, cups=cups_default(), phone=dict(), grip_back=gb, grip_front=gf)
    return table_scene(t, cam, A)


# ═════════════════════════ s12: Дима берёт телефон и убирает в рюкзак («рюкзак»), застёгивает, поворачивается к другу ═════════════════════════
BP_MOUTH = (BP_POS[0], BP_POS[1] - 30 - 168 * BP_POS[2])


def s12(t):
    k = clamp((t - 24.52) / 3.72)
    cam = (470 + 30 * ease_io(k), 1030 - 20 * ease_io(k), 1.42 + .2 * ease_io(k), .3 * osc(t, .3))
    set_ink(cam[2])
    tr = T_RYUKZAK
    # фазы ближней руки: от чашки к телефону, взял, поднёс к рюкзаку, опустил внутрь, застегнул, вернулся к чашке
    cupw = np.array(cup_wrist(CUP_D, -1, "dima"))
    ph_w = np.array([PHONE[0] - 70, PHONE[1] - 6])
    above = np.array([BP_MOUTH[0] + 22, BP_MOUTH[1] - 50])
    bpx, bpy, bpk = BP_POS[0], BP_POS[1] - 30, BP_POS[2]
    t_grab, t_lift = 25.15, 26.5
    t_zip0, t_zip1 = tr + .2, tr + .62
    near_mouth = above + np.array([-4, 26])
    zw = lambda zu: room.zip_pos(bpx, bpy, bpk, zu) + np.array([50, 16])  # noqa: E731
    if t < t_grab:
        u = ease_io(clamp((t - 24.6) / (t_grab - 24.6)))
        w = cupw + (ph_w - cupw) * u
        hold = False
    elif t < t_lift:
        u = clamp((t - t_grab) / (t_lift - t_grab))
        mid = ph_w + np.array([-10, -110])
        w = ph_w + (mid - ph_w) * ease_io(u / .55) if u < .55 else mid + (above - mid) * ease_io((u - .55) / .45)
        hold = True
    elif t < tr:
        u = ease_io(clamp((t - t_lift) / (tr - t_lift)))
        w = above + (near_mouth - above) * u
        hold = True
    elif t < t_zip0:
        u = ease_io(clamp((t - tr) / (t_zip0 - tr)))
        w = near_mouth + (zw(0) - near_mouth) * u
        hold = False
    elif t < t_zip1:
        u = ease_io(clamp((t - t_zip0) / (t_zip1 - t_zip0)))
        w = zw(u)
        hold = False
    else:
        u = ease_io(clamp((t - t_zip1) / .45))
        w = zw(1) + (cupw - zw(1)) * u
        hold = False
    zip_u = 0.0 if t < t_zip0 else ease_io(clamp((t - t_zip0) / (t_zip1 - t_zip0)))
    to_friend = smooth(t_zip1, t_zip1 + .35, t)
    look_bp = smooth(25.9, 26.3, t) * (1 - to_friend)
    expr = dict(lid=.6 + .2 * to_friend, look=(.35 + .15 * to_friend - .35 * look_bp, .55 * (1 - look_bp - to_friend) + .1 - .5 * look_bp),
                brows="calm" if to_friend < .5 else "up", mouth="smile", smile=.4 + .6 * to_friend)
    d_hand = dict(kind="open", dir=(1, -.2) if not hold else (1, .1), curl=(.55, .6, .65, .7) if hold else (.2, .25, .3, .35), spread=.05,
                  thumb=.75 if hold else .3)
    if t_zip0 - .1 < t < t_zip1 + .1:       # пальцы тянут бегунок: щепоть
        d_hand = dict(kind="open", dir=(-1, .2), flip=-1, curl=(.35, .75, .85, .9), spread=.03, thumb=.85)
    farw = (cupw[0] + 40, cupw[1] - 30)
    pd = dict(arms={"n": ("ik", tuple(w), -1), "f": ("ik", farw)}, hands={"n": d_hand, "f": dict(kind="none")},
              expr=expr, head_ang=-.08 * look_bp + .05 * to_friend, lean=.12 - .04 * look_bp)
    d = dima_seated(t, **pd)
    gb, gf = grip_cup(CUP_D, -1, "dima", far=True)
    gb, gf = (gb, room.cup(*CUP_D, steam_t=t) + gf)
    f = friend_rest(t, dict(lid=.8, look=(.45 - .2 * look_bp, .1), brows="up", mouth="grin" if to_friend > .3 else "smile", open=.4, smile=.8),
                    head_ang=.02 * osc(t, .8))
    A = dict(dima=d, friend=f, cat=dict(look=(.2 - .7 * look_bp, .3 - .3 * look_bp), tail=4 * osc(t, .45), turn=-.4 * look_bp,
                                        blink=blink_at(t, 24.9)),
             cups=cups_default(), grip_back=gb, grip_front=gf, bp=dict(open_=1 - zip_u, zip_u=zip_u))
    wr = d["wrist"]["n"]
    if t < t_grab:
        A["phone"] = dict()
    elif t < tr + .02:
        A["phone"] = None
        A["mid"] = held_phone(wr, t, smooth(t_grab, t_grab + .6, t))
    else:
        A["phone"] = None
        drop = clamp((t - tr - .02) / .2)
        if drop < 1:
            A["behind_table"] = phone_drop(drop)
    return table_scene(t, cam, A)


def held_phone(wr, t, u):
    """Телефон в руке: от «лежит на столе» к «стоит в пальцах» (поворот и подъём плоскости), тот же рисунок."""
    k = PHONE[2] * (1 - .25 * u)
    return room.phone(wr[0] + 44 + 6 * u, wr[1] + 6 - 30 * u, k, ang=-24 - 56 * u, squash=.42 + .5 * u)


def phone_drop(u):
    x, y = BP_MOUTH[0] + 14, BP_MOUTH[1] - 50 + 90 * u * u
    clip = lib.clip_rect(x - 120, y - 400, 240, BP_MOUTH[1] + 8 - (y - 400))
    return f'<g clip-path="url(#{clip})">{room.phone(x, y, PHONE[2] * .75, ang=-80, squash=.92)}</g>'


def backpack_lip(t):
    """Передняя стенка рюкзака ниже горловины — поверх кисти, опущенной внутрь."""
    x, y, k = BP_POS[0], BP_POS[1] - 30, BP_POS[2]
    clip = lib.clip_of([(x - 90 * k, y - 146 * k), (x - 30 * k, y - 160 * k), (x, y - 164 * k), (x + 30 * k, y - 160 * k), (x + 90 * k, y - 146 * k),
                        (x + 90 * k, y + 10), (x - 90 * k, y + 10)])
    return f'<g clip-path="url(#{clip})">{room.backpack(x, y, k, open_=1.0, zip_u=0.0)}</g>'


# ═════════════════════════ s13: друг рассказывает, размахивая руками; «хохочут» — оба смеются до слёз ═════════════════════════
def s13(t):
    th = T_HOHOCHUT
    lg = smooth(th - .2, th + .15, t)
    shake = lg * osc(t, 7.5)
    k = clamp((t - 27.84) / 3.36)
    hitz = .05 * bump(t, th, .3)
    cam = (548 + 10 * k, 1030 - 10 * k + 4 * shake, 1.42 + .1 * ease_io(k) + hitz, .3 * osc(t, .3) + .5 * shake * lg)
    set_ink(cam[2])
    tears = smooth(th + .2, th + .9, t)
    # друг: рассказ, руки широко; на смехе — ладонь к груди, другая хлопает по столу
    sw = osc(t, 1.25)
    near_story = (650 - 40 * sw, 980 - 70 * abs(osc(t, 1.25, .5)))
    far_story = (900 + 30 * sw, 920 - 50 * osc(t, 1.8))
    near_l = (700, 1060 + 10 * shake)
    slap = bump(t, th + .02, .22)
    far_l = (640, 1170 - 60 * (1 - slap) * lg * abs(osc(t, 3.5)))
    near = tuple(np.array(near_story) * (1 - lg) + np.array(near_l) * lg)
    far = tuple(np.array(far_story) * (1 - lg) + np.array((740, 1080)) * lg)
    f = friend_rest(t, dict(lid=.9, look=(.45, -.05), brows="up", mouth="talk" if lg < .5 else "laugh", open=talk(t, 28.0, th, 6.5) if lg < .5 else
                            .8 + .2 * osc(t, 7.5), smile=1.0, laugh=lg, tears=tears),
                    near=near, far=far, head_ang=-.05 * osc(t, 1.25) * (1 - lg) - .12 * lg + .03 * shake, hip_off=(0, 6 * shake),
                    hn=dict(kind="open", flip=-1, dir=(-.5 + .5 * lg, -1 + 1.4 * lg), curl=(.05 + .3 * lg,) * 4, spread=.3 * (1 - lg) + .08, thumb=.2),
                    hf=dict(kind="open", flip=-1, dir=(.2, -1), curl=(.05,) * 4, spread=.3, thumb=.15), lean=.06 - .05 * lg)
    # Дима: смеётся, на «хохочут» хлопает ладонью по столу (чашки подпрыгивают)
    slap_d = bump(t, th, .26)
    dn = (390 + 10 * lg, 1196 - 70 * lg * (1 - slap_d) * (.5 + .5 * abs(osc(t, 3.5, .5))))
    expr = dict(lid=.7, look=(.5, -.1), brows="up", mouth="grin" if lg < .5 else "laugh", open=.9, laugh=lg, tears=tears * .9,
                hair=8 * shake * lg)
    wr = cup_wrist(CUP_D, -1, "dima")
    pd = dict(arms={"n": ("ik", dn), "f": ("ik", (wr[0] + 40, wr[1] - 30))},
              hands={"n": dict(kind="open", dir=(1, .25), curl=(.12, .15, .2, .25), spread=.1, thumb=.35), "f": dict(kind="none")},
              expr=expr, head_ang=-.16 * lg + .04 * shake, hip_off=(0, 5 * shake), lean=.12 - .08 * lg)
    d = dima_seated(t, **pd)
    gb, gf = grip_cup(CUP_D, -1, "dima", far=True)
    jump = 8 * bump(t, th + .03, .2)
    cupd = (CUP_D[0], CUP_D[1] - jump, CUP_D[2])
    A = dict(dima=d, friend=f, cat=dict(look=(.5 * osc(t, .4), .0), tail=6 * osc(t, .6), turn=.2 * osc(t, .4), smile=1 if lg > .5 else 0),
             cups=[(CUP_F, dict(band_col="#c8642e", handle=-1))], phone=None, grip_back=gb, grip_front=room.cup(*cupd, steam_t=t) + gf)
    A["cups"] = [((CUP_F[0], CUP_F[1] - jump * .7, CUP_F[2]), dict(band_col="#c8642e", handle=-1))]
    return table_scene(t, cam, A)


# ═════════════════════════ s14: кот поворачивает голову к ним и слушает, уши торчком («кот») ═════════════════════════
def s14(t):
    fx, fy = cat_face()
    k = clamp((t - 30.8) / 2.0)
    cam = (fx + 30 - 16 * k, fy + 90, 1.9 + .12 * ease_io(k), -.3 + .5 * k)
    set_ink(cam[2])
    tk = T_KOT
    turn = smooth(tk - .1, tk + .3, t)
    perk = 1 - math.exp(-8 * max(0, t - tk)) * math.cos(12 * max(0, t - tk)) if t > tk else 0
    lg = .85 + .15 * osc(t, 7.5)
    shake = osc(t, 7.5)
    f = friend_rest(t, dict(lid=.9, look=(.45, -.05), brows="up", mouth="laugh", open=.7 + .2 * shake, laugh=.9, tears=1, smile=1),
                    near=(700, 1060 + 8 * shake), far=(740, 1080), head_ang=-.1 + .03 * shake, hip_off=(0, 5 * shake),
                    hn=dict(kind="open", flip=-1, dir=(0, .4), curl=(.35,) * 4, spread=.08, thumb=.2))
    d, gb, gf = dima_cup(t, dict(lid=.7, look=(.5, -.1), brows="up", mouth="laugh", open=.8, laugh=lg, tears=.9, hair=6 * shake),
                         head_ang=-.12 + .04 * shake, hip_off=(0, 4 * shake))
    A = dict(dima=d, friend=f, cat=dict(turn=.75 * turn, look=(.9 * turn, -.1 * turn), perk=clamp(perk), tail=5 * osc(t, .5),
                                        tilt=-4 * turn, ear=4 * bump(t, 32.0, .25)),
             cups=cups_default(), phone=None, grip_back=gb, grip_front=gf)
    return table_scene(t, cam, A)


# ═════════════════════════ s15: крупно кот смотрит в камеру и медленно моргает; рядом рюкзак ═════════════════════════
def s15(t):
    fx, fy = cat_face()
    k = clamp((t - 32.4) / 3.9)
    cam = (fx - 70 + 20 * ease_io(k), fy + 70, 2.55 + .3 * ease_io(k), .4 - .6 * k)
    set_ink(cam[2])
    tb = 34.25
    if t < tb:
        bl = smooth(tb - .45, tb, t)
    else:
        bl = 1 - smooth(tb + .35, tb + .85, t)
    turn = .5 * (1 - smooth(32.5, 32.95, t))
    st = dict(turn=turn, look=(.6 * turn, 0), blink=bl * .999, tail=5 * osc(t, .4), smile=1 if t > tb + .5 else 0, tilt=3 * smooth(34.6, 35.4, t),
              ear=7 * bump(t, 35.6, .25), flame_e=1.1)
    shake = osc(t, 6)
    d, gb, gf = dima_cup(t, dict(lid=.7, look=(.5, -.05), brows="up", mouth="grin", open=.6, hair=2 * shake), head_ang=.02 * shake)
    f = friend_rest(t, dict(lid=.85, look=(.45, 0), brows="up", mouth="talk", open=talk(t, 32.4, 36.3, 5.5), smile=.9),
                    near=(650 + 20 * osc(t, .8), 1040 - 40 * abs(osc(t, .8, .3))),
                    hn=dict(kind="open", flip=-1, dir=(-.4, -1), curl=(.1,) * 4, spread=.25, thumb=.2))
    A = dict(dima=d, friend=f, cat=st, cups=cups_default(), phone=None, grip_back=gb, grip_front=gf, bp=dict(open_=0, zip_u=1))
    return table_scene(t, cam, A)


SHOTS = {"s02": s02, "s03": s03, "s04": s04, "s05": s05, "s12": s12, "s13": s13, "s14": s14, "s15": s15}


def frame(sid, t):
    lib.DEFS.clear()
    lib.INK_K[0] = 1.0
    return SHOTS[sid](t)
