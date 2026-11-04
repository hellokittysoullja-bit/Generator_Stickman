#!/usr/bin/env python3
"""Звуки длинного ролика на событиях — те же звуки владельца и те же уровни, что в рилсах (27.10, L01: «хук у длинного
видео — буквально как хук у шортса»).

Вход — videos/NN/sfx.json: [{"name": звук из assets/sfx/reels/library.json, "phrase": номер фразы (с 1),
"word": начало слова в этой фразе | "at": секунды от начала фразы, "align": "peak" (по умолчанию: пик звука на
моменте) | "end" (пик на начале фразы — riser к склейке), "role": whoosh | impact | meme | ui, "gain_db": 0,
"why": зачем звук здесь}]. Без why звук не ставится: звук озвучивает событие, а не украшает склейку.

Громкость — как в рилсах (reel.ROLE_DB): пик звука = p95 пиков голоса + роль + gain_db; проверка «громче голоса»
и «не слышно» — те же пороги. Выход — дорожка wav длиной ролика; сводит её assemble_frames до loudnorm."""
import json
import os
import re

import numpy as np

import reel


def _stem(w):
    return re.sub(r"[^а-яёa-z0-9]", "", w.lower())


def resolve(events, starts, word_times):
    """Время момента каждого события (абсолютное, с). Не нашлось слово — ошибка, а не догадка."""
    out, errs = [], []
    for e in events:
        if not e.get("why"):
            errs.append(f"«{e.get('name')}»: нет why — зачем звук здесь")
            continue
        if e.get("name") not in reel.SFX:
            errs.append(f"«{e.get('name')}»: такого звука нет в библиотеке владельца")
            continue
        i = int(e["phrase"]) - 1
        if i >= len(starts):
            errs.append(f"«{e['name']}»: фразы {e['phrase']} нет")
            continue
        if "word" in e and not word_times:
            continue                                  # немое превью без alignment: звук на слове негде поставить
        if "word" not in e:                           # «секунды от начала фразы» — промах, как только сдвинется
            errs.append(f"«{e['name']}» во фразе {e['phrase']}: звук без слова — на слово (word) или, если он на "
                        f"склейку, в план монтажа edit.json (\"sound\"): тогда он встанет ровно на склейку")
            continue
        import long_edit                              # то же слово и то же вхождение, что у склейки монтажа
        ws = word_times[i] if i < len(word_times) else []
        try:
            t = long_edit.word_time(e["word"], ws) + e.get("offset", 0.0)
        except ValueError:
            errs.append(f"«{e['name']}»: слова «{e['word']}» нет во фразе {e['phrase']}")
            continue
        out.append(dict(e, t=max(0.0, t)))
    return out, errs


def track(events, total, voice_wav):
    """Стерео-дорожка звуков (float32, reel.SR) и замер уровней."""
    import subprocess
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", voice_wav, "-ac", "1", "-ar", str(reel.SR), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    vp = reel.voice_p95(np.abs(np.frombuffer(p.stdout, np.float32)))
    n = int((total + 0.5) * reel.SR)
    st = np.zeros((n, 2), np.float32)
    levels, errs = [], []
    for e in events:
        name = e["name"]
        lvl, peak = reel.SFX[name][2], reel.SFX[name][1]
        tgt = reel.ROLE_DB[e.get("role", "whoosh")] + e.get("gain_db", 0.0)
        x = reel.sfx(name) * (10 ** ((vp + tgt - lvl) / 20))
        t0 = e["t"] - peak if e.get("align", "peak") in ("peak", "end") else e["t"]
        i = int(t0 * reel.SR)
        if i < 0:
            x, i = x[-i:], 0
        m = min(len(x), n - i)
        if m > 0:
            st[i:i + m] += x[:m]
        own = float(20 * np.log10(max(float(np.abs(x).max()), 1e-9))) - vp
        if own > reel.SFX_LOUDER_MAX:
            errs.append(f"«{name}» на {e['t']:.2f} с громче голоса: {own:+.1f} дБ")
        elif own < reel.SFX_INAUDIBLE:
            errs.append(f"«{name}» на {e['t']:.2f} с не слышно: {own:+.1f} дБ")
        levels.append(dict(name=name, t=round(e["t"], 3), vs_voice_db=round(own, 1), why=e["why"],
                           **({"cut": True} if e.get("cut") else {})))
    return st, dict(voice_p95=round(vp, 1), sounds=levels, errors=errs)


SNAP_SEC = 0.06    # звук на слове ближе этого к склейке встаёт ровно на кадр склейки: глаз и ухо видят одно событие


def snap(events, cuts):
    """Звук на слове ближе SNAP_SEC к склейке — ровно на кадр склейки (на месте, events меняются)."""
    import bisect
    cuts = sorted(cuts)
    for e in events:
        k = bisect.bisect_left(cuts, e["t"])
        near = min((cuts[j] for j in (k - 1, k) if 0 <= j < len(cuts)), key=lambda c: abs(c - e["t"]), default=None)
        if near is not None and abs(near - e["t"]) <= SNAP_SEC:
            e["t"] = near
    return events


def build(video_dir, starts, word_times, total, voice_wav, out_wav, cut_sounds=(), cuts=()):
    """Дорожка звуков ролика в out_wav или None (нет ни sfx.json, ни звуков склеек). cut_sounds — звуки планов
    монтажа (edit.json "sound") на настоящем времени склейки, как в рилсах (reel.sound_plan): пик звука ровно на
    склейке. Ошибки — исключение: ролик с неслышным или оглушающим звуком не собирается."""
    path = os.path.join(video_dir, "sfx.json")
    if not os.path.exists(path) and not cut_sounds:
        return None
    raw = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
    events, errs = resolve(raw, starts, word_times)
    snap(events, cuts)
    for c in cut_sounds:
        if c["name"] not in reel.SFX:
            errs.append(f"«{c['name']}» на склейке {c['t']:.2f} с: такого звука нет в библиотеке владельца")
            continue
        events.append(dict(c, cut=True))
    events.sort(key=lambda e: e["t"])
    st, rep = track(events, total, voice_wav)
    errs += rep["errors"]
    with open(os.path.join(video_dir, "media_plan", "sfx_report.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(rep, errors=errs), fh, ensure_ascii=False, indent=1)
    if errs:
        raise SystemExit("Звуки ролика: " + "; ".join(errs))
    import wave
    pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(reel.SR)
        w.writeframes(pcm.tobytes())
    return rep
