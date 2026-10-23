"""Геометрия рилса ДО рендера: то, что в v12–v14 находилось только глазами после трёхминутного рендера (23.10).

Каждая проверка — по настоящей ошибке, которую ловил человек на листе кадров:
- `slivers` — обрывок рисунка у края окна плана: усы и ухо кота торчали из-под крупного плана часов (фразы 1 и 5,
  было ещё в v12), глаз и полоски щёк — над крупным планом телефона (v14, окно подняло правило fill_ink). Рисунок
  делится на связные пятна туши; пятно, от которого в окне видно 0 < доля < SLIVER_SHARE, — обрывок. Крупный план,
  который режет предмет нарочно (видно много), обрывком не считается.
- `doll_fit` — кукла не помещается в кадр: наезд твиста 0.16 резал хвост, большая кукла v12 (h 820) выходила за оба
  края. Осознанный крупный план — `"closeup": true`.
- `overlay_on_drawing` — рукописная надпись легла на рисунок: «Напарник» на уши кота, «?» на обод таймера (первая
  правка безопасной зоны, 23.10), «Напарник» на крупный план головы (держался 0.06 с в чужом плане, v14).
Все три — ошибки (рилс не рендерится), потому что каждая была настоящим браком на экране.
"""
import math

import cv2
import numpy as np

SLIVER_SHARE = 0.12        # видно меньше 12 % пятна туши — это обрывок, а не крупный план предмета
SLIVER_MIN_PX = 250        # и обрывок заметен: ≥ 250 точек сетки ¼ (калибровка 23.10: усы у часов v12 — 3100–5900,
#                            край кота у таймера — 1637, обод часов — 289; лампа у края сцены — 206, крошки — 68–105)
HERO_BLOB_SHARE = 0.02     # большое пятно (кот вместе с мебелью): у него обрывком считаются и тонкие кончики усов —
THIN_MIN_PX = 40           # от 40 точек (усы у края крупного плана таймера — 68, v14 и v15, найдено глазами 23.10)
BLOB_MIN_SHARE = 0.004     # пятна меньше 0.4 % исходника (крошки, штрихи бумаги) не считаются предметами
INK_GRAY = 165             # туша и тени рисунка темнее этого на кремовой бумаге
DOLL_EDGE_PX = 4           # тушь куклы ближе 4 px к краю кадра — обрывок хвоста или усов
OVERLAY_INK_SHARE = 0.03   # под рамкой надписи больше 3 % туши рисунка — надпись на рисунке
_INK = {}


def ink_blobs(reel, reel_dir, name):
    """Связные пятна туши исходника на сетке ¼: метки и площади (кэш на процесс)."""
    key = (reel_dir, name)
    if key not in _INK:
        g = cv2.cvtColor(reel.load_src(reel_dir, name), cv2.COLOR_RGB2GRAY)
        small = cv2.resize(g, (g.shape[1] // 4, g.shape[0] // 4), interpolation=cv2.INTER_AREA)
        ink = (small < INK_GRAY).astype(np.uint8)
        ink = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        n, lab, stats, _ = cv2.connectedComponentsWithStats(ink, connectivity=8)
        _INK[key] = (lab, stats[:, cv2.CC_STAT_AREA], ink)
    return _INK[key]


def window_rect(reel, view):
    """Окно плана [cx, cy, h] в координатах исходного кадра -> прямоугольник на сетке ¼ исходника (src ×2, сетка /4)."""
    cx, cy, h = view
    w = h * reel.W / reel.PH
    return [(cx - w / 2) / 2, (cy - h / 2) / 2, (cx + w / 2) / 2, (cy + h / 2) / 2]


def shot_times(s, n=6):
    """Моменты плана для проверки: начало (после хлёста — он смазан), середина, конец."""
    t0 = s["t0"] + (0.2 if s.get("whip") else 0.25 if s.get("zoom_in") else 0.0)   # вход смазан: обрывок не читается
    return list(np.linspace(t0, max(t0, s["t1"] - 1e-3), n))


def cut_blobs(lab, area, rect):
    """Обрывки у края окна: [(id, видно точек, доля, False)]. Крупный план может резать предмет — это монтаж; плохо,
    когда от пятна в окне торчит малая доля (< 12 %). Предмет, разрезанный пополам (будильник у края таймера), этим не
    ловится: пятна предметов на столе сливаются со столом, а вычитание линий стола и рамки модели со зрением дали
    ложные тревоги на проверенных планах (23.10) — это пункт осмотра листа глазами (docs/REELS_LESSONS.md)."""
    total = lab.size
    x0, y0, x1, y1 = (int(round(v)) for v in rect)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(lab.shape[1], x1), min(lab.shape[0], y1)
    if X1 <= X0 or Y1 <= Y0:
        return []
    ids, cnt = np.unique(lab[Y0:Y1, X0:X1], return_counts=True)
    out = []
    for i, c in zip(ids, cnt):
        if not i or area[i] <= BLOB_MIN_SHARE * total:
            continue
        share = c / area[i]; big = area[i] > HERO_BLOB_SHARE * total
        if share < SLIVER_SHARE and c >= (THIN_MIN_PX if big else SLIVER_MIN_PX):
            out.append((int(i), int(c), share, False))
    return out


def fit_window(reel, reel_dir, src, view, step=8, reach=320):
    """Ближайшее окно того же размера (или до 15 % меньше), которое ничего не режет; None — не нашлось."""
    lab, area, _ = ink_blobs(reel, reel_dir, src)
    cx, cy, h = view
    best = None
    for k in (1.0, 0.95, 0.9, 0.85):
        for dx in range(-reach, reach + 1, step):
            for dy in range(-reach // 2, reach // 2 + 1, step):
                d = math.hypot(dx, dy) + (1 - k) * 2000
                if best and d >= best[0]:
                    continue
                v = (cx + dx, cy + dy, h * k)
                if not cut_blobs(lab, area, window_rect(reel, v)):
                    best = (d, [round(cx + dx), round(cy + dy), round(h * k)])
        if best:
            break
    return best[1] if best else None


def to_spec(reel, v):
    """Окно после layout() -> как его писать в reel.json (высота делится обратно на view_scale)."""
    k = getattr(reel, "VIEW_K", 1.0)
    return [v[0], v[1], round(v[2] / k)]


def slivers(reel, reel_dir, shots):
    err = []
    for s in shots:
        if s.get("kind", "crop") != "crop" or "from" not in s:
            continue
        lab, area, _ = ink_blobs(reel, reel_dir, s["src"])
        for t in shot_times(s):
            view = reel.shot_view(s, t)
            bad = cut_blobs(lab, area, window_rect(reel, view))
            if bad:
                i, c, share, obj = max(bad, key=lambda b: b[1])
                what = f"у края обрывок рисунка — видно {share:.0%} пятна (усы, ухо, край предмета)"
                sug = [fit_window(reel, reel_dir, s["src"], s[k]) for k in ("from", "to") if k in s]
                tip = (f" Ближайшие чистые окна (в координатах reel.json): from {to_spec(reel, sug[0])}, to {to_spec(reel, sug[-1])}."
                       if all(sug) else " Чистого окна рядом нет — другой план.")
                err.append(f"план {s['t0']:.2f}–{s['t1']:.2f} с ({s['src']}) на {t:.2f} с: край окна {what}.{tip}"
                           " Вход наездом (zoom_in) расширяет окно — его тоже проверьте")
                break
    return err


def doll_mask(reel, s, zs):
    """Маска куклы плана на экране (без движения рига — поза покоя) при масштабе zs; (маска, x0, y0)."""
    rgba = reel.doll_frame(reel.DOLL_LIFE_PHASE, 20.0, [])
    R = reel._DOLL["rig"]
    bx0, _, bx1, by1 = (int(v) for v in R.bb)
    reg = rgba[0:by1, bx0:bx1, 3]
    h = s.get("h", 900) * zs
    sc = h / by1
    rw, rh = max(1, int((bx1 - bx0) * sc)), max(1, int(by1 * sc))
    m = cv2.resize(reg.astype(np.float32), (rw, rh), interpolation=cv2.INTER_AREA) > 0.3
    cx, cy = s.get("cx", reel.W / 2), s.get("cy", reel.PH * 0.55)
    return m, int(cx - rw / 2), int(cy - rh / 2)


def doll_zoom_max(s, events):
    z = max(s.get("zoom", (1.0, 1.06)))
    for e in events:
        if e.get("kind") == "punch" and s["t0"] <= e["t"] < s["t1"]:
            z *= 1 + e.get("amt", 0.14)
    return z


def doll_fit(reel, shots, events):
    err = []
    for s in shots:
        if s.get("kind") != "doll" or s.get("closeup"):
            continue
        m, x0, y0 = doll_mask(reel, s, doll_zoom_max(s, events))
        ys, xs = np.where(m)
        if not len(xs):
            continue
        left, right, bottom = x0 + xs.min(), x0 + xs.max(), y0 + ys.max()
        if left < DOLL_EDGE_PX or right > reel.W - 1 - DOLL_EDGE_PX or bottom > reel.PH - 1:
            err.append(f"кукла {s['t0']:.2f}–{s['t1']:.2f} с не помещается в кадр при наезде ×{doll_zoom_max(s, events):.2f}: "
                       f"x {left}–{right}, низ {bottom} (кадр 0–{reel.W - 1}, картинка до {reel.PH}). Меньше h или сдвиг cx; "
                       "осознанный крупный план — \"closeup\": true")
    return err


def overlay_on_drawing(reel, reel_dir, shots, events):
    """Рамка надписи (по туши букв) против рисунка под ней — во всех планах, где надпись видна."""
    err = []
    for e in events:
        if e["kind"] not in ("write", "mark"):
            continue
        im = reel.text_img(e["text"], reel.font(reel.HAND, e.get("size", 120), 700), reel.INK)
        gx0, gy0, gx1, gy1 = im.getchannel("A").getbbox()
        bx0, by0 = e["x"] - im.width / 2 + gx0, e["y"] - im.height / 2 + gy0
        bx1, by1 = e["x"] - im.width / 2 + gx1, e["y"] - im.height / 2 + gy1
        end = e["t"] + max(e.get("dur", 0.5), e.get("hold") or 0.0)
        for s in shots:
            kind = s.get("kind", "crop")
            started = s["t0"] - 0.01 <= e["t"] < s["t1"]
            if not (started or (kind == e.get("kind_of_shot", "crop") and s["t0"] < end and s["t1"] > e["t"])):
                continue
            share = 0.0
            if kind == "doll":
                m, x0, y0 = doll_mask(reel, s, doll_zoom_max(s, events))
                X0, Y0 = int(max(bx0, x0)), int(max(by0, y0))
                X1, Y1 = int(min(bx1, x0 + m.shape[1])), int(min(by1, y0 + m.shape[0]))
                if X1 > X0 and Y1 > Y0:
                    share = m[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0].mean() * (X1 - X0) * (Y1 - Y0) / ((bx1 - bx0) * (by1 - by0))
            elif kind == "crop" and "from" in s:
                _, _, ink = ink_blobs(reel, reel_dir, s["src"])
                vx, vy, vh = reel.shot_view(s, max(e["t"], s["t0"]))
                k = vh / reel.PH
                sx0, sy0 = (vx + (bx0 - reel.W / 2) * k) / 2, (vy + (by0 - reel.PH / 2) * k) / 2
                sx1, sy1 = (vx + (bx1 - reel.W / 2) * k) / 2, (vy + (by1 - reel.PH / 2) * k) / 2
                X0, Y0, X1, Y1 = (int(max(0, v)) for v in (sx0, sy0, sx1, sy1))
                X1, Y1 = min(X1, ink.shape[1]), min(Y1, ink.shape[0])
                if X1 > X0 and Y1 > Y0:
                    share = float(ink[Y0:Y1, X0:X1].mean())
            if share > OVERLAY_INK_SHARE:
                err.append(f"надпись «{e['text']}» ({e['t']:.2f} с) лежит на рисунке плана {s['t0']:.2f}–{s['t1']:.2f} с: "
                           f"под ней {share:.0%} туши. На чистую бумагу (сдвиг x/y) или короче hold, чтобы не уходила в чужой план")
                break
    return err


def check(reel, reel_dir, shots, events):
    return slivers(reel, reel_dir, shots) + doll_fit(reel, shots, events) + overlay_on_drawing(reel, reel_dir, shots, events)
