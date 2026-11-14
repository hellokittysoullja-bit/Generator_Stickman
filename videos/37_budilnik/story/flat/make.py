"""Рендер клипов сцены flat рилса 37 (s14–s18): python3 make.py s14 [s15 ...] → ../clips/<id>.mp4 по контракту
брифа (1080×1920, 30 к/с, H.264 CRF 16, yuv420p, без звука; кадр k = max(0, t0−0.2) + k/30, до t1+0.2, s18 — до 27.9).
python3 make.py s14 --sheet [t1,t2,...] — PNG кадров на эти моменты (по умолчанию 6 равномерно) в TMP/sheets/<id>/.
SVG кадров строит Python (4 процесса), растр — Chromium (render.js, 4 процесса), PNG потоком в ffmpeg."""
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.dirname(HERE)
SH = json.load(open(os.path.join(STORY, "shots.json")))
SHOTS = {s["id"]: s for s in SH["shots"]}
TMP = os.environ.get("FLAT_TMP", "/tmp/claude-0/-home-user-Generator-Stickman/9595787f-b591-5c3d-bdd0-89e667214c94/scratchpad/flat/tmp")
NP = 4


def span(sid):
    s = SHOTS[sid]
    a = max(0.0, s["t0"] - SH["pad"])
    b = SH["end"] if sid == "s18" else min(s["t1"] + SH["pad"], SH["end"])
    return a, int(round((b - a) * 30))


def _job(args):
    sys.path.insert(0, HERE)
    sid, t, path = args
    open(path, "w").write(importlib.import_module(sid).frame(t))
    return path


def build_svgs(sid, times, tmp):
    jobs = [(sid, t, os.path.join(tmp, f"f{i:04d}.svg")) for i, t in enumerate(times)]
    with Pool(NP) as p:
        return p.map(_job, jobs, chunksize=4)


def main():
    sys.path.insert(0, HERE)
    args = sys.argv[1:]
    sheet = "--sheet" in args
    ids = [a for a in args if a.startswith("s") and a[1:].isdigit()]
    tl = [a for a in args if "," in a or a.replace(".", "").isdigit()]
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(os.path.join(STORY, "clips"), exist_ok=True)
    for sid in ids:
        a, n = span(sid)
        tmp = tempfile.mkdtemp(dir=TMP, prefix=sid + "_")
        t0 = time.time()
        if sheet:
            times = [float(x) for x in tl[0].split(",")] if tl else [a + (n - 1) / 30 * k / 5 for k in range(6)]
            svgs = build_svgs(sid, times, tmp)
            outd = os.path.join(TMP, "sheets", sid)
            os.makedirs(outd, exist_ok=True)
            pngs = [os.path.join(outd, f"{sid}_{t:.2f}.png") for t in times]
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(f"{s}\t{p}" for s, p in zip(svgs, pngs)))
            subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "list.txt"), "png",
                                   str(min(NP, len(times))), "x"])
            print(sid, "sheet", " ".join(pngs))
        else:
            times = [a + k / 30 for k in range(n)]
            svgs = build_svgs(sid, times, tmp)
            t1 = time.time()
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(svgs))
            pre = os.path.join(tmp, "seg")
            subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "list.txt"), "mp4", str(NP), pre])
            segs = sorted((x for x in os.listdir(tmp) if x.startswith("seg_") and x.endswith(".mp4")),
                          key=lambda x: int(x[4:-4]))
            open(os.path.join(tmp, "concat.txt"), "w").write("".join(f"file '{os.path.join(tmp, s)}'\n" for s in segs))
            out = os.path.join(STORY, "clips", f"{sid}.mp4")
            subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                                   os.path.join(tmp, "concat.txt"), "-c", "copy", "-movflags", "+faststart", out])
            nf = int(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                              "stream=nb_read_frames", "-of", "csv=p=0", out]).decode().strip())
            print(f"{sid}: {out} frames {nf}/{n}  svg {t1 - t0:.0f}s render {time.time() - t1:.0f}s")
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
