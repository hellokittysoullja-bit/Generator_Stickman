"""Конфиг выгрузки слоёв по планам room рилса 24: диапазоны кадров (контракт клипа), масштаб S, окно рендера; пишет
room/chars/<id>/layout.json, room/cameras.json и chars_src/cfg.json (для render24.js)."""
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
FLAME_PX = [987, 934]
NOTE = {'s03': 'средний план, лёгкий наезд', 's04': 'крупно лицо в свете ноутбука, медленный дрейф',
        's07': 'крупно кот, лёгкий наезд', 's14': 'средний план', 's16': 'средний план, наезд',
        's17': 'широкий план, наезд; толчок камеры на «празднует»', 's18': 'крупно кот, конец'}
WIDE = {'s03', 's14', 's16', 's17'}
only = sys.argv[1].split(',') if len(sys.argv) > 1 else list(CAM_DEFAULT)
cfg, cams = [], {}
for sid, (c0, c1) in CAM_DEFAULT.items():
    sh = shots[sid]
    start = max(0.0, sh['t0'] - PAD)
    end = END if sid == 's18' else min(END, sh['t1'] + PAD)
    n = int(round((end - start) * FPS))
    if True:
        S = round(min(2.2, max(1.15, 1.06 * 1920 / min(c0[2], c1[2]))), 3)
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
    lay = {"shot": sid, "fps": FPS, "t_start": round(start, 4), "frames": n, "frame_time": "t = t_start + k/30",
           "scale": S, "offset_px": region[:2], "size_px": region[2:], "out_size": [ow, oh], "order": ORDER,
           "flame_px": FLAME_PX,
           "notes": "пиксель (u, v) PNG = точка кадра 0 комнаты (offset_px + (u, v) / scale). Камера в слои не запечена: окна — room/cameras.json. "
                    "L_dima — Дима (тело, голова); L_plaid — плед и всё Димино поверх пледа (ноутбук, хлопушка, блокнот, руки); "
                    "L_cat — кот с огоньком (прыжок запечён в слой); L_fx — конфетти хлопушки, искры и конфетти кота."}
    json.dump(lay, open(os.path.join(out, 'layout.json'), 'w'), ensure_ascii=False, indent=1)
    cams[sid] = {"t0": c0, "t1": c1, "note": NOTE[sid]}
    if sid in only:
        cfg.append({"id": sid, "start": start, "n": n, "region": region, "S": S, "ow": ow, "oh": oh, "out": out})
json.dump(cams, open(os.path.join(ROOM, 'cameras.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(cfg, open(os.path.join(HERE, 'cfg.json'), 'w'), indent=1)
for c in cfg:
    print(c['id'], c['n'], 'frames', c['region'], 'S', c['S'], (c['ow'], c['oh']))
