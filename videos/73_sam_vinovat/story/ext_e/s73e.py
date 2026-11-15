"""Рилс 73 «Ты сам виноват», группа E — тепло на кровати и конверт.
s10 (13.10–14.90): тёплый свет ночника, Дима сидит в кровати под одеялом, кот сидит на одеяле, рядом судейский молоток из s02.
    «Ты не виноват» (13.49) кот спокойно сталкивает лапой молоток — он падает с кровати вниз из кадра; «что начинать» Дима выдыхает;
    «тяжело» (14.45) плечи опускаются, кот прислоняется боком к его руке.
s11 (14.90–16.05): общий план, Дима и кот сидят рядом на краю кровати в пятне ночника, луна в окне, на стене пыльный конверт.
    «один» (15.45) кот бодает Диму головой в плечо, Дима улыбается краешком рта и кладёт ладонь коту на спину, огонёк разгорается.
s13 (17.40–18.85, хлёст): пробковая доска с пыльным конвертом в паутине, Дима стоит у доски, кот у ног. «одно» (17.58) кот дует на
    конверт — облако пыли, паучок убегает по нитке вверх; «маленькое» Дима снимает конверт двумя пальцами; «действие» (18.30) отгибает
    клапан — внутри чистый лист.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, Дима — common/people.py, кот — common/cat.py,
предметы — common/props.py; здесь только хореография и камера. Надписей, букв и цифр нет."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
import cat as CAT  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from h73 import blinks, bump, flame_world, lerp, lerp2, set_ink, shake, sm, whip, wt  # noqa: E402
from lib import blob, clamp, ease_in, ease_out, ellipse_pts, line  # noqa: E402

BG = "#3a2418"
FRAMES = {}
LAYERS_UP = ("pelvis", "arm_f", "body", "arm_n")


def ex(name, **kw):
    e = dict(people.EXPR["dima"][name])
    e.setdefault("bags", False)
    e.update(kw)
    return e


def frame(sid, t):
    lib.dyn_begin()
    lib.INK_K[0] = 1.0
    body, bg = FRAMES[sid](t)
    return lib.svg(f'<rect width="1080" height="1920" fill="{bg}"/>{body}')


def puff(head, t, t0, dur=.7, side=1, col="#f3e6d2"):
    """Выдох: три мягких пятна у рта растут и тают."""
    q = clamp((t - t0) / dur)
    if q <= 0 or q >= 1:
        return ""
    hx, hy = head
    o = ""
    for j in range(3):
        x0 = hx + side * (140 + 70 * q + j * 26)
        y0 = hy + 62 - 10 * q + (j - 1) * 14
        r = (14 + 10 * j) * (.5 + .7 * q)
        o += blob(ellipse_pts(x0, y0, r * 1.3, r, 12), col, .45 * math.sin(math.pi * q))
    return o


WARM_ = '<rect x="-4000" y="-4000" width="9000" height="9000" fill="#ff9a40" opacity="{op}" style="mix-blend-mode:soft-light"/>'


# ═════════════════════════ s10: «Ты не виноват» — молоток с кровати ═════════════════════════
T_A10 = 13.10
T_TY, T_VIN, T_CHTO, T_NACH, T_TYAZH = wt(34), wt(36), wt(37), wt(38), wt(39)      # 13.16, 13.49, 13.95, 14.05, 14.45
BT = R.BED73_TOP
DIMA10 = (1790.0, BT + 20)          # таз Димы у подушки (изголовье справа), сидит лицом влево, ноги под одеялом
CAT10 = (1420.0, BT - 70)           # кот сидит на одеяле у его колен
CAT10_K = 1.0
GAV10 = (1272.0, BT - 112)           # молоток лежит на одеяле: (x, y) — конец рукояти, боёк слева


def mir(p, x0):
    return (2 * x0 - p[0], p[1])


def s10(t):
    sc = R.bedroom(t, "lamp", "bed")
    P = sc["P"]
    # Дима: сидит, плечи сначала подняты (зажат); «что начинать» — выдох, «тяжело» плечи опускаются, голова клонится, тёплая улыбка
    drop = sm(t, T_TYAZH - .05, T_TYAZH + .4)
    sh = .5 * (1 - drop) + .03 * math.sin(t * 2.2)
    exh = bump(t, T_CHTO, .55)
    if t < T_CHTO - .05:
        e = ex("sag73", look=(.4, .4), lid=.5, closed=blinks(t, (13.02,)))
    elif t < T_TYAZH + .1:
        e = ex("exhale73", closed=.6 * exh)
    else:
        e = ex("smile73", look=(.5, .55), closed=blinks(t, (14.8,)))
    hx, hy = DIMA10
    # руки (цели в координатах до отражения: фигура рисуется лицом вправо и отражается вокруг таза): кисти лежат на одеяле на коленях
    Wn = (hx + 190 + 10 * drop, BT - 56 + 16 * drop)
    Wf = (hx + 150, BT - 50 + 10 * drop)
    hn = {"dir": (1, .25), "curl": (.25, .3, .35, .4), "thumb": .35, "spread": .1}
    kw = dict(arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, hands={"f": hn, "n": hn}, lean_add=.04 + .1 * drop + .012 * math.sin(t * 2.0),
              head_add=.08 * drop - .03 * exh, shrug=sh, flip=True)
    full = people.dima(hx, hy, 1.0, e, None, **kw)
    parts = {k: R.warm_tint(people.dima(hx, hy, 1.0, e, None, layers=(k,), **kw)["svg"], .6) for k in LAYERS_UP}
    # кот: смотрит на молоток → «Ты не виноват» левая (от зрителя) передняя лапа толкает его (та же лапа, вторая на одеяле) → лапа
    # назад → «тяжело» кот переступает к Диме и прислоняется боком к его руке, жмурится
    push = sm(t, T_TY + .02, T_VIN + .04) * (1 - sm(t, T_VIN + .25, T_VIN + .5))
    lean_c = sm(t, T_TYAZH - .12, T_TYAZH + .35)
    cx = CAT10[0] + 45 * lean_c
    cy = CAT10[1] - 4 * lean_c
    look_d = sm(t, T_VIN + .3, T_TYAZH - .1)
    st = dict(turn=lerp(-.55, .5, look_d), look=(lerp(-.8, .7, look_d), lerp(.5, -.2, lean_c)),
              tilt=lerp(-4, 10, lean_c) + 2 * math.sin(t * 1.7), blink=max(blinks(t, (13.98,)), .6 * lean_c), smile=1.0 if lean_c > .4 else 0.0,
              paw_l=.3 * push, paw_l_dx=200, rot=8 * lean_c - 3 * push, tail=-8 + 6 * math.sin(t * 2.3), ear=3 * math.sin(t * 2.9),
              walk=(t - T_TYAZH + .12) * 2.2 if .02 < lean_c < .98 else None, flame_e=1.0 + .5 * lean_c)
    cat = R.warm_tint(CAT.draw(cx, cy, CAT10_K, st, t), .25)
    flx, fly = flame_world(cx, cy, CAT10_K, st["tail"])
    cat += PR.glow(flx, fly - 40, 80, .4, "#ffb347")
    # молоток: лежит; на «виноват» лапа толкает — скользит влево, переваливается через край кровати и падает вниз из кадра
    tp = T_VIN - .03
    if t < tp:
        gx, gy, gr = GAV10[0], GAV10[1], -6.0
    else:
        q = t - tp
        slide = 150 * ease_out(clamp(q / .22), 2)
        fall = max(0.0, q - .2)
        gx = GAV10[0] - slide - 160 * fall
        gy = GAV10[1] + .5 * 4200 * fall * fall
        gr = -6 - 220 * fall
    gav = R.warm_tint(PR.gavel(gx, gy, .62, gr, t), .5)
    world = [sc["bg"], sc["pillow"], parts["pelvis"], parts["arm_f"], parts["body"], sc["blanket"], gav, cat, parts["arm_n"],
             puff(full["head"], t, T_CHTO - .02, .75, side=-1)]
    # камера: медленный дрейф вправо, на падении молотка короткий сдвиг вниз 2 %
    u = sm(t, T_A10 - .2, 15.1)
    s = 1.3 + .03 * u + .01 * math.sin(t * 1.8)
    ccx = lerp(1520, 1560, u) + 4 * math.sin(t * 1.3)
    ccy = 960 + 3 * math.sin(t * 1.6) + 30 * bump(t, T_VIN + .25, .5)
    set_ink(s)
    return f'<g transform="{lib.cam(ccx, ccy, s, lerp(-.4, .3, u))}">{"".join(world)}</g>', BG


FRAMES["s10"] = s10
