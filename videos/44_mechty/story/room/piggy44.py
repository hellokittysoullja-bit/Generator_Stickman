"""Копилка-кот и фон стены/полки рилса 44 — копия отрисовки агента ext_b (ext_b/scene_piggy44.py, calbase.wallpaper),
чтобы s18 совпал с s17: та же копилка (глаза-точки, румянец, прорезь на макушке, наклейка с Фудзи), шалфейные обои,
полка светлого дерева. Переписано на lib.py папки room (те же сигнатуры blob/shape/line)."""
import lib
from lib import DEFS, W, H, blob, blur, ellipse_pts, f, line, rad_grad, rect_pts, shape

CER, CER_SH, CER_HI, CER_DK = "#f3c48e", "#d9965a", "#fff4e2", "#b8743e"
SHELF_Y = 1150


def wallpaper():
    """Стена комнаты Димы: шалфейные обои в узкую полоску с веточкой, тёплый свет лампы сверху-слева."""
    if not any('id="pWall40"' in d for d in DEFS):
        DEFS.append('<pattern id="pWall40" width="96" height="140" patternUnits="userSpaceOnUse">'
                    '<rect width="96" height="140" fill="#b9c7a8"/>'
                    '<rect x="44" width="8" height="140" fill="#aebd9c"/>'
                    '<path d="M20 30 C26 40 26 52 20 62 C14 52 14 40 20 30Z M76 100 C82 110 82 122 76 132 C70 122 70 110 76 100Z" fill="#a3b391"/>'
                    '</pattern>')
    s = [f'<rect x="-2600" y="-2600" width="{W + 5200}" height="{H + 5200}" fill="url(#pWall40)"/>']
    g = rad_grad([(0, "#ffe2a8", .5), (.55, "#ffd08a", .14), (1, "#ffd08a", 0)], 300, 300, 1200, 1200)
    s.append(f'<rect x="-2600" y="-2600" width="{W + 5200}" height="{H + 5200}" fill="url(#{g})" style="mix-blend-mode:screen"/>')
    g2 = rad_grad([(0, "#000", 0), (.5, "#000", 0), (1, "#14200f", .5)], 540, 860, 1300, 1550)
    s.append(f'<rect x="-2600" y="-2600" width="{W + 5200}" height="{H + 5200}" fill="url(#{g2})"/>')
    return "".join(s)


def piggy(sticker=0.0, slot_glow=0.0, sd=7000):
    """Копилка в своих координатах: низ (0, 0), рост ~400. sticker 0..1 — наклейка с Фудзи (вылет)."""
    o = []
    o.append(blob(ellipse_pts(10, 4, 190, 22, 16), "#2a1608", .3, blur(8)))
    # хвостик-завиток, нарисованный на керамике сзади справа
    tail = [(150, -40), (210, -60), (226, -120), (200, -160), (176, -146), (196, -120), (186, -84), (146, -70)]
    o.append(shape(tail, CER, blob([(196, -120), (226, -120), (210, -60), (186, -84)], CER_SH, .8), w=4.4, seed=sd))
    body = [(-170, -20), (-176, -120), (-150, -220), (-110, -270), (0, -286), (110, -270), (150, -220), (176, -120), (170, -20), (120, 0, 1),
            (-120, 0, 1)]
    inner = blob([(60, -280), (150, -220), (176, -120), (170, -20), (120, 0), (30, 0), (110, -140)], CER_SH, .85)
    inner += blob(ellipse_pts(-20, -60, 90, 40, 14), "#fbe3c0", .8)
    # лапки, нарисованные краской
    for dx in (-60, 40):
        inner += shape(ellipse_pts(dx, -14, 38, 20, 12), "#fbe3c0", "", w=3, seed=sd + 3 + dx)
        inner += line([(dx - 8, -24), (dx - 8, -8)], 2.2, CER_DK, seed=sd + 5 + dx, op=.8)
        inner += line([(dx + 8, -24), (dx + 8, -8)], 2.2, CER_DK, seed=sd + 6 + dx, op=.8)
    o.append(shape(body, CER, inner, w=5.2, seed=sd + 10))
    # голова
    hd = [(-140, -300), (-120, -380), (-60, -416), (60, -416), (120, -380), (140, -300), (110, -250), (0, -236), (-110, -250)]
    for sx in (-1, 1):
        ear = [(sx * 70, -404, 1), (sx * 116, -480, 1), (sx * 136, -360, 1)]
        o.append(shape(ear, CER, blob([(sx * 88, -398), (sx * 114, -458), (sx * 124, -378)], "#f2a0a0", .9), w=4.6, seed=sd + 20 + sx))
    hin = blob([(40, -414), (120, -380), (140, -300), (110, -250), (40, -246), (90, -320)], CER_SH, .8)
    # нарисованные глаза-точки, носик, улыбка, румянец
    for sx in (-1, 1):
        hin += f'<circle cx="{sx * 50}" cy="-330" r="13" fill="#2a2230"/>'
        hin += f'<circle cx="{sx * 50 - 4}" cy="-335" r="4" fill="#ffffff"/>'
        hin += blob(ellipse_pts(sx * 86, -292, 18, 10, 10), "#f29a8a", .8)
    hin += shape([(-10, -306), (10, -306), (0, -294)], "#e0706a", "", w=2, seed=sd + 30)
    hin += line([(-22, -284), (-11, -276), (0, -286), (11, -276), (22, -284)], 3.4, "#2a2230", seed=sd + 31)
    for sx in (-1, 1):
        for j in range(2):
            hin += line([(sx * 100, -300 + j * 14), (sx * 140, -306 + j * 18)], 2.4, CER_DK, seed=sd + 40 + j + sx, op=.9)
    o.append(shape(hd, CER, hin, w=5.2, seed=sd + 50))
    # прорезь на макушке-спине
    o.append(shape(rect_pts(-46, -432, 46, -416, 8), "#2a1810", "", w=3, seed=sd + 60) if False else "")
    slot = [(-50, -421, 1), (50, -421, 1), (46, -409, 1), (-46, -409, 1)]
    o.append(shape(slot, "#3a2216", "", w=3.2, seed=sd + 61))
    if slot_glow > 0.01:
        o.append(line([(-34, -415), (34, -415)], 6 * slot_glow, "#ffd84a", taper=.3, seed=sd + 62))
    # глянцевые блики — керамика
    o.append(line([(-130, -180), (-136, -120), (-126, -70)], 14, CER_HI, taper=.6, seed=sd + 70))
    o.append(line([(-96, -390), (-72, -404)], 10, CER_HI, taper=.6, seed=sd + 71))
    o.append(f'<circle cx="-142" cy="-226" r="7" fill="{CER_HI}"/>')
    if sticker > 0.01:
        k = sticker
        o.append(f'<g transform="translate(36 -140) rotate(-8) scale({f(k)})">' + fuji_sticker(sd + 80) + "</g>")
    return "".join(o)


def fuji_sticker(sd):
    pts = [(-62, -46, 1), (62, -46, 1), (62, 46, 1), (-62, 46, 1)]
    inner = blob(rect_pts(-70, -50, 70, 50), "#cfe6f6")
    inner += '<circle cx="34" cy="-22" r="13" fill="#e0352b"/>'
    inner += blob([(-60, 46), (-14, -22), (14, -22), (60, 46)], "#6f8fb8")
    inner += blob([(-24, -8), (-14, -22), (14, -22), (24, -8), (10, -2), (0, -10), (-10, -2)], "#ffffff")
    inner += blob(rect_pts(-70, 34, 70, 50), "#f4b6c8")
    o = shape(rect_pts(-66, -50, 66, 50, 12), "#ffffff", "", w=3.4, seed=sd)
    o += shape(pts, "#cfe6f6", inner, w=2.6, seed=sd + 1)
    return o


def piggy_at(x, y, k, rot=0.0, sqx=1.0, sqy=1.0, **kw):
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(k * sqx)} {f(k * sqy)})">{piggy(**kw)}</g>')


def shelf(x0=-400, x1=1500):
    s = []
    s.append(blob(rect_pts(x0, SHELF_Y + 30, x1, SHELF_Y + 80), "#1d2412", .3, blur(10)))
    s.append(shape(rect_pts(x0, SHELF_Y, x1, SHELF_Y + 40), "#b07a4a", blob(rect_pts(x0, SHELF_Y + 24, x1, SHELF_Y + 40), "#7f4b2b") +
                   line([(x0, SHELF_Y + 8), (x1, SHELF_Y + 8)], 3, "#d29a66", taper=.05, wmin=.9, seed=7401, op=.8), w=4.6, seed=7402))
    s.append(f'<rect x="{x0}" y="{SHELF_Y + 40}" width="{x1 - x0}" height="2000" fill="#7a5a3e"/>')
    s.append(f'<rect x="{x0}" y="{SHELF_Y + 40}" width="{x1 - x0}" height="2000" fill="#3a2a1e" opacity=".35"/>')
    s.append(line([(x0, SHELF_Y + 300), (x1, SHELF_Y + 300)], 3, "#5a3e28", taper=.05, wmin=.9, seed=7403, op=.8))
    return "".join(s)

_ = lib
