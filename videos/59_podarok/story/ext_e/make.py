"""Рендер клипов группы E рилса 59 (s11, s14; сцены в kit.py): python3 make.py s11 [s14]  — clips/<id>.mp4 по контракту брифа;
python3 make.py s11 --sheet [t1,t2,...] — кадры PNG на эти моменты (по умолчанию 6 равномерно) + лист sheets/<id>.jpg.
Один процесс: SVG кадра строится в Python, растр — Chromium (render.js, один процесс), PNG потоком в ffmpeg."""
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
os.makedirs(os.path.join(STORY, "clips"), exist_ok=True)
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}
TMPB = "/tmp/e59"


def span(sid):
    s = SHOTS[sid]
    a = max(0.0, s["t0"] - SH["pad"])
    b = s["t1"] + SH["pad"]
    return a, int(round((b - a) * 30))


def main():
    sys.path.insert(0, HERE)
    args = sys.argv[1:]
    sheet = "--sheet" in args
    ids = [a for a in args if a.startswith("s") and a[1:].isdigit()]
    tl = [a for a in args if "," in a or a.replace(".", "").isdigit()]
    os.makedirs(TMPB, exist_ok=True)
    m = importlib.import_module("kit")
    for sid in ids:
        a, n = span(sid)
        tmp = tempfile.mkdtemp(dir=TMPB, prefix=sid + "_")
        t0 = time.time()
        if sheet:
            times = [float(x) for x in tl[0].split(",")] if tl else [a + (n - 1) / 30 * k / 5 for k in range(6)]
        else:
            times = [a + k / 30 for k in range(n)]
        svgs = []
        for i, t in enumerate(times):
            p = os.path.join(tmp, f"f{i:04d}.svg")
            open(p, "w").write(m.frame(sid, t))
            svgs.append(p)
        if sheet:
            outd = os.path.join(TMPB, "sheets", sid)
            os.makedirs(outd, exist_ok=True)
            pngs = [os.path.join(outd, f"{sid}_{t:.2f}.png") for t in times]
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(f"{s}\t{p}" for s, p in zip(svgs, pngs)))
            subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "list.txt"), "png", "1", "x"])
            print(sid, "sheet", " ".join(pngs))
        else:
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(svgs))
            subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "list.txt"), "mp4", "1", os.path.join(tmp, "seg")])
            out = os.path.join(STORY, "clips", f"{sid}.mp4")
            shutil.copy(os.path.join(tmp, "seg_0.mp4"), out)
            print(sid, n, "кадров", f"{time.time() - t0:.0f} с", out)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
