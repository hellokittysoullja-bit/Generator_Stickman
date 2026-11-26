"""Рилс 116 «Вкладки», все планы (одна группа ext_a). frame(sid, t) -> SVG 1080×1920, t — время ролика.
Время — только из shots.json и voice/words.json. Говорит Дима от первого лица. Места: браузер крупно (вкладки), стол
с монитором, бумажка «ПОТОМ». NOCAM=1 — без влёта, тряски и надписей."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
from h4 import *  # noqa: E402,F401,F403
from h4 import PR, CT, lib, people  # noqa: E402

HIT = stress(1, .3)
TAB_COLS = ["#e2453a", "#3fb26a", "#FFD23F", "#9a6fd1", "#2f8fe0", "#ff8a1f", "#d26fa8", "#5a5f6e"]
SKIN = "#ecc4a2"


def browser(n, w=900.0, h=1000.0, progress=None, page="doc", title="Отчёт", plus_x=False, active=0):
    """Окно браузера (центр 0,0): n вкладок в полосе сверху, страница — документ."""
    o = [blob(lib.rect_pts(-w / 2 + 14, -h / 2 + 18, w / 2 + 14, h / 2 + 18), "#000000", .18)]
    inner = rect(-w / 2, -h / 2, w / 2, -h / 2 + 140, "#dfe3ea")
    n = max(1, n)
    tw = min(260.0, (w - 120) / n)
    for j in range(n):
        x0 = -w / 2 + 20 + tw * j
        on = j == active
        inner += shape(lib.rrect(x0, -h / 2 + 30, x0 + tw - 4, -h / 2 + 90, min(14, tw / 3)), "#ffffff" if on else "#eef0f4", "", w=2.6,
                       seed=2300 + j % 40)
        inner += blob(ellipse_pts(x0 + min(26, tw * .4), -h / 2 + 60, min(11, tw * .25), min(11, tw * .25), 10), TAB_COLS[j % 8])
        if tw > 120:
            inner += plain(title if j == 0 else ["Видео", "Магазин", "Новости", "Мемы"][j % 4], x0 + 48, -h / 2 + 74, 34, fill="#1d2448")
    px = -w / 2 + 20 + tw * n + 24
    inner += text("+", min(px, w / 2 - 40), -h / 2 + 80, 60, fill="#5a5f6e", stroke="#5a5f6e", sw=.01)
    if plus_x:
        inner += PR.cross_stroke((px - 30, -h / 2 + 30), (px + 30, -h / 2 + 90), (px + 30, -h / 2 + 30), (px - 30, -h / 2 + 90), u=1.0, w=14, seed=2)
    inner += rect(-w / 2, -h / 2 + 100, w / 2, -h / 2 + 140, "#ffffff")
    inner += shape(lib.rrect(-w / 2 + 30, -h / 2 + 104, w / 2 - 30, -h / 2 + 136, 16), "#eef0f4", "", w=2, seed=2350)
    if page == "doc":
        inner += plain(title, -w / 2 + 80, -h / 2 + 240, 64, fill="#1d2448")
        for j in range(8):
            inner += line([(-w / 2 + 80, -h / 2 + 320 + 70 * j), (w / 2 - 100 - 80 * (j % 3), -h / 2 + 320 + 70 * j)], 6, "#c9cdd5", taper=.1,
                          wmin=.8, seed=2360 + j)
        if progress is not None:
            inner += shape(lib.rrect(-w / 2 + 80, h / 2 - 140, w / 2 - 80, h / 2 - 90, 25), "#eef0f4", "", w=3, seed=2370)
            inner += rect(-w / 2 + 86, h / 2 - 134, -w / 2 + 86 + (w - 172) * progress, h / 2 - 96, "#3fb26a")
            inner += text(f"{int(round(progress * 100))}%", 0, h / 2 - 160, 60, fill="#1d2448", stroke="#ffffff", sw=6)
    o.append(shape(lib.rrect(-w / 2, -h / 2, w / 2, h / 2, 26), "#ffffff", inner, w=5, seed=2380))
    return "".join(o)


def tab_badge(x, y, n, k=1.0):
    return tf(shape(lib.rrect(-90, -70, 90, 70, 30), "#e2453a", "", w=5, seed=2390) + text(str(n), 0, 30, 90, fill="#ffffff", stroke="#7a1e18", sw=6),
              x, y, k)


def frame_s01(t):
    """ХУК: браузер крупно, вкладки размножаются до 40, счётчик вкладок прыгает."""
    n = 1 + int(39 * clamp((t + .1) / .85) ** 1.5)
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552"), PR.glow(540, 900, 800, .3, "#8fb7ff")]
    o.append(tf(browser(n, h=840), 540, 1030, 1.05, -1.5))
    o.append(tab_badge(900, 620, n, 1.0 + .15 * math.sin(t * 30)))
    dx, dy = shake(t, HIT, 10)
    return hook_view("".join(o), t, HIT, 540, 960, 1.0, 0, bg="#3b3552", dx=dx, dy=dy)


def monitor(x, y, k, inner):
    """Монитор на столе: (x, y) — низ подставки."""
    o = shape(lib.rect_pts(-30, -120, 30, 0), "#5a5f6e", "", w=4, seed=2400)
    o += shape(lib.rrect(-120, -20, 120, 6, 6), "#5a5f6e", "", w=4, seed=2401)
    o += shape(lib.rrect(-330, -560, 330, -120, 20), "#2a2d36", "", w=5, seed=2402)
    o += tf(inner, 0, -340, .66)
    return tf(o, x, y, k)


def desk_scene(t, mode="day", sun=0.0):
    o = desk_room(t, mode=mode, sun=sun)
    return o


def frame_s02(t):
    """«работаю два часа подряд без вкладок»: вкладки схлопываются в одну, Дима спокойно печатает, часы «2 ЧАСА» над ним; кот на столе."""
    a, b = T0("s02"), T1("s02")
    tc = W(3)
    n = 40 if t < tc - .3 else max(1, int(40 * (1 - clamp((t - tc + .3) / .35))))
    o = desk_scene(t, sun=1.0)
    o.append(monitor(700, DESK_Y - 8, .9, browser(n, w=900, h=640)))
    tap = math.sin(t * 30)
    f = dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(.9, -.1)), lean=.18,
                  arms={"f": ("ik", (560 + 10 * tap, DESK_Y - 30), 1), "n": ("ik", (640 - 10 * tap, DESK_Y - 25), 1)})
    o.append(f["svg"])
    o.append(shape(lib.rrect(520, DESK_Y - 30, 760, DESK_Y - 6, 8), "#c9cdd5", "", w=3, seed=2410))
    o.append(cat(960, DESK_Y - 4, .5, t, dict(look=(-.8, -.3), smile=.8, tail=10 * math.sin(t * 3))))
    if t > W(5) - .1:
        o.append(tf(PR.clock(0, 0, 70, *PR.clock_hm(2 + 2 * ramp(t, W(5) - .1, .6), 0), seed=1)
                    + text("2 ЧАСА", 0, 140, 60, fill="#ffffff", stroke="#111", sw=8), 430, 560, pop(t, W(5) - .1, .25)))
    o.append(PR.sparkles(700, 700, 1.8, bump(t, tc + .1, .05, .5), t, seed=21, n=6, r=260))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tc + .05, 8)
    return view("".join(o), 600 + dx, 800 + dy, 1.35 + .06 * u, -1 + 2 * u, t=t)


def cursor(x, y, k=1.0):
    pts = [(0, 0, 1), (0, 70, 1), (18, 54, 1), (32, 84, 1), (44, 78, 1), (30, 50, 1), (54, 50, 1)]
    return tf(shape(pts, "#ffffff", "", w=4, seed=2420), x, y, k)


def frame_s03(t):
    """«открывал одну вкладку по делу»: браузер с одной вкладкой «Отчёт», курсор кликает по ней, страница документа открывается."""
    a, b = T0("s03"), T1("s03")
    tcl = W(12)
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552")]
    o.append(tf(browser(1, page="doc" if t > tcl else "blank"), 540, 920, 1.0))
    mv = ease_out(ramp(t, a, tcl - a))
    cx, cy = 900 + (260 - 900) * mv, 1300 + (470 - 1300) * mv
    o.append(cursor(cx, cy, 1.4 * (1 - .15 * bump(t, tcl, .04, .15))))
    o.append(PR.sparkles(260, 470, 1.2, bump(t, tcl, .05, .4), t, seed=31, n=5, r=90))
    k = .5
    f = people.dima82(160, 1720 - (people.LEG_LEN - 12) * k - 6, k, "calm82", "d82_one", t=t, feet="stand")
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 980, 1.0 + .05 * u, 0, bg="#3b3552", t=t)


def frame_s04(t):
    """«через минуту было сорок»: вкладки взрываются до 40 на «сорок», счётчик прыгает, Дима в панике сбоку."""
    a, b = T0("s04"), T1("s04")
    n = 1 + int(39 * clamp((t - a) / (W(18) - a)) ** 1.2)
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552"), PR.glow(540, 900, 800, .3 + .3 * bump(t, W(18), .05, .4), "#ff8a7a")]
    o.append(tf(browser(n, active=n - 1, h=840), 540, 1000, 1.0, 2 * math.sin(t * 20) * bump(t, W(18), .05, .4)))
    o.append(tab_badge(900, 590, n, 1.0 + .3 * bump(t, W(18), .04, .25)))
    k = .5
    f = people.dima82(160, 1720 - (people.LEG_LEN - 12) * k - 6, k, "panic82", "d82_shrug", t=t, feet="stand")
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(18), 12)
    return view("".join(o), 540 + dx, 980 + dy, 1.0 + .06 * u, 0, bg="#3b3552", t=t)


def frame_s05(t):
    """«а к вечеру работа не сдвинулась»: вечер в окне, на мониторе документ «0%», Дима уронил голову на руки."""
    a, b = T0("s05"), T1("s05")
    o = desk_scene(t, mode="evening")
    o.append(monitor(700, DESK_Y - 8, .9, browser(40, w=900, h=640, progress=0.0)))
    o.append(shape(lib.rrect(520, DESK_Y - 30, 760, DESK_Y - 6, 8), "#c9cdd5", "", w=3, seed=2410))
    f = dima_desk(t, dict(people.EXPR["dima"]["zombie"], look=(.6, .6)), head_add=.25, lean=.3)
    o.append(f["svg"])
    o.append(PR.gloom(f["head"][0], f["head"][1] - 160, 1.2, t, ramp(t, a, .4), seed=3))
    o.append(rect(-1400, -1400, 2600, 2900, "#3b2a4a", .25))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(24), 6)
    return view("".join(o), 580 + dx, 820 + dy, 1.4 + .08 * u, 0, t=t)


def frame_s06(t):
    """«Вот что я поменял»: Дима за столом поднимает голову, над ним лампочка; надпись сверху."""
    a, b = T0("s06"), T1("s06")
    ti = W(25) + .15
    o = desk_scene(t)
    o.append(monitor(700, DESK_Y - 8, .9, browser(1, w=900, h=640)))
    f = dima_desk(t, "wow82" if t > ti else "sure82", head_add=.05 * bump(t, ti, .08, .3), lean=0.0)
    o.append(f["svg"])
    hx, hy = f["head"]
    if t > ti:
        o.append(PR.glow(hx + 150, hy - 190, 220, .7, "#fff1b0"))
        o.append(PR.idea_bulb(hx + 150, hy - 190 + 8 * math.sin(t * 5), 1.1 * pop(t, ti, .25), on=1.0, t=t))
        o.append(PR.sparkles(hx + 150, hy - 190, 1.8, bump(t, ti, .05, .5), t, seed=61, n=5, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ti, 9)
    return view("".join(o), 580 + dx, 820 + dy, 1.4 + .06 * u, -1 + 2 * u, t=t)


def icon_bubble(kind, x, y, k, u):
    """Желание «глянуть потом»: видео (play), магазин (корзина), новости (газета)."""
    if u <= 0:
        return ""
    inner = ""
    if kind == "video":
        inner = shape([(-20, -30, 1), (34, 0, 1), (-20, 30, 1)], "#e2453a", "", w=3, seed=2430)
    elif kind == "shop":
        inner = shape([(-40, -20, 1), (40, -20, 1), (30, 26, 1), (-30, 26, 1)], "#ff8a1f", "", w=3, seed=2431)
        inner += line([(-50, -36), (-40, -20)], 5, seed=2432)
    else:
        inner = shape(lib.rect_pts(-40, -30, 40, 30), "#ffffff", "".join(line([(-28, -14 + 14 * j), (28, -14 + 14 * j)], 3, "#7d8597", seed=2433 + j)
                                                                          for j in range(3)), w=3, seed=2436)
    return PR.thought_cloud(x, y, k, w=200, h=150, u=u, seed=hash(kind) % 7, inner=inner)


def frame_s07(t):
    """«Всё, что хочу глянуть потом»: из головы Димы по одной выскакивают облачка — видео, магазин, новости."""
    a, b = T0("s07"), T1("s07")
    o = desk_scene(t)
    o.append(monitor(700, DESK_Y - 8, .9, browser(1, w=900, h=640)))
    f = dima_desk(t, dict(people.EXPR["dima"]["calm82"], look=(-.3, -.8)), head_add=-.12, lean=0.0)
    o.append(f["svg"])
    hx, hy = f["head"]
    for j, (kind, dx_, dy_) in enumerate((("video", -60, -250), ("shop", 170, -330), ("news", 400, -260))):
        o.append(icon_bubble(kind, hx + dx_, hy + dy_, 1.1, ramp(t, a + .1 + .3 * j, .25)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, W(32), 6)
    return view("".join(o), 600 + dx, 760 + dy, 1.3 + .06 * u, 0, t=t)


def note(x, y, k, items, rot=-3.0, fold=0.0):
    """Бумажка «ПОТОМ:» со списком; fold — сложена пополам."""
    inner = plain("ПОТОМ:", -150, -120, 56, fill="#e2453a")
    for j, s_ in enumerate(items):
        inner += plain("• " + s_, -150, -40 + 62 * j, 44, fill="#1d2448")
    sy = 1 - .5 * fold
    o = blob(lib.rect_pts(-190 + 10, -200 + 12, 190 + 10, 200 + 12), "#000000", .14)
    o += shape(lib.rect_pts(-190, -200, 190, 200), "#fff6b0", inner if fold < .5 else "", w=4, seed=2440)
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({k:.3f} {k * sy:.3f})">{o}</g>'


def frame_s08(t):
    """«пишу на бумажку»: крупно — рука пишет на жёлтой бумажке «ПОТОМ:» видео, кроссовки, новости."""
    a, b = T0("s08"), T1("s08")
    items = ["видео", "кроссовки", "новости"]
    n = 1 + int(3 * clamp((t - a) / (b - a)))
    o = [rect(-1400, -1400, 2600, 2900, "#c9a477")]
    o.append(note(540, 900, 2.0, items[:min(3, n)]))
    px, py = 540 - 150 * 2 + 340 * 2 * clamp((t - a) / (b - a)) * .7, 900 + (-40 + 62 * min(2, n - 1)) * 2
    o.append(PR.pen(px + 70, py - 70, 2.2, -135))
    o.append(shape(lib.band([(px + 500, py + 500), (px + 120, py + 40)], 150, 110), SKIN, "", w=5, seed=2450))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 920, 1.0 + .06 * u, 0, bg="#c9a477", t=t)


def frame_s09(t):
    """«а вкладку не открываю»: курсор тянется к «+», лапа кота закрывает его, на «не открываю» красный крест."""
    a, b = T0("s09"), T1("s09")
    tx = W(39)
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552")]
    o.append(tf(browser(1, plus_x=t > tx), 540, 920, 1.0))
    px = -450 + 20 + 260 + 24
    mv = ease_out(ramp(t, a, tx - a))
    o.append(cursor(800 + (540 + px - 800) * mv * .9, 1300 + (470 - 1300) * mv * .9, 1.4))
    paw = ease_out(ramp(t, tx - .25, .25))
    o.append(cat(540 + px + 300 - 250 * paw, 640 + 120 * (1 - paw), 1.0, t,
                 dict(look=(-.9, -.4), smile=.8, paw=paw, perk=1.0)))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tx, 10)
    return view("".join(o), 540 + dx, 900 + dy, 1.05 + .05 * u, 0, bg="#3b3552", t=t)


def frame_s10(t):
    return cta_code(t, T0("s10"), T1("s10"))


def frame_s11(t):
    """«чтобы работа двигалась»: документ в одной вкладке, полоса прогресса ползёт 0 → 70%."""
    a, b = T0("s11"), T1("s11")
    p = .7 * ease_out(clamp((t - a + .1) / (b - a)))
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552"), PR.glow(540, 900, 700, .3, "#9fe0a4")]
    o.append(tf(browser(1, progress=p), 540, 920, 1.0))
    o.append(cat(900, 1450, .8, t, dict(look=(-.6, -.6), smile=1.0)))
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 540, 960, 1.0 + .05 * u, 0, bg="#3b3552", t=t)


def frame_s12(t):
    """«а не тонула во вкладках»: море из вкладок, документ тонет; на «вкладках» кот выдёргивает его наверх."""
    a, b = T0("s12"), T1("s12")
    tr = W(51) - .1
    o = [rect(-1400, -1400, 2600, 2900, "#cfe3ea")]
    lvl = 1150
    rise = ease_out(ramp(t, tr, .35))
    doc_y = lvl + 60 * clamp((t - a) / (tr - a)) - 420 * rise
    o.append(tf(shape(lib.rect_pts(-160, -210, 160, 210), "#ffffff", plain("Отчёт", -120, -140, 50, fill="#1d2448")
                      + "".join(line([(-120, -80 + 40 * j), (120 - 30 * (j % 2), -80 + 40 * j)], 5, "#c9cdd5", seed=2460 + j) for j in range(6)),
                      w=4, seed=2465), 540, doc_y, 1.0, -8 + 8 * rise))
    for j in range(46):
        rs = (j * 53 % 23) / 23
        x = -100 + (j % 12) * 110 + 30 * math.sin(t * 2 + j)
        y = lvl - 40 + (j // 12) * 90 + 16 * math.sin(t * 3 + j * 1.3)
        o.append(tf(shape(lib.rrect(-60, -24, 60, 24, 12), "#eef0f4", blob(ellipse_pts(-36, 0, 9, 9, 8), TAB_COLS[j % 8]), w=2.6, seed=2470 + j % 30),
                    x, y, 1.0, 20 * (rs - .5)))
    o.append(cat(700, doc_y - 120, .9, t, dict(look=(-.5, .4), smile=1.0 if rise > .5 else .2, paw=1.0, perk=1.0)))
    o.append(PR.sparkles(540, doc_y - 100, 1.6, bump(t, tr + .35, .05, .5), t, seed=121, n=6, r=200))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, tr + .3, 8)
    return view("".join(o), 540 + dx, 1000 + dy, 1.0 + .06 * u, 0, bg="#cfe3ea", t=t)


def frame_s13(t):
    """«В шесть вечера работа сдана»: часы 18:00 на стене, на мониторе документ 100% и штамп «СДАНО», Дима потягивается; кот на столе."""
    a, b = T0("s13"), T1("s13")
    ts = W(56)
    o = desk_scene(t, mode="evening")
    o.append(PR.clock(330, 520, 90, *PR.clock_hm(6, 0), seed=1))
    inner = browser(1, w=900, h=640, progress=1.0)
    if t > ts:
        s = 1.0 + 1.2 * (1 - ease_out(clamp((t - ts) / .25)))
        inner += (f'<g transform="translate(0 0) rotate(-12) scale({s:.3f})"><rect x="-230" y="-80" width="460" height="160" rx="16" fill="none" '
                  f'stroke="#3fb26a" stroke-width="16"/>' + text("СДАНО", 0, 44, 120, fill="#3fb26a", stroke="#3fb26a", sw=.01) + "</g>")
    o.append(monitor(700, DESK_Y - 8, .9, inner))
    f = dima_desk(t, "laugh82" if t > ts else "proud82", lean=-.05, head_add=-.05)
    o.append(f["svg"])
    o.append(cat(960, DESK_Y - 4, .5, t, dict(look=(-.8, -.4), smile=1.0, tail=10 * math.sin(t * 3))))
    o.append(PR.sparkles(700, 640, 1.8, bump(t, ts + .1, .05, .5), t, seed=131, n=7, r=260))
    u = ease_io(ramp(t, a, b - a))
    dx, dy = shake(t, ts, 9)
    return view("".join(o), 600 + dx, 800 + dy, 1.35 + .06 * u, 0, t=t)


def frame_s14(t):
    """«а бумажку с „потом“ я так и не открыл»: на столе сложенная жёлтая бумажка «ПОТОМ», кот ложится на неё и засыпает."""
    a, b = T0("s14"), T1("s14")
    o = desk_scene(t, mode="evening")
    o.append(monitor(760, DESK_Y - 8, .8, browser(1, w=900, h=640, progress=1.0)))
    o.append(note(520, DESK_Y - 40, .5, ["видео", "кроссовки", "новости"], rot=-6, fold=1.0))
    o.append(plain("ПОТОМ", 450, DESK_Y - 46, 34, fill="#e2453a"))
    lie = ramp(t, W(61), .4)
    if lie < .5:
        o.append(cat(620 - 80 * lie, DESK_Y - 4, .5, t, dict(look=(-.8, .4), smile=.6)))
    else:
        o.append(CT.curl(520, DESK_Y - 30, .5, dict(eye=.0, look=(.6, -.4)), t))
        o.append(PR.zzz(560, DESK_Y - 200, .9, t, 1.0))
    f = dima_desk(t, "proud82", lean=0.0, head_add=-.05, x=300)
    o.append(f["svg"])
    u = ease_io(ramp(t, a, b - a))
    return view("".join(o), 560, 840, 1.5 + .08 * u, 1 - 2 * u, t=t)


def frame_s15(t):
    """Петля: кадр хука — браузер с одной вкладкой, вот-вот начнут множиться."""
    a, b = T0("s15"), T1("s15")
    o = [rect(-1400, -1400, 2600, 2900, "#3b3552"), PR.glow(540, 900, 800, .3, "#8fb7ff")]
    o.append(tf(browser(1, h=840), 540, 1030, 1.05, -1.5))
    o.append(tab_badge(900, 620, 1, 1.0))
    return loop_view("".join(o), t, a, b, HIT, 540, 960, 1.0, bg="#3b3552")


def frame(sid, t):
    lib.DEFS.clear()
    return globals()["frame_" + sid](t)
