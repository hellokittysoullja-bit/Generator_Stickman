# Склейка трёх голосов в одну дорожку по словам: реплики по порядку сценария, паузы 0.2–0.35 с; огибающая рта по говорящему.
import json, os, subprocess, numpy as np, wave
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SR = 48000; FPS = 30
W = {v: json.load(open(f'{B}/v_{v}/voice/words.json')) for v in ('mom', 'dima', 'dad')}
def pcm(v):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{B}/v_{v}/voice/voice.wav', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
A = {v: pcm(v) for v in W}
# (кто, слова с..по, пауза перед репликой)
LINES = [('mom', 0, 3, 0.45), ('dima', 0, 10, 0.3), ('dad', 0, 5, 0.25), ('mom', 3, 7, 0.2), ('dima', 10, 20, 0.3), ('dima', 20, 29, 0.35)]
TAIL = 2.6  # финал: кот залезает в шкаф
out = []; t = 0.0; lines = []
for sp, a, b, gap in LINES:
    ws = W[sp][a:b]; s0 = max(0, ws[0]['start'] - 0.06); s1 = ws[-1]['end'] + 0.1
    if b < len(W[sp]): s1 = min(s1, W[sp][b]['start'] - 0.02)
    t += gap; seg = A[sp][int(s0 * SR):int(s1 * SR)].copy(); f = int(0.008 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    lines.append(dict(speaker=sp, start=round(t, 3), end=round(t + s1 - s0, 3), words=[dict(word=w['word'], start=round(t + w['start'] - s0, 3), end=round(t + w['end'] - s0, 3)) for w in ws]))
    out.append((int(t * SR), seg, sp)); t += s1 - s0
total = round(t + TAIL, 2); N = int(total * SR); mix = np.zeros(N, np.float32); per = {v: np.zeros(N, np.float32) for v in W}
for o, seg, sp in out: mix[o:o + len(seg)] += seg; per[sp][o:o + len(seg)] += seg
with wave.open(f'{B}/voice_master.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
json.dump(dict(total=total, lines=lines), open(f'{B}/timeline.json', 'w'), ensure_ascii=False, indent=1)
mouth = {}
for v, x in per.items():
    n = int(total * FPS); hop = SR // FPS; r = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
    r = np.convolve(r, [0.25, 0.5, 0.25], 'same'); r = np.clip(r / (np.percentile(r[r > 1e-3], 95) + 1e-6), 0, 1); mouth[v] = [round(float(q), 3) for q in r]
json.dump(dict(total=total, lines=lines, mouth=mouth), open(f'{B}/three/voice99.json', 'w'), ensure_ascii=False)
for l in lines: print(l['speaker'], l['start'], l['end'], ' '.join(w['word'] for w in l['words']))
print('total', total)
