"""python3 prev.py OUT shot:t[:crop] ... — слои (preview24.js) + сборка кадра assemble.py → OUT/<shot>_<t>.png и лист OUT/sheet.png.
crop: x0,y0,x1,y1 в пикселях выхода — дополнительно сохраняет увеличенную вырезку."""
import os
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOM = os.path.dirname(HERE)
out = sys.argv[1]
specs = sys.argv[2:]
subprocess.run(['node', os.path.join(HERE, 'preview24.js'), out] + [':'.join(s.split(':')[:2]) for s in specs], check=True)
sys.argv = ['x']
sys.path.insert(0, ROOM)
import assemble as A  # noqa: E402
ims = []
for s in specs:
    parts = s.split(':')
    shot, ts = parts[0], parts[1]
    A.G.clear()
    A.load(os.environ.get('ROOM24_PASSES', '/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/blender/p24all'),
           os.path.join(out, f'{shot}_{ts}'), shot)
    t = float(ts)
    im = A.to8(A.frame(0, t=t))[..., ::-1]
    cv2.imwrite(os.path.join(out, f'{shot}_{ts}.png'), im)
    ims.append(cv2.resize(im, (405, 720), interpolation=cv2.INTER_AREA))
    if len(parts) > 2:
        x0, y0, x1, y1 = map(int, parts[2].split(','))
        cr = im[y0:y1, x0:x1]
        cv2.imwrite(os.path.join(out, f'{shot}_{ts}_crop.png'), cr)
cv2.imwrite(os.path.join(out, 'sheet.png'), np.hstack(ims))
print('ok', len(ims))
