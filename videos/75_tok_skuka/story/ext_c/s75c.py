"""Рилс 75 «Ток или скука», группа C — хук, пустой стул, полёт вдоль провода, окно и петля:
s01 (хук: белая комната опыта, Дима на стуле жмёт красную кнопку, разряд, волосы дыбом, счётчик 188→189, кот роняет кружку),
s02 (ближе: второй всплеск на «бьёт», дым кольцами на «током», на «снова» жмёт ещё раз — 190),
s04 (пустой стул анфас, кнопка к зрителю пульсирует, на «тоже» разгорается, на «нажал» жмётся сама),
s07 (от коробки камера уходит вдоль провода под дверь, летит над ночным кампусом, провод упирается в старый аппарат),
s17 (Дима и кот у окна, облака быстрее на «пять минут», выдох на «смотрит»),
s18 (петля ракурсом s01: комната Димы днём, окно вместо счётчика, лампочки-идеи, ящик с кнопкой задвинут, кот отпивает).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. ВСЕ времена — из shots.json и voice/words.json при импорте (ни одной
секунды руками). Места — common/room.py, люди — common/people.py, кот — common/cat.py, предметы — common/props.py, надпись хука —
common/hook_text.py. NOCAM=1 — без камеры и без надписи (замер движения рисунка), MASK=1 — силуэт рисунка хука (замер высоты)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as CAT  # noqa: E402
import hook_text as HT  # noqa: E402
import lib  # noqa: E402
import people as PE  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, rect_pts, shape  # noqa: E402,F401

W = json.load(open(os.path.join(STORY, "voice", "words.json")))
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOT = {s["id"]: s for s in SH["shots"]}


def ws(i):
    return W[i]["start"]


def we(i):
    return W[i]["end"]


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


def decay(t, t0, k=6.0):
    return math.exp(-k * (t - t0)) if t >= t0 else 0.0


def shake2(t, t0, amp, k=9.0, fr=19.0):
    def dec(tt):
        if tt < 0:
            return 0.0
        return math.exp(-k * tt) * math.sin(2 * math.pi * fr * tt)
    return amp * dec(t - t0), amp * .7 * dec(t - t0 - .013)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def hook_cam(t, t_hit, t_hit2, rot0=3.6, side0=-55.0):
    """Влёт правил 28/29: с 40 % дальше (1/(1+0.4)) за 0.22 с, перелёт 5 % с отскоком, поворот rot0 с возвратом, занос сбоку;
    удар +4 % на t_hit (разряд) и +8 % на t_hit2 (щелчок счётчика). -> (множитель масштаба, поворот, занос)."""
    u = clamp(t / .22)
    e = ease_out(u, 3)
    s = 1 / 1.4 + (1 - 1 / 1.4) * e
    if t > .22:
        s += .05 * math.exp(-7 * (t - .22)) * math.sin(2 * math.pi * 2.2 * (t - .22) + math.pi / 2)
    rot = rot0 * (1 - e) + damp(t, .22, -1.2, 2.0, 6.0)
    side = side0 * (1 - e)
    hit = 0.0
    for th, a in ((t_hit, .04), (t_hit2, .08)):
        if t > th:
            h = t - th
            hit += a * math.exp(-5.5 * h) * (1 if h > .03 else h / .03)
    return s * (1 + hit), rot, side


def mask_svg(svg):
    fid = "mk75"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        lib.DEFS.append(f'<filter id="{fid}"><feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 9 0"/></filter>')
    return f'<g filter="url(#{fid})">{svg}</g>'


# ═════════════════════════ хук: общее для s01 и s02 ═════════════════════════
T_S02 = SHOT["s02"]["t0"]
T_HIT = ws(1)                 # «жмёт»: палец вдавливает кнопку — разряд
T_K1 = ws(2)                  # «кнопку»: счётчик 188 → 189
T_BREAK = ws(2) + .4          # кружка бьётся о столешницу
T_BEAT = ws(4)                # «бьёт»: второй всплеск тока
T_SMOKE = ws(5)               # «током»: дым кольцами, выдох облачком
T_REACH = ws(8)               # «жмёт»: палец снова идёт к кнопке
T_SNOVA = ws(9)               # «снова»: нажал, 189 → 190
SX, SY = R.LAB_SIT
BOX = R.LAB_BOX
BOX_K = .82
CNT = R.LAB_COUNTER
CNT_K = .8
CATP = R.LAB_CAT
CAT_K = R.LAB_CAT_K
CAM1 = (560.0, 740.0, 1.35)   # s01 после влёта (= LAB_CAMS["hook"])
CAM2 = (554.0, 650.0, 1.7)    # s02 ближе: волосы дыбом не заходят под надпись
MUG_LAND = (CATP[0] - 18.0, R.LAB_TOP - 8.0)


def counter_state(t):
    """(value, roll): кадр 0 — докрутка 187→188, «кнопку» — 188→189, «снова» — 189→190."""
    if t < .2:
        return 187, .5 + .5 * ease_out(t / .2, 2)
    if t < T_K1:
        return 188, 0.0
    if t < T_SNOVA + .02:
        return 188, clamp((t - T_K1) / .24) if t < T_K1 + .24 else 1.0
    return 189, clamp((t - T_SNOVA - .02) / .24)


def press_state(t):
    """(reach, press) ближней руки Димы."""
    if t < T_HIT:
        r = lerp(.42, 1.0, t / max(1e-6, T_HIT - .03)) if t < T_HIT - .03 else 1.0
        p = sm(t, T_HIT - .05, T_HIT)
        return r, p
    if t < T_REACH:
        # после разряда рука отдёргивается к колену, потом лежит на колене
        back = sm(t, T_HIT + .22, T_HIT + .55)
        return 1 - .85 * back, 1 - sm(t, T_HIT + .16, T_HIT + .3)
    r = lerp(.15, 1.0, ease_out(clamp((t - T_REACH) / max(.05, T_SNOVA - T_REACH - .02)), 1.4))
    p = sm(t, T_SNOVA - .05, T_SNOVA)
    if t > T_SNOVA + .25:
        p = 1 - sm(t, T_SNOVA + .25, T_SNOVA + .4)
    return r, p


def hair_state(t):
    h = .55 * math.exp(-4 * t) + .05
    for th, a in ((T_HIT, 1.0), (T_BEAT, 1.0), (T_SNOVA, 1.0)):
        if t >= th:
            h = max(h, a * (.82 + .18 * math.exp(-3 * (t - th))) * min(1, (t - th) / .05))
    return min(1.0, h)


def zap_u(t):
    u = .0
    for th, a, d in ((T_HIT, 1.0, .32), (T_BEAT, .9, .34), (T_SNOVA, 1.0, .36)):
        if th - .01 <= t < th + d:
            u = max(u, a * (1 - (t - th) / d) ** .7)
    return u


def flicker(t):
    """Свет комнаты пульсирует от разряда (в кадре 0 — ещё от прошлого): доля затемнения 0…1, плавно (без стробоскопа)."""
    v = .0
    for th, a in ((-.12, .7), (T_HIT, 1.0), (T_BEAT, .9), (T_SNOVA, 1.0)):
        if t >= th:
            q = t - th
            v = max(v, a * math.exp(-4.5 * q) * (.55 + .45 * math.cos(2 * math.pi * 6.5 * q)) * min(1.0, q / .03 + (th < 0)))
    return v


def cast_shadow(svg, dx=78.0, dy=8.0, op=.15):
    """Тень фигуры на белой стене от высокого окна слева: силуэт тёмным, мягкий край, сдвиг вправо."""
    fid = "sh75"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        lib.DEFS.append(f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%"><feColorMatrix type="matrix" '
                        f'values="0 0 0 0 .2 0 0 0 0 .22 0 0 0 0 .26 0 0 0 9 0"/><feGaussianBlur stdDeviation="7"/></filter>')
    return f'<g transform="translate({dx:.1f} {dy:.1f})" opacity="{op:.3f}"><g filter="url(#{fid})">{svg}</g></g>'


def smoke_puffs(head, s, t, u, seed=0, top=None):
    """Дымок из волос: клубочки поднимаются невысоко и уходят влево-назад (не выше top — под надписью чисто)."""
    if u <= .01:
        return ""
    hx, hy = head
    o = []
    for j in range(5):
        ph = (t * .85 + j / 5 + seed * .17) % 1.0
        y = hy - 150 * s - 120 * s * ph
        if top is not None and y - 30 * s < top:
            continue
        x = hx - 30 * s - 90 * s * ph + 18 * s * math.sin(t * 3 + j)
        r = (16 + 26 * ph) * s
        op = u * (1 - ph) ** 1.3 * .75
        pts = ellipse_pts(x, y, r, r * .8, 12)
        o.append(f'<g opacity="{op:.3f}">' + shape(pts, "#c9cdd2", blob(ellipse_pts(x + r * .25, y + r * .25, r * .6, r * .45, 10), "#aeb3ba", .7),
                                                     w=2.4 * s, seed=8800 + j + seed, ink_color="#7d838b") + "</g>")
    return "".join(o)


def sparks(p, t, u, n=6, r=60.0, seed=0):
    """Искорки разлетаются из точки (u — сила)."""
    if u <= .02:
        return ""
    fr = int(t * 15)
    o = []
    for j in range(n):
        a = (j * 2.399 + fr * .7 + seed) % (2 * math.pi)
        L = r * (.5 + .5 * ((j * 7 + fr) % 5) / 4)
        x0, y0 = p[0] + math.cos(a) * L * .4, p[1] + math.sin(a) * L * .4
        x1, y1 = p[0] + math.cos(a) * L, p[1] + math.sin(a) * L
        o.append(line([(x0, y0), (x1, y1)], 6 * u, INK, taper=.6, wmin=.3, seed=8900 + j))
        o.append(line([(x0, y0), (x1, y1)], 3.4 * u, PR.C_ZAP, taper=.6, wmin=.3, seed=8910 + j))
    return "".join(o)


def cat_hook(t):
    """Кот на краю столика: держит кружку (кадр 0 — подносит к морде), вздрагивает на разряде, кружка выскальзывает, кувыркается
    и бьётся о столешницу; дальше — пустые лапы, отвисшая челюсть, уши прижаты. -> (svg кота, svg кружки)."""
    x, y = CATP
    k = CAT_K
    if t < T_HIT + .04:
        lift = lerp(.15, .75, clamp(t / max(.05, T_HIT)))
        st = dict(look=(.3 + .5 * t, -.1), ear=4 * math.sin(t * 9), tail=-6 + 22 * math.sin(2 * math.pi * 2.2 * t + .9), flame_e=1.1 + .4 * math.sin(t * 11))
        return PE.cat_mug(x, y, k, t, st, hold=1.0, lift=lift), ""
    a = t - T_HIT
    if t < T_BREAK + .1:
        st = PE.cat_st("startle", tail=18 * math.sin(t * 20) * math.exp(-3 * a) + 10, flame_e=1.8, ear=8 * math.sin(t * 25) * math.exp(-4 * a))
        st["sy"] = 1.06 + .05 * math.exp(-8 * a) * math.sin(a * 40)
        st["drop"] = -.25 * bump(t, T_HIT, .3)
        # лапы ловят кружку в воздухе (поднимаются за ней), не успевают
        cat = CAT.draw(x, y, k, dict(st, paw=.62 + .35 * bump(t, T_HIT + .05, .5), paw_l=.6 + .3 * bump(t, T_HIT + .12, .5), paw_dx=40, paw_l_dx=40), t)
    else:
        st = PE.cat_st("gape", gape_u=min(1.0, (t - T_BREAK) / .12), flame_e=.9, tail=-4 + 6 * math.sin(t * 3))
        st["flat_ears"] = .7
        st["paw"] = .55
        st["paw_l"] = .55
        st["paw_dx"] = 60
        st["paw_l_dx"] = 60
        st["look"] = (-.2, .8)
        cat = CAT.draw(x, y, k, st, t)
    # кружка: из лап подлетает, кувыркается, падает на столешницу
    m0 = PE.cat_mug_at(x, y, k, .75)
    if t < T_BREAK:
        q = (t - T_HIT) / (T_BREAK - T_HIT)
        mx = lerp(m0[0], MUG_LAND[0], q)
        my = lerp(m0[1] + 18 * k, MUG_LAND[1], q * q) - 190 * math.sin(math.pi * q) * (1 - q * .3)
        mug = PR.mug(mx, my, 1.05 * k, rot=-30 - 520 * q, col="red", steam=.6 * (1 - q), t=t)
    else:
        mug = PR.mug_shatter(MUG_LAND[0], MUG_LAND[1], 1.05 * k, clamp((t - T_BREAK) / .45), seed=3)
    return cat, mug


def lab_hook(t, close=False):
    """Мир хука (s01 и s02 — одно место): слои по порядку и точки. -> (svg мира, dict(head, tip, subj))."""
    d = R.lab_room(t, "close" if close else "hook")
    reach, press = press_state(t)
    hu = hair_state(t)
    zu = zap_u(t)
    tw = max(bump(t, T_HIT + .05, .5), bump(t, T_BEAT, .6), bump(t, T_SNOVA + .05, .5))
    if t < T_HIT:
        ex = PE.zapped("calm75", hu, t)
        ex["closed_n"] = .9 * bump(t, .18, .14)
        ex["closed_f"] = ex["closed_n"]
    elif t < T_HIT + .4 or T_BEAT <= t < T_BEAT + .38 or T_SNOVA <= t < T_SNOVA + .4:
        ex = PE.zapped("zap75", hu, t, tw)
    elif t < T_BEAT or (T_SMOKE + .1 < t < T_REACH):
        ex = PE.zapped("dazed75", hu, t, .5 * tw)
        ex["closed_n"] = max(ex.get("closed_n", 0), .9 * bump(t, T_HIT + .62, .16), .9 * bump(t, T_SMOKE + .4, .16))
        ex["closed_f"] = ex["closed_n"]
    else:
        ex = PE.zapped("calm75", hu, t, .4 * tw)
    lean = .03 * math.sin(t * 2.2) - .05 * bump(t, T_HIT, .4) - .05 * bump(t, T_BEAT, .4) - .05 * bump(t, T_SNOVA, .4)
    shrug = .5 * max(bump(t, T_HIT, .35), bump(t, T_BEAT, .35), bump(t, T_SNOVA, .35))
    btop = PR.shock_button_top(*BOX, BOX_K, 0.0, "top", press)
    kw = dict(expr=ex, t=t, lean_add=lean, shrug=shrug, head_add=.04 * math.sin(t * 1.7))
    f_legs = PE.press_at("dima", SX, SY, 1.0, btop, reach, press, layers=("legs",), **kw)
    f_body = PE.press_at("dima", SX, SY, 1.0, btop, reach, press, layers=("pelvis", "arm_f", "body"), **kw)
    f_arm = PE.press_at("dima", SX, SY, 1.0, btop, reach, press, layers=("arm_n",), **kw)
    head = f_body["head"]
    wr = f_arm["wrist"]["n"]
    el = f_arm["elbow"]["n"]
    # провод от коробки к манжете на запястье (качается)
    wx, wy = PR.shock_button_wire(*BOX, BOX_K, 0.0, "top")
    sway = 14 + 30 * max(bump(t, T_HIT, .5), bump(t, T_BEAT, .5), bump(t, T_SNOVA, .5))
    ang = math.degrees(math.atan2(wr[1] - el[1], wr[0] - el[0]))
    wire = PR.cuff_wire((wx, wy), (wr[0] - 8 * math.cos(math.radians(ang)) * 3, wr[1] - 8 * math.sin(math.radians(ang)) * 3), sway=sway, t=t * 1.6, k=.9,
                        seed=1, cuff=True, cuff_rot=ang - 90, sag=120)
    box = PR.shock_button(*BOX, BOX_K, 0.0, press, glow=.35 + .6 * zu + .15 * math.sin(t * 9) ** 2, arc=zu, heat=0.0, t=t, view="top", seed=1)
    v, roll = counter_state(t)
    cnt = PR.drum_counter(*CNT, CNT_K, v, roll, t=t, seed=1)
    cat, mug = cat_hook(t)
    # разряд: молния от кнопки по руке к плечу и голове, сетка по худи, искры
    zz = ""
    if zu > .02:
        zz += PR.zap(btop, wr, t, seed=1, u=zu, w=18, branches=2)
        zz += PR.zap(wr, el, t, seed=2, u=zu, w=16, branches=1)
        zz += PR.zap(el, (head[0] + 30, head[1] + 120), t, seed=3, u=zu * .9, w=14, branches=2)
        zz += PR.zap_net(SX - 60, SY - 520, SX + 150, SY - 120, t, seed=4, u=zu * .85, n=5)
        zz += sparks(btop, t, zu, 7, 90, 1) + sparks((head[0], head[1] - 140), t, zu * .8, 6, 110, 2)
    smoke_u = clamp(.9 * math.exp(-1.5 * t) + max(.9 * decay(t, T_HIT + .1, 1.4) * (t > T_HIT + .1), 1.0 * decay(t, T_SMOKE, 1.2) * (t > T_SMOKE),
                                                   .9 * decay(t, T_SNOVA + .1, 1.2) * (t > T_SNOVA + .1)))
    top_lim = 330.0 if not close else 360.0
    smoke = smoke_puffs(head, 1.0, t, smoke_u, 0, top=top_lim)
    if close and t > T_SMOKE:
        smoke += PR.smoke_rings(head[0] - 60, head[1] - 120, .8, u=clamp((t - T_SMOKE) / .2) * decay(t, T_SMOKE + .4, 1.2) if t > T_SMOKE + .4
                                else clamp((t - T_SMOKE) / .2), t=t - T_SMOKE, seed=5, n=3)
        # выдох облачком у рта
        bu = bump(t, T_SMOKE + .2, .7)
        if bu > .02:
            mx, my = head[0] + 90, head[1] + 70
            smoke += f'<g opacity="{.8 * bu:.3f}">' + shape(ellipse_pts(mx + 50 * (t - T_SMOKE), my - 10 * (t - T_SMOKE), 26 + 40 * (t - T_SMOKE), 18 + 24 * (t - T_SMOKE), 12),
                                                         "#e3e6ea", "", w=2.4, seed=8990, ink_color="#8a9098") + "</g>"
    subj = f_legs["svg"] + f_body["svg"] + box + cnt + cat + mug + f_arm["svg"]
    shadow = cast_shadow(f_body["svg"] + f_arm["svg"]) + cast_shadow(cat, 40, 4, .12)
    world = (d["bg"] + shadow + cnt + d["chair_back"] + d["table_top"] + f_legs["svg"] + d["table_legs"] + d["chair_seat"] + f_body["svg"] + wire + box
             + cat + mug + f_arm["svg"] + zz + smoke)
    # свет: вспышка разряда и мигание лампы
    fl = flicker(t)
    if fl > .01:
        world += f'<rect x="-2000" y="-2000" width="6000" height="6000" fill="#2a2f3a" opacity="{.2 * fl:.3f}"/>'
    if zu > .6:
        world += f'<rect x="-2000" y="-2000" width="6000" height="6000" fill="#fffbe0" opacity="{.35 * (zu - .6) / .4:.3f}"/>'
    return world, dict(head=head, subj=subj)


def hook_frame(t, close):
    lib.dyn_begin()
    world, info = lab_hook(t, close)
    if os.environ.get("MASK"):
        g = '<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>' + mask_svg(info["subj"])
        cx, cy, s = CAM1 if not close else CAM2
        if not close:
            kk, rc, side = hook_cam(t, T_HIT, T_K1)
            s *= kk
            cx += side
        else:
            rc = 0
        return lib.svg(f'<g transform="{lib.cam(cx, cy, s, rc)}">{g}</g>')
    if os.environ.get("NOCAM"):
        cx, cy, s = CAM1 if not close else CAM2
        set_ink(s)
        return lib.svg(f'<g transform="{lib.cam(cx, cy, s)}">{world}</g>')
    if not close:
        cx, cy, s0 = CAM1
        kk, rc, side = hook_cam(t, T_HIT, T_K1)
        sx1, sy1 = shake2(t, T_HIT, 9)
        s = s0 * kk * (1 + .012 * sm(t, .5, 1.6))
        ccx = cx + side - sx1 + 3 * math.sin(t * 2.3)
        ccy = cy - sy1
    else:
        cx, cy, s0 = CAM2
        a = t - T_S02
        z = 1 + .035 * sm(t, T_S02, SHOT["s02"]["t1"])
        z += .06 * math.exp(-6 * max(0.0, t - T_SNOVA)) * (1 if t > T_SNOVA + .03 else max(0.0, t - T_SNOVA) / .03) * (t > T_SNOVA)
        s = s0 * z
        sh = [shake2(t, th, 8) for th in (T_BEAT, T_SNOVA)]
        ccx = cx - sum(p[0] for p in sh) + 2 * math.sin(a * 2.1)
        ccy = cy - sum(p[1] for p in sh) - 10 * sm(t, T_S02, SHOT["s02"]["t1"])
        rc = .4 * math.sin(a * 1.3)
    set_ink(s)
    body = f'<g transform="{lib.cam(ccx, ccy, s, rc)}">{world}</g>'
    fade = 1.0
    return lib.svg(body + HT.hook_text(t, fade=fade))


def s01(t):
    return hook_frame(t, False)


def s02(t):
    return hook_frame(t, True)


# ═════════════════════════ s04: пустой стул, кнопка жмётся сама ═════════════════════════
PRESS_SELF = True             # False — вариант из брифа: кнопка только разгорается (если сама нажимающаяся покажется жуткой)
T4A, T4B = SHOT["s04"]["t0"], SHOT["s04"]["t1"]
T_TOZHE = ws(15)              # «тоже»: кнопка разгорается
T_NAZH = ws(16)               # «нажал»: кнопка щёлкает вниз сама
EB = R.EMPTY_BOX
EB_K = 1.15


def s04(t):
    lib.dyn_begin()
    d = R.lab_room(t, "empty")
    a = t - T4A
    pulse = .5 + .5 * math.sin(2 * math.pi * 1.6 * a + 1.2)
    glow = clamp(.3 + .35 * pulse + .45 * sm(t, T_TOZHE - .05, T_TOZHE + .2) + .3 * bump(t, T_NAZH, .4))
    press = 0.0
    hop = 0.0
    if PRESS_SELF:
        press = sm(t, T_NAZH - .04, T_NAZH) * (1 - sm(t, T_NAZH + .22, T_NAZH + .36))
        hop = 26 * bump(t, T_NAZH + .02, .26)
    arc = clamp(1 - (t - T_NAZH) / .35) if (PRESS_SELF and t >= T_NAZH) else .25 * sm(t, T_TOZHE, T_TOZHE + .2) * (.5 + .5 * math.sin(t * 23))
    bx, by = EB
    # красный свет кнопки на стене за ней и на сиденье стула
    gl = lib.rad_grad([(0, "#ff5a48", .55 * glow), (.5, "#ff7a5a", .22 * glow), (1, "#ff8a6a", 0)], bx, by - 60 * EB_K, 420 + 160 * glow)
    light = f'<circle cx="{bx:.1f}" cy="{by - 60 * EB_K:.1f}" r="{420 + 160 * glow:.1f}" fill="url(#{gl})"/>'
    # провод: из коробки вниз по тумбе к сиденью стула, на сиденье пустая манжета
    cx, cy = R.EMPTY_CHAIR
    wx, wy = PR.shock_button_wire(bx, by, EB_K, 0.0, "face")
    seat_y = R.EMPTY_FL - 380 - hop
    wire = PR.cuff_wire((wx, wy), (cx + 70, seat_y - 30), sway=10 + 20 * bump(t, T_NAZH, .5), t=t * 1.4, k=1.0, seed=4, cuff=True, cuff_rot=80, sag=150)
    btn = PR.shock_button(bx, by, EB_K, 0.0, press, glow=glow, arc=arc, heat=0.0, t=t, view="face", seed=4)
    chair = R.chair_front(cx, R.EMPTY_FL, 1.0, hop)
    top = PR.shock_button_top(bx, by, EB_K, 0.0, "face", press)
    fx = ""
    if PRESS_SELF and t >= T_NAZH:
        fx += sparks(top, t, clamp(1 - (t - T_NAZH) / .3), 8, 120, 4)
        fx += smoke_puffs((top[0] + 20, top[1] + 170), .9, t, clamp((t - T_NAZH) / .15) * decay(t, T_NAZH + .2, 1.2), seed=4)
    motes = R.motes(t, (cx - 300, 300, bx + 200, 1100), n=18, u=.9, seed=4)
    beam = (f'<path d="M{cx - 520:.0f} 120L{cx - 260:.0f} 120L{bx + 260:.0f} 1560L{cx - 80:.0f} 1560Z" fill="#fff6dc" opacity=".16"/>')
    world = d["bg"] + beam + light + d["table_top"] + chair + wire + btn + fx + motes
    if os.environ.get("NOCAM"):
        set_ink(1.45)
        return lib.svg(f'<g transform="{lib.cam(2540, 1000, 1.45)}">{world}</g>')
    u = sm(t, T4A - .2, T4B + .2)
    s = lerp(1.45, 1.62, u) * (1 + .06 * decay(t, T_NAZH, 6) * (t > T_NAZH))
    sx, sy = shake2(t, T_NAZH, 9)
    ccx = lerp(2540, 2610, u) - sx
    ccy = lerp(1000, 990, u) - sy
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(ccx, ccy, s, .6 * math.sin(t * 1.1))}">{world}</g>')


# ═════════════════════════ s07: вдоль провода к старому аппарату ═════════════════════════
T7A, T7B = SHOT["s07"]["t0"], SHOT["s07"]["t1"]
T_TEP = ws(33)                # «теперь»: камера уходит вдоль провода
T_OTK = ws(35)                # «откуда»: полёт над кампусом
T_KNP = ws(37)                # «кнопка»: провод упирается в старый аппарат
DOOR7 = (1500.0, 1700.0)      # дверь в белой комнате (x0, x1), щель под ней — на полу
SLIT = (1600.0, R.FL - 6.0)


def _wire7_pts():
    """Провод в мире белой комнаты: из коробки вниз со стола, по полу вправо, в щель под дверью."""
    wx, wy = PR.shock_button_wire(*BOX, BOX_K, 0.0, "top")
    return [(wx, wy), (wx - 40, wy + 60), (R.LAB_TABLE[0] - 10, R.LAB_TOP + 40), (R.LAB_TABLE[0] - 20, R.LAB_TOP + 300), (R.LAB_TABLE[0] + 40, R.FL + 30),
            (800, R.FL + 70), (1100, R.FL + 50), (1400, R.FL + 20), SLIT]


def _room7(t):
    P = R.LAB
    o = R._room_shell(P, seed=7, corner=None)
    x0, x1 = DOOR7
    door = shape(rect_pts(x0, 560, x1, R.FL - 14), "#dfe3e2", blob(rect_pts(x1 - 40, 560, x1, R.FL - 14), "#c3c9c8", .8)
                 + shape(ellipse_pts(x0 + 30, 1060, 12, 12, 10), "#9aa0a8", "", w=2.4, seed=7071), w=3.6, seed=7070)
    door = shape(rect_pts(x0 - 26, 534, x1 + 26, R.FL - 8), "#eef0ee", "", w=3.4, seed=7069) + door
    slit = blob(rect_pts(x0, R.FL - 14, x1, R.FL - 2), "#0c1020")
    tb = R.lab_table(*R.LAB_TABLE, R.LAB_TOP, P)
    wire = PR.cable(_wire7_pts(), w=8, seed=7072)
    box = PR.shock_button(*BOX, BOX_K, 0.0, 0.0, glow=.3 + .2 * math.sin(t * 5) ** 2, t=t, view="top", seed=7)
    return o + door + slit + tb["top"] + tb["legs"] + wire + box


def _along(pts, u):
    """Точка на ломаной при доле длины u."""
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    d = u * L[-1]
    for i in range(len(pts) - 1):
        if d <= L[i + 1]:
            q = (d - L[i]) / max(1e-6, L[i + 1] - L[i])
            return pts[i][0] + (pts[i + 1][0] - pts[i][0]) * q, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * q
    return pts[-1]


def s07(t):
    lib.dyn_begin()
    t_dark = T_OTK - .06
    t_lab = T_KNP - .14
    if t < t_dark:
        world = _room7(t)
        if t < T_TEP:
            u = 0.0
        else:
            u = ease_in(clamp((t - T_TEP) / (t_dark - T_TEP)), 1.7)
        p0 = (BOX[0] + 10, BOX[1] - 60)
        pw = _along(_wire7_pts(), u)
        cx = lerp(p0[0], pw[0], min(1.0, u * 3)) if u < .34 else pw[0]
        cy = lerp(p0[1], pw[1], min(1.0, u * 3)) if u < .34 else pw[1] - 40 * (1 - u)
        s = 2.1 * (1 + .03 * (t - T7A)) if u <= 0 else lerp(2.1, 1.25, sm(u, 0, .35)) if u < .6 else lerp(1.25, 9.0, ease_in(clamp((u - .6) / .4), 2.4))
        rot = 2 * math.sin(t * 1.3) + 6 * sm(u, .3, .9)
        body = f'<g transform="{lib.cam(cx, cy, s, rot)}">{world}</g>'
        dk = sm(u, .93, 1.0)
        if dk > 0:
            body += f'<rect x="0" y="0" width="1080" height="1920" fill="#0a1020" opacity="{dk:.3f}"/>'
        set_ink(min(s, 3.0))
        return lib.svg(body)
    if t < t_lab:
        u = (t - t_dark) / (t_lab - t_dark)
        bg = R.campus_night(t, u * 1.4)
        wp = R.CAMPUS_WIRE(u * 1.4, t)
        wire = line(wp, 26, '#7f95d8', taper=.0, wmin=1, seed=7081, op=.35) + PR.cable(wp, w=18, seed=7080)
        rot = -4 * math.sin(math.pi * u) + 2 * u
        body = f'<g transform="rotate({rot:.2f} 540 960) scale(1.08) translate(-40 -60)">{bg}{wire}</g>'
        fade = 1 - clamp((t - t_dark) / .08)
        if fade > 0:
            body += f'<rect x="0" y="0" width="1080" height="1920" fill="#0a1020" opacity="{fade:.3f}"/>'
        set_ink(1.0)
        return lib.svg(body)
    # старая лаборатория: провод снизу к клемме аппарата, стрелка дёргается, тумблер щёлкает, лампа качается
    a = t - t_lab
    swing = 9 * math.exp(-1.2 * a) * math.cos(2 * math.pi * .7 * a) + 3 * math.sin(t * 1.4)
    d = R.old_lab(t, swing)
    ax, ay = R.OLD_APP
    k = 1.7
    needle = -.8 + 1.5 * sm(t, T_KNP, T_KNP + .08) + damp(t, T_KNP + .08, .35, 4.0, 5.0) + .05 * math.sin(t * 13)
    sw = sm(t, T_KNP + .05, T_KNP + .1)
    app = PR.shock_box_old(ax, ay, k, needle=needle, switch=sw, t=t, seed=7)
    tx, ty = PR.shock_box_old_wire(ax, ay, k)
    wire = PR.cable([(-60, 1980), (120, 1700), (260, 1380), (tx - 120, ty + 60), (tx, ty)], w=10, seed=7090)
    fx = sparks((tx, ty), t, clamp(1 - (t - T_KNP) / .25), 6, 70, 7) if t >= T_KNP else ""
    world = d["bg"] + d["light"] + d["table"] + wire + app + fx + d["lamp"]
    s = lerp(1.35, 1.0, ease_out(clamp(a / .45), 3)) * (1 + .05 * decay(t, T_KNP, 6) * (t > T_KNP))
    sx_, sy_ = shake2(t, T_KNP + .05, 6)
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(ax - sx_ - 30 * (1 - clamp(a / .45)), ay - 230 - sy_, s, -3 * (1 - ease_out(clamp(a / .45), 3)))}">{world}</g>')


def ease_in(u, p=2.0):
    return clamp(u) ** p


# ═════════════════════════ s17: у окна ═════════════════════════
T17A, T17B = SHOT["s17"]["t0"], SHOT["s17"]["t1"]
T_PYAT = ws(92)
T_MIN_E = we(93)
T_SMOT = ws(94)               # «смотрит»: выдох, плечи опускаются
T_OKNO = ws(96)               # «окно»: оба чуть наклоняют головы


def s17(t):
    lib.dyn_begin()
    warm = sm(t, T17A, T17B)
    shift = 40 * (t - T17A) + 260 * sm(t, T_PYAT - .05, T_MIN_E + .05) + 600
    d = R.window_day(t, cloud_shift=shift, warm=warm)
    tilt = 7 * sm(t, T_OKNO - .05, T_OKNO + .3) + 1.2 * math.sin(t * 1.3)
    shrug = .35 * (1 - sm(t, T_SMOT, T_SMOT + .45)) + .05 * math.sin(t * 2.2)
    br = 1 + .01 * math.sin(2 * math.pi * t / 3.0)
    dx, dy = R.WD_DIMA
    dima = PE.dima_back(dx - 10, dy + 330, 2.05, tilt=-tilt, look_up=.04 + .06 * sm(t, T_OKNO, T_OKNO + .4), shrug=shrug, hair=0.0, t=t)
    dsvg = f'<g transform="translate({dx} {dy + 900}) scale(1 {br:.4f}) translate({-dx} {-dy - 900})">{dima["svg"]}</g>'
    # выдох облачком у плеча
    pu = bump(t, T_SMOT + .1, .8)
    puff = ""
    if pu > .02:
        q = t - T_SMOT - .1
        puff = f'<g opacity="{.6 * pu:.3f}">' + shape(ellipse_pts(dx + 200 + 60 * q, dy - 40 - 20 * q, 30 + 40 * q, 20 + 26 * q, 12), "#f4f6f8", "", w=2.4,
                                                     seed=1701, ink_color="#9aa0a8") + "</g>"
    cx, cy = R.WD_CAT
    st = PE.cat_st("window", turn=.6, look=(.95, -.95), tilt=8 * sm(t, T_OKNO - .02, T_OKNO + .3) + 2 * math.sin(t * 1.7), tail=-4 + 10 * math.sin(t * 2.3),
                   ear=3 * math.sin(t * 2.9), blink=.9 * bump(t, T_SMOT + .3, .16) + .15)
    cat = CAT.draw(cx, cy, 1.0, st, t)
    world = d["bg"] + cat + d["sill"] + dsvg + puff
    if os.environ.get("NOCAM"):
        set_ink(1.0)
        return lib.svg(f'<g transform="{lib.cam(560, 960, 1.0)}">{world}</g>')
    u = sm(t, T17A - .2, T17B + .2)
    s = lerp(1.0, 1.07, u)
    set_ink(s)
    tint = f'<rect x="0" y="0" width="1080" height="1920" fill="#ffb860" opacity="{.07 * warm:.3f}"/>'
    return lib.svg(f'<g transform="{lib.cam(lerp(560, 600, u), lerp(960, 930, u), s)}">{world}</g>' + tint)


# ═════════════════════════ s18: петля ═════════════════════════
T18A = SHOT["s18"]["t0"]
T_IDEI = ws(98)
T_PRIH = ws(99)
T_SAMI = ws(100)
IDEAS = ((40, -250, .9, 0.0), (-150, -150, .55, .0), (190, -170, .6, .12), (-60, -350, .5, .24), (150, -330, .5, .36))


def s18(t):
    lib.dyn_begin()
    dr = 1 - sm(t, T_SAMI, T_SAMI + .35)
    d = R.room_day(t, "hook", drawer=dr)
    knee = bump(t, T_SAMI - .05, .5)
    feet = PE.sit_kw(SX, SY, 1.0)["feet"]
    (nx, ny), nphi = feet["n"]
    feet = dict(feet)
    feet["n"] = ((nx + 30 * knee, ny), nphi)
    ex = dict(PE.EXPR["dima"]["window75"])
    ex["closed_n"] = .9 * bump(t, T_PRIH + .25, .16)
    ex["closed_f"] = ex["closed_n"]
    ex["smile"] = .3 + .3 * sm(t, T_IDEI, T_IDEI + .4)
    rest = {"n": ("ik", (SX + 250 + 20 * knee, SY - 40), -1), "f": ("ik", (SX + 215, SY - 45), -1)}
    hands = {"n": {"curl": (.35, .4, .45, .5), "thumb": .3, "dir": (1, .35)}, "f": {"curl": (.35, .4, .45, .5), "thumb": .3}}
    kw = dict(expr=ex, feet=feet, arms=rest, hands=hands, lean_add=.02 * math.sin(t * 1.4) - .03 * knee, head_add=-.06 + .03 * math.sin(t * 1.1))
    legs = PE.dima(SX, SY, 1.0, layers=("legs",), **kw)
    body = PE.dima(SX, SY, 1.0, layers=("pelvis", "arm_f", "body", "arm_n"), **kw)
    head = body["head"]
    # кнопка в ящике (пока он открыт)
    ins = ""
    if d["inside"]:
        x0, y0, x1, y1 = d["inside"]
        c = lib.clip_rect(x0, y0 - 14, x1 - x0, y1 - y0 + 14)
        ins = f'<g clip-path="url(#{c})">' + PR.shock_button((x0 + x1) / 2 + 10, y1 + 2, .3, -6, 0.0, glow=0.0, t=t, view="top", seed=18) + "</g>"
    # кот отпивает из целой кружки и смотрит в окно
    lift = bump(t, T_SAMI - .1, 1.1) + .15
    st = PE.cat_st("window", tail=-4 + 10 * math.sin(t * 2.1), ear=3 * math.sin(t * 2.7), flame_e=1.2 + .2 * math.sin(t * 6))
    cat = PE.cat_mug(*CATP, CAT_K, t, st, hold=1.0, lift=clamp(lift), steam=1.0)
    ideas = ""
    for i, (ox, oy, kk, dt) in enumerate(IDEAS):
        t0 = (T_IDEI if i == 0 else T_PRIH) + dt
        if t < t0:
            continue
        u = PR.back_out(clamp((t - t0) / .3)) if hasattr(PR, "back_out") else lib.back_out(clamp((t - t0) / .3))
        fx = head[0] + ox + 14 * math.sin(t * 1.3 + i)
        fy = head[1] + oy + 10 * math.sin(t * 1.7 + 2 * i)
        ideas += PR.idea_spark(fx, fy, kk, u, t, seed=18 + i)
    world = (d["bg"] + d["chair_back"] + d["table_top"] + ins + d["drawer_front"] + legs["svg"] + d["table_legs"] + d["chair_seat"] + body["svg"]
             + cat + ideas)
    cx, cy, s0 = CAM1
    if os.environ.get("NOCAM"):
        set_ink(s0)
        return lib.svg(f'<g transform="{lib.cam(cx, cy, s0)}">{world}</g>')
    s = s0 * (1 + .03 * sm(t, T18A - .2, SH["end"]))
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(cx + 2 * math.sin(t * .9), cy - 8 * sm(t, T18A - .2, SH["end"]), s)}">{world}</g>')


def frame(sid, t):
    return {"s01": s01, "s02": s02, "s04": s04, "s07": s07, "s17": s17, "s18": s18}[sid](t)
