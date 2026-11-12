"""Проверка слоёв room: (1) альфа <255 глубже 2 px от края силуэта; (2) лист: 3 кадра каждого плана поверх фона комнаты.
python3 audit23.py room_bg.png out_dir"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

BG, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(HERE, 'cfg.json')))
room = Image.open(BG).convert('RGBA')
L = ('L_dima', 'L_plaid', 'L_cat', 'L_fx')
KEY = {'s01': [0, 15, 40], 's05': [5, 30, 55], 's06': [10, 21, 60], 's12': [5, 35, 60], 's13': [8, 40, 80],
       's16': [5, 25, 45], 's17': [10, 30, 70], 's18': [10, 40, 75]}
for c in cfg:
    worst = 0
    for k in range(0, c['n'], 4):
        for l in L:
            a = np.array(Image.open(f"{c['out']}/{l}/{k:04d}.png"))[..., 3]
            if a.max() == 0:
                continue
            ins = np.array(Image.fromarray(((a > 0) * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))) > 0
            worst = max(worst, int((ins & (a < 255)).sum()))
    x, y, w, h = c['region']
    bg = room.crop((x, y, x + w, y + h)).resize((c['ow'], c['oh']), Image.LANCZOS)
    row = []
    for k in KEY[c['id']]:
        k = min(k, c['n'] - 1)
        im = bg.copy()
        for l in L:
            im.alpha_composite(Image.open(f"{c['out']}/{l}/{k:04d}.png"))
        im = im.convert('RGB')
        im.save(f"{OUT}/{c['id']}_{k:02d}.png")
        row.append(im.resize((c['ow'] * 600 // c['oh'], 600)))
    sheet = Image.new('RGB', (sum(r.width for r in row) + 20, 600), (20, 20, 20))
    xx = 0
    for r in row:
        sheet.paste(r, (xx, 0)); xx += r.width + 10
    sheet.save(f"{OUT}/sheet_{c['id']}.png")
    print(c['id'], 'кадров', c['n'], '| пикселей с альфой<255 внутри силуэта (макс):', worst)
