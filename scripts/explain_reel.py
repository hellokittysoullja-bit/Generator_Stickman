#!/usr/bin/env python3
"""Рилс формата «тема, объясняет котик» (владелец 07.11, разбор — docs/reels_knowledge/format_explained_by_animal.md).

Не reel.py и не его правила: белый фон, наш кот-вырезка по центру всё время слегка качается, подпись одной строкой
сверху меняется кусками по 2–3 слова в такт голосу (курсив — *слово*), предметы-эмодзи (Noto, Apache 2.0) появляются
на своём слове и живут циклом, склейки жёсткие, «тёмный» момент — уход фона в серо-синий за 0,5 с, финал — кот
кувыркается и встаёт. Голос без пауз (Lumean, шаблон рилсов), под ним тихая музыка.

    python scripts/explain_reel.py videos/19_prokrastinatsiya_koty/reel [--preview] [--voice-only]
Вход — <dir>/explain.json, вырезки <dir>/cut/<имя>.png, эмодзи <dir>/emoji/<код>.png. Выход — <dir>/explain.mp4.
"""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

W, H, FPS = 1080, 1920, 30
FONT = os.path.join(ROOT, "assets", "fonts", "ShantellSans-ExtraBold.ttf")
CAP_Y, CAP_SIZE, TITLE_SIZE, SUB_SIZE = 185, 78, 112, 56
CAT_BOTTOM = 1500                      # низ кота: нижние ~20 % экрана — под интерфейс, как у образца пусто
DIM = (104, 110, 128)                  # «тёмный» фон: у образца чёрный, но наш кот чёрный — серо-синий
WOBBLE_DEG, WOBBLE_HZ = 2.2, 0.9       # кот покачивается всё время, как герой образца
POP_SEC = 0.15
MUSIC_LUFS = -31.0                     # голос −16 LUFS, подложка на ~15 дБ тише (образец: ~12 дБ)
WORD_RE = re.compile(r"[\wёЁ]+(?:-[\wёЁ]+)?")


def clean(t):
    return t.replace("*", "")


def words_of(text):
    """Слова фразы и множество курсивных (внутри *…*)."""
    out, emph, on = [], set(), False
    for part in re.split(r"(\*)", text):
        if part == "*":
            on = not on; continue
        for w in WORD_RE.findall(part):
            if on:
                emph.add(len(out))
            out.append(w)
    return out, emph


# ---------- голос ----------
def voice(d, spec, force=False):
    import lumean_tts as L
    import reel_voice as RV
    RV.load_env()
    key, tpl = os.environ.get("LUMEAN_API_KEY"), RV.voice_template()
    if not key or not tpl:
        raise SystemExit("нужны LUMEAN_API_KEY в .env и voice_template в docs/reels_brand.json")
    text = "\n".join(clean(b["text"]) for b in spec["beats"])
    sig = hashlib.sha1(f"{tpl}\n{text}".encode()).hexdigest()[:16]
    out = os.path.join(d, "voice"); os.makedirs(out, exist_ok=True)
    meta = os.path.join(out, "meta.json")
    if not force and os.path.exists(meta) and json.load(open(meta, encoding="utf8")).get("sig") == sig:
        return out
    words = [w for b in spec["beats"] for w in words_of(b["text"])[0]]
    with tempfile.TemporaryDirectory() as tmp:
        res = L.process_section(key, tpl, tmp, 0, "explain", text, os.path.basename(os.path.dirname(os.path.abspath(d))))
        if not res.get("audio_path") or not res.get("alignment"):
            raise SystemExit(f"озвучка не получена: {res.get('reason')}")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", res["audio_path"], "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", os.path.join(out, "voice.wav")],
                       check=True)
        times = RV.word_times(text, words, res["alignment"])
    json.dump(times, open(os.path.join(out, "words.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    json.dump(dict(sig=sig, template=tpl, order=res.get("order_id"), text=text), open(meta, "w", encoding="utf8"),
              ensure_ascii=False, indent=1)
    return out


# ---------- раскладка по времени ----------
def timeline(spec, times):
    """Начало и конец каждой фразы, слова с временем, куски подписи."""
    beats, k = [], 0
    for b in spec["beats"]:
        ws, emph = words_of(b["text"])
        tw = times[k:k + len(ws)]; k += len(ws)
        beats.append(dict(spec=b, words=[(w, t["start"], t["end"], i in emph) for i, (w, t) in enumerate(zip(ws, tw))]))
    for i, b in enumerate(beats):
        b["t0"] = 0.0 if i == 0 else beats[i]["words"][0][1] - 0.04
    for i, b in enumerate(beats):
        b["t1"] = beats[i + 1]["t0"] if i + 1 < len(beats) else b["words"][-1][2] + 0.9
    for b in beats:
        b["chunks"] = chunks(b)
    return beats


def chunks(b):
    """Подпись кусками по 2–3 слова; граница — после знака препинания. Кусок висит до начала следующего."""
    raw = clean(b["spec"]["text"])
    toks = WORD_RE.findall(raw)
    # где после слова стоит знак — граница куска
    stops, pos = set(), 0
    for i, tkn in enumerate(toks):
        j = raw.find(tkn, pos); pos = j + len(tkn)
        nxt = raw[pos:pos + 2]
        if re.match(r"\s*[.,:;!?—»…]", nxt):
            stops.add(i)
    out, cur = [], []
    for i, _w in enumerate(b["words"]):
        cur.append(i)
        if i in stops or len(cur) >= 3:
            out.append(cur); cur = []
    if cur:
        if out and len(cur) == 1 and len(out[-1]) < 3:
            out[-1] += cur
        else:
            out.append(cur)
    res = []
    for n, idx in enumerate(out):
        t0 = b["t0"] if n == 0 else b["words"][idx[0]][1] - 0.03
        res.append(dict(t0=t0, words=[(b["words"][i][0], b["words"][i][3]) for i in idx], text_raw=raw))
    for n in range(len(res)):
        res[n]["t1"] = res[n + 1]["t0"] if n + 1 < len(res) else b["t1"]
    return res


def word_time(b, word, default=None):
    for w, s, _e, _ in b["words"]:
        if w.lower().startswith(word.lower()[:max(3, len(word) - 2)]):
            return s
    return b["t0"] if default is None else default


# ---------- графика ----------
_font_cache = {}


def font(sz):
    if sz not in _font_cache:
        _font_cache[sz] = ImageFont.truetype(FONT, sz)
    return _font_cache[sz]


def text_img(parts, size, fill, stroke=0, stroke_fill=None, maxw=960):
    """parts — [(слово, курсив)]; курсив — наклон слова. Перенос на вторую строку, если не влезает."""
    f = font(size)
    sp = f.getlength(" ")
    lines, cur, curw = [], [], 0
    for w, it in parts:
        ww = f.getlength(w) + (size*0.18 if it else 0)
        if cur and curw + sp + ww > maxw:
            lines.append(cur); cur, curw = [], 0
        cur.append((w, it, ww)); curw += (sp if len(cur) > 1 else 0) + ww
    lines.append(cur)
    lh = int(size*1.22)
    img = Image.new("RGBA", (W, lh*len(lines) + 2*stroke + 10), (0, 0, 0, 0))
    for li, line in enumerate(lines):
        tw = sum(x[2] for x in line) + sp*(len(line) - 1)
        x = (W - tw)/2; y = li*lh + stroke
        for w, it, ww in line:
            wi = Image.new("RGBA", (int(ww + size*0.6 + 2*stroke), lh + 2*stroke), (0, 0, 0, 0))
            ImageDraw.Draw(wi).text((stroke + size*0.1, stroke), w, font=f, fill=fill, stroke_width=stroke,
                                    stroke_fill=stroke_fill)
            if it:
                wi = wi.transform(wi.size, Image.AFFINE, (1, 0.22, -0.22*wi.size[1]*0.5, 0, 1, 0), Image.BICUBIC)
            img.alpha_composite(wi, (int(x - stroke - size*0.1), int(y - stroke)))
            x += ww + sp
    return img


_img_cache = {}


def load(path, h=None, maxw=1000):
    key = (path, h, maxw)
    if key not in _img_cache:
        im = Image.open(path).convert("RGBA")
        if h:
            s = h/im.height
            if im.width*s > maxw:
                s = maxw/im.width
            im = im.resize((max(1, int(im.width*s)), max(1, int(im.height*s))), Image.LANCZOS)
        _img_cache[key] = im
    return _img_cache[key]


def grey(im):
    a = np.asarray(im).astype(np.float32)
    lum = (a[..., :3] @ [0.299, 0.587, 0.114])[..., None]
    a[..., :3] = lum*0.65 + 255*0.35*0.6 + a[..., :3]*0.0
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def ease_out(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u)**3


def scribble(size, t, seed=3):
    """Каракуля-клубок над головой (тревога): петли тушью, медленно крутится."""
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (size*2, size*2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = size
    pts = []
    for k in range(260):
        a = k*0.37 + t*2.0
        r = size*0.55*(0.6 + 0.4*math.sin(k*0.11 + rng.random()*0.2))
        pts.append((c + r*math.cos(a), c + 0.8*r*math.sin(a*1.3)))
    d.line(pts, fill=(30, 30, 34, 255), width=6, joint="curve")
    return im


def prop_frame(p, d, t, appear, b):
    """Эмодзи-реквизит в момент t (с момента появления — u)."""
    u = t - appear
    if u < 0:
        return None
    size = p.get("size", 200)
    x, y, rot, sc, alpha = p["x"], p["y"], 0.0, 1.0, 1.0
    m = p.get("motion", "pop")
    if u < POP_SEC and m not in ("walk_in", "grow"):
        sc, alpha = 0.6 + 0.4*ease_out(u/POP_SEC), min(1, u/POP_SEC)
    if m == "bob":
        y += 10*math.sin(2*math.pi*1.1*u)
    elif m == "shake":
        rot = 9*math.sin(2*math.pi*5*u)
    elif m == "pulse":
        sc *= 1 + 0.08*math.sin(2*math.pi*2*u)
    elif m == "flip":
        sc *= 1.0
        sx = abs(math.cos(min(1, u/0.25)*math.pi/2 - math.pi/2)) if u < 0.25 else 1.0
        p = dict(p, _sx=max(0.05, sx))
    elif m == "grow":
        sc, alpha = 0.5 + 0.7*ease_out(u/1.2), min(1, u/POP_SEC)
    elif m == "walk_in":
        x = W + size - (W + size - p["x"])*ease_out(u/0.6)
        y += 8*abs(math.sin(2*math.pi*2.2*u)) * (1 if u < 0.6 else 0.3)
        rot = 5*math.sin(2*math.pi*2.2*u) if u < 0.6 else 2*math.sin(2*math.pi*0.9*u)
    else:
        y += 4*math.sin(2*math.pi*0.8*u)
    if p.get("scribble"):
        im = scribble(int(size/2), u)
    else:
        im = load(os.path.join(d, "emoji", p["emoji"] + ".png"), h=size, maxw=size)
    s = max(1, int(im.width*sc*p.get("_sx", 1))), max(1, int(im.height*sc))
    im = im.resize(s, Image.BICUBIC)
    if rot:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 1:
        a = np.asarray(im).copy(); a[..., 3] = (a[..., 3]*alpha).astype(np.uint8); im = Image.fromarray(a)
    return im, (int(x - im.width/2), int(y - im.height/2))


def render_frame(d, beats, t, title_img, sub_img, cap_cache):
    b = next(x for x in beats if x["t0"] <= t < x["t1"]) if t < beats[-1]["t1"] else beats[-1]
    s = b["spec"]; lt = t - b["t0"]
    bg = (255, 255, 255)
    dark = s.get("bg") == "dark"
    if dark:
        k = ease_out(lt/0.5)
        bg = tuple(int(255 + (c - 255)*k) for c in DIM)
    fr = Image.new("RGBA", (W, H), bg + (255,))
    if s.get("scene"):                              # сцена на весь экран (у образца — кафе, пруд), наш рисунок
        fr.alpha_composite(scene_img(os.path.join(ROOT, s["scene"]), s.get("scene_cx", 0.5), lt), (0, 0))
    for o in s.get("others", []):                   # другие коты — копии героя с аксессуаром, как у образца
        if t >= word_time(b, o.get("at", "")) if o.get("at") else True:
            draw_cat(fr, d, o["cat"], o.get("h", 520), o["x"], t + o.get("phase", 1.3), acc=o.get("acc"),
                     acc_dx=o.get("acc_dx", 0.0), acc_dy=o.get("acc_dy", -0.45), acc_size=o.get("acc_size", 170),
                     bottom=o.get("bottom", CAT_BOTTOM))
    if s.get("cat") is None:
        cat = None
    # кот (со сменой по слову и кувырком)
    cat, ch, tumble_t = s.get("cat"), s.get("cat_h", 700), None
    for sw in s.get("swap", []):
        ts = word_time(b, sw["at"])
        if t >= ts:
            cat, ch = sw["cat"], sw.get("cat_h", ch)
            if sw.get("tumble"):
                tumble_t = t - ts
    close = None
    for cl in s.get("close", []):                   # крупный план: огромная морда въезжает снизу на своём слове
        ts = word_time(b, cl["at"])
        if t >= ts and (not cl.get("until") or t < word_time(b, cl["until"])):
            close = (cl, t - ts)
    if cat and close:
        cl, u = close
        im = load(os.path.join(d, "cut", cl.get("cat", cat) + ".png"), h=cl.get("h", 1900), maxw=2600)
        if s.get("grey"):
            im = grey(im)
        slide = (1 - ease_out(u/0.22))*500
        rot = 1.2*math.sin(2*math.pi*WOBBLE_HZ*t)
        big = im.rotate(rot, Image.BICUBIC, expand=True)
        fr.alpha_composite(big, (int(W*cl.get("x", 0.5) - big.width/2), int(H*cl.get("y", 0.62) - big.height/2 + slide)))
    elif cat:
        draw_cat(fr, d, cat, ch, s.get("cat_x", W//2), t, grey_on=s.get("grey"), zoom=s.get("zoom", 1.0),
                 tumble_t=tumble_t, shake=s.get("shake", 0.0))
    # реквизит
    for p in s.get("props", []):
        ap = word_time(b, p["at"])
        if p.get("until") and t >= word_time(b, p["until"]):
            continue
        r = prop_frame(p, d, t, ap, b)
        if r:
            fr.alpha_composite(r[0], (max(-r[0].width + 1, r[1][0]), max(-r[0].height + 1, r[1][1])))
    # подпись
    if s.get("title"):
        fr.alpha_composite(title_img, (0, 250))
        if lt >= 0.9:
            fr.alpha_composite(sub_img, (0, CAT_BOTTOM + 70))
    else:
        c = next((c for c in b["chunks"] if c["t0"] <= t < c["t1"]), b["chunks"][-1])
        key = (id(c), dark)
        if key not in cap_cache:
            cap_cache[key] = text_img(c["words"], CAP_SIZE, (255, 255, 255) if dark else (12, 12, 14),
                                      stroke=5 if dark else 0, stroke_fill=(0, 0, 0))
        fr.alpha_composite(cap_cache[key], (0, CAP_Y - CAP_SIZE//2))
    if s.get("flash") and lt < 0.25:                # белая вспышка на переходе
        a = int(255*(1 - lt/0.25))
        fr.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, a)))
    return fr.convert("RGB")


def draw_cat(fr, d, cat, ch, cx, t, grey_on=False, zoom=1.0, tumble_t=None, shake=0.0, acc=None, acc_dx=0.0,
             acc_dy=-0.45, acc_size=170, bottom=CAT_BOTTOM):
    """Кот-вырезка: всё время покачивается; кувырок; дрожь (страх); аксессуар-эмодзи на голове (другие коты)."""
    im = load(os.path.join(d, "cut", cat + ".png"), h=ch)
    if grey_on:
        im = grey(im)
    if zoom != 1.0:
        im = im.resize((int(im.width*zoom), int(im.height*zoom)), Image.BICUBIC)
    if acc:
        im = im.copy()
        e = load(os.path.join(d, "emoji", acc + ".png"), h=acc_size, maxw=acc_size)
        ax, ay = int(im.width*(0.5 + acc_dx) - e.width/2), int(im.height*(0.5 + acc_dy) - e.height/2)
        pad = Image.new("RGBA", (im.width, im.height + max(0, -ay)), (0, 0, 0, 0))
        pad.alpha_composite(im, (0, max(0, -ay))); pad.alpha_composite(e, (ax, max(0, ay)))
        im = pad
    rot = WOBBLE_DEG*math.sin(2*math.pi*WOBBLE_HZ*t)
    hop = 6*abs(math.sin(2*math.pi*WOBBLE_HZ*t))
    dx = shake*math.sin(2*math.pi*13*t)
    if tumble_t is not None and tumble_t < 0.7:
        u = tumble_t/0.7
        rot += 360*ease_out(u); hop += 160*math.sin(math.pi*u)
    big = im.rotate(rot, Image.BICUBIC, expand=True, center=(im.width/2, im.height*0.9))
    fr.alpha_composite(big, (int(cx + dx - big.width/2), int(bottom + (zoom - 1)*ch*0.25 - hop - big.height/2 - im.height*0.4)))


def scene_img(path, cx, lt):
    """Рисунок на весь экран 9:16, медленный наезд 4 % за сцену."""
    key = ("scene", path, cx)
    if key not in _img_cache:
        im = Image.open(path).convert("RGBA")
        s = H/im.height*1.06
        im = im.resize((int(im.width*s), int(im.height*s)), Image.LANCZOS)
        x0 = int(min(max(im.width*cx - W/2, 0), im.width - W))
        _img_cache[key] = im.crop((x0, int((im.height - H)/2), x0 + W, int((im.height - H)/2) + H))
    im = _img_cache[key]
    z = 1 + 0.04*min(1, lt/3)
    if z > 1.001:
        w2, h2 = int(W*z), int(H*z)
        im = im.resize((w2, h2), Image.BILINEAR).crop(((w2 - W)//2, (h2 - H)//2, (w2 - W)//2 + W, (h2 - H)//2 + H))
    return im


# ---------- звуки: свои, синтез (без чужих сэмплов) ----------
SR = 48000


def _env(n, a=0.004, r=0.08):
    t = np.arange(n)/SR
    return np.minimum(1, t/a)*np.exp(-t/r)


def sfx(kind, seed=0):
    rng = np.random.default_rng(seed)
    if kind == "pop":                               # появление предмета: короткий «поп» с падающим тоном
        n = int(0.09*SR); t = np.arange(n)/SR
        f = 900*np.exp(-t*28) + 260
        return 0.8*np.sin(2*np.pi*np.cumsum(f)/SR)*_env(n, 0.002, 0.03)
    if kind == "whoosh":                            # склейка: шум с проходом частоты
        n = int(0.32*SR); x = rng.standard_normal(n)
        k = np.linspace(0, 1, n); y = np.zeros(n); a = 0.0
        for i in range(n):
            c = 0.02 + 0.25*math.sin(math.pi*k[i]); a += c*(x[i] - a); y[i] = a
        return 0.9*y*np.sin(np.pi*k)**1.5
    if kind == "boing":                             # кувырок
        n = int(0.45*SR); t = np.arange(n)/SR
        f = 180 + 140*np.sin(2*np.pi*9*t)*np.exp(-t*5)
        return 0.6*np.sin(2*np.pi*np.cumsum(f)/SR)*_env(n, 0.005, 0.18)
    if kind == "ding":                              # финал: колокольчик
        n = int(1.2*SR); t = np.arange(n)/SR
        y = sum(a*np.sin(2*np.pi*f*t) for f, a in ((1320, 1), (2640, 0.4), (3960, 0.2)))
        return 0.35*y*_env(n, 0.003, 0.35)
    if kind == "tick":
        n = int(0.03*SR); return 0.5*rng.standard_normal(n)*_env(n, 0.001, 0.006)
    if kind == "thud":                              # тяжесть, «бум»
        n = int(0.3*SR); t = np.arange(n)/SR
        return 0.9*np.sin(2*np.pi*(70 + 60*np.exp(-t*20))*t)*_env(n, 0.003, 0.09)
    raise ValueError(kind)


def sfx_events(beats):
    """Звук на каждом событии кадра, как у образца (~5 на 10 с): поп — предмет, свист — склейка/вспышка,
    бум — тяжесть, кувырок, колокольчик в финале. Свои на фразе — поле sfx [{at, kind}]."""
    ev = []
    for i, b in enumerate(beats):
        s = b["spec"]
        if i and (s.get("cut") == "hard" or s.get("flash") or s.get("scene")):
            ev.append((b["t0"], "whoosh"))
        for p in s.get("props", []):
            ev.append((word_time(b, p["at"]), p.get("sound", "pop")))
        for cl in s.get("close", []):
            ev.append((word_time(b, cl["at"]), "whoosh"))
        for sw in s.get("swap", []):
            ev.append((word_time(b, sw["at"]), "boing" if sw.get("tumble") else "pop"))
        for o in s.get("others", []):
            if o.get("at"):
                ev.append((word_time(b, o["at"]), "pop"))
        for x in s.get("sfx", []):
            ev.append((word_time(b, x["at"]), x["kind"]))
    ev.sort()
    out, last = [], {}
    for t, k in ev:                                 # одинаковые звуки не ближе 0,12 с
        if t - last.get(k, -9) >= 0.12:
            out.append((t, k)); last[k] = t
    return out


def sfx_track(events, dur, path, gain_db=-7.0):
    y = np.zeros(int(dur*SR) + SR)
    for i, (t, k) in enumerate(events):
        s = sfx(k, seed=i); a = int(max(0, t)*SR)
        y[a:a + len(s)] += s[:len(y) - a]
    y *= 10**(gain_db/20)
    y = np.clip(y, -0.98, 0.98)
    import wave
    w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((y*32767).astype(np.int16).tobytes()); w.close()


def mix(d, voice_wav, music, dur, out_wav, sfx_wav=None):
    m = os.path.normpath(os.path.join(d, music)) if music else None
    if not m or not os.path.exists(m):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice_wav, "-t", f"{dur:.3f}", out_wav], check=True)
        return
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", m, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
    g = MUSIC_LUFS - lufs
    ins = ["-i", voice_wav, "-stream_loop", "-1", "-i", m] + (["-i", sfx_wav] if sfx_wav else [])
    fx = "[2:a]aresample=48000[fx];" if sfx_wav else ""
    n = 3 if sfx_wav else 2
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex",
                    f"[1:a]volume={g:.1f}dB,afade=t=out:st={dur - 1.2:.2f}:d=1.2[mu];{fx}"
                    f"[0:a][mu]{'[fx]' if sfx_wav else ''}amix=inputs={n}:duration=first:normalize=0,apad[a]",
                    "-map", "[a]", "-t", f"{dur:.3f}", "-ar", "48000", out_wav], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir"); ap.add_argument("--preview", action="store_true"); ap.add_argument("--voice-only", action="store_true")
    ap.add_argument("--force-voice", action="store_true")
    a = ap.parse_args()
    d = a.dir
    spec = json.load(open(os.path.join(d, "explain.json"), encoding="utf8"))
    vdir = voice(d, spec, a.force_voice)
    if a.voice_only:
        print("голос:", vdir); return
    times = json.load(open(os.path.join(vdir, "words.json"), encoding="utf8"))
    sp = float(spec.get("speed", 1.0))      # образец говорит 2,5 слова/с без пауз; наш голос медленнее — ускоряем
    vwav = os.path.join(vdir, "voice.wav")
    if sp != 1.0:
        fast = os.path.join(vdir, f"voice_x{sp:g}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vwav, "-af", f"atempo={sp}", fast], check=True)
        vwav = fast
        times = [dict(t, start=t["start"]/sp, end=t["end"]/sp) for t in times]
    beats = timeline(spec, times)
    dur = beats[-1]["t1"]
    title_img = text_img([(w, False) for w in spec["title"].split()], TITLE_SIZE, (12, 12, 14))
    sub_img = text_img([(w, False) for w in spec["subtitle"].split()], SUB_SIZE, (12, 12, 14))
    fps = 15 if a.preview else FPS
    out = os.path.join(d, "explain_preview.mp4" if a.preview else "explain.mp4")
    wav = os.path.join(d, "voice", "mix.wav")
    fxw = os.path.join(d, "voice", "sfx.wav")
    events = sfx_events(beats)
    sfx_track(events, dur, fxw)
    mix(d, vwav, spec.get("music"), dur, wav, fxw)
    print(f"звуков: {len(events)} ({len(events)/dur*10:.1f} на 10 с)")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(fps), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE)
    cap_cache = {}
    n = int(dur*fps)
    for i in range(n):
        p.stdin.write(render_frame(d, beats, i/fps, title_img, sub_img, cap_cache).tobytes())
    p.stdin.close(); p.wait()
    json.dump([dict(text=clean(b["spec"]["text"]), t0=round(b["t0"], 2), t1=round(b["t1"], 2),
                    chunks=[(" ".join(w for w, _ in c["words"]), round(c["t0"], 2)) for c in b["chunks"]]) for b in beats],
              open(os.path.join(d, "explain_report.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"готово: {out}, {dur:.1f} с")


if __name__ == "__main__":
    main()
