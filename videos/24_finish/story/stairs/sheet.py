"""Лист кадров: python3 sheet.py s01 0.0,0.3,... [out.jpg] — рендер PNG через render.js и склейка."""
import os, subprocess, sys, tempfile
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene
TMP = "/tmp/claude-0/-home-user/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/stairs"
sid = sys.argv[1]
times = [float(x) for x in sys.argv[2].split(",")]
out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(TMP, f"sheet_{sid}.jpg")
crop = sys.argv[4] if len(sys.argv) > 4 else None
d = tempfile.mkdtemp(dir=TMP)
lst = []
for i, t in enumerate(times):
    p = os.path.join(d, f"f{i}.svg"); open(p, "w").write(scene.frame(sid, t))
    lst.append(f"{p}\t{os.path.join(d, f'f{i}.png')}")
open(os.path.join(d, "l.txt"), "w").write("\n".join(lst))
subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(d, "l.txt"), "png", str(min(3, len(times))), "x"])
ims = [Image.open(os.path.join(d, f"f{i}.png")).convert("RGB") for i in range(len(times))]
if crop:
    x0, y0, x1, y1 = map(int, crop.split(","))
    ims = [im.crop((x0, y0, x1, y1)) for im in ims]
    w = ims[0].width
    sc = 1.0
else:
    sc = 0.36
ims = [im.resize((int(im.width * sc), int(im.height * sc))) for im in ims]
n = len(ims); cols = min(n, 6)
rows = (n + cols - 1) // cols
W, H = ims[0].width, ims[0].height
o = Image.new("RGB", (W * cols, H * rows), "white")
for i, im in enumerate(ims):
    o.paste(im, ((i % cols) * W, (i // cols) * H))
o.save(out, quality=88)
for i in range(len(times)):
    os.rename(os.path.join(d, f"f{i}.png"), os.path.join(TMP, f"{sid}_{times[i]:.2f}.png"))
import shutil; shutil.rmtree(d)
print(out)
