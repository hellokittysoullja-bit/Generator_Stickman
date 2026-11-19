"""Заголовок хука рилса 82 «ОПЯТЬ / ОПОЗДАЛ?» — экранный слой (камера и влёт его НЕ двигают).
Бриф docs/story_brief_82.md, раздел «ЗАГОЛОВОК»: жирный IDB (Inter Display Black, вшит в common/base.html), заглавные,
белые буквы с чёрной обводкой ~8 px и мягкой тенью (вариант style="yellow" — #FFD23F). Две строки одним кеглем, кегль —
под ширину ≤ 980 px по длинной строке (поля ≥ 50 px), верхняя зона y ≈ 130–520.
Влёт: на кадре 0 уже виден (масштаб START=1.1 — при 1.4 строка режется краями), к ~0.2 с — 1.0 затухающей пружиной (перелёт ~0.94); непрозрачность 0.85→1 за 2 кадра.
Тряска: толчок масштаба +6 % и сдвиг ±8 px на каждом ударе голоса, затухание 0.18 с. Уход: на t_out масштаб 1→0.85 и
прозрачность 1→0 за 0.15 с. Время — аргументами (hits — начала слов из voice/words.json, t_out — t0 плана из shots.json).

API: layer(t, text, t_in, t_out, hits, style) -> SVG-строка (пусто вне окна); text_box(...) -> (x0, y0, x1, y1) рамка
надписи в покое (с обводкой). Самопроверка: python3 big_title.py out.png --t 0.0 0.1 0.2 1.0 2.4 (лист кадров)."""
import base64
import io
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
MAX_W = 968.0            # ширина букв; с обводкой ≤ 976 px — поле ≥ 52 px с каждой стороны
SIZE_MAX = 190.0         # кегль не больше
TOP = 135.0              # верх надписи (шапка Reels ~110 px)
LEAD = 0.96              # межстрочный шаг в кеглях
STROKE = 8.0             # обводка (видимая половина снаружи — paint-order: stroke)
START = 1.1              # масштаб на кадре 0: бриф просил 1.4, но тогда «ОПОЗДАЛ?» режется краями кадра
                         # (ширина 976×1.4 > 1080); 1.1 — самый крупный влёт, при котором надпись целиком в кадре
COLORS = {"white": "#FFFFFF", "yellow": "#FFD23F"}
_ADV = {}
_UPM = [2048, 1490]      # unitsPerEm, высота заглавных


def _adv():
    """Ширины знаков IDB из шрифта, вшитого в base.html (точно как рисует браузер, без кернинга)."""
    if _ADV:
        return _ADV
    try:
        from fontTools.ttLib import TTFont
        s = open(os.path.join(HERE, "base.html"), encoding="utf-8").read()
        m = re.search(r'font-family:"IDB";src:url\(data:font/otf;base64,([^)]*)\)', s)
        f = TTFont(io.BytesIO(base64.b64decode(m.group(1))))
        cm, hm = f.getBestCmap(), f["hmtx"]
        _UPM[0], _UPM[1] = f["head"].unitsPerEm, f["OS/2"].sCapHeight
        for code, g in cm.items():
            _ADV[chr(code)] = hm[g][0]
    except Exception:                                     # без fontTools — средняя ширина заглавной IDB
        _ADV["_"] = 1490
    return _ADV


def text_w(s, size):
    a = _adv()
    d = a.get("_", 1490)
    return sum(a.get(c, d) for c in s) * size / _UPM[0]


def layout(text="ОПЯТЬ\nОПОЗДАЛ?"):
    """Кегль и строки: [(строка, x_центр, y_базовой)], size, cap."""
    lines = text.split("\n")
    size = min(SIZE_MAX, min(MAX_W / max(1e-6, text_w(s, 1.0)) for s in lines))
    size = math.floor(size)
    cap = size * _UPM[1] / _UPM[0]
    out = []
    y = TOP + cap
    for s in lines:
        out.append((s, W / 2, y))
        y += size * LEAD
    return out, size, cap


def text_box(text="ОПЯТЬ\nОПОЗДАЛ?", **_):
    """Рамка надписи в покое (буквы + обводка), экранные пиксели."""
    lines, size, cap = layout(text)
    wmax = max(text_w(s, size) for s, _, _ in lines)
    x0 = W / 2 - wmax / 2 - STROKE / 2
    y0 = lines[0][2] - cap - STROKE / 2
    y1 = lines[-1][2] + STROKE / 2 + size * 0.02
    return (x0, y0, W - x0, y1)


def _spring_in(u):
    """Масштаб влёта: 1.4 на u=0 → 1.0 к ~0.2 с, перелёт ~0.94 и затухание."""
    if u <= 0:
        return START
    return 1.0 + (START - 1.0) * math.exp(-15.0 * u) * math.cos(2 * math.pi * 3.1 * u)


def _hit(t, hits):
    """(добавка масштаба, сдвиг x, сдвиг y) от ударов голоса, затухание 0.18 с."""
    ds = dx = dy = 0.0
    for k, h in enumerate(hits or ()):
        u = t - h
        if u < 0 or u > 0.18:
            continue
        rise = min(1.0, u / 0.035)
        env = rise * math.exp(-max(0.0, u - 0.035) / 0.05)
        ds += 0.06 * env
        sgn = 1 if k % 2 == 0 else -1
        dx += sgn * 8.0 * env * math.cos(2 * math.pi * 14 * u)
        dy += -0.5 * 8.0 * env * math.sin(2 * math.pi * 11 * u)
    return ds, dx, dy


def layer(t, text="ОПЯТЬ\nОПОЗДАЛ?", t_in=0.0, t_out=None, hits=(), style="white"):
    """SVG-группа заголовка в экранных координатах (кладётся поверх кадра, вне камеры)."""
    if t < t_in - 1e-6:
        return ""
    if t_out is not None and t >= t_out + 0.15:
        return ""
    lines, size, cap = layout(text)
    x0, y0, x1, y1 = text_box(text)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    u = t - t_in
    s = _spring_in(u)
    op = 0.85 + 0.15 * min(1.0, u / (2 / 30.0)) if u < 2 / 30.0 else 1.0
    ds, dx, dy = _hit(t, hits)
    s += ds
    if t_out is not None and t >= t_out:
        v = min(1.0, (t - t_out) / 0.15)
        s *= 1.0 - 0.15 * v
        op *= 1.0 - v
    if op <= 0.002:
        return ""
    fill = COLORS.get(style, style)
    sh = (f'<filter id="btsh" x="-20%" y="-20%" width="140%" height="160%">'
          f'<feGaussianBlur stdDeviation="6"/></filter>')
    rows = []
    for s_, x, y in lines:
        rows.append((s_, x, y))
    common = (f'font-family="IDB" font-size="{size}" text-anchor="middle" '
              f'style="font-kerning:none;font-variant-ligatures:none"')
    shadow = "".join(f'<text x="{x:.1f}" y="{y + 6:.1f}" {common} fill="#000" stroke="#000" stroke-width="{STROKE * 2:.1f}" '
                     f'stroke-linejoin="round">{s_}</text>' for s_, x, y in rows)
    body = "".join(f'<text x="{x:.1f}" y="{y:.1f}" {common} fill="{fill}" stroke="#111" stroke-width="{STROKE * 2:.1f}" '
                   f'stroke-linejoin="round" paint-order="stroke">{s_}</text>' for s_, x, y in rows)
    tr = f"translate({cx + dx:.2f} {cy + dy:.2f}) scale({s:.4f}) translate({-cx:.2f} {-cy:.2f})"
    return (f'<defs>{sh}</defs><g transform="{tr}" opacity="{op:.3f}">'
            f'<g filter="url(#btsh)" opacity="0.45">{shadow}</g>{body}</g>')


def _demo(out, times, style):
    import json
    import subprocess
    import tempfile
    story = os.path.dirname(HERE)
    sh = json.load(open(os.path.join(story, "shots.json")))
    wd = json.load(open(os.path.join(story, "voice", "words.json")))
    ti = sh.get("title", {})
    t_out = {s["id"]: s["t0"] for s in sh["shots"]}.get(ti.get("t_out_cut", "s03"))
    hits = [wd[i]["start"] for i in ti.get("hits", [1, 2, 6])]
    tmp = tempfile.mkdtemp()
    items = []
    for i, t in enumerate(times):
        g = layer(t, t_out=t_out, hits=hits, style=style)
        bx = text_box()
        frame = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#9fc3d8"/>'
                 f'<rect x="{bx[0]:.0f}" y="{bx[1]:.0f}" width="{bx[2] - bx[0]:.0f}" height="{bx[3] - bx[1]:.0f}" fill="none" '
                 f'stroke="#d33" stroke-width="2" stroke-dasharray="10 8"/>{g}'
                 f'<text x="40" y="1880" font-family="IDB" font-size="60" fill="#333">t={t:.2f}</text></svg>')
        p = os.path.join(tmp, f"{i}.svg")
        open(p, "w").write(frame)
        items.append(f"{p}\t{os.path.join(tmp, f'{i}.png')}")
    open(os.path.join(tmp, "l.txt"), "w").write("\n".join(items))
    subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "l.txt"), "png", "1", "x"])
    n = len(times)
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(tmp, "%d.png"), "-vf",
                           f"scale=360:-1,tile={n}x1", "-frames:v", "1", out])
    print("кегль", layout()[1], "рамка", [round(v) for v in text_box()], "→", out)


if __name__ == "__main__":
    import sys
    a = sys.argv[1:]
    out = a[0] if a and not a[0].startswith("--") else "big_title.png"
    ts = [float(x) for x in a[a.index("--t") + 1:]] if "--t" in a else [0.0, 0.1, 0.2, 1.0, 2.4]
    _demo(out, [x for x in ts if not x != x], "yellow" if "--yellow" in a else "white")
