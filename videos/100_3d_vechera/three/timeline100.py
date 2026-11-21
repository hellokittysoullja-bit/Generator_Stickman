# Рилс 100: одна дорожка Димы (male2) по словам, паузы между репликами сжаты; огибающая рта для Димы.
import json, os, subprocess, numpy as np, wave
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SR = 48000; FPS = 30
W = json.load(open(f'{B}/v_dima/voice/words.json'))
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{B}/v_dima/voice/voice.wav', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
A = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
# (слова с..по, пауза перед репликой)
LINES = [(0, 13, 0.1), (13, 24, 0.25), (24, 33, 0.2), (33, 44, 0.2), (44, 48, 0.35), (48, 61, 0.3), (61, 69, 0.25), (69, 80, 0.25)]
TAIL = 2.2  # петля: кот возвращается без телефона
out = []; t = 0.0; lines = []
for a, b, gap in LINES:
    ws = W[a:b]; s0 = max(0, ws[0]['start'] - 0.06); s1 = ws[-1]['end'] + 0.1
    if b < len(W): s1 = min(s1, W[b]['start'] - 0.02)
    t += gap; seg = A[int(s0 * SR):int(s1 * SR)].copy(); f = int(0.008 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    lines.append(dict(speaker='dima', start=round(t, 3), end=round(t + s1 - s0, 3), words=[dict(word=w['word'], start=round(t + w['start'] - s0, 3), end=round(t + w['end'] - s0, 3)) for w in ws]))
    out.append((int(t * SR), seg)); t += s1 - s0
total = round(t + TAIL, 2); N = int(total * SR); mix = np.zeros(N, np.float32)
for o, seg in out: mix[o:o + len(seg)] += seg
with wave.open(f'{B}/voice_master.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
json.dump(dict(total=total, lines=lines), open(f'{B}/timeline.json', 'w'), ensure_ascii=False, indent=1)
n = int(total * FPS); hop = SR // FPS; r = np.array([np.sqrt(np.mean(mix[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
r = np.convolve(r, [0.25, 0.5, 0.25], 'same'); r = np.clip(r / (np.percentile(r[r > 1e-3], 95) + 1e-6), 0, 1)
json.dump(dict(total=total, lines=lines, mouth=dict(dima=[round(float(q), 3) for q in r])), open(f'{B}/three/voice100.json', 'w'), ensure_ascii=False)
for l in lines: print(l['start'], l['end'], ' '.join(w['word'] for w in l['words']))
print('total', total)
