"""Рилс 81 «Всё, поздно», группа A: s08, s10, s13, s14, s15, s16.
Время — ТОЛЬКО из shots.json (t0/t1 плана) и voice/words.json (слово по индексу wN); числа в коде — длительности движений.
s08 ночь, стена с дверью: Дима держит ручку; «теперь» (w34) толкает, «смотри» (w35) дверь распахивается, свет заливает, камера ныряет.
s10 улица гаражей днём: «самых» (w40) — из крыш гаражей лезут дома, «быстрорастущих» (w41) — этажи хлопают, «компаний» (w42) — три
    самых высоких вырываются вверх и качаются; камера поднимается вслед.
s13 позёр под софитом, отъезд: вокруг в полутьме десятки людей постарше работают в мастерских; «чаще» (w56) сверху падает рамка
    телефона, «ленту» (w59) — в рамке только позёр, всё вокруг гаснет.
s14 день, комната: Дима смотрит в телефон (вспышки на лице), «сравнивает» (w64) хмыкает, «лентой» (w67) кладёт телефон экраном вниз
    на комод и идёт к верстаку у окна.
s15 верстак у окна: на «каждый» (w69), «день» (w70), «делает» (w71) Дима ставит дощечку, лодка растёт; свет на стене день-ночь-день.
s16 крупно лодка: «один» (w72)–«шаг» (w73) мачта встаёт в гнездо, «своему» (w75) парус поднимается; кот трогает парус лапой.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
COMMON = os.path.join(STORY, "common")
sys.path.insert(0, HERE)
sys.path.insert(0, COMMON)
import lib  # noqa: E402
import people  # noqa: E402
import props as P  # noqa: E402
from lib import blob, clamp, ease_io, ease_out, ellipse_pts, line, rect_pts, shape, svg  # noqa: E402

INK = lib.INK
WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}


def ws(i):
    return WORDS[i]["start"]


def we(i):
    return WORDS[i]["end"]


def T0(sid):
    return SHOTS[sid]["t0"]


def T1(sid):
    return SHOTS[sid]["t1"]


def lerp(a, b, u):
    return a + (b - a) * u


def ramp(t, a, d):
    return clamp((t - a) / d)


def bump(t, a, up, hold, down):
    if t < a:
        return 0.0
    if t < a + up:
        return ease_out((t - a) / up, 2)
    if t < a + up + hold:
        return 1.0
    return 1 - ease_io((t - a - up - hold) / down)


def frame_svg(body, cx, cy, s, rot, bg, over=""):
    return svg(f'<rect width="1080" height="1920" fill="{bg}"/><g transform="{lib.cam(cx, cy, s, rot)}">{body}</g>{over}')


def shadow(x, y, rx, op=.18, col="#2A1A10"):
    return blob(ellipse_pts(x, y, rx, rx * .12, 20), col, op)


def whip_in(t, t0, amp=420.0, dur=.3):
    u = clamp((t - t0 + .06) / dur)
    return amp * (1 - ease_out(u, 3))


def rect(x0, y0, x1, y1, col, op=1.0):
    o = f' opacity="{op:.3f}"' if op < 1 else ""
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{col}"{o}/>'


def vignette(col="#120c08", op=.35):
    g = lib.rad_grad([(0, col, 0), (.62, col, 0), (1, col, op)], 540, 760, 1050, 1250)
    return f'<rect width="1080" height="1920" fill="url(#{g})"/>'


def ex(name, **over):
    e = dict(people.EXPR["dima"].get(name, {}))
    e.update(over)
    return e


def breath(t, a=1.0):
    return a * math.sin(t * 2.6)


# ═══════════════════════════════ s08: дверь со светом распахивается ═══════════════════════════════
import room  # noqa: E402

D8X, D8Y = room.DOOR81           # та же дверь, что в s05 (петли справа, ручка слева)
SC8 = .56
FEET8 = room.FL81 + 40


def s08(t):
    if not any('id="dim8"' in d for d in lib.DEFS):
        lib.DEFS.append('<filter id="dim8"><feColorMatrix type="matrix" values=".78 0 0 0 0  0 .74 0 0 0  0 0 .8 0 .02  0 0 0 1 0"/></filter>')
    a = ws(34)          # «теперь» — толкает
    b = ws(35)          # «смотри» — распахивается
    push = ease_io(ramp(t, a, .26)) * .22
    swing = ease_out(ramp(t, b, .3), 3)
    open_u = clamp(push + swing * .78)
    nr = room.night81(t, view="door", glow=.6 + .4 * open_u)
    o = [nr["bg"], nr["rug"]]
    # Дима: рука на ручке, пока дверь не ушла из-под неё; потом опускается, свет на лице
    hx, hy = P.glow_door_handle(D8X, D8Y, 1.0, open_u)
    rel = ramp(t, b + .12, .3)
    hip = (hx - 190 + 30 * push / .22 + 40 * ease_io(ramp(t, b + .1, .5)), FEET8 - 598 * SC8 + breath(t, 2.5))
    tgt = (lerp(hx - 14, hip[0] + 50, ease_io(rel)), lerp(hy + 4, hip[1] + 110, ease_io(rel)))
    arms = {"n": ("ik", tgt, -1), "f": ("ang", .2 - .5 * ease_io(rel), .25 + .9 * ease_io(rel))}
    hands = {"n": {"dir": (1, .1), "curl": (.65, .68, .72, .75), "thumb": .55} if rel < .5 else {"curl": (.3, .3, .35, .4), "thumb": .3},
             "f": {"dir": (.3, -1), "spread": .25, "curl": (.1, .1, .15, .2), "thumb": .15} if rel > .3 else {"curl": (.4, .45, .5, .55), "thumb": .4}}
    e = ex("reach81") if t < b else ex("wonder81", look=(.75, -.1))
    fig = people.figure("dima", hip[0], hip[1], SC8, e, lean=.04 + .12 * push / .22 + .06 * rel, head_ang=.04, arms=arms, hands=hands,
                        feet=people.stand_kw(hip[0], hip[1], SC8)["feet"])
    lw = 190
    spill = .35 + .65 * open_u
    fl = [(D8X - lw, D8Y), (D8X + lw, D8Y), (D8X + lw + 520 * spill, D8Y + 700), (D8X - lw - 520 * spill, D8Y + 700)]
    o.append(nr["dark"])
    o.append(blob(fl, "#FFD98A", .55 * ease_io(clamp(open_u * 1.6))))
    o.append(blob([(D8X - lw, D8Y), (D8X + lw, D8Y), (D8X + lw + 40, D8Y + 34), (D8X - lw - 40, D8Y + 34)], "#FFD98A", .55))
    o.append(P.glow(D8X, D8Y - 420, 500, .3 + .5 * open_u, "#FFC86A", ry=620))
    o.append(P.glow_door(D8X, D8Y, 1.0, open_u, t, seed=3, sil=1 - open_u, light=1.0))
    o.append(shadow(hip[0], FEET8 + 4, 130, .35, "#05060f"))
    o.append(f'<g filter="url(#dim8)">{fig["svg"]}</g>')
    if open_u > .05:     # тёплый отсвет на Диме со стороны двери
        o.append(f'<g opacity="{.4 * open_u:.3f}">{P.glow(D8X - 260, D8Y - 420, 330, 1.0, "#FFE6A8", ry=520)}</g>')
    # камера: лёгкий наезд, на «смотри» — нырок в проём
    dive = ease_io(ramp(t, b + .12, T1("s08") - b + .1))
    s = lerp(1.1 + .05 * ramp(t, T0("s08") - .2, 1.0), 3.3, dive ** 1.5)
    cx = lerp(1420, D8X, dive ** .7)
    cy = lerp(840, D8Y - 410, dive ** .7)
    rot = lerp(-.6, .4, ramp(t, T0("s08") - .2, 1.4))
    over = ""
    fl_u = clamp((t - (b + .5)) / .55)
    if fl_u > 0:
        over = rect(0, 0, 1080, 1920, "#FFF4D6", .75 * ease_io(fl_u))
    return frame_svg("".join(o), cx, cy, s, rot, room.N81["wall"], over + vignette("#05060f", .45 * (1 - open_u)))


# ═══════════════════════════════ s10: дома растут из гаражей ═══════════════════════════════
GROUND10 = room.ST81_GROUND
FL10 = [(4, 6), (6, 14), (5, 7), (6, 13), (5, 11)]     # этажей к «быстрорастущих» и к концу; три самых высоких — 1, 3, 4


def floors10(t, i):
    """Сколько этажей у дома i сейчас (дробная часть — верхний выскакивает)."""
    f1, f2 = FL10[i]
    a = ws(40) + .05 * i
    m = ws(41) + .7
    c = ws(42) + .02 * i
    if t < a:
        return 0.0
    if t < m:     # рывками: этаж за этажом
        u = (t - a) / (m - a)
        n = f1 * u
        return int(n) + ease_out(min(1.0, (n - int(n)) * 2.2), 2)
    if t < c:
        return float(f1)
    return f1 + (f2 - f1) * ease_out(clamp((t - c) / .55), 2)


def s10(t):
    a0 = T0("s10") - .2
    st = room.us_street(t)
    o = [st["bg"]]
    hit = ws(42)
    gk = room.ST81_GARAGE_K
    for i, (x, gy) in enumerate(room.ST81_GARAGES):
        fl = floors10(t, i)
        Fm = FL10[i][1]
        sw = .4 * math.sin(t * 3 + i)
        if t > hit + .3 and i in (1, 3, 4):
            u = t - hit - .3
            sw += (2.6 if i != 3 else -3.0) * math.exp(-2.2 * u) * math.sin(7.5 * u)
        if fl > 0.01:
            o.append(P.sprout_building(x, gy - 260 * gk, gk, fl / Fm, seed=i, sway=sw, floors=Fm))
    o.append(st["garages"])
    for i, (x, gy) in enumerate(room.ST81_GARAGES):     # пыль с крыши, когда дом пробивается
        pu = ramp(t, ws(40) + .05 * i, .45)
        if 0 < pu < 1:
            o.append(P.dust_puff(x, gy - 290 * gk, 1.2, pu, seed=40 + i))
    o.append(st["front"])
    # камера: с улицы вверх вслед росту, отъезд
    up = ease_io(ramp(t, ws(40), ws(42) + .7 - ws(40)))
    s = lerp(.95, .5, up)
    cx = lerp(1150, 1380, up) + 10 * math.sin(t * 1.3)
    gy_scr = lerp(1150, 1285, up)
    cy = GROUND10 - (gy_scr - 960) / s
    cy += 6 * math.sin(t * 9) * bump(t, ws(42), .05, .1, .4)
    rot = lerp(.8, -.6, ramp(t, a0, T1("s10") - a0))
    cx -= whip_in(t, T0("s10"), -380, .25)
    return frame_svg("".join(o), cx, cy, s, rot, room.ST81["sky1"])


def rrect_(x0, y0, x1, y1, r):
    return lib.rrect(x0, y0, x1, y1, r)


# ═══════════════════════════════ s13: позёр в рамке телефона ═══════════════════════════════
DARK13 = "#151726"
POSER13 = (520.0, 1350.0)        # таз позёра (стоит)
FR13 = (540.0, 1000.0, 1.5)      # рамка телефона: центр экрана и масштаб
_OLDW = ("psych", "father", "teacher_o", "inventor", "bald", "granny", "beard", "mama")
_OLDP = ("write", "fold", "draw", "tick")
OLD13 = []
for _r, _y in enumerate((250, 700, 1150, 1600)):
    for _c, _x in enumerate((-170, 1250)):
        _i = _r * 2 + _c
        OLD13.append((_x, _y, _OLDW[(_i * 3) % 8], .34, _OLDP[_i % 4], 20 + _i))
for _c, _x in enumerate((-170, 260, 540, 820, 1250)):
    OLD13.append((_x, -200, _OLDW[(_c * 5 + 1) % 8], .3, _OLDP[(_c + 1) % 4], 40 + _c))


def workshop(x, y, who, sc, pose, sd, t):
    """Ячейка-мастерская: полка-стена, лампа, человек постарше за верстаком (по пояс)."""
    o = [shape(rect_pts(x - 150, y - 330, x + 150, y + 90), "#262A3F", blob(rect_pts(x - 150, y + 40, x + 150, y + 90), "#1D2033"), w=3.4, seed=sd)]
    o.append(P.glow(x + 70, y - 70, 150, .6, "#FFD98A"))
    hip = (x - 40, y + 120 * sc / .3)
    ph = math.sin(t * (2.2 + sd * .13) + sd)
    try:
        fig = people.person(who, hip[0], hip[1], sc, "", pose, lean_add=.03 * ph, head_add=.04 * ph)
        o.append(fig["svg"])
    except Exception:
        pass
    o.append(shape(rect_pts(x - 140, y, x + 140, y + 24), P.C_WOOD, "", w=3.2, seed=sd + 1))
    o.append(P.table_lamp(x + 90, y, .45, 1.0, seed=sd, table=False))
    o.append(P.paper(x + 10 + 6 * ph, y - 4, .5, -6, seed=sd, sy=.4))
    return "".join(o)


def poser13(t):
    """Юный позёр рилса (people.youngster81, как в s11–s12): обе руки вверх у машины."""
    x, y = POSER13
    return people.youngster81(x, y + 2 * math.sin(t * 5), .6, "hooray", t)["svg"]


def flashes(t, cx, cy, R, n=6, seed=0):
    o = []
    for i in range(n):
        ph = (t * 2.3 + i * .37 + seed * .11) % 1.0
        if ph < .16:
            u = 1 - ph / .16
            ang = i * 2.4 + seed
            px, py = cx + R * math.cos(ang) * (.7 + .3 * math.sin(i)), cy + R * .6 * math.sin(ang * 1.3)
            o.append(P.glow(px, py, 70, .8 * u, "#FFFFFF"))
            o.append(P.star4(px, py, 26 * u + 6, u))
    return "".join(o)


def s13(t):
    a0 = T0("s13") - .2
    c = ws(56)           # «чаще» — рамка падает
    L = ws(59)           # «ленту» — только позёр
    o = [rect(-1200, -1000, 2400, 3000, DARK13)]
    for (x, y, who, sc, pose, sd) in OLD13:
        o.append(workshop(x, y, who, sc, pose, sd, t))
    # сцена позёра: пол, машина, софит
    o.append(P.beam(520, 330, 90, 1400, 20, 1.0, color="#FFF2C4"))
    o.append(blob(ellipse_pts(520, 1712, 360, 60, 30), "#FFF2C4", .4))
    o.append(P.sports_car(760, 1716, .52, seed=1, t=t))
    o.append(poser13(t))
    o.append(shape(rrect_(450, 260, 590, 340, 20), "#55595F", line([(470, 330), (570, 330)], 6, "#FFF6D8", seed=3), w=4, seed=1301))
    o.append(flashes(t, 540, 1150, 330, 7, 1))
    # рамка телефона
    drop = ramp(t, c, .55)
    fx, fy, fk = FR13
    body = "".join(o)
    if drop > 0:
        x0, y0, x1, y1 = P.phone_frame_rect(fx, fy, fk, drop)
        dim = .25 * ease_io(drop) + .45 * ease_io(ramp(t, L, .35))
        hole = lib.fill_d(lib.rrect(x0, y0, x1, y1, 30 * fk))
        body += f'<path d="M-1500 -1500H2600V3200H-1500Z {hole}" fill="#05060c" fill-rule="evenodd" opacity="{dim:.3f}"/>'
        body += P.phone_frame(fx, fy, fk, drop, glow_=ramp(t, L, .3))
    # камера: отъезд от позёра на всю сцену, после «ленту» — лёгкий наезд к рамке
    pull = ease_out(ramp(t, a0, c - a0 + .05), 2)
    s = lerp(1.45, .62, pull) + .03 * ease_io(ramp(t, L, .5))
    cx = lerp(560, 540, pull)
    cy = lerp(1230, FR13[1] + 266, pull)
    sh = bump(t, c + .5, .04, .05, .3)
    cy += 10 * sh * math.sin(t * 60)
    rot = lerp(.8, 0, pull)
    return frame_svg(body, cx, cy, s, rot, DARK13, vignette("#000000", .45))


# ═══════════════════════════════ s14: день, телефон экраном вниз ═══════════════════════════════
D_WALL = "#F1E1C2"
D_WALL_LN = "#E6D2AC"
D_FLOOR = "#C99A6B"
D_FLOOR_SH = "#AD7F52"
SC14 = .66
FLOOR14 = 1560.0


def room_day(t, x0=-600, x1=2400, light=1.0, wall=D_WALL):
    o = [rect(x0, -800, x1, FLOOR14, wall)]
    o.append(f'<path d="{"".join(f"M{x} -800V{FLOOR14:.0f}" for x in range(x0, x1, 90))}" stroke="{D_WALL_LN}" stroke-width="8"/>')
    o.append(rect(x0, FLOOR14, x1, 2800, D_FLOOR))
    o.append(f'<path d="{"".join(f"M{x0} {y}H{x1}" for y in range(int(FLOOR14) + 70, 2800, 90))}" stroke="{D_FLOOR_SH}" stroke-width="5"/>')
    o.append(shape(rect_pts(x0, FLOOR14 - 34, x1, FLOOR14), "#FBF3DC", "", w=4, seed=1401))
    return "".join(o)


def dresser(x, y, w=300, h=330, seed=0):
    """Комод: (x, y) — центр верхней крышки."""
    o = [shape(rect_pts(x - w / 2, y, x + w / 2, y + h), "#B98B5C", blob(rect_pts(x + w / 2 - 30, y, x + w / 2, y + h), "#9A6F45"), w=4, seed=seed)]
    for i in range(2):
        yy = y + 40 + i * (h - 50) / 2
        o.append(shape(rect_pts(x - w / 2 + 18, yy, x + w / 2 - 18, yy + (h - 80) / 2), "#C99A6B", "", w=3.4, seed=seed + 1 + i))
        o.append(shape(ellipse_pts(x, yy + (h - 80) / 4, 14, 9, 10), P.C_BRASS, "", w=2.6, seed=seed + 4 + i))
    o.append(shape(rect_pts(x - w / 2 - 14, y - 14, x + w / 2 + 14, y + 6), "#A87A4C", "", w=4, seed=seed + 7))
    return "".join(o)


def s14(t):
    a0 = T0("s14") - .2
    w64 = ws(64)        # «сравнивает» — хмыкает
    w67 = ws(67)        # «лентой» — телефон лёг
    reach = ease_io(ramp(t, w67 - .55, .55))
    walk = ramp(t, w67 + .08, T1("s14") + .2 - w67)
    hip = [420.0 + 300 * walk, FLOOR14 - 598 * SC14 * 1.0 - 14]
    drx, dry = 420 + 345 * SC14 + 30, FLOOR14 - 598 * SC14 - 14 - 205 * SC14 + 26
    o = [room_day(t)]
    o.append(P.window(1320, 1060, 520, 640, mode="day", t=t, seed=4, curtain=True))
    o.append(blob([(1060, 1080), (1580, 1080), (1700, FLOOR14 + 400), (900, FLOOR14 + 400)], "#FFF4D0", .35))
    o.append(P.workbench(1330, 1200, 700, 1.0, seed=2))
    o.append(P.model_boat(1300, 1190, .55, 3, 0, 0, t, seed=1))
    o.append(dresser(drx, dry, 320, FLOOR14 - dry))
    o.append(shadow(hip[0], FLOOR14, 170, .22))
    if t < w67 - .55:
        # смотрит в телефон, вспышки ленты на лице
        e = ex("lit78", bags=False) if t < w64 else ex("smug", look=(.5, .45), bags=False)
        sh = .25 * bump(t, w64, .1, .2, .25)
        fig = people.dima_phone(hip[0], hip[1] + breath(t, 2), SC14, e, "phone_chest74", t=t, thumb=.6 * (1 - ramp(t, w64 - .3, .2)), shrug=sh,
                                head_add=-.08 * sh, **people.stand_kw(hip[0], hip[1], SC14))
        px, py = fig["phone"]
        hd = fig["head"]
        fl = 0.5 + .5 * math.sin(t * 17) * math.sin(t * 5.3)
        o.append(fig["svg"])
        o.append(P.glow(hd[0] + 40, hd[1] + 10, 160, .25 + .3 * fl * (1 - ramp(t, w64, .3)), "#BFE1FF"))
        o.append(P.glow(px + 18, py, 70, .5 + .4 * fl, "#DDEFFF"))
        for j in range(3):        # вспышки ленты над телефоном
            q = (t * 2.6 + j * .33) % 1.0
            if q < .22 and t < w64 + .2:
                u = 1 - q / .22
                o.append(P.star4(px + (-50 + 50 * j) * SC14, py - (90 + 40 * (j % 2)) * SC14 - 30 * (1 - u), 22 * u + 6, u))
    else:
        # кладёт телефон экраном вниз на комод и уходит к верстаку
        if walk <= 0:
            pk = people.mix_pose("phone_chest74", "place74", reach, hip[0], hip[1], SC14)
            fig = people.figure("dima", hip[0], hip[1], SC14, ex("smug", look=(.6, .5), bags=False), lean=pk["lean"], head_ang=pk["head_ang"],
                                arms=pk["arms"], hands=pk["hands"], feet=people.stand_kw(hip[0], hip[1], SC14)["feet"])
            wn = fig["wrist"]["n"]
            body = fig["svg"]
            if t < w67:
                ph = P.phone_flat(wn[0] + 50, wn[1] - 6 - 22 * (1 - reach), .32, 0, 90 * reach - 10, face_down=True)
                body = body + ph
            else:
                body = body
            o.append(body)
        else:
            w = people.walk_kw(hip[0], hip[1], SC14, walk * 1.3)
            arms = {"n": ("ang", -.2 + .3 * math.sin(walk * 8), .2), "f": ("ang", .25 - .3 * math.sin(walk * 8), .2)}
            fig = people.figure("dima", w["hip"][0], w["hip"][1], SC14, ex("calm_smile", look=(.6, .1), bags=False), lean=.06, arms=arms,
                                feet=w["feet"])
            o.append(fig["svg"])
        if t >= w67:
            k = settle_u(t, w67)
            o.append(P.phone_flat(drx + 40, dry - 8 - 6 * k, .32, 0, 80, face_down=True))
            o.append(P.click(drx + 40, dry - 30, .8, 1 - ramp(t, w67, .25)) if t < w67 + .25 else "")
    # камера: светлый день, дрейф за Димой
    s = 1.12 + .03 * ramp(t, a0, 1.6) + .05 * bump(t, w64, .12, .3, .4)
    cx = 600 + 260 * ease_io(walk) + 6 * math.sin(t * 1.2)
    cy = 1070
    rot = lerp(-.5, .3, ramp(t, a0, T1("s14") - a0))
    return frame_svg("".join(o), cx, cy, s, rot, D_WALL)


def settle_u(t, t0):
    u = t - t0
    return math.exp(-8 * u) * math.cos(30 * u) if u > 0 else 1.0


# ═══════════════════════════════ s15 / s16: верстак, лодка ═══════════════════════════════
BENCH_Y = 1170.0          # крышка верстака
BOAT = (700.0, 1160.0)    # дно подставки лодки
BOAT_K = .78
HIP15 = (300.0, 1250.0)
SC15 = .7


def wall_light(t, phase):
    """Свет окна на стене: phase 0 — день (тёплый), 1 — ночь (синий, слабый)."""
    day = 1 - phase
    col = lib.mix("#FFE6A8", "#7D8FD0", phase)
    sx = 120 * phase
    pts = [(330 + sx, 300, 1), (660 + sx, 270, 1), (700 + sx, 740, 1), (370 + sx, 780, 1)]
    o = blob(pts, col, .22 + .26 * day)
    mx = 515 + sx       # тень крестовины окна в пятне
    o += blob([(mx - 8, 285, 1), (mx + 8, 285, 1), (mx + 12, 760, 1), (mx - 4, 760, 1)], "#000000", .05 * day)
    return o


def bench_scene(t, phase, planks, mast_u, sail_u, hand=None, cat_st=None, cat_paw=None):
    o = [room_day(t, -400, 1600)]
    o.append(P.window(980, 900, 520, 680, mode="day" if phase < .5 else "night", t=t, seed=5, curtain=False))
    o.append(wall_light(t, phase))
    o.append(P.workbench(760, BENCH_Y, 1000, 1.0, seed=3))
    # дощечки-заготовки в стопке на верстаке
    left = max(0, 7 - int(planks))
    for i in range(left):
        o.append(shape(rect_pts(420 - 6 * i, BENCH_Y - 18 - 16 * i, 560 - 6 * i, BENCH_Y - 4 - 16 * i), P.C_BOAT_HI if i % 2 else P.C_BOAT, "", w=3,
                       seed=1500 + i))
    o.append(P.model_boat(BOAT[0], BOAT[1], BOAT_K, planks, mast_u, sail_u, t, seed=2))
    return o


def plank_in_hand(x, y, rot, k=1.0):
    return P._tf(shape(rect_pts(-80, -9, 80, 9), P.C_BOAT_HI, line([(-70, -2), (60, -1)], 2.4, P.C_BOAT_SH, seed=3), w=3, seed=1599), x, y, k, rot)


def s15(t):
    a0 = T0("s15") - .2
    hits = [ws(69), ws(70), ws(71)]
    n = 4.0
    for h in hits:
        n += ease_out(ramp(t, h - .02, .16), 3)
    # день-ночь-день: ночь между дощечками
    ph = .5 - .5 * math.cos(2 * math.pi * clamp((t - hits[0]) / (hits[2] - hits[0]))) if t > hits[0] else 0.0
    o = bench_scene(t, ph, n, 0, 0)
    # рука ставит дощечку: от стопки к корпусу к каждому слову
    cyc = 0.0
    nxt = None
    for i, h in enumerate(hits):
        if t < h:
            nxt = h
            break
    if nxt is None:
        nxt = hits[-1] + .5
    prev = max([a0] + [h for h in hits if h <= t])
    u = clamp((t - prev) / max(.1, nxt - prev))
    cyc = u
    pile = (480.0, BENCH_Y - 50)
    hull = (BOAT[0] - 40, BOAT[1] - 150 * BOAT_K - 10)
    go = ease_io(clamp((cyc - .15) / .7))
    hx = lerp(pile[0], hull[0], go)
    hy = lerp(pile[1], hull[1], go) - 70 * math.sin(math.pi * go)
    if t >= hits[-1] + .05:
        hx, hy = lerp(hull[0], hull[0] - 120, ease_io(ramp(t, hits[-1] + .05, .4))), hull[1] + 20
    arms = {"n": ("ik", (hx, hy), -1), "f": ("ik", (BOAT[0] - 170, BOAT[1] - 110), -1)}
    hands = {"n": {"dir": (1, .2), "curl": (.6, .62, .66, .7), "thumb": .55}, "f": {"dir": (1, .4), "curl": (.3, .3, .35, .4), "thumb": .3}}
    hip = (HIP15[0] + 4 * math.sin(t * 2), HIP15[1])
    fig = people.figure("dima", hip[0], hip[1], SC15, ex("focus", look=(.7, .55), bags=False, mouth="smile", smile=.35), lean=.16, head_ang=.12,
                        arms=arms, hands=hands, feet=people.stand_kw(hip[0], hip[1], SC15)["feet"])
    o.append(fig["svg"])
    if t < hits[-1] + .05 and .1 < cyc < .95:
        wn = fig["wrist"]["n"]
        o.append(plank_in_hand(wn[0] + 40, wn[1] - 10, -8, .8))
    # тук: опилки на каждом слове
    for i, h in enumerate(hits):
        bu = ramp(t, h, .35)
        if 0 < bu < 1:
            o.append(P.click(hull[0] + 30, hull[1] - 30, 1.0, bu, seed=i))
    over = rect(0, 0, 1080, 1920, "#1B2350", .35 * ph)
    pk = sum(bump(t, h, .05, .02, .25) for h in hits)
    s = 1.42 + .02 * ramp(t, a0, 1.5) + .035 * pk
    cx = 560 + 8 * math.sin(t * 1.1)
    cy = 1010 + 6 * pk
    return frame_svg("".join(o), cx, cy, s, -.3 + .3 * ramp(t, a0, 1.5), D_WALL, over)


def s16(t):
    a0 = T0("s16") - .2
    m0 = ws(72)            # «один» — мачта в руке
    m1 = ws(73)            # «шаг» — мачта встала
    sl = ws(75)            # «своему» — парус
    mast = ease_io(ramp(t, m0 - .05, m1 + .2 - m0))
    sail = ramp(t, sl - .02, .45)
    o = bench_scene(t, 0.0, 7.0, mast, sail)
    # кот на верстаке справа: сидит, на «своему» — лапой к парусу
    pu = bump(t, sl + .2, .25, .35, .3)
    cat_x, cat_y, cat_k = BOAT[0] + 300, BENCH_Y - 118, .6
    st = {"look": (-.7, -.4), "tilt": -6 + 4 * pu, "paw_l": pu, "paw_l_dx": 122, "smile": .6, "blink": 0.0}
    o.append(shape(rect_pts(cat_x - 130, BENCH_Y - 120, cat_x + 130, BENCH_Y - 6), P.C_WOOD_HI,
                   line([(cat_x - 110, BENCH_Y - 60), (cat_x + 100, BENCH_Y - 62)], 3, P.C_WOOD_SH, seed=5), w=4, seed=1650))
    o.append(shadow(cat_x, cat_y + 2, 110, .2))
    o.append(people.cat_svg(cat_x, cat_y, cat_k, st, t))
    # рука Димы держит мачту и вдвигает
    mx, my = BOAT[0] + 10 * BOAT_K, BOAT[1] - 200 * BOAT_K
    top = my - 380 * BOAT_K * min(1.0, mast + .01)
    hgt = lerp(my - 120 - 60 * (1 - mast), my - 170 * BOAT_K, mast)
    rel = ease_io(ramp(t, m1 + .25, .4))
    tgt = (lerp(mx - 30, mx - 220, rel), lerp(hgt, BENCH_Y - 40, rel))
    if mast < .05:
        tgt = (mx - 30, my - 240 + 60 * ease_io(ramp(t, a0, m0 - a0)))
    arms = {"n": ("ik", tgt, -1), "f": ("ik", (BOAT[0] - 200, BENCH_Y - 30), -1)}
    hands = {"n": {"dir": (1, -.1), "curl": (.7, .72, .75, .78), "thumb": .6} if rel < .5 else {"curl": (.3, .3, .35, .4), "thumb": .3},
             "f": {"dir": (1, .4), "curl": (.3, .3, .35, .4), "thumb": .3}}
    hip = (HIP15[0] + 40, HIP15[1])
    e = ex("calm_smile", look=(.6, -.2), bags=False) if t > sl else ex("focus", look=(.7, .2), bags=False)
    fig = people.figure("dima", hip[0], hip[1], SC15, e, lean=.14, head_ang=.0, arms=arms, hands=hands,
                        feet=people.stand_kw(hip[0], hip[1], SC15)["feet"])
    o.append(fig["svg"])
    if mast < .05:      # мачта в руке до «один»
        wn = fig["wrist"]["n"]
        o.append(line([(wn[0] + 30, wn[1] + 90), (wn[0] + 30, wn[1] - 200)], 10, P.C_WOOD_SH, taper=.15, wmin=.7, seed=1601))
    _ = top
    # камера: наезд к парусу
    z = ease_io(ramp(t, sl - .1, .7))
    s = lerp(1.38, 1.62, z) + .02 * bump(t, m1, .05, .02, .3)
    cx = lerp(620, BOAT[0], z)
    cy = lerp(900, BOAT[1] - 260, z)
    return frame_svg("".join(o), cx, cy, s, lerp(.5, -.4, ramp(t, a0, 1.5)), D_WALL)


SCENES = {"s08": s08, "s10": s10, "s13": s13, "s14": s14, "s15": s15, "s16": s16}
_STATIC = [False]


def frame(sid, t):
    if not _STATIC[0]:
        lib.static_done()
        _STATIC[0] = True
    lib.dyn_begin()
    return SCENES[sid](t)
