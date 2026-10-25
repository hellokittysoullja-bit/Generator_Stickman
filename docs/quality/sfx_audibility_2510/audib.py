"""Слышен ли каждый звук рилса поверх голоса: RMS(голос+звуки) − RMS(голос) в окне звука (метод claude-youtube-editor)."""
import sys, os, wave, json
import numpy as np
sys.path.insert(0, "/home/user/Generator_Stickman/scripts")
import reel

class Got(Exception): pass
cap = {}
def fake_mix(path, total, shots, events, spec, voiced=False, voice=None):
    cap.update(total=total, shots=shots, events=events, spec=spec, voiced=voiced, voice=voice); raise Got()
orig_mix, orig_plan = reel.mix_audio, reel.sound_plan
reel.render_video = lambda *a, **k: None
reel.mix_audio = fake_mix

def read(p):
    with wave.open(p) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2) / 32767.0
    return x.mean(1)

def db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)

out = {}
for rd in sys.argv[1:]:
    cap.clear()
    try: reel.build(rd, force=True)
    except Got: pass
    tmp = os.path.dirname(__file__)
    plan = orig_plan(cap["shots"], cap["events"])
    a = os.path.join(tmp, "mix.wav"); v = os.path.join(tmp, "voice.wav")
    orig_mix(a, cap["total"], cap["shots"], cap["events"], cap["spec"], cap["voiced"], cap["voice"])
    reel.sound_plan = lambda s, e: []
    orig_mix(v, cap["total"], cap["shots"], cap["events"], cap["spec"], cap["voiced"], cap["voice"])
    reel.sound_plan = orig_plan
    A, V = read(a), read(v); SR = reel.SR
    from scipy.signal import butter, sosfilt
    hp = butter(4, 3000, 'hp', fs=SR, output='sos'); Ah, Vh = sosfilt(hp, A), sosfilt(hp, V)
    # нормировка пика в mix_audio могла масштабировать по-разному — сравниваем с учётом масштаба: голос в миксе
    # найден как проекция (звуки и голос не коррелируют)
    s = float(np.dot(A, V) / (np.dot(V, V) + 1e-9)); Vs = V * s
    rows = []
    for p in sorted(plan, key=lambda p: p["peak"]):
        w = 0.3 if p["name"] != "riser" else 1.0
        i0, i1 = int((p["peak"] - (w if p["name"] == "riser" else w / 2)) * SR), int((p["peak"] + (0 if p["name"] == "riser" else w / 2)) * SR)
        i0 = max(i0, 0)
        va, vv = db(A[i0:i1]), db(Vs[i0:i1]); sx = db(A[i0:i1] - Vs[i0:i1]); hadd = db(Ah[i0:i1]) - db(Vh[i0:i1])
        rows.append(dict(name=p["name"], peak=round(p["peak"], 2), gain=p["gain_db"], soft=p["soft"],
                         voice_db=round(float(vv), 1), add_db=round(float(va - vv), 1), snr=round(float(sx - vv), 1), hi_add=round(float(hadd), 1), under_voice=bool(vv > -35)))
    out[os.path.basename(os.path.dirname(rd.rstrip('/')))] = dict(voiced=cap["voiced"], scale=round(s, 3), rows=rows)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "audib.json"), "w"), ensure_ascii=False, indent=1)
for k, r in out.items():
    rs = r["rows"]; important = [x for x in rs if not x["soft"]]
    print(f"== {k} голос={r['voiced']} звуков={len(rs)}")
    for x in rs: print(f"  {x['peak']:6.2f} {x['name']:12s} gain={x['gain']:5.1f} soft={int(x['soft'])} голос в окне={x['voice_db']:6.1f} дБ  прибавка={x['add_db']:5.1f} дБ звук/голос={x['snr']:6.1f} дБ  выше 3 кГц +{x['hi_add']:4.1f}{'  ПОД РЕЧЬЮ' if x['under_voice'] else ''}")
