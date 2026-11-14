import sys, glob
from PIL import Image
sid = sys.argv[1]
fs = sorted(glob.glob(f"/tmp/a59f/sheets/{sid}/{sid}_*.png"), key=lambda p: float(p.rsplit("_", 1)[1][:-4]))
ims = [Image.open(f).convert("RGB").resize((360, 640)) for f in fs]
cols = 6 if len(ims) > 6 else len(ims)
rows = (len(ims) + cols - 1) // cols
W = Image.new("RGB", (cols * 360, rows * 640))
for i, im in enumerate(ims):
    W.paste(im, ((i % cols) * 360, (i // cols) * 640))
W.save(f"/tmp/a59f/{sid}_sheet.jpg", quality=85)
print(f"/tmp/a59f/{sid}_sheet.jpg")
