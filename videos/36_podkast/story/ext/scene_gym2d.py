"""Сцены gym2d рилса 36 (s10, s11, s12): спортзал опыта Milkman 2014 — светлые стены, серо-зелёный пол. Без букв.
s10 «аудиокнигу только в зале» (15.3–17.75): шкафчик у входа в зал, дверца открыта, на полке плеер с белыми
     наушниками; на «аудиокнигу» (15.88) экран плеера загорается иконкой книги, от него звуковые волны; дверца
     захлопывается, на «только» (16.68) рука вешает на дверцу замок-гантель; камера отъезжает: человек в спортивном
     входит в зал через порог (за порогом — беговые дорожки), на «зале» (17.24) замок отщёлкивается, дверца
     распахивается, человек берёт наушники.
s11 «И они стали ходить туда заметно чаще» (17.75–19.9): зал — двое на беговых дорожках и женщина на велотренажёре, все в
     наушниках; на стене календарь-месяц, с «ходить» (18.48) клетки быстро заполняются зелёными галочками, на «чаще»
     (19.52) последняя — с ударом.
s12 «просто чтобы узнать, что дальше» (19.9–21.9): крупно женщина на велотренажёре в наушниках: глаза распахнуты,
     крутит педали всё быстрее; на «узнать» (20.68) подаётся вперёд, на «дальше» (21.28) над ней облачко с книгой и «!».
Всё — функция общего времени ролика t."""
import math

import numpy as np

import lib
import parts34 as P
import person
from lib import (INK, W, H, back_out, blob, blur, cam, clamp, ease_in, ease_io, ease_out, ellipse_pts, f, line, rad_grad,
                 rect_pts, shape, smooth, svg)

_ST = {}
AUDIO = P.wt("аудиокнигу")        # 15.88
TOLKO = P.wt("только", 16)        # 16.68
ZALE = P.wt("зале", 17)           # 17.24
HODIT = P.wt("ходить", 18)        # 18.48
CHASCHE = P.wt("чаще")            # 19.52
UZNAT = P.wt("узнать")            # 20.68
DALSHE = P.wt("дальше")           # 21.28

FLOOR = 1180
WALL, WALL_SH, FLOOR_C, FLOOR_SH = "#eef0e8", "#dfe3d8", "#a9b8a6", "#93a491"
STEEL, STEEL_SH, STEEL_DK = "#c9ced8", "#9aa2b2", "#6b7385"
BELT, DECK, MACH = "#5b5f6a", "#2a2d36", "#3a3e4a"

# люди в спортивном (у всех белые наушники)
MAN_A = dict(skin="#f2c9a8", hair="short", hair_c="#3a2418", top="#e8762a", low="#2a2f44", track="#ffffff", zip=True, face=.35, shoes="#f2eee6", phones=True)
MAN_B = dict(skin="#6b4430", hair="short", hair_c="#1c1412", top="#2f6db5", low="#24304a", track="#ffffff", face=.35, shoes="#e2543f", phones=True)
WOMAN = dict(skin="#d9a477", hair="ponytail", hair_c="#2a1a14", top="#d9467a", low="#2a2a3a", track="#f2eee6", face=.35, lashes=True, shoes="#f2eee6",
             phones=True)
MAN_C = dict(skin="#e8b890", hair="curly", hair_c="#5a3420", top="#3a9a6a", low="#3a3f4c", track="#ffd23a", zip=True, face=.35, shoes="#3a3440")


# ═══════════════════════════════ общие предметы
def room(door=False):
    s = []
    s.append(f'<rect x="-1400" y="-1200" width="{W + 2800}" height="{FLOOR + 1200}" fill="{WALL}"/>')
    g = rad_grad([(0, "#ffffff", .7), (1, "#ffffff", 0)], 560, 420, 800, 600)
    s.append(f'<rect x="-1400" y="-1200" width="{W + 2800}" height="{FLOOR + 1200}" fill="url(#{g})"/>')
    # полоса по стене
    s.append(blob(rect_pts(-1400, 760, W + 1400, 800), "#7fc2b8"))
    s.append(blob([(-1400, FLOOR), (W + 1400, FLOOR), (W + 1400, H + 1200), (-1400, H + 1200)], FLOOR_C))
    s.append(blob(rect_pts(-1400, FLOOR - 26, W + 1400, FLOOR), "#d4d8cc"))
    s.append(line([(-1400, FLOOR - 26), (W + 1400, FLOOR - 26)], 2.6, INK, taper=.05, wmin=.8, seed=3001, op=.8))
    s.append(line([(-1400, FLOOR), (W + 1400, FLOOR)], 4.2, INK, taper=.05, wmin=.9, seed=3002))
    for k in range(-10, 18):
        x = 540 + k * 170
        s.append(line([(540 + (x - 540) * .45, FLOOR + 6), (x, H + 900)], 2.2, FLOOR_SH, taper=.1, wmin=.7, seed=3010 + k % 9, op=.8))
    return "".join(s)


def window(x0, y0, x1, y1, sd):
    inner = blob(rect_pts(x0, y0, x1, y1), "#a6d4f5")
    inner += blob([(x0, y1 - 60), (x0 + 80, y1 - 110), (x0 + 170, y1 - 80), (x1, y1 - 120), (x1, y1), (x0, y1)], "#8fbf7a")
    inner += line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], 6, "#f4f1e8", taper=.05, wmin=.9, seed=sd + 1)
    inner += blob([(x0 + 20, y1 - 30), (x0 + 70, y0 + 20), (x0 + 110, y0 + 20), (x0 + 40, y1 - 30)], "#ffffff", .35)
    return shape(rect_pts(x0, y0, x1, y1), "#a6d4f5", inner, w=4.6, seed=sd) + shape(rect_pts(x0 - 14, y1, x1 + 14, y1 + 16), "#f4f1e8", "", w=3.2, seed=sd + 2)


def treadmill(x, y, sc, t, speed=1.0, sd=4000, back=True, front=True):
    """Беговая дорожка сбоку (лицом вправо): низ деки (x — задний край, y — пол). back — дека и лента, front — стойка с
    поручнями и пульт (рисуется поверх бегуна)."""
    L = 470
    s = []
    if back:
        s.append(blob(ellipse_pts(x + L / 2 * sc, y + 4, (L / 2 + 30) * sc, 14 * sc, 14), "#7b8a78", .5, blur(4)))
        deck = rect_pts(x, y - 70 * sc, x + L * sc, y - 8 * sc, 30 * sc)
        inner = blob(rect_pts(x, y - 38 * sc, x + L * sc, y - 8 * sc), "#1a1c24", .9)
        s.append(shape(deck, DECK, inner, w=4, seed=sd))
        belt = rect_pts(x + 18 * sc, y - 84 * sc, x + (L - 18) * sc, y - 66 * sc, 9 * sc)
        bi = ""
        off = (t * 260 * speed) % 46
        for k in range(12):
            bx = x + (24 + k * 46 - off) * sc
            if x + 22 * sc < bx < x + (L - 22) * sc:
                bi += line([(bx, y - 82 * sc), (bx + 4 * sc, y - 68 * sc)], 2.4 * sc, "#3e424c", taper=.1, wmin=.8, seed=sd + 5 + k)
        s.append(shape(belt, BELT, bi, w=3.4, seed=sd + 1))
        for k, rx in enumerate((x + 22 * sc, x + (L - 22) * sc)):
            ang = -t * 360 * speed * 2
            s.append(shape(ellipse_pts(rx, y - 40 * sc, 16 * sc, 16 * sc, 12), STEEL, line([(rx - 10 * sc * math.cos(math.radians(ang)), y - 40 * sc - 10 * sc * math.sin(math.radians(ang))),
                                                                                         (rx + 10 * sc * math.cos(math.radians(ang)), y - 40 * sc + 10 * sc * math.sin(math.radians(ang)))],
                                                                                        3, STEEL_DK, seed=sd + 30 + k), w=3, seed=sd + 20 + k))
    if front:
        fx = x + (L - 40) * sc
        post = [(fx - 14 * sc, y - 60 * sc), (fx + 14 * sc, y - 60 * sc), (fx + 64 * sc, y - 520 * sc), (fx + 36 * sc, y - 520 * sc)]
        s.append(shape(post, MACH, blob([(fx, y - 60 * sc), (fx + 14 * sc, y - 60 * sc), (fx + 64 * sc, y - 520 * sc), (fx + 50 * sc, y - 520 * sc)], "#262a34", .9),
                       w=3.6, seed=sd + 40))
        # поручень — от стойки назад
        rail = [(fx + 40 * sc, y - 420 * sc), (fx - 150 * sc, y - 400 * sc)]
        s.append(line(rail, 18 * sc, INK, taper=.05, wmin=.95, seed=sd + 41))
        s.append(line(rail, 11 * sc, STEEL, taper=.05, wmin=.95, seed=sd + 42))
        # пульт
        con = [(fx + 6 * sc, y - 560 * sc, 1), (fx + 110 * sc, y - 600 * sc, 1), (fx + 120 * sc, y - 540 * sc, 1), (fx + 20 * sc, y - 506 * sc, 1)]
        ci = blob([(fx + 30 * sc, y - 558 * sc), (fx + 96 * sc, y - 582 * sc), (fx + 100 * sc, y - 552 * sc), (fx + 36 * sc, y - 530 * sc)], "#4fb3e8")
        for k in range(3):
            ci += f'<circle cx="{f(fx + (44 + k * 18) * sc)}" cy="{f(y - (528 + 12 - k * 6) * sc)}" r="{f(4 * sc)}" fill="{["#e2543f", "#ffd23a", "#3cbf63"][k]}"/>'
        s.append(shape(con, MACH, ci, w=3.6, seed=sd + 43))
    return "".join(s)


def bike(x, y, sc, t, crank, sd=4200, part="back"):
    """Велотренажёр сбоку (лицом вправо): x — центр каретки, y — пол. crank — угол шатунов (рад).
    part: back — рама, маховик, дальняя педаль; front — руль, седло, ближний шатун и педаль."""
    s = []
    k = sc
    if part == "back":
        s.append(blob(ellipse_pts(x + 20 * k, y + 4, 230 * k, 14 * k, 14), "#7b8a78", .5, blur(4)))
        # опоры
        for x0, x1 in ((-190, -90), (150, 250)):
            s.append(shape(rect_pts(x + x0 * k, y - 22 * k, x + x1 * k, y, 10 * k), MACH, "", w=3.4, seed=sd + int(x0)))
        # маховик спереди
        fw = (x + 170 * k, y - 170 * k)
        ang = crank * 2
        inner = blob(ellipse_pts(fw[0] + 10 * k, fw[1] + 12 * k, 76 * k, 76 * k, 18), "#262a34", .9)
        for j in range(3):
            a = ang + j * 2 * math.pi / 3
            inner += line([(fw[0], fw[1]), (fw[0] + 60 * k * math.cos(a), fw[1] + 60 * k * math.sin(a))], 5 * k, STEEL_DK, taper=.1, wmin=.9, seed=sd + 10 + j)
        s.append(shape(ellipse_pts(*fw, 92 * k, 92 * k, 24), MACH, inner, w=4, seed=sd + 5))
        s.append(shape(ellipse_pts(*fw, 18 * k, 18 * k, 10), STEEL, "", w=3, seed=sd + 6))
        # рама: от задней опоры к каретке, к рулевой стойке, к седлу
        frame = [(x - 140 * k, y - 18 * k), (x, y - 120 * k), (x + 120 * k, y - 300 * k)]
        s.append(line(frame, 30 * k, INK, taper=.05, wmin=.95, seed=sd + 20))
        s.append(line(frame, 22 * k, "#e2543f", taper=.05, wmin=.95, seed=sd + 21))
        s.append(line([(x, y - 120 * k), (x - 110 * k, y - 310 * k)], 30 * k, INK, taper=.05, wmin=.95, seed=sd + 22))
        s.append(line([(x, y - 120 * k), (x - 110 * k, y - 310 * k)], 22 * k, "#e2543f", taper=.05, wmin=.95, seed=sd + 23))
        s.append(line([(x + 200 * k, y - 18 * k), (x + 170 * k, y - 170 * k)], 22 * k, INK, taper=.05, wmin=.95, seed=sd + 24))
        s.append(line([(x + 200 * k, y - 18 * k), (x + 170 * k, y - 170 * k)], 14 * k, MACH, taper=.05, wmin=.95, seed=sd + 25))
        # дальний шатун и педаль
        a = crank + math.pi
        p = (x + 62 * k * math.cos(a), y - 120 * k + 62 * k * math.sin(a))
        s.append(line([(x, y - 120 * k), p], 12 * k, "#262a34", taper=.05, wmin=.95, seed=sd + 26))
        s.append(shape(rect_pts(p[0] - 22 * k, p[1] - 6 * k, p[0] + 22 * k, p[1] + 6 * k, 3 * k), "#262a34", "", w=2.6, seed=sd + 27))
    elif part == "seat":
        # седло (поверх бёдер не рисуется — седло под тазом, рисуется до человека)
        sx, sy = x - 116 * k, y - 318 * k
        s.append(shape([(sx - 60 * k, sy - 8 * k), (sx + 50 * k, sy - 14 * k), (sx + 70 * k, sy - 4 * k), (sx + 40 * k, sy + 14 * k), (sx - 56 * k, sy + 12 * k)],
                       "#2a2d36", blob(ellipse_pts(sx - 20 * k, sy - 6 * k, 30 * k, 4 * k, 8), "#4a4e5a", .9), w=3.6, seed=sd + 30))
    else:
        # руль и пульт — поверх рук
        hx, hy = x + 120 * k, y - 300 * k
        bar = [(hx, hy), (hx + 30 * k, hy - 60 * k), (hx - 30 * k, hy - 90 * k)]
        s.append(line(bar, 22 * k, INK, taper=.05, wmin=.95, seed=sd + 40))
        s.append(line(bar, 14 * k, "#262a34", taper=.05, wmin=.95, seed=sd + 41))
        s.append(shape(rect_pts(hx + 6 * k, hy - 150 * k, hx + 76 * k, hy - 96 * k, 8 * k), MACH,
                       blob(rect_pts(hx + 16 * k, hy - 140 * k, hx + 66 * k, hy - 110 * k, 4 * k), "#4fb3e8"), w=3.4, seed=sd + 42))
        s.append(line([(hx + 30 * k, hy - 60 * k), (hx + 38 * k, hy - 96 * k)], 10 * k, "#262a34", taper=.05, wmin=.95, seed=sd + 43))
        # ближний шатун и педаль
        p = (x + 62 * k * math.cos(crank), y - 120 * k + 62 * k * math.sin(crank))
        s.append(shape(ellipse_pts(x, y - 120 * k, 26 * k, 26 * k, 14), STEEL, blob(ellipse_pts(x + 6 * k, y - 114 * k, 18 * k, 18 * k, 10), STEEL_SH, .9),
                       w=3.4, seed=sd + 44))
        s.append(line([(x, y - 120 * k), p], 14 * k, INK, taper=.05, wmin=.95, seed=sd + 45))
        s.append(line([(x, y - 120 * k), p], 8 * k, STEEL, taper=.05, wmin=.95, seed=sd + 46))
    return "".join(s)


def bike_pedals(x, y, sc, crank):
    """Мировые точки педалей (ближняя, дальняя) и седла/руля для посадки человека."""
    k = sc
    near = (x + 62 * k * math.cos(crank), y - 120 * k + 62 * k * math.sin(crank))
    far = (x + 62 * k * math.cos(crank + math.pi), y - 120 * k + 62 * k * math.sin(crank + math.pi))
    return near, far, (x - 120 * k, y - 328 * k), (x + 96 * k, y - 384 * k)


def rider(spec, x, y, sc, t, crank, extra=None, sd=4400):
    """Человек на велотренажёре: таз на седле, ступни на педалях (IK), руки на руле."""
    extra = extra or {}
    near, far, seat, grip = bike_pedals(x, y, sc, crank)
    ps = sc * spec.get("h", 1.0)
    # начало координат человека: таз (y=-300 человека) — на седле
    ox, oy = seat[0] + 4 * sc, seat[1] + 300 * ps - 40 * sc
    lean = extra.get("lean", 8.0)

    def loc(p):
        return ((p[0] - ox) / ps, (p[1] - oy) / ps)
    legs = {}
    for side, pd in (("R", near), ("L", far)):
        hip = (26 if side == "R" else -26, -300)
        ft = loc((pd[0] - 6 * sc, pd[1] - 4 * sc))
        ft = (ft[0], ft[1] - 20)
        legs[side] = person.leg_ik(hip, ft)
    g = loc(grip)
    pose = {"legs": legs, "hand_target": {"R": (g[0], g[1] + 10), "L": (g[0] - 30, g[1] + 14)}, "curl": {"L": .75, "R": .75},
            "look": extra.get("look", (0.7, 0.1)), "mouth": extra.get("mouth", "smile"), "brow": extra.get("brow", 0.4),
            "head_tilt": extra.get("tilt", 2 * math.sin(t * 2)), "blink": extra.get("blink", 0.0), "eye_k": extra.get("eye_k", 1.0), "lean": lean}
    return person.draw(spec, pose, ox, oy, sc, sd=sd)


def run_pose(ph, look=(0.7, 0.0), mouth="smile", blink=0.0, tilt=0.0):
    """Бег на месте (лицом вправо): ноги — фаза ph, руки согнуты и машут в противофазе."""
    legs = {}
    for side, o in (("R", 0.0), ("L", math.pi)):
        p = ph + o
        a1 = 32 * math.sin(p)
        k = 18 + 60 * max(0.0, math.sin(p - 1.4))
        legs[side] = (a1, k)
    arms = {"R": (-28 * math.sin(ph), 95), "L": (28 * math.sin(ph), 95)}
    return {"legs": legs, "arms": arms, "look": look, "mouth": mouth, "brow": 0.4, "head_tilt": tilt, "blink": blink, "curl": {"L": .8, "R": .8}}


def runner(spec, x, y, sc, t, ph, sd, **kw):
    """Бегун на ленте дорожки: нижняя ступня всегда на ленте (y — верх ленты), тело подпрыгивает вместе с ней."""
    pose = run_pose(ph, **kw)
    low = max(-300 + 140 * (math.cos(math.radians(a1)) + math.cos(math.radians(a1 - k))) for a1, k in pose["legs"].values())
    low = min(low, -20)
    return person.draw(spec, pose, x, y - (low + 20) * sc * spec.get("h", 1.0), sc, sd=sd)


def sound_waves(x, y, t, t0, sc=1.0, col="#2fb3a8", side=1, n=3):
    if t < t0:
        return ""
    s = []
    for k in range(n):
        ph = ((t - t0) * 1.4 + k / n) % 1
        r = (30 + 110 * ph) * sc
        op = (1 - ph) * min(1, (t - t0) / 0.15)
        a0, a1 = -0.7, 0.7
        pts = [(x + side * r * math.cos(a), y + r * math.sin(a)) for a in np.linspace(a0, a1, 9)]
        s.append(line(pts, 9 * sc * (1 - .4 * ph), col, taper=.4, wmin=.5, seed=5000 + k, op=op))
    return "".join(s)


def book_icon(x, y, sc, sd=5100, col="#2fb3a8"):
    """Значок «книга»: раскрытая книга двумя страницами, без букв."""
    s = []
    for side in (-1, 1):
        pg = [(0, 8), (side * 4, -24), (side * 30, -30), (side * 52, -22), (side * 50, 18), (side * 26, 12), (side * 4, 20)]
        if side < 0:
            pg = pg[::-1]
        s.append(shape(pg, "#ffffff", "".join(line([(side * 12, -14 + j * 10), (side * 40, -18 + j * 10)], 2.4, col, taper=.1, wmin=.8, seed=sd + 5 + j + side * 3)
                                                 for j in range(3)), w=3, seed=sd + side))
    s.append(line([(0, -22), (0, 18)], 3, col, seed=sd + 9))
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{"".join(s)}</g>'


def player(x, y, sc, on, t, sd=5200):
    """Плеер (тёмный, скруглённый) с экраном: on 0..1 — экран загорается, на нём значок книги."""
    s = []
    s.append(shape(rect_pts(-58, -92, 58, 92, 18), "#2a2d36", blob(rect_pts(20, -92, 58, 92), "#1c1e26", .9) +
                   blob(rect_pts(-46, -80, -34, 40, 6), "#4a4e5a", .8), w=4, seed=sd))
    scr = lib.mix("#3a3e4a", "#e6f7f4", on)
    s.append(shape(rect_pts(-44, -78, 44, 8, 8), scr, "", w=3, seed=sd + 1))
    if on > 0.05:
        k = back_out(clamp(on), 2.2)
        s.append(f'<g opacity="{min(1, on * 2):.3f}">{book_icon(0, -36, 0.75 * k, sd + 10)}</g>')
    s.append(shape(ellipse_pts(0, 50, 28, 28, 16), "#3a3e4a", blob(ellipse_pts(0, 50, 10, 10, 10), "#2a2d36"), w=3, seed=sd + 2))
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)})">{"".join(s)}</g>'


def headphones(x, y, sc, rot=0.0, sd=5300):
    """Белые накладные наушники (лежат/в руке): центр дужки (x, y)."""
    s = []
    band_ = [(-62, 40), (-58, -10), (-30, -48), (0, -56), (30, -48), (58, -10), (62, 40)]
    s.append(line(band_, 18, INK, taper=.05, wmin=.95, seed=sd))
    s.append(line(band_, 10, "#f4f4f0", taper=.05, wmin=.95, seed=sd + 1))
    for k, side in enumerate((-1, 1)):
        cup = ellipse_pts(side * 62, 52, 26, 38, 14)
        s.append(shape(cup, "#f4f4f0", blob(ellipse_pts(side * 62 + 8, 60, 16, 28, 10), "#c9ccd4", .9) +
                       blob(ellipse_pts(side * 62 - 8, 38, 5, 12, 8), "#ffffff"), w=3.8, seed=sd + 2 + k))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{"".join(s)}</g>'


def dumb_lock(x, y, sc, rot=0.0, opened=0.0, sd=5400):
    """Замок-гантель: дужка сверху, корпус — гантель (гриф и два диска). opened — дужка поднята."""
    s = []
    lift = -34 * opened
    sh = [(-22, 0), (-24, -40 + lift), (-12, -62 + lift), (12, -62 + lift), (24, -40 + lift), (22, 0 + lift * (1 - opened) + lift * opened * .3)]
    s.append(line(sh, 16, INK, taper=.05, wmin=.95, seed=sd))
    s.append(line(sh, 9, STEEL, taper=.05, wmin=.95, seed=sd + 1))
    s.append(shape(rect_pts(-56, -10, 56, 14, 6), STEEL, blob(rect_pts(-56, 4, 56, 14), STEEL_SH), w=3.4, seed=sd + 2))
    for k, side in enumerate((-1, 1)):
        s.append(shape(rect_pts(side * 50 - 20, -40, side * 50 + 20, 44, 10), "#2fb3a8", blob(rect_pts(side * 50 + 4, -40, side * 50 + 20, 44), "#1f8a80", .9) +
                       blob(rect_pts(side * 50 - 14, -32, side * 50 - 8, 20, 3), "#8fe0d6", .9), w=3.8, seed=sd + 3 + k))
    s.append(shape(ellipse_pts(0, 2, 8, 8, 10), "#2a2d36", "", w=2, seed=sd + 6))
    return f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(sc)})">{"".join(s)}</g>'


def calendar(x, y, n_done, t, pop_t, sd=5500, sc=1.0):
    """Календарь-месяц на стене: красная шапка, сетка 7×5 (без чисел); n_done — сколько клеток отмечено галочкой;
    pop_t[i] — время галочки i (для вылета)."""
    s = []
    w, h = 420, 400
    x0, y0 = x - w / 2, y - h / 2
    s.append(blob(rect_pts(x0 + 10, y0 + 14, x0 + w + 10, y0 + h + 14, 10), "#c9cec0", .7))
    inner = blob(rect_pts(x0, y0, x0 + w, y0 + 70), "#e2543f")
    for r in range(5):
        for c in range(7):
            cx, cy = x0 + 22 + c * 54 + 24, y0 + 92 + r * 58 + 24
            inner += f'<rect x="{f(cx - 22)}" y="{f(cy - 22)}" width="44" height="44" rx="6" fill="#eef0f4"/>'
    s.append(shape(rect_pts(x0, y0, x0 + w, y0 + h, 10), "#ffffff", inner, w=4.4, seed=sd))
    for k in range(4):
        rx = x0 + 70 + k * 94
        s.append(shape(rect_pts(rx - 7, y0 - 20, rx + 7, y0 + 16, 7), STEEL, "", w=2.6, seed=sd + 2 + k))
    for i in range(n_done):
        r, c = divmod(i, 7)
        cx, cy = x0 + 22 + c * 54 + 24, y0 + 92 + r * 58 + 24
        e = t - pop_t[i]
        k = back_out(clamp(e / 0.14), 2.6)
        s.append(P.check(cx, cy + 4, 0.34 * (0.6 + 0.4 * k), prog=clamp(e / 0.1), sd=sd + 20 + i))
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(sc)}) translate({f(-x)} {f(-y)})">{"".join(s)}</g>'


# ═══════════════════════════════ s10: шкафчик у входа
LK = (620, FLOOR)           # низ среднего шкафчика (центр)
LW, LH = 170, 640
DOOR_X = 190                 # дверной проём (центр), порог
SHELF_Y = LK[1] - 400


def locker_bank(t):
    """Три шкафчика: левый и правый закрыты, средний — корпус (внутренность рисуется отдельно)."""
    s = []
    s.append(blob(ellipse_pts(LK[0], FLOOR + 6, 380, 14, 14), "#7b8a78", .5, blur(4)))
    for k, dx in enumerate((-LW, 0, LW)):
        cx = LK[0] + dx
        x0, x1 = cx - LW / 2, cx + LW / 2
        body = rect_pts(x0, LK[1] - LH, x1, LK[1] - 16)
        if dx == 0:
            inner = blob(rect_pts(x0 + 12, LK[1] - LH + 12, x1 - 12, LK[1] - 28), "#3a4660")
            inner += blob(rect_pts(x0 + 12, LK[1] - LH + 12, x0 + 60, LK[1] - 28), "#2c364c", .9)
            inner += blob(rect_pts(x0 + 12, SHELF_Y, x1 - 12, SHELF_Y + 14), "#9aa6b8")
            inner += line([(x0 + 12, SHELF_Y), (x1 - 12, SHELF_Y)], 3, INK, seed=5610)
            inner += blob(rect_pts(x0 + 12, LK[1] - LH + 140, x1 - 12, LK[1] - LH + 152), "#9aa6b8")
            s.append(shape(body, "#6fa8c8", inner, w=4.6, seed=5600 + k))
        else:
            s.append(locker_door_closed(x0, x1, 5620 + k * 10))
    s.append(shape(rect_pts(LK[0] - 1.5 * LW - 10, LK[1] - 20, LK[0] + 1.5 * LW + 10, LK[1], 4), "#4a5468", "", w=3.4, seed=5650))
    return "".join(s)


def locker_door_closed(x0, x1, sd):
    inner = blob(rect_pts(x0 + (x1 - x0) * .62, LK[1] - LH, x1, LK[1] - 16), "#5c93b3", .85)
    for j in range(4):
        yy = LK[1] - LH + 40 + j * 16
        inner += line([(x0 + 40, yy), (x1 - 40, yy)], 4, "#4a7890", taper=.1, wmin=.9, seed=sd + j)
    inner += shape(rect_pts(x1 - 40, LK[1] - LH / 2 - 40, x1 - 26, LK[1] - LH / 2 + 40, 6), STEEL, "", w=2.6, seed=sd + 5)
    return shape(rect_pts(x0, LK[1] - LH, x1, LK[1] - 16), "#6fa8c8", inner, w=4.6, seed=sd + 6)


def locker_door(open_k, sd=5700):
    """Дверца среднего шкафчика на петлях слева: open_k 1 — распахнута (узкая полоса влево), 0 — закрыта.
    Возвращает (svg, точка петли замка-ушка на дверце)."""
    x0, x1 = LK[0] - LW / 2, LK[0] + LW / 2
    y0, y1 = LK[1] - LH, LK[1] - 16
    c = math.cos(math.pi * 0.9 * open_k)        # проекция ширины
    wx = LW * c
    persp = 26 * math.sin(math.pi * 0.9 * open_k)
    if abs(wx) < 16:          # дверца ребром — тонкая полоса, не линия на всю высоту
        wx = 16 if wx >= 0 else -16
        persp = 6
    xe = x0 + wx
    pts = [(x0, y0, 1), (xe, y0 - persp, 1), (xe, y1 + persp, 1), (x0, y1, 1)]
    face_front = wx > 0
    col = "#6fa8c8" if face_front else "#4f7f9a"
    inner = ""
    if face_front:
        for j in range(4):
            yy = y0 + 40 + j * 16
            inner += line([(x0 + 40 * c, yy - persp * .2), (xe - 40 * c, yy - persp * .8)], 4, "#4a7890", taper=.1, wmin=.9, seed=sd + j)
        inner += blob([(x0 + wx * .62, y0), (xe, y0 - persp), (xe, y1 + persp), (x0 + wx * .62, y1)], "#5c93b3", .85)
    s = shape(pts, col, inner, w=4.6, seed=sd + 6)
    hasp = (x0 + wx * 0.86, (y0 + y1) / 2 + 10)
    if face_front and wx > 60:
        s += shape(rect_pts(hasp[0] - 10 * c, hasp[1] - 40, hasp[0] + 6 * c, hasp[1] + 40, 5), STEEL, "", w=2.6, seed=sd + 7)
        s += shape(ellipse_pts(hasp[0] + 24, hasp[1] - 18, 9, 9, 10), STEEL, blob(ellipse_pts(hasp[0] + 24, hasp[1] - 18, 4, 4, 8), "#3a4660"), w=2.4, seed=sd + 8)
    return s, (hasp[0] + 24, hasp[1] - 18)


def doorway(t):
    """Дверной проём слева: коридор за ним (тёплый бежевый), порог, наличник."""
    s = []
    x0, x1, y0 = DOOR_X - 150, DOOR_X + 150, FLOOR - 620
    inner = blob(rect_pts(x0, y0, x1, FLOOR), "#e8d6b8")
    inner += blob([(x0, FLOOR - 140), (x1, FLOOR - 120), (x1, FLOOR), (x0, FLOOR)], "#cbb594")
    inner += line([(x0, FLOOR - 140), (x1, FLOOR - 120)], 3, INK, seed=5801, op=.7)
    inner += blob(rect_pts(x0 + 40, y0 + 120, x0 + 120, y0 + 300, 6), "#c9b08a", .8)
    s.append(shape(rect_pts(x0, y0, x1, FLOOR), "#e8d6b8", inner, w=4, seed=5800))
    s.append(shape([(x0 - 26, FLOOR, 1), (x0 - 26, y0 - 26, 1), (x1 + 26, y0 - 26, 1), (x1 + 26, FLOOR, 1), (x1, FLOOR, 1), (x1, y0, 1), (x0, y0, 1), (x0, FLOOR, 1)],
                   "#f7f7f2", "", w=4, seed=5802))
    s.append(shape(rect_pts(x0 - 30, FLOOR - 6, x1 + 30, FLOOR + 14, 4), "#8a7a62", "", w=3.4, seed=5803))
    return "".join(s)


def hanging_hand(t, hasp):
    """Рука справа приносит замок-гантель и вешает на ушко на «только»; уходит. -> (svg руки, позиция замка или None)."""
    t_in, t_hang, t_out = TOLKO - 0.3, TOLKO, TOLKO + 0.22
    if t < t_in or t > t_out + 0.35:
        return "", None
    u_in = ease_out(clamp((t - t_in) / (t_hang - t_in)), 3)
    u_out = ease_in(clamp((t - t_out) / 0.3), 2)
    hx = hasp[0] + 40 + (1 - u_in) * 520 + u_out * 600
    hy = hasp[1] + 20 + (1 - u_in) * 60
    shoulder = (hx + 520, hy + 260)
    elbow = ((shoulder[0] + hx) / 2 + 20, (shoulder[1] + hy) / 2 + 60)
    s = person.tube(shoulder, elbow, (hx + 36, hy + 6), 70, 62, 54, "#7a8494", 5900, inner_sh=True)
    s += person.fhand(hx + 34, hy + 4, 200, "#c98e6a", 5910, sc=1.05, curl=0.55)
    lock = (hasp[0], hasp[1] + 40) if t >= t_hang else (hx - 10, hy + 30)
    return s, lock


def s10(t):
    art = [_ST["room10"], doorway(t)]
    # дорожки за порогом справа (зал)
    art.append(locker_bank(t))
    tx0 = 890
    art.append(f'<g transform="translate({2 * tx0 + 470 * 0.56} 0) scale(-1 1)">{treadmill(tx0, FLOOR - 30, 0.56, t, 1.2, 5950)}</g>')
    # внутренность шкафчика: плеер и наушники на полке
    on = smooth(AUDIO - 0.05, AUDIO + 0.15, t)
    px, py = LK[0] + 40, SHELF_Y - 92
    grab = ZALE + 0.12
    taken = t > grab
    if not taken:
        art.append(headphones(LK[0] - 30, SHELF_Y - 70, 0.72, -8, 5960))
    art.append(player(px + 6, py + 10 - 4 * on * math.sin(t * 20) * (t < AUDIO + 0.3), 0.72, on, t))
    if t < TOLKO - 0.3 or t > ZALE + 0.2:
        art.append(sound_waves(px + 50, py - 30, t, AUDIO, 1.0, side=1))
        art.append(sound_waves(px - 50, py - 30, t, AUDIO + 0.1, 1.0, side=-1))
    # дверца: открыта → захлопывается перед «только» → на «зале» распахивается
    close = ease_in(clamp((t - (TOLKO - 0.32)) / 0.16), 2)
    reopen = ease_out(clamp((t - (ZALE + 0.06)) / 0.22), 2)
    open_k = 1 - close + reopen * close
    bounce = 0.04 * P.kick(t, TOLKO - 0.16, 8, 20)
    door, hasp = locker_door(clamp(open_k + bounce))
    art.append(door)
    # замок
    hand, lock = hanging_hand(t, hasp)
    if t < ZALE + 0.04:
        if lock is not None:
            sw = 14 * math.exp(-max(0, t - TOLKO) * 4) * math.sin(max(0, t - TOLKO) * 18)
            art.append(dumb_lock(lock[0], lock[1], 0.8, sw))
        elif t > TOLKO:
            sw = 14 * math.exp(-max(0, t - TOLKO) * 4) * math.sin(max(0, t - TOLKO) * 18)
            art.append(dumb_lock(hasp[0], hasp[1] + 40, 0.8, sw))
        art.append(P.pop_lines(hasp[0], hasp[1] + 40, t - TOLKO, 60, 110, 6, col="#2fb3a8", w=8, sd=5970))
    else:
        e = t - ZALE
        lx = hasp[0] + 160 * e
        ly = hasp[1] + 40 - 300 * e + 1400 * e * e
        if ly < FLOOR - 30:
            art.append(dumb_lock(lx, ly, 0.8, 300 * e, opened=1.0))
        art.append(P.pop_lines(hasp[0], hasp[1] + 40, e, 60, 120, 8, col="#ffd23a", w=9, sd=5980))
    # человек входит через порог и берёт наушники
    art += visitor(t, taken)
    art.append(hand)
    # камера: крупно шкафчик (наезд) → отъезд, видно порог и человека; толчок на «зале»
    pull = ease_io(clamp((t - (TOLKO + 0.05)) / 0.42))
    cx = (LK[0] + 10) + (600 - (LK[0] + 10)) * pull
    cy = (SHELF_Y + 90) + (930 - (SHELF_Y + 90)) * pull
    push = clamp((t - 15.1) / 1.6)
    sc = (2.1 + 0.12 * push) * (1 - pull) + 1.22 * pull + 0.04 * P.kick(t, ZALE, 6, 14) + 0.03 * P.kick(t, AUDIO, 7, 14)
    return "".join(art), cam(cx, cy, sc, 0.5 - 0.8 * clamp((t - 15.1) / 2.85))


def visitor(t, taken):
    """Человек в спортивном: с «только» входит из коридора через порог, подходит к шкафчику, на «зале» берёт наушники."""
    t0 = TOLKO + 0.3
    stop = ZALE - 0.06
    if t < t0:
        return []
    e = clamp((t - t0) / (stop - t0))
    ee = ease_out(e, 1.6)
    x = DOOR_X + (LK[0] - 250 - DOOR_X) * ee
    y = FLOOR - 14 + 50 * ee
    sc = 0.86 + 0.08 * ee
    walking = t < stop
    pose = {"look": (0.7, 0.1), "mouth": "smile", "brow": 0.5, "head_tilt": 2 * math.sin(t * 3), "blink": P.bump(t, 17.6, 0.14),
            "curl": {"L": .5, "R": .5}}
    if walking:
        pose["walk"] = (t - t0) * 11
    else:
        pose["legs"] = {"L": (4, 0), "R": (-4, 0)}
        reach = ease_out(clamp((t - stop) / 0.16), 2)
        lift = ease_io(clamp((t - (ZALE + 0.2)) / 0.35))
        # кисть: к полке шкафчика → поднимает наушники к себе
        tgt_w = (LK[0] - 40 + (x + 190 - (LK[0] - 40)) * lift, SHELF_Y - 70 + 90 * lift)
        tl = ((tgt_w[0] - x) / sc, (tgt_w[1] - y) / sc)
        rest = (120, -330)
        pose["hand_target"] = {"R": (rest[0] + (tl[0] - rest[0]) * reach, rest[1] + (tl[1] - rest[1]) * reach)}
        pose["curl"]["R"] = 0.7
        if taken:
            pose["over_hand"] = {"R": lambda h, a: headphones(h[0] + 10, h[1] + 20, 0.6 / 1.0, -10 + 8 * math.sin(t * 6), 5990)}
    shadow = blob(ellipse_pts(x, y + 6, 110, 16, 12), "#7b8a78", .45, blur(4))
    return [shadow + person.draw(MAN_A_NOPH, pose, x, y, sc, sd=6000)]


MAN_A_NOPH = dict(MAN_A, phones=False)


# ═══════════════════════════════ s11, s12: зал
TM1 = (40, 1010, 0.62)        # дальняя дорожка слева (x задний край, y пол, масштаб)
TM2 = (640, 1010, 0.62)       # дальняя дорожка справа
BK = (470, 1330, 0.82)        # велотренажёр (центр каретки, пол, масштаб)
CAL_P = (540, 420)


def check_times():
    """Времена галочек: 35 клеток. Первые 3 отмечены заранее (до «ходить»), с «ходить» — быстро, последняя на «чаще»."""
    n = 35
    pre = [17.2, 17.4, 17.6]
    rest = n - len(pre)
    out = list(pre)
    for i in range(rest):
        u = i / (rest - 1)
        out.append(HODIT + (CHASCHE - HODIT) * (1 - (1 - u) ** 1.3))
    return out


CHECKS = check_times()


def crank_angle(t, shot):
    """Угол шатунов: в s11 — ровно ~1 об/с, в s12 — разгоняется до ~2 об/с (интеграл скорости)."""
    def w(tt):
        base = 2 * math.pi * 1.0
        return base * (1 + 0.6 * smooth(19.95, UZNAT, tt) + 0.5 * smooth(UZNAT, DALSHE, tt))
    t0 = 17.0
    n = max(2, int((t - t0) * 60))
    ts = np.linspace(t0, t, n)
    return float(np.trapezoid([w(x) for x in ts], ts))


def gym_scene(t, shot):
    art = [_ST["room11"]]
    art.append(window(-260, 300, 120, 700, 6100))
    art.append(window(960, 300, 1340, 700, 6110))
    n_done = sum(1 for x in CHECKS if t >= x)
    sc_cal = 1 + 0.08 * P.kick(t, CHASCHE, 6, 16)
    art.append(calendar(*CAL_P, n_done, t, CHECKS, sc=sc_cal))
    if t >= CHASCHE:
        art.append(P.pop_lines(CAL_P[0] + 160, CAL_P[1] + 150, t - CHASCHE, 60, 130, 8, col="#3cbf63", w=10, sd=6150))
    # дальние дорожки с бегунами
    for i, ((x, y, sc), spec) in enumerate(((TM1, MAN_B), (TM2, MAN_C))):
        ph = t * 9.5 + i * 1.3
        art.append(treadmill(x, y, sc, t, 1.3, 6200 + i * 50, back=True, front=False))
        bx = x + 230 * sc
        spec2 = dict(spec, phones=True)
        art.append(runner(spec2, bx, y - 84 * sc, sc * 0.95, t, ph, 6300 + i * 100, blink=P.bump(t, 18.9 + i * .4, 0.14)))
        art.append(treadmill(x, y, sc, t, 1.3, 6200 + i * 50, back=False, front=True))
    # велотренажёр с женщиной
    x, y, sc = BK
    crank = crank_angle(t, shot)
    lean = 8.0 + 9.0 * smooth(UZNAT - 0.1, UZNAT + 0.2, t)
    look = (0.7, 0.0)
    eye_k = 1.0
    mouth = "smile"
    if shot == "s12":
        eye_k = 1.0 + 0.3 * smooth(19.95, 20.3, t)
        mouth = "o" if t > UZNAT - 0.05 else "smile"
        look = (0.8, -0.1 if t < DALSHE else -0.6)
    art.append(bike(x, y, sc, t, crank, 6400, "back"))
    art.append(bike(x, y, sc, t, crank, 6400, "seat"))
    art.append(rider(WOMAN, x, y, sc, t, crank, {"lean": lean, "look": look, "eye_k": eye_k, "mouth": mouth,
                                                 "blink": P.bump(t, 18.3, 0.14) + P.bump(t, 21.75, 0.12), "tilt": 2 * math.sin(t * 2.5)}))
    art.append(bike(x, y, sc, t, crank, 6400, "front"))
    # облачко с книгой и «!» на «дальше»
    if shot == "s12" and t > DALSHE - 0.04:
        e = t - (DALSHE - 0.04)
        k = back_out(clamp(e / 0.28), 2.4) * (1 + 0.03 * math.sin(e * 6))
        art.append(thought(x + 120, y - 860, k, t))
    # «скорость» у педалей в s12
    if shot == "s12" and t > UZNAT:
        for j in range(3):
            ph = (t * 3 + j / 3) % 1
            a = -0.5 + j * 0.5
            r0 = 120 + 40 * ph
            art.append(line([(x - 10 + r0 * math.cos(math.pi + a), y - 120 * sc + r0 * math.sin(math.pi + a) * .6),
                             (x - 10 + (r0 + 50) * math.cos(math.pi + a), y - 120 * sc + (r0 + 50) * math.sin(math.pi + a) * .6)], 6, "#9aa6b8",
                            taper=.5, seed=6500 + j, op=1 - ph))
    return "".join(art)


def thought(x, y, k, t):
    """Облачко-мысль: круглое облако с хвостиком из кружков, внутри раскрытая книга и восклицательный знак (фигурами)."""
    if k < 0.02:
        return ""
    s = []
    for j, (dx, dy, r) in enumerate(((-150, 170, 14), (-120, 130, 22))):
        s.append(shape(ellipse_pts(x + dx, y + dy, r, r, 12), "#ffffff", "", w=3.6, seed=6600 + j))
    s.append(shape(P.cloud_pts(x, y, 190, 110, 8, 6610), "#ffffff", blob(ellipse_pts(x + 30, y + 40, 150, 40, 14), "#eef1f6", .9), w=4.6, seed=6611))
    s.append(book_icon(x - 50, y + 6, 1.55, 6620, col="#d9467a"))
    # «!» — толстая палка и точка
    bx = x + 100
    s.append(shape([(bx - 16, y - 70, 1), (bx + 18, y - 70, 1), (bx + 8, y + 22, 1), (bx - 6, y + 22, 1)], "#ffd23a", "", w=4, seed=6630))
    s.append(shape(ellipse_pts(bx + 1, y + 52, 15, 15, 12), "#ffd23a", "", w=4, seed=6631))
    tx, ty = x - 150, y + 170
    return f'<g transform="translate({f(tx)} {f(ty)}) scale({f(k)}) translate({f(-tx)} {f(-ty)})">{"".join(s)}</g>'


def s11(t):
    art = gym_scene(t, "s11")
    u = clamp((t - 17.55) / 2.55)
    sc = 1.12 + 0.05 * ease_io(u) + 0.035 * P.kick(t, CHASCHE, 6, 14) + 0.015 * P.kick(t, HODIT, 7, 14)
    return art, cam(540, 860 + 10 * u, sc, -0.5 + 0.8 * u)


def s12(t):
    art = gym_scene(t, "s12")
    x, y, sc = BK
    u = clamp((t - 19.7) / 2.4)
    s = 1.5 + 0.14 * ease_io(u) + 0.04 * P.kick(t, DALSHE, 6, 14) + 0.025 * P.kick(t, UZNAT, 6, 14)
    return art, cam(x + 30 + 20 * u, 930 - 30 * u, s, 0.6 - 0.9 * u)


def build_static():
    if _ST:
        return
    _ST["room10"] = room(True)
    _ST["room11"] = room()
    lib.static_done()


def frame(sid, t):
    build_static()
    lib.dyn_begin()
    if sid == "s10":
        art, cm = s10(t)
    elif sid == "s11":
        art, cm = s11(t)
    else:
        lib.INK_K[0] = 0.8
        art, cm = s12(t)
        lib.INK_K[0] = 1.0
    return svg(f'<rect width="{W}" height="{H}" fill="{WALL}"/><g transform="{cm}">{art}</g>')
