# Сборка рилса 99: кадры Blender 540×960 → lanczos 1080×1920, заголовок, субтитры по словам, звуки владельца, loudnorm −16.
import json, glob, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = os.path.dirname(os.path.abspath(__file__)); R = '/home/user/Generator_Stickman'; B = os.path.dirname(S)
FR = sys.argv[1]  # папка кадров fNNNN.jpg
T = json.load(open(f'{B}/timeline.json')); LN = T['lines']
def font(sz, w):
    f = ImageFont.truetype(f'{S}/onest.ttf', sz); f.set_variation_by_axes([w]); return f
FS, FT, FH = font(66, 750), font(38, 650), font(76, 850)
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
HOOK = 'СКОЛЬКО ХОББИ\nТЫ БРОСИЛ\nНА ВТОРОЙ ДЕНЬ?\nУ ДИМЫ ДЕВЯТЬ.'
def clean(w): return w.upper().replace('«', '').replace('»', '').rstrip(',.')
files = sorted(glob.glob(f'{FR}/f*.jpg'))
# звук
SFX = f'{R}/assets/sfx/reels'; lib = json.load(open(f'{SFX}/library.json'))
wt = lambda li, wi: LN[li]['words'][wi]['start']
tend = LN[5]['end'] + 0.25
plan = [('fast_whoosh', 0.08, -10), ('swoosh', 0.35, -13), ('swoosh_deep', 0.66, -11), ('shock', 0.82, -12),
        ('fast_whoosh', LN[1]['start'], -14), ('swoosh', wt(1, 4) - 0.05, -15), ('oof', LN[2]['start'] + 0.05, -11),
        ('swoosh', LN[3]['start'], -15), ('shock', wt(3, 3) + 0.05, -14), ('fast_whoosh', LN[4]['start'], -14), ('fast_glitch', wt(4, 6), -16),
        ('swoosh_deep', LN[5]['start'] + 0.1, -13), ('typing', wt(5, 1), -14), ('level_up', wt(5, 2) + 0.05, -10),
        ('swoosh', tend, -14), ('swoosh_deep', tend + 0.6, -14), ('shock', tend + 1.7, -15)]
args = ['ffmpeg', '-v', 'error', '-y', '-i', f'{B}/voice_master.wav']; fl = []
for k, (n, peak, g) in enumerate(plan):
    args += ['-i', f"{SFX}/{lib[n]['file']}"]; st = max(0, peak - lib[n]['peak_sec'])
    fl.append(f"[{k + 1}]aresample=48000,volume={g}dB,adelay={int(st * 1000)}|{int(st * 1000)}[s{k}]")
mix = ''.join(f'[s{k}]' for k in range(len(plan)))
fl.append(f"[0]aresample=48000[v];[v]{mix}amix=inputs={len(plan) + 1}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
WAV = f'{S}/mix99.wav'
subprocess.run(args + ['-filter_complex', ';'.join(fl), '-map', '[a]', '-ar', '48000', '-t', str(T['total']), WAV], check=True)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30', '-i', '-', '-i', WAV, '-map', '0:v', '-map', '1:a', '-shortest',
                        '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f'{B}/reel.mp4'], stdin=subprocess.PIPE)
for p in files:
    i = int(os.path.basename(p)[1:5]); t = i / 30
    img = Image.open(p).convert('RGB').resize((1080, 1920), Image.LANCZOS).convert('RGBA')
    if t < 3.6:
        pop = min(1, t / 0.15); lay = Image.new('RGBA', img.size, 0); text(lay, HOOK, 200, FH, 5)
        if pop < 1:
            s = 0.85 + 0.15 * pop; lay2 = lay.resize((int(1080 * s), int(1920 * s))); lay = Image.new('RGBA', img.size, 0); lay.alpha_composite(lay2, ((1080 - lay2.width) // 2, int(200 * (1 - s))))
        img.alpha_composite(lay)
    else:
        text(img, 'МАМА ОТКРЫЛА ШКАФ ДИМЫ', 200, FT, 2)
    cur = None
    for c in chunks:
        if c[0]['start'] - 0.03 <= t: cur = c
    if cur and t < cur[-1]['end'] + 0.35:
        text(img, ' '.join(clean(w['word']) for w in cur if w['start'] - 0.03 <= t), 1270, FS, 4)
    enc.stdin.write(img.convert('RGB').tobytes())
enc.stdin.close(); enc.wait(); os.remove(WAV); print('ok', len(files))
