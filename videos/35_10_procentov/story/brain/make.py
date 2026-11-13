"""Рендер 2D-клипов рилса 35, сцена «мозг» (brain: s01 s02 s07 s08 s10 s15; vault: s11 s12): python3 make.py s02 [s14 ...]  — клип clips/<id>.mp4 по контракту брифа;
python3 make.py s02 --sheet [t1,t2,...] — кадры PNG на эти моменты (по умолчанию 6 равномерно) + лист sheets/<id>.jpg.
SVG кадров строятся в Python, растр — Chromium в NP процессов (по умолчанию 2), PNG потоком в ffmpeg."""
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
SCENE_MOD = {"s01": "scene_brain35", "s02": "scene_brain35", "s07": "scene_brain35", "s08": "scene_brain35", "s10": "scene_brain35",
             "s15": "scene_brain35", "s11": "scene_vault", "s12": "scene_vault"}
NP = int(os.environ.get("NP", "2"))   # процессов: 4 ядра общие с другими агентами


def span(sid):
    s = SHOTS[sid]
    a = max(0.0, s["t0"] - SH["pad"])
    b = s["t1"] + SH["pad"]
    n = int(round((b - a) * 30))
    return a, n


def _job(args):
    sid, i, t, path = args
    m = importlib.import_module(SCENE_MOD[sid])
    open(path, "w").write(m.frame(sid, t))
    return path


def build_svgs(sid, times, tmp):
    jobs = [(sid, i, t, os.path.join(tmp, f"f{i:04d}.svg")) for i, t in enumerate(times)]
    with Pool(NP) as p:
        return p.map(_job, jobs, chunksize=4)


def main():
    sys.path.insert(0, HERE)
    args = sys.argv[1:]
    sheet = "--sheet" in args
    ids = [a for a in args if a.startswith("s") and a[1:].isdigit()]
    tl = [a for a in args if "," in a or a.replace(".", "").isdigit()]
    base_tmp = os.environ.get("EXT_TMP", "/tmp/claude-0/-home-user-Generator-Stickman/bf395f21-db87-51d7-8095-aa76d06b9aee/scratchpad/brain_tmp")
    os.makedirs(base_tmp, exist_ok=True)
    for sid in ids:
        a, n = span(sid)
        tmp = tempfile.mkdtemp(dir=base_tmp, prefix=sid + "_")
        t0 = time.time()
        if sheet:
            if tl:
                times = [float(x) for x in tl[0].split(",")]
            else:
                times = [a + (n - 1) / 30 * k / 5 for k in range(6)]
            svgs = build_svgs(sid, times, tmp)
            outd = os.path.join(base_tmp, "sheets", sid)
            os.makedirs(outd, exist_ok=True)
            pngs = [os.path.join(outd, f"{sid}_{t:.2f}.png") for t in times]
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(f"{s}\t{p}" for s, p in zip(svgs, pngs)))
            subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "list.txt"), "png",
                                   str(min(NP, len(times))), "x"])
            jpg = os.path.join(base_tmp, "sheets", f"{sid}.jpg")
            subprocess.check_call([sys.executable, os.path.join(HERE, "sheet.py"), jpg] + pngs)
            print(sid, "sheet", jpg)
        else:
            times = [a + k / 30 for k in range(n)]
            svgs = build_svgs(sid, times, tmp)
            t1 = time.time()
            open(os.path.join(tmp, "list.txt"), "w").write("\n".join(svgs))
            pre = os.path.join(tmp, "seg")
            subprocess.check_call(["node", os.path.join(HERE, "render.js"), os.path.join(tmp, "list.txt"), "mp4", str(NP), pre])
            segs = sorted(x for x in os.listdir(tmp) if x.startswith("seg_") and x.endswith(".mp4"))
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
