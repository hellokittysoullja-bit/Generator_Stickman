#!/usr/bin/env python3
"""Ручной монтаж кадров длинного ролика — как в рилсах (владелец 28.10: «хотя бы первую минуту кадры подбирал вручную
ты… профи монтаж»; прожектор).

Вход — videos/NN/edit.json: {"frames": {"<номер фразы с картинкой>": {"shots": [план, ...]}}}. План:
  "at"    слово, с которого план начинается: "слово" (первое вхождение в клипе), ["слово", k] (k-е вхождение) или
          секунды от начала клипа; первый план клипа — с 0;
  "win"   [cx, cy, w] — центр и ширина окна 16:9 в пикселях рисунка (того файла, что идёт в сборку);
  "to"    [cx, cy, w] — куда окно приходит к концу плана (проводка, наезд, отъезд); нет — медленный наезд 4 %;
  "punch" удар: 0,25 с влёт из прошлого окна в это (SNAP), потом стоит; "shake" — тряска на ударе (px экрана);
  "spot"  [x, y, r] — прожектор: всё дальше r от точки темнеет до 25 %, проявляется за 0,25 с (как в рилсах);
  "whip"  "left" | "right" — хлёсткая склейка: смаз уходящего и входящего плана по направлению;
  "parallax" true | {"dx", "dz"} — объём по карте глубины (depth_parallax.py): редкий эффект, только где за котом
          чистая бумага или стол (владелец 02.11: «на очень малом количестве кадров, где реально подходит»);
  "why"   зачем этот план — обязательно (монтаж со смыслом, а не ради склейки).
Кадр с edit.json монтирует оркестратор целиком: автоматическая раскладка планов для него не используется, а надписи
(главная мысль, акцент) раскладываются заново в окне того плана, где их пишут."""
import json
import os
import re

import numpy as np

import camera

PUNCH_SNAP = 0.25
SPOT_IN = 0.25
SPOT_DARK = 0.25
WHIP_SEC = 0.12
PUSH = 0.04


def load(video_dir):
    path = os.path.join(video_dir, "edit.json")
    if not os.path.exists(path):
        return {}
    return {int(k) - 1: v for k, v in json.load(open(path, encoding="utf-8")).get("frames", {}).items()}


def _stem(w):
    return re.sub(r"[^а-яёa-z0-9]", "", w.lower())


def word_time(at, words):
    """Время начала плана в клипе. Слово ищется по началу (без знаков и регистра); k-е вхождение — ["слово", k]."""
    if isinstance(at, (int, float)):
        return float(at)
    stem, k = (at, 1) if isinstance(at, str) else (at[0], int(at[1]))
    hits = [w["start"] for w in words if _stem(w["word"]) == _stem(stem)] or \
        [w["start"] for w in words if _stem(w["word"]).startswith(_stem(stem))]   # точное слово важнее начала
    if len(hits) < k:
        raise ValueError(f"слова «{stem}» (вхождение {k}) нет в клипе")
    return hits[k - 1]


def _win(fr, c):
    ox, oy = fr["off"]
    return camera.window(c[0] + ox, c[1] + oy, c[2], fr["SW"], fr["SH"])


def _parallax(p):
    """"parallax": true | {"dx": px, "dz": доля} — объём по карте глубины на этом плане (редкий эффект, 02.11)."""
    if not p:
        return None
    import depth_parallax as dp
    return dict(dx=dp.DX, dz=dp.DZ) if p is True else dict(dx=float(p.get("dx", dp.DX)), dz=float(p.get("dz", dp.DZ)))


def segments(fr, shots, words, D):
    """Ручные планы -> сегменты камеры (kind="manual") в координатах холста."""
    if not shots:
        return []
    for s in shots:
        if not s.get("why"):
            raise ValueError(f"план {s.get('at')}: нет why — зачем он")
    ts = [0.0] + [word_time(s["at"], words) for s in shots[1:]]
    if any(b <= a for a, b in zip(ts, ts[1:])) or ts[-1] >= D:
        raise ValueError(f"планы не по порядку или за концом клипа: {[round(t, 2) for t in ts]} при длине {D:.2f}")
    ox, oy = fr["off"]
    segs, prev = [], None
    for i, (s, t0) in enumerate(zip(shots, ts)):
        t1 = ts[i + 1] if i + 1 < len(ts) else D
        win = _win(fr, s["win"])
        if s.get("to"):
            win_to = _win(fr, s["to"])
        else:
            cx, cy = camera.center(win)
            win_to = camera.window(cx, cy, (win[2] - win[0])/(1 + PUSH), fr["SW"], fr["SH"])
        sp = s.get("spot")
        seg = dict(t0=t0, t1=t1, kind="manual", win=win, win_to=win_to, why=s["why"],
                   punch_from=prev if s.get("punch") and prev is not None else None,
                   shake=float(s.get("shake", 0)), whip=s.get("whip"),
                   spot=(sp[0] + ox, sp[1] + oy, sp[2]) if sp else None,
                   parallax=_parallax(s.get("parallax")))
        segs.append(seg)
        prev = win_to
    for a, b in zip(segs, segs[1:]):          # хлёст смазывает и уходящий план
        if b.get("whip"):
            a["whip_out"] = b["whip"]
    return segs


def window_at(s, t):
    u = (t - s["t0"])/max(1e-6, s["t1"] - s["t0"])
    if s.get("punch_from") is not None and t - s["t0"] < PUNCH_SNAP:
        return camera.lerp(s["punch_from"], s["win"], camera.ease_out((t - s["t0"])/PUNCH_SNAP))
    return camera.lerp(s["win"], s["win_to"], camera.through(u))


def shake_px(s, t):
    """Сдвиг экрана на ударе: затухающая тряска 0,35 с."""
    a = s.get("shake") or 0.0
    u = t - s["t0"] - (PUNCH_SNAP if s.get("punch_from") is not None else 0.0)
    if a <= 0 or not 0 <= u < 0.35:
        return 0.0, 0.0
    k = a*(1 - u/0.35)
    return k*np.sin(2*np.pi*13*u), k*0.6*np.cos(2*np.pi*11*u)


def spot(f, s, t, win, W, H):
    """Прожектор (как в рилсах): всё дальше r от главного темнеет до 25 %."""
    if not s.get("spot"):
        return f
    u = camera.ease_out(min(1.0, (t - s["t0"])/SPOT_IN))
    x, y, r = s["spot"]
    k = W/(win[2] - win[0])
    sx, sy, rr = (x - win[0])*k, (y - win[1])*k, r*k
    Y, X = np.ogrid[:H, :W]
    d = np.sqrt((X - sx)**2 + (Y - sy)**2)
    m = np.clip((d - rr)/(rr*1.2), 0, 1).astype(np.float32)[..., None]*SPOT_DARK*u
    return f*(1 - m)


def whip(f, s, t):
    """Хлёст: горизонтальный смаз в начале входящего и в конце уходящего плана."""
    import cv2
    amt = 0.0
    if s.get("whip") and t - s["t0"] < WHIP_SEC:
        amt = 1 - (t - s["t0"])/WHIP_SEC
    elif s.get("whip_out") and s["t1"] - t < WHIP_SEC*0.7:
        amt = 1 - (s["t1"] - t)/(WHIP_SEC*0.7)
    if amt <= 0.02:
        return f
    n = max(3, int(90*amt)) | 1
    kern = np.zeros((1, n), np.float32)
    kern[0, :] = 1.0/n
    return cv2.filter2D(np.ascontiguousarray(f, np.float32), -1, kern, borderType=cv2.BORDER_REFLECT)


def active(segs, t):
    return next((s for s in segs if s["t0"] <= t < s["t1"]), segs[-1])


def relayout_text(fr, p, frame_clip):
    """Мысль и акцент — заново в окне того плана, где их пишут (автораскладка считала их в своих окнах)."""
    for kind, layout in (("key", frame_clip.key_layout), ("accent", frame_clip.accent_layout)):
        item, t = p.get(kind), p.get(f"{kind}_time")
        if not item or t is None:
            continue
        s = active(p["segments"], t)
        win = window_at(s, t)
        res = layout(fr, item["text"], win)
        if res is None:
            p[f"{kind}_time"] = None
            p.setdefault("notes", []).append(f"{kind} «{item['text']}» не пишется: в ручном плане нет места")
            continue
        _, center, size = res
        item.update(win=win, center=center, size=size)
        box = frame_clip.letters_box_world(res[0], win)
        if box is not None:                       # дописанное: дальше в кадре целиком или нет вовсе
            keep_text(p["segments"], t, box, fr["SW"], fr["SH"])
    return p


TEXT_EDGE = 0.02          # как shots.TEXT_EDGE_OVERLAP: больше этой доли надписи на краю кадра — обрывок


def _fits(win, box):
    return camera.inside(box, win) or camera.overlap_share(win, box) <= TEXT_EDGE


def fit_text(win, box, SW, SH):
    """Окно, в котором надпись box целиком или её нет вовсе (L03, 04.11: крупный ручной план резал рукописную мысль
    до «тс», «только д…»). Сначала сдвиг, чтобы надпись вошла целиком; не входит — окно шире (до 1,6×);
    иначе сдвиг, чтобы надпись ушла из кадра."""
    if _fits(win, box):
        return win
    w, h = win[2] - win[0], win[3] - win[1]
    bw, bh = box[2] - box[0], box[3] - box[1]
    cx, cy = camera.center(win)
    for k in (1.0, 1.15, 1.3, 1.45, 1.6):
        ww, hh = w*k, h*k
        if bw <= ww*0.96 and bh <= hh*0.96:
            nx = min(max(cx, box[2] - ww/2 + ww*0.02), box[0] + ww/2 - ww*0.02)
            ny = min(max(cy, box[3] - hh/2 + hh*0.02), box[1] + hh/2 - hh*0.02)
            cand = camera.window(nx, ny, ww, SW, SH)
            if camera.inside(box, cand):
                return cand
    best = None                               # надпись не входит: сдвинуть окно, чтобы её не было вовсе
    for dx, dy in ((box[2] - win[0] + 2, 0), (box[0] - win[2] - 2, 0), (0, box[3] - win[1] + 2), (0, box[1] - win[3] - 2)):
        cand = camera.window(cx + dx, cy + dy, w, SW, SH)
        if _fits(cand, box) and (best is None or abs(dx) + abs(dy) < best[0]):
            best = (abs(dx) + abs(dy), cand)
    return best[1] if best else win


def show_text(win, box, SW, SH):
    """Окно, в котором надпись box целиком: сдвиг, потом шире — вплоть до всего холста. Для времени, пока надпись
    пишется и читается (подпись рукой, L03 04.11: «скука» и «игровой автомат» уходили из кадра следующим крупным
    планом через полсекунды после того, как дописаны)."""
    if camera.inside(box, win):
        return win
    w = win[2] - win[0]
    cx, cy = camera.center(win)
    k = 1.0
    while True:
        ww = min(SW, w*k)
        hh = ww*SH/SW
        nx = min(max(cx, box[2] - ww/2 + ww*0.02), box[0] + ww/2 - ww*0.02)
        ny = min(max(cy, box[3] - hh/2 + hh*0.02), box[1] + hh/2 - hh*0.02)
        cand = camera.window(nx, ny, ww, SW, SH)
        if camera.inside(box, cand) or ww >= SW:
            return cand
        k *= 1.12


def hold_text(segs, t0, t1, box, SW, SH):
    """Планы, идущие в [t0, t1), показывают надпись box целиком (и начало, и конец проводки)."""
    for s in segs:
        if s["t1"] <= t0 or s["t0"] >= t1:
            continue
        s["win"] = show_text(s["win"], box, SW, SH)
        s["win_to"] = show_text(s["win_to"], box, SW, SH)
    return segs


def keep_text(segs, t, box, SW, SH):
    """Все планы после момента письма t: надпись целиком или вне кадра (и в начале, и в конце проводки)."""
    prev_to = None
    for s in segs:
        if s["t1"] <= t:
            prev_to = s["win_to"]
            continue
        if s["t0"] > t or not camera.inside(box, s["win"]):
            s["win"] = fit_text(s["win"], box, SW, SH)
        s["win_to"] = fit_text(s["win_to"], box, SW, SH)
        if s.get("punch_from") is not None and prev_to is not None:
            s["punch_from"] = prev_to
        prev_to = s["win_to"]
    return segs
