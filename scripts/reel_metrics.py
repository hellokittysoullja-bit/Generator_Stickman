"""Замеры готового рилса по пикселям и звуку — сравнить версии одним прибором, а не на глаз (22.10).

    python scripts/reel_metrics.py old.mp4 new.mp4          # картинка и звук
    python scripts/reel_metrics.py videos/NN/reel           # то же + темп по reel_report.json рядом с reel.mp4
    python scripts/reel_metrics.py --at 18.5 videos/NN/reel # что на экране и в звуке в эту секунду (провал на графике)

frozen_share — доля кадров, где картинка почти не меняется (без склеек); motion_median — средняя смена пикселей
кадр к кадру; sharpness — дисперсия вторых разностей (кипение линий вторым проходом снижало её на 11%);
silence_share / longest_silence_s — тишина звука (<-50 dB по 100 мс); sound_events — отдельные звуки (>-30 dB);
true_peak_db / lufs_i / lra — громкость мастера по ebur128 (true peak выше −1 dBTP — клиппинг на телефоне).
Картинка меряется по своей высоте (`picture_h` из reel_report.json, по умолчанию 1380): до 23.10 прибор резал 1420 px
и захватывал полосу субтитров — эталон перемерен новым прибором (план 04, п.1.26)."""
import json
import os
import re
import subprocess
import sys

import numpy as np

TRUE_PEAK_MAX = -1.0       # dBTP: выше — интерсэмпловый клиппинг после AAC на телефоне (SalimEdits dJidGbUDmqA)
WINDOW_SEC = 30.0          # окно для «смен рисунка» и «планов за первые 30 с»
MAX_SRC_CHANGES = 10       # смен рисунка за любые 30 с (Lang 1999: перегрузка после ~10 смен содержания за 30 с)


def frames(p, ph=1380):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-vf', f'crop=1080:{ph}:0:0,scale=270:{ph // 4},format=gray',
                        '-f', 'rawvideo', '-'], capture_output=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, ph // 4, 270).astype(np.float32)


def audio(p, sr=16000):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True)
    return np.frombuffer(r.stdout, np.float32)


def loudness(p):
    """True peak, интегральная громкость и LRA мастера (ebur128 с пиком по 4× передискретизации)."""
    err = subprocess.run(['ffmpeg', '-v', 'info', '-nostats', '-i', p, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    summ = err[err.rfind('Summary:'):]
    def num(key):
        m = re.search(key + r':\s+(-?[\d.]+|-inf)', summ)
        return None if not m or m.group(1) == '-inf' else round(float(m.group(1)), 1)
    return dict(true_peak_db=num('Peak'), lufs_i=num(r'\bI'), lra=num('LRA'))


def measure(p, ph=1380):
    a = frames(p, ph); d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
    moving = d[d <= 6]
    lap = [np.var(np.diff(f, 2, axis=0)) + np.var(np.diff(f, 2, axis=1)) for f in a[::15]]
    x = audio(p); w = 1600
    db = 20 * np.log10(np.array([np.sqrt(np.mean(x[i:i + w] ** 2)) for i in range(0, len(x) - w, w)]) + 1e-9)
    run = best = 0
    for v in db < -50: run = run + 1 if v else 0; best = max(best, run)
    ev = int(np.sum((db[1:] > -30) & (db[:-1] <= -30)))
    return dict(frozen_share=round(float((moving < 0.15).mean()), 3), motion_median=round(float(np.median(moving)), 3),
                sharpness=round(float(np.median(lap)), 1), silence_share=round(float((db < -50).mean()), 2),
                longest_silence_s=round(best * 0.1, 1), sound_events=ev, **loudness(p))


def tempo(report):
    """Темп по reel_report.json: планов за первые 30 с, смен рисунка за любые 30 с, разброс длин, доля куклы, повторы."""
    shots = report["shots"]; total = report["total"]
    durs = np.array([s["t1"] - s["t0"] for s in shots])
    changes = [s["t0"] for a, s in zip(shots, shots[1:]) if (s.get("src") or s["kind"]) != (a.get("src") or a["kind"])]
    worst = max([sum(t0 <= c < t0 + WINDOW_SEC for c in changes) for t0 in [0.0] + changes] or [0])
    doll = [s for s in shots if s["kind"] == "doll"]
    seq = []                                          # склейка / акцент / звук по времени: два одинаковых акцента подряд —
    for s in shots[1:]: seq.append((s["t0"], "склейка"))   # без склейки между ними — однообразно
    for e in report.get("events", []):
        if e["kind"] in ("punch", "shake", "spot", "circle", "write", "mark", "arrow"): seq.append((e["t"], e["kind"]))
    seq.sort()
    repeats = [f"{a[1]} {a[0]:.2f}→{b[0]:.2f}" for a, b in zip(seq, seq[1:]) if a[1] == b[1] != "склейка"]
    return dict(shots=len(shots), shots_first_30s=sum(s["t0"] < WINDOW_SEC for s in shots),
                src_changes_max_30s=worst, shot_cv=round(float(durs.std() / durs.mean()), 2),
                shot_min_s=round(float(durs.min()), 2), shot_max_s=round(float(durs.max()), 2),
                first_cut_s=shots[1]["t0"] if len(shots) > 1 else None,
                doll_share=round(sum(s["t1"] - s["t0"] for s in doll) / total, 2), doll_shots=len(doll),
                accent_repeats=repeats)


def at(report, t):
    """Что на экране и в звуке в секунду t: план, субтитр, звуки и фраза — чтобы провал графика удержания читался."""
    sh = next((s for s in report["shots"] if s["t0"] <= t < s["t1"]), report["shots"][-1])
    cap = next((c for c in report["captions"] if c["t0"] <= t < c["t1"]), None)
    said = " ".join(w["word"] for w in report["words"] if t - 2.0 <= w["start"] <= t)
    near = [f"{e['kind']}{'/' + e['name'] if e.get('name') else ''} {e['t']:.2f}" for e in report.get("events", [])
            if abs(e["t"] - t) <= 1.0]
    return dict(t=t, shot=f"{sh['t0']:.2f}–{sh['t1']:.2f} {sh.get('src') or sh['kind']}", caption=cap and cap["text"],
                said_last_2s=said, events_within_1s=near)


def warnings(m, tp=None):
    out = []
    if m.get("true_peak_db") is not None and m["true_peak_db"] > TRUE_PEAK_MAX:
        out.append(f"true peak {m['true_peak_db']} dBTP > {TRUE_PEAK_MAX}: клиппинг после сжатия")
    if tp and tp["src_changes_max_30s"] > MAX_SRC_CHANGES:
        out.append(f"смен рисунка за 30 с {tp['src_changes_max_30s']} > {MAX_SRC_CHANGES}: перегрузка")
    if tp and tp["accent_repeats"]:
        out.append("одинаковые акценты подряд без склейки: " + ", ".join(tp["accent_repeats"]))
    return out


def run(arg):
    if os.path.isdir(arg):
        rep = json.load(open(os.path.join(arg, "reel_report.json"), encoding="utf8"))
        m = measure(os.path.join(arg, "reel.mp4"), rep.get("picture_h", 1380)); tp = tempo(rep)
        return dict(m, tempo=tp, warnings=warnings(m, tp))
    m = measure(arg)
    return dict(m, warnings=warnings(m))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--at"]:
        rep = json.load(open(os.path.join(args[2], "reel_report.json"), encoding="utf8"))
        print(json.dumps(at(rep, float(args[1])), ensure_ascii=False, indent=1))
    else:
        print(json.dumps({p: run(p) for p in args}, ensure_ascii=False, indent=1))
