"""python3 composite.py bg.png layers_dir out.png [crop x0,y0,x1,y1] — слои героев поверх фона (порядок: дима, плед, кот)."""
import sys
from PIL import Image
bg = Image.open(sys.argv[1]).convert("RGBA")
for L in ("L_dima", "L_plaid", "L_cat"):
    bg.alpha_composite(Image.open(f"{sys.argv[2]}/{L}.png").convert("RGBA"))
if len(sys.argv) > 4:
    bg = bg.crop(tuple(int(v) for v in sys.argv[4].split(",")))
bg.convert("RGB").save(sys.argv[3])
