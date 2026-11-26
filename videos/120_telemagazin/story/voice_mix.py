"""Рилс 120: общий голос из двух дорожек (как рилс 98: v_*/ — свои reel.json и голоса, здесь общий voice/).
Ведущий (v_host, шаблон рилсов по умолчанию — Даниил) фразы 1–3, покупатель Дима (v_dima, male2) фраза 4, ведущий фразы 5–6.
Пишет voice/voice.wav, voice/words.json (слова подряд по времени ролика) и voice/timeline.json (кто когда говорит)."""
import json
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
CUT_A = 16.46          # конец «…две минуты.» у ведущего (тишина 16.40–16.52 по огибающей)
CUT_B = 16.50          # начало «Но подождите» (звук с 16.54)
GAP1, GAP2 = 0.30, 0.35


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def fade(x, a=0.01, b=0.03):
    na, nb = int(a * SR), int(b * SR)
    x[:na] *= np.linspace(0, 1, na)[:, None]
    x[-nb:] *= np.linspace(1, 0, nb)[:, None]
    return x


host, dima = load(os.path.join(HERE, "v_host/voice/voice.wav")), load(os.path.join(HERE, "v_dima/voice/voice.wav"))
hw = json.load(open(os.path.join(HERE, "v_host/voice/words.json")))
dw = json.load(open(os.path.join(HERE, "v_dima/voice/words.json")))
hw[0]["start"] = 0.04          # «Устали»: «У» звучит с 0.04 (огибающая), разметка дала 0.15
A = fade(host[:int(CUT_A * SR)])
B = fade(host[int(CUT_B * SR):])
D = fade(dima)
oD = CUT_A + GAP1
oB = oD + len(D) / SR + GAP2
out = np.zeros((int((oB + len(B) / SR) * SR) + 10, 2), np.float32)
out[:len(A)] += A
out[int(oD * SR):int(oD * SR) + len(D)] += D
out[int(oB * SR):int(oB * SR) + len(B)] += B
os.makedirs(os.path.join(HERE, "voice"), exist_ok=True)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", os.path.join(HERE, "voice/voice.wav")],
                     stdin=subprocess.PIPE)
p.communicate(out.tobytes())
r = lambda v: round(v, 3)  # noqa: E731
words = [dict(w, speaker="host") for w in hw[:40]]
words += [dict(w, start=r(w["start"] + oD), end=r(w["end"] + oD), speaker="dima") for w in dw]
words += [dict(w, start=r(w["start"] - CUT_B + oB), end=r(w["end"] - CUT_B + oB), speaker="host") for w in hw[40:]]
json.dump(words, open(os.path.join(HERE, "voice/words.json"), "w"), ensure_ascii=False, indent=1)
tl = {"host_a": [0.0, CUT_A], "dima": [r(oD), r(oD + len(D) / SR)], "host_b": [r(oB), r(oB + len(B) / SR)]}
json.dump(tl, open(os.path.join(HERE, "voice/timeline.json"), "w"), indent=1)
print(tl, len(words))
