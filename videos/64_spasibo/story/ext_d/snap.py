"""Отладка: python3 snap.py s14 33.9 34.9 … — полноразмерные PNG кадров в D64_TMP/snap_<id>_<t>.png (и сшитые в одну полосу)."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s64d  # noqa: E402
from make import BASE_TMP, STORY  # noqa: E402

sid = sys.argv[1]
ts = [float(x) for x in sys.argv[2:]]
os.makedirs(BASE_TMP, exist_ok=True)
d = tempfile.mkdtemp(dir=BASE_TMP)
lst = []
for i, t in enumerate(ts):
    p = os.path.join(d, f"{i}.svg")
    open(p, "w").write(s64d.frame(sid, t))
    lst.append(f"{p}\t{os.path.join(d, f'p{i:03d}.png')}")
open(d + "/l.txt", "w").write("\n".join(lst))
subprocess.check_call(["node", os.path.join(STORY, "common", "render.js"), d + "/l.txt", "png", "1", "x"])
out = os.path.join(BASE_TMP, f"snap_{sid}.jpg")
subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(d, "p%03d.png"), "-vf", f"scale=540:-1,tile={len(ts)}x1",
                       "-frames:v", "1", out])
subprocess.call(["rm", "-rf", d])
print(out)
