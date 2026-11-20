import json, glob, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(f'{S}/voice.json')); words = V['words']
groups = [[0, 1], [2], [3, 4, 5], [6, 7, 8], [9, 10]]
def font(sz, w):
    f = ImageFont.truetype(f'{S}/onest.ttf', sz); f.set_variation_by_axes([w]); return f
FS, FT = font(64, 700), font(34, 600)
def text_layer(img, txt, y, f, stroke):
    W = img.width; d = ImageDraw.Draw(img)
    lines = txt.split('\n')
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=f); x = (W - w) / 2; yy = y + i * f.size * 1.15
        sh = Image.new('RGBA', img.size, 0); ImageDraw.Draw(sh).text((x, yy + 3), ln, font=f, fill=(0, 0, 0, 150), stroke_width=stroke + 2, stroke_fill=(0, 0, 0, 150))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
        d.text((x, yy), ln, font=f, fill='white', stroke_width=stroke, stroke_fill=(20, 20, 20))
os.makedirs(f'{S}/out', exist_ok=True)
for p in sorted(glob.glob(f'{S}/frames/*.jpg')):
    i = int(os.path.basename(p)[1:5]); t = i / 30
    img = Image.open(p).convert('RGBA')
    text_layer(img, 'ПРИВЁЛ КОТА\nЗНАКОМИТЬСЯ С РОДИТЕЛЯМИ', 150, FT, 2)
    cur = None
    for g in groups:
        if words[g[0]]['start'] - 0.02 <= t: cur = g
    if cur is not None and t < words[-1]['end'] + 0.4:
        shown = [words[k]['word'] for k in cur if words[k]['start'] - 0.02 <= t]
        text_layer(img, ' '.join(shown).upper(), 1300, FS, 4)
    img.convert('RGB').save(f'{S}/out/{os.path.basename(p)}', quality=94)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', f'{S}/out/f%04d.jpg', '-i', '/home/user/Generator_Stickman/videos/97_3d_test/reel/voice/voice.wav',
                '-filter_complex', '[1]adelay=0|0,apad[a]', '-map', '0:v', '-map', '[a]', '-shortest', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', f'{S}/test3d.mp4'], check=True)
print('ok')
