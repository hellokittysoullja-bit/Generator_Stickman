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
CAT_POS = (570.0, 1080.0, 0.55)
BP_POS = (430.0, 1080.0, 0.78)
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
    people.LWK = 1.0 / sc
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
    lib.DEFS.clear()
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
