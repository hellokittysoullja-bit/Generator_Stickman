"""Рилс 73 «Ты сам виноват», группа C — хук, поворот, петля:
s01 (хук: холодный кот-судья крупно перед пробковой доской уже на середине поворота головы, пыльный конверт качается на кнопке,
паучок раскачивается; «Если» — голова встаёт на зрителя, уши прижаты; «дело» — коготь стукает по конверту, пыль; «висит» —
паучок падает на нитке; «месяц» — паутина дрожит, глаза в щёлки),
s06 (поворот: белый всполох-сбой, темнота, часы на трёх двенадцати, удар сердца 7.30, проезд к кровати, тень судьи на потолке),
s17 (петля тем же ракурсом, что s01, в тёплом свете ночника: коготь снимает старую карточку с кнопки, тёплый кивок).
frame(sid, t) -> SVG 1080×1920, t — общее время ролика. Места — common/room.py, кот — common/cat.py, предметы — common/props.py,
Дима — common/people.py. Букв и цифр нет. NOCAM=1 — без камеры (замер движения рисунка), MASK=face|env|both — силуэт для замера."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from lib import INK, blob, clamp, ease_io, ease_out, ellipse_pts, line, rect_pts, shape  # noqa: E402,F401

WORDS = json.load(open(os.path.join(STORY, "voice", "words.json")))


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["word"].strip(",.!?«»:").lower() == word:
            return w["start"]
    raise KeyError(word)


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


def shake2(t, t0, amp, k=9.0, fr=19.0):
    def dec(tt):
        if tt < 0:
            return 0.0
        return math.exp(-k * tt) * math.sin(2 * math.pi * fr * tt)
    return amp * dec(t - t0), amp * .7 * dec(t - t0 - .013)


def set_ink(s):
    lib.INK_K[0] = 1.0 / max(1.0, s) ** 0.62


def hook_cam(t, t_hit, t_hit2, rot0=3.8, side0=-60.0):
    """Влёт правил 28/29: с 40 % дальше (1/(1+0.4)) за 0.22 с, перелёт с отскоком, поворот rot0 с возвратом, занос сбоку;
    удар +8 % на ударном слоге t_hit2 и поменьше на t_hit. Возвращает (масштаб-множитель, поворот, занос)."""
    u = clamp(t / .22)
    e = ease_out(u, 3)
    s = 1 / 1.4 + (1 - 1 / 1.4) * e
    if t > .22:
        s += .06 * math.exp(-7 * (t - .22)) * math.sin(2 * math.pi * 2.2 * (t - .22) + math.pi / 2)
    rot = rot0 * (1 - e) + damp(t, .22, -1.2, 2.0, 6.0)
    side = side0 * (1 - e)
    hit = 0.0
    for th, a in ((t_hit, .04), (t_hit2, .08)):
        if t > th:
            h = t - th
            hit += a * math.exp(-5.5 * h) * (1 if h > .03 else h / .03)
    return s * (1 + hit), rot, side


def mask_svg(svg, kind):
    """Силуэт для замера: всё нарисованное — сплошным цветом (face — красный, env — синий)."""
    col = "1 0 0" if kind == "face" else "0 0 1"
    fid = f"mk{kind}"
    if not any(f'id="{fid}"' in d for d in lib.DEFS):
        r, g, b = col.split()
        lib.DEFS.append(f'<filter id="{fid}"><feColorMatrix type="matrix" values="0 0 0 0 {r} 0 0 0 0 {g} 0 0 0 0 {b} 0 0 0 9 0"/></filter>')
    return f'<g filter="url(#{fid})">{svg}</g>'


# ═════════════════════════ кот: голова в системе рисунка cat.draw ═════════════════════════
def head_tf(x, y, k, st, t):
    """Тот же переход, что у головы в cat.draw: мир ← рисунок (единицы кота 384 в высоту)."""
    sl = st.get("sleep", 0.0)
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1) * (1 + 1.5 * sl)
    sy = br * (1 - .2 * sl) * st.get("sy", 1.0)
    hy = -(sy - 1) * (CAT.CBOT - CAT.NECK[1]) + 34 * sl + 70 * st.get("drop", 0.0)
    tilt = st.get("tilt", 0.0) + 16 * sl
    return (f'translate({x:.2f} {y:.2f}) rotate({st.get("rot", 0.0):.2f}) scale({k:.4f}) translate({-CAT.CX} {-CAT.CBOT}) '
            f'translate({22 * sl:.2f} {hy:.2f}) rotate({tilt:.2f} {CAT.NECK[0]} {CAT.NECK[1]})')


def face_mask(x, y, k, st, t):
    return mask_svg(f'<g transform="{head_tf(x, y, k, st, t)}">{CAT.head(st, t)}</g>', "face")


def judge_face(st, slit=1.0, flat_mouth=1.0):
    """Холод судьи поверх головы кота (в единицах рисунка кота): узкие вертикальные зрачки-щёлки под веком и прямой рот.
    slit 0…1 — насколько зрачок сужен (1 — щёлка), flat_mouth — прямой рот вместо «w». Облик кота тот же (cat.head рисует всё
    остальное); тут только перекрашиваются зрачки и рот."""
    if slit < .02 and flat_mouth < .02:
        return ""
    turn = st.get("turn", 0.0)
    lx, ly = st.get("look", (0.0, 0.0))
    FX = 22 * turn
    CXH = CAT.CX + FX
    o = []
    if slit > .02:
        for nm, ex in (("L", CXH - 44 - 4 * turn), ("R", CXH + 44 - 4 * turn)):
            sq = 1.0 - .22 * max(0.0, turn if nm == "R" else -turn)
            bl = st.get("blink_" + nm, st.get("blink", 0.0))
            if bl > .95:
                continue
            ey, rx, ry = 1072.0, 34 * sq, 38.0
            ly2 = ey - ry - 4 + (2 * ry + 8) * bl
            cid = lib.clip_of(ellipse_pts(ex, ey, rx - 1.5, ry - 1.5, 14))
            cid2 = lib.clip_rect(ex - 60, ly2 + 4, 120, 120)
            px, py = ex + lx * 12 * sq, ey + 2 + ly * 10
            w = 11.5 * sq * (1 - .62 * slit)
            g = (blob(ellipse_pts(px, py + 2, 14 * sq, 27, 14), "#a9d84a")
                 + blob(ellipse_pts(px, py + 26, 12 * sq, 8, 10), "#c8ea6a", .8)
                 + f'<ellipse cx="{px:.1f}" cy="{py + 2:.1f}" rx="{w:.1f}" ry="25" fill="#0b0a10"/>'
                 + f'<circle cx="{px - 9 * sq:.1f}" cy="{max(py - 6, ly2 + 12):.1f}" r="5" fill="#f4f8ff"/>')
            o.append(f'<g clip-path="url(#{cid})"><g clip-path="url(#{cid2})">{g}</g></g>')
    if flat_mouth > .02:
        o.append(blob([(818 + FX, 1121), (856 + FX, 1121), (856 + FX, 1137), (818 + FX, 1137)], CAT.CAT, flat_mouth))
        o.append(line([(820 + FX, 1128), (836 + FX, 1129.5), (852 + FX, 1128)], 3.4, INK, seed=7390, op=flat_mouth))
    return "".join(o)


def cat_draw(x, y, k, st, t, judge=None):
    """Кот из cat.draw (+ холод судьи поверх головы в той же системе)."""
    o = CAT.draw(x, y, k, st, t)
    if judge:
        o += f'<g transform="{head_tf(x, y, k, st, t)}">{judge_face(st, **judge)}</g>'
    return o


# ═════════════════════════ s01: хук ═════════════════════════
S0 = 2.4                     # базовый масштаб камеры хука и петли (доска на весь кадр до зоны субтитров)
CAM_HOOK = (-950.0, 675.0)   # центр камеры (мир)


def W(fx, fy):
    """Точка кадра (после влёта, без удара) → мир."""
    return CAM_HOOK[0] + (fx - 540) / S0, CAM_HOOK[1] + (fy - 960) / S0


SHELF_FY = 1190.0                        # кадр: верх полочки под котом (слева; доска справа уходит ниже неё)
SHELF_X1 = 600.0                         # кадр: правый край полочки
CAT_F = (318.0, SHELF_FY, 3.3)           # кадр: точка между задних лап кота и масштаб рисунка в кадре
ENV_F = (838.0, 1013.0, 2.2)              # кадр: кнопка конверта (низ конверта ≈ 1290) и масштаб
SPIDER_F = (985.0, 700.0)                # кадр: точка крепления нитки паучка на доске (над конвертом справа)
T_IF = wt("если")            # 0.34 — голова встаёт на зрителя, удар камерой
T_DE = wt("дело")            # 0.70 — коготь стукает по конверту, удар камерой +8 %
T_TAP = T_DE + .04
T_VI = wt("висит")           # 1.00 — паучок падает
T_ME = wt("месяц")           # 1.26 — паутина дрожит, глаза сужаются
T_MID = .17                  # подскок конверта и рывок паучка до первого удара


def shelf(fy_top, P_cold=True):
    """Настенная полочка под котом (кадр → мир): доска с кромкой и две скобы; справа от неё доска на стене уходит ниже."""
    x0, y0 = W(-200, fy_top)
    x1, _ = W(SHELF_X1, fy_top)
    if P_cold:
        top, top_sh, br = "#9a8d82", "#7c7068", "#6f747c"
    else:
        top, top_sh, br = "#b07a4c", "#86592f", "#6a4430"
    o = [blob(rect_pts(x0, y0 + 30, x1 - 10, y0 + 44), "#000000", .18)]
    for bx in (x0 + 90, x1 - 60):
        o.append(shape([(bx - 9, y0 + 30, 1), (bx + 9, y0 + 30, 1), (bx + 9, y0 + 112), (bx - 30, y0 + 34)], br, "", w=3.2, seed=7500 + int(bx) % 7))
    o.append(shape(rect_pts(x0, y0, x1, y0 + 32), top, blob(rect_pts(x0, y0 + 20, x1, y0 + 32), top_sh), w=4.0, seed=7501))
    return "".join(o)


def s01_cat(t):
    st = dict(_t=t, cold=1.0)       # cat.py: холодный судья — веки наполовину, зрачки-щёлки, прямой рот, уши прижаты
    # поворот головы к зрителю: в кадре 0 уже на середине (голова к конверту, скорость с кадра 0), встаёт на зрителя к «Если»
    u = clamp(t / T_IF)
    e = 1 - (1 - u) ** 2.2                      # *.out: максимальная скорость в кадре 0
    st["turn"] = lerp(-.62, 0.0, e) + damp(t, T_IF, -.09, 3.2, 7)
    st["tilt"] = lerp(-9.0, 0.0, e) + damp(t, T_IF, 2.6, 3.0, 7) + damp(t, T_TAP, -1.6, 3.4, 8)
    st["look"] = (lerp(.9, 0.0, e) + .7 * bump(t, T_TAP - .3, .55), lerp(.25, 0.0, e) + .4 * bump(t, T_TAP - .3, .55) + .5 * bump(t, T_VI, .4))
    lid = .5 + .16 * sm(t, T_ME, T_ME + .3) - .08 * bump(t, T_IF, .2)
    st["blink_L"] = lid + .03
    st["blink_R"] = lid
    # уши прижаты (cold) и ещё дёргаются: в кадре 0 — дрожь, на «Если» — прижим с отдачей
    st["ear"] = lerp(-10, 4, e) + damp(t, T_IF, 7, 4.5, 6) + 4 * math.sin(t * 13) * (1 - sm(t, .2, .6))
    st["perk"] = 0.0
    # хвост хлещет рывками (не синус с остановками) справа от тела, выше конверта; на стук — вскидывается
    lash = -29 + 8 * math.sin(2 * math.pi * 1.55 * t + 1.9) + 3.5 * math.sin(2 * math.pi * 3.1 * t + .4)
    st["tail"] = lash - 17 * sm(t, T_TAP - .36, T_TAP - .12) * (1 - sm(t, T_TAP + .25, T_TAP + .55)) + damp(t, T_TAP, -4, 3, 6)
    st["flame_e"] = 1.0 + .3 * math.sin(t * 7)
    # правая передняя лапа (та же, вторая на полке): замах, удар коготком по краю конверта на T_TAP, задержка, назад
    pw = 0.0
    if t > T_TAP - .32:
        if t < T_TAP - .1:
            pw = .62 * ease_out(clamp((t - (T_TAP - .32)) / .22), 2)
        elif t < T_TAP:
            pw = lerp(.62, .323, clamp((t - (T_TAP - .1)) / .1) ** 2)
        else:
            pw = .323 * (1 - ease_io(clamp((t - T_TAP - .16) / .3))) + damp(t, T_TAP, .03, 4, 9)
    st["paw"] = max(0.0, pw)
    st["paw_dx"] = lerp(60.0, 170.0, clamp((t - (T_TAP - .2)) / .2)) if t < T_TAP + .2 else 170.0
    # тело: вдох-рывок на поворот, сжатие на ударах
    sq = damp(t, T_IF, .025, 3.0, 7) + damp(t, T_TAP, .02, 3.2, 8)
    st["sy"] = 1 - sq
    st["sx"] = 1 + .5 * sq
    st["rot"] = lerp(-2.2, 0.0, e) + damp(t, T_IF, .8, 2.5, 6)
    return st, None


def shoulder_patch(x, y, k, st, t):
    """Плечо над началом вытянутой лапы (cat.body рисует лапу трубкой с обрезом у груди): мех поверх обреза, без контура."""
    if st.get("paw", 0.0) < .02:
        return ""
    br = 1 + 0.012 * math.sin(t * 2 * math.pi / 3.1)
    sy = br * st.get("sy", 1.0)
    sx = st.get("sx", 1.0)
    fx = CAT.CX + 25
    g = (blob(ellipse_pts(fx + 4, 1236, 30, 26, 16), lib.mix(CAT.CAT, CAT.CAT_FUR, .25))
         + line([(fx - 14, 1222), (fx - 8, 1240)], 2.2, CAT.CAT_EDGE, seed=7520, op=.8))
    return (f'<g transform="translate({x:.2f} {y:.2f}) rotate({st.get("rot", 0.0):.2f}) scale({k:.4f}) translate({-CAT.CX} {-CAT.CBOT})">'
            f'<g transform="translate({CAT.CX} {CAT.CBOT}) scale({sx:.4f} {sy:.4f}) translate({-CAT.CX} {-CAT.CBOT})">{g}</g></g>')


def s01_env(t):
    """Качание конверта (град) и пыль: в кадре 0 уже качается, подскок T_MID, стук когтем T_TAP — сильнее."""
    sw = -9.0 * math.cos(2 * math.pi * 1.35 * t + .9) * math.exp(-.6 * t)
    sw += damp(t, T_MID, 5.0, 2.4, 3.5)
    sw += damp(t, T_TAP, 13.0, 1.7, 1.9)
    sw += damp(t, .5, 4.0, 2.6, 4.0)
    hop = 14 * bump(t, T_MID - .06, .2) + 12 * bump(t, .46, .2) + 10 * bump(t, T_TAP, .18)
    return sw, hop


def s01_spider(t):
    """Паучок: качается на нитке (кадр 0 — уже в движении), рывок вверх T_MID, на «висит» падает вниз перед конвертом."""
    drop = 120 + 18 * math.sin(2 * math.pi * 2.1 * t + 1.1) - 40 * bump(t, T_MID - .05, .22) - 34 * bump(t, .5, .2)
    if t > T_VI:
        q = t - T_VI
        drop += 300 * clamp(q / .16) ** 2 - damp(t, T_VI + .16, 40, 2.6, 4.0)
    sway = 22 * math.sin(2 * math.pi * 1.2 * t + .3) + damp(t, T_VI + .16, 14, 1.6, 2.5)
    return drop, sway


def s01_world(t, warm=False):
    """Мир хука: доска, комод, конверт, паутина, паучок, кот. Возвращает (список слоёв, кот(x, y, k, st), конверт SVG)."""
    st, jd = s01_cat(t)
    cx, cy = W(CAT_F[0], CAT_F[1])
    k = CAT_F[2] / S0
    ex, ey = W(ENV_F[0], ENV_F[1])
    ek = ENV_F[2] / S0
    sw, hop = s01_env(t)
    dust = 1.0
    env = PR.pinned_envelope(ex, ey - hop / S0, ek, swing=sw, dust=dust, web=1.0, t=t, seed=73)
    # паутина в углу доски у кнопки, дрожит от удара и на «месяц»
    tremble = clamp(.35 + .9 * bump(t, T_TAP, .5) + 1.0 * sm(t, T_ME, T_ME + .12) * (1 - sm(t, T_ME + .5, T_ME + .9)))
    wx, wy = W(1080, 560)
    web = PR.cobweb(wx, wy, 1.3, tremble=tremble, t=t, ang=100, span=80, L=170, seed=731)
    sx_, sy_ = W(*SPIDER_F)
    drop, sway = s01_spider(t)
    spd = PR.spider(sx_ + sway / S0, sy_, .88, drop=drop / S0 * 1.0, t=t, seed=73, look=-.6)
    thread = line([(sx_, sy_ - 60), (sx_ + sway / S0, sy_)], 1.6, "#d9dde2", taper=.1, wmin=.7, seed=7510, op=.9)
    # облачко пыли от стука
    puff = PR.dust_puff(*W(640, 960), 1.15, clamp((t - T_TAP) / .5), seed=73) if t > T_TAP else ""
    puff2 = PR.dust_puff(*W(860, 1300), .8, clamp((t - T_TAP - .06) / .55), seed=74) if t > T_TAP + .06 else ""
    cat = cat_draw(cx, cy, k, st, t, judge=jd) + shoulder_patch(cx, cy, k, st, t)
    cat = R.cold_tint(cat, .7)
    cat_sh = blob([(cx - 150 * k, cy - 4), (cx + 160 * k, cy - 4), (cx + 180 * k, cy + 10), (cx - 140 * k, cy + 10)], "#5a6068", .55)
    bc = R.board_close(t, "cold")
    layers = [bc["bg"], R.cold_tint(web, .5), R.cold_tint(env, .8), shelf(SHELF_FY), cat_sh, R.cold_tint(thread + spd, .6), cat,
              R.cold_tint(puff + puff2, .6)]
    return st, (cx, cy, k), env, layers


def s01(t):
    lib.dyn_begin()
    st, (cx, cy, k), env, world = s01_world(t)
    mk = os.environ.get("MASK")
    if mk:
        world = ['<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>']
        if mk in ("face", "both"):
            world.append(face_mask(cx, cy, k, st, t))
        if mk in ("env", "both"):      # конверт с кнопкой — без пыли и паутины
            ex, ey = W(ENV_F[0], ENV_F[1])
            sw, hop = s01_env(t)
            world.append(mask_svg(PR.pinned_envelope(ex, ey - hop / S0, ENV_F[2] / S0, swing=sw, t=t, seed=73), "env"))
    if os.environ.get("NOCAM"):
        set_ink(S0)
        return lib.svg(f'<g transform="{lib.cam(CAM_HOOK[0], CAM_HOOK[1], S0)}">{"".join(world)}</g>')
    kk, rc, side = hook_cam(t, T_IF, T_DE)
    sx1, sy1 = shake2(t, T_VI + .16, 7)
    ccx = CAM_HOOK[0] + side - sx1 + 4 * math.sin(t * 2.3)
    ccy = CAM_HOOK[1] - sy1
    s = S0 * kk * (1 + .02 * sm(t, .5, 1.9))
    set_ink(s)
    return lib.svg(f'<g transform="{lib.cam(ccx, ccy, s, rc)}">{"".join(world)}</g>')


# ═════════════════════════ s06: поворот — сбой, темнота, часы 3:12, удар сердца, кровать, тень судьи ═════════════════════════
T_CUT = 6.90
T_BEAT = 7.30
T_VOT = wt("вот", 7.0)          # 7.82 — проезд вниз к кровати
T_GOV = wt("говорит", 7.0)      # 8.38 — тень судьи на потолке


def s06_dima(t):
    """Дима лежит на спине (вид от изножья): голова на подушке, глаза открыты, взгляд в потолок, медленное моргание."""
    import people as PP
    PP.C = PP.PAL["dima"]
    hx, hy = R.FOOT_HEAD
    bl = bump(t, 7.95, .5) * .95 + bump(t, 8.6, .45) * .9
    ex = PP.awake_blink("awake73", bl)
    rot = -7 + 1.5 * math.sin(t * .9) - 3 * sm(t, T_GOV, T_GOV + .4)
    head = f'<g transform="translate({hx:.1f} {hy - 40:.1f}) rotate({rot:.2f}) scale(1.55)">{PP.dima_head(ex)}</g>'
    return R.cold_tint(head, 0.0, .55)


def s06_shadow(t):
    """Тень холодного кота-судьи линией на потолке и верху стены слева над кроватью (та же поза, что в хуке)."""
    import people as PP
    u = sm(t, T_GOV - .05, T_GOV + .3)
    if u < .01:
        return ""
    st = dict(cold=1.0, look=(0, 0), tilt=-2 + 2 * math.sin(t * 1.3), tail=-20 + 8 * math.sin(t * 2.4), ear=4 * math.sin(t * 5))
    k = 1.35 * (1.06 - .06 * u)
    sh = PP.cat_judge_shadow(250, 520 + 30 * (1 - u), k, st, t, col="#93a6d6", w=5.5, op=.9)
    # тень шевелит губами: короткий штрих рта открывается и закрывается в такт словам
    mo = abs(math.sin(2 * math.pi * 3.2 * (t - T_GOV))) * (1 if t < 8.73 else 0)
    mx, my = 250 + 0 * k, 520 + (1124 - 1306) * k + 30 * (1 - u)
    mouth = line([(mx - 14 * k, my), (mx, my + 10 * k * mo), (mx + 14 * k, my)], 4, "#93a6d6", taper=.3, wmin=.5, seed=7530, op=.9 * u)
    return f'<g opacity="{u:.3f}">{sh}</g>' + mouth


def s06(t):
    lib.dyn_begin()
    if t < T_CUT + 2 / 30:      # хвост холодного дня (кот-судья у доски) и белый всполох-сбой 2 кадра
        _, _, _, world = s01_world(t - 5.0)
        set_ink(S0)
        day = f'<g transform="{lib.cam(CAM_HOOK[0], CAM_HOOK[1], S0 * 1.06)}">{"".join(world)}</g>'
        if t < T_CUT:
            return lib.svg(day)
        g = (t - T_CUT) * 30
        out = []
        for i, (y0, h, dx) in enumerate(((120, 160, 70), (520, 90, -110), (900, 210, 140), (1380, 120, -60))):
            c = lib.clip_rect(0, y0, 1080, h)
            out.append(f'<g clip-path="url(#{c})"><g transform="translate({dx * (1 + g):.1f} 0)">{day}</g></g>')
        return lib.svg(day + "".join(out) + f'<rect width="1080" height="1920" fill="#ffffff" opacity="{.75 + .2 * g:.2f}"/>'
                       + f'<rect y="{700 + 300 * g:.0f}" width="1080" height="26" fill="#0b0f1e" opacity=".7"/>')
    bd = R.bedroom(t, "moon", "foot")
    cxk, cyk, rk = R.CLOCK_F
    clock = R.lib_clock73(cxk, cyk, rk, t, R.PAL73["moon"])
    dima = s06_dima(t) if t > T_VOT - .1 else ""      # до проезда голова за нижним краем кадра в темноте (без обрывка волос)
    world = [bd["bg"], clock, dima, bd["front"], s06_shadow(t)]
    # темнота: почти чёрная синяя вуаль, проступает к удару сердца; часы и лунный прямоугольник видны сквозь неё
    q = t - T_CUT
    dk = .9 - .3 * sm(t, T_CUT + .1, T_BEAT) - .25 * sm(t, T_BEAT, T_BEAT + .6) - .1 * sm(t, T_VOT, T_VOT + .5)
    holes = [(PR.circle_d(cxk, cyk, rk * 1.1), .85), (PR.circle_d(160, 520, 260, 330), .6 * sm(t, T_BEAT - .05, T_BEAT + .3))]
    world.append(PR.darkness(dk, "#03050d", holes=holes, blur_sd=7, box=(-800, -800, 1900, 2800)))
    # камера: часы крупно с микродрейфом → на «Вот так» плавный проезд вниз к кровати → на «говорит» наклон к тени
    cx0, cy0, s0 = R.CAM73_CLOCK
    cx1, cy1, s1 = R.CAM73_FOOT
    u = ease_io(clamp((t - T_VOT) / .7))
    cx = lerp(cx0, cx1, u) + 5 * math.sin(t * 1.7) - 40 * sm(t, T_GOV, T_GOV + .5)
    cy = lerp(cy0, cy1, u) + 4 * math.sin(t * 1.3 + 1) - 90 * sm(t, T_GOV, T_GOV + .5)
    s = lerp(s0, s1, u) * (1 + .025 * q) * (1 + .04 * R.heart_k(t, T_BEAT))
    rot = -1.2 * sm(t, T_GOV, T_GOV + .5)
    set_ink(s)
    body = f'<g transform="{lib.cam(cx, cy, s, rot)}">{"".join(world)}</g>' + R.heart_pulse(t, T_BEAT, 1.2)
    if q < .2:      # след всполоха: синий отсвет гаснет
        body += f'<rect width="1080" height="1920" fill="#6f86d8" opacity="{.35 * (1 - q / .2):.3f}"/>'
    return lib.svg(body)


# ═════════════════════════ s17: петля — ракурс хука в тепле, карточка снята с кнопки, тёплый кивок ═════════════════════════
T_RAZ = wt("разберу", 23.0)     # 23.25
T_PER = wt("первым", 23.0)      # 23.72
T_TAP17 = T_RAZ + .2            # коготь поддевает карточку
T_FALL = T_RAZ + .3             # карточка соскальзывает с кнопки
CARD_F = (838.0, 1030.0, 2.6)   # кадр: кнопка карточки (низ ≈ 1295), масштаб


def s17_cat(t):
    import people as PP
    st = dict(_t=t, blink=.28, smile=1.0, perk=.25, look=(.5 * sm(t, 23.0, T_TAP17) * (1 - sm(t, T_FALL + .1, T_FALL + .4)), .35))
    st["look"] = (st["look"][0], .2 + .5 * sm(t, T_FALL, T_FALL + .2) * (1 - sm(t, T_PER, T_PER + .3)))
    st["drop"] = PP.cat_nod(t, T_PER, .55, .32)
    st["tilt"] = 3 * math.sin(t * 1.4) + 5 * bump(t, T_PER, .55)
    st["blink"] = max(.28, .9 * bump(t, T_PER + .05, .4), bump(t, 24.2, .2))
    st["ear"] = 5 * math.sin(t * 3.1) + damp(t, T_TAP17, 6, 4, 6)
    st["tail"] = -30 + 5 * math.sin(2 * math.pi * .8 * t)
    st["flame_e"] = 1.2 + 1.3 * bump(t, T_PER + .05, .6) + .2 * math.sin(t * 8)
    pw = 0.0
    a = T_TAP17 - .25
    if t > a:
        if t < T_TAP17:
            pw = .323 * ease_out(clamp((t - a) / .25), 2)
        else:
            pw = .323 * (1 - ease_io(clamp((t - T_TAP17 - .15) / .3)))
    st["paw"] = pw
    st["paw_dx"] = 170.0
    return st


def s17_card(t):
    """Карточка: качается на кнопке, коготь поддевает, соскальзывает и падает на полочку к лапам кота (кнопка остаётся)."""
    px, py = W(CARD_F[0], CARD_F[1])
    k = CARD_F[2] / S0
    if t < T_FALL:
        sw = 3 * math.sin(2 * math.pi * 1.1 * t) + damp(t, T_TAP17, 8, 2.2, 3)
        return PR.pinned_card(px, py, k, swing=sw, dust=.5, t=t, seed=73), PR.push_pin(px, py, k)
    q = clamp((t - T_FALL) / .32)
    tx, ty = W(470, SHELF_FY - 8)
    x = lerp(px, tx, ease_io(q))
    y = lerp(py, ty - 60 * k, q * q) - 40 * k * math.sin(math.pi * q) + 6 * bump(t, T_FALL + .32, .18)
    rot = lerp(4, -12, q) + damp(t, T_FALL + .32, 4, 3, 6)
    sy = lerp(1.0, .45, ease_io(q))      # ложится на полочку (вид сверху сжимается)
    card = PR.pinned_card(0, 0, k, swing=0, dust=.5, t=t, seed=73, pin=False)
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f}) scale(1 {sy:.3f})">{card}</g>', PR.push_pin(px, py, k)


def s17(t):
    lib.dyn_begin()
    st = s17_cat(t)
    cx, cy = W(CAT_F[0], CAT_F[1])
    k = CAT_F[2] / S0
    bc = R.board_close(t, "lamp")
    card, pin = s17_card(t)
    cat = R.warm_tint(CAT.draw(cx, cy, k, st, t) + shoulder_patch(cx, cy, k, st, t), .5)
    cat_sh = blob([(cx - 150 * k, cy - 4), (cx + 160 * k, cy - 4), (cx + 180 * k, cy + 10), (cx - 140 * k, cy + 10)], "#3a2418", .5)
    sh = shelf(SHELF_FY, P_cold=False)
    if t < T_FALL + .2:
        world = [bc["bg"], R.warm_tint(pin, .4), R.warm_tint(card, .5), bc["light"], sh, cat_sh, cat]
    else:
        world = [bc["bg"], R.warm_tint(pin, .4), bc["light"], sh, cat_sh, cat, R.warm_tint(card, .5)]
    mk = os.environ.get("MASK")
    if mk:
        world = ['<rect x="-3000" y="-3000" width="8000" height="8000" fill="#fff"/>']
        if mk in ("face", "both"):
            world.append(face_mask(cx, cy, k, st, t))
        if mk in ("env", "both"):
            world.append(mask_svg(card, "env"))
    s = S0 * (1 + .03 * sm(t, 23.02, 24.5) + .025 * bump(t, T_PER, .6))
    set_ink(s)
    body = f'<g transform="{lib.cam(CAM_HOOK[0], CAM_HOOK[1] - 8 * bump(t, T_PER, .6), s)}">{"".join(world)}</g>'
    fl = bump(t, T_PER + .05, .6)
    if fl > .01 and not mk:
        body += f'<rect width="1080" height="1920" fill="#ffb054" opacity="{.05 * fl:.3f}" style="mix-blend-mode:screen"/>'
    return lib.svg(body)


def frame(sid, t):
    return {"s01": s01, "s06": s06, "s17": s17}[sid](t)
