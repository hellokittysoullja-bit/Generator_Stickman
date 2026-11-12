"""Конфиг выгрузки слоёв по планам room: диапазоны кадров (контракт клипа), масштаб S, окно рендера; пишет
room/chars/<id>/layout.json, room/cameras.json и chars_src/cfg.json (для render23.js)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.abspath(os.path.join(HERE, '..', '..'))
shots = {s['id']: s for s in json.load(open(os.path.join(STORY, 'shots.json')))['shots']}
PAD, END, FPS = 0.20, 34.10, 30
ORDER = ['L_dima', 'L_plaid', 'L_cat', 'L_fx']
FLAME_PX, TV_PX = [987, 934], [-260, 930]
DIMA_BOX = [60, 660, 560, 1260]
# окна камеры [cx, cy, h] в пикселях кадра 0 комнаты (1080×1920) на t0 и t1
CAM = {
    's01': ([540, 960, 1920], [513, 952, 1714], 'наезд 1.00→1.12 к лицу Димы'),
    's05': ([300, 925, 720], [306, 918, 680], 'крупно лицо, дрейф'),
    's06': ([820, 1010, 760], [818, 1000, 700], 'крупно кот, лёгкий наезд'),
    's12': ([440, 980, 1560], [330, 930, 1240], 'наезд на голову с карточками'),
    's13': ([300, 905, 680], [300, 900, 620], 'крупно лицо; тряска на «боится» 20.56: амплитуда 12 px, затухание 0.4 с'),
    's16': ([400, 1000, 1300], [395, 990, 1240], 'средний план'),
    's17': ([560, 1030, 1800], [580, 1040, 1600], 'широкий план, наезд'),
    's18': ([818, 1005, 700], [818, 1000, 660], 'крупно кот, конец'),
}
WIDE = {'s01', 's12', 's16', 's17'}
cfg, cams = [], {}
for sid, (c0, c1, note) in CAM.items():
    sh = shots[sid]
    start = max(0.0, sh['t0'] - PAD)
    end = END if sid == 's18' else min(END, sh['t1'] + PAD)
    n = int(round((end - start) * FPS))
    if sid in WIDE:
        S, region = 1.15, [0, 0, 1080, 1920]
    else:
        S = 2.2
        xs, ys = [], []
        for cx, cy, h in (c0, c1):
            w = h * 1080 / 1920
            xs += [cx - w / 2, cx + w / 2]
            ys += [cy - h / 2, cy + h / 2]
        mx, my = (max(xs) - min(xs)) * .08 + 14, (max(ys) - min(ys)) * .08 + 14
        x0, y0, x1, y1 = min(xs) - mx, min(ys) - my, max(xs) + mx, max(ys) + my
        w = x1 - x0
        h = w * 1920 / 1080 if (y1 - y0) < w * 1920 / 1080 else y1 - y0
        region = [round(x0), round((y0 + y1) / 2 - h / 2), round(w), round(h)]
    ow, oh = round(region[2] * S), round(region[3] * S)
    out = os.path.join(STORY, 'room', 'chars', sid)
    os.makedirs(out, exist_ok=True)
    lay = {"shot": sid, "fps": FPS, "t_start": round(start, 4), "frames": n, "frame_time": "t = t_start + k/30",
           "scale": S, "offset_px": region[:2], "size_px": region[2:], "out_size": [ow, oh], "order": ORDER,
           "flame_px": FLAME_PX, "tv_px": TV_PX, "dima_bbox_px": DIMA_BOX,
           "notes": "пиксель (u, v) PNG = точка кадра 0 комнаты (offset_px + (u, v) / scale). Камера в слои не запечена: окна — room/cameras.json. "
                    "L_dima — Дима (тело, голова) и карточки за головой; L_plaid — плед и всё Димино поверх пледа (тарелка, руки, вилка, пульт); "
                    "L_cat — кот с огоньком; L_fx — карточки перед лицом и пар над тарелкой. tv_px — телевизор за кадром слева спереди (ближе к камере)."}
    json.dump(lay, open(os.path.join(out, 'layout.json'), 'w'), ensure_ascii=False, indent=1)
    cams[sid] = {"t0": c0, "t1": c1, "note": note}
    if sid == 's13':
        cams[sid]["shake"] = {"at": 20.56, "amp_px": 12, "decay_s": 0.4, "hz": 18}
    cfg.append({"id": sid, "start": start, "n": n, "region": region, "S": S, "ow": ow, "oh": oh, "out": out})
json.dump(cams, open(os.path.join(STORY, 'room', 'cameras.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(cfg, open(os.path.join(HERE, 'cfg.json'), 'w'), indent=1)
for c in cfg:
    print(c['id'], c['n'], 'frames', c['region'], 'S', c['S'], (c['ow'], c['oh']))
