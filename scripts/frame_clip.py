#!/usr/bin/env python3
"""Клип одного кадра: рисунок на кремовой бумаге, подписи по словам голоса,
быстрый наезд на предмет, главная мысль карандашом, камера по плану shots.py.

Мир кадра — холст 16:9, увеличенный в UPSCALE раз (upscale.py) с впечённой
фактурой бумаги. Подписи схемы и дописанная главная мысль впекаются в мир в
момент появления — дальше двигаются вместе с рисунком, как нарисованные.
Экранный кадр — окно камеры, вырезанное из мира одним Lanczos-ресемплом.
Пока главная мысль пишется, её чернила живут в экранных координатах того
окна, где начали писать, и переносятся в текущее окно аффинным переносом
(камера в это время только дрейфует — план запрещает склейки и наезды).

prepare() — дорогая часть, общая для плана и рендера (холст, увеличение,
карта занятости); plan_clip() — план с учётом наезда в прошлом кадре
(последовательно по ролику); render() — клип в mp4 (параллельно)."""
import hashlib
import math
import json
import os
import subprocess

import numpy as np
from PIL import Image

import camera
import canvas
import labels as labels_mod
import long_edit
import placement
import shots
import upscale
import writeon

W, H = 1920, 1080
UPSCALE = 2
KEY_SIZES = (200, 175, 150, 125, 110)   # крупно, если есть место (критики: «мелкая, прижата к краю»)
KEY_MAX_W = 0.62
INK = np.array([14, 14, 16], np.float32)       # чёрная тушь (владелец 20.10: карандаш был серым — графит 52 x прозрачность 0.8)
END_FADE_SEC = 0.6
DIM = 0.3                # схема до сборки — 30% силы, остальное бумага (критик монтажа 04.10)
REVEAL_SEC = 0.35        # часть схемы проявляется за столько
REVEAL_MAX_SHARE = 0.25  # общий прямоугольник «подпись + часть» не больше четверти холста
RENDER_VERSION = 3   # 07.10: ход камеры сквозь склейку (camera.through)


def upscale_sig():
    """Способ и версия увеличения рисунка — в ключ кэша клипа (02.11: после смены на waifu2x сборщик брал старые
    клипы, и ролик выходил прежним до байта)."""
    return f"{upscale.method()}:{upscale.VERSION}:{os.environ.get('UPSCALE_NEURAL', '1')}"


def _hash(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def prepare(src_path, recs, objects, work, seed=0, tex=None):
    """Холст и мир кадра. recs — подписи генератора (labels_placed) в координатах
    src_path; пусто — подписей нет или они уже на картинке. objects — предметы
    [{name, box, word, role}] в координатах src_path. Возвращает dict."""
    img = Image.open(src_path).convert("RGB")
    if recs:
        img = labels_mod.flatten_paper(img, [r["box"] for r in recs])
    cv, off, on_paper = canvas.prepare(img)
    SH, SW = cv.shape[:2]
    ox, oy = off

    def shift(b):
        x0, y0, x1, y1 = b
        return (float(np.clip(x0 + ox, 0, SW)), float(np.clip(y0 + oy, 0, SH)),
                float(np.clip(x1 + ox, 0, SW)), float(np.clip(y1 + oy, 0, SH)))
    objs = []
    for o in objects or []:
        if o.get("box"):
            b = shift(o["box"])
            if b[2] - b[0] > 4 and b[3] - b[1] > 4:
                objs.append({**o, "box": b})
    world = upscale.upscale(cv, UPSCALE, cache_dir=os.path.join(work, "upscale"))
    if tex is None:
        tex = canvas.paper_texture()
    world = canvas.bake_texture(world, tex, seed=seed)
    final = Image.fromarray(cv)                       # холст со всеми подписями — для карты занятости
    for r in recs:
        labels_mod.draw_rec(final, r, 1.0, off)
    busy = placement.busy_map(np.asarray(final, np.float32), margin=8)
    # части схемы по подписям: рамка части от судьи, иначе — сама подпись с её стрелкой-указателем
    parts, have = [], 0
    for k, r in enumerate(recs):
        lb = shift(r["box"])
        pb = next((o["box"] for o in objs if o.get("role") == f"label:{k}"), None)
        have += pb is not None
        parts.append(dict(label=lb, part=pb))
    assemble = len(recs) >= 2 and have*2 >= len(recs)
    return dict(world=world, canvas=cv, off=off, on_paper=on_paper, SW=SW, SH=SH, recs=recs,
                objects=objs, busy=busy, final_rgb=np.asarray(final), parts=parts, assemble=assemble)


def reveal_mask(fr, i, scale):
    """Мягкая маска (в мире) того, что проявляется на слове подписи i: подпись со
    стрелкой-указателем и часть, которую она описывает."""
    from scipy import ndimage
    SW, SH = fr["SW"], fr["SH"]
    p = fr["parts"][i]
    lb = p["label"]
    lh = lb[3] - lb[1]
    rects = [(lb[0] - 0.8*lh, lb[1] - 0.8*lh, lb[2] + 0.8*lh, lb[3] + 0.8*lh)]
    if p["part"]:
        pb = p["part"]
        mx, my = 0.1*(pb[2] - pb[0]), 0.1*(pb[3] - pb[1])
        rects.append((pb[0] - mx, pb[1] - my, pb[2] + mx, pb[3] + my))
        u = (min(lb[0], pb[0]), min(lb[1], pb[1]), max(lb[2], pb[2]), max(lb[3], pb[3]))
        if (u[2] - u[0])*(u[3] - u[1]) <= REVEAL_MAX_SHARE*SW*SH:
            rects.append(u)
    m = np.zeros((SH*scale, SW*scale), np.float32)
    for x0, y0, x1, y1 in rects:
        m[max(0, int(y0*scale)):max(0, int(y1*scale)), max(0, int(x0*scale)):max(0, int(x1*scale))] = 1
    return np.clip(ndimage.gaussian_filter(m, 10*scale), 0, 1)[..., None]


def _screen(world, win, scale):
    x0, y0, x1, y1 = win
    return np.asarray(Image.fromarray(world).resize((W, H), Image.LANCZOS,
                                                    box=(x0*scale, y0*scale, x1*scale, y1*scale)), np.float32)


def _parallax_frame(f, fr, win, seg, t):
    """Кадр плана с параллаксом: глубина рисунка (кэш на кадр) в том же окне, сдвиг по ходу плана."""
    import depth_parallax as dp
    if "_depth" not in fr:
        d = dp.depth_map(fr["canvas"], cache_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "depth_cache"))
        fr["_depth"] = (np.repeat(d[..., None], 3, axis=2) * 255).astype(np.uint8)
    x0, y0, x1, y1 = win
    d = np.asarray(Image.fromarray(fr["_depth"]).resize((W, H), Image.BILINEAR, box=(x0, y0, x1, y1)), np.float32)[..., 0] / 255
    tau = (t - seg["t0"]) / max(1e-6, seg["t1"] - seg["t0"])
    return dp.apply(f, dp.prepare(f, d), tau, seg["parallax"]["dx"], seg["parallax"]["dz"])


def key_layout(fr, text, win, seed=9):
    """Где и каким кеглем писать главную мысль в окне win. (letters, (cx, cy), кегль) или None."""
    scr = _screen(np.asarray(Image.fromarray(fr["final_rgb"]).resize(
        (fr["SW"]*UPSCALE, fr["SH"]*UPSCALE), Image.BILINEAR)), win, UPSCALE)

    def wh(sz):
        return writeon.measure(text, sz, KEY_MAX_W*W)
    # рядом со своим предметом (критики 04.10: надпись «висела в пустоте» отдельно от сцены)
    anchor = next((o["box"] for o in fr.get("objects", []) if o.get("role") == "key_anchor"), None)
    obj = None
    if anchor:
        s_ = W/(win[2] - win[0])
        obj = ((anchor[0] - win[0])*s_, (anchor[1] - win[1])*s_, (anchor[2] - win[0])*s_, (anchor[3] - win[1])*s_)
        if obj[2] < 0 or obj[3] < 0 or obj[0] > W or obj[1] > H:
            obj = None
    size, pl = placement.choose_fit(scr, obj, wh, KEY_SIZES)
    if not pl and obj is not None:
        size, pl = placement.choose_fit(scr, None, wh, KEY_SIZES)
    if not pl:
        return None
    cx, cy = pl["center"]
    return writeon.layout(text, size, W, H, cx, cy, seed=seed, max_w=KEY_MAX_W*W), (cx, cy), size


def letters_box_world(letters, win):
    """Рамка надписи (раскладка writeon.layout в экранных координатах окна win) в координатах холста."""
    xs, ys = [], []
    for L in letters or []:
        for m in [L.get("soft")] + list(L.get("dots") or []):
            if m is None:
                continue
            yy, xx = np.nonzero(m > 0.2)
            if len(xx):
                xs += [int(xx.min()), int(xx.max())]; ys += [int(yy.min()), int(yy.max())]
    if not xs:
        return None
    s_ = (win[2] - win[0])/W
    return (win[0] + min(xs)*s_, win[1] + min(ys)*s_, win[0] + (max(xs) + 1)*s_, win[1] + (max(ys) + 1)*s_)


PLAN_PASSES = 4                 # план ↔ раскладка надписи: обычно сходится за 2-3 (замер эп.01: 3)


def _same_window(a, b, tol=0.5):
    """Окна совпадают с точностью до полпикселя холста."""
    return max(abs(x - y) for x, y in zip(a, b)) < tol


KEY_SPEEDUPS = (1.0, 1.25, 1.5)   # не успевает дописаться и постоять — карандаш быстрее, но не больше чем в 1.5 раза


ACCENT_SIZES = (140, 120, 100)   # акцент от руки — мельче главной мысли: та главнее


def accent_layout(fr, text, win, seed=11):
    """(раскладка букв, центр, кегль) рукописного акцента в окне win — у главного предмета,
    по пустому месту; None — места нет. Тот же карандаш, что у главной мысли (writeon)."""
    scr = _screen(np.asarray(Image.fromarray(fr["final_rgb"]).resize(
        (fr["SW"]*UPSCALE, fr["SH"]*UPSCALE), Image.BILINEAR)), win, UPSCALE)

    def wh(sz):
        return writeon.measure(text, sz, KEY_MAX_W*W)
    subj = shots.subject_box(fr["busy"], fr["objects"])
    obj = None
    if subj:
        s_ = W/(win[2] - win[0])
        obj = ((subj[0] - win[0])*s_, (subj[1] - win[1])*s_, (subj[2] - win[0])*s_, (subj[3] - win[1])*s_)
    size, pl = placement.choose_fit(scr, obj, wh, ACCENT_SIZES)
    if not pl:
        return None
    cx, cy = pl["center"]
    return writeon.layout(text, size, W, H, cx, cy, seed=seed, max_w=KEY_MAX_W*W), (cx, cy), size


def plan_clip(fr, D, words, key=None, last_punch=-1e9, T0=0.0, zoom_in=True, fps=24, accent=None, mascot=None,
              first_of_film=False):
    """План кадра (shots.plan) + раскладка главной мысли. Главная мысль, которой
    нет места, не пишется — с записью в notes. Не успевает — пишется быстрее
    (KEY_SPEEDUPS), а не пропадает: живой ролик 04.10 потерял «только открыть»,
    потому что фраза стоит в конце кадра.
    mascot — {text, state, seed}: поставить живую куклу героя (mascot_live) — ДО раскладки
    мысли и плана камеры, чтобы они её обходили. Нет рига или места — кадр без куклы."""
    ms = None
    if mascot:
        import mascot_live
        if mascot_live.available():
            ms = mascot_live.place(fr, mascot)
    key_l = None
    if key:
        key_l = key_layout(fr, key, camera.full_window(fr["SW"], fr["SH"]))
    parts = [pp["part"] or pp["label"] for pp in fr.get("parts", [])]
    acc_l = None
    if accent:
        acc_l = accent_layout(fr, accent, camera.full_window(fr["SW"], fr["SH"]))
    acc_speed, acc_dur = 1.0, 0.0
    if acc_l:
        at = shots.word_time(accent, words) if words else None
        for acc_speed in KEY_SPEEDUPS:     # как у главной мысли: быстрее, а не пропасть
            acc_dur = writeon.plan(acc_l[0], fps, factor=acc_speed)[1]
            if at is None or at + acc_dur + shots.KEY_HOLD_SEC <= D - 0.2:
                break
    p, speed = None, 1.0
    key_box = acc_box = None
    key_fit = acc_fit = None                  # (окно момента, раскладка) последнего прохода
    for _pass in range(PLAN_PASSES):
        # план -> раскладка надписи в окне момента -> рамка надписи -> план заново, уже с рамкой: пока
        # дописанное стоит, склейки идут только в планы, где оно целиком в кадре (shots.plan, key_box).
        # Сходимость — по ОКНУ момента: при том же окне раскладка та же (детерминирована), рамка та же
        for speed in (KEY_SPEEDUPS if key_l else (1.0,)):
            key_dur = writeon.plan(key_l[0], fps, factor=speed)[1] if key_l else 0.0
            p = shots.plan(D, fr["busy"], words, fr["recs"], fr["objects"], key if key_l else None, key_dur,
                           last_punch=last_punch, T0=T0, zoom_in=zoom_in, parts=parts,
                           accent=accent if acc_l else None, accent_dur=acc_dur, first_of_film=first_of_film,
                           key_box=key_box, accent_box=acc_box)
            if not key_l or p["key_time"] is not None:
                break
        nk = na = None
        if key_l and p["key_time"] is not None:
            win = shots.window_at(p, p["key_time"], fr["SW"], fr["SH"])
            nk = key_fit if key_fit and _same_window(key_fit[0], win) else (win, key_layout(fr, key, win))
        if acc_l and p.get("accent_time") is not None:
            win = shots.window_at(p, p["accent_time"], fr["SW"], fr["SH"])
            na = acc_fit if acc_fit and _same_window(acc_fit[0], win) else (win, accent_layout(fr, accent, win))
        converged = (nk is key_fit) and (na is acc_fit)
        key_fit, acc_fit = nk, na
        if converged:
            break
        key_box = letters_box_world(key_fit[1][0], key_fit[0]) if key_fit and key_fit[1] else None
        acc_box = letters_box_world(acc_fit[1][0], acc_fit[0]) if acc_fit and acc_fit[1] else None
    else:
        p["notes"].append("удержание надписи: план и раскладка не сошлись за отведённые проходы — рамка последнего прохода")
    p["assemble"] = bool(fr.get("assemble"))
    if mascot and ms is None:
        p["notes"].append("живой кукле нет места рядом с предметом — кадр без неё" if mascot_live.available()
                          else "живая кукла: рига нет на диске — кадр без неё")
    if ms:
        if ms.get("share", mascot_live.HEIGHT_SHARE) < mascot_live.HEIGHT_SHARE:
            p["notes"].append(f"живая кукла уменьшена до {ms['share']:.0%} высоты: рядом с предметом тесно")
        ms["actions"] = mascot_live.plan_actions(D, words, mascot.get("text", ""), ms["gaze"], seed=int(mascot.get("seed", 0)),
                                                 action=mascot.get("action"), mood=mascot.get("mood"))
        ms["seed"] = int(mascot.get("seed", 0)); ms["sig"] = mascot_live.signature(); ms["state"] = mascot.get("state")
        ms["look"] = mascot.get("look") or {}
        p["mascot"] = ms
    if accent and not acc_l:
        p["notes"].append(f"акценту «{accent}» нет места — не пишется")
    if p.get("accent_time") is not None:
        win, al = acc_fit
        if al and writeon.plan(al[0], fps, factor=acc_speed)[1] <= acc_dur*1.05 + 0.1:
            p["accent"] = dict(text=accent, win=win, center=al[1], size=al[2], speed=acc_speed)
        else:
            p["notes"].append(f"акценту «{accent}» нет места в плане момента — не пишется")
            p["accent_time"] = None
    if key and not key_l:
        p["notes"].append(f"главной мысли «{key}» нет места на кадре — не пишется")
    if key_l and p["key_time"] is not None:
        if speed > 1.0:
            p["notes"] = [n for n in p["notes"] if "главная мысль" not in n]
            p["notes"].append(f"главная мысль пишется в {speed:.2f} раза быстрее, чтобы успеть и постоять")
        # писать в окне, где камера будет в этот момент (план держит его без склеек)
        win, kl = key_fit
        if kl and writeon.plan(kl[0], fps, factor=speed)[1] <= key_dur*1.05 + 0.1:
            p["key"] = dict(text=key, win=win, center=kl[1], size=kl[2], speed=speed)
        else:
            p["notes"].append(f"главной мысли «{key}» нет места в плане момента — не пишется")
            p["key_time"] = None
    return p


HAND_SIZES = (104, 92, 80)     # рукописная подпись к предмету — мельче мысли (KEY_SIZES): это подпись, не мысль
HAND_MAX_W = 0.40
HAND_SIZES_ALL = (300, 260, 220, 190, 160, 130, 112, 96, 84, 74, 64)   # кегль экрана в окне раскладки
HAND_MIN_FULL, HAND_MAX_FULL = 52, 76   # кегль на общем плане: подпись рядом с рисунком, а не поверх (было 64–96);
                               # не мельче: написанная на крупном плане кеглем 80 на общем выходила 25 px (L03 04.11)
HAND_HOLD_SEC = 2.35           # пока подпись видна (PENCIL_SHOW_SEC + уход) — она целиком в кадре
HAND_PAD = 22                  # «точка» без рамки: предмет — квадрат ±HAND_PAD px холста вокруг неё
PENCIL_SHOW_SEC = 2.0          # дописанная надпись карандашом стоит столько и уходит (не висит до конца картинки)
PENCIL_FADE_SEC = 0.35
HAND_TAIL = 0.6                # подпись дописывается не позже чем за 0,6 с до конца кадра: иначе её режет склейка


def hand_target(fr, to):
    """Рамка предмета подписи в координатах холста. to — [x, y] или [x0, y0, x1, y1] в пикселях исходного рисунка
    (как окна edit.json) либо роль предмета от судьи («subject», «hero», «hero_head», «detail»…)."""
    if isinstance(to, str):
        return next((tuple(o["box"]) for o in fr["objects"] if o.get("role") == to or o.get("name") == to), None)
    ox, oy = fr["off"]
    if len(to) == 2:
        return (to[0] + ox - HAND_PAD, to[1] + oy - HAND_PAD, to[0] + ox + HAND_PAD, to[1] + oy + HAND_PAD)
    return (to[0] + ox, to[1] + oy, to[2] + ox, to[3] + oy)


def hand_layout(fr, text, box, win, at=None, seed=13, arrow=True, avoid=()):
    """Рукописная подпись к предмету box (холст) в окне win: раскладка букв и стрелка тем же карандашом.
    Место — пустая бумага рядом с предметом (placement.choose: не на рисунке, стрелка не режет рисунок); at — центр
    подписи в пикселях исходного рисунка, если место выбрано руками. None — места нет."""
    scr = _screen(np.asarray(Image.fromarray(fr["final_rgb"]).resize(
        (fr["SW"]*UPSCALE, fr["SH"]*UPSCALE), Image.BILINEAR)), win, UPSCALE)
    s_ = W/(win[2] - win[0])
    obj = ((box[0] - win[0])*s_, (box[1] - win[1])*s_, (box[2] - win[0])*s_, (box[3] - win[1])*s_)
    if obj[2] < 0 or obj[3] < 0 or obj[0] > W or obj[1] > H:
        return None                                   # предмета нет в кадре — подписывать нечего

    def wh(sz):
        return writeon.measure(text, sz, HAND_MAX_W*W)
    b = placement.busy_map(scr)
    for a in avoid:                                   # уже стоящие надписи кадра — как рисунок (L03: «погода?» и
        ax0, ay0 = int((a[0] - win[0])*s_) - 30, int((a[1] - win[1])*s_) - 30     # «40 минут спустя» наползали)
        ax1, ay1 = int((a[2] - win[0])*s_) + 30, int((a[3] - win[1])*s_) + 30
        b[max(0, ay0):max(0, ay1), max(0, ax0):max(0, ax1)] = 1.0
    point = obj
    obj = _blob_box(b, obj)                           # подпись встаёт у края предмета, а не у точки в его середине
    res = None
    k_full = (win[2] - win[0])/fr["SW"]               # доля холста в окне: 1 — общий план
    sizes = [z for z in HAND_SIZES_ALL if z*k_full >= HAND_MIN_FULL and z*k_full <= HAND_MAX_FULL]
    for size in sizes:
        tw, th = wh(size)
        if at is not None:
            cx, cy = (at[0] + fr["off"][0] - win[0])*s_, (at[1] + fr["off"][1] - win[1])*s_
            tb = (cx - tw/2, cy - th/2, cx + tw/2, cy + th/2)
            res = dict(center=(cx, cy), arrow=placement.arrow_points(tb, obj, th, b))
            break
        r = placement.choose(scr, obj, (tw, th), b=b)
        if r:
            res = r
            break
    if res is None:
        return None
    letters = writeon.layout(text, size, W, H, res["center"][0], res["center"][1], seed=seed, max_w=HAND_MAX_W*W)
    arr, why = _hand_arrow(b, res["center"], wh(size), obj, point) if arrow else (None, "стрелка не нужна")
    if why:
        _HAND_WHY[text] = why
    if arr:
        letters = letters + [writeon.arrow_letter(arr[0], arr[1], arr[2], size, W, H, seed=seed)]
    return letters, res["center"], size, arr


_HAND_WHY = {}
HAND_TIP_INK = 0.35            # кончик стрелки — там, где от предмета начинается бумага (busy_map ниже порога)
HAND_SHAFT_BUSY = 0.45         # древко по рисунку гуще этого — стрелки нет, только подпись рядом (0,25 снимал 6 из 33)


HAND_BLOB_INK = 0.5            # предмет вокруг точки-цели — связный рисунок гуще этого
HAND_BLOB_MAX = 0.30           # не больше трети кадра по каждой стороне: слитый рисунок — окрестность точки


def _blob_box(b, box):
    """Рамка предмета вокруг точки-цели по карте занятости: связная область рисунка, содержащая центр точки, но не
    шире HAND_BLOB_MAX кадра по каждой стороне (вся сцена бывает одним куском). Цель-рамку не трогает."""
    if (box[2] - box[0]) > 0.12*b.shape[1] or (box[3] - box[1]) > 0.12*b.shape[0]:
        return box
    from scipy import ndimage
    cx, cy = int((box[0] + box[2])/2), int((box[1] + box[3])/2)
    if not (0 <= cx < b.shape[1] and 0 <= cy < b.shape[0]) or b[cy, cx] < HAND_BLOB_INK:
        return box
    lab, _ = ndimage.label(b >= HAND_BLOB_INK)
    ys, xs = np.nonzero(lab == lab[cy, cx])
    hw, hh = HAND_BLOB_MAX*b.shape[1]/2, HAND_BLOB_MAX*b.shape[0]/2
    x0, x1 = max(xs.min(), cx - hw), min(xs.max(), cx + hw)
    y0, y1 = max(ys.min(), cy - hh), min(ys.max(), cy + hh)
    return (float(x0), float(y0), float(x1), float(y1))


def _hand_arrow(b, center, twh, obj, point=None):
    """Стрелка от подписи к предмету: кончик у края рисунка предмета, а не в его середине (цель — точка внутри
    предмета; прежняя стрелка в точку шла по самому рисунку, и проверка «не режет рисунок» её молча снимала — замер
    на синтетике). (p0, p1, изгиб) или None."""
    tw, th = twh
    tb = (center[0] - tw/2, center[1] - th/2, center[0] + tw/2, center[1] + th/2)
    p0, _, bend = placement.arrow_points(tb, obj, th, b)
    tgt = point or obj
    oc = np.array([(tgt[0] + tgt[2])/2, (tgt[1] + tgt[3])/2])
    d = np.asarray(p0) - oc
    L = float(np.hypot(*d))
    if L < 1:
        return None, "подпись на предмете"
    d /= L
    def at(q):
        return float(b[int(np.clip(q[1], 0, b.shape[0] - 1)), int(np.clip(q[0], 0, b.shape[1] - 1))])
    # «бумага» — уровень там, где стоит подпись (светлый экран, серая стена — тоже фон для неё), а не ноль
    ground = at(np.asarray(p0))
    tip = None
    for s_ in np.arange(0.0, L, 4.0):
        q = oc + d*s_
        if at(q) < max(HAND_TIP_INK, ground + 0.12):
            tip = oc + d*min(L, s_ + 10)
            break
    if tip is None:
        return None, "от точки до подписи сплошной рисунок"
    if np.hypot(*(np.asarray(p0) - tip)) < 0.6*th:
        return None, "подпись вплотную к предмету"
    busy = placement._line_busy(b, p0, tuple(tip))
    if busy > HAND_SHAFT_BUSY:
        return None, f"древко пошло бы по рисунку ({busy:.2f})"
    return (tuple(map(float, p0)), tuple(map(float, tip)), float(bend)), None


def hand_plan(fr, p, hand, D=None):
    """Рукописные подписи кадра (fx.json hand) — в окне плана, где их пишут; после письма планы держат подпись со
    стрелкой целиком или вне кадра (long_edit.keep_text). hand — [{text, t (с от начала клипа), to, at?, arrow?}]."""
    p["hand"] = []
    manual = any(s.get("kind") == "manual" for s in p["segments"])
    holds = []                                         # (начало, конец удержания, рамка с целью, рамка подписи)
    placed = []                                        # рамки надписей кадра на холсте: мысль, акцент, прошлые подписи
    for kind in ("key", "accent"):
        it = p.get(kind)
        if it and p.get(f"{kind}_time") is not None:
            L = writeon.layout(it["text"], it["size"], W, H, it["center"][0], it["center"][1], max_w=KEY_MAX_W*W)
            wb = letters_box_world(L, it["win"])
            if wb is not None:
                placed.append(wb)
    for k, h in enumerate(sorted(hand or [], key=lambda h: h["t"])):
        box = hand_target(fr, h["to"])
        if box is None:
            p["notes"].append(f"подпись «{h['text']}»: предмет {h['to']} не найден — не пишется")
            continue
        # раскладка — по всему рисунку (там больше бумаги и цель всегда видна), как у мысли карандашом; планы, пока
        # подпись пишется и читается, расширяются до неё (hold_text). Прежняя раскладка в окне момента на тесных ручных
        # планах L03 не находила места у 9 из 33 подписей, а написанная на крупном плане на общем выходила в 25 px
        t = h["t"]
        win = camera.full_window(fr["SW"], fr["SH"])
        res = hand_layout(fr, h["text"], box, win, at=h.get("at"), seed=13 + k, arrow=h.get("arrow", True),
                          avoid=placed)
        if res is None:
            p["notes"].append(f"подпись «{h['text']}»: на рисунке нет места рядом с предметом — не пишется")
            continue
        letters, center, size, arr = res
        if arr is None and h.get("arrow", True):
            p["notes"].append(f"подпись «{h['text']}»: без стрелки — {_HAND_WHY.pop(h['text'], 'места нет')}")
        dur = writeon.plan(letters, 24)[1]
        if D is not None and t + dur > D - HAND_TAIL:     # слово в конце кадра — начать раньше, чтобы успеть дописать
            t = max(0.0, D - HAND_TAIL - dur)
            p["notes"].append(f"подпись «{h['text']}»: слово в конце кадра — пишется с {t:.2f} с, раньше слова")
        t_end = t + dur
        p["hand"].append(dict(text=h["text"], t=t, end=t_end, win=win, center=center, size=size, arrow=arr,
                              seed=13 + k, target=box))
        wb = letters_box_world(letters, win)
        if wb is not None:
            placed.append(wb)
        if manual and wb is not None:
            # и подпись, и то, на что показывает стрелка (L03: «Глория Марк» стояла, а стрелка уходила за край кадра)
            hb = (min(wb[0], box[0]), min(wb[1], box[1]), max(wb[2], box[2]), max(wb[3], box[3])) if arr else wb
            holds.append((t, t_end + HAND_HOLD_SEC, hb, wb))
    # после удержания — подпись целиком или вне кадра; пока пишется и ещё HAND_HOLD_SEC — целиком в кадре. Удержание
    # последним: оно главнее. Пересекающиеся удержания — одной рамкой (L03, фр.54: «палец дёрнулся» выталкивал из
    # кадра только что написанное «20 минут про котов»)
    for s_ in p["segments"]:
        on = [hb for t0, t1, hb, wb in holds if t0 < s_["t1"] and s_["t0"] < t1]
        if on:
            u = (min(b[0] for b in on), min(b[1] for b in on), max(b[2] for b in on), max(b[3] for b in on))
            long_edit.hold_text([s_], s_["t0"], s_["t1"], u, fr["SW"], fr["SH"])
    return p


def _warp(alpha, src_win, dst_win):
    """Альфа в экранных координатах окна src_win -> экранные координаты окна dst_win."""
    s_src = W/(src_win[2] - src_win[0]); s_dst = W/(dst_win[2] - dst_win[0])
    # экранная точка dst -> мир -> экранная точка src
    a = s_src/s_dst
    c = (dst_win[0] - src_win[0])*s_src
    f = (dst_win[1] - src_win[1])*s_src
    im = Image.fromarray(np.clip(alpha*255, 0, 255).astype(np.uint8))
    return np.asarray(im.transform((W, H), Image.AFFINE, (a, 0, c, 0, a, f), Image.BILINEAR), np.float32)/255


def _bake_alpha(world, alpha, win, scale, color):
    """Впечь экранную альфу окна win в мир (масштаб scale)."""
    x0, y0, x1, y1 = [v*scale for v in win]
    bw, bh = int(round(x1 - x0)), int(round(y1 - y0))
    a = np.asarray(Image.fromarray(np.clip(alpha*255, 0, 255).astype(np.uint8)).resize((bw, bh), Image.LANCZOS),
                   np.float32)/255
    X0, Y0 = int(round(x0)), int(round(y0))
    ys = slice(max(0, Y0), min(world.shape[0], Y0 + bh)); xs = slice(max(0, X0), min(world.shape[1], X0 + bw))
    aa = a[ys.start - Y0:ys.stop - Y0, xs.start - X0:xs.stop - X0][..., None]
    sub = world[ys, xs].astype(np.float32)
    world[ys, xs] = np.clip(sub*(1 - aa) + color*aa, 0, 255).round().astype(np.uint8)


def _cam_window(win, cam, SW, SH):
    """Окно плана с камерой сцены поверх: zoom > 1 — ближе, dx/dy — сдвиг в пикселях экрана."""
    x0, y0, x1, y1 = win
    k = (x1 - x0)/W
    cx, cy = (x0 + x1)/2 - cam.get("dx", 0.0)*k, (y0 + y1)/2 - cam.get("dy", 0.0)*k
    return camera.window(cx, cy, (x1 - x0)/max(1e-6, cam.get("zoom", 1.0)), SW, SH)


def _roll(f, deg):
    if abs(deg) < 1e-3:
        return f
    import cv2
    M = cv2.getRotationMatrix2D((W/2, H/2), deg, 1.0 + abs(math.radians(deg))*0.9)   # чуть ближе: углы без пустоты
    return cv2.warpAffine(np.ascontiguousarray(f, np.float32), M, (W, H), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT)


def render(fr, p, D, out, fps=24, end_fade=False, crf="18", anim=None, fx=None):
    """Клип в out. Возвращает [(t0, t1, kind)] штрихов карандаша (от начала клипа).
    anim — сцена движения внутри рисунка (videos/NN/anim/<имя>.py, класс Scene): frame(t, world) -> world с
    движущимися слоями, cam(t) -> {zoom, dx, dy, rot} поверх камеры плана (хук длинного ролика, 27.10).
    fx — события long_fx (кот-ведущий с размытием сцены, жирные строки) поверх готового кадра (28.10)."""
    SW, SH = fr["SW"], fr["SH"]
    track = None
    full = fr["world"].copy()                  # рисунок целиком (и подписи, когда появятся)
    assemble = p.get("assemble") and len(fr["recs"]) >= 2
    if assemble:
        world = (full.astype(np.float32)*DIM + canvas.CREAM*(1 - DIM)).round().astype(np.uint8)
    else:
        world = full
    n = max(1, int(round(D*fps)))
    lab_t = list(p["label_times"])
    shown = [False]*len(fr["recs"])
    # всё, что пишется карандашом: главная мысль и акцент — один и тот же карандаш и звук
    writes, cues = [], []
    for item, t0, seed in ((p.get("key"), p.get("key_time"), 9), (p.get("accent"), p.get("accent_time"), 11)):
        if not item or t0 is None:
            continue
        L = writeon.layout(item["text"], item["size"], W, H, item["center"][0], item["center"][1], seed=seed,
                           max_w=KEY_MAX_W*W)
        ev, T = writeon.plan(L, fps, t0=t0, factor=item.get("speed", 1.0))
        writes.append(dict(ink=writeon.Ink(L, ev, H, W), end=t0 + T, win=item["win"], baked=False,
                           life=t0 + T + PENCIL_SHOW_SEC))
        cues += [(e["t0"], e["t1"], e["kind"]) for e in ev]
    for h in p.get("hand") or []:              # рукописные подписи к предметам со стрелкой — тот же карандаш
        L = writeon.layout(h["text"], h["size"], W, H, h["center"][0], h["center"][1], seed=h["seed"],
                           max_w=HAND_MAX_W*W)
        if h.get("arrow"):
            L = L + [writeon.arrow_letter(h["arrow"][0], h["arrow"][1], h["arrow"][2], h["size"], W, H, seed=h["seed"])]
        ev, T = writeon.plan(L, fps, t0=h["t"])
        writes.append(dict(ink=writeon.Ink(L, ev, H, W), end=h["t"] + T, win=h["win"], baked=False,
                           life=h["t"] + T + PENCIL_SHOW_SEC))
        cues += [(e["t0"], e["t1"], e["kind"]) for e in ev]
    cues.sort()
    if fx:
        import long_fx
        # кот-ведущий не уводит в размытие недописанную мысль (критик L02: «его возвращают» ушла в размытие на
        # «его возвраща-», целиком видна 0,25 с): ведущий выходит, когда мысль дописана и простояла KEY_HOLD_SEC
        fx = long_fx.after_writing(fx, [w["end"] for w in writes], shots.KEY_HOLD_SEC)
        def peek(tt):                                  # кадр плана в момент tt без надписей — куда встанет строка
            return _screen(world, shots.window_at(p, tt, SW, SH), UPSCALE)
        track = long_fx.Track(fx, D, peek=peek)
    doll = None
    if p.get("mascot"):
        import mascot_live
        doll = mascot_live.Layer(p["mascot"], D)
        world = mascot_live.bake_shadow(world, p["mascot"], SW, SH, UPSCALE)   # тень под лапами — в мире, как у предметов
        if assemble and full is not world:
            full = mascot_live.bake_shadow(full, p["mascot"], SW, SH, UPSCALE)
    prev_world, fade_from, fade_len = None, None, shots.LABEL_FADE_SEC
    tmp = out + ".tmp.mp4"
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(fps), "-i", "-", "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium",
                             "-crf", crf, "-pix_fmt", "yuv420p", "-r", str(fps), tmp], stdin=subprocess.PIPE)
    try:
        for k in range(n):
            t = k/fps
            for i, lt in enumerate(lab_t):
                if not shown[i] and t >= lt:
                    prev_world, fade_from = world.copy(), lt
                    off2 = (fr["off"][0]*UPSCALE, fr["off"][1]*UPSCALE)
                    if assemble:
                        big = Image.fromarray(full)
                        labels_mod.draw_rec(big, fr["recs"][i], UPSCALE, off2)
                        full = np.asarray(big).copy()
                        last = all(shown[j] or j == i for j in range(len(shown)))
                        m = 1.0 if last else reveal_mask(fr, i, UPSCALE)   # последняя — схема целиком
                        world = (world*(1 - m) + full*m).round().astype(np.uint8) if not last else full.copy()
                        fade_len = REVEAL_SEC
                    else:
                        big = Image.fromarray(world)
                        labels_mod.draw_rec(big, fr["recs"][i], UPSCALE, off2)
                        world = np.asarray(big).copy()
                        fade_len = shots.LABEL_FADE_SEC
                    shown[i] = True
            win = shots.window_at(p, t, SW, SH)
            cam = anim.cam(t) if anim is not None else {}
            if cam:
                win = _cam_window(win, cam, SW, SH)
            seg = next((s_ for s_ in p["segments"] if s_["t0"] <= t < s_["t1"]), p["segments"][-1])
            manual = seg.get("kind") == "manual"
            if manual:                                 # ручной монтаж: тряска на ударе
                dx, dy = long_edit.shake_px(seg, t)
                if dx or dy:
                    win = _cam_window(win, {"dx": dx, "dy": dy}, SW, SH)
            base = anim.frame(t, world) if anim is not None else world
            f = _screen(base, win, UPSCALE)
            if manual and seg.get("parallax"):          # объём по глубине — редкий эффект ручного плана (02.11)
                f = _parallax_frame(f, fr, win, seg, t)
            if prev_world is not None and t - fade_from < fade_len:
                a = camera.ease_io((t - fade_from)/fade_len)
                f = _screen(prev_world, win, UPSCALE)*(1 - a) + f*a
            elif prev_world is not None:
                prev_world = None
            if doll is not None:                      # кукла — рисунок на бумаге: под карандашом, над подписями
                f = doll.composite(f, t, win, W, H)
            for wr in writes:
                if wr["baked"]:
                    continue
                if wr.get("life") is not None:        # надпись живёт, пока её читают, и уходит (владелец 04.11:
                    if t >= wr["end"] + 1.0/fps:       # «карандаша слишком много» — висела до конца картинки)
                        if "still" not in wr:
                            wr["ink"].advance(wr["end"] + 1.0)
                            wr["still"] = wr["ink"].alpha()
                        al = wr["still"]*float(np.clip(1 - (t - wr["life"])/PENCIL_FADE_SEC, 0, 1))
                        if t >= wr["life"] + PENCIL_FADE_SEC:
                            wr["baked"] = True         # ушла: больше не рисуется
                            continue
                    else:
                        wr["ink"].advance(t)
                        al = wr["ink"].alpha()
                    if al.any():
                        al = _warp(al, wr["win"], win)
                        f = f*(1 - al[..., None]) + INK*al[..., None]
                    continue
                wr["ink"].advance(t)
                al = wr["ink"].alpha()
                if t >= wr["end"] + 1.0/fps:
                    _bake_alpha(world, al, wr["win"], UPSCALE, INK)
                    if assemble and full is not world:
                        _bake_alpha(full, al, wr["win"], UPSCALE, INK)   # иначе следующее проявление её сотрёт
                    wr["baked"] = True
                    base = anim.frame(t, world) if anim is not None else world
                    f = _screen(base, win, UPSCALE)
                    if doll is not None:              # кадр пересчитан с нуля — кукла снова (из кэша кадра);
                        f = doll.composite(f, t, win, W, H)   # без этого она пропадала ровно на один кадр (пилот 07.10)
                elif al.any():
                    al = _warp(al, wr["win"], win)
                    f = f*(1 - al[..., None]) + INK*al[..., None]
            if cam.get("zoom_blur", 0.0) > 0.002:      # правило 28 и в длинном: размытие влёта, пока камера летит
                import anim as anim_mod
                f = anim_mod.zoom_blur(np.asarray(f, np.float32), cam["zoom_blur"])
            if cam.get("rot"):
                f = _roll(f, cam["rot"])
            if manual:                                 # прожектор и хлёст — поверх картинки, под затемнением конца
                f = long_edit.whip(long_edit.spot(f, seg, t, win, W, H), seg, t)
            if track is not None:                      # кот-ведущий и жирный текст — поверх всего, под затемнением конца
                f = track.apply(np.asarray(f, np.float32), t)
            if end_fade and t > D - END_FADE_SEC:
                a = camera.ease_io((t - (D - END_FADE_SEC))/END_FADE_SEC)
                f = f*(1 - a) + canvas.CREAM*a
            proc.stdin.write(np.clip(f, 0, 255).round().astype(np.uint8).tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg не записал клип")
    except Exception:
        proc.kill()
        raise
    os.replace(tmp, out)
    return cues


def plan_record(p):
    """План в JSON-виде для отчёта."""
    # кортежи json пишет сам; numpy-скаляры — числом, а не строкой (иначе смена типа одного поля меняла бы хэш клипа)
    return json.loads(json.dumps(p, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)))
