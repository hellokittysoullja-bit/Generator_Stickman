"""Надписи «ДО» / «ПОСЛЕ» на превью владельца (12.11): белый жирный гротеск, как у «это Даня», обводка чёрная еле
заметная. На белом фоне белые буквы без тени не видны — мягкая тень снизу (shadow) держит их читаемыми."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
base = Image.open(sys.argv[1]).convert("RGBA"); out = sys.argv[2]
shadow_a = int(sys.argv[3]) if len(sys.argv) > 3 else 90
W, H = base.size
F = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 124)
layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
for txt, cx in (("ДО", W * 0.25), ("ПОСЛЕ", W * 0.75)):
    d = ImageDraw.Draw(layer); ds = ImageDraw.Draw(sh)
    w = d.textlength(txt, font=F); x, y = cx - w / 2, 14
    ds.text((x + 4, y + 8), txt, font=F, fill=(0, 0, 0, shadow_a))
    d.text((x, y), txt, font=F, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 70))
    d.text((x, y), txt, font=F, fill=(255, 255, 255, 255))
sh = sh.filter(ImageFilter.GaussianBlur(10))
Image.alpha_composite(Image.alpha_composite(base, sh), layer).convert("RGB").save(out, quality=95)
print(out)
