"""Сцена brain рилса 28 (s06, s07): мозг рилсов 24–26 с ручками (scene_brain.py, brain_art.py без изменений), без лица.
s06 «мозг тратит силы, чтобы не тянуться к нему» (10.88–13.28): справа на табурете телефон экраном вниз. Правая ручка
     тянется к нему и дрожит, левая обхватила её за предплечье и держит; пот, черточки усилия. На «тянуться» (12.36)
     правая рывком дёргается к телефону, левая перехватывает и тянет назад (пружина), мозг сплющивается от натуги.
s07 «и на учёбу остаётся меньше» (13.28–15.17): слева шкала сил из 10 делений над учебником. Сверху вниз 8 делений по
     очереди гаснут — их свет сгустком утекает в сцепленные руки; к учебнику остаются 2 деления, на «меньше» (14.4) они
     вспыхивают и тонкой струйкой дотягиваются до учебника. Всё — функция общего времени ролика t."""
import math

import numpy as np

import brain_art
import lib
import scene_brain as sb
from brain_art import BCX, BCY
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, mix,
                 rad_grad, rect_pts, shape, smooth, spring, svg)

_ST = {}
JERK = 12.36      # «тянуться»
LESS = 14.40      # «меньше»
PHONE = (985, 1020)            # центр телефона (лежит на табурете)
STOOL_TOP = 1038
GAUGE = (52, 330, 168, 940)  # x0, y0, x1, y1 шкалы
CELLS = 10
DRAIN0, DRAIN_DT = 13.34, 0.125


# ───────────────────────── предметы
def stool():
    s = []
    x0, x1 = 860, 1110
    s.append(sb.shadow(985, sb.FLOOR + 4, 150, .5))
    for k, (xa, xb) in enumerate([(888, 870), (1082, 1100), (950, 944), (1022, 1028)]):
        col = "#8a5a36" if k < 2 else "#6e4528"
        s.append(shape([(xa - 12, STOOL_TOP + 20, 1), (xa + 12, STOOL_TOP + 20, 1), (xb + 12, sb.FLOOR, 1), (xb - 12, sb.FLOOR, 1)], col,
                       blob([(xa + 2, STOOL_TOP + 20), (xa + 12, STOOL_TOP + 20), (xb + 12, sb.FLOOR), (xb + 2, sb.FLOOR)], "#5a3820", .8),
                       w=3.6, seed=900 + k))
    s.append(shape(rect_pts(880, STOOL_TOP + 52, 1090, STOOL_TOP + 70), "#7a4c2c", "", w=3.2, seed=905))
    top = rect_pts(x0, STOOL_TOP, x1, STOOL_TOP + 30, 10)
    s.append(shape(top, "#b07a48", blob(rect_pts(x0, STOOL_TOP + 16, x1, STOOL_TOP + 30), "#8a5a36", .9) +
                   line([(x0 + 20, STOOL_TOP + 7), (x1 - 40, STOOL_TOP + 6)], 3.4, "#d8a874", seed=906, op=.8), w=4.4, seed=907))
    return "".join(s)


def phone_down(x, y, sd=0, sc=1.0):
    """Телефон экраном вниз, вид сверху-спереди: тёмная крышка, блок камер, кромка экрана снизу."""
    s = []
    s.append(blob(ellipse_pts(x, y + 22, 118, 16, 14), "#2a1a10", .45, blur(5)))
    side = [(x - 116, y + 4, 1), (x + 116, y + 4, 1), (x + 112, y + 20, 1), (x - 112, y + 20, 1)]
    s.append(shape(side, "#1a1d26", "", w=3.4, seed=sd + 1))
    top = [(x - 110, y - 26, 1), (x + 110, y - 26, 1), (x + 118, y + 6, 1), (x - 118, y + 6, 1)]
    inner = blob([(x + 10, y - 26), (x + 110, y - 26), (x + 118, y + 6), (x + 30, y + 6)], "#262a36", .9)
    inner += line([(x - 96, y - 20), (x + 40, y - 21)], 3.4, "#6a7290", seed=sd + 2, op=.8)
    s.append(shape(top, "#353a4a", inner, w=4.2, seed=sd + 3))
    # блок камер (кольца) у дальнего края
    s.append(shape([(x - 92, y - 22, 1), (x - 46, y - 22, 1), (x - 50, y - 6, 1), (x - 96, y - 6, 1)], "#2a2e3c", "", w=2.8, seed=sd + 4))
    for k, cx in enumerate((x - 82, x - 62)):
        s.append(f'<ellipse cx="{f(cx)}" cy="{f(y - 14)}" rx="8" ry="4.6" fill="#11131a" stroke="{INK}" stroke-width="2.2"/>'
                 f'<ellipse cx="{f(cx - 2)}" cy="{f(y - 15.5)}" rx="2.6" ry="1.4" fill="#8fa0d0"/>')
    if sc != 1.0:
        return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)}) translate({f(-x)} {f(-y)})">{"".join(s)}</g>'
    return "".join(s)


def book(x, y, glow, sd=0):
    """Учебник, лежит раскрытым на полу (центр корешка x, y); glow 0..1 — тёплый свет страниц."""
    s = []
    s.append(blob(ellipse_pts(x, y + 30, 190, 22, 14), "#141b38", .5, blur(6)))
    if glow > 0.01:
        g = rad_grad([(0, "#fff1b8", .75 * glow), (1, "#fff1b8", 0)], x, y - 20, 210, 120)
        s.append(f'<ellipse cx="{f(x)}" cy="{f(y - 20)}" rx="210" ry="120" fill="url(#{g})"/>')
    # обложка
    s.append(shape([(x - 176, y - 2, 1), (x + 176, y - 2, 1), (x + 170, y + 30, 1), (x - 170, y + 30, 1)], "#2e6fb6",
                   blob([(x - 176, y + 16), (x + 176, y + 16), (x + 170, y + 30), (x - 170, y + 30)], "#1f4f86"), w=4.2, seed=sd + 1))
    pc = mix("#c9c3b4", "#fffaf0", 0.35 + 0.65 * glow)
    psh = mix("#a39d8f", "#efe6d2", 0.35 + 0.65 * glow)
    for side in (-1, 1):
        pts = [(x, y - 30), (x + side * 70, y - 46), (x + side * 160, y - 40), (x + side * 168, y + 6, 1), (x + side * 80, y + 4), (x, y + 14, 1)]
        if side < 0:
            pts = pts[::-1]
        inner = blob([(x, y - 30), (x + side * 26, y - 36), (x + side * 26, y + 12), (x, y + 14)], psh, .8)
        for k in range(4):
            yy = y - 30 + k * 10
            inner += line([(x + side * 34, yy - 6 + k * 1.5), (x + side * 92, yy - 12 + k * 1.5), (x + side * 146, yy - 8 + k * 1.5)],
                          3.4, "#7e8aa8", taper=.3, wmin=.4, seed=sd + 10 + k + (side > 0) * 5, op=.85)
        s.append(shape(pts, pc, inner, w=3.8, seed=sd + 3 + (side > 0)))
    s.append(line([(x, y - 30), (x, y + 13)], 3.6, INK, taper=.2, seed=sd + 8))
    return "".join(s)


# ───────────────────────── руки-«борьба»
def grip_pose(t):
    """Где правая кисть (тянется к телефону) и насколько её дёрнуло. Возвращает (wrist, ang, lunge 0..1)."""
    tremble = 5 * math.sin(t * 41) + 3 * math.sin(t * 67 + 1)
    creep = 0.35 + 0.25 * math.sin(t * 1.3)            # потихоньку ползёт к телефону и обратно
    e = t - JERK
    lunge = 0.0
    if e > -0.06:
        u = clamp((e + 0.06) / 0.12)
        out = ease_out(u, 3)
        back = 1 - spring(max(e - 0.10, 0), 2.2, 6.0) if e > 0.10 else 1.0
        lunge = out * back
    base = (742 + 26 * creep, 880 + 14 * creep)
    tgt = (838, 944)
    wx = base[0] + (tgt[0] - base[0]) * lunge + tremble * 0.6
    wy = base[1] + (tgt[1] - base[1]) * lunge + tremble * 0.4
    ang = 24 + 8 * lunge + 2 * math.sin(t * 37)
    return (wx, wy), ang, lunge, tremble


def struggle(t, pose, extra_grip_glow=0.0):
    """Мозг, правая ручка к телефону, левая держит правую за предплечье. Кисть левой — кулак поверх предплечья."""
    wr, ar, lunge, tr = grip_pose(t)
    SL = pose.pt(*sb.SH_L)
    SR = pose.pt(*sb.SH_R)
    # правая ручка: от плеча к запястью; точка хвата на ~62% длины
    bend_r = -26 - 10 * lunge
    dx, dy = wr[0] - SR[0], wr[1] - SR[1]
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    C = ((SR[0] + wr[0]) / 2 + nx * bend_r, (SR[1] + wr[1]) / 2 + ny * bend_r)
    u = 0.70
    gp = ((1 - u) ** 2 * SR[0] + 2 * (1 - u) * u * C[0] + u * u * wr[0], (1 - u) ** 2 * SR[1] + 2 * (1 - u) * u * C[1] + u * u * wr[1])
    tx, ty = 2 * (1 - u) * (C[0] - SR[0]) + 2 * u * (wr[0] - C[0]), 2 * (1 - u) * (C[1] - SR[1]) + 2 * u * (wr[1] - C[1])
    ta = math.degrees(math.atan2(ty, tx))
    # левая кисть обхватывает сверху: пальцы поперёк предплечья, вниз; запястье над ним (ближе к мозгу)
    ga = ta + 90                      # поперёк
    pull = 18 * lunge
    lw = (gp[0] - math.cos(math.radians(ga)) * 40 - pull * 0.6, gp[1] - math.sin(math.radians(ga)) * 40 - pull * 0.2)
    s = []
    s.append(sb.arm(SL, lw, 70 + 30 * lunge, 11, pose.sc))                 # левая ручка — под мозгом, провисает
    s.append(sb.arm(SR, wr, bend_r, 12, pose.sc))
    s.append(f'<g transform="{pose.tf()}">{_ST["brain"]}</g>')
    # правая кисть: растопыренные пальцы тянутся к телефону, на рывке — шире
    s.append(sb.toon_hand(wr[0], wr[1], ar, 0.15 + 0.25 * (1 - lunge), 30, pose.sc * 1.3, spread=1.2 + 0.4 * lunge))
    if extra_grip_glow > 0.01:
        g = rad_grad([(0, "#9dffb2", .8 * extra_grip_glow), (1, "#9dffb2", 0)], gp[0], gp[1], 120, 120)
        s.append(f'<circle cx="{f(gp[0])}" cy="{f(gp[1])}" r="120" fill="url(#{g})"/>')
    s.append(sb.toon_hand(lw[0], lw[1], ga, 0.92, 60, pose.sc * 1.3, spread=0.8))
    return "".join(s), gp, wr, lunge


def strain_fx(t, pose, lunge):
    """Капли пота (стекают и срываются), черточки натуги у макушки."""
    s = []
    top = pose.pt(BCX - 20, BCY - 150)
    s.append(sb.effort_lines(top[0] + 10, top[1] + 120, 175, t, a0=-2.55, n=4, col="#e9eeff"))
    s.append(sb.effort_lines(top[0] + 10, top[1] + 120, 175, t + 0.21, a0=-0.95, n=3, col="#e9eeff"))
    for k, (lx, ly, ph) in enumerate([(BCX - 150, BCY - 90, 0.0), (BCX + 150, BCY - 70, 0.37), (BCX - 40, BCY - 140, 0.71)]):
        cyc = 0.9
        e = ((t - 10.5) / cyc + ph) % 1.0
        x, y = pose.pt(lx, ly)
        side = -1 if lx < BCX else 1
        dy = 60 * ease_in(e, 2) + 20 * e
        sc = 0.9 * back_out(clamp(e / 0.18), 2) * (1 - smooth(0.82, 1.0, e))
        s.append(sb.sweat(x + side * 14 * e, y + dy, sc * (1 + 0.3 * lunge)))
    return "".join(s)


def brain_pose(t):
    wr, ar, lunge, tr = grip_pose(t)
    breath = 1 + 0.012 * math.sin(t * 2.6)
    strain = 0.035 * math.sin(t * 13)                  # трясётся от натуги
    lean = 3.5 + 7 * lunge + 1.6 * math.sin(t * 9)
    pose = sb.Pose(430 + 22 * lunge + 2.5 * math.sin(t * 23), 500 + 6 * math.sin(t * 2.6) - 10 * lunge, 1.0 * breath,
                   lean, 1 - 0.06 * lunge - 0.02 + strain * 0.4)
    return pose, lunge


def jerk_lines(t):
    """Рывок: три линии движения за кистью и «удар»-звёздочка на перехвате."""
    e = t - JERK
    if e < 0 or e > 0.42:
        return ""
    s = []
    a = 1 - e / 0.42
    for k in range(3):
        y = 860 + k * 34
        s.append(line([(660 - 30 * k, y), (760 - 20 * k, y + 18)], 7, "#e9eeff", taper=.6, seed=950 + k, op=a))
    if 0.08 < e < 0.4:
        u = (e - 0.08) / 0.32
        cx, cy = 690, 840
        for k in range(8):
            ang = k * math.pi / 4 + 0.3
            r0 = 40 + 70 * ease_out(u)
            L = 34 * (1 - u)
            s.append(line([(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0), (cx + math.cos(ang) * (r0 + L), cy + math.sin(ang) * (r0 + L))],
                          8, "#ffe27a", taper=.5, seed=960 + k))
    return "".join(s)


def phone_pull(t):
    """Телефон «тянет»: чуть подрагивает к мозгу и по краю дышит холодный отсвет — молчит, но манит."""
    x, y = PHONE
    wob = 1.5 * math.sin(t * 5.3)
    g = rad_grad([(0, "#7fa8ff", .32 + .12 * math.sin(t * 3.1)), (1, "#7fa8ff", 0)], x, y - 4, 190, 70)
    s = f'<ellipse cx="{f(x)}" cy="{f(y - 4)}" rx="190" ry="70" fill="url(#{g})"/>'
    rot = 1.2 * math.sin(t * 4.1) + (2.5 * math.exp(-max(t - JERK - .1, 0) * 7) * math.sin((t - JERK) * 40) if t > JERK + .1 else 0)
    return s + f'<g transform="rotate({f(rot)} {x} {y + 10}) translate({f(wob)} 0)">{_ST["phone"]}</g>'


# ───────────────────────── шкала сил
def cell_rect(i):
    """i = 0 — нижнее деление."""
    x0, y0, x1, y1 = GAUGE
    pad, gap = 12, 8
    h = (y1 - y0 - 2 * pad - gap * (CELLS - 1)) / CELLS
    yb = y1 - pad - i * (h + gap)
    return x0 + pad, yb - h, x1 - pad, yb


def drain_time(i):
    """Делит сверху: i = 9 первым ... i = 2 последним; два нижних (0, 1) остаются."""
    if i < 2:
        return None
    return DRAIN0 + (9 - i) * DRAIN_DT


def gauge(t, appear):
    x0, y0, x1, y1 = GAUGE
    s = []
    k = back_out(clamp(appear), 1.6)
    if k <= 0.01:
        return ""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    body = shape(rect_pts(x0, y0, x1, y1, 22), "#2a3358", blob(rect_pts(x0 + 50, y0, x1, y1, 22), "#222a4a", .8), w=5.2, seed=980)
    body += shape(rect_pts(cx - 34, y0 - 26, cx + 34, y0 + 4, 8), "#3a4572", "", w=4, seed=981)
    for i in range(CELLS):
        a0, b0, a1, b1 = cell_rect(i)
        td = drain_time(i)
        lit = 1.0 if td is None else 1 - smooth(td, td + 0.10, t)
        flash = 0.0 if td is None else math.exp(-max(t - td, 0) * 10) * (t > td)
        if i < 2 and t > LESS:
            flash = 0.8 * math.exp(-(t - LESS) * 5) + 0.15 * (0.5 + 0.5 * math.sin((t - LESS) * 9))
        col = mix("#3a4470", "#4fdc7a", lit)
        hi = mix("#46507c", "#a8ffbf", lit)
        if flash > 0:
            col = mix(col, "#e8ffe9", min(1, flash * 0.7))
        body += shape(rect_pts(a0, b0, a1, b1, 7), col, blob(rect_pts(a0 + 8, b0 + 5, a1 - 30, b0 + 13, 4), hi, .85 * max(lit, .3)), w=3.2, seed=990 + i)
    # тень на полу под шкалой
    out = blob(ellipse_pts(cx, sb.FLOOR + 4, 90, 12, 12), "#141b38", .45, blur(6))
    out += f'<g transform="translate({f(cx)} {f(y1)}) scale({f(k)}) translate({f(-cx)} {f(-y1)})">{body}</g>'
    return out


def flows(t, gp):
    """Свет погасших делений сгустком летит по дуге в сцепленные руки."""
    s = []
    for i in range(2, CELLS):
        td = drain_time(i)
        e = t - td
        dur = 0.42
        if e < 0 or e > dur + 0.05:
            continue
        a0, b0, a1, b1 = cell_rect(i)
        p0 = ((a0 + a1) / 2, (b0 + b1) / 2)
        c = ((p0[0] + gp[0]) / 2 + 40, min(p0[1], gp[1]) - 220)
        u = ease_in(clamp(e / dur), 1.4)
        tail = []
        for j in range(8):
            v = clamp(u - j * 0.045)
            tail.append(((1 - v) ** 2 * p0[0] + 2 * (1 - v) * v * c[0] + v * v * gp[0], (1 - v) ** 2 * p0[1] + 2 * (1 - v) * v * c[1] + v * v * gp[1]))
        if u < 1:
            s.append(line(tail[::-1], 16, "#7dff9a", taper=.95, wmin=.2, seed=1000 + i, op=.85))
            hx, hy = tail[0]
            s.append(f'<circle cx="{f(hx)}" cy="{f(hy)}" r="15" fill="#e8ffe9" stroke="#2f9c55" stroke-width="3"/>')
    return "".join(s)


def book_stream(t, gp_book):
    """На «меньше»: от двух оставшихся делений к учебнику — тонкая струйка (2 искры бегут вниз)."""
    if t < LESS - 0.05:
        return ""
    s = []
    a0, b0, a1, b1 = cell_rect(0)
    p0 = ((a0 + a1) / 2, b1 + 14)
    p1 = gp_book
    k = smooth(LESS - 0.05, LESS + 0.15, t)
    s.append(line([p0, ((p0[0] + p1[0]) / 2 + 30, (p0[1] + p1[1]) / 2), p1], 5, "#7dff9a", taper=.1, wmin=.8, seed=1100, op=.7 * k))
    for j in range(2):
        v = ((t - LESS) * 1.4 + j * 0.5) % 1.0
        x = (1 - v) ** 2 * p0[0] + 2 * (1 - v) * v * ((p0[0] + p1[0]) / 2 + 30) + v * v * p1[0]
        y = (1 - v) ** 2 * p0[1] + 2 * (1 - v) * v * ((p0[1] + p1[1]) / 2) + v * v * p1[1]
        s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(8 * k)}" fill="#e8ffe9" stroke="#2f9c55" stroke-width="2.4"/>')
    return "".join(s)


# ───────────────────────── кадры
def common(t, grip_glow=0.0):
    pose, lunge = brain_pose(t)
    body, gp, wr, lunge = struggle(t, pose, grip_glow)
    art = sb.shadow(pose.x + 40, sb.FLOOR + 8, 190, .45) + _ST["stool"] + phone_pull(t) + body + strain_fx(t, pose, lunge) + jerk_lines(t)
    return art, gp, pose, lunge


def s06(t):
    art, gp, pose, lunge = common(t)
    u = clamp((t - 10.68) / 2.8)
    jolt = 0.04 * math.exp(-max(t - JERK, 0) * 6) * (t > JERK)
    shake = 6 * math.exp(-max(t - JERK - .1, 0) * 9) * math.sin((t - JERK) * 55) * (t > JERK + .1)
    cm = cam(655 + 10 * u + shake, 770 - 10 * u, 1.04 + 0.09 * (0.4 * u + 0.6 * ease_io(u)) + jolt, -0.8 + 1.2 * u)
    return art, cm


def s07(t):
    # сгустки, долетевшие до рук, — короткая вспышка хвата
    glow = 0.0
    for i in range(2, CELLS):
        e = t - drain_time(i) - 0.42
        if 0 < e < 0.3:
            glow = max(glow, 1 - e / 0.3)
    art, gp, pose, lunge = common(t, glow)
    bk = (190, 1096)
    gl = 0.25 + 0.45 * smooth(LESS, LESS + 0.3, t) * (0.8 + 0.2 * math.sin((t - LESS) * 6))
    appear = (t - 13.12) / 0.3
    left = book(bk[0], bk[1], gl * clamp(appear), sd=1200) + gauge(t, appear) + book_stream(t, (bk[0] + 10, bk[1] - 40))
    art = left + art + flows(t, gp)
    u = clamp((t - 13.08) / 2.3)
    pop = 0.025 * math.exp(-max(t - LESS, 0) * 6) * (t > LESS)
    cm = cam(598 - 10 * u, 790, 0.94 + 0.025 * ease_io(u) + pop, 0.5 - 0.7 * u)
    return art, cm


def build_static():
    if _ST:
        return
    sb.build_static()
    _ST["bg"] = sb._ST["bg"]
    _ST["brain"] = sb._ST["brain"]
    _ST["stool"] = stool()
    _ST["phone"] = phone_down(*PHONE, sd=920)
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    art, cm = {"s06": s06, "s07": s07}[sid](t)
    return svg(f'<rect width="{W}" height="{H}" fill="#1f2747"/><g transform="{cm}">{_ST["bg"]}{sb.dust(t)}{art}</g>')
