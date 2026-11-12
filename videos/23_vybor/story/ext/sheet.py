"""python3 sheet.py out.jpg a.png b.png ... — лист кадров в ряд (по 540 px в ширину)."""
import sys
from PIL import Image
ims = [Image.open(p).convert("RGB") for p in sys.argv[2:]]
w = 540; h = int(w * 1920 / 1080)
cols = min(len(ims), 4); rows = (len(ims) + cols - 1) // cols
S = Image.new("RGB", (cols * w + (cols - 1) * 8, rows * h + (rows - 1) * 8), "white")
for i, im in enumerate(ims):
    S.paste(im.resize((w, h), Image.LANCZOS), ((i % cols) * (w + 8), (i // cols) * (h + 8)))
S.save(sys.argv[1], quality=90)
