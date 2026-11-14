"""s01 (0.00–1.45, клип 0.00–1.65): хук. Вечер, прихожая. Дима с новой сумкой на плече вскидывает над головой
абонемент (рука уже летит вверх с кадра 0); на «абонемент» (0.76) — дожим рукой вверх, блик-звёздочка по карте, искры,
Дима сияет (улыбка во весь рот, глаза шире, тёплый свет). Камера — влёт правила 28–29 и удар +8 % на 0.76."""
import math

import numpy as np

import dima
import hall
import hero
import lib
from lib import clamp, ease_out, smooth

HIT = 0.76
HX = 110.0
BASE = (240.0, -470.0, 1.95, 0.0)
_C = {}


def hand_target(t):
    a = np.array([HX + 120, -470.0])
    b = np.array([HX + 66, -664.0])
    u = ease_out(t / 0.42, 2.4)
    p = a + (b - a) * u
    pump = 26 * smooth(HIT - 0.08, HIT, t) * math.exp(-4 * max(0, t - HIT))
    p[1] -= pump
    p[0] += 6 * math.sin(t * 9) * (1 - u) + 3 * math.sin(t * 6)
    return p


def held_card(t):
    def f(Wr, d):
        d = np.array(d, float) / np.linalg.norm(d)
        c = Wr + d * 150
        rot = -10 + 6 * math.sin(t * 7) * math.exp(-1.5 * t) + 5 * smooth(HIT - .06, HIT + .05, t) * math.exp(-5 * max(0, t - HIT))
        sh = clamp((t - HIT + 0.04) / 0.3) if t > HIT - 0.04 else 0.0
        _C["c"] = c
        _C["rot"] = rot
        return hero.card(c[0], c[1], w=290, rot=rot, shine=sh if 0 < sh < 1 else 0, seed=31, ink_w=10)
    return f


def pose(t):
    wow = smooth(HIT - 0.06, HIT + 0.06, t)
    bob = -8 * math.sin(math.pi * clamp(t / 0.3)) + 4 * math.sin(t * 5.5) - 10 * wow * math.exp(-5 * max(0, t - HIT))
    expr = dict(lid=0.72 + 0.28 * wow, look=(0.25, -0.75), brows="up", mouth="grin" if wow > .5 else "smile",
                hair=-10 * math.exp(-4 * t) * math.cos(t * 18) - 9 * wow * math.exp(-6 * max(0, t - HIT)) * math.cos((t - HIT) * 22))
    p = hero.stand(HX, HX - 40, HX + 34, dy=bob, lean=-0.06 - 0.03 * wow, expr=expr, head_ang=-0.16 - 0.04 * wow)
    fist = np.array([HX + 96, -400.0]) + np.array([0, -30.0]) * smooth(HIT - .08, HIT, t) * math.exp(-4 * max(0, t - HIT))
    fist += np.array([30 * (1 - ease_out(t / 0.3)), 60 * (1 - ease_out(t / 0.3))])
    p["arms"] = {"f": ("ik", hand_target(t), -1), "n": ("ik", fist, -1)}
    p["hands"] = {"n": "fist", "f": "fist"}
    p["held"] = ("behind", held_card(t))
    p["held_side"] = "f"
    sw = -40 * math.exp(-3 * t) * math.cos(t * 9) + 14 * wow * math.exp(-5 * max(0, t - HIT)) * math.sin((t - HIT) * 20)
    p["over_torso"] = hero.bag_on_shoulder(sw)
    p["hood"] = 8 * math.sin(t * 10) * math.exp(-3 * t)
    return p


def frame(t):
    lib.DEFS.clear()
    cam = hero.cam_hook(t, BASE, HIT)
    g, info = dima.draw(pose(t))
    mid = []
    wow = smooth(HIT - 0.06, HIT + 0.08, t)
    hd = info["head"]
    if wow > 0:
        gl = lib.rad_grad([(0, "#fff0b0", .55 * wow), (.5, "#ffd98a", .25 * wow), (1, "#ffd98a", 0)], hd[0], hd[1] - 60, 380)
        mid.append(f'<circle cx="{hd[0]:.1f}" cy="{hd[1] - 60:.1f}" r="380" fill="url(#{gl})"/>')
    mid.append(f'<ellipse cx="{HX:.1f}" cy="4" rx="150" ry="18" fill="#3a2418" opacity=".28"/>')
    mid.append(g)
    fg = []
    if "c" in _C:
        c = hero_world(_C["c"], pose(t))
        a = math.radians(_C["rot"])
        cx_, cy_ = c[0] + 40 * math.cos(a) * dima.BS * 2.2, c[1] + 40 * math.sin(a) * dima.BS * 2.2
        if t > HIT - 0.05:
            u = t - HIT
            r = 120 * math.sin(math.pi * clamp((u + 0.05) / 0.5)) + 34 * smooth(0.3, 0.6, u)
            fg.append(hero.star(cx_ + 20, cy_ - 30, r, 1.0, rot=u * 90))
            fg.append(hero.sparkles(c[0], c[1], t, HIT - 0.02, R=150, n=6, seed=5))
        else:
            fg.append(hero.star(cx_ + 20, cy_ - 30, 14 + 6 * math.sin(t * 14), .8, rot=t * 60))
    return hall.frame(t, cam=cam, mid="".join(mid), fg="".join(fg))


def hero_world(pL, p):
    return np.array(p["hip"], float) + np.array(pL) * dima.BS
