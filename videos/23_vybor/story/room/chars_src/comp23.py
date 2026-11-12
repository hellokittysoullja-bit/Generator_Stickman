"""python3 comp23.py room.png layers_dir out.png [x y w h scale] — слои поверх фона (фон кадрируется и масштабируется так же)."""
import sys
from PIL import Image
bg = Image.open(sys.argv[1]).convert("RGBA")
if len(sys.argv) > 4:
    x, y, w, h, s = [float(v) for v in sys.argv[4:9]]
    bg = bg.crop((int(x), int(y), int(x + w), int(y + h))).resize((round(w * s), round(h * s)), Image.LANCZOS)
for L in ("L_dima", "L_plaid", "L_cat", "L_fx"):
    bg.alpha_composite(Image.open(f"{sys.argv[2]}/{L}.png").convert("RGBA"))
bg.convert("RGB").save(sys.argv[3])
