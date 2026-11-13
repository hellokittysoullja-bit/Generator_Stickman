"""Покупатели супермаркета — в стиле героев: контур тушью с нажимом, большие глаза, cel-тень справа-снизу (свет сверху-
слева). Человек строится в своих координатах: ступни на y=0, рост ~700; поза — словарь углов. person(spec, pose) -> SVG."""
import math

import numpy as np

import lib
from lib import INK, band, blob, ellipse_pts, f, line, shape

SH_K = (0.80, 0.78, 0.86)        # cel-тень: умножение цвета (чуть в холод)


def shade(h, k=SH_K):
    return lib.mul(h, k)


def rot(p, ang, c=(0, 0)):
    a = math.radians(ang)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def limb(p0, a1, l1, a2, l2):
    """плечо/бедро p0, угол сегмента 1 (0 = вниз, + = вперёд-вправо по часовой), длины; -> локоть, кисть."""
    def d(a, l):
        r = math.radians(a)
        return (l * math.sin(r), l * math.cos(r))
    e = (p0[0] + d(a1, l1)[0], p0[1] + d(a1, l1)[1])
    h = (e[0] + d(a1 + a2, l2)[0], e[1] + d(a1 + a2, l2)[1])
    return e, h


def tube(p0, p1, p2, w0, w1, w2, fill, sd, inner_sh=True):
    pts = [p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), p1, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2), p2]
    pl = band(pts, w0, w2, step=6, wmid=w1, cap=True)
    inner = ""
    if inner_sh:
        sh = band([(x + w1 * .22, y) for x, y in pts], w0 * .45, w2 * .45, step=6, wmid=w1 * .45, cap=False)
        inner = blob(sh, shade(fill), .9)
    return shape(pl, fill, inner, w=3.6, seed=sd)


def _finger(base, ang, L, wd, curl, skin, sd):
    from scene_brain import sausage
    pts = [base]
    a, x, y = ang, base[0], base[1]
    for k in range(3):
        a += curl * 30
        x += L / 3 * math.cos(math.radians(a))
        y += L / 3 * math.sin(math.radians(a))
        pts.append((x, y))
    return shape(sausage(pts, wd, wd * .9), skin, "", w=3.0, seed=sd)


def fhand(x, y, ang, skin, sd=0, sc=1.0, curl=0.3, spread=1.0, thumb_up=True):
    """Кисть с пальцами (как у ручек мозга, тон кожи): запястье (x, y), пальцы вдоль ang (градусы экрана).
    Три пальца и большой; curl 0..1 — сжатие (хват)."""
    sh = shade(skin)
    palm = [(-6, -13), (14, -22), (36, -22), (50, -10), (52, 6), (42, 19), (18, 22), (-6, 12)]
    inner = blob([(-6, 6), (16, 13), (40, 11), (52, 6), (42, 19), (18, 22), (-6, 12)], sh, .85)
    s = [_finger((22, -18), -62 + 30 * curl, 26, 15, curl * .8, skin, sd + 20)]
    s.append(shape(palm, skin, inner, w=3.4, seed=sd + 1))
    for k, (bx, by, fa, L) in enumerate([(46, -14, -14 * spread, 34), (50, -1, 0, 38), (46, 12, 14 * spread, 33)]):
        s.append(_finger((bx, by), fa, L, 15, curl, skin, sd + 10 + k))
    flip = math.cos(math.radians(ang)) < 0
    if not thumb_up:
        flip = not flip
    rot = ang if not flip else ang - 180
    sx = -1 if flip else 1
    if flip and thumb_up:
        pass
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc * sx)} {f(sc)})">{"".join(s)}</g>'


def hand(c, r, skin, sd, ang=90, curl=0.3):
    """Кисть на конце руки: запястье в c, пальцы по направлению ang (по умолчанию вниз)."""
    return fhand(c[0], c[1], ang, skin, sd, sc=r * 0.042, curl=curl)


def shoe(c, face, color, sd):
    x, y = c
    pts = [(x - 24 * face, y - 30), (x + 14 * face, y - 30), (x + 34 * face, y - 18), (x + 48 * face, y - 8), (x + 48 * face, y + 2, 1),
           (x - 28 * face, y + 2, 1), (x - 30 * face, y - 14)]
    if face < 0:
        pts = pts[::-1]
    return shape(pts, color, blob([(x - 26, y - 2), (x + 46 * face, y - 2), (x + 44 * face, y + 4), (x - 26, y + 4)], shade(color, (.6, .6, .7)), .8),
                 w=3.4, seed=sd)


def face(spec, pose, sd):
    """Голова: центр (0,0), лицо в 3/4 к стороне facing; глаза большие."""
    fc = spec["face"]          # -1..1 поворот
    skin = spec["skin"]
    hx = 64 * spec.get("hw", 1.0)
    hy = 74
    s = []
    if spec.get("back"):
        return back_head(spec, hx, hy, sd)
    # волосы сзади
    hair = spec["hair"]
    hc = spec["hair_c"]
    if hair == "bob":
        s.append(shape([(-hx - 10, -20), (-hx - 4, -70), (-30, -100), (30, -100), (hx + 4, -70), (hx + 12, -10), (hx + 10, 50, 1),
                        (-hx - 12, 50, 1)], hc, w=4, seed=sd + 1))
    if hair == "ponytail":
        tail = [(-fc * 50, -60), (-fc * 110, -40), (-fc * 128, 10), (-fc * 116, 70), (-fc * 96, 40), (-fc * 92, -10), (-fc * 60, -40)]
        s.append(shape(tail if fc >= 0 else tail[::-1], hc, blob([(-fc * 100, -20), (-fc * 116, 40), (-fc * 100, 30)], shade(hc), .9), w=4, seed=sd + 2))
    if hair == "bun":
        s.append(shape(ellipse_pts(-fc * 10, -96, 34, 28, 12), hc, blob(ellipse_pts(-fc * 2, -90, 22, 16, 10), shade(hc), .8), w=4, seed=sd + 3))
    # ухо (на дальней от взгляда стороне)
    ex = -fc * (hx - 6) if abs(fc) > .15 else hx - 4
    s.append(shape(ellipse_pts(ex, 8, 14, 20, 10), skin, blob(ellipse_pts(ex + 3, 10, 7, 12, 8), shade(skin), .9), w=3.4, seed=sd + 4))
    if abs(fc) <= .15:
        s.append(shape(ellipse_pts(-hx + 4, 8, 14, 20, 10), skin, w=3.4, seed=sd + 5))
    # лицо: чуть вытянуто к стороне взгляда, подбородок
    jaw = spec.get("jaw", 0.0)
    fp = [(-hx, -10), (-hx + 6, -54), (-30, -hy), (20, -hy - 2), (hx - 4, -56), (hx, -6), (hx - 8, 34 + jaw * 6),
          (fc * 20 + 30, 64 + jaw * 10), (fc * 20, 74 + jaw * 8), (fc * 20 - 34, 64 + jaw * 6), (-hx + 8, 34)]
    inner = blob([(hx * .35 - fc * 30, -hy), (hx, -60), (hx + 4, 10), (hx - 8, 40), (fc * 20 + 34, 70), (fc * 20 + 10, 80),
                  (fc * 20 + 40, 30), (hx * .5, -20)], shade(skin), .9)
    inner += blob(ellipse_pts(-20 + fc * 26, 30, 16, 9, 8), "#e88a7a", .35)
    inner += blob(ellipse_pts(36 + fc * 26, 30, 14, 8, 8), "#e88a7a", .3)
    if spec.get("stubble"):
        inner += blob([(-hx + 10, 30), (fc * 20 - 30, 64), (fc * 20 + 30, 64), (hx - 10, 30), (hx, 90), (-hx, 90)], "#8a7a80", .28)
    s.append(shape(fp, skin, inner, w=4.6, seed=sd + 6))
    # глаза
    ex_ = [-24 + fc * 22, 24 + fc * 22]
    lx, ly = pose.get("look", (0.0, 0.0))
    blink = pose.get("blink", 0.0)
    for i, x in enumerate(ex_):
        rx, ry = 15 * (1 - .18 * abs(fc) * (1 if (x - fc * 22) * fc < 0 else 0)), 19
        ey = -8
        e = ellipse_pts(x, ey, rx, ry, 14)
        if blink < .95:
            s.append(shape(e, "#ffffff", f'<circle cx="{f(x + lx * 6)}" cy="{f(ey + 3 + ly * 6)}" r="6.4" fill="{INK}"/>'
                           f'<circle cx="{f(x + lx * 6 - 2)}" cy="{f(ey + 0 + ly * 6)}" r="1.8" fill="#fff"/>'
                           + (f'<rect x="{x - rx - 2}" y="{ey - ry - 2}" width="{2 * rx + 4}" height="{f((2 * ry + 4) * blink)}" fill="{skin}"/>'
                              f'<rect x="{x - rx - 2}" y="{f(ey - ry - 2 + (2 * ry + 4) * blink - 2.5)}" width="{2 * rx + 4}" height="3.5" fill="{INK}"/>' if blink > 0 else ""),
                           w=3.2, seed=sd + 10 + i))
        else:
            s.append(line([(x - rx, ey + 2), (x, ey + 6), (x + rx, ey + 2)], 3.4, seed=sd + 12 + i))
        # бровь
        br = pose.get("brow", 0.0)
        tilt = (-1 if i == 0 else 1) * br * 6
        s.append(line([(x - 14, ey - 28 - tilt), (x, ey - 32), (x + 14, ey - 28 + tilt)], 5, spec.get("brow_c", "#3a2a22"), seed=sd + 14 + i, taper=.5, wmin=.4))
    if spec.get("glasses"):
        for x in ex_:
            s.append(f'<ellipse cx="{f(x)}" cy="-8" rx="21" ry="20" fill="#cfe4ff" fill-opacity=".18" stroke="{INK}" stroke-width="3.6"/>')
        s.append(line([(ex_[0] + 20, -10), (ex_[1] - 20, -10)], 3.2, seed=sd + 16, taper=.1, wmin=.9))
    # нос и рот
    nx = fc * 30 + 4
    s.append(line([(nx - 2, 6), (nx + 7 * (1 if fc >= 0 else -1), 22), (nx, 26)], 3, seed=sd + 17, taper=.4, wmin=.3))
    m = pose.get("mouth", "flat")
    mx = fc * 24 + 2
    if m == "smile":
        s.append(line([(mx - 16, 42), (mx, 50), (mx + 16, 42)], 3.6, seed=sd + 18))
    elif m == "o":
        s.append(shape(ellipse_pts(mx, 46, 6, 8, 10), "#5a2a2a", w=2.6, seed=sd + 18))
    elif m == "frown":
        s.append(line([(mx - 14, 50), (mx, 44), (mx + 14, 50)], 3.4, seed=sd + 18))
    elif m == "wavy":
        s.append(line([(mx - 16, 46), (mx - 6, 42), (mx + 4, 48), (mx + 14, 44)], 3.2, seed=sd + 18))
    else:
        s.append(line([(mx - 12, 46), (mx + 12, 45)], 3.2, seed=sd + 18))
    if spec.get("mustache"):
        s.append(shape([(mx - 22, 36), (mx, 30), (mx + 22, 36), (mx + 14, 40), (mx, 36), (mx - 14, 40)], spec["hair_c"], w=2.6, seed=sd + 19))
    # волосы сверху
    if hair in ("short", "bob", "ponytail", "bun") and not (spec.get("cap") and hair == "short"):
        top = [(-hx - 6, -4), (-hx - 4, -50), (-40, -hy - 22), (10, -hy - 30), (hx - 2, -hy - 6), (hx + 6, -40), (hx + 4, -6),
               (hx - 10, -36), (fc * 20 + 20, -54), (fc * 20 - 10, -46), (-hx + 14, -30)]
        if hair == "short":
            top = [(-hx - 4, 0), (-hx - 6, -50), (-52, -hy - 18), (-20, -hy - 34, 1), (8, -hy - 20), (34, -hy - 30, 1), (hx - 4, -hy - 6),
                   (hx + 6, -38), (hx + 2, -8), (hx - 10, -40), (fc * 18 + 14, -58), (fc * 18 - 20, -50), (-hx + 12, -34), (-hx + 6, 0)]
        s.append(shape(top, hc, blob([(hx * .2, -hy - 20), (hx + 6, -40), (hx - 10, -40), (fc * 18 + 14, -58)], shade(hc), .9)
                       + line([(-30, -hy - 10), (-10, -64)], 3, shade(hc, (.6, .6, .7)), seed=sd + 21), w=4.4, seed=sd + 20))
    elif hair == "curly":
        bumps = []
        for k in range(15):
            a = math.pi * (0.95 + 1.1 * k / 14)
            r = 1.0 if k % 2 == 0 else 1.13
            bumps.append((1.18 * hx * r * math.cos(a), -16 + 1.25 * hy * r * math.sin(a)))
        bumps += [(hx + 8, 10), (hx - 6, -30), (fc * 20, -52), (-hx + 6, -30), (-hx - 8, 10)]
        s.append(shape(bumps, hc, blob([(0, -110), (hx + 20, -50), (hx, -30), (fc * 20, -52)], shade(hc), .9), w=4.4, seed=sd + 20))
    elif hair == "bald":
        s.append(blob([(-hx + 2, -40), (-hx - 6, 0), (-hx + 2, 20), (-hx + 10, -10)], spec["hair_c"]))
        s.append(blob([(hx - 2, -40), (hx + 6, 0), (hx - 2, 20), (hx - 10, -10)], spec["hair_c"]))
        s.append(line([(-hx + 26, -60), (-hx + 40, -66)], 4, "#ffffff", seed=sd + 22, op=.6))
    if spec.get("cap"):
        cc = spec["cap"]
        s.append(shape([(-hx - 6, -36), (-hx + 4, -78), (-10, -hy - 28), (hx - 6, -78), (hx + 6, -36)], cc, blob([(10, -hy - 20), (hx, -70), (hx + 6, -36), (20, -36)], shade(cc), .9), w=4.2, seed=sd + 23))
        s.append(shape([(fc * 30 - 40, -40), (fc * 30 + 50 + 40 * fc, -44), (fc * 30 + 60 + 50 * fc, -30), (fc * 30 - 40, -30)], shade(cc), w=3.6, seed=sd + 24))
    return "".join(s)


def back_head(spec, hx, hy, sd):
    """Голова со спины: уши по бокам, затылок волосами, шея ниже."""
    skin, hc = spec["skin"], spec["hair_c"]
    s = []
    for side in (-1, 1):
        s.append(shape(ellipse_pts(side * (hx - 4), 8, 14, 20, 10), skin, blob(ellipse_pts(side * (hx - 2), 10, 7, 12, 8), shade(skin), .9), w=3.4, seed=sd + 4 + side))
    head = ellipse_pts(0, 0, hx, hy, 16)
    s.append(shape(head, skin, blob(ellipse_pts(30, 20, hx, hy, 12), shade(skin), .85), w=4.6, seed=sd + 6))
    hair = [(-hx - 4, 30), (-hx - 6, -40), (-40, -hy - 20), (10, -hy - 26), (hx - 6, -hy - 6), (hx + 6, -36), (hx + 4, 30),
            (hx - 14, 50), (40, 44, 1), (24, 60), (0, 46, 1), (-24, 60), (-40, 44, 1), (-hx + 14, 50)]
    inner = blob([(10, -hy - 20), (hx + 6, -36), (hx + 4, 30), (hx - 14, 50), (20, 50)], shade(hc), .9)
    for i, st in enumerate([[(-30, -60), (-26, 0), (-36, 40)], [(10, -70), (16, -10), (8, 40)], [(44, -50), (46, 10)]]):
        inner += line(st, 3, shade(hc, (.6, .6, .7)), seed=sd + 30 + i, op=.8)
    s.append(shape(hair, hc, inner, w=4.4, seed=sd + 20))
    return "".join(s)


def _stripe(pts, color, side, w, sd, cut=1.0):
    """Полоса вдоль конечности со смещением side·w/2 от средней линии (по нормали к отрезку бедро→колено)."""
    S = lib.sample(pts, False, 3.0)
    n = max(3, int(len(S) * cut))
    S = S[:n]
    T = np.gradient(S, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    Q = S + N * side * w / 2 * 0.62
    return line([tuple(q) for q in Q[1:-1]], 6.5, color, taper=.15, wmin=.7, seed=sd)


def person(spec, pose, sd=0):
    """spec: skin, hair, hair_c, top, top2 (низ), shoes, face(-1..1), h (масштаб). pose: walk (фаза, рад) или None,
    arms: {'L': (a1, a2), 'R': (a1, a2)} углы плечо/локоть, head_tilt, look, mouth, brow, basket ('L'/'R'), item."""
    fc = spec["face"]
    s = []
    hipY, shY = -300, -520
    walk = pose.get("walk")
    bob = 0.0
    if walk is not None:
        sw = math.sin(walk)
        bob = -8 * abs(math.cos(walk))
        dr = 1 if fc >= 0 else -1
        legs = {"L": (24 * sw, max(0, -38 * math.sin(walk - 1.2))), "R": (-24 * sw, max(0, 38 * math.sin(walk - 1.2)))}
        arms = {"L": (-16 * sw * dr, 16 * dr), "R": (16 * sw * dr, 16 * dr)}
    else:
        legs = pose.get("legs", {"L": (3, 0), "R": (-3, 0)})
        arms = {"L": (8, -6), "R": (-8, 6)}
    arms.update(pose.get("arms", {}))
    sh_w0 = 74 * spec.get("bw", 1.0)
    for side, tgt in pose.get("hand_target", {}).items():          # IK: кисть в точку (координаты человека)
        sign = -1 if side == "L" else 1
        p0 = (sign * (sh_w0 - 10), shY + 18 + bob)
        dx, dy = tgt[0] - p0[0], tgt[1] - p0[1]
        d = min(math.hypot(dx, dy), 249.0)
        d = max(d, 20.0)
        base = math.degrees(math.atan2(dx, dy))
        al = math.degrees(math.acos(max(-1, min(1, (130 ** 2 + d ** 2 - 120 ** 2) / (2 * 130 * d)))))
        a1 = base + al * sign            # локоть наружу
        ex, ey = p0[0] + 130 * math.sin(math.radians(a1)), p0[1] + 130 * math.cos(math.radians(a1))
        a2 = math.degrees(math.atan2(tgt[0] - ex, tgt[1] - ey)) - a1
        arms[side] = (a1 - sign * 6, a2)
    top, low, skin = spec["top"], spec["low"], spec["skin"]
    sh_w = 74 * spec.get("bw", 1.0)
    # порядок: дальняя рука и нога — первыми
    far, near = ("L", "R") if fc >= 0 else ("R", "L")
    hips = {"L": (-26, hipY + bob), "R": (26, hipY + bob)}
    shs = {"L": (-sh_w + 10, shY + 18 + bob), "R": (sh_w - 10, shY + 18 + bob)}

    def leg(side):
        a1, k = legs[side]
        dr = 1 if fc >= 0 else -1
        knee, foot = limb(hips[side], a1 * dr, 140, -k * dr, 140)
        lift = max(0.0, foot[1] + 20)
        foot = (foot[0], foot[1] - lift)
        out = tube(hips[side], knee, foot, 46, 40, 34, low, sd + (1 if side == "L" else 2))
        if spec.get("track"):       # лампасы спортивного костюма (рилс 26)
            out += _stripe([hips[side], knee, foot], spec["track"], 0.62 * (1 if side == "R" else -1) * (1 if fc >= 0 else -1), 40, sd + 90)
        out += shoe((foot[0], foot[1] + 20), 1 if fc >= 0 else -1, spec.get("shoes", "#3a3440"), sd + 3 + (side == "L"))
        return out

    def arm(side):
        a1, a2 = arms[side]
        p0 = shs[side]
        sign = -1 if side == "L" else 1
        elbow, hnd = limb(p0, a1 * 1.0 + sign * 6, 130, a2, 120)
        out = tube(p0, elbow, hnd, 40, 34, 28, spec.get("sleeve", top), sd + 5 + (side == "L"))
        if spec.get("track"):
            out += _stripe([p0, elbow, hnd], spec["track"], 0.55 * sign, 34, sd + 92, cut=0.86)
        ang = math.degrees(math.atan2(hnd[1] - elbow[1], hnd[0] - elbow[0]))
        item = pose.get("in_hand", {}).get(side)
        if item:
            out += item(hnd, ang)
        out += hand(hnd, 17, skin, sd + 7 + (side == "L"), ang, pose.get("curl", {}).get(side, 0.3))
        top_item = pose.get("over_hand", {}).get(side)
        if top_item:
            out += top_item(hnd, ang)
        return out, hnd

    hands = {}
    nl = pose.get("no_legs")
    if not nl:
        s.append(leg(far))
    a_far, hands[far] = arm(far)
    s.append(a_far)
    if not nl:
        s.append(leg(near))
    a_near, hands[near] = arm(near)
    s.append(a_near)
    a_near = ""
    # туловище
    torso = [(-sh_w, shY + 30 + bob), (-sh_w + 14, shY + 4 + bob), (-30, shY - 8 + bob), (30, shY - 8 + bob), (sh_w - 14, shY + 4 + bob),
             (sh_w, shY + 30 + bob), (sh_w - 10, hipY - 60 + bob), (sh_w - 6, hipY + 26 + bob, 1), (-sh_w + 6, hipY + 26 + bob, 1),
             (-sh_w + 10, hipY - 60 + bob)]
    inner = blob([(10, shY - 20 + bob), (sh_w + 4, shY + 10 + bob), (sh_w, hipY + 30 + bob), (14, hipY + 30 + bob), (30, shY + 80 + bob)], shade(top), .85)
    if spec.get("zip"):
        inner += line([(fc * 14, shY + 2 + bob), (fc * 16, hipY + 20 + bob)], 3, seed=sd + 30, op=.8)
    if spec.get("stripes"):
        for k in range(4):
            y = shY + 70 + k * 46 + bob
            inner += f'<rect x="-120" y="{f(y)}" width="240" height="14" fill="{spec["stripes"]}" opacity=".9"/>'
    inner += line([(-sh_w + 30, hipY - 10 + bob), (-sh_w + 40, hipY + 20 + bob)], 2.6, seed=sd + 31, op=.6)
    s.append(shape(torso, top, inner, w=5, seed=sd + 32))
    # воротник/шея
    s.append(shape([(-22, shY - 10 + bob), (22, shY - 10 + bob), (20, shY - 40 + bob), (-20, shY - 40 + bob)], skin,
                   blob([(-22, shY - 40 + bob), (22, shY - 40 + bob), (22, shY - 24 + bob), (-22, shY - 24 + bob)], shade(skin), .9), w=3.6, seed=sd + 33))
    if spec.get("collar"):
        s.append(shape([(-34, shY - 4 + bob), (0, shY + 22 + bob), (34, shY - 4 + bob), (24, shY + 10 + bob), (0, shY + 34 + bob), (-24, shY + 10 + bob)],
                       spec["collar"], w=3.4, seed=sd + 34))
    # голова
    tilt = pose.get("head_tilt", 0.0)
    s.append(f'<g transform="translate({fc * 6:.1f} {f(shY - 104 + bob)}) rotate({tilt:.2f})">{face(spec, pose, sd + 40)}</g>')
    # корзина в руке (до ближней руки, если в дальней)
    bk = pose.get("basket")
    if bk:
        hx, hy = hands[bk]
        b = basket(hx, hy, pose.get("basket_items", 0), sd + 60, pose.get("basket_c", "#d23a32"))
        s.append(b)
        s.append(hand(hands[bk], 17, skin, sd + 70))
    s.append(a_near)
    item = pose.get("item")
    if item:
        hx, hy = hands[item[0]]
        s.append(jar_small(hx, hy - 4, item[1], sd + 80))
        s.append(hand((hx - 6, hy + 4), 15, skin, sd + 81))
    return "".join(s)


def draw(spec, pose, x, y, sc=1.0, sd=0, flip=False):
    fl = " scale(-1 1)" if flip else ""
    return f'<g transform="translate({f(x)} {f(y)}) scale({sc * spec.get("h", 1.0):.4f}){fl}">{person(spec, pose, sd)}</g>'


def basket(hx, hy, items, sd, col):
    """Пластиковая корзина: ручка в кисти, корпус ниже."""
    s = []
    x0, y0 = hx - 80, hy + 40
    s.append(line([(hx - 60, y0 + 6), (hx - 40, hy - 6), (hx, hy - 12), (hx + 40, hy - 6), (hx + 60, y0 + 6)], 7, shade(col, (.7, .7, .7)), taper=.1, wmin=.9, seed=sd))
    body = [(x0 - 10, y0, 1), (x0 + 170, y0, 1), (x0 + 156, y0 + 100, 1), (x0 + 4, y0 + 100, 1)]
    inner = ""
    for k in range(5):
        inner += f'<rect x="{f(x0 + 6 + k * 32)}" y="{f(y0 + 20)}" width="16" height="22" rx="5" fill="{shade(col, (.6, .55, .6))}"/>'
        inner += f'<rect x="{f(x0 + 8 + k * 32)}" y="{f(y0 + 56)}" width="14" height="22" rx="5" fill="{shade(col, (.6, .55, .6))}"/>'
    inner += blob([(x0 + 100, y0), (x0 + 170, y0), (x0 + 156, y0 + 100), (x0 + 110, y0 + 100)], shade(col), .6)
    if items:
        s.append(jar_small(x0 + 80, y0 - 4, items, sd + 5, sc=1.0))
    s.append(shape(body, col, inner, w=4, seed=sd + 1))
    s.append(shape([(x0 - 14, y0 - 8, 1), (x0 + 174, y0 - 8, 1), (x0 + 172, y0 + 6, 1), (x0 - 12, y0 + 6, 1)], shade(col, (.85, .85, .85)), w=3.6, seed=sd + 2))
    return "".join(s)


def jar_small(cx, by, color, sd, sc=0.9):
    from jars import jar
    return jar(cx, by + 40 * sc, color, sc * 0.9, sd)
