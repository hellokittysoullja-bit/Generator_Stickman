"""Рилс 129: общая дорожка из голосов реплик (v_dima male2, v_kot Даниил) по dialog.json.
Каждая реплика вырезается из дорожки своего голоса по времени её слов, реплики идут подряд с паузой GAP.
Выход: voice/voice.wav (48 кГц, стерео) и voice/words.json (время слов в общей дорожке), voice/speakers.json (кто когда говорит).
python3 voice_merge.py"""
import json
import os
import re
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
GAP = 0.22
D = json.load(open(os.path.join(HERE, "dialog.json"), encoding="utf8"))["utterances"]


def load(who):
    d = os.path.join(HERE, f"v_{who}", "voice")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(d, "voice.wav"), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2), json.load(open(os.path.join(d, "words.json")))


def nwords(s):
    return len([w for w in re.split(r"\s+", s.strip()) if re.search(r"\w", w)])


def main():
    src = {w: load(w) for w in {u["who"] for u in D}}
    pos = {w: 0 for w in src}
    out, words, spk = [], [], []
    t = 0.0
    for u in D:
        a, W = src[u["who"]]
        i0 = pos[u["who"]]
        n = nwords(u["text"])
        ws = W[i0:i0 + n]
        pos[u["who"]] = i0 + n
        nxt = W[i0 + n]["start"] if i0 + n < len(W) else len(a) / SR
        s0 = max(0.0, ws[0]["start"] - .06)
        s1 = min(len(a) / SR, max(ws[-1]["end"] + .22, min(nxt - .04, ws[-1]["end"] + .35)))
        seg = a[int(s0 * SR):int(s1 * SR)].copy()
        f = int(.01 * SR)
        seg[:f] *= np.linspace(0, 1, f)[:, None]
        seg[-f:] *= np.linspace(1, 0, f)[:, None]
        for w in ws:
            words.append({"word": w["word"], "start": round(t + w["start"] - s0, 3), "end": round(t + w["end"] - s0, 3)})
        spk.append({"who": u["who"], "text": u["text"], "start": round(t, 3), "end": round(t + len(seg) / SR, 3),
                    "w0": len(words) - n, "w1": len(words) - 1})
        out.append(seg)
        t += len(seg) / SR
        out.append(np.zeros((int(GAP * SR), 2), np.float32))
        t += GAP
    audio = np.concatenate(out[:-1])
    vd = os.path.join(HERE, "voice")
    os.makedirs(vd, exist_ok=True)
    p = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le",
                        os.path.join(vd, "voice.wav")], input=audio.tobytes(), check=True)
    del p
    json.dump(words, open(os.path.join(vd, "words.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    json.dump(spk, open(os.path.join(vd, "speakers.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    for s in spk:
        print(s["who"], s["start"], s["end"], s["w0"], s["w1"], s["text"])
    print("слов", len(words), "длина", round(len(audio) / SR, 2))


if __name__ == "__main__":
    main()
