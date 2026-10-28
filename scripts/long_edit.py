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
                   spot=(sp[0] + ox, sp[1] + oy, sp[2]) if sp else None)
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
    return p
