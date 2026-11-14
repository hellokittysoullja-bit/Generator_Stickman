"""Кот группы F рилса 63 поверх общего кота (common/cat.py: анфас, как look/hero.png, ЛЕВОЕ от зрителя ухо загнуто).

draw_f(x, y, k, st, t) — сидящий/шагающий кот, как cat.draw, но голова и передние лапы живее:
  st['turn']    −2…2 — поворот головы; до ±1 как у общего кота, дальше морда уходит за край головы (обрезается её контуром),
                а с другой стороны проступает затылок: три четверти со спины через промежуточные кадры, а не подменой;
  st['body_turn'] −1…1 — поворот туловища: тень и светлое пятно груди уходят вбок, хвост заходит вперёд/назад;
  st['sniff']   0…1 — нос приподнят, ноздри раздуты, у носа короткие дуги вдоха;
  st['wrinkle'] 0…1 — нос сморщен: складки над носом, рот «фу», уши слегка прижаты;
  st['tongue']  0…1 — язык лакает вниз (как в общем коте);  st['lick'] 0…1 — облизывается: язычок выходит вбок и проходит по губе;
  st['squint']  0…1 — довольный прищур (глаза-дуги ∩);  st['milk'] 0…1 — белая капля молока на усах;
  st['paw']     0…1 — правая (от зрителя) передняя лапа поднята, st['paw_shake'] — фаза отряхивания;
  st['walk']    — фаза шага (лапы по очереди), st['head_dx'], st['head_dy'], st['drop'] — голова вбок/вниз (к миске).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as Cat  # noqa: E402
import lib  # noqa: E402
from ink import ellipse_pts, fur  # noqa: E402
from lib import INK, blob, line, shape  # noqa: E402

import numpy as np  # noqa: E402

CAT, CAT_SH, CAT_FUR, CAT_EDGE = Cat.CAT, Cat.CAT_SH, Cat.CAT_FUR, Cat.CAT_EDGE
CX, CBOT, NECK = Cat.CX, Cat.CBOT, Cat.NECK
PAD = "#e8823a"
MILK = "#FBF8F0"
HEAD = [(744, 1062), (760, 1012), (800, 990), (870, 990), (914, 1014), (930, 1062), (922, 1112), (884, 1146), (788, 1146), (750, 1112)]


def _fx(turn):
    a = abs(turn)
    return math.copysign(22 * min(a, 1.0) + 62 * max(0.0, a - 1.0), turn)


def _happy_eye(ex, ey, rx, sd, u):
    """Довольный прищур: дуга ∩ с пушистым нижним веком."""
    h = 14 * u
    return line([(ex - rx * .9, ey + 6), (ex - rx * .45, ey - h + 4), (ex + rx * .45, ey - h + 4), (ex + rx * .9, ey + 6)], 6, INK, seed=sd,
                taper=.5, wmin=.35)


def head_f(st, t):
    turn = st.get("turn", 0.0)
    look = st.get("look", (0.0, 0.0))
    bl = st.get("blink", 0.0)
    eyes = st.get("eyes", (bl, bl))
    sq_ = st.get("squint", 0.0)
    wr = st.get("wrinkle", 0.0)
    sn = st.get("sniff", 0.0)
    FX = _fx(turn)
    away = max(0.0, abs(turn) - 1.0)            # 0…1: морда уходит за край головы
    sgn = 1 if turn >= 0 else -1
    s = []
    hp = fur(HEAD, 8, 6, seed=23)
    inner = blob([(884 + FX * .5, 990), (940, 1050), (930, 1150), (866 + FX * .5, 1150), (902 + FX * .5, 1080)], CAT_SH, .85)
    inner += blob([(784, 1004), (836, 994), (880, 1004), (862, 1018), (804, 1020)], CAT_FUR, .6)
    if away > 0:     # затылок: с противоположной стороны тёмная шерсть, мягкий блик по макушке
        bx = 836 - sgn * (110 - 60 * away)
        inner += blob(ellipse_pts(bx, 1070, 70 + 40 * away, 80, 14), CAT_SH, .55 + .3 * away)
        inner += line([(836 - sgn * 20, 1000), (836 - sgn * (40 + 30 * away), 1060), (836 - sgn * (30 + 20 * away), 1120)], 2.2, CAT_EDGE, seed=297, op=.7)
    s.append(shape(hp, CAT, inner, w=5.2, seed=250))
    ear_r = st.get("ear", 0.0) - 9 * wr
    s.append(f'<g transform="translate({FX * .35:.1f} {4 * wr:.1f})">{Cat.ears(ear_r, st.get("perk", 0.0))}</g>')
    # черты морды — внутри контура головы (уходят за край при большом повороте)
    f = []
    CXH = CX + FX
    for sx in (-1, 1):
        if away > .55 and sx == sgn:
            continue
        for k, dy in enumerate((0, 14)):
            x0 = CX + sx * 76 + FX * (.5 if sx * turn > 0 else 1.0)
            ln = 30 * (1 - .4 * max(0, sx * turn))
            f.append(line([(x0, 1100 + dy), (x0 + sx * ln, 1094 + dy + k * 3)], 5.6, "#f0903e", seed=260 + k + sx, taper=.3, wmin=.5))
    for i, (nm, ex, sd) in enumerate([("L", CXH - 44 - 4 * turn, 255), ("R", CXH + 44 - 4 * turn, 256)]):
        side = -1 if nm == "L" else 1
        sq = 1.0 - .22 * max(0.0, turn * side) - .3 * away * (side == sgn)
        sq = max(.35, sq)
        if sq_ > .05:
            f.append(_happy_eye(ex, 1072, 34 * sq, sd + 50, sq_))
        else:
            e = eyes[i]
            if wr > 0:
                e = max(e, .5 * wr)
            f.append(Cat.eye(ex, 1072, 34, 38, look, e, sd, sq))
    ny = 1108 - 4 * sn - 2 * wr
    nk = 1 + .18 * sn
    f.append(shape([(836 + FX - 10 * nk, ny), (836 + FX + 10 * nk, ny), (836 + FX, ny + 11 * nk)], "#c47a72", w=2.6, seed=262))
    if wr > .05:     # складки над носом
        for j, dx in enumerate((-12, 0, 12)):
            f.append(line([(836 + FX + dx - 6, 1094 - 3 * abs(dx) / 12), (836 + FX + dx, 1090 - 5 * wr), (836 + FX + dx + 6, 1094 - 3 * abs(dx) / 12)],
                          2.4 * wr + .4, INK, seed=300 + j, taper=.5, wmin=.3))
    if sn > .05:     # дуги вдоха у ноздрей
        for j, sx in enumerate((-1, 1)):
            x0 = 836 + FX + sx * 16
            f.append(line([(x0 + sx * 4, ny - 2), (x0 + sx * 14, ny - 10 * sn), (x0 + sx * 10, ny - 20 * sn)], 2.4, INK, seed=310 + j, taper=.6, wmin=.3))
    f.append(line([(836 + FX, ny + 11 * nk), (836 + FX, 1124)], 2.4, seed=263))
    tg, lk = st.get("tongue", 0.0), st.get("lick", 0.0)
    if tg > .02:      # лакает: розовая лопатка вниз из приоткрытого рта
        L_ = 44 * tg
        tp = [(824 + FX, 1124, 1), (848 + FX, 1124, 1), (850 + FX, 1124 + L_ * .6), (844 + FX, 1124 + L_), (836 + FX, 1124 + L_ + 4),
              (828 + FX, 1124 + L_), (822 + FX, 1124 + L_ * .6)]
        f.append(shape([(818 + FX, 1121), (854 + FX, 1121), (846 + FX, 1131), (826 + FX, 1131)], "#5a2b33", w=2.4, seed=266))
        f.append(shape(tp, "#e8808c", line([(836 + FX, 1128), (836 + FX, 1124 + L_)], 1.6, "#c4565f", seed=267), w=2.8, seed=268))
    elif lk > .02:    # облизывается: язык выходит вбок и вверх по губе (полный круг за lk 0→1)
        a = math.pi * lk
        ox = 836 + FX + 26 * math.cos(math.pi - a) * .9
        oy = 1126 - 10 * math.sin(a)
        ext = math.sin(a)
        f.append(shape([(820 + FX, 1121), (852 + FX, 1121), (846 + FX, 1132), (826 + FX, 1132)], "#5a2b33", w=2.4, seed=266))
        tp = [(828 + FX, 1126, 1), (846 + FX, 1126, 1), (ox + 12 * ext, oy + 2), (ox + 6 * ext, oy - 10 * ext), (ox - 4, oy - 12 * ext),
              (ox - 12 * ext, oy - 2)]
        f.append(shape(tp, "#e8808c", "", w=2.6, seed=269))
    elif wr > .05:    # «фу»: рот волной вниз, уголки опущены
        f.append(line([(818 + FX, 1132), (828 + FX, 1124), (836 + FX, 1128), (844 + FX, 1124), (854 + FX, 1132)], 3.2, seed=271))
    elif st.get("smile", 0) > .5:
        f.append(line([(818 + FX, 1122), (828 + FX, 1134), (836 + FX, 1126), (844 + FX, 1134), (854 + FX, 1122)], 3.2, seed=265))
    else:
        f.append(line([(822 + FX, 1124), (829 + FX, 1131), (836 + FX, 1124), (843 + FX, 1131), (850 + FX, 1124)], 3, seed=264))
    c = lib.clip_of(HEAD)
    s.append(f'<g clip-path="url(#{c})">{"".join(f)}</g>')
    # усы — поверх контура (выходят за голову); дальние прячутся при повороте затылком
    for sx in (-1, 1):
        if away > .35 and sx == sgn:
            continue
        for k, (dy, dl) in enumerate([(-4, -8), (4, 2), (12, 12)]):
            x0 = CXH + sx * 58
            wv = 3 * math.sin(t * 2.3 + k + sx)
            ln = 1.0 - .5 * away
            s.append(line([(x0, 1128 + dy * .8), (x0 + sx * 50 * ln, 1126 + dy + dl * .5 + wv * .5), (x0 + sx * 96 * ln, 1124 + dy * 1.2 + dl + wv)],
                          1.4, "#cfcbe0", seed=270 + k + sx, op=.9))
    mk = st.get("milk", 0.0)
    if mk > .02:      # капля молока на усах справа
        x0, y0 = CXH + 40, 1146
        r = 7 * mk
        s.append(shape([(x0, y0 - 2 * r), (x0 + r, y0), (x0 + r * .7, y0 + r * 1.1), (x0, y0 + r * 1.4), (x0 - r * .7, y0 + r * 1.1), (x0 - r, y0)],
                       MILK, blob(ellipse_pts(x0 - r * .3, y0, r * .3, r * .4, 8), "#ffffff"), w=2.2, seed=320))
        s.append(blob(ellipse_pts(CXH - 24, 1129, 9 * mk, 4 * mk, 10), MILK))      # молочный ус на губе
    return "".join(s)


# ───────────────────────────── передние лапы ─────────────────────────────
def _paw_leg(top, foot, w=40.0, seed=0, pad=False):
    tx, ty = top
    fx, fy = foot
    d = np.array([fx - tx, fy - ty], float)
    L = float(np.linalg.norm(d)) + 1e-6
    u = d / L
    n = np.array([-u[1], u[0]])
    h = w / 2
    pts = [tuple(np.array(top) + n * h * 1.05), tuple(np.array(top) + n * h * .98 + u * L * .55)]
    for a in np.linspace(0, math.pi, 9):
        pts.append(tuple(np.array(foot) + n * h * 1.08 * math.cos(a) + u * h * .95 * math.sin(a)))
    pts += [tuple(np.array(top) - n * h * .98 + u * L * .55), tuple(np.array(top) - n * h * 1.05)]
    inner = blob([tuple(np.array(top) - n * h * 1.2), tuple(np.array(top) - n * h * .2), tuple(np.array(foot) - n * h * .2 + u * h),
                  tuple(np.array(foot) - n * h * 1.3 + u * h)], CAT_SH, .7)
    o = shape(pts, CAT, inner, w=4.6, seed=seed)
    if pad:
        c = np.array(foot) + u * h * .2
        o += blob(ellipse_pts(c[0], c[1], 12, 9, 10), PAD)
        for kk in (-1, 0, 1):
            q = c + n * kk * 14 + u * (14 - 4 * abs(kk))
            o += blob(ellipse_pts(q[0], q[1], 4.6, 4, 8), PAD)
    else:
        for kk in (-7, 7):
            a = np.array(foot) + n * kk + u * (h * .55)
            o += line([tuple(a - u * 11), tuple(a)], 2.2, seed=seed + 5 + kk)
    return o


def body_f(st, t):
    s = []
    bt = st.get("body_turn", 0.0)
    walk = st.get("walk")
    bd = [(760, 1296), (744, 1240), (756, 1180), (790, 1142), (880, 1142), (916, 1180), (928, 1240), (912, 1296)]
    bp = fur(bd, 7, 7, seed=22)
    shx = -70 * bt if bt < 0 else 0
    inner = blob([(860 + shx, 1140), (930, 1180), (930, 1300), (874 + shx, 1300), (888 + shx, 1220)], CAT_SH, .9)
    if bt > 0:     # туловище повёрнуто вправо: грудь уходит вправо, левая половина — бок и спина в тени
        inner += blob([(744, 1150), (800 + 70 * bt, 1150), (810 + 70 * bt, 1300), (744, 1300)], CAT_SH, .6 * bt)
    elif bt < 0:   # влево: тень на правой половине
        inner += blob([(928, 1150), (872 + 70 * bt, 1150), (862 + 70 * bt, 1300), (928, 1300)], CAT_SH, .5 * -bt)
    gx = 120 * bt
    inner += blob([(798 + gx, 1170), (836 + gx, 1160), (874 + gx, 1170), (864 + gx, 1244), (836 + gx, 1266), (808 + gx, 1244)], CAT_FUR, .6 * (1 - .6 * abs(bt)))
    for i, p in enumerate([[(816, 1190), (826, 1208)], [(852, 1192), (846, 1212)], [(834, 1214), (836, 1236)], [(806, 1222), (814, 1238)],
                           [(864, 1226), (858, 1244)]]):
        inner += line(lib.T(p, gx * .5, 0), 2.2, CAT_EDGE, seed=240 + i, op=.85)
    s.append(shape(bp, CAT, inner, w=5, seed=241))
    for sx, sd in [(-1, 242), (1, 243)]:          # задние лапы
        px = CX + sx * 70 + 18 * bt
        hl = 0.0
        if walk is not None:
            hl = max(0.0, math.sin(2 * math.pi * walk + (math.pi if sx < 0 else 0))) * 12
        foot = ellipse_pts(px, 1286 - hl, 34, 26, 12, rot=sx * 12)
        s.append(shape(foot, CAT, blob(lib.T(ellipse_pts(px, 1292 - hl, 26, 20, 10), sx * 4, 0), CAT_SH, .5), w=4.6, seed=sd))
        if abs(bt) < .6 or sx * bt < 0:
            s.append(blob(ellipse_pts(px + sx * 3, 1296 - hl, 13, 10, 10, rot=sx * 10), PAD))
            for k in range(3):
                ang = math.radians(-90 + (k - 1) * 42 + sx * 10)
                s.append(blob(ellipse_pts(px + sx * 3 + math.cos(ang) * 19, 1296 - hl + math.sin(ang) * 15, 5, 4.4, 8), PAD))
    paw, shk = st.get("paw", 0.0), st.get("paw_shake", 0.0)
    for sx, sd in [(-1, 244), (1, 245)]:          # передние лапы
        fx = CX + sx * 25 + 40 * bt
        lift = 0.0
        if walk is not None:
            lift = max(0.0, math.sin(2 * math.pi * walk + (0 if sx < 0 else math.pi))) * 30
        dx = 0.0
        if sx > 0 and paw > 0:
            lift += 60 * paw
            dx = 30 * paw + 10 * paw * math.sin(2 * math.pi * shk)
            lift += 8 * paw * math.cos(2 * math.pi * shk)
        foot = (fx + dx, 1290 - lift)
        top = (fx + 4 * sx, 1206)
        s.append(_paw_leg(top, foot, 42, seed=sd, pad=(sx > 0 and paw > .45)))
        if sx > 0 and paw > .45 and shk:     # штрихи отряхивания
            for j in range(2):
                a = -.6 + j * .9
                q = (foot[0] + 34 + 8 * j, foot[1] - 10 + 18 * j)
                s.append(line([q, (q[0] + 20 * math.cos(a), q[1] + 20 * math.sin(a))], 3 * paw, INK, seed=330 + j, taper=.6))
    return "".join(s)


def draw_f(x, y, k, st, t):
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1)
    sx, sy = st.get("sx", 1.0), st.get("sy", 1.0) * br
    bt = st.get("body_turn", 0.0)
    tail = (f'<g transform="translate({-40 * bt:.1f} 0) rotate({st.get("tail", 0.0):.2f} {Cat.TAIL_PIVOT[0]} {Cat.TAIL_PIVOT[1]})">{Cat.tail_art()}'
            f'{Cat.flame(t, 1.3, st.get("flame_e", 1.0))}</g>')
    o = [tail]
    cr = st.get("crouch", 0.0)
    sy *= 1 - .3 * cr
    sx *= 1 + .06 * cr
    o.append(f'<g transform="translate({CX} {CBOT}) scale({sx:.4f} {sy:.4f}) translate({-CX} {-CBOT})">{body_f(st, t)}</g>')
    if cr > .02:     # пригнулся к миске: лопатки и спина горбом над опущенной головой
        hp = fur([(744, 1250), (752, 1180 - 40 * cr), (790, 1130 - 50 * cr), (836, 1118 - 52 * cr), (884, 1130 - 50 * cr), (922, 1180 - 40 * cr),
                  (930, 1250)], 7, 6, seed=29)
        inner = blob([(870, 1100), (940, 1150), (940, 1260), (880, 1260)], CAT_SH, .85)
        inner += blob(ellipse_pts(812, 1110 - 40 * cr, 50, 14, 10), CAT_FUR, .55)
        inner += line([(800, 1150 - 40 * cr), (812, 1132 - 44 * cr)], 2.2, CAT_EDGE, seed=298, op=.8)
        inner += line([(866, 1150 - 40 * cr), (856, 1132 - 44 * cr)], 2.2, CAT_EDGE, seed=299, op=.8)
        o.append(shape(hp, CAT, inner, w=5, seed=296))
    hy = -(sy - 1) * (CBOT - NECK[1]) + st.get("head_dy", 0.0) + 70 * st.get("drop", 0.0)
    o.append(f'<g transform="translate({st.get("head_dx", 0.0):.2f} {hy:.2f}) rotate({st.get("tilt", 0.0):.2f} {NECK[0]} {NECK[1]})">'
             f'{head_f(st, t)}</g>')
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({st.get("rot", 0.0):.2f}) scale({k:.4f}) translate({-CX} {-CBOT})">{"".join(o)}</g>'


def head_world(x, y, k, st):
    return x + st.get("head_dx", 0.0) * k, y + (1072 - CBOT + st.get("head_dy", 0.0) + 70 * st.get("drop", 0.0)) * k
