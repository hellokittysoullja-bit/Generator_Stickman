import json, glob, os, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = os.path.dirname(os.path.abspath(__file__)); R = '/home/user/Generator_Stickman'; B = f'{R}/videos/98_3d_sdvg'
T = json.load(open(f'{B}/timeline.json'))
def font(sz, w):
    f = ImageFont.truetype(f'{S}/onest.ttf', sz); f.set_variation_by_axes([w]); return f
FS, FT, FH = font(66, 750), font(38, 650), font(80, 850)
chunks = []
for l in T['lines']:
    ws = l['words']; i = 0
    while i < len(ws):
        n = 3 if len(ws) - i > 4 else len(ws) - i
        if n > 3: n = 2
        chunks.append(ws[i:i + n]); i += n
def text(img, txt, y, f, stroke, scale=1.0, fill='white'):
    d = ImageDraw.Draw(img); W = img.width
    for i, ln in enumerate(txt.split('\n')):
        w = d.textlength(ln, font=f); x = (W - w) / 2; yy = y + i * f.size * 1.12
        sh = Image.new('RGBA', img.size, 0); ImageDraw.Draw(sh).text((x, yy + 4), ln, font=f, fill=(0, 0, 0, 170), stroke_width=stroke + 3, stroke_fill=(0, 0, 0, 170))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
        d.text((x, yy), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=(15, 15, 15))
def star(d, x, y, r, a):
    pts = [(x + math.cos(k * math.pi / 4 - math.pi / 2) * (r if k % 2 == 0 else r * 0.28), y + math.sin(k * math.pi / 4 - math.pi / 2) * (r if k % 2 == 0 else r * 0.28)) for k in range(8)]
    d.polygon(pts, fill=(255, 214, 80, int(255 * a)))
os.makedirs(f'{S}/out98', exist_ok=True)
for p in sorted(glob.glob(f'{S}/frames98/*.jpg')):
    i = int(os.path.basename(p)[1:5]); t = i / 30
    img = Image.open(p).convert('RGBA'); W, H = img.size
    if t < 3.6:
        pop = min(1, t / 0.15)
        hook = 'ТЫ ТОЖЕ СЛЫШАЛ:\n«В НАШЕ ВРЕМЯ\nСДВГ НЕ БЫЛО»?'
        lay = Image.new('RGBA', img.size, 0); text(lay, hook, 250, FH, 5)
        if pop < 1: lay = lay.resize((int(W * (0.85 + 0.15 * pop)), int(H * (0.85 + 0.15 * pop)))); off = Image.new('RGBA', img.size, 0); off.alpha_composite(lay, ((W - lay.width) // 2, int(250 * (1 - (0.85 + 0.15 * pop))))); lay = off
        img.alpha_composite(lay)
    else:
        text(img, 'СКАЗАЛ РОДИТЕЛЯМ ПРО СДВГ', 250, FT, 2)
    cur = None
    for c in chunks:
        if c[0]['start'] - 0.03 <= t: cur = c
    if cur and t < cur[-1]['end'] + 0.35:
        shown = [w['word'].upper() for w in cur if w['start'] - 0.03 <= t]
        text(img, ' '.join(shown), 1270, FS, 4)
    mp = p[:-4] + '.json'
    if os.path.exists(mp):
        m = json.load(open(mp)); age = t - m['tap']
        if 0 <= age < 1.0:
            bx, by = m['btn'][0] * W, m['btn'][1] * H
            gl = Image.new('RGBA', img.size, 0); d = ImageDraw.Draw(gl)
            for k in range(16):
                an = k / 16 * 6.283 + (k % 3) * 0.2; dist = 30 + age * (260 + (k % 4) * 60); a = max(0, 1 - age)
                star(d, bx + math.cos(an) * dist, by + math.sin(an) * dist - age * age * 120, 34 * (1 - age * 0.5) * (0.7 + (k % 3) * 0.2), a)
            img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(6))); img.alpha_composite(gl)
    img.convert('RGB').save(f'{S}/out98/{os.path.basename(p)}', quality=94)
# звук
SFX = f'{R}/assets/sfx/reels'; lib = json.load(open(f'{SFX}/library.json'))
plan = [('fast_whoosh', 0.13, -10), ('riser', 1.85, -15), ('swoosh', 6.45, -14), ('shock', 6.75, -12), ('swoosh_deep', 14.6, -12), ('fast_whoosh', 16.1, -12), ('level_up', 18.66, -8), ('oof', 23.25, -11)]
args = ['ffmpeg', '-v', 'error', '-y', '-i', f'{B}/voice_master.wav']; fl = []
for k, (n, peak, g) in enumerate(plan):
    args += ['-i', f"{SFX}/{lib[n]['file']}"]; st = max(0, peak - lib[n]['peak_sec'])
    fl.append(f"[{k + 1}]aresample=48000,volume={g}dB,adelay={int(st * 1000)}|{int(st * 1000)}[s{k}]")
mix = ''.join(f'[s{k}]' for k in range(len(plan)))
fl.append(f"[0]aresample=48000[v];[v]{mix}amix=inputs={len(plan) + 1}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
subprocess.run(args + ['-filter_complex', ';'.join(fl), '-map', '[a]', '-ar', '48000', f'{S}/mix98.wav'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', f'{S}/out98/f%04d.jpg', '-i', f'{S}/mix98.wav', '-map', '0:v', '-map', '1:a', '-shortest',
                '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f'{B}/reel.mp4'], check=True)
print('ok')
