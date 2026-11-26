"""Рилс 129 «Детектив: кто украл моё время?», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json (общая дорожка voice_merge.py).
Нуарный кабинет: жалюзи с полосами света, стол с зелёной лампой, доска улик с красными нитками, стена опознания с ростовыми
линиями. Кот-детектив: коричневый плащ, чёрная шляпа, чёрные очки, лупа — костюм внутри рисунка кота (costume.py).
Подозреваемые — предметы с лицами: Телефон, «Ещё одна серия» (экран с кнопкой «следующая»), «Почта» (конверт); главный вор —
серый секундомер в маске «На секундочку». NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402
import h4 as H4  # noqa: E402
import room as RM  # noqa: E402
import costume as CO  # noqa: E402

HIT = stress(1, .4)
NWALL, NWALL_SH, NFLOOR = "#b49674", "#9c7f5f", "#6f5138"
LINE_WALL = "#a9b7c2"


def dcat(x, y, k, t, st=None, paw=None, loupe_on=True, loupe_rot=-20.0, glint=0.0):
    """Кот-детектив: тот же кот рилсов + костюм (плащ, шляпа, очки, лупа)."""
    st = dict(dict(look=(-.4, -.2), tail=8 * math.sin(t * 1.7), flame_e=1.0), **(st or {}))
    return CT.draw(x, y, k, CO.dress(st, paw, loupe_on, loupe_rot, glint), t)


H4.cat = dcat       # призыв cta_code тоже рисует кота в костюме


# ═════════════ кабинет ═════════════
def blinds_light(x0, y0, op=.22):
    o = ""
    for j in range(6):
        y = y0 + 70 * j
        o += f'<path d="M{x0} {y} L{x0 + 520} {y + 160} L{x0 + 520} {y + 196} L{x0} {y + 36} Z" fill="#fff4d6" opacity="{op:.3f}"/>'
    return o


def blinds(x, y, w=300, h=380):
    o = shape(lib.rect_pts(x - w / 2 - 14, y - h - 14, x + w / 2 + 14, y + 14), "#5a4030", "", w=4, seed=12950)
    o += rect(x - w / 2, y - h, x + w / 2, y, "#f7e7b8")
    for j in range(12):
        yy = y - h + 8 + j * (h - 16) / 12
        o += shape(lib.rect_pts(x - w / 2, yy, x + w / 2, yy + 18), "#e2cfa0", "", w=2, seed=12951 + j)
    return o


def noir_room(t, lamp=1.0, light=True):
    o = [plain_room(t, wall=NWALL, floor=NFLOOR)]
    o.append(blinds(250, 980))
    if light:
        o.append(blinds_light(420, 700))
    return o


def desk_noir(x, y, lamp=1.0, papers=True):
    """Стол детектива (верх столешницы в y): лампа с зелёным абажуром, папка «ДЕЛО»."""
    o = [shape(lib.rect_pts(x - 340, y, x + 340, y + 40), "#5b3a22", "", w=4.6, seed=12960)]
    o.append(shape(lib.rect_pts(x - 320, y + 40, x + 320, y + 300), "#6e4a2c", blob(lib.rect_pts(x + 120, y + 40, x + 320, y + 300), "#5b3a22", .7)
                   + line([(x - 300, y + 150), (x + 300, y + 150)], 3, "#4a2e18", seed=12962), w=4.6, seed=12961))
    if papers:
        o.append(tf(shape(lib.rect_pts(-120, -14, 120, 0), "#e9c98a", plain("ДЕЛО", -30, -18, 34, fill="#5b3a22"), w=3, seed=12963), x - 150, y, 1.0, -3))
    lx, ly = x + 220, y
    o.append(shape(lib.rrect(lx - 50, ly - 16, lx + 50, ly, 6), "#c9a24a", "", w=3, seed=12964))
    o.append(line([(lx, ly - 16), (lx, ly - 150)], 8, "#c9a24a", taper=0, wmin=1, seed=12965))
    o.append(shape([(lx - 100, ly - 140, 1), (lx - 80, ly - 190), (lx + 80, ly - 190), (lx + 100, ly - 140, 1)], "#2f7a4a",
                   blob([(lx - 60, ly - 186), (lx - 30, ly - 186), (lx - 50, ly - 146), (lx - 86, ly - 146)], "#4ea36a", .7), w=4, seed=12966))
    if lamp > 0:
        o.append(f'<path d="M{lx - 96} {ly - 140} L{lx + 96} {ly - 140} L{lx + 260} {ly + 4} L{lx - 300} {ly + 4} Z" fill="#fff1b0" opacity="{.28 * lamp:.3f}"/>')
    return "".join(o)


DESK = (560.0, 1240.0)


def office(t, cat_st=None, paw=None, cat_k=1.0, dima=None, lamp=1.0, loupe_rot=-20.0, glint=0.0, dx=0.0):
    o = noir_room(t)
    o.append(board(860 + dx, 820, .55, t))
    if dima:
        o.append(dima)
    # кот сидит на стуле за столом: виден над столешницей
    o.append(dcat(DESK[0] - 40 + dx, DESK[1] - 6, cat_k, t, cat_st, paw=paw, loupe_rot=loupe_rot, glint=glint))
    o.append(desk_noir(DESK[0] + dx, DESK[1], lamp))
    return o


# ═════════════ лица предметов ═════════════
def face(cx, cy, s=1.0, mood="calm", look=(0.0, 0.0), talk=0.0, sweat=0.0, t=0.0, sd=0):
    """Мультяшное лицо предмета: глаза-овалы со зрачками, брови, рот. mood: calm, smug, worry, shock, sly, grin."""
    o = []
    for sx in (-1, 1):
        ex, ey = cx + sx * 34 * s, cy
        o.append(shape(ellipse_pts(ex, ey, 20 * s, 26 * s, 14), "#ffffff", "", w=3.2, seed=sd + 1 + sx))
        r = 9 * s if mood != "shock" else 6 * s
        o.append(f'<circle cx="{ex + look[0] * 8 * s:.1f}" cy="{ey + 4 * s + look[1] * 8 * s:.1f}" r="{r:.1f}" fill="#111"/>')
        o.append(f'<circle cx="{ex + look[0] * 8 * s - 3 * s:.1f}" cy="{ey + look[1] * 8 * s:.1f}" r="{2.6 * s:.1f}" fill="#fff"/>')
        if mood in ("smug", "sly"):
            o.append(f'<path d="M{ex - 22 * s:.1f} {ey - 26 * s:.1f} L{ex + 22 * s:.1f} {ey - 26 * s:.1f} L{ex + 22 * s:.1f} {ey - 4 * s:.1f} '
                     f'L{ex - 22 * s:.1f} {ey - 8 * s:.1f} Z" fill="#555" opacity=".85"/>')
        by = ey - 34 * s
        tilt = {"worry": 10, "shock": -4, "smug": -6, "sly": -10, "grin": 0, "calm": 0}.get(mood, 0) * sx
        o.append(line([(ex - 18 * s, by + tilt * s * .5), (ex + 18 * s, by - tilt * s * .5)], 5 * s, seed=sd + 5 + sx))
    my = cy + 50 * s
    if mood in ("shock",) or talk > .05:
        op = max(talk, .7 if mood == "shock" else 0)
        o.append(shape(ellipse_pts(cx, my, 18 * s, (6 + 18 * op) * s, 14), "#5a2b33", "", w=3, seed=sd + 9))
    elif mood in ("smug", "grin", "sly"):
        o.append(line([(cx - 30 * s, my - 4 * s), (cx, my + 10 * s), (cx + 34 * s, my - 10 * s)], 5 * s, seed=sd + 10))
    elif mood == "worry":
        o.append(line([(cx - 26 * s, my + 6 * s), (cx - 8 * s, my - 4 * s), (cx + 8 * s, my + 4 * s), (cx + 26 * s, my - 4 * s)], 4.4 * s, seed=sd + 11))
    else:
        o.append(line([(cx - 24 * s, my), (cx, my + 8 * s), (cx + 24 * s, my)], 4.6 * s, seed=sd + 12))
    if sweat > .02:
        for j, (dx, dy) in enumerate(((70, -30), (-76, -10))):
            yy = cy + dy * s + 30 * s * ((t * 1.3 + j * .5) % 1)
            o.append(shape([(cx + dx * s, yy - 22 * s, 1), (cx + dx * s + 11 * s, yy), (cx + dx * s, yy + 12 * s), (cx + dx * s - 11 * s, yy)],
                           "#9fd3f5", "", w=2.4, seed=sd + 20 + j))
    return "".join(o)


def limbs(x, y, s, arm=(0.0, 0.0), legs=True, walk=None, sd=0, top=-120.0, half=90.0):
    """Ручки и ножки предмета: (x, y) — низ предмета посередине; arm — (подъём левой, правой) 0…1."""
    o = []
    if legs:
        for sx in (-1, 1):
            ph = 0.0 if walk is None else 30 * math.sin(walk * 2 * math.pi + (0 if sx < 0 else math.pi))
            fx = x + sx * 40 * s + ph * s
            o.append(line([(x + sx * 40 * s, y - 4), (fx, y + 90 * s)], 8 * s, taper=0, wmin=1, seed=sd + 30 + sx))
            o.append(shape(ellipse_pts(fx + sx * 14 * s, y + 96 * s, 28 * s, 13 * s, 12), "#2a2c30", "", w=3, seed=sd + 32 + sx))
    for j, sx in enumerate((-1, 1)):
        up = arm[j]
        sx0, sy0 = x + sx * half * s, y + top * s
        ex, ey = sx0 + sx * (70 - 20 * up) * s, sy0 + (80 - 190 * up) * s
        o.append(line([(sx0, sy0), (sx0 + sx * 50 * s, sy0 + (40 - 80 * up) * s), (ex, ey)], 8 * s, taper=0, wmin=1, seed=sd + 40 + j))
        o.append(shape(ellipse_pts(ex, ey, 17 * s, 17 * s, 12), "#ffffff", "", w=3, seed=sd + 44 + j))
    return "".join(o)


def phone_char(x, y, s, t, mood="calm", look=(0, 0), talk=0.0, sweat=0.0, arm=(0.0, 0.0), notif=0.0, walk=None, legs=True):
    """Телефон с лицом на экране; (x, y) — низ корпуса. notif — уведомления на экране (сыплются сверху)."""
    o = [limbs(x, y, s, arm, legs, walk, sd=13000, top=-140, half=118)]
    o.append(shape(lib.rrect(x - 130 * s, y - 470 * s, x + 130 * s, y, 40 * s), "#2a2d36", "", w=5, seed=13001))
    o.append(shape(lib.rrect(x - 108 * s, y - 440 * s, x + 108 * s, y - 34 * s, 22 * s), "#9fc8ee",
                   blob(lib.rect_pts(x - 108 * s, y - 440 * s, x + 108 * s, y - 380 * s), "#c4e0f8", .8), w=3, seed=13002))
    o.append(shape(ellipse_pts(x, y - 456 * s, 22 * s, 5 * s, 10), "#111", "", w=2, seed=13003))
    for j in range(3):
        u = clamp(notif * 3 - j)
        if u > .01:
            yy = y - 420 * s + 60 * j * s
            c = lib.clip_rect(x - 108 * s, y - 440 * s, 216 * s, 406 * s, 22 * s)
            o.append(f'<g clip-path="url(#{c})" opacity="{u:.3f}">' + shape(lib.rrect(x - 96 * s, yy - 60 * s + 60 * s * u, x + 96 * s, yy + 0 * s + 60 * s * u, 12 * s),
                                                                          "#ffffff", blob(ellipse_pts(x - 70 * s, yy - 30 * s + 60 * s * u, 14 * s, 14 * s, 10), RED), w=2.4,
                                                                          seed=13004 + j) + "</g>")
    o.append(face(x, y - 230 * s, s * 1.15, mood, look, talk, sweat, t, sd=13010))
    if notif > .05:
        bx, by = x + 120 * s, y - 470 * s
        o.append(shape(ellipse_pts(bx, by, 34 * s, 34 * s, 16), RED, text("!", 0, 0, 1, fill="#fff", stroke="#fff", sw=0.01)[:0], w=3, seed=13020))
        o.append(text("1", bx, by + 16 * s, 46 * s, fill="#ffffff", stroke="#7a1a10", sw=4))
    return "".join(o)


def series_char(x, y, s, t, mood="calm", look=(0, 0), talk=0.0, sweat=0.0, arm=(0.0, 0.0), press=0.0, walk=None):
    """«Ещё одна серия»: экран на ножке с лицом, под экраном кнопка «следующая ▶»; (x, y) — низ подставки."""
    o = [limbs(x, y, s, arm, True, walk, sd=13100, top=-330, half=210)]
    o.append(shape(lib.rect_pts(x - 22 * s, y - 120 * s, x + 22 * s, y - 10 * s), "#3a3d46", "", w=4, seed=13101))
    o.append(shape(ellipse_pts(x, y - 8 * s, 90 * s, 16 * s, 16), "#3a3d46", "", w=4, seed=13102))
    o.append(shape(lib.rrect(x - 230 * s, y - 470 * s, x + 230 * s, y - 110 * s, 22 * s), "#2a2d36", "", w=5, seed=13103))
    o.append(shape(lib.rrect(x - 206 * s, y - 448 * s, x + 206 * s, y - 196 * s, 12 * s), "#5a6b9a",
                   blob(lib.rect_pts(x - 206 * s, y - 448 * s, x + 206 * s, y - 400 * s), "#7a8bba", .8), w=3, seed=13104))
    o.append(face(x, y - 350 * s, s * 1.05, mood, look, talk, sweat, t, sd=13110))
    pr = clamp(press)
    bw = 300 * s
    by0 = y - 182 * s + 6 * s * pr
    o.append(shape(lib.rrect(x - bw / 2, by0, x + bw / 2, by0 + 56 * s, 26 * s), "#e2453a" if pr < .5 else "#ff6a4a", "", w=3.4, seed=13105))
    o.append(plain("следующая ▶", x, by0 + 40 * s, 36 * s, fill="#ffffff", anchor="middle"))
    return "".join(o)


def mail_char(x, y, s, t, mood="calm", look=(0, 0), talk=0.0, sweat=0.0, arm=(0.0, 0.0), walk=None, rot=0.0):
    """«Почта»: конверт с лицом на ножках; (x, y) — низ конверта."""
    o = [limbs(x, y, s, arm, True, walk, sd=13200, top=-120, half=200)]
    w, h = 400 * s, 270 * s
    env = shape(lib.rect_pts(x - w / 2, y - h, x + w / 2, y), "#fbf3df", "", w=5, seed=13201)
    env += line([(x - w / 2, y - h), (x, y - h * .45), (x + w / 2, y - h)], 4.4, seed=13202)
    env += line([(x - w / 2, y), (x - w * .1, y - h * .4)], 3, seed=13203, op=.6)
    env += line([(x + w / 2, y), (x + w * .1, y - h * .4)], 3, seed=13204, op=.6)
    env += shape(ellipse_pts(x, y - h * .45, 26 * s, 26 * s, 14), RED, "", w=3, seed=13205)
    o.append(f'<g transform="rotate({rot:.2f} {x:.1f} {y:.1f})">{env}</g>')
    o.append(face(x, y - h * .62, s * .9, mood, look, talk, sweat, t, sd=13210))
    return "".join(o)


def sec_thief(x, y, s, t, look=(0, 0), mood="sly", arm=(0.0, 0.0), legs=True):
    """Главный вор «На секундочку»: серый секундомер в чёрной маске; (x, y) — низ корпуса."""
    o = [limbs(x, y, s, arm, legs, None, sd=13300, top=-150, half=150)]
    cy = y - 170 * s
    o.append(shape(lib.rect_pts(x - 22 * s, cy - 210 * s, x + 22 * s, cy - 160 * s), "#8a8f98", "", w=3.4, seed=13301))
    o.append(shape(ellipse_pts(x, cy - 214 * s, 40 * s, 14 * s, 12), "#8a8f98", "", w=3.4, seed=13302))
    o.append(shape(ellipse_pts(x, cy, 170 * s, 170 * s, 30), "#a7adb6", blob(ellipse_pts(x + 60 * s, cy + 50 * s, 110 * s, 100 * s, 20), "#8a8f98", .6),
                   w=5, seed=13303))
    o.append(shape(ellipse_pts(x, cy, 140 * s, 140 * s, 30), "#eef1f4", "", w=3.6, seed=13304))
    o.append(line([(x, cy), (x + 60 * s * math.sin(t * 9), cy - 60 * s * math.cos(t * 9))], 5 * s, RED, taper=0, wmin=1, seed=13305))
    o.append(f'<path d="M{x - 150 * s:.1f} {cy - 66 * s:.1f} Q{x:.1f} {cy - 96 * s:.1f} {x + 150 * s:.1f} {cy - 66 * s:.1f} L{x + 150 * s:.1f} {cy - 6 * s:.1f} '
             f'Q{x:.1f} {cy - 30 * s:.1f} {x - 150 * s:.1f} {cy - 6 * s:.1f} Z" fill="#14161c"/>')
    o.append(line([(x + 150 * s, cy - 40 * s), (x + 200 * s, cy - 60 * s + 10 * s * math.sin(t * 8))], 9 * s, "#14161c", taper=.2, wmin=.4, seed=13306))
    for sx in (-1, 1):
        ex, ey = x + sx * 56 * s, cy - 40 * s
        o.append(shape(ellipse_pts(ex, ey, 22 * s, 16 * s, 12), "#ffffff", "", w=2.6, seed=13307 + sx))
        o.append(f'<circle cx="{ex + look[0] * 8 * s:.1f}" cy="{ey + 2 * s + look[1] * 5 * s:.1f}" r="{8 * s:.1f}" fill="#111"/>')
    if mood == "sly":
        o.append(line([(x - 50 * s, cy + 56 * s), (x, cy + 74 * s), (x + 56 * s, cy + 46 * s)], 6 * s, seed=13310))
    else:
        o.append(shape(ellipse_pts(x, cy + 64 * s, 20 * s, 26 * s, 14), "#5a2b33", "", w=3, seed=13311))
    return "".join(o)


def name_plate(x, y, txt, size=54, u=1.0, rot=-2.0):
    if u <= .02:
        return ""
    w = big_title_w(txt, size) + 60
    body = shape(lib.rrect(-w / 2, -size * .9, w / 2, size * .55, 12), "#fbf3df", "", w=4, seed=13400) + plain(txt, 0, size * .25, size, fill="#1d2448", anchor="middle")
    s = lib.back_out(clamp(u), 2.0)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.2f}) scale({s:.4f})">{body}</g>'


def big_title_w(txt, size):
    import big_title
    return big_title.text_w(txt, size) * .92


def lineup_wall(t, x0=-600, x1=1700):
    """Стена опознания: серо-голубая, ростовые линии без чисел, пол."""
    o = [rect(x0, -1400, x1, RFL, LINE_WALL)]
    for j in range(18):
        y = RFL - 100 * j
        o.append(line([(x0, y), (x1, y)], 3 if j % 5 else 6, "#7d8a96", taper=0, wmin=1, seed=13500 + j, op=.8))
    o.append(rect(x0, RFL, x1, RFL + 1400, "#6d7782"))
    o.append(line([(x0, RFL), (x1, RFL)], 5, seed=13520))
    o.append(PR.glow(540, 700, 700, .25, "#ffffff"))
    return "".join(o)


def board(x, y, k, t, threads=1.0, pull=0.0, thieves=0.0, cards=3, q=True, hi=-1):
    """Доска улик: пробка, три карточки подозреваемых и «?» в центре, красные нитки. pull — нитки стягиваются к центру;
    thieves — на карточках проступает маленький воришка-секундомер. hi — номер карточки под лупой."""
    o = [PR.cork_board(0, 0, 900, 640, seed=3)]
    pos = [(-280, -150), (280, -150), (-250, 160), (250, 160)]
    ctr = (0, 10)
    kinds = ["phone", "series", "mail"]
    for j in range(min(cards, 3)):
        px, py = pos[j]
        px, py = px + (ctr[0] - px) * .25 * pull, py + (ctr[1] - py) * .25 * pull
        card = shape(lib.rect_pts(-110, -90, 110, 100), "#fbf8f1", rect(-96, -76, 96, 70, "#d9d2c2"), w=3.4, seed=13600 + j)
        if kinds[j] == "phone":
            card += phone_char(0, 60, .26, t, "smug", legs=False)
        elif kinds[j] == "series":
            card += series_char(0, 70, .3, t, "smug")
        else:
            card += mail_char(0, 46, .34, t, "worry")
        if thieves > .02:
            card += f'<g opacity="{clamp(thieves * 3 - j):.3f}">' + sec_thief(66, 66, .2, t, look=(-.6, 0), legs=False) + "</g>"
        o.append(tf(card, px, py, 1.0 + (.25 if hi == j else 0), (-4, 3, 5)[j]))
        o.append(PR.push_pin(px, py - 84, 1.0))
    if q:
        o.append(shape(lib.rect_pts(-70, -70, 70, 80), "#fbf8f1", "", w=3.4, seed=13610) + PR.question_mark(0, 6, .9, col=RED))
        o.append(PR.push_pin(0, -64, 1.0))
    if threads > .02:
        for j in range(min(cards, 3)):
            px, py = pos[j]
            px, py = px + (ctr[0] - px) * .25 * pull, py + (ctr[1] - py) * .25 * pull
            u = clamp(threads * 3 - j)
            ex, ey = px + (0 - px) * u, (py - 84) + (-64 - (py - 84)) * u
            o.append(line([(px, py - 84), ((px + ex) / 2, (py - 84 + ey) / 2 + 30 * (1 - pull)), (ex, ey)], 4, "#c81e1e", taper=0, wmin=1, seed=13620 + j))
    return tf("".join(o), x, y, k)


def empty_clock(x, y, r, hands=0.0, t=0.0, wobble=0.0):
    """Часы без стрелок (день украли); hands 0…1 — стрелки возвращаются."""
    o = [shape(ellipse_pts(0, 0, r, r, 30), "#4F78B5", "", w=5, seed=13700)]
    o.append(shape(ellipse_pts(0, 0, r * .86, r * .86, 30), "#F7F1E3", "", w=3, seed=13701))
    for j in range(12):
        a = j * math.pi / 6
        o.append(line([(math.cos(a) * r * .7, math.sin(a) * r * .7), (math.cos(a) * r * .8, math.sin(a) * r * .8)], 5, seed=13702 + j))
    if hands > .02:
        h = clamp(hands)
        o.append(f'<g opacity="{h:.3f}">' + line([(0, 0), (0, -r * .55 * h)], 10, taper=0, wmin=1, seed=13720)
                 + line([(0, 0), (r * .4 * h, r * .1)], 12, taper=0, wmin=1, seed=13721) + "</g>")
    o.append(shape(ellipse_pts(0, 0, 10, 10, 10), "#111", "", w=2, seed=13722))
    return tf("".join(o), x, y, 1.0, wobble)


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: Дима влетает в кабинет детектива с часами без стрелок в руках, кот за столом под лампой поднимает голову."""
    o = office(t, dict(look=(-.9, -.2), perk=1.0), paw=.5, loupe_rot=-30, dx=230)
    x = 170 - 80 * (1 - ease_out(clamp((t + .3) / .5)))
    f = stand(x, t, "panic82", "d82_hold", head_add=.04)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(empty_clock(x + 150, hy + 230, 105, t=t, wobble=10 * math.sin(t * 18)))
    dx, dy = shake(t, HIT, 10)
    return hook_view("".join(o), t, HIT, 460, 980, 1.12, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«целый день»: Дима крупно трясёт часы без стрелок; на стене лист календаря с вырезанной дырой."""
    a, b = T0("s02"), T1("s02")
    o = noir_room(t)
    cal = shape(lib.rect_pts(-120, -150, 120, 150), "#fbf8f1", rect(-120, -150, 120, -96, "#c8553d") +
                shape(ellipse_pts(0, 30, 70, 74, 20), NWALL_SH, "", w=4, seed=13801), w=4, seed=13800)
    o.append(tf(cal, 820, 760, 1.0, 4))
    o.append(PR.push_pin(820, 620, 1.0))
    f = stand(380, t, "panic82", "d82_hold", head_add=.05 * math.sin(t * 9))
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(empty_clock(530, hy + 230, 120, t=t, wobble=14 * math.sin(t * 20)))
    o.append(PR.question_mark(hx + 190, hy - 60, 1.0, u=pop(t, W(5), .25), col=RED))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(5), 10)
    return view("".join(o), 560 + dx, hy + 260 + dy, 1.3 + .06 * u, 0, t=t)


def frame_s03(t):
    """Кот: «Дело принял детектив Кот» — кот-детектив под лампой поднимает лупу, блик на линзе."""
    a, b = T0("s03"), T1("s03")
    up = ease_out(ramp(t, W(8), .35))
    o = office(t, dict(look=(.1, 0), smile=.6, tilt=-4 * up), paw=.45 + .55 * up, loupe_rot=-35 - 10 * up, glint=bump(t, W(9), .05, .4))
    o.append(PR.sparkles(DESK[0] + 60, DESK[1] - 520, 1.2, bump(t, W(9), .05, .5), t, seed=31, n=5, r=120))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), DESK[0], 1080, 1.55 + .07 * u, 0, t=t)


def frame_s04(t):
    """«Первый подозреваемый»: доска улик, кот с лупой у доски, красные нитки тянутся к «?»."""
    a, b = T0("s04"), T1("s04")
    o = noir_room(t)
    o.append(board(560, 880, 1.0, t, threads=ramp(t, a, .9)))
    o.append(dcat(880, RFL - 4, .95, t, dict(look=(-.8, -.6), turn=-.3), paw=.9, loupe_rot=-35))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1080, 1.0 + .05 * u, 0, t=t)


PLATE_Y = {"phone": 790, "series": 860, "mail": 1050}


def lineup(t, who, cx=440, mood="smug", plate_txt="", plate_u=1.0, **kw):
    o = [lineup_wall(t)]
    if who == "phone":
        o.append(phone_char(cx, RFL - 100, 1.3, t, mood, **kw))
    elif who == "series":
        o.append(series_char(cx, RFL - 100, 1.15, t, mood, **kw))
    elif who == "mail":
        o.append(mail_char(cx, RFL - 100, 1.2, t, mood, **kw))
    if plate_txt:      # табличка над головой подозреваемого: внизу кадра её закрыли бы субтитры
        o.append(name_plate(cx, PLATE_Y[who], plate_txt, 60, plate_u))
    return o


def frame_s05(t):
    """«Телефон»: Телефон с лицом шагает к стене опознания, табличка «ТЕЛЕФОН»; кот-детектив сбоку щурится через лупу."""
    a, b = T0("s05"), T1("s05")
    j = ease_out(ramp(t, a - .2, .4))
    o = lineup(t, "phone", cx=380 + 120 * (1 - j), mood="smug", plate_txt="ТЕЛЕФОН", plate_u=ramp(t, W(12), .25), walk=t * 2 if j < 1 else None,
               look=(.6, 0))
    o.append(dcat(850, RFL + 40, 1.0, t, dict(look=(-.9, -.3), turn=-.4), paw=.9, loupe_rot=-40))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(12), 8)
    return view("".join(o), 600 + dx, 1180 + dy, 1.25 + .05 * u, 0, t=t)


def frame_s06(t):
    """«Алиби: я просто показал уведомление»: Телефон разводит ручками, на экране всплывает уведомление, пузырь с алиби."""
    a, b = T0("s06"), T1("s06")
    talk = abs(math.sin(t * 12)) if t < WE(17) else 0
    o = lineup(t, "phone", cx=420, mood="calm", plate_txt="ТЕЛЕФОН", look=(.4, -.3), talk=.5 * talk, arm=(.8, .8), notif=ramp(t, W(16), .6) * .34)
    o.append(PR.speech_bubble(720, 540, 600, 300, pop(t, W(13) + .1, .25), seed=6, tail=(-180, 110)))
    if pop(t, W(13) + .1, .25) > .8:
        for j, ln in enumerate(("я просто показал", "уведомление")):
            o.append(plain(ln, 720, 530 + 64 * j, 54, fill="#1d2448", anchor="middle"))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1180, 1.25 + .05 * u, 0, t=t)


def frame_s07(t):
    """«показал уведомление»: лупа кота наезжает на экран Телефона, уведомления сыплются, Телефон потеет."""
    a, b = T0("s07"), T1("s07")
    o = [lineup_wall(t)]
    o.append(phone_char(580, RFL - 100, 1.05, t, "worry", look=(.5, .2), sweat=1.0, arm=(.2, .2), notif=clamp((t - a) / .9)))
    o.append(name_plate(560, 920, "ТЕЛЕФОН", 60))
    o.append(dcat(900, RFL + 60, 1.15, t, dict(look=(-.9, -.4), turn=-.5, tilt=-4), paw=1.0, loupe_rot=-45, glint=bump(t, W(17), .05, .4)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 680, 1250, 1.3 + .12 * u, 0, t=t)

def frame_s08(t):
    """«Второй: Ещё одна серия»: экран с лицом и кнопкой «следующая» встаёт к стене, табличка «ЕЩЁ ОДНА СЕРИЯ»."""
    a, b = T0("s08"), T1("s08")
    j = ease_out(ramp(t, a - .2, .4))
    o = lineup(t, "series", cx=480 + 140 * (1 - j), mood="smug", plate_txt="ЕЩЁ ОДНА СЕРИЯ", plate_u=ramp(t, W(19), .25),
               walk=t * 2 if j < 1 else None, look=(.4, 0), press=bump(t, W(21), .05, .3))
    o.append(dcat(860, RFL + 60, .95, t, dict(look=(-.9, -.3), turn=-.4), paw=.8, loupe_rot=-35))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(19), 8)
    return view("".join(o), 600 + dx, 1180 + dy, 1.25 + .05 * u, 0, t=t)


def frame_s09(t):
    """«Говорит, что была последней»: экран клянётся — ручка вверх, пузырь «последняя!»."""
    a, b = T0("s09"), T1("s09")
    talk = abs(math.sin(t * 12)) if t < WE(25) else 0
    o = lineup(t, "series", cx=470, mood="calm", plate_txt="ЕЩЁ ОДНА СЕРИЯ", look=(.4, -.2), talk=.5 * talk, arm=(.0, 1.0))
    o.append(PR.speech_bubble(760, 640, 480, 220, pop(t, W(24), .25), seed=7, tail=(-160, 100)))
    if pop(t, W(24), .25) > .8:
        o.append(plain("последняя!", 760, 658, 62, fill="#1d2448", anchor="middle"))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(25), 6)
    return view("".join(o), 600 + dx, 1180 + dy, 1.25 + .05 * u, 0, t=t)


def frame_s10(t):
    """«Четвёртый раз»: кнопка «следующая» жмётся снова, кот-детектив лапой ставит на стене четвёртую черту."""
    a, b = T0("s10"), T1("s10")
    o = lineup(t, "series", cx=430, mood="worry", plate_txt="ЕЩЁ ОДНА СЕРИЯ", look=(.6, -.3), sweat=1.0, press=bump(t, W(26), .05, .25))
    for j in range(4):
        u = 1.0 if j < 3 else ramp(t, W(26) + .05, .2)
        if u > 0:
            x0 = 760 + 46 * j
            o.append(line([(x0, 640), (x0 + 4, 640 + 200 * u)], 12, RED, taper=0, wmin=1, seed=13900 + j))
    o.append(plain("4-й раз", 830, 920, 64, fill="#1d2448", anchor="middle", op=ramp(t, W(26) + .1, .2)))
    o.append(dcat(860, RFL + 40, .95, t, dict(look=(-.6, -.8), turn=-.3), paw=1.0, loupe_rot=-30))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(26), 10)
    return view("".join(o), 600 + dx, 1180 + dy, 1.25 + .06 * u, 0, t=t)


def frame_s11(t):
    """«Третий: Сейчас только почту проверю»: конверт с лицом встаёт к стене, табличка «ПОЧТА»."""
    a, b = T0("s11"), T1("s11")
    j = ease_out(ramp(t, a - .2, .4))
    o = lineup(t, "mail", cx=450 + 140 * (1 - j), mood="calm", plate_txt="ПОЧТА", plate_u=ramp(t, W(28) + .1, .25), walk=t * 2 if j < 1 else None,
               look=(.4, -.2), talk=.4 * abs(math.sin(t * 12)) if t > W(29) else 0)
    o.append(dcat(860, RFL + 60, .95, t, dict(look=(-.9, -.3), turn=-.4), paw=.8, loupe_rot=-35))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(28), 8)
    return view("".join(o), 600 + dx, 1180 + dy, 1.25 + .05 * u, 0, t=t)


def frame_s12(t):
    """«почту проверю»: Дима за ноутбуком «на минутку» открывает почту — конверт выпрыгивает из экрана."""
    a, b = T0("s12"), T1("s12")
    o = desk_room(t)
    o.append(PR.laptop(640, DESK_Y - 8, 1.0, screen="lines", lines=.3, t=t, seed=1))
    jmp = ease_out(ramp(t, a + .15, .5))
    o.append(mail_char(660 + 40 * jmp, DESK_Y - 140 - 240 * jmp, .45, t, "smug", look=(-.6, .3), arm=(.6, .6), walk=t * 3))
    o.append(dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.8, -.3)), lean=.15,
                       arms={"f": ("ik", (560, DESK_Y - 30), 1), "n": ("ik", (630, DESK_Y - 25), 1)})["svg"])
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 820, 1.4 + .06 * u, 0, t=t)


def frame_s13(t):
    """«Ушёл проверить и не вернулся»: конверт убегает в дверь, на его месте у стены пустой меловой контур."""
    a, b = T0("s13"), T1("s13")
    run = ease_in2(ramp(t, a + .1, 1.0))
    o = [lineup_wall(t)]
    o.append(PR.door(1120, RFL, 1.0, ajar=ease_out(ramp(t, a, .3)) * (1 - ramp(t, W(36), .25)), seed=4))
    d = ramp(t, a + .7, .5)
    if d > 0:
        w, h = 480, 324
        o.append(f'<rect x="{450 - w / 2}" y="{RFL - 100 - h}" width="{w}" height="{h}" fill="none" stroke="#ffffff" stroke-width="9" '
                 f'stroke-dasharray="34 18" stroke-linecap="round" opacity="{d:.3f}"/>')
        o.append(PR.question_mark(450, RFL - 270, 1.0, u=ramp(t, W(36), .3), col="#ffffff"))
    if run < 1:
        o.append(mail_char(450 + 760 * run, RFL - 100, 1.2 * (1 - .35 * run), t, "sly", look=(.8, 0), walk=t * 4))
        o.append(PR.speed_arcs(300 + 760 * run, RFL - 300, 1.4, run, t, seed=8, n=3, ang=0))
    o.append(name_plate(450, 1050, "ПОЧТА", 60))
    o.append(dcat(800, RFL + 60, .95, t, dict(look=(.9, -.3), turn=.4), paw=.7, loupe_rot=-25))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(37), 6)
    return view("".join(o), 600 + dx, 1180 + dy, 1.25 + .05 * u, 0, t=t)

def frame_s14(t):
    """«Но главный вор прятался в каждой улике»: кот у доски, нитки стягиваются к «?» в центре."""
    a, b = T0("s14"), T1("s14")
    o = noir_room(t)
    o.append(board(560, 880, 1.0, t, threads=1.0, pull=ease_io(ramp(t, a + .3, 1.2))))
    o.append(dcat(800, RFL - 4, 1.0, t, dict(look=(-.8, -.7), turn=-.3, tilt=-5), paw=1.0, loupe_rot=-40))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1080, 1.05 + .08 * u, 0, t=t)


def frame_s15(t):
    """«в каждой улике»: лупа идёт по карточкам — на каждой проступает маленький серый воришка-секундомер."""
    a, b = T0("s15"), T1("s15")
    o = noir_room(t)
    th = clamp((t - a) / (b - a) * 1.2)
    o.append(board(560, 880, 1.0, t, threads=1.0, pull=1.0, thieves=th, hi=min(2, int(th * 3))))
    o.append(dcat(780, RFL - 4, 1.0, t, dict(look=(-.8, -.7), turn=-.3), paw=1.0, loupe_rot=-40 + 20 * math.sin(t * 5)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 1000, 1.2 + .06 * u, 0, t=t)


def frame_s16(t):
    """«Его зовут На секундочку»: из-за доски выскакивает воришка-секундомер в маске; кот наводит лупу, табличка «НА СЕКУНДОЧКУ»."""
    a, b = T0("s16"), T1("s16")
    o = noir_room(t)
    o.append(board(560, 820, .9, t, threads=1.0, pull=1.0, thieves=1.0))
    pk = ease_out(ramp(t, a - .1, .35))
    o.append(sec_thief(300, RFL - 100 + 300 * (1 - pk), .95, t, look=(.6, -.2), mood="o" if t > W(47) else "sly", arm=(.5 * pk, .5 * pk)))
    o.append(name_plate(330, 1040, "НА СЕКУНДОЧКУ", 58, ramp(t, W(47), .25)))
    o.append(dcat(840, RFL + 20, .95, t, dict(look=(-.9, -.1), turn=-.4, perk=1.0), paw=1.0, loupe_rot=-70, glint=bump(t, W(47), .05, .4)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(47), 12)
    return view("".join(o), 560 + dx, 1140 + dy, 1.0 + .06 * u, 0, t=t)


def verdict_sheet(t, cross=0.0, two=0.0, stamp=0.0):
    o = shape(lib.rect_pts(-300, -380, 300, 380), "#fbf8f1", "", w=5, seed=14000)
    o += plain("ПРИГОВОР", 0, -280, 70, fill="#1d2448", anchor="middle")
    o += line([(-220, -250), (220, -250)], 4, seed=14001)
    o += plain("каждое", 0, -120, 60, fill="#1d2448", anchor="middle")
    o += plain("«на секундочку»", 0, -20, 64, fill="#1d2448", anchor="middle")
    if cross > .02:
        o += line([(-260, -36), (-260 + 520 * cross, -36 + 10 * cross)], 14, RED, taper=0, wmin=1, seed=14002)
    if two > .02:
        o += f'<g opacity="{clamp(two * 2):.3f}">' + plain("2 минуты", 0, 120, 92, fill="#2a7a3a", anchor="middle") + plain("дела", -40, 214, 80, fill="#2a7a3a", anchor="middle") + "</g>"
    if stamp > .02:      # отпечаток лапы (без выдуманных слов)
        s = 1.0 + .6 * (1 - ease_out(clamp(stamp)))
        pw = blob(ellipse_pts(0, 30, 70, 56, 18), RED) + "".join(blob(ellipse_pts(dx_, dy_, 22, 26, 12), RED)
                                                               for dx_, dy_ in ((-70, -40), (-26, -76), (26, -76), (70, -40)))
        o += f'<g opacity="{min(1.0, stamp * 3) * .85:.3f}" transform="translate(190 320) rotate(-14) scale({.6 * s:.3f})">{pw}</g>'
    return o


def frame_s17(t):
    """«Приговор»: кот-детектив отложил лупу на стол и правой лапой бьёт печатью по листу «ПРИГОВОР» — тряска, отпечаток лапы."""
    a, b = T0("s17"), T1("s17")
    hit = W(49) + .1
    X, Y, K, PDX = 770.0, DESK[1] + 10, 1.05, -110.0
    o = noir_room(t)
    o.append(shape(lib.rect_pts(-200, DESK[1], 1300, DESK[1] + 600), "#6e4a2c", "", w=4, seed=14010))
    o.append(tf(verdict_sheet(t), 400, 900, .85, -3))
    if t > hit:      # отпечаток лапы ровно там, где печать коснулась листа
        s_ = 1.0 + .5 * (1 - ease_out(ramp(t, hit, .12)))
        pw = blob(ellipse_pts(0, 30, 70, 56, 18), RED) + "".join(blob(ellipse_pts(dx_, dy_, 22, 26, 12), RED)
                                                               for dx_, dy_ in ((-70, -40), (-26, -76), (26, -76), (70, -40)))
        o.append(f'<g opacity=".85" transform="translate({X - 127:.0f} 1170) rotate(-14) scale({.55 * s_:.3f})">{pw}</g>')
    o.append(tf(CO.loupe(80), 960, DESK[1] - 8, .9))
    # печать в правой лапе: лапа поднята (1.0) и опускается к удару (0.83)
    dn = ease_in2(ramp(t, hit - .22, .22)) * (1 - .6 * ramp(t, hit + .2, .3))
    pw_ = 1.0 - .17 * dn
    lx, ly = 861 + PDX * 1.6 * pw_, 1306 - 150 * pw_
    tx, ty = X + (lx - 836) * K, Y + (ly - 1306) * K
    o.append(shape(lib.rrect(tx - 30, ty - 70, tx + 30, ty + 10, 18), "#6b3f20", "", w=4, seed=14011))
    o.append(dcat(X, Y, K, t, dict(look=(-.9, .4), turn=-.4, smile=.6, paw=pw_, paw_dx=PDX), loupe_on=False))
    o.append(shape(lib.rect_pts(tx - 70, ty + 10, tx + 70, ty + 50), RED, "", w=4, seed=14012))
    if t > hit:
        o.append(PR.ring_arcs(X - 127, 1170, 1.0, ramp(t, hit, .35), 0.0, seed=5, r=260))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, hit, 14)
    return view("".join(o), 570 + dx, 1000 + dy, 1.12 + .05 * u, 0, t=t)

def frame_s18(t):
    """«каждое „на секундочку“»: на листе приговора «на секундочку» перечёркивается красным."""
    a, b = T0("s18"), T1("s18")
    o = [paper_bg()]
    o.append(tf(verdict_sheet(t, cross=ease_io(ramp(t, W(51), .6)), two=ramp(t, W(53), .4), stamp=1.0), 540, 1000, 1.25, -2))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(52) + .3, 6)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .06 * u, 0, bg=PAPER, t=t)


def frame_s19(t):
    """«заменить на две минуты дела»: Дима работает за ноутбуком, таймер 2:00 идёт, кот-детектив рядом на столе кивает."""
    a, b = T0("s19"), T1("s19")
    o = desk_room(t, sun=1.0)
    o.append(PR.laptop(620, DESK_Y - 8, 1.0, screen="lines", lines=clamp((t - a) / (b - a)), t=t, seed=1))
    tap = math.sin(t * 30)
    o.append(dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.9, -.1)), lean=.18,
                       arms={"f": ("ik", (540 + 10 * tap, DESK_Y - 30), 1), "n": ("ik", (620 - 10 * tap, DESK_Y - 25), 1)})["svg"])
    o.append(dcat(880, DESK_Y - 4, .6, t, dict(look=(-.8, -.2), smile=1.0, tilt=4 * math.sin(t * 6)), paw=.4))
    o.append(tf(shape(lib.rrect(-170, -80, 170, 80, 26), "#FFD23F", text("2 минуты", 0, 24, 66, fill="#111", stroke="#111", sw=.01), w=5,
                      seed=14020), 400, 560, pop(t, W(55) - .1, .25) * (1 + .15 * bump(t, W(56), .05, .3)), -4))     # только слова фразы, без бегущего таймера
    o.append(PR.sparkles(640, 700, 1.8, bump(t, W(56), .05, .5), t, seed=191, n=6, r=240))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 600, 820, 1.35 + .06 * u, 0, t=t)


def frame_s20(t):
    return cta_code(t, T0("s20"), T1("s20"))


def frame_s21(t):
    """«чтобы вернуть своё время»: кот-детектив протягивает Диме часы — стрелки возвращаются на место, искры."""
    a, b = T0("s21"), T1("s21")
    o = noir_room(t)
    f = stand(300, t, "proud82", "d82_hold", head_add=.04)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(empty_clock(450, hy + 230, 105, hands=ease_out(ramp(t, W(62), .5)), t=t))
    o.append(dcat(800, RFL - 4, .95, t, dict(look=(-.8, -.3), smile=1.0, turn=-.3), paw=.7, loupe_rot=-30))
    o.append(PR.sparkles(450, hy + 230, 1.6, bump(t, W(64), .05, .5), t, seed=211, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 1080, 1.1 + .06 * u, 0, t=t)


def frame_s22(t):
    """«Сегодня вечером время было на месте»: вечер, Дима на диване отдыхает, часы со стрелками на стене, кот в шляпе дремлет."""
    a, b = T0("s22"), T1("s22")
    o = [plain_room(t, wall="#d9c4a6")]
    o.append(PR.window(930, 1020, 280, 380, mode="evening", t=t, seed=4, curtain=False))
    o.append(empty_clock(540, 640, 110, hands=1.0, t=t))
    sf = RM.sofa(540, RFL, 1.0)
    o.append(sf["back"])
    x, k = 400.0, .66
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    f = people.dima82(x, RFL - 314, k, "laugh82", "sit_desk", t=t, feet=feet,
                      arms={"n": ("ik", (x + 150, RFL - 330), -1), "f": ("ik", (x + 110, RFL - 340), -1)})
    o.append(f["svg"])
    o.append(sf["arm_r"])
    o.append(dcat(770, RFL - 300, .7, t, dict(look=(-.4, 0), smile=1.0, blink=1.0, sleep=.4 + .3 * ramp(t, a, b - a)), loupe_on=False))
    o.append(PR.zzz(850, RFL - 620, .8, t, ramp(t, a + .4, .4)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1080, 1.2 + .05 * u, 0, t=t)


def frame_s23(t):
    """Петля: кадр хука — кабинет, Дима с часами без стрелок, кот-детектив за столом."""
    a, b = T0("s23"), T1("s23")
    o = office(t, dict(look=(-.9, -.2), perk=1.0), paw=.5, loupe_rot=-30, dx=230)
    f = stand(170, t, "panic82", "d82_hold", head_add=.04)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(empty_clock(320, hy + 230, 105, t=t))
    return loop_view("".join(o), t, a, b, HIT, 460, 980, 1.12)

def ease_in2(u):
    return u * u


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
