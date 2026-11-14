"""python3 sheet.py out.jpg a.png b.png ... [--w 360] — лист кадров в ряд (подпись — имя файла)."""
import sys
from PIL import Image, ImageDraw
a = sys.argv[1:]
w = 360
if "--w" in a:
    i = a.index("--w"); w = int(a[i + 1]); del a[i:i + 2]
out, files = a[0], a[1:]
ims = [Image.open(p).convert("RGB") for p in files]
ims = [im.resize((w, int(im.height * w / im.width)), Image.LANCZOS) for im in ims]
H = max(im.height for im in ims)
S = Image.new("RGB", (w * len(ims) + 6 * (len(ims) - 1), H + 26), "white")
d = ImageDraw.Draw(S)
for k, (im, p) in enumerate(zip(ims, files)):
    S.paste(im, (k * (w + 6), 26)); d.text((k * (w + 6) + 4, 6), p.rsplit("/", 1)[-1], fill="black")
S.save(out, quality=88)
