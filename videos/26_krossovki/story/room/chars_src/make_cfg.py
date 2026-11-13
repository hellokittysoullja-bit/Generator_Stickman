"""Конфиг выгрузки слоёв по планам room рилса 26: диапазоны кадров (контракт клипа), масштаб S, окно рендера, какая
HTML-сцена (s02 лёжа — heroes26l.html, остальные — heroes26e.html); пишет room/chars/<id>/layout.json, room/cameras.json и
chars_src/cfg.json (для render25.js)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOM = os.path.dirname(HERE)
STORY = os.path.dirname(ROOM)
sys.path.insert(0, ROOM)
from assemble import CAM_DEFAULT  # noqa: E402

sj = json.load(open(os.path.join(STORY, 'shots.json')))
shots = {s['id']: s for s in sj['shots']}
PAD, END, FPS = sj['pad'], sj['end'], 30
ORDER = ['L_dima', 'L_plaid', 'L_cat', 'L_fx']
FLAME = {'lie': [987, 934], 'eve': [987, 934]}   # s02: переписывается из heroes26l (FLAME_C)
NOTE = {'s02': 'средний план, наезд: кулак «завтра», обмяк; кот с сомнением', 's05': 'крупно кот, наклон на «почему»',
        's13': 'средний план: пишет на стикере, кот смотрит', 's17': 'крупно кот у пустой коробки, конец'}
try:
    FLAME['lie'] = json.load(open(os.path.join(HERE, 'flame26l.json')))
except FileNotFoundError:
    pass
only = sys.argv[1].split(',') if len(sys.argv) > 1 else list(CAM_DEFAULT)
cfg, cams = [], {}
for sid, (c0, c1) in CAM_DEFAULT.items():
    sh = shots[sid]
    start = max(0.0, sh['t0'] - PAD)
    end = min(END, sh['t1'] + PAD)
    n = int(round((end - start) * FPS))
    S = round(min(2.6, max(1.15, 1.06 * 1920 / min(c0[2], c1[2]))), 3)
    xs, ys = [], []
    for cx, cy, h in (c0, c1):
        w = h * 1080 / 1920
        xs += [cx - w / 2, cx + w / 2]
        ys += [cy - h / 2, cy + h / 2]
    mx, my = (max(xs) - min(xs)) * .05 + 14, (max(ys) - min(ys)) * .05 + 14
    x0, y0, x1, y1 = min(xs) - mx, min(ys) - my, max(xs) + mx, max(ys) + my
    w = x1 - x0
    h = w * 1920 / 1080 if (y1 - y0) < w * 1920 / 1080 else y1 - y0
    region = [round(x0), round((y0 + y1) / 2 - h / 2), round(w), round(h)]
    ow, oh = round(region[2] * S), round(region[3] * S)
    out = os.path.join(ROOM, 'chars', sid)
    os.makedirs(out, exist_ok=True)
    kind = 'lie' if sid == 's02' else 'eve'
    lay = {"shot": sid, "fps": FPS, "t_start": round(start, 4), "frames": n, "frame_time": "t = t_start + k/30",
           "scale": S, "offset_px": region[:2], "size_px": region[2:], "out_size": [ow, oh], "order": ORDER,
           "flame_px": FLAME[kind],
           "notes": "пиксель (u, v) PNG = точка кадра 0 комнаты (offset_px + (u, v) / scale). Камера — room/cameras.json. "
                    "L_dima — Дима (и подушка в s02); L_plaid — плед и всё поверх него (руки, стикер, чипсы, коробка); L_cat — кот с огоньком; L_fx — пусто."}
    json.dump(lay, open(os.path.join(out, 'layout.json'), 'w'), ensure_ascii=False, indent=1)
    cams[sid] = {"t0": c0, "t1": c1, "note": NOTE[sid]}
    if sid in only:
        cfg.append({"id": sid, "start": start, "n": n, "region": region, "S": S, "ow": ow, "oh": oh, "out": out,
                    "html": 'heroes26l.html' if kind == 'lie' else 'heroes26e.html'})
json.dump(cams, open(os.path.join(ROOM, 'cameras.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(cfg, open(os.path.join(HERE, 'cfg.json'), 'w'), indent=1)
for c in cfg:
    print(c['id'], c['n'], 'frames', c['region'], 'S', c['S'], (c['ow'], c['oh']))
