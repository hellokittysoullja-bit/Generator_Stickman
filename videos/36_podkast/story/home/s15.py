"""s15 (26.20–28.15, клип 26.00–28.35): вечер, прихожая. Телефон Димы стоит на полочке у двери; на «серия» (26.64)
телефон дрожит и на экране выскакивает уведомление (кружок с треугольником «играть» и микрофон, без букв), экран
светит; Дима слева расплывается в улыбке; на «ждёт» (27.04) нагибается и подхватывает сумку с пола,
шагает к двери; на «зале» (27.72) бодро распахивает дверь — с площадки свет. Камера — лёгкий наезд и толчок на
«серия», потом отъезд к двери."""
import math

import numpy as np

import dima
import hall
import hero
import lib
from lib import INK, back_out, clamp, ease_in, ease_io, ease_out, smooth

T_A, T_B = 26.00, 28.35
T_NOTE, T_BAG, T_DOOR = 26.64, 27.04, 27.72
PH = np.array([200.0, hall.SHELF[1]])        # низ телефона на полочке
BAG0 = np.array([88.0, -40.0])


def phone(t):
    """Телефон стоит на полке, прислонён к стене; уведомление на экране."""
    x, y = PH
    buzz = 3.0 * math.sin(t * 95) * smooth(T_NOTE - 0.12, T_NOTE - 0.08, t) * (1 - smooth(T_NOTE + 0.1, T_NOTE + 0.2, t))
    x += buzz
    w, h = 64.0, 118.0
    o = []
    lit = smooth(T_NOTE - 0.04, T_NOTE + 0.04, t)
    if lit > 0:
        gl = lib.rad_grad([(0, "#bfe3ff", .55 * lit), (1, "#bfe3ff", 0)], x, y - h / 2, 190)
        o.append(f'<circle cx="{x:.1f}" cy="{y - h / 2:.1f}" r="190" fill="url(#{gl})"/>')
    body = lib.rect_pts(x - w / 2, y - h, x + w / 2, y, 10)
    scr = lib.rect_pts(x - w / 2 + 6, y - h + 10, x + w / 2 - 6, y - 10, 5)
    scol = lib.mix("#1d2130", "#2e4a7a", lit)
    inner = f'<path d="{lib.fill_d(scr)}" fill="{scol}"/>'
    if lit > 0:
        # обложка подкаста: микрофон
        cx, cy = x, y - h * 0.62
        inner += f'<path d="{lib.fill_d(lib.rect_pts(cx - 20, cy - 22, cx + 20, cy + 22, 6))}" fill="#f08a2c" opacity="{lit:.2f}"/>'
        inner += f'<rect x="{cx - 6:.1f}" y="{cy - 16:.1f}" width="12" height="20" rx="6" fill="#ffffff" opacity="{lit:.2f}"/>'
        inner += (f'<path d="M{cx - 11:.1f} {cy - 2:.1f} Q{cx - 11:.1f} {cy + 11:.1f} {cx:.1f} {cy + 11:.1f} Q{cx + 11:.1f} {cy + 11:.1f} {cx + 11:.1f} {cy - 2:.1f}" '
                  f'fill="none" stroke="#ffffff" stroke-width="3" opacity="{lit:.2f}"/>'
                  f'<rect x="{cx - 1.5:.1f}" y="{cy + 11:.1f}" width="3" height="7" fill="#ffffff" opacity="{lit:.2f}"/>')
        # кнопка «играть»
        px, py = x, y - h * 0.27
        inner += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="11" fill="#ffffff" opacity="{lit:.2f}"/>'
        inner += f'<path d="M{px - 3.5:.1f} {py - 6:.1f}L{px + 6:.1f} {py:.1f}L{px - 3.5:.1f} {py + 6:.1f}Z" fill="#2e4a7a" opacity="{lit:.2f}"/>'
    inner += lib.blob([(x - w / 2, y - h), (x - w / 2 + 18, y - h), (x - w / 2 + 4, y), (x - w / 2, y)], "#ffffff", .08)
    o.append(lib.shape(body, "#22242c", inner, w=3.4, seed=8001))
    if 0 < abs(buzz) or (T_NOTE - 0.12 < t < T_NOTE + 0.2):
        a = math.sin(math.pi * clamp((t - T_NOTE + 0.12) / 0.32))
        for j, sx in enumerate((-1, 1)):
            for k in range(2):
                xx = x + sx * (w / 2 + 12 + k * 12)
                o.append(lib.line([(xx, y - h * .7 + k * 6), (xx + sx * 4, y - h * .5), (xx, y - h * .3 - k * 6)], 3.2, INK, seed=8010 + j * 3 + k,
                                  op=.9 * a))
    return "".join(o)


def bubble(t):
    """Уведомление-пузырь над телефоном (выскакивает на «серия»): кружок с «играть» и значок микрофона."""
    u = t - T_NOTE
    if u < -0.02:
        return ""
    sc = back_out(clamp(u / 0.22), 2.4) * (1 - ease_in(clamp((t - 27.12) / 0.16), 2))
    if sc <= 0.01:
        return hero.sparkles(PH[0], PH[1] - 210, t, T_NOTE, R=150, n=5, seed=9) if t < T_NOTE + 0.7 else ""
    fade = 1.0
    x, y = PH[0], PH[1] - 118 - 92 + 4 * math.sin(t * 5)
    o = []
    o.append(lib.shape(lib.rect_pts(-92, -44, 92, 44, 30), "#ffffff",
                       lib.blob([(-92, 14), (92, 14), (92, 44), (-92, 44)], "#e4ecf4", .9), w=4.0, seed=8101))
    o.append(lib.shape([(-14, 40), (14, 40), (0, 64, 1)], "#ffffff", "", w=3.6, seed=8102))
    o.append(lib.blob([(-14, 36), (14, 36), (12, 46), (-12, 46)], "#ffffff"))
    o.append(f'<circle cx="-42" cy="0" r="27" fill="#2fb3a8"/><circle cx="-42" cy="0" r="27" fill="none" stroke="{INK}" stroke-width="3"/>')
    o.append('<path d="M-51 -13L-27 0L-51 13Z" fill="#ffffff"/>')
    mx = 38
    o.append(f'<rect x="{mx - 11}" y="-26" width="22" height="34" rx="11" fill="#f08a2c" stroke="{INK}" stroke-width="3"/>')
    o.append(f'<path d="M{mx - 19} -2 Q{mx - 19} 20 {mx} 20 Q{mx + 19} 20 {mx + 19} -2" fill="none" stroke="{INK}" stroke-width="3.4"/>')
    o.append(f'<rect x="{mx - 2}" y="20" width="4" height="10" fill="{INK}"/><rect x="{mx - 10}" y="29" width="20" height="4" rx="2" fill="{INK}"/>')
    g = "".join(o)
    sp = hero.sparkles(x, y, t, T_NOTE, R=150, n=5, seed=9)
    return sp + f'<g opacity="{fade:.3f}" transform="translate({x:.1f} {y:.1f}) scale({max(sc, .01):.4f})">{g}</g>'


def pose(t):
    happy = smooth(T_NOTE + 0.02, T_NOTE + 0.15, t)
    dip = smooth(T_BAG - 0.12, T_BAG, t) * (1 - smooth(T_BAG + 0.04, T_BAG + 0.24, t))
    walk = ease_io((t - 27.28) / 0.36)
    hx = -30 + 182 * walk
    un = clamp((t - 27.28) / 0.22)
    uf = clamp((t - 27.42) / 0.22)
    nx = 0 + 120 * ease_io(un)
    fx = -62 + 220 * ease_io(uf)
    ny = -hero.SOLE - 30 * math.sin(math.pi * un)
    fy = -hero.SOLE - 26 * math.sin(math.pi * uf)
    expr = dict(lid=0.5 + 0.45 * happy, look=(0.55, -0.15 + 0.1 * dip), brows="up" if happy > .5 else "calm",
                mouth="grin" if happy > .5 else "flat",
                hair=-10 * happy * math.exp(-6 * max(0, t - T_NOTE - .05)) * math.cos((t - T_NOTE) * 24) + 6 * math.sin(math.pi * un))
    bob = -8 * math.sin(math.pi * un) - 6 * math.sin(math.pi * uf)
    p = hero.stand(hx, fx, nx, dy=bob + 64 * dip, lean=0.04 + 0.5 * dip + 0.08 * walk * (1 - smooth(T_DOOR, T_DOOR + .2, t)), expr=expr,
                   head_ang=-0.05 * happy - 0.25 * dip)
    p["feet"] = {"f": (np.array([fx, fy]), 0.2 * math.sin(math.pi * uf)), "n": (np.array([nx, ny]), 0.2 * math.sin(math.pi * un))}
    # ближняя рука: висит → к сумке на полу → несёт сумку → к ручке двери → толкает
    shw = p["hip"] + np.array([math.sin(p["lean"]), -math.cos(p["lean"])]) * 176
    hang = shw + np.array([30.0, 190.0])
    bag_h = BAG0 + np.array([0.0, -48.0])
    tgt = hang + (bag_h - hang) * smooth(T_BAG - 0.12, T_BAG - 0.01, t)
    carry = shw + np.array([50.0, 185.0])
    tgt = tgt + (carry - tgt) * smooth(T_BAG + 0.02, T_BAG + 0.2, t)
    knob = np.array(hall.KNOB) + np.array([-30.0, 6.0])
    push = smooth(T_DOOR - 0.02, T_DOOR + 0.12, t)
    kn = knob + np.array([60.0, -10.0]) * push
    tgt = tgt + (kn - tgt) * smooth(T_DOOR - 0.24, T_DOOR - 0.06, t)
    p["arms"] = {"n": ("ik", tgt, -1), "f": ("ik", shw + np.array([-30.0 + 60 * walk, 190.0]), -1)}
    if smooth(T_DOOR - 0.24, T_DOOR - 0.06, t) > 0.5:
        p["hands"] = {"n": ("open", 0.75 * (1 - push)), "f": "fist"}
        p["hand_dir"] = {"n": (1.0, 0.1)}
    return p


def frame(t):
    lib.DEFS.clear()
    dima.set_palette(dima.HOODIE)
    p = pose(t)
    held = T_BAG - 0.01 <= t
    g, info = dima.draw(p)
    mid = []
    door = 0.0
    if t > T_DOOR - 0.02:
        v = t - T_DOOR + 0.02
        door = clamp(1 - math.exp(-9 * v) * math.cos(2 * math.pi * 1.3 * v) * (1 if v > 0 else 0)) if v > 0 else 0.0
    if door > 0.02:          # свет с площадки — на стену и пол за Димой (не поверх героя)
        x0, y0, x1, y1 = hall.DOOR
        gl = lib.rad_grad([(0, "#fff0c0", .45 * door), (1, "#fff0c0", 0)], (x0 + x1) / 2, -300, 520, 600)
        mid.append(f'<ellipse cx="{(x0 + x1) / 2}" cy="-300" rx="520" ry="600" fill="url(#{gl})"/>')
    mid.append(phone(t))
    mid.append(f'<ellipse cx="{p["hip"][0] + 20:.1f}" cy="4" rx="150" ry="18" fill="#3a2418" opacity=".28"/>')
    if not held:
        mid.append(f'<ellipse cx="{BAG0[0]:.1f}" cy="2" rx="80" ry="10" fill="#3a2418" opacity=".3"/>')
        mid.append(f'<g transform="translate({BAG0[0]:.1f} {BAG0[1]:.1f}) scale(0.44)">{hero.duffel(0, 0, w=330, h=170, seed=984)}</g>')
    mid.append(g)
    if held:      # сумка в руке (качается)
        wr = info["n"]
        sw = 12 * math.sin((t - T_BAG) * 9) * math.exp(-2 * (t - T_BAG))
        c = wr + np.array([sw, 52.0])
        mid.append(hero.line([tuple(wr + np.array([-14, 8])), tuple(c + np.array([-30, -26]))], 5.4, "#1b2445", seed=977, taper=.1, wmin=.9))
        mid.append(hero.line([tuple(wr + np.array([14, 8])), tuple(c + np.array([30, -26]))], 5.4, "#1b2445", seed=978, taper=.1, wmin=.9))
        mid.append(f'<g transform="translate({c[0]:.1f} {c[1]:.1f}) rotate({sw * .4:.1f}) scale(0.44)">{hero.duffel(0, 0, w=330, h=170, seed=984)}</g>')
    fg = [bubble(t)]
    # камера: близко к телефону и Диме, толчок на «серия», потом отъезд к двери
    o = ease_io((t - 26.92) / 0.6)
    cx = 120 + 110 * o
    cy = -500 + 80 * o
    s = 2.05 + 0.08 * (t - T_A) * (1 - o) - 0.45 * o
    k = t - T_NOTE
    if k > -0.03:
        s *= 1 + 0.06 * smooth(-0.03, 0.03, k) * math.exp(-4 * max(0, k))
    if t > T_DOOR:
        s *= 1 + 0.04 * smooth(0, 0.06, t - T_DOOR) * math.exp(-4 * (t - T_DOOR))
    return hall.frame(t, cam=(cx, cy, s, 0.4 * math.sin(t * 1.5)), door=door, mid="".join(mid), fg="".join(fg), phone=False)
