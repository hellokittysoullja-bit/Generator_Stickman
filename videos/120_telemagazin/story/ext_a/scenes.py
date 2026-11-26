"""Рилс 120 «Телемагазин», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json (общий голос voice_mix.py: слова 0–39 и 52–77 — ведущий, 40–51 — Дима).
Ведущий — кот в пиджаке, с бабочкой и микрофоном, в студии телемагазина (яркие плашки, лампочки, прожекторы, вспышки).
Покупатель — Дима. Призыв — TG-карточка v5 (scripts/story_cta_tg.py). Итог — таблички «ДО» и «ПОСЛЕ». NOCAM=1 — без влёта,
тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people, REPO, COMMON  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "scripts"))
import story_cta_tg as TG  # noqa: E402

HIT = stress(2, .3)
ST_BG, ST_FL = "#2a1f4a", "#3a2a63"
SFL = 1500.0                      # пол студии
JACKET, JACKET_SH, BOW = "#2f5fd0", "#1f43a0", "#e2453a"


def lw(lx, ly, x, y, k):
    """Точка рисунка кота (локальные единицы cat.py) в мир."""
    return x + (lx - CT.CX) * k, y + (ly - CT.CBOT) * k


def host_cat(x, y, k, t, st=None, mic=True, point=0.0):
    """Кот-ведущий: пиджак, белая манишка, красная бабочка, микрофон в правой (от зрителя) лапе; point 0…1 — левая лапа
    тянется к зрителю (показывает)."""
    st = dict(dict(look=(0, .2), smile=1.0, tail=10 * math.sin(t * 3), flame_e=1.3), **(st or {}))
    if mic:
        st.setdefault("paw", .62)
    if point > 0:
        st["paw_l"] = point
        st["paw_l_dx"] = 60
    o = [cat(x, y, k, t, st)]
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1)
    P = lambda pts: [lw(a, CT.CBOT - (CT.CBOT - b) * br, x, y, k) for a, b in pts]  # noqa: E731
    left = [(812, 1146), (772, 1150), (749, 1182), (744, 1250), (800, 1252), (806, 1200)]
    right = [(2 * CT.CX - a, b) for a, b in left]
    shirt = [(812, 1146), (860, 1146), (850, 1205), (836, 1222), (822, 1205)]
    o.append(shape(P(shirt), "#fbf8f1", "", w=3 * k / 1.3, seed=5001))
    for pts, sd in ((left, 5002), (right, 5003)):
        o.append(shape(P(pts), JACKET, blob(P([(a, b) for a, b in pts[:3]] + [(760, 1250)]), JACKET_SH, .5), w=4 * k / 1.3, seed=sd))
    for s_ in (-1, 1):
        o.append(line(P([(CT.CX + s_ * 24, 1148), (CT.CX + s_ * 36, 1205)]), 3 * k / 1.3, "#0f1d4a", seed=5004 + s_))
        o.append(blob(P(ellipse_pts(CT.CX + s_ * 56, 1210, 5, 5, 8)), "#ffd35a"))
    bx, by = CT.CX, 1156
    bow = (f'<path d="M0 0 L-30 -16 L-32 16 Z M0 0 L30 -16 L32 16 Z" fill="{BOW}" stroke="#111" stroke-width="4" stroke-linejoin="round"/>'
           f'<circle r="8" fill="{BOW}" stroke="#111" stroke-width="4"/>')
    bwx, bwy = lw(bx, CT.CBOT - (CT.CBOT - by) * br, x, y, k)
    o.append(tf(bow, bwx, bwy, k * 1.0, 4 * math.sin(t * 4)))
    if mic:
        p = st["paw"]
        tip = lw(906 + 70 * p * 1.6, 1306 - 150 * p, x, y, k)
        ball = lw(906 + 70 * p * 1.6 - 34, 1306 - 150 * p - 86, x, y, k)
        o.append(line([tip, ball], 13 * k, "#2a2d36", taper=0, wmin=1, seed=5010))
        o.append(shape(ellipse_pts(ball[0], ball[1], 19 * k, 19 * k, 14), "#9aa0aa",
                       "".join(line([(ball[0] - 20 * k, ball[1] + d * k), (ball[0] + 20 * k, ball[1] + d * k)], 1.6, "#5a5f6e", taper=0, wmin=1,
                                    seed=5011 + i) for i, d in enumerate((-8, 0, 8))), w=3, seed=5015))
        o.append(shape(ellipse_pts(tip[0], tip[1], 13 * k, 11 * k, 10), CT.CAT, "", w=3, seed=5016))
    return "".join(o)


def bulbs(x0, y0, x1, y1, t, n=10, ph=0.0):
    """Лампочки по краю плашки, бегут огоньки."""
    o = []
    pts = [(x0 + (x1 - x0) * i / n, y0) for i in range(n)] + [(x1, y0 + (y1 - y0) * i / 4) for i in range(4)] \
        + [(x1 - (x1 - x0) * i / n, y1) for i in range(n)] + [(x0, y1 - (y1 - y0) * i / 4) for i in range(4)]
    for i, (a, b) in enumerate(pts):
        on = (i + int(t * 8 + ph)) % 3 == 0
        o.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="9" fill="{"#fff6b0" if on else "#c9a640"}" stroke="#111" stroke-width="2.5"/>')
    return "".join(o)


def burst(x, y, r, col, t, rot=0.0, n=12, inner=""):
    pts = []
    for i in range(2 * n):
        a = math.pi * i / n + math.radians(rot + 10 * t)
        rr = r if i % 2 == 0 else r * .72
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a), 1))
    return shape(pts, col, inner, w=4, seed=5100 + int(r))


def studio(t, flash=0.0, beams=1.0):
    """Студия телемагазина: тёмно-фиолетовый фон, цветные плашки с лампочками, звёзды-кляксы, прожекторы, сцена."""
    o = [rect(-1400, -1400, 2600, SFL, ST_BG)]
    for i in range(-6, 12):
        o.append(rect(i * 160, -1400, i * 160 + 70, SFL, "#33275a", .6))
    for j, (cx, cy, w, h, col, rot) in enumerate(((60, 520, 360, 200, "#ffd23f", -6), (1020, 470, 360, 220, "#3fb2e0", 5),
                                                  (-60, 980, 280, 180, "#ff5a8a", 4), (1130, 1000, 300, 170, "#7bd65a", -5))):
        g = shape(lib.rrect(-w / 2, -h / 2, w / 2, h / 2, 26), col, "", w=5, seed=5200 + j)
        g += bulbs(-w / 2 + 16, -h / 2 + 16, w / 2 - 16, h / 2 - 16, t, n=7, ph=j)
        g += PR.star4(0, 0, 34 + 6 * math.sin(t * 5 + j))
        o.append(tf(g, cx, cy, 1.0, rot))
    o.append(burst(560, 300, 150, "#ff8a3d", t, 0, inner=PR.star4(560, 300, 40)))
    for j, (bx, col) in enumerate(((-200, "#fff1b0"), (540, "#ffd0f0"), (1280, "#c0f0ff"))):
        sw = 22 * math.sin(t * 1.6 + j * 2)
        a = math.radians(90 + sw + (j - 1) * 18)
        ex, ey = bx + 1500 * math.cos(a), -300 + 1500 * math.sin(a)
        nx, ny = -math.sin(a) * 200, math.cos(a) * 200
        o.append(f'<path d="M{bx - 30} -300 L{bx + 30} -300 L{ex + nx:.0f} {ey + ny:.0f} L{ex - nx:.0f} {ey - ny:.0f} Z" fill="{col}" '
                 f'opacity="{.16 * beams:.3f}"/>')
    o.append(rect(-1400, SFL, 2600, SFL + 1400, ST_FL))
    o.append(line([(-1400, SFL), (2600, SFL)], 6, seed=5300))
    for i in range(-8, 16):
        o.append(line([(540 + (i - 4) * 90, SFL), (540 + (i - 4) * 260, SFL + 700)], 3, "#4a3a7a", taper=0, wmin=1, seed=5301 + i))
    if flash > 0:
        o.append(f'<rect x="-1400" y="-1400" width="4000" height="4000" fill="#ffffff" opacity="{.55 * clamp(flash):.3f}"/>')
    return "".join(o)


def counter(x, y, w=520, h=300):
    """Стойка ведущего (дно по центру): полосы, звезда спереди."""
    o = shape(lib.rect_pts(x - w / 2, y - h, x + w / 2, y), "#e2453a", "".join(
        rect(x - w / 2 + 40 + 90 * i, y - h, x - w / 2 + 80 + 90 * i, y, "#ffffff", .35) for i in range(6)), w=5, seed=5400)
    o += shape(lib.rect_pts(x - w / 2 - 20, y - h - 30, x + w / 2 + 20, y - h), "#ffd23f", "", w=5, seed=5401)
    o += burst(x, y - h / 2, 80, "#ffd23f", 0, 0, n=8)
    o += text("ТВ", x, y - h / 2 + 22, 64, fill="#e2453a", stroke="#111", sw=6)
    return o


def podium(x, y, k=1.0):
    o = shape(lib.rect_pts(-260, -160, 260, 0), "#f2f4f7", blob(lib.rect_pts(140, -160, 260, 0), "#cfd4dd", .8), w=5, seed=5450)
    o += shape(lib.rect_pts(-290, -190, 290, -160), "#ffd23f", "", w=5, seed=5451)
    o += bulbs(-240, -140, 240, -20, 0.0, n=8)
    return tf(o, x, y, k)


def gift(x, y, k=1.0, lid=0.0, label="2 МИНУТЫ", col="#e2453a", sq=0.0):
    """Коробка-подарок (дно по центру) с бантом и надписью; lid 0…1 — крышка слетает вверх-вбок."""
    sx, sy = 1 + .12 * sq, 1 - .12 * sq
    o = shape(lib.rect_pts(-180, -260, 180, 0), col, rect(-30, -260, 30, 0, "#ffd23f") + text(label, 0, -100, 64 if len(label) < 9 else 52,
                                                                                               fill="#ffffff", stroke="#111", sw=8), w=5, seed=5500)
    lu = clamp(lid)
    lidg = shape(lib.rect_pts(-200, -320, 200, -250), lib.mul(col, (.85, .85, .85)), rect(-34, -320, 34, -250, "#ffd23f"), w=5, seed=5501)
    lidg += (f'<path d="M0 -320 C-90 -420 -150 -330 0 -320 C150 -330 90 -420 0 -320 Z" fill="#ffd23f" stroke="#111" stroke-width="5"/>')
    o += f'<g transform="translate({220 * lu:.1f} {-380 * lu + 300 * lu * lu:.1f}) rotate({60 * lu:.1f} 0 -290)">{lidg}</g>'
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k * sx:.4f} {k * sy:.4f})">{o}</g>'


def confetti(t, t0, n=22, cx=540, y0=400, spread=1000):
    if t < t0:
        return ""
    u = t - t0
    o = []
    cols = ["#e2453a", "#ffd23f", "#3fb26a", "#2f8fe0", "#ff5a8a"]
    for i in range(n):
        x = cx + spread * ((i * 0.618) % 1 - .5) + 40 * math.sin(u * 3 + i)
        y = y0 - 300 + 700 * u + 200 * ((i * .37) % 1) - 400 * ((i * .21) % 1)
        o.append(f'<rect x="-10" y="-6" width="20" height="12" fill="{cols[i % 5]}" transform="translate({x:.1f} {y:.1f}) rotate({(u * 400 + i * 47) % 360:.1f})"/>')
    return f'<g opacity="{1 - ramp(t, t0 + 1.2, .4):.3f}">{"".join(o)}</g>'


def phone_scroll(x, y, k, t, rot=0.0):
    """Телефон с бегущей лентой (карточки едут вверх)."""
    cards = ""
    off = (t * 600) % 220
    for i in range(5):
        cy = -260 + 220 * i - off
        cards += shape(lib.rrect(-110, cy - 90, 110, cy + 90, 16), ("#ffd0d8", "#cfe8ff", "#d8f5c8", "#fff0b0", "#e8d8ff")[i % 5], "", w=2.5,
                       seed=5600 + i)
        cards += blob(ellipse_pts(-60, cy - 30, 30, 30, 12), "#ffffff", .8)
    inner = f'<g clip-path="none">{cards}</g>'
    o = shape(lib.rrect(-140, -300, 140, 300, 36), "#2a2d36", "", w=5, seed=5610)
    o += shape(lib.rrect(-122, -276, 122, 276, 22), "#fbf8f1", inner, w=3, seed=5611)
    return tf(o, x, y, k, rot)


def room(t):
    return [plain_room(t), rug(540, RFL + 150, 600)]


# ═══════════════ ХУК ═══════════════
def frame_s01(t):
    """ХУК: студия загорается, вспышки, кот-ведущий за стойкой с микрофоном."""
    fl = max(bump(t, 0.0, .03, .25), bump(t, W(2), .04, .25), bump(t, W(4), .04, .25))
    o = [studio(t, flash=fl)]
    hop = .6 * bump(t, W(0), .1, .3) + .5 * bump(t, W(3), .1, .3)
    o.append(host_cat(540, SFL - 300 - 40 * hop, 1.35, t, dict(look=(0, .3), tilt=6 * math.sin(t * 5))))
    o.append(counter(540, SFL + 20))
    o.append(PR.sparkles(540, 900, 2.2, bump(t, W(2), .05, .5), t, seed=11, n=8, r=420))
    dx, dy = shake(t, W(2), 10)
    return hook_view("".join(o), t, HIT, 540, 1120, 1.5, 0, bg=ST_BG, dx=dx, dy=dy)


def frame_s02(t):
    """«Тогда это для вас!»: кот вытягивает лапу к зрителю, наезд, конфетти и вспышка на «вас»."""
    a, b = T0("s02"), T1("s02")
    tv = W(8)
    o = [studio(t, flash=bump(t, tv, .04, .3))]
    pt = ease_out(ramp(t, a, .3))
    o.append(host_cat(540, SFL - 300, 1.35, t, dict(look=(0, .5), tilt=-4), point=pt))
    o.append(counter(540, SFL + 20))
    o.append(confetti(t, tv - .05, cx=540, y0=600))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tv, 12)
    return view("".join(o), 540 + dx, 1020 + dy, 1.35 + .25 * u, 0, bg=ST_BG, t=t)


# ═══════════════ ПРОБЛЕМА ═══════════════
def frame_s03(t):
    """«Садитесь за дело»: Дима садится к ноутбуку, решительный."""
    a, b = T0("s03"), T1("s03")
    o = desk_room(t, mode="day")
    sit = ease_out(ramp(t, a - .1, .4))
    f = dima_desk(t, "sure82", "sit_desk", lean=.1 + .2 * (1 - sit))
    o.append(f["svg"])
    o.append(PR.laptop(700, DESK_Y, .55, 1.0, screen="page", lines=.3, t=t))
    o.append(PR.mug(880, DESK_Y, 1.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(11), 6)
    return view("".join(o), 560 + dx, 900 + dy, 1.5 + .08 * u, 0, t=t)


def frame_s04(t):
    """«через минуту листаете ленту?»: Дима откинулся, листает телефон, ноутбук забыт; часики «+1 мин»."""
    a, b = T0("s04"), T1("s04")
    o = desk_room(t, mode="day")
    f = dima_desk(t, {"brows": "calm", "mouth": "smile", "smile": .5, "lid": .6, "look": (.6, .9)}, "sit_desk", lean=-.15)
    o.append(f["svg"])
    o.append(PR.laptop(700, DESK_Y, .55, 1.0, screen="page", lines=.3, t=t))
    hx, hy = f["head"]
    o.append(phone_scroll(hx + 170, hy + 290, .42, t, -18))
    o.append(text("+1 мин", 720, 560, 90 * pop(t, W(14), .25), fill="#FFD23F", stroke="#111", sw=8) if t > W(14) else "")
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 520, 880, 1.45 + .1 * u, 0, t=t)


def flames(x, y, w, t, n=5, h=160.0):
    o = []
    for i in range(n):
        fx = x - w / 2 + w * (i + .5) / n
        o.append(PR.att_flame(fx, y, h / 70 * (.8 + .4 * abs(math.sin(i * 1.7))), t + i * .3, seed=i))
    return "".join(o)


def frame_s05(t):
    """«Дедлайн горит»: лист «ДЕДЛАЙН» с датой, загорается снизу, огонь растёт; часы тикают."""
    a, b = T0("s05"), T1("s05")
    tg = W(18)
    o = [rect(-1400, -1400, 2600, 3400, "#3b3552"), PR.glow(540, 1000, 700, .5 + .3 * ramp(t, tg, .3), "#ff7a3a")]
    sheet = shape(lib.rect_pts(-260, -340, 260, 340), "#fbf8f1", "".join(
        line([(-200, -120 + 60 * q), (200, -120 + 60 * q)], 3, "#9aa0aa", taper=0, wmin=1, seed=5700 + q) for q in range(6)), w=5, seed=5710)
    sheet += text("ДЕДЛАЙН", 0, -210, 84, fill="#e2453a", stroke="#111", sw=6)
    o.append(tf(sheet, 540, 1000, 1.0, -4 + 2 * math.sin(t * 20) * ramp(t, tg, .2)))
    o.append(flames(540, 1340, 560, t, n=6, h=140 + 260 * ease_out(ramp(t, a - .1, .6))))
    o.append(PR.clock(840, 560, 110, angle_h=200, angle_m=(t * 900) % 360))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tg, 12)
    return view("".join(o), 540 + dx, 1000 + dy, 1.05 + .08 * u, 0, bg="#3b3552", t=t)


def frame_s06(t):
    """«а вы моете кружки?»: Дима у раковины трёт кружку, пена, рядом стопка чистых кружек, блёстки."""
    a, b = T0("s06"), T1("s06")
    tk = W(22)
    o = [plain_room(t, wall="#dfeef0", floor="#b9c4c9")]
    o.append(shape(lib.rect_pts(300, RFL - 520, 1100, RFL), "#e9edf2", "", w=5, seed=5800))
    o.append(shape(lib.rect_pts(280, RFL - 560, 1120, RFL - 520), "#c9cdd5", "", w=5, seed=5801))
    o.append(shape(lib.rrect(450, RFL - 560, 760, RFL - 470, 20), "#9aa0aa", "", w=4, seed=5802))
    o.append(line([(600, RFL - 560), (600, RFL - 700), (680, RFL - 700)], 14, "#7d8597", taper=0, wmin=1, seed=5803))
    f = stand(330, t, "sure82", "d82_hold", head_add=.04 * math.sin(t * 8))
    o.append(f["svg"])
    hx, hy = f["hold"]
    rub = 14 * math.sin(t * 22)
    o.append(PR.mug(hx + 40 + rub, hy + 30, 1.3, rot=10 * math.sin(t * 11), col="red", coffee=False))
    for j in range(6):
        ph = (t * 1.5 + j / 6) % 1
        o.append(shape(ellipse_pts(hx + 40 + 60 * math.sin(j * 2.1), hy - 40 - 160 * ph, 16 * (1 - ph) + 4, 16 * (1 - ph) + 4, 10), "#ffffff", "", w=2,
                       seed=5810 + j))
    n = 2 + int(clamp((t - a) / (b - a)) * 4)
    for i in range(n):
        o.append(PR.mug(880 + 60 * (i % 2), RFL - 560 - 85 * (i // 2) - 4, 1.0, coffee=False, col=("red", "blue")[i % 2] if False else "red"))
    o.append(PR.sparkles(900, RFL - 700, 1.4, bump(t, tk, .05, .4), t, seed=61, n=5, r=160))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tk, 6)
    return view("".join(o), 600 + dx, 1050 + dy, 1.2 + .06 * u, 0, bg="#dfeef0", t=t)


def wall_cal(x, y, k, year, t, circ=0.0, cross=0.0, seed=0):
    """Настенный лист месяца с годом сверху; «ПН» в первой колонке обведён / перечёркнут."""
    o = shape(lib.rect_pts(-200, -240, 200, 240), "#fbf8f1", blob(lib.rect_pts(-200, -240, 200, -130), "#c8553d"), w=4, seed=5900 + seed)
    o += text(year, 0, -165, 68, fill="#ffffff", stroke="#7a2a1e", sw=5)
    for i, d in enumerate(("ПН", "ВТ", "СР", "ЧТ")):
        o += plain(d, -170 + 90 * i, -80, 34, fill="#1d2448" if i else "#e2453a")
    for r_ in range(4):
        for c in range(4):
            o += rect(-170 + 90 * c, -50 + 70 * r_, -110 + 90 * c, 0 + 70 * r_, "#e3d6bb", .8)
    if circ > 0:
        pts = [(-150 + 50 * math.cos(2 * math.pi * q * circ * 1.1), -92 + 34 * math.sin(2 * math.pi * q * circ * 1.1)) for q in [i / 40 for i in range(41)]]
        o += line(pts, 7, "#e2453a", taper=.1, wmin=.6, seed=5950 + seed)
    if cross > 0:
        o += PR.cross_stroke((-200, -120), (60, -60), (60, -120), (-200, -60), u=cross, w=14, seed=5960 + seed)
    return tf(o, x, y, k)


def frame_s07(t):
    """«Обещаете себе „с понедельника“»: Дима у календаря поднял палец-клятву, «ПН» обводится красным."""
    a, b = T0("s07"), T1("s07")
    o = room(t)
    o.append(wall_cal(740, 860, 1.1, "ГОД 1", t, circ=ramp(t, W(26) - .1, .5)))
    f = stand(300, t, "proud82", "d82_one", head_add=.05)
    o.append(f["svg"])
    hx, hy = f["head"]
    o.append(PR.speech_bubble(hx + 60, hy - 330, 420, 160, u=pop(t, W(25) - .1, .25), seed=7, tail=(-80, 70)))
    if t > W(25):
        o.append(text("С ПН!", hx + 60, hy - 310, 80, fill="#e2453a", stroke="#ffffff", sw=4))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(26), 6)
    return view("".join(o), 540 + dx, 1000 + dy, 1.12 + .06 * u, 0, t=t)


def frame_s08(t):
    """«уже третий год?»: три календаря 2024, 2025, 2026 выезжают подряд, у каждого «ПН» перечёркнут; «×3»."""
    a, b = T0("s08"), T1("s08")
    o = room(t)
    for j, yr in enumerate(("ГОД 1", "ГОД 2", "ГОД 3")):
        tj = a + .25 * j
        if t > tj - .05:
            o.append(wall_cal(240 + 300 * j, 820 + 60 * (j % 2), .7 * pop(t, tj, .2), yr, t, circ=1.0, cross=ramp(t, tj + .15, .2), seed=j))
    f = stand(540, t, "squint82", "d82_shrug", head_add=-.06)
    o.append(f["svg"])
    if t > W(28):
        o.append(text("×3", 900, 560, 200 * pop(t, W(28), .25), fill="#e2453a", stroke="#111", sw=12))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(29), 10)
    return view("".join(o), 540 + dx, 1000 + dy, 1.05 + .05 * u, 0, t=t)


# ═══════════════ РЕШЕНИЕ ═══════════════
def frame_s09(t):
    """«Встречайте!»: прожекторы сходятся на подиуме, кот-ведущий у края разводит лапами; вспышка."""
    a, b = T0("s09"), T1("s09")
    o = [studio(t, flash=bump(t, a + .05, .04, .3))]
    o.append(podium(560, SFL))
    o.append(PR.glow(560, SFL - 300, 380, .5 * ramp(t, a, .4), "#fff4c0"))
    o.append(host_cat(900, SFL, 1.0, t, dict(look=(-.8, -.2)), point=.0))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, a + .05, 8)
    return view("".join(o), 640 + dx, 1100 + dy, 1.0 + .1 * u, 0, bg=ST_BG, t=t)


def frame_s10(t):
    """«Две минуты!»: на подиуме выпрыгивает коробка «2 МИНУТЫ» с бантом, звёзды и конфетти."""
    a, b = T0("s10"), T1("s10")
    tb = W(32)
    o = [studio(t, flash=bump(t, tb, .04, .3))]
    o.append(podium(560, SFL))
    o.append(PR.glow(560, SFL - 400, 420, .6, "#fff4c0"))
    jump = pop(t, a, .3)
    o.append(gift(560, SFL - 190 - 60 * bump(t, tb, .08, .3), 1.1 * jump, sq=-.4 * bump(t, tb, .05, .2)))
    o.append(confetti(t, tb - .05, cx=560, y0=500))
    o.append(host_cat(950, SFL, .9, t, dict(look=(-.8, -.2))))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb, 10)
    return view("".join(o), 620 + dx, 1080 + dy, 1.12 + .08 * u, 0, bg=ST_BG, t=t)


def frame_s11(t):
    """«Просто откройте дело»: крышка коробки слетает, из коробки поднимается ноутбук с открытым делом."""
    a, b = T0("s11"), T1("s11")
    to = W(34)
    o = [studio(t)]
    o.append(podium(540, SFL))
    o.append(PR.glow(540, SFL - 500, 460, .6, "#fff4c0"))
    rise = ease_out(ramp(t, to + .1, .5))
    o.append(PR.laptop(540, SFL - 300 - 320 * rise, .8, open_=ramp(t, to + .4, .4), screen="page", lines=ramp(t, W(35), .5), t=t))
    o.append(gift(540, SFL - 190, 1.1, lid=ramp(t, to, .35)))
    o.append(PR.sparkles(540, SFL - 700, 2.0, bump(t, to + .5, .05, .5), t, seed=111, n=7, r=300))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, to, 8)
    return view("".join(o), 540 + dx, 1050 + dy, 1.2 + .08 * u, 0, bg=ST_BG, t=t)


def timer_badge(x, y, k, secs, t, ring=0.0):
    m, s = int(secs // 60), int(secs % 60)
    o = shape(lib.rrect(-170, -80, 170, 80, 40), "#1d2448", "", w=5, seed=6000)
    o += text(f"{m}:{s:02d}", 0, 32, 96, fill="#7bd65a" if secs < 120 else "#FFD23F", stroke="#111", sw=4)
    return tf(o, x, y, k * (1 + .12 * ring))


def frame_s12(t):
    """«и поработайте две минуты»: Дима за ноутбуком печатает, над ним табло-таймер бежит к 2:00."""
    a, b = T0("s12"), T1("s12")
    o = desk_room(t, mode="day")
    f = dima_desk(t, "sure82", "sit_desk", lean=.15)
    o.append(f["svg"])
    o.append(PR.laptop(700, DESK_Y, .55, 1.0, screen="page", lines=.3 + .6 * ramp(t, a, b - a), t=t))
    secs = 120 * ramp(t, a + .1, b - a - .1) * .8
    o.append(timer_badge(560, 560, 1.0, secs, t))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 860, 1.4 + .08 * u, 0, t=t)


# ═══════════════ ДИМА-ПОКУПАТЕЛЬ ═══════════════
def frame_s13(t):
    """Дима: «Я не верил»: Дима в студии, руки разведены скептически, табличка «ПОКУПАТЕЛЬ»."""
    a, b = T0("s13"), T1("s13")
    o = [studio(t, beams=.6)]
    f = stand(540, t, "squint82", "d82_shrug", fl=SFL, k=.74, head_add=-.08)
    o.append(f["svg"])
    pl = shape(lib.rrect(-230, -50, 230, 50, 18), "#ffd23f", "", w=5, seed=6100) + text("ПОКУПАТЕЛЬ", 0, 18, 52, fill="#111", stroke="#ffd23f", sw=1)
    o.append(tf(pl, 540, SFL + 120, 1.0 * pop(t, a, .25)))
    o.append(PR.question_mark(860, 520, 1.6))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(42), 6)
    return view("".join(o), 540 + dx, 1060 + dy, 1.1 + .06 * u, 0, bg=ST_BG, t=t)


def frame_s14(t):
    """«Но через две минуты»: секундомер крупно, стрелка доходит до верха, звонок; табло 2:00."""
    a, b = T0("s14"), T1("s14")
    td = W(46) + .3
    o = [rect(-1400, -1400, 2600, 3400, "#3b3552"), PR.glow(540, 960, 700, .4, "#8fb7ff")]
    ang = 300 + 60 * clamp((t - a) / (td - a))
    o.append(PR.stopwatch(540, 1080, 1.3, hand_a=ang, click=bump(t, td, .05, .2), t=t))
    if t > td:
        o.append(timer_badge(540, 560, 1.0, 120, t, ring=bump(t, td, .05, .3)))
        o.append(PR.sparkles(540, 1080, 2.2, bump(t, td, .05, .5), t, seed=141, n=8, r=360))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, td, 10)
    return view("".join(o), 540 + dx, 980 + dy, 1.0 + .08 * u, 0, bg="#3b3552", t=t)


def frame_s15(t):
    """«я просто не смог остановиться»: Дима печатает быстро, руки мелькают, линии скорости, таймер бежит дальше 2:00."""
    a, b = T0("s15"), T1("s15")
    o = desk_room(t, mode="day")
    f = dima_desk(t, "laugh82" if t > W(50) else "sure82", "sit_desk", lean=.2 + .03 * math.sin(t * 30))
    o.append(f["svg"])
    o.append(PR.laptop(700, DESK_Y, .55, 1.0, screen="page", lines=1.0, t=t))
    for j in range(5):
        y = DESK_Y - 160 + 40 * j
        ph = (t * 4 + j * .3) % 1
        o.append(line([(860 + 200 * ph, y), (960 + 200 * ph, y)], 6, "#2f8fe0", taper=.6, seed=6200 + j, op=1 - ph))
    secs = 120 + 300 * ramp(t, a, b - a)
    o.append(timer_badge(560, 560, 1.0, secs, t, ring=bump(t, W(51), .05, .3)))
    o.append(PR.sparkles(700, DESK_Y - 200, 1.6, bump(t, W(51), .05, .5), t, seed=151, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(51), 7)
    return view("".join(o), 580 + dx, 860 + dy, 1.4 + .12 * u, 0, t=t)


# ═══════════════ «ЭТО ЕЩЁ НЕ ВСЁ» ═══════════════
def frame_s16(t):
    """«Но подождите, это ещё не всё!»: кот-ведущий крупно, лапа вверх, вспышки."""
    a, b = T0("s16"), T1("s16")
    tn = W(57)
    o = [studio(t, flash=bump(t, tn, .04, .3))]
    o.append(host_cat(540, SFL - 300, 1.35, t, dict(look=(0, .4), tilt=-6 + 4 * math.sin(t * 6), perk=1.0), point=.5 + .3 * ease_out(ramp(t, a, .3))))
    o.append(counter(540, SFL + 20))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tn, 12)
    return view("".join(o), 540 + dx, 1000 + dy, 1.55 + .15 * u, 0, bg=ST_BG, t=t)


def frame_s17(t):
    """«К двум минутам вы получаете кота»: на подиуме коробка «2 МИНУТЫ», выскакивает «+», кот в бабочке запрыгивает рядом."""
    a, b = T0("s17"), T1("s17")
    tc = W(63)
    o = [studio(t)]
    o.append(podium(540, SFL))
    o.append(PR.glow(540, SFL - 400, 460, .6, "#fff4c0"))
    o.append(gift(400, SFL - 190, .8))
    if t > W(60):
        o.append(text("+", 590, SFL - 330, 200 * pop(t, W(60), .2), fill="#FFD23F", stroke="#111", sw=12))
    j = ease_out(ramp(t, tc - .35, .45))
    cx = 1250 + (730 - 1250) * j
    cy = SFL - 190 - 300 * math.sin(math.pi * j)
    o.append(host_cat(cx, cy, .9, t, dict(look=(-.4, .3), legs=1.0 - j if j < 1 else 0.0, smile=1.0), mic=False))
    o.append(PR.sparkles(730, SFL - 400, 1.8, bump(t, tc + .1, .05, .5), t, seed=171, n=6, r=240))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tc + .1, 9)
    return view("".join(o), 560 + dx, 1100 + dy, 1.15 + .06 * u, 0, bg=ST_BG, t=t)


def frame_s18(t):
    """«который сидит рядом!»: Дима работает за ноутбуком, кот с бабочкой сидит рядом на столе и смотрит в экран."""
    a, b = T0("s18"), T1("s18")
    o = desk_room(t, mode="day")
    f = dima_desk(t, "proud82", "sit_desk", lean=.12)
    o.append(f["svg"])
    o.append(PR.laptop(610, DESK_Y, .55, 1.0, screen="page", lines=.8, t=t))
    o.append(host_cat(850, DESK_Y, .62, t, dict(look=(-.8, .3), smile=1.0, tail=10 * math.sin(t * 2.5)), mic=False))
    o.append(PR.sparkles(850, DESK_Y - 250, 1.4, bump(t, W(66), .05, .5), t, seed=181, n=5, r=160))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(66), 6)
    return view("".join(o), 600 + dx, 880 + dy, 1.45 + .08 * u, 0, t=t)


# ═══════════════ ПРИЗЫВ ═══════════════
def cta(t, zoom=1.0, focus=None):
    c = SH["cta"]
    if "bg" not in TG._ST:
        TG._ST["bg"] = TG.background(lib)
        TG.prepare(COMMON)
        lib.static_done()
    lib.dyn_begin()
    body, (cx, cy, s, rot) = TG.layer(t, c["t0"], c["press"], COMMON)
    if focus:
        cx, cy = cx + (focus[0] - cx) * .3, cy + (focus[1] - cy) * .3
    return lib.svg(f'<rect width="1080" height="1920" fill="#6e4a32"/><g transform="{lib.cam(cx, cy, s * zoom, rot)}">{TG._ST["bg"]}{body}</g>{over(t)}')


def frame_s19(t):
    return cta(t)


def frame_s20(t):
    return cta(t, 1.1, (540, 1000))


def frame_s21(t):
    return cta(t, 1.04)


# ═══════════════ ИТОГ И ПЕТЛЯ ═══════════════
def sign(x, y, k, word, col, u=1.0):
    o = shape(lib.rrect(-170, -70, 170, 70, 20), col, "", w=6, seed=6300 + len(word))
    o += text(word, 0, 30, 92, fill="#ffffff", stroke="#111", sw=8)
    o += line([(-120, 70), (-120, 160)], 10, "#7a5232", taper=0, wmin=1, seed=6310) + line([(120, 70), (120, 160)], 10, "#7a5232", taper=0, wmin=1, seed=6311)
    return tf(o, x, y, k * u)


def folder(x, y, k, closed=1.0):
    o = shape(lib.rrect(-120, -90, 120, 90, 12), "#f2b541", blob(lib.rect_pts(-120, -90, 120, -40), "#e09a20", .7), w=4, seed=6400)
    o += shape(lib.rrect(-120, -110, -30, -86, 8), "#f2b541", "", w=4, seed=6401)
    o += line([(-90, -10), (90, -10)], 4, "#7a5232", taper=0, wmin=1, seed=6402)
    return tf(o, x, y, k)


def frame_s22(t):
    """ИТОГ: слева табличка «ДО» — Дима в куче из десяти начатых дел (листы, кружки, телефон), справа «ПОСЛЕ» — Дима с закрытой папкой и
    большой галочкой, кот рядом. Делит вертикальная черта."""
    a, b = T0("s22"), T1("s22")
    ta, tb = a + .25, a + .9
    o = [rect(-1400, -1400, 540, 3400, "#d9d3c4"), rect(540, -1400, 2600, 3400, "#f3e7c4")]
    o.append(rect(-1400, RFL, 540, 3400, "#b9ad95"))
    o.append(rect(540, RFL, 2600, 3400, FLOOR_C))
    o.append(line([(540, -1400), (540, 3400)], 10, seed=6500, taper=0, wmin=1))
    o.append(sign(270, 520, .9, "ДО", "#7d8597", pop(t, ta, .25)))
    o.append(sign(810, 520, .9, "ПОСЛЕ", "#3fb26a", pop(t, tb, .25)))
    o.append(PR.paper_pile(170, RFL, 1.5, seed=3))
    o.append(PR.paper_stack(380, RFL, 1.0, n=7, seed=4, mess=.6))
    for j in range(3):
        o.append(PR.mug(110 + 70 * j, RFL - 10, .9, coffee=False))
    f = stand(300, t, "puzzled82", "d82_rest", k=.62, head_add=-.08)
    o.append(f["svg"])
    f2 = stand(700, t, "laugh82", "d82_hold", k=.62)
    o.append(f2["svg"])
    hx, hy = f2["hold"]
    o.append(folder(hx + 10, hy - 30, .75))
    o.append(PR.check_mark(hx + 10, hy - 40, 3.2, ramp(t, tb + .1, .3)))
    o.append(cat(980, RFL, .55, t, dict(look=(-.7, -.5), smile=1.0)))
    o.append(PR.sparkles(820, 900, 1.6, bump(t, tb + .1, .05, .5), t, seed=221, n=6, r=260))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb, 6)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .04 * u, 0, bg="#d9d3c4", t=t)


def frame_s23(t):
    """Петля: кадр хука — студия, кот-ведущий за стойкой."""
    a, b = T0("s23"), T1("s23")
    o = [studio(t)]
    o.append(host_cat(540, SFL - 300, 1.35, t, dict(look=(0, .3))))
    o.append(counter(540, SFL + 20))
    return loop_view("".join(o), t, a, b, HIT, 540, 1120, 1.5, bg=ST_BG)


def frame(sid, t):
    if sid not in ("s19", "s20", "s21"):
        lib.DEFS.clear()
    return globals()["frame_" + sid](t)
