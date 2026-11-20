"""Призыв в Телеграм «ноутбук» для рилсов-историй формата 4 (2D кодом), эксперимент владельца 20.11: та же хореография,
что у 3D-призыва рилса 98, но в нашей рисованной линии.

Ноутбук на столе открывается, экран вспыхивает: интерфейс канала «СДВГ | Напарник» (аватар, t.me/ru_adhd, посты
листаются, золотые искры, красные следы лап к кнопке). Кнопка «ПОДПИСАТЬСЯ» выпрыгивает из экрана (растёт, тень,
наклон), кот рилсов привстаёт и жмёт её лапой, кнопка проседает, зеленеет «✓ ВЫ ПОДПИСАНЫ», шлёпается обратно в экран;
искры, аватар подпрыгивает и подмигивает, красные следы выходят из экрана на стол к коту.

Время — параметрами: t0 (крышка начинает открываться) и press (лапа жмёт, ≥ t0 + 1.6).
    import story_cta_laptop as lp; svg = lp.frame(t, t0=W["подпишись"], press=W["Телеграм"])
Демо: python3 scripts/story_cta_laptop.py [out.mp4] [--sheet sheet.jpg]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import story_cta_tg as tg  # noqa: E402

_cl, _back, _eio, _expo, _sc, _text, _mixc = tg._cl, tg._back, tg._eio, tg._expo, tg._sc, tg._text, tg._mixc

# раскладка (мир 1080×1920; всё главное выше 1300 — ниже субтитры)
HINGE = 1250                       # шарнир крышки на столе
LX0, LX1, LTOP = 150, 1030, 640     # крышка
SX0, SX1, SY0, SY1 = 175, 1005, 665, 1225   # экран
AVC, AVR = (800, 815), 96           # аватар (правая колонка)
NAME_Y, LINK_Y = 960, 1010
BTN = (625, 1075, 975, 1165)        # кнопка
BTN_C = ((BTN[0] + BTN[2]) / 2, (BTN[1] + BTN[3]) / 2)
TOUCH = (668, 1140)                 # куда приходит подушечка
POSTS = ["Это не лень", "Дофаминовое меню", "Гений в 3 ночи", "Слепота ко времени", "Посиди со мной", "Гиперфокус"]
GREEN, GREEN_SH = "#4fae4e", "#3a8f3a"
SCREEN_BG, BAR = "#0e1621", "#17212b"
CAT_X = 330
_ST = {}


def _setup(lib, cat):
    """Кот левее ноутбука, подушечка — в кнопку (переиспользуем позу и лапу story_cta_tg)."""
    if "ok" in _ST:
        return
    tg.CAT_X = CAT_X
    yr = tg.CAT_Y - 64 * tg.RISE * tg.CAT_K
    tg.PAW_TIP = ((TOUCH[0] - CAT_X) / tg.CAT_K + cat.CX, (TOUCH[1] - yr) / tg.CAT_K + cat.CBOT)
    tg.ELBOW = (cat.CX + 25 + tg.PAW_DX * tg.PAW_PW * 1.6, 1306 - 150 * tg.PAW_PW)
    _ST["ok"] = True


def _rr(lib, x0, y0, x1, y1, r, fill, sd, w=4.4, inner=""):
    return lib.shape(lib.rrect(x0, y0, x1, y1, r), fill, inner, w=w, seed=sd)


def laptop_base(lib):
    o = [lib.blob(lib.rect_pts(LX0 - 40, HINGE + 30, LX1 + 50, HINGE + 92, 30), "#5a3418", .35, lib.blur(14))]
    base = [(LX0 - 10, HINGE, 1), (LX1 + 10, HINGE, 1), (LX1 + 60, HINGE + 62, 1), (LX0 - 60, HINGE + 62, 1)]
    inner = lib.blob([(LX0 - 60, HINGE + 44), (LX1 + 60, HINGE + 44), (LX1 + 60, HINGE + 62), (LX0 - 60, HINGE + 62)], "#8b9097")
    for k in range(3):
        y = HINGE + 12 + k * 11
        inner += lib.line([(LX0 + 40 - k * 12, y), (LX1 - 40 + k * 12, y)], 2.2, "#7b8088", seed=800 + k, op=.7)
    inner += lib.blob(lib.rect_pts(530, HINGE + 47, 650, HINGE + 58, 4), "#7b8088")
    o.append(lib.shape(base, "#b6bcc4", inner, w=4.6, seed=805))
    return "".join(o)


def screen_ui(lib, t, st):
    """Интерфейс канала в координатах мира (внутри экрана)."""
    o = [f'<rect x="{SX0}" y="{SY0}" width="{SX1 - SX0}" height="{SY1 - SY0}" fill="{SCREEN_BG}"/>',
         f'<rect x="{SX0}" y="{SY0}" width="{SX1 - SX0}" height="40" fill="{BAR}"/>',
         _text(SX0 + 26, SY0 + 29, "Telegram", 24, "#6c7883", anchor="start")]
    # левая колонка: посты листаются
    cid = _ST.setdefault("pclip", lib.clip_of(lib.rect_pts(SX0, SY0 + 40, 600, SY1)))
    p = []
    for i in range(8):
        y = SY0 + 60 + i * 150 - st["scroll"]
        p.append(f'<rect x="{SX0 + 18}" y="{y:.1f}" width="390" height="130" rx="18" fill="#182533"/>')
        p.append(f'<circle cx="{SX0 + 52}" cy="{y + 36:.1f}" r="20" fill="#f4f1ea"/>')
        p.append(f'<image href="{tg._avatar_uri()}" x="{SX0 + 32}" y="{y + 16:.1f}" width="40" height="40" clip-path="circle(20px at 20px 20px)"/>')
        p.append(_text(SX0 + 84, y + 46, POSTS[i % len(POSTS)], 27, "#ffffff", anchor="start"))
        for k in range(2):
            p.append(f'<rect x="{SX0 + 34}" y="{y + 74 + k * 24:.1f}" width="{330 - k * 110}" height="11" rx="5" fill="#3a4b5c"/>')
    o.append(f'<g clip-path="url(#{cid})">{"".join(p)}</g>')
    # правая колонка: аватар (живой после нажатия), имя, ссылка
    al = st["alive"]
    hop = abs(math.sin(al * math.pi * 3)) * (1 - al) if 0 < al < 1 else 0.0
    ax, ay = AVC[0], AVC[1] - hop * 30
    sx, sy = 1 + hop * .06, 1 - hop * .06
    av = (f'<circle cx="0" cy="0" r="{AVR + 7}" fill="#2ea6ff"/><circle cx="0" cy="0" r="{AVR}" fill="#f4f1ea"/>'
          f'<image href="{tg._avatar_uri()}" x="{-AVR}" y="{-AVR}" width="{2 * AVR}" height="{2 * AVR}" '
          f'clip-path="circle({AVR}px at {AVR}px {AVR}px)"/>')
    if 0.08 < al < 0.75:   # подмигивает правым глазом
        ex, ey, er = AVR * .4 * .5 * 2 * (360 / 600 - .5) * 2.5, 0, AVR * .16
        av += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{er:.1f}" fill="#2f2d33"/>'
        av += f'<path d="M{ex - er:.1f} {ey + 3:.1f} Q{ex:.1f} {ey - er:.1f} {ex + er:.1f} {ey + 3:.1f}" stroke="#141216" stroke-width="5" fill="none" stroke-linecap="round"/>'
    if 0 < al < 1:          # машет лапкой
        rot = -35 + 35 * math.sin(al * 20)
        av += (f'<g transform="translate({-AVR * .62:.1f} {AVR * .3:.1f}) rotate({rot:.1f})"><ellipse cx="0" cy="-24" rx="13" ry="24" fill="#2f2d33"/>'
               f'<circle cx="0" cy="-41" r="6" fill="#e8875a"/></g>')
    o.append(f'<g transform="translate({ax:.1f} {ay:.1f}) scale({sx:.3f} {sy:.3f})">{av}</g>')
    for k, (x, y, ph) in enumerate([(680, 740, 0), (930, 735, 1.7), (945, 880, 3.1), (665, 885, 4.4), (805, 690, 2.4)]):
        w = t * 5 + ph
        o.append(_sc(tg.star4(lib, x, y, 16, 0, 830 + k), x, y, 0.7 + 0.35 * math.sin(w), 0, 0.5 + 0.5 * math.sin(w)))
    o.append(_text(800, NAME_Y, "СДВГ | Напарник", 44, "#ffffff"))
    o.append(_text(800, LINK_Y, "t.me/ru_adhd", 36, "#5eb5f7"))
    # красные следы лап к кнопке (по постам)
    trail = [(560, 1205, -1.9), (500, 1180, -1.6), (560, 1150, -1.7), (600, 1125, -1.5)]
    for k, (x, y, r) in enumerate(trail):
        a = _cl(st["paws"] * len(trail) - k)
        if a > 0:
            o.append(_sc(tg.paw_print(lib, x, y, 0.75, math.degrees(r) + 90, col=tg.RED), x, y, a))
    # место кнопки на экране (когда кнопка «выпрыгнула» — тёмная выемка)
    if st["pop"] > 0.02:
        o.append(f'<rect x="{BTN[0]}" y="{BTN[1]}" width="{BTN[2] - BTN[0]}" height="{BTN[3] - BTN[1]}" rx="28" fill="#000" opacity=".35"/>')
    else:
        o.append(button_svg(lib, st["sub"], 0))
    return "".join(o)


def button_svg(lib, sub, dn):
    x0, y0, x1, y1 = BTN
    col, sh = (GREEN, GREEN_SH) if sub else (tg.TG_BLUE, tg.TG_BLUE_SH)
    o = [f'<rect x="{x0}" y="{y0 + 8 + dn:.1f}" width="{x1 - x0}" height="{y1 - y0}" rx="30" fill="{sh}"/>',
         f'<rect x="{x0}" y="{y0 + dn:.1f}" width="{x1 - x0}" height="{y1 - y0}" rx="30" fill="{col}" stroke="{lib.INK}" stroke-width="4"/>',
         f'<rect x="{x0 + 14}" y="{y0 + 8 + dn:.1f}" width="{x1 - x0 - 28}" height="30" rx="15" fill="#ffffff" opacity=".22"/>']
    o.append(_text(BTN_C[0], BTN_C[1] + 15 + dn, "✓ ВЫ ПОДПИСАНЫ" if sub else "ПОДПИСАТЬСЯ", 40 if sub else 44, "#ffffff"))
    return "".join(o)


def lid(lib, t, t0, st):
    """Крышка: открывается от шарнира (сжатие по высоте с перелётом), экран вспыхивает."""
    u = 0.04 + 0.96 * _back((t - t0) / 0.5, 1.7)
    on = _eio((t - t0 - 0.35) / 0.25)
    o = [_rr(lib, LX0, LTOP, LX1, HINGE, 34, "#2b2d31", 806, w=5)]
    o.append(f'<circle cx="{(LX0 + LX1) / 2}" cy="{LTOP + 12}" r="4" fill="#555"/>')
    o.append(f'<rect x="{SX0}" y="{SY0}" width="{SX1 - SX0}" height="{SY1 - SY0}" fill="#101418"/>')
    if on > 0:
        o.append(f'<g opacity="{on:.3f}">{screen_ui(lib, t, st)}</g>')
        flash = _cl(1 - (t - t0 - 0.45) / 0.25) * on
        if flash > 0:
            o.append(f'<rect x="{SX0}" y="{SY0}" width="{SX1 - SX0}" height="{SY1 - SY0}" fill="#ffffff" opacity="{flash * .7:.3f}"/>')
        o.append(f'<rect x="{SX0}" y="{SY0}" width="{(SX1 - SX0) * .45:.0f}" height="{SY1 - SY0}" fill="#ffffff" opacity=".05"/>')
    return f'<g transform="translate(0 {HINGE}) scale(1 {u:.4f}) translate(0 {-HINGE})">{"".join(o)}</g>', on


def popped_button(lib, t, press, sub):
    """Кнопка выпрыгивает из экрана к зрителю: растёт, отбрасывает тень, качается; тап — проседает; потом шлёпается обратно."""
    a = press - 0.95
    pop = _eio((t - a) / 0.32) * (1 - _eio((t - press - 0.55) / 0.22))
    if pop <= 0.02:
        return "", 0.0
    e = t - press
    tap = math.exp(-((e - 0.04) / 0.07) ** 2) if e > -0.2 else 0.0
    wob = math.sin((t - a) * 17) * math.exp(-(t - a) * 4) if t > a else 0.0
    s = 1 + 0.32 * pop - 0.09 * tap + 0.04 * wob
    lift = 40 * pop * (1 - 0.6 * tap)
    rot = -4 * pop + 3 * wob
    cx, cy = BTN_C
    sh = f'<rect x="{BTN[0] + 10}" y="{BTN[1] + 18 + lift * .9:.1f}" width="{BTN[2] - BTN[0]}" height="{BTN[3] - BTN[1]}" rx="30" fill="#000" opacity="{.38 * pop:.3f}" {lib.blur(10 + 10 * pop)}/>'
    body = button_svg(lib, sub, 0)
    g = sh + f'<g transform="translate(0 {-lift:.1f})">{_sc(body, cx, cy, s, rot)}</g>'
    return g, pop


def burst(lib, t, press):
    e = t - press - 0.04
    if not 0 <= e < 1.0:
        return ""
    o = []
    for k in range(16):
        an = k / 16 * 2 * math.pi + (k % 3) * .2
        d = 30 + e * (260 + (k % 4) * 60)
        x, y = TOUCH[0] + math.cos(an) * d, TOUCH[1] - 40 + math.sin(an) * d * .8 - e * e * 120
        r = 26 * (1 - e * .5) * (0.7 + (k % 3) * .2)
        o.append(f'<g opacity="{1 - e:.3f}">{tg.star4(lib, x, y, r, 0, 860 + k)}</g>')
    return "".join(o)


def table_paws(lib, t, press):
    pts = [(520, 1300, -150), (440, 1318, -160), (360, 1300, -165), (285, 1320, -170)]
    o = []
    for k, (x, y, r) in enumerate(pts):
        a = _back((t - press - 0.3 - k * 0.14) / 0.25, 2.0) if t > press + 0.3 + k * 0.14 else 0.0
        if a > 0:
            o.append(_sc(tg.paw_print(lib, x, y, 0.8, r, col=tg.RED), x, y, a))
    return "".join(o)


def layer(t, t0=0.1, press=2.0, common=None):
    lib, cat = tg._mods(common)
    _setup(lib, cat)
    tg.prepare(common)
    X, Y, cst, touch = tg.cat_state(lib, cat, t, t0, press)
    sub = t >= press + 0.06
    pop_svg, pop = popped_button(lib, t, press, sub)
    st = dict(scroll=max(0.0, t - t0 - 0.5) * 45, paws=_cl((t - t0 - 0.8) / 0.8), alive=(t - press) / 1.1, sub=sub, pop=pop)
    out = [tg.steam(lib, t), laptop_base(lib)]
    lid_svg, on = lid(lib, t, t0, st)
    out.append(lid_svg)
    gl = lib.rad_grad([(0, "#9fd0ff", .22 * on), (1, "#9fd0ff", 0)], 590, 950, 700, 500)
    out.append(f'<rect x="-100" y="400" width="1300" height="1100" fill="url(#{gl})" style="mix-blend-mode:screen"/>')
    out.append(table_paws(lib, t, press))
    arm = cst.pop("_arm")
    out.append(cat.draw(X, Y, tg.CAT_K, cst, t))
    out.append(pop_svg)
    out.append(tg.forearm(lib, cat, X, tg.CAT_K, *arm))
    out.append(burst(lib, t, press))
    pin = _eio((t - t0 - 0.2) / 1.2)
    pout = _eio((t - press - 0.5) / 1.0)
    s = 1.12 + 0.06 * pin - 0.04 * pout
    s *= 1 + 0.03 * math.exp(-((t - press - 0.06) / 0.12) ** 2)
    return "".join(out), (585 + 4 * math.sin(t * .7), 1060 - 15 * pin + 10 * pout, s, 0.3 * math.sin(t * .8))


def frame(t, t0=0.1, press=2.0, common=None):
    lib, cat = tg._mods(common)
    if "bg" not in _ST:
        _ST["bg"] = tg.background(lib)
        tg.prepare(common)
        lib.static_done()
    lib.dyn_begin()
    body, (ccx, ccy, s, rot) = layer(t, t0, press, common)
    return lib.svg(f'<rect width="{lib.W}" height="{lib.H}" fill="#6e4a32"/><g transform="{lib.cam(ccx, ccy, s, rot)}">{_ST["bg"]}{body}</g>')


def _job(a):
    t, path, t0, press, common = a
    tg._mods(common)
    open(path, "w").write(frame(t, t0, press, common))
    return path


if __name__ == "__main__":
    import shutil
    import subprocess
    import tempfile
    from multiprocessing import Pool
    args = sys.argv[1:]
    sheet = args[args.index("--sheet") + 1] if "--sheet" in args else None
    only = [float(x) for x in args[args.index("--frames") + 1].split(",")] if "--frames" in args else None
    pos = [a for a in args if a.endswith(".mp4")]
    common = tg.DEFAULT_COMMON
    tmp = tempfile.mkdtemp(prefix="lpcta_")
    try:
        ts = only or [k / 30 for k in range(int(4.2 * 30))]
        jobs = [(t, os.path.join(tmp, f"f{k:04d}.svg"), 0.1, 2.0, common) for k, t in enumerate(ts)]
        with Pool(4) as p:
            svgs = p.map(_job, jobs, chunksize=4)
        rjs = os.path.join(common, "render.js")
        if only:
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(f"{x}\t{x[:-4]}.png" for x in svgs))
            subprocess.check_call(["node", rjs, os.path.join(tmp, "list.txt"), "png", "2"])
            pngs = sorted(x for x in os.listdir(tmp) if x.endswith(".png"))
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error"] + sum([["-i", os.path.join(tmp, x)] for x in pngs], []) +
                                  ["-filter_complex", f"hstack={len(pngs)},scale={270 * len(pngs)}:-1", sheet or "lp_sheet.jpg"])
            print(sheet)
        else:
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(svgs))
            subprocess.check_call(["node", rjs, os.path.join(tmp, "list.txt"), "mp4", "4", os.path.join(tmp, "seg")])
            segs = sorted(x for x in os.listdir(tmp) if x.startswith("seg_") and x.endswith(".mp4"))
            open(os.path.join(tmp, "concat.txt"), "w").write("".join(f"file '{os.path.join(tmp, s)}'\n" for s in segs))
            out = pos[0] if pos else os.path.join(tg.REPO, "assets", "story_cta", "demo_laptop.mp4")
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "concat.txt"),
                                   "-c", "copy", "-movflags", "+faststart", out])
            if sheet:
                subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-vf", "fps=6,scale=216:-1,tile=9x3", "-frames:v", "1", sheet])
            print(out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
