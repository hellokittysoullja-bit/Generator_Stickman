"""Рилс 134 «Если бы мой день был игрой», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920.
Говорит Дима от первого лица (male2). Кухня как уровень игры: интерфейс поверх — полоска энергии, окно квеста, кружка-босс
с полоской здоровья, красное окно «СОХРАНЕНИЕ НЕ УДАЛОСЬ», бонус от кота-помощника «+2 МИНУТЫ». На экране только слова и
числа из звучащей фразы. Призыв — число в комментариях (поле комментария, шкала от 1 до 10). NOCAM=1 — без влёта и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402

HIT = stress(3, .4)
INK2 = "#1d2448"
HUD = "#1b2140"
GOLDY = "#FFD23F"
SINK = (640.0, 1180.0)          # раковина: центр устья на столешнице
COUNTER_Y = 1180.0


# ═════════════ кухня-уровень ═════════════
def kitchen(t, night=0.0):
    o = [rect(-1400, -1400, 2600, COUNTER_Y, "#dfe8e4")]
    for i in range(-12, 22):
        for j in range(-6, 12):
            o.append(line([(i * 110, j * 110), (i * 110 + 110, j * 110)], 2, "#c5d3ce", taper=0, wmin=1, seed=100 + i * 30 + j))
        o.append(line([(i * 110, -800), (i * 110, COUNTER_Y)], 2, "#c5d3ce", taper=0, wmin=1, seed=900 + i))
    o.append(PR.window(220, 760, 300, 380, mode="night" if night > .5 else "day", t=t, seed=3, curtain=False))
    o.append(shape(lib.rect_pts(-1400, COUNTER_Y, 2600, COUNTER_Y + 40), "#c9a27a", "", w=5, seed=101))
    o.append(shape(lib.rect_pts(-1400, COUNTER_Y + 40, 2600, RFL), "#6fa3a0", "".join(
        line([(x_, COUNTER_Y + 60), (x_, RFL - 20)], 3, "#4f8380", taper=0, wmin=1, seed=110 + i) for i, x_ in enumerate(range(-200, 1400, 280))), w=5, seed=102))
    o.append(rect(-1400, RFL, 2600, RFL + 1400, FLOOR_C))
    o.append(line([(-1400, RFL), (2600, RFL)], 5, seed=11))
    sx, sy = SINK
    o.append(shape(ellipse_pts(sx, sy + 6, 200, 34, 24), "#9aa7b0", blob(ellipse_pts(sx, sy + 14, 180, 24, 20), "#6f7c86"), w=4, seed=120))
    return o


def tap(x, y, k=1.0, water=0.0, t=0.0):
    """Кран (основание на столешнице в (x, y)); water — струя."""
    o = shape(lib.rrect(-24, -40, 24, 0, 8), "#b8c2ca", "", w=4, seed=130)
    o += line([(0, -40), (0, -150), (40, -190), (110, -190), (130, -170)], 22, "#b8c2ca", taper=0, wmin=1, seed=131)
    o += line([(0, -40), (0, -150), (40, -190), (110, -190), (130, -170)], 8, "#e8eef2", taper=0, wmin=1, seed=132)
    o += shape(ellipse_pts(-6, -120, 32, 14, 12), "#e2453a", "", w=3, seed=133)
    if water > 0:
        o += line([(130, -165), (128 + 2 * math.sin(t * 30), -165 + 180 * water)], 14, "#8fc8ff", taper=0, wmin=1, seed=134)
    return tf(o, x, y, k)


def boss_mug(x, y, k, t, hp=1.0, angry=1.0, fall=0.0, clean=0.0, glow=0.0):
    """Кружка-босс (дно в (x, y)): грязная кружка с злыми глазами, над ней полоска здоровья; fall — падает набок; clean — чистая и довольная."""
    o = ""
    if glow > 0:
        o += PR.glow(0, -50, 140, glow, "#fff1b0")
    o += PR.mug(0, 0, 1.0, col="red", coffee=False)
    if clean < 1:
        for j in range(5):
            o += blob(ellipse_pts(-20 + 11 * j, -46 + 9 * (j % 3), 6, 5, 8), "#7a5a3a", .85 * (1 - clean))
        o += blob(ellipse_pts(0, -78, 26, 7, 12), "#6b4a2b", .9 * (1 - clean))
    for s_ in (-1, 1):
        o += shape(ellipse_pts(s_ * 12, -52, 8, 9, 10), "#ffffff", blob(ellipse_pts(s_ * 12 + 2, -50, 4, 5, 8), "#111"), w=2.2, seed=140 + s_)
        if angry > 0 and clean < .5:
            o += line([(s_ * 4, -62 + 4 * angry), (s_ * 22, -68 - 2 * angry)], 3, "#111", seed=142 + s_)
    if clean >= .5:
        o += line([(-10, -32), (0, -26), (10, -32)], 3, "#111", seed=145)
    else:
        o += line([(-10, -26), (0, -31), (10, -26)], 3, "#111", seed=146)
    body = tf(o, 0, 0, 1.0, 90 * ease_io(clamp(fall)))
    out = tf(body, x, y, k)
    if hp is not None:
        w_ = 50 * k
        out += f'<rect x="{x - w_:.1f}" y="{y - 86 * k - 40:.1f}" width="{2 * w_:.1f}" height="{12 * min(k, 3.2):.1f}" rx="{4 * min(k, 3.2):.1f}" fill="#3b0f0f" stroke="#111" stroke-width="{3 * k / 2:.1f}"/>'
        if hp > 0:
            out += f'<rect x="{x - w_:.1f}" y="{y - 86 * k - 40:.1f}" width="{2 * w_ * clamp(hp):.1f}" height="{12 * min(k, 3.2):.1f}" rx="{4 * min(k, 3.2):.1f}" fill="#e2453a"/>'
    return out


def energy(u, x=60.0, y=200.0, w=440.0, flash=0.0):
    """Полоска энергии (экранные координаты, слева вверху): молния и шкала."""
    o = f'<g transform="translate({x:.1f} {y:.1f})">'
    o += f'<rect x="0" y="0" width="{w + 90:.1f}" height="78" rx="20" fill="{HUD}" opacity=".85" stroke="#111" stroke-width="5"/>'
    o += '<path d="M44 10 L22 44 L40 44 L32 70 L60 32 L42 32 L52 10 Z" fill="#FFD23F" stroke="#111" stroke-width="3" stroke-linejoin="round"/>'
    o += f'<rect x="76" y="20" width="{w:.1f}" height="38" rx="12" fill="#2c3354"/>'
    col = lib.mix("#e2453a", "#46d36b", clamp(u * 1.6))
    if u > 0:
        o += f'<rect x="76" y="20" width="{w * clamp(u):.1f}" height="38" rx="12" fill="{col}"/>'
    if flash > 0:
        o += f'<rect x="76" y="20" width="{w:.1f}" height="38" rx="12" fill="#ffffff" opacity="{.6 * flash:.2f}"/>'
    return o + "</g>"


def quest_win(lines, u=1.0, x=540.0, y=360.0, w=900.0, head="КВЕСТ", col="#2f5fd0", size=64):
    """Окно игры (экранные координаты): цветная шапка и строки."""
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.0) if u < 1 else 1.0
    h = 110 + 86 * len(lines)
    o = f'<rect x="{-w / 2 + 12:.1f}" y="{-h / 2 + 14:.1f}" width="{w:.1f}" height="{h:.1f}" rx="26" fill="#000" opacity=".3"/>'
    o += f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="26" fill="#fbf8ef" stroke="#111" stroke-width="7"/>'
    o += f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="92" rx="26" fill="{col}" stroke="#111" stroke-width="7"/>'
    o += text(head, 0, -h / 2 + 68, 60, fill="#ffffff", stroke="#111", sw=6)
    for j, ln in enumerate(lines):
        o += text(ln, 0, -h / 2 + 170 + 86 * j, size, fill=INK2, stroke="#fbf8ef", sw=.01)
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">{o}</g>'


def plus2(x, y, u):
    """Бонус «+2 МИНУТЫ»: плюс рисуется формой (в шрифте его нет)."""
    if u <= .01:
        return ""
    s = lib.back_out(clamp(u), 2.4) if u < 1 else 1.0
    o = '<rect x="-330" y="-80" width="660" height="160" rx="40" fill="#46d36b" stroke="#111" stroke-width="7"/>'
    o += '<path d="M-270 -12 h30 v-30 h24 v30 h30 v24 h-30 v30 h-24 v-30 h-30 Z" fill="#ffffff" stroke="#111" stroke-width="4"/>'
    o += text("2 МИНУТЫ", 50, 30, 84, fill="#ffffff", stroke="#1e5a32", sw=7)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate(-3) scale({s:.4f})">{o}</g>'


def gview(o, cx, cy, s, t, hud="", dx=0.0, dy=0.0, bg=BG):
    return view("".join(o), cx + dx, cy + dy, s, 0, bg=bg, t=t, extra=hud)


def dima_at(t, x=300.0, expr="calm82", pose="d82_rest", **kw):
    return stand(x, t, expr, pose, k=.68, **kw)


# ═════════════ планы ═════════════
def frame_s01(t):
    """ХУК: кухня-уровень, огромная грязная кружка-босс с злыми глазами в раковине, Дима с губкой на старте, кот-помощник."""
    tl = HIT
    o = kitchen(t)
    o.append(tap(SINK[0] + 120, COUNTER_Y, 1.0))
    hop = -30 * bump(t, tl, .05, .3)
    o.append(boss_mug(SINK[0] + 80, COUNTER_Y + 10 + hop, 8.2, t, hp=1.0))
    f = dima_at(t, 170, "wow82", "d82_hold")
    o.append(f["svg"])
    o.append(cat(980, RFL, .7, t, dict(look=(-.8, -.6), perk=1.0, tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(SINK[0] - 20, COUNTER_Y - 200, 1.8, bump(t, tl, .05, .5), t, seed=11, n=6, r=260))
    dx, dy = shake(t, tl, 12)
    return hook_view("".join(o), t, HIT, 560, 940, .98, 0, dx=dx, dy=dy)


def frame_s02(t):
    """«был игрой»: тот же уровень, сверху загорается полоска энергии, Дима встаёт в стойку, кот рядом."""
    a, b = T0("s02"), T1("s02")
    o = kitchen(t)
    o.append(tap(SINK[0] + 120, COUNTER_Y, 1.0))
    o.append(boss_mug(SINK[0] - 20, COUNTER_Y + 10, 2.6, t, hp=1.0))
    f = dima_at(t, 300, "proud82", "d82_one")
    o.append(f["svg"])
    o.append(cat(900, RFL, .7, t, dict(look=(-.8, -.6), smile=1.0, perk=1.0)))
    hud = energy(ramp(t, a - .1, .4), flash=bump(t, W(5), .05, .3)) if not NOCAM else ""
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(5), 7)
    return gview(o, 560, 900, 1.05 + .05 * uu, t, hud, dx, dy)


def frame_s03(t):
    """«Первый квест»: окно «ПЕРВЫЙ КВЕСТ» выскакивает над кухней."""
    a, b = T0("s03"), T1("s03")
    o = kitchen(t)
    o.append(tap(SINK[0] + 120, COUNTER_Y, 1.0))
    o.append(boss_mug(SINK[0] - 20, COUNTER_Y + 10, 2.6, t, hp=1.0))
    f = dima_at(t, 300, "proud82", "d82_rest")
    o.append(f["svg"])
    o.append(cat(900, RFL, .7, t, dict(look=(-.6, -.8), smile=1.0, perk=1.0)))
    hud = energy(1.0) + quest_win(["ПЕРВЫЙ"], pop(t, a - .05, .3), y=560, w=760, head="КВЕСТ") if not NOCAM else ""
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(7), 7)
    return gview(o, 560, 900, 1.05 + .05 * uu, t, hud, dx, dy)


def frame_s04(t):
    """«помыть одну кружку»: окно квеста крупно — «Помыть одну кружку», рядом кружка-значок."""
    a, b = T0("s04"), T1("s04")
    o = kitchen(t)
    f = dima_at(t, 300, "doubt", "d82_rest")
    o.append(f["svg"])
    o.append(rect(-1400, -1400, 2600, 3400, HUD, .35))
    hud = energy(1.0) if not NOCAM else ""
    hud += quest_win(["Помыть", "одну кружку"], 1.0, y=620, w=860, head="ПЕРВЫЙ КВЕСТ", size=80)
    hud += boss_mug(640, 1300, 3.6, t, hp=None, angry=0.0)
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(10), 6)
    return gview(o, 560, 900, 1.1 + .04 * uu, t, hud, dx, dy)


def frame_s05(t):
    """«Уровень сложности: босс»: кружка вырастает в босса, полоска здоровья, красная плашка «БОСС», тряска."""
    a, b = T0("s05"), T1("s05")
    tb = W(13)
    grow = ease_out(ramp(t, tb - .25, .35))
    o = kitchen(t)
    o.append(tap(SINK[0] + 120, COUNTER_Y, 1.0))
    o.append(PR.glow(SINK[0], COUNTER_Y - 200, 500, .4 * grow, "#ff6a5a"))
    o.append(boss_mug(SINK[0] - 20, COUNTER_Y + 10, 3.0 + 2.2 * grow, t, hp=1.0, angry=.5 + .5 * grow))
    f = dima_at(t, 220, "scared" if grow > .3 else "doubt", "d82_hold")
    o.append(f["svg"])
    hud = energy(1.0) if not NOCAM else ""
    hud += quest_win(["СЛОЖНОСТИ"], 1.0, y=520, w=760, head="УРОВЕНЬ", col="#7a3fd0")
    if grow > 0:
        hud += tf(shape(lib.rrect(-200, -70, 200, 70, 30), RED, "", w=6, seed=150) + text("БОСС", 0, 30, 96, fill="#ffffff", stroke="#7a1e18", sw=7),
                  740, 1240, pop(t, tb - .1, .25), -6)
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tb, 14)
    return gview(o, 560, 900, 1.04 + .05 * uu, t, hud, dx, dy)


def frame_s06(t):
    """«Полоска энергии кончилась»: полоска энергии крупно стекает до нуля и мигает красным; Дима обмякает."""
    a, b = T0("s06"), T1("s06")
    e = 1 - ease_io(ramp(t, a, WE(16) - a))
    o = kitchen(t)
    o.append(boss_mug(SINK[0] - 20, COUNTER_Y + 10, 3.6, t, hp=1.0))
    f = dima_at(t, 260, "zombie" if e < .5 else "doubt", "d82_rest", head_add=.15 * (1 - e))
    o.append(f["svg"])
    hud = ""
    if not NOCAM:
        blink = .5 + .5 * math.sin(t * 20) if e < .05 else 0.0
        hud = f'<g transform="translate(540 420) scale(1.7) translate(-265 -39)">{energy(e, 0, 0)}</g>'
        if blink > 0:
            hud += f'<rect x="60" y="350" width="960" height="140" rx="30" fill="#e2453a" opacity="{.35 * blink:.2f}"/>'
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, WE(16), 8)
    return gview(o, 560, 900, 1.05 + .05 * uu, t, hud, dx, dy)


def frame_s07(t):
    """«на втором шаге: открыть кран»: окно «ШАГ 2 — открыть кран», Дима тянет руку к крану и сползает по столешнице."""
    a, b = T0("s07"), T1("s07")
    sl = ease_io(ramp(t, W(20) - .1, .6))
    o = kitchen(t)
    o.append(boss_mug(SINK[0] + 260, COUNTER_Y + 10, 3.2, t, hp=1.0))
    o.append(tap(SINK[0] + 60, COUNTER_Y, 1.3))
    f = dima_at(t, 420, "zombie", "d82_rest", head_add=.2, lean_add=.25 * sl,
                arms={"n": ("ik", (SINK[0] - 40 - 60 * sl, COUNTER_Y - 160 + 220 * sl), -1)})
    o.append(f["svg"])
    hud = energy(0.0) if not NOCAM else ""
    hud += quest_win(["Шаг 2: открыть кран"], 1.0, y=470, w=900, head="КВЕСТ", size=62)
    uu = ease_io(ramp(t, a, b - a))
    return gview(o, 620, 900, 1.15 + .05 * uu, t, hud)


def frame_s08(t):
    """«Сохранение не удалось»: тёмный экран, красное окно «СОХРАНЕНИЕ НЕ УДАЛОСЬ», сбой полосами; Дима и кружка серые позади."""
    a, b = T0("s08"), T1("s08")
    o = kitchen(t)
    o.append(boss_mug(SINK[0] - 20, COUNTER_Y + 10, 3.2, t, hp=1.0))
    f = dima_at(t, 300, "zombie", "d82_rest", head_add=.2)
    o.append(f["svg"])
    o.append(rect(-1400, -1400, 2600, 3400, "#0b0d1a", .6))
    hud = ""
    gl = bump(t, a + .02, .03, .2) + bump(t, W(24), .03, .2)
    if gl > .05:
        for j in range(5):
            yy = (j * 377 + int(t * 60) * 131) % 1500 + 200
            hud += f'<rect x="0" y="{yy}" width="1080" height="{16 + 10 * j}" fill="#e2453a" opacity="{.35 * min(1, gl):.2f}"/>'
    hud += quest_win(["НЕ УДАЛОСЬ"], pop(t, a - .05, .25), y=880, w=900, head="СОХРАНЕНИЕ", col="#d8352a", size=96)
    dx, dy = shake(t, W(24), 12)
    uu = ease_io(ramp(t, a, b - a))
    return gview(o, 560 + dx, 900 + dy, 1.05 + .05 * uu, t, hud)


def frame_s09(t):
    """«Начинать придётся с утра»: ночь, Дима в кровати под одеялом, за окном луна; плашка «С УТРА»."""
    a, b = T0("s09"), T1("s09")
    o = [rect(-1400, -1400, 2600, RFL, "#3b3f66"), rect(-1400, RFL, 2600, 3400, "#2a2d4a")]
    o.append(PR.window(780, 820, 300, 380, mode="night", t=t, seed=5, curtain=False))
    o.append(shape(lib.rrect(120, RFL - 620, 200, RFL, 12), "#8a5a3a", "", w=5, seed=200))
    o.append(shape(lib.rect_pts(120, RFL - 300, 1000, RFL - 200), "#f4efe4", "", w=5, seed=201))
    o.append(shape(lib.rect_pts(120, RFL - 200, 1000, RFL - 120), "#8a5a3a", "", w=5, seed=202))
    for x_ in (150, 970):
        o.append(shape(lib.rect_pts(x_ - 18, RFL - 120, x_ + 18, RFL), "#6e4a2c", "", w=4, seed=203 + x_))
    o.append(PR.pillow(270, RFL - 330, 1.1))
    o.append(shape([(560, RFL - 300, 1), (1000, RFL - 300, 1), (990, RFL - 190, 1), (560, RFL - 190, 1)], "#5b7fc4", "", w=5, seed=204))
    x, k = 420.0, .62
    feet = {"n": ((x + 230 * k, RFL - 10), 0.0), "f": ((x + 180 * k, RFL - 16), 0.0)}
    f = people.dima82(x, RFL - 320, k, "sleepy", "sit_desk", t=t, feet=feet, lean_add=-.05, head_add=.15)
    o.append(f["svg"])
    o.append(PR.zzz(560, RFL - 760, 1.0, t, 1.0))
    o.append(CT.curl(840, RFL - 300, .5, dict(eye=.0), t))
    o.append(tf(shape(lib.rrect(-200, -66, 200, 66, 30), GOLDY, "", w=5, seed=160) + text("С УТРА", 0, 26, 80, fill="#111", stroke="#111", sw=.01),
                540, 760, pop(t, W(28) - .15, .25), -3))
    uu = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 1120, 1.05 + .05 * uu, 0, bg="#3b3f66", t=t)


def gift(x, y, k, lid=0.0, glow_=0.0):
    o = ""
    if glow_ > 0:
        o += PR.glow(0, -120, 260, glow_, "#fff1b0")
    o += shape(lib.rect_pts(-120, -160, 120, 0), "#46d36b", rect(-18, -160, 18, 0, "#FFD23F"), w=5, seed=170)
    ly = -160 - 120 * lid
    o += tf(shape(lib.rect_pts(-135, -40, 135, 0), "#3cbf5e", rect(-18, -40, 18, 0, "#FFD23F"), w=5, seed=171), 0, ly, 1.0, -25 * lid)
    return tf(o, x, y, k)


def frame_s10(t):
    """«Тогда котик дал бонус»: кот-помощник выпрыгивает с сияющей коробкой бонуса; Дима поднимает голову."""
    a, b = T0("s10"), T1("s10")
    j = ease_out(ramp(t, a - .1, .4))
    lid = ease_out(ramp(t, W(32) - .1, .3))
    o = kitchen(t)
    o.append(boss_mug(SINK[0] - 20, COUNTER_Y + 10, 3.0, t, hp=1.0))
    f = dima_at(t, 260, "hope", "d82_rest")
    o.append(f["svg"])
    o.append(gift(760, RFL, 1.0, lid, .5 + .5 * lid))
    o.append(cat(980 - 60 * j, RFL - 200 * math.sin(math.pi * j), .8, t, dict(look=(-.8, -.4), smile=1.0, legs=1 - j, perk=1.0, paw=.6 * j, paw_dx=-90)))
    o.append(PR.sparkles(760, RFL - 240, 1.8, bump(t, W(32), .05, .5), t, seed=101, n=7, r=260))
    hud = energy(0.0) if not NOCAM else ""
    hud += quest_win([], pop(t, W(32) - .1, .25), y=420, w=520, head="БОНУС", col="#2f9f55")
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(32), 7)
    return gview(o, 600, 900, 1.08 + .05 * uu, t, hud, dx, dy)


def frame_s11(t):
    """«плюс две минуты»: из коробки вылетает карточка «+2 МИНУТЫ», полоска энергии заливается."""
    a, b = T0("s11"), T1("s11")
    e = ease_out(ramp(t, W(34), .4))
    o = kitchen(t)
    o.append(boss_mug(SINK[0] - 20, COUNTER_Y + 10, 3.0, t, hp=1.0))
    f = dima_at(t, 260, "laugh82", "d82_one")
    o.append(f["svg"])
    o.append(gift(760, RFL, 1.0, 1.0, .8))
    o.append(cat(900, RFL, .8, t, dict(look=(-.8, -.4), smile=1.0, perk=1.0)))
    hud = energy(e, flash=bump(t, W(35), .05, .3)) if not NOCAM else ""
    hud += plus2(560, 450, pop(t, a - .05, .3))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(34), 8)
    return gview(o, 600, 900, 1.08 + .05 * uu, t, hud, dx, dy)


def sponge(x, y, k, rot=0.0):
    o = shape(lib.rrect(-60, -34, 60, 34, 10), "#f6d24a", "".join(blob(ellipse_pts(-40 + 20 * i, -6 + 10 * (i % 2), 5, 4, 8), "#d9b330") for i in range(5)),
              w=4, seed=180)
    o += shape(lib.rrect(-60, -34, 60, -12, 8), "#46a35e", "", w=4, seed=181)
    return tf(o, x, y, k, rot)


def frame_s12(t):
    """«С ним босс упал с первого удара»: Дима замахивается губкой и бьёт — полоска здоровья босса в ноль, кружка падает набок."""
    a, b = T0("s12"), T1("s12")
    th = W(42)
    sw = ease_io(ramp(t, th - .35, .3))
    fall = ease_out(ramp(t, th, .35))
    o = kitchen(t)
    o.append(tap(SINK[0] + 120, COUNTER_Y, 1.0, water=1.0, t=t))
    o.append(boss_mug(SINK[0] + 20, COUNTER_Y + 10, 3.4, t, hp=1 - fall, fall=fall))
    hx, hy = 420 + 200 * sw, 1060 + 60 * sw
    f = dima_at(t, 250, "zeal", "d82_rest", arms={"n": ("ik", (hx, hy), -1)})
    o.append(f["svg"])
    o.append(sponge(hx + 20, hy - 10, 1.0, -30 + 50 * sw))
    o.append(cat(950, RFL, .7, t, dict(look=(-.8, -.5), smile=1.0, perk=1.0, tail=12 * math.sin(t * 5))))
    o.append(PR.sparkles(SINK[0], COUNTER_Y - 150, 2.0, bump(t, th, .05, .5), t, seed=121, n=8, r=300))
    hud = energy(1.0) if not NOCAM else ""
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, th, 14)
    return gview(o, 560, 900, 1.1 + .05 * uu, t, hud, dx, dy)


def frame_s13(t):
    """«и кружка чистая»: чистая блестящая кружка крупно, окно «ЧИСТАЯ», Дима и кот дают «пять»."""
    a, b = T0("s13"), T1("s13")
    tc = W(45)
    o = kitchen(t)
    o.append(boss_mug(SINK[0], COUNTER_Y + 10, 3.6, t, hp=None, clean=1.0, glow=.7))
    f = dima_at(t, 260, "laugh82", "d82_one")
    o.append(f["svg"])
    o.append(cat(900, RFL, .85, t, dict(look=(-.8, -.6), smile=1.0, perk=1.0, paw=ease_out(ramp(t, tc - .2, .3)), paw_dx=-90)))
    o.append(PR.sparkles(SINK[0], COUNTER_Y - 160, 2.2, bump(t, tc, .05, .6), t, seed=131, n=8, r=300))
    hud = energy(1.0) if not NOCAM else ""
    hud += quest_win(["ЧИСТАЯ"], pop(t, a - .05, .25), y=520, w=640, head="КРУЖКА", col="#2f9f55", size=90)
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tc, 8)
    return gview(o, 560, 900, 1.08 + .05 * uu, t, hud, dx, dy)


def comment_box(t, a, num_u=0.0):
    """Поле комментария со шкалой от 1 до 10 (числа из фразы призыва)."""
    o = (f'<rect x="-460" y="-210" width="920" height="420" rx="40" fill="#ffffff" stroke="#111" stroke-width="7"/>'
         + '<path d="M-260 206 l-40 90 l120 -90 z" fill="#ffffff" stroke="#111" stroke-width="7" stroke-linejoin="round"/>'
         + '<rect x="-456" y="160" width="912" height="40" fill="#ffffff"/>'
         + plain("комментарий", -400, -140, 40, fill="#9aa0aa"))
    for i in range(10):
        u = clamp((num_u * 12) - i)
        if u <= 0:
            continue
        x_ = -405 + 90 * i
        col = lib.mix("#46d36b", "#e2453a", i / 9)
        o += (f'<g transform="translate({x_} 20) scale({lib.back_out(u, 2.2) if u < 1 else 1.0:.3f})">'
              f'<rect x="-40" y="-60" width="80" height="120" rx="18" fill="{col}" stroke="#111" stroke-width="5"/>'
              + text(str(i + 1), 0, 22, 56 if i < 9 else 46, fill="#ffffff", stroke="#111", sw=5) + "</g>")
    return o


def frame_s14(t):
    """ПРИЗЫВ «Напиши в комментах»: поле комментария с первого кадра, шкала 1…10 уже стоит; кот запрыгивает к Диме."""
    a, b = T0("s14"), T1("s14")
    o = [paper_bg()]
    o.append(tf(comment_box(t, a, 1.0), 540, 640, 1.0, -1.5))
    o.append(PR.glow(540, 700, 460, .4, "#ffe9a8"))
    k = .62
    hip = 1640 - (people.LEG_LEN - 12) * k - 6
    f = people.dima82(330, hip, k, "proud82", "d82_one", t=t, feet="stand", head_add=.05 * math.sin(t * 3))
    o.append(f["svg"])
    j = ease_io(ramp(t, a + .1, .4))
    o.append(cat(1180 + (640 - 1180) * j, 1640 - 260 * math.sin(math.pi * j), .9, t,
                 dict(look=(-.7, -.4), legs=1.0 - j if j < 1 else 0.0, smile=1.0 if j >= 1 else .4)))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, a + .05, 8)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .06 * uu, 0, bg=PAPER, t=t)


def dish_pile(x, y, k, t, hp=1.0):
    o = ""
    for i in range(5):
        o += shape(ellipse_pts(0, -30 - 34 * i, 150 - 10 * i, 26, 20), ["#f4f6f8", "#e8ecf0"][i % 2], "", w=4, seed=190 + i)
    o += PR.mug(-90, -200, 1.4, col="red", coffee=False) + PR.mug(80, -190, 1.3, col="blue", coffee=False)
    for s_ in (-1, 1):
        o += shape(ellipse_pts(s_ * 40, -130, 18, 20, 10), "#ffffff", blob(ellipse_pts(s_ * 40 + 4, -126, 8, 10, 8), "#111"), w=3, seed=196 + s_)
        o += line([(s_ * 16, -156), (s_ * 64, -170)], 5, "#111", seed=198 + s_)
    return tf(o, x, y, k)


def frame_s15(t):
    """«какой уровень сложности у твоей посуды»: гора посуды с глазами — босс; окно «УРОВЕНЬ СЛОЖНОСТИ», шкала 1…10 рядом."""
    a, b = T0("s15"), T1("s15")
    o = kitchen(t)
    o.append(dish_pile(SINK[0] - 80, COUNTER_Y + 20, 2.2, t))
    o.append(cat(930, RFL, .8, t, dict(look=(-.8, -.6), smug=.6, perk=1.0)))
    hud = quest_win(["СЛОЖНОСТИ"], pop(t, a - .05, .3), y=300, w=760, head="УРОВЕНЬ", col="#7a3fd0")
    hud += tf(comment_box(t, a, 1.0), 540, 680, .72, 0)
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(54), 8)
    return gview(o, 560, 900, 1.05 + .05 * uu, t, hud, dx, dy)


def frame_s16(t):
    """«от одного до десяти»: шкала крупно, на «одного» загорается 1, на «десяти» — 10; кот лапой показывает на шкалу."""
    a, b = T0("s16"), T1("s16")
    o = [paper_bg()]
    box = comment_box(t, a, 1.0)
    box += f'<g opacity="{.9 * bump(t, W(56), .05, .5):.2f}"><rect x="-450" y="-45" width="90" height="130" rx="20" fill="none" stroke="#FFD23F" stroke-width="10"/></g>'
    box += f'<g opacity="{.9 * min(1.0, bump(t, W(58), .05, 1.5) * 1.3):.2f}"><rect x="365" y="-45" width="90" height="130" rx="20" fill="none" stroke="#FFD23F" stroke-width="10"/></g>'
    o.append(tf(box, 540, 820, 1.05))
    o.append(cat(780, 1640, 1.0, t, dict(look=(-.5, -.8), smile=1.0, perk=1.0, paw=.8, paw_dx=60)))
    o.append(PR.sparkles(540, 820, 2.0, bump(t, W(58), .05, .5), t, seed=161, n=6, r=420))
    uu = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(58), 7)
    return view("".join(o), 540 + dx, 1020 + dy, 1.0 + .05 * uu, 0, bg=PAPER, t=t)


def frame_s17(t):
    """Петля: кадр хука — кухня-уровень, кружка-босс, Дима с губкой, кот."""
    a, b = T0("s17"), T1("s17")
    o = kitchen(t)
    o.append(tap(SINK[0] + 120, COUNTER_Y, 1.0))
    o.append(boss_mug(SINK[0] + 80, COUNTER_Y + 10, 8.2, t, hp=1.0))
    f = dima_at(t, 170, "wow82", "d82_hold")
    o.append(f["svg"])
    o.append(cat(980, RFL, .7, t, dict(look=(-.8, -.6), perk=1.0)))
    return loop_view("".join(o), t, a, b, HIT, 560, 940, .98)


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
