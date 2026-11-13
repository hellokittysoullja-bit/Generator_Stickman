"""s02 рилса 26 «кроссовки»: вечер, торшер. Дима лежит на диване под пледом (поза рилса 25), на животе пачка чипсов;
правая рука — плечо и предплечье на двух суставах (IK в template26l.html): на «обещает» кулак вверх, на «бегать» рука
падает на плед. Кот рилса 24 сидит у него на бёдрах и смотрит с сомнением (прищур, бровь домиком).
Запуск: python3 heroes26l.py → heroes26l.html (анимация — template26l.html); пишет flame26l.json (центр огонька для сборки).
"""
import inspect
import json
import math
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import heroes25 as L  # noqa: E402  (импортирует heroes24 и ставит голову лёжа)
import heroes24 as H  # noqa: E402
from heroes24 import shape, blob, line, rect_pts, blur, INK  # noqa: E402
from heroes26e import arm_parts  # noqa: E402
from ink import ellipse_pts, fill_d  # noqa: E402

W, H_ = 1080, 1920
DEFS = H.DEFS
REG = H.REG

# ─── кот: сидит на бёдрах лежащего (верх пледа у x≈720 — y≈1108), лапы чуть утоплены в плед
CAT_AT = (720, 1120)
H.CAT_TF = f"translate({CAT_AT[0]} {CAT_AT[1]}) scale(1.1) translate(-836 -1306)"
H.FLAME_C = (987 - 812 + CAT_AT[0], 934 - 1244 + CAT_AT[1])

# ─── свет на лицо лёжа: обратное к голове рилса 25 (не зеркальной)


def G2H_lie(x, y, hr=0.0):
    dx, dy = x - L.HX, y - L.HY
    c, s_ = math.cos(math.radians(-L.HR)), math.sin(math.radians(-L.HR))
    return (dx * c - dy * s_) / L.HS, (dx * s_ + dy * c) / L.HS


H.G2H = G2H_lie

# ─── плед лёжа: тень кота — под сидящим котом
_src = inspect.getsource(L.plaid_lying).replace("ellipse_pts(910, 1148, 160, 16, 12)",
                                                f"ellipse_pts({CAT_AT[0] + 4}, {CAT_AT[1] + 2}, 104, 13, 12)")
_ns = dict(vars(L))
exec(_src, _ns)
plaid_lying = _ns["plaid_lying"]

# ─── рука: плечо S, локоть E0, запястье W0 в покое (рука лежит на пледе, кулак на пачке)
ARM_S, ARM_E, ARM_W = (440, 1132), (548, 1168), (606, 1104)
FIST_REL = (2.0, -34.0)          # центр кулака от запястья — в осях предплечья позы с ручкой рилса 24
FIST_DANG = 133 - 196.1          # угол кулака относительно направления предплечья (из той же позы)


def fist_place():
    """Кулак жёстко на конце предплечья: смещение и угол — как у кулака с ручкой рилса 24 относительно его предплечья."""
    a24 = math.atan2(1196 - 1222, 430 - 520)
    a = math.atan2(ARM_W[1] - ARM_E[1], ARM_W[0] - ARM_E[0])
    rx, ry = 432 - 430, 1162 - 1196
    c, s_ = math.cos(a - a24), math.sin(a - a24)
    cx, cy = ARM_W[0] + rx * c - ry * s_, ARM_W[1] + rx * s_ + ry * c
    return cx, cy, math.degrees(a) + (133 - math.degrees(a24))


def chips():
    """Пачка чипсов на животе: фольга без букв (красная, с жёлтым кругом-«чипсом»), открытый верх, чипсы видны."""
    s = ['<g id="chips">']
    pc = H.clip_of(REG["plaid"])
    s.append(f'<g clip-path="url(#{pc})">' + blob(ellipse_pts(586, 1104, 56, 12, 12), "#0d160f", .55, blur(5)) + "</g>")
    bag = [(538, 1104, 1), (544, 1040), (542, 994, 1), (632, 990, 1), (628, 1036), (636, 1100, 1), (590, 1110)]
    inner = blob([(538, 1104), (544, 1040), (566, 1040), (562, 1106)], "#a8202a", .8)          # тень слева
    inner += blob([(604, 1000), (630, 996), (628, 1100), (614, 1104)], "#f2606a", .45)          # блик фольги
    inner += blob(ellipse_pts(586, 1054, 24, 18, 14, rot=-8), "#f2c23a")                         # «чипс» на пачке
    inner += blob(ellipse_pts(582, 1050, 12, 7, 10, rot=-8), "#ffe08a", .9)
    inner += line([(560, 1076), (572, 1082)], 2, "#ffd0a0", seed=1502, op=.8)
    inner += blob([(542, 994), (632, 990), (632, 1006), (542, 1010)], "#7a1018", .7)             # смятый верх
    s.append(shape(bag, "#d8333c", inner, w=4.4, seed=1500))
    for i, (x0, x1) in enumerate([(552, 572), (588, 600), (612, 622)]):
        s.append(line([(x0, 1000), ((x0 + x1) / 2, 992), (x1, 1002)], 2.2, INK, seed=1505 + i, op=.8))
    # чипсы в раскрытом верху
    for i, (x, y, r) in enumerate([(562, 990, 14), (586, 984, 16), (610, 990, 13)]):
        s.append(shape(ellipse_pts(x, y, r, r * .62, 12, rot=(-1) ** i * 14), "#f2c23a",
                       blob(ellipse_pts(x - 3, y - 2, r * .5, r * .26, 10), "#ffe08a", .9), w=3.0, seed=1510 + i))
    # пара крошек на пледе
    for i, (x, y) in enumerate([(650, 1108), (520, 1112), (668, 1120)]):
        s.append(shape(ellipse_pts(x, y, 5, 3.4, 8, rot=20 * i), "#f2c23a", w=1.8, seed=1520 + i))
    s.append("</g>")
    return "".join(s)


def arm():
    up, fore = arm_parts(ARM_S, ARM_E, ARM_W, seed=1600)
    fx, fy, fa = fist_place()
    return (f'<g id="arm_up" transform="rotate(0 {ARM_S[0]} {ARM_S[1]})">{up}'
            f'<g id="arm_fore" transform="rotate(0 {ARM_E[0]} {ARM_E[1]})">{fore}{H.hand_s(H.fist, fx, fy, round(fa, 2), 1620, 1.05)}'
            f'</g></g>')


def hem():
    """Подвёрнутый край пледа у груди (как в plaid_lying) — поверх корня руки."""
    hm = [(338, 1252), (354, 1198), (394, 1150), (448, 1112), (512, 1090), (520, 1114), (462, 1136), (414, 1170), (378, 1216), (360, 1262)]
    return shape(hm, "#86b276", H.tartan(0, W, 1080, 1300) + blob([(338, 1250), (354, 1198), (394, 1150), (414, 1170), (378, 1220)],
                                                                 "#5f8a52", .55) +
                 line([(370, 1226), (404, 1172), (456, 1132), (512, 1108)], 2.2, "#4f7a44", seed=548, op=.8), w=4.6, seed=547)


def cat_brows():
    """Брови сомнения поверх глаз (светлым по шерсти, как веко): левая (от зрителя) сведена вниз к носу, правая
    поднята дугой. В осях головы кота — наклоняются вместе с ней."""
    s = [f'<g id="cat_brows" transform="{H.CAT_TF}"><g id="cat_brows_tilt">']
    ex = H.CX - 44
    s.append(f'<g id="brow_L">' + line([(ex - 30, 1016), (ex - 4, 1022), (ex + 24, 1032)], 5.2, "#a59ec4", seed=1700, taper=.55, wmin=.3) +
             "</g>")
    ex = H.CX + 44
    s.append(f'<g id="brow_R">' + line([(ex - 26, 1020), (ex - 2, 1000), (ex + 28, 1008)], 5.2, "#a59ec4", seed=1701, taper=.55, wmin=.3) +
             "</g>")
    s.append("</g></g>")
    return "".join(s)


def build():
    H.light_defs()
    a_dima = ('<g id="dima_all">' + L.dima_lying_back() + f'<g id="dima_head_pose">{H.dima_head()}</g></g>')
    a_plaid = '<g id="plaid_breath">' + plaid_lying() + "</g>" + chips() + arm() + hem()
    a_cat = H.cat_art()
    layers = []
    for name, art, lit, top in [("dima", a_dima, H.lights_dima(), ""),
                                ("plaid", a_plaid, H.lights_plaid(), ""),
                                ("cat", a_cat, H.lights_cat(), H.cat_eyes() + cat_brows() + H.cat_flame()), ("fx", "", "", "")]:
        if art:
            m = H.mask_of(f"A_{name}")
            body = (f'<g id="A_{name}" filter="url(#fNight)">{art}</g>'
                    f'<g style="mix-blend-mode:screen" mask="url(#{m})">{lit}</g>')
        else:
            body = ""
        inner = body + top
        if name == "cat":
            inner = f'<g id="cat_jump">{inner}</g>'
        layers.append(f'<g id="L_{name}" style="isolation:isolate">{inner}</g>')
    return (f'<svg id="scene" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H_}" viewBox="0 0 {W} {H_}">'
            f'<defs>{"".join(DEFS)}</defs>{"".join(layers)}</svg>')


if __name__ == "__main__":
    here = __file__.rsplit("/", 1)[0]
    svg = build()
    html = open(f"{here}/template26l.html").read().replace("<!--SVG-->", svg)
    html = html.replace("/*CONST*/", f"const CAT_AT = {list(CAT_AT)}, ARM = {{S: {list(ARM_S)}, E: {list(ARM_E)}, P: {list(ARM_W)}}};")
    open(f"{here}/heroes26l.html", "w").write(html)
    json.dump([round(H.FLAME_C[0], 1), round(H.FLAME_C[1], 1)], open(f"{here}/flame26l.json", "w"))
    print("heroes26l.html", len(html) // 1024, "KB", "flame", H.FLAME_C)
