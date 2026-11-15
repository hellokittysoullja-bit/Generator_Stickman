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
    return s * (1 + hit), rot, side, 1 - e


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
    x = lerp(TX + 300, TX, e)
    y = lerp(TY - 470, TY, e) - 40 * math.sin(math.pi * e)
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
    kk, rc, side, fl = hook_cam(t, t1, t2)
    sx1, sy1 = shake2(t, t1, 10)
    sx2, sy2 = shake2(t, t2, 8)
    cx0, cy0, s0 = R.CAM76["hook"]
    cx = cx0 + side - sx1 - sx2 + 4 * math.sin(t * 2.1)
    cy = cy0 - sy1 - sy2
    s = s0 * kk * (1 + .02 * sm(t, .5, 1.6))
    world = s01_world(t, (cx, cy, s, rc))
    if MASK:
        return wrap(world, cx0, cy0, s0)
    over = R.hook_title(t, WE(8))
    blur = radial_blur(world, cx, cy, s, rc, fl)
    return wrap(world, cx, cy, s, rc, blur + over)


def frame(sid, t):
    return {"s01": s01}[sid](t)
