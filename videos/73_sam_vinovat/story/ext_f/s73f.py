"""Рилс 73 «Ты сам виноват», группа F — вместе и призыв.
s14 (18.85–20.05): Дима за столом под тёплой лампой, открытый конверт рядом, ноутбук ЭКРАНОМ К ДИМЕ (зритель видит крышку сбоку,
    свет экрана на лице); кот сидит на столе у ближнего края. «давай» (18.93) кот кладёт лапу Диме на запястье; «вместе» (19.20)
    оба наклоняются к экрану, Дима печатает, свет экрана теплеет.
s15 (20.05–21.62, хлёст вниз): призыв — кот близко к зрителю тянет лапу к камере, за ним чистая пробковая доска на тёмной тёплой
    стене; рукописное «кот» 20.35–20.85 (common/hand_kot.py) на чистой стене над доской; «висит» (21.11) на доске на новой кнопке
    появляется и качается пустая карточка.
frame(sid, t) -> SVG 1080×1920; t — общее время ролика. Комната — common/room.py, Дима — common/people.py, кот — common/cat.py,
предметы — common/props.py, «кот» — common/hand_kot.py; здесь только хореография и камера (ноутбук экраном к Диме — h73.laptop_side).
Надписей, букв и цифр нет (кроме «кот»)."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STORY, "common"))
sys.path.insert(0, os.path.join(STORY, "ext_e"))
import cat as CAT  # noqa: E402
import hand_kot  # noqa: E402
import lib  # noqa: E402
import people  # noqa: E402
import props as PR  # noqa: E402
import room as R  # noqa: E402
from h73 import blinks, bump, flame_world, laptop_side, lerp, lerp2, set_ink, shake, sm, whip, wt  # noqa: E402
from lib import blob, clamp, ease_out, ellipse_pts, line  # noqa: E402

BG = "#2a1d17"
FRAMES = {}
LAYERS = ("legs", "pelvis", "arm_f", "body", "arm_n")


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


# ═════════════════════════ s14: давай вместе — лапа на запястье, печатают ═════════════════════════
T_A14 = 18.85
T_DAV, T_VME = wt(52), wt(53)            # 18.93, 19.20
SX14, SY14 = R.SIT
FEET14 = {"n": ((SX14 + 300, R.FL - 52), 0.0), "f": ((SX14 + 250, R.FL - 50), 0.0)}
LAP14 = (640.0, R.DESK_TOP - 66)
LAP14_K = .8
CAT14 = (1000.0, R.DESK_TOP - 4)          # кот на ближнем крае стола справа от рук, ближе к камере, чем ноутбук
CAT14_K = .9
ENV14 = (1210.0, R.DESK_TOP - 40)        # открытый конверт на столе за котом


def type_hand(t, base, phase, amp=1.0):
    ph = t * 10.0 + phase
    W = (base[0] + 7 * amp * math.sin(ph * .7), base[1] - 5 * amp * abs(math.sin(ph)))
    curl = tuple(.35 + .25 * amp * max(0.0, math.sin(ph + i * 1.7)) for i in range(4))
    return W, {"dir": (1, .32), "curl": curl, "thumb": .35, "spread": .12, "bend": .1}


def s14(t):
    sc = R.desk_scene(t, "night", lamp_on=1.0)
    warmth = sm(t, T_VME, T_VME + .5)
    lp = laptop_side(LAP14[0], LAP14[1], LAP14_K, 1.0, on=1.0, lines=clamp(.15 + (t - T_VME) * .9) if t > T_VME else .15, t=t, seed=3)
    kc = lp["keys"]
    # руки: до «вместе» — лежат у клавиатуры неподвижно (Дима не решается), ближнее запястье ждёт лапу; «вместе» — печатает
    typ = sm(t, T_VME - .02, T_VME + .2)
    lean = sm(t, T_VME - .05, T_VME + .35)
    Wf_rest = (kc[0] - 95, kc[1] + 8)
    Wn_rest = (kc[0] + 5, kc[1] + 16)
    Wf_t, hf_t = type_hand(t, (kc[0] - 75, kc[1] + 2), 0.0, typ)
    Wn_t, hn_t = type_hand(t, (kc[0] - 20, kc[1] + 10), 1.9, typ)
    rest_h = {"dir": (1, .3), "curl": (.3, .35, .4, .45), "thumb": .35, "spread": .1}
    Wf = lerp2(Wf_rest, Wf_t, typ)
    Wn = lerp2(Wn_rest, Wn_t, typ)
    hf = hf_t if typ > .5 else rest_h
    hn = hn_t if typ > .5 else rest_h
    # Дима: смотрит на экран неуверенно → на «давай» переводит взгляд на лапу и кота → «вместе» наклоняется к экрану, улыбка
    look_cat = bump(t, T_DAV + .02, .32)
    if typ > .3:
        e = ex("focus_smile", look=(.6, .45), closed=blinks(t, (19.75,)))
    elif look_cat > .2:
        e = ex("relief71", look=(.7, .7), closed=0.0)
    else:
        e = ex("focus", look=(.6, .4), lid=.55, brows="worry", closed=blinks(t, (18.72,)))
    kw = dict(feet=FEET14, arms={"f": ("ik", Wf, -1), "n": ("ik", Wn, -1)}, hands={"f": hf, "n": hn},
              lean_add=.06 + .1 * lean + .012 * math.sin(t * 2.3), head_add=.04 + .05 * lean - .05 * look_cat + .015 * math.sin(t * 1.9))
    parts = {k: people.dima(SX14, SY14, 1.0, e, "type", layers=(k,), **kw)["svg"] for k in LAYERS}
    head = people.dima(SX14, SY14, 1.0, e, "type", **kw)["head"]
    # кот: смотрит на Диму, «давай» — левая (от зрителя) передняя лапа ложится на ближнее запястье (та же лапа, вторая на столе);
    # «вместе» — лапа уходит назад на стол, кот наклоняется к экрану вместе с Димой
    cx, cy = CAT14
    reach = sm(t, T_DAV - .1, T_DAV + .12) * (1 - sm(t, T_VME + .15, T_VME + .45))
    # кончик лапы — на ближнее запястье (сверху); подъём и вынос лапы считаются от кончика
    pw = max(.05, (cy - (Wn[1] - 14)) / (150 * CAT14_K))
    dxw = max(10.0, ((cx - (Wn[0] + 4)) / CAT14_K - 25) / (1.6 * pw))
    st = dict(turn=lerp(-.6, -.85, reach) + .25 * lean, look=(lerp(-.7, -.9, reach), lerp(-.2, .2, reach)),
              tilt=-4 * lean + 3 * math.sin(t * 1.6) - 3 * reach, blink=blinks(t, (19.45,)), smile=1.0,
              paw_l=pw * reach, paw_l_dx=dxw,
              tail=-8 + 6 * math.sin(t * 2.1), rot=-6 * lean, ear=2 * math.sin(t * 3.1), flame_e=1.0 + .5 * warmth)
    cat = CAT.draw(cx, cy, CAT14_K, st, t)
    if reach > .05:      # та же левая передняя лапа поверх трубки рига: живая форма с изгибом и подушечками (people.cat_forearm)
        k_ = CAT14_K
        sh_ = (cx + (-25 + 4) * k_, cy + (1238 - CAT.CBOT) * k_)
        tip_ = people.cat_paw_tip(cx, cy, k_, st, side="l")
        cat += people.cat_forearm(sh_, tip_, k=.6 * k_, seed=14)
        cat += blob(ellipse_pts(sh_[0] + 6 * k_, sh_[1], 30 * k_, 26 * k_, 14), CAT.CAT)      # плечо закрывает срез лапы
    flx, fly = flame_world(cx, cy, CAT14_K, st["tail"])
    fl = PR.glow(flx, fly - 40, 70, .35 + .25 * warmth, "#ffb347")
    shadow = blob(ellipse_pts(cx, cy + 4, 150, 12, 16), "#2a1a12", .3)
    # открытый конверт: лежит на столе за котом (клапан отогнут, внутри чистый лист)
    env = PR.letter(ENV14[0], ENV14[1] - 30, .5, rot=-8, write=0.0, seed=4)
    # свет экрана на лице: холодно-белый → теплеет на «вместе»
    hx, hy = head
    light = PR.glow(hx + 70, hy + 10, 140, .45, lib.mix("#DDE8FF", "#FFE2B0", warmth), ry=160)
    world = [sc["bg"], sc["chair_back"], sc["desk_top"], parts["legs"], sc["desk_legs"], sc["chair_seat"], parts["pelvis"], parts["arm_f"],
             parts["body"], env, lp["svg"], parts["arm_n"], shadow, cat, fl, f'<g transform="translate(150 0)">{sc["lamp"]}</g>', light]
    # камера: медленный дрейф к ноутбуку, на «вместе» лёгкий удар +3 %
    u = sm(t, T_A14 - .2, 20.25)
    s = lerp(1.08, 1.15, u) + .04 * bump(t, T_VME, .3)
    ccx = lerp(705, 720, u) + 4 * math.sin(t * 1.4)
    ccy = lerp(900, 880, u) + 3 * math.sin(t * 1.7)
    set_ink(s)
    warm_ = '<rect x="-3000" y="-3000" width="8000" height="8000" fill="#ff9a40" opacity=".32" style="mix-blend-mode:soft-light"/>'
    return f'<g transform="{lib.cam(ccx, ccy, s, lerp(-.3, .3, u))}">{"".join(world)}{warm_}</g>', BG


FRAMES["s14"] = s14


# ═════════════════════════ s15: призыв — лапа к зрителю, «кот», карточка на кнопке ═════════════════════════
T_A15 = 20.05
T_NAP, T_VIS = wt(54), wt(56)            # 20.09, 21.11
KOT_T0, KOT_DUR = 20.35, .5              # дописано к 20.85 (звук «дописано» 20.90), стоит до склейки 21.62
CAM15 = (-950.0, 860.0, 1.15)
CAT15 = (-1125.0, 1175.0)                # кот в самом переднем плане, перед доской (крупнее мира комнаты)
CAT15_K = 2.15
KOT15 = (-1135.0, 262.0, 1.55)           # чистая стена над доской (room.BOARD73_CLEAN): за буквами ничего
CARD15 = (-662.0, 455.0)                 # новая кнопка с пустой карточкой справа от головы кота


def whip_v(g, t, t_in, amp=300.0, blur=30.0, dur=.2, side=-1):
    """Хлёст вниз на входе плана: картинка приезжает сверху (side=-1) с вертикальным размытием, гаснет за dur."""
    e = ease_out(clamp((t - t_in) / dur), 2)
    dy, b = side * amp * (1 - e), blur * (1 - e)
    g = f'<g transform="translate(0 {dy:.1f})">{g}</g>'
    if b > .5:
        fid = lib.uid("wv")
        lib.DEFS.append(f'<filter id="{fid}" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="0 {b:.1f}"/></filter>')
        g = f'<g filter="url(#{fid})">{g}</g>'
    return g


def s15(t):
    sc = R.bedroom(t, "lamp", "board")
    P = sc["P"]
    # кот: смотрит на зрителя; «Напиши» тянет правую (от зрителя) переднюю лапу к камере (вторая на полу), держит, опускает к «висит»;
    # на «висит» поворачивает морду к карточке, потом снова на зрителя, медленно моргает
    reach = sm(t, T_NAP - .05, T_NAP + .3) * (1 - sm(t, 20.95, 21.2))
    look_card = bump(t, T_VIS - .05, .6)
    done = sm(t, KOT_T0 + KOT_DUR, KOT_T0 + KOT_DUR + .25)
    st = dict(turn=.45 * look_card, look=(.9 * look_card, -.1 - .4 * look_card), tilt=-5 * reach + 6 * look_card + 2 * math.sin(t * 1.6),
              paw=reach, paw_dx=26, smile=1.0, blink=blinks(t, (20.0, 21.45), .22),
              tail=-6 + 8 * math.sin(t * 2.2), ear=4 * bump(t, T_NAP, .3) + 2 * math.sin(t * 3.1), perk=.4 * reach,
              flame_e=1.2 + .4 * reach, sx=1 + .04 * reach, sy=1 + .03 * reach)
    cx, cy = CAT15
    cat = CAT.draw(cx, cy, CAT15_K, st, t)
    if reach > .05:      # та же правая передняя лапа тянется к камере: живая лапа с подушечками, растёт навстречу зрителю
        k_ = CAT15_K
        sh_ = (cx + (25 - 4) * k_, cy + (1238 - CAT.CBOT) * k_)
        tip_ = people.cat_paw_tip(cx, cy, k_, st, side="r")
        tip_ = (tip_[0] + 10 * k_ * reach, tip_[1] + 6 * k_ * reach)
        cat += people.cat_forearm(sh_, tip_, k=(.55 + .35 * reach) * k_, seed=15)
        cat += blob(ellipse_pts(sh_[0] - 6 * k_, sh_[1], 28 * k_, 24 * k_, 14), CAT.CAT)
    cat = R.warm_tint(cat, .25)
    flx, fly = flame_world(cx, cy, CAT15_K, st["tail"])
    glow = PR.glow(flx, fly - 80, 150, .45, "#ffb347")
    # карточка: на «висит» новая кнопка втыкается (с отскоком), пустая карточка повисает на ней и качается
    ca = clamp((t - (T_VIS - .08)) / .12)
    card = ""
    if ca > 0:
        q = max(0.0, t - (T_VIS - .08))
        swing = 14 * math.exp(-2.6 * q) * math.sin(2 * math.pi * 1.7 * q + .6)
        k_ = 1.25 * (1 + .25 * (1 - ease_out(ca, 3)))
        card = R.light_tint(PR.pinned_card(CARD15[0], CARD15[1], k_, swing=swing, dust=0.0, web=0.0, t=t, seed=5), P)
    kot = hand_kot.kot(t, KOT_T0, KOT_DUR, KOT15[0], KOT15[1], KOT15[2], col="#f6e7c8")
    shadow = blob(ellipse_pts(cx, cy + 6, 200 * CAT15_K * .7, 22, 18), "#1a100c", .35)
    world = [sc["bg"], kot, card, shadow, cat, glow]
    # камера: хлёст вниз, затем медленный наезд 4 % к коту; мини-удар, когда слово дописано
    u = sm(t, T_A15 - .1, 21.82)
    s = lerp(1.15, 1.2, u) + .02 * bump(t, KOT_T0 + KOT_DUR, .35)
    ccx = lerp(-950, -960, u) + 4 * math.sin(t * 1.3)
    ccy = lerp(770, 790, u) + 3 * math.sin(t * 1.6)
    set_ink(s)
    g = f'<g transform="{lib.cam(ccx, ccy, s, lerp(.4, -.2, u))}">{"".join(world)}</g>'
    return whip_v(g, t, T_A15), BG


FRAMES["s15"] = s15
