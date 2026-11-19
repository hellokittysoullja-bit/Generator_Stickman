import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
ST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ST + "/ext_a")
import s87a
from s87a import PE, lib
# кот с огоньком: SVG → PNG на белом
lib.DEFS.clear()
svg = lib.svg('<rect width="1080" height="1920" fill="#ffffff"/>' + PE.cat_svg(540, 1500, 1.4, dict(look=(-.4, -.2), perk=.8, smile=1.0, tail=8), 0.7))
open("cat.svg", "w").write(svg); open("l.txt", "w").write(os.path.abspath("cat.svg") + "\t" + os.path.abspath("cat.png"))
subprocess.check_call(["node", ST + "/common/render.js", "l.txt", "png", "1", "x"])
cat = Image.open("cat.png").convert("RGB")
bb = Image.eval(cat.convert("L"), lambda v: 255 if v < 245 else 0).getbbox()
cat = cat.crop(bb)
W, H = 2480, 3508
im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
F = "/home/user/Generator_Stickman/assets/fonts/reels/Onest[wght].ttf"
ft = ImageFont.truetype(F, 150); ft.set_variation_by_axes([800])
fs = ImageFont.truetype(F, 46); fs.set_variation_by_axes([600])
fm = ImageFont.truetype(F, 40); fm.set_variation_by_axes([500])
title = "Моя жизнь в неделях"
tw = d.textlength(title, font=ft); d.text(((W - tw) / 2, 150), title, font=ft, fill="#1f1d1a")
sub = "Каждая клетка это одна неделя. Закрашивай прожитые."
sw = d.textlength(sub, font=fm); d.text(((W - sw) / 2, 350), sub, font=fm, fill="#6b6660")
c = 35.0                               # клетка: 52 × 35 = 1820, 80 × 35 = 2800
gx = (W - 52 * c) / 2 + 40; gy = 500
g = 5
for r in range(80):
    for k in range(52):
        x0, y0 = gx + k * c + g / 2, gy + r * c + g / 2
        d.rectangle([x0, y0, x0 + c - g, y0 + c - g], outline="#8c8378", width=2)
    if r % 5 == 0:
        lb = str(r); lw = d.textlength(lb, font=fs)
        d.text((gx - 24 - lw, gy + r * c + c / 2 - 28), lb, font=fs, fill="#3a3632")
        d.line([gx - 16, gy + r * c + c / 2, gx - 4, gy + r * c + c / 2], fill="#3a3632", width=3)
lb = "80"; lw = d.textlength(lb, font=fs); d.text((gx - 24 - lw, gy + 80 * c - 28), lb, font=fs, fill="#3a3632")
for k in range(0, 53, 13):            # недели сверху: 1, 13, 26, 39, 52 — мелко
    pass
d.text((gx, gy - 70), "недели →", font=fm, fill="#6b6660")
d.text((gx - 190, gy - 70), "годы ↓", font=fm, fill="#6b6660")
link = "t.me/ru_adhd"; lw = d.textlength(link, font=fm)
d.text(((W - lw) / 2, H - 120), link, font=fm, fill="#6b6660")
ch = 230; cw = int(cat.width * ch / cat.height)
im.paste(cat.resize((cw, ch), Image.LANCZOS), (W - cw - 70, H - ch - 50))
im.save(ST + "/poster.png", dpi=(300, 300), optimize=True)
print(gx, gy, gy + 80 * c, os.path.getsize(ST + "/poster.png"))
