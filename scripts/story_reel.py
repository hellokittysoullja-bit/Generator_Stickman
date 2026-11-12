#!/usr/bin/env python3
"""Сборщик рилса-истории (формат «нарисовано кодом», владелец 12.11): клипы планов → один ролик с хлёстами на
выбранных склейках, субтитрами на тёмной плашке (как у первого образца владельца: тёмная плашка, белые слова,
сказанное слово цветом), звуками из библиотеки владельца и голосом.

    python scripts/story_reel.py videos/23_vybor/story [--preview]

Вход: <dir>/shots.json (планы t0/t1, у плана может быть "whip": true — въезд хлёстом), <dir>/clips/<id>.mp4 (по
контракту: кадр k = время ролика max(0, t0 − pad) + k/fps), <dir>/voice/voice.wav и words.json, <dir>/sound.json
({"sfx": [{"name", "t" | "word": индекс, "why"}], "keys": [индексы ключевых слов]}). Выход: <dir>/reel.mp4.
"""
import argparse
import json
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import reel  # noqa: E402  (группы субтитров, библиотека звуков, роли громкости)

W, H = 1080, 1920
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
CAP_SIZE, CAP_Y = 66, 1430           # центр плашки: выше зоны интерфейса (низ 1560), ниже главного в кадре
PLATE = (34, 31, 44)                 # тёмная плашка (образец владельца: тёмно-фиолетовая)
SAID, KEY, WHITE = (255, 214, 92), (186, 166, 255), (255, 255, 255)   # сказанное — жёлтым, ключевое — лавандовым
WHIP_FRAMES = 3                      # по 3 кадра с каждой стороны склейки
SR = reel.SR


class Clip:
    def __init__(self, path, start, fps):
        self.start, self.fps = start, fps
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           capture_output=True, check=True)
        self.frames = np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W, 3)

    def at(self, t):
        k = int(round((t - self.start) * self.fps))
        return self.frames[min(max(k, 0), len(self.frames) - 1)]


def hblur(img, px):
    px = int(abs(px))
    if px < 2:
        return img
    k = np.zeros((1, px), np.float32); k[0, :] = 1.0 / px
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_REFLECT)


def shift(img, dx):
    M = np.float32([[1, 0, dx], [0, 1, 0]])
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)


def whip(out_f, in_f, d):
    """d — номер кадра от склейки (−3…−1 уходящий, 0…2 входящий): уходящий уносится влево со смазом, входящий
    влетает справа и тормозит."""
    if d < 0:
        u = (WHIP_FRAMES + d + 1) / WHIP_FRAMES            # 1/3, 2/3, 1
        return hblur(shift(out_f, -W * 0.35 * u * u), 160 * u)
    u = 1 - d / WHIP_FRAMES                                 # 1, 2/3, 1/3
    return hblur(shift(in_f, W * 0.35 * u * u), 160 * u)


_F = {}
def font(size):
    if size not in _F:
        _F[size] = ImageFont.truetype(FONT, size)
    return _F[size]


def caption(img, words, idx, t, keys):
    """Плашка с группой слов: сказанное — цветом, ключевое после того, как сказано, — лавандовым."""
    f = font(CAP_SIZE)
    toks = [reel.cap_text(words[i]["word"]) for i in idx]
    sp = f.getlength(" ")
    ws = [f.getlength(x) for x in toks]
    tw = sum(ws) + sp * (len(toks) - 1)
    padx, pady = 34, 20
    bw, bh = int(tw + 2 * padx), int(CAP_SIZE * 1.18 + 2 * pady)
    layer = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((20, 20, 20 + bw, 20 + bh), radius=16, fill=PLATE + (236,))
    x = 20 + padx
    for i, tok, w in zip(idx, toks, ws):
        said = words[i]["start"] <= t
        col = (KEY if i in keys else SAID) if said else WHITE
        d.text((x, 20 + pady - CAP_SIZE * 0.06), tok, font=f, fill=col)
        x += w + sp
    layer = layer.rotate(-1.6, resample=Image.BICUBIC, expand=True)
    base = Image.fromarray(img)
    pos = (W // 2 - layer.width // 2, CAP_Y - layer.height // 2)
    base.paste(layer, pos, layer)
    return np.asarray(base)


def sound_track(spec_dir, words, total):
    snd = json.load(open(os.path.join(spec_dir, "sound.json"), encoding="utf8"))
    voice = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(spec_dir, "voice", "voice.wav"), "-ac", "2",
                            "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    v = np.frombuffer(voice, np.float32).reshape(-1, 2)
    n = int(total * SR)
    track = np.zeros((n, 2), np.float32)
    track[:min(n, len(v))] += v[:n]
    vp = float(np.percentile(np.abs(v[np.abs(v).max(1) > 0.02]), 95)) if len(v) else 0.3
    for e in snd["sfx"]:
        name = e["name"]
        t = e["t"] if "t" in e else words[e["word"]]["start"] + e.get("offset", 0.0)
        role = reel.SFX_LIB[name].get("role", "whoosh")
        x = reel.sfx(name)
        target = vp * 10 ** ((reel.ROLE_DB.get(role, -12.0) + e.get("gain_db", 0.0)) / 20)
        x = x * (target / max(1e-6, float(np.abs(x).max())))
        s = int((t - reel.SFX[name][1]) * SR)            # пик звука — на момент события
        a, b = max(0, s), min(n, s + len(x))
        if b > a:
            track[a:b] += x[a - s:b - s]
    peak = float(np.abs(track).max())
    if peak > 0.95:
        track *= 0.95 / peak
    return track


def build(d, preview=False):
    spec = json.load(open(os.path.join(d, "shots.json"), encoding="utf8"))
    words = json.load(open(os.path.join(d, "voice", "words.json"), encoding="utf8"))
    snd = json.load(open(os.path.join(d, "sound.json"), encoding="utf8"))
    keys = set(snd.get("keys", []))
    fps = spec["fps"]; pad = spec["pad"]; total = spec["end"]
    shots = spec["shots"]
    clips = {s["id"]: Clip(os.path.join(d, "clips", s["id"] + ".mp4"), max(0.0, s["t0"] - pad), fps) for s in shots}
    caps = reel.chunks([w["word"] for w in words], words)
    nfr = int(round(total * fps))
    out = os.path.join(d, "reel.mp4")
    tmpv = os.path.join(d, ".video.mp4")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium" if not preview else "veryfast",
                            "-crf", "17", "-pix_fmt", "yuv420p", tmpv], stdin=subprocess.PIPE)
    cut_f = [int(round(s["t0"] * fps)) for s in shots]
    for f in range(nfr):
        t = f / fps
        i = max(k for k in range(len(shots)) if cut_f[k] <= f)
        frame = clips[shots[i]["id"]].at(t)
        for k in range(1, len(shots)):                       # хлёст: 3 кадра до и 3 после склейки k
            if shots[k].get("whip") and -WHIP_FRAMES <= f - cut_f[k] < WHIP_FRAMES:
                dd = f - cut_f[k]
                frame = whip(clips[shots[k - 1]["id"]].at(t), clips[shots[k]["id"]].at(t), dd)
        c = next((c for c in caps if c["t0"] <= t < c["t1"]), None)
        if c:
            frame = caption(np.ascontiguousarray(frame).copy(), words, c["idx"], t, keys)
        enc.stdin.write(np.ascontiguousarray(frame, np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
    track = sound_track(d, words, total)
    wav = os.path.join(d, ".mix.f32")
    track.astype(np.float32).tofile(wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", out], check=True)
    os.remove(tmpv); os.remove(wav)
    print("Готово:", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dir"); ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    build(a.dir, a.preview)
