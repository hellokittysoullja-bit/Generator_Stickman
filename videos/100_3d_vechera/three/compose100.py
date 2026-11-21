# Сборка рилса 100: кадры Blender 540×960 → lanczos 1080×1920, хук-надпись и заголовок, субтитры по словам, влёт с размытием,
# искры на нажатии (2D), звуки владельца, loudnorm −16.
import json, glob, os, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
S = os.path.dirname(os.path.abspath(__file__)); R = '/home/user/Generator_Stickman'; B = os.path.dirname(S)
FR = sys.argv[1]
T = json.load(open(f'{B}/timeline.json')); LN = T['lines']
def font(sz, w):
    f = ImageFont.truetype(f'{S}/onest.ttf', sz); f.set_variation_by_axes([w]); return f
FS, FT, FH = font(66, 750), font(40, 700), font(82, 850)
chunks = []
for l in LN:
    ws = l['words']; i = 0
    while i < len(ws):
        n = 3 if len(ws) - i > 4 else len(ws) - i
        if n > 3: n = 2
        chunks.append(ws[i:i + n]); i += n
def text(img, txt, y, f, stroke, fill='white'):
    d = ImageDraw.Draw(img); W = img.width
    for i, ln in enumerate(txt.split('\n')):
        w = d.textlength(ln, font=f); x = (W - w) / 2; yy = y + i * f.size * 1.12
        sh = Image.new('RGBA', img.size, 0); ImageDraw.Draw(sh).text((x, yy + 4), ln, font=f, fill=(0, 0, 0, 170), stroke_width=stroke + 3, stroke_fill=(0, 0, 0, 170))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
        d.text((x, yy), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=(15, 15, 15))
def star(d, x, y, r, a):
    pts = [(x + math.cos(k * math.pi / 4 - math.pi / 2) * (r if k % 2 == 0 else r * 0.28), y + math.sin(k * math.pi / 4 - math.pi / 2) * (r if k % 2 == 0 else r * 0.28)) for k in range(8)]
    d.polygon(pts, fill=(255, 214, 80, int(255 * a)))
HOOK = 'ПЕРЕСТАЛ ТЕРЯТЬ\nВЕЧЕРА В ЛЕНТЕ'
def clean(w): return w.upper().replace('«', '').replace('»', '').rstrip(',.')
wt = lambda li, wi: LN[li]['words'][wi]['start']
# звук (времена — те же события, что в scene100.js)
SFX = f'{R}/assets/sfx/reels'; lib = json.load(open(f'{SFX}/library.json'))
CLICK = wt(4, 0) + 0.04; TAP = wt(7, 8); POP = wt(7, 4); CAT_JUMP = wt(7, 1) - 0.1; T_END = LN[7]['end'] + 0.12
plan = [('fast_whoosh', 0.08, -10), ('shock', wt(0, 1) + 0.12, -14), ('swoosh', wt(0, 6) - 0.06, -15), ('swoosh_deep', wt(0, 10), -16),
        ('fast_whoosh', LN[1]['start'] - 0.08, -13), ('swoosh', wt(1, 5) - 0.04, -15), ('oof', wt(1, 9), -13),
        ('fast_whoosh', LN[2]['start'] - 0.08, -13), ('fast_glitch', wt(2, 1), -17), ('swoosh', wt(2, 7) - 0.04, -15),
        ('swoosh_deep', LN[3]['start'] - 0.08, -14), ('swoosh', wt(3, 4) - 0.04, -16),
        ('shock', CLICK, -11), ('typing', CLICK + 0.02, -14),
        ('swoosh', LN[5]['start'] - 0.08, -15), ('fast_whoosh', LN[5]['start'] + 1.5, -15), ('swoosh', wt(5, 5) - 0.04, -15), ('keyboard_soft', LN[5]['start'] + 1.7, -17),
        ('fast_whoosh', LN[6]['start'] - 0.08, -14), ('keyboard_soft', LN[6]['start'] + 0.1, -16), ('swoosh', wt(6, 5) - 0.04, -16),
        ('swoosh_deep', LN[7]['start'] - 0.08, -14), ('fast_whoosh', CAT_JUMP + 0.2, -14), ('swoosh', POP, -15), ('swoosh', wt(7, 5) - 0.04, -16), ('swoosh', wt(7, 7) - 0.04, -16), ('level_up', TAP + 0.03, -9),
        ('fast_whoosh', T_END + 0.05, -13), ('swoosh_deep', T_END + 0.45, -15)]
args = ['ffmpeg', '-v', 'error', '-y', '-i', f'{B}/voice_master.wav']; fl = []
for k, (n, peak, g) in enumerate(plan):
    args += ['-i', f"{SFX}/{lib[n]['file']}"]; st = max(0, peak - lib[n]['peak_sec'])
    fl.append(f"[{k + 1}]aresample=48000,volume={g}dB,adelay={int(st * 1000)}|{int(st * 1000)}[s{k}]")
mix = ''.join(f'[s{k}]' for k in range(len(plan)))
fl.append(f"[0]aresample=48000[v];[v]{mix}amix=inputs={len(plan) + 1}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
WAV = f'{S}/mix100.wav'
subprocess.run(args + ['-filter_complex', ';'.join(fl), '-map', '[a]', '-ar', '48000', '-t', str(T['total']), WAV], check=True)
files = sorted(glob.glob(f'{FR}/f*.jpg'))
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30', '-i', '-', '-i', WAV, '-map', '0:v', '-map', '1:a', '-shortest',
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f'{B}/reel.mp4'], stdin=subprocess.PIPE)
for p in files:
    i = int(os.path.basename(p)[1:5]); t = i / 30
    img = Image.open(p).convert('RGB').resize((1080, 1920), Image.LANCZOS)
    if t < LN[1]['start'] - 0.08 or t >= T_END + 0.05 or (LN[4]['start'] - 0.12 <= t < CLICK):  # кресло и сумрак до щелчка: лицо в Blender пересвечено фронтом — ниже и теплее
        img = ImageEnhance.Color(ImageEnhance.Brightness(img).enhance(0.86)).enhance(1.15)
    if t < 0.25:  # радиальное размытие влёта
        k = 1 - t / 0.25; acc = img.copy()
        for n, s in enumerate((1.03, 1.06, 1.09)):
            z = img.resize((int(1080 * (1 + (s - 1) * k)), int(1920 * (1 + (s - 1) * k))), Image.BILINEAR); x0 = (z.width - 1080) // 2; y0 = (z.height - 1920) // 2
            acc = Image.blend(acc, z.crop((x0, y0, x0 + 1080, y0 + 1920)), 1 / (n + 2))
        img = acc
    img = img.convert('RGBA')
    if t < 3.5:
        pop = min(1, t / 0.15); lay = Image.new('RGBA', img.size, 0); text(lay, HOOK, 190, FH, 6)
        if pop < 1:
            s = 0.85 + 0.15 * pop; lay2 = lay.resize((int(1080 * s), int(1920 * s))); lay = Image.new('RGBA', img.size, 0); lay.alpha_composite(lay2, ((1080 - lay2.width) // 2, int(190 * (1 - s))))
        img.alpha_composite(lay)
    else:
        text(img, 'ВОТ ЧТО Я ПОМЕНЯЛ', 190, FT, 3)
    mp = p[:-4] + '.json'
    if os.path.exists(mp):
        m = json.load(open(mp)); age = t - m['tap']
        if 0 <= age < 1.0 and m.get('btn'):
            bx, by = m['btn'][0] * 1080, m['btn'][1] * 1920
            gl = Image.new('RGBA', img.size, 0); d = ImageDraw.Draw(gl)
            for k in range(16):
                an = k / 16 * 6.283 + (k % 3) * 0.2; dist = 30 + age * (260 + (k % 4) * 60); a = max(0, 1 - age)
                star(d, bx + math.cos(an) * dist, by + math.sin(an) * dist - age * age * 120, 34 * (1 - age * 0.5) * (0.7 + (k % 3) * 0.2), a)
            img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(6))); img.alpha_composite(gl)
    cur = None
    for c in chunks:
        if c[0]['start'] - 0.03 <= t: cur = c
    if cur and t < cur[-1]['end'] + 0.35:
        text(img, ' '.join(clean(w['word']) for w in cur if w['start'] - 0.03 <= t), 1300, FS, 4)
    enc.stdin.write(img.convert('RGB').tobytes())
enc.stdin.close(); enc.wait(); os.remove(WAV); print('ok', len(files))
