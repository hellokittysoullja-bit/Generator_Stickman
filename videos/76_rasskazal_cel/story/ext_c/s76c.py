"""Рилс 76 «Рассказал о цели», группа C — хук, комната, кот, петля: s01, s04, s05, s09, s18, s19.
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Всё время — из shots.json (t0/t1) и voice/words.json (слова по индексу wN),
секунды в коде — только длительности движений. Комната — common/room.py (раздел 76), Дима — common/people.py (dima_pj / dima),
кот — common/cat.py (через people.cat_*), предметы — common/props.py, надпись хука — room.hook_title (common/hand_text.py).
Букв и цифр нет, кроме «Кубок за что?» (s01) и «кот» (s05, common/hand_kot.py).
NOCAM=1 — без камеры и без надписи (замер движения рисунка); MASK=1 — силуэт рисунка хука (Дима, матрас, кубок) для замера заполнения.
C76_WORDS / C76_SHOTS — подмена файлов (проверка сдвига времени)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import lib  # noqa: E402
import people as PE  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from hand_kot import kot  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, rect_pts, shape  # noqa: E402,F401

WORDS = json.load(open(os.environ.get("C76_WORDS") or os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.environ.get("C76_SHOTS") or os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}
NOCAM = bool(os.environ.get("NOCAM"))
MASK = bool(os.environ.get("MASK"))
A = R.A76


def W(i):
    return WORDS[i]["start"]


def WE(i):
    return WORDS[i]["end"]


def stress(i, u):
    """Момент ударного слога: доля u длины слова i."""
    return W(i) + (WE(i) - W(i)) * u


def T0(sid):
    return SHOT[sid]["t0"]


def T1(sid):
    return SHOT[sid]["t1"]


def lerp(a, b, u):
    return a + (b - a) * u


def sm(t, a, b):
    return ease_io(clamp((t - a) / max(1e-6, b - a)))


def bump(t, t0, dur=.35):
    u = (t - t0) / dur
    if u <= 0 or u >= 1:
        return 0.0
    return math.sin(math.pi * u) ** 2


def damp(t, t0, amp, freq=3.0, dmp=6.0):
    u = t - t0
    if u <= 0:
        return 0.0
    return amp * math.exp(-dmp * u) * math.sin(2 * math.pi * freq * u)


def kick(t, t0, rise=.08, dmp=5.0):
    """Импульс 0→1 за rise и затухание."""
    u = t - t0
    if u <= 0:
        return 0.0
    return (u / rise) if u < rise else math.exp(-dmp * (u - rise))


def shake2(t, t0, amp, k=9.0, fr=19.0):
    def dec(tt):
        if tt < 0:
            return 0.0
        return math.exp(-k * tt) * math.sin(2 * math.pi * fr * tt)
    return amp * dec(t - t0), amp * .7 * dec(t - t0 - .013)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def wrap(world, cx, cy, s, rot=0.0, over="", under=""):
    """Мир в камере + экранный слой over (надпись — вне камеры)."""
    set_ink(s)
    if NOCAM:
        c = R.CAM76["hook"]
        return lib.svg(f'<g transform="{lib.cam(c[0], c[1], c[2])}">{world}</g>')
    return lib.svg(f'{under}<g transform="{lib.cam(cx, cy, s, rot)}">{world}</g>{over}')


def hook_cam(t, t_hit, t_hit2, rot0=3.8, side0=52.0, fly=.2, far=1.46, over=.06):
    """Влёт правил 28/29 (не слабее эталона 17): масштаб 1/far → 1 за fly с без разгона, перелёт over с отскоком, поворот rot0 с
    возвратом, боковой занос; удар +4 % на t_hit и +10 % на t_hit2. -> (множитель масштаба, поворот, занос, доля полёта 0…1)."""
    u = clamp(t / fly)
    e = ease_out(u, 3)
    s = 1 / far + (1 - 1 / far) * e
    if t > fly:
        s += over * math.exp(-7 * (t - fly)) * math.cos(2 * math.pi * 2.2 * (t - fly))
    rot = rot0 * (1 - e) + damp(t, fly, -1.3, 2.0, 6.0)
    side = side0 * (1 - e)
    hit = .04 * kick(t, t_hit, .03, 5.5) + .10 * kick(t, t_hit2, .03, 4.5)
    return s * (1 + hit), rot, side, 1 - e, 1 + hit


def radial_blur(world, cx, cy, s, rot, amount):
    """Радиальное размытие влёта: несколько копий мира с чуть большим масштабом поверх, полупрозрачно."""
    if amount <= .02 or NOCAM:
        return ""
    o = []
    for dk, op in ((.035, .22), (.07, .14), (.11, .08)):
        o.append(f'<g opacity="{op * amount:.3f}" transform="{lib.cam(cx, cy, s * (1 + dk * amount), rot)}">{world}</g>')
    return "".join(o)


TEXT_ZONE = [(10, 120), (700, 120), (700, 480), (10, 480)]      # экранная зона надписи хука: конфетти за ней не летит


def to_world(pts, cx, cy, s, rot=0.0):
    """Экранные точки -> мир под камерой lib.cam(cx, cy, s, rot)."""
    c, sn = math.cos(math.radians(-rot)), math.sin(math.radians(-rot))
    out = []
    for x, y in pts:
        u, v = (x - 540) / s, (y - 960) / s
        out.append((cx + u * c - v * sn, cy + u * sn + v * c))
    return out


def outside_clip(poly):
    """clip-path: всё, кроме многоугольника (мир)."""
    cid = lib.uid("ot")
    d = "M-6000 -6000H8000V8000H-6000Z M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in poly) + "Z"
    lib.DEFS.append(f'<clipPath id="{cid}"><path d="{d}" clip-rule="evenodd"/></clipPath>')
    return cid


def mask_of(svg):
    """Силуэт рисунка (белый фон, чёрная фигура) — для замера заполнения."""
    lib.DEFS.append('<filter id="mk76"><feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 9 0"/></filter>')
    return '<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>' + f'<g filter="url(#mk76)">{svg}</g>'


# ═════════════════════════ s01: хук — кубок опускается на Диму на матрасе ═════════════════════════
MX, MY, MK = A["MAT"]
HX, HY = A["HIP"]
DK = A["DK"]
TX, TY, TK = A["TROPHY"]
HATCH = A["HATCH"]


def trophy_path(t, t_land):
    """Кубок на шнурах: кадр 0 — уже летит вниз-влево маятником из правого верхнего угла (скорость не нулевая), на t_land
    садится Диме на колени и подпрыгивает. -> (x, y, rot, на месте 0/1)."""
    if t >= t_land:
        dt = t - t_land
        y = TY - 26 * math.exp(-9 * dt) * abs(math.sin(2 * math.pi * 2.6 * dt))
        rot = damp(t, t_land, 7.0, 2.4, 5.0)
        return TX, y, rot, 1.0
    u = clamp(t / t_land)
    # путь: от (TX+300, TY−470) к месту; без разгона с нуля — ease_in линейно-квадратичный, скорость в кадре 0 уже есть
    e = .35 * u + .65 * u * u
    # сначала вниз справа от надписи, влево — только когда ручки ниже её (буквы не перекрывает ни кадр)
    x = TX + 380 * (1 - e * e)
    y = lerp(TY - 470, TY, e)
    rot = lerp(-16, 0, e) + 4 * math.sin(2 * math.pi * 2.0 * t)
    return x, y, rot, 0.0


def s01_world(t, cam=None):
    t1, t2 = stress(1, .42), stress(2, .3)          # вру-ЧИ-ли, КУ-бок
    d = R.trophy_room(t, "hook", "spot")
    tx, ty, trot, landed = trophy_path(t, t1)
    hitq = kick(t, t1, .04, 7)
    # матрас пружинит от удара
    sag = .25 + .55 * kick(t, t1, .04, 4) + .08 * math.sin(t * 9)
    mat_b = PR.floor_mattress(MX, MY, MK, sag=sag, sag_x=TX - 60, layer="back")
    mat_f = PR.floor_mattress(MX, MY, MK, sag=sag, sag_x=TX - 60, layer="front")
    bounce = 10 * DK * math.sin(t * 9) + 18 * kick(t, t1, .04, 5)
    # Дима жуёт (кадр 0 — рот в движении), на ударе поднимает бровь, на «кубок» чипс выпадает изо рта
    chew = .5 + .5 * math.sin(2 * math.pi * 3.2 * t)
    expr = dict(PE.EXPR["dima"]["chew76"], chew=chew)
    if t > t1 - .02:
        expr = dict(PE.EXPR["dima"]["brow76"])
        if t > t2:
            expr = dict(expr, mouth="o", open=.35)
    hand_up = .55 + .45 * math.sin(2 * math.pi * 1.6 * t + .9)        # рука с чипсом ходит ко рту
    pose = "chips76"
    fig = PE.dima_pj(HX, HY + bounce, DK, expr, pose, u_pose=("chew76", hand_up), **PE.mattress_kw(HX, HY + bounce, DK),
                     head_add=-.04 * kick(t, t1, .05, 5) + .02 * math.sin(t * 3))
    # пакет чипсов в дальней руке на животе
    bx, by = fig["wrist"]["f"]
    bag = PR.chips_bag(bx + 34 * DK, by - 10 * DK, .9 * DK, -18 + 4 * math.sin(t * 5), crunch=bump(t, t1, .3), seed=1)
    # чипс у рта: в ближней руке, на «кубок» выпадает изо рта по дуге
    if t < t2:
        cx_, cy_ = PE.hand_pos(fig, "n", 55)
        chip = PR.chip(cx_, cy_, .9 * DK, 20 * math.sin(t * 6), seed=3)
    else:
        m = PE.mouth_pt(fig)
        dt = t - t2
        chip = PR.chip(m[0] + 160 * dt, m[1] + 30 * dt + 900 * dt * dt, .9 * DK, 400 * dt, seed=3)
    tr = PR.trophy(tx, ty, TK, glint=clamp((t - t2 + .05) / .3) if t > t2 - .05 else (t * 1.4) % 1.0, t=t, rot=trot)
    cords = PR.trophy_cords(HATCH, (tx, ty, TK, 1.0, trot), 1.0, t, sway=.3 * (1 - landed) + .5 * kick(t, t1, .04, 4))
    # конфетти: фон сыплется везде, кроме зоны надписи (верх слева); залп на ударе из-под кубка, второй — на «кубок»
    conf = PR.confetti((640, 40, 1100, 520), t, -1.0, n=18, seed=1, k=1.2)
    conf += PR.confetti((-20, 520, 1100, 1320), t, -1.0, n=34, seed=2, k=1.2)
    conf += PR.confetti((0, 0, 1, 1), t, t1, n=34, seed=3, k=1.3, burst=(tx, ty - 200), life=1.4)
    conf += PR.confetti((0, 0, 1, 1), t, t2, n=24, seed=4, k=1.2, burst=(tx + 60, ty - 330), life=1.2)
    crowd = PE.crowd_backs(-230, 1770, 470, t, clap_phase=.2, n=2, k=.82, seed=0) + PE.crowd_backs(850, 1790, 470, t, clap_phase=.6, n=2, k=.86, seed=2)
    # звон-вспышка на «кубок»
    flash = ""
    a = bump(t, t2 - .02, .3)
    if a > .01:
        flash = f'<g opacity="{a:.3f}">' + PR.star4(tx - 60 * TK, ty - 250 * TK, 60 * a + 20, 1.0) + '</g>'
        for j in range(6):
            ang = math.radians(-160 + 28 * j)
            r0, r1 = 230 * TK, 230 * TK + 90 * a
            flash += line([(tx + r0 * math.cos(ang), ty - 170 * TK + r0 * math.sin(ang)),
                           (tx + r1 * math.cos(ang), ty - 170 * TK + r1 * math.sin(ang))], 6, "#f2b632", seed=7601 + j, op=min(1, 2 * a))
    if MASK:
        return mask_of(mat_b + mat_f + fig["svg"] + bag + tr)
    if cam is not None and t < WE(8) + .3:
        conf = f'<g clip-path="url(#{outside_clip(to_world(TEXT_ZONE, *cam))})">{conf}</g>'
    world = d["bg"] + mat_b + d["pool"] + fig["svg"] + bag + chip + mat_f + cords + tr + conf + flash + crowd + d["light"]
    return world


def s01(t):
    lib.dyn_begin()
    t1, t2 = stress(1, .42), stress(2, .3)
    kk, rc, side, fl, hk = hook_cam(t, t1, t2)
    sx1, sy1 = shake2(t, t1, 10)
    sx2, sy2 = shake2(t, t2, 8)
    cx0, cy0, s0 = R.CAM76["hook"]
    cx = cx0 + side - sx1 - sx2 + 4 * math.sin(t * 2.1)
    cy = cy0 - sy1 - sy2
    # удары камерой — вокруг точки у макушки Димы (под надписью): волосы не заходят под буквы
    s = s0 * kk * (1 + .02 * sm(t, .5, 1.6))
    if t > .2:                                   # после влёта: перелёт и удары — вокруг макушки
        px, py = 230.0, 460.0
        r_ = s / s0
        cx, cy = px - (px - cx) / r_, py - (py - cy) / r_
    world = s01_world(t, (cx, cy, s, rc))
    if MASK:
        return wrap(world, cx0, cy0, s0)
    over = R.hook_title(t, WE(8))
    blur = radial_blur(world, cx, cy, s, rc, fl)
    return wrap(world, cx, cy, s, rc, blur + over)


# ═════════════════════════ ноутбук сбоку (экран — к тому, кто смотрит в него; зритель видит крышку сзади или ребром) ═════════════════════════
def laptop_side(x, y, k=1.0, th=0.0, glow=1.0, t=0.0, dust=0.0, open_=1.0):
    """Ноутбук на столе/коленях. th 0 — экран смотрит ВЛЕВО (на Диму), π — ВПРАВО (на кота); на середине поворота к зрителю
    повёрнута задняя крышка (экран зрителю не виден никогда). (x, y) — середина дна. glow — свет экрана (пятно в сторону экрана)."""
    W_, D_, H_ = 300.0, 210.0, 230.0
    c, sn = math.cos(th), math.sin(th)
    dx, dz = -c, -sn                 # куда смотрит экран (z — к зрителю)
    wx, wz = sn, -c                  # ось ширины

    def P(a, b, h):                  # a — вдоль экрана (к пользователю), b — по ширине, h — вверх
        X = a * dx + b * wx
        Z = a * dz + b * wz
        return (x + X * k, y + (Z * .32 - h) * k)
    th_ = 14.0
    base = [P(0, -W_ / 2, 0), P(0, W_ / 2, 0), P(D_, W_ / 2, 0), P(D_, -W_ / 2, 0)]
    top = [P(0, -W_ / 2, th_), P(0, W_ / 2, th_), P(D_, W_ / 2, th_), P(D_, -W_ / 2, th_)]
    o = []
    side = [base[0], base[3], top[3], top[0]] if wz * 1 > 0 else [base[1], base[2], top[2], top[1]]
    o.append(shape([p + (1,) for p in base[:2] + top[1::-1]], "#9fa4ae", "", w=3.6 * k, seed=7630))
    o.append(shape([p + (1,) for p in side], "#8f949e", "", w=3.4 * k, seed=7631))
    o.append(shape([p + (1,) for p in top], "#c9cdd5", "", w=3.6 * k, seed=7632))
    lean = 30.0 * clamp(open_)        # крышка откинута назад от экрана
    hh = H_ * clamp(open_)
    lid = [P(0, -W_ / 2, th_), P(0, W_ / 2, th_), P(-lean, W_ / 2, th_ + hh), P(-lean, -W_ / 2, th_ + hh)]
    edge = abs(sn) < .12
    inner = ""
    if not edge:
        mid = P(-lean / 2, 0, th_ + hh / 2)
        inner = blob(ellipse_pts(mid[0], mid[1], 26 * k * abs(sn) + 2, 20 * k, 14), "#c3c7cf", .9)
    if dust > .01:
        r = R.rs(7640)
        for i in range(int(18 * dust)):
            a = r.uniform(.1, .9)
            b = r.uniform(-.45, .45)
            q = P(a * D_, b * W_, th_ + 1)
            inner_d = blob(ellipse_pts(q[0], q[1], 3.2 * k, 2.2 * k, 6), "#e8e2d4", .9)
            o.append(inner_d)
    o.append(shape([p + (1,) for p in lid], "#aeb3bd", inner, w=4.0 * k, seed=7633))
    lt = ""
    if glow > .01 and open_ > .5:
        sc_ = P(-lean / 2, 0, th_ + hh / 2)
        tip = (sc_[0] + dx * 300 * k, sc_[1] + 40 * k)
        lt = f'<g {lib.blur(14)}>' + blob(ellipse_pts((sc_[0] + tip[0]) / 2, (sc_[1] + tip[1]) / 2, 170 * k, 120 * k, 20), "#cfe4ff", .32 * glow) + '</g>'
    return "".join(o), lt


# ═════════════════════════ общая сцена «утонул в матрасе» (s04, s05, s09) ═════════════════════════
def sunk_world(t, u_sink, grow, tr_pos=None, tr_k=None, glint=0.0, sag=.5, expr="pinned76", arm_up=1.0, rise=0.0, bag_shake=0.0,
               light="spot", glow=1.0, dust=1.0, sticky=None, confetti_t=None, conf_rev=False, cords_k=1.0, dima_x=0.0):
    """Комната хука: кубок (рост grow) вдавил Диму в матрас на глубину u_sink 0…1, торчит рука с пакетом; ноутбук на полу в пыли.
    rise 0…1 — Дима встаёт с матраса (перемотка). -> dict(back, fig, front, light, arm_pt)."""
    d = R.trophy_room(t, "hook", light, glow)
    tx, ty = tr_pos or (TX - 40, TY + 160 * u_sink)
    tk = tr_k or TK * grow
    mat_b = PR.floor_mattress(MX, MY, MK, sag=sag, sag_x=TX - 160, layer="back")
    mat_f = PR.floor_mattress(MX, MY, MK, sag=sag, sag_x=TX - 100, sink=u_sink, layer="front")
    hx, hy = HX + dima_x, HY
    dy = 650 * u_sink
    if rise > 0:
        hip_y, fk = PE.rise_kw(rise, hx, hy, DK)
        fig = PE.dima_pj(hx, hip_y, DK, "glance76", "shrug76", **fk)
        bx, by = fig["wrist"]["f"]
        arm_pt = (bx, by)
        clipd = fig["svg"]
    else:
        tgt = (hx + 150, lerp(hy - 150, 930, arm_up))
        kwf = dict(arms={"f": ("ik", tgt, -1)}, hands={"f": {"dir": (.2, -1), "curl": (.62, .66, .7, .74), "thumb": .55}})
        fig = PE.dima_pj(hx, hy + dy, DK, expr, "pinned76", **kwf)
        cut = clamp(u_sink * 1.4)
        cl = lib.clip_of(rect_pts(-3000, -3000, 4000, lerp(1400, 1090, cut)))
        cla = lib.clip_of(rect_pts(-3000, -3000, 4000, lerp(1400, 1185, cut)))
        armf = PE.dima_pj(hx, hy + dy, DK, expr, "pinned76", layers=("arm_f",), **kwf)["svg"]
        rest_ = PE.dima_pj(hx, hy + dy, DK, expr, "pinned76", layers=("legs", "pelvis", "body", "arm_n"), **kwf)["svg"]
        clipd = f'<g clip-path="url(#{cla})">{armf}</g><g clip-path="url(#{cl})">{rest_}</g>'
        arm_pt = fig["wrist"]["f"]
    bag = PR.chips_bag(arm_pt[0] + 10, arm_pt[1] - 70, .9, -10 + 8 * math.sin(t * 5) + 25 * bag_shake, crunch=.2, seed=1)
    tr = PR.trophy(tx, ty, tk, glint=glint, t=t, heavy=clamp(grow - 1))
    cords = PR.trophy_cords(HATCH, (tx, ty, tk, 1.0, 0.0), cords_k, t, sway=.1)
    lx, ly = A["LAPTOP"]
    lap, _ = laptop_side(lx, ly - 4, 1.4, th=.0, glow=0.0, t=t, dust=dust, open_=0.0)
    st = ""
    if sticky is not None:
        sx_, sy_, srot = sticky
        st = PR.sticky(sx_, sy_, 1.2, srot, "yellow", seed=7, mark="none")
    conf = ""
    if confetti_t is not None:
        conf = PR.confetti((-200, -300, 1500, 1500), confetti_t, 0.0, n=40, seed=31, k=1.4, reverse=conf_rev)
    back = d["bg"] + st + mat_b + d["pool"] + lap
    front = cords + tr + mat_f
    return dict(back=back, fig=clipd, bag=bag, front=front, light=d["light"], conf=conf, arm_pt=arm_pt, tr=(tx, ty, tk))


def _sticky_fall(t, tf):
    """Стикер на стене (A76 STICKY); с tf отклеивается уголком и падает на пол, кувыркаясь."""
    sx_, sy_ = A["STICKY"]
    if t < tf:
        return (sx_, sy_, 4.0)
    u = t - tf
    peel = clamp(u / .25)
    if u < .25:
        return (sx_ + 4 * peel, sy_ + 6 * peel, 4 + 18 * peel)
    v = u - .25
    y = min(sy_ + 6 + 260 * v + 900 * v * v, A["FLOOR"] + 70)
    x = sx_ + 4 + 60 * math.sin(v * 5) + 40 * v
    return (x, y, 22 + 140 * v if y < A["FLOOR"] + 70 else 80)


# ═════════════════════════ s04: кубок вырастает и вдавливает Диму в матрас ═════════════════════════
def s04(t):
    lib.dyn_begin()
    t14, t17, t20 = stress(14, .3), W(17), stress(20, .35)
    e20 = WE(20)
    g = clamp((t - (t14 - .04)) / .14)
    grow = 1 + (1 - math.exp(-6 * g) * math.cos(9 * g)) if g > 0 else 1.0
    grow = min(grow, 2.12)
    if t > t14 + .3:
        grow = 2.0 + .06 * math.exp(-5 * (t - t14 - .3)) * math.cos(12 * (t - t14))
    u = sm(t, t14 - .02, t17 + .1)
    w = sunk_world(t, u, grow, glint=clamp((t - t14) / .5), sag=.4 + .6 * u, expr="pinned76", arm_up=sm(t, W(16) - .2, t17),
                   bag_shake=bump(t, t17, .4), light="spot", glow=1 - .5 * sm(t, e20, e20 + .6), dust=1.0,
                   sticky=_sticky_fall(t, t20), confetti_t=T0("s04") + (t - T0("s04")) * (1 - .5 * sm(t, e20, e20 + .5)))
    lx, ly = A["LAPTOP"]
    puff = PR.dust_puff(lx, ly - 60, 1.3, (t - (t20 - .05)) / .9, seed=4)
    world = w["back"] + w["fig"] + w["bag"] + w["front"] + puff + w["conf"] + w["light"]
    # камера: отъезд на росте кубка, потом медленный дрейф к торчащей руке
    pull = sm(t, t14 - .05, t14 + .35)
    drift = sm(t, t14 + .35, T1("s04") + .2)
    cx = lerp(lerp(640, 660, pull), 560, drift)
    cy = lerp(lerp(980, 700, pull), 820, drift)
    s = lerp(lerp(.82, .56, pull), .66, drift)
    sx_, sy_ = shake2(t, t14 + .1, 9)
    s *= 1 + .04 * kick(t, t14 + .08, .04, 5)
    # толпа (экран): хлопает всё реже после «сделает»
    tc = t if t < e20 else e20 + (t - e20) * .35
    crowd = PE.crowd_backs(-60, 2040, 1200, tc, clap_phase=.15, n=4, k=.84, seed=1)
    return wrap(world, cx - sx_, cy - sy_, s, 0.0, crowd)


# ═════════════════════════ s05: кот входит, «кот» на стене ═════════════════════════
CAM05 = (300.0, 1030.0, .75)
CAT05 = (-80.0, 1440.0, 2.0)
KOT05 = (-260.0, 330.0, 2.2)          # «кот» на чистой стене (мир): левый край, линия строки, размер


def s05(t):
    lib.dyn_begin()
    t21, t22, t22e, t24 = W(21), W(22), WE(22), W(24)
    a = max(0.0, T0("s05") - SH["pad"])
    w = sunk_world(t, 1.0, 2.0, glint=0.0, sag=1.0, light="day", glow=0.0, dust=1.0, sticky=_sticky_fall(t, -99))
    cx_, cy_, ck = CAT05
    t_arr = lerp(a, t21, .42)                   # дошёл
    if t < t_arr:
        x = lerp(cx_ - 620, cx_, ease_out(clamp((t - a) / (t_arr - a)), 1.4) * .8 + .2 * clamp((t - a) / (t_arr - a)))
        st = dict(look=(.8, .1), tail=6 * math.sin(t * 4), flame_e=.9)
        cat = PE.cat_walk(x, cy_, ck, t, st, .42)
    else:
        sniff = bump(t, t_arr, .5)
        no = clamp((t - (t_arr + .4)) / .5)
        shake = 14 * math.sin(2 * math.pi * 2.6 * (t - t_arr - .4)) * (1 - no) if .0 < no < 1 else 0.0
        camp = sm(t, t21 - .15, t21 + .1)
        st = dict(look=lerp(.8, 0.0, camp), tail=6 * math.sin(t * 3), flame_e=1.0 + 1.1 * bump(t, t24, .5))
        st["look"] = (lerp(.8, 0.0, camp), lerp(.6 * sniff, 0.0, camp))
        st["drop"] = .4 * sniff
        st["turn"] = shake / 30
        st["tilt"] = shake * .4 + 4 * camp * math.sin(t * 2)
        st["paw"] = .45 * camp
        st["paw_dx"] = 40
        st["perk"] = .5 * camp
        st["ear"] = 18 * bump(t, t24, .3)
        st["blink"] = bump(t, t21 + .7, .16)
        cat = PE.cat_svg(cx_, cy_, ck, st, t)
    kx, ky, ks = KOT05
    note = kot(t, t22 - .2, t22e - (t22 - .2), kx, ky, ks)
    world = w["back"] + w["fig"] + w["bag"] + w["front"] + note + cat + w["light"]
    u = sm(t, a, T1("s05") + .2)
    lean = sm(t, t22 - .3, t22e + .2)
    cx, cy, s = CAM05
    return wrap(world, cx - 30 * u - 40 * lean, cy - 10 * u - 30 * lean, s * (1 + .06 * u))


# ═════════════════════════ s09: перемотка назад ═════════════════════════
def s09(t):
    lib.dyn_begin()
    a = max(0.0, T0("s09") - SH["pad"])
    t43, t47 = W(43), stress(47, .3)
    r = clamp((t - T0("s09")) / (t47 - T0("s09")))
    rr = r * r * (3 - 2 * r) * .5 + r * .5
    u_sink = 1 - sm(rr, .0, .38)
    grow = 2 - sm(rr, .12, .42)
    rise = sm(rr, .5, .88)
    lift = clamp((rr - .45) / .55)
    # кубок: от места на Диме — вверх по шнурам в люк, уменьшаясь
    rest = (TX - 40, TY + 160 * u_sink)
    hx_, hy_ = HATCH
    e = lift ** 1.6
    tr_pos = (lerp(rest[0], hx_, e), lerp(rest[1], hy_ + 330, e))
    tr_k = TK * grow * (1 - .65 * e)
    gone = t > t47
    w = sunk_world(t, u_sink, grow, tr_pos=tr_pos, tr_k=tr_k, sag=.3 + .7 * u_sink, expr="pinned76", arm_up=1.0, rise=rise if u_sink < .02 else 0.0,
                   light="spot", glow=1.0, dust=1.0 - sm(rr, .3, .6), sticky=_sticky_fall(2 * T0("s09") - t + 6.4 - T0("s09") if False else -99, 0),
                   confetti_t=2 * T0("s09") - t, conf_rev=False)
    world = w["back"] + w["fig"] + w["bag"]
    if not gone:
        world += w["front"]
    else:
        mx = PR.floor_mattress(MX, MY, MK, sag=.3, sag_x=TX - 160, layer="front")
        world += mx
    world += w["conf"] + w["light"]
    # штрихи скорости вдоль хода назад — вверх, за кубком
    streak = ""
    if not gone and lift > .02:
        for j in range(5):
            x0 = tr_pos[0] + (j - 2) * 60 * tr_k
            y0 = tr_pos[1] + 40
            streak += line([(x0, y0 + 260 + 80 * (j % 2)), (x0 + 10, y0 + 40)], 7, "#ffffff", seed=7900 + j, op=.75)
    world += streak
    # вспышка в потолке на «кубок»
    fl = bump(t, t47 - .03, .35)
    if fl > .01:
        world += blob(ellipse_pts(hx_, hy_ + 30, 260 * fl + 60, 120 * fl + 30, 24), "#fff6c8", .9 * fl)
        world += PR.star4(hx_, hy_ + 40, 140 * fl, 1.0)
    # камера: ускоряющийся отъезд против хода
    q = clamp((t - a) / (T1("s09") + SH["pad"] - a)) ** 1.8
    cx, cy, s = lerp(620, 760, q), lerp(900, 420, q), lerp(.8, .5, q)
    s *= 1 + .05 * kick(t, t47, .04, 5)
    # кот на переднем плане (экран): тычет лапой вперёд-назад, «перемотка»
    pk = sm(t, t43 - .25, t43) * (1 - sm(t, t47 + .1, t47 + .4))
    jab = .5 + .5 * math.sin(2 * math.pi * 3.0 * (t - t43)) if t > t43 else .5
    st = dict(PE.CAT_ST76["poke"])
    st.update(paw=pk * (.55 + .45 * jab), paw_dx=80 + 50 * jab, look=(.7, -.3), blink=bump(t, t47 + .2, .16))
    cat = PE.cat_svg(120, 1560, 1.15, st, t)
    crowd = PE.crowd_backs(-60, 2140, 1200, 2 * T0("s09") - t, clap_phase=.15, n=4, k=.84, seed=1)
    # штрихи перемотки (экран): короткие дуги «назад» поперёк кадра, пока идёт перемотка
    lines_ = ""
    if t < t47 + .05:
        for j in range(7):
            yy = 240 + 150 * j
            ph = ((t * 2.4 + j * .37) % 1.0)
            x1 = 1100 - 1300 * ph
            lines_ += line([(x1 + 160, yy + 30), (x1, yy)], 5, "#fffaf0", seed=7910 + j, op=.55)
    flash = ""
    f2 = clamp(1 - abs(t - t47) * 30 / 2)
    if f2 > .01:
        flash = f'<rect width="1080" height="1920" fill="#fff8de" opacity="{.55 * f2:.3f}"/>'
    return wrap(world, cx, cy, s, 0.0, lines_ + crowd + cat + flash)


# ═════════════════════════ s18: печатает молча, разворачивает ноутбук к коту ═════════════════════════
DS18 = .92
CAM18 = (780.0, 900.0, 1.05)


def s18(t):
    lib.dyn_begin()
    t91, t92, t93, t94, t96 = W(91), W(92), W(93), W(94), stress(96, .3)
    nd = R.desk_evening(t)
    hx, hy = R.SIT
    turn = sm(t, t93 - .05, t94 + .35)
    pose = "type76" if turn < .02 else ("turn76" if turn > .98 else None)
    tap = math.sin(2 * math.pi * 6.0 * t) * (1 - turn)
    ex = dict(PE.EXPR["dima"]["screen76"]) if turn < .5 else dict(PE.EXPR["dima"]["beam76"], look=(.7, .1), open=.35)
    ex["closed"] = bump(t, t91 - .3, .14)
    fkw = dict(PE.sit_kw(hx, hy, DS18))
    if pose is None:
        kw = dict(u_pose=("turn76", turn))
        pose = "type76"
    else:
        kw = {}
    arms = None
    if turn < .05:      # пальцы бегают по клавишам
        lap = R.LAPTOP
        arms = {"n": ("ik", (hx + 330 * DS18 + 10 * tap, hy - 212 * DS18 - 8 * abs(tap)), -1),
                "f": ("ik", (hx + 250 * DS18 - 8 * tap, hy - 215 * DS18 - 8 * abs(math.cos(t * 37))), -1)}
    lay = dict(fkw)
    lay.update(kw)
    legs = PE.dima(hx, hy, DS18, ex, pose, layers=("legs",), arms=arms, **lay)
    body = PE.dima(hx, hy, DS18, ex, pose, layers=("pelvis", "arm_f", "body"), arms=arms, head_add=.03 * math.sin(t * 2), **lay)
    arm = PE.dima(hx, hy, DS18, ex, pose, layers=("arm_n",), arms=arms, **lay)
    lx, ly = R.LAPTOP
    lap_svg, lap_lt = laptop_side(lx + 40, ly + 10, .8, th=math.pi * turn, glow=1.0, t=t)
    cup = PR.trophy_pencils(R.CUP76[0], R.CUP76[1], .8, t)
    # кот на столе: следит за пальцами, на развороте получает свет экрана, на «готовым» глаза — звёзды и искорки
    cx_, cy_ = R.CAT_DESK[0] + 70, R.CAT_DESK[1]
    wow = sm(t, t96 - .08, t96 + .1)
    st = dict(PE.CAT_ST76["watch"]) if turn < .6 else dict(PE.CAT_ST76["wow"] if wow > .3 else {"look": (-.6, .2), "perk": .8})
    st["tail"] = 6 * math.sin(t * 2.4)
    st["blink"] = bump(t, t91 + .5, .15)
    st["look"] = st.get("look", (0, 0)) if turn < .6 else ((-.6, .2) if wow < .3 else (0, 0))
    if turn < .6:
        st["look"] = (-.6 + .15 * math.sin(t * 12), .7)      # глаза бегают за пальцами
    cat = PE.cat_svg(cx_, cy_, .82, st, t)
    spark = PR.sparkles(cx_, cy_ - 250 * .82, 1.2, wow, t, seed=18, n=5, col="#f2c94c", r=180)
    lit_cat = ""
    if turn > .5:
        lit_cat = f'<g {lib.blur(18)}>' + blob(ellipse_pts(cx_ - 40, cy_ - 220 * .82, 110, 90, 18), "#cfe2ff", .2 * sm(t, t94, t94 + .3)) + '</g>'
    lit_d = ""
    if turn < .7:
        hd = body["head"]
        lit_d = f'<g {lib.blur(16)}>' + blob(ellipse_pts(hd[0] + 50, hd[1] + 10, 110, 130, 18), "#d6e8ff", .3 * (1 - turn) * (1 + .1 * tap)) + '</g>'
    world = (nd["bg"] + cup + nd["chair_back"] + nd["desk_top"] + legs["svg"] + nd["desk_legs"] + nd["chair_seat"] + body["svg"]
             + cat + lap_svg + arm["svg"] + lap_lt + lit_d + lit_cat + spark)          # настольную лампу не ставим: свет — от экрана
    u = sm(t, T0("s18") - .2, T1("s18") + .2)
    cx, cy, s = CAM18
    cx += 60 * turn + 10 * u
    s *= 1 + .02 * u + .05 * kick(t, t96, .05, 4)
    return wrap(world, cx, cy - 20 * u, s)


# ═════════════════════════ s19: петля — кот хлопает лапами ═════════════════════════
def s19(t):
    lib.dyn_begin()
    t98, t99, t101 = W(98), stress(99, .25), stress(101, .3)
    d = R.trophy_room(t, "hook", "lamp")
    mat_b = PR.floor_mattress(MX, MY, MK, sag=.12, sag_x=HX + 200, layer="back")
    mat_f = PR.floor_mattress(MX, MY, MK, sag=.12, sag_x=HX + 200, layer="front")
    hx, hy = HX - 10, HY - 10
    laugh = sm(t, t101 - .1, t101 + .1)
    ex = dict(PE.EXPR["dima"]["laugh76"]) if laugh > .5 else dict(PE.EXPR["dima"]["dream76"], look=(.6, -.1))
    ex["closed"] = bump(t, T0("s19") + .3, .14)
    fig = PE.dima(hx, hy + 6 * laugh * math.sin(t * 30), DK, ex, "laptop_lap76", head_add=.03 * math.sin(t * 2) - .08 * laugh,
                  **PE.sit_mat_kw(hx, hy, DK))
    lap_svg, lap_lt = laptop_side(hx + 310 * DK, hy - 120 * DK, 1.0, th=0.0, glow=.8, t=t)
    # кот на матрасе на месте кубка: встаёт на задние лапы, хлопает передними
    cx_, cy_, ck = TX + 20, TY - 40, 1.45
    up = sm(t, t98 - .1, t98 + .15)
    def clap_amt(tt):
        return max(bump(tt, t99 - .12, .26), bump(tt, t101 - .12, .26))
    cu = clap_amt(t)
    gap = 110 * (1 - cu) + 4
    st = dict(sy=1 + .1 * up, sx=1 - .04 * up, paw=.95 * up, paw_l=.95 * up, paw_dx=gap / 1.6 - 15, paw_l_dx=gap / 1.6 - 15, perk=.6 + .4 * up,
              smile=1.0, look=(-.3 * (1 - up), 0), flame_e=1.0 + .8 * bump(t, t101, .5), tail=8 * math.sin(t * 3),
              blink=bump(t, T0("s19") + .1, .15))
    cat = PE.cat_svg(cx_, cy_, ck, st, t)
    conf = ""
    for tc in (t99, t101):
        conf += PR.confetti((0, 0, 1, 1), t, tc, n=16, seed=int(tc * 10) % 50, k=1.0, burst=(cx_, cy_ - 250 * ck), life=1.1)
    world = d["bg"] + mat_b + fig["svg"] + lap_svg + mat_f + lap_lt + d["light"] + cat + conf
    if MASK:
        return wrap(mask_of(mat_b + mat_f + fig["svg"] + lap_svg + cat), *R.CAM76["hook"])
    cx0, cy0, s0 = R.CAM76["hook"]
    u = sm(t, T0("s19") - .2, T1("s19") + .2)
    s = s0 * (1 + .03 * u + .025 * kick(t, t99, .04, 6) + .025 * kick(t, t101, .04, 6))
    return wrap(world, cx0 + 20 * u, cy0 - 10 * u, s)


def frame(sid, t):
    return {"s01": s01, "s04": s04, "s05": s05, "s09": s09, "s18": s18, "s19": s19}[sid](t)
