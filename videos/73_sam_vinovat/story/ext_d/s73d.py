"""Рилс 73 «Ты сам виноват», группа D — кот крупно:
s04 (холодный вызов: кот наклоняется к зрителю у доски, удар сердца 4.45, «нравится» — наклон головы, бровь-складка, ухо дёргается,
хвост бьёт), s09 (второй поворот: щёлкает ночник, тёплый кот запрыгивает на кровать, «неправда» — хвостом рассыпает клубок-мозг,
тень судьи тает), s12 (кот садится рядом с камерой, обвивает лапы хвостом; «минуты» — ставит лапой чашку чая на тумбочку, пар).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Общие помощники (камера, слова, «плечо» над вытянутой лапой) — из ext_c/s73c.
Места — common/room.py, кот — common/cat.py (+ people.cat_jump), предметы — common/props.py, Дима — common/people.py. Букв и цифр нет."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "ext_c"))
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people as PP  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
import s73c as C  # noqa: E402
from lib import blob, clamp, ease_io, ease_out, ellipse_pts, line, rect_pts  # noqa: E402,F401
from s73c import bump, damp, lerp, set_ink, sm, wt  # noqa: E402


def cam_map(cx0, cy0, s0):
    def Wm(fx, fy):
        return cx0 + (fx - 540) / s0, cy0 + (fy - 960) / s0
    return Wm


# ═════════════════════════ s04: холодный вызов ═════════════════════════
CAM4 = (-950.0, 675.0, 2.4)
W4 = cam_map(*CAM4)
T_BEAT4 = 4.45
T_NE = wt("не", 5.0)             # 5.11
T_NRA = 5.25                      # ударный «нра»


def s04_cat(t):
    st = dict(_t=t, cold=1.0)
    lean = ease_out(clamp((t - 4.28) / .6), 3)                       # кадр 0 — уже наклоняется (скорость с кадра 0)
    ch = sm(t, T_NE - .05, T_NE + .3)                                 # «Не нравится?» — вызов: наклон головы, бровь-складка
    st["smug"] = .7 * ch
    st["tilt"] = -2 + 4 * (1 - lean) - 10 * ch + 1.2 * math.sin(t * 1.9) + damp(t, T_NRA, -2.5, 3, 6)
    st["turn"] = .05 * math.sin(t * 1.3) - .1 * ch
    st["look"] = (0.0, .05)
    st["drop"] = .18 * lean - .06 * ch
    st["ear"] = damp(t, T_NRA, 16, 5, 6) + damp(t, T_BEAT4, 6, 5, 7) + 3 * math.sin(t * 6.1)
    st["tail"] = -28 + 4 * math.sin(t * 2.6) + 20 * bump(t, T_NRA - .12, .3)       # хвост хлещет вниз на «нра»
    st["flame_e"] = .8 + .2 * math.sin(t * 9)
    st["rot"] = -1.5 * (1 - lean) + .6 * math.sin(t * 1.1)
    hb = R.heart_k(t, T_BEAT4)
    st["sy"] = 1 - .02 * hb
    return st, lean


def s04(t):
    lib.dyn_begin()
    st, lean = s04_cat(t)
    kf = 3.95 + .45 * lean                                             # приближается к зрителю
    cx, cy = W4(540, 1760)
    k = kf / CAM4[2]
    bc = R.board_close(t, "cold")
    # конверт на доске за котом справа вверху — дёргается на ударе сердца
    hb = R.heart_k(t, T_BEAT4)
    ex, ey = W4(985, 300)
    sw = 4 * math.sin(2 * math.pi * 1.2 * t) + damp(t, T_BEAT4, 9, 2.4, 3) + damp(t, T_NRA, 5, 2.4, 3)
    env = PR.pinned_envelope(ex, ey - 10 * hb, 1.5 / CAM4[2] * 1.6, swing=sw, dust=1.0, web=1.0, t=t, seed=74)
    cat = R.cold_tint(PP.cat_svg(cx, cy, k, st, t), .7)
    # хвост бьёт по полу: короткие штрихи удара и пыль у кончика
    hit = ""
    if t > T_NRA:
        hit = PR.dust_puff(*W4(900, 1600), .9, clamp((t - T_NRA) / .45), seed=75)
    world = [bc["bg"], R.cold_tint(env, .8), C.shelf(1760), cat, R.cold_tint(hit, .6)]
    cx0, cy0, s0 = CAM4
    push = .06 * sm(t, 4.28, 6.0)
    s = s0 * (1 + push) * (1 + .02 * hb)
    fx, fy = W4(540, 760)
    ccx = lerp(cx0, fx, push / .06 * .5) + 3 * math.sin(t * 1.7)
    ccy = lerp(cy0, fy, push / .06 * .5)
    set_ink(s)
    body = f'<g transform="{lib.cam(ccx, ccy, s)}">{"".join(world)}</g>' + R.heart_pulse(t, T_BEAT4, 1.0)
    return lib.svg(body)


# ═════════════════════════ s09: ночник, тёплый кот на кровати, клубок рассыпается ═════════════════════════
CAM9 = (1780.0, 900.0, 1.35)
T_NO = wt("но", 11.0)            # 11.61 — щёлк ночника
T_ETO = wt("это", 11.0)          # 12.31 — кот поднимает голову к клубку
T_NPR = 12.70                    # ударный «прав» — хвост рассыпает клубок
T_JUMP = (T_NO + .12, T_NO + .62)
CAT9_FLOOR = (1400.0, R.FL73 - 4)
CAT9_BED = (1520.0, R.BED73_TOP + 8)
BRAIN9 = (1700.0, 560.0)
K9 = 1.0


def s09_cat(t):
    """Состояние кота и где он: до прыжка — на полу (присел, смотрит вверх), прыжок, на кровати — к клубку, взмах хвостом."""
    st = dict(_t=t, blink=.22, smile=1.0, perk=.4, flame_e=1.3 + .4 * sm(t, T_NO, T_NO + .2) + 1.0 * bump(t, T_NPR - .05, .4))
    up = sm(t, T_ETO - .05, T_ETO + .2)
    st["look"] = (.35 * up, -.2 - .8 * up)
    st["tilt"] = -6 * up + 2 * math.sin(t * 2.1)
    st["ear"] = 4 * math.sin(t * 3.3) + damp(t, T_JUMP[1], 8, 4, 6)
    # взмах хвостом: замах назад и резкий хлёст вверх к клубку на «прав»
    st["tail"] = -10 + 6 * math.sin(t * 2.4) + 25 * sm(t, T_NPR - .3, T_NPR - .1) - 70 * (sm(t, T_NPR - .1, T_NPR + .02) - sm(t, T_NPR + .2, T_NPR + .6) * 0)
    st["tail"] += 50 * sm(t, T_NPR + .2, T_NPR + .6)
    return st


def s09(t):
    lib.dyn_begin()
    lu = ease_out(clamp((t - T_NO) / .15), 2)          # ночник: 4–5 кадров
    bd = R.bedroom(t, lu, "bed", lamp_u=lu)
    P = bd["P"]
    dm = PP.dima_bed(1640, R.BED73_TOP + 6, .52, "awake73", t=t, flip=True, cover=.3, seed=73)
    st = s09_cat(t)
    if t < T_JUMP[0]:
        st2 = dict(st, perk=.6)
        st2["sy"] = 1 - .08 * sm(t, T_NO - .1, T_JUMP[0])
        cat = PP.cat_svg(*CAT9_FLOOR, K9, st2, t)
    elif t < T_JUMP[1]:
        u = (t - T_JUMP[0]) / (T_JUMP[1] - T_JUMP[0])
        cat = PP.cat_jump(CAT9_FLOOR, CAT9_BED, K9, u, t, st)
    else:
        st["sy"] = 1 - .05 * damp(t, T_JUMP[1], 1, 3, 6)
        cat = PP.cat_svg(*CAT9_BED, K9, st, t)
    warm = lu
    cat = R.warm_tint(R.cold_tint(cat, 0.0, .5 * (1 - warm)), .5 * warm)
    # клубок-мозг под потолком над Димой: прищуренные глазки; на «прав» рассыпается искрами
    burst = clamp((t - T_NPR) / .55)
    brain = PR.brain_scribble(*BRAIN9, 1.25, 1.0, eyes=max(0.0, 1 - 2.5 * burst), burst=burst, t=t, seed=73)
    # тень судьи на стене над кроватью (линия) — тает со светом и на рассыпании
    sh_op = (1 - .5 * lu) * (1 - sm(t, T_NPR, T_NPR + .45))
    shadow = ""
    if sh_op > .02:
        shadow = f'<g opacity="{sh_op:.3f}">' + PP.cat_judge_shadow(1450, 820, .8, dict(cold=1.0), t, col="#93a6d6", w=5) + "</g>"
    dima = R.warm_tint(R.cold_tint(dm["svg"], 0.0, .55 * (1 - warm)), .4 * warm)
    world = [bd["bg"], shadow, bd["pillow"], dima, cat, brain]
    cx0, cy0, s0 = CAM9
    s = s0 * (1.07 - .07 * ease_out(clamp((t - T_NO) / .6), 2)) * (1 + .06 * bump(t, T_NPR, .35))
    sx1, sy1 = C.shake2(t, T_NPR, 8)
    set_ink(s)
    body = f'<g transform="{lib.cam(cx0 - sx1, cy0 - sy1 - 30 * up_cam(t), s)}">{"".join(world)}</g>'
    if t < T_NO:      # перед щелчком — ночная темнота
        body += '<rect width="1080" height="1920" fill="#03050d" opacity=".35"/>'
    return lib.svg(body)


def up_cam(t):
    return sm(t, T_ETO, T_ETO + .3)


# ═════════════════════════ s12: кот садится у камеры, чашка чая ═════════════════════════
CAM12 = (2000.0, 1060.0, 1.5)
W12 = cam_map(*CAM12)
T_RYA = wt("рядом", 16.0)         # 16.23
T_MIN = wt("минуты", 16.0)        # 16.89
CAT12_F = (450.0, 1290.0, 2.5)    # кадр: точка между задних лап, масштаб рисунка в кадре (кот ≈ 50 % высоты)
CUP_F = (830.0, 1172.0)           # кадр: дно блюдца на тумбочке


def s12_cat(t):
    st = dict(_t=t, smile=1.0, look=(0.0, 0.0), perk=.35, flame_e=1.2 + .7 * sm(t, T_RYA, T_RYA + .3) + .2 * math.sin(t * 8))
    bl = .12 + .85 * bump(t, 16.55, .5) + .85 * bump(t, 17.3, .45)        # медленное моргание
    st["blink"] = clamp(bl)
    st["tail"] = lerp(8, -26, ease_io(clamp((t - 16.0) / .45))) + 2 * math.sin(t * 2)    # обвивает лапы хвостом
    st["tilt"] = 2.5 * math.sin(t * 1.6) + 4 * bump(t, T_MIN, .5)
    st["ear"] = 4 * math.sin(t * 2.7)
    # лапа (правая передняя, та же) подвигает чашку к краю тумбочки на «минуты» и возвращается на место
    a = T_MIN - .28
    pw = 0.0
    if t > a:
        pw = .37 * ease_out(clamp((t - a) / .22), 2) if t < T_MIN else .37 * (1 - ease_io(clamp((t - T_MIN - .12) / .3)))
    st["paw"] = pw
    st["paw_dx"] = 208.0
    return st


def s12(t):
    lib.dyn_begin()
    bd = R.bedroom(t, "lamp", "cam")
    st = s12_cat(t)
    # кот подходит (шаг) и садится: до 16.0 идёт слева, 16.0–16.2 садится
    fx, fy, kf = CAT12_F
    walk_u = clamp((t - 15.85) / .3)
    fx_t = lerp(fx - 170, fx, ease_out(walk_u, 2))
    cx, cy = W12(fx_t, fy)
    k = kf / CAM12[2]
    if t < 16.15:
        st2 = dict(st, walk=(t - 15.85) / .45 * 1.0, paw=0.0)
        st2["sy"] = 1 + .03 * math.sin(t * 20)
        cat = PP.cat_svg(cx, cy - 8 * abs(math.sin(math.pi * (t - 15.85) / .225)), k, st2, t)
    else:
        st["sy"] = 1 - .05 * damp(t, 16.15, 1, 3, 6) - .015 * bump(t, T_RYA, .4)
        cat = PP.cat_svg(cx, cy, k, st, t) + C.shoulder_patch(cx, cy, k, st, t)
    cat = R.warm_tint(cat, .6)
    # чашка: стоит у края; лапа подвигает её на место на «минуты», звяк; пар поднимается
    cu = ease_out(clamp((t - (T_MIN - .06)) / .18), 2)
    ux, uy = CUP_F
    cupx = lerp(ux - 70, ux, cu) + damp(t, T_MIN + .12, 3, 4, 7)
    wx, wy = W12(cupx, uy)
    cup = PR.tea_cup(wx, wy, .95, steam=sm(t, T_MIN, T_MIN + .4) * .9 + .1, t=t, seed=73)
    clink = PR.clink(*W12(ux - 40, uy - 150), .8, clamp((t - T_MIN) / .3), seed=73) if t > T_MIN else ""
    # Дима на кровати позади — размыт (сидит)
    dm = PP.dima_bed(1720, R.BED73_TOP + 6, .55, "smile73", sit=1.0, t=t, flip=True, seed=74)
    dima = f'<g {lib.blur(7)} opacity=".9">{R.warm_tint(dm["svg"], .6)}</g>'
    # край кровати на переднем плане, где сидит кот
    bx0, by0 = W12(-100, fy - 6)
    bx1, by1 = W12(720, 2000)
    bedfront = (blob(rect_pts(bx0, by0, bx1, by1), "#a8584a")
                + line([(bx0, by0 + 4), (bx1, by0 + 4)], 4, "#5a2a22", taper=0, wmin=1, seed=7601)
                + "".join(line([(bx0 + 120 * i, by0 + 30), (bx0 + 120 * i + 8, by1)], 3, "#8a4438", taper=.3, wmin=.5, seed=7602 + i) for i in range(7)))
    world = [bd["bg"], bd["blanket"], bd["pillow"], dima, R.warm_tint(cup + clink, .3), bedfront, cat]
    cx0, cy0, s0 = CAM12
    hx, hy = W12(fx, 620)
    push = .04 * sm(t, 15.85, 17.6)
    s = s0 * (1 + push)
    ccx, ccy = lerp(cx0, hx, push / .04 * .4), lerp(cy0, hy, push / .04 * .4)
    set_ink(s)
    body = f'<g transform="{lib.cam(ccx, ccy, s)}">{"".join(world)}</g>'
    pl = bump(t, T_RYA, .5)
    if pl > .01:
        body += f'<rect width="1080" height="1920" fill="#ffc870" opacity="{.06 * pl:.3f}" style="mix-blend-mode:screen"/>'
    return lib.svg(body)


def frame(sid, t):
    return {"s04": s04, "s09": s09, "s12": s12}[sid](t)
