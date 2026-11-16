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
N_WALL = "#2B3060"
N_WALL_LN = "#353B70"
N_FLOOR = "#1B1E40"
N_BOARD = "#3B4278"
D8X, D8Y, D8K = 760.0, 1500.0, 1.04     # дверь: центр дна, масштаб
HIP8 = (420.0, 1500.0 - 598 * .62 - 8)


def door_mirror(svg_, x):
    return f'<g transform="translate({2 * x:.2f} 0) scale(-1 1)">{svg_}</g>'


def s08(t):
    a = ws(34)          # «теперь» — толкает
    b = ws(35)          # «смотри» — распахивается
    push = ease_io(ramp(t, a, .26)) * .22
    swing = ease_out(ramp(t, b, .3), 3)
    open_u = clamp(push + swing * .78 + .02 * math.sin(t * 3) * (1 - swing))
    o = [rect(-800, -400, 2000, D8Y, N_WALL)]
    o.append(f'<path d="{"".join(f"M{x} -400V{D8Y:.0f}" for x in range(-780, 2000, 70))}" stroke="{N_WALL_LN}" stroke-width="10"/>')
    o.append(rect(-800, D8Y, 2000, 2600, N_FLOOR))
    o.append(shape(rect_pts(-800, D8Y - 40, 2000, D8Y), N_BOARD, "", w=4, seed=8001))
    # свет на полу из двери: трапеция растёт при открытии
    lw = 190 * D8K
    spill = .35 + .65 * open_u
    fl = [(D8X - lw, D8Y), (D8X + lw, D8Y), (D8X + lw + 520 * spill, D8Y + 900), (D8X - lw - 520 * spill, D8Y + 900)]
    o.append(blob(fl, "#FFD98A", .6 * ease_io(clamp(open_u * 1.6))))
    o.append(blob([(D8X - lw, D8Y), (D8X + lw, D8Y), (D8X + lw + 30, D8Y + 26), (D8X - lw - 30, D8Y + 26)], "#FFD98A", .7))
    o.append(P.glow(D8X, D8Y - 420, 520, .25 + .55 * open_u, "#FFC86A", ry=640))
    door = P.glow_door(D8X, D8Y, D8K, open_u, t, seed=3, sil=1 - open_u, light=1.0)
    o.append(door_mirror(door, D8X))
    # Дима: рука на ручке, пока дверь не ушла из-под неё; потом опускается, свет на лице
    hx, hy = P.glow_door_handle(D8X, D8Y, D8K, open_u)
    hx = 2 * D8X - hx
    rel = ramp(t, b + .12, .3)
    hip = (HIP8[0] + 30 * push / .22 + 50 * ease_io(ramp(t, b + .1, .5)), HIP8[1] + breath(t, 3))
    tgt = (lerp(hx - 18, hip[0] + 60, ease_io(rel)), lerp(hy, hip[1] + 120, ease_io(rel)))
    arms = {"n": ("ik", tgt, -1), "f": ("ang", .2 - .5 * ease_io(rel), .25 + .9 * ease_io(rel))}
    hands = {"n": {"dir": (1, .1), "curl": (.65, .68, .72, .75), "thumb": .55} if rel < .5 else {"curl": (.3, .3, .35, .4), "thumb": .3},
             "f": {"dir": (.3, -1), "spread": .25, "curl": (.1, .1, .15, .2), "thumb": .15} if rel > .3 else {"curl": (.4, .45, .5, .55), "thumb": .4}}
    e = ex("surprise", look=(.7, -.05)) if t > b else ex("carry78", look=(.7, .1))
    if t > b + .25:
        e = dict(e, brows="up", mouth="o", open=.3, lid=.75)
    st = people.stand_kw(hip[0], hip[1], .62)
    fig = people.figure("dima", hip[0], hip[1], .62, e, lean=.04 + .12 * push / .22 + .06 * rel, head_ang=.04, arms=arms, hands=hands,
                        feet=st["feet"])
    o.insert(len(o) - 0, shadow(hip[0], D8Y, 150, .3, "#0B0E22"))
    o.append(fig["svg"])
    # тёплый отсвет на Диме со стороны двери
    if open_u > .05:
        o.append(f'<g opacity="{.35 * open_u:.3f}">{P.glow(D8X - 120, D8Y - 520, 380, 1.0, "#FFE6A8", ry=600)}</g>')
    # камера: лёгкий наезд, на «смотри» — нырок в проём
    dive = ease_io(ramp(t, b + .12, T1("s08") - b + .1))
    s = lerp(1.08 + .05 * ramp(t, T0("s08") - .2, 1.0), 3.4, dive ** 1.5)
    cx = lerp(580, D8X - 10, dive ** .7)
    cy = lerp(1190, D8Y - 420, dive ** .7)
    rot = lerp(-.6, .4, ramp(t, T0("s08") - .2, 1.4))
    over = ""
    fl_u = clamp((t - (b + .5)) / .55)
    if fl_u > 0:
        over = rect(0, 0, 1080, 1920, "#FFF4D6", .75 * ease_io(fl_u))
    return frame_svg("".join(o), cx, cy, s, rot, N_WALL, over + vignette("#05060f", .5 * (1 - open_u)))


# ═══════════════════════════════ s10: дома растут из гаражей ═══════════════════════════════
GROUND10 = 1500.0
B10 = [  # x, k гаража, цвет-индекс, (этажей к «быстрорастущих», к концу)
    (-240.0, .78, 0, (4, 6)),
    (160.0, .82, 1, (6, 14)),
    (560.0, .78, 2, (5, 7)),
    (960.0, .82, 3, (6, 16)),
    (1360.0, .78, 4, (5, 13)),
]


def floors10(t, i):
    """Сколько этажей у дома i сейчас (дробная часть — верхний выскакивает)."""
    f1, f2 = B10[i][3]
    a = ws(40) + .05 * i
    m = ws(41) + .7
    c = ws(42) + .02 * i
    if t < a:
        return 0.0
    if t < m:     # рывками: этаж каждые ~0.14 с
        u = (t - a) / (m - a)
        n = f1 * u
        return int(n) + ease_out(min(1.0, (n - int(n)) * 2.2), 2)
    if t < c:
        return float(f1)
    u = clamp((t - c) / .55)
    n = f1 + (f2 - f1) * ease_out(u, 2)
    return n


def flag_us(x, y, k, t):
    o = [line([(x, y), (x, y - 360 * k)], 9 * k, "#6E737D", taper=0, wmin=1, seed=1001)]
    fx, fy = x + 5 * k, y - 350 * k
    w, h = 200 * k, 120 * k

    def pt(u, v):
        return (fx + w * u, fy + h * v + 10 * k * math.sin(t * 6 - u * 5) * u)
    inner = ""
    for i in range(7):
        v0, v1 = i * 2 / 13, (i * 2 + 1) / 13
        inner += blob([pt(0, v0), pt(.5, v0), pt(1, v0), pt(1, v1), pt(.5, v1), pt(0, v1)], "#D9483B")
    inner += blob([pt(0, 0), pt(.4, 0), pt(.4, 7 / 13), pt(0, 7 / 13)], "#3E5A9A")
    for r in range(3):
        for c in range(3):
            px, py = pt(.07 + c * .13, .09 + r * .15)
            inner += blob(ellipse_pts(px, py, 5 * k, 5 * k, 6), "#FFFFFF")
    o.append(shape([pt(0, 0) + (1,), pt(.5, 0), pt(1, 0) + (1,), pt(1, 1) + (1,), pt(.5, 1), pt(0, 1) + (1,)], "#F4F1EA", inner, w=3.4 * k,
                   seed=1002))
    return "".join(o)


def taxi(x, y, k, t, seed=0):
    o = [shape([(-170, -30, 1), (-166, -78), (-110, -88), (-70, -140), (70, -140), (112, -88), (166, -80), (172, -30, 1)], P.C_TAXI,
               blob([(-170, -54), (172, -54), (172, -30), (-170, -30)], "#C99A1E") + line([(-150, -90), (150, -90)], 3, "#C99A1E", seed=1), w=4.4,
               seed=1100 + seed)]
    o.append(shape([(-60, -130, 1), (0, -130, 1), (0, -92, 1), (-96, -92, 1)], "#9DB6D6", "", w=3, seed=1101 + seed))
    o.append(shape([(10, -130, 1), (62, -130, 1), (98, -92, 1), (10, -92, 1)], "#9DB6D6", "", w=3, seed=1102 + seed))
    o.append(shape(rrect_(-34, -162, 34, -140, 5), "#F4F1EA", "", w=3, seed=1103 + seed))   # фонарь-шашка без букв
    for wx in (-108, 110):
        o.append(shape(ellipse_pts(wx, -30, 36, 36, 18), "#22252B", blob(ellipse_pts(wx, -30, 17, 17, 12), P.C_METAL), w=4, seed=1104 + wx))
    return P._tf("".join(o), x, y, k)


def rrect_(x0, y0, x1, y1, r):
    return lib.rrect(x0, y0, x1, y1, r)


def sky10(top=-1600, bot=GROUND10):
    g = lib.lin_grad([(0, "#6FA8DC", 1), (.7, "#A9D2F0", 1), (1, "#E6F2F8", 1)], 0, top, 0, bot, units="userSpaceOnUse")
    return f'<rect x="-900" y="{top}" width="3000" height="{bot - top}" fill="url(#{g})"/>'


def cloud10(x, y, k, seed):
    return P.cloud(x, y, 260 * k, 120 * k, seed=seed, col="#FFFFFF", ink_w=3.2)


def s10(t):
    a0 = T0("s10") - .2
    o = [sky10()]
    for i in range(14):     # дальние кварталы — бледные силуэты, чтобы небо не пустовало
        bx = -900 + i * 210 + 37 * (i % 3)
        bh = 260 + 170 * ((i * 7) % 5)
        o.append(blob(rect_pts(bx, GROUND10 - 180 - bh, bx + 170, GROUND10), "#B9CEE0"))
        for r in range(int(bh / 70)):
            o.append(blob(rect_pts(bx + 30, GROUND10 - 150 - bh + r * 70, bx + 140, GROUND10 - 130 - bh + r * 70), "#C9DAEA"))
    for i, (cx_, cy_, ck) in enumerate([(120, 160, 1.0), (760, -80, .8), (420, -520, .9), (980, -760, .7)]):
        o.append(cloud10(cx_ + 22 * (t - a0), cy_, ck, 1200 + i))
    o.append(rect(-900, GROUND10, 2000, 2600, "#8E8A84"))
    o.append(rect(-900, GROUND10, 2000, GROUND10 + 60, "#C9C2B6"))
    o.append(line([(-900, GROUND10 + 60), (2000, GROUND10 + 60)], 4, INK, taper=0, wmin=1, seed=1301))
    o.append(f'<path d="{"".join(f"M{x} {GROUND10 + 160:.0f}h70" for x in range(-880, 2000, 150))}" stroke="#F2EDE2" stroke-width="10"/>')
    # дома растут из крыш гаражей: сначала дома (за гаражами), потом гаражи
    hit = ws(42)
    for i, (x, gk, ci, _) in enumerate(B10):
        fl = floors10(t, i)
        Fm = B10[i][3][1]
        sw = 0.0
        if t > hit and i in (1, 3, 4):
            u = t - hit - .3
            sw = (2.6 if i != 3 else -3.0) * math.exp(-2.2 * max(0.0, u)) * math.sin(7.5 * max(0.0, u)) if u > 0 else 0.0
        sw += .4 * math.sin(t * 3 + i)
        gy = GROUND10 - 330 * gk + 50 * gk
        if fl > 0.01:
            o.append(P.sprout_building(x, gy + 20, gk * 1.0, fl / Fm, seed=i, sway=sw, floors=Fm))
        # обломки крыши разлетаются на первом этаже
        pu = ramp(t, ws(40) + .05 * i, .45)
        if 0 < pu < 1:
            o.append(P.dust_puff(x, gy + 10, gk * 1.2, pu, seed=40 + i))
    for i, (x, gk, ci, _) in enumerate(B10):
        o.append(P.garage(x, GROUND10, gk, seed=i, open_u=.15 * (i % 2)))
    o.append(flag_us(140, GROUND10, 1.0, t))
    o.append(taxi(760 - 30 * (t - a0), GROUND10 + 120, .9, t))
    o.append(shadow(760 - 30 * (t - a0), GROUND10 + 122, 170, .25))
    # камера: с улицы вверх вслед росту, отъезд
    up = ease_io(ramp(t, ws(40), ws(42) + .7 - ws(40)))
    s0, s1 = 1.32, .6
    s = lerp(s0, s1, up)
    cx = lerp(560, 580, up) + 10 * math.sin(t * 1.3)
    top_y = GROUND10 - 1250
    gy_scr = lerp(1240, 1290, up)
    cy = GROUND10 - (gy_scr - 960) / s
    cy += 6 * math.sin(t * 9) * bump(t, ws(42), .05, .1, .4)
    _ = top_y
    rot = lerp(.8, -.6, ramp(t, a0, T1("s10") - a0))
    # хвост хлёста с s09 (влёт слева)
    cx -= whip_in(t, T0("s10"), 0, .25)
    return frame_svg("".join(o), cx, cy, s, rot, "#A9D2F0")


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
    """Юный позёр у машины: худи, гладкое лицо, руки вверх (на «чаще» уже стоит так с s12)."""
    x, y = POSER13
    sc = .6
    ph = math.sin(t * 5)
    arms = {"n": ("ik", (x + 170 * sc + 10 * ph, y - 760 * sc), 1), "f": ("ik", (x - 120 * sc - 10 * ph, y - 760 * sc), 1)}
    hands = {"n": {"dir": (.3, -1), "spread": .4, "curl": (0, 0, .05, .1), "thumb": .1}, "f": {"dir": (-.3, -1), "spread": .4, "curl": (0, 0, .05, .1),
                                                                                              "thumb": .1}}
    e = {"brows": "up", "mouth": "grin", "open": .5, "lid": .9, "look": (0, 0), "bags": False}
    st = people.stand_kw(x, y, sc, who="youth")
    return people.figure("youth", x, y + 3 * ph, sc, e, lean=-.05, head_ang=-.08, arms=arms, hands=hands, feet=st["feet"])["svg"]


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
    pts = [(380 + sx, 260), (760 + sx, 230), (820 + sx, 760), (440 + sx, 800)]
    return blob(pts, col, .28 + .3 * day)


def bench_scene(t, phase, planks, mast_u, sail_u, hand=None, cat_st=None, cat_paw=None):
    o = [room_day(t, -400, 1600)]
    o.append(P.window(980, 900, 520, 680, mode="day" if phase < .5 else "night", t=t, seed=5, curtain=False))
    o.append(wall_light(t, phase))
    o.append(P.workbench(760, BENCH_Y, 1000, 1.0, seed=3))
    # дощечки-заготовки в стопке на верстаке
    left = max(0, 3 - int(planks - 3.0)) if planks >= 3 else 3
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
    n = 3.0
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
            o.append(P.dust_puff(hull[0] + 40, hull[1] + 40, .5, bu, seed=i))
    over = rect(0, 0, 1080, 1920, "#1B2350", .35 * ph)
    pk = sum(bump(t, h, .05, .02, .25) for h in hits)
    s = 1.14 + .015 * ramp(t, a0, 1.5) + .03 * pk
    cx = 600 + 8 * math.sin(t * 1.1)
    cy = 950 + 6 * pk
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
    cat_x, cat_y, cat_k = BOAT[0] + 330, BENCH_Y - 4, .62
    st = {"look": (-.7, -.3), "tilt": -6 + 4 * pu, "paw_l": pu, "paw_l_dx": 120, "smile": .6, "blink": 0.0}
    o.append(shadow(cat_x, BENCH_Y + 2, 120, .2))
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
    s = lerp(1.45, 1.9, z) + .02 * bump(t, m1, .05, .02, .3)
    cx = lerp(600, BOAT[0] + 60, z)
    cy = lerp(880, BOAT[1] - 330, z)
    return frame_svg("".join(o), cx, cy, s, lerp(.5, -.4, ramp(t, a0, 1.5)), D_WALL)


SCENES = {"s08": s08, "s10": s10, "s13": s13, "s14": s14, "s15": s15, "s16": s16}
_STATIC = [False]


def frame(sid, t):
    if not _STATIC[0]:
        lib.static_done()
        _STATIC[0] = True
    lib.dyn_begin()
    return SCENES[sid](t)
