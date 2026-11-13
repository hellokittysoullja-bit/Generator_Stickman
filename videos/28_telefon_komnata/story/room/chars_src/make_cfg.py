"""Конфиг выгрузки слоёв по планам room рилса 28: диапазоны кадров (контракт клипа), масштаб S и окно рендера — по
настоящей камере сборщика (assemble.window + влёт hook_cam: углы выходного кадра обратно в кадр 0 для каждого слоя
героев на каждом кадре клипа). Пишет room/chars/<id>/layout.json, room/cameras.json и chars_src/cfg.json (для render25.js)."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOM = os.path.dirname(HERE)
STORY = os.path.dirname(ROOM)
sys.path.insert(0, ROOM)
import assemble as A  # noqa: E402

sj = json.load(open(os.path.join(STORY, 'shots.json')))
shots = {s['id']: s for s in sj['shots']}
PAD, END, FPS = sj['pad'], sj['end'], 30
ORDER = ['L_fxb', 'L_dima', 'L_plaid', 'L_cat', 'L_fx']
NOTE = {'s01': 'хук: влёт к Диме с учебником, карточки слов кружат вокруг головы',
        's04': 'крупно кот, наклон на «почему»',
        's14': 'средний план, наезд: карточки влетают в голову, Дима улыбается'}
only = sys.argv[1].split(',') if len(sys.argv) > 1 else list(A.CAM_DEFAULT)
cfg, cams = [], {}
for sid, (c0, c1) in A.CAM_DEFAULT.items():
    sh = shots[sid]
    A.G.clear()
    A.G.update(shot=sh, cams=dict(A.CAM_DEFAULT), shake={}, depths=dict(A.DEPTH_DEFAULT), clip=sid, pad=PAD, end=END)
    start, n = A.clip_range()
    xs, ys, smax = [], [], 0.0
    for k in range(n):
        t = start + k / FPS
        for L in ORDER:
            M, S = A.affine(A.G['depths'].get(L, A.G['depths']['L_dima']), t)
            Mi = np.linalg.inv(np.vstack([M.astype(np.float64), [0, 0, 1]]))
            for (u, v) in ((0, 0), (A.W, 0), (0, A.H), (A.W, A.H)):
                p = Mi @ [u, v, 1]
                xs.append(p[0])
                ys.append(p[1])
            smax = max(smax, S)
    S = round(min(2.6, 1.04 * smax), 3)
    m = 10
    x0, y0, x1, y1 = min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m
    region = [round(x0), round(y0), round(x1 - x0), round(y1 - y0)]
    ow, oh = round(region[2] * S), round(region[3] * S)
    out = os.path.join(ROOM, 'chars', sid)
    os.makedirs(out, exist_ok=True)
    lay = {"shot": sid, "fps": FPS, "t_start": round(start, 4), "frames": n, "frame_time": "t = t_start + k/30",
           "scale": S, "offset_px": region[:2], "size_px": region[2:], "out_size": [ow, oh], "order": ORDER,
           "flame_px": [987 + (-140 if sid == 's14' else 0), 934],
           "notes": "пиксель (u, v) PNG = точка кадра 0 комнаты (offset_px + (u, v) / scale). Камера — room/cameras.json + hook_cam. "
                    "L_fxb — карточки за головой; L_dima — Дима; L_plaid — плед, учебник и руки; L_cat — кот с огоньком; "
                    "L_fx — карточки перед лицом, искры."}
    json.dump(lay, open(os.path.join(out, 'layout.json'), 'w'), ensure_ascii=False, indent=1)
    cams[sid] = {"t0": c0, "t1": c1, "note": NOTE[sid]}
    if sid in only:
        cfg.append({"id": sid, "start": start, "n": n, "region": region, "S": S, "ow": ow, "oh": oh, "out": out,
                    "html": 'heroes28e.html'})
json.dump(cams, open(os.path.join(ROOM, 'cameras.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(cfg, open(os.path.join(HERE, 'cfg.json'), 'w'), indent=1)
for c in cfg:
    print(c['id'], c['n'], 'frames', c['region'], 'S', c['S'], (c['ow'], c['oh']))
