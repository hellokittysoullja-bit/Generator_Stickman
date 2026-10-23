"""Черновик рилса программой (23.10, решение владельца: экономить токены без потери качества).

Агент пишет только сценарий — `reel_script.txt` рядом с будущим reel.json, по фразе в строке:

    Ты не *ленишься*.            @f1
    Ты не видишь *время*.        @f5
    «Ещё пять минут»… |а уже *ночь*.
    ...

`*слово*` — ключевое (оранжевое, на нём наезд), `|` — разрыв группы субтитров, `@fN` — какой кадр эпизода под
фразой (без метки — тот же, что у прошлой фразы). Кадры эпизода берутся из `../frames/00N.png` как f1, f2, ...

Программа делает всё механическое, что раньше писалось руками и тратило токены, — по правилам reel_rules:
riser с нулевой секунды и раскрытие на его пике; окна кадрирования по пятнам туши на рисунке (общий план → крупнее →
деталь, без пустой бумаги); второй план во фразе длиннее ~2.8 с; вход наездом на новый рисунок, хлёст со свистом на
смене места в том же рисунке; наезд на первом ключевом слове через фразу; финал на рисунке начала (петля).

Чего программа НЕ делает и что решает качество — остаётся агенту, правкой reel.json после черновика:
диссонанс первой фразы, звуки по смыслу (`oof` на провале, `swoosh_deep` на появлении), окна под смысл слова,
пометки от руки, кукла, часы хука. Черновик — каркас, а не готовый рилс.

    python scripts/reel_draft.py videos/NN/reel          # reel_script.txt -> reel.json (старый — в reel.json.bak)
"""
import json
import os
import re
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel  # noqa: E402
import reel_rules  # noqa: E402

SHOT_SPLIT_SEC = 2.8       # фраза длиннее — второй план на середине (правило «план ≤ 3 с» с запасом)
PUNCH_EVERY = 2            # наезд на ключевом слове — через фразу, а не на каждой (акцент на всём = ни на чём)


def parse(path):
    beats = []
    for line in open(path, encoding="utf8"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        m = re.search(r"\s@(f\d+)\s*$", line)
        src = m.group(1) if m else None
        text = line[:m.start()].strip() if m else line
        beats.append(dict(text=text, src=src))
    if beats and not beats[0]["src"]: beats[0]["src"] = "f1"
    for a, b in zip(beats, beats[1:]):
        b["src"] = b["src"] or a["src"]
    return beats


def ink_views(img):
    """Окна [cx, cy, h] в координатах ИСХОДНОГО кадра (src увеличен вдвое). Пятна туши двух крупностей (слитые
    предметы и отдельные), мельче 1% кадра не берутся. Горизонтальный рисунок 3:2 в вертикальное окно целиком не
    входит, поэтому каждое окно сдвигается туда, где его края идут по пустой бумаге, а не по рисунку — то же правило,
    что у камеры длинных роликов («край кадра не режет предмет», camera.edge_cross)."""
    small = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4), interpolation=cv2.INTER_AREA)
    ink = (small.mean(axis=2) < 200).astype(np.uint8)
    H, W = ink.shape                                    # 1/4 размера src = 1/2 исходного кадра
    probe = {"beats": [{"text": "", "shots": [{"from": [0, 0, 1.0]}]}]}; reel.layout(probe)
    vk = probe["beats"][0]["shots"][0]["from"][2]; aspect = reel.W * vk / reel.PH
    def edge_cost(cx, cy, h):                           # тушь на краях окна, как на экране после view_scale
        hh, ww = h * vk, h * aspect                     # окно h (как в reel.json) на экране: h·vk в высоту
        x0, x1, y0, y1 = int(cx - ww / 2), int(cx + ww / 2), int(cy - hh / 2), int(cy + hh / 2)
        cost = 0
        for x in (x0, x1):
            if 0 <= x < W: cost += ink[max(0, y0):min(H, y1), max(0, x - 1):x + 2].sum()
        for y in (y0, y1):
            if 0 <= y < H: cost += ink[max(0, y - 1):y + 2, max(0, x0):min(W, x1)].sum()
        return cost
    def place(bx0, by0, bx1, by1):
        h = min(max((by1 - by0) / vk, (bx1 - bx0) / aspect) * 1.15, H / vk)
        h = max(h, 0.3 * H / vk)
        cx0, cy0 = (bx0 + bx1) / 2, (by0 + by1) / 2; w = h * aspect
        best = None
        for dx in np.linspace(-0.3, 0.3, 13) * w:
            for dy in np.linspace(-0.15, 0.15, 5) * h:
                c_ = edge_cost(cx0 + dx, cy0 + dy, h) + 0.02 * (abs(dx) + abs(dy))
                if best is None or c_ < best[0]: best = (c_, cx0 + dx, cy0 + dy)
        return [round(best[1] * 2, 1), round(best[2] * 2, 1), round(h * 2, 1)]   # 1/2 кадра -> кадр
    rows = np.where(ink.mean(axis=1) > 0.005)[0]; cols = np.where(ink.mean(axis=0) > 0.005)[0]
    if not len(rows):
        return [[W, H, 2 * H / vk]]
    views = [place(cols[0], rows[0], cols[-1], rows[-1])]
    for k in (31, 11):
        blob = cv2.dilate(ink, np.ones((k, k), np.uint8))
        n, _lab, st, _ = cv2.connectedComponentsWithStats(blob)
        for x, y, w, h, _a in sorted((st[i] for i in range(1, n) if st[i][4] > 0.01 * H * W), key=lambda s: -s[4])[:4]:
            views.append(place(x, y, x + w, y + h))
    out = []
    for v in views:                                     # без почти одинаковых окон
        if all(abs(v[0] - o[0]) + abs(v[1] - o[1]) > 0.2 * o[2] or abs(v[2] - o[2]) > 0.2 * o[2] for o in out):
            out.append(v)
    return out[:6]


def draft(reel_dir):
    lines = parse(os.path.join(reel_dir, "reel_script.txt"))
    srcs = sorted({b["src"] for b in lines}, key=lambda s: int(s[1:]))
    sources = {s: {"frame": f"../frames/{int(s[1:]):03d}.png"} for s in srcs}
    reel.prepare_src(reel_dir, sources)
    views = {s: ink_views(reel.load_src(reel_dir, s)) for s in srcs}
    used = {s: 0 for s in srcs}
    words_all, _spans = reel.tokens([dict(text=b["text"]) for b in lines])
    times = reel.estimate_times([reel.clean(w) for w in words_all])
    beats, wi, prev_src = [], 0, None
    for bi, b in enumerate(lines):
        n = len(reel.tokens([dict(text=b["text"])])[0])
        dur = times[min(wi + n, len(times) - 1)]["start"] - times[wi]["start"] if wi + n < len(times) else 1.5
        def next_view(src):
            v = views[src][used[src] % len(views[src])]; used[src] += 1
            return v
        v = next_view(b["src"])
        shot = {"at": 0, "src": b["src"], "from": v, "to": [v[0], v[1], round(v[2] * 0.94, 1)]}
        if b["src"] != prev_src and bi > 0: shot["zoom_in"] = 0.3
        elif bi > 0: shot["whip"] = [-560 if bi % 2 else 560, 0]
        shots = [shot]
        if dur > SHOT_SPLIT_SEC and n > 3:
            v2 = next_view(b["src"])
            shots.append({"at": n // 2, "src": b["src"], "from": v2, "to": [v2[0], v2[1], round(v2[2] * 0.94, 1)]})
        fx = []
        keys = [k for k, w in enumerate(reel.tokens([dict(text=b["text"])])[0]) if "*" in w]
        if keys and bi % PUNCH_EVERY == 1:
            fx.append({"kind": "punch", "at": keys[0], "amt": 0.12})
        beats.append({"text": b["text"], "shots": shots, "fx": fx})
        wi += n; prev_src = b["src"]
    # хук: riser с нулевой секунды, раскрытие на его пике, наезд с разгоном в эту склейку
    beats[0]["fx"].append({"kind": "sfx", "name": "riser", "at": 0, "align": "start", "dt": -0.25})
    beats[0]["shots"][0]["ease"] = "in"
    if len(beats) > 1: beats[1]["after_sfx"] = "riser"
    for s in beats[1]["shots"] if len(beats) > 1 else []:
        s.pop("whip", None)
    # петля: финал на рисунке начала, тем же окном
    first = beats[0]["shots"][0]
    beats[-1]["shots"][0].update(src=first["src"], **{"from": first["to"], "to": first["from"]})
    beats[-1]["shots"][0].pop("whip", None); beats[-1]["shots"][0]["zoom_in"] = 0.25
    passport = {"hook_type": "", "structure": "", "devices": []}   # заполняет агент: reel_rules сверит с docs/reels_log.json
    # знания базы (маркетинг, воронка, бренд, удержание): у каждого пункта — номер фразы или {"skip": "причина"};
    # пока стоит TODO, reel.py не рендерит (docs/reels_knowledge/apply_checklist.json)
    items = reel_rules.load_json(reel_rules.CHECKLIST_PATH, {"items": []})["items"]
    passport["knowledge"] = {it["id"]: "TODO" for it in items if it["kind"] == "beat"}
    passport.update({"goal": {"question": "TODO", "emotion": "TODO"}, "cta_beat": len(lines) - 2, "labels": [],
                     "cover": {"text": ""}, "caption": "", "hook_variants": []})
    spec = {"title": lines[0]["text"], "rate": 1.15, "lead_in": 0.25, "tail": 0.45, "sources": sources, "passport": passport,
            "beats": beats,
            "_draft": "черновик reel_draft.py: звуки по смыслу, окна под слова, пометки и кукла — руками"}
    out = os.path.join(reel_dir, "reel.json")
    if os.path.exists(out): os.replace(out, out + ".bak")
    json.dump(spec, open(out, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    errs = reel_rules.check_spec(spec, set(reel.SFX))
    print(out, f"— фраз {len(beats)}, планов {sum(len(b['shots']) for b in beats)}")
    print("\n".join("  ✗ " + e for e in errs) or "  ✓ правила reel.json соблюдены (тайминг проверит reel.py)")
    return out


if __name__ == "__main__":
    draft(sys.argv[1])
